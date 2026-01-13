@echo off
REM ============================================
REM  ALFRED Brain Sync - Sync with Batcave
REM ============================================

echo.
echo  ============================================
echo   ALFRED Brain Sync
echo  ============================================
echo.

cd /d "%~dp0"

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Check if server URL is set
if "%ALFRED_SYNC_SERVER%"=="" (
    echo  ERROR: ALFRED_SYNC_SERVER not set
    echo.
    echo  Set it with:
    echo    set ALFRED_SYNC_SERVER=http://BATCAVE_IP:5050
    echo.
    echo  Or run with:
    echo    python brain_sync_client.py --server http://IP:5050 --sync
    echo.
    pause
    exit /b 1
)

echo  Syncing with: %ALFRED_SYNC_SERVER%
echo.

python brain_sync_client.py --sync

pause
