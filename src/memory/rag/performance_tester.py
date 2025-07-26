"""
Performance Testing Module for RAG Vector Search

This module provides comprehensive performance testing capabilities
for the RAG vector search system, including:
1. Search speed benchmarks
2. Cache performance analysis
3. Optimization effectiveness measurement
4. System load testing
"""

import time
import statistics
import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

logger = logging.getLogger(__name__)


@dataclass
class PerformanceResult:
    """Result of a performance test"""
    test_name: str
    total_searches: int
    total_time: float
    average_time: float
    min_time: float
    max_time: float
    median_time: float
    std_deviation: float
    success_rate: float
    target_met: bool
    target_time: float


class PerformanceTester:
    """
    Comprehensive performance testing for RAG vector search
    
    Provides various benchmarking and performance analysis tools
    to measure and optimize the RAG system performance.
    """
    
    def __init__(self, knowledge_base):
        """
        Initialize the performance tester
        
        Args:
            knowledge_base: RAGKnowledgeBase instance to test
        """
        self.knowledge_base = knowledge_base
        self.test_observations = [
            "I see coffee beans on the counter",
            "The kettle is heating water with steam rising",
            "I'm grinding coffee beans to medium consistency",
            "The filter is placed in the dripper",
            "I'm pouring hot water in circular motions",
            "Coffee is dripping into the mug below",
            "I see a full cup of fresh coffee",
            "Steam is rising from the hot coffee",
            "The grinder is making noise while processing beans",
            "Water temperature looks optimal for brewing",
            "The coffee grounds are evenly distributed",
            "I can smell the fresh coffee aroma",
            "The dripper is positioned over the mug",
            "Hot water is being poured slowly",
            "The coffee bed is expanding during bloom",
            "Equipment is ready for the next step"
        ]
        
        logger.info("Performance tester initialized")
    
    def run_basic_speed_test(self, 
                           num_searches: int = 50,
                           target_time_ms: float = 10.0) -> PerformanceResult:
        """
        Run basic speed test for vector search
        
        Args:
            num_searches: Number of searches to perform
            target_time_ms: Target time in milliseconds
            
        Returns:
            PerformanceResult with test results
        """
        logger.info(f"Running basic speed test with {num_searches} searches...")
        
        # Warm up the system
        for _ in range(5):
            obs = random.choice(self.test_observations)
            self.knowledge_base.find_matching_step(obs)
        
        # Run actual test
        search_times = []
        successful_searches = 0
        
        start_total = time.time()
        
        for i in range(num_searches):
            observation = random.choice(self.test_observations)
            
            start_time = time.time()
            match = self.knowledge_base.find_matching_step(observation)
            search_time = (time.time() - start_time) * 1000  # Convert to ms
            
            search_times.append(search_time)
            
            if match and match.similarity > 0.3:
                successful_searches += 1
            
            if (i + 1) % 10 == 0:
                logger.debug(f"Completed {i + 1}/{num_searches} searches")
        
        total_time = time.time() - start_total
        
        # Calculate statistics
        avg_time = statistics.mean(search_times)
        min_time = min(search_times)
        max_time = max(search_times)
        median_time = statistics.median(search_times)
        std_dev = statistics.stdev(search_times) if len(search_times) > 1 else 0.0
        success_rate = successful_searches / num_searches
        target_met = avg_time <= target_time_ms
        
        result = PerformanceResult(
            test_name="Basic Speed Test",
            total_searches=num_searches,
            total_time=total_time,
            average_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            median_time=median_time,
            std_deviation=std_dev,
            success_rate=success_rate,
            target_met=target_met,
            target_time=target_time_ms
        )
        
        logger.info(f"Basic speed test completed: avg={avg_time:.1f}ms, target_met={target_met}")
        return result
    
    def run_cache_performance_test(self) -> Dict[str, Any]:
        """
        Test cache performance and effectiveness
        
        Returns:
            Dictionary with cache performance metrics
        """
        logger.info("Running cache performance test...")
        
        # Get initial cache stats
        initial_stats = self.knowledge_base.get_system_stats()
        initial_optimizer_stats = initial_stats.get('vector_optimizer', {})
        
        # Run searches to populate cache
        cache_warm_searches = 20
        for i in range(cache_warm_searches):
            obs = random.choice(self.test_observations)
            self.knowledge_base.find_matching_step(obs)
        
        # Get post-warm-up stats
        post_warmup_stats = self.knowledge_base.get_system_stats()
        post_optimizer_stats = post_warmup_stats.get('vector_optimizer', {})
        
        # Test search performance with warm cache
        warm_cache_times = []
        for _ in range(10):
            obs = random.choice(self.test_observations)
            start_time = time.time()
            self.knowledge_base.find_matching_step(obs)
            search_time = (time.time() - start_time) * 1000
            warm_cache_times.append(search_time)
        
        # Clear cache and test cold performance
        self.knowledge_base.vector_optimizer.clear_all_cache()
        
        # Reinitialize to simulate cold start
        self.knowledge_base.initialize(precompute_embeddings=False)
        
        cold_cache_times = []
        for _ in range(10):
            obs = random.choice(self.test_observations)
            start_time = time.time()
            self.knowledge_base.find_matching_step(obs)
            search_time = (time.time() - start_time) * 1000
            cold_cache_times.append(search_time)
        
        # Calculate performance improvement
        avg_warm = statistics.mean(warm_cache_times)
        avg_cold = statistics.mean(cold_cache_times)
        improvement = ((avg_cold - avg_warm) / avg_cold) * 100 if avg_cold > 0 else 0
        
        cache_stats = post_optimizer_stats.get('cache_stats', {})
        
        result = {
            "cache_warm_up_searches": cache_warm_searches,
            "average_warm_cache_time_ms": avg_warm,
            "average_cold_cache_time_ms": avg_cold,
            "performance_improvement_percent": improvement,
            "cache_hit_rate": cache_stats.get('hit_rate', 0),
            "total_embeddings": cache_stats.get('total_embeddings', 0),
            "precompute_time": cache_stats.get('precompute_time', 0),
            "cached_tasks": post_optimizer_stats.get('cached_tasks', 0)
        }
        
        logger.info(f"Cache performance test completed: improvement={improvement:.1f}%")
        return result
    
    def run_concurrent_load_test(self, 
                                num_threads: int = 5,
                                searches_per_thread: int = 10) -> Dict[str, Any]:
        """
        Test system performance under concurrent load
        
        Args:
            num_threads: Number of concurrent threads
            searches_per_thread: Number of searches per thread
            
        Returns:
            Dictionary with load test results
        """
        logger.info(f"Running concurrent load test: {num_threads} threads, {searches_per_thread} searches each")
        
        def worker_thread(thread_id: int) -> List[float]:
            """Worker thread function"""
            thread_times = []
            for i in range(searches_per_thread):
                obs = random.choice(self.test_observations)
                start_time = time.time()
                match = self.knowledge_base.find_matching_step(obs)
                search_time = (time.time() - start_time) * 1000
                thread_times.append(search_time)
            return thread_times
        
        # Run concurrent test
        start_total = time.time()
        all_times = []
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Submit all worker threads
            future_to_thread = {
                executor.submit(worker_thread, i): i 
                for i in range(num_threads)
            }
            
            # Collect results
            for future in as_completed(future_to_thread):
                thread_id = future_to_thread[future]
                try:
                    thread_times = future.result()
                    all_times.extend(thread_times)
                    logger.debug(f"Thread {thread_id} completed with avg time: {statistics.mean(thread_times):.1f}ms")
                except Exception as e:
                    logger.error(f"Thread {thread_id} failed: {str(e)}")
        
        total_time = time.time() - start_total
        total_searches = len(all_times)
        
        if all_times:
            avg_time = statistics.mean(all_times)
            min_time = min(all_times)
            max_time = max(all_times)
            median_time = statistics.median(all_times)
            throughput = total_searches / total_time
        else:
            avg_time = min_time = max_time = median_time = throughput = 0
        
        result = {
            "num_threads": num_threads,
            "searches_per_thread": searches_per_thread,
            "total_searches": total_searches,
            "total_time_seconds": total_time,
            "average_time_ms": avg_time,
            "min_time_ms": min_time,
            "max_time_ms": max_time,
            "median_time_ms": median_time,
            "throughput_searches_per_second": throughput,
            "concurrent_performance_degradation": max(0, avg_time - 10)  # Assuming 10ms baseline
        }
        
        logger.info(f"Concurrent load test completed: throughput={throughput:.1f} searches/sec")
        return result
    
    def run_optimization_effectiveness_test(self) -> Dict[str, Any]:
        """
        Test the effectiveness of vector optimization
        
        Returns:
            Dictionary with optimization effectiveness metrics
        """
        logger.info("Running optimization effectiveness test...")
        
        # Test without optimization
        self.knowledge_base.vector_optimizer.enable_precompute = False
        self.knowledge_base.clear_all_caches()
        
        # Reinitialize without precomputation
        self.knowledge_base.initialize(precompute_embeddings=False)
        
        # Test performance without optimization
        unoptimized_times = []
        for _ in range(20):
            obs = random.choice(self.test_observations)
            start_time = time.time()
            self.knowledge_base.find_matching_step(obs)
            search_time = (time.time() - start_time) * 1000
            unoptimized_times.append(search_time)
        
        avg_unoptimized = statistics.mean(unoptimized_times)
        
        # Test with optimization
        self.knowledge_base.vector_optimizer.enable_precompute = True
        self.knowledge_base.clear_all_caches()
        
        # Reinitialize with precomputation
        start_precompute = time.time()
        self.knowledge_base.initialize(precompute_embeddings=True)
        precompute_time = time.time() - start_precompute
        
        # Test performance with optimization
        optimized_times = []
        for _ in range(20):
            obs = random.choice(self.test_observations)
            start_time = time.time()
            self.knowledge_base.find_matching_step(obs)
            search_time = (time.time() - start_time) * 1000
            optimized_times.append(search_time)
        
        avg_optimized = statistics.mean(optimized_times)
        
        # Calculate effectiveness
        speed_improvement = ((avg_unoptimized - avg_optimized) / avg_unoptimized) * 100 if avg_unoptimized > 0 else 0
        
        result = {
            "precompute_time_seconds": precompute_time,
            "average_unoptimized_time_ms": avg_unoptimized,
            "average_optimized_time_ms": avg_optimized,
            "speed_improvement_percent": speed_improvement,
            "optimization_overhead_ms": max(0, avg_optimized - avg_unoptimized),
            "effectiveness_score": max(0, min(100, speed_improvement))
        }
        
        logger.info(f"Optimization effectiveness test completed: improvement={speed_improvement:.1f}%")
        return result
    
    def run_comprehensive_performance_suite(self) -> Dict[str, Any]:
        """
        Run comprehensive performance test suite
        
        Returns:
            Dictionary with all test results
        """
        logger.info("Starting comprehensive performance test suite...")
        
        results = {}
        
        try:
            # Basic speed test
            results["basic_speed_test"] = self.run_basic_speed_test()
            
            # Cache performance test
            results["cache_performance_test"] = self.run_cache_performance_test()
            
            # Concurrent load test
            results["concurrent_load_test"] = self.run_concurrent_load_test()
            
            # Optimization effectiveness test
            results["optimization_effectiveness_test"] = self.run_optimization_effectiveness_test()
            
            # System stats
            results["system_stats"] = self.knowledge_base.get_system_stats()
            
            # Overall assessment
            basic_result = results["basic_speed_test"]
            cache_result = results["cache_performance_test"]
            
            results["overall_assessment"] = {
                "performance_grade": self._calculate_performance_grade(basic_result, cache_result),
                "recommendations": self._generate_recommendations(results),
                "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info("Comprehensive performance test suite completed")
            
        except Exception as e:
            logger.error(f"Performance test suite failed: {str(e)}")
            results["error"] = str(e)
        
        return results
    
    def _calculate_performance_grade(self, basic_result: PerformanceResult, cache_result: Dict) -> str:
        """Calculate overall performance grade"""
        score = 0
        
        # Speed score (40 points)
        if basic_result.average_time <= 5:
            score += 40
        elif basic_result.average_time <= 10:
            score += 30
        elif basic_result.average_time <= 20:
            score += 20
        elif basic_result.average_time <= 50:
            score += 10
        
        # Success rate score (30 points)
        score += int(basic_result.success_rate * 30)
        
        # Cache effectiveness score (30 points)
        improvement = cache_result.get("performance_improvement_percent", 0)
        if improvement >= 50:
            score += 30
        elif improvement >= 25:
            score += 20
        elif improvement >= 10:
            score += 10
        
        # Convert to grade
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        basic_result = results.get("basic_speed_test")
        cache_result = results.get("cache_performance_test", {})
        
        if basic_result and basic_result.average_time > 10:
            recommendations.append("Consider optimizing embedding model or using GPU acceleration")
        
        if cache_result.get("performance_improvement_percent", 0) < 25:
            recommendations.append("Improve caching strategy or increase cache size")
        
        if basic_result and basic_result.success_rate < 0.8:
            recommendations.append("Review and improve semantic matching algorithms")
        
        concurrent_result = results.get("concurrent_load_test", {})
        if concurrent_result.get("concurrent_performance_degradation", 0) > 20:
            recommendations.append("Consider implementing connection pooling or async processing")
        
        if not recommendations:
            recommendations.append("Performance is good! Consider monitoring for regression")
        
        return recommendations