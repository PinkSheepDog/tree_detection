#!/usr/bin/env python3
"""
Test script to check model loading
"""

import os
import sys

def test_model_loading():
    """Test if the model can be loaded"""
    print("🧪 Testing model loading...")
    
    # Check if model file exists
    model_path = 'best.pt'
    if not os.path.exists(model_path):
        print(f"❌ Model file '{model_path}' not found!")
        return False
    
    print(f"✅ Model file found: {model_path}")
    print(f"📁 File size: {os.path.getsize(model_path) / (1024*1024):.2f} MB")
    
    # Check if YOLOv7 modules are available
    try:
        from models.experimental import attempt_load
        from utils.general import non_max_suppression, scale_coords
        print("✅ YOLOv7 modules imported successfully")
    except ImportError as e:
        print(f"❌ YOLOv7 modules import failed: {e}")
        return False
    
    # Try to load the model
    try:
        import torch
        
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"✅ Using device: {device}")
        
        model = attempt_load(model_path, map_location=device)
        model.eval()
        print("✅ Model loaded successfully!")
        
        # Test a simple inference
        print("🧪 Testing simple inference...")
        dummy_input = torch.randn(1, 3, 640, 640).to(device)
        
        with torch.no_grad():
            output = model(dummy_input, augment=False)[0]
            print(f"✅ Inference test passed! Output shape: {output.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_model_loading()
    
    if success:
        print("\n🎉 Model loading test passed!")
    else:
        print("\n❌ Model loading test failed!")
        sys.exit(1) 