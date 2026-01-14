"""Tests for grains and pillars endpoints"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


def test_get_grains(client: TestClient, api_base_url: str):
    """Test getting grains for a minion"""
    mock_response = {
        "return": [
            {
                "minion-1": {
                    "os": "Ubuntu",
                    "osrelease": "22.04",
                    "kernel": "Linux",
                    "cpuarch": "x86_64",
                }
            }
        ]
    }

    with patch(
        "app.services.salt_api.salt_client.get_grains", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_response
        response = client.get(f"{api_base_url}/minions/minion-1/grains")

        assert response.status_code == 200
        data = response.json()
        assert data["minion_id"] == "minion-1"
        assert "grains" in data
        assert data["grains"]["os"] == "Ubuntu"


def test_get_grains_error(client: TestClient, api_base_url: str):
    """Test grains endpoint error handling"""
    with patch(
        "app.services.salt_api.salt_client.get_grains",
        new_callable=AsyncMock,
        side_effect=Exception("Connection error"),
    ):
        response = client.get(f"{api_base_url}/minions/minion-1/grains")

        assert response.status_code == 500
        assert "Connection error" in response.json()["detail"]


def test_get_pillars(client: TestClient, api_base_url: str):
    """Test getting pillars for a minion"""
    mock_response = {
        "return": [
            {
                "minion-1": {
                    "app_config": {"port": 8080, "debug": False},
                    "database": {"host": "localhost"},
                }
            }
        ]
    }

    with patch(
        "app.services.salt_api.salt_client.get_pillars", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_response
        response = client.get(f"{api_base_url}/minions/minion-1/pillars")

        assert response.status_code == 200
        data = response.json()
        assert data["minion_id"] == "minion-1"
        assert "pillars" in data
        assert "app_config" in data["pillars"]


def test_list_pillar_keys(client: TestClient, api_base_url: str):
    """Test listing pillar keys"""
    mock_response = {"return": [{"minion-1": ["app_config", "database", "users"]}]}

    with patch(
        "app.services.salt_api.salt_client.list_pillar_keys", new_callable=AsyncMock
    ) as mock_list:
        mock_list.return_value = mock_response
        response = client.get(f"{api_base_url}/pillars/minion-1/keys")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data


def test_get_pillar_item(client: TestClient, api_base_url: str):
    """Test getting specific pillar item"""
    mock_response = {"return": [{"minion-1": {"port": 8080, "debug": False}}]}

    with patch(
        "app.services.salt_api.salt_client.get_pillar_item", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_response
        response = client.get(f"{api_base_url}/pillars/minion-1/item/app_config")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


def test_get_all_pillars(client: TestClient, api_base_url: str):
    """Test getting all pillars for a minion"""
    mock_response = {"return": [{"minion-1": {"key1": "value1", "key2": "value2"}}]}

    with patch(
        "app.services.salt_api.salt_client.get_pillars", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_response
        response = client.get(f"{api_base_url}/pillars/minion-1")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["minion_id"] == "minion-1"
