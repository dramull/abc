@echo off
rem ABC Multi-Agent Framework Startup Script for Windows
rem This script starts both the backend and frontend servers

echo 🚀 Starting ABC Multi-Agent Framework
echo ======================================

rem Check if .env file exists
if not exist ".env" (
    echo ⚠️  No .env file found. Creating from template...
    copy .env.example .env
    echo 📝 Please edit .env and add your Kimi K2 API key
)

echo.
echo 🔧 Configuration:
echo    Backend:  http://localhost:8000
echo    Frontend: http://localhost:3000
echo    API Docs: http://localhost:8000/docs
echo.

rem Check if Python dependencies are installed
python -c "import fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo 📦 Installing Python dependencies...
    pip install -r requirements.txt
)

rem Check if Node.js dependencies are installed
if not exist "node_modules" (
    echo 📦 Installing Node.js dependencies...
    npm install
)

echo 🔄 Starting backend server...
start "ABC Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

rem Wait a moment for backend to start
timeout /t 3 /nobreak >nul

echo 🔄 Starting frontend server...
start "ABC Frontend" cmd /k "npm run dev"

rem Wait for frontend to start
timeout /t 5 /nobreak >nul

echo.
echo ✅ Both servers are starting up!
echo 🌐 Open http://localhost:3000 in your browser
echo.
echo Press any key to stop both servers and exit...

pause >nul

rem Close the server windows
taskkill /f /im "cmd.exe" /fi "WINDOWTITLE eq ABC Backend*" 2>nul
taskkill /f /im "cmd.exe" /fi "WINDOWTITLE eq ABC Frontend*" 2>nul

echo 🛑 Servers stopped.
pause