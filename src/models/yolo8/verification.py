import cv2
from ultralytics import YOLO
import requests
import base64
import json
import numpy as np

# --- MODEL LOADING ---
model = YOLO('yolov8s.pt')  # Better model

# --- SMOLVLM VERIFICATION SETTINGS ---
SMOLVLM_SERVER = "http://localhost:8080"  # SmolVLM server URL
VERIFY_LOW_CONFIDENCE = True  # Verify detections with confidence < 0.8
MIN_CONFIDENCE = 0.5  # Lower threshold since we'll verify

# --- VERIFICATION FUNCTIONS ---
def crop_object(frame, bbox, padding=20):
    """Crop object from frame with some padding"""
    x1, y1, x2, y2 = [int(coord) for coord in bbox]
    h, w = frame.shape[:2]
    
    # Add padding
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(w, x2 + padding)
    y2 = min(h, y2 + padding)
    
    return frame[y1:y2, x1:x2]

def verify_with_smolvlm(cropped_image, yolo_classification):
    """Use SmolVLM to verify YOLO classification"""
    try:
        # Convert image to base64
        _, buffer = cv2.imencode('.jpg', cropped_image)
        image_b64 = base64.b64encode(buffer).decode('utf-8')
        
        prompt = f"""
        YOLO detected this as: "{yolo_classification}"
        
        Look at this object carefully and answer:
        1. What is this object exactly?
        2. Is YOLO's classification of "{yolo_classification}" correct?
        3. If incorrect, what should it be called?
        
        Give a brief, clear answer.
        """
        
        # Prepare request for SmolVLM
        payload = {
            "prompt": prompt,
            "stream": False,
            "temperature": 0.1,
            "n_predict": 100
        }
        
        files = {
            'image_data': ('image.jpg', base64.b64decode(image_b64), 'image/jpeg')
        }
        
        # Send to SmolVLM server
        response = requests.post(
            f"{SMOLVLM_SERVER}/completion",
            data=json.dumps(payload),
            files=files,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            verification_text = result.get('content', '')
            return verification_text
        else:
            return f"Verification failed: {response.status_code}"
            
    except Exception as e:
        return f"Verification error: {str(e)}"

def extract_corrected_classification(verification_text, original_classification):
    """Extract corrected classification from SmolVLM response"""
    verification_lower = verification_text.lower()
    
    # Simple keyword matching for common corrections
    corrections = {
        'pencil': ['pencil', 'pen', 'writing'],
        'remote control': ['remote', 'controller', 'remote control'],
        'toothbrush': ['toothbrush', 'brush'],
        'knife': ['knife', 'blade'],
        'spoon': ['spoon', 'utensil'],
        'fork': ['fork'],
        'cup': ['cup', 'mug', 'glass'],
        'bottle': ['bottle', 'container'],
        'phone': ['phone', 'mobile', 'smartphone'],
        'laptop': ['laptop', 'computer'],
        'mouse': ['mouse', 'computer mouse'],
        'keyboard': ['keyboard'],
        'book': ['book', 'notebook'],
        'scissors': ['scissors'],
        'clock': ['clock', 'watch']
    }
    
    # Check if verification suggests a different object
    for correct_class, keywords in corrections.items():
        for keyword in keywords:
            if keyword in verification_lower:
                return correct_class
    
    # If no clear correction found, return original
    return original_classification

# --- WEBCAM INITIALIZATION ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Cannot open webcam")

print("Starting YOLO8 with SmolVLM verification...")
print("- YOLO8s for detection")
print("- SmolVLM verification for low confidence detections")
print("- Press 'q' to quit")

# --- MAIN LOOP ---
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO detection
    results = model(frame)
    
    verified_detections = []
    
    for box in results[0].boxes:
        coords = box.xyxy[0].tolist()
        class_id = int(box.cls[0])
        class_name = model.names[class_id]
        confidence = float(box.conf[0])
        
        # Only process detections above minimum confidence
        if confidence >= MIN_CONFIDENCE:
            # Calculate area to filter tiny detections
            width = coords[2] - coords[0]
            height = coords[3] - coords[1]
            area = width * height
            
            if area >= 1000:  # Minimum area threshold
                verification_status = "YOLO"
                corrected_name = class_name
                
                # Verify low-confidence detections with SmolVLM
                if VERIFY_LOW_CONFIDENCE and confidence < 0.8:
                    print(f"\nVerifying low-confidence detection: {class_name} ({confidence:.2f})")
                    
                    # Crop the object
                    cropped = crop_object(frame, coords)
                    
                    # Verify with SmolVLM
                    verification = verify_with_smolvlm(cropped, class_name)
                    corrected_name = extract_corrected_classification(verification, class_name)
                    
                    if corrected_name != class_name:
                        verification_status = "CORRECTED"
                        print(f"SmolVLM correction: {class_name} → {corrected_name}")
                    else:
                        verification_status = "VERIFIED"
                
                verified_detections.append({
                    'bbox': coords,
                    'original_class': class_name,
                    'final_class': corrected_name,
                    'confidence': confidence,
                    'status': verification_status
                })
    
    # Print results
    for det in verified_detections:
        status_marker = f" [{det['status']}]"
        if det['status'] == "CORRECTED":
            print(f"Detected: {det['final_class']} "
                  f"(was: {det['original_class']}, "
                  f"confidence: {det['confidence']:.2f}){status_marker}")
        else:
            print(f"Detected: {det['final_class']} "
                  f"(confidence: {det['confidence']:.2f}){status_marker}")
    
    # Visualize
    annotated_frame = results[0].plot()
    
    # Add verification status to visualization
    for det in verified_detections:
        x1, y1, x2, y2 = [int(coord) for coord in det['bbox']]
        
        # Color based on verification status
        color = {
            'YOLO': (255, 255, 0),      # Yellow - YOLO only
            'VERIFIED': (0, 255, 0),    # Green - SmolVLM verified
            'CORRECTED': (0, 0, 255)    # Red - SmolVLM corrected
        }.get(det['status'], (255, 255, 255))
        
        # Draw custom rectangle and label
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
        
        label = f"{det['final_class']} {det['confidence']:.2f} [{det['status']}]"
        cv2.putText(annotated_frame, label, (x1, y1-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    cv2.imshow('YOLO + SmolVLM Verification', annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- CLEANUP ---
cap.release()
cv2.destroyAllWindows() 