"""All Salt-related schemas consolidated"""

from typing import Any
from pydantic import BaseModel, Field

# ===== Minion Schemas =====
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
    grains: dict[str, Any] | None = Field(None, description="Minion grains data")
    pillars: dict[str, Any] | None = Field(None, description="Minion pillars data")


class MinionList(BaseModel):
    """List of minions"""
    minions: list[MinionStatus] = Field(default_factory=list)
    total: int = Field(0, description="Total number of minions")


# ===== Job Schemas =====
class JobBase(BaseModel):
    """Base job model"""
    jid: str = Field(..., description="Job ID")


class JobRequest(BaseModel):
    """Job execution request"""
    target: str = Field(..., description="Target minions (glob pattern)")
    function: str = Field(..., description="Salt function to execute")
    args: list[Any] = Field(default_factory=list, description="Function arguments")


class JobStatus(JobBase):
    """Job status information"""
    function: str = Field(..., description="Function name")
    target: str = Field(..., description="Target pattern")
    user: str = Field(..., description="User who started the job")
    start_time: str = Field(..., description="Job start time")


class JobDetail(JobStatus):
    """Detailed job information"""
    result: dict[str, Any] = Field(default_factory=dict)


class JobResult(JobStatus):
    """Job result with detailed information"""
    result: dict[str, Any] | None = Field(None, description="Job execution results")
    end_time: str | None = Field(None, description="Job end time")
    minions: list[str] = Field(default_factory=list, description="Target minions")
    status: str = Field(..., description="Job status (running/completed/failed)")


class JobList(BaseModel):
    """List of jobs"""
    jobs: list[JobStatus] = Field(default_factory=list)
    total: int = Field(0)


class JobExecuteRequest(BaseModel):
    """Request to execute a job"""
    target: str = Field(..., description="Target minions (can use glob patterns)")
    function: str = Field(..., description="Salt function to execute")
    args: list[str] = Field(default_factory=list, description="Function arguments")


# ===== Grains & Pillars Schemas =====
class GrainsData(BaseModel):
    """Grains data for a minion"""
    minion_id: str = Field(..., description="Minion ID")
    grains: dict[str, Any] = Field(default_factory=dict, description="Grains data")


class GrainsResponse(BaseModel):
    """Grains data response"""
    minion_id: str
    grains: dict[str, Any]


class PillarsData(BaseModel):
    """Pillars data for a minion"""
    minion_id: str = Field(..., description="Minion ID")
    pillars: dict[str, Any] = Field(default_factory=dict, description="Pillars data")


class PillarsResponse(BaseModel):
    """Pillars data response"""
    minion_id: str
    pillars: dict[str, Any]


class PillarKeys(BaseModel):
    """Pillar keys list"""
    minion_id: str = Field(..., description="Minion ID")
    keys: list[str] = Field(default_factory=list, description="Pillar keys")


class PillarItem(BaseModel):
    """Specific pillar item"""
    minion_id: str = Field(..., description="Minion ID")
    key: str = Field(..., description="Pillar key")
    value: dict[str, Any] | str | list[Any] | None = Field(
        None, description="Pillar value"
    )


class PillarKeysResponse(BaseModel):
    """Pillar keys list"""
    keys: list[str]


class PillarItemResponse(BaseModel):
    """Single pillar item"""
    key: str
    value: Any


# ===== State Schemas =====
class StateRequest(BaseModel):
    """State application request"""
    target: str = Field(..., description="Target minions")
    state: str = Field(..., description="State name")
    test: bool = Field(default=False, description="Test mode")


class StateResponse(BaseModel):
    """State application response"""
    jid: str
    result: dict[str, Any]


class StateList(BaseModel):
    """List of available states"""
    states: list[str]


# ===== Keys Schemas =====
class KeysResponse(BaseModel):
    """Salt keys response"""
    minions: list[str] = Field(default_factory=list)
    minions_pre: list[str] = Field(default_factory=list)
    minions_rejected: list[str] = Field(default_factory=list)


class KeyActionResponse(BaseModel):
    """Key action response"""
    success: bool
    message: str


# ===== Schedule Schemas =====
class ScheduleConfig(BaseModel):
    """Schedule configuration"""
    function: str
    seconds: int | None = None
    minutes: int | None = None
    hours: int | None = None
    job_args: list[Any] = Field(default_factory=list)
    job_kwargs: dict[str, Any] = Field(default_factory=dict)


class ScheduleResponse(BaseModel):
    """Schedule response"""
    schedules: dict[str, dict[str, Any]]


# ===== Runner Schemas =====
class RunnerRequest(BaseModel):
    """Runner execution request"""
    function: str = Field(..., description="Runner function")
    args: list[Any] = Field(default_factory=list)
    kwargs: dict[str, Any] = Field(default_factory=dict)


class RunnerResponse(BaseModel):
    """Runner execution response"""
    result: Any


class CommonRunnersResponse(BaseModel):
    """Common runners list"""
    runners: list[str]


# ===== Orchestration Schemas =====
class OrchestrationRequest(BaseModel):
    """Orchestration request"""
    orchestration: str = Field(..., description="Orchestration state file")
    target: str = Field(default="*", description="Target minions")
    pillar: dict[str, Any] = Field(default_factory=dict)


