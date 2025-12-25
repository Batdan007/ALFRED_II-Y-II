# ALFRED Chat Launcher for Windows PowerShell
# Start ALFRED with full capabilities in modern chat interface
# Usage: .\alfred_chat.ps1

param(
    [switch]$SkipOllama = $false,
    [int]$Port = 8000,
    [string]$Host = "127.0.0.1"
)

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AlfredDir = Split-Path -Parent $ScriptDir
Set-Location $AlfredDir

Write-Host "================================" -ForegroundColor Cyan
Write-Host "ALFRED Chat Launcher" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $PythonVersion = python --version 2>&1 | Select-String -Pattern "Python"
    Write-Host "✓ Python found: $PythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "  Please install Python 3.10+ from https://www.python.org" -ForegroundColor Yellow
    exit 1
}

# Check if required dependencies are installed
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Cyan

try {
    python -c "import fastapi, uvicorn" 2>$null
    Write-Host "✓ FastAPI and Uvicorn found" -ForegroundColor Green
} catch {
    Write-Host "⚠ Installing missing dependencies..." -ForegroundColor Yellow
    pip install -q fastapi "uvicorn[standard]" aiohttp
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
}

# Check if Ollama is running (local-first privacy)
Write-Host ""
Write-Host "Checking for Ollama (local AI)..." -ForegroundColor Cyan

$OllamaRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/version" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✓ Ollama is running" -ForegroundColor Green
    $OllamaRunning = $true
} catch {
    if (-not $SkipOllama) {
        Write-Host "⚠ Ollama not detected" -ForegroundColor Yellow
        Write-Host "  For best privacy: Install Ollama from https://ollama.ai" -ForegroundColor Yellow
    }
}

# Display privacy info
Write-Host ""
Write-Host "PRIVACY SETTINGS:" -ForegroundColor Cyan
Write-Host "  Default Mode: LOCAL-FIRST" -ForegroundColor Green
Write-Host "  Your data stays on your device unless you explicitly approve cloud access" -ForegroundColor Green
Write-Host "  Cloud AI: Requires your permission" -ForegroundColor Yellow

if ($OllamaRunning) {
    Write-Host "  Local AI: Available (Ollama)" -ForegroundColor Green
} else {
    Write-Host "  Local AI: Not available (install Ollama for privacy)" -ForegroundColor Yellow
}

# Start ALFRED Chat
Write-Host ""
Write-Host "Starting ALFRED Chat Server..." -ForegroundColor Cyan
Write-Host "  Host: $Host" -ForegroundColor Yellow
Write-Host "  Port: $Port" -ForegroundColor Yellow
Write-Host ""

# Start server in new window
$ServerProcess = Start-Process -FilePath python -ArgumentList "ui/chat_interface.py" -PassThru -NoNewWindow

# Wait for server to start
Write-Host "Waiting for server to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

# Open browser
Write-Host ""
Write-Host "Opening browser..." -ForegroundColor Cyan
Start-Process "http://localhost:$Port"

# Display running info
Write-Host ""
Write-Host "════════════════════════════════" -ForegroundColor Green
Write-Host "✓ ALFRED Chat is running!" -ForegroundColor Green
Write-Host "════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "  Open:  http://localhost:$Port" -ForegroundColor Cyan
Write-Host "  PID:   $($ServerProcess.Id)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Keep script running
$ServerProcess | Wait-Process
