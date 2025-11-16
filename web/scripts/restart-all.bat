@echo off
echo ========================================
echo BroBro Platform - Full Restart
echo ========================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0

echo Step 1: Cleaning up old processes...
call "%SCRIPT_DIR%cleanup-windows.bat"

echo.
echo Step 2: Starting all services...
call "%SCRIPT_DIR%start-all.bat"

echo.
echo Done! Platform should be running.
pause
