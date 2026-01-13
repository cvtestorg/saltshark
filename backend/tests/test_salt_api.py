"""Tests for the Salt API client"""
import pytest
from app.services.salt_api import SaltAPIClient


@pytest.mark.asyncio
async def test_login():
    """Test login functionality"""
    client = SaltAPIClient()
    token = await client.login()
    assert token is not None
    assert isinstance(token, str)


@pytest.mark.asyncio
async def test_list_minions():
    """Test listing minions"""
    client = SaltAPIClient()
    await client.login()
    
    result = await client.list_minions()
    assert "return" in result
    assert isinstance(result["return"], list)
    
    # Check mock data
    minions = result["return"][0]
    assert "minion-1" in minions
    assert "minion-2" in minions
    assert "minion-3" in minions


@pytest.mark.asyncio
async def test_list_jobs():
    """Test listing jobs"""
    client = SaltAPIClient()
    await client.login()
    
    result = await client.list_jobs()
    assert "return" in result
    assert isinstance(result["return"], list)
    
    # Check mock data
    jobs = result["return"][0]
    assert len(jobs) > 0


@pytest.mark.asyncio
async def test_execute_command():
    """Test executing a command"""
    client = SaltAPIClient()
    await client.login()
    
    result = await client.execute_command("*", "test.ping")
    assert result is not None
    assert "return" in result


@pytest.mark.asyncio
async def test_get_grains():
    """Test getting grains"""
    client = SaltAPIClient()
    await client.login()
    
    result = await client.get_grains("minion-1")
    assert result is not None
    assert "return" in result
