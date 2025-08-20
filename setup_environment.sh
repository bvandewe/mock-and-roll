#!/usr/bin/env bash

# Setup script for vManage API Mock Server
# This ensures Poetry environment is properly configured

set -e

echo "🔧 Setting up vManage API Mock Server environment..."

# Check if Poetry is available
if ! command -v poetry &> /dev/null; then
    echo "❌ Error: Poetry is not available in PATH!"
    echo "   Please install Poetry: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Configure Poetry to use local virtual environment
echo "📁 Configuring Poetry for local virtual environment..."
poetry config virtualenvs.in-project true

# Install dependencies
echo "📦 Installing dependencies with Poetry..."
poetry install

# Check if virtual environment was created
if [ -d ".venv" ]; then
    echo "✅ Virtual environment created at .venv"
else
    echo "⚠️  Virtual environment not found in .venv (may be in global location)"
fi

# Show environment info
echo "📊 Poetry environment info:"
poetry env info

echo ""
echo "✅ Setup complete! You can now use:"
echo "   ./start_vmanage_api.sh - to start the server"
echo "   ./stop_vmanage_api.sh  - to stop the server"
