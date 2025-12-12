@echo off
echo ========================================
echo   Installing Frontend Dependencies
echo ========================================
echo.

cd /d "%~dp0"

echo [*] Checking for Node.js...
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

node --version
npm --version
echo.

echo [*] Installing dependencies...
call npm install

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm install failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo To start the development server, run:
echo   npm start
echo.
pause
