import base64
import io
import json
import time
from pathlib import Path
import sys
from flask import Flask, request, jsonify
from PIL import Image

# Add project root to path for module imports
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from src.models.llava_mlx.llava_mlx_model import LlavaMlxModel

app = Flask(__name__)

def load_config():
    """Load LLaVA MLX configuration"""
    try:
        config_path = project_root / "src/config/model_configs/llava_mlx.json"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found at {config_path}")
            
        with open(config_path, 'r') as f:
            return json.load(f)
            
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return {}

# Load configuration and initialize the model
config = load_config()
model = None
if config:
    try:
        print("Initializing LLaVA MLX model...")
        model = LlavaMlxModel(model_name=config.get("model_name", "LLaVA-MLX-Default"), config=config)
        model.load_model()
        print("LLaVA MLX model ready.")
    except Exception as e:
        print(f"FATAL: Could not load model. {e}")
        model = None

@app.route('/health', methods=['GET'])
def health_check():
    if model and model.loaded:
        return jsonify({"status": "healthy", "model": model.model_name}), 200
    else:
        return jsonify({"status": "unhealthy", "error": "Model not loaded"}), 500

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    if not model:
        return jsonify({"error": "Model is not available"}), 503

    data = request.get_json()
    if not data or "messages" not in data:
        return jsonify({"error": "Invalid request body, 'messages' is required."}), 400

    try:
        # Extract image and prompt from the message
        image, prompt = model.process_messages(data["messages"])
        
        # Generate a response
        response_text = model.generate_response(image, prompt)
        
        # Format the response in OpenAI-compatible format
        response = {
            "id": f"chatcmpl-{model.model_name.lower()}-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model.model_name,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text,
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
        return jsonify(response), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

if __name__ == '__main__':
    server_config = config.get("server_config", {})
    host = server_config.get("host", "0.0.0.0")
    port = server_config.get("port", 8080)
    print(f"Starting LLaVA MLX server on http://{host}:{port}")
    app.run(host=host, port=port) 