@echo off
cd /d "%~dp0web\frontend"
echo.
echo ================================
echo Starting BroBro Frontend Server
echo ================================
echo.
echo Path: %~dp0web\frontend
echo Command: npm run dev
echo.
echo Waiting for server to start...
echo.
npm run dev
pause
