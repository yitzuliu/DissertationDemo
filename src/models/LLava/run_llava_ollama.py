# run_llava_ollama.py

import ollama
from PIL import Image
import cv2
import json
import time
import base64
from io import BytesIO

# --- 1. CONFIGURATION ---
# The model name must match what you pulled with `ollama pull`
MODEL_NAME = "llava:7b" 

# --- 2. THE CORE ANALYSIS FUNCTION ---
def analyze_frame(image_frame, prompt: str):
    """
    This function takes an OpenCV image frame and a text prompt,
    sends it to the Ollama LLaVA server, and returns the analysis.
    """
    start_time = time.time()

    # Convert the OpenCV frame (numpy array) to a byte stream
    _, buffer = cv2.imencode('.jpg', image_frame)
    image_bytes = buffer.tobytes()

    print("Generating response from LLaVA model...")

    # Call the Ollama chat API
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                'role': 'user',
                'content': prompt,
                'images': [image_bytes] # The image data is sent here
            }
        ]
    )
    
    end_time = time.time()
    print(f"Analysis completed in {end_time - start_time:.2f} seconds.")
    
    # Extract the text content from the response
    return response['message']['content']


# --- 3. MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    # This prompt is almost identical to the Phi-3 one to ensure a fair comparison.
    # We ask for a JSON object to get structured data.
    structured_prompt = """
    You are an expert AI assistant for a hands-on manual task. Analyze the user's workspace in the image.
    Respond ONLY with a valid JSON object. Do not include any other text, explanations, or markdown formatting.
    The JSON object should have the following keys:
    - "primary_tool": Identify the main tool the user is holding or using. If none, say "None".
    - "key_objects": A list of up to 3 important objects on the workspace.
    - "user_action": A short, descriptive sentence of what the user is currently doing.
    """

    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    print(f"\nWebcam opened. Using model '{MODEL_NAME}'.")
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
            
            # The frame is passed directly to the analysis function
            analysis_text = analyze_frame(frame, structured_prompt)
            
            print("\n" + "="*20 + " AI ANALYSIS " + "="*20)
            print("Raw Response:")
            print(analysis_text)
            
            # Attempt to parse the JSON for clean output
            try:
                # LLaVA sometimes wraps its response in markdown, so we clean it.
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