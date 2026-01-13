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

    async def list_states(self) -> dict[str, Any]:
        """List available states"""
        return await self.execute_command("*", "state.show_top")

    async def apply_state(
        self, target: str, state: str, test: bool = False
    ) -> dict[str, Any]:
        """Apply a state to target minions"""
        args = [state]
        if test:
            args.append("test=True")
        return await self.execute_command(target, "state.apply", args)

    async def get_state_status(self, target: str) -> dict[str, Any]:
        """Get current state status for minions"""
        return await self.execute_command(target, "state.show_sls")

    async def highstate(self, target: str, test: bool = False) -> dict[str, Any]:
        """Apply highstate to target minions"""
        args = ["test=True"] if test else []
        return await self.execute_command(target, "state.highstate", args)

    async def list_pillar_keys(self, target: str = "*") -> dict[str, Any]:
        """List all pillar keys"""
        return await self.execute_command(target, "pillar.keys")

    async def get_pillar_item(
        self, target: str, key: str
    ) -> dict[str, Any]:
        """Get specific pillar item"""
        return await self.execute_command(target, "pillar.get", [key])

    async def list_schedules(self, target: str = "*") -> dict[str, Any]:
        """List scheduled jobs"""
        return await self.execute_command(target, "schedule.list")

    async def add_schedule(
        self, target: str, name: str, function: str, schedule: dict[str, Any]
    ) -> dict[str, Any]:
        """Add a scheduled job"""
        payload = {
            "client": "local",
            "tgt": target,
            "fun": "schedule.add",
            "arg": [name, function, schedule],
        }
        return await self._request("POST", "/", json=payload)

    async def delete_schedule(self, target: str, name: str) -> dict[str, Any]:
        """Delete a scheduled job"""
        return await self.execute_command(target, "schedule.delete", [name])

    async def list_keys(self, status: str = "all") -> dict[str, Any]:
        """List minion keys by status (accepted, denied, pending, rejected, all)"""
        payload = {
            "client": "wheel",
            "fun": "key.list_all",
        }
        return await self._request("POST", "/", json=payload)

    async def accept_key(self, minion_id: str) -> dict[str, Any]:
        """Accept a pending minion key"""
        payload = {
            "client": "wheel",
            "fun": "key.accept",
            "match": minion_id,
        }
        return await self._request("POST", "/", json=payload)

    async def delete_key(self, minion_id: str) -> dict[str, Any]:
        """Delete a minion key"""
        payload = {
            "client": "wheel",
            "fun": "key.delete",
            "match": minion_id,
        }
        return await self._request("POST", "/", json=payload)

    async def reject_key(self, minion_id: str) -> dict[str, Any]:
        """Reject a pending minion key"""
        payload = {
            "client": "wheel",
            "fun": "key.reject",
            "match": minion_id,
        }
        return await self._request("POST", "/", json=payload)

    async def run_salt_runner(self, runner: str, args: list[str] | None = None) -> dict[str, Any]:
        """Execute a Salt runner"""
        payload = {
            "client": "runner",
            "fun": runner,
        }
        if args:
            payload["arg"] = args
        return await self._request("POST", "/", json=payload)

    async def list_file_roots(self) -> dict[str, Any]:
        """List file server roots"""
        return await self.execute_command("*", "cp.list_master")

    async def list_files(self, environment: str = "base") -> dict[str, Any]:
        """List files in file server"""
        return await self.execute_command("*", "cp.list_master_files", [environment])

    async def get_file_content(self, path: str) -> dict[str, Any]:
        """Get content of a file from file server"""
        return await self.execute_command("*", "cp.get_file_str", [f"salt://{path}"])

    async def orchestrate(
        self, orchestration: str, target: str = "*"
    ) -> dict[str, Any]:
        """Run a Salt orchestration"""
        payload = {
            "client": "runner",
            "fun": "state.orchestrate",
            "arg": [orchestration],
            "kwarg": {"pillar": {"target": target}},
        }
        return await self._request("POST", "/", json=payload)

    async def list_beacons(self, target: str = "*") -> dict[str, Any]:
        """List configured beacons"""
        return await self.execute_command(target, "beacons.list")

    async def add_beacon(
        self, target: str, name: str, beacon_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Add a beacon"""
        return await self.execute_command(
            target, "beacons.add", [name, beacon_data]
        )

    async def delete_beacon(self, target: str, name: str) -> dict[str, Any]:
        """Delete a beacon"""
        return await self.execute_command(target, "beacons.delete", [name])

    async def list_returners(self) -> dict[str, Any]:
        """List available returners"""
        return await self.execute_command("*", "sys.list_returner_functions")

    async def get_mine_data(self, target: str, function: str) -> dict[str, Any]:
        """Get data from Salt Mine"""
        return await self.execute_command(target, "mine.get", [target, function])

    async def send_mine_data(self, target: str, function: str) -> dict[str, Any]:
        """Send data to Salt Mine"""
        return await self.execute_command(target, "mine.send", [function])

    async def list_cloud_providers(self) -> dict[str, Any]:
        """List configured cloud providers"""
        payload = {
            "client": "runner",
            "fun": "cloud.list_providers",
        }
        return await self._request("POST", "/", json=payload)

    async def list_cloud_profiles(self, provider: str | None = None) -> dict[str, Any]:
        """List cloud profiles"""
        payload = {
            "client": "runner",
            "fun": "cloud.list_profiles",
        }
        if provider:
            payload["arg"] = [provider]
        return await self._request("POST", "/", json=payload)

    async def create_cloud_instance(
        self, profile: str, names: list[str]
    ) -> dict[str, Any]:
        """Create cloud instances"""
        payload = {
            "client": "runner",
            "fun": "cloud.profile",
            "arg": [profile],
            "kwarg": {"names": names},
        }
        return await self._request("POST", "/", json=payload)

    async def ssh_execute(
        self, target: str, function: str, roster: str = "flat"
    ) -> dict[str, Any]:
        """Execute command via Salt SSH"""
        payload = {
            "client": "ssh",
            "tgt": target,
            "fun": function,
            "roster": roster,
        }
        return await self._request("POST", "/", json=payload)

    async def get_events(self, tag: str = "") -> dict[str, Any]:
        """Subscribe to Salt event stream"""
        # Note: This would typically use SSE or WebSocket
        # For now, return recent events
        payload = {
            "client": "runner",
            "fun": "event.get_event",
            "kwarg": {"tag": tag, "wait": 5},
        }
        return await self._request("POST", "/", json=payload)

    async def list_nodegroups(self) -> dict[str, Any]:
        """List configured nodegroups"""
        # Nodegroups are typically defined in master config
        # We can get them via runner
        payload = {
            "client": "runner",
            "fun": "config.get",
            "arg": ["nodegroups"],
        }
        return await self._request("POST", "/", json=payload)

    async def list_reactor_systems(self) -> dict[str, Any]:
        """List configured reactor systems"""
        payload = {
            "client": "runner",
            "fun": "config.get",
            "arg": ["reactor"],
        }
        return await self._request("POST", "/", json=payload)

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global client instance
salt_client = SaltAPIClient()
