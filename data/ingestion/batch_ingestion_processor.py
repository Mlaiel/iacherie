"""
Batch Ingestion Processor
========================

Professional batch processing system for high-volume content ingestion.
Provides scalable, fault-tolerant batch processing with progress tracking,
resume capabilities, and comprehensive monitoring for IA Influencer Agent platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

  INTELLECTUAL PROPERTY WARNING 
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, BinaryIO, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import uuid
import hashlib
import pickle
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
import aiofiles
from celery import Celery, group, chord
from celery.result import AsyncResult

from .content_ingestion_manager import ContentIngestionManager, IngestionRequest, IngestionResult
from .multi_format_processor import MultiFormatProcessor, ProcessingOptions
from .metadata_extractor import MetadataExtractor
from ...core.exceptions import BatchProcessingError, ValidationError
from ...core.monitoring import MetricsCollector
from ...core.config import get_settings


class BatchStatus(Enum):
    """Batch processing status"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL_SUCCESS = "partial_success"


class BatchPriority(Enum):
    """Batch processing priority levels"""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


class ProcessingMode(Enum):
    """Batch processing execution modes"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    DISTRIBUTED = "distributed"
    ADAPTIVE = "adaptive"


@dataclass
class BatchItem:
    """Individual item in a batch"""
    item_id: str
    file_data: Union[bytes, BinaryIO, str]  # Can be data or file path
    filename: str
    content_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    retry_count: int = 0
    max_retries: int = 3
    status: str = "pending"
    error_message: str = ""
    processing_start_time: Optional[datetime] = None
    processing_end_time: Optional[datetime] = None
    result: Optional[IngestionResult] = None


@dataclass
class BatchConfiguration:
    """Batch processing configuration"""
    batch_id: str
    name: str
    description: str
    user_id: str
    processing_mode: ProcessingMode = ProcessingMode.PARALLEL
    priority: BatchPriority = BatchPriority.NORMAL
    max_concurrent_items: int = 10
    chunk_size: int = 100
    timeout_per_item: int = 300  # 5 minutes
    timeout_total: int = 3600    # 1 hour
    enable_resume: bool = True
    enable_preprocessing: bool = True
    enable_postprocessing: bool = True
    processing_options: Optional[ProcessingOptions] = None
    notification_webhooks: List[str] = field(default_factory=list)
    custom_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchProgress:
    """Batch processing progress tracking"""
    batch_id: str
    total_items: int
    processed_items: int = 0
    successful_items: int = 0
    failed_items: int = 0
    skipped_items: int = 0
    current_chunk: int = 0
    total_chunks: int = 0
    start_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    throughput_items_per_second: float = 0.0
    average_processing_time: float = 0.0
    error_rate: float = 0.0
    current_status: BatchStatus = BatchStatus.PENDING


@dataclass
class BatchResult:
    """Comprehensive batch processing result"""
    batch_id: str
    status: BatchStatus
    progress: BatchProgress
    items: List[BatchItem]
    summary: Dict[str, Any]
    metrics: Dict[str, Any]
    processing_log: List[Dict[str, Any]]
    created_at: datetime
    completed_at: Optional[datetime] = None
    total_processing_time: float = 0.0


class BatchIngestionProcessor:
    """
    Professional batch ingestion processor for IA Influencer Agent platform.
    
    Provides enterprise-grade batch processing capabilities including:
    - Scalable parallel and distributed processing
    - Fault tolerance with automatic retry mechanisms
    - Progress tracking and real-time monitoring
    - Resume/pause functionality for long-running batches
    - Comprehensive error handling and logging
    - Performance optimization and adaptive scaling
    - Integration with Celery for distributed processing
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis,
                 content_manager: ContentIngestionManager, 
                 multi_processor: MultiFormatProcessor,
                 metadata_extractor: MetadataExtractor,
                 celery_app: Optional[Celery] = None):
        """
        Initialize BatchIngestionProcessor.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching and queuing
            content_manager: Content ingestion manager
            multi_processor: Multi-format processor
            metadata_extractor: Metadata extractor
            celery_app: Celery app for distributed processing
        """
        self.db_session = db_session
        self.redis = redis_client
        self.content_manager = content_manager
        self.multi_processor = multi_processor
        self.metadata_extractor = metadata_extractor
        self.celery = celery_app
        self.logger = logging.getLogger(__name__)
        
        # Initialize metrics collector
        self.metrics = MetricsCollector()
        
        # Processing configuration
        self.settings = get_settings()
        self.max_workers = min(32, mp.cpu_count() + 4)
        self.default_timeout = 300  # 5 minutes per item
        self.checkpoint_interval = 10  # Save progress every 10 items
        
        # Processing pools
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=min(8, mp.cpu_count()))
        
        # Batch storage keys
        self.batch_key_prefix = "batch_ingestion"
        self.progress_key_prefix = "batch_progress"
        self.checkpoint_key_prefix = "batch_checkpoint"
        
        # Active batches tracking
        self.active_batches: Dict[str, BatchConfiguration] = {}
        self.batch_futures: Dict[str, Any] = {}
        
    async def create_batch(self, items: List[BatchItem], 
                          config: BatchConfiguration) -> str:
        """
        Create a new batch for processing.
        
        Args:
            items: List of items to process
            config: Batch configuration
            
        Returns:
            Batch ID for tracking
        """



        try:
            batch_id = config.batch_id or str(uuid.uuid4())
            config.batch_id = batch_id
            
            self.logger.info(f"Creating batch: {batch_id} with {len(items)} items")
            
            # Validate batch items
            await self._validate_batch_items(items)
            
            # Initialize batch progress
            progress = BatchProgress(
                batch_id=batch_id,
                total_items=len(items),
                total_chunks=max(1, len(items) // config.chunk_size + 
                               (1 if len(items) % config.chunk_size else 0)),
                start_time=datetime.utcnow()
            )
            
            # Create batch result structure
            batch_result = BatchResult(
                batch_id=batch_id,
                status=BatchStatus.PENDING,
                progress=progress,
                items=items,
                summary={},
                metrics={},
                processing_log=[],
                created_at=datetime.utcnow()
            )
            
            # Store batch data in Redis
            await self._store_batch_data(batch_id, config, batch_result)
            
            # Store in active batches
            self.active_batches[batch_id] = config
            
            # Log batch creation
            await self._log_batch_event(batch_id, "batch_created", {
                "total_items": len(items),
                "processing_mode": config.processing_mode.value,
                "priority": config.priority.value
            })
            
            self.logger.info(f"Batch created successfully: {batch_id}")
            return batch_id
            
        except Exception as e:
            self.logger.error(f"Batch creation failed: {str(e)}")
            raise BatchProcessingError(f"Failed to create batch: {str(e)}")
    
    async def start_batch_processing(self, batch_id: str) -> bool:
        """
        Start processing a batch.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Success status
        """



        try:
            self.logger.info(f"Starting batch processing: {batch_id}")
            
            # Get batch configuration and data
            config = await self._get_batch_config(batch_id)
            batch_result = await self._get_batch_result(batch_id)
            
            if not config or not batch_result:
                raise BatchProcessingError(f"Batch not found: {batch_id}")
            
            # Update status to processing
            batch_result.status = BatchStatus.PROCESSING
            batch_result.progress.start_time = datetime.utcnow()
            
            await self._store_batch_result(batch_id, batch_result)
            
            # Select processing strategy based on mode
            if config.processing_mode == ProcessingMode.SEQUENTIAL:
                future = asyncio.create_task(self._process_sequential(batch_id, config, batch_result))
            elif config.processing_mode == ProcessingMode.PARALLEL:
                future = asyncio.create_task(self._process_parallel(batch_id, config, batch_result))
            elif config.processing_mode == ProcessingMode.DISTRIBUTED:
                future = asyncio.create_task(self._process_distributed(batch_id, config, batch_result))
            elif config.processing_mode == ProcessingMode.ADAPTIVE:
                future = asyncio.create_task(self._process_adaptive(batch_id, config, batch_result))
            else:
                raise BatchProcessingError(f"Unsupported processing mode: {config.processing_mode}")
            
            # Store future for tracking
            self.batch_futures[batch_id] = future
            
            # Log processing start
            await self._log_batch_event(batch_id, "processing_started", {
                "processing_mode": config.processing_mode.value,
                "start_time": datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start batch processing: {batch_id} - {str(e)}")
            await self._update_batch_status(batch_id, BatchStatus.FAILED)
            return False
    
    async def pause_batch(self, batch_id: str) -> bool:
        """
        Pause batch processing.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Success status
        """



        try:
            self.logger.info(f"Pausing batch: {batch_id}")
            
            # Update status
            await self._update_batch_status(batch_id, BatchStatus.PAUSED)
            
            # Cancel future if exists
            if batch_id in self.batch_futures:
                future = self.batch_futures[batch_id]
                if not future.done():
                    future.cancel()
            
            # Save checkpoint
            await self._save_batch_checkpoint(batch_id)
            
            await self._log_batch_event(batch_id, "batch_paused", {})
            
            self.logger.info(f"Batch paused successfully: {batch_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to pause batch: {batch_id} - {str(e)}")
            return False
    
    async def resume_batch(self, batch_id: str) -> bool:
        """
        Resume paused batch processing.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Success status
        """



        try:
            self.logger.info(f"Resuming batch: {batch_id}")
            
            # Check if batch is paused
            batch_result = await self._get_batch_result(batch_id)
            if not batch_result or batch_result.status != BatchStatus.PAUSED:
                raise BatchProcessingError(f"Batch {batch_id} is not in paused state")
            
            # Load checkpoint if available
            checkpoint = await self._load_batch_checkpoint(batch_id)
            if checkpoint:
                # Restore progress from checkpoint
                batch_result.progress = checkpoint.get('progress', batch_result.progress)
                batch_result.items = checkpoint.get('items', batch_result.items)
                await self._store_batch_result(batch_id, batch_result)
            
            # Restart processing
            success = await self.start_batch_processing(batch_id)
            
            if success:
                await self._log_batch_event(batch_id, "batch_resumed", {})
                self.logger.info(f"Batch resumed successfully: {batch_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to resume batch: {batch_id} - {str(e)}")
            return False
    
    async def cancel_batch(self, batch_id: str) -> bool:
        """
        Cancel batch processing.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Success status
        """



        try:
            self.logger.info(f"Cancelling batch: {batch_id}")
            
            # Update status
            await self._update_batch_status(batch_id, BatchStatus.CANCELLED)
            
            # Cancel future if exists
            if batch_id in self.batch_futures:
                future = self.batch_futures[batch_id]
                if not future.done():
                    future.cancel()
                del self.batch_futures[batch_id]
            
            # Remove from active batches
            if batch_id in self.active_batches:
                del self.active_batches[batch_id]
            
            # Cleanup resources
            await self._cleanup_batch_resources(batch_id)
            
            await self._log_batch_event(batch_id, "batch_cancelled", {})
            
            self.logger.info(f"Batch cancelled successfully: {batch_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cancel batch: {batch_id} - {str(e)}")
            return False
    
    async def get_batch_status(self, batch_id: str) -> Optional[BatchResult]:
        """
        Get current batch status and progress.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Batch result with current status
        """



        try:
            return await self._get_batch_result(batch_id)
            
        except Exception as e:
            self.logger.error(f"Failed to get batch status: {batch_id} - {str(e)}")
            return None
    
    async def get_batch_metrics(self, batch_id: str) -> Dict[str, Any]:
        """
        Get detailed batch processing metrics.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Comprehensive metrics dictionary
        """



        try:
            batch_result = await self._get_batch_result(batch_id)
            if not batch_result:
                return {}
            
            # Calculate current metrics
            progress = batch_result.progress
            now = datetime.utcnow()
            
            elapsed_time = 0
            if progress.start_time:
                elapsed_time = (now - progress.start_time).total_seconds()
            
            # Throughput calculation
            throughput = 0
            if elapsed_time > 0:
                throughput = progress.processed_items / elapsed_time
            
            # Error rate calculation
            error_rate = 0
            if progress.processed_items > 0:
                error_rate = (progress.failed_items / progress.processed_items) * 100
            
            # Estimated completion
            estimated_completion = None
            if throughput > 0 and progress.processed_items < progress.total_items:
                remaining_items = progress.total_items - progress.processed_items
                remaining_seconds = remaining_items / throughput
                estimated_completion = now + timedelta(seconds=remaining_seconds)
            
            metrics = {
                'batch_id': batch_id,
                'status': batch_result.status.value,
                'progress': {
                    'total_items': progress.total_items,
                    'processed_items': progress.processed_items,
                    'successful_items': progress.successful_items,
                    'failed_items': progress.failed_items,
                    'skipped_items': progress.skipped_items,
                    'completion_percentage': (progress.processed_items / progress.total_items) * 100 if progress.total_items > 0 else 0
                },
                'performance': {
                    'elapsed_time_seconds': elapsed_time,
                    'throughput_items_per_second': throughput,
                    'average_processing_time_seconds': progress.average_processing_time,
                    'estimated_completion': estimated_completion.isoformat() if estimated_completion else None
                },
                'quality': {
                    'error_rate_percentage': error_rate,
                    'success_rate_percentage': 100 - error_rate
                },
                'resource_usage': await self._get_resource_metrics(batch_id)
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get batch metrics: {batch_id} - {str(e)}")
            return {}
    
    async def list_active_batches(self) -> List[Dict[str, Any]]:
        """
        List all active batches with their current status.
        
        Returns:
            List of active batch summaries
        """



        try:
            active_batches = []
            
            for batch_id in self.active_batches.keys():
                batch_result = await self._get_batch_result(batch_id)
                if batch_result:
                    summary = {
                        'batch_id': batch_id,
                        'status': batch_result.status.value,
                        'total_items': batch_result.progress.total_items,
                        'processed_items': batch_result.progress.processed_items,
                        'created_at': batch_result.created_at.isoformat(),
                        'completion_percentage': (
                            batch_result.progress.processed_items / 
                            batch_result.progress.total_items * 100
                        ) if batch_result.progress.total_items > 0 else 0
                    }
                    active_batches.append(summary)
            
            return active_batches
            
        except Exception as e:
            self.logger.error(f"Failed to list active batches: {str(e)}")
            return []
    
    async def cleanup_completed_batches(self, older_than_hours: int = 24) -> int:
        """
        Cleanup completed batches older than specified time.
        
        Args:
            older_than_hours: Remove batches completed more than this many hours ago
            
        Returns:
            Number of batches cleaned up
        """



        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
            cleaned_count = 0
            
            # Get all batch keys
            batch_keys = await self.redis.keys(f"{self.batch_key_prefix}:*")
            
            for batch_key in batch_keys:
                batch_id = batch_key.split(':')[-1]
                batch_result = await self._get_batch_result(batch_id)
                
                if (batch_result and 
                    batch_result.status in [BatchStatus.COMPLETED, BatchStatus.FAILED, BatchStatus.CANCELLED] and
                    batch_result.completed_at and 
                    batch_result.completed_at < cutoff_time):
                    
                    await self._cleanup_batch_resources(batch_id)
                    cleaned_count += 1
                    
            self.logger.info(f"Cleaned up {cleaned_count} completed batches")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Batch cleanup failed: {str(e)}")
            return 0
    
    # Processing implementation methods
    
    async def _process_sequential(self, batch_id: str, config: BatchConfiguration, 
                                batch_result: BatchResult):
        """Process batch items sequentially"""



        try:
            self.logger.info(f"Starting sequential processing: {batch_id}")
            
            for i, item in enumerate(batch_result.items):
                if batch_result.status == BatchStatus.CANCELLED:
                    break
                
                # Process single item
                await self._process_single_item(batch_id, item, config)
                
                # Update progress
                batch_result.progress.processed_items = i + 1
                await self._update_progress(batch_id, batch_result.progress)
                
                # Save checkpoint periodically
                if (i + 1) % self.checkpoint_interval == 0:
                    await self._save_batch_checkpoint(batch_id)
            
            await self._finalize_batch(batch_id, batch_result)
            
        except Exception as e:
            self.logger.error(f"Sequential processing failed: {batch_id} - {str(e)}")
            await self._handle_batch_error(batch_id, str(e))
    
    async def _process_parallel(self, batch_id: str, config: BatchConfiguration, 
                              batch_result: BatchResult):
        """Process batch items in parallel"""



        try:
            self.logger.info(f"Starting parallel processing: {batch_id}")
            
            # Process items in chunks
            chunk_size = config.chunk_size
            items = batch_result.items
            
            for chunk_idx in range(0, len(items), chunk_size):
                if batch_result.status == BatchStatus.CANCELLED:
                    break
                
                chunk = items[chunk_idx:chunk_idx + chunk_size]
                
                # Process chunk in parallel
                semaphore = asyncio.Semaphore(config.max_concurrent_items)
                
                async def process_with_semaphore(item):
                    async with semaphore:
                        return await self._process_single_item(batch_id, item, config)
                
                # Execute chunk tasks
                chunk_tasks = [process_with_semaphore(item) for item in chunk]
                await asyncio.gather(*chunk_tasks, return_exceptions=True)
                
                # Update progress
                batch_result.progress.processed_items = min(
                    chunk_idx + chunk_size, len(items)
                )
                batch_result.progress.current_chunk = chunk_idx // chunk_size + 1
                
                await self._update_progress(batch_id, batch_result.progress)
                await self._save_batch_checkpoint(batch_id)
            
            await self._finalize_batch(batch_id, batch_result)
            
        except Exception as e:
            self.logger.error(f"Parallel processing failed: {batch_id} - {str(e)}")
            await self._handle_batch_error(batch_id, str(e))
    
    async def _process_distributed(self, batch_id: str, config: BatchConfiguration, 
                                 batch_result: BatchResult):
        """Process batch items using Celery distributed processing"""



        try:
            if not self.celery:
                raise BatchProcessingError("Celery not configured for distributed processing")
            
            self.logger.info(f"Starting distributed processing: {batch_id}")
            
            # Create Celery group for batch processing
            chunk_size = config.chunk_size
            items = batch_result.items
            
            # Split items into chunks for distribution
            chunks = [
                items[i:i + chunk_size] 
                for i in range(0, len(items), chunk_size)
            ]
            
            # Create Celery task group
            job_group = group(
                self._process_chunk_task.s(batch_id, chunk_idx, chunk, config.dict())
                for chunk_idx, chunk in enumerate(chunks)
            )
            
            # Execute distributed processing
            group_result = job_group.apply_async()
            
            # Monitor progress
            await self._monitor_distributed_processing(batch_id, group_result, batch_result)
            
        except Exception as e:
            self.logger.error(f"Distributed processing failed: {batch_id} - {str(e)}")
            await self._handle_batch_error(batch_id, str(e))
    
    async def _process_adaptive(self, batch_id: str, config: BatchConfiguration, 
                              batch_result: BatchResult):
        """Process batch with adaptive strategy based on performance"""



        try:
            self.logger.info(f"Starting adaptive processing: {batch_id}")
            
            # Start with parallel processing
            total_items = len(batch_result.items)
            
            # Determine optimal strategy based on batch characteristics
            if total_items < 50:
                # Small batch - use sequential
                await self._process_sequential(batch_id, config, batch_result)
            elif total_items < 500:
                # Medium batch - use parallel
                await self._process_parallel(batch_id, config, batch_result)
            else:
                # Large batch - use distributed if available, otherwise parallel
                if self.celery:
                    await self._process_distributed(batch_id, config, batch_result)
                else:
                    await self._process_parallel(batch_id, config, batch_result)
            
        except Exception as e:
            self.logger.error(f"Adaptive processing failed: {batch_id} - {str(e)}")
            await self._handle_batch_error(batch_id, str(e))
    
    async def _process_single_item(self, batch_id: str, item: BatchItem, 
                                 config: BatchConfiguration) -> bool:
        """Process a single batch item"""



        try:
            item.processing_start_time = datetime.utcnow()
            item.status = "processing"
            
            # Create ingestion request
            ingestion_request = IngestionRequest(
                user_id=config.user_id,
                file_data=item.file_data,
                filename=item.filename,
                content_type=item.content_type,
                title=item.metadata.get('title', item.filename),
                description=item.metadata.get('description', ''),
                tags=item.metadata.get('tags', []),
                metadata=item.metadata,
                protection_enabled=item.metadata.get('protection_enabled', True),
                monetization_enabled=item.metadata.get('monetization_enabled', False),
                visibility=item.metadata.get('visibility', 'private'),
                upload_ip='127.0.0.1',  # Batch processing
                upload_user_agent='BatchProcessor/1.0'
            )
            
            # Process with timeout
            try:
                result = await asyncio.wait_for(
                    self.content_manager.ingest_content(ingestion_request),
                    timeout=config.timeout_per_item
                )
                
                item.result = result
                item.status = "completed" if result.success else "failed"
                
                if not result.success:
                    item.error_message = "; ".join(result.errors)
                
            except asyncio.TimeoutError:
                item.status = "failed"
                item.error_message = "Processing timeout"
                return False
            
            item.processing_end_time = datetime.utcnow()
            
            # Update metrics
            await self._update_item_metrics(batch_id, item)
            
            return item.status == "completed"
            
        except Exception as e:
            item.status = "failed"
            item.error_message = str(e)
            item.processing_end_time = datetime.utcnow()
            
            self.logger.error(f"Item processing failed: {item.item_id} - {str(e)}")
            return False
    
    # Helper methods
    
    async def _validate_batch_items(self, items: List[BatchItem]):
        """Validate batch items before processing"""
        if not items:
            raise ValidationError("Batch cannot be empty")
        
        if len(items) > 10000:  # Arbitrary limit
            raise ValidationError("Batch too large (max 10,000 items)")
        
        # Validate individual items
        for item in items:
            if not item.filename:
                raise ValidationError(f"Item {item.item_id} missing filename")
            if not item.file_data:
                raise ValidationError(f"Item {item.item_id} missing file data")
    
    async def _store_batch_data(self, batch_id: str, config: BatchConfiguration, 
                              batch_result: BatchResult):
        """Store batch configuration and initial result"""



        try:
            # Store configuration
            config_key = f"{self.batch_key_prefix}:config:{batch_id}"
            await self.redis.setex(
                config_key, 
                86400 * 7,  # 7 days
                pickle.dumps(config)
            )
            
            # Store batch result
            await self._store_batch_result(batch_id, batch_result)
            
        except Exception as e:
            self.logger.error(f"Failed to store batch data: {batch_id} - {str(e)}")
            raise
    
    async def _store_batch_result(self, batch_id: str, batch_result: BatchResult):
        """Store batch result in Redis"""



        try:
            result_key = f"{self.batch_key_prefix}:result:{batch_id}"
            await self.redis.setex(
                result_key,
                86400 * 7,  # 7 days
                pickle.dumps(batch_result)
            )
        except Exception as e:
            self.logger.error(f"Failed to store batch result: {batch_id} - {str(e)}")
            raise
    
    async def _get_batch_config(self, batch_id: str) -> Optional[BatchConfiguration]:
        """Get batch configuration from Redis"""



        try:
            config_key = f"{self.batch_key_prefix}:config:{batch_id}"
            config_data = await self.redis.get(config_key)
            
            if config_data:
                return pickle.loads(config_data)
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get batch config: {batch_id} - {str(e)}")
            return None
    
    async def _get_batch_result(self, batch_id: str) -> Optional[BatchResult]:
        """Get batch result from Redis"""



        try:
            result_key = f"{self.batch_key_prefix}:result:{batch_id}"
            result_data = await self.redis.get(result_key)
            
            if result_data:
                return pickle.loads(result_data)
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get batch result: {batch_id} - {str(e)}")
            return None
    
    async def _update_batch_status(self, batch_id: str, status: BatchStatus):
        """Update batch status"""



        try:
            batch_result = await self._get_batch_result(batch_id)
            if batch_result:
                batch_result.status = status
                if status in [BatchStatus.COMPLETED, BatchStatus.FAILED, BatchStatus.CANCELLED]:
                    batch_result.completed_at = datetime.utcnow()
                await self._store_batch_result(batch_id, batch_result)
        except Exception as e:
            self.logger.error(f"Failed to update batch status: {batch_id} - {str(e)}")
    
    async def _update_progress(self, batch_id: str, progress: BatchProgress):
        """Update batch progress"""



        try:
            # Calculate metrics
            if progress.processed_items > 0:
                successful = sum(1 for item in await self._get_batch_items(batch_id) 
                               if item.status == "completed")
                failed = sum(1 for item in await self._get_batch_items(batch_id) 
                           if item.status == "failed")
                
                progress.successful_items = successful
                progress.failed_items = failed
                progress.error_rate = (failed / progress.processed_items) * 100
            
            # Store updated progress
            progress_key = f"{self.progress_key_prefix}:{batch_id}"
            await self.redis.setex(
                progress_key,
                86400,  # 24 hours
                pickle.dumps(progress)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to update progress: {batch_id} - {str(e)}")
    
    async def _get_batch_items(self, batch_id: str) -> List[BatchItem]:
        """Get batch items"""



        try:
            batch_result = await self._get_batch_result(batch_id)
            return batch_result.items if batch_result else []
        except Exception as e:
            self.logger.error(f"Failed to get batch items: {batch_id} - {str(e)}")
            return []
    
    async def _save_batch_checkpoint(self, batch_id: str):
        """Save batch processing checkpoint"""



        try:
            batch_result = await self._get_batch_result(batch_id)
            if batch_result:
                checkpoint_data = {
                    'progress': batch_result.progress,
                    'items': batch_result.items,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                checkpoint_key = f"{self.checkpoint_key_prefix}:{batch_id}"
                await self.redis.setex(
                    checkpoint_key,
                    86400 * 2,  # 48 hours
                    pickle.dumps(checkpoint_data)
                )
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint: {batch_id} - {str(e)}")
    
    async def _load_batch_checkpoint(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Load batch processing checkpoint"""



        try:
            checkpoint_key = f"{self.checkpoint_key_prefix}:{batch_id}"
            checkpoint_data = await self.redis.get(checkpoint_key)
            
            if checkpoint_data:
                return pickle.loads(checkpoint_data)
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to load checkpoint: {batch_id} - {str(e)}")
            return None
    
    async def _finalize_batch(self, batch_id: str, batch_result: BatchResult):
        """Finalize batch processing"""



        try:
            # Update final status
            successful_items = sum(1 for item in batch_result.items if item.status == "completed")
            failed_items = sum(1 for item in batch_result.items if item.status == "failed")
            
            if failed_items == 0:
                batch_result.status = BatchStatus.COMPLETED
            elif successful_items == 0:
                batch_result.status = BatchStatus.FAILED
            else:
                batch_result.status = BatchStatus.PARTIAL_SUCCESS
            
            batch_result.completed_at = datetime.utcnow()
            
            # Calculate final metrics
            if batch_result.progress.start_time:
                total_time = (batch_result.completed_at - batch_result.progress.start_time).total_seconds()
                batch_result.total_processing_time = total_time
            
            # Generate summary
            batch_result.summary = {
                'total_items': len(batch_result.items),
                'successful_items': successful_items,
                'failed_items': failed_items,
                'success_rate': (successful_items / len(batch_result.items)) * 100,
                'total_processing_time': batch_result.total_processing_time
            }
            
            await self._store_batch_result(batch_id, batch_result)
            
            # Log completion
            await self._log_batch_event(batch_id, "batch_completed", batch_result.summary)
            
            # Cleanup
            if batch_id in self.active_batches:
                del self.active_batches[batch_id]
            if batch_id in self.batch_futures:
                del self.batch_futures[batch_id]
            
            self.logger.info(f"Batch finalized: {batch_id} - {batch_result.status.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to finalize batch: {batch_id} - {str(e)}")
    
    async def _handle_batch_error(self, batch_id: str, error_message: str):
        """Handle batch processing error"""



        try:
            await self._update_batch_status(batch_id, BatchStatus.FAILED)
            
            await self._log_batch_event(batch_id, "batch_error", {
                'error_message': error_message,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Cleanup
            if batch_id in self.active_batches:
                del self.active_batches[batch_id]
            if batch_id in self.batch_futures:
                del self.batch_futures[batch_id]
                
        except Exception as e:
            self.logger.error(f"Error handling failed: {batch_id} - {str(e)}")
    
    async def _log_batch_event(self, batch_id: str, event_type: str, data: Dict[str, Any]):
        """Log batch processing event"""



        try:
            event_data = {
                'batch_id': batch_id,
                'event_type': event_type,
                'timestamp': datetime.utcnow().isoformat(),
                'data': data
            }
            
            log_key = f"batch_log:{batch_id}"
            await self.redis.lpush(log_key, json.dumps(event_data))
            await self.redis.expire(log_key, 86400 * 7)  # 7 days
            
        except Exception as e:
            self.logger.error(f"Failed to log batch event: {batch_id} - {str(e)}")
    
    async def _update_item_metrics(self, batch_id: str, item: BatchItem):
        """Update metrics for processed item"""



        try:
            # Update batch-level metrics
            metrics_key = f"batch_metrics:{batch_id}"
            
            # Increment counters
            await self.redis.hincrby(metrics_key, "processed_items", 1)
            
            if item.status == "completed":
                await self.redis.hincrby(metrics_key, "successful_items", 1)
            else:
                await self.redis.hincrby(metrics_key, "failed_items", 1)
            
            # Update processing time
            if item.processing_start_time and item.processing_end_time:
                processing_time = (item.processing_end_time - item.processing_start_time).total_seconds()
                await self.redis.hincrbyfloat(metrics_key, "total_processing_time", processing_time)
            
            await self.redis.expire(metrics_key, 86400 * 7)  # 7 days
            
        except Exception as e:
            self.logger.error(f"Failed to update item metrics: {batch_id} - {str(e)}")
    
    async def _get_resource_metrics(self, batch_id: str) -> Dict[str, Any]:
        """Get resource usage metrics for batch"""



        try:
            # This would integrate with system monitoring
            # For now, return basic metrics
            return {
                'cpu_usage_percent': 0.0,
                'memory_usage_mb': 0.0,
                'disk_io_mb': 0.0,
                'network_io_mb': 0.0
            }
        except Exception as e:
            self.logger.error(f"Failed to get resource metrics: {batch_id} - {str(e)}")
            return {}
    
    async def _cleanup_batch_resources(self, batch_id: str):
        """Cleanup batch-related resources"""



        try:
            # Remove batch data from Redis
            keys_to_delete = [
                f"{self.batch_key_prefix}:config:{batch_id}",
                f"{self.batch_key_prefix}:result:{batch_id}",
                f"{self.progress_key_prefix}:{batch_id}",
                f"{self.checkpoint_key_prefix}:{batch_id}",
                f"batch_metrics:{batch_id}",
                f"batch_log:{batch_id}"
            ]
            
            for key in keys_to_delete:
                await self.redis.delete(key)
            
            self.logger.info(f"Batch resources cleaned up: {batch_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup batch resources: {batch_id} - {str(e)}")
    
    def __del__(self):
        """Cleanup on destructor"""



        try:
            if hasattr(self, 'thread_pool'):
                self.thread_pool.shutdown(wait=False)
            if hasattr(self, 'process_pool'):
                self.process_pool.shutdown(wait=False)
        except Exception:
            pass
