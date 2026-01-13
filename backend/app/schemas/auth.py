"""Authentication schemas."""
from datetime import datetime

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token payload data."""
    username: str | None = None


class User(BaseModel):
    """User model (without password)."""
    id: str
    username: str
    email: EmailStr
    full_name: str | None = None
    role: str = "read-only"  # admin, operator, auditor, read-only
    is_active: bool = True
    created_at: datetime


class UserInDB(User):
    """User model with hashed password (for database)."""
    hashed_password: str


class UserCreate(BaseModel):
    """User creation request."""
    username: str
    email: EmailStr
    full_name: str | None = None
    password: str
    role: str = "read-only"


class UserUpdate(BaseModel):
    """User update request."""
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None
    role: str | None = None
    is_active: bool | None = None
