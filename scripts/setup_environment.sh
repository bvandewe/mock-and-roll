#!/usr/bin/env bash

# Setup Environment Script for Mock Server
# This script sets up the development environment and dependencies

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root directory (parent of scripts)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root to ensure relative paths work correctly
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Setting up Mock Server environment...${NC}"

# Check if Poetry is available
if ! command -v poetry &> /dev/null; then
    echo "❌ Error: Poetry is not available in PATH!"
    echo "   Please install Poetry: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Configure Poetry to use local virtual environment
echo "📁 Configuring Poetry for local virtual environment..."
poetry config virtualenvs.in-project true

# Install dependencies with version-compatible command
echo "📦 Installing dependencies with Poetry..."

# Check Poetry version to use appropriate install command
POETRY_VERSION=$(poetry --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
POETRY_MAJOR=$(echo "$POETRY_VERSION" | cut -d. -f1)
POETRY_MINOR=$(echo "$POETRY_VERSION" | cut -d. -f2)

echo "📝 Detected Poetry version: $POETRY_VERSION"

# Handle different Poetry versions
if [ "$POETRY_MAJOR" -gt 2 ] || ([ "$POETRY_MAJOR" -eq 2 ] && [ "$POETRY_MINOR" -ge 0 ]); then
    # Poetry 2.0+ with package-mode support
    echo "📝 Using Poetry $POETRY_VERSION (v2+ syntax with package-mode)"
    poetry install
elif [ "$POETRY_MAJOR" -gt 1 ] || ([ "$POETRY_MAJOR" -eq 1 ] && [ "$POETRY_MINOR" -ge 8 ]); then
    # Poetry 1.8+ supports modern syntax but may need --no-root
    echo "📝 Using Poetry $POETRY_VERSION (modern syntax with --no-root)"
    poetry install --no-root
else
    # Poetry < 1.8 uses legacy syntax
    echo "📝 Using Poetry $POETRY_VERSION (legacy syntax)"
    poetry install --no-root
fi

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
