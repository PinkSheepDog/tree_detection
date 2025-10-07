"""
Hugging Face Spaces compatible version of the Tree Detection API
This version uses Gradio for the interface which is perfect for HF Spaces
"""

import gradio as gr
import torch
import cv2
import numpy as np
import time
from PIL import Image
import os

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
    
    if detections is None or len(detections) == 0:
        return img_draw
    
    for *xyxy, conf, cls in detections:
        # Convert coordinates to integers
        x1, y1, x2, y2 = map(int, xyxy)
        
        # Draw bounding box
        cv2.rectangle(img_draw, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Add confidence label
        label = f'Tree: {conf:.2f}'
        cv2.putText(img_draw, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return img_draw

def detect_trees(image):
    """
    Main detection function for Gradio interface
    """
    if not model_loaded:
        return None, "❌ Model not loaded. Please refresh the page."
    
    if image is None:
        return None, "❌ Please upload an image first."
    
    try:
        start_time = time.time()
        
        # Convert PIL Image to numpy array (RGB)
        img0 = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        img0_bgr = cv2.cvtColor(img0, cv2.COLOR_RGB2BGR)
        
        print(f"Processing image: {img0_bgr.shape}")
        
        # Preprocess image
        img = preprocess_image(img0_bgr)
        
        # Run inference
        with torch.no_grad():
            pred = model(img, augment=False)[0]
            pred = non_max_suppression(pred, 0.2, 0.45)[0]
        
        # Rescale boxes to original image size
        if pred is not None and len(pred):
            pred[:, :4] = scale_coords(img.shape[2:], pred[:, :4], img0_bgr.shape).round()
        
        # Calculate results
        tree_count = 0 if pred is None else len(pred)
        processing_time = round(time.time() - start_time, 2)
        
        # Calculate average confidence
        avg_confidence = 0.0
        if pred is not None and len(pred):
            confidences = pred[:, 4].cpu().numpy()
            avg_confidence = round(float(np.mean(confidences)) * 100, 1)
        
        # Draw detections on image
        result_img = draw_detections(img0_bgr, pred)
        
        # Convert back to RGB for display
        result_img_rgb = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
        
        # Create result text
        result_text = f"""
## 🌳 Detection Results

- **Trees Detected**: {tree_count}
- **Average Confidence**: {avg_confidence}%
- **Processing Time**: {processing_time}s
- **Device**: {device}
"""
        
        return result_img_rgb, result_text
        
    except Exception as e:
        print(f"Error processing image: {e}")
        import traceback
        traceback.print_exc()
        return None, f"❌ Error processing image: {str(e)}"

# Load model on startup
print("Loading YOLOv7 model...")
try:
    load_model()
    startup_message = "✅ Model loaded successfully!"
except Exception as e:
    startup_message = f"❌ Failed to load model: {str(e)}"
print(startup_message)

# Create Gradio interface
with gr.Blocks(title="🌳 Tree Detection with YOLOv7", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🌳 Tree Detection with YOLOv7
        
        Upload an image to detect and count trees using a YOLOv7 deep learning model.
        
        **Features:**
        - Detects trees in aerial/satellite imagery
        - Shows bounding boxes around detected trees
        - Provides confidence scores and processing time
        """
    )
    
    gr.Markdown(f"**Model Status:** {startup_message}")
    
    with gr.Row():
        with gr.Column():
            input_image = gr.Image(
                type="pil",
                label="📤 Upload Image",
                height=400
            )
            detect_btn = gr.Button("🔍 Detect Trees", variant="primary", size="lg")
            
            gr.Examples(
                examples=[],  # Add example images if you have any
                inputs=input_image,
                label="📸 Example Images"
            )
        
        with gr.Column():
            output_image = gr.Image(
                type="numpy",
                label="📊 Detection Results",
                height=400
            )
            output_text = gr.Markdown(label="Results")
    
    gr.Markdown(
        """
        ---
        ### 📖 How to Use:
        1. Upload an image (JPG, PNG, TIFF)
        2. Click "Detect Trees"
        3. View the results with bounding boxes
        
        ### ℹ️ About:
        This app uses YOLOv7, a state-of-the-art object detection model, 
        fine-tuned for tree detection in aerial imagery.
        """
    )
    
    # Connect button to function
    detect_btn.click(
        fn=detect_trees,
        inputs=input_image,
        outputs=[output_image, output_text]
    )

# Launch the app
if __name__ == "__main__":
    demo.launch()

