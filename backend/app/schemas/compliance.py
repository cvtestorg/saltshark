"""Compliance monitoring schemas."""
from datetime import datetime

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
