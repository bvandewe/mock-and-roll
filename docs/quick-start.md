# Getting Started with Mock-and-Roll

Get up and running with Mock-and-Roll's highly configurable REST API server in just a few minutes!

## Prerequisites

- Python 3.11+
- Git
- Redis (optional - for persistence features)

## 🚀 Quick Installation

### Option 1: Using Setup Script (Recommended)

```bash
# Clone the repository
git clone https://github.com/bvandewe/mock-and-roll.git
cd mock-and-roll

# Run the setup script (Alpine Linux / minimal environments)
./setup/alpine_minimal.sh

# For other platforms, see our installation guide
```

### Option 2: Manual Setup

```bash
# Clone and enter directory
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Make CLI executable
chmod +x mockctl
```

**That's it!** 🎉 Your mock API server is ready. Access Swagger UI at `http://localhost:8000/docs`

## 🎯 Your First Mock API

### Start with a Pre-configured Profile

Mock-and-Roll includes several ready-to-use configurations:

```bash
# Interactive selection (recommended for first time)
./mockctl start

# Or start a specific configuration directly
./mockctl start basic --port 8000
```

### Test Your API

```bash
# Test the health endpoint
curl http://localhost:8000/api/v1/health

# Test with authentication (using API key from config)
curl -H "X-API-Key: demo-api-key-123" \
     http://localhost:8000/api/v1/items/123
```

### Explore Swagger Documentation

Open your browser and navigate to `http://localhost:8000/docs` to:

- View all available endpoints
- Test authentication methods
- Try out API calls interactively
- View request/response schemas

## 📋 Available Configuration Profiles

Mock-and-Roll comes with four pre-built profiles to get you started:

### Basic Profile

Simple REST API with minimal setup - perfect for development and testing.

**Features:**

- API key authentication
- Static JSON responses
- Path parameter support
- No external dependencies

```bash
./mockctl start basic
```

### Persistence Profile

Full-featured API with Redis-backed data persistence.

**Features:**

- Multiple authentication methods (API key, Basic Auth, OIDC)
- CRUD operations with real data storage
- Conditional responses based on request content
- User management endpoints

```bash
# Requires Redis server
./mockctl start persistence
```

### vManage Profile

Cisco SD-WAN vManage API simulation for network automation testing.

**Features:**

- Multi-factor authentication workflows
- Network device management
- 25+ realistic endpoints
- Template variables and dynamic responses

```bash
./mockctl start vmanage
```

### Airgapped Profile

Offline-capable API for environments without internet access.

**Features:**

- No CDN dependencies
- Local Swagger UI assets
- Air-gapped deployment ready
- Security-focused configuration

```bash
./mockctl start airgapped
```

## 🔧 Creating Your Custom API Configuration

### Step 1: Copy a Base Configuration

```bash
# Create your custom config directory
cp -r configs/basic configs/myapi

# Navigate to your new config
cd configs/myapi
```

### Step 2: Configure API Metadata (`api.json`)

```json
{
  "api_name": "My Custom API",
  "version": "1.0.0",
  "description": "Custom mock API for my project",
  "base_url": "https://api.mycompany.com",
  "root_path": "/api/v1",
  "openapi_tags": [
    {
      "name": "Users",
      "description": "User management operations"
    }
  ],
  "system": {
    "authentication": ["system_api_key"],
    "endpoints": ["system_health"]
  }
}
```

### Step 3: Set Up Authentication (`auth.json`)

```json
{
  "authentication_methods": {
    "api_key": {
      "type": "api_key",
      "name": "X-API-Key",
      "location": "header",
      "valid_keys": ["my-secret-key-123", "another-key-456"]
    },
    "bearer_token": {
      "type": "http_bearer",
      "valid_tokens": ["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.demo-token"]
    },
    "system_api_key": {
      "type": "api_key",
      "name": "X-System-Key",
      "location": "header",
      "valid_keys": ["system-admin-key"]
    }
  }
}
```

### Step 4: Define Your Endpoints (`endpoints.json`)

```json
{
  "endpoints": [
    {
      "method": "GET",
      "path": "/users/{user_id}",
      "tag": "Users",
      "authentication": ["api_key"],
      "description": "Get user by ID",
      "parameters": {
        "user_id": {
          "type": "string",
          "description": "Unique user identifier"
        }
      },
      "responses": [
        {
          "response": {
            "status_code": 200,
            "body": {
              "id": "{user_id}",
              "name": "John Doe",
              "email": "john@example.com",
              "created_at": "{{timestamp}}"
            }
          }
        }
      ]
    },
    {
      "method": "POST",
      "path": "/users",
      "tag": "Users",
      "authentication": ["bearer_token"],
      "description": "Create a new user",
      "request_schema": {
        "type": "object",
        "required": ["name", "email"],
        "properties": {
          "name": { "type": "string" },
          "email": { "type": "string", "format": "email" }
        }
      },
      "responses": [
        {
          "response": {
            "status_code": 201,
            "body": {
              "id": "{{random_uuid}}",
              "name": "{{request.name}}",
              "email": "{{request.email}}",
              "created_at": "{{timestamp}}"
            }
          }
        }
      ]
    }
  ]
}
```

### Step 5: Start Your Custom API

```bash
./mockctl start myapi --port 8080
```

## 🎛️ Key Features Explained

