# Configuration System - AI Vision Intelligence Hub

*Last Updated: August 8, 2025*

## 📋 Overview

The configuration system manages all settings for the AI Vision Intelligence Hub, including model configurations, application settings, prompt templates, VLM system settings, VLM fallback system settings, and **State Tracker configuration**. This system provides a centralized, flexible, and validated approach to managing the entire application's behavior including intelligent query processing, multi-model vision-language processing, and recent observation aware fallback.

## 🏗️ Architecture

```
src/config/
├── README.md                    # This documentation
├── app_config.json             # Main application configuration
├── models_config.json          # Model registry and metadata
├── validate_model_configs.py   # Configuration validation tool
├── state_tracker_config.json   # State Tracker and recent observation fallback settings
├── model_configs/              # Individual model configurations
│   ├── template.json           # Template for new models
│   ├── smolvlm.json           # Current active model
│   ├── moondream2.json        # Standard Moondream2
│   ├── moondream2_optimized.json # Optimized Moondream2
│   ├── llava_mlx.json         # MLX-optimized LLaVA
│   ├── phi3_vision.json       # Standard Phi-3 Vision
│   ├── phi3_vision_optimized.json # Optimized Phi-3 Vision
│   ├── smolvlm2_500m_video.json # Standard SmolVLM2 Video
│   ├── smolvlm2_500m_video_optimized.json # Optimized SmolVLM2 Video
│   └── yolo8.json             # YOLO8 Object Detection
├── prompts/                   # Prompt templates
│   └── manual_assistant_prompts.json # Assistant prompt variations
├── vlm_fallback_config.json  # VLM Fallback system configuration
└── vlm_system_config.json    # VLM System multi-model configuration
```

## 🚀 Core Components

### 1. Application Configuration (`app_config.json`)
**Main application settings:**
```json
{
  "server": {
    "host": "localhost",
    "port": 8000
  },
  "frontend": {
    "video_width": 640,
    "video_height": 480,
    "api_base_url": "http://localhost:8000"
  },
  "model_server": {
    "host": "localhost",
    "port": 8080
  },
  "active_model": "smolvlm"
}
```

### 2. Model Registry (`models_config.json`)
**Comprehensive model metadata and categorization:**
- **Model Information**: Display names, descriptions, capabilities
- **Framework Support**: Transformers, MLX, Ultralytics
- **Platform Requirements**: Apple Silicon, Universal
- **Memory Usage**: Estimated RAM requirements
- **Categories**: Lightweight, MLX-optimized, video-capable, etc.
- **Switching Guide**: How to change active models
- **Requirements**: Dependencies for each model
- **Recommendations**: Use case suggestions

### 3. Model Configurations (`model_configs/`)
**Individual model-specific settings:**
- **Model Parameters**: ID, path, device settings
- **Image Processing**: Size, quality, enhancement options
- **Generation Config**: Tokens, temperature, sampling
- **Server Settings**: Framework, ports, CORS
- **UI Configuration**: Instructions, capture intervals
- **Performance**: Optimization settings, memory management

### 4. Prompt Templates (`prompts/`)
**Specialized assistant prompts:**
- **Default Instruction**: General purpose
- **Cooking Assistant**: Kitchen and cooking tasks
- **Repair Assistant**: Troubleshooting and repairs
- **Assembly Assistant**: Building and assembly
- **Learning Assistant**: Educational guidance
- **Safety First**: Safety-focused instructions
- **Troubleshooting**: Problem diagnosis
- **Progress Check**: Task monitoring
- **Tool Identification**: Equipment recognition

### 5. VLM Fallback Configuration (`vlm_fallback_config.json`)
**Intelligent query processing settings:**
- **Decision Engine**: Confidence thresholds and fallback criteria
- **VLM Client**: Connection settings and timeout configuration
- **Prompt Management**: Template switching and optimization
- **Performance**: Response time limits and retry policies

### 6. VLM System Configuration (`vlm_system_config.json`)
**Multi-model vision-language processing settings:**
- **Model Selection**: Intelligent model routing and selection criteria
- **Performance Monitoring**: Model-specific performance tracking
- **Load Balancing**: Request distribution across multiple models
- **Fault Tolerance**: Model failure handling and recovery

### 7. State Tracker Configuration (`state_tracker_config.json`)
**State tracking and recent observation aware fallback settings:**
- **Recent Observation Fallback**: TTL thresholds and confidence settings
- **Fallback Triggers**: Conditions for triggering VLM fallback
- **Performance Tuning**: Memory and processing optimization
- **Feature Flags**: Enable/disable recent observation awareness

## 🔧 Configuration Features

### Unified Model Management
- **Single Source of Truth**: All model information centralized
- **Automatic Validation**: Built-in configuration checking
- **Easy Switching**: Simple model activation process
- **Framework Flexibility**: Support for multiple ML frameworks

### Advanced Image Processing
- **Model-Specific Optimization**: Tailored preprocessing for each model
- **Quality Enhancement**: Advanced algorithms (CLAHE, noise reduction)
- **Smart Cropping**: Intelligent aspect ratio preservation
- **Format Flexibility**: Support for multiple image formats

