#!/usr/bin/env python3
"""
Test module for Webex configuration profile validation.

Tests cover Webex authentication and endpoint exposure to ensure the
new config profile is consistent with the runtime configuration model.
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from typing import Any

from fastapi import Request

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.factory import create_app
from config.loader import load_auth_config
from config.loader import load_endpoints_config
from config.loader import load_api_config
from handlers import routes as route_handlers
from handlers.routes import create_handler
from handlers.routes import create_handler_with_body
from routes.setup import setup_routes

WEBEX_CONFIG_PATH = Path(__file__).resolve().parent.parent / "configs" / "webex"


def load_webex_runtime_config(
    monkeypatch: object,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Load Webex profile configuration for runtime-style tests."""
    monkeypatch.setenv("MOCK_CONFIG_FOLDER", str(WEBEX_CONFIG_PATH))

    api_config = load_api_config()
    auth_config = load_auth_config()
    endpoints_config = load_endpoints_config()
    return api_config, auth_config, endpoints_config


def get_endpoint_config(endpoints_config: dict[str, Any], path: str, method: str) -> dict[str, Any]:
    """Return the matching endpoint config for a path and method."""
    for endpoint in endpoints_config.get("endpoints", []):
        if endpoint.get("path") == path and endpoint.get("method") == method:
            return endpoint
    raise AssertionError(f"Endpoint not found for {method} {path}")


def create_request(method: str, path: str, headers: dict[str, str] | None = None) -> Request:
    """Create a minimal request instance for direct handler invocation."""
    encoded_headers = []
    for key, value in (headers or {}).items():
        encoded_headers.append((key.lower().encode("utf-8"), value.encode("utf-8")))

    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": method,
        "path": path,
        "headers": encoded_headers,
        "query_string": b"",
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
        "scheme": "http",
    }
    return Request(scope)


def decode_response_json(response: Any) -> dict[str, Any]:
    """Decode JSON content from a FastAPI response object."""
    return json.loads(response.body.decode("utf-8"))


def create_in_memory_persistence(monkeypatch: object) -> dict[str, list[dict[str, object]]]:
    """Mock Redis persistence helpers with an in-memory store for route tests."""
    store: dict[str, list[dict[str, object]]] = {"rooms": [], "memberships": []}

    def fake_store_entity(
        entity_name: str, data: dict[str, object], entity_id: str | None = None
    ) -> str:
        generated_id = entity_id or f"{entity_name}-{len(store.get(entity_name, [])) + 1}"
        entity = {
            "id": generated_id,
            "entity_type": entity_name,
            "created_at": "2026-05-20T00:00:00",
            "data": data,
        }
        store.setdefault(entity_name, []).append(entity)
        return generated_id

    def fake_list_entities(entity_name: str) -> list[dict[str, object]]:
        return list(store.get(entity_name, []))

    monkeypatch.setattr(route_handlers, "store_entity", fake_store_entity)
    monkeypatch.setattr(route_handlers, "list_entities", fake_list_entities)
    return store


def test_webex_security_schemes_match_auth_config(monkeypatch):
    """Test Webex profile exposes only its configured security schemes."""
    monkeypatch.setenv("MOCK_CONFIG_FOLDER", str(WEBEX_CONFIG_PATH))

    auth_config = load_auth_config()
    app = create_app()
    openapi_schema = app.openapi()

    auth_methods = auth_config.get("authentication_methods", {})
    security_schemes = openapi_schema.get("components", {}).get("securitySchemes", {})

    assert set(auth_methods.keys()) == {"oidc_auth_code", "system_api_key"}
    assert set(security_schemes.keys()) == set(auth_methods.keys())
    assert security_schemes["oidc_auth_code"]["type"] == "http"
    assert security_schemes["oidc_auth_code"]["scheme"] == "bearer"
    assert security_schemes["system_api_key"]["type"] == "apiKey"


def test_webex_profile_exposes_expected_paths(monkeypatch):
    """Test Webex profile publishes the documented room and membership paths."""
    monkeypatch.setenv("MOCK_CONFIG_FOLDER", str(WEBEX_CONFIG_PATH))

    auth_config = load_auth_config()
    endpoints_config = load_endpoints_config()
    app = create_app()
    setup_routes(app, endpoints_config, auth_config)
    openapi_schema = app.openapi()
    paths = openapi_schema.get("paths", {})

    assert "/rooms" in paths
    assert "/memberships" in paths
    assert "get" in paths["/rooms"]
    assert "post" in paths["/rooms"]
    assert "get" in paths["/memberships"]
    assert "post" in paths["/memberships"]
    assert paths["/rooms"]["get"].get("security") == [{"oidc_auth_code": []}]
    assert paths["/memberships"]["post"].get("security") == [{"oidc_auth_code": []}]


