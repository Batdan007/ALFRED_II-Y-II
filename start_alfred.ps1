# ALFRED II-Y-II Startup Script
# Author: Daniel J Rita (BATDAN)

$Host.UI.RawUI.WindowTitle = "ALFRED II-Y-II - British Butler AI"

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "   ALFRED II-Y-II - The Distinguished British Butler" -ForegroundColor Cyan
Write-Host "   Patent-Pending AI with Permanent Memory" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Set environment
$env:ALFRED_HOME = "C:\Drive"
$env:PYTHONIOENCODING = "utf-8"

# Check Ollama
Write-Host "Checking Ollama..." -ForegroundColor Yellow
try {
    $null = Invoke-WebRequest -Uri "http://localhost:11434/api/version" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "  Starting Ollama..." -ForegroundColor Yellow
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

# Launch Alfred
Write-Host ""
Write-Host "Launching Alfred Terminal..." -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot
python alfred_terminal.py
