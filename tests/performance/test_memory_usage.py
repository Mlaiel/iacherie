"""
Memory Usage Performance Tests

Tests for memory consumption, memory leaks, and memory efficiency.
"""

import pytest
import asyncio
import time
import gc
import statistics
from typing import List, Dict, Any, Optional
import sys


class MemoryMetrics:
    """Memory usage metrics collection."""
    
    def __init__(self):
        self.memory_samples: List[Dict[str, Any]] = []
        self.peak_memory_mb: float = 0
        self.start_memory_mb: float = 0
        self.end_memory_mb: float = 0
        self.start_time: float = 0
        self.end_time: float = 0
        self.gc_collections: int = 0
    
    def start_monitoring(self):
        """Start memory monitoring."""
        self.start_time = time.time()
        self.start_memory_mb = self._get_memory_usage()
        self.gc_collections = sum(gc.get_count())
        gc.collect()  # Clean start
    
    def stop_monitoring(self):
        """Stop memory monitoring."""
        self.end_time = time.time()
        gc.collect()  # Clean end
        self.end_memory_mb = self._get_memory_usage()
    
    def sample_memory(self, operation: str = "sample", metadata: Optional[Dict] = None):
        """Take a memory usage sample."""
        current_memory = self._get_memory_usage()
        self.peak_memory_mb = max(self.peak_memory_mb, current_memory)
        
        sample = {
            "timestamp": time.time(),
            "memory_mb": current_memory,
            "operation": operation,
            "metadata": metadata or {}
        }
        self.memory_samples.append(sample)
        
        return current_memory
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            # Fallback to approximation using sys.getsizeof
            # This is less accurate but works without psutil
            return sys.getsizeof(gc.get_objects()) / 1024 / 1024
    
    def get_summary(self) -> Dict[str, Any]:
        """Get memory usage summary."""
        if not self.memory_samples:
            return {"error": "No memory samples recorded"}
        
        memory_values = [sample["memory_mb"] for sample in self.memory_samples]
        duration = self.end_time - self.start_time
        
        # Memory leak detection
        memory_delta = self.end_memory_mb - self.start_memory_mb
        
        # Memory stability (variance in usage)
        memory_variance = statistics.variance(memory_values) if len(memory_values) > 1 else 0
        
        return {
            "duration_seconds": duration,
            "start_memory_mb": self.start_memory_mb,
            "end_memory_mb": self.end_memory_mb,
            "peak_memory_mb": self.peak_memory_mb,
            "memory_delta_mb": memory_delta,
            "memory_variance": memory_variance,
            "sample_count": len(self.memory_samples),
            "memory_stats": {
                "min_mb": min(memory_values),
                "max_mb": max(memory_values),
                "mean_mb": statistics.mean(memory_values),
                "median_mb": statistics.median(memory_values)
            },
            "gc_collections_during_test": sum(gc.get_count()) - self.gc_collections,
            "memory_efficiency_mb_per_second": memory_delta / duration if duration > 0 else 0
        }


