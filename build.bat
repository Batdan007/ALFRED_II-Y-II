@echo off
echo.
echo ============================================================
echo   ALFRED Windows Build
echo ============================================================
echo.

:: Check Python
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.11 not found
    pause
    exit /b 1
)

:: Install PyInstaller if needed
py -3.11 -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    py -3.11 -m pip install pyinstaller
)

:: Build
echo Building ALFRED.exe...
py -3.11 -m PyInstaller ^
    --name=ALFRED ^
    --onefile ^
    --console ^
    --noconfirm ^
    --clean ^
    alfred/__main__.py

if exist dist\ALFRED.exe (
    echo.
    echo ============================================================
    echo   BUILD SUCCESS!
    echo   Output: dist\ALFRED.exe
    echo.
    echo   Test with: dist\ALFRED.exe --help
    echo ============================================================
) else (
    echo BUILD FAILED
)

pause
