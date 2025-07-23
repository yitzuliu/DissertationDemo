#!/usr/bin/env python3
"""
Unified Model Launcher

This script provides a unified interface for launching and managing all VLM models.

Usage:
python src/models/model_launcher_en.py --model smolvlm2_500m_video_optimized
python src/models/model_launcher_en.py --model moondream2_optimized --port 8081
python src/models/model_launcher_en.py --list  # List all available models
"""

import argparse
import sys
import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
import time

class ModelLauncher:
    """Unified Model Launcher"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.models_dir = self.project_root / "src" / "models"
        self.config_dir = self.project_root / "src" / "config"
        
        # Model launch mapping table - now using unified server
        self.model_runners = {
            "smolvlm2_500m_video_optimized": {
                "script": "src/models/unified_model_server.py",
                "description": "SmolVLM2-500M-Video Optimized (Recommended)",
                "status": "✅ Unified Launch",
                "model_arg": "smolvlm2_500m_video_optimized"
            },
            "smolvlm2_500m_video": {
                "script": "src/models/unified_model_server.py",
                "description": "SmolVLM2-500M-Video Standard",
                "status": "✅ Unified Launch",
                "model_arg": "smolvlm2_500m_video"
            },
            "moondream2_optimized": {
                "script": "src/models/unified_model_server.py",
                "description": "Moondream2 Optimized (Fastest Speed)",
                "status": "✅ Unified Launch",
                "model_arg": "moondream2_optimized"
            },
            "moondream2": {
                "script": "src/models/unified_model_server.py",
                "description": "Moondream2 Standard",
                "status": "✅ Unified Launch",
                "model_arg": "moondream2"
            },
            "phi3_vision_optimized": {
                "script": "src/models/unified_model_server.py",
                "description": "Phi-3.5-Vision MLX Optimized",
                "status": "✅ Unified Launch",
                "model_arg": "phi3_vision_optimized"
            },
            "phi3_vision": {
                "script": "src/models/unified_model_server.py",
                "description": "Phi-3.5-Vision MLX Standard",
                "status": "✅ Unified Launch",
                "model_arg": "phi3_vision"
            },
            "llava_mlx": {
                "script": "src/models/unified_model_server.py",
                "description": "LLaVA MLX Version",
                "status": "⚠️ Performance Issues",
                "model_arg": "llava_mlx"
            },
            "smolvlm": {
                "script": "src/models/unified_model_server.py",
                "description": "SmolVLM Standard (Default)",
                "status": "✅ Unified Launch",
                "model_arg": "smolvlm"
            }
        }
    
    def list_models(self):
        """List all available models"""
        print("🤖 Available Vision-Language Models:")
        print("=" * 80)
        
        for model_id, info in self.model_runners.items():
            script_path = self.project_root / info["script"]
            exists = "✅" if script_path.exists() else "❌"
            
            print(f"{exists} {model_id}")
            print(f"   Description: {info['description']}")
            print(f"   Status: {info['status']}")
            print(f"   Script: {info['script']}")
            print()
        
        print("🚀 Recommended Usage:")
        print("   • Best Performance: smolvlm2_500m_video_optimized")
        print("   • Fastest Speed: moondream2_optimized")
        print("   • Detailed Analysis: phi3_vision_optimized")
        print("   • Default Model: smolvlm")
    
    def check_model_config(self, model_id: str) -> Optional[Dict]:
        """Check model configuration"""
        config_path = self.config_dir / "model_configs" / f"{model_id}.json"
        
        if not config_path.exists():
            print(f"⚠️ Configuration file not found: {config_path}")
            return None
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"❌ Failed to read configuration file: {e}")
            return None
    
    def check_dependencies(self, model_id: str) -> bool:
        """Check model dependencies"""
        print(f"🔍 Checking dependencies for {model_id}...")
        
        # Basic dependency check
        required_packages = {
            "torch": "PyTorch",
            "transformers": "Transformers",
            "PIL": "Pillow",
            "flask": "Flask"
        }
        
        missing_packages = []
        for package, name in required_packages.items():
            try:
                __import__(package)
                print(f"   ✅ {name}")
            except ImportError:
                missing_packages.append(name)
                print(f"   ❌ {name} (missing)")
        
        # MLX special check
        if "mlx" in model_id.lower():
            try:
                import mlx_vlm
                print("   ✅ MLX-VLM")
            except ImportError:
                missing_packages.append("MLX-VLM")
                print("   ❌ MLX-VLM (missing)")
        
        if missing_packages:
            print(f"❌ Missing dependencies: {', '.join(missing_packages)}")
            print("Please run: pip install -r requirements.txt")
            return False
        
        print("✅ All dependencies satisfied")
        return True
    
    def launch_model(self, model_id: str, port: int = 8080, host: str = "0.0.0.0", 
                    check_deps: bool = True) -> bool:
        """Launch specified model"""
        
        if model_id not in self.model_runners:
            print(f"❌ Unknown model: {model_id}")
            print("Use --list to see available models")
            return False
        
        model_info = self.model_runners[model_id]
        script_path = self.project_root / model_info["script"]
        
        if not script_path.exists():
            print(f"❌ Launch script not found: {script_path}")
            return False
        
        # Check configuration
        config = self.check_model_config(model_id)
        if not config:
            print("⚠️ Configuration check failed, but continuing launch...")
        
        # Check dependencies
        if check_deps and not self.check_dependencies(model_id):
            return False
        
        print(f"🚀 Launching model: {model_id}")
        print(f"   Description: {model_info['description']}")
        print(f"   Port: {port}")
        print(f"   Host: {host}")
        print(f"   Script: {script_path}")
        print()
        
        # Set environment variables
        env = os.environ.copy()
        env["MODEL_PORT"] = str(port)
        env["MODEL_HOST"] = host
        
        try:
            # Launch model server - using unified server
            print("⏳ Starting unified model server...")
            model_arg = model_info.get("model_arg", model_id)
            cmd = [
                sys.executable, str(script_path),
                "--model", model_arg,
                "--port", str(port),
                "--host", host
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=str(self.project_root),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitor startup process
            startup_timeout = 60  # 60 second timeout
            start_time = time.time()
            
            while True:
                if process.poll() is not None:
                    # Process has ended
                    print(f"❌ Model launch failed, exit code: {process.returncode}")
                    return False
                
                if time.time() - start_time > startup_timeout:
                    print("❌ Launch timeout")
                    process.terminate()
                    return False
                
                # Check if startup successful (simple port check)
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex((host, port))
                    sock.close()
                    
                    if result == 0:
                        print(f"✅ Model server launched successfully!")
                        print(f"🌐 Service URL: http://{host}:{port}")
                        print(f"🔍 Health check: http://{host}:{port}/health")
                        print(f"📡 API endpoint: http://{host}:{port}/v1/chat/completions")
                        print()
                        print("Press Ctrl+C to stop server")
                        
                        # Keep process running
                        try:
                            process.wait()
                        except KeyboardInterrupt:
                            print("\\n🛑 Stopping server...")
                            process.terminate()
                            process.wait()
                            print("✅ Server stopped")
                        
                        return True
                        
                except ImportError:
                    # If no socket module, wait longer
                    time.sleep(5)
                    print(f"✅ Model server should be started")
                    print(f"🌐 Service URL: http://{host}:{port}")
                    return True
                
                time.sleep(1)
                
        except Exception as e:
            print(f"❌ Launch failed: {e}")
            return False
    
    def get_default_model(self) -> str:
        """Get default model (smolvlm)"""
        print("🔍 Using default model...")
        print("🎯 Default model: smolvlm")
        return "smolvlm"
    
    def get_model_status(self, model_id: str) -> Dict:
        """Get model status"""
        if model_id not in self.model_runners:
            return {"status": "unknown", "message": "Model not found"}
        
        model_info = self.model_runners[model_id]
        script_path = self.project_root / model_info["script"]
        
        status = {
            "model_id": model_id,
            "description": model_info["description"],
            "script_exists": script_path.exists(),
            "script_path": str(script_path),
            "config_exists": False,
            "dependencies_ok": False
        }
        
        # Check configuration
        config = self.check_model_config(model_id)
        status["config_exists"] = config is not None
        
        # Check dependencies (silent mode)
        status["dependencies_ok"] = self.check_dependencies(model_id)
        
        return status

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="AI Manual Assistant - Unified Model Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Examples:
  python src/models/model_launcher_en.py --list
  python src/models/model_launcher_en.py --model smolvlm
  python src/models/model_launcher_en.py --model moondream2_optimized --port 8081
  python src/models/model_launcher_en.py --status smolvlm
        """
    )
    
    parser.add_argument('--model', '-m', help='Model name to launch')
    parser.add_argument('--port', '-p', type=int, default=8080, help='Server port (default: 8080)')
    parser.add_argument('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    parser.add_argument('--list', '-l', action='store_true', help='List all available models')
    parser.add_argument('--status', '-s', help='Check specified model status')
    parser.add_argument('--no-deps-check', action='store_true', help='Skip dependency check')
    
    args = parser.parse_args()
    
    launcher = ModelLauncher()
    
    if args.list:
        launcher.list_models()
        return
    
    if args.status:
        status = launcher.get_model_status(args.status)
        print(f"📊 Model Status: {args.status}")
        print("=" * 50)
        for key, value in status.items():
            print(f"{key}: {value}")
        return
    
    if not args.model:
        # Smart default model selection
        default_model = launcher.get_default_model()
        print("🤖 No model specified, using default model")
        print(f"📋 Default model: {default_model}")
        print("💡 Tip: Use --list to see all available models")
        print("⏳ Auto-launching in 3 seconds, press Ctrl+C to cancel...")
        
        try:
            time.sleep(3)
            args.model = default_model
        except KeyboardInterrupt:
            print("\n👋 Launch cancelled")
            sys.exit(0)
    
    success = launcher.launch_model(
        args.model, 
        port=args.port, 
        host=args.host,
        check_deps=not args.no_deps_check
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()