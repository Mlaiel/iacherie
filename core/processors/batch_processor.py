"""Batch Processor Module - IA-Influencer-Agent Platform

Industrial-grade batch processing engine for content creators and influencers.
Handles bulk content processing, scheduled jobs, and large-scale operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Any unauthorized use, copying, 
distribution, or commercialization without explicit written permission is 
strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
================================================================================
"""

import asyncio
import logging
import hashlib
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Union, BinaryIO, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import concurrent.futures
from collections import defaultdict

# Import content processor for individual processing
from .content_processor import ContentProcessor, ContentProcessingConfig

# Batch processing imports
try:
    import pandas as pd
    import numpy as np
    BATCH_LIBS_AVAILABLE = True
except ImportError:
    BATCH_LIBS_AVAILABLE = False

# Distributed processing
try:
    from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
    import multiprocessing
    PARALLEL_PROCESSING_AVAILABLE = True
except ImportError:
    PARALLEL_PROCESSING_AVAILABLE = False

# Progress tracking
try:
    from tqdm import tqdm
    PROGRESS_TRACKING_AVAILABLE = True
except ImportError:
    PROGRESS_TRACKING_AVAILABLE = False

logger = logging.getLogger(__name__)


class BatchType(str, Enum):
    """
Types of batch operations"""

    BULK_UPLOAD = "bulk_upload"
    BULK_ANALYSIS = "bulk_analysis"
    BULK_ENHANCEMENT = "bulk_enhancement"
    BULK_PROTECTION = "bulk_protection"
    BULK_DISTRIBUTION = "bulk_distribution"
    SCHEDULED_PROCESSING = "scheduled_processing"
    MIGRATION = "migration"
    BACKUP = "backup"
    CLEANUP = "cleanup"
    QUALITY_AUDIT = "quality_audit"
    COMPLIANCE_CHECK = "compliance_check"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"


class BatchStatus(str, Enum):
    """Batch operation status"""

    PENDING = "pending"
    PREPARING = "preparing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIALLY_COMPLETED = "partially_completed"


class BatchPriority(str, Enum):
    """Batch processing priority"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ProcessingStrategy(str, Enum):
    """Batch processing strategies"""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"
    STREAMING = "streaming"
    CHUNKED = "chunked"


@dataclass
class BatchProcessingConfig:
    """Configuration for batch processing"""
    # Processing strategy
    default_strategy: ProcessingStrategy = ProcessingStrategy.PARALLEL
    max_parallel_jobs: int = 4
    max_concurrent_batches: int = 2
    chunk_size: int = 100
    
    # Resource management
    max_memory_usage: int = 4 * 1024 * 1024 * 1024  # 4GB
    max_disk_usage: int = 100 * 1024 * 1024 * 1024  # 100GB
    cpu_usage_limit: float = 0.8  # 80%
    
    # Retry and error handling
    retry_attempts: int = 3
    retry_delay: int = 300  # 5 minutes
    continue_on_error: bool = True
    error_threshold: float = 0.1  # 10% failure rate
    
    # Progress and monitoring
    enable_progress_tracking: bool = True
    progress_update_interval: int = 30  # seconds
    enable_detailed_logging: bool = True
    save_intermediate_results: bool = True
    
    # Scheduling
    enable_scheduling: bool = True
    default_schedule_time: Optional[str] = None  # "02:00" for 2 AM
    max_batch_duration: int = 24 * 3600  # 24 hours
    
    # Output and results
    output_directory: Optional[str] = None
    generate_reports: bool = True
    compress_results: bool = True
    cleanup_temp_files: bool = True
    
    # Content processor config
    content_processor_config: Optional[Dict[str, Any]] = None


@dataclass
class BatchItem:
    """Individual item in a batch"""
    item_id: str
    content_path: Optional[str] = None
    content_data: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    processing_time: float = 0.0
    retry_count: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class BatchJob:
    """Batch processing job"""
    batch_id: str
    batch_type: BatchType
    name: Optional[str] = None
    description: Optional[str] = None
    status: BatchStatus = BatchStatus.PENDING
    priority: BatchPriority = BatchPriority.NORMAL
    strategy: ProcessingStrategy = ProcessingStrategy.PARALLEL
    
    # Items and progress
    items: List[BatchItem] = field(default_factory=list)
    total_items: int = 0
    processed_items: int = 0
    successful_items: int = 0
    failed_items: int = 0
    skipped_items: int = 0
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    
    # Progress and statistics
    progress_percentage: float = 0.0
    current_item: Optional[str] = None
    processing_rate: float = 0.0  # items per second
    average_item_time: float = 0.0
    
    # Configuration
    config: Optional[BatchProcessingConfig] = None
    options: Dict[str, Any] = field(default_factory=dict)
    
    # Results and output
    results_summary: Dict[str, Any] = field(default_factory=dict)
    output_files: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    # Resource usage
    peak_memory_usage: float = 0.0
    peak_cpu_usage: float = 0.0
    total_processing_time: float = 0.0
    
    # Creator information
    creator_id: Optional[str] = None
    creator_name: Optional[str] = None


@dataclass
class BatchReport:
    """
