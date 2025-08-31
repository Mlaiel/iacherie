"""Batch Processor Module

High-performance batch processing system for database operations with intelligent
chunking, parallel processing, and comprehensive error handling.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
import asyncio
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable, Awaitable, TypeVar, Generic
from enum import Enum
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.exc import IntegrityError, OperationalError

from ...core.logging import get_logger
from ...core.config import settings
from ...core.metrics import MetricsCollector

logger = get_logger(__name__)

T = TypeVar('T')


class BatchStrategy(Enum):
    """Batch processing strategies"""    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"
    BULK_INSERT = "bulk_insert"
    BULK_UPDATE = "bulk_update"
    BULK_DELETE = "bulk_delete"


class BatchStatus(Enum):
    """Batch processing status"""    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIALLY_COMPLETED = "partially_completed"


class ErrorHandling(Enum):
    """Error handling strategies"""    FAIL_FAST = "fail_fast"
    CONTINUE_ON_ERROR = "continue_on_error"
    RETRY_FAILED = "retry_failed"
    SKIP_FAILED = "skip_failed"


@dataclass
class BatchConfig:
    """Batch processing configuration"""    batch_size: int = 1000
    max_workers: int = 4
    strategy: BatchStrategy = BatchStrategy.ADAPTIVE
    error_handling: ErrorHandling = ErrorHandling.CONTINUE_ON_ERROR
    
    # Performance settings
    connection_pool_size: int = 10
    chunk_size_adaptive: bool = True
    min_chunk_size: int = 100
    max_chunk_size: int = 10000
    
    # Retry settings
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    exponential_backoff: bool = True
    
    # Timeout settings
    operation_timeout_seconds: float = 300.0
    batch_timeout_seconds: float = 3600.0
    
    # Progress reporting
    progress_callback_interval: int = 100
    enable_progress_logging: bool = True
    
    # Memory management
    memory_limit_mb: int = 1024
    gc_frequency: int = 10  # Every N batches


@dataclass
class BatchMetrics:
    """Batch processing metrics"""    batch_id: str
    total_items: int = 0
    processed_items: int = 0
    successful_items: int = 0
    failed_items: int = 0
    skipped_items: int = 0
    
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    total_batches: int = 0
    completed_batches: int = 0
    failed_batches: int = 0
    
    avg_batch_time: float = 0.0
    total_processing_time: float = 0.0
    throughput_items_per_sec: float = 0.0
    
    memory_usage_mb: float = 0.0
    peak_memory_mb: float = 0.0
    
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""        if self.total_items == 0:
            return 0.0
        return (self.processed_items / self.total_items) * 100
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""        if self.processed_items == 0:
            return 0.0
        return (self.successful_items / self.processed_items) * 100
    
    @property
    def estimated_completion_time(self) -> Optional[datetime]:
        """Estimate completion time based on current progress"""        if self.processed_items == 0 or self.throughput_items_per_sec == 0:
            return None
        
        remaining_items = self.total_items - self.processed_items
        remaining_seconds = remaining_items / self.throughput_items_per_sec
        return datetime.now() + timedelta(seconds=remaining_seconds)


@dataclass
class BatchResult:
    """Batch processing result"""    batch_id: str
    status: BatchStatus
    metrics: BatchMetrics
    successful_items: List[Any] = field(default_factory=list)
    failed_items: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def is_successful(self) -> bool:
        """Check if batch was successful"""        return self.status == BatchStatus.COMPLETED and self.metrics.failed_items == 0
    
    @property
    def has_partial_success(self) -> bool:
        """Check if batch had partial success"""        return (self.status == BatchStatus.PARTIALLY_COMPLETED or 
                (self.status == BatchStatus.COMPLETED and self.metrics.failed_items > 0))


class BatchChunkCalculator:
    """Adaptive batch chunk size calculator"""    
    def __init__(self, config: BatchConfig):
        self.config = config
        self._performance_history: List[Dict[str, float]] = []
        self._current_chunk_size = config.batch_size
    
    def calculate_optimal_chunk_size(self, total_items: int, available_memory_mb: float) -> int:
        """Calculate optimal chunk size based on data and system state"""        if not self.config.chunk_size_adaptive:
            return self.config.batch_size
        
        # Memory-based calculation
        memory_based_size = self._calculate_memory_based_size(available_memory_mb)
        
        # Performance-based calculation
        performance_based_size = self._calculate_performance_based_size()
        
        # Data-based calculation
        data_based_size = self._calculate_data_based_size(total_items)
        
        # Take the minimum to be conservative
        optimal_size = min(memory_based_size, performance_based_size, data_based_size)
        
        # Ensure within bounds
        optimal_size = max(self.config.min_chunk_size, 
                          min(optimal_size, self.config.max_chunk_size))
        
        self._current_chunk_size = optimal_size
        return optimal_size
    
    def _calculate_memory_based_size(self, available_memory_mb: float) -> int:
        """Calculate chunk size based on available memory"""        # Conservative estimate: use 50% of available memory
        usable_memory_mb = available_memory_mb * 0.5
        
        # Estimate 1KB per item (very rough estimate)
        estimated_items = int((usable_memory_mb * 1024) / 1)  # 1KB per item
        
        return max(self.config.min_chunk_size, estimated_items)
    
    def _calculate_performance_based_size(self) -> int:
        """Calculate chunk size based on performance history"""        if len(self._performance_history) < 3:
            return self.config.batch_size
        
        # Find the chunk size with best throughput
        best_throughput = 0
        best_chunk_size = self.config.batch_size
        
        for perf in self._performance_history[-10:]:  # Last 10 measurements
            if perf['throughput'] > best_throughput:
                best_throughput = perf['throughput']
                best_chunk_size = int(perf['chunk_size'])
        
        return best_chunk_size
    
    def _calculate_data_based_size(self, total_items: int) -> int:
        """Calculate chunk size based on total data volume"""        if total_items < 1000:
            return min(total_items, self.config.batch_size)
        elif total_items < 10000:
            return self.config.batch_size
        else:
            # For large datasets, use larger chunks for efficiency
            return min(total_items // 100, self.config.max_chunk_size)
    
    def record_performance(self, chunk_size: int, processing_time: float, items_processed: int) -> None:
        """Record performance metrics for adaptive sizing"""        if processing_time > 0:
            throughput = items_processed / processing_time
            
            self._performance_history.append({
                'chunk_size': chunk_size,
                'processing_time': processing_time,
                'items_processed': items_processed,
                'throughput': throughput,
                'timestamp': time.time()
            })
            
            # Keep only recent history
            if len(self._performance_history) > 50:
                self._performance_history = self._performance_history[-25:]


class BatchProcessor(Generic[T]):
    """High-performance batch processor for database operations"""    
    def __init__(self, config: BatchConfig):
        self.config = config
        self.metrics_collector = MetricsCollector()
        self.chunk_calculator = BatchChunkCalculator(config)
        
        # Processing state
        self._active_batches: Dict[str, BatchMetrics] = {}
        self._cancelled_batches: set = set()
        
        # Progress callbacks
        self._progress_callbacks: List[Callable[[BatchMetrics], Awaitable[None]]] = []
        
        # Thread pool for parallel processing
        self._thread_pool: Optional[ThreadPoolExecutor] = None
    
    async def process_batch(
        self,
        items: List[T],
        processor_func: Callable[[List[T]], Awaitable[List[Any]]],
        batch_id: Optional[str] = None,
        progress_callback: Optional[Callable[[BatchMetrics], Awaitable[None]]] = None
    ) -> BatchResult:
        """Process a batch of items with the specified processor function"""        
        batch_id = batch_id or f"batch_{int(time.time() * 1000)}"
        
        # Initialize metrics
        metrics = BatchMetrics(
            batch_id=batch_id,
            total_items=len(items)
        )
        self._active_batches[batch_id] = metrics
        
        try:
            logger.info(f"Starting batch processing: {batch_id} ({len(items)} items)")
            
            # Calculate optimal chunk size
            chunk_size = self.chunk_calculator.calculate_optimal_chunk_size(
                len(items), 
                self._get_available_memory_mb()
            )
            
            # Split items into chunks
            chunks = self._create_chunks(items, chunk_size)
            metrics.total_batches = len(chunks)
            
            # Process based on strategy
            if self.config.strategy == BatchStrategy.SEQUENTIAL:
                result = await self._process_sequential(chunks, processor_func, metrics, progress_callback)
            elif self.config.strategy == BatchStrategy.PARALLEL:
                result = await self._process_parallel(chunks, processor_func, metrics, progress_callback)
            else:  # ADAPTIVE
                result = await self._process_adaptive(chunks, processor_func, metrics, progress_callback)
            
            # Finalize metrics
            metrics.end_time = datetime.now()
            metrics.total_processing_time = (metrics.end_time - metrics.start_time).total_seconds()
            
            if metrics.total_processing_time > 0:
                metrics.throughput_items_per_sec = metrics.processed_items / metrics.total_processing_time
            
            # Determine final status
            if batch_id in self._cancelled_batches:
                result.status = BatchStatus.CANCELLED
            elif metrics.failed_items == 0:
                result.status = BatchStatus.COMPLETED
            elif metrics.successful_items > 0:
                result.status = BatchStatus.PARTIALLY_COMPLETED
            else:
                result.status = BatchStatus.FAILED
            
            logger.info(f"Batch processing completed: {batch_id} - {result.status.value}")
            
            # Send final metrics
            await self._send_batch_metrics(metrics, result.status)
            
            return result
            
        except Exception as e:
            logger.error(f"Batch processing failed: {batch_id} - {e}")
            metrics.errors.append({
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'type': 'batch_failure'
            })
            
            return BatchResult(
                batch_id=batch_id,
                status=BatchStatus.FAILED,
                metrics=metrics,
                warnings=[f"Batch processing failed: {e}"]
            )
        
        finally:
            # Cleanup
            if batch_id in self._active_batches:
                del self._active_batches[batch_id]
            
            self._cancelled_batches.discard(batch_id)
    
    async def _process_sequential(
        self,
        chunks: List[List[T]],
        processor_func: Callable[[List[T]], Awaitable[List[Any]]],
        metrics: BatchMetrics,
        progress_callback: Optional[Callable[[BatchMetrics], Awaitable[None]]]
    ) -> BatchResult:
        """Process chunks sequentially"""        
        result = BatchResult(
            batch_id=metrics.batch_id,
            status=BatchStatus.RUNNING,
            metrics=metrics
        )
        
        for i, chunk in enumerate(chunks):
            if metrics.batch_id in self._cancelled_batches:
                break
            
            try:
                chunk_start_time = time.time()
                
                # Process chunk
                chunk_results = await self._process_chunk_with_retry(chunk, processor_func)
                
                # Update metrics
                chunk_processing_time = time.time() - chunk_start_time
                self._update_metrics(metrics, chunk, chunk_results, chunk_processing_time)
                
                # Record performance for adaptive sizing
                self.chunk_calculator.record_performance(
                    len(chunk), chunk_processing_time, len(chunk_results['successful'])
                )
                
                # Update result
                result.successful_items.extend(chunk_results['successful'])
                result.failed_items.extend(chunk_results['failed'])
                
                # Progress callback
                if progress_callback and (i + 1) % self.config.progress_callback_interval == 0:
                    await progress_callback(metrics)
                
                # Memory management
                if (i + 1) % self.config.gc_frequency == 0:
                    import gc
                    gc.collect()
                
            except Exception as e:
                logger.error(f"Chunk processing failed: {e}")
                metrics.failed_batches += 1
                metrics.errors.append({
                    'error': str(e),
                    'chunk_index': i,
                    'timestamp': datetime.now().isoformat()
                })
                
                if self.config.error_handling == ErrorHandling.FAIL_FAST:
                    raise
        
        return result
    
    async def _process_parallel(
        self,
        chunks: List[List[T]],
        processor_func: Callable[[List[T]], Awaitable[List[Any]]],
        metrics: BatchMetrics,
        progress_callback: Optional[Callable[[BatchMetrics], Awaitable[None]]]
    ) -> BatchResult:
        """Process chunks in parallel"""        
        result = BatchResult(
            batch_id=metrics.batch_id,
            status=BatchStatus.RUNNING,
            metrics=metrics
        )
        
        # Create semaphore to limit concurrent operations
        semaphore = asyncio.Semaphore(self.config.max_workers)
        
        async def process_chunk_with_semaphore(chunk_index: int, chunk: List[T]) -> Dict[str, Any]:
            async with semaphore:
                try:
                    chunk_start_time = time.time()
                    chunk_results = await self._process_chunk_with_retry(chunk, processor_func)
                    chunk_processing_time = time.time() - chunk_start_time
                    
                    return {
                        'index': chunk_index,
                        'results': chunk_results,
                        'processing_time': chunk_processing_time,
                        'success': True
                    }
                except Exception as e:
                    return {
                        'index': chunk_index,
                        'error': str(e),
                        'success': False
                    }
        
        # Process all chunks concurrently
        tasks = [
            process_chunk_with_semaphore(i, chunk)
            for i, chunk in enumerate(chunks)
        ]
        
        completed_count = 0
        async for task in asyncio.as_completed(tasks):
            if metrics.batch_id in self._cancelled_batches:
                # Cancel remaining tasks
                for remaining_task in tasks:
                    if not remaining_task.done():
                        remaining_task.cancel()
                break
            
            try:
                chunk_result = await task
                
                if chunk_result['success']:
                    chunk_index = chunk_result['index']
                    chunk = chunks[chunk_index]
                    chunk_results = chunk_result['results']
                    chunk_processing_time = chunk_result['processing_time']
                    
                    # Update metrics
                    self._update_metrics(metrics, chunk, chunk_results, chunk_processing_time)
                    
                    # Record performance
                    self.chunk_calculator.record_performance(
                        len(chunk), chunk_processing_time, len(chunk_results['successful'])
                    )
                    
                    # Update result
                    result.successful_items.extend(chunk_results['successful'])
                    result.failed_items.extend(chunk_results['failed'])
                else:
                    metrics.failed_batches += 1
                    metrics.errors.append({
                        'error': chunk_result['error'],
                        'chunk_index': chunk_result['index'],
                        'timestamp': datetime.now().isoformat()
                    })
                
                completed_count += 1
                
                # Progress callback
                if progress_callback and completed_count % self.config.progress_callback_interval == 0:
                    await progress_callback(metrics)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Parallel chunk processing error: {e}")
                metrics.failed_batches += 1
        
        return result
    
    async def _process_adaptive(
        self,
        chunks: List[List[T]],
        processor_func: Callable[[List[T]], Awaitable[List[Any]]],
        metrics: BatchMetrics,
        progress_callback: Optional[Callable[[BatchMetrics], Awaitable[None]]]
    ) -> BatchResult:
        """Process chunks with adaptive strategy (parallel with fallback to sequential)"""        
        # Start with parallel processing
        try:
            # Monitor system resources
            cpu_percent = self._get_cpu_usage()
            memory_usage = self._get_memory_usage_mb()
            
            # Switch to sequential if system is under stress
            if cpu_percent > 80 or memory_usage > self.config.memory_limit_mb:
                logger.info(f"High resource usage detected (CPU: {cpu_percent}%, Memory: {memory_usage}MB), switching to sequential processing")
                return await self._process_sequential(chunks, processor_func, metrics, progress_callback)
            else:
                return await self._process_parallel(chunks, processor_func, metrics, progress_callback)
                
        except Exception as e:
            logger.warning(f"Parallel processing failed, falling back to sequential: {e}")
            return await self._process_sequential(chunks, processor_func, metrics, progress_callback)
    
    async def _process_chunk_with_retry(
        self,
        chunk: List[T],
        processor_func: Callable[[List[T]], Awaitable[List[Any]]]
    ) -> Dict[str, List[Any]]:
        """Process a single chunk with retry logic"""        
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                # Apply timeout
                results = await asyncio.wait_for(
                    processor_func(chunk),
                    timeout=self.config.operation_timeout_seconds
                )
                
                # Assume processor returns a list of results
                # In case of partial failure, implement proper error handling
                return {
                    'successful': results if results else [],
                    'failed': []
                }
                
            except asyncio.TimeoutError as e:
                last_exception = e
                logger.warning(f"Chunk processing timeout (attempt {attempt + 1})")
                
                if attempt < self.config.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    await asyncio.sleep(delay)
                
            except (IntegrityError, OperationalError) as e:
                last_exception = e
                logger.warning(f"Database error in chunk processing (attempt {attempt + 1}): {e}")
                
                if attempt < self.config.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    await asyncio.sleep(delay)
                
            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error in chunk processing: {e}")
                
                if self.config.error_handling == ErrorHandling.FAIL_FAST:
                    raise
                break
        
        # All retries failed
        if self.config.error_handling == ErrorHandling.CONTINUE_ON_ERROR:
            return {
                'successful': [],
                'failed': [{'item': item, 'error': str(last_exception)} for item in chunk]
            }
        else:
            raise last_exception
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay with optional exponential backoff"""        base_delay = self.config.retry_delay_seconds
        
        if self.config.exponential_backoff:
            return base_delay * (2 ** attempt)
        else:
            return base_delay
    
    def _create_chunks(self, items: List[T], chunk_size: int) -> List[List[T]]:
        """Split items into chunks of specified size"""        chunks = []
        for i in range(0, len(items), chunk_size):
            chunks.append(items[i:i + chunk_size])
        return chunks
    
    def _update_metrics(
        self,
        metrics: BatchMetrics,
        chunk: List[T],
        chunk_results: Dict[str, List[Any]],
        processing_time: float
    ) -> None:
        """Update batch metrics with chunk results"""        
        successful_count = len(chunk_results['successful'])
        failed_count = len(chunk_results['failed'])
        
        metrics.processed_items += len(chunk)
        metrics.successful_items += successful_count
        metrics.failed_items += failed_count
        metrics.completed_batches += 1
        
        # Update average batch time
        if metrics.completed_batches == 1:
            metrics.avg_batch_time = processing_time
        else:
            metrics.avg_batch_time = (
                (metrics.avg_batch_time * (metrics.completed_batches - 1) + processing_time)
                / metrics.completed_batches
            )
        
        # Update throughput
        elapsed_time = (datetime.now() - metrics.start_time).total_seconds()
        if elapsed_time > 0:
            metrics.throughput_items_per_sec = metrics.processed_items / elapsed_time
        
        # Update memory usage
        current_memory = self._get_memory_usage_mb()
        metrics.memory_usage_mb = current_memory
        metrics.peak_memory_mb = max(metrics.peak_memory_mb, current_memory)
    
    def _get_available_memory_mb(self) -> float:
        """Get available system memory in MB"""        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.available / (1024 ** 2)
        except ImportError:
            return 1024.0  # Default fallback
    
    def _get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB"""        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 ** 2)
        except ImportError:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0
    
    async def _send_batch_metrics(self, metrics: BatchMetrics, status: BatchStatus) -> None:
        """Send batch metrics to monitoring system"""        try:
            self.metrics_collector.counter(
                "batch_processing_total",
                1,
                {"status": status.value, "strategy": self.config.strategy.value}
            )
            
            self.metrics_collector.histogram(
                "batch_processing_duration_seconds",
                metrics.total_processing_time
            )
            
            self.metrics_collector.histogram(
                "batch_processing_throughput_items_per_sec",
                metrics.throughput_items_per_sec
            )
            
            self.metrics_collector.gauge(
                "batch_processing_success_rate",
                metrics.success_rate
            )
            
        except Exception as e:
            logger.warning(f"Failed to send batch metrics: {e}")
    
    def cancel_batch(self, batch_id: str) -> bool:
        """Cancel a running batch"""        if batch_id in self._active_batches:
            self._cancelled_batches.add(batch_id)
            logger.info(f"Batch cancellation requested: {batch_id}")
            return True
        return False
    
    def get_batch_status(self, batch_id: str) -> Optional[BatchMetrics]:
        """Get current status of a batch"""        return self._active_batches.get(batch_id)
    
    def add_progress_callback(self, callback: Callable[[BatchMetrics], Awaitable[None]]) -> None:
        """Add a progress callback function"""        self._progress_callbacks.append(callback)
    
    async def cleanup(self) -> None:
        """Cleanup resources"""        if self._thread_pool:
            self._thread_pool.shutdown(wait=True)
            self._thread_pool = None


# Specialized batch processors for common database operations
class DatabaseBatchProcessor:
    """Specialized batch processor for database operations"""    
    def __init__(self, engine: AsyncEngine, config: BatchConfig):
        self.engine = engine
        self.config = config
        self.processor = BatchProcessor[Dict[str, Any]](config)
    
    async def bulk_insert(
        self,
        table_name: str,
        records: List[Dict[str, Any]],
        batch_id: Optional[str] = None
    ) -> BatchResult:
        """Perform bulk insert operation"""        
        async def insert_processor(chunk: List[Dict[str, Any]]) -> List[Any]:
            async with self.engine.begin() as conn:
                # Generate INSERT statement
                if chunk:
                    columns = list(chunk[0].keys())
                    placeholders = ', '.join([f':{col}' for col in columns])
                    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                    
                    # Execute batch insert
                    await conn.execute(text(insert_sql), chunk)
                    return chunk
                return []
        
        return await self.processor.process_batch(
            records,
            insert_processor,
            batch_id or f"bulk_insert_{table_name}_{int(time.time())}"
        )
    
    async def bulk_update(
        self,
        table_name: str,
        records: List[Dict[str, Any]],
        key_columns: List[str],
        batch_id: Optional[str] = None
    ) -> BatchResult:
        """Perform bulk update operation"""        
        async def update_processor(chunk: List[Dict[str, Any]]) -> List[Any]:
            async with self.engine.begin() as conn:
                updated_records = []
                
                for record in chunk:
                    # Build WHERE clause
                    where_conditions = [f"{key} = :{key}" for key in key_columns]
                    where_clause = " AND ".join(where_conditions)
                    
                    # Build SET clause
                    update_columns = [col for col in record.keys() if col not in key_columns]
                    set_clause = ", ".join([f"{col} = :{col}" for col in update_columns])
                    
                    # Generate UPDATE statement
                    update_sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
                    
                    result = await conn.execute(text(update_sql), record)
                    if result.rowcount > 0:
                        updated_records.append(record)
                
                return updated_records
        
        return await self.processor.process_batch(
            records,
            update_processor,
            batch_id or f"bulk_update_{table_name}_{int(time.time())}"
        )
    
    async def bulk_delete(
        self,
        table_name: str,
        conditions: List[Dict[str, Any]],
        batch_id: Optional[str] = None
    ) -> BatchResult:
        """Perform bulk delete operation"""        
        async def delete_processor(chunk: List[Dict[str, Any]]) -> List[Any]:
            async with self.engine.begin() as conn:
                deleted_records = []
                
                for condition in chunk:
                    # Build WHERE clause
                    where_conditions = [f"{key} = :{key}" for key in condition.keys()]
                    where_clause = " AND ".join(where_conditions)
                    
                    # Generate DELETE statement
                    delete_sql = f"DELETE FROM {table_name} WHERE {where_clause}"
                    
                    result = await conn.execute(text(delete_sql), condition)
                    if result.rowcount > 0:
                        deleted_records.append(condition)
                
                return deleted_records
        
        return await self.processor.process_batch(
            conditions,
            delete_processor,
            batch_id or f"bulk_delete_{table_name}_{int(time.time())}"
        )

    async def process_content_fingerprints(
        self, 
        content_items: List[Dict[str, Any]], 
        batch_id: Optional[str] = None
    ) -> BatchResult:
        """Process content fingerprints in optimized batches for protection system"""        
        async def fingerprint_processor(chunk: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            async with self.engine.begin() as conn:
                processed_items = []
                
                for item in chunk:
                    try:
                        # Insert content fingerprint with vector data
                        insert_sql = """                        INSERT INTO content_fingerprints 
                        (user_id, content_type, original_filename, fingerprint_hash, 
                         vector_embedding, metadata, created_at)
                        VALUES (:user_id, :content_type, :original_filename, :fingerprint_hash,
                                :vector_embedding, :metadata, :created_at)
                        RETURNING id, fingerprint_hash
                        """                        
                        result = await conn.execute(text(insert_sql), {
                            'user_id': item['user_id'],
                            'content_type': item['content_type'],
                            'original_filename': item['original_filename'],
                            'fingerprint_hash': item['fingerprint_hash'],
                            'vector_embedding': item['vector_embedding'],
                            'metadata': item.get('metadata', {}),
                            'created_at': datetime.now()
                        })
                        
                        row = result.fetchone()
                        processed_items.append({
                            'id': row.id,
                            'fingerprint_hash': row.fingerprint_hash,
                            'original_item': item
                        })
                        
                    except Exception as e:
                        logger.error(f"Failed to process fingerprint for {item.get('original_filename')}: {e}")
                        continue
                
                return processed_items
        
        return await self.processor.process_batch(
            content_items,
            fingerprint_processor,
            batch_id or f"content_fingerprints_{int(time.time())}"
        )
    
    async def process_protection_alerts(
        self,
        alerts: List[Dict[str, Any]],
        batch_id: Optional[str] = None
    ) -> BatchResult:
        """Process protection alerts in optimized batches"""        
        async def alerts_processor(chunk: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            async with self.engine.begin() as conn:
                processed_alerts = []
                
                for alert in chunk:
                    try:
                        # Insert protection alert
                        insert_sql = """                        INSERT INTO protection_alerts 
                        (fingerprint_id, detected_url, platform, similarity_score, 
                         status, evidence_screenshot, created_at)
                        VALUES (:fingerprint_id, :detected_url, :platform, :similarity_score,
                                :status, :evidence_screenshot, :created_at)
                        RETURNING id, status
                        """                        
                        result = await conn.execute(text(insert_sql), {
                            'fingerprint_id': alert['fingerprint_id'],
                            'detected_url': alert['detected_url'],
                            'platform': alert['platform'],
                            'similarity_score': alert['similarity_score'],
                            'status': alert.get('status', 'pending'),
                            'evidence_screenshot': alert.get('evidence_screenshot'),
                            'created_at': datetime.now()
                        })
                        
                        row = result.fetchone()
                        processed_alerts.append({
                            'id': row.id,
                            'status': row.status,
                            'original_alert': alert
                        })
                        
                    except Exception as e:
                        logger.error(f"Failed to process alert for {alert.get('detected_url')}: {e}")
                        continue
                
                return processed_alerts
        
        return await self.processor.process_batch(
            alerts,
            alerts_processor,
            batch_id or f"protection_alerts_{int(time.time())}"
        )
    
    async def process_revenue_tracking(
        self,
        revenue_data: List[Dict[str, Any]],
        batch_id: Optional[str] = None
    ) -> BatchResult:
        """Process revenue tracking data in optimized batches for monetization system"""        
        async def revenue_processor(chunk: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            async with self.engine.begin() as conn:
                processed_revenue = []
                
                for revenue in chunk:
                    try:
                        # Insert or update revenue tracking
                        upsert_sql = """                        INSERT INTO revenue_tracking 
                        (user_id, content_id, platform, revenue_amount, currency, 
                         period_start, period_end, created_at)
                        VALUES (:user_id, :content_id, :platform, :revenue_amount, :currency,
                                :period_start, :period_end, :created_at)
                        ON CONFLICT (user_id, content_id, platform, period_start) 
                        DO UPDATE SET 
                            revenue_amount = EXCLUDED.revenue_amount,
                            updated_at = NOW()
                        RETURNING id, revenue_amount
                        """                        
                        result = await conn.execute(text(upsert_sql), {
                            'user_id': revenue['user_id'],
                            'content_id': revenue['content_id'],
                            'platform': revenue['platform'],
                            'revenue_amount': revenue['revenue_amount'],
                            'currency': revenue.get('currency', 'EUR'),
                            'period_start': revenue['period_start'],
                            'period_end': revenue['period_end'],
                            'created_at': datetime.now()
                        })
                        
                        row = result.fetchone()
                        processed_revenue.append({
                            'id': row.id,
                            'revenue_amount': row.revenue_amount,
                            'original_revenue': revenue
                        })
                        
                    except Exception as e:
                        logger.error(f"Failed to process revenue for user {revenue.get('user_id')}: {e}")
                        continue
                
                return processed_revenue
        
        return await self.processor.process_batch(
            revenue_data,
            revenue_processor,
            batch_id or f"revenue_tracking_{int(time.time())}"
        )
    
    async def process_multimedia_content(
        self,
        content_items: List[Dict[str, Any]],
        batch_id: Optional[str] = None
    ) -> BatchResult:
        """Process multimedia content uploads with optimized chunking for large files"""        
        async def multimedia_processor(chunk: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            async with self.engine.begin() as conn:
                processed_content = []
                
                for item in chunk:
                    try:
                        # Process different content types optimally
                        content_type = item['content_type']
                        
                        if content_type in ['audio', 'video']:
                            # Use larger chunk sizes for multimedia
                            self.config.chunk_size = min(self.config.chunk_size * 2, 100)
                        elif content_type == 'image':
                            # Moderate chunk sizes for images
                            self.config.chunk_size = min(self.config.chunk_size * 1.5, 75)
                        
                        # Insert content metadata
                        insert_sql = """                        INSERT INTO content_metadata 
                        (user_id, content_type, file_path, file_size, duration, 
                         format, quality, metadata, created_at)
                        VALUES (:user_id, :content_type, :file_path, :file_size, :duration,
                                :format, :quality, :metadata, :created_at)
                        RETURNING id, file_path
                        """                        
                        result = await conn.execute(text(insert_sql), {
                            'user_id': item['user_id'],
                            'content_type': content_type,
                            'file_path': item['file_path'],
                            'file_size': item.get('file_size', 0),
                            'duration': item.get('duration'),
                            'format': item.get('format'),
                            'quality': item.get('quality'),
                            'metadata': item.get('metadata', {}),
                            'created_at': datetime.now()
                        })
                        
                        row = result.fetchone()
                        processed_content.append({
                            'id': row.id,
                            'file_path': row.file_path,
                            'original_item': item
                        })
                        
                    except Exception as e:
                        logger.error(f"Failed to process content {item.get('file_path')}: {e}")
                        continue
                
                return processed_content
        
        return await self.processor.process_batch(
            content_items,
            multimedia_processor,
            batch_id or f"multimedia_content_{int(time.time())}"
        )
    
    async def process_vector_embeddings(
        self,
        embeddings: List[Dict[str, Any]],
        batch_id: Optional[str] = None
    ) -> BatchResult:
        """Process vector embeddings for AI similarity matching with FAISS optimization"""        
        async def embedding_processor(chunk: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            async with self.engine.begin() as conn:
                processed_embeddings = []
                
                # Use larger batch sizes for vector operations
                self.config.chunk_size = min(self.config.chunk_size * 3, 500)
                
                for embedding in chunk:
                    try:
                        # Insert vector embedding with FAISS indexing preparation
                        insert_sql = """                        INSERT INTO vector_embeddings 
                        (content_id, embedding_type, vector_data, dimension, 
                         model_version, created_at)
                        VALUES (:content_id, :embedding_type, :vector_data, :dimension,
                                :model_version, :created_at)
                        RETURNING id, content_id
                        """                        
                        result = await conn.execute(text(insert_sql), {
                            'content_id': embedding['content_id'],
                            'embedding_type': embedding['embedding_type'],
                            'vector_data': embedding['vector_data'],
                            'dimension': embedding['dimension'],
                            'model_version': embedding.get('model_version', '1.0'),
                            'created_at': datetime.now()
                        })
                        
                        row = result.fetchone()
                        processed_embeddings.append({
                            'id': row.id,
                            'content_id': row.content_id,
                            'original_embedding': embedding
                        })
                        
                    except Exception as e:
                        logger.error(f"Failed to process embedding for content {embedding.get('content_id')}: {e}")
                        continue
                
                return processed_embeddings
        
        return await self.processor.process_batch(
            embeddings,
            embedding_processor,
            batch_id or f"vector_embeddings_{int(time.time())}"
        )

    async def process_creator_analytics(
        self,
        analytics_data: List[Dict[str, Any]],
        batch_id: Optional[str] = None
    ) -> BatchResult:
        """Process creator analytics data for performance insights"""        
        async def analytics_processor(chunk: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            async with self.engine.begin() as conn:
                processed_analytics = []
                
                for analytics in chunk:
                    try:
                        # Insert analytics with aggregation optimization
                        upsert_sql = """                        INSERT INTO creator_analytics 
                        (user_id, platform, metric_type, metric_value, timestamp, 
                         aggregation_period, metadata)
                        VALUES (:user_id, :platform, :metric_type, :metric_value, :timestamp,
                                :aggregation_period, :metadata)
                        ON CONFLICT (user_id, platform, metric_type, aggregation_period) 
                        DO UPDATE SET 
                            metric_value = creator_analytics.metric_value + EXCLUDED.metric_value,
                            updated_at = NOW()
                        RETURNING id, metric_value
                        """                        
                        result = await conn.execute(text(upsert_sql), {
                            'user_id': analytics['user_id'],
                            'platform': analytics['platform'],
                            'metric_type': analytics['metric_type'],
                            'metric_value': analytics['metric_value'],
                            'timestamp': analytics.get('timestamp', datetime.now()),
                            'aggregation_period': analytics.get('aggregation_period', 'daily'),
                            'metadata': analytics.get('metadata', {})
                        })
                        
                        row = result.fetchone()
                        processed_analytics.append({
                            'id': row.id,
                            'metric_value': row.metric_value,
                            'original_analytics': analytics
                        })
                        
                    except Exception as e:
                        logger.error(f"Failed to process analytics for user {analytics.get('user_id')}: {e}")
                        continue
                
                return processed_analytics
        
        return await self.processor.process_batch(
            analytics_data,
            analytics_processor,
            batch_id or f"creator_analytics_{int(time.time())}"
        )
