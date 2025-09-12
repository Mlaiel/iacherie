"""Batch Operations Client for Ainflue SDK

Multi-expert implementation:
- Backend Senior: Robust batch processing architecture
- ML Engineer: Optimized batch ML processing algorithms
- DBA: Efficient data batching and storage strategies
- DevOps: Monitoring and metrics for batch operations
- Lead Dev IA: Intelligent batch optimization and scheduling

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import json
import logging
import time
import hashlib
from typing import Dict, Any, Optional, List, Callable, Union, Iterator
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
import aiofiles
import httpx
from pydantic import BaseModel, Field

from .exceptions import (
    BatchProcessingError, ValidationError, ResourceError,
    TimeoutError, AuthenticationError
)
from .auth_manager import AuthenticationManager


class BatchStatus(Enum):
    """Batch processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class BatchPriority(Enum):
    """Batch processing priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class BatchMetrics:
    """Batch processing metrics (DevOps expertise)"""
    total_batches: int = 0
    completed_batches: int = 0
    failed_batches: int = 0
    total_items: int = 0
    processed_items: int = 0
    average_batch_time: float = 0.0
    throughput_per_second: float = 0.0
    error_rate: float = 0.0
    start_time: Optional[datetime] = None
    last_update: Optional[datetime] = None
    
    @property
    def completion_rate(self) -> float:
        """Calculate completion rate percentage"""
        if self.total_batches == 0:
            return 0.0
        return (self.completed_batches / self.total_batches) * 100
    
    @property
    def processing_time(self) -> float:
        """Total processing time in seconds"""
        if not self.start_time:
            return 0.0
        end_time = self.last_update or datetime.now()
        return (end_time - self.start_time).total_seconds()


class BatchItem(BaseModel):
    """Individual batch item with metadata"""
    id: str = Field(..., description="Unique item identifier")
    data: Dict[str, Any] = Field(..., description="Item data")
    priority: BatchPriority = Field(default=BatchPriority.NORMAL, description="Processing priority")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    timeout: float = Field(default=30.0, description="Processing timeout")
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def can_retry(self) -> bool:
        """Check if item can be retried"""
        return self.retry_count < self.max_retries


class BatchJob(BaseModel):
    """Batch job with intelligent scheduling"""
    id: str = Field(..., description="Unique batch job identifier")
    name: str = Field(..., description="Human-readable batch name")
    items: List[BatchItem] = Field(..., description="Batch items")
    status: BatchStatus = Field(default=BatchStatus.PENDING)
    priority: BatchPriority = Field(default=BatchPriority.NORMAL)
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    progress: float = Field(default=0.0, description="Completion percentage")
    
    # Processing configuration (Backend Senior expertise)
    batch_size: int = Field(default=50, description="Items per batch")
    max_concurrent: int = Field(default=5, description="Maximum concurrent batches")
    timeout: float = Field(default=300.0, description="Total job timeout")
    
    # ML processing settings (ML Engineer expertise)
    ml_model: Optional[str] = Field(default=None, description="ML model to use")
    ml_batch_size: int = Field(default=32, description="ML model batch size")
    use_gpu: bool = Field(default=False, description="Use GPU acceleration")
    
    @property
    def total_items(self) -> int:
        """Total number of items in batch"""
        return len(self.items)
    
    @property
    def processing_time(self) -> float:
        """Processing time in seconds"""
        if not self.started_at:
            return 0.0
        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()


class DatabaseBatchOptimizer:
    """Database batch optimization (DBA expertise)"""
    
    def __init__(self, connection_pool_size: int = 10):
        self.connection_pool_size = connection_pool_size
        self.connection_cache = {}
        
    def optimize_batch_structure(self, items: List[BatchItem]) -> List[List[BatchItem]]:
        """Optimize batch structure for database operations"""
        # Group by data similarity to optimize database queries
        similarity_groups = {}
        
        for item in items:
            # Create a simple hash of the data structure
            data_keys = tuple(sorted(item.data.keys()))
            if data_keys not in similarity_groups:
                similarity_groups[data_keys] = []
            similarity_groups[data_keys].append(item)
        
        # Create optimized batches
        optimized_batches = []
        for group_items in similarity_groups.values():
            # Sort by priority for better processing order
            group_items.sort(key=lambda x: x.priority.value, reverse=True)
            
            # Split into manageable chunks
            chunk_size = 100  # Optimal for most databases
            for i in range(0, len(group_items), chunk_size):
                chunk = group_items[i:i + chunk_size]
                optimized_batches.append(chunk)
        
        return optimized_batches
    
    def prepare_bulk_operations(self, items: List[BatchItem]) -> Dict[str, List[Dict]]:
        """Prepare bulk database operations"""
        operations = {
            "inserts": [],
            "updates": [],
            "deletes": []
        }
        
        for item in items:
            operation_type = item.metadata.get("operation", "insert")
            if operation_type in operations:
                operations[operation_type].append(item.data)
        
        return operations


class MLBatchProcessor:
    """ML batch processing optimization (ML Engineer expertise)"""
    
    def __init__(self, model_cache_size: int = 3):
        self.model_cache = {}
        self.model_cache_size = model_cache_size
        self.gpu_available = False  # Check GPU availability
        
    async def process_ml_batch(self, items: List[BatchItem], model_name: str) -> List[Dict[str, Any]]:
        """Process ML batch with optimized algorithms"""
        try:
            # Load or get cached model
            model = await self._get_model(model_name)
            
            # Prepare data for ML processing
            input_data = [item.data for item in items]
            
            # Optimize batch size for GPU/CPU
            optimal_batch_size = self._calculate_optimal_batch_size(len(input_data))
            
            results = []
            for i in range(0, len(input_data), optimal_batch_size):
                batch_data = input_data[i:i + optimal_batch_size]
                batch_results = await self._process_model_batch(model, batch_data)
                results.extend(batch_results)
            
            return results
            
        except Exception as e:
            logging.error(f"ML batch processing error: {e}")
            raise BatchProcessingError(f"ML processing failed: {e}")
    
    def _calculate_optimal_batch_size(self, data_size: int) -> int:
        """Calculate optimal batch size based on available resources"""
        if self.gpu_available:
            # GPU can handle larger batches
            return min(128, data_size)
        else:
            # CPU processing - smaller batches
            return min(32, data_size)
    
    async def _get_model(self, model_name: str):
        """Get model from cache or load new model"""
        if model_name in self.model_cache:
            return self.model_cache[model_name]
        
        # Simulate model loading (replace with actual ML framework)
        await asyncio.sleep(0.1)  # Model loading time
        
        # Cache management - remove oldest if cache is full
        if len(self.model_cache) >= self.model_cache_size:
            oldest_model = next(iter(self.model_cache))
            del self.model_cache[oldest_model]
        
        # Load new model (simulated)
        model = {"name": model_name, "loaded_at": datetime.now()}
        self.model_cache[model_name] = model
        
        return model
    
    async def _process_model_batch(self, model, batch_data: List[Dict]) -> List[Dict[str, Any]]:
        """Process batch through ML model"""
        # Simulate ML model inference
        await asyncio.sleep(0.01 * len(batch_data))  # Processing time
        
        results = []
        for i, data in enumerate(batch_data):
            result = {
                "input_id": data.get("id", f"item_{i}"),
                "prediction": f"processed_by_{model['name']}",
                "confidence": 0.95,
                "processing_time": 0.01,
                "model_version": "1.0.0"
            }
            results.append(result)
        
        return results


class IntelligentScheduler:
    """Intelligent batch scheduling (Lead Dev IA expertise)"""
    
    def __init__(self):
        self.job_queue = []
        self.running_jobs = {}
        self.completed_jobs = {}
        self.resource_monitor = ResourceMonitor()
        
    def schedule_job(self, job: BatchJob) -> str:
        """Schedule batch job with intelligent prioritization"""
        # Calculate job score for prioritization
        job_score = self._calculate_job_score(job)
        
        # Insert job in priority order
        inserted = False
        for i, (existing_job, _) in enumerate(self.job_queue):
            existing_score = self._calculate_job_score(existing_job)
            if job_score > existing_score:
                self.job_queue.insert(i, (job, job_score))
                inserted = True
                break
        
        if not inserted:
            self.job_queue.append((job, job_score))
        
        logging.info(f"Scheduled job {job.id} with score {job_score}")
        return job.id
    
    def _calculate_job_score(self, job: BatchJob) -> float:
        """Calculate job priority score using multiple factors"""
        # Priority weight
        priority_weight = job.priority.value * 10
        
        # Age weight (older jobs get higher priority)
        age_hours = (datetime.now() - job.created_at).total_seconds() / 3600
        age_weight = min(age_hours * 2, 20)  # Cap at 20 points
        
        # Size weight (smaller jobs get slightly higher priority for quick wins)
        size_weight = max(5 - (job.total_items / 1000), 0)
        
        # Resource availability weight
        resource_weight = self.resource_monitor.get_availability_score()
        
        total_score = priority_weight + age_weight + size_weight + resource_weight
        return total_score
    
    async def process_next_job(self) -> Optional[BatchJob]:
        """Get next job to process based on intelligent scheduling"""
        if not self.job_queue:
            return None
        
        # Check resource availability
        if not self.resource_monitor.can_accept_job():
            return None
        
        # Get highest priority job
        job, score = self.job_queue.pop(0)
        job.status = BatchStatus.PROCESSING
        job.started_at = datetime.now()
        
        self.running_jobs[job.id] = job
        logging.info(f"Started processing job {job.id} (score: {score})")
        
        return job
    
    def complete_job(self, job_id: str, success: bool = True):
        """Mark job as completed"""
        if job_id in self.running_jobs:
            job = self.running_jobs.pop(job_id)
            job.status = BatchStatus.COMPLETED if success else BatchStatus.FAILED
            job.completed_at = datetime.now()
            self.completed_jobs[job_id] = job


class ResourceMonitor:
    """System resource monitoring (DevOps expertise)"""
    
    def __init__(self):
        self.cpu_threshold = 80.0  # CPU usage threshold
        self.memory_threshold = 85.0  # Memory usage threshold
        self.max_concurrent_jobs = 10
        
    def get_availability_score(self) -> float:
        """Get resource availability score (0-10)"""
        # Simulate resource monitoring (replace with actual monitoring)
        cpu_usage = 45.0  # Example CPU usage
        memory_usage = 60.0  # Example memory usage
        
        cpu_score = max(0, (100 - cpu_usage) / 10)
        memory_score = max(0, (100 - memory_usage) / 10)
        
        return (cpu_score + memory_score) / 2
    
    def can_accept_job(self) -> bool:
        """Check if system can accept new jobs"""
        # Simple resource check (enhance with actual monitoring)
        return self.get_availability_score() > 3.0


class BatchClient:
    """Main batch operations client with multi-expert architecture"""
    
    def __init__(self, 
                 auth_manager: AuthenticationManager,
                 max_concurrent_jobs: int = 5):
        self.auth_manager = auth_manager
        self.max_concurrent_jobs = max_concurrent_jobs
        self.logger = logging.getLogger(__name__)
        
        # Expert components
        self.db_optimizer = DatabaseBatchOptimizer()
        self.ml_processor = MLBatchProcessor()
        self.scheduler = IntelligentScheduler()
        
        # Metrics and monitoring
        self.metrics = BatchMetrics()
        self.http_client = None
        
        # Thread pool for concurrent processing
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_jobs)
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.http_client = httpx.AsyncClient(timeout=300.0)
        self.metrics.start_time = datetime.now()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.http_client:
            await self.http_client.aclose()
        self.executor.shutdown(wait=True)
    
    async def submit_batch_job(self, 
                              name: str,
                              items: List[Dict[str, Any]],
                              priority: BatchPriority = BatchPriority.NORMAL,
                              **kwargs) -> str:
        """Submit a new batch job for processing"""
        try:
            # Create batch items
            batch_items = []
            for i, item_data in enumerate(items):
                batch_item = BatchItem(
                    id=f"{name}_{i}",
                    data=item_data,
                    priority=priority
                )
                batch_items.append(batch_item)
            
            # Create batch job
            job_id = hashlib.md5(f"{name}_{datetime.now().isoformat()}".encode()).hexdigest()
            batch_job = BatchJob(
                id=job_id,
                name=name,
                items=batch_items,
                priority=priority,
                **kwargs
            )
            
            # Schedule job
            scheduled_id = self.scheduler.schedule_job(batch_job)
            
            # Update metrics
            self.metrics.total_batches += 1
            self.metrics.total_items += len(items)
            
            self.logger.info(f"Submitted batch job: {scheduled_id} with {len(items)} items")
            return scheduled_id
            
        except Exception as e:
            self.logger.error(f"Failed to submit batch job: {e}")
            raise BatchProcessingError(f"Job submission failed: {e}")
    
    async def process_batch_job(self, job: BatchJob) -> Dict[str, Any]:
        """Process a batch job with expert optimizations"""
        try:
            job.status = BatchStatus.PROCESSING
            start_time = time.time()
            
            # Database optimization (DBA expertise)
            optimized_batches = self.db_optimizer.optimize_batch_structure(job.items)
            
            results = []
            processed_items = 0
            
            for batch_items in optimized_batches:
                if job.ml_model:
                    # ML processing (ML Engineer expertise)
                    batch_results = await self.ml_processor.process_ml_batch(
                        batch_items, job.ml_model
                    )
                else:
                    # Standard processing
                    batch_results = await self._process_standard_batch(batch_items)
                
                results.extend(batch_results)
                processed_items += len(batch_items)
                
                # Update progress
                job.progress = (processed_items / job.total_items) * 100
                self.logger.info(f"Job {job.id} progress: {job.progress:.1f}%")
            
            # Complete job
            processing_time = time.time() - start_time
            job.status = BatchStatus.COMPLETED
            job.completed_at = datetime.now()
            
            # Update metrics
            self.metrics.completed_batches += 1
            self.metrics.processed_items += processed_items
            self.metrics.last_update = datetime.now()
            
            # Update average processing time
            if self.metrics.completed_batches > 0:
                total_time = self.metrics.average_batch_time * (self.metrics.completed_batches - 1)
                total_time += processing_time
                self.metrics.average_batch_time = total_time / self.metrics.completed_batches
            
            result_summary = {
                "job_id": job.id,
                "status": job.status.value,
                "processed_items": processed_items,
                "processing_time": processing_time,
                "throughput": processed_items / processing_time if processing_time > 0 else 0,
                "results": results
            }
            
            self.logger.info(f"Completed batch job {job.id} in {processing_time:.2f}s")
            return result_summary
            
        except Exception as e:
            job.status = BatchStatus.FAILED
            job.error_message = str(e)
            self.metrics.failed_batches += 1
            
            self.logger.error(f"Batch job {job.id} failed: {e}")
            raise BatchProcessingError(f"Batch processing failed: {e}")
    
    async def _process_standard_batch(self, items: List[BatchItem]) -> List[Dict[str, Any]]:
        """Process standard batch without ML"""
        results = []
        
        for item in items:
            try:
                # Simulate processing
                await asyncio.sleep(0.01)  # Processing time
                
                result = {
                    "item_id": item.id,
                    "status": "processed",
                    "processed_at": datetime.now().isoformat(),
                    "processing_time": 0.01
                }
                results.append(result)
                
            except Exception as e:
                # Handle item failure
                if item.can_retry():
                    item.retry_count += 1
                    # Add back to processing queue (simplified)
                    result = {
                        "item_id": item.id,
                        "status": "retry",
                        "error": str(e),
                        "retry_count": item.retry_count
                    }
                else:
                    result = {
                        "item_id": item.id,
                        "status": "failed",
                        "error": str(e),
                        "retry_count": item.retry_count
                    }
                results.append(result)
        
        return results
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get current status of a batch job"""
        # Check running jobs
        if job_id in self.scheduler.running_jobs:
            job = self.scheduler.running_jobs[job_id]
            return {
                "job_id": job_id,
                "status": job.status.value,
                "progress": job.progress,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "processing_time": job.processing_time
            }
        
        # Check completed jobs
        if job_id in self.scheduler.completed_jobs:
            job = self.scheduler.completed_jobs[job_id]
            return {
                "job_id": job_id,
                "status": job.status.value,
                "progress": 100.0,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "processing_time": job.processing_time
            }
        
        # Check queued jobs
        for queued_job, _ in self.scheduler.job_queue:
            if queued_job.id == job_id:
                return {
                    "job_id": job_id,
                    "status": queued_job.status.value,
                    "progress": 0.0,
                    "queue_position": self.scheduler.job_queue.index((queued_job, _)) + 1
                }
        
        raise ValidationError(f"Job {job_id} not found")
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a batch job"""
        # Remove from queue
        for i, (job, score) in enumerate(self.scheduler.job_queue):
            if job.id == job_id:
                job.status = BatchStatus.CANCELLED
                self.scheduler.job_queue.pop(i)
                self.logger.info(f"Cancelled queued job {job_id}")
                return True
        
        # Cancel running job (simplified - in production would need proper cancellation)
        if job_id in self.scheduler.running_jobs:
            job = self.scheduler.running_jobs[job_id]
            job.status = BatchStatus.CANCELLED
            self.logger.info(f"Cancelled running job {job_id}")
            return True
        
        return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current batch processing metrics"""
        # Calculate throughput
        if self.metrics.processing_time > 0:
            self.metrics.throughput_per_second = self.metrics.processed_items / self.metrics.processing_time
        
        # Calculate error rate
        if self.metrics.total_batches > 0:
            self.metrics.error_rate = (self.metrics.failed_batches / self.metrics.total_batches) * 100
        
        return {
            "total_batches": self.metrics.total_batches,
            "completed_batches": self.metrics.completed_batches,
            "failed_batches": self.metrics.failed_batches,
            "completion_rate": self.metrics.completion_rate,
            "total_items": self.metrics.total_items,
            "processed_items": self.metrics.processed_items,
            "average_batch_time": self.metrics.average_batch_time,
            "throughput_per_second": self.metrics.throughput_per_second,
            "error_rate": self.metrics.error_rate,
            "processing_time": self.metrics.processing_time
        }


# Example usage
async def example_batch_usage():
    """Example usage of batch client"""
    from .auth_manager import AuthenticationManager
    
    # Setup authentication
    auth_manager = AuthenticationManager("your-api-key")
    
    async with BatchClient(auth_manager, max_concurrent_jobs=3) as client:
        # Submit a batch job
        items = [
            {"id": f"item_{i}", "data": f"process_this_{i}"}
            for i in range(100)
        ]
        
        job_id = await client.submit_batch_job(
            name="example_batch",
            items=items,
            priority=BatchPriority.HIGH,
            ml_model="text_processor"
        )
        
        print(f"Submitted job: {job_id}")
        
        # Monitor job status
        while True:
            status = await client.get_job_status(job_id)
            print(f"Job status: {status}")
            
            if status["status"] in ["completed", "failed", "cancelled"]:
                break
            
            await asyncio.sleep(1)
        
        # Get final metrics
        metrics = client.get_metrics()
        print(f"Final metrics: {metrics}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_batch_usage())