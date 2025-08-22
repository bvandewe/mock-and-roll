#!/usr/bin/env bash

# Server State Management Library
# Provides centralized functions to manage running server information
# Replaces the scattered .*_API_PORT file approach

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# State management configuration
STATE_DIR="$PROJECT_ROOT/.server_state"
SERVERS_FILE="$STATE_DIR/servers.json"

# Ensure state directory exists
ensure_state_dir() {
    if [ ! -d "$STATE_DIR" ]; then
        mkdir -p "$STATE_DIR"
        echo "[]" > "$SERVERS_FILE"
    fi
    
    if [ ! -f "$SERVERS_FILE" ]; then
        echo "[]" > "$SERVERS_FILE"
    fi
}

# Add a server to the state
# Usage: add_server CONFIG_NAME PORT PID HOST
add_server() {
    local config_name="$1"
    local port="$2"
    local pid="$3"
    local host="${4:-0.0.0.0}"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    ensure_state_dir
    
    # Remove any existing entry for this config/port combination
    remove_server_by_config "$config_name"
    remove_server_by_port "$port"
    
    # Create new server entry
    local temp_file=$(mktemp)
    python3 -c "
import json
import sys

try:
    with open('$SERVERS_FILE', 'r') as f:
        servers = json.load(f)
except:
    servers = []

new_server = {
    'config': '$config_name',
    'port': $port,
    'pid': $pid,
    'host': '$host',
    'started_at': '$timestamp',
    'status': 'running'
}

servers.append(new_server)

with open('$temp_file', 'w') as f:
    json.dump(servers, f, indent=2)
" && mv "$temp_file" "$SERVERS_FILE"
    
    echo -e "${GREEN}✅ Added server to state: $config_name (PID: $pid, Port: $port)${NC}" >&2
}

# Remove a server by PID
# Usage: remove_server_by_pid PID
remove_server_by_pid() {
    local pid="$1"
    
    ensure_state_dir
    
    local temp_file=$(mktemp)
    python3 -c "
import json

try:
    with open('$SERVERS_FILE', 'r') as f:
        servers = json.load(f)
except:
    servers = []

servers = [s for s in servers if s.get('pid') != $pid]

with open('$temp_file', 'w') as f:
    json.dump(servers, f, indent=2)
" && mv "$temp_file" "$SERVERS_FILE"
    
    echo -e "${BLUE}🗑️  Removed server from state: PID $pid${NC}" >&2
}

# Remove a server by config name
# Usage: remove_server_by_config CONFIG_NAME
remove_server_by_config() {
    local config_name="$1"
    
    ensure_state_dir
    
    local temp_file=$(mktemp)
    python3 -c "
import json

try:
    with open('$SERVERS_FILE', 'r') as f:
        servers = json.load(f)
except:
    servers = []

servers = [s for s in servers if s.get('config') != '$config_name']

with open('$temp_file', 'w') as f:
    json.dump(servers, f, indent=2)
" && mv "$temp_file" "$SERVERS_FILE"
}

# Remove a server by port
# Usage: remove_server_by_port PORT
remove_server_by_port() {
    local port="$1"
    
    ensure_state_dir
    
    local temp_file=$(mktemp)
    python3 -c "
import json

try:
    with open('$SERVERS_FILE', 'r') as f:
        servers = json.load(f)
except:
    servers = []

servers = [s for s in servers if s.get('port') != $port]

with open('$temp_file', 'w') as f:
    json.dump(servers, f, indent=2)
" && mv "$temp_file" "$SERVERS_FILE"
}

# Get server info by config name
# Usage: get_server_by_config CONFIG_NAME
get_server_by_config() {
    local config_name="$1"
    
    ensure_state_dir
    
    python3 -c "
import json

try:
    with open('$SERVERS_FILE', 'r') as f:
        servers = json.load(f)
    
    for server in servers:
        if server.get('config') == '$config_name':
            print(json.dumps(server))
            break
except:
    pass
"
}

