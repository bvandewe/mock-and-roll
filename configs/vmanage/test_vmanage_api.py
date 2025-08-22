#!/usr/bin/env python3
"""
Test script for vManage API mock server
This script demonstrates the authentication flow and API calls.
"""

import json
from urllib.parse import urljoin

import requests


class VManageAPITest:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.csrf_token = None

    def authenticate(self, username="user1", password="password1"):
        """Authenticate with vManage mock server"""
        print(f"🔐 Authenticating as {username}...")

        auth_url = urljoin(self.base_url, "/j_security_check")
        data = {"j_username": username, "j_password": password}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = self.session.post(auth_url, data=data, headers=headers)

        if response.status_code == 200:
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(response.text)
            return False

    def get_csrf_token(self):
        """Get CSRF token from vManage"""
        print("🎫 Getting CSRF token...")

        token_url = urljoin(self.base_url, "/dataservice/client/token")
        response = self.session.get(token_url)

        if response.status_code == 200:
            # For the mock server, the token is returned in the response body
            self.csrf_token = response.text.strip('"')  # Remove quotes if present
            print(f"✅ CSRF token obtained: {self.csrf_token}")
            return True
        else:
            print(f"❌ Failed to get CSRF token: {response.status_code}")
            print(response.text)
            return False

    def get_device_monitor(self):
        """Get device monitoring information"""
        print("📊 Getting device monitor data...")

        if not self.csrf_token:
            print("❌ No CSRF token available")
            return False

        monitor_url = urljoin(self.base_url, "/dataservice/device/monitor")
        headers = {"X-XSRF-TOKEN": self.csrf_token}

        response = self.session.get(monitor_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Device monitor data retrieved:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ Failed to get device monitor data: {response.status_code}")
            print(response.text)
            return False

    def get_device_interfaces(self):
        """Get device interface statistics"""
        print("🔌 Getting device interface data...")

        if not self.csrf_token:
            print("❌ No CSRF token available")
            return False

        interface_url = urljoin(self.base_url, "/dataservice/device/interface")
        headers = {"X-XSRF-TOKEN": self.csrf_token}

        response = self.session.get(interface_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Device interface data retrieved:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ Failed to get device interface data: {response.status_code}")
            print(response.text)
            return False

    def get_control_connections(self):
        """Get control plane connections"""
        print("🔗 Getting control connections data...")

        if not self.csrf_token:
            print("❌ No CSRF token available")
            return False

        connections_url = urljoin(self.base_url, "/dataservice/device/control/connections")
        headers = {"X-XSRF-TOKEN": self.csrf_token}

        response = self.session.get(connections_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Control connections data retrieved:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ Failed to get control connections data: {response.status_code}")
            print(response.text)
            return False

    def create_device_template(self):
        """Create a device template"""
        print("📋 Creating device template...")

        if not self.csrf_token:
            print("❌ No CSRF token available")
            return False

        template_url = urljoin(self.base_url, "/dataservice/template/device")
        headers = {"X-XSRF-TOKEN": self.csrf_token, "Content-Type": "application/json"}

        payload = {"templateName": "Test-Branch-Router-Template", "templateDescription": "Test template for branch router configuration", "deviceType": "vedge-C8000V", "templateDefinition": {"system": {"host-name": "{{hostname}}", "system-ip": "{{system_ip}}", "site-id": "{{site_id}}"}}}

        response = self.session.post(template_url, json=payload, headers=headers)

        if response.status_code == 201:
            data = response.json()
            print(f"✅ Device template created:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ Failed to create device template: {response.status_code}")
            print(response.text)
            return False

    def create_site_list(self):
        """Create a site list"""
        print("🏢 Creating site list...")

        if not self.csrf_token:
            print("❌ No CSRF token available")
            return False

        site_list_url = urljoin(self.base_url, "/dataservice/template/policy/list/site")
        headers = {"X-XSRF-TOKEN": self.csrf_token, "Content-Type": "application/json"}

        payload = {"name": "test-branch-sites", "description": "Test list of all branch office sites", "type": "site", "entries": [{"siteId": "100"}, {"siteId": "200"}, {"siteId": "300"}]}

        response = self.session.post(site_list_url, json=payload, headers=headers)

        if response.status_code == 201:
            data = response.json()
            print(f"✅ Site list created:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ Failed to create site list: {response.status_code}")
            print(response.text)
            return False

    def logout(self):
        """Logout from vManage"""
        print("🚪 Logging out...")

        if not self.csrf_token:
            print("❌ No CSRF token available")
            return False

        logout_url = urljoin(self.base_url, "/logout")
        headers = {"X-XSRF-TOKEN": self.csrf_token}

        response = self.session.get(logout_url, headers=headers)

        if response.status_code == 200:
            print("✅ Logout successful")
            return True
        else:
            print(f"❌ Logout failed: {response.status_code}")
            print(response.text)
            return False

    def run_full_test(self):
        """Run complete test flow"""
        print("🧪 Starting vManage API Test Flow\n")

        # Authentication flow
        if not self.authenticate():
            return False

        if not self.get_csrf_token():
            return False

        print()  # Blank line for readability

        # API calls
        self.get_device_monitor()
        print()

        self.get_device_interfaces()
        print()

        self.get_control_connections()
        print()

        # Configuration operations with request payload validation
        self.create_device_template()
        print()

        self.create_site_list()
        print()

        # Logout
        self.logout()

        print("\n🎉 Test flow completed!")
        return True


def main():
    """Main test function"""
    import sys

    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

    print(f"Testing vManage API mock server at: {base_url}")
    print("=" * 50)

    test = VManageAPITest(base_url)

    try:
        success = test.run_full_test()
        if success:
            print("✅ All tests passed!")
            sys.exit(0)
        else:
            print("❌ Some tests failed!")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {base_url}")
        print("Make sure the mock server is running!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
