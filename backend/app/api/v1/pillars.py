"""Pillar management API endpoints"""
from typing import Any

from fastapi import APIRouter, HTTPException

from app.services.salt_api import salt_client

router = APIRouter()


@router.get("/pillars/{target}/keys")
async def list_pillar_keys(target: str) -> dict[str, Any]:
    """List all pillar keys for target"""
    try:
        response = await salt_client.list_pillar_keys(target)
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pillars/{target}/item/{key}")
async def get_pillar_item(target: str, key: str) -> dict[str, Any]:
    """Get specific pillar item"""
    try:
        response = await salt_client.get_pillar_item(target, key)
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pillars/{minion_id}")
async def get_all_pillars(minion_id: str) -> dict[str, Any]:
    """Get all pillars for a minion"""
    try:
        response = await salt_client.get_pillars(minion_id)
        return {
            "success": True,
            "minion_id": minion_id,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
