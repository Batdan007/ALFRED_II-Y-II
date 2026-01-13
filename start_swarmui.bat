@echo off
title Starting SwarmUI for ALFRED
echo ========================================
echo   Starting SwarmUI Image Generation
echo   For ALFRED AI Assistant
echo ========================================
echo.

cd /d "C:\Users\danie\OneDrive\Desktop\A.I\SwarmUI-master"

if exist "launch-windows.bat" (
    echo Launching SwarmUI...
    echo.
    echo Once started, SwarmUI will be at: http://localhost:7801
    echo.
    call launch-windows.bat
) else (
    echo ERROR: launch-windows.bat not found!
    echo Looking in: C:\Users\danie\OneDrive\Desktop\A.I\SwarmUI-master
    echo.
    pause
)