class TestMemoryUsageBaseline:
    """Baseline memory usage tests."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_idle_memory_usage(self):
        """Test memory usage during idle operations."""
        metrics = MemoryMetrics()
        metrics.start_monitoring()
        
        # Test parameters
        idle_duration = 10  # 10 seconds
        max_idle_memory_growth_mb = 5
        sample_interval = 1  # Sample every second
        
        # Take baseline sample
        metrics.sample_memory("baseline")
        
        # Idle period with periodic sampling
        samples_taken = 0
        start_time = time.time()
        
        while time.time() - start_time < idle_duration:
            await asyncio.sleep(sample_interval)
            metrics.sample_memory(f"idle_sample_{samples_taken}")
            samples_taken += 1
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Idle memory assertions
        assert summary["memory_delta_mb"] <= max_idle_memory_growth_mb
        assert summary["memory_variance"] <= 10.0  # Low variance during idle
        assert summary["sample_count"] >= idle_duration  # Adequate sampling
        
        print(f"Idle Memory Usage: {summary}")
    
    @pytest.mark.performance
    def test_startup_memory_baseline(self):
        """Test memory usage baseline at application startup."""
        metrics = MemoryMetrics()
        metrics.start_monitoring()
        
        max_startup_memory_mb = 100  # 100MB startup limit
        
        # Simulate application startup components
        startup_components = [
            "configuration_loading",
            "database_connection_pool",
            "cache_initialization", 
            "route_registration",
            "middleware_setup"
        ]
        
        for component in startup_components:
            # Simulate component initialization
            component_data = {
                "component": component,
                "config": {"setting_" + str(i): f"value_{i}" for i in range(10)},
                "metadata": {"initialized": True, "timestamp": time.time()}
            }
            
            metrics.sample_memory(f"startup_{component}", {"component": component})
            time.sleep(0.1)  # Brief initialization delay
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Startup memory assertions
        assert summary["peak_memory_mb"] <= max_startup_memory_mb
        assert summary["memory_delta_mb"] >= 0  # Should not decrease during startup
        
        print(f"Startup Memory Baseline: {summary}")
        
        # Component memory breakdown
        for sample in metrics.memory_samples:
            if sample["operation"].startswith("startup_"):
                component = sample["operation"].replace("startup_", "")
                print(f"  {component}: {sample['memory_mb']:.1f}MB")


class TestMemoryLeakDetection:
    """Memory leak detection tests."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_repeated_operations_memory_leak(self):
        """Test for memory leaks in repeated operations."""
        metrics = MemoryMetrics()
        metrics.start_monitoring()
        
        # Test parameters
        operation_cycles = 100
        max_memory_growth_per_cycle_kb = 50  # 50KB per cycle max
        leak_detection_threshold_mb = 5  # 5MB total growth threshold
        
        async def memory_intensive_operation(cycle_id: int):
            """Operation that should not leak memory."""
            # Create temporary data structures
            temp_data = []
            
            # Allocate memory
            for i in range(100):
                item = {
                    "id": f"{cycle_id}_{i}",
                    "data": "x" * 1000,  # 1KB per item
                    "metadata": {
                        "cycle": cycle_id,
                        "sequence": i,
                        "timestamp": time.time()
                    }
                }
                temp_data.append(item)
            
            # Simulate processing
            await asyncio.sleep(0.01)  # 10ms processing
            
            # Process data
            processed_count = len(temp_data)
            checksum = sum(len(str(item)) for item in temp_data)
            
            # Cleanup (critical for leak prevention)
            del temp_data
            
            return {
                "cycle_id": cycle_id,
                "processed_count": processed_count,
                "checksum": checksum
            }
        
        # Execute repeated operations with memory sampling
        baseline_memory = metrics.sample_memory("baseline")
        
        for cycle in range(operation_cycles):
            # Execute operation
            result = await memory_intensive_operation(cycle)
            
            # Sample memory periodically
            if cycle % 10 == 0:
                current_memory = metrics.sample_memory(
                    f"cycle_{cycle}",
                    {"cycle": cycle, "processed_count": result["processed_count"]}
                )
                
                # Check for gradual memory growth
                memory_growth = current_memory - baseline_memory
                if memory_growth > leak_detection_threshold_mb:
                    print(f"Warning: Potential memory leak detected at cycle {cycle}: +{memory_growth:.1f}MB")
            
            # Occasional garbage collection to help detect real leaks
            if cycle % 25 == 0:
                gc.collect()
        
        # Final memory check
        final_memory = metrics.sample_memory("final")
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Memory leak assertions
        total_growth = summary["memory_delta_mb"]
        growth_per_cycle = total_growth / operation_cycles
        
        assert total_growth <= leak_detection_threshold_mb
        assert growth_per_cycle * 1024 <= max_memory_growth_per_cycle_kb  # Convert to KB
        
        print(f"Memory Leak Test: {summary}")
        print(f"Growth per cycle: {growth_per_cycle * 1024:.1f}KB")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_long_running_process_memory_stability(self):
        """Test memory stability in long-running processes."""
        metrics = MemoryMetrics()
        metrics.start_monitoring()
        
        # Test parameters
        test_duration_minutes = 3  # 3 minutes for testing
        operation_interval_seconds = 5
        max_memory_variance = 20.0  # MB variance
        max_total_growth_mb = 10
        
        async def periodic_operation(operation_id: int):
            """Periodic operation that should maintain stable memory."""
            # Simulate regular application work
            work_data = []
            
            # Create working set
            for i in range(50):
                item = {
                    "operation_id": operation_id,
                    "item_id": i,
                    "payload": "data_" * 50,  # ~200 bytes
                    "timestamp": time.time()
                }
                work_data.append(item)
            
            # Process work
            await asyncio.sleep(0.02)  # 20ms processing
            
            # Simulate result generation
            result = {
                "operation_id": operation_id,
                "processed_items": len(work_data),
                "total_size": sum(len(str(item)) for item in work_data)
            }
            
            # Cleanup
            del work_data
            
            return result
        
        # Run long-term stability test
        test_duration_seconds = test_duration_minutes * 60
        operations_count = int(test_duration_seconds / operation_interval_seconds)
        
        start_time = time.time()
        operation_id = 0
        
        while time.time() - start_time < test_duration_seconds:
            # Execute periodic operation
            result = await periodic_operation(operation_id)
            
            # Sample memory
            current_memory = metrics.sample_memory(
                f"operation_{operation_id}",
                {"operation_id": operation_id, "processed_items": result["processed_items"]}
            )
            
            # Progress reporting
            if operation_id % 10 == 0:
                elapsed = time.time() - start_time
                progress = (elapsed / test_duration_seconds) * 100
                print(f"    Long-running test progress: {progress:.1f}% - Memory: {current_memory:.1f}MB")
            
            operation_id += 1
            
            # Wait for next operation
            await asyncio.sleep(operation_interval_seconds)
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Long-running stability assertions
        assert summary["memory_variance"] <= max_memory_variance
        assert abs(summary["memory_delta_mb"]) <= max_total_growth_mb
        assert summary["sample_count"] >= operations_count * 0.8  # Allow some variance
        
        print(f"Long-running Memory Stability: {summary}")


