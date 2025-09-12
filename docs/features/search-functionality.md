# Search Command Implementation

## Overview

The search command has been successfully implemented to return the list of requests/responses per status_code (ordered newest first) for a given path regex, as requested.

## Command Usage

```bash
# Search with regex pattern - searches latest log file
mockctl search "/api/.*"

# Search with time filter - searches latest log file
mockctl search "/users" --since "30m ago"

# Search ALL logs for specific configuration type
mockctl search ".*" --config basic

# Search ALL available log files from all servers
mockctl search ".*" --all-logs

# JSON output
mockctl --json search "/docs"

# Clean output without emojis
mockctl --no-emoji search "/api"

# JQ-friendly status codes (no quotes needed)
mockctl --json search "/api" | jq '.status_code_summary.status_200'
```

## Enhanced Multi-File Search Capabilities

The search functionality now supports comprehensive log file selection:

### Configuration-Specific Search

When using `--config`, the system searches **ALL** log files for that configuration type:

- `--config basic` searches all basic configuration logs (multiple files)
- `--config persistence` searches all persistence configuration logs
- `--config vmanage` searches all vManage configuration logs
- Results are combined with merged status summaries and chronological ordering

### Smart Latest Log Selection

When no config is specified, automatically selects the most recent timestamped log file:

- Filters out generic system logs (`latest.logs`)
- Focuses on structured request/response logs with correlation IDs
- Provides efficient single-file search for recent activity

### All-Logs Mode

The `--all-logs` flag searches across **ALL** available server log files:

- Aggregates results from every configuration type
- Combines all server instances and historical data
- Provides complete API interaction history

### Robust Error Handling

- Continues searching if individual log files are corrupted or inaccessible
- Reports warnings for failed files but completes search of available files
- Maintains search integrity across multiple file operations

## Command Options

- `path_regex` (required): Regular expression to match request paths
- `--config CONFIG`: Configuration name (auto-detect if omitted)
- `--port PORT`: Port number to search logs for
- `--since SINCE`: Filter logs since time (e.g., '30m ago', 'today', '2024-01-01 10:00')
- `--all-logs`: Search all available log files
- `--json`: Output in JSON format (no emojis)
- `--no-emoji`: Remove emojis from text output (ignored with --json)

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
🔍 Search Results:
   Total requests found: 5

📊 Status Code Summary:
   200: 3 requests
   403: 1 requests
   404: 1 requests

📝 Request/Response Details:

   [1] 2025-09-08 16:14:22.976000
       Method: GET
       Path: /system/logging/status
       Status: 403
       Correlation ID: f81c05e3
       Response Time: 2.00ms
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
