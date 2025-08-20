#!/usr/bin/env python3
"""
Test script to verify template functionality
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from main import (
    generate_realistic_timestamp,
    process_response_body,
    substitute_timestamp_templates,
)


def test_timestamp_templates():
    """Test timestamp template substitution"""
    print("Testing timestamp template substitution...")

    # Test static timestamp replacement
    test_data = {"device": {"last_updated": "2025-08-19T10:30:00Z", "created_at": "2024-12-01T15:45:30Z", "timestamp": "1724058600"}, "interface": {"status_time": "2025-08-20T09:15:22+00:00"}}

    print("Original data:")
    print(test_data)

    processed_data = process_response_body(test_data)

    print("\nProcessed data:")
    print(processed_data)

    # Test explicit template placeholders
    template_data = {"timestamp": "{{timestamp}}", "date": "{{date}}", "unix_ts": "{{unix_timestamp}}", "unix_ts_ms": "{{unix_timestamp_ms}}"}

    print("\nTemplate data:")
    print(template_data)

    processed_templates = process_response_body(template_data)

    print("\nProcessed templates:")
    print(processed_templates)


def test_individual_functions():
    """Test individual helper functions"""
    print("\n" + "=" * 50)
    print("Testing individual helper functions...")

    # Test timestamp substitution function
    test_strings = ["2025-08-19T10:30:00Z", "Last updated: 2025-08-19T10:30:00Z at server", "Unix timestamp: 1724058600", "Date: 2025-08-19", "Multiple timestamps: 2025-08-19T10:30:00Z and 2024-12-01T15:45:30Z"]

    for test_str in test_strings:
        result = substitute_timestamp_templates(test_str)
        print(f"'{test_str}' -> '{result}'")

    # Test realistic timestamp generation
    print("\nRealistic timestamp examples:")
    for i in range(5):
        print(f"  {i+1}: {generate_realistic_timestamp()}")


if __name__ == "__main__":
    test_timestamp_templates()
    test_individual_functions()
    print("\nTemplate testing completed!")
