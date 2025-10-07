#!/usr/bin/env python3
"""
Cross-platform startup script for the Tree Detection API backend
"""

import uvicorn
import os
import sys
import platform
import subprocess
import time
import requests
from pathlib import Path

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_status(message):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

def print_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def activate_virtual_environment():
    """Activate virtual environment based on platform"""
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate"
        python_path = "venv\\Scripts\\python.exe"
    else:
        activate_script = "venv/bin/activate"
        python_path = "venv/bin/python"
    
    if not os.path.exists(python_path):
        print_error("Virtual environment not found!")
        print_status("Please run 'python setup.py' first to set up the environment.")
        return None
    
    print_success("Virtual environment found")
    return python_path

def check_model_file():
    """Check if model file exists"""
    model_path = 'best.pt'
    if not os.path.exists(model_path):
        print_warning(f"Model file '{model_path}' not found!")
        print_status("Please ensure your YOLOv7 model file is in the current directory.")
        print_status("You can update the model path in app.py if needed.")
        return False
    else:
        print_success(f"Model file found: {model_path}")
        return True

def check_yolov7_modules():
    """Check if YOLOv7 modules are available"""
    print_status("Checking YOLOv7 modules...")
    
    try:
        # Test imports
        test_code = """
try:
    from models.experimental import attempt_load
    from utils.general import non_max_suppression, scale_coords
    print('✅ YOLOv7 modules found')
except ImportError as e:
    print('❌ YOLOv7 modules not found!')
    print('Please ensure you have the YOLOv7 code in your project directory.')
    print('You can run python setup.py to set up the environment.')
    exit(1)
"""
        
        result = subprocess.run([sys.executable, "-c", test_code], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("YOLOv7 modules found")
            return True
        else:
            print_error("YOLOv7 modules not found!")
            print_status("Please run 'python setup.py' to set up the environment.")
            return False
            
    except Exception as e:
        print_error(f"Error checking YOLOv7 modules: {e}")
        return False

def main():
    print("🌳 Starting Tree Detection Backend for all platforms...")
    print("=" * 55)
    
    # Check virtual environment
    python_path = activate_virtual_environment()
    if not python_path:
        sys.exit(1)
    
    # Check model file
    check_model_file()
    
    # Check YOLOv7 modules
    if not check_yolov7_modules():
        sys.exit(1)
    
    print_success("All checks passed!")
    
    print("")
    print_status("Starting Tree Detection API...")
    print_status("📍 API will be available at: http://localhost:8000")
    print_status("📖 API docs will be available at: http://localhost:8000/docs")
    print_status("🔍 Health check: http://localhost:8000/health")
    print("")
    print_status("Press Ctrl+C to stop the server")
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