"""
Example of how to extend the mockctl CLI with new features.

This demonstrates the clean architecture benefits:
1. Adding new use cases is straightforward
2. Business logic is separated from presentation
3. Infrastructure details are abstracted away
4. Testing is simplified with clear interfaces
"""

from pathlib import Path

from ..domain.entities import LogEntry, TestResult
from ..domain.repositories import ServerInstanceRepository
from ..interface.commands import CommandHandler
from ..interface.presentation import Colors, Presenter


class LogsUseCase:
    """Use case for retrieving server logs."""

    def __init__(self, server_repo: ServerInstanceRepository):
        self.server_repo = server_repo

    def execute(self, port: int = None, lines: int = 100) -> list[LogEntry]:
        """Get logs from server(s)."""
        # Implementation would fetch logs from server or file
        # This is a simplified example
        return []


class TestEndpointsUseCase:
    """Use case for testing server endpoints."""

    def __init__(self, server_repo: ServerInstanceRepository):
        self.server_repo = server_repo

    def execute(self, config_name: str = None) -> list[TestResult]:
        """Test server endpoints."""
        # Implementation would make HTTP requests to test endpoints
        # This is a simplified example
        return []


class LogsCommand(CommandHandler):
    """Handler for logs command - demonstrates easy extensibility."""

    def __init__(self, project_root: Path):
        super().__init__(project_root)
        self.logs_use_case = LogsUseCase(self.server_repo)

    def execute(self, args) -> None:
        """Execute logs command."""
        try:
            logs = self.logs_use_case.execute(port=getattr(args, "port", None), lines=getattr(args, "lines", 100))
            self.presenter.show_logs(logs)
        except Exception as e:
            self.presenter.show_error(f"Failed to get logs: {e}")


class TestCommand(CommandHandler):
    """Handler for test command - demonstrates easy extensibility."""

    def __init__(self, project_root: Path):
        super().__init__(project_root)
        self.test_use_case = TestEndpointsUseCase(self.server_repo)

    def execute(self, args) -> None:
        """Execute test command."""
        try:
            results = self.test_use_case.execute(config_name=getattr(args, "config", None))
            self.presenter.show_test_results(results)
        except Exception as e:
            self.presenter.show_error(f"Failed to run tests: {e}")


class ExtendedPresenter(Presenter):
    """Extended presenter with new display methods."""

    def show_logs(self, logs: list[LogEntry]) -> None:
        """Show log entries."""
        if not logs:
            print(f"{Colors.YELLOW}📭 No logs found{Colors.NC}")
            return

        print(f"{Colors.BLUE}📋 Showing {len(logs)} log entries:{Colors.NC}")
        print()

        for log in logs:
            color = Colors.RED if log.is_error else Colors.GREEN if log.is_success else Colors.NC
            print(f"{color}{log.timestamp} [{log.level}] {log.message}{Colors.NC}")

    def show_test_results(self, results: list[TestResult]) -> None:
        """Show test results."""
        if not results:
            print(f"{Colors.YELLOW}📭 No test results{Colors.NC}")
            return

        successful = sum(1 for r in results if r.is_success)
        total = len(results)

        print(f"{Colors.BLUE}🧪 Test Results: {successful}/{total} passed{Colors.NC}")
        print()

        for result in results:
            status = f"{Colors.GREEN}✅" if result.is_success else f"{Colors.RED}❌"
            print(f"{status} {result.method} {result.endpoint} - {result.status_code} ({result.response_time:.2f}ms){Colors.NC}")
            if result.error_message:
                print(f"   {Colors.RED}Error: {result.error_message}{Colors.NC}")


def add_commands_to_parser(parser, project_root: Path):
    """
    Example of how to extend the CLI with new commands.

    This shows how the clean architecture makes it easy to:
    1. Add new commands without modifying existing code
    2. Reuse existing infrastructure and domain logic
    3. Maintain consistency in presentation
    """
    subparsers = parser._subparsers._group_actions[0].choices

    # Add logs command
    logs_parser = subparsers.add_parser("logs", help="View server logs")
    logs_parser.add_argument("--port", type=int, help="Server port")
    logs_parser.add_argument("--lines", type=int, default=100, help="Number of lines")
    logs_command = LogsCommand(project_root)
    logs_parser.set_defaults(func=logs_command.execute)

    # Add test command
    test_parser = subparsers.add_parser("test", help="Test server endpoints")
    test_parser.add_argument("config", nargs="?", help="Configuration to test")
    test_command = TestCommand(project_root)
    test_parser.set_defaults(func=test_command.execute)


# Benefits of this architecture:

# 1. SINGLE RESPONSIBILITY
#    - Each class has one reason to change
#    - CommandHandler: CLI interface
#    - UseCase: Business logic
#    - Repository: Data access
#    - Presenter: Display logic

# 2. DEPENDENCY INVERSION
#    - High-level modules don't depend on low-level modules
#    - Both depend on abstractions (interfaces)
#    - Easy to swap implementations (e.g., Redis instead of file storage)

# 3. OPEN/CLOSED PRINCIPLE
#    - Open for extension (new commands, use cases)
#    - Closed for modification (existing code doesn't change)

# 4. EASY TESTING
#    - Each layer can be tested independently
#    - Mock repositories for unit testing use cases
#    - Mock use cases for testing command handlers

# 5. CLEAR SEPARATION OF CONCERNS
#    - Domain: Business entities and rules
#    - Application: Use cases and workflows
#    - Infrastructure: External dependencies
#    - Interface: User interaction

# Example test for a use case:
"""
def test_start_server_use_case():
    # Arrange
    mock_server_repo = Mock(ServerInstanceRepository)
    mock_config_repo = Mock(ServerConfigRepository)
    mock_process_repo = Mock(ProcessRepository)
    
    use_case = StartServerUseCase(mock_server_repo, mock_config_repo, mock_process_repo, Path("/"))
    
    # Act
    result = use_case.execute("basic", port=8080)
    
    # Assert
    assert result.config_name == "basic"
    assert result.port == 8080
    mock_server_repo.save.assert_called_once()
"""
