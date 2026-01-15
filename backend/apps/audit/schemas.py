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
"""Compliance monitoring schemas."""

from pydantic import BaseModel


class ComplianceStatus(BaseModel):
    """Overall compliance status."""

    total_minions: int
    compliant_minions: int
    non_compliant_minions: int
    compliance_percentage: float
    last_check: str


class FailedState(BaseModel):
    """Failed state information."""

    state_name: str
    state_id: str
    reason: str
    failed_at: str


class MinionCompliance(BaseModel):
    """Minion compliance status."""

    minion_id: str
    is_compliant: bool
    failed_states: list[FailedState] = []
    last_highstate: str | None = None
    compliance_score: float = 100.0


class DriftDetection(BaseModel):
    """Configuration drift detection."""

    minion_id: str
    resource_type: str  # package, file, service, etc.
    resource_name: str
    expected_value: str
    actual_value: str
    drift_type: str  # missing, modified, unexpected
    detected_at: str
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
