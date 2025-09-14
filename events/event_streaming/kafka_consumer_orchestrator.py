"""IA Influencer Agent - Kafka Consumer Orchestrator
Enterprise Kafka Consumer Group Management for Ainflue Platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.0.0

⚠️ LEGAL WARNING: Unauthorized use prohibited. This is proprietary technology.
"""

from typing import Dict, Any, List, Optional, Callable, Set, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
import json
import logging
import time
from uuid import uuid4
from collections import defaultdict

logger = logging.getLogger(__name__)


class ConsumerState(Enum):
    """Consumer states"""
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies for consumers"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    STICKY = "sticky"
    COOPERATIVE = "cooperative"


class AinflueBusinesConsumerGroups:
    """Consumer groups for Ainflue business workflows"""
    
    # Content Processing Pipeline
    CONTENT_UPLOAD_PROCESSOR = "ainflue-content-upload-processor"
    AI_ANALYSIS_PROCESSOR = "ainflue-ai-analysis-processor"
    CONTENT_PROTECTION_PROCESSOR = "ainflue-content-protection-processor"
    
    # SEO & Search
    SEO_OPTIMIZATION_PROCESSOR = "ainflue-seo-optimization-processor"
    SEARCH_INDEXING_PROCESSOR = "ainflue-search-indexing-processor"
    
    # Collaboration & Matching
    COLLABORATION_MATCHING_PROCESSOR = "ainflue-collaboration-matching-processor"
    RECOMMENDATION_ENGINE_PROCESSOR = "ainflue-recommendation-engine-processor"
    
    # Analytics & Monetization
    REVENUE_ANALYTICS_PROCESSOR = "ainflue-revenue-analytics-processor"
    ENGAGEMENT_METRICS_PROCESSOR = "ainflue-engagement-metrics-processor"
    
    # Distribution & Publishing
    DISTRIBUTION_ORCHESTRATOR = "ainflue-distribution-orchestrator"
    PLATFORM_SYNC_PROCESSOR = "ainflue-platform-sync-processor"


@dataclass
class ConsumerConfig:
    """Configuration for individual consumer"""
    
    consumer_id: str
    group_id: str
    topics: List[str]
    max_poll_records: int = 500
    session_timeout_ms: int = 30000
    heartbeat_interval_ms: int = 3000
    max_poll_interval_ms: int = 300000
    auto_offset_reset: str = "latest"
    enable_auto_commit: bool = False
    auto_commit_interval_ms: int = 5000
    fetch_min_bytes: int = 1
    fetch_max_wait_ms: int = 500
    max_partition_fetch_bytes: int = 1048576  # 1MB
    retry_attempts: int = 3
    retry_delay_ms: int = 1000
    dead_letter_topic: Optional[str] = None
    message_handler: Optional[Callable] = None
    error_handler: Optional[Callable] = None


@dataclass
class ConsumerMetrics:
    """Consumer performance metrics"""
    
    consumer_id: str
    messages_processed: int = 0
    messages_failed: int = 0
    processing_time_ms: float = 0.0
    lag: int = 0
    throughput_per_sec: float = 0.0
    last_commit_offset: int = -1
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    errors: List[str] = field(default_factory=list)
    state: ConsumerState = ConsumerState.IDLE


@dataclass
class ConsumerGroupMetrics:
    """Consumer group aggregate metrics"""
    
    group_id: str
    total_consumers: int = 0
    active_consumers: int = 0
    total_lag: int = 0
    avg_processing_time_ms: float = 0.0
    total_throughput_per_sec: float = 0.0
    error_rate: float = 0.0
    rebalance_count: int = 0
    last_rebalance: Optional[datetime] = None


class MessageProcessor(ABC):
    """Abstract base class for message processors"""
    
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> bool:
        """Process a message. Return True if successful, False otherwise."""
        pass
    
    @abstractmethod
    async def handle_error(self, message: Dict[str, Any], error: Exception) -> bool:
        """Handle processing error. Return True to retry, False to skip."""
        pass


