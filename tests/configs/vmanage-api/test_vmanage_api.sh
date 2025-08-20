#!/bin/bash

# vManage API Mock Server Test Script
# This script tests the vManage API endpoints using curl with comprehensive authentication testing

set -e  # Exit on any error

# Configuration
BASE_URL=# Test 14: Device Monitor endpoint
echo "Test 14: Get device monitor data with authentication"
response=$(curl -s -w "%{http_code}" 
    -b "$COOKIE_JAR" 
    -H "X-XSRF-TOKEN: $csrf_token" 
    "$BASE_URL/dataservice/device/monitor")
status_code="${response: -3}"
monitor_data="${response%???}"
run_test "Device monitor endpoint" "200" "$status_code"
if [[ "$status_code" == "200" ]]; then
    echo "   Sample data: $(echo "$monitor_data" | jq -r '.data[0].hostname // "No data"' 2>/dev/null || echo "Raw response")"
fi

# Test 15: Device Interface Statistics endpoint  
echo "Test 15: Get device interface statistics"
response=$(curl -s -w "%{http_code}" 
    -b "$COOKIE_JAR" 
    -H "X-XSRF-TOKEN: $csrf_token" 
    "$BASE_URL/dataservice/device/interface")
status_code="${response: -3}"
interface_data="${response%???}"
run_test "Device interface endpoint" "200" "$status_code"

# Test 16: Device Control Connections endpoint
echo "Test 16: Get device control connections"
response=$(curl -s -w "%{http_code}" 
    -b "$COOKIE_JAR" 
    -H "X-XSRF-TOKEN: $csrf_token" 
    "$BASE_URL/dataservice/device/control/connections")
status_code="${response: -3}"
connections_data="${response%???}"
run_test "Control connections endpoint" "200" "$status_code"

# Test 17: Create Device Template endpoint
echo "Test 17: Create device template"
template_payload='{
    "templateName": "Test-Auth-Branch-Router-Template",
    "templateDescription": "Authentication test template for branch router configuration",
    "deviceType": "vedge-C8000V",
    "templateDefinition": {
        "system": {
            "host-name": "{{hostname}}",
            "system-ip": "{{system_ip}}",
            "site-id": "{{site_id}}"
        }
    }
}'
response=$(curl -s -w "%{http_code}" 
    -b "$COOKIE_JAR" 
    -H "X-XSRF-TOKEN: $csrf_token" 
    -H "Content-Type: application/json" 
    -d "$template_payload" 
    "$BASE_URL/dataservice/template/device")
status_code="${response: -3}"
template_data="${response%???}"
run_test "Create device template" "201" "$status_code"

# Test 18: Attach Device to Template endpoint
echo "Test 18: Attach device to template"
attach_payload='{
    "templateId": "template-12345",
    "devices": [
        {
            "deviceId": "C8K-001",
            "variables": {
                "hostname": "branch-router-001",
                "system_ip": "1.1.1.1", 
                "site_id": "100"
            }
        }
    ]
}'
response=$(curl -s -w "%{http_code}" 
    -b "$COOKIE_JAR" 
    -H "X-XSRF-TOKEN: $csrf_token" 
    -H "Content-Type: application/json" 
    -d "$attach_payload" 
    "$BASE_URL/dataservice/template/device/config/attachfeature")
status_code="${response: -3}"
attach_data="${response%???}"
run_test "Attach device to template" "200" "$status_code"

# Test 19: Create Site List endpoint
echo "Test 19: Create site list"
site_list_payload='{
    "name": "test-auth-branch-sites",
    "description": "Authentication test list of all branch office sites",
    "type": "site",
    "entries": [
        {"siteId": "100"},
        {"siteId": "200"},
        {"siteId": "300"}
    ]
}'
response=$(curl -s -w "%{http_code}" 
    -b "$COOKIE_JAR" 
    -H "X-XSRF-TOKEN: $csrf_token" 
    -H "Content-Type: application/json" 
    -d "$site_list_payload" 
    "$BASE_URL/dataservice/template/policy/list/site")
status_code="${response: -3}"
site_list_data="${response%???}"
run_test "Create site list" "201" "$status_code"

