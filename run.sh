#!/usr/bin/env bash

# Mock Server Scripts - Quick Access Helper
# This script provides easy access to all server scripts
# 
# Usage:
#   ./run.sh                    # Show help
#   ./run.sh start basic        # Start basic config
#   ./run.sh stop               # Stop servers  
#   ./run.sh list               # List running servers
#   ./run.sh help               # Show detailed help

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/scripts" && pwd)"

# If no arguments provided, show help
if [ $# -eq 0 ]; then
    "$SCRIPTS_DIR/help.sh"
    exit 0
fi

# Handle common commands directly
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
        exec "$SCRIPTS_DIR/get_logs.sh" "$@"
        ;;
    "success")
        exec "$SCRIPTS_DIR/success_report.sh" "$@"
        ;;
    "config-help")
        exec "$SCRIPTS_DIR/config_help.sh" "$@"
        ;;
    "help")
        exec "$SCRIPTS_DIR/help.sh" "$@"
        ;;
    *)
        # Handle script names (with or without .sh extension)
        SCRIPT_NAME="$COMMAND"
        if [[ ! "$SCRIPT_NAME" == *.sh ]]; then
            SCRIPT_NAME="${SCRIPT_NAME}.sh"
        fi
        
        # Full path to the script
        SCRIPT_PATH="$SCRIPTS_DIR/$SCRIPT_NAME"
        
        # Check if script exists
        if [ ! -f "$SCRIPT_PATH" ]; then
            echo "❌ Command or script not found: $COMMAND"
            echo ""
            echo "📋 Available commands:"
            echo "   start [config] [options]    # Start server"
            echo "   stop [options]              # Stop server"
            echo "   list                        # List running servers"
            echo "   logs [options]              # View logs"
            echo "   success [format]            # Success report"
            echo "   config-help                 # Configuration help"
            echo "   help                        # Show all scripts"
            echo ""
            echo "📋 Or run any script directly:"
            "$SCRIPTS_DIR/help.sh" | grep "scripts/"
            exit 1
        fi
        
        # Make sure script is executable
        chmod +x "$SCRIPT_PATH"
        
        # Execute the script with remaining arguments
        exec "$SCRIPT_PATH" "$@"
        ;;
esac
