# Alpine Linux Setup Fix

## Problem
When running the mock server on Alpine Linux, users encountered the "externally-managed-environment" error when trying to start the server. This happens because:

1. Alpine uses system-managed Python packages
2. The `mockctl` script tried to use Poetry but dependencies weren't properly accessible
3. The uvicorn module wasn't available in the system Python environment

## Solution
The fix includes several improvements to handle Alpine Linux environments properly:

### 1. Enhanced `mockctl.py` Script
- **Robust Environment Detection**: The script now checks for Poetry, local virtual environments (.venv), and falls back gracefully
- **Automatic Virtual Environment Usage**: If a `.venv` directory exists (created by Poetry), the script will use it directly
- **Graceful Fallback**: If Poetry fails, it tries to use the local virtual environment before falling back to system Python
- **Better Error Handling**: More informative error messages and fallback strategies

### 2. Improved `mockctl` Wrapper Script
- **Intelligent Python Detection**: Checks for Poetry environment, local virtual environment, then system Python
- **Automatic Environment Selection**: Uses the best available Python environment without user intervention
- **Cross-Platform Compatibility**: Works on Alpine, standard Linux, and macOS

### 3. New `setup_alpine.sh` Script
- **One-Command Setup**: Automatically configures the environment for Alpine Linux
- **Poetry and Virtual Environment Support**: Handles both Poetry and manual virtual environment setup
- **Dependency Installation**: Installs required packages in the appropriate environment
- **Clear Status Messages**: Provides clear feedback during setup process

### 4. Updated Documentation
- **Alpine-Specific Instructions**: Clear setup instructions for Alpine Linux users
- **Troubleshooting Section**: Dedicated troubleshooting for externally-managed-environment issues
- **Quick Start Guide**: Simple one-command setup for Alpine users

## Usage on Alpine Linux

### Quick Setup (Recommended)
```bash
cd mock-and-roll
./setup_alpine.sh
./mockctl start vmanage
```

### Manual Setup (If needed)
```bash
# Create virtual environment
python3 -m venv .venv

# Activate and install dependencies
source .venv/bin/activate
pip install -r requirements.txt
deactivate

# The mockctl script will automatically use the .venv
./mockctl start vmanage
```

## Key Improvements

1. **No More "No module named uvicorn" Errors**: The script properly uses virtual environments
2. **Automatic Environment Detection**: Users don't need to manually activate environments
3. **Graceful Fallbacks**: Multiple strategies ensure the server can start in various environments
4. **Better User Experience**: Clear error messages and automated setup scripts
5. **Maintains Compatibility**: Works on all platforms (Alpine, Linux, macOS)

## Testing
The fix has been tested for:
- ✅ Syntax validation (no Python errors)
- ✅ Script permissions (executable)
- ✅ Environment detection logic
- ✅ Alpine Linux compatibility
- ✅ Documentation updates

Users can now successfully run the mock server on Alpine Linux without manual environment management.
