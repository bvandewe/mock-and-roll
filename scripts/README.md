# 🚀 Mock Server - Simplified Script System

This document describes the streamlined, generic script system for the Mock API Server.

## 📁 Project Structure

```
mock-and-roll/
├── run.sh                    # 🎯 Main entry point - simplified commands
├── scripts/                  # 📂 All server management scripts
│   ├── start_server.sh      # 🚀 Generic server starter (any config)
│   ├── stop_server.sh       # 🛑 Generic server stopper (any config)
│   ├── list_servers.sh      # 📋 List running servers (all configs)
│   ├── get_logs.sh          # 📊 Log viewer and filter
│   ├── success_report.sh    # 📈 Success rate analysis
│   ├── config_help.sh       # 📖 Configuration guide
│   ├── help.sh             # 🔧 Complete script documentation
│   ├── setup_alpine.sh     # 🐧 Alpine Linux setup
│   └── setup_environment.sh # ⚙️ Environment setup
├── configs/                 # 📂 Server configurations
│   ├── basic/              # 🟢 Simple REST API
│   ├── persistence/        # 🔴 Redis-enabled API
│   └── vmanage/            # 🟡 SD-WAN vManage API
└── logs/                   # 📝 Server logs
```

## 🎯 Quick Commands (via run.sh)

### 🚀 Server Management
```bash
# Start servers
./run.sh start                          # Interactive config selection
./run.sh start basic                    # Start basic config
./run.sh start vmanage --port 8001      # Start vmanage on custom port
./run.sh start persistence              # Start with Redis persistence

# Stop servers
./run.sh stop                           # Auto-detect or interactive
./run.sh stop basic                     # Stop by config name
./run.sh stop --all                     # Stop all servers
./run.sh stop --pid 12345               # Stop by process ID

# Status
./run.sh list                           # List running servers
./run.sh status                         # Alias for list
```

### 📊 Monitoring & Analysis
```bash
# Logs
./run.sh logs                           # Recent logs
./run.sh logs 100                       # Last 100 lines
./run.sh logs /login                    # Filter by endpoint

# Success analysis
./run.sh success                        # Success summary
./run.sh success detailed               # Detailed report
./run.sh success json                   # JSON output
```

### 📖 Help & Configuration
```bash
# Help
./run.sh help                           # All available scripts
./run.sh config-help                    # Configuration guide

# Or use scripts directly
./scripts/start_server.sh --help        # Detailed start options
./scripts/stop_server.sh --help         # Detailed stop options
```

## 🔧 Direct Script Usage

If you prefer using scripts directly instead of the `run.sh` helper:

```bash
# Server operations
./scripts/start_server.sh vmanage --port 8001
./scripts/stop_server.sh --all
./scripts/list_servers.sh

# Monitoring
./scripts/get_logs.sh /dataservice/device
./scripts/success_report.sh detailed

# Help
./scripts/help.sh
./scripts/config_help.sh
```

## 📂 Configuration System

### Available Configurations
- **basic**: Simple REST API with 1 endpoint
- **persistence**: API with Redis caching (12 endpoints)  
- **vmanage**: Cisco SD-WAN vManage API simulation (many endpoints)

### Configuration Structure
Each config in `configs/[NAME]/` contains:
- `api.json`: API metadata, persistence settings
- `auth.json`: Authentication rules and tokens
- `endpoints.json`: Route definitions and responses

### Creating Custom Configs
```bash
# Copy existing config
cp -r configs/basic configs/my-config

# Edit configuration files
# ... modify api.json, auth.json, endpoints.json ...

# Start with new config
./run.sh start my-config
```

## 🌐 Server Access

Once started, servers are available at:
- **Main API**: `http://localhost:PORT/`
- **Interactive Docs**: `http://localhost:PORT/docs`
- **OpenAPI Schema**: `http://localhost:PORT/openapi.json`

## 📝 Logging

- **File**: `logs/latest.logs` (automatic rotation)
- **Console**: Real-time output to terminal
- **Levels**: DEBUG, INFO, WARNING, ERROR
- **Format**: Timestamp, correlation IDs, request/response details

## 🛠️ Removed Legacy Scripts

The following legacy scripts have been removed and replaced:
- ❌ `start_vmanage_api.sh` → ✅ `start_server.sh vmanage`
- ❌ `stop_vmanage_api.sh` → ✅ `stop_server.sh`
- ❌ `kill_all_servers.sh` → ✅ `stop_server.sh --all`
- ❌ `test_vmanage_api.sh` → ✅ Generic testing via curl/API calls
- ❌ `run_server.py` → ✅ Direct uvicorn with environment variables

## 🐧 Alpine Compatibility

All scripts are optimized for both macOS (bash 3.x) and Alpine Linux (bash 5.x+):
- ✅ Cross-platform process management
- ✅ Compatible command syntax
- ✅ Environment variable handling
- ✅ File path resolution

## 🎉 Benefits of New System

1. **🎯 Simplified**: One command (`./run.sh start`) for any configuration
2. **🔧 Flexible**: Interactive or CLI-driven server management
3. **📊 Comprehensive**: Built-in monitoring, logging, and analysis
4. **🌐 Generic**: Works with any configuration, not just vManage
5. **🐧 Cross-platform**: macOS and Alpine Linux compatible
6. **📖 Self-documenting**: Extensive help and examples built-in

## 💡 Quick Start Examples

```bash
# 1. Start server interactively
./run.sh start

# 2. View running servers  
./run.sh list

# 3. Check recent activity
./run.sh logs

# 4. Generate success report
./run.sh success

# 5. Stop all servers
./run.sh stop --all

# 6. Get help
./run.sh help
```

This streamlined system provides a much cleaner, more maintainable, and user-friendly way to manage the Mock API Server across all configurations! 🚀
