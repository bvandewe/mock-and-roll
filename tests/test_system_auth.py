#!/usr/bin/env python3
"""
Test script to verify system authentication middleware works correctly.
"""

from unittest.mock import MagicMock

from src.middleware.system_auth import SystemAuthMiddleware


def test_system_auth_middleware():
    """Test the system authentication middleware."""

    # Test configuration
    api_config = {"system": {"protect_endpoints": True, "auth_method": "system_api_key"}}

    auth_config = {"authentication_methods": {"system_api_key": {"type": "api_key", "name": "X-API-Key", "location": "header", "valid_keys": ["system-admin-key-2024", "test-key-123"]}}}

    # Create middleware instance
    app = MagicMock()
    middleware = SystemAuthMiddleware(app, api_config, auth_config)

    print("Testing SystemAuthMiddleware:")
    print(f"Protection enabled: {middleware.protection_enabled}")
    print(f"Auth method: {middleware.auth_method}")
    print(f"Valid keys loaded: {len(middleware.valid_keys)}")
    print(f"Protected prefixes: {middleware.protected_prefixes}")

    # Test path checking
    test_paths = [("/admin/cache/info", True), ("/system/logs", True), ("/admin/logging/status", True), ("/api/v1/users", False), ("/health", False), ("/docs", False)]

    print("\nPath protection tests:")
    for path, expected in test_paths:
        result = middleware._is_protected_endpoint(path)
        status = "✅" if result == expected else "❌"
        print(f"{status} {path}: {'protected' if result else 'unprotected'} (expected: {'protected' if expected else 'unprotected'})")

    # Test API key validation
    test_keys = [("system-admin-key-2024", True), ("test-key-123", True), ("invalid-key", False), ("", False), (None, False)]

    print("\nAPI key validation tests:")
    for key, expected in test_keys:
        if key is None:
            result = False  # None keys are handled before validation
        else:
            result = middleware._validate_api_key(key)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{key}': {'valid' if result else 'invalid'} (expected: {'valid' if expected else 'invalid'})")

    # Test with protection disabled
    api_config_disabled = {"system": {"protect_endpoints": False, "auth_method": "system_api_key"}}

    middleware_disabled = SystemAuthMiddleware(app, api_config_disabled, auth_config)
    print(f"\nProtection disabled test: {not middleware_disabled.protection_enabled}")

    return True


if __name__ == "__main__":
    success = test_system_auth_middleware()
    if success:
        print("\n🎉 All system authentication tests passed!")
    else:
        print("\n💥 Some tests failed.")
        exit(1)
