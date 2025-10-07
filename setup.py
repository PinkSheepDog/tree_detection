#!/usr/bin/env python3
"""
Cross-platform setup script for Tree Detection Application
"""

import os
import sys
import subprocess
import platform
import shutil
import urllib.request
import zipfile
import tarfile
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

def run_command(command, check=True, capture_output=False):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=check, 
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Command failed: {command}")
            print_error(f"Error: {e}")
        return e

def check_command_exists(command):
    """Check if a command exists in PATH"""
    return shutil.which(command) is not None

def get_python_command():
    """Get the appropriate Python command for the system"""
    python_commands = ['python3.11', 'python3.10', 'python3.9', 'python3', 'python']
    
    for cmd in python_commands:
        if check_command_exists(cmd):
            result = run_command(f"{cmd} --version", capture_output=True)
            if result.returncode == 0:
                print_success(f"Found Python: {result.stdout.strip()}")
                return cmd
    
    print_error("No Python installation found!")
    print_status("Please install Python 3.9 or higher")
    sys.exit(1)

def install_python_dependencies():
    """Install Python dependencies"""
    print_status("Installing Python dependencies...")
    
    # Upgrade pip
    run_command(f"{python_cmd} -m pip install --upgrade pip")
    
    # Install requirements
    if os.path.exists("requirements.txt"):
        run_command(f"{python_cmd} -m pip install -r requirements.txt")
        print_success("Python dependencies installed")
    else:
        print_warning("requirements.txt not found")

def setup_virtual_environment():
    """Create and setup virtual environment"""
    print_status("Setting up virtual environment...")
    
    if not os.path.exists("venv"):
        run_command(f"{python_cmd} -m venv venv")
        print_success("Virtual environment created")
    else:
        print_success("Virtual environment already exists")
    
    # Get the activation script path
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate"
    else:
        activate_script = "venv/bin/activate"
    
    return activate_script

def install_node_dependencies():
    """Install Node.js dependencies"""
    print_status("Installing Node.js dependencies...")
    
    if not check_command_exists("npm"):
        print_error("npm not found! Please install Node.js")
        print_status("Download from: https://nodejs.org/")
        return False
    
    run_command("npm install")
    print_success("Node.js dependencies installed")
    return True

def setup_yolov7():
    """Setup YOLOv7 repository and modules"""
    print_status("Setting up YOLOv7...")
    
    # Clone YOLOv7 if it doesn't exist
    if not os.path.exists("yolov7"):
        print_status("Cloning YOLOv7 repository...")
        run_command("git clone https://github.com/WongKinYiu/yolov7.git")
        print_success("YOLOv7 repository cloned")
    else:
        print_success("YOLOv7 repository already exists")
    
    # Create symbolic links or copy modules
    if platform.system() == "Windows":
        # Windows doesn't support symbolic links easily, so we'll copy
        if not os.path.exists("models"):
            shutil.copytree("yolov7/models", "models")
        if not os.path.exists("utils"):
            shutil.copytree("yolov7/utils", "utils")
    else:
        # Unix-like systems can use symbolic links
        for module in ["models", "utils"]:
            if os.path.exists(module):
                if os.path.islink(module):
                    os.unlink(module)
                else:
                    shutil.rmtree(module)
            os.symlink(f"yolov7/{module}", module)
    
    print_success("YOLOv7 modules setup complete")

def check_model_file():
    """Check if model file exists"""
    model_path = "best.pt"
    if not os.path.exists(model_path):
        print_warning(f"Model file '{model_path}' not found!")
        print_status("Please place your trained YOLOv7 model file in the current directory.")
        print_status("You can update the model path in app.py if needed.")
    else:
        print_success(f"Model file found: {model_path}")

def main():
    global python_cmd
    
    print("🌳 Setting up Tree Detection for all platforms...")
    print("=" * 50)
    
    # Get Python command
    python_cmd = get_python_command()
    
    # Setup virtual environment
    activate_script = setup_virtual_environment()
    
    # Install Python dependencies
    install_python_dependencies()
    
    # Setup YOLOv7
    setup_yolov7()
    
    # Check model file
    check_model_file()
    
    # Install Node.js dependencies
    install_node_dependencies()
    
    print("")
    print("🎉 Setup complete!")
    print("")
    print("Next steps:")
    print("1. Start the backend: python start_backend.py")
    print("2. Start the frontend: npm start")
    print("3. Open your browser to: http://localhost:3000")
    print("")
    print("Happy tree detecting! 🌲")

if __name__ == "__main__":
    main() 