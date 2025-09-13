# Changelog

All notable changes to Mock-and-Roll will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2025-09-12

### Added

- **Air-gapped Swagger UI Support**: Complete offline documentation interface for secure environments
  - Local Swagger UI assets (CSS/JS) bundled with application - no CDN dependencies
  - **Local Favicon Support**: FastAPI favicon served locally without internet dependency
  - Automatic air-gapped mode detection via configuration (`airgapped_mode: true`)
  - Direct static file routes serving local assets at `/static/swagger-ui/` endpoints
  - Custom Swagger UI title indicating air-gapped mode for environment awareness
  - New `airgapped` configuration profile for immediate deployment in isolated networks
  - Fully functional Swagger UI interface with authentication testing in offline environments

- **New Test Command**: `mockctl test [config]` command to validate server endpoints
  - Tests root `/`, `/docs`, and `/openapi.json` endpoints for all running servers or a specific config
  - Displays response status, response time, and content type information
  - Supports JSON output mode for automation and integration
  - Returns appropriate exit codes for CI/CD pipelines (0 for success, 1 for failures)
- **Emoji-free Output Option**: New `--no-emoji` global flag for clean text output
  - Removes all Unicode emojis from CLI output for cleaner logs and scripts
  - Applies to all text output modes (ignored when using `--json`)
  - Comprehensive Unicode emoji pattern matching for complete removal
- Comprehensive MkDocs documentation with Material theme
- GitHub Pages deployment workflow
- Professional documentation structure with navigation

### Enhanced

- **Enhanced Search Command with Mandatory Config Parameter**: Redesigned search interface for better organization and control
  - **New Command Signature**: Changed from `mockctl search [--config name] pattern` to `mockctl search <config_name> <pattern>`
  - **Mandatory Config Parameter**: Config name is now required - use specific config ('basic', 'vmanage', 'persistence') or 'all'
  - **"All" Config Mode**: `mockctl search all "/pattern"` searches most recent log file for each configuration type
  - **Enhanced File Selection Logic**:
    - Without `--all-logs`: Searches most recent log file for selected config(s)
    - With `--all-logs`: Searches ALL historical log files for selected config(s)
  - **Improved Output with File Tracking**:
    - Text output shows "Log file processed" (single) or "Log files processed (N)" (multiple)
    - JSON output includes `"log_files"` array with all processed file paths
    - Each request includes `"log_file_source"` field indicating source file
    - "Source" field displayed for each request when multiple files are searched
  - **Better Error Messages**: Clear error messages when no logs found for specified config
  - **Backward Compatibility**: `--all-logs` flag continues to work with enhanced config-specific scope

### Changed

- **Simplified Port Detection**: Replaced complex OS-dependent port detection with simple socket-based approach
  - Uses Python's built-in `socket` module for cross-platform compatibility
  - Eliminates dependencies on `lsof`, `netstat`, `ss`, and other system utilities
  - Works reliably in minimal container environments like Alpine Linux
  - Automatic port assignment starting from 8000 with fallback scanning
  - Improved reliability and reduced system requirements
- **Documentation Updates**: Complete documentation overhaul to reflect CLI flag changes
  - Updated all command examples to use global flag syntax (`mockctl --json [command]`)
  - Corrected CLI reference documentation to remove deprecated command-specific flags
  - Updated README.md, user guides, and example documentation for consistency
  - Fixed incorrect syntax patterns in automation examples and CI/CD scripts

### Fixed

- **Air-gapped Static Routes**: Fixed missing `/static/swagger-ui/swagger-ui-standalone-preset.js` endpoint
  - Added missing static file route for swagger-ui-standalone-preset.js in air-gapped mode
  - Resolves 404 errors when accessing Swagger UI in air-gapped environments
  - Ensures complete air-gapped functionality without external dependencies
- **Complete Logging System Overhaul**: Eliminated generic log files and ensured proper log file management
  - **Removed latest.logs Usage**: Completely eliminated `latest.logs` references throughout the codebase
  - **Mandatory LOG_FILE Environment Variable**: Server now requires LOG_FILE environment variable to start
  - **Prevents Direct Server Startup**: Server refuses to start without proper log file configuration
  - **Config-Specific Log Files**: All server logs use timestamped format `{timestamp}_{config}_{port}.logs`
  - **Dedicated mockctl Logging**: CLI operations logged separately to `logs/mockctl.log`
  - **Clean Log Directory**: Only proper config-specific server logs and mockctl.log are generated
  - **Generic Server Log Prevention**: Eliminated fallback generic server log creation mechanism

