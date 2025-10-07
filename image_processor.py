import cv2
import numpy as np
import requests
import base64
import json
import time
from PIL import Image
import os
import io
from typing import List, Dict, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_load_image_from_path(image_path: str) -> np.ndarray:
    """
    Safely load image from file path using PIL to handle large images that OpenCV can't process
    """
    try:
        # First try OpenCV for smaller images
        image = cv2.imread(image_path)
        if image is not None:
            return image
    except Exception as e:
        logger.warning(f"OpenCV failed to load image: {e}")
    
    # If OpenCV fails, use PIL for large images
    try:
        # Temporarily disable PIL's decompression bomb protection
        Image.MAX_IMAGE_PIXELS = None
        
        # Use PIL for TIFF files as OpenCV might have issues with large TIFFs
        pil_image = Image.open(image_path)
        
        # Check if image is extremely large and needs resizing
        width, height = pil_image.size
        total_pixels = width * height
        max_pixels = 50000000  # 50 million pixels limit (more conservative)
        
        if total_pixels > max_pixels:
            logger.info(f"Image too large ({total_pixels} pixels), resizing...")
            # Calculate new size while preserving aspect ratio
            aspect_ratio = width / height
            if width > height:
                new_width = int(np.sqrt(max_pixels * aspect_ratio))
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = int(np.sqrt(max_pixels / aspect_ratio))
                new_width = int(new_height * aspect_ratio)
            
            logger.info(f"Resizing from {width}x{height} to {new_width}x{new_height}")
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to RGB if needed
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        # Convert to numpy array
        image = np.array(pil_image)
        # Convert RGB to BGR for OpenCV
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        logger.info(f"Successfully loaded image with PIL: {image.shape}")
        return image
        
    except Exception as e:
        logger.error(f"PIL failed to load image: {e}")
        # Try with even more aggressive resizing
        try:
            logger.info("Attempting aggressive resizing...")
            Image.MAX_IMAGE_PIXELS = None
            pil_image = Image.open(image_path)
            
            # Force resize to a reasonable size
            max_dimension = 8000  # Maximum dimension
            width, height = pil_image.size
            
            if width > max_dimension or height > max_dimension:
                if width > height:
                    new_width = max_dimension
                    new_height = int(height * max_dimension / width)
                else:
                    new_height = max_dimension
                    new_width = int(width * max_dimension / height)
                
                logger.info(f"Aggressive resizing from {width}x{height} to {new_width}x{new_height}")
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array
            image = np.array(pil_image)
            
            # Convert RGB to BGR for OpenCV
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            logger.info(f"Successfully loaded image with aggressive resizing: {image.shape}")
            return image
            
        except Exception as e2:
            logger.error(f"Aggressive resizing also failed: {e2}")
            raise ValueError(f"Could not load image with any method: {e}")
    finally:
        # Restore PIL's default limit
        Image.MAX_IMAGE_PIXELS = 178956970

