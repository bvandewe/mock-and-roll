"""
System authentication middleware for protecting admin/system endpoints.

This middleware validates X-API-Key headers for system endpoints like
logging management and cache administration.
"""

import logging
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class SystemAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to protect system endpoints with API key authentication.

    Validates X-API-Key header against configured system API keys for
    endpoints that start with /admin/ or /system/.
    """

    def __init__(self, app, api_config: dict[str, Any], auth_config: dict[str, Any]):
        """
        Initialize the system authentication middleware.

        Args:
            app: The FastAPI application
            api_config: API configuration dictionary
            auth_config: Authentication configuration dictionary
        """
        super().__init__(app)
        self.api_config = api_config
        self.auth_config = auth_config
        self.logger = logging.getLogger("api.system_auth")

        # Get system configuration
        system_config = api_config.get("system", {})
        self.protection_enabled = system_config.get("protect_endpoints", False)
        self.auth_method = system_config.get("auth_method", "system_api_key")

        # Load valid API keys
        self.valid_keys = self._load_valid_keys()

        # Protected path prefixes
        self.protected_prefixes = ["/admin/", "/system/"]

    def _load_valid_keys(self) -> list[str]:
        """
        Load valid API keys from auth configuration.

        Returns:
            List of valid API keys
        """
        try:
            auth_methods = self.auth_config.get("authentication_methods", {})
            system_auth = auth_methods.get(self.auth_method, {})
            return system_auth.get("valid_keys", [])
        except Exception as e:
            self.logger.error(f"Failed to load system API keys: {e}")
            return []

    def _is_protected_endpoint(self, path: str) -> bool:
        """
        Check if the endpoint path should be protected.

        Args:
            path: Request path

        Returns:
            True if endpoint should be protected
        """
        return any(path.startswith(prefix) for prefix in self.protected_prefixes)

    def _validate_api_key(self, api_key: str) -> bool:
        """
        Validate the provided API key.

        Args:
            api_key: API key to validate

        Returns:
            True if API key is valid
        """
        return api_key in self.valid_keys

    async def dispatch(self, request: Request, call_next):
        """
        Process the request and validate system authentication if needed.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            The HTTP response

        Raises:
            HTTPException: If authentication fails for protected endpoints
        """
        # Check if protection is enabled
        if not self.protection_enabled:
            return await call_next(request)

        # Check if this is a protected endpoint
        if not self._is_protected_endpoint(request.url.path):
            return await call_next(request)

        # Get API key from header
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            self.logger.warning(f"Missing API key for protected endpoint: {request.url.path}")
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Missing X-API-Key header for system endpoint"}, headers={"WWW-Authenticate": "X-API-Key"})

        # Validate API key
        if not self._validate_api_key(api_key):
            self.logger.warning(f"Invalid API key for protected endpoint: {request.url.path}")
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Invalid API key for system endpoint"})

        # Log successful authentication
        self.logger.info(f"System authentication successful for: {request.url.path}")

        # Continue to next middleware/handler
        return await call_next(request)
