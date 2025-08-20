"""
Configuration loading utilities for the mock API server.
"""

import json
import logging
import os
from typing import Any


def load_api_config() -> dict[str, Any]:
    """Loads the API configuration from api.json in the config directory."""
    # First try /app/config (Docker environment), then fall back to relative path
    config_paths = ["/app/config/api.json", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config", "api.json")]

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
    # First try /app/config (Docker environment), then fall back to relative path
    config_paths = ["/app/config/endpoints.json", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config", "endpoints.json")]

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
    # First try /app/config (Docker environment), then fall back to relative path
    config_paths = ["/app/config/auth.json", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config", "auth.json")]

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
