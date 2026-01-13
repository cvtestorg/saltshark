"""Beacons configuration schemas"""
from typing import Any

from pydantic import BaseModel, Field


class BeaconConfig(BaseModel):
    """Beacon configuration"""

    name: str = Field(..., description="Beacon name")
    target: str = Field("*", description="Target minions")
    config: dict[str, Any] = Field(..., description="Beacon configuration")


class BeaconList(BaseModel):
    """List of configured beacons"""

    beacons: dict[str, Any] = Field(default_factory=dict, description="Beacon configurations")
