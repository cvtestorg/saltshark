"""Tests for authentication endpoints"""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from api.v1.auth import (
    create_access_token,
    fake_users_db,
    get_password_hash,
    verify_password,
)
from schemas.auth import UserInDB


@pytest.fixture(autouse=True)
def reset_users_db():
    """Reset users database before each test"""
    # Save original state
    original_db = fake_users_db.copy()

    yield

    # Restore original state
    fake_users_db.clear()
    fake_users_db.update(original_db)


def test_verify_password():
    """Test password verification"""
    password = "testpassword123"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_create_access_token():
    """Test JWT token creation"""
    data = {"sub": "testuser"}
    token = create_access_token(data)

    assert token
    assert isinstance(token, str)


def test_login_success(client: TestClient):
    """Test successful login"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_json_success(client: TestClient):
    """Test successful login with JSON payload"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_json_invalid_credentials(client: TestClient):
    """Test JSON login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrongpassword"},
    )

    assert response.status_code == 401


def test_get_current_user(client: TestClient):
    """Test getting current user info"""
    # First login to get token
    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin123"},
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["email"] == "admin@example.com"
    assert data["role"] == "admin"
    assert data["is_active"] is True


def test_get_current_user_invalid_token(client: TestClient):
    """Test getting current user with invalid token"""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"},
    )

    assert response.status_code == 401


def test_list_users_as_admin(client: TestClient):
    """Test listing users as admin"""
    # Login as admin
    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin123"},
    )
    token = login_response.json()["access_token"]

    # List users
    response = client.get(
        "/api/v1/auth/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 1
    assert any(u["username"] == "admin" for u in users)


def test_create_user_as_admin(client: TestClient):
    """Test creating a new user as admin"""
    # Login as admin
    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin123"},
    )
    token = login_response.json()["access_token"]

    # Create new user
    new_user = {
        "username": "newuser",
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "newpass123",
        "role": "operator",
    }

    response = client.post(
        "/api/v1/auth/users",
        json=new_user,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "operator"
    assert "hashed_password" not in data  # Should not expose password


def test_create_user_duplicate_username(client: TestClient):
    """Test creating user with duplicate username"""
    # Login as admin
    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin123"},
    )
    token = login_response.json()["access_token"]

    # Try to create user with existing username
    new_user = {
        "username": "admin",  # Already exists
        "email": "another@example.com",
        "full_name": "Another User",
        "password": "pass123",
        "role": "operator",
    }

    response = client.post(
        "/api/v1/auth/users",
        json=new_user,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_update_user_as_admin(client: TestClient):
    """Test updating user as admin"""
    # Login as admin
    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin123"},
    )
    token = login_response.json()["access_token"]

    # Create a test user first
    new_user = {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpass123",
        "role": "operator",
    }
    create_response = client.post(
        "/api/v1/auth/users",
        json=new_user,
        headers={"Authorization": f"Bearer {token}"},
    )
    user_id = create_response.json()["id"]

    # Update the user
    update_data = {
        "email": "updated@example.com",
        "full_name": "Updated User",
    }

    response = client.put(
        f"/api/v1/auth/users/{user_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated@example.com"
    assert data["full_name"] == "Updated User"


def test_update_nonexistent_user(client: TestClient):
    """Test updating non-existent user"""
    # Login as admin
    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin123"},
    )
    token = login_response.json()["access_token"]

    update_data = {"email": "test@example.com"}

    response = client.put(
        "/api/v1/auth/users/nonexistent_id",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_delete_user_as_admin(client: TestClient):
    """Test deleting user as admin"""
    # Login as admin
    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin123"},
    )
    token = login_response.json()["access_token"]

    # Create a test user first
    new_user = {
        "username": "deleteuser",
        "email": "delete@example.com",
        "full_name": "Delete User",
        "password": "deletepass123",
        "role": "operator",
    }
    create_response = client.post(
        "/api/v1/auth/users",
        json=new_user,
        headers={"Authorization": f"Bearer {token}"},
    )
    user_id = create_response.json()["id"]

    # Delete the user
    response = client.delete(
        f"/api/v1/auth/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"].lower()


def test_delete_self_forbidden(client: TestClient):
    """Test that users cannot delete themselves"""
    # Login as admin
    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin123"},
    )
    token = login_response.json()["access_token"]

    # Try to delete self (admin user has id "1")
    response = client.delete(
        "/api/v1/auth/users/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert "Cannot delete yourself" in response.json()["detail"]


def test_delete_nonexistent_user(client: TestClient):
    """Test deleting non-existent user"""
    # Login as admin
    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin123"},
    )
    token = login_response.json()["access_token"]

    response = client.delete(
        "/api/v1/auth/users/nonexistent_id",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_unauthorized_access(client: TestClient):
    """Test accessing protected endpoints without authentication"""
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_inactive_user_access(client: TestClient):
    """Test that inactive users cannot access protected resources"""
    # Login as admin
    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin123"},
    )
    token = login_response.json()["access_token"]

    # Create an inactive user
    fake_users_db["inactive"] = UserInDB(
        id="inactive_id",
        username="inactive",
        email="inactive@example.com",
        full_name="Inactive User",
        hashed_password=get_password_hash("password"),
        role="operator",
        is_active=False,
        created_at=datetime.now(tz=timezone.utc),
    )

    # Login as inactive user
    inactive_response = client.post(
        "/api/v1/auth/token",
        data={"username": "inactive", "password": "password"},
    )
    inactive_token = inactive_response.json()["access_token"]

    # Try to access protected endpoint
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {inactive_token}"},
    )

    assert response.status_code == 400
    assert "Inactive user" in response.json()["detail"]
