#!/usr/bin/env bash

# Simple script to kill all Python processes that might be our server
# Use this as a fallback if the stop script doesn't work

echo "🛑 Killing all mock server processes..."

# Kill by pattern matching
pkill -f "run_server.py" 2>/dev/null || true
pkill -f "main:app" 2>/dev/null || true
pkill -f "uvicorn.*8000" 2>/dev/null || true
pkill -f "poetry run python run_server" 2>/dev/null || true

# Wait a moment
sleep 2

# Force kill if still running
pkill -9 -f "run_server.py" 2>/dev/null || true
pkill -9 -f "main:app" 2>/dev/null || true

echo "✅ All server processes killed"
echo "💡 You can now restart the server with ./start_vmanage_api.sh"
