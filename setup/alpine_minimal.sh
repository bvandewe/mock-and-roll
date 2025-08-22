#!/bin/bash

# Minimal setup script for Alpine Linux environment (no admin privileges required)
# This script sets up the Mock API server using only user-level installations

set -e

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

echo "🏔️  Setting up Mock API Server on Alpine Linux (Minimal Setup)..."

# Get the project root directory (parent of setup directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

print_status "📍 Project directory: $PROJECT_DIR"

print_status "📋 Minimal setup (no admin privileges required)..."

# Check for Python 3
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "✅ Python 3 is available: $PYTHON_VERSION"
else
    print_error "❌ Python 3 is required but not found"
    print_error "   Please ask your system administrator to install: apk add --no-cache python3"
    exit 1
fi

# Check for pip
if ! python3 -m pip --version >/dev/null 2>&1; then
    print_error "❌ pip is required but not found"
    print_error "   Please ask your system administrator to install: apk add --no-cache py3-pip"
    exit 1
fi

# Check if we have a virtual environment capability
if ! python3 -m venv --help >/dev/null 2>&1; then
    print_error "❌ Python venv module is not available"
    print_error "   This is required for virtual environment setup"
    exit 1
fi

print_status "🔧 Setting up Python virtual environment..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    if python3 -m venv .venv; then
        print_success "✅ Virtual environment created"
    else
        print_error "❌ Failed to create virtual environment"
        exit 1
    fi
else
    print_success "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
print_status "📦 Installing dependencies in virtual environment..."
source .venv/bin/activate

# Upgrade pip
if pip install --upgrade pip; then
    print_success "✅ pip upgraded"
else
    print_warning "⚠️  pip upgrade failed, continuing anyway"
fi

# Install dependencies
if pip install -r requirements.txt; then
    print_success "✅ Dependencies installed successfully"
else
    print_error "❌ Failed to install dependencies"
    deactivate
    exit 1
fi

deactivate

# Make mockctl executable
chmod +x mockctl

# Setup mockctl in PATH
print_status "🔗 Setting up mockctl in PATH..."

MOCKCTL_PATH="$PROJECT_DIR/mockctl"

# Create ~/.local/bin if it doesn't exist
mkdir -p "$HOME/.local/bin"

# Create a symbolic link or wrapper script in ~/.local/bin
if [ -L "$HOME/.local/bin/mockctl" ]; then
    print_success "✅ mockctl symlink already exists in PATH"
elif [ -f "$HOME/.local/bin/mockctl" ]; then
    print_warning "⚠️  mockctl file exists in PATH, backing up and replacing..."
    mv "$HOME/.local/bin/mockctl" "$HOME/.local/bin/mockctl.backup.$(date +%s)"
fi

# Create symlink to mockctl
if ln -s "$MOCKCTL_PATH" "$HOME/.local/bin/mockctl" 2>/dev/null; then
    print_success "✅ mockctl symlink created in ~/.local/bin"
else
    # If symlink fails, create a wrapper script
    print_status "🔧 Creating mockctl wrapper script..."
    cat > "$HOME/.local/bin/mockctl" << EOF
#!/bin/bash
# Auto-generated mockctl wrapper
exec "$MOCKCTL_PATH" "\$@"
EOF
    chmod +x "$HOME/.local/bin/mockctl"
    print_success "✅ mockctl wrapper script created in ~/.local/bin"
fi

# Ensure ~/.local/bin is in PATH
PATH_EXPORT='export PATH="$HOME/.local/bin:$PATH"'
PATH_ADDED=false

# Function to add PATH to profile if not already present
add_to_profile() {
    local profile_file="$1"
    if [ -f "$profile_file" ]; then
        if ! grep -q "/.local/bin" "$profile_file"; then
            echo "" >> "$profile_file"
            echo "# Added by mockctl setup" >> "$profile_file"
            echo "$PATH_EXPORT" >> "$profile_file"
            print_status "📝 Added ~/.local/bin to PATH in $profile_file"
            PATH_ADDED=true
        else
            print_success "✅ ~/.local/bin already in PATH in $profile_file"
        fi
    fi
}

# Add to appropriate shell profile
if [ -f "$HOME/.bashrc" ]; then
    add_to_profile "$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    add_to_profile "$HOME/.zshrc"
elif [ -f "$HOME/.profile" ]; then
    add_to_profile "$HOME/.profile"
else
    # Create .profile if no shell config exists
    echo "$PATH_EXPORT" > "$HOME/.profile"
    print_status "📝 Created ~/.profile with PATH configuration"
    PATH_ADDED=true
fi

# Add to current session PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    export PATH="$HOME/.local/bin:$PATH"
    print_status "📝 Added ~/.local/bin to current session PATH"
fi

print_success "🎉 Minimal setup complete!"
print_status ""
print_status "📖 Usage:"
print_status "  mockctl start <config_name>     # Start a mock server (global command)"
print_status "  mockctl stop                    # Stop all servers"
print_status "  mockctl list                    # List running servers"
print_status "  mockctl --help                  # Show help"
print_status ""
print_status "  Or use local script:"
print_status "  ./mockctl start <config_name>   # Start a mock server (local)"
print_status ""
print_status "🔍 Example:"
print_status "  mockctl start vmanage           # Start vManage mock server"
print_status ""
print_status "✨ Your environment is configured to use the local virtual environment"
print_warning "💡 Note: Some advanced process management features may be limited"
print_warning "     if system tools (ps, lsof, kill) are not available"
print_status ""
print_status "🔧 Environment Details:"
print_status "   - Python: $(python3 --version)"
print_status "   - Virtual Environment: .venv (ready)"
print_status "   - mockctl: Available globally in PATH"
print_status ""

if [ "$PATH_ADDED" = true ]; then
    print_warning "💡 Note: You may need to restart your shell or run 'source ~/.bashrc' to use 'mockctl' globally"
    print_status "   Alternatively, you can use './mockctl' in this directory right now"
else
    print_success "🎯 You can now use 'mockctl' from anywhere!"
fi

print_status ""
print_success "🚀 Ready to start your mock server!"

print_status ""
print_status "📝 If you encounter issues with process management, ask your admin to install:"
print_status "   apk add --no-cache procps util-linux lsof"
