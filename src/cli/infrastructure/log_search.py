"""Infrastructure implementation for log searching."""

import re
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..domain.entities import (
    LogEntry,
    RequestResponsePair,
    SearchResult,
    ServerInstance,
)
from ..domain.repositories import LogSearchRepository


class FileSystemLogSearchRepository(LogSearchRepository):
    """File system implementation of log search repository."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logs_dir = project_root / "logs"

    def search_logs(self, log_file_path: str, path_regex: str, since_timestamp: Optional[datetime] = None) -> SearchResult:
        """Search log file for requests matching path regex."""
        start_time = time.time()

        # Convert relative path to absolute
        if not Path(log_file_path).is_absolute():
            log_file_path = str(self.project_root / log_file_path)

        log_file = Path(log_file_path)
        if not log_file.exists():
            raise FileNotFoundError(f"Log file not found: {log_file_path}")

        # Parse log file
        log_entries = self._parse_log_file(log_file, since_timestamp)

        # Find request/response pairs
        request_response_pairs = self._match_requests_responses(log_entries, log_file_path)

        # Filter by path regex
        matched_pairs = self._filter_by_path_regex(request_response_pairs, path_regex)

        # Sort by timestamp (newest first)
        matched_pairs.sort(key=lambda x: x.timestamp, reverse=True)

        # Calculate status code summary
        status_summary = self._calculate_status_summary(matched_pairs)

        search_duration = (time.time() - start_time) * 1000

        return SearchResult(path_pattern=path_regex, log_files=[log_file_path], total_requests=len(matched_pairs), matched_requests=matched_pairs, status_code_summary=status_summary, search_duration_ms=search_duration, since_timestamp=since_timestamp)

    def find_log_file_for_server(self, server: ServerInstance) -> Optional[str]:
        """Find the log file path for a server instance."""
        if server.log_file:
            log_file = self.project_root / server.log_file
            if log_file.exists():
                return str(log_file)

        # Try to find by pattern: {timestamp}_{config}_{port}.logs
        pattern = f"*{server.config_name}_{server.port}.logs"
        matching_files = list(self.logs_dir.glob(pattern))

        if matching_files:
            # Return the most recent one
            return str(max(matching_files, key=lambda f: f.stat().st_mtime))

        return None

    def list_available_log_files(self, config_name: Optional[str] = None) -> list[str]:
        """List available log files, excluding generic log files like latest.logs."""
        if not self.logs_dir.exists():
            return []

        if config_name:
            pattern = f"*{config_name}*.logs"
        else:
            pattern = "*.logs"

        log_files = list(self.logs_dir.glob(pattern))

        # Filter out generic log files that don't contain request/response data
        log_files = [f for f in log_files if f.name != "latest.logs"]

        # Sort by modification time (newest first)
        log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        return [str(f) for f in log_files]

    def _parse_log_file(self, log_file: Path, since_timestamp: Optional[datetime] = None) -> list[LogEntry]:
        """Parse log file into log entries."""
        entries = []

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    entry = LogEntry.from_line(line)
                    if entry:
                        # Filter by timestamp if provided
                        if since_timestamp and entry.timestamp < since_timestamp:
                            continue
                        entries.append(entry)
        except Exception as e:
            raise RuntimeError(f"Failed to parse log file {log_file}: {e}")

        return entries

    def _match_requests_responses(self, log_entries: list[LogEntry], log_file_path: str) -> list[RequestResponsePair]:
        """Match request and response log entries by correlation ID."""
        # Group all entries by correlation ID
        correlation_groups: dict[str, list[LogEntry]] = defaultdict(list)

        for entry in log_entries:
            if entry.correlation_id:  # Only include entries with correlation IDs
                correlation_groups[entry.correlation_id].append(entry)

        # Create request/response pairs
        pairs = []
        for correlation_id, entries in correlation_groups.items():
            # Find the main request and response entries
            request_entry = None
            response_entry = None
            request_headers_entry = None
            response_headers_entry = None
            response_body_entry = None

            for entry in entries:
                if "REQUEST:" in entry.message:
                    request_entry = entry
                elif "RESPONSE:" in entry.message and "Time:" in entry.message:
                    response_entry = entry
                elif "Request Headers:" in entry.message:
                    request_headers_entry = entry
                elif "Response Headers:" in entry.message:
                    response_headers_entry = entry
                elif "Response Body:" in entry.message:
                    response_body_entry = entry

            if request_entry:
                pair = RequestResponsePair.from_log_entries(request_entry, response_entry, request_headers_entry, response_headers_entry, response_body_entry)
                if pair:
                    pair.log_file_source = log_file_path  # Set the log file source
                    pairs.append(pair)

        return pairs

    def _filter_by_path_regex(self, pairs: list[RequestResponsePair], path_regex: str) -> list[RequestResponsePair]:
        """Filter request/response pairs by path regex."""
        try:
            pattern = re.compile(path_regex, re.IGNORECASE)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{path_regex}': {e}")

        matched_pairs = []
        for pair in pairs:
            if pattern.search(pair.path):
                matched_pairs.append(pair)

        return matched_pairs

    def _calculate_status_summary(self, pairs: list[RequestResponsePair]) -> dict[str, int]:
        """Calculate status code summary from request/response pairs."""
        status_summary = defaultdict(int)

        for pair in pairs:
            status_key = f"status_{pair.status_code}"
            status_summary[status_key] += 1

        return dict(status_summary)