class OrchestrationResponse(BaseModel):
    """Orchestration response"""
    jid: str
    result: dict[str, Any]


class CommonOrchestrationsResponse(BaseModel):
    """Common orchestrations list"""
    orchestrations: list[str]


# ===== Beacons Schemas =====
class BeaconConfig(BaseModel):
    """Beacon configuration"""
    beacon_data: dict[str, Any]


class BeaconResponse(BaseModel):
    """Beacon response"""
    beacons: dict[str, Any]


# ===== Mine Schemas =====
class MineGetRequest(BaseModel):
    """Mine get request"""
    target: str
    function: str


class MineSendRequest(BaseModel):
    """Mine send request"""
    function: str


class MineResponse(BaseModel):
    """Mine data response"""
    data: dict[str, Any]


class ReturnersResponse(BaseModel):
    """Returners list"""
    returners: list[str]


# ===== Cloud Schemas =====
class CloudProvider(BaseModel):
    """Cloud provider info"""
    name: str
    driver: str


class CloudProfile(BaseModel):
    """Cloud profile info"""
    name: str
    provider: str


class CloudInstanceRequest(BaseModel):
    """Cloud instance creation request"""
    profile: str
    names: list[str]


class CloudResponse(BaseModel):
    """Cloud operation response"""
    result: dict[str, Any]


# ===== SSH Schemas =====
class SSHRequest(BaseModel):
    """SSH execution request"""
    target: str
    function: str
    args: list[Any] = Field(default_factory=list)


class SSHResponse(BaseModel):
    """SSH execution response"""
    result: dict[str, Any]


# ===== Events Schemas =====
class EventResponse(BaseModel):
    """Event data response"""
    events: list[dict[str, Any]]


class NodeGroupsResponse(BaseModel):
    """Node groups list"""
    nodegroups: dict[str, str]


class ReactorsResponse(BaseModel):
    """Reactors list"""
    reactors: list[dict[str, Any]]


# ===== Fileserver Schemas =====
class FileserverResponse(BaseModel):
    """Fileserver response"""
    files: list[str]


# ===== Template Schemas =====
class Template(BaseModel):
    """Template model"""
    id: str
    name: str
    description: str
    target: str
    function: str
    args: list[Any] = Field(default_factory=list)
    created_by: str
    created_at: str


class TemplateCreate(BaseModel):
    """Template creation request"""
    name: str
    description: str
    target: str
    function: str
    args: list[Any] = Field(default_factory=list)


class TemplateUpdate(BaseModel):
    """Template update request"""
    name: str | None = None
    description: str | None = None
    target: str | None = None
    function: str | None = None
    args: list[Any] | None = None


class TemplateList(BaseModel):
    """Templates list"""
    templates: list[Template]
    total: int

# ===== State Apply Schemas =====
class StateApplyRequest(BaseModel):
    """Request to apply a state"""
    target: str = Field(..., description="Target minions")
    state: str = Field(..., description="State name to apply")
    test: bool = Field(False, description="Test mode (dry run)")


class HighstateRequest(BaseModel):
    """Request to apply highstate"""
    target: str = Field(..., description="Target minions")
    test: bool = Field(False, description="Test mode (dry run)")


# ===== Schedule Schemas =====
class ScheduleRequest(BaseModel):
    """Request to add/modify schedule"""
    target: str = Field(..., description="Target minions")
    name: str = Field(..., description="Schedule name")
    function: str = Field(..., description="Function to execute")
    schedule: dict[str, Any] = Field(
        ..., description="Schedule configuration (cron, interval, etc)"
    )


# ===== SSH Schemas =====
class SSHExecuteRequest(BaseModel):
    """Request to execute via Salt SSH"""
    target: str = Field(..., description="Target hosts")
    function: str = Field(..., description="Function to execute")
    roster: str = Field("flat", description="Roster name")


# ===== Job Template Schemas =====
class JobTemplate(BaseModel):
    """Job template model"""
    id: str
    name: str
    description: str | None = None
    target: str
    function: str
    args: list[Any] = Field(default_factory=list)
    created_by: str | None = None
    created_at: str | None = None
"""Job template schemas."""

from typing import Any

from pydantic import BaseModel


class JobTemplate(BaseModel):
    """Job template model."""

    id: str
    name: str
    description: str | None = None
    target: str
    function: str
    args: list[Any] = []
    kwargs: dict[str, Any] = {}
    category: str = "general"
    is_public: bool = True
    created_by: str


class JobTemplateCreate(BaseModel):
    """Job template creation request."""

    name: str
    description: str | None = None
    target: str
    function: str
    args: list[Any] | None = None
    kwargs: dict[str, Any] | None = None
    category: str = "general"
    is_public: bool = True


class JobTemplateUpdate(BaseModel):
    """Job template update request."""

    name: str | None = None
    description: str | None = None
    target: str | None = None
    function: str | None = None
    args: list[Any] | None = None
    kwargs: dict[str, Any] | None = None
    category: str | None = None
    is_public: bool | None = None
