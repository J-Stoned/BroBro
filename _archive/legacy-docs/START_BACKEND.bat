@echo off
cd /d "%~dp0web\backend"
echo.
echo ================================
echo Starting BroBro Backend Server
echo ================================
echo.
echo Path: %~dp0web\backend
echo Command: python main.py
echo.
echo Waiting for server to start...
echo.
python main.py
pause
