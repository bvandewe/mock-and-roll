"""
Route handlers for different endpoint types.
"""

import inspect
import json
import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import Body, HTTPException, Request
from fastapi.responses import JSONResponse

from auth.security import clear_auth_resolution_cache
from models.dynamic import create_request_model
from persistence.redis_client import get_entity, list_entities, store_entity
from processing.templates import (
    check_conditions,
    process_response_body,
    process_response_headers,
)


def get_matching_response_rule(
    endpoint_config: dict[str, Any], request_body: dict[str, Any]
) -> dict[str, Any] | None:
    """Get the first response rule matching the incoming request body."""
    for rule in endpoint_config.get("responses", []):
        conditions = rule.get("body_conditions")
        if conditions is None or check_conditions(request_body, conditions):
            return rule
    return None


def extract_persisted_entity_data(entity: dict[str, Any]) -> dict[str, Any]:
    """Extract stored payload data from a persisted entity wrapper."""
    payload = entity.get("data")
    return payload if isinstance(payload, dict) else entity


def build_persistence_list_response(
    request: Request,
    endpoint_config: dict[str, Any],
    auth_config: dict[str, Any],
    entities: list[dict[str, Any]],
) -> JSONResponse:
    """Build a list response that can merge persisted entities into a configured response template."""
    persistence_config = endpoint_config.get("persistence", {})
    list_key = persistence_config.get("response_list_key")

    if not list_key:
        return JSONResponse(status_code=200, content={"entities": entities, "count": len(entities)})

    response_rule = get_matching_response_rule(endpoint_config, {})
    response_data = response_rule.get("response", {}) if response_rule else {}
    status_code = response_data.get("status_code", 200)
    headers = process_response_headers(response_data.get("headers", {}), auth_config)
    request_context = extract_request_context(request, auth_config)
    response_body = process_response_body(
        response_data.get("body", {}), auth_config, request_context
    )

    if not isinstance(response_body, dict):
        return JSONResponse(status_code=status_code, content=response_body, headers=headers)

    static_items = []
    if persistence_config.get("merge_with_static_response", False):
        existing_items = response_body.get(list_key, [])
        if isinstance(existing_items, list):
            static_items = existing_items

    persisted_items = [extract_persisted_entity_data(entity) for entity in entities]
    response_body[list_key] = [*static_items, *persisted_items]

    count_key = persistence_config.get("response_count_key")
    if count_key:
        response_body[count_key] = len(response_body[list_key])

    return JSONResponse(status_code=status_code, content=response_body, headers=headers)


def extract_request_context(request: Request, auth_config: dict[str, Any]) -> dict:
    """Import and call extract_request_context to avoid circular imports."""
    from auth.security import extract_request_context as _extract_request_context

    return _extract_request_context(request, auth_config)


def check_required_headers(request: Request, required_headers: dict[str, str]):
    """Import and call check_required_headers to avoid circular imports."""
    from auth.security import check_required_headers as _check_required_headers

    return _check_required_headers(request, required_headers)


