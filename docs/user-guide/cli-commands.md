# CLI Commands Reference

Complete reference for the `mockctl` command-line interface.

## Overview

The `mockctl` tool is your primary interface for managing Mock-and-Roll servers. It provides commands for starting, stopping, monitoring, and searching mock API servers.

## Basic Usage

```bash
mockctl [COMMAND] [OPTIONS]
```

## Global Options

| Option | Description | Default |
|--------|-------------|---------|
| `--help`, `-h` | Show help message | - |
| `--version`, `-v` | Show version information | - |
| `--verbose` | Enable verbose output | false |
| `--json` | Output in JSON format | false |
| `--no-emoji` | Remove emojis from text output (ignored with --json) | false |

## Commands

### `start` - Start Mock Server

Start a mock server with the specified configuration.

```bash
mockctl start <config_name> [OPTIONS]
```

**Arguments:**
- `config_name` - Configuration profile name (basic, persistence, vmanage, or custom)

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--port`, `-p` | Port number to run on | From config |
| `--host` | Host address to bind to | From config |
| `--reload` | Enable auto-reload on changes | false |
| `--debug` | Enable debug mode | false |

**Examples:**

```bash
# Start basic configuration
mockctl start basic

# Start on custom port
mockctl start basic --port 8080

# Start with auto-reload (development)
mockctl start basic --reload --debug

# Start vManage simulation
mockctl start vmanage

