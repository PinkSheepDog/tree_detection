#!/usr/bin/env python3
"""
Simple script to run the large image processing pipeline
"""

import sys
import os
from image_processor import ImageProcessor

def main():
    if len(sys.argv) != 2:
        print("Usage: python run_pipeline.py <image_path>")
        print("Example: python run_pipeline.py large_image.tif")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    print(f"🌳 Starting tree detection pipeline for: {image_path}")
    print("=" * 50)
    
    # Initialize processor
    processor = ImageProcessor()
    
    # Process the image
    result = processor.process_large_image(image_path)
    
    # Display results
    print("\n" + "=" * 50)
    print("🎯 FINAL RESULTS")
    print("=" * 50)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)
    
    print(f"🌲 Total Trees Detected: {result['totalTreeCount']}")
    print(f"⏱️  Total Processing Time: {result['totalTime']} seconds")
    print(f"📊 Average Time per Tile: {result['averageProcessingTime']} seconds")
    print(f"🧩 Tiles Processed: {result['tilesProcessed']}")
    
    if result['allDetections']:
        print(f"\n📍 Detection Details:")
        for i, detection in enumerate(result['allDetections'][:10]):  # Show first 10
            bbox = detection['bbox']
            print(f"  Tree {i+1}: Confidence {detection['confidence']}% at ({bbox['x']}, {bbox['y']})")
        if len(result['allDetections']) > 10:
            print(f"  ... and {len(result['allDetections']) - 10} more detections")
    
    print("\n✅ Pipeline completed successfully!")

if __name__ == "__main__":
    main() 