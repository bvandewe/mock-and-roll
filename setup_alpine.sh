#!/bin/bash

# Setup script for Alpine Linux environment
# This script helps setup the Mock API server on Alpine Linux systems

set -e

echo "🏔️  Setting up Mock API Server on Alpine Linux..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

# Check if we're on Alpine
if [ ! -f /etc/alpine-release ]; then
    print_warning "⚠️  This script is designed for Alpine Linux. Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

print_status "📋 Checking system requirements..."

# Check for Poetry
if command -v poetry >/dev/null 2>&1; then
    print_success "✅ Poetry is available"
    POETRY_AVAILABLE=true
else
    print_warning "⚠️  Poetry not found. Will use virtual environment setup."
    POETRY_AVAILABLE=false
fi

# Check for Python 3
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "✅ Python 3 is available: $PYTHON_VERSION"
else
    print_error "❌ Python 3 is required but not found"
    exit 1
fi

# Setup virtual environment if Poetry is not available or not working
if [ "$POETRY_AVAILABLE" = true ]; then
    print_status "🔧 Setting up Poetry environment..."
    
    # Configure Poetry for in-project virtual environment
    poetry config virtualenvs.in-project true
    poetry config virtualenvs.create true
    
    # Install dependencies
    if poetry install --only=main; then
        print_success "✅ Poetry environment setup complete"
    else
        print_warning "⚠️  Poetry install failed. Falling back to virtual environment setup."
        POETRY_AVAILABLE=false
    fi
fi

if [ "$POETRY_AVAILABLE" = false ]; then
    print_status "🔧 Setting up Python virtual environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        print_success "✅ Virtual environment created"
    else
        print_success "✅ Virtual environment already exists"
    fi
    
    # Activate virtual environment and install dependencies
    print_status "📦 Installing dependencies..."
    source .venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    if pip install -r requirements.txt; then
        print_success "✅ Dependencies installed successfully"
    else
        print_error "❌ Failed to install dependencies"
        exit 1
    fi
    
    deactivate
fi

# Make mockctl executable
chmod +x mockctl

print_success "🎉 Setup complete!"
print_status ""
print_status "📖 Usage:"
print_status "  ./mockctl start <config_name>    # Start a mock server"
print_status "  ./mockctl stop                   # Stop all servers"
print_status "  ./mockctl list                   # List running servers"
print_status "  ./mockctl --help                 # Show help"
print_status ""
print_status "🔍 Example:"
print_status "  ./mockctl start vmanage          # Start vManage mock server"
print_status ""

if [ "$POETRY_AVAILABLE" = true ]; then
    print_status "✨ Your environment is configured to use Poetry"
else
    print_status "✨ Your environment is configured to use the local virtual environment"
    print_warning "💡 Note: The virtual environment will be automatically used by mockctl"
fi
