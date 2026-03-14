# Insurance Fraud Detection - Setup Script (Windows PowerShell)
$ErrorActionPreference = "Stop"

Write-Host "=== Insurance Fraud Detection Setup ===" -ForegroundColor Cyan
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
& .\venv\Scripts\Activate.ps1

# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create data directory and generate synthetic data
Write-Host "Generating synthetic data..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path data | Out-Null
python data_generator.py

# Initialize database
Write-Host "Initializing database..." -ForegroundColor Yellow
python -c "from models import init_database; init_database(); print('Database initialized')"

# Train ML model
Write-Host "Training ML model..." -ForegroundColor Yellow
python train_model.py

# Install frontend dependencies
if (Test-Path frontend\package.json) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Push-Location frontend
    npm install
    Pop-Location
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host "To run the application:"
Write-Host "1. Backend:  .\venv\Scripts\Activate.ps1; python app.py"
Write-Host "2. Frontend: cd frontend; npm run dev"
Write-Host ""
Write-Host "API will be available at http://localhost:5000"
