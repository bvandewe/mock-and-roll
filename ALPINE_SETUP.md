# Alpine Linux Setup Guide for Mock Server

This guide helps you set up the required command-line tools in Alpine Linux to run the mock server successfully.

## Quick Setup

Run the provided setup script:
```bash
./setup_alpine.sh
```

## Manual Installation

If you prefer to install tools manually, here are the commands:

### Essential Tools
```bash
# Update package index
apk update

# Install process and system tools
apk add --no-cache procps util-linux coreutils findutils

# Install networking tools
apk add --no-cache net-tools iproute2 lsof curl wget

# Install bash for better scripting
apk add --no-cache bash
```

### Package Breakdown

| Package | Provides | Why Needed |
|---------|----------|------------|
| `procps` | `ps`, `top`, `pgrep`, `pkill` | Process management for stop scripts |
| `util-linux` | `kill`, `lscpu`, etc. | Process termination |
| `coreutils` | `grep`, `awk`, `cut`, `sort` | Text processing in scripts |
| `net-tools` | `netstat`, `ifconfig` | Network diagnostics |
| `iproute2` | `ss`, `ip` | Modern networking tools |
| `lsof` | `lsof` | List open files/ports |
| `curl` | `curl` | HTTP testing |
| `bash` | `bash` | Better shell for scripts |

### Optional Development Tools
```bash
# Text editors
apk add --no-cache nano vim

# Additional utilities
apk add --no-cache less grep sed awk

# Git (if not installed)
apk add --no-cache git
```

## Docker Setup

Use the provided `Dockerfile.alpine` for a complete Alpine-based container:

```bash
# Build the Alpine image
docker build -f Dockerfile.alpine -t mock-server-alpine .

# Run the container
docker run -p 8000:8000 mock-server-alpine
```

## Verification

After installation, verify the tools are available:

```bash
# Check process tools
ps --version
kill -V

# Check networking tools
netstat --version
lsof -v
ss --version

# Check text processing
grep --version
awk --version
```

## Common Alpine Differences

Alpine's BusyBox implementations may behave differently:

1. **lsof**: Use `lsof -i :8000` instead of `lsof -ti:8000`
2. **ps**: Some flags may differ from GNU ps
3. **grep**: BusyBox grep vs GNU grep differences

The stop script has been updated to handle these differences automatically.

## Troubleshooting

If you encounter "command not found" errors:

1. Run `./setup_alpine.sh`
2. Or use the fallback script: `./kill_all_servers.sh`
3. Check which tools are missing: `which <command>`

## Minimal Installation

For the absolute minimum setup, you only need:
```bash
apk add --no-cache procps lsof
```

This provides the essential `ps` and `lsof` commands for the stop script.