# Get server info by port
# Usage: get_server_by_port PORT
get_server_by_port() {
    local port="$1"
    
    ensure_state_dir
    
    python3 -c "
import json

try:
    with open('$SERVERS_FILE', 'r') as f:
        servers = json.load(f)
    
    for server in servers:
        if server.get('port') == $port:
            print(json.dumps(server))
            break
except:
    pass
"
}

# Get all servers
# Usage: get_all_servers
get_all_servers() {
    ensure_state_dir
    
    python3 -c "
import json

try:
    with open('$SERVERS_FILE', 'r') as f:
        servers = json.load(f)
    print(json.dumps(servers))
except:
    print('[]')
"
}

# Clean up dead processes
# Usage: cleanup_dead_processes
cleanup_dead_processes() {
    ensure_state_dir
    
    local temp_file=$(mktemp)
    python3 -c "
import json
import subprocess

try:
    with open('$SERVERS_FILE', 'r') as f:
        servers = json.load(f)
except:
    servers = []

active_servers = []
for server in servers:
    pid = server.get('pid')
    if pid:
        try:
            # Check if process is still running
            subprocess.check_output(['ps', '-p', str(pid)], stderr=subprocess.DEVNULL)
            active_servers.append(server)
        except subprocess.CalledProcessError:
            print(f\"Removing dead process: PID {pid} (config: {server.get('config', 'unknown')})\", file=sys.stderr)

with open('$temp_file', 'w') as f:
    json.dump(active_servers, f, indent=2)
" && mv "$temp_file" "$SERVERS_FILE"
}

# Get port for a configuration (for backward compatibility)
# Usage: get_port_for_config CONFIG_NAME
get_port_for_config() {
    local config_name="$1"
    
    server_info=$(get_server_by_config "$config_name")
    if [ -n "$server_info" ]; then
        echo "$server_info" | python3 -c "
import json
import sys
try:
    server = json.load(sys.stdin)
    print(server.get('port', ''))
except:
    pass
"
    fi
}

# Clear all server state (for cleanup)
# Usage: clear_all_state
clear_all_state() {
    ensure_state_dir
    echo "[]" > "$SERVERS_FILE"
    echo -e "${YELLOW}🗑️  Cleared all server state${NC}" >&2
}

# Migrate from old .*_API_PORT files
# Usage: migrate_from_old_files
migrate_from_old_files() {
    echo -e "${BLUE}🔄 Migrating from old .*_API_PORT files...${NC}" >&2
    
    cd "$PROJECT_ROOT"
    
    # Clean up any dead processes first
    cleanup_dead_processes
    
    # Check for old port files and try to match them with running processes
    local found_files=false
    
    # Use find to locate port files instead of glob
    if find . -maxdepth 1 -name ".*_API_PORT" -type f | grep -q .; then
        find . -maxdepth 1 -name ".*_API_PORT" -type f | while read -r port_file; do
            found_files=true
            config_name=$(echo "$port_file" | sed 's/^\.\///' | sed 's/^\.\(.*\)_API_PORT$/\1/' | tr '[:upper:]' '[:lower:]')
            port=$(cat "$port_file" | tr -d '[:space:]')
            
            echo -e "${YELLOW}  Found old port file: $port_file (config: $config_name, port: $port)${NC}" >&2
            
            # Try to find a running process on this port
            if command -v lsof >/dev/null 2>&1; then
                pid=$(lsof -ti tcp:$port 2>/dev/null | head -1)
            else
                pid=$(netstat -tulpn 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1 | head -1)
            fi
            
            if [ -n "$pid" ] && ps -p "$pid" >/dev/null 2>&1; then
                # Process is running, add to new state
                add_server "$config_name" "$port" "$pid" "0.0.0.0"
                echo -e "${GREEN}  Migrated: $config_name -> new state${NC}" >&2
            else
                echo -e "${RED}  No running process found for $config_name on port $port${NC}" >&2
            fi
            
            # Remove old file
            rm -f "$port_file"
            echo -e "${BLUE}  Removed old file: $port_file${NC}" >&2
        done
    else
        echo -e "${CYAN}  No old .*_API_PORT files found${NC}" >&2
    fi
    
    echo -e "${GREEN}✅ Migration completed${NC}" >&2
}
