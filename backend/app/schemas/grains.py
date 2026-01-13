"""Grains and Pillars schemas"""
from pydantic import BaseModel, Field


class GrainsData(BaseModel):
    """Grains data for a minion"""

    minion_id: str = Field(..., description="Minion ID")
    grains: dict = Field(default_factory=dict, description="Grains data")


class PillarsData(BaseModel):
    """Pillars data for a minion"""

    minion_id: str = Field(..., description="Minion ID")
    pillars: dict = Field(default_factory=dict, description="Pillars data")
