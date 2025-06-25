# run_phi3_vision.py

import torch
from transformers import AutoModelForCausalLM, AutoProcessor, AutoConfig
from PIL import Image
import cv2
import json
import time

# --- 1. CONFIGURATION ---
# The official model identifier on Hugging Face
MODEL_ID = "microsoft/Phi-3-vision-128k-instruct"

# Automatically detect the best available device for computation
# This is crucial for performance on a MacBook Air with an M1/M2/M3 chip
if torch.backends.mps.is_available():
    DEVICE = "mps"
    print("Using Apple Metal (MPS) for GPU acceleration.")
elif torch.cuda.is_available():
    DEVICE = "cuda"
    print("Using NVIDIA CUDA for GPU acceleration.")
else:
    DEVICE = "cpu"
    print("Using CPU. This will be significantly slower.")

# We use bfloat16 for better performance on modern GPUs/MPUs
# It uses less memory than float32 with minimal precision loss
TORCH_DTYPE = torch.bfloat16 if DEVICE != "cpu" else torch.float32


# --- 2. MODEL LOADING ---
print(f"Loading model '{MODEL_ID}' to device '{DEVICE}'. This may take several minutes...")

# Load config and disable FlashAttention2 for Apple Silicon compatibility
print("Loading and modifying config to disable FlashAttention2...")
config = AutoConfig.from_pretrained(MODEL_ID, trust_remote_code=True)
config._attn_implementation = "eager"
if hasattr(config, "use_flash_attention_2"):
    config.use_flash_attention_2 = False

# device_map=DEVICE ensures the model is loaded onto the correct hardware (e.g., your Mac's GPU)
# `trust_remote_code=True` is required as this model has custom code.
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID, 
    config=config,
    device_map=DEVICE, 
    trust_remote_code=True, 
    torch_dtype=TORCH_DTYPE,
    attn_implementation="eager"
)

# The processor handles both text tokenization and image pre-processing
processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
print("Model and processor loaded successfully.")


# --- 3. THE CORE ANALYSIS FUNCTION ---
def analyze_frame(image: Image.Image, prompt: str):
    """
    This function takes a PIL Image and a text prompt, 
    and returns the structured analysis from Phi-3 Vision.
    """
    start_time = time.time()
    
    # The prompt format for Phi-3 is specific. It uses a chat-like structure.
    # The `<|image_1|>` token is a special placeholder where the processor will insert the image data.
    messages = [
        {"role": "user", "content": f"<|image_1|>\n{prompt}"},
    ]

    # Use the processor to format the entire input
    prompt_for_model = processor.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(prompt_for_model, [image], return_tensors="pt").to(DEVICE)

    # Generation arguments control how the model creates the output text
    generation_args = {
        "max_new_tokens": 500,  # Max length of the response
        "temperature": 0.0,     # 0.0 means deterministic output (no randomness)
        "do_sample": False,     # Disables random sampling, used with temperature=0.0
    }

    print("Generating response from model...")
    # Generate an output sequence of token IDs
    generate_ids = model.generate(**inputs, eos_token_id=processor.tokenizer.eos_token_id, **generation_args)

    # Decode the generated IDs, skipping the input prompt part
    generate_ids = generate_ids[:, inputs['input_ids'].shape[1]:]
    response = processor.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    
    end_time = time.time()
    print(f"Analysis completed in {end_time - start_time:.2f} seconds.")
    
    return response


# --- 4. MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    # This is our carefully crafted prompt to guide the AI.
    # Asking for JSON output is a key technique called "Prompt Engineering".
    structured_prompt = """
    You are an expert AI assistant for a hands-on manual task. Analyze the user's workspace in the image.
    Respond ONLY with a valid JSON object. Do not include any other text or explanations.
    The JSON object should have the following keys:
    - "primary_tool": Identify the main tool the user is holding or using. If none, say "None".
    - "key_objects": A list of up to 3 important objects on the workspace.
    - "user_action": A short, descriptive sentence of what the user is currently doing.
    - "is_safe": A boolean (true/false) indicating if the scene looks safe.
    """

    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    print("\nWebcam opened. Press 'c' to capture an image, or 'q' to quit.")

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        # Display the resulting frame
        cv2.imshow('Webcam - Press "c" to capture, "q" to quit', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            print("\nImage captured! Starting analysis...")
            
            # Convert the captured frame (OpenCV BGR format) to a PIL Image (RGB format)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            # Call our analysis function
            analysis_text = analyze_frame(pil_image, structured_prompt)
            
            print("\n" + "="*20 + " AI ANALYSIS " + "="*20)
            print("Raw Response:")
            print(analysis_text)
            
            # Attempt to parse the JSON for clean output
            try:
                # Clean up potential markdown formatting from the model
                clean_text = analysis_text.strip().replace("```json", "").replace("```", "")
                parsed_json = json.loads(clean_text)
                print("\nParsed JSON:")
                # Pretty print the JSON
                print(json.dumps(parsed_json, indent=2))
            except json.JSONDecodeError:
                print("\n[Warning] The model's response was not a valid JSON object.")
            print("="*55)
            print("\nReady for next capture. Press 'c' to capture again, or 'q' to quit.")

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()