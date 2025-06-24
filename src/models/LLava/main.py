# main_llava.py - The Backend Server for LLaVA via Ollama

from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
import cv2
import numpy as np
import ollama
import io
import json
import time

# --- 1. SETUP & CONFIGURATION ---

# Initialize FastAPI app
app = FastAPI(title="AI Manual Assistant Backend (LLaVA Ollama)", version="1.0")

# Model Configuration
MODEL_NAME = "llava:7b" 

# --- 2. MODEL LOADING ---
# No model loading here! Ollama handles it in a separate process.
# We will just check if the Ollama server is reachable on startup.
@app.on_event("startup")
async def startup_event():
    """On server startup, check if we can connect to Ollama."""
    print("Checking connection to Ollama server...")
    try:
        ollama.list()
        print(f"Successfully connected to Ollama. Model '{MODEL_NAME}' should be available.")
    except Exception as e:
        print("="*50)
        print("FATAL: Could not connect to Ollama server.")
        print("Please ensure the Ollama application is running and you have pulled the model with:")
        print(f"ollama run {MODEL_NAME}")
        print("="*50)
        # Note: The server will still start, but requests will fail.

# --- 3. HELPER MODULES ---

# A) Image Enhancement Module (Identical to previous versions)
def enhance_image(image_bytes: bytes):
    """Applies CLAHE enhancement to an image provided as bytes."""
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        merged = cv2.merge([cl, a, b])
        enhanced_frame = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
        
        # Convert enhanced frame back to bytes for Ollama
        _, buffer = cv2.imencode('.jpg', enhanced_frame)
        return buffer.tobytes()
    except Exception as e:
        print(f"Error during image enhancement: {e}")
        return image_bytes # Fallback to original bytes

# B) VLM Perception Engine (Adapted for Ollama)
def analyze_with_vlm(image_bytes: bytes, prompt: str):
    """Sends the image bytes and prompt to the Ollama server for analysis."""
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    'role': 'user',
                    'content': prompt,
                    'images': [image_bytes]
                }
            ]
        )
        return response['message']['content']
    except Exception as e:
        print(f"Error communicating with Ollama: {e}")
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not communicate with Ollama server.")

# --- 4. API ENDPOINT ---

@app.get("/", summary="Root endpoint to check server status")
def read_root():
    """A simple endpoint to confirm the server is running."""
    return {"status": "AI Manual Assistant Backend (LLaVA) is running."}

@app.post("/analyze", summary="Analyze an uploaded image with LLaVA")
async def analyze_image_endpoint(file: UploadFile = File(...)):
    """
    Receives an image file, enhances it, sends it to the Ollama server,
    and returns a structured JSON response.
    """
    start_time = time.time()
    
    image_bytes = await file.read()
    enhanced_image_bytes = enhance_image(image_bytes)
    
    structured_prompt = """
    You are an expert AI assistant for a hands-on task. Analyze the image.
    Respond ONLY with a valid JSON object. Do not include markdown formatting.
    The JSON object should have keys: "primary_tool", "key_objects", and "user_action".
    """
    analysis_text = analyze_with_vlm(enhanced_image_bytes, structured_prompt)

    try:
        clean_text = analysis_text.strip()
        # Some models still add the markdown block, so we robustly remove it
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
            
        parsed_json = json.loads(clean_text)
        
        end_time = time.time()
        processing_time = end_time - start_time
        parsed_json["processing_time_seconds"] = round(processing_time, 2)
        
        return parsed_json
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "The VLM did not return a valid JSON object.",
                "raw_response": analysis_text
            }
        )

# --- 5. HOW TO RUN THIS SERVER ---
# 1. Make sure Ollama is running in another terminal (`ollama serve`)
# 2. Run this script with: uvicorn main_llava:app --reload