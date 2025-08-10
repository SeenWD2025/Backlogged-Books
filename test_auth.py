#!/usr/bin/env python3
"""
Phase 2.4 Authentication Testing Script
Tests all three authentication endpoints to verify fixes
"""
import httpx
import json
import sys

def test_authentication():
    """Test all authentication endpoints"""
    print("=== Phase 2.4 Authentication Testing ===")
    print("Testing all three authentication endpoints after fixes")
    print()
    
    base_url = "http://localhost:8000"
    
    # Test 1: Registration
    print("1. Testing user registration...")
    try:
        register_data = {
            "email": "testuser@example.com",
            "password": "testpass123"
        }
        register_response = httpx.post(
            f"{base_url}/auth/register",
            json=register_data,
            timeout=10
        )
        print(f"Registration Status Code: {register_response.status_code}")
        print(f"Registration Response: {register_response.text}")
        print()
    except Exception as e:
        print(f"Registration failed with error: {e}")
        register_response = None
    
    # Test 2: Login
    print("2. Testing user login...")
    try:
        login_data = {
            "username": "testuser@example.com",
            "password": "testpass123"
        }
        login_response = httpx.post(
            f"{base_url}/auth/jwt/login",
            data=login_data,  # form data, not json
            timeout=10
        )
        print(f"Login Status Code: {login_response.status_code}")
        print(f"Login Response: {login_response.text}")
        
        # Extract token
        token = None
        if login_response.status_code == 200:
            try:
                login_json = login_response.json()
                token = login_json.get("access_token")
                print(f"Extracted Token: {token[:50] if token else 'None'}...")
            except:
                print("Failed to parse login response as JSON")
        print()
    except Exception as e:
        print(f"Login failed with error: {e}")
        login_response = None
        token = None
    
    # Test 3: Protected endpoint
    print("3. Testing protected endpoint (/users/me)...")
    if token:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            me_response = httpx.get(
                f"{base_url}/users/me",
                headers=headers,
                timeout=10
            )
            print(f"Protected Endpoint Status Code: {me_response.status_code}")
            print(f"Protected Endpoint Response: {me_response.text}")
            print()
        except Exception as e:
            print(f"Protected endpoint failed with error: {e}")
            me_response = None
    else:
        print("No token available - login failed")
        me_response = None
        print()
    
    # Summary
    print("=== TEST SUMMARY ===")
    reg_status = register_response.status_code if register_response else "FAILED"
    login_status = login_response.status_code if login_response else "FAILED"
    me_status = me_response.status_code if me_response else "FAILED"
    
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
