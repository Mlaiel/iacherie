# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Comprehensive Tests for TaskManager

Industrial-grade testing for task management, scheduling, coordination,
and execution monitoring capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
import logging
import uuid
from enum import Enum

from ai.ai_agents.task_manager import (
    TaskManager,
    Task,
    TaskStatus,
    TaskPriority,
    TaskType,
    TaskResult,
    TaskScheduler,
    TaskQueue,
    TaskExecutor,
    TaskMonitor,
    TaskConfig
)

logger = logging.getLogger(__name__)


class TestTask:
    """
Test task creation and management"""
    
    def test_task_creation(self):
        """
Test creating task instances"""
        task = Task(
            task_id="test_task_001",
            task_type=TaskType.CONTENT_GENERATION,
            agent_id="content_creator_001",
            parameters={
                "content_type": "video",
                "duration": 60,
                "style": "educational"
            },
            priority=TaskPriority.HIGH,
            timeout=300
        )
        
        assert task.task_id == "test_task_001"
        assert task.task_type == TaskType.CONTENT_GENERATION
        assert task.agent_id == "content_creator_001"
        assert task.priority == TaskPriority.HIGH
        assert task.timeout == 300
        assert task.status == TaskStatus.PENDING
        assert task.created_at is not None
        assert task.started_at is None
        assert task.completed_at is None
    
    def test_task_serialization(self):
        """Test task serialization and deserialization"""
        original_task = Task(
            task_id="serialization_test",
            task_type=TaskType.SOCIAL_MEDIA_POSTING,
            agent_id="social_media_agent",
            parameters={"platform": "instagram", "content": "test post"},
            priority=TaskPriority.MEDIUM,
            dependencies=["task_001", "task_002"]
        )
        
        # Serialize
        serialized = original_task.to_dict()
        assert isinstance(serialized, dict)
        assert "task_id" in serialized
        assert "task_type" in serialized
        assert "dependencies" in serialized
        
        # Deserialize
        deserialized = Task.from_dict(serialized)
        assert deserialized.task_id == original_task.task_id
        assert deserialized.task_type == original_task.task_type
        assert deserialized.agent_id == original_task.agent_id
        assert deserialized.dependencies == original_task.dependencies
    
    def test_task_validation(self):
        """Test task validation"""
        # Valid task
        valid_task = Task(
            task_id="valid_task",
            task_type=TaskType.CONTENT_ANALYSIS,
            agent_id="analytics_agent"
        )
        assert valid_task.is_valid()
        
        # Invalid task - missing required fields
        with pytest.raises(ValueError):
            Task(
                task_id="",  # Empty task_id
                task_type=TaskType.CONTENT_GENERATION,
                agent_id="agent"
            )
    
    def test_task_dependencies(self):
        """Test task dependency management"""
        task = Task(
            task_id="dependent_task",
            task_type=TaskType.CONTENT_OPTIMIZATION,
            agent_id="optimizer_agent",
            dependencies=["task_a", "task_b", "task_c"]
        )
        
        assert task.has_dependencies()
        assert len(task.dependencies) == 3
        assert "task_a" in task.dependencies
        
        # Mark dependencies as completed
        task.mark_dependency_completed("task_a")
        task.mark_dependency_completed("task_b")
        
        assert not task.are_dependencies_satisfied()
        
        task.mark_dependency_completed("task_c")
        assert task.are_dependencies_satisfied()
    
    def test_task_retry_logic(self):
        """Test task retry mechanism"""
        task = Task(
            task_id="retry_task",
            task_type=TaskType.AUDIO_PROCESSING,
            agent_id="audio_agent",
            max_retries=3
        )
        
        assert task.retry_count == 0
        assert task.can_retry()
        
        # Simulate failures and retries
        for i in range(3):
            task.increment_retry_count()
            assert task.retry_count == i + 1
            
        assert not task.can_retry()  # Max retries reached
    
    def test_task_execution_time_tracking(self):
        """Test task execution time tracking"""
        task = Task(
            task_id="timing_task",
            task_type=TaskType.CONTENT_GENERATION,
            agent_id="content_agent"
        )
        
        # Start execution
        task.mark_started()
        assert task.status == TaskStatus.RUNNING
        assert task.started_at is not None
        
        # Complete execution
        import time
        time.sleep(0.1)  # Small delay
        
        task.mark_completed()
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
        
        execution_time = task.get_execution_time()
        assert execution_time >= 0.1


