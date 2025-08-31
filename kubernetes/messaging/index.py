"""IA Influencer Agent - Messaging Deployment Orchestrator
Main orchestration module for enterprise messaging infrastructure deployment

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
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field

from ...core.config import get_settings
from ...core.logging import get_logger
from ...monitoring.health_checker import HealthChecker
from .celery_manager import CeleryClusterConfig, CeleryManager
from .kafka_manager import KafkaClusterConfig, KafkaManager
from .message_router import Message, MessageRouter, MessageType, MessagePriority
from .rabbitmq_manager import RabbitMQClusterConfig, RabbitMQManager

logger = get_logger(__name__)
settings = get_settings()


class MessagingInfrastructureConfig(BaseModel):
    """Configuration for complete messaging infrastructure"""    deployment_name: str = Field(default="ia-influencer-messaging", description="Deployment name")
    deploy_kafka: bool = Field(default=True, description="Deploy Kafka cluster")
    deploy_rabbitmq: bool = Field(default=True, description="Deploy RabbitMQ cluster")
    deploy_celery: bool = Field(default=True, description="Deploy Celery workers")
    enable_monitoring: bool = Field(default=True, description="Enable monitoring")
    enable_ssl: bool = Field(default=True, description="Enable SSL/TLS")
    auto_scaling: bool = Field(default=True, description="Enable auto-scaling")
    backup_enabled: bool = Field(default=True, description="Enable backups")
    disaster_recovery: bool = Field(default=True, description="Enable disaster recovery")
    
    # Infrastructure sizing
    cluster_size: str = Field(default="medium", description="Cluster size: small, medium, large, enterprise")
    performance_profile: str = Field(default="balanced", description="Performance profile: memory, cpu, storage, balanced")
    
    # Custom configurations
    kafka_config: Optional[KafkaClusterConfig] = Field(None, description="Custom Kafka configuration")
    rabbitmq_config: Optional[RabbitMQClusterConfig] = Field(None, description="Custom RabbitMQ configuration")
    celery_config: Optional[CeleryClusterConfig] = Field(None, description="Custom Celery configuration")


class MessagingDeploymentOrchestrator:
    """    Enterprise messaging infrastructure deployment orchestrator
    Manages complete lifecycle of multi-protocol messaging systems
    """    def __init__(self, config: Optional[MessagingInfrastructureConfig] = None):
        self.config = config or self._get_default_config()
        self.health_checker = HealthChecker()
        
        # Component managers
        self.kafka_manager: Optional[KafkaManager] = None
        self.rabbitmq_manager: Optional[RabbitMQManager] = None
        self.celery_manager: Optional[CeleryManager] = None
        self.message_router: Optional[MessageRouter] = None
        
        # Deployment state
        self.deployment_status: Dict[str, str] = {}
        self.deployment_timestamp: Optional[float] = None
        self.monitoring_tasks: List[asyncio.Task] = []

    def _get_default_config(self) -> MessagingInfrastructureConfig:
        """Get default infrastructure configuration"""        return MessagingInfrastructureConfig(
            deployment_name="ia-influencer-messaging",
            deploy_kafka=True,
            deploy_rabbitmq=True,
            deploy_celery=True,
            enable_monitoring=True,
            enable_ssl=True,
            auto_scaling=True,
            cluster_size="medium",
            performance_profile="balanced"
        )

    async def deploy_infrastructure(self) -> Dict[str, Union[str, bool, Dict]]:
        """Deploy complete messaging infrastructure"""        try:
            logger.info("Starting messaging infrastructure deployment")
            self.deployment_timestamp = time.time()
            
            deployment_results = {}
            
            # Initialize message router first
            self.message_router = MessageRouter()
            deployment_results["message_router"] = {"status": "initialized"}
            
            # Deploy Kafka cluster
            if self.config.deploy_kafka:
                kafka_result = await self._deploy_kafka_cluster()
                deployment_results["kafka"] = kafka_result
                
            # Deploy RabbitMQ cluster
            if self.config.deploy_rabbitmq:
                rabbitmq_result = await self._deploy_rabbitmq_cluster()
                deployment_results["rabbitmq"] = rabbitmq_result
                
            # Deploy Celery workers
            if self.config.deploy_celery:
                celery_result = await self._deploy_celery_cluster()
                deployment_results["celery"] = celery_result
                
            # Initialize message router with deployed components
            await self._initialize_message_router()
            
            # Setup monitoring
            if self.config.enable_monitoring:
                await self._setup_monitoring()
                deployment_results["monitoring"] = {"status": "enabled"}
                
            # Setup backup and disaster recovery
            if self.config.backup_enabled:
                await self._setup_backup_systems()
                deployment_results["backup"] = {"status": "configured"}
                
            # Update deployment status
            self.deployment_status = {
                "overall_status": "deployed",
                "deployment_time": time.time() - self.deployment_timestamp,
                "components": deployment_results
            }
            
            logger.info(f"Messaging infrastructure deployed successfully in {self.deployment_status['deployment_time']:.2f}s")
            
            return {
                "status": "success",
                "deployment_id": f"{self.config.deployment_name}-{int(self.deployment_timestamp)}",
                "deployment_time": self.deployment_status["deployment_time"],
                "components_deployed": len([k for k, v in deployment_results.items() if v.get("status") == "success"]),
                "results": deployment_results
            }
            
        except Exception as e:
            logger.error(f"Failed to deploy messaging infrastructure: {e}")
            self.deployment_status["overall_status"] = "failed"
            self.deployment_status["error"] = str(e)
            raise

    async def _deploy_kafka_cluster(self) -> Dict[str, Union[str, bool, int]]:
        """Deploy Kafka cluster"""        try:
            logger.info("Deploying Kafka cluster")
            
            # Use custom config or generate based on cluster size
            kafka_config = self.config.kafka_config or self._generate_kafka_config()
            
            self.kafka_manager = KafkaManager(kafka_config)
            result = await self.kafka_manager.deploy_cluster()
            
            logger.info("Kafka cluster deployed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to deploy Kafka cluster: {e}")
            return {"status": "failed", "error": str(e)}

    async def _deploy_rabbitmq_cluster(self) -> Dict[str, Union[str, bool, int]]:
        """Deploy RabbitMQ cluster"""        try:
            logger.info("Deploying RabbitMQ cluster")
            
            # Use custom config or generate based on cluster size
            rabbitmq_config = self.config.rabbitmq_config or self._generate_rabbitmq_config()
            
            self.rabbitmq_manager = RabbitMQManager(rabbitmq_config)
            result = await self.rabbitmq_manager.deploy_cluster()
            
            logger.info("RabbitMQ cluster deployed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to deploy RabbitMQ cluster: {e}")
            return {"status": "failed", "error": str(e)}

    async def _deploy_celery_cluster(self) -> Dict[str, Union[str, bool, int]]:
        """Deploy Celery workers"""        try:
            logger.info("Deploying Celery workers")
            
            # Use custom config or generate based on cluster size
            celery_config = self.config.celery_config or self._generate_celery_config()
            
            self.celery_manager = CeleryManager(celery_config)
            result = await self.celery_manager.deploy_cluster()
            
            logger.info("Celery workers deployed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to deploy Celery workers: {e}")
            return {"status": "failed", "error": str(e)}

    def _generate_kafka_config(self) -> KafkaClusterConfig:
        """Generate Kafka configuration based on cluster size"""        cluster_configs = {
            "small": {
                "brokers": 1,
                "zookeepers": 1,
                "memory": "2GB",
                "replication_factor": 1
            },
            "medium": {
                "brokers": 3,
                "zookeepers": 3,
                "memory": "4GB",
                "replication_factor": 3
            },
            "large": {
                "brokers": 5,
                "zookeepers": 3,
                "memory": "8GB",
                "replication_factor": 3
            },
            "enterprise": {
                "brokers": 7,
                "zookeepers": 5,
                "memory": "16GB",
                "replication_factor": 3
            }
        }
        
        cluster_spec = cluster_configs.get(self.config.cluster_size, cluster_configs["medium"])
        
        # Generate broker configurations
        brokers = []
        for i in range(cluster_spec["brokers"]):
            brokers.append({
                "id": i + 1,
                "name": f"kafka-broker-{i + 1}",
                "host": f"kafka-{i + 1}",
                "port": 9092,
                "memory_limit": cluster_spec["memory"]
            })
        
        # Generate Zookeeper configurations
        zookeepers = []
        for i in range(cluster_spec["zookeepers"]):
            zookeepers.append({
                "id": i + 1,
                "name": f"zookeeper-{i + 1}",
                "host": f"zk-{i + 1}",
                "port": 2181
            })
        
        return KafkaClusterConfig(
            cluster_name=f"{self.config.deployment_name}-kafka",
            brokers=brokers,
            zookeepers=zookeepers,
            replication_factor=cluster_spec["replication_factor"],
            ssl_enabled=self.config.enable_ssl,
            monitoring_enabled=self.config.enable_monitoring
        )

    def _generate_rabbitmq_config(self) -> RabbitMQClusterConfig:
        """Generate RabbitMQ configuration based on cluster size"""        cluster_configs = {
            "small": {"nodes": 1, "memory": "2GB"},
            "medium": {"nodes": 3, "memory": "4GB"},
            "large": {"nodes": 5, "memory": "6GB"},
            "enterprise": {"nodes": 7, "memory": "8GB"}
        }
        
        cluster_spec = cluster_configs.get(self.config.cluster_size, cluster_configs["medium"])
        
        # Generate node configurations
        nodes = []
        for i in range(cluster_spec["nodes"]):
            nodes.append({
                "name": f"rabbitmq-node-{i + 1}",
                "host": f"rabbitmq-{i + 1}",
                "port": 5672,
                "memory_limit": cluster_spec["memory"],
                "node_type": "disc" if i < 2 else "ram"
            })
        
        return RabbitMQClusterConfig(
            cluster_name=f"{self.config.deployment_name}-rabbitmq",
            nodes=nodes,
            password=os.getenv("RABBITMQ_PASSWORD", "secure-default-password"),
            ssl_enabled=self.config.enable_ssl,
            high_availability=True,
            monitoring_enabled=self.config.enable_monitoring
        )

    def _generate_celery_config(self) -> CeleryClusterConfig:
        """Generate Celery configuration based on cluster size and performance profile"""        cluster_configs = {
            "small": {"workers": 3, "concurrency": 4},
            "medium": {"workers": 5, "concurrency": 8},
            "large": {"workers": 8, "concurrency": 12},
            "enterprise": {"workers": 12, "concurrency": 16}
        }
        
        cluster_spec = cluster_configs.get(self.config.cluster_size, cluster_configs["medium"])
        
        # Performance profile adjustments
        if self.config.performance_profile == "cpu":
            cluster_spec["concurrency"] *= 2
        elif self.config.performance_profile == "memory":
            cluster_spec["concurrency"] = max(2, cluster_spec["concurrency"] // 2)
        
        # Generate worker configurations for different task types
        workers = [
            {
                "name": "content_processor",
                "concurrency": cluster_spec["concurrency"],
                "queues": ["content_processing", "fingerprint_generation"],
                "optimization": "speed"
            },
            {
                "name": "ai_analyzer",
                "concurrency": max(2, cluster_spec["concurrency"] // 2),
                "queues": ["ai_analysis", "ml_inference"],
                "optimization": "memory"
            },
            {
                "name": "crawler_worker",
                "concurrency": cluster_spec["concurrency"] // 2,
                "queues": ["web_crawling", "monitoring"],
                "optimization": "io"
            },
            {
                "name": "notification_worker",
                "concurrency": cluster_spec["concurrency"] * 2,
                "queues": ["notifications", "alerts"],
                "optimization": "speed"
            },
            {
                "name": "revenue_processor",
                "concurrency": 2,
                "queues": ["revenue_calculation", "payment_processing"],
                "optimization": "reliability"
            }
        ]
        
        # Add additional workers for larger clusters
        if cluster_spec["workers"] > 5:
            workers.extend([
                {
                    "name": "analytics_worker",
                    "concurrency": 4,
                    "queues": ["analytics", "reporting"],
                    "optimization": "memory"
                },
                {
                    "name": "backup_worker",
                    "concurrency": 2,
                    "queues": ["backup", "maintenance"],
                    "optimization": "io"
                }
            ])
        
        return CeleryClusterConfig(
            broker_url=settings.CELERY_BROKER_URL,
            result_backend=settings.CELERY_RESULT_BACKEND,
            workers=workers[:cluster_spec["workers"]],
            auto_scaling=self.config.auto_scaling,
            max_workers=cluster_spec["workers"] * 2,
            min_workers=max(1, cluster_spec["workers"] // 2)
        )

    async def _initialize_message_router(self) -> None:
        """Initialize message router with deployed components"""        try:
            await self.message_router.initialize_protocols(
                kafka_manager=self.kafka_manager,
                rabbitmq_manager=self.rabbitmq_manager,
                celery_manager=self.celery_manager
            )
            
            logger.info("Message router initialized with deployed components")
            
        except Exception as e:
            logger.error(f"Failed to initialize message router: {e}")
            raise

    async def _setup_monitoring(self) -> None:
        """Setup comprehensive monitoring for all components"""        try:
            # Start infrastructure monitoring
            monitor_task = asyncio.create_task(self._monitor_infrastructure())
            self.monitoring_tasks.append(monitor_task)
            
            # Start performance monitoring
            perf_task = asyncio.create_task(self._monitor_performance())
            self.monitoring_tasks.append(perf_task)
            
            # Start health checks
            health_task = asyncio.create_task(self._monitor_health())
            self.monitoring_tasks.append(health_task)
            
            logger.info("Comprehensive monitoring setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup monitoring: {e}")
            raise

    async def _setup_backup_systems(self) -> None:
        """Setup backup and disaster recovery systems"""        try:
            # Create backup directories
            backup_dir = Path("/app/backups/messaging")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Start backup tasks
            backup_task = asyncio.create_task(self._run_periodic_backups())
            self.monitoring_tasks.append(backup_task)
            
            logger.info("Backup systems configured")
            
        except Exception as e:
            logger.error(f"Failed to setup backup systems: {e}")
            raise

    async def _monitor_infrastructure(self) -> None:
        """Monitor infrastructure components"""        while True:
            try:
                # Monitor each component
                if self.kafka_manager:
                    kafka_status = await self.kafka_manager.get_cluster_status()
                    if kafka_status.get("cluster_status") != "healthy":
                        logger.warning("Kafka cluster health issues detected")
                
                if self.rabbitmq_manager:
                    rabbitmq_status = await self.rabbitmq_manager.get_cluster_status()
                    if rabbitmq_status.get("cluster_status") != "healthy":
                        logger.warning("RabbitMQ cluster health issues detected")
                
                if self.celery_manager:
                    celery_status = await self.celery_manager.get_cluster_status()
                    if celery_status.get("cluster_status") != "healthy":
                        logger.warning("Celery cluster health issues detected")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in infrastructure monitoring: {e}")
                await asyncio.sleep(60)

    async def _monitor_performance(self) -> None:
        """Monitor performance metrics"""        while True:
            try:
                performance_metrics = await self.get_performance_metrics()
                
                # Check for performance issues
                if performance_metrics.get("message_throughput", 0) < 100:
                    logger.warning("Low message throughput detected")
                
                if performance_metrics.get("average_latency", 0) > 1000:
                    logger.warning("High latency detected")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(120)

    async def _monitor_health(self) -> None:
        """Monitor overall health"""        while True:
            try:
                health_status = await self.health_check()
                
                if health_status.get("overall_status") != "healthy":
                    logger.warning("Overall system health issues detected")
                
                await asyncio.sleep(45)  # Check every 45 seconds
                
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(90)

    async def _run_periodic_backups(self) -> None:
        """Run periodic backups"""        while True:
            try:
                # Run backup every 6 hours
                await asyncio.sleep(21600)
                
                backup_result = await self.create_backup()
                if backup_result.get("status") == "success":
                    logger.info("Periodic backup completed successfully")
                else:
                    logger.error("Periodic backup failed")
                
            except Exception as e:
                logger.error(f"Error in periodic backup: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour

    async def send_message(self, 
                          message_type: MessageType,
                          source: str,
                          payload: Dict,
                          priority: MessagePriority = MessagePriority.MEDIUM,
                          destination: Optional[str] = None,
                          routing_key: Optional[str] = None) -> bool:
        """Send message through the routing system"""        try:
            if not self.message_router:
                raise ValueError("Message router not initialized")
            
            message = Message(
                id=f"{source}_{int(time.time() * 1000)}",
                type=message_type,
                priority=priority,
                source=source,
                destination=destination,
                payload=payload,
                routing_key=routing_key
            )
            
            return await self.message_router.route_message(message)
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    async def get_infrastructure_status(self) -> Dict[str, Union[str, int, Dict]]:
        """Get comprehensive infrastructure status"""        try:
            status = {
                "overall_status": self.deployment_status.get("overall_status", "unknown"),
                "deployment_timestamp": self.deployment_timestamp,
                "uptime": time.time() - self.deployment_timestamp if self.deployment_timestamp else 0,
                "components": {}
            }
            
            # Get component statuses
            if self.kafka_manager:
                status["components"]["kafka"] = await self.kafka_manager.get_cluster_status()
            
            if self.rabbitmq_manager:
                status["components"]["rabbitmq"] = await self.rabbitmq_manager.get_cluster_status()
            
            if self.celery_manager:
                status["components"]["celery"] = await self.celery_manager.get_cluster_status()
            
            if self.message_router:
                status["components"]["message_router"] = await self.message_router.get_routing_stats()
            
            # Determine overall status
            component_statuses = [
                comp.get("cluster_status", "unknown") 
                for comp in status["components"].values()
                if isinstance(comp, dict)
            ]
            
            if all(s == "healthy" for s in component_statuses):
                status["overall_status"] = "healthy"
            elif any(s == "error" for s in component_statuses):
                status["overall_status"] = "error"
            else:
                status["overall_status"] = "degraded"
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get infrastructure status: {e}")
            return {"overall_status": "error", "error": str(e)}

    async def get_performance_metrics(self) -> Dict[str, Union[int, float]]:
        """Get performance metrics from all components"""        try:
            metrics = {
                "timestamp": time.time(),
                "message_throughput": 0,
                "average_latency": 0,
                "total_messages_processed": 0,
                "error_rate": 0
            }
            
            # Collect metrics from message router
            if self.message_router:
                routing_stats = await self.message_router.get_routing_stats()
                metrics["total_messages_processed"] = routing_stats.get("total_routed", 0)
                metrics["error_rate"] = 100 - routing_stats.get("success_rate", 0)
            
            # Add component-specific metrics
            component_metrics = {}
            
            if self.kafka_manager:
                kafka_status = await self.kafka_manager.get_cluster_status()
                kafka_stats = kafka_status.get("cluster_stats", {})
                component_metrics["kafka"] = {
                    "messages_per_second": kafka_stats.get("message_rate", 0),
                    "bytes_in_per_second": kafka_stats.get("bytes_in_per_second", 0),
                    "bytes_out_per_second": kafka_stats.get("bytes_out_per_second", 0)
                }
                metrics["message_throughput"] += kafka_stats.get("message_rate", 0)
            
            if self.rabbitmq_manager:
                rabbitmq_status = await self.rabbitmq_manager.get_cluster_status()
                rabbitmq_stats = rabbitmq_status.get("cluster_stats", {})
                component_metrics["rabbitmq"] = {
                    "message_rate": rabbitmq_stats.get("message_rate", 0),
                    "publish_rate": rabbitmq_stats.get("publish_rate", 0),
                    "deliver_rate": rabbitmq_stats.get("deliver_rate", 0)
                }
                metrics["message_throughput"] += rabbitmq_stats.get("message_rate", 0)
            
            metrics["components"] = component_metrics
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {"error": str(e)}

    async def health_check(self) -> Dict[str, Union[str, bool, List[Dict]]]:
        """Perform comprehensive health check"""        try:
            health_checks = []
            overall_healthy = True
            
            # Check each component
            if self.kafka_manager:
                kafka_status = await self.kafka_manager.get_cluster_status()
                kafka_healthy = kafka_status.get("cluster_status") == "healthy"
                health_checks.append({
                    "component": "kafka",
                    "status": "healthy" if kafka_healthy else "unhealthy",
                    "details": kafka_status
                })
                overall_healthy &= kafka_healthy
            
            if self.rabbitmq_manager:
                rabbitmq_status = await self.rabbitmq_manager.get_cluster_status()
                rabbitmq_healthy = rabbitmq_status.get("cluster_status") == "healthy"
                health_checks.append({
                    "component": "rabbitmq",
                    "status": "healthy" if rabbitmq_healthy else "unhealthy",
                    "details": rabbitmq_status
                })
                overall_healthy &= rabbitmq_healthy
            
            if self.celery_manager:
                celery_status = await self.celery_manager.get_cluster_status()
                celery_healthy = celery_status.get("cluster_status") == "healthy"
                health_checks.append({
                    "component": "celery",
                    "status": "healthy" if celery_healthy else "unhealthy", 
                    "details": celery_status
                })
                overall_healthy &= celery_healthy
            
            return {
                "overall_status": "healthy" if overall_healthy else "unhealthy",
                "timestamp": time.time(),
                "checks": health_checks
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"overall_status": "error", "error": str(e)}

    async def scale_infrastructure(self, component: str, scale_factor: float) -> Dict[str, Union[str, bool]]:
        """Scale infrastructure components"""        try:
            if component == "kafka" and self.kafka_manager:
                # Kafka scaling would be implemented here
                logger.info(f"Scaling Kafka cluster by factor {scale_factor}")
                return {"status": "success", "component": "kafka", "scale_factor": scale_factor}
            
            elif component == "rabbitmq" and self.rabbitmq_manager:
                # RabbitMQ scaling would be implemented here
                logger.info(f"Scaling RabbitMQ cluster by factor {scale_factor}")
                return {"status": "success", "component": "rabbitmq", "scale_factor": scale_factor}
            
            elif component == "celery" and self.celery_manager:
                # Celery scaling is already implemented
                if scale_factor > 1:
                    await self.celery_manager._scale_up_workers(int(scale_factor))
                else:
                    await self.celery_manager._scale_down_workers(int(1/scale_factor))
                return {"status": "success", "component": "celery", "scale_factor": scale_factor}
            
            else:
                return {"status": "error", "error": f"Component {component} not found or scaling not supported"}
                
        except Exception as e:
            logger.error(f"Failed to scale {component}: {e}")
            return {"status": "error", "error": str(e)}

    async def create_backup(self) -> Dict[str, Union[str, bool]]:
        """Create backup of messaging infrastructure"""        try:
            backup_timestamp = int(time.time())
            backup_dir = Path(f"/app/backups/messaging/{backup_timestamp}")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_data = {
                "timestamp": backup_timestamp,
                "deployment_config": self.config.dict(),
                "infrastructure_status": await self.get_infrastructure_status(),
                "performance_metrics": await self.get_performance_metrics()
            }
            
            # Save routing configuration
            if self.message_router:
                backup_data["routing_config"] = self.message_router.export_routing_config()
            
            # Save component configurations
            if self.kafka_manager:
                backup_data["kafka_config"] = self.kafka_manager.export_cluster_config()
            
            if self.rabbitmq_manager:
                backup_data["rabbitmq_config"] = self.rabbitmq_manager.export_cluster_config()
            
            if self.celery_manager:
                backup_data["celery_config"] = self.celery_manager.export_cluster_config()
            
            # Write backup file
            backup_file = backup_dir / "messaging_infrastructure_backup.json"
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            logger.info(f"Backup created successfully: {backup_file}")
            return {
                "status": "success",
                "backup_file": str(backup_file),
                "backup_timestamp": backup_timestamp
            }
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return {"status": "error", "error": str(e)}

    async def restore_from_backup(self, backup_file: str) -> Dict[str, Union[str, bool]]:
        """Restore infrastructure from backup"""        try:
            logger.info(f"Restoring from backup: {backup_file}")
            
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            # Restore configuration
            restored_config = MessagingInfrastructureConfig(**backup_data["deployment_config"])
            
            # Shutdown current infrastructure
            await self.shutdown_infrastructure()
            
            # Update configuration
            self.config = restored_config
            
            # Redeploy infrastructure
            result = await self.deploy_infrastructure()
            
            logger.info("Infrastructure restored successfully")
            return {
                "status": "success",
                "restored_from": backup_file,
                "deployment_result": result
            }
            
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return {"status": "error", "error": str(e)}

    async def shutdown_infrastructure(self) -> Dict[str, Union[str, bool]]:
        """Gracefully shutdown messaging infrastructure"""        try:
            logger.info("Starting infrastructure shutdown")
            
            shutdown_results = {}
            
            # Stop monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
            
            # Shutdown components
            if self.celery_manager:
                result = await self.celery_manager.shutdown_cluster()
                shutdown_results["celery"] = result
            
            if self.rabbitmq_manager:
                result = await self.rabbitmq_manager.shutdown_cluster()
                shutdown_results["rabbitmq"] = result
            
            if self.kafka_manager:
                result = await self.kafka_manager.shutdown_cluster()
                shutdown_results["kafka"] = result
            
            # Reset state
            self.deployment_status = {"overall_status": "shutdown"}
            
            logger.info("Infrastructure shutdown completed")
            return {
                "status": "success",
                "message": "Infrastructure shutdown completed",
                "components": shutdown_results
            }
            
        except Exception as e:
            logger.error(f"Error during infrastructure shutdown: {e}")
            return {"status": "error", "error": str(e)}

    def export_deployment_config(self) -> Dict:
        """Export current deployment configuration"""        return {
            "infrastructure_config": self.config.dict(),
            "deployment_status": self.deployment_status,
            "deployment_timestamp": self.deployment_timestamp,
            "export_timestamp": time.time()
        }


# Factory functions for creating component managers
async def create_kafka_manager(config: Optional[KafkaClusterConfig] = None) -> KafkaManager:
    """Create and deploy Kafka manager"""    manager = KafkaManager(config)
    await manager.deploy_cluster()
    return manager


async def create_rabbitmq_manager(config: Optional[RabbitMQClusterConfig] = None) -> RabbitMQManager:
    """Create and deploy RabbitMQ manager"""    manager = RabbitMQManager(config)
    await manager.deploy_cluster()
    return manager


async def create_celery_manager(config: Optional[CeleryClusterConfig] = None) -> CeleryManager:
    """Create and deploy Celery manager"""    manager = CeleryManager(config)
    await manager.deploy_cluster()
    return manager


async def create_message_router() -> MessageRouter:
    """Create and initialize message router"""    router = MessageRouter()
    return router


async def create_messaging_orchestrator(config: Optional[MessagingInfrastructureConfig] = None) -> MessagingDeploymentOrchestrator:
    """Create messaging deployment orchestrator"""    return MessagingDeploymentOrchestrator(config)


async def deploy_messaging_infrastructure(config: Optional[MessagingInfrastructureConfig] = None) -> MessagingDeploymentOrchestrator:
    """Deploy complete messaging infrastructure"""    orchestrator = MessagingDeploymentOrchestrator(config)
    await orchestrator.deploy_infrastructure()
    return orchestrator


# Main deployment function
if __name__ == "__main__":
    async def main():
        """Main deployment function"""        try:
            orchestrator = await deploy_messaging_infrastructure()
            status = await orchestrator.get_infrastructure_status()
            print(f"Deployment Status: {status['overall_status']}")
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            
    asyncio.run(main())

import asyncio
import logging
from typing import Dict, Optional, Union

from .celery_manager import CeleryManager, CeleryClusterConfig
from .kafka_manager import KafkaManager, KafkaClusterConfig
from .message_router import Message, MessageRouter, MessageType, MessagePriority
from .rabbitmq_manager import RabbitMQManager, RabbitMQClusterConfig

from ...core.config import get_settings
from ...core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class MessagingDeploymentOrchestrator:
    """    Enterprise messaging deployment orchestrator
    Manages complete messaging infrastructure for IA content processing
    """    def __init__(self):
        self.kafka_manager: Optional[KafkaManager] = None
        self.rabbitmq_manager: Optional[RabbitMQManager] = None
        self.celery_manager: Optional[CeleryManager] = None
        self.message_router: Optional[MessageRouter] = None
        self.deployment_status: Dict[str, str] = {}

    async def deploy_complete_infrastructure(self,
                                           kafka_config: Optional[KafkaClusterConfig] = None,
                                           rabbitmq_config: Optional[RabbitMQClusterConfig] = None,
                                           celery_config: Optional[CeleryClusterConfig] = None) -> Dict[str, Union[str, bool]]:
        """Deploy complete messaging infrastructure"""        try:
            logger.info("Starting complete messaging infrastructure deployment")
            
            deployment_results = {}
            
            # Deploy Kafka cluster
            if kafka_config or settings.DEPLOY_KAFKA:
                logger.info("Deploying Kafka cluster...")
                self.kafka_manager = KafkaManager(kafka_config)
                kafka_result = await self.kafka_manager.deploy_cluster()
                deployment_results["kafka"] = kafka_result
                self.deployment_status["kafka"] = "deployed"
            
            # Deploy RabbitMQ cluster
            if rabbitmq_config or settings.DEPLOY_RABBITMQ:
                logger.info("Deploying RabbitMQ cluster...")
                self.rabbitmq_manager = RabbitMQManager(rabbitmq_config)
                rabbitmq_result = await self.rabbitmq_manager.deploy_cluster()
                deployment_results["rabbitmq"] = rabbitmq_result
                self.deployment_status["rabbitmq"] = "deployed"
            
            # Deploy Celery cluster
            if celery_config or settings.DEPLOY_CELERY:
                logger.info("Deploying Celery cluster...")
                self.celery_manager = CeleryManager(celery_config)
                celery_result = await self.celery_manager.deploy_cluster()
                deployment_results["celery"] = celery_result
                self.deployment_status["celery"] = "deployed"
            
            # Setup message router
            logger.info("Setting up message router...")
            self.message_router = MessageRouter()
            await self.message_router.initialize_protocols(
                kafka_manager=self.kafka_manager,
                rabbitmq_manager=self.rabbitmq_manager,
                celery_manager=self.celery_manager
            )
            self.deployment_status["router"] = "deployed"
            
            logger.info("Complete messaging infrastructure deployed successfully")
            return {
                "status": "success",
                "components_deployed": len(deployment_results),
                "deployment_results": deployment_results,
                "router_initialized": True
            }
            
        except Exception as e:
            logger.error(f"Failed to deploy messaging infrastructure: {e}")
            return {"status": "error", "error": str(e)}

    async def get_infrastructure_status(self) -> Dict[str, Union[str, int, Dict]]:
        """Get complete infrastructure status"""        try:
            status_report = {
                "overall_status": "healthy",
                "deployment_status": self.deployment_status,
                "components": {}
            }
            
            # Kafka status
            if self.kafka_manager:
                kafka_status = await self.kafka_manager.get_cluster_status()
                status_report["components"]["kafka"] = kafka_status
                if kafka_status.get("cluster_status") != "healthy":
                    status_report["overall_status"] = "degraded"
            
            # RabbitMQ status
            if self.rabbitmq_manager:
                rabbitmq_status = await self.rabbitmq_manager.get_cluster_status()
                status_report["components"]["rabbitmq"] = rabbitmq_status
                if rabbitmq_status.get("cluster_status") != "healthy":
                    status_report["overall_status"] = "degraded"
            
            # Celery status
            if self.celery_manager:
                celery_status = await self.celery_manager.get_cluster_status()
                status_report["components"]["celery"] = celery_status
                if celery_status.get("cluster_status") != "healthy":
                    status_report["overall_status"] = "degraded"
            
            # Router status
            if self.message_router:
                router_stats = await self.message_router.get_routing_stats()
                status_report["components"]["router"] = router_stats
            
            return status_report
            
        except Exception as e:
            logger.error(f"Failed to get infrastructure status: {e}")
            return {"overall_status": "error", "error": str(e)}

    async def send_message(self, 
                         message_type: MessageType,
                         source: str,
                         payload: Dict,
                         priority: MessagePriority = MessagePriority.MEDIUM,
                         destination: Optional[str] = None) -> bool:
        """Send message through the routing system"""        try:
            if not self.message_router:
                logger.error("Message router not initialized")
                return False
            
            # Create message
            import uuid
            message = Message(
                id=str(uuid.uuid4()),
                type=message_type,
                priority=priority,
                source=source,
                destination=destination,
                payload=payload
            )
            
            # Route message
            return await self.message_router.route_message(message)
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    async def shutdown_infrastructure(self) -> Dict[str, Union[str, bool]]:
        """Gracefully shutdown complete infrastructure"""        try:
            logger.info("Starting infrastructure shutdown")
            
            shutdown_results = {}
            
            # Shutdown Celery cluster
            if self.celery_manager:
                celery_result = await self.celery_manager.shutdown_cluster()
                shutdown_results["celery"] = celery_result
            
            # Shutdown RabbitMQ cluster
            if self.rabbitmq_manager:
                rabbitmq_result = await self.rabbitmq_manager.shutdown_cluster()
                shutdown_results["rabbitmq"] = rabbitmq_result
            
            # Shutdown Kafka cluster
            if self.kafka_manager:
                kafka_result = await self.kafka_manager.shutdown_cluster()
                shutdown_results["kafka"] = kafka_result
            
            # Clear deployment status
            self.deployment_status.clear()
            
            logger.info("Infrastructure shutdown completed")
            return {
                "status": "success",
                "shutdown_results": shutdown_results
            }
            
        except Exception as e:
            logger.error(f"Error during infrastructure shutdown: {e}")
            return {"status": "error", "error": str(e)}


# Factory functions for easy instantiation

def create_kafka_manager(config: Optional[KafkaClusterConfig] = None) -> KafkaManager:
    """Create Kafka manager instance"""    return KafkaManager(config)


def create_rabbitmq_manager(config: Optional[RabbitMQClusterConfig] = None) -> RabbitMQManager:
    """Create RabbitMQ manager instance"""    return RabbitMQManager(config)


def create_celery_manager(config: Optional[CeleryClusterConfig] = None) -> CeleryManager:
    """Create Celery manager instance"""    return CeleryManager(config)


def create_message_router() -> MessageRouter:
    """Create message router instance"""    return MessageRouter()


def create_messaging_orchestrator() -> MessagingDeploymentOrchestrator:
    """Create messaging deployment orchestrator"""    return MessagingDeploymentOrchestrator()


# Main deployment function for easy usage

async def deploy_messaging_infrastructure(
    kafka_config: Optional[KafkaClusterConfig] = None,
    rabbitmq_config: Optional[RabbitMQClusterConfig] = None,
    celery_config: Optional[CeleryClusterConfig] = None
) -> MessagingDeploymentOrchestrator:
    """    Deploy complete messaging infrastructure with optional configurations
    
    Returns:
        MessagingDeploymentOrchestrator: Configured orchestrator instance
    """    try:
        orchestrator = MessagingDeploymentOrchestrator()
        
        result = await orchestrator.deploy_complete_infrastructure(
            kafka_config=kafka_config,
            rabbitmq_config=rabbitmq_config,
            celery_config=celery_config
        )
        
        if result["status"] == "success":
            logger.info("Messaging infrastructure deployment completed successfully")
            return orchestrator
        else:
            raise Exception(f"Deployment failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Failed to deploy messaging infrastructure: {e}")
        raise


if __name__ == "__main__":
    """Example usage of messaging deployment"""    
    async def main():
        try:
            # Deploy complete infrastructure
            orchestrator = await deploy_messaging_infrastructure()
            
            # Get status
            status = await orchestrator.get_infrastructure_status()
            print(f"Infrastructure status: {status}")
            
            # Send test message
            await orchestrator.send_message(
                message_type=MessageType.CONTENT_UPLOAD,
                source="test_service",
                payload={"file_name": "test.mp3", "file_size": 1024000},
                priority=MessagePriority.HIGH
            )
            
            # Wait a bit
            await asyncio.sleep(5)
            
            # Shutdown
            await orchestrator.shutdown_infrastructure()
            
        except Exception as e:
            logger.error(f"Error in main: {e}")
    
    asyncio.run(main())
