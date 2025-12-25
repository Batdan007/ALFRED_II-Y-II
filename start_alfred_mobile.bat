@echo off
echo ============================================
echo   ALFRED Mobile Server
echo   Access from iPhone at: http://YOUR_IP:5000
echo ============================================
echo.

REM Get local IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    goto :found
)
:found
set IP=%IP:~1%

echo Your local IP: %IP%
echo.
echo On your iPhone:
echo   1. Open Safari
echo   2. Go to: http://%IP%:5000
echo   3. Tap Share button
echo   4. Tap "Add to Home Screen"
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

cd /d "%~dp0"
python alfred_api_server.py
