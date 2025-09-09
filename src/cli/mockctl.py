#!"""Clean Architecture Mock Server CLI."""

import argparse
import sys
from pathlib import Path

# Add the project root to Python path for absolute imports
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Import after path setup
from src.cli.interface.commands import (  # noqa: E402
    ConfigHelpCommand,
    ListCommand,
    SearchCommand,
    StartCommand,
    StopCommand,
)
from src.cli.interface.presentation import Colors  # noqa: E402


class MockServerCLI:
    """Main CLI application using clean architecture."""

    def __init__(self):
        """Initialize CLI."""
        self.project_root = Path(__file__).resolve().parent.parent.parent

    def main(self):
        """Main entry point."""
        parser = self.create_parser()
        args = parser.parse_args()

        # Create command handlers with JSON mode based on args
        json_mode = getattr(args, "json", False)
        start_command = StartCommand(self.project_root, json_mode)
        stop_command = StopCommand(self.project_root, json_mode)
        list_command = ListCommand(self.project_root, json_mode)
        config_help_command = ConfigHelpCommand(self.project_root, json_mode)
        search_command = SearchCommand(self.project_root, json_mode)

        # Map commands to handlers
        command_map = {
            "start": start_command.execute,
            "stop": stop_command.execute,
            "list": list_command.execute,
            "status": list_command.execute,  # alias for list
            "config-help": config_help_command.execute,
            "search": search_command.execute,
        }

        if args.command in command_map:
            try:
                command_map[args.command](args)
            except KeyboardInterrupt:
                if not json_mode:
                    print(f"\n{Colors.YELLOW}⚠️  Operation cancelled{Colors.NC}")
                else:
                    print('{"status": "cancelled", "message": "Operation cancelled"}')
                sys.exit(1)
            except Exception as e:
                if not json_mode:
                    print(f"{Colors.RED}❌ Error: {e}{Colors.NC}")
                else:
                    print(f'{{"status": "error", "message": "{str(e)}"}}')
                sys.exit(1)
        else:
            parser.print_help()

    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description="🚀 Mock API Server Management (Clean Architecture)",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s start                     # Interactive config selection
  %(prog)s start basic               # Start basic configuration
  %(prog)s start vmanage --port 8080 # Start vManage config on port 8080
  %(prog)s stop                      # Stop servers (auto-detect)
  %(prog)s list                      # Show running servers
  %(prog)s list --json               # Show running servers in JSON format
  %(prog)s config-help --json        # Show configuration guide in JSON format
  %(prog)s search "/api/.*"          # Search requests matching path pattern
  %(prog)s search "/users" --since "30m ago" # Search recent user requests
  %(prog)s search ".*" --config basic --json # Search all requests in JSON format

📂 Available configurations: basic, persistence, vmanage
💡 Use --json with any command for machine-readable output (no emojis)
            """,
        )

        # Add global --json option
        parser.add_argument("--json", action="store_true", help="Output in JSON format (no emojis)")

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Start command
        start_parser = subparsers.add_parser("start", help="Start mock server")
        start_parser.add_argument("config", nargs="?", help="Configuration name (interactive if omitted)")
        start_parser.add_argument("--port", type=int, help="Server port")
        start_parser.add_argument("--host", default="0.0.0.0", help="Server host")
        start_parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
        start_parser.add_argument("--json", action="store_true", help="Output in JSON format (no emojis)")

        # Stop command
        stop_parser = subparsers.add_parser("stop", help="Stop mock server")
        stop_parser.add_argument("config", nargs="?", help="Configuration name (auto-detect if omitted)")
        stop_parser.add_argument("--port", type=int, help="Stop server on specific port")
        stop_parser.add_argument("--pid", type=int, help="Stop specific process ID")
        stop_parser.add_argument("--all", action="store_true", help="Stop all servers")
        stop_parser.add_argument("--json", action="store_true", help="Output in JSON format (no emojis)")

        # List command
        list_parser = subparsers.add_parser("list", help="List running servers")
        list_parser.add_argument("--json", action="store_true", help="Output in JSON format (no emojis)")

        # Status command (alias for list)
        status_parser = subparsers.add_parser("status", help="Show server status (alias for list)")
        status_parser.add_argument("--json", action="store_true", help="Output in JSON format (no emojis)")

        # Config-help command
        config_help_parser = subparsers.add_parser("config-help", help="Show configuration guide")
        config_help_parser.add_argument("--json", action="store_true", help="Output in JSON format (no emojis)")

        # Search command
        search_parser = subparsers.add_parser("search", help="Search logged requests/responses")
        search_parser.add_argument("path_regex", help="Regular expression to match request paths")
        search_parser.add_argument("--config", help="Configuration name (auto-detect if omitted)")
        search_parser.add_argument("--port", type=int, help="Port number to search logs for")
        search_parser.add_argument("--since", help="Filter logs since time (e.g., '30m ago', 'today', '2024-01-01 10:00')")
        search_parser.add_argument("--all-logs", action="store_true", help="Search all available log files")
        search_parser.add_argument("--json", action="store_true", help="Output in JSON format (no emojis)")

        return parser


def main():
    """Main entry point for the CLI."""
    cli = MockServerCLI()
    cli.main()


if __name__ == "__main__":
    main()
