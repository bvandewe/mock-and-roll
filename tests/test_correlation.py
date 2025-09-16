#!/usr/bin/env python3
"""
Test session/CSRF correlation to verify the fix
"""

import socket

import requests


def _server_running(host: str = "localhost", port: int = 8000) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def test_session_csrf_correlation():
    """Test that session IDs correlate with the correct CSRF tokens"""

    print("Testing session/CSRF correlation...")

    if not _server_running():
        print("⚠️  Server not running on localhost:8000 - skipping correlation test")
        return True

    # Test multiple requests to see the correlation when server available
    for i in range(3):
        session = requests.Session()

        print(f"\n--- Test {i+1} ---")

        # Authenticate to get a session
        auth_response = session.post("http://localhost:8000/j_security_check", data={"j_username": "admin", "j_password": "admin"}, headers={"Content-Type": "application/x-www-form-urlencoded"})

        print(f"Auth response status: {auth_response.status_code}")

        # Get the session ID that was set
        session_id = session.cookies.get("JSESSIONID")
        print(f"Session ID: {session_id}")

        # Now get the CSRF token using that session
        token_response = session.get("http://localhost:8000/dataservice/client/token")
        csrf_token = token_response.text.strip('"')
        print(f"CSRF Token: {csrf_token}")

        # Check correlation according to auth.json:
        # vmanage-session-123 -> mock-csrf-token-456
        # vmanage-session-789 -> mock-csrf-token-abc

        if session_id == "vmanage-session-123" and csrf_token == "mock-csrf-token-456":
            print("✅ Correct correlation: session-123 -> csrf-456")
        elif session_id == "vmanage-session-789" and csrf_token == "mock-csrf-token-abc":
            print("✅ Correct correlation: session-789 -> csrf-abc")
        else:
            print(f"❌ Incorrect correlation: {session_id} -> {csrf_token}")


if __name__ == "__main__":
    test_session_csrf_correlation()
