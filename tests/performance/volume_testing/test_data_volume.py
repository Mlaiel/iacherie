"""
Volume Testing Suite

Tests system behavior with large amounts of data and extended operations.
"""

import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any, Optional
import tempfile
import os


class VolumeTestMetrics:
    """Metrics collection for volume testing."""
    
    def __init__(self):
        self.operations: List[Dict[str, Any]] = []
        self.data_processed_bytes: int = 0
        self.start_time: float = 0
        self.end_time: float = 0
        self.peak_memory_usage_mb: float = 0
        self.total_items_processed: int = 0
    
    def start_monitoring(self):
        self.start_time = time.time()
    
    def stop_monitoring(self):
        self.end_time = time.time()
    
    def record_operation(self, operation_type: str, duration: float, data_size: int, 
                        items_processed: int, success: bool = True, metadata: Optional[Dict] = None):
        """Record a volume operation."""
        self.operations.append({
            "operation_type": operation_type,
            "duration": duration,
            "data_size_bytes": data_size,
            "items_processed": items_processed,
            "success": success,
            "timestamp": time.time(),
            "metadata": metadata or {}
        })
        
        if success:
            self.data_processed_bytes += data_size
            self.total_items_processed += items_processed
    
    def update_peak_memory(self, memory_mb: float):
        self.peak_memory_usage_mb = max(self.peak_memory_usage_mb, memory_mb)
    
    def get_summary(self) -> Dict[str, Any]:
        if not self.operations:
            return {"error": "No operations recorded"}
        
        successful_ops = [op for op in self.operations if op["success"]]
        total_duration = self.end_time - self.start_time
        
        response_times = [op["duration"] for op in self.operations]
        throughput_mbps = (self.data_processed_bytes / (1024 * 1024)) / total_duration if total_duration > 0 else 0
        items_per_second = self.total_items_processed / total_duration if total_duration > 0 else 0
        
        return {
            "total_operations": len(self.operations),
            "successful_operations": len(successful_ops),
            "success_rate_percent": (len(successful_ops) / len(self.operations)) * 100,
            "total_duration_seconds": total_duration,
            "data_processed_mb": self.data_processed_bytes / (1024 * 1024),
            "total_items_processed": self.total_items_processed,
            "throughput_mbps": throughput_mbps,
            "items_per_second": items_per_second,
            "peak_memory_usage_mb": self.peak_memory_usage_mb,
            "response_times_ms": {
                "min": min(response_times) * 1000,
                "max": max(response_times) * 1000,
                "mean": statistics.mean(response_times) * 1000,
                "median": statistics.median(response_times) * 1000,
                "p95": sorted(response_times)[int(0.95 * len(response_times))] * 1000 if len(response_times) > 20 else max(response_times) * 1000,
            }
        }


