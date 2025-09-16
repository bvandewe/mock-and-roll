"""Command line interface handlers."""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from ..application.server_management import (
    GetConfigurationsUseCase,
    ListServersUseCase,
    SearchLogsUseCase,
    StartServerUseCase,
    StopServerUseCase,
)
from ..domain.entities import ServerInstance
from ..infrastructure.filesystem import (
    FileSystemServerConfigRepository,
    FileSystemServerInstanceRepository,
)
from ..infrastructure.log_search import FileSystemLogSearchRepository
from ..infrastructure.process import SystemProcessRepository
from .presentation import Colors, Presenter


class CommandHandler:
    """Base command handler."""

    def __init__(self, project_root: Path, json_mode: bool = False, no_emoji: bool = False):
        self.project_root = project_root
        self.presenter = Presenter(json_mode=json_mode, no_emoji=no_emoji)

        # Initialize repositories
        self.server_repo = FileSystemServerInstanceRepository(project_root)
        self.config_repo = FileSystemServerConfigRepository(project_root / "configs")
        self.process_repo = SystemProcessRepository()
        self.log_search_repo = FileSystemLogSearchRepository(project_root)

        # Initialize use cases
        self.start_use_case = StartServerUseCase(self.server_repo, self.config_repo, self.process_repo, project_root)
        self.stop_use_case = StopServerUseCase(self.server_repo, self.process_repo)
        self.list_use_case = ListServersUseCase(self.server_repo, self.process_repo)
        self.config_use_case = GetConfigurationsUseCase(self.config_repo)
        self.search_use_case = SearchLogsUseCase(self.log_search_repo, self.server_repo, self.config_repo)


class StartCommand(CommandHandler):
    """Handler for start command."""

    def execute(self, args: argparse.Namespace) -> None:
        """Execute start command."""
        try:
            # Get configuration name
            config_name = args.config
            if not config_name:
                config_name = self._interactive_config_selection()

            # Start server
            instance = self.start_use_case.execute(config_name=config_name, port=args.port, host=args.host, reload=args.reload)

            self.presenter.show_server_started(instance)

        except ValueError as e:
            self.presenter.show_error(str(e))
            sys.exit(1)
        except Exception as e:
            self.presenter.show_error(f"Unexpected error: {e}")
            sys.exit(1)

    def _interactive_config_selection(self) -> str:
        """Interactive configuration selection."""
        configs = self.config_use_case.execute()

        if not configs:
            self.presenter.show_error("No configurations found")
            sys.exit(1)

        if len(configs) == 1:
            return configs[0].name

        self.presenter.show_config_selection(configs)

        try:
            choice = int(input(f"{Colors.CYAN}Select configuration (1-{len(configs)}): {Colors.NC}"))
            if 1 <= choice <= len(configs):
                return configs[choice - 1].name
            else:
                self.presenter.show_error("Invalid selection")
                sys.exit(1)
        except (ValueError, KeyboardInterrupt):
            self.presenter.show_error("Invalid selection")
            sys.exit(1)


class StopCommand(CommandHandler):
    """Handler for stop command."""

    def execute(self, args: argparse.Namespace) -> None:
        """Execute stop command."""
        try:
            if args.all:
                results = self.stop_use_case.execute_all()
                self.presenter.show_stop_all_results(results)
            elif args.pid:
                success = self.stop_use_case.execute_by_pid(args.pid)
                self.presenter.show_stop_result(success, f"PID {args.pid}")
            elif args.port:
                success = self.stop_use_case.execute_by_port(args.port)
                self.presenter.show_stop_result(success, f"port {args.port}")
            elif args.config:
                success = self.stop_use_case.execute_by_config(args.config)
                self.presenter.show_stop_result(success, f"config {args.config}")
            else:
                # Auto-detect server to stop
                servers = self.list_use_case.execute()
                if not servers:
                    self.presenter.show_warning("No tracked servers found")
                    return

                if len(servers) == 1:
                    success = self.stop_use_case.execute_by_pid(servers[0].pid)
                    self.presenter.show_stop_result(success, f"config {servers[0].config_name}")
                else:
                    self._interactive_stop_selection(servers)

        except ValueError as e:
            self.presenter.show_error(str(e))
            sys.exit(1)
        except Exception as e:
            self.presenter.show_error(f"Unexpected error: {e}")
            sys.exit(1)

    def _interactive_stop_selection(self, servers: list[ServerInstance]) -> None:
        """Interactive server stop selection."""
        self.presenter.show_server_selection(servers, "stop")

        try:
            choice = int(input(f"{Colors.CYAN}Select server to stop (1-{len(servers)}): {Colors.NC}"))
            if 1 <= choice <= len(servers):
                server = servers[choice - 1]
                success = self.stop_use_case.execute_by_pid(server.pid)
                self.presenter.show_stop_result(success, f"config {server.config_name}")
            else:
                self.presenter.show_error("Invalid selection")
        except (ValueError, KeyboardInterrupt):
            self.presenter.show_error("Invalid selection")


