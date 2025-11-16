@echo off
echo ========================================
echo BroBro Desktop - Quick Start
echo ========================================
echo.

cd /d "C:\Users\justi\BroBro\brobro-desktop"

echo Checking if node_modules exists...
if not exist "node_modules\" (
    echo.
    echo [1/2] Installing dependencies...
    echo This will take 2-3 minutes...
    call npm install
    echo.
    echo Dependencies installed!
) else (
    echo Dependencies already installed!
)

echo.
echo [2/2] Starting BroBro Desktop...
echo.
echo IMPORTANT: Make sure your FastAPI backend is running!
echo Backend should be at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the app
echo.

call npm run electron:dev

pause
