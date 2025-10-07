@echo off
echo 🌳 Testing Cross-Platform Compatibility for Windows...
echo ===================================================

python test_cross_platform.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Some tests failed! Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✅ All tests passed! Your setup is ready.
pause 