class ImageProcessor:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.tile_size = 512
        self.overlap = 100  # Overlap between tiles to avoid cutting trees
        
    def load_image(self, image_path: str) -> np.ndarray:
        """Load image using safe loading method"""
        logger.info(f"Loading image: {image_path}")
        
        image = safe_load_image_from_path(image_path)
            
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
            
        logger.info(f"Image loaded successfully. Shape: {image.shape}")
        return image
    
    def create_tiles(self, image: np.ndarray) -> List[Tuple[np.ndarray, Tuple[int, int]]]:
        """Create 1024x1024 tiles with overlap from the image"""
        height, width = image.shape[:2]
        tiles = []
        
        logger.info(f"Creating tiles from image of size {width}x{height}")
        
        # Calculate step size with overlap
        step = self.tile_size - self.overlap
        
        for y in range(0, height, step):
            for x in range(0, width, step):
                # Calculate tile boundaries
                y1 = y
                y2 = min(y + self.tile_size, height)
                x1 = x
                x2 = min(x + self.tile_size, width)
                
                # Extract tile
                tile = image[y1:y2, x1:x2]
                
                # Skip tiles that are too small
                if tile.shape[0] < 100 or tile.shape[1] < 100:
                    continue
                    
                # Pad tile to 1024x1024 if necessary
                if tile.shape[0] < self.tile_size or tile.shape[1] < self.tile_size:
                    padded_tile = np.zeros((self.tile_size, self.tile_size, 3), dtype=np.uint8)
                    padded_tile[:tile.shape[0], :tile.shape[1]] = tile
                    tile = padded_tile
                
                tiles.append((tile, (x, y)))
                
        logger.info(f"Created {len(tiles)} tiles")
        return tiles
    
    def tile_to_base64(self, tile: np.ndarray) -> str:
        """Convert tile to base64 string for API transmission"""
        # Encode as JPEG
        _, buffer = cv2.imencode('.jpg', tile)
        # Convert to base64
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{img_base64}"
    
    def process_tile(self, tile: np.ndarray, tile_position: Tuple[int, int]) -> Dict:
        """Process a single tile through the API"""
        try:
            # Convert tile to base64
            tile_base64 = self.tile_to_base64(tile)
            
            # Prepare request data
            data = {
                "image_data": tile_base64,
                "tile_position": tile_position
            }
            
            # Make API request
            response = requests.post(
                f"{self.api_url}/api/detect-trees-tile",
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return {"error": f"API error: {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return {"error": f"Request error: {str(e)}"}
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return {"error": f"Processing error: {str(e)}"}
    
    def merge_results(self, results: List[Dict], tile_positions: List[Tuple[int, int]]) -> Dict:
        """Merge results from multiple tiles"""
        total_tree_count = 0
        total_processing_time = 0
        all_detections = []
        
        for result, (tile_x, tile_y) in zip(results, tile_positions):
            if "error" not in result:
                total_tree_count += result.get("treeCount", 0)
                total_processing_time += result.get("processingTime", 0)
                
                # Adjust detection coordinates to original image
                for detection in result.get("detections", []):
                    bbox = detection["bbox"]
                    adjusted_detection = {
                        "confidence": detection["confidence"],
                        "bbox": {
                            "x": bbox["x"] + tile_x,
                            "y": bbox["y"] + tile_y,
                            "width": bbox["width"],
                            "height": bbox["height"]
                        }
                    }
                    all_detections.append(adjusted_detection)
        
        return {
            "totalTreeCount": total_tree_count,
            "totalTime": round(total_processing_time, 2),
            "averageProcessingTime": round(total_processing_time / len(results), 2) if results else 0,
            "tilesProcessed": len(results),
            "allDetections": all_detections
        }
    
    def process_large_image(self, image_path: str) -> Dict:
        """Process a large image by tiling it and processing each tile"""
        try:
            # Load the image
            image = self.load_image(image_path)
            
            # Create tiles
            tiles = self.create_tiles(image)
            
            if not tiles:
                return {"error": "No valid tiles created from image"}
            
            logger.info(f"Processing {len(tiles)} tiles...")
            
            # Process each tile
            results = []
            for i, (tile, position) in enumerate(tiles):
                logger.info(f"Processing tile {i+1}/{len(tiles)} at position {position}")
                
                result = self.process_tile(tile, position)
                results.append(result)
                
                # Add small delay to avoid overwhelming the API
                time.sleep(0.1)
            
            # Merge results
            merged_result = self.merge_results(results, [pos for _, pos in tiles])
            
            logger.info(f"Processing complete. Total trees: {merged_result['totalTreeCount']}")
            return merged_result
            
        except Exception as e:
            logger.error(f"Error processing large image: {e}")
            return {"error": f"Processing error: {str(e)}"}

def main():
    """Main function for testing"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python image_processor.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    processor = ImageProcessor()
    result = processor.process_large_image(image_path)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    
    print(f"Results: {result}")

if __name__ == "__main__":
    main() 