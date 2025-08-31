"""Serializers Usage Examples
===========================

Complete usage examples for the IA-Influencer-Agent serialization system.
Demonstrates advanced orchestration, batch processing, and enterprise features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

# Import the serialization system
from . import (
    get_serializer_index,
    SerializerType,
    OperationType,
    Priority,
    ContentData,
    SurveillanceData,
    PlatformData,
    FingerprintData,
    ViolationData,
    AnalyticsData
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def basic_serialization_example():
    """Basic serialization example using the index."""    logger.info("=== Basic Serialization Example ===")
    
    # Get the serializer index
    serializer_index = get_serializer_index(enable_orchestrator=True, max_workers=5)
    
    # Create sample content data
    content = ContentData(
        content_id="example_content_001",
        content_type="audio",
        file_size=2048576,
        file_format="mp3",
        metadata={
            "title": "Example Audio Track",
            "artist": "Test Artist",
            "duration": 180.0
        }
    )
    
    # Serialize with high priority
    task_id = await serializer_index.serialize(
        data=content,
        serializer_type=SerializerType.CONTENT,
        priority=Priority.HIGH
    )
    
    logger.info(f"Serialization task submitted: {task_id}")
    
    # Check task status
    await asyncio.sleep(1)  # Allow processing time
    status = serializer_index.orchestrator.get_task_status(task_id)
    logger.info(f"Task status: {status}")
    
    return content

async def batch_processing_example():
    """Demonstrate batch processing capabilities."""    logger.info("=== Batch Processing Example ===")
    
    serializer_index = get_serializer_index()
    
    # Create multiple content objects
    content_list = []
    for i in range(10):
        content = ContentData(
            content_id=f"batch_content_{i:03d}",
            content_type="video" if i % 2 == 0 else "audio",
            file_size=1024 * 1024 * (i + 1),
            file_format="mp4" if i % 2 == 0 else "mp3",
            metadata={
                "title": f"Batch Content {i}",
                "duration": 120.0 + (i * 10)
            }
        )
        content_list.append(content)
    
    # Batch serialize with normal priority
    batch_task_id = await serializer_index.batch_serialize(
        data_list=content_list,
        serializer_type=SerializerType.CONTENT,
        priority=Priority.NORMAL
    )
    
    logger.info(f"Batch processing task submitted: {batch_task_id}")
    
    return content_list

async def multi_serializer_example():
    """Example using multiple serializer types."""    logger.info("=== Multi-Serializer Example ===")
    
    serializer_index = get_serializer_index()
    
    # Create different types of data
    
    # Content data
    content = ContentData(
        content_id="multi_content_001",
        content_type="video",
        file_size=10485760,
        file_format="mp4"
    )
    
    # Surveillance data
    surveillance = SurveillanceData(
        surveillance_id="surveillance_001",
        content_id="multi_content_001",
        detection_type="copyright_violation",
        confidence_score=0.95,
        detection_method="fingerprint_matching"
    )
    
    # Platform data
    platform = PlatformData(
        platform_id="youtube_001",
        content_id="multi_content_001",
        platform_name="youtube",
        platform_url="https://youtube.com/watch?v=example",
        upload_status="published"
    )
    
    # Fingerprint data
    fingerprint = FingerprintData(
        fingerprint_id="fp_001",
        content_id="multi_content_001",
        fingerprint_type="audio_spectral",
        fingerprint_data=b"fingerprint_bytes_here",
        algorithm="chromaprint"
    )
    
    # Submit all serialization tasks
    tasks = []
    
    tasks.append(await serializer_index.serialize(
        content, SerializerType.CONTENT, Priority.HIGH
    ))
    
    tasks.append(await serializer_index.serialize(
        surveillance, SerializerType.SURVEILLANCE, Priority.CRITICAL
    ))
    
    tasks.append(await serializer_index.serialize(
        platform, SerializerType.PLATFORM, Priority.NORMAL
    ))
    
    tasks.append(await serializer_index.serialize(
        fingerprint, SerializerType.FINGERPRINT, Priority.HIGH
    ))
    
    logger.info(f"Submitted {len(tasks)} serialization tasks")
    
    # Wait for processing and check statuses
    await asyncio.sleep(2)
    
    for task_id in tasks:
        status = serializer_index.orchestrator.get_task_status(task_id)
        logger.info(f"Task {task_id}: {status['status'] if status else 'Unknown'}")
    
    return tasks

async def performance_monitoring_example():
    """Demonstrate performance monitoring and metrics."""    logger.info("=== Performance Monitoring Example ===")
    
    serializer_index = get_serializer_index()
    
    # Generate some workload
    tasks = []
    
    # Create mixed workload
    for i in range(50):
        if i % 5 == 0:
            # High priority content
            content = ContentData(
                content_id=f"perf_content_{i}",
                content_type="video",
                file_size=5242880,
                file_format="mp4"
            )
            task_id = await serializer_index.serialize(
                content, SerializerType.CONTENT, Priority.HIGH
            )
        elif i % 3 == 0:
            # Analytics data
            analytics = AnalyticsData(
                analytics_id=f"analytics_{i}",
                content_id=f"perf_content_{i}",
                metric_type="engagement",
                metric_value=float(i * 10),
                platform="youtube"
            )
            task_id = await serializer_index.serialize(
                analytics, SerializerType.ANALYTICS, Priority.NORMAL
            )
        else:
            # Surveillance data
            surveillance = SurveillanceData(
                surveillance_id=f"surveillance_{i}",
                content_id=f"perf_content_{i}",
                detection_type="content_match",
                confidence_score=0.8 + (i % 20) / 100,
                detection_method="hash_matching"
            )
            task_id = await serializer_index.serialize(
                surveillance, SerializerType.SURVEILLANCE, Priority.HIGH
            )
        
        tasks.append(task_id)
    
    logger.info(f"Generated workload with {len(tasks)} tasks")
    
    # Wait for processing
    await asyncio.sleep(5)
    
    # Get comprehensive metrics
    metrics = serializer_index.get_metrics()
    if metrics:
        logger.info("=== System Metrics ===")
        logger.info(f"Total operations: {metrics.total_operations}")
        logger.info(f"Successful operations: {metrics.successful_operations}")
        logger.info(f"Failed operations: {metrics.failed_operations}")
        logger.info(f"Success rate: {(metrics.successful_operations / max(metrics.total_operations, 1)) * 100:.2f}%")
        logger.info(f"Average processing time: {metrics.average_processing_time:.3f}s")
        logger.info(f"Throughput: {metrics.throughput_ops_per_second:.2f} ops/sec")
        logger.info(f"P95 latency: {metrics.p95_latency:.3f}s")
        logger.info(f"P99 latency: {metrics.p99_latency:.3f}s")
        logger.info(f"Queue size: {metrics.queue_size}")
        logger.info(f"Active workers: {metrics.active_workers}")
        logger.info(f"Error rate: {metrics.error_rate:.4f}")
        
        # Per-serializer metrics
        logger.info("=== Per-Serializer Metrics ===")
        for serializer_name, serializer_metrics in metrics.serializer_metrics.items():
            logger.info(f"{serializer_name}: {serializer_metrics}")
        
        # Error types
        if metrics.error_types:
            logger.info("=== Error Types ===")
            for error_type, count in metrics.error_types.items():
                logger.info(f"{error_type}: {count}")
    
    return tasks, metrics

async def direct_serializer_access_example():
    """Example of direct serializer access without orchestrator."""    logger.info("=== Direct Serializer Access Example ===")
    
    # Create index without orchestrator for direct access
    serializer_index = get_serializer_index(enable_orchestrator=False)
    
    # Get direct access to content serializer
    content_serializer = serializer_index.get_serializer(SerializerType.CONTENT)
    
    # Create content data
    content = ContentData(
        content_id="direct_content_001",
        content_type="image",
        file_size=1048576,
        file_format="jpg",
        metadata={
            "width": 1920,
            "height": 1080,
            "color_space": "RGB"
        }
    )
    
    # Direct serialization
    start_time = datetime.now()
    serialized = content_serializer.serialize_content(content)
    serialization_time = (datetime.now() - start_time).total_seconds()
    
    logger.info(f"Direct serialization completed in {serialization_time:.3f}s")
    logger.info(f"Serialized size: {len(serialized)} bytes")
    
    # Direct deserialization
    start_time = datetime.now()
    deserialized = content_serializer.deserialize_content(serialized)
    deserialization_time = (datetime.now() - start_time).total_seconds()
    
    logger.info(f"Direct deserialization completed in {deserialization_time:.3f}s")
    logger.info(f"Data integrity check: {content.content_id == deserialized.content_id}")
    
    return content, serialized, deserialized

async def error_handling_example():
    """Demonstrate error handling and circuit breaker patterns."""    logger.info("=== Error Handling Example ===")
    
    serializer_index = get_serializer_index()
    
    # Create invalid data to trigger errors
    invalid_data = {
        "invalid_field": "this_will_cause_validation_error",
        "missing_required_fields": True
    }
    
    try:
        # Attempt to serialize invalid data
        task_id = await serializer_index.serialize(
            invalid_data,
            SerializerType.CONTENT,
            Priority.NORMAL
        )
        
        # Wait and check task status
        await asyncio.sleep(2)
        status = serializer_index.orchestrator.get_task_status(task_id)
        
        if status and status.get('status') == 'failed':
            logger.info(f"Expected error handled gracefully: {status.get('error')}")
        
    except Exception as e:
        logger.info(f"Exception caught and handled: {e}")
    
    # Get metrics to see error tracking
    metrics = serializer_index.get_metrics()
    if metrics and metrics.error_types:
        logger.info(f"Error types recorded: {metrics.error_types}")

async def caching_example():
    """Demonstrate caching capabilities."""    logger.info("=== Caching Example ===")
    
    serializer_index = get_serializer_index()
    
    # Create content for caching test
    content = ContentData(
        content_id="cache_test_001",
        content_type="audio",
        file_size=3145728,
        file_format="flac"
    )
    
    # First serialization (cache miss)
    start_time = datetime.now()
    task_id_1 = await serializer_index.serialize(
        content, SerializerType.CONTENT, Priority.NORMAL
    )
    first_time = (datetime.now() - start_time).total_seconds()
    
    await asyncio.sleep(1)
    
    # Second serialization (cache hit)
    start_time = datetime.now()
    task_id_2 = await serializer_index.serialize(
        content, SerializerType.CONTENT, Priority.NORMAL
    )
    second_time = (datetime.now() - start_time).total_seconds()
    
    logger.info(f"First serialization: {first_time:.3f}s")
    logger.info(f"Second serialization: {second_time:.3f}s")
    logger.info(f"Cache speedup: {first_time / max(second_time, 0.001):.2f}x")
    
    # Clear cache
    serializer_index.orchestrator.clear_cache()
    logger.info("Cache cleared")

async def main():
    """Run all examples."""    logger.info("🚀 Starting IA-Influencer-Agent Serialization System Examples")
    logger.info("=" * 70)
    
    try:
        # Run all examples
        await basic_serialization_example()
        await asyncio.sleep(1)
        
        await batch_processing_example()
        await asyncio.sleep(1)
        
        await multi_serializer_example()
        await asyncio.sleep(1)
        
        await performance_monitoring_example()
        await asyncio.sleep(1)
        
        await direct_serializer_access_example()
        await asyncio.sleep(1)
        
        await error_handling_example()
        await asyncio.sleep(1)
        
        await caching_example()
        
        logger.info("=" * 70)
        logger.info("✅ All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Example execution failed: {e}")
        raise
    
    finally:
        # Cleanup
        from . import reset_serializer_index
        reset_serializer_index()
        logger.info("🧹 Cleanup completed")

if __name__ == "__main__":
    asyncio.run(main())
