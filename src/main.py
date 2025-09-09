"""
Main entry point for the Mock API Server.

This server dynamically creates endpoints based on configuration files and provides
authentication, request/response templating, and optional Redis persistence.
"""

import argparse
import logging
import os
import sys

# Add the src directory to the Python path to enable absolute imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from config.loader import (
    load_api_config,
    load_auth_config,
    load_endpoints_config,
    set_config_folder,
)
from config.logging_config import setup_logging
from routes.cache_management import add_cache_management_endpoints
from routes.logging_management import add_logging_management_endpoints
from routes.setup import setup_routes


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Mock API Server")
    parser.add_argument("--config-folder", type=str, help="Path to the configuration folder containing api.json, auth.json, and endpoints.json files")
    parser.add_argument("--log-file", type=str, help="Path to the log file")
    return parser.parse_known_args()


def create_application():
    """Create and configure the FastAPI application."""
    # Parse command line arguments
    args, unknown = parse_arguments()

    # Set custom config folder if provided via command line argument
    if args.config_folder:
        if not os.path.exists(args.config_folder):
            print(f"Error: Config folder '{args.config_folder}' does not exist")
            sys.exit(1)
        set_config_folder(args.config_folder)
    # Or if provided via environment variable
    elif os.getenv("CONFIG_FOLDER"):
        config_folder = os.getenv("CONFIG_FOLDER")
        if config_folder and not os.path.exists(config_folder):
            print(f"Error: Config folder '{config_folder}' (from CONFIG_FOLDER env var) does not exist")
            sys.exit(1)
        if config_folder:
            set_config_folder(config_folder)

    # --- Configuration Loading ---
    # Load configurations first
    config_data = load_endpoints_config()
    auth_data = load_auth_config()
    api_config = load_api_config()

    # --- Logging Setup ---
    # Set up logging based on configuration, with optional log file override
    log_file_override = args.log_file or os.getenv("LOG_FILE")
    setup_logging(api_config, log_file_override)

    # Create the FastAPI application
    app = create_app()

    # Set up dynamic routes
    setup_routes(app, config_data, auth_data)

    # Add cache management endpoints if Redis persistence is configured
    if api_config.get("persistence") == "redis":
        logging.info("Redis persistence configured - adding cache management endpoints")
        add_cache_management_endpoints(app, api_config, auth_data)
    else:
        logging.info("Redis persistence not configured - cache management endpoints not added")

    # Add logging management endpoints
    logging.info("Adding logging management endpoints")
    add_logging_management_endpoints(app, api_config, auth_data)

    return app


# Create the application instance
app = create_application()


@app.get("/", include_in_schema=False)
async def root():
    """A simple root endpoint to confirm the server is running."""
    return {"message": "Mock server is running."}


# For backward compatibility, expose the app instance
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
