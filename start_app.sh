#!/bin/bash

# Start the backend FastAPI server
echo "Starting FastAPI backend..."
cd /workspaces/Backlogged-Books
source venv/bin/activate
python -m uvicorn afsp_app.app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Backend started with PID: $BACKEND_PID"

# Wait a bit for the backend to initialize
echo "Waiting for backend to initialize..."
sleep 3

# Start the React frontend
echo "Starting React frontend..."
cd /workspaces/Backlogged-Books/frontend
npm install
npm start &
FRONTEND_PID=$!

echo "Frontend started with PID: $FRONTEND_PID"

# Function to clean up processes on script exit
cleanup() {
  echo "Cleaning up processes..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
  exit 0
}

# Trap signals to ensure cleanup
trap cleanup SIGINT SIGTERM

# Keep script running
echo "Both services are running. Press Ctrl+C to stop."
wait
