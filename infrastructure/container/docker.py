"""Docker Infrastructure Management - Consolidated Module
=======================================================
All Docker functionality consolidated into a single module

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
License: Proprietary - All rights reserved
"""

import asyncio
import logging
import os
import subprocess
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import yaml

# Docker client imports (would be available in production)
try:
    import docker
    from docker.errors import DockerException, ImageNotFound, ContainerError
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    logging.warning("Docker client not available. Running in simulation mode.")

class ContainerStatus(Enum):
    """Container status enumeration"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    RESTARTING = "restarting"
    REMOVING = "removing"
    DEAD = "dead"
    EXITED = "exited"

class ImageType(Enum):
    """Docker image types"""
    APPLICATION = "application"
    DATABASE = "database"
    CACHE = "cache"
    PROXY = "proxy"
    MONITORING = "monitoring"
    SECURITY = "security"
    AI_ENGINE = "ai_engine"
    WORKER = "worker"

class RegistryType(Enum):
    """Container registry types"""
    DOCKER_HUB = "docker_hub"
    AWS_ECR = "aws_ecr"
    GCP_GCR = "gcp_gcr"
    AZURE_ACR = "azure_acr"
    HARBOR = "harbor"
    GITLAB = "gitlab"

@dataclass
class ContainerConfig:
    """Container configuration"""
    name: str
    image: str
    ports: Dict[str, str] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    volumes: Dict[str, Dict[str, str]] = field(default_factory=dict)
    networks: List[str] = field(default_factory=list)
    restart_policy: str = "unless-stopped"
    memory_limit: Optional[str] = None
    cpu_limit: Optional[str] = None
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class ImageBuildConfig:
    """Docker image build configuration"""
    name: str
    tag: str
    dockerfile_path: str
    context_path: str
    build_args: Dict[str, str] = field(default_factory=dict)
    target: Optional[str] = None
    platform: Optional[str] = None
    cache_from: List[str] = field(default_factory=list)

@dataclass
class ContainerMetrics:
    """Container runtime metrics"""
    cpu_percentage: float = 0.0
    memory_usage: int = 0
    memory_limit: int = 0
    network_io: Dict[str, int] = field(default_factory=dict)
    block_io: Dict[str, int] = field(default_factory=dict)

class DockerManager:
    """Unified Docker management interface"""
    
    def __init__(self):
        self.client = None
        self.logger = logging.getLogger(__name__)
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Docker client"""
        if not DOCKER_AVAILABLE:
            self.logger.warning("Docker client not available")
            return
            
        try:
            self.client = docker.from_env()
            self.logger.info("Docker client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Docker client: {e}")

class ContainerManager:
    """Docker container management"""
    
    def __init__(self, docker_manager: DockerManager):
        self.docker_manager = docker_manager
        self.logger = logging.getLogger(__name__)
    
    async def create_container(self, config: ContainerConfig) -> bool:
        """Create and start a Docker container"""
        try:
            if not self.docker_manager.client:
                self.logger.error("Docker client not available")
                return False
            
            container = self.docker_manager.client.containers.run(
                image=config.image,
                name=config.name,
                ports=config.ports,
                environment=config.environment,
                volumes=config.volumes,
                network=config.networks[0] if config.networks else None,
                restart_policy={"Name": config.restart_policy},
                mem_limit=config.memory_limit,
                labels=config.labels,
                detach=True
            )
            
            self.logger.info(f"Container {config.name} created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create container {config.name}: {e}")
            return False
    
    async def get_container_status(self, container_name: str) -> Optional[ContainerStatus]:
        """Get container status"""
        try:
            if not self.docker_manager.client:
                return None
                
            container = self.docker_manager.client.containers.get(container_name)
            status = container.status.lower()
            
            # Map Docker status to our enum
            status_mapping = {
                'created': ContainerStatus.CREATED,
                'running': ContainerStatus.RUNNING,
                'paused': ContainerStatus.PAUSED,
                'restarting': ContainerStatus.RESTARTING,
                'removing': ContainerStatus.REMOVING,
                'dead': ContainerStatus.DEAD,
                'exited': ContainerStatus.EXITED
            }
            
            return status_mapping.get(status, ContainerStatus.EXITED)
            
        except Exception as e:
            self.logger.error(f"Failed to get container status: {e}")
            return None
    
    async def stop_container(self, container_name: str) -> bool:
        """Stop a container"""
        try:
            if not self.docker_manager.client:
                return False
                
            container = self.docker_manager.client.containers.get(container_name)
            container.stop()
            self.logger.info(f"Container {container_name} stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop container {container_name}: {e}")
            return False
    
    async def restart_container(self, container_name: str) -> bool:
        """Restart a container"""
        try:
            if not self.docker_manager.client:
                return False
                
            container = self.docker_manager.client.containers.get(container_name)
            container.restart()
            self.logger.info(f"Container {container_name} restarted")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restart container {container_name}: {e}")
            return False

