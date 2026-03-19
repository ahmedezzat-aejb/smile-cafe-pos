@echo off
chcp 65001 >nul
title Smile Cafe POS Server

echo.
echo ========================================
echo     SMILE CAFE POS SYSTEM
echo ========================================
echo.
echo Starting server...
echo.

python simple_server.py

echo.
echo Server stopped. Press any key to exit...
pause >nul