class ListCommand(CommandHandler):
    """Handler for list command."""

    def execute(self, args: argparse.Namespace) -> None:
        """Execute list command."""
        try:
            servers = self.list_use_case.execute()

            if not servers:
                self.presenter.show_no_servers()

                # Look for untracked processes
                untracked = self.process_repo.list_mock_server_processes()
                if untracked:
                    self.presenter.show_untracked_processes(untracked)
            else:
                self.presenter.show_servers_list(servers)

        except Exception as e:
            self.presenter.show_error(f"Unexpected error: {e}")
            sys.exit(1)


class ConfigHelpCommand(CommandHandler):
    """Handler for config help command."""

    def execute(self, args: argparse.Namespace) -> None:
        """Execute config help command."""
        try:
            configs = self.config_use_case.execute()
            self.presenter.show_config_help(configs)
        except Exception as e:
            self.presenter.show_error(f"Unexpected error: {e}")
            sys.exit(1)


class SearchCommand(CommandHandler):
    """Handler for search command."""

    def execute(self, args: argparse.Namespace) -> None:
        """Execute search command."""
        try:
            # Parse since parameter if provided
            since_timestamp = None
            if args.since:
                since_timestamp = self._parse_since_parameter(args.since)

            # Execute search with new parameter structure
            result = self.search_use_case.execute(path_regex=args.path_regex, config_name=args.config, port=args.port, since_timestamp=since_timestamp, use_all_logs=args.all_logs)

            self.presenter.show_search_results(result)

        except ValueError as e:
            self.presenter.show_error(str(e))
            sys.exit(1)
        except Exception as e:
            self.presenter.show_error(f"Unexpected error: {e}")
            sys.exit(1)

    def _parse_since_parameter(self, since_str: str) -> datetime:
        """Parse the --since parameter into a datetime."""
        now = datetime.now()
        since_str = since_str.lower().strip()

        # Handle relative time formats
        if since_str.endswith("ago"):
            time_part = since_str[:-3].strip()

            # Parse formats like "30m", "2h", "1d"
            if time_part.endswith("m"):
                minutes = int(time_part[:-1])
                return now - timedelta(minutes=minutes)
            elif time_part.endswith("h"):
                hours = int(time_part[:-1])
                return now - timedelta(hours=hours)
            elif time_part.endswith("d"):
                days = int(time_part[:-1])
                return now - timedelta(days=days)

        # Handle special cases
        elif since_str == "today":
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif since_str == "yesterday":
            yesterday = now - timedelta(days=1)
            return yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

        # Try to parse as ISO format or common formats
        formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%H:%M:%S", "%H:%M"]

        for fmt in formats:
            try:
                if fmt.startswith("%H"):
                    # For time-only formats, use today's date
                    parsed_time = datetime.strptime(since_str, fmt).time()
                    return now.replace(hour=parsed_time.hour, minute=parsed_time.minute, second=parsed_time.second, microsecond=0)
                else:
                    return datetime.strptime(since_str, fmt)
            except ValueError:
                continue

        raise ValueError(f"Could not parse time format: {since_str}")


class VersionCommand(CommandHandler):
    """Handler for version command."""

    def execute(self, args: argparse.Namespace) -> None:
        """Execute version command."""
        import tomllib

        try:
            # Read version from pyproject.toml
            pyproject_path = self.project_root / "pyproject.toml"

            if not pyproject_path.exists():
                self.presenter.show_error("pyproject.toml not found")
                return

            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            version = data.get("tool", {}).get("poetry", {}).get("version")

            if not version:
                self.presenter.show_error("Version not found in pyproject.toml")
                return

            # Display version
            if self.presenter.json_mode:
                # For JSON mode, output structured data
                version_data = {"name": data.get("tool", {}).get("poetry", {}).get("name", "MockAndRoll"), "version": version, "description": data.get("tool", {}).get("poetry", {}).get("description", "")}
                self.presenter._output_json(version_data)
            else:
                # For text mode, show simple version string
                name = data.get("tool", {}).get("poetry", {}).get("name", "MockAndRoll")
                self.presenter.show_info(f"{name} version {version}")

        except Exception as e:
            self.presenter.show_error(f"Failed to read version: {str(e)}")


