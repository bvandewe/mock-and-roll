# Persistence & Redis Integration

Mock-and-Roll provides optional Redis integration for stateful API simulation, enabling realistic CRUD operations, user sessions, and data persistence across requests.

## Overview

Persistence features allow you to:

- Store and retrieve data across API requests
- Implement realistic CRUD operations
- Maintain user sessions and authentication state
- Create stateful workflows and business processes
- Test data consistency and transaction scenarios

## Redis Configuration

### Setup Redis

Mock-and-Roll supports Redis for data persistence:

```bash
# Install Redis locally
# macOS
brew install redis
redis-server

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:alpine
```

### Environment Configuration

Configure Redis connection through environment variables:

```bash
# Redis connection settings
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
export REDIS_DB="0"
export REDIS_PASSWORD=""  # Optional

# Start server with persistence profile
./mockctl start persistence
```

### Docker Compose Setup

Use the included Docker Compose for Redis:

```yaml
# docker-compose.yml
version: "3.8"
services:
  mock-server:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - redis
    environment:
      - REDIS_HOST=redis
      - CONFIG_NAME=persistence

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

```bash
# Start with Redis
docker-compose up -d
```

## Persistence Configuration

### Enable Persistence in Endpoints

Add persistence configuration to your endpoints:

```json
{
  "method": "POST",
  "path": "/users",
  "tag": "User Management",
  "authentication": ["api_key"],
  "persistence": {
    "entity_name": "users",
    "action": "create"
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
```

### CRUD Operations

#### Create (POST)

Store new entities in Redis:

```json
{
  "method": "POST",
  "path": "/users",
  "persistence": {
    "entity_name": "users",
    "action": "create",
    "key_field": "id",
    "auto_generate_id": true
  },
  "responses": [
    {
      "response": {
        "status_code": 201,
        "body": {
          "id": "{{generated_id}}",
          "name": "{{request.name}}",
          "email": "{{request.email}}",
          "created_at": "{{timestamp}}"
        }
      }
    }
  ]
}
```

#### Read (GET)

Retrieve entities from Redis:

```json
{
  "method": "GET",
  "path": "/users/{user_id}",
  "persistence": {
    "entity_name": "users",
    "action": "read",
    "key_field": "user_id"
  },
  "responses": [
    {
      "response": {
        "status_code": 200,
        "body": "{{stored_entity}}"
      }
    }
  ]
}
```

#### Update (PUT)

Modify existing entities:

```json
{
  "method": "PUT",
  "path": "/users/{user_id}",
  "persistence": {
    "entity_name": "users",
    "action": "update",
    "key_field": "user_id",
    "merge_strategy": "replace"
  },
  "responses": [
    {
      "response": {
        "status_code": 200,
        "body": {
          "id": "{user_id}",
          "name": "{{request.name}}",
          "email": "{{request.email}}",
          "updated_at": "{{timestamp}}"
        }
      }
    }
  ]
}
```

#### Delete (DELETE)

Remove entities from Redis:

```json
{
  "method": "DELETE",
  "path": "/users/{user_id}",
  "persistence": {
    "entity_name": "users",
    "action": "delete",
    "key_field": "user_id"
  },
  "responses": [
    {
      "response": {
        "status_code": 204
      }
    }
  ]
}
```

#### List (GET)

Retrieve multiple entities:

```json
{
  "method": "GET",
  "path": "/users",
  "persistence": {
    "entity_name": "users",
    "action": "list",
    "pagination": {
      "enabled": true,
      "default_limit": 10,
      "max_limit": 100
    }
  },
  "responses": [
    {
      "response": {
        "status_code": 200,
        "body": {
          "users": "{{entity_list}}",
          "total": "{{entity_count}}",
          "pagination": {
            "limit": "{{request.limit}}",
            "offset": "{{request.offset}}",
            "has_more": "{{has_more_entities}}"
          }
        }
      }
    }
  ]
}
```

## Advanced Persistence Features

### Entity Relationships

Define relationships between entities:

```json
{
  "method": "POST",
  "path": "/users/{user_id}/posts",
  "persistence": {
    "entity_name": "posts",
    "action": "create",
    "relationships": {
      "user_id": {
        "entity": "users",
        "field": "user_id",
        "required": true
      }
    }
  },
  "responses": [
    {
      "response": {
        "status_code": 201,
        "body": {
          "id": "{{generated_id}}",
          "user_id": "{user_id}",
          "title": "{{request.title}}",
          "content": "{{request.content}}",
          "created_at": "{{timestamp}}"
        }
      }
    }
  ]
}
```

### Data Validation

Validate data before persistence:

```json
{
  "persistence": {
    "entity_name": "users",
    "action": "create",
    "validation": {
      "required_fields": ["name", "email"],
      "unique_fields": ["email"],
      "field_constraints": {
        "name": {
          "min_length": 1,
          "max_length": 100
        },
        "email": {
          "format": "email"
        }
      }
    }
  }
}
```

### Conditional Persistence

Persist data based on conditions:

```json
{
  "method": "POST",
  "path": "/events",
  "responses": [
    {
      "body_conditions": { "type": "important" },
      "persistence": {
        "entity_name": "important_events",
        "action": "create"
      },
      "response": {
        "status_code": 201,
        "body": { "message": "Important event stored" }
      }
    },
    {
      "persistence": {
        "entity_name": "regular_events",
        "action": "create"
      },
      "response": {
        "status_code": 201,
        "body": { "message": "Regular event stored" }
      }
    }
  ]
}
```

### TTL (Time To Live)

Set expiration times for entities:

```json
{
  "persistence": {
    "entity_name": "sessions",
    "action": "create",
    "ttl": 3600, // Expire after 1 hour
    "key_field": "session_id"
  }
}
```

## User Session Management

### Session Creation

Create and store user sessions:

```json
{
  "method": "POST",
  "path": "/auth/login",
  "persistence": {
    "entity_name": "sessions",
    "action": "create",
    "ttl": 86400 // 24 hours
  },
  "responses": [
    {
      "body_conditions": {
        "username": "admin",
        "password": "secret123"
      },
      "response": {
        "status_code": 200,
        "body": {
          "session_id": "{{generated_id}}",
          "user_id": "admin",
          "expires_at": "{{timestamp_plus_seconds(86400)}}",
          "permissions": ["read", "write", "admin"]
        }
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

### Session Validation

Validate sessions for protected endpoints:

```json
{
  "method": "GET",
  "path": "/api/profile",
  "authentication": ["session_auth"],
  "persistence": {
    "entity_name": "sessions",
    "action": "read",
    "key_field": "session_id"
  },
  "responses": [
    {
      "response": {
        "status_code": 200,
        "body": {
          "user": "{{session_data.user_id}}",
          "permissions": "{{session_data.permissions}}"
        }
      }
    }
  ]
}
```

### Session Cleanup

Remove expired or logged-out sessions:

```json
{
  "method": "POST",
  "path": "/auth/logout",
  "persistence": {
    "entity_name": "sessions",
    "action": "delete",
    "key_field": "session_id"
  },
  "responses": [
    {
      "response": {
        "status_code": 200,
        "body": {
          "message": "Logged out successfully"
        }
      }
    }
  ]
}
```

## Data Consistency Patterns

### Atomic Operations

Perform multiple operations atomically:

```json
{
  "method": "POST",
  "path": "/orders",
  "persistence": {
    "atomic": true,
    "operations": [
      {
        "entity_name": "orders",
        "action": "create",
        "data": {
          "id": "{{generated_id}}",
          "user_id": "{{request.user_id}}",
          "total": "{{request.total}}"
        }
      },
      {
        "entity_name": "inventory",
        "action": "update",
        "key_field": "product_id",
        "data": {
          "quantity": "{{current.quantity - request.quantity}}"
        }
      }
    ]
  }
}
```

### Optimistic Locking

Implement optimistic concurrency control:

```json
{
  "method": "PUT",
  "path": "/users/{user_id}",
  "persistence": {
    "entity_name": "users",
    "action": "update",
    "optimistic_lock": {
      "version_field": "version",
      "expected_version": "{{request.version}}"
    }
  },
  "responses": [
    {
      "response": {
        "status_code": 200,
        "body": {
          "id": "{user_id}",
          "version": "{{incremented_version}}",
          "updated_at": "{{timestamp}}"
        }
      }
    }
  ]
}
```

### Transaction Rollback

Handle errors with rollback support:

```json
{
  "persistence": {
    "transaction": true,
    "rollback_on_error": true,
    "operations": [
      { "entity_name": "users", "action": "create" },
      { "entity_name": "profiles", "action": "create" },
      { "entity_name": "permissions", "action": "create" }
    ]
  }
}
```

## Cache Management

### System Cache Endpoints

Mock-and-Roll provides built-in cache management endpoints:

```bash
# Clear all cached data
curl -X DELETE \
     -H "X-System-Key: system-admin-key" \
     http://localhost:8000/system/cache

# Clear specific entity cache
curl -X DELETE \
     -H "X-System-Key: system-admin-key" \
     http://localhost:8000/system/cache/users

# Get cache statistics
curl -H "X-System-Key: system-admin-key" \
     http://localhost:8000/system/cache/stats
```

### Manual Cache Control

Control caching behavior in endpoints:

```json
{
  "persistence": {
    "entity_name": "users",
    "action": "read",
    "cache": {
      "enabled": true,
      "ttl": 300, // 5 minutes
      "key_prefix": "user_cache"
    }
  }
}
```

## Data Seeding

### Initial Data Setup

Seed Redis with initial data:

```json
{
  "system": {
    "data_seeding": {
      "enabled": true,
      "entities": {
        "users": [
          {
            "id": "user_001",
            "name": "Admin User",
            "email": "admin@example.com",
            "role": "admin"
          },
          {
            "id": "user_002",
            "name": "Test User",
            "email": "test@example.com",
            "role": "user"
          }
        ],
        "products": [
          {
            "id": "prod_001",
            "name": "Sample Product",
            "price": 99.99,
            "inventory": 100
          }
        ]
      }
    }
  }
}
```

### Programmatic Seeding

Seed data through API endpoints:

```bash
# Seed users
curl -X POST \
     -H "X-System-Key: system-admin-key" \
     -H "Content-Type: application/json" \
     -d '{"entities": {"users": [{"id": "1", "name": "John"}]}}' \
     http://localhost:8000/system/seed

# Clear and reseed
curl -X POST \
     -H "X-System-Key: system-admin-key" \
     http://localhost:8000/system/reseed
```

## Monitoring and Debugging

### Redis Connection Status

Check Redis connectivity:

```bash
# System health with Redis status
curl -H "X-System-Key: system-admin-key" \
     http://localhost:8000/system/health

# Example response:
{
    "status": "healthy",
    "redis": {
        "connected": true,
        "version": "6.2.0",
        "memory_usage": "1.2MB"
    }
}
```

### Data Inspection

Inspect stored data:

```bash
# List all entities
curl -H "X-System-Key: system-admin-key" \
     http://localhost:8000/system/data

# Get specific entity data
curl -H "X-System-Key: system-admin-key" \
     http://localhost:8000/system/data/users

# Search entities
curl -H "X-System-Key: system-admin-key" \
     "http://localhost:8000/system/data/users?search=admin"
```

### Persistence Logging

Enable persistence debugging:

```bash
# Start with persistence debugging
./mockctl start persistence --debug-persistence

# View persistence logs
./mockctl search persistence "redis" --since "10m ago"
```

## Performance Considerations

### Connection Pooling

Redis connection pooling is handled automatically:

```python
# Configuration in Redis client
{
    "redis": {
        "connection_pool": {
            "max_connections": 20,
            "retry_on_timeout": true,
            "socket_keepalive": true
        }
    }
}
```

### Memory Management

Monitor Redis memory usage:

```bash
# Check Redis memory info
redis-cli info memory

# Set memory limits
redis-cli config set maxmemory 100mb
redis-cli config set maxmemory-policy allkeys-lru
```

### Batch Operations

Use batch operations for efficiency:

```json
{
    "persistence": {
        "batch_operation": true,
        "entities": [
            {"entity_name": "users", "action": "create", "data": {...}},
            {"entity_name": "users", "action": "create", "data": {...}},
            {"entity_name": "users", "action": "create", "data": {...}}
        ]
    }
}
```

## Best Practices

### 1. **Key Naming Convention**

Use consistent key naming patterns:

```json
{
  "persistence": {
    "key_pattern": "myapi:users:{user_id}",
    "index_patterns": {
      "by_email": "myapi:users:email:{email}",
      "by_role": "myapi:users:role:{role}"
    }
  }
}
```

### 2. **Error Handling**

Handle Redis connection failures gracefully:

```json
{
  "persistence": {
    "error_handling": {
      "on_connection_failure": "fallback_response",
      "on_data_not_found": "return_404",
      "on_validation_error": "return_400"
    }
  }
}
```

### 3. **Data Backup**

Regularly backup Redis data:

```bash
# Manual backup
redis-cli bgsave

# Automated backup script
./scripts/backup-redis-data.sh
```

### 4. **Testing with Persistence**

Test persistence features thoroughly:

```python
import requests
import json

# Test CRUD operations
def test_user_crud():
    base_url = "http://localhost:8000"
    headers = {"X-API-Key": "demo-key-123", "Content-Type": "application/json"}

    # Create user
    user_data = {"name": "Test User", "email": "test@example.com"}
    response = requests.post(f"{base_url}/users", headers=headers, json=user_data)
    assert response.status_code == 201
    user_id = response.json()["id"]

    # Read user
    response = requests.get(f"{base_url}/users/{user_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test User"

    # Update user
    update_data = {"name": "Updated User"}
    response = requests.put(f"{base_url}/users/{user_id}", headers=headers, json=update_data)
    assert response.status_code == 200

    # Delete user
    response = requests.delete(f"{base_url}/users/{user_id}", headers=headers)
    assert response.status_code == 204

    # Verify deletion
    response = requests.get(f"{base_url}/users/{user_id}", headers=headers)
    assert response.status_code == 404
```

## Troubleshooting

### Common Issues

**Redis Connection Failed:**

```bash
# Check Redis server status
redis-cli ping
# Should return PONG

# Check connection settings
echo $REDIS_HOST
echo $REDIS_PORT
```

**Data Not Persisting:**

```bash
# Verify persistence configuration
./mockctl validate-config persistence

# Check Redis data
redis-cli keys "*"
redis-cli get "myapi:users:123"
```

**Memory Issues:**

```bash
# Check Redis memory usage
redis-cli info memory

# Clear cache if needed
curl -X DELETE -H "X-System-Key: system-admin-key" \
     http://localhost:8000/system/cache
```

### Debug Commands

```bash
# Debug persistence operations
./mockctl start persistence --debug-persistence --verbose

# Monitor Redis operations
redis-cli monitor

# Check logs for persistence errors
./mockctl search persistence "persistence_error" --since "1h ago"
```

Redis integration enables Mock-and-Roll to provide sophisticated, stateful API simulation that closely mimics real-world application behavior and data persistence patterns.
