"""
Logging management endpoints for the mock API server.

Provides endpoints to view and configure logging settings at runtime.
"""

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from auth.security import create_system_auth_dependency, system_api_key
from config.logging_config import get_logging_status, update_logging_config


class LoggingConfigUpdate(BaseModel):
    """Model for updating logging configuration."""

    enabled: Optional[bool] = Field(None, description="Enable or disable logging")
    level: Optional[str] = Field(None, description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    file_path: Optional[str] = Field(None, description="Path to log file")
    format: Optional[str] = Field(None, description="Log format string")
    max_file_size_mb: Optional[int] = Field(None, description="Maximum file size in MB before rotation", gt=0)
    backup_count: Optional[int] = Field(None, description="Number of backup files to keep", ge=0)
    allow_log_deletion: Optional[bool] = Field(None, description="Allow or disable log file deletion via API")


def add_logging_management_endpoints(app, api_config: dict[str, Any], auth_data: Optional[dict[str, Any]] = None):
    """
    Add logging management endpoints to the FastAPI app.

    Args:
        app: FastAPI application instance
        api_config: API configuration dictionary
        auth_data: Authentication configuration dictionary
    """
    router = APIRouter(prefix="/system", tags=["Logs"])

    # Create system auth dependency using the provided auth configuration
    system_config = api_config.get("system", {})
    auth_method = system_config.get("auth_method", "system_api_key")

    if auth_data:
        get_system_auth = create_system_auth_dependency(auth_data, auth_method)
    else:
        # Fallback to basic auth for backward compatibility
        def get_system_auth(api_key: str = Depends(system_api_key)):
            return api_key

    @router.get("/logging/status", summary="Get current logging status")
    async def get_logging_status_endpoint(auth: str = Depends(get_system_auth)):
        """Get the current logging configuration and status."""
        try:
            status = get_logging_status(api_config)
            return {"status": "success", "data": status}
        except Exception as e:
            logging.error(f"Error getting logging status: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get logging status: {str(e)}")

    @router.post("/logging/config", summary="Update logging configuration")
    async def update_logging_config_endpoint(config_update: LoggingConfigUpdate, auth: str = Depends(get_system_auth)):
        """Update the logging configuration at runtime."""
        try:
            # Convert Pydantic model to dict, excluding None values
            new_config = config_update.model_dump(exclude_none=True)

            if not new_config:
                raise HTTPException(status_code=400, detail="No configuration parameters provided")

            # Validate log level if provided
            if "level" in new_config:
                valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                if new_config["level"].upper() not in valid_levels:
                    raise HTTPException(status_code=400, detail=f"Invalid log level. Must be one of: {', '.join(valid_levels)}")
                new_config["level"] = new_config["level"].upper()

            # Update configuration
            updated_config = update_logging_config(api_config, new_config)

            logging.info(f"Logging configuration updated: {new_config}")

            return {"status": "success", "message": "Logging configuration updated successfully", "data": get_logging_status(updated_config)}

        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Error updating logging configuration: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to update logging configuration: {str(e)}")

    @router.get("/logging/logs", summary="Get recent log entries")
    async def get_recent_logs(lines: int = Query(50, description="Number of recent lines to return", ge=1, le=10000), auth: str = Depends(get_system_auth)):
        """Get recent log entries from the log file."""
        try:
            logging_config = api_config.get("logging", {})
            log_file_path = logging_config.get("file_path", "/app/latest.logs")

            try:
                with open(log_file_path, "r", encoding="utf-8") as f:
                    all_lines = f.readlines()
                    recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

                return {"status": "success", "data": {"total_lines": len(all_lines), "returned_lines": len(recent_lines), "logs": [line.rstrip("\n") for line in recent_lines]}}
            except FileNotFoundError:
                return {"status": "success", "data": {"total_lines": 0, "returned_lines": 0, "logs": [], "message": "Log file not found"}}

        except Exception as e:
            logging.error(f"Error reading log file: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to read log file: {str(e)}")

    @router.delete("/logging/logs", summary="Clear log file")
    async def clear_logs(auth: str = Depends(get_system_auth)):
        """Clear the current log file."""
        try:
            logging_config = api_config.get("logging", {})

            # Check if log deletion is allowed
            if not logging_config.get("allow_log_deletion", True):
                raise HTTPException(status_code=403, detail="Log file deletion is disabled in the configuration")

            log_file_path = logging_config.get("file_path", "/app/latest.logs")

            try:
                # Clear the file by opening it in write mode and immediately closing
                with open(log_file_path, "w", encoding="utf-8"):
                    pass

                logging.info("Log file cleared via API")

                return {"status": "success", "message": "Log file cleared successfully"}
            except FileNotFoundError:
                return {"status": "success", "message": "Log file did not exist"}

        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Error clearing log file: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to clear log file: {str(e)}")

    # Add the router to the app
    app.include_router(router)