echo
echo -e "${BLUE}🔓 SECTION 5: Alternative Authentication Methods${NC}"
echo "Testing other authentication methods from auth.json"
echo

# Test 20: API Key authentication (if supported by any endpoints)
echo "Test 20: API Key authentication test"
response=$(curl -s -w "%{http_code}" 
    -H "X-API-Key: demo-api-key-123" 
    "$BASE_URL/dataservice/device/monitor")
status_code="${response: -3}"
response_body="${response%???}"
# This should still fail since vManage endpoints require session+CSRF specifically
run_test "API Key auth on vManage endpoint should fail" "401" "$status_code"

# Test 21: Basic Authentication test
echo "Test 21: Basic Authentication test"
response=$(curl -s -w "%{http_code}" 
    -u "admin:secret123" 
    "$BASE_URL/dataservice/device/monitor")
status_code="${response: -3}"
response_body="${response%???}"
# This should still fail since vManage endpoints require session+CSRF specifically
run_test "Basic auth on vManage endpoint should fail" "401" "$status_code"

# Test 22: Bearer Token test
echo "Test 22: Bearer Token test"
response=$(curl -s -w "%{http_code}" 
    -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.demo-token" 
    "$BASE_URL/dataservice/device/monitor")
status_code="${response: -3}"
response_body="${response%???}"
# This should still fail since vManage endpoints require session+CSRF specifically
run_test "Bearer token on vManage endpoint should fail" "401" "$status_code"

echo
echo -e "${BLUE}🚪 SECTION 6: Session Termination${NC}"
echo "Testing logout functionality"
echohost:8000}"
COOKIE_JAR="/tmp/vmanage_cookies.txt"
USERNAME="admin"
PASSWORD="admin"

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🧪 Testing vManage API Mock Server at: $BASE_URL"
echo "📋 Comprehensive Authentication & Endpoint Testing"
echo "=" | tr '=' '=' | head -c 80 && echo

