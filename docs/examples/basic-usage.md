# Basic Usage Examples

Real-world examples of using Mock-and-Roll for common scenarios.

## Getting Started

This guide shows practical examples of Mock-and-Roll usage for different scenarios.

## Example 1: Simple API Development

### Scenario
You're developing a frontend application and need a backend API for testing.

### Setup

```bash
# Start basic mock server
./mockctl start basic

# Server starts on http://localhost:8000
# API docs available at http://localhost:8000/docs
```

### Test the API

```bash
# Health check
curl http://localhost:8000/api/health

# Response:
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00Z"
}

# Get user data
curl http://localhost:8000/api/users/123

# Response:
{
  "id": "123",
  "name": "User 123", 
  "email": "user123@example.com"
}
```

### Custom Endpoints

Edit `configs/basic/endpoints.json` to add your endpoints:

```json
{
  "endpoints": [
    {
      "path": "/api/products",
      "method": "GET",
      "response": {
        "products": [
          {
            "id": 1,
            "name": "Laptop",
            "price": 999.99
          },
          {
            "id": 2, 
            "name": "Phone",
            "price": 699.99
          }
        ]
      },
      "status_code": 200
    },
    {
      "path": "/api/products/{product_id}",
      "method": "GET",
      "response": {
        "id": "{{path.product_id}}",
        "name": "Product {{path.product_id}}",
        "price": "{{random}}.99",
        "created_at": "{{now}}"
      },
      "status_code": 200
    }
  ]
}
```

Restart the server to apply changes:

```bash
./mockctl stop
./mockctl start basic
```

Test your new endpoints:

```bash
# Get all products
curl http://localhost:8000/api/products

# Get specific product
curl http://localhost:8000/api/products/42
```

## Example 2: Authentication Testing

### Scenario
Test your application's authentication flows with different credentials.

### Configuration

Create a custom authentication setup in `configs/basic/auth.json`:

```json
{
  "methods": {
    "api_key": {
      "enabled": true,
      "header_name": "X-API-Key",
      "valid_keys": [
        "user-key-123",
        "admin-key-456", 
        "test-key-789"
      ]
    }
  },
  "default_method": "api_key",
  "require_auth": false
}
```

Add protected endpoints in `endpoints.json`:

```json
{
  "endpoints": [
    {
      "path": "/api/login",
      "method": "POST",
      "response": {
        "token": "mock-jwt-token-{{uuid}}",
        "expires_in": 3600,
        "user": {
          "id": "{{body.username}}",
          "role": "user"
        }
      },
      "status_code": 200,
      "auth_required": false
    },
    {
      "path": "/api/protected",
      "method": "GET",
      "response": {
        "message": "This is protected content",
        "user_id": "{{headers.x-user-id}}",
        "timestamp": "{{now}}"
      },
      "status_code": 200,
      "auth_required": true
    }
  ]
}
```

### Testing

```bash
# Start server
./mockctl start basic

# Login (no auth required)
curl -X POST -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}' \
  http://localhost:8000/api/login

# Access protected endpoint
curl -H "X-API-Key: user-key-123" \
  http://localhost:8000/api/protected

# Try without authentication (should fail)
curl http://localhost:8000/api/protected
```

## Example 3: Error Scenario Testing

### Scenario
Test how your application handles various error conditions.

### Configuration

Add error simulation endpoints:

```json
{
  "endpoints": [
    {
      "path": "/api/error-demo",
      "method": "GET",
      "conditions": [
        {
          "when": "{{query.error}} == 'server'",
          "response": {
            "error": "Internal server error occurred",
            "code": "INTERNAL_ERROR"
          },
          "status_code": 500
        },
        {
          "when": "{{query.error}} == 'auth'",
          "response": {
            "error": "Authentication required",
            "code": "AUTH_REQUIRED"
          },
          "status_code": 401
        },
        {
          "when": "{{query.error}} == 'not-found'",
          "response": {
            "error": "Resource not found",
            "code": "NOT_FOUND"
          },
          "status_code": 404
        },
        {
          "when": "{{query.error}} == 'rate-limit'",
          "response": {
            "error": "Rate limit exceeded",
            "code": "RATE_LIMIT_EXCEEDED",
            "retry_after": 60
          },
          "status_code": 429
        }
      ],
      "response": {
        "message": "Success response",
        "data": {"test": true}
      },
      "status_code": 200
    }
  ]
}
```