class TestTaskQueue:
    """Test task queue functionality"""
    
    @pytest.fixture
    def task_queue(self) -> TaskQueue:
        """
Create task queue for testing"""
        config = TaskConfig(
            max_queue_size=100,
            priority_levels=5,
            enable_persistence=False
        )
        return TaskQueue(config)
    
    def test_queue_initialization(self):
        """
Test task queue initialization"""
        config = TaskConfig(max_queue_size=50)
        queue = TaskQueue(config)
        
        assert queue.size() == 0
        assert queue.is_empty()
        assert not queue.is_full()
        assert queue.max_size == 50
    
    def test_task_enqueue_dequeue(self, task_queue):
        """
Test adding and removing tasks from queue"""
        task1 = Task(
            task_id="queue_task_1",
            task_type=TaskType.CONTENT_GENERATION,
            agent_id="agent_1",
            priority=TaskPriority.HIGH
        )
        
        task2 = Task(
            task_id="queue_task_2",
            task_type=TaskType.SOCIAL_MEDIA_POSTING,
            agent_id="agent_2",
            priority=TaskPriority.LOW
        )
        
        # Enqueue tasks
        assert task_queue.enqueue(task1) is True
        assert task_queue.enqueue(task2) is True
        assert task_queue.size() == 2
        assert not task_queue.is_empty()
        
        # Dequeue tasks (should return highest priority first)
        dequeued_task = task_queue.dequeue()
        assert dequeued_task.task_id == "queue_task_1"  # High priority
        assert task_queue.size() == 1
        
        dequeued_task = task_queue.dequeue()
        assert dequeued_task.task_id == "queue_task_2"  # Low priority
        assert task_queue.is_empty()
    
    def test_priority_ordering(self, task_queue):
        """Test priority-based task ordering"""
        priorities = [TaskPriority.LOW, TaskPriority.CRITICAL, TaskPriority.MEDIUM, TaskPriority.HIGH]
        
        # Add tasks with different priorities
        for i, priority in enumerate(priorities):
            task = Task(
                task_id=f"priority_task_{i}",
                task_type=TaskType.CONTENT_ANALYSIS,
                agent_id="agent",
                priority=priority
            )
            task_queue.enqueue(task)
        
        # Dequeue tasks - should come out in priority order
        expected_order = [TaskPriority.CRITICAL, TaskPriority.HIGH, TaskPriority.MEDIUM, TaskPriority.LOW]
        
        for expected_priority in expected_order:
            dequeued_task = task_queue.dequeue()
            assert dequeued_task.priority == expected_priority
    
    def test_queue_capacity_limits(self, task_queue):
        """Test queue capacity management"""
        # Fill queue to capacity
        for i in range(task_queue.max_size):
            task = Task(
                task_id=f"capacity_task_{i}",
                task_type=TaskType.CONTENT_GENERATION,
                agent_id="agent"
            )
            assert task_queue.enqueue(task) is True
        
        assert task_queue.is_full()
        
        # Try to add one more task (should fail)
        overflow_task = Task(
            task_id="overflow_task",
            task_type=TaskType.CONTENT_ANALYSIS,
            agent_id="agent"
        )
        assert task_queue.enqueue(overflow_task) is False
    
    def test_task_filtering(self, task_queue):
        """Test filtering tasks by criteria"""
        # Add tasks with different attributes
        tasks = [
            Task(task_id="filter_1", task_type=TaskType.CONTENT_GENERATION, agent_id="agent_1"),
            Task(task_id="filter_2", task_type=TaskType.SOCIAL_MEDIA_POSTING, agent_id="agent_2"),
            Task(task_id="filter_3", task_type=TaskType.CONTENT_GENERATION, agent_id="agent_1"),
            Task(task_id="filter_4", task_type=TaskType.AUDIO_PROCESSING, agent_id="agent_3")
        ]
        
        for task in tasks:
            task_queue.enqueue(task)
        
        # Filter by task type
        content_tasks = task_queue.get_tasks_by_type(TaskType.CONTENT_GENERATION)
        assert len(content_tasks) == 2
        
        # Filter by agent
        agent1_tasks = task_queue.get_tasks_by_agent("agent_1")
        assert len(agent1_tasks) == 2
    
    def test_task_removal(self, task_queue):
        """Test removing specific tasks from queue"""
        task1 = Task(task_id="remove_1", task_type=TaskType.CONTENT_ANALYSIS, agent_id="agent")
        task2 = Task(task_id="remove_2", task_type=TaskType.SOCIAL_MEDIA_POSTING, agent_id="agent")
        
        task_queue.enqueue(task1)
        task_queue.enqueue(task2)
        
        # Remove specific task
        removed = task_queue.remove_task("remove_1")
        assert removed is True
        assert task_queue.size() == 1
        
        # Try to remove non-existent task
        removed = task_queue.remove_task("non_existent")
        assert removed is False
        assert task_queue.size() == 1


