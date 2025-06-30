# Development setup script for Windows PowerShell

Write-Host "Setting up Terminal Toys development environment..." -ForegroundColor Green

# Create virtual environment if it doesn't exist
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install in development mode
Write-Host "Installing terminal-toys in development mode..." -ForegroundColor Yellow
pip install -e .

Write-Host "`nDevelopment environment set up!" -ForegroundColor Green
Write-Host "You can now run commands like: fire, tetris, snake, etc." -ForegroundColor Cyan
Write-Host "Or run 'terminal-toys' for the main menu" -ForegroundColor Cyan 