# Local Development Setup Guide

This guide explains how to set up and run the PricePulse application for local development.

## Prerequisites

- Python 3.8+ (with pip)
- Node.js 16+ (with npm)
- Virtual environment tool (venv, virtualenv, etc.)

## Database Configuration

For local development, the application uses SQLite to avoid PostgreSQL driver issues on Windows. The production environment uses PostgreSQL.

The database configuration is set in the `backend/.env` file:

```
# For local development (SQLite)
DATABASE_URL=sqlite:///pricepulse.db

# For production (PostgreSQL)
# DATABASE_URL=postgresql://username:password@localhost:5432/pricepulse
```

## Running the Backend

### On Windows

Two options are provided for Windows users:

#### Option 1: PowerShell Script

```powershell
cd backend
.\start_backend_windows.ps1
```

#### Option 2: Batch File

```cmd
cd backend
start_backend_windows.bat
```

These scripts will:
1. Set the required environment variables
2. Create a virtual environment if needed
3. Install dependencies
4. Start the Flask application

### On Linux/macOS

```bash
cd backend
./start_backend.sh
```

## Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:5173/

## AI Integration

The application supports AI-enhanced product metadata using Groq's API. The Groq API key is configured in the `backend/.env` file.

## Troubleshooting

### PostgreSQL Driver Issues on Windows

If you encounter errors related to PostgreSQL drivers when trying to run the backend directly:

```
ImportError: DLL load failed while importing _psycopg: The specified module could not be found.
```

Make sure you're using SQLite for local development as configured in this guide. Use the provided Windows scripts to start the backend.

### Virtual Environment Issues

If you encounter issues with activating the virtual environment, you may need to:

1. Ensure Python is properly installed and in your PATH
2. Run PowerShell as Administrator
3. Set the execution policy to allow scripts: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

## Deployment

For deployment to production environments, refer to the deployment scripts in the project root:

- `deploy_heroku.sh`
- `deploy_railway.sh`
- `deploy_render.sh`
- `deploy_vercel.sh`

When deploying, make sure to uncomment and configure the PostgreSQL connection string in the `.env` file.