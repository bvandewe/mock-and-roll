# Template Variables

Mock-and-Roll supports dynamic template variables in responses for generating realistic, varied data without hardcoding static values.

## Overview

Template variables enable:

- Dynamic timestamp generation
- Unique identifier creation
- Authentication placeholder resolution
- Automatic static timestamp replacement
- Path parameter substitution

## Supported Template Variables

### UUID Generation

Generate unique identifiers:

```json
{
  "method": "POST",
  "path": "/users",
  "responses": [
    {
      "response": {
        "status_code": 201,
        "body": {
          "id": "{{random_uuid}}",
          "correlation_id": "{{random_uuid}}"
        }
      }
    }
  ]
}
```

Output example:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "correlation_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
}
```

### Current Timestamp

Get the current UTC timestamp:

```json
{
  "response": {
    "body": {
      "created_at": "{{current_timestamp}}"
    }
  }
}
```

Output example:

```json
{
  "created_at": "2025-10-27T14:30:15Z"
}
```

### Realistic Recent Timestamp

Generate a realistic timestamp (1-30 minutes ago):

```json
{
  "response": {
    "body": {
      "last_updated": "{{timestamp}}"
    }
  }
}
```

Output example:

```json
{
  "last_updated": "2025-10-27T14:15:42Z"
}
```

### Realistic Recent Date

Generate a realistic date (1-7 days ago):

```json
{
  "response": {
    "body": {
      "last_login": "{{date}}"
    }
  }
}
```

Output example:

```json
{
  "last_login": "2025-10-25"
}
```

### Unix Timestamps

Generate realistic Unix timestamps:

```json
{
  "response": {
    "body": {
      "timestamp_seconds": "{{unix_timestamp}}",
      "timestamp_milliseconds": "{{unix_timestamp_ms}}"
    }
  }
}
```

Output example:

```json
{
  "timestamp_seconds": "1729953795",
  "timestamp_milliseconds": "1729953795000"
}
```

## Path Parameter Substitution

URL path parameters are automatically available in responses using `{parameter_name}` syntax:

```json
{
  "method": "GET",
  "path": "/users/{user_id}/posts/{post_id}",
  "responses": [
    {
      "response": {
        "status_code": 200,
        "body": {
          "user_id": "{user_id}",
          "post_id": "{post_id}",
          "retrieved_at": "{{timestamp}}"
        }
      }
    }
  ]
}
```

Request: `GET /users/123/posts/456`

Response:

```json
{
  "user_id": "123",
  "post_id": "456",
  "retrieved_at": "2025-10-27T14:20:15Z"
}
```

## Automatic Timestamp Replacement

The server automatically detects and replaces static timestamps in responses with realistic recent values:

```json
{
  "response": {
    "body": {
      "data": {
        "created_at": "2025-08-19T10:30:00Z",
        "timestamp": "1724058600",
        "date": "2025-08-19"
      }
    }
  }
}
```

These static values are automatically replaced with recent, realistic timestamps during response generation.

**Detected Patterns:**

- ISO 8601 timestamps: `YYYY-MM-DDTHH:MM:SSZ`
- Unix timestamps (10 digits): `1724058600`
- Unix timestamps in milliseconds (13 digits): `1724058600000`
- Date strings: `YYYY-MM-DD`

## Authentication Placeholders

Reference session data and authentication state using special placeholders:

```json
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
        "body": {
          "token": "${auth.vmanage_session.random_session.csrf_token}"
        }
      }
    }
  ]
}
```

**Placeholder Syntax:** `${auth.<method>.<selector>.<field>}`

- `method` - Authentication method name from auth.json
- `selector` - Session selector (e.g., `random_session`, `current_session`)
- `field` - Field to extract (e.g., `session_id`, `csrf_token`, `username`)

### Available Placeholders

For `vmanage_session` authentication:

- `${auth.vmanage_session.random_session.session_id}` - Random session ID
- `${auth.vmanage_session.random_session.csrf_token}` - CSRF token for random session
- `${auth.vmanage_session.random_session.username}` - Username for random session
- `${auth.vmanage_session.current_session.csrf_token}` - CSRF token for current request session

For `api_key` authentication:

- `${auth.api_key.random_key}` - Random API key from valid_keys

For `csrf_token` authentication:

- `${auth.csrf_token.random_key}` - Random CSRF token from valid_keys

## Complete Example

Combining multiple template features:

```json
{
  "method": "POST",
  "path": "/devices/{device_id}",
  "authentication": ["vmanage_session", "csrf_token"],
  "responses": [
    {
      "response": {
        "status_code": 200,
        "headers": {
          "Content-Type": "application/json",
          "X-XSRF-TOKEN": "${auth.vmanage_session.random_session.csrf_token}"
        },
        "body": {
          "device_id": "{device_id}",
          "transaction_id": "{{random_uuid}}",
          "timestamp": "{{current_timestamp}}",
          "last_updated": "{{timestamp}}",
          "session_info": {
            "session_id": "${auth.vmanage_session.random_session.session_id}",
            "user": "${auth.vmanage_session.random_session.username}"
          }
        }
      }
    }
  ]
}
```

## Best Practices

1. **Use Realistic Timestamps**: Prefer `{{timestamp}}` and `{{date}}` for more believable test data
2. **Consistent IDs**: Use path parameters `{id}` when echoing request data
3. **Authentication Context**: Use `${auth.*}` placeholders for session-aware responses
4. **Automatic Replacement**: Let the server replace static timestamps automatically

## Limitations

The template system currently does NOT support:

- Request body field access (e.g., `{{request.name}}`)
- Query parameter access (e.g., `{{query.limit}}`)
- Request header access (e.g., `{{headers.user-agent}}`)
- Conditional logic (e.g., `{{if/else}}`)
- Random numbers or strings (e.g., `{{random_int}}`)
- Faker/realistic fake data generation
- Custom functions or calculations
- Array/list generation

For these use cases, use conditional responses with `body_conditions` to match request data and return appropriate static responses.

## See Also

- [Configuration Guide](../configuration.md) - Complete configuration reference
- [Conditional Responses](conditional-responses.md) - Dynamic response patterns
- [Authentication](authentication.md) - Authentication methods and placeholders

````

Request:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30
}
````

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30,
  "created_at": "2024-12-28T10:30:15.123Z"
}
```

