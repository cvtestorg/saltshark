"""Audit, compliance and notifications routes"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from apps.audit.schemas import *
from apps.auth.routes import get_current_active_user, require_role
from apps.auth.schemas import User

router = APIRouter(prefix="/api/v1")


# ===== Audit Endpoints =====
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


# ===== Compliance Endpoints =====
# Mock compliance data (replace with real data from Salt)
mock_compliance_data: dict[str, Any] = {
    "overall": ComplianceStatus(
        total_minions=3,
        compliant_minions=2,
        non_compliant_minions=1,
        compliance_percentage=66.7,
        last_check="2024-01-13T08:00:00",
    ),
    "minions": {
        "minion-1": MinionCompliance(
            minion_id="minion-1",
            is_compliant=True,
            failed_states=[],
            last_highstate="2024-01-13T07:00:00",
            compliance_score=100.0,
        ),
        "minion-2": MinionCompliance(
            minion_id="minion-2",
            is_compliant=True,
            failed_states=[],
            last_highstate="2024-01-13T06:30:00",
            compliance_score=100.0,
        ),
        "minion-3": MinionCompliance(
            minion_id="minion-3",
            is_compliant=False,
            failed_states=[
                FailedState(
                    state_name="webserver.nginx",
                    state_id="nginx-install",
                    reason="Package nginx not found",
                    failed_at="2024-01-13T05:00:00",
                )
            ],
            last_highstate="2024-01-13T05:00:00",
            compliance_score=85.0,
        ),
    },
}


@router.get("/status", response_model=ComplianceStatus)
async def get_compliance_status(
    current_user: User = Depends(get_current_active_user),
) -> ComplianceStatus:
    """Get overall compliance status."""
    return cast(ComplianceStatus, mock_compliance_data["overall"])


@router.get("/minions/{minion_id}", response_model=MinionCompliance)
async def get_minion_compliance(
    minion_id: str,
    current_user: User = Depends(get_current_active_user),
) -> MinionCompliance:
    """Get compliance status for a specific minion."""
    minions_data = cast(
        dict[str, MinionCompliance], mock_compliance_data.get("minions", {})
    )
    compliance = minions_data.get(minion_id)
    if not compliance:
        raise HTTPException(status_code=404, detail="Minion not found")
    return compliance


@router.get("/failed-states", response_model=list[dict[str, Any]])
async def get_failed_states(
    current_user: User = Depends(get_current_active_user),
) -> list[dict[str, Any]]:
    """Get all failed states across all minions."""
    failed_states: list[dict[str, Any]] = []
    minions_data = cast(
        dict[str, MinionCompliance], mock_compliance_data.get("minions", {})
    )
    for minion_id, compliance in minions_data.items():
        for failed_state in compliance.failed_states:
            failed_states.append(
                {
                    "minion_id": minion_id,
                    **failed_state.model_dump(),
                }
            )
    return failed_states


@router.get("/drift", response_model=list[DriftDetection])
async def get_configuration_drift(
    current_user: User = Depends(get_current_active_user),
) -> list[DriftDetection]:
    """Detect configuration drift across minions."""
    # Mock drift detection
    return [
        DriftDetection(
            minion_id="minion-3",
            resource_type="package",
            resource_name="nginx",
            expected_value="1.18.0",
            actual_value="not installed",
            drift_type="missing",
            detected_at="2024-01-13T05:00:00",
        )
    ]


@router.post("/remediate/{minion_id}")
async def remediate_compliance(
    minion_id: str,
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """Auto-remediate compliance issues for a minion."""
    compliance = mock_compliance_data["minions"].get(minion_id)
    if not compliance:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Minion not found")

    if compliance.is_compliant:
        return {"message": "Minion is already compliant", "minion_id": minion_id}

    # In real implementation, this would trigger highstate or specific state fixes
    return {
        "message": "Remediation initiated",
        "minion_id": minion_id,
        "failed_states": [fs.state_name for fs in compliance.failed_states],
        "action": "Running highstate to restore compliance",
    }


# ===== Notifications Endpoints =====
# Mock notification storage
notifications_db: list[Notification] = [
    Notification(
        id="1",
        user="admin",
        type="job_completed",
        title="Job Completed",
        message="Job test.ping on * completed successfully",
        priority="info",
        is_read=False,
        created_at=datetime.now(),
        data={"job_id": "20240113001", "function": "test.ping"},
    ),
    Notification(
        id="2",
        user="admin",
        type="job_failed",
        title="Job Failed",
        message="Job state.apply on minion-3 failed",
        priority="high",
        is_read=False,
        created_at=datetime.now(),
        data={"job_id": "20240113002", "minion": "minion-3"},
    ),
]

settings_db: dict[str, NotificationSettings] = {
    "admin": NotificationSettings(
        user="admin",
        email_enabled=True,
        email_address="admin@example.com",
        notify_on_job_completion=True,
        notify_on_job_failure=True,
        notify_on_minion_down=True,
        notify_on_compliance_failure=True,
    )
}


@router.get("", response_model=list[Notification])
async def list_notifications(
    unread_only: bool = False,
    current_user: User = Depends(get_current_active_user),
) -> list[Notification]:
    """List notifications for current user."""
    user_notifications = [
        n for n in notifications_db if n.user == current_user.username
    ]

    if unread_only:
        user_notifications = [n for n in user_notifications if not n.is_read]

    # Sort by created_at (newest first)
    user_notifications.sort(key=lambda x: x.created_at, reverse=True)

    return user_notifications


@router.post("/mark-read")
async def mark_notifications_read(
    notification_ids: list[str],
    current_user: User = Depends(get_current_active_user),
) -> dict[str, str]:
    """Mark notifications as read."""
    count = 0
    for notification in notifications_db:
        if (
            notification.id in notification_ids
            and notification.user == current_user.username
        ):
            notification.is_read = True
            count += 1

    return {"message": f"Marked {count} notifications as read"}


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
) -> dict[str, str]:
    """Mark all notifications as read for current user."""
    count = 0
    for notification in notifications_db:
        if notification.user == current_user.username and not notification.is_read:
            notification.is_read = True
            count += 1

    return {"message": f"Marked {count} notifications as read"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_active_user),
) -> dict[str, str]:
    """Delete a notification."""
    for i, notification in enumerate(notifications_db):
        if (
            notification.id == notification_id
            and notification.user == current_user.username
        ):
            notifications_db.pop(i)
            return {"message": "Notification deleted"}

    from fastapi import HTTPException

    raise HTTPException(status_code=404, detail="Notification not found")


@router.get("/settings", response_model=NotificationSettings)
async def get_notification_settings(
    current_user: User = Depends(get_current_active_user),
) -> NotificationSettings:
    """Get notification settings for current user."""
    settings = settings_db.get(current_user.username)
    if not settings:
        # Create default settings
        settings = NotificationSettings(
            user=current_user.username,
            email_enabled=False,
            email_address=current_user.email,
        )
        settings_db[current_user.username] = settings
    return settings


@router.put("/settings", response_model=NotificationSettings)
async def update_notification_settings(
    settings_update: NotificationSettings,
    current_user: User = Depends(get_current_active_user),
) -> NotificationSettings:
    """Update notification settings for current user."""
    settings_update.user = current_user.username
    settings_db[current_user.username] = settings_update
    return settings_update


@router.get("/unread-count", response_model=dict[str, int])
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
) -> dict[str, int]:
    """Get count of unread notifications."""
    count = sum(
        1 for n in notifications_db if n.user == current_user.username and not n.is_read
    )
    return {"count": count}


async def create_notification(
    user: str,
    notification_type: str,
    title: str,
    message: str,
    priority: str = "info",
    data: dict[str, Any] | None = None,
) -> Notification:
    """Create a new notification (internal function)."""
    notification_id = str(len(notifications_db) + 1)

    notification = Notification(
        id=notification_id,
        user=user,
        type=notification_type,
        title=title,
        message=message,
        priority=priority,
        is_read=False,
        created_at=datetime.now(),
        data=data or {},
    )

    notifications_db.append(notification)
    return notification

