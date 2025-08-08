#!/usr/bin/env python3
"""
Manual Test Script for VLM Fallback Image Enhancement

This script provides manual testing capabilities for the image fallback functionality.
Run this script to test the complete image fallback flow with real or mock data.
"""

import sys
import os
import asyncio
import base64
import time
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from state_tracker.query_processor import QueryProcessor
from vlm_fallback.config import VLMFallbackConfig
from vlm_fallback.image_capture_manager import ImageCaptureManager
from vlm_fallback.enhanced_fallback_processor import EnhancedVLMFallbackProcessor

def create_mock_image_data():
    """Create mock image data for testing"""
    # Create a simple test image (1x1 pixel JPEG-like data)
    test_image_bytes = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
    
    return {
        "image_data": base64.b64encode(test_image_bytes).decode('utf-8'),
        "format": "jpeg",
        "size": len(test_image_bytes),
        "processed": True,
        "timestamp": datetime.now()
    }

def load_real_test_images():
    """Load real test images from the materials directory"""
    images_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'testing', 'materials', 'images')
    test_images = {}
    
    # Load test images
    image_files = ['test_image.jpg', 'IMG_0119.JPG']
    
    for image_file in image_files:
        image_path = os.path.join(images_dir, image_file)
        if os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                    test_images[image_file] = {
                        "image_data": base64.b64encode(image_data).decode('utf-8'),
                        "format": "jpeg",
                        "size": len(image_data),
                        "processed": True,
                        "timestamp": datetime.now()
                    }
                    print(f"✅ Loaded real image: {image_file} ({len(image_data)} bytes)")
            except Exception as e:
                print(f"❌ Failed to load {image_file}: {e}")
        else:
            print(f"⚠️ Image file not found: {image_path}")
    
    return test_images

def test_image_capture_manager():
    """Test ImageCaptureManager functionality"""
    print("🧪 Testing ImageCaptureManager")
    print("-" * 40)
    
    try:
        manager = ImageCaptureManager()
        print("✅ ImageCaptureManager created successfully")
        
        # Test with mock image data
        mock_image = create_mock_image_data()
        manager.last_captured_image = base64.b64decode(mock_image["image_data"])
        
        # Test image processing
        result = manager._process_for_fallback(manager.last_captured_image, "smolvlm")
        if result:
            print(f"✅ Image processing successful: {result['size']} bytes, format: {result['format']}")
        else:
            print("❌ Image processing failed")
            
    except Exception as e:
        print(f"❌ ImageCaptureManager test failed: {e}")

def test_image_capture_manager_with_real_images():
    """Test ImageCaptureManager with real images"""
    print("\n🧪 Testing ImageCaptureManager with Real Images")
    print("-" * 50)
    
    try:
        # Load real test images
        real_images = load_real_test_images()
        
        if not real_images:
            print("⚠️ No real test images available, skipping real image tests")
            return
        
        manager = ImageCaptureManager()
        print("✅ ImageCaptureManager created successfully")
        
        # Test with each real image
        for image_name, image_data in real_images.items():
            print(f"\n📸 Testing with {image_name}:")
            
            # Set the real image as cached image
            manager.last_captured_image = base64.b64decode(image_data["image_data"])
            
            # Test image processing
            result = manager._process_for_fallback(manager.last_captured_image, "smolvlm")
            if result:
                print(f"  ✅ Processing successful: {result['size']} bytes, format: {result['format']}")
                print(f"  📊 Original size: {image_data['size']} bytes")
                print(f"  📊 Processed size: {result['size']} bytes")
                print(f"  🔄 Size ratio: {result['size']/image_data['size']:.2f}")
            else:
                print(f"  ❌ Processing failed")
                
    except Exception as e:
        print(f"❌ Real image test failed: {e}")

def test_enhanced_fallback_processor():
    """Test EnhancedVLMFallbackProcessor functionality"""
    print("\n🧪 Testing EnhancedVLMFallbackProcessor")
    print("-" * 40)
    
    try:
        config = VLMFallbackConfig()
        config.enable_image_fallback = True
        
        processor = EnhancedVLMFallbackProcessor(config)
        print("✅ EnhancedVLMFallbackProcessor created successfully")
        print(f"📸 Image fallback enabled: {processor.enable_image_fallback}")
        
        # Test configuration
        if hasattr(processor, 'image_capture_manager'):
            print("✅ ImageCaptureManager integrated")
        else:
            print("❌ ImageCaptureManager not integrated")
            
    except Exception as e:
        print(f"❌ EnhancedVLMFallbackProcessor test failed: {e}")

