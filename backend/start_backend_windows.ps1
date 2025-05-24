Write-Host "Starting PricePulse Backend for Windows..." -ForegroundColor Green

# Set environment variables
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Start the Flask application
Write-Host "Starting Flask application..." -ForegroundColor Green
python -m flask run --host=0.0.0.0

# Note: The virtual environment will be deactivated when PowerShell session ends