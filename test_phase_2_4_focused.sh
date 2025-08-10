#!/bin/bash

echo "🔍 Phase 2.4 FOCUSED TEST: Authentication Routing Implementation"
echo "================================================================"

echo -e "\n✅ REQUIREMENT 1: AuthProvider wraps entire application"
if grep -q "AuthProvider" /workspaces/Backlogged-Books/frontend/src/App.js; then
    echo "✅ AuthProvider import and usage found in App.js"
    echo "   $(grep -n "AuthProvider" /workspaces/Backlogged-Books/frontend/src/App.js | head -1)"
else
    echo "❌ AuthProvider not found in App.js"
fi

echo -e "\n✅ REQUIREMENT 2: Login and Register routes added"
if grep -q 'path="/login"' /workspaces/Backlogged-Books/frontend/src/App.js; then
    echo "✅ Login route found: $(grep -n 'path="/login"' /workspaces/Backlogged-Books/frontend/src/App.js)"
else
    echo "❌ Login route not found"
fi

if grep -q 'path="/register"' /workspaces/Backlogged-Books/frontend/src/App.js; then
    echo "✅ Register route found: $(grep -n 'path="/register"' /workspaces/Backlogged-Books/frontend/src/App.js)"
else
    echo "❌ Register route not found"
fi

echo -e "\n✅ REQUIREMENT 3: ProtectedRoute component exists"
if [ -f "/workspaces/Backlogged-Books/frontend/src/components/ProtectedRoute.js" ]; then
    echo "✅ ProtectedRoute.js file exists"
    if grep -q "isAuthenticated" /workspaces/Backlogged-Books/frontend/src/components/ProtectedRoute.js; then
        echo "✅ ProtectedRoute checks isAuthenticated"
    else
        echo "❌ ProtectedRoute missing isAuthenticated check"
    fi
    if grep -q 'Navigate to="/login"' /workspaces/Backlogged-Books/frontend/src/components/ProtectedRoute.js; then
        echo "✅ ProtectedRoute redirects to /login"
    else
        echo "❌ ProtectedRoute missing redirect to /login"
    fi
else
    echo "❌ ProtectedRoute.js file not found"
fi

echo -e "\n✅ REQUIREMENT 4: Upload and Jobs routes wrapped with ProtectedRoute"
if grep -A5 'path="/upload"' /workspaces/Backlogged-Books/frontend/src/App.js | grep -q "ProtectedRoute"; then
    echo "✅ Upload route wrapped with ProtectedRoute"
else
    echo "❌ Upload route not protected"
fi

if grep -A5 'path="/jobs"' /workspaces/Backlogged-Books/frontend/src/App.js | grep -q "ProtectedRoute"; then
    echo "✅ Jobs route wrapped with ProtectedRoute"
else
    echo "❌ Jobs route not protected"
fi

echo -e "\n📋 FUNCTIONAL TEST: React App Serving"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ Frontend serving React app (Status: $FRONTEND_STATUS)"
else
    echo "❌ Frontend not working (Status: $FRONTEND_STATUS)"
fi

echo -e "\n📋 FUNCTIONAL TEST: All Routes Accessible"
ROUTES=("/login" "/register" "/upload" "/jobs" "/settings")
ALL_ROUTES_OK=true

for route in "${ROUTES[@]}"; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000$route")
    if [ "$STATUS" = "200" ]; then
        echo "✅ Route $route accessible"
    else
        echo "❌ Route $route failed (Status: $STATUS)"
        ALL_ROUTES_OK=false
    fi
done

echo -e "\n🎯 PHASE 2.4 IMPLEMENTATION SUMMARY"
echo "==================================="

if [ -f "/workspaces/Backlogged-Books/frontend/src/components/ProtectedRoute.js" ] && \
   grep -q "AuthProvider" /workspaces/Backlogged-Books/frontend/src/App.js && \
   grep -q 'path="/login"' /workspaces/Backlogged-Books/frontend/src/App.js && \
   grep -q 'path="/register"' /workspaces/Backlogged-Books/frontend/src/App.js && \
   grep -A5 'path="/upload"' /workspaces/Backlogged-Books/frontend/src/App.js | grep -q "ProtectedRoute" && \
   grep -A5 'path="/jobs"' /workspaces/Backlogged-Books/frontend/src/App.js | grep -q "ProtectedRoute" && \
   [ "$FRONTEND_STATUS" = "200" ] && [ "$ALL_ROUTES_OK" = true ]; then
    
    echo "🎉 PHASE 2.4 SUCCESSFULLY IMPLEMENTED!"
    echo ""
    echo "✅ All requirements met:"
    echo "   • AuthProvider wraps application"
    echo "   • Login/Register routes added"
    echo "   • ProtectedRoute component created"
    echo "   • Upload/Jobs routes protected"
    echo "   • Frontend serving correctly"
    echo "   • All routes accessible"
    echo ""
    echo "📝 Phase 2.4 can be marked as COMPLETED"
else
    echo "❌ PHASE 2.4 IMPLEMENTATION INCOMPLETE"
    echo "Some requirements are missing or not working properly"
fi

echo -e "\n🔗 Next Step: Manual browser testing recommended"
echo "   1. Open http://localhost:3000"
echo "   2. Test authentication flow manually"
