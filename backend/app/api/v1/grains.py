"""Grains and Pillars API endpoints"""

from fastapi import APIRouter, HTTPException

from schemas.grains import GrainsData, PillarsData
from app.services.salt_api import salt_client

router = APIRouter()


@router.get("/minions/{minion_id}/grains", response_model=GrainsData)
async def get_grains(minion_id: str) -> GrainsData:
    """Get grains for a specific minion"""
    try:
        response = await salt_client.get_grains(minion_id)
        grains_data = response.get("return", [{}])[0].get(minion_id, {})

        return GrainsData(minion_id=minion_id, grains=grains_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/minions/{minion_id}/pillars", response_model=PillarsData)
async def get_pillars(minion_id: str) -> PillarsData:
    """Get pillars for a specific minion"""
    try:
        response = await salt_client.get_pillars(minion_id)
        pillars_data = response.get("return", [{}])[0].get(minion_id, {})

        return PillarsData(minion_id=minion_id, pillars=pillars_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