### Testing Different Errors

```bash
# Test success case
curl http://localhost:8000/api/error-demo

# Test server error
curl http://localhost:8000/api/error-demo?error=server

# Test authentication error  
curl http://localhost:8000/api/error-demo?error=auth

# Test not found error
curl http://localhost:8000/api/error-demo?error=not-found

# Test rate limiting
curl http://localhost:8000/api/error-demo?error=rate-limit
```

## Example 4: Data Persistence

### Scenario
Test stateful applications that create, update, and delete data.

### Setup

Start with persistence configuration:

```bash
# Make sure Redis is running
docker run -d -p 6379:6379 redis:alpine

# Start persistence server
./mockctl start persistence
```

### Configuration

The persistence profile includes endpoints that store data in Redis:

```json
{
  "endpoints": [
    {
      "path": "/api/users",
      "method": "POST",
      "response": {
        "id": "{{uuid}}",
        "name": "{{body.name}}",
        "email": "{{body.email}}",
        "created_at": "{{now}}",
        "status": "active"
      },
      "status_code": 201,
      "persistence": {
        "store": true,
        "key": "user:{{response.id}}"
      }
    },
    {
      "path": "/api/users/{user_id}",
      "method": "GET",
      "response": {
        "retrieve_from": "user:{{path.user_id}}"
      },
      "status_code": 200
    }
  ]
}
```

### Testing CRUD Operations

```bash
# Create a user
USER_RESPONSE=$(curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}' \
  http://localhost:8000/api/users)

# Extract user ID from response
USER_ID=$(echo $USER_RESPONSE | jq -r '.id')

# Retrieve the user
curl http://localhost:8000/api/users/$USER_ID

# Create another user
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "Jane Smith", "email": "jane@example.com"}' \
  http://localhost:8000/api/users
```

## Example 5: Log Analysis

### Scenario
Monitor and analyze API usage patterns during testing.

### Setup

```bash
# Start server with some activity
./mockctl start basic

# Generate some test traffic
for i in {1..10}; do
  curl http://localhost:8000/api/users/$i
  curl http://localhost:8000/api/products/$((i*2))
done

# Make some auth requests
curl -H "X-API-Key: invalid-key" http://localhost:8000/api/protected
curl -H "X-API-Key: user-key-123" http://localhost:8000/api/protected
```

### Log Analysis

```bash
# Search for all API requests
./mockctl search "/api"

# Search for user-related requests
./mockctl search "/api/users"

# Search for authentication failures
./mockctl search "401"

# Get JSON output for processing
./mockctl search "/api" --json > api_requests.json

# Analyze with jq
cat api_requests.json | jq '.status_code_summary'
cat api_requests.json | jq '.matched_requests[] | select(.status_code >= 400)'
```

### Performance Analysis

```bash
# Find slow requests (if response time tracking is enabled)
./mockctl search "/api" --json | jq '.matched_requests[] | select(.response_time_ms > 100)'

# Count requests by endpoint
./mockctl search "/api" --json | jq -r '.matched_requests[].path' | sort | uniq -c

# Time-based analysis
./mockctl search "/api" --since "2025-01-01T12:00:00Z" --json
```

## Example 6: CI/CD Integration

### Scenario
Use Mock-and-Roll in automated testing pipelines.

### GitHub Actions Example

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on: [push, pull_request]

jobs:
  integration-test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:alpine
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.11'
          
      - name: Install Mock-and-Roll
        run: |
          pip install -r requirements.txt
          chmod +x mockctl
          
      - name: Start Mock Server
        run: |
          ./mockctl start persistence --port 8080 &
          
          # Wait for server to be ready
          timeout 30 bash -c '
            while ! curl -s http://localhost:8080/api/health; do
              sleep 1
            done
          '
          
      - name: Run Integration Tests
        run: |
          # Your test suite here
          npm test  # or pytest, etc.
          
      - name: Analyze Mock API Usage
        run: |
          ./mockctl search "/api" --json > test_api_usage.json
          
          # Upload as artifact for analysis
          echo "API Requests: $(jq '.total_requests' test_api_usage.json)"
          echo "Status Summary: $(jq '.status_code_summary' test_api_usage.json)"
          
      - name: Cleanup
        run: |
          ./mockctl stop --all
