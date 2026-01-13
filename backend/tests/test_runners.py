"""Tests for Salt runners endpoints"""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


def test_execute_runner(client: TestClient, api_base_url: str):
    """Test executing a Salt runner"""
    mock_response = {
        "return": [
            {
                "up": ["minion-1", "minion-2"],
                "down": ["minion-3"],
            }
        ]
    }

    runner_data = {
        "runner": "manage.status",
        "args": [],
    }

    with patch("app.services.salt_api.salt_client.run_salt_runner", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = mock_response
        response = client.post(f"{api_base_url}/runners/execute", json=runner_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "executed" in data["message"].lower()
        mock_run.assert_called_once_with(runner="manage.status", args=None)


def test_execute_runner_with_args(client: TestClient, api_base_url: str):
    """Test executing runner with arguments"""
    mock_response = {"return": [{"versions": {"minion-1": "3005.1"}}]}

    runner_data = {
        "runner": "manage.versions",
        "args": ["3005"],
    }

    with patch("app.services.salt_api.salt_client.run_salt_runner", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = mock_response
        response = client.post(f"{api_base_url}/runners/execute", json=runner_data)

        assert response.status_code == 200
        mock_run.assert_called_once_with(runner="manage.versions", args=["3005"])


def test_list_common_runners(client: TestClient, api_base_url: str):
    """Test listing common runners"""
    response = client.get(f"{api_base_url}/runners/common")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "runners" in data
    assert isinstance(data["runners"], list)
    assert len(data["runners"]) > 0

    # Check that each runner has expected fields
    for runner in data["runners"]:
        assert "name" in runner
        assert "description" in runner
        assert "category" in runner


def test_execute_runner_error(client: TestClient, api_base_url: str):
    """Test runner execution error handling"""
    runner_data = {
        "runner": "invalid.runner",
        "args": [],
    }

    with patch(
        "app.services.salt_api.salt_client.run_salt_runner",
        new_callable=AsyncMock,
        side_effect=Exception("Runner not found"),
    ):
        response = client.post(f"{api_base_url}/runners/execute", json=runner_data)

        assert response.status_code == 500
        assert "Runner not found" in response.json()["detail"]
