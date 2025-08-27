"""
IA Influencer Agent - Kafka Deployment Manager
Enterprise Kafka cluster management for high-throughput event streaming

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

STRICT WARNING: This code is proprietary and confidential.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Legal action will be taken against violators.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + DevOps 
- Audio Processing + Security + Microservices + IA Prompt Engineering
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

import docker
import yaml
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient, ConfigResource, ConfigResourceType, NewTopic
from kafka.errors import KafkaError
from pydantic import BaseModel, Field

from ...core.config import get_settings
from ...core.logging import get_logger
from ...monitoring.health_checker import HealthChecker

logger = get_logger(__name__)
settings = get_settings()


class KafkaBrokerConfig(BaseModel):
    """Configuration for Kafka broker"""
    id: int = Field(..., description="Broker ID")
    name: str = Field(..., description="Broker name")
    host: str = Field(..., description="Broker host")
    port: int = Field(default=9092, description="Kafka port")
    jmx_port: int = Field(default=9999, description="JMX port for monitoring")
    memory_limit: str = Field(default="4GB", description="Memory limit")
    storage_limit: str = Field(default="50GB", description="Storage limit")


class ZookeeperConfig(BaseModel):
    """Configuration for Zookeeper ensemble"""
    id: int = Field(..., description="Zookeeper ID")
    name: str = Field(..., description="Zookeeper name")
    host: str = Field(..., description="Zookeeper host")
    port: int = Field(default=2181, description="Client port")
    peer_port: int = Field(default=2888, description="Peer communication port")
    election_port: int = Field(default=3888, description="Leader election port")


class KafkaClusterConfig(BaseModel):
    """Configuration for Kafka cluster"""
    cluster_name: str = Field(default="ia-influencer-kafka", description="Cluster name")
    brokers: List[KafkaBrokerConfig] = Field(..., description="Kafka brokers")
    zookeepers: List[ZookeeperConfig] = Field(..., description="Zookeeper ensemble")
    replication_factor: int = Field(default=3, description="Default replication factor")
    min_insync_replicas: int = Field(default=2, description="Minimum in-sync replicas")
    retention_hours: int = Field(default=168, description="Default retention in hours (7 days)")
    compression_type: str = Field(default="snappy", description="Compression type")
    ssl_enabled: bool = Field(default=True, description="Enable SSL")
    sasl_enabled: bool = Field(default=True, description="Enable SASL authentication")
    monitoring_enabled: bool = Field(default=True, description="Enable monitoring")


class TopicConfig(BaseModel):
    """Configuration for Kafka topic"""
    name: str = Field(..., description="Topic name")
    partitions: int = Field(default=6, description="Number of partitions")
    replication_factor: int = Field(default=3, description="Replication factor")
    retention_ms: int = Field(default=604800000, description="Retention in milliseconds")
    compression_type: str = Field(default="snappy", description="Compression type")
    cleanup_policy: str = Field(default="delete", description="Cleanup policy")
    min_insync_replicas: int = Field(default=2, description="Minimum in-sync replicas")
    segment_ms: int = Field(default=86400000, description="Segment roll time")


class KafkaManager:
    """
    Enterprise Kafka cluster deployment and management system
    Handles high-throughput event streaming for IA content processing
    """

    def __init__(self, config: Optional[KafkaClusterConfig] = None):
        self.config = config or self._get_default_config()
        self.docker_client = docker.from_env()
        self.health_checker = HealthChecker()
        self.admin_client: Optional[AIOKafkaAdminClient] = None
        self.producer: Optional[AIOKafkaProducer] = None
        self.consumers: Dict[str, AIOKafkaConsumer] = {}
        self.monitoring_tasks: List[asyncio.Task] = []

    def _get_default_config(self) -> KafkaClusterConfig:
        """Get default Kafka cluster configuration"""
        return KafkaClusterConfig(
            cluster_name="ia-influencer-kafka",
            brokers=[
                KafkaBrokerConfig(
                    id=1,
                    name="kafka-broker-1",
                    host="kafka-1",
                    port=9092,
                    memory_limit="6GB"
                ),
                KafkaBrokerConfig(
                    id=2,
                    name="kafka-broker-2",
                    host="kafka-2",
                    port=9092,
                    memory_limit="6GB"
                ),
                KafkaBrokerConfig(
                    id=3,
                    name="kafka-broker-3",
                    host="kafka-3",
                    port=9092,
                    memory_limit="4GB"
                )
            ],
            zookeepers=[
                ZookeeperConfig(id=1, name="zookeeper-1", host="zk-1"),
                ZookeeperConfig(id=2, name="zookeeper-2", host="zk-2"),
                ZookeeperConfig(id=3, name="zookeeper-3", host="zk-3")
            ],
            replication_factor=3,
            min_insync_replicas=2,
            ssl_enabled=True,
            sasl_enabled=True,
            monitoring_enabled=True
        )

    async def deploy_cluster(self) -> Dict[str, Union[str, bool, int]]:
        """Deploy complete Kafka cluster"""
        try:
            logger.info("Starting Kafka cluster deployment")
            
            # Create Docker network
            await self._create_cluster_network()
            
            # Deploy Zookeeper ensemble first
            zk_results = await self._deploy_zookeeper_ensemble()
            
            # Wait for Zookeeper to be ready
            await asyncio.sleep(30)
            
            # Deploy Kafka brokers
            broker_results = await self._deploy_kafka_brokers()
            
            # Wait for Kafka to be ready
            await asyncio.sleep(45)
            
            # Setup admin client
            await self._setup_admin_client()
            
            # Create topics for IA processing
            await self._create_topics()
            
            # Setup producer and consumers
            await self._setup_producer()
            
            # Enable monitoring
            if self.config.monitoring_enabled:
                await self._enable_monitoring()
                
            logger.info("Kafka cluster deployed successfully")
            return {
                "status": "success",
                "zookeepers_deployed": len(zk_results),
                "brokers_deployed": len(broker_results),
                "ssl_enabled": self.config.ssl_enabled,
                "sasl_enabled": self.config.sasl_enabled,
                "monitoring_enabled": self.config.monitoring_enabled
            }
            
        except Exception as e:
            logger.error(f"Failed to deploy Kafka cluster: {e}")
            raise

    async def _create_cluster_network(self) -> None:
        """Create Docker network for cluster communication"""
        try:
            network_name = f"{self.config.cluster_name}-network"
            
            try:
                network = self.docker_client.networks.get(network_name)
                logger.info(f"Network {network_name} already exists")
            except docker.errors.NotFound:
                network = self.docker_client.networks.create(
                    name=network_name,
                    driver="bridge",
                    options={
                        "com.docker.network.bridge.enable_icc": "true",
                        "com.docker.network.bridge.enable_ip_masquerade": "true"
                    }
                )
                logger.info(f"Created network {network_name}")
                
        except Exception as e:
            logger.error(f"Failed to create cluster network: {e}")
            raise

    async def _deploy_zookeeper_ensemble(self) -> List[Dict[str, Union[str, int]]]:
        """Deploy Zookeeper ensemble"""
        try:
            deployment_results = []
            
            for zk_config in self.config.zookeepers:
                result = await self._deploy_zookeeper_node(zk_config)
                deployment_results.append(result)
                
            logger.info("Zookeeper ensemble deployed successfully")
            return deployment_results
            
        except Exception as e:
            logger.error(f"Failed to deploy Zookeeper ensemble: {e}")
            raise

    async def _deploy_zookeeper_node(self, zk_config: ZookeeperConfig) -> Dict[str, Union[str, int]]:
        """Deploy individual Zookeeper node"""
        try:
            # Generate Zookeeper configuration
            zoo_cfg = self._generate_zookeeper_config(zk_config)
            
            # Environment variables
            environment = {
                "ZOOKEEPER_CLIENT_PORT": str(zk_config.port),
                "ZOOKEEPER_TICK_TIME": "2000",
                "ZOOKEEPER_SYNC_LIMIT": "5",
                "ZOOKEEPER_INIT_LIMIT": "10",
                "ZOOKEEPER_MAX_CLIENT_CNXNS": "60",
                "ZOOKEEPER_AUTOPURGE_SNAP_RETAIN_COUNT": "3",
                "ZOOKEEPER_AUTOPURGE_PURGE_INTERVAL": "1",
                "ZOOKEEPER_SERVER_ID": str(zk_config.id)
            }
            
            # Add server list for ensemble
            for i, zk in enumerate(self.config.zookeepers, 1):
                environment[f"ZOOKEEPER_SERVER_{i}"] = f"{zk.host}:{zk.peer_port}:{zk.election_port}"
                
            # Create container
            container = self.docker_client.containers.run(
                image="confluentinc/cp-zookeeper:7.4.0",
                name=zk_config.name,
                hostname=zk_config.name,
                detach=True,
                environment=environment,
                ports={
                    f"{zk_config.port}/tcp": zk_config.port,
                    f"{zk_config.peer_port}/tcp": zk_config.peer_port,
                    f"{zk_config.election_port}/tcp": zk_config.election_port
                },
                volumes={
                    f"zookeeper-data-{zk_config.id}": {"bind": "/var/lib/zookeeper/data", "mode": "rw"},
                    f"zookeeper-logs-{zk_config.id}": {"bind": "/var/lib/zookeeper/log", "mode": "rw"}
                },
                networks=[f"{self.config.cluster_name}-network"],
                restart_policy={"Name": "unless-stopped"},
                mem_limit="2GB",
                healthcheck={
                    "test": ["CMD", "echo", "ruok", "|", "nc", "localhost", str(zk_config.port)],
                    "interval": 30000000000,  # 30s
                    "timeout": 10000000000,   # 10s
                    "retries": 3
                }
            )
            
            logger.info(f"Zookeeper node {zk_config.name} deployed successfully")
            return {
                "container_id": container.id[:12],
                "name": zk_config.name,
                "host": zk_config.host,
                "port": zk_config.port,
                "status": "running"
            }
            
        except Exception as e:
            logger.error(f"Failed to deploy Zookeeper node {zk_config.name}: {e}")
            raise

    def _generate_zookeeper_config(self, zk_config: ZookeeperConfig) -> str:
        """Generate Zookeeper configuration"""
        config_lines = [
            f"tickTime=2000",
            f"initLimit=10",
            f"syncLimit=5",
            f"dataDir=/var/lib/zookeeper/data",
            f"dataLogDir=/var/lib/zookeeper/log",
            f"clientPort={zk_config.port}",
            f"maxClientCnxns=60",
            f"autopurge.snapRetainCount=3",
            f"autopurge.purgeInterval=1"
        ]
        
        # Add server list for ensemble
        for zk in self.config.zookeepers:
            config_lines.append(f"server.{zk.id}={zk.host}:{zk.peer_port}:{zk.election_port}")
            
        return "\n".join(config_lines)

    async def _deploy_kafka_brokers(self) -> List[Dict[str, Union[str, int]]]:
        """Deploy Kafka brokers"""
        try:
            deployment_results = []
            
            for broker_config in self.config.brokers:
                result = await self._deploy_kafka_broker(broker_config)
                deployment_results.append(result)
                
            logger.info("Kafka brokers deployed successfully")
            return deployment_results
            
        except Exception as e:
            logger.error(f"Failed to deploy Kafka brokers: {e}")
            raise

    async def _deploy_kafka_broker(self, broker_config: KafkaBrokerConfig) -> Dict[str, Union[str, int]]:
        """Deploy individual Kafka broker"""
        try:
            # Build Zookeeper connection string
            zk_connect = ",".join([f"{zk.host}:{zk.port}" for zk in self.config.zookeepers])
            
            # Environment variables
            environment = {
                "KAFKA_BROKER_ID": str(broker_config.id),
                "KAFKA_ZOOKEEPER_CONNECT": zk_connect,
                "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP": "PLAINTEXT:PLAINTEXT,SSL:SSL,SASL_SSL:SASL_SSL",
                "KAFKA_ADVERTISED_LISTENERS": f"PLAINTEXT://{broker_config.host}:{broker_config.port}",
                "KAFKA_LISTENERS": f"PLAINTEXT://0.0.0.0:{broker_config.port}",
                "KAFKA_INTER_BROKER_LISTENER_NAME": "PLAINTEXT",
                "KAFKA_NUM_NETWORK_THREADS": "8",
                "KAFKA_NUM_IO_THREADS": "8",
                "KAFKA_SOCKET_SEND_BUFFER_BYTES": "102400",
                "KAFKA_SOCKET_RECEIVE_BUFFER_BYTES": "102400",
                "KAFKA_SOCKET_REQUEST_MAX_BYTES": "104857600",
                "KAFKA_NUM_PARTITIONS": "6",
                "KAFKA_NUM_RECOVERY_THREADS_PER_DATA_DIR": "1",
                "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR": str(self.config.replication_factor),
                "KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR": str(self.config.replication_factor),
                "KAFKA_TRANSACTION_STATE_LOG_MIN_ISR": str(self.config.min_insync_replicas),
                "KAFKA_DEFAULT_REPLICATION_FACTOR": str(self.config.replication_factor),
                "KAFKA_MIN_INSYNC_REPLICAS": str(self.config.min_insync_replicas),
                "KAFKA_LOG_RETENTION_HOURS": str(self.config.retention_hours),
                "KAFKA_LOG_SEGMENT_BYTES": "1073741824",
                "KAFKA_LOG_RETENTION_CHECK_INTERVAL_MS": "300000",
                "KAFKA_COMPRESSION_TYPE": self.config.compression_type,
                "KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS": "3000",
                "KAFKA_JMX_PORT": str(broker_config.jmx_port),
                "KAFKA_JMX_HOSTNAME": broker_config.host,
                "KAFKA_HEAP_OPTS": "-Xmx3G -Xms3G"
            }
            
            # SSL configuration
            if self.config.ssl_enabled:
                environment.update({
                    "KAFKA_SSL_KEYSTORE_LOCATION": "/etc/kafka/ssl/kafka.server.keystore.jks",
                    "KAFKA_SSL_KEYSTORE_PASSWORD": "kafka-password",
                    "KAFKA_SSL_KEY_PASSWORD": "kafka-password",
                    "KAFKA_SSL_TRUSTSTORE_LOCATION": "/etc/kafka/ssl/kafka.server.truststore.jks",
                    "KAFKA_SSL_TRUSTSTORE_PASSWORD": "kafka-password",
                    "KAFKA_SSL_CLIENT_AUTH": "required"
                })
                
            # SASL configuration
            if self.config.sasl_enabled:
                environment.update({
                    "KAFKA_SASL_ENABLED_MECHANISMS": "PLAIN,SCRAM-SHA-256",
                    "KAFKA_SASL_MECHANISM_INTER_BROKER_PROTOCOL": "SCRAM-SHA-256"
                })
                
            # Create container
            container = self.docker_client.containers.run(
                image="confluentinc/cp-kafka:7.4.0",
                name=broker_config.name,
                hostname=broker_config.name,
                detach=True,
                environment=environment,
                ports={
                    f"{broker_config.port}/tcp": broker_config.port,
                    f"{broker_config.jmx_port}/tcp": broker_config.jmx_port
                },
                volumes={
                    f"kafka-data-{broker_config.id}": {"bind": "/var/lib/kafka/data", "mode": "rw"},
                    "/app/config/kafka/ssl": {"bind": "/etc/kafka/ssl", "mode": "ro"}
                },
                networks=[f"{self.config.cluster_name}-network"],
                restart_policy={"Name": "unless-stopped"},
                mem_limit=broker_config.memory_limit,
                healthcheck={
                    "test": ["CMD", "kafka-broker-api-versions", "--bootstrap-server", f"localhost:{broker_config.port}"],
                    "interval": 30000000000,  # 30s
                    "timeout": 10000000000,   # 10s
                    "retries": 5
                }
            )
            
            logger.info(f"Kafka broker {broker_config.name} deployed successfully")
            return {
                "container_id": container.id[:12],
                "name": broker_config.name,
                "host": broker_config.host,
                "port": broker_config.port,
                "broker_id": broker_config.id,
                "status": "running"
            }
            
        except Exception as e:
            logger.error(f"Failed to deploy Kafka broker {broker_config.name}: {e}")
            raise

    async def _setup_admin_client(self) -> None:
        """Setup Kafka admin client"""
        try:
            bootstrap_servers = [f"{broker.host}:{broker.port}" for broker in self.config.brokers]
            
            self.admin_client = AIOKafkaAdminClient(
                bootstrap_servers=bootstrap_servers,
                client_id="ia-influencer-admin"
            )
            
            await self.admin_client.start()
            logger.info("Kafka admin client setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup admin client: {e}")
            raise

    async def _create_topics(self) -> None:
        """Create topics for IA content processing"""
        try:
            topics_config = self._get_topics_config()
            
            new_topics = []
            for topic_config in topics_config:
                new_topic = NewTopic(
                    name=topic_config.name,
                    num_partitions=topic_config.partitions,
                    replication_factor=topic_config.replication_factor,
                    topic_configs={
                        "retention.ms": str(topic_config.retention_ms),
                        "compression.type": topic_config.compression_type,
                        "cleanup.policy": topic_config.cleanup_policy,
                        "min.insync.replicas": str(topic_config.min_insync_replicas),
                        "segment.ms": str(topic_config.segment_ms)
                    }
                )
                new_topics.append(new_topic)
                
            # Create topics
            await self.admin_client.create_topics(new_topics, validate_only=False)
            
            logger.info(f"Created {len(new_topics)} topics for IA processing")
            
        except Exception as e:
            logger.error(f"Failed to create topics: {e}")
            raise

    def _get_topics_config(self) -> List[TopicConfig]:
        """Get topic configurations for IA processing pipeline"""
        return [
            # Content processing topics
            TopicConfig(
                name="ia.content.uploads",
                partitions=12,
                retention_ms=2592000000,  # 30 days
                compression_type="lz4"
            ),
            TopicConfig(
                name="ia.content.fingerprints",
                partitions=8,
                retention_ms=7776000000,  # 90 days
                compression_type="snappy"
            ),
            TopicConfig(
                name="ia.content.analysis",
                partitions=6,
                retention_ms=1209600000,  # 14 days
                compression_type="gzip"
            ),
            TopicConfig(
                name="ia.content.protection",
                partitions=4,
                retention_ms=15552000000,  # 180 days
                compression_type="snappy"
            ),
            
            # AI processing topics
            TopicConfig(
                name="ia.ai.inference.requests",
                partitions=8,
                retention_ms=604800000,  # 7 days
                compression_type="lz4"
            ),
            TopicConfig(
                name="ia.ai.inference.results",
                partitions=8,
                retention_ms=2592000000,  # 30 days
                compression_type="snappy"
            ),
            TopicConfig(
                name="ia.ai.training.data",
                partitions=4,
                retention_ms=31536000000,  # 1 year
                compression_type="gzip"
            ),
            
            # Monitoring and alerts topics
            TopicConfig(
                name="ia.monitoring.events",
                partitions=6,
                retention_ms=2592000000,  # 30 days
                compression_type="snappy"
            ),
            TopicConfig(
                name="ia.alerts.violations",
                partitions=3,
                retention_ms=7776000000,  # 90 days
                compression_type="lz4"
            ),
            TopicConfig(
                name="ia.alerts.notifications",
                partitions=3,
                retention_ms=1209600000,  # 14 days
                compression_type="snappy"
            ),
            
            # Crawling and web monitoring topics
            TopicConfig(
                name="ia.crawling.tasks",
                partitions=10,
                retention_ms=604800000,  # 7 days
                compression_type="lz4"
            ),
            TopicConfig(
                name="ia.crawling.results",
                partitions=10,
                retention_ms=2592000000,  # 30 days
                compression_type="snappy"
            ),
            TopicConfig(
                name="ia.social.monitoring",
                partitions=8,
                retention_ms=2592000000,  # 30 days
                compression_type="snappy"
            ),
            
            # Revenue and monetization topics
            TopicConfig(
                name="ia.revenue.events",
                partitions=4,
                retention_ms=31536000000,  # 1 year
                compression_type="gzip"
            ),
            TopicConfig(
                name="ia.payments.transactions",
                partitions=6,
                retention_ms=94608000000,  # 3 years
                compression_type="gzip"
            ),
            TopicConfig(
                name="ia.analytics.metrics",
                partitions=8,
                retention_ms=7776000000,  # 90 days
                compression_type="snappy"
            ),
            
            # System and operational topics
            TopicConfig(
                name="ia.system.logs",
                partitions=6,
                retention_ms=1209600000,  # 14 days
                compression_type="gzip"
            ),
            TopicConfig(
                name="ia.system.metrics",
                partitions=4,
                retention_ms=2592000000,  # 30 days
                compression_type="snappy"
            ),
            TopicConfig(
                name="ia.audit.events",
                partitions=3,
                retention_ms=94608000000,  # 3 years
                compression_type="gzip"
            )
        ]

    async def _setup_producer(self) -> None:
        """Setup Kafka producer for high-throughput messaging"""
        try:
            bootstrap_servers = [f"{broker.host}:{broker.port}" for broker in self.config.brokers]
            
            self.producer = AIOKafkaProducer(
                bootstrap_servers=bootstrap_servers,
                client_id="ia-influencer-producer",
                compression_type=self.config.compression_type,
                max_batch_size=1048576,  # 1MB
                linger_ms=10,
                acks="all",
                retries=5,
                retry_backoff_ms=1000,
                request_timeout_ms=30000,
                enable_idempotence=True
            )
            
            await self.producer.start()
            logger.info("Kafka producer setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup producer: {e}")
            raise

    async def _enable_monitoring(self) -> None:
        """Enable cluster monitoring and metrics collection"""
        try:
            # Start cluster health monitoring
            health_task = asyncio.create_task(self._monitor_cluster_health())
            self.monitoring_tasks.append(health_task)
            
            # Start performance monitoring
            perf_task = asyncio.create_task(self._monitor_performance())
            self.monitoring_tasks.append(perf_task)
            
            # Start topic monitoring
            topic_task = asyncio.create_task(self._monitor_topics())
            self.monitoring_tasks.append(topic_task)
            
            logger.info("Kafka cluster monitoring enabled")
            
        except Exception as e:
            logger.error(f"Failed to enable monitoring: {e}")
            raise

    async def _monitor_cluster_health(self) -> None:
        """Monitor cluster health continuously"""
        while True:
            try:
                # Check Zookeeper nodes
                for zk_config in self.config.zookeepers:
                    container = self.docker_client.containers.get(zk_config.name)
                    container.reload()
                    
                    if container.status != "running":
                        logger.warning(f"Zookeeper node {zk_config.name} is not running")
                        
                # Check Kafka brokers
                for broker_config in self.config.brokers:
                    container = self.docker_client.containers.get(broker_config.name)
                    container.reload()
                    
                    if container.status != "running":
                        logger.warning(f"Kafka broker {broker_config.name} is not running")
                        
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in cluster health monitoring: {e}")
                await asyncio.sleep(60)

    async def _monitor_performance(self) -> None:
        """Monitor cluster performance metrics"""
        while True:
            try:
                # Get cluster metadata
                metadata = await self.producer.client.cluster
                
                # Monitor broker performance
                for broker in metadata.brokers:
                    # This would integrate with JMX metrics
                    logger.debug(f"Monitoring broker {broker.nodeId} at {broker.host}:{broker.port}")
                    
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(120)

    async def _monitor_topics(self) -> None:
        """Monitor topic metrics and health"""
        while True:
            try:
                # Get topic metadata
                metadata = await self.admin_client.describe_topics()
                
                for topic_name, topic_metadata in metadata.items():
                    # Monitor partition health
                    for partition in topic_metadata.partitions:
                        if len(partition.replicas) < self.config.replication_factor:
                            logger.warning(f"Topic {topic_name} partition {partition.partition} under-replicated")
                            
                await asyncio.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                logger.error(f"Error in topic monitoring: {e}")
                await asyncio.sleep(180)

    async def publish_event(self, topic: str, key: str, value: Dict, partition: Optional[int] = None) -> bool:
        """Publish event to Kafka topic"""
        try:
            if not self.producer:
                raise ValueError("Producer not initialized")
                
            # Serialize value
            serialized_value = json.dumps(value).encode()
            serialized_key = key.encode() if key else None
            
            # Send message
            await self.producer.send(
                topic=topic,
                key=serialized_key,
                value=serialized_value,
                partition=partition
            )
            
            logger.debug(f"Published event to topic {topic} with key {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False

    async def create_consumer(self, topics: List[str], group_id: str) -> AIOKafkaConsumer:
        """Create Kafka consumer for specified topics"""
        try:
            bootstrap_servers = [f"{broker.host}:{broker.port}" for broker in self.config.brokers]
            
            consumer = AIOKafkaConsumer(
                *topics,
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                client_id=f"ia-influencer-consumer-{group_id}",
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                auto_commit_interval_ms=5000,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000,
                max_poll_interval_ms=300000,
                max_poll_records=500
            )
            
            await consumer.start()
            self.consumers[group_id] = consumer
            
            logger.info(f"Created consumer for topics {topics} with group {group_id}")
            return consumer
            
        except Exception as e:
            logger.error(f"Failed to create consumer: {e}")
            raise

    async def get_cluster_status(self) -> Dict[str, Union[str, int, List[Dict]]]:
        """Get comprehensive cluster status"""
        try:
            # Check Zookeeper status
            zk_statuses = []
            for zk_config in self.config.zookeepers:
                try:
                    container = self.docker_client.containers.get(zk_config.name)
                    container.reload()
                    
                    zk_statuses.append({
                        "name": zk_config.name,
                        "status": container.status,
                        "host": zk_config.host,
                        "port": zk_config.port
                    })
                except docker.errors.NotFound:
                    zk_statuses.append({
                        "name": zk_config.name,
                        "status": "not_found"
                    })
                    
            # Check Kafka broker status
            broker_statuses = []
            for broker_config in self.config.brokers:
                try:
                    container = self.docker_client.containers.get(broker_config.name)
                    container.reload()
                    
                    broker_statuses.append({
                        "name": broker_config.name,
                        "broker_id": broker_config.id,
                        "status": container.status,
                        "host": broker_config.host,
                        "port": broker_config.port
                    })
                except docker.errors.NotFound:
                    broker_statuses.append({
                        "name": broker_config.name,
                        "broker_id": broker_config.id,
                        "status": "not_found"
                    })
                    
            # Get cluster stats
            cluster_stats = await self._get_cluster_stats()
            
            return {
                "cluster_status": "healthy" if all(z["status"] == "running" for z in zk_statuses) and all(b["status"] == "running" for b in broker_statuses) else "degraded",
                "zookeeper_nodes": len(self.config.zookeepers),
                "kafka_brokers": len(self.config.brokers),
                "ssl_enabled": self.config.ssl_enabled,
                "sasl_enabled": self.config.sasl_enabled,
                "monitoring_enabled": self.config.monitoring_enabled,
                "zookeepers": zk_statuses,
                "brokers": broker_statuses,
                "cluster_stats": cluster_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to get cluster status: {e}")
            return {"cluster_status": "error", "error": str(e)}

    async def _get_cluster_stats(self) -> Dict[str, Union[int, float]]:
        """Get cluster statistics"""
        try:
            # This would integrate with JMX metrics and Kafka APIs
            # For now, return mock data
            return {
                "total_topics": 19,
                "total_partitions": 128,
                "total_producers": 8,
                "total_consumers": 12,
                "messages_per_second": 2500.5,
                "bytes_in_per_second": 1048576.0,
                "bytes_out_per_second": 2097152.0,
                "active_controller_count": 1,
                "under_replicated_partitions": 0,
                "offline_partitions": 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get cluster stats: {e}")
            return {}

    async def shutdown_cluster(self) -> Dict[str, Union[str, bool]]:
        """Gracefully shutdown the cluster"""
        try:
            logger.info("Starting Kafka cluster shutdown")
            
            # Stop monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
                
            # Stop consumers
            for consumer in self.consumers.values():
                await consumer.stop()
                
            # Stop producer
            if self.producer:
                await self.producer.stop()
                
            # Stop admin client
            if self.admin_client:
                await self.admin_client.close()
                
            # Stop Kafka brokers
            for broker_config in self.config.brokers:
                try:
                    container = self.docker_client.containers.get(broker_config.name)
                    container.stop(timeout=30)
                    container.remove()
                except docker.errors.NotFound:
                    pass
                    
            # Stop Zookeeper nodes
            for zk_config in self.config.zookeepers:
                try:
                    container = self.docker_client.containers.get(zk_config.name)
                    container.stop(timeout=30)
                    container.remove()
                except docker.errors.NotFound:
                    pass
                    
            logger.info("Kafka cluster shutdown completed")
            return {"status": "success", "message": "Cluster shutdown completed"}
            
        except Exception as e:
            logger.error(f"Error during cluster shutdown: {e}")
            return {"status": "error", "error": str(e)}

    def export_cluster_config(self) -> Dict:
        """Export current cluster configuration"""
        return {
            "cluster_config": self.config.dict(),
            "deployment_timestamp": time.time(),
            "zookeeper_nodes": len(self.config.zookeepers),
            "kafka_brokers": len(self.config.brokers),
            "ssl_enabled": self.config.ssl_enabled,
            "sasl_enabled": self.config.sasl_enabled
        }

    @classmethod
    def from_config_file(cls, config_path: str) -> "KafkaManager":
        """Create KafkaManager from configuration file"""
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        config = KafkaClusterConfig(**config_data)
        return cls(config)
