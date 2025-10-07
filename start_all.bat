@echo off
echo 🌳 Starting Tree Detection Application for Windows...
echo ==================================================

python start_all_cross_platform.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Application failed to start! Please check the error messages above.
    pause
    exit /b 1
) 