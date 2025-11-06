#!/usr/bin/env python3
"""
Comprehensive API Endpoint Tester for Cookie Licking Detector
Tests all available endpoints to verify they're working correctly.
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Tuple
import sys

# Base URL for the API
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# ANSI color codes for pretty output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Global auth token
auth_token = None


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")


def print_test(name: str, method: str, endpoint: str):
    """Print test information."""
    print(f"{YELLOW}Testing:{RESET} {method} {endpoint}")
    print(f"{YELLOW}Name:{RESET} {name}")


def print_result(success: bool, status_code: int, message: str = ""):
    """Print test result."""
    if success:
        print(f"{GREEN}✓ PASSED{RESET} - Status: {status_code}")
        if message:
            print(f"  Response: {message}")
    else:
        print(f"{RED}✗ FAILED{RESET} - Status: {status_code}")
        if message:
            print(f"  Error: {message}")
    print()


def test_endpoint(
    method: str,
    endpoint: str,
    name: str,
    expected_status: int = 200,
    data: Dict = None,
    headers: Dict = None,
    auth_required: bool = False
) -> Tuple[bool, int, str]:
    """
    Test a single endpoint.
    
    Returns: (success, status_code, message)
    """
    print_test(name, method, endpoint)
    
    url = f"{BASE_URL}{endpoint}" if endpoint.startswith('/') else f"{API_V1}{endpoint}"
    
    # Prepare headers
    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    if auth_required and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        elif method == "PATCH":
            response = requests.patch(url, json=data, headers=headers, timeout=10)
        else:
            return False, 0, f"Unsupported method: {method}"
        
        # Check if status code matches expected
        success = response.status_code == expected_status
        
        # Try to get response message
        try:
            response_data = response.json()
            message = json.dumps(response_data, indent=2)[:200]  # Truncate long responses
        except:
            message = response.text[:200] if response.text else "No response body"
        
        print_result(success, response.status_code, message)
        
        return success, response.status_code, message
        
    except requests.exceptions.RequestException as e:
        print_result(False, 0, str(e))
        return False, 0, str(e)


def run_tests():
    """Run all endpoint tests."""
    global auth_token
    
    results = []
    
    print_header("🍪 COOKIE LICKING DETECTOR - API ENDPOINT TESTS 🍪")
    print(f"{BLUE}Testing Backend at:{RESET} {BASE_URL}")
    print(f"{BLUE}Started:{RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # =================================================================
    # SYSTEM ENDPOINTS (No auth required)
    # =================================================================
    print_header("SYSTEM ENDPOINTS")
    
    success, code, msg = test_endpoint(
        "GET", "/", "API Root Information"
    )
    results.append(("GET /", success))
    
    success, code, msg = test_endpoint(
        "GET", "/health", "System Health Check"
    )
    results.append(("GET /health", success))
    
    success, code, msg = test_endpoint(
        "GET", "/version", "Version Information"
    )
    results.append(("GET /version", success))
    
    success, code, msg = test_endpoint(
        "GET", "/metrics", "Prometheus Metrics"
    )
    results.append(("GET /metrics", success))
    
    success, code, msg = test_endpoint(
        "GET", "/docs", "Swagger UI Documentation"
    )
    results.append(("GET /docs", success))
    
    success, code, msg = test_endpoint(
        "GET", "/redoc", "ReDoc Documentation"
    )
    results.append(("GET /redoc", success))
    
    success, code, msg = test_endpoint(
        "GET", "/openapi.json", "OpenAPI Specification"
    )
    results.append(("GET /openapi.json", success))
    
    # =================================================================
    # AUTHENTICATION ENDPOINTS
    # =================================================================
    print_header("AUTHENTICATION ENDPOINTS")
    
    # Register a test user
    test_user_email = f"test_{datetime.now().timestamp()}@example.com"
    register_data = {
        "email": test_user_email,
        "password": "TestPassword123!",
        "full_name": "Test User",
        "github_username": "testuser"
    }
    
    success, code, msg = test_endpoint(
        "POST", "/auth/register", 
        "Register New User",
        expected_status=201,
        data=register_data
    )
    results.append(("POST /api/v1/auth/register", success))
    
    # Login with the test user
    login_data = {
        "email": test_user_email,
        "password": "TestPassword123!"
    }
    
    success, code, msg = test_endpoint(
        "POST", "/auth/login",
        "User Login",
        data=login_data
    )
    results.append(("POST /api/v1/auth/login", success))
    
    # Extract token if login successful
    if success and msg:
        try:
            response_data = json.loads(msg)
            auth_token = response_data.get("access_token")
            print(f"{GREEN}✓ Auth token obtained successfully{RESET}\n")
        except:
            print(f"{RED}✗ Failed to extract auth token{RESET}\n")
    
    # Get current user info (requires auth)
    success, code, msg = test_endpoint(
        "GET", "/auth/me",
        "Get Current User Info",
        auth_required=True
    )
    results.append(("GET /api/v1/auth/me", success))
    
    # List API keys
    success, code, msg = test_endpoint(
        "GET", "/auth/api-keys",
        "List API Keys",
        auth_required=True
    )
    results.append(("GET /api/v1/auth/api-keys", success))
    
    # Create API key
    api_key_data = {
        "name": "Test API Key",
        "description": "API key for testing",
        "scopes": ["read"]
    }
    
    success, code, msg = test_endpoint(
        "POST", "/auth/api-keys",
        "Create API Key",
        expected_status=201,
        data=api_key_data,
        auth_required=True
    )
    results.append(("POST /api/v1/auth/api-keys", success))
    
    # Logout
    success, code, msg = test_endpoint(
        "POST", "/auth/logout",
        "User Logout",
        auth_required=True
    )
    results.append(("POST /api/v1/auth/logout", success))
    
    # =================================================================
    # USER ENDPOINTS
    # =================================================================
    print_header("USER ENDPOINTS")
    
    success, code, msg = test_endpoint(
        "GET", "/users/me",
        "Get Current User Profile",
        auth_required=True
    )
    results.append(("GET /api/v1/users/me", success))
    
    success, code, msg = test_endpoint(
        "GET", "/users/me/preferences",
        "Get User Preferences",
        auth_required=True
    )
    results.append(("GET /api/v1/users/me/preferences", success))
    
    # Update user profile
    profile_update = {
        "full_name": "Updated Test User",
        "bio": "This is a test bio"
    }
    
    success, code, msg = test_endpoint(
        "PUT", "/users/me",
        "Update User Profile",
        data=profile_update,
        auth_required=True
    )
    results.append(("PUT /api/v1/users/me", success))
    
    # =================================================================
    # REPOSITORY ENDPOINTS
    # =================================================================
    print_header("REPOSITORY ENDPOINTS")
    
    # List repositories
    success, code, msg = test_endpoint(
        "GET", "/repositories",
        "List Repositories"
    )
    results.append(("GET /api/v1/repositories", success))
    
    # Register a repository (will likely fail without valid GitHub token)
    repo_data = {
        "owner": "facebook",
        "name": "react",
        "grace_period_days": 7,
        "nudge_count": 2,
        "claim_detection_threshold": 75
    }
    
    success, code, msg = test_endpoint(
        "POST", "/repositories",
        "Register Repository",
        expected_status=201,
        data=repo_data
    )
    results.append(("POST /api/v1/repositories", success))
    
    # =================================================================
    # CLAIMS ENDPOINTS
    # =================================================================
    print_header("CLAIMS ENDPOINTS")
    
    # List claims
    success, code, msg = test_endpoint(
        "GET", "/claims",
        "List All Claims"
    )
    results.append(("GET /api/v1/claims", success))
    
    # Get specific claim (ID 1)
    success, code, msg = test_endpoint(
        "GET", "/claims/1",
        "Get Claim Details",
        expected_status=404  # Expecting 404 if no claims exist
    )
    results.append(("GET /api/v1/claims/{id}", success))
    
    # =================================================================
    # DASHBOARD ENDPOINTS
    # =================================================================
    print_header("DASHBOARD ENDPOINTS")
    
    success, code, msg = test_endpoint(
        "GET", "/dashboard/stats",
        "Dashboard Statistics"
    )
    results.append(("GET /api/v1/dashboard/stats", success))
    
    success, code, msg = test_endpoint(
        "GET", "/dashboard/repositories",
        "Repository Metrics"
    )
    results.append(("GET /api/v1/dashboard/repositories", success))
    
    success, code, msg = test_endpoint(
        "GET", "/dashboard/users",
        "User Metrics"
    )
    results.append(("GET /api/v1/dashboard/users", success))
    
    success, code, msg = test_endpoint(
        "GET", "/dashboard/activity",
        "Recent Activity Feed"
    )
    results.append(("GET /api/v1/dashboard/activity", success))
    
    # =================================================================
    # SETTINGS ENDPOINTS
    # =================================================================
    print_header("SETTINGS ENDPOINTS")
    
    success, code, msg = test_endpoint(
        "GET", "/settings",
        "Get System Settings"
    )
    results.append(("GET /api/v1/settings", success))
    
    success, code, msg = test_endpoint(
        "GET", "/system/stats",
        "System Statistics"
    )
    results.append(("GET /api/v1/system/stats", success))
    
    success, code, msg = test_endpoint(
        "GET", "/system/health",
        "System Health Status"
    )
    results.append(("GET /api/v1/system/health", success))
    
    # =================================================================
    # WEBHOOK ENDPOINTS
    # =================================================================
    print_header("WEBHOOK ENDPOINTS")
    
    success, code, msg = test_endpoint(
        "GET", "/webhooks/health",
        "Webhook Service Health"
    )
    results.append(("GET /api/v1/webhooks/health", success))
    
    # Test webhook (only in development)
    test_payload = {
        "test": "data",
        "timestamp": datetime.now().isoformat()
    }
    
    success, code, msg = test_endpoint(
        "POST", "/webhooks/test",
        "Test Webhook Endpoint",
        data=test_payload
    )
    results.append(("POST /api/v1/webhooks/test", success))
    
    # =================================================================
    # SUMMARY
    # =================================================================
    print_header("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"{BLUE}Total Endpoints Tested:{RESET} {total_tests}")
    print(f"{GREEN}Passed:{RESET} {passed_tests}")
    print(f"{RED}Failed:{RESET} {failed_tests}")
    print(f"{YELLOW}Pass Rate:{RESET} {pass_rate:.1f}%\n")
    
    if failed_tests > 0:
        print(f"{RED}Failed Endpoints:{RESET}")
        for endpoint, success in results:
            if not success:
                print(f"  {RED}✗{RESET} {endpoint}")
    
    print(f"\n{BLUE}Completed:{RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return exit code based on results
    return 0 if failed_tests == 0 else 1


if __name__ == "__main__":
    try:
        # Check if backend is running
        try:
            response = requests.get(BASE_URL, timeout=5)
            print(f"{GREEN}✓ Backend is running{RESET}")
        except requests.exceptions.RequestException as e:
            print(f"{RED}✗ Cannot connect to backend at {BASE_URL}{RESET}")
            print(f"{RED}  Error: {e}{RESET}")
            print(f"\n{YELLOW}Please start the backend first:{RESET}")
            print(f"  cd /Users/void/Desktop/CookiesCop/cookie-licking-detector")
            print(f"  python3 start_backend.py")
            sys.exit(1)
        
        # Run all tests
        exit_code = run_tests()
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Tests interrupted by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Unexpected error: {e}{RESET}")
        sys.exit(1)
