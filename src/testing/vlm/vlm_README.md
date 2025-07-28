# VLM Testing Suite Documentation

## Overview
This directory (`vlm/`) contains scripts and resources for evaluating and benchmarking Vision-Language Models (VLMs) on a variety of tasks, including performance, general image and text understanding, and context retention. The results of these tests are saved in the `../results/` directory for further analysis and reporting.

---

## Directory Structure

- **vlm/**
  - `vlm_tester.py` — Main performance and capability benchmarking script for VLMs (image and text tasks, NOT VQA 2.0 evaluation).
  - `vlm_context_tester.py` — Tests multi-turn context understanding and conversation retention.
  - `__init__.py` — Marks this directory as a Python package.
  - `vlm_README.md` — This documentation file.
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
- **How to Run:**
  ```bash
  source ai_vision_env/bin/activate
  python vlm_tester.py
  ```
- **Output:**
  - Results are saved as `test_results_YYYYMMDD_HHMMSS.json` in `../results/`.
  - Intermediate results for each model are saved as `test_results_intermediate_<ModelName>.json`.

### 2. Context Understanding Testing (`vlm_context_tester.py`)
- **Purpose:**
  - Evaluates a model's ability to maintain conversation context and answer follow-up questions based on previous dialogue and image content.
- **How to Run:**
  ```bash
  source ai_vision_env/bin/activate
  python vlm_context_tester.py
  ```
- **Output:**
  - Results are saved as `context_understanding_test_results_YYYYMMDD_HHMMSS.json` in `../results/`.
  - Intermediate results for each model are saved as `context_understanding_test_results_intermediate_<ModelName>.json`.

### 3. VQA 2.0 COCO Evaluation (see also `../vqa/`)
- **Purpose:**
  - Evaluates models on the VQA 2.0 COCO dataset for standardized accuracy metrics.
  - **All VQA 2.0 testing is handled by scripts in the `../vqa/` folder, not in `vlm/`.**
- **How to Run:**
  - Use the VQA test scripts in the `../vqa/` directory (e.g., `vqa_test.py`).
- **Output:**
  - Results are saved as `vqa2_results_coco_YYYYMMDD_HHMMSS.json` in `../results/`.

---

## Latest Test Results Summary (Updated: 2025-07-28)

### **Performance Rankings**

| Model | Avg Inference (s) | Load Time (s) | Memory Diff (GB) | Status |
|-------|------------------|---------------|------------------|--------|
| **SmolVLM GGUF** | 🏆 **0.93** | 2.04 | 0.07 | ✅ **Fastest** |
| **SmolVLM2-MLX** | 9.80 | 1.02 | 0.06 | ✅ **Fast & Accurate** |
| **Phi-3.5-MLX** | 10.54 | 1.52 | 0.28 | ✅ **Balanced** |
| **Moondream2** | 11.58 | 5.34 | -1.15 | ✅ **Best Overall** |
| **LLaVA-MLX** | 21.93 | 2.17 | 0.46 | ⚠️ **Issues** |

### **Context Understanding Results**

| Model | Context Success Rate | Avg Context Time (s) | Notes |
|-------|-------------------|---------------------|-------|
| **SmolVLM GGUF** | 100% | ~0.9 | Best context retention, fastest |
| **SmolVLM2-MLX** | 100% | ~6.2 | Consistent but generic answers |
| **Moondream2** | 0% | ~5.9 | Vision-only, no context |
| **LLaVA-MLX** | ~66% | ~19.5 | Incomplete, batch inference issues |
| **Phi-3.5-MLX** | ~66% | ~6.9 | Incomplete answers |

---

## How to Interpret Results
- **test_results_*.json:**
  - Contains detailed timing, memory, and accuracy metrics for each model and test case on general image and text tasks (not VQA 2.0).
- **context_understanding_test_results_*.json:**
  - Contains conversation flows, model responses, and context retention scores.
- **vqa2_results_*.json:**
  - Contains VQA accuracy and answer breakdowns for the COCO dataset (from the `../vqa/` folder).
- **Intermediate files:**
  - Useful for debugging or tracking progress during long batch runs.

---

## Model Recommendations

### **Best Overall Performance**
- **Moondream2**: Best accuracy, balanced speed
- **Use case**: General vision tasks, accuracy-critical applications

### **Fastest Inference**
- **SmolVLM GGUF**: Fastest inference (0.93s), stable, unified API
- **Use case**: Speed-critical applications, production deployments

### **Context Understanding**
- **SmolVLM GGUF**: Best context retention, fastest context inference (~0.9s)
- **Use case**: Multi-turn conversations, context-dependent tasks

### **Avoid for Production**
- **LLaVA-MLX**: Batch inference issues, poor performance, slow inference
- **Use case**: Research only, not recommended for production

---

## Adding New Models or Tests
- To add a new model, update the model loader section in `vlm_tester.py` and/or `vlm_context_tester.py`.
- To add new test images or prompts, update the relevant materials directory (see `../materials/`).
- All outputs will be automatically saved in the `../results/` directory.

---

## Best Practices
- Always activate the correct Python environment before running tests:
  ```bash
  source ai_vision_env/bin/activate
  ```
- Ensure test images are placed in the appropriate materials directory (`../materials/images/`).
- Review the output JSON files in `../results/` for detailed metrics and analysis.
- For large batch tests, monitor intermediate result files for progress and troubleshooting.

---

## Contact & Support
For questions, bug reports, or contributions, please refer to the main project README or contact the maintainers.

---

_Last updated: 2025-07-28_