# Server Management

Learn how to effectively manage Mock-and-Roll servers using the `mockctl` command-line interface for development, testing, and production scenarios.

## Overview

The `mockctl` CLI provides comprehensive server lifecycle management:

- Start and stop servers with different configurations
- Monitor running instances and resource usage
- Manage logs and search request patterns
- Handle multiple server instances simultaneously
- Perform maintenance and cleanup operations

## Basic Server Operations

### Starting Servers

#### Interactive Configuration Selection

```bash
# Start with configuration selection menu
./mockctl start

# Example output:
# Available configurations:
# 1. basic - Simple REST API with minimal setup
# 2. persistence - Full-featured API with Redis
# 3. vmanage - Cisco SD-WAN vManage API simulation
# 4. airgapped - Offline-capable API
#
# Select configuration (1-4): 2
# Starting persistence server on port 8000...
```

#### Direct Configuration Start

```bash
# Start specific configuration
./mockctl start basic

# Start on custom port
./mockctl start basic --port 8080

# Start in background
./mockctl start basic --daemon

# Start with custom config folder
./mockctl start --config-dir /path/to/configs myconfig
```

#### Development Mode

```bash
# Start with hot reloading (restarts on config changes)
./mockctl start basic --reload

# Start with debug logging
./mockctl start basic --debug

# Start with verbose output
./mockctl start basic --verbose
```

### Stopping Servers

```bash
# Stop specific server by configuration
./mockctl stop basic

# Stop server by port
./mockctl stop --port 8080

# Stop all running servers
./mockctl stop --all

# Force stop unresponsive server
./mockctl stop basic --force

# Stop with cleanup
./mockctl stop basic --cleanup
```

### Server Status

```bash
# List all running servers
./mockctl list

# Example output:
# Running Mock Servers:
# ┌────────────┬─────┬──────┬────────────┬─────────────────────┐
# │ Config     │ PID │ Port │ Status     │ Started             │
# ├────────────┼─────┼──────┼────────────┼─────────────────────┤
# │ basic      │ 1234│ 8000 │ ✅ running │ 2024-12-28 10:30:15 │
# │ persistence│ 5678│ 8001 │ ✅ running │ 2024-12-28 10:32:22 │
# └────────────┴─────┴──────┴────────────┴─────────────────────┘

# List with detailed information
./mockctl list --detailed

# JSON output for scripting
./mockctl --json list

# Clean output without emojis
./mockctl --no-emoji list
```

## Advanced Server Management

### Multiple Server Instances

Run multiple configurations simultaneously:

```bash
# Start multiple servers on different ports
./mockctl start basic --port 8000 &
./mockctl start persistence --port 8001 &
./mockctl start vmanage --port 8002 &

# Use port auto-assignment
./mockctl start basic --auto-port
./mockctl start persistence --auto-port

# Check all running instances
./mockctl list
```

### Server Health Monitoring

```bash
# Check server health
curl http://localhost:8000/system/health

# Monitor server metrics
curl -H "X-System-Key: system-admin-key" \
     http://localhost:8000/system/stats

# Example health response:
{
    "status": "healthy",
    "uptime_seconds": 3600,
    "version": "1.0.0",
    "config": "basic",
    "redis": {
        "connected": true,
        "status": "healthy"
    }
}
```

### Process Management

```bash
# Check process status
ps aux | grep "python.*main.py"

# Kill specific process
./mockctl kill 1234  # Kill by PID

# Kill by port
./mockctl kill --port 8000

# Clean up dead processes
./mockctl cleanup-processes
```

## Configuration Management

### Configuration Validation

```bash
# Validate configuration files
./mockctl validate basic

# Check specific configuration file
./mockctl validate basic --file endpoints.json

# Validate all configurations
./mockctl validate-all

# Example validation output:
# ✅ API configuration valid
# ✅ Authentication configuration valid
# ✅ Endpoints configuration valid
# ❌ Error: Missing required field 'method' in endpoint 3
```

### Configuration Testing

