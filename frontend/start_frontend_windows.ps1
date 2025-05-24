Write-Host "Starting PricePulse Frontend for Windows..." -ForegroundColor Green

# Navigate to the frontend directory (script assumes it's run from the project root)
# If already in the frontend directory, this has no effect
try {
    if (!(Test-Path "package.json")) {
        Write-Host "package.json not found. Make sure you're in the frontend directory." -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "Error checking directory: $_" -ForegroundColor Red
    exit 1
}

# Install dependencies if node_modules doesn't exist
if (!(Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Start the development server
Write-Host "Starting development server..." -ForegroundColor Green
npm run dev