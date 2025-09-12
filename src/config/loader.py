"""
Configuration loading utilities for the mock API server.
"""

import json
import logging
import os
from typing import Any

# Global variable to store custom config folder path
_config_folder = None


def set_config_folder(config_folder: str) -> None:
    """Set the custom config folder path."""
    global _config_folder
    _config_folder = config_folder
    logging.info(f"Config folder set to: {config_folder}")


def get_config_paths(filename: str) -> list[str]:
    """Get the list of config file paths to try in order of priority."""
    paths = []

    # Check environment variables first (MOCK_CONFIG_FOLDER takes precedence over CONFIG_FOLDER)
    env_config_folder = os.environ.get("MOCK_CONFIG_FOLDER") or os.environ.get("CONFIG_FOLDER")
    if env_config_folder:
        env_path = os.path.join(env_config_folder, filename)
        paths.append(env_path)

    # If custom config folder is set, use it next
    if _config_folder:
        custom_path = os.path.join(_config_folder, filename)
        paths.append(custom_path)

    # Docker environment path
    paths.append(f"/app/config/{filename}")

    # Default relative path
    default_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config", filename)
    paths.append(default_path)

    return paths


def load_api_config() -> dict[str, Any]:
    """Loads the API configuration from api.json in the config directory."""
    config_paths = get_config_paths("api.json")

    for api_path in config_paths:
        try:
            with open(api_path, "r") as f:
                config = json.load(f)
                logging.info(f"Loaded API configuration from '{api_path}'")
                return config
        except FileNotFoundError:
            continue
        except json.JSONDecodeError:
            logging.error(f"Could not decode JSON from '{api_path}'. Using defaults.")
            return {}

    logging.warning("API configuration file not found at any location. Using defaults.")
    return {}


def load_endpoints_config() -> dict[str, Any]:
    """Loads the mock configuration from endpoints.json in the config directory."""
    config_paths = get_config_paths("endpoints.json")

    for config_path in config_paths:
        try:
            with open(config_path, "r") as f:
                logging.info(f"Loaded endpoints configuration from '{config_path}'")
                return json.load(f)
        except FileNotFoundError:
            continue
        except json.JSONDecodeError:
            logging.error(f"Could not decode JSON from '{config_path}'")
            return {"endpoints": []}

    logging.error("Configuration file not found at any location")
    return {"endpoints": []}


def load_auth_config() -> dict[str, Any]:
    """Loads the authentication configuration from auth.json in the config directory."""
    config_paths = get_config_paths("auth.json")

    for auth_path in config_paths:
        try:
            with open(auth_path, "r") as f:
                logging.info(f"Loaded authentication configuration from '{auth_path}'")
                return json.load(f)
        except FileNotFoundError:
            continue
        except json.JSONDecodeError:
            logging.error(f"Could not decode JSON from '{auth_path}'")
            return {"authentication_methods": {}}

    logging.warning("Authentication file not found at any location. Authentication disabled.")
    return {"authentication_methods": {}}
