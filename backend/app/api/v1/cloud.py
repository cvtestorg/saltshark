"""Cloud management API endpoints"""
from typing import Any

from fastapi import APIRouter, HTTPException

from app.schemas.cloud import CloudInstanceRequest
from app.services.salt_api import salt_client

router = APIRouter()


@router.get("/cloud/providers")
async def list_providers() -> dict[str, Any]:
    """List cloud providers"""
    try:
        response = await salt_client.list_cloud_providers()
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cloud/profiles")
async def list_profiles(provider: str | None = None) -> dict[str, Any]:
    """List cloud profiles"""
    try:
        response = await salt_client.list_cloud_profiles(provider)
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cloud/instances")
async def create_instance(request: CloudInstanceRequest) -> dict[str, Any]:
    """Create cloud instances"""
    try:
        response = await salt_client.create_cloud_instance(
            profile=request.profile,
            names=request.names,
        )
        return {
            "success": True,
            "message": f"Creating instances: {', '.join(request.names)}",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