class ImageBuilder:
    """Docker image building and management"""
    
    def __init__(self, docker_manager: DockerManager):
        self.docker_manager = docker_manager
        self.logger = logging.getLogger(__name__)
    
    async def build_image(self, config: ImageBuildConfig) -> bool:
        """Build Docker image"""
        try:
            if not self.docker_manager.client:
                self.logger.error("Docker client not available")
                return False
            
            full_tag = f"{config.name}:{config.tag}"
            
            # Build the image
            image, build_logs = self.docker_manager.client.images.build(
                path=config.context_path,
                dockerfile=config.dockerfile_path,
                tag=full_tag,
                buildargs=config.build_args,
                target=config.target,
                platform=config.platform,
                cache_from=config.cache_from
            )
            
            # Log build output
            for log in build_logs:
                if 'stream' in log:
                    self.logger.info(log['stream'].strip())
            
            self.logger.info(f"Image {full_tag} built successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to build image {config.name}:{config.tag}: {e}")
            return False
    
    async def push_image(self, image_name: str, tag: str, registry_url: Optional[str] = None) -> bool:
        """Push image to registry"""
        try:
            if not self.docker_manager.client:
                return False
            
            if registry_url:
                full_name = f"{registry_url}/{image_name}:{tag}"
            else:
                full_name = f"{image_name}:{tag}"
            
            # Tag image for registry
            image = self.docker_manager.client.images.get(f"{image_name}:{tag}")
            image.tag(full_name)
            
            # Push image
            push_logs = self.docker_manager.client.images.push(full_name, stream=True, decode=True)
            
            for log in push_logs:
                if 'status' in log:
                    self.logger.info(f"Push status: {log['status']}")
            
            self.logger.info(f"Image {full_name} pushed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to push image {image_name}:{tag}: {e}")
            return False

class RegistryManager:
    """Container registry management"""
    
    def __init__(self, docker_manager: DockerManager):
        self.docker_manager = docker_manager
        self.logger = logging.getLogger(__name__)
    
    async def login_registry(self, 
                           registry_url: str,
                           username: str,
                           password: str,
                           registry_type: RegistryType = RegistryType.DOCKER_HUB) -> bool:
        """Login to container registry"""
        try:
            if not self.docker_manager.client:
                return False
            
            self.docker_manager.client.login(
                username=username,
                password=password,
                registry=registry_url
            )
            
            self.logger.info(f"Successfully logged into {registry_type.value} registry")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to login to registry: {e}")
            return False
    
    async def pull_image(self, image_name: str, tag: str = "latest") -> bool:
        """Pull image from registry"""
        try:
            if not self.docker_manager.client:
                return False
            
            full_name = f"{image_name}:{tag}"
            self.docker_manager.client.images.pull(full_name)
            
            self.logger.info(f"Image {full_name} pulled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to pull image {image_name}:{tag}: {e}")
            return False

class DockerComposeManager:
    """Docker Compose management"""
    
    def __init__(self, docker_manager: DockerManager):
        self.docker_manager = docker_manager
        self.logger = logging.getLogger(__name__)
    
    async def deploy_compose(self, compose_file_path: str, project_name: Optional[str] = None) -> bool:
        """Deploy Docker Compose stack"""
        try:
            cmd = ["docker-compose", "-f", compose_file_path]
            
            if project_name:
                cmd.extend(["-p", project_name])
            
            cmd.append("up")
            cmd.extend(["-d", "--remove-orphans"])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            self.logger.info(f"Docker Compose stack deployed successfully")
            self.logger.debug(f"Compose output: {result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to deploy Compose stack: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to deploy Compose stack: {e}")
            return False
    
    async def stop_compose(self, compose_file_path: str, project_name: Optional[str] = None) -> bool:
        """Stop Docker Compose stack"""
        try:
            cmd = ["docker-compose", "-f", compose_file_path]
            
            if project_name:
                cmd.extend(["-p", project_name])
            
            cmd.append("down")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            self.logger.info(f"Docker Compose stack stopped successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to stop Compose stack: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to stop Compose stack: {e}")
            return False