```bash
# Test configuration endpoints
./mockctl test basic

# Test specific endpoint
./mockctl test basic --endpoint "/api/users"

# Test authentication methods
./mockctl test basic --auth-only

# Load testing
./mockctl stress-test basic --requests 1000 --concurrent 10
```

### Configuration Switching

```bash
# Hot-swap configuration (requires restart)
./mockctl restart basic --new-config persistence

# Update configuration files and reload
./mockctl reload basic

# Apply configuration changes without restart
./mockctl refresh-config basic
```

## Log Management

### Real-time Log Monitoring

```bash
# Follow logs for specific server
./mockctl logs basic --follow

# Show last N lines
./mockctl logs basic --lines 100

# Show logs with timestamps
./mockctl logs basic --timestamps

# Show logs from specific time
./mockctl logs basic --since "2024-12-28 10:00:00"
```

### Log Search and Analysis

```bash
# Search for specific patterns
./mockctl search basic "POST /api/users"

# Search with regex
./mockctl search basic "GET.*users.*" --regex

# Search multiple servers
./mockctl search all "authentication failure"

# Time-filtered search
./mockctl search basic "ERROR" --since "1h ago"

# Export search results
./mockctl --json search basic "/api" > api-requests.json
```

### Log Archival and Cleanup

```bash
# Archive old logs
./mockctl archive-logs --older-than 30d

# Clean up logs
./mockctl clean-logs --keep-days 7

# Compress log files
./mockctl compress-logs basic

# Rotate logs manually
./mockctl rotate-logs basic
```

## Maintenance Operations

### Data Management

```bash
# Clear Redis cache (persistence servers)
curl -X DELETE \
     -H "X-System-Key: system-admin-key" \
     http://localhost:8000/system/cache

# Reset server data
./mockctl reset-data basic

# Backup server state
./mockctl backup basic --output /path/to/backup.json

# Restore server state
./mockctl restore basic --input /path/to/backup.json
```

### Server Cleanup

```bash
# Clean up all stopped servers
./mockctl clean-up

# Remove stale PID files
./mockctl cleanup-pids

# Clear temporary files
./mockctl cleanup-temp

# Full system cleanup
./mockctl cleanup-all
```

### Health Checks

```bash
# Perform health check on all servers
./mockctl health-check

# Deep health check with diagnostics
./mockctl health-check --detailed

# Check specific server components
./mockctl health-check basic --check redis,auth,endpoints
```

## Monitoring and Debugging

### Performance Monitoring

```bash
# Monitor resource usage
./mockctl monitor basic

# Show performance statistics
./mockctl stats basic

# Example stats output:
# Server Statistics (basic):
# ├─ Uptime: 2h 15m 30s
# ├─ Total Requests: 1,247
# ├─ Requests/sec: 0.17
# ├─ Avg Response Time: 23ms
# ├─ Memory Usage: 45.2 MB
# ├─ Redis Connections: 3
# └─ Active Sessions: 8
```

### Debug Mode

```bash
# Start with comprehensive debugging
./mockctl start basic --debug --verbose

# Enable specific debug categories
./mockctl start basic --debug-auth --debug-persistence

# Debug configuration loading
./mockctl start basic --debug-config

# Debug template rendering
./mockctl start basic --debug-templates
```

### Error Diagnosis

```bash
# Check for common issues
./mockctl doctor basic

# Validate system requirements
./mockctl check-requirements

# Test connectivity
./mockctl test-connection basic

# Example doctor output:
# Mock-and-Roll Health Check:
# ✅ Python version (3.11.0)
# ✅ Required packages installed
# ✅ Configuration files valid
# ❌ Redis connection failed (check if Redis is running)
# ✅ Port 8000 available
```

## Automation and Scripting

### Batch Operations

```bash
# Start multiple servers from script
./scripts/start-all-servers.sh

# Example script content:
#!/bin/bash
./mockctl start basic --port 8000 --daemon
./mockctl start persistence --port 8001 --daemon
./mockctl start vmanage --port 8002 --daemon

echo "All servers started"
./mockctl list
```

### Scheduled Maintenance

