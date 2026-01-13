"""Grains and Pillars schemas"""

from typing import Any

from pydantic import BaseModel, Field


class GrainsData(BaseModel):
    """Grains data for a minion"""

    minion_id: str = Field(..., description="Minion ID")
    grains: dict[str, Any] = Field(default_factory=dict, description="Grains data")


class PillarsData(BaseModel):
    """Pillars data for a minion"""

    minion_id: str = Field(..., description="Minion ID")
    pillars: dict[str, Any] = Field(default_factory=dict, description="Pillars data")
