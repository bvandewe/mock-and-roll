# Quick Start Guide

Get up and running with Mock-and-Roll in just a few minutes!

## Prerequisites

- Python 3.11+
- Git

## 🚀 Quick Installation

### Option 1: Using Setup Script (Recommended)

```bash
# Clone the repository
git clone https://github.com/bvandewe/mock-and-roll.git
cd mock-and-roll

# Run the setup script (Alpine Linux / minimal environments)
./setup/alpine_minimal.sh

# For other platforms, see our installation guide
```

### Option 2: Manual Setup

```bash
# Clone and enter directory
git clone https://github.com/bvandewe/mock-and-roll.git
cd mock-and-roll

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Make CLI executable
chmod +x mockctl
```

## 🎯 Your First Mock Server

### Start a Basic Server

```bash
# Start with the basic configuration
./mockctl start basic

# The server will start on http://localhost:8000
# Swagger docs available at http://localhost:8000/docs
```

### Test Your Server

```bash
# In another terminal, test the API
curl http://localhost:8000/api/health

# Expected response:
# {"status": "healthy", "timestamp": "2025-01-01T12:00:00Z"}
```

## 🔍 Exploring Features

### View Available Commands

```bash
./mockctl --help

# Common commands:
# start <config>  - Start a mock server
# stop           - Stop servers  
# list           - List running servers
# search <pattern> - Search logs
# version        - Show version information

# Global options:
# --json        - Output in JSON format
# --no-emoji    - Remove emojis from output
# --version/-v  - Show version information
```

### List Running Servers

```bash
./mockctl list

# Clean output without emojis
./mockctl --no-emoji list

# Example output:
# Running Mock Servers:
# Config: basic | PID: 12345 | Port: 8000 | Status: ✅ running
```

### Search Server Logs

```bash
# Search for API requests
./mockctl --json search "/api"

# Search for authentication requests
./mockctl search "/auth"

# Clean search output without emojis
./mockctl --no-emoji search "/auth"

# Search with regex patterns
./mockctl search "POST.*login"
```

## 📋 Configuration Profiles

Mock-and-Roll comes with three pre-configured profiles:

### Basic Profile
- Simple REST API endpoints
- JSON responses
- No authentication required
- Perfect for testing and development

```bash
./mockctl start basic
```

### Persistence Profile
- All basic features
- Redis integration for data persistence
- Stateful responses
- User data management

```bash
# Requires Redis server running
./mockctl start persistence
```

### vManage Profile
- Cisco vManage API simulation
- Authentication workflows
- Network device management endpoints
- Realistic networking scenarios

```bash
./mockctl start vmanage
```

## 🐳 Docker Quick Start

### Using Docker Compose

```bash
# Start all services (includes Redis)
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Docker Directly

```bash
# Build the image
docker build -t mock-and-roll .

# Run basic server
docker run -p 8000:8000 mock-and-roll

# Run with custom config
docker run -p 8080:8080 -e CONFIG_NAME=vmanage mock-and-roll
```

## 🎨 Customizing Your Server

### Configuration Structure

```bash
configs/
├── basic/          # Simple mock API
├── persistence/    # With Redis persistence
└── vmanage/        # Cisco vManage simulation
```

### Creating Custom Endpoints

Edit `configs/<profile>/endpoints.json`:

```json
{
  "endpoints": [
    {
      "path": "/api/custom",
      "method": "GET",
      "response": {
        "message": "Hello from Mock-and-Roll!",
        "timestamp": "{{now}}"
      },
      "status_code": 200
    }
  ]
}
```

## 🔧 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Check what's running on port 8000
./mockctl list

# Stop all servers
./mockctl stop --all

# Or specify a different port
./mockctl start basic --port 8080
```

**Python/dependency issues:**
```bash
# Verify Python version
python3 --version  # Should be 3.11+

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

**Redis connection errors (persistence profile):**
```bash
# Check if Redis is running
redis-cli ping  # Should return "PONG"

# Start Redis (if installed)
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:alpine
```

### Getting Help

```bash
# Command help
./mockctl --help
./mockctl start --help

# Check server status
./mockctl list --verbose

# View recent logs
tail -f logs/latest.logs
```

## 🎉 What's Next?

You're now ready to explore Mock-and-Roll! Here are some next steps:

- **[Configuration Guide](configuration.md)**: Learn about advanced configuration options
- **[CLI Commands](user-guide/cli-commands.md)**: Master the `mockctl` tool
- **[Examples](examples/basic-usage.md)**: See real-world usage scenarios
- **[Architecture](architecture/overview.md)**: Understand how Mock-and-Roll works

## 💡 Pro Tips

1. **Use JSON output for automation:**
   ```bash
   ./mockctl --json search "/api" | jq '.total_requests'
   ```

2. **Monitor multiple servers:**
   ```bash
   watch './mockctl list'
   ```

3. **Quick configuration changes:**
   ```bash
   # Edit and restart
   vim configs/basic/endpoints.json
   ./mockctl stop
   ./mockctl start basic
   ```

Happy mocking! 🚀
