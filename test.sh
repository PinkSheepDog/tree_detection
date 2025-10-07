#!/bin/bash

echo "🌳 Testing Cross-Platform Compatibility for Unix/Linux..."
echo "========================================================"

python3 test_cross_platform.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Some tests failed! Please check the error messages above."
    exit 1
fi

echo ""
echo "✅ All tests passed! Your setup is ready." 