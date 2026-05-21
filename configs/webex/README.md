# Webex Messaging API Mock

Mock profile simulating the [Cisco Webex REST API](https://developer.webex.com/docs/api/getting-started) for Rooms and Memberships workflows. Built on Mock-and-Roll with Redis persistence for stateful CRUD operations.

## Prerequisites

- Mock-and-Roll installed and configured
- Redis running (required — `api.json` sets `"persistence": "redis"`)
- Python 3.10+

## Quick Start

```bash
# Start with mockctl
mockctl start --config webex

# Or set environment variable and run directly
export MOCK_CONFIG_FOLDER=configs/webex
python src/main.py
```

The server starts at `http://127.0.0.1:8000/v1` (root_path is `/v1`).

## Authentication

### User Authentication (OIDC Bearer Token)

All API endpoints require a valid Bearer token in the `Authorization` header:

```
Authorization: Bearer YzBjZGFhNWItMDMzMS00YmZlLTlkOGQtZmEwNGQyZDA3YWM3MDI4MGFiNTUtNTAw_P0A1_2a4eb71b-e09c-477b-9c88-ddafe36bae8b
```

Auth method name: `oidc_auth_code` (configured in `auth.json`)

### System API Key

Protected system endpoints (logs, config reload, etc.) require:

```
X-API-Key: webex-system-admin-key-123
```

## Endpoints

| Method | Path | Name | Description |
|--------|------|------|-------------|
| GET | `/v1/rooms` | List Rooms | List all rooms |
| GET | `/v1/rooms/{room_id}` | Get Room Details | Retrieve a specific room |
| POST | `/v1/rooms` | Create Room | Create a new room |
| DELETE | `/v1/rooms/{roomId}` | Delete a Room | Delete an existing room |
| GET | `/v1/memberships?roomId={id}` | List Memberships | List members of a room |
| POST | `/v1/memberships` | Create a Membership | Add a member to a room |
| DELETE | `/v1/memberships/{membershipId}` | Delete a Membership | Remove a member from a room |

---

## Working Scenarios

### a. List Rooms

**Request:**
```
GET /v1/rooms
Authorization: Bearer {ACCESS_TOKEN}
```

**Response:** `200 OK`
```json
{
    "items": [
        {
            "id": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vMzk5ZWE4ZTAtM2YwZC0xMWYxLWE4NjQtNTM5NjdjZTYyMjkw",
            "title": "Cisco-Devnet",
            "type": "group",
            "isLocked": false,
            "lastActivity": "2026-04-23T12:09:05.902Z",
            "creatorId": "Y2lzY29zcGFyazovL3VzL1BFT1BMRS8zNWE4ZDlhNS1jYzA2LTQ4MDQtYTdhYi0yMGZmMDNhMWJhNGQ",
            "created": "2026-04-23T12:09:05.902Z",
            "ownerId": "Y2lzY29zcGFyazovL3VzL09SR0FOSVpBVElPTi8yYTRlYjcxYi1lMDljLTQ3N2ItOWM4OC1kZGFmZTM2YmFlOGI",
            "description": "Internal team with members",
            "isPublic": false,
            "isReadOnly": false
        }
    ]
}
```

### b. Get Room Details

**Request:**
```
GET /v1/rooms/{room_id}
Authorization: Bearer {ACCESS_TOKEN}
```

**Response (found):** `200 OK` — returns the room object from persistence.

**Response (not found):** `404 Not Found`
```json
{
    "message": "The requested resource could not be found.",
    "errors": [
        { "description": "The requested resource could not be found." }
    ],
    "trackingId": "ROUTERGW_5c5523e7-e936-4f9c-81c1-a7bcb6bb8fd1"
}
```

### c. Create Room

**Request:**
```
POST /v1/rooms
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json

{
    "title": "Cisco-Devnet",
    "description": "Internal team with members"
}
```

**Response:** `200 OK`
```json
{
    "id": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vMDFlNTQ3YjAtM2YyMS0xMWYxLWFkZWMtYWQ0MzIwYzRlMjcw",
    "title": "Cisco-Devnet",
    "type": "group",
    "isLocked": false,
    "lastActivity": "2026-04-23T14:30:42.347Z",
    "creatorId": "Y2lzY29zcGFyazovL3VzL1BFT1BMRS8zNWE4ZDlhNS1jYzA2LTQ4MDQtYTdhYi0yMGZmMDNhMWJhNGQ",
    "created": "2026-04-23T14:30:42.347Z",
    "ownerId": "Y2lzY29zcGFyazovL3VzL09SR0FOSVpBVElPTi8yYTRlYjcxYi1lMDljLTQ3N2ItOWM4OC1kZGFmZTM2YmFlOGI",
    "description": "Internal team with members",
    "isPublic": false
}
```

### d. Delete a Room

**Request:**
```
DELETE /v1/rooms/{roomId}
Authorization: Bearer {ACCESS_TOKEN}
```

**Response (success):** `204 No Content`

**Response (not found):** `404 Not Found`
```json
{
    "message": "The requested resource could not be found.",
    "errors": [
        { "description": "The requested resource could not be found." }
    ],
    "trackingId": "ROUTERGW_a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### e. List Memberships

**Request:**
```
GET /v1/memberships?roomId={room_id}
Authorization: Bearer {ACCESS_TOKEN}
```

**Response:** `200 OK`
```json
{
    "items": [
        {
            "id": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL01FTUJFUlNISVAvMzQxMDUzODUtMjY4Ny00MTI5LWE3NzQtYmIzZTgxYjEyOWIyOjM5OWVhOGUwLTNmMGQtMTFmMS1hODY0LTUzOTY3Y2U2MjI5MA",
            "roomId": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vMzk5ZWE4ZTAtM2YwZC0xMWYxLWE4NjQtNTM5NjdjZTYyMjkw",
            "roomType": "group",
            "personId": "Y2lzY29zcGFyazovL3VzL1BFT1BMRS8zNDEwNTM4NS0yNjg3LTQxMjktYTc3NC1iYjNlODFiMTI5YjI",
            "personEmail": "aytac125@gmail.com",
            "personDisplayName": "aytac125",
            "personOrgId": "Y2lzY29zcGFyazovL3VzL09SR0FOSVpBVElPTi85Njc2ZDM4YS04OTIyLTQ1MzUtYmE4Zi0yZjRjODk3MzVmZDQ",
            "isModerator": false,
            "isMonitor": false,
            "created": "2026-04-23T12:15:30.856Z"
        }
    ]
}
```

### f. Create a Membership (Add Room Member)

**Request:**
```
POST /v1/memberships
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json

{
    "roomId": "{room_id}",
    "personEmail": "aytac125@gmail.com",
    "isModerator": false
}
```

**Response:** `200 OK`
```json
{
    "id": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL01FTUJFUlNISVAvMmNkMzI5MGItOGQwNC00MjY2LWIyZjYtMDVlMmY1NTQzY2IwOjM5OWVhOGUwLTNmMGQtMTFmMS1hODY0LTUzOTY3Y2U2MjI5MA",
    "roomId": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vMzk5ZWE4ZTAtM2YwZC0xMWYxLWE4NjQtNTM5NjdjZTYyMjkw",
    "roomType": "group",
    "personId": "Y2lzY29zcGFyazovL3VzL1BFT1BMRS8yY2QzMjkwYi04ZDA0LTQyNjYtYjJmNi0wNWUyZjU1NDNjYjA",
    "personEmail": "aytac125@gmail.com",
    "personDisplayName": "aytacyu",
    "personOrgId": "Y2lzY29zcGFyazovL3VzL09SR0FOSVpBVElPTi8xOGY3ZWVmYS1iOTZkLTQwZTQtOTYzYi04NTM0MmQ2YjIxZGI",
    "isModerator": false,
    "isMonitor": false,
    "isRoomHidden": false,
    "created": "2026-04-23T14:34:23.782Z"
}
```

### g. Delete a Membership

**Request:**
```
DELETE /v1/memberships/{membershipId}
Authorization: Bearer {ACCESS_TOKEN}
```

**Response (success):** `204 No Content`

**Response (not found):** `404 Not Found`
```json
{
    "message": "The requested resource could not be found.",
    "errors": [
        { "description": "The requested resource could not be found." }
    ],
    "trackingId": "ROUTERGW_b2c3d4e5-f6a7-8901-bcde-f12345678901"
}
```

---

## Error Scenarios

### 1. Authentication Errors (All Endpoints)

#### Missing Token

```
ANY /v1/...
(no Authorization header)
```

**Response:** `401 Unauthorized`
```json
{
    "message": "The request requires a valid access token set in the Authorization request header.",
    "errors": [
        { "description": "The request requires a valid access token set in the Authorization request header." }
    ],
    "trackingId": "ROUTERGW_175a83ac-a7b9-457d-b690-a36aabcab3d8"
}
```

#### Invalid Token

```
ANY /v1/...
Authorization: Bearer INVALID_TOKEN
```

**Response:** `401 Unauthorized`
```json
{
    "message": "The request requires a valid access token set in the Authorization request header.",
    "errors": [
        { "description": "The request requires a valid access token set in the Authorization request header." }
    ],
    "trackingId": "ROUTERGW_27dce605-d127-4cdf-abec-a5e3a7c9bb31"
}
```

#### Wrong Content-Type (POST Endpoints)

Applies to POST endpoints that have `required_headers` configured with `Content-Type: application/json`.

```
POST /v1/rooms
Content-Type: text/plain
```

**Response:** `400 Bad Request`
```json
{
    "message": "The request could not be understood by the server due to malformed syntax.",
    "errors": [
        { "description": "The request could not be understood by the server due to malformed syntax." }
    ],
    "trackingId": "ROUTERGW_211cbafa-4f75-4ff6-be94-874135b723d9"
}
```

### 2. Room Errors

#### Missing Title on Create

```
POST /v1/rooms
Content-Type: application/json

{ "description": "Internal team with members" }
```

**Response:** `400 Bad Request`
```json
{
    "message": "Title cannot be empty.",
    "errors": [
        { "description": "Title cannot be empty." }
    ],
    "trackingId": "ROUTERGW_18f6c1f3-2622-4d71-b081-5aa2b2c79a21"
}
```

### 3. Membership Errors

#### Member Already Exists

When adding `aytac125@gmail.com` to the default seeded room:

**Response:** `409 Conflict`
```json
{
    "message": "User is already a participant in the room.",
    "errors": [
        { "description": "User is already a participant in the room." }
    ],
    "trackingId": "ROUTERGW_7846d88e-9578-4c9a-a42e-5d83e77dc0c9"
}
```

#### Invalid Email (Missing @ Symbol)

When `personEmail` has no `@` (e.g., `aytac125gmail.com`):

**Response:** `404 Not Found`
```json
{
    "message": "The requested resource could not be found.",
    "errors": [
        { "description": "The requested resource could not be found." }
    ],
    "trackingId": "ROUTERGW_4f743a39-0b28-4538-9704-e3eee6357eb1"
}
```

---

## Configuration Files

| File | Purpose |
|------|---------|
| `api.json` | Server metadata, root path (`/v1`), Redis persistence, logging, swagger UI settings |
| `auth.json` | OIDC bearer token and system API key definitions |
| `endpoints.json` | All endpoint definitions with conditional responses and persistence actions |

## Notes

- All responses use template variable `{{timestamp}}` for dynamic date fields.
- Persistence is Redis-backed — rooms and memberships created via POST are stored and returned in subsequent GET/LIST calls.
- The `merge_with_static_response` flag ensures static seed data is always included alongside persisted entities.
- Memberships support `filter_by_query_params` on `roomId` to scope listings to a specific room.
