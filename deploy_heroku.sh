#!/bin/bash

# This script deploys the application to Heroku
# Prerequisites: Heroku CLI installed and logged in

# Function to display messages
print_message() {
  echo "====================================="
  echo "$1"
  echo "====================================="
}

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
  print_message "Heroku CLI is not installed. Please install it first."
  exit 1
fi

# Check if logged in to Heroku
heroku whoami &> /dev/null
if [ $? -ne 0 ]; then
  print_message "Not logged in to Heroku. Please login first:"
  echo "heroku login"
  exit 1
fi

# Create Procfile for backend
print_message "Creating Procfile for backend..."
echo "web: cd backend && gunicorn app:app" > Procfile

# Create app.json for Heroku
print_message "Creating app.json for Heroku..."
cat > app.json << EOL
{
  "name": "PricePulse",
  "description": "E-commerce Price Tracking Platform",
  "repository": "https://github.com/yourusername/pricepulse",
  "keywords": ["python", "flask", "react", "price-tracking"],
  "env": {
    "FLASK_ENV": {
      "description": "Flask environment",
      "value": "production"
    },
    "PRICE_CHECK_INTERVAL": {
      "description": "Price check interval in minutes",
      "value": "30"
    }
  },
  "addons": [
    "heroku-postgresql:hobby-dev"
  ],
  "buildpacks": [
    {
      "url": "heroku/python"
    }
  ]
}
EOL

print_message "Creating Heroku app..."
heroku create pricepulse-app

print_message "Adding PostgreSQL addon..."
heroku addons:create heroku-postgresql:hobby-dev

print_message "Setting environment variables..."
heroku config:set FLASK_ENV=production
heroku config:set PRICE_CHECK_INTERVAL=30

print_message "Deployment configuration created!"
print_message "To deploy to Heroku:"
echo "1. Push this repository to Heroku:"
echo "   git push heroku main"
echo "2. Set up the remaining environment variables in the Heroku dashboard"
echo "3. For the frontend, deploy to Vercel or Netlify and set VITE_API_URL to your Heroku backend URL"
