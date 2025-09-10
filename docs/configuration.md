# Configuration Guide

Learn how to configure Mock-and-Roll for your specific needs.

## Overview

Mock-and-Roll uses a three-tier configuration system stored in the `configs/` directory:

```
configs/
├── basic/          # Simple mock API configuration
├── persistence/    # Configuration with Redis persistence  
└── vmanage/        # Cisco vManage API simulation
```

Each configuration profile contains three main files:

- **`api.json`** - API metadata and server settings
- **`auth.json`** - Authentication methods and security
- **`endpoints.json`** - Dynamic endpoint definitions

## Configuration Files

### API Configuration (`api.json`)

Defines basic API metadata and server settings:

```json
{
  "info": {
    "title": "Mock API Server",
    "description": "Configurable mock REST API",
    "version": "1.0.0"
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": false
  },
  "system_auth": {
    "enabled": true,
    "api_key": "system-admin-key-12345"
  }
}
```

**Key Settings:**

| Field | Description | Default |
|-------|-------------|---------|
| `info.title` | API title in documentation | "Mock API Server" |
| `info.description` | API description | Basic description |
| `info.version` | API version | "1.0.0" |
| `server.host` | Bind address | "0.0.0.0" |
| `server.port` | Server port | 8000 |
| `server.reload` | Auto-reload on changes | false |
| `system_auth.enabled` | Enable system authentication | true |
| `system_auth.api_key` | System admin API key | Generated key |

### Authentication Configuration (`auth.json`)

Configures authentication methods and security settings:

```json
{
  "methods": {
    "api_key": {
      "enabled": true,
      "header_name": "X-API-Key",
      "valid_keys": [
        "demo-key-123",
        "test-key-456"
      ]
    },
    "oauth": {
      "enabled": false,
      "token_url": "/oauth/token",
      "introspect_url": "/oauth/introspect"
    }
  },
  "default_method": "api_key",
  "require_auth": false
}
```

**Authentication Methods:**

| Method | Description | Use Case |
|--------|-------------|----------|
| `api_key` | Simple API key authentication | Development, testing |
| `oauth` | OAuth 2.0 token authentication | Production-like scenarios |
| `basic` | HTTP Basic authentication | Legacy system simulation |
| `jwt` | JWT token authentication | Modern API simulation |

### Endpoint Configuration (`endpoints.json`)

Defines the API endpoints and their behavior:

```json
{
  "endpoints": [
    {
      "path": "/api/health",
      "method": "GET", 
      "response": {
        "status": "healthy",
        "timestamp": "{{now}}"
      },
      "status_code": 200,
      "auth_required": false
    },
    {
      "path": "/api/users/{user_id}",
      "method": "GET",
      "response": {
        "id": "{{path.user_id}}",
        "name": "User {{path.user_id}}",
        "email": "user{{path.user_id}}@example.com"
      },
      "status_code": 200,
      "auth_required": true
    }
  ]
}
```

**Endpoint Properties:**

| Property | Type | Description | Required |
|----------|------|-------------|----------|
| `path` | string | URL path with optional parameters | ✅ |
| `method` | string | HTTP method (GET, POST, PUT, DELETE, etc.) | ✅ |
| `response` | object | Response body template | ✅ |
| `status_code` | integer | HTTP status code | ✅ |
| `auth_required` | boolean | Whether authentication is required | ❌ |
| `headers` | object | Custom response headers | ❌ |
| `conditions` | array | Conditional response rules | ❌ |

## Template Variables

Mock-and-Roll supports dynamic response generation using template variables:

### Built-in Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{now}}` | Current timestamp (ISO 8601) | "2025-01-01T12:00:00Z" |
| `{{uuid}}` | Random UUID | "550e8400-e29b-41d4-a716-446655440000" |
| `{{random}}` | Random number (0-1000) | 42 |
| `{{timestamp}}` | Unix timestamp | 1640995200 |

### Path Parameters

Extract values from URL paths:

```json
{
  "path": "/api/users/{user_id}/posts/{post_id}",
  "response": {
    "user_id": "{{path.user_id}}",
    "post_id": "{{path.post_id}}"
  }
}
```

### Query Parameters

Access query string values:

```json
{
  "path": "/api/search",
  "response": {
    "query": "{{query.q}}",
    "limit": "{{query.limit|default:10}}"
  }
}
```

### Request Headers

Use request headers in responses:

```json
{
  "response": {
    "correlation_id": "{{headers.x-correlation-id}}",
    "user_agent": "{{headers.user-agent}}"
  }
}
```

## Conditional Responses

Create dynamic responses based on request conditions:

```json
{
  "path": "/api/login",
  "method": "POST",
  "conditions": [
    {
      "when": "{{body.username}} == 'admin'",
      "response": {
        "token": "admin-token-123",
        "role": "administrator"
      },
      "status_code": 200
    },
    {
      "when": "{{body.username}} == 'user'", 
      "response": {
        "token": "user-token-456",
        "role": "user"
      },
      "status_code": 200
    }
  ],
  "response": {
    "error": "Invalid credentials"
  },
  "status_code": 401
}
```

## Environment Variables