# Test helper functions
run_test() {
    local test_name="$1"
    local expected_status="$2"
    local actual_status="$3"
    local response_body="$4"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [[ "$actual_status" == "$expected_status" ]]; then
        echo -e "✅ ${GREEN}PASS${NC}: $test_name (Status: $actual_status)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "❌ ${RED}FAIL${NC}: $test_name (Expected: $expected_status, Got: $actual_status)"
        if [[ -n "$response_body" ]]; then
            echo -e "   ${YELLOW}Response:${NC} $response_body"
        fi
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Clean up any existing cookie jar
rm -f "$COOKIE_JAR"

echo
echo -e "${BLUE}� SECTION 1: Authentication Validation Tests${NC}"
echo "Testing various authentication scenarios against auth.json configuration"
echo

# Test 1: No authentication should fail
echo "Test 1: No authentication provided"
response=$(curl -s -w "%{http_code}" "$BASE_URL/dataservice/device/monitor")
status_code="${response: -3}"
response_body="${response%???}"
run_test "No auth should fail" "401" "$status_code" "$response_body"

# Test 2: Only session cookie (should fail - need both session + CSRF)
echo "Test 2: Only session cookie (missing CSRF token)"
response=$(curl -s -w "%{http_code}" \
    -H "Cookie: JSESSIONID=vmanage-session-123" \
    "$BASE_URL/dataservice/device/monitor")
status_code="${response: -3}"
response_body="${response%???}"
run_test "Session only should fail" "401" "$status_code" "$response_body"

# Test 3: Only CSRF token (should fail - need both session + CSRF)
echo "Test 3: Only CSRF token (missing session)"
response=$(curl -s -w "%{http_code}" \
    -H "X-XSRF-TOKEN: mock-csrf-token-456" \
    "$BASE_URL/dataservice/device/monitor")
status_code="${response: -3}"
response_body="${response%???}"
run_test "CSRF only should fail" "401" "$status_code" "$response_body"

# Test 4: Invalid session cookie
echo "Test 4: Invalid session cookie"
response=$(curl -s -w "%{http_code}" \
    -H "Cookie: JSESSIONID=invalid-session" \
    -H "X-XSRF-TOKEN: mock-csrf-token-456" \
    "$BASE_URL/dataservice/device/monitor")
status_code="${response: -3}"
response_body="${response%???}"
run_test "Invalid session should fail" "401" "$status_code" "$response_body"

# Test 5: Invalid CSRF token
echo "Test 5: Invalid CSRF token"
response=$(curl -s -w "%{http_code}" \
    -H "Cookie: JSESSIONID=vmanage-session-123" \
    -H "X-XSRF-TOKEN: invalid-csrf-token" \
    "$BASE_URL/dataservice/device/monitor")
status_code="${response: -3}"
response_body="${response%???}"
run_test "Invalid CSRF should fail" "401" "$status_code" "$response_body"

# Test 6: Valid session + CSRF combination #1
echo "Test 6: Valid vManage session authentication (admin user)"
response=$(curl -s -w "%{http_code}" \
    -H "Cookie: JSESSIONID=vmanage-session-123" \
    -H "X-XSRF-TOKEN: mock-csrf-token-456" \
    "$BASE_URL/dataservice/device/monitor")
status_code="${response: -3}"
response_body="${response%???}"
run_test "Valid session+CSRF #1" "200" "$status_code"

# Test 7: Valid session + CSRF combination #2
echo "Test 7: Valid vManage session authentication (operator user)"
response=$(curl -s -w "%{http_code}" \
    -H "Cookie: JSESSIONID=vmanage-session-789" \
    -H "X-XSRF-TOKEN: mock-csrf-token-abc" \
    "$BASE_URL/dataservice/device/monitor")
status_code="${response: -3}"
response_body="${response%???}"
run_test "Valid session+CSRF #2" "200" "$status_code"

# Test 8: Alternative valid CSRF tokens
echo "Test 8: Alternative valid CSRF token"
response=$(curl -s -w "%{http_code}" \
    -H "Cookie: JSESSIONID=vmanage-session-123" \
    -H "X-XSRF-TOKEN: test-csrf-token-123" \
    "$BASE_URL/dataservice/device/monitor")
status_code="${response: -3}"
response_body="${response%???}"
run_test "Alternative CSRF token" "200" "$status_code"

echo
echo -e "${BLUE}🔐 SECTION 2: Login Flow Testing${NC}"
echo "Testing the j_security_check endpoint and session establishment"
echo

# Test 9: Valid login with correct credentials
echo "Test 9: Valid login with admin/admin credentials"
response=$(curl -s -w "%{http_code}" \
    -c "$COOKIE_JAR" \
    -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "j_username=$USERNAME&j_password=$PASSWORD" \
    "$BASE_URL/j_security_check")
status_code="${response: -3}"
response_body="${response%???}"
run_test "Valid login" "200" "$status_code"

# Test 10: Invalid login credentials
echo "Test 10: Invalid login credentials"
response=$(curl -s -w "%{http_code}" \
    -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "j_username=invalid&j_password=invalid" \
    "$BASE_URL/j_security_check")
status_code="${response: -3}"
response_body="${response%???}"
run_test "Invalid login should fail" "401" "$status_code"

# Test 11: Missing login parameters
echo "Test 11: Missing login parameters"
response=$(curl -s -w "%{http_code}" \
    -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "j_username=admin" \
    "$BASE_URL/j_security_check")
status_code="${response: -3}"
response_body="${response%???}"
run_test "Missing password should fail" "422" "$status_code"

echo
echo -e "${BLUE}🎫 SECTION 3: CSRF Token Endpoint Testing${NC}"
echo "Testing token retrieval and validation"
echo

# Test 12: Get CSRF token with valid session
echo "Test 12: Get CSRF token with valid session"
response=$(curl -s -w "%{http_code}" \
    -b "$COOKIE_JAR" \
    "$BASE_URL/dataservice/client/token")
status_code="${response: -3}"
csrf_token="${response%???}"
run_test "Get CSRF token" "200" "$status_code"

# Remove quotes if present in token
csrf_token=$(echo "$csrf_token" | tr -d '"')
echo "   Retrieved token: $csrf_token"

# Test 13: Get CSRF token without session (should still work as it's a public endpoint)
echo "Test 13: Get CSRF token without session"
response=$(curl -s -w "%{http_code}" \
    "$BASE_URL/dataservice/client/token")
status_code="${response: -3}"
response_body="${response%???}"
run_test "Get CSRF token without session" "200" "$status_code"

echo
echo -e "${BLUE}📊 SECTION 4: Protected Endpoint Testing${NC}"
echo "Testing all vManage API endpoints with proper authentication"
echo

echo
echo "📊 Step 3: Getting device monitor data..."
monitor_response=$(curl -s -w "%{http_code}" \
    -b "$COOKIE_JAR" \
    -H "X-XSRF-TOKEN: $csrf_token" \
    "$BASE_URL/dataservice/device/monitor")

status_code="${monitor_response: -3}"
monitor_data="${monitor_response%???}"

if [[ "$status_code" == "200" ]]; then
    echo "✅ Device monitor data retrieved:"
    echo "$monitor_data" | jq . 2>/dev/null || echo "$monitor_data"
else
    echo "❌ Failed to get device monitor data: $status_code"
    echo "$monitor_data"
fi

echo
echo "🔌 Step 4: Getting device interface data..."
interface_response=$(curl -s -w "%{http_code}" \
    -b "$COOKIE_JAR" \
    -H "X-XSRF-TOKEN: $csrf_token" \
    "$BASE_URL/dataservice/device/interface")

status_code="${interface_response: -3}"
interface_data="${interface_response%???}"

if [[ "$status_code" == "200" ]]; then
    echo "✅ Device interface data retrieved:"
    echo "$interface_data" | jq . 2>/dev/null || echo "$interface_data"
else
    echo "❌ Failed to get device interface data: $status_code"
    echo "$interface_data"
fi

echo
echo "🔗 Step 5: Getting control connections data..."
connections_response=$(curl -s -w "%{http_code}" \
    -b "$COOKIE_JAR" \
    -H "X-XSRF-TOKEN: $csrf_token" \
    "$BASE_URL/dataservice/device/control/connections")

status_code="${connections_response: -3}"
connections_data="${connections_response%???}"

if [[ "$status_code" == "200" ]]; then
    echo "✅ Control connections data retrieved:"
    echo "$connections_data" | jq . 2>/dev/null || echo "$connections_data"
else
    echo "❌ Failed to get control connections data: $status_code"
    echo "$connections_data"
fi

echo
echo "� Step 6: Creating device template..."
template_payload='{
    "templateName": "Test-Branch-Router-Template",
    "templateDescription": "Test template for branch router configuration",
    "deviceType": "vedge-C8000V",
    "templateDefinition": {
        "system": {
            "host-name": "{{hostname}}",
            "system-ip": "{{system_ip}}",
            "site-id": "{{site_id}}"
        }
    }
}'

