import time
import cv2
import base64
from flask import Flask, render_template
from flask_socketio import SocketIO
from ultralytics import YOLO
import threading

# Initialize the Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Load the YOLOv8 model
model = YOLO('yolov8n.pt')

# Initialize the webcam
cap = cv2.VideoCapture(0)

# --- Background Thread for Video Streaming ---
def generate_frames():
    """
    This function runs in a background thread to continuously 
    process frames from the webcam and send them to the client.
    """
    while True:
        # Read a frame from the webcam
        success, frame = cap.read()
        if not success:
            break
        
        # Run YOLOv8 inference on the frame
        results = model(frame)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        if not ret:
            continue
            
        # Convert the buffer to a base64 string
        frame_b64 = base64.b64encode(buffer).decode('utf-8')

        # Emit the frame to the connected clients
        # The 'video_frame' event can be caught by our JavaScript client
        socketio.emit('video_frame', {'image': frame_b64})
        
        # A small sleep to manage CPU usage and frame rate
        time.sleep(0.01)

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """
    This function is called when a client connects to the server.
    We start the background thread for video streaming here.
    """
    print('Client connected')
    # Start the frame generation in a background thread
    # This prevents the main server thread from being blocked
    threading.Thread(target=generate_frames, daemon=True).start()

# --- Main execution block ---
if __name__ in '__main__':
    # We use socketio.run() instead of app.run()
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
