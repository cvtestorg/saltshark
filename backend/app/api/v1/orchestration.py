"""Orchestration API endpoints"""
from typing import Any

from fastapi import APIRouter, HTTPException

from app.schemas.orchestration import OrchestrationRequest
from app.services.salt_api import salt_client

router = APIRouter()


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
