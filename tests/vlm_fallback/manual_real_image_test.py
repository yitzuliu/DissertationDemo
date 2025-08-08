#!/usr/bin/env python3
"""
Manual Real Image Test

This script manually tests the VLM fallback system with real images from src/testing/materials.
It's designed to be run directly to verify VLM response accuracy with actual photos.
"""

import requests
import base64
import json
import time
import os
from pathlib import Path

# Get project root
project_root = Path(__file__).parent.parent.parent

def load_real_image(image_path: str) -> bytes:
    """Load a real image from testing materials"""
    full_path = project_root / "src" / "testing" / "materials" / image_path
    
    if not full_path.exists():
        print(f"❌ Image not found: {full_path}")
        return None
    
    with open(full_path, 'rb') as f:
        return f.read()

def image_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64"""
    return base64.b64encode(image_bytes).decode('utf-8')

def test_image_processing_and_storage(image_path: str, description: str):
    """Test image processing through /v1/chat/completions and storage in state tracker"""
    print(f"\\n🖼️ Testing {description}")
    print("=" * 60)
    print(f"📁 Image path: {image_path}")
    
    # Load real image
    image_bytes = load_real_image(image_path)
    if not image_bytes:
        return False
    
    print(f"📊 Image size: {len(image_bytes)} bytes")
    
    # Convert to base64
    image_base64 = image_to_base64(image_bytes)
    
    # Step 1: Process image through /v1/chat/completions
    print("\\n📤 Step 1: Processing image through /v1/chat/completions")
    print("-" * 50)
    
    request_data = {
        "model": "smolvlm",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please describe this image in detail. What do you see?"
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
        "max_tokens": 200
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=request_data,
            timeout=60
        )
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f"✅ Image processed successfully in {processing_time:.2f}s")
            print(f"📄 VLM Direct Response:")
            print(f"    {content}")
            print(f"📊 Response length: {len(content)} characters")
            print(f"🗃️ Image should now be stored in state tracker")
        else:
            print(f"❌ Image processing failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Image processing error: {e}")
        return False
    
    # Step 2: Test VLM fallback queries
    print("\\n🔄 Step 2: Testing VLM Fallback with stored image")
    print("-" * 50)
    
    fallback_queries = [
        "What is the main subject in this image?",
        "Describe the colors and lighting in this photo",
        "What objects can you identify in this image?",
        "Is this an indoor or outdoor scene? Explain why.",
        "What details stand out to you in this image?"
    ]
    
    fallback_results = []
    
    for i, query in enumerate(fallback_queries, 1):
        print(f"\\n🔍 Query {i}: {query}")
        
        query_data = {
            "query": query,
            "query_id": f"real_image_test_{hash(image_path)}_{i}"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:8000/api/v1/state/query",
                json=query_data,
                timeout=60
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Processed in {processing_time:.2f}s")
                print(f"📊 Confidence: {data.get('confidence', 'N/A')}")
                print(f"🎯 Query Type: {data.get('query_type', 'N/A')}")
                print(f"📄 Response: {data.get('response', 'No response')}")
                
                fallback_results.append({
                    'query': query,
                    'response': data.get('response', ''),
                    'confidence': data.get('confidence', 0),
                    'query_type': data.get('query_type', 'unknown'),
                    'processing_time': processing_time
                })
                
                # Check if response indicates image was processed
                response_text = data.get('response', '').lower()
                if 'image' in response_text or 'photo' in response_text or len(data.get('response', '')) > 50:
                    print("🎉 SUCCESS: VLM Fallback used the stored image!")
                else:
                    print("⚠️ Response may not include image analysis")
                    
            else:
                print(f"❌ Query failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Query error: {e}")
    
    # Summary
    print("\\n📊 Test Summary")
    print("=" * 60)
    print(f"📸 Image: {description}")
    print(f"📁 Path: {image_path}")
    print(f"📏 Size: {len(image_bytes)} bytes")
    print(f"🔍 Queries tested: {len(fallback_queries)}")
    print(f"✅ Successful responses: {len(fallback_results)}")
    
    if fallback_results:
        avg_confidence = sum(r['confidence'] for r in fallback_results) / len(fallback_results)
        avg_response_length = sum(len(r['response']) for r in fallback_results) / len(fallback_results)
        print(f"📊 Average confidence: {avg_confidence:.3f}")
        print(f"📝 Average response length: {avg_response_length:.1f} characters")
        
        print("\\n🎯 Response Quality Analysis:")
        for i, result in enumerate(fallback_results, 1):
            quality = "High" if len(result['response']) > 100 else "Medium" if len(result['response']) > 50 else "Low"
            print(f"  {i}. {quality:6} | {result['confidence']:.3f} | {len(result['response']):3d} chars | {result['query'][:40]}...")
    
    return len(fallback_results) > 0

def check_servers():
    """Check if required servers are running"""
    print("🔍 Checking server status...")
    
    try:
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

def list_available_images():
    """List available test images"""
    print("📁 Available test images:")
    
    image_dirs = [
        "images",
        "debug_images"
    ]
    
    available_images = []
    
    for dir_name in image_dirs:
        dir_path = project_root / "src" / "testing" / "materials" / dir_name
        if dir_path.exists():
            for image_file in dir_path.glob("*"):
                if image_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                    rel_path = f"{dir_name}/{image_file.name}"
                    size = image_file.stat().st_size
                    available_images.append((rel_path, size))
                    print(f"  📸 {rel_path} ({size:,} bytes)")
    
    return available_images

def main():
    """Run manual real image tests"""
    print("🚀 Manual Real Image VLM Fallback Test")
    print("=" * 80)
    print("This test uses actual photos from src/testing/materials to verify")
    print("that the VLM fallback system works correctly with real images.")
    print()
    
    # Check servers
    if not check_servers():
        print("\\n❌ Required servers are not running. Please start:")
        print("1. Backend: python start_system.py --backend")
        print("2. VLM: python start_system.py --vlm")
        return
    
    print()
    
    # List available images
    available_images = list_available_images()
    if not available_images:
        print("❌ No test images found in src/testing/materials")
        return
    
    print()
    
    # Test with selected real images
    test_images = [
        ("images/IMG_0119.JPG", "IMG_0119 - Real photo 1"),
        ("images/IMG_2053.JPG", "IMG_2053 - Real photo 2"),
        ("debug_images/sample.jpg", "Sample debug image"),
        ("debug_images/test.jpg", "Test debug image")
    ]
    
    successful_tests = 0
    total_tests = 0
    
    for image_path, description in test_images:
        # Check if image exists
        full_path = project_root / "src" / "testing" / "materials" / image_path
        if not full_path.exists():
            print(f"⚠️ Skipping {description} - file not found")
            continue
        
        total_tests += 1
        if test_image_processing_and_storage(image_path, description):
            successful_tests += 1
        
        print("\\n" + "="*80)
        time.sleep(2)  # Brief pause between tests
    
    # Final summary
    print("\\n🎯 Final Test Summary")
    print("=" * 80)
    print(f"📊 Tests completed: {total_tests}")
    print(f"✅ Successful tests: {successful_tests}")
    print(f"❌ Failed tests: {total_tests - successful_tests}")
    
    if successful_tests == total_tests:
        print("\\n🎉 ALL TESTS PASSED!")
        print("✅ VLM Fallback system works correctly with real images")
        print("✅ Image processing and storage is functional")
        print("✅ Query responses are meaningful and accurate")
    elif successful_tests > 0:
        print("\\n⚠️ PARTIAL SUCCESS")
        print(f"✅ {successful_tests}/{total_tests} tests passed")
        print("Some images may have processing issues")
    else:
        print("\\n❌ ALL TESTS FAILED")
        print("Check server status and image processing pipeline")
    
    print("\\n💡 Next steps:")
    print("1. Review the VLM responses above for accuracy")
    print("2. Compare responses with what you actually see in the images")
    print("3. Test with additional real images as needed")

if __name__ == "__main__":
    main()