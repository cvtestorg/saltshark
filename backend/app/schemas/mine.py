"""Salt Mine schemas"""

from pydantic import BaseModel, Field


class MineGetRequest(BaseModel):
    """Request to get mine data"""

    target: str = Field(..., description="Target minions")
    function: str = Field(..., description="Mine function")


class MineSendRequest(BaseModel):
    """Request to send mine data"""

    target: str = Field(..., description="Target minions")
    function: str = Field(..., description="Mine function")
