# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.2] - 2025-10-27

### Fixed

- **Binary Content Logging**: Fixed logging middleware to skip binary content types
  - Detects and bypasses logging for images, videos, audio, PDFs, fonts, and other binary formats
  - Prevents log pollution and performance issues when serving static assets
  - Added debug logging message when skipping binary content
  - Improves logging efficiency for applications serving mixed content types
- **Dynamic Security Schemes**: Fixed OpenAPI/Swagger UI to dynamically load authentication methods from config

  - Security schemes now loaded from `auth.json` at runtime instead of hardcoded
  - Automatically adapts Swagger UI authentication to match configured auth methods
  - Supports dynamic addition/removal of authentication methods without code changes
  - Includes comprehensive tests for security scheme generation
  - Docker Compose configuration updated with proper debugger port (5699) and environment variables

- **Documentation Accuracy Overhaul**: Comprehensive review and correction of all documentation to ensure 100% alignment with actual codebase implementation
  - **configuration.md**: Removed documentation for unimplemented features including:
    - `required_scopes` OIDC validation (not implemented in auth system)
    - `delay_ms` response delay configuration (not supported)
    - `mockctl validate` command (does not exist)
    - Query parameter and header template variables (not implemented)
    - `when` conditions in authentication (not supported)
  - **features/template-variables.md**: Complete rewrite removing ~60% fictional content
    - Removed 20+ non-existent template variables (`{{request.*}}`, `{{query.*}}`, `{{headers.*}}`, `{{faker.*}}`, etc.)
    - Removed unsupported features: conditional logic, math operations, string manipulation, array generation
    - Documented only actual 6 template variables: `{{random_uuid}}`, `{{current_timestamp}}`, `{{timestamp}}`, `{{date}}`, `{{unix_timestamp}}`, `{{unix_timestamp_ms}}`
    - Added clear limitations section
  - **features/conditional-responses.md**: Complete rewrite removing ~40% fictional content
    - Removed `query_conditions` and `header_conditions` (not implemented)
    - Removed regex patterns, numeric comparisons, nested conditions (not supported)
    - Documented only actual conditional features: `body_conditions` and `path_conditions` with exact matching
    - Added clear limitations section
  - **features.md**: Updated feature descriptions to accurately reflect actual capabilities
  - **architecture/overview.md**: Corrected architectural documentation
    - Added airgapped profile to configuration profiles
    - Removed "JSON schema validation" and "Hot-reloading" (not implemented)
    - Updated template variables to actual implementations
    - Removed "Plugin System" references (doesn't exist)
    - Added note that scope validation is not implemented
    - Replaced speculative "Future Architecture Considerations" with practical "Best Practices" section
  - **index.md**: Fixed MkDocs Material grid cards formatting
    - Corrected markdown syntax for proper rendering
    - Added `.prettierignore` to prevent formatter from breaking grid card indentation

### Changed

- **Documentation Policy**: All documentation now strictly represents implemented features only, with no aspirational or planned features documented as if they exist

### Added

- Comprehensive test suite for binary content logging (`test_binary_content_logging.py`)
- Test suite for dynamic security scheme generation (`test_dynamic_security_schemes.py`)
- OpenAPI verification script for vManage profile (`verify_vmanage_openapi.py`)

## [0.4.1] - 2025-10-06

### Fixed

- **JSON Response Body Parsing**: Fixed `mockctl --json search` to return properly parsed JSON objects for response bodies instead of escaped strings
  - Enhanced logging middleware to detect and log JSON response/request bodies in structured format
  - Updated log parsing in `RequestResponsePair.from_log_entries()` to parse JSON bodies when detected
  - Added request body parsing support with same JSON detection logic
  - Modified presentation layer to handle both string and parsed JSON objects for backward compatibility
  - Response bodies like `{"error":"Auth failed"}` now appear as proper JSON objects `{"error":"Auth failed"}` in search output
  - Enables seamless use with `jq` for JSON manipulation: `mockctl --json search config pattern | jq '.matched_requests[].response_body.error'`

## [0.4.0] - 2025-09-16

### Overview

Feature and tooling release adding environment housekeeping command and test/documentation improvements.

### Added

- **Clean-up Command**: New `mockctl clean-up` (alias `mockctl cleanup`) command for environment housekeeping
  - Gracefully stops all tracked running mock server instances
  - Deletes timestamped server log files (`logs/*.logs`) while preserving `logs/mockctl.log`
  - Truncates `logs/mockctl.log` to keep file for ongoing CLI logging
  - JSON mode provides structured summary including stopped instances and deleted files
  - Useful before packaging, between integration test runs, or reclaiming disk space
- Shared pytest session fixture for automatic `LOG_FILE` provisioning (`tests/conftest.py`)

### Changed

- Converted legacy tests that returned boolean values into pytest assertion style (removes warning noise)
- Clarified mandatory `config_name` positional argument and `all` mode behavior in search command documentation

### Maintenance

- General test suite stabilization (logging environment consistency, assertion hygiene)

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

| Version | Release Date | Key Features                                      |
| ------- | ------------ | ------------------------------------------------- |
| 0.2.0   | 2024-09-10   | Advanced search, clean architecture, enhanced CLI |
| 0.1.0   | 2024-08-XX   | Initial release with core mock API functionality  |

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
