# Logging & Monitoring

Mock-and-Roll provides comprehensive logging and monitoring capabilities to track API usage, debug issues, and analyze request patterns.

## Overview

The logging system captures:

- All HTTP requests and responses
- Authentication attempts and failures
- Configuration changes and server events
- Error conditions and debugging information
- Performance metrics and timing data

## Log Configuration

### Default Logging Setup

Mock-and-Roll automatically logs to the `logs/` directory:

```bash
logs/
├── mockctl.log          # CLI and server management logs
├── server_basic.log     # Basic profile server logs
├── server_persistence.log # Persistence profile logs
└── server_vmanage.log   # vManage profile logs
```

### Log Levels

Configure logging verbosity through environment variables:

```bash
# Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
export LOG_LEVEL="INFO"

# Enable detailed request logging
export LOG_REQUESTS="true"

# Enable authentication debugging
export LOG_AUTH="true"

# Start server with logging configuration
./mockctl start myapi --log-level DEBUG
```

### Custom Log Configuration

Configure logging in your API configuration:

```json
{
  "logging": {
    "level": "INFO",
    "format": "detailed",
    "outputs": ["file", "console"],
    "file_rotation": {
      "enabled": true,
      "max_size": "10MB",
      "backup_count": 5
    },
    "request_logging": {
      "enabled": true,
      "include_headers": true,
      "include_body": false,
      "include_response": true
    }
  }
}
```

## Request and Response Logging

### Automatic Request Logging

All API requests are automatically logged:

```
2024-12-28 10:30:15 INFO [REQUEST] GET /api/v1/users/123
  Headers: {
    "X-API-Key": "demo-***-123",
    "User-Agent": "curl/7.68.0",
    "Accept": "*/*"
  }
  Client: 192.168.1.100

2024-12-28 10:30:15 INFO [RESPONSE] 200 OK (45ms)
  Body: {"id": "123", "name": "John Doe"}
  Size: 156 bytes
```

### Detailed Response Logging

Enable comprehensive response logging:

```json
{
  "logging": {
    "response_logging": {
      "enabled": true,
      "include_timing": true,
      "include_headers": true,
      "include_body": true,
      "max_body_size": 1000
    }
  }
}
```

### Conditional Logging

Log specific conditions or errors:

```json
{
  "method": "POST",
  "path": "/api/users",
  "logging": {
    "log_conditions": {
      "on_error": "full",
      "on_success": "minimal",
      "on_auth_failure": "detailed"
    }
  }
}
```

## Authentication Logging

### Authentication Attempts

Track all authentication events:

```
2024-12-28 10:30:10 INFO [AUTH] API Key authentication successful
  Method: api_key
  Key: demo-***-123
  Endpoint: GET /api/users
  Client: 192.168.1.100

2024-12-28 10:30:12 WARNING [AUTH] Invalid API key attempted
  Method: api_key
  Key: invalid-***-key
  Endpoint: GET /api/admin
  Client: 192.168.1.101
  Result: 401 Unauthorized
```

### Security Event Logging

Log security-related events:

```json
{
  "security_logging": {
    "enabled": true,
    "events": [
      "authentication_failure",
      "authorization_denied",
      "rate_limit_exceeded",
      "suspicious_patterns",
      "admin_access"
    ]
  }
}
```

## CLI Log Management

### Viewing Logs

Use `mockctl` to view and analyze logs:

```bash
# View recent logs for all servers
./mockctl logs --lines 50

# View logs for specific configuration
./mockctl logs basic --lines 100

# Follow logs in real-time
./mockctl logs basic --follow

# View logs with timestamps
./mockctl logs basic --timestamps
```

### Log Search

Search logs using patterns and filters:

```bash
# Search for specific endpoints
./mockctl search basic "/api/users"

# Search with regex patterns
./mockctl search basic "POST.*login"

# Search for authentication events
./mockctl search basic "authentication" --since "1h ago"

# Search for errors
./mockctl search basic "ERROR|WARN" --since "24h ago"

# Case-insensitive search
./mockctl search basic "error" --ignore-case

# Export search results
./mockctl --json search basic "/api" > api_requests.json
```

### Advanced Search Options

```bash
# Time-based filtering
./mockctl search basic "login" --since "2024-12-28 10:00"
./mockctl search basic "error" --until "2024-12-28 12:00"
./mockctl search basic "api" --since "2h ago" --until "1h ago"

# Multiple pattern search
./mockctl search basic "GET|POST" --regex

# Context around matches
./mockctl search basic "error" --context 3

# Limit results
./mockctl search basic "request" --max-results 20
```

## Structured Logging

### JSON Log Format

Enable JSON logging for machine processing:

```json
{
  "logging": {
    "format": "json",
    "structured": true
  }
}
```

Example JSON log entry:

```json
{
  "timestamp": "2024-12-28T10:30:15.123Z",
  "level": "INFO",
  "event_type": "request",
  "method": "GET",
  "path": "/api/users/123",
  "status_code": 200,
  "response_time_ms": 45,
  "client_ip": "192.168.1.100",
  "user_agent": "curl/7.68.0",
  "auth_method": "api_key",
  "auth_success": true,
  "request_id": "req_abc123",
  "config_name": "basic"
}
```

