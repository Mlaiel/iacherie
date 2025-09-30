"""Batch Processing Optimizer Module

Intelligent batch processing optimization for efficiency and throughput
in the Ainflue Message Queues Enterprise system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This Batch Processing Optimizer architecture and implementation are EXCLUSIVE PROPERTY
of Fahed Mlaiel. Unauthorized use, reproduction, or adaptation is STRICTLY PROHIBITED.
Legal consequences include substantial damages and criminal prosecution.

Authorization Contact: mlaiel@live.de
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4
from collections import defaultdict, deque
import statistics

from ..core.exceptions import MessageQueueError
from ..utils.monitoring import MetricsCollector
from ..security.encryption import EncryptionManager

logger = logging.getLogger(__name__)


class BatchStrategy(Enum):
    """Batch processing strategies"""
    SIZE_BASED = "size_based"
    TIME_BASED = "time_based"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"
    BUSINESS_LOGIC = "business_logic"


class ProcessingMode(Enum):
    """Processing modes for batches"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINE = "pipeline"
    MAP_REDUCE = "map_reduce"


class BatchStatus(Enum):
    """Batch processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL_SUCCESS = "partial_success"


@dataclass
class BatchConfiguration:
    """Batch processing configuration"""
    batch_id: str = field(default_factory=lambda: str(uuid4()))
    strategy: BatchStrategy = BatchStrategy.HYBRID
    processing_mode: ProcessingMode = ProcessingMode.PARALLEL
    
    # Size-based settings
    min_batch_size: int = 10
    max_batch_size: int = 100
    optimal_batch_size: int = 50
    
    # Time-based settings
    max_wait_time: float = 30.0  # seconds
    flush_interval: float = 60.0  # seconds
    
    # Processing settings
    max_parallel_workers: int = 10
    timeout_per_item: float = 30.0
    retry_failed_items: bool = True
    
    # Business logic settings
    business_grouping_key: Optional[str] = None
    priority_grouping: bool = True
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class BatchItem:
    """Individual item in a batch"""
    item_id: str = field(default_factory=lambda: str(uuid4()))
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    processing_time: Optional[float] = None
    error: Optional[str] = None
    success: bool = False
    business_context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ProcessingBatch:
    """A batch of items for processing"""
    batch_id: str = field(default_factory=lambda: str(uuid4()))
    items: List[BatchItem] = field(default_factory=list)
    configuration: BatchConfiguration = field(default_factory=BatchConfiguration)
    status: BatchStatus = BatchStatus.PENDING
    
    # Processing metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_duration: float = 0.0
    
    # Results
    successful_items: int = 0
    failed_items: int = 0
    error_details: List[str] = field(default_factory=list)
    
    # Performance metrics
    throughput: float = 0.0  # items per second
    efficiency_score: float = 0.0


@dataclass
class BatchMetrics:
    """Batch processing metrics"""
    total_batches: int = 0
    completed_batches: int = 0
    failed_batches: int = 0
    total_items_processed: int = 0
    avg_batch_size: float = 0.0
    avg_processing_time: float = 0.0
    avg_throughput: float = 0.0
    efficiency_scores: List[float] = field(default_factory=list)
    strategy_performance: Dict[str, float] = field(default_factory=dict)


class AinflueBusiness:
    """Ainflue Business Batch Processing Rules"""
    
    # Batch configurations by message type
    BATCH_CONFIGS = {
        # Content processing batches
        "content_upload": BatchConfiguration(
            strategy=BatchStrategy.BUSINESS_LOGIC,
            processing_mode=ProcessingMode.PARALLEL,
            min_batch_size=5,
            max_batch_size=20,
            optimal_batch_size=10,
            max_wait_time=60.0,
            max_parallel_workers=8,
            business_grouping_key="creator_id",
            priority_grouping=True
        ),
        
        # AI analysis batches
        "ai_content_analysis": BatchConfiguration(
            strategy=BatchStrategy.ADAPTIVE,
            processing_mode=ProcessingMode.PIPELINE,
            min_batch_size=3,
            max_batch_size=15,
            optimal_batch_size=8,
            max_wait_time=120.0,
            max_parallel_workers=4,
            timeout_per_item=180.0,
            business_grouping_key="content_type"
        ),
        
        # Collaboration matching batches
        "collaboration_match": BatchConfiguration(
            strategy=BatchStrategy.HYBRID,
            processing_mode=ProcessingMode.MAP_REDUCE,
            min_batch_size=10,
            max_batch_size=50,
            optimal_batch_size=25,
            max_wait_time=30.0,
            max_parallel_workers=6,
            business_grouping_key="criteria_type"
        ),
        
        # Revenue calculation batches
        "revenue_calculation": BatchConfiguration(
            strategy=BatchStrategy.TIME_BASED,
            processing_mode=ProcessingMode.SEQUENTIAL,
            min_batch_size=20,
            max_batch_size=200,
            optimal_batch_size=100,
            max_wait_time=300.0,  # 5 minutes
            max_parallel_workers=2,
            timeout_per_item=60.0,
            business_grouping_key="calculation_period"
        ),
        
        # Analytics processing batches
        "analytics_processing": BatchConfiguration(
            strategy=BatchStrategy.SIZE_BASED,
            processing_mode=ProcessingMode.PARALLEL,
            min_batch_size=50,
            max_batch_size=500,
            optimal_batch_size=200,
            max_wait_time=600.0,  # 10 minutes
            max_parallel_workers=12,
            business_grouping_key="analytics_type"
        ),
        
        # SEO optimization batches
        "seo_optimization": BatchConfiguration(
            strategy=BatchStrategy.BUSINESS_LOGIC,
            processing_mode=ProcessingMode.PIPELINE,
            min_batch_size=15,
            max_batch_size=75,
            optimal_batch_size=30,
            max_wait_time=180.0,
            max_parallel_workers=6,
            business_grouping_key="optimization_type"
        )
    }
    
    # Business grouping logic
    BUSINESS_GROUPING_FUNCTIONS = {
        "creator_id": lambda item: item.business_context.get("creator_id", "default"),
        "content_type": lambda item: item.payload.get("content_type", "unknown"),
        "criteria_type": lambda item: item.payload.get("criteria_type", "general"),
        "calculation_period": lambda item: item.business_context.get("period", "current"),
        "analytics_type": lambda item: item.payload.get("analytics_type", "basic"),
        "optimization_type": lambda item: item.payload.get("optimization_type", "standard"),
        "priority": lambda item: f"priority_{item.priority}",
        "creator_tier": lambda item: item.business_context.get("creator_tier", "standard")
    }
    
    # Performance thresholds
    PERFORMANCE_THRESHOLDS = {
        "min_efficiency_score": 0.7,
        "max_processing_time": 300.0,  # 5 minutes
        "min_throughput": 1.0,  # items per second
        "max_failure_rate": 0.1  # 10%
    }


class BatchProcessingOptimizer:
    """
    Intelligent batch processing optimization for efficiency and throughput
    Supports multiple strategies and adapts to workload patterns
    """
    
    def __init__(self,
                 metrics_collector: Optional[MetricsCollector] = None,
                 encryption_manager: Optional[EncryptionManager] = None):
        self.metrics = metrics_collector
        self.encryption = encryption_manager
        
        # Batch management
        self.pending_items = defaultdict(deque)  # message_type -> deque of items
        self.active_batches = {}  # batch_id -> ProcessingBatch
        self.completed_batches = {}  # batch_id -> ProcessingBatch
        self.batch_configurations = {}  # message_type -> BatchConfiguration
        
        # Performance tracking
        self.batch_metrics = BatchMetrics()
        self.performance_history = defaultdict(deque)  # message_type -> performance data
        
        # Adaptive optimization
        self.adaptation_enabled = True
        self.learning_window = 100  # Number of batches for learning
        
        # Batch timers
        self.batch_timers = {}  # message_type -> timer task
        
        # Processing functions
        self.processors = {}  # message_type -> processing function
        
        logger.info("Initialized Batch Processing Optimizer")
    
    async def register_processor(self, message_type: str, processor_func: Callable):
        """Register a processing function for a message type"""
        self.processors[message_type] = processor_func
        
        # Set default configuration if not exists
        if message_type not in self.batch_configurations:
            self.batch_configurations[message_type] = AinflueBusiness.BATCH_CONFIGS.get(
                message_type, BatchConfiguration()
            )
        
        logger.info(f"Registered processor for message type: {message_type}")
    
    async def add_item_to_batch(self, message_type: str, item: BatchItem) -> str:
        """Add item to batch for processing"""
        try:
            # Encrypt item if needed
            if self.encryption:
                item.payload = await self._encrypt_payload(item.payload)
            
            # Add to pending items
            self.pending_items[message_type].append(item)
            
            # Check if we should create a batch
            await self._check_batch_creation(message_type)
            
            logger.debug(f"Added item {item.item_id} to {message_type} batch queue")
            return item.item_id
            
        except Exception as e:
            logger.error(f"Error adding item to batch: {str(e)}")
            raise MessageQueueError(f"Failed to add item to batch: {str(e)}")
    
    async def create_batch_from_messages(self,
                                       message_type: str,
                                       payloads: List[Dict[str, Any]],
                                       business_contexts: Optional[List[Dict[str, Any]]] = None) -> str:
        """Create batch from list of message payloads"""
        try:
            # Create batch items
            items = []
            for i, payload in enumerate(payloads):
                context = business_contexts[i] if business_contexts and i < len(business_contexts) else {}
                
                item = BatchItem(
                    payload=payload,
                    business_context=context,
                    priority=context.get("priority", 5)
                )
                items.append(item)
            
            # Create batch configuration
            config = self._get_batch_configuration(message_type)
            config.optimal_batch_size = len(items)  # Override for custom batch
            
            # Create and process batch
            batch = ProcessingBatch(
                items=items,
                configuration=config
            )
            
            batch_id = await self._process_batch(message_type, batch)
            
            logger.info(f"Created and processed batch {batch_id} with {len(items)} items")
            return batch_id
            
        except Exception as e:
            logger.error(f"Error creating batch from messages: {str(e)}")
            raise MessageQueueError(f"Failed to create batch: {str(e)}")
    
    async def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Get status of a processing batch"""
        try:
            # Check active batches
            if batch_id in self.active_batches:
                batch = self.active_batches[batch_id]
                return self._batch_to_dict(batch, include_items=False)
            
            # Check completed batches
            if batch_id in self.completed_batches:
                batch = self.completed_batches[batch_id]
                return self._batch_to_dict(batch, include_items=False)
            
            return {"error": "Batch not found"}
            
        except Exception as e:
            logger.error(f"Error getting batch status: {str(e)}")
            return {"error": str(e)}
    
    async def get_batch_performance_metrics(self, message_type: Optional[str] = None) -> Dict[str, Any]:
        """Get batch processing performance metrics"""
        try:
            if message_type:
                # Metrics for specific message type
                config = self._get_batch_configuration(message_type)
                history = list(self.performance_history[message_type])
                
                if not history:
                    return {
                        "message_type": message_type,
                        "total_batches": 0,
                        "avg_processing_time": 0.0,
                        "avg_throughput": 0.0,
                        "avg_efficiency": 0.0
                    }
                
                return {
                    "message_type": message_type,
                    "total_batches": len(history),
                    "avg_processing_time": statistics.mean([h["processing_time"] for h in history]),
                    "avg_throughput": statistics.mean([h["throughput"] for h in history]),
                    "avg_efficiency": statistics.mean([h["efficiency_score"] for h in history]),
                    "current_configuration": {
                        "strategy": config.strategy.value,
                        "processing_mode": config.processing_mode.value,
                        "optimal_batch_size": config.optimal_batch_size,
                        "max_wait_time": config.max_wait_time
                    },
                    "pending_items": len(self.pending_items[message_type])
                }
            else:
                # Global metrics
                return {
                    "global_metrics": {
                        "total_batches": self.batch_metrics.total_batches,
                        "completed_batches": self.batch_metrics.completed_batches,
                        "failed_batches": self.batch_metrics.failed_batches,
                        "success_rate": (self.batch_metrics.completed_batches / 
                                       max(self.batch_metrics.total_batches, 1)) * 100,
                        "total_items_processed": self.batch_metrics.total_items_processed,
                        "avg_batch_size": self.batch_metrics.avg_batch_size,
                        "avg_processing_time": self.batch_metrics.avg_processing_time,
                        "avg_throughput": self.batch_metrics.avg_throughput
                    },
                    "by_message_type": {
                        msg_type: {
                            "pending_items": len(self.pending_items[msg_type]),
                            "configuration": self._get_batch_configuration(msg_type).strategy.value
                        }
                        for msg_type in self.pending_items.keys()
                    }
                }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            return {"error": str(e)}
    
    async def optimize_batch_configurations(self) -> Dict[str, Any]:
        """Optimize batch configurations based on performance history"""
        try:
            optimization_results = {}
            
            for message_type in self.performance_history.keys():
                result = await self._optimize_message_type_config(message_type)
                optimization_results[message_type] = result
            
            return {
                "optimization_results": optimization_results,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error optimizing configurations: {str(e)}")
            return {"error": str(e)}
    
    async def force_flush_batches(self, message_type: Optional[str] = None) -> List[str]:
        """Force flush pending batches"""
        try:
            flushed_batches = []
            
            if message_type:
                if self.pending_items[message_type]:
                    batch_id = await self._create_batch_from_pending(message_type, force=True)
                    if batch_id:
                        flushed_batches.append(batch_id)
            else:
                # Flush all message types
                for msg_type in list(self.pending_items.keys()):
                    if self.pending_items[msg_type]:
                        batch_id = await self._create_batch_from_pending(msg_type, force=True)
                        if batch_id:
                            flushed_batches.append(batch_id)
            
            logger.info(f"Force flushed {len(flushed_batches)} batches")
            return flushed_batches
            
        except Exception as e:
            logger.error(f"Error force flushing batches: {str(e)}")
            return []
    
    # Core batch processing logic
    
    async def _check_batch_creation(self, message_type: str):
        """Check if we should create a batch for the message type"""
        config = self._get_batch_configuration(message_type)
        pending_count = len(self.pending_items[message_type])
        
        should_create = False
        
        if config.strategy == BatchStrategy.SIZE_BASED:
            should_create = pending_count >= config.optimal_batch_size
        
        elif config.strategy == BatchStrategy.TIME_BASED:
            # Time-based batching handled by timers
            should_create = pending_count >= config.max_batch_size
        
        elif config.strategy == BatchStrategy.HYBRID:
            should_create = (pending_count >= config.optimal_batch_size or
                           pending_count >= config.max_batch_size)
        
        elif config.strategy == BatchStrategy.ADAPTIVE:
            # Use learned optimal size
            optimal_size = await self._get_adaptive_batch_size(message_type)
            should_create = pending_count >= optimal_size
        
        elif config.strategy == BatchStrategy.BUSINESS_LOGIC:
            should_create = await self._check_business_logic_batch_creation(message_type, config)
        
        if should_create:
            await self._create_batch_from_pending(message_type)
        
        # Start timer if not already running
        await self._ensure_batch_timer(message_type, config)
    
    async def _create_batch_from_pending(self, message_type: str, force: bool = False) -> Optional[str]:
        """Create a batch from pending items"""
        try:
            config = self._get_batch_configuration(message_type)
            pending_items = list(self.pending_items[message_type])
            
            if not pending_items and not force:
                return None
            
            if not force and len(pending_items) < config.min_batch_size:
                return None
            
            # Determine batch size
            batch_size = min(len(pending_items), config.max_batch_size)
            
            # Group items if business logic grouping is enabled
            if config.business_grouping_key:
                batches = await self._group_items_by_business_logic(pending_items, config)
                
                # Process each group as a separate batch
                batch_ids = []
                for group_items in batches:
                    if len(group_items) >= config.min_batch_size or force:
                        batch = ProcessingBatch(
                            items=group_items,
                            configuration=config
                        )
                        batch_id = await self._process_batch(message_type, batch)
                        batch_ids.append(batch_id)
                        
                        # Remove processed items from pending
                        for item in group_items:
                            if item in self.pending_items[message_type]:
                                self.pending_items[message_type].remove(item)
                
                return batch_ids[0] if batch_ids else None
            
            else:
                # Take items for batch
                batch_items = []
                for _ in range(batch_size):
                    if self.pending_items[message_type]:
                        batch_items.append(self.pending_items[message_type].popleft())
                
                if not batch_items:
                    return None
                
                # Create and process batch
                batch = ProcessingBatch(
                    items=batch_items,
                    configuration=config
                )
                
                return await self._process_batch(message_type, batch)
        
        except Exception as e:
            logger.error(f"Error creating batch from pending: {str(e)}")
            return None
    
    async def _process_batch(self, message_type: str, batch: ProcessingBatch) -> str:
        """Process a batch of items"""
        try:
            batch.started_at = datetime.now(timezone.utc)
            batch.status = BatchStatus.PROCESSING
            
            self.active_batches[batch.batch_id] = batch
            
            # Get processor function
            processor = self.processors.get(message_type)
            if not processor:
                raise MessageQueueError(f"No processor registered for {message_type}")
            
            # Decrypt items if needed
            if self.encryption:
                for item in batch.items:
                    item.payload = await self._decrypt_payload(item.payload)
            
            # Process based on processing mode
            if batch.configuration.processing_mode == ProcessingMode.SEQUENTIAL:
                await self._process_sequential(batch, processor)
            elif batch.configuration.processing_mode == ProcessingMode.PARALLEL:
                await self._process_parallel(batch, processor)
            elif batch.configuration.processing_mode == ProcessingMode.PIPELINE:
                await self._process_pipeline(batch, processor)
            elif batch.configuration.processing_mode == ProcessingMode.MAP_REDUCE:
                await self._process_map_reduce(batch, processor)
            
            # Complete batch processing
            batch.completed_at = datetime.now(timezone.utc)
            batch.processing_duration = (batch.completed_at - batch.started_at).total_seconds()
            
            # Calculate metrics
            await self._calculate_batch_metrics(batch)
            
            # Update performance history
            await self._update_performance_history(message_type, batch)
            
            # Move to completed
            self.completed_batches[batch.batch_id] = batch
            del self.active_batches[batch.batch_id]
            
            # Update global metrics
            await self._update_global_metrics(batch)
            
            logger.info(f"Completed batch {batch.batch_id} with {batch.successful_items}/{len(batch.items)} successful items")
            return batch.batch_id
            
        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}")
            batch.status = BatchStatus.FAILED
            batch.error_details.append(str(e))
            return batch.batch_id
    
    async def _process_sequential(self, batch: ProcessingBatch, processor: Callable):
        """Process batch items sequentially"""
        for item in batch.items:
            try:
                start_time = time.time()
                
                # Process item
                result = await processor(item.payload, item.business_context)
                
                item.processing_time = time.time() - start_time
                item.success = True
                batch.successful_items += 1
                
            except Exception as e:
                item.processing_time = time.time() - start_time
                item.error = str(e)
                item.success = False
                batch.failed_items += 1
                batch.error_details.append(f"Item {item.item_id}: {str(e)}")
    
    async def _process_parallel(self, batch: ProcessingBatch, processor: Callable):
        """Process batch items in parallel"""
        semaphore = asyncio.Semaphore(batch.configuration.max_parallel_workers)
        
        async def process_item(item: BatchItem):
            async with semaphore:
                try:
                    start_time = time.time()
                    
                    # Process with timeout
                    result = await asyncio.wait_for(
                        processor(item.payload, item.business_context),
                        timeout=batch.configuration.timeout_per_item
                    )
                    
                    item.processing_time = time.time() - start_time
                    item.success = True
                    batch.successful_items += 1
                    
                except Exception as e:
                    item.processing_time = time.time() - start_time if 'start_time' in locals() else 0
                    item.error = str(e)
                    item.success = False
                    batch.failed_items += 1
                    batch.error_details.append(f"Item {item.item_id}: {str(e)}")
        
        # Process all items in parallel
        tasks = [process_item(item) for item in batch.items]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_pipeline(self, batch: ProcessingBatch, processor: Callable):
        """Process batch items in pipeline stages"""
        # For pipeline processing, we process items in groups through stages
        # This is a simplified implementation
        
        pipeline_stages = batch.configuration.max_parallel_workers
        items_per_stage = len(batch.items) // pipeline_stages
        
        stages = []
        for i in range(0, len(batch.items), items_per_stage):
            stage_items = batch.items[i:i + items_per_stage]
            stages.append(stage_items)
        
        # Process each stage
        for stage_items in stages:
            await self._process_parallel_stage(stage_items, processor, batch)
    
    async def _process_parallel_stage(self, items: List[BatchItem], processor: Callable, batch: ProcessingBatch):
        """Process a stage of items in parallel"""
        tasks = []
        for item in items:
            task = self._process_single_item(item, processor, batch)
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_single_item(self, item: BatchItem, processor: Callable, batch: ProcessingBatch):
        """Process a single item"""
        try:
            start_time = time.time()
            result = await processor(item.payload, item.business_context)
            
            item.processing_time = time.time() - start_time
            item.success = True
            batch.successful_items += 1
            
        except Exception as e:
            item.processing_time = time.time() - start_time if 'start_time' in locals() else 0
            item.error = str(e)
            item.success = False
            batch.failed_items += 1
            batch.error_details.append(f"Item {item.item_id}: {str(e)}")
    
    async def _process_map_reduce(self, batch: ProcessingBatch, processor: Callable):
        """Process batch using map-reduce pattern"""
        # Map phase - process items in parallel
        await self._process_parallel(batch, processor)
        
        # Reduce phase - aggregate results (simplified)
        successful_results = [item for item in batch.items if item.success]
        
        # Additional reduce processing could be added here
        logger.debug(f"Map-reduce completed: {len(successful_results)} successful items")
    
    # Helper methods
    
    def _get_batch_configuration(self, message_type: str) -> BatchConfiguration:
        """Get batch configuration for message type"""
        if message_type in self.batch_configurations:
            return self.batch_configurations[message_type]
        
        # Get from business defaults
        if message_type in AinflueBusiness.BATCH_CONFIGS:
            config = AinflueBusiness.BATCH_CONFIGS[message_type]
            self.batch_configurations[message_type] = config
            return config
        
        # Create default configuration
        config = BatchConfiguration()
        self.batch_configurations[message_type] = config
        return config
    
    async def _group_items_by_business_logic(self, items: List[BatchItem], config: BatchConfiguration) -> List[List[BatchItem]]:
        """Group items by business logic"""
        if not config.business_grouping_key:
            return [items]
        
        grouping_func = AinflueBusiness.BUSINESS_GROUPING_FUNCTIONS.get(config.business_grouping_key)
        if not grouping_func:
            return [items]
        
        groups = defaultdict(list)
        for item in items:
            group_key = grouping_func(item)
            groups[group_key].append(item)
        
        # Sort by priority if enabled
        if config.priority_grouping:
            for group_items in groups.values():
                group_items.sort(key=lambda x: x.priority)
        
        return list(groups.values())
    
    async def _check_business_logic_batch_creation(self, message_type: str, config: BatchConfiguration) -> bool:
        """Check if business logic requires batch creation"""
        pending_items = list(self.pending_items[message_type])
        
        if not pending_items:
            return False
        
        # Group by business logic
        if config.business_grouping_key:
            groups = await self._group_items_by_business_logic(pending_items, config)
            
            # Check if any group meets minimum size
            for group in groups:
                if len(group) >= config.min_batch_size:
                    return True
        
        # Check if we have enough total items
        return len(pending_items) >= config.optimal_batch_size
    
    async def _get_adaptive_batch_size(self, message_type: str) -> int:
        """Get adaptive batch size based on performance history"""
        config = self._get_batch_configuration(message_type)
        history = list(self.performance_history[message_type])
        
        if len(history) < 10:  # Not enough data for adaptation
            return config.optimal_batch_size
        
        # Find optimal batch size based on efficiency scores
        recent_history = history[-20:]  # Last 20 batches
        
        batch_size_performance = defaultdict(list)
        for record in recent_history:
            batch_size = record["batch_size"]
            efficiency = record["efficiency_score"]
            batch_size_performance[batch_size].append(efficiency)
        
        # Find batch size with best average efficiency
        best_size = config.optimal_batch_size
        best_efficiency = 0.0
        
        for size, efficiencies in batch_size_performance.items():
            avg_efficiency = statistics.mean(efficiencies)
            if avg_efficiency > best_efficiency:
                best_efficiency = avg_efficiency
                best_size = size
        
        # Ensure within bounds
        return max(config.min_batch_size, min(best_size, config.max_batch_size))
    
    async def _ensure_batch_timer(self, message_type: str, config: BatchConfiguration):
        """Ensure batch timer is running for time-based batching"""
        if message_type in self.batch_timers:
            return  # Timer already running
        
        if config.strategy in [BatchStrategy.TIME_BASED, BatchStrategy.HYBRID]:
            timer_task = asyncio.create_task(self._batch_timer(message_type, config.max_wait_time))
            self.batch_timers[message_type] = timer_task
    
    async def _batch_timer(self, message_type: str, wait_time: float):
        """Timer for time-based batch creation"""
        try:
            await asyncio.sleep(wait_time)
            
            # Create batch if items are pending
            if self.pending_items[message_type]:
                await self._create_batch_from_pending(message_type, force=True)
            
            # Remove timer
            if message_type in self.batch_timers:
                del self.batch_timers[message_type]
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in batch timer: {str(e)}")
    
    async def _calculate_batch_metrics(self, batch: ProcessingBatch):
        """Calculate performance metrics for batch"""
        total_items = len(batch.items)
        
        if total_items == 0:
            return
        
        # Calculate throughput
        if batch.processing_duration > 0:
            batch.throughput = total_items / batch.processing_duration
        
        # Calculate efficiency score
        success_rate = batch.successful_items / total_items
        
        # Efficiency is based on success rate and processing speed
        ideal_processing_time = total_items * 0.1  # Assume 0.1s per item ideal
        time_efficiency = min(1.0, ideal_processing_time / max(batch.processing_duration, 0.1))
        
        batch.efficiency_score = (success_rate * 0.7) + (time_efficiency * 0.3)
        
        # Determine batch status
        if batch.failed_items == 0:
            batch.status = BatchStatus.COMPLETED
        elif batch.successful_items == 0:
            batch.status = BatchStatus.FAILED
        else:
            batch.status = BatchStatus.PARTIAL_SUCCESS
    
    async def _update_performance_history(self, message_type: str, batch: ProcessingBatch):
        """Update performance history for adaptive optimization"""
        performance_record = {
            "batch_id": batch.batch_id,
            "batch_size": len(batch.items),
            "processing_time": batch.processing_duration,
            "throughput": batch.throughput,
            "efficiency_score": batch.efficiency_score,
            "success_rate": batch.successful_items / max(len(batch.items), 1),
            "timestamp": batch.completed_at.timestamp() if batch.completed_at else time.time()
        }
        
        # Keep limited history
        history = self.performance_history[message_type]
        history.append(performance_record)
        
        # Keep only recent history
        max_history = self.learning_window
        while len(history) > max_history:
            history.popleft()
    
    async def _update_global_metrics(self, batch: ProcessingBatch):
        """Update global batch metrics"""
        self.batch_metrics.total_batches += 1
        
        if batch.status == BatchStatus.COMPLETED:
            self.batch_metrics.completed_batches += 1
        elif batch.status == BatchStatus.FAILED:
            self.batch_metrics.failed_batches += 1
        
        self.batch_metrics.total_items_processed += len(batch.items)
        
        # Update averages
        total_batches = self.batch_metrics.total_batches
        
        # Update average batch size
        new_avg_size = ((self.batch_metrics.avg_batch_size * (total_batches - 1)) + len(batch.items)) / total_batches
        self.batch_metrics.avg_batch_size = new_avg_size
        
        # Update average processing time
        new_avg_time = ((self.batch_metrics.avg_processing_time * (total_batches - 1)) + batch.processing_duration) / total_batches
        self.batch_metrics.avg_processing_time = new_avg_time
        
        # Update average throughput
        new_avg_throughput = ((self.batch_metrics.avg_throughput * (total_batches - 1)) + batch.throughput) / total_batches
        self.batch_metrics.avg_throughput = new_avg_throughput
        
        # Track efficiency scores
        self.batch_metrics.efficiency_scores.append(batch.efficiency_score)
        
        # Keep limited efficiency history
        if len(self.batch_metrics.efficiency_scores) > 1000:
            self.batch_metrics.efficiency_scores = self.batch_metrics.efficiency_scores[-500:]
    
    async def _optimize_message_type_config(self, message_type: str) -> Dict[str, Any]:
        """Optimize configuration for specific message type"""
        config = self._get_batch_configuration(message_type)
        history = list(self.performance_history[message_type])
        
        if len(history) < 20:  # Need sufficient data
            return {"status": "insufficient_data", "min_required": 20, "current": len(history)}
        
        optimization_suggestions = []
        
        # Analyze efficiency trends
        recent_efficiency = [h["efficiency_score"] for h in history[-10:]]
        avg_recent_efficiency = statistics.mean(recent_efficiency)
        
        if avg_recent_efficiency < AinflueBusiness.PERFORMANCE_THRESHOLDS["min_efficiency_score"]:
            optimization_suggestions.append("Consider adjusting batch size or processing mode")
        
        # Analyze batch size optimization
        size_performance = defaultdict(list)
        for record in history:
            size_performance[record["batch_size"]].append(record["efficiency_score"])
        
        optimal_sizes = []
        for size, efficiencies in size_performance.items():
            if len(efficiencies) >= 3:  # Enough samples
                avg_efficiency = statistics.mean(efficiencies)
                if avg_efficiency > 0.8:  # Good performance threshold
                    optimal_sizes.append((size, avg_efficiency))
        
        if optimal_sizes:
            best_size, best_efficiency = max(optimal_sizes, key=lambda x: x[1])
            
            if best_size != config.optimal_batch_size:
                old_size = config.optimal_batch_size
                config.optimal_batch_size = best_size
                optimization_suggestions.append(f"Adjusted optimal batch size from {old_size} to {best_size}")
        
        return {
            "status": "optimized",
            "suggestions": optimization_suggestions,
            "current_efficiency": avg_recent_efficiency,
            "optimal_batch_size": config.optimal_batch_size,
            "analysis_period": len(history)
        }
    
    def _batch_to_dict(self, batch: ProcessingBatch, include_items: bool = True) -> Dict[str, Any]:
        """Convert batch to dictionary representation"""
        result = {
            "batch_id": batch.batch_id,
            "status": batch.status.value,
            "total_items": len(batch.items),
            "successful_items": batch.successful_items,
            "failed_items": batch.failed_items,
            "processing_duration": batch.processing_duration,
            "throughput": batch.throughput,
            "efficiency_score": batch.efficiency_score,
            "created_at": batch.created_at.isoformat(),
            "started_at": batch.started_at.isoformat() if batch.started_at else None,
            "completed_at": batch.completed_at.isoformat() if batch.completed_at else None,
            "configuration": {
                "strategy": batch.configuration.strategy.value,
                "processing_mode": batch.configuration.processing_mode.value,
                "max_parallel_workers": batch.configuration.max_parallel_workers
            }
        }
        
        if include_items:
            result["items"] = [
                {
                    "item_id": item.item_id,
                    "success": item.success,
                    "processing_time": item.processing_time,
                    "error": item.error
                }
                for item in batch.items
            ]
        
        return result
    
    async def _encrypt_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt payload"""
        # Placeholder for encryption
        return payload
    
    async def _decrypt_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt payload"""
        # Placeholder for decryption
        return payload


# Export for public API
__all__ = [
    "BatchProcessingOptimizer",
    "BatchConfiguration",
    "BatchItem",
    "ProcessingBatch",
    "BatchMetrics",
    "BatchStrategy",
    "ProcessingMode",
    "BatchStatus",
    "AinflueBusiness"
]