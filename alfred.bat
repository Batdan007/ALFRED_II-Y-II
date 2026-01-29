@echo off
cd /d "%~dp0"
py -3.11 alfred_terminal.py --voice %*
