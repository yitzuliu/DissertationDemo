import cv2
from ultralytics import YOLO

# --- MODEL LOADING ---
# Load the YOLOv8 model. 'yolov8n.pt' is the smallest and fastest version.
# The first time you run this, it will be downloaded automatically.
model = YOLO('yolov8s.pt')

# --- WEBCAM INITIALIZATION ---
# Initialize a video capture object for the default webcam (index 0)
cap = cv2.VideoCapture(0)

# Check if the webcam is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open webcam")

# --- MAIN LOOP ---
# Loop to continuously get frames from the webcam
# --- MAIN LOOP (V2 - WITH DATA ACCESS) ---
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Send the frame to the model for prediction
    results = model(frame)

    # The result object contains all the detection information
    # We loop through each detected box in the first result (for the first image)
    for box in results[0].boxes:
        # Get the coordinates of the bounding box (x1, y1, x2, y2)
        coords = box.xyxy[0].tolist()
        
        # Get the class ID and the class name
        class_id = int(box.cls[0])
        class_name = model.names[class_id]
        
        # Get the confidence score
        confidence = float(box.conf[0])

        # Print the information to the console
        print(f"Detected: {class_name} with confidence {confidence:.2f} at {coords}")

    # --- For visualization, you can still display the frame ---
    annotated_frame = results[0].plot()
    cv2.imshow('AI Eye', annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- CLEANUP ---
# Release the webcam and destroy all OpenCV windows
cap.release()
cv2.destroyAllWindows()