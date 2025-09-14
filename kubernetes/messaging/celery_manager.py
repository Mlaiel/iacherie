"""IA Influencer Agent - Celery Deployment Manager
Enterprise Celery worker deployment and management for distributed task processing

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
import logging
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

import docker
import yaml
from celery import Celery
from kombu import Connection
from pydantic import BaseModel, Field

from ...core.config import get_settings
from ...core.logging import get_logger
from ...monitoring.health_checker import HealthChecker

logger = get_logger(__name__)
settings = get_settings()


class CeleryWorkerConfig(BaseModel):
    """
Configuration for Celery worker deployment"""
    name: str = Field(..., description="Worker name identifier")
    concurrency: int = Field(default=4, description="Number of concurrent processes")
    queues: List[str] = Field(default=["default"], description="Queues to process")
    loglevel: str = Field(default="INFO", description="Logging level")
    max_tasks_per_child: int = Field(default=1000, description="Max tasks before worker restart")
    time_limit: int = Field(default=300, description="Hard time limit for tasks")
    soft_time_limit: int = Field(default=240, description="Soft time limit for tasks")
    prefetch_multiplier: int = Field(default=1, description="Prefetch multiplier")
    optimization: str = Field(default="fair", description="Optimization strategy")


class CeleryClusterConfig(BaseModel):
    """Configuration for Celery cluster deployment"""
    broker_url: str = Field(..., description="Message broker URL")
    result_backend: str = Field(..., description="Result backend URL")
    workers: List[CeleryWorkerConfig] = Field(..., description="Worker configurations")
    monitoring_enabled: bool = Field(default=True, description="Enable monitoring")
    auto_scaling: bool = Field(default=True, description="Enable auto-scaling")
    max_workers: int = Field(default=20, description="Maximum number of workers")
    min_workers: int = Field(default=2, description="Minimum number of workers")


class CeleryManager:
    """
    Enterprise Celery deployment and management system
    Handles distributed task processing for IA content protection
    """
    def __init__(self, config -> None: Optional[CeleryClusterConfig] = None) -> None:
        self.config = config or self._get_default_config()
        self.docker_client = docker.from_env()
        self.health_checker = HealthChecker()
        self.workers: Dict[str, dict] = {}
        self.monitoring_tasks: List[asyncio.Task] = []
        
    def _get_default_config(self) -> CeleryClusterConfig:
        """
