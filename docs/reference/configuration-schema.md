# Configuration Schema Reference

Complete reference for Mock-and-Roll configuration files.

## Overview

Mock-and-Roll uses JSON configuration files to define API behavior. This reference documents all available configuration options.

## File Structure

Each configuration profile contains three main files:

```
configs/<profile_name>/
├── api.json       # API metadata and server settings
├── auth.json      # Authentication configuration
└── endpoints.json # Endpoint definitions
```

## API Configuration (`api.json`)

### Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "info": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
        "version": {"type": "string"},
        "contact": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "email": {"type": "string"},
            "url": {"type": "string"}
          }
        }
      },
      "required": ["title", "description", "version"]
    },
    "server": {
      "type": "object", 
      "properties": {
        "host": {"type": "string"},
        "port": {"type": "integer", "minimum": 1, "maximum": 65535},
        "reload": {"type": "boolean"},
        "debug": {"type": "boolean"},
        "workers": {"type": "integer", "minimum": 1}
      },
      "required": ["host", "port"]
    },
    "system_auth": {
      "type": "object",
      "properties": {
        "enabled": {"type": "boolean"},
        "api_key": {"type": "string"},
        "endpoints": {
          "type": "array",
          "items": {"type": "string"}
        }
      },
      "required": ["enabled"]
    },
    "redis": {
      "type": "object",
      "properties": {
        "enabled": {"type": "boolean"},
        "host": {"type": "string"},
        "port": {"type": "integer"},
        "db": {"type": "integer"},
        "password": {"type": "string"},
        "ssl": {"type": "boolean"}
      }
    }
  },
  "required": ["info", "server"]
}
```

### Configuration Options

#### `info` (required)

| Field | Type | Description | Default | Example |
|-------|------|-------------|---------|---------|
| `title` | string | API title for documentation | - | "Mock API Server" |
| `description` | string | API description | - | "Configurable mock REST API" |
| `version` | string | API version | - | "1.0.0" |
| `contact.name` | string | Contact name | - | "API Team" |
| `contact.email` | string | Contact email | - | "api@example.com" |
| `contact.url` | string | Contact URL | - | "https://example.com" |

#### `server` (required)

| Field | Type | Description | Default | Example |
|-------|------|-------------|---------|---------|
| `host` | string | Server bind address | - | "0.0.0.0" |
| `port` | integer | Server port (1-65535) | - | 8000 |
| `reload` | boolean | Auto-reload on file changes | false | true |
| `debug` | boolean | Enable debug mode | false | true |
| `workers` | integer | Number of worker processes | 1 | 4 |

#### `system_auth` (optional)

| Field | Type | Description | Default | Example |
|-------|------|-------------|---------|---------|
| `enabled` | boolean | Enable system authentication | false | true |
| `api_key` | string | System admin API key | generated | "admin-key-123" |
| `endpoints` | array | Protected system endpoints | ["/system/*"] | ["/admin", "/metrics"] |

#### `redis` (optional)

| Field | Type | Description | Default | Example |
|-------|------|-------------|---------|---------|
| `enabled` | boolean | Enable Redis integration | false | true |
| `host` | string | Redis server host | "localhost" | "redis.example.com" |
| `port` | integer | Redis server port | 6379 | 6380 |
| `db` | integer | Redis database number | 0 | 1 |
| `password` | string | Redis password | null | "secret123" |
| `ssl` | boolean | Use SSL connection | false | true |

## Authentication Configuration (`auth.json`)

### Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "methods": {
      "type": "object",
      "properties": {
        "api_key": {
          "type": "object",
          "properties": {
            "enabled": {"type": "boolean"},
            "header_name": {"type": "string"},
            "query_param": {"type": "string"},
            "valid_keys": {
              "type": "array",
              "items": {"type": "string"}
            }
          }
        },
        "oauth": {
          "type": "object",
          "properties": {
            "enabled": {"type": "boolean"},
            "token_url": {"type": "string"},
            "introspect_url": {"type": "string"},
            "client_id": {"type": "string"},
            "client_secret": {"type": "string"}
          }
        },
        "basic": {
          "type": "object",
          "properties": {
            "enabled": {"type": "boolean"},
            "username": {"type": "string"},
            "password": {"type": "string"}
          }
        },
        "jwt": {
          "type": "object",
          "properties": {
            "enabled": {"type": "boolean"},
            "secret": {"type": "string"},
            "algorithm": {"type": "string"},
            "verify_signature": {"type": "boolean"}
          }
        }
      }
    },
    "default_method": {"type": "string"},
    "require_auth": {"type": "boolean"},
    "auth_failure_response": {
      "type": "object",
      "properties": {
        "status_code": {"type": "integer"},
        "response": {"type": "object"}
      }
    }
  }
}
```

