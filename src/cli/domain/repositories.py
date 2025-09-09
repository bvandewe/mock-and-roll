"""Repository interfaces for the domain layer."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from .entities import ApiKey, SearchResult, ServerConfig, ServerInstance


class ServerInstanceRepository(ABC):
    """Repository interface for server instances."""

    @abstractmethod
    def save(self, instance: ServerInstance) -> None:
        """Save a server instance."""

    @abstractmethod
    def find_by_id(self, pid: int) -> Optional[ServerInstance]:
        """Find server instance by process ID."""

    @abstractmethod
    def find_by_port(self, port: int) -> Optional[ServerInstance]:
        """Find server instance by port."""

    @abstractmethod
    def find_by_config(self, config_name: str) -> Optional[ServerInstance]:
        """Find server instance by configuration name."""

    @abstractmethod
    def find_all(self) -> list[ServerInstance]:
        """Find all server instances."""

    @abstractmethod
    def remove(self, instance: ServerInstance) -> None:
        """Remove a server instance."""

    @abstractmethod
    def remove_by_id(self, pid: int) -> None:
        """Remove server instance by process ID."""


class ServerConfigRepository(ABC):
    """Repository interface for server configurations."""

    @abstractmethod
    def find_all(self) -> list[ServerConfig]:
        """Find all available configurations."""

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[ServerConfig]:
        """Find configuration by name."""

    @abstractmethod
    def get_api_key(self, config: ServerConfig) -> Optional[ApiKey]:
        """Get system API key for configuration."""


class ProcessRepository(ABC):
    """Repository interface for process management."""

    @abstractmethod
    def exists(self, pid: int) -> bool:
        """Check if process exists."""

    @abstractmethod
    def find_by_port(self, port: int) -> Optional[int]:
        """Find process ID using specific port."""

    @abstractmethod
    def is_mock_server(self, pid: int) -> bool:
        """Check if process is a mock server."""

    @abstractmethod
    def terminate(self, pid: int, timeout: int = 10) -> bool:
        """Terminate process gracefully."""

    @abstractmethod
    def find_next_available_port(self, start_port: int = 8000) -> int:
        """Find next available port."""


class LogSearchRepository(ABC):
    """Repository interface for searching logs."""

    @abstractmethod
    def search_logs(self, log_file_path: str, path_regex: str, since_timestamp: Optional[datetime] = None) -> SearchResult:
        """Search log file for requests matching path regex.

        Args:
            log_file_path: Path to the log file to search
            path_regex: Regular expression pattern to match request paths
            since_timestamp: Optional timestamp to filter logs from

        Returns:
            SearchResult containing matched requests grouped by status code
        """

    @abstractmethod
    def find_log_file_for_server(self, server: ServerInstance) -> Optional[str]:
        """Find the log file path for a server instance.

        Args:
            server: Server instance to find log file for

        Returns:
            Path to log file if found, None otherwise
        """

    @abstractmethod
    def list_available_log_files(self, config_name: Optional[str] = None) -> list[str]:
        """List available log files.

        Args:
            config_name: Optional config name to filter by

        Returns:
            List of available log file paths
        """
