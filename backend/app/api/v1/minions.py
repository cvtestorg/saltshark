"""Minions API endpoints"""
from fastapi import APIRouter, HTTPException

from app.schemas.minion import MinionDetail, MinionList, MinionStatus
from app.services.salt_api import salt_client

router = APIRouter()


@router.get("/minions", response_model=MinionList)
async def list_minions() -> MinionList:
    """List all minions"""
    try:
        response = await salt_client.list_minions()
        minions_data = response.get("return", [{}])[0]

        minions = [
            MinionStatus(
                id=minion_id,
                os=data.get("os"),
                osrelease=data.get("osrelease"),
                status=data.get("status", "unknown"),
            )
            for minion_id, data in minions_data.items()
        ]

        return MinionList(minions=minions, total=len(minions))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/minions/{minion_id}", response_model=MinionDetail)
async def get_minion(minion_id: str) -> MinionDetail:
    """Get details for a specific minion"""
    try:
        response = await salt_client.get_minion(minion_id)
        minion_data = response.get("return", [{}])[0].get(minion_id, {})

        if not minion_data:
            raise HTTPException(status_code=404, detail="Minion not found")

        return MinionDetail(
            id=minion_id,
            os=minion_data.get("os"),
            osrelease=minion_data.get("osrelease"),
            status=minion_data.get("status", "unknown"),
            grains=minion_data.get("grains"),
            pillars=minion_data.get("pillars"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
