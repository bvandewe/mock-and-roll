#!/usr/bin/env python3
"""
Integration test script to verify system endpoints are protected by auth_data configuration.
Tests the actual running server at http://0.0.0.0:8000
"""

import json
import sys

import requests


def test_system_endpoints():
    """Test system endpoints with the running server."""

    base_url = "http://0.0.0.0:8000"

    # Valid API keys from auth.json
    valid_keys = ["system-admin-key-123", "sysadmin-secret-key-789", "admin-system-access-123"]

    # Invalid API keys for testing
    invalid_keys = ["invalid-key", "wrong-key-123", ""]

    # System endpoints to test
    system_endpoints = ["/system/logging/status", "/admin/cache/info"]  # Only available if Redis persistence is configured

    print("🚀 Testing System Endpoints Authentication")
    print(f"Server: {base_url}")
    print("=" * 60)

    # Test 1: Check server is running
    print("\n1. Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

    # Test 2: Test endpoints without authentication
    print("\n2. Testing endpoints without authentication (should fail)...")
    all_passed = True

    for endpoint in system_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 401:
                print(f"✅ {endpoint}: Correctly rejected (401 Unauthorized)")
            elif response.status_code == 404:
                print(f"⚠️  {endpoint}: Endpoint not found (404) - may not be configured")
            else:
                print(f"❌ {endpoint}: Expected 401, got {response.status_code}")
                print(f"   Response: {response.text[:100]}")
                all_passed = False
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: Request failed - {e}")
            all_passed = False

    # Test 3: Test endpoints with invalid API keys
    print("\n3. Testing endpoints with invalid API keys (should fail)...")

    for invalid_key in invalid_keys:
        headers = {"X-API-Key": invalid_key} if invalid_key else {}
        for endpoint in system_endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
                if response.status_code in [401, 403]:
                    print(f"✅ {endpoint} with key '{invalid_key}': Correctly rejected ({response.status_code})")
                elif response.status_code == 404:
                    print(f"⚠️  {endpoint} with key '{invalid_key}': Endpoint not found (404)")
                else:
                    print(f"❌ {endpoint} with key '{invalid_key}': Expected 401/403, got {response.status_code}")
                    all_passed = False
            except requests.exceptions.RequestException as e:
                print(f"❌ {endpoint}: Request failed - {e}")
                all_passed = False

    # Test 4: Test endpoints with valid API keys
    print("\n4. Testing endpoints with valid API keys (should succeed)...")

    for valid_key in valid_keys:
        headers = {"X-API-Key": valid_key}
        for endpoint in system_endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {endpoint} with key '{valid_key[:10]}...': Success (200)")
                    # Try to parse response as JSON
                    try:
                        data = response.json()
                        if "status" in data:
                            print(f"   Status: {data['status']}")
                    except json.JSONDecodeError:
                        print(f"   Response: {response.text[:100]}")
                elif response.status_code == 404:
                    print(f"⚠️  {endpoint} with key '{valid_key[:10]}...': Endpoint not found (404)")
                elif response.status_code == 503:
                    print(f"⚠️  {endpoint} with key '{valid_key[:10]}...': Service unavailable (503) - dependency issue")
                else:
                    print(f"❌ {endpoint} with key '{valid_key[:10]}...': Expected 200, got {response.status_code}")
                    print(f"   Response: {response.text[:100]}")
                    all_passed = False
            except requests.exceptions.RequestException as e:
                print(f"❌ {endpoint}: Request failed - {e}")
                all_passed = False

    # Test 5: Test the OpenAPI documentation includes system endpoints
    print("\n5. Testing OpenAPI documentation...")
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})

            system_paths_found = []
            for path in paths:
                if path.startswith("/system/") or path.startswith("/admin/"):
                    system_paths_found.append(path)

            if system_paths_found:
                print(f"✅ OpenAPI includes system endpoints: {system_paths_found}")

                # Check if security schemes are properly defined
                components = openapi_spec.get("components", {})
                security_schemes = components.get("securitySchemes", {})

                if security_schemes:
                    print(f"✅ Security schemes defined: {list(security_schemes.keys())}")
                else:
                    print("⚠️  No security schemes found in OpenAPI spec")
            else:
                print("⚠️  No system endpoints found in OpenAPI spec")
        else:
            print(f"❌ Failed to get OpenAPI spec: {response.status_code}")
            all_passed = False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get OpenAPI spec: {e}")
        all_passed = False

    print("\n" + "=" * 60)
    return all_passed


def test_auth_integration():
    """Test that system endpoints are using auth_data configuration."""

    print("\n🔐 Testing Authentication Integration")
    print("=" * 60)

    base_url = "http://0.0.0.0:8000"

    # Test with the specific system API key from auth.json
    system_key = "system-admin-key-123"
    headers = {"X-API-Key": system_key}

    print(f"\n6. Testing with system key from auth.json: {system_key}")

    # Test logging endpoint
    try:
        response = requests.get(f"{base_url}/system/logging/status", headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ Logging endpoint responds to auth_data configured key")
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
        else:
            print(f"❌ Logging endpoint failed: {response.status_code}")
            print(f"   Response: {response.text[:100]}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Logging endpoint request failed: {e}")
        return False

    # Test cache endpoint (if available)
    try:
        response = requests.get(f"{base_url}/admin/cache/info", headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ Cache endpoint responds to auth_data configured key")
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
        elif response.status_code == 404:
            print("⚠️  Cache endpoint not available (Redis may not be configured)")
        elif response.status_code == 503:
            print("⚠️  Cache endpoint service unavailable (Redis connection issue)")
        else:
            print(f"❌ Cache endpoint failed: {response.status_code}")
            print(f"   Response: {response.text[:100]}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cache endpoint request failed: {e}")
        return False

    return True


if __name__ == "__main__":
    print("🧪 System Endpoint Authentication Tests")
    print("Testing integration with auth_data configuration")
    print("Server: http://0.0.0.0:8000")

    # Run the tests
    basic_tests_passed = test_system_endpoints()
    integration_tests_passed = test_auth_integration()

    if basic_tests_passed and integration_tests_passed:
        print("\n🎉 All tests passed! System endpoints are properly protected by auth_data configuration.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Check the output above for details.")
        sys.exit(1)
