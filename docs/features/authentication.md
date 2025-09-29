# Authentication Methods

Mock-and-Roll supports multiple authentication schemes to simulate real-world API security patterns. Configure different authentication methods for different endpoints and test various security scenarios.

## Supported Authentication Types

### API Key Authentication

The most common authentication method for REST APIs.

#### Header-based API Keys

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

#### Query Parameter API Keys

```json
{
  "query_api_key": {
    "type": "api_key",
    "name": "api_key",
    "location": "query",
    "valid_keys": ["public-key-123", "service-key-456"]
  }
}
```

#### Usage Examples

```bash
# Header-based authentication
curl -H "X-API-Key: demo-api-key-123" \
     http://localhost:8000/api/v1/users

# Query parameter authentication
curl "http://localhost:8000/api/v1/users?api_key=public-key-123"
```

### Bearer Token Authentication

For JWT tokens and OAuth2 access tokens.

#### Configuration

```json
{
  "bearer_token": {
    "type": "http_bearer",
    "valid_tokens": [
      "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.demo-token",
      "simple-bearer-token-123",
      "oauth2-access-token-456"
    ]
  }
}
```

#### Usage Examples

```bash
# Bearer token authentication
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.demo-token" \
     http://localhost:8000/api/v1/protected

# Simple bearer token
curl -H "Authorization: Bearer simple-bearer-token-123" \
     http://localhost:8000/api/v1/data
```

### Basic Authentication

Username and password authentication using HTTP Basic Auth.

#### Configuration

```json
{
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
      },
      {
        "username": "guest",
        "password": "guest123"
      }
    ]
  }
}
```

#### Usage Examples

```bash
# Basic authentication
curl -u admin:secret123 \
     http://localhost:8000/api/v1/admin

# Base64 encoded
curl -H "Authorization: Basic YWRtaW46c2VjcmV0MTIz" \
     http://localhost:8000/api/v1/admin
```

### OAuth2 / OIDC Authentication

Simulate OAuth2 authorization code flow and OpenID Connect.

#### Authorization Code Flow

```json
{
  "oidc_auth_code": {
    "type": "oidc",
    "grant_type": "authorization_code",
    "client_id": "demo-client-id",
    "client_secret": "demo-client-secret",
    "authorization_url": "https://auth.example.com/oauth2/authorize",
    "token_url": "https://auth.example.com/oauth2/token",
    "scopes": ["read", "write", "admin"],
    "valid_tokens": [
      {
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.demo-token",
        "scope": "read write",
        "expires_in": 3600
      },
      {
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.admin-token",
        "scope": "read write admin",
        "expires_in": 7200
      }
    ]
  }
}
```

#### Client Credentials Flow

```json
{
  "oauth2_client_creds": {
    "type": "oauth2",
    "grant_type": "client_credentials",
    "client_id": "service-client-123",
    "client_secret": "service-secret-456",
    "token_url": "https://auth.example.com/oauth2/token",
    "scopes": ["api:read", "api:write"]
  }
}
```

### Session-based Authentication

Cookie-based authentication for web applications.

#### Configuration

```json
{
  "session_auth": {
    "type": "session",
    "session_cookie_name": "session_id",
    "valid_sessions": [
      {
        "session_id": "sess_123456789",
        "user_id": "user_001",
        "role": "admin"
      },
      {
        "session_id": "sess_987654321",
        "user_id": "user_002",
        "role": "user"
      }
    ]
  }
}
```

#### Usage Examples

```bash
# Session cookie authentication
curl -b "session_id=sess_123456789" \
     http://localhost:8000/api/v1/profile

# Set cookie in browser and access Swagger UI
document.cookie = "session_id=sess_123456789"
```

### Multi-Factor Authentication (MFA)

Simulate multi-factor authentication workflows.

#### TOTP (Time-based One-Time Password)

```json
{
  "mfa_totp": {
    "type": "mfa",
    "primary_auth": "basic_auth",
    "secondary_auth": {
      "type": "totp",
      "valid_codes": [
        { "username": "admin", "totp_secret": "JBSWY3DPEHPK3PXP" },
        { "username": "user", "totp_secret": "HXDMVJECJJWSRB3HWIZR4IFUGFTMXBOZ" }
      ]
    }
  }
}
```

#### SMS Verification

```json
{
  "mfa_sms": {
    "type": "mfa",
    "primary_auth": "api_key",
    "secondary_auth": {
      "type": "sms_code",
      "valid_codes": [
        { "phone": "+1234567890", "code": "123456" },
        { "phone": "+0987654321", "code": "654321" }
      ]
    }
  }
}
```

