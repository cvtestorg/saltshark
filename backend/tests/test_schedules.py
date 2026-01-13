"""Tests for schedule management endpoints"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


def test_list_schedules(client: TestClient, api_base_url: str):
    """Test listing scheduled jobs"""
    mock_response = {
        "return": [
            {
                "minion-1": {
                    "daily_backup": {
                        "function": "cmd.run",
                        "seconds": 86400,
                        "args": ["backup.sh"],
                    },
                    "hourly_check": {
                        "function": "test.ping",
                        "seconds": 3600,
                    },
                }
            }
        ]
    }

    with patch(
        "app.services.salt_api.salt_client.list_schedules", new_callable=AsyncMock
    ) as mock_list:
        mock_list.return_value = mock_response
        response = client.get(f"{api_base_url}/schedules/*")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        mock_list.assert_called_once_with("*")


def test_list_schedules_specific_target(client: TestClient, api_base_url: str):
    """Test listing schedules for specific target"""
    mock_response = {"return": [{"minion-2": {"test_schedule": {}}}]}

    with patch(
        "app.services.salt_api.salt_client.list_schedules", new_callable=AsyncMock
    ) as mock_list:
        mock_list.return_value = mock_response
        response = client.get(f"{api_base_url}/schedules/minion-2")

        assert response.status_code == 200
        mock_list.assert_called_once_with("minion-2")


def test_add_schedule(client: TestClient, api_base_url: str):
    """Test adding a scheduled job"""
    mock_response = {"return": [{"minion-1": True}]}

    schedule_data = {
        "target": "minion-1",
        "name": "daily_backup",
        "function": "cmd.run",
        "schedule": {
            "seconds": 86400,
            "args": ["backup.sh"],
        },
    }

    with patch(
        "app.services.salt_api.salt_client.add_schedule", new_callable=AsyncMock
    ) as mock_add:
        mock_add.return_value = mock_response
        response = client.post(f"{api_base_url}/schedules", json=schedule_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "added" in data["message"].lower()


def test_delete_schedule(client: TestClient, api_base_url: str):
    """Test deleting a scheduled job"""
    mock_response = {"return": [{"minion-1": True}]}

    with patch(
        "app.services.salt_api.salt_client.delete_schedule", new_callable=AsyncMock
    ) as mock_delete:
        mock_delete.return_value = mock_response
        response = client.delete(f"{api_base_url}/schedules/minion-1/daily_backup")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deleted" in data["message"].lower()
        mock_delete.assert_called_once_with("minion-1", "daily_backup")


def test_add_schedule_error(client: TestClient, api_base_url: str):
    """Test schedule add error handling"""
    schedule_data = {
        "target": "minion-1",
        "name": "test",
        "function": "invalid.function",
        "schedule": {},
    }

    with patch(
        "app.services.salt_api.salt_client.add_schedule",
        new_callable=AsyncMock,
        side_effect=Exception("Invalid function"),
    ):
        response = client.post(f"{api_base_url}/schedules", json=schedule_data)

        assert response.status_code == 500
        assert "Invalid function" in response.json()["detail"]
