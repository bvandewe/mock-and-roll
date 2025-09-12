"""Use cases for server management."""

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..domain.entities import SearchResult, ServerConfig, ServerInstance, ServerStatus
from ..domain.repositories import (
    LogSearchRepository,
    ProcessRepository,
    ServerConfigRepository,
    ServerInstanceRepository,
)


class StartServerUseCase:
    """Use case for starting a server."""

    def __init__(self, server_repo: ServerInstanceRepository, config_repo: ServerConfigRepository, process_repo: ProcessRepository, project_root: Path):
        self.server_repo = server_repo
        self.config_repo = config_repo
        self.process_repo = process_repo
        self.project_root = project_root

    def execute(self, config_name: str, port: Optional[int] = None, host: str = "0.0.0.0", reload: bool = False) -> ServerInstance:
        """Start a server with the given configuration."""
        # Find and validate configuration
        config = self.config_repo.find_by_name(config_name)
        if not config:
            raise ValueError(f"Configuration '{config_name}' not found")

        if not config.is_valid():
            raise ValueError(f"Configuration '{config_name}' is invalid")

        # Check for existing server
        existing = self.server_repo.find_by_config(config_name)
        if existing and existing.is_running:
            raise ValueError(f"Server with configuration '{config_name}' is already running")

        # Determine port
        if port is None:
            port = self.process_repo.find_next_available_port()
        else:
            existing_pid = self.process_repo.find_by_port(port)
            if existing_pid:
                raise ValueError(f"Port {port} is already in use by process {existing_pid}")

        # Create server instance first to generate timestamped log file path
        instance = ServerInstance(config_name=config_name, port=port, pid=0, host=host, status=ServerStatus.STARTING)

        # Ensure log file path is set
        if instance.log_file is None:
            raise RuntimeError("Failed to generate log file path for server instance")

        # Start server process with the log file path
        process = self._start_server_process(config, port, host, reload, instance.log_file)

        # Update instance with actual PID and set as running
        instance.pid = process.pid
        instance.status = ServerStatus.RUNNING

        # Save to repository
        self.server_repo.save(instance)

        return instance

    def _start_server_process(self, config: ServerConfig, port: int, host: str, reload: bool, log_file_path: str) -> subprocess.Popen:
        """Start the actual server process with specified log file path."""
        import os

        # Prepare environment
        env = os.environ.copy()
        # Make sure config path is absolute
        if config.path.is_absolute():
            env["CONFIG_FOLDER"] = str(config.path)
        else:
            env["CONFIG_FOLDER"] = str(self.project_root / config.path)
        env["LOG_FILE"] = log_file_path  # Pass the timestamped log file path
        env["PYTHONPATH"] = str(self.project_root / "src")

        # Build command
        cmd = [sys.executable, "-m", "uvicorn", "src.main:app", "--host", host, "--port", str(port)]

        if reload:
            cmd.append("--reload")

        # Start process
        process = subprocess.Popen(cmd, cwd=self.project_root, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Give it a moment to start
        import time

        time.sleep(2)

        # Check if process started successfully
        if process.poll() is not None:
            # Capture stderr to show the actual error
            stdout, stderr = process.communicate(timeout=1)
            error_msg = stderr.decode("utf-8") if stderr else "Unknown error"
            raise RuntimeError(f"Failed to start server process: {error_msg.strip()}")

        return process


class StopServerUseCase:
    """Use case for stopping a server."""

    def __init__(self, server_repo: ServerInstanceRepository, process_repo: ProcessRepository):
        self.server_repo = server_repo
        self.process_repo = process_repo

    def execute_by_config(self, config_name: str) -> bool:
        """Stop server by configuration name."""
        instance = self.server_repo.find_by_config(config_name)
        if not instance:
            raise ValueError(f"No server found for configuration '{config_name}'")

        return self._stop_instance(instance)

    def execute_by_port(self, port: int) -> bool:
        """Stop server by port."""
        instance = self.server_repo.find_by_port(port)
        if not instance:
            raise ValueError(f"No server found on port {port}")

        return self._stop_instance(instance)

    def execute_by_pid(self, pid: int) -> bool:
        """Stop server by process ID."""
        instance = self.server_repo.find_by_id(pid)
        if not instance:
            raise ValueError(f"No server found with PID {pid}")

        return self._stop_instance(instance)

    def execute_all(self) -> list[bool]:
        """Stop all running servers."""
        instances = self.server_repo.find_all()
        results = []

        for instance in instances:
            if instance.is_running:
                results.append(self._stop_instance(instance))

        return results

    def _stop_instance(self, instance: ServerInstance) -> bool:
        """Stop a specific server instance."""
        success = self.process_repo.terminate(instance.pid)

        if success:
            instance.status = ServerStatus.STOPPED
            self.server_repo.remove(instance)

        return success


class ListServersUseCase:
    """Use case for listing servers."""

    def __init__(self, server_repo: ServerInstanceRepository, process_repo: ProcessRepository):
        self.server_repo = server_repo
        self.process_repo = process_repo

    def execute(self) -> list[ServerInstance]:
        """List all servers and update their status."""
        instances = self.server_repo.find_all()
        updated_instances = []

        for instance in instances:
            # Update status based on actual process state
            if self.process_repo.exists(instance.pid):
                instance.status = ServerStatus.RUNNING
                updated_instances.append(instance)
            else:
                instance.status = ServerStatus.STOPPED
                # Remove dead processes from tracking
                self.server_repo.remove(instance)

        return updated_instances


class GetConfigurationsUseCase:
    """Use case for getting available configurations."""

    def __init__(self, config_repo: ServerConfigRepository):
        self.config_repo = config_repo

    def execute(self) -> list[ServerConfig]:
        """Get all available configurations."""
        return self.config_repo.find_all()

    def find_by_name(self, name: str) -> Optional[ServerConfig]:
        """Find configuration by name."""
        return self.config_repo.find_by_name(name)


class SearchLogsUseCase:
    """Use case for searching server logs."""

    def __init__(self, log_search_repo: LogSearchRepository, server_repo: ServerInstanceRepository, config_repo: ServerConfigRepository):
        self.log_search_repo = log_search_repo
        self.server_repo = server_repo
        self.config_repo = config_repo

    def execute(self, path_regex: str, config_name: Optional[str] = None, port: Optional[int] = None, since_timestamp: Optional[datetime] = None, use_all_logs: bool = False) -> SearchResult:
        """Search logs for requests matching the path regex.

        Args:
            path_regex: Regular expression to match request paths
            config_name: Optional config name to search logs for
            port: Optional port to search logs for
            since_timestamp: Optional timestamp to filter logs from
            use_all_logs: If True, search all available log files

        Returns:
            SearchResult with matched requests grouped by status code

        Raises:
            ValueError: If no log file can be found or determined
        """
        log_file_paths = self._determine_log_files(config_name, port, use_all_logs)

        if not log_file_paths:
            raise ValueError("Could not determine log files to search")

        # If multiple log files, combine results
        if len(log_file_paths) == 1:
            return self.log_search_repo.search_logs(log_file_paths[0], path_regex, since_timestamp)
        else:
            return self._search_multiple_log_files(log_file_paths, path_regex, since_timestamp)

    def _determine_log_files(self, config_name: Optional[str], port: Optional[int], use_all_logs: bool) -> list[str]:
        """Determine which log files to search.

        Args:
            config_name: Config name to filter logs for ('all' means all configs)
            port: Optional port to find specific server logs for
            use_all_logs: If True, return all available log files for selected configs

        Returns:
            List of log file paths to search
        """
        if port:
            # Port takes precedence - find the specific server's log file
            server = self.server_repo.find_by_port(port)
            if server:
                log_file = self.log_search_repo.find_log_file_for_server(server)
                if log_file:
                    return [log_file]
            raise ValueError(f"No log file found for port {port}")

        if config_name == "all":
            # Handle "all" config - search across all configs
            if use_all_logs:
                # All log files for all configs
                return self.log_search_repo.list_available_log_files()
            else:
                # Most recent log file for each config
                return self._get_most_recent_logs_per_config()

        elif config_name:
            # Specific config name
            if use_all_logs:
                # All log files for this specific config
                config_logs = self.log_search_repo.list_available_log_files(config_name)
                if config_logs:
                    return config_logs
            else:
                # Most recent log file for this specific config
                config_logs = self.log_search_repo.list_available_log_files(config_name)
                if config_logs:
                    # Return only the most recent (first in the list)
                    return [config_logs[0]]

            # Also check if there's a running server with this config
            server = self.server_repo.find_by_config(config_name)
            if server:
                log_file = self.log_search_repo.find_log_file_for_server(server)
                if log_file:
                    return [log_file]

            raise ValueError(f"No log files found for config '{config_name}'")

        # This should not happen with the new mandatory config parameter
        raise ValueError("Config name is required. Use 'all' to search all configs.")

    def _get_most_recent_logs_per_config(self) -> list[str]:
        """Get the most recent log file for each config type.

        Returns:
            List of most recent log file paths for each config
        """
        import re
        from collections import defaultdict

        all_logs = self.log_search_repo.list_available_log_files()
        config_logs = defaultdict(list)

        # Group log files by config name (extract from filename pattern)
        log_pattern = re.compile(r"(\d{8}_\d{6})_([^_]+)_(\d+)\.logs")

        for log_file in all_logs:
            filename = log_file.split("/")[-1] if "/" in log_file else log_file
            match = log_pattern.match(filename)
            if match:
                timestamp, config, port = match.groups()
                config_logs[config].append(log_file)

        # Return the first (most recent) log file for each config
        most_recent_logs = []
        for config, logs in config_logs.items():
            if logs:
                most_recent_logs.append(logs[0])  # logs are sorted by timestamp desc

        return most_recent_logs

    def _search_multiple_log_files(self, log_file_paths: list[str], path_regex: str, since_timestamp: Optional[datetime] = None) -> SearchResult:
        """Search multiple log files and combine results.

        Args:
            log_file_paths: List of log file paths to search
            path_regex: Regular expression to match request paths
            since_timestamp: Optional timestamp to filter logs from

        Returns:
            Combined SearchResult from all log files
        """
        import time
        from collections import defaultdict

        start_time = time.time()

        # Combine results from all log files
        all_matched_requests = []
        all_status_summary = defaultdict(int)
        total_requests = 0
        log_files_searched = []

        for log_file_path in log_file_paths:
            try:
                result = self.log_search_repo.search_logs(log_file_path, path_regex, since_timestamp)
                all_matched_requests.extend(result.matched_requests)
                total_requests += result.total_requests
                log_files_searched.append(log_file_path)

                # Combine status code summaries
                for status_key, count in result.status_code_summary.items():
                    all_status_summary[status_key] += count

            except (FileNotFoundError, Exception) as e:
                # Log the error but continue with other files
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to search log file {log_file_path}: {e}")
                continue

        # Sort combined results by timestamp (newest first)
        all_matched_requests.sort(key=lambda x: x.timestamp, reverse=True)

        # Calculate search duration
        search_duration_ms = (time.time() - start_time) * 1000

        # Create combined result
        from ..domain.entities import SearchResult

        return SearchResult(path_pattern=path_regex, log_files=log_files_searched, total_requests=total_requests, matched_requests=all_matched_requests, status_code_summary=dict(all_status_summary), search_duration_ms=search_duration_ms, since_timestamp=since_timestamp)
