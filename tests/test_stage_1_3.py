#!/usr/bin/env python3
"""
Test script for Stage 1.3: Precomputed Vector Optimization

This script tests the vector optimization features including:
1. Precomputed embeddings during system startup
2. Vector cache and fast retrieval mechanisms
3. Vector update and maintenance interfaces
4. Vector search performance testing
"""

import sys
import time
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from memory.rag.knowledge_base import RAGKnowledgeBase
from memory.rag.performance_tester import PerformanceTester

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_precomputed_embeddings():
    """Test precomputed embeddings during system startup"""
    print("🧪 Testing Precomputed Embeddings...")
    
    try:
        # Initialize with precomputation enabled
        kb = RAGKnowledgeBase(
            tasks_directory="data/tasks",
            cache_dir="cache/stage_1_3_test"
        )
        
        # Measure initialization time with precomputation
        start_time = time.time()
        kb.initialize(precompute_embeddings=True)
        init_time = time.time() - start_time
        
        print(f"✅ System initialized with precomputation in {init_time:.2f} seconds")
        
        # Check optimizer stats
        stats = kb.get_system_stats()
        optimizer_stats = stats.get('vector_optimizer', {})
        cache_stats = optimizer_stats.get('cache_stats', {})
        
        print(f"   - Total embeddings: {cache_stats.get('total_embeddings', 0)}")
        print(f"   - Precompute time: {cache_stats.get('precompute_time', 0):.2f}s")
        print(f"   - Cached tasks: {optimizer_stats.get('cached_tasks', 0)}")
        
        # Verify embeddings are cached
        if cache_stats.get('total_embeddings', 0) > 0:
            print("✅ Embeddings successfully precomputed and cached")
            return True
        else:
            print("❌ No embeddings found in cache")
            return False
            
    except Exception as e:
        print(f"❌ Precomputed embeddings test failed: {str(e)}")
        return False

def test_vector_cache_and_retrieval():
    """Test vector cache and fast retrieval mechanisms"""
    print("\n🧪 Testing Vector Cache and Fast Retrieval...")
    
    try:
        kb = RAGKnowledgeBase(
            tasks_directory="data/tasks",
            cache_dir="cache/stage_1_3_cache"
        )
        kb.initialize(precompute_embeddings=True)
        
        # Test cache retrieval
        # Get the actual task name from loaded tasks
        task_names = list(kb.loaded_tasks.keys())
        if not task_names:
            print("❌ No tasks loaded")
            return False
            
        task_name = task_names[0]  # Use the first (and likely only) task
        step_id = 1
        
        # Get cached embedding
        cached_embedding = kb.vector_optimizer.get_cached_embedding(task_name, step_id)
        
        if cached_embedding is not None:
            print("✅ Successfully retrieved cached embedding")
            print(f"   - Embedding shape: {cached_embedding.shape if hasattr(cached_embedding, 'shape') else 'N/A'}")
        else:
            print("❌ Failed to retrieve cached embedding")
            return False
        
        # Test cache hit/miss statistics
        optimizer_stats = kb.vector_optimizer.get_optimization_stats()
        cache_stats = optimizer_stats.get('cache_stats', {})
        
        print(f"   - Cache hits: {cache_stats.get('cache_hits', 0)}")
        print(f"   - Cache misses: {cache_stats.get('cache_misses', 0)}")
        print(f"   - Hit rate: {cache_stats.get('hit_rate', 0):.1%}")
        
        # Test fast retrieval performance
        search_times = []
        for i in range(10):
            start_time = time.time()
            match = kb.find_matching_step("I see coffee beans on the counter")
            search_time = (time.time() - start_time) * 1000
            search_times.append(search_time)
        
        avg_search_time = sum(search_times) / len(search_times)
        print(f"   - Average search time: {avg_search_time:.1f}ms")
        
        return avg_search_time < 50  # Reasonable threshold
        
    except Exception as e:
        print(f"❌ Vector cache test failed: {str(e)}")
        return False

def test_vector_update_and_maintenance():
    """Test vector update and maintenance interfaces"""
    print("\n🧪 Testing Vector Update and Maintenance...")
    
    try:
        kb = RAGKnowledgeBase(
            tasks_directory="data/tasks",
            cache_dir="cache/stage_1_3_maintenance"
        )
        kb.initialize(precompute_embeddings=True)
        
        # Get initial stats
        initial_stats = kb.vector_optimizer.get_optimization_stats()
        initial_cached_tasks = initial_stats.get('cached_tasks', 0)
        
        print(f"   Initial cached tasks: {initial_cached_tasks}")
        
        # Test cache invalidation
        # Get the actual task name from loaded tasks
        task_names = list(kb.loaded_tasks.keys())
        if not task_names:
            print("❌ No tasks loaded")
            return False
            
        task_name = task_names[0]
        kb.vector_optimizer.invalidate_task_cache(task_name)
        
        after_invalidation_stats = kb.vector_optimizer.get_optimization_stats()
        after_cached_tasks = after_invalidation_stats.get('cached_tasks', 0)
        
        print(f"   After invalidation: {after_cached_tasks}")
        
        # Test cache update
        if kb.loaded_tasks and task_name in kb.loaded_tasks:
            task = kb.loaded_tasks[task_name]
            success = kb.vector_optimizer.update_task_embeddings(task_name, task)
            
            if success:
                print("✅ Successfully updated task embeddings")
            else:
                print("❌ Failed to update task embeddings")
                return False
        
        # Test health check
        health = kb.vector_optimizer.health_check()
        print(f"   Optimizer health: {health['status']}")
        
        if health['issues']:
            print(f"   Issues: {health['issues']}")
        
        if health['warnings']:
            print(f"   Warnings: {health['warnings']}")
        
        return health['status'] in ['healthy', 'warning']
        
    except Exception as e:
        print(f"❌ Vector maintenance test failed: {str(e)}")
        return False

