# SmolVLM2-500M Unified Testing Suite

## Overview

The `unified_test.py` script combines all SmolVLM2-500M-Video-Instruct testing functionality into one comprehensive tool, optimized for Apple Silicon with MPS acceleration.

## Features

- **MPS Optimized**: Automatically uses Apple Silicon MPS for optimal performance
- **Multi-Modal Testing**: Tests image analysis, single frame video, multi-frame video, and direct video processing
- **Memory Monitoring**: Real-time MPS memory usage tracking
- **Performance Metrics**: Inference time measurement for all tests

## Usage

```bash
cd src/models/smolvlm2
python unified_test.py
```

## Test Options

1. **Comprehensive Test**: Runs all test categories (images, single frame, multi-frame, direct video)
2. **Quick Test**: Representative samples from image and video testing
3. **Image Analysis Only**: Tests image understanding capabilities
4. **Video Tests Only**: All video processing methods
5. **Frame Preview Only**: Shows frame extraction without model inference

## Requirements

- SmolVLM2-500M-Video-Instruct model in local directory
- Apple Silicon Mac with MPS support
- PyAV installed: `pip install av`
- OpenCV installed: `pip install opencv-python`

## Performance

- **Model Size**: 500M parameters (1.9GB)
- **Memory Usage**: ~1.9GB MPS memory
- **Video Support**: 64 frames @ 1 FPS, MP4 format
- **Image Support**: Up to 2048px resolution

## Test Files

- **Video**: `src/debug/viedo/Generated File June 24, 2025 - 5_04PM.mp4`
- **Images**: `src/debug/images/` directory (IMG_0119.JPG, etc.)

This unified script replaces the previous individual test scripts (test_video_smolvlm2.py, simple_video_test.py, quick_test_smolvlm2.py, direct_video_test.py). 