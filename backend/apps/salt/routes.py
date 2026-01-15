"""Salt management routes - all endpoints consolidated"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from apps.auth.routes import get_current_active_user, require_role
from apps.auth.schemas import User
from apps.salt.salt_api_client import salt_client
from apps.salt.schemas import (
    GrainsData,
    HighstateRequest,
    JobExecuteRequest,
    JobList,
    JobResult,
    JobStatus,
    MinionDetail,
    MinionList,
    MinionStatus,
    PillarsData,
    ScheduleRequest,
    StateApplyRequest,
)

router = APIRouter(prefix="/api/v1", tags=["salt"])


# ===== Minions Endpoints =====
@router.get("/minions", response_model=MinionList)
async def list_minions() -> MinionList:
    """List all minions"""
    try:
        response = await salt_client.list_minions()
        minions_data = response.get("return", [{}])[0]

        minions = [
            MinionStatus(
                id=minion_id,
                os=data.get("os"),
                osrelease=data.get("osrelease"),
                status=data.get("status", "unknown"),
            )
            for minion_id, data in minions_data.items()
        ]

        return MinionList(minions=minions, total=len(minions))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/minions/{minion_id}", response_model=MinionDetail)
async def get_minion(minion_id: str) -> MinionDetail:
    """Get details for a specific minion"""
    try:
        response = await salt_client.get_minion(minion_id)
        minion_data = response.get("return", [{}])[0].get(minion_id, {})

        if not minion_data:
            raise HTTPException(status_code=404, detail="Minion not found")

        return MinionDetail(
            id=minion_id,
            os=minion_data.get("os"),
            osrelease=minion_data.get("osrelease"),
            status=minion_data.get("status", "unknown"),
            grains=minion_data.get("grains"),
            pillars=minion_data.get("pillars"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Jobs Endpoints =====
@router.get("/jobs", response_model=JobList)
async def list_jobs() -> JobList:
    """List all jobs"""
    try:
        response = await salt_client.list_jobs()
        jobs_data = response.get("return", [{}])[0]

        jobs = [
            JobStatus(
                jid=jid,
                function=data.get("function", ""),
                minions=data.get("minions", []),
                start_time=data.get("start_time"),
                status=data.get("status", "unknown"),
            )
            for jid, data in jobs_data.items()
        ]

        return JobList(jobs=jobs, total=len(jobs))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{jid}", response_model=JobResult)
async def get_job(jid: str) -> JobResult:
    """Get job details and results"""
    try:
        response = await salt_client.get_job(jid)
        job_data = response.get("return", [{}])[0]

        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")

        return JobResult(
            jid=jid,
            function=job_data.get("function", ""),
            minions=job_data.get("minions", []),
            start_time=job_data.get("start_time"),
            end_time=job_data.get("end_time"),
            status=job_data.get("status", "unknown"),
            result=job_data.get("result"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs/execute")
async def execute_job(job_request: JobExecuteRequest) -> dict[str, Any]:
    """Execute a Salt job on target minions"""
    try:
        response = await salt_client.execute_command(
            target=job_request.target,
            function=job_request.function,
            args=job_request.args if job_request.args else None,
        )

        return {
            "success": True,
            "message": "Job submitted successfully",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Grains Endpoints =====
@router.get("/minions/{minion_id}/grains", response_model=GrainsData)
async def get_grains(minion_id: str) -> GrainsData:
    """Get grains for a specific minion"""
    try:
        response = await salt_client.get_grains(minion_id)
        grains_data = response.get("return", [{}])[0].get(minion_id, {})

        return GrainsData(minion_id=minion_id, grains=grains_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/minions/{minion_id}/pillars", response_model=PillarsData)
async def get_pillars(minion_id: str) -> PillarsData:
    """Get pillars for a specific minion"""
    try:
        response = await salt_client.get_pillars(minion_id)
        pillars_data = response.get("return", [{}])[0].get(minion_id, {})

        return PillarsData(minion_id=minion_id, pillars=pillars_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== States Endpoints =====
@router.get("/states")
async def list_states() -> dict[str, Any]:
    """List available states"""
    try:
        response = await salt_client.list_states()
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/states/apply")
async def apply_state(request: StateApplyRequest) -> dict[str, Any]:
    """Apply a state to target minions"""
    try:
        response = await salt_client.apply_state(
            target=request.target,
            state=request.state,
            test=request.test,
        )
        return {
            "success": True,
            "message": f"State '{request.state}' {'tested' if request.test else 'applied'} on {request.target}",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/states/highstate")
async def apply_highstate(request: HighstateRequest) -> dict[str, Any]:
    """Apply highstate to target minions"""
    try:
        response = await salt_client.highstate(
            target=request.target,
            test=request.test,
        )
        return {
            "success": True,
            "message": f"Highstate {'tested' if request.test else 'applied'} on {request.target}",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/states/status/{target}")
async def get_state_status(target: str) -> dict[str, Any]:
    """Get current state status for minions"""
    try:
        response = await salt_client.get_state_status(target)
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Pillars Endpoints =====
@router.get("/pillars/{target}/keys")
async def list_pillar_keys(target: str) -> dict[str, Any]:
    """List all pillar keys for target"""
    try:
        response = await salt_client.list_pillar_keys(target)
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pillars/{target}/item/{key}")
async def get_pillar_item(target: str, key: str) -> dict[str, Any]:
    """Get specific pillar item"""
    try:
        response = await salt_client.get_pillar_item(target, key)
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pillars/{minion_id}")
async def get_all_pillars(minion_id: str) -> dict[str, Any]:
    """Get all pillars for a minion"""
    try:
        response = await salt_client.get_pillars(minion_id)
        return {
            "success": True,
            "minion_id": minion_id,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Schedules Endpoints =====
@router.get("/schedules/{target}")
async def list_schedules(target: str = "*") -> dict[str, Any]:
    """List scheduled jobs"""
    try:
        response = await salt_client.list_schedules(target)
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedules")
async def add_schedule(request: ScheduleRequest) -> dict[str, Any]:
    """Add a scheduled job"""
    try:
        response = await salt_client.add_schedule(
            target=request.target,
            name=request.name,
            function=request.function,
            schedule=request.schedule,
        )
        return {
            "success": True,
            "message": f"Schedule '{request.name}' added to {request.target}",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/schedules/{target}/{name}")
async def delete_schedule(target: str, name: str) -> dict[str, Any]:
    """Delete a scheduled job"""
    try:
        response = await salt_client.delete_schedule(target, name)
        return {
            "success": True,
            "message": f"Schedule '{name}' deleted from {target}",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Keys Endpoints =====
@router.get("/keys")
async def list_keys() -> dict[str, Any]:
    """List all minion keys by status"""
    try:
        response = await salt_client.list_keys()
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/keys/{minion_id}/accept")
async def accept_key(minion_id: str) -> dict[str, Any]:
    """Accept a pending minion key"""
    try:
        response = await salt_client.accept_key(minion_id)
        return {
            "success": True,
            "message": f"Key for '{minion_id}' accepted",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/keys/{minion_id}/reject")
async def reject_key(minion_id: str) -> dict[str, Any]:
    """Reject a pending minion key"""
    try:
        response = await salt_client.reject_key(minion_id)
        return {
            "success": True,
            "message": f"Key for '{minion_id}' rejected",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/keys/{minion_id}")
async def delete_key(minion_id: str) -> dict[str, Any]:
    """Delete a minion key"""
    try:
        response = await salt_client.delete_key(minion_id)
        return {
            "success": True,
            "message": f"Key for '{minion_id}' deleted",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Runners Endpoints =====
@router.post("/runners/execute")
async def execute_runner(request: RunnerRequest) -> dict[str, Any]:
    """Execute a Salt runner"""
    try:
        response = await salt_client.run_salt_runner(
            runner=request.runner,
            args=request.args if request.args else None,
        )
        return {
            "success": True,
            "message": f"Runner '{request.runner}' executed",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/runners/common")
async def list_common_runners() -> dict[str, Any]:
    """List commonly used runners"""
    common_runners = [
        {
            "name": "manage.status",
            "description": "Show minion status (up/down)",
            "category": "management",
        },
        {
            "name": "manage.versions",
            "description": "Show Salt versions of minions",
            "category": "management",
        },
        {
            "name": "jobs.active",
            "description": "Show active jobs",
            "category": "jobs",
        },
        {
            "name": "jobs.list_jobs",
            "description": "List all jobs",
            "category": "jobs",
        },
        {
            "name": "state.orchestrate",
            "description": "Run orchestration",
            "category": "orchestration",
        },
        {
            "name": "cache.clear_all",
            "description": "Clear all caches",
            "category": "cache",
        },
    ]
    return {
        "success": True,
        "runners": common_runners,
    }


# ===== Fileserver Endpoints =====
@router.get("/fileserver/files")
async def list_files(environment: str = "base") -> dict[str, Any]:
    """List files in file server"""
    try:
        response = await salt_client.list_files(environment)
        return {
            "success": True,
            "environment": environment,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fileserver/roots")
async def list_file_roots() -> dict[str, Any]:
    """List file server roots"""
    try:
        response = await salt_client.list_file_roots()
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fileserver/file")
async def get_file_content(path: str) -> dict[str, Any]:
    """Get content of a file from file server"""
    try:
        response = await salt_client.get_file_content(path)
        return {
            "success": True,
            "path": path,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Orchestration Endpoints =====
@router.post("/orchestration/run")
async def run_orchestration(request: OrchestrationRequest) -> dict[str, Any]:
    """Run a Salt orchestration"""
    try:
        response = await salt_client.orchestrate(
            orchestration=request.orchestration,
            target=request.target,
        )
        return {
            "success": True,
            "message": f"Orchestration '{request.orchestration}' executed on {request.target}",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orchestration/common")
async def list_common_orchestrations() -> dict[str, Any]:
    """List commonly used orchestrations"""
    common_orch = [
        {
            "name": "deploy.webapp",
            "description": "Deploy web application",
            "target": "web-*",
        },
        {
            "name": "upgrade.system",
            "description": "System upgrade orchestration",
            "target": "*",
        },
        {
            "name": "provision.stack",
            "description": "Provision full application stack",
            "target": "*",
        },
    ]
    return {
        "success": True,
        "orchestrations": common_orch,
    }


# ===== Beacons Endpoints =====
@router.get("/beacons/{target}")
async def list_beacons(target: str = "*") -> dict[str, Any]:
    """List configured beacons"""
    try:
        response = await salt_client.list_beacons(target)
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/beacons")
async def add_beacon(config: BeaconConfig) -> dict[str, Any]:
    """Add a beacon"""
    try:
        response = await salt_client.add_beacon(
            target=config.target,
            name=config.name,
            beacon_data=config.config,
        )
        return {
            "success": True,
            "message": f"Beacon '{config.name}' added to {config.target}",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/beacons/{target}/{name}")
async def delete_beacon(target: str, name: str) -> dict[str, Any]:
    """Delete a beacon"""
    try:
        response = await salt_client.delete_beacon(target, name)
        return {
            "success": True,
            "message": f"Beacon '{name}' deleted from {target}",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Cloud Endpoints =====
@router.get("/cloud/providers")
async def list_providers() -> dict[str, Any]:
    """List cloud providers"""
    try:
        response = await salt_client.list_cloud_providers()
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cloud/profiles")
async def list_profiles(provider: str | None = None) -> dict[str, Any]:
    """List cloud profiles"""
    try:
        response = await salt_client.list_cloud_profiles(provider)
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cloud/instances")
async def create_instance(request: CloudInstanceRequest) -> dict[str, Any]:
    """Create cloud instances"""
    try:
        response = await salt_client.create_cloud_instance(
            profile=request.profile,
            names=request.names,
        )
        return {
            "success": True,
            "message": f"Creating instances: {', '.join(request.names)}",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Ssh Endpoints =====
@router.post("/ssh/execute")
async def execute_ssh(request: SSHExecuteRequest) -> dict[str, Any]:
    """Execute command via Salt SSH"""
    try:
        response = await salt_client.ssh_execute(
            target=request.target,
            function=request.function,
            roster=request.roster,
        )
        return {
            "success": True,
            "message": f"Executed '{request.function}' on {request.target} via SSH",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Events Endpoints =====
@router.get("/events")
async def get_events(tag: str = "") -> dict[str, Any]:
    """Get events from event stream"""
    try:
        response = await salt_client.get_events(tag)
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nodegroups")
async def list_nodegroups() -> dict[str, Any]:
    """List configured nodegroups"""
    try:
        response = await salt_client.list_nodegroups()
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reactor")
async def list_reactors() -> dict[str, Any]:
    """List configured reactor systems"""
    try:
        response = await salt_client.list_reactor_systems()
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Mine Endpoints =====
@router.post("/mine/get")
async def get_mine_data(request: MineGetRequest) -> dict[str, Any]:
    """Get data from Salt Mine"""
    try:
        response = await salt_client.get_mine_data(
            target=request.target,
            function=request.function,
        )
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mine/send")
async def send_mine_data(request: MineSendRequest) -> dict[str, Any]:
    """Send data to Salt Mine"""
    try:
        response = await salt_client.send_mine_data(
            target=request.target,
            function=request.function,
        )
        return {
            "success": True,
            "message": f"Sent mine data from {request.target}",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mine/returners")
async def list_returners() -> dict[str, Any]:
    """List available returners"""
    try:
        response = await salt_client.list_returners()
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Templates Endpoints =====
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
