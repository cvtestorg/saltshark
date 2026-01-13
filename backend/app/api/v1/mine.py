"""Salt Mine API endpoints"""
from fastapi import APIRouter, HTTPException

from app.schemas.mine import MineGetRequest, MineSendRequest
from app.services.salt_api import salt_client

router = APIRouter()


@router.post("/mine/get")
async def get_mine_data(request: MineGetRequest):
    """Get data from Salt Mine"""
    try:
        response = await salt_client.get_mine_data(
            target=request.target,
            function=request.function,
        )
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mine/send")
async def send_mine_data(request: MineSendRequest):
    """Send data to Salt Mine"""
    try:
        response = await salt_client.send_mine_data(
            target=request.target,
            function=request.function,
        )
        return {
            "success": True,
            "message": f"Sent mine data from {request.target}",
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mine/returners")
async def list_returners():
    """List available returners"""
    try:
        response = await salt_client.list_returners()
        return {
            "success": True,
            "data": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
