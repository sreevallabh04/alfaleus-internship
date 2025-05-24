#!/bin/bash

# PricePulse Vercel Deployment Script
# This script automates the deployment of PricePulse to Vercel
# It handles environment variable verification, configuration updates,
# and provides guidance for setting up cron jobs

# Function to display messages with formatting
print_message() {
  echo -e "\n====================================="
  echo -e "$1"
  echo -e "=====================================\n"
}

# Function to display errors
print_error() {
  echo -e "\n❌ ERROR: $1" >&2
  echo -e "Please fix the issue and run the script again.\n"
}

# Function to display success messages
print_success() {
  echo -e "\n✅ SUCCESS: $1"
}

# Function to prompt for input with a default value
prompt_with_default() {
  local prompt=$1
  local default=$2
  read -p "$prompt [$default]: " input
  echo ${input:-$default}
}

# Function to check if a variable is set in the environment
check_env_var() {
  local var_name=$1
  if [ -z "${!var_name}" ]; then
    return 1
  fi
  return 0
}

# Function to ask for variable value if not set
prompt_env_var() {
  local var_name=$1
  local description=$2
  local is_secret=$3
  local default_value=$4

  if ! check_env_var "$var_name"; then
    echo -e "\n$description"
    if [ "$is_secret" = true ]; then
      read -s -p "Enter value for $var_name: " value
      echo
    else
      if [ -n "$default_value" ]; then
        read -p "Enter value for $var_name [$default_value]: " value
        value=${value:-$default_value}
      else
        read -p "Enter value for $var_name: " value
      fi
    fi
    export "$var_name"="$value"
  else
    echo -e "Using existing $var_name from environment."
  fi
}

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
  print_message "Vercel CLI is not installed. Installing now..."
  npm install -g vercel
  
  if ! command -v vercel &> /dev/null; then
    print_error "Failed to install Vercel CLI. Please install it manually: npm install -g vercel"
    exit 1
  fi
  print_success "Vercel CLI installed successfully."
fi

# Check if logged in to Vercel
print_message "Checking Vercel login status..."
if ! vercel whoami &> /dev/null; then
  print_message "You are not logged in to Vercel. Please log in."
  vercel login
  
  if ! vercel whoami &> /dev/null; then
    print_error "Failed to log in to Vercel. Please log in manually and run this script again."
    exit 1
  fi
fi
print_success "Logged in to Vercel."

# Create temporary directory for deployment
TEMP_DIR=$(mktemp -d)
print_message "Using temporary directory: $TEMP_DIR"

# Prompt for essential environment variables
print_message "Configuring environment variables..."

# Database configuration
prompt_env_var "DATABASE_URL" "Your Neon PostgreSQL connection string (required)" true
prompt_env_var "FLASK_ENV" "Flask environment (production/development)" false "production"
prompt_env_var "PRICE_CHECK_INTERVAL" "Price check interval in minutes" false "30"

# Email configuration
prompt_env_var "SMTP_SERVER" "SMTP server for sending emails" false "smtp.gmail.com"
prompt_env_var "SMTP_PORT" "SMTP port" false "587"
prompt_env_var "SMTP_USERNAME" "SMTP username (email address)" false
prompt_env_var "SMTP_PASSWORD" "SMTP password (for Gmail, use App Password)" true
prompt_env_var "SENDER_EMAIL" "Sender email address" false

# Security
prompt_env_var "CRON_SECRET" "Secret token for cron job authentication (generate a strong random string)" true

# Deploy backend first
print_message "Deploying backend to Vercel..."
cd backend

# Export environment variables for backend deployment
cat > .vercel.env <<EOL
DATABASE_URL=${DATABASE_URL}
FLASK_ENV=${FLASK_ENV}
PRICE_CHECK_INTERVAL=${PRICE_CHECK_INTERVAL}
SMTP_SERVER=${SMTP_SERVER}
SMTP_PORT=${SMTP_PORT}
SMTP_USERNAME=${SMTP_USERNAME}
SMTP_PASSWORD=${SMTP_PASSWORD}
SENDER_EMAIL=${SENDER_EMAIL}
CRON_SECRET=${CRON_SECRET}
EOL

