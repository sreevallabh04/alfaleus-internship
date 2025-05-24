#!/bin/bash

# Function to display messages
print_message() {
  echo "====================================="
  echo "$1"
  echo "====================================="
}

# Create directories if they don't exist
mkdir -p screenshots

# Setup backend
print_message "Setting up backend..."
cd backend
chmod +x start_backend.sh

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  print_message "Creating virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
print_message "Installing backend dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
  print_message "Creating backend .env file from example..."
  cp .env.example .env
  echo "Please update the backend .env file with your configuration."
fi

# Deactivate virtual environment
deactivate

cd ..

# Setup frontend
print_message "Setting up frontend..."
cd frontend
chmod +x start_frontend.sh

# Install dependencies
print_message "Installing frontend dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
  print_message "Creating frontend .env file..."
  echo "VITE_API_URL=http://localhost:5000/api" > .env
  echo "Please update the frontend .env file with your configuration if needed."
fi

cd ..

# Seed the database with sample data
print_message "Seeding database with sample data..."
chmod +x seed_database.sh
./seed_database.sh

print_message "Setup complete!"
print_message "To start the application, run: ./start.sh"
