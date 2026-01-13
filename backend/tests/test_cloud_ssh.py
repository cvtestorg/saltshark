"""Tests for SSH and cloud endpoints"""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


def test_execute_ssh(client: TestClient, api_base_url: str):
    """Test executing command via Salt SSH"""
    mock_response = {
        "return": [
            {
                "ssh-host-1": {
                    "stdout": "Hello from SSH",
                    "retcode": 0,
                }
            }
        ]
    }

    ssh_data = {
        "target": "ssh-host-1",
        "function": "cmd.run",
        "roster": "flat",
    }

    with patch("app.services.salt_api.salt_client.ssh_execute", new_callable=AsyncMock) as mock_ssh:
        mock_ssh.return_value = mock_response
        response = client.post(f"{api_base_url}/ssh/execute", json=ssh_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "executed" in data["message"].lower()


def test_list_cloud_providers(client: TestClient, api_base_url: str):
    """Test listing cloud providers"""
    mock_response = {
        "return": [
            {
                "aws": {"driver": "ec2"},
                "digitalocean": {"driver": "digitalocean"},
            }
        ]
    }

    with patch("app.services.salt_api.salt_client.list_cloud_providers", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_response
        response = client.get(f"{api_base_url}/cloud/providers")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


def test_list_cloud_profiles(client: TestClient, api_base_url: str):
    """Test listing cloud profiles"""
    mock_response = {
        "return": [
            {
                "aws_ubuntu": {"provider": "aws", "size": "t2.micro"},
                "do_ubuntu": {"provider": "digitalocean", "size": "1gb"},
            }
        ]
    }

    with patch("app.services.salt_api.salt_client.list_cloud_profiles", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_response
        response = client.get(f"{api_base_url}/cloud/profiles")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


def test_create_cloud_instance(client: TestClient, api_base_url: str):
    """Test creating cloud instances"""
    mock_response = {
        "return": [
            {
                "web-01": {
                    "provider": "aws",
                    "state": "running",
                    "public_ip": "1.2.3.4",
                }
            }
        ]
    }

    instance_data = {
        "profile": "aws_ubuntu",
        "names": ["web-01", "web-02"],
    }

    with patch("app.services.salt_api.salt_client.create_cloud_instance", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        response = client.post(f"{api_base_url}/cloud/instances", json=instance_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Creating instances" in data["message"]
