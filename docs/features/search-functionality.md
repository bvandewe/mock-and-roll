# Search Command Implementation

## Overview

The search command has been successfully implemented with enhanced functionality to search across configurations and log files. The command now uses a mandatory config parameter for better organization and control.

## Command Usage

```bash
# Search specific config (most recent log)
mockctl search basic "/api/.*"

# Search all configs (most recent log per config)
mockctl search all "/docs"

# Search specific config with time filter
mockctl search vmanage "/users" --since "30m ago"

# Search ALL logs for specific configuration type
mockctl search basic --all-logs ".*"

# Search ALL available log files from all configs
mockctl search all --all-logs ".*"

# JSON output
mockctl --json search basic "/docs"

# Clean output without emojis
mockctl --no-emoji search all "/api"

# JQ-friendly status codes (no quotes needed)
mockctl --json search all "/api" | jq '.status_code_summary.status_200'
```

## Enhanced Multi-Config Search Capabilities

The search functionality now requires a mandatory config parameter and supports advanced log file selection:

### Mandatory Config Parameter

The search command signature has been updated to:

```bash
mockctl search <config_name> <pattern> [OPTIONS]
```

- `<config_name>`: **Required** - Config name or 'all'
- `<pattern>`: **Required** - Search pattern (supports regex)

### Config-Specific Search

- `mockctl search basic "/api"` searches the **most recent** log file for basic config
- `mockctl search vmanage "/users"` searches the **most recent** log file for vmanage config
- `mockctl search persistence "/docs"` searches the **most recent** log file for persistence config

### "All" Config Mode

- `mockctl search all "/pattern"` searches the **most recent log file for each config type**
- Combines results from multiple configurations in a single search
- Shows log file sources for each request when multiple files are processed

### All-Logs Mode Enhancement

The `--all-logs` flag now works with the selected config(s):

- `mockctl search basic --all-logs "/api"` searches **ALL** log files for basic config
- `mockctl search all --all-logs "/docs"` searches **ALL** log files for **ALL** configs
- Provides complete historical search across selected configuration scope

### Enhanced Output with File Tracking

**Text Output:**
- Shows "Log file processed" (single file) or "Log files processed (N)" (multiple files)  
- Displays "Source" field for each request when multiple log files are searched
- Lists all processed log files in the main results section

**JSON Output:**
- Includes `"log_files"` array with all processed log file paths
- Each request includes `"log_file_source"` field indicating its source file
- Maintains full traceability for automation and analysis

## Command Options

- `config_name` (required): Configuration name ('all' for all configs, specific config name for that config)
- `path_regex` (required): Regular expression to match request paths
- `--port PORT`: Port number to search logs for (overrides config)
- `--since SINCE`: Filter logs since time (e.g., '30m ago', 'today', '2024-01-01 10:00')
- `--all-logs`: Search all available log files for the selected config(s)
- `--json`: Output in JSON format (global flag)
- `--no-emoji`: Remove emojis from text output (global flag, ignored with --json)

## Time Filter Formats

The `--since` option supports various formats:
- Relative: "30m ago", "2h ago", "1d ago"
- Special: "today", "yesterday"
- Absolute: "2024-01-01 10:00", "10:30"

## Architecture

The implementation follows clean architecture principles:

### Domain Layer
- `RequestResponsePair`: Entity representing a matched request/response pair
- `SearchResult`: Entity containing search results with status code summaries
- `LogEntry`: Entity for parsing individual log lines
- `LogSearchRepository`: Repository interface for log search operations

### Application Layer
- `SearchLogsUseCase`: Orchestrates the search operation and determines appropriate log files

### Infrastructure Layer
- `FileSystemLogSearchRepository`: Implementation that parses log files and performs search operations

### Interface Layer
- `SearchCommand`: Command handler for CLI integration
- `Presenter.show_search_results()`: Displays results in text or JSON format

## Key Features

1. **Regex Path Matching**: Search requests using regular expressions
2. **Status Code Summary**: Groups results by HTTP status codes with JQ-friendly keys
3. **Time Filtering**: Filter results by timestamp
4. **Multiple Log Sources**: Search specific config logs or all available logs
5. **Correlation ID Tracking**: Matches requests with responses using correlation IDs
6. **Performance Metrics**: Shows response times for each request
7. **Dual Output**: Both human-readable and JSON formats
8. **Ordered Results**: Results ordered newest first as requested
9. **JQ Compatibility**: Status codes formatted as `"status_200"` for easy JQ access without quotes

## JQ Integration Examples

The JSON output uses status codes in a format that's easy to work with in JQ:

```bash
# Access status code counts directly (no quotes needed)
mockctl --json search "/api" | jq '.status_code_summary.status_200'

# Filter by status code ranges  
mockctl --json search "/api" | jq '.status_code_summary | keys[] | select(ltrimstr("status_") | tonumber >= 400)'

# Calculate error rate
mockctl --json search "/api" | jq '.status_code_summary | to_entries | map(select(.key | ltrimstr("status_") | tonumber >= 400)) | map(.value) | add // 0'
```

## Example Output

### Text Format
```
### Text Format

```text
🔍 Search Results:
   Total requests found: 3
   Log files processed (2):
     • 20250912_113314_basic_8001.logs
     • 20250912_113306_vmanage_8000.logs

📊 Status Code Summary:
   status_200: 2 requests
   status_403: 1 requests

📝 Request/Response Details:

   [1] 2025-09-08 16:14:22.976000
       Method: GET
       Path: /system/logging/status
       Status: 403
       Correlation ID: f81c05e3
       Response Time: 2.00ms
       Source: 20250912_113314_basic_8001.logs
```

### JSON Format

```json
{
  "total_requests": 3,
  "log_files": [
    "/path/to/logs/20250912_113314_basic_8001.logs",
    "/path/to/logs/20250912_113306_vmanage_8000.logs"
  ],
  "status_code_summary": {
    "status_200": 2,
    "status_403": 1
  },
  "matched_requests": [
    {
      "timestamp": "2025-09-08T16:14:22.976000",
      "correlation_id": "f81c05e3",
      "method": "GET",
      "path": "/system/logging/status",
      "status_code": 403,
      "response_time_ms": 2.0,
      "log_file_source": "/path/to/logs/20250912_113314_basic_8001.logs"
    }
  ]
}
```
```

### JSON Format
```json
{
  "total_requests": 5,
  "status_code_summary": {
    "status_200": 3,
    "status_403": 1,
    "status_404": 1
  },
  "matched_requests": [
    {
      "timestamp": "2025-09-08T16:14:22.976000",
      "correlation_id": "f81c05e3",
      "method": "GET",
      "path": "/system/logging/status",
      "status_code": 403,
      "response_time_ms": 2.0
    }
  ]
}
```

## Implementation Details

- **Log Parsing**: Parses structured logs with correlation IDs
- **Request/Response Matching**: Uses correlation IDs to pair requests with responses
- **Time Filtering**: Supports flexible time parsing for filtering
- **Error Handling**: Comprehensive error handling with meaningful messages
- **Performance**: Efficient file-based searching with minimal memory usage
- **Configuration Integration**: Seamlessly integrates with existing config system

The search command is now fully functional and ready for use!
