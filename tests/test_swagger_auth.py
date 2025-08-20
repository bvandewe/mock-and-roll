#!/usr/bin/env python3
"""
Test to verify Swagger authentication setup for system endpoints.
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from app.factory import create_app
from config.loader import load_api_config, load_auth_config
from routes.cache_management import add_cache_management_endpoints
from routes.logging_management import add_logging_management_endpoints


def test_swagger_security_setup():
    """Test that the OpenAPI spec correctly sets up system endpoint security."""

    print("🔧 Testing Swagger Security Setup")
    print("=" * 50)

    # Create a test app with our configuration
    app = create_app()

    # Load configurations
    auth_data = load_auth_config()
    api_config = load_api_config()

    # Add system endpoints
    add_logging_management_endpoints(app, api_config, auth_data)

    if api_config.get("persistence") == "redis":
        add_cache_management_endpoints(app, api_config, auth_data)

    # Get the OpenAPI schema
    openapi_schema = app.openapi()

    # Check security schemes
    security_schemes = openapi_schema.get("components", {}).get("securitySchemes", {})

    print("📋 Security Schemes:")
    for scheme_name, scheme_config in security_schemes.items():
        print(f"   • {scheme_name}: {scheme_config.get('type')} - {scheme_config.get('description', 'No description')}")

    if "system_api_key" not in security_schemes:
        print("❌ system_api_key security scheme not found!")
        return False

    print("✅ system_api_key security scheme is properly defined")

    # Check system endpoints
    paths = openapi_schema.get("paths", {})
    system_endpoints = []

    for path in paths:
        if path.startswith("/system/") or path.startswith("/admin/"):
            system_endpoints.append(path)

    print(f"\n🔒 System Endpoints Found: {len(system_endpoints)}")

    all_correct = True
    for path in system_endpoints:
        path_config = paths[path]
        for method, method_config in path_config.items():
            if method.lower() in ["get", "post", "put", "delete", "patch"]:
                security = method_config.get("security", [])
                print(f"   {method.upper()} {path}")
                print(f"      Security: {security}")

                # Check if system_api_key is used
                uses_system_key = any("system_api_key" in req for req in security)
                if uses_system_key:
                    print("      ✅ Uses system_api_key")
                else:
                    print("      ❌ Does not use system_api_key")
                    all_correct = False

    return all_correct


def test_security_scheme_configuration():
    """Test that the security scheme has the correct configuration."""

    print("\n🔑 Testing Security Scheme Configuration")
    print("=" * 50)

    # Test the static security scheme
    from auth.security import system_api_key

    print(f"Security scheme name: {system_api_key.model.name}")
    print(f"Security scheme description: {system_api_key.model.description}")

    # Check if it matches expected values
    expected_name = "X-API-Key"
    if system_api_key.model.name == expected_name:
        print("✅ Security scheme name is correct")
    else:
        print(f"❌ Security scheme name mismatch: got {system_api_key.model.name}, expected {expected_name}")
        return False

    if "System API Key" in system_api_key.model.description:
        print("✅ Security scheme description is appropriate")
    else:
        print(f"❌ Security scheme description seems wrong: {system_api_key.model.description}")
        return False

    return True


if __name__ == "__main__":
    print("🧪 Swagger Authentication Setup Tests")
    print("=" * 60)

    test1_passed = test_security_scheme_configuration()
    test2_passed = test_swagger_security_setup()

    print("\n" + "=" * 60)
    if test1_passed and test2_passed:
        print("🎉 SUCCESS: Swagger authentication is properly configured!")
        print("✅ system_api_key security scheme is defined correctly")
        print("✅ System endpoints will use proper authentication in Swagger")
        print("✅ OpenAPI spec will show correct security requirements")
        print("\nNote: Server restart required to see changes in Swagger UI")
    else:
        print("💥 FAILED: Issues found with Swagger authentication setup")
        sys.exit(1)
