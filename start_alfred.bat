@echo off
title ALFRED II-Y-II - British Butler AI
color 0A

echo.
echo ====================================================
echo    ALFRED II-Y-II - The Distinguished British Butler
echo    Patent-Pending AI with Permanent Memory
echo ====================================================
echo.

REM Set environment
set ALFRED_HOME=C:\Drive
set PYTHONIOENCODING=utf-8

REM Check Ollama
echo Checking Ollama...
curl -s http://localhost:11434/api/version >nul 2>&1
if errorlevel 1 (
    echo Starting Ollama...
    start /B ollama serve
    timeout /t 3 /nobreak >nul
)

REM Launch Alfred
echo.
echo Launching Alfred Terminal...
echo.
cd /d "%~dp0"
python alfred_terminal.py

pause
