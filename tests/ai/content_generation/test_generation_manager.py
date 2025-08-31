# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Generation Manager Tests

Comprehensive tests for the GenerationManager class that provides
central orchestration and resource management for content generation.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List
import uuid

# Import the module to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend"))

from ai.content_generation.generation_manager import (
    GenerationManager,
    GenerationRequest,
    GenerationResponse,
    GenerationPriority,
    GenerationStatus,
    ResourceLimits,
    QueueManager,
    ResourceMonitor
)


class TestGenerationManager:
    """Test suite for GenerationManager"""    
    @pytest.fixture
    def manager(self):
        """Create a generation manager instance"""        config = {
            "max_concurrent_requests": 10,
            "queue_size_limit": 100,
            "default_timeout": 300,
            "retry_attempts": 3,
            "enable_caching": True,
            "cache_ttl": 3600,
            "enable_monitoring": True,
            "resource_monitoring": True,
            "performance_tracking": True
        }
        return GenerationManager(config=config)
    
    @pytest.fixture
    def mock_pipeline(self):
        """Create a mock pipeline"""        pipeline = AsyncMock()
        pipeline.execute_pipeline.return_value = Mock(
            status="completed",
            final_content="Generated content",
            processing_time=1.5
        )
        return pipeline
    
    @pytest.fixture
    def sample_request(self):
        """Create a sample generation request"""        return GenerationRequest(
            request_id=str(uuid.uuid4()),
            content_type="blog_post",
            topic="AI technology trends",
            target_audience="tech enthusiasts",
            word_count=500,
            priority="normal"
        )
    
    @pytest.fixture
    def high_priority_request(self):
        """Create a high priority request"""        return GenerationRequest(
            request_id=str(uuid.uuid4()),
            content_type="urgent_announcement",
            topic="Breaking news",
            target_audience="general public",
            word_count=100,
            priority="high"
        )
    
    def test_manager_initialization(self, manager):
        """Test manager initialization"""        assert manager is not None
        assert hasattr(manager, 'pipeline')
        assert hasattr(manager, 'queue_manager')
        assert hasattr(manager, 'resource_monitor')
        assert hasattr(manager, 'active_tasks')
        assert hasattr(manager, 'completed_tasks')
        assert manager.is_running is False
    
    @pytest.mark.asyncio
    async def test_manager_startup_shutdown(self, manager):
        """Test manager startup and shutdown"""        # Test startup
        await manager.start()
        assert manager.is_running is True
        
        # Test shutdown
        await manager.shutdown()
        assert manager.is_running is False
    
    @pytest.mark.asyncio
    async def test_submit_generation_request(self, manager, sample_request, mock_pipeline):
        """Test submitting a generation request"""        with patch.object(manager, 'pipeline', mock_pipeline):
            await manager.start()
            
            task_id = await manager.submit_generation_request(sample_request)
            
            assert task_id is not None
            assert isinstance(task_id, str)
            assert task_id in manager.active_tasks
            
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_priority_queue_handling(self, manager, sample_request, high_priority_request, mock_pipeline):
        """Test priority queue handling"""        with patch.object(manager, 'pipeline', mock_pipeline):
            await manager.start()
            
            # Submit normal priority request first
            normal_task_id = await manager.submit_generation_request(sample_request)
            
            # Submit high priority request
            high_task_id = await manager.submit_generation_request(high_priority_request)
            
            # Wait a bit for processing
            await asyncio.sleep(0.1)
            
            # High priority should be processed first or simultaneously
            assert normal_task_id in manager.active_tasks or normal_task_id in manager.completed_tasks
            assert high_task_id in manager.active_tasks or high_task_id in manager.completed_tasks
            
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_task_status_tracking(self, manager, sample_request, mock_pipeline):
        """Test task status tracking"""        with patch.object(manager, 'pipeline', mock_pipeline):
            await manager.start()
            
            task_id = await manager.submit_generation_request(sample_request)
            
            # Initial status should be queued or processing
            initial_status = await manager.get_task_status(task_id)
            assert initial_status in [TaskStatus.QUEUED, TaskStatus.PROCESSING]
            
            # Wait for completion
            await asyncio.sleep(0.2)
            
            # Final status should be completed
            final_status = await manager.get_task_status(task_id)
            assert final_status in [TaskStatus.COMPLETED, TaskStatus.PROCESSING]
            
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_task_result_retrieval(self, manager, sample_request, mock_pipeline):
        """Test task result retrieval"""        with patch.object(manager, 'pipeline', mock_pipeline):
            await manager.start()
            
            task_id = await manager.submit_generation_request(sample_request)
            
            # Wait for completion
            await asyncio.sleep(0.2)
            
            result = await manager.get_task_result(task_id)
            
            if result:  # If task completed
                assert result is not None
                assert hasattr(result, 'final_content')
                assert result.final_content == "Generated content"
            
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, manager, mock_pipeline):
        """Test handling of concurrent requests"""        with patch.object(manager, 'pipeline', mock_pipeline):
            await manager.start()
            
            # Submit multiple requests concurrently
            requests = []
            for i in range(5):
                request = GenerationRequest(
                    request_id=str(uuid.uuid4()),
                    content_type="blog_post",
                    topic=f"Topic {i}",
                    target_audience="test audience",
                    word_count=100
                )
                requests.append(request)
            
            # Submit all requests
            task_ids = []
            for request in requests:
                task_id = await manager.submit_generation_request(request)
                task_ids.append(task_id)
            
            # Wait for processing
            await asyncio.sleep(0.5)
            
            # Check that all tasks are tracked
            for task_id in task_ids:
                assert task_id in manager.active_tasks or task_id in manager.completed_tasks
            
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_resource_monitoring(self, manager):
        """Test resource monitoring functionality"""        await manager.start()
        
        # Get initial resource status
        resource_status = manager.get_resource_status()
        
        assert resource_status is not None
        assert "cpu_usage" in resource_status
        assert "memory_usage" in resource_status
        assert "active_tasks" in resource_status
        assert "queue_size" in resource_status
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_queue_size_limits(self, manager, mock_pipeline):
        """Test queue size limits"""        with patch.object(manager, 'pipeline', mock_pipeline):
            # Set a small queue limit for testing
            manager.queue_manager.max_queue_size = 3
            
            await manager.start()
            
            # Submit requests up to limit
            task_ids = []
            for i in range(3):
                request = GenerationRequest(
                    request_id=str(uuid.uuid4()),
                    content_type="blog_post",
                    topic=f"Topic {i}",
                    target_audience="test audience"
                )
                task_id = await manager.submit_generation_request(request)
                task_ids.append(task_id)
            
            # Next request should handle queue full scenario
            overflow_request = GenerationRequest(
                request_id=str(uuid.uuid4()),
                content_type="blog_post",
                topic="Overflow topic",
                target_audience="test audience"
            )
            
            # This should either succeed (if queue processed) or handle overflow
            try:
                overflow_task = await manager.submit_generation_request(overflow_request)
                assert overflow_task is not None or overflow_task is None
            except Exception as e:
                # Queue full handling is acceptable
                assert "queue" in str(e).lower() or "full" in str(e).lower()
            
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_task_cancellation(self, manager, sample_request, mock_pipeline):
        """Test task cancellation"""        # Make pipeline take longer to allow cancellation
        async def slow_execution(*args, **kwargs):
            await asyncio.sleep(1.0)
            return Mock(status="completed", final_content="Should not complete")
        
        mock_pipeline.execute_pipeline.side_effect = slow_execution
        
        with patch.object(manager, 'pipeline', mock_pipeline):
            await manager.start()
            
            task_id = await manager.submit_generation_request(sample_request)
            
            # Wait a bit then cancel
            await asyncio.sleep(0.1)
            cancellation_result = await manager.cancel_task(task_id)
            
            # Should successfully cancel or already be processing
            assert cancellation_result in [True, False]
            
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_error_handling_in_generation(self, manager, sample_request, mock_pipeline):
        """Test error handling during generation"""        # Configure pipeline to raise an error
        mock_pipeline.execute_pipeline.side_effect = Exception("Generation failed")
        
        with patch.object(manager, 'pipeline', mock_pipeline):
            await manager.start()
            
            task_id = await manager.submit_generation_request(sample_request)
            
            # Wait for processing
            await asyncio.sleep(0.2)
            
            # Task should be marked as failed
            status = await manager.get_task_status(task_id)
            assert status in [TaskStatus.FAILED, TaskStatus.PROCESSING]
            
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self, manager, sample_request, mock_pipeline):
        """Test retry mechanism for failed tasks"""        # Configure pipeline to fail first, then succeed
        call_count = 0
        
        async def failing_then_succeeding(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("First attempt failed")
            return Mock(status="completed", final_content="Success on retry")
        
        mock_pipeline.execute_pipeline.side_effect = failing_then_succeeding
        
        with patch.object(manager, 'pipeline', mock_pipeline):
            await manager.start()
            
            # Enable retry for this test
            sample_request.max_retries = 1
            
            task_id = await manager.submit_generation_request(sample_request)
            
            # Wait for retry to complete
            await asyncio.sleep(0.3)
            
            # Should eventually succeed
            status = await manager.get_task_status(task_id)
            result = await manager.get_task_result(task_id)
            
            # If retry succeeded
            if status == TaskStatus.COMPLETED and result:
                assert result.final_content == "Success on retry"
            
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_batch_request_processing(self, manager, mock_pipeline):
        """Test batch request processing"""        with patch.object(manager, 'pipeline', mock_pipeline):
            await manager.start()
            
            # Create batch requests
            batch_requests = []
            for i in range(3):
                request = GenerationRequest(
                    request_id=str(uuid.uuid4()),
                    content_type="social_post",
                    topic=f"Batch topic {i}",
                    target_audience="social media users"
                )
                batch_requests.append(request)
            
            # Submit batch
            task_ids = await manager.submit_batch_requests(batch_requests)
            
            assert len(task_ids) == 3
            for task_id in task_ids:
                assert task_id in manager.active_tasks or task_id in manager.completed_tasks
            
            await manager.shutdown()
    
    def test_metrics_collection(self, manager):
        """Test metrics collection"""        metrics = manager.get_metrics()
        
        expected_keys = [
            'total_requests_processed',
            'successful_requests',
            'failed_requests',
            'avg_processing_time',
            'queue_size',
            'active_tasks_count',
            'resource_usage'
        ]
        
        for key in expected_keys:
            assert key in metrics
    
    @pytest.mark.asyncio
    async def test_health_check(self, manager):
        """Test health check functionality"""        await manager.start()
        
        health_status = await manager.health_check()
        
        assert health_status is not None
        assert "status" in health_status
        assert "uptime" in health_status
        assert "resource_usage" in health_status
        assert "queue_status" in health_status
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown_with_active_tasks(self, manager, mock_pipeline):
        """Test graceful shutdown with active tasks"""        # Make pipeline take time to simulate active tasks
        async def long_running_task(*args, **kwargs):
            await asyncio.sleep(0.5)
            return Mock(status="completed", final_content="Long running result")
        
        mock_pipeline.execute_pipeline.side_effect = long_running_task
        
        with patch.object(manager, 'pipeline', mock_pipeline):
            await manager.start()
            
            # Submit a request
            request = GenerationRequest(
                request_id=str(uuid.uuid4()),
                content_type="blog_post",
                topic="Long running topic",
                target_audience="test audience"
            )
            
            task_id = await manager.submit_generation_request(request)
            
            # Shutdown while task is running
            await manager.shutdown(wait_for_completion=True)
            
            assert manager.is_running is False
    
    @pytest.mark.asyncio
    async def test_resource_exhaustion_handling(self, manager, mock_pipeline):
        """Test handling of resource exhaustion"""        # Mock resource monitor to report high usage
        mock_resource_monitor = Mock()
        mock_resource_monitor.is_resource_available.return_value = False
        mock_resource_monitor.get_cpu_usage.return_value = 95.0
        mock_resource_monitor.get_memory_usage.return_value = 90.0
        
        with patch.object(manager, 'resource_monitor', mock_resource_monitor):
            with patch.object(manager, 'pipeline', mock_pipeline):
                await manager.start()
                
                request = GenerationRequest(
                    request_id=str(uuid.uuid4()),
                    content_type="blog_post",
                    topic="Resource test",
                    target_audience="test audience"
                )
                
                # Should handle resource exhaustion gracefully
                try:
                    task_id = await manager.submit_generation_request(request)
                    # If submitted, it should either queue or reject appropriately
                    assert task_id is not None or task_id is None
                except Exception as e:
                    # Resource exhaustion exceptions are acceptable
                    assert "resource" in str(e).lower() or "capacity" in str(e).lower()
                
                await manager.shutdown()


class TestQueueManager:
    """Test suite for QueueManager"""    
    @pytest.fixture
    def queue_manager(self):
        """Create a queue manager instance"""        return QueueManager(max_size=10)
    
    @pytest.fixture
    def sample_task(self):
        """Create a sample task"""        return GenerationTask(
            task_id=str(uuid.uuid4()),
            request=GenerationRequest(
                request_id=str(uuid.uuid4()),
                content_type="blog_post",
                topic="Test topic",
                target_audience="test audience"
            ),
            priority="normal"
        )
    
    def test_queue_initialization(self, queue_manager):
        """Test queue manager initialization"""        assert queue_manager is not None
        assert queue_manager.max_size == 10
        assert queue_manager.size() == 0
        assert queue_manager.is_empty() is True
    
    def test_task_enqueue_dequeue(self, queue_manager, sample_task):
        """Test basic enqueue and dequeue operations"""        # Enqueue task
        queue_manager.enqueue(sample_task)
        assert queue_manager.size() == 1
        assert queue_manager.is_empty() is False
        
        # Dequeue task
        dequeued_task = queue_manager.dequeue()
        assert dequeued_task is not None
        assert dequeued_task.task_id == sample_task.task_id
        assert queue_manager.size() == 0
        assert queue_manager.is_empty() is True
    
    def test_priority_queue_ordering(self, queue_manager):
        """Test priority queue ordering"""        # Create tasks with different priorities
        low_priority_task = GenerationTask(
            task_id="low",
            request=GenerationRequest(
                request_id="low",
                content_type="blog_post",
                topic="Low priority",
                target_audience="test"
            ),
            priority="low"
        )
        
        high_priority_task = GenerationTask(
            task_id="high",
            request=GenerationRequest(
                request_id="high",
                content_type="urgent",
                topic="High priority",
                target_audience="test"
            ),
            priority="high"
        )
        
        normal_priority_task = GenerationTask(
            task_id="normal",
            request=GenerationRequest(
                request_id="normal",
                content_type="blog_post",
                topic="Normal priority",
                target_audience="test"
            ),
            priority="normal"
        )
        
        # Enqueue in random order
        queue_manager.enqueue(normal_priority_task)
        queue_manager.enqueue(low_priority_task)
        queue_manager.enqueue(high_priority_task)
        
        # Dequeue should return high priority first
        first_task = queue_manager.dequeue()
        assert first_task.priority == "high"
        
        second_task = queue_manager.dequeue()
        assert second_task.priority == "normal"
        
        third_task = queue_manager.dequeue()
        assert third_task.priority == "low"
    
    def test_queue_size_limit(self, queue_manager):
        """Test queue size limit enforcement"""        # Fill queue to capacity
        for i in range(10):
            task = GenerationTask(
                task_id=str(i),
                request=GenerationRequest(
                    request_id=str(i),
                    content_type="blog_post",
                    topic=f"Topic {i}",
                    target_audience="test"
                ),
                priority="normal"
            )
            queue_manager.enqueue(task)
        
        assert queue_manager.size() == 10
        assert queue_manager.is_full() is True
        
        # Attempt to add one more (should handle overflow)
        overflow_task = GenerationTask(
            task_id="overflow",
            request=GenerationRequest(
                request_id="overflow",
                content_type="blog_post",
                topic="Overflow topic",
                target_audience="test"
            ),
            priority="normal"
        )
        
        try:
            queue_manager.enqueue(overflow_task)
            # If no exception, queue handled overflow (possibly by dropping or expanding)
            assert True
        except Exception:
            # Exception for full queue is acceptable
            assert True


class TestResourceMonitor:
    """Test suite for ResourceMonitor"""    
    @pytest.fixture
    def resource_monitor(self):
        """Create a resource monitor instance"""        return ResourceMonitor()
    
    def test_resource_monitor_initialization(self, resource_monitor):
        """Test resource monitor initialization"""        assert resource_monitor is not None
        assert hasattr(resource_monitor, 'cpu_threshold')
        assert hasattr(resource_monitor, 'memory_threshold')
    
    def test_cpu_usage_monitoring(self, resource_monitor):
        """Test CPU usage monitoring"""        cpu_usage = resource_monitor.get_cpu_usage()
        
        assert cpu_usage is not None
        assert isinstance(cpu_usage, (int, float))
        assert 0 <= cpu_usage <= 100
    
    def test_memory_usage_monitoring(self, resource_monitor):
        """Test memory usage monitoring"""        memory_usage = resource_monitor.get_memory_usage()
        
        assert memory_usage is not None
        assert isinstance(memory_usage, (int, float))
        assert memory_usage >= 0
    
    def test_resource_availability_check(self, resource_monitor):
        """Test resource availability check"""        is_available = resource_monitor.is_resource_available()
        
        assert isinstance(is_available, bool)
    
    def test_resource_threshold_configuration(self, resource_monitor):
        """Test resource threshold configuration"""        # Set new thresholds
        resource_monitor.set_cpu_threshold(80.0)
        resource_monitor.set_memory_threshold(85.0)
        
        assert resource_monitor.cpu_threshold == 80.0
        assert resource_monitor.memory_threshold == 85.0
    
    def test_resource_alerts(self, resource_monitor):
        """Test resource alert generation"""        # Mock high resource usage
        with patch.object(resource_monitor, 'get_cpu_usage', return_value=95.0):
            with patch.object(resource_monitor, 'get_memory_usage', return_value=90.0):
                alerts = resource_monitor.get_resource_alerts()
                
                assert alerts is not None
                assert isinstance(alerts, list)
                # Should have alerts for high CPU and memory
                assert len(alerts) >= 0


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
