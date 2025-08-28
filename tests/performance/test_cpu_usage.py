"""
CPU Usage Performance Tests

Tests for CPU utilization, efficiency, and performance under load.
"""

import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import multiprocessing


class CPUMetrics:
    """CPU performance metrics collection."""
    
    def __init__(self):
        self.cpu_samples: List[Dict[str, Any]] = []
        self.operation_times: List[float] = []
        self.start_time: float = 0
        self.end_time: float = 0
        self.cpu_bound_operations: int = 0
        self.io_bound_operations: int = 0
    
    def start_monitoring(self):
        """Start CPU monitoring."""
        self.start_time = time.time()
    
    def stop_monitoring(self):
        """Stop CPU monitoring."""
        self.end_time = time.time()
    
    def record_operation(self, operation_type: str, execution_time: float, 
                        cpu_intensive: bool = True, metadata: Optional[Dict] = None):
        """Record CPU operation metrics."""
        self.operation_times.append(execution_time)
        
        if cpu_intensive:
            self.cpu_bound_operations += 1
        else:
            self.io_bound_operations += 1
        
        operation_record = {
            "timestamp": time.time(),
            "operation_type": operation_type,
            "execution_time": execution_time,
            "cpu_intensive": cpu_intensive,
            "metadata": metadata or {}
        }
        self.cpu_samples.append(operation_record)
    
    def sample_cpu_usage(self, operation: str = "sample"):
        """Sample current CPU usage."""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            sample = {
                "timestamp": time.time(),
                "cpu_percent": cpu_percent,
                "operation": operation
            }
            self.cpu_samples.append(sample)
            
            return cpu_percent
        except ImportError:
            # Fallback when psutil is not available
            return 0.0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get CPU performance summary."""
        if not self.operation_times:
            return {"error": "No CPU operations recorded"}
        
        duration = self.end_time - self.start_time
        total_operations = len(self.operation_times)
        
        # CPU usage samples
        cpu_samples = [s for s in self.cpu_samples if "cpu_percent" in s]
        avg_cpu_usage = statistics.mean([s["cpu_percent"] for s in cpu_samples]) if cpu_samples else 0
        
        return {
            "duration_seconds": duration,
            "total_operations": total_operations,
            "cpu_bound_operations": self.cpu_bound_operations,
            "io_bound_operations": self.io_bound_operations,
            "operations_per_second": total_operations / duration if duration > 0 else 0,
            "execution_times": {
                "min_ms": min(self.operation_times) * 1000,
                "max_ms": max(self.operation_times) * 1000,
                "mean_ms": statistics.mean(self.operation_times) * 1000,
                "median_ms": statistics.median(self.operation_times) * 1000,
                "p95_ms": sorted(self.operation_times)[int(0.95 * len(self.operation_times))] * 1000 if len(self.operation_times) > 20 else max(self.operation_times) * 1000,
            },
            "cpu_utilization": {
                "average_percent": avg_cpu_usage,
                "sample_count": len(cpu_samples)
            }
        }


class TestCPUBasicPerformance:
    """Basic CPU performance tests."""
    
    @pytest.mark.performance
    def test_cpu_bound_computation_performance(self):
        """Test CPU-bound computation performance."""
        metrics = CPUMetrics()
        metrics.start_monitoring()
        
        # Test parameters
        computation_tasks = 20
        max_computation_time_ms = 500
        min_operations_per_second = 10
        
        def cpu_intensive_computation(task_id: int):
            """CPU-intensive computation task."""
            start_time = time.time()
            
            # Mathematical computation
            result = 0
            computation_size = 100000 + (task_id % 5) * 20000  # Variable complexity
            
            for i in range(computation_size):
                result += i ** 2
                # Add some complexity
                if i % 1000 == 0:
                    result = result % 1000000
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            return {
                "task_id": task_id,
                "result": result,
                "execution_time": execution_time,
                "computation_size": computation_size
            }
        
        # Execute CPU-bound tasks
        results = []
        for i in range(computation_tasks):
            result = cpu_intensive_computation(i)
            results.append(result)
            
            metrics.record_operation(
                "cpu_computation",
                result["execution_time"],
                cpu_intensive=True,
                metadata={"task_id": result["task_id"], "computation_size": result["computation_size"]}
            )
            
            # Sample CPU usage periodically
            if i % 5 == 0:
                metrics.sample_cpu_usage(f"computation_task_{i}")
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # CPU computation assertions
        assert summary["execution_times"]["mean_ms"] <= max_computation_time_ms
        assert summary["operations_per_second"] >= min_operations_per_second
        assert len(results) == computation_tasks
        
        print(f"CPU Computation Performance: {summary}")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_mixed_cpu_io_workload_performance(self):
        """Test performance with mixed CPU and I/O workload."""
        metrics = CPUMetrics()
        metrics.start_monitoring()
        
        # Test parameters
        mixed_operations = 40
        cpu_to_io_ratio = 0.5  # 50% CPU, 50% I/O
        max_avg_operation_time_ms = 200
        
        async def cpu_bound_operation(operation_id: int):
            """CPU-bound operation."""
            start_time = time.time()
            
            # CPU computation
            result = 0
            for i in range(50000):
                result += i * i
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            return {
                "operation_id": operation_id,
                "type": "cpu_bound",
                "execution_time": execution_time,
                "result": result
            }
        
        async def io_bound_operation(operation_id: int):
            """I/O-bound operation simulation."""
            start_time = time.time()
            
            # Simulate I/O wait
            await asyncio.sleep(0.05)  # 50ms I/O simulation
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            return {
                "operation_id": operation_id,
                "type": "io_bound",
                "execution_time": execution_time,
                "result": "io_complete"
            }
        
        # Create mixed workload
        tasks = []
        for i in range(mixed_operations):
            if i % 2 == 0:  # Alternate between CPU and I/O
                tasks.append(cpu_bound_operation(i))
            else:
                tasks.append(io_bound_operation(i))
        
        # Execute mixed workload
        results = await asyncio.gather(*tasks)
        
        # Collect metrics
        for result in results:
            is_cpu_intensive = result["type"] == "cpu_bound"
            metrics.record_operation(
                result["type"],
                result["execution_time"],
                cpu_intensive=is_cpu_intensive,
                metadata={"operation_id": result["operation_id"]}
            )
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Mixed workload assertions
        assert summary["execution_times"]["mean_ms"] <= max_avg_operation_time_ms
        assert summary["cpu_bound_operations"] > 0
        assert summary["io_bound_operations"] > 0
        
        # Check ratio
        actual_cpu_ratio = summary["cpu_bound_operations"] / summary["total_operations"]
        assert abs(actual_cpu_ratio - cpu_to_io_ratio) <= 0.1  # Allow 10% variance
        
        print(f"Mixed CPU/IO Workload Performance: {summary}")
    
    @pytest.mark.performance
    def test_cpu_scaling_with_load(self):
        """Test CPU performance scaling with increasing load."""
        metrics = CPUMetrics()
        metrics.start_monitoring()
        
        # Test parameters
        load_levels = [1, 2, 4, 8]  # Number of concurrent CPU tasks
        max_degradation_factor = 2.0  # Performance shouldn't degrade more than 2x
        
        def cpu_task(task_id: int, load_level: int):
            """CPU task for scaling test."""
            start_time = time.time()
            
            # Consistent workload per task
            result = 0
            for i in range(75000):
                result += i ** 2
                if i % 10000 == 0:
                    result = result % 1000000
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            return {
                "task_id": task_id,
                "load_level": load_level,
                "execution_time": execution_time,
                "result": result
            }
        
        load_results = {}
        baseline_time = None
        
        for load_level in load_levels:
            print(f"    Testing CPU load level: {load_level} concurrent tasks")
            
            # Execute tasks for this load level
            with ThreadPoolExecutor(max_workers=load_level) as executor:
                load_start_time = time.time()
                
                futures = [
                    executor.submit(cpu_task, i, load_level) 
                    for i in range(load_level)
                ]
                
                level_results = [future.result() for future in futures]
                
                load_end_time = time.time()
                total_load_time = load_end_time - load_start_time
            
            # Calculate load level metrics
            avg_task_time = statistics.mean([r["execution_time"] for r in level_results])
            total_throughput = load_level / total_load_time
            
            load_results[load_level] = {
                "avg_task_time": avg_task_time,
                "total_load_time": total_load_time,
                "throughput": total_throughput
            }
            
            # Record metrics
            for result in level_results:
                metrics.record_operation(
                    f"cpu_scaling_load_{load_level}",
                    result["execution_time"],
                    cpu_intensive=True,
                    metadata={"load_level": load_level, "task_id": result["task_id"]}
                )
            
            # Set baseline from single task
            if baseline_time is None:
                baseline_time = avg_task_time
            
            # Check degradation
            degradation_factor = avg_task_time / baseline_time
            print(f"      Load {load_level}: {avg_task_time:.3f}s avg, "
                  f"{degradation_factor:.2f}x degradation")
            
            # Sample CPU usage
            metrics.sample_cpu_usage(f"load_level_{load_level}")
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # CPU scaling assertions
        max_load_time = load_results[max(load_levels)]["avg_task_time"]
        final_degradation = max_load_time / baseline_time
        
        assert final_degradation <= max_degradation_factor
        assert all(r["avg_task_time"] > 0 for r in load_results.values())
        
        print(f"CPU Scaling Performance: {summary}")
        print(f"Final degradation factor: {final_degradation:.2f}x")


class TestCPUConcurrencyPerformance:
    """CPU concurrency and parallelization performance tests."""
    
    @pytest.mark.performance
    def test_thread_pool_cpu_performance(self):
        """Test CPU performance with thread pool parallelization."""
        metrics = CPUMetrics()
        metrics.start_monitoring()
        
        # Test parameters
        total_tasks = 32
        thread_pool_sizes = [2, 4, 8, 16]
        target_speedup_factor = 2.0  # Should be at least 2x faster with threading
        
        def cpu_worker_task(task_id: int):
            """Worker task for thread pool."""
            start_time = time.time()
            
            # CPU-intensive work
            result = 0
            for i in range(100000):
                result += (i * task_id) % 1000
            
            end_time = time.time()
            return {
                "task_id": task_id,
                "execution_time": end_time - start_time,
                "result": result
            }
        
        # Baseline: sequential execution
        sequential_start = time.time()
        sequential_results = []
        for i in range(total_tasks):
            result = cpu_worker_task(i)
            sequential_results.append(result)
        sequential_end = time.time()
        sequential_time = sequential_end - sequential_start
        
        print(f"    Sequential execution: {sequential_time:.3f}s")
        
        # Test different thread pool sizes
        pool_results = {}
        
        for pool_size in thread_pool_sizes:
            pool_start = time.time()
            
            with ThreadPoolExecutor(max_workers=pool_size) as executor:
                futures = [executor.submit(cpu_worker_task, i) for i in range(total_tasks)]
                pool_task_results = [future.result() for future in futures]
            
            pool_end = time.time()
            pool_time = pool_end - pool_start
            speedup = sequential_time / pool_time
            
            pool_results[pool_size] = {
                "execution_time": pool_time,
                "speedup": speedup,
                "tasks_completed": len(pool_task_results)
            }
            
            print(f"    Thread pool {pool_size}: {pool_time:.3f}s, {speedup:.2f}x speedup")
            
            # Record metrics
            for result in pool_task_results:
                metrics.record_operation(
                    f"thread_pool_{pool_size}",
                    result["execution_time"],
                    cpu_intensive=True,
                    metadata={"pool_size": pool_size, "task_id": result["task_id"]}
                )
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Thread pool performance assertions
        best_speedup = max(r["speedup"] for r in pool_results.values())
        assert best_speedup >= target_speedup_factor
        assert all(r["tasks_completed"] == total_tasks for r in pool_results.values())
        
        print(f"Thread Pool CPU Performance: {summary}")
    
    @pytest.mark.performance
    def test_process_pool_cpu_performance(self):
        """Test CPU performance with process pool parallelization."""
        metrics = CPUMetrics()
        metrics.start_monitoring()
        
        # Test parameters
        cpu_intensive_tasks = 16
        process_pool_size = min(4, multiprocessing.cpu_count())
        min_process_speedup = 1.5  # Should be at least 1.5x faster with multiprocessing
        
        def cpu_intensive_process_task(task_data):
            """CPU-intensive task for process pool."""
            task_id, iterations = task_data
            start_time = time.time()
            
            # Heavy computation that benefits from multiprocessing
            result = 0
            for i in range(iterations):
                for j in range(1000):
                    result += (i * j + task_id) % 10000
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            return {
                "task_id": task_id,
                "execution_time": execution_time,
                "result": result,
                "iterations": iterations
            }
        
        # Prepare task data
        task_data_list = [(i, 5000 + i * 100) for i in range(cpu_intensive_tasks)]
        
        # Sequential baseline
        sequential_start = time.time()
        sequential_results = []
        for task_data in task_data_list:
            result = cpu_intensive_process_task(task_data)
            sequential_results.append(result)
        sequential_end = time.time()
        sequential_time = sequential_end - sequential_start
        
        print(f"    Sequential process tasks: {sequential_time:.3f}s")
        
        # Process pool execution
        process_start = time.time()
        
        with ProcessPoolExecutor(max_workers=process_pool_size) as executor:
            process_results = list(executor.map(cpu_intensive_process_task, task_data_list))
        
        process_end = time.time()
        process_time = process_end - process_start
        process_speedup = sequential_time / process_time
        
        print(f"    Process pool {process_pool_size}: {process_time:.3f}s, {process_speedup:.2f}x speedup")
        
        # Record metrics
        for result in process_results:
            metrics.record_operation(
                "process_pool",
                result["execution_time"],
                cpu_intensive=True,
                metadata={
                    "task_id": result["task_id"],
                    "iterations": result["iterations"],
                    "pool_size": process_pool_size
                }
            )
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Process pool assertions
        assert process_speedup >= min_process_speedup
        assert len(process_results) == cpu_intensive_tasks
        assert all(r["execution_time"] > 0 for r in process_results)
        
        print(f"Process Pool CPU Performance: {summary}")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_async_cpu_task_performance(self):
        """Test CPU task performance with async coordination."""
        metrics = CPUMetrics()
        metrics.start_monitoring()
        
        # Test parameters
        async_coordinated_tasks = 20
        max_concurrent_cpu_tasks = 4
        max_coordination_overhead_percent = 20  # Max 20% overhead from async coordination
        
        def cpu_computation(task_id: int):
            """CPU computation that runs in thread."""
            start_time = time.time()
            
            # CPU work
            result = 0
            for i in range(80000):
                result += i ** 2
                if i % 20000 == 0:
                    result = result % 1000000
            
            end_time = time.time()
            return {
                "task_id": task_id,
                "execution_time": end_time - start_time,
                "result": result
            }
        
        async def async_cpu_coordinator(task_id: int, executor: ThreadPoolExecutor):
            """Async coordinator for CPU task."""
            coordination_start = time.time()
            
            # Submit CPU work to thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(executor, cpu_computation, task_id)
            
            coordination_end = time.time()
            coordination_time = coordination_end - coordination_start
            
            return {
                "task_id": task_id,
                "cpu_execution_time": result["execution_time"],
                "total_coordination_time": coordination_time,
                "result": result["result"]
            }
        
        # Baseline: direct CPU computation
        baseline_start = time.time()
        baseline_results = []
        for i in range(async_coordinated_tasks):
            result = cpu_computation(i)
            baseline_results.append(result)
        baseline_end = time.time()
        baseline_time = baseline_end - baseline_start
        
        # Async coordinated execution
        async_start = time.time()
        
        with ThreadPoolExecutor(max_workers=max_concurrent_cpu_tasks) as executor:
            # Control concurrency
            semaphore = asyncio.Semaphore(max_concurrent_cpu_tasks)
            
            async def controlled_cpu_task(task_id: int):
                async with semaphore:
                    return await async_cpu_coordinator(task_id, executor)
            
            # Execute async coordinated tasks
            async_tasks = [controlled_cpu_task(i) for i in range(async_coordinated_tasks)]
            async_results = await asyncio.gather(*async_tasks)
        
        async_end = time.time()
        async_time = async_end - async_start
        
        # Calculate coordination overhead
        coordination_overhead = ((async_time - baseline_time) / baseline_time) * 100
        
        # Record metrics
        for result in async_results:
            metrics.record_operation(
                "async_coordinated_cpu",
                result["cpu_execution_time"],
                cpu_intensive=True,
                metadata={
                    "task_id": result["task_id"],
                    "coordination_time": result["total_coordination_time"]
                }
            )
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Async CPU coordination assertions
        assert coordination_overhead <= max_coordination_overhead_percent
        assert len(async_results) == async_coordinated_tasks
        assert async_time <= baseline_time * 1.5  # Should not be 50% slower
        
        print(f"Async CPU Coordination Performance: {summary}")
        print(f"Coordination overhead: {coordination_overhead:.1f}%")
        print(f"Baseline time: {baseline_time:.3f}s, Async time: {async_time:.3f}s")


class TestCPUResourceUtilization:
    """CPU resource utilization and efficiency tests."""
    
    @pytest.mark.performance
    def test_cpu_utilization_efficiency(self):
        """Test CPU utilization efficiency during intensive workloads."""
        metrics = CPUMetrics()
        metrics.start_monitoring()
        
        # Test parameters
        workload_duration_seconds = 15
        target_cpu_utilization_percent = 70  # Should achieve at least 70% CPU usage
        max_cpu_utilization_percent = 95   # Should not exceed 95% (leave room for system)
        
        def sustained_cpu_workload():
            """Sustained CPU workload for utilization testing."""
            workload_start = time.time()
            operation_count = 0
            
            while time.time() - workload_start < workload_duration_seconds:
                # CPU-intensive computation
                result = 0
                for i in range(50000):
                    result += i * i
                
                operation_count += 1
                
                # Brief yield to allow CPU sampling
                if operation_count % 100 == 0:
                    time.sleep(0.001)  # 1ms yield
            
            return {
                "duration": time.time() - workload_start,
                "operations": operation_count
            }
        
        # Sample CPU usage before workload
        initial_cpu = metrics.sample_cpu_usage("initial")
        
        # Execute sustained workload with CPU monitoring
        cpu_samples = []
        workload_result = None
        
        def cpu_sampling_thread():
            """Thread to sample CPU usage during workload."""
            sample_count = 0
            while workload_result is None:
                cpu_usage = metrics.sample_cpu_usage(f"workload_sample_{sample_count}")
                cpu_samples.append(cpu_usage)
                sample_count += 1
                time.sleep(0.5)  # Sample every 500ms
        
        # Start CPU sampling in background
        sampling_thread = threading.Thread(target=cpu_sampling_thread)
        sampling_thread.daemon = True
        sampling_thread.start()
        
        # Execute CPU workload
        workload_start_time = time.time()
        workload_result = sustained_cpu_workload()
        workload_end_time = time.time()
        
        # Wait for final samples
        time.sleep(1)
        
        # Sample CPU after workload
        final_cpu = metrics.sample_cpu_usage("final")
        
        # Record workload metrics
        metrics.record_operation(
            "sustained_cpu_workload",
            workload_result["duration"],
            cpu_intensive=True,
            metadata={
                "operations": workload_result["operations"],
                "ops_per_second": workload_result["operations"] / workload_result["duration"]
            }
        )
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # CPU utilization analysis
        valid_samples = [cpu for cpu in cpu_samples if cpu > 0]
        if valid_samples:
            avg_cpu_utilization = statistics.mean(valid_samples)
            peak_cpu_utilization = max(valid_samples)
        else:
            avg_cpu_utilization = 0
            peak_cpu_utilization = 0
        
        # CPU utilization assertions
        if valid_samples:  # Only test if we have valid CPU samples
            assert avg_cpu_utilization >= target_cpu_utilization_percent
            assert peak_cpu_utilization <= max_cpu_utilization_percent
        
        assert workload_result["operations"] > 0
        assert workload_result["duration"] >= workload_duration_seconds * 0.9  # Allow 10% variance
        
        print(f"CPU Utilization Efficiency: {summary}")
        print(f"Average CPU utilization: {avg_cpu_utilization:.1f}%")
        print(f"Peak CPU utilization: {peak_cpu_utilization:.1f}%")
        print(f"Operations completed: {workload_result['operations']}")
    
    @pytest.mark.performance
    def test_cpu_thermal_throttling_simulation(self):
        """Test CPU performance under simulated thermal conditions."""
        metrics = CPUMetrics()
        metrics.start_monitoring()
        
        # Test parameters
        thermal_phases = [
            ("normal", 1.0, 30),      # Normal performance for 30 operations
            ("warm", 0.9, 20),        # 90% performance (10% throttling)
            ("hot", 0.7, 15),         # 70% performance (30% throttling)
            ("recovery", 0.95, 25)    # 95% performance (recovery)
        ]
        
        max_performance_degradation = 0.5  # Performance should not drop below 50%
        
        def thermal_adjusted_cpu_task(task_id: int, thermal_factor: float, phase: str):
            """CPU task with thermal adjustment."""
            start_time = time.time()
            
            # Base computation
            base_iterations = 60000
            adjusted_iterations = int(base_iterations * thermal_factor)
            
            result = 0
            for i in range(adjusted_iterations):
                result += i ** 2
                
                # Simulate thermal throttling by adding delays
                if thermal_factor < 1.0 and i % 10000 == 0:
                    time.sleep(0.001)  # Throttling delay
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            return {
                "task_id": task_id,
                "phase": phase,
                "thermal_factor": thermal_factor,
                "execution_time": execution_time,
                "iterations": adjusted_iterations,
                "result": result
            }
        
        # Execute thermal simulation phases
        all_results = []
        normal_performance_baseline = None
        
        for phase_name, thermal_factor, task_count in thermal_phases:
            print(f"    Thermal phase '{phase_name}': {thermal_factor:.1%} performance")
            
            phase_results = []
            for i in range(task_count):
                result = thermal_adjusted_cpu_task(i, thermal_factor, phase_name)
                phase_results.append(result)
                all_results.append(result)
                
                # Record metrics
                metrics.record_operation(
                    f"thermal_{phase_name}",
                    result["execution_time"],
                    cpu_intensive=True,
                    metadata={
                        "phase": phase_name,
                        "thermal_factor": thermal_factor,
                        "iterations": result["iterations"]
                    }
                )
            
            # Calculate phase performance
            avg_phase_time = statistics.mean([r["execution_time"] for r in phase_results])
            
            if phase_name == "normal":
                normal_performance_baseline = avg_phase_time
            
            if normal_performance_baseline:
                relative_performance = normal_performance_baseline / avg_phase_time
                print(f"      Average time: {avg_phase_time:.3f}s, "
                      f"Relative performance: {relative_performance:.2f}x")
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Thermal performance analysis
        hot_phase_results = [r for r in all_results if r["phase"] == "hot"]
        if hot_phase_results and normal_performance_baseline:
            hot_avg_time = statistics.mean([r["execution_time"] for r in hot_phase_results])
            hot_performance_ratio = normal_performance_baseline / hot_avg_time
            
            assert hot_performance_ratio >= max_performance_degradation
        
        # Recovery analysis
        recovery_results = [r for r in all_results if r["phase"] == "recovery"]
        if recovery_results and normal_performance_baseline:
            recovery_avg_time = statistics.mean([r["execution_time"] for r in recovery_results])
            recovery_performance_ratio = normal_performance_baseline / recovery_avg_time
            
            assert recovery_performance_ratio >= 0.8  # Should recover to at least 80%
        
        print(f"CPU Thermal Simulation: {summary}")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cpu_burst_performance(self):
        """Test CPU performance during burst workloads."""
        metrics = CPUMetrics()
        metrics.start_monitoring()
        
        # Test parameters
        burst_cycles = 5
        burst_intensity = 10  # Operations per burst
        burst_interval = 2    # Seconds between bursts
        max_burst_response_time_ms = 300
        
        async def cpu_burst_operation(operation_id: int, burst_id: int):
            """CPU operation during burst."""
            start_time = time.time()
            
            # CPU computation with burst characteristics
            result = 0
            iterations = 40000 + (operation_id % 5) * 5000  # Variable load
            
            for i in range(iterations):
                result += i * i
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            return {
                "operation_id": operation_id,
                "burst_id": burst_id,
                "execution_time": execution_time,
                "iterations": iterations,
                "result": result
            }
        
        # Execute burst pattern
        all_burst_results = []
        
        for burst_id in range(burst_cycles):
            print(f"    Executing burst {burst_id + 1}/{burst_cycles}")
            
            # Burst phase: execute multiple operations concurrently
            burst_start = time.time()
            
            # Create burst tasks
            burst_tasks = [
                cpu_burst_operation(burst_id * burst_intensity + i, burst_id)
                for i in range(burst_intensity)
            ]
            
            # Execute burst with limited concurrency
            max_concurrent = 4
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def controlled_burst_operation(task):
                async with semaphore:
                    # Run CPU operation in thread to avoid blocking event loop
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, lambda: asyncio.run(task))
            
            # Wait for burst completion
            burst_results = await asyncio.gather(*burst_tasks)
            
            burst_end = time.time()
            burst_duration = burst_end - burst_start
            
            print(f"      Burst {burst_id} completed in {burst_duration:.3f}s")
            
            # Record burst metrics
            for result in burst_results:
                metrics.record_operation(
                    f"cpu_burst_{burst_id}",
                    result["execution_time"],
                    cpu_intensive=True,
                    metadata={
                        "burst_id": result["burst_id"],
                        "operation_id": result["operation_id"],
                        "iterations": result["iterations"]
                    }
                )
                
                all_burst_results.append(result)
            
            # Inter-burst interval
            if burst_id < burst_cycles - 1:
                await asyncio.sleep(burst_interval)
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Burst performance assertions
        assert summary["execution_times"]["p95_ms"] <= max_burst_response_time_ms
        assert len(all_burst_results) == burst_cycles * burst_intensity
        assert summary["operations_per_second"] > 0
        
        # Analyze burst consistency
        burst_times_by_cycle = {}
        for result in all_burst_results:
            burst_id = result["burst_id"]
            if burst_id not in burst_times_by_cycle:
                burst_times_by_cycle[burst_id] = []
            burst_times_by_cycle[burst_id].append(result["execution_time"])
        
        # Check burst consistency
        burst_variances = []
        for burst_id, times in burst_times_by_cycle.items():
            if len(times) > 1:
                variance = statistics.variance(times)
                burst_variances.append(variance)
        
        if burst_variances:
            avg_burst_variance = statistics.mean(burst_variances)
            assert avg_burst_variance <= 0.01  # Low variance within bursts
        
        print(f"CPU Burst Performance: {summary}")
        print(f"Burst cycles completed: {burst_cycles}")
        print(f"Total operations: {len(all_burst_results)}")