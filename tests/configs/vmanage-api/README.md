# vManage API Mock Configuration

This configuration has been updated to support Cisco SD-WAN vManage API endpoints based on the Postman collection in `tests/data/SD-WAN-API Requests.postman.json`.

## Key Features Added

### 1. Request Body Schema Validation
- **JSON Schema Support**: All POST endpoints include comprehensive `request_body_schema` definitions
- **Swagger Documentation**: Schemas are automatically included in the OpenAPI/Swagger UI
- **Payload Validation**: Request bodies are validated against the defined schemas
- **Form Data Support**: Authentication endpoint supports `application/x-www-form-urlencoded`

### 2. Custom Headers Support
- **Response Headers**: Endpoints can now return custom headers in responses
- **Required Headers**: Endpoints can validate required headers in requests (e.g., X-XSRF-TOKEN)
- **Authentication Headers**: Support for session-based authentication with CSRF tokens

### 3. vManage Authentication
Added `vmanage_session` authentication method in `auth.json`:
- Session-based authentication using JSESSIONID cookie
- CSRF token validation via X-XSRF-TOKEN header
- Multiple valid session/token combinations for testing

### 4. SD-WAN API Endpoints

#### Authentication Endpoints
- `POST /j_security_check` - User authentication with form data validation
- `GET /dataservice/client/token` - Get CSRF token
- `GET /logout` - User logout

#### Device Management Endpoints  
- `GET /dataservice/device/monitor` - Get device status information
- `GET /dataservice/device/interface` - Get device interface statistics
- `GET /dataservice/device/control/connections` - Get control plane connections

#### Configuration Management Endpoints
- `POST /dataservice/template/device` - Create device template with schema validation
- `POST /dataservice/template/device/config/attachfeature` - Attach devices to template
- `POST /dataservice/template/policy/list/site` - Create site list

## Configuration Structure Changes

### endpoints.json with Request Schemas
```json
{
  "name": "Endpoint Name",
  "method": "POST",
  "path": "/api/path",
  "authentication": ["vmanage_session"],
  "required_headers": {
    "X-XSRF-TOKEN": "expected-value"
  },
  "request_headers": {
    "Content-Type": "application/json"
  },
  "request_body_schema": {
    "type": "object",
    "properties": {
      "field1": {
        "type": "string",
        "description": "Field description",
        "example": "example-value"
      }
    },
    "required": ["field1"],
    "additionalProperties": false
  },
  "responses": [
    {
      "body_conditions": {...},
      "response": {
        "status_code": 200,
        "headers": {
          "Content-Type": "application/json",
          "X-Custom-Header": "value"
        },
        "body": {...}
      }
    }
  ]
}
```

### auth.json
```json
{
  "authentication_methods": {
    "vmanage_session": {
      "type": "session_based",
      "session_cookie": "JSESSIONID",
      "csrf_token_header": "X-XSRF-TOKEN",
      "valid_sessions": [
        {
          "session_id": "session-id",
          "csrf_token": "token-value",
          "username": "admin"
        }
      ]
    }
  }
}
```

## Request Body Schema Validation

The configuration now includes comprehensive request body schemas for all POST endpoints:

### Authentication Schema
- Validates `j_username` and `j_password` fields
- Supports form-urlencoded content type
- Required fields validation

### Device Template Schema
- Template name and description validation
- Device type enumeration
- Template definition structure validation
- Nested object validation for system properties

### Site List Schema
- Site list name and type validation
- Entries array with site ID validation
- Strict schema with no additional properties

## Usage Example

1. **Authenticate**: POST to `/j_security_check` with form data
   ```bash
   curl -X POST -d "j_username=admin&j_password=admin" /j_security_check
   ```

2. **Get Token**: GET `/dataservice/client/token` with session cookie
3. **Create Template**: POST with JSON payload to `/dataservice/template/device`
4. **API Calls**: Use session cookie + X-XSRF-TOKEN header for authenticated endpoints
5. **Logout**: GET `/logout` with session cookie + X-XSRF-TOKEN header

## Mock Server Code Changes

### Added Features in main.py
- `check_required_headers()` function for header validation
- Support for `headers` field in response configuration
- Support for `required_headers` field in endpoint configuration
- Enhanced request body parsing for form-urlencoded data
- Header validation integrated into both request handlers

### Request Body Parsing
- Automatic detection of content-type
- Support for `application/x-www-form-urlencoded`
- Support for `application/json`
- Schema validation using existing schema infrastructure

### Response Headers
All JSONResponse objects now support custom headers from the configuration.

### Header Validation
Required headers are validated before processing requests, returning 400 error if missing or incorrect.

## Testing

The configuration supports realistic SD-WAN API testing scenarios including:
- Authentication flows with form data
- Session management  
- Device monitoring
- Interface statistics
- Control plane status
- Configuration management with schema validation

### Test Scripts
- `test_vmanage_api.py` - Python test script with all endpoints
- `test_vmanage_api.sh` - Bash script with curl commands
- Both scripts test request payload validation

### Swagger Documentation
Visit `/docs` when the server is running to see:
- Complete API documentation
- Interactive request/response examples
- Schema validation in the Swagger UI
- Try-it-out functionality with schema validation

This allows for comprehensive testing of SD-WAN applications against a mock vManage API with full request/response validation.
