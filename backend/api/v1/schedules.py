"""Schedule management API endpoints"""

from typing import Any

from fastapi import APIRouter, HTTPException

from schemas.schedule import ScheduleRequest
from services.salt_api import salt_client

router = APIRouter()


@router.get("/schedules/{target}")
async def list_schedules(target: str = "*") -> dict[str, Any]:
    """List scheduled jobs"""
    try:
        response = await salt_client.list_schedules(target)
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedules")
async def add_schedule(request: ScheduleRequest) -> dict[str, Any]:
    """Add a scheduled job"""
    try:
        response = await salt_client.add_schedule(
            target=request.target,
            name=request.name,
            function=request.function,
            schedule=request.schedule,
        )
        return {
            "success": True,
            "message": f"Schedule '{request.name}' added to {request.target}",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/schedules/{target}/{name}")
async def delete_schedule(target: str, name: str) -> dict[str, Any]:
    """Delete a scheduled job"""
    try:
        response = await salt_client.delete_schedule(target, name)
        return {
            "success": True,
            "message": f"Schedule '{name}' deleted from {target}",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
