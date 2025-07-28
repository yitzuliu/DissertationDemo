# VLM Testing Suite Documentation

## Overview
This directory (`vlm/`) contains scripts and resources for evaluating and benchmarking Vision-Language Models (VLMs) on a variety of tasks, including performance, general image and text understanding, and context retention. The results of these tests are saved in the `../results/` directory for further analysis and reporting.

**Key Features:**
- ✅ **Unified SmolVLM Support**: All test scripts now use GGUF version via HTTP API (consistent with production deployment)
- ✅ **Port Safety**: Automatic cleanup of SmolVLM server processes on exit
- ✅ **Robust Error Handling**: Comprehensive exception handling and recovery mechanisms
- ✅ **Memory Management**: Proper cleanup of model resources after testing

---

## Directory Structure

- **vlm/**
  - `vlm_tester.py` — Main performance and capability benchmarking script for VLMs (image and text tasks, NOT VQA 2.0 evaluation).
    - **Features**: Unified SmolVLM GGUF support, automatic port cleanup, comprehensive error handling
  - `vlm_context_tester.py` — Tests multi-turn context understanding and conversation retention.
    - **Features**: Unified SmolVLM GGUF support, automatic port cleanup, conversation flow testing
  - `__init__.py` — Marks this directory as a Python package.
  - `README.md` — This documentation file.
  - `__pycache__/` — Python bytecode cache (auto-generated).

- **../results/**
  - Contains all output JSON files from test runs, including:
    - `test_results_*.json` — Performance and general image/text test results (not VQA 2.0).
    - `context_understanding_test_results_*.json` — Context understanding test results.
    - `vqa2_results_*.json` — VQA 2.0 COCO evaluation results (from scripts in the `../vqa/` folder).
    - `*_intermediate_*.json` — Intermediate results for each model during batch runs.

---

## Test Scripts and Their Outputs

### 1. Performance & Capability Testing (`vlm_tester.py`)
- **Purpose:**
  - Benchmarks model load time, inference speed, memory usage, and accuracy on general vision and text tasks.
  - Does **not** perform VQA 2.0 COCO evaluation or use the VQA dataset.
  - **SmolVLM Support**: Uses GGUF version via HTTP API with automatic server management
- **How to Run:**
  ```bash
  source ai_vision_env/bin/activate
  python vlm_tester.py                    # Test all models
  python vlm_tester.py SmolVLM-500M-Instruct  # Test specific model
  ```
- **Features:**
  - ✅ Automatic SmolVLM server startup and cleanup
  - ✅ Port conflict resolution (kills existing processes on port 8080)
  - ✅ Retry mechanism (up to 3 attempts for server startup)
  - ✅ Memory usage tracking and cleanup
  - ✅ Comprehensive error handling
- **Output:**
  - Results are saved as `test_results_YYYYMMDD_HHMMSS.json` in `../results/`.
  - Intermediate results for each model are saved as `test_results_intermediate_<ModelName>.json`.

### 2. Context Understanding Testing (`vlm_context_tester.py`)
- **Purpose:**
  - Evaluates a model's ability to maintain conversation context and answer follow-up questions based on previous dialogue and image content.
  - **SmolVLM Support**: Uses GGUF version via HTTP API with automatic server management
- **How to Run:**
  ```bash
  source ai_vision_env/bin/activate
  python vlm_context_tester.py
  ```
- **Features:**
  - ✅ Automatic SmolVLM server startup and cleanup
  - ✅ Port conflict resolution (kills existing processes on port 8080)
  - ✅ Retry mechanism (up to 3 attempts for server startup)
  - ✅ Multi-turn conversation testing
  - ✅ Context retention evaluation
  - ✅ Memory usage tracking and cleanup
- **Output:**
  - Results are saved as `context_understanding_test_results_YYYYMMDD_HHMMSS.json` in `../results/`.
  - Intermediate results for each model are saved as `context_understanding_test_results_intermediate_<ModelName>.json`.

### 3. VQA 2.0 COCO Evaluation (see also `../vqa/`)
- **Purpose:**
  - Evaluates models on the VQA 2.0 COCO dataset for standardized accuracy metrics.
  - **All VQA 2.0 testing is handled by scripts in the `../vqa/` folder, not in `vlm/`.**
  - **SmolVLM Support**: VQA framework also uses unified GGUF version via HTTP API
- **How to Run:**
  - Use the VQA test scripts in the `../vqa/` directory (e.g., `vqa_test.py`).
  ```bash
  python ../vqa/vqa_test.py --models smolvlm_instruct --questions 10 --verbose
  ```
- **Output:**
  - Results are saved as `vqa2_results_coco_YYYYMMDD_HHMMSS.json` in `../results/`.

---

## How to Interpret Results
- **test_results_*.json:**
  - Contains detailed timing, memory, and accuracy metrics for each model and test case on general image and text tasks (not VQA 2.0).
  - Includes SmolVLM GGUF performance metrics and server management logs.
- **context_understanding_test_results_*.json:**
  - Contains conversation flows, model responses, and context retention scores.
  - Includes multi-turn conversation evaluation with SmolVLM GGUF.
- **vqa2_results_*.json:**
  - Contains VQA accuracy and answer breakdowns for the COCO dataset (from the `../vqa/` folder).
  - Includes SmolVLM GGUF VQA performance metrics.
- **Intermediate files:**
  - Useful for debugging or tracking progress during long batch runs.
  - Include server startup/cleanup logs for SmolVLM testing.

---

## Adding New Models or Tests
- To add a new model, update the model loader section in `vlm_tester.py` and/or `vlm_context_tester.py`.
- For SmolVLM models, use the unified GGUF approach with HTTP API support.
- To add new test images or prompts, update the relevant materials directory (see `../materials/`).
- All outputs will be automatically saved in the `../results/` directory.

---

## Best Practices
- Always activate the correct Python environment before running tests:
  ```bash
  source ai_vision_env/bin/activate
  ```
- Ensure test images are placed in the appropriate materials directory (`../materials/images/`).
- For SmolVLM testing, ensure `llama-server` is installed and port 8080 is available.
- The system automatically handles SmolVLM server startup, port conflicts, and cleanup.
- Review the output JSON files in `../results/` for detailed metrics and analysis.
- For large batch tests, monitor intermediate result files for progress and troubleshooting.
- Check server cleanup logs to ensure proper resource management.

---

## Contact & Support
For questions, bug reports, or contributions, please refer to the main project README or contact the maintainers.

## Troubleshooting

### SmolVLM Server Issues
- **Port 8080 occupied**: The system automatically detects and kills conflicting processes
- **Server startup failure**: Check if `llama-server` is properly installed
- **Server not responding**: The system includes retry mechanisms and timeout handling

### Memory Issues
- **High memory usage**: Models are automatically cleaned up after testing
- **Memory leaks**: Check cleanup logs in test output

### Performance Issues
- **Slow inference**: Check model loading times and server response times
- **Timeout errors**: Adjust timeout settings in test configuration

---

_Last updated: 2025-07-28_