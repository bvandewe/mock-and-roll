"""
Main entry point for the Mock API Server.

This server dynamically creates endpoints based on configuration files and provides
authentication, request/response templating, and optional Redis persistence.
"""

import logging

from app.factory import create_app
from config.loader import load_api_config, load_auth_config, load_endpoints_config
from config.logging_config import setup_logging
from routes.cache_management import add_cache_management_endpoints
from routes.logging_management import add_logging_management_endpoints
from routes.setup import setup_routes

# --- Configuration Loading ---
# Load configurations first
config_data = load_endpoints_config()
auth_data = load_auth_config()
api_config = load_api_config()

# --- Logging Setup ---
# Set up logging based on configuration
setup_logging(api_config)

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


@app.get("/", include_in_schema=False)
async def root():
    """A simple root endpoint to confirm the server is running."""
    return {"message": "Mock server is running. Check /docs for available endpoints."}


# For backward compatibility, expose the app instance
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
