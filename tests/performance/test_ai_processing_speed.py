"""
AI Processing Speed Tests
========================

Tests the performance of AI processing components including
NLP analysis, content generation, and various AI operations.
"""

import pytest
import asyncio
import time
import random
import statistics
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MockAIProcessor:
    """Mock AI processor for performance testing."""
    
    def __init__(self):
        self.processing_times = {
            "sentiment_analysis": (0.05, 0.15),  # 50-150ms
            "content_classification": (0.1, 0.3),  # 100-300ms
            "text_generation": (0.5, 1.5),  # 500-1500ms
            "image_processing": (0.8, 2.0),  # 800-2000ms
            "audio_analysis": (1.0, 3.0),  # 1-3 seconds
            "video_processing": (2.0, 5.0),  # 2-5 seconds
        }
    
    async def process_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Mock sentiment analysis processing."""
        processing_time = random.uniform(*self.processing_times["sentiment_analysis"])
        await asyncio.sleep(processing_time)
        
        return {
            "operation": "sentiment_analysis",
            "input_length": len(text),
            "processing_time_ms": processing_time * 1000,
            "result": {
                "sentiment": random.choice(["positive", "negative", "neutral"]),
                "confidence": random.uniform(0.7, 0.95),
                "text_length": len(text)
            },
            "success": True
        }
    
    async def process_content_classification(self, content: str) -> Dict[str, Any]:
        """Mock content classification processing."""
        processing_time = random.uniform(*self.processing_times["content_classification"])
        await asyncio.sleep(processing_time)
        
        return {
            "operation": "content_classification",
            "input_length": len(content),
            "processing_time_ms": processing_time * 1000,
            "result": {
                "category": random.choice(["entertainment", "educational", "promotional", "news"]),
                "subcategory": random.choice(["music", "gaming", "tutorial", "review"]),
                "confidence": random.uniform(0.8, 0.98)
            },
            "success": True
        }
    
    async def process_text_generation(self, prompt: str, max_length: int = 100) -> Dict[str, Any]:
        """Mock text generation processing."""
        # Processing time increases with output length
        base_time = self.processing_times["text_generation"][0]
        additional_time = (max_length / 100) * random.uniform(0.1, 0.3)
        processing_time = base_time + additional_time
        
        await asyncio.sleep(processing_time)
        
        generated_text = f"Generated content based on: {prompt[:50]}..." + " Sample generated text." * (max_length // 20)
        
        return {
            "operation": "text_generation",
            "input_length": len(prompt),
            "processing_time_ms": processing_time * 1000,
            "result": {
                "generated_text": generated_text[:max_length],
                "actual_length": min(len(generated_text), max_length),
                "tokens_per_second": max_length / processing_time if processing_time > 0 else 0
            },
            "success": True
        }
    
    async def process_image_analysis(self, image_size_kb: int) -> Dict[str, Any]:
        """Mock image processing."""
        # Processing time scales with image size
        base_time = self.processing_times["image_processing"][0]
        size_factor = min(image_size_kb / 500, 3)  # Cap at 3x for very large images
        processing_time = base_time * (1 + size_factor)
        
        await asyncio.sleep(processing_time)
        
        return {
            "operation": "image_processing",
            "input_size_kb": image_size_kb,
            "processing_time_ms": processing_time * 1000,
            "result": {
                "objects_detected": random.randint(1, 10),
                "faces_detected": random.randint(0, 5),
                "quality_score": random.uniform(0.6, 0.9),
                "processing_speed_kb_per_sec": image_size_kb / processing_time if processing_time > 0 else 0
            },
            "success": True
        }
    
    async def process_audio_analysis(self, audio_duration_seconds: int) -> Dict[str, Any]:
        """Mock audio processing."""
        # Processing time scales with audio duration
        base_time = self.processing_times["audio_analysis"][0]
        duration_factor = audio_duration_seconds / 60  # Factor based on minutes
        processing_time = base_time * (1 + duration_factor)
        
        await asyncio.sleep(processing_time)
        
        return {
            "operation": "audio_analysis",
            "input_duration_seconds": audio_duration_seconds,
            "processing_time_ms": processing_time * 1000,
            "result": {
                "speech_detected": random.choice([True, False]),
                "music_genre": random.choice(["pop", "rock", "classical", "jazz", "electronic"]),
                "tempo": random.randint(60, 180),
                "processing_speed_ratio": audio_duration_seconds / processing_time if processing_time > 0 else 0
            },
            "success": True
        }


@pytest.mark.performance
@pytest.mark.asyncio
async def test_sentiment_analysis_performance():
    """Test sentiment analysis processing speed."""
    processor = MockAIProcessor()
    
    # Test various text lengths
    test_texts = [
        "Short text",
        "Medium length text that contains more content for analysis and processing.",
        "Long text content that simulates typical social media posts or content descriptions that need to be analyzed for sentiment detection and classification purposes. This text is longer and more complex." * 3
    ]
    
    results = []
    
    for i, text in enumerate(test_texts):
        start_time = time.time()
        result = await processor.process_sentiment_analysis(text)
        end_time = time.time()
        
        result["test_id"] = i
        result["actual_processing_time_ms"] = (end_time - start_time) * 1000
        results.append(result)
    
    # Analyze sentiment analysis performance
    successful_results = [r for r in results if r["success"]]
    assert len(successful_results) == len(test_texts), "Some sentiment analysis operations failed"
    
    processing_times = [r["processing_time_ms"] for r in successful_results]
    avg_processing_time = statistics.mean(processing_times)
    max_processing_time = max(processing_times)
    
    # Performance assertions
    assert avg_processing_time < 200, f"Average sentiment analysis time too high: {avg_processing_time:.2f}ms"
    assert max_processing_time < 500, f"Max sentiment analysis time too high: {max_processing_time:.2f}ms"
    
    # Check processing time scales reasonably with text length
    for result in successful_results:
        text_length = result["input_length"]
        processing_time = result["processing_time_ms"]
        
        # Should process at least 100 characters per second
        min_chars_per_sec = 100
        chars_per_sec = (text_length / (processing_time / 1000)) if processing_time > 0 else 0
        assert chars_per_sec >= min_chars_per_sec, f"Sentiment analysis too slow: {chars_per_sec:.2f} chars/sec"
    
    logger.info(f"Sentiment analysis test completed - Avg time: {avg_processing_time:.2f}ms, "
                f"Max time: {max_processing_time:.2f}ms")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_ai_operations():
    """Test concurrent AI operations performance."""
    processor = MockAIProcessor()
    concurrent_operations = 10
    
    # Mix of different operations
    operations = [
        ("sentiment_analysis", {"text": "Test content for sentiment analysis"}),
        ("content_classification", {"content": "Content for classification"}),
        ("text_generation", {"prompt": "Generate content about topic", "max_length": 50}),
        ("image_analysis", {"image_size_kb": random.randint(100, 1000)}),
        ("audio_analysis", {"audio_duration_seconds": random.randint(30, 180)})
    ]
    
    async def perform_operation(op_id: int) -> Dict[str, Any]:
        """Perform a single AI operation."""
        operation_type, params = random.choice(operations)
        
        start_time = time.time()
        
        try:
            if operation_type == "sentiment_analysis":
                result = await processor.process_sentiment_analysis(params["text"])
            elif operation_type == "content_classification":
                result = await processor.process_content_classification(params["content"])
            elif operation_type == "text_generation":
                result = await processor.process_text_generation(params["prompt"], params["max_length"])
            elif operation_type == "image_analysis":
                result = await processor.process_image_analysis(params["image_size_kb"])
            elif operation_type == "audio_analysis":
                result = await processor.process_audio_analysis(params["audio_duration_seconds"])
            else:
                result = {"success": False, "error": "Unknown operation"}
            
            end_time = time.time()
            
            result["operation_id"] = op_id
            result["total_time_ms"] = (end_time - start_time) * 1000
            
            return result
            
        except Exception as e:
            end_time = time.time()
            return {
                "operation_id": op_id,
                "operation": operation_type,
                "success": False,
                "error": str(e),
                "total_time_ms": (end_time - start_time) * 1000
            }
    
    # Execute concurrent operations
    start_time = time.time()
    
    tasks = [perform_operation(i) for i in range(concurrent_operations)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    
    # Analyze concurrent operations
    valid_results = [r for r in results if isinstance(r, dict)]
    successful_results = [r for r in valid_results if r["success"]]
    
    success_rate = len(successful_results) / len(valid_results) if valid_results else 0
    total_duration = end_time - start_time
    operations_per_second = len(successful_results) / total_duration if total_duration > 0 else 0
    
    processing_times = [r["processing_time_ms"] for r in successful_results if "processing_time_ms" in r]
    avg_processing_time = statistics.mean(processing_times) if processing_times else 0
    
    # Group by operation type
    operation_types = {}
    for result in successful_results:
        op_type = result.get("operation", "unknown")
        if op_type not in operation_types:
            operation_types[op_type] = []
        operation_types[op_type].append(result)
    
    # Assertions
    assert success_rate >= 0.90, f"Concurrent AI operations success rate too low: {success_rate:.2f}"
    assert operations_per_second >= 3, f"AI operations per second too low: {operations_per_second:.2f}"
    assert avg_processing_time < 2000, f"Average concurrent AI processing time too high: {avg_processing_time:.2f}ms"
    
    logger.info(f"Concurrent AI operations test completed - Operations: {concurrent_operations}, "
                f"Success rate: {success_rate:.2f}, OPS: {operations_per_second:.2f}, "
                f"Avg time: {avg_processing_time:.2f}ms")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_ai_batch_processing():
    """Test AI batch processing performance."""
    processor = MockAIProcessor()
    batch_size = 20
    
    # Create batch of sentiment analysis tasks
    texts = [
        f"Batch processing test content item {i} with varying lengths and complexity levels."
        + " Additional content." * random.randint(1, 5)
        for i in range(batch_size)
    ]
    
    async def process_batch_item(item_id: int, text: str) -> Dict[str, Any]:
        """Process a single batch item."""
        result = await processor.process_sentiment_analysis(text)
        result["batch_item_id"] = item_id
        return result
    
    # Process batch concurrently
    start_time = time.time()
    
    batch_tasks = [process_batch_item(i, texts[i]) for i in range(batch_size)]
    batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
    
    end_time = time.time()
    
    # Analyze batch processing
    valid_results = [r for r in batch_results if isinstance(r, dict)]
    successful_results = [r for r in valid_results if r["success"]]
    
    success_rate = len(successful_results) / len(valid_results) if valid_results else 0
    total_duration = end_time - start_time
    items_per_second = len(successful_results) / total_duration if total_duration > 0 else 0
    
    processing_times = [r["processing_time_ms"] for r in successful_results]
    avg_processing_time = statistics.mean(processing_times) if processing_times else 0
    total_text_length = sum(r["input_length"] for r in successful_results)
    chars_per_second = total_text_length / total_duration if total_duration > 0 else 0
    
    # Batch processing efficiency
    sequential_time_estimate = sum(processing_times) / 1000  # Convert to seconds
    parallel_efficiency = sequential_time_estimate / total_duration if total_duration > 0 else 1
    
    # Assertions
    assert success_rate >= 0.95, f"Batch processing success rate too low: {success_rate:.2f}"
    assert items_per_second >= 10, f"Batch items per second too low: {items_per_second:.2f}"
    assert parallel_efficiency >= 5, f"Batch parallel efficiency too low: {parallel_efficiency:.2f}x"
    assert chars_per_second >= 500, f"Batch chars per second too low: {chars_per_second:.2f}"
    
    logger.info(f"AI batch processing test completed - Batch size: {batch_size}, "
                f"Success rate: {success_rate:.2f}, Items/sec: {items_per_second:.2f}, "
                f"Efficiency: {parallel_efficiency:.2f}x, Chars/sec: {chars_per_second:.2f}")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_ai_processing_scalability():
    """Test AI processing scalability with increasing load."""
    processor = MockAIProcessor()
    load_levels = [5, 10, 20, 30]  # Number of concurrent operations
    
    scalability_results = []
    
    for load_level in load_levels:
        logger.info(f"Testing AI scalability at load level: {load_level}")
        
        async def process_load_item(item_id: int) -> Dict[str, Any]:
            """Process an item at current load level."""
            # Mix of fast and slow operations
            if item_id % 3 == 0:
                result = await processor.process_sentiment_analysis(f"Text for analysis {item_id}")
            elif item_id % 3 == 1:
                result = await processor.process_content_classification(f"Content for classification {item_id}")
            else:
                result = await processor.process_text_generation(f"Generate content {item_id}", 50)
            
            result["load_item_id"] = item_id
            return result
        
        start_time = time.time()
        
        load_tasks = [process_load_item(i) for i in range(load_level)]
        load_results = await asyncio.gather(*load_tasks, return_exceptions=True)
        
        end_time = time.time()
        
        # Analyze this load level
        valid_results = [r for r in load_results if isinstance(r, dict)]
        successful_results = [r for r in valid_results if r["success"]]
        
        success_rate = len(successful_results) / len(valid_results) if valid_results else 0
        total_duration = end_time - start_time
        operations_per_second = len(successful_results) / total_duration if total_duration > 0 else 0
        
        processing_times = [r["processing_time_ms"] for r in successful_results if "processing_time_ms" in r]
        avg_processing_time = statistics.mean(processing_times) if processing_times else 0
        
        scalability_result = {
            "load_level": load_level,
            "success_rate": success_rate,
            "total_duration": total_duration,
            "operations_per_second": operations_per_second,
            "avg_processing_time_ms": avg_processing_time,
            "successful_operations": len(successful_results)
        }
        
        scalability_results.append(scalability_result)
        
        # Brief pause between load levels
        await asyncio.sleep(1)
    
    # Analyze scalability
    success_rates = [r["success_rate"] for r in scalability_results]
    ops_per_second = [r["operations_per_second"] for r in scalability_results]
    avg_processing_times = [r["avg_processing_time_ms"] for r in scalability_results]
    
    # Check scalability characteristics
    min_success_rate = min(success_rates)
    max_ops_per_second = max(ops_per_second)
    processing_time_increase = max(avg_processing_times) / min(avg_processing_times) if min(avg_processing_times) > 0 else 1
    
    # Assertions
    assert min_success_rate >= 0.85, f"Minimum success rate across load levels too low: {min_success_rate:.2f}"
    assert max_ops_per_second >= 15, f"Peak operations per second too low: {max_ops_per_second:.2f}"
    assert processing_time_increase <= 2.0, f"Processing time degradation too high: {processing_time_increase:.2f}x"
    
    # Check that OPS scales reasonably with load
    for i in range(1, len(ops_per_second)):
        load_ratio = load_levels[i] / load_levels[i-1]
        ops_ratio = ops_per_second[i] / ops_per_second[i-1] if ops_per_second[i-1] > 0 else 1
        
        # OPS should scale at least 50% as well as load
        min_scaling_ratio = 0.5
        assert ops_ratio >= (load_ratio * min_scaling_ratio), f"Poor scaling at level {load_levels[i]}: {ops_ratio:.2f} vs expected {load_ratio:.2f}"
    
    logger.info(f"AI scalability test completed - Max OPS: {max_ops_per_second:.2f}, "
                f"Min success rate: {min_success_rate:.2f}, "
                f"Processing time increase: {processing_time_increase:.2f}x")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_mixed_ai_workload_performance():
    """Test performance with mixed AI workload (different operation types and complexities)."""
    processor = MockAIProcessor()
    
    # Define workload mix
    workload_specs = [
        {"operation": "sentiment_analysis", "count": 10, "params": {"text": "Sample text for sentiment analysis"}},
        {"operation": "content_classification", "count": 8, "params": {"content": "Content for classification analysis"}},
        {"operation": "text_generation", "count": 5, "params": {"prompt": "Generate creative content", "max_length": 75}},
        {"operation": "image_analysis", "count": 3, "params": {"image_size_kb": 500}},
        {"operation": "audio_analysis", "count": 2, "params": {"audio_duration_seconds": 60}}
    ]
    
    workload_tasks = []
    task_id = 0
    
    # Create mixed workload tasks
    for spec in workload_specs:
        for i in range(spec["count"]):
            workload_tasks.append({
                "task_id": task_id,
                "operation": spec["operation"],
                "params": spec["params"].copy()
            })
            task_id += 1
    
    # Shuffle workload for realistic execution pattern
    random.shuffle(workload_tasks)
    
    async def execute_workload_task(task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workload task."""
        try:
            start_time = time.time()
            
            if task["operation"] == "sentiment_analysis":
                result = await processor.process_sentiment_analysis(task["params"]["text"])
            elif task["operation"] == "content_classification":
                result = await processor.process_content_classification(task["params"]["content"])
            elif task["operation"] == "text_generation":
                result = await processor.process_text_generation(
                    task["params"]["prompt"], 
                    task["params"]["max_length"]
                )
            elif task["operation"] == "image_analysis":
                result = await processor.process_image_analysis(task["params"]["image_size_kb"])
            elif task["operation"] == "audio_analysis":
                result = await processor.process_audio_analysis(task["params"]["audio_duration_seconds"])
            else:
                result = {"success": False, "error": "Unknown operation"}
            
            end_time = time.time()
            
            result["task_id"] = task["task_id"]
            result["total_execution_time_ms"] = (end_time - start_time) * 1000
            
            return result
            
        except Exception as e:
            return {
                "task_id": task["task_id"],
                "operation": task["operation"],
                "success": False,
                "error": str(e),
                "total_execution_time_ms": 0
            }
    
    # Execute mixed workload
    start_time = time.time()
    
    # Limit concurrency to simulate real-world constraints
    semaphore = asyncio.Semaphore(15)
    
    async def controlled_task_execution(task):
        async with semaphore:
            return await execute_workload_task(task)
    
    tasks = [controlled_task_execution(task) for task in workload_tasks]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    
    # Analyze mixed workload results
    valid_results = [r for r in results if isinstance(r, dict)]
    successful_results = [r for r in valid_results if r["success"]]
    
    # Overall metrics
    success_rate = len(successful_results) / len(valid_results) if valid_results else 0
    total_duration = end_time - start_time
    operations_per_second = len(successful_results) / total_duration if total_duration > 0 else 0
    
    # Operation-specific analysis
    operation_metrics = {}
    for result in successful_results:
        op_type = result.get("operation", "unknown")
        if op_type not in operation_metrics:
            operation_metrics[op_type] = []
        operation_metrics[op_type].append(result)
    
    # Calculate metrics per operation type
    operation_performance = {}
    for op_type, op_results in operation_metrics.items():
        processing_times = [r["processing_time_ms"] for r in op_results if "processing_time_ms" in r]
        execution_times = [r["total_execution_time_ms"] for r in op_results]
        
        operation_performance[op_type] = {
            "count": len(op_results),
            "success_rate": len(op_results) / sum(1 for r in valid_results if r.get("operation") == op_type),
            "avg_processing_time_ms": statistics.mean(processing_times) if processing_times else 0,
            "avg_execution_time_ms": statistics.mean(execution_times) if execution_times else 0
        }
    
    # Assertions
    assert success_rate >= 0.90, f"Mixed workload success rate too low: {success_rate:.2f}"
    assert operations_per_second >= 8, f"Mixed workload operations per second too low: {operations_per_second:.2f}"
    
    # Operation-specific assertions
    for op_type, metrics in operation_performance.items():
        assert metrics["success_rate"] >= 0.85, f"{op_type} success rate too low: {metrics['success_rate']:.2f}"
        
        # Check reasonable processing times per operation type
        expected_max_times = {
            "sentiment_analysis": 300,
            "content_classification": 500,
            "text_generation": 2000,
            "image_analysis": 3000,
            "audio_analysis": 4000
        }
        
        max_expected = expected_max_times.get(op_type, 1000)
        assert metrics["avg_processing_time_ms"] < max_expected, f"{op_type} processing time too high: {metrics['avg_processing_time_ms']:.2f}ms"
    
    logger.info(f"Mixed AI workload test completed - Total tasks: {len(workload_tasks)}, "
                f"Success rate: {success_rate:.2f}, OPS: {operations_per_second:.2f}")
    
    for op_type, metrics in operation_performance.items():
        logger.info(f"  {op_type}: {metrics['count']} tasks, "
                    f"success_rate={metrics['success_rate']:.2f}, "
                    f"avg_time={metrics['avg_processing_time_ms']:.2f}ms")


