"""Salt API Client Service

This module provides a client for interacting with the SaltStack API.
"""
import httpx
from typing import Any

from app.core.config import settings


class SaltAPIClient:
    """Client for SaltStack API communication"""

    def __init__(self):
        self.base_url = settings.SALT_API_URL
        self.username = settings.SALT_API_USER
        self.password = settings.SALT_API_PASSWORD
        self.token: str | None = None
        self.client = httpx.AsyncClient(timeout=30.0)

    async def login(self) -> str:
        """Authenticate with Salt API and get token"""
        response = await self.client.post(
            f"{self.base_url}/login",
            json={
                "username": self.username,
                "password": self.password,
                "eauth": "pam",
            },
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["return"][0]["token"]
        return self.token

    async def _request(
        self, method: str, endpoint: str, **kwargs
    ) -> dict[str, Any]:
        """Make authenticated request to Salt API"""
        if not self.token:
            await self.login()

        headers = kwargs.pop("headers", {})
        headers["X-Auth-Token"] = self.token

        response = await self.client.request(
            method, f"{self.base_url}{endpoint}", headers=headers, **kwargs
        )
        response.raise_for_status()
        return response.json()

    async def list_minions(self) -> dict[str, Any]:
        """List all minions"""
        return await self._request("GET", "/minions")

    async def get_minion(self, minion_id: str) -> dict[str, Any]:
        """Get details for a specific minion"""
        return await self._request("GET", f"/minions/{minion_id}")

    async def execute_command(
        self, target: str, function: str, args: list[str] | None = None
    ) -> dict[str, Any]:
        """Execute a command on minions"""
        payload = {
            "client": "local",
            "tgt": target,
            "fun": function,
        }
        if args:
            payload["arg"] = args

        return await self._request("POST", "/", json=payload)

    async def list_jobs(self) -> dict[str, Any]:
        """List all jobs"""
        return await self._request("GET", "/jobs")

    async def get_job(self, jid: str) -> dict[str, Any]:
        """Get job details"""
        return await self._request("GET", f"/jobs/{jid}")

    async def get_grains(self, minion_id: str) -> dict[str, Any]:
        """Get grains for a minion"""
        return await self.execute_command(minion_id, "grains.items")

    async def get_pillars(self, minion_id: str) -> dict[str, Any]:
        """Get pillars for a minion"""
        return await self.execute_command(minion_id, "pillar.items")

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global client instance
salt_client = SaltAPIClient()