class TestCommand(CommandHandler):
    """Handler for test command."""

    def execute(self, args: argparse.Namespace) -> None:
        """Execute test command."""
        from urllib.parse import urljoin

        import requests

        try:
            # Get all running servers
            servers = self.list_use_case.execute()

            if not servers:
                self.presenter.show_error("No running servers found")
                return

            # Filter servers by config if specified
            if args.config:
                servers = [s for s in servers if s.config_name == args.config]
                if not servers:
                    self.presenter.show_error(f"No running server found for config '{args.config}'")
                    return

            test_results = []

            for server in servers:
                base_url = f"http://{server.host}:{server.port}"
                server_result = {"config": server.config_name, "base_url": base_url, "tests": []}

                # Test endpoints: /, /docs, /openapi.json
                endpoints = [{"path": "/", "description": "Root endpoint"}, {"path": "/docs", "description": "API documentation"}, {"path": "/openapi.json", "description": "OpenAPI schema"}]

                for endpoint in endpoints:
                    url = urljoin(base_url + "/", endpoint["path"])
                    test_result: dict[str, Any] = {"endpoint": endpoint["path"], "url": url, "description": endpoint["description"]}

                    try:
                        response = requests.get(url, timeout=5)
                        test_result["status"] = "success"
                        test_result["status_code"] = response.status_code
                        test_result["response_time_ms"] = int(response.elapsed.total_seconds() * 1000)
                        test_result["content_type"] = response.headers.get("content-type", "unknown")

                        if response.status_code >= 400:
                            test_result["status"] = "warning"
                            test_result["message"] = f"HTTP {response.status_code}"

                    except requests.exceptions.Timeout:
                        test_result["status"] = "error"
                        test_result["message"] = "Request timeout (5s)"
                    except requests.exceptions.ConnectionError:
                        test_result["status"] = "error"
                        test_result["message"] = "Connection failed"
                    except Exception as e:
                        test_result["status"] = "error"
                        test_result["message"] = f"Request failed: {str(e)}"

                    server_result["tests"].append(test_result)

                test_results.append(server_result)

            # Display results
            self.presenter.show_test_results(test_results)

            # Exit with error code if any tests failed
            failed_tests = sum(1 for result in test_results for test in result["tests"] if test.get("status") == "error")

            if failed_tests > 0:
                sys.exit(1)

        except Exception as e:
            self.presenter.show_error(f"Test command failed: {str(e)}")
            sys.exit(1)


class CleanUpCommand(CommandHandler):
    """Handler for clean-up command.

    Removes all timestamped server log files, truncates the main mockctl log,
    and stops any currently running server instances.
    """

    def execute(self, args: argparse.Namespace) -> None:  # noqa: D401
        """Execute clean-up command performing orderly shutdown and log removal.

        Steps:
            1. Stop all running server instances (if any)
            2. Delete all server log files matching pattern logs/*.logs (except mockctl.log)
            3. Truncate (or recreate) logs/mockctl.log
            4. Provide JSON or human readable summary
        """
        import glob
        import os
        from datetime import datetime

        try:
            # 1. Stop all running servers
            servers = self.list_use_case.execute()
            stopped = []
            for server in servers:
                try:
                    result = self.stop_use_case.execute_by_pid(server.pid)
                    stopped.append({"config": server.config_name, "pid": server.pid, "stopped": result})
                except Exception as e:  # pragma: no cover - defensive
                    stopped.append({"config": server.config_name, "pid": server.pid, "stopped": False, "error": str(e)})

            # 2. Delete server log files (timestamped) except mockctl.log
            logs_dir = self.project_root / "logs"
            deleted_logs: list[str] = []
            if logs_dir.exists():
                pattern = str(logs_dir / "*.logs")
                for path in glob.glob(pattern):
                    # Ensure not deleting mockctl log (different extension) but safeguard anyway
                    if os.path.basename(path) == "mockctl.log":
                        continue
                    try:
                        os.remove(path)
                        deleted_logs.append(os.path.basename(path))
                    except OSError as e:  # pragma: no cover - edge case
                        deleted_logs.append(f"FAILED:{os.path.basename(path)}:{e}")

            # 3. Truncate or recreate mockctl.log
            mockctl_log_path = logs_dir / "mockctl.log"
            mockctl_log_truncated = False
            try:
                if mockctl_log_path.exists():
                    with open(mockctl_log_path, "w", encoding="utf-8"):
                        pass  # truncates
                    mockctl_log_truncated = True
                else:
                    logs_dir.mkdir(exist_ok=True)
                    mockctl_log_path.touch()
                    mockctl_log_truncated = True
            except OSError as e:  # pragma: no cover - edge case
                self.presenter.show_warning(f"Could not truncate mockctl.log: {e}")

            summary = {
                "action": "clean-up",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "stopped_instances": stopped,
                "deleted_log_files": deleted_logs,
                "mockctl_log_truncated": mockctl_log_truncated,
            }

            if self.presenter.json_mode:
                self.presenter._output_json({"status": "success", **summary})
            else:
                self.presenter.show_success("Clean-up completed")
                if stopped:
                    running_stopped = [s for s in stopped if s.get("stopped")]
                    if running_stopped:
                        self.presenter.show_info(f"Stopped {len(running_stopped)} server instance(s)")
                if deleted_logs:
                    self.presenter.show_info(f"Removed {len(deleted_logs)} log file(s)")
                if mockctl_log_truncated:
                    self.presenter.show_info("mockctl.log truncated")

        except Exception as e:  # pragma: no cover - catch-all
            self.presenter.show_error(f"Clean-up failed: {e}")
            sys.exit(1)
