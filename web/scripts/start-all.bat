@echo off
echo ========================================
echo BroBro Platform Startup
echo ========================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

echo Starting services...
echo.

echo [1/3] Starting ChromaDB on port 8001...
start "ChromaDB" cmd /k "cd /d %PROJECT_ROOT%\.. && npm run start-chroma"
timeout /t 5 /nobreak >nul

echo [2/3] Starting Backend on port 8000...
start "Backend" cmd /k "cd /d %PROJECT_ROOT%\backend && python main.py"
timeout /t 5 /nobreak >nul

echo [3/3] Starting Frontend on port 3000...
start "Frontend" cmd /k "cd /d %PROJECT_ROOT%\frontend && npm run dev"

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo ChromaDB:  http://localhost:8001
echo Backend:   http://localhost:8000
echo Frontend:  http://localhost:3000
echo.
echo Check the opened terminal windows for status.
echo Close this window when done.
pause
