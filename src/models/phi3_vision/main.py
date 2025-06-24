# main_phi3.py - The Complete Backend Server for Phi-3 Vision

from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
import cv2
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoProcessor
import io
import json
import time

# --- 1. SETUP & CONFIGURATION ---

# Initialize FastAPI app
app = FastAPI(title="AI Manual Assistant Backend (Phi-3 Vision)", version="1.0")

# Model Configuration
MODEL_ID = "microsoft/Phi-3-vision-128k-instruct"

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
# This is a large model. Loading will take time and significant memory.
model = None
processor = None
try:
    print(f"Loading model '{MODEL_ID}' into memory. This will take several minutes and >8GB of RAM...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, 
        device_map=DEVICE, 
        trust_remote_code=True, 
        torch_dtype=TORCH_DTYPE
    )
    processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
    print("Model loaded successfully.")
except Exception as e:
    print(f"FATAL: Could not load model. Error: {e}")
    # The app will still run but will fail at the /analyze endpoint.

# --- 3. HELPER MODULES ---

# A) Image Enhancement Module (Identical to the previous version)
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
        enhanced_pil_image = Image.fromarray(cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2RGB))
        return enhanced_pil_image
    except Exception as e:
        print(f"Error during image enhancement: {e}")
        return Image.open(io.BytesIO(image_bytes))

# B) VLM Perception Engine (Adapted for Phi-3)
def analyze_with_vlm(image: Image.Image, prompt: str):
    """Analyzes the image using the pre-loaded Phi-3 Vision model."""
    if model is None or processor is None:
        raise HTTPException(status_code=500, detail="Model or processor is not available.")

    try:
        messages = [
            {"role": "user", "content": f"<|image_1|>\n{prompt}"},
        ]
        prompt_for_model = processor.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(prompt_for_model, [image], return_tensors="pt").to(DEVICE)

        generation_args = {
            "max_new_tokens": 500,
            "temperature": 0.0,
            "do_sample": False,
        }
        
        generate_ids = model.generate(**inputs, eos_token_id=processor.tokenizer.eos_token_id, **generation_args)
        generate_ids = generate_ids[:, inputs['input_ids'].shape[1]:]
        response = processor.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
        
        return response
    except Exception as e:
        print(f"Error during VLM analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze image with VLM.")

# --- 4. API ENDPOINT ---

@app.get("/", summary="Root endpoint to check server status")
def read_root():
    """A simple endpoint to confirm the server is running."""
    return {"status": "AI Manual Assistant Backend (Phi-3) is running."}

@app.post("/analyze", summary="Analyze an uploaded image with Phi-3 Vision")
async def analyze_image_endpoint(file: UploadFile = File(...)):
    """
    Receives an image file, enhances it, analyzes it with Phi-3 Vision,
    and returns a structured JSON response.
    """
    start_time = time.time()
    
    image_bytes = await file.read()
    enhanced_pil_image = enhance_image(image_bytes)
    
    structured_prompt = """
    You are an expert AI assistant for a hands-on manual task. Analyze the image.
    Respond ONLY with a valid JSON object. Do not include any other text, explanations, or markdown.
    The JSON object should have keys: "primary_tool", "key_objects", and "user_action".
    """
    analysis_text = analyze_with_vlm(enhanced_pil_image, structured_prompt)

    try:
        clean_text = analysis_text.strip().replace("```json", "").replace("```", "")
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
# uvicorn main_phi3:app --reload