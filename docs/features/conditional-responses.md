# Conditional Responses

Mock-and-Roll allows you to return different responses based on request conditions, enabling sophisticated API behavior simulation for testing various scenarios.

## Overview

Conditional responses let you:

- Return different data based on request body content
- Return different data based on URL path parameters
- Simulate error conditions for specific inputs
- Test edge cases and error handling
- Create realistic API behavior patterns

## Supported Condition Types

Mock-and-Roll currently supports two types of conditions:

1. **Body Conditions** - Match against request body JSON fields
2. **Path Conditions** - Match against URL path parameters

## Body Conditions

Match against request body content with exact key-value matching:

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
          "message": "Admin user created successfully",
          "user_id": 999,
          "permissions": ["read", "write", "admin"]
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
          "message": "Guest user created with limited permissions",
          "user_id": 100,
          "permissions": ["read"]
        }
      }
    },
    {
      "body_conditions": null,
      "response": {
        "status_code": 400,
        "body": {
          "error": "Bad Request",
          "detail": "Role must be specified"
        }
      }
    }
  ]
}
```

### Body Condition Matching Rules

- **Exact Match**: All fields in `body_conditions` must match exactly
- **All Fields Required**: Every field specified in conditions must have matching value
- **Order**: Responses are evaluated in order, first match wins
- **Catch-All**: Use `"body_conditions": null` as default/fallback response

### Example: Authentication

```json
{
  "method": "POST",
  "path": "/auth/login",
  "responses": [
    {
      "body_conditions": {
        "username": "admin",
        "password": "admin123"
      },
      "response": {
        "status_code": 200,
        "body": {
          "token": "admin-token-xyz",
          "role": "administrator",
          "expires_in": 3600
        }
      }
    },
    {
      "body_conditions": {
        "username": "user",
        "password": "user123"
      },
      "response": {
        "status_code": 200,
        "body": {
          "token": "user-token-abc",
          "role": "user",
          "expires_in": 1800
        }
      }
    },
    {
      "body_conditions": null,
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

## Path Conditions

Match against URL path parameters with exact value matching:

```json
{
  "method": "GET",
  "path": "/users/{user_id}",
  "responses": [
    {
      "path_conditions": {
        "user_id": "123"
      },
      "response": {
        "status_code": 200,
        "body": {
          "id": "123",
          "name": "John Doe",
          "role": "admin"
        }
      }
    },
    {
      "path_conditions": {
        "user_id": "999"
      },
      "response": {
        "status_code": 404,
        "body": {
          "error": "User not found",
          "message": "User with ID 999 does not exist"
        }
      }
    },
    {
      "path_conditions": null,
      "response": {
        "status_code": 200,
        "body": {
          "id": "{user_id}",
          "name": "Generic User",
          "role": "user"
        }
      }
    }
  ]
}
```

### Path Condition Matching Rules

- **Exact String Match**: Path parameter values are compared as strings
- **Type Coercion**: Numeric path parameters are compared as strings (e.g., `123` matches `"123"`)
- **Multiple Parameters**: Can match multiple path parameters simultaneously
- **Order**: Evaluated in order, first match wins
- **Catch-All**: Use `"path_conditions": null` as default response

### Example: Item Details with Special Cases

```json
{
  "method": "GET",
  "path": "/items/{item_id}",
  "responses": [
    {
      "path_conditions": {
        "item_id": "123"
      },
      "response": {
        "status_code": 200,
        "body": {
          "message": "Special item 123",
          "item_id": "123",
          "special": true,
          "data": {
            "name": "Premium Item",
            "value": 9999
          }
        }
      }
    },
    {
      "path_conditions": null,
      "response": {
        "status_code": 200,
        "body": {
          "message": "Here is the item you requested",
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

## Combining Conditions

You can use both body and path conditions in the same endpoint. Note that only one set of conditions can be active per response rule:

```json
{
  "method": "POST",
  "path": "/users/{user_id}/actions",
  "responses": [
    {
      "path_conditions": {
        "user_id": "admin"
      },
      "response": {
        "status_code": 200,
        "body": {
          "message": "Admin user - all actions allowed"
        }
      }
    },
    {
      "body_conditions": {
        "action": "delete"
      },
      "response": {
        "status_code": 403,
        "body": {
          "error": "Delete action not permitted"
        }
      }
    },
    {
      "body_conditions": null,
      "response": {
        "status_code": 200,
        "body": {
          "message": "Action performed successfully"
        }
      }
    }
  ]
}
```

## Common Patterns

### Error Simulation

Simulate different error scenarios:

```json
{
  "method": "POST",
  "path": "/api/payment",
  "responses": [
    {
      "body_conditions": {
        "card_number": "4000000000000002"
      },
      "response": {
        "status_code": 402,
        "body": {
          "error": "card_declined",
          "message": "Your card was declined"
        }
      }
    },
    {
      "body_conditions": {
        "amount": "0"
      },
      "response": {
        "status_code": 400,
        "body": {
          "error": "invalid_amount",
          "message": "Amount must be greater than 0"
        }
      }
    },
    {
      "body_conditions": null,
      "response": {
        "status_code": 200,
        "body": {
          "transaction_id": "{{random_uuid}}",
          "status": "success"
        }
      }
    }
  ]
}
```

### Status-Based Responses

Return different data based on status:

```json
{
  "method": "GET",
  "path": "/orders/{order_id}",
  "responses": [
    {
      "path_conditions": {
        "order_id": "pending-123"
      },
      "response": {
        "status_code": 200,
        "body": {
          "id": "pending-123",
          "status": "pending",
          "can_cancel": true
        }
      }
    },
    {
      "path_conditions": {
        "order_id": "shipped-456"
      },
      "response": {
        "status_code": 200,
        "body": {
          "id": "shipped-456",
          "status": "shipped",
          "can_cancel": false,
          "tracking_number": "TRACK123456"
        }
      }
    },
    {
      "path_conditions": null,
      "response": {
        "status_code": 404,
        "body": {
          "error": "Order not found"
        }
      }
    }
  ]
}
```

### Role-Based Access

Simulate role-based permissions:

```json
{
  "method": "DELETE",
  "path": "/admin/users/{user_id}",
  "authentication": ["api_key"],
  "responses": [
    {
      "path_conditions": {
        "user_id": "1"
      },
      "response": {
        "status_code": 403,
        "body": {
          "error": "Cannot delete primary admin user"
        }
      }
    },
    {
      "body_conditions": {
        "force": "true"
      },
      "response": {
        "status_code": 200,
        "body": {
          "message": "User deleted (forced)",
          "user_id": "{user_id}"
        }
      }
    },
    {
      "body_conditions": null,
      "response": {
        "status_code": 200,
        "body": {
          "message": "User deleted successfully",
          "user_id": "{user_id}"
        }
      }
    }
  ]
}
```

## Best Practices

### 1. Order Matters

Place more specific conditions first:

```json
{
  "responses": [
    { "body_conditions": { "role": "admin", "action": "delete" }, "response": {...} },
    { "body_conditions": { "role": "admin" }, "response": {...} },
    { "body_conditions": { "action": "delete" }, "response": {...} },
    { "body_conditions": null, "response": {...} }
  ]
}
```

### 2. Always Include a Default

Use `null` conditions as a catch-all:

```json
{
  "responses": [
    { "body_conditions": { "specific": "case" }, "response": {...} },
    { "body_conditions": null, "response": { "status_code": 400, "body": {"error": "Bad request"} } }
  ]
}
```

### 3. Use Realistic Values

Test with realistic data:

```json
{
  "body_conditions": {
    "email": "test@example.com",
    "age": "25"
  }
}
```

### 4. Document Special Cases

Add comments in configuration (via separate docs) for special test cases:

- `user_id: "123"` - Returns premium user
- `user_id: "999"` - Returns 404
- `card_number: "4000000000000002"` - Card declined error

## Limitations

The conditional response system currently does NOT support:

- **Query Parameter Conditions**: Cannot match against URL query strings (e.g., `?limit=10`)
- **Header Conditions**: Cannot match against request headers (e.g., `Accept: application/json`)
- **Regular Expressions**: Only exact string matching is supported
- **Numeric Comparisons**: Cannot use `>`, `<`, `>=`, `<=` operators
- **Complex Logic**: No AND/OR operators or nested conditions
- **Partial Matching**: Cannot match substrings or patterns
- **Type Validation**: No type checking (all values compared as strings)

For more complex scenarios, consider:

- Creating separate endpoints for different cases
- Using Redis persistence with dynamic data
- Combining multiple simple conditions strategically

## See Also

- [Configuration Guide](../configuration.md) - Complete endpoint configuration
- [Template Variables](template-variables.md) - Dynamic response content
- [Authentication](authentication.md) - Authentication methods
- [Persistence](persistence.md) - Stateful API simulation

          }
        }
      },
      {
        "header_conditions": {
          "User-Agent": "^Mobile.*"
        },
        "response": {
          "status_code": 200,
          "body": {
            "mobile_optimized": true,
            "data": "Mobile-friendly response"
          }
        }
      }

  ]
  }

````

## Advanced Condition Matching

### Regular Expression Patterns

Use regex patterns for flexible matching:

```json
{
  "body_conditions": {
    "email": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
    "phone": "^\\+?[1-9]\\d{1,14}$"
  },
  "response": {
    "status_code": 201,
    "body": {
      "message": "Valid email and phone format"
    }
  }
}
````

### Numeric Comparisons

Compare numeric values with operators:

```json
{
  "query_conditions": {
    "age": ">= 18",
    "score": "< 100"
  },
  "response": {
    "status_code": 200,
    "body": {
      "access": "granted",
      "message": "Adult user with valid score"
    }
  }
}
```

### Array and Object Conditions

Match against complex data structures:

```json
{
  "body_conditions": {
    "tags": ["premium", "verified"],
    "metadata.type": "enterprise",
    "settings.notifications": true
  },
  "response": {
    "status_code": 200,
    "body": {
      "tier": "enterprise",
      "features": ["advanced-analytics", "priority-support"]
    }
  }
}
```

### Multiple Condition Logic

#### AND Logic (Default)

All conditions must match:

```json
{
  "body_conditions": {
    "role": "admin",
    "department": "IT",
    "active": true
  },
  "condition_logic": "AND",
  "response": {
    "status_code": 200,
    "body": {
      "access_level": "full"
    }
  }
}
```

#### OR Logic

Any condition can match:

```json
{
  "body_conditions": {
    "role": "admin",
    "permissions": "admin",
    "override": true
  },
  "condition_logic": "OR",
  "response": {
    "status_code": 200,
    "body": {
      "access_granted": true
    }
  }
}
```

#### Complex Logic

Use nested conditions for complex logic:

```json
{
  "conditions": {
    "and": [
      {
        "or": [{ "body.role": "admin" }, { "body.permissions": "admin" }]
      },
      { "body.active": true },
      { "header.X-Request-Source": "internal" }
    ]
  },
  "response": {
    "status_code": 200,
    "body": {
      "message": "Complex condition match"
    }
  }
}
```

## Error Simulation Patterns

### HTTP Error Status Codes

Simulate various error conditions:

```json
{
  "responses": [
    {
      "body_conditions": { "simulate_error": "400" },
      "response": {
        "status_code": 400,
        "body": {
          "error": "Bad Request",
          "message": "Invalid request format"
        }
      }
    },
    {
      "body_conditions": { "simulate_error": "401" },
      "response": {
        "status_code": 401,
        "body": {
          "error": "Unauthorized",
          "message": "Authentication required"
        }
      }
    },
    {
      "body_conditions": { "simulate_error": "403" },
      "response": {
        "status_code": 403,
        "body": {
          "error": "Forbidden",
          "message": "Insufficient permissions"
        }
      }
    },
    {
      "body_conditions": { "simulate_error": "404" },
      "response": {
        "status_code": 404,
        "body": {
          "error": "Not Found",
          "message": "Resource does not exist"
        }
      }
    },
    {
      "body_conditions": { "simulate_error": "500" },
      "response": {
        "status_code": 500,
        "body": {
          "error": "Internal Server Error",
          "message": "Unexpected server error occurred"
        }
      }
    }
  ]
}
```

### Rate Limiting Simulation

Simulate rate limiting based on headers:

```json
{
  "header_conditions": {
    "X-Rate-Test": "exceeded"
  },
  "response": {
    "status_code": 429,
    "headers": {
      "Retry-After": "60",
      "X-Rate-Limit-Remaining": "0",
      "X-Rate-Limit-Reset": "{{timestamp_plus_seconds(60)}}"
    },
    "body": {
      "error": "Rate limit exceeded",
      "message": "Too many requests. Please wait before retrying."
    }
  }
}
```

### Network Error Simulation

Simulate timeouts and connection issues:

```json
{
  "body_conditions": { "simulate": "timeout" },
  "response": {
    "delay_seconds": 30,
    "status_code": 408,
    "body": {
      "error": "Request Timeout",
      "message": "Request took too long to process"
    }
  }
}
```

## Testing Scenarios

### A/B Testing Simulation

Test different response variations:

```json
{
  "responses": [
    {
      "header_conditions": {
        "X-AB-Test": "variant-a"
      },
      "response": {
        "status_code": 200,
        "body": {
          "variant": "A",
          "message": "Welcome to our new design!",
          "features": ["feature1", "feature2"]
        }
      }
    },
    {
      "header_conditions": {
        "X-AB-Test": "variant-b"
      },
      "response": {
        "status_code": 200,
        "body": {
          "variant": "B",
          "message": "Check out our enhanced experience!",
          "features": ["feature1", "feature3", "feature4"]
        }
      }
    },
    {
      "response": {
        "status_code": 200,
        "body": {
          "variant": "control",
          "message": "Standard experience",
          "features": ["feature1"]
        }
      }
    }
  ]
}
```

### User Role Testing

Test different user permission levels:

```json
{
  "responses": [
    {
      "body_conditions": { "user_type": "premium" },
      "response": {
        "status_code": 200,
        "body": {
          "data": "Premium content with exclusive features",
          "access_level": "premium",
          "features": ["advanced-analytics", "priority-support", "custom-reports"]
        }
      }
    },
    {
      "body_conditions": { "user_type": "standard" },
      "response": {
        "status_code": 200,
        "body": {
          "data": "Standard content",
          "access_level": "standard",
          "features": ["basic-analytics"]
        }
      }
    },
    {
      "body_conditions": { "user_type": "trial" },
      "response": {
        "status_code": 200,
        "body": {
          "data": "Limited trial content",
          "access_level": "trial",
          "trial_days_remaining": "{{random_int(1, 30)}}",
          "features": ["basic-preview"]
        }
      }
    }
  ]
}
```

### Environment-Specific Responses

Different responses for different environments:

```json
{
  "responses": [
    {
      "header_conditions": {
        "X-Environment": "development"
      },
      "response": {
        "status_code": 200,
        "body": {
          "environment": "development",
          "debug_info": {
            "server": "dev-server-01",
            "version": "1.0.0-dev",
            "timestamp": "{{timestamp}}"
          },
          "data": "Development data with debug information"
        }
      }
    },
    {
      "header_conditions": {
        "X-Environment": "production"
      },
      "response": {
        "status_code": 200,
        "body": {
          "environment": "production",
          "data": "Production data"
        }
      }
    }
  ]
}
```

## Dynamic Response Content

### Template Variables in Conditional Responses

Use template variables that change based on conditions:

```json
{
  "body_conditions": { "priority": "high" },
  "response": {
    "status_code": 200,
    "body": {
      "ticket_id": "{{random_uuid}}",
      "priority": "high",
      "estimated_resolution": "{{timestamp_plus_hours(2)}}",
      "assigned_agent": "Senior Agent {{random_int(1, 5)}}"
    }
  }
}
```

### Request Data Reflection

Echo back request data in responses:

```json
{
  "response": {
    "status_code": 201,
    "body": {
      "id": "{{random_uuid}}",
      "created_user": {
        "name": "{{request.name}}",
        "email": "{{request.email}}",
        "department": "{{request.department}}"
      },
      "created_at": "{{timestamp}}",
      "status": "active"
    }
  }
}
```

## Condition Evaluation Order

Responses are evaluated in the order they appear in the configuration. The first matching condition wins:

```json
{
  "responses": [
    // Most specific conditions first
    {
      "body_conditions": {
        "role": "admin",
        "department": "IT",
        "action": "delete"
      },
      "response": { "status_code": 200, "body": { "access": "granted" } }
    },
    // Less specific conditions
    {
      "body_conditions": { "role": "admin" },
      "response": { "status_code": 200, "body": { "access": "limited" } }
    },
    // Default fallback (no conditions)
    {
      "response": { "status_code": 403, "body": { "access": "denied" } }
    }
  ]
}
```

## Best Practices

### 1. Order Conditions by Specificity

Place more specific conditions before general ones:

```json
{
  "responses": [
    // Specific: admin user from IT department
    {
      "body_conditions": { "role": "admin", "department": "IT" },
      "response": { "message": "Full IT admin access" }
    },
    // General: any admin user
    {
      "body_conditions": { "role": "admin" },
      "response": { "message": "General admin access" }
    },
    // Default: regular user
    {
      "response": { "message": "Standard user access" }
    }
  ]
}
```

### 2. Use Meaningful Error Messages

Provide clear, actionable error messages:

```json
{
  "body_conditions": { "age": "< 18" },
  "response": {
    "status_code": 400,
    "body": {
      "error": "AGE_RESTRICTION",
      "message": "User must be at least 18 years old to create an account",
      "required_age": 18,
      "provided_age": "{{request.age}}"
    }
  }
}
```

### 3. Test Edge Cases

Create conditions for boundary values and edge cases:

```json
{
  "responses": [
    // Empty string
    {
      "body_conditions": { "name": "" },
      "response": { "status_code": 400, "body": { "error": "Name cannot be empty" } }
    },
    // Very long string
    {
      "body_conditions": { "name": ".{256,}" },
      "response": { "status_code": 400, "body": { "error": "Name too long (max 255 characters)" } }
    },
    // Special characters
    {
      "body_conditions": { "name": ".*[<>\"'].*" },
      "response": { "status_code": 400, "body": { "error": "Name contains invalid characters" } }
    }
  ]
}
```

### 4. Document Response Scenarios

Add comments or descriptions to explain response conditions:

```json
{
  "responses": [
    {
      "description": "Success response for valid admin users",
      "body_conditions": { "role": "admin", "active": true },
      "response": { "status_code": 200, "body": { "access": "granted" } }
    },
    {
      "description": "Error response for inactive admin accounts",
      "body_conditions": { "role": "admin", "active": false },
      "response": { "status_code": 403, "body": { "error": "Account deactivated" } }
    }
  ]
}
```

## Testing Conditional Responses

### Using curl

Test different conditions with curl:

```bash
# Test admin role condition
curl -X POST \
     -H "Content-Type: application/json" \
     -H "X-API-Key: demo-key-123" \
     -d '{"role": "admin", "name": "John Doe"}' \
     http://localhost:8000/api/users

# Test user role condition
curl -X POST \
     -H "Content-Type: application/json" \
     -H "X-API-Key: demo-key-123" \
     -d '{"role": "user", "name": "Jane Smith"}' \
     http://localhost:8000/api/users

# Test error condition
curl -X POST \
     -H "Content-Type: application/json" \
     -H "X-API-Key: demo-key-123" \
     -d '{"role": "invalid"}' \
     http://localhost:8000/api/users
```

### Automated Testing

Create test scripts to verify all conditions:

```python
import requests
import json

base_url = "http://localhost:8000"
headers = {"X-API-Key": "demo-key-123", "Content-Type": "application/json"}

# Test cases
test_cases = [
    {"role": "admin", "expected_status": 201, "expected_message": "Admin user created"},
    {"role": "user", "expected_status": 201, "expected_message": "Regular user created"},
    {"role": "invalid", "expected_status": 400, "expected_error": "Invalid role specified"}
]

for case in test_cases:
    response = requests.post(
        f"{base_url}/api/users",
        headers=headers,
        data=json.dumps({"role": case["role"], "name": "Test User"})
    )

    assert response.status_code == case["expected_status"]
    print(f"✓ Test passed for role: {case['role']}")
```

## Troubleshooting

### Common Issues

**Condition Not Matching:**

```bash
# Check condition syntax and data types
# String comparison vs numeric comparison
{"age": "18"}    # String match
{"age": 18}      # Numeric match
```

**Response Order Issues:**

```bash
# More specific conditions should come first
# Generic conditions should come last
# Default response should have no conditions
```

**Regular Expression Errors:**

```bash
# Escape special characters properly
{"email": ".*@example\\.com$"}  # Correct
{"email": ".*@example.com$"}    # Incorrect (. matches any character)
```

### Debugging Conditions

```bash
# Enable response debugging
./mockctl start myapi --debug-responses

# Test specific condition
curl -v -X POST \
     -H "Content-Type: application/json" \
     -d '{"debug": true, "role": "admin"}' \
     http://localhost:8000/api/users

# Check response evaluation logs
./mockctl search myapi "condition_evaluation" --since "5m ago"
```

Conditional responses are a powerful feature that enables realistic API behavior simulation, comprehensive testing scenarios, and dynamic content generation based on request characteristics.