- GitHub Pages deployment permissions and workflow configuration
- Port detection failures in minimal container environments
- Auto port assignment when no port is explicitly specified
- Documentation inconsistencies between CLI implementation and documented examples

## [0.2.0] - 2024-09-10

### Added

- **Advanced Log Search Functionality**: New search command with regex, time filtering, and status grouping
- **Clean Architecture Implementation**: Domain-driven design with clear separation of concerns
  - Domain Layer: Server entities and business logic
  - Application Layer: Server management use cases
  - Infrastructure Layer: Log search and file operations
  - Interface Layer: Command handling and presentation
- **Enhanced CLI Experience**: Comprehensive command-line interface for server management
- **JSON Output Mode**: Machine-readable responses for automation
- **Request/Response Correlation**: Advanced tracking via correlation IDs
- **Time-based Log Filtering**: Support for relative time expressions (`--since "30m ago"`, `--since "today"`)
- **Status Code Grouping**: Summarization and analysis of response patterns
- **Header Extraction**: Display and analysis of HTTP headers

### Changed

- **Version Update**: Incremented from 0.1.0 to 0.2.0 for major feature additions
- **Architecture Cleanup**: Consolidated CLI architecture by removing duplicate components

### Removed

- `mockctl_clean` (bash script) - Duplicate entry point, outdated
- `src/cli/mockctl_clean.py` - Duplicate Python CLI, missing search functionality
- `.mypy_cache/` - Cleaned up cache for removed files

### Security

- **CLI Consistency**: Unified command interface across all operations
- **Documentation**: Improved inline help and command descriptions

## [0.1.0] - 2024-08-XX

### Added

- **Initial Release**: Core mock API server functionality
- **FastAPI Foundation**: High-performance REST API framework
- **Configuration-Driven Development**: JSON-based endpoint definitions
- **Multiple Authentication Methods**: API keys, Basic Auth, OIDC/OAuth2, sessions, CSRF tokens
- **Request Schema Validation**: JSON Schema validation for request bodies
- **Conditional Responses**: Different responses based on request conditions
- **Template Variables**: Dynamic values like `{{random_uuid}}`, `{{timestamp}}`
- **Path Parameters**: Dynamic URL parameters with automatic substitution
- **Redis Persistence**: Optional data persistence with CRUD operations
- **Interactive Swagger UI**: Auto-generated API documentation
- **Docker Support**: Ready-to-use containerization
- **Configuration Profiles**: Pre-built configurations
  - **basic**: Simple REST API with API key auth
  - **persistence**: Full-featured API with Redis persistence
  - **vmanage**: Cisco SD-WAN API simulation with 25+ endpoints
- **Management CLI**: Basic server start/stop functionality
- **Comprehensive Logging**: Request/response tracking with configurable verbosity
- **Hot Reloading**: Development mode with automatic code updates

### Core Features

- Dynamic endpoint configuration through JSON files
- Multiple server instance management
- Process tracking and monitoring
- Configuration validation and error handling
- Extensible plugin architecture

---

## Version History Summary

| Version | Release Date | Key Features |
|---------|--------------|--------------|
| 0.2.0   | 2024-09-10   | Advanced search, clean architecture, enhanced CLI |
| 0.1.0   | 2024-08-XX   | Initial release with core mock API functionality |

---

## Migration Guide

### From 0.1.0 to 0.2.0

No breaking changes were introduced in this version. All existing configurations and usage patterns remain fully compatible.

**New Features Available:**

- Use `./mockctl search <config> <pattern>` for advanced log analysis
- JSON output mode: Add `--json` flag to most commands
- Enhanced time filtering: Use `--since` with human-readable expressions

**Deprecated:**

- No features were deprecated in this release

---

## Contributing

When contributing to this project, please:

1. Follow [Semantic Versioning](https://semver.org/) for version numbers
2. Update this changelog with your changes
3. Follow the [Keep a Changelog](https://keepachangelog.com/) format
4. Include migration notes for breaking changes

For detailed contribution guidelines, see [CONTRIBUTING.md](https://github.com/bvandewe/mock-and-roll/blob/main/docs/development/contributing.md).
