#!/usr/bin/env python3
"""
Cross-platform script to start both backend and frontend servers
"""

import os
import sys
import platform
import subprocess
import time
import signal
import threading
import requests
import psutil
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

class ProcessManager:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def add_process(self, process):
        self.processes.append(process)
    
    def cleanup(self):
        print_status("Stopping servers...")
        for process in self.processes:
            try:
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        print_success("Servers stopped")
    
    def signal_handler(self, signum, frame):
        print("\n")
        self.running = False
        self.cleanup()
        sys.exit(0)

def check_port(port):
    """Check if a port is in use"""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result == 0
    except:
        return False

def kill_process_on_port(port):
    """Kill process running on a specific port"""
    try:
        if platform.system() == "Windows":
            # Windows
            cmd = f"netstat -ano | findstr :{port}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if f":{port}" in line and "LISTENING" in line:
                        parts = line.split()
                        if len(parts) > 4:
                            pid = parts[-1]
                            subprocess.run(f"taskkill /PID {pid} /F", shell=True)
        else:
            # Unix-like systems
            cmd = f"lsof -ti:{port}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        subprocess.run(f"kill -9 {pid}", shell=True)
    except Exception as e:
        print_warning(f"Could not kill process on port {port}: {e}")

def check_virtual_environment():
    """Check if virtual environment exists"""
    if platform.system() == "Windows":
        python_path = "venv\\Scripts\\python.exe"
    else:
        python_path = "venv/bin/python"
    
    if not os.path.exists(python_path):
        print_error("Virtual environment not found!")
        print_status("Please run 'python setup.py' first to set up the environment.")
        return False
    
    print_success("Virtual environment found")
    return True

def check_model_file():
    """Check if model file exists"""
    if not os.path.exists("best.pt"):
        print_warning("Model file 'best.pt' not found!")
        print_status("Please ensure your YOLOv7 model file is in the current directory.")
        return False
    else:
        print_success("Model file found: best.pt")
        return True

def test_backend_imports():
    """Test if backend imports work"""
    print_status("Testing backend imports...")
    
    test_code = """
try:
    from models.experimental import attempt_load
    from utils.general import non_max_suppression, scale_coords
    print('✅ YOLOv7 modules found')
except ImportError as e:
    print('❌ YOLOv7 modules not found!')
    print('Please run python setup.py to set up the environment.')
    exit(1)
"""
    
    result = subprocess.run([sys.executable, "-c", test_code], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print_success("Backend imports successful")
        return True
    else:
        print_error("Backend imports failed!")
        return False

def start_backend(process_manager):
    """Start the backend server"""
    print_status("Starting backend server...")
    
    # Kill any existing process on port 8000
    kill_process_on_port(8000)
    
    # Start backend
    if platform.system() == "Windows":
        cmd = [sys.executable, "start_backend_cross_platform.py"]
    else:
        cmd = [sys.executable, "start_backend_cross_platform.py"]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process_manager.add_process(process)
    
    # Wait for backend to start
    print_status("Waiting for backend to start...")
    for i in range(30):
        if check_port(8000):
            print_success("Backend started successfully on port 8000")
            return True
        time.sleep(1)
    
    print_error("Backend failed to start within 30 seconds")
    return False

def test_backend_health():
    """Test backend health endpoint"""
    print_status("Testing backend health...")
    time.sleep(2)
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print_success("Backend health check passed")
            return True
        else:
            print_error("Backend health check failed")
            return False
    except Exception as e:
        print_error(f"Backend health check failed: {e}")
        return False

def start_frontend(process_manager):
    """Start the frontend server"""
    print_status("Starting frontend server...")
    
    # Kill any existing process on port 3000
    kill_process_on_port(3000)
    
    # Start frontend
    cmd = ["npm", "start"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process_manager.add_process(process)
    
    # Wait for frontend to start
    print_status("Waiting for frontend to start...")
    for i in range(60):
        if check_port(3000):
            print_success("Frontend started successfully on port 3000")
            return True
        time.sleep(1)
    
    print_error("Frontend failed to start within 60 seconds")
    return False

def main():
    print("🌳 Starting Tree Detection Application for all platforms...")
    print("=" * 55)
    
    # Initialize process manager
    process_manager = ProcessManager()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, process_manager.signal_handler)
    signal.signal(signal.SIGTERM, process_manager.signal_handler)
    
    # Check virtual environment
    if not check_virtual_environment():
        sys.exit(1)
    
    # Check model file
    check_model_file()
    
    # Test backend imports
    if not test_backend_imports():
        sys.exit(1)
    
    # Start backend
    if not start_backend(process_manager):
        process_manager.cleanup()
        sys.exit(1)
    
    # Test backend health
    if not test_backend_health():
        process_manager.cleanup()
        sys.exit(1)
    
    # Start frontend
    if not start_frontend(process_manager):
        process_manager.cleanup()
        sys.exit(1)
    
    print("")
    print_success("🎉 Application started successfully!")
    print("")
    print("📍 Frontend: http://localhost:3000")
    print("📍 Backend API: http://localhost:8000")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("📍 Health Check: http://localhost:8000/health")
    print("")
    print_status("Press Ctrl+C to stop both servers")
    print("-" * 50)
    
    # Keep the script running
    try:
        while process_manager.running:
            time.sleep(1)
    except KeyboardInterrupt:
        process_manager.signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main() 