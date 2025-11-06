#!/usr/bin/env python3
"""
Comprehensive API Endpoint Tester for Cookie Licking Detector
Tests all API endpoints to verify they are working correctly
"""

import requests
import json
from typing import Dict, Optional
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

# ANSI color codes for pretty output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Test results tracking
total_tests = 0
passed_tests = 0
failed_tests = 0
failed_endpoints = []

def test_endpoint(method: str, path: str, expected_status: int = 200, 
                  data: Optional[Dict] = None, auth_token: Optional[str] = None,
                  description: str = "") -> bool:
    """Test a single API endpoint"""
    global total_tests, passed_tests, failed_tests, failed_endpoints
    
    total_tests += 1
    url = f"{BASE_URL}{path}"
    headers = {}
    
    if auth_token:
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
        else:
            print(f"{RED}✗{RESET} Unknown HTTP method: {method}")
            failed_tests += 1
            return False
        
        # Check status code
        if response.status_code == expected_status:
            print(f"{GREEN}✓{RESET} {method} {path} - {description}")
            passed_tests += 1
            return True
        else:
            print(f"{RED}✗{RESET} {method} {path} - Expected {expected_status}, got {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            failed_tests += 1
            failed_endpoints.append(f"{method} {path}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"{RED}✗{RESET} {method} {path} - Request timeout")
        failed_tests += 1
        failed_endpoints.append(f"{method} {path}")
        return False
    except Exception as e:
        print(f"{RED}✗{RESET} {method} {path} - Error: {str(e)}")
        failed_tests += 1
        failed_endpoints.append(f"{method} {path}")
        return False

def main():
    """Run all endpoint tests"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Cookie Licking Detector - API Endpoint Tests{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # System Endpoints (no /api/v1 prefix)
    print(f"\n{YELLOW}System Endpoints:{RESET}")
    test_endpoint("GET", "/", description="API Root")
    test_endpoint("GET", "/health", description="Health Check", expected_status=200)
    test_endpoint("GET", "/version", description="Version Info")
    test_endpoint("GET", "/metrics", description="Prometheus Metrics")
    test_endpoint("GET", "/docs", description="Swagger UI")
    test_endpoint("GET", "/redoc", description="ReDoc Documentation")
    test_endpoint("GET", "/openapi.json", description="OpenAPI Spec")
    
    # Authentication Endpoints
    print(f"\n{YELLOW}Authentication Endpoints:{RESET}")
    auth_token = None
    
    # Test registration (expect 422 without data)
    test_endpoint("POST", f"{API_PREFIX}/auth/register", 
                 expected_status=422,
                 description="Register (no data - should fail)")
    
    # Test login (expect 422 without credentials)
    test_endpoint("POST", f"{API_PREFIX}/auth/login",
                 expected_status=422,
                 description="Login (no credentials - should fail)")
    
    # Test auth/me (expect 401 without token)
    test_endpoint("GET", f"{API_PREFIX}/auth/me",
                 expected_status=401,
                 description="Get Current User (no auth - should fail)")
    
    # Test API keys list (expect 401 without token)
    test_endpoint("GET", f"{API_PREFIX}/auth/api-keys",
                 expected_status=401,
                 description="List API Keys (no auth - should fail)")
    
    # Test API key creation (expect 401 without token)
    test_endpoint("POST", f"{API_PREFIX}/auth/api-keys",
                 expected_status=401,
                 description="Create API Key (no auth - should fail)")
    
    # Test logout (expect 401 without token)
    test_endpoint("POST", f"{API_PREFIX}/auth/logout",
                 expected_status=401,
                 description="Logout (no auth - should fail)")
    
    # Users Endpoints
    print(f"\n{YELLOW}Users Endpoints:{RESET}")
    test_endpoint("GET", f"{API_PREFIX}/users/me",
                 expected_status=401,
                 description="Get User Profile (no auth - should fail)")
    
    test_endpoint("PUT", f"{API_PREFIX}/users/me",
                 expected_status=401,
                 description="Update User Profile (no auth - should fail)")
    
    test_endpoint("GET", f"{API_PREFIX}/users/me/preferences",
                 expected_status=401,
                 description="Get User Preferences (no auth - should fail)")
    
    # Repositories Endpoints
    print(f"\n{YELLOW}Repositories Endpoints:{RESET}")
    test_endpoint("GET", f"{API_PREFIX}/repositories",
                 description="List Repositories (public access)")
    
    test_endpoint("POST", f"{API_PREFIX}/repositories",
                 expected_status=401,
                 description="Create Repository (no auth - should fail)")
    
    # Claims Endpoints
    print(f"\n{YELLOW}Claims Endpoints:{RESET}")
    test_endpoint("GET", f"{API_PREFIX}/claims",
                 description="List Claims (public access)")
    
    # Get specific claim (expect 404 for non-existent claim)
    test_endpoint("GET", f"{API_PREFIX}/claims/1",
                 expected_status=404,
                 description="Get Claim (non-existent)")
    
    # Dashboard Endpoints
    print(f"\n{YELLOW}Dashboard Endpoints:{RESET}")
    test_endpoint("GET", f"{API_PREFIX}/dashboard/stats",
                 expected_status=401,
                 description="Dashboard Stats (no auth - should fail)")
    
    test_endpoint("GET", f"{API_PREFIX}/dashboard/repositories",
                 expected_status=401,
                 description="Dashboard Repositories (no auth - should fail)")
    
    test_endpoint("GET", f"{API_PREFIX}/dashboard/users",
                 expected_status=401,
                 description="Dashboard Users (no auth - should fail)")
    
    test_endpoint("GET", f"{API_PREFIX}/dashboard/activity",
                 expected_status=401,
                 description="Dashboard Activity (no auth - should fail)")
    
    # Settings Endpoints
    print(f"\n{YELLOW}Settings Endpoints:{RESET}")
    test_endpoint("GET", f"{API_PREFIX}/settings",
                 expected_status=401,
                 description="Get Settings (no auth - should fail)")
    
    test_endpoint("GET", f"{API_PREFIX}/system/stats",
                 expected_status=401,
                 description="System Stats (no auth - should fail)")
    
    test_endpoint("GET", f"{API_PREFIX}/system/health",
                 description="System Health Check")
    
    # Webhooks Endpoints
    print(f"\n{YELLOW}Webhooks Endpoints:{RESET}")
    test_endpoint("GET", f"{API_PREFIX}/webhooks/health",
                 description="Webhook Health")
    
    test_endpoint("POST", f"{API_PREFIX}/webhooks/test",
                 expected_status=422,
                 description="Test Webhook (no data - should fail)")
    
    # Print Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Test Summary:{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"Total Endpoints Tested: {total_tests}")
    print(f"{GREEN}Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%){RESET}")
    print(f"{RED}Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%){RESET}")
    
    if failed_endpoints:
        print(f"\n{RED}Failed Endpoints:{RESET}")
        for endpoint in failed_endpoints:
            print(f"  - {endpoint}")
    
    print(f"\n{BLUE}{'='*60}{RESET}\n")

if __name__ == "__main__":
    main()
