# Cookie-Licking Detector API Endpoints Guide

Complete documentation for all API endpoints with usage examples, request/response formats, and authentication requirements.

**Base URL**: `http://localhost:8000`  
**API Version**: `v1`  
**All API endpoints are prefixed with**: `/api/v1`

---

## Table of Contents

1. [System Endpoints](#system-endpoints)
2. [Authentication Endpoints](#authentication-endpoints)
3. [User Management Endpoints](#user-management-endpoints)
4. [Repository Endpoints](#repository-endpoints)
5. [Claims Endpoints](#claims-endpoints)
6. [Dashboard Endpoints](#dashboard-endpoints)
7. [Settings Endpoints](#settings-endpoints)
8. [Webhook Endpoints](#webhook-endpoints)
9. [Authentication Guide](#authentication-guide)
10. [Error Responses](#error-responses)

---

## System Endpoints

### 1. Root Endpoint
**GET** `/`

Returns API welcome message and version information.

**Authentication**: None required

**Example Request**:
```bash
curl http://localhost:8000/
```

**Example Response**:
```json
{
  "message": "Cookie-Licking Detector API",
  "version": "1.0.0",
  "status": "operational"
}
```

---

### 2. Health Check
**GET** `/health`

Returns detailed health status of all services including database, Redis, GitHub API, and system resources.

**Authentication**: None required

**Example Request**:
```bash
curl http://localhost:8000/health
```

**Example Response**:
```json
{
  "status": "healthy",
  "timestamp": 1762363694.2043352,
  "summary": {
    "total_checks": 5,
    "healthy_checks": 5,
    "critical_failures": 0,
    "optional_failures": 0,
    "message": "5/5 services healthy"
  },
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 5.21,
      "message": "Database connection successful"
    },
    "redis": {
      "status": "healthy",
      "response_time_ms": 3.04,
      "message": "Redis connection successful"
    },
    "system_resources": {
      "status": "healthy",
      "cpu_percent": 24.8,
      "memory_percent": 75.3,
      "disk_percent": 10.3
    },
    "github_api": {
      "status": "healthy",
      "response_time_ms": 222.13,
      "rate_limit_remaining": 50
    },
    "ecosystems_api": {
      "status": "healthy",
      "response_time_ms": 1546.34
    }
  }
}
```

**Use Cases**:
- Monitoring system health
- CI/CD health checks
- Load balancer health probes
- Debugging connectivity issues

---

### 3. Version Info
**GET** `/version`

Returns API version, build information, and environment details.

**Authentication**: None required

**Example Request**:
```bash
curl http://localhost:8000/version
```

**Example Response**:
```json
{
  "version": "1.0.0",
  "environment": "development",
  "build_date": "2025-11-05",
  "commit_hash": "abc123"
}
```

---

### 4. Metrics (Prometheus)
**GET** `/metrics`

Returns Prometheus-compatible metrics for monitoring and alerting.

**Authentication**: None required

**Example Request**:
```bash
curl http://localhost:8000/metrics
```

**Example Response**:
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/health",status="200"} 1234
...
```

**Use Cases**:
- Prometheus scraping
- Grafana dashboards
- Performance monitoring
- SLA tracking

---

### 5. API Documentation (Swagger)
**GET** `/docs`

Interactive Swagger UI documentation for testing API endpoints in the browser.

**Authentication**: None required

**Access**: Open `http://localhost:8000/docs` in your browser

**Features**:
- Interactive endpoint testing
- Request/response schemas
- Try-it-out functionality
- Authentication testing

---

### 6. API Documentation (ReDoc)
**GET** `/redoc`

Alternative API documentation with a clean, three-panel design.

**Authentication**: None required

**Access**: Open `http://localhost:8000/redoc` in your browser

**Features**:
- Clean, readable documentation
- Search functionality
- Downloadable OpenAPI spec
- Better for reading than testing

---

### 7. OpenAPI Specification
**GET** `/openapi.json`

Returns the OpenAPI 3.0 specification in JSON format.

**Authentication**: None required

**Example Request**:
```bash
curl http://localhost:8000/openapi.json > openapi.json
```

**Use Cases**:
- Code generation (client SDKs)
- API testing tools (Postman, Insomnia)
- Contract testing
- Documentation generation

---

## Authentication Endpoints

All authentication endpoints are under `/api/v1/auth`

### 1. Register User
**POST** `/api/v1/auth/register`

Creates a new user account.

**Authentication**: None required

**Request Body**:
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'
```

**Success Response** (201 Created):
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-11-05T12:00:00Z"
}
```

**Error Response** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

**Validation Rules**:
- Username: 3-50 characters, alphanumeric + underscore
- Email: Valid email format
- Password: Minimum 8 characters, requires uppercase, lowercase, number, special char
- Full name: Optional, max 255 characters

---

### 2. Login
**POST** `/api/v1/auth/login`

Authenticates a user and returns an access token.

**Authentication**: None required

**Request Body**:
```json
{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123!"
  }'
```

**Success Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe"
  }
}
```

**Error Response** (401 Unauthorized):
```json
{
  "detail": "Incorrect username or password"
}
```

**Use Cases**:
- Web application login
- Mobile app authentication
- CLI tool authentication
- API client authentication

---

### 3. Get Current User
**GET** `/api/v1/auth/me`

Returns the currently authenticated user's information.

**Authentication**: Required (Bearer token)

**Example Request**:
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false,
  "github_username": "johndoe",
  "created_at": "2025-11-05T12:00:00Z",
  "last_login": "2025-11-05T14:30:00Z"
}
```

**Error Response** (401 Unauthorized):
```json
{
  "detail": "Not authenticated"
}
```

---

### 4. List API Keys
**GET** `/api/v1/auth/api-keys`

Returns all API keys for the current user.

**Authentication**: Required (Bearer token)

**Example Request**:
```bash
curl http://localhost:8000/api/v1/auth/api-keys \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Success Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Production Key",
    "key_preview": "ck_prod_****3a2f",
    "created_at": "2025-11-05T12:00:00Z",
    "last_used_at": "2025-11-05T14:30:00Z",
    "expires_at": null,
    "is_active": true
  },
  {
    "id": 2,
    "name": "Development Key",
    "key_preview": "ck_dev_****9b4c",
    "created_at": "2025-11-04T10:00:00Z",
    "last_used_at": "2025-11-05T08:15:00Z",
    "expires_at": "2025-12-31T23:59:59Z",
    "is_active": true
  }
]
```

---

### 5. Create API Key
**POST** `/api/v1/auth/api-keys`

Creates a new API key for the current user.

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "name": "Production Key",
  "expires_in_days": 90,
  "scopes": ["repositories:read", "claims:read", "claims:write"]
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/api-keys \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Key",
    "expires_in_days": 90,
    "scopes": ["repositories:read", "claims:read"]
  }'
```

**Success Response** (201 Created):
```json
{
  "id": 3,
  "name": "Production Key",
  "api_key": "ck_prod_1a2b3c4d5e6f7g8h9i0j",
  "created_at": "2025-11-05T15:00:00Z",
  "expires_at": "2026-02-03T15:00:00Z",
  "message": "Store this API key securely. It will not be shown again."
}
```

**⚠️ Important**: The full API key is only returned once. Store it securely.

---

### 6. Logout
**POST** `/api/v1/auth/logout`

Invalidates the current access token.

**Authentication**: Required (Bearer token)

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Success Response** (200 OK):
```json
{
  "message": "Successfully logged out"
}
```

---

## User Management Endpoints

All user management endpoints are under `/api/v1/users`

### 1. Get Current User Profile
**GET** `/api/v1/users/me`

Returns detailed profile information for the current user.

**Authentication**: Required (Bearer token)

**Example Request**:
```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "github_username": "johndoe",
  "github_id": 12345678,
  "avatar_url": "https://avatars.githubusercontent.com/u/12345678",
  "is_active": true,
  "is_admin": false,
  "email_verified": true,
  "created_at": "2025-11-05T12:00:00Z",
  "updated_at": "2025-11-05T14:30:00Z",
  "last_login": "2025-11-05T14:30:00Z",
  "statistics": {
    "total_claims": 15,
    "active_claims": 3,
    "completed_claims": 12,
    "repositories_watching": 5
  }
}
```

---

### 2. Update Current User Profile
**PUT** `/api/v1/users/me`

Updates the current user's profile information.

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "full_name": "John A. Doe",
  "email": "john.doe@example.com",
  "github_username": "johndoe",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

**Example Request**:
```bash
curl -X PUT http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John A. Doe",
    "email": "john.doe@example.com"
  }'
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john.doe@example.com",
  "full_name": "John A. Doe",
  "updated_at": "2025-11-05T15:00:00Z",
  "message": "Profile updated successfully"
}
```

---

### 3. Get User Preferences
**GET** `/api/v1/users/me/preferences`

Returns notification and UI preferences for the current user.

**Authentication**: Required (Bearer token)

**Example Request**:
```bash
curl http://localhost:8000/api/v1/users/me/preferences \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Success Response** (200 OK):
```json
{
  "notifications": {
    "email_enabled": true,
    "email_frequency": "daily",
    "nudge_notifications": true,
    "claim_notifications": true,
    "weekly_summary": true
  },
  "ui": {
    "theme": "dark",
    "language": "en",
    "timezone": "America/New_York",
    "items_per_page": 25
  },
  "privacy": {
    "profile_public": true,
    "show_statistics": true
  }
}
```

---

## Repository Endpoints

All repository endpoints are under `/api/v1/repositories`

### 1. List Repositories
**GET** `/api/v1/repositories`

Returns a paginated list of all monitored repositories.

**Authentication**: None required (public endpoint)

**Query Parameters**:
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 100, max: 1000)
- `is_monitored` (optional): Filter by monitoring status (true/false)
- `owner` (optional): Filter by repository owner

**Example Request**:
```bash
# Get all repositories
curl http://localhost:8000/api/v1/repositories

# Get repositories with pagination
curl "http://localhost:8000/api/v1/repositories?skip=0&limit=10"

# Filter by owner
curl "http://localhost:8000/api/v1/repositories?owner=facebook"

# Only monitored repositories
curl "http://localhost:8000/api/v1/repositories?is_monitored=true"
```

**Success Response** (200 OK):
```json
{
  "total": 42,
  "skip": 0,
  "limit": 10,
  "repositories": [
    {
      "id": 1,
      "github_repo_id": 123456789,
      "owner_id": 1,
      "owner_name": "facebook",
      "name": "react",
      "full_name": "facebook/react",
      "url": "https://github.com/facebook/react",
      "is_monitored": true,
      "grace_period_days": 7,
      "nudge_count": 2,
      "claim_detection_threshold": 75,
      "notification_settings": {
        "nudge_enabled": true,
        "auto_release_enabled": true
      },
      "created_at": "2025-11-05T12:00:00Z",
      "updated_at": "2025-11-05T14:30:00Z",
      "statistics": {
        "total_issues": 150,
        "active_claims": 12,
        "completed_claims": 45
      }
    }
  ]
}
```

**Use Cases**:
- Display repository list in UI
- Monitor which repositories are being tracked
- Analytics dashboards
- Public API access for transparency

---

### 2. Register Repository
**POST** `/api/v1/repositories`

Adds a new repository to the monitoring system.

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "github_repo_id": 123456789,
  "owner_name": "facebook",
  "name": "react",
  "full_name": "facebook/react",
  "url": "https://github.com/facebook/react",
  "grace_period_days": 7,
  "nudge_count": 2,
  "claim_detection_threshold": 75,
  "notification_settings": {
    "nudge_enabled": true,
    "auto_release_enabled": true,
    "email_notifications": true
  }
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/repositories \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "github_repo_id": 123456789,
    "owner_name": "facebook",
    "name": "react",
    "full_name": "facebook/react",
    "url": "https://github.com/facebook/react",
    "grace_period_days": 7
  }'
```

**Success Response** (201 Created):
```json
{
  "id": 1,
  "github_repo_id": 123456789,
  "owner_name": "facebook",
  "name": "react",
  "full_name": "facebook/react",
  "url": "https://github.com/facebook/react",
  "is_monitored": true,
  "grace_period_days": 7,
  "nudge_count": 2,
  "created_at": "2025-11-05T15:00:00Z",
  "message": "Repository registered successfully"
}
```

**Error Response** (401 Unauthorized):
```json
{
  "detail": "Not authenticated"
}
```

**Error Response** (409 Conflict):
```json
{
  "detail": "Repository already registered"
}
```

---

## Claims Endpoints

All claims endpoints are under `/api/v1/claims`

### 1. List Claims
**GET** `/api/v1/claims`

Returns a paginated list of all issue claims.

**Authentication**: None required (public endpoint)

**Query Parameters**:
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 100)
- `status` (optional): Filter by status (active/released/completed/expired)
- `repository_id` (optional): Filter by repository ID
- `user_id` (optional): Filter by user ID
- `github_username` (optional): Filter by GitHub username

**Example Request**:
```bash
# Get all claims
curl http://localhost:8000/api/v1/claims

# Get active claims
curl "http://localhost:8000/api/v1/claims?status=active"

# Get claims for a specific repository
curl "http://localhost:8000/api/v1/claims?repository_id=1"

# Get claims by GitHub username
curl "http://localhost:8000/api/v1/claims?github_username=johndoe"

# Pagination
curl "http://localhost:8000/api/v1/claims?skip=0&limit=20"
```

**Success Response** (200 OK):
```json
{
  "total": 156,
  "skip": 0,
  "limit": 20,
  "claims": [
    {
      "id": 1,
      "issue_id": 42,
      "repository_id": 1,
      "user_id": 1,
      "github_user_id": 12345678,
      "github_username": "johndoe",
      "claim_comment_id": 987654321,
      "claim_text": "I'll work on this issue",
      "claim_timestamp": "2025-11-05T10:00:00Z",
      "status": "active",
      "first_nudge_sent_at": "2025-11-12T10:00:00Z",
      "last_activity_timestamp": "2025-11-05T10:00:00Z",
      "auto_release_timestamp": "2025-11-19T10:00:00Z",
      "confidence_score": 95,
      "context_metadata": {
        "is_assigned": false,
        "has_recent_activity": false,
        "claim_pattern": "explicit"
      },
      "created_at": "2025-11-05T10:00:00Z",
      "updated_at": "2025-11-05T10:00:00Z",
      "issue": {
        "id": 42,
        "github_issue_number": 1234,
        "title": "Add dark mode support",
        "status": "open"
      },
      "repository": {
        "id": 1,
        "full_name": "facebook/react",
        "url": "https://github.com/facebook/react"
      }
    }
  ]
}
```

**Use Cases**:
- Display claims dashboard
- Monitor claim status
- Track user activity
- Public transparency of claims

---

### 2. Get Claim Details
**GET** `/api/v1/claims/{claim_id}`

Returns detailed information about a specific claim.

**Authentication**: None required (public endpoint)

**Path Parameters**:
- `claim_id`: Integer ID of the claim

**Example Request**:
```bash
curl http://localhost:8000/api/v1/claims/1
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "issue_id": 42,
  "repository_id": 1,
  "user_id": 1,
  "github_user_id": 12345678,
  "github_username": "johndoe",
  "claim_comment_id": 987654321,
  "claim_text": "I'll work on this issue",
  "claim_timestamp": "2025-11-05T10:00:00Z",
  "status": "active",
  "first_nudge_sent_at": "2025-11-12T10:00:00Z",
  "last_activity_timestamp": "2025-11-05T10:00:00Z",
  "auto_release_timestamp": "2025-11-19T10:00:00Z",
  "release_reason": null,
  "confidence_score": 95,
  "context_metadata": {
    "is_assigned": false,
    "has_recent_activity": false,
    "claim_pattern": "explicit",
    "detection_method": "comment_analysis"
  },
  "created_at": "2025-11-05T10:00:00Z",
  "updated_at": "2025-11-05T10:00:00Z",
  "issue": {
    "id": 42,
    "repository_id": 1,
    "github_repo_id": 123456789,
    "github_issue_id": 1234567890,
    "github_issue_number": 1234,
    "title": "Add dark mode support",
    "description": "We should add a dark mode option to improve user experience",
    "status": "open",
    "created_at": "2025-11-01T08:00:00Z",
    "updated_at": "2025-11-05T10:00:00Z"
  },
  "repository": {
    "id": 1,
    "github_repo_id": 123456789,
    "owner_name": "facebook",
    "name": "react",
    "full_name": "facebook/react",
    "url": "https://github.com/facebook/react",
    "is_monitored": true,
    "grace_period_days": 7,
    "nudge_count": 2
  },
  "activity_logs": [
    {
      "id": 1,
      "activity_type": "claim_detected",
      "description": "Claim detected with 95% confidence",
      "timestamp": "2025-11-05T10:00:00Z"
    },
    {
      "id": 2,
      "activity_type": "nudge_sent",
      "description": "First nudge sent to user",
      "timestamp": "2025-11-12T10:00:00Z"
    }
  ]
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Claim not found"
}
```

**Use Cases**:
- View claim details page
- Track claim history
- Debug claim detection
- Audit claim lifecycle

---

## Dashboard Endpoints

All dashboard endpoints are under `/api/v1/dashboard` and **require authentication**.

### 1. Dashboard Statistics
**GET** `/api/v1/dashboard/stats`

Returns overall system statistics and metrics.

**Authentication**: Required (Bearer token)

**Example Request**:
```bash
curl http://localhost:8000/api/v1/dashboard/stats \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Success Response** (200 OK):
```json
{
  "overview": {
    "total_repositories": 42,
    "monitored_repositories": 38,
    "total_issues": 1523,
    "open_issues": 847,
    "total_claims": 342,
    "active_claims": 156,
    "completed_claims": 186
  },
  "claims_by_status": {
    "active": 156,
    "released": 45,
    "completed": 186,
    "expired": 12
  },
  "recent_activity": {
    "claims_last_24h": 23,
    "nudges_sent_last_24h": 12,
    "auto_releases_last_24h": 3,
    "issues_closed_last_24h": 8
  },
  "top_repositories": [
    {
      "repository": "facebook/react",
      "active_claims": 15,
      "total_claims": 87
    },
    {
      "repository": "microsoft/vscode",
      "active_claims": 12,
      "total_claims": 64
    }
  ],
  "top_claimers": [
    {
      "github_username": "johndoe",
      "active_claims": 5,
      "completed_claims": 23,
      "completion_rate": 82.1
    }
  ],
  "performance_metrics": {
    "average_claim_duration_days": 5.3,
    "claim_completion_rate": 74.2,
    "nudge_response_rate": 68.5
  }
}
```

**Use Cases**:
- Admin dashboard homepage
- System monitoring
- Performance analysis
- Reporting

---

### 2. Dashboard Repositories
**GET** `/api/v1/dashboard/repositories`

Returns detailed repository statistics for the dashboard.

**Authentication**: Required (Bearer token)

**Example Request**:
```bash
curl http://localhost:8000/api/v1/dashboard/repositories \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Success Response** (200 OK):
```json
{
  "repositories": [
    {
      "id": 1,
      "full_name": "facebook/react",
      "is_monitored": true,
      "statistics": {
        "total_issues": 150,
        "open_issues": 85,
        "active_claims": 15,
        "completed_claims": 45,
        "expired_claims": 3,
        "average_claim_duration_days": 4.2,
        "completion_rate": 75.0
      },
      "health_score": 85.5,
      "last_activity": "2025-11-05T14:30:00Z"
    }
  ],
  "summary": {
    "total_repositories": 42,
    "healthy_repositories": 38,
    "warning_repositories": 3,
    "critical_repositories": 1
  }
}
```

---

### 3. Dashboard Users
**GET** `/api/v1/dashboard/users`

Returns user activity statistics for the dashboard.

**Authentication**: Required (Bearer token)

**Example Request**:
```bash
curl http://localhost:8000/api/v1/dashboard/users \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Success Response** (200 OK):
```json
{
  "users": [
    {
      "id": 1,
      "username": "johndoe",
      "github_username": "johndoe",
      "statistics": {
        "active_claims": 5,
        "completed_claims": 23,
        "expired_claims": 2,
        "total_claims": 30,
        "completion_rate": 76.7,
        "average_claim_duration_days": 5.1
      },
      "last_activity": "2025-11-05T14:30:00Z",
      "reputation_score": 87.5
    }
  ],
  "summary": {
    "total_users": 156,
    "active_users_30d": 89,
    "new_users_30d": 12
  }
}
```

---

### 4. Dashboard Activity
**GET** `/api/v1/dashboard/activity`

Returns recent system activity logs for the dashboard.

**Authentication**: Required (Bearer token)

**Query Parameters**:
- `limit` (optional): Number of activities to return (default: 50)
- `activity_type` (optional): Filter by type

**Example Request**:
```bash
curl http://localhost:8000/api/v1/dashboard/activity \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by type
curl "http://localhost:8000/api/v1/dashboard/activity?activity_type=claim_detected" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Success Response** (200 OK):
```json
{
  "activities": [
    {
      "id": 1234,
      "claim_id": 42,
      "activity_type": "claim_detected",
      "description": "New claim detected on facebook/react#1234",
      "timestamp": "2025-11-05T14:30:00Z",
      "metadata": {
        "repository": "facebook/react",
        "issue_number": 1234,
        "github_username": "johndoe",
        "confidence_score": 95
      }
    },
    {
      "id": 1233,
      "claim_id": 41,
      "activity_type": "nudge_sent",
      "description": "First nudge sent to johndoe",
      "timestamp": "2025-11-05T14:15:00Z",
      "metadata": {
        "repository": "facebook/react",
        "issue_number": 1230,
        "nudge_number": 1
      }
    }
  ],
  "total": 1234
}
```

**Activity Types**:
- `claim_detected`: New claim identified
- `claim_released`: Claim released (auto or manual)
- `nudge_sent`: Progress nudge sent to user
- `issue_closed`: Issue marked as closed
- `issue_reopened`: Issue reopened
- `progress_update`: User provided progress update
- `auto_release`: Automatic claim release
- `manual_release`: Manual claim release by admin

---

## Settings Endpoints

All settings endpoints are under `/api/v1` and **require authentication**.

### 1. Get Settings
**GET** `/api/v1/settings`

Returns current system settings and configuration.

**Authentication**: Required (Bearer token)

**Example Request**:
```bash
curl http://localhost:8000/api/v1/settings \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Success Response** (200 OK):
```json
{
  "system": {
    "environment": "production",
    "version": "1.0.0",
    "maintenance_mode": false
  },
  "claims": {
    "default_grace_period_days": 7,
    "default_nudge_count": 2,
    "default_claim_threshold": 75,
    "auto_release_enabled": true
  },
  "notifications": {
    "email_enabled": true,
    "smtp_configured": true,
    "sendgrid_configured": true,
    "notification_batch_size": 100
  },
  "github": {
    "api_configured": true,
    "webhook_configured": true,
    "rate_limit_remaining": 4850
  },
  "monitoring": {
    "prometheus_enabled": true,
    "health_check_interval": 60,
    "metrics_retention_days": 30
  }
}
```

---

### 2. Update Settings
**PUT** `/api/v1/settings`

Updates system settings (admin only).

**Authentication**: Required (Bearer token + Admin role)

**Request Body**:
```json
{
  "claims": {
    "default_grace_period_days": 10,
    "default_nudge_count": 3,
    "auto_release_enabled": true
  },
  "notifications": {
    "email_enabled": true
  }
}
```

**Example Request**:
```bash
curl -X PUT http://localhost:8000/api/v1/settings \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "claims": {
      "default_grace_period_days": 10
    }
  }'
```

**Success Response** (200 OK):
```json
{
  "message": "Settings updated successfully",
  "updated_settings": {
    "claims": {
      "default_grace_period_days": 10
    }
  }
}
```

---

### 3. System Stats
**GET** `/api/v1/system/stats`

Returns detailed system performance and resource statistics.

**Authentication**: Required (Bearer token)

**Example Request**:
```bash
curl http://localhost:8000/api/v1/system/stats \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Success Response** (200 OK):
```json
{
  "system": {
    "uptime_seconds": 86400,
    "cpu_usage_percent": 24.8,
    "memory_usage_percent": 75.3,
    "memory_used_mb": 1024,
    "memory_total_mb": 4096,
    "disk_usage_percent": 45.2,
    "disk_used_gb": 250,
    "disk_total_gb": 500
  },
  "database": {
    "connections_active": 5,
    "connections_idle": 10,
    "connections_max": 50,
    "query_avg_duration_ms": 12.5,
    "slow_queries_count": 2
  },
  "redis": {
    "connected_clients": 3,
    "used_memory_mb": 128,
    "hit_rate_percent": 94.5,
    "keys_count": 15234
  },
  "api": {
    "requests_total": 156234,
    "requests_per_second": 12.5,
    "avg_response_time_ms": 45.2,
    "errors_5xx_count": 3,
    "errors_4xx_count": 245
  },
  "github": {
    "rate_limit_limit": 5000,
    "rate_limit_remaining": 4850,
    "rate_limit_reset": "2025-11-05T16:00:00Z",
    "webhook_events_processed": 1234
  },
  "background_jobs": {
    "queue_size": 23,
    "processing_count": 2,
    "completed_count": 5678,
    "failed_count": 12
  }
}
```

---

### 4. System Health
**GET** `/api/v1/system/health`

Detailed health check endpoint (alias for `/health` with more details).

**Authentication**: None required

**Example Request**:
```bash
curl http://localhost:8000/api/v1/system/health
```

**Response**: Same as `/health` endpoint (see System Endpoints section)

---

## Webhook Endpoints

All webhook endpoints are under `/api/v1/webhooks`

### 1. Webhook Health
**GET** `/api/v1/webhooks/health`

Returns health status of the webhook system.

**Authentication**: None required

**Example Request**:
```bash
curl http://localhost:8000/api/v1/webhooks/health
```

**Success Response** (200 OK):
```json
{
  "status": "healthy",
  "webhook_processor": "running",
  "last_event_processed": "2025-11-05T14:30:00Z",
  "events_processed_24h": 156,
  "events_queued": 3,
  "signature_validation": "enabled"
}
```

---

### 2. Test Webhook
**POST** `/api/v1/webhooks/test`

Test endpoint for webhook payload validation (development only).

**Authentication**: None required

**Request Body**: Any valid JSON (GitHub webhook payload format)

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{
    "action": "created",
    "comment": {
      "id": 987654321,
      "body": "I will work on this issue",
      "user": {
        "login": "johndoe",
        "id": 12345678
      }
    },
    "issue": {
      "number": 1234,
      "title": "Add dark mode support"
    },
    "repository": {
      "id": 123456789,
      "full_name": "facebook/react"
    }
  }'
```

**Success Response** (200 OK):
```json
{
  "message": "Webhook payload received successfully",
  "payload_type": "issue_comment",
  "validation": "passed",
  "would_trigger_claim_detection": true
}
```

**Error Response** (422 Unprocessable Entity):
```json
{
  "detail": "Request body must be valid JSON"
}
```

**Use Cases**:
- Test webhook integration
- Validate payload format
- Debug webhook issues
- Development testing

---

## Authentication Guide

### Using Bearer Tokens

Most protected endpoints require a Bearer token in the Authorization header:

```bash
curl http://localhost:8000/api/v1/protected-endpoint \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Getting an Access Token

1. **Register** a new account:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

2. **Login** to get your access token:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123!"
  }'
```

3. **Use the token** in subsequent requests:
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### Using API Keys

For programmatic access, create an API key:

```bash
# Create API key (requires Bearer token)
curl -X POST http://localhost:8000/api/v1/auth/api-keys \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production API Key",
    "expires_in_days": 90
  }'

# Use API key
curl http://localhost:8000/api/v1/repositories \
  -H "X-API-Key: ck_prod_1a2b3c4d5e6f7g8h9i0j"
```

---

## Error Responses

All endpoints follow consistent error response format:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters",
  "errors": [
    {
      "field": "limit",
      "message": "Must be between 1 and 1000"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions to perform this action"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 409 Conflict
```json
{
  "detail": "Resource already exists"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Retry after 60 seconds",
  "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred",
  "timestamp": "2025-11-05T15:00:00Z"
}
```

### 503 Service Unavailable
```json
{
  "detail": "Service temporarily unavailable",
  "status": "unhealthy",
  "checks": {
    "database": "unhealthy",
    "redis": "healthy"
  }
}
```

---

## Rate Limiting

All API endpoints are rate-limited:

- **Unauthenticated requests**: 100 requests per hour per IP
- **Authenticated requests**: 1000 requests per hour per user
- **API key requests**: 5000 requests per hour per key

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1699200000
```

---

## Pagination

List endpoints support pagination with `skip` and `limit` parameters:

```bash
# First page (items 0-19)
curl "http://localhost:8000/api/v1/repositories?skip=0&limit=20"

# Second page (items 20-39)
curl "http://localhost:8000/api/v1/repositories?skip=20&limit=20"

# Third page (items 40-59)
curl "http://localhost:8000/api/v1/repositories?skip=40&limit=20"
```

Pagination metadata is included in responses:
```json
{
  "total": 156,
  "skip": 0,
  "limit": 20,
  "items": [...]
}
```

---

## Best Practices

1. **Always use HTTPS in production** - Never send credentials over HTTP
2. **Store API keys securely** - Use environment variables, never commit to git
3. **Implement retry logic** - Handle transient errors with exponential backoff
4. **Respect rate limits** - Monitor `X-RateLimit-*` headers
5. **Validate responses** - Check status codes and error messages
6. **Use pagination** - Don't fetch all records at once
7. **Cache responses** - Reduce API calls for static data
8. **Monitor health** - Regularly check `/health` endpoint

---

## Support & Resources

- **Interactive Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

---

**Last Updated**: November 5, 2025  
**API Version**: 1.0.0  
**Status**: All endpoints operational ✅
