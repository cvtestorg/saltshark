"""Beacons configuration schemas"""
from pydantic import BaseModel, Field


class BeaconConfig(BaseModel):
    """Beacon configuration"""

    name: str = Field(..., description="Beacon name")
    target: str = Field("*", description="Target minions")
    config: dict = Field(..., description="Beacon configuration")


class BeaconList(BaseModel):
    """List of configured beacons"""

    beacons: dict = Field(default_factory=dict, description="Beacon configurations")
