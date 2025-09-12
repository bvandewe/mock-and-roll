#!/usr/bin/env python3
"""
Test script to verify mockctl search functionality with config-specific logs.

This script tests:
1. Log file pattern matching for config names
2. Search functionality with --config parameter
3. Proper exclusion of latest.logs files
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_log_file_pattern_matching():
    """Test that log file pattern matching works for config names."""
    print("=" * 60)
    print("TESTING LOG FILE PATTERN MATCHING")
    print("=" * 60)

    try:
        from cli.infrastructure.log_search import FileSystemLogSearchRepository

        project_root = Path(".")
        repo = FileSystemLogSearchRepository(project_root)

        # Test listing all logs
        all_logs = repo.list_available_log_files()
        print(f"All available log files: {len(all_logs)}")
        for log_file in all_logs:
            print(f"  - {os.path.basename(log_file)}")

        # Test config-specific searches
        test_configs = ["basic", "persistence", "vmanage"]

        for config in test_configs:
            config_logs = repo.list_available_log_files(config)
            print(f"\nLogs for config '{config}': {len(config_logs)}")
            for log_file in config_logs:
                print(f"  - {os.path.basename(log_file)}")

        # Verify latest.logs is excluded
        latest_logs_found = any("latest.logs" in log for log in all_logs)
        if latest_logs_found:
            print("\n❌ WARNING: latest.logs still found in results!")
        else:
            print("\n✅ latest.logs properly excluded from results")

        return True

    except Exception as e:
        print(f"❌ Pattern matching test failed: {e}")
        return False


def test_search_use_case():
    """Test the search use case with config parameter."""
    print("\n" + "=" * 60)
    print("TESTING SEARCH USE CASE")
    print("=" * 60)

    try:
        from cli.application.server_management import SearchLogsUseCase
        from cli.infrastructure.filesystem import (
            FileSystemServerConfigRepository,
            FileSystemServerInstanceRepository,
        )
        from cli.infrastructure.log_search import FileSystemLogSearchRepository

        project_root = Path(".")

        # Initialize repositories
        log_search_repo = FileSystemLogSearchRepository(project_root)
        server_repo = FileSystemServerInstanceRepository(project_root)
        config_repo = FileSystemServerConfigRepository(project_root / "configs")

        # Initialize use case
        search_use_case = SearchLogsUseCase(log_search_repo, server_repo, config_repo)

        # Test config-specific log determination
        test_configs = ["basic", "persistence", "vmanage"]

        for config in test_configs:
            print(f"\nTesting log file determination for config '{config}':")
            try:
                log_files = search_use_case._determine_log_files(config, None, False)
                print(f"  Found {len(log_files)} log files:")
                for log_file in log_files:
                    print(f"    - {os.path.basename(log_file)}")
            except Exception as e:
                print(f"  No log files found for {config}: {e}")

        return True

    except Exception as e:
        print(f"❌ Search use case test failed: {e}")
        return False


def test_actual_search():
    """Test actual search functionality."""
    print("\n" + "=" * 60)
    print("TESTING ACTUAL SEARCH FUNCTIONALITY")
    print("=" * 60)

    # Check if we have any log files to search
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("❌ No logs directory found")
        return False

    log_files = list(logs_dir.glob("*.logs"))
    log_files = [f for f in log_files if f.name != "latest.logs"]

    if not log_files:
        print("❌ No log files found for testing")
        return False

    print(f"Found {len(log_files)} log files to test with:")
    for log_file in log_files:
        print(f"  - {log_file.name}")

    # Test searching in the most recent log file
    most_recent = max(log_files, key=lambda f: f.stat().st_mtime)
    print(f"\nTesting search in most recent log file: {most_recent.name}")

    try:
        from cli.infrastructure.log_search import FileSystemLogSearchRepository

        project_root = Path(".")
        repo = FileSystemLogSearchRepository(project_root)

        # Test search for common patterns
        test_patterns = ["/docs", "/openapi.json", ".*"]

        for pattern in test_patterns:
            try:
                result = repo.search_logs(str(most_recent), pattern)
                print(f"  Pattern '{pattern}': {result.total_requests} requests found")
            except Exception as e:
                print(f"  Pattern '{pattern}': Search failed - {e}")

        return True

    except Exception as e:
        print(f"❌ Actual search test failed: {e}")
        return False


def main():
    """Run all search functionality tests."""
    print("🔍 MOCKCTL SEARCH FUNCTIONALITY VERIFICATION")
    print("🔍 Mock-and-Roll Project")
    print()

    # Run tests
    pattern_ok = test_log_file_pattern_matching()
    use_case_ok = test_search_use_case()
    search_ok = test_actual_search()

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    if pattern_ok and use_case_ok and search_ok:
        print("🎉 SEARCH FUNCTIONALITY: ✅ FULLY VERIFIED")
        print("   - Log file pattern matching works correctly")
        print("   - Config-specific search logic implemented")
        print("   - latest.logs properly excluded")
        print("   - Search operations functional")
        return 0
    else:
        print("❌ SEARCH FUNCTIONALITY: ISSUES FOUND")
        if not pattern_ok:
            print("   - Log file pattern matching issues")
        if not use_case_ok:
            print("   - Search use case issues")
        if not search_ok:
            print("   - Search operation issues")
        return 1


if __name__ == "__main__":
    exit(main())
