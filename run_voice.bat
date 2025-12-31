@echo off
echo.
echo ============================================================
echo    A.L.F.R.E.D. Voice Interface
echo ============================================================
echo.

:: Check if venv exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

:: Check Ollama
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo WARNING: Ollama not running!
    echo Start Ollama first: ollama serve
    echo.
    pause
    exit /b 1
)

:: Run ALFRED
python alfred_voice_loop.py %*

pause
