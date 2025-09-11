#!/usr/bin/env python3
"""Test script for --no-emoji functionality."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import after path setup
from cli.interface.presentation import Presenter  # noqa: E402


def test_emoji_removal():
    """Test emoji removal functionality."""

    # Test with emojis enabled (default)
    presenter_with_emojis = Presenter(json_mode=False, no_emoji=False)

    # Test with emojis disabled
    presenter_no_emojis = Presenter(json_mode=False, no_emoji=True)

    # Test with JSON mode (should ignore no_emoji)
    presenter_json = Presenter(json_mode=True, no_emoji=True)

    print("=== Testing Emoji Handling ===\n")

    # Test basic emoji removal
    test_messages = ["🚀 Starting server...", "✅ Success message", "❌ Error occurred", "🔍 Search results: 5 items found", "📊 Server Information", "⚠️ Warning message"]

    print("1. Default behavior (emojis enabled):")
    for msg in test_messages:
        formatted = presenter_with_emojis._format_output(msg)
        print(f"   '{formatted}'")

    print("\n2. With --no-emoji flag:")
    for msg in test_messages:
        formatted = presenter_no_emojis._format_output(msg)
        print(f"   '{formatted}'")

    print("\n3. JSON mode (ignores --no-emoji):")
    print("   JSON mode outputs structured data, not text messages.")

    # Test that JSON mode correctly ignores no_emoji setting
    print(f"\n4. JSON mode presenter no_emoji setting: {presenter_json.no_emoji}")
    print("   (Should be False even when no_emoji=True was passed)")


if __name__ == "__main__":
    test_emoji_removal()