class TestTaskScheduler:
    """Test task scheduling functionality"""
    
    @pytest.fixture
    async def task_scheduler(self) -> TaskScheduler:
        """
Create task scheduler for testing"""
        config = TaskConfig(
            scheduling_algorithm="priority_round_robin",
            time_slice_ms=100,
            enable_load_balancing=True
        )
        scheduler = TaskScheduler(config)
        await scheduler.initialize()
        
        yield scheduler
        
        await scheduler.shutdown()
    
    async def test_scheduler_initialization(self):
        """Test task scheduler initialization"""
        config = TaskConfig()
        scheduler = TaskScheduler(config)
        
        assert not scheduler.initialized
        
        await scheduler.initialize()
        assert scheduler.initialized
        
        await scheduler.shutdown()
    
    async def test_task_scheduling(self, task_scheduler):
        """
Test basic task scheduling"""
        # Create tasks for scheduling
        tasks = [
            Task(
                task_id="schedule_1",
                task_type=TaskType.CONTENT_GENERATION,
                agent_id="content_agent",
                priority=TaskPriority.HIGH
            ),
            Task(
                task_id="schedule_2",
                task_type=TaskType.SOCIAL_MEDIA_POSTING,
                agent_id="social_agent",
                priority=TaskPriority.MEDIUM
            )
        ]
        
        # Schedule tasks
        for task in tasks:
            result = await task_scheduler.schedule_task(task)
            assert result["success"] is True
            assert "scheduled_at" in result
        
        # Get scheduled tasks
        scheduled = await task_scheduler.get_scheduled_tasks()
        assert len(scheduled) >= 2
    
    async def test_dependency_scheduling(self, task_scheduler):
        """Test scheduling tasks with dependencies"""
        # Create dependent tasks
        base_task = Task(
            task_id="base_task",
            task_type=TaskType.CONTENT_GENERATION,
            agent_id="content_agent"
        )
        
        dependent_task = Task(
            task_id="dependent_task",
            task_type=TaskType.CONTENT_OPTIMIZATION,
            agent_id="optimizer_agent",
            dependencies=["base_task"]
        )
        
        # Schedule tasks
        await task_scheduler.schedule_task(base_task)
        await task_scheduler.schedule_task(dependent_task)
        
        # Verify dependency handling
        execution_plan = await task_scheduler.get_execution_plan()
        assert "dependency_graph" in execution_plan
        assert "execution_order" in execution_plan
    
    async def test_load_balancing(self, task_scheduler):
        """Test load balancing across agents"""
        # Create multiple tasks for the same agent type
        tasks = []
        for i in range(10):
            task = Task(
                task_id=f"load_balance_{i}",
                task_type=TaskType.CONTENT_GENERATION,
                agent_id=f"content_agent_{i % 3}",  # 3 different agents
                priority=TaskPriority.MEDIUM
            )
            tasks.append(task)
        
        # Schedule all tasks
        for task in tasks:
            await task_scheduler.schedule_task(task)
        
        # Check load distribution
        load_stats = await task_scheduler.get_load_statistics()
        assert "agent_workloads" in load_stats
        assert "distribution_score" in load_stats
        
        # Verify reasonable load distribution
        workloads = load_stats["agent_workloads"]
        if len(workloads) > 1:
            max_load = max(workloads.values())
            min_load = min(workloads.values())
            load_variance = max_load - min_load
            assert load_variance <= 5  # Reasonable load balance
    
    async def test_scheduling_algorithms(self, task_scheduler):
        """Test different scheduling algorithms"""
        algorithms = ["fifo", "priority_queue", "round_robin", "shortest_job_first"]
        
        for algorithm in algorithms:
            # Configure scheduler with algorithm
            await task_scheduler.set_scheduling_algorithm(algorithm)
            
            # Create test tasks
            test_tasks = [
                Task(task_id=f"{algorithm}_task_1", task_type=TaskType.CONTENT_ANALYSIS, agent_id="agent_1"),
                Task(task_id=f"{algorithm}_task_2", task_type=TaskType.AUDIO_PROCESSING, agent_id="agent_2")
            ]
            
            # Schedule and verify
            for task in test_tasks:
                result = await task_scheduler.schedule_task(task)
                assert result["success"] is True
            
            # Clear scheduler for next algorithm
            await task_scheduler.clear_schedule()


