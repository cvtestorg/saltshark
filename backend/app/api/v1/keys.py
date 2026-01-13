"""Minion Keys management API endpoints"""
from typing import Any

from fastapi import APIRouter, HTTPException

from app.services.salt_api import salt_client

router = APIRouter()


@router.get("/keys")
async def list_keys() -> dict[str, Any]:
    """List all minion keys by status"""
    try:
        response = await salt_client.list_keys()
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/keys/{minion_id}/accept")
async def accept_key(minion_id: str) -> dict[str, Any]:
    """Accept a pending minion key"""
    try:
        response = await salt_client.accept_key(minion_id)
        return {
            "success": True,
            "message": f"Key for '{minion_id}' accepted",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/keys/{minion_id}/reject")
async def reject_key(minion_id: str) -> dict[str, Any]:
    """Reject a pending minion key"""
    try:
        response = await salt_client.reject_key(minion_id)
        return {
            "success": True,
            "message": f"Key for '{minion_id}' rejected",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/keys/{minion_id}")
async def delete_key(minion_id: str) -> dict[str, Any]:
    """Delete a minion key"""
    try:
        response = await salt_client.delete_key(minion_id)
        return {
            "success": True,
            "message": f"Key for '{minion_id}' deleted",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
