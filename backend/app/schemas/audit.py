"""Audit log schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AuditLog(BaseModel):
    """Audit log entry."""

    id: str
    timestamp: datetime
    user: str
    action: str  # job.execute, state.apply, minion.create, etc.
    resource_type: str  # job, state, minion, key, etc.
    resource_id: str
    details: dict[str, Any] = {}
    result: str = "success"  # success, failure, error
    ip_address: str | None = None


class AuditLogCreate(BaseModel):
    """Audit log creation request."""

    user: str
    action: str
    resource_type: str
    resource_id: str
    details: dict[str, Any] | None = None
    result: str = "success"
    ip_address: str | None = None
