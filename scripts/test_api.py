#!/usr/bin/env python3
"""
API Test Script for Mock Server
Tests the GET /system/logging/logs endpoint using system API key authentication
"""

import argparse
import json
import sys
from typing import Optional

import requests


def test_system_logs_endpoint(host: str, port: int, api_key: str) -> bool:
    """
    Test the system logging endpoint

    Args:
        host: Server host
        port: Server port
        api_key: System API key for authentication

    Returns:
        True if test passes, False otherwise
    """
    base_url = f"http://{host}:{port}"
    endpoint = "/system/logging/logs"
    url = f"{base_url}{endpoint}"

    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    print(f"🧪 Testing System Logs Endpoint")
    print(f"📍 URL: {url}")
    print(f"🔑 API Key: {api_key[:10]}..." if len(api_key) > 10 else f"🔑 API Key: {api_key}")
    print(f"📊 Headers: {json.dumps(headers, indent=2)}")
    print()

    try:
        print("🚀 Making GET request...")
        response = requests.get(url, headers=headers, timeout=10)

        print(f"📈 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        print()

        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Success! Response body:")
                print(json.dumps(data, indent=2))
                return True
            except json.JSONDecodeError:
                print("✅ Success! Response body (text):")
                print(response.text)
                return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"📄 Response body: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed: Could not connect to {base_url}")
        print("💡 Make sure the server is running on the specified host and port")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def get_system_api_key(config_path: str) -> Optional[str]:
    """
    Extract system API key from auth.json configuration

    Args:
        config_path: Path to configuration directory

    Returns:
        System API key if found, None otherwise
    """
    auth_file = f"{config_path}/auth.json"
    try:
        with open(auth_file, "r") as f:
            auth_config = json.load(f)

        system_auth = auth_config.get("authentication_methods", {}).get("system_api_key", {})
        valid_keys = system_auth.get("valid_keys", [])

        if valid_keys:
            return valid_keys[0]  # Use first valid key
        else:
            print(f"❌ No system API keys found in {auth_file}")
            return None

    except FileNotFoundError:
        print(f"❌ Auth configuration not found: {auth_file}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in auth configuration: {e}")
        return None
    except Exception as e:
        print(f"❌ Error reading auth configuration: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Test Mock Server System Logging API")
    parser.add_argument("--host", default="localhost", help="Server host (default: localhost)")
    parser.add_argument("--port", type=int, required=True, help="Server port")
    parser.add_argument("--config", default="configs/basic", help="Configuration directory (default: configs/basic)")
    parser.add_argument("--api-key", help="System API key (auto-detected from config if not provided)")

    args = parser.parse_args()

    print("🔧 Mock Server API Test")
    print("=" * 50)

    # Get API key
    api_key = args.api_key
    if not api_key:
        print(f"📁 Reading API key from {args.config}/auth.json...")
        api_key = get_system_api_key(args.config)
        if not api_key:
            print("❌ Could not find system API key")
            return 1

    # Test the endpoint
    success = test_system_logs_endpoint(args.host, args.port, api_key)

    print()
    if success:
        print("✅ Test PASSED")
        return 0
    else:
        print("❌ Test FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
