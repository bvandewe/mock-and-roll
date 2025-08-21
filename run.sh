#!/usr/bin/env bash

# Mock Server Management Script
# Unified interface that simplifies access to server management operations
# 
# This script calls specialized scripts in the scripts/ directory for actual operations

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"

# Function to show usage
show_usage() {
    echo "🚀 Mock API Server Management"
    echo ""
    echo "USAGE:"
    echo "  ./run.sh COMMAND [OPTIONS...]"
    echo ""
    echo "COMMANDS:"
    echo "  start [CONFIG] [--port PORT] [--reload]"
    echo "                          Start server with optional configuration"
    echo "                          CONFIG: basic, persistence, vmanage (interactive if omitted)"
    echo "                          --port: Custom port (default: 8001)"
    echo "                          --reload: Enable auto-reload for development"
    echo ""
    echo "  stop [--all] [--pid PID]"
    echo "                          Stop running servers"
    echo "                          --all: Stop all servers"
    echo "                          --pid: Stop specific process ID"
    echo ""
    echo "  list                    List running mock API servers"
    echo "  status                  Alias for 'list'"
    echo ""
    echo "  logs [--lines N] [FILTER]"
    echo "                          View server logs"
    echo "                          --lines: Number of recent lines (default: 500)"
    echo "                          FILTER: Optional endpoint filter pattern"
    echo ""
    echo "  success [FORMAT]        Generate success rate report"
    echo "                          FORMAT: summary (default), detailed, json"
    echo ""
    echo "  config-help             Show configuration system guide"
    echo "  help                    Show detailed script information"
    echo ""
    echo "EXAMPLES:"
    echo "  ./run.sh start                     # Interactive config selection"
    echo "  ./run.sh start basic               # Start basic configuration"
    echo "  ./run.sh start vmanage --port 8080 # Start vManage config on port 8080"
    echo "  ./run.sh stop                      # Stop servers (auto-detect)"
    echo "  ./run.sh list                      # Show running servers"
    echo "  ./run.sh logs --lines 100          # Show last 100 log lines"
    echo "  ./run.sh success detailed          # Detailed success analysis"
    echo ""
    echo "📂 Available configurations: basic, persistence, vmanage"
    echo "📖 For complete documentation: ./run.sh help"
}

# If no arguments provided, show usage
if [ $# -eq 0 ]; then
    show_usage
    exit 0
fi

# Handle commands
COMMAND="$1"
shift  # Remove the command from arguments

case "$COMMAND" in
    "start")
        exec "$SCRIPTS_DIR/start_server.sh" "$@"
        ;;
    "stop")
        exec "$SCRIPTS_DIR/stop_server.sh" "$@"
        ;;
    "list"|"status")
        exec "$SCRIPTS_DIR/list_servers.sh" "$@"
        ;;
    "logs")
        if [ -f "$SCRIPTS_DIR/get_logs.sh" ]; then
            exec "$SCRIPTS_DIR/get_logs.sh" "$@"
        else
            exec "$SCRIPTS_DIR/logs/filter_logs.sh" "$@"
        fi
        ;;
    "success")
        exec "$SCRIPTS_DIR/logs/success_report.sh" "$@"
        ;;
    "config-help")
        exec "$SCRIPTS_DIR/config_help.sh" "$@"
        ;;
    "help")
        exec "$SCRIPTS_DIR/help.sh" "$@"
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        echo ""
        show_usage
        exit 1
        ;;
esac
