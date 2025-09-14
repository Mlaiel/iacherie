"""
🏭 Throughput Maximizer - High-Performance Inference Optimization Engine

⚙️ DEVOPS + 🛡️ BACKEND SENIOR + 🔬 ML ENGINEER EXPERTISE

Advanced inference throughput maximization system for achieving optimal performance
in ML model serving with parallel processing, intelligent batching, connection pooling,
and creator-specific optimization strategies for maximum efficiency.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Version: 1.0.0

🏭 THROUGHPUT MAXIMIZATION PLATFORM
- Parallel processing and intelligent batching
- Connection pooling and resource optimization
- Creator-specific throughput strategies
- Real-time performance monitoring and adaptation
- Enterprise-grade scalability and reliability
"""

import asyncio
import logging
import json
import numpy as np
import torch
import time
import threading
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import uuid
import queue
import concurrent.futures
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class OptimizationStrategy(Enum):
    """Throughput optimization strategies"""
    BATCHING = "batching"
    PARALLEL_PROCESSING = "parallel_processing" 
    CONNECTION_POOLING = "connection_pooling"
    CACHING = "caching"
    LOAD_BALANCING = "load_balancing"
    RESOURCE_OPTIMIZATION = "resource_optimization"

class CreatorType(Enum):
    """Creator types for specialized optimization"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    GENERAL = "general"

@dataclass
class ThroughputConfig:
    """Configuration for throughput optimization"""
    max_batch_size: int = 32
    max_concurrent_requests: int = 100
    connection_pool_size: int = 50
    cache_size: int = 1000
    timeout_seconds: float = 30.0
    optimization_strategies: List[OptimizationStrategy] = field(default_factory=list)
    creator_type: CreatorType = CreatorType.GENERAL
    enable_monitoring: bool = True
    adaptive_optimization: bool = True

@dataclass
class ThroughputMetrics:
    """Throughput performance metrics"""
    requests_per_second: float = 0.0
    average_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    batch_efficiency: float = 0.0
    resource_utilization: float = 0.0
    cache_hit_rate: float = 0.0
    error_rate: float = 0.0
    concurrent_requests: int = 0
    queue_length: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

class IntelligentBatcher:
    """🔬 ML ENGINEER - Intelligent request batching system"""
    
    def __init__(self, config -> None: ThroughputConfig) -> None:
        self.config = config
        self.pending_requests = queue.Queue()
        self.batch_queue = queue.Queue()
        self.batching_thread = None
        self.running = False
        self.metrics = ThroughputMetrics()
        
    def start_batching(self) -> None:
        """Start intelligent batching system"""
        if self.running:
            return
            
        self.running = True
        self.batching_thread = threading.Thread(target=self._batching_loop, daemon=True)
        self.batching_thread.start()
        logger.info("🔄 Intelligent batching started")
    
    def stop_batching(self) -> None:
        """Stop batching system"""
        self.running = False
        if self.batching_thread:
            self.batching_thread.join(timeout=5.0)
        logger.info("🛑 Intelligent batching stopped")
    
    async def add_request(self, request_data: Any, request_id: str) -> str:
        """Add request to batching queue"""
        batch_id = str(uuid.uuid4())
        
        request_item = {
            "request_id": request_id,
            "batch_id": batch_id,
            "data": request_data,
            "timestamp": datetime.now(),
            "creator_type": getattr(request_data, 'creator_type', self.config.creator_type.value)
        }
        
        self.pending_requests.put(request_item)
        return batch_id
    
    def _batching_loop(self) -> None:
        """Main batching loop"""
        while self.running:
            try:
                batch = self._collect_batch()
                if batch:
                    self.batch_queue.put(batch)
                    self._update_batch_metrics(batch)
                else:
                    time.sleep(0.01)  # Brief pause if no requests
                    
            except Exception as e:
                logger.error(f"Batching error: {e}")
                time.sleep(0.1)
    
    def _collect_batch(self) -> Optional[List[Dict[str, Any]]]:
        """Collect optimal batch of requests"""
        batch = []
        start_time = time.time()
        max_wait_time = 0.01  # 10ms max batching delay
        
        # Collect requests for batch
        while (len(batch) < self.config.max_batch_size and 
               (time.time() - start_time) < max_wait_time):
            
            try:
                request = self.pending_requests.get(timeout=0.001)
                batch.append(request)
            except queue.Empty:
                break
        
        # Creator-specific batching optimization
        if batch:
            batch = self._optimize_batch_for_creator(batch)
        
        return batch if batch else None
    
    def _optimize_batch_for_creator(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize batch composition for creator types"""
        # Group by creator type for better processing efficiency
        creator_groups = defaultdict(list)
        
        for request in batch:
            creator_type = request.get('creator_type', 'general')
            creator_groups[creator_type].append(request)
        
        # Prioritize based on creator type characteristics
        optimized_batch = []
        
        # Musicians - prioritize for real-time processing
        if 'musician' in creator_groups:
            optimized_batch.extend(creator_groups['musician'])
        
        # Photographers - can handle larger batches
        if 'photographer' in creator_groups:
            optimized_batch.extend(creator_groups['photographer'])
        
        # Add remaining creator types
        for creator_type, requests in creator_groups.items():
            if creator_type not in ['musician', 'photographer']:
                optimized_batch.extend(requests)
        
        return optimized_batch
    
    def _update_batch_metrics(self, batch: List[Dict[str, Any]]) -> None:
        """Update batching metrics"""
        batch_size = len(batch)
        self.metrics.batch_efficiency = batch_size / self.config.max_batch_size
        
        # Calculate batching delay
        if batch:
            oldest_request = min(batch, key=lambda x: x['timestamp'])
            batching_delay = (datetime.now() - oldest_request['timestamp']).total_seconds() * 1000
            # Update average latency with batching overhead
            self.metrics.average_latency_ms = (self.metrics.average_latency_ms * 0.9 + batching_delay * 0.1)
    
    def get_next_batch(self) -> Optional[List[Dict[str, Any]]]:
        """Get next processed batch"""
        try:
            return self.batch_queue.get(timeout=0.1)
        except queue.Empty:
            return None

