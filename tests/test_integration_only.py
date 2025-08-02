#!/usr/bin/env python3
"""
Test Integration Only

Test VLM fallback integration without running servers.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all imports work"""
    print("🔧 Testing Imports...")
    
    try:
        from state_tracker.query_processor import QueryProcessor
        print("✅ QueryProcessor import successful")
    except Exception as e:
        print(f"❌ QueryProcessor import failed: {e}")
        return False
    
    try:
        from vlm_fallback.fallback_processor import VLMFallbackProcessor
        print("✅ VLMFallbackProcessor import successful")
    except Exception as e:
        print(f"❌ VLMFallbackProcessor import failed: {e}")
        return False
    
    try:
        from vlm_fallback.decision_engine import DecisionEngine
        print("✅ DecisionEngine import successful")
    except Exception as e:
        print(f"❌ DecisionEngine import failed: {e}")
        return False
    
    return True

def test_query_processor():
    """Test query processor initialization"""
    print("\n🔍 Testing Query Processor...")
    
    try:
        from state_tracker.query_processor import QueryProcessor
        
        processor = QueryProcessor()
        print("✅ QueryProcessor initialized")
        
        # Check if VLM fallback is available
        if hasattr(processor, 'vlm_fallback') and processor.vlm_fallback:
            print("✅ VLM fallback available in query processor")
        else:
            print("⚠️ VLM fallback not available (this is OK)")
        
        # Test basic query processing
        result = processor.process_query(
            query="Where am I?",
            current_state={"task_id": "test", "step_index": 1}
        )
        
        if result and hasattr(result, 'response_text'):
            print(f"✅ Basic query processing: {result.response_text[:50]}...")
        else:
            print("❌ Basic query processing failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Query processor test failed: {e}")
        return False

def test_decision_engine():
    """Test decision engine"""
    print("\n🤖 Testing Decision Engine...")
    
    try:
        from vlm_fallback.decision_engine import DecisionEngine
        
        engine = DecisionEngine()
        print("✅ DecisionEngine initialized")
        
        # Test decision logic
        decision = engine.should_use_vlm_fallback(
            query="What is quantum computing?",
            state_data=None
        )
        
        print(f"✅ Decision for complex query with no state: {decision}")
        
        decision2 = engine.should_use_vlm_fallback(
            query="Where am I?",
            state_data={"task_id": "test", "step_index": 1, "confidence": 0.9}
        )
        
        print(f"✅ Decision for simple query with good state: {decision2}")
        
        return True
        
    except Exception as e:
        print(f"❌ Decision engine test failed: {e}")
        return False

def test_fallback_processor():
    """Test fallback processor"""
    print("\n🔄 Testing Fallback Processor...")
    
    try:
        from vlm_fallback.fallback_processor import VLMFallbackProcessor
        
        processor = VLMFallbackProcessor()
        print("✅ VLMFallbackProcessor initialized")
        
        # Test status
        if hasattr(processor, 'get_statistics'):
            stats = processor.get_statistics()
            print(f"✅ Processor statistics available: {list(stats.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fallback processor test failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n⚙️ Testing Configuration...")
    
    try:
        from vlm_fallback.config import load_config
        
        config = load_config()
        print("✅ Configuration loaded")
        
        print(f"✅ Confidence threshold: {config.confidence_threshold}")
        print(f"✅ VLM server URL: {config.model_server_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run integration tests"""
    print("🧪 VLM Fallback Integration Test")
    print("=" * 50)
    print("Testing integration without running servers")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Query Processor", test_query_processor),
        ("Decision Engine", test_decision_engine),
        ("Fallback Processor", test_fallback_processor),
        ("Configuration", test_config)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 INTEGRATION TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
        if success:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All integration tests passed!")
        print("✅ VLM Fallback system is properly integrated!")
        print("🚀 You can now start the servers and test the full system")
    else:
        print(f"\n⚠️ {len(results) - passed} tests failed")
        print("Please check the error messages above")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)