class ContentUploadProcessor(MessageProcessor):
    """Processor for content upload events"""
    
    async def process_message(self, message: Dict[str, Any]) -> bool:
        """Process content upload message"""
        try:
            payload = message.get("payload", {})
            creator_id = payload.get("creator_id")
            content_type = payload.get("content_type")
            
            logger.info(f"Processing content upload for creator {creator_id}, type {content_type}")
            
            # Simulate content processing
            await asyncio.sleep(0.1)
            
            # Trigger AI analysis
            # In real implementation, would call AI analysis service
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing content upload: {e}")
            return False
    
    async def handle_error(self, message: Dict[str, Any], error: Exception) -> bool:
        """Handle content upload processing error"""
        retry_count = message.get("retry_count", 0)
        if retry_count < 3:
            logger.warning(f"Retrying content upload processing (attempt {retry_count + 1})")
            return True
        else:
            logger.error(f"Max retries exceeded for content upload: {error}")
            return False


class AIAnalysisProcessor(MessageProcessor):
    """Processor for AI analysis events"""
    
    async def process_message(self, message: Dict[str, Any]) -> bool:
        """Process AI analysis message"""
        try:
            payload = message.get("payload", {})
            content_id = payload.get("content_id")
            analysis_type = payload.get("analysis_type")
            
            logger.info(f"Processing AI analysis for content {content_id}, type {analysis_type}")
            
            # Simulate AI analysis processing
            await asyncio.sleep(0.5)  # AI processing takes longer
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing AI analysis: {e}")
            return False
    
    async def handle_error(self, message: Dict[str, Any], error: Exception) -> bool:
        """Handle AI analysis processing error"""
        # AI analysis failures are more critical, retry more times
        retry_count = message.get("retry_count", 0)
        if retry_count < 5:
            logger.warning(f"Retrying AI analysis processing (attempt {retry_count + 1})")
            return True
        else:
            logger.error(f"Max retries exceeded for AI analysis: {error}")
            return False


