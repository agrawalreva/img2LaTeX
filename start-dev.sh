#!/bin/bash

# Start development environment

echo "Starting img2LaTeX AI..."

cleanup() {
    echo "Stopping services..."
    pkill -f "uvicorn app.main:app" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "Starting backend..."
cd apps/api
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 3

echo "Testing backend..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "Backend running on http://localhost:8000"
else
    echo "Backend failed to start"
    cleanup
fi

echo "Starting frontend..."
cd ../web
npm run dev &
FRONTEND_PID=$!

sleep 5

echo ""
echo "img2LaTeX AI is running"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"

wait
