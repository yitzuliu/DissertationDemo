# 🎯 YOLO8 Object Detection Model

## 📋 **Overview**

This directory contains YOLO8 object detection implementation for real-time object recognition in the AI Manual Assistant.

## 📁 **Files Structure**

- **`verification.py`** - YOLO8 model verification and testing
- **`run_yolo.py`** - Main YOLO8 inference script
- **`original_flask_app.py`** - Original Flask application for YOLO8
- **`requirements.txt`** - YOLO8 specific dependencies
- **`original_templates/`** - Original HTML templates

## 🚀 **Quick Start**

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Download YOLO model** (not included due to file size):
   ```bash
   # Download YOLOv8 models manually from:
   # https://github.com/ultralytics/ultralytics
   wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
   wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt
   ```

3. **Run verification**:
   ```bash
   python verification.py
   ```

4. **Start YOLO inference**:
   ```bash
   python run_yolo.py
   ```

## 📊 **Model Files (Not Included)**

The following model files are excluded due to GitHub size limits:
- `yolov8n.pt` (6.5MB) - Nano model, fastest inference
- `yolov8s.pt` (22MB) - Small model, balanced speed/accuracy
- `yolov8m.pt` - Medium model
- `yolov8l.pt` - Large model
- `yolov8x.pt` - Extra large model, highest accuracy

## 🔧 **Integration with AI Manual Assistant**

YOLO8 provides object detection capabilities that feed into the contextual understanding engine:

```
Camera → YOLO8 Detection → Context Engine → AI Assistant → User Guidance
```

## 🛠️ **Development Notes**

- Optimized for real-time inference
- Supports various input formats (image, video, webcam)
- Configurable confidence thresholds
- Multi-class object detection (80+ COCO classes) 