
# REST API Mock Server

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![Redis](https://img.shields.io/badge/Redis-5.0+-red.svg)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Table of Contents

- [Quick Start](#-quick-start)
- [Features](#-features)
  - [Core Functionality](#-core-functionality)
  - [Authentication & Security](#-authentication--security)
  - [Developer Experience](#-developer-experience)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
  - [Prerequisites](#prerequisites)
  - [Using Poetry (Recommended)](#using-poetry-recommended)
  - [Using pip](#using-pip)
  - [Using Docker](#using-docker)
- [Configuration](#-configuration)
  - [Endpoint Configuration](#endpoint-configuration-srcconfigendpointsjson)
  - [Authentication Configuration](#authentication-configuration-srcconfigauthjson)
  - [Persistence Configuration](#persistence-configuration-redis)
  - [Environment Variables](#environment-variables)
- [Usage](#-usage)
  - [Starting the Server](#starting-the-server)
- [API Examples](#-api-examples)
  - [Public Endpoint (No Authentication)](#1-public-endpoint-no-authentication)
  - [API Key Authentication](#2-api-key-authentication)
  - [HTTP Basic Authentication](#3-http-basic-authentication)
  - [Bearer Token (OIDC) Authentication](#4-bearer-token-oidc-authentication)
  - [Conditional Responses](#5-conditional-responses)
  - [OAuth2 Token Exchange](#6-oauth2-token-exchange)
  - [Error Responses](#7-error-responses)
  - [Redis Persistence Examples](#8-redis-persistence-examples)
- [Roadmap](#-roadmap)
- [Development](#-development)
  - [Running Tests](#-running-tests)
  - [Code Formatting](#-code-formatting)
  - [Code Quality](#-code-quality)
  - [Development Commands](#-development-commands)
  - [VS Code Setup](#-vs-code-setup)
- [Docker Usage](#-docker-usage)
  - [Development](#development)
  - [Production](#production)
- [Contributing](#-contributing)
- [License](#-license)
- [Troubleshooting](#-troubleshooting)
  - [Common Issues](#common-issues)



## 🚀 Quick Start

Get up and running in under 2 minutes:

```bash
# Clone and setup
git clone <repository-url>
cd mock-api

# Install with Poetry
poetry install && poetry shell

# Ajust the configuration to Mock your own API
edit src/config/endpoints.json
edit src/config/auth.json
# >>> See below for example endpoints configs <<<

# Start the server
python -m uvicorn src.main:app --reload --port 8000
```


**🎉 That's it!** Your mock API server is now running at:
- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json


### Example: Create a Product with Persistence

**Endpoint config (`src/config/endpoints.json`):**
```json
{
  "endpoints": [
    {
            "method": "POST",
            "path": "/products",
            "authentication": [
                "api_key"
            ],
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
                "required": [
                    "name",
                    "price"
                ]
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
            "authentication": [
                "api_key"
            ],
            "persistence": {
                "entity_name": "products",
                "action": "retrieve"
            }
        },
  ]
}
```

**Auth config (`src/config/auth.json`):**
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

## 🚀 Features


### Core Functionality
- **Dynamic Endpoint Configuration**: Create REST endpoints through JSON config files (`src/config/endpoints.json`)
- **Path Parameter Support**: Dynamic URL parameters with automatic substitution in responses
- **Conditional Responses**: Different responses based on request body conditions (see `/users` endpoint)
- **Request Body Validation**: Support for JSON request bodies with condition matching
- **Redis Persistence**: Optional data persistence layer with Redis for entity storage and retrieval
- **Admin/Cache Endpoints**: Inspect and manage Redis cache via `/admin/cache/*` endpoints

### Authentication & Security
- **Multiple Authentication Methods**: API Key, HTTP Basic Auth, and OIDC (OAuth2)
- **Flexible Authentication**: Multiple auth methods per endpoint with OR logic
- **OpenAPI Integration**: Full Swagger UI support with security scheme visualization
- **Grant Type Support**: Authorization Code flow for OIDC (see config)

### Developer Experience
- **Interactive Documentation**: Auto-generated Swagger UI at `/docs`
- **Hot Reloading**: Development mode with automatic code reloading
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Docker Support**: Ready-to-use Docker configuration with Redis
- **Cache Management**: Admin endpoints for Redis cache inspection and management

## 📁 Project Structure

```
mock-api/
├── src/                          # Main application source
│   ├── main.py                   # FastAPI application and core logic
│   ├── config/                   # Configuration files
│   │   ├── endpoints.json        # Endpoint definitions and responses
│   │   └── auth.json            # Authentication configuration
│   └── __init__.py
├── .vscode/                      # VS Code configuration
│   └── settings.json            # Python formatting settings (Black)
├── Dockerfile                    # Docker container configuration
├── docker-compose.yml           # Multi-service orchestration
├── pyproject.toml               # Python dependencies and project metadata
└── README.md                    # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.12+
- Poetry (recommended) or pip

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd mock-api

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Using pip

```bash
# Clone the repository
git clone <repository-url>
cd mock-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn
```

### Using Docker

```bash
# Clone the repository
git clone <repository-url>
cd mock-api

# Build and run with Docker Compose
docker-compose up --build
```

## ⚙️ Configuration

### Endpoint Configuration (`src/config/endpoints.json`)

Define your mock endpoints with this structure:

```json
{
    "endpoints": [
        {
            "method": "GET|POST|PUT|DELETE|PATCH",
            "path": "/your/path/{parameter}",
            "authentication": ["api_key", "basic_auth", "oidc_auth_code"],
            "required_scopes": ["read", "write"],
            "responses": [
                {
                    "body_conditions": {
                        "key": "value"
                    },
                    "response": {
                        "status_code": 200,
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

### Authentication Configuration (`src/config/auth.json`)

Configure authentication methods:

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
        }
    }
}
```

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
- `GET /admin/cache/info` - Get Redis connection status and statistics
- `DELETE /admin/cache/flush` - Clear all cached data
- `GET /admin/cache/entities/{entity_name}` - List all entities of a type
- `DELETE /admin/cache/entities/{entity_name}/{entity_id}` - Delete specific entity

### Environment Variables

Configure the application behavior using these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | `localhost` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |
| `REDIS_DB` | `0` | Redis database number |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

**Example .env file:**
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
LOG_LEVEL=DEBUG
```

## 🚀 Usage

### Starting the Server

```bash
# Development mode (from src directory)
cd src
python -m uvicorn main:app --reload --port 8000

# Production mode
cd src
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Docker
docker-compose up
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
curl -X GET "http://localhost:8000/admin/settings" \
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

### 5. Conditional Responses

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


### 6. OAuth2 Token Exchange

**Authorization Code Grant:**
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

### 7. Error Responses

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

### 8. Redis Persistence Examples


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
curl -X GET "http://localhost:8000/admin/cache/info"
```

**Response:**
```json
{
    "redis_connected": true,
    "total_keys": 5,
    "memory_usage": "1.2MB",
    "uptime_seconds": 3600
}
```

## 🗺️ Roadmap

### Version 0.2.0 - Persistence Layer ✅
- **Redis Integration**: Store and retrieve entity data using Redis
- **Cache Management**: Admin endpoints for cache inspection and management
- **Entity Operations**: CRUD operations with automatic caching
- **Data Persistence**: Maintain data across server restarts

### Version 0.3.0 - Advanced Workflows
- **Database Integration**: SQLite/PostgreSQL support for storing configurations
- **Dynamic Configuration**: Runtime configuration updates via API
- **Configuration Versioning**: Track and rollback configuration changes
- **Backup/Restore**: Export and import configurations

### Version 0.3.0 - Advanced Workflows
- **Request Sequencing**: Chain multiple requests with state management
- **Response Templates**: Jinja2 templating for dynamic response generation
- **Data Fixtures**: Pre-populated datasets for complex scenarios
- **Request Recording**: Capture and replay real API interactions

### Version 0.4.0 - Enhanced Features
- **Rate Limiting**: Per-endpoint and per-user rate limiting
- **Request Validation**: JSON Schema validation for request bodies
- **Response Transformation**: Modify responses based on request headers
- **Webhook Support**: Trigger external webhooks on specific requests

### Version 0.5.0 - Production Features
- **Metrics & Analytics**: Request/response metrics and analytics dashboard
- **Load Testing**: Built-in load testing capabilities
- **Multi-tenancy**: Support for multiple isolated environments
- **Plugin System**: Custom middleware and extension support

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
- Ensure JSON files are valid (use `jq . config/endpoints.json` to validate)
- Check file paths are correct relative to the `src` directory
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
