#!/bin/bash

# Install dependencies
echo "Installing dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    echo "VITE_API_URL=http://localhost:5000/api" > .env
    echo "Please update the .env file with your configuration if needed."
fi

# Start the development server
echo "Starting development server..."
npm run dev
