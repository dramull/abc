#!/bin/bash

# Start script for Docker container

echo "🐳 Starting ABC Multi-Agent Framework in Docker"
echo "================================================"

# Create logs directory
mkdir -p /app/logs

# Start backend
echo "🔄 Starting backend server..."
cd /app/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --log-file /app/logs/backend.log &
BACKEND_PID=$!

# Wait for backend
sleep 5

# Start frontend (in production mode)
echo "🔄 Starting frontend server..."
cd /app/frontend
npx next start --port 3000 --hostname 0.0.0.0 &
FRONTEND_PID=$!

# Wait for frontend
sleep 3

echo "✅ ABC Framework is running!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📋 API Documentation: http://localhost:8000/docs"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait