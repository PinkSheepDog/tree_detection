"""
Full-stack Tree Detection App for Hugging Face Spaces
Combines React frontend with FastAPI backend using Gradio's custom components
"""

import gradio as gr
import torch
import cv2
import numpy as np
import time
from PIL import Image
import os
import base64
from io import BytesIO

# Import YOLOv7 utilities
try:
    from models.experimental import attempt_load
    from utils.general import non_max_suppression, scale_coords
    YOLO_AVAILABLE = True
except ImportError as e:
    print(f"Warning: YOLOv7 modules not found: {e}")
    YOLO_AVAILABLE = False

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
        
        model_path = 'best.pt'
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

def safe_load_image(image_data):
    """Safely load image"""
    if isinstance(image_data, np.ndarray):
        return image_data
    elif isinstance(image_data, Image.Image):
        return np.array(image_data)
    else:
        return None

def preprocess_image(img0):
    """Preprocess image for YOLOv7 inference"""
    img = cv2.resize(img0, (640, 640))
    img = img[:, :, ::-1].transpose(2, 0, 1)
    img = torch.from_numpy(np.ascontiguousarray(img)).to(device).float() / 255.0
    img = img.unsqueeze(0)
    return img

def draw_detections(img0, detections):
    """Draw bounding boxes on image"""
    img_draw = img0.copy()
    
    if detections is None or len(detections) == 0:
        return img_draw
    
    for *xyxy, conf, cls in detections:
        x1, y1, x2, y2 = map(int, xyxy)
        cv2.rectangle(img_draw, (x1, y1), (x2, y2), (0, 255, 0), 3)
        label = f'Tree: {conf:.2f}'
        
        # Draw label background
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(img_draw, (x1, y1 - 20), (x1 + w, y1), (0, 255, 0), -1)
        cv2.putText(img_draw, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    return img_draw

def create_tiles(image, tile_size=1024, overlap=100):
    """Create tiles from large image"""
    height, width = image.shape[:2]
    tiles = []
    step = tile_size - overlap
    
    for y in range(0, height, step):
        for x in range(0, width, step):
            y1, y2 = y, min(y + tile_size, height)
            x1, x2 = x, min(x + tile_size, width)
            
            tile = image[y1:y2, x1:x2]
            
            if tile.shape[0] < 100 or tile.shape[1] < 100:
                continue
                
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
                x1, y1, x2, y2 = xyxy
                x1 += tile_x
                y1 += tile_y
                x2 += tile_x
                y2 += tile_y
                
                if (0 <= x1 < original_shape[1] and 0 <= y1 < original_shape[0] and
                    0 <= x2 < original_shape[1] and 0 <= y2 < original_shape[0]):
                    merged_detections.append([x1, y1, x2, y2, conf, cls])
    
    return merged_detections

def detect_trees(image, use_tiling=False):
    """
    Main detection function
    """
    if not model_loaded:
        return None, "❌ Model not loaded", {}, ""
    
    if image is None:
        return None, "❌ Please upload an image first", {}, ""
    
    try:
        start_time = time.time()
        
        # Convert to numpy array
        img0 = safe_load_image(image)
        if img0 is None:
            return None, "❌ Invalid image format", {}, ""
        
        # Convert RGB to BGR for OpenCV
        if len(img0.shape) == 3 and img0.shape[2] == 3:
            img0_bgr = cv2.cvtColor(img0, cv2.COLOR_RGB2BGR)
        else:
            img0_bgr = img0
        
        height, width = img0_bgr.shape[:2]
        processing_method = "single"
        tiles_processed = 0
        
        # Check if should use tiling
        max_size = 2048
        if use_tiling or height > max_size or width > max_size:
            # Use tiling for large images
            processing_method = "tiled"
            tiles = create_tiles(img0_bgr, tile_size=1024, overlap=100)
            tiles_processed = len(tiles)
            
            all_detections = []
            tile_positions = []
            
            for tile_info in tiles:
                tile = tile_info['tile']
                position = tile_info['position']
                
                img = preprocess_image(tile)
                
                with torch.no_grad():
                    pred = model(img, augment=False)[0]
                    pred = non_max_suppression(pred, 0.2, 0.45)[0]
                
                if pred is not None and len(pred):
                    pred[:, :4] = scale_coords(img.shape[2:], pred[:, :4], tile.shape).round()
                
                all_detections.append(pred)
                tile_positions.append(position)
            
            # Merge detections
            merged_detections = merge_detections(all_detections, tile_positions, img0_bgr.shape)
            
            if merged_detections:
                pred = torch.tensor(merged_detections, device=device)
            else:
                pred = None
        else:
            # Process normally
            img = preprocess_image(img0_bgr)
            
            with torch.no_grad():
                pred = model(img, augment=False)[0]
                pred = non_max_suppression(pred, 0.2, 0.45)[0]
            
            if pred is not None and len(pred):
                pred[:, :4] = scale_coords(img.shape[2:], pred[:, :4], img0_bgr.shape).round()
        
        # Calculate results
        tree_count = 0 if pred is None else len(pred)
        processing_time = round(time.time() - start_time, 2)
        
        # Calculate average confidence
        avg_confidence = 0.0
        confidence_distribution = []
        
        if pred is not None and len(pred):
            confidences = pred[:, 4].cpu().numpy()
            avg_confidence = round(float(np.mean(confidences)) * 100, 1)
            confidence_distribution = [round(float(c) * 100, 1) for c in confidences]
        
        # Draw detections
        result_img = draw_detections(img0_bgr, pred)
        result_img_rgb = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
        
        # Create statistics dictionary
        stats = {
            "Trees Detected": tree_count,
            "Average Confidence": f"{avg_confidence}%",
            "Processing Time": f"{processing_time}s",
            "Image Size": f"{width}x{height}",
            "Processing Method": processing_method.title(),
            "Device": str(device).upper()
        }
        
        if processing_method == "tiled":
            stats["Tiles Processed"] = tiles_processed
        
        # Create detailed info
        details = f"""
### 📊 Detection Statistics

**Total Trees Found:** {tree_count}

**Confidence Range:** 
- Average: {avg_confidence}%
- Min: {min(confidence_distribution) if confidence_distribution else 0}%
- Max: {max(confidence_distribution) if confidence_distribution else 0}%

**Image Information:**
- Resolution: {width} × {height} pixels
- Processing Method: {processing_method.title()}
- Processing Time: {processing_time}s
- Device: {device}

{'**Tiles Processed:** ' + str(tiles_processed) if processing_method == "tiled" else ''}
"""
        
        status = f"✅ Successfully detected {tree_count} tree{'s' if tree_count != 1 else ''}"
        
        return result_img_rgb, status, stats, details
        
    except Exception as e:
        print(f"Error processing image: {e}")
        import traceback
        traceback.print_exc()
        return None, f"❌ Error: {str(e)}", {}, ""

# Load model on startup
print("🌳 Loading YOLOv7 Tree Detection Model...")
try:
    load_model()
    startup_status = "✅ Model loaded successfully!"
    model_info = f"Device: {device} | Model: YOLOv7"
except Exception as e:
    startup_status = f"❌ Failed to load model: {str(e)}"
    model_info = "Model loading failed"

print(startup_status)

# Create Gradio interface with custom theme
theme = gr.themes.Soft(
    primary_hue="green",
    secondary_hue="emerald",
).set(
    body_background_fill="*neutral_50",
    button_primary_background_fill="*primary_500",
)

with gr.Blocks(title="🌳 Tree Detection with YOLOv7", theme=theme, css="""
    .gradio-container {max-width: 1200px !important}
    h1 {text-align: center; color: #2d5016;}
    .status-box {padding: 10px; border-radius: 5px; margin: 10px 0;}
""") as demo:
    
    gr.Markdown(
        """
        # 🌳 Tree Detection with YOLOv7
        
        ### Advanced AI-powered tree detection in aerial and satellite imagery
        
        Upload an image to detect and count trees using a state-of-the-art YOLOv7 deep learning model.
        Perfect for forestry analysis, environmental monitoring, and land management.
        """
    )
    
    with gr.Row():
        with gr.Column():
            gr.Markdown(f"**🤖 Model Status:** {startup_status}")
            gr.Markdown(f"**📋 Info:** {model_info}")
        
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📤 Upload Image")
            input_image = gr.Image(
                type="pil",
                label="Drop your image here or click to upload",
                height=400
            )
            
            use_tiling = gr.Checkbox(
                label="🔲 Use Tiling (for very large images >2048px)",
                value=False,
                info="Enables tile-based processing for large images"
            )
            
            with gr.Row():
                detect_btn = gr.Button("🔍 Detect Trees", variant="primary", size="lg", scale=2)
                clear_btn = gr.Button("🗑️ Clear", size="lg", scale=1)
        
        with gr.Column(scale=1):
            gr.Markdown("### 📊 Detection Results")
            output_image = gr.Image(
                type="numpy",
                label="Detected Trees",
                height=400
            )
            
            status_text = gr.Markdown(value="Waiting for image...", elem_classes="status-box")
    
    with gr.Row():
        stats_json = gr.JSON(label="📈 Quick Stats", scale=1)
        details_md = gr.Markdown(value="", scale=1)
    
    with gr.Accordion("ℹ️ How to Use & Information", open=False):
        gr.Markdown(
            """
            ### 📖 How to Use:
            
            1. **Upload an Image:** Click or drag-and-drop an aerial/satellite image
            2. **Optional:** Enable tiling for very large images (>2048 pixels)
            3. **Click "Detect Trees":** Wait for processing (usually 2-10 seconds)
            4. **View Results:** See detected trees with bounding boxes and statistics
            
            ### 🎯 Best Practices:
            
            - **Image Quality:** Higher resolution images provide better detection
            - **Image Type:** Works best with aerial/satellite imagery showing tree canopies
            - **Large Images:** Enable tiling for images larger than 2048x2048 pixels
            - **File Formats:** Supports JPG, PNG, TIFF
            
            ### 🔬 About the Model:
            
            This application uses **YOLOv7** (You Only Look Once v7), a state-of-the-art 
            real-time object detection system. The model has been specifically fine-tuned 
            for tree detection in aerial imagery.
            
            **Features:**
            - Fast inference (2-10 seconds per image)
            - High accuracy with confidence scores
            - Handles images of various sizes
            - Tile-based processing for large images
            
            ### 🛠️ Technology Stack:
            
            - **Model:** YOLOv7 (Custom trained)
            - **Framework:** PyTorch
            - **Interface:** Gradio
            - **Image Processing:** OpenCV
            - **Platform:** Hugging Face Spaces
            
            ### 📊 Use Cases:
            
            - 🌲 Forest inventory and management
            - 🌍 Environmental monitoring
            - 🏞️ Land use assessment
            - 📈 Deforestation tracking
            - 🌳 Urban tree mapping
            """
        )
    
    # Event handlers
    detect_btn.click(
        fn=detect_trees,
        inputs=[input_image, use_tiling],
        outputs=[output_image, status_text, stats_json, details_md]
    )
    
    clear_btn.click(
        fn=lambda: (None, "Waiting for image...", {}, ""),
        inputs=[],
        outputs=[output_image, status_text, stats_json, details_md]
    )

# Launch
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

