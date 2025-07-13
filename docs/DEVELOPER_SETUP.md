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

**Example: Start the LLaVA MLX server (Recommended for Apple Silicon)**
```bash
python src/models/llava_mlx/run_llava_mlx.py
```

**Alternative: Start the Moondream2 server (Lightweight & Fast)**
```bash
python src/models/moondream2/run_moondream2_optimized.py
```

**Alternative: Start the Phi-3.5-Vision MLX server (High Accuracy)**
```bash
python "src/models/Phi_3.5_Vision MLX/run_phi3_vision_optimized.py"
```

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

## Troubleshooting

- **`ModuleNotFoundError`**: This usually means your virtual environment is not active or you ran a script from the wrong directory. Make sure `source ai_vision_env/bin/activate` is run in each terminal and that you are in the project's root directory.
- **`mlx` related errors**: Ensure you are on an Apple Silicon Mac and have successfully installed `mlx-vlm`.
- **Port conflicts**: If a port (8080, 8000, 5500) is already in use, you will need to stop the other application or modify the port in the appropriate script or configuration file.
- **Model loading failures**: Some models are large and may fail to load on systems with insufficient RAM. Ensure you have at least 16GB of free memory.