def create_handler_with_body(endpoint_config: dict[str, Any], auth_config: dict[str, Any]):
    """Create a handler that accepts a request body for POST/PUT endpoints."""
    # Create the request model from schema
    request_model = create_request_model(endpoint_config)

    # Extract path parameter names from the path string
    path_param_names = []
    path = endpoint_config.get("path", "")
    for part in path.split("/"):
        if part.startswith("{") and part.endswith("}"):
            path_param_names.append(part[1:-1])

    async def handler(request: Request, **kwargs) -> JSONResponse:
        # Clear auth resolution cache for this request cycle
        clear_auth_resolution_cache()

        # Check required headers first
        required_headers = endpoint_config.get("required_headers", {})
        header_error = check_required_headers(request, required_headers)
        if header_error:
            return header_error

        # Extract body and path parameters from kwargs
        body = kwargs.pop("body", {})

        # Convert Pydantic model to dictionary if needed
        if hasattr(body, "model_dump"):
            request_body = body.model_dump()
        elif hasattr(body, "dict"):
            request_body = body.dict()
        elif isinstance(body, dict):
            request_body = body
        else:
            request_body = {}

        # Check for Redis persistence configuration
        persistence_config = endpoint_config.get("persistence", {})
        entity_name = persistence_config.get("entity_name")

        # Handle Redis operations based on method and configuration
        if (
            request.method == "POST"
            and entity_name
            and persistence_config.get("action") == "create"
        ):
            response_rule = get_matching_response_rule(endpoint_config, request_body)
            if response_rule is None:
                return JSONResponse(
                    status_code=400, content={"error": "No matching response condition found"}
                )

            response_data = response_rule.get("response", {})
            status_code = response_data.get("status_code", 201)
            request_context = extract_request_context(request, auth_config)
            response_body = process_response_body(
                response_data.get("body", {}), auth_config, request_context
            )
            headers = process_response_headers(response_data.get("headers", {}), auth_config)

            if status_code >= 400:
                return JSONResponse(status_code=status_code, content=response_body, headers=headers)

            try:
                if isinstance(response_body, dict):
                    entity_id = str(uuid.uuid4())
                    response_body.update({"id": entity_id, **request_body})
                    entity_to_store = (
                        response_body
                        if persistence_config.get("store_response_body", False)
                        else request_body
                    )
                    store_entity(entity_name, entity_to_store, entity_id=entity_id)
                    return JSONResponse(
                        status_code=status_code, content=response_body, headers=headers
                    )

                entity_id = store_entity(entity_name, request_body)
                return JSONResponse(status_code=status_code, content=response_body, headers=headers)
                # Fallback if no response config found
                return JSONResponse(
                    status_code=201,
                    content={"id": entity_id, "entity_type": entity_name, **request_body},
                )
            except HTTPException as e:
                return JSONResponse(status_code=e.status_code, content={"error": e.detail})

        elif (
            request.method in ["PUT", "PATCH"]
            and entity_name
            and persistence_config.get("action") == "update"
        ):
            # Handle update operations
            try:
                entity_id = store_entity(entity_name, request_body)
                # After successful persistence, use configured response
                for rule in endpoint_config.get("responses", []):
                    conditions = rule.get("body_conditions")
                    if conditions is None or check_conditions(request_body, conditions):
                        response_data = rule.get("response", {})
                        status_code = response_data.get("status_code", 200)
                        request_context = extract_request_context(request, auth_config)
                        response_body = process_response_body(
                            response_data.get("body", {}), auth_config, request_context
                        )
                        # Add the entity_id to the response
                        if isinstance(response_body, dict):
                            response_body.update({"id": entity_id, **request_body})
                        return JSONResponse(status_code=status_code, content=response_body)
                # Fallback if no response config found
                return JSONResponse(
                    status_code=200,
                    content={"id": entity_id, "entity_type": entity_name, **request_body},
                )
            except HTTPException as e:
                return JSONResponse(status_code=e.status_code, content={"error": e.detail})

        # Fall back to original static response handling
        for rule in endpoint_config.get("responses", []):
            conditions = rule.get("body_conditions")
            if conditions is None or check_conditions(request_body, conditions):
                response_data = rule["response"]
                headers = response_data.get("headers", {})
                return JSONResponse(
                    status_code=response_data["status_code"],
                    content=response_data["body"],
                    headers=headers,
                )

        # Default response if no conditions match
        return JSONResponse(
            status_code=400, content={"error": "No matching response condition found"}
        )

    # Build explicit parameters for FastAPI
    params = [
        inspect.Parameter("request", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Request)
    ]

    # Add path parameters first (no defaults)
    for param_name in path_param_names:
        params.append(
            inspect.Parameter(param_name, inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=str)
        )

    # Add body parameter last (has default) with the dynamic model
    params.append(
        inspect.Parameter(
            "body",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=request_model,
            default=Body(...),
        )
    )

    # Set the function signature (ignore typing errors)
    setattr(handler, "__signature__", inspect.Signature(params))  # type: ignore

    return handler


