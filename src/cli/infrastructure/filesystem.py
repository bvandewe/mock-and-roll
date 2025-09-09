"""File system repository implementations."""

import json
from pathlib import Path
from typing import Optional

from ..domain.entities import ApiKey, ConfigType, ServerConfig, ServerInstance
from ..domain.repositories import ServerConfigRepository, ServerInstanceRepository


class FileSystemServerInstanceRepository(ServerInstanceRepository):
    """File system implementation of server instance repository."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.state_dir = project_root / ".server_state"
        self.servers_file = self.state_dir / "servers.json"
        self._ensure_state_dir()

    def _ensure_state_dir(self):
        """Ensure state directory and file exist."""
        self.state_dir.mkdir(exist_ok=True)
        if not self.servers_file.exists():
            self._save_servers([])

    def _load_servers(self) -> list[dict]:
        """Load servers from state file."""
        try:
            with open(self.servers_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_servers(self, servers_data: list[dict]):
        """Save servers to state file."""
        with open(self.servers_file, "w") as f:
            json.dump(servers_data, f, indent=2)

    def save(self, instance: ServerInstance) -> None:
        """Save a server instance."""
        servers_data = self._load_servers()

        # Remove any existing entries for this config/port
        servers_data = [s for s in servers_data if s.get("config") != instance.config_name and s.get("port") != instance.port]

        # Add new instance
        servers_data.append(instance.to_dict())
        self._save_servers(servers_data)

    def find_by_id(self, pid: int) -> Optional[ServerInstance]:
        """Find server instance by process ID."""
        servers_data = self._load_servers()
        for server_data in servers_data:
            if server_data.get("pid") == pid:
                return ServerInstance.from_dict(server_data)
        return None

    def find_by_port(self, port: int) -> Optional[ServerInstance]:
        """Find server instance by port."""
        servers_data = self._load_servers()
        for server_data in servers_data:
            if server_data.get("port") == port and server_data.get("status") == "running":
                return ServerInstance.from_dict(server_data)
        return None

    def find_by_config(self, config_name: str) -> Optional[ServerInstance]:
        """Find server instance by configuration name."""
        servers_data = self._load_servers()
        for server_data in servers_data:
            if server_data.get("config") == config_name:
                return ServerInstance.from_dict(server_data)
        return None

    def find_all(self) -> list[ServerInstance]:
        """Find all server instances."""
        servers_data = self._load_servers()
        return [ServerInstance.from_dict(data) for data in servers_data]

    def remove(self, instance: ServerInstance) -> None:
        """Remove a server instance."""
        self.remove_by_id(instance.pid)

    def remove_by_id(self, pid: int) -> None:
        """Remove server instance by process ID."""
        servers_data = self._load_servers()
        servers_data = [s for s in servers_data if s.get("pid") != pid]
        self._save_servers(servers_data)


class FileSystemServerConfigRepository(ServerConfigRepository):
    """File system implementation of server config repository."""

    def __init__(self, configs_dir: Path):
        self.configs_dir = configs_dir

    def find_all(self) -> list[ServerConfig]:
        """Find all available configurations."""
        if not self.configs_dir.exists():
            return []

        configs = []
        for item in self.configs_dir.iterdir():
            if item.is_dir():
                config_type = self._determine_config_type(item.name)
                description = self._get_config_description(item)
                configs.append(ServerConfig(name=item.name, path=item, config_type=config_type, description=description))

        return sorted(configs, key=lambda c: c.name)

    def find_by_name(self, name: str) -> Optional[ServerConfig]:
        """Find configuration by name."""
        config_path = self.configs_dir / name
        if not config_path.exists() or not config_path.is_dir():
            return None

        config_type = self._determine_config_type(name)
        description = self._get_config_description(config_path)

        return ServerConfig(name=name, path=config_path, config_type=config_type, description=description)

    def get_api_key(self, config: ServerConfig) -> Optional[ApiKey]:
        """Get system API key for configuration."""
        try:
            with open(config.auth_file, "r") as f:
                auth_data = json.load(f)

            # Look for system API key
            auth_methods = auth_data.get("authentication_methods", {})
            system_auth = auth_methods.get("system_api_key", {})

            if system_auth and "valid_keys" in system_auth:
                keys = system_auth["valid_keys"]
                if keys:
                    return ApiKey(value=keys[0], name=system_auth.get("name", "X-API-Key"))

            return None
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return None

    def _determine_config_type(self, name: str) -> ConfigType:
        """Determine configuration type from name."""
        name_lower = name.lower()
        if name_lower == "basic":
            return ConfigType.BASIC
        elif name_lower == "persistence":
            return ConfigType.PERSISTENCE
        elif name_lower == "vmanage":
            return ConfigType.VMANAGE
        else:
            return ConfigType.BASIC  # Default

    def _get_config_description(self, config_path: Path) -> Optional[str]:
        """Get description for a configuration."""
        descriptions = {"basic": "Basic mock server setup", "persistence": "Redis-enabled configuration", "vmanage": "vManage SD-WAN API mock"}
        return descriptions.get(config_path.name)
