#!/bin/sh

# Alpine Linux Setup Script for Mock Server
# This script installs additional command-line tools that may be needed
# Run this script in your Alpine container to install missing tools

echo "🐧 Setting up Alpine Linux environment for Mock Server..."

# Update package index
echo "📦 Updating package index..."
apk update

# Install essential networking and process tools
echo "🔧 Installing essential tools..."

# Process and system tools
apk add --no-cache \
    procps \
    util-linux \
    coreutils \
    findutils

# Networking tools
apk add --no-cache \
    net-tools \
    iproute2 \
    lsof \
    curl \
    wget

# Development and debugging tools (optional)
echo "🛠️  Installing development tools..."
apk add --no-cache \
    bash \
    grep \
    sed \
    awk \
    less \
    nano \
    vim \
    jq

# Git (if not already installed)
apk add --no-cache git

echo "✅ Alpine Linux setup complete!"
echo ""
echo "📋 Installed tools:"
echo "   - procps (ps, top, etc.)"
echo "   - util-linux (kill, etc.)"
echo "   - coreutils (standard utilities)"
echo "   - net-tools (netstat, etc.)"
echo "   - iproute2 (ss, ip, etc.)"
echo "   - lsof (list open files)"
echo "   - curl/wget (HTTP tools)"
echo "   - bash (better shell)"
echo "   - text editors (nano, vim)"
echo "   - JSON processor (jq)"
echo ""
echo "🚀 Your environment is now ready for the mock server!"
