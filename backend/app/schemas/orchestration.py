"""Orchestration schemas"""
from typing import Any

from pydantic import BaseModel, Field


class OrchestrationRequest(BaseModel):
    """Request to run orchestration"""

    orchestration: str = Field(..., description="Orchestration SLS file name")
    target: str = Field("*", description="Target minions")


class OrchestrationResult(BaseModel):
    """Orchestration execution result"""

    orchestration: str = Field(..., description="Orchestration name")
    success: bool = Field(..., description="Execution success status")
    result: dict[str, Any] = Field(default_factory=dict, description="Orchestration result")
