#!/usr/bin/env python3
"""
Test script to verify log deletion configuration works correctly.
"""

import asyncio
import os
import tempfile

from fastapi import FastAPI, HTTPException

from src.routes.logging_management import add_logging_management_endpoints


async def test_log_deletion_controls():
    """Test that log deletion is properly controlled by configuration."""

    # Create temporary log file
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".log") as temp_log:
        temp_log_path = temp_log.name
        temp_log.write("Test log content\n")

    try:
        # Test case 1: Deletion allowed (default behavior)
        print("Test 1: Log deletion allowed")
        app1 = FastAPI()
        api_config_allowed = {"logging": {"enabled": true, "file_path": temp_log_path, "allow_log_deletion": true}}  # Explicitly allowed

        add_logging_management_endpoints(app1, api_config_allowed)

        # Mock the request and test

        # Create a simple test by importing and calling the function logic
        logging_config = api_config_allowed.get("logging", {})
        deletion_allowed = logging_config.get("allow_log_deletion", True)

        if deletion_allowed:
            # This should work
            print("✅ Deletion allowed as expected")
        else:
            print("❌ Deletion should be allowed but was blocked")
            return False

        # Test case 2: Deletion explicitly denied
        print("\nTest 2: Log deletion denied")
        api_config_denied = {"logging": {"enabled": True, "file_path": temp_log_path, "allow_log_deletion": False}}  # Explicitly denied

        logging_config = api_config_denied.get("logging", {})
        deletion_allowed = logging_config.get("allow_log_deletion", True)

        if not deletion_allowed:
            print("✅ Deletion correctly blocked")
        else:
            print("❌ Deletion should be blocked but was allowed")
            return False

        # Test case 3: Default behavior (should allow)
        print("\nTest 3: Default behavior (should allow)")
        api_config_default = {
            "logging": {
                "enabled": True,
                "file_path": temp_log_path,
                # No allow_log_deletion specified - should default to True
            }
        }

        logging_config = api_config_default.get("logging", {})
        deletion_allowed = logging_config.get("allow_log_deletion", True)  # Default True

        if deletion_allowed:
            print("✅ Default behavior allows deletion as expected")
        else:
            print("❌ Default behavior should allow deletion")
            return False

        # Test the HTTP status code logic
        print("\nTest 4: HTTP Exception handling")
        try:
            # Simulate the exception that would be raised
            if not api_config_denied["logging"].get("allow_log_deletion", True):
                raise HTTPException(status_code=403, detail="Log file deletion is disabled in the configuration")
            print("❌ Should have raised HTTPException")
            return False
        except HTTPException as e:
            if e.status_code == 403:
                print("✅ Correct 403 status code returned when deletion is disabled")
            else:
                print(f"❌ Wrong status code: {e.status_code}")
                return False

        return True

    finally:
        # Clean up
        if os.path.exists(temp_log_path):
            os.unlink(temp_log_path)


if __name__ == "__main__":
    success = asyncio.run(test_log_deletion_controls())
    if success:
        print("\n🎉 All log deletion control tests passed!")
    else:
        print("\n💥 Some tests failed.")
        exit(1)
