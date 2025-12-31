@echo off
echo.
echo ============================================================
echo   ALFRED II-Y-II - One Command Install
echo   The Distinguished British Butler AI
echo ============================================================
echo.

:: Try Python 3.11 first (best compatibility)
py -3.11 --version >nul 2>&1
if not errorlevel 1 (
    echo Using Python 3.11 (recommended)
    py -3.11 -m pip install -r requirements.txt
    py -3.11 -m pip install -e .
    py -3.11 install.py %*
    goto :done
)

:: Try Python 3.12
py -3.12 --version >nul 2>&1
if not errorlevel 1 (
    echo Using Python 3.12
    py -3.12 -m pip install -r requirements.txt
    py -3.12 -m pip install -e .
    py -3.12 install.py %*
    goto :done
)

:: Fallback to default python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.11 from python.org
    pause
    exit /b 1
)

echo WARNING: Using default Python. Recommended: Python 3.11
python install.py %*

:done
echo.
echo ============================================================
echo   To run ALFRED:
echo     alfred              (terminal mode)
echo     alfred --voice      (voice mode)
echo ============================================================
pause
