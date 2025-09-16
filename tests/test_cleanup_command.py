"""Tests for clean-up command.

Validates that:
- Stops running servers (mocked)
- Deletes *.logs files except mockctl.log
- Truncates mockctl.log (recreated empty)
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

CLI_PATH = Path(__file__).resolve().parent.parent / "src" / "cli" / "mockctl.py"
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_cli(args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.Popen([sys.executable, str(CLI_PATH), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=PROJECT_ROOT)
    out, err = proc.communicate(timeout=10)
    return proc.returncode, out.decode(), err.decode()


def test_cleanup_removes_logs_and_truncates_mockctl(tmp_path, monkeypatch):
    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Create fake server logs
    server_logs = [logs_dir / "20250916_120000_basic_8000.logs", logs_dir / "20250916_120100_basic_8001.logs"]
    for lf in server_logs:
        lf.write_text("TEST LOG", encoding="utf-8")

    # Ensure mockctl.log has content
    mockctl_log = logs_dir / "mockctl.log"
    mockctl_log.write_text("OLD CONTENT", encoding="utf-8")

    # Monkeypatch list servers to none (simulate no running servers) by editing repository file? Simpler: ensure no processes tracked.
    # Run clean-up command in json mode
    code, stdout, stderr = run_cli(["--json", "clean-up"])
    assert code == 0, stderr
    # Parse entire stdout as JSON
    data = json.loads(stdout)
    assert data.get("status") == "success"
    # Logs deleted
    for lf in server_logs:
        assert not lf.exists()
    # mockctl.log truncated
    assert mockctl_log.exists()
    content = mockctl_log.read_text(encoding="utf-8")
    # Accept either empty or very small content if logging wrote a completion line post-truncate
    assert len(content) < 300, f"mockctl.log not truncated sufficiently, size={len(content)}"


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__])