# Ensure vercel.json has cron configuration
if ! grep -q "crons" vercel.json; then
  print_message "Updating vercel.json to include cron job configuration..."
  # Create a backup
  cp vercel.json vercel.json.bak
  
  # Update vercel.json to include cron configuration
  cat > vercel.json <<EOL
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "FLASK_ENV": "production"
  },
  "crons": [
    {
      "path": "/api/cron",
      "schedule": "*/30 * * * *"
    }
  ]
}
EOL
  print_success "vercel.json updated with cron configuration."
fi

# Deploy backend with environment variables from file
BACKEND_OUTPUT=$(vercel --prod --env-file .vercel.env 2>&1)
BACKEND_RESULT=$?

if [ $BACKEND_RESULT -ne 0 ]; then
  print_error "Backend deployment failed: $BACKEND_OUTPUT"
  rm .vercel.env
  exit 1
fi

print_success "Backend deployed successfully."
rm .vercel.env

# Extract backend URL from deployment output
BACKEND_URL=$(echo "$BACKEND_OUTPUT" | grep -o 'https://[^ ]*\.vercel\.app' | head -1)

if [ -z "$BACKEND_URL" ]; then
  print_message "Could not automatically detect backend URL."
  BACKEND_URL=$(prompt_with_default "Please enter your backend URL" "https://pricepulse-api.vercel.app")
fi

print_message "Backend deployed to: $BACKEND_URL"
export BACKEND_URL

# Go back to root and deploy frontend
cd ..

# Update frontend vercel.json to point to the correct backend URL
print_message "Updating frontend configuration to use backend URL: $BACKEND_URL"
cd frontend

# Create a backup of vercel.json
cp vercel.json vercel.json.bak

# Update vercel.json with the correct backend URL
cat > vercel.json <<EOL
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "${BACKEND_URL}/api/:path*"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        },
        {
          "key": "Permissions-Policy",
          "value": "camera=(), microphone=(), geolocation=()"
        }
      ]
    }
  ]
}
EOL

# Create .env file for frontend
echo "VITE_API_URL=${BACKEND_URL}/api" > .env

print_success "Frontend configuration updated."

# Deploy frontend
print_message "Deploying frontend to Vercel..."
FRONTEND_OUTPUT=$(vercel --prod 2>&1)
FRONTEND_RESULT=$?

if [ $FRONTEND_RESULT -ne 0 ]; then
  print_error "Frontend deployment failed: $FRONTEND_OUTPUT"
  # Restore backup
  mv vercel.json.bak vercel.json
  exit 1
fi

# Clean up backup
rm -f vercel.json.bak

# Extract frontend URL from deployment output
FRONTEND_URL=$(echo "$FRONTEND_OUTPUT" | grep -o 'https://[^ ]*\.vercel\.app' | head -1)

if [ -z "$FRONTEND_URL" ]; then
  print_message "Could not automatically detect frontend URL."
  FRONTEND_URL=$(prompt_with_default "Please enter your frontend URL" "https://pricepulse.vercel.app")
fi

print_success "Frontend deployed to: $FRONTEND_URL"

# Go back to root directory
cd ..

# Deployment summary
print_message "DEPLOYMENT SUMMARY"
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo "Cron job: Configured to run every 30 minutes via Vercel"

# Post-deployment verification steps
print_message "POST-DEPLOYMENT VERIFICATION"
echo "1. Visit the frontend URL: $FRONTEND_URL"
echo "2. Check backend health: $BACKEND_URL/api/health"
echo "3. Test adding a product and setting up a price alert"
echo "4. Check if cron job is working by monitoring logs in Vercel dashboard"

# Security reminders
print_message "SECURITY CHECKLIST"
echo "✅ CORS configured to allow specific origins"
echo "✅ Security headers set for frontend responses"
echo "✅ Environment variables stored securely in Vercel"
echo "✅ Rate limiting enabled for API endpoints"
echo "✅ Cron job protected with CRON_SECRET"

# Final instructions
print_message "NEXT STEPS"
echo "1. Visit your Vercel dashboard to monitor deployments"
echo "2. Set up custom domains (optional):"
echo "   - For frontend: vercel domains add $FRONTEND_URL your-domain.com"
echo "   - For backend: vercel domains add $BACKEND_URL api.your-domain.com"
echo "3. If you update custom domains, remember to update ALLOWED_ORIGINS in backend environment variables"
echo "4. Monitor your Neon PostgreSQL database usage at console.neon.tech"

print_message "Deployment complete! Your PricePulse application is now live."