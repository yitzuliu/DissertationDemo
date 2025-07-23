# 🎯 Complete Model Configuration Guide

## ✅ **Correct Model Names for `app_config.json`**

When you want to change the model, use these **exact names** in `src/config/app_config.json`:

### **Available Models:**

| Model Name in `app_config.json` | Run Script | Description |
|----------------------------------|------------|-------------|
| `"moondream2"` | `src/models/moondream2/run_moondream2.py` | Standard Moondream2 |
| `"moondream2_optimized"` | `src/models/moondream2/run_moondream2_optimized.py` | Optimized Moondream2 |
| `"phi3_vision"` | `src/models/phi3_vision_mlx/run_phi3_vision.py` | Standard Phi-3.5-Vision |
| `"phi3_vision_optimized"` | `src/models/phi3_vision_mlx/run_phi3_vision_optimized.py` | Optimized Phi-3.5-Vision |
| `"llava_mlx"` | `src/models/llava_mlx/run_llava_mlx.py` | LLaVA with MLX |
| `"smolvlm"` | `src/models/smolvlm/run_smolvlm.py` | Standard SmolVLM |
| `"smolvlm2_500m_video"` | `src/models/smolvlm2/run_smolvlm2_500m_video.py` | SmolVLM2 Video |
| `"smolvlm2_500m_video_optimized"` | `src/models/smolvlm2/run_smolvlm2_500m_video_optimized.py` | SmolVLM2 Video Optimized |

## 🔄 **How to Switch Models**

### **Step 1: Update Configuration**
Edit `src/config/app_config.json`:
```json
{
  "active_model": "phi3_vision_optimized"
}
```

### **Step 2: Start the Correct Model Server**
```bash
# For phi3_vision_optimized
cd src/models/phi3_vision_mlx
python run_phi3_vision_optimized.py

# For moondream2_optimized  
cd src/models/moondream2
python run_moondream2_optimized.py

# For smolvlm2_500m_video_optimized
cd src/models/smolvlm2
python run_smolvlm2_500m_video_optimized.py
```

### **Step 3: Start Backend**
```bash
cd src/backend
python main.py
```

### **Step 4: Start Frontend**
```bash
cd src/frontend
python -m http.server 5500
```

## 🛠️ **Quick Start with Helper Script**

Instead of manual steps, use:
```bash
python start_model.py
```

This automatically starts the correct model based on your `app_config.json`.

## 🔍 **Troubleshooting Steps**

### **1. Check All Components**
```bash
python debug_connection.py
```

Expected output:
```
✅ Model Server is running and responding
✅ Backend API is running and responding  
✅ Frontend is running and responding
✅ All components are running!
```

### **2. Test Chat Functionality**
```bash
python test_chat_completion.py
```

Expected output:
```
✅ Backend chat completion successful!
✅ Model server direct test successful!
✅ All tests passed!
```

### **3. Common Issues & Solutions**

#### **Issue: "Connection Error" in Frontend**
- **Cause**: Model server not running or crashed
- **Solution**: Restart the model server for your active model

#### **Issue: "ASK ABOUT THE IMAGE is empty"**
- **Cause**: Frontend not getting the correct configuration
- **Solution**: 
  1. Check `app_config.json` has correct model name
  2. Restart backend: `cd src/backend && python main.py`
  3. Clear browser cache and refresh

#### **Issue: "Internal Server Error" (500)**
- **Cause**: Model failed to load or crashed
- **Solution**: 
  1. Stop model server (Ctrl+C)
  2. Restart with: `python run_[model_name].py`
  3. Check terminal for error messages

#### **Issue: Model server won't start**
- **Cause**: Missing dependencies
- **Solution**: Install required packages:
  ```bash
  # For MLX models (phi3_vision, llava_mlx, smolvlm2)
  pip install mlx-vlm
  
  # For standard models (moondream2, smolvlm)
  pip install transformers torch
  ```

## 📋 **Current Status Check**

Your current configuration:
- **Active Model**: `phi3_vision` 
- **Expected Server**: `src/models/phi3_vision_mlx/run_phi3_vision.py`
- **Backend Port**: 8000
- **Frontend Port**: 5500
- **Model Server Port**: 8080

## 🎯 **Recommended Models**

### **For Apple Silicon (M1/M2/M3):**
- `"phi3_vision_optimized"` - Best quality + performance
- `"smolvlm2_500m_video_optimized"` - Fast + video support
- `"llava_mlx"` - Good balance

### **For Universal Compatibility:**
- `"moondream2_optimized"` - Fast + reliable
- `"smolvlm"` - Lightweight

### **For Video Tasks:**
- `"smolvlm2_500m_video_optimized"` - Best for video
- `"smolvlm2_500m_video"` - Standard video support

## 🚨 **Important Notes**

1. **Always restart the model server** after changing `app_config.json`
2. **Use exact model names** from the table above
3. **Check all three components** are running (model server, backend, frontend)
4. **Clear browser cache** if frontend shows old information
5. **Check terminal logs** for detailed error messages

## 🔧 **Fixed Issues**

- ✅ Fixed `.loaded` attribute errors in health checks
- ✅ Fixed chat completion endpoints  
- ✅ Updated model configuration mapping
- ✅ Created diagnostic and testing tools

Your system should now work correctly with any of the supported models!