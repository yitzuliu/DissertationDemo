#!/usr/bin/env python3
"""
Backend Test Script
Test the backend server functionality without actually starting the server.
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

def test_backend():
    """Test backend functionality"""
    print("🧪 Testing AI Manual Assistant Backend...")
    print("=" * 50)
    
    try:
        # Test imports
        print("1. Testing imports...")
        import main
        from utils.config_manager import config_manager
        from utils.image_processing import convert_to_pil_image
        print("   ✅ All imports successful")
        
        # Test configuration
        print("\n2. Testing configuration...")
        active_model = config_manager.get_active_model()
        model_config = config_manager.get_active_model_config()
        print(f"   ✅ Active model: {active_model}")
        print(f"   ✅ Model name: {model_config.get('model_name', 'Unknown')}")
        
        # Test FastAPI app
        print("\n3. Testing FastAPI app...")
        app = main.app
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        print(f"   ✅ App created with {len(routes)} routes")
        
        # Test model server URL
        print("\n4. Testing model server URL...")
        model_server_url = main.MODEL_SERVER_URL
        print(f"   ✅ Model server URL: {model_server_url}")
        
        # Test image processing
        print("\n5. Testing image processing...")
        from PIL import Image
        test_image = Image.new('RGB', (100, 100), color='red')
        processed = convert_to_pil_image(test_image)
        print("   ✅ Image processing works")
        
        # Test message formatting
        print("\n6. Testing message formatting...")
        test_message = {
            'content': [
                {'type': 'text', 'text': 'Test message'},
                {'type': 'image_url', 'image_url': {'url': 'test'}}
            ]
        }
        formatted = main.format_message_for_model(test_message, 1, active_model)
        print("   ✅ Message formatting works")
        
        print("\n" + "=" * 50)
        print("🎉 All backend tests passed!")
        print("\n📋 Backend is ready to start:")
        print("   python src/backend/main.py")
        print("\n🌐 Expected endpoints:")
        for route in sorted(routes):
            if route != '/openapi.json' and route != '/docs' and route != '/redoc':
                print(f"   http://localhost:8000{route}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Backend test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1)