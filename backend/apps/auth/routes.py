"""Authentication routes for SaltShark"""
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from schemas.auth import Token, User, UserCreate, UserInDB, UserUpdate

router = APIRouter()

# Security configuration
SECRET_KEY = "your-secret-key-here-change-in-production"  # TODO: Move to settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Mock user database (replace with real database)
fake_users_db: dict[str, UserInDB] = {
    "admin": UserInDB(
        id="1",
        username="admin",
        email="admin@example.com",
        full_name="Administrator",
        hashed_password=pwd_context.hash("admin123"),
        role="admin",
        is_active=True,
        created_at=datetime.now(tz=timezone.utc),
    )
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    result = pwd_context.verify(plain_password, hashed_password)
    return bool(result)


def get_password_hash(password: str) -> str:
    """Hash password."""
    result = pwd_context.hash(password)
    return str(result)


def get_user(username: str) -> UserInDB | None:
    """Get user from database."""
    return fake_users_db.get(username)


def authenticate_user(username: str, password: str) -> UserInDB | None:
    """Authenticate user with username and password."""
    user = get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return str(encoded_jwt)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or not isinstance(username, str):
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return User.model_validate(user)


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(*roles: str):  # type: ignore[no-untyped-def]
    """Dependency to check user has required role."""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict[str, str]:
    """Login endpoint - returns JWT token."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login_json(credentials: dict[str, str]) -> dict[str, str]:
    """Login with JSON payload."""
    user = authenticate_user(credentials["username"], credentials["password"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current user info."""
    return current_user


@router.get("/users", response_model=list[User])
async def list_users(
    current_user: User = Depends(require_role("admin"))
) -> list[User]:
    """List all users (admin only)."""
    return [User.model_validate(u) for u in fake_users_db.values()]


@router.post("/users", response_model=User)
async def create_user(
    user_create: UserCreate,
    current_user: User = Depends(require_role("admin"))
) -> User:
    """Create new user (admin only)."""
    if user_create.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user_id = str(len(fake_users_db) + 1)
    hashed_password = get_password_hash(user_create.password)
    
    user_db = UserInDB(
        id=user_id,
        username=user_create.username,
        email=user_create.email,
        full_name=user_create.full_name,
        hashed_password=hashed_password,
        role=user_create.role,
        is_active=True,
        created_at=datetime.now(tz=timezone.utc),
    )
    fake_users_db[user_create.username] = user_db
    return User.model_validate(user_db)


@router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(require_role("admin"))
) -> User:
    """Update user (admin only)."""
    # Find user by ID
    user = None
    username_key = None
    for key, u in fake_users_db.items():
        if u.id == user_id:
            user = u
            username_key = key
            break
    
    if not user or not username_key:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    if user_update.email:
        user.email = user_update.email
    if user_update.full_name:
        user.full_name = user_update.full_name
    if user_update.role:
        user.role = user_update.role
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    if user_update.password:
        user.hashed_password = get_password_hash(user_update.password)
    
    fake_users_db[username_key] = user
    return User.model_validate(user)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_role("admin"))
) -> dict[str, str]:
    """Delete user (admin only)."""
    # Find and delete user
    for key, user in list(fake_users_db.items()):
        if user.id == user_id:
            if user.username == current_user.username:
                raise HTTPException(status_code=400, detail="Cannot delete yourself")
            del fake_users_db[key]
            return {"message": "User deleted successfully"}
    
    raise HTTPException(status_code=404, detail="User not found")


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)) -> dict[str, str]:
    """
    Logout endpoint (for compatibility with rest_cherrypy).
    
    Note: JWT tokens are stateless, so this endpoint only returns a success message.
    The client should discard the token. For real token revocation, implement a
    token blacklist with database.
    """
    return {
        "message": "Logged out successfully",
        "user": current_user.username,
        "note": "JWT token is stateless - please discard the token on client side"
    }
