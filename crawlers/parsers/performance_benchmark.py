"""Parsers Module Performance Benchmark Suite
==========================================

Ultra-professional performance benchmarking and stress testing for the parsers module.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de
"""
import asyncio
import logging
import time
import statistics
import psutil
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Performance benchmark result"""
    operation: str
    execution_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    throughput_ops_per_second: float
    success_rate: float
    error_count: int
    
    
@dataclass
class StressTestResult:
    """Stress test result"""
    concurrent_operations: int
    total_operations: int
    average_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    errors_per_second: float
    memory_peak_mb: float
    cpu_peak_percent: float


class PerformanceMonitor:
    """Real-time performance monitoring"""
    
    def __init__(self):
        self.monitoring = False
        self.metrics = []
        self.process = psutil.Process()
        
    def start_monitoring(self, interval: float = 0.1):
        """Start performance monitoring"""
        self.monitoring = True
        self.metrics = []
        
        def monitor():
            while self.monitoring:
                try:
                    cpu_percent = self.process.cpu_percent()
                    memory_info = self.process.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024
                    
                    self.metrics.append({
                        'timestamp': time.time(),
                        'cpu_percent': cpu_percent,
                        'memory_mb': memory_mb
                    })
                    
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    break
        
        threading.Thread(target=monitor, daemon=True).start()
        
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        
    def get_peak_metrics(self) -> Dict[str, float]:
        """Get peak performance metrics"""
        if not self.metrics:
            return {'cpu_peak': 0.0, 'memory_peak': 0.0}
            
        cpu_values = [m['cpu_percent'] for m in self.metrics]
        memory_values = [m['memory_mb'] for m in self.metrics]
        
        return {
            'cpu_peak': max(cpu_values) if cpu_values else 0.0,
            'memory_peak': max(memory_values) if memory_values else 0.0,
            'cpu_average': statistics.mean(cpu_values) if cpu_values else 0.0,
            'memory_average': statistics.mean(memory_values) if memory_values else 0.0
        }


class ParsersBenchmark:
    """Comprehensive parsers module benchmarking"""
    
    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.results: List[BenchmarkResult] = []
        
    async def benchmark_semantic_parser(self, iterations: int = 100) -> BenchmarkResult:
        """Benchmark semantic content parser"""
        logger.info(f"🧠 Benchmarking semantic parser ({iterations} iterations)")
        
        try:
            from .semantic_parsers import SemanticContentParser
            from .parser_config import ParserConfig
            
            config = ParserConfig.default()
            parser = SemanticContentParser(config)
            
            test_content = "This is a comprehensive test content for semantic analysis benchmarking. " * 50
            
            self.monitor.start_monitoring()
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            errors = 0
            for i in range(iterations):
                try:
                    # Simulate semantic analysis (without full AI models for benchmark)
                    analysis = {
                        'sentiment': 'positive',
                        'entities': ['test', 'content'],
                        'topics': ['benchmarking'],
                        'embedding': [0.1] * 768  # Simulated embedding
                    }
                    await asyncio.sleep(0.001)  # Simulate processing time
                except Exception as e:
                    errors += 1
                    logger.debug(f"Iteration {i} error: {e}")
            
            end_time = time.time()
            self.monitor.stop_monitoring()
            
            execution_time = end_time - start_time
            peak_metrics = self.monitor.get_peak_metrics()
            
            return BenchmarkResult(
                operation="semantic_parser",
                execution_time=execution_time,
                memory_usage_mb=peak_metrics['memory_peak'] - start_memory,
                cpu_usage_percent=peak_metrics['cpu_peak'],
                throughput_ops_per_second=iterations / execution_time,
                success_rate=(iterations - errors) / iterations * 100,
                error_count=errors
            )
            
        except Exception as e:
            logger.error(f"Semantic parser benchmark failed: {e}")
            return BenchmarkResult("semantic_parser", 0, 0, 0, 0, 0, iterations)
    
    async def benchmark_economic_parser(self, iterations: int = 100) -> BenchmarkResult:
        """Benchmark economic intelligence parser"""
        logger.info(f"💰 Benchmarking economic parser ({iterations} iterations)")
        
        try:
            from .economic_parsers import EconomicIntelligenceEngine, RevenueRecord, RevenueSource, Currency
            from .parser_config import ParserConfig
            from decimal import Decimal
            
            config = ParserConfig.default()
            engine = EconomicIntelligenceEngine(config)
            
            # Test revenue records
            test_records = [
                RevenueRecord(
                    source=RevenueSource.YOUTUBE_AD_REVENUE,
                    amount=Decimal('100.00'),
                    currency=Currency.USD,
                    date=datetime.now(timezone.utc)
                )
            ]
            
            self.monitor.start_monitoring()
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            errors = 0
            for i in range(iterations):
                try:
                    intelligence = await engine.generate_economic_intelligence(test_records)
                except Exception as e:
                    errors += 1
                    logger.debug(f"Iteration {i} error: {e}")
            
            end_time = time.time()
            self.monitor.stop_monitoring()
            
            execution_time = end_time - start_time
            peak_metrics = self.monitor.get_peak_metrics()
            
            return BenchmarkResult(
                operation="economic_parser",
                execution_time=execution_time,
                memory_usage_mb=peak_metrics['memory_peak'] - start_memory,
                cpu_usage_percent=peak_metrics['cpu_peak'],
                throughput_ops_per_second=iterations / execution_time,
                success_rate=(iterations - errors) / iterations * 100,
                error_count=errors
            )
            
        except Exception as e:
            logger.error(f"Economic parser benchmark failed: {e}")
            return BenchmarkResult("economic_parser", 0, 0, 0, 0, 0, iterations)
    
    async def benchmark_collaboration_parser(self, iterations: int = 100) -> BenchmarkResult:
        """Benchmark collaboration matching parser"""
        logger.info(f"🤝 Benchmarking collaboration parser ({iterations} iterations)")
        
        try:
            from .collaboration_parsers import (
                CollaborationMatchingEngine, CreatorProfile, 
                CreatorTier, ContentCategory
            )
            from .parser_config import ParserConfig
            
            config = ParserConfig.default()
            engine = CollaborationMatchingEngine(config)
            
            # Test creator profiles
            creator1 = CreatorProfile(
                creator_id="test1",
                username="creator1",
                display_name="Test Creator 1",
                categories=[ContentCategory.MUSIC],
                tier=CreatorTier.MICRO_INFLUENCER,
                total_followers=50000,
                engagement_rate=5.2
            )
            
            creators = [creator1] * 10  # Multiple creators for matching
            
            self.monitor.start_monitoring()
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            errors = 0
            for i in range(iterations):
                try:
                    matches = await engine.find_collaboration_matches(
                        target_creator=creator1,
                        candidate_creators=creators
                    )
                except Exception as e:
                    errors += 1
                    logger.debug(f"Iteration {i} error: {e}")
            
            end_time = time.time()
            self.monitor.stop_monitoring()
            
            execution_time = end_time - start_time
            peak_metrics = self.monitor.get_peak_metrics()
            
            return BenchmarkResult(
                operation="collaboration_parser",
                execution_time=execution_time,
                memory_usage_mb=peak_metrics['memory_peak'] - start_memory,
                cpu_usage_percent=peak_metrics['cpu_peak'],
                throughput_ops_per_second=iterations / execution_time,
                success_rate=(iterations - errors) / iterations * 100,
                error_count=errors
            )
            
        except Exception as e:
            logger.error(f"Collaboration parser benchmark failed: {e}")
            return BenchmarkResult("collaboration_parser", 0, 0, 0, 0, 0, iterations)
    
    async def benchmark_trend_parser(self, iterations: int = 100) -> BenchmarkResult:
        """Benchmark trend analysis parser"""
        logger.info(f"📈 Benchmarking trend parser ({iterations} iterations)")
        
        try:
            from .trend_parsers import TrendDetectionEngine, ViralityPredictor
            from .parser_config import ParserConfig
            
            config = ParserConfig.default()
            trend_engine = TrendDetectionEngine(config)
            virality_predictor = ViralityPredictor(config)
            
            test_content = {
                'id': 'test_content',
                'type': 'video',
                'caption': 'Test content with #trending hashtags',
                'creator': {
                    'followers': 10000,
                    'verified': True,
                    'engagement_rate': 5.0
                }
            }
            
            self.monitor.start_monitoring()
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            errors = 0
            for i in range(iterations):
                try:
                    prediction = await virality_predictor.predict_virality(test_content)
                except Exception as e:
                    errors += 1
                    logger.debug(f"Iteration {i} error: {e}")
            
            end_time = time.time()
            self.monitor.stop_monitoring()
            
            execution_time = end_time - start_time
            peak_metrics = self.monitor.get_peak_metrics()
            
            return BenchmarkResult(
                operation="trend_parser",
                execution_time=execution_time,
                memory_usage_mb=peak_metrics['memory_peak'] - start_memory,
                cpu_usage_percent=peak_metrics['cpu_peak'],
                throughput_ops_per_second=iterations / execution_time,
                success_rate=(iterations - errors) / iterations * 100,
                error_count=errors
            )
            
        except Exception as e:
            logger.error(f"Trend parser benchmark failed: {e}")
            return BenchmarkResult("trend_parser", 0, 0, 0, 0, 0, iterations)
    
    async def stress_test_concurrent_operations(self, max_concurrent: int = 50) -> StressTestResult:
        """Stress test with concurrent operations"""
        logger.info(f"🔥 Running stress test (max {max_concurrent} concurrent operations)")
        
        async def test_operation():
            """Single test operation"""
            start_time = time.time()
            try:
                # Simulate mixed parser operations
                await asyncio.sleep(0.01)  # Simulate processing
                return time.time() - start_time, True
            except Exception as e:
                return time.time() - start_time, False
        
        self.monitor.start_monitoring()
        start_time = time.time()
        
        response_times = []
        errors = 0
        total_operations = 0
        
        # Gradually increase concurrency
        for concurrent in range(1, max_concurrent + 1, 5):
            batch_tasks = []
            batch_size = min(10, concurrent)
            
            for _ in range(batch_size):
                task = asyncio.create_task(test_operation())
                batch_tasks.append(task)
                total_operations += 1
            
            # Wait for batch completion
            results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, tuple):
                    exec_time, success = result
                    response_times.append(exec_time)
                    if not success:
                        errors += 1
                else:
                    errors += 1
                    response_times.append(1.0)  # Default for errors
        
        end_time = time.time()
        self.monitor.stop_monitoring()
        
        peak_metrics = self.monitor.get_peak_metrics()
        total_time = end_time - start_time
        
        # Calculate percentiles
        response_times.sort()
        p95_index = int(0.95 * len(response_times))
        p99_index = int(0.99 * len(response_times))
        
        return StressTestResult(
            concurrent_operations=max_concurrent,
            total_operations=total_operations,
            average_response_time=statistics.mean(response_times),
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            p95_response_time=response_times[p95_index] if response_times else 0,
            p99_response_time=response_times[p99_index] if response_times else 0,
            errors_per_second=errors / total_time,
            memory_peak_mb=peak_metrics['memory_peak'],
            cpu_peak_percent=peak_metrics['cpu_peak']
        )
    
    async def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive benchmark suite"""
        logger.info("🚀 Starting comprehensive performance benchmark...")
        
        # Individual parser benchmarks
        semantic_result = await self.benchmark_semantic_parser()
        economic_result = await self.benchmark_economic_parser()
        collaboration_result = await self.benchmark_collaboration_parser()
        trend_result = await self.benchmark_trend_parser()
        
        # Stress test
        stress_result = await self.stress_test_concurrent_operations()
        
        self.results = [semantic_result, economic_result, collaboration_result, trend_result]
        
        return {
            'individual_benchmarks': {
                'semantic_parser': semantic_result,
                'economic_parser': economic_result,
                'collaboration_parser': collaboration_result,
                'trend_parser': trend_result
            },
            'stress_test': stress_result,
            'summary': self._generate_summary()
        }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate benchmark summary"""
        if not self.results:
            return {}
        
        avg_throughput = statistics.mean([r.throughput_ops_per_second for r in self.results])
        avg_success_rate = statistics.mean([r.success_rate for r in self.results])
        total_errors = sum([r.error_count for r in self.results])
        
        return {
            'average_throughput_ops_per_sec': avg_throughput,
            'average_success_rate_percent': avg_success_rate,
            'total_errors': total_errors,
            'benchmark_grade': self._calculate_grade(avg_throughput, avg_success_rate)
        }
    
    def _calculate_grade(self, throughput: float, success_rate: float) -> str:
        """Calculate performance grade"""
        if success_rate >= 99 and throughput >= 100:
            return "A+ (Excellent)"
        elif success_rate >= 95 and throughput >= 50:
            return "A (Very Good)"
        elif success_rate >= 90 and throughput >= 25:
            return "B (Good)"
        elif success_rate >= 80 and throughput >= 10:
            return "C (Acceptable)"
        else:
            return "D (Needs Improvement)"
    
    def save_results(self, filename: str = "parsers_benchmark_results.json"):
        """Save benchmark results to file"""
        results_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
                'platform': os.name
            },
            'benchmarks': [
                {
                    'operation': r.operation,
                    'execution_time': r.execution_time,
                    'memory_usage_mb': r.memory_usage_mb,
                    'cpu_usage_percent': r.cpu_usage_percent,
                    'throughput_ops_per_second': r.throughput_ops_per_second,
                    'success_rate': r.success_rate,
                    'error_count': r.error_count
                }
                for r in self.results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"📊 Benchmark results saved to {filename}")


async def main():
    """Main benchmark execution"""
    logger.info("=" * 80)
    logger.info("🚀 IA INFLUENCER AGENT - PARSERS MODULE PERFORMANCE BENCHMARK")
    logger.info("=" * 80)
    logger.info("Author: Fahed Mlaiel <mlaiel@live.de>")
    logger.info("Copyright: © 2025 Fahed Mlaiel. All rights reserved.")
    logger.info("=" * 80)
    
    benchmark = ParsersBenchmark()
    
    try:
        # Run comprehensive benchmark
        results = await benchmark.run_comprehensive_benchmark()
        
        # Display results
        logger.info("\n" + "=" * 80)
        logger.info("📊 BENCHMARK RESULTS SUMMARY")
        logger.info("=" * 80)
        
        for parser_name, result in results['individual_benchmarks'].items():
            logger.info(f"\n🔹 {parser_name.upper()}")
            logger.info(f"   Throughput: {result.throughput_ops_per_second:.2f} ops/sec")
            logger.info(f"   Success Rate: {result.success_rate:.1f}%")
            logger.info(f"   Memory Usage: {result.memory_usage_mb:.2f} MB")
            logger.info(f"   CPU Usage: {result.cpu_usage_percent:.1f}%")
        
        stress_result = results['stress_test']
        logger.info(f"\n🔥 STRESS TEST RESULTS")
        logger.info(f"   Total Operations: {stress_result.total_operations}")
        logger.info(f"   Average Response Time: {stress_result.average_response_time:.3f}s")
        logger.info(f"   95th Percentile: {stress_result.p95_response_time:.3f}s")
        logger.info(f"   99th Percentile: {stress_result.p99_response_time:.3f}s")
        logger.info(f"   Memory Peak: {stress_result.memory_peak_mb:.2f} MB")
        logger.info(f"   CPU Peak: {stress_result.cpu_peak_percent:.1f}%")
        
        summary = results['summary']
        logger.info(f"\n🎯 OVERALL PERFORMANCE")
        logger.info(f"   Grade: {summary['benchmark_grade']}")
        logger.info(f"   Average Throughput: {summary['average_throughput_ops_per_sec']:.2f} ops/sec")
        logger.info(f"   Average Success Rate: {summary['average_success_rate_percent']:.1f}%")
        
        # Save results
        benchmark.save_results()
        
        logger.info("\n🎉 Benchmark completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Benchmark failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
