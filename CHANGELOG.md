# Changelog

All notable changes to Mock-and-Roll will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Emoji-free Output Option**: New `--no-emoji` global flag for clean text output
  - Removes all Unicode emojis from CLI output for cleaner logs and scripts
  - Applies to all text output modes (ignored when using `--json`)
  - Comprehensive Unicode emoji pattern matching for complete removal
- Comprehensive MkDocs documentation with Material theme
- GitHub Pages deployment workflow
- Professional documentation structure with navigation

### Changed

- **Simplified Port Detection**: Replaced complex OS-dependent port detection with simple socket-based approach
  - Uses Python's built-in `socket` module for cross-platform compatibility
  - Eliminates dependencies on `lsof`, `netstat`, `ss`, and other system utilities
  - Works reliably in minimal container environments like Alpine Linux
  - Automatic port assignment starting from 8000 with fallback scanning
  - Improved reliability and reduced system requirements

### Fixed

- GitHub Pages deployment permissions and workflow configuration
- Port detection failures in minimal container environments
- Auto port assignment when no port is explicitly specified

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

- Use `./mockctl search` for advanced log analysis
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
