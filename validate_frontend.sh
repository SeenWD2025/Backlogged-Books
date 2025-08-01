#!/bin/bash

# AFSP Frontend Validation Script
# This script checks critical parts of the frontend implementation

echo "============================================"
echo "AFSP Frontend Validation"
echo "============================================"
echo

# Check if the FastAPI backend is running
echo "Checking backend status..."
if curl -s http://localhost:8000/health | grep -q "status.*up"; then
    echo "✓ Backend is running"
else
    echo "✗ Backend is not running or not responding"
    echo "  Try running: ./start_app.sh"
    exit 1
fi

# Check if React frontend is running
echo "Checking frontend status..."
if curl -s http://localhost:3000 | grep -q "React App"; then
    echo "✓ Frontend is running"
else
    echo "✗ Frontend is not running or not responding"
    echo "  Try running: ./start_app.sh"
    exit 1
fi

# Check for critical files
echo "Checking critical files..."

# Check frontend components
if [ -f "/workspaces/Backlogged-Books/frontend/src/components/FileUpload.js" ] && \
   [ -f "/workspaces/Backlogged-Books/frontend/src/components/Header.js" ] && \
   [ -f "/workspaces/Backlogged-Books/frontend/src/pages/JobsPage.js" ]; then
    echo "✓ Frontend components found"
else
    echo "✗ Some frontend components are missing"
fi

# Check documentation
if [ -f "/workspaces/Backlogged-Books/frontend_development_guide.md" ] && \
   [ -f "/workspaces/Backlogged-Books/README-frontend.md" ] && \
   [ -f "/workspaces/Backlogged-Books/frontend_final_implementation.md" ]; then
    echo "✓ Frontend documentation found"
else
    echo "✗ Some frontend documentation is missing"
fi

# Check API endpoint connections
echo "Checking API connectivity..."
if curl -s http://localhost:8000/api/jobs | grep -q "\[\]" || curl -s http://localhost:8000/api/jobs | grep -q "id"; then
    echo "✓ API Jobs endpoint is accessible"
else
    echo "✗ API Jobs endpoint is not responding correctly"
fi

echo
echo "============================================"
echo "Validation Complete"
echo "============================================"
echo
echo "For a full application tour, visit:"
echo "http://localhost:3000"
echo
echo "Documentation is available in:"
echo "- /workspaces/Backlogged-Books/frontend_documentation_guide.md"
echo "- /workspaces/Backlogged-Books/frontend_final_implementation.md"
echo "- /workspaces/Backlogged-Books/README-frontend.md"
echo
echo "To verify accessibility compliance:"
echo "./run_screen_reader_test.sh"
echo
echo "To create a backup of your data:"
echo "./backup_restore.sh backup"
echo
