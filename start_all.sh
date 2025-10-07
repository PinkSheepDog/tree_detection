#!/bin/bash

echo "🌳 Starting Tree Detection Application for Unix/Linux..."
echo "======================================================="

python3 start_all_cross_platform.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Application failed to start! Please check the error messages above."
    exit 1
fi 