### Custom Log Fields

Add custom fields to log entries:

```json
{
  "logging": {
    "custom_fields": {
      "application": "mock-api",
      "environment": "development",
      "version": "1.0.0"
    }
  }
}
```

## Performance Monitoring

### Request Timing

Track request performance:

```
2024-12-28 10:30:15 INFO [TIMING] GET /api/users/123
  Total: 45ms
  Authentication: 5ms
  Processing: 35ms
  Response: 5ms
```

### Performance Metrics

Configure performance logging:

```json
{
  "performance": {
    "enabled": true,
    "metrics": {
      "request_duration": true,
      "auth_duration": true,
      "db_query_duration": true,
      "response_size": true
    },
    "slow_request_threshold_ms": 1000
  }
}
```

### Resource Usage Monitoring

Track server resource usage:

```bash
# View server statistics
curl -H "X-System-Key: system-admin-key" \
     http://localhost:8000/system/stats

# Example response:
{
    "uptime_seconds": 3600,
    "requests_total": 1543,
    "requests_per_second": 0.43,
    "avg_response_time_ms": 23,
    "memory_usage_mb": 45.6,
    "redis_connections": 5
}
```

## Error Logging and Debugging

### Error Categorization

Errors are categorized by type and severity:

```
2024-12-28 10:30:20 ERROR [CONFIG] Invalid endpoint configuration
  File: configs/myapi/endpoints.json
  Line: 15
  Error: Missing required field 'method'

2024-12-28 10:30:25 ERROR [AUTH] Authentication method not found
  Method: invalid_bearer
  Endpoint: GET /api/protected
  Config: myapi

2024-12-28 10:30:30 ERROR [REDIS] Redis connection failed
  Host: localhost:6379
  Error: Connection refused
  Retry: 3/5
```

### Debug Logging

Enable verbose debugging:

```bash
# Start with debug logging
./mockctl start myapi --debug

# Enable specific debug categories
./mockctl start myapi --debug-auth --debug-persistence

# View debug logs
./mockctl search myapi "DEBUG" --since "10m ago"
```

### Error Handling Configuration

Configure error logging behavior:

```json
{
  "error_handling": {
    "log_stack_traces": true,
    "log_request_context": true,
    "notify_on_errors": {
      "enabled": true,
      "webhook_url": "https://alerts.example.com/webhook",
      "severity_threshold": "ERROR"
    }
  }
}
```

## Log Analysis and Metrics

### Request Analytics

Analyze request patterns:

```bash
# Generate request statistics
./mockctl --json search basic "/api" | \
  jq -r '.requests[] | .status_code' | \
  sort | uniq -c | sort -nr

# Output:
#    125 200
#     23 404
#     12 401
#      5 500

# Analyze response times
./mockctl --json search basic "/api" | \
  jq -r '.requests[] | .response_time_ms' | \
  awk '{sum+=$1; count++} END {print "Average:", sum/count "ms"}'
```

### Popular Endpoints

Identify most used endpoints:

```bash
# Top endpoints by request count
./mockctl --json search basic "" --since "24h ago" | \
  jq -r '.requests[] | .path' | \
  sort | uniq -c | sort -nr | head -10
```

### Error Analysis

Analyze error patterns:

```bash
# Error rate by endpoint
./mockctl --json search basic "ERROR" --since "24h ago" | \
  jq -r '.requests[] | select(.status_code >= 400) | .path' | \
  sort | uniq -c | sort -nr
```

## Log Rotation and Archival

### Automatic Log Rotation

Configure log rotation to manage disk space:

```json
{
  "logging": {
    "rotation": {
      "enabled": true,
      "max_file_size": "10MB",
      "backup_count": 10,
      "compress_backups": true
    }
  }
}
```

### Manual Log Management

```bash
# Archive old logs
./mockctl archive-logs --older-than "30d"

# Clean up logs
./mockctl clean-logs --keep-days 7

# Compress logs
./mockctl compress-logs logs/server_basic.log
```

## Integration with External Systems

### Webhook Notifications

Send log events to external systems:

```json
{
  "webhooks": {
    "error_notifications": {
      "enabled": true,
      "url": "https://alerts.example.com/webhook",
      "events": ["error", "auth_failure", "slow_request"],
      "headers": {
        "Authorization": "Bearer webhook-token-123"
      }
    }
  }
}
```

### Syslog Integration

Forward logs to syslog servers:

```json
{
  "syslog": {
    "enabled": true,
    "server": "syslog.example.com",
    "port": 514,
    "facility": "local0",
    "protocol": "udp"
  }
}
```

### ELK Stack Integration

Send structured logs to Elasticsearch:

```json
{
  "elasticsearch": {
    "enabled": true,
    "url": "http://elasticsearch:9200",
    "index": "mock-api-logs",
    "username": "elastic",
    "password": "password"
  }
}
```

