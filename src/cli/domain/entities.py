"""Domain entities for the mock server CLI."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional, Union


class ServerStatus(Enum):
    """Server status enumeration."""

    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    FAILED = "failed"


class ConfigType(Enum):
    """Configuration type enumeration."""

    BASIC = "basic"
    PERSISTENCE = "persistence"
    VMANAGE = "vmanage"


@dataclass
class ServerInstance:
    """Domain entity representing a mock server instance."""

    config_name: str
    port: int
    pid: int
    host: str = "0.0.0.0"
    status: ServerStatus = ServerStatus.RUNNING
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    log_file: Optional[str] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if self.log_file is None:
            timestamp = self.started_at.strftime("%Y%m%d_%H%M%S")
            self.log_file = f"logs/{timestamp}_{self.config_name}_{self.port}.logs"

    @property
    def is_running(self) -> bool:
        """Check if server is currently running."""
        return self.status == ServerStatus.RUNNING

    @property
    def base_url(self) -> str:
        """Get the base URL for this server."""
        return f"http://{self.host}:{self.port}"

    @property
    def docs_url(self) -> str:
        """Get the API documentation URL."""
        return f"{self.base_url}/docs"

    @property
    def openapi_url(self) -> str:
        """Get the OpenAPI schema URL."""
        return f"{self.base_url}/openapi.json"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {"config": self.config_name, "port": self.port, "pid": self.pid, "host": self.host, "status": self.status.value, "started_at": self.started_at.isoformat(), "log_file": self.log_file}

    @classmethod
    def from_dict(cls, data: dict) -> "ServerInstance":
        """Create instance from dictionary."""
        return cls(config_name=data["config"], port=data["port"], pid=data["pid"], host=data.get("host", "0.0.0.0"), status=ServerStatus(data.get("status", "running")), started_at=datetime.fromisoformat(data["started_at"]), log_file=data.get("log_file"))


@dataclass
class ServerConfig:
    """Domain entity representing a server configuration."""

    name: str
    path: Path
    config_type: ConfigType
    description: Optional[str] = None

    @property
    def api_file(self) -> Path:
        """Get path to API configuration file."""
        return self.path / "api.json"

    @property
    def auth_file(self) -> Path:
        """Get path to authentication configuration file."""
        return self.path / "auth.json"

    @property
    def endpoints_file(self) -> Path:
        """Get path to endpoints configuration file."""
        return self.path / "endpoints.json"

    @property
    def required_files(self) -> list[Path]:
        """Get list of required configuration files."""
        return [self.api_file, self.auth_file, self.endpoints_file]

    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        path_exists = self.path.exists()
        is_directory = self.path.is_dir()
        files_exist = all(f.exists() for f in self.required_files)
        return path_exists and is_directory and files_exist


@dataclass
class Port:
    """Value object representing a network port."""

    number: int

    def __post_init__(self):
        """Validate port number."""
        if not (1 <= self.number <= 65535):
            raise ValueError(f"Port number must be between 1 and 65535, got {self.number}")

    def is_available(self) -> bool:
        """Check if port is available (to be implemented in infrastructure)."""
        raise NotImplementedError("Port availability check must be implemented in infrastructure layer")


@dataclass
class ProcessId:
    """Value object representing a process ID."""

    pid: int

    def __post_init__(self):
        """Validate process ID."""
        if self.pid <= 0:
            raise ValueError(f"Process ID must be positive, got {self.pid}")

    def exists(self) -> bool:
        """Check if process exists (to be implemented in infrastructure)."""
        raise NotImplementedError("Process existence check must be implemented in infrastructure layer")


@dataclass
class LogEntry:
    """Domain entity representing a log entry."""

    timestamp: datetime
    level: str
    message: str
    correlation_id: str = ""
    logger: str = ""
    raw_line: str = ""
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None

    @classmethod
    def from_line(cls, line: str) -> Optional["LogEntry"]:
        """Parse a log line into a LogEntry."""
        import re

        # Pattern: 2025-09-09 10:00:05,158 - api.requests - INFO - [7d9f40c0] REQUEST: GET ...
        pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - ([\w\.]+) - (\w+) - \[([a-f0-9]+)\] (.+)"
        match = re.match(pattern, line.strip())

        if not match:
            return None

        timestamp_str, logger, level, correlation_id, message = match.groups()

        try:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")
        except ValueError:
            return None

        return cls(timestamp=timestamp, correlation_id=correlation_id, level=level, logger=logger, message=message, raw_line=line.strip())

    @property
    def is_error(self) -> bool:
        """Check if this is an error log entry."""
        return self.level.upper() in ("ERROR", "CRITICAL")

    @property
    def is_success(self) -> bool:
        """Check if this represents a successful request."""
        return self.status_code is not None and 200 <= self.status_code < 300


@dataclass
class TestResult:
    """Domain entity representing a test result."""

    endpoint: str
    method: str
    status_code: int
    response_time: float
    success: bool
    error_message: Optional[str] = None

    @property
    def is_success(self) -> bool:
        """Check if test was successful."""
        return self.success and 200 <= self.status_code < 300


@dataclass
class ApiKey:
    """Value object representing an API key."""

    value: str
    name: str = "X-API-Key"

    def __post_init__(self):
        """Validate API key."""
        if not self.value or not self.value.strip():
            raise ValueError("API key cannot be empty")

    @property
    def masked(self) -> str:
        """Get masked version of API key for display."""
        if len(self.value) <= 10:
            return self.value
        return f"{self.value[:10]}..."


@dataclass
class RequestResponsePair:
    """Domain entity representing a matched request/response pair."""

    correlation_id: str
    method: str
    path: str
    status_code: int
    timestamp: datetime
    response_time_ms: Optional[float] = None
    request_headers: Optional[Union[dict[str, str], str]] = None
    response_headers: Optional[Union[dict[str, str], str]] = None
    request_body: Optional[str] = None
    response_body: Optional[str] = None
    log_file_source: Optional[str] = None  # Track which log file this came from

    @classmethod
    def from_log_entries(cls, request_entry: "LogEntry", response_entry: Optional["LogEntry"] = None, request_headers_entry: Optional["LogEntry"] = None, response_headers_entry: Optional["LogEntry"] = None, response_body_entry: Optional["LogEntry"] = None) -> Optional["RequestResponsePair"]:
        """Create a RequestResponsePair from log entries."""
        import json
        import re

        # Parse request: "REQUEST: GET http://0.0.0.0:8000/items/123 from 127.0.0.1"
        request_pattern = r"REQUEST: (\w+) http://[^/]+(/[^\s]*) from"
        request_match = re.search(request_pattern, request_entry.message)

        if not request_match:
            return None

        method, path = request_match.groups()

        status_code = 200  # Default
        response_time_ms = None
        request_headers = None
        response_headers = None
        request_body = None
        response_body = None

        if response_entry:
            # Parse response: "RESPONSE: 200 for GET http://0.0.0.0:8000/items/123 - Time: 0.002s"
            response_pattern = r"RESPONSE: (\d+) for \w+ [^\s]+ - Time: ([\d\.]+)s"
            response_match = re.search(response_pattern, response_entry.message)

            if response_match:
                status_code = int(response_match.group(1))
                response_time_ms = float(response_match.group(2)) * 1000

        # Parse request headers
        if request_headers_entry:
            headers_pattern = r"Request Headers: (.+)"
            headers_match = re.search(headers_pattern, request_headers_entry.message)
            if headers_match:
                try:
                    # Replace single quotes with double quotes for valid JSON
                    headers_str = headers_match.group(1).replace("'", '"')
                    request_headers = json.loads(headers_str)
                except (json.JSONDecodeError, ValueError):
                    # If parsing fails, store as string
                    request_headers = headers_match.group(1)

        # Parse response headers
        if response_headers_entry:
            headers_pattern = r"Response Headers: (.+)"
            headers_match = re.search(headers_pattern, response_headers_entry.message)
            if headers_match:
                try:
                    # Replace single quotes with double quotes for valid JSON
                    headers_str = headers_match.group(1).replace("'", '"')
                    response_headers = json.loads(headers_str)
                except (json.JSONDecodeError, ValueError):
                    # If parsing fails, store as string
                    response_headers = headers_match.group(1)

        # Parse response body
        if response_body_entry:
            body_pattern = r"Response Body: (.+)"
            body_match = re.search(body_pattern, response_body_entry.message)
            if body_match:
                response_body = body_match.group(1)

        return cls(correlation_id=request_entry.correlation_id, method=method, path=path, status_code=status_code, timestamp=request_entry.timestamp, response_time_ms=response_time_ms, request_headers=request_headers, response_headers=response_headers, request_body=request_body, response_body=response_body)


@dataclass
class SearchResult:
    """Domain entity representing search results."""

    path_pattern: str
    log_files: list[str]  # Changed from log_file to log_files to support multiple files
    total_requests: int
    matched_requests: list[RequestResponsePair]
    status_code_summary: dict[str, int]  # status_code -> count (e.g., "status_200": 3)
    search_duration_ms: float
    since_timestamp: Optional[datetime] = None

    @property
    def log_file(self) -> str:
        """Backward compatibility property - returns first log file."""
        return self.log_files[0] if self.log_files else ""

    @property
    def success_rate(self) -> float:
        """Calculate success rate (2xx responses)."""
        if not self.total_requests:
            return 0.0

        success_count = 0
        for status_key, count in self.status_code_summary.items():
            # Extract numeric status code from "status_XXX" format
            if status_key.startswith("status_"):
                try:
                    status_code = int(status_key[7:])  # Remove "status_" prefix
                    if 200 <= status_code < 300:
                        success_count += count
                except ValueError:
                    continue

        return (success_count / self.total_requests) * 100

    def get_requests_by_status(self, status_code: int) -> list[RequestResponsePair]:
        """Get all requests with a specific status code, sorted by timestamp (newest first)."""
        matching_requests = [req for req in self.matched_requests if req.status_code == status_code]
        return sorted(matching_requests, key=lambda x: x.timestamp, reverse=True)
