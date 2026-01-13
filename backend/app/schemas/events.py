"""Event stream and reactor schemas"""
from pydantic import BaseModel, Field


class EventStreamConfig(BaseModel):
    """Event stream configuration"""

    tag: str = Field("", description="Event tag filter")
    wait: int = Field(5, description="Wait time in seconds")


class ReactorConfig(BaseModel):
    """Reactor system configuration"""

    event_tag: str = Field(..., description="Event tag pattern")
    reactions: list[str] = Field(..., description="Reactor SLS files")


class NodegroupConfig(BaseModel):
    """Nodegroup configuration"""

    name: str = Field(..., description="Nodegroup name")
    members: str = Field(..., description="Nodegroup members pattern")
