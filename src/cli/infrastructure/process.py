"""Process management repository implementation."""

import os
import socket
import subprocess
import time
from typing import Optional

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from ..domain.repositories import ProcessRepository


class SystemProcessRepository(ProcessRepository):
    """System implementation of process repository."""

    def exists(self, pid: int) -> bool:
        """Check if process exists."""
        if HAS_PSUTIL:
            return psutil.pid_exists(pid)
        else:
            # Fallback using os.kill with signal 0
            try:
                os.kill(pid, 0)
                return True
            except (OSError, ProcessLookupError):
                return False

    def find_by_port(self, port: int) -> Optional[int]:
        """Check if a port is in use using socket binding.

        Uses simple socket binding to test port availability.
        This is cross-platform and doesn't require OS-specific tools.

        Returns:
            1 if port is in use (we can't determine the actual PID reliably
            without OS tools), None if port is available
        """
        try:
            # Try to bind to the port to check if it's available
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
                test_socket.bind(("127.0.0.1", port))
                return None  # Port is available
        except OSError:
            # Port is in use
            return 1

    def is_mock_server(self, pid: int) -> bool:
        """Check if process is a mock server."""
        if HAS_PSUTIL:
            try:
                process = psutil.Process(pid)
                cmdline = " ".join(process.cmdline())
                uvicorn_match = "uvicorn" in cmdline and "src.main:app" in cmdline
                python_match = "python" in cmdline and "main.py" in cmdline
                return uvicorn_match or python_match
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return False
        else:
            # Fallback using ps
            try:
                result = subprocess.run(["ps", "-p", str(pid), "-o", "args="], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    cmdline = result.stdout.strip()
                    uvicorn_match = "uvicorn" in cmdline and "src.main:app" in cmdline
                    python_match = "python" in cmdline and "main.py" in cmdline
                    return uvicorn_match or python_match
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                pass

        return False

    def terminate(self, pid: int, timeout: int = 10) -> bool:
        """Terminate process gracefully."""
        if not self.exists(pid):
            return True

        if HAS_PSUTIL:
            try:
                process = psutil.Process(pid)
                process.terminate()

                # Wait for graceful termination
                try:
                    process.wait(timeout=timeout)
                    return True
                except psutil.TimeoutExpired:
                    # Force kill if graceful termination fails
                    process.kill()
                    try:
                        process.wait(timeout=5)
                        return True
                    except psutil.TimeoutExpired:
                        return False

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return False
        else:
            # Fallback using kill command
            try:
                # Try SIGTERM first
                subprocess.run(["kill", str(pid)], check=True, timeout=5)

                # Wait for process to exit
                for _ in range(timeout):
                    if not self.exists(pid):
                        return True
                    time.sleep(1)

                # Force kill if still running
                subprocess.run(["kill", "-9", str(pid)], check=True, timeout=5)

                # Final check
                time.sleep(1)
                return not self.exists(pid)

            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                return False

    def find_next_available_port(self, start_port: int = 8000) -> int:
        """Find the next available port starting from start_port.

        Uses socket binding to test port availability. This is cross-platform
        and doesn't require OS-specific tools.

        Args:
            start_port: Port to start checking from (default: 8000)

        Returns:
            First available port number

        Raises:
            RuntimeError: If no available port found in reasonable range
        """
        max_attempts = 100  # Check up to 100 ports

        for port in range(start_port, start_port + max_attempts):
            try:
                # Try to bind to the port to check if it's available
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
                    test_socket.bind(("127.0.0.1", port))
                    return port
            except OSError:
                # Port is in use, try the next one
                continue

        # If we get here, no available port was found
        raise RuntimeError(f"No available port found in range {start_port}-{start_port + max_attempts - 1}")

    def list_mock_server_processes(self) -> list[dict]:
        """List all mock server processes."""
        processes = []

        if HAS_PSUTIL:
            for proc in psutil.process_iter(["pid", "cmdline"]):
                try:
                    if proc.info["cmdline"]:
                        cmdline = " ".join(proc.info["cmdline"])
                        if self.is_mock_server(proc.info["pid"]):
                            processes.append({"pid": proc.info["pid"], "cmdline": cmdline})
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        else:
            # Fallback implementation
            try:
                result = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    for line in result.stdout.split("\n"):
                        uvicorn_match = "uvicorn" in line and "src.main:app" in line
                        python_match = "python" in line and "main.py" in line
                        if uvicorn_match or python_match:
                            parts = line.split()
                            if len(parts) > 1:
                                try:
                                    pid = int(parts[1])
                                    processes.append({"pid": pid, "cmdline": " ".join(parts[10:])})
                                except ValueError:
                                    continue
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                pass

        return processes
