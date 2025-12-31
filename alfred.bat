@echo off
:: ALFRED II-Y-II Launcher
cd /d "%~dp0"

:: Use Python 3.11 with the proper module
py -3.11 -m alfred %*
