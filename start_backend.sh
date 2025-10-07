#!/bin/bash

echo "🌳 Starting Tree Detection Backend for Unix/Linux..."
echo "===================================================="

python3 start_backend_cross_platform.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Backend failed to start! Please check the error messages above."
    exit 1
fi 