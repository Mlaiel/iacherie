"""🐳 Docker Container Manager - IA-Influencer-Agent Production Platform
=====================================================================
Expert: Lead DevOps Engineer + Docker Specialist + Kubernetes Expert
Creator: Fahed Mlaiel <mlaiel@live.de>
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Professional Docker container management for IA-Influencer multi-format 
content protection and monetization platform.

Enterprise container orchestration supporting:
- Multi-format content processing containers
- AI fingerprinting engine management
- Real-time scaling and health monitoring  
- Production-grade security and compliance
- Microservices lifecycle management
"""
import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import docker
from docker.errors import DockerException, APIError
import subprocess
import shlex
from pathlib import Path
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContainerStatus(Enum):
    """Container status enumeration"""    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    RESTARTING = "restarting"
    REMOVING = "removing"
    EXITED = "exited"
    DEAD = "dead"
    CREATED = "created"

class ServiceType(Enum):
    """Service type enumeration"""    API_GATEWAY = "api_gateway"
    BACKEND_SERVICE = "backend_service"
    AI_ENGINE = "ai_engine"
    FINGERPRINTING_ENGINE = "fingerprinting_engine"
    CONTENT_PROTECTION = "content_protection"
    MONETIZATION_ENGINE = "monetization_engine"
    DATABASE = "database"
    CACHE = "cache"
    SEARCH_ENGINE = "search_engine"
    MONITORING = "monitoring"
    WORKER = "worker"
    STORAGE = "storage"

@dataclass
class ContainerConfig:
    """Container configuration data structure"""    name: str
    image: str
    service_type: ServiceType
    ports: Dict[str, str] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    volumes: Dict[str, str] = field(default_factory=dict)
    networks: List[str] = field(default_factory=list)
    restart_policy: str = "unless-stopped"
    memory_limit: str = "1g"
    cpu_limit: str = "1.0"
    healthcheck: Dict[str, Any] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    command: Optional[str] = None
    entrypoint: Optional[str] = None

@dataclass
class ContainerMetrics:
    """Container performance metrics"""    container_id: str
    name: str
    cpu_percent: float
    memory_usage: int
    memory_limit: int
    memory_percent: float
    network_rx_bytes: int
    network_tx_bytes: int
    block_read_bytes: int
    block_write_bytes: int
    timestamp: datetime

