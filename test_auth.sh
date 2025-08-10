#!/bin/bash

echo "=== Phase 2.4 Authentication Testing ==="
echo "Testing all three authentication endpoints after fixes"
echo

# Test 1: Registration
echo "1. Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "testuser@example.com", "password": "testpass123"}' \
     -w "\nSTATUS:%{http_code}")

echo "Registration Response:"
echo "$REGISTER_RESPONSE"
REGISTER_STATUS=$(echo "$REGISTER_RESPONSE" | grep "STATUS:" | cut -d: -f2)
echo "Registration Status Code: $REGISTER_STATUS"
echo

# Test 2: Login
echo "2. Testing user login..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/jwt/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser@example.com&password=testpass123" \
     -w "\nSTATUS:%{http_code}")

echo "Login Response:"
echo "$LOGIN_RESPONSE"
LOGIN_STATUS=$(echo "$LOGIN_RESPONSE" | grep "STATUS:" | cut -d: -f2)
echo "Login Status Code: $LOGIN_STATUS"

# Extract token from response
TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
echo "Extracted Token: ${TOKEN:0:50}..." # Show first 50 chars
echo

# Test 3: Protected endpoint with token
echo "3. Testing protected endpoint (/users/me)..."
if [ -n "$TOKEN" ]; then
    ME_RESPONSE=$(curl -s -X GET "http://localhost:8000/users/me" \
         -H "Authorization: Bearer $TOKEN" \
         -w "\nSTATUS:%{http_code}")
    
    echo "Protected Endpoint Response:"
    echo "$ME_RESPONSE"
    ME_STATUS=$(echo "$ME_RESPONSE" | grep "STATUS:" | cut -d: -f2)
    echo "Protected Endpoint Status Code: $ME_STATUS"
else
    echo "No token available - login failed"
    ME_STATUS="N/A"
fi
echo

# Summary
echo "=== TEST SUMMARY ==="
echo "Registration (POST /auth/register): $REGISTER_STATUS"
echo "Login (POST /auth/jwt/login): $LOGIN_STATUS"
echo "Protected Endpoint (GET /users/me): $ME_STATUS"
echo

if [ "$REGISTER_STATUS" = "201" ] && [ "$LOGIN_STATUS" = "200" ] && [ "$ME_STATUS" = "200" ]; then
    echo "✅ Phase 2.4 Authentication Routing: PASSED"
    echo "All authentication endpoints working correctly!"
else
    echo "❌ Phase 2.4 Authentication Routing: FAILED"
    echo "Some authentication endpoints are not working properly."
fi
