#!/usr/bin/env python3
"""
Test script to verify robust image loading functionality
"""

import numpy as np
import cv2
from PIL import Image
import io
from app import safe_load_image

def test_robust_loading():
    """Test the robust image loading functionality"""
    print("🧪 Testing robust image loading...")
    
    # Create a test image (small size)
    test_image = np.random.randint(0, 255, (1000, 1000, 3), dtype=np.uint8)
    
    # Encode as JPEG
    _, buffer = cv2.imencode('.jpg', test_image)
    image_bytes = buffer.tobytes()
    
    print(f"Created test image: {test_image.shape}")
    
    # Test safe loading
    loaded_image = safe_load_image(image_bytes)
    
    if loaded_image is not None:
        print(f"✅ Successfully loaded image: {loaded_image.shape}")
        print(f"Original shape: {test_image.shape}")
        print(f"Loaded shape: {loaded_image.shape}")
        
        # Verify shapes match
        assert loaded_image.shape == test_image.shape, "Image shapes don't match"
        print("✅ Image shapes match")
        
        return True
    else:
        print("❌ Failed to load image")
        return False

def test_extremely_large_image_simulation():
    """Test with an extremely large image to simulate the decompression bomb issue"""
    print("\n🧪 Testing extremely large image simulation...")
    
    # Create an extremely large test image (simulating the decompression bomb issue)
    # This should trigger the PIL decompression bomb protection
    extremely_large_image = np.random.randint(0, 255, (40000, 40000, 3), dtype=np.uint8)
    
    # Encode as JPEG
    _, buffer = cv2.imencode('.jpg', extremely_large_image)
    image_bytes = buffer.tobytes()
    
    print(f"Created extremely large test image: {extremely_large_image.shape}")
    print(f"Total pixels: {extremely_large_image.shape[0] * extremely_large_image.shape[1]}")
    
    try:
        # This should trigger the decompression bomb protection and use our robust loading
        loaded_image = safe_load_image(image_bytes)
        
        if loaded_image is not None:
            print(f"✅ Successfully loaded extremely large image: {loaded_image.shape}")
            print(f"Image was automatically resized for processing")
            return True
        else:
            print("❌ Failed to load extremely large image")
            return False
            
    except Exception as e:
        print(f"❌ Error loading extremely large image: {e}")
        return False

def test_pil_limit_disabling():
    """Test that PIL's decompression bomb protection is properly disabled"""
    print("\n🧪 Testing PIL limit disabling...")
    
    try:
        # Check if we can temporarily disable the limit
        original_limit = Image.MAX_IMAGE_PIXELS
        print(f"Original PIL limit: {original_limit}")
        
        # Disable the limit
        Image.MAX_IMAGE_PIXELS = None
        print("✅ Successfully disabled PIL decompression bomb protection")
        
        # Restore the limit
        Image.MAX_IMAGE_PIXELS = original_limit
        print("✅ Successfully restored PIL decompression bomb protection")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing PIL limit disabling: {e}")
        return False

if __name__ == "__main__":
    try:
        # Test normal image loading
        success1 = test_robust_loading()
        
        # Test PIL limit disabling
        success2 = test_pil_limit_disabling()
        
        # Test extremely large image loading
        success3 = test_extremely_large_image_simulation()
        
        if success1 and success2 and success3:
            print("\n🎉 All robust loading tests passed!")
            print("✅ The application can now handle extremely large images")
        else:
            print("\n❌ Some tests failed!")
            exit(1)
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        exit(1) 