class DockerContainerManager:
    """    Enterprise Docker container management system
    
    Provides comprehensive container lifecycle management with:
    - Multi-service container orchestration
    - Health monitoring and auto-recovery
    - Performance metrics collection
    - Security and compliance management
    - Automatic scaling capabilities
    """    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize container manager with optional configuration"""        self.logger = logger
        self.config_path = config_path or Path(__file__).parent / "config"
        self.containers: Dict[str, ContainerConfig] = {}
        self.running_containers: Dict[str, Any] = {}
        
        try:
            self.client = docker.from_env()
            self.client.ping()
            self.logger.info("✅ Docker client connected successfully")
        except DockerException as e:
            self.logger.error(f"❌ Failed to connect to Docker: {e}")
            raise
    
    async def register_container(self, config: ContainerConfig) -> str:
        """Register a new container configuration"""        try:
            self.containers[config.name] = config
            self.logger.info(f"📝 Registered container: {config.name}")
            return config.name
        except Exception as e:
            self.logger.error(f"❌ Failed to register container {config.name}: {e}")
            raise
    
    async def create_container(self, name: str, **kwargs) -> str:
        """Create a new container from registered configuration"""        if name not in self.containers:
            raise ValueError(f"Container configuration not found: {name}")
        
        config = self.containers[name]
        
        try:
            # Prepare container arguments
            container_args = {
                'image': config.image,
                'name': config.name,
                'ports': config.ports,
                'environment': config.environment,
                'volumes': config.volumes,
                'restart_policy': {"Name": config.restart_policy},
                'mem_limit': config.memory_limit,
                'cpu_period': 100000,
                'cpu_quota': int(float(config.cpu_limit) * 100000),
                'labels': config.labels,
                'detach': True
            }
            
            # Add optional parameters
            if config.command:
                container_args['command'] = config.command
            if config.entrypoint:
                container_args['entrypoint'] = config.entrypoint
            if config.healthcheck:
                container_args['healthcheck'] = config.healthcheck
            
            # Override with provided kwargs
            container_args.update(kwargs)
            
            # Create container
            container = self.client.containers.create(**container_args)
            container_id = container.id
            
            self.running_containers[name] = container
            self.logger.info(f"🐳 Created container: {name} ({container_id[:12]})")
            
            return container_id
            
        except APIError as e:
            self.logger.error(f"❌ Failed to create container {name}: {e}")
            raise
    
    async def start_container(self, name: str) -> bool:
        """Start a registered container"""        try:
            if name in self.running_containers:
                container = self.running_containers[name]
            else:
                # Try to find existing container
                try:
                    container = self.client.containers.get(name)
                    self.running_containers[name] = container
                except docker.errors.NotFound:
                    # Create new container if not found
                    await self.create_container(name)
                    container = self.running_containers[name]
            
            container.start()
            self.logger.info(f"▶️ Started container: {name}")
            
            # Wait for container to be healthy
            await self._wait_for_healthy(name)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start container {name}: {e}")
            return False
    
    async def stop_container(self, name: str, timeout: int = 30) -> bool:
        """Stop a running container"""        try:
            if name not in self.running_containers:
                self.logger.warning(f"⚠️ Container not found in running containers: {name}")
                return False
            
            container = self.running_containers[name]
            container.stop(timeout=timeout)
            
            self.logger.info(f"⏹️ Stopped container: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop container {name}: {e}")
            return False
    
    async def restart_container(self, name: str, timeout: int = 30) -> bool:
        """Restart a container"""        try:
            if name not in self.running_containers:
                return await self.start_container(name)
            
            container = self.running_containers[name]
            container.restart(timeout=timeout)
            
            self.logger.info(f"🔄 Restarted container: {name}")
            
            # Wait for container to be healthy
            await self._wait_for_healthy(name)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to restart container {name}: {e}")
            return False
    
    async def remove_container(self, name: str, force: bool = False) -> bool:
        """Remove a container"""        try:
            if name in self.running_containers:
                container = self.running_containers[name]
                container.remove(force=force)
                del self.running_containers[name]
            
            self.logger.info(f"🗑️ Removed container: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to remove container {name}: {e}")
            return False
    
    async def get_container_status(self, name: str) -> Optional[ContainerStatus]:
        """Get current status of a container"""        try:
            if name not in self.running_containers:
                return None
            
            container = self.running_containers[name]
            container.reload()
            status = container.status
            
            # Map Docker status to our enum
            status_mapping = {
                'running': ContainerStatus.RUNNING,
                'stopped': ContainerStatus.STOPPED,
                'paused': ContainerStatus.PAUSED,
                'restarting': ContainerStatus.RESTARTING,
                'removing': ContainerStatus.REMOVING,
                'exited': ContainerStatus.EXITED,
                'dead': ContainerStatus.DEAD,
                'created': ContainerStatus.CREATED
            }
            
            return status_mapping.get(status.lower(), ContainerStatus.EXITED)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get container status {name}: {e}")
            return None
    
    async def get_container_metrics(self, name: str) -> Optional[ContainerMetrics]:
        """Get performance metrics for a container"""        try:
            if name not in self.running_containers:
                return None
            
            container = self.running_containers[name]
            stats = container.stats(stream=False)
            
            # Calculate CPU percentage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            
            cpu_percent = 0.0
            if system_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * 100.0
            
            # Memory metrics
            memory_usage = stats['memory_stats']['usage']
            memory_limit = stats['memory_stats']['limit']
            memory_percent = (memory_usage / memory_limit) * 100.0
            
            # Network metrics
            network_rx = stats['networks']['eth0']['rx_bytes'] if 'networks' in stats else 0
            network_tx = stats['networks']['eth0']['tx_bytes'] if 'networks' in stats else 0
            
            # Block I/O metrics
            block_read = stats['blkio_stats']['io_service_bytes_recursive'][0]['value'] if 'blkio_stats' in stats else 0
            block_write = stats['blkio_stats']['io_service_bytes_recursive'][1]['value'] if 'blkio_stats' in stats else 0
            
            return ContainerMetrics(
                container_id=container.id,
                name=name,
                cpu_percent=cpu_percent,
                memory_usage=memory_usage,
                memory_limit=memory_limit,
                memory_percent=memory_percent,
                network_rx_bytes=network_rx,
                network_tx_bytes=network_tx,
                block_read_bytes=block_read,
                block_write_bytes=block_write,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get container metrics {name}: {e}")
            return None
    
    async def get_container_logs(self, name: str, lines: int = 100) -> Optional[str]:
        """Get recent logs from a container"""        try:
            if name not in self.running_containers:
                return None
            
            container = self.running_containers[name]
            logs = container.logs(tail=lines, timestamps=True).decode('utf-8')
            
            return logs
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get container logs {name}: {e}")
            return None
    
    async def execute_command(self, name: str, command: str) -> Optional[str]:
        """Execute a command inside a container"""        try:
            if name not in self.running_containers:
                return None
            
            container = self.running_containers[name]
            result = container.exec_run(command)
            
            return result.output.decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"❌ Failed to execute command in container {name}: {e}")
            return None
    
    async def health_check(self, name: str) -> bool:
        """Perform health check on a container"""        try:
            status = await self.get_container_status(name)
            if status != ContainerStatus.RUNNING:
                return False
            
            # Check if container has custom health check
            if name in self.containers:
                config = self.containers[name]
                if config.healthcheck:
                    # Execute health check command
                    result = await self.execute_command(name, config.healthcheck.get('test', 'echo healthy'))
                    return 'healthy' in result.lower() if result else False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed for container {name}: {e}")
            return False
    
    async def auto_recover(self, name: str) -> bool:
        """Automatically recover a failed container"""        try:
            self.logger.info(f"🔧 Attempting auto-recovery for container: {name}")
            
            # Stop container if running
            await self.stop_container(name)
            
            # Wait a bit
            await asyncio.sleep(5)
            
            # Start container again
            success = await self.start_container(name)
            
            if success:
                self.logger.info(f"✅ Auto-recovery successful for container: {name}")
            else:
                self.logger.error(f"❌ Auto-recovery failed for container: {name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Auto-recovery error for container {name}: {e}")
            return False
    
    async def _wait_for_healthy(self, name: str, timeout: int = 60) -> bool:
        """Wait for container to become healthy"""        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout:
            if await self.health_check(name):
                self.logger.info(f"✅ Container {name} is healthy")
                return True
            
            await asyncio.sleep(2)
        
        self.logger.warning(f"⚠️ Container {name} did not become healthy within {timeout}s")
        return False
    
    async def monitor_containers(self) -> Dict[str, ContainerMetrics]:
        """Monitor all registered containers and return metrics"""        metrics = {}
        
        for name in self.running_containers:
            container_metrics = await self.get_container_metrics(name)
            if container_metrics:
                metrics[name] = container_metrics
        
        return metrics
    
    async def scale_service(self, service_type: ServiceType, replicas: int) -> bool:
        """Scale a service to specified number of replicas"""        try:
            # Find containers of specified service type
            service_containers = [
                name for name, config in self.containers.items()
                if config.service_type == service_type
            ]
            
            current_replicas = len(service_containers)
            
            if replicas > current_replicas:
                # Scale up - create new containers
                for i in range(current_replicas, replicas):
                    # Create new container config based on existing one
                    if service_containers:
                        base_config = self.containers[service_containers[0]]
                        new_name = f"{base_config.name}-{i+1}"
                        
                        new_config = ContainerConfig(
                            name=new_name,
                            image=base_config.image,
                            service_type=base_config.service_type,
                            ports={},  # Will need port management
                            environment=base_config.environment,
                            volumes=base_config.volumes,
                            networks=base_config.networks,
                            restart_policy=base_config.restart_policy,
                            memory_limit=base_config.memory_limit,
                            cpu_limit=base_config.cpu_limit,
                            healthcheck=base_config.healthcheck,
                            labels=base_config.labels,
                            command=base_config.command,
                            entrypoint=base_config.entrypoint
                        )
                        
                        await self.register_container(new_config)
                        await self.start_container(new_name)
            
            elif replicas < current_replicas:
                # Scale down - remove excess containers
                containers_to_remove = service_containers[replicas:]
                for name in containers_to_remove:
                    await self.stop_container(name)
                    await self.remove_container(name)
            
            self.logger.info(f"📊 Scaled {service_type.value} service to {replicas} replicas")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to scale service {service_type.value}: {e}")
            return False
    
    async def cleanup_orphaned_containers(self) -> int:
        """Remove orphaned containers that are no longer needed"""        cleaned_count = 0
        
        try:
            # Get all containers
            all_containers = self.client.containers.list(all=True)
            
            for container in all_containers:
                # Check if container belongs to our system
                labels = container.labels
                if 'ia-influencer-agent' in labels.get('project', ''):
                    # Check if container is in our registry
                    if container.name not in self.containers:
                        # This is an orphaned container
                        self.logger.info(f"🧹 Removing orphaned container: {container.name}")
                        container.remove(force=True)
                        cleaned_count += 1
            
            self.logger.info(f"✅ Cleaned up {cleaned_count} orphaned containers")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to cleanup orphaned containers: {e}")
        
        return cleaned_count
    
    async def backup_container_configs(self, backup_path: Path) -> bool:
        """Backup container configurations to file"""        try:
            backup_data = {
                'containers': {},
                'timestamp': datetime.now().isoformat(),
                'version': '2.0.0'
            }
            
            for name, config in self.containers.items():
                backup_data['containers'][name] = {
                    'name': config.name,
                    'image': config.image,
                    'service_type': config.service_type.value,
                    'ports': config.ports,
                    'environment': config.environment,
                    'volumes': config.volumes,
                    'networks': config.networks,
                    'restart_policy': config.restart_policy,
                    'memory_limit': config.memory_limit,
                    'cpu_limit': config.cpu_limit,
                    'healthcheck': config.healthcheck,
                    'labels': config.labels,
                    'command': config.command,
                    'entrypoint': config.entrypoint
                }
            
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            with open(backup_path, 'w') as f:
                yaml.dump(backup_data, f, default_flow_style=False)
            
            self.logger.info(f"💾 Container configurations backed up to {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to backup container configs: {e}")
            return False
    
    async def restore_container_configs(self, backup_path: Path) -> bool:
        """Restore container configurations from backup file"""        try:
            with open(backup_path, 'r') as f:
                backup_data = yaml.load(f, Loader=yaml.SafeLoader)
            
            for name, config_data in backup_data['containers'].items():
                config = ContainerConfig(
                    name=config_data['name'],
                    image=config_data['image'],
                    service_type=ServiceType(config_data['service_type']),
                    ports=config_data.get('ports', {}),
                    environment=config_data.get('environment', {}),
                    volumes=config_data.get('volumes', {}),
                    networks=config_data.get('networks', []),
                    restart_policy=config_data.get('restart_policy', 'unless-stopped'),
                    memory_limit=config_data.get('memory_limit', '1g'),
                    cpu_limit=config_data.get('cpu_limit', '1.0'),
                    healthcheck=config_data.get('healthcheck', {}),
                    labels=config_data.get('labels', {}),
                    command=config_data.get('command'),
                    entrypoint=config_data.get('entrypoint')
                )
                
                await self.register_container(config)
            
            self.logger.info(f"📥 Container configurations restored from {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to restore container configs: {e}")
            return False

# Global container manager instance
_container_manager: Optional[DockerContainerManager] = None

def get_container_manager() -> DockerContainerManager:
    """Get global container manager instance"""    global _container_manager
    if _container_manager is None:
        _container_manager = DockerContainerManager()
    return _container_manager

async def initialize_container_manager(config_path: Optional[Path] = None) -> DockerContainerManager:
    """Initialize container manager with configuration"""    global _container_manager
    _container_manager = DockerContainerManager(config_path)
    return _container_manager

# Convenience functions for common operations
async def start_service(service_type: ServiceType) -> bool:
    """Start all containers of specified service type"""    manager = get_container_manager()
    
    service_containers = [
        name for name, config in manager.containers.items()
        if config.service_type == service_type
    ]
    
    success = True
    for name in service_containers:
        if not await manager.start_container(name):
            success = False
    
    return success

async def stop_service(service_type: ServiceType) -> bool:
    """Stop all containers of specified service type"""    manager = get_container_manager()
    
    service_containers = [
        name for name, config in manager.containers.items()
        if config.service_type == service_type
    ]
    
    success = True
    for name in service_containers:
        if not await manager.stop_container(name):
            success = False
    
    return success

async def restart_service(service_type: ServiceType) -> bool:
    """Restart all containers of specified service type"""    manager = get_container_manager()
    
    service_containers = [
        name for name, config in manager.containers.items()
        if config.service_type == service_type
    ]
    
    success = True
    for name in service_containers:
        if not await manager.restart_container(name):
            success = False
    
    return success

# Export container manager singleton
container_manager = get_container_manager()
