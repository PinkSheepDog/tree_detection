#!/usr/bin/env python3
"""
Startup script for the Tree Detection API backend
"""

import uvicorn
import os
import sys

def main():
    # Check if model file exists
    model_path = 'best.pt'
    if not os.path.exists(model_path):
        print(f"⚠️  Warning: Model file '{model_path}' not found!")
        print("Please ensure your YOLOv7 model file is in the current directory.")
        print("You can update the model path in app.py if needed.")
        print()
    
    # Check if YOLOv7 modules are available
    try:
        from models.experimental import attempt_load
        from utils.general import non_max_suppression, scale_coords
        print("✅ YOLOv7 modules found")
    except ImportError:
        print("❌ YOLOv7 modules not found!")
        print("Please ensure you have the YOLOv7 code in your project directory.")
        print("You can clone it from: https://github.com/WongKinYiu/yolov7")
        sys.exit(1)
    
    print("🚀 Starting Tree Detection API...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 API docs will be available at: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Start the server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 