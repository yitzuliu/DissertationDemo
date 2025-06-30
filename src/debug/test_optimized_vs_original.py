#!/usr/bin/env python3
"""
Performance Comparison: Original vs Optimized SmolVLM2

This script tests both versions side by side to measure:
- Speed improvements
- Memory usage
- Response quality
- Optimization effectiveness
"""

import time
import json
import requests
import base64
from PIL import Image
import io
from pathlib import Path
from datetime import datetime

class PerformanceComparison:
    """
    Compare original vs optimized SmolVLM2 performance
    """
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.results = {
            "original": [],
            "optimized": [],
            "comparison": {}
        }
        
        # Test images
        self.images_dir = Path(__file__).parent / "images"
        self.test_images = self.get_test_images()
        
        print("🔥 PERFORMANCE COMPARISON TEST")
        print("=" * 60)
        print("🎯 Testing: Original SmolVLM2 vs Optimized SmolVLM2")
        print(f"📸 Test Images: {len(self.test_images)}")
        print("⚙️ Metrics: Speed, Quality, Memory Efficiency")
        print("=" * 60)
    
    def get_test_images(self):
        """Get test images for comparison"""
        if not self.images_dir.exists():
            return []
        
        image_files = []
        for file in self.images_dir.iterdir():
            if file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                image_files.append(file)
        
        return sorted(image_files)[:2]  # Test with 2 images for quick comparison
    
    def encode_image(self, image_path):
        """Encode image to base64"""
        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=90)
            image_bytes = buffer.getvalue()
            
            return base64.b64encode(image_bytes).decode('utf-8')
    
    def test_model_version(self, model_config, version_name):
        """Test a specific model version"""
        print(f"\n🧪 Testing {version_name} Version")
        print("-" * 40)
        
        # Update backend configuration
        if not self.switch_model_config(model_config):
            print(f"❌ Failed to switch to {version_name} version")
            return []
        
        # Wait for model to load
        print("⏳ Waiting for model to load...")
        time.sleep(5)  # 減少等待時間
        
        # Verify model is ready
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code != 200:
                print(f"❌ Backend not ready for {version_name} version")
                return []
            
            health_data = response.json()
            print(f"✅ Model Ready: {health_data.get('active_model')}")
            
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return []
        
        # Run tests
        version_results = []
        
        for i, image_path in enumerate(self.test_images):
            print(f"\n📸 Image {i+1}: {image_path.name}")
            
            try:
                image_base64 = self.encode_image(image_path)
                
                prompt = "Describe what you see in this image."
                
                # Test request
                start_time = time.time()
                
                payload = {
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }],
                    "max_tokens": 150
                }
                
                response = requests.post(
                    f"{self.backend_url}/v1/chat/completions",
                    json=payload,
                    timeout=60
                )
                
                processing_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = data["choices"][0]["message"]["content"]
                    
                    result = {
                        "image": image_path.name,
                        "version": version_name,
                        "success": True,
                        "processing_time": processing_time,
                        "response": response_text,
                        "response_length": len(response_text),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    print(f"✅ Success: {processing_time:.2f}s")
                    print(f"📝 Response: {response_text[:80]}...")
                    
                else:
                    result = {
                        "image": image_path.name,
                        "version": version_name,
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "processing_time": processing_time
                    }
                    print(f"❌ Failed: HTTP {response.status_code}")
                
                version_results.append(result)
                
            except Exception as e:
                print(f"❌ Error testing {image_path.name}: {e}")
                version_results.append({
                    "image": image_path.name,
                    "version": version_name,
                    "success": False,
                    "error": str(e)
                })
        
        return version_results
    
    def switch_model_config(self, model_config):
        """Switch backend model configuration"""
        try:
            # Update app_config.json
            config_path = Path(__file__).parent.parent / "config" / "app_config.json"
            
            with open(config_path, 'r') as f:
                app_config = json.load(f)
            
            app_config["active_model"] = model_config
            
            with open(config_path, 'w') as f:
                json.dump(app_config, f, indent=2)
            
            print(f"✅ Switched to model config: {model_config}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to switch model config: {e}")
            return False
    
    def run_comparison(self):
        """Run complete performance comparison"""
        print("🚀 Starting Performance Comparison...")
        
        # Test original SmolVLM2
        print("\n🧪 Testing Original SmolVLM2")
        original_results = self.test_model_version("smolvlm2_500m_video", "Original")
        self.results["original"] = original_results
        
        # Test optimized SmolVLM2
        print("\n🧪 Testing Optimized SmolVLM2")
        optimized_results = self.test_model_version("smolvlm2_500m_video_optimized", "Optimized")
        self.results["optimized"] = optimized_results
        
        # Generate comparison
        self.generate_comparison()
        
        # Save results
        self.save_results()
    
    def generate_comparison(self):
        """Generate performance comparison metrics"""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE COMPARISON RESULTS")
        print("=" * 60)
        
        original_times = [r["processing_time"] for r in self.results["original"] if r.get("success")]
        optimized_times = [r["processing_time"] for r in self.results["optimized"] if r.get("success")]
        
        if original_times and optimized_times:
            orig_avg = sum(original_times) / len(original_times)
            opt_avg = sum(optimized_times) / len(optimized_times)
            speed_improvement = orig_avg / opt_avg if opt_avg > 0 else 0
            
            print(f"⏱️ Original Average: {orig_avg:.2f}s")
            print(f"🚀 Optimized Average: {opt_avg:.2f}s")
            print(f"📈 Speed Improvement: {speed_improvement:.1f}x faster")
            
            # Response quality comparison
            orig_lengths = [r["response_length"] for r in self.results["original"] if r.get("success")]
            opt_lengths = [r["response_length"] for r in self.results["optimized"] if r.get("success")]
            
            if orig_lengths and opt_lengths:
                orig_avg_len = sum(orig_lengths) / len(orig_lengths)
                opt_avg_len = sum(opt_lengths) / len(opt_lengths)
                
                print(f"📝 Original Response Length: {orig_avg_len:.0f} chars")
                print(f"📝 Optimized Response Length: {opt_avg_len:.0f} chars")
                print(f"📊 Length Ratio: {opt_avg_len/orig_avg_len:.2f}")
            
            self.results["comparison"] = {
                "original_avg_time": orig_avg,
                "optimized_avg_time": opt_avg,
                "speed_improvement": speed_improvement,
                "original_avg_length": orig_avg_len if orig_lengths else 0,
                "optimized_avg_length": opt_avg_len if opt_lengths else 0
            }
            
            # Optimization effectiveness
            print(f"\n🎯 OPTIMIZATION EFFECTIVENESS:")
            if speed_improvement >= 3:
                print(f"🏆 EXCELLENT: {speed_improvement:.1f}x speed improvement!")
            elif speed_improvement >= 2:
                print(f"✅ GOOD: {speed_improvement:.1f}x speed improvement")
            elif speed_improvement >= 1.5:
                print(f"👍 MODERATE: {speed_improvement:.1f}x speed improvement")
            else:
                print(f"⚠️ LIMITED: {speed_improvement:.1f}x speed improvement")
        
        else:
            print("❌ Insufficient data for comparison")
    
    def save_results(self):
        """Save comparison results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = Path(__file__).parent / f"performance_comparison_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")

def main():
    """Main execution"""
    print("⚡ SmolVLM2 Performance Optimization Test")
    print("Testing original vs optimized implementations...")
    
    comparator = PerformanceComparison()
    
    try:
        comparator.run_comparison()
        print("\n🎉 Performance comparison completed!")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    main() 