# Start with custom host binding
mockctl start basic --host 127.0.0.1 --port 9000
```

### `stop` - Stop Mock Servers

Stop running mock servers.

```bash
mockctl stop [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--all`, `-a` | Stop all running servers | false |
| `--port`, `-p` | Stop server on specific port | - |
| `--config`, `-c` | Stop servers with specific config | - |
| `--force`, `-f` | Force stop (kill process) | false |

**Examples:**

```bash
# Stop all servers (interactive selection if multiple)
mockctl stop

# Stop all servers without prompt
mockctl stop --all

# Stop server on specific port
mockctl stop --port 8000

# Stop all servers with 'basic' config
mockctl stop --config basic

# Force stop unresponsive server
mockctl stop --port 8000 --force
```

### `list` - List Running Servers

Display information about running mock servers.

```bash
mockctl list [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--verbose`, `-v` | Show detailed information | false |
| `--config`, `-c` | Filter by configuration name | - |

**Examples:**

```bash
# List all running servers
mockctl list

# Detailed information
mockctl list --verbose

# JSON output for scripting
mockctl --json list

# Clean output without emojis
mockctl --no-emoji list

# Filter by configuration
mockctl list --config basic

# Combine global options for clean detailed output
mockctl --no-emoji list --verbose
```

**Sample Output:**

```
# mockctl list

🔍 Scanning for running Mock API Servers...

📊 Found 3 tracked server(s):

Config: vmanage
Status: 🟢 Running
PID: 33562
Address: http://0.0.0.0:8001
Started: 2025-09-11 21:54:45
API Docs: http://0.0.0.0:8001/docs

Config: persistence
Status: 🟢 Running
PID: 33710
Address: http://0.0.0.0:8002
Started: 2025-09-11 21:54:48
API Docs: http://0.0.0.0:8002/docs

Config: basic
Status: 🟢 Running
PID: 53472
Address: http://0.0.0.0:8000
Started: 2025-09-11 22:00:25
API Docs: http://0.0.0.0:8000/docs
```

### `clean-up` - Stop All Servers & Purge Logs

Perform a full housekeeping operation:

- Gracefully stops all tracked running mock server instances
- Deletes all timestamped server log files in `./logs/*.logs` (e.g. `20250916_120000_basic_8000.logs`)
- Preserves and truncates `logs/mockctl.log` (clears its contents but keeps the file)
- Provides structured JSON output when used with `--json`

```bash
mockctl clean-up
mockctl cleanup        # alias
mockctl --json clean-up
```

**When to Use:**

- Before packaging or archiving the project
- To reclaim disk space after heavy testing
- To reset environment between integration test runs

**Examples:**

```bash
# Standard clean-up with human readable output
mockctl clean-up

# JSON output for automation scripts
mockctl --json clean-up | jq '.deleted_log_files'

# Combined with search workflow (prior to re-running tests)
mockctl clean-up && mockctl start basic && mockctl search basic "/api"
```

**Sample JSON Output:**

```json
{
  "status": "success",
  "action": "clean-up",
  "timestamp": "2025-09-16T12:34:56Z",
  "stopped_instances": [
    {"config": "basic", "pid": 34567, "stopped": true},
    {"config": "vmanage", "pid": 34572, "stopped": true}
  ],
  "deleted_log_files": [
    "20250916_120000_basic_8000.logs",
    "20250916_120010_vmanage_8001.logs"
  ],
  "mockctl_log_truncated": true
}
```

**Safety Notes:**

- Only affects files within the `./logs` directory
- Does not remove configuration or data persistence stores (e.g. Redis)
- Non-fatal errors during individual file deletions are reported but do not abort the operation


**Sample Output with `--no-emoji`:**

```
# mockctl --no-emoji list     
 Scanning for running Mock API Servers...

 Found 3 tracked server(s):

Config: vmanage
Status:  Running
PID: 33562
Address: http://0.0.0.0:8001
Started: 2025-09-11 21:54:45
API Docs: http://0.0.0.0:8001/docs

Config: persistence
Status:  Running
PID: 33710
Address: http://0.0.0.0:8002
Started: 2025-09-11 21:54:48
API Docs: http://0.0.0.0:8002/docs

Config: basic
Status:  Running
PID: 53472
Address: http://0.0.0.0:8000
Started: 2025-09-11 22:00:25
API Docs: http://0.0.0.0:8000/docs
```

### `search` - Search Server Logs

Search server logs for specific patterns and requests. The first positional
argument (`config_name`) is mandatory and must be either a specific
configuration profile (e.g. `basic`, `vmanage`, `persistence`, a custom
profile) or the literal `all` to search across the most recent log of each
available configuration.

```bash
mockctl search <config_name> <pattern> [OPTIONS]
```

**Arguments:**
- `config_name` - Configuration name ('all' for all configs, or specific config like 'basic', 'vmanage', etc.)
- `pattern` - Search pattern (supports regex)

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--port`, `-p` | Search logs for specific port (overrides config) | auto-detect |
| `--since` | Search since timestamp (supports relative time) | - |
| `--all-logs` | Search ALL available log files for selected config(s) | false |

**Enhanced Search Capabilities:**

- **Config-specific**: `basic`, `vmanage`, `persistence` searches most recent log for that config
- **All configs**: `all` searches most recent log file for each configuration type
- **All logs**: `--all-logs` searches ALL historical log files for selected config(s)
- **Smart filtering**: Automatically excludes generic system logs, focuses on request/response logs

**Examples:**

```bash
# Search most recent basic config logs
mockctl search basic "/auth"

# Search most recent logs for all configs (use 'all' explicitly)
mockctl search all "/api"

# Search ALL historical vmanage logs
mockctl search vmanage --all-logs ".*"

# Search ALL historical logs for ALL configs
mockctl search all --all-logs "/docs"

# Search with regex pattern in basic logs
mockctl search basic "POST.*login"

# Search recent requests with time filter
mockctl search basic "/api" --since "2025-01-01T11:00:00Z"

# JSON output for processing (always include config_name)
mockctl --json search all "/j_security_check"

# Clean output without emojis
mockctl --no-emoji search basic "/auth"

# Search specific server logs by port (overrides config)
mockctl search basic "/api" --port 8443
```

**Sample Output (Text):**

```text
🔍 Search Results:
   Total requests found: 3
   Log file processed: 20250912_113314_basic_8001.logs

📊 Status Code Summary:
   status_200: 2 requests
   status_401: 1 requests

📝 Request/Response Details:

   [1] 2025-01-01T12:30:00Z
       Method: POST
       Path: /j_security_check
       Status: 401
       Correlation ID: req_12345
       Response Time: 45.2ms
       Request: {"username": "admin", "password": "wrong"}
       Response: {"error": "Invalid credentials"}

   [2] 2025-01-01T12:32:00Z
       Method: POST  
       Path: /j_security_check
       Status: 200
       Correlation ID: req_12346
       Response Time: 23.1ms
       Request: {"username": "admin", "password": "admin"}
       Response: {"token": "abc123", "expires": 3600}
```

**Sample Output with Multiple Files (all configs):**

```text
🔍 Search Results:
   Total requests found: 5
   Log files processed (3):
     • 20250912_113314_basic_8001.logs
     • 20250912_113306_vmanage_8000.logs
     • 20250912_113400_persistence_8002.logs

📊 Status Code Summary:
   status_200: 3 requests
   status_401: 2 requests

📝 Request/Response Details:

   [1] 2025-01-01T12:30:00Z
       Method: POST
       Path: /j_security_check
       Status: 401
       Correlation ID: req_12345
       Response Time: 45.2ms
       Source: 20250912_113314_basic_8001.logs
```

**Sample Output (JSON):**

```json
{
  "total_requests": 2,
  "log_files": [
    "/path/to/logs/20250912_113314_basic_8001.logs"
  ],
  "status_code_summary": {
    "status_200": 1,
    "status_401": 1
  },
  "matched_requests": [
    {
      "timestamp": "2025-01-01T12:32:00Z",
      "correlation_id": "req_12346",
      "method": "POST",
      "path": "/j_security_check",
      "status_code": 200,
      "response_time_ms": 23.1,
      "request_body": "{\"username\": \"admin\", \"password\": \"admin\"}",
      "response_body": "{\"token\": \"abc123\", \"expires\": 3600}",
      "request_headers": {"Content-Type": "application/json"},
      "response_headers": {"Content-Type": "application/json"},
      "log_file_source": "/path/to/logs/20250912_113314_basic_8001.logs"
    }
  ]
}
```

### `logs` - View Server Logs

Display real-time or historical server logs.

```bash
mockctl logs [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--follow`, `-f` | Follow log output (tail -f) | false |
| `--lines`, `-n` | Number of lines to show | 50 |
| `--config`, `-c` | Show logs for specific config | auto-detect |
| `--port`, `-p` | Show logs for specific port | auto-detect |
| `--level` | Filter by log level | - |

**Examples:**

```bash
# Show recent logs
mockctl logs

# Follow live logs
mockctl logs --follow

# Show last 100 lines
mockctl logs --lines 100

# Show logs for specific server
mockctl logs --config vmanage --port 8443

# Filter by log level
mockctl logs --level ERROR,WARN
```

### `status` - Server Health Check

Check the health and status of running servers.

```bash
mockctl status [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--config`, `-c` | Check specific config | all |
| `--port`, `-p` | Check specific port | all |

**Examples:**

```bash
# Check all servers
mockctl status

# Check specific server
mockctl status --port 8000

# JSON output
mockctl --json status
```

### `restart` - Restart Servers

Restart running mock servers.

```bash
mockctl restart [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--all`, `-a` | Restart all servers | false |
| `--config`, `-c` | Restart servers with specific config | - |
| `--port`, `-p` | Restart server on specific port | - |

**Examples:**

```bash
# Restart all servers
mockctl restart --all

# Restart specific configuration
mockctl restart --config basic

# Restart server on specific port  
mockctl restart --port 8000
```

### `validate` - Validate Configuration

Validate configuration files for syntax and completeness.

```bash
mockctl validate <config_name> [OPTIONS]
```

**Arguments:**
- `config_name` - Configuration profile to validate

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--strict` | Enable strict validation | false |

**Examples:**

```bash
# Validate basic configuration
mockctl validate basic

# Strict validation
mockctl validate vmanage --strict

# JSON output
mockctl --json validate basic
```

### `test` - Test Server Endpoints

Test the health and availability of running mock servers by sending requests to their standard endpoints.

```bash
mockctl test [CONFIG] [OPTIONS]
```

**Arguments:**
- `CONFIG` - Configuration name to test (optional, tests all running servers if omitted)

**Options:**

| Option | Description | Default |
|--------|-------------|---------|

**Tested Endpoints:**
- `/` - Root endpoint
- `/docs` - Interactive API documentation
- `/openapi.json` - OpenAPI schema

**Examples:**

```bash
# Test all running servers
mockctl test

# Test specific configuration
mockctl test basic

# JSON output for automation
mockctl --json test vmanage

# Test results with different outcomes
mockctl test persistence
```

**JSON Output Format:**
```json
{
  "test_results": [
    {
      "config": "basic",
      "base_url": "http://0.0.0.0:8000",
      "tests": [
        {
          "endpoint": "/",
          "url": "http://0.0.0.0:8000/",
          "description": "Root endpoint",
          "status": "success",
          "status_code": 200,
          "response_time_ms": 6,
          "content_type": "application/json"
        }
      ]
    }
  ]
}
```

**Exit Codes:**
- `0` - All tests passed
- `1` - One or more tests failed or command error occurred

### `version` - Show Version Information

Display version information for Mock-and-Roll.

```bash
mockctl version [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|

**Examples:**

```bash
# Show version information
mockctl version

# JSON output with detailed information
mockctl --json version

# Using global flags (alternative syntax)
mockctl --version         # Short version info
mockctl -v               # Short version info  
mockctl --json --version # JSON version info with global flags
```

**Sample Output (Text):**

```
ℹ️  MockAndRoll version 0.2.0
```

**Sample Output (JSON):**

```json
{
  "name": "MockAndRoll",
  "version": "0.2.0",
  "description": "A highly configurable and extensible mock REST API server built with FastAPI that allows to quickly create mock endpoints with various authentication methods, conditional responses, and dynamic path parameters."
}
```

## Advanced Usage

### Scripting and Automation

Use `mockctl` in scripts with JSON output:

```bash
#!/bin/bash

# Start server and get port
PORT=$(mockctl --json start basic | jq -r '.server.port')

# Wait for server to be ready
while ! curl -s http://localhost:$PORT/api/health > /dev/null; do
  sleep 1
done

# Run tests
pytest tests/

# Stop server
mockctl stop --port $PORT
```

### Monitoring Multiple Servers

```bash
# Monitor servers in a loop
while true; do
  clear
  echo "=== Mock Server Status ==="
  mockctl list
  echo
  echo "=== Recent Activity ==="
  mockctl search all ".*" --limit 5 --since "$(date -d '1 minute ago' -Iseconds)"
  sleep 10
done
```

### Log Analysis

```bash
# Count requests by status code
mockctl --json search all ".*" | jq '.status_code_summary'

# Find slow requests
mockctl --json search all ".*" | jq '.matched_requests[] | select(.response_time_ms > 1000)'

# Extract request paths
mockctl --json search ".*" | jq -r '.matched_requests[].path' | sort | uniq -c
```

## Configuration and Environment

### Environment Variables

Control `mockctl` behavior with environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MOCKCTL_CONFIG_DIR` | Default configuration directory | `configs` |
| `MOCKCTL_LOGS_DIR` | Logs directory | `logs` |
| `MOCKCTL_DEFAULT_CONFIG` | Default configuration profile | `basic` |
| `MOCKCTL_JSON_OUTPUT` | Default to JSON output | `false` |

### Configuration Files

`mockctl` looks for configuration files in:

1. `./configs/<profile>/` (relative to current directory)
2. `$MOCKCTL_CONFIG_DIR/<profile>/`
3. `~/.mockctl/configs/<profile>/`

## Exit Codes

`mockctl` uses standard exit codes:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Configuration error |
| 4 | Server error |
| 5 | Not found |

## Tips and Best Practices

### Performance

1. **Use JSON output** for scripting to avoid parsing text
2. **Limit search results** when dealing with large log files
3. **Use specific patterns** instead of broad searches
4. **Monitor resource usage** for long-running servers

### Debugging

1. **Use verbose mode** (`--verbose`) for detailed output
2. **Check logs** (`mockctl logs`) when servers don't start
3. **Validate configurations** before starting servers
4. **Use debug mode** (`--debug`) during development

### Automation

1. **Use JSON output** for reliable parsing
2. **Check exit codes** in scripts
3. **Wait for server readiness** before running tests
4. **Clean up resources** (stop servers) after use

### Security

1. **Use different ports** for different environments
2. **Secure configuration files** with appropriate permissions
3. **Rotate API keys** in production-like setups
4. **Monitor access logs** for security analysis

## Common Workflows

### Development Workflow

```bash
# Start development server with auto-reload
mockctl start basic --reload --debug

# In another terminal, monitor logs
mockctl logs --follow

# Make configuration changes and test
curl http://localhost:8000/api/test

# Search for specific requests
mockctl search basic "/api/test"

# Stop when done
mockctl stop
```

### Testing Workflow

```bash
# Start clean environment
mockctl stop --all
mockctl start basic --port 8080

# Run tests
npm test  # or pytest, etc.

# Analyze results
mockctl --json search ".*" > test_results.json
mockctl stop --all
```

### CI/CD Integration

```bash
# In CI pipeline
export MOCKCTL_JSON_OUTPUT=true

# Start background server
mockctl start basic --port 8080 &
SERVER_PID=$!

# Wait for readiness
timeout 30 bash -c 'while ! curl -s http://localhost:8080/api/health; do sleep 1; done'

# Run integration tests
npm run test:integration

# Cleanup
kill $SERVER_PID
```

## Troubleshooting

### Common Issues

**Command not found:**
```bash
# Ensure mockctl is executable
chmod +x mockctl

# Use relative path if not in PATH
./mockctl --help
```

**Permission denied:**
```bash
# Check file permissions
ls -la mockctl

# Make executable
chmod +x mockctl
```

**Port in use:**
```bash
# Check what's using the port
lsof -i :8000

# Use different port
mockctl start basic --port 8080
```

**Configuration errors:**
```bash
# Validate configuration
mockctl validate basic

# Check configuration files exist
ls -la configs/basic/
```

For more troubleshooting help, see our [troubleshooting guide](../development/troubleshooting.md).
