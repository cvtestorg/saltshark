"""Test configuration"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.salt_api import salt_client


@pytest.fixture(autouse=True)
def reset_salt_client():
    """Reset the Salt API client before each test"""
    # Reset token to force re-login
    salt_client.token = None
    yield
    # Clean up after test
    salt_client.token = None


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def api_base_url():
    """API base URL"""
    return "/api/v1"
