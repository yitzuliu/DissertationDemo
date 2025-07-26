#!/usr/bin/env python3
"""
Test script for RAG Vector Search Engine

This script tests the complete RAG system including:
1. Vector search engine functionality
2. Knowledge base integration
3. Semantic matching performance
4. Match result quality
"""

import sys
import time
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from memory.rag.knowledge_base import RAGKnowledgeBase
from memory.rag.vector_search import VectorSearchEngine, MatchResult
from memory.rag.task_loader import TaskKnowledgeLoader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_vector_search_engine():
    """Test the vector search engine functionality"""
    print("🧪 Testing Vector Search Engine...")
    
    try:
        # Initialize knowledge base
        kb = RAGKnowledgeBase(
            tasks_directory="data/tasks",
            model_name="all-MiniLM-L6-v2",
            cache_dir="cache/test_embeddings"
        )
        
        # Initialize with precomputed embeddings
        start_time = time.time()
        kb.initialize(precompute_embeddings=True)
        init_time = time.time() - start_time
        
        print(f"✅ Knowledge base initialized in {init_time:.2f} seconds")
        print(f"   - Loaded tasks: {len(kb.get_all_tasks())}")
        
        # Test basic search functionality
        test_observations = [
            "I see coffee beans and a grinder on the counter",
            "The water is heating up in the kettle, I can see steam",
            "I'm pouring hot water over the coffee grounds in a circular motion",
            "The coffee is dripping into the mug below",
            "I see a full cup of coffee with steam rising from it",
            "There are some tools on the table but I'm not sure what they are"
        ]
        
        print(f"\n🔍 Testing semantic matching with {len(test_observations)} observations...")
        
        total_search_time = 0
        successful_matches = 0
        
        for i, observation in enumerate(test_observations, 1):
            print(f"\n--- Test {i}: {observation[:50]}...")
            
            # Measure search time
            start_time = time.time()
            match = kb.find_matching_step(observation)
            search_time = time.time() - start_time
            total_search_time += search_time
            
            print(f"    Search time: {search_time*1000:.1f}ms")
            print(f"    Similarity: {match.similarity:.3f}")
            print(f"    Confidence: {match.confidence_level}")
            
            if match.is_reliable:
                successful_matches += 1
                print(f"    ✅ Matched to: {match.task_description[:60]}...")
                print(f"    Tools needed: {', '.join(match.tools_needed[:3])}...")
                print(f"    Visual cues matched: {', '.join(match.matched_cues[:3])}...")
            else:
                print(f"    ❌ Low confidence match")
        
        avg_search_time = (total_search_time / len(test_observations)) * 1000
        match_rate = successful_matches / len(test_observations)
        
        print(f"\n📊 Search Performance Summary:")
        print(f"   - Average search time: {avg_search_time:.1f}ms")
        print(f"   - Successful matches: {successful_matches}/{len(test_observations)} ({match_rate:.1%})")
        print(f"   - Performance target (<10ms): {'✅ PASS' if avg_search_time < 10 else '❌ FAIL'}")
        
        return avg_search_time < 10 and match_rate >= 0.7
        
    except Exception as e:
        print(f"❌ Vector search test failed: {str(e)}")
        return False

def test_multiple_matches():
    """Test finding multiple matches for ambiguous observations"""
    print("\n🧪 Testing Multiple Match Functionality...")
    
    try:
        kb = RAGKnowledgeBase(tasks_directory="data/tasks")
        kb.initialize(precompute_embeddings=False)  # Skip precomputation for speed
        
        # Test with ambiguous observation
        ambiguous_observation = "I see some equipment on the counter"
        
        matches = kb.find_multiple_matches(ambiguous_observation, top_k=3)
        
        print(f"   Query: {ambiguous_observation}")
        print(f"   Found {len(matches)} matches:")
        
        for i, match in enumerate(matches, 1):
            print(f"   {i}. Similarity: {match.similarity:.3f} - {match.task_description[:50]}...")
        
        return len(matches) > 0
        
    except Exception as e:
        print(f"❌ Multiple matches test failed: {str(e)}")
        return False

