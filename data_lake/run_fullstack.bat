@echo off
echo ========================================
echo   Starting Full Stack Application
echo ========================================
echo.
echo   Backend:  http://localhost:5000
echo   Frontend: http://localhost:3000
echo.
echo   Press Ctrl+C to stop both servers
echo ========================================
echo.

cd /d "%~dp0"

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup_venv.bat first
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo [ERROR] Frontend dependencies not installed!
    echo Please run frontend\setup_frontend.bat first
    pause
    exit /b 1
)

echo [*] Starting Flask backend...
start "Flask Backend" cmd /k "cd /d %~dp0 && venv\Scripts\activate && python api_panel\app.py"

timeout /t 3 /nobreak >nul

echo [*] Starting React frontend...
start "React Frontend" cmd /k "cd /d %~dp0\frontend && npm start"

echo.
echo [✓] Both servers are starting!
echo.
echo Press any key to close this window (servers will keep running)
pause >nul
