"""Event stream and targeting API endpoints"""
from fastapi import APIRouter, HTTPException

from app.services.salt_api import salt_client

router = APIRouter()


@router.get("/events")
async def get_events(tag: str = ""):
    """Get events from event stream"""
    try:
        response = await salt_client.get_events(tag)
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nodegroups")
async def list_nodegroups():
    """List configured nodegroups"""
    try:
        response = await salt_client.list_nodegroups()
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reactor")
async def list_reactors():
    """List configured reactor systems"""
    try:
        response = await salt_client.list_reactor_systems()
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