### Comprehensive Validation
- **Schema Validation**: Ensures configuration integrity
- **Path Verification**: Checks file and directory existence
- **Dependency Checking**: Validates framework requirements
- **Cross-Reference Validation**: Ensures consistency across files

## 📊 Model Categories

### By Performance
- **Lightweight**: `smolvlm`, `moondream2` (~1-3GB RAM)
- **Large Models**: `llava_mlx`, `phi3_vision_optimized` (~4-6GB RAM)

### By Platform
- **Apple Silicon**: MLX-optimized models for M1/M2/M3
- **Universal**: Transformers-based models for all platforms

### By Capability
- **Video Understanding**: `smolvlm2_500m_video*` models
- **Object Detection**: `yolo8` for detection tasks
- **General Vision**: All other models for image understanding

### By Framework
- **MLX-VLM**: Apple Silicon optimization
- **Transformers**: Universal HuggingFace support
- **Ultralytics**: YOLO object detection

## 🚀 Getting Started

### Viewing Current Configuration
```bash
# Check active model
cat app_config.json | grep active_model

# View model registry
cat models_config.json | jq '.models | keys'

# Validate all configurations
python validate_model_configs.py
```

### Switching Models
```bash
# 1. Edit app_config.json
# Change "active_model" value to desired model

# 2. Validate the change
python validate_model_configs.py

# 3. Restart the backend service
cd ../backend && python main.py
```

### Adding New Models
1. **Create Configuration**: Copy `template.json` and customize
2. **Add to Registry**: Update `models_config.json`
3. **Validate**: Run validation script
4. **Test**: Ensure model works correctly

## 📝 Configuration Schema

### Model Configuration Structure
```json
{
  "model_name": "Display Name",
  "model_id": "unique_identifier",
  "model_path": "huggingface/model/path",
  "device": "auto|mps|cpu|cuda",
  "capabilities": {
    "vision": true,
    "text_generation": true,
    "video_understanding": false
  },
  "image_processing": {
    "size": [width, height],
    "quality": 95,
    "smart_crop": true
  },
  "server": {
    "framework": "fastapi|flask",
    "port": 8080
  }
}
```

### Validation Rules
- **Required Fields**: `model_id`, `model_name`, `device`
- **Path Consistency**: Model paths must be valid
- **Framework Compatibility**: Check platform requirements
- **File Existence**: Verify run scripts exist

## 🔍 Troubleshooting

### Common Issues

1. **Configuration Validation Errors**
   ```bash
   # Run validation to identify issues
   python validate_model_configs.py
   
   # Check specific model config
   cat model_configs/smolvlm.json | jq '.model_id'
   ```

2. **Model Switching Problems**
   ```bash
   # Verify active model exists
   grep "active_model" app_config.json
   
   # Check model config exists
   ls model_configs/$(grep "active_model" app_config.json | cut -d'"' -f4).json
   ```

3. **Path Issues**
   ```bash
   # Validate all paths
   python validate_model_configs.py
   
   # Check specific paths
   find . -name "*.py" | grep -E "(run_|main\.py)"
   ```

### Validation Commands
```bash
# Full validation
python validate_model_configs.py

# Check specific model
python -c "
import json
with open('model_configs/smolvlm.json') as f:
    config = json.load(f)
    print(f'Model: {config[\"model_name\"]}')
    print(f'Path: {config[\"model_path\"]}')
"
```

## 📈 Performance Optimization

### Model Selection Guide
- **Apple Silicon**: Use MLX-optimized models
- **Low Memory**: Choose lightweight models
- **Video Tasks**: Select video-capable models
- **Best Quality**: Use larger models
- **Fastest Inference**: Choose optimized versions

### Configuration Optimization
- **Image Quality**: Balance between quality and speed
- **Memory Management**: Configure cleanup intervals
- **Caching**: Enable where appropriate
- **Batch Processing**: Use for multiple images

## 🔮 Future Enhancements

### Planned Features
- **Dynamic Configuration**: Runtime configuration updates
- **A/B Testing**: Model performance comparison
- **Auto-Optimization**: Automatic parameter tuning
- **Cloud Integration**: Remote configuration management

### Development Roadmap
- **Q1**: Enhanced validation and error reporting
- **Q2**: Configuration UI for easier management
- **Q3**: Performance monitoring integration
- **Q4**: Advanced model switching capabilities

## 🤝 Integration

### Backend Integration
The configuration system integrates with:
- **Backend Service**: Loads and applies configurations
- **Image Processing**: Uses model-specific settings
- **State Tracker**: Configures memory and processing
- **Logging System**: Sets up logging parameters

### Frontend Integration
- **UI Configuration**: Controls interface behavior
- **Model Selection**: Provides model switching options
- **Performance Display**: Shows model capabilities

---

## 📞 Support

For configuration issues:
1. Run `python validate_model_configs.py`
2. Check the troubleshooting section above
3. Review model-specific documentation
4. Verify file paths and permissions

---

**Last Updated**: August 2, 2025  
**Version**: 4.0 (VLM System Integration)  
**Maintainer**: AI Vision Intelligence Hub Team 