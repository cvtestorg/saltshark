"""Tests for API endpoints"""
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_endpoint(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_minions(client: TestClient, api_base_url: str):
    """Test listing minions"""
    response = client.get(f"{api_base_url}/minions")
    assert response.status_code == 200
    data = response.json()
    assert "minions" in data
    assert "total" in data
    assert isinstance(data["minions"], list)
    assert data["total"] >= 0


def test_list_jobs(client: TestClient, api_base_url: str):
    """Test listing jobs"""
    response = client.get(f"{api_base_url}/jobs")
    if response.status_code != 200:
        print(f"Error response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert "total" in data
    assert isinstance(data["jobs"], list)


def test_execute_job(client: TestClient, api_base_url: str):
    """Test executing a job"""
    job_request = {
        "target": "*",
        "function": "test.ping",
        "args": [],
    }
    response = client.post(f"{api_base_url}/jobs/execute", json=job_request)
    assert response.status_code == 200
    data = response.json()
    assert "success" in data or "data" in data
