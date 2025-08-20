"""
Dynamic route setup for the mock API server.
"""

import logging
from typing import Any

from fastapi import FastAPI

from auth.security import get_security_dependencies
from handlers.routes import (
    create_form_handler,
    create_handler,
    create_handler_with_body,
)
from models.dynamic import needs_request_body


def setup_routes(app_instance: FastAPI, config: dict[str, Any], auth_config: dict[str, Any]):
    """Reads the config and dynamically adds routes to the FastAPI app."""
    endpoints = config.get("endpoints", [])
    if not endpoints:
        logging.warning("No endpoints found in configuration. The server will have no routes.")

    for endpoint_config in endpoints:
        try:
            path = endpoint_config["path"]
            method = endpoint_config["method"].upper()
            auth_methods = endpoint_config.get("authentication", [])

            # Special handling for form endpoints like j_security_check
            if endpoint_config.get("form_parameters"):
                logging.info(f"Creating form handler for {path}")

                # Capture variables to avoid closure issues
                current_path = path
                current_config = endpoint_config.copy()

                handler_func = create_form_handler(current_config, current_path, auth_config)
            # Choose the appropriate handler based on whether a request body is needed
            elif needs_request_body(endpoint_config):
                handler_func = create_handler_with_body(endpoint_config, auth_config)
            else:
                handler_func = create_handler(endpoint_config, auth_config)

            # Get security dependencies if authentication is required
            dependencies = get_security_dependencies(auth_methods, auth_config) if auth_methods else None

            # Extract tag configuration if provided
            tag_config = endpoint_config.get("tag")
            tags = None
            if tag_config:
                tags_list = []
                if isinstance(tag_config, dict):
                    # If tag is a dict, use it as a single tag object
                    tags_list.append(str(tag_config.get("name", "Default")))
                elif isinstance(tag_config, str):
                    # If tag is a string, use it as the tag name
                    tags_list.append(tag_config)
                elif isinstance(tag_config, list):
                    # If tag is a list, extract tag names from each item
                    for tag_item in tag_config:
                        if isinstance(tag_item, dict):
                            tags_list.append(str(tag_item.get("name", "Default")))
                        else:
                            tags_list.append(str(tag_item))
                tags = tags_list if tags_list else None

            app_instance.add_api_route(
                path,
                handler_func,
                methods=[method],
                dependencies=dependencies,
                tags=tags,
                # Define a unique name to avoid conflicts if paths/methods are reused
                name=f"{method.lower()}_{path.replace('/', '_').replace('{', '').replace('}', '')}",
            )
            logging.info(f"Successfully created route: {method} {path}")
        except KeyError as e:
            logging.error(f"Skipping invalid endpoint configuration. Missing key: {e}. Config: {endpoint_config}")