### Path Parameter Variables

Use URL path parameters in responses:

```json
{
  "method": "GET",
  "path": "/users/{user_id}/posts/{post_id}",
  "responses": [
    {
      "response": {
        "status_code": 200,
        "body": {
          "user_id": "{user_id}",
          "post_id": "{post_id}",
          "url": "/users/{user_id}/posts/{post_id}",
          "retrieved_at": "{{timestamp}}"
        }
      }
    }
  ]
}
```

### Query Parameter Variables

Access query parameters in responses:

```json
{
  "method": "GET",
  "path": "/search",
  "responses": [
    {
      "response": {
        "body": {
          "query": "{{query.q}}",
          "limit": "{{query.limit}}",
          "offset": "{{query.offset}}",
          "total_results": "{{random_int(0, 1000)}}"
        }
      }
    }
  ]
}
```

Request: `GET /search?q=users&limit=10&offset=0`

Response:

```json
{
  "query": "users",
  "limit": "10",
  "offset": "0",
  "total_results": 347
}
```

## Advanced Template Variables

### Date and Time Calculations

Calculate relative timestamps:

```json
{
  "response": {
    "body": {
      "created_at": "{{timestamp}}",
      "expires_at": "{{timestamp_plus_seconds(3600)}}",
      "one_day_ago": "{{timestamp_minus_days(1)}}",
      "next_week": "{{timestamp_plus_weeks(1)}}",
      "last_month": "{{timestamp_minus_months(1)}}"
    }
  }
}
```

### Conditional Variables

Use conditional logic in templates:

```json
{
  "response": {
    "body": {
      "user_type": "{{if request.role == 'admin' then 'administrator' else 'regular_user'}}",
      "access_level": "{{request.role == 'admin' ? 'full' : 'limited'}}",
      "permissions": "{{request.role == 'admin' ? ['read', 'write', 'delete'] : ['read']}}"
    }
  }
}
```

### Array and List Variables

Generate arrays of data:

```json
{
  "response": {
    "body": {
      "users": [
        {
          "id": "{{random_uuid}}",
          "name": "User {{random_int(1, 1000)}}"
        },
        {
          "id": "{{random_uuid}}",
          "name": "User {{random_int(1, 1000)}}"
        }
      ],
      "tags": "{{random_array(['tag1', 'tag2', 'tag3', 'tag4'], 2)}}",
      "scores": "{{random_int_array(5, 0, 100)}}"
    }
  }
}
```

### Faker Variables

Generate realistic fake data:

```json
{
  "response": {
    "body": {
      "user": {
        "name": "{{fake.name}}",
        "email": "{{fake.email}}",
        "phone": "{{fake.phone_number}}",
        "address": {
          "street": "{{fake.street_address}}",
          "city": "{{fake.city}}",
          "country": "{{fake.country}}"
        },
        "company": "{{fake.company}}",
        "job_title": "{{fake.job}}"
      }
    }
  }
}
```

## Context Variables

### Authentication Context

Access authentication information:

```json
{
  "response": {
    "body": {
      "authenticated_user": "{{auth.user_id}}",
      "auth_method": "{{auth.method}}",
      "permissions": "{{auth.permissions}}",
      "session_id": "{{auth.session_id}}"
    }
  }
}
```

### Server Context

Include server and request metadata:

```json
{
  "response": {
    "body": {
      "server_info": {
        "hostname": "{{server.hostname}}",
        "version": "{{server.version}}",
        "uptime": "{{server.uptime_seconds}}",
        "config": "{{server.config_name}}"
      },
      "request_info": {
        "method": "{{request.method}}",
        "path": "{{request.path}}",
        "client_ip": "{{request.client_ip}}",
        "user_agent": "{{request.user_agent}}",
        "request_id": "{{request.id}}"
      }
    }
  }
}
```

## Persistence Variables

### Stored Data Access

Access data from Redis persistence:

```json
{
  "method": "GET",
  "path": "/users/{user_id}",
  "persistence": {
    "entity_name": "users",
    "action": "read"
  },
  "responses": [
    {
      "response": {
        "body": {
          "id": "{{stored.id}}",
          "name": "{{stored.name}}",
          "email": "{{stored.email}}",
          "last_accessed": "{{timestamp}}",
          "access_count": "{{stored.access_count + 1}}"
        }
      }
    }
  ]
}
```

### Entity Count Variables

Get entity statistics:

```json
{
  "response": {
    "body": {
      "total_users": "{{entity_count('users')}}",
      "active_sessions": "{{entity_count('sessions')}}",
      "recent_orders": "{{entity_count_where('orders', 'status', 'pending')}}"
    }
  }
}
```

## Custom Template Functions

### Mathematical Operations

Perform calculations in templates:

```json
{
  "response": {
    "body": {
      "subtotal": "{{request.quantity * request.price}}",
      "tax": "{{(request.quantity * request.price) * 0.08}}",
      "total": "{{(request.quantity * request.price) * 1.08}}",
      "discount": "{{max(0, request.total - 100)}}"
    }
  }
}
```

### String Manipulation

Transform string values:

```json
{
  "response": {
    "body": {
      "username": "{{request.email.split('@')[0]}}",
      "domain": "{{request.email.split('@')[1]}}",
      "uppercase_name": "{{request.name.upper()}}",
      "formatted_phone": "{{request.phone.replace('-', '')}}",
      "slug": "{{request.title.lower().replace(' ', '-')}}"
    }
  }
}
```

### Data Formatting

Format values for display:

```json
{
  "response": {
    "body": {
      "price": "{{format_currency(request.amount, 'USD')}}",
      "percentage": "{{format_percent(request.score)}}",
      "file_size": "{{format_bytes(request.size)}}",
      "duration": "{{format_duration(request.seconds)}}"
    }
  }
}
```

## Environment-Specific Variables

### Configuration-Based Variables

Use different values per environment:

```json
{
  "response": {
    "body": {
      "api_url": "{{config.base_url}}",
      "environment": "{{config.environment}}",
      "debug_mode": "{{config.debug}}",
      "version": "{{config.version}}"
    }
  }
}
```

### Dynamic Configuration Loading

Load values from configuration:

```json
{
  "template_variables": {
    "api_endpoints": {
      "users": "{{config.endpoints.users_service}}",
      "orders": "{{config.endpoints.orders_service}}"
    },
    "feature_flags": {
      "new_ui": "{{config.features.new_ui_enabled}}",
      "analytics": "{{config.features.analytics_enabled}}"
    }
  }
}
```

## Performance Optimization

### Variable Caching

Cache expensive template calculations:

