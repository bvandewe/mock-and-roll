# Configuration-Driven API Development

Mock-and-Roll's core philosophy is **configuration over code** - create sophisticated REST APIs through JSON configuration files without writing any server code.

## Overview

Instead of writing FastAPI routes and handlers, you define your entire API through three simple JSON files:

- **`api.json`** - Server metadata, OpenAPI settings, system configuration
- **`auth.json`** - Authentication methods and credentials
- **`endpoints.json`** - API endpoints, request/response schemas

This approach enables rapid prototyping, consistent API structure, and easy maintenance.

## Benefits of Configuration-Driven Development

### 🚀 **Rapid Prototyping**

Create working APIs in minutes, not hours. Perfect for:

- Proof of concepts
- Client development before backend is ready
- Testing and integration scenarios
- API design validation

### 📝 **Declarative API Design**

Define what your API does, not how it works:

- Clear separation of API contract from implementation
- Version control friendly JSON files
- Easy to review and modify
- Self-documenting structure

### 🔄 **Consistency Across Teams**

Standardized configuration ensures consistent APIs:

- Common patterns and conventions
- Reusable authentication schemes
- Standardized error handling
- Unified logging and monitoring

### 🎯 **Focus on Business Logic**

Spend time on API design rather than infrastructure:

- No boilerplate FastAPI code
- Automatic Swagger documentation generation
- Built-in authentication handling
- Integrated request validation

## Configuration Architecture

### Three-File Structure

Mock-and-Roll uses a modular configuration approach:

```
configs/myapi/
├── api.json        # Server & API metadata
├── auth.json       # Authentication configuration
└── endpoints.json  # API endpoints definition
```

### Configuration Inheritance

Build complex APIs by extending base configurations:

```bash
# Start with a base configuration
cp -r configs/basic configs/myapi

# Customize for your needs
vim configs/myapi/endpoints.json

# Add new authentication methods
vim configs/myapi/auth.json
```

## API Configuration (`api.json`)

Define your API's core properties and metadata:

### Basic Structure

```json
{
  "api_name": "My Custom API",
  "version": "1.0.0",
  "description": "A comprehensive mock API for testing",
  "base_url": "https://api.mycompany.com",
  "root_path": "/api/v1"
}
```

### OpenAPI Integration

Automatic Swagger documentation generation:

```json
{
  "openapi_tags": [
    {
      "name": "Users",
      "description": "User management operations"
    },
    {
      "name": "Products",
      "description": "Product catalog and inventory"
    }
  ],
  "swagger_ui": {
    "airgapped_mode": true,
    "doc_expansion": "list",
    "try_it_out_enabled": true,
    "display_request_duration": true
  }
}
```

### System Configuration

Built-in health checks and admin endpoints:

```json
{
  "system": {
    "authentication": ["system_api_key"],
    "endpoints": ["system_health", "system_info", "cache_management"]
  }
}
```

## Authentication Configuration (`auth.json`)

Define multiple authentication methods for different use cases:

### Multiple Authentication Schemes

```json
{
  "authentication_methods": {
    "api_key": {
      "type": "api_key",
      "name": "X-API-Key",
      "location": "header",
      "valid_keys": ["key1", "key2"]
    },
    "bearer_token": {
      "type": "http_bearer",
      "valid_tokens": ["token1", "token2"]
    },
    "basic_auth": {
      "type": "http_basic",
      "valid_credentials": [{ "username": "admin", "password": "secret" }]
    }
  }
}
```

### Advanced Authentication

Support for OAuth2, OIDC, and session-based auth:

```json
{
  "oidc_auth": {
    "type": "oidc",
    "grant_type": "authorization_code",
    "client_id": "my-client-id",
    "authorization_url": "https://auth.example.com/oauth2/authorize",
    "token_url": "https://auth.example.com/oauth2/token",
    "scopes": ["read", "write", "admin"]
  }
}
```

## Endpoints Configuration (`endpoints.json`)

Define your API endpoints with full FastAPI compatibility:

### Basic Endpoint

