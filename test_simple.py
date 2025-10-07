#!/usr/bin/env python3
"""
Simple test script to verify basic functionality
"""

import sys
import os

def test_basic_imports():
    """Test basic imports"""
    print("🧪 Testing basic imports...")
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ PIL imported successfully")
    except ImportError as e:
        print(f"❌ PIL import failed: {e}")
        return False
    
    return True

def test_safe_load_image():
    """Test the safe_load_image function"""
    print("\n🧪 Testing safe_load_image function...")
    
    try:
        # Import the function
        from app import safe_load_image
        print("✅ safe_load_image imported successfully")
        
        # Create a simple test image
        import numpy as np
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Encode as JPEG
        import cv2
        _, buffer = cv2.imencode('.jpg', test_image)
        image_bytes = buffer.tobytes()
        
        # Test loading
        loaded_image = safe_load_image(image_bytes)
        
        if loaded_image is not None:
            print(f"✅ Successfully loaded image: {loaded_image.shape}")
            return True
        else:
            print("❌ Failed to load image")
            return False
            
    except Exception as e:
        print(f"❌ Error testing safe_load_image: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting simple tests...")
    
    # Test basic imports
    success1 = test_basic_imports()
    
    if success1:
        # Test safe_load_image function
        success2 = test_safe_load_image()
        
        if success2:
            print("\n🎉 All simple tests passed!")
        else:
            print("\n❌ safe_load_image test failed!")
            sys.exit(1)
    else:
        print("\n❌ Basic import tests failed!")
        sys.exit(1) 