```json
{
  "template_caching": {
    "enabled": true,
    "cache_duration": 300,
    "cached_variables": ["{{entity_count('users')}}", "{{expensive_calculation()}}", "{{fake.large_dataset}}"]
  }
}
```

### Lazy Evaluation

Compute variables only when needed:

```json
{
  "lazy_variables": {
    "large_report": "{{generate_report()}}",
    "complex_query": "{{database_query()}}"
  }
}
```

## Testing Template Variables

### Variable Testing

Test template rendering:

```bash
# Test template with sample data
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"name": "Test User", "email": "test@example.com"}' \
     http://localhost:8000/api/users

# Verify template variables are resolved
curl http://localhost:8000/api/users/123 | jq '.created_at'
```

### Debug Template Rendering

Enable template debugging:

```json
{
  "template_debugging": {
    "enabled": true,
    "log_variable_resolution": true,
    "show_template_source": true
  }
}
```

Debug output:

```
2024-12-28 10:30:15 DEBUG [TEMPLATE] Resolving variable: {{request.name}}
  Value: "John Doe"
  Source: request.body.name

2024-12-28 10:30:15 DEBUG [TEMPLATE] Resolving variable: {{timestamp}}
  Value: "2024-12-28T10:30:15.123Z"
  Source: system.current_time
```

## Best Practices

### 1. **Variable Naming**

Use descriptive variable names:

```json
{
  "user_creation_timestamp": "{{timestamp}}",
  "user_provided_email": "{{request.email}}",
  "system_generated_id": "{{random_uuid}}"
}
```

### 2. **Error Handling**

Provide fallback values:

```json
{
  "name": "{{request.name || 'Anonymous User'}}",
  "age": "{{request.age || 0}}",
  "country": "{{request.country || 'Unknown'}}"
}
```

### 3. **Type Safety**

Ensure correct data types:

```json
{
  "user_id": "{{int(request.user_id)}}",
  "price": "{{float(request.price)}}",
  "active": "{{bool(request.active)}}"
}
```

### 4. **Performance Considerations**

Optimize template complexity:

```json
{
  // Good: Simple template
  "timestamp": "{{timestamp}}",

  // Avoid: Complex nested operations
  "complex": "{{users.filter(u => u.active).map(u => u.name).join(', ')}}"
}
```

## Common Template Patterns

### API Response Templates

Standard API response structure:

```json
{
  "response": {
    "body": {
      "success": true,
      "data": "{{response_data}}",
      "message": "{{success_message}}",
      "timestamp": "{{timestamp}}",
      "request_id": "{{request.id}}",
      "server": "{{server.hostname}}"
    }
  }
}
```

### Pagination Templates

Paginated response structure:

```json
{
  "response": {
    "body": {
      "data": "{{paginated_data}}",
      "pagination": {
        "page": "{{query.page || 1}}",
        "limit": "{{query.limit || 20}}",
        "total": "{{total_records}}",
        "has_next": "{{has_next_page}}",
        "has_previous": "{{has_previous_page}}"
      }
    }
  }
}
```

### Error Response Templates

Consistent error responses:

```json
{
  "response": {
    "body": {
      "error": true,
      "code": "{{error_code}}",
      "message": "{{error_message}}",
      "details": "{{error_details}}",
      "timestamp": "{{timestamp}}",
      "request_id": "{{request.id}}"
    }
  }
}
```

## Troubleshooting Template Variables

### Common Issues

**Variable Not Resolving:**

```bash
# Check variable syntax
"{{request.name}}"     # Correct
"{{request name}}"     # Incorrect (no dot notation)
"{{request->name}}"    # Incorrect (wrong syntax)
```

**Type Conversion Errors:**

```json
{
  "age": "{{int(request.age)}}", // Convert to integer
  "price": "{{float(request.price)}}", // Convert to float
  "active": "{{bool(request.active)}}" // Convert to boolean
}
```

**Missing Request Data:**

```json
{
  "name": "{{request.name || 'Default Name'}}",
  "optional_field": "{{request.optional_field | default('N/A')}}"
}
```

### Debug Commands

```bash
# Test template rendering
./mockctl test-template myapi --template "{{timestamp}}"

# Debug variable resolution
./mockctl start myapi --debug-templates

# Validate template syntax
./mockctl validate-templates configs/myapi/endpoints.json
```

Template variables provide powerful dynamic content generation capabilities, enabling realistic API simulations that adapt to request data and generate varied, contextual responses.
