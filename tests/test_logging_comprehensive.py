#!/usr/bin/env python3
"""
Test script to verify comprehensive logging functionality.
"""

import json
import logging
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_logging_setup():
    """Test the logging configuration setup."""
    print("🧪 Testing logging setup...")

    try:
        from config.logging_config import get_logging_status, setup_logging

        # Sample API config with logging
        api_config = {"logging": {"enabled": True, "level": "DEBUG", "file_path": "/tmp/test_mock_api.log", "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s", "max_file_size_mb": 1, "backup_count": 2, "max_body_log_size": 1024, "request_response_logging": True}}

        # Setup logging
        setup_logging(api_config)

        # Test various loggers
        loggers_to_test = [
            ("root", logging.getLogger()),
            ("uvicorn", logging.getLogger("uvicorn")),
            ("uvicorn.access", logging.getLogger("uvicorn.access")),
            ("api.requests", logging.getLogger("api.requests")),
        ]

        print("\n📝 Testing logger outputs...")
        for logger_name, logger in loggers_to_test:
            logger.info(f"Test message from {logger_name} logger")
            logger.debug(f"Debug message from {logger_name} logger")

        # Check logging status
        status = get_logging_status(api_config)
        print(f"\n📊 Logging Status: {json.dumps(status, indent=2)}")

        # Check if log file was created and has content
        log_file = status["file_path"]
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                content = f.read()
            print(f"\n📄 Log file content ({len(content)} chars):")
            print("=" * 50)
            print(content)
            print("=" * 50)

            # Count log lines
            lines = content.strip().split("\n") if content.strip() else []
            print(f"\n✅ Log file created with {len(lines)} lines")

            # Verify different loggers are present
            loggers_found = set()
            for line in lines:
                for logger_name, _ in loggers_to_test:
                    if f" - {logger_name} - " in line:
                        loggers_found.add(logger_name)

            print(f"🔍 Loggers found in file: {loggers_found}")

            if len(loggers_found) >= 2:
                print("✅ Multiple loggers are writing to the file - SUCCESS!")
                return True
            else:
                print("❌ Not all loggers are writing to the file")
                return False
        else:
            print(f"❌ Log file not created at {log_file}")
            return False

    except Exception as e:
        print(f"❌ Error testing logging: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_logging_setup()

    if success:
        print("\n🎉 Logging test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Logging test failed!")
        sys.exit(1)
