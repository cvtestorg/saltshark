"""Audit logging API endpoints."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Query

from app.api.v1.auth import require_role
from schemas.audit import AuditLog
from schemas.auth import User

router = APIRouter()

# Mock audit log storage (replace with database)
audit_logs_db: list[AuditLog] = [
    AuditLog(
        id="1",
        timestamp=datetime.now(tz=UTC),
        user="admin",
        action="job.execute",
        resource_type="job",
        resource_id="20240113001",
        details={"function": "test.ping", "target": "*"},
        result="success",
        ip_address="192.168.1.100",
    ),
]


@router.get("", response_model=list[AuditLog])
async def list_audit_logs(
    user: str | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_role("admin", "auditor")),
) -> list[AuditLog]:
    """List audit logs with filtering."""
    logs = audit_logs_db.copy()

    # Filter by user
    if user:
        logs = [log for log in logs if log.user == user]

    # Filter by action
    if action:
        logs = [log for log in logs if log.action == action]

    # Filter by resource type
    if resource_type:
        logs = [log for log in logs if log.resource_type == resource_type]

    # Sort by timestamp (newest first)
    logs.sort(key=lambda x: x.timestamp, reverse=True)

    # Pagination
    return logs[skip : skip + limit]


@router.get("/{log_id}", response_model=AuditLog)
async def get_audit_log(
    log_id: str,
    current_user: User = Depends(require_role("admin", "auditor")),
) -> AuditLog:
    """Get a specific audit log."""
    for log in audit_logs_db:
        if log.id == log_id:
            return log
    raise HTTPException(status_code=404, detail="Audit log not found")


@router.get("/users/{username}", response_model=list[AuditLog])
async def get_user_audit_logs(
    username: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_role("admin", "auditor")),
) -> list[AuditLog]:
    """Get audit logs for a specific user."""
    logs = [log for log in audit_logs_db if log.user == username]
    logs.sort(key=lambda x: x.timestamp, reverse=True)
    return logs[skip : skip + limit]


@router.get("/actions/list", response_model=list[str])
async def list_action_types(
    current_user: User = Depends(require_role("admin", "auditor")),
) -> list[str]:
    """List all action types in audit logs."""
    actions = set(log.action for log in audit_logs_db)
    return sorted(actions)


async def create_audit_log(
    user: str,
    action: str,
    resource_type: str,
    resource_id: str,
    details: dict[str, Any] | None = None,
    result: str = "success",
    ip_address: str | None = None,
) -> AuditLog:
    """Create a new audit log entry (internal function)."""
    log_id = str(len(audit_logs_db) + 1)

    audit_log = AuditLog(
        id=log_id,
        timestamp=datetime.now(),
        user=user,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        result=result,
        ip_address=ip_address,
    )

    audit_logs_db.append(audit_log)
    return audit_log


from fastapi import HTTPException