# Service-specific Docker configurations consolidated from original modules

class AIEnginesDockerConfig:
    """AI engines Docker configuration"""
    
    @staticmethod
    def get_ai_processing_config() -> ContainerConfig:
        """AI processing container configuration"""
        return ContainerConfig(
            name="ai-processing-engine",
            image="ainflue/ai-processing:latest",
            ports={"8080": "8080", "9090": "9090"},
            environment={
                "AI_MODEL_PATH": "/models",
                "PROCESSING_WORKERS": "4",
                "CUDA_VISIBLE_DEVICES": "0"
            },
            volumes={
                "/data/models": {"bind": "/models", "mode": "ro"},
                "/data/temp": {"bind": "/tmp", "mode": "rw"}
            },
            memory_limit="4g",
            labels={"service": "ai-processing", "tier": "compute"}
        )

class MonitoringStackDockerConfig:
    """Monitoring stack Docker configuration"""
    
    @staticmethod
    def get_prometheus_config() -> ContainerConfig:
        """Prometheus container configuration"""
        return ContainerConfig(
            name="prometheus",
            image="prom/prometheus:latest",
            ports={"9090": "9090"},
            volumes={
                "/data/prometheus": {"bind": "/prometheus", "mode": "rw"},
                "/config/prometheus.yml": {"bind": "/etc/prometheus/prometheus.yml", "mode": "ro"}
            },
            labels={"service": "monitoring", "component": "prometheus"}
        )
    
    @staticmethod
    def get_grafana_config() -> ContainerConfig:
        """Grafana container configuration"""
        return ContainerConfig(
            name="grafana",
            image="grafana/grafana:latest",
            ports={"3000": "3000"},
            environment={
                "GF_SECURITY_ADMIN_PASSWORD": "admin",
                "GF_INSTALL_PLUGINS": "grafana-piechart-panel"
            },
            volumes={
                "/data/grafana": {"bind": "/var/lib/grafana", "mode": "rw"}
            },
            labels={"service": "monitoring", "component": "grafana"}
        )

class DatabaseClusterDockerConfig:
    """Database cluster Docker configuration"""
    
    @staticmethod
    def get_postgresql_config() -> ContainerConfig:
        """PostgreSQL container configuration"""
        return ContainerConfig(
            name="postgresql-main",
            image="postgres:15-alpine",
            ports={"5432": "5432"},
            environment={
                "POSTGRES_DB": "ainflue",
                "POSTGRES_USER": "ainflue_user",
                "POSTGRES_PASSWORD": "secure_password",
                "POSTGRES_INITDB_ARGS": "--encoding=UTF-8"
            },
            volumes={
                "/data/postgresql": {"bind": "/var/lib/postgresql/data", "mode": "rw"}
            },
            labels={"service": "database", "component": "postgresql"}
        )
    
    @staticmethod
    def get_redis_config() -> ContainerConfig:
        """Redis container configuration"""
        return ContainerConfig(
            name="redis-cache",
            image="redis:7-alpine",
            ports={"6379": "6379"},
            volumes={
                "/data/redis": {"bind": "/data", "mode": "rw"}
            },
            labels={"service": "cache", "component": "redis"}
        )

# Global instances for backward compatibility
docker_manager = DockerManager()
container_manager = ContainerManager(docker_manager)
image_builder = ImageBuilder(docker_manager)
registry_manager = RegistryManager(docker_manager)
compose_manager = DockerComposeManager(docker_manager)

def get_docker_manager() -> DockerManager:
    """Get global Docker manager instance"""
    return docker_manager

def initialize_docker_manager() -> DockerManager:
    """Initialize and return Docker manager"""
    global docker_manager
    docker_manager = DockerManager()
    return docker_manager

# Consolidated exports from original docker modules
__all__ = [
    "DockerManager",
    "ContainerManager",
    "ImageBuilder",
    "RegistryManager", 
    "DockerComposeManager",
    "ContainerConfig",
    "ImageBuildConfig",
    "ContainerMetrics",
    "ContainerStatus",
    "ImageType",
    "RegistryType",
    "AIEnginesDockerConfig",
    "MonitoringStackDockerConfig",
    "DatabaseClusterDockerConfig",
    "docker_manager",
    "container_manager",
    "image_builder",
    "registry_manager",
    "compose_manager",
    "get_docker_manager",
    "initialize_docker_manager"
]