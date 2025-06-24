# main.py - The Complete Backend Server

from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
import cv2
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import io
import json
import time

# --- 1. SETUP & CONFIGURATION ---

# Initialize FastAPI app
app = FastAPI(title="AI Manual Assistant Backend", version="1.0")

# Model Configuration
MODEL_ID = "vikhyatk/moondream2"
MODEL_REVISION = "2024-05-20"

# Hardware Configuration
if torch.backends.mps.is_available():
    DEVICE = "mps"
    TORCH_DTYPE = torch.bfloat16
    print("Backend configured to use Apple Metal (MPS) GPU.")
else:
    DEVICE = "cpu"
    TORCH_DTYPE = torch.float32
    print("Backend configured to use CPU.")

# --- 2. MODEL LOADING (GLOBAL) ---
# Load the model only ONCE when the server starts.
# This is crucial for performance.
try:
    print(f"Loading model '{MODEL_ID}' into memory...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        trust_remote_code=True,
        revision=MODEL_REVISION,
        torch_dtype=TORCH_DTYPE,
    ).to(DEVICE)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
    print("Model loaded successfully.")
except Exception as e:
    print(f"FATAL: Could not load model. Error: {e}")
    model = None # Set model to None if loading fails

# --- 3. HELPER MODULES ---

# A) Image Enhancement Module
def enhance_image(image_bytes: bytes):
    """Applies CLAHE enhancement to an image provided as bytes."""
    try:
        # Convert bytes to a numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        # Decode image
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Apply CLAHE
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l_channel)
        merged = cv2.merge([cl, a_channel, b_channel])
        enhanced_frame = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
        
        # Convert enhanced frame back to PIL Image for the model
        enhanced_pil_image = Image.fromarray(cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2RGB))
        return enhanced_pil_image
    except Exception as e:
        print(f"Error during image enhancement: {e}")
        # Fallback: just use the original image
        return Image.open(io.BytesIO(image_bytes))

# B) VLM Perception Engine
def analyze_with_vlm(image: Image, prompt: str):
    """Analyzes the image using the pre-loaded Moondream2 model."""
    if model is None:
        raise HTTPException(status_code=500, detail="Model is not available.")

    try:
        enc_image = model.encode_image(image)
        response = model.answer_question(enc_image, prompt, tokenizer)
        return response
    except Exception as e:
        print(f"Error during VLM analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze image with VLM.")

# --- 4. API ENDPOINT ---

@app.get("/", summary="Root endpoint to check server status")
def read_root():
    """A simple endpoint to confirm the server is running."""
    return {"status": "AI Manual Assistant Backend is running."}

@app.post("/analyze", summary="Analyze an uploaded image")
async def analyze_image_endpoint(file: UploadFile = File(...)):
    """
    Receives an image file, enhances it, analyzes it with Moondream2,
    and returns a structured JSON response.
    """
    start_time = time.time()
    
    # Read image bytes from the uploaded file
    image_bytes = await file.read()

    # Step 1: Enhance the Image
    enhanced_pil_image = enhance_image(image_bytes)
    
    # Step 2: Analyze with VLM
    structured_prompt = """
    Analyze the image and describe the scene in JSON format with keys "primary_tool", "key_objects", and "user_action".
    """
    analysis_text = analyze_with_vlm(enhanced_pil_image, structured_prompt)

    # Step 3: Parse and Return Response
    try:
        # Clean the response and parse it as JSON
        clean_text = analysis_text.strip().replace("```json", "").replace("```", "")
        parsed_json = json.loads(clean_text)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Add processing time to the response for performance analysis
        parsed_json["processing_time_seconds"] = round(processing_time, 2)
        
        return parsed_json
    except json.JSONDecodeError:
        # If the model fails to return valid JSON, return an error
        raise HTTPException(
            status_code=500,
            detail={
                "error": "The VLM did not return a valid JSON object.",
                "raw_response": analysis_text
            }
        )

# --- 5. HOW TO RUN THIS SERVER ---
# Open your terminal in this directory and run the following command:
# uvicorn main:app --reload
#
# --reload means the server will automatically restart when you save changes.