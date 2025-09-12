"""Presentation layer for displaying information to users."""

import json
import re
from datetime import datetime
from typing import Any, Optional

from ..domain.entities import ServerConfig, ServerInstance


class Colors:
    """Terminal color codes."""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    MAGENTA = "\033[0;35m"
    NC = "\033[0m"  # No Color


class Presenter:
    """Handles presentation of information to users."""

    def __init__(self, json_mode: bool = False, no_emoji: bool = False):
        """Initialize presenter with output mode.

        Args:
            json_mode: If True, outputs JSON instead of colored text with emojis
            no_emoji: If True, removes emojis from text output (ignored when json_mode is True)
        """
        self.json_mode = json_mode
        self.no_emoji = no_emoji and not json_mode  # Only apply no_emoji when not in JSON mode

    def _remove_emojis(self, text: str) -> str:
        """Remove emojis from text using regex pattern.

        Args:
            text: Input text that may contain emojis

        Returns:
            Text with emojis removed
        """
        if not self.no_emoji:
            return text

        # Comprehensive emoji pattern that matches most Unicode emoji ranges
        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"  # emoticons
            "\U0001f300-\U0001f5ff"  # symbols & pictographs
            "\U0001f680-\U0001f6ff"  # transport & map symbols
            "\U0001f1e0-\U0001f1ff"  # flags (iOS)
            "\U00002702-\U000027b0"  # dingbats
            "\U000024c2-\U0001f251"
            "\U0001f900-\U0001f9ff"  # supplemental symbols and pictographs
            "\U00002600-\U000026ff"  # miscellaneous symbols
            "\U00002700-\U000027bf"  # dingbats
            "\U0001f018-\U0001f270"  # various symbols
            "\U0001f300-\U0001f6ff"  # miscellaneous symbols and pictographs
            "\U0001f780-\U0001f7ff"  # geometric shapes extended
            "\U0001f800-\U0001f8ff"  # supplemental arrows-c
            "\U0001f900-\U0001f9ff"  # supplemental symbols and pictographs
            "\U0001fa00-\U0001fa6f"  # chess symbols
            "\U0001fa70-\U0001faff"  # symbols and pictographs extended-a
            "\U00002000-\U0000206f"  # general punctuation
            "\U0000fe00-\U0000fe0f"  # variation selectors
            "]+",
            flags=re.UNICODE,
        )

        return emoji_pattern.sub("", text).strip()

    def _format_output(self, text: str) -> str:
        """Format text output by removing emojis if needed.

        Args:
            text: Input text to format

        Returns:
            Formatted text with emojis removed if no_emoji is True
        """
        return self._remove_emojis(text) if self.no_emoji else text

    def _format_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """Format datetime for JSON output."""
        return dt.isoformat() if dt else None

    def _output_json(self, data: dict[str, Any]) -> None:
        """Output data as JSON."""
        print(json.dumps(data, indent=2, default=str))

    def show_error(self, message: str) -> None:
        """Show error message."""
        if self.json_mode:
            self._output_json({"status": "error", "message": message})
        else:
            formatted_message = self._format_output(f"{Colors.RED}❌ Error: {message}{Colors.NC}")
            print(formatted_message)

    def show_warning(self, message: str) -> None:
        """Show warning message."""
        if self.json_mode:
            self._output_json({"status": "warning", "message": message})
        else:
            formatted_message = self._format_output(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")
            print(formatted_message)

    def show_success(self, message: str) -> None:
        """Show success message."""
        if self.json_mode:
            self._output_json({"status": "success", "message": message})
        else:
            formatted_message = self._format_output(f"{Colors.GREEN}✅ {message}{Colors.NC}")
            print(formatted_message)

    def show_info(self, message: str) -> None:
        """Show info message."""
        if self.json_mode:
            self._output_json({"status": "info", "message": message})
        else:
            formatted_message = self._format_output(f"{Colors.BLUE}ℹ️  {message}{Colors.NC}")
            print(formatted_message)

    def show_server_started(self, instance: ServerInstance) -> None:
        """Show server started information."""
        if self.json_mode:
            self._output_json({"status": "success", "action": "server_started", "server": {"config_name": instance.config_name, "pid": instance.pid, "host": instance.host, "port": instance.port, "base_url": instance.base_url, "docs_url": instance.docs_url, "openapi_url": instance.openapi_url, "started_at": self._format_datetime(instance.started_at)}})
        else:
            print(self._format_output(f"{Colors.GREEN}🚀 Starting Mock Server with '{instance.config_name}' configuration...{Colors.NC}"))
            print(self._format_output(f"{Colors.BLUE}🌐 Host: {instance.host}{Colors.NC}"))
            print(self._format_output(f"{Colors.BLUE}🔌 Port: {instance.port}{Colors.NC}"))
            print()

            print(self._format_output(f"{Colors.GREEN}✅ Server started successfully!{Colors.NC}"))
            print()
            print(self._format_output(f"{Colors.GREEN}📊 Server Information:{Colors.NC}"))
            print(f"{Colors.BLUE}   Configuration: {instance.config_name}{Colors.NC}")
            print(f"{Colors.BLUE}   Process ID: {instance.pid}{Colors.NC}")
            print(f"{Colors.BLUE}   Access the API at: {instance.base_url}{Colors.NC}")
            print(f"{Colors.BLUE}   Interactive docs: {instance.docs_url}{Colors.NC}")
            print(f"{Colors.BLUE}   OpenAPI schema: {instance.openapi_url}{Colors.NC}")
            print()
            print(self._format_output(f"{Colors.YELLOW}🛑 To stop the server:{Colors.NC}"))
            print(f"{Colors.CYAN}   mockctl stop{Colors.NC}")
            print(f"{Colors.CYAN}   mockctl stop --pid {instance.pid}{Colors.NC}")

    def show_config_selection(self, configs: list[ServerConfig]) -> None:
        """Show configuration selection menu."""
        if self.json_mode:
            self._output_json({"action": "config_selection", "configs": [{"index": i, "name": config.name, "description": config.description, "is_valid": config.is_valid()} for i, config in enumerate(configs, 1)]})
        else:
            print(self._format_output(f"{Colors.CYAN}📂 Available Configurations:{Colors.NC}"))
            print()

            for i, config in enumerate(configs, 1):
                status = "✅" if config.is_valid() else "❌"
                formatted_status = self._format_output(status)
                print(f"{Colors.YELLOW}{i}){Colors.NC} {config.name} {formatted_status}")
                if config.description:
                    print(f"   {Colors.BLUE}{config.description}{Colors.NC}")
            print()

    def show_servers_list(self, servers: list[ServerInstance]) -> None:
        """Show list of servers."""
        if self.json_mode:
            self._output_json({"action": "list_servers", "count": len(servers), "servers": [{"config_name": server.config_name, "pid": server.pid, "host": server.host, "port": server.port, "base_url": server.base_url, "docs_url": server.docs_url, "openapi_url": server.openapi_url, "started_at": self._format_datetime(server.started_at), "is_running": server.is_running} for server in servers]})
        else:
            print(self._format_output(f"{Colors.BLUE}🔍 Scanning for running Mock API Servers...{Colors.NC}"))
            print()
            print(self._format_output(f"{Colors.GREEN}📊 Found {len(servers)} tracked server(s):{Colors.NC}"))
            print()

            for server in servers:
                # Format started time
                started_str = "unknown"
                if server.started_at:
                    started_str = server.started_at.strftime("%Y-%m-%d %H:%M:%S")

                status_text = f"{Colors.GREEN}🟢 Running{Colors.NC}" if server.is_running else f"{Colors.RED}🔴 Stopped{Colors.NC}"
                formatted_status = self._format_output(status_text)

                print(f"{Colors.CYAN}Config:{Colors.NC} {server.config_name}")
                print(f"{Colors.CYAN}Status:{Colors.NC} {formatted_status}")
                print(f"{Colors.CYAN}PID:{Colors.NC} {server.pid}")
                print(f"{Colors.CYAN}Address:{Colors.NC} {server.base_url}")
                print(f"{Colors.CYAN}Started:{Colors.NC} {started_str}")
                print(f"{Colors.CYAN}API Docs:{Colors.NC} {server.docs_url}")
                print()

    def show_no_servers(self) -> None:
        """Show no servers found message."""
        if self.json_mode:
            self._output_json({"action": "list_servers", "count": 0, "servers": [], "message": "No tracked servers found"})
        else:
            print(self._format_output(f"{Colors.YELLOW}📭 No tracked servers found{Colors.NC}"))
            print()
            print(self._format_output(f"{Colors.BLUE}💡 Looking for untracked mock servers...{Colors.NC}"))

    def show_untracked_processes(self, processes: list[dict]) -> None:
        """Show untracked processes."""
        if self.json_mode:
            self._output_json({"action": "untracked_processes", "count": len(processes), "processes": processes})
        else:
            for proc_info in processes:
                print(f"{Colors.YELLOW}   Untracked: PID {proc_info['pid']} - {proc_info['cmdline']}{Colors.NC}")

    def show_server_selection(self, servers: list[ServerInstance], action: str) -> None:
        """Show server selection menu."""
        if self.json_mode:
            self._output_json({"action": "server_selection", "operation": action, "servers": [{"index": i, "config_name": server.config_name, "pid": server.pid, "port": server.port} for i, server in enumerate(servers, 1)]})
        else:
            print(f"{Colors.CYAN}Multiple servers found. Choose one to {action}:{Colors.NC}")
            for i, server in enumerate(servers, 1):
                print(f"{Colors.YELLOW}{i}){Colors.NC} {server.config_name} (PID: {server.pid}, Port: {server.port})")

    def show_stop_result(self, success: bool, identifier: str) -> None:
        """Show stop operation result."""
        if self.json_mode:
            self._output_json({"action": "stop_server", "success": success, "identifier": identifier, "message": f"Successfully stopped server ({identifier})" if success else f"Failed to stop server ({identifier})"})
        else:
            if success:
                print(self._format_output(f"{Colors.GREEN}✅ Successfully stopped server ({identifier}){Colors.NC}"))
            else:
                print(self._format_output(f"{Colors.RED}❌ Failed to stop server ({identifier}){Colors.NC}"))

    def show_stop_all_results(self, results: list[bool]) -> None:
        """Show stop all operation results."""
        successful = sum(results)
        total = len(results)

        if self.json_mode:
            self._output_json({"action": "stop_all_servers", "total": total, "successful": successful, "failed": total - successful, "success_rate": successful / total if total > 0 else 0})
        else:
            if successful == total:
                print(self._format_output(f"{Colors.GREEN}✅ Successfully stopped all {total} servers{Colors.NC}"))
            elif successful > 0:
                print(self._format_output(f"{Colors.YELLOW}⚠️  Stopped {successful} of {total} servers{Colors.NC}"))
            else:
                print(self._format_output(f"{Colors.RED}❌ Failed to stop any servers{Colors.NC}"))

    def show_config_help(self, configs: list[ServerConfig]) -> None:
        """Show configuration help."""
        if self.json_mode:
            self._output_json(
                {
                    "action": "config_help",
                    "configs": [{"name": config.name, "description": config.description, "is_valid": config.is_valid(), "path": config.path} for config in configs],
                    "usage_examples": {"start_interactive": "mockctl start", "start_specific": "mockctl start basic", "start_with_port": "mockctl start vmanage --port 8080", "stop_auto": "mockctl stop", "stop_by_config": "mockctl stop basic", "stop_by_port": "mockctl stop --port 8080", "stop_all": "mockctl stop --all", "list_servers": "mockctl list", "list_json": "mockctl list --json"},
                }
            )
        else:
            print(self._format_output(f"{Colors.CYAN}🔧 Mock Server Configuration Management{Colors.NC}"))
            print(f"{Colors.BLUE}{'=' * 38}{Colors.NC}")
            print()
            print(self._format_output(f"{Colors.GREEN}📁 Configuration Structure:{Colors.NC}"))
            print("   configs/")

            for config in configs:
                status = "✅" if config.is_valid() else "❌"
                formatted_status = self._format_output(status)
                print(f"   ├── {config.name}/          {formatted_status} {config.description or ''}")

            print()
            print("   Each config directory contains:")
            print("   ├── api.json        # API metadata and settings")
            print("   ├── auth.json       # Authentication configuration")
            print("   └── endpoints.json  # Route definitions")
            print()
            print(self._format_output(f"{Colors.GREEN}🚀 Starting Servers:{Colors.NC}"))
            print()
            print("   # Interactive mode")
            print(f"   {Colors.CYAN}mockctl start{Colors.NC}")
            print()
            print("   # Specific configuration")
            print(f"   {Colors.CYAN}mockctl start basic{Colors.NC}")
            print(f"   {Colors.CYAN}mockctl start vmanage --port 8080{Colors.NC}")
            print()
            print(self._format_output(f"{Colors.GREEN}🛑 Stopping Servers:{Colors.NC}"))
            print()
            print(f"   {Colors.CYAN}mockctl stop{Colors.NC}              # Auto-detect")
            print(f"   {Colors.CYAN}mockctl stop basic{Colors.NC}        # By config")
            print(f"   {Colors.CYAN}mockctl stop --port 8080{Colors.NC}  # By port")
            print(f"   {Colors.CYAN}mockctl stop --all{Colors.NC}        # Stop all")

    def show_search_results(self, result) -> None:
        """Show search results for requests and responses."""
        if self.json_mode:
            # Convert SearchResult to JSON-serializable format
            json_data = {"total_requests": result.total_requests, "status_code_summary": result.status_code_summary, "matched_requests": []}

            for req_resp in result.matched_requests:
                json_data["matched_requests"].append({"timestamp": req_resp.timestamp.isoformat() if req_resp.timestamp else None, "correlation_id": req_resp.correlation_id, "method": req_resp.method, "path": req_resp.path, "status_code": req_resp.status_code, "response_time_ms": req_resp.response_time_ms, "request_body": req_resp.request_body, "response_body": req_resp.response_body, "request_headers": req_resp.request_headers, "response_headers": req_resp.response_headers})

            self._output_json(json_data)
        else:
            # Text output with colors
            print(self._format_output(f"\n{Colors.GREEN}🔍 Search Results:{Colors.NC}"))
            print(f"   Total requests found: {Colors.CYAN}{result.total_requests}{Colors.NC}")

            if result.status_code_summary:
                print(self._format_output(f"\n{Colors.YELLOW}📊 Status Code Summary:{Colors.NC}"))
                # Sort status codes numerically by extracting the numeric part
                sorted_items = sorted(result.status_code_summary.items(), key=lambda x: int(x[0][7:]) if x[0].startswith("status_") else 0)

                for status_key, count in sorted_items:
                    # Extract numeric status code for color determination
                    try:
                        status_code = int(status_key[7:]) if status_key.startswith("status_") else 0
                        color = Colors.GREEN if status_code < 400 else Colors.RED if status_code >= 400 else Colors.YELLOW
                    except (ValueError, IndexError):
                        color = Colors.YELLOW

                    # Display using the string key directly (already has "status_" prefix)
                    print(f"   {color}{status_key}{Colors.NC}: {count} requests")

            if result.matched_requests:
                print(self._format_output(f"\n{Colors.BLUE}📝 Request/Response Details:{Colors.NC}"))
                for i, req_resp in enumerate(result.matched_requests):
                    print(f"\n   {Colors.CYAN}[{i+1}]{Colors.NC} {req_resp.timestamp}")
                    print(f"       Method: {Colors.MAGENTA}{req_resp.method}{Colors.NC}")
                    print(f"       Path: {req_resp.path}")

                    # Color status code based on value
                    status_color = Colors.GREEN if req_resp.status_code < 400 else Colors.RED
                    print(f"       Status: {status_color}{req_resp.status_code}{Colors.NC}")

                    if req_resp.correlation_id:
                        print(f"       Correlation ID: {req_resp.correlation_id}")

                    if req_resp.response_time_ms:
                        print(f"       Response Time: {req_resp.response_time_ms:.2f}ms")

                    if req_resp.request_headers:
                        print(f"       Request Headers: {req_resp.request_headers}")

                    if req_resp.response_headers:
                        print(f"       Response Headers: {req_resp.response_headers}")

                    if req_resp.request_body:
                        print(f"       Request: {req_resp.request_body}")

                    if req_resp.response_body:
                        print(f"       Response: {req_resp.response_body}")
            else:
                print(f"\n{Colors.YELLOW}   No matching requests found.{Colors.NC}")

            print()

    def show_test_results(self, test_results: list[dict[str, Any]]) -> None:
        """Display test results for server endpoints.

        Args:
            test_results: List of test results for each server
        """
        if self.json_mode:
            self._output_json({"test_results": test_results})
            return

        print(self._format_output(f"{Colors.BLUE}🧪 Server Endpoint Tests{Colors.NC}\n"))

        for server_result in test_results:
            config_name = server_result["config"]
            base_url = server_result["base_url"]

            print(self._format_output(f"{Colors.CYAN}📊 Testing server: {config_name}{Colors.NC}"))
            print(f"   Base URL: {base_url}")

            for test in server_result["tests"]:
                status = test["status"]
                endpoint = test["endpoint"]
                description = test["description"]

                # Choose status indicator and color based on result
                if status == "success":
                    indicator = "✅"
                    color = Colors.GREEN
                elif status == "warning":
                    indicator = "⚠️"
                    color = Colors.YELLOW
                else:  # error
                    indicator = "❌"
                    color = Colors.RED

                print(f"\n   {self._format_output(indicator)} {color}{endpoint}{Colors.NC} - {description}")

                if status in ["success", "warning"]:
                    status_code = test.get("status_code")
                    response_time = test.get("response_time_ms")
                    content_type = test.get("content_type", "unknown")

                    if status_code is not None:
                        status_color = Colors.GREEN if status_code < 400 else Colors.RED
                        print(f"      Status: {status_color}{status_code}{Colors.NC}")

                    if response_time is not None:
                        print(f"      Response time: {response_time}ms")

                    print(f"      Content type: {content_type}")

                if "message" in test:
                    print(f"      {color}Error: {test['message']}{Colors.NC}")

                print(f"      URL: {test['url']}")

            print()  # Extra spacing between servers