@pytest.mark.performance
@pytest.mark.slow
async def test_ai_endurance_processing():
    """Test AI processing endurance over extended time."""
    processor = MockAIProcessor()
    test_duration_minutes = 1  # Reduced for testing, normally would be longer
    operations_per_minute = 60
    
    test_duration_seconds = test_duration_minutes * 60
    total_operations = operations_per_minute * test_duration_minutes
    operation_interval = test_duration_seconds / total_operations
    
    endurance_results = []
    
    async def continuous_ai_processing():
        """Continuously process AI operations for the test duration."""
        start_time = time.time()
        operation_count = 0
        
        while (time.time() - start_time) < test_duration_seconds:
            operation_start = time.time()
            
            # Rotate through different operation types
            operations = [
                ("sentiment", lambda: processor.process_sentiment_analysis(f"Endurance test text {operation_count}")),
                ("classification", lambda: processor.process_content_classification(f"Endurance content {operation_count}")),
                ("generation", lambda: processor.process_text_generation(f"Generate for endurance {operation_count}", 30))
            ]
            
            operation_type, operation_func = operations[operation_count % len(operations)]
            
            try:
                result = await operation_func()
                result["endurance_operation_id"] = operation_count
                result["operation_type"] = operation_type
                result["elapsed_time"] = time.time() - start_time
                endurance_results.append(result)
                
            except Exception as e:
                error_result = {
                    "endurance_operation_id": operation_count,
                    "operation_type": operation_type,
                    "success": False,
                    "error": str(e),
                    "elapsed_time": time.time() - start_time
                }
                endurance_results.append(error_result)
            
            operation_count += 1
            
            # Rate limiting
            operation_end = time.time()
            elapsed = operation_end - operation_start
            sleep_time = operation_interval - elapsed
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
    
    # Run endurance test
    await continuous_ai_processing()
    
    # Analyze endurance results
    successful_results = [r for r in endurance_results if r.get("success", False)]
    total_operations_completed = len(endurance_results)
    success_rate = len(successful_results) / total_operations_completed if total_operations_completed > 0 else 0
    
    # Time-based analysis
    time_buckets = {}
    bucket_size_seconds = 15  # 15-second buckets
    
    for result in successful_results:
        bucket = int(result["elapsed_time"] // bucket_size_seconds)
        if bucket not in time_buckets:
            time_buckets[bucket] = []
        time_buckets[bucket].append(result)
    
    # Check for performance degradation over time
    bucket_performance = []
    for bucket_id in sorted(time_buckets.keys()):
        bucket_results = time_buckets[bucket_id]
        processing_times = [r["processing_time_ms"] for r in bucket_results if "processing_time_ms" in r]
        
        if processing_times:
            bucket_performance.append({
                "bucket": bucket_id,
                "avg_processing_time": statistics.mean(processing_times),
                "operation_count": len(bucket_results)
            })
    
    # Calculate performance stability
    if len(bucket_performance) >= 2:
        first_half = bucket_performance[:len(bucket_performance)//2]
        second_half = bucket_performance[len(bucket_performance)//2:]
        
        first_half_avg = statistics.mean([b["avg_processing_time"] for b in first_half])
        second_half_avg = statistics.mean([b["avg_processing_time"] for b in second_half])
        
        performance_degradation = second_half_avg / first_half_avg if first_half_avg > 0 else 1
    else:
        performance_degradation = 1.0
    
    # Operation type analysis
    operation_types = {}
    for result in successful_results:
        op_type = result.get("operation_type", "unknown")
        if op_type not in operation_types:
            operation_types[op_type] = []
        operation_types[op_type].append(result)
    
    # Assertions
    assert success_rate >= 0.85, f"Endurance success rate too low: {success_rate:.2f}"
    assert total_operations_completed >= (total_operations * 0.8), f"Too few operations completed: {total_operations_completed}"
    assert performance_degradation <= 1.5, f"Performance degradation too high: {performance_degradation:.2f}x"
    
    # Check each operation type maintained reasonable performance
    for op_type, op_results in operation_types.items():
        op_processing_times = [r["processing_time_ms"] for r in op_results if "processing_time_ms" in r]
        op_avg_time = statistics.mean(op_processing_times) if op_processing_times else 0
        
        expected_max_times = {
            "sentiment": 300,
            "classification": 500,
            "generation": 2000
        }
        
        max_expected = expected_max_times.get(op_type, 1000)
        assert op_avg_time < max_expected, f"Endurance {op_type} processing time too high: {op_avg_time:.2f}ms"
    
    logger.info(f"AI endurance test completed - Duration: {test_duration_minutes}min, "
                f"Operations: {total_operations_completed}, Success rate: {success_rate:.2f}, "
                f"Performance degradation: {performance_degradation:.2f}x")