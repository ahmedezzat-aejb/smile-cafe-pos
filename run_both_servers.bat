@echo off
chcp 65001 >nul
title SMILE CAFE POS - Dual Servers

echo.
echo ========================================
echo     SMILE CAFE POS - DUAL SERVERS
echo ========================================
echo.
echo Starting Flask Server (Port 5000)...
echo.

start "Flask Server" cmd /k "python app.py"

timeout /t 3 /nobreak >nul

echo.
echo Starting Simple Server (Port 8000)...
echo.

start "Simple Server" cmd /k "python simple_server.py"

echo.
echo ========================================
echo Both servers are starting...
echo.
echo Flask Server: http://localhost:5000
echo   - Admin Panel: http://localhost:5000/admin
echo   - POS System:  http://localhost:5000/
echo.
echo Simple Server: http://localhost:8000
echo   - Main Page:   http://localhost:8000/index.html
echo   - POS:         http://localhost:8000/templates/pos.html
echo   - Admin:       http://localhost:8000/admin.html
echo ========================================
echo.
echo Press any key to exit...
pause >nul