```json
{
  "endpoints": [
    {
      "method": "GET",
      "path": "/users/{user_id}",
      "tag": "Users",
      "description": "Get user by ID",
      "authentication": ["api_key"],
      "responses": [
        {
          "response": {
            "status_code": 200,
            "body": {
              "id": "{user_id}",
              "name": "John Doe",
              "email": "john@example.com"
            }
          }
        }
      ]
    }
  ]
}
```

### Request Validation

JSON Schema validation for request bodies:

```json
{
  "method": "POST",
  "path": "/users",
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
      }
    }
  }
}
```

### Dynamic Responses

Template variables and conditional logic:

```json
{
  "responses": [
    {
      "body_conditions": { "role": "admin" },
      "response": {
        "status_code": 200,
        "body": {
          "access_level": "full",
          "user_id": "{{random_uuid}}",
          "timestamp": "{{timestamp}}"
        }
      }
    },
    {
      "response": {
        "status_code": 403,
        "body": { "error": "Access denied" }
      }
    }
  ]
}
```

## Configuration Patterns

### Modular Design

Organize endpoints by functional areas:

```json
{
  "endpoints": [
    // User Management
    { "method": "GET", "path": "/users", "tag": "Users" },
    { "method": "POST", "path": "/users", "tag": "Users" },

    // Product Catalog
    { "method": "GET", "path": "/products", "tag": "Products" },
    { "method": "POST", "path": "/products", "tag": "Products" }
  ]
}
```

### Environment-Specific Configurations

Use different configurations for different environments:

```bash
configs/
├── development/    # Local development
├── staging/        # Staging environment
├── testing/        # Test automation
└── production/     # Production-like mocks
```

### Configuration Validation

Mock-and-Roll validates your configuration on startup:

```bash
# Test configuration validity
./mockctl config-help myapi

# Start with validation
./mockctl start myapi --validate
```

## Best Practices

### 1. **Start Simple, Build Up**

```json
// Start with minimal configuration
{
    "method": "GET",
    "path": "/health",
    "responses": [{"response": {"status_code": 200, "body": {"status": "ok"}}}]
}

// Add complexity incrementally
{
    "method": "GET",
    "path": "/users/{id}",
    "authentication": ["api_key"],
    "parameters": {"id": {"type": "string", "pattern": "^[0-9]+$"}},
    "responses": [
        {"path_conditions": {"id": "999"}, "response": {"status_code": 404}},
        {"response": {"status_code": 200, "body": {"id": "{id}", "name": "User"}}}
    ]
}
```

### 2. **Use Meaningful Names**

```json
{
    "authentication_methods": {
        "public_api_key": {...},      // For public endpoints
        "admin_bearer_token": {...},  // For admin operations
        "user_session_auth": {...}    // For user sessions
    }
}
```

### 3. **Leverage Template Variables**

```json
{
  "body": {
    "id": "{{random_uuid}}",
    "created_at": "{{timestamp}}",
    "user_data": "{{request.user_info}}",
    "random_score": "{{random_int(1, 100)}}"
  }
}
```

### 4. **Design for Testing**

```json
{
  "responses": [
    // Test success case
    {
      "body_conditions": { "test_mode": true },
      "response": { "status_code": 200, "body": { "success": true } }
    },
    // Test error case
    {
      "body_conditions": { "simulate_error": true },
      "response": { "status_code": 500, "body": { "error": "Simulated failure" } }
    },
    // Default response
    {
      "response": { "status_code": 200, "body": { "result": "normal" } }
    }
  ]
}
```

## Advanced Configuration Features

### 1. **Path Parameter Validation**

```json
{
  "path": "/users/{user_id}/posts/{post_id}",
  "parameters": {
    "user_id": {
      "type": "integer",
      "minimum": 1
    },
    "post_id": {
      "type": "string",
      "pattern": "^[a-zA-Z0-9-]+$"
    }
  }
}
```

### 2. **Conditional Authentication**

```json
{
  "method": "GET",
  "path": "/data/{category}",
  "conditional_auth": {
    "public": [], // No auth for public data
    "private": ["api_key"], // API key for private data
    "admin": ["admin_bearer_token"] // Admin token for admin data
  }
}
```