def create_handler(endpoint_config: dict[str, Any], auth_config: dict[str, Any]):
    """
    Factory function to create a request handler for a specific endpoint configuration.
    This closure ensures each created handler has its own isolated config.
    """
    # Dynamically build the handler signature to match path params
    path_param_names = []
    path = endpoint_config.get("path", "")
    # Extract path param names from the path string
    for part in path.split("/"):
        if part.startswith("{") and part.endswith("}"):
            path_param_names.append(part[1:-1])

    # Build the handler with explicit path params
    async def handler(request: Request, **path_params: Any) -> JSONResponse:
        # Clear auth resolution cache for this request cycle
        clear_auth_resolution_cache()

        # Check required headers first
        required_headers = endpoint_config.get("required_headers", {})
        header_error = check_required_headers(request, required_headers)
        if header_error:
            return header_error

        request_body = {}
        try:
            if request.method != "GET" and request.headers.get("content-length"):
                content_type = request.headers.get("content-type", "").lower()
                if "application/x-www-form-urlencoded" in content_type:
                    # Parse form data
                    form_data = await request.form()
                    request_body = dict(form_data)
                else:
                    # Parse JSON data
                    request_body = await request.json()
        except (json.JSONDecodeError, ValueError):
            return JSONResponse(status_code=400, content={"error": "Invalid request body format."})

        # Check for Redis persistence configuration
        persistence_config = endpoint_config.get("persistence", {})
        entity_name = persistence_config.get("entity_name")

        # Handle Redis operations based on method and configuration
        if (
            request.method == "POST"
            and entity_name
            and persistence_config.get("action") == "create"
        ):
            try:
                entity_id = store_entity(entity_name, request_body)
                # Return the created entity with its ID
                response_body = {
                    "id": entity_id,
                    "entity_type": entity_name,
                    "created_at": datetime.utcnow().isoformat(),
                    **request_body,
                }
                return JSONResponse(status_code=201, content=response_body)
            except HTTPException as e:
                return JSONResponse(status_code=e.status_code, content={"error": e.detail})

        elif (
            request.method == "GET"
            and entity_name
            and persistence_config.get("action") == "retrieve"
        ):
            # Extract entity ID from path parameters based on endpoint pattern
            entity_id = None
            path = endpoint_config.get("path", "")

            # Use configured id_path_param if available
            id_path_param = persistence_config.get("id_path_param")
            if id_path_param:
                entity_id = path_params.get(id_path_param)
            # Look for the ID parameter based on the endpoint pattern
            elif "{product_id}" in path:
                entity_id = path_params.get("product_id")
            elif "{customer_id}" in path:
                entity_id = path_params.get("customer_id")
            elif "{order_id}" in path:
                entity_id = path_params.get("order_id")
            elif "{item_id}" in path:
                entity_id = path_params.get("item_id")
            else:
                # Fallback to generic patterns
                entity_id = path_params.get("id") or path_params.get("entity_id")

            if entity_id:
                entity = get_entity(entity_name, entity_id)
                if entity:
                    # Return the actual stored entity data
                    entity_data = extract_persisted_entity_data(entity)
                    return JSONResponse(status_code=200, content=entity_data)
                else:
                    # Use configured fallback response if available
                    response_rule = get_matching_response_rule(endpoint_config, {})
                    if response_rule:
                        response_data = response_rule["response"]
                        request_context = extract_request_context(request, auth_config)
                        processed_body = process_response_body(
                            response_data.get("body", {}), auth_config, request_context
                        )
                        headers = process_response_headers(
                            response_data.get("headers", {}), auth_config
                        )
                        return JSONResponse(
                            status_code=response_data.get("status_code", 404),
                            content=processed_body,
                            headers=headers,
                        )
                    return JSONResponse(
                        status_code=404,
                        content={"error": f"{entity_name.title()} not found", "id": entity_id},
                    )
            else:
                return JSONResponse(status_code=400, content={"error": "Missing entity ID in path"})

        elif request.method == "GET" and entity_name and persistence_config.get("action") == "list":
            entities = list_entities(entity_name)

            # Filter entities by query parameters if configured
            filter_params = persistence_config.get("filter_by_query_params", [])
            if filter_params:
                query_params = dict(request.query_params)
                for param_name in filter_params:
                    param_value = query_params.get(param_name)
                    if param_value:
                        entities = [
                            entity
                            for entity in entities
                            if extract_persisted_entity_data(entity).get(param_name) == param_value
                        ]

            return build_persistence_list_response(request, endpoint_config, auth_config, entities)

        # Fall back to original static response handling
        for rule in endpoint_config.get("responses", []):
            conditions = rule.get("body_conditions")

            if conditions is None or check_conditions(request_body, conditions):
                response_data = rule["response"]
                status_code = response_data.get("status_code", 200)
                body = response_data.get("body", {})
                headers = process_response_headers(response_data.get("headers", {}), auth_config)
                # Process response body with auth placeholders
                request_context = extract_request_context(request, auth_config)
                processed_body = process_response_body(body, auth_config, request_context)

                body_str = json.dumps(processed_body)
                # Substitute all path params
                for key in path_param_names:
                    if key in path_params:
                        body_str = body_str.replace(f"{{{key}}}", str(path_params[key]))

                return JSONResponse(
                    status_code=status_code, content=json.loads(body_str), headers=headers
                )

        return JSONResponse(
            status_code=500,
            content={
                "error": "Server Configuration Error",
                "detail": "No matching response rule found.",
            },
        )

    # Set correct signature for FastAPI to recognize path params
    params = [
        inspect.Parameter("request", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Request)
    ]
    for name in path_param_names:
        params.append(inspect.Parameter(name, inspect.Parameter.KEYWORD_ONLY, annotation=str))
    # Note: Setting __signature__ is handled at runtime by FastAPI
    setattr(handler, "__signature__", inspect.Signature(params))
    return handler


