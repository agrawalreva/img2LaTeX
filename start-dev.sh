#!/bin/bash

# Start img2LaTeX AI development environment

echo "🚀 Starting img2LaTeX AI..."

# Function to cleanup background processes
cleanup() {
    echo "🛑 Stopping services..."
    pkill -f "uvicorn app.main:app" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    exit 0
}

# Set up cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start backend
echo "📡 Starting backend (FastAPI)..."
cd apps/api
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Test backend
echo "🔍 Testing backend..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "❌ Backend failed to start"
    cleanup
fi

# Start frontend
echo "🎨 Starting frontend (React)..."
cd ../web
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 5

echo ""
echo "🎉 img2LaTeX AI is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
wait
