"""IA Influencer Agent - Pulsar Integration Engine
Apache Pulsar Integration for Cross-Datacenter Event Streaming in Ainflue Platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.0.0

⚠️ LEGAL WARNING: Unauthorized use prohibited. This is proprietary technology.
"""

from typing import Dict, Any, List, Optional, Callable, Union, Set
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import logging
import time
import hashlib
from uuid import uuid4
from collections import defaultdict

logger = logging.getLogger(__name__)


class PulsarCompressionType(Enum):
    """Pulsar compression types"""
    NONE = "NONE"
    LZ4 = "LZ4"
    ZLIB = "ZLIB"
    ZSTD = "ZSTD"
    SNAPPY = "SNAPPY"


class PulsarSubscriptionType(Enum):
    """Pulsar subscription types"""
    EXCLUSIVE = "Exclusive"
    SHARED = "Shared"
    FAILOVER = "Failover"
    KEY_SHARED = "Key_Shared"


class ReplicationStrategy(Enum):
    """Geo-replication strategies"""
    ASYNC_REPLICATION = "async"
    SYNC_REPLICATION = "sync"
    LAZY_REPLICATION = "lazy"


class AinflueBusinesPulsarTopics:
    """Pulsar topics for Ainflue cross-datacenter events"""
    
    # Global content distribution
    GLOBAL_CONTENT_DISTRIBUTION = "persistent://ainflue/global/content-distribution"
    CROSS_REGION_SYNC = "persistent://ainflue/global/cross-region-sync"
    
    # Creator-specific tenants (template)
    CREATOR_EVENTS_TEMPLATE = "persistent://ainflue/creator-{creator_id}/events"
    CREATOR_ANALYTICS_TEMPLATE = "persistent://ainflue/creator-{creator_id}/analytics"
    
    # Business critical events
    REVENUE_RECONCILIATION = "persistent://ainflue/finance/revenue-reconciliation"
    AUDIT_TRAIL = "persistent://ainflue/audit/trail"
    
    # Cross-datacenter coordination
    DATACENTER_HEARTBEAT = "persistent://ainflue/system/datacenter-heartbeat"
    GLOBAL_CONFIGURATION = "persistent://ainflue/system/global-configuration"


@dataclass
class PulsarProducerConfig:
    """Pulsar producer configuration"""
    
    topic: str
    producer_name: Optional[str] = None
    send_timeout_ms: int = 30000
    block_if_queue_full: bool = True
    max_pending_messages: int = 1000
    compression_type: PulsarCompressionType = PulsarCompressionType.LZ4
    batching_enabled: bool = True
    batching_max_messages: int = 1000
    batching_max_publish_delay_ms: int = 10
    encryption_key: Optional[str] = None
    properties: Dict[str, str] = field(default_factory=dict)


@dataclass
class PulsarConsumerConfig:
    """Pulsar consumer configuration"""
    
    topics: List[str]
    subscription_name: str
    subscription_type: PulsarSubscriptionType = PulsarSubscriptionType.SHARED
    consumer_name: Optional[str] = None
    receive_queue_size: int = 1000
    ack_timeout_ms: int = 30000
    unacked_messages_timeout_ms: int = 60000
    negative_ack_redelivery_delay_ms: int = 60000
    max_total_receiver_queue_size_across_partitions: int = 50000
    properties: Dict[str, str] = field(default_factory=dict)


@dataclass
class PulsarClusterConfig:
    """Pulsar cluster configuration"""
    
    service_url: str
    auth_plugin: Optional[str] = None
    auth_params: Optional[str] = None
    operation_timeout_seconds: int = 30
    io_threads: int = 1
    message_listener_threads: int = 1
    concurrent_lookup_requests: int = 5000
    log_conf_file_path: Optional[str] = None
    use_tls: bool = False
    tls_trust_certs_file_path: Optional[str] = None
    tls_allow_insecure_connection: bool = False


