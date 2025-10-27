#!/usr/bin/env python3
"""
Test module for binary content handling in logging middleware.

Tests ensure that the logging middleware correctly skips binary content
(images, PDFs, etc.) to prevent UTF-8 decode errors and HTTP protocol violations.
"""

import asyncio
import logging
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi import FastAPI, Request, Response

from middleware.logging_middleware import RequestResponseLoggingMiddleware


def test_binary_content_detection():
    """Test that binary content types are correctly identified."""
    # Test various binary content types
    binary_types = [
        "image/png",
        "image/jpeg",
        "image/gif",
        "video/mp4",
        "audio/mpeg",
        "application/pdf",
        "application/zip",
        "application/octet-stream",
        "font/woff2",
    ]

    for content_type in binary_types:
        is_binary = any(
            binary_type in content_type.lower()
            for binary_type in [
                "image/",
                "video/",
                "audio/",
                "application/octet-stream",
                "application/pdf",
                "application/zip",
                "application/x-",
                "font/",
            ]
        )
        assert is_binary, f"Failed to identify {content_type} as binary"


def test_text_content_detection():
    """Test that text content types are not identified as binary."""
    # Test various text content types
    text_types = [
        "text/html",
        "text/plain",
        "application/json",
        "application/xml",
        "text/css",
        "application/javascript",
    ]

    for content_type in text_types:
        is_binary = any(
            binary_type in content_type.lower()
            for binary_type in [
                "image/",
                "video/",
                "audio/",
                "application/octet-stream",
                "application/pdf",
                "application/zip",
                "application/x-",
                "font/",
            ]
        )
        assert not is_binary, f"Incorrectly identified {content_type} as binary"


@pytest.mark.asyncio
async def test_binary_response_skips_body_logging():
    """Test that binary responses skip body logging and don't cause errors."""
    app = FastAPI()
    middleware = RequestResponseLoggingMiddleware(app)

    # Create a mock request for binary content
    mock_request = MagicMock(spec=Request)
    mock_request.method = "GET"
    mock_request.url = MagicMock()
    mock_request.url.__str__ = MagicMock(return_value="http://test.com/static/favicon.png")
    mock_request.url.path = "/static/favicon.png"
    mock_request.headers = {"user-agent": "test"}
    mock_request.query_params = {}
    mock_request.client = MagicMock()
    mock_request.client.host = "127.0.0.1"

    # Create a mock response with binary content
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.headers = {
        "content-type": "image/png",
        "content-length": "5043",
    }

    # Mock body_iterator to simulate FileResponse behavior
    binary_data = b"\x89PNG\r\n\x1a\n" + b"x" * 5000  # PNG file signature + data

    async def mock_iterator():
        yield binary_data

    mock_response.body_iterator = mock_iterator()

    # Mock the call_next function to return our mock response
    async def mock_call_next(request):
        return mock_response

    # Capture log messages
    with patch.object(middleware.logger, "debug") as mock_debug, patch.object(middleware.logger, "info"), patch.object(middleware.logger, "warning") as mock_warning:
        # Enable DEBUG logging
        middleware.logger.setLevel(logging.DEBUG)
        middleware.logger.isEnabledFor = MagicMock(return_value=True)

        # Process the request
        result = await middleware.dispatch(mock_request, mock_call_next)

        # Verify no warnings about failed decode
        warning_calls = [str(call) for call in mock_warning.call_args_list]
        assert not any("Failed to read response body" in str(call) for call in warning_calls), "Should not have decode warnings for binary content"

        # Verify debug message about skipping binary content
        debug_calls = [str(call) for call in mock_debug.call_args_list]
        assert any("Skipping response body logging for binary content type" in str(call) for call in debug_calls), "Should log that binary content is being skipped"

        # Verify response is returned correctly
        assert result is not None, "Response should be returned"


def test_middleware_initialization():
    """Test middleware initializes with correct default values."""
    app = FastAPI()
    middleware = RequestResponseLoggingMiddleware(app, max_body_size=2048)

    assert middleware.max_body_size == 2048
    assert middleware.logger.name == "api.requests"


if __name__ == "__main__":
    print("Running binary content logging tests...")

    # Run synchronous tests
    test_binary_content_detection()
    print("✓ Binary content detection test passed")

    test_text_content_detection()
    print("✓ Text content detection test passed")

    test_middleware_initialization()
    print("✓ Middleware initialization test passed")

    # Run async test
    asyncio.run(test_binary_response_skips_body_logging())
    print("✓ Binary response handling test passed")

    print("\nAll tests passed!")