def test_query_processor_integration():
    """Test QueryProcessor integration with image fallback"""
    print("\n🧪 Testing QueryProcessor Integration")
    print("-" * 40)
    
    try:
        processor = QueryProcessor()
        print("✅ QueryProcessor created successfully")
        
        # Check if enhanced VLM fallback is available
        if hasattr(processor, 'enhanced_vlm_fallback') and processor.enhanced_vlm_fallback:
            print("✅ Enhanced VLM Fallback integrated")
            print(f"📸 Image fallback enabled: {processor.enhanced_vlm_fallback.enable_image_fallback}")
        else:
            print("⚠️ Enhanced VLM Fallback not available")
        
        # Check if standard VLM fallback is available
        if hasattr(processor, 'vlm_fallback') and processor.vlm_fallback:
            print("✅ Standard VLM Fallback available as backup")
        else:
            print("⚠️ Standard VLM Fallback not available")
            
    except Exception as e:
        print(f"❌ QueryProcessor integration test failed: {e}")

def test_confidence_calculation():
    """Test confidence calculation for image queries"""
    print("\n🧪 Testing Confidence Calculation")
    print("-" * 40)
    
    try:
        processor = QueryProcessor()
        
        # Test queries that should trigger image fallback
        test_queries = [
            ("What do you see in this image?", None),
            ("Describe the objects in the picture", None),
            ("What colors are visible?", {"task_id": "test", "step_index": 1}),
            ("Can you identify the items?", None)
        ]
        
        for query, state in test_queries:
            query_type = processor._classify_query(query)
            
            if hasattr(processor, '_calculate_confidence'):
                confidence = processor._calculate_confidence(query_type, state, query)
                should_fallback = processor._should_use_vlm_fallback(query_type, state, confidence)
                
                print(f"📝 Query: '{query[:30]}...'")
                print(f"   Type: {query_type}, Confidence: {confidence:.3f}, Fallback: {should_fallback}")
            else:
                print(f"📝 Query: '{query[:30]}...' - Type: {query_type}")
                
    except Exception as e:
        print(f"❌ Confidence calculation test failed: {e}")

def test_mock_image_fallback():
    """Test image fallback with mock data"""
    print("\n🧪 Testing Mock Image Fallback")
    print("-" * 40)
    
    try:
        processor = QueryProcessor()
        
        # Test image-related query
        query = "What objects do you see in this image?"
        current_state = None  # No state to trigger fallback
        
        print(f"📝 Testing query: '{query}'")
        print("🔄 Processing...")
        
        start_time = time.time()
        result = processor.process_query(query, current_state)
        processing_time = (time.time() - start_time) * 1000
        
        print(f"⏱️  Processing time: {processing_time:.2f}ms")
        print(f"🎯 Query type: {result.query_type}")
        print(f"📊 Confidence: {result.confidence}")
        print(f"📄 Response: {result.response_text[:100]}...")
        
        # Check if it looks like a fallback response
        if len(result.response_text) > 50 and result.confidence > 0.5:
            print("✅ Likely successful fallback response")
        else:
            print("⚠️ May be template response")
            
    except Exception as e:
        print(f"❌ Mock image fallback test failed: {e}")

def main():
    """Run all manual tests"""
    print("🚀 VLM Fallback Image Enhancement - Manual Test")
    print("=" * 60)
    print("This script tests the image fallback functionality")
    print("without requiring actual VLM server connection.")
    print()
    
    # Run all tests
    test_image_capture_manager()
    test_image_capture_manager_with_real_images()
    test_enhanced_fallback_processor()
    test_query_processor_integration()
    test_confidence_calculation()
    test_mock_image_fallback()
    
    print("\n" + "=" * 60)
    print("🏁 Manual testing completed!")
    print()
    print("💡 Next steps:")
    print("1. Start VLM server: python src/models/smolvlm/run_smolvlm.py")
    print("2. Start backend: python src/backend/main.py")
    print("3. Test with real queries: curl -X POST http://localhost:8000/api/v1/state/query \\")
    print("   -H 'Content-Type: application/json' \\")
    print("   -d '{\"query\": \"What do you see in this image?\"}'")

if __name__ == "__main__":
    main()