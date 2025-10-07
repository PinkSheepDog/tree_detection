#!/bin/bash

echo "🌳 Setting up Tree Detection for Unix/Linux..."
echo "==============================================="

python3 setup.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Setup failed! Please check the error messages above."
    exit 1
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Start the backend: python3 start_backend_cross_platform.py"
echo "2. Start the frontend: npm start"
echo "3. Open your browser to: http://localhost:3000"
echo "" 