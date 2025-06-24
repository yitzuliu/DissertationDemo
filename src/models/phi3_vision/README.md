# AI Manual Assistant: Vision Perception Engine

This project is the core vision perception engine for an AI Manual Assistant. It provides real-time, step-by-step guidance for hands-on tasks by analyzing a user's workspace via a camera using a state-of-the-art Vision-Language Model (VLM). The engine outputs structured data for a higher-level "State & Context Engine."

**Core Model:** `microsoft/Phi-3-vision-128k-instruct`

**Key Functionality:**
- Captures a single frame from a camera
- Analyzes the scene based on a structured prompt
- Returns a JSON object describing objects, tools, and user actions

---

## Table of Contents
- [Project Goal](#project-goal)
- [System Requirements](#system-requirements)
- [Setup & Installation (macOS)](#setup--installation-macos)
- [How to Run](#how-to-run)
- [Expected Output](#expected-output)
- [Implementation on iPhone (Conceptual Path)](#implementation-on-iphone-conceptual-path)
- [Customization](#customization)

---

## Project Goal

Transform a raw video feed into structured, actionable intelligence. Beyond object detection, this module performs **contextual activity recognition**—answering not just "What is this?" but also "What is the user doing with these objects?"

**Primary Output Example:**
```json
{
  "primary_tool": "Phillips screwdriver",
  "key_objects": [
    "Wooden panel",
    "M4 screw",
    "Instruction manual"
  ],
  "user_action": "The user is aligning the screwdriver with a screw on the wooden panel.",
  "is_safe": true
}
```

---

## System Requirements
- macOS (tested)
- Python 3.8+
- Webcam
- Sufficient disk space (model download ~8GB)

---

## Setup & Installation (macOS)

1. **Clone the repository and navigate to the project directory.**
2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv phi3-vision-env
   source phi3-vision-env/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## How to Run

1. **Activate your virtual environment:**
   ```bash
   source phi3-vision-env/bin/activate
   ```
2. **Run the main script:**
   ```bash
   python run_phi3_vision.py
   ```
   - On first run, macOS will prompt for camera access. Click "OK" to allow.
   - The script will download the Phi-3-vision model (~8GB) if not already present.
   - A window will show your webcam feed.
   - Position your camera to view your workspace.
   - Press `c` to capture a frame for analysis.
   - Press `q` to quit the application.

---

## Expected Output

After pressing `c`, the script will analyze the captured frame. Example terminal output:

```
Image captured! Starting analysis...
Generating response from model...
Analysis completed in 12.34 seconds.

==================== AI ANALYSIS ====================
Raw Response:
{
  "primary_tool": "Phillips screwdriver",
  "key_objects": [
    "Wooden panel",
    "M4 screw",
    "Instruction manual"
  ],
  "user_action": "The user is aligning the screwdriver with a screw on the wooden panel.",
  "is_safe": true
}
Parsed JSON:
{
  "primary_tool": "Phillips screwdriver",
  "key_objects": [
    "Wooden panel",
    "M4 screw",
    "Instruction manual"
  ],
  "user_action": "The user is aligning the screwdriver with a screw on the wooden panel.",
  "is_safe": true
}
Ready for next capture. Press 'c' to capture again, or 'q' to quit.
```

---

## Implementation on iPhone (Conceptual Path)

Running a model of this size directly on an iPhone is a significant engineering challenge. The path forward involves model conversion and a native iOS app.

### Key Challenges
1. **Model Size:** The ~8GB Phi-3 model is too large for a typical iOS app bundle and may exceed RAM limits.
2. **Model Format:** The PyTorch model must be converted to a mobile-friendly format (e.g., Core ML).
3. **Performance:** Inference must be optimized for near real-time use without excessive battery drain.

### Conceptual Steps
1. **Model Quantization & Conversion:**
   - Use `coremltools` to convert the PyTorch model to Core ML format.
   - Apply quantization (16-bit or 8-bit) to reduce file size and memory usage.
2. **Native iOS App Development (Swift):**
   - Create a new iOS project in Xcode.
   - Import the converted `.mlmodel` file.
   - Use Apple's `Vision` framework for camera input and `CoreML` for inference.
3. **Conceptual Swift Code:**
   ```swift
   import CoreML
   import Vision

   // Load your converted Core ML model
   let model = try MyPhi3VisionModel(configuration: .init())

   // Create a Vision request
   let request = VNCoreMLRequest(model: try VNCoreMLModel(for: model.model)) { request, error in
       // Handle the model's output (which would be text)
       guard let results = request.results as? [VNCoreMLFeatureValueObservation] else { return }
       // Process results...
   }

   // Use AVCaptureSession to get camera frames (CVPixelBuffer)
   // For each frame, create a VNImageRequestHandler and perform the request.
   let handler = VNImageRequestHandler(cvPixelBuffer: pixelBuffer, options: [:])
   try? handler.perform([request])
   ```

---

## Customization

You can easily change the "brain" of the assistant by modifying the main prompt.

- Open `run_phi3_vision.py`.
- Find the `structured_prompt` variable.
- Change the instructions and required JSON keys to suit your task. For example, for a cooking assistant:

```python
structured_prompt = """
You are an expert cooking assistant. Analyze the image from the user's kitchen.
Respond ONLY with a valid JSON object.
The JSON object should have the following keys:
- "ingredients_visible": A list of ingredients you can identify.
- "utensils_in_use": The primary utensil the user is holding.
- "current_cooking_step": Describe what the user is doing (e.g., "chopping onions", "stirring a pot").
"""
```

---

## License

See [LICENSE](../../../../LICENSE) for details.