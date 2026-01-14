"""Salt Runners API endpoints"""

from typing import Any

from fastapi import APIRouter, HTTPException

from schemas.runners import RunnerRequest
from services.salt_api import salt_client

router = APIRouter()


@router.post("/runners/execute")
async def execute_runner(request: RunnerRequest) -> dict[str, Any]:
    """Execute a Salt runner"""
    try:
        response = await salt_client.run_salt_runner(
            runner=request.runner,
            args=request.args if request.args else None,
        )
        return {
            "success": True,
            "message": f"Runner '{request.runner}' executed",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/runners/common")
async def list_common_runners() -> dict[str, Any]:
    """List commonly used runners"""
    common_runners = [
        {
            "name": "manage.status",
            "description": "Show minion status (up/down)",
            "category": "management",
        },
        {
            "name": "manage.versions",
            "description": "Show Salt versions of minions",
            "category": "management",
        },
        {
            "name": "jobs.active",
            "description": "Show active jobs",
            "category": "jobs",
        },
        {
            "name": "jobs.list_jobs",
            "description": "List all jobs",
            "category": "jobs",
        },
        {
            "name": "state.orchestrate",
            "description": "Run orchestration",
            "category": "orchestration",
        },
        {
            "name": "cache.clear_all",
            "description": "Clear all caches",
            "category": "cache",
        },
    ]
    return {
        "success": True,
        "runners": common_runners,
    }
