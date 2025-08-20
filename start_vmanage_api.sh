#!/usr/bin/env bash

# Quick start script for vManage API mock server
# This script checks for the vManage configuration and starts the server

set -e  # Exit on any error

CONFIG_FOLDER="tests/configs/vmanage-api"
HOST="0.0.0.0"

# Read port from .VMANAGE_API_PORT file if it exists, otherwise use default
if [ -f ".VMANAGE_API_PORT" ]; then
    PORT=$(cat .VMANAGE_API_PORT | tr -d '[:space:]')
    echo "📁 Port read from .VMANAGE_API_PORT file: $PORT"
else
    PORT="8001"
    echo "📁 Using default port (no .VMANAGE_API_PORT file found): $PORT"
fi

# Validate port is a number
if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; then
    echo "❌ Error: Invalid port number '$PORT'. Must be between 1-65535"
    exit 1
fi

echo "🚀 Starting vManage API Mock Server..."
echo "📂 Config folder: $CONFIG_FOLDER"
echo "🌐 Host: $HOST"
echo "🔌 Port: $PORT"
echo ""

# Check if config folder exists
if [ ! -d "$CONFIG_FOLDER" ]; then
    echo "❌ Error: Configuration folder '$CONFIG_FOLDER' does not exist!"
    echo "   Please ensure you have the vManage API configuration files in place."
    exit 1
fi

# Check for required config files
REQUIRED_FILES=("api.json" "auth.json" "endpoints.json")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$CONFIG_FOLDER/$file" ]; then
        echo "❌ Error: Required configuration file '$CONFIG_FOLDER/$file' is missing!"
        exit 1
    fi
done

echo "✅ Configuration files found"
echo "🔧 Checking Python environment..."

# Check if Poetry is available
if ! command -v poetry &> /dev/null; then
    echo "❌ Error: Poetry is not available in PATH!"
    echo "   Please install Poetry: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Check if pyproject.toml exists (Poetry project)
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found in current directory!"
    echo "   Please run this script from the project root directory."
    exit 1
fi

# Configure Poetry to use local virtual environment
echo "� Configuring Poetry for local virtual environment..."
poetry config virtualenvs.in-project true

# Install dependencies if needed
echo "📦 Installing/updating dependencies with Poetry..."
poetry install --only=main

# Check if run_server.py exists
if [ ! -f "run_server.py" ]; then
    echo "❌ Error: run_server.py not found in current directory!"
    echo "   Please run this script from the project root directory."
    exit 1
fi

echo "✅ Poetry environment ready"
echo ""
echo "🔄 Starting server in background using Poetry..."
poetry run python run_server.py --host "$HOST" --port "$PORT" --config-folder "$CONFIG_FOLDER" --reload &

# Capture the process ID
SERVER_PID=$!

echo "✅ Server started successfully!"
echo ""
echo "📊 Server Information:"
echo "   Process ID: $SERVER_PID"
echo "   Access the API at: http://$HOST:$PORT"
echo "   Interactive docs: http://$HOST:$PORT/docs"
echo "   OpenAPI schema: http://$HOST:$PORT/openapi.json"
echo ""
echo "🛑 To stop the server, run:"
echo "   kill $SERVER_PID"
echo "   OR use: ./stop_vmanage_api.sh $SERVER_PID"
echo "   OR use: ./stop_vmanage_api.sh (auto-detect by port)"
echo ""
echo "💡 To check if the server is still running:"
echo "   ps -p $SERVER_PID"
echo ""

# Wait a moment for the server to start
sleep 3

# Check if the process is still running
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "🟢 Server is running (PID: $SERVER_PID)"
    
    # Additional verification - check if port is being used
    if lsof -ti:$PORT > /dev/null 2>&1; then
        ACTUAL_PID=$(lsof -ti:$PORT)
        echo "🌐 Port $PORT is in use by process: $ACTUAL_PID"
        
        # Test server response
        echo "🔍 Testing server response..."
        if curl -s http://localhost:$PORT/ > /dev/null 2>&1; then
            echo "✅ Server is responding to HTTP requests"
        else
            echo "⚠️  Server not responding to HTTP requests yet"
        fi
    else
        echo "⚠️  Port $PORT is not in use - server may not have started correctly"
    fi
else
    echo "🔴 Server failed to start or exited immediately"
    echo "   Check the logs above for error details"
    exit 1
fi