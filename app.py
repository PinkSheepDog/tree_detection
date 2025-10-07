from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import torch
import cv2
import numpy as np
import base64
import time
import io
from PIL import Image, ImageDraw, ImageFont
import os
from typing import List, Dict, Any

# Import YOLOv7 utilities (you'll need to have YOLOv7 code in your project)
try:
    from models.experimental import attempt_load
    from utils.general import non_max_suppression, scale_coords
    from utils.plots import plot_one_box
    YOLO_AVAILABLE = True
except ImportError:
    print("Warning: YOLOv7 modules not found. Please ensure YOLOv7 code is in your project.")
    YOLO_AVAILABLE = False

app = FastAPI(
    title="Tree Detection API",
    description="YOLOv7-based tree detection API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model
device = None
model = None
model_loaded = False

def load_model():
    """Load YOLOv7 model"""
    global device, model, model_loaded
    
    if not YOLO_AVAILABLE:
        raise Exception("YOLOv7 modules not available")
    
    try:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {device}")
        
        # Load your trained model - update path as needed
        model_path = 'best.pt'  # Update this to your model path
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        model = attempt_load(model_path, map_location=device)
        model.eval()
        model_loaded = True
        print("YOLOv7 model loaded successfully!")
        
    except Exception as e:
        print(f"Error loading model: {e}")
        model_loaded = False
        raise

def safe_load_image(image_bytes: bytes) -> np.ndarray:
    """
    Safely load image using PIL to handle large images that OpenCV can't process
    """
    try:
        # First try OpenCV for smaller images
        npimg = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        
        if img is not None:
            return img
    except Exception as e:
        print(f"OpenCV failed to load image: {e}")
    
    # If OpenCV fails, use PIL for large images
    try:
        # Temporarily disable PIL's decompression bomb protection
        Image.MAX_IMAGE_PIXELS = None
        
        # Load with PIL
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # Check if image is extremely large and needs resizing
        width, height = pil_image.size
        total_pixels = width * height
        max_pixels = 50000000  # 50 million pixels limit (more conservative)
        
        if total_pixels > max_pixels:
            print(f"Image too large ({total_pixels} pixels), resizing...")
            # Calculate new size while preserving aspect ratio
            aspect_ratio = width / height
            if width > height:
                new_width = int(np.sqrt(max_pixels * aspect_ratio))
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = int(np.sqrt(max_pixels / aspect_ratio))
                new_width = int(new_height * aspect_ratio)
            
            print(f"Resizing from {width}x{height} to {new_width}x{new_height}")
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to RGB if needed
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert to numpy array
        img_array = np.array(pil_image)
        
        # Convert RGB to BGR for OpenCV compatibility
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        print(f"Successfully loaded image with PIL: {img_bgr.shape}")
        return img_bgr
        
    except Exception as e:
        print(f"PIL failed to load image: {e}")
        # Try with even more aggressive resizing
        try:
            print("Attempting aggressive resizing...")
            Image.MAX_IMAGE_PIXELS = None
            pil_image = Image.open(io.BytesIO(image_bytes))
            
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
                
                print(f"Aggressive resizing from {width}x{height} to {new_width}x{new_height}")
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array
            img_array = np.array(pil_image)
            
            # Convert RGB to BGR for OpenCV compatibility
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            print(f"Successfully loaded image with aggressive resizing: {img_bgr.shape}")
            return img_bgr
            
        except Exception as e2:
            print(f"Aggressive resizing also failed: {e2}")
            raise ValueError(f"Could not load image with any method: {e}")
    finally:
        # Restore PIL's default limit
        Image.MAX_IMAGE_PIXELS = 178956970

def preprocess_image(img0):
    """Preprocess image for YOLOv7 inference"""
    # Resize image to YOLOv7 input size
    img = cv2.resize(img0, (640, 640))
    
    # Convert BGR to RGB and transpose
    img = img[:, :, ::-1].transpose(2, 0, 1)
    
    # Convert to tensor and normalize
    img = torch.from_numpy(np.ascontiguousarray(img)).to(device).float() / 255.0
    img = img.unsqueeze(0)
    
    return img

def draw_detections(img0, detections):
    """Draw bounding boxes on image"""
    img_draw = img0.copy()
    
    for *xyxy, conf, cls in detections:
        # Convert coordinates to integers
        x1, y1, x2, y2 = map(int, xyxy)
        
        # Draw bounding box
        cv2.rectangle(img_draw, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Add confidence label
        label = f'Tree: {conf:.2f}'
        cv2.putText(img_draw, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return img_draw

def image_to_base64(img):
    """Convert OpenCV image to base64 string"""
    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Encode to JPEG
    _, buffer = cv2.imencode('.jpg', img_rgb)
    
    # Convert to base64
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return f"data:image/jpeg;base64,{img_base64}"

def create_tiles(image, tile_size=1024, overlap=100):
    """Create tiles from large image"""
    height, width = image.shape[:2]
    tiles = []
    
    # Calculate step size with overlap
    step = tile_size - overlap
    
    for y in range(0, height, step):
        for x in range(0, width, step):
            # Calculate tile boundaries
            y1 = y
            y2 = min(y + tile_size, height)
            x1 = x
            x2 = min(x + tile_size, width)
            
            # Extract tile
            tile = image[y1:y2, x1:x2]
            
            # Skip tiles that are too small
            if tile.shape[0] < 100 or tile.shape[1] < 100:
                continue
                
            # Pad tile to tile_size if necessary
            if tile.shape[0] < tile_size or tile.shape[1] < tile_size:
                padded_tile = np.zeros((tile_size, tile_size, 3), dtype=np.uint8)
                padded_tile[:tile.shape[0], :tile.shape[1]] = tile
                tile = padded_tile
            
            tiles.append({
                'tile': tile,
                'position': (x, y),
                'original_size': (y2 - y1, x2 - x1)
            })
    
    return tiles

def merge_detections(all_detections, tile_positions, original_shape):
    """Merge detections from multiple tiles"""
    merged_detections = []
    
    for tile_detections, (tile_x, tile_y) in zip(all_detections, tile_positions):
        if tile_detections is not None and len(tile_detections):
            for *xyxy, conf, cls in tile_detections:
                # Adjust coordinates to original image
                x1, y1, x2, y2 = xyxy
                x1 += tile_x
                y1 += tile_y
                x2 += tile_x
                y2 += tile_y
                
                # Check if detection is within original image bounds
                if (0 <= x1 < original_shape[1] and 0 <= y1 < original_shape[0] and
                    0 <= x2 < original_shape[1] and 0 <= y2 < original_shape[0]):
                    merged_detections.append([x1, y1, x2, y2, conf, cls])
    
    return merged_detections

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    try:
        load_model()
    except Exception as e:
        print(f"Failed to load model on startup: {e}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Tree Detection API is running",
        "model_loaded": model_loaded,
        "device": str(device) if device else None
    }

@app.post("/api/detect-trees")
async def detect_trees(file: UploadFile = File(...)):
    """
    Detect trees in uploaded image using YOLOv7
    """
    if not model_loaded:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        start_time = time.time()
        
        # Read image file
        contents = await file.read()
        
        # Safely load image using PIL if OpenCV fails
        img0 = safe_load_image(contents)
        
        if img0 is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        print(f"Loaded image: {img0.shape}")
        
        # Check if image is too large and needs tiling
        height, width = img0.shape[:2]
        max_size = 2048  # Maximum size for single processing
        
        if height > max_size or width > max_size:
            # Use tiling for large images
            print(f"Large image detected ({width}x{height}), using tiling...")
            return await process_large_image(img0)
        else:
            # Process normally for smaller images
            return await process_single_image(img0)
        
    except Exception as e:
        print(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

async def process_single_image(img0):
    """Process a single image without tiling"""
    start_time = time.time()
    
    # Preprocess image
    img = preprocess_image(img0)
    
    # Run inference
    with torch.no_grad():
        pred = model(img, augment=False)[0]
        pred = non_max_suppression(pred, 0.2, 0.45)[0]
    
    # Rescale boxes to original image size
    if pred is not None and len(pred):
        pred[:, :4] = scale_coords(img.shape[2:], pred[:, :4], img0.shape).round()
    
    # Calculate results
    tree_count = 0 if pred is None else len(pred)
    processing_time = round(time.time() - start_time, 2)
    
    # Calculate average confidence
    avg_confidence = 0.0
    detections = []
    
    if pred is not None and len(pred):
        confidences = pred[:, 4].cpu().numpy()
        avg_confidence = round(float(np.mean(confidences)) * 100, 1)
        
        # Create detections list
        for i, (*xyxy, conf, cls) in enumerate(pred):
            x1, y1, x2, y2 = map(int, xyxy)
            detections.append({
                "confidence": round(float(conf) * 100, 2),
                "bbox": {
                    "x": x1,
                    "y": y1,
                    "width": x2 - x1,
                    "height": y2 - y1
                }
            })
    
    # Draw detections on image
    labeled_image = draw_detections(img0, pred) if pred is not None else img0
    labeled_image_url = image_to_base64(labeled_image)
    
    return {
        "treeCount": tree_count,
        "confidence": avg_confidence,
        "processingTime": processing_time,
        "labeledImageUrl": labeled_image_url,
        "detections": detections,
        "processingMethod": "single"
    }

async def process_large_image(img0):
    """Process large image using tiling"""
    start_time = time.time()
    
    # Create tiles
    tiles = create_tiles(img0, tile_size=1024, overlap=100)
    print(f"Created {len(tiles)} tiles for processing")
    
    all_detections = []
    tile_positions = []
    
    # Process each tile
    for i, tile_info in enumerate(tiles):
        tile = tile_info['tile']
        position = tile_info['position']
        
        print(f"Processing tile {i+1}/{len(tiles)} at position {position}")
        
        # Preprocess tile
        img = preprocess_image(tile)
        
        # Run inference on tile
        with torch.no_grad():
            pred = model(img, augment=False)[0]
            pred = non_max_suppression(pred, 0.2, 0.45)[0]
        
        # Rescale boxes to tile size
        if pred is not None and len(pred):
            pred[:, :4] = scale_coords(img.shape[2:], pred[:, :4], tile.shape).round()
        
        all_detections.append(pred)
        tile_positions.append(position)
    
    # Merge detections from all tiles
    merged_detections = merge_detections(all_detections, tile_positions, img0.shape)
    
    # Convert to tensor for final processing
    if merged_detections:
        final_pred = torch.tensor(merged_detections, device=device)
    else:
        final_pred = None
    
    # Calculate results
    tree_count = 0 if final_pred is None else len(final_pred)
    processing_time = round(time.time() - start_time, 2)
    
    # Calculate average confidence
    avg_confidence = 0.0
    detections = []
    
    if final_pred is not None and len(final_pred):
        confidences = final_pred[:, 4].cpu().numpy()
        avg_confidence = round(float(np.mean(confidences)) * 100, 1)
        
        # Create detections list
        for i, (*xyxy, conf, cls) in enumerate(final_pred):
            x1, y1, x2, y2 = map(int, xyxy)
            detections.append({
                "confidence": round(float(conf) * 100, 2),
                "bbox": {
                    "x": x1,
                    "y": y1,
                    "width": x2 - x1,
                    "height": y2 - y1
                }
            })
    
    # Draw detections on original image
    labeled_image = draw_detections(img0, final_pred) if final_pred is not None else img0
    labeled_image_url = image_to_base64(labeled_image)
    
    return {
        "treeCount": tree_count,
        "confidence": avg_confidence,
        "processingTime": processing_time,
        "labeledImageUrl": labeled_image_url,
        "detections": detections,
        "processingMethod": "tiled",
        "tilesProcessed": len(tiles)
    }

@app.post("/api/detect-trees-tile")
async def detect_trees_tile(request: dict):
    """
    Detect trees in a single tile (1024x1024) using YOLOv7
    """
    if not model_loaded:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        start_time = time.time()
        
        # Extract image data from request
        image_data = request.get("image_data", "")
        tile_position = request.get("tile_position", (0, 0))
        
        if not image_data:
            raise HTTPException(status_code=400, detail="No image data provided")
        
        # Remove data URL prefix if present
        if image_data.startswith("data:image/jpeg;base64,"):
            image_data = image_data.split(",")[1]
        
        # Decode base64 image
        img_bytes = base64.b64decode(image_data)
        img0 = safe_load_image(img_bytes)
        
        if img0 is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        # Preprocess image
        img = preprocess_image(img0)
        
        # Run inference
        with torch.no_grad():
            pred = model(img, augment=False)[0]
            pred = non_max_suppression(pred, 0.25, 0.45)[0]
        
        # Rescale boxes to original image size
        if pred is not None and len(pred):
            pred[:, :4] = scale_coords(img.shape[2:], pred[:, :4], img0.shape).round()
        
        # Calculate results
        tree_count = 0 if pred is None else len(pred)
        processing_time = round(time.time() - start_time, 2)
        
        # Calculate average confidence
        avg_confidence = 0.0
        detections = []
        
        if pred is not None and len(pred):
            confidences = pred[:, 4].cpu().numpy()
            avg_confidence = round(float(np.mean(confidences)) * 100, 1)
            
            # Create detections list
            for i, (*xyxy, conf, cls) in enumerate(pred):
                x1, y1, x2, y2 = map(int, xyxy)
                detections.append({
                    "confidence": round(float(conf) * 100, 2),
                    "bbox": {
                        "x": x1,
                        "y": y1,
                        "width": x2 - x1,
                        "height": y2 - y1
                    }
                })
        
        # Return results
        return {
            "treeCount": tree_count,
            "confidence": avg_confidence,
            "processingTime": processing_time,
            "tilePosition": tile_position,
            "detections": detections
        }
        
    except Exception as e:
        print(f"Error processing tile: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing tile: {str(e)}")

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": model_loaded,
        "device": str(device) if device else None,
        "yolo_available": YOLO_AVAILABLE
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 