
# REST API Mock Server

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![Redis](https://img.shields.io/badge/Redis-5.0+-red.svg)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Table of Contents

- [Quick Start](#-quick-start)
- [Scripts & Tools](#-scripts--tools)
  - [Available Scripts](#available-scripts)
  - [Usage Options](#usage-options)
  - [Script Categories](#script-categories)
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
  - [Configuration Folder Options](#configuration-folder-options)
  - [Endpoint Configuration](#endpoint-configuration-srcconfigendpointsjson)
  - [Authentication Configuration](#authentication-configuration-srcconfigauthjson)
  - [Template Variables & Dynamic Values](#template-variables--dynamic-values)
  - [Persistence Configuration](#persistence-configuration-redis)
  - [Logging Configuration](#logging-configuration-srcconfigapijson)
  - [Environment Variables](#environment-variables)
- [Usage](#-usage)
  - [Starting the Server](#starting-the-server)
- [API Examples](#-api-examples)
  - [Public Endpoint (No Authentication)](#1-public-endpoint-no-authentication)
  - [API Key Authentication](#2-api-key-authentication)
  - [HTTP Basic Authentication](#3-http-basic-authentication)
  - [Bearer Token (OIDC) Authentication](#4-bearer-token-oidc-authentication)
  - [Session Authentication](#5-session-authentication)
  - [Conditional Responses](#6-conditional-responses)
  - [OAuth2 Token Exchange](#7-oauth2-token-exchange)
  - [Error Responses](#8-error-responses)
  - [Redis Persistence Examples](#9-redis-persistence-examples)
  - [vManage API Example (Dynamic Authentication)](#10-vmanage-api-example-dynamic-authentication)
  - [Logging Management Examples](#11-logging-management-examples)
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
cd mock-and-roll

# Install with Poetry
poetry install && poetry shell

# Start the server (interactive configuration selection)
./run.sh start

# Or start with a specific configuration
./run.sh start basic           # Simple REST API
./run.sh start vmanage         # SD-WAN vManage API mock
./run.sh start persistence     # API with Redis persistence
```

**🎉 That's it!** Your mock API server is now running at:
- **API Base URL**: http://localhost:8001 (default)
- **Interactive Docs**: http://localhost:8001/docs
- **OpenAPI Schema**: http://localhost:8001/openapi.json

### 🎯 Simple Management Commands

```bash
# Start any configuration
./run.sh start                    # Interactive selection
./run.sh start basic --port 8000  # Basic config on custom port

# Manage servers
./run.sh list                     # See what's running
./run.sh stop                     # Stop servers (auto-detect)
./run.sh stop --all               # Stop everything

# Monitor activity
./run.sh logs                     # Recent logs
./run.sh success detailed         # Success analysis

# Get help
./run.sh help                     # All available scripts
./run.sh config-help              # Configuration guide
```

### 📂 Available Configurations

- **basic**: Simple REST API with 1 endpoint
- **persistence**: API with Redis caching (12 endpoints)  
- **vmanage**: Cisco SD-WAN vManage API simulation (many endpoints)

See [SCRIPTS.md](SCRIPTS.md) for complete script documentation.

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

**Endpoint config (`src/config/endpoints.json`):**
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

