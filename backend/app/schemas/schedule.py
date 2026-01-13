"""Schedule management schemas"""
from typing import Any

from pydantic import BaseModel, Field


class ScheduleItem(BaseModel):
    """Scheduled job item"""

    name: str = Field(..., description="Schedule name")
    function: str = Field(..., description="Function to execute")
    schedule: dict[str, Any] = Field(..., description="Schedule configuration")
    enabled: bool = Field(True, description="Whether schedule is enabled")


class ScheduleRequest(BaseModel):
    """Request to add/modify schedule"""

    target: str = Field(..., description="Target minions")
    name: str = Field(..., description="Schedule name")
    function: str = Field(..., description="Function to execute")
    schedule: dict[str, Any] = Field(..., description="Schedule configuration (cron, interval, etc)")


class ScheduleList(BaseModel):
    """List of schedules"""

    schedules: list[ScheduleItem] = Field(default_factory=list)
    total: int = Field(0, description="Total number of schedules")
