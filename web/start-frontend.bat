@echo off
echo ========================================
echo BroBro Frontend Development Server
echo ========================================
echo.

cd frontend

echo Installing/Updating Node dependencies...
call npm install

echo.
echo Starting Vite development server on http://localhost:3000
echo.

call npm run dev

pause
