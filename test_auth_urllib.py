#!/usr/bin/env python3
"""
Phase 2.4 Authentication Testing Script
Tests all three authentication endpoints to verify fixes
"""
import urllib.request
import urllib.parse
import json
import sys

def make_request(url, method="GET", data=None, headers=None):
    """Make HTTP request using urllib"""
    if headers is None:
        headers = {}
    
    if data is not None:
        if isinstance(data, dict):
            if headers.get('Content-Type') == 'application/json':
                data = json.dumps(data).encode('utf-8')
                headers['Content-Type'] = 'application/json'
            else:
                data = urllib.parse.urlencode(data).encode('utf-8')
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.getcode(), response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return None, str(e)

def test_authentication():
    """Test all authentication endpoints"""
    print("=== Phase 2.4 Authentication Testing ===")
    print("Testing all three authentication endpoints after fixes")
    print()
    
    base_url = "http://localhost:8000"
    
    # Test 1: Registration
    print("1. Testing user registration...")
    register_data = {
        "email": "newuser@example.com",
        "password": "newpass123"
    }
    reg_status, reg_response = make_request(
        f"{base_url}/auth/register",
        method="POST",
        data=register_data,
        headers={'Content-Type': 'application/json'}
    )
    print(f"Registration Status Code: {reg_status}")
    print(f"Registration Response: {reg_response}")
    print()
    
    # Test 2: Login
    print("2. Testing user login...")
    login_data = {
        "username": "newuser@example.com",
        "password": "newpass123"
    }
    login_status, login_response = make_request(
        f"{base_url}/auth/jwt/login",
        method="POST",
        data=login_data
    )
    print(f"Login Status Code: {login_status}")
    print(f"Login Response: {login_response}")
    
    # Extract token
    token = None
    if login_status == 200:
        try:
            login_json = json.loads(login_response)
            token = login_json.get("access_token")
            print(f"Extracted Token: {token[:50] if token else 'None'}...")
        except:
            print("Failed to parse login response as JSON")
    print()
    
    # Test 3: Protected endpoint
    print("3. Testing protected endpoint (/users/me)...")
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        me_status, me_response = make_request(
            f"{base_url}/users/me",
            headers=headers
        )
        print(f"Protected Endpoint Status Code: {me_status}")
        print(f"Protected Endpoint Response: {me_response}")
    else:
        print("No token available - login failed")
        me_status = None
    print()
    
    # Summary
    print("=== TEST SUMMARY ===")
    print(f"Registration (POST /auth/register): {reg_status}")
    print(f"Login (POST /auth/jwt/login): {login_status}")
    print(f"Protected Endpoint (GET /users/me): {me_status}")
    print()
    
    if reg_status == 201 and login_status == 200 and me_status == 200:
        print("✅ Phase 2.4 Authentication Routing: PASSED")
        print("All authentication endpoints working correctly!")
        return True
    else:
        print("❌ Phase 2.4 Authentication Routing: FAILED")
        print("Some authentication endpoints are not working properly.")
        return False

if __name__ == "__main__":
    success = test_authentication()
    sys.exit(0 if success else 1)