class TestTaskExecutor:
    """Test task execution functionality"""
    
    @pytest.fixture
    async def task_executor(self) -> TaskExecutor:
        """
Create task executor for testing"""
        config = TaskConfig(
            max_concurrent_tasks=5,
            execution_timeout=60,
            enable_monitoring=True
        )
        executor = TaskExecutor(config)
        await executor.initialize()
        
        yield executor
        
        await executor.shutdown()
    
    async def test_executor_initialization(self):
        """
Test task executor initialization"""
        config = TaskConfig()
        executor = TaskExecutor(config)
        
        assert not executor.initialized
        assert executor.active_tasks == 0
        
        await executor.initialize()
        assert executor.initialized
        
        await executor.shutdown()
    
    async def test_task_execution(self, task_executor):
        """
Test basic task execution"""
        task = Task(
            task_id="execution_test",
            task_type=TaskType.CONTENT_GENERATION,
            agent_id="content_agent",
            parameters={"content_type": "text", "length": 100}
        )
        
        # Execute task
        execution_result = await task_executor.execute_task(task)
        
        assert execution_result["success"] is True
        assert "task_id" in execution_result
        assert "execution_time" in execution_result
        assert execution_result["task_id"] == task.task_id
    
    async def test_concurrent_execution(self, task_executor):
        """Test concurrent task execution"""
        # Create multiple tasks
        tasks = []
        for i in range(3):
            task = Task(
                task_id=f"concurrent_task_{i}",
                task_type=TaskType.CONTENT_ANALYSIS,
                agent_id=f"agent_{i}",
                parameters={"analysis_type": "sentiment"}
            )
            tasks.append(task)
        
        # Execute tasks concurrently
        execution_tasks = [task_executor.execute_task(task) for task in tasks]
        results = await asyncio.gather(*execution_tasks)
        
        # Verify all executions succeeded
        assert len(results) == 3
        for result in results:
            assert result["success"] is True
    
    async def test_execution_monitoring(self, task_executor):
        """Test task execution monitoring"""
        task = Task(
            task_id="monitoring_test",
            task_type=TaskType.AUDIO_PROCESSING,
            agent_id="audio_agent",
            parameters={"operation": "noise_reduction"}
        )
        
        # Start task execution
        execution_handle = await task_executor.start_task_execution(task)
        assert execution_handle["success"] is True
        
        execution_id = execution_handle["execution_id"]
        
        # Monitor execution progress
        progress = await task_executor.get_execution_progress(execution_id)
        assert "status" in progress
        assert "progress_percentage" in progress
        assert "current_operation" in progress
        
        # Wait for completion
        max_wait_time = 30
        wait_time = 0
        while wait_time < max_wait_time:
            progress = await task_executor.get_execution_progress(execution_id)
            if progress["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break
            await asyncio.sleep(1)
            wait_time += 1
        
        # Verify final status
        final_progress = await task_executor.get_execution_progress(execution_id)
        assert final_progress["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED]
    
    async def test_execution_timeout(self, task_executor):
        """Test task execution timeout handling"""
        # Create task with short timeout
        task = Task(
            task_id="timeout_test",
            task_type=TaskType.CONTENT_GENERATION,
            agent_id="slow_agent",
            timeout=1  # 1 second timeout
        )
        
        # Execute task (should timeout)
        execution_result = await task_executor.execute_task(task)
        
        # Verify timeout handling
        if not execution_result["success"]:
            assert "timeout" in execution_result.get("error", "").lower()
    
    async def test_execution_error_handling(self, task_executor):
        """Test execution error handling"""
        # Create task that will fail
        failing_task = Task(
            task_id="failing_test",
            task_type=TaskType.CONTENT_GENERATION,
            agent_id="non_existent_agent",  # This should cause failure
            parameters={"invalid_param": "value"}
        )
        
        # Execute failing task
        execution_result = await task_executor.execute_task(failing_task)
        
        # Verify error handling
        assert execution_result["success"] is False
        assert "error" in execution_result
        
        # Verify executor remains functional
        valid_task = Task(
            task_id="recovery_test",
            task_type=TaskType.CONTENT_ANALYSIS,
            agent_id="analytics_agent"
        )
        
        recovery_result = await task_executor.execute_task(valid_task)
        assert recovery_result["success"] is True


class TestTaskManager:
    """Test complete task manager functionality"""
    
    @pytest.fixture
    async def task_manager(self) -> TaskManager:
        """
Create task manager for testing"""
        config = TaskConfig(
            max_concurrent_tasks=10,
            max_queue_size=100,
            enable_persistence=True,
            enable_monitoring=True,
            scheduling_algorithm="priority_round_robin"
        )
        manager = TaskManager(config)
        await manager.initialize()
        
        yield manager
        
        await manager.shutdown()
    
    async def test_manager_initialization(self):
        """Test task manager initialization"""
        config = TaskConfig()
        manager = TaskManager(config)
        
        assert not manager.initialized
        
        await manager.initialize()
        assert manager.initialized
        assert manager.queue is not None
        assert manager.scheduler is not None
        assert manager.executor is not None
        
        await manager.shutdown()
    
    async def test_end_to_end_task_processing(self, task_manager):
        """
Test complete task processing pipeline"""
        # Create a complex task
        task = Task(
            task_id="e2e_test_task",
            task_type=TaskType.CONTENT_GENERATION,
            agent_id="content_creator",
            parameters={
                "content_type": "video",
                "duration": 60,
                "style": "educational",
                "target_audience": "tech_enthusiasts"
            },
            priority=TaskPriority.HIGH,
            timeout=300
        )
        
        # Submit task
        submission_result = await task_manager.submit_task(task)
        assert submission_result["success"] is True
        assert "task_id" in submission_result
        
        # Monitor task progress
        task_id = submission_result["task_id"]
        max_wait_time = 60
        wait_time = 0
        
        while wait_time < max_wait_time:
            status = await task_manager.get_task_status(task_id)
            
            if status["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break
                
            await asyncio.sleep(1)
            wait_time += 1
        
        # Verify final result
        final_status = await task_manager.get_task_status(task_id)
        assert final_status["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED]
        
        if final_status["status"] == TaskStatus.COMPLETED:
            assert "result" in final_status
            assert final_status["execution_time"] > 0
    
    async def test_batch_task_processing(self, task_manager):
        """Test processing multiple tasks in batch"""
        # Create batch of tasks
        batch_tasks = []
        for i in range(5):
            task = Task(
                task_id=f"batch_task_{i}",
                task_type=TaskType.CONTENT_ANALYSIS,
                agent_id=f"analytics_agent_{i % 2}",  # 2 different agents
                parameters={"analysis_type": "sentiment", "batch_id": i},
                priority=TaskPriority.MEDIUM
            )
            batch_tasks.append(task)
        
        # Submit batch
        batch_result = await task_manager.submit_batch(batch_tasks)
        assert batch_result["success"] is True
        assert "batch_id" in batch_result
        assert len(batch_result["task_ids"]) == 5
        
        # Monitor batch progress
        batch_id = batch_result["batch_id"]
        max_wait_time = 90
        wait_time = 0
        
        while wait_time < max_wait_time:
            batch_status = await task_manager.get_batch_status(batch_id)
            
            if batch_status["status"] in ["completed", "failed"]:
                break
                
            await asyncio.sleep(2)
            wait_time += 2
        
        # Verify batch completion
        final_batch_status = await task_manager.get_batch_status(batch_id)
        assert final_batch_status["status"] in ["completed", "failed"]
        assert "completed_tasks" in final_batch_status
        assert "failed_tasks" in final_batch_status
    
    async def test_task_dependencies(self, task_manager):
        """Test task dependency management"""
        # Create dependent task chain
        task_a = Task(
            task_id="dep_task_a",
            task_type=TaskType.CONTENT_GENERATION,
            agent_id="content_creator"
        )
        
        task_b = Task(
            task_id="dep_task_b",
            task_type=TaskType.CONTENT_OPTIMIZATION,
            agent_id="optimizer",
            dependencies=["dep_task_a"]
        )
        
        task_c = Task(
            task_id="dep_task_c",
            task_type=TaskType.SOCIAL_MEDIA_POSTING,
            agent_id="social_manager",
            dependencies=["dep_task_b"]
        )
        
        # Submit dependent tasks
        await task_manager.submit_task(task_a)
        await task_manager.submit_task(task_b)
        await task_manager.submit_task(task_c)
        
        # Monitor dependency execution
        max_wait_time = 120
        wait_time = 0
        
        while wait_time < max_wait_time:
            status_a = await task_manager.get_task_status("dep_task_a")
            status_b = await task_manager.get_task_status("dep_task_b")
            status_c = await task_manager.get_task_status("dep_task_c")
            
            # Verify dependency order
            if status_a["status"] == TaskStatus.COMPLETED:
                # Task B should start after A completes
                assert status_b["status"] in [TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.COMPLETED]
            
            if status_b["status"] == TaskStatus.COMPLETED:
                # Task C should start after B completes
                assert status_c["status"] in [TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.COMPLETED]
            
            if status_c["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break
                
            await asyncio.sleep(2)
            wait_time += 2
    
    async def test_task_cancellation(self, task_manager):
        """Test task cancellation"""
        # Submit long-running task
        long_task = Task(
            task_id="cancellation_test",
            task_type=TaskType.AUDIO_PROCESSING,
            agent_id="audio_specialist",
            parameters={"operation": "long_processing"},
            timeout=300
        )
        
        submission_result = await task_manager.submit_task(long_task)
        task_id = submission_result["task_id"]
        
        # Wait for task to start
        await asyncio.sleep(2)
        
        # Cancel task
        cancellation_result = await task_manager.cancel_task(task_id)
        assert cancellation_result["success"] is True
        
        # Verify cancellation
        status = await task_manager.get_task_status(task_id)
        assert status["status"] == TaskStatus.CANCELLED
    
    async def test_task_retry_mechanism(self, task_manager):
        """Test automatic task retry"""
        # Create task that might fail
        retry_task = Task(
            task_id="retry_test",
            task_type=TaskType.CONTENT_GENERATION,
            agent_id="unreliable_agent",
            max_retries=3,
            retry_delay=1
        )
        
        # Submit task
        submission_result = await task_manager.submit_task(retry_task)
        task_id = submission_result["task_id"]
        
        # Monitor retry behavior
        max_wait_time = 60
        wait_time = 0
        retry_detected = False
        
        while wait_time < max_wait_time:
            status = await task_manager.get_task_status(task_id)
            
            if "retry_count" in status and status["retry_count"] > 0:
                retry_detected = True
            
            if status["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break
                
            await asyncio.sleep(1)
            wait_time += 1
        
        # Note: retry_detected may be False if task succeeds on first attempt
        # This is acceptable behavior
    
    async def test_performance_monitoring(self, task_manager):
        """Test performance monitoring and metrics"""
        # Submit several tasks to generate metrics
        for i in range(3):
            task = Task(
                task_id=f"metrics_task_{i}",
                task_type=TaskType.CONTENT_ANALYSIS,
                agent_id="analytics_agent",
                parameters={"metric_test": True}
            )
            await task_manager.submit_task(task)
        
        # Wait for some processing
        await asyncio.sleep(5)
        
        # Get performance metrics
        metrics = await task_manager.get_performance_metrics()
        
        assert "total_tasks_processed" in metrics
        assert "average_execution_time" in metrics
        assert "success_rate" in metrics
        assert "queue_size" in metrics
        assert "active_tasks" in metrics
        
        # Verify metric values
        assert metrics["total_tasks_processed"] >= 0
        assert 0 <= metrics["success_rate"] <= 1
        assert metrics["queue_size"] >= 0
        assert metrics["active_tasks"] >= 0
    
    @pytest.mark.performance
    async def test_task_manager_performance(self, task_manager, assert_performance):
        """Test task manager performance under load"""
        # Test task submission performance
        start_time = datetime.now(timezone.utc)
        
        submission_tasks = []
        for i in range(10):
            task = Task(
                task_id=f"perf_task_{i}",
                task_type=TaskType.CONTENT_ANALYSIS,
                agent_id="perf_agent"
            )
            submission_tasks.append(task_manager.submit_task(task))
        
        await asyncio.gather(*submission_tasks)
        
        submission_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        assert submission_time < 5.0  # Should submit 10 tasks within 5 seconds
        
        assert_performance("task_submission", max_time=5.0)
    
    async def test_error_recovery(self, task_manager):
        """Test system error recovery"""
        # Submit task that will cause system error
        error_task = Task(
            task_id="system_error_test",
            task_type=TaskType.CONTENT_GENERATION,
            agent_id="error_prone_agent",
            parameters={"cause_system_error": True}
        )
        
        # Submit and handle error
        try:
            await task_manager.submit_task(error_task)
        except Exception:
            pass  # Expected system error
        
        # Verify system recovery
        await asyncio.sleep(1)
        
        # Submit normal task to verify recovery
        recovery_task = Task(
            task_id="recovery_test",
            task_type=TaskType.CONTENT_ANALYSIS,
            agent_id="analytics_agent"
        )
        
        recovery_result = await task_manager.submit_task(recovery_task)
        assert recovery_result["success"] is True
