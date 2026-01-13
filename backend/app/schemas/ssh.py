"""Salt SSH schemas"""
from typing import Any

from pydantic import BaseModel, Field


class SSHExecuteRequest(BaseModel):
    """Request to execute via Salt SSH"""

    target: str = Field(..., description="Target hosts")
    function: str = Field(..., description="Function to execute")
    roster: str = Field("flat", description="Roster name")


class SSHResult(BaseModel):
    """Salt SSH execution result"""

    target: str = Field(..., description="Target host")
    success: bool = Field(..., description="Execution success")
    result: dict[str, Any] | str = Field(..., description="Execution result")
