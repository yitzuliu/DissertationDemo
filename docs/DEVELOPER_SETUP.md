# AI Manual Assistant - Developer Setup Guide

This guide provides step-by-step instructions for setting up the development environment for the AI Manual Assistant project.

## Prerequisites

### System Requirements
- **macOS (Apple Silicon M1/M2/M3 recommended) or Linux**.
- **Python 3.9+**.
- **16GB RAM minimum** (32GB recommended for running larger models).
- **50GB free disk space** for models and dependencies.

### Required Software
- **Git**.
- A Python environment manager like `venv` (built-in) or `conda`.

## Setup Process

### 1. Clone the Repository

```bash
git clone https://github.com/yitzuliu/DissertationDemo.git
cd destination_code
```

### 2. Python Environment Setup

It is strongly recommended to use a virtual environment to manage project dependencies.

```bash
# Create a virtual environment using venv
python3 -m venv ai_vision_env

# Activate the virtual environment
# On macOS/Linux:
source ai_vision_env/bin/activate
# On Windows (note: some models may not be compatible):
# .\ai_vision_env\Scripts\activate
```

### 3. Install Dependencies

Install the required Python packages from the `requirements.txt` file.

```bash
# Ensure your virtual environment is active
pip install -r requirements.txt
```

### 4. Special Setup for Apple Silicon (M1/M2/M3)

To run the high-performance MLX-optimized models (like LLaVA and Phi-3.5-Vision), you **must** install the `mlx-vlm` package. This is not required for other models but is essential for the best-performing ones.

```bash
# From your active virtual environment
pip install mlx-vlm
```

This package enables the use of Apple's unified memory and neural engine for dramatic performance improvements. Without it, larger models will be too slow to be usable.

## Running the Project

The AI Manual Assistant uses a **3-layer architecture**. You must start three separate components in three separate terminal windows. Make sure your virtual environment is activated in each terminal.

### Step 1: Start a Model Server (Terminal 1)

Choose **one** model to run. Each model runs as its own server.

**🏆 Recommended: SmolVLM2-500M-Video-Instruct (Best Overall Performance)**
```bash
python src/models/smolvlm2/run_smolvlm2.py
```
- **VQA Accuracy**: 66.0% (highest)
- **Inference Time**: 6.61s (balanced)
- **Memory Usage**: 2.08GB

**⚡ Alternative: Moondream2 (Fastest Inference)**
```bash
python src/models/moondream2/run_moondream2_optimized.py
```
- **VQA Accuracy**: 56.0%
- **Inference Time**: 4.06s (fastest)
- **Memory Usage**: 0.10GB (lowest)

**✅ Alternative: SmolVLM-500M-Instruct (Reliable Alternative)**
```bash
python src/models/smolvlm/run_smolvlm.py
```
- **VQA Accuracy**: 64.0%
- **Inference Time**: 5.98s
- **Memory Usage**: 1.58GB

**⚠️ Not Recommended: LLaVA-MLX (Underperforming)**
```bash
python src/models/llava_mlx/run_llava_mlx.py
```
- **VQA Accuracy**: 34.0% (significant degradation)
- **Inference Time**: 17.86s (slow due to reloading)
- **Issue**: Model reloading for each image causing performance degradation

**Alternative: Phi-3.5-Vision MLX (High Accuracy, Moderate Speed)**
```bash
python "src/models/Phi_3.5_Vision MLX/run_phi3_vision_optimized.py"
```
- **VQA Accuracy**: 60.0%
- **Inference Time**: 13.61s (moderate)
- **Memory Usage**: 1.53GB

You should see output indicating the server has started, usually on `http://localhost:8080`.

### Step 2: Start the Backend Server (Terminal 2)

The backend server acts as a gateway between the frontend and the model server.

```bash
python src/backend/main.py
```

This server will start on `http://localhost:8000`.

### Step 3: Start the Frontend Server (Terminal 3)

The frontend is a simple web interface for interacting with the system.

```bash
# Navigate to the frontend directory first
cd src/frontend

# Start a basic Python HTTP server
python -m http.server 5500
```

This server will start on `http://localhost:5500`.

### Step 4: Use the Application

Open your web browser and navigate to **`http://localhost:5500`**. You should see the application interface, grant camera permissions, and be able to start interacting with the AI assistant.

## Model Performance Guide

### 🏆 Best Models for Different Use Cases

#### Production Use (Recommended)
1. **SmolVLM2-500M-Video-Instruct**: Best overall performance (66.0% VQA accuracy)
2. **SmolVLM-500M-Instruct**: Excellent alternative (64.0% VQA accuracy)

#### Speed-Critical Applications
- **Moondream2**: Fastest inference (4.06s average)

#### Resource-Constrained Environments
- **Moondream2**: Lowest memory usage (0.10GB)
- **SmolVLM-500M-Instruct**: Good balance (1.58GB)

#### ⚠️ Models to Avoid
- **LLaVA-MLX**: Underperforming due to reloading overhead (34.0% VQA accuracy)

### Performance Testing

The project includes a comprehensive VQA 2.0 testing framework:

```bash
# Quick test (10 questions)
python src/testing/vqa_test.py --questions 10 --models smolvlm_v2_instruct

# Standard test (15 questions)
python src/testing/vqa_test.py --questions 15 --models smolvlm_v2_instruct

# Comprehensive test (20 questions)
python src/testing/vqa_test.py --questions 20 --models smolvlm_v2_instruct
```

For detailed test results and time analysis, see `src/testing/vqa_test_result.md`.

## Troubleshooting

- **`ModuleNotFoundError`**: This usually means your virtual environment is not active or you ran a script from the wrong directory. Make sure `source ai_vision_env/bin/activate` is run in each terminal and that you are in the project's root directory.
- **`mlx` related errors**: Ensure you are on an Apple Silicon Mac and have successfully installed `mlx-vlm`.
- **Port conflicts**: If a port (8080, 8000, 5500) is already in use, you will need to stop the other application or modify the port in the appropriate script or configuration file.
- **Model loading failures**: Some models are large and may fail to load on systems with insufficient RAM. Ensure you have at least 16GB of free memory.
- **LLaVA-MLX performance issues**: If you experience poor performance with LLaVA-MLX, this is expected due to model reloading overhead. Switch to SmolVLM2 or SmolVLM for better performance.

## Development Workflow

### Testing Different Models

To test different models, you can easily switch between them:

1. **Stop the current model server** (Ctrl+C in Terminal 1)
2. **Start a different model** using one of the commands above
3. **The frontend and backend will automatically connect** to the new model

### Performance Monitoring

Monitor model performance using the built-in testing framework:

```bash
# Test specific model performance
python src/testing/vqa_test.py --questions 10 --models moondream2

# Compare multiple models
python src/testing/vqa_test.py --questions 10 --models smolvlm_v2_instruct moondream2
```

### Configuration

Model configurations are stored in `src/config/model_configs/`. You can modify these files to adjust model parameters, prompts, and other settings.

## Additional Resources

- **Model Comparison**: See `docs/MODEL_COMPARISON.md` for detailed model analysis
- **API Documentation**: See `docs/API.md` for API usage
- **Troubleshooting**: See `docs/TROUBLESHOOTING.md` for common issues
- **FAQ**: See `docs/FAQ.md` for frequently asked questions

---

**Last Updated**: July 19, 2025  
**Test Framework**: VQA 2.0 Standard Evaluation  
**Hardware**: MacBook Air M3, 16GB RAM
