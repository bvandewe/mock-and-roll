#!/usr/bin/env python3
"""
Quick test to verify auth placeholder resolution
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_auth_placeholders():
    """Test authentication placeholder resolution."""
    try:
        from auth.security import resolve_auth_placeholders

        # Sample auth config similar to vManage
        auth_config = {"authentication_methods": {"vmanage_session": {"type": "session_based", "session_cookie": "JSESSIONID", "csrf_token_header": "X-XSRF-TOKEN", "valid_sessions": [{"session_id": "vmanage-session-123", "csrf_token": "mock-csrf-token-456", "username": "admin"}, {"session_id": "vmanage-session-789", "csrf_token": "mock-csrf-token-abc", "username": "operator"}]}}}

        # Test placeholder resolution
        test_value = "${auth.vmanage_session.random_session.session_id}"
        resolved_value = resolve_auth_placeholders(test_value, auth_config)

        print(f"Original: {test_value}")
        print(f"Resolved: {resolved_value}")

        if resolved_value != test_value and resolved_value in ["vmanage-session-123", "vmanage-session-789"]:
            print("✅ Authentication placeholder resolution is working!")
            return True
        else:
            print("❌ Authentication placeholder resolution is not working!")
            return False

    except Exception as e:
        print(f"❌ Error testing auth placeholders: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_auth_placeholders()