```

### Docker Compose for Testing

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  mock-api:
    build: .
    ports:
      - "8080:8000"
    environment:
      - CONFIG_NAME=persistence
      - REDIS_HOST=redis
    depends_on:
      - redis
      
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
      
  tests:
    build:
      context: .
      dockerfile: Dockerfile.test
    depends_on:
      - mock-api
    environment:
      - API_BASE_URL=http://mock-api:8000
    command: pytest tests/integration/
```

### Test Script Example

```bash
#!/bin/bash
# test-integration.sh

set -e

echo "Starting integration test suite..."

# Start mock server
./mockctl start basic --port 8080 &
SERVER_PID=$!

# Wait for server
echo "Waiting for server to start..."
timeout 30 bash -c 'while ! curl -s http://localhost:8080/api/health; do sleep 1; done'

# Run tests
echo "Running tests..."
pytest tests/integration/ --api-url=http://localhost:8080

# Analyze results
echo "Analyzing API usage..."
./mockctl search "/api" --json | jq '{
  total_requests: .total_requests,
  status_summary: .status_code_summary,
  error_rate: (.status_code_summary | to_entries | map(select(.key | tonumber >= 400)) | map(.value) | add // 0) / .total_requests * 100
}'

# Cleanup
echo "Cleaning up..."
kill $SERVER_PID 2>/dev/null || true
./mockctl stop --all

echo "Integration tests completed!"
```

## Example 7: Multiple Environment Testing

### Scenario
Test against different configurations representing different environments.

### Setup Multiple Profiles

```bash
# Development environment (relaxed auth)
./mockctl start basic --port 8001

# Staging environment (with persistence) 
./mockctl start persistence --port 8002

# Production simulation (strict auth)
./mockctl start vmanage --port 8443
```

### Test Suite

```bash
#!/bin/bash
# multi-env-test.sh

# Test development environment
echo "Testing development environment..."
curl http://localhost:8001/api/health
curl http://localhost:8001/api/users/test

# Test staging environment
echo "Testing staging environment..."
curl http://localhost:8002/api/health
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "Test User"}' \
  http://localhost:8002/api/users

# Test production simulation
echo "Testing production environment..."
curl -k https://localhost:8443/api/health
curl -k -H "Authorization: Bearer test-token" \
  https://localhost:8443/api/devices

# Compare behaviors
./mockctl search "/api/health" --json | jq '{
  dev: .matched_requests[] | select(.port == 8001),
  staging: .matched_requests[] | select(.port == 8002), 
  prod: .matched_requests[] | select(.port == 8443)
}'
```

## Tips and Best Practices

### 1. Realistic Data

Use template variables to create realistic, dynamic data:

```json
{
  "response": {
    "id": "{{uuid}}",
    "created_at": "{{now}}",
    "user_id": "user_{{random}}",
    "session_token": "sess_{{uuid}}",
    "expires_at": "{{now|add_hours:24}}"
  }
}
```

### 2. Gradual Complexity

Start simple and add complexity as needed:

1. **Basic responses** - Static JSON responses
2. **Dynamic data** - Template variables
3. **Conditional logic** - Different responses based on input
4. **Persistence** - Stateful interactions
5. **Complex workflows** - Multi-step processes

### 3. Documentation

Document your mock configurations:

```json
{
  "endpoints": [
    {
      "path": "/api/orders",
      "method": "POST",
      "description": "Create new order - simulates e-commerce checkout",
      "response": {
        "order_id": "{{uuid}}",
        "status": "pending",
        "total": "{{body.total}}",
        "created_at": "{{now}}"
      },
      "status_code": 201
    }
  ]
}
```

### 4. Version Control

Keep your configurations in version control alongside your code:

```
project/
├── src/
├── tests/
├── configs/
│   ├── development/
│   ├── staging/
│   └── production/
└── docker-compose.yml
```

### 5. Monitoring

Use log analysis to understand usage patterns:

```bash
# Monitor in real-time
watch './mockctl search "/api" --json | jq .total_requests'

# Daily usage report
./mockctl search "/api" --since "$(date -d yesterday -Iseconds)" --json > daily_report.json
```

This covers the most common usage patterns for Mock-and-Roll. Each example can be adapted and extended based on your specific testing needs.
