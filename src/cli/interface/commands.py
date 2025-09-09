"""Command line interface handlers."""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

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

    def __init__(self, project_root: Path, json_mode: bool = False):
        self.project_root = project_root
        self.presenter = Presenter(json_mode=json_mode)

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

            # Execute search
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
