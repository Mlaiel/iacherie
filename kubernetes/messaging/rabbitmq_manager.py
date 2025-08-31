"""IA Influencer Agent - RabbitMQ Deployment Manager
Enterprise RabbitMQ cluster management for high-performance messaging

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

STRICT WARNING: This code is proprietary and confidential.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Legal action will be taken against violators.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + DevOps 
- Audio Processing + Security + Microservices + IA Prompt Engineering
"""import asyncio
import json
import logging
import ssl
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

import aio_pika
import docker
import yaml
from aio_pika import Connection, Exchange, Message, Queue
from aio_pika.pool import Pool
from pydantic import BaseModel, Field

from ...core.config import get_settings
from ...core.logging import get_logger
from ...monitoring.health_checker import HealthChecker

logger = get_logger(__name__)
settings = get_settings()


class RabbitMQNodeConfig(BaseModel):
    """Configuration for RabbitMQ cluster node"""    name: str = Field(..., description="Node name identifier")
    host: str = Field(default="localhost", description="Node host address")
    port: int = Field(default=5672, description="AMQP port")
    management_port: int = Field(default=15672, description="Management UI port")
    memory_limit: str = Field(default="2GB", description="Memory limit")
    disk_limit: str = Field(default="10GB", description="Disk limit")
    node_type: str = Field(default="disc", description="Node type: disc or ram")


class RabbitMQClusterConfig(BaseModel):
    """Configuration for RabbitMQ cluster"""    cluster_name: str = Field(default="ia-influencer-rabbitmq", description="Cluster name")
    nodes: List[RabbitMQNodeConfig] = Field(..., description="Cluster nodes")
    username: str = Field(default="ia_admin", description="Admin username")
    password: str = Field(..., description="Admin password")
    virtual_host: str = Field(default="/ia_influencer", description="Virtual host")
    ssl_enabled: bool = Field(default=True, description="Enable SSL/TLS")
    high_availability: bool = Field(default=True, description="Enable HA queues")
    federation_enabled: bool = Field(default=False, description="Enable federation")
    monitoring_enabled: bool = Field(default=True, description="Enable monitoring")


class ExchangeConfig(BaseModel):
    """Configuration for RabbitMQ exchange"""    name: str = Field(..., description="Exchange name")
    type: str = Field(default="topic", description="Exchange type")
    durable: bool = Field(default=True, description="Durable exchange")
    auto_delete: bool = Field(default=False, description="Auto-delete exchange")
    arguments: Dict = Field(default_factory=dict, description="Exchange arguments")


class QueueConfig(BaseModel):
    """Configuration for RabbitMQ queue"""    name: str = Field(..., description="Queue name")
    durable: bool = Field(default=True, description="Durable queue")
    exclusive: bool = Field(default=False, description="Exclusive queue")
    auto_delete: bool = Field(default=False, description="Auto-delete queue")
    arguments: Dict = Field(default_factory=dict, description="Queue arguments")
    routing_keys: List[str] = Field(default_factory=list, description="Routing keys")
    dead_letter_exchange: Optional[str] = Field(None, description="Dead letter exchange")
    message_ttl: Optional[int] = Field(None, description="Message TTL in ms")
    max_length: Optional[int] = Field(None, description="Maximum queue length")


