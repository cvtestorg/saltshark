"""Tests for event stream and targeting endpoints"""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


def test_get_events(client: TestClient, api_base_url: str):
    """Test getting events from event stream"""
    mock_response = {
        "return": [
            {
                "tag": "salt/job/20240113/ret/minion-1",
                "data": {"fun": "test.ping", "id": "minion-1", "return": True},
            }
        ]
    }

    with patch("app.services.salt_api.salt_client.get_events", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        response = client.get(f"{api_base_url}/events")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        mock_get.assert_called_once_with("")


def test_get_events_with_tag(client: TestClient, api_base_url: str):
    """Test getting events with tag filter"""
    mock_response = {"return": [{"tag": "salt/job/*", "data": {}}]}

    with patch("app.services.salt_api.salt_client.get_events", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        response = client.get(f"{api_base_url}/events?tag=salt/job/*")

        assert response.status_code == 200
        mock_get.assert_called_once_with("salt/job/*")


def test_list_nodegroups(client: TestClient, api_base_url: str):
    """Test listing configured nodegroups"""
    mock_response = {
        "return": [
            {
                "web": "web-*",
                "db": "db-*",
                "prod": "prod-*",
            }
        ]
    }

    with patch("app.services.salt_api.salt_client.list_nodegroups", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_response
        response = client.get(f"{api_base_url}/nodegroups")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


def test_list_reactors(client: TestClient, api_base_url: str):
    """Test listing configured reactor systems"""
    mock_response = {
        "return": [
            [
                {"salt/minion/*/start": ["/srv/reactor/start.sls"]},
                {"salt/cloud/*/destroyed": ["/srv/reactor/destroy.sls"]},
            ]
        ]
    }

    with patch("app.services.salt_api.salt_client.list_reactor_systems", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_response
        response = client.get(f"{api_base_url}/reactor")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


def test_get_events_error(client: TestClient, api_base_url: str):
    """Test events endpoint error handling"""
    with patch(
        "app.services.salt_api.salt_client.get_events",
        new_callable=AsyncMock,
        side_effect=Exception("Connection error"),
    ):
        response = client.get(f"{api_base_url}/events")

        assert response.status_code == 500
        assert "Connection error" in response.json()["detail"]