### Configuration-Driven Development

Mock-and-Roll uses JSON files to define your API without writing code:

- **`api.json`**: Server metadata, OpenAPI settings, system configuration
- **`auth.json`**: Authentication methods and credentials
- **`endpoints.json`**: API endpoints, request/response schemas

### Dynamic Template Variables

Use template variables for dynamic responses:

```json
{
  "user_id": "{{random_uuid}}",
  "timestamp": "{{timestamp}}",
  "request_data": "{{request.field_name}}",
  "random_number": "{{random_int(1, 100)}}"
}
```

### Conditional Responses

Return different responses based on request conditions:

```json
{
  "responses": [
    {
      "body_conditions": { "role": "admin" },
      "response": { "status_code": 200, "body": { "access": "granted" } }
    },
    {
      "body_conditions": { "role": "user" },
      "response": { "status_code": 403, "body": { "error": "forbidden" } }
    }
  ]
}
```

### Multiple Authentication Methods

Support various authentication schemes:

- **API Keys**: Header or query parameter based
- **Bearer Tokens**: JWT and simple bearer tokens
- **Basic Auth**: Username/password authentication
- **OIDC/OAuth2**: Authorization code flow simulation
- **Session Auth**: Cookie-based sessions
- **CSRF Protection**: Anti-CSRF token validation

### Redis Persistence (Optional)

Enable stateful behavior with Redis:

```json
{
  "method": "POST",
  "path": "/users",
  "persistence": {
    "entity_name": "users",
    "action": "create"
  }
}
```

### Comprehensive Logging

Monitor your API with detailed logging:

```bash
# Search logs by pattern
./mockctl search myapi "POST /users"

# Search with time filtering
./mockctl search myapi "/auth" --since "1h ago"

# Export logs as JSON
./mockctl --json search myapi "/api" > api-logs.json
```

## 🔧 Advanced Configuration

### Custom Request Validation

Add JSON Schema validation for request bodies:

```json
{
  "request_schema": {
    "type": "object",
    "required": ["name", "email"],
    "properties": {
      "name": {
        "type": "string",
        "minLength": 1,
        "maxLength": 100
      },
      "email": {
        "type": "string",
        "format": "email"
      },
      "age": {
        "type": "integer",
        "minimum": 0,
        "maximum": 150
      }
    }
  }
}
```

### Path Parameters and Conditions

Create dynamic paths with validation:

```json
{
  "path": "/users/{user_id}/posts/{post_id}",
  "path_conditions": {
    "user_id": 123,
    "post_id": "^[0-9]+$"
  }
}
```

### Multi-Response Endpoints

Handle different scenarios with multiple response conditions:

```json
{
  "responses": [
    {
      "path_conditions": { "user_id": 999 },
      "response": { "status_code": 404, "body": { "error": "User not found" } }
    },
    {
      "body_conditions": { "action": "delete" },
      "response": { "status_code": 204 }
    },
    {
      "response": { "status_code": 200, "body": { "success": true } }
    }
  ]
}
```

## � Production Deployment

### Docker Deployment

```bash
# Build production image
docker build -t my-mock-api .

# Run with custom config
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/configs/myapi:/app/configs/custom \
  -e CONFIG_NAME=custom \
  my-mock-api
```

### Environment Variables

Configure your deployment with environment variables:

```bash
export CONFIG_FOLDER="/path/to/configs"
export REDIS_HOST="redis.example.com"
export REDIS_PORT="6379"
export LOG_LEVEL="INFO"

./mockctl start myapi
```

## 🔍 Monitoring and Debugging

### Server Management

```bash
# List all running servers
./mockctl list

# Stop specific server
./mockctl stop --config myapi

# Stop all servers
./mockctl stop --all

# Clean up logs and processes
./mockctl clean-up
```

### Log Analysis

```bash
# Real-time log monitoring
tail -f logs/mockctl.log

# Search for specific patterns
./mockctl search myapi "ERROR"

# JSON output for analysis
./mockctl --json search myapi "/users" | jq '.requests[].status_code'
```

### Health Checks

Every Mock-and-Roll server includes system endpoints:

```bash
# Health check
curl http://localhost:8000/system/health

# Server info
curl -H "X-System-Key: system-admin-key" \
     http://localhost:8000/system/info

# Clear Redis cache (if persistence enabled)
curl -X DELETE \
     -H "X-System-Key: system-admin-key" \
     http://localhost:8000/system/cache
```

## 🎉 What's Next?

You now have a fully functional custom mock API! Explore these advanced topics:

- **[Configuration Reference](reference/configuration-schema.md)**: Complete configuration options
- **[Authentication Guide](../features/authentication.md)**: Advanced authentication setups
- **[Persistence Features](../features/persistence.md)**: Redis integration and data management
- **[CLI Reference](user-guide/cli-commands.md)**: Master all `mockctl` commands
- **[Examples](examples/basic-usage.md)**: Real-world use cases and patterns

## 💡 Pro Tips

**Development Workflow:**

```bash
# Quick config validation
./mockctl config-help

# Auto-restart on config changes
./mockctl start myapi --reload

# Test specific endpoints
./mockctl test myapi
   # Edit and restart
   vim configs/basic/endpoints.json
   ./mockctl stop
   ./mockctl start basic
```

Happy mocking! 🚀
