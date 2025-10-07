@echo off
echo 🌳 Starting Tree Detection Backend for Windows...
echo ===============================================

python start_backend_cross_platform.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Backend failed to start! Please check the error messages above.
    pause
    exit /b 1
) 