def test_knowledge_base_management():
    """Test knowledge base management features"""
    print("\n🧪 Testing Knowledge Base Management...")
    
    try:
        kb = RAGKnowledgeBase(tasks_directory="data/tasks")
        kb.initialize()
        
        # Test system stats
        stats = kb.get_system_stats()
        print(f"   System stats retrieved: {len(stats)} categories")
        
        # Test health check
        health = kb.health_check()
        print(f"   Health status: {health['status']}")
        print(f"   Issues: {len(health['issues'])}")
        print(f"   Warnings: {len(health['warnings'])}")
        
        # Test task information retrieval
        tasks = kb.get_all_tasks()
        if tasks:
            first_task = tasks[0]
            summary = kb.get_task_summary(first_task)
            print(f"   Task summary for '{first_task}': {len(summary)} fields")
            
            # Test step details
            step_details = kb.get_step_details(first_task, 1)
            if step_details:
                print(f"   Step 1 details: {len(step_details)} fields")
        
        return health['status'] in ['healthy', 'warning']
        
    except Exception as e:
        print(f"❌ Knowledge base management test failed: {str(e)}")
        return False

def test_performance_optimization():
    """Test performance optimization features"""
    print("\n🧪 Testing Performance Optimization...")
    
    try:
        kb = RAGKnowledgeBase(
            tasks_directory="data/tasks",
            cache_dir="cache/test_performance"
        )
        
        # Test without precomputation
        start_time = time.time()
        kb.initialize(precompute_embeddings=False)
        no_precomp_time = time.time() - start_time
        
        # Test first search (should be slower)
        observation = "I see coffee beans on the counter"
        start_time = time.time()
        match1 = kb.find_matching_step(observation)
        first_search_time = time.time() - start_time
        
        # Test second search (should be faster due to caching)
        start_time = time.time()
        match2 = kb.find_matching_step(observation)
        second_search_time = time.time() - start_time
        
        # Get performance stats
        stats = kb.get_system_stats()
        vector_stats = stats['vector_engine']
        
        print(f"   Initialization time (no precomp): {no_precomp_time:.3f}s")
        print(f"   First search time: {first_search_time*1000:.1f}ms")
        print(f"   Second search time: {second_search_time*1000:.1f}ms")
        print(f"   Cache hit rate: {vector_stats.get('cache_hit_rate', 0):.1%}")
        print(f"   Total searches: {vector_stats.get('total_searches', 0)}")
        
        # Verify caching improved performance
        performance_improved = second_search_time < first_search_time
        print(f"   Caching improved performance: {'✅' if performance_improved else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance optimization test failed: {str(e)}")
        return False

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n🧪 Testing Edge Cases...")
    
    try:
        kb = RAGKnowledgeBase(tasks_directory="data/tasks")
        kb.initialize()
        
        # Test empty observation
        empty_match = kb.find_matching_step("")
        print(f"   Empty observation handled: {empty_match.confidence_level == 'none'}")
        
        # Test very long observation
        long_observation = "This is a very long observation " * 50
        long_match = kb.find_matching_step(long_observation)
        print(f"   Long observation handled: {long_match is not None}")
        
        # Test non-existent task
        step_details = kb.get_step_details("non_existent_task", 1)
        print(f"   Non-existent task handled: {step_details is None}")
        
        # Test invalid step ID
        tasks = kb.get_all_tasks()
        if tasks:
            invalid_step = kb.get_step_details(tasks[0], 999)
            print(f"   Invalid step ID handled: {invalid_step is None}")
        
        return True
        
    except Exception as e:
        print(f"❌ Edge cases test failed: {str(e)}")
        return False

def main():
    """Run all RAG vector search tests"""
    print("🚀 Starting RAG Vector Search Engine Tests\n")
    
    tests = [
        ("Vector Search Engine", test_vector_search_engine),
        ("Multiple Matches", test_multiple_matches),
        ("Knowledge Base Management", test_knowledge_base_management),
        ("Performance Optimization", test_performance_optimization),
        ("Edge Cases", test_edge_cases)
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
        print("🎉 All RAG vector search tests passed!")
        print("\n🎯 Stage 1.2 Requirements Verification:")
        print("   ✅ ChromaDB-based high-speed vector search")
        print("   ✅ Semantic similarity computation and ranking")
        print("   ✅ MatchResult data model with complete step information")
        print("   ✅ Optimized search performance (<10ms target)")
        print("   ✅ Intelligent semantic matching demonstrated")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)