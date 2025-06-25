# main_phi3.py - The Complete Backend Server for Phi-3 Vision

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from PIL import Image
import cv2
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoProcessor, AutoConfig
import io
import json
import time
import base64
import re

# --- 1. SETUP & CONFIGURATION ---

# Initialize FastAPI app
app = FastAPI(title="AI Manual Assistant Backend (Phi-3 Vision)", version="1.0")

# Model Configuration
MODEL_ID = "microsoft/Phi-3-vision-128k-instruct"

# Hardware Configuration - Fixed for MPS compatibility
# Force CPU mode to avoid MPS device allocation issues
DEVICE = "cpu"
TORCH_DTYPE = torch.float32
print("Backend configured to use CPU (MPS compatibility mode).")

# Global variables for model and processor
model = None
processor = None

# --- 2. PYDANTIC MODELS ---

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[Dict[str, Any]]
    model: Optional[str] = "phi3_vision"
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.1

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

# --- 3. MODEL LOADING ---

def load_model():
    """Load the Phi-3 Vision model and processor into global variables."""
    global model, processor
    
    try:
        print(f"Loading model '{MODEL_ID}' into memory. This will take several minutes and >8GB of RAM...")
        
        # Load config and disable FlashAttention2 for compatibility
        print("Loading and modifying config to disable FlashAttention2...")
        config = AutoConfig.from_pretrained(MODEL_ID, trust_remote_code=True)
        config._attn_implementation = "eager"  # Disable FlashAttention2
        
        # Explicitly disable cache at config level for DynamicCache compatibility
        if hasattr(config, 'use_cache'):
            config.use_cache = False
        if hasattr(config, '_use_cache'):
            config._use_cache = False
        
        # Load processor first
        processor = AutoProcessor.from_pretrained(
            MODEL_ID, 
            trust_remote_code=True,
            torch_dtype=TORCH_DTYPE
        )
        
        # Load model with CPU configuration and cache disabled
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            config=config,
            torch_dtype=TORCH_DTYPE,
            trust_remote_code=True,
            device_map=None,  # Don't use device_map
            low_cpu_mem_usage=True,
            attn_implementation="eager"  # Explicit eager attention
        )
        
        # Move to CPU explicitly
        model = model.to(DEVICE)
        model.eval()
        
        # Additional cache configuration
        if hasattr(model, 'config'):
            model.config.use_cache = False
            if hasattr(model.config, '_use_cache'):
                model.config._use_cache = False
        
        print("Model loaded successfully.")
        return True
        
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

# Load model on startup
@app.on_event("startup")
async def startup_event():
    success = load_model()
    if not success:
        print("WARNING: Model failed to load. Server will start but image analysis will not work.")

# --- 4. UTILITY FUNCTIONS ---

def extract_base64_images(messages: List[Dict[str, Any]]) -> List[Image.Image]:
    """Extract base64 encoded images from chat messages."""
    images = []
    
    for message in messages:
        content = message.get("content", "")
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "image_url":
                    image_url = item.get("image_url", {}).get("url", "")
                    if image_url.startswith("data:image"):
                        try:
                            # Extract base64 data
                            base64_data = image_url.split(",")[1]
                            image_data = base64.b64decode(base64_data)
                            image = Image.open(io.BytesIO(image_data))
                            if image.mode != "RGB":
                                image = image.convert("RGB")
                            images.append(image)
                        except Exception as e:
                            print(f"Error processing base64 image: {e}")
                            continue
        elif isinstance(content, str):
            # Look for base64 images in string content
            base64_pattern = r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)'
            matches = re.findall(base64_pattern, content)
            for match in matches:
                try:
                    image_data = base64.b64decode(match)
                    image = Image.open(io.BytesIO(image_data))
                    if image.mode != "RGB":
                        image = image.convert("RGB")
                    images.append(image)
                except Exception as e:
                    print(f"Error processing base64 image from string: {e}")
                    continue
    
    return images

def format_prompt_for_phi3(messages: List[Dict[str, Any]]) -> str:
    """Format messages for Phi-3 Vision with proper image placeholders."""
    formatted_parts = []
    image_count = 0
    
    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        
        if role == "user":
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                        elif item.get("type") == "image_url":
                            image_count += 1
                            text_parts.append(f"<|image_{image_count}|>")
                formatted_parts.append(" ".join(text_parts))
            else:
                # Handle string content with embedded base64 images
                text_with_placeholders = content
                base64_pattern = r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)'
                matches = re.findall(base64_pattern, content)
                for _ in matches:
                    image_count += 1
                    text_with_placeholders = re.sub(
                        base64_pattern, 
                        f"<|image_{image_count}|>", 
                        text_with_placeholders, 
                        count=1
                    )
                formatted_parts.append(text_with_placeholders)
        else:
            formatted_parts.append(content)
    
    return "\n".join(formatted_parts)

# --- 5. VLM ANALYSIS ENGINE ---