@dataclass
class GeoReplicationConfig:
    """Geo-replication configuration"""
    
    source_cluster: str
    target_clusters: List[str]
    replication_strategy: ReplicationStrategy = ReplicationStrategy.ASYNC_REPLICATION
    lag_threshold_ms: int = 5000
    max_replication_lag_ms: int = 30000
    enable_deduplication: bool = True
    retention_policy_minutes: int = 10080  # 7 days


@dataclass
class PulsarMessage:
    """Pulsar message structure"""
    
    topic: str
    message_id: str
    payload: bytes
    properties: Dict[str, str]
    event_time: datetime
    publish_time: datetime
    producer_name: Optional[str] = None
    key: Optional[str] = None
    ordering_key: Optional[bytes] = None
    partition_key: Optional[str] = None
    redelivery_count: int = 0


@dataclass
class PulsarMetrics:
    """Pulsar performance metrics"""
    
    messages_sent: int = 0
    messages_received: int = 0
    messages_failed: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    producer_send_latency_ms: float = 0.0
    consumer_receive_latency_ms: float = 0.0
    throughput_per_sec: float = 0.0
    backlog_size: int = 0
    replication_lag_ms: Dict[str, float] = field(default_factory=dict)


class PulsarProducer:
    """Pulsar producer for high-throughput publishing"""
    
    def __init__(self, config: PulsarProducerConfig, cluster_config: PulsarClusterConfig, metrics_collector=None):
        self.config = config
        self.cluster_config = cluster_config
        self.metrics_collector = metrics_collector
        self.metrics = PulsarMetrics()
        self._producer = None
        self._is_connected = False
        
    async def start(self):
        """Start the Pulsar producer"""
        try:
            logger.info(f"Starting Pulsar producer for topic {self.config.topic}")
            
            # In real implementation, this would create actual Pulsar producer
            # For now, we simulate the connection
            await asyncio.sleep(0.1)  # Simulate connection time
            
            self._is_connected = True
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("pulsar_producer_started")
            
            logger.info(f"Pulsar producer started for topic {self.config.topic}")
            
        except Exception as e:
            logger.error(f"Failed to start Pulsar producer: {e}")
            raise
    
    async def stop(self):
        """Stop the Pulsar producer"""
        try:
            if not self._is_connected:
                return
            
            logger.info(f"Stopping Pulsar producer for topic {self.config.topic}")
            
            # Flush any pending messages
            await self._flush_pending_messages()
            
            # Close producer
            self._is_connected = False
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("pulsar_producer_stopped")
            
            logger.info(f"Pulsar producer stopped for topic {self.config.topic}")
            
        except Exception as e:
            logger.error(f"Error stopping Pulsar producer: {e}")
            raise
    
    async def send_async(self, 
                        payload: Dict[str, Any], 
                        key: Optional[str] = None,
                        properties: Optional[Dict[str, str]] = None,
                        event_time: Optional[datetime] = None) -> str:
        """Send message asynchronously"""
        try:
            if not self._is_connected:
                raise RuntimeError("Producer not connected")
            
            start_time = time.time()
            
            # Prepare message
            message_id = str(uuid4())
            serialized_payload = json.dumps(payload).encode('utf-8')
            
            # Create Pulsar message
            message = PulsarMessage(
                topic=self.config.topic,
                message_id=message_id,
                payload=serialized_payload,
                properties=properties or {},
                event_time=event_time or datetime.now(timezone.utc),
                publish_time=datetime.now(timezone.utc),
                producer_name=self.config.producer_name,
                key=key,
                partition_key=key
            )
            
            # Simulate sending (in real implementation, would use Pulsar client)
            await self._send_message(message)
            
            # Update metrics
            send_latency = (time.time() - start_time) * 1000
            self.metrics.messages_sent += 1
            self.metrics.bytes_sent += len(serialized_payload)
            self._update_send_latency(send_latency)
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("pulsar_messages_sent")
                self.metrics_collector.histogram("pulsar_send_latency", send_latency)
                self.metrics_collector.histogram("pulsar_message_size", len(serialized_payload))
            
            logger.debug(f"Sent message {message_id} to {self.config.topic} in {send_latency:.2f}ms")
            
            return message_id
            
        except Exception as e:
            self.metrics.messages_failed += 1
            if self.metrics_collector:
                self.metrics_collector.increment_counter("pulsar_send_errors")
            
            logger.error(f"Failed to send message to {self.config.topic}: {e}")
            raise
    
    async def send_batch(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Send multiple messages in batch"""
        try:
            message_ids = []
            
            for message_data in messages:
                message_id = await self.send_async(
                    payload=message_data.get("payload", {}),
                    key=message_data.get("key"),
                    properties=message_data.get("properties"),
                    event_time=message_data.get("event_time")
                )
                message_ids.append(message_id)
            
            return message_ids
            
        except Exception as e:
            logger.error(f"Failed to send batch messages: {e}")
            raise
    
    async def _send_message(self, message: PulsarMessage):
        """Send message to Pulsar (simulated)"""
        try:
            # Simulate message sending
            await asyncio.sleep(0.001)  # 1ms simulated latency
            
            # In real implementation, would use actual Pulsar producer
            logger.debug(f"Simulated sending message {message.message_id} to {message.topic}")
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
    
    async def _flush_pending_messages(self):
        """Flush any pending messages"""
        try:
            # In real implementation, would flush Pulsar producer
            logger.debug("Flushing pending messages")
            
        except Exception as e:
            logger.error(f"Error flushing messages: {e}")
    
    def _update_send_latency(self, latency_ms: float):
        """Update send latency metrics"""
        if self.metrics.producer_send_latency_ms == 0:
            self.metrics.producer_send_latency_ms = latency_ms
        else:
            alpha = 0.1
            self.metrics.producer_send_latency_ms = (
                (1 - alpha) * self.metrics.producer_send_latency_ms + 
                alpha * latency_ms
            )


class PulsarConsumer:
    """Pulsar consumer for reliable message consumption"""
    
    def __init__(self, 
                 config: PulsarConsumerConfig, 
                 cluster_config: PulsarClusterConfig, 
                 message_handler: Callable[[PulsarMessage], bool],
                 metrics_collector=None):
        self.config = config
        self.cluster_config = cluster_config
        self.message_handler = message_handler
        self.metrics_collector = metrics_collector
        self.metrics = PulsarMetrics()
        self._consumer = None
        self._is_connected = False
        self._consumer_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
    async def start(self):
        """Start the Pulsar consumer"""
        try:
            logger.info(f"Starting Pulsar consumer for topics {self.config.topics}")
            
            # In real implementation, would create actual Pulsar consumer
            await asyncio.sleep(0.1)  # Simulate connection
            
            self._is_connected = True
            
            # Start consumer task
            self._consumer_task = asyncio.create_task(self._consumer_loop())
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("pulsar_consumer_started")
            
            logger.info(f"Pulsar consumer started for topics {self.config.topics}")
            
        except Exception as e:
            logger.error(f"Failed to start Pulsar consumer: {e}")
            raise
    
    async def stop(self):
        """Stop the Pulsar consumer"""
        try:
            if not self._is_connected:
                return
            
            logger.info(f"Stopping Pulsar consumer for topics {self.config.topics}")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Wait for consumer task
            if self._consumer_task:
                await self._consumer_task
            
            self._is_connected = False
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("pulsar_consumer_stopped")
            
            logger.info(f"Pulsar consumer stopped for topics {self.config.topics}")
            
        except Exception as e:
            logger.error(f"Error stopping Pulsar consumer: {e}")
            raise
    
    async def _consumer_loop(self):
        """Main consumer loop"""
        try:
            while not self._shutdown_event.is_set():
                try:
                    # Receive messages
                    message = await self._receive_message()
                    
                    if message:
                        await self._process_message(message)
                    
                except asyncio.TimeoutError:
                    # No message received, continue
                    continue
                except Exception as e:
                    logger.error(f"Error in consumer loop: {e}")
                    await asyncio.sleep(1)  # Brief pause before retrying
                    
        except Exception as e:
            logger.error(f"Fatal error in consumer loop: {e}")
            raise
    
    async def _receive_message(self, timeout_ms: int = 1000) -> Optional[PulsarMessage]:
        """Receive message from Pulsar"""
        try:
            # Simulate message reception
            await asyncio.sleep(0.01)  # Simulate polling
            
            # Create simulated message
            if time.time() % 2 < 1:  # 50% chance of receiving message
                message = PulsarMessage(
                    topic=self.config.topics[0],
                    message_id=str(uuid4()),
                    payload=json.dumps({
                        "event_type": "test_event",
                        "data": {"test": "data"},
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }).encode('utf-8'),
                    properties={"source": "ainflue"},
                    event_time=datetime.now(timezone.utc),
                    publish_time=datetime.now(timezone.utc)
                )
                
                return message
            
            return None
            
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            return None
    
    async def _process_message(self, message: PulsarMessage):
        """Process received message"""
        try:
            start_time = time.time()
            
            # Call message handler
            success = await self.message_handler(message)
            
            processing_time = (time.time() - start_time) * 1000
            
            if success:
                # Acknowledge message
                await self._acknowledge_message(message)
                
                self.metrics.messages_received += 1
                self.metrics.bytes_received += len(message.payload)
                self._update_receive_latency(processing_time)
                
                if self.metrics_collector:
                    self.metrics_collector.increment_counter("pulsar_messages_received")
                    self.metrics_collector.histogram("pulsar_processing_time", processing_time)
                
                logger.debug(f"Processed message {message.message_id} in {processing_time:.2f}ms")
                
            else:
                # Negative acknowledge for retry
                await self._negative_acknowledge_message(message)
                
                self.metrics.messages_failed += 1
                
                if self.metrics_collector:
                    self.metrics_collector.increment_counter("pulsar_processing_errors")
                
                logger.warning(f"Failed to process message {message.message_id}")
                
        except Exception as e:
            self.metrics.messages_failed += 1
            logger.error(f"Error processing message {message.message_id}: {e}")
            
            # Negative acknowledge on error
            await self._negative_acknowledge_message(message)
    
    async def _acknowledge_message(self, message: PulsarMessage):
        """Acknowledge processed message"""
        try:
            # In real implementation, would acknowledge via Pulsar consumer
            logger.debug(f"Acknowledged message {message.message_id}")
            
        except Exception as e:
            logger.error(f"Error acknowledging message: {e}")
    
    async def _negative_acknowledge_message(self, message: PulsarMessage):
        """Negative acknowledge failed message"""
        try:
            # In real implementation, would negative acknowledge via Pulsar consumer
            logger.debug(f"Negative acknowledged message {message.message_id}")
            
        except Exception as e:
            logger.error(f"Error negative acknowledging message: {e}")
    
    def _update_receive_latency(self, latency_ms: float):
        """Update receive latency metrics"""
        if self.metrics.consumer_receive_latency_ms == 0:
            self.metrics.consumer_receive_latency_ms = latency_ms
        else:
            alpha = 0.1
            self.metrics.consumer_receive_latency_ms = (
                (1 - alpha) * self.metrics.consumer_receive_latency_ms + 
                alpha * latency_ms
            )


class GeoReplicationManager:
    """Manages geo-replication across Pulsar clusters"""
    
    def __init__(self, source_cluster: str, replication_config: GeoReplicationConfig, metrics_collector=None):
        self.source_cluster = source_cluster
        self.config = replication_config
        self.metrics_collector = metrics_collector
        self.replication_metrics: Dict[str, float] = {}
        self._monitoring_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
    async def start(self):
        """Start geo-replication monitoring"""
        try:
            logger.info(f"Starting geo-replication monitoring for {self.source_cluster}")
            
            # Start monitoring task
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info("Geo-replication monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start geo-replication monitoring: {e}")
            raise
    
    async def stop(self):
        """Stop geo-replication monitoring"""
        try:
            logger.info("Stopping geo-replication monitoring")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Wait for monitoring task
            if self._monitoring_task:
                await self._monitoring_task
            
            logger.info("Geo-replication monitoring stopped")
            
        except Exception as e:
            logger.error(f"Error stopping geo-replication monitoring: {e}")
            raise
    
    async def _monitoring_loop(self):
        """Monitor geo-replication lag and health"""
        try:
            while not self._shutdown_event.is_set():
                # Check replication lag for all target clusters
                for target_cluster in self.config.target_clusters:
                    lag_ms = await self._check_replication_lag(target_cluster)
                    self.replication_metrics[target_cluster] = lag_ms
                    
                    if lag_ms > self.config.lag_threshold_ms:
                        logger.warning(f"High replication lag to {target_cluster}: {lag_ms}ms")
                        
                        if self.metrics_collector:
                            self.metrics_collector.increment_counter("pulsar_replication_lag_high")
                    
                    if self.metrics_collector:
                        self.metrics_collector.histogram(f"pulsar_replication_lag_{target_cluster}", lag_ms)
                
                # Sleep before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            logger.error(f"Error in geo-replication monitoring: {e}")
    
    async def _check_replication_lag(self, target_cluster: str) -> float:
        """Check replication lag to target cluster"""
        try:
            # In real implementation, would query Pulsar admin API
            # For now, simulate lag measurement
            await asyncio.sleep(0.01)
            
            # Simulate varying lag
            import random
            lag_ms = random.uniform(100, 2000)
            
            return lag_ms
            
        except Exception as e:
            logger.error(f"Error checking replication lag to {target_cluster}: {e}")
            return float('inf')


class PulsarIntegrationEngine:
    """Main engine for Pulsar integration in Ainflue platform"""
    
    def __init__(self, cluster_configs: Dict[str, PulsarClusterConfig], metrics_collector=None):
        self.cluster_configs = cluster_configs
        self.metrics_collector = metrics_collector
        self.producers: Dict[str, PulsarProducer] = {}
        self.consumers: Dict[str, PulsarConsumer] = {}
        self.geo_replication_managers: Dict[str, GeoReplicationManager] = {}
        self._engine_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
    async def start(self):
        """Start the Pulsar integration engine"""
        try:
            logger.info("Starting Pulsar Integration Engine")
            
            # Setup default producers and consumers for Ainflue
            await self._setup_default_topology()
            
            # Start engine monitoring task
            self._engine_task = asyncio.create_task(self._engine_loop())
            
            logger.info("Pulsar Integration Engine started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Pulsar integration engine: {e}")
            raise
    
    async def stop(self):
        """Stop the Pulsar integration engine"""
        try:
            logger.info("Stopping Pulsar Integration Engine")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Stop all components
            for producer in self.producers.values():
                await producer.stop()
            
            for consumer in self.consumers.values():
                await consumer.stop()
            
            for geo_manager in self.geo_replication_managers.values():
                await geo_manager.stop()
            
            # Wait for engine task
            if self._engine_task:
                await self._engine_task
            
            logger.info("Pulsar Integration Engine stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping Pulsar integration engine: {e}")
            raise
    
    async def _setup_default_topology(self):
        """Setup default Pulsar topology for Ainflue"""
        try:
            # Get primary cluster config
            if "primary" not in self.cluster_configs:
                raise ValueError("Primary cluster configuration not found")
            
            primary_config = self.cluster_configs["primary"]
            
            # Create producers for key topics
            key_topics = [
                AinflueBusinesPulsarTopics.GLOBAL_CONTENT_DISTRIBUTION,
                AinflueBusinesPulsarTopics.CROSS_REGION_SYNC,
                AinflueBusinesPulsarTopics.REVENUE_RECONCILIATION,
                AinflueBusinesPulsarTopics.AUDIT_TRAIL
            ]
            
            for topic in key_topics:
                producer_config = PulsarProducerConfig(
                    topic=topic,
                    producer_name=f"ainflue-producer-{topic.split('/')[-1]}",
                    compression_type=PulsarCompressionType.LZ4,
                    batching_enabled=True
                )
                
                producer = PulsarProducer(producer_config, primary_config, self.metrics_collector)
                await producer.start()
                
                self.producers[topic] = producer
            
            # Create consumers with default handlers
            consumer_topics = [
                AinflueBusinesPulsarTopics.GLOBAL_CONTENT_DISTRIBUTION,
                AinflueBusinesPulsarTopics.REVENUE_RECONCILIATION
            ]
            
            for topic in consumer_topics:
                consumer_config = PulsarConsumerConfig(
                    topics=[topic],
                    subscription_name=f"ainflue-subscription-{topic.split('/')[-1]}",
                    subscription_type=PulsarSubscriptionType.SHARED
                )
                
                consumer = PulsarConsumer(
                    consumer_config, 
                    primary_config, 
                    self._default_message_handler,
                    self.metrics_collector
                )
                await consumer.start()
                
                self.consumers[topic] = consumer
            
            # Setup geo-replication if multiple clusters
            if len(self.cluster_configs) > 1:
                await self._setup_geo_replication()
            
            logger.info("Default Pulsar topology setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up default topology: {e}")
            raise
    
    async def _setup_geo_replication(self):
        """Setup geo-replication between clusters"""
        try:
            # Setup replication from primary to other clusters
            target_clusters = [name for name in self.cluster_configs.keys() if name != "primary"]
            
            if target_clusters:
                replication_config = GeoReplicationConfig(
                    source_cluster="primary",
                    target_clusters=target_clusters,
                    replication_strategy=ReplicationStrategy.ASYNC_REPLICATION
                )
                
                geo_manager = GeoReplicationManager("primary", replication_config, self.metrics_collector)
                await geo_manager.start()
                
                self.geo_replication_managers["primary"] = geo_manager
                
                logger.info(f"Setup geo-replication from primary to {target_clusters}")
            
        except Exception as e:
            logger.error(f"Error setting up geo-replication: {e}")
            raise
    
    async def _default_message_handler(self, message: PulsarMessage) -> bool:
        """Default message handler for Pulsar messages"""
        try:
            # Parse message payload
            payload = json.loads(message.payload.decode('utf-8'))
            
            logger.info(f"Received Pulsar message from {message.topic}: {payload.get('event_type', 'unknown')}")
            
            # Basic processing based on topic
            if "content-distribution" in message.topic:
                await self._handle_content_distribution_message(payload)
            elif "revenue-reconciliation" in message.topic:
                await self._handle_revenue_reconciliation_message(payload)
            elif "audit" in message.topic:
                await self._handle_audit_message(payload)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in default message handler: {e}")
            return False
    
    async def _handle_content_distribution_message(self, payload: Dict[str, Any]):
        """Handle content distribution message"""
        try:
            creator_id = payload.get("creator_id")
            content_id = payload.get("content_id")
            
            logger.info(f"Processing content distribution for creator {creator_id}, content {content_id}")
            
            # Implement content distribution logic
            
        except Exception as e:
            logger.error(f"Error handling content distribution message: {e}")
    
    async def _handle_revenue_reconciliation_message(self, payload: Dict[str, Any]):
        """Handle revenue reconciliation message"""
        try:
            transaction_id = payload.get("transaction_id")
            amount = payload.get("amount")
            
            logger.info(f"Processing revenue reconciliation for transaction {transaction_id}, amount {amount}")
            
            # Implement revenue reconciliation logic
            
        except Exception as e:
            logger.error(f"Error handling revenue reconciliation message: {e}")
    
    async def _handle_audit_message(self, payload: Dict[str, Any]):
        """Handle audit trail message"""
        try:
            event_type = payload.get("event_type")
            user_id = payload.get("user_id")
            
            logger.info(f"Processing audit event {event_type} for user {user_id}")
            
            # Implement audit logging
            
        except Exception as e:
            logger.error(f"Error handling audit message: {e}")
    
    async def _engine_loop(self):
        """Main engine monitoring loop"""
        try:
            while not self._shutdown_event.is_set():
                # Monitor producer/consumer health
                await self._monitor_component_health()
                
                # Check geo-replication status
                await self._check_geo_replication_status()
                
                # Perform maintenance tasks
                await self._perform_maintenance()
                
                # Sleep before next iteration
                await asyncio.sleep(60)  # Check every minute
                
        except Exception as e:
            logger.error(f"Error in engine loop: {e}")
    
    async def _monitor_component_health(self):
        """Monitor health of producers and consumers"""
        try:
            # Check producer health
            for topic, producer in self.producers.items():
                if not producer._is_connected:
                    logger.warning(f"Producer for {topic} is disconnected, attempting restart")
                    try:
                        await producer.start()
                    except Exception as e:
                        logger.error(f"Failed to restart producer for {topic}: {e}")
            
            # Check consumer health
            for topic, consumer in self.consumers.items():
                if not consumer._is_connected:
                    logger.warning(f"Consumer for {topic} is disconnected, attempting restart")
                    try:
                        await consumer.start()
                    except Exception as e:
                        logger.error(f"Failed to restart consumer for {topic}: {e}")
                        
        except Exception as e:
            logger.error(f"Error monitoring component health: {e}")
    
    async def _check_geo_replication_status(self):
        """Check geo-replication status"""
        try:
            for cluster, geo_manager in self.geo_replication_managers.items():
                for target_cluster, lag_ms in geo_manager.replication_metrics.items():
                    if lag_ms > geo_manager.config.max_replication_lag_ms:
                        logger.error(f"Replication lag to {target_cluster} exceeded threshold: {lag_ms}ms")
                        
                        if self.metrics_collector:
                            self.metrics_collector.increment_counter("pulsar_replication_lag_critical")
                            
        except Exception as e:
            logger.error(f"Error checking geo-replication status: {e}")
    
    async def _perform_maintenance(self):
        """Perform routine maintenance tasks"""
        try:
            # Update metrics
            for producer in self.producers.values():
                # Calculate throughput
                # In real implementation, would get actual metrics
                pass
            
            # Log system status
            logger.debug(f"Pulsar engine health check: {len(self.producers)} producers, {len(self.consumers)} consumers")
            
        except Exception as e:
            logger.error(f"Error performing maintenance: {e}")
    
    def get_engine_metrics(self) -> Dict[str, Any]:
        """Get comprehensive engine metrics"""
        try:
            metrics = {
                "producers": len(self.producers),
                "consumers": len(self.consumers),
                "geo_replication_managers": len(self.geo_replication_managers),
                "producer_metrics": {},
                "consumer_metrics": {},
                "replication_metrics": {}
            }
            
            # Producer metrics
            for topic, producer in self.producers.items():
                metrics["producer_metrics"][topic] = {
                    "messages_sent": producer.metrics.messages_sent,
                    "messages_failed": producer.metrics.messages_failed,
                    "bytes_sent": producer.metrics.bytes_sent,
                    "send_latency_ms": producer.metrics.producer_send_latency_ms,
                    "is_connected": producer._is_connected
                }
            
            # Consumer metrics
            for topic, consumer in self.consumers.items():
                metrics["consumer_metrics"][topic] = {
                    "messages_received": consumer.metrics.messages_received,
                    "messages_failed": consumer.metrics.messages_failed,
                    "bytes_received": consumer.metrics.bytes_received,
                    "receive_latency_ms": consumer.metrics.consumer_receive_latency_ms,
                    "is_connected": consumer._is_connected
                }
            
            # Replication metrics
            for cluster, geo_manager in self.geo_replication_managers.items():
                metrics["replication_metrics"][cluster] = geo_manager.replication_metrics
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting engine metrics: {e}")
            return {"error": str(e)}


# Export public API
__all__ = [
    "PulsarIntegrationEngine", "PulsarProducer", "PulsarConsumer",
    "PulsarProducerConfig", "PulsarConsumerConfig", "PulsarClusterConfig",
    "GeoReplicationManager", "GeoReplicationConfig", "AinflueBusinesPulsarTopics",
    "PulsarMessage", "PulsarMetrics", "PulsarCompressionType", "PulsarSubscriptionType",
    "ReplicationStrategy"
]