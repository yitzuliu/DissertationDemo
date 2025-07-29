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

YOLO8 provides object detection capabilities that feed into the dual-loop memory system:

```
Camera → YOLO8 Detection → State Tracker → RAG Knowledge Base → User Guidance
```

### **Current System Status**
- **Primary VLMs**: Moondream2, SmolVLM2, SmolVLM, Phi-3.5-Vision
- **YOLO8 Role**: Specialized object detection for enhanced context understanding
- **Integration**: Feeds into dual-loop memory system for comprehensive scene analysis

### **Performance Context (2025-07-29)**
While VLMs provide comprehensive scene understanding, YOLO8 offers:
- **Real-time object detection** (>30 FPS)
- **80+ COCO object classes** recognition
- **Bounding box precision** for spatial understanding
- **Complement to VLM analysis** for enhanced accuracy

## 🛠️ **Development Notes**

- **Optimized for real-time inference** (>30 FPS)
- **Supports various input formats** (image, video, webcam)
- **Configurable confidence thresholds** (0.1-0.9)
- **Multi-class object detection** (80+ COCO classes)
- **Complements VLM analysis** for enhanced scene understanding
- **Integration ready** with dual-loop memory system

### **Latest VLM Performance Context (2025-07-29)**
Current VLM rankings for comparison:
1. **🥇 Moondream2**: 65.0% accuracy, 8.35s inference
2. **🥈 SmolVLM2-MLX**: 55.0% accuracy, 8.41s inference  
3. **⚡ SmolVLM-GGUF**: 35.0% accuracy, 0.39s inference
4. **🥉 Phi-3.5-MLX**: 35.0% accuracy, 5.29s inference
5. **🚫 LLaVA-MLX**: 20.0% accuracy, 24.15s inference (avoid)

YOLO8 provides complementary object detection capabilities to enhance overall system accuracy. 