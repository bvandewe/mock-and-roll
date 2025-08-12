import json
import logging
import os
import base64
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Type

from fastapi import FastAPI, Request, HTTPException, Depends, Security, Body
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field, create_model
import redis
from redis.exceptions import ConnectionError as RedisConnectionError

# --- Basic Setup ---
logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Mock API Server", description="A configurable mock API server with authentication support", version="1.0.0")

# Add security schemes for Swagger UI
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
security_basic = HTTPBasic(auto_error=False)
security_bearer = HTTPBearer(auto_error=False)

# Global auth config (will be loaded on startup)
global_auth_config = {}

# Redis connection
redis_client = None


def get_redis_client():
    """Get Redis client with connection handling."""
    global redis_client
    if redis_client is None:
        try:
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", "6379"))
            redis_db = int(os.getenv("REDIS_DB", "0"))
            redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
            # Test connection
            redis_client.ping()
            logging.info(f"Connected to Redis at {redis_host}:{redis_port}")
        except RedisConnectionError:
            logging.warning("Redis connection failed. Persistence features disabled.")
            redis_client = None
    return redis_client


def store_entity(entity_name: str, data: Dict[str, Any]) -> str:
    """Store entity in Redis and return the generated key."""
    redis_conn = get_redis_client()
    if not redis_conn:
        raise HTTPException(status_code=503, detail="Redis not available")

    entity_id = str(uuid.uuid4())
    key = f"{entity_name}.{entity_id}"

    # Add metadata
    entity_data = {"id": entity_id, "entity_type": entity_name, "created_at": datetime.utcnow().isoformat(), "data": data}

    try:
        redis_conn.setex(key, 3600, json.dumps(entity_data))  # 1 hour TTL
        logging.info(f"Stored entity: {key}")
        return entity_id
    except Exception as e:
        logging.error(f"Failed to store entity: {e}")
        raise HTTPException(status_code=500, detail="Failed to store entity")


def get_entity(entity_name: str, entity_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve entity from Redis."""
    redis_conn = get_redis_client()
    if not redis_conn:
        return None

    key = f"{entity_name}.{entity_id}"
    try:
        data = redis_conn.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        logging.error(f"Failed to retrieve entity {key}: {e}")
        return None


def list_entities(entity_name: str) -> List[Dict[str, Any]]:
    """List all entities of a given type."""
    redis_conn = get_redis_client()
    if not redis_conn:
        return []

    pattern = f"{entity_name}.*"
    try:
        keys = redis_conn.keys(pattern)
        entities = []
        for key in keys:
            data = redis_conn.get(key)
            if data:
                entity = json.loads(data)
                entities.append(entity)
        return entities
    except Exception as e:
        logging.error(f"Failed to list entities for {entity_name}: {e}")
        return []


def flush_cache() -> bool:
    """Flush all cache data."""
    redis_conn = get_redis_client()
    if not redis_conn:
        return False

    try:
        redis_conn.flushdb()
        logging.info("Redis cache flushed")
        return True
    except Exception as e:
        logging.error(f"Failed to flush cache: {e}")
        return False


def get_cache_info() -> Dict[str, Any]:
    """Get Redis cache information."""
    redis_conn = get_redis_client()
    if not redis_conn:
        return {"status": "disconnected", "keys": 0}

    try:
        info = redis_conn.info()
        keys = redis_conn.dbsize()
        return {"status": "connected", "keys": keys, "memory_used": info.get("used_memory_human", "N/A"), "connected_clients": info.get("connected_clients", 0), "uptime": info.get("uptime_in_seconds", 0)}
    except Exception as e:
        logging.error(f"Failed to get cache info: {e}")
        return {"status": "error", "error": str(e)}


async def get_api_key(api_key: str = Security(api_key_header)):
    """Dependency for API key authentication."""
    if api_key is None:
        raise HTTPException(status_code=401, detail="API Key required")

    api_key_config = global_auth_config.get("authentication_methods", {}).get("api_key", {})
    valid_keys = api_key_config.get("valid_keys", [])

    if api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key


async def get_basic_auth(credentials: HTTPBasicCredentials = Security(security_basic)):
    """Dependency for HTTP Basic authentication."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Basic authentication required")

    basic_config = global_auth_config.get("authentication_methods", {}).get("basic_auth", {})
    valid_credentials = basic_config.get("valid_credentials", [])

    for cred in valid_credentials:
        if cred.get("username") == credentials.username and cred.get("password") == credentials.password:
            return credentials.username

    raise HTTPException(status_code=401, detail="Invalid credentials")


async def get_bearer_token(credentials: HTTPAuthorizationCredentials = Security(security_bearer)):
    """Dependency for Bearer token authentication."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Bearer token required")

    # Check both OIDC configurations for valid tokens
    for auth_method in ["oidc_auth_code", "oidc_client_credentials"]:
        oidc_config = global_auth_config.get("authentication_methods", {}).get(auth_method, {})
        valid_tokens = oidc_config.get("valid_tokens", [])

        for valid_token in valid_tokens:
            if valid_token.get("access_token") == credentials.credentials:
                return credentials.credentials

    raise HTTPException(status_code=401, detail="Invalid bearer token")


def load_config() -> Dict[str, List[Dict[str, Any]]]:
    """Loads the mock configuration from endpoints.json in the config directory."""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "endpoints.json")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file not found at '{config_path}'")
        return {"endpoints": []}
    except json.JSONDecodeError:
        logging.error(f"Could not decode JSON from '{config_path}'")
        return {"endpoints": []}


def load_auth_config() -> Dict[str, Any]:
    """Loads the authentication configuration from auth.json in the config directory."""
    auth_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "auth.json")
    try:
        with open(auth_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"Authentication file not found at '{auth_path}'. Authentication disabled.")
        return {"authentication_methods": {}}
    except json.JSONDecodeError:
        logging.error(f"Could not decode JSON from '{auth_path}'")
        return {"authentication_methods": {}}


def check_conditions(body: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
    """Checks if the request body satisfies all conditions."""
    if not conditions:
        return False

    for key, expected_value in conditions.items():
        if body.get(key) != expected_value:
            return False
    return True


def get_security_dependencies(auth_methods: List[str]):
    """Returns the appropriate security dependencies for the given auth methods."""
    if not auth_methods:
        return None

    # Create a custom dependency that handles multiple auth types
    async def verify_auth(request: Request, api_key: Optional[str] = Security(api_key_header), credentials: Optional[HTTPBasicCredentials] = Security(security_basic), bearer: Optional[HTTPAuthorizationCredentials] = Security(security_bearer)):
        # Try each authentication method
        auth_errors = []

        # Try API Key if required
        if "api_key" in auth_methods and api_key:
            api_key_config = global_auth_config.get("authentication_methods", {}).get("api_key", {})
            valid_keys = api_key_config.get("valid_keys", [])
            if api_key in valid_keys:
                return {"type": "api_key", "value": api_key}
            auth_errors.append("Invalid API key")

        # Try Basic Auth if required
        if "basic_auth" in auth_methods and credentials:
            basic_config = global_auth_config.get("authentication_methods", {}).get("basic_auth", {})
            valid_credentials = basic_config.get("valid_credentials", [])
            for cred in valid_credentials:
                if cred.get("username") == credentials.username and cred.get("password") == credentials.password:
                    return {"type": "basic", "value": credentials.username}
            auth_errors.append("Invalid credentials")

        # Try Bearer Token if required
        if any(method in auth_methods for method in ["oidc_auth_code", "oidc_client_credentials"]) and bearer:
            for auth_method in ["oidc_auth_code", "oidc_client_credentials"]:
                if auth_method in auth_methods:
                    oidc_config = global_auth_config.get("authentication_methods", {}).get(auth_method, {})
                    valid_tokens = oidc_config.get("valid_tokens", [])
                    for valid_token in valid_tokens:
                        if valid_token.get("access_token") == bearer.credentials:
                            return {"type": "bearer", "value": bearer.credentials}
            auth_errors.append("Invalid bearer token")

        # If we get here, no authentication method worked
        raise HTTPException(status_code=401, detail=f"Authentication failed. Required methods: {', '.join(auth_methods)}. Errors: {'; '.join(auth_errors)}")

    return [Depends(verify_auth)]


# Generic request body models
class ProductRequest(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None


class OrderRequest(BaseModel):
    product_id: Optional[str] = None
    quantity: Optional[int] = None
    priority: Optional[str] = None
    customer_id: Optional[str] = None


class CustomerRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


def needs_request_body(endpoint_config: Dict[str, Any]) -> bool:
    """Determine if endpoint needs a request body for Swagger UI."""
    method = endpoint_config.get("method", "").upper()
    persistence = endpoint_config.get("persistence", {})

    # POST/PUT/PATCH methods with create/update actions need request bodies
    if method in ["POST", "PUT", "PATCH"]:
        action = persistence.get("action")
        if action in ["create", "update"]:
            return True

    # Also check if any response has body_conditions (indicating expected request body)
    responses = endpoint_config.get("responses", [])
    for response in responses:
        if response.get("body_conditions"):
            return True

    return False


def get_request_body_model(endpoint_config: Dict[str, Any]) -> type:
    """Get appropriate request body model based on endpoint configuration."""
    entity_name = endpoint_config.get("persistence", {}).get("entity_name", "").lower()

    if "product" in entity_name:
        return ProductRequest
    elif "order" in entity_name:
        return OrderRequest
    elif "customer" in entity_name:
        return CustomerRequest
    else:
        # Generic model for other entities
        class GenericRequest(BaseModel):
            name: Optional[str] = None
            value: Optional[Any] = None
            data: Optional[Dict[str, Any]] = None

        return GenericRequest


def create_dynamic_model_from_schema(schema: Dict[str, Any], model_name: str = "DynamicRequest") -> Type[BaseModel]:
    """Create a dynamic Pydantic model from a JSON schema."""
    if not schema or schema.get("type") != "object":
        # Fallback to generic model
        return create_model(model_name, __base__=BaseModel)

    properties = schema.get("properties", {})
    required_fields = set(schema.get("required", []))

    # Convert JSON schema types to Python types
    type_mapping = {"string": str, "integer": int, "number": float, "boolean": bool, "array": List[Any], "object": Dict[str, Any]}

    field_definitions = {}

    for field_name, field_schema in properties.items():
        field_type = type_mapping.get(field_schema.get("type", "string"), str)

        # Handle enum values
        if "enum" in field_schema:
            # Create a union type for enum values
            from enum import Enum

            enum_class = Enum(f"{field_name.title()}Enum", {v: v for v in field_schema["enum"]})
            field_type = enum_class

        # Handle object types (nested objects)
        elif field_schema.get("type") == "object" and "properties" in field_schema:
            field_type = Dict[str, Any]  # Keep as dict for now, could make recursive

        # Set default value and make optional if not required
        if field_name in required_fields:
            default_value = ...  # Required field
        else:
            default_value = None
            field_type = Optional[field_type]

        # Create Field with description and example if available
        field_kwargs = {}
        if "description" in field_schema:
            field_kwargs["description"] = field_schema["description"]
        if "example" in field_schema:
            field_kwargs["example"] = field_schema["example"]
        if "minimum" in field_schema:
            field_kwargs["ge"] = field_schema["minimum"]
        if "maximum" in field_schema:
            field_kwargs["le"] = field_schema["maximum"]

        if field_kwargs:
            field_definitions[field_name] = (field_type, Field(default=default_value, **field_kwargs))
        else:
            field_definitions[field_name] = (field_type, default_value)

    # Create the dynamic model
    return create_model(model_name, **field_definitions)


def process_response_body(body: Any) -> Any:
    """Process response body to replace template variables."""
    if isinstance(body, dict):
        processed = {}
        for key, value in body.items():
            processed[key] = process_response_body(value)
        return processed
    elif isinstance(body, list):
        return [process_response_body(item) for item in body]
    elif isinstance(body, str):
        # Replace template variables
        if body == "{{random_uuid}}":
            return str(uuid.uuid4())
        elif body == "{{current_timestamp}}":
            return datetime.utcnow().isoformat() + "Z"
        else:
            # Handle path parameter substitution like {product_id}
            import re

            return re.sub(r"\{(\w+)\}", lambda m: f"path_param_{m.group(1)}", body)
    else:
        return body


def create_request_model(endpoint_config: Dict[str, Any]) -> Type[BaseModel]:
    """Create a request model based on endpoint configuration."""
    request_body_schema = endpoint_config.get("request_body_schema")

    if request_body_schema:
        # Use the detailed schema to create a proper model
        method = endpoint_config.get("method", "").lower()
        endpoint_path = endpoint_config.get("path", "").replace("/", "_").replace("{", "").replace("}", "")
        model_name = f"RequestModel{method.title()}{endpoint_path.title()}"
        return create_dynamic_model_from_schema(request_body_schema, model_name)
    else:
        # Fallback to a generic model
        return create_model("GenericRequest", name=(Optional[str], None), value=(Optional[Any], None), data=(Optional[Dict[str, Any]], None))


def create_handler_with_body(endpoint_config: Dict[str, Any]):
    """Create a handler that accepts a request body for POST/PUT endpoints."""
    import inspect

    # Create the request model from schema
    request_model = create_request_model(endpoint_config)

    # Extract path parameter names from the path string
    path_param_names = []
    path = endpoint_config.get("path", "")
    for part in path.split("/"):
        if part.startswith("{") and part.endswith("}"):
            path_param_names.append(part[1:-1])

    async def handler(request: Request, **kwargs) -> JSONResponse:
        # Extract body and path parameters from kwargs
        body = kwargs.pop("body", {})
        path_params = kwargs  # Remaining kwargs are path parameters

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
        if request.method == "POST" and entity_name and persistence_config.get("action") == "create":
            try:
                entity_id = store_entity(entity_name, request_body)
                # After successful persistence, use configured response
                for rule in endpoint_config.get("responses", []):
                    conditions = rule.get("body_conditions")
                    if conditions is None or all(request_body.get(k) == v for k, v in conditions.items()):
                        response_data = rule.get("response", {})
                        status_code = response_data.get("status_code", 201)
                        response_body = process_response_body(response_data.get("body", {}))
                        # Add the generated entity_id to the response
                        if isinstance(response_body, dict):
                            response_body.update({"id": entity_id, **request_body})
                        return JSONResponse(status_code=status_code, content=response_body)
                # Fallback if no response config found
                return JSONResponse(status_code=201, content={"id": entity_id, "entity_type": entity_name, **request_body})
            except HTTPException as e:
                return JSONResponse(status_code=e.status_code, content={"error": e.detail})

        elif request.method in ["PUT", "PATCH"] and entity_name and persistence_config.get("action") == "update":
            # Handle update operations
            try:
                entity_id = store_entity(entity_name, request_body)
                # After successful persistence, use configured response
                for rule in endpoint_config.get("responses", []):
                    conditions = rule.get("body_conditions")
                    if conditions is None or all(request_body.get(k) == v for k, v in conditions.items()):
                        response_data = rule.get("response", {})
                        status_code = response_data.get("status_code", 200)
                        response_body = process_response_body(response_data.get("body", {}))
                        # Add the entity_id to the response
                        if isinstance(response_body, dict):
                            response_body.update({"id": entity_id, **request_body})
                        return JSONResponse(status_code=status_code, content=response_body)
                # Fallback if no response config found
                return JSONResponse(status_code=200, content={"id": entity_id, "entity_type": entity_name, **request_body})
            except HTTPException as e:
                return JSONResponse(status_code=e.status_code, content={"error": e.detail})

        # Fall back to original static response handling
        for rule in endpoint_config.get("responses", []):
            conditions = rule.get("body_conditions")
            if conditions is None or all(request_body.get(k) == v for k, v in conditions.items()):
                return JSONResponse(status_code=rule["response"]["status_code"], content=rule["response"]["body"])

        # Default response if no conditions match
        return JSONResponse(status_code=400, content={"error": "No matching response condition found"})

    # Build explicit parameters for FastAPI
    params = [inspect.Parameter("request", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Request)]

    # Add path parameters first (no defaults)
    for param_name in path_param_names:
        params.append(inspect.Parameter(param_name, inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=str))

    # Add body parameter last (has default) with the dynamic model
    params.append(inspect.Parameter("body", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=request_model, default=Body(...)))

    # Set the function signature (ignore typing errors)
    handler.__signature__ = inspect.Signature(params)  # type: ignore

    return handler


def create_handler(endpoint_config: Dict[str, Any]):
    """
    Factory function to create a request handler for a specific endpoint configuration.
    This closure ensures each created handler has its own isolated config.
    """
    # Dynamically build the handler signature to match path params
    import inspect

    path_param_names = []
    path = endpoint_config.get("path", "")
    # Extract path param names from the path string
    for part in path.split("/"):
        if part.startswith("{") and part.endswith("}"):
            path_param_names.append(part[1:-1])

    # Build the handler with explicit path params
    async def handler(request: Request, **path_params: Any) -> JSONResponse:
        request_body = {}
        try:
            if request.method != "GET" and request.headers.get("content-length"):
                request_body = await request.json()
        except json.JSONDecodeError:
            return JSONResponse(status_code=400, content={"error": "Invalid JSON in request body."})

        # Check for Redis persistence configuration
        persistence_config = endpoint_config.get("persistence", {})
        entity_name = persistence_config.get("entity_name")

        # Handle Redis operations based on method and configuration
        if request.method == "POST" and entity_name and persistence_config.get("action") == "create":
            try:
                entity_id = store_entity(entity_name, request_body)
                # Return the created entity with its ID
                response_body = {"id": entity_id, "entity_type": entity_name, "created_at": datetime.utcnow().isoformat(), **request_body}
                return JSONResponse(status_code=201, content=response_body)
            except HTTPException as e:
                return JSONResponse(status_code=e.status_code, content={"error": e.detail})

        elif request.method == "GET" and entity_name and persistence_config.get("action") == "retrieve":
            # Extract entity ID from path parameters based on endpoint pattern
            entity_id = None
            path = endpoint_config.get("path", "")

            # Look for the ID parameter based on the endpoint pattern
            if "{product_id}" in path:
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
                    return JSONResponse(status_code=200, content=entity)
                else:
                    return JSONResponse(status_code=404, content={"error": f"{entity_name.title()} not found", "id": entity_id})
            else:
                return JSONResponse(status_code=400, content={"error": "Missing entity ID in path"})

        elif request.method == "GET" and entity_name and persistence_config.get("action") == "list":
            entities = list_entities(entity_name)
            return JSONResponse(status_code=200, content={"entities": entities, "count": len(entities)})

        # Fall back to original static response handling
        for rule in endpoint_config.get("responses", []):
            conditions = rule.get("body_conditions")
            if conditions is None or check_conditions(request_body, conditions):
                response_data = rule["response"]
                status_code = response_data.get("status_code", 200)
                body = response_data.get("body", {})
                body_str = json.dumps(body)
                # Substitute all path params
                for key in path_param_names:
                    if key in path_params:
                        body_str = body_str.replace(f"{{{key}}}", str(path_params[key]))
                return JSONResponse(status_code=status_code, content=json.loads(body_str))

        return JSONResponse(status_code=500, content={"error": "Server Configuration Error", "detail": "No matching response rule found."})

    # Set correct signature for FastAPI to recognize path params
    params = [inspect.Parameter("request", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Request)]
    for name in path_param_names:
        params.append(inspect.Parameter(name, inspect.Parameter.KEYWORD_ONLY, annotation=str))
    handler.__signature__ = inspect.Signature(params)
    return handler


# --- Dynamic Route Creation ---


def setup_routes(app_instance: FastAPI, config: Dict[str, List[Dict[str, Any]]], auth_config: Dict[str, Any]):
    """Reads the config and dynamically adds routes to the FastAPI app."""
    global global_auth_config
    global_auth_config = auth_config

    endpoints = config.get("endpoints", [])
    if not endpoints:
        logging.warning("No endpoints found in configuration. The server will have no routes.")

    for endpoint_config in endpoints:
        try:
            path = endpoint_config["path"]
            method = endpoint_config["method"].upper()
            auth_methods = endpoint_config.get("authentication", [])

            # Choose the appropriate handler based on whether a request body is needed
            if needs_request_body(endpoint_config):
                handler_func = create_handler_with_body(endpoint_config)
            else:
                handler_func = create_handler(endpoint_config)

            # Get security dependencies if authentication is required
            dependencies = get_security_dependencies(auth_methods) if auth_methods else None

            app_instance.add_api_route(
                path,
                handler_func,
                methods=[method],
                dependencies=dependencies,
                # Define a unique name to avoid conflicts if paths/methods are reused
                name=f"{method.lower()}_{path.replace('/', '_').replace('{', '').replace('}', '')}",
            )
            logging.info(f"Successfully created route: {method} {path}")
        except KeyError as e:
            logging.error(f"Skipping invalid endpoint configuration. Missing key: {e}. Config: {endpoint_config}")


# --- Main Execution ---

config_data = load_config()
auth_data = load_auth_config()
setup_routes(app, config_data, auth_data)


# --- Redis Management Endpoints ---


@app.get("/admin/cache/info", tags=["Cache Management"])
async def get_cache_info_endpoint():
    """Get Redis cache information and statistics."""
    return get_cache_info()


@app.delete("/admin/cache/flush", tags=["Cache Management"])
async def flush_cache_endpoint():
    """Flush all data from Redis cache."""
    success = flush_cache()
    if success:
        return {"message": "Cache flushed successfully"}
    else:
        raise HTTPException(status_code=503, detail="Redis not available or flush failed")


@app.get("/admin/cache/entities/{entity_name}", tags=["Cache Management"])
async def list_cached_entities_endpoint(entity_name: str):
    """List all cached entities of a specific type."""
    entities = list_entities(entity_name)
    return {"entity_name": entity_name, "entities": entities, "count": len(entities)}


@app.get("/admin/cache/entities/{entity_name}/{entity_id}", tags=["Cache Management"])
async def get_cached_entity_endpoint(entity_name: str, entity_id: str):
    """Get a specific cached entity by name and ID."""
    entity = get_entity(entity_name, entity_id)
    if entity:
        return entity
    else:
        raise HTTPException(status_code=404, detail="Entity not found in cache")


@app.get("/", include_in_schema=False)
async def root():
    """A simple root endpoint to confirm the server is running."""
    return {"message": "Mock server is running. Check /docs for available endpoints."}
