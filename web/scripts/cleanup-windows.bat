@echo off
echo ========================================
echo BroBro Platform Cleanup Script
echo ========================================
echo.

echo [1/4] Killing all Python processes...
taskkill /F /IM python.exe /T 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Python processes killed
) else (
    echo [WARN] No Python processes found or already stopped
)
timeout /t 2 /nobreak >nul

echo.
echo [2/4] Killing all Node processes...
taskkill /F /IM node.exe /T 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Node processes killed
) else (
    echo [WARN] No Node processes found or already stopped
)
timeout /t 2 /nobreak >nul

echo.
echo [3/4] Checking port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Found process on port 8000: %%a
    taskkill /F /PID %%a 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Killed process %%a on port 8000
    ) else (
        echo [WARN] Could not kill process %%a
    )
)
timeout /t 2 /nobreak >nul

echo.
echo [4/4] Checking port 8001...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 ^| findstr LISTENING') do (
    echo Found process on port 8001: %%a
    taskkill /F /PID %%a 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Killed process %%a on port 8001
    ) else (
        echo [WARN] Could not kill process %%a
    )
)
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo Cleanup Complete!
echo ========================================
echo.
echo If zombie processes still exist, restart your computer.
echo.
pause
