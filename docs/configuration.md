# Configuration Guide

Learn how to configure Mock-and-Roll for your specific needs.

## Overview

Mock-and-Roll uses a three-tier configuration system stored in the `configs/` directory:

```
configs/
├── airgapped/      # Air-gapped deployment configuration
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

| Field                 | Description                  | Default           |
| --------------------- | ---------------------------- | ----------------- |
| `info.title`          | API title in documentation   | "Mock API Server" |
| `info.description`    | API description              | Basic description |
| `info.version`        | API version                  | "1.0.0"           |
| `server.host`         | Bind address                 | "0.0.0.0"         |
| `server.port`         | Server port                  | 8000              |
| `server.reload`       | Auto-reload on changes       | false             |
| `system_auth.enabled` | Enable system authentication | true              |
| `system_auth.api_key` | System admin API key         | Generated key     |

### Authentication Configuration (`auth.json`)

Configures authentication methods and security settings:

```json
{
  "authentication_methods": {
    "api_key": {
      "type": "api_key",
      "name": "X-API-Key",
      "location": "header",
      "valid_keys": ["demo-api-key-123", "test-key-456"]
    },
    "basic_auth": {
      "type": "http_basic",
      "valid_credentials": [
        {
          "username": "admin",
          "password": "secret123"
        },
        {
          "username": "user",
          "password": "password"
        }
      ]
    },
    "oidc_auth_code": {
      "type": "oidc",
      "grant_type": "authorization_code",
      "client_id": "demo-client-id",
      "client_secret": "demo-client-secret",
      "authorization_url": "https://auth.example.com/oauth2/authorize",
      "token_url": "https://auth.example.com/oauth2/token",
      "scopes": ["read", "write"],
      "valid_tokens": [
        {
          "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.demo-token",
          "scope": "read write",
          "expires_in": 3600
        }
      ]
    }
  }
}
```

**Authentication Methods:**

| Method                    | Type       | Description                           |
| ------------------------- | ---------- | ------------------------------------- |
| `api_key`                 | api_key    | API key in header (X-API-Key)         |
| `basic_auth`              | http_basic | HTTP Basic authentication             |
| `oidc_auth_code`          | oidc       | OAuth 2.0 Authorization Code flow     |
| `oidc_client_credentials` | oidc       | OAuth 2.0 Client Credentials flow     |
| `vmanage_session`         | session    | Session-based authentication (cookie) |
| `csrf_token`              | csrf       | CSRF token validation                 |
| `system_api_key`          | api_key    | System administration API key         |

### Endpoint Configuration (`endpoints.json`)

Defines the API endpoints, their authentication requirements, conditional logic, and response behavior.

#### Endpoint Structure Overview

Each endpoint in the `endpoints.json` file follows this structure:

```json
{
    "endpoints": [
        {
            "name": "Endpoint Display Name",
            "method": "GET|POST|PUT|DELETE|PATCH",
            "path": "/api/path/{param}",
            "tag": "Category",
            "authentication": ["auth_method1", "auth_method2"],
            "persistence": {
                "entity_name": "entity_type",
                "action": "create|retrieve|update|delete|list"
            },
            "form_parameters": [...],
            "request_body_schema": {...},
            "responses": [...]
        }
    ]
}
```

**Core Endpoint Properties:**

| Property              | Type   | Description                                        | Required |
| --------------------- | ------ | -------------------------------------------------- | -------- |
| `name`                | string | Human-readable endpoint name (for documentation)   | ❌       |
| `method`              | string | HTTP method (GET, POST, PUT, DELETE, PATCH)        | ✅       |
| `path`                | string | URL path with optional `{parameters}`              | ✅       |
| `tag`                 | string | Category for grouping in OpenAPI documentation     | ❌       |
| `authentication`      | array  | List of authentication methods required            | ❌       |
| `persistence`         | object | Redis persistence configuration                    | ❌       |
| `form_parameters`     | array  | Form data parameters (for POST with form encoding) | ❌       |
| `request_body_schema` | object | JSON Schema for request body validation            | ❌       |
| `responses`           | array  | Conditional response definitions                   | ✅       |

#### Basic Endpoint Example

Simple GET endpoint with path parameters:

```json
{
  "method": "GET",
  "path": "/items/{item_id}",
  "tag": "Items",
  "authentication": ["api_key"],
  "responses": [
    {
      "path_conditions": {
        "item_id": 123
      },
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

**Key Features:**

- Path parameter `{item_id}` extracted from URL
- API key authentication required
- Conditional response when `item_id` equals 123
- Tagged as "Items" in OpenAPI docs

#### Authentication Configuration

Endpoints can require one or more authentication methods:

```json
{
    "method": "POST",
    "path": "/users",
    "authentication": [
        "basic_auth",
        "oidc_auth_code"
    ],
    "responses": [...]
}
```

**Authentication Options:**

- `api_key` - API key in header (X-API-Key)
- `basic_auth` - HTTP Basic authentication
- `oidc_auth_code` - OAuth 2.0 Authorization Code flow
- `oidc_client_credentials` - OAuth 2.0 Client Credentials flow
- `vmanage_session` - Session-based authentication (vManage profile)
- `csrf_token` - CSRF token validation (vManage profile)

**Multiple Authentication:** When multiple methods are listed, they act as alternatives (OR logic) - any one valid method allows access.

#### Conditional Responses

Define different responses based on request conditions:

##### Body Conditions

Match against request body content:

```json
{
  "method": "POST",
  "path": "/users",
  "responses": [
    {
      "body_conditions": {
        "role": "admin",
        "action": "create"
      },
      "response": {
        "status_code": 201,
        "body": {
          "message": "Admin user created successfully.",
          "user_id": 999
        }
      }
    },
    {
      "body_conditions": {
        "role": "guest"
      },
      "response": {
        "status_code": 201,
        "body": {
          "message": "Guest user created with limited permissions.",
          "user_id": 100
        }
      }
    },
    {
      "body_conditions": null,
      "response": {
        "status_code": 400,
        "body": {
          "error": "Bad Request",
          "detail": "Role must be specified."
        }
      }
    }
  ]
}
```

**Matching Logic:**

- Responses are evaluated in order
- First matching condition wins
- `null` conditions act as catch-all/default
- All specified fields must match for condition to succeed

##### Path Conditions

Match against URL path parameters:

```json
{
  "method": "GET",
  "path": "/items/{item_id}",
  "responses": [
    {
      "path_conditions": {
        "item_id": 123
      },
      "response": {
        "status_code": 200,
        "body": {
          "message": "Special item 123",
          "special": true
        }
      }
    },
    {
      "path_conditions": null,
      "response": {
        "status_code": 200,
        "body": {
          "message": "Generic item",
          "item_id": "{item_id}"
        }
      }
    }
  ]
}
```

#### Persistence Configuration

Enable Redis-backed CRUD operations:

```json
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
      "name": { "type": "string" },
      "price": { "type": "number" }
    },
    "required": ["name", "price"]
  },
  "responses": [
    {
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
}
```

**Persistence Actions:**

| Action     | Description                     | HTTP Method |
| ---------- | ------------------------------- | ----------- |
| `create`   | Store new entity in Redis       | POST        |
| `retrieve` | Get entity by ID from Redis     | GET         |
| `update`   | Update existing entity in Redis | PUT/PATCH   |
| `delete`   | Remove entity from Redis        | DELETE      |
| `list`     | List all entities of type       | GET (no ID) |

**Entity Storage:** Entities are stored in Redis with keys like `{entity_name}:{entity_id}` and automatically support CRUD operations.

#### Form Parameters

Handle form-encoded POST requests (common in authentication flows):

```json
{
  "method": "POST",
  "path": "/j_security_check",
  "form_parameters": [
    {
      "name": "j_username",
      "type": "string",
      "required": true,
      "description": "Username for authentication"
    },
    {
      "name": "j_password",
      "type": "string",
      "required": true,
      "description": "Password for authentication"
    }
  ],
  "responses": [
    {
      "body_conditions": {
        "j_username": "admin",
        "j_password": "admin"
      },
      "response": {
        "status_code": 200,
        "headers": {
          "Set-Cookie": "JSESSIONID=${auth.vmanage_session.random_session.session_id}; Path=/; HttpOnly"
        },
        "body": {}
      }
    },
    {
      "response": {
        "status_code": 401,
        "body": {
          "error": "Invalid credentials"
        }
      }
    }
  ]
}
```

**Form Parameter Properties:**

- `name` - Form field name
- `type` - Data type (string, number, boolean)
- `required` - Whether field is mandatory
- `description` - Field documentation
- `example` - Example value

**Content-Type:** Automatically handles `application/x-www-form-urlencoded` and validates form parameters.

#### Request Body Schema

Define JSON Schema for request body validation:

```json
{
    "method": "POST",
    "path": "/template/device",
    "request_body_schema": {
        "type": "object",
        "properties": {
            "templateName": {
                "type": "string",
                "description": "Name of the device template",
                "example": "Branch-Router-Template"
            },
            "deviceType": {
                "type": "string",
                "enum": ["vedge-C8000V", "vedge-ISR4331"],
                "example": "vedge-C8000V"
            },
            "templateDefinition": {
                "type": "object",
                "properties": {
                    "system": {
                        "type": "object",
                        "properties": {
                            "host-name": {"type": "string"},
                            "system-ip": {"type": "string"}
                        }
                    }
                }
            }
        },
        "required": ["templateName", "deviceType"],
        "additionalProperties": true
    },
    "responses": [...]
}
```

**Schema Features:**

- Full JSON Schema Draft 7 support
- Type validation (string, number, boolean, array, object)
- Required field enforcement
- Enum constraints
- Nested object schemas
- OpenAPI documentation generation

#### Response Configuration

Define response structure with headers and body:

```json
{
  "responses": [
    {
      "body_conditions": null,
      "response": {
        "status_code": 200,
        "headers": {
          "Content-Type": "application/json",
          "X-Custom-Header": "Custom Value",
          "X-Request-ID": "{{uuid}}"
        },
        "body": {
          "status": "success",
          "data": {
            "timestamp": "{{timestamp}}",
            "correlation_id": "{{uuid}}"
          }
        }
      }
    }
  ]
}
```

**Response Properties:**

| Property      | Type    | Description                      | Required |
| ------------- | ------- | -------------------------------- | -------- |
| `status_code` | integer | HTTP status code (200, 201, etc) | ✅       |
| `headers`     | object  | Custom response headers          | ❌       |
| `body`        | any     | Response body (JSON object)      | ❌       |

#### Dynamic Placeholders

Use placeholders for dynamic content in responses:

##### Authentication Placeholders

Reference session data and authentication state:

```json
{
  "headers": {
    "X-XSRF-TOKEN": "${auth.vmanage_session.random_session.csrf_token}",
    "Set-Cookie": "JSESSIONID=${auth.vmanage_session.random_session.session_id}; Path=/; HttpOnly"
  }
}
```

**Syntax:** `${auth.<auth_method>.<session_type>.<field>}`

- `auth_method` - Authentication method name from auth.json
- `session_type` - Session type (e.g., random_session)
- `field` - Specific field (session_id, csrf_token, etc.)

##### Template Variables

Built-in template variables for dynamic values:

```json
{
  "body": {
    "timestamp": "{{timestamp}}",
    "uuid": "{{uuid}}",
    "correlation_id": "{{random_uuid}}",
    "current_time": "{{current_timestamp}}"
  }
}
```

**Available Variables:**

- `{{timestamp}}` - Realistic recent timestamp (ISO 8601 format with Z suffix)
- `{{date}}` - Realistic recent date (YYYY-MM-DD format)
- `{{unix_timestamp}}` - Realistic recent Unix timestamp (10 digits)
- `{{unix_timestamp_ms}}` - Realistic recent Unix timestamp in milliseconds (13 digits)
- `{{random_uuid}}` - Random UUID v4
- `{{current_timestamp}}` - Current timestamp in ISO 8601 format with Z suffix

#### Complete Examples

##### Example 1: Simple GET with Path Parameters (Basic Profile)

```json
{
  "method": "GET",
  "path": "/items/{item_id}",
  "tag": "Items",
  "authentication": ["api_key"],
  "responses": [
    {
      "path_conditions": {
        "item_id": 123
      },
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

##### Example 2: POST with Persistence (Persistence Profile)

```json
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
      }
    },
    "required": ["name", "price"]
  },
  "responses": [
    {
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
}
```

##### Example 3: Form Authentication (vManage Profile)

```json
{
  "name": "vManage Authentication",
  "method": "POST",
  "path": "/j_security_check",
  "tag": "Authentication",
  "form_parameters": [
    {
      "name": "j_username",
      "type": "string",
      "required": true,
      "description": "Username for authentication"
    },
    {
      "name": "j_password",
      "type": "string",
      "required": true,
      "description": "Password for authentication"
    }
  ],
  "responses": [
    {
      "body_conditions": {
        "j_username": "admin",
        "j_password": "admin"
      },
      "response": {
        "status_code": 200,
        "headers": {
          "Set-Cookie": "JSESSIONID=${auth.vmanage_session.random_session.session_id}; Path=/; HttpOnly",
          "Content-Type": "text/html"
        },
        "body": {}
      }
    },
    {
      "body_conditions": null,
      "response": {
        "status_code": 401,
        "headers": {
          "Content-Type": "application/json"
        },
        "body": {
          "error": "Authentication failed",
          "message": "Invalid username or password"
        }
      }
    }
  ]
}
```

##### Example 4: OIDC Token Endpoint (Persistence Profile)

```json
{
  "method": "POST",
  "path": "/auth/token",
  "tag": "Authentication",
  "responses": [
    {
      "body_conditions": {
        "grant_type": "authorization_code",
        "client_id": "demo-client-id"
      },
      "response": {
        "status_code": 200,
        "body": {
          "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.demo-token",
          "token_type": "Bearer",
          "expires_in": 3600,
          "scope": "read write"
        }
      }
    },
    {
      "body_conditions": {
        "grant_type": "client_credentials",
        "client_id": "service-client-id"
      },
      "response": {
        "status_code": 200,
        "body": {
          "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.service-token",
          "token_type": "Bearer",
          "expires_in": 7200,
          "scope": "service read"
        }
      }
    }
  ]
}
```

##### Example 5: Complex Request Schema (vManage Profile)

```json
{
  "name": "Create Device Template",
  "method": "POST",
  "path": "/dataservice/template/device",
  "authentication": ["vmanage_session", "csrf_token"],
  "tag": "Templates",
  "request_body_schema": {
    "type": "object",
    "properties": {
      "templateName": {
        "type": "string",
        "description": "Name of the device template",
        "example": "Branch-Router-Template"
      },
      "deviceType": {
        "type": "string",
        "enum": ["vedge-C8000V", "vedge-ISR4331", "vsmart", "vbond"],
        "example": "vedge-C8000V"
      },
      "templateDefinition": {
        "type": "object",
        "properties": {
          "system": {
            "type": "object",
            "properties": {
              "host-name": { "type": "string", "example": "{{hostname}}" },
              "system-ip": { "type": "string", "example": "{{system_ip}}" },
              "site-id": { "type": "string", "example": "{{site_id}}" }
            }
          }
        }
      }
    },
    "required": ["templateName", "deviceType", "templateDefinition"],
    "additionalProperties": true
  },
  "responses": [
    {
      "response": {
        "status_code": 201,
        "headers": {
          "Content-Type": "application/json",
          "X-XSRF-TOKEN": "${auth.vmanage_session.random_session.csrf_token}"
        },
        "body": {
          "templateId": "template-12345",
          "templateName": "Branch-Router-Template",
          "status": "created",
          "message": "Device template created successfully"
        }
      }
    }
  ]
}
```

## Template Variables

Mock-and-Roll supports dynamic response generation using template variables in response bodies:

### Built-in Variables

| Variable                | Description                                    | Example                                |
| ----------------------- | ---------------------------------------------- | -------------------------------------- |
| `{{timestamp}}`         | Realistic recent timestamp (ISO 8601 with Z)   | "2025-10-27T14:23:15Z"                 |
| `{{date}}`              | Realistic recent date (YYYY-MM-DD)             | "2025-10-27"                           |
| `{{unix_timestamp}}`    | Realistic recent Unix timestamp (seconds)      | 1729953795                             |
| `{{unix_timestamp_ms}}` | Realistic recent Unix timestamp (milliseconds) | 1729953795000                          |
| `{{random_uuid}}`       | Random UUID v4                                 | "550e8400-e29b-41d4-a716-446655440000" |
| `{{current_timestamp}}` | Current UTC timestamp (ISO 8601 with Z)        | "2025-10-27T14:25:30Z"                 |

### Automatic Timestamp Substitution

Static timestamps in responses are automatically replaced with realistic, recent timestamps:

```json
{
  "response": {
    "body": {
      "created_at": "2025-08-19T10:30:00Z",
      "updated_at": "1724058600"
    }
  }
}
```

The server automatically detects and replaces:

- ISO 8601 timestamps (e.g., `2025-08-19T10:30:00Z`)
- Unix timestamps (10-digit numbers)
- Unix timestamps in milliseconds (13-digit numbers)
- Date strings (e.g., `2025-08-19`)

### Path Parameter Substitution

Path parameters from the URL are automatically available in responses using `{parameter_name}` syntax:

```json
{
  "method": "GET",
  "path": "/items/{item_id}",
  "responses": [
    {
      "response": {
        "status_code": 200,
        "body": {
          "message": "Item requested",
          "item_id": "{item_id}"
        }
      }
    }
  ]
}
```

## Environment Variables

Override configuration settings using environment variables:

| Variable             | Description                      | Default         |
| -------------------- | -------------------------------- | --------------- |
| `MOCK_CONFIG_FOLDER` | Configuration directory path     | `configs/basic` |
| `CONFIG_FOLDER`      | Alternative config path variable | -               |
| `REDIS_HOST`         | Redis server hostname            | `localhost`     |
| `REDIS_PORT`         | Redis server port                | `6379`          |
| `REDIS_DB`           | Redis database number            | `0`             |
| `LOG_LEVEL`          | Logging level                    | `INFO`          |

## Configuration Profiles

### Basic Profile

**Purpose:** Simple mock API for development and testing

**Features:**

- RESTful endpoints
- JSON responses
- API key and Basic authentication
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
- Data persistence (CRUD operations)
- OAuth/OIDC authentication support
- User management
- Session handling

**Use Cases:**

- Integration testing
- Demonstration environments
- Training scenarios

**Requirements:**

- Redis server (5.0+)

### vManage Profile

**Purpose:** Cisco vManage SD-WAN controller simulation

**Features:**

- Form-based authentication workflows
- Session and CSRF token management
- Device management endpoints
- Template configuration
- Policy management
- Network monitoring endpoints
- Realistic SD-WAN data structures

**Use Cases:**

- Network automation development
- SD-WAN training
- Cisco ecosystem integration testing
- vManage API development

### Airgapped Profile

**Purpose:** Mock API for air-gapped/offline environments

**Features:**

- No external CDN dependencies
- Self-contained Swagger UI
- Simple authentication
- Optimized for offline deployment

**Use Cases:**

- Air-gapped environments
- Offline development
- Secure/isolated networks
- Compliance-restricted deployments

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

Add custom headers to responses:

```json
{
  "method": "GET",
  "path": "/api/data",
  "responses": [
    {
      "response": {
        "status_code": 200,
        "headers": {
          "X-Custom-Header": "Custom Value",
          "X-Request-ID": "static-id-123"
        },
        "body": {
          "data": "example"
        }
      }
    }
  ]
}
```

### Error Simulation

Simulate different error conditions using body conditions:

```json
{
  "method": "GET",
  "path": "/api/test",
  "responses": [
    {
      "body_conditions": {
        "error_type": "server"
      },
      "response": {
        "status_code": 500,
        "body": {
          "error": "Internal server error"
        }
      }
    },
    {
      "body_conditions": {
        "error_type": "auth"
      },
      "response": {
        "status_code": 401,
        "body": {
          "error": "Unauthorized"
        }
      }
    },
    {
      "body_conditions": null,
      "response": {
        "status_code": 200,
        "body": {
          "message": "Success"
        }
      }
    }
  ]
}
```

## Validation and Testing

### Test Configuration

Start the server and check for errors:

```bash
# Start server with configuration
./mockctl start myprofile --port 8080

# Check server status
./mockctl list

# View logs for errors
./mockctl search --config myprofile
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

## Next Steps

- **[CLI Commands](user-guide/cli-commands.md)**: Learn advanced CLI usage
- **[Examples](examples/basic-usage.md)**: See configuration examples
- **[Architecture](architecture/overview.md)**: Understand the system design
- **[API Reference](reference/api-reference.md)**: Complete API documentation
