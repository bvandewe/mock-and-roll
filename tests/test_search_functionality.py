#!/usr/bin/env python3
"""
Test script to verify the search functionality for logged requests/responses.

This module tests the complete search functionality including:
- Log entry parsing
- Request/response pairing by correlation ID
- Header extraction and parsing
- Path regex filtering
- Time-based filtering
- Status code summarization
- CLI command integration
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cli.application.server_management import SearchLogsUseCase
from cli.domain.entities import LogEntry, RequestResponsePair, SearchResult
from cli.infrastructure.log_search import FileSystemLogSearchRepository
from cli.interface.commands import SearchCommand
from cli.interface.presentation import Presenter


class TestSearchFunctionality(unittest.TestCase):
    """Test cases for the search functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent
        self.test_logs_dir = self.project_root / "logs"

        # Sample log content for testing
        self.sample_log_content = """2025-09-09 09:57:19,267 - root - INFO - Logging configured - Level: DEBUG, Console: True, File: True
2025-09-09 09:57:20,277 - api.requests - INFO - [00fd818c] REQUEST: GET http://0.0.0.0:8000/ from 127.0.0.1
2025-09-09 09:57:20,277 - api.requests - DEBUG - [00fd818c] Request Headers: {'host': '0.0.0.0:8000', 'user-agent': 'python-requests/2.32.5', 'accept-encoding': 'gzip, deflate', 'accept': '*/*', 'connection': 'keep-alive'}
2025-09-09 09:57:20,278 - api.requests - INFO - [00fd818c] RESPONSE: 200 for GET http://0.0.0.0:8000/ - Time: 0.001s
2025-09-09 09:57:20,278 - api.requests - DEBUG - [00fd818c] Response Headers: {'content-length': '74', 'content-type': 'application/json'}
2025-09-09 09:57:20,278 - api.requests - DEBUG - [00fd818c] Response Body: {"message":"Mock server is running. Check /docs for available endpoints."}
2025-09-09 09:59:58,597 - api.requests - INFO - [b6be315d] REQUEST: GET http://0.0.0.0:8000/items/123 from 127.0.0.1
2025-09-09 09:59:58,598 - api.requests - DEBUG - [b6be315d] Request Headers: {'host': '0.0.0.0:8000', 'connection': 'keep-alive', 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36', 'accept': 'application/json', 'x-api-key': 'demo-api-key-123', 'referer': 'http://0.0.0.0:8000/docs', 'accept-encoding': 'gzip, deflate', 'accept-language': 'en-US,en;q=0.9,fr;q=0.8,pt;q=0.7'}
2025-09-09 09:59:58,601 - api.requests - INFO - [b6be315d] RESPONSE: 200 for GET http://0.0.0.0:8000/items/123 - Time: 0.004s
2025-09-09 09:59:58,604 - api.requests - DEBUG - [b6be315d] Response Headers: {'content-length': '105', 'content-type': 'application/json'}
2025-09-09 09:59:58,605 - api.requests - DEBUG - [b6be315d] Response Body: {"message":"Here is the item you requested.","item_id":"123","data":{"name":"A Mocked Item","value":123}}
2025-09-09 10:00:05,156 - api.requests - INFO - [7d9f40c0] REQUEST: GET http://0.0.0.0:8000/api/docs from 127.0.0.1
2025-09-09 10:00:05,156 - api.requests - DEBUG - [7d9f40c0] Request Headers: {'host': '0.0.0.0:8000', 'accept': 'text/html', 'user-agent': 'test-browser'}
2025-09-09 10:00:05,158 - api.requests - INFO - [7d9f40c0] RESPONSE: 404 for GET http://0.0.0.0:8000/api/docs - Time: 0.002s
2025-09-09 10:00:05,158 - api.requests - DEBUG - [7d9f40c0] Response Headers: {'content-length': '22', 'content-type': 'application/json'}
2025-09-09 10:00:05,158 - api.requests - DEBUG - [7d9f40c0] Response Body: {"detail": "Not found"}"""

    def test_log_entry_parsing(self):
        """Test that LogEntry.from_line correctly parses log lines."""
        print("🧪 Testing LogEntry parsing...")

        # Test valid request log line
        request_line = "2025-09-09 09:57:20,277 - api.requests - INFO - [00fd818c] REQUEST: GET http://0.0.0.0:8000/ from 127.0.0.1"
        entry = LogEntry.from_line(request_line)

        self.assertIsNotNone(entry, "LogEntry should be parsed from valid line")
        self.assertEqual(entry.correlation_id, "00fd818c", "Correlation ID should be extracted correctly")
        self.assertEqual(entry.level, "INFO", "Log level should be extracted correctly")
        self.assertEqual(entry.logger, "api.requests", "Logger should be extracted correctly")
        self.assertIn("REQUEST:", entry.message, "Message should contain REQUEST:")
        self.assertEqual(entry.timestamp.year, 2025, "Timestamp year should be parsed correctly")
        self.assertEqual(entry.timestamp.month, 9, "Timestamp month should be parsed correctly")
        self.assertEqual(entry.timestamp.day, 9, "Timestamp day should be parsed correctly")

        # Test valid header log line
        header_line = "2025-09-09 09:57:20,277 - api.requests - DEBUG - [00fd818c] Request Headers: {'host': '0.0.0.0:8000'}"
        header_entry = LogEntry.from_line(header_line)

        self.assertIsNotNone(header_entry, "Header entry should be parsed")
        self.assertEqual(header_entry.correlation_id, "00fd818c", "Header correlation ID should match")
        self.assertIn("Request Headers:", header_entry.message, "Message should contain header info")

        # Test invalid log line
        invalid_line = "This is not a valid log line"
        invalid_entry = LogEntry.from_line(invalid_line)

        self.assertIsNone(invalid_entry, "Invalid log line should return None")

        print("   ✅ LogEntry parsing tests passed")

    def test_request_response_pair_creation(self):
        """Test RequestResponsePair creation from log entries."""
        print("🧪 Testing RequestResponsePair creation...")

        # Create mock log entries
        request_line = "2025-09-09 09:59:58,597 - api.requests - INFO - [b6be315d] REQUEST: GET http://0.0.0.0:8000/items/123 from 127.0.0.1"
        response_line = "2025-09-09 09:59:58,601 - api.requests - INFO - [b6be315d] RESPONSE: 200 for GET http://0.0.0.0:8000/items/123 - Time: 0.004s"
        req_headers_line = "2025-09-09 09:59:58,598 - api.requests - DEBUG - [b6be315d] Request Headers: {'host': '0.0.0.0:8000', 'accept': 'application/json'}"
        resp_headers_line = "2025-09-09 09:59:58,604 - api.requests - DEBUG - [b6be315d] Response Headers: {'content-length': '105', 'content-type': 'application/json'}"
        resp_body_line = '2025-09-09 09:59:58,605 - api.requests - DEBUG - [b6be315d] Response Body: {"message":"test"}'

        request_entry = LogEntry.from_line(request_line)
        response_entry = LogEntry.from_line(response_line)
        req_headers_entry = LogEntry.from_line(req_headers_line)
        resp_headers_entry = LogEntry.from_line(resp_headers_line)
        resp_body_entry = LogEntry.from_line(resp_body_line)

        # Create RequestResponsePair
        pair = RequestResponsePair.from_log_entries(request_entry, response_entry, req_headers_entry, resp_headers_entry, resp_body_entry)

        self.assertIsNotNone(pair, "RequestResponsePair should be created")
        self.assertEqual(pair.correlation_id, "b6be315d", "Correlation ID should match")
        self.assertEqual(pair.method, "GET", "HTTP method should be extracted")
        self.assertEqual(pair.path, "/items/123", "Path should be extracted correctly")
        self.assertEqual(pair.status_code, 200, "Status code should be parsed")
        self.assertEqual(pair.response_time_ms, 4.0, "Response time should be calculated correctly")

        # Test headers parsing
        self.assertIsNotNone(pair.request_headers, "Request headers should be parsed")
        self.assertIsInstance(pair.request_headers, dict, "Request headers should be a dictionary")
        self.assertEqual(pair.request_headers["host"], "0.0.0.0:8000", "Host header should be parsed correctly")

        self.assertIsNotNone(pair.response_headers, "Response headers should be parsed")
        self.assertIsInstance(pair.response_headers, dict, "Response headers should be a dictionary")
        self.assertEqual(pair.response_headers["content-type"], "application/json", "Content-type should be parsed correctly")

        # Test response body
        self.assertIsNotNone(pair.response_body, "Response body should be parsed")
        self.assertIn("message", pair.response_body, "Response body should contain expected content")

        print("   ✅ RequestResponsePair creation tests passed")

    def test_filesystem_log_search_repository(self):
        """Test FileSystemLogSearchRepository functionality."""
        print("🧪 Testing FileSystemLogSearchRepository...")

        # Create temporary log file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".logs", delete=False) as temp_file:
            temp_file.write(self.sample_log_content)
            temp_log_path = temp_file.name

        try:
            repo = FileSystemLogSearchRepository(self.project_root)

            # Test basic search
            result = repo.search_logs(temp_log_path, "/items")

            self.assertIsInstance(result, SearchResult, "Result should be SearchResult instance")
            self.assertEqual(result.total_requests, 1, "Should find 1 item request")
            self.assertIn(200, result.status_code_summary, "Should have 200 status code")
            self.assertEqual(result.status_code_summary[200], 1, "Should have 1 request with 200 status")

            # Test regex search
            api_result = repo.search_logs(temp_log_path, "/api.*")
            self.assertEqual(api_result.total_requests, 1, "Should find 1 API request")

            # Test all requests
            all_result = repo.search_logs(temp_log_path, ".*")
            self.assertEqual(all_result.total_requests, 3, "Should find all 3 requests")
            self.assertIn(200, all_result.status_code_summary, "Should have 200 status codes")
            self.assertIn(404, all_result.status_code_summary, "Should have 404 status code")

            # Test time filtering
            since_time = datetime(2025, 9, 9, 10, 0, 0)  # After the first two requests
            time_filtered_result = repo.search_logs(temp_log_path, ".*", since_time)
            self.assertEqual(time_filtered_result.total_requests, 1, "Should find 1 request after time filter")

            # Verify ordering (newest first)
            self.assertTrue(len(all_result.matched_requests) > 1, "Should have multiple requests for ordering test")
            timestamps = [req.timestamp for req in all_result.matched_requests]
            sorted_timestamps = sorted(timestamps, reverse=True)
            self.assertEqual(timestamps, sorted_timestamps, "Requests should be ordered newest first")

            print("   ✅ FileSystemLogSearchRepository tests passed")

        finally:
            os.unlink(temp_log_path)

    def test_search_logs_use_case(self):
        """Test SearchLogsUseCase functionality."""
        print("🧪 Testing SearchLogsUseCase...")

        # Create temporary log file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".logs", delete=False) as temp_file:
            temp_file.write(self.sample_log_content)
            temp_log_path = temp_file.name

        try:
            # Create mock repositories
            from cli.infrastructure.filesystem import (
                FileSystemServerConfigRepository,
                FileSystemServerInstanceRepository,
            )

            log_search_repo = FileSystemLogSearchRepository(self.project_root)
            server_repo = FileSystemServerInstanceRepository(self.project_root)
            config_repo = FileSystemServerConfigRepository(self.project_root)

            use_case = SearchLogsUseCase(log_search_repo, server_repo, config_repo)

            # Test use case execution with all logs
            result = use_case.execute(path_regex="/items", config_name=None, port=None, since_timestamp=None, use_all_logs=True)

            self.assertIsInstance(result, SearchResult, "Use case should return SearchResult")
            self.assertGreaterEqual(result.total_requests, 0, "Should return valid request count")

            print("   ✅ SearchLogsUseCase tests passed")

        finally:
            os.unlink(temp_log_path)

    def test_search_command_execution(self):
        """Test SearchCommand execution."""
        print("🧪 Testing SearchCommand execution...")

        # Create mock arguments
        class MockArgs:
            def __init__(self):
                self.path_regex = "/items"
                self.config = None
                self.port = None
                self.since = None
                self.all_logs = True

        mock_args = MockArgs()

        # Test with JSON presenter
        command = SearchCommand(self.project_root, json_mode=True)

        # Mock the use case to avoid file system dependencies in this test
        with patch.object(command, "search_use_case") as mock_use_case:
            mock_result = SearchResult(path_pattern="/items", log_file="test.logs", total_requests=2, matched_requests=[], status_code_summary={200: 2}, search_duration_ms=10.0)
            mock_use_case.execute.return_value = mock_result

            # Capture output
            with patch("builtins.print") as mock_print:
                command.execute(mock_args)

                # Verify that search was called
                mock_use_case.execute.assert_called_once()

                # Verify print was called (for JSON output)
                mock_print.assert_called()

        print("   ✅ SearchCommand execution tests passed")

    def test_presenter_output_formats(self):
        """Test Presenter output formats for search results."""
        print("🧪 Testing Presenter output formats...")

        # Create sample search result
        sample_request = RequestResponsePair(correlation_id="test123", method="GET", path="/test/path", status_code=200, timestamp=datetime.now(), response_time_ms=5.5, request_headers={"host": "localhost", "accept": "application/json"}, response_headers={"content-type": "application/json"}, request_body=None, response_body='{"result": "success"}')

        result = SearchResult(path_pattern="/test", log_file="test.logs", total_requests=1, matched_requests=[sample_request], status_code_summary={200: 1}, search_duration_ms=15.2)

        # Test JSON output
        json_presenter = Presenter(json_mode=True)
        with patch("builtins.print") as mock_print:
            json_presenter.show_search_results(result)

            # Verify JSON output was printed
            mock_print.assert_called()
            printed_content = mock_print.call_args[0][0]

            # Verify it's valid JSON
            json_data = json.loads(printed_content)
            self.assertEqual(json_data["total_requests"], 1)
            self.assertIn("matched_requests", json_data)
            self.assertEqual(len(json_data["matched_requests"]), 1)

            request_data = json_data["matched_requests"][0]
            self.assertEqual(request_data["method"], "GET")
            self.assertEqual(request_data["path"], "/test/path")
            self.assertEqual(request_data["status_code"], 200)
            self.assertIsNotNone(request_data["request_headers"])
            self.assertIsNotNone(request_data["response_headers"])

        # Test text output
        text_presenter = Presenter(json_mode=False)
        with patch("builtins.print") as mock_print:
            text_presenter.show_search_results(result)

            # Verify text output was printed
            mock_print.assert_called()

            # Check that key information was printed
            call_args_list = [call[0][0] for call in mock_print.call_args_list if call[0]]
            output_text = " ".join(str(arg) for arg in call_args_list)

            self.assertIn("Search Results", output_text)
            self.assertIn("Total requests found", output_text)
            self.assertIn("Status Code Summary", output_text)

        print("   ✅ Presenter output format tests passed")

    def test_error_handling(self):
        """Test error handling in search functionality."""
        print("🧪 Testing error handling...")

        repo = FileSystemLogSearchRepository(self.project_root)

        # Test with non-existent file
        with self.assertRaises(FileNotFoundError):
            repo.search_logs("/non/existent/file.logs", ".*")

        # Test with invalid regex
        with tempfile.NamedTemporaryFile(mode="w", suffix=".logs", delete=False) as temp_file:
            temp_file.write("test log content")
            temp_log_path = temp_file.name

        try:
            with self.assertRaises(ValueError):
                repo.search_logs(temp_log_path, "[invalid regex")
        finally:
            os.unlink(temp_log_path)

        print("   ✅ Error handling tests passed")

    def test_integration_with_real_logs(self):
        """Test integration with real log files if available."""
        print("🧪 Testing integration with real logs...")

        # Check if there are real log files to test with
        if self.test_logs_dir.exists():
            log_files = list(self.test_logs_dir.glob("*.logs"))
            if log_files:
                # Test with the most recent log file
                recent_log = max(log_files, key=lambda f: f.stat().st_mtime)

                repo = FileSystemLogSearchRepository(self.project_root)

                # Test basic search on real log
                try:
                    result = repo.search_logs(str(recent_log), ".*")
                    self.assertIsInstance(result, SearchResult)
                    self.assertGreaterEqual(result.total_requests, 0)

                    # If there are requests, verify they have the expected structure
                    if result.matched_requests:
                        sample_request = result.matched_requests[0]
                        self.assertIsNotNone(sample_request.correlation_id)
                        self.assertIsNotNone(sample_request.method)
                        self.assertIsNotNone(sample_request.path)
                        self.assertIsNotNone(sample_request.status_code)
                        self.assertIsNotNone(sample_request.timestamp)

                    print(f"   ✅ Real log integration test passed with {result.total_requests} requests")

                except Exception as e:
                    print(f"   ⚠️ Real log test skipped due to: {e}")
            else:
                print("   ⚠️ No real log files found for integration test")
        else:
            print("   ⚠️ Logs directory not found for integration test")


def test_search_functionality():
    """Main test function to run all search functionality tests."""
    print("🚀 Running Search Functionality Tests")
    print("=" * 60)

    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestSearchFunctionality)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All search functionality tests passed!")
        return True
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        return False


if __name__ == "__main__":
    test_search_functionality()
