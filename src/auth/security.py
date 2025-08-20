"""
Authentication and security utilities for the mock API server.
"""

import random
import re
from typing import Any, Optional

from fastapi import Depends, HTTPException, Request, Security
from fastapi.responses import JSONResponse
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)
from fastapi.security.api_key import APIKeyHeader

# Security schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
csrf_token_header = APIKeyHeader(name="X-XSRF-TOKEN", auto_error=False)
session_cookie = APIKeyHeader(name="Cookie", auto_error=False)
security_basic = HTTPBasic(auto_error=False)
security_bearer = HTTPBearer(auto_error=False)

# System API key security scheme (static for proper OpenAPI integration)
system_api_key = APIKeyHeader(name="X-API-Key", description="System API Key for admin endpoints")


def create_system_auth_dependency(auth_config: dict[str, Any], auth_method: str = "system_api_key"):
    """
    Create a system authentication dependency that uses the centralized auth configuration.

    Args:
        auth_config: Authentication configuration dictionary
        auth_method: Authentication method name to use (default: "system_api_key")

    Returns:
        FastAPI dependency function for system authentication
    """

    def get_system_auth(api_key: str = Depends(system_api_key)):
        """Dependency for system authentication (actual validation is done by middleware)."""
        return api_key

    return get_system_auth


# Global cache for consistent auth placeholder resolution within request cycles
_auth_resolution_cache = {}


def clear_auth_resolution_cache():
    """Clear the auth resolution cache for a new request cycle."""
    global _auth_resolution_cache
    _auth_resolution_cache = {}


def resolve_auth_placeholders(value: Any, auth_config: Optional[dict[str, Any]] = None, request_context: Optional[dict] = None) -> Any:
    """
    Resolves authentication placeholders in configuration values.

    Supported placeholders:
    - ${auth.vmanage_session.random_session.session_id} - Random session ID
    - ${auth.vmanage_session.random_session.csrf_token} - Corresponding CSRF token
    - ${auth.vmanage_session.current_session.csrf_token} - CSRF token for current session
    - ${auth.csrf_token.random_key} - Random CSRF token from valid_keys
    - ${auth.api_key.random_key} - Random API key

    Args:
        value: The value to process for placeholders
        auth_config: Authentication configuration
        request_context: Optional context with current session info
    """
    if isinstance(value, str) and "${auth." in value:
        # Pattern to match ${auth.method.selector.property}
        pattern = r"\$\{auth\.([^.]+)\.([^.}]+)(?:\.([^}]+))?\}"

        def replace_placeholder(match):
            method = match.group(1)
            selector = match.group(2)
            property_name = match.group(3)

            if auth_config is None:
                return match.group(0)  # Return original placeholder

            auth_methods = auth_config.get("authentication_methods", {})
            method_config = auth_methods.get(method)

            if not method_config:
                return match.group(0)  # Return original placeholder

            if method == "vmanage_session":
                if selector == "current_session" and request_context:
                    # Find the session that matches the current request
                    current_session_id = request_context.get("session_id")
                    if current_session_id:
                        valid_sessions = method_config.get("valid_sessions", [])
                        for session in valid_sessions:
                            if session.get("session_id") == current_session_id:
                                if property_name == "csrf_token":
                                    return session.get("csrf_token", "")
                                elif property_name == "session_id":
                                    return session.get("session_id", "")
                                elif property_name == "username":
                                    return session.get("username", "")
                    return match.group(0)  # Return original if no match

                elif selector == "random_session":
                    # Use cached random session for consistency within request
                    cache_key = f"{method}.{selector}"
                    if cache_key not in _auth_resolution_cache:
                        valid_sessions = method_config.get("valid_sessions", [])
                        if valid_sessions:
                            _auth_resolution_cache[cache_key] = random.choice(valid_sessions)
                        else:
                            return match.group(0)

                    random_session = _auth_resolution_cache[cache_key]
                    if property_name == "session_id":
                        return random_session.get("session_id", "")
                    elif property_name == "csrf_token":
                        return random_session.get("csrf_token", "")
                    elif property_name == "username":
                        return random_session.get("username", "")
                    else:
                        return str(random_session)

            elif selector == "random_key":
                cache_key = f"{method}.{selector}"
                if cache_key not in _auth_resolution_cache:
                    valid_keys = method_config.get("valid_keys", [])
                    if valid_keys:
                        _auth_resolution_cache[cache_key] = random.choice(valid_keys)
                    else:
                        return match.group(0)

                return _auth_resolution_cache[cache_key]

            return match.group(0)  # Return original placeholder

        # Replace all placeholders in the string
        resolved = re.sub(pattern, replace_placeholder, value)
        return resolved

    elif isinstance(value, dict):
        # Recursively resolve placeholders in dictionary values
        return {k: resolve_auth_placeholders(v, auth_config, request_context) for k, v in value.items()}

    elif isinstance(value, list):
        # Recursively resolve placeholders in list items
        return [resolve_auth_placeholders(item, auth_config, request_context) for item in value]

    return value


def extract_request_context(request: Request, auth_config: dict[str, Any]) -> dict:
    """Extract session context from the request for placeholder resolution."""
    session_config = auth_config.get("authentication_methods", {}).get("vmanage_session", {})
    session_cookie_name = session_config.get("session_cookie", "JSESSIONID")

    # Check for session cookie in request cookies first
    session_id = request.cookies.get(session_cookie_name)

    # If not found in cookies, check headers (for Swagger UI)
    if not session_id:
        session_cookie_header = request.headers.get("Cookie")
        if session_cookie_header and "=" in session_cookie_header:
            cookie_parts = session_cookie_header.split("=", 1)
            if cookie_parts[0].strip() == session_cookie_name:
                session_id = cookie_parts[1].strip()

    return {"session_id": session_id} if session_id else {}


