
# REST API Mock Server

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![Redis](https://img.shields.io/badge/Redis-5.0+-red.svg)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Table of Contents

- [Quick Start](#-quick-start)
- [Management CLI](#-management-cli)
- [Features](#-features)
  - [Core Functionality](#-core-functionality)
  - [Authentication & Security](#-authentication--security)
  - [Developer Experience](#-developer-experience)
- [Project Structure](#-project-structure)
- [Installation](#️-installation)
  - [System Requirements](#system-requirements)
  - [macOS Installation](#macos-installation)
  - [Linux Installation](#linux-installation)
  - [Docker Installation](#docker-installation-cross-platform)
  - [Verification](#verification)
  - [Dependencies](#dependencies)
  - [Troubleshooting Installation](#troubleshooting-installation)
- [Configuration](#️-configuration)
  - [Configuration System](#configuration-system)
  - [Creating Custom Configurations](#creating-custom-configurations)
  - [Endpoint Configuration](#endpoint-configuration-endpointsjson)
  - [Authentication Configuration](#authentication-configuration-authjson)
  - [Template Variables & Dynamic Values](#template-variables--dynamic-values)
  - [Persistence Configuration](#persistence-configuration-redis)
  - [Logging Configuration](#logging-configuration-apijson)
  - [Environment Variables](#environment-variables)
- [Usage](#-usage)
  - [Starting the Server](#starting-the-server)
- [API Examples](#-api-examples)
- [Development](#-development)
- [Docker Usage](#-docker-usage)
- [Contributing](#-contributing)
- [License](#-license)
- [Troubleshooting](#-troubleshooting)



## 🚀 Quick Start

Get up and running in under 2 minutes:

```bash
# Clone and setup
git clone <repository-url>
cd mock-and-roll

# Install with Poetry
poetry install && poetry shell

# Start the server (interactive configuration selection)
./mockctl start

# Or start with a specific configuration
./mockctl start basic           # Simple REST API
./mockctl start vmanage         # SD-WAN vManage API mock
./mockctl start persistence     # API with Redis persistence
```

**🎉 That's it!** Your mock API server is now running at:
- **API Base URL**: http://localhost:8001 (default)
- **Interactive Docs**: http://localhost:8001/docs
- **OpenAPI Schema**: http://localhost:8001/openapi.json

### 🎯 Simple Management Commands

```bash
# Start any configuration
./mockctl start                    # Interactive selection
./mockctl start basic --port 8000  # Basic config on custom port

# Manage servers
./mockctl list                     # See what's running
./mockctl stop                     # Stop servers (auto-detect)
./mockctl stop --all               # Stop everything

# Monitor activity
./mockctl logs                     # Recent logs
./mockctl success detailed         # Success analysis

# Get help
./mockctl help                     # All available scripts
./mockctl config-help              # Configuration guide
```

### 📂 Available Configurations

- **basic**: Simple REST API with 1 endpoint
- **persistence**: Sample API with Redis caching (12 endpoints)  
- **vmanage**: Cisco SD-WAN vManage API simulation (incl. MFA authentication)

The interactive Swagger UI organizes endpoints into clear categories:
- **Your configured endpoints** (from `endpoints.json`) grouped by tags:
  - **Items** - Product/inventory operations
  - **User Management** - User creation and management  
  - **Authentication** - Login and security operations
  - **Devices** - Device monitoring (vManage example)
  - **Templates** - Configuration templates (vManage example)
- **Cache** - Redis cache management (`/system/cache/*`)  
- **Logs** - Runtime logging management (`/system/logging/*`)

All endpoint groups start **collapsed by default** for a clean overview.

### 🔥 Key Features at a Glance
- **Dynamic Value Substitution**: Use placeholders like `${auth.vmanage_session.random_session.session_id}` 
- **Template Variables**: Realistic timestamp generation with `{{timestamp}}`, `{{date}}`, `{{random_uuid}}`
- **Automatic Timestamp Detection**: Static timestamps automatically replaced with realistic recent ones
- **Multi-Factor Authentication**: Enforce multiple auth methods (session + CSRF token)
- **Request Schema Validation**: JSON Schema validation for request bodies
- **OpenAPI Tag Organization**: Categorize endpoints with custom tags for organized Swagger UI
- **Customizable Swagger UI**: Configure interface behavior (collapsed sections, timing display, etc.)
- **Redis Persistence**: Optional data persistence with CRUD operations
- **Comprehensive Logging**: Multi-logger capture, request/response tracking, runtime configuration
- **Real API Behavior**: Mimics production authentication flows like vManage SD-WAN API


### Example: Create a Product with Persistence

**Endpoint config (`configs/basic/endpoints.json`):**
```json
{
  "endpoints": [
    {
      "method": "POST",
      "path": "/products",
      "authentication": ["api_key"],
      "persistence": {
        "entity_name": "products",
        "action": "create"
      },
      "request_body_schema": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "Product name",
            "example": "Laptop Pro"
          },
          "price": {
            "type": "number",
            "description": "Product price in USD",
            "example": 999.99
          },
          "category": {
            "type": "string",
            "description": "Product category",
            "example": "electronics"
          },
          "description": {
            "type": "string",
            "description": "Product description",
            "example": "High-performance laptop for professionals"
          },
          "in_stock": {
            "type": "boolean",
            "description": "Whether product is in stock",
            "example": true
          }
        },
        "required": ["name", "price"]
      },
      "responses": [
        {
          "body_conditions": null,
          "response": {
            "status_code": 201,
            "body": {
              "message": "Product created successfully.",
              "product_id": "{{random_uuid}}",
              "created_at": "{{current_timestamp}}"
            }
          }
        }
      ]
    },
    {
      "method": "GET",
      "path": "/products/{product_id}",
      "authentication": ["api_key"],
      "persistence": {
        "entity_name": "products",
        "action": "retrieve"
      }
    }
  ]
}
```

**Auth config (`configs/basic/auth.json`):**
```json
{
  "authentication_methods": {
    "api_key": {
      "type": "api_key",
      "name": "X-API-Key",
      "location": "header",
      "valid_keys": ["demo-api-key-123", "test-key-456", "admin-key-789"]
    }
  }
}
```

**Create a new product (persistence action):**
```bash
curl -X 'POST' \
  'http://localhost:8080/products' \
  -H 'accept: application/json' \
  -H 'X-API-Key: demo-api-key-123' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Laptop Pro",
  "price": 999.99,
  "category": "electronics",
  "description": "High-performance laptop for professionals",
  "in_stock": true
}'
```

**Response:**

**201 Created**
```json
{
  "message": "Product created successfully.",
  "product_id": "3d2ae57c-ac07-4709-9977-a45dc928084d",
  "created_at": "2025-08-12T12:07:10.104556Z",
  "id": "fddcbefc-acef-4bd3-8037-07f727eeea7c",
  "name": "Laptop Pro",
  "price": 999.99,
  "category": "electronics",
  "description": "High-performance laptop for professionals",
  "in_stock": true
}
```

**Retrieve the created product:**
```bash
curl -X 'GET' \
  'http://localhost:8080/products/fddcbefc-acef-4bd3-8037-07f727eeea7c' \
  -H 'accept: application/json' \
  -H 'X-API-Key: demo-api-key-123'
```

**Response:**
```json
{
  "id": "fddcbefc-acef-4bd3-8037-07f727eeea7c",
  "entity_type": "products",
  "created_at": "2025-08-12T12:07:10.103049",
  "data": {
    "name": "Laptop Pro",
    "price": 999.99,
    "category": "electronics",
    "description": "High-performance laptop for professionals",
    "in_stock": true
  }
}
```

---

## 🛠 Management CLI

The mock server includes a unified Python CLI application that provides comprehensive server management with cross-platform support.

### Usage

**Primary Interface:** `./mockctl` - Main entry point  
**Direct Access:** `./mockctl` or `python3 mockctl.py` - Direct CLI access

### Available Commands

| Command | Description | Examples |
|---------|-------------|----------|
| `start` | Start mock server with configuration | `./mockctl start basic --port 8080` |
| `stop` | Stop running servers | `./mockctl stop --all` |
| `list` | List running servers | `./mockctl list` |
| `logs` | View server logs with filtering | `./mockctl logs --filter /api/users` |
| `test` | Test server endpoints | `./mockctl test --port 8000` |
| `success` | Generate success rate reports | `./mockctl success detailed` |
| `config-help` | Show configuration guide | `./mockctl config-help` |
| `help` | Show detailed help | `./mockctl help` |

### Examples

```bash
# Interactive configuration selection
./mockctl start                    # Choose from available configs

# Start specific configuration
./mockctl start vmanage --port 8080 --reload

# Stop servers by different methods
./mockctl stop                     # Auto-detect or interactive selection
./mockctl stop basic               # Stop by config name
./mockctl stop --port 8001         # Stop by port
./mockctl stop --all               # Stop all servers

# Server monitoring and logs
./mockctl list                     # List all running servers
./mockctl logs --lines 100         # View last 100 log entries
./mockctl logs --filter REQUEST:   # Filter logs by pattern
./mockctl logs --port 8000         # View logs from specific server
```

#### 📋 Logs Command Details

The `logs` command provides comprehensive log viewing capabilities:

**Basic Usage:**
```bash
# View recent logs from all running servers
./mockctl logs

# Limit number of lines
./mockctl logs --lines 50

# View logs from a specific server
./mockctl logs --port 8000

# Filter logs by pattern
./mockctl logs --filter "ERROR"
./mockctl logs --filter "REQUEST:"
```

**Multi-Server Support:**
- When no `--port` is specified, shows logs from all running servers
- Each server's logs are clearly separated with headers
- Automatically detects and excludes stopped servers

**Server State Tracking:**
- Each server tracks its own log file location
- Server state includes log file paths for better management
- Supports concurrent servers on different ports

### Features

- **🎯 Interactive Configuration Selection**: Choose from available configs when none specified
- **🔄 Smart Process Management**: Robust process tracking and management across platforms
- **📊 Enhanced State Management**: JSON-based server state tracking
- **🌐 Cross-platform Support**: Works on macOS, Linux, and Windows
- **🛡️ Graceful Degradation**: Works even with missing optional dependencies
- **🎨 Colored Output**: Clear, readable status messages and error reporting

---

## �🚀 Features

### Core API Functionality
- **Dynamic Endpoint Configuration**: Create REST endpoints through JSON config files (`configs/{config-name}/endpoints.json`)
- **HTTP Method Support**: Full support for GET, POST, PUT, DELETE, PATCH operations
- **Path Parameter Support**: Dynamic URL parameters with automatic substitution in responses (e.g., `/items/{item_id}`)
- **Query Parameter Handling**: Extract and use query parameters in endpoint logic
- **Request Body Processing**: Support for JSON and form-encoded (`application/x-www-form-urlencoded`) request bodies
- **Conditional Responses**: Different responses based on request body conditions using `body_conditions`
- **Custom Response Headers**: Support for custom headers in endpoint responses
- **Status Code Control**: Configurable HTTP status codes for different response scenarios
- **Content Type Support**: Multiple content types including JSON, HTML, and plain text responses

### Request/Response Features
- **Request Schema Validation**: Comprehensive JSON Schema validation for request payloads with `request_body_schema`
- **Dynamic Response Generation**: Template variables and placeholders in response bodies
- **Response Templating**: Support for dynamic values like `{{random_uuid}}` and `{{current_timestamp}}`
- **Request Body Merging**: Automatically merge request data with response templates
- **Error Response Handling**: Structured error responses for validation failures and authentication errors
- **CORS Support**: Cross-Origin Resource Sharing headers for web applications

### Authentication & Security
- **Multiple Authentication Methods**: 
  - **API Key**: Header-based API key authentication (`X-API-Key`)
  - **HTTP Basic Auth**: Username/password authentication
  - **OIDC/OAuth2**: Bearer token authentication with scope validation
  - **Session Authentication**: Cookie-based sessions (`JSESSIONID`)
  - **CSRF Token Protection**: Anti-CSRF token validation (`X-XSRF-TOKEN`)
- **Multi-Factor Authentication**: Enforce multiple auth methods simultaneously (AND logic)
- **Flexible Authentication**: Multiple auth methods per endpoint with OR logic within each method
- **Dynamic Authentication Values**: Runtime placeholder resolution using `${auth.method.selector.property}` syntax
- **Session Management**: Realistic session handling with dynamic session ID generation
- **CSRF Token Correlation**: Automatic correlation between session IDs and CSRF tokens
- **Scope-based Authorization**: OIDC scope validation for fine-grained access control
- **OpenAPI Integration**: Full Swagger UI support with security scheme visualization

### Data Persistence & Caching
- **Redis Integration**: Optional Redis-based persistence for entity storage
- **CRUD Operations**: Complete Create, Read, Update, Delete, List operations for entities
- **Entity Management**: Type-based entity storage with automatic ID generation
- **Cache Management**: System endpoints for Redis inspection and management
- **Data Validation**: Entity data validation before storage
- **Automatic Timestamps**: Created/updated timestamp tracking
- **Entity Relationships**: Support for related entity data storage

### System & Management Features
- **Flexible Configuration Management**:
  - Custom config folder support via `--config-folder` CLI argument
  - Multiple config source priority handling (CLI > ENV > Docker > Default)
  - Environment-specific configuration loading
  - Pre-configured API templates support
- **Cache Administration**: 
  - `GET /system/cache/info` - Redis connection status and statistics (requires system auth)
  - `DELETE /system/cache/flush` - Clear all cached data (requires system auth)
  - `GET /system/cache/entities/{entity_name}` - List entities by type (requires system auth)
  - `GET /system/cache/entities/{entity_name}/{entity_id}` - Get specific entity details (requires system auth)
  - `DELETE /system/cache/entities/{entity_name}/{entity_id}` - Delete specific entities (requires system auth)
- **Logging Management**:
  - `GET /system/logging/status` - Get current logging configuration and status (requires system auth)
  - `POST /system/logging/config` - Update logging configuration at runtime (requires system auth)
  - `GET /system/logging/logs` - Retrieve recent log entries from log file (requires system auth)
  - `DELETE /system/logging/logs` - Clear log file (requires `allow_log_deletion: true` and system auth)
  - **File Logging**: Automatic log file creation and management at configurable location
  - **Dual Output**: Simultaneous logging to both stdout/stderr and file
  - **Runtime Configuration**: Change log levels and settings without restart
- **Enhanced Server Runner**: Custom `run_server.py` script with full CLI argument support
- **Centralized Authentication**: System endpoints use the same `auth.json` configuration as regular API endpoints
- **Health Monitoring**: Server health and status endpoints
- **Configuration Validation**: Startup validation of JSON configuration files
- **Error Logging**: Comprehensive error logging and debugging information

### Dynamic Value Substitution
- **Authentication Placeholders**: 
  - `${auth.vmanage_session.random_session.session_id}` - Random session selection
  - `${auth.vmanage_session.random_session.csrf_token}` - Correlated CSRF tokens
  - `${auth.csrf_token.random_key}` - Random CSRF token selection
- **Response Templates**: Dynamic value injection in response bodies and headers
- **Timestamp Templates**: Realistic timestamp generation for mock data
  - `{{timestamp}}` - Generates realistic ISO 8601 timestamps (recent but not current)
  - `{{date}}` - Generates realistic dates in YYYY-MM-DD format  
  - `{{unix_timestamp}}` - Generates realistic Unix timestamps (10 digits)
  - `{{unix_timestamp_ms}}` - Generates realistic Unix timestamps in milliseconds (13 digits)
  - `{{current_timestamp}}` - Generates current timestamp in ISO 8601 format
  - `{{random_uuid}}` - Generates random UUIDs
- **Automatic Timestamp Detection**: Automatically replaces static timestamps in responses with realistic ones
  - Detects and replaces ISO 8601 timestamps: `2025-08-19T10:30:00Z`
  - Detects and replaces Unix timestamps: `1724058600`
  - Detects and replaces date patterns: `2025-08-19`
- **Real-time Resolution**: Values resolved at request time for realistic behavior
- **State Correlation**: Maintain consistency between related authentication values

### Developer Experience
- **Interactive Documentation**: Auto-generated Swagger UI at `/docs` with authentication testing
- **OpenAPI Schema**: Complete OpenAPI 3.0 specification at `/openapi.json`
- **Hot Reloading**: Development mode with automatic code reloading
- **Advanced Logging System**: 
  - **Multi-Logger Support**: Captures all HTTP requests, server events, and application logs
  - **Request/Response Middleware**: Detailed logging of HTTP calls with timing and body content
  - **Configurable Output**: Dual output (stdout + file) with independent control
  - **Runtime Configuration**: Change log levels and settings via REST API without restart
  - **File Management**: Automatic log file creation, rotation, and size management
  - **Debug Mode**: Comprehensive request/response body logging for development
  - **Production Ready**: Structured logging with appropriate verbosity levels
- **Docker Support**: Ready-to-use Docker configuration with Redis orchestration
- **Configuration Validation**: Startup validation with clear error messages
- **VS Code Integration**: Pre-configured development environment settings

## 📁 Project Structure

```
mock-and-roll/
├── src/                          # Main application source
│   ├── main.py                   # FastAPI application and core logic
│   ├── app/                      # Application modules
│   ├── auth/                     # Authentication handlers
│   ├── config/                   # Configuration loaders
│   └── routes/                   # API route handlers
├── configs/                      # Configuration sets
│   ├── basic/                    # Simple REST API configuration
│   │   ├── api.json
│   │   ├── auth.json
│   │   └── endpoints.json
│   ├── persistence/              # API with Redis persistence
│   │   ├── api.json
│   │   ├── auth.json
│   │   └── endpoints.json
│   └── vmanage/                  # Cisco SD-WAN vManage API
│       ├── api.json
│       ├── auth.json
│       └── endpoints.json
├── src/
│   ├── cli/
│   │   └── mockctl.py         # Unified Python CLI for server management
│   ├── app/                      # FastAPI application
│   ├── auth/                     # Authentication modules
│   ├── config/                   # Configuration loaders
│   ├── handlers/                 # Request handlers
│   ├── middleware/               # Middleware components
│   ├── models/                   # Data models
│   ├── persistence/              # Redis integration
│   ├── processing/               # Template processing
│   └── routes/                   # Route definitions
├── mockctl                    # Main CLI entry point
├── Dockerfile                    # Docker container configuration
├── docker-compose.yml           # Multi-service orchestration
├── pyproject.toml               # Python dependencies and project metadata
└── README.md                    # This file
```

## 🛠️ Installation

### System Requirements

**Supported Platforms:**
- macOS 10.15+ (Catalina or later)
- Linux (Ubuntu 18.04+, CentOS 7+, Debian 9+, etc.)
- Windows 10+ (via WSL recommended)

**Required Software:**
- Python 3.11+ 
- Git

**Optional (Enhanced Features):**
- Redis Server (for persistence configuration)
- Docker & Docker Compose (for containerized deployment)

### macOS Installation

```bash
# Install Python 3.11+ (if not already installed)
# Option 1: Using Homebrew
brew install python@3.11

# Option 2: Using pyenv
brew install pyenv
pyenv install 3.11.7
pyenv local 3.11.7

# Install Poetry (recommended)
curl -sSL https://install.python-poetry.org | python3 -

# Clone and setup project
git clone <repository-url>
cd mock-and-roll

# Install dependencies with Poetry
poetry install

# Or install with pip if Poetry not available
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # or pip install fastapi uvicorn redis psutil requests

# Optional: Install Redis for persistence features
brew install redis
brew services start redis
```

### Linux Installation

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install Python 3.11+ and pip
sudo apt install python3.11 python3.11-venv python3-pip git

# Install Poetry (recommended)
curl -sSL https://install.python-poetry.org | python3 -

# Clone and setup project
git clone <repository-url>
cd mock-and-roll

# Install dependencies with Poetry
poetry install

# Or install with pip if Poetry not available
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn redis psutil requests

# Optional: Install Redis for persistence features
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### CentOS/RHEL/Fedora
```bash
# CentOS/RHEL
sudo yum install python3 python3-pip git
# OR for Fedora
sudo dnf install python3 python3-pip git

# Install Poetry (recommended)
curl -sSL https://install.python-poetry.org | python3 -

# Clone and setup project
git clone <repository-url>
cd mock-and-roll

# Install dependencies with Poetry
poetry install

# Or install with pip if Poetry not available
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn redis psutil requests

# Optional: Install Redis for persistence features
# CentOS/RHEL
sudo yum install redis
sudo systemctl start redis
sudo systemctl enable redis
# OR for Fedora
sudo dnf install redis
sudo systemctl start redis
sudo systemctl enable redis
```

#### Alpine Linux
Alpine Linux requires additional system tools for proper operation:

```bash
# Essential package installation
apk update
apk add --no-cache python3 py3-pip git

# Install command-line tools required by the server management
apk add --no-cache procps util-linux coreutils findutils
apk add --no-cache net-tools iproute2 lsof curl wget bash

# Install Poetry (recommended)
curl -sSL https://install.python-poetry.org | python3 -

# Clone and setup project
git clone <repository-url>
cd mock-and-roll

# 🚀 Quick Setup (Recommended for Alpine)
# Use the automated setup script for Alpine Linux
./setup_alpine.sh

# Or manual setup:
# Install dependencies with Poetry
poetry install

# Or install with pip if Poetry not available
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Optional: Install Redis for persistence features
apk add --no-cache redis
rc-service redis start
rc-update add redis
```

**Alpine Package Breakdown:**
- `procps` - Provides `ps`, `top`, `pgrep`, `pkill` for process management
- `util-linux` - Provides `kill`, `lscpu` for process termination
- `coreutils` - Essential text processing tools (`grep`, `awk`, `cut`, `sort`)
- `net-tools` - Network diagnostics (`netstat`, `ifconfig`)
- `iproute2` - Modern networking tools (`ss`, `ip`)
- `lsof` - List open files/ports for server detection
- `bash` - Better shell compatibility for scripts

**Minimal Alpine Installation:**
For minimal setups, only these packages are essential:
```bash
apk add --no-cache procps lsof
```

**Docker Alpine Usage:**
Use the provided Alpine Dockerfile for containerized deployment:
```bash
# Build Alpine-based image
docker build -f Dockerfile.alpine -t mock-server-alpine .

# Run Alpine container
docker run -p 8000:8000 mock-server-alpine
```

### Docker Installation (Cross-platform)

```bash
# Clone the repository
git clone <repository-url>
cd mock-and-roll

# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t mock-server .
docker run -p 8000:8000 mock-server
```

### Verification

```bash
# Verify Python version
python3 --version  # Should show 3.11+

# Verify installation
./mockctl --help

# Test basic functionality
./mockctl start basic --port 8000
# In another terminal:
curl http://localhost:8000/
./mockctl stop
```

### Dependencies

**Core Dependencies (automatically installed):**
- `fastapi` - Modern web framework
- `uvicorn` - ASGI server
- `redis` - Redis client (for persistence features)
- `psutil` - Process management utilities
- `requests` - HTTP client library
- `pyhumps` - JSON key transformation
- `pyjwt` - JWT token handling
- `python-dateutil` - Date parsing utilities
- `python-multipart` - Form data handling
- `email-validator` - Email validation

**Development Dependencies:**
- `pytest` - Testing framework
- `python-dotenv` - Environment variable management
- `pre-commit` - Git hooks for code quality

### Troubleshooting Installation

**Common Issues:**

1. **Python version too old**
   ```bash
   # Check version
   python3 --version
   # Upgrade if needed (see platform-specific instructions above)
   ```

2. **Permission errors on macOS/Linux**
   ```bash
   # Use virtual environment to avoid system-wide installs
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   ```

3. **Poetry not found**
   ```bash
   # Add Poetry to PATH (typically needed after installation)
   export PATH="$HOME/.local/bin:$PATH"
   # Add to ~/.bashrc or ~/.zshrc for persistence
   ```

4. **Redis connection errors**
   ```bash
   # Check if Redis is running
   redis-cli ping  # Should return PONG
   # Start Redis if needed (see platform-specific instructions above)
   ```

5. **Alpine Linux - externally-managed-environment error**
   ```bash
   # If you see "externally-managed-environment" when trying to install packages:
   
   # Option 1: Use the automated setup script (recommended)
   ./setup_alpine.sh
   
   # Option 2: Manual virtual environment setup
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   
   # Option 3: Use Poetry (if available)
   poetry config virtualenvs.in-project true
   poetry install
   
   # The mockctl script will automatically detect and use the virtual environment
   ```

6. **Alpine Linux - Command not found errors**
   ```bash
   # If you see "command not found" for ps, kill, lsof, etc.
   # Install the required system tools:
   apk add --no-cache procps util-linux lsof
   
   # Verify tools are available:
   ps --version
   kill -V
   lsof -v
   ```

7. **Alpine Linux - BusyBox compatibility issues**
   ```bash
   # Some Alpine BusyBox tools behave differently than GNU versions
   # The server management automatically handles these differences
   # If you encounter issues, install GNU versions:
   apk add --no-cache coreutils findutils grep
   ```

## ⚙️ Configuration

### Configuration System

The mock server uses a flexible configuration system with pre-built configuration sets:

**Available Configuration Sets:**
```
configs/
├── basic/              # Simple REST API (1 endpoint)
│   ├── api.json
│   ├── auth.json
│   └── endpoints.json
├── persistence/        # API with Redis persistence (12 endpoints)
│   ├── api.json
│   ├── auth.json
│   └── endpoints.json
└── vmanage/           # Cisco SD-WAN vManage API simulation
    ├── api.json
    ├── auth.json
    └── endpoints.json
```

**Usage with CLI:**
```bash
# Interactive selection
./mockctl start

# Specific configuration
./mockctl start basic           # Uses configs/basic/
./mockctl start persistence     # Uses configs/persistence/
./mockctl start vmanage         # Uses configs/vmanage/
```

**Configuration File Structure:**
Each configuration set contains three files:
- `api.json` - API metadata and logging settings  
- `auth.json` - Authentication methods and keys
- `endpoints.json` - API endpoint definitions

### Creating Custom Configurations

**1. Copy an existing configuration:**
```bash
cp -r configs/basic configs/my-api
```

**2. Edit the configuration files:**
```bash
# Edit endpoints
vim configs/my-api/endpoints.json

# Edit authentication  
vim configs/my-api/auth.json

# Edit API settings
vim configs/my-api/api.json
```

**3. Start with your custom configuration:**
```bash
./mockctl start my-api
```

### Endpoint Configuration (`endpoints.json`)

Define your mock endpoints with this structure:

```json
{
    "endpoints": [
        {
            "method": "GET|POST|PUT|DELETE|PATCH",
            "path": "/your/path/{parameter}",
            "tag": "API Category",
            "authentication": ["api_key", "basic_auth", "oidc_auth_code"],
            "required_scopes": ["read", "write"],
            "request_body_schema": {
                "type": "object",
                "properties": {
                    "field": {"type": "string"}
                },
                "required": ["field"]
            },
            "persistence": {
                "entity_name": "entities",
                "action": "create"
            },
            "responses": [
                {
                    "body_conditions": {
                        "key": "value"
                    },
                    "response": {
                        "status_code": 200,
                        "headers": {
                            "X-Custom-Header": "value"
                        },
                        "body": {
                            "message": "Response with {parameter} substitution"
                        }
                    }
                }
            ]
        }
    ]
}
```

**Example from Default Configuration:**
```json
{
    "method": "GET",
    "path": "/items/{item_id}",
    "tag": "Items",
    "authentication": ["api_key"],
    "responses": [
        {
            "body_conditions": null,
            "response": {
                "status_code": 200,
                "body": {
                    "message": "Here is the item you requested.",
                    "item_id": "{item_id}",
                    "data": {
                        "name": "A Mocked Item",
                        "value": 123
                    }
                }
            }
        }
    ]
}
```

**Example from vManage Configuration:**
```json
{
    "method": "GET",
    "path": "/dataservice/device/monitor",
    "tag": "Devices",
    "authentication": ["vmanage_session", "csrf_token"],
    "responses": [
        {
            "body_conditions": null,
            "response": {
                "status_code": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "X-XSRF-TOKEN": "${auth.vmanage_session.random_session.csrf_token}"
                },
                "body": {
                    "data": [
                        {
                            "device_id": "C8K-001",
                            "hostname": "vEdge-C8K-001",
                            "device_type": "vedge",
                            "device_model": "vedge-C8000V",
                            "status": "normal",
                            "system_ip": "1.1.1.1",
                            "site_id": "100",
                            "version": "20.6.3",
                            "uptime": "15:23:45:10",
                            "last_updated": "2025-08-19T10:30:00Z"
                        }
                    ]
                }
            }
        }
    ]
}
```

### OpenAPI Tag Configuration

Organize your API endpoints in the Swagger UI using tags. Tags can be configured at two levels:

#### 1. Endpoint-Level Tags (`endpoints.json`)

Add a `tag` field to any endpoint to categorize it in the Swagger UI:

```json
{
    "method": "GET",
    "path": "/users/{user_id}",
    "tag": "User Management",
    "authentication": ["api_key"],
    "responses": [...]
}
```

**Tag Configuration Options:**
- **String**: Simple tag name
  ```json
  "tag": "Authentication"
  ```
- **Object**: Tag with metadata (name extracted for endpoint)
  ```json
  "tag": {
      "name": "User Management",
      "description": "User operations"
  }
  ```
- **Array**: Multiple tags (names extracted)
  ```json
  "tag": ["Users", "Management"]
  ```

#### 2. Global Tag Metadata (`api.json`)

Define tag descriptions and documentation in your API configuration:

```json
{
    "api_name": "My API",
    "openapi_tags": [
        {
            "name": "Authentication",
            "description": "Login, session management and security operations"
        },
        {
            "name": "User Management",
            "description": "User creation, authentication and management operations"
        },
        {
            "name": "Items",
            "description": "Operations with items and inventory management"
        },
        {
            "name": "Devices",
            "description": "Device monitoring and configuration operations"
        },
        {
            "name": "Templates",
            "description": "Configuration templates and policy management"
        }
    ]
}
```

This creates organized, well-documented API sections in the Swagger UI with:
- **Collapsible sections** grouped by tag
- **Descriptions** for each tag category
- **Consistent organization** across all endpoints

### Swagger UI Configuration (`api.json`)

Customize the Swagger UI interface behavior and appearance:

```json
{
    "api_name": "My API",
    "swagger_ui": {
        "doc_expansion": "none",
        "default_models_expand_depth": -1,
        "default_model_expand_depth": -1,
        "display_request_duration": true,
        "try_it_out_enabled": true
    }
}
```

**Configuration Options:**
- **`doc_expansion`**: Controls initial expansion state
  - `"none"` - All sections collapsed (default)
  - `"list"` - Expand operations only
  - `"full"` - Expand everything
- **`default_models_expand_depth`**: Model schema expansion depth (-1 = collapsed)
- **`default_model_expand_depth`**: Individual model detail expansion (-1 = collapsed)
- **`display_request_duration`**: Show request timing in UI (true/false)
- **`try_it_out_enabled`**: Enable "Try it out" by default (true/false)

This configuration creates a clean, professional interface where:
- ✅ **All endpoint groups start collapsed** for better overview
- ✅ **Models don't auto-expand** to reduce visual clutter
- ✅ **Request timing is displayed** for performance insights
- ✅ **Try it out is enabled** for easy API testing

### Authentication Configuration (`auth.json`)

Configure authentication methods with support for dynamic value resolution:

```json
{
    "authentication_methods": {
        "api_key": {
            "type": "api_key",
            "name": "X-API-Key",
            "location": "header",
            "valid_keys": ["your-api-key-here"]
        },
        "basic_auth": {
            "type": "http_basic",
            "valid_credentials": [
                {"username": "admin", "password": "secret"}
            ]
        },
        "oidc_auth_code": {
            "type": "oidc",
            "grant_type": "authorization_code",
            "valid_tokens": [
                {"access_token": "your-token", "scope": "read write"}
            ]
        },
        "vmanage_session": {
            "type": "session",
            "cookie_name": "JSESSIONID",
            "valid_sessions": [
                {
                    "session_id": "vmanage-session-123",
                    "csrf_token": "mock-csrf-token-xyz",
                    "user": "admin"
                },
                {
                    "session_id": "vmanage-session-456",
                    "csrf_token": "mock-csrf-token-abc",
                    "user": "operator"
                },
                {
                    "session_id": "vmanage-session-789",
                    "csrf_token": "mock-csrf-token-def",
                    "user": "admin"
                }
            ]
        },
        "csrf_token": {
            "type": "csrf",
            "header_name": "X-XSRF-TOKEN",
            "valid_tokens": [
                "mock-csrf-token-xyz",
                "mock-csrf-token-abc",
                "mock-csrf-token-def",
                "csrf-alt-token-123",
                "csrf-alt-token-456"
            ]
        }
    }
}
```

#### Dynamic Authentication Values

The mock server supports **dynamic authentication value substitution** using placeholder syntax. This eliminates hardcoded values and enables realistic session/token behavior:

**Placeholder Syntax:**
```
${auth.method.selector.property}
```

**Available Placeholders:**
- `${auth.vmanage_session.random_session.session_id}` - Random session ID from valid_sessions
- `${auth.vmanage_session.random_session.csrf_token}` - Corresponding CSRF token for the session
- `${auth.csrf_token.random_key}` - Random CSRF token from valid_tokens

**Example Usage in Endpoints:**
```json
{
    "method": "POST",
    "path": "/j_security_check",
    "responses": [
        {
            "response": {
                "status_code": 200,
                "headers": {
                    "Set-Cookie": "JSESSIONID=${auth.vmanage_session.random_session.session_id}; Path=/; HttpOnly"
                },
                "body": {
                    "message": "Authentication successful"
                }
            }
        }
    ]
},
{
    "method": "GET",
    "path": "/dataservice/client/token",
    "authentication": ["vmanage_session"],
    "responses": [
        {
            "response": {
                "status_code": 200,
                "headers": {
                    "X-XSRF-TOKEN": "${auth.vmanage_session.random_session.csrf_token}"
                },
                "body": "${auth.vmanage_session.random_session.csrf_token}"
            }
        }
    ]
}
```

#### Multi-Factor Authentication

For endpoints requiring multiple authentication factors (like vManage APIs), specify multiple methods:

```json
{
    "method": "GET",
    "path": "/dataservice/device/monitor",
    "authentication": [
        "vmanage_session",
        "csrf_token"
    ],
    "responses": [
        {
            "response": {
                "status_code": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "X-XSRF-TOKEN": "${auth.vmanage_session.random_session.csrf_token}"
                },
                "body": {
                    "data": [...]
                }
            }
        }
    ]
}
```

**Authentication Logic:**
- **Multiple methods = AND logic**: All specified methods must be valid
- **Single method = OR logic**: Any valid credential for that method works
- **No authentication = Public endpoint**: No validation required

#### CSRF Token Management

The server automatically includes CSRF tokens in response headers for authenticated endpoints:

```json
{
    "headers": {
        "X-XSRF-TOKEN": "${auth.vmanage_session.random_session.csrf_token}"
    }
}
```

This enables proper CSRF token rotation and client-side token management, mimicking real API behavior.

### Template Variables & Dynamic Values

The mock server supports powerful template variables for generating realistic, dynamic response data. Templates are processed at request time to provide fresh, realistic data for testing.

#### Available Template Variables

**Core Templates:**
- `{{random_uuid}}` - Generates random UUIDs
- `{{current_timestamp}}` - Current timestamp in ISO 8601 format

**Timestamp Templates (Realistic):**
- `{{timestamp}}` - Recent but not current ISO 8601 timestamp (1-30 minutes ago)
- `{{date}}` - Recent date in YYYY-MM-DD format (1-7 days ago)  
- `{{unix_timestamp}}` - Recent Unix timestamp (10 digits)
- `{{unix_timestamp_ms}}` - Recent Unix timestamp in milliseconds (13 digits)

#### Usage Examples

**Basic Template Usage:**
```json
{
    "response": {
        "status_code": 200,
        "body": {
            "transaction_id": "{{random_uuid}}",
            "timestamp": "{{timestamp}}",
            "created_date": "{{date}}",
            "last_seen": "{{unix_timestamp}}"
        }
    }
}
```

**Realistic Device Data:**
```json
{
    "response": {
        "body": {
            "devices": [
                {
                    "device_id": "router-001", 
                    "status": "online",
                    "last_updated": "{{timestamp}}",
                    "boot_time": "{{unix_timestamp}}",
                    "session_id": "{{random_uuid}}"
                }
            ]
        }
    }
}
```

#### Automatic Timestamp Detection

The server automatically detects and replaces static timestamps in your configuration with realistic recent timestamps:

**Automatic Detection Patterns:**
- ISO 8601: `2025-08-19T10:30:00Z` → Recent realistic timestamp  
- Unix timestamps: `1724058600` → Recent realistic Unix timestamp
- Dates: `2025-08-19` → Recent realistic date

**Example Configuration:**
```json
{
    "response": {
        "body": {
            "devices": [
                {
                    "device_id": "C8K-001",
                    "last_updated": "2025-08-19T10:30:00Z"
                }
            ]
        }
    }
}
```

The static timestamp `2025-08-19T10:30:00Z` will automatically be replaced with a realistic recent timestamp when the response is served.

#### Template Benefits

- **Realistic Testing**: Generate believable mock data that changes over time
- **No Hardcoding**: Eliminate static timestamps that become stale
- **Consistent Behavior**: Templates generate consistent patterns (e.g., always 1-30 minutes ago)
- **Easy Migration**: Existing static timestamps are automatically converted

### Persistence Configuration (Redis)

Enable data persistence for your endpoints by adding persistence configuration:

```json
{
    "method": "POST",
    "path": "/products/{product_id}",
    "authentication": ["api_key"],
    "persistence": {
        "entity_name": "products",
        "action": "create"
    },
    "responses": [
        {
            "body_conditions": null,
            "response": {
                "status_code": 201,
                "body": {
                    "message": "Product created successfully.",
                    "product_id": "{product_id}"
                }
            }
        }
    ]
}
```

**Supported persistence actions:**
- `create`: Store the request body as an entity
- `retrieve`: Get stored entity data  
- `update`: Update existing entity data
- `delete`: Remove entity from storage
- `list`: Get all entities of a given type

**Redis Management Endpoints:**
- `GET /system/cache/info` - Get Redis connection status and statistics
- `DELETE /system/cache/flush` - Clear all cached data
- `GET /system/cache/entities/{entity_name}` - List all entities of a type
- `GET /system/cache/entities/{entity_name}/{entity_id}` - Get specific entity details
- `DELETE /system/cache/entities/{entity_name}/{entity_id}` - Delete specific entity

### System Security Configuration (`api.json`)

The application supports protecting system endpoints with API key authentication using centralized configuration:

```json
{
  "system": {
    "protect_endpoints": true,
    "auth_method": "system_api_key"
  }
}
```

**System Configuration Options:**
- `protect_endpoints`: Enable/disable protection for `/admin/*` and `/system/*` endpoints (cache and logging management)
- `auth_method`: Authentication method to use (must exist in `auth.json`)

**Authentication Configuration (`auth.json`):**
```json
{
  "authentication_methods": {
    "system_api_key": {
      "type": "api_key",
      "name": "X-API-Key",
      "location": "header",
      "description": "System administration API key for protected endpoints",
      "valid_keys": [
        "system-admin-key-123",
        "sysadmin-secret-key-789",
        "admin-system-access-123"
      ]
    }
  }
}
```

**Protected Endpoints:**
- All `/admin/*` endpoints (cache management)
- All `/system/*` endpoints (logging management)

**🔐 Centralized Authentication Integration:**
System endpoints use the same centralized `auth.json` configuration as regular API endpoints, ensuring:
- **Single source of truth** for all authentication configuration
- **Consistent security policies** across all endpoints
- **Unified API key management** 
- **Swagger UI integration** with proper authentication schemes

When protection is enabled, these endpoints require a valid `X-API-Key` header with one of the configured system API keys. The authentication is validated by middleware before reaching the endpoint handlers.

**Using System Endpoints in Swagger UI:**
1. Navigate to http://localhost:8000/docs
2. Click the "Authorize" button 
3. Enter one of the valid system API keys in the `system_api_key` field
4. System endpoints will now be accessible through the Swagger interface

### Logging Configuration (`api.json`)

The application supports comprehensive logging with dual output, request/response tracking, and runtime management:

```json
{
  "logging": {
    "enabled": true,
    "level": "INFO",
    "console_enabled": true,
    "file_enabled": true,
    "file_path": "/app/latest.logs",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "max_file_size_mb": 10,
    "backup_count": 5,
    "max_body_log_size": 2048,
    "request_response_logging": true,
    "allow_log_deletion": true
  }
}
```

**Core Configuration Options:**
- `enabled`: Enable/disable entire logging system
- `level`: Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- `console_enabled`: Enable logging to stdout/stderr
- `file_enabled`: Enable logging to file
- `file_path`: Path where log file will be created (auto-creates if missing)
- `format`: Python logging format string
- `max_file_size_mb`: Maximum log file size before rotation (MB)
- `backup_count`: Number of rotated log files to keep

**Request/Response Logging Options:**
- `request_response_logging`: Enable detailed HTTP request/response logging middleware
- `max_body_log_size`: Maximum size of request/response body to log (characters)

**Security and Management Options:**
- `allow_log_deletion`: Enable/disable log file deletion via API (default: true)

**Multi-Logger Support:**
The system captures logs from all components:
- **Application Logs** (`root`) - Core server logic and business operations
- **HTTP Access Logs** (`uvicorn.access`) - Standard web server access logs
- **Request/Response Logs** (`api.requests`) - Detailed API call tracking with timing
- **Server Logs** (`uvicorn`) - Server startup, shutdown, and system events
- **Framework Logs** (`fastapi`) - FastAPI framework operations

**Log Output Examples:**

*INFO Level (Production):*
```
2025-08-20 10:41:41,097 - root - INFO - Logging configured - Level: INFO, File: /app/latest.logs
2025-08-20 10:41:41,139 - root - INFO - Adding logging management endpoints
2025-08-20 10:42:15,234 - api.requests - INFO - REQUEST: GET /dataservice/device/monitor from 192.168.65.1
2025-08-20 10:42:15,236 - api.requests - INFO - RESPONSE: 401 for GET /dataservice/device/monitor - Time: 0.002s
2025-08-20 10:42:15,237 - uvicorn.access - INFO - 192.168.65.1:22520 - "GET /dataservice/device/monitor HTTP/1.1" 401 Unauthorized
```

*DEBUG Level (Development):*
```
2025-08-20 10:42:15,234 - api.requests - INFO - REQUEST: GET /dataservice/device/monitor from 192.168.65.1
2025-08-20 10:42:15,234 - api.requests - DEBUG - Request Headers: {'host': '0.0.0.0:8000', 'user-agent': 'curl/8.7.1', 'accept': '*/*'}
2025-08-20 10:42:15,235 - root - DEBUG - Checking authentication for endpoint: /dataservice/device/monitor
2025-08-20 10:42:15,235 - root - DEBUG - Authentication methods required: ['vmanage_session', 'csrf_token']
2025-08-20 10:42:15,236 - api.requests - INFO - RESPONSE: 401 for GET /dataservice/device/monitor - Time: 0.002s
2025-08-20 10:42:15,236 - api.requests - DEBUG - Response Headers: {'content-length': '74', 'content-type': 'application/json'}
2025-08-20 10:42:15,236 - api.requests - DEBUG - Response Body: {"error":"Authentication failed","message":"Invalid credentials"}
```

**Logging Management API Endpoints:**
- `GET /system/logging/status` - View current logging configuration and file status (requires system auth)
- `POST /system/logging/config` - Update logging settings at runtime (requires system auth)
- `GET /system/logging/logs?lines=100` - Get recent log entries from file (requires system auth)
- `DELETE /system/logging/logs` - Clear log file (requires `allow_log_deletion: true` and system auth)

**Example: Update logging configuration at runtime:**
```bash
curl -X POST "http://localhost:8000/system/logging/config" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: system-admin-key-123" \
  -d '{
    "level": "DEBUG",
    "file_enabled": true,
    "console_enabled": true,
    "request_response_logging": true,
    "max_body_log_size": 4096,
    "allow_log_deletion": false
  }'
```

**Example: Get recent log entries:**
```bash
curl -X GET "http://localhost:8000/system/logging/logs?lines=50" \
  -H "X-API-Key: system-admin-key-123"
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_lines": 147,
    "returned_lines": 50,
    "logs": [
      "2025-08-20 10:42:15,234 - api.requests - INFO - REQUEST: GET /dataservice/device/monitor from 192.168.65.1",
      "2025-08-20 10:42:15,236 - api.requests - INFO - RESPONSE: 401 for GET /dataservice/device/monitor - Time: 0.002s",
      "2025-08-20 10:42:15,237 - uvicorn.access - INFO - 192.168.65.1:22520 - \"GET /dataservice/device/monitor HTTP/1.1\" 401 Unauthorized"
    ]
  }
}
```

**Example: Clear log file:**
```bash
curl -X DELETE "http://localhost:8000/system/logging/logs" \
  -H "X-API-Key: system-admin-key-123"
```

**Response (when allowed):**
```json
{
  "status": "success",
  "message": "Log file cleared successfully"
}
```

**Response (when disabled):**
```json
{
  "detail": "Log file deletion is disabled in the configuration"
}
```

**Authentication Examples:**

**Unauthenticated request (when protection is enabled):**
```bash
curl -X GET "http://localhost:8000/system/logging/status"
```
**Response:**
```json
{
  "detail": "Missing X-API-Key header for system endpoint"
}
```

**Authenticated request:**
```bash
curl -X GET "http://localhost:8000/system/logging/status" \
  -H "X-API-Key: system-admin-key-123"
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "enabled": true,
    "level": "DEBUG",
    "console_enabled": true,
    "file_enabled": true,
    "allow_log_deletion": true
  }
}
```

### Environment Variables

Configure the application behavior using these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | `localhost` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |
| `REDIS_DB` | `0` | Redis database number |
| `LOG_LEVEL` | `INFO` | Default logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE_PATH` | `/app/latest.logs` | Default log file location |
| `LOG_TO_FILE` | `true` | Enable file logging by default |
| `LOG_TO_CONSOLE` | `true` | Enable console logging by default |
| `LOG_MAX_BODY_SIZE` | `2048` | Maximum request/response body size to log |
| `LOG_REQUEST_RESPONSE` | `true` | Enable detailed request/response logging |
| `LOG_ALLOW_DELETION` | `true` | Allow log file deletion via API |
| `SYSTEM_PROTECT_ENDPOINTS` | `false` | Enable system endpoint protection |
| `SYSTEM_AUTH_METHOD` | `system_api_key` | Authentication method for system endpoints |

**Example .env file:**
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
LOG_LEVEL=DEBUG
LOG_FILE_PATH=/app/debug.logs
LOG_TO_FILE=true
LOG_TO_CONSOLE=true
LOG_MAX_BODY_SIZE=4096
LOG_REQUEST_RESPONSE=true
LOG_ALLOW_DELETION=true
SYSTEM_PROTECT_ENDPOINTS=true
SYSTEM_AUTH_METHOD=system_api_key
```

## 🚀 Usage

### Starting the Server

#### Recommended: Using CLI

**Interactive configuration selection:**
```bash
./mockctl start
# Prompts you to choose: basic, persistence, vmanage
```

**Direct configuration:**
```bash
./mockctl start basic           # Simple REST API
./mockctl start persistence     # API with Redis persistence  
./mockctl start vmanage         # Cisco SD-WAN vManage API
```

**Custom ports:**
```bash
./mockctl start basic --port 8000
./mockctl start vmanage --port 8002
```

#### Alternative: Direct Python Execution

**Development mode (from project root):**
```bash
# Using specific configuration
python run_server.py --host 0.0.0.0 --port 8000 --config-folder configs/basic --reload

# Using vManage configuration
python run_server.py --host 0.0.0.0 --port 8000 --config-folder configs/vmanage --reload
```

**Traditional uvicorn approach (from src directory):**
```bash
# Development mode
cd src
python -m uvicorn main:app --reload --port 8000

# Production mode  
cd src
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Available CLI Options:**
- `--config-folder`: Path to custom configuration folder containing `api.json`, `auth.json`, and `endpoints.json`
- `--host`: Bind socket to this host (default: 127.0.0.1)
- `--port`: Bind socket to this port (default: 8000)
- `--reload`: Enable auto-reload for development
- `--workers`: Number of worker processes (default: 1)
- `--log-level`: Log level (default: info)

#### Shell Scripts for Server Management

For convenient server management, several shell scripts are provided that handle Poetry virtual environments automatically:

**Quick Server Management:**
```bash
# Start server in background with Poetry environment
./mockctl start [config-name]

# Stop all running servers  
./mockctl stop

# List all running servers
./mockctl list

# Test server status and functionality
./test_vmanage_api.sh [port]

# Setup Poetry environment (one-time setup)
./setup_environment.sh
```

**Script Features:**
- **Port Configuration**: Reads port from `.VMANAGE_API_PORT` file (default: 8000)
- **Background Execution**: Servers run in background with process tracking
- **Poetry Integration**: Automatically uses Poetry virtual environment
- **Configuration Validation**: Checks for required config files before starting
- **Process Management**: PID tracking and graceful shutdown

**Example Usage:**
```bash
# Setup environment (first time only)
./setup_environment.sh

# Start with default config selection
./mockctl start
# Output: Interactive config selection menu

# Start with specific config
./mockctl start vmanage
# Output: Server started in background (PID: 12346)

# Test server functionality
./test_vmanage_api.sh
# Output: Comprehensive server status report

# List running servers
./list_servers.sh
# Output: Shows all running servers with PIDs and URLs

# Stop all servers
./stop_vmanage_api.sh
# Output: Gracefully stops all running servers
```

#### Docker Execution

```bash
# Using default config
docker-compose up

# Using volume-mounted custom config
docker run -p 8000:8000 -v /path/to/custom/config:/app/config mock-and-roll
```

Access the server:
- API Base URL: `http://localhost:8000`
- Interactive Documentation: `http://localhost:8000/docs`
- OpenAPI Schema: `http://localhost:8000/openapi.json`

## 📋 API Examples

### 1. Public Endpoint (No Authentication)

**Request:**
```bash
curl -X GET "http://localhost:8000/public/health"
```

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-08-11T00:00:00Z"
}
```


### 2. API Key Authentication

**Valid Request:**
```bash
curl -X GET "http://localhost:8000/items/123" \
  -H "X-API-Key: demo-api-key-123"
```

**Response:**
```json
{
  "message": "Here is the item you requested.",
  "item_id": "123",
  "data": {
    "name": "A Mocked Item",
    "value": 123
  }
}
```

**Invalid Request (Missing or Wrong API Key):**
```bash
curl -X GET "http://localhost:8000/items/123"
```

**Response:**
```json
{
  "detail": "Authentication failed. Required methods: api_key. Errors: Invalid API key"
}
```


### 3. HTTP Basic Authentication

**Valid Request:**
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -u "admin:secret123" \
  -d '{"role": "admin", "action": "create"}'
```

**Response:**
```json
{
    "message": "Admin user created successfully.",
    "user_id": 999
}
```

**Valid Request (Other Credentials):**
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -u "guest:guest123" \
  -d '{"role": "guest"}'
```

**Response:**
```json
{
    "message": "Guest user created with limited permissions.",
    "user_id": 100
}
```

**Invalid Request (Wrong Credentials):**
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -u "admin:wrongpassword" \
  -d '{"role": "admin", "action": "create"}'
```

**Response:**
```json
{
    "detail": "Authentication failed. Required methods: basic_auth, oidc_auth_code. Errors: Invalid credentials"
}
```


### 4. Bearer Token (OIDC) Authentication

**Valid Request:**
```bash
curl -X GET "http://localhost:8000/user/settings" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.demo-token"
```

**Response:**
```json
{
  "settings": {
    "max_users": 1000,
    "feature_flags": {
      "new_ui": true,
      "beta_features": false
    }
  }
}
```

### 5. Session Authentication

Session authentication uses cookies for authentication, which is common in web applications. This mock server supports session authentication via `JSESSIONID` cookies.

**Valid Request with Session Cookie:**
```bash
curl -X GET "http://localhost:8000/dataservice/device" \
  -H "Cookie: JSESSIONID=C4AC92C3F40C2B9A2DE9C2839FB45"
```

**Response:**
```json
{
  "data": [
    {
      "deviceId": "CSR1000V-001",
      "hostname": "CSR1000V-001",
      "deviceType": "vedge",
      "deviceModel": "CSR1000V"
    }
  ]
}
```

**Using Session Authentication in Swagger UI:**

Since Swagger UI doesn't automatically handle `Set-Cookie` responses, you need to manually provide the session cookie:

1. In Swagger UI, click the "Authorize" button (🔒)
2. In the "session_cookie (apiKey)" section, enter the session ID:
   - **Value:** `JSESSIONID=C4AC92C3F40C2B9A2DE9C2839FB45` (full cookie format)
   - **Or:** `C4AC92C3F40C2B9A2DE9C2839FB45` (just the session ID)

**Using CSRF Token Authentication in Swagger UI:**

Many vManage endpoints require a CSRF token (X-XSRF-TOKEN header) for security:

1. In Swagger UI, click the "Authorize" button (🔒)
2. In the "csrf_token (apiKey)" section, enter the CSRF token:
   - **Value:** `mock-csrf-token-456`

**Note:** For endpoints that require both session and CSRF token authentication, you need to provide both tokens in Swagger UI.

**Using CSRF Token with Session:**
```bash
curl -X GET "http://localhost:8000/dataservice/device/monitor" \
  -H "Cookie: JSESSIONID=vmanage-session-123" \
  -H "X-XSRF-TOKEN: mock-csrf-token-456"
```

**Response:**
```json
{
  "data": [
    {
      "device_id": "C8K-001",
      "hostname": "vEdge-C8K-001",
      "device_type": "vedge",
      "device_model": "vedge-C8000V",
      "status": "normal"
    }
  ]
}
```

**CSRF Token Only Authentication:**
```bash
curl -X GET "http://localhost:8000/dataservice/device/monitor" \
  -H "X-XSRF-TOKEN: mock-csrf-token-456"
```

**Invalid Session Example:**
```bash
curl -X GET "http://localhost:8000/dataservice/device" \
  -H "Cookie: JSESSIONID=invalid-session"
```

**Response:**
```json
{
  "detail": "Authentication failed. Required methods: vmanage_session. Errors: Invalid session cookie"
}
```

### 6. Conditional Responses

**Request with Admin Role:**
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -u "admin:secret123" \
  -d '{"role": "admin", "action": "create"}'
```

**Response:**
```json
{
    "message": "Admin user created successfully.",
    "user_id": 999
}
```

**Request with Guest Role:**
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -u "admin:secret123" \
  -d '{"role": "guest"}'
```

**Response:**
```json
{
    "message": "Guest user created with limited permissions.",
    "user_id": 100
}
```


### 7. OAuth2 Token Exchange

**Authorization Code Grant (Default Configuration):**
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "authorization_code",
    "client_id": "demo-client-id",
    "code": "auth-code-here"
  }'
```

**Response:**
```json
{
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.demo-token",
    "token_type": "Bearer",
    "expires_in": 3600,
    "scope": "read write"
}
```

### 8. Error Responses

**400 Bad Request (Invalid JSON):**
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -u "admin:secret123" \
  -d '{"invalid": json}'
```

**Response:**
```json
{
    "error": "Invalid JSON in request body."
}
```

**401 Unauthorized:**
```bash
curl -X GET "http://localhost:8000/items/123"
```

**Response:**
```json
{
    "detail": "Authentication failed. Required methods: api_key. Errors: "
}
```

**422 Validation Error (Missing Path Parameter):**
```bash
curl -X GET "http://localhost:8000/items/"
```

**Response:**
```json
{
    "detail": [
        {
            "loc": ["path", "item_id"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

### 9. Redis Persistence Examples


**Create a Product (with persistence):**
```bash
curl -X POST "http://localhost:8000/products/123" \
  -H "X-API-Key: test-key-456" \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "price": 999.99, "category": "electronics"}'
```

**Response:**
```json
{
    "message": "Product created successfully.",
    "product_id": "123",
    "created_at": "2025-01-11T10:30:00Z"
}
```

**Retrieve a Cached Product:**
```bash
curl -X GET "http://localhost:8000/products/123" \
  -H "X-API-Key: test-api-key-123"
```

**Response:**
```json
{
    "product_id": "123",
    "name": "Mock Product",
    "price": 29.99,
    "retrieved_from_cache": true
}
```

**List All Products:**
```bash
curl -X GET "http://localhost:8000/products" \
  -H "X-API-Key: test-api-key-123"
```

**Response:**
```json
{
    "products": [],
    "total_count": 0,
    "cached_results": true
}
```

**Check Redis Cache Status:**
```bash
curl -X GET "http://localhost:8000/system/cache/info" \
  -H "X-API-Key: system-admin-key-123"
```

**Response:**
```json
{
    "status": "connected",
    "keys": 5,
    "memory_used": "1.2MB",
    "connected_clients": 1,
    "uptime": 3600
}
```

### 10. vManage API Example (Dynamic Authentication)

**Running with vManage Configuration:**
```bash
# Start server with vManage API configuration
python run_server.py --host 0.0.0.0 --port 8000 --config-folder tests/configs/vmanage-api --reload

# Or using traditional uvicorn (requires manual config management)
MOCK_CONFIG_FOLDER=tests/configs/vmanage-api python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

This example demonstrates the complete vManage SD-WAN API authentication flow using dynamic authentication values. The vManage configuration organizes endpoints into logical groups:
- **Authentication** - Login, logout, and CSRF token management  
- **Devices** - Device monitoring and management operations
- **Templates** - Configuration templates and policy management

**Step 1: Login and Get Session Cookie**
```bash
curl -X POST "http://localhost:8000/j_security_check" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "j_username=admin&j_password=admin" \
  -i
```

**Response:**
```http
HTTP/1.1 200 OK
Set-Cookie: JSESSIONID=vmanage-session-789; Path=/; HttpOnly
Content-Type: text/html

{"message":"Authentication successful","redirect":"/dataservice/client/token"}
```

**Step 2: Get CSRF Token**
```bash
curl -X GET "http://localhost:8000/dataservice/client/token" \
  -H "Cookie: JSESSIONID=vmanage-session-789" \
  -i
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: text/plain
X-XSRF-TOKEN: mock-csrf-token-abc

"mock-csrf-token-abc"
```

**Step 3: Access Protected Endpoints**
```bash
curl -X GET "http://localhost:8000/dataservice/device/monitor" \
  -H "Cookie: JSESSIONID=vmanage-session-789" \
  -H "X-XSRF-TOKEN: mock-csrf-token-abc" \
  -i
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-XSRF-TOKEN: mock-csrf-token-abc

{
  "data": [
    {
      "device_id": "C8K-001",
      "hostname": "vEdge-C8K-001",
      "device_type": "vedge",
      "device_model": "vedge-C8000V",
      "status": "normal",
      "system_ip": "1.1.1.1",
      "site_id": "100",
      "version": "20.6.3",
      "uptime": "15:23:45:10",
      "last_updated": "2025-08-19T10:30:00Z"
    }
  ]
}
```

**Step 4: Create Device Template with CSRF Protection**
```bash
curl -X POST "http://localhost:8000/dataservice/template/device" \
  -H "Cookie: JSESSIONID=vmanage-session-789" \
  -H "X-XSRF-TOKEN: mock-csrf-token-abc" \
  -H "Content-Type: application/json" \
  -d '{
    "templateName": "Branch-Router-Template",
    "deviceType": "vedge-C8000V",
    "templateDefinition": {
      "system": {
        "host-name": "{{hostname}}",
        "system-ip": "{{system_ip}}",
        "site-id": "{{site_id}}"
      }
    }
  }' \
  -i
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json
X-XSRF-TOKEN: mock-csrf-token-abc

{
  "templateId": "template-12345",
  "templateName": "Branch-Router-Template",
  "status": "created",
  "message": "Device template created successfully"
}
```

**Key Features Demonstrated:**

1. **Dynamic Session Management**: Each login generates a random session ID from `auth.json`
2. **CSRF Token Correlation**: CSRF tokens are automatically correlated with session IDs
3. **Multi-Factor Authentication**: Endpoints require both session cookie AND CSRF token
4. **Automatic Token Rotation**: Fresh CSRF tokens included in response headers
5. **Real API Behavior**: Mimics actual vManage authentication patterns

**Authentication Test Suite:**

Run the comprehensive authentication test suite:
```bash
./tests/configs/vmanage-api/test_vmanage_auth.sh
```

This test suite validates:
- 19 different authentication scenarios
- Session and CSRF token validation
- Multi-factor authentication enforcement
- Login/logout flows
- Dynamic value resolution

### 11. Logging Management Examples

**Get comprehensive logging status:**
```bash
curl -X GET "http://localhost:8000/system/logging/status"
```

**Response:**
```json
{
  "enabled": true,
  "level": "INFO",
  "console_enabled": true,
  "file_enabled": true,
  "file_path": "/app/latest.logs",
  "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  "max_file_size_mb": 10,
  "backup_count": 5,
  "max_body_log_size": 2048,
  "request_response_logging": true,
  "allow_log_deletion": true,
  "file_exists": true,
  "file_size_bytes": 15420,
  "file_size_mb": 0.01
}
```

**Enable DEBUG mode with detailed request/response logging:**
```bash
curl -X POST "http://localhost:8000/system/logging/config" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "DEBUG",
    "console_enabled": true,
    "file_enabled": true,
    "request_response_logging": true,
    "max_body_log_size": 4096,
    "allow_log_deletion": false
  }'
```

**Response:**
```json
{
  "message": "Logging configuration updated successfully",
  "new_config": {
    "enabled": true,
    "level": "DEBUG",
    "console_enabled": true,
    "file_enabled": true,
    "request_response_logging": true,
    "max_body_log_size": 4096,
    "allow_log_deletion": false
  }
}
```

**View recent logs with all API calls captured:**
```bash
curl -X GET "http://localhost:8000/system/logging/logs?lines=20"
```

**Response showing comprehensive logging:**
```json
{
  "status": "success",
  "data": {
    "total_lines": 147,
    "returned_lines": 20,
    "logs": [
      "2025-08-20 10:42:15,234 - api.requests - INFO - REQUEST: POST /j_security_check from 192.168.65.1",
      "2025-08-20 10:42:15,234 - api.requests - DEBUG - Request Headers: {'content-type': 'application/x-www-form-urlencoded', 'content-length': '36'}",
      "2025-08-20 10:42:15,235 - api.requests - DEBUG - Request Body: j_username=admin&j_password=admin123",
      "2025-08-20 10:42:15,235 - root - INFO - Form handler called for /j_security_check with username: admin",
      "2025-08-20 10:42:15,236 - api.requests - INFO - RESPONSE: 200 for POST /j_security_check - Time: 0.002s",
      "2025-08-20 10:42:15,236 - api.requests - DEBUG - Response Headers: {'content-type': 'application/json', 'set-cookie': 'JSESSIONID=vmanage-session-123; Path=/; HttpOnly'}",
      "2025-08-20 10:42:15,236 - api.requests - DEBUG - Response Body: {\"message\": \"Authentication successful\"}",
      "2025-08-20 10:42:15,237 - uvicorn.access - INFO - 192.168.65.1:22520 - \"POST /j_security_check HTTP/1.1\" 200 OK",
      "2025-08-20 10:42:18,445 - api.requests - INFO - REQUEST: GET /dataservice/device/monitor from 192.168.65.1",
      "2025-08-20 10:42:18,445 - api.requests - DEBUG - Request Headers: {'cookie': 'JSESSIONID=vmanage-session-123', 'x-xsrf-token': 'mock-csrf-token-456'}",
      "2025-08-20 10:42:18,446 - root - DEBUG - Checking authentication for endpoint: /dataservice/device/monitor",
      "2025-08-20 10:42:18,446 - root - DEBUG - Authentication methods required: ['vmanage_session', 'csrf_token']",
      "2025-08-20 10:42:18,447 - root - DEBUG - Session authentication successful for user: admin",
      "2025-08-20 10:42:18,447 - api.requests - INFO - RESPONSE: 200 for GET /dataservice/device/monitor - Time: 0.002s",
      "2025-08-20 10:42:18,447 - api.requests - DEBUG - Response Body: {\"data\": [{\"device_id\": \"C8K-001\", \"hostname\": \"vEdge-C8K-001\"}]}",
      "2025-08-20 10:42:18,448 - uvicorn.access - INFO - 192.168.65.1:44316 - \"GET /dataservice/device/monitor HTTP/1.1\" 200 OK"
    ]
  }
}
```

**Production mode (INFO level) for cleaner logs:**
```bash
curl -X POST "http://localhost:8000/system/logging/config" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "INFO",
    "console_enabled": false,
    "file_enabled": true,
    "request_response_logging": true,
    "allow_log_deletion": true
  }'
```

**Key Features Demonstrated:**
- **Multi-Logger Capture**: All HTTP requests, server events, and application logs in one file
- **Request/Response Middleware**: Complete HTTP call tracking with timing information
- **Debug vs Production**: Configurable verbosity levels for different environments
- **Body Content Logging**: Request/response payloads captured (configurable size limits)
- **Authentication Tracking**: Detailed auth flow logging for debugging security issues
- **Runtime Configuration**: Change settings without server restart
- **File Management**: Automatic creation, rotation, and size management

## 🗺️ Roadmap

### Recent Updates ✨
- **Centralized System Authentication**: System endpoints now use the same `auth.json` configuration as regular API endpoints for consistent security management
- **System Namespace Consistency**: Cache management endpoints remain in `/system/cache/*` namespace for consistent system operations organization  
- **Custom Configuration Folder Support**: Added `--config-folder` CLI argument to specify custom configuration directory
- **Enhanced Server Runner**: New `run_server.py` script with comprehensive CLI argument support for native Python execution
- **Configuration Priority System**: Hierarchical config loading (CLI > ENV > Docker > Default) for flexible deployment options
- **Environment-Specific Configurations**: Easy switching between different API configurations (e.g., vManage, custom APIs)  
- **Enhanced Swagger Integration**: System endpoints now properly display authentication requirements in Swagger UI
- **Improved Security Consistency**: Single source of truth for all authentication configuration across the application

### Version 0.1.0 - Persistence Layer ✅
- **Redis Integration**: Store and retrieve entity data using Redis
- **Cache Management**: System endpoints for cache inspection and management
- **Entity Operations**: CRUD operations with automatic caching
- **Data Persistence**: Maintain data across server restarts

### Version 0.2.0 - Advanced Authentication Features ✅
- **Multi-Factor Authentication**: Support for additional authentication factors (e.g., TOTP)
- **OAuth 2.0 Support**: Integration with external OAuth providers
- **API Key Management**: Generate and revoke API keys for users
- **Session Management**: Fine-grained control over user sessions

### Version 0.3.0 - Advanced Workflows 📋
- **Request Sequencing**: Chain multiple requests with state management
- **Response Templates**: Jinja2 templating for dynamic response generation
- **Data Fixtures**: Pre-populated datasets for complex scenarios
- **Request Recording**: Capture and replay real API interactions

## 🧪 Development

### 🧪 Running Tests
```bash
# Install test dependencies
poetry install --with test

# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run tests with verbose output
pytest -v

# Test template functionality
python test_templates.py
```

### 🧪 Testing Template Functionality
You can test the template system using the included test script:

```bash
# Test timestamp templates and substitution
python test_templates.py
```

This will show examples of:
- Static timestamp replacement with realistic values
- Template placeholder processing (`{{timestamp}}`, `{{date}}`, etc.)
- Automatic detection and conversion of various timestamp formats

**Sample output:**
```
Testing timestamp template substitution...
Original data:
{'device': {'last_updated': '2025-08-19T10:30:00Z', 'timestamp': '1724058600'}}

Processed data:  
{'device': {'last_updated': '2025-08-20T14:23:15Z', 'timestamp': '1724074995'}}
```

### 🎨 Code Formatting
The project uses Black for code formatting:
```bash
# Format all code
black src/ tests/

# Check formatting without making changes
black --check src/

# Format with line length limit
black --line-length 88 src/
```

### 🔍 Code Quality
```bash
# Run linting with flake8
flake8 src/

# Type checking with mypy
mypy src/

# Security scanning with bandit
bandit -r src/
```

### 🔧 Development Commands
```bash
# Start development server with auto-reload
python -m uvicorn src.main:app --reload --port 8000

# Start with debug logging
LOG_LEVEL=DEBUG python -m uvicorn src.main:app --reload

# Run with different port
python -m uvicorn src.main:app --reload --port 8001

# Check Redis connection
redis-cli ping

# Monitor Redis operations
redis-cli monitor
```

### 💻 VS Code Setup
The project includes VS Code configuration for:
- Auto-formatting on save with Black
- Python environment detection
- Debugging configuration

## 🐳 Docker Usage

### Development
```bash
# Build and run all services (API + Redis)
docker-compose up --build

# Run in background
docker-compose up -d

# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f mock-api
docker-compose logs -f redis

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

**Access URLs after starting:**
- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Redis**: localhost:6379

### Production
```bash
# Build production image
docker build -t mock-api-server .

# Run production container with Redis link
docker run -d --name redis redis:8.0.0
docker run -d -p 8000:8000 --link redis:redis \
  -e REDIS_HOST=redis \
  -e REDIS_PORT=6379 \
  -e LOG_LEVEL=INFO \
  mock-api-server
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔧 Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Kill existing processes
pkill -f "uvicorn"

# Or use a different port
python -m uvicorn main:app --port 8001
```

**Configuration Not Loading:**
- Ensure JSON files are valid (use `jq . configs/basic/endpoints.json` to validate)
- Check that the configuration exists in the `configs/` directory
- Verify file permissions

**Authentication Not Working:**
- Check that valid credentials are configured in `auth.json`
- Ensure the correct authentication method is specified in endpoints
- Verify headers are properly formatted

**Docker Issues:**
```bash
# Rebuild containers
docker-compose down
docker-compose up --build

# Check logs
docker-compose logs mock-api-server
```

**Script Issues on macOS:**
All scripts are now compatible with macOS bash 3.x:
- **Working Directory Resolution**: Scripts automatically navigate to project root
- **Cross-Directory Execution**: Works from any directory location
- **Bash 3.x Compatibility**: No associative arrays dependency
- **Relative Path Handling**: All configuration and resource paths resolve correctly

```bash
# Python CLI works from project root
./mockctl start vmanage

# Direct Python CLI usage
python src/cli/mockctl.py start vmanage

# Simple unified interface
./mockctl start
```

**Success Report Not Finding Requests:**
- Ensure the server has processed some requests before running the report
- Use `--lines` parameter to increase log analysis scope
- Check that the server is using the expected log format
- Verify the success status codes match your expectations (default: 200,201,202,204)

For more help, please open an issue on the repository.

---

## 📚 Additional Resources

### 📖 Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redis Documentation](https://redis.io/documentation)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Poetry Documentation](https://python-poetry.org/docs/)

### 🔗 Related Projects
- [FastAPI](https://github.com/tiangolo/fastapi) - Modern web framework for building APIs
- [Redis](https://github.com/redis/redis) - In-memory data structure store
- [Swagger UI](https://swagger.io/tools/swagger-ui/) - API documentation interface

### 💡 Use Cases
- **API Prototyping**: Quickly mock third-party APIs during development
- **Testing**: Create predictable responses for integration tests
- **Development**: Develop frontend applications without backend dependencies
- **Training**: Learn API concepts with hands-on examples

---

**⭐ Star this repository if you find it useful!**