def analyze_with_vlm(image: Image.Image, prompt: str):
    """Analyzes the image using the pre-loaded Phi-3 Vision model with CPU compatibility."""
    if model is None or processor is None:
        raise HTTPException(status_code=500, detail="Model or processor is not available.")

    try:
        # Create messages for the model
        messages = [
            {"role": "user", "content": f"<|image_1|>\n{prompt}"},
        ]
        
        # Apply chat template
        prompt_for_model = processor.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        # Process inputs with CPU configuration
        inputs = processor(
            prompt_for_model, 
            [image], 
            return_tensors="pt"
        )
        
        # Move inputs to CPU
        inputs = {k: v.to(DEVICE) if isinstance(v, torch.Tensor) else v 
                 for k, v in inputs.items()}
        
        # Generation arguments optimized for CPU and cache compatibility
        generation_args = {
            "max_new_tokens": 150,  # Reduced for faster processing
            "do_sample": False,  # Use greedy decoding
            "pad_token_id": processor.tokenizer.eos_token_id,
            "eos_token_id": processor.tokenizer.eos_token_id,
            "use_cache": False,  # Disable cache to avoid DynamicCache issues
            "past_key_values": None,  # Explicitly set to None
        }
        
        print("Starting VLM inference on CPU...")
        start_time = time.time()
        
        # Generate with proper error handling and cache management
        with torch.no_grad():
            try:
                # Clear any existing cache
                if hasattr(model, 'config') and hasattr(model.config, 'use_cache'):
                    original_use_cache = model.config.use_cache
                    model.config.use_cache = False
                
                generate_ids = model.generate(
                    **inputs,
                    **generation_args
                )
                
                # Restore original cache setting
                if hasattr(model, 'config') and hasattr(model.config, 'use_cache'):
                    model.config.use_cache = original_use_cache
                    
            except RuntimeError as e:
                if "MPS" in str(e) or "Metal" in str(e):
                    print(f"MPS-related error detected, falling back to safer generation: {e}")
                    # Force all tensors to CPU and retry
                    inputs = {k: v.cpu() if isinstance(v, torch.Tensor) else v 
                             for k, v in inputs.items()}
                    model.cpu()
                    
                    # Retry with explicit cache disabling
                    if hasattr(model, 'config'):
                        model.config.use_cache = False
                    
                    generate_ids = model.generate(
                        **inputs,
                        **generation_args
                    )
                elif "DynamicCache" in str(e) or "get_max_length" in str(e):
                    print(f"Cache-related error detected, trying alternative generation: {e}")
                    # Try with minimal parameters
                    minimal_args = {
                        "max_new_tokens": 100,
                        "do_sample": False,
                        "pad_token_id": processor.tokenizer.eos_token_id,
                        "use_cache": False,
                    }
                    generate_ids = model.generate(
                        inputs['input_ids'],
                        pixel_values=inputs.get('pixel_values'),
                        image_sizes=inputs.get('image_sizes'),
                        **minimal_args
                    )
                else:
                    raise e
        
        end_time = time.time()
        print(f"VLM inference completed in {end_time - start_time:.2f} seconds")
        
        # Decode the response
        generate_ids = generate_ids[:, inputs['input_ids'].shape[1]:]
        response = processor.batch_decode(
            generate_ids, 
            skip_special_tokens=True, 
            clean_up_tokenization_spaces=False
        )[0]
        
        return response.strip()
        
    except Exception as e:
        print(f"Error during VLM analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze image with VLM: {str(e)}")

# --- 6. API ENDPOINTS ---

@app.get("/")
async def root():
    """Root endpoint to verify server is running."""
    return {
        "status": "AI Manual Assistant Backend (Phi-3) is running.",
        "model": MODEL_ID,
        "device": DEVICE,
        "timestamp": time.time()
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint for VLM analysis."""
    try:
        print(f"Received chat completion request with {len(request.messages)} messages")
        
        # Extract images from messages
        images = extract_base64_images(request.messages)
        
        if not images:
            raise HTTPException(status_code=400, detail="No image provided in the request")
        
        print(f"Extracted {len(images)} images from request")
        
        # Format prompt for Phi-3
        formatted_prompt = format_prompt_for_phi3(request.messages)
        print(f"Formatted prompt: {formatted_prompt[:100]}...")
        
        # Use the first image for analysis
        image = images[0]
        
        # Analyze with VLM
        start_time = time.time()
        analysis_result = analyze_with_vlm(image, formatted_prompt)
        end_time = time.time()
        
        print(f"Analysis completed in {end_time - start_time:.2f} seconds")
        print(f"Analysis result preview: {analysis_result[:100]}...")
        
        # Format response in OpenAI format
        response = ChatCompletionResponse(
            id=f"chatcmpl-{int(time.time())}",
            created=int(time.time()),
            model=request.model or "phi3_vision",
            choices=[
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": analysis_result
                    },
                    "finish_reason": "stop"
                }
            ],
            usage={
                "prompt_tokens": len(formatted_prompt.split()),
                "completion_tokens": len(analysis_result.split()),
                "total_tokens": len(formatted_prompt.split()) + len(analysis_result.split())
            }
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in chat completions: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """Legacy analyze endpoint for direct image upload."""
    try:
        # Read and process the uploaded image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Default prompt for analysis
        prompt = "Analyze what is happening in this image. Describe the objects, actions, and any relevant details you can observe."
        
        # Analyze with VLM
        result = analyze_with_vlm(image, prompt)
        
        return {
            "status": "success",
            "analysis": result,
            "timestamp": time.time()
        }
        
    except Exception as e:
        print(f"Error in analyze endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze image: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)