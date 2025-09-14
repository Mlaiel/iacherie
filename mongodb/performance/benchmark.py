"""
Benchmark module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""MongoDB Performance Benchmarking Script
========================================

Comprehensive performance benchmarking for MongoDB operations.
Measures and reports on all critical performance metrics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import time
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List
import statistics
import psutil
from dataclasses import dataclass, asdict

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import motor.motor_asyncio
    import pymongo
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("Warning: MongoDB drivers not available. Using simulation mode.")

@dataclass
class BenchmarkResult:
    """Performance benchmark result."""
    test_name: str
    operation_type: str
    duration_seconds: float
    operations_per_second: float
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    cpu_usage_percent: float
    memory_usage_mb: float
    success_rate: float
    error_count: int
    total_operations: int
    timestamp: str

@dataclass
class BenchmarkConfig:
    """Benchmark configuration."""
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "benchmark_test"
    collection_name: str = "test_collection"
    warmup_operations: int = 100
    test_operations: int = 1000
    concurrent_clients: int = 10
    document_size_bytes: int = 1024
    batch_size: int = 100
    test_duration_seconds: int = 60
    cleanup_after_test: bool = True

class MongoDBBenchmark:
    """MongoDB performance benchmark suite."""
    
    def __init__(self, config -> None: BenchmarkConfig) -> None:
        self.config = config
        self.results: List[BenchmarkResult] = []
        self.client = None
        self.database = None
        self.collection = None
    
    async def setup(self) -> None:
        """Setup benchmark environment."""
        global MONGODB_AVAILABLE
        print("🚀 Setting up MongoDB benchmark environment...")
        
        if MONGODB_AVAILABLE:
            try:
                self.client = motor.motor_asyncio.AsyncIOMotorClient(self.config.mongodb_url)
                self.database = self.client[self.config.database_name]
                self.collection = self.database[self.config.collection_name]
                
                # Test connection
                await self.client.admin.command('ping')
                print("✅ MongoDB connection established")
                
                # Create indexes for testing
                await self._create_test_indexes()
                
            except Exception as e:
                print(f"⚠️  MongoDB connection failed: {e}")
                print("Running in simulation mode...")
                MONGODB_AVAILABLE = False
        
        if not MONGODB_AVAILABLE:
            print("📝 Running in simulation mode (no actual MongoDB operations)")
    
    async def cleanup(self) -> None:
        """Cleanup benchmark environment."""
        global MONGODB_AVAILABLE
        if self.config.cleanup_after_test and MONGODB_AVAILABLE and self.client:
            try:
                await self.client.drop_database(self.config.database_name)
                await self.client.close()
                print("🧹 Benchmark environment cleaned up")
            except Exception as e:
                print(f"⚠️  Cleanup error: {e}")
    
    async def _create_test_indexes(self) -> None:
        """Create indexes for performance testing."""
        global MONGODB_AVAILABLE
        if not MONGODB_AVAILABLE:
            return
            
        indexes = [
            [("test_field", 1)],
            [("created_at", -1)],
            [("test_field", 1), ("category", 1)],
            [("tags", 1)],
            [("metadata.score", -1)]
        ]
        
        for index in indexes:
            try:
                await self.collection.create_index(index)
            except Exception as e:
                print(f"Index creation warning: {e}")
    
    def _generate_test_document(self, doc_id: int) -> Dict[str, Any]:
        """Generate a test document."""
        import random
        import string
        
        # Generate content to reach target size
        content_size = max(100, self.config.document_size_bytes - 500)  # Reserve space for other fields
        content = ''.join(random.choices(string.ascii_letters + string.digits, k=content_size))
        
        return {
            "_id": doc_id,
            "test_field": f"test_value_{doc_id}",
            "category": random.choice(["A", "B", "C", "D"]),
            "score": random.randint(1, 100),
            "tags": [f"tag_{i}" for i in range(random.randint(1, 5))],
            "created_at": datetime.now(timezone.utc),
            "metadata": {
                "version": "1.0",
                "score": random.uniform(0.0, 1.0),
                "active": random.choice([True, False])
            },
            "content": content
        }
    
    async def _measure_operation(self, operation_func, *args, **kwargs) -> None:
        """Measure operation performance."""
        start_cpu = psutil.cpu_percent()
        start_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
        
        start_time = time.perf_counter()
        
        try:
            result = await operation_func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        
        end_time = time.perf_counter()
        
        end_cpu = psutil.cpu_percent()
        end_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
        
        return {
            'result': result,
            'success': success,
            'error': error,
            'duration': end_time - start_time,
            'cpu_usage': max(0, end_cpu - start_cpu),
            'memory_delta': end_memory - start_memory
        }
    
    async def benchmark_insert_performance(self) -> None:
        """Benchmark insert operations."""
        global MONGODB_AVAILABLE
        print("📊 Benchmarking INSERT operations...")
        
        latencies = []
        errors = 0
        total_ops = self.config.test_operations
        
        start_time = time.perf_counter()
        
        for i in range(total_ops):
            document = self._generate_test_document(i)
            
            if MONGODB_AVAILABLE:
                measurement = await self._measure_operation(
                    self.collection.insert_one, document
                )
            else:
                # Simulate operation
                await asyncio.sleep(0.001)  # 1ms simulated latency
                measurement = {
                    'success': True,
                    'duration': 0.001,
                    'cpu_usage': 0.1,
                    'memory_delta': 0.01
                }
            
            latencies.append(measurement['duration'] * 1000)  # Convert to ms
            if not measurement['success']:
                errors += 1
        
        end_time = time.perf_counter()
        total_duration = end_time - start_time
        
        result = BenchmarkResult(
            test_name="Insert Performance",
            operation_type="INSERT",
            duration_seconds=total_duration,
            operations_per_second=total_ops / total_duration,
            avg_latency_ms=statistics.mean(latencies),
            min_latency_ms=min(latencies),
            max_latency_ms=max(latencies),
            p95_latency_ms=statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies),
            p99_latency_ms=statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies),
            cpu_usage_percent=psutil.cpu_percent(),
            memory_usage_mb=psutil.virtual_memory().used / 1024 / 1024,
            success_rate=(total_ops - errors) / total_ops * 100,
            error_count=errors,
            total_operations=total_ops,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.results.append(result)
        print(f"  ✅ Completed: {result.operations_per_second:.2f} ops/sec, avg latency: {result.avg_latency_ms:.2f}ms")
    
    async def benchmark_query_performance(self) -> None:
        """Benchmark query operations."""
        global MONGODB_AVAILABLE
        print("📊 Benchmarking QUERY operations...")
        
        # First insert some test data if not in simulation mode
        if MONGODB_AVAILABLE:
            print("  📝 Preparing test data...")
            test_docs = [self._generate_test_document(i) for i in range(1000)]
            await self.collection.insert_many(test_docs)
        
        latencies = []
        errors = 0
        total_ops = self.config.test_operations
        
        start_time = time.perf_counter()
        
        for i in range(total_ops):
            query = {"test_field": f"test_value_{i % 1000}"}
            
            if MONGODB_AVAILABLE:
                measurement = await self._measure_operation(
                    self.collection.find_one, query
                )
            else:
                # Simulate operation
                await asyncio.sleep(0.0005)  # 0.5ms simulated latency
                measurement = {
                    'success': True,
                    'duration': 0.0005,
                    'cpu_usage': 0.05,
                    'memory_delta': 0.001
                }
            
            latencies.append(measurement['duration'] * 1000)
            if not measurement['success']:
                errors += 1
        
        end_time = time.perf_counter()
        total_duration = end_time - start_time
        
        result = BenchmarkResult(
            test_name="Query Performance",
            operation_type="QUERY",
            duration_seconds=total_duration,
            operations_per_second=total_ops / total_duration,
            avg_latency_ms=statistics.mean(latencies),
            min_latency_ms=min(latencies),
            max_latency_ms=max(latencies),
            p95_latency_ms=statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies),
            p99_latency_ms=statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies),
            cpu_usage_percent=psutil.cpu_percent(),
            memory_usage_mb=psutil.virtual_memory().used / 1024 / 1024,
            success_rate=(total_ops - errors) / total_ops * 100,
            error_count=errors,
            total_operations=total_ops,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.results.append(result)
        print(f"  ✅ Completed: {result.operations_per_second:.2f} ops/sec, avg latency: {result.avg_latency_ms:.2f}ms")
    
    async def benchmark_update_performance(self) -> None:
        """Benchmark update operations."""
        global MONGODB_AVAILABLE
        print("📊 Benchmarking UPDATE operations...")
        
        latencies = []
        errors = 0
        total_ops = self.config.test_operations
        
        start_time = time.perf_counter()
        
        for i in range(total_ops):
            query = {"test_field": f"test_value_{i % 1000}"}
            update = {"$set": {"last_updated": datetime.now(timezone.utc), "update_count": i}}
            
            if MONGODB_AVAILABLE:
                measurement = await self._measure_operation(
                    self.collection.update_one, query, update
                )
            else:
                # Simulate operation
                await asyncio.sleep(0.002)  # 2ms simulated latency
                measurement = {
                    'success': True,
                    'duration': 0.002,
                    'cpu_usage': 0.2,
                    'memory_delta': 0.005
                }
            
            latencies.append(measurement['duration'] * 1000)
            if not measurement['success']:
                errors += 1
        
        end_time = time.perf_counter()
        total_duration = end_time - start_time
        
        result = BenchmarkResult(
            test_name="Update Performance",
            operation_type="UPDATE",
            duration_seconds=total_duration,
            operations_per_second=total_ops / total_duration,
            avg_latency_ms=statistics.mean(latencies),
            min_latency_ms=min(latencies),
            max_latency_ms=max(latencies),
            p95_latency_ms=statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies),
            p99_latency_ms=statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies),
            cpu_usage_percent=psutil.cpu_percent(),
            memory_usage_mb=psutil.virtual_memory().used / 1024 / 1024,
            success_rate=(total_ops - errors) / total_ops * 100,
            error_count=errors,
            total_operations=total_ops,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.results.append(result)
        print(f"  ✅ Completed: {result.operations_per_second:.2f} ops/sec, avg latency: {result.avg_latency_ms:.2f}ms")
    
    async def benchmark_aggregation_performance(self) -> None:
        """Benchmark aggregation operations."""
        global MONGODB_AVAILABLE
        print("📊 Benchmarking AGGREGATION operations...")
        
        latencies = []
        errors = 0
        total_ops = min(100, self.config.test_operations // 10)  # Fewer aggregation operations
        
        start_time = time.perf_counter()
        
        for i in range(total_ops):
            pipeline = [
                {"$match": {"category": {"$in": ["A", "B"]}}},
                {"$group": {"_id": "$category", "count": {"$sum": 1}, "avg_score": {"$avg": "$score"}}},
                {"$sort": {"count": -1}}
            ]
            
            if MONGODB_AVAILABLE:
                async def run_aggregation() -> None:
                    cursor = self.collection.aggregate(pipeline)
                    return await cursor.to_list(length=None)
                
                measurement = await self._measure_operation(run_aggregation)
            else:
                # Simulate operation
                await asyncio.sleep(0.01)  # 10ms simulated latency
                measurement = {
                    'success': True,
                    'duration': 0.01,
                    'cpu_usage': 0.5,
                    'memory_delta': 0.1
                }
            
            latencies.append(measurement['duration'] * 1000)
            if not measurement['success']:
                errors += 1
        
        end_time = time.perf_counter()
        total_duration = end_time - start_time
        
        result = BenchmarkResult(
            test_name="Aggregation Performance",
            operation_type="AGGREGATION",
            duration_seconds=total_duration,
            operations_per_second=total_ops / total_duration,
            avg_latency_ms=statistics.mean(latencies),
            min_latency_ms=min(latencies),
            max_latency_ms=max(latencies),
            p95_latency_ms=statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies),
            p99_latency_ms=statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies),
            cpu_usage_percent=psutil.cpu_percent(),
            memory_usage_mb=psutil.virtual_memory().used / 1024 / 1024,
            success_rate=(total_ops - errors) / total_ops * 100,
            error_count=errors,
            total_operations=total_ops,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.results.append(result)
        print(f"  ✅ Completed: {result.operations_per_second:.2f} ops/sec, avg latency: {result.avg_latency_ms:.2f}ms")
    
    async def run_all_benchmarks(self) -> None:
        """Run all performance benchmarks."""
        print("🏃‍♂️ Starting MongoDB Performance Benchmarks")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Run benchmarks
            await self.benchmark_insert_performance()
            await self.benchmark_query_performance()
            await self.benchmark_update_performance()
            await self.benchmark_aggregation_performance()
        
        finally:
            await self.cleanup()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive benchmark report."""
        if not self.results:
            return {"error": "No benchmark results available"}
        
        # Calculate overall statistics
        total_operations = sum(r.total_operations for r in self.results)
        avg_ops_per_sec = statistics.mean([r.operations_per_second for r in self.results])
        avg_latency = statistics.mean([r.avg_latency_ms for r in self.results])
        overall_success_rate = statistics.mean([r.success_rate for r in self.results])
        
        report = {
            "benchmark_summary": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_operations": total_operations,
                "avg_operations_per_second": avg_ops_per_sec,
                "avg_latency_ms": avg_latency,
                "overall_success_rate": overall_success_rate,
                "mongodb_available": MONGODB_AVAILABLE
            },
            "configuration": asdict(self.config),
            "results": [asdict(result) for result in self.results],
            "performance_analysis": self._analyze_performance()
        }
        
        return report
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance results and provide insights."""
        analysis = {
            "performance_grade": "A",
            "bottlenecks": [],
            "recommendations": [],
            "alerts": []
        }
        
        # Analyze each operation type
        for result in self.results:
            # Check for performance issues
            if result.avg_latency_ms > 100:
                analysis["bottlenecks"].append(f"{result.operation_type} latency is high ({result.avg_latency_ms:.2f}ms)")
                analysis["recommendations"].append(f"Optimize {result.operation_type} operations with better indexing")
            
            if result.operations_per_second < 100:
                analysis["bottlenecks"].append(f"{result.operation_type} throughput is low ({result.operations_per_second:.2f} ops/sec)")
                analysis["recommendations"].append(f"Consider connection pooling for {result.operation_type} operations")
            
            if result.success_rate < 99:
                analysis["alerts"].append(f"{result.operation_type} has {100 - result.success_rate:.2f}% error rate")
        
        # Overall performance grade
        avg_latency = statistics.mean([r.avg_latency_ms for r in self.results])
        avg_throughput = statistics.mean([r.operations_per_second for r in self.results])
        
        if avg_latency < 10 and avg_throughput > 1000:
            analysis["performance_grade"] = "A+"
        elif avg_latency < 50 and avg_throughput > 500:
            analysis["performance_grade"] = "A"
        elif avg_latency < 100 and avg_throughput > 100:
            analysis["performance_grade"] = "B"
        else:
            analysis["performance_grade"] = "C"
        
        return analysis
    
    def save_report(self, filename -> None: str = None) -> None:
        """Save benchmark report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mongodb_benchmark_report_{timestamp}.json"
        
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📋 Benchmark report saved to: {filename}")
        return filename
    
    def print_summary(self) -> None:
        """Print benchmark summary."""
        if not self.results:
            print("❌ No benchmark results to display")
            return
        
        print("\n" + "="*60)
        print("📊 MONGODB PERFORMANCE BENCHMARK SUMMARY")
        print("="*60)
        
        for result in self.results:
            print(f"\n🔍 {result.test_name}")
            print(f"   Operations/sec: {result.operations_per_second:>10.2f}")
            print(f"   Avg Latency:    {result.avg_latency_ms:>10.2f} ms")
            print(f"   P95 Latency:    {result.p95_latency_ms:>10.2f} ms")
            print(f"   Success Rate:   {result.success_rate:>10.1f} %")
        
        # Overall analysis
        analysis = self._analyze_performance()
        print(f"\n🎯 Overall Performance Grade: {analysis['performance_grade']}")
        
        if analysis['bottlenecks']:
            print("\n⚠️  Performance Bottlenecks:")
            for bottleneck in analysis['bottlenecks']:
                print(f"   • {bottleneck}")
        
        if analysis['recommendations']:
            print("\n💡 Recommendations:")
            for rec in analysis['recommendations']:
                print(f"   • {rec}")
        
        if analysis['alerts']:
            print("\n🚨 Alerts:")
            for alert in analysis['alerts']:
                print(f"   • {alert}")
        
        # Add MongoDB availability note
        global MONGODB_AVAILABLE
        if not MONGODB_AVAILABLE:
            print(f"\n📝 Note: This benchmark ran in simulation mode (MongoDB not available)")
            print("   Install MongoDB and motor driver for real performance testing.")

async def main() -> None:
    """Main benchmark execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MongoDB Performance Benchmark")
    parser.add_argument("--url", default="mongodb://localhost:27017", help="MongoDB connection URL")
    parser.add_argument("--operations", type=int, default=1000, help="Number of test operations")
    parser.add_argument("--size", type=int, default=1024, help="Document size in bytes")
    parser.add_argument("--output", help="Output report filename")
    parser.add_argument("--quick", action="store_true", help="Run quick benchmark (fewer operations)")
    
    args = parser.parse_args()
    
    # Configure benchmark
    config = BenchmarkConfig(
        mongodb_url=args.url,
        test_operations=100 if args.quick else args.operations,
        document_size_bytes=args.size
    )
    
    # Run benchmark
    benchmark = MongoDBBenchmark(config)
    await benchmark.run_all_benchmarks()
    
    # Display and save results
    benchmark.print_summary()
    report_file = benchmark.save_report(args.output)
    
    print(f"\n🎉 Benchmark completed! Report saved to: {report_file}")

if __name__ == "__main__":
    asyncio.run(main())