#!/usr/bin/env python3
"""
Mock Server Control CLI
A unified Python CLI tool that manages mock server instances.
"""

import argparse
import json
import os
import secrets
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    MAGENTA = "\033[0;35m"
    NC = "\033[0m"  # No Color


class ProcessUtils:
    """Utility class for process management with fallback methods"""

    @staticmethod
    def pid_exists(pid: int) -> bool:
        """Check if process exists"""
        if HAS_PSUTIL:
            return psutil.pid_exists(pid)
        else:
            # Fallback using os.kill with signal 0
            try:
                os.kill(pid, 0)
                return True
            except (OSError, ProcessLookupError):
                return False

    @staticmethod
    def find_process_by_port(port: int) -> Optional[int]:
        """Find process ID using a specific port"""
        if HAS_PSUTIL:
            try:
                for conn in psutil.net_connections(kind="inet"):
                    if hasattr(conn, "laddr") and conn.laddr and hasattr(conn.laddr, "port"):
                        if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                            return conn.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        else:
            # Fallback using lsof/netstat
            try:
                # Try lsof first
                result = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    return int(result.stdout.strip().split("\n")[0])
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError, FileNotFoundError):
                pass

            try:
                # Try netstat as fallback
                result = subprocess.run(["netstat", "-tulpn"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.split("\n"):
                        if f":{port} " in line:
                            parts = line.split()
                            for part in parts:
                                if "/" in part:
                                    try:
                                        return int(part.split("/")[0])
                                    except ValueError:
                                        continue
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                pass

        return None

    @staticmethod
    def is_mock_server_process(pid: int) -> bool:
        """Check if process is our mock server"""
        if HAS_PSUTIL:
            try:
                process = psutil.Process(pid)
                cmdline = " ".join(process.cmdline())
                return "python" in cmdline and ("uvicorn" in cmdline or "main:app" in cmdline)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                return False
        else:
            # Fallback using ps
            try:
                result = subprocess.run(["ps", "-p", str(pid), "-o", "command="], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    cmdline = result.stdout.strip()
                    return "python" in cmdline and ("uvicorn" in cmdline or "main:app" in cmdline)
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                pass

        return False

    @staticmethod
    def terminate_process(pid: int, timeout: int = 10) -> bool:
        """Terminate process gracefully with fallback to force kill"""
        if HAS_PSUTIL:
            try:
                process = psutil.Process(pid)
                process.terminate()

                try:
                    process.wait(timeout=timeout)
                    return True
                except psutil.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                    return True

            except psutil.NoSuchProcess:
                return True  # Already dead
            except psutil.AccessDenied:
                return False
            except Exception:
                return False
        else:
            # Fallback using kill command
            try:
                # Try SIGTERM first
                subprocess.run(["kill", str(pid)], check=True, timeout=5)

                # Wait for process to die
                for _ in range(timeout):
                    if not ProcessUtils.pid_exists(pid):
                        return True
                    time.sleep(1)

                # Force kill if still alive
                subprocess.run(["kill", "-9", str(pid)], check=True, timeout=5)

                # Wait a bit more
                for _ in range(5):
                    if not ProcessUtils.pid_exists(pid):
                        return True
                    time.sleep(1)

                return False

            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                return False

    @staticmethod
    def list_mock_server_processes() -> list[dict]:
        """List all mock server processes"""
        processes = []

        if HAS_PSUTIL:
            try:
                for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                    try:
                        if ProcessUtils.is_mock_server_process(proc.info["pid"]):
                            processes.append({"pid": proc.info["pid"], "cmdline": " ".join(proc.info["cmdline"])})
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception:
                pass
        else:
            # Fallback using ps
            try:
                result = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    for line in result.stdout.split("\n")[1:]:  # Skip header
                        if "python" in line and ("uvicorn" in line or "main:app" in line):
                            parts = line.split(None, 10)
                            if len(parts) >= 2:
                                try:
                                    pid = int(parts[1])
                                    processes.append({"pid": pid, "cmdline": parts[-1] if len(parts) > 10 else line})
                                except ValueError:
                                    continue
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                pass

        return processes

    @staticmethod
    def find_next_available_port(start_port: int = 8000, max_attempts: int = 100) -> int:
        """
        Find the next available port starting from start_port.

        Args:
            start_port: Port to start searching from (default: 8000)
            max_attempts: Maximum number of ports to try (default: 100)

        Returns:
            Next available port number

        Raises:
            RuntimeError: If no available port is found within max_attempts
        """
        for port in range(start_port, start_port + max_attempts):
            if ProcessUtils.find_process_by_port(port) is None:
                return port

        raise RuntimeError(f"No available port found in range {start_port}-{start_port + max_attempts - 1}")


class ServerState:
    """Manages server state tracking"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.state_dir = project_root / ".server_state"
        self.servers_file = self.state_dir / "servers.json"
        self._ensure_state_dir()

    def _ensure_state_dir(self):
        """Ensure state directory and file exist"""
        self.state_dir.mkdir(exist_ok=True)
        if not self.servers_file.exists():
            self._save_servers([])

    def _load_servers(self) -> list[dict]:
        """Load servers from state file"""
        try:
            with open(self.servers_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_servers(self, servers: list[dict]):
        """Save servers to state file"""
        with open(self.servers_file, "w") as f:
            json.dump(servers, f, indent=2)

    def add_server(self, config_name: str, port: int, pid: int, host: str = "0.0.0.0"):
        """Add a server to state tracking"""
        servers = self._load_servers()

        # Remove any existing entries for this config/port
        servers = [s for s in servers if s.get("config") != config_name and s.get("port") != port]

        # Generate unique log file path with random prefix
        random_prefix = secrets.token_hex(4)  # 8 character hex string
        log_file = f"logs/{random_prefix}_{config_name}_{port}.logs"

        new_server = {"config": config_name, "port": port, "pid": pid, "host": host, "started_at": datetime.now(timezone.utc).isoformat(), "status": "running", "log_file": log_file}

        servers.append(new_server)
        self._save_servers(servers)
        print(f"{Colors.GREEN}✅ Added server to state: {config_name} (PID: {pid}, Port: {port}){Colors.NC}")

    def get_server_by_port(self, port: int) -> Optional[dict]:
        """Get server info by port"""
        servers = self._load_servers()
        for server in servers:
            if server.get("port") == port and server.get("status") == "running":
                return server
        return None

    def get_server_by_config(self, config_name: str) -> Optional[dict]:
        """Get server info by config name"""
        servers = self._load_servers()
        for server in servers:
            if server.get("config") == config_name:
                return server
        return None

    def remove_server_by_pid(self, pid: int):
        """Remove server by PID"""
        servers = self._load_servers()
        servers = [s for s in servers if s.get("pid") != pid]
        self._save_servers(servers)

    def remove_server_by_config(self, config_name: str):
        """Remove server by config name"""
        servers = self._load_servers()
        servers = [s for s in servers if s.get("config") != config_name]
        self._save_servers(servers)

    def remove_server_by_port(self, port: int):
        """Remove server by port"""
        servers = self._load_servers()
        servers = [s for s in servers if s.get("port") != port]
        self._save_servers(servers)

    def get_all_servers(self) -> list[dict]:
        """Get all tracked servers"""
        return self._load_servers()

    def cleanup_dead_processes(self):
        """Remove servers with dead processes"""
        servers = self._load_servers()
        alive_servers = []

        for server in servers:
            pid = server.get("pid")
            if pid and ProcessUtils.pid_exists(pid):
                alive_servers.append(server)

        self._save_servers(alive_servers)


class MockServerCLI:
    """Main CLI application"""

    def __init__(self):
        # Get the project root (two levels up from src/cli/mockctl.py)
        self.project_root = Path(__file__).parent.parent.parent
        self.configs_dir = self.project_root / "configs"
        self.state = ServerState(self.project_root)
        self.default_host = "0.0.0.0"
        self.default_port = 8000

    def main(self):
        """Main entry point"""
        parser = self.create_parser()
        args = parser.parse_args()

        if hasattr(args, "func"):
            try:
                args.func(args)
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}⚠️  Operation cancelled{Colors.NC}")
                sys.exit(1)
            except Exception as e:
                print(f"{Colors.RED}❌ Error: {e}{Colors.NC}")
                sys.exit(1)
        else:
            parser.print_help()

    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            description="🚀 Mock API Server Management",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s start                     # Interactive config selection
  %(prog)s start basic               # Start basic configuration
  %(prog)s start vmanage --port 8080 # Start vManage config on port 8080
  %(prog)s stop                      # Stop servers (auto-detect)
  %(prog)s list                      # Show running servers
  %(prog)s logs --lines 100          # Show last 100 log lines
  %(prog)s search /api/users         # Search for requests to /api/users
  %(prog)s search /items --since 1h  # Search for /items requests in last hour
  %(prog)s test --port 8000          # Test API endpoints on port 8000
  %(prog)s success detailed          # Detailed success analysis

📂 Available configurations: basic, persistence, vmanage
            """,
        )

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Start command
        start_parser = subparsers.add_parser("start", help="Start mock server")
        start_parser.add_argument("config", nargs="?", help="Configuration name (interactive if omitted)")
        start_parser.add_argument("--port", type=int, help="Server port")
        start_parser.add_argument("--host", default=self.default_host, help="Server host")
        start_parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
        start_parser.set_defaults(func=self.cmd_start)

        # Stop command
        stop_parser = subparsers.add_parser("stop", help="Stop mock server")
        stop_parser.add_argument("config", nargs="?", help="Configuration name (auto-detect if omitted)")
        stop_parser.add_argument("--port", type=int, help="Stop server on specific port")
        stop_parser.add_argument("--pid", type=int, help="Stop specific process ID")
        stop_parser.add_argument("--all", action="store_true", help="Stop all servers")
        stop_parser.set_defaults(func=self.cmd_stop)

        # List command
        list_parser = subparsers.add_parser("list", help="List running servers")
        list_parser.set_defaults(func=self.cmd_list)

        # Status command (alias for list)
        status_parser = subparsers.add_parser("status", help="Show server status (alias for list)")
        status_parser.set_defaults(func=self.cmd_list)

        # Logs command
        logs_parser = subparsers.add_parser("logs", help="View server logs")
        logs_parser.add_argument("--lines", type=int, default=500, help="Number of recent lines")
        logs_parser.add_argument("--port", type=int, help="Server port (auto-detect if omitted)")
        logs_parser.add_argument("--host", default="localhost", help="Server host")
        logs_parser.add_argument("--filter", help="Optional endpoint filter pattern")
        logs_parser.set_defaults(func=self.cmd_logs)

        # Test command
        test_parser = subparsers.add_parser("test", help="Test server endpoints")
        test_parser.add_argument("--port", type=int, required=True, help="Server port")
        test_parser.add_argument("--host", default="localhost", help="Server host")
        test_parser.add_argument("--config", default="configs/basic", help="Configuration directory")
        test_parser.add_argument("--api-key", help="System API key (auto-detected if not provided)")
        test_parser.set_defaults(func=self.cmd_test)

        # Success command
        success_parser = subparsers.add_parser("success", help="Generate success rate report")
        success_parser.add_argument("format", nargs="?", default="summary", choices=["summary", "detailed", "json"], help="Report format")
        success_parser.add_argument("--port", type=int, help="Server port (auto-detect if omitted)")
        success_parser.add_argument("--lines", type=int, default=10000, help="Number of log lines to analyze")
        success_parser.set_defaults(func=self.cmd_success)

        # Config-help command
        config_help_parser = subparsers.add_parser("config-help", help="Show configuration guide")
        config_help_parser.set_defaults(func=self.cmd_config_help)

        # Search command
        search_parser = subparsers.add_parser("search", help="Search server logs for requests to specific paths")
        search_parser.add_argument("path", help="Path to search for in logs (e.g., '/api/users', '/items')")
        search_parser.add_argument("--port", type=int, help="Server port (auto-detect if omitted)")
        search_parser.add_argument("--lines", type=int, default=10000, help="Number of log lines to analyze (default: 10000)")
        search_parser.add_argument("--since", help="Search logs since date/time (e.g., '2025-08-22 10:00', 'today', '1h ago')")
        search_parser.set_defaults(func=self.cmd_search)

        # Help command
        help_parser = subparsers.add_parser("help", help="Show detailed help information")
        help_parser.set_defaults(func=self.cmd_help)

        return parser

    def list_available_configs(self) -> list[str]:
        """List available configuration directories"""
        if not self.configs_dir.exists():
            return []

        configs = []
        for item in self.configs_dir.iterdir():
            if item.is_dir():
                configs.append(item.name)
        return sorted(configs)

    def validate_config(self, config_name: str) -> bool:
        """Validate configuration directory and files"""
        config_path = self.configs_dir / config_name

        if not config_path.exists():
            print(f"{Colors.RED}❌ Error: Configuration '{config_name}' not found{Colors.NC}")
            available = self.list_available_configs()
            if available:
                print(f"{Colors.YELLOW}💡 Available configurations: {', '.join(available)}{Colors.NC}")
            return False

        required_files = ["api.json", "auth.json", "endpoints.json"]
        for file_name in required_files:
            file_path = config_path / file_name
            if not file_path.exists():
                print(f"{Colors.RED}❌ Error: Required file '{file_name}' not found in '{config_path}'{Colors.NC}")
                return False

            # Validate JSON
            try:
                with open(file_path, "r") as f:
                    json.load(f)
            except json.JSONDecodeError:
                print(f"{Colors.RED}❌ Error: Invalid JSON in '{file_path}'{Colors.NC}")
                return False

        return True

    def interactive_config_selection(self) -> str:
        """Interactive configuration selection"""
        configs = self.list_available_configs()

        if not configs:
            print(f"{Colors.RED}❌ No configurations found in '{self.configs_dir}'{Colors.NC}")
            sys.exit(1)

        print(f"{Colors.CYAN}🔧 Interactive Configuration Selection{Colors.NC}")
        print()
        print(f"{Colors.BLUE}Available configurations:{Colors.NC}")

        for i, config_name in enumerate(configs, 1):
            config_path = self.configs_dir / config_name
            description = self.get_config_description(config_path)
            print(f"{Colors.YELLOW}{i:2d}){Colors.NC} {config_name:15s} {description}")

        print()
        try:
            choice = input(f"{Colors.CYAN}Select configuration (1-{len(configs)}): {Colors.NC}")
            choice_num = int(choice)
            if 1 <= choice_num <= len(configs):
                selected = configs[choice_num - 1]
                print(f"{Colors.GREEN}✅ Selected: {selected}{Colors.NC}")
                return selected
            else:
                print(f"{Colors.RED}❌ Invalid selection{Colors.NC}")
                sys.exit(1)
        except (ValueError, KeyboardInterrupt):
            print(f"{Colors.RED}❌ Invalid selection{Colors.NC}")
            sys.exit(1)

    def get_config_description(self, config_path: Path) -> str:
        """Get description for a configuration"""
        readme_path = config_path / "README.md"
        if readme_path.exists():
            try:
                with open(readme_path, "r") as f:
                    lines = f.readlines()
                    for line in lines[:5]:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            return line.lstrip("*- ")
            except:
                pass

        # Fallback: count endpoints
        endpoints_path = config_path / "endpoints.json"
        if endpoints_path.exists():
            try:
                with open(endpoints_path, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        count = len(data)
                    else:
                        count = len([k for k in data.keys() if "path" in str(data[k])])
                    return f"Mock API with {count} endpoints"
            except:
                pass

        return "Mock API configuration"

    def find_process_by_port(self, port: int) -> Optional[int]:
        """Find process ID using a specific port"""
        return ProcessUtils.find_process_by_port(port)

    def is_mock_server_process(self, pid: int) -> bool:
        """Check if process is our mock server"""
        return ProcessUtils.is_mock_server_process(pid)

    def stop_process_gracefully(self, pid: int, config_name: str = "unknown") -> bool:
        """Stop process gracefully with fallback to force kill"""
        print(f"{Colors.BLUE}🛑 Stopping server (PID: {pid}, Config: {config_name})...{Colors.NC}")

        if ProcessUtils.terminate_process(pid):
            print(f"{Colors.GREEN}✅ Server stopped successfully{Colors.NC}")
            return True
        else:
            print(f"{Colors.RED}❌ Failed to stop server{Colors.NC}")
            return False

    def get_system_api_key(self, config_path: str) -> Optional[str]:
        """Extract system API key from auth.json"""
        auth_file = Path(config_path) / "auth.json"
        try:
            with open(auth_file, "r") as f:
                auth_config = json.load(f)

            system_auth = auth_config.get("authentication_methods", {}).get("system_api_key", {})
            valid_keys = system_auth.get("valid_keys", [])

            if valid_keys:
                return valid_keys[0]
            return None
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return None

    def get_next_available_port(self, start_port: int = 8000) -> int:
        """
        Get the next available port starting from start_port.
        Considers both tracked servers and running processes.

        Args:
            start_port: Port to start searching from (default: 8000)

        Returns:
            Next available port number
        """
        # Get ports used by tracked servers
        used_ports = set()
        tracked_servers = self.state.get_all_servers()
        for server in tracked_servers:
            used_ports.add(server.get("port"))

        # Find next available port considering both tracked servers and running processes
        for port in range(start_port, start_port + 100):  # Check up to 100 ports
            if port not in used_ports and ProcessUtils.find_process_by_port(port) is None:
                return port

        raise RuntimeError(f"No available port found in range {start_port}-{start_port + 99}")

    def cmd_start(self, args):
        """Start server command"""
        # Get configuration
        if args.config:
            config_name = args.config
        else:
            config_name = self.interactive_config_selection()

        # Validate configuration
        if not self.validate_config(config_name):
            sys.exit(1)

        # Check for existing server
        existing_server = self.state.get_server_by_config(config_name)
        if existing_server:
            port = existing_server["port"]
            print(f"{Colors.BLUE}📁 Found existing server for {config_name} on port: {port}{Colors.NC}")
            print(f"{Colors.YELLOW}⚠️  A server with this configuration is already tracked. Use 'stop' first or specify a different port.{Colors.NC}")
            sys.exit(1)

        # Determine port
        if args.port:
            # User specified a port, validate it's available
            port = args.port

            # Validate port range
            if not (1 <= port <= 65535):
                print(f"{Colors.RED}❌ Invalid port number '{port}'. Must be between 1-65535{Colors.NC}")
                sys.exit(1)

            # Check if port is available
            existing_process = self.find_process_by_port(port)
            if existing_process:
                print(f"{Colors.RED}❌ Port {port} is already in use by process {existing_process}{Colors.NC}")
                sys.exit(1)
        else:
            # Auto-select next available port starting from 8000
            try:
                port = self.get_next_available_port(start_port=8000)
                print(f"{Colors.GREEN}🔍 Auto-selected available port: {port}{Colors.NC}")
            except RuntimeError as e:
                print(f"{Colors.RED}❌ {e}{Colors.NC}")
                sys.exit(1)

        config_path = self.configs_dir / config_name

        print()
        print(f"{Colors.GREEN}🚀 Starting Mock Server with '{config_name}' configuration...{Colors.NC}")
        print(f"{Colors.BLUE}📂 Config folder: {config_path}{Colors.NC}")
        print(f"{Colors.BLUE}🌐 Host: {args.host}{Colors.NC}")
        print(f"{Colors.BLUE}🔌 Port: {port}{Colors.NC}")
        print()

        # Start server
        os.chdir(self.project_root)

        # Generate unique log file path with random prefix
        random_prefix = secrets.token_hex(4)  # 8 character hex string
        log_file = f"logs/{random_prefix}_{config_name}_{port}.logs"

        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

        env = os.environ.copy()
        env["CONFIG_FOLDER"] = str(config_path)
        env["LOG_FILE"] = log_file

        cmd = [sys.executable, "-m", "uvicorn", "src.main:app", "--host", args.host, "--port", str(port)]

        if args.reload:
            cmd.append("--reload")

        # Try different approaches to run the server
        poetry_available = False
        venv_available = False

        try:
            # Check if Poetry is available
            result = subprocess.run(["poetry", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                poetry_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Check if there's a local .venv directory (Poetry in-project virtual environment)
        venv_path = self.project_root / ".venv"
        if venv_path.exists():
            venv_available = True

        if poetry_available:
            print(f"{Colors.BLUE}🔧 Using Poetry environment...{Colors.NC}")
            try:
                # Configure Poetry for local virtual environment
                subprocess.run(["poetry", "config", "virtualenvs.in-project", "true"], check=True)
                # Install dependencies
                result = subprocess.run(["poetry", "install", "--only=main"], check=True)
                # Run with Poetry
                cmd = ["poetry", "run"] + cmd
            except subprocess.CalledProcessError as e:
                print(f"{Colors.YELLOW}⚠️  Poetry install failed: {e}{Colors.NC}")
                if venv_available:
                    print(f"{Colors.BLUE}🔧 Falling back to direct virtual environment...{Colors.NC}")
                    # Use the .venv directly
                    venv_python = venv_path / "bin" / "python"
                    if venv_python.exists():
                        cmd = [str(venv_python), "-m", "uvicorn", "src.main:app", "--host", args.host, "--port", str(port)]
                        if args.reload:
                            cmd.append("--reload")
                    else:
                        print(f"{Colors.YELLOW}⚠️  Virtual environment Python not found, using system Python{Colors.NC}")
                else:
                    print(f"{Colors.BLUE}🔧 Using system Python...{Colors.NC}")
        elif venv_available:
            print(f"{Colors.BLUE}🔧 Using local virtual environment...{Colors.NC}")
            # Use the .venv directly
            venv_python = venv_path / "bin" / "python"
            if venv_python.exists():
                cmd = [str(venv_python), "-m", "uvicorn", "src.main:app", "--host", args.host, "--port", str(port)]
                if args.reload:
                    cmd.append("--reload")
            else:
                print(f"{Colors.YELLOW}⚠️  Virtual environment Python not found, using system Python{Colors.NC}")
        else:
            print(f"{Colors.BLUE}🔧 Using system Python...{Colors.NC}")
            # Try to install dependencies if we have pip
            try:
                print(f"{Colors.BLUE}📦 Attempting to install dependencies...{Colors.NC}")
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            except subprocess.CalledProcessError:
                print(f"{Colors.YELLOW}⚠️  Could not install dependencies. Server may fail to start.{Colors.NC}")

        print(f"{Colors.BLUE}🔄 Starting server...{Colors.NC}")

        # Start the server process
        process = subprocess.Popen(cmd, env=env)

        # Give server time to start
        time.sleep(3)

        # Check if process is still running
        if process.poll() is None:
            # Add to state tracking
            self.state.add_server(config_name, port, process.pid, args.host)

            print(f"{Colors.GREEN}✅ Server started successfully!{Colors.NC}")
            print()
            print(f"{Colors.GREEN}📊 Server Information:{Colors.NC}")
            print(f"{Colors.BLUE}   Configuration: {config_name}{Colors.NC}")
            print(f"{Colors.BLUE}   Process ID: {process.pid}{Colors.NC}")
            print(f"{Colors.BLUE}   Access the API at: http://{args.host}:{port}{Colors.NC}")
            print(f"{Colors.BLUE}   Interactive docs: http://{args.host}:{port}/docs{Colors.NC}")
            print(f"{Colors.BLUE}   OpenAPI schema: http://{args.host}:{port}/openapi.json{Colors.NC}")
            print()
            print(f"{Colors.YELLOW}🛑 To stop the server:{Colors.NC}")
            print(f"{Colors.CYAN}   mockctl stop{Colors.NC}")
            print(f"{Colors.CYAN}   mockctl stop --pid {process.pid}{Colors.NC}")

            # Test server response
            print(f"{Colors.BLUE}🔍 Testing server response...{Colors.NC}")
            if HAS_REQUESTS:
                try:
                    response = requests.get(f"http://{args.host}:{port}/", timeout=3)
                    print(f"{Colors.GREEN}✅ Server is responding to HTTP requests{Colors.NC}")
                except:
                    print(f"{Colors.YELLOW}⚠️  Server may still be starting up...{Colors.NC}")
            else:
                print(f"{Colors.YELLOW}⚠️  Requests library not available, skipping HTTP test{Colors.NC}")

        else:
            print(f"{Colors.RED}❌ Failed to start server{Colors.NC}")
            sys.exit(1)

    def cmd_stop(self, args):
        """Stop server command"""
        self.state.cleanup_dead_processes()

        if args.all:
            # Stop all tracked servers
            servers = self.state.get_all_servers()
            if not servers:
                print(f"{Colors.YELLOW}⚠️  No tracked servers found{Colors.NC}")
                return

            for server in servers:
                pid = server["pid"]
                config = server["config"]
                if self.stop_process_gracefully(pid, config):
                    self.state.remove_server_by_pid(pid)
            return

        if args.pid:
            # Stop specific PID
            if self.stop_process_gracefully(args.pid):
                self.state.remove_server_by_pid(args.pid)
            return

        if args.port:
            # Stop by port
            server = self.state.get_server_by_port(args.port)
            if server:
                pid = server["pid"]
                config = server["config"]
                if self.stop_process_gracefully(pid, config):
                    self.state.remove_server_by_pid(pid)
            else:
                # Try to find process by port
                pid = self.find_process_by_port(args.port)
                if pid and self.is_mock_server_process(pid):
                    if self.stop_process_gracefully(pid):
                        self.state.remove_server_by_pid(pid)
                else:
                    print(f"{Colors.YELLOW}⚠️  No mock server found on port {args.port}{Colors.NC}")
            return

        if args.config:
            # Stop by config name
            server = self.state.get_server_by_config(args.config)
            if server:
                pid = server["pid"]
                if self.stop_process_gracefully(pid, args.config):
                    self.state.remove_server_by_pid(pid)
            else:
                print(f"{Colors.YELLOW}⚠️  No server found for configuration '{args.config}'{Colors.NC}")
            return

        # Auto-detect server to stop
        servers = self.state.get_all_servers()
        if not servers:
            print(f"{Colors.YELLOW}⚠️  No tracked servers found{Colors.NC}")
            return

        if len(servers) == 1:
            server = servers[0]
            pid = server["pid"]
            config = server["config"]
            if self.stop_process_gracefully(pid, config):
                self.state.remove_server_by_pid(pid)
        else:
            print(f"{Colors.CYAN}Multiple servers found. Choose one to stop:{Colors.NC}")
            for i, server in enumerate(servers, 1):
                print(f"{Colors.YELLOW}{i}){Colors.NC} {server['config']} (PID: {server['pid']}, Port: {server['port']})")

            try:
                choice = int(input(f"{Colors.CYAN}Select server to stop (1-{len(servers)}): {Colors.NC}"))
                if 1 <= choice <= len(servers):
                    server = servers[choice - 1]
                    pid = server["pid"]
                    config = server["config"]
                    if self.stop_process_gracefully(pid, config):
                        self.state.remove_server_by_pid(pid)
                else:
                    print(f"{Colors.RED}❌ Invalid selection{Colors.NC}")
            except (ValueError, KeyboardInterrupt):
                print(f"{Colors.RED}❌ Invalid selection{Colors.NC}")

    def cmd_list(self, args):
        """List servers command"""
        print(f"{Colors.BLUE}🔍 Scanning for running Mock API Servers...{Colors.NC}")
        print()

        self.state.cleanup_dead_processes()
        servers = self.state.get_all_servers()

        if not servers:
            print(f"{Colors.YELLOW}📭 No tracked servers found{Colors.NC}")
            print()
            print(f"{Colors.BLUE}💡 Looking for untracked mock servers...{Colors.NC}")

            # Look for untracked processes
            found_untracked = False
            untracked_processes = ProcessUtils.list_mock_server_processes()

            for proc_info in untracked_processes:
                found_untracked = True
                print(f"{Colors.YELLOW}   Untracked: PID {proc_info['pid']} - {proc_info['cmdline']}{Colors.NC}")

            if not found_untracked:
                print(f"{Colors.YELLOW}   No untracked mock servers found{Colors.NC}")
            return

        print(f"{Colors.GREEN}📊 Found {len(servers)} tracked server(s):{Colors.NC}")
        print()

        for server in servers:
            config = server["config"]
            port = server["port"]
            pid = server["pid"]
            host = server.get("host", "unknown")
            started_at = server.get("started_at", "unknown")

            # Check if process is still alive
            if ProcessUtils.pid_exists(pid):
                status = f"{Colors.GREEN}🟢 Running{Colors.NC}"
            else:
                status = f"{Colors.RED}🔴 Dead{Colors.NC}"

            print(f"{Colors.CYAN}Config:{Colors.NC} {config}")
            print(f"{Colors.CYAN}Status:{Colors.NC} {status}")
            print(f"{Colors.CYAN}PID:{Colors.NC} {pid}")
            print(f"{Colors.CYAN}Address:{Colors.NC} http://{host}:{port}")
            print(f"{Colors.CYAN}Started:{Colors.NC} {started_at}")
            print(f"{Colors.CYAN}API Docs:{Colors.NC} http://{host}:{port}/docs")
            print()

    def cmd_logs(self, args):
        """View logs command"""
        self.state.cleanup_dead_processes()
        servers = self.state.get_all_servers()

        # If a specific port is provided, get logs from that server
        if args.port:
            target_server = self.state.get_server_by_port(args.port)
            if not target_server:
                print(f"{Colors.RED}❌ No server found running on port {args.port}{Colors.NC}")
                return
            servers_to_check = [target_server]
        else:
            # If no port specified, show logs from all running servers
            if not servers:
                print(f"{Colors.RED}❌ No servers are currently running{Colors.NC}")
                print(f"{Colors.YELLOW}💡 Start a server with: ./mockctl start{Colors.NC}")
                return
            servers_to_check = servers

        # Process each server
        for i, server in enumerate(servers_to_check):
            config = server["config"]
            port = server["port"]
            host = server.get("host", "localhost")

            if len(servers_to_check) > 1:
                print(f"\n{Colors.MAGENTA}{'='*60}{Colors.NC}")
                print(f"{Colors.MAGENTA}📋 Logs for {config} server (port {port}){Colors.NC}")
                print(f"{Colors.MAGENTA}{'='*60}{Colors.NC}")

            self._fetch_logs_from_server(host, port, args)

    def _fetch_logs_from_server(self, host: str, port: int, args):
        """Fetch logs from a specific server"""
        base_url = f"http://{host}:{port}"
        endpoint = "/system/logging/logs"
        url = f"{base_url}{endpoint}"

        # Try to get API key
        api_key = "system-admin-key-123"  # Default

        headers = {"X-API-Key": api_key}
        params = {"lines": args.lines}

        print(f"{Colors.BLUE}📋 Fetching logs from {url}...{Colors.NC}")

        if not HAS_REQUESTS:
            print(f"{Colors.RED}❌ Requests library not available. Cannot fetch logs via HTTP.{Colors.NC}")
            print(f"{Colors.YELLOW}💡 Install requests: pip install requests{Colors.NC}")
            return

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Check if response has the expected structure
                if "data" in data and "logs" in data["data"]:
                    logs = data["data"]["logs"]
                    total_lines = data["data"].get("total_lines", 0)
                    returned_lines = data["data"].get("returned_lines", len(logs))
                else:
                    # Fallback for direct logs array
                    logs = data.get("logs", [])
                    total_lines = len(logs)
                    returned_lines = len(logs)

                if args.filter:
                    # Filter logs by endpoint
                    filtered_logs = []
                    for log_entry in logs:
                        if args.filter in log_entry:
                            filtered_logs.append(log_entry)
                    logs = filtered_logs
                    print(f"{Colors.BLUE}📊 Showing {len(logs)} filtered log entries for '{args.filter}' (from {returned_lines} total){Colors.NC}")
                else:
                    print(f"{Colors.BLUE}📊 Showing {len(logs)} log entries (from {total_lines} total lines){Colors.NC}")

                print()
                for log_entry in logs:
                    print(log_entry)

            else:
                print(f"{Colors.RED}❌ Failed to fetch logs: HTTP {response.status_code}{Colors.NC}")
                if response.status_code == 401:
                    print(f"{Colors.YELLOW}💡 Authentication failed. Check API key.{Colors.NC}")
                elif response.status_code == 404:
                    print(f"{Colors.YELLOW}💡 Logs endpoint not found. Server may not support system logging.{Colors.NC}")
                else:
                    print(f"Response: {response.text}")

        except Exception as e:
            if "ConnectionError" in str(type(e)):
                print(f"{Colors.RED}❌ Could not connect to server at {base_url}{Colors.NC}")
                print(f"{Colors.YELLOW}💡 Make sure a server is running on port {port}{Colors.NC}")
            else:
                print(f"{Colors.RED}❌ Error fetching logs: {e}{Colors.NC}")

    def cmd_search(self, args):
        """Search logs for requests to specific paths"""
        # Import required modules for date parsing
        import re
        from collections import defaultdict
        from datetime import datetime

        # Auto-detect port if not provided
        port = args.port
        if not port:
            self.state.cleanup_dead_processes()
            servers = self.state.get_all_servers()
            if servers:
                port = servers[0]["port"]
                print(f"{Colors.BLUE}📍 Auto-detected server on port {port}{Colors.NC}")
            else:
                print(f"{Colors.RED}❌ No servers are currently running{Colors.NC}")
                print(f"{Colors.YELLOW}💡 Start a server with: ./mockctl start{Colors.NC}")
                return

        # Get server info
        server = self.state.get_server_by_port(port)
        if not server:
            print(f"{Colors.RED}❌ No server found running on port {port}{Colors.NC}")
            return

        # Get log file path
        log_file_path = self.project_root / server.get("log_file", f"logs/server_{port}.logs")

        if not log_file_path.exists():
            # Fallback: try to find the correct log file by searching the logs directory
            logs_dir = self.project_root / "logs"
            if logs_dir.exists():
                config_name = server.get("config", "unknown")
                # Look for log files matching the pattern: *_{config_name}_{port}.logs
                pattern = f"*_{config_name}_{port}.logs"
                matching_files = list(logs_dir.glob(pattern))

                print(f"{Colors.BLUE}🔍 Expected log file: {log_file_path}{Colors.NC}")
                print(f"{Colors.BLUE}🔍 Searching pattern: {pattern} in {logs_dir}{Colors.NC}")
                print(f"{Colors.BLUE}🔍 Found {len(matching_files)} matching files{Colors.NC}")

                if matching_files:
                    # Use the most recently modified log file
                    log_file_path = max(matching_files, key=lambda f: f.stat().st_mtime)
                    print(f"{Colors.YELLOW}⚠️  State log file not found, using: {log_file_path.name}{Colors.NC}")

                    # Update the server state with the correct log file path
                    try:
                        servers = self.state.get_all_servers()
                        for i, srv in enumerate(servers):
                            if srv.get("port") == port:
                                servers[i]["log_file"] = str(log_file_path.relative_to(self.project_root))
                                self.state._save_servers(servers)
                                print(f"{Colors.BLUE}💡 Updated server state with correct log file path{Colors.NC}")
                                break
                    except Exception as e:
                        print(f"{Colors.YELLOW}⚠️  Could not update server state: {e}{Colors.NC}")
                else:
                    print(f"{Colors.RED}❌ No log files found matching pattern: {pattern}{Colors.NC}")
                    print(f"{Colors.BLUE}💡 Available log files in logs/:{Colors.NC}")
                    for log_file in logs_dir.glob("*.logs"):
                        print(f"   {log_file.name}")
                    return
            else:
                print(f"{Colors.RED}❌ Log file not found: {log_file_path}{Colors.NC}")
                print(f"{Colors.RED}❌ Logs directory not found: {logs_dir}{Colors.NC}")
                return

        print(f"{Colors.BLUE}🔍 Searching logs for requests to path: {args.path}{Colors.NC}")
        print(f"{Colors.BLUE}📂 Log file: {log_file_path}{Colors.NC}")

        # Parse time filter if provided
        since_datetime = None
        if args.since:
            since_datetime = self._parse_since_time(args.since)
            if since_datetime:
                print(f"{Colors.BLUE}⏰ Searching since: {since_datetime.strftime('%Y-%m-%d %H:%M:%S')}{Colors.NC}")

        print()

        # Parse log file and search for requests
        request_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*?\[([a-f0-9]+)\] REQUEST: (\w+) http://[^/]+(/[^\s]*)")
        response_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*?\[([a-f0-9]+)\] RESPONSE: (\d+) for (\w+) http://[^/]+(/[^\s]*)")

        requests_found = {}
        responses_found = defaultdict(list)

        try:
            with open(log_file_path, "r") as f:
                lines = f.readlines()
                # Process last N lines if specified
                if args.lines and len(lines) > args.lines:
                    lines = lines[-args.lines :]

                for line in lines:
                    # Check if this line is within our time filter
                    if since_datetime:
                        try:
                            log_time_str = line.split(" - ")[0].strip()
                            log_time = datetime.strptime(log_time_str, "%Y-%m-%d %H:%M:%S,%f")
                            if log_time < since_datetime:
                                continue
                        except (ValueError, IndexError):
                            continue

                    # Search for REQUEST entries
                    request_match = request_pattern.search(line)
                    if request_match:
                        timestamp, correlation_id, method, path = request_match.groups()
                        # Check if this path matches what we're searching for
                        if args.path in path:
                            requests_found[correlation_id] = {"timestamp": timestamp, "method": method, "path": path, "line": line.strip()}

                    # Search for RESPONSE entries
                    response_match = response_pattern.search(line)
                    if response_match:
                        timestamp, correlation_id, status_code, method, path = response_match.groups()
                        # Check if this path matches what we're searching for
                        if args.path in path and correlation_id in requests_found:
                            responses_found[status_code].append({"timestamp": timestamp, "correlation_id": correlation_id, "method": method, "path": path, "status_code": status_code, "request_time": requests_found[correlation_id]["timestamp"]})

        except IOError as e:
            print(f"{Colors.RED}❌ Error reading log file: {e}{Colors.NC}")
            return

        # Display results
        if not requests_found:
            print(f"{Colors.YELLOW}🔍 No requests found for path '{args.path}'{Colors.NC}")
            print(f"{Colors.BLUE}💡 Try a partial path match (e.g., '/api' instead of '/api/users/123'){Colors.NC}")
            return

        print(f"{Colors.GREEN}✅ Found {len(requests_found)} request(s) to paths containing '{args.path}'{Colors.NC}")

        if responses_found:
            print(f"{Colors.GREEN}📊 Response Summary by Status Code:{Colors.NC}")
            print()

            # Group by status code and display
            total_responses = sum(len(responses) for responses in responses_found.values())

            for status_code in sorted(responses_found.keys()):
                responses = responses_found[status_code]
                count = len(responses)
                percentage = (count / total_responses) * 100

                # Color code status codes
                if status_code.startswith("2"):
                    status_color = Colors.GREEN
                elif status_code.startswith("4"):
                    status_color = Colors.YELLOW
                elif status_code.startswith("5"):
                    status_color = Colors.RED
                else:
                    status_color = Colors.BLUE

                print(f"{status_color}📈 Status {status_code}:{Colors.NC} {count} responses ({percentage:.1f}%)")

                # Show first few timestamps for each status code
                for i, response in enumerate(responses[:3]):  # Show up to 3 examples
                    print(f"   {Colors.CYAN}└─ {response['timestamp']} - {response['method']} {response['path']}{Colors.NC}")

                if len(responses) > 3:
                    print(f"   {Colors.BLUE}└─ ... and {len(responses) - 3} more{Colors.NC}")
                print()
        else:
            print(f"{Colors.YELLOW}⚠️  Found requests but no corresponding responses{Colors.NC}")
            print(f"{Colors.BLUE}💡 This might indicate incomplete request cycles or connection issues{Colors.NC}")
            print()

            # Show some example requests
            print(f"{Colors.BLUE}📋 Example requests found:{Colors.NC}")
            for i, (corr_id, req) in enumerate(list(requests_found.items())[:5]):
                print(f"   {Colors.CYAN}• {req['timestamp']} - {req['method']} {req['path']}{Colors.NC}")

            if len(requests_found) > 5:
                print(f"   {Colors.BLUE}• ... and {len(requests_found) - 5} more{Colors.NC}")

    def _parse_since_time(self, since_str: str):
        """Parse various time formats for the --since parameter"""
        import re
        from datetime import datetime, timedelta

        now = datetime.now()

        # Handle relative times like "1h ago", "30m ago", "2d ago"
        relative_match = re.match(r"(\d+)([hmsd])\s*ago", since_str.lower())
        if relative_match:
            amount, unit = relative_match.groups()
            amount = int(amount)

            if unit == "m":
                return now - timedelta(minutes=amount)
            elif unit == "h":
                return now - timedelta(hours=amount)
            elif unit == "d":
                return now - timedelta(days=amount)
            elif unit == "s":
                return now - timedelta(seconds=amount)

        # Handle "today"
        if since_str.lower() == "today":
            return now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Handle "yesterday"
        if since_str.lower() == "yesterday":
            yesterday = now - timedelta(days=1)
            return yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

        # Try to parse various datetime formats
        formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%m-%d %H:%M", "%H:%M:%S", "%H:%M"]

        for fmt in formats:
            try:
                parsed_time = datetime.strptime(since_str, fmt)
                # If only time is provided, assume today
                if fmt in ["%H:%M:%S", "%H:%M"]:
                    parsed_time = parsed_time.replace(year=now.year, month=now.month, day=now.day)
                # If month-day is provided, assume current year
                elif fmt == "%m-%d %H:%M":
                    parsed_time = parsed_time.replace(year=now.year)

                return parsed_time
            except ValueError:
                continue

        print(f"{Colors.YELLOW}⚠️  Could not parse time format: {since_str}{Colors.NC}")
        print(f"{Colors.BLUE}💡 Supported formats: 'today', '1h ago', '30m ago', '2025-08-22 10:00', etc.{Colors.NC}")
        return None

    def cmd_test(self, args):
        """Test server command"""
        # Get API key
        api_key = args.api_key
        if not api_key:
            api_key = self.get_system_api_key(args.config)
            if not api_key:
                api_key = "system-admin-key-123"  # Fallback

        base_url = f"http://{args.host}:{args.port}"
        endpoint = "/system/logging/logs"
        url = f"{base_url}{endpoint}"

        headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

        print("🧪 Testing System Logs Endpoint")
        print(f"📍 URL: {url}")
        print(f"🔑 API Key: {api_key[:10]}...{Colors.NC}" if len(api_key) > 10 else f"🔑 API Key: {api_key}")
        print()

        if not HAS_REQUESTS:
            print(f"{Colors.RED}❌ Requests library not available. Cannot test endpoints.{Colors.NC}")
            print(f"{Colors.YELLOW}💡 Install requests: pip install requests{Colors.NC}")
            return

        try:
            print("🚀 Making GET request...")
            if HAS_REQUESTS:
                response = requests.get(url, headers=headers, timeout=10)

                print(f"📈 Response Status: {response.status_code}")

                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"{Colors.GREEN}✅ Success! Response received{Colors.NC}")
                        logs_count = len(data.get("logs", []))
                        print(f"📊 Log entries returned: {logs_count}")
                    except json.JSONDecodeError:
                        print(f"{Colors.GREEN}✅ Success! Response received (text){Colors.NC}")
                        print(f"Response: {response.text}")
                else:
                    print(f"{Colors.RED}❌ Failed with status {response.status_code}{Colors.NC}")
                    print(f"Response: {response.text}")
            else:
                print(f"{Colors.RED}❌ Requests library not available{Colors.NC}")

        except Exception as e:
            if "ConnectionError" in str(type(e)):
                print(f"{Colors.RED}❌ Connection failed: Could not connect to {base_url}{Colors.NC}")
                print("💡 Make sure the server is running on the specified host and port")
            elif "Timeout" in str(type(e)):
                print(f"{Colors.RED}❌ Request timed out{Colors.NC}")
            else:
                print(f"{Colors.RED}❌ Unexpected error: {e}{Colors.NC}")

    def cmd_success(self, args):
        """Success report command"""
        # Auto-detect port if not provided
        port = args.port
        if not port:
            self.state.cleanup_dead_processes()
            servers = self.state.get_all_servers()
            if servers:
                port = servers[0]["port"]
            else:
                port = self.default_port

        print(f"{Colors.BLUE}📊 Generating success report for port {port}...{Colors.NC}")
        print(f"{Colors.YELLOW}⚠️  Success reporting functionality would need to be implemented{Colors.NC}")
        print(f"{Colors.BLUE}This would analyze the last {args.lines} log entries for HTTP status codes{Colors.NC}")
        print(f"{Colors.BLUE}Format: {args.format}{Colors.NC}")

    def cmd_config_help(self, args):
        """Configuration help command"""
        print(f"{Colors.CYAN}🔧 Mock Server Configuration Management{Colors.NC}")
        print(f"{Colors.BLUE}{'=' * 38}{Colors.NC}")
        print()
        print(f"{Colors.GREEN}📁 Configuration Structure:{Colors.NC}")
        print("   configs/")
        print("   ├── basic/          # Basic mock server setup")
        print("   ├── persistence/    # Redis-enabled configuration")
        print("   └── vmanage/        # vManage SD-WAN API mock")
        print()
        print("   Each config directory contains:")
        print("   ├── api.json        # API metadata and settings")
        print("   ├── auth.json       # Authentication configuration")
        print("   └── endpoints.json  # Route definitions")
        print()
        print(f"{Colors.GREEN}🚀 Starting Servers:{Colors.NC}")
        print()
        print(f"{Colors.YELLOW}Using the Python CLI (Recommended):{Colors.NC}")
        print("   mockctl start                    # Interactive selection")
        print("   mockctl start vmanage            # Start vmanage config")
        print("   mockctl start basic              # Start basic config")
        print("   mockctl start persistence        # Start persistence config")
        print("   mockctl start --port 8002        # Custom port")
        print("   mockctl start vmanage --host 127.0.0.1")
        print()
        print(f"{Colors.GREEN}🛑 Stopping Servers:{Colors.NC}")
        print()
        print("   mockctl stop                     # Auto-detect or interactive")
        print("   mockctl stop vmanage             # Stop vmanage config")
        print("   mockctl stop --port 8001         # Stop by port")
        print("   mockctl stop --pid 12345         # Stop by process ID")
        print("   mockctl stop --all               # Stop all mock servers")
        print()
        print(f"{Colors.GREEN}📊 Server Management:{Colors.NC}")
        print()
        print("   mockctl list                     # List running servers")
        print("   mockctl logs                     # Get recent logs")
        print("   mockctl logs --lines 100         # Get last 100 lines")
        print("   mockctl logs --filter /login     # Filter by endpoint")
        print("   mockctl search /api/users        # Search for endpoint requests")
        print("   mockctl search /items --since 1h # Search recent requests")
        print("   mockctl test --port 8000         # Test API endpoints")
        print("   mockctl success detailed         # Success analysis")
        print()

    def cmd_help(self, args):
        """Detailed help command"""
        print(f"{Colors.CYAN}🚀 Mock Server Control CLI{Colors.NC}")
        print(f"{Colors.BLUE}{'=' * 28}{Colors.NC}")
        print()
        print("This unified CLI tool replaces all the bash scripts for managing mock servers.")
        print()
        print(f"{Colors.GREEN}Main Commands:{Colors.NC}")
        print(f"  {Colors.YELLOW}start{Colors.NC}      - Start a mock server with specified configuration")
        print(f"  {Colors.YELLOW}stop{Colors.NC}       - Stop running mock servers")
        print(f"  {Colors.YELLOW}list{Colors.NC}       - List all running servers")
        print(f"  {Colors.YELLOW}logs{Colors.NC}       - View server logs")
        print(f"  {Colors.YELLOW}search{Colors.NC}     - Search logs for requests to specific paths")
        print(f"  {Colors.YELLOW}test{Colors.NC}       - Test server endpoints")
        print(f"  {Colors.YELLOW}success{Colors.NC}    - Generate success reports")
        print()
        print(f"{Colors.GREEN}Configuration:{Colors.NC}")
        print(f"  Available configs: {', '.join(self.list_available_configs())}")
        print()
        print(f"{Colors.GREEN}Examples:{Colors.NC}")
        print("  mockctl start                     # Interactive config selection")
        print("  mockctl start basic --port 8080   # Start basic config on port 8080")
        print("  mockctl stop --all                # Stop all servers")
        print("  mockctl logs --filter /api/users  # Filter logs by endpoint")
        print("  mockctl search /api/users         # Search for endpoint requests")
        print("  mockctl search /items --since 1h  # Search recent requests")
        print()
        print("For detailed configuration help, use: mockctl config-help")


if __name__ == "__main__":
    cli = MockServerCLI()
    cli.main()
