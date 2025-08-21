# Scripts Organization

All shell scripts have been organized into the `scripts/` directory for better project structure and maintainability.

## 📁 Directory Structure

```
scripts/
├── help.sh                    # Lists all available scripts with descriptions
├── start_vmanage_api.sh      # Start the mock server
├── stop_vmanage_api.sh       # Stop the mock server  
├── get_logs.sh               # Fetch and filter server logs
├── kill_all_servers.sh       # Emergency kill all server processes
├── list_servers.sh           # List running servers
├── test_vmanage_api.sh       # Test the API endpoints
├── setup_environment.sh      # Environment setup
└── setup_alpine.sh           # Alpine Linux setup tools
```

## 🚀 Usage Options

### Option 1: Direct Script Access
```bash
./scripts/start_vmanage_api.sh
./scripts/get_logs.sh /dataservice/device
./scripts/stop_vmanage_api.sh
```

### Option 2: Using the Wrapper Script (Recommended)
```bash
./run.sh start_vmanage_api
./run.sh get_logs /dataservice/device  
./run.sh stop_vmanage_api
```

### Option 3: Backward Compatibility (Symbolic Links)
```bash
./start_vmanage_api.sh    # Links to scripts/start_vmanage_api.sh
./stop_vmanage_api.sh     # Links to scripts/stop_vmanage_api.sh
```

## 📋 Getting Help

### Show all available scripts:
```bash
./run.sh                    # Shows help automatically
./scripts/help.sh           # Direct help access
```

### Get help for specific scripts:
```bash
./run.sh SCRIPT_NAME --help
./scripts/SCRIPT_NAME.sh --help
```

## 🔧 Script Categories

### 🚀 **Server Operations**
- `start_vmanage_api.sh` - Start the mock server
- `stop_vmanage_api.sh` - Stop the mock server gracefully
- `kill_all_servers.sh` - Force kill all server processes
- `list_servers.sh` - List running server instances

### 📊 **Monitoring & Debugging**
- `get_logs.sh` - Fetch and filter server logs by endpoint
- `test_vmanage_api.sh` - Test API endpoints

### ⚙️ **Setup & Environment**
- `setup_environment.sh` - General environment setup
- `setup_alpine.sh` - Alpine Linux specific setup

### 🛠️ **Utilities**
- `help.sh` - Script documentation and help

## 🌟 Benefits of This Organization

1. **Clean Project Root** - Main directory is less cluttered
2. **Easy Discovery** - `./run.sh` shows all available scripts
3. **Backward Compatibility** - Existing workflows still work
4. **Better Documentation** - Each script category is clearly defined
5. **Maintainability** - Scripts are grouped logically

## 🚀 Quick Start Examples

```bash
# Get help
./run.sh

# Start server
./run.sh start_vmanage_api

# Monitor logs
./run.sh get_logs

# Filter logs by endpoint
./run.sh get_logs /dataservice/device

# Stop server
./run.sh stop_vmanage_api
```
