"""
Logging configuration module for the mock API server.

This module sets up both stdout and file logging based on configuration.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Any, Optional


def setup_logging(api_config: dict[str, Any], log_file_override: Optional[str] = None) -> None:
    """
    Set up logging configuration based on API config.

    Args:
        api_config: The API configuration dictionary containing logging settings
        log_file_override: Optional path to override the log file location
    """
    # Get logging configuration or use defaults
    logging_config = api_config.get("logging", {})

    # Check if logging is enabled
    if not logging_config.get("enabled", True):
        logging.disable(logging.CRITICAL)
        return

    # Get logging parameters
    log_level = getattr(logging, logging_config.get("level", "INFO").upper(), logging.INFO)
    log_format = logging_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Use override if provided, otherwise use config, otherwise default
    if log_file_override:
        log_file_path = log_file_override
    else:
        log_file_path = logging_config.get("file_path", "/app/latest.logs")

    max_file_size = logging_config.get("max_file_size_mb", 10) * 1024 * 1024  # Convert MB to bytes
    backup_count = logging_config.get("backup_count", 5)

    # Control console and file logging separately
    console_enabled = logging_config.get("console_enabled", True)
    file_enabled = logging_config.get("file_enabled", True)

    # Handle Docker vs local development paths
    if log_file_path.startswith("/app/") and not os.path.exists("/app"):
        # Convert Docker path to local development path
        log_file_path = log_file_path.replace("/app/", "logs/")
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

    # Create log directory if it doesn't exist
    log_dir = Path(log_file_path).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Remove any existing handlers to avoid duplicates
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # List to store handlers that will be used
    handlers = []

    # Set up console handler (stdout) if enabled
    if console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)
        root_logger.addHandler(console_handler)

    # Set up file handler with rotation if enabled
    if file_enabled:
        try:
            file_handler = logging.handlers.RotatingFileHandler(log_file_path, maxBytes=max_file_size, backupCount=backup_count, encoding="utf-8")
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
            root_logger.addHandler(file_handler)
        except Exception as e:
            logging.error(f"Failed to set up file logging: {e}")
            # If file logging fails but console is disabled, force enable console
            if not console_enabled:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(log_level)
                console_handler.setFormatter(formatter)
                handlers.append(console_handler)
                root_logger.addHandler(console_handler)
                logging.warning("File logging failed and console was disabled - enabling console logging as fallback")

    # If no handlers were added, add console as fallback
    if not handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)
        root_logger.addHandler(console_handler)
        logging.warning("No logging handlers configured - using console as fallback")

    # Configure uvicorn loggers to use the same handlers
    uvicorn_loggers = ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi", "api.requests"]  # Our custom middleware logger

    for logger_name in uvicorn_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        # Add our handlers
        for handler in handlers:
            logger.addHandler(handler)
        # Prevent propagation to avoid duplicate logs
        logger.propagate = False

    # Disable noisy loggers
    logging.getLogger("multipart.multipart").setLevel(logging.WARNING)

    logging.info(f"Logging configured - Level: {logging_config.get('level', 'INFO')}, Console: {console_enabled}, File: {file_enabled}")
    if file_enabled:
        logging.info(f"Log file: {log_file_path}")


def get_logging_status(api_config: dict[str, Any]) -> dict[str, Any]:
    """
    Get current logging configuration status.

    Args:
        api_config: The API configuration dictionary

    Returns:
        Dictionary containing logging status information
    """
    logging_config = api_config.get("logging", {})

    status = {
        "enabled": logging_config.get("enabled", True),
        "level": logging_config.get("level", "INFO"),
        "console_enabled": logging_config.get("console_enabled", True),
        "file_enabled": logging_config.get("file_enabled", True),
        "file_path": logging_config.get("file_path", "/app/latest.logs"),
        "format": logging_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
        "max_file_size_mb": logging_config.get("max_file_size_mb", 10),
        "backup_count": logging_config.get("backup_count", 5),
        "max_body_log_size": logging_config.get("max_body_log_size", 2048),
        "request_response_logging": logging_config.get("request_response_logging", True),
        "allow_log_deletion": logging_config.get("allow_log_deletion", True),
    }

    # Check if log file exists and get its size
    log_file_path = status["file_path"]
    if os.path.exists(log_file_path):
        file_size = os.path.getsize(log_file_path)
        status["file_exists"] = True
        status["file_size_bytes"] = file_size
        status["file_size_mb"] = round(file_size / (1024 * 1024), 2)
    else:
        status["file_exists"] = False
        status["file_size_bytes"] = 0
        status["file_size_mb"] = 0

    return status


def update_logging_config(api_config: dict[str, Any], new_config: dict[str, Any]) -> dict[str, Any]:
    """
    Update logging configuration and reinitialize logging.

    Args:
        api_config: The current API configuration dictionary
        new_config: New logging configuration parameters

    Returns:
        Updated API configuration
    """
    # Update the logging configuration
    if "logging" not in api_config:
        api_config["logging"] = {}

    api_config["logging"].update(new_config)

    # Reinitialize logging with new configuration
    setup_logging(api_config)

    return api_config
