"""Tests for beacons and mine endpoints"""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


def test_list_beacons(client: TestClient, api_base_url: str):
    """Test listing configured beacons"""
    mock_response = {
        "return": [
            {
                "minion-1": {
                    "diskusage": [
                        {"interval": 60},
                        {"/": "90%"},
                    ],
                    "service": [
                        {"nginx": {}},
                    ],
                }
            }
        ]
    }

    with patch("app.services.salt_api.salt_client.list_beacons", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_response
        response = client.get(f"{api_base_url}/beacons/minion-1")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


def test_add_beacon(client: TestClient, api_base_url: str):
    """Test adding a beacon"""
    mock_response = {"return": [{"minion-1": True}]}

    beacon_data = {
        "target": "minion-1",
        "name": "diskusage",
        "config": {
            "interval": 60,
            "/": "90%",
        },
    }

    with patch("app.services.salt_api.salt_client.add_beacon", new_callable=AsyncMock) as mock_add:
        mock_add.return_value = mock_response
        response = client.post(f"{api_base_url}/beacons", json=beacon_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "added" in data["message"].lower()


def test_delete_beacon(client: TestClient, api_base_url: str):
    """Test deleting a beacon"""
    mock_response = {"return": [{"minion-1": True}]}

    with patch("app.services.salt_api.salt_client.delete_beacon", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = mock_response
        response = client.delete(f"{api_base_url}/beacons/minion-1/diskusage")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deleted" in data["message"].lower()


def test_get_mine_data(client: TestClient, api_base_url: str):
    """Test getting data from Salt Mine"""
    mock_response = {
        "return": [
            {
                "minion-1": {
                    "network.ip_addrs": ["192.168.1.10"],
                }
            }
        ]
    }

    mine_data = {
        "target": "minion-1",
        "function": "network.ip_addrs",
    }

    with patch("app.services.salt_api.salt_client.get_mine_data", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        response = client.post(f"{api_base_url}/mine/get", json=mine_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


def test_send_mine_data(client: TestClient, api_base_url: str):
    """Test sending data to Salt Mine"""
    mock_response = {"return": [{"minion-1": True}]}

    mine_data = {
        "target": "minion-1",
        "function": "network.ip_addrs",
    }

    with patch("app.services.salt_api.salt_client.send_mine_data", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = mock_response
        response = client.post(f"{api_base_url}/mine/send", json=mine_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


def test_list_returners(client: TestClient, api_base_url: str):
    """Test listing available returners"""
    mock_response = {
        "return": [
            {
                "minion-1": [
                    "mysql.returner",
                    "postgres.returner",
                    "redis.returner",
                ]
            }
        ]
    }

    with patch("app.services.salt_api.salt_client.list_returners", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_response
        response = client.get(f"{api_base_url}/mine/returners")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
