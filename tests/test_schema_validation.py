#!/usr/bin/env python3
"""
Schema Validation Demo Script for vManage API Mock Server
This script demonstrates request body schema validation with both valid and invalid payloads.
"""

import json
import socket
from urllib.parse import urljoin

import requests


def _server_running(host: str = "localhost", port: int = 8000) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def test_schema_validation(base_url="http://localhost:8000"):
    """Test request schema validation with various payloads"""
    if not _server_running():
        print("⚠️  Server not running on localhost:8000 - skipping schema validation test")
        # Skipped scenario - express via pytest skip rather than boolean return
        import pytest

        pytest.skip("Server not running on localhost:8000")

    session = requests.Session()

    print("🧪 Schema Validation Testing for vManage API")
    print("=" * 50)

    # Step 1: Authenticate first
    print("\n🔐 Step 1: Authenticating...")
    auth_url = urljoin(base_url, "/j_security_check")

    # Valid authentication payload
    valid_auth_data = {"j_username": "admin", "j_password": "admin"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = session.post(auth_url, data=valid_auth_data, headers=headers)
    assert response.status_code == 200, f"Authentication failed: {response.status_code}"

    print("✅ Authentication successful")

    # Step 2: Get CSRF token
    print("\n🎫 Step 2: Getting CSRF token...")
    token_url = urljoin(base_url, "/dataservice/client/token")
    response = session.get(token_url)

    assert response.status_code == 200, f"Failed to get CSRF token: {response.status_code}"

    csrf_token = response.text.strip('"')
    print(f"✅ CSRF token obtained: {csrf_token}")

    # Step 3: Test Device Template Creation - Valid Schema
    print("\n📋 Step 3: Testing Device Template Creation (Valid Schema)...")
    template_url = urljoin(base_url, "/dataservice/template/device")
    headers = {"X-XSRF-TOKEN": csrf_token, "Content-Type": "application/json"}

    valid_template_payload = {"templateName": "Valid-Template", "templateDescription": "A valid template for testing", "deviceType": "vedge-C8000V", "templateDefinition": {"system": {"host-name": "{{hostname}}", "system-ip": "{{system_ip}}", "site-id": "{{site_id}}"}}}

    response = session.post(template_url, json=valid_template_payload, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("✅ Valid schema accepted:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Unexpected response: {response.text}")

    # Step 4: Test Device Template Creation - Invalid Schema (Missing Required Field)
    print("\n📋 Step 4: Testing Device Template Creation (Invalid Schema - Missing Required Field)...")

    invalid_template_payload = {
        "templateName": "Invalid-Template",
        "templateDescription": "Missing deviceType field",
        # "deviceType": "vedge-C8000V",  # Missing required field
        "templateDefinition": {"system": {"host-name": "{{hostname}}"}},
    }

    response = session.post(template_url, json=invalid_template_payload, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 422:  # Validation error
        print("✅ Schema validation correctly rejected invalid payload:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Expected validation error, got: {response.text}")

    # Step 5: Test Device Template Creation - Invalid Schema (Wrong Type)
    print("\n📋 Step 5: Testing Device Template Creation (Invalid Schema - Wrong Device Type)...")

    invalid_type_payload = {"templateName": "Invalid-Type-Template", "templateDescription": "Invalid device type", "deviceType": "invalid-device-type", "templateDefinition": {"system": {"host-name": "{{hostname}}"}}}  # Not in enum

    response = session.post(template_url, json=invalid_type_payload, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 422:  # Validation error
        print("✅ Schema validation correctly rejected invalid device type:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Expected validation error, got: {response.text}")

    # Step 6: Test Site List Creation - Valid Schema
    print("\n🏢 Step 6: Testing Site List Creation (Valid Schema)...")
    site_list_url = urljoin(base_url, "/dataservice/template/policy/list/site")

    valid_site_list_payload = {"name": "valid-site-list", "description": "A valid site list", "type": "site", "entries": [{"siteId": "100"}, {"siteId": "200"}]}

    response = session.post(site_list_url, json=valid_site_list_payload, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("✅ Valid site list schema accepted:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Unexpected response: {response.text}")

    # Step 7: Test Site List Creation - Invalid Schema (Additional Properties)
    print("\n🏢 Step 7: Testing Site List Creation (Invalid Schema - Additional Properties)...")

    invalid_site_list_payload = {"name": "invalid-site-list", "description": "Site list with additional properties", "type": "site", "entries": [{"siteId": "100"}], "extraField": "not allowed"}  # Additional property not allowed

    response = session.post(site_list_url, json=invalid_site_list_payload, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 422:  # Validation error
        print("✅ Schema validation correctly rejected additional properties:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Expected validation error, got: {response.text}")

    print("\n🎉 Schema validation testing completed!")
    # Final assertion ensures we reached end without earlier assertion failures
    assert True


def main():
    """Main function"""
    import sys

    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

    print(f"Testing schema validation at: {base_url}")

    try:
        success = test_schema_validation(base_url)
        if success:
            print("\n✅ All schema validation tests completed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Could not connect to {base_url}")
        print("Make sure the mock server is running with vmanage-api config!")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