class RabbitMQManager:
    """    Enterprise RabbitMQ cluster deployment and management system
    Handles high-performance messaging for IA content processing pipeline
    """    def __init__(self, config: Optional[RabbitMQClusterConfig] = None):
        self.config = config or self._get_default_config()
        self.docker_client = docker.from_env()
        self.health_checker = HealthChecker()
        self.connections: Dict[str, Connection] = {}
        self.connection_pool: Optional[Pool] = None
        self.exchanges: Dict[str, Exchange] = {}
        self.queues: Dict[str, Queue] = {}
        self.monitoring_tasks: List[asyncio.Task] = []

    def _get_default_config(self) -> RabbitMQClusterConfig:
        """Get default RabbitMQ cluster configuration"""        return RabbitMQClusterConfig(
            cluster_name="ia-influencer-rabbitmq",
            nodes=[
                RabbitMQNodeConfig(
                    name="rabbit-node-1",
                    host="rabbitmq-1",
                    port=5672,
                    memory_limit="4GB",
                    node_type="disc"
                ),
                RabbitMQNodeConfig(
                    name="rabbit-node-2", 
                    host="rabbitmq-2",
                    port=5672,
                    memory_limit="4GB",
                    node_type="disc"
                ),
                RabbitMQNodeConfig(
                    name="rabbit-node-3",
                    host="rabbitmq-3", 
                    port=5672,
                    memory_limit="2GB",
                    node_type="ram"
                )
            ],
            password=settings.RABBITMQ_PASSWORD,
            ssl_enabled=True,
            high_availability=True,
            monitoring_enabled=True
        )

    async def deploy_cluster(self) -> Dict[str, Union[str, bool, int]]:
        """Deploy complete RabbitMQ cluster"""        try:
            logger.info("Starting RabbitMQ cluster deployment")
            
            # Create Docker network
            await self._create_cluster_network()
            
            # Deploy cluster nodes
            deployment_results = {}
            for node_config in self.config.nodes:
                result = await self._deploy_node(node_config)
                deployment_results[node_config.name] = result
                
            # Wait for nodes to start
            await asyncio.sleep(30)
            
            # Form cluster
            await self._form_cluster()
            
            # Configure virtual host and permissions
            await self._configure_virtual_host()
            
            # Setup exchanges and queues
            await self._setup_messaging_topology()
            
            # Enable monitoring
            if self.config.monitoring_enabled:
                await self._enable_monitoring()
                
            # Setup connection pool
            await self._setup_connection_pool()
                
            logger.info(f"RabbitMQ cluster deployed successfully: {deployment_results}")
            return {
                "status": "success",
                "nodes_deployed": len(deployment_results),
                "cluster_formed": True,
                "monitoring_enabled": self.config.monitoring_enabled,
                "ssl_enabled": self.config.ssl_enabled
            }
            
        except Exception as e:
            logger.error(f"Failed to deploy RabbitMQ cluster: {e}")
            raise

    async def _create_cluster_network(self) -> None:
        """Create Docker network for cluster communication"""        try:
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

    async def _deploy_node(self, node_config: RabbitMQNodeConfig) -> Dict[str, Union[str, int]]:
        """Deploy individual RabbitMQ node"""        try:
            # Generate Erlang cookie for cluster
            erlang_cookie = self._generate_erlang_cookie()
            
            # Environment variables
            environment = {
                "RABBITMQ_DEFAULT_USER": self.config.username,
                "RABBITMQ_DEFAULT_PASS": self.config.password,
                "RABBITMQ_DEFAULT_VHOST": self.config.virtual_host,
                "RABBITMQ_ERLANG_COOKIE": erlang_cookie,
                "RABBITMQ_NODE_TYPE": node_config.node_type,
                "RABBITMQ_VM_MEMORY_HIGH_WATERMARK": "0.8",
                "RABBITMQ_DISK_FREE_LIMIT": "2GB"
            }
            
            # SSL configuration
            if self.config.ssl_enabled:
                environment.update({
                    "RABBITMQ_SSL_CERTFILE": "/etc/rabbitmq/ssl/cert.pem",
                    "RABBITMQ_SSL_KEYFILE": "/etc/rabbitmq/ssl/key.pem",
                    "RABBITMQ_SSL_CACERTFILE": "/etc/rabbitmq/ssl/ca.pem"
                })
            
            # Create container
            container = self.docker_client.containers.run(
                image="rabbitmq:3.12-management-alpine",
                name=node_config.name,
                hostname=node_config.name,
                detach=True,
                environment=environment,
                ports={
                    f"{node_config.port}/tcp": node_config.port,
                    f"{node_config.management_port}/tcp": node_config.management_port,
                    "25672/tcp": 25672  # Inter-node communication
                },
                volumes={
                    f"rabbitmq-data-{node_config.name}": {"bind": "/var/lib/rabbitmq", "mode": "rw"},
                    "/app/config/rabbitmq": {"bind": "/etc/rabbitmq", "mode": "ro"}
                },
                networks=[f"{self.config.cluster_name}-network"],
                restart_policy={"Name": "unless-stopped"},
                mem_limit=node_config.memory_limit,
                healthcheck={
                    "test": ["CMD", "rabbitmq-diagnostics", "ping"],
                    "interval": 30000000000,  # 30s in nanoseconds
                    "timeout": 10000000000,   # 10s in nanoseconds
                    "retries": 3
                }
            )
            
            logger.info(f"RabbitMQ node {node_config.name} deployed successfully")
            return {
                "container_id": container.id[:12],
                "status": "running",
                "host": node_config.host,
                "port": node_config.port,
                "management_port": node_config.management_port
            }
            
        except Exception as e:
            logger.error(f"Failed to deploy node {node_config.name}: {e}")
            raise

    def _generate_erlang_cookie(self) -> str:
        """Generate Erlang cookie for cluster communication"""        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))

    async def _form_cluster(self) -> None:
        """Form RabbitMQ cluster from deployed nodes"""        try:
            if len(self.config.nodes) < 2:
                logger.info("Single node deployment, skipping cluster formation")
                return
                
            # Use first node as primary
            primary_node = self.config.nodes[0]
            
            # Join other nodes to cluster
            for node_config in self.config.nodes[1:]:
                await self._join_node_to_cluster(node_config, primary_node)
                
            logger.info("RabbitMQ cluster formed successfully")
            
        except Exception as e:
            logger.error(f"Failed to form cluster: {e}")
            raise

    async def _join_node_to_cluster(self, node_config: RabbitMQNodeConfig, primary_node: RabbitMQNodeConfig) -> None:
        """Join a node to the cluster"""        try:
            # Execute cluster join commands in container
            container = self.docker_client.containers.get(node_config.name)
            
            # Stop RabbitMQ app
            container.exec_run("rabbitmqctl stop_app")
            
            # Reset node
            container.exec_run("rabbitmqctl reset")
            
            # Join cluster
            join_cmd = f"rabbitmqctl join_cluster rabbit@{primary_node.name}"
            result = container.exec_run(join_cmd)
            
            if result.exit_code != 0:
                raise Exception(f"Failed to join cluster: {result.output.decode()}")
                
            # Start RabbitMQ app
            container.exec_run("rabbitmqctl start_app")
            
            logger.info(f"Node {node_config.name} joined cluster successfully")
            
        except Exception as e:
            logger.error(f"Failed to join node {node_config.name} to cluster: {e}")
            raise

    async def _configure_virtual_host(self) -> None:
        """Configure virtual host and user permissions"""        try:
            # Get primary node container
            primary_node = self.config.nodes[0]
            container = self.docker_client.containers.get(primary_node.name)
            
            # Create virtual host if not exists
            vhost_cmd = f"rabbitmqctl add_vhost {self.config.virtual_host}"
            container.exec_run(vhost_cmd)
            
            # Set permissions for admin user
            perms_cmd = f"rabbitmqctl set_permissions -p {self.config.virtual_host} {self.config.username} '.*' '.*' '.*'"
            container.exec_run(perms_cmd)
            
            # Enable management plugin
            container.exec_run("rabbitmq-plugins enable rabbitmq_management")
            
            # Set admin tag
            tag_cmd = f"rabbitmqctl set_user_tags {self.config.username} administrator"
            container.exec_run(tag_cmd)
            
            logger.info("Virtual host and permissions configured")
            
        except Exception as e:
            logger.error(f"Failed to configure virtual host: {e}")
            raise

    async def _setup_messaging_topology(self) -> None:
        """Setup exchanges, queues, and bindings for IA processing"""        try:
            # Connect to RabbitMQ
            connection = await self._get_connection()
            channel = await connection.channel()
            
            # Define exchanges for IA processing pipeline
            exchanges_config = self._get_exchanges_config()
            for exchange_config in exchanges_config:
                exchange = await self._declare_exchange(channel, exchange_config)
                self.exchanges[exchange_config.name] = exchange
                
            # Define queues for different processing stages
            queues_config = self._get_queues_config()
            for queue_config in queues_config:
                queue = await self._declare_queue(channel, queue_config)
                self.queues[queue_config.name] = queue
                
                # Bind queue to exchanges
                for routing_key in queue_config.routing_keys:
                    await queue.bind(self.exchanges["ia.content"], routing_key)
                    
            logger.info("Messaging topology setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup messaging topology: {e}")
            raise

    def _get_exchanges_config(self) -> List[ExchangeConfig]:
        """Get exchange configurations for IA processing"""        return [
            ExchangeConfig(
                name="ia.content",
                type="topic",
                durable=True,
                arguments={"alternate-exchange": "ia.deadletter"}
            ),
            ExchangeConfig(
                name="ia.notifications",
                type="direct",
                durable=True
            ),
            ExchangeConfig(
                name="ia.monitoring",
                type="fanout",
                durable=True
            ),
            ExchangeConfig(
                name="ia.deadletter",
                type="fanout",
                durable=True
            )
        ]

    def _get_queues_config(self) -> List[QueueConfig]:
        """Get queue configurations for IA processing pipeline"""        base_arguments = {
            "x-message-ttl": 3600000,  # 1 hour TTL
            "x-max-length": 10000,     # Max 10k messages
            "x-dead-letter-exchange": "ia.deadletter"
        }
        
        if self.config.high_availability:
            base_arguments["x-ha-policy"] = "all"
            
        return [
            # Content processing queues
            QueueConfig(
                name="ia.content.upload",
                arguments=base_arguments,
                routing_keys=["content.upload.*", "content.new.*"]
            ),
            QueueConfig(
                name="ia.content.fingerprint",
                arguments=base_arguments,
                routing_keys=["content.fingerprint.*", "fingerprint.generate.*"]
            ),
            QueueConfig(
                name="ia.content.analysis",
                arguments=base_arguments,
                routing_keys=["content.analysis.*", "ai.analyze.*"]
            ),
            QueueConfig(
                name="ia.content.protection",
                arguments=base_arguments,
                routing_keys=["content.protection.*", "protect.*"]
            ),
            
            # AI processing queues
            QueueConfig(
                name="ia.ai.inference",
                arguments={**base_arguments, "x-max-priority": 10},
                routing_keys=["ai.inference.*", "ml.predict.*"]
            ),
            QueueConfig(
                name="ia.ai.training",
                arguments={**base_arguments, "x-message-ttl": 86400000},  # 24h TTL
                routing_keys=["ai.training.*", "ml.train.*"]
            ),
            
            # Monitoring and crawling queues
            QueueConfig(
                name="ia.crawling.web",
                arguments=base_arguments,
                routing_keys=["crawling.web.*", "monitor.scan.*"]
            ),
            QueueConfig(
                name="ia.crawling.social",
                arguments=base_arguments,
                routing_keys=["crawling.social.*", "social.scan.*"]
            ),
            
            # Notification queues
            QueueConfig(
                name="ia.notifications.alerts",
                arguments={**base_arguments, "x-max-priority": 5},
                routing_keys=["notification.alert.*", "alert.*"]
            ),
            QueueConfig(
                name="ia.notifications.email",
                arguments=base_arguments,
                routing_keys=["notification.email.*", "email.*"]
            ),
            
            # Revenue and monetization queues
            QueueConfig(
                name="ia.revenue.calculation",
                arguments=base_arguments,
                routing_keys=["revenue.calculate.*", "monetization.*"]
            ),
            QueueConfig(
                name="ia.payment.processing",
                arguments={**base_arguments, "x-max-priority": 8},
                routing_keys=["payment.process.*", "payout.*"]
            ),
            
            # Dead letter queue
            QueueConfig(
                name="ia.deadletter.queue",
                arguments={"x-message-ttl": 604800000},  # 7 days TTL
                routing_keys=[]
            )
        ]

    async def _declare_exchange(self, channel, config: ExchangeConfig) -> Exchange:
        """Declare an exchange with configuration"""        exchange = await channel.declare_exchange(
            name=config.name,
            type=config.type,
            durable=config.durable,
            auto_delete=config.auto_delete,
            arguments=config.arguments
        )
        
        logger.info(f"Declared exchange: {config.name}")
        return exchange

    async def _declare_queue(self, channel, config: QueueConfig) -> Queue:
        """Declare a queue with configuration"""        queue = await channel.declare_queue(
            name=config.name,
            durable=config.durable,
            exclusive=config.exclusive,
            auto_delete=config.auto_delete,
            arguments=config.arguments
        )
        
        logger.info(f"Declared queue: {config.name}")
        return queue

    async def _get_connection(self) -> Connection:
        """Get connection to RabbitMQ cluster"""        try:
            if self.connection_pool:
                return await self.connection_pool.acquire()
                
            # Build connection URL
            primary_node = self.config.nodes[0]
            protocol = "amqps" if self.config.ssl_enabled else "amqp"
            url = f"{protocol}://{self.config.username}:{self.config.password}@{primary_node.host}:{primary_node.port}{self.config.virtual_host}"
            
            connection = await aio_pika.connect_robust(url)
            return connection
            
        except Exception as e:
            logger.error(f"Failed to get RabbitMQ connection: {e}")
            raise

    async def _setup_connection_pool(self) -> None:
        """Setup connection pool for high-performance messaging"""        try:
            async def get_connection():
                primary_node = self.config.nodes[0]
                protocol = "amqps" if self.config.ssl_enabled else "amqp"
                url = f"{protocol}://{self.config.username}:{self.config.password}@{primary_node.host}:{primary_node.port}{self.config.virtual_host}"
                return await aio_pika.connect_robust(url)
            
            self.connection_pool = Pool(get_connection, max_size=20)
            logger.info("Connection pool setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup connection pool: {e}")
            raise

    async def _enable_monitoring(self) -> None:
        """Enable cluster monitoring and health checks"""        try:
            # Start health monitoring task
            health_task = asyncio.create_task(self._monitor_cluster_health())
            self.monitoring_tasks.append(health_task)
            
            # Start performance monitoring task
            perf_task = asyncio.create_task(self._monitor_performance())
            self.monitoring_tasks.append(perf_task)
            
            logger.info("Cluster monitoring enabled")
            
        except Exception as e:
            logger.error(f"Failed to enable monitoring: {e}")
            raise

    async def _monitor_cluster_health(self) -> None:
        """Monitor cluster health continuously"""        while True:
            try:
                for node_config in self.config.nodes:
                    container = self.docker_client.containers.get(node_config.name)
                    container.reload()
                    
                    if container.status != "running":
                        logger.warning(f"RabbitMQ node {node_config.name} is not running")
                        # Could implement auto-restart logic here
                        
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in cluster health monitoring: {e}")
                await asyncio.sleep(60)

    async def _monitor_performance(self) -> None:
        """Monitor cluster performance metrics"""        while True:
            try:
                # Get cluster stats via management API
                stats = await self._get_cluster_stats()
                
                # Check for performance issues
                if stats.get("total_messages", 0) > 50000:
                    logger.warning("High message volume detected")
                    
                if stats.get("memory_usage", 0) > 0.9:
                    logger.warning("High memory usage on cluster")
                    
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(120)

    async def get_cluster_status(self) -> Dict[str, Union[str, int, List[Dict]]]:
        """Get comprehensive cluster status"""        try:
            node_statuses = []
            
            for node_config in self.config.nodes:
                try:
                    container = self.docker_client.containers.get(node_config.name)
                    container.reload()
                    
                    node_statuses.append({
                        "name": node_config.name,
                        "status": container.status,
                        "host": node_config.host,
                        "port": node_config.port,
                        "management_port": node_config.management_port,
                        "node_type": node_config.node_type,
                        "memory_limit": node_config.memory_limit
                    })
                except docker.errors.NotFound:
                    node_statuses.append({
                        "name": node_config.name,
                        "status": "not_found",
                        "error": "Container not found"
                    })
                    
            cluster_stats = await self._get_cluster_stats()
            
            return {
                "cluster_status": "healthy" if all(n["status"] == "running" for n in node_statuses) else "degraded",
                "total_nodes": len(self.config.nodes),
                "running_nodes": len([n for n in node_statuses if n["status"] == "running"]),
                "ssl_enabled": self.config.ssl_enabled,
                "high_availability": self.config.high_availability,
                "monitoring_enabled": self.config.monitoring_enabled,
                "nodes": node_statuses,
                "cluster_stats": cluster_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to get cluster status: {e}")
            return {"cluster_status": "error", "error": str(e)}

    async def _get_cluster_stats(self) -> Dict[str, Union[int, float]]:
        """Get cluster statistics"""        try:
            # This would integrate with RabbitMQ Management API
            # For now, return mock data
            return {
                "total_messages": 1250,
                "total_queues": len(self.queues),
                "total_exchanges": len(self.exchanges),
                "total_connections": 15,
                "memory_usage": 0.65,
                "disk_usage": 0.45,
                "message_rate": 125.5,
                "publish_rate": 85.2,
                "deliver_rate": 40.3
            }
            
        except Exception as e:
            logger.error(f"Failed to get cluster stats: {e}")
            return {}

    async def publish_message(self, exchange_name: str, routing_key: str, message: Dict, priority: int = 0) -> bool:
        """Publish message to exchange"""        try:
            connection = await self._get_connection()
            channel = await connection.channel()
            
            exchange = self.exchanges.get(exchange_name)
            if not exchange:
                raise ValueError(f"Exchange {exchange_name} not found")
                
            message_body = Message(
                json.dumps(message).encode(),
                priority=priority,
                content_type="application/json",
                delivery_mode=2  # Persistent
            )
            
            await exchange.publish(message_body, routing_key=routing_key)
            
            logger.debug(f"Published message to {exchange_name} with routing key {routing_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return False

    async def shutdown_cluster(self) -> Dict[str, Union[str, bool]]:
        """Gracefully shutdown the cluster"""        try:
            logger.info("Starting cluster shutdown")
            
            # Stop monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
                
            # Close connection pool
            if self.connection_pool:
                await self.connection_pool.close()
                
            # Stop all nodes
            for node_config in self.config.nodes:
                try:
                    container = self.docker_client.containers.get(node_config.name)
                    container.stop(timeout=30)
                    container.remove()
                except docker.errors.NotFound:
                    pass
                    
            logger.info("Cluster shutdown completed")
            return {"status": "success", "message": "Cluster shutdown completed"}
            
        except Exception as e:
            logger.error(f"Error during cluster shutdown: {e}")
            return {"status": "error", "error": str(e)}

    def export_cluster_config(self) -> Dict:
        """Export current cluster configuration"""        return {
            "cluster_config": self.config.dict(),
            "deployment_timestamp": time.time(),
            "nodes_count": len(self.config.nodes),
            "ssl_enabled": self.config.ssl_enabled,
            "high_availability": self.config.high_availability
        }

    @classmethod
    def from_config_file(cls, config_path: str) -> "RabbitMQManager":
        """Create RabbitMQManager from configuration file"""        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        config = RabbitMQClusterConfig(**config_data)
        return cls(config)
