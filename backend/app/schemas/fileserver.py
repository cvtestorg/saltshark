"""File Server schemas"""
from pydantic import BaseModel, Field


class FileList(BaseModel):
    """List of files in file server"""

    environment: str = Field("base", description="File server environment")
    files: list[str] = Field(default_factory=list, description="File paths")


class FileContent(BaseModel):
    """File content from file server"""

    path: str = Field(..., description="File path")
    content: str = Field(..., description="File content")
