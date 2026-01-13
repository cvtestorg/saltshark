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
