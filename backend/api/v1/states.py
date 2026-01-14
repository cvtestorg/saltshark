"""State management API endpoints"""

from typing import Any

from fastapi import APIRouter, HTTPException

from schemas.state import HighstateRequest, StateApplyRequest
from services.salt_api import salt_client

router = APIRouter()


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
