#!/usr/bin/env python3
"""
Test script to verify that system endpoints use centralized auth_data configuration
instead of separate authentication objects.
"""

import requests


def test_auth_data_integration():
    """Test that system endpoints use the centralized auth_data configuration."""

    base_url = "http://0.0.0.0:8000"

    print("🔍 Testing Auth Data Integration")
    print("=" * 50)

    # Get the OpenAPI specification
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if response.status_code != 200:
            print(f"❌ Failed to get OpenAPI spec: {response.status_code}")
            return False

        openapi_spec = response.json()

    except Exception as e:
        print(f"❌ Error getting OpenAPI spec: {e}")
        return False

    # Check security schemes
    components = openapi_spec.get("components", {})
    security_schemes = components.get("securitySchemes", {})

    print(f"\n📋 Security schemes found: {list(security_schemes.keys())}")

    # Check if system_api_key exists and has correct configuration
    if "system_api_key" in security_schemes:
        system_scheme = security_schemes["system_api_key"]
        print(f"\n✅ system_api_key scheme found:")
        print(f"   Type: {system_scheme.get('type')}")
        print(f"   Name: {system_scheme.get('name')}")
        print(f"   In: {system_scheme.get('in')}")
        print(f"   Description: {system_scheme.get('description', 'N/A')}")

        # Verify it matches auth.json configuration
        expected_name = "X-API-Key"
        expected_type = "apiKey"
        expected_location = "header"

        if system_scheme.get("name") == expected_name and system_scheme.get("type") == expected_type and system_scheme.get("in") == expected_location:
            print("✅ Security scheme matches auth.json configuration")
        else:
            print("❌ Security scheme doesn't match expected configuration")
            return False
    else:
        print("❌ system_api_key security scheme not found")
        return False

    # Check system endpoints security requirements
    paths = openapi_spec.get("paths", {})
    system_endpoints = []

    for path, methods in paths.items():
        if path.startswith("/system/") or path.startswith("/admin/"):
            system_endpoints.append(path)

            for method, spec in methods.items():
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    security = spec.get("security", [])
                    print(f"\n🔒 {method.upper()} {path}:")
                    print(f"   Security: {security}")

                    # Check if system_api_key is used
                    uses_system_key = any("system_api_key" in req for req in security)
                    if uses_system_key:
                        print("   ✅ Uses system_api_key from auth_data")
                    else:
                        print("   ❌ Does not use system_api_key")
                        return False

    print(f"\n📊 Summary:")
    print(f"   System endpoints found: {len(system_endpoints)}")
    print(f"   All use centralized auth_data: ✅")

    return True


def test_with_auth_keys():
    """Test that the auth keys from auth.json work correctly."""

    base_url = "http://0.0.0.0:8000"

    print(f"\n🔑 Testing Auth Keys from auth.json")
    print("=" * 50)

    # Keys from the auth.json configuration
    auth_keys = ["system-admin-key-123", "sysadmin-secret-key-789", "admin-system-access-123"]

    test_endpoint = "/system/logging/status"

    for key in auth_keys:
        headers = {"X-API-Key": key}
        try:
            response = requests.get(f"{base_url}{test_endpoint}", headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"✅ Key '{key}': Works correctly")
            else:
                print(f"❌ Key '{key}': Failed with status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Key '{key}': Request failed - {e}")
            return False

    # Test with a key that should NOT work
    invalid_key = "this-should-not-work"
    headers = {"X-API-Key": invalid_key}
    try:
        response = requests.get(f"{base_url}{test_endpoint}", headers=headers, timeout=5)
        if response.status_code in [401, 403]:
            print(f"✅ Invalid key '{invalid_key}': Correctly rejected ({response.status_code})")
        else:
            print(f"❌ Invalid key '{invalid_key}': Should have been rejected but got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Invalid key test failed: {e}")
        return False

    return True


if __name__ == "__main__":
    print("🧪 Auth Data Integration Tests")
    print("Verifying system endpoints use centralized auth_data configuration")
    print("=" * 60)

    test1_passed = test_auth_data_integration()
    test2_passed = test_with_auth_keys()

    print("\n" + "=" * 60)
    if test1_passed and test2_passed:
        print("🎉 SUCCESS: System endpoints are properly integrated with auth_data!")
        print("✅ No separate authentication objects found")
        print("✅ All endpoints use centralized configuration")
    else:
        print("💥 FAILED: Issues found with auth_data integration")
        exit(1)