### CSRF Token Protection

Protect against Cross-Site Request Forgery attacks.

#### Configuration

```json
{
  "csrf_protection": {
    "type": "csrf",
    "token_header": "X-CSRF-Token",
    "valid_tokens": ["csrf-token-abc123", "csrf-token-def456", "csrf-token-ghi789"],
    "required_for_methods": ["POST", "PUT", "DELETE"]
  }
}
```

#### Usage Examples

```bash
# Include CSRF token in POST requests
curl -X POST \
     -H "X-CSRF-Token: csrf-token-abc123" \
     -H "Content-Type: application/json" \
     -d '{"name": "New User"}' \
     http://localhost:8000/api/v1/users
```

## Endpoint Authentication Configuration

### Single Authentication Method

Require one specific authentication method:

```json
{
    "method": "GET",
    "path": "/api/users",
    "authentication": ["api_key"],
    "responses": [...]
}
```

### Multiple Authentication Options

Allow multiple authentication methods (OR logic):

```json
{
    "method": "GET",
    "path": "/api/data",
    "authentication": ["api_key", "bearer_token", "basic_auth"],
    "responses": [...]
}
```

### Conditional Authentication

Different authentication requirements based on conditions:

```json
{
    "method": "GET",
    "path": "/api/content/{category}",
    "conditional_authentication": {
        "public": [],                    // No auth for public content
        "premium": ["api_key"],          // API key for premium content
        "admin": ["bearer_token"]        // Bearer token for admin content
    },
    "responses": [...]
}
```

### Multiple Required Authentication (AND logic)

Require multiple authentication methods simultaneously:

```json
{
    "method": "DELETE",
    "path": "/api/admin/users/{id}",
    "authentication": {
        "required": ["bearer_token", "csrf_protection"],
        "logic": "AND"
    },
    "responses": [...]
}
```

## Advanced Authentication Features

### Role-Based Access Control (RBAC)

Define user roles and permissions:

```json
{
  "rbac_auth": {
    "type": "rbac",
    "roles": {
      "admin": {
        "permissions": ["read", "write", "delete", "admin"],
        "valid_tokens": ["admin-token-123"]
      },
      "editor": {
        "permissions": ["read", "write"],
        "valid_tokens": ["editor-token-456"]
      },
      "viewer": {
        "permissions": ["read"],
        "valid_tokens": ["viewer-token-789"]
      }
    }
  }
}
```

### Scoped Authentication

OAuth2-style scopes for fine-grained permissions:

```json
{
  "scoped_auth": {
    "type": "scoped_bearer",
    "valid_tokens": [
      {
        "token": "token-with-user-read",
        "scopes": ["user:read"]
      },
      {
        "token": "token-with-full-access",
        "scopes": ["user:read", "user:write", "admin:all"]
      }
    ]
  }
}
```

Use scoped authentication in endpoints:

```json
{
    "method": "POST",
    "path": "/api/users",
    "authentication": ["scoped_auth"],
    "required_scopes": ["user:write"],
    "responses": [...]
}
```

### Time-based Authentication

Tokens that expire at specific times:

```json
{
  "time_based_auth": {
    "type": "time_bearer",
    "valid_tokens": [
      {
        "token": "temporary-token-123",
        "expires_at": "2025-12-31T23:59:59Z"
      },
      {
        "token": "long-lived-token-456",
        "expires_at": "2026-12-31T23:59:59Z"
      }
    ]
  }
}
```

### IP-based Authentication

Restrict access based on client IP addresses:

```json
{
  "ip_based_auth": {
    "type": "ip_whitelist",
    "allowed_ips": ["192.168.1.0/24", "10.0.0.1", "172.16.0.0/16"],
    "fallback_auth": ["api_key"]
  }
}
```

## Testing Authentication in Swagger UI

Mock-and-Roll's Swagger UI supports interactive authentication testing:

### API Key Testing

1. Open Swagger UI at `http://localhost:8000/docs`
2. Click the "Authorize" button
3. Enter your API key in the appropriate field
4. Test endpoints with authentication

### Bearer Token Testing

1. Click "Authorize" in Swagger UI
2. Select "bearerAuth"
3. Enter your bearer token
4. Execute protected endpoints

### Basic Auth Testing

1. Click "Authorize" in Swagger UI
2. Select "basicAuth"
3. Enter username and password
4. Test authenticated endpoints

### OAuth2 Flow Testing