Get default Celery cluster configuration"""
        return CeleryClusterConfig(
            broker_url=settings.CELERY_BROKER_URL,
            result_backend=settings.CELERY_RESULT_BACKEND,
            workers=[
                CeleryWorkerConfig(
                    name="content_processor",
                    concurrency=8,
                    queues=["content_processing", "fingerprint_generation"],
                    optimization="speed"
                ),
                CeleryWorkerConfig(
                    name="ai_analyzer",
                    concurrency=4,
                    queues=["ai_analysis", "ml_inference"],
                    optimization="memory"
                ),
                CeleryWorkerConfig(
                    name="crawler_worker",
                    concurrency=6,
                    queues=["web_crawling", "monitoring"],
                    optimization="io"
                ),
                CeleryWorkerConfig(
                    name="notification_worker",
                    concurrency=10,
                    queues=["notifications", "alerts"],
                    optimization="speed"
                ),
                CeleryWorkerConfig(
                    name="revenue_processor",
                    concurrency=2,
                    queues=["revenue_calculation", "payment_processing"],
                    optimization="reliability"
                )
            ],
            auto_scaling=True,
            max_workers=25,
            min_workers=3
        )

    async def deploy_cluster(self) -> Dict[str, Union[str, bool]]:
        """Deploy complete Celery cluster"""
        try:
            logger.info("Starting Celery cluster deployment")
            
            # Validate broker connection
            await self._validate_broker_connection()
            
            # Deploy workers
            deployment_results = {}
            for worker_config in self.config.workers:
                result = await self._deploy_worker(worker_config)
                deployment_results[worker_config.name] = result
                
            # Start monitoring if enabled
            if self.config.monitoring_enabled:
                await self._start_monitoring()
                
            # Enable auto-scaling if configured
            if self.config.auto_scaling:
                await self._enable_auto_scaling()
                
            logger.info(f"Celery cluster deployed successfully: {deployment_results}")
            return {
                "status": "success",
                "workers_deployed": len(deployment_results),
                "monitoring_enabled": self.config.monitoring_enabled,
                "auto_scaling_enabled": self.config.auto_scaling
            }
            
        except Exception as e:
            logger.error(f"Failed to deploy Celery cluster: {e}")
            raise

    async def _deploy_worker(self, worker_config: CeleryWorkerConfig) -> Dict[str, Union[str, int]]:
        """Deploy individual Celery worker"""
        try:
            # Generate worker command
            command = self._generate_worker_command(worker_config)
            
            # Create Docker container for worker
            container = self.docker_client.containers.run(
                image="ia-influencer-celery:latest",
                command=command,
                name=f"celery-{worker_config.name}",
                detach=True,
                environment={
                    "CELERY_BROKER_URL": self.config.broker_url,
                    "CELERY_RESULT_BACKEND": self.config.result_backend,
                    "WORKER_NAME": worker_config.name,
                    "PYTHONPATH": "/app"
                },
                volumes={
                    "/app/logs": {"bind": "/app/logs", "mode": "rw"},
                    "/app/data": {"bind": "/app/data", "mode": "rw"}
                },
                networks=["ia-influencer-network"],
                restart_policy={"Name": "unless-stopped"},
                mem_limit="2g",
                cpus=worker_config.concurrency / 2
            )
            
            # Store worker information
            self.workers[worker_config.name] = {
                "container": container,
                "config": worker_config,
                "status": "running",
                "started_at": time.time()
            }
            
            logger.info(f"Worker {worker_config.name} deployed successfully")
            return {
                "container_id": container.id[:12],
                "status": "running",
                "queues": worker_config.queues,
                "concurrency": worker_config.concurrency
            }
            
        except Exception as e:
            logger.error(f"Failed to deploy worker {worker_config.name}: {e}")
            raise

    def _generate_worker_command(self, config: CeleryWorkerConfig) -> List[str]:
        """Generate Celery worker command"""
        command = [
            "celery", "-A", "backend.app.core.celery_app", "worker",
            "--hostname", f"{config.name}@%h",
            "--concurrency", str(config.concurrency),
            "--loglevel", config.loglevel,
            "--max-tasks-per-child", str(config.max_tasks_per_child),
            "--time-limit", str(config.time_limit),
            "--soft-time-limit", str(config.soft_time_limit),
            "--prefetch-multiplier", str(config.prefetch_multiplier),
            "--optimization", config.optimization
        ]
        
        if config.queues:
            command.extend(["--queues", ",".join(config.queues)])
            
        return command

    async def _validate_broker_connection(self) -> bool:
        """Validate connection to message broker"""
        try:
            with Connection(self.config.broker_url) as conn:
                conn.ensure_connection(max_retries=3)
            logger.info("Broker connection validated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to broker: {e}")
            raise

    async def _start_monitoring(self) -> None:
        """Start worker monitoring tasks"""
        try:
            # Start health monitoring
            health_task = asyncio.create_task(self._monitor_worker_health())
            self.monitoring_tasks.append(health_task)
            
            # Start performance monitoring
            perf_task = asyncio.create_task(self._monitor_performance())
            self.monitoring_tasks.append(perf_task)
            
            logger.info("Worker monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            raise

    async def _monitor_worker_health(self) -> None:
        """Monitor worker health continuously"""
        while True:
            try:
                for worker_name, worker_info in self.workers.items():
                    container = worker_info["container"]
                    container.reload()
                    
                    if container.status != "running":
                        logger.warning(f"Worker {worker_name} is not running, restarting...")
                        await self._restart_worker(worker_name)
                        
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(60)

    async def _monitor_performance(self) -> None:
        """Monitor worker performance metrics"""
        while True:
            try:
                for worker_name, worker_info in self.workers.items():
                    # Get worker stats
                    stats = await self._get_worker_stats(worker_name)
                    
                    # Check for performance issues
                    if stats.get("active_tasks", 0) > worker_info["config"].concurrency * 2:
                        logger.warning(f"Worker {worker_name} overloaded, considering scaling")
                        
                    if stats.get("memory_usage", 0) > 0.9:
                        logger.warning(f"Worker {worker_name} high memory usage")
                        
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(120)

    async def _enable_auto_scaling(self) -> None:
        """Enable auto-scaling based on queue length and worker load"""
        try:
            scaling_task = asyncio.create_task(self._auto_scale_workers())
            self.monitoring_tasks.append(scaling_task)
            logger.info("Auto-scaling enabled")
            
        except Exception as e:
            logger.error(f"Failed to enable auto-scaling: {e}")
            raise

    async def _auto_scale_workers(self) -> None:
        """Auto-scale workers based on demand"""
        while True:
            try:
                # Get queue lengths
                queue_stats = await self._get_queue_stats()
                
                # Calculate scaling decisions
                scaling_decision = self._calculate_scaling_decision(queue_stats)
                
                if scaling_decision["action"] == "scale_up":
                    await self._scale_up_workers(scaling_decision["count"])
                elif scaling_decision["action"] == "scale_down":
                    await self._scale_down_workers(scaling_decision["count"])
                    
                await asyncio.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                logger.error(f"Error in auto-scaling: {e}")
                await asyncio.sleep(300)

    def _calculate_scaling_decision(self, queue_stats: Dict[str, int]) -> Dict[str, Union[str, int]]:
        """Calculate scaling decision based on queue stats"""
        total_pending = sum(queue_stats.values())
        active_workers = len([w for w in self.workers.values() if w["status"] == "running"])
        
        # Scale up if average queue length > 10 per worker
        if total_pending > active_workers * 10 and active_workers < self.config.max_workers:
            scale_count = min(3, self.config.max_workers - active_workers)
            return {"action": "scale_up", "count": scale_count}
            
        # Scale down if average queue length < 2 per worker
        elif total_pending < active_workers * 2 and active_workers > self.config.min_workers:
            scale_count = min(2, active_workers - self.config.min_workers)
            return {"action": "scale_down", "count": scale_count}
            
        return {"action": "none", "count": 0}

    async def get_cluster_status(self) -> Dict[str, Union[str, int, List[Dict]]]:
        """Get comprehensive cluster status"""
        try:
            worker_statuses = []
            
            for worker_name, worker_info in self.workers.items():
                container = worker_info["container"]
                container.reload()
                
                stats = await self._get_worker_stats(worker_name)
                
                worker_statuses.append({
                    "name": worker_name,
                    "status": container.status,
                    "uptime": time.time() - worker_info["started_at"],
                    "active_tasks": stats.get("active_tasks", 0),
                    "processed_tasks": stats.get("processed_tasks", 0),
                    "memory_usage": stats.get("memory_usage", 0),
                    "cpu_usage": stats.get("cpu_usage", 0),
                    "queues": worker_info["config"].queues
                })
                
            return {
                "cluster_status": "healthy",
                "total_workers": len(self.workers),
                "running_workers": len([w for w in worker_statuses if w["status"] == "running"]),
                "monitoring_enabled": self.config.monitoring_enabled,
                "auto_scaling_enabled": self.config.auto_scaling,
                "workers": worker_statuses
            }
            
        except Exception as e:
            logger.error(f"Failed to get cluster status: {e}")
            return {"cluster_status": "error", "error": str(e)}

    async def _get_worker_stats(self, worker_name: str) -> Dict[str, Union[int, float]]:
        """Get individual worker statistics"""
        try:
            # This would integrate with Celery's monitoring API
            # For now, return mock data
            return {
                "active_tasks": 2,
                "processed_tasks": 1500,
                "memory_usage": 0.65,
                "cpu_usage": 0.45
            }
            
        except Exception as e:
            logger.error(f"Failed to get worker stats for {worker_name}: {e}")
            return {}

    async def _get_queue_stats(self) -> Dict[str, int]:
        """Get queue length statistics"""
        try:
            # This would integrate with broker API to get queue lengths
            # For now, return mock data
            return {
                "content_processing": 15,
                "fingerprint_generation": 8,
                "ai_analysis": 12,
                "ml_inference": 6,
                "web_crawling": 20,
                "monitoring": 5,
                "notifications": 3,
                "alerts": 1,
                "revenue_calculation": 4,
                "payment_processing": 2
            }
            
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return {}

    async def _restart_worker(self, worker_name: str) -> bool:
        """Restart a specific worker"""
        try:
            if worker_name not in self.workers:
                raise ValueError(f"Worker {worker_name} not found")
                
            worker_info = self.workers[worker_name]
            container = worker_info["container"]
            
            # Stop and remove old container
            container.stop()
            container.remove()
            
            # Deploy new worker
            result = await self._deploy_worker(worker_info["config"])
            
            logger.info(f"Worker {worker_name} restarted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restart worker {worker_name}: {e}")
            return False

    async def _scale_up_workers(self, count: int) -> None:
        """Scale up workers by adding new instances"""
        try:
            for i in range(count):
                # Create new worker config based on load
                new_config = CeleryWorkerConfig(
                    name=f"dynamic_worker_{int(time.time())}{i}",
                    concurrency=4,
                    queues=["default", "content_processing"]
                )
                
                await self._deploy_worker(new_config)
                
            logger.info(f"Scaled up {count} workers")
            
        except Exception as e:
            logger.error(f"Failed to scale up workers: {e}")

    async def _scale_down_workers(self, count: int) -> None:
        """Scale down workers by removing least active instances"""
        try:
            # Find workers to remove (dynamic workers first)
            workers_to_remove = []
            for worker_name in list(self.workers.keys()):
                if worker_name.startswith("dynamic_worker_") and len(workers_to_remove) < count:
                    workers_to_remove.append(worker_name)
                    
            for worker_name in workers_to_remove:
                container = self.workers[worker_name]["container"]
                container.stop()
                container.remove()
                del self.workers[worker_name]
                
            logger.info(f"Scaled down {len(workers_to_remove)} workers")
            
        except Exception as e:
            logger.error(f"Failed to scale down workers: {e}")

    async def shutdown_cluster(self) -> Dict[str, Union[str, bool]]:
        """Gracefully shutdown the entire cluster"""
        try:
            logger.info("Starting cluster shutdown")
            
            # Stop monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
                
            # Stop all workers gracefully
            for worker_name, worker_info in self.workers.items():
                container = worker_info["container"]
                container.stop(timeout=30)
                container.remove()
                
            self.workers.clear()
            
            logger.info("Cluster shutdown completed")
            return {"status": "success", "message": "Cluster shutdown completed"}
            
        except Exception as e:
            logger.error(f"Error during cluster shutdown: {e}")
            return {"status": "error", "error": str(e)}

    def export_cluster_config(self) -> Dict:
        """Export current cluster configuration"""
        return {
            "cluster_config": self.config.dict(),
            "deployment_timestamp": time.time(),
            "workers_count": len(self.workers),
            "monitoring_enabled": self.config.monitoring_enabled
        }

    @classmethod
    def from_config_file(cls, config_path: str) -> "CeleryManager":
        """Create CeleryManager from configuration file"""
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        config = CeleryClusterConfig(**config_data)
        return cls(config)
