"""Cloud management schemas"""

from pydantic import BaseModel, Field


class CloudProvider(BaseModel):
    """Cloud provider configuration"""

    name: str = Field(..., description="Provider name")
    driver: str = Field(..., description="Cloud driver")


class CloudProfile(BaseModel):
    """Cloud profile configuration"""

    name: str = Field(..., description="Profile name")
    provider: str = Field(..., description="Provider name")
    size: str | None = Field(None, description="Instance size")
    image: str | None = Field(None, description="Image name")


class CloudInstanceRequest(BaseModel):
    """Request to create cloud instance"""

    profile: str = Field(..., description="Profile name")
    names: list[str] = Field(..., description="Instance names")
