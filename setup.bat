@echo off
echo 🌳 Setting up Tree Detection for Windows...
echo ==========================================

python setup.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Setup failed! Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✅ Setup completed successfully!
echo.
echo Next steps:
echo 1. Start the backend: python start_backend_cross_platform.py
echo 2. Start the frontend: npm start
echo 3. Open your browser to: http://localhost:3000
echo.
pause 