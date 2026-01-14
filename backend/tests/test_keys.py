"""Tests for minion key management endpoints"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


def test_list_keys(client: TestClient, api_base_url: str):
    """Test listing all minion keys"""
    mock_response = {
        "return": [
            {
                "data": {
                    "return": {
                        "minions": ["minion-1", "minion-2"],
                        "minions_pre": ["minion-3"],
                        "minions_denied": [],
                        "minions_rejected": [],
                    }
                }
            }
        ]
    }

    with patch(
        "app.services.salt_api.salt_client.list_keys", new_callable=AsyncMock
    ) as mock_list:
        mock_list.return_value = mock_response
        response = client.get(f"{api_base_url}/keys")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


def test_accept_key(client: TestClient, api_base_url: str):
    """Test accepting a pending minion key"""
    mock_response = {"return": [{"data": {"return": {"minions": ["minion-3"]}}}]}

    with patch(
        "app.services.salt_api.salt_client.accept_key", new_callable=AsyncMock
    ) as mock_accept:
        mock_accept.return_value = mock_response
        response = client.post(f"{api_base_url}/keys/minion-3/accept")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "accepted" in data["message"].lower()
        mock_accept.assert_called_once_with("minion-3")


def test_reject_key(client: TestClient, api_base_url: str):
    """Test rejecting a pending minion key"""
    mock_response = {
        "return": [{"data": {"return": {"minions_rejected": ["minion-4"]}}}]
    }

    with patch(
        "app.services.salt_api.salt_client.reject_key", new_callable=AsyncMock
    ) as mock_reject:
        mock_reject.return_value = mock_response
        response = client.post(f"{api_base_url}/keys/minion-4/reject")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "rejected" in data["message"].lower()
        mock_reject.assert_called_once_with("minion-4")


def test_delete_key(client: TestClient, api_base_url: str):
    """Test deleting a minion key"""
    mock_response = {"return": [{"data": {"return": {"minions": []}}}]}

    with patch(
        "app.services.salt_api.salt_client.delete_key", new_callable=AsyncMock
    ) as mock_delete:
        mock_delete.return_value = mock_response
        response = client.delete(f"{api_base_url}/keys/minion-5")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deleted" in data["message"].lower()
        mock_delete.assert_called_once_with("minion-5")


def test_accept_key_error(client: TestClient, api_base_url: str):
    """Test key accept error handling"""
    with patch(
        "app.services.salt_api.salt_client.accept_key",
        new_callable=AsyncMock,
        side_effect=Exception("Key not found"),
    ):
        response = client.post(f"{api_base_url}/keys/invalid/accept")

        assert response.status_code == 500
        assert "Key not found" in response.json()["detail"]
