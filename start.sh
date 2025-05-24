#!/bin/bash

# Function to display messages
print_message() {
  echo "====================================="
  echo "$1"
  echo "====================================="
}

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
  print_message "tmux is not installed. Please install it to run both servers simultaneously."
  exit 1
fi

# Create a new tmux session
tmux new-session -d -s pricepulse

# Split the window horizontally
tmux split-window -h -t pricepulse

# Start backend in the left pane
tmux send-keys -t pricepulse:0.0 "cd backend && chmod +x start_backend.sh && ./start_backend.sh" C-m

# Start frontend in the right pane
tmux send-keys -t pricepulse:0.1 "cd frontend && chmod +x start_frontend.sh && ./start_frontend.sh" C-m

# Attach to the session
print_message "Starting PricePulse application..."
print_message "Backend will run on http://localhost:5000"
print_message "Frontend will run on http://localhost:5173"
print_message "Press Ctrl+B then D to detach from tmux without stopping the servers"

tmux attach-session -t pricepulse
