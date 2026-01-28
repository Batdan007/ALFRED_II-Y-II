@echo off
REM Alfred Global Launcher (Windows)
REM
REM Installation:
REM   1. Add C:\ALFRED_IV-Y-VI\launchers to your PATH environment variable
REM   2. alfred  (from any directory)
REM
REM Or copy to a directory already in PATH:
REM   copy launchers\alfred.bat C:\Windows\System32\alfred.bat
REM
REM Author: Daniel J Rita (BATDAN)

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Determine Alfred root directory
if exist "%SCRIPT_DIR%..\alfred\__init__.py" (
    REM Script is in launchers\ subdirectory
    set ALFRED_ROOT=%SCRIPT_DIR%..
) else if exist "%SCRIPT_DIR%alfred\__init__.py" (
    REM Script is in alfred root
    set ALFRED_ROOT=%SCRIPT_DIR%
) else (
    REM Try to run from current directory
    set ALFRED_ROOT=
)

REM Change to Alfred directory if found
if defined ALFRED_ROOT (
    cd /d "%ALFRED_ROOT%"
)

REM Run Alfred as Python module
python -m alfred %*
