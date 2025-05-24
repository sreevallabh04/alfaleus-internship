#!/bin/bash

# This script prepares the application for deployment to Render
# You'll need to connect your GitHub repository to Render

# Function to display messages
print_message() {
  echo "====================================="
  echo "$1"
  echo "====================================="
}

# Create Procfile for backend
print_message "Creating Procfile for backend..."
echo "web: cd backend && gunicorn app:app" > Procfile

# Create render.yaml configuration
print_message "Creating render.yaml configuration..."
cat > render.yaml << EOL
services:
  - type: web
    name: pricepulse-backend
    env: python
    buildCommand: cd backend && pip install -r requirements.txt
    startCommand: cd backend && gunicorn app:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: PRICE_CHECK_INTERVAL
        value: 30
      - key: DATABASE_URL
        sync: false
      - key: SMTP_SERVER
        sync: false
      - key: SMTP_PORT
        sync: false
      - key: SMTP_USERNAME
        sync: false
      - key: SMTP_PASSWORD
        sync: false
      - key: SENDER_EMAIL
        sync: false
      - key: OPENAI_API_KEY
        sync: false

  - type: web
    name: pricepulse-frontend
    env: static
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: frontend/dist
    envVars:
      - key: VITE_API_URL
        value: https://pricepulse-backend.onrender.com/api
EOL

print_message "Deployment configuration created!"
print_message "To deploy to Render:"
echo "1. Push this repository to GitHub"
echo "2. Go to render.com and create a new 'Blueprint' deployment"
echo "3. Connect your GitHub repository"
echo "4. Render will automatically deploy both services"