class TestDataVolumeProcessing:
    """Large data volume processing tests."""
    
    @pytest.mark.volume
    @pytest.mark.asyncio
    async def test_large_dataset_processing(self):
        """Test processing large datasets."""
        metrics = VolumeTestMetrics()
        metrics.start_monitoring()
        
        # Volume test parameters
        dataset_sizes = [1000, 5000, 10000, 20000]  # Number of records
        max_processing_time_per_1k_records_ms = 200
        min_throughput_records_per_second = 1000
        max_memory_usage_mb = 500
        
        async def process_dataset(dataset_size: int):
            """Process a dataset of given size."""
            start_time = time.time()
            
            # Generate dataset
            dataset = []
            for i in range(dataset_size):
                record = {
                    "id": i,
                    "data": f"record_{i}_{'x' * 50}",  # ~60 bytes per record
                    "timestamp": time.time(),
                    "metadata": {"processed": False, "batch": i // 100}
                }
                dataset.append(record)
            
            # Simulate memory usage tracking
            estimated_memory_mb = len(dataset) * 0.0001  # ~0.1KB per record
            metrics.update_peak_memory(estimated_memory_mb)
            
            # Process dataset in batches
            batch_size = 100
            processed_count = 0
            
            for i in range(0, len(dataset), batch_size):
                batch = dataset[i:i + batch_size]
                
                # Simulate batch processing
                batch_start = time.time()
                
                for record in batch:
                    # Simulate record processing
                    record["metadata"]["processed"] = True
                    record["processed_at"] = time.time()
                    
                    # Add small delay to simulate processing
                    await asyncio.sleep(0.0001)  # 0.1ms per record
                
                batch_end = time.time()
                processed_count += len(batch)
                
                # Progress reporting
                if processed_count % 1000 == 0:
                    progress = (processed_count / dataset_size) * 100
                    print(f"  Processing progress: {progress:.1f}% ({processed_count}/{dataset_size})")
            
            end_time = time.time()
            total_time = end_time - start_time
            data_size = dataset_size * 100  # Estimated bytes
            
            # Cleanup
            del dataset
            
            return {
                "dataset_size": dataset_size,
                "processing_time": total_time,
                "data_size": data_size,
                "processed_count": processed_count,
                "success": processed_count == dataset_size
            }
        
        # Test different dataset sizes
        for dataset_size in dataset_sizes:
            print(f"Testing dataset size: {dataset_size} records")
            
            result = await process_dataset(dataset_size)
            
            metrics.record_operation(
                operation_type="dataset_processing",
                duration=result["processing_time"],
                data_size=result["data_size"],
                items_processed=result["processed_count"],
                success=result["success"],
                metadata={"dataset_size": dataset_size}
            )
            
            # Per-dataset assertions
            time_per_1k_records = (result["processing_time"] * 1000) / (dataset_size / 1000)
            assert time_per_1k_records <= max_processing_time_per_1k_records_ms
            
            records_per_second = dataset_size / result["processing_time"]
            assert records_per_second >= min_throughput_records_per_second
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Overall volume test assertions
        assert summary["success_rate_percent"] >= 95.0
        assert summary["peak_memory_usage_mb"] <= max_memory_usage_mb
        assert summary["items_per_second"] >= min_throughput_records_per_second
        
        print(f"Large Dataset Processing: {summary}")
    
    @pytest.mark.volume
    @pytest.mark.asyncio
    async def test_file_volume_processing(self):
        """Test processing large volumes of files."""
        metrics = VolumeTestMetrics()
        metrics.start_monitoring()
        
        # File volume parameters
        file_counts = [100, 500, 1000]
        file_sizes_kb = [1, 5, 10, 50]  # Different file sizes
        max_file_processing_time_ms = 100
        min_file_throughput_per_second = 50
        
        async def process_file_batch(file_count: int, file_size_kb: int):
            """Process a batch of files."""
            start_time = time.time()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Generate files
                file_paths = []
                total_data_size = 0
                
                for i in range(file_count):
                    file_path = os.path.join(temp_dir, f"file_{i}.txt")
                    file_content = "x" * (file_size_kb * 1024)  # Create file of specified size
                    
                    with open(file_path, 'w') as f:
                        f.write(file_content)
                    
                    file_paths.append(file_path)
                    total_data_size += len(file_content)
                
                # Process files
                processed_files = 0
                processing_start = time.time()
                
                for file_path in file_paths:
                    file_start = time.time()
                    
                    # Simulate file processing
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                        # Simulate content analysis
                        word_count = len(content.split())
                        char_count = len(content)
                        
                        # Add processing delay
                        await asyncio.sleep(0.01)  # 10ms per file
                    
                    file_end = time.time()
                    processed_files += 1
                    
                    # Progress reporting for large batches
                    if processed_files % 100 == 0:
                        progress = (processed_files / file_count) * 100
                        print(f"    File processing progress: {progress:.1f}% ({processed_files}/{file_count})")
                
                processing_end = time.time()
                total_time = processing_end - start_time
                processing_time = processing_end - processing_start
                
                return {
                    "file_count": file_count,
                    "file_size_kb": file_size_kb,
                    "total_time": total_time,
                    "processing_time": processing_time,
                    "total_data_size": total_data_size,
                    "processed_files": processed_files,
                    "success": processed_files == file_count
                }
        
        # Test different file volumes and sizes
        for file_count in file_counts:
            for file_size_kb in file_sizes_kb:
                print(f"Testing {file_count} files of {file_size_kb}KB each")
                
                result = await process_file_batch(file_count, file_size_kb)
                
                metrics.record_operation(
                    operation_type="file_processing",
                    duration=result["processing_time"],
                    data_size=result["total_data_size"],
                    items_processed=result["processed_files"],
                    success=result["success"],
                    metadata={
                        "file_count": file_count,
                        "file_size_kb": file_size_kb
                    }
                )
                
                # Per-batch assertions
                avg_time_per_file = result["processing_time"] / file_count
                assert avg_time_per_file * 1000 <= max_file_processing_time_ms
                
                files_per_second = file_count / result["processing_time"]
                if file_count >= 100:  # Only check throughput for larger batches
                    assert files_per_second >= min_file_throughput_per_second
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # File volume assertions
        assert summary["success_rate_percent"] >= 95.0
        assert summary["items_per_second"] >= min_file_throughput_per_second
        
        print(f"File Volume Processing: {summary}")
    
    @pytest.mark.volume
    @pytest.mark.asyncio
    async def test_streaming_data_volume(self):
        """Test processing large volumes of streaming data."""
        metrics = VolumeTestMetrics()
        metrics.start_monitoring()
        
        # Streaming volume parameters
        stream_duration_seconds = 30
        events_per_second = 100
        max_event_processing_time_ms = 50
        max_backlog_size = 1000
        
        async def data_stream_generator(events_per_second: int, duration: int):
            """Generate streaming data events."""
            event_id = 0
            start_time = time.time()
            
            while time.time() - start_time < duration:
                # Generate event
                event = {
                    "id": event_id,
                    "timestamp": time.time(),
                    "data": f"event_data_{event_id}_{'x' * 20}",
                    "metadata": {
                        "source": f"source_{event_id % 10}",
                        "priority": event_id % 3
                    }
                }
                
                yield event
                event_id += 1
                
                # Control event rate
                await asyncio.sleep(1.0 / events_per_second)
        
        async def stream_processor():
            """Process streaming data with backlog management."""
            processed_events = 0
            backlog = []
            max_backlog_reached = 0
            
            async for event in data_stream_generator(events_per_second, stream_duration_seconds):
                # Add to backlog
                backlog.append(event)
                max_backlog_reached = max(max_backlog_reached, len(backlog))
                
                # Process events from backlog
                while backlog and len(backlog) <= max_backlog_size:
                    event_to_process = backlog.pop(0)
                    
                    process_start = time.time()
                    
                    # Simulate event processing
                    processed_data = {
                        "original_id": event_to_process["id"],
                        "processed_at": time.time(),
                        "processing_result": f"processed_{event_to_process['id']}"
                    }
                    
                    # Add processing delay
                    await asyncio.sleep(0.005)  # 5ms per event
                    
                    process_end = time.time()
                    processing_time = process_end - process_start
                    
                    # Record processing metrics
                    event_size = len(str(event_to_process))
                    success = processing_time <= (max_event_processing_time_ms / 1000)
                    
                    metrics.record_operation(
                        operation_type="stream_event",
                        duration=processing_time,
                        data_size=event_size,
                        items_processed=1,
                        success=success,
                        metadata={"event_id": event_to_process["id"]}
                    )
                    
                    processed_events += 1
                    
                    # Progress reporting
                    if processed_events % 500 == 0:
                        print(f"    Processed {processed_events} events, backlog: {len(backlog)}")
                
                # Check backlog size
                if len(backlog) > max_backlog_size:
                    print(f"    Warning: Backlog size exceeded ({len(backlog)} events)")
                    # Drop oldest events to prevent memory issues
                    backlog = backlog[-max_backlog_size:]
            
            # Process remaining backlog
            while backlog:
                event_to_process = backlog.pop(0)
                process_start = time.time()
                
                # Quick processing for cleanup
                await asyncio.sleep(0.001)  # 1ms for cleanup
                
                process_end = time.time()
                processing_time = process_end - process_start
                event_size = len(str(event_to_process))
                
                metrics.record_operation(
                    operation_type="stream_event_cleanup",
                    duration=processing_time,
                    data_size=event_size,
                    items_processed=1,
                    success=True,
                    metadata={"event_id": event_to_process["id"], "cleanup": True}
                )
                
                processed_events += 1
            
            return {
                "processed_events": processed_events,
                "max_backlog_reached": max_backlog_reached,
                "success": max_backlog_reached <= max_backlog_size * 1.1  # Allow 10% overflow
            }
        
        # Run streaming test
        print(f"Starting streaming test: {events_per_second} events/sec for {stream_duration_seconds}s")
        stream_result = await stream_processor()
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Streaming volume assertions
        expected_total_events = events_per_second * stream_duration_seconds
        processing_efficiency = (stream_result["processed_events"] / expected_total_events) * 100
        
        assert processing_efficiency >= 90.0  # Should process at least 90% of events
        assert stream_result["success"]  # Backlog should be manageable
        assert summary["success_rate_percent"] >= 95.0  # 95% of events processed successfully
        
        print(f"Streaming Data Volume: {summary}")
        print(f"Stream efficiency: {processing_efficiency:.1f}% ({stream_result['processed_events']}/{expected_total_events})")


class TestConcurrentVolumeOperations:
    """Concurrent volume operations testing."""
    
    @pytest.mark.volume
    @pytest.mark.asyncio
    async def test_concurrent_bulk_operations(self):
        """Test concurrent bulk operations."""
        metrics = VolumeTestMetrics()
        metrics.start_monitoring()
        
        # Concurrent bulk parameters
        concurrent_operations = 20
        items_per_operation = 500
        max_operation_time_s = 10
        min_overall_throughput_items_per_second = 500
        
        async def bulk_operation(operation_id: int, item_count: int):
            """Perform bulk operation on many items."""
            start_time = time.time()
            
            # Generate items for bulk operation
            items = []
            for i in range(item_count):
                item = {
                    "id": f"{operation_id}_{i}",
                    "data": f"bulk_data_{operation_id}_{i}_{'x' * 30}",
                    "operation_id": operation_id,
                    "sequence": i
                }
                items.append(item)
            
            # Simulate bulk processing
            processed_items = 0
            batch_size = 50
            
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                
                # Process batch
                for item in batch:
                    # Simulate item processing
                    item["processed"] = True
                    item["processed_at"] = time.time()
                    
                    # Small processing delay
                    await asyncio.sleep(0.002)  # 2ms per item
                
                processed_items += len(batch)
                
                # Yield control occasionally
                if processed_items % 100 == 0:
                    await asyncio.sleep(0.01)
            
            end_time = time.time()
            total_time = end_time - start_time
            total_data_size = sum(len(str(item)) for item in items)
            
            return {
                "operation_id": operation_id,
                "total_time": total_time,
                "processed_items": processed_items,
                "total_data_size": total_data_size,
                "success": processed_items == item_count
            }
        
        # Execute concurrent bulk operations
        print(f"Starting {concurrent_operations} concurrent bulk operations...")
        
        tasks = [
            bulk_operation(i, items_per_operation) 
            for i in range(concurrent_operations)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Collect metrics
        for result in results:
            metrics.record_operation(
                operation_type="concurrent_bulk",
                duration=result["total_time"],
                data_size=result["total_data_size"],
                items_processed=result["processed_items"],
                success=result["success"],
                metadata={"operation_id": result["operation_id"]}
            )
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Concurrent bulk assertions
        assert summary["success_rate_percent"] >= 95.0
        assert summary["items_per_second"] >= min_overall_throughput_items_per_second
        
        # Check individual operation times
        max_operation_time = max(result["total_time"] for result in results)
        assert max_operation_time <= max_operation_time_s
        
        print(f"Concurrent Bulk Operations: {summary}")
    
    @pytest.mark.volume
    @pytest.mark.asyncio
    async def test_database_volume_simulation(self):
        """Test simulated database operations with large volumes."""
        metrics = VolumeTestMetrics()
        metrics.start_monitoring()
        
        # Database volume parameters
        total_records = 10000
        batch_sizes = [100, 500, 1000]
        operation_types = ["insert", "update", "select", "delete"]
        max_batch_time_s = 5
        min_records_per_second = 1000
        
        async def database_batch_operation(operation_type: str, batch_size: int, start_id: int):
            """Simulate database batch operation."""
            start_time = time.time()
            
            # Generate batch data
            batch_data = []
            for i in range(batch_size):
                record = {
                    "id": start_id + i,
                    "data": f"{operation_type}_data_{start_id + i}_{'x' * 40}",
                    "timestamp": time.time(),
                    "operation": operation_type
                }
                batch_data.append(record)
            
            # Simulate database operation time based on type and size
            base_time_per_record = {
                "insert": 0.002,  # 2ms per insert
                "update": 0.003,  # 3ms per update
                "select": 0.001,  # 1ms per select
                "delete": 0.0015  # 1.5ms per delete
            }
            
            operation_time = base_time_per_record[operation_type] * batch_size
            
            # Add batch overhead
            batch_overhead = 0.01 + (batch_size / 10000)  # Overhead increases with batch size
            total_operation_time = operation_time + batch_overhead
            
            await asyncio.sleep(total_operation_time)
            
            end_time = time.time()
            actual_time = end_time - start_time
            total_data_size = sum(len(str(record)) for record in batch_data)
            
            # Simulate occasional failures (2% failure rate)
            import random
            success = random.random() > 0.02
            
            return {
                "operation_type": operation_type,
                "batch_size": batch_size,
                "start_id": start_id,
                "actual_time": actual_time,
                "total_data_size": total_data_size,
                "records_processed": batch_size if success else 0,
                "success": success
            }
        
        # Execute database volume test
        all_operations = []
        current_id = 0
        
        for batch_size in batch_sizes:
            batches_needed = total_records // (batch_size * len(operation_types))
            
            for batch_num in range(batches_needed):
                for operation_type in operation_types:
                    all_operations.append(
                        database_batch_operation(operation_type, batch_size, current_id)
                    )
                    current_id += batch_size
        
        print(f"Executing {len(all_operations)} database batch operations...")
        
        # Process operations in smaller concurrent groups to avoid overwhelming
        max_concurrent = 10
        results = []
        
        for i in range(0, len(all_operations), max_concurrent):
            batch_operations = all_operations[i:i + max_concurrent]
            batch_results = await asyncio.gather(*batch_operations)
            results.extend(batch_results)
            
            # Progress reporting
            progress = ((i + len(batch_operations)) / len(all_operations)) * 100
            print(f"  Database operations progress: {progress:.1f}%")
        
        # Collect metrics
        for result in results:
            metrics.record_operation(
                operation_type=f"db_{result['operation_type']}",
                duration=result["actual_time"],
                data_size=result["total_data_size"],
                items_processed=result["records_processed"],
                success=result["success"],
                metadata={
                    "batch_size": result["batch_size"],
                    "operation_type": result["operation_type"]
                }
            )
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Database volume assertions
        assert summary["success_rate_percent"] >= 95.0
        assert summary["items_per_second"] >= min_records_per_second
        
        # Check batch performance
        max_batch_time = max(result["actual_time"] for result in results)
        assert max_batch_time <= max_batch_time_s
        
        print(f"Database Volume Simulation: {summary}")
        
        # Operation type breakdown
        operation_breakdown = {}
        for result in results:
            op_type = result["operation_type"]
            if op_type not in operation_breakdown:
                operation_breakdown[op_type] = {"count": 0, "total_time": 0, "total_records": 0}
            
            operation_breakdown[op_type]["count"] += 1
            operation_breakdown[op_type]["total_time"] += result["actual_time"]
            operation_breakdown[op_type]["total_records"] += result["records_processed"]
        
        for op_type, stats in operation_breakdown.items():
            avg_time = stats["total_time"] / stats["count"]
            records_per_second = stats["total_records"] / stats["total_time"]
            print(f"  {op_type}: {stats['count']} batches, avg {avg_time:.3f}s, "
                  f"{records_per_second:.1f} records/s")