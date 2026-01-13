"""Notification schemas."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr


class Notification(BaseModel):
    """Notification model."""
    id: str
    user: str
    type: str  # job_completed, job_failed, minion_down, compliance_failure, etc.
    title: str
    message: str
    priority: str = "info"  # info, warning, high, critical
    is_read: bool = False
    created_at: datetime
    data: dict[str, Any] = {}


class NotificationSettings(BaseModel):
    """Notification settings for a user."""
    user: str
    email_enabled: bool = False
    email_address: EmailStr | None = None
    notify_on_job_completion: bool = True
    notify_on_job_failure: bool = True
    notify_on_minion_down: bool = True
    notify_on_compliance_failure: bool = True
