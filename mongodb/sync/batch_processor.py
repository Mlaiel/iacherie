"""MongoDB Batch Processor
=======================

Optimized batch data processing system for MongoDB synchronization
in the Ainflue platform enterprise infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple, Iterator
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import threading
from queue import Queue
import time

try:
    import pymongo
    from pymongo import MongoClient, InsertOne, UpdateOne, DeleteOne, ReplaceOne
    from pymongo.errors import BulkWriteError
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

from . import SyncEvent

logger = logging.getLogger(__name__)

class BatchOperation(Enum):
    """Batch operation types."""
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    REPLACE = "replace"
    UPSERT = "upsert"

class BatchStatus(Enum):
    """Batch processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

@dataclass
class BatchItem:
    """Individual item in a batch."""
    operation: BatchOperation
    collection: str
    document: Dict[str, Any]
    filter_criteria: Optional[Dict[str, Any]] = None
    update_document: Optional[Dict[str, Any]] = None

@dataclass
class BatchJob:
    """Batch processing job."""
    batch_id: str
    items: List[BatchItem]
    status: BatchStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_items: int = 0
    processed_items: int = 0
    failed_items: int = 0
    error_message: Optional[str] = None

class BatchProcessor:
    """Enterprise-grade MongoDB batch processing system."""
    
    def __init__(self, connection_string -> None: str, database_name -> None: str) -> None:
        """Initialize batch processor."""
        if not MONGODB_AVAILABLE:
            raise ImportError("PyMongo is required for batch processing")
            
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.database = None
        
        # Batch configuration
        self.max_batch_size = 1000
        self.batch_timeout_seconds = 30
        self.max_concurrent_batches = 5
        self.retry_attempts = 3
        self.retry_delay_seconds = 2
        
        # Processing queues and state
        self.batch_queue = Queue(maxsize=1000)
        self.active_batches: Dict[str, BatchJob] = {}
        self.batch_history: List[BatchJob] = []
        self.max_history_size = 1000
        
        # Worker threads
        self.worker_threads = []
        self.running = False
        self.shutdown_event = threading.Event()
        
        # Statistics
        self.stats = {
            'total_batches': 0,
            'successful_batches': 0,
            'failed_batches': 0,
            'total_items_processed': 0,
            'total_processing_time_ms': 0
        }
    
    def connect(self) -> bool:
        """Connect to MongoDB."""
        try:
            self.client = MongoClient(self.connection_string)
            self.database = self.client[self.database_name]
            
            # Test connection
            self.client.admin.command("isMaster")
            logger.info("Batch processor connected to MongoDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def start_processing(self, num_workers -> None: int = None) -> None:
        """Start batch processing workers."""
        if self.running:
            logger.warning("Batch processor already running")
            return
        
        if not self.client and not self.connect():
            raise RuntimeError("Failed to connect to MongoDB")
        
        if num_workers is None:
            num_workers = min(self.max_concurrent_batches, 3)
        
        self.running = True
        
        # Start worker threads
        for i in range(num_workers):
            worker_thread = threading.Thread(
                target=self._worker_loop,
                args=(f"batch_worker_{i}",),
                daemon=True
            )
            worker_thread.start()
            self.worker_threads.append(worker_thread)
        
        logger.info(f"Started {num_workers} batch processing workers")
    
    def _worker_loop(self, worker_name -> None: str) -> None:
        """Main worker loop for processing batches."""
        logger.info(f"Batch worker started: {worker_name}")
        
        while self.running and not self.shutdown_event.is_set():
            try:
                # Get batch from queue
                batch_job = self.batch_queue.get(timeout=1)
                
                # Process the batch
                self._process_batch(batch_job, worker_name)
                
                # Mark task as done
                self.batch_queue.task_done()
                
            except:
                # Timeout or shutdown
                continue
        
        logger.info(f"Batch worker stopped: {worker_name}")
    
    def create_batch_from_events(self, events: List[SyncEvent]) -> str:
        """Create a batch job from sync events."""
        batch_items = []
        
        for event in events:
            # Convert sync event to batch item
            batch_item = self._sync_event_to_batch_item(event)
            if batch_item:
                batch_items.append(batch_item)
        
        return self.create_batch(batch_items)
    
    def _sync_event_to_batch_item(self, event: SyncEvent) -> Optional[BatchItem]:
        """Convert sync event to batch item."""
        try:
            operation_map = {
                'insert': BatchOperation.INSERT,
                'update': BatchOperation.UPDATE,
                'delete': BatchOperation.DELETE,
                'replace': BatchOperation.REPLACE
            }
            
            operation = operation_map.get(event.operation_type)
            if not operation:
                logger.warning(f"Unknown operation type: {event.operation_type}")
                return None
            
            # Extract document data
            document = event.data.get('document', {})
            filter_criteria = None
            update_document = None
            
            if operation == BatchOperation.UPDATE:
                # For updates, separate filter and update document
                filter_criteria = {'_id': event.document_id}
                update_description = event.data.get('updateDescription', {})
                update_document = {
                    '$set': update_description.get('updatedFields', {}),
                    '$unset': {field: "" for field in update_description.get('removedFields', [])}
                }
                # Remove empty operations
                update_document = {k: v for k, v in update_document.items() if v}
            
            elif operation == BatchOperation.DELETE:
                filter_criteria = {'_id': event.document_id}
                document = {}  # No document needed for delete
            
            return BatchItem(
                operation=operation,
                collection=event.collection.split('.')[-1],  # Extract collection name
                document=document,
                filter_criteria=filter_criteria,
                update_document=update_document
            )
            
        except Exception as e:
            logger.error(f"Failed to convert sync event to batch item: {e}")
            return None
    
    def create_batch(self, items: List[BatchItem]) -> str:
        """Create a new batch job."""
        batch_id = self._generate_batch_id()
        
        batch_job = BatchJob(
            batch_id=batch_id,
            items=items,
            status=BatchStatus.PENDING,
            created_at=datetime.now(),
            total_items=len(items)
        )
        
        # Queue for processing
        try:
            self.batch_queue.put(batch_job, timeout=1)
            self.active_batches[batch_id] = batch_job
            self.stats['total_batches'] += 1
            
            logger.info(f"Created batch job: {batch_id} with {len(items)} items")
            return batch_id
            
        except:
            logger.error(f"Failed to queue batch job: {batch_id}")
            raise RuntimeError("Batch queue is full")
    
    def _generate_batch_id(self) -> str:
        """Generate unique batch ID."""
        timestamp = int(time.time() * 1000)
        return f"batch_{timestamp}"
    
    def _process_batch(self, batch_job -> None: BatchJob, worker_name -> None: str) -> None:
        """Process a batch job."""
        batch_job.status = BatchStatus.PROCESSING
        batch_job.started_at = datetime.now()
        
        logger.info(f"Processing batch {batch_job.batch_id} with {batch_job.total_items} items ({worker_name})")
        
        start_time = time.time()
        
        try:
            # Group items by collection for efficient processing
            collections_items = self._group_items_by_collection(batch_job.items)
            
            total_processed = 0
            total_failed = 0
            
            # Process each collection
            for collection_name, items in collections_items.items():
                processed, failed = self._process_collection_batch(collection_name, items)
                total_processed += processed
                total_failed += failed
            
            # Update batch status
            batch_job.processed_items = total_processed
            batch_job.failed_items = total_failed
            
            if total_failed == 0:
                batch_job.status = BatchStatus.COMPLETED
                self.stats['successful_batches'] += 1
            elif total_processed > 0:
                batch_job.status = BatchStatus.PARTIAL
                self.stats['successful_batches'] += 1
            else:
                batch_job.status = BatchStatus.FAILED
                self.stats['failed_batches'] += 1
            
            batch_job.completed_at = datetime.now()
            
            # Update statistics
            processing_time = (time.time() - start_time) * 1000
            self.stats['total_items_processed'] += total_processed
            self.stats['total_processing_time_ms'] += processing_time
            
            logger.info(f"Batch {batch_job.batch_id} completed: {total_processed}/{batch_job.total_items} processed, {total_failed} failed")
            
        except Exception as e:
            batch_job.status = BatchStatus.FAILED
            batch_job.error_message = str(e)
            batch_job.completed_at = datetime.now()
            self.stats['failed_batches'] += 1
            
            logger.error(f"Batch {batch_job.batch_id} failed: {e}")
        
        # Move to history and clean up
        self._finalize_batch(batch_job)
    
    def _group_items_by_collection(self, items: List[BatchItem]) -> Dict[str, List[BatchItem]]:
        """Group batch items by collection."""
        collections = {}
        
        for item in items:
            if item.collection not in collections:
                collections[item.collection] = []
            collections[item.collection].append(item)
        
        return collections
    
    def _process_collection_batch(self, collection_name: str, items: List[BatchItem]) -> Tuple[int, int]:
        """Process batch items for a specific collection."""
        collection = self.database[collection_name]
        
        # Group operations by type for bulk processing
        operations = {
            BatchOperation.INSERT: [],
            BatchOperation.UPDATE: [],
            BatchOperation.DELETE: [],
            BatchOperation.REPLACE: [],
            BatchOperation.UPSERT: []
        }
        
        for item in items:
            operations[item.operation].append(item)
        
        total_processed = 0
        total_failed = 0
        
        # Process each operation type
        for operation_type, operation_items in operations.items():
            if not operation_items:
                continue
            
            processed, failed = self._execute_bulk_operation(
                collection, operation_type, operation_items
            )
            total_processed += processed
            total_failed += failed
        
        return total_processed, total_failed
    
    def _execute_bulk_operation(self, 
                               collection, 
                               operation_type: BatchOperation, 
                               items: List[BatchItem]) -> Tuple[int, int]:
        """Execute bulk operation for a specific operation type."""
        if not items:
            return 0, 0
        
        try:
            bulk_operations = []
            
            # Convert items to pymongo bulk operations
            for item in items:
                if operation_type == BatchOperation.INSERT:
                    bulk_operations.append(InsertOne(item.document))
                
                elif operation_type == BatchOperation.UPDATE:
                    bulk_operations.append(UpdateOne(
                        item.filter_criteria or {'_id': item.document.get('_id')},
                        item.update_document or {'$set': item.document}
                    ))
                
                elif operation_type == BatchOperation.DELETE:
                    bulk_operations.append(DeleteOne(
                        item.filter_criteria or {'_id': item.document.get('_id')}
                    ))
                
                elif operation_type == BatchOperation.REPLACE:
                    bulk_operations.append(ReplaceOne(
                        item.filter_criteria or {'_id': item.document.get('_id')},
                        item.document
                    ))
                
                elif operation_type == BatchOperation.UPSERT:
                    bulk_operations.append(UpdateOne(
                        item.filter_criteria or {'_id': item.document.get('_id')},
                        {'$set': item.document},
                        upsert=True
                    ))
            
            if not bulk_operations:
                return 0, 0
            
            # Execute bulk operation
            result = collection.bulk_write(bulk_operations, ordered=False)
            
            # Calculate results
            processed_count = (
                result.inserted_count +
                result.modified_count +
                result.deleted_count +
                result.upserted_count
            )
            
            logger.debug(f"Bulk {operation_type.value}: {processed_count}/{len(items)} processed")
            return processed_count, len(items) - processed_count
            
        except BulkWriteError as e:
            # Handle partial success in bulk operations
            processed_count = (
                e.details.get('nInserted', 0) +
                e.details.get('nModified', 0) +
                e.details.get('nRemoved', 0) +
                e.details.get('nUpserted', 0)
            )
            failed_count = len(items) - processed_count
            
            logger.warning(f"Bulk {operation_type.value} partially failed: {failed_count} errors")
            return processed_count, failed_count
            
        except Exception as e:
            logger.error(f"Bulk {operation_type.value} failed: {e}")
            return 0, len(items)
    
    def _finalize_batch(self, batch_job -> None: BatchJob) -> None:
        """Finalize batch job processing."""
        # Remove from active batches
        if batch_job.batch_id in self.active_batches:
            del self.active_batches[batch_job.batch_id]
        
        # Add to history
        self.batch_history.append(batch_job)
        
        # Limit history size
        if len(self.batch_history) > self.max_history_size:
            self.batch_history = self.batch_history[-self.max_history_size:]
    
    def get_batch_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific batch."""
        # Check active batches
        if batch_id in self.active_batches:
            batch = self.active_batches[batch_id]
            return self._batch_to_dict(batch)
        
        # Check history
        for batch in self.batch_history:
            if batch.batch_id == batch_id:
                return self._batch_to_dict(batch)
        
        return None
    
    def _batch_to_dict(self, batch: BatchJob) -> Dict[str, Any]:
        """Convert batch job to dictionary."""
        return {
            'batch_id': batch.batch_id,
            'status': batch.status.value,
            'created_at': batch.created_at,
            'started_at': batch.started_at,
            'completed_at': batch.completed_at,
            'total_items': batch.total_items,
            'processed_items': batch.processed_items,
            'failed_items': batch.failed_items,
            'error_message': batch.error_message,
            'processing_time_ms': (
                (batch.completed_at - batch.started_at).total_seconds() * 1000
                if batch.started_at and batch.completed_at else None
            )
        }
    
    def get_active_batches(self) -> List[Dict[str, Any]]:
        """Get list of active batch jobs."""
        return [self._batch_to_dict(batch) for batch in self.active_batches.values()]
    
    def get_batch_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get batch processing history."""
        # Sort by creation time (newest first) and limit
        sorted_batches = sorted(self.batch_history, key=lambda b: b.created_at, reverse=True)
        return [self._batch_to_dict(batch) for batch in sorted_batches[:limit]]
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get batch processing statistics."""
        # Calculate averages
        avg_processing_time = 0
        avg_items_per_batch = 0
        
        if self.stats['successful_batches'] > 0:
            avg_processing_time = self.stats['total_processing_time_ms'] / self.stats['successful_batches']
            avg_items_per_batch = self.stats['total_items_processed'] / self.stats['successful_batches']
        
        # Calculate success rate
        total_completed = self.stats['successful_batches'] + self.stats['failed_batches']
        success_rate = (self.stats['successful_batches'] / total_completed * 100) if total_completed > 0 else 0
        
        return {
            'total_batches': self.stats['total_batches'],
            'successful_batches': self.stats['successful_batches'],
            'failed_batches': self.stats['failed_batches'],
            'success_rate_percent': round(success_rate, 2),
            'total_items_processed': self.stats['total_items_processed'],
            'average_processing_time_ms': round(avg_processing_time, 2),
            'average_items_per_batch': round(avg_items_per_batch, 2),
            'active_batches_count': len(self.active_batches),
            'queue_size': self.batch_queue.qsize(),
            'worker_threads': len(self.worker_threads)
        }
    
    def cancel_batch(self, batch_id: str) -> bool:
        """Cancel a pending batch job."""
        if batch_id in self.active_batches:
            batch = self.active_batches[batch_id]
            
            if batch.status == BatchStatus.PENDING:
                batch.status = BatchStatus.FAILED
                batch.error_message = "Cancelled by user"
                batch.completed_at = datetime.now()
                
                self._finalize_batch(batch)
                logger.info(f"Cancelled batch: {batch_id}")
                return True
        
        return False
    
    def retry_failed_batch(self, batch_id: str) -> bool:
        """Retry a failed batch job."""
        # Find the batch in history
        for batch in self.batch_history:
            if batch.batch_id == batch_id and batch.status == BatchStatus.FAILED:
                # Create new batch with same items
                new_batch_id = self.create_batch(batch.items)
                logger.info(f"Retrying failed batch {batch_id} as {new_batch_id}")
                return True
        
        return False
    
    def stop_processing(self) -> None:
        """Stop batch processing."""
        if not self.running:
            return
        
        logger.info("Stopping batch processor")
        self.running = False
        self.shutdown_event.set()
        
        # Wait for workers to finish current jobs
        for thread in self.worker_threads:
            thread.join(timeout=10)
        
        # Close database connection
        if self.client:
            self.client.close()
        
        logger.info("Batch processor stopped")

# Export the main class
__all__ = ['BatchProcessor', 'BatchItem', 'BatchJob', 'BatchOperation', 'BatchStatus']