### Authentication Methods

#### API Key Authentication

```json
{
  "methods": {
    "api_key": {
      "enabled": true,
      "header_name": "X-API-Key",
      "query_param": "api_key",
      "valid_keys": [
        "user-key-123",
        "admin-key-456"
      ]
    }
  }
}
```

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `enabled` | boolean | Enable API key auth | false |
| `header_name` | string | HTTP header name | "X-API-Key" |
| `query_param` | string | Query parameter name | "api_key" |
| `valid_keys` | array | List of valid API keys | [] |

#### OAuth 2.0 Authentication

```json
{
  "methods": {
    "oauth": {
      "enabled": true,
      "token_url": "/oauth/token",
      "introspect_url": "/oauth/introspect", 
      "client_id": "mock-client",
      "client_secret": "mock-secret"
    }
  }
}
```

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `enabled` | boolean | Enable OAuth auth | false |
| `token_url` | string | Token endpoint URL | "/oauth/token" |
| `introspect_url` | string | Token introspection URL | "/oauth/introspect" |
| `client_id` | string | OAuth client ID | - |
| `client_secret` | string | OAuth client secret | - |

#### HTTP Basic Authentication

```json
{
  "methods": {
    "basic": {
      "enabled": true,
      "username": "admin",
      "password": "secret"
    }
  }
}
```

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `enabled` | boolean | Enable basic auth | false |
| `username` | string | Valid username | - |
| `password` | string | Valid password | - |

#### JWT Authentication

```json
{
  "methods": {
    "jwt": {
      "enabled": true,
      "secret": "jwt-secret-key",
      "algorithm": "HS256",
      "verify_signature": true
    }
  }
}
```

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `enabled` | boolean | Enable JWT auth | false |
| `secret` | string | JWT signing secret | - |
| `algorithm` | string | JWT algorithm | "HS256" |
| `verify_signature` | boolean | Verify JWT signature | true |

## Endpoint Configuration (`endpoints.json`)

### Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "endpoints": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "path": {"type": "string"},
          "method": {"type": "string"},
          "response": {"type": "object"},
          "status_code": {"type": "integer"},
          "auth_required": {"type": "boolean"},
          "headers": {"type": "object"},
          "conditions": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "when": {"type": "string"},
                "response": {"type": "object"},
                "status_code": {"type": "integer"}
              }
            }
          },
          "delay_ms": {"type": "integer"},
          "persistence": {
            "type": "object",
            "properties": {
              "store": {"type": "boolean"},
              "key": {"type": "string"},
              "ttl": {"type": "integer"}
            }
          }
        },
        "required": ["path", "method", "response", "status_code"]
      }
    }
  },
  "required": ["endpoints"]
}
```

### Endpoint Properties

#### Basic Properties

| Field | Type | Description | Required | Example |
|-------|------|-------------|----------|---------|
| `path` | string | URL path with optional parameters | ✅ | "/api/users/{id}" |
| `method` | string | HTTP method | ✅ | "GET", "POST", "PUT", "DELETE" |
| `response` | object | Response body template | ✅ | {"id": "{{path.id}}"} |
| `status_code` | integer | HTTP status code | ✅ | 200, 201, 404, 500 |

#### Optional Properties

| Field | Type | Description | Default | Example |
|-------|------|-------------|---------|---------|
| `auth_required` | boolean | Require authentication | false | true |
| `headers` | object | Custom response headers | {} | {"X-Custom": "value"} |
| `delay_ms` | integer | Response delay in milliseconds | 0 | 1000 |

#### Advanced Properties

##### Conditions

```json
{
  "conditions": [
    {
      "when": "{{query.type}} == 'admin'",
      "response": {"role": "administrator"},
      "status_code": 200
    },
    {
      "when": "{{headers.x-test}} == 'true'",
      "response": {"test_mode": true},
      "status_code": 200
    }
  ]
}
```

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `when` | string | Condition expression | ✅ |
| `response` | object | Conditional response | ✅ |
| `status_code` | integer | Conditional status code | ❌ |

##### Persistence

```json
{
  "persistence": {
    "store": true,
    "key": "user:{{path.id}}",
    "ttl": 3600
  }
}
```

| Field | Type | Description | Default | Example |
|-------|------|-------------|---------|---------|
| `store` | boolean | Store response in Redis | false | true |
| `key` | string | Redis key template | - | "user:{{path.id}}" |
| `ttl` | integer | Time to live in seconds | null | 3600 |

## Template Variables

### Built-in Variables

| Variable | Description | Example Output |
|----------|-------------|----------------|
| `{{now}}` | Current ISO timestamp | "2025-01-01T12:00:00Z" |
| `{{uuid}}` | Random UUID | "550e8400-e29b-41d4-a716-..." |
| `{{random}}` | Random number (0-1000) | 42 |
| `{{timestamp}}` | Unix timestamp | 1640995200 |

### Request Context Variables

#### Path Parameters

```json
{
  "path": "/api/users/{user_id}/posts/{post_id}",
  "response": {
    "user_id": "{{path.user_id}}",
    "post_id": "{{path.post_id}}"
  }
}
```

#### Query Parameters

```json
{
  "response": {
    "search": "{{query.q}}",
    "page": "{{query.page|default:1}}",
    "limit": "{{query.limit|default:10}}"
  }
}
```

#### Request Headers

```json
{
  "response": {
    "correlation_id": "{{headers.x-correlation-id}}",
    "user_agent": "{{headers.user-agent}}"
  }
}
```

#### Request Body

```json
{
  "response": {
    "username": "{{body.username}}",
    "email": "{{body.email}}",
    "created_user": "{{body.name}}"
  }
}
```

### Template Filters

| Filter | Description | Example |
|--------|-------------|---------|
| `default:value` | Default value if empty | `{{query.page|default:1}}` |
| `upper` | Convert to uppercase | `{{body.name|upper}}` |
| `lower` | Convert to lowercase | `{{headers.content-type|lower}}` |
| `add:N` | Add number | `{{query.page|add:1}}` |
| `multiply:N` | Multiply by number | `{{body.quantity|multiply:2}}` |

## Environment Variable Overrides

Override configuration values using environment variables:

| Environment Variable | Configuration Path | Example |
|---------------------|-------------------|---------|
| `MOCK_API_TITLE` | `info.title` | "Custom API Title" |
| `MOCK_API_PORT` | `server.port` | 8080 |
| `MOCK_API_HOST` | `server.host` | "127.0.0.1" |
| `MOCK_REDIS_HOST` | `redis.host` | "redis.example.com" |
| `MOCK_REDIS_PORT` | `redis.port` | 6380 |
| `MOCK_AUTH_ENABLED` | `methods.api_key.enabled` | true |

## Validation

### Configuration Validation

Mock-and-Roll validates configurations on startup:

```bash
# Validate specific profile
./mockctl validate basic

# Validate with strict checking
./mockctl validate basic --strict
```

### Common Validation Errors

#### Invalid JSON Syntax

```json
{
  "path": "/api/test",
  "method": "GET",
  "response": {
    "message": "Hello"  // Missing comma
    "status": "ok"
  }
}
```

#### Missing Required Fields

```json
{
  "path": "/api/test",
  // Missing required "method" field
  "response": {"message": "Hello"},
  "status_code": 200
}
```

#### Invalid Field Types

```json
{
  "path": "/api/test",
  "method": "GET",
  "response": {"message": "Hello"},
  "status_code": "200"  // Should be integer, not string
}
```

## Best Practices

### Configuration Organization

1. **Separate Concerns** - Use different profiles for different environments
2. **Consistent Naming** - Use clear, descriptive endpoint paths
3. **Version Control** - Keep configurations in version control
4. **Documentation** - Document custom configurations

### Security

1. **Strong Keys** - Use complex API keys and secrets
2. **Minimal Permissions** - Only enable required authentication methods
3. **Environment Variables** - Use env vars for sensitive data
4. **Regular Rotation** - Rotate keys and secrets regularly

### Performance

1. **Efficient Templates** - Minimize complex template processing
2. **Appropriate Delays** - Use realistic response delays
3. **Redis TTL** - Set appropriate TTL for cached data
4. **Resource Limits** - Configure reasonable limits

### Maintainability

1. **Clear Structure** - Organize endpoints logically
2. **Reusable Patterns** - Use consistent response patterns
3. **Comprehensive Testing** - Test all configurations
4. **Regular Updates** - Keep configurations current

This reference provides complete documentation for all Mock-and-Roll configuration options. For specific examples and use cases, see the [Configuration Guide](../configuration.md) and [Examples](../examples/basic-usage.md).
