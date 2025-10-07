#!/usr/bin/env python3
"""
Test script to verify cross-platform compatibility
"""

import os
import sys
import platform
import subprocess
import importlib.util

def print_status(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def test_python_version():
    """Test Python version compatibility"""
    print_info("Testing Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} is not compatible (need 3.9+)")
        return False

def test_platform_detection():
    """Test platform detection"""
    print_info("Testing platform detection...")
    system = platform.system()
    print_status(f"Detected platform: {system}")
    return True

def test_virtual_environment():
    """Test virtual environment setup"""
    print_info("Testing virtual environment...")
    
    if platform.system() == "Windows":
        python_path = "venv\\Scripts\\python.exe"
    else:
        python_path = "venv/bin/python"
    
    if os.path.exists(python_path):
        print_status("Virtual environment found")
        return True
    else:
        print_error("Virtual environment not found")
        return False

def test_yolov7_modules():
    """Test YOLOv7 module availability"""
    print_info("Testing YOLOv7 modules...")
    
    try:
        # Test if modules can be imported
        test_code = """
try:
    from models.experimental import attempt_load
    from utils.general import non_max_suppression, scale_coords
    print('YOLOv7 modules found')
except ImportError as e:
    print(f'YOLOv7 modules not found: {e}')
    exit(1)
"""
        
        result = subprocess.run([sys.executable, "-c", test_code], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print_status("YOLOv7 modules are available")
            return True
        else:
            print_error("YOLOv7 modules are not available")
            return False
            
    except Exception as e:
        print_error(f"Error testing YOLOv7 modules: {e}")
        return False

def test_model_file():
    """Test model file existence"""
    print_info("Testing model file...")
    
    if os.path.exists("best.pt"):
        print_status("Model file found")
        return True
    else:
        print_error("Model file not found (best.pt)")
        return False

def test_node_dependencies():
    """Test Node.js dependencies"""
    print_info("Testing Node.js dependencies...")
    
    if not os.path.exists("node_modules"):
        print_error("Node.js dependencies not installed")
        return False
    
    if not os.path.exists("package.json"):
        print_error("package.json not found")
        return False
    
    print_status("Node.js dependencies found")
    return True

def test_ports():
    """Test if required ports are available"""
    print_info("Testing port availability...")
    
    import socket
    
    ports_to_test = [8000, 3000]
    available_ports = []
    
    for port in ports_to_test:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                if result != 0:
                    available_ports.append(port)
                else:
                    print_error(f"Port {port} is already in use")
        except Exception as e:
            print_error(f"Error testing port {port}: {e}")
    
    if len(available_ports) == len(ports_to_test):
        print_status("All required ports are available")
        return True
    else:
        print_error("Some required ports are not available")
        return False

def main():
    print("🌳 Testing Cross-Platform Compatibility")
    print("=" * 40)
    
    tests = [
        ("Python Version", test_python_version),
        ("Platform Detection", test_platform_detection),
        ("Virtual Environment", test_virtual_environment),
        ("YOLOv7 Modules", test_yolov7_modules),
        ("Model File", test_model_file),
        ("Node.js Dependencies", test_node_dependencies),
        ("Port Availability", test_ports),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
    
    print(f"\n{'='*40}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print_status("All tests passed! Your setup is ready.")
        print_info("You can now run:")
        print_info("  python start_all_cross_platform.py")
    else:
        print_error("Some tests failed. Please check the setup.")
        print_info("Run 'python setup.py' to fix issues.")

if __name__ == "__main__":
    main() 