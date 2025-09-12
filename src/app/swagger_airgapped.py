"""
Air-gapped Swagger UI implementation for offline environments.

This module provides functionality to serve Swagger UI assets locally
instead of relying on external CDNs, making it suitable for air-gapped
environments without internet access.
"""

import json
from pathlib import Path
from typing import Any

from fastapi.responses import HTMLResponse


def get_swagger_ui_html_airgapped(*, openapi_url: str, title: str, swagger_ui_parameters: dict[str, Any] = None, template_path: str = None) -> HTMLResponse:
    """Generate Swagger UI HTML for air-gapped environments.

    Args:
        openapi_url: URL to the OpenAPI JSON schema
        title: Title for the Swagger UI page
        swagger_ui_parameters: Configuration parameters for Swagger UI
        template_path: Optional custom template path

    Returns:
        HTML response with self-contained Swagger UI

    Example:
        response = get_swagger_ui_html_airgapped(
            openapi_url="/openapi.json",
            title="My API - Swagger UI",
            swagger_ui_parameters={
                "docExpansion": "none",
                "defaultModelsExpandDepth": -1
            }
        )
    """
    if swagger_ui_parameters is None:
        swagger_ui_parameters = {}

    # Default template path
    if template_path is None:
        current_dir = Path(__file__).parent.parent
        template_path = current_dir / "static" / "swagger-ui-template.html"
    else:
        template_path = Path(template_path)

    # Load template
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()
    except FileNotFoundError:
        # Fallback to inline template if file doesn't exist
        template_content = _get_fallback_template()

    # Format Swagger UI parameters as JavaScript object
    swagger_params_js = _format_swagger_parameters(swagger_ui_parameters)

    # Replace template variables
    html_content = template_content.replace("{{title}}", title)
    html_content = html_content.replace("{{openapi_url}}", openapi_url)
    html_content = html_content.replace("{{swagger_ui_parameters}}", swagger_params_js)

    return HTMLResponse(content=html_content)


def _format_swagger_parameters(params: dict[str, Any]) -> str:
    """Format Swagger UI parameters as JavaScript object properties.

    Args:
        params: Dictionary of Swagger UI configuration parameters

    Returns:
        JavaScript object properties as string
    """
    if not params:
        return ""

    js_properties = []
    for key, value in params.items():
        if isinstance(value, bool):
            js_value = "true" if value else "false"
        elif isinstance(value, str):
            js_value = json.dumps(value)
        elif isinstance(value, (int, float)):
            js_value = str(value)
        else:
            js_value = json.dumps(value)

        js_properties.append(f"{key}: {js_value}")

    return ",\n      ".join(js_properties) + ","


def _get_fallback_template() -> str:
    """Get fallback HTML template if external template file is not available.

    Returns:
        Complete HTML template as string
    """
    return """<!DOCTYPE html>
<html>
<head>
  <link type="text/css" rel="stylesheet" href="/static/swagger-ui/swagger-ui.css">
  <link rel="shortcut icon" href="data:image/x-icon;base64,AAABAAEAEBAAAAAAAABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAA">
  <title>{{title}}</title>
</head>

<body>
  <div id="swagger-ui">
  </div>

  <script src="/static/swagger-ui/swagger-ui-bundle.js"></script>
  <script src="/static/swagger-ui/swagger-ui-standalone-preset.js"></script>
  <script>
    const ui = SwaggerUIBundle({
      url: '{{openapi_url}}',
      dom_id: '#swagger-ui',
      layout: "StandaloneLayout",
      presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIStandalonePreset
      ],
      {{swagger_ui_parameters}}
      supportedSubmitMethods: ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace']
    });
  </script>
</body>
</html>"""


def check_airgapped_assets() -> bool:
    """Check if all required Swagger UI assets are available locally.

    Returns:
        True if all assets are present, False otherwise
    """
    current_dir = Path(__file__).parent.parent
    static_dir = current_dir / "static" / "swagger-ui"

    required_files = ["swagger-ui-bundle.js", "swagger-ui-standalone-preset.js", "swagger-ui.css"]

    for filename in required_files:
        if not (static_dir / filename).exists():
            return False

    return True
