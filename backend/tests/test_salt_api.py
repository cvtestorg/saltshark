"""Tests for the Salt API client"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from services.salt_api import SaltAPIClient


@pytest.mark.asyncio
async def test_login():
    """Test login functionality"""
    client = SaltAPIClient()

    # Mock the HTTP client response
    mock_response = MagicMock()
    mock_response.json = MagicMock(
        return_value={"return": [{"token": "test-token-123"}]}
    )
    mock_response.raise_for_status = MagicMock()

    client.client.post = AsyncMock(return_value=mock_response)

    token = await client.login()
    assert token == "test-token-123"
    assert client.token == "test-token-123"


@pytest.mark.asyncio
async def test_list_minions():
    """Test listing minions"""
    client = SaltAPIClient()
    client.token = "test-token"  # Set token directly

    mock_response = MagicMock()
    mock_response.json = MagicMock(
        return_value={
            "return": [
                {
                    "minion-1": {"id": "minion-1", "os": "Ubuntu"},
                    "minion-2": {"id": "minion-2", "os": "CentOS"},
                }
            ]
        }
    )
    mock_response.raise_for_status = MagicMock()

    client.client.request = AsyncMock(return_value=mock_response)

    result = await client.list_minions()
    assert "return" in result
    assert isinstance(result["return"], list)
    minions = result["return"][0]
    assert "minion-1" in minions
    assert "minion-2" in minions


@pytest.mark.asyncio
async def test_list_jobs():
    """Test listing jobs"""
    client = SaltAPIClient()
    client.token = "test-token"

    mock_response = MagicMock()
    mock_response.json = MagicMock(
        return_value={
            "return": [
                {
                    "20240113001": {
                        "jid": "20240113001",
                        "function": "test.ping",
                    }
                }
            ]
        }
    )
    mock_response.raise_for_status = MagicMock()

    client.client.request = AsyncMock(return_value=mock_response)

    result = await client.list_jobs()
    assert "return" in result
    assert isinstance(result["return"], list)
    jobs = result["return"][0]
    assert len(jobs) > 0


@pytest.mark.asyncio
async def test_execute_command():
    """Test executing a command"""
    client = SaltAPIClient()
    client.token = "test-token"

    mock_response = MagicMock()
    mock_response.json = MagicMock(return_value={"return": [{"minion-1": True}]})
    mock_response.raise_for_status = MagicMock()

    client.client.request = AsyncMock(return_value=mock_response)

    result = await client.execute_command("*", "test.ping")
    assert result is not None
    assert "return" in result


@pytest.mark.asyncio
async def test_get_grains():
    """Test getting grains"""
    client = SaltAPIClient()
    client.token = "test-token"

    mock_response = MagicMock()
    mock_response.json = MagicMock(
        return_value={"return": [{"minion-1": {"os": "Ubuntu", "kernel": "Linux"}}]}
    )
    mock_response.raise_for_status = MagicMock()

    client.client.request = AsyncMock(return_value=mock_response)

    result = await client.get_grains("minion-1")
    assert result is not None
    assert "return" in result
