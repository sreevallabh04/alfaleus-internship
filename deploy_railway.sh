#!/bin/bash

# This script deploys the application to Railway
# Prerequisites: Railway CLI installed and logged in

# Function to display messages
print_message() {
  echo "====================================="
  echo "$1"
  echo "====================================="
}

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
  print_message "Railway CLI is not installed. Please install it first:"
  echo "npm i -g @railway/cli"
  exit 1
fi

# Check if logged in to Railway
railway whoami &> /dev/null
if [ $? -ne 0 ]; then
  print_message "Not logged in to Railway. Please login first:"
  echo "railway login"
  exit 1
fi

# Deploy backend
print_message "Deploying backend to Railway..."
cd backend
railway up --detach
cd ..

# Deploy frontend
print_message "Deploying frontend to Railway..."
cd frontend
railway up --detach
cd ..

print_message "Deployment complete!"
print_message "Check your Railway dashboard for the deployment status and URLs."
