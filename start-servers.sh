#!/bin/bash
# BroBro - Complete Server Startup Script
# Starts both FastAPI backend and Vite frontend

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=================================="
echo "  BroBro - Server Startup"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}[ERROR] Python not found. Please install Python 3.8+${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}[ERROR] Node.js not found. Please install Node.js 16+${NC}"
    exit 1
fi

echo -e "${BLUE}[1] Starting FastAPI Backend...${NC}"
echo "    Location: web/backend"
echo ""

# Start FastAPI backend in background
cd web/backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo "    API: http://localhost:8000"
echo "    Docs: http://localhost:8000/docs"
echo ""

# Wait a bit for backend to start
sleep 3

# Start frontend
cd ../frontend
echo -e "${BLUE}[2] Starting Vite Frontend...${NC}"
echo "    Location: web/frontend"
echo ""

npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo "    URL: http://localhost:5173"
echo ""

echo "=================================="
echo -e "${GREEN}  Both servers running!${NC}"
echo "=================================="
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "To stop all servers, press Ctrl+C"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID

echo -e "${YELLOW}Servers stopped${NC}"