template_response=$(curl -s -w "%{http_code}" \
    -b "$COOKIE_JAR" \
    -H "X-XSRF-TOKEN: $csrf_token" \
    -H "Content-Type: application/json" \
    -d "$template_payload" \
    "$BASE_URL/dataservice/template/device")

status_code="${template_response: -3}"
template_data="${template_response%???}"

if [[ "$status_code" == "201" ]]; then
    echo "✅ Device template created:"
    echo "$template_data" | jq . 2>/dev/null || echo "$template_data"
else
    echo "❌ Failed to create device template: $status_code"
    echo "$template_data"
fi

echo
echo "🏢 Step 7: Creating site list..."
site_list_payload='{
    "name": "test-branch-sites",
    "description": "Test list of all branch office sites",
    "type": "site",
    "entries": [
        {"siteId": "100"},
        {"siteId": "200"},
        {"siteId": "300"}
    ]
}'

site_list_response=$(curl -s -w "%{http_code}" \
    -b "$COOKIE_JAR" \
    -H "X-XSRF-TOKEN: $csrf_token" \
    -H "Content-Type: application/json" \
    -d "$site_list_payload" \
    "$BASE_URL/dataservice/template/policy/list/site")

status_code="${site_list_response: -3}"
site_list_data="${site_list_response%???}"

if [[ "$status_code" == "201" ]]; then
    echo "✅ Site list created:"
    echo "$site_list_data" | jq . 2>/dev/null || echo "$site_list_data"
else
    echo "❌ Failed to create site list: $status_code"
    echo "$site_list_data"
fi

