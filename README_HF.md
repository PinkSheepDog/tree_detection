---
title: Tree Detection YOLOv7
emoji: 🌳
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 4.44.0
app_file: app_hf.py
pinned: false
license: mit
---

# 🌳 Tree Detection with YOLOv7

Detect and count trees in aerial/satellite imagery using YOLOv7 deep learning model.

## Features

- 🎯 Accurate tree detection in aerial images
- 📊 Bounding box visualization
- 💯 Confidence scores
- ⚡ Fast inference

## How to Use

1. Upload an image (aerial/satellite imagery preferred)
2. Click "Detect Trees"
3. View results with bounding boxes and statistics

## Model

This application uses YOLOv7, a state-of-the-art object detection model, fine-tuned for tree detection.

## Technology Stack

- YOLOv7 for object detection
- Gradio for the web interface
- PyTorch for deep learning
- OpenCV for image processing

## Local Development

```bash
pip install -r requirements_hf.txt
python app_hf.py
```

Visit http://localhost:7860 to use the app locally.

