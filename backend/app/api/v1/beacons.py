"""Beacons API endpoints"""

from typing import Any

from fastapi import APIRouter, HTTPException

from app.schemas.beacons import BeaconConfig
from app.services.salt_api import salt_client

router = APIRouter()


@router.get("/beacons/{target}")
async def list_beacons(target: str = "*") -> dict[str, Any]:
    """List configured beacons"""
    try:
        response = await salt_client.list_beacons(target)
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/beacons")
async def add_beacon(config: BeaconConfig) -> dict[str, Any]:
    """Add a beacon"""
    try:
        response = await salt_client.add_beacon(
            target=config.target,
            name=config.name,
            beacon_data=config.config,
        )
        return {
            "success": True,
            "message": f"Beacon '{config.name}' added to {config.target}",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/beacons/{target}/{name}")
async def delete_beacon(target: str, name: str) -> dict[str, Any]:
    """Delete a beacon"""
    try:
        response = await salt_client.delete_beacon(target, name)
        return {
            "success": True,
            "message": f"Beacon '{name}' deleted from {target}",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