class TestMemoryEfficiency:
    """Memory efficiency and optimization tests."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_large_dataset_memory_efficiency(self):
        """Test memory efficiency when processing large datasets."""
        metrics = MemoryMetrics()
        metrics.start_monitoring()
        
        # Test parameters
        dataset_sizes = [1000, 5000, 10000, 20000]
        max_memory_per_record_kb = 2  # 2KB per record max
        memory_cleanup_efficiency = 0.9  # 90% memory should be freed after processing
        
        for dataset_size in dataset_sizes:
            print(f"    Testing dataset size: {dataset_size} records")
            
            # Measure memory before dataset processing
            pre_processing_memory = metrics.sample_memory(f"pre_dataset_{dataset_size}")
            
            async def process_large_dataset(size: int):
                """Process dataset with memory-efficient approach."""
                # Process in batches to maintain memory efficiency
                batch_size = 500
                processed_records = 0
                
                for batch_start in range(0, size, batch_size):
                    batch_end = min(batch_start + batch_size, size)
                    batch = []
                    
                    # Create batch data
                    for i in range(batch_start, batch_end):
                        record = {
                            "id": i,
                            "data": f"record_{i}_{'x' * 100}",  # ~120 bytes per record
                            "metadata": {
                                "batch": batch_start // batch_size,
                                "processed": False
                            }
                        }
                        batch.append(record)
                    
                    # Process batch
                    for record in batch:
                        record["metadata"]["processed"] = True
                        record["processed_at"] = time.time()
                    
                    processed_records += len(batch)
                    
                    # Cleanup batch to free memory
                    del batch
                    
                    # Brief processing pause
                    await asyncio.sleep(0.001)
                
                return processed_records
            
            # Process dataset
            processed_count = await process_large_dataset(dataset_size)
            
            # Measure memory after processing
            post_processing_memory = metrics.sample_memory(
                f"post_dataset_{dataset_size}",
                {"dataset_size": dataset_size, "processed_count": processed_count}
            )
            
            # Memory efficiency analysis
            memory_used_during_processing = post_processing_memory - pre_processing_memory
            memory_per_record_kb = (memory_used_during_processing * 1024) / dataset_size
            
            # Force garbage collection and measure cleanup
            gc.collect()
            await asyncio.sleep(0.1)  # Allow cleanup
            
            cleanup_memory = metrics.sample_memory(f"cleanup_dataset_{dataset_size}")
            memory_freed = post_processing_memory - cleanup_memory
            cleanup_efficiency = memory_freed / memory_used_during_processing if memory_used_during_processing > 0 else 1
            
            # Efficiency assertions per dataset
            assert memory_per_record_kb <= max_memory_per_record_kb
            assert cleanup_efficiency >= memory_cleanup_efficiency
            
            print(f"      Memory per record: {memory_per_record_kb:.2f}KB, "
                  f"Cleanup efficiency: {cleanup_efficiency:.1%}")
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Overall efficiency assertions
        assert summary["memory_delta_mb"] <= 50  # Total growth should be reasonable
        
        print(f"Large Dataset Memory Efficiency: {summary}")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_memory_usage(self):
        """Test memory usage under concurrent operations."""
        metrics = MemoryMetrics()
        metrics.start_monitoring()
        
        # Test parameters
        concurrent_operations = 50
        max_concurrent_memory_mb = 200
        memory_sharing_efficiency = 0.8  # Should be more efficient than linear scaling
        
        # Baseline: single operation memory usage
        baseline_memory = metrics.sample_memory("baseline")
        
        async def memory_using_operation(operation_id: int):
            """Operation that uses memory."""
            # Allocate memory for operation
            operation_data = []
            
            for i in range(200):  # 200 items per operation
                item = {
                    "operation_id": operation_id,
                    "item_id": i,
                    "data": "operation_data_" * 20,  # ~300 bytes per item
                    "metadata": {"created_at": time.time()}
                }
                operation_data.append(item)
            
            # Simulate processing time
            await asyncio.sleep(0.05)  # 50ms processing
            
            # Process data
            processed_items = []
            for item in operation_data:
                processed_item = {
                    "original_id": item["item_id"],
                    "processed_data": item["data"].upper(),
                    "operation_id": operation_id
                }
                processed_items.append(processed_item)
            
            # Cleanup original data
            del operation_data
            
            # Brief additional processing
            await asyncio.sleep(0.02)  # 20ms additional processing
            
            result_count = len(processed_items)
            del processed_items
            
            return {
                "operation_id": operation_id,
                "result_count": result_count
            }
        
        # Execute single operation for baseline
        single_result = await memory_using_operation(-1)
        single_operation_memory = metrics.sample_memory(
            "single_operation", 
            {"operation_id": -1, "result_count": single_result["result_count"]}
        )
        single_memory_usage = single_operation_memory - baseline_memory
        
        # Brief cleanup
        gc.collect()
        await asyncio.sleep(0.1)
        
        # Execute concurrent operations
        concurrent_baseline = metrics.sample_memory("concurrent_baseline")
        
        # Control concurrency with semaphore
        max_concurrent = 25
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def controlled_operation(operation_id: int):
            async with semaphore:
                return await memory_using_operation(operation_id)
        
        # Execute concurrent operations
        concurrent_tasks = [
            controlled_operation(i) 
            for i in range(concurrent_operations)
        ]
        
        concurrent_results = await asyncio.gather(*concurrent_tasks)
        
        peak_concurrent_memory = metrics.sample_memory(
            "peak_concurrent",
            {"concurrent_operations": concurrent_operations}
        )
        
        # Memory efficiency analysis
        concurrent_memory_usage = peak_concurrent_memory - concurrent_baseline
        expected_linear_memory = single_memory_usage * max_concurrent
        memory_efficiency = concurrent_memory_usage / expected_linear_memory if expected_linear_memory > 0 else 1
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Concurrent memory assertions
        assert summary["peak_memory_mb"] <= max_concurrent_memory_mb
        assert memory_efficiency <= (1 / memory_sharing_efficiency)  # Should be more efficient than linear
        assert len(concurrent_results) == concurrent_operations
        
        print(f"Concurrent Memory Usage: {summary}")
        print(f"Single operation: {single_memory_usage:.1f}MB")
        print(f"Concurrent usage: {concurrent_memory_usage:.1f}MB for {max_concurrent} concurrent")
        print(f"Memory efficiency: {memory_efficiency:.2f}x (lower is better)")


class TestMemoryPressureHandling:
    """Test system behavior under memory pressure."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_low_memory_graceful_degradation(self):
        """Test graceful degradation under low memory conditions."""
        metrics = MemoryMetrics()
        metrics.start_monitoring()
        
        # Test parameters
        memory_pressure_threshold_mb = 150  # Simulate pressure at 150MB
        operations_under_pressure = 50
        min_success_rate_under_pressure = 80  # 80% operations should succeed
        
        async def memory_pressure_operation(operation_id: int, under_pressure: bool):
            """Operation that adapts to memory pressure."""
            try:
                current_memory = metrics.sample_memory(f"operation_{operation_id}")
                
                if under_pressure and current_memory > memory_pressure_threshold_mb:
                    # Reduce memory allocation under pressure
                    data_size = 50  # Reduced from normal size
                else:
                    # Normal memory allocation
                    data_size = 200
                
                # Allocate memory based on pressure
                operation_data = []
                for i in range(data_size):
                    item = {
                        "id": f"{operation_id}_{i}",
                        "data": "x" * (100 if not under_pressure else 50),
                        "operation_id": operation_id
                    }
                    operation_data.append(item)
                
                # Process data
                await asyncio.sleep(0.01)  # 10ms processing
                
                result = {
                    "operation_id": operation_id,
                    "data_size": data_size,
                    "under_pressure": under_pressure,
                    "success": True
                }
                
                # Cleanup
                del operation_data
                return result
                
            except MemoryError:
                return {
                    "operation_id": operation_id,
                    "success": False,
                    "error": "memory_error"
                }
        
        # Execute operations with simulated memory pressure
        results = []
        
        # Normal operations first
        for i in range(25):
            result = await memory_pressure_operation(i, False)
            results.append(result)
        
        # Operations under memory pressure
        for i in range(25, 25 + operations_under_pressure):
            result = await memory_pressure_operation(i, True)
            results.append(result)
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Analyze results under pressure
        pressure_results = [r for r in results if r.get("under_pressure", False)]
        successful_under_pressure = sum(1 for r in pressure_results if r["success"])
        success_rate_under_pressure = (successful_under_pressure / len(pressure_results)) * 100 if pressure_results else 100
        
        # Memory pressure assertions
        assert success_rate_under_pressure >= min_success_rate_under_pressure
        assert summary["peak_memory_mb"] <= memory_pressure_threshold_mb * 1.2  # Allow 20% overage
        
        print(f"Memory Pressure Handling: {summary}")
        print(f"Success rate under pressure: {success_rate_under_pressure:.1f}%")