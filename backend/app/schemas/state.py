"""State management schemas"""
from pydantic import BaseModel, Field


class StateApplyRequest(BaseModel):
    """Request to apply a state"""

    target: str = Field(..., description="Target minions")
    state: str = Field(..., description="State name to apply")
    test: bool = Field(False, description="Test mode (dry run)")


class HighstateRequest(BaseModel):
    """Request to apply highstate"""

    target: str = Field(..., description="Target minions")
    test: bool = Field(False, description="Test mode (dry run)")


class StateResult(BaseModel):
    """State execution result"""

    minion_id: str = Field(..., description="Minion ID")
    state: str = Field(..., description="State name")
    result: bool = Field(..., description="Execution result")
    changes: dict = Field(default_factory=dict, description="Changes made")
    comment: str | None = Field(None, description="Result comment")
