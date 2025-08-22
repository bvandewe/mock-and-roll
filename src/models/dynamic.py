"""
Pydantic model creation utilities for dynamic request models.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, create_model


def needs_request_body(endpoint_config: dict[str, Any]) -> bool:
    """Determine if endpoint needs a request body for Swagger UI."""
    method = endpoint_config.get("method", "").upper()
    persistence = endpoint_config.get("persistence", {})

    # Check if this is a form-encoded endpoint
    request_headers = endpoint_config.get("request_headers", {})
    content_type = request_headers.get("Content-Type", "")
    if "application/x-www-form-urlencoded" in content_type:
        # Form endpoints don't need Pydantic request body models
        return False

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


def create_dynamic_model_from_schema(schema: dict[str, Any], model_name: str = "DynamicRequest") -> type[BaseModel]:
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


def create_request_model(endpoint_config: dict[str, Any]) -> type[BaseModel]:
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
