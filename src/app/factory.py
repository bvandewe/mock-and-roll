"""
FastAPI application setup and OpenAPI customization.
"""

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from config.loader import load_api_config


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Load API configuration first to set FastAPI attributes
    api_config = load_api_config()

    # Configure FastAPI app with settings from api.json
    app_kwargs = {
        "title": api_config.get("api_name", "Mock API Server"),
        "description": api_config.get("description", "A configurable mock API server"),
        "version": api_config.get("version", "0.1.0"),
    }

    # Add additional OpenAPI configuration if present
    if "support" in api_config:
        support_info = api_config["support"]
        contact = {}
        if "email" in support_info:
            contact["email"] = support_info["email"]
        if "phone" in support_info:
            contact["name"] = f"Support ({support_info['phone']})"
        if contact:
            app_kwargs["contact"] = contact

    # Add terms of service and license if present
    if "terms_of_service" in api_config:
        app_kwargs["terms_of_service"] = api_config["terms_of_service"]

    if "license" in api_config:
        license_info = api_config["license"]
        if isinstance(license_info, dict):
            app_kwargs["license_info"] = license_info
        elif isinstance(license_info, str):
            app_kwargs["license_info"] = {"name": license_info}

    if "root_path" in api_config:
        app_kwargs["root_path"] = api_config["root_path"]

    # Add tag metadata if present
    if "openapi_tags" in api_config:
        app_kwargs["openapi_tags"] = api_config["openapi_tags"]

    # Add server information if base_url is provided
    servers = []
    if "base_url" in api_config:
        servers.append({"url": api_config["base_url"], "description": "Production server"})
    if servers:
        app_kwargs["servers"] = servers

    app = FastAPI(**app_kwargs)

    # Configure Swagger UI to collapse all tags by default
    from fastapi import Request
    from fastapi.openapi.docs import get_swagger_ui_html
    from fastapi.responses import HTMLResponse

    # Get Swagger UI configuration from api config
    swagger_config = api_config.get("swagger_ui", {})

    async def custom_swagger_ui_html(req: Request) -> HTMLResponse:
        # Default Swagger UI parameters that collapse all sections
        default_params = {
            "docExpansion": "none",  # Collapse all sections by default
            "defaultModelsExpandDepth": -1,  # Don't expand models
            "defaultModelExpandDepth": -1,  # Don't expand model details
            "displayRequestDuration": True,  # Show request duration
            "tryItOutEnabled": True,  # Enable try it out by default
        }

        # Override with configured values
        swagger_params = {}
        swagger_params["docExpansion"] = swagger_config.get("doc_expansion", default_params["docExpansion"])
        swagger_params["defaultModelsExpandDepth"] = swagger_config.get("default_models_expand_depth", default_params["defaultModelsExpandDepth"])
        swagger_params["defaultModelExpandDepth"] = swagger_config.get("default_model_expand_depth", default_params["defaultModelExpandDepth"])
        swagger_params["displayRequestDuration"] = swagger_config.get("display_request_duration", default_params["displayRequestDuration"])
        swagger_params["tryItOutEnabled"] = swagger_config.get("try_it_out_enabled", default_params["tryItOutEnabled"])

        return get_swagger_ui_html(openapi_url=app.openapi_url or "/openapi.json", title=app.title + " - Swagger UI", swagger_ui_parameters=swagger_params)

    # Override the default docs endpoint
    app.get("/docs", include_in_schema=False)(custom_swagger_ui_html)

    # Add request/response logging middleware if enabled
    logging_config = api_config.get("logging", {})
    if logging_config.get("request_response_logging", True):
        from middleware.logging_middleware import RequestResponseLoggingMiddleware

        # Configure middleware with body size limit from config
        max_body_size = logging_config.get("max_body_log_size", 2048)
        app.add_middleware(RequestResponseLoggingMiddleware, max_body_size=max_body_size)

    # Add system authentication middleware if enabled
    system_config = api_config.get("system", {})
    if system_config.get("protect_endpoints", False):
        from config.loader import load_auth_config
        from middleware.system_auth import SystemAuthMiddleware

        # Load auth configuration
        auth_config = load_auth_config()
        app.add_middleware(SystemAuthMiddleware, api_config=api_config, auth_config=auth_config)

    # Set up custom OpenAPI schema
    app.openapi = lambda: custom_openapi(app, api_config)

    return app


def custom_openapi(app: FastAPI, api_config: dict[str, Any]):
    """Custom OpenAPI schema to fix security schemes."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        terms_of_service=app.terms_of_service,
        license_info=app.license_info,
        contact=app.contact,
        tags=app.openapi_tags,
    )

    # Customize security schemes with proper names
    openapi_schema["components"]["securitySchemes"] = {
        "session_cookie": {"type": "apiKey", "in": "header", "name": "Cookie", "description": "Session cookie (e.g., JSESSIONID=session-id)"},
        "csrf_token": {"type": "apiKey", "in": "header", "name": "X-XSRF-TOKEN", "description": "CSRF Token"},
        "api_key": {"type": "apiKey", "in": "header", "name": "X-API-Key", "description": "API Key authentication"},
        "http_basic": {"type": "http", "scheme": "basic", "description": "HTTP Basic Authentication"},
        "http_bearer": {"type": "http", "scheme": "bearer", "description": "Bearer Token (OIDC)"},
        "system_api_key": {"type": "apiKey", "in": "header", "name": "X-API-Key", "description": "System API Key for admin endpoints"},
    }

    # Fix security requirements for endpoints based on their auth methods
    # This maps our custom auth methods to the correct OpenAPI security schemes
    auth_mapping = {"api_key": "api_key", "csrf_token": "csrf_token", "vmanage_session": "session_cookie", "basic_auth": "http_basic", "oidc_auth_code": "http_bearer", "oidc_client_credentials": "http_bearer", "system_api_key": "system_api_key"}

    # Load auth config and endpoints to map endpoints to their required auth methods
    from config.loader import load_auth_config, load_endpoints_config

    load_auth_config()  # Load for initialization
    config_data = load_endpoints_config()
    endpoints = config_data.get("endpoints", [])

    for endpoint_config in endpoints:
        path = endpoint_config.get("path")
        method = endpoint_config.get("method", "").lower()
        auth_methods = endpoint_config.get("authentication", [])

        if path in openapi_schema["paths"] and method in openapi_schema["paths"][path]:
            if auth_methods:
                security_requirements = []
                for auth_method in auth_methods:
                    if auth_method in auth_mapping:
                        security_scheme = auth_mapping[auth_method]
                        security_requirements.append({security_scheme: []})

                if security_requirements:
                    openapi_schema["paths"][path][method]["security"] = security_requirements

    # Fix security requirements for system endpoints
    # These endpoints should use the system_api_key security scheme
    for path in openapi_schema["paths"]:
        if path.startswith("/system/"):
            for method in openapi_schema["paths"][path]:
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    # Set system_api_key security for all system endpoints
                    openapi_schema["paths"][path][method]["security"] = [{"system_api_key": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema
