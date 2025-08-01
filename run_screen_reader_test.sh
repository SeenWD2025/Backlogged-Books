#!/bin/bash

echo "Starting Screen Reader Compatibility Test"
echo "----------------------------------------"
echo "This script will assist with manually testing the AFSP application with screen readers"

# Check if the application is running
echo "Step 1: Ensuring the application is running..."
curl -s http://localhost:3000 > /dev/null
if [ $? -eq 0 ]; then
  echo "✓ The frontend application is running at http://localhost:3000"
else
  echo "✗ The frontend application is not running!"
  echo "  Please start the application with ./start_app.sh and try again."
  exit 1
fi

# Print instructions
echo ""
echo "Step 2: Screen Reader Testing Instructions"
echo "----------------------------------------"
echo "Please enable a screen reader on your system:"
echo "- macOS: VoiceOver (Command + F5 to toggle)"
echo "- Windows: NVDA or JAWS"
echo "- Linux: Orca"
echo ""
echo "Test the following pages with your screen reader:"
echo "1. Homepage: http://localhost:3000/"
echo "2. Upload Page: http://localhost:3000/upload"
echo "3. Jobs Page: http://localhost:3000/jobs"
echo "4. Job Details: http://localhost:3000/jobs/<job_id> (if available)"
echo "5. Settings: http://localhost:3000/settings"
echo ""
echo "Focus on testing:"
echo "- Navigation using keyboard (Tab, Shift+Tab, Arrow keys)"
echo "- Form controls (buttons, inputs, dropdowns)"
echo "- Dynamic content updates (status changes, error messages)"
echo "- Descriptive text alternatives for images and icons"
echo ""

# Prompt to record results
echo "Step 3: Record Results"
echo "--------------------"
echo "After testing, please record your findings in the file:"
echo "  /workspaces/Backlogged-Books/screen_reader_test_results.md"
echo ""
echo "A template file has been created for you."

# Create template file for results
cat > /workspaces/Backlogged-Books/screen_reader_test_results.md << 'EOF'
# Screen Reader Compatibility Test Results

## Testing Environment
- **Date:** [Enter Date]
- **Screen Reader:** [Enter Screen Reader Name and Version]
- **Browser:** [Enter Browser Name and Version]
- **Tester:** [Enter Your Name]

## Test Results

### Homepage
- Navigation: [Pass/Fail]
- Content Readability: [Pass/Fail]
- Button Accessibility: [Pass/Fail]
- Issues Identified:
  - [List any issues]

### Upload Page
- Form Controls: [Pass/Fail]
- Error Messages: [Pass/Fail]
- File Selection: [Pass/Fail]
- Issues Identified:
  - [List any issues]

### Jobs Page
- Table Navigation: [Pass/Fail]
- Status Information: [Pass/Fail]
- Pagination Controls: [Pass/Fail]
- Issues Identified:
  - [List any issues]

### Job Details Page
- Data Presentation: [Pass/Fail]
- Download Options: [Pass/Fail]
- Dynamic Updates: [Pass/Fail]
- Issues Identified:
  - [List any issues]

### Settings Page
- Form Controls: [Pass/Fail]
- Save/Reset Functionality: [Pass/Fail]
- Feedback Messages: [Pass/Fail]
- Issues Identified:
  - [List any issues]

## Overall Assessment
[Enter overall assessment of screen reader compatibility]

## Recommendations
[Enter recommendations for improvements]
EOF

echo "Screen reader test preparation complete!"
echo "Follow the instructions above to complete the testing."
