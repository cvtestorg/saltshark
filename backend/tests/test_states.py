"""Tests for state management endpoints"""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


def test_list_states(client: TestClient, api_base_url: str):
    """Test listing available states"""
    mock_response = {
        "return": [
            {
                "base": {
                    "webserver": ["webserver.nginx", "webserver.apache"],
                    "database": ["database.mysql", "database.postgresql"],
                }
            }
        ]
    }

    with patch("app.services.salt_api.salt_client.list_states", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_response
        response = client.get(f"{api_base_url}/states")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data


def test_apply_state(client: TestClient, api_base_url: str):
    """Test applying a state"""
    mock_response = {
        "return": [
            {
                "minion-1": {
                    "nginx-install": {
                        "name": "nginx",
                        "result": True,
                        "changes": {"pkg": "installed"},
                    }
                }
            }
        ]
    }

    request_data = {
        "target": "minion-1",
        "state": "webserver.nginx",
        "test": False,
    }

    with patch("app.services.salt_api.salt_client.apply_state", new_callable=AsyncMock) as mock_apply:
        mock_apply.return_value = mock_response
        response = client.post(f"{api_base_url}/states/apply", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "applied" in data["message"]
        mock_apply.assert_called_once_with(
            target="minion-1", state="webserver.nginx", test=False
        )


def test_apply_state_test_mode(client: TestClient, api_base_url: str):
    """Test applying state in test mode (dry run)"""
    mock_response = {"return": [{"minion-1": {"test": "success"}}]}

    request_data = {
        "target": "minion-1",
        "state": "webserver.nginx",
        "test": True,
    }

    with patch("app.services.salt_api.salt_client.apply_state", new_callable=AsyncMock) as mock_apply:
        mock_apply.return_value = mock_response
        response = client.post(f"{api_base_url}/states/apply", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "tested" in data["message"]
        mock_apply.assert_called_once_with(
            target="minion-1", state="webserver.nginx", test=True
        )


def test_apply_highstate(client: TestClient, api_base_url: str):
    """Test applying highstate"""
    mock_response = {
        "return": [{"minion-1": {"state1": {"result": True}, "state2": {"result": True}}}]
    }

    request_data = {"target": "*", "test": False}

    with patch("app.services.salt_api.salt_client.highstate", new_callable=AsyncMock) as mock_highstate:
        mock_highstate.return_value = mock_response
        response = client.post(f"{api_base_url}/states/highstate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "applied" in data["message"]


def test_apply_highstate_test_mode(client: TestClient, api_base_url: str):
    """Test applying highstate in test mode"""
    mock_response = {"return": [{"minion-1": {"test_results": True}}]}

    request_data = {"target": "*", "test": True}

    with patch("app.services.salt_api.salt_client.highstate", new_callable=AsyncMock) as mock_highstate:
        mock_highstate.return_value = mock_response
        response = client.post(f"{api_base_url}/states/highstate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "tested" in data["message"]


def test_get_state_status(client: TestClient, api_base_url: str):
    """Test getting state status for minions"""
    mock_response = {
        "return": [
            {
                "minion-1": {
                    "webserver": {"nginx": "running"},
                    "database": {"mysql": "stopped"},
                }
            }
        ]
    }

    with patch("app.services.salt_api.salt_client.get_state_status", new_callable=AsyncMock) as mock_status:
        mock_status.return_value = mock_response
        response = client.get(f"{api_base_url}/states/status/minion-1")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


def test_apply_state_error(client: TestClient, api_base_url: str):
    """Test state apply error handling"""
    request_data = {
        "target": "minion-1",
        "state": "invalid.state",
        "test": False,
    }

    with patch(
        "app.services.salt_api.salt_client.apply_state",
        new_callable=AsyncMock,
        side_effect=Exception("State not found"),
    ):
        response = client.post(f"{api_base_url}/states/apply", json=request_data)

        assert response.status_code == 500
        assert "State not found" in response.json()["detail"]
