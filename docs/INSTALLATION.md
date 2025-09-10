# Installation Guide

Complete installation instructions for Mock-and-Roll across different platforms.

## System Requirements

**Supported Platforms:**

- macOS 10.15+ (Catalina or later)
- Linux (Ubuntu 18.04+, CentOS 7+, Debian 9+, etc.)
- Windows 10+ (via WSL recommended)

**Required Software:**

- Python 3.11+ 
- Git

**Optional (Enhanced Features):**

- Redis Server (for persistence configuration)
- Docker & Docker Compose (for containerized deployment)

## macOS Installation

```bash
# Install Python 3.11+ (if not already installed)
# Option 1: Using Homebrew
brew install python@3.11

# Option 2: Using pyenv
brew install pyenv
pyenv install 3.11.7
pyenv local 3.11.7

# Install Poetry (recommended)
curl -sSL https://install.python-poetry.org | python3 -

# Clone and setup project
git clone <repository-url>
cd mock-and-roll

# Install dependencies with Poetry
poetry install

# Or install with pip if Poetry not available
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # or pip install fastapi uvicorn redis psutil requests

# Optional: Install Redis for persistence features
brew install redis
brew services start redis
```

## Linux Installation

### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install Python 3.11+ and pip
sudo apt install python3.11 python3.11-venv python3-pip git

# Install Poetry (recommended)
curl -sSL https://install.python-poetry.org | python3 -

# Clone and setup project
git clone <repository-url>
cd mock-and-roll

# Install dependencies with Poetry
poetry install

# Or install with pip if Poetry not available
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn redis psutil requests

# Optional: Install Redis for persistence features
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### CentOS/RHEL/Fedora

```bash
# CentOS/RHEL
sudo yum install python3 python3-pip git
# OR for Fedora
sudo dnf install python3 python3-pip git

# Install Poetry (recommended)
curl -sSL https://install.python-poetry.org | python3 -

# Clone and setup project
git clone <repository-url>
cd mock-and-roll

# Install dependencies with Poetry
poetry install

# Or install with pip if Poetry not available
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn redis psutil requests

# Optional: Install Redis for persistence features
# CentOS/RHEL
sudo yum install redis
sudo systemctl start redis
sudo systemctl enable redis
# OR for Fedora
sudo dnf install redis
sudo systemctl start redis
sudo systemctl enable redis
```

### Alpine Linux

Alpine Linux requires additional system tools for proper operation:

```bash
# Essential package installation
apk update
apk add --no-cache python3 py3-pip git

# Install command-line tools required by the server management
apk add --no-cache procps util-linux coreutils findutils
apk add --no-cache net-tools iproute2 lsof curl wget bash

# Install Poetry (recommended)
curl -sSL https://install.python-poetry.org | python3 -

# Clone and setup project
git clone <repository-url>
cd mock-and-roll

# 🚀 Quick Setup (Recommended for Alpine)
# Use the automated setup scripts for Alpine Linux

# Full setup (installs Poetry, system packages, creates venv, adds mockctl to PATH)
setup/alpine.sh

# Or minimal setup (only user-level, no admin privileges required, adds mockctl to PATH)
setup/alpine_minimal.sh

# Or manual setup:
# Install dependencies with Poetry
poetry install

# Or install with pip if Poetry not available
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Optional: Install Redis for persistence features
apk add --no-cache redis
rc-service redis start
rc-update add redis
```

**Alpine Package Breakdown:**
- `procps` - Provides `ps`, `top`, `pgrep`, `pkill` for process management
- `util-linux` - Provides `kill`, `lscpu` for process termination
- `coreutils` - Essential text processing tools (`grep`, `awk`, `cut`, `sort`)
- `net-tools` - Network diagnostics (`netstat`, `ifconfig`)
- `iproute2` - Modern networking tools (`ss`, `ip`)
- `lsof` - List open files/ports for server detection
- `bash` - Better shell compatibility for scripts

**Minimal Alpine Installation:**
For minimal setups, only these packages are essential:
```bash
apk add --no-cache procps lsof
```

**Docker Alpine Usage:**
Use the provided Alpine Dockerfile for containerized deployment:
```bash
# Build Alpine-based image
docker build -f Dockerfile.alpine -t mock-server-alpine .

# Run Alpine container
docker run -p 8000:8000 mock-server-alpine
```

## Docker Installation (Cross-platform)

```bash
# Clone the repository
git clone <repository-url>
cd mock-and-roll

# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t mock-server .
docker run -p 8000:8000 mock-server
```

## Verification

```bash
# Verify Python version
python3 --version  # Should show 3.11+

# Verify installation
./mockctl --help

# Test basic functionality
./mockctl start basic --port 8000
# In another terminal:
curl http://localhost:8000/
./mockctl stop
```

## Dependencies

**Core Dependencies (automatically installed):**
- `fastapi` - Modern web framework
- `uvicorn` - ASGI server
- `redis` - Redis client (for persistence features)
- `psutil` - Process management utilities
- `requests` - HTTP client library
- `pyhumps` - JSON key transformation
- `pyjwt` - JWT token handling
- `python-dateutil` - Date parsing utilities
- `python-multipart` - Form data handling
- `email-validator` - Email validation

**Development Dependencies:**
- `pytest` - Testing framework
- `python-dotenv` - Environment variable management
- `pre-commit` - Git hooks for code quality

## Troubleshooting Installation

**Common Issues:**

1. **Python version too old**
   ```bash
   # Check version
   python3 --version
   # Upgrade if needed (see platform-specific instructions above)
   ```

2. **Permission errors on macOS/Linux**
   ```bash
   # Use virtual environment to avoid system-wide installs
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   ```

3. **Poetry not found**
   ```bash
   # Add Poetry to PATH (typically needed after installation)
   export PATH="$HOME/.local/bin:$PATH"
   # Add to ~/.bashrc or ~/.zshrc for persistence
   ```

4. **Redis connection errors**
   ```bash
   # Check if Redis is running
   redis-cli ping  # Should return PONG
   # Start Redis if needed (see platform-specific instructions above)
   ```

5. **Alpine Linux - externally-managed-environment error**
   ```bash
   # If you see "externally-managed-environment" when trying to install packages:
   
   # Option 1: Full automated setup (installs Poetry, system packages)
   setup/alpine.sh
   
   # Option 2: Minimal setup (no admin privileges required)
   setup/alpine_minimal.sh
   
   # Option 3: Manual virtual environment setup
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   
   # Option 3: Use Poetry (if available)
   poetry config virtualenvs.in-project true
   poetry install
   ```

## Post-Installation Setup

After successful installation, see the main [README.md](../README.md) for:
- Quick start guide
- Configuration options
- Usage examples
- CLI command reference
