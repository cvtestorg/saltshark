"""Tests for API endpoints"""
from unittest.mock import AsyncMock, patch
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
    # Mock the Salt API response
    mock_salt_response = {
        "return": [
            {
                "minion-1": {"id": "minion-1", "os": "Ubuntu", "osrelease": "22.04", "status": "up"},
                "minion-2": {"id": "minion-2", "os": "CentOS", "osrelease": "8", "status": "up"},
            }
        ]
    }
    
    with patch('app.services.salt_api.salt_client.list_minions', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_salt_response
        response = client.get(f"{api_base_url}/minions")
        assert response.status_code == 200
        data = response.json()
        assert "minions" in data
        assert "total" in data
        assert isinstance(data["minions"], list)
        assert data["total"] >= 0


def test_list_jobs(client: TestClient, api_base_url: str):
    """Test listing jobs"""
    # Mock the Salt API response
    mock_salt_response = {
        "return": [
            {
                "20240113001": {
                    "jid": "20240113001",
                    "function": "test.ping",
                    "minions": ["minion-1"],
                    "start_time": "2024-01-13T08:00:00",
                    "status": "completed",
                }
            }
        ]
    }
    
    with patch('app.services.salt_api.salt_client.list_jobs', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_salt_response
        response = client.get(f"{api_base_url}/jobs")
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert "total" in data
        assert isinstance(data["jobs"], list)


def test_execute_job(client: TestClient, api_base_url: str):
    """Test executing a job"""
    # Mock the Salt API response
    mock_salt_response = {"return": [{"minion-1": True, "minion-2": True}]}
    
    job_request = {
        "target": "*",
        "function": "test.ping",
        "args": [],
    }
    
    with patch('app.services.salt_api.salt_client.execute_command', new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_salt_response
        response = client.post(f"{api_base_url}/jobs/execute", json=job_request)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data or "data" in data

