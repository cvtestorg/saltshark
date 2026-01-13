"""Tests for orchestration endpoints"""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


def test_run_orchestration(client: TestClient, api_base_url: str):
    """Test running a Salt orchestration"""
    mock_response = {
        "return": [
            {
                "data": {
                    "outputter": "highstate",
                    "data": {
                        "master": {
                            "salt_|-deploy_|-state.orchestrate.deploy_|-runner": {
                                "result": True,
                                "comment": "Successfully ran deploy orchestration",
                            }
                        }
                    },
                }
            }
        ]
    }

    orchestration_data = {
        "orchestration": "deploy.webapp",
        "target": "web-*",
    }

    with patch("app.services.salt_api.salt_client.orchestrate", new_callable=AsyncMock) as mock_orch:
        mock_orch.return_value = mock_response
        response = client.post(f"{api_base_url}/orchestration/run", json=orchestration_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "executed" in data["message"].lower()
        mock_orch.assert_called_once_with(orchestration="deploy.webapp", target="web-*")


def test_run_orchestration_default_target(client: TestClient, api_base_url: str):
    """Test orchestration with default target"""
    mock_response = {"return": [{"data": {"result": True}}]}

    orchestration_data = {
        "orchestration": "upgrade.system",
        "target": "*",
    }

    with patch("app.services.salt_api.salt_client.orchestrate", new_callable=AsyncMock) as mock_orch:
        mock_orch.return_value = mock_response
        response = client.post(f"{api_base_url}/orchestration/run", json=orchestration_data)

        assert response.status_code == 200


def test_list_common_orchestrations(client: TestClient, api_base_url: str):
    """Test listing common orchestrations"""
    response = client.get(f"{api_base_url}/orchestration/common")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "orchestrations" in data
    assert isinstance(data["orchestrations"], list)
    assert len(data["orchestrations"]) > 0

    # Check structure of orchestration entries
    for orch in data["orchestrations"]:
        assert "name" in orch
        assert "description" in orch
        assert "target" in orch


def test_run_orchestration_error(client: TestClient, api_base_url: str):
    """Test orchestration error handling"""
    orchestration_data = {
        "orchestration": "invalid.orch",
        "target": "*",
    }

    with patch(
        "app.services.salt_api.salt_client.orchestrate",
        new_callable=AsyncMock,
        side_effect=Exception("Orchestration not found"),
    ):
        response = client.post(f"{api_base_url}/orchestration/run", json=orchestration_data)

        assert response.status_code == 500
        assert "Orchestration not found" in response.json()["detail"]