def test_performance_optimization():
    """Test vector search performance with optimization"""
    print("\n🧪 Testing Performance Optimization...")
    
    try:
        kb = RAGKnowledgeBase(
            tasks_directory="data/tasks",
            cache_dir="cache/stage_1_3_performance"
        )
        kb.initialize(precompute_embeddings=True)
        
        # Create performance tester
        tester = PerformanceTester(kb)
        
        # Run basic speed test
        print("   Running basic speed test...")
        speed_result = tester.run_basic_speed_test(num_searches=20, target_time_ms=15.0)
        
        print(f"   - Average search time: {speed_result.average_time:.1f}ms")
        print(f"   - Min time: {speed_result.min_time:.1f}ms")
        print(f"   - Max time: {speed_result.max_time:.1f}ms")
        print(f"   - Success rate: {speed_result.success_rate:.1%}")
        print(f"   - Target met (<15ms): {'✅' if speed_result.target_met else '❌'}")
        
        # Run cache performance test
        print("   Running cache performance test...")
        cache_result = tester.run_cache_performance_test()
        
        print(f"   - Cache improvement: {cache_result.get('performance_improvement_percent', 0):.1f}%")
        print(f"   - Cache hit rate: {cache_result.get('cache_hit_rate', 0):.1%}")
        
        # Overall assessment
        performance_good = (
            speed_result.average_time < 20 and 
            speed_result.success_rate > 0.8 and
            cache_result.get('performance_improvement_percent', 0) > 0
        )
        
        if performance_good:
            print("✅ Performance optimization working effectively")
        else:
            print("⚠️ Performance optimization needs improvement")
        
        return performance_good
        
    except Exception as e:
        print(f"❌ Performance optimization test failed: {str(e)}")
        return False

def test_engineering_optimization_value():
    """Test the engineering optimization practical value"""
    print("\n🧪 Testing Engineering Optimization Practical Value...")
    
    try:
        # Test without optimization
        kb_unoptimized = RAGKnowledgeBase(
            tasks_directory="data/tasks",
            cache_dir="cache/stage_1_3_unoptimized"
        )
        
        # Disable precomputation
        kb_unoptimized.vector_optimizer.enable_precompute = False
        kb_unoptimized.initialize(precompute_embeddings=False)
        
        # Measure unoptimized performance
        unoptimized_times = []
        for _ in range(10):
            start_time = time.time()
            kb_unoptimized.find_matching_step("I see coffee beans")
            search_time = (time.time() - start_time) * 1000
            unoptimized_times.append(search_time)
        
        avg_unoptimized = sum(unoptimized_times) / len(unoptimized_times)
        
        # Test with optimization
        kb_optimized = RAGKnowledgeBase(
            tasks_directory="data/tasks",
            cache_dir="cache/stage_1_3_optimized"
        )
        
        start_precompute = time.time()
        kb_optimized.initialize(precompute_embeddings=True)
        precompute_time = time.time() - start_precompute
        
        # Measure optimized performance
        optimized_times = []
        for _ in range(10):
            start_time = time.time()
            kb_optimized.find_matching_step("I see coffee beans")
            search_time = (time.time() - start_time) * 1000
            optimized_times.append(search_time)
        
        avg_optimized = sum(optimized_times) / len(optimized_times)
        
        # Calculate improvement
        improvement = ((avg_unoptimized - avg_optimized) / avg_unoptimized) * 100 if avg_unoptimized > 0 else 0
        
        print(f"   - Precompute time: {precompute_time:.2f}s")
        print(f"   - Unoptimized avg: {avg_unoptimized:.1f}ms")
        print(f"   - Optimized avg: {avg_optimized:.1f}ms")
        print(f"   - Performance improvement: {improvement:.1f}%")
        
        # Practical value assessment
        practical_value = improvement > 10 or avg_optimized < 15
        
        if practical_value:
            print("✅ Engineering optimization provides practical value")
        else:
            print("⚠️ Engineering optimization value is limited")
        
        return practical_value
        
    except Exception as e:
        print(f"❌ Engineering optimization value test failed: {str(e)}")
        return False

def main():
    """Run all Stage 1.3 tests"""
    print("🚀 Starting Stage 1.3: Precomputed Vector Optimization Tests\n")
    
    tests = [
        ("Precomputed Embeddings", test_precomputed_embeddings),
        ("Vector Cache and Retrieval", test_vector_cache_and_retrieval),
        ("Vector Update and Maintenance", test_vector_update_and_maintenance),
        ("Performance Optimization", test_performance_optimization),
        ("Engineering Optimization Value", test_engineering_optimization_value)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"{'='*60}")
            result = test_func()
            if result:
                print(f"✅ {test_name}: PASSED")
                passed_tests += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {str(e)}")
    
    print(f"\n{'='*60}")
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All Stage 1.3 tests passed!")
        print("\n🎯 Stage 1.3 Requirements Verification:")
        print("   ✅ System startup precomputed embeddings")
        print("   ✅ Vector cache and fast retrieval mechanisms")
        print("   ✅ Vector update and maintenance interfaces")
        print("   ✅ Vector search performance testing")
        print("   ✅ Engineering optimization practical value demonstrated")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)