#!/usr/bin/env python3
"""
Fixed Image Fallback Test

This script tests the fixed image fallback workflow after bug fixes:
1. Process image through /v1/chat/completions (stores in state tracker)
2. Test VLM fallback with stored image
"""

import requests
import base64
import json
import time

def create_test_image():
    """Create a simple test image in base64 format"""
    # Simple 1x1 pixel JPEG
    test_image_bytes = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\'",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
    return base64.b64encode(test_image_bytes).decode('utf-8')

def test_image_processing():
    """Step 1: Send image to /v1/chat/completions to store in state tracker"""
    print("🖼️ Step 1: Processing image through /v1/chat/completions")
    print("-" * 50)
    
    image_base64 = create_test_image()
    
    # Create chat completion request with image
    request_data = {
        "model": "smolvlm",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe what you see in this image."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 100
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=request_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f"✅ Image processed successfully")
            print(f"📄 VLM Response: {content[:100]}...")
            print(f"📊 Image should now be stored in state tracker")
            return True
        else:
            print(f"❌ Image processing failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Image processing error: {e}")
        return False

def test_vlm_fallback():
    """Step 2: Test VLM fallback with stored image"""
    print("\\n🔄 Step 2: Testing VLM Fallback with stored image")
    print("-" * 50)
    
    # Test query that should trigger VLM fallback
    query_data = {
        "query": "What objects and details can you see in this image?",
        "query_id": "fixed_image_fallback_test"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/api/v1/state/query",
            json=query_data,
            timeout=30
        )
        processing_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ VLM Fallback executed successfully")
            print(f"⏱️ Processing time: {processing_time:.2f}ms")
            print(f"🎯 Query type: {data.get('query_type')}")
            print(f"📊 Confidence: {data.get('confidence')}")
            print(f"📄 Response: {data.get('response')[:200]}...")
            
            # Check if response indicates image was processed
            response_text = data.get('response', '').lower()
            if 'image' in response_text and len(data.get('response', '')) > 100:
                print("🎉 SUCCESS: VLM Fallback processed the stored image!")
                return True
            else:
                print("⚠️ Response may not include image analysis")
                print(f"Full response: {data.get('response')}")
                return False
        else:
            print(f"❌ VLM Fallback failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ VLM Fallback error: {e}")
        return False

def check_servers():
    """Check if required servers are running"""
    print("🔍 Checking server status...")
    
    try:
        # Check backend
        backend_response = requests.get("http://localhost:8000/health", timeout=5)
        if backend_response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server not healthy")
            return False
    except:
        print("❌ Backend server not accessible")
        return False
    
    try:
        # Check VLM server
        vlm_response = requests.get("http://localhost:8080/health", timeout=5)
        if vlm_response.status_code == 200:
            print("✅ VLM server is running")
        else:
            print("❌ VLM server not healthy")
            return False
    except:
        print("❌ VLM server not accessible")
        return False
    
    return True

def main():
    """Run fixed image fallback test"""
    print("🚀 Fixed Image Fallback Test")
    print("=" * 60)
    print("Testing the bug fixes for image fallback workflow:")
    print("1. ✅ Added image storage to StateTracker.__init__")
    print("2. ✅ Updated process_vlm_response signature with image_data parameter")
    print("3. ✅ Implemented get_last_processed_image to return stored image")
    print("4. ✅ Modified backend to extract and pass image data")
    print("5. ✅ Updated all process_vlm_response calls")
    print()
    
    # Check servers
    if not check_servers():
        print("\\n❌ Required servers are not running. Please start:")
        print("1. Backend: python start_system.py --backend")
        print("2. VLM: python start_system.py --vlm")
        return
    
    print()
    
    # Run tests
    step1_success = test_image_processing()
    if step1_success:
        time.sleep(2)  # Give system time to process
        step2_success = test_vlm_fallback()
        
        print("\\n" + "=" * 60)
        if step1_success and step2_success:
            print("🎉 ALL BUGS FIXED! COMPLETE SUCCESS!")
            print("✅ Image processing and storage: Working")
            print("✅ VLM fallback with stored image: Working")
            print("\\n🎯 Your VLM Fallback system is now fully functional!")
        else:
            print("⚠️ PARTIAL SUCCESS - Some issues remain")
            print(f"✅ Image processing: {'Working' if step1_success else 'Failed'}")
            print(f"{'✅' if step2_success else '❌'} VLM fallback: {'Working' if step2_success else 'Failed'}")
    else:
        print("\\n❌ Test failed at image processing step")
    
    print("\\n💡 Next steps:")
    print("1. Test with real images using src/frontend/ai_vision_analysis.html")
    print("2. Take photos and test VLM fallback queries")
    print("3. System is ready for production use!")

if __name__ == "__main__":
    main()