#!/usr/bin/env python3
"""
Phi-3 Vision Server Launcher
Launch Phi-3 Vision model server (powered by vLLM)
Supports multiple model variants and flexible configuration
"""

import subprocess
import sys
import time
import signal
import os
import argparse
import json
import traceback

# Available Phi-3 Vision models
AVAILABLE_MODELS = {
    "phi3": "microsoft/Phi-3-vision-128k-instruct",
    "phi3.5": "microsoft/Phi-3.5-vision-instruct", 
    "phi3-128k": "microsoft/Phi-3-vision-128k-instruct",
    "phi3.5-instruct": "microsoft/Phi-3.5-vision-instruct"
}

class Phi3VisionServer:
    def __init__(self, model_variant="phi3"):
        self.process = None
        self.model_variant = model_variant
        self.model_name = AVAILABLE_MODELS.get(model_variant, AVAILABLE_MODELS["phi3"])
        self.port = int(os.getenv('PHI3_PORT', '8080'))
        self.gpu_memory = float(os.getenv('PHI3_GPU_MEMORY', '0.8'))
        
        # CPU memory optimization settings
        self.cpu_kv_cache_space = int(os.getenv('VLLM_CPU_KVCACHE_SPACE', '8'))  # 8GB for KV cache
        self.max_model_len = int(os.getenv('PHI3_MAX_MODEL_LEN', '8192'))  # Reduced from 131072
        
    def get_model_info(self):
        """Get model information"""
        if "3.5" in self.model_name:
            return {
                "version": "Phi-3.5 Vision",
                "release": "August 2024",
                "features": ["Enhanced multi-image", "Improved video understanding", "Better reasoning"]
            }
        else:
            return {
                "version": "Phi-3 Vision",
                "release": "April 2024", 
                "features": ["128K context", "Multi-modal", "OCR capabilities"]
            }
        
    def start_server(self):
        """Start Phi-3 Vision server"""
        # Set environment variables for CPU optimization
        os.environ['VLLM_CPU_KVCACHE_SPACE'] = str(self.cpu_kv_cache_space)
        
        cmd = [
            sys.executable, "-m", "vllm.entrypoints.openai.api_server",
            "--model", self.model_name,
            "--trust-remote-code",
            "--port", str(self.port),
            "--gpu-memory-utilization", str(self.gpu_memory),
            "--max-model-len", str(self.max_model_len),  # Limit context length for memory efficiency
            "--dtype", "float16",  # Use float16 for memory efficiency
            "--enforce-eager",  # Disable CUDA graphs for CPU compatibility
        ]
        
        # Add CPU-specific optimizations
        if not os.getenv('CUDA_VISIBLE_DEVICES'):
            cmd.extend([
                "--device", "cpu",
            ])
        
        model_info = self.get_model_info()
        
        print("🚀 Starting Phi-3 Vision server...")
        print(f"📦 Model: {self.model_name}")
        print(f"🏷️  Variant: {self.model_variant}")
        print(f"📅 Version: {model_info['version']} ({model_info['release']})")
        print(f"🌐 Port: {self.port}")
        print(f"💾 GPU Memory: {self.gpu_memory}")
        print(f"🧠 CPU KV Cache: {self.cpu_kv_cache_space}GB")
        print(f"📏 Max Model Length: {self.max_model_len} tokens")
        print(f"⭐ Features: {', '.join(model_info['features'])}")
        print(f"⚡ Engine: vLLM")
        print(f"💻 Command: {' '.join(cmd)}")
        print("-" * 60)

        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, 'model_server.log')

        print(f"📝 Logging server output to: {log_file_path}\n")

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                encoding='utf-8',
                errors='replace'
            )

            # Monitor output and write to log file
            if self.process.stdout:
                with open(log_file_path, 'w', encoding='utf-8') as log_file:
                    for line in iter(self.process.stdout.readline, ''):
                        print(line.rstrip())
                        log_file.write(line)

                        # Check if server started successfully
                        if ("Uvicorn running" in line or
                            "server listening" in line or
                            "Application startup complete" in line):
                            success_message = (
                                f"\n✅ Phi-3 Vision server running at http://localhost:{self.port}\n"
                                "📡 API endpoint: /v1/chat/completions\n"
                                "🔍 Health check: /health\n"
                                "📖 API docs: /docs\n"
                                "🛑 Press Ctrl+C to stop server\n"
                            )
                            print(success_message)
                            log_file.write(success_message)

        except FileNotFoundError:
            print("❌ Error: vLLM not found")
            print("Please ensure vLLM is properly installed:")
            print("  pip install vllm")
            return False
        except KeyboardInterrupt:
            print("\n🛑 Received stop signal...")
            self.stop_server()
            return True
        except Exception as e:
            print(f"❌ An unexpected error occurred during server startup: {e}")
            print("="*60)
            print("Full Traceback:")
            traceback.print_exc()
            print("="*60)
            return False
            
    def stop_server(self):
        """Stop server"""
        if self.process:
            print("🔄 Stopping Phi-3 Vision server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
                print("✅ Phi-3 Vision server stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Force stopping server...")
                self.process.kill()
                self.process.wait()
                print("✅ Phi-3 Vision server force stopped")

def signal_handler(signum, frame):
    """Handle system signals"""
    print("\n🛑 Received stop signal, shutting down server...")
    sys.exit(0)

def list_models():
    """List available models"""
    print("🎯 Available Phi-3 Vision Models:")
    print("=" * 50)
    for variant, model_path in AVAILABLE_MODELS.items():
        print(f"📦 {variant:15} → {model_path}")
    print("\nUsage examples:")
    print("  python start_server.py --model phi3")
    print("  python start_server.py --model phi3.5")
    print("  PHI3_MODEL=phi3.5 python start_server.py")
    print("\nMemory optimization:")
    print("  VLLM_CPU_KVCACHE_SPACE=16 python start_server.py  # Use 16GB for KV cache")
    print("  PHI3_MAX_MODEL_LEN=4096 python start_server.py    # Reduce context length")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Phi-3 Vision Server Launcher")
    parser.add_argument(
        "--model", "-m",
        choices=list(AVAILABLE_MODELS.keys()),
        default=os.getenv('PHI3_MODEL', 'phi3'),
        help="Model variant to use (default: phi3)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=int(os.getenv('PHI3_PORT', '8080')),
        help="Server port (default: 8080)"
    )
    parser.add_argument(
        "--gpu-memory",
        type=float,
        default=float(os.getenv('PHI3_GPU_MEMORY', '0.8')),
        help="GPU memory utilization (default: 0.8)"
    )
    parser.add_argument(
        "--cpu-kv-cache",
        type=int,
        default=int(os.getenv('VLLM_CPU_KVCACHE_SPACE', '8')),
        help="CPU KV cache space in GB (default: 8)"
    )
    parser.add_argument(
        "--max-model-len",
        type=int,
        default=int(os.getenv('PHI3_MAX_MODEL_LEN', '8192')),
        help="Maximum model length in tokens (default: 8192)"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available models"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_models()
        return
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Override with command line arguments
    os.environ['PHI3_PORT'] = str(args.port)
    os.environ['PHI3_GPU_MEMORY'] = str(args.gpu_memory)
    os.environ['VLLM_CPU_KVCACHE_SPACE'] = str(args.cpu_kv_cache)
    os.environ['PHI3_MAX_MODEL_LEN'] = str(args.max_model_len)
    
    print("🎯 Phi-3 Vision Server Launcher")
    print("=" * 60)
    print("🔧 Technical Specifications:")
    print("   - Model size: 4.2B parameters")
    print("   - Multimodal: Image + Text support")
    print(f"   - Context: {args.max_model_len} tokens (optimized for memory)")
    print("   - Inference engine: vLLM (CPU-optimized)")
    print("   - Image processing: 336x336 resize")
    print(f"   - CPU KV Cache: {args.cpu_kv_cache}GB")
    print("=" * 60)
    
    server = Phi3VisionServer(model_variant=args.model)
    server.cpu_kv_cache_space = args.cpu_kv_cache
    server.max_model_len = args.max_model_len
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        server.stop_server()
    except Exception as e:
        print(f"❌ A critical error occurred in the main application: {e}")
        print("="*60)
        print("Full Traceback:")
        traceback.print_exc()
        print("="*60)
    finally:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()