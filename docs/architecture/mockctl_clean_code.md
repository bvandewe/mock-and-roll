# MockCTL Clean Architecture

This directory contains a refactored version of the `mockctl` CLI tool using Clean Architecture principles. The new design makes it much easier to maintain, test, and extend with new features.

## Architecture Overview

```
src/cli/
├── domain/           # Core business logic (entities, rules)
├── application/      # Use cases and application services  
├── infrastructure/   # External dependencies (filesystem, processes)
├── interface/        # User interface (CLI commands, presentation)
└── examples/         # Extension examples and documentation
```

## Key Benefits

### 1. **Separation of Concerns**
- **Domain**: Business entities like `ServerInstance`, `ServerConfig`
- **Application**: Use cases like `StartServerUseCase`, `StopServerUseCase`
- **Infrastructure**: File system, process management implementations
- **Interface**: CLI commands and presentation logic

### 2. **Easy to Extend**
Adding new commands is straightforward:

```python
# 1. Create a new use case
class GetServerLogsUseCase:
    def execute(self, server_id: str) -> List[LogEntry]:
        # Business logic here
        pass

# 2. Create a command handler
class LogsCommand(CommandHandler):
    def execute(self, args):
        logs = self.logs_use_case.execute(args.server_id)
        self.presenter.show_logs(logs)

# 3. Add to CLI parser
logs_parser = subparsers.add_parser("logs", help="View server logs")
logs_parser.set_defaults(func=LogsCommand(project_root).execute)
```

### 3. **Testable**
Each layer can be tested independently:

```python
def test_start_server_use_case():
    # Mock dependencies
    mock_server_repo = Mock()
    mock_config_repo = Mock() 
    mock_process_repo = Mock()
    
    # Test use case in isolation
    use_case = StartServerUseCase(mock_server_repo, mock_config_repo, mock_process_repo)
    result = use_case.execute("basic", port=8080)
    
    assert result.config_name == "basic"
    assert result.port == 8080
```

### 4. **Consistent Error Handling**
Errors are handled consistently across all commands:

```python
try:
    result = use_case.execute(args)
    presenter.show_success(result)
except ValueError as e:
    presenter.show_error(str(e))
    sys.exit(1)
```

## Domain Layer

### Entities
- `ServerInstance`: Represents a running mock server
- `ServerConfig`: Represents a configuration set
- `LogEntry`: Represents a log entry
- `TestResult`: Represents an endpoint test result

### Value Objects
- `Port`: Network port with validation
- `ProcessId`: Process ID with validation  
- `ApiKey`: API key with masking capabilities

### Repositories (Interfaces)
- `ServerInstanceRepository`: Server instance persistence
- `ServerConfigRepository`: Configuration management
- `ProcessRepository`: Process management

## Application Layer

### Use Cases
- `StartServerUseCase`: Start a server with configuration
- `StopServerUseCase`: Stop a server by various criteria
- `ListServersUseCase`: List and update server status
- `GetConfigurationsUseCase`: Manage configurations

Each use case:
- Takes dependencies via constructor injection
- Has a single `execute()` method
- Contains pure business logic
- Returns domain entities

## Infrastructure Layer

### Implementations
- `FileSystemServerInstanceRepository`: JSON file-based persistence
- `FileSystemServerConfigRepository`: Configuration file management
- `SystemProcessRepository`: OS-level process management

### Key Features
- Graceful fallbacks when `psutil` is not available
- Cross-platform process management
- Robust error handling

## Interface Layer

### Command Handlers
- `StartCommand`: Handles start command logic
- `StopCommand`: Handles stop command logic  
- `ListCommand`: Handles list command logic
- `ConfigHelpCommand`: Handles configuration help

### Presentation
- `Presenter`: Formats output for users
- `Colors`: Terminal color constants
- Consistent styling across all commands

## Usage Examples

### Starting a Server
```bash
# Interactive configuration selection
./mockctl_clean.py start

# Specific configuration
./mockctl_clean.py start vmanage --port 8080 --reload

# Auto-select available port
./mockctl_clean.py start basic
```

### Stopping Servers
```bash
# Auto-detect and stop
./mockctl_clean.py stop

# Stop by configuration
./mockctl_clean.py stop vmanage

# Stop by port
./mockctl_clean.py stop --port 8080

# Stop all servers
./mockctl_clean.py stop --all
```

### Listing Servers
```bash
# Show all tracked servers
./mockctl_clean.py list

# Show server status (alias)
./mockctl_clean.py status
```

## Extending the CLI

See `examples/extension_example.py` for detailed examples of:

1. **Adding new use cases**
2. **Creating new command handlers**
3. **Extending the presenter**
4. **Adding new domain entities**
5. **Writing tests**

## Migration from Original

The original `mockctl.py` can coexist with this new version:

- **Original**: `./mockctl` (full featured, monolithic)
- **New**: `./mockctl_clean.py` (clean architecture, extensible)

To fully migrate:

1. **Phase 1**: Add remaining features (logs, search, test, etc.)
2. **Phase 2**: Add comprehensive tests
3. **Phase 3**: Replace original script
4. **Phase 4**: Add advanced features (configuration validation, metrics, etc.)

## Development Guidelines

### Adding New Features

1. **Start with Domain**: Define entities and business rules
2. **Create Use Cases**: Implement business logic
3. **Add Infrastructure**: Implement external dependencies
4. **Create Interface**: Add command handlers and presentation
5. **Write Tests**: Test each layer independently

### Best Practices

- **Single Responsibility**: Each class has one reason to change
- **Dependency Inversion**: Depend on abstractions, not implementations
- **Open/Closed**: Open for extension, closed for modification
- **Interface Segregation**: Many small interfaces vs. few large ones
- **DRY**: Don't repeat yourself, especially business logic

### Testing Strategy

- **Unit Tests**: Test use cases with mocked repositories
- **Integration Tests**: Test command handlers with real infrastructure
- **End-to-End Tests**: Test complete CLI workflows
- **Property Tests**: Test domain entity validation

## Performance Considerations

The clean architecture introduces some overhead:

- **Memory**: More objects and abstractions
- **CPU**: Additional method calls and abstractions
- **Startup**: More classes to instantiate

For a CLI tool, these overheads are negligible compared to:

- **Process management** (subprocess calls)
- **File I/O** (reading configurations)
- **Network** (HTTP requests for testing)

The benefits in maintainability far outweigh the minimal performance cost.

## Future Enhancements

With this architecture, these features become much easier to add:

1. **Plugin System**: Load commands from external modules
2. **Configuration Validation**: Rich validation with detailed error messages
3. **Metrics Collection**: Track server usage and performance
4. **Remote Management**: Manage servers on remote machines
5. **Web UI**: RESTful API for web-based management
6. **Database Backend**: Store state in PostgreSQL/SQLite instead of JSON
7. **Container Support**: Docker and Kubernetes integration
8. **Monitoring**: Health checks and alerting
9. **Load Testing**: Built-in performance testing
10. **Configuration Templates**: Generate configurations from templates
