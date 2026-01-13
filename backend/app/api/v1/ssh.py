"""Salt SSH API endpoints"""
from fastapi import APIRouter, HTTPException

from app.schemas.ssh import SSHExecuteRequest
from app.services.salt_api import salt_client

router = APIRouter()


@router.post("/ssh/execute")
async def execute_ssh(request: SSHExecuteRequest):
    """Execute command via Salt SSH"""
    try:
        response = await salt_client.ssh_execute(
            target=request.target,
            function=request.function,
            roster=request.roster,
        )
        return {
            "success": True,
            "message": f"Executed '{request.function}' on {request.target} via SSH",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
