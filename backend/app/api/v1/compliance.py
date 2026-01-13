"""Compliance monitoring API endpoints."""

from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.auth import get_current_active_user
from app.schemas.auth import User
from app.schemas.compliance import (
    ComplianceStatus,
    DriftDetection,
    FailedState,
    MinionCompliance,
)

router = APIRouter()

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
