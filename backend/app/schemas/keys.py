"""Minion Keys management schemas"""
from pydantic import BaseModel, Field


class KeyList(BaseModel):
    """List of minion keys by status"""

    accepted: list[str] = Field(default_factory=list, description="Accepted keys")
    denied: list[str] = Field(default_factory=list, description="Denied keys")
    pending: list[str] = Field(default_factory=list, description="Pending keys")
    rejected: list[str] = Field(default_factory=list, description="Rejected keys")


class KeyAction(BaseModel):
    """Key action request"""

    minion_id: str = Field(..., description="Minion ID")
    action: str = Field(..., description="Action: accept, reject, delete")
