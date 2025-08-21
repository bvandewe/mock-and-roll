#!/usr/bin/env bash

# Mock Server Scripts - Quick Access Helper
# This script provides easy access to all server scripts

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/scripts" && pwd)"

# If no arguments provided, show help
if [ $# -eq 0 ]; then
    "$SCRIPTS_DIR/help.sh"
    exit 0
fi

# Handle common script names without the .sh extension for convenience
SCRIPT_NAME="$1"
shift  # Remove the script name from arguments

# Add .sh extension if not present
if [[ ! "$SCRIPT_NAME" == *.sh ]]; then
    SCRIPT_NAME="${SCRIPT_NAME}.sh"
fi

# Full path to the script
SCRIPT_PATH="$SCRIPTS_DIR/$SCRIPT_NAME"

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Script not found: $SCRIPT_NAME"
    echo ""
    echo "📋 Available scripts:"
    "$SCRIPTS_DIR/help.sh"
    exit 1
fi

# Make sure script is executable
chmod +x "$SCRIPT_PATH"

# Execute the script with remaining arguments
exec "$SCRIPT_PATH" "$@"