echo
echo "�🚪 Step 8: Logging out..."
logout_response=$(curl -s -w "%{http_code}" \
    -b "$COOKIE_JAR" \
    -H "X-XSRF-TOKEN: $csrf_token" \
    "$BASE_URL/logout")

status_code="${logout_response: -3}"
logout_data="${logout_response%???}"

if [[ "$status_code" == "200" ]]; then
    echo "✅ Logout successful"
    echo "$logout_data" | jq . 2>/dev/null || echo "$logout_data"
else
    echo "❌ Logout failed: $status_code"
    echo "$logout_data"
fi

# Test 23: Logout with valid session
echo "Test 23: Logout with authenticated session"
response=$(curl -s -w "%{http_code}" \
    -b "$COOKIE_JAR" \
    -H "X-XSRF-TOKEN: $csrf_token" \
    "$BASE_URL/logout")
status_code="${response: -3}"
logout_data="${response%???}"
run_test "Authenticated logout" "200" "$status_code"

# Test 24: Verify session is invalidated after logout
echo "Test 24: Verify session invalidated after logout"
response=$(curl -s -w "%{http_code}" \
    -b "$COOKIE_JAR" \
    -H "X-XSRF-TOKEN: $csrf_token" \
    "$BASE_URL/dataservice/device/monitor")
status_code="${response: -3}"
response_body="${response%???}"
run_test "Session should be invalid after logout" "401" "$status_code"

echo
echo -e "${BLUE}🔄 SECTION 7: Cross-Authentication Validation${NC}"
echo "Testing authentication boundaries and edge cases"
echo

# Test 25: Mixed valid/invalid credentials
echo "Test 25: Valid session + invalid CSRF token"
response=$(curl -s -w "%{http_code}" \
    -H "Cookie: JSESSIONID=vmanage-session-123" \
    -H "X-XSRF-TOKEN: totally-invalid-token" \
    "$BASE_URL/dataservice/device/monitor")
status_code="${response: -3}"
response_body="${response%???}"
run_test "Mixed credentials should fail" "401" "$status_code"

# Test 26: Case sensitivity test
echo "Test 26: Case sensitive authentication headers"
response=$(curl -s -w "%{http_code}" \
    -H "cookie: jsessionid=vmanage-session-123" \
    -H "x-xsrf-token: mock-csrf-token-456" \
    "$BASE_URL/dataservice/device/monitor")
status_code="${response: -3}"
response_body="${response%???}"
# Should fail due to case sensitivity
run_test "Case sensitive headers should fail" "401" "$status_code"

# Test 27: Multiple authentication methods (should only accept vManage specific)
echo "Test 27: Multiple auth methods provided"
response=$(curl -s -w "%{http_code}" \
    -H "Cookie: JSESSIONID=vmanage-session-123" \
    -H "X-XSRF-TOKEN: mock-csrf-token-456" \
    -H "X-API-Key: demo-api-key-123" \
    -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.demo-token" \
    -u "admin:secret123" \
    "$BASE_URL/dataservice/device/monitor")
status_code="${response: -3}"
response_body="${response%???}"
run_test "Multiple auth methods should succeed" "200" "$status_code"

echo
echo -e "${BLUE}📈 TEST SUMMARY${NC}"
echo "=" | tr '=' '=' | head -c 80 && echo
echo -e "Total Tests: ${BLUE}$TOTAL_TESTS${NC}"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"
echo

if [[ $FAILED_TESTS -eq 0 ]]; then
    echo -e "🎉 ${GREEN}ALL TESTS PASSED!${NC}"
    echo "✅ Authentication system is working correctly"
    echo "✅ All vManage API endpoints are properly secured"
    echo "✅ Session and CSRF token validation is enforced"
    exit_code=0
else
    echo -e "⚠️  ${YELLOW}SOME TESTS FAILED${NC}"
    echo "❌ Please review the failed test cases above"
    echo "🔍 Check authentication configuration in auth.json"
    echo "🔧 Verify endpoint security requirements in endpoints.json"
    exit_code=1
fi

# Clean up
rm -f "$COOKIE_JAR"

echo
echo "🧹 Cleanup completed"
echo "📋 Test execution finished"

exit $exit_code