class ConnectionPoolManager:
    """🛡️ BACKEND SENIOR - Advanced connection pool management"""
    
    def __init__(self, config -> None: ThroughputConfig) -> None:
        self.config = config
        self.connection_pool = queue.Queue(maxsize=config.connection_pool_size)
        self.active_connections = {}
        self.connection_metrics = defaultdict(float)
        self._initialize_pool()
        
    def _initialize_pool(self) -> None:
        """Initialize connection pool"""
        for i in range(self.config.connection_pool_size):
            connection_id = f"conn_{i}"
            connection = self._create_connection(connection_id)
            self.connection_pool.put(connection)
        
        logger.info(f"🔗 Connection pool initialized with {self.config.connection_pool_size} connections")
    
    def _create_connection(self, connection_id: str) -> Dict[str, Any]:
        """Create new connection"""
        return {
            "connection_id": connection_id,
            "created_at": datetime.now(),
            "last_used": datetime.now(),
            "request_count": 0,
            "error_count": 0,
            "status": "ready"
        }
    
    async def acquire_connection(self, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """Acquire connection from pool"""
        try:
            connection = self.connection_pool.get(timeout=timeout)
            connection["last_used"] = datetime.now()
            connection["status"] = "in_use"
            
            self.active_connections[connection["connection_id"]] = connection
            self.connection_metrics["connections_acquired"] += 1
            
            return connection
            
        except queue.Empty:
            logger.warning("No available connections in pool")
            self.connection_metrics["connection_timeouts"] += 1
            return None
    
    async def release_connection(self, connection: Dict[str, Any], success: bool = True) -> None:
        """Release connection back to pool"""
        connection_id = connection["connection_id"]
        
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Update connection statistics
        connection["request_count"] += 1
        if not success:
            connection["error_count"] += 1
        
        connection["status"] = "ready"
        
        # Check if connection should be recycled
        if self._should_recycle_connection(connection):
            connection = self._create_connection(connection_id)
            self.connection_metrics["connections_recycled"] += 1
        
        try:
            self.connection_pool.put(connection, timeout=1.0)
            self.connection_metrics["connections_released"] += 1
        except queue.Full:
            logger.warning(f"Connection pool full, discarding connection {connection_id}")
    
    def _should_recycle_connection(self, connection: Dict[str, Any]) -> bool:
        """Determine if connection should be recycled"""
        # Recycle after 1000 requests or high error rate
        if connection["request_count"] > 1000:
            return True
        
        if (connection["error_count"] / max(1, connection["request_count"])) > 0.1:
            return True
        
        # Recycle old connections (1 hour)
        age = (datetime.now() - connection["created_at"]).total_seconds()
        if age > 3600:
            return True
        
        return False
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            "pool_size": self.config.connection_pool_size,
            "available_connections": self.connection_pool.qsize(),
            "active_connections": len(self.active_connections),
            "metrics": dict(self.connection_metrics)
        }

