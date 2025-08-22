#!/bin/bash

# Setup script for Alpine Linux environment
# This script helps setup the Mock API server on Alpine Linux systems

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

echo "🏔️  Setting up Mock API Server on Alpine Linux..."

# Get the project root directory (parent of setup directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

print_status "📍 Project directory: $PROJECT_DIR"

# Check if we're on Alpine
if [ ! -f /etc/alpine-release ]; then
    print_warning "⚠️  This script is designed for Alpine Linux. Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

print_status "📋 Checking system requirements..."

# Check for required system packages and install them if needed
print_status "🔍 Checking required system packages..."

REQUIRED_PACKAGES=("python3" "py3-pip" "git" "curl" "bash")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! command -v "$package" >/dev/null 2>&1; then
        MISSING_PACKAGES+=("$package")
    fi
done

# Check for additional system tools needed for process management
SYSTEM_TOOLS=("procps" "util-linux" "lsof")
MISSING_TOOLS=()

for tool in "${SYSTEM_TOOLS[@]}"; do
    case "$tool" in
        "procps")
            if ! command -v ps >/dev/null 2>&1; then
                MISSING_TOOLS+=("procps")
            fi
            ;;
        "util-linux")
            if ! command -v kill >/dev/null 2>&1; then
                MISSING_TOOLS+=("util-linux")
            fi
            ;;
        "lsof")
            if ! command -v lsof >/dev/null 2>&1; then
                MISSING_TOOLS+=("lsof")
            fi
            ;;
    esac
done

# Install missing packages if any
if [ ${#MISSING_PACKAGES[@]} -gt 0 ] || [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    print_status "📦 Installing missing system packages..."
    
    ALL_MISSING=("${MISSING_PACKAGES[@]}" "${MISSING_TOOLS[@]}")
    
    if command -v apk >/dev/null 2>&1; then
        # Alpine Linux
        print_status "🏔️  Installing packages for Alpine Linux: ${ALL_MISSING[*]}"
        
        # Try with sudo first
        if sudo apk update && sudo apk add --no-cache "${ALL_MISSING[@]}" 2>/dev/null; then
            print_success "✅ System packages installed successfully"
        # If sudo fails, try without sudo (in case user is root)
        elif apk update && apk add --no-cache "${ALL_MISSING[@]}" 2>/dev/null; then
            print_success "✅ System packages installed successfully"
        else
            print_warning "⚠️  Failed to install some system packages automatically."
            print_warning "   Please run manually as root or with sudo:"
            print_warning "   apk update && apk add --no-cache ${ALL_MISSING[*]}"
            print_warning "   Continuing setup anyway..."
        fi
    else
        print_warning "⚠️  Package manager not found or not supported. Please manually install: ${ALL_MISSING[*]}"
    fi
else
    print_success "✅ All required system packages are available"
fi

# Verify essential tools are working
print_status "🔍 Verifying essential tools..."
TOOLS_STATUS=()

if command -v ps >/dev/null 2>&1; then
    TOOLS_STATUS+=("✅ ps")
else
    TOOLS_STATUS+=("❌ ps")
fi

if command -v lsof >/dev/null 2>&1; then
    TOOLS_STATUS+=("✅ lsof")
else
    TOOLS_STATUS+=("❌ lsof")
fi

if command -v kill >/dev/null 2>&1; then
    TOOLS_STATUS+=("✅ kill")
else
    TOOLS_STATUS+=("❌ kill")
fi

print_status "   Tools status: ${TOOLS_STATUS[*]}"

# Warn if critical tools are missing
if [[ "${TOOLS_STATUS[*]}" == *"❌"* ]]; then
    print_warning "⚠️  Some process management tools are missing. The server may have limited functionality."
    print_warning "   Consider installing: apk add --no-cache procps util-linux lsof"
fi

# Check for Python 3
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "✅ Python 3 is available: $PYTHON_VERSION"
else
    print_error "❌ Python 3 is required but not found"
    print_error "   Please install Python 3: apk add --no-cache python3"
    exit 1
fi

# Check for pip
if ! python3 -m pip --version >/dev/null 2>&1; then
    print_error "❌ pip is required but not found"
    print_error "   Please install pip: apk add --no-cache py3-pip"
    exit 1
fi

# Check for Poetry and install if not available
if command -v poetry >/dev/null 2>&1; then
    print_success "✅ Poetry is available"
    POETRY_AVAILABLE=true
else
    print_warning "⚠️  Poetry not found. Installing Poetry..."
    
    # Install Poetry using the official installer
    if curl -sSL https://install.python-poetry.org | python3 -; then
        # Add Poetry to PATH for this session
        export PATH="$HOME/.local/bin:$PATH"
        
        # Check if Poetry is now available
        if command -v poetry >/dev/null 2>&1; then
            print_success "✅ Poetry installed successfully"
            POETRY_AVAILABLE=true
            
            # Add Poetry to shell profile for future sessions
            SHELL_PROFILE=""
            if [ -f "$HOME/.bashrc" ]; then
                SHELL_PROFILE="$HOME/.bashrc"
            elif [ -f "$HOME/.zshrc" ]; then
                SHELL_PROFILE="$HOME/.zshrc"
            elif [ -f "$HOME/.profile" ]; then
                SHELL_PROFILE="$HOME/.profile"
            fi
            
            if [ -n "$SHELL_PROFILE" ]; then
                if ! grep -q "/.local/bin" "$SHELL_PROFILE"; then
                    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_PROFILE"
                    print_status "📝 Added Poetry to PATH in $SHELL_PROFILE"
                fi
            fi
            
            print_status "💡 Note: You may need to restart your shell or run 'source ~/.bashrc' to use Poetry in new sessions"
        else
            print_warning "⚠️  Poetry installation completed but not found in PATH. Will use virtual environment setup."
            POETRY_AVAILABLE=false
        fi
    else
        print_warning "⚠️  Poetry installation failed. Will use virtual environment setup."
        POETRY_AVAILABLE=false
    fi
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

print_success "🎉 Setup complete!"
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

if [ "$POETRY_AVAILABLE" = true ]; then
    print_status "✨ Your environment is configured to use Poetry"
    print_status "💡 Poetry configuration:"
    print_status "   - Virtual environments will be created in project (.venv)"
    print_status "   - Dependencies are managed by Poetry"
    if [ -d ".venv" ]; then
        print_status "   - Project virtual environment is ready"
    fi
else
    print_status "✨ Your environment is configured to use a local virtual environment"
    print_warning "💡 Note: The virtual environment (.venv) will be automatically used by mockctl"
fi

print_status ""
print_status "🔧 Environment Details:"
print_status "   - Python: $(python3 --version)"
if command -v poetry >/dev/null 2>&1; then
    print_status "   - Poetry: $(poetry --version)"
fi
if [ -d ".venv" ]; then
    print_status "   - Virtual Environment: .venv (ready)"
else
    print_status "   - Virtual Environment: Will be created when needed"
fi
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
