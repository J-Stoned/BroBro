@echo off
echo ========================================
echo BroBro Backend Server
echo ========================================
echo.

cd backend

echo Installing/Updating Python dependencies...
pip install -r requirements.txt

echo.
echo Starting FastAPI server on http://localhost:8000
echo API Docs available at: http://localhost:8000/docs
echo.

python main.py

pause
