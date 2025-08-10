#!/usr/bin/env python3
"""
Debug authentication test to trace the exact issue
"""
import urllib.request
import urllib.parse
import json
import sys

def make_request_debug(url, method="GET", data=None, headers=None):
    """Make HTTP request with debug output"""
    if headers is None:
        headers = {}
    
    print(f"Making {method} request to: {url}")
    print(f"Headers: {headers}")
    
    if data is not None:
        if isinstance(data, dict):
            if headers.get('Content-Type') == 'application/json':
                data = json.dumps(data).encode('utf-8')
                headers['Content-Type'] = 'application/json'
            else:
                data = urllib.parse.urlencode(data).encode('utf-8')
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
        print(f"Data: {data}")
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            response_data = response.read().decode('utf-8')
            print(f"Response code: {response.getcode()}")
            print(f"Response headers: {dict(response.headers)}")
            print(f"Response body: {response_data}")
            return response.getcode(), response_data
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8')
        print(f"HTTP Error code: {e.code}")
        print(f"Error headers: {dict(e.headers)}")
        print(f"Error body: {error_data}")
        return e.code, error_data
    except Exception as e:
        print(f"Request failed: {e}")
        return None, str(e)

def test_me_endpoint():
    """Debug the /users/me endpoint specifically"""
    base_url = "http://localhost:8000"
    
    # First login to get a fresh token
    print("=== Getting fresh login token ===")
    login_data = {
        "username": "newuser@example.com",
        "password": "newpass123"
    }
    login_status, login_response = make_request_debug(
        f"{base_url}/auth/jwt/login",
        method="POST",
        data=login_data
    )
    
    if login_status != 200:
        print("Login failed, cannot test /users/me")
        return False
    
    # Extract token
    try:
        login_json = json.loads(login_response)
        token = login_json.get("access_token")
    except:
        print("Failed to parse login response")
        return False
    
    if not token:
        print("No token in login response")
        return False
    
    print(f"\n=== Testing /users/me with token ===")
    print(f"Token: {token}")
    
    # Test different authorization header formats
    auth_formats = [
        f"Bearer {token}",
        f"bearer {token}",  # lowercase
        token,  # just the token
        f"JWT {token}",  # JWT prefix
    ]
    
    for i, auth_header in enumerate(auth_formats):
        print(f"\n--- Test {i+1}: Authorization header = '{auth_header}' ---")
        headers = {"Authorization": auth_header}
        me_status, me_response = make_request_debug(
            f"{base_url}/users/me",
            headers=headers
        )
        
        if me_status == 200:
            print("✅ SUCCESS!")
            return True
        else:
            print(f"❌ Failed with status {me_status}")
    
    print("\nAll authorization header formats failed")
    return False

if __name__ == "__main__":
    success = test_me_endpoint()
    sys.exit(0 if success else 1)
