@echo off
REM ALFRED Chat Launcher for Windows
REM Start ALFRED with full capabilities in modern chat interface
REM Creates desktop shortcut for easy access

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set ALFRED_DIR=%~dp0
cd /d "%ALFRED_DIR%"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org
    pause
    exit /b 1
)

REM Check if required dependencies are installed
python -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo Installing required dependencies...
    pip install -q fastapi uvicorn[standard] aiohttp
    if errorlevel 1 (
        echo Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if Ollama is running (local-first privacy)
echo Checking for Ollama (local AI)...
python -c "import requests; requests.get('http://localhost:11434/api/version', timeout=2)" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Note: Ollama not detected. ALFRED can still use Claude or other models,
    echo but will require cloud access (you'll be asked for permission).
    echo.
    echo For best privacy: Install Ollama from https://ollama.ai
    echo.
    choice /C YN /M "Continue without local Ollama?"
    if errorlevel 2 (
        exit /b 0
    )
)

REM Start ALFRED Chat
echo.
echo Starting ALFRED Chat Server...
echo.
echo Privacy Mode: LOCAL-FIRST (your data stays on your device)
echo Opening browser in 3 seconds...
echo.

REM Start the server in background
start "" python ui\chat_interface.py

REM Wait for server to start
timeout /t 3 /nobreak

REM Open browser
start http://localhost:8000

REM Keep window open for logs
echo.
echo ALFRED Chat is running at http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.
pause
