#!/usr/bin/env bash

# Mock Server Scripts Help
# This script lists all available scripts and their purposes

set -e

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPTS_DIR")"

echo "🛠️  Mock Server - Available Scripts"
echo "=" | tr '=' '=' | head -c 60
echo ""
echo "📁 Location: $SCRIPTS_DIR"
echo ""

# Function to get script description from comments
get_script_description() {
    local script_file="$1"
    local description=""
    
    # Look for description in comments (lines starting with # that contain description text)
    description=$(grep -E "^#.*([Ss]cript|[Dd]escription|[Pp]urpose)" "$script_file" 2>/dev/null | head -1 | sed 's/^#[[:space:]]*//' || echo "")
    
    # If no description found, try to extract from the filename or first meaningful comment
    if [ -z "$description" ]; then
        description=$(grep -E "^#[[:space:]]*[A-Z]" "$script_file" 2>/dev/null | head -1 | sed 's/^#[[:space:]]*//' || echo "")
    fi
    
    # If still no description, provide a generic one based on filename
    if [ -z "$description" ]; then
        case "$script_file" in
            *start*) description="Start the mock server" ;;
            *stop*) description="Stop the mock server" ;;
            *test*) description="Test script" ;;
            *setup*) description="Setup script" ;;
            *get_logs*) description="Fetch and filter server logs" ;;
            *kill*) description="Kill server processes" ;;
            *list*) description="List server information" ;;
            *alpine*) description="Alpine Linux setup" ;;
            *) description="Utility script" ;;
        esac
    fi
    
    echo "$description"
}

# Main scripts (server operations)
echo "🚀 Server Operations:"
echo "--------------------"

if [ -f "$SCRIPTS_DIR/start_server.sh" ]; then
    desc=$(get_script_description "$SCRIPTS_DIR/start_server.sh")
    echo "  ./scripts/start_server.sh         - $desc (Recommended)"
    echo "    Examples:"
    echo "      ./scripts/start_server.sh                 # Interactive selection"
    echo "      ./scripts/start_server.sh vmanage         # Start vmanage config"
    echo "      ./scripts/start_server.sh basic --port 8002"
fi

if [ -f "$SCRIPTS_DIR/stop_server.sh" ]; then
    desc=$(get_script_description "$SCRIPTS_DIR/stop_server.sh")
    echo "  ./scripts/stop_server.sh          - $desc (Recommended)"
    echo "    Examples:"
    echo "      ./scripts/stop_server.sh                  # Auto-detect or interactive"
    echo "      ./scripts/stop_server.sh vmanage          # Stop vmanage config"
    echo "      ./scripts/stop_server.sh --all            # Stop all servers"
fi

if [ -f "$SCRIPTS_DIR/config_help.sh" ]; then
    desc=$(get_script_description "$SCRIPTS_DIR/config_help.sh")
    echo "  ./scripts/config_help.sh          - $desc"
fi

if [ -f "$SCRIPTS_DIR/list_servers.sh" ]; then
    desc=$(get_script_description "$SCRIPTS_DIR/list_servers.sh")
    echo "  ./scripts/list_servers.sh         - $desc"
fi

echo ""

# Configuration Management
echo "🔧 Configuration Management:"
echo "-----------------------------"
echo "  Available configs: basic, persistence, vmanage"
echo "  Config location: configs/[NAME]/"
echo "  Each config contains: api.json, auth.json, endpoints.json"
echo ""

# Monitoring and debugging
echo "📊 Monitoring & Debugging:"
echo "---------------------------"

if [ -f "$SCRIPTS_DIR/success_report.sh" ]; then
    desc=$(get_script_description "$SCRIPTS_DIR/success_report.sh")
    echo "  ./scripts/success_report.sh       - $desc"
    echo "    Examples:"
    echo "      ./scripts/success_report.sh               # Summary report"
    echo "      ./scripts/success_report.sh detailed      # Detailed analysis"
    echo "      ./scripts/success_report.sh json          # JSON output"
fi

if [ -f "$SCRIPTS_DIR/get_logs.sh" ]; then
    desc=$(get_script_description "$SCRIPTS_DIR/get_logs.sh")
    echo "  ./scripts/get_logs.sh             - $desc"
    echo "    Examples:"
    echo "      ./scripts/get_logs.sh                     # All recent logs"
    echo "      ./scripts/get_logs.sh /dataservice/device # Filter by endpoint"
    echo "      ./scripts/get_logs.sh --lines 500 /logout # Custom line count"
fi

echo ""

# Setup and environment
echo "⚙️  Setup & Environment:"
echo "------------------------"

if [ -f "$SCRIPTS_DIR/setup_environment.sh" ]; then
    desc=$(get_script_description "$SCRIPTS_DIR/setup_environment.sh")
    echo "  ./scripts/setup_environment.sh    - $desc"
fi

if [ -f "$SCRIPTS_DIR/setup_alpine.sh" ]; then
    desc=$(get_script_description "$SCRIPTS_DIR/setup_alpine.sh")
    echo "  ./scripts/setup_alpine.sh         - $desc"
fi

echo ""

# All other scripts
echo "🔧 Other Utilities:"
echo "-------------------"

for script in "$SCRIPTS_DIR"/*.sh; do
    if [ -f "$script" ]; then
        script_name=$(basename "$script")
        
        # Skip scripts already listed above
        case "$script_name" in
            "help.sh"|"start_server.sh"|"stop_server.sh"|"config_help.sh"|"list_servers.sh"|"success_report.sh"|"get_logs.sh"|"setup_environment.sh"|"setup_alpine.sh")
                continue
                ;;
        esac
        
        desc=$(get_script_description "$script")
        printf "  ./scripts/%-25s - %s\n" "$script_name" "$desc"
    fi
done

echo ""
echo "💡 Quick Start:"
echo "---------------"
echo "  1. Start server:    ./scripts/start_server.sh"
echo "  2. Check logs:      ./scripts/get_logs.sh"
echo "  3. Stop server:     ./scripts/stop_server.sh"
echo ""
echo "📋 Configuration Help:"
echo "---------------------"
echo "  ./scripts/config_help.sh           # Detailed configuration guide"
echo ""
echo "📖 For detailed help on any script, run:"
echo "  ./scripts/SCRIPT_NAME --help"
echo ""
echo "🌐 Server will be available at: http://0.0.0.0:8001"
echo "📚 API Documentation: http://0.0.0.0:8001/docs"
