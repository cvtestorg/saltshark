"""Salt Runners schemas"""
from typing import Any

from pydantic import BaseModel, Field


class RunnerRequest(BaseModel):
    """Request to execute a Salt runner"""

    runner: str = Field(..., description="Runner function name")
    args: list[str] = Field(default_factory=list, description="Runner arguments")


class RunnerResult(BaseModel):
    """Runner execution result"""

    runner: str = Field(..., description="Runner function name")
    success: bool = Field(..., description="Execution success status")
    result: dict[str, Any] | list[Any] | str = Field(..., description="Runner result data")
