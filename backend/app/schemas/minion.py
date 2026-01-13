"""Minion schemas"""
from pydantic import BaseModel, Field


class MinionBase(BaseModel):
    """Base minion model"""

    id: str = Field(..., description="Minion ID")


class MinionStatus(MinionBase):
    """Minion status information"""

    os: str | None = Field(None, description="Operating system")
    osrelease: str | None = Field(None, description="OS release version")
    status: str | None = Field(None, description="Minion status (up/down)")


class MinionDetail(MinionStatus):
    """Detailed minion information"""

    grains: dict | None = Field(None, description="Minion grains data")
    pillars: dict | None = Field(None, description="Minion pillars data")


class MinionList(BaseModel):
    """List of minions"""

    minions: list[MinionStatus] = Field(default_factory=list)
    total: int = Field(0, description="Total number of minions")
