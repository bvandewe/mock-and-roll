# REST API Mock Server

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![Redis](https://img.shields.io/badge/Redis-5.0+-red.svg)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A highly configurable and extensible mock REST API server built with FastAPI. Create realistic API endpoints with authentication, persistence, and dynamic responses through simple JSON configuration files.

---

## 📖 Table of Contents

- [REST API Mock Server](#rest-api-mock-server)
  - [📖 Table of Contents](#-table-of-contents)
  - [🚀 Quick Start](#-quick-start)
  - [✨ Key Features](#-key-features)
    - [🎯 Core Functionality](#-core-functionality)
    - [🏗️ Architecture \& Management](#️-architecture--management)
    - [🔧 Developer Experience](#-developer-experience)
  - [🛠 Management CLI](#-management-cli)
  - [📂 Available Configurations](#-available-configurations)
  - [📦 Installation](#-installation)
    - [Quick Installation](#quick-installation)
    - [Docker Installation](#docker-installation)
  - [⚙️ Basic Configuration](#️-basic-configuration)
    - [Create a Simple Endpoint](#create-a-simple-endpoint)
  - [🚀 Usage Examples](#-usage-examples)
    - [Basic API Call](#basic-api-call)
    - [With Persistence (Redis required)](#with-persistence-redis-required)
    - [Advanced Search](#advanced-search)
  - [📚 Documentation](#-documentation)
  - [🐳 Docker Usage](#-docker-usage)
    - [Quick Start with Docker](#quick-start-with-docker)
    - [Environment Variables](#environment-variables)
  - [🤝 Contributing](#-contributing)
    - [Development Setup](#development-setup)
    - [Running Tests](#running-tests)
  - [📋 Changelog](#-changelog)
    - [Recent Updates](#recent-updates)
  - [📄 License](#-license)

## 🚀 Quick Start

Get up and running in under 2 minutes:

```bash
# Clone and setup
git clone <repository-url>
cd mock-and-roll

# Install dependencies
pip install -r requirements.txt
# OR with Poetry: poetry install

# Start interactive server
./mockctl start

# Choose configuration and test
curl http://localhost:8000/
```

**That's it!** 🎉 Your mock API server is running with Swagger UI at `http://localhost:8000/docs`

## ✨ Key Features

### 🎯 Core Functionality
- **Dynamic Endpoint Configuration**: Create REST endpoints through JSON config files
- **Multiple Authentication Methods**: API keys, Basic Auth, OIDC/OAuth2, sessions, CSRF tokens
- **Request Schema Validation**: JSON Schema validation for request bodies
- **Conditional Responses**: Different responses based on request conditions
- **Template Variables**: Dynamic values like `{{random_uuid}}`, `{{timestamp}}`
- **Path Parameters**: Dynamic URL parameters with automatic substitution

### 🏗️ Architecture & Management
- **Clean Architecture**: Domain-driven design with clear separation of concerns
- **Unified CLI**: Comprehensive command-line interface for server management
- **Log Search**: Advanced log analysis with regex filtering and time-based queries
- **Process Management**: Start, stop, and monitor multiple server instances
- **Configuration Profiles**: Pre-built configurations for different use cases

### 🔧 Developer Experience
- **Interactive Swagger UI**: Auto-generated API documentation with authentication testing
- **Air-gapped Support**: Offline Swagger UI with local static assets (no CDN dependencies)
- **Hot Reloading**: Development mode with automatic code updates
- **Comprehensive Logging**: Request/response tracking with configurable verbosity
- **Redis Persistence**: Optional data persistence with CRUD operations
- **Docker Support**: Ready-to-use containerization

## 🛠 Management CLI

The `mockctl` command provides comprehensive server management:

```bash
# Server Management
./mockctl start                     # Interactive config selection
./mockctl start basic --port 8080   # Start specific config
./mockctl stop --all                # Stop all servers
./mockctl list                      # Show running servers
./mockctl --json list               # JSON output for scripting

# Monitoring & Logs
./mockctl logs --lines 100                # View recent logs
./mockctl search basic "/api/users"       # Search basic config logs
./mockctl search all "/docs"              # Search all configs
./mockctl search vmanage "/items" --since "1h ago" # Time-filtered search

# Configuration & Testing
./mockctl config-help               # Configuration guide
./mockctl test vmanage              # Test endpoints

# Version Information
./mockctl version                   # Show version information
./mockctl --version                 # Show version (global flag)
./mockctl -v                        # Show version (short flag)

# Output Formatting
./mockctl --no-emoji list           # Clean text output (removes emojis)
./mockctl --json config-help        # Machine-readable JSON output
./mockctl --json search "/api"      # JSON search results for automation
```

**Global Options:**
- `--json`: Output results in JSON format for scripting and automation
- `--no-emoji`: Remove emojis from text output for cleaner display (ignored when using `--json`)

All commands support both `--json` and `--no-emoji` flags to customize output formatting.

## 📂 Available Configurations

| Configuration | Description | Endpoints | Features |
|---------------|-------------|-----------|----------|
| **basic** | Simple REST API | 1 | API key auth, basic CRUD |
| **persistence** | Full-featured API | 12 | Redis persistence, advanced auth |
| **vmanage** | Cisco SD-WAN API | 25+ | Multi-factor auth, realistic workflows |
| **airgapped** | Offline REST API | 1 | Air-gapped Swagger UI, no CDN dependencies |

Each configuration includes:
- `api.json` - Server settings and metadata
- `auth.json` - Authentication methods and keys
- `endpoints.json` - API endpoint definitions

## 📦 Installation

### Quick Installation

```bash
# macOS (with Homebrew)
brew install python@3.11
pip install -r requirements.txt

# Ubuntu/Debian
sudo apt install python3.11 python3-pip
pip install -r requirements.txt

# With Poetry (recommended)
curl -sSL https://install.python-poetry.org | python3 -
poetry install
```

### Docker Installation

```bash
# Docker Compose (recommended)
docker-compose up --build

# Or build manually
docker build -t mock-server .
docker run -p 8000:8000 mock-server

# Alpine Linux (minimal image)
docker build -f Dockerfile.alpine -t mock-server-alpine .
docker run -p 8000:8000 mock-server-alpine
```

### Cross-Platform Compatibility

Mock-and-Roll is designed to work across different operating systems and container environments:

**✅ Fully Supported Platforms:**
- **macOS** (Intel & Apple Silicon)
- **Ubuntu/Debian Linux**
- **Alpine Linux** (Docker containers)
- **CentOS/RHEL/Rocky Linux**
- **Windows** (via WSL2 or native Python)

**🔧 Port Detection Methods:**
The CLI automatically detects available ports using a simple, reliable socket-based approach:
- **Socket Binding Test**: Uses Python's built-in `socket` module to test port availability
- **Cross-Platform**: Works on all platforms without external dependencies
- **No OS Tools Required**: Doesn't rely on `lsof`, `netstat`, `ss`, or other system utilities
- **Alpine Linux Ready**: Works out-of-the-box in minimal container environments

This ensures reliable auto port detection on any platform where Python runs, without requiring additional system packages.

📋 **Need detailed installation instructions?** See [Installation Guide](docs/INSTALLATION.md)

## ⚙️ Basic Configuration

### Create a Simple Endpoint

**1. Create endpoint configuration (`my-config/endpoints.json`):**
```json
{
  "endpoints": [
    {
      "method": "GET",
      "path": "/users/{user_id}",
      "authentication": ["api_key"],
      "responses": [
        {
          "response": {
            "status_code": 200,
            "body": {
              "id": "{user_id}",
              "name": "User {{random_uuid}}",
              "created_at": "{{timestamp}}"
            }
          }
        }
      ]
    }
  ]
}
```

**2. Configure authentication (`my-config/auth.json`):**
```json
{
  "authentication_methods": {
    "api_key": {
      "type": "api_key",
      "name": "X-API-Key",
      "location": "header",
      "valid_keys": ["my-secret-key"]
    }
  }
}
```

**3. Set server metadata (`my-config/api.json`):**
```json
{
  "api": {
    "title": "My Mock API",
    "version": "1.0.0",
    "description": "Custom mock API server"
  }
}
```

**4. Start your server:**
```bash
./mockctl start my-config
```

## 🚀 Usage Examples

### Basic API Call
```bash
curl -H "X-API-Key: my-secret-key" http://localhost:8000/users/123
```

### With Persistence (Redis required)
```bash
# Start persistence configuration
./mockctl start persistence

# Create a product
curl -X POST http://localhost:8000/products \
  -H "X-API-Key: demo-api-key-123" \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "price": 999.99}'

# Retrieve it back
curl -H "X-API-Key: demo-api-key-123" http://localhost:8000/products/{id}
```

### Advanced Search

```bash
# Find all user API calls from the last hour (most recent basic logs)
./mockctl --json search basic "/api/users" --since "1h ago"

# Search across all configurations (most recent log per config)
./mockctl search all "/auth"

# Search all historical logs for a specific config
./mockctl search basic --all-logs "/docs"
```

### Air-gapped Environment
```bash
# Start air-gapped server (no CDN dependencies)
./mockctl start airgapped

# Access offline Swagger UI at http://localhost:8000/docs
# All assets (CSS/JS) served locally without internet connectivity
curl -H "X-API-Key: my-secret-key" http://localhost:8000/items
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Installation Guide](docs/INSTALLATION.md) | Complete installation instructions for all platforms |
| [Search Command](docs/features/SEARCH_COMMAND_IMPLEMENTATION.md) | Advanced log search functionality |
| [Clean Architecture](docs/architecture/README_clean_architecture.md) | Architecture design and patterns |
| [Development Guide](docs/development/CLEANUP_SUMMARY.md) | Development setup and maintenance |

📖 **Browse all documentation:** [docs/](docs/)

## 🐳 Docker Usage

### Quick Start with Docker
```bash
# Start with default configuration
docker-compose up

# Custom configuration
docker run -v ./my-config:/app/config mock-server

# With Redis persistence
docker-compose -f docker-compose.yml up
```

### Environment Variables
- `CONFIG_FOLDER`: Path to configuration directory
- `REDIS_HOST`: Redis server hostname (default: localhost)
- `REDIS_PORT`: Redis server port (default: 6379)

## 🤝 Contributing

We welcome contributions! Please see our [contribution guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone <repository-url>
cd mock-and-roll
poetry install
poetry run pre-commit install
```

### Running Tests

```bash
pytest tests/
python tests/test_search_functionality.py
```

## 📋 Changelog

All notable changes to this project are documented in our [CHANGELOG.md](CHANGELOG.md).

### Recent Updates

**Version 0.2.0** (2024-09-10)
- ✨ Advanced log search functionality with regex and time filtering
- 🏗️ Clean architecture implementation with domain-driven design
- 🔧 Enhanced CLI experience with JSON output mode
- 📊 Request/response correlation and status code grouping

**Version 0.1.0** (2024-08-XX)
- 🚀 Initial release with core mock API server functionality
- ⚙️ Configuration-driven endpoint development
- 🔐 Multiple authentication methods
- 🐳 Docker support and Redis persistence

For detailed release notes, migration guides, and complete version history, see the [full changelog](CHANGELOG.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Version 0.2.0** • [Changelog](CHANGELOG.md) • [Issues](https://github.com/bvandewe/mock-and-roll/issues) • [Docs](https://bvandewe.github.io/mock-and-roll/)