### 3. **Response Headers**

```json
{
  "response": {
    "status_code": 201,
    "headers": {
      "Location": "/users/{{random_uuid}}",
      "X-Rate-Limit": "100",
      "Cache-Control": "no-cache"
    },
    "body": { "created": true }
  }
}
```

### 4. **Multi-Format Responses**

```json
{
  "responses": [
    {
      "query_conditions": { "format": "xml" },
      "response": {
        "status_code": 200,
        "headers": { "Content-Type": "application/xml" },
        "body": "<?xml version='1.0'?><user><id>123</id></user>"
      }
    },
    {
      "response": {
        "status_code": 200,
        "headers": { "Content-Type": "application/json" },
        "body": { "id": 123, "name": "User" }
      }
    }
  ]
}
```

## Configuration Management

### Version Control

Track configuration changes with Git:

```bash
# Commit configuration changes
git add configs/myapi/
git commit -m "Add user authentication endpoints"

# Compare configurations
git diff configs/myapi/endpoints.json

# Rollback changes
git checkout HEAD~1 configs/myapi/
```

### Configuration Testing

Validate configurations before deployment:

```bash
# Syntax validation
./mockctl validate-config myapi

# Integration testing
./mockctl test myapi --endpoint "/users"

# Load testing
./mockctl stress-test myapi --requests 1000
```

### Hot Reloading

Update configurations without restarting:

```bash
# Start in development mode
./mockctl start myapi --reload

# Configuration changes are detected automatically
# Server reloads with new settings
```

## Migration and Evolution

### Updating Existing APIs

Safely evolve your API configuration:

```json
{
  // Version your endpoints
  "endpoints": [
    {
      "method": "GET",
      "path": "/v1/users/{id}", // Legacy version
      "deprecated": true
    },
    {
      "method": "GET",
      "path": "/v2/users/{id}", // New version
      "tag": "Users v2"
    }
  ]
}
```

### Configuration Migration

Automated migration between configuration versions:

```bash
# Migrate old configuration format
./mockctl migrate-config myapi --from-version 1.0 --to-version 2.0

# Backup before migration
./mockctl backup-config myapi
```

## Integration with Development Workflow

### CI/CD Integration

```yaml
# .github/workflows/api-tests.yml
- name: Test Mock API Configuration
  run: |
    ./mockctl validate-config production
    ./mockctl start production --port 8080 &
    sleep 5
    curl http://localhost:8080/health
    ./mockctl stop --all
```

### API Documentation Generation

```bash
# Generate OpenAPI spec from configuration
./mockctl export-openapi myapi > api-spec.yaml

# Generate documentation
swagger-codegen generate -i api-spec.yaml -l html -o docs/
```

## Troubleshooting Configuration Issues

### Common Configuration Errors

**Invalid JSON Syntax:**

```bash
# Validate JSON syntax
./mockctl validate myapi
# Error: Invalid JSON in endpoints.json line 45
```

**Missing Authentication Method:**

```bash
# Referenced auth method doesn't exist
# Error: Authentication method 'nonexistent_key' not found in auth.json
```

**Path Parameter Mismatch:**

```bash
# Path parameters don't match endpoint definition
# Error: Parameter 'user_id' defined but not used in path '/users'
```

### Configuration Debugging

```bash
# Debug configuration loading
./mockctl start myapi --debug

# Show effective configuration
./mockctl show-config myapi --resolved

# Validate specific configuration file
./mockctl validate myapi --file endpoints.json
```

## Conclusion

Configuration-driven development with Mock-and-Roll enables rapid API prototyping and consistent development practices. By defining APIs through JSON configuration rather than code, teams can:

- Iterate quickly on API designs
- Maintain consistent patterns across projects
- Enable non-developers to contribute to API design
- Create comprehensive test scenarios
- Generate documentation automatically

Start with simple configurations and gradually add complexity as your needs evolve. The configuration-driven approach scales from simple prototypes to complex, realistic API simulations.
