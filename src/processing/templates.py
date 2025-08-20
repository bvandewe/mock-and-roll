"""
Request/response processing utilities for the mock API server.
"""

import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional


def resolve_auth_placeholders(value: Any, auth_config: Optional[dict[str, Any]] = None, request_context: Optional[dict] = None) -> Any:
    """
    Import the resolve_auth_placeholders function from auth.security.
    This avoids circular imports by importing only when needed.
    """
    from auth.security import resolve_auth_placeholders as _resolve_auth_placeholders

    return _resolve_auth_placeholders(value, auth_config, request_context)


def check_conditions(data: dict[str, Any], conditions: dict[str, Any]) -> bool:
    """Checks if the request body satisfies all conditions."""
    if not conditions:
        return False

    for key, expected_value in conditions.items():
        if data.get(key) != expected_value:
            return False
    return True


def process_response_body(body: Any, auth_config: Optional[dict[str, Any]] = None, request_context: Optional[dict] = None) -> Any:
    """Process response body to replace template variables and auth placeholders."""
    if isinstance(body, dict):
        processed = {}
        for key, value in body.items():
            processed[key] = process_response_body(value, auth_config, request_context)
        return processed
    elif isinstance(body, list):
        return [process_response_body(item, auth_config, request_context) for item in body]
    elif isinstance(body, str):
        # First resolve auth placeholders
        resolved_body = resolve_auth_placeholders(body, auth_config, request_context)

        # Then replace other template variables
        if resolved_body == "{{random_uuid}}":
            return str(uuid.uuid4())
        elif resolved_body == "{{current_timestamp}}":
            return datetime.utcnow().isoformat() + "Z"
        elif resolved_body == "{{timestamp}}":
            return generate_realistic_timestamp()
        elif resolved_body == "{{date}}":
            return generate_realistic_date()
        elif resolved_body == "{{unix_timestamp}}":
            return generate_realistic_unix_timestamp()
        elif resolved_body == "{{unix_timestamp_ms}}":
            return generate_realistic_unix_timestamp_ms()
        else:
            # Check for realistic timestamp patterns
            resolved_body = substitute_timestamp_templates(resolved_body)

            # Handle path parameter substitution like {product_id}
            resolved_body = re.sub(r"\{(\w+)\}", lambda m: f"path_param_{m.group(1)}", resolved_body)

            return resolved_body
    else:
        return body


def substitute_timestamp_templates(text: str) -> str:
    """
    Replace static timestamps with realistic, recent timestamps.

    This function identifies timestamp patterns and replaces them with realistic
    timestamps that are recent but not exactly current time, making mock responses
    more believable for testing and development.
    """
    if not isinstance(text, str):
        return text

    # Common timestamp patterns
    timestamp_patterns = [
        # ISO 8601 with Z suffix (UTC): 2025-08-19T10:30:00Z
        (r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", generate_realistic_timestamp),
        # ISO 8601 with timezone: 2025-08-19T10:30:00+00:00
        (r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", generate_realistic_timestamp),
        # ISO 8601 basic: 2025-08-19T10:30:00
        (r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", generate_realistic_timestamp),
        # Date only: 2025-08-19
        (r"\d{4}-\d{2}-\d{2}(?!T)", generate_realistic_date),
        # Unix timestamp (10 digits): 1724058600
        (r"\b\d{10}\b", generate_realistic_unix_timestamp),
        # Unix timestamp milliseconds (13 digits): 1724058600000
        (r"\b\d{13}\b", generate_realistic_unix_timestamp_ms),
    ]

    result = text
    for pattern, generator in timestamp_patterns:
        result = re.sub(pattern, lambda m: generator(), result)

    return result


def generate_realistic_timestamp() -> str:
    """Generate a realistic timestamp that's recent but not current."""
    # Generate a timestamp between 1-30 minutes ago to make it seem recent but realistic
    now = datetime.now(timezone.utc)
    minutes_ago = 1 + (hash(str(now.microsecond)) % 30)  # Pseudo-random but deterministic
    realistic_time = now - timedelta(minutes=minutes_ago)
    return realistic_time.isoformat() + "Z"


def generate_realistic_date() -> str:
    """Generate a realistic date that's recent but not today."""
    now = datetime.now(timezone.utc)
    days_ago = 1 + (hash(str(now.microsecond)) % 7)  # 1-7 days ago
    realistic_date = now - timedelta(days=days_ago)
    return realistic_date.strftime("%Y-%m-%d")


def generate_realistic_unix_timestamp() -> str:
    """Generate a realistic Unix timestamp."""
    now = datetime.now(timezone.utc)
    minutes_ago = 1 + (hash(str(now.microsecond)) % 30)
    realistic_time = now - timedelta(minutes=minutes_ago)
    return str(int(realistic_time.timestamp()))


def generate_realistic_unix_timestamp_ms() -> str:
    """Generate a realistic Unix timestamp in milliseconds."""
    now = datetime.now(timezone.utc)
    minutes_ago = 1 + (hash(str(now.microsecond)) % 30)
    realistic_time = now - timedelta(minutes=minutes_ago)
    return str(int(realistic_time.timestamp() * 1000))


def process_response_headers(headers: dict[str, Any], auth_config: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Process response headers to replace auth placeholders."""
    processed_headers = {}
    for key, value in headers.items():
        processed_headers[key] = resolve_auth_placeholders(value, auth_config)

    return processed_headers
