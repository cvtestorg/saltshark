"""Job schemas"""

from typing import Any

from pydantic import BaseModel, Field


class JobBase(BaseModel):
    """Base job model"""

    jid: str = Field(..., description="Job ID")


class JobStatus(JobBase):
    """Job status information"""

    function: str = Field(..., description="Salt function executed")
    minions: list[str] = Field(default_factory=list, description="Target minions")
    start_time: str | None = Field(None, description="Job start time")
    status: str = Field(..., description="Job status (running/completed/failed)")


class JobResult(JobStatus):
    """Job result with detailed information"""

    result: dict[str, Any] | None = Field(None, description="Job execution results")
    end_time: str | None = Field(None, description="Job end time")


class JobList(BaseModel):
    """List of jobs"""

    jobs: list[JobStatus] = Field(default_factory=list)
    total: int = Field(0, description="Total number of jobs")


class JobExecuteRequest(BaseModel):
    """Request to execute a job"""

    target: str = Field(..., description="Target minions (can use glob patterns)")
    function: str = Field(..., description="Salt function to execute")
    args: list[str] = Field(default_factory=list, description="Function arguments")
