"""Job templates API endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.auth import get_current_active_user, require_role
from app.schemas.auth import User
from app.schemas.template import JobTemplate, JobTemplateCreate, JobTemplateUpdate
from app.services.salt_api import SaltAPIClient

router = APIRouter()

# Mock template storage (replace with database)
templates_db: dict[str, JobTemplate] = {
    "1": JobTemplate(
        id="1",
        name="Ping All Minions",
        description="Quick connectivity test for all minions",
        target="*",
        function="test.ping",
        args=[],
        kwargs={},
        category="testing",
        is_public=True,
        created_by="admin",
    ),
    "2": JobTemplate(
        id="2",
        name="Disk Usage Check",
        description="Check disk usage on all minions",
        target="*",
        function="disk.usage",
        args=[],
        kwargs={},
        category="monitoring",
        is_public=True,
        created_by="admin",
    ),
    "3": JobTemplate(
        id="3",
        name="Update Package Lists",
        description="Update package repositories",
        target="*",
        function="pkg.refresh_db",
        args=[],
        kwargs={},
        category="maintenance",
        is_public=True,
        created_by="admin",
    ),
}


@router.get("", response_model=list[JobTemplate])
async def list_templates(
    category: str | None = None,
    current_user: User = Depends(get_current_active_user),
) -> list[JobTemplate]:
    """List all job templates."""
    templates = list(templates_db.values())

    # Filter by category
    if category:
        templates = [t for t in templates if t.category == category]

    # Filter by visibility (show public + own templates)
    templates = [
        t for t in templates if t.is_public or t.created_by == current_user.username
    ]

    return templates


@router.post("", response_model=JobTemplate)
async def create_template(
    template: JobTemplateCreate,
    current_user: User = Depends(require_role("admin", "operator")),
) -> JobTemplate:
    """Create a new job template."""
    template_id = str(len(templates_db) + 1)

    new_template = JobTemplate(
        id=template_id,
        name=template.name,
        description=template.description,
        target=template.target,
        function=template.function,
        args=template.args or [],
        kwargs=template.kwargs or {},
        category=template.category,
        is_public=template.is_public,
        created_by=current_user.username,
    )

    templates_db[template_id] = new_template
    return new_template


@router.get("/{template_id}", response_model=JobTemplate)
async def get_template(
    template_id: str,
    current_user: User = Depends(get_current_active_user),
) -> JobTemplate:
    """Get a specific job template."""
    template = templates_db.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Check access
    if not template.is_public and template.created_by != current_user.username:
        raise HTTPException(status_code=403, detail="Access denied")

    return template


@router.put("/{template_id}", response_model=JobTemplate)
async def update_template(
    template_id: str,
    template_update: JobTemplateUpdate,
    current_user: User = Depends(require_role("admin", "operator")),
) -> JobTemplate:
    """Update a job template."""
    template = templates_db.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Check permissions (only creator or admin can update)
    if template.created_by != current_user.username and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    # Update fields
    if template_update.name is not None:
        template.name = template_update.name
    if template_update.description is not None:
        template.description = template_update.description
    if template_update.target is not None:
        template.target = template_update.target
    if template_update.function is not None:
        template.function = template_update.function
    if template_update.args is not None:
        template.args = template_update.args
    if template_update.kwargs is not None:
        template.kwargs = template_update.kwargs
    if template_update.category is not None:
        template.category = template_update.category
    if template_update.is_public is not None:
        template.is_public = template_update.is_public

    templates_db[template_id] = template
    return template


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    current_user: User = Depends(require_role("admin", "operator")),
) -> dict[str, str]:
    """Delete a job template."""
    template = templates_db.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Check permissions
    if template.created_by != current_user.username and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    del templates_db[template_id]
    return {"message": "Template deleted successfully"}


@router.post("/{template_id}/execute")
async def execute_template(
    template_id: str,
    overrides: dict[str, Any] | None = None,
    current_user: User = Depends(require_role("admin", "operator")),
) -> dict[str, Any]:
    """Execute a job from template."""
    template = templates_db.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Check access
    if not template.is_public and template.created_by != current_user.username:
        raise HTTPException(status_code=403, detail="Access denied")

    # Prepare job parameters
    target = overrides.get("target", template.target) if overrides else template.target
    function = (
        overrides.get("function", template.function) if overrides else template.function
    )
    args = overrides.get("args", template.args) if overrides else template.args
    kwargs = overrides.get("kwargs", template.kwargs) if overrides else template.kwargs

    # Execute via Salt API
    salt_client = SaltAPIClient()
    result = await salt_client.execute_job(
        target=target,
        function=function,
        args=args,
        kwargs=kwargs,
    )

    return {
        "template_id": template_id,
        "template_name": template.name,
        "job_result": result,
    }


@router.get("/categories/list")
async def list_categories(
    current_user: User = Depends(get_current_active_user),
) -> list[str]:
    """List all template categories."""
    categories = set()
    for template in templates_db.values():
        if template.is_public or template.created_by == current_user.username:
            categories.add(template.category)
    return sorted(categories)