Batch processing report"""
    batch_id: str
    batch_name: Optional[str] = None
    execution_summary: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    error_analysis: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    detailed_results: List[Dict[str, Any]] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)


class BatchProcessor:
    """
    🔄 ENTERPRISE BATCH PROCESSOR
    
    Industrial-grade batch processing engine with advanced scheduling,
    parallel processing, and comprehensive monitoring capabilities.
    """
    
    def __init__(
        self,
        db_session,
        redis_client,
        config: Optional[BatchProcessingConfig] = None
    ):
        self.db_session = db_session
        self.redis_client = redis_client
        self.config = config or BatchProcessingConfig()
        self.logger = logging.getLogger(f"{__name__}.BatchProcessor")
        
        # Content processor
        self.content_processor = None
        
        # Batch management
        self._active_batches: Dict[str, BatchJob] = {}
        self._batch_queue = asyncio.Queue()
        self._scheduler_tasks = []
        self._worker_tasks = []
        self._monitoring_task = None
        
        # Resource monitoring
        self._resource_monitor = {
            "memory_usage": 0.0,
            "cpu_usage": 0.0,
            "disk_usage": 0.0,
            "active_jobs": 0
        }
        
        # Statistics
        self._stats = {
            "total_batches": 0,
            "completed_batches": 0,
            "failed_batches": 0,
            "total_items_processed": 0,
            "average_batch_time": 0.0,
            "peak_parallel_jobs": 0
        }
        
        self._initialized = False
        self._shutdown_event = asyncio.Event()
        
        if not BATCH_LIBS_AVAILABLE:
            self.logger.warning("Batch processing libraries not available")
        
        if not PARALLEL_PROCESSING_AVAILABLE:
            self.logger.warning("Parallel processing not available")
    
    async def initialize(self) -> bool:
        """Initialize the batch processor"""
        try:
            # Initialize content processor
            self.content_processor = ContentProcessor(
                db_session=self.db_session,
                redis_client=self.redis_client,
                config=ContentProcessingConfig(**(self.config.content_processor_config or {}))
            )
            await self.content_processor.initialize()
            
            # Create output directory
            if self.config.output_directory:
                output_path = Path(self.config.output_directory)
                output_path.mkdir(parents=True, exist_ok=True)
            
            # Start worker tasks
            await self._start_workers()
            
            # Start monitoring task
            if self.config.enable_progress_tracking:
                self._monitoring_task = asyncio.create_task(self._monitor_resources())
            
            self._initialized = True
            self.logger.info("✅ Batch processor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize batch processor: {e}")
            return False
    
    async def create_batch(
        self,
        batch_type: BatchType,
        items: List[Dict[str, Any]],
        name: Optional[str] = None,
        description: Optional[str] = None,
        priority: BatchPriority = BatchPriority.NORMAL,
        strategy: Optional[ProcessingStrategy] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new batch processing job
        
        Args:
            batch_type: Type of batch operation
            items: List of items to process
            name: Optional batch name
            description: Optional description
            priority: Processing priority
            strategy: Processing strategy
            options: Additional options
            
        Returns:
            Batch creation result
        """
        try:
            if not self._initialized:
                await self.initialize()
            
            # Generate batch ID
            batch_id = str(uuid.uuid4())
            
            # Create batch items
            batch_items = []
            for i, item_data in enumerate(items):
                item = BatchItem(
                    item_id=f"{batch_id}_{i}",
                    content_path=item_data.get("content_path"),
                    content_data=item_data.get("content_data"),
                    metadata=item_data.get("metadata", {}),
                    options=item_data.get("options", {})
                )
                batch_items.append(item)
            
            # Create batch job
            batch_job = BatchJob(
                batch_id=batch_id,
                batch_type=batch_type,
                name=name or f"Batch_{batch_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                description=description,
                priority=priority,
                strategy=strategy or self.config.default_strategy,
                items=batch_items,
                total_items=len(batch_items),
                config=self.config,
                options=options or {}
            )
            
            # Add to queue
            await self._batch_queue.put(batch_job)
            self._active_batches[batch_id] = batch_job
            
            self.logger.info(f"Created batch {batch_id} with {len(batch_items)} items")
            
            return {
                "success": True,
                "batch_id": batch_id,
                "batch_name": batch_job.name,
                "total_items": len(batch_items),
                "estimated_start": datetime.now() + timedelta(minutes=5),
                "queue_position": self._batch_queue.qsize()
            }
            
        except Exception as e:
            self.logger.error(f"Batch creation failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Get status of a batch job"""
        try:
            if batch_id not in self._active_batches:
                return {
                    "success": False,
                    "error_message": "Batch not found"
                }
            
            batch = self._active_batches[batch_id]
            
            return {
                "success": True,
                "batch_id": batch.batch_id,
                "name": batch.name,
                "status": batch.status.value,
                "progress": {
                    "percentage": batch.progress_percentage,
                    "processed_items": batch.processed_items,
                    "total_items": batch.total_items,
                    "successful_items": batch.successful_items,
                    "failed_items": batch.failed_items,
                    "current_item": batch.current_item
                },
                "timing": {
                    "created_at": batch.created_at.isoformat(),
                    "started_at": batch.started_at.isoformat() if batch.started_at else None,
                    "estimated_completion": batch.estimated_completion.isoformat() if batch.estimated_completion else None,
                    "processing_rate": batch.processing_rate,
                    "average_item_time": batch.average_item_time
                },
                "resources": {
                    "memory_usage": batch.peak_memory_usage,
                    "cpu_usage": batch.peak_cpu_usage
                }
            }
            
        except Exception as e:
            self.logger.error(f"Batch status retrieval failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def cancel_batch(self, batch_id: str) -> Dict[str, Any]:
        """Cancel a batch job"""
        try:
            if batch_id not in self._active_batches:
                return {
                    "success": False,
                    "error_message": "Batch not found"
                }
            
            batch = self._active_batches[batch_id]
            
            if batch.status in [BatchStatus.COMPLETED, BatchStatus.FAILED, BatchStatus.CANCELLED]:
                return {
                    "success": False,
                    "error_message": f"Cannot cancel batch in {batch.status.value} status"
                }
            
            batch.status = BatchStatus.CANCELLED
            
            self.logger.info(f"Batch {batch_id} cancelled")
            
            return {
                "success": True,
                "message": "Batch cancelled successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Batch cancellation failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def pause_batch(self, batch_id: str) -> Dict[str, Any]:
        """Pause a batch job"""
        try:
            if batch_id not in self._active_batches:
                return {
                    "success": False,
                    "error_message": "Batch not found"
                }
            
            batch = self._active_batches[batch_id]
            
            if batch.status != BatchStatus.RUNNING:
                return {
                    "success": False,
                    "error_message": f"Cannot pause batch in {batch.status.value} status"
                }
            
            batch.status = BatchStatus.PAUSED
            
            return {
                "success": True,
                "message": "Batch paused successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def resume_batch(self, batch_id: str) -> Dict[str, Any]:
        """Resume a paused batch job"""
        try:
            if batch_id not in self._active_batches:
                return {
                    "success": False,
                    "error_message": "Batch not found"
                }
            
            batch = self._active_batches[batch_id]
            
            if batch.status != BatchStatus.PAUSED:
                return {
                    "success": False,
                    "error_message": f"Cannot resume batch in {batch.status.value} status"
                }
            
            batch.status = BatchStatus.RUNNING
            
            return {
                "success": True,
                "message": "Batch resumed successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def get_batch_report(self, batch_id: str) -> Dict[str, Any]:
        """Generate comprehensive batch report"""
        try:
            if batch_id not in self._active_batches:
                return {
                    "success": False,
                    "error_message": "Batch not found"
                }
            
            batch = self._active_batches[batch_id]
            
            # Generate report
            report = await self._generate_batch_report(batch)
            
            return {
                "success": True,
                "report": report.__dict__
            }
            
        except Exception as e:
            self.logger.error(f"Batch report generation failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def list_batches(
        self,
        status_filter: Optional[BatchStatus] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """List batch jobs with optional filtering"""
        try:
            batches = []
            
            for batch in self._active_batches.values():
                if status_filter and batch.status != status_filter:
                    continue
                
                batches.append({
                    "batch_id": batch.batch_id,
                    "name": batch.name,
                    "type": batch.batch_type.value,
                    "status": batch.status.value,
                    "progress": batch.progress_percentage,
                    "total_items": batch.total_items,
                    "processed_items": batch.processed_items,
                    "created_at": batch.created_at.isoformat(),
                    "started_at": batch.started_at.isoformat() if batch.started_at else None
                })
                
                if len(batches) >= limit:
                    break
            
            return {
                "success": True,
                "batches": batches,
                "total_count": len(self._active_batches)
            }
            
        except Exception as e:
            self.logger.error(f"Batch listing failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def _start_workers(self):
        """Start batch processing workers"""
        try:
            # Start batch workers
            for i in range(self.config.max_concurrent_batches):
                worker_task = asyncio.create_task(
                    self._batch_worker(f"batch-worker-{i}")
                )
                self._worker_tasks.append(worker_task)
            
            self.logger.info(f"Started {len(self._worker_tasks)} batch workers")
            
        except Exception as e:
            self.logger.error(f"Worker startup failed: {e}")
            raise
    
    async def _batch_worker(self, worker_id: str):
        """Worker loop for processing batches"""
        while not self._shutdown_event.is_set():
            try:
                # Get batch from queue
                batch = await asyncio.wait_for(
                    self._batch_queue.get(),
                    timeout=1.0
                )
                
                # Process batch
                await self._process_batch(batch, worker_id)
                
            except asyncio.TimeoutError:
                # No batches available, continue
                continue
            except Exception as e:
                self.logger.error(f"Batch worker {worker_id} error: {e}")
                await asyncio.sleep(1)
    
    async def _process_batch(self, batch: BatchJob, worker_id: str):
        """Process a complete batch"""
        try:
            batch.status = BatchStatus.RUNNING
            batch.started_at = datetime.now()
            
            self.logger.info(f"Worker {worker_id} processing batch {batch.batch_id}")
            
            # Update statistics
            self._stats["total_batches"] += 1
            self._resource_monitor["active_jobs"] += 1
            
            # Process based on strategy
            if batch.strategy == ProcessingStrategy.SEQUENTIAL:
                await self._process_sequential(batch)
            elif batch.strategy == ProcessingStrategy.PARALLEL:
                await self._process_parallel(batch)
            elif batch.strategy == ProcessingStrategy.ADAPTIVE:
                await self._process_adaptive(batch)
            elif batch.strategy == ProcessingStrategy.CHUNKED:
                await self._process_chunked(batch)
            else:
                await self._process_parallel(batch)  # Default
            
            # Finalize batch
            await self._finalize_batch(batch)
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            batch.status = BatchStatus.FAILED
            batch.errors.append(str(e))
            self._stats["failed_batches"] += 1
        finally:
            self._resource_monitor["active_jobs"] -= 1
            batch.completed_at = datetime.now()
            if batch.started_at:
                batch.total_processing_time = (batch.completed_at - batch.started_at).total_seconds()
    
    async def _process_sequential(self, batch: BatchJob):
        """Process batch items sequentially"""
        try:
            for i, item in enumerate(batch.items):
                if batch.status == BatchStatus.CANCELLED:
                    break
                
                while batch.status == BatchStatus.PAUSED:
                    await asyncio.sleep(1)
                
                # Process item
                await self._process_item(batch, item)
                
                # Update progress
                await self._update_batch_progress(batch, i + 1)
                
        except Exception as e:
            self.logger.error(f"Sequential processing failed: {e}")
            raise
    
    async def _process_parallel(self, batch: BatchJob):
        """Process batch items in parallel"""
        try:
            semaphore = asyncio.Semaphore(self.config.max_parallel_jobs)
            
            async def process_with_semaphore(item):
                async with semaphore:
                    if batch.status == BatchStatus.CANCELLED:
                        return
                    
                    while batch.status == BatchStatus.PAUSED:
                        await asyncio.sleep(1)
                    
                    await self._process_item(batch, item)
            
            # Create tasks for all items
            tasks = [
                asyncio.create_task(process_with_semaphore(item))
                for item in batch.items
            ]
            
            # Process with progress updates
            completed = 0
            for task in asyncio.as_completed(tasks):
                await task
                completed += 1
                await self._update_batch_progress(batch, completed)
                
                if batch.status == BatchStatus.CANCELLED:
                    # Cancel remaining tasks
                    for remaining_task in tasks:
                        if not remaining_task.done():
                            remaining_task.cancel()
                    break
            
        except Exception as e:
            self.logger.error(f"Parallel processing failed: {e}")
            raise
    
    async def _process_adaptive(self, batch: BatchJob):
        """Process batch with adaptive strategy based on resource usage"""
        try:
            # Start with sequential and adapt based on resource usage
            current_parallel = 1
            max_parallel = self.config.max_parallel_jobs
            
            items_processed = 0
            
            while items_processed < len(batch.items):
                if batch.status == BatchStatus.CANCELLED:
                    break
                
                while batch.status == BatchStatus.PAUSED:
                    await asyncio.sleep(1)
                
                # Determine optimal parallelism
                current_parallel = await self._calculate_optimal_parallelism(
                    current_parallel, max_parallel
                )
                
                # Process next chunk
                chunk_end = min(items_processed + current_parallel, len(batch.items))
                chunk_items = batch.items[items_processed:chunk_end]
                
                # Process chunk in parallel
                semaphore = asyncio.Semaphore(current_parallel)
                
                async def process_with_semaphore(item):
                    async with semaphore:
                        await self._process_item(batch, item)
                
                tasks = [
                    asyncio.create_task(process_with_semaphore(item))
                    for item in chunk_items
                ]
                
                await asyncio.gather(*tasks)
                
                items_processed = chunk_end
                await self._update_batch_progress(batch, items_processed)
            
        except Exception as e:
            self.logger.error(f"Adaptive processing failed: {e}")
            raise
    
    async def _process_chunked(self, batch: BatchJob):
        """Process batch in chunks"""
        try:
            chunk_size = self.config.chunk_size
            total_items = len(batch.items)
            
            for start_idx in range(0, total_items, chunk_size):
                if batch.status == BatchStatus.CANCELLED:
                    break
                
                while batch.status == BatchStatus.PAUSED:
                    await asyncio.sleep(1)
                
                # Get chunk
                end_idx = min(start_idx + chunk_size, total_items)
                chunk = batch.items[start_idx:end_idx]
                
                # Process chunk in parallel
                semaphore = asyncio.Semaphore(self.config.max_parallel_jobs)
                
                async def process_with_semaphore(item):
                    async with semaphore:
                        await self._process_item(batch, item)
                
                tasks = [
                    asyncio.create_task(process_with_semaphore(item))
                    for item in chunk
                ]
                
                await asyncio.gather(*tasks)
                
                # Update progress
                await self._update_batch_progress(batch, end_idx)
            
        except Exception as e:
            self.logger.error(f"Chunked processing failed: {e}")
            raise
    
    async def _process_item(self, batch: BatchJob, item: BatchItem):
        """Process a single batch item"""
        start_time = time.time()
        
        try:
            item.status = "processing"
            item.started_at = datetime.now()
            batch.current_item = item.item_id
            
            # Prepare content
            content = None
            if item.content_path:
                content = item.content_path
            elif item.content_data:
                content = item.content_data
            else:
                raise ValueError("No content provided for item")
            
            # Route to appropriate processing based on batch type
            if batch.batch_type == BatchType.BULK_ANALYSIS:
                result = await self.content_processor.process_content(
                    content=content,
                    options=item.options,
                    metadata=item.metadata
                )
            elif batch.batch_type == BatchType.BULK_ENHANCEMENT:
                # Enhanced processing with auto-enhancement enabled
                enhanced_options = {**item.options, "enhance": True}
                result = await self.content_processor.process_content(
                    content=content,
                    options=enhanced_options,
                    metadata=item.metadata
                )
            else:
                # Default processing
                result = await self.content_processor.process_content(
                    content=content,
                    options=item.options,
                    metadata=item.metadata
                )
            
            if result["success"]:
                item.status = "completed"
                item.result = result
                batch.successful_items += 1
            else:
                item.status = "failed"
                item.error_message = result.get("error_message", "Unknown error")
                batch.failed_items += 1
                
                if not self.config.continue_on_error:
                    batch.status = BatchStatus.FAILED
                    return
            
        except Exception as e:
            item.status = "failed"
            item.error_message = str(e)
            batch.failed_items += 1
            
            self.logger.error(f"Item processing failed: {e}")
            
            if not self.config.continue_on_error:
                batch.status = BatchStatus.FAILED
                return
        finally:
            item.completed_at = datetime.now()
            item.processing_time = time.time() - start_time
            batch.processed_items += 1
    
    async def _update_batch_progress(self, batch: BatchJob, completed_items: int):
        """Update batch progress and statistics"""
        try:
            batch.processed_items = completed_items
            batch.progress_percentage = (completed_items / batch.total_items) * 100
            
            # Calculate processing rate
            if batch.started_at:
                elapsed_time = (datetime.now() - batch.started_at).total_seconds()
                if elapsed_time > 0:
                    batch.processing_rate = completed_items / elapsed_time
            
            # Calculate average item time
            completed_item_times = [
                item.processing_time for item in batch.items
                if item.status in ["completed", "failed"] and item.processing_time > 0
            ]
            
            if completed_item_times:
                batch.average_item_time = sum(completed_item_times) / len(completed_item_times)
                
                # Estimate completion time
                remaining_items = batch.total_items - completed_items
                if batch.processing_rate > 0:
                    remaining_time = remaining_items / batch.processing_rate
                    batch.estimated_completion = datetime.now() + timedelta(seconds=remaining_time)
            
            # Log progress
            if self.config.enable_detailed_logging:
                self.logger.info(
                    f"Batch {batch.batch_id}: {completed_items}/{batch.total_items} "
                    f"({batch.progress_percentage:.1f}%) - "
                    f"Success: {batch.successful_items}, Failed: {batch.failed_items}"
                )
            
        except Exception as e:
            self.logger.error(f"Progress update failed: {e}")
    
    async def _calculate_optimal_parallelism(
        self,
        current_parallel: int,
        max_parallel: int
    ) -> int:
        """Calculate optimal parallelism based on resource usage"""
        try:
            memory_usage = self._resource_monitor["memory_usage"]
            cpu_usage = self._resource_monitor["cpu_usage"]
            
            # Adjust based on resource usage
            if memory_usage > 0.9 or cpu_usage > 0.9:
                # High resource usage - reduce parallelism
                return max(1, current_parallel - 1)
            elif memory_usage < 0.5 and cpu_usage < 0.5:
                # Low resource usage - increase parallelism
                return min(max_parallel, current_parallel + 1)
            else:
                # Maintain current level
                return current_parallel
                
        except Exception as e:
            self.logger.error(f"Parallelism calculation failed: {e}")
            return current_parallel
    
    async def _finalize_batch(self, batch: BatchJob):
        """Finalize batch processing"""
        try:
            # Determine final status
            if batch.status != BatchStatus.CANCELLED:
                if batch.failed_items == 0:
                    batch.status = BatchStatus.COMPLETED
                elif batch.successful_items > 0:
                    batch.status = BatchStatus.PARTIALLY_COMPLETED
                else:
                    batch.status = BatchStatus.FAILED
            
            # Update statistics
            if batch.status == BatchStatus.COMPLETED:
                self._stats["completed_batches"] += 1
            elif batch.status == BatchStatus.FAILED:
                self._stats["failed_batches"] += 1
            
            self._stats["total_items_processed"] += batch.processed_items
            
            # Update average batch time
            if batch.total_processing_time > 0:
                current_avg = self._stats["average_batch_time"]
                total_batches = self._stats["total_batches"]
                self._stats["average_batch_time"] = (
                    (current_avg * (total_batches - 1) + batch.total_processing_time) / total_batches
                )
            
            # Generate results summary
            batch.results_summary = await self._generate_results_summary(batch)
            
            # Save results if configured
            if self.config.save_intermediate_results:
                await self._save_batch_results(batch)
            
            # Generate report if configured
            if self.config.generate_reports:
                report = await self._generate_batch_report(batch)
                await self._save_batch_report(batch, report)
            
            # Cleanup if configured
            if self.config.cleanup_temp_files:
                await self._cleanup_batch_temp_files(batch)
            
            self.logger.info(
                f"Batch {batch.batch_id} finalized: {batch.status.value} - "
                f"Success: {batch.successful_items}, Failed: {batch.failed_items}"
            )
            
        except Exception as e:
            self.logger.error(f"Batch finalization failed: {e}")
    
    async def _generate_results_summary(self, batch: BatchJob) -> Dict[str, Any]:
        """Generate batch results summary"""
        try:
            summary = {
                "execution": {
                    "total_items": batch.total_items,
                    "processed_items": batch.processed_items,
                    "successful_items": batch.successful_items,
                    "failed_items": batch.failed_items,
                    "success_rate": batch.successful_items / batch.total_items if batch.total_items > 0 else 0,
                    "total_processing_time": batch.total_processing_time,
                    "average_item_time": batch.average_item_time,
                    "processing_rate": batch.processing_rate
                },
                "performance": {
                    "peak_memory_usage": batch.peak_memory_usage,
                    "peak_cpu_usage": batch.peak_cpu_usage,
                    "strategy_used": batch.strategy.value
                },
                "quality": await self._analyze_batch_quality(batch),
                "errors": await self._analyze_batch_errors(batch)
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Results summary generation failed: {e}")
            return {}
    
    async def _analyze_batch_quality(self, batch: BatchJob) -> Dict[str, Any]:
        """Analyze quality metrics for the batch"""
        try:
            quality_scores = []
            
            for item in batch.items:
                if item.status == "completed" and item.result:
                    # Extract quality metrics from item results
                    quality_metrics = item.result.get("quality_metrics", {})
                    if quality_metrics:
                        overall_quality = quality_metrics.get("overall_quality")
                        if overall_quality is not None:
                            quality_scores.append(overall_quality)
            
            if quality_scores:
                return {
                    "average_quality": sum(quality_scores) / len(quality_scores),
                    "min_quality": min(quality_scores),
                    "max_quality": max(quality_scores),
                    "quality_distribution": await self._calculate_quality_distribution(quality_scores)
                }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Quality analysis failed: {e}")
            return {}
    
    async def _analyze_batch_errors(self, batch: BatchJob) -> Dict[str, Any]:
        """Analyze error patterns in the batch"""
        try:
            error_types = defaultdict(int)
            error_messages = []
            
            for item in batch.items:
                if item.status == "failed" and item.error_message:
                    error_messages.append(item.error_message)
                    
                    # Categorize error types
                    error_msg = item.error_message.lower()
                    if "timeout" in error_msg:
                        error_types["timeout"] += 1
                    elif "memory" in error_msg:
                        error_types["memory"] += 1
                    elif "format" in error_msg or "unsupported" in error_msg:
                        error_types["format"] += 1
                    elif "permission" in error_msg or "access" in error_msg:
                        error_types["permission"] += 1
                    else:
                        error_types["other"] += 1
            
            return {
                "error_types": dict(error_types),
                "error_rate": batch.failed_items / batch.total_items if batch.total_items > 0 else 0,
                "error_messages": error_messages[:10]  # First 10 error messages
            }
            
        except Exception as e:
            self.logger.error(f"Error analysis failed: {e}")
            return {}
    
    async def _calculate_quality_distribution(self, quality_scores: List[float]) -> Dict[str, int]:
        """Calculate quality score distribution"""
        try:
            distribution = {
                "excellent": 0,  # 0.9-1.0
                "good": 0,       # 0.7-0.9
                "fair": 0,       # 0.5-0.7
                "poor": 0        # 0.0-0.5
            }
            
            for score in quality_scores:
                if score >= 0.9:
                    distribution["excellent"] += 1
                elif score >= 0.7:
                    distribution["good"] += 1
                elif score >= 0.5:
                    distribution["fair"] += 1
                else:
                    distribution["poor"] += 1
            
            return distribution
            
        except Exception as e:
            self.logger.error(f"Quality distribution calculation failed: {e}")
            return {}
    
    async def _generate_batch_report(self, batch: BatchJob) -> BatchReport:
        """Generate comprehensive batch report"""
        try:
            report = BatchReport(
                batch_id=batch.batch_id,
                batch_name=batch.name,
                execution_summary=batch.results_summary.get("execution", {}),
                performance_metrics=batch.results_summary.get("performance", {}),
                error_analysis=batch.results_summary.get("errors", {}),
                quality_metrics=batch.results_summary.get("quality", {})
            )
            
            # Generate recommendations
            report.recommendations = await self._generate_recommendations(batch)
            
            # Add detailed results for failed items
            for item in batch.items:
                if item.status == "failed":
                    report.detailed_results.append({
                        "item_id": item.item_id,
                        "error": item.error_message,
                        "retry_count": item.retry_count
                    })
            
            return report
            
        except Exception as e:
            self.logger.error(f"Batch report generation failed: {e}")
            return BatchReport(batch_id=batch.batch_id)
    
    async def _generate_recommendations(self, batch: BatchJob) -> List[str]:
        """Generate recommendations based on batch results"""
        try:
            recommendations = []
            
            # Performance recommendations
            if batch.average_item_time > 60:  # Items taking more than 1 minute
                recommendations.append("Consider optimizing content processing pipeline for better performance")
            
            if batch.peak_memory_usage > 0.8:
                recommendations.append("High memory usage detected - consider processing smaller batches")
            
            # Quality recommendations
            quality_metrics = batch.results_summary.get("quality", {})
            if quality_metrics.get("average_quality", 1.0) < 0.7:
                recommendations.append("Low average quality detected - review content enhancement settings")
            
            # Error recommendations
            error_analysis = batch.results_summary.get("errors", {})
            error_rate = error_analysis.get("error_rate", 0)
            
            if error_rate > 0.1:  # More than 10% failure rate
                recommendations.append("High error rate detected - review input content quality and format support")
            
            error_types = error_analysis.get("error_types", {})
            if error_types.get("timeout", 0) > 0:
                recommendations.append("Timeout errors detected - consider increasing processing timeout limits")
            
            if error_types.get("memory", 0) > 0:
                recommendations.append("Memory errors detected - reduce batch size or optimize memory usage")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendations generation failed: {e}")
            return []
    
    async def _save_batch_results(self, batch: BatchJob):
        """Save batch results to file"""
        try:
            if not self.config.output_directory:
                return
            
            output_dir = Path(self.config.output_directory)
            results_file = output_dir / f"batch_{batch.batch_id}_results.json"
            
            results_data = {
                "batch_info": {
                    "batch_id": batch.batch_id,
                    "name": batch.name,
                    "type": batch.batch_type.value,
                    "status": batch.status.value,
                    "created_at": batch.created_at.isoformat(),
                    "completed_at": batch.completed_at.isoformat() if batch.completed_at else None
                },
                "summary": batch.results_summary,
                "items": [
                    {
                        "item_id": item.item_id,
                        "status": item.status,
                        "processing_time": item.processing_time,
                        "error_message": item.error_message,
                        "result": item.result
                    }
                    for item in batch.items
                ]
            }
            
            with open(results_file, 'w') as f:
                json.dump(results_data, f, indent=2, default=str)
            
            batch.output_files.append(str(results_file))
            
        except Exception as e:
            self.logger.error(f"Batch results saving failed: {e}")
    
    async def _save_batch_report(self, batch: BatchJob, report: BatchReport):
        """Save batch report to file"""
        try:
            if not self.config.output_directory:
                return
            
            output_dir = Path(self.config.output_directory)
            report_file = output_dir / f"batch_{batch.batch_id}_report.json"
            
            with open(report_file, 'w') as f:
                json.dump(report.__dict__, f, indent=2, default=str)
            
            batch.output_files.append(str(report_file))
            
        except Exception as e:
            self.logger.error(f"Batch report saving failed: {e}")
    
    async def _cleanup_batch_temp_files(self, batch: BatchJob):
        """Clean up temporary files created during batch processing"""
        try:
            # Placeholder for temp file cleanup
            logger.debug('Method executed')
            return True
        except Exception as e:
            self.logger.error(f"Temp file cleanup failed: {e}")
    
    async def _monitor_resources(self):
        """Monitor system resources"""
        while not self._shutdown_event.is_set():
            try:
                # Monitor memory usage (placeholder)
                self._resource_monitor["memory_usage"] = 0.5  # Simulated
                
                # Monitor CPU usage (placeholder)
                self._resource_monitor["cpu_usage"] = 0.4  # Simulated
                
                # Monitor disk usage (placeholder)
                self._resource_monitor["disk_usage"] = 0.3  # Simulated
                
                await asyncio.sleep(self.config.progress_update_interval)
                
            except Exception as e:
                self.logger.error(f"Resource monitoring failed: {e}")
                await asyncio.sleep(5)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get batch processor statistics"""
        return {
            "batch_stats": self._stats,
            "resource_usage": self._resource_monitor,
            "active_batches": len(self._active_batches),
            "queue_size": self._batch_queue.qsize()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the batch processor"""
        health_status = {
            "status": "healthy" if self._initialized else "not_initialized",
            "batch_libs_available": BATCH_LIBS_AVAILABLE,
            "parallel_processing_available": PARALLEL_PROCESSING_AVAILABLE,
            "progress_tracking_available": PROGRESS_TRACKING_AVAILABLE,
            "active_batches": len(self._active_batches),
            "worker_count": len(self._worker_tasks),
            "resource_usage": self._resource_monitor,
            "statistics": self._stats,
            "config": self.config.__dict__
        }
        
        # Check content processor
        if self.content_processor:
            health_status["content_processor"] = await self.content_processor.health_check()
        
        return health_status
    
    async def shutdown(self):
        """Gracefully shutdown the batch processor"""
        try:
            self._shutdown_event.set()
            
            # Cancel all worker tasks
            for task in self._worker_tasks:
                task.cancel()
            
            if self._monitoring_task:
                self._monitoring_task.cancel()
            
            # Wait for tasks to complete
            all_tasks = self._worker_tasks + ([self._monitoring_task] if self._monitoring_task else [])
            await asyncio.gather(*all_tasks, return_exceptions=True)
            
            # Shutdown content processor
            if self.content_processor:
                await self.content_processor.shutdown()
            
            self.logger.info("Batch processor shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Shutdown failed: {e}")


async def create_batch_processor(
    db_session,
    redis_client,
    config: Optional[Dict[str, Any]] = None
) -> BatchProcessor:
    """
    Factory function to create and initialize a batch processor
    
    Args:
        db_session: Database session
        redis_client: Redis client
        config: Configuration dictionary
        
    Returns:
        Initialized BatchProcessor instance
    """
    # Create config from dict if provided
    processor_config = None
    if config:
        processor_config = BatchProcessingConfig(**{
            k: v for k, v in config.items() 
            if k in BatchProcessingConfig.__dataclass_fields__
        })
    
    # Create processor
    processor = BatchProcessor(
        db_session=db_session,
        redis_client=redis_client,
        config=processor_config
    )
    
    # Initialize
    await processor.initialize()
    
    return processor
