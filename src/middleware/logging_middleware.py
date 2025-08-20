"""
Request/Response logging middleware for the mock API server.

This middleware logs detailed information about all HTTP requests and responses,
including headers, body content, and timing information.
"""

import json
import logging
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestResponseLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses with detailed information.

    Logs include:
    - Unique request ID for correlating request/response pairs
    - Request method, URL, headers, query parameters
    - Request body (for POST/PUT/PATCH requests)
    - Response status code, headers
    - Response body (truncated if too large)
    - Request processing time
    """

    def __init__(self, app, max_body_size: int = 1024):
        """
        Initialize the logging middleware.

        Args:
            app: The FastAPI application
            max_body_size: Maximum size of request/response body to log (in characters)
        """
        super().__init__(app)
        self.max_body_size = max_body_size
        self.logger = logging.getLogger("api.requests")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and log detailed information.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            The HTTP response
        """
        start_time = time.time()

        # Generate unique request ID for correlation
        request_id = str(uuid.uuid4())[:8]  # Use first 8 characters for brevity

        # Extract request information
        method = request.method
        url = str(request.url)
        client_ip = self._get_client_ip(request)
        headers = dict(request.headers)
        query_params = dict(request.query_params)

        # Log request details with request ID
        self.logger.info(f"[{request_id}] REQUEST: {method} {url} from {client_ip}")
        self.logger.debug(f"[{request_id}] Request Headers: {headers}")
        if query_params:
            self.logger.debug(f"[{request_id}] Query Parameters: {query_params}")

        # Log request body for POST/PUT/PATCH requests
        request_body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    request_body = body_bytes.decode("utf-8")
                    if len(request_body) > self.max_body_size:
                        truncated_body = request_body[: self.max_body_size] + "... [TRUNCATED]"
                        self.logger.debug(f"[{request_id}] Request Body: {truncated_body}")
                    else:
                        self.logger.debug(f"[{request_id}] Request Body: {request_body}")

                    # Try to parse as JSON for better formatting
                    try:
                        json_body = json.loads(request_body)
                        self.logger.debug(f"[{request_id}] Request Body (JSON): {json.dumps(json_body, indent=2)}")
                    except json.JSONDecodeError:
                        pass  # Not JSON, already logged as string

            except Exception as e:
                self.logger.warning(f"[{request_id}] Failed to read request body: {e}")

        # Process the request
        try:
            response = await call_next(request)
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"[{request_id}] REQUEST FAILED: {method} {url} - Exception: {str(e)} - Time: {processing_time:.3f}s")
            raise

        # Calculate processing time
        processing_time = time.time() - start_time

        # Log response details
        status_code = response.status_code
        response_headers = dict(response.headers)

        self.logger.info(f"[{request_id}] RESPONSE: {status_code} for {method} {url} - Time: {processing_time:.3f}s")
        self.logger.debug(f"[{request_id}] Response Headers: {response_headers}")

        # Log response body if in DEBUG mode, but skip /docs and /system/logs endpoints to prevent recursive logging
        should_log_response_body = self.logger.isEnabledFor(logging.DEBUG) and not request.url.path.endswith("/docs") and not request.url.path.endswith("/openapi.json") and not request.url.path.endswith("/system/logs")

        if should_log_response_body:
            try:
                # Read response body
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk

                if response_body:
                    body_str = response_body.decode("utf-8")
                    if len(body_str) > self.max_body_size:
                        truncated_body = body_str[: self.max_body_size] + "... [TRUNCATED]"
                        self.logger.debug(f"[{request_id}] Response Body: {truncated_body}")
                    else:
                        self.logger.debug(f"[{request_id}] Response Body: {body_str}")

                    # # Try to parse as JSON for better formatting
                    # try:
                    #     json_body = json.loads(body_str)
                    #     self.logger.debug(f"[{request_id}] Response Body (JSON): {json.dumps(json_body, indent=2)}")
                    # except json.JSONDecodeError:
                    #     pass  # Not JSON, already logged as string

                # Create new response with the body we read
                from fastapi import Response as FastAPIResponse

                response = FastAPIResponse(content=response_body, status_code=status_code, headers=dict(response.headers), media_type=response.headers.get("content-type"))

            except Exception as e:
                self.logger.warning(f"[{request_id}] Failed to read response body: {e}")
        else:
            # For /system/logs endpoint, just log that we're skipping response body logging
            if request.url.path.endswith("/system/logs"):
                self.logger.debug(f"[{request_id}] Skipping response body logging for /system/logs endpoint to prevent recursion")

        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract the client IP address from the request.

        Args:
            request: The HTTP request

        Returns:
            The client IP address as a string
        """
        # Check for X-Forwarded-For header (common in reverse proxy setups)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check for X-Real-IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fall back to direct client IP
        if request.client:
            return request.client.host

        return "unknown"
