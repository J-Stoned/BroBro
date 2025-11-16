@echo off
REM BroBro - Complete Server Startup Script (Windows)
REM Starts both FastAPI backend and Vite frontend in separate console windows

title BroBro - Server Startup

echo ==================================
echo   BroBro - Server Startup
echo ==================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js 16+
    pause
    exit /b 1
)

echo [1] Starting FastAPI Backend...
echo     Location: web\backend
echo.

REM Start backend in new window
cd /d "%~dp0\web\backend"
start cmd /k "title BroBro - FastAPI Backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a bit for backend to start
timeout /t 3 /nobreak

REM Start frontend in new window
cd /d "%~dp0\web\frontend"
echo [2] Starting Vite Frontend...
echo     Location: web\frontend
echo.
start cmd /k "title BroBro - Vite Frontend && npm run dev"

echo ==================================
echo   Both servers starting!
echo ==================================
echo.
echo Frontend: http://localhost:5173
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Check the separate console windows for server output.
echo.

pause