## Monitoring Dashboards

### Real-time Monitoring

Create monitoring dashboards using log data:

```bash
# Real-time request monitoring
watch './mockctl --json search basic "" --since "1m ago" | jq ".total_requests"'

# Monitor error rates
watch './mockctl --json search basic "ERROR" --since "5m ago" | jq ".total_requests"'

# Track response times
./mockctl --json search basic "" --since "10m ago" | \
  jq -r '.requests[] | .response_time_ms' | \
  awk '{
    sum += $1;
    count++;
    if($1 > max) max = $1;
    if(min == 0 || $1 < min) min = $1
  }
  END {
    print "Requests:", count;
    print "Average:", sum/count "ms";
    print "Min:", min "ms";
    print "Max:", max "ms"
  }'
```

### Custom Metrics

Extract custom metrics from logs:

```python
#!/usr/bin/env python3
import json
import subprocess
from collections import defaultdict

# Get log data
result = subprocess.run([
    './mockctl', '--json', 'search', 'basic', '', '--since', '1h ago'
], capture_output=True, text=True)

data = json.loads(result.stdout)

# Calculate metrics
status_codes = defaultdict(int)
endpoints = defaultdict(int)
response_times = []

for request in data.get('requests', []):
    status_codes[request['status_code']] += 1
    endpoints[request['path']] += 1
    response_times.append(request['response_time_ms'])

# Print metrics
print("Status Code Distribution:")
for code, count in sorted(status_codes.items()):
    print(f"  {code}: {count}")

print("\nTop Endpoints:")
for endpoint, count in sorted(endpoints.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {endpoint}: {count}")

if response_times:
    avg_response = sum(response_times) / len(response_times)
    print(f"\nAverage Response Time: {avg_response:.2f}ms")
```

## Security and Compliance Logging

### Audit Trail

Maintain audit logs for compliance:

```json
{
  "audit_logging": {
    "enabled": true,
    "events": ["user_creation", "user_deletion", "admin_access", "config_changes", "auth_failures"],
    "retention_days": 90
  }
}
```

### Data Privacy

Protect sensitive data in logs:

```json
{
  "privacy": {
    "sanitize_logs": true,
    "mask_fields": ["password", "api_key", "authorization", "credit_card", "ssn"],
    "mask_pattern": "***"
  }
}
```

## Best Practices

### 1. **Log Level Management**

Use appropriate log levels:

```bash
# Development - verbose logging
export LOG_LEVEL="DEBUG"

# Staging - balanced logging
export LOG_LEVEL="INFO"

# Production - minimal logging
export LOG_LEVEL="WARNING"
```

### 2. **Structured Data**

Use consistent log structure:

```json
{
  "timestamp": "ISO8601",
  "level": "INFO|WARNING|ERROR",
  "event_type": "request|auth|error|system",
  "message": "Human readable message",
  "context": {
    "request_id": "uuid",
    "client_ip": "ip_address",
    "user_id": "identifier"
  }
}
```

### 3. **Performance Considerations**

Optimize logging performance:

```json
{
  "logging": {
    "async": true,
    "buffer_size": 1000,
    "flush_interval": 5,
    "exclude_paths": ["/health", "/metrics"]
  }
}
```

### 4. **Log Retention**

Manage log storage costs:

```bash
# Automated cleanup
0 2 * * * /path/to/mockctl clean-logs --keep-days 30

# Compress old logs
0 3 * * 0 /path/to/mockctl compress-logs --older-than 7d
```

## Troubleshooting

### Common Logging Issues

**Logs Not Appearing:**

```bash
# Check log level configuration
echo $LOG_LEVEL

# Verify log directory permissions
ls -la logs/

# Check if logging is enabled
./mockctl config-check myapi | grep logging
```

**Large Log Files:**

```bash
# Check log file sizes
du -sh logs/*

# Enable log rotation
vim configs/myapi/api.json  # Add rotation config

# Manual cleanup
./mockctl clean-logs --keep-days 7
```

**Missing Log Entries:**

```bash
# Check log filters
./mockctl search basic "" --debug

# Verify timestamp format
./mockctl search basic "" --since "1h ago" --verbose
```

### Debug Commands

```bash
# Test logging configuration
./mockctl test-logging myapi

# Validate log format
./mockctl validate-logs logs/server_myapi.log

# Check log parsing
./mockctl --json search myapi "" --max-results 1 | jq .
```

## Performance Monitoring Commands

```bash
# Monitor request rate
./mockctl --json search basic "" --since "1m ago" | \
  jq -r '.summary.requests_per_second'

# Track error rate
./mockctl --json search basic "ERROR" --since "5m ago" | \
  jq -r '.summary.error_rate'

# Response time percentiles
./mockctl --json search basic "" --since "10m ago" | \
  jq -r '.summary.response_times | {p50, p95, p99}'

```

Mock-and-Roll's comprehensive logging system provides the visibility and insights needed to monitor API behavior, debug issues, and ensure reliable operation in any environment.
