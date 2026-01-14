"""Notifications and alerts API endpoints."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends

from app.api.v1.auth import get_current_active_user
from app.schemas.auth import User
from app.schemas.notification import Notification, NotificationSettings

router = APIRouter()

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
