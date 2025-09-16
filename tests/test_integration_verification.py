#!/usr/bin/env python3
"""
Test the updated system authentication integration without requiring a server restart.
"""

import os
import sys

# Ensure project root src directory on path BEFORE other imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from auth.security import create_system_auth_dependency
from auth.security import system_api_key as system_api_key_header  # noqa: E402
from config.loader import load_api_config, load_auth_config  # noqa: E402


def test_security_scheme_integration():
    """Test that the system auth dependency and API key config are consistent.

    The original test referenced a removed helper (configure_system_security_scheme). We now
    validate that the exported system API key model matches the configuration and that a
    dependency callable can be created for the configured auth method.
    """

    print("🔧 Testing Security Scheme Integration (updated)")
    print("=" * 50)

    # Load configurations
    auth_data = load_auth_config()
    api_config = load_api_config()

    system_config = api_config.get("system", {})
    auth_method = system_config.get("auth_method", "system_api_key")
    print(f"Auth method from config: {auth_method}")

    # Obtain system API key model (should be pre-configured at import time if applicable)
    system_api_key = system_api_key_header
    assert system_api_key, "System API key object not initialized"

    print(f"System API Key scheme name: {getattr(system_api_key.model, 'name', 'N/A')}")
    print(f"System API Key scheme description: {getattr(system_api_key.model, 'description', 'N/A')}")

    # Compare with configuration
    auth_methods = auth_data.get("authentication_methods", {})
    method_config = auth_methods.get(auth_method, {})
    expected_name = method_config.get("name", "X-API-Key")
    expected_description = method_config.get("description", "")

    assert getattr(system_api_key.model, "name", None) == expected_name, f"Security scheme name mismatch: got {getattr(system_api_key.model, 'name', None)}, expected {expected_name}"

    assert expected_description in getattr(system_api_key.model, "description", ""), f"Security scheme description mismatch: got '{getattr(system_api_key.model, 'description', '')}', expected to contain '{expected_description}'"

    # Validate dependency creation
    get_system_auth = create_system_auth_dependency(auth_data, auth_method)
    assert get_system_auth, "Failed to create system auth dependency"

    print("✅ All security scheme integration checks passed")
    # Success if assertions did not fail
    assert True


def test_configuration_loading():
    """Test that the configuration loading works correctly."""
    auth_data = load_auth_config()
    api_config = load_api_config()

    auth_methods = auth_data.get("authentication_methods", {})
    assert "system_api_key" in auth_methods, "system_api_key not found in auth configuration"
    system_auth_config = auth_methods["system_api_key"]
    print("✅ System API key config loaded:")
    print(f"   Type: {system_auth_config.get('type')}")
    print(f"   Name: {system_auth_config.get('name')}")
    print(f"   Location: {system_auth_config.get('location')}")
    print(f"   Valid keys: {len(system_auth_config.get('valid_keys', []))} keys")

    system_config = api_config.get("system", {})
    assert system_config, "System configuration not found in API config"
    print("✅ System config loaded:")
    print(f"   Protection enabled: {system_config.get('protect_endpoints')}")
    print(f"   Auth method: {system_config.get('auth_method')}")
    assert True