Override configuration settings using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MOCK_CONFIG_FOLDER` | Configuration directory path | `configs/basic` |
| `CONFIG_FOLDER` | Alternative config path variable | - |
| `REDIS_HOST` | Redis server hostname | `localhost` |
| `REDIS_PORT` | Redis server port | `6379` |
| `REDIS_DB` | Redis database number | `0` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Configuration Profiles

### Basic Profile

**Purpose:** Simple mock API for development and testing

**Features:**
- RESTful endpoints
- JSON responses
- Optional authentication
- Template variables
- In-memory data

**Use Cases:**
- Frontend development
- API client testing
- Rapid prototyping

### Persistence Profile

**Purpose:** Stateful mock API with data persistence

**Features:**
- All basic features
- Redis integration
- Data persistence
- User management
- Session handling

**Use Cases:**
- Integration testing
- Demonstration environments
- Training scenarios

**Requirements:**
- Redis server

### vManage Profile

**Purpose:** Cisco vManage SD-WAN controller simulation

**Features:**
- Authentication workflows
- Device management
- Policy configuration
- Network monitoring
- Realistic data structures

**Use Cases:**
- Network automation development
- SD-WAN training
- Cisco ecosystem integration

## Creating Custom Profiles

### Step 1: Create Directory Structure

```bash
mkdir -p configs/myprofile
cd configs/myprofile
```

### Step 2: Create Configuration Files

```bash
# Copy from existing profile
cp ../basic/api.json .
cp ../basic/auth.json .
cp ../basic/endpoints.json .
```

### Step 3: Customize Configuration

Edit the files to match your requirements:

```json
// api.json
{
  "info": {
    "title": "My Custom API",
    "description": "Custom mock API for my project",
    "version": "1.0.0"
  },
  "server": {
    "host": "0.0.0.0", 
    "port": 8080
  }
}
```

### Step 4: Test Your Configuration

```bash
./mockctl start myprofile --port 8080
```

## Advanced Configuration

### Custom Headers

Add custom headers to all responses:

```json
{
  "path": "/api/data",
  "response": {"data": "example"},
  "headers": {
    "X-Custom-Header": "Custom Value",
    "X-Request-ID": "{{uuid}}"
  }
}
```

### Error Simulation

Simulate different error conditions:

```json
{
  "path": "/api/error-test",
  "conditions": [
    {
      "when": "{{query.error}} == 'server'",
      "status_code": 500,
      "response": {"error": "Internal server error"}
    },
    {
      "when": "{{query.error}} == 'auth'",
      "status_code": 401,
      "response": {"error": "Unauthorized"}
    }
  ],
  "response": {"message": "Success"},
  "status_code": 200
}
```

### Response Delays

Add realistic response delays:

```json
{
  "path": "/api/slow",
  "response": {"message": "This was slow"},
  "delay_ms": 2000,
  "status_code": 200
}
```

## Validation and Testing

### Validate Configuration

```bash
# Test configuration syntax
./mockctl validate myprofile

# Start with verbose logging
./mockctl start myprofile --verbose
```

### Test Endpoints

```bash
# Test health endpoint
curl http://localhost:8080/api/health

# Test with authentication
curl -H "X-API-Key: demo-key-123" http://localhost:8080/api/protected

# Test POST with data
curl -X POST -H "Content-Type: application/json" \
  -d '{"username": "admin"}' \
  http://localhost:8080/api/login
```

## Best Practices

### Security

1. **Use strong API keys** in production-like environments
2. **Enable authentication** for sensitive endpoints
3. **Rotate system auth keys** regularly
4. **Use HTTPS** in production deployments

### Performance

1. **Minimize response size** for high-volume testing
2. **Use appropriate delays** to simulate realistic performance
3. **Monitor resource usage** for long-running tests
4. **Cache static responses** when possible

### Maintainability

1. **Use descriptive endpoint names**
2. **Document custom configurations**
3. **Version configuration profiles**
4. **Test configurations** before deployment

### Organization

1. **Group related endpoints** logically
2. **Use consistent naming** conventions
3. **Separate environments** (dev, test, prod)
4. **Keep configurations simple** and focused

## Troubleshooting

### Common Configuration Issues

**Invalid JSON syntax:**
```bash
# Validate JSON files
python -m json.tool configs/myprofile/api.json
```

**Port conflicts:**
```bash
# Check port usage
./mockctl list
netstat -an | grep :8080
```

**Authentication issues:**
```bash
# Test without auth
curl http://localhost:8080/api/health

# Test with auth
curl -H "X-API-Key: demo-key-123" http://localhost:8080/api/protected
```

**Template variable errors:**
```bash
# Check logs for template errors
tail -f logs/latest.logs
```

### Configuration Validation

Mock-and-Roll includes built-in configuration validation:

```bash
# Validate specific profile
./mockctl validate basic

# Start with validation
./mockctl start myprofile --validate
```

## Next Steps

- **[CLI Commands](user-guide/cli-commands.md)**: Learn advanced CLI usage
- **[Examples](examples/basic-usage.md)**: See configuration examples
- **[Architecture](architecture/overview.md)**: Understand the system design
- **[API Reference](reference/api-reference.md)**: Complete API documentation
