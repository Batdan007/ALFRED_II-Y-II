@echo off
REM Create Windows Desktop Shortcut for ALFRED Chat
REM Run this script once to add ALFRED to your desktop and start menu

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set ALFRED_DIR=%~dp0..
cd /d "%ALFRED_DIR%"

REM Get username for paths
for /f "tokens=2-4 delims=\ " %%a in ('echo %cd%') do set "USERNAME=%%a"

REM Create desktop shortcut
echo Creating desktop shortcut...

REM Use PowerShell to create shortcut (more reliable)
powershell -NoProfile -Command ^
    "$WshShell = New-Object -ComObject WScript.Shell; " ^
    "$Shortcut = $WshShell.CreateShortcut('%%USERPROFILE%%\Desktop\ALFRED Chat.lnk'); " ^
    "$Shortcut.TargetPath = '%ALFRED_DIR%\launchers\alfred_chat.bat'; " ^
    "$Shortcut.WorkingDirectory = '%ALFRED_DIR%'; " ^
    "$Shortcut.Description = 'ALFRED - Private AI Assistant with Persistent Memory'; " ^
    "$Shortcut.IconLocation = '%ALFRED_DIR%\assets\alfred_icon.ico'; " ^
    "$Shortcut.WindowStyle = 1; " ^
    "$Shortcut.Save()"

if %errorlevel% neq 0 (
    echo Failed to create desktop shortcut
    pause
    exit /b 1
)

echo.
echo ✓ Desktop shortcut created successfully!
echo.

REM Create Start Menu shortcut
echo Creating Start Menu shortcut...

REM Get path to Start Menu programs folder
set START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs

REM Create ALFRED folder in Start Menu
if not exist "%START_MENU%\ALFRED" mkdir "%START_MENU%\ALFRED"

REM Create shortcut
powershell -NoProfile -Command ^
    "$WshShell = New-Object -ComObject WScript.Shell; " ^
    "$Shortcut = $WshShell.CreateShortcut('%START_MENU%\ALFRED\ALFRED Chat.lnk'); " ^
    "$Shortcut.TargetPath = '%ALFRED_DIR%\launchers\alfred_chat.bat'; " ^
    "$Shortcut.WorkingDirectory = '%ALFRED_DIR%'; " ^
    "$Shortcut.Description = 'ALFRED - Private AI Assistant with Persistent Memory'; " ^
    "$Shortcut.WindowStyle = 1; " ^
    "$Shortcut.Save()"

echo ✓ Start Menu shortcut created!
echo.

REM Optional: Create quick launch shortcut
echo Creating Quick Launch shortcut...

powershell -NoProfile -Command ^
    "$WshShell = New-Object -ComObject WScript.Shell; " ^
    "$Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Internet Explorer\Quick Launch\ALFRED Chat.lnk'); " ^
    "$Shortcut.TargetPath = '%ALFRED_DIR%\launchers\alfred_chat.bat'; " ^
    "$Shortcut.WorkingDirectory = '%ALFRED_DIR%'; " ^
    "$Shortcut.Description = 'ALFRED - Private AI Assistant'; " ^
    "$Shortcut.WindowStyle = 1; " ^
    "$Shortcut.Save()"

echo ✓ Quick Launch shortcut created!
echo.

echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo ALFRED is now accessible from:
echo   • Desktop (shortcut icon)
echo   • Start Menu (ALFRED folder)
echo   • Quick Launch bar
echo.
echo To start ALFRED Chat:
echo   1. Click the desktop shortcut, OR
echo   2. Search for "ALFRED Chat" in Start Menu, OR
echo   3. Run: launchers\alfred_chat.bat
echo.
echo Privacy First:
echo   • All data stays on your device by default
echo   • Cloud AI requires your explicit permission
echo   • Install Ollama for maximum privacy
echo.
pause
