# run_moondream2.py

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
import cv2
import json
import time

# --- 1. CONFIGURATION ---
# The official model identifier on Hugging Face for Moondream2
MODEL_ID = "vikhyatk/moondream2"

# Moondream2 is a bit unique; it uses a specific revision of the code
MODEL_REVISION = "2024-05-20"

# Automatically detect the best available device
if torch.backends.mps.is_available():
    DEVICE = "mps"
    print("Using Apple Metal (MPS) for GPU acceleration.")
elif torch.cuda.is_available():
    DEVICE = "cuda"
    print("Using NVIDIA CUDA for GPU acceleration.")
else:
    DEVICE = "cpu"
    print("Using CPU. This will be significantly slower.")

# Use bfloat16 for better performance, same as with Phi-3
TORCH_DTYPE = torch.bfloat16 if DEVICE != "cpu" else torch.float32

# --- 2. MODEL LOADING ---
print(f"Loading model '{MODEL_ID}' to device '{DEVICE}'. This should be faster than Phi-3.")
# Note: Moondream2 does not require `trust_remote_code=True`
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    trust_remote_code=True, # Moondream now requires this
    revision=MODEL_REVISION,
    torch_dtype=TORCH_DTYPE,
).to(DEVICE)

# Moondream uses a standard tokenizer, not a full "processor"
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
print("Model and tokenizer loaded successfully.")


# --- 3. THE CORE ANALYSIS FUNCTION ---
def analyze_frame(image: Image.Image, prompt: str):
    """
    This function takes a PIL Image and a text prompt, 
    and returns the structured analysis from Moondream2.
    """
    start_time = time.time()
    
    # Moondream2 has a simpler prompt structure.
    # It takes the image and processes it first.
    enc_image = model.encode_image(image)

    print("Generating response from Moondream2 model...")

    # The model's `answer_question` method is a convenient wrapper
    # It combines the image encoding and the text prompt for you.
    response = model.answer_question(
        enc_image,
        prompt,
        tokenizer
    )
    
    end_time = time.time()
    print(f"Analysis completed in {end_time - start_time:.2f} seconds.")
    
    return response


# --- 4. MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    # We use a simplified prompt for Moondream2. Because it's a smaller model,
    # being very direct and less conversational often yields better results.
    # We are still asking for JSON output.
    structured_prompt = """
    Analyze the image and describe the scene in JSON format with keys "primary_tool", "key_objects", and "user_action".
    """

    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    print(f"\nWebcam opened. Using model '{MODEL_ID}'.")
    print("Press 'c' to capture an image, or 'q' to quit.")

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
            
            # Convert the captured frame to a PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            # Call our analysis function
            analysis_text = analyze_frame(pil_image, structured_prompt)
            
            print("\n" + "="*20 + " AI ANALYSIS " + "="*20)
            print("Raw Response:")
            print(analysis_text)
            
            # Attempt to parse the JSON
            try:
                # Moondream is usually direct but let's be safe
                clean_text = analysis_text.strip().replace("```json", "").replace("```", "")
                parsed_json = json.loads(clean_text)
                print("\nParsed JSON:")
                print(json.dumps(parsed_json, indent=2))
            except json.JSONDecodeError:
                print("\n[Warning] The model's response was not a valid JSON object.")
            print("="*55)
            print("\nReady for next capture. Press 'c' to capture again, or 'q' to quit.")

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()