def check_required_headers(request: Request, required_headers: dict[str, str]) -> Optional[JSONResponse]:
    """
    Check if request contains required headers with expected values.
    Returns None if validation passes, otherwise returns error response.
    """
    if not required_headers:
        return None

    for header_name, expected_value in required_headers.items():
        actual_value = request.headers.get(header_name)
        if actual_value != expected_value:
            return JSONResponse(status_code=400, content={"error": f"Missing or invalid header: {header_name}", "expected": expected_value, "received": actual_value})
    return None


def get_security_dependencies(auth_methods: list[str], auth_config: dict[str, Any]):
    """Returns the appropriate security dependencies for the given auth methods."""
    if not auth_methods:
        return None

    # Create a custom dependency that handles multiple auth types
    async def verify_auth(request: Request, api_key: Optional[str] = Security(api_key_header), csrf_token: Optional[str] = Security(csrf_token_header), session_cookie_header: Optional[str] = Security(session_cookie), credentials: Optional[HTTPBasicCredentials] = Security(security_basic), bearer: Optional[HTTPAuthorizationCredentials] = Security(security_bearer)):
        # Collect validation results for all required methods
        auth_errors = []
        auth_results = {}

        # Check API Key if required
        if "api_key" in auth_methods:
            if api_key:
                api_key_config = auth_config.get("authentication_methods", {}).get("api_key", {})
                valid_keys = api_key_config.get("valid_keys", [])
                if api_key in valid_keys:
                    auth_results["api_key"] = {"type": "api_key", "value": api_key}
                else:
                    auth_errors.append("Invalid API key")
            else:
                auth_errors.append("Missing API key")

        # Check CSRF Token if required
        if "csrf_token" in auth_methods:
            if csrf_token:
                csrf_config = auth_config.get("authentication_methods", {}).get("csrf_token", {})
                valid_tokens = csrf_config.get("valid_keys", [])
                if csrf_token in valid_tokens:
                    auth_results["csrf_token"] = {"type": "csrf_token", "value": csrf_token}
                else:
                    auth_errors.append("Invalid CSRF token")
            else:
                auth_errors.append("Missing CSRF token")

        # Check Basic Auth if required
        if "basic_auth" in auth_methods:
            if credentials:
                basic_config = auth_config.get("authentication_methods", {}).get("basic_auth", {})
                valid_credentials = basic_config.get("valid_credentials", [])
                valid_cred = None
                for cred in valid_credentials:
                    if cred.get("username") == credentials.username and cred.get("password") == credentials.password:
                        valid_cred = cred
                        break
                if valid_cred:
                    auth_results["basic_auth"] = {"type": "basic", "value": credentials.username}
                else:
                    auth_errors.append("Invalid credentials")
            else:
                auth_errors.append("Missing basic auth credentials")

        # Check Bearer Token if required
        if any(method in auth_methods for method in ["oidc_auth_code", "oidc_client_credentials"]):
            if bearer:
                valid_token_found = False
                for auth_method in ["oidc_auth_code", "oidc_client_credentials"]:
                    if auth_method in auth_methods:
                        oidc_config = auth_config.get("authentication_methods", {}).get(auth_method, {})
                        valid_tokens = oidc_config.get("valid_tokens", [])
                        for valid_token in valid_tokens:
                            if valid_token.get("access_token") == bearer.credentials:
                                auth_results["oidc"] = {"type": "bearer", "value": bearer.credentials}
                                valid_token_found = True
                                break
                    if valid_token_found:
                        break
                if not valid_token_found:
                    auth_errors.append("Invalid bearer token")
            else:
                auth_errors.append("Missing bearer token")

        # Check vManage Session if required
        if "vmanage_session" in auth_methods:
            session_config = auth_config.get("authentication_methods", {}).get("vmanage_session", {})
            session_cookie_name = session_config.get("session_cookie", "JSESSIONID")
            valid_sessions = session_config.get("valid_sessions", [])

            # Check for session cookie in request cookies first
            session_id = request.cookies.get(session_cookie_name)

            # If not found in cookies, check if provided via Cookie header
            # (for Swagger UI)
            if not session_id and session_cookie_header:
                # Parse cookie header manually for Swagger UI
                # Expected format: "JSESSIONID=value" or just "value"
                if "=" in session_cookie_header:
                    cookie_parts = session_cookie_header.split("=", 1)
                    if cookie_parts[0].strip() == session_cookie_name:
                        session_id = cookie_parts[1].strip()
                else:
                    # Assume the whole value is the session ID
                    session_id = session_cookie_header.strip()

            if session_id:
                valid_session = None
                for session in valid_sessions:
                    if session.get("session_id") == session_id:
                        valid_session = session
                        break
                if valid_session:
                    auth_results["vmanage_session"] = {"type": "session", "value": session_id, "username": valid_session.get("username")}
                else:
                    auth_errors.append("Invalid session cookie")
            else:
                auth_errors.append("Missing session cookie")

        # Check if ALL required auth methods passed
        missing_methods = []
        for method in auth_methods:
            # Map method names to result keys
            result_key = method
            if method in ["oidc_auth_code", "oidc_client_credentials"]:
                result_key = "oidc"

            if result_key not in auth_results:
                missing_methods.append(method)

        if missing_methods:
            raise HTTPException(status_code=401, detail=(f"Authentication failed. Required methods: " f"{', '.join(auth_methods)}. " f"Errors: {'; '.join(auth_errors)}"))

        # Return combined auth info
        return auth_results

    return [Depends(verify_auth)]