```bash
# Cron job for log cleanup (daily at 2 AM)
0 2 * * * /path/to/mockctl clean-logs --keep-days 30

# Weekly server restart (Sunday at 3 AM)
0 3 * * 0 /path/to/scripts/restart-servers.sh

# Health check every 5 minutes
*/5 * * * * /path/to/mockctl health-check --quiet || /path/to/scripts/alert.sh
```

### CI/CD Integration

```yaml
# GitHub Actions workflow
name: Test Mock API
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Start mock server
        run: ./mockctl start basic --daemon --port 8080

      - name: Wait for server
        run: sleep 5

      - name: Test API endpoints
        run: |
          curl -f http://localhost:8080/system/health
          curl -f -H "X-API-Key: demo-key-123" http://localhost:8080/api/v1/items/123

      - name: Stop server
        run: ./mockctl stop --all
```

## Production Deployment

### Service Management

```bash
# Install as systemd service
sudo ./setup/install-service.sh

# Service operations
sudo systemctl start mock-and-roll
sudo systemctl stop mock-and-roll
sudo systemctl restart mock-and-roll
sudo systemctl status mock-and-roll

# Enable auto-start
sudo systemctl enable mock-and-roll
```

### Load Balancing

```bash
# Start multiple instances for load balancing
./mockctl start basic --port 8000 --daemon
./mockctl start basic --port 8001 --daemon
./mockctl start basic --port 8002 --daemon

# Configure nginx load balancer
sudo vim /etc/nginx/sites-available/mock-api

# Example nginx config:
upstream mock_api {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://mock_api;
    }
}
```

### Container Deployment

```bash
# Docker deployment
docker build -t mock-api .
docker run -d -p 8000:8000 --name mock-api-basic \
  -e CONFIG_NAME=basic mock-api

# Docker Compose
docker-compose up -d

# Kubernetes deployment
kubectl apply -f k8s/deployment.yaml
kubectl scale deployment mock-api --replicas=3
```

## Troubleshooting

### Common Issues

**Server Won't Start:**

```bash
# Check port availability
./mockctl check-port 8000

# Validate configuration
./mockctl validate basic

# Check Python dependencies
./mockctl check-requirements
```

**Server Crashes:**

```bash
# Check recent logs
./mockctl logs basic --lines 50 | grep -i error

# Start with debug output
./mockctl start basic --debug --foreground

# Check system resources
free -h
df -h
```

**Performance Issues:**

```bash
# Monitor resource usage
./mockctl monitor basic --interval 5

# Check slow requests
./mockctl search basic "response_time" --since "1h ago" | grep -E "[0-9]{4,}"

# Analyze request patterns
./mockctl stats basic --detailed
```

### Debug Commands

```bash
# Comprehensive system check
./mockctl doctor --all

# Test configuration integrity
./mockctl test-config basic --comprehensive

# Network connectivity test
./mockctl test-network --host localhost --port 8000

# Permission check
./mockctl check-permissions
```

## Best Practices

### 1. **Environment Separation**

```bash
# Use different configs per environment
./mockctl start dev-config --port 8000      # Development
./mockctl start staging-config --port 8001  # Staging
./mockctl start prod-config --port 8002     # Production-like
```

### 2. **Resource Management**

```bash
# Monitor resource usage
./mockctl monitor --threshold memory=100MB,cpu=80%

# Set resource limits
./mockctl start basic --memory-limit 128MB --cpu-limit 0.5
```

### 3. **Security Considerations**

```bash
# Use strong system API keys
export SYSTEM_API_KEY=$(openssl rand -base64 32)

# Restrict network access
./mockctl start basic --bind 127.0.0.1 --port 8000

# Enable audit logging
./mockctl start basic --audit-log
```

### 4. **Backup and Recovery**

```bash
# Regular configuration backups
./mockctl backup-config basic --output configs/backup/

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
./mockctl backup-all --output /backup/mock-api-$DATE/
```

The `mockctl` CLI provides comprehensive server management capabilities that scale from simple development scenarios to complex production deployments with multiple server instances and advanced monitoring.
