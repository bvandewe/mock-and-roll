"""Pytest configuration and shared fixtures.

Provides a shared LOG_FILE fixture so tests that import application code relying
on LOG_FILE environment variable do not need to set it individually.
"""

from __future__ import annotations

import os
import pathlib
import tempfile

import pytest


@pytest.fixture(scope="session", autouse=True)
def log_file_env() -> str:
    """Ensure LOG_FILE environment variable is set for the test session.

    Creates a temporary file in a dedicated temp directory. If LOG_FILE is
    already defined (e.g., a specific test wants a custom path) it is preserved.

    Yields:
        The path to the log file used for tests.
    """
    if os.environ.get("LOG_FILE"):
        return os.environ["LOG_FILE"]

    temp_dir = tempfile.mkdtemp(prefix="mock_and_roll_logs_")
    log_path = pathlib.Path(temp_dir) / "test-session.log"
    # Touch the file so existence checks pass early.
    log_path.touch()
    os.environ["LOG_FILE"] = str(log_path)
    return str(log_path)
