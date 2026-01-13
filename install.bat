@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   ALFRED II-Y-II - One-Click Install
echo   The Distinguished British Butler AI
echo ============================================================
echo.

:: Check for Python 3.11 first (recommended)
py -3.11 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=py -3.11
    echo [OK] Found Python 3.11 (recommended)
    goto :install
)

:: Try Python 3.12
py -3.12 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=py -3.12
    echo [OK] Found Python 3.12
    goto :install
)

:: Check default python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python 3.11 from:
    echo   https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

:: Check if default python is compatible
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [WARN] Using Python %PYVER% - Python 3.11 recommended
set PYTHON=python

:install
echo.
echo [INFO] Installing with %PYTHON%...
echo.

:: Upgrade pip first
%PYTHON% -m pip install --upgrade pip --quiet

:: Install requirements
echo [INFO] Installing dependencies...
%PYTHON% -m pip install -r requirements.txt
if errorlevel 1 (
    echo [WARN] Some packages may have failed - continuing...
)

:: Install as editable package
echo [INFO] Registering alfred command...
%PYTHON% -m pip install -e . --quiet

:: Run the full installer for Ollama etc
echo [INFO] Running full setup (Ollama, FFmpeg, models)...
%PYTHON% install.py --skip-venv

echo.
echo ============================================================
echo   Installation Complete!
echo ============================================================
echo.
echo   To run ALFRED:
echo     alfred              (type anywhere)
echo     alfred --voice      (with voice mode)
echo.
echo   First time? ALFRED will use Ollama (local AI).
echo   For cloud AI, set your API keys in .env file.
echo.
pause
