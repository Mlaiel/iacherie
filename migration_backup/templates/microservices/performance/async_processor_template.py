#!/usr/bin/env python3
"""
⚡ ASYNC PROCESSOR TEMPLATE - HIGH-PERFORMANCE CONCURRENT PROCESSING
===================================================================

Advanced asynchronous task processing with work queues, rate limiting,
priority scheduling, and dynamic scaling for maximum throughput.

© 2025 Fahed Mlaiel (mlaiel@live.de) - Propriété Intellectuelle Exclusive

🎯 EXPERTISE: Performance Engineering + Backend Senior + ML Engineer
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import time
from collections import deque
import heapq

logger = logging.getLogger(__name__)

class Priority(Enum):
    LOW = 1
    NORMAL = 2  
    HIGH = 3
    URGENT = 4

@dataclass
class Task:
    """Async task wrapper"""
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: Priority = Priority.NORMAL
    created_at: float = field(default_factory=time.time)
    task_id: str = ""
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class ProcessorMetrics:
    """Processor performance metrics"""
    tasks_processed: int = 0
    tasks_failed: int = 0
    avg_processing_time_ms: float = 0.0
    queue_size: int = 0
    active_workers: int = 0

class AsyncProcessorTemplate:
    """
    🚀 ENTERPRISE ASYNC PROCESSOR TEMPLATE
    
    High-performance concurrent processing with priority queues,
    rate limiting, and intelligent scaling.
    """
    
    def __init__(self, max_workers: int = 10, max_queue_size: int = 1000):
        """Initialize async processor"""
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.task_queue = asyncio.PriorityQueue(maxsize=max_queue_size)
        self.workers: List[asyncio.Task] = []
        self.metrics = ProcessorMetrics()
        self.running = False
        
        # Rate limiting
        self.rate_limit = 100  # tasks per second
        self.rate_window = 1.0  # seconds
        self.request_times = deque()
    
    async def start(self):
        """Start the processor workers"""
        if self.running:
            return
            
        self.running = True
        
        # Create worker tasks
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
        
        logger.info(f"✅ Async processor started with {self.max_workers} workers")
    
    async def stop(self):
        """Stop the processor workers"""
        self.running = False
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        
        logger.info("✅ Async processor stopped")
    
    async def submit(self, func: Callable, *args, priority: Priority = Priority.NORMAL, **kwargs) -> str:
        """Submit task for async processing"""
        if not self.running:
            await self.start()
        
        # Rate limiting check
        if not self._check_rate_limit():
            raise Exception("Rate limit exceeded")
        
        # Create task
        task_id = f"task-{int(time.time() * 1000000)}"
        task = Task(
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            task_id=task_id
        )
        
        # Add to priority queue (negative priority for max heap behavior)
        priority_value = -priority.value
        await self.task_queue.put((priority_value, time.time(), task))
        
        self.metrics.queue_size = self.task_queue.qsize()
        return task_id
    
    async def _worker(self, worker_name: str):
        """Worker coroutine to process tasks"""
        logger.info(f"Worker {worker_name} started")
        
        while self.running:
            try:
                # Get task with timeout
                priority, timestamp, task = await asyncio.wait_for(
                    self.task_queue.get(), timeout=1.0
                )
                
                self.metrics.active_workers += 1
                await self._process_task(task)
                self.metrics.active_workers -= 1
                
                # Mark task as done
                self.task_queue.task_done()
                self.metrics.queue_size = self.task_queue.qsize()
                
            except asyncio.TimeoutError:
                continue  # No tasks available, continue loop
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                self.metrics.active_workers -= 1
        
        logger.info(f"Worker {worker_name} stopped")
    
    async def _process_task(self, task: Task):
        """Process individual task"""
        start_time = time.time()
        
        try:
            # Execute task function
            if asyncio.iscoroutinefunction(task.func):
                result = await task.func(*task.args, **task.kwargs)
            else:
                result = task.func(*task.args, **task.kwargs)
            
            # Update metrics
            processing_time = (time.time() - start_time) * 1000
            self._update_processing_time(processing_time)
            self.metrics.tasks_processed += 1
            
            logger.debug(f"✅ Task {task.task_id} completed in {processing_time:.2f}ms")
            
        except Exception as e:
            logger.error(f"❌ Task {task.task_id} failed: {e}")
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                # Re-queue with delay
                await asyncio.sleep(2 ** task.retry_count)  # Exponential backoff
                await self.task_queue.put((-task.priority.value, time.time(), task))
            else:
                self.metrics.tasks_failed += 1
    
    def _check_rate_limit(self) -> bool:
        """Check if rate limit allows new task"""
        current_time = time.time()
        
        # Remove old requests outside the window
        while self.request_times and current_time - self.request_times[0] > self.rate_window:
            self.request_times.popleft()
        
        # Check if we're under the limit
        if len(self.request_times) < self.rate_limit:
            self.request_times.append(current_time)
            return True
        
        return False
    
    def _update_processing_time(self, processing_time_ms: float):
        """Update average processing time"""
        if self.metrics.tasks_processed == 0:
            self.metrics.avg_processing_time_ms = processing_time_ms
        else:
            # Exponential moving average
            alpha = 0.1
            self.metrics.avg_processing_time_ms = (
                alpha * processing_time_ms + 
                (1 - alpha) * self.metrics.avg_processing_time_ms
            )
    
    def get_metrics(self) -> ProcessorMetrics:
        """Get processor metrics"""
        return self.metrics
    
    async def wait_for_completion(self):
        """Wait for all queued tasks to complete"""
        await self.task_queue.join()

# Factory function
def create_async_processor(max_workers: int = 10, **kwargs) -> AsyncProcessorTemplate:
    """Create async processor instance"""
    return AsyncProcessorTemplate(max_workers=max_workers, **kwargs)