def create_form_handler(
    endpoint_config: dict[str, Any], endpoint_path: str, auth_config: dict[str, Any]
):
    """Create a special form handler for form-encoded endpoints."""
    from typing import Annotated

    from fastapi import Form

    async def form_handler(
        request: Request,
        j_username: Annotated[str, Form(description="Username for authentication")],
        j_password: Annotated[str, Form(description="Password for authentication")],
    ):
        # Clear auth resolution cache for this request cycle
        clear_auth_resolution_cache()

        logging.info(f"Form handler called for {endpoint_path} with username: {j_username}")
        # Create a mock request object with form data
        form_data = {"j_username": j_username, "j_password": j_password}

        # Check conditions against form data
        for rule in endpoint_config.get("responses", []):
            conditions = rule.get("body_conditions")

            if conditions is None or check_conditions(form_data, conditions):
                response_data = rule["response"]
                status_code = response_data.get("status_code", 200)
                # Extract request context for session-aware placeholders
                request_context = extract_request_context(request, auth_config)
                body = process_response_body(
                    response_data.get("body", {}), auth_config, request_context
                )
                headers = process_response_headers(response_data.get("headers", {}), auth_config)

                logging.info(f"Form handler returning {status_code} for {endpoint_path}")
                return JSONResponse(status_code=status_code, content=body, headers=headers)

        # Default error response
        logging.error(f"No matching response rule for {endpoint_path} with data: {form_data}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Server Configuration Error",
                "detail": "No matching response rule found.",
            },
        )

    return form_handler
