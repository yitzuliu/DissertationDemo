#!/usr/bin/env python3
"""
Real Image Fallback Test

This test uses actual photos from src/testing/materials to test the VLM fallback system.
It helps verify that the VLM responses are accurate and meaningful for real images.
"""

import pytest
import asyncio
import base64
import os
import sys
from pathlib import Path
from PIL import Image
import io

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from vlm_fallback.query_processor import QueryProcessor
from vlm_fallback.image_capture_manager import ImageCaptureManager
from vlm_fallback.fallback_processor import VLMFallbackProcessor
from state_tracker import get_state_tracker

class TestRealImageFallback:
    """Test VLM fallback with real images from testing materials"""
    
    @pytest.fixture
    def config(self):
        """Test configuration"""
        return {
            "vlm_fallback": {
                "enabled": True,
                "confidence_threshold": 0.4,
                "image_fallback_enabled": True,
                "vlm_server_url": "http://localhost:8080"
            }
        }
    
    @pytest.fixture
    def query_processor(self, config):
        """Create QueryProcessor instance"""
        return QueryProcessor(config)
    
    def load_real_image(self, image_path: str) -> bytes:
        """Load a real image from testing materials and return as bytes"""
        full_path = project_root / "src" / "testing" / "materials" / image_path
        
        if not full_path.exists():
            pytest.skip(f"Test image not found: {full_path}")
        
        with open(full_path, 'rb') as f:
            return f.read()
    
    def image_to_base64(self, image_bytes: bytes) -> str:
        """Convert image bytes to base64 string"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def store_image_in_state_tracker(self, image_bytes: bytes):
        """Store image in state tracker to simulate previous processing"""
        state_tracker = get_state_tracker()
        # Directly set the image data (simulating what happens after /v1/chat/completions)
        state_tracker.last_processed_image = image_bytes
        print(f"📸 Stored image in state tracker: {len(image_bytes)} bytes")
    
    @pytest.mark.asyncio
    async def test_real_image_fallback_img_0119(self, query_processor):
        """Test VLM fallback with IMG_0119.JPG"""
        print("\\n🖼️ Testing with IMG_0119.JPG")
        print("-" * 50)
        
        # Load real image
        image_bytes = self.load_real_image("images/IMG_0119.JPG")
        self.store_image_in_state_tracker(image_bytes)
        
        # Test queries about the image
        test_queries = [
            "What do you see in this image?",
            "Describe the main objects in this photo",
            "What colors are prominent in this image?",
            "Is this an indoor or outdoor scene?"
        ]
        
        for query in test_queries:
            print(f"\\n🔍 Query: {query}")
            
            result = await query_processor.process_query(
                query=query,
                query_id=f"real_img_0119_{hash(query)}"
            )
            
            print(f"📊 Confidence: {result.get('confidence', 'N/A')}")
            print(f"🎯 Query Type: {result.get('query_type', 'N/A')}")
            print(f"📄 Response: {result.get('response', 'No response')[:200]}...")
            
            # Verify response quality
            response = result.get('response', '')
            assert len(response) > 50, "Response should be substantial"
            assert 'image' in response.lower() or 'photo' in response.lower() or 'see' in response.lower(), "Response should reference visual content"
    
    @pytest.mark.asyncio
    async def test_real_image_fallback_img_2053(self, query_processor):
        """Test VLM fallback with IMG_2053.JPG"""
        print("\\n🖼️ Testing with IMG_2053.JPG")
        print("-" * 50)
        
        # Load real image
        image_bytes = self.load_real_image("images/IMG_2053.JPG")
        self.store_image_in_state_tracker(image_bytes)
        
        # Test specific queries
        test_queries = [
            "What is the main subject of this photograph?",
            "Describe the setting and environment",
            "What details can you observe in this image?"
        ]
        
        for query in test_queries:
            print(f"\\n🔍 Query: {query}")
            
            result = await query_processor.process_query(
                query=query,
                query_id=f"real_img_2053_{hash(query)}"
            )
            
            print(f"📊 Confidence: {result.get('confidence', 'N/A')}")
            print(f"🎯 Query Type: {result.get('query_type', 'N/A')}")
            print(f"📄 Response: {result.get('response', 'No response')[:200]}...")
            
            # Verify response quality
            response = result.get('response', '')
            assert len(response) > 30, "Response should be meaningful"
            assert result.get('confidence', 0) > 0.3, "Should have reasonable confidence"
    
    @pytest.mark.asyncio
    async def test_real_image_fallback_sample_jpg(self, query_processor):
        """Test VLM fallback with sample.jpg from debug_images"""
        print("\\n🖼️ Testing with sample.jpg")
        print("-" * 50)
        
        # Load real image
        image_bytes = self.load_real_image("debug_images/sample.jpg")
        self.store_image_in_state_tracker(image_bytes)
        
        # Test comprehensive queries
        test_queries = [
            "Analyze this image and describe what you see",
            "What objects are visible in this photo?",
            "Describe the composition and visual elements",
            "What can you tell me about this image?"
        ]
        
        results = []
        for query in test_queries:
            print(f"\\n🔍 Query: {query}")
            
            result = await query_processor.process_query(
                query=query,
                query_id=f"real_sample_{hash(query)}"
            )
            
            print(f"📊 Confidence: {result.get('confidence', 'N/A')}")
            print(f"🎯 Query Type: {result.get('query_type', 'N/A')}")
            print(f"📄 Response: {result.get('response', 'No response')[:200]}...")
            
            results.append(result)
            
            # Verify response quality
            response = result.get('response', '')
            assert len(response) > 20, "Response should not be empty or too short"
        
        # Verify at least one response was high quality
        high_quality_responses = [r for r in results if len(r.get('response', '')) > 100]
        assert len(high_quality_responses) > 0, "At least one response should be detailed"
    
    @pytest.mark.asyncio
    async def test_real_image_comparison(self, query_processor):
        """Test and compare responses across different real images"""
        print("\\n🔄 Comparing responses across different real images")
        print("-" * 60)
        
        images_to_test = [
            ("images/IMG_0119.JPG", "IMG_0119"),
            ("images/IMG_2053.JPG", "IMG_2053"),
            ("debug_images/sample.jpg", "sample"),
            ("debug_images/test.jpg", "test")
        ]
        
        comparison_query = "Describe what you see in this image in detail"
        results = {}
        
        for image_path, image_name in images_to_test:
            try:
                print(f"\\n📸 Testing {image_name}...")
                
                # Load and store image
                image_bytes = self.load_real_image(image_path)
                self.store_image_in_state_tracker(image_bytes)
                
                # Process query
                result = await query_processor.process_query(
                    query=comparison_query,
                    query_id=f"comparison_{image_name}"
                )
                
                results[image_name] = {
                    'response': result.get('response', ''),
                    'confidence': result.get('confidence', 0),
                    'query_type': result.get('query_type', 'unknown'),
                    'response_length': len(result.get('response', ''))
                }
                
                print(f"✅ {image_name}: {results[image_name]['response_length']} chars, confidence: {results[image_name]['confidence']:.3f}")
                
            except Exception as e:
                print(f"⚠️ Skipped {image_name}: {e}")
                continue
        
        # Print comparison summary
        print("\\n📊 Comparison Summary:")
        print("-" * 40)
        for image_name, data in results.items():
            print(f"{image_name:15} | {data['response_length']:4d} chars | {data['confidence']:.3f} conf | {data['query_type']}")
            print(f"{'':15} | {data['response'][:80]}...")
            print()
        
        # Verify we got meaningful results
        assert len(results) > 0, "Should have processed at least one image"
        
        # Verify response quality varies appropriately
        response_lengths = [data['response_length'] for data in results.values()]
        assert max(response_lengths) > 50, "At least one response should be substantial"
    
    def test_image_loading_and_format_validation(self):
        """Test that we can load and validate the format of real test images"""
        print("\\n🔍 Validating test image formats")
        print("-" * 40)
        
        test_images = [
            "images/IMG_0119.JPG",
            "images/IMG_2053.JPG", 
            "images/test_image.jpg",
            "debug_images/sample.jpg",
            "debug_images/test_image.png",
            "debug_images/test.jpg"
        ]
        
        valid_images = []
        
        for image_path in test_images:
            try:
                image_bytes = self.load_real_image(image_path)
                
                # Validate image can be opened
                image = Image.open(io.BytesIO(image_bytes))
                width, height = image.size
                format_type = image.format
                
                print(f"✅ {image_path}: {width}x{height} {format_type} ({len(image_bytes)} bytes)")
                valid_images.append(image_path)
                
            except Exception as e:
                print(f"❌ {image_path}: {e}")
        
        assert len(valid_images) >= 3, f"Should have at least 3 valid test images, found {len(valid_images)}"
        print(f"\\n📊 Found {len(valid_images)} valid test images")

def main():
    """Run real image fallback tests manually"""
    print("🚀 Real Image Fallback Test")
    print("=" * 60)
    print("Testing VLM fallback with actual photos from src/testing/materials")
    print("This helps verify VLM response accuracy with real images")
    print()
    
    # Create test instance
    test_instance = TestRealImageFallback()
    
    # Test image loading first
    print("Step 1: Validating test images...")
    test_instance.test_image_loading_and_format_validation()
    
    print("\\nStep 2: Testing VLM fallback with real images...")
    print("Note: This requires the backend and VLM servers to be running")
    print("Start servers with: python start_system.py --backend --vlm")
    print()
    
    # You can uncomment these to run async tests manually
    # asyncio.run(test_instance.test_real_image_fallback_img_0119(QueryProcessor({"vlm_fallback": {"enabled": True}})))

if __name__ == "__main__":
    main()