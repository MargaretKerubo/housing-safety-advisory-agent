#!/bin/bash
# Script to run both frontend and backend for development

echo "Starting Housing Safety Advisory Agent development environment..."

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Terminal 1: Start the Python backend
echo "Starting Python backend on port 5000..."
gnome-terminal -- bash -c "cd $SCRIPT_DIR/backend && python server.py; exec bash" &

# Wait a moment for the backend to start
sleep 3

# Terminal 2: Start the React frontend
echo "Starting React frontend on port 3000..."
gnome-terminal -- bash -c "cd $SCRIPT_DIR/frontend && npm start; exec bash" &

echo "Both applications are now running:"
echo "- Backend: http://localhost:5000"
echo "- Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both applications."