def test_webex_profile_enables_redis_persistence(monkeypatch):
    """Test Webex profile declares Redis persistence for its dynamic room endpoints."""
    api_config, _, endpoints_config = load_webex_runtime_config(monkeypatch)
    endpoints_by_path_method = {
        (endpoint["path"], endpoint["method"]): endpoint
        for endpoint in endpoints_config["endpoints"]
    }

    assert api_config.get("persistence") == "redis"
    assert endpoints_by_path_method[("/rooms", "GET")]["persistence"]["action"] == "list"
    assert endpoints_by_path_method[("/rooms", "POST")]["persistence"]["action"] == "create"
    assert endpoints_by_path_method[("/memberships", "GET")]["persistence"]["action"] == "list"
    assert endpoints_by_path_method[("/memberships", "POST")]["persistence"]["action"] == "create"


def test_webex_create_room_persists_and_list_includes_new_room(monkeypatch):
    """Test creating a room persists the generated room and exposes it from GET /rooms."""
    store = create_in_memory_persistence(monkeypatch)
    _, auth_config, endpoints_config = load_webex_runtime_config(monkeypatch)
    create_room_handler = create_handler_with_body(
        get_endpoint_config(endpoints_config, "/rooms", "POST"), auth_config
    )
    list_rooms_handler = create_handler(
        get_endpoint_config(endpoints_config, "/rooms", "GET"), auth_config
    )

    create_response = asyncio.run(
        create_room_handler(
            request=create_request("POST", "/rooms", headers={"Content-Type": "application/json"}),
            body={"title": "My Persisted Room", "description": "Created in test"},
        )
    )

    assert create_response.status_code == 200
    created_room = decode_response_json(create_response)
    assert created_room["title"] == "My Persisted Room"
    assert created_room["description"] == "Created in test"
    assert store["rooms"][0]["data"]["id"] == created_room["id"]

    list_response = asyncio.run(list_rooms_handler(request=create_request("GET", "/rooms")))

    assert list_response.status_code == 200
    rooms = decode_response_json(list_response)["items"]
    assert any(
        room["id"] == created_room["id"] and room["title"] == "My Persisted Room" for room in rooms
    )


def test_webex_create_room_rejects_missing_or_empty_title(monkeypatch):
    """Test creating a room rejects both omitted and empty-string titles."""
    store = create_in_memory_persistence(monkeypatch)
    _, auth_config, endpoints_config = load_webex_runtime_config(monkeypatch)
    create_room_handler = create_handler_with_body(
        get_endpoint_config(endpoints_config, "/rooms", "POST"), auth_config
    )

    missing_title_response = asyncio.run(
        create_room_handler(
            request=create_request("POST", "/rooms", headers={"Content-Type": "application/json"}),
            body={"description": "Created in test"},
        )
    )
    empty_title_response = asyncio.run(
        create_room_handler(
            request=create_request("POST", "/rooms", headers={"Content-Type": "application/json"}),
            body={"title": "", "description": "Created in test"},
        )
    )

    missing_title_body = decode_response_json(missing_title_response)
    empty_title_body = decode_response_json(empty_title_response)

    assert missing_title_response.status_code == 400
    assert empty_title_response.status_code == 400
    assert missing_title_body["message"] == "Title cannot be empty."
    assert empty_title_body["message"] == "Title cannot be empty."
    assert store["rooms"] == []


def test_webex_add_membership_persists_and_invalid_membership_does_not(monkeypatch):
    """Test membership persistence stores successful creates and skips configured error responses."""
    store = create_in_memory_persistence(monkeypatch)
    _, auth_config, endpoints_config = load_webex_runtime_config(monkeypatch)
    create_membership_handler = create_handler_with_body(
        get_endpoint_config(endpoints_config, "/memberships", "POST"), auth_config
    )
    list_memberships_handler = create_handler(
        get_endpoint_config(endpoints_config, "/memberships", "GET"), auth_config
    )

    invalid_response = asyncio.run(
        create_membership_handler(
            request=create_request(
                "POST", "/memberships", headers={"Content-Type": "application/json"}
            ),
            body={
                "roomId": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vMzk5ZWE4ZTAtM2YwZC0xMWYxLWE4NjQtNTM5NjdjZTYyMjkw",
                "personEmail": "aytac125@gmail.com",
                "isModerator": False,
            },
        )
    )

    assert invalid_response.status_code == 409
    assert store["memberships"] == []

    create_response = asyncio.run(
        create_membership_handler(
            request=create_request(
                "POST", "/memberships", headers={"Content-Type": "application/json"}
            ),
            body={
                "roomId": "room-123",
                "personEmail": "new.member@example.com",
                "isModerator": True,
            },
        )
    )

    assert create_response.status_code == 200
    created_membership = decode_response_json(create_response)
    assert created_membership["personEmail"] == "new.member@example.com"
    assert created_membership["isModerator"] is True
    assert store["memberships"][0]["data"]["id"] == created_membership["id"]

    list_response = asyncio.run(
        list_memberships_handler(request=create_request("GET", "/memberships"))
    )

    assert list_response.status_code == 200
    memberships = decode_response_json(list_response)["items"]
    assert any(
        membership["id"] == created_membership["id"]
        and membership["personEmail"] == "new.member@example.com"
        for membership in memberships
    )
