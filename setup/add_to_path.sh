#!/bin/bash

# Add mockctl to PATH for existing installations
# This script can be run independently to add mockctl to the user's PATH

set -e

echo "🔗 Adding mockctl to PATH..."

# Get the project root directory (parent of setup directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

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

# Check if mockctl exists in project directory
if [ ! -f "./mockctl" ]; then
    print_error "❌ mockctl not found in project directory: $PROJECT_DIR"
    print_error "   Please ensure you're in the correct project structure"
    exit 1
fi

# Make mockctl executable if it isn't already
chmod +x mockctl

MOCKCTL_PATH="$PROJECT_DIR/mockctl"

print_status "📍 Project directory: $PROJECT_DIR"

# Create ~/.local/bin if it doesn't exist
mkdir -p "$HOME/.local/bin"
print_status "📁 Created ~/.local/bin directory"

# Handle existing mockctl in PATH
if [ -L "$HOME/.local/bin/mockctl" ]; then
    # Check if it points to our mockctl
    CURRENT_TARGET=$(readlink "$HOME/.local/bin/mockctl")
    if [ "$CURRENT_TARGET" = "$MOCKCTL_PATH" ]; then
        print_success "✅ mockctl is already correctly linked to this project"
        exit 0
    else
        print_warning "⚠️  mockctl symlink exists but points to different location:"
        print_warning "     Current: $CURRENT_TARGET"
        print_warning "     New:     $MOCKCTL_PATH"
        print_warning "   Updating symlink..."
        rm "$HOME/.local/bin/mockctl"
    fi
elif [ -f "$HOME/.local/bin/mockctl" ]; then
    print_warning "⚠️  mockctl file exists in PATH, backing up and replacing..."
    mv "$HOME/.local/bin/mockctl" "$HOME/.local/bin/mockctl.backup.$(date +%s)"
fi

# Create symlink to mockctl
if ln -s "$MOCKCTL_PATH" "$HOME/.local/bin/mockctl" 2>/dev/null; then
    print_success "✅ mockctl symlink created in ~/.local/bin"
    LINK_TYPE="symlink"
else
    # If symlink fails, create a wrapper script
    print_status "🔧 Creating mockctl wrapper script..."
    cat > "$HOME/.local/bin/mockctl" << EOF
#!/bin/bash
# Auto-generated mockctl wrapper for $PROJECT_DIR
exec "$MOCKCTL_PATH" "\$@"
EOF
    chmod +x "$HOME/.local/bin/mockctl"
    print_success "✅ mockctl wrapper script created in ~/.local/bin"
    LINK_TYPE="wrapper script"
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

print_success "🎉 mockctl PATH setup complete!"
print_status ""
print_status "📖 Usage:"
print_status "  mockctl start <config_name>     # Start a mock server (global command)"
print_status "  mockctl stop                    # Stop all servers"
print_status "  mockctl list                    # List running servers"
print_status "  mockctl --help                  # Show help"
print_status ""
print_status "🔧 Setup Details:"
print_status "   - Project: $PROJECT_DIR"
print_status "   - Link type: $LINK_TYPE"
print_status "   - Target: ~/.local/bin/mockctl"

if [ "$PATH_ADDED" = true ]; then
    print_warning ""
    print_warning "💡 Note: You may need to restart your shell or run 'source ~/.bashrc' to use 'mockctl' globally"
    print_status "   Alternatively, you can test it now with a new terminal session"
else
    print_success ""
    print_success "🎯 You can now use 'mockctl' from anywhere!"
fi

# Test the command
print_status ""
print_status "🧪 Testing mockctl command..."
if command -v mockctl >/dev/null 2>&1; then
    print_success "✅ mockctl is available in current session"
    print_status "   Version check:"
    mockctl --version 2>/dev/null || print_status "   Use 'mockctl --help' for usage information"
else
    print_warning "⚠️  mockctl not yet available in current session"
    print_status "   Try: source ~/.bashrc (or restart your shell)"
fi