class KafkaConsumer:
    """Individual Kafka consumer instance"""
    
    def __init__(self, config -> None: ConsumerConfig, metrics_collector=None) -> None:
        self.config = config
        self.metrics_collector = metrics_collector
        self.metrics = ConsumerMetrics(consumer_id=config.consumer_id)
        self.state = ConsumerState.IDLE
        self._consumer_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # Start unpaused
        
    async def start(self) -> None:
        """Start the consumer"""
        try:
            if self.state != ConsumerState.IDLE:
                raise ValueError(f"Consumer {self.config.consumer_id} is not in idle state")
            
            self.state = ConsumerState.STARTING
            self.metrics.state = ConsumerState.STARTING
            
            logger.info(f"Starting consumer {self.config.consumer_id}")
            
            # Start consumer task
            self._consumer_task = asyncio.create_task(self._consume_loop())
            
            self.state = ConsumerState.RUNNING
            self.metrics.state = ConsumerState.RUNNING
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("kafka_consumer_started")
            
            logger.info(f"Consumer {self.config.consumer_id} started successfully")
            
        except Exception as e:
            self.state = ConsumerState.ERROR
            self.metrics.state = ConsumerState.ERROR
            logger.error(f"Failed to start consumer {self.config.consumer_id}: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the consumer gracefully"""
        try:
            if self.state not in [ConsumerState.RUNNING, ConsumerState.PAUSED]:
                return
            
            self.state = ConsumerState.STOPPING
            self.metrics.state = ConsumerState.STOPPING
            
            logger.info(f"Stopping consumer {self.config.consumer_id}")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Wait for consumer task to complete
            if self._consumer_task:
                await self._consumer_task
            
            self.state = ConsumerState.STOPPED
            self.metrics.state = ConsumerState.STOPPED
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("kafka_consumer_stopped")
            
            logger.info(f"Consumer {self.config.consumer_id} stopped successfully")
            
        except Exception as e:
            self.state = ConsumerState.ERROR
            self.metrics.state = ConsumerState.ERROR
            logger.error(f"Error stopping consumer {self.config.consumer_id}: {e}")
            raise
    
    async def pause(self) -> None:
        """Pause the consumer"""
        if self.state == ConsumerState.RUNNING:
            self.state = ConsumerState.PAUSED
            self.metrics.state = ConsumerState.PAUSED
            self._pause_event.clear()
            logger.info(f"Consumer {self.config.consumer_id} paused")
    
    async def resume(self) -> None:
        """Resume the consumer"""
        if self.state == ConsumerState.PAUSED:
            self.state = ConsumerState.RUNNING
            self.metrics.state = ConsumerState.RUNNING
            self._pause_event.set()
            logger.info(f"Consumer {self.config.consumer_id} resumed")
    
    async def _consume_loop(self) -> None:
        """Main consumer loop"""
        try:
            while not self._shutdown_event.is_set():
                # Wait if paused
                await self._pause_event.wait()
                
                # Simulate message fetching
                messages = await self._fetch_messages()
                
                if messages:
                    await self._process_messages(messages)
                else:
                    # No messages, sleep briefly
                    await asyncio.sleep(0.1)
                
                # Update heartbeat
                self.metrics.last_heartbeat = datetime.now(timezone.utc)
                
        except Exception as e:
            logger.error(f"Error in consumer loop for {self.config.consumer_id}: {e}")
            self.state = ConsumerState.ERROR
            self.metrics.state = ConsumerState.ERROR
            raise
    
    async def _fetch_messages(self) -> List[Dict[str, Any]]:
        """Fetch messages from Kafka (simulated)"""
        try:
            # Simulate message fetching
            await asyncio.sleep(0.01)  # Simulate network latency
            
            # Return simulated messages based on topics
            messages = []
            for topic in self.config.topics:
                if "content" in topic:
                    messages.append({
                        "topic": topic,
                        "partition": 0,
                        "offset": self.metrics.last_commit_offset + 1,
                        "key": f"content_{uuid4()}",
                        "value": {
                            "event_type": "content.upload.completed",
                            "payload": {
                                "creator_id": f"creator_{uuid4()}",
                                "content_type": "video",
                                "content_id": f"content_{uuid4()}"
                            },
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    })
            
            return messages[:self.config.max_poll_records]
            
        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
            return []
    
    async def _process_messages(self, messages -> None: List[Dict[str, Any]]) -> None:
        """Process fetched messages"""
        try:
            for message in messages:
                start_time = time.time()
                
                try:
                    # Process message
                    success = await self._process_single_message(message)
                    
                    if success:
                        self.metrics.messages_processed += 1
                        
                        # Commit offset if auto-commit is disabled
                        if not self.config.enable_auto_commit:
                            await self._commit_offset(message)
                    else:
                        self.metrics.messages_failed += 1
                        await self._handle_failed_message(message)
                    
                except Exception as e:
                    self.metrics.messages_failed += 1
                    self.metrics.errors.append(str(e))
                    logger.error(f"Error processing message: {e}")
                    
                    # Send to dead letter queue if configured
                    if self.config.dead_letter_topic:
                        await self._send_to_dead_letter_queue(message, str(e))
                
                # Update processing time metrics
                processing_time = (time.time() - start_time) * 1000
                self._update_processing_time(processing_time)
                
                if self.metrics_collector:
                    self.metrics_collector.histogram("kafka_message_processing_time", processing_time)
            
        except Exception as e:
            logger.error(f"Error processing message batch: {e}")
            raise
    
    async def _process_single_message(self, message: Dict[str, Any]) -> bool:
        """Process a single message"""
        try:
            if self.config.message_handler:
                return await self.config.message_handler(message)
            else:
                # Default processing
                logger.debug(f"Processing message from {message['topic']}: {message['key']}")
                return True
                
        except Exception as e:
            if self.config.error_handler:
                return await self.config.error_handler(message, e)
            else:
                logger.error(f"No error handler configured for message processing error: {e}")
                return False
    
    async def _commit_offset(self, message -> None: Dict[str, Any]) -> None:
        """Commit message offset"""
        try:
            # Simulate offset commit
            self.metrics.last_commit_offset = message["offset"]
            logger.debug(f"Committed offset {message['offset']} for topic {message['topic']}")
            
        except Exception as e:
            logger.error(f"Error committing offset: {e}")
    
    async def _handle_failed_message(self, message -> None: Dict[str, Any]) -> None:
        """Handle failed message processing"""
        try:
            retry_count = message.get("retry_count", 0)
            
            if retry_count < self.config.retry_attempts:
                # Retry after delay
                await asyncio.sleep(self.config.retry_delay_ms / 1000.0)
                message["retry_count"] = retry_count + 1
                await self._process_single_message(message)
            else:
                # Max retries exceeded
                logger.error(f"Max retries exceeded for message: {message['key']}")
                
                if self.config.dead_letter_topic:
                    await self._send_to_dead_letter_queue(message, "Max retries exceeded")
            
        except Exception as e:
            logger.error(f"Error handling failed message: {e}")
    
    async def _send_to_dead_letter_queue(self, message -> None: Dict[str, Any], error -> None: str) -> None:
        """Send failed message to dead letter queue"""
        try:
            dlq_message = {
                **message,
                "dlq_timestamp": datetime.now(timezone.utc).isoformat(),
                "dlq_error": error,
                "dlq_consumer_id": self.config.consumer_id
            }
            
            # In real implementation, would send to actual DLQ topic
            logger.warning(f"Sending message to DLQ {self.config.dead_letter_topic}: {message['key']}")
            
        except Exception as e:
            logger.error(f"Error sending message to DLQ: {e}")
    
    def _update_processing_time(self, processing_time_ms -> None: float) -> None:
        """Update processing time metrics"""
        if self.metrics.processing_time_ms == 0:
            self.metrics.processing_time_ms = processing_time_ms
        else:
            # Exponential moving average
            alpha = 0.1
            self.metrics.processing_time_ms = (
                (1 - alpha) * self.metrics.processing_time_ms + 
                alpha * processing_time_ms
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get consumer metrics"""
        return {
            "consumer_id": self.metrics.consumer_id,
            "state": self.metrics.state.value,
            "messages_processed": self.metrics.messages_processed,
            "messages_failed": self.metrics.messages_failed,
            "processing_time_ms": self.metrics.processing_time_ms,
            "lag": self.metrics.lag,
            "throughput_per_sec": self.metrics.throughput_per_sec,
            "last_commit_offset": self.metrics.last_commit_offset,
            "last_heartbeat": self.metrics.last_heartbeat.isoformat(),
            "error_count": len(self.metrics.errors),
            "recent_errors": self.metrics.errors[-5:]  # Last 5 errors
        }


class KafkaConsumerOrchestrator:
    """Orchestrates multiple Kafka consumer groups for Ainflue platform"""
    
    def __init__(self, metrics_collector=None) -> None:
        self.metrics_collector = metrics_collector
        self.consumer_groups: Dict[str, List[KafkaConsumer]] = {}
        self.group_metrics: Dict[str, ConsumerGroupMetrics] = {}
        self.processors: Dict[str, MessageProcessor] = {}
        self._orchestrator_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Register default processors
        self._register_default_processors()
    
    def _register_default_processors(self) -> None:
        """Register default message processors for Ainflue business logic"""
        self.processors["content_upload"] = ContentUploadProcessor()
        self.processors["ai_analysis"] = AIAnalysisProcessor()
    
    async def start(self) -> None:
        """Start the consumer orchestrator"""
        try:
            logger.info("Starting Kafka Consumer Orchestrator")
            
            # Start orchestrator monitoring task
            self._orchestrator_task = asyncio.create_task(self._orchestrator_loop())
            
            # Setup default consumer groups for Ainflue
            await self._setup_default_consumer_groups()
            
            logger.info("Kafka Consumer Orchestrator started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start consumer orchestrator: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the consumer orchestrator"""
        try:
            logger.info("Stopping Kafka Consumer Orchestrator")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Stop all consumers
            for group_id, consumers in self.consumer_groups.items():
                for consumer in consumers:
                    await consumer.stop()
            
            # Wait for orchestrator task
            if self._orchestrator_task:
                await self._orchestrator_task
            
            logger.info("Kafka Consumer Orchestrator stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping consumer orchestrator: {e}")
            raise
    
    async def _setup_default_consumer_groups(self) -> None:
        """Setup default consumer groups for Ainflue platform"""
        try:
            # Content upload processing group
            await self.create_consumer_group(
                group_id=AinflueBusinesConsumerGroups.CONTENT_UPLOAD_PROCESSOR,
                topics=["ainflue-content-events"],
                consumer_count=3,
                processor=self.processors["content_upload"]
            )
            
            # AI analysis processing group
            await self.create_consumer_group(
                group_id=AinflueBusinesConsumerGroups.AI_ANALYSIS_PROCESSOR,
                topics=["ainflue-content-events"],
                consumer_count=2,
                processor=self.processors["ai_analysis"]
            )
            
            # Revenue analytics group
            await self.create_consumer_group(
                group_id=AinflueBusinesConsumerGroups.REVENUE_ANALYTICS_PROCESSOR,
                topics=["ainflue-revenue-events"],
                consumer_count=1,
                processor=None  # Default processing
            )
            
        except Exception as e:
            logger.error(f"Error setting up default consumer groups: {e}")
            raise
    
    async def create_consumer_group(self, 
                                  group_id: str, 
                                  topics: List[str], 
                                  consumer_count: int = 1,
                                  processor: Optional[MessageProcessor] = None) -> List[str]:
        """Create a new consumer group"""
        try:
            logger.info(f"Creating consumer group {group_id} with {consumer_count} consumers")
            
            consumers = []
            consumer_ids = []
            
            for i in range(consumer_count):
                consumer_id = f"{group_id}-consumer-{i}"
                consumer_ids.append(consumer_id)
                
                # Create message handler if processor provided
                message_handler = None
                error_handler = None
                if processor:
                    message_handler = processor.process_message
                    error_handler = processor.handle_error
                
                # Create consumer config
                config = ConsumerConfig(
                    consumer_id=consumer_id,
                    group_id=group_id,
                    topics=topics,
                    message_handler=message_handler,
                    error_handler=error_handler,
                    dead_letter_topic=f"{group_id}-dlq"
                )
                
                # Create and start consumer
                consumer = KafkaConsumer(config, self.metrics_collector)
                await consumer.start()
                
                consumers.append(consumer)
            
            # Store consumer group
            self.consumer_groups[group_id] = consumers
            self.group_metrics[group_id] = ConsumerGroupMetrics(
                group_id=group_id,
                total_consumers=consumer_count,
                active_consumers=consumer_count
            )
            
            logger.info(f"Created consumer group {group_id} successfully")
            return consumer_ids
            
        except Exception as e:
            logger.error(f"Error creating consumer group {group_id}: {e}")
            raise
    
    async def scale_consumer_group(self, group_id -> None: str, target_consumer_count -> None: int) -> None:
        """Scale consumer group up or down"""
        try:
            if group_id not in self.consumer_groups:
                raise ValueError(f"Consumer group {group_id} not found")
            
            current_consumers = self.consumer_groups[group_id]
            current_count = len(current_consumers)
            
            if target_consumer_count == current_count:
                logger.info(f"Consumer group {group_id} already has {current_count} consumers")
                return
            
            if target_consumer_count > current_count:
                # Scale up
                await self._scale_up_consumer_group(group_id, target_consumer_count - current_count)
            else:
                # Scale down
                await self._scale_down_consumer_group(group_id, current_count - target_consumer_count)
            
            # Update metrics
            self.group_metrics[group_id].total_consumers = target_consumer_count
            self.group_metrics[group_id].active_consumers = target_consumer_count
            
            logger.info(f"Scaled consumer group {group_id} to {target_consumer_count} consumers")
            
        except Exception as e:
            logger.error(f"Error scaling consumer group {group_id}: {e}")
            raise
    
    async def _scale_up_consumer_group(self, group_id -> None: str, additional_consumers -> None: int) -> None:
        """Add consumers to a group"""
        try:
            existing_consumers = self.consumer_groups[group_id]
            
            # Get config from existing consumer
            template_config = existing_consumers[0].config
            
            for i in range(additional_consumers):
                consumer_index = len(existing_consumers) + i
                consumer_id = f"{group_id}-consumer-{consumer_index}"
                
                # Create new consumer config
                config = ConsumerConfig(
                    consumer_id=consumer_id,
                    group_id=group_id,
                    topics=template_config.topics,
                    message_handler=template_config.message_handler,
                    error_handler=template_config.error_handler,
                    dead_letter_topic=template_config.dead_letter_topic
                )
                
                # Create and start consumer
                consumer = KafkaConsumer(config, self.metrics_collector)
                await consumer.start()
                
                existing_consumers.append(consumer)
            
        except Exception as e:
            logger.error(f"Error scaling up consumer group {group_id}: {e}")
            raise
    
    async def _scale_down_consumer_group(self, group_id -> None: str, consumers_to_remove -> None: int) -> None:
        """Remove consumers from a group"""
        try:
            existing_consumers = self.consumer_groups[group_id]
            
            # Stop and remove consumers
            for _ in range(consumers_to_remove):
                if existing_consumers:
                    consumer = existing_consumers.pop()
                    await consumer.stop()
            
        except Exception as e:
            logger.error(f"Error scaling down consumer group {group_id}: {e}")
            raise
    
    async def _orchestrator_loop(self) -> None:
        """Main orchestrator monitoring loop"""
        try:
            while not self._shutdown_event.is_set():
                # Update metrics for all consumer groups
                await self._update_group_metrics()
                
                # Check for rebalancing needs
                await self._check_rebalancing_needs()
                
                # Health checks
                await self._perform_health_checks()
                
                # Sleep before next iteration
                await asyncio.sleep(10)  # Check every 10 seconds
                
        except Exception as e:
            logger.error(f"Error in orchestrator loop: {e}")
    
    async def _update_group_metrics(self) -> None:
        """Update metrics for all consumer groups"""
        try:
            for group_id, consumers in self.consumer_groups.items():
                group_metrics = self.group_metrics[group_id]
                
                # Aggregate consumer metrics
                total_processed = sum(c.metrics.messages_processed for c in consumers)
                total_failed = sum(c.metrics.messages_failed for c in consumers)
                active_consumers = sum(1 for c in consumers if c.state == ConsumerState.RUNNING)
                
                # Update group metrics
                group_metrics.active_consumers = active_consumers
                group_metrics.error_rate = (
                    total_failed / max(1, total_processed + total_failed)
                ) * 100
                
                if total_processed > 0:
                    group_metrics.avg_processing_time_ms = sum(
                        c.metrics.processing_time_ms for c in consumers
                    ) / len(consumers)
                
        except Exception as e:
            logger.error(f"Error updating group metrics: {e}")
    
    async def _check_rebalancing_needs(self) -> None:
        """Check if any consumer groups need rebalancing"""
        try:
            for group_id, consumers in self.consumer_groups.items():
                group_metrics = self.group_metrics[group_id]
                
                # Simple auto-scaling based on lag
                avg_lag = sum(c.metrics.lag for c in consumers) / len(consumers)
                
                if avg_lag > 1000 and group_metrics.active_consumers < 10:
                    # High lag, scale up
                    logger.info(f"High lag detected for group {group_id}, scaling up")
                    await self.scale_consumer_group(group_id, group_metrics.total_consumers + 1)
                    group_metrics.rebalance_count += 1
                    group_metrics.last_rebalance = datetime.now(timezone.utc)
                
                elif avg_lag < 100 and group_metrics.active_consumers > 1:
                    # Low lag, scale down if safe
                    logger.info(f"Low lag detected for group {group_id}, considering scale down")
                    # Only scale down if stable for a while
                    
        except Exception as e:
            logger.error(f"Error checking rebalancing needs: {e}")
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks on all consumers"""
        try:
            for group_id, consumers in self.consumer_groups.items():
                for consumer in consumers:
                    # Check if consumer is responsive
                    time_since_heartbeat = (
                        datetime.now(timezone.utc) - consumer.metrics.last_heartbeat
                    ).total_seconds()
                    
                    if time_since_heartbeat > 60:  # 1 minute without heartbeat
                        logger.warning(f"Consumer {consumer.config.consumer_id} appears unresponsive")
                        
                        # Restart consumer
                        await consumer.stop()
                        await consumer.start()
                        
                        logger.info(f"Restarted unresponsive consumer {consumer.config.consumer_id}")
                    
        except Exception as e:
            logger.error(f"Error performing health checks: {e}")
    
    def get_orchestrator_metrics(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator metrics"""
        try:
            metrics = {
                "total_consumer_groups": len(self.consumer_groups),
                "total_consumers": sum(len(consumers) for consumers in self.consumer_groups.values()),
                "consumer_groups": {},
                "system_health": "healthy"
            }
            
            for group_id, group_metrics in self.group_metrics.items():
                metrics["consumer_groups"][group_id] = {
                    "total_consumers": group_metrics.total_consumers,
                    "active_consumers": group_metrics.active_consumers,
                    "total_lag": group_metrics.total_lag,
                    "avg_processing_time_ms": group_metrics.avg_processing_time_ms,
                    "total_throughput_per_sec": group_metrics.total_throughput_per_sec,
                    "error_rate": group_metrics.error_rate,
                    "rebalance_count": group_metrics.rebalance_count,
                    "last_rebalance": (
                        group_metrics.last_rebalance.isoformat() 
                        if group_metrics.last_rebalance else None
                    )
                }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting orchestrator metrics: {e}")
            return {"error": str(e)}


# Export public API
__all__ = [
    "KafkaConsumerOrchestrator", "KafkaConsumer", "ConsumerConfig",
    "AinflueBusinesConsumerGroups", "MessageProcessor", "ContentUploadProcessor",
    "AIAnalysisProcessor", "ConsumerState", "LoadBalancingStrategy"
]