1. Click "Authorize" in Swagger UI
2. Select OAuth2 authentication
3. Follow the authorization flow
4. Use the returned token for API calls

## Authentication Response Patterns

### Success Responses

Configure different success responses based on authentication:

```json
{
  "responses": [
    {
      "auth_conditions": { "method": "api_key", "key": "admin-key-789" },
      "response": {
        "status_code": 200,
        "body": {
          "access_level": "admin",
          "user_role": "administrator"
        }
      }
    },
    {
      "auth_conditions": { "method": "api_key" },
      "response": {
        "status_code": 200,
        "body": {
          "access_level": "standard",
          "user_role": "user"
        }
      }
    }
  ]
}
```

### Authentication Error Responses

Customize error responses for authentication failures:

```json
{
  "authentication_errors": {
    "missing_auth": {
      "status_code": 401,
      "body": {
        "error": "Authentication required",
        "message": "Please provide valid credentials"
      }
    },
    "invalid_auth": {
      "status_code": 401,
      "body": {
        "error": "Invalid credentials",
        "message": "The provided credentials are not valid"
      }
    },
    "insufficient_permissions": {
      "status_code": 403,
      "body": {
        "error": "Insufficient permissions",
        "message": "Your account does not have permission to access this resource"
      }
    }
  }
}
```

## Best Practices

### Security Best Practices

1. **Use Strong Keys**: Generate cryptographically secure API keys

   ```bash
   # Generate secure API keys
   openssl rand -base64 32
   ```

2. **Rotate Credentials**: Regularly update authentication credentials

   ```json
   {
     "valid_keys": [
       "current-key-123", // Current key
       "previous-key-456" // Previous key for graceful rotation
     ]
   }
   ```

3. **Scope Permissions**: Use the principle of least privilege
   ```json
   {
     "read_only_key": {
       "valid_keys": ["readonly-key-123"],
       "allowed_methods": ["GET"]
     }
   }
   ```

### Development Best Practices

1. **Environment-specific Keys**: Use different keys per environment

   ```bash
   configs/
   ├── development/auth.json    # Development keys
   ├── staging/auth.json        # Staging keys
   └── production/auth.json     # Production-like keys
   ```

2. **Document Authentication**: Clearly document auth requirements

   ```json
   {
     "api_key": {
       "description": "API key for accessing public endpoints",
       "example": "demo-api-key-123"
     }
   }
   ```

3. **Test All Auth Methods**: Verify each authentication method works
   ```bash
   # Test different authentication methods
   ./mockctl test myapi --auth api_key
   ./mockctl test myapi --auth bearer_token
   ./mockctl test myapi --auth basic_auth
   ```

## Troubleshooting Authentication

### Common Issues

**Authentication Method Not Found:**

```bash
# Error: Authentication method 'invalid_key' not found
# Check auth.json for typos in method names
```

**Invalid Credentials:**

```bash
# Check if the provided credentials match auth.json
curl -v -H "X-API-Key: wrong-key" http://localhost:8000/api/users
# Returns 401 Unauthorized
```

**Missing Authentication Header:**

```bash
# Endpoint requires authentication but none provided
curl -v http://localhost:8000/api/protected
# Returns 401 Unauthorized
```

### Debug Authentication

```bash
# Enable authentication debugging
./mockctl start myapi --debug-auth

# View authentication logs
./mockctl search myapi "authentication" --since "10m ago"

# Test specific authentication method
curl -v -H "X-API-Key: demo-key-123" \
     http://localhost:8000/api/users 2>&1 | grep -i auth
```

## Integration Examples

### Frontend Integration

```javascript
// API key authentication
const apiKey = "demo-api-key-123";

fetch("/api/users", {
  headers: {
    "X-API-Key": apiKey,
    "Content-Type": "application/json",
  },
})
  .then(response => response.json())
  .then(data => console.log(data));

// Bearer token authentication
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.demo-token";

fetch("/api/protected", {
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
});
```

### Backend Integration

```python
import requests

# API key authentication
headers = {'X-API-Key': 'demo-api-key-123'}
response = requests.get('http://localhost:8000/api/users', headers=headers)

# Basic authentication
from requests.auth import HTTPBasicAuth
auth = HTTPBasicAuth('admin', 'secret123')
response = requests.get('http://localhost:8000/api/admin', auth=auth)

# Bearer token authentication
headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.demo-token'}
response = requests.get('http://localhost:8000/api/protected', headers=headers)
```

Mock-and-Roll's flexible authentication system allows you to simulate any authentication pattern your application needs, from simple API keys to complex multi-factor authentication workflows.
