"""Pillar management schemas"""

from typing import Any

from pydantic import BaseModel, Field


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
