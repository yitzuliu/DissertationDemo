# SmolVLM2-500M Testing Suite

## Overview

This directory contains comprehensive testing tools for SmolVLM2-500M-Video-Instruct, optimized for Apple Silicon with MPS acceleration.

## Test Scripts

- **`unified_test.py`**: Quick and comprehensive testing with multiple options
- **`comprehensive_smolvlm2_test.py`**: Full test suite with detailed analysis
- **`tests/test_smolvlm2_capabilities.py`**: Capability assessment with 100% success rate validation

## Features

- **MPS Optimized**: Automatically uses Apple Silicon MPS for optimal performance
- **Multi-Modal Testing**: Tests image analysis, single frame video, multi-frame video, and direct video processing
- **Memory Monitoring**: Real-time MPS memory usage tracking
- **Performance Metrics**: Inference time measurement for all tests

## Usage

```bash
# Run from any directory - scripts use absolute paths
cd src/models/smolvlm2/SmolVLM2-500M-Video-Instruct/project_workspace

# Quick unified testing
python unified_test.py

# Comprehensive testing suite  
python comprehensive_smolvlm2_test.py

# Capability assessment
python tests/test_smolvlm2_capabilities.py
```

## Test Options

1. **Comprehensive Test**: Runs all test categories (images, single frame, multi-frame, direct video)
2. **Quick Test**: Representative samples from image and video testing
3. **Image Analysis Only**: Tests image understanding capabilities
4. **Video Tests Only**: All video processing methods
5. **Frame Preview Only**: Shows frame extraction without model inference

## Requirements

- SmolVLM2-500M-Video-Instruct model files (in current directory)
- Apple Silicon Mac with MPS support
- PyAV installed: `pip install av`
- OpenCV installed: `pip install opencv-python`

## Performance

- **Model Size**: 500M parameters (1.9GB)
- **Memory Usage**: ~1.9GB MPS memory  
- **Loading Time**: 2-4 seconds (excellent)
- **Video Support**: 64 frames @ 1 FPS, MP4 format
- **Image Support**: Up to 2048px resolution

## Test Assets

- **Video**: `../../../../../src/debug/viedo/Generated File June 24, 2025 - 5_04PM.mp4`
- **Images**: `../../../../../src/debug/images/` directory (IMG_0119.JPG, test_image.png, etc.)

## Project Structure

```
SmolVLM2-500M-Video-Instruct/
├── model.safetensors (1.9GB)      # ← Model files (from git clone)
├── config.json, tokenizer.json, etc.
└── project_workspace/             # ← Testing workspace
    ├── README.md                   # Main workspace documentation
    ├── requirements.txt            # Dependencies
    ├── unified_test.py             # ← Quick testing script
    ├── comprehensive_smolvlm2_test.py  # ← Full test suite
    ├── docs/                       # 📁 Documentation
    │   ├── README_TESTING.md       #   ← This file
    │   ├── SmolVLM2: Bringing Video Understanding to Every Device.md
    │   └── TODOLIST.md            #   Testing progress tracker
    ├── tests/                      # 📁 Test scripts
    │   ├── test_smolvlm2_capabilities.py  # Capability assessment
    │   └── mps_vs_cpu_test.py     #   Performance comparison
    ├── scripts/                    # 📁 Utility scripts
    │   └── model_wrapper.py       #   Model wrapper utilities
    ├── examples/                   # 📁 Example usage
    │   └── basic_inference.py     #   Basic usage examples
    ├── configs/                    # 📁 Configuration files
    │   └── model_config_template.json
    └── results/                    # 📁 Test outputs and results
```

## Test Results

All testing scripts achieve **100% success rates** with excellent performance on Apple Silicon MPS acceleration. 