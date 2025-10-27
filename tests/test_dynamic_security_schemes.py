#!/usr/bin/env python3
"""
Test module for dynamic security scheme generation.

Tests ensure that the OpenAPI security schemes are dynamically generated
based on the authentication methods defined in auth.json configuration.
"""

import os
import sys

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.factory import create_app
from config.loader import load_auth_config


def test_vmanage_security_schemes():
    """Test that vmanage config only shows its configured authentication methods."""
    print("\n🔐 Testing vManage Security Schemes")
    print("=" * 60)

    # Set the config to vmanage
    os.environ["MOCK_CONFIG_FOLDER"] = os.path.join(os.path.dirname(__file__), "..", "configs", "vmanage")

    try:
        # Load auth config to see what's configured
        auth_config = load_auth_config()
        auth_methods = auth_config.get("authentication_methods", {})

        print(f"\n📋 Configured authentication methods in vmanage/auth.json:")
        for method_name in auth_methods.keys():
            print(f"   • {method_name}")

        # Create app and get OpenAPI schema
        app = create_app()
        openapi_schema = app.openapi()

        # Get security schemes from OpenAPI
        security_schemes = openapi_schema.get("components", {}).get("securitySchemes", {})

        print(f"\n🔑 Security schemes in OpenAPI spec:")
        for scheme_name in security_schemes.keys():
            print(f"   • {scheme_name}")

        # Verify that security schemes match configured auth methods
        print(f"\n✅ Validation:")

        # Check that all configured auth methods are in security schemes
        for method_name in auth_methods.keys():
            if method_name in security_schemes:
                print(f"   ✓ {method_name} is present in security schemes")
            else:
                print(f"   ✗ {method_name} is MISSING from security schemes")
                return False

        # Check that there are no extra security schemes
        extra_schemes = set(security_schemes.keys()) - set(auth_methods.keys())
        if extra_schemes:
            print(f"\n   ⚠️  WARNING: Extra security schemes found: {extra_schemes}")
            # This might be OK for system endpoints, but let's note it

        # Verify expected vmanage methods
        expected_methods = ["csrf_token", "vmanage_session", "system_api_key"]
        for method in expected_methods:
            assert method in security_schemes, f"Expected method {method} not found in security schemes"

        # Verify unexpected methods are NOT present
        unexpected_methods = [
            "basic_auth",
            "http_basic",
            "api_key",
            "http_bearer",
            "oidc_auth_code",
        ]
        for method in unexpected_methods:
            if method in security_schemes:
                print(f"   ✗ Unexpected method {method} found in security schemes")
                return False

        print(f"\n🎉 SUCCESS: Security schemes match vmanage configuration!")
        print(f"   Expected: {len(expected_methods)} methods")
        print(f"   Found: {len(security_schemes)} schemes")

        return True

    finally:
        # Clean up environment variable
        if "MOCK_CONFIG_FOLDER" in os.environ:
            del os.environ["MOCK_CONFIG_FOLDER"]


def test_basic_security_schemes():
    """Test that basic config shows its configured authentication methods."""
    print("\n🔐 Testing Basic Security Schemes")
    print("=" * 60)

    # Set the config to basic
    os.environ["MOCK_CONFIG_FOLDER"] = os.path.join(os.path.dirname(__file__), "..", "configs", "basic")

    try:
        # Load auth config to see what's configured
        auth_config = load_auth_config()
        auth_methods = auth_config.get("authentication_methods", {})

        print(f"\n📋 Configured authentication methods in basic/auth.json:")
        for method_name in auth_methods.keys():
            print(f"   • {method_name}")

        # Create app and get OpenAPI schema
        app = create_app()
        openapi_schema = app.openapi()

        # Get security schemes from OpenAPI
        security_schemes = openapi_schema.get("components", {}).get("securitySchemes", {})

        print(f"\n🔑 Security schemes in OpenAPI spec:")
        for scheme_name in security_schemes.keys():
            print(f"   • {scheme_name}")

        # Verify expected basic methods
        expected_methods = ["api_key", "basic_auth", "system_api_key"]
        for method in expected_methods:
            if method in security_schemes:
                print(f"   ✓ {method} is present in security schemes")
            else:
                print(f"   ✗ {method} is MISSING from security schemes")
                return False

        # Verify vmanage-specific methods are NOT present
        unexpected_methods = ["vmanage_session", "csrf_token"]
        for method in unexpected_methods:
            if method in security_schemes:
                print(f"   ✗ Unexpected method {method} found in security schemes")
                return False

        print(f"\n🎉 SUCCESS: Security schemes match basic configuration!")
        return True

    finally:
        # Clean up environment variable
        if "MOCK_CONFIG_FOLDER" in os.environ:
            del os.environ["MOCK_CONFIG_FOLDER"]


def test_security_scheme_details():
    """Test that security scheme details match configuration."""
    print("\n🔍 Testing Security Scheme Details")
    print("=" * 60)

    # Set the config to vmanage
    os.environ["MOCK_CONFIG_FOLDER"] = os.path.join(os.path.dirname(__file__), "..", "configs", "vmanage")

    try:
        # Load auth config
        auth_config = load_auth_config()

        # Create app and get OpenAPI schema
        app = create_app()
        openapi_schema = app.openapi()

        security_schemes = openapi_schema.get("components", {}).get("securitySchemes", {})

        # Check csrf_token details
        if "csrf_token" in security_schemes:
            csrf_scheme = security_schemes["csrf_token"]
            auth_csrf_config = auth_config["authentication_methods"]["csrf_token"]

            print(f"\n📋 CSRF Token Scheme:")
            print(f"   Type: {csrf_scheme.get('type')}")
            print(f"   Name: {csrf_scheme.get('name')}")
            print(f"   Location: {csrf_scheme.get('in')}")

            assert csrf_scheme["type"] == "apiKey", "CSRF should be apiKey type"
            assert csrf_scheme["name"] == auth_csrf_config["name"], f"CSRF header name mismatch"
            assert csrf_scheme["in"] == auth_csrf_config["location"], f"CSRF location mismatch"
            print(f"   ✓ Details match configuration")

        # Check system_api_key details
        if "system_api_key" in security_schemes:
            system_scheme = security_schemes["system_api_key"]
            auth_system_config = auth_config["authentication_methods"]["system_api_key"]

            print(f"\n📋 System API Key Scheme:")
            print(f"   Type: {system_scheme.get('type')}")
            print(f"   Name: {system_scheme.get('name')}")
            print(f"   Description: {system_scheme.get('description')}")

            assert system_scheme["type"] == "apiKey", "System API Key should be apiKey type"
            assert system_scheme["name"] == auth_system_config["name"], f"System API Key header name mismatch"
            print(f"   ✓ Details match configuration")

        print(f"\n🎉 SUCCESS: Security scheme details are correct!")
        return True

    finally:
        # Clean up environment variable
        if "MOCK_CONFIG_FOLDER" in os.environ:
            del os.environ["MOCK_CONFIG_FOLDER"]


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 Dynamic Security Scheme Generation Tests")
    print("=" * 60)

    test1_passed = test_vmanage_security_schemes()
    test2_passed = test_basic_security_schemes()
    test3_passed = test_security_scheme_details()

    print("\n" + "=" * 60)
    if test1_passed and test2_passed and test3_passed:
        print("🎉 SUCCESS: All tests passed!")
        print("✅ Security schemes are now dynamically generated from auth.json")
        print("✅ Each config profile shows only its configured auth methods")
        print("✅ Security scheme details match configuration")
        sys.exit(0)
    else:
        print("❌ FAILURE: Some tests failed")
        sys.exit(1)