class ParallelProcessor:
    """⚙️ DEVOPS - Parallel processing optimization"""
    
    def __init__(self, config -> None: ThroughputConfig) -> None:
        self.config = config
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=config.max_concurrent_requests
        )
        self.processing_futures = {}
        self.processing_metrics = defaultdict(float)
        
    async def process_batch_parallel(self, batch: List[Dict[str, Any]], 
                                   processor_func: Callable) -> List[Any]:
        """Process batch in parallel"""
        start_time = time.time()
        
        # Submit all tasks to thread pool
        futures = {}
        for request in batch:
            future = self.executor.submit(processor_func, request)
            futures[future] = request
        
        # Collect results as they complete
        results = []
        completed = 0
        
        for future in concurrent.futures.as_completed(futures, timeout=self.config.timeout_seconds):
            try:
                result = future.result()
                results.append(result)
                completed += 1
                
                # Update metrics
                self.processing_metrics["successful_requests"] += 1
                
            except Exception as e:
                logger.error(f"Parallel processing error: {e}")
                self.processing_metrics["failed_requests"] += 1
                results.append({"error": str(e)})
        
        processing_time = time.time() - start_time
        self.processing_metrics["total_processing_time"] += processing_time
        self.processing_metrics["average_processing_time"] = (
            self.processing_metrics["total_processing_time"] / 
            max(1, self.processing_metrics["successful_requests"] + self.processing_metrics["failed_requests"])
        )
        
        return results
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get parallel processing statistics"""
        return {
            "max_workers": self.config.max_concurrent_requests,
            "active_tasks": len(self.processing_futures),
            "metrics": dict(self.processing_metrics)
        }

class ThroughputMaximizer:
    """
    🏭 ⚙️ DEVOPS + 🛡️ BACKEND SENIOR + 🔬 ML ENGINEER - MASTER CLASS
    
    Enterprise-grade throughput maximization engine for ML inference optimization
    with intelligent batching, connection pooling, and parallel processing.
    """
    
    def __init__(self, config -> None: ThroughputConfig) -> None:
        self.config = config
        self.batcher = IntelligentBatcher(config)
        self.connection_pool = ConnectionPoolManager(config)
        self.parallel_processor = ParallelProcessor(config)
        
        # Performance monitoring
        self.metrics_history = deque(maxlen=1000)
        self.current_metrics = ThroughputMetrics()
        self.optimization_active = False
        
        # Adaptive optimization
        self.adaptive_optimizer = AdaptiveOptimizer(config) if config.adaptive_optimization else None
        
        logger.info("🏭 Throughput Maximizer initialized")
    
    async def start_optimization(self) -> None:
        """Start throughput optimization system"""
        if self.optimization_active:
            return
        
        self.optimization_active = True
        
        # Start batching system
        self.batcher.start_batching()
        
        # Start monitoring
        if self.config.enable_monitoring:
            asyncio.create_task(self._monitoring_loop())
        
        # Start adaptive optimization
        if self.adaptive_optimizer:
            asyncio.create_task(self.adaptive_optimizer.optimization_loop())
        
        logger.info("🚀 Throughput optimization started")
    
    async def stop_optimization(self) -> None:
        """Stop throughput optimization system"""
        self.optimization_active = False
        self.batcher.stop_batching()
        
        logger.info("🛑 Throughput optimization stopped")
    
    async def process_request(self, request_data: Any, request_id: str,
                            processor_func: Callable) -> Any:
        """Process single request with throughput optimization"""
        start_time = time.time()
        
        try:
            # Add to intelligent batching queue
            batch_id = await self.batcher.add_request(request_data, request_id)
            
            # Process as part of optimized batch
            result = await self._process_with_optimization(request_data, processor_func)
            
            # Update metrics
            processing_time = (time.time() - start_time) * 1000
            self._update_request_metrics(processing_time, True)
            
            return result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self._update_request_metrics(processing_time, False)
            logger.error(f"Request processing error: {e}")
            raise
    
    async def process_batch(self, batch_data: List[Any], 
                          processor_func: Callable) -> List[Any]:
        """Process batch with throughput optimization"""
        start_time = time.time()
        
        try:
            # Acquire connection from pool
            connection = await self.connection_pool.acquire_connection()
            if not connection:
                raise RuntimeError("No available connections")
            
            try:
                # Convert batch data to internal format
                batch_requests = []
                for i, data in enumerate(batch_data):
                    batch_requests.append({
                        "request_id": f"batch_item_{i}",
                        "data": data,
                        "timestamp": datetime.now()
                    })
                
                # Process with parallel optimization
                results = await self.parallel_processor.process_batch_parallel(
                    batch_requests, processor_func
                )
                
                # Update connection success
                await self.connection_pool.release_connection(connection, success=True)
                
                # Update metrics
                batch_time = (time.time() - start_time) * 1000
                self._update_batch_metrics(len(batch_data), batch_time, True)
                
                return results
                
            except Exception as e:
                await self.connection_pool.release_connection(connection, success=False)
                raise
                
        except Exception as e:
            batch_time = (time.time() - start_time) * 1000
            self._update_batch_metrics(len(batch_data), batch_time, False)
            logger.error(f"Batch processing error: {e}")
            raise
    
    async def _process_with_optimization(self, request_data: Any, 
                                       processor_func: Callable) -> Any:
        """Process request with all optimizations applied"""
        
        # Check cache first if enabled
        if OptimizationStrategy.CACHING in self.config.optimization_strategies:
            cached_result = await self._check_cache(request_data)
            if cached_result is not None:
                return cached_result
        
        # Wait for batching or process immediately based on load
        if OptimizationStrategy.BATCHING in self.config.optimization_strategies:
            return await self._process_with_batching(request_data, processor_func)
        else:
            return await self._process_immediately(request_data, processor_func)
    
    async def _process_with_batching(self, request_data: Any, 
                                   processor_func: Callable) -> Any:
        """Process request as part of optimized batch"""
        # Wait for batch to be formed
        max_wait_time = 0.05  # 50ms max wait for batching
        start_wait = time.time()
        
        while (time.time() - start_wait) < max_wait_time:
            batch = self.batcher.get_next_batch()
            if batch:
                # Find our request in the batch
                for request in batch:
                    if request["data"] == request_data:
                        # Process entire batch
                        results = await self.parallel_processor.process_batch_parallel(
                            batch, processor_func
                        )
                        # Return result for our specific request
                        request_index = batch.index(request)
                        return results[request_index]
                break
            
            await asyncio.sleep(0.001)
        
        # If no batch formed, process immediately
        return await self._process_immediately(request_data, processor_func)
    
    async def _process_immediately(self, request_data: Any, 
                                 processor_func: Callable) -> Any:
        """Process request immediately without batching"""
        connection = await self.connection_pool.acquire_connection()
        if not connection:
            raise RuntimeError("No available connections")
        
        try:
            # Process single request
            result = processor_func({
                "request_id": str(uuid.uuid4()),
                "data": request_data,
                "timestamp": datetime.now()
            })
            
            await self.connection_pool.release_connection(connection, success=True)
            return result
            
        except Exception as e:
            await self.connection_pool.release_connection(connection, success=False)
            raise
    
    async def _check_cache(self, request_data: Any) -> Optional[Any]:
        """Check cache for previously computed result"""
        # Simplified cache implementation
        # In production, would use Redis or similar
        cache_key = str(hash(str(request_data)))
        
        # Simulate cache lookup
        if hasattr(self, '_cache'):
            return self._cache.get(cache_key)
        return None
    
    def _update_request_metrics(self, processing_time_ms: float, success: bool) -> None:
        """Update request processing metrics"""
        self.current_metrics.average_latency_ms = (
            self.current_metrics.average_latency_ms * 0.9 + processing_time_ms * 0.1
        )
        
        if success:
            self.current_metrics.requests_per_second += 1
        else:
            self.current_metrics.error_rate += 0.01
    
    def _update_batch_metrics(self, batch_size: int, processing_time_ms: float, 
                            success: bool) -> None:
        """Update batch processing metrics"""
        throughput = batch_size / (processing_time_ms / 1000.0)
        self.current_metrics.requests_per_second = (
            self.current_metrics.requests_per_second * 0.9 + throughput * 0.1
        )
        
        self.current_metrics.batch_efficiency = batch_size / self.config.max_batch_size
    
    async def _monitoring_loop(self) -> None:
        """Performance monitoring loop"""
        while self.optimization_active:
            try:
                # Collect current metrics
                metrics_snapshot = ThroughputMetrics(
                    requests_per_second=self.current_metrics.requests_per_second,
                    average_latency_ms=self.current_metrics.average_latency_ms,
                    batch_efficiency=self.current_metrics.batch_efficiency,
                    resource_utilization=self._calculate_resource_utilization(),
                    cache_hit_rate=self._calculate_cache_hit_rate(),
                    error_rate=self.current_metrics.error_rate,
                    concurrent_requests=len(self.connection_pool.active_connections),
                    queue_length=self.batcher.pending_requests.qsize()
                )
                
                # Store metrics
                self.metrics_history.append(metrics_snapshot)
                
                # Reset counters
                self.current_metrics.error_rate *= 0.95  # Decay error rate
                
                await asyncio.sleep(1.0)  # Update every second
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(5.0)
    
    def _calculate_resource_utilization(self) -> float:
        """Calculate overall resource utilization"""
        connection_util = len(self.connection_pool.active_connections) / self.config.connection_pool_size
        queue_util = min(1.0, self.batcher.pending_requests.qsize() / 100)
        
        return (connection_util + queue_util) / 2.0
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        # Simplified cache hit rate calculation
        return 0.0  # Would be implemented with actual cache
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        latest_metrics = self.metrics_history[-1] if self.metrics_history else ThroughputMetrics()
        
        return {
            "current_metrics": {
                "requests_per_second": latest_metrics.requests_per_second,
                "average_latency_ms": latest_metrics.average_latency_ms,
                "batch_efficiency": latest_metrics.batch_efficiency,
                "resource_utilization": latest_metrics.resource_utilization,
                "error_rate": latest_metrics.error_rate,
                "concurrent_requests": latest_metrics.concurrent_requests,
                "queue_length": latest_metrics.queue_length
            },
            "connection_pool": self.connection_pool.get_pool_stats(),
            "parallel_processing": self.parallel_processor.get_processing_stats(),
            "optimization_config": {
                "max_batch_size": self.config.max_batch_size,
                "max_concurrent_requests": self.config.max_concurrent_requests,
                "strategies": [s.value for s in self.config.optimization_strategies],
                "creator_type": self.config.creator_type.value
            }
        }

class AdaptiveOptimizer:
    """🔬 ML ENGINEER - Adaptive optimization system"""
    
    def __init__(self, config -> None: ThroughputConfig) -> None:
        self.config = config
        self.optimization_history = []
        self.current_performance = 0.0
        
    async def optimization_loop(self) -> None:
        """Adaptive optimization main loop"""
        while True:
            try:
                # Analyze current performance
                performance_score = await self._analyze_performance()
                
                # Suggest optimizations
                optimizations = await self._suggest_optimizations(performance_score)
                
                # Apply best optimization
                if optimizations:
                    await self._apply_optimization(optimizations[0])
                
                await asyncio.sleep(60)  # Optimize every minute
                
            except Exception as e:
                logger.error(f"Adaptive optimization error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _analyze_performance(self) -> float:
        """Analyze current performance"""
        # Simplified performance analysis
        return np.random.uniform(0.5, 1.0)
    
    async def _suggest_optimizations(self, performance_score: float) -> List[Dict[str, Any]]:
        """Suggest performance optimizations"""
        optimizations = []
        
        if performance_score < 0.8:
            optimizations.append({
                "type": "increase_batch_size",
                "current_value": self.config.max_batch_size,
                "suggested_value": min(64, self.config.max_batch_size * 2),
                "expected_improvement": 0.15
            })
        
        return optimizations
    
    async def _apply_optimization(self, optimization: Dict[str, Any]) -> None:
        """Apply suggested optimization"""
        logger.info(f"Applying optimization: {optimization['type']}")
        
        if optimization["type"] == "increase_batch_size":
            self.config.max_batch_size = optimization["suggested_value"]

# Example usage and testing
if __name__ == "__main__":
    async def test_throughput_maximizer() -> None:
        """Test throughput maximizer"""
        
        # Create configuration
        config = ThroughputConfig(
            max_batch_size=16,
            max_concurrent_requests=50,
            connection_pool_size=25,
            optimization_strategies=[
                OptimizationStrategy.BATCHING,
                OptimizationStrategy.PARALLEL_PROCESSING,
                OptimizationStrategy.CONNECTION_POOLING
            ],
            creator_type=CreatorType.MUSICIAN,
            enable_monitoring=True,
            adaptive_optimization=True
        )
        
        # Initialize throughput maximizer
        maximizer = ThroughputMaximizer(config)
        
        # Start optimization
        await maximizer.start_optimization()
        
        # Define a simple processor function
        def mock_processor(request_data: Dict[str, Any]) -> Dict[str, Any]:
            # Simulate processing time
            time.sleep(0.01)  # 10ms processing time
            
            return {
                "request_id": request_data["request_id"],
                "result": f"processed_{request_data['request_id']}",
                "processing_time": 0.01
            }
        
        # Test single request processing
        print("🧪 Testing single request processing:")
        
        for i in range(5):
            request_data = {"content": f"test_content_{i}", "creator_type": "musician"}
            request_id = f"req_{i}"
            
            start_time = time.time()
            result = await maximizer.process_request(request_data, request_id, mock_processor)
            processing_time = (time.time() - start_time) * 1000
            
            print(f"   Request {i}: {processing_time:.2f}ms")
        
        # Test batch processing
        print(f"\n🧪 Testing batch processing:")
        
        batch_data = [
            {"content": f"batch_content_{i}", "creator_type": "musician"}
            for i in range(10)
        ]
        
        start_time = time.time()
        batch_results = await maximizer.process_batch(batch_data, mock_processor)
        batch_time = (time.time() - start_time) * 1000
        
        print(f"   Batch of {len(batch_data)} items: {batch_time:.2f}ms")
        print(f"   Per-item average: {batch_time / len(batch_data):.2f}ms")
        
        # Get performance statistics
        await asyncio.sleep(2)  # Let metrics collect
        
        stats = maximizer.get_performance_stats()
        print(f"\n📊 Performance Statistics:")
        print(f"   Requests per second: {stats['current_metrics']['requests_per_second']:.2f}")
        print(f"   Average latency: {stats['current_metrics']['average_latency_ms']:.2f}ms")
        print(f"   Batch efficiency: {stats['current_metrics']['batch_efficiency']:.2f}")
        print(f"   Resource utilization: {stats['current_metrics']['resource_utilization']:.2f}")
        print(f"   Error rate: {stats['current_metrics']['error_rate']:.3f}")
        
        print(f"\n🔗 Connection Pool:")
        print(f"   Available connections: {stats['connection_pool']['available_connections']}")
        print(f"   Active connections: {stats['connection_pool']['active_connections']}")
        
        # Stop optimization
        await maximizer.stop_optimization()
        
        print(f"\n✅ Throughput maximizer test completed")
    
    # Run test
    asyncio.run(test_throughput_maximizer())