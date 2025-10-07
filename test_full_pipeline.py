#!/usr/bin/env python3
"""
Test the full pipeline - backend API and image processing
"""

import requests
import numpy as np
import cv2
import base64
import io
import time

def test_backend_health():
    """Test backend health endpoint"""
    print("🧪 Testing backend health...")
    
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend health: {data}")
            return data.get("model_loaded", False)
        else:
            print(f"❌ Backend health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health error: {e}")
        return False

def test_backend_root():
    """Test backend root endpoint"""
    print("\n🧪 Testing backend root endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend root: {data}")
            return True
        else:
            print(f"❌ Backend root failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend root error: {e}")
        return False

def test_image_upload():
    """Test image upload and processing"""
    print("\n🧪 Testing image upload and processing...")
    
    # Create a test image
    test_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    
    # Encode as JPEG
    _, buffer = cv2.imencode('.jpg', test_image)
    image_bytes = buffer.tobytes()
    
    # Create a file-like object
    files = {'file': ('test_image.jpg', image_bytes, 'image/jpeg')}
    
    try:
        response = requests.post("http://localhost:8000/api/detect-trees", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Image processing successful!")
            print(f"   - Trees detected: {data.get('treeCount', 0)}")
            print(f"   - Confidence: {data.get('confidence', 0)}%")
            print(f"   - Processing time: {data.get('processingTime', 0)}s")
            print(f"   - Processing method: {data.get('processingMethod', 'unknown')}")
            return True
        else:
            print(f"❌ Image processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Image processing error: {e}")
        return False

def test_frontend_connection():
    """Test frontend connection"""
    print("\n🧪 Testing frontend connection...")
    
    try:
        response = requests.get("http://localhost:3000")
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend connection error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting full pipeline test...")
    print("=" * 50)
    
    # Test backend health
    backend_healthy = test_backend_health()
    
    # Test backend root
    backend_root = test_backend_root()
    
    # Test image upload (only if backend is healthy)
    image_processing = False
    if backend_healthy:
        image_processing = test_image_upload()
    else:
        print("\n⚠️  Skipping image processing test - backend not healthy")
    
    # Test frontend
    frontend_accessible = test_frontend_connection()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"   Backend Health: {'✅ PASS' if backend_healthy else '❌ FAIL'}")
    print(f"   Backend Root: {'✅ PASS' if backend_root else '❌ FAIL'}")
    print(f"   Image Processing: {'✅ PASS' if image_processing else '❌ FAIL'}")
    print(f"   Frontend Access: {'✅ PASS' if frontend_accessible else '❌ FAIL'}")
    
    if backend_healthy and backend_root and image_processing and frontend_accessible:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Your tree detection system is working correctly!")
        print("\n🌐 You can now:")
        print("   - Access the frontend at: http://localhost:3000")
        print("   - Access the backend API at: http://localhost:8000")
        print("   - View API docs at: http://localhost:8000/docs")
        return True
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Please check the errors above and fix the issues.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 