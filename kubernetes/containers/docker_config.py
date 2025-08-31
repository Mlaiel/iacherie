"""🐳 Docker Configuration Manager - IA-Influencer-Agent Infrastructure
====================================================================
Expert: DevOps Engineer + Cloud Architect + Container Security
Creator: Fahed Mlaiel <mlaiel@live.de>
====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Professional Docker configuration and management for IA-Influencer-Agent platform.
"""
from typing import Dict, List, Optional, Any, Union, Tuple, Set
import asyncio
import logging
import json
import yaml
import os
import docker
import hashlib
import subprocess
import aiofiles
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
import concurrent.futures
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class DockerImageType(Enum):
    """Docker image types for IA-Influencer-Agent platform"""    WEB_API = "web-api"
    AI_ENGINE = "ai-engine"
    ML_WORKER = "ml-worker"
    AUDIO_PROCESSOR = "audio-processor"
    CONTENT_PROTECTION = "content-protection"
    FINGERPRINT_ENGINE = "fingerprint-engine"
    CRAWLER_SERVICE = "crawler-service"
    MONETIZATION_SERVICE = "monetization-service"
    REVENUE_TRACKER = "revenue-tracker"
    LICENSING_ENGINE = "licensing-engine"
    PLATFORM_DETECTOR = "platform-detector"
    AI_FINGERPRINT = "ai-fingerprint"
    VECTOR_MATCHER = "vector-matcher"
    WEB_SCRAPER = "web-scraper"
    CONTENT_SCANNER = "content-scanner"
    DATABASE = "database"
    CACHE = "cache"
    VECTOR_DB = "vector-db"
    MONITORING = "monitoring"
    NGINX_PROXY = "nginx-proxy"
    API_GATEWAY = "api-gateway"

class DockerBuildTarget(Enum):
    """Docker build targets for multi-stage builds"""    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
    SECURITY_SCAN = "security-scan"

class DockerRegistry(Enum):
    """Supported Docker registries"""    DOCKER_HUB = "docker.io"
    AWS_ECR = "ecr"
    GOOGLE_GCR = "gcr.io"
    AZURE_ACR = "acr"
    HARBOR = "harbor"
    PRIVATE = "private"

@dataclass
class DockerConfig:
    """Advanced Docker configuration for IA-Influencer services"""    name: str
    image: str
    tag: str
    image_type: DockerImageType
    build_target: DockerBuildTarget = DockerBuildTarget.PRODUCTION
    registry: DockerRegistry = DockerRegistry.PRIVATE
    base_image: str = "python:3.11-slim"
    working_dir: str = "/app"
    exposed_ports: List[int] = field(default_factory=list)
    environment_vars: Dict[str, str] = field(default_factory=dict)
    volumes: List[str] = field(default_factory=list)
    networks: List[str] = field(default_factory=list)
    security_options: Dict[str, Any] = field(default_factory=dict)
    health_check: Optional[Dict[str, Any]] = None
    resource_limits: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    build_args: Dict[str, str] = field(default_factory=dict)
    dockerfile_path: str = "Dockerfile"
    context_path: str = "."
    dependencies: List[str] = field(default_factory=list)
    gpu_required: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""        return asdict(self)
    
    def generate_dockerfile(self) -> str:
        """Generate Dockerfile content for this configuration."""        dockerfile_content = f"""# IA-Influencer-Agent {self.image_type.value} Service
# Creator: Fahed Mlaiel <mlaiel@live.de>
# Professional-grade multi-stage Docker build

# Base stage
FROM {self.base_image} AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL version="{self.tag}"
LABEL service="{self.name}"
LABEL platform="IA-Influencer-Agent"

# Security hardening
RUN addgroup --system --gid 1001 appgroup && \\
    adduser --system --uid 1001 --gid 1001 --no-create-home appuser

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    ca-certificates \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean

# Development stage
FROM base AS development
RUN apt-get update && apt-get install -y \\
    git \\
    vim \\
    htop \\
    && rm -rf /var/lib/apt/lists/*

# Testing stage  
FROM base AS testing
COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

# Security scan stage
FROM base AS security-scan
RUN apt-get update && apt-get install -y \\
    wget \\
    && wget -qO- https://github.com/aquasecurity/trivy/releases/latest/download/trivy_Linux-64bit.tar.gz | tar xz \\
    && mv trivy /usr/local/bin/

# Production stage
FROM base AS production
WORKDIR {self.working_dir}

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set ownership and permissions
RUN chown -R appuser:appgroup {self.working_dir} && \\
    chmod -R 755 {self.working_dir}

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
    CMD curl -f http://localhost:{self.exposed_ports[0] if self.exposed_ports else 8000}/health || exit 1

# Expose ports
{chr(10).join(f'EXPOSE {port}' for port in self.exposed_ports)}

# Environment variables
{chr(10).join(f'ENV {key}={value}' for key, value in self.environment_vars.items())}

# Run application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{self.exposed_ports[0] if self.exposed_ports else 8000}"]
"""        return dockerfile_content.strip()


@dataclass
class DockerBuildResult:
    """Docker build operation result"""    success: bool
    image_id: str
    image_size: int
    build_time: float
    logs: List[str]
    warnings: List[str]
    errors: List[str]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass 
class DockerRegistryCredentials:
    """Docker registry authentication credentials"""    registry_url: str
    username: str
    password: str
    email: Optional[str] = None
    auth_token: Optional[str] = None


class DockerConfigManager:
    """Enterprise-grade Docker configuration manager for IA-Influencer-Agent"""    
    def __init__(self, config_path: str = "/app/config/docker"):
        self.config_path = Path(config_path)
        self.client = None
        self.configs: Dict[str, DockerConfig] = {}
        self.initialized = False
        self.build_cache_enabled = True
        self.registry_credentials: Dict[str, DockerRegistryCredentials] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    async def initialize(self) -> bool:
        """Initialize Docker configuration manager with enterprise features"""        try:
            # Initialize Docker client with enhanced error handling
            try:
                self.client = docker.from_env()
                # Test Docker daemon connectivity
                self.client.ping()
            except docker.errors.DockerException as e:
                self.logger.error(f"❌ Docker daemon not accessible: {e}")
                return False
            
            # Create config directory structure
            self.config_path.mkdir(parents=True, exist_ok=True)
            (self.config_path / "services").mkdir(exist_ok=True)
            (self.config_path / "templates").mkdir(exist_ok=True)
            (self.config_path / "secrets").mkdir(exist_ok=True, mode=0o700)
            
            # Load existing configurations
            await self._load_configurations()
            
            # Load registry credentials
            await self._load_registry_credentials()
            
            # Generate IA-Influencer specific configurations
            await self._generate_ia_influencer_configs()
            
            # Validate Docker environment
            await self._validate_docker_environment()
            
            self.initialized = True
            self.logger.info("✅ DockerConfigManager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing DockerConfigManager: {e}")
            return False
    
    async def _load_configurations(self) -> None:
        """Load existing Docker configurations from filesystem"""        try:
            config_dir = self.config_path / "services"
            if not config_dir.exists():
                return
                
            config_files = config_dir.glob("*.yml")
            for config_file in config_files:
                async with aiofiles.open(config_file, 'r') as f:
                    content = await f.read()
                    config_data = yaml.safe_load(content)
                    service_name = config_file.stem
                    
                    # Validate and create DockerConfig
                    try:
                        docker_config = DockerConfig(**config_data)
                        self.configs[service_name] = docker_config
                        self.logger.debug(f"✅ Loaded config for {service_name}")
                    except TypeError as e:
                        self.logger.warning(f"⚠️ Invalid config format for {service_name}: {e}")
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Error loading configurations: {e}")
    
    async def _load_registry_credentials(self) -> None:
        """Load Docker registry credentials securely"""        try:
            credentials_file = self.config_path / "secrets" / "registry_credentials.yml"
            if credentials_file.exists():
                async with aiofiles.open(credentials_file, 'r') as f:
                    content = await f.read()
                    credentials_data = yaml.safe_load(content)
                    
                    for registry_name, creds in credentials_data.items():
                        self.registry_credentials[registry_name] = DockerRegistryCredentials(**creds)
                        
        except Exception as e:
            self.logger.warning(f"⚠️ Error loading registry credentials: {e}")
    
    async def _generate_ia_influencer_configs(self) -> None:
        """Generate Docker configurations for all IA-Influencer-Agent services"""        try:
            # Define service configurations based on cahier des charges
            service_definitions = {
                "web-api": {
                    "image_type": DockerImageType.WEB_API,
                    "base_image": "python:3.11-slim",
                    "exposed_ports": [8000, 9090],
                    "environment_vars": {
                        "ENVIRONMENT": "production",
                        "API_VERSION": "v1",
                        "METRICS_ENABLED": "true"
                    },
                    "resource_limits": {"memory": "2Gi", "cpu": "1000m"},
                    "dependencies": ["database", "cache"],
                    "health_check": {
                        "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3
                    }
                },
                "ai-engine": {
                    "image_type": DockerImageType.AI_ENGINE,
                    "base_image": "nvidia/cuda:11.8-runtime-ubuntu20.04",
                    "exposed_ports": [8001, 9091],
                    "environment_vars": {
                        "CUDA_VISIBLE_DEVICES": "0",
                        "AI_MODEL_PATH": "/app/models",
                        "GPU_MEMORY_FRACTION": "0.8"
                    },
                    "resource_limits": {"memory": "16Gi", "cpu": "4000m"},
                    "gpu_required": True,
                    "dependencies": ["vector-db", "cache"],
                    "volumes": ["/app/models:/app/models:ro"]
                },
                "content-protection": {
                    "image_type": DockerImageType.CONTENT_PROTECTION,
                    "base_image": "python:3.11-slim",
                    "exposed_ports": [8002, 9092],
                    "environment_vars": {
                        "FINGERPRINT_ENABLED": "true",
                        "SCAN_INTERVAL": "30",
                        "PROTECTION_LEVEL": "high"
                    },
                    "resource_limits": {"memory": "4Gi", "cpu": "2000m"},
                    "dependencies": ["ai-engine", "vector-db"]
                },
                "fingerprint-engine": {
                    "image_type": DockerImageType.FINGERPRINT_ENGINE,
                    "base_image": "python:3.11-slim",
                    "exposed_ports": [8003, 9093],
                    "environment_vars": {
                        "CHROMAPRINT_ENABLED": "true",
                        "OPENCV_ENABLED": "true",
                        "CLIP_MODEL": "ViT-B/32"
                    },
                    "resource_limits": {"memory": "8Gi", "cpu": "2000m"},
                    "dependencies": ["vector-db", "ai-engine"]
                },
                "crawler-service": {
                    "image_type": DockerImageType.CRAWLER_SERVICE,
                    "base_image": "python:3.11-slim",
                    "exposed_ports": [8004, 9094],
                    "environment_vars": {
                        "CRAWL_DELAY": "1",
                        "MAX_CONCURRENT": "10",
                        "RESPECT_ROBOTS_TXT": "true"
                    },
                    "resource_limits": {"memory": "4Gi", "cpu": "1000m"},
                    "dependencies": ["database", "content-protection"]
                },
                "monetization-service": {
                    "image_type": DockerImageType.MONETIZATION_SERVICE,
                    "base_image": "python:3.11-slim",
                    "exposed_ports": [8005, 9095],
                    "environment_vars": {
                        "PAYMENT_GATEWAY": "stripe",
                        "REVENUE_CALCULATION": "realtime",
                        "PAYOUT_SCHEDULE": "weekly"
                    },
                    "resource_limits": {"memory": "2Gi", "cpu": "1000m"},
                    "dependencies": ["database", "web-api"]
                },
                "vector-db": {
                    "image_type": DockerImageType.VECTOR_DB,
                    "base_image": "faiss-cpu:latest",
                    "exposed_ports": [9200, 9300],
                    "environment_vars": {
                        "FAISS_INDEX_TYPE": "IVF",
                        "VECTOR_DIMENSION": "512",
                        "ES_JAVA_OPTS": "-Xms2g -Xmx2g"
                    },
                    "resource_limits": {"memory": "8Gi", "cpu": "2000m"},
                    "volumes": ["/data/vector:/data:rw"]
                }
            }
            
            # Generate configurations for each service
            for service_name, service_def in service_definitions.items():
                if service_name not in self.configs:
                    config = DockerConfig(
                        name=service_name,
                        image=f"ia-influencer/{service_name}",
                        tag="v2.1.0",
                        **service_def
                    )
                    self.configs[service_name] = config
                    
                    # Save configuration to file
                    await self._save_config(service_name, config)
            
            self.logger.info("✅ IA-Influencer service configurations generated")
            
        except Exception as e:
            self.logger.error(f"❌ Error generating IA-Influencer configs: {e}")
            raise
    
    async def _validate_docker_environment(self) -> None:
        """Validate Docker environment for IA-Influencer-Agent requirements"""        try:
            # Check Docker version
            docker_version = self.client.version()
            self.logger.info(f"🐳 Docker version: {docker_version['Version']}")
            
            # Check available resources
            system_info = self.client.info()
            
            # Memory check (minimum 8GB recommended)
            total_memory = system_info.get('MemTotal', 0) / (1024**3)  # Convert to GB
            if total_memory < 8:
                self.logger.warning(f"⚠️ Low memory: {total_memory:.1f}GB (recommended: 8GB+)")
            
            # CPU check
            cpu_count = system_info.get('NCPU', 0)
            if cpu_count < 4:
                self.logger.warning(f"⚠️ Low CPU count: {cpu_count} (recommended: 4+)")
            
            # Storage check
            containers_running = len(self.client.containers.list())
            images_count = len(self.client.images.list())
            
            self.logger.info(f"📊 System: {cpu_count} CPUs, {total_memory:.1f}GB RAM")
            self.logger.info(f"📊 Docker: {containers_running} containers, {images_count} images")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error validating Docker environment: {e}")
    
    async def _save_config(self, service_name: str, config: DockerConfig) -> None:
        """Save Docker configuration to filesystem"""        try:
            config_file = self.config_path / "services" / f"{service_name}.yml"
            config_data = config.to_dict()
            
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(yaml.dump(config_data, default_flow_style=False))
                
        except Exception as e:
            self.logger.error(f"❌ Error saving config for {service_name}: {e}")
    
    async def get_config(self, service_name: str) -> Optional[DockerConfig]:
        """Get Docker configuration for a service"""        return self.configs.get(service_name)
    
    async def create_config(self, service_name: str, config: DockerConfig) -> bool:
        """Create new Docker configuration"""        try:
            self.configs[service_name] = config
            await self._save_config(service_name, config)
            self.logger.info(f"✅ Created config for {service_name}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error creating config for {service_name}: {e}")
            return False
    
    async def update_config(self, service_name: str, config: DockerConfig) -> bool:
        """Update existing Docker configuration"""        try:
            if service_name not in self.configs:
                return False
            
            config.updated_at = datetime.now()
            self.configs[service_name] = config
            await self._save_config(service_name, config)
            self.logger.info(f"✅ Updated config for {service_name}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error updating config for {service_name}: {e}")
            return False
    
    async def delete_config(self, service_name: str) -> bool:
        """Delete Docker configuration"""        try:
            if service_name in self.configs:
                del self.configs[service_name]
                
                config_file = self.config_path / "services" / f"{service_name}.yml"
                if config_file.exists():
                    config_file.unlink()
                
                self.logger.info(f"✅ Deleted config for {service_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Error deleting config for {service_name}: {e}")
            return False
    
    async def generate_dockerfile(self, service_name: str) -> Optional[str]:
        """Generate Dockerfile for a service"""        try:
            config = self.configs.get(service_name)
            if not config:
                return None
            
            dockerfile_content = config.generate_dockerfile()
            
            # Save Dockerfile
            dockerfile_path = self.config_path / "templates" / f"{service_name}.Dockerfile"
            async with aiofiles.open(dockerfile_path, 'w') as f:
                await f.write(dockerfile_content)
            
            return dockerfile_content
        except Exception as e:
            self.logger.error(f"❌ Error generating Dockerfile for {service_name}: {e}")
            return None
    
    async def generate_docker_compose(self, services: List[str] = None) -> Optional[str]:
        """Generate docker-compose.yml for specified services"""        try:
            if services is None:
                services = list(self.configs.keys())
            
            compose_config = {
                "version": "3.8",
                "services": {},
                "networks": {
                    "ia-influencer-network": {
                        "driver": "bridge"
                    }
                },
                "volumes": {}
            }
            
            for service_name in services:
                config = self.configs.get(service_name)
                if not config:
                    continue
                
                service_config = {
                    "image": f"{config.image}:{config.tag}",
                    "container_name": f"ia-influencer-{service_name}",
                    "restart": "unless-stopped",
                    "networks": ["ia-influencer-network"]
                }
                
                # Add ports
                if config.exposed_ports:
                    service_config["ports"] = [f"{port}:{port}" for port in config.exposed_ports]
                
                # Add environment variables
                if config.environment_vars:
                    service_config["environment"] = config.environment_vars
                
                # Add volumes
                if config.volumes:
                    service_config["volumes"] = config.volumes
                
                # Add dependencies
                if config.dependencies:
                    service_config["depends_on"] = config.dependencies
                
                # Add resource limits
                if config.resource_limits:
                    service_config["deploy"] = {
                        "resources": {
                            "limits": config.resource_limits
                        }
                    }
                
                # Add health check
                if config.health_check:
                    service_config["healthcheck"] = config.health_check
                
                compose_config["services"][service_name] = service_config
            
            # Convert to YAML
            compose_yaml = yaml.dump(compose_config, default_flow_style=False)
            
            # Save docker-compose.yml
            compose_file = self.config_path / "docker-compose.yml"
            async with aiofiles.open(compose_file, 'w') as f:
                await f.write(compose_yaml)
            
            return compose_yaml
            
        except Exception as e:
            self.logger.error(f"❌ Error generating docker-compose: {e}")
            return None
    
    async def list_configs(self) -> Dict[str, DockerConfig]:
        """List all Docker configurations"""        return self.configs.copy()


class DockerImageBuilder:
    """Professional Docker image builder with advanced features"""    
    def __init__(self, docker_client, registry_manager=None):
        self.client = docker_client
        self.registry_manager = registry_manager
        self.build_cache: Dict[str, DockerBuildResult] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def build_image(
        self,
        config: DockerConfig,
        context_path: str = ".",
        no_cache: bool = False,
        pull: bool = True,
        build_args: Dict[str, str] = None
    ) -> DockerBuildResult:
        """Build Docker image with advanced options"""        start_time = datetime.now()
        build_logs = []
        warnings = []
        errors = []
        
        try:
            self.logger.info(f"🔨 Building image: {config.image}:{config.tag}")
            
            # Prepare build arguments
            effective_build_args = {**config.build_args}
            if build_args:
                effective_build_args.update(build_args)
            
            # Generate Dockerfile content
            dockerfile_content = config.generate_dockerfile()
            
            # Create temporary Dockerfile
            dockerfile_path = Path(context_path) / "Dockerfile.tmp"
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            
            try:
                # Build the image
                image, build_logs_raw = self.client.images.build(
                    path=context_path,
                    dockerfile="Dockerfile.tmp",
                    tag=f"{config.image}:{config.tag}",
                    nocache=no_cache,
                    pull=pull,
                    buildargs=effective_build_args,
                    target=config.build_target.value if config.build_target else None
                )
                
                # Process build logs
                for log_entry in build_logs_raw:
                    if 'stream' in log_entry:
                        log_line = log_entry['stream'].strip()
                        build_logs.append(log_line)
                        
                        # Detect warnings and errors
                        if 'WARNING' in log_line.upper():
                            warnings.append(log_line)
                        elif 'ERROR' in log_line.upper():
                            errors.append(log_line)
                
                # Get image size
                image_size = image.attrs.get('Size', 0)
                
                # Calculate build time
                build_time = (datetime.now() - start_time).total_seconds()
                
                # Tag image with additional tags
                if config.registry != DockerRegistry.DOCKER_HUB:
                    registry_tag = f"{config.registry.value}/{config.image}:{config.tag}"
                    image.tag(registry_tag)
                
                build_result = DockerBuildResult(
                    success=True,
                    image_id=image.id,
                    image_size=image_size,
                    build_time=build_time,
                    logs=build_logs,
                    warnings=warnings,
                    errors=errors
                )
                
                # Cache build result
                cache_key = f"{config.image}:{config.tag}"
                self.build_cache[cache_key] = build_result
                
                self.logger.info(f"✅ Image built successfully: {config.image}:{config.tag}")
                self.logger.info(f"📊 Build time: {build_time:.2f}s, Size: {image_size / 1024 / 1024:.1f}MB")
                
                return build_result
                
            finally:
                # Clean up temporary Dockerfile
                if dockerfile_path.exists():
                    dockerfile_path.unlink()
                    
        except docker.errors.BuildError as e:
            self.logger.error(f"❌ Build failed for {config.image}:{config.tag}")
            for log_entry in e.build_log:
                if 'stream' in log_entry:
                    error_line = log_entry['stream'].strip()
                    errors.append(error_line)
                    self.logger.error(f"Build error: {error_line}")
            
            build_time = (datetime.now() - start_time).total_seconds()
            
            return DockerBuildResult(
                success=False,
                image_id="",
                image_size=0,
                build_time=build_time,
                logs=build_logs,
                warnings=warnings,
                errors=errors
            )
            
        except Exception as e:
            self.logger.error(f"❌ Unexpected build error: {e}")
            build_time = (datetime.now() - start_time).total_seconds()
            
            return DockerBuildResult(
                success=False,
                image_id="",
                image_size=0,
                build_time=build_time,
                logs=build_logs,
                warnings=warnings,
                errors=[str(e)]
            )
    
    async def build_multi_stage(
        self,
        config: DockerConfig,
        targets: List[DockerBuildTarget],
        context_path: str = "."
    ) -> Dict[DockerBuildTarget, DockerBuildResult]:
        """Build multiple stages of a multi-stage Dockerfile"""        results = {}
        
        for target in targets:
            target_config = config
            target_config.build_target = target
            target_config.tag = f"{config.tag}-{target.value}"
            
            result = await self.build_image(target_config, context_path)
            results[target] = result
        
        return results
    
    async def optimize_image_size(self, config: DockerConfig) -> DockerConfig:
        """Optimize Docker image for smaller size"""        optimized_config = config
        
        # Add optimization build args
        optimized_config.build_args.update({
            "PIP_NO_CACHE_DIR": "1",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONUNBUFFERED": "1"
        })
        
        # Optimize base image
        if "python" in config.base_image and "slim" not in config.base_image:
            optimized_config.base_image = config.base_image.replace("python:", "python:").replace("-", "-slim-")
        
        return optimized_config
    
    async def get_build_history(self, image_name: str) -> List[DockerBuildResult]:
        """Get build history for an image"""        history = []
        for cache_key, result in self.build_cache.items():
            if image_name in cache_key:
                history.append(result)
        
        return sorted(history, key=lambda x: x.created_at, reverse=True)


class DockerRegistryManager:
    """Professional Docker registry management"""    
    def __init__(self, default_registry: str = "registry.ia-influencer-agent.com"):
        self.default_registry = default_registry
        self.credentials: Dict[str, DockerRegistryCredentials] = {}
        self.client = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self, docker_client) -> bool:
        """Initialize registry manager"""        try:
            self.client = docker_client
            await self._load_credentials()
            self.logger.info("✅ DockerRegistryManager initialized")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error initializing registry manager: {e}")
            return False
    
    async def _load_credentials(self) -> None:
        """Load registry credentials"""        try:
            # Load from environment or config file
            # Implementation depends on security requirements
            pass
        except Exception as e:
            self.logger.warning(f"⚠️ Error loading credentials: {e}")
    
    async def login(self, registry_url: str, credentials: DockerRegistryCredentials) -> bool:
        """Login to Docker registry"""        try:
            self.client.login(
                username=credentials.username,
                password=credentials.password,
                email=credentials.email,
                registry=registry_url
            )
            
            self.credentials[registry_url] = credentials
            self.logger.info(f"✅ Logged in to registry: {registry_url}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Registry login failed for {registry_url}: {e}")
            return False
    
    async def push_image(self, image_name: str, tag: str, registry: str = None) -> bool:
        """Push image to registry"""        try:
            target_registry = registry or self.default_registry
            full_image_name = f"{target_registry}/{image_name}:{tag}"
            
            # Tag the image for the target registry
            image = self.client.images.get(f"{image_name}:{tag}")
            image.tag(full_image_name)
            
            # Push the image
            push_logs = self.client.images.push(full_image_name, stream=True, decode=True)
            
            for log_entry in push_logs:
                if 'error' in log_entry:
                    raise Exception(log_entry['error'])
                elif 'status' in log_entry:
                    self.logger.debug(f"Push status: {log_entry['status']}")
            
            self.logger.info(f"✅ Image pushed: {full_image_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Image push failed: {e}")
            return False
    
    async def pull_image(self, image_name: str, tag: str, registry: str = None) -> bool:
        """Pull image from registry"""        try:
            target_registry = registry or self.default_registry
            full_image_name = f"{target_registry}/{image_name}:{tag}"
            
            # Pull the image
            self.client.images.pull(full_image_name)
            
            self.logger.info(f"✅ Image pulled: {full_image_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Image pull failed: {e}")
            return False
    
    async def list_tags(self, image_name: str, registry: str = None) -> List[str]:
        """List available tags for an image"""        try:
            # Implementation depends on registry API
            # This is a placeholder for the actual implementation
            return []
        except Exception as e:
            self.logger.error(f"❌ Error listing tags: {e}")
            return []
    
    async def delete_image(self, image_name: str, tag: str, registry: str = None) -> bool:
        """Delete image from registry"""        try:
            # Implementation depends on registry API
            # This is a placeholder for the actual implementation
            self.logger.info(f"✅ Image deleted: {image_name}:{tag}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error deleting image: {e}")
            return False
    
    async def _generate_default_configs(self) -> None:
        """Generate default Docker configurations for IA-Influencer services"""        
        # Web API Service
        web_api_config = DockerConfig(
            name="ia-influencer-web-api",
            image="ia-influencer/web-api",
            tag="latest",
            ports=[{"container": 8000, "host": 8000}],
            environment={
                "ENVIRONMENT": "production",
                "DATABASE_URL": "postgresql://user:pass@postgres:5432/ia_influencer",
                "REDIS_URL": "redis://redis:6379/0",
                "JWT_SECRET": "${JWT_SECRET}",
                "API_VERSION": "v1",
                "MAX_WORKERS": "4"
            },
            volumes=[
                {"host": "./logs", "container": "/app/logs"},
                {"host": "./uploads", "container": "/app/uploads"}
            ],
            networks=["ia-influencer-network"],
            depends_on=["postgres", "redis"],
            health_check={
                "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            },
            security_options=["no-new-privileges:true"],
            labels={
                "service": "web-api",
                "version": "v1",
                "environment": "production"
            }
        )
        
        # AI Engine Service
        ai_engine_config = DockerConfig(
            name="ia-influencer-ai-engine",
            image="ia-influencer/ai-engine",
            tag="latest",
            ports=[{"container": 8001, "host": 8001}],
            environment={
                "HUGGINGFACE_TOKEN": "${HUGGINGFACE_TOKEN}",
                "OPENAI_API_KEY": "${OPENAI_API_KEY}",
                "MODEL_CACHE_PATH": "/app/models",
                "GPU_ENABLED": "true",
                "TORCH_DEVICE": "cuda"
            },
            volumes=[
                {"host": "./models", "container": "/app/models"},
                {"host": "./ai_cache", "container": "/app/cache"}
            ],
            networks=["ia-influencer-network"],
            depends_on=["redis"],
            memory_limit="4g",
            cpu_limit="2.0",
            health_check={
                "test": ["CMD", "python", "-c", "import torch; print('OK')"],
                "interval": "60s",
                "timeout": "30s",
                "retries": 2
            }
        )
        
        # Content Protection Service
        protection_config = DockerConfig(
            name="ia-influencer-content-protection",
            image="ia-influencer/content-protection",
            tag="latest",
            ports=[{"container": 8002, "host": 8002}],
            environment={
                "FINGERPRINT_ENGINE": "chromaprint",
                "VECTOR_DB_URL": "http://faiss:8000",
                "STORAGE_BACKEND": "s3",
                "AWS_ACCESS_KEY_ID": "${AWS_ACCESS_KEY_ID}",
                "AWS_SECRET_ACCESS_KEY": "${AWS_SECRET_ACCESS_KEY}"
            },
            volumes=[
                {"host": "./fingerprints", "container": "/app/fingerprints"},
                {"host": "./evidence", "container": "/app/evidence"}
            ],
            networks=["ia-influencer-network"],
            depends_on=["faiss", "postgres"],
            memory_limit="2g",
            cpu_limit="1.5"
        )
        
        # Audio Processor Service
        audio_processor_config = DockerConfig(
            name="ia-influencer-audio-processor",
            image="ia-influencer/audio-processor",
            tag="latest",
            ports=[{"container": 8003, "host": 8003}],
            environment={
                "AUDIO_FORMAT_SUPPORT": "mp3,wav,flac,aac,ogg",
                "MAX_FILE_SIZE": "100MB",
                "PROCESSING_QUEUE": "audio_processing",
                "ESSENTIA_MODELS_PATH": "/app/essentia_models"
            },
            volumes=[
                {"host": "./audio_temp", "container": "/app/temp"},
                {"host": "./audio_models", "container": "/app/essentia_models"}
            ],
            networks=["ia-influencer-network"],
            depends_on=["redis", "celery"],
            memory_limit="3g",
            cpu_limit="2.0"
        )
        
        # Database Service
        postgres_config = DockerConfig(
            name="ia-influencer-postgres",
            image="postgres",
            tag="15-alpine",
            ports=[{"container": 5432, "host": 5432}],
            environment={
                "POSTGRES_DB": "ia_influencer",
                "POSTGRES_USER": "ia_user",
                "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD}",
                "POSTGRES_INITDB_ARGS": "--encoding=UTF8 --locale=en_US.UTF-8"
            },
            volumes=[
                {"host": "./postgres_data", "container": "/var/lib/postgresql/data"},
                {"host": "./postgres_backup", "container": "/backup"}
            ],
            networks=["ia-influencer-network"],
            depends_on=[],
            health_check={
                "test": ["CMD-SHELL", "pg_isready -U ia_user -d ia_influencer"],
                "interval": "10s",
                "timeout": "5s",
                "retries": 5
            }
        )
        
        # Redis Cache Service
        redis_config = DockerConfig(
            name="ia-influencer-redis",
            image="redis",
            tag="7-alpine",
            ports=[{"container": 6379, "host": 6379}],
            environment={
                "REDIS_PASSWORD": "${REDIS_PASSWORD}"
            },
            volumes=[
                {"host": "./redis_data", "container": "/data"}
            ],
            networks=["ia-influencer-network"],
            depends_on=[],
            health_check={
                "test": ["CMD", "redis-cli", "ping"],
                "interval": "5s",
                "timeout": "3s",
                "retries": 3
            }
        )
        
        # Store configurations
        configs_to_store = {
            "web-api": web_api_config,
            "ai-engine": ai_engine_config,
            "content-protection": protection_config,
            "audio-processor": audio_processor_config,
            "postgres": postgres_config,
            "redis": redis_config
        }
        
        for name, config in configs_to_store.items():
            self.configs[name] = config
            await self._save_config(name, config)
    
    async def _save_config(self, name: str, config: DockerConfig) -> None:
        """Save Docker configuration to file"""        try:
            config_file = self.config_path / f"{name}.yml"
            with open(config_file, 'w') as f:
                yaml.dump(asdict(config), f, default_flow_style=False)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving config {name}: {e}")
    
    async def generate_docker_compose(self, services: List[str] = None) -> str:
        """Generate docker-compose.yml file"""        try:
            if services is None:
                services = list(self.configs.keys())
            
            compose_data = {
                "version": "3.8",
                "services": {},
                "networks": {
                    "ia-influencer-network": {
                        "driver": "bridge",
                        "ipam": {
                            "config": [{"subnet": "172.20.0.0/16"}]
                        }
                    }
                },
                "volumes": {}
            }
            
            for service_name in services:
                if service_name in self.configs:
                    config = self.configs[service_name]
                    service_def = {
                        "image": f"{config.image}:{config.tag}",
                        "container_name": config.name,
                        "restart": config.restart_policy,
                        "environment": config.environment,
                        "networks": config.networks,
                        "deploy": {
                            "resources": {
                                "limits": {
                                    "memory": config.memory_limit,
                                    "cpus": config.cpu_limit
                                }
                            }
                        }
                    }
                    
                    if config.ports:
                        service_def["ports"] = [
                            f"{port['host']}:{port['container']}" 
                            for port in config.ports
                        ]
                    
                    if config.volumes:
                        service_def["volumes"] = [
                            f"{vol['host']}:{vol['container']}" 
                            for vol in config.volumes
                        ]
                    
                    if config.depends_on:
                        service_def["depends_on"] = config.depends_on
                    
                    if config.health_check:
                        service_def["healthcheck"] = config.health_check
                    
                    if config.security_options:
                        service_def["security_opt"] = config.security_options
                    
                    if config.labels:
                        service_def["labels"] = config.labels
                    
                    compose_data["services"][service_name] = service_def
            
            # Save docker-compose.yml
            compose_file = self.config_path / "docker-compose.yml"
            with open(compose_file, 'w') as f:
                yaml.dump(compose_data, f, default_flow_style=False)
            
            self.logger.info(f"✅ Generated docker-compose.yml for {len(services)} services")
            return str(compose_file)
            
        except Exception as e:
            self.logger.error(f"❌ Error generating docker-compose: {e}")
            return ""
    
    async def get_service_config(self, service_name: str) -> Optional[DockerConfig]:
        """Get configuration for specific service"""        return self.configs.get(service_name)
    
    async def update_service_config(self, service_name: str, config: DockerConfig) -> bool:
        """Update configuration for specific service"""        try:
            self.configs[service_name] = config
            await self._save_config(service_name, config)
            self.logger.info(f"✅ Updated config for service: {service_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error updating service config: {e}")
            return False

class DockerImageBuilder:
    """Professional Docker image builder"""    
    def __init__(self, registry_url: str = None):
        self.registry_url = registry_url
        self.client = None
        self.build_cache = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self) -> bool:
        """Initialize Docker image builder"""        try:
            self.client = docker.from_env()
            self.logger.info("✅ DockerImageBuilder initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing DockerImageBuilder: {e}")
            return False
    
    async def build_image(
        self, 
        dockerfile_path: str, 
        image_name: str, 
        tag: str = "latest",
        build_args: Dict[str, str] = None,
        platform: str = "linux/amd64"
    ) -> bool:
        """Build Docker image"""        try:
            build_args = build_args or {}
            full_image_name = f"{image_name}:{tag}"
            
            self.logger.info(f"🔨 Building image: {full_image_name}")
            
            # Build image
            image, logs = self.client.images.build(
                path=str(Path(dockerfile_path).parent),
                dockerfile=str(Path(dockerfile_path).name),
                tag=full_image_name,
                buildargs=build_args,
                platform=platform,
                rm=True,
                pull=True
            )
            
            # Log build process
            for log in logs:
                if 'stream' in log:
                    self.logger.debug(log['stream'].strip())
            
            # Store in cache
            self.build_cache[full_image_name] = {
                'image_id': image.id,
                'build_time': datetime.now(),
                'size': image.attrs.get('Size', 0)
            }
            
            self.logger.info(f"✅ Successfully built image: {full_image_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error building image {image_name}: {e}")
            return False
    
    async def push_image(self, image_name: str, tag: str = "latest") -> bool:
        """Push image to registry"""        try:
            if not self.registry_url:
                self.logger.warning("⚠️ No registry URL configured")
                return False
            
            full_image_name = f"{image_name}:{tag}"
            registry_image_name = f"{self.registry_url}/{full_image_name}"
            
            # Tag for registry
            image = self.client.images.get(full_image_name)
            image.tag(registry_image_name)
            
            # Push to registry
            self.logger.info(f"📤 Pushing image: {registry_image_name}")
            push_logs = self.client.images.push(registry_image_name, stream=True)
            
            for log in push_logs:
                if 'status' in log:
                    self.logger.debug(log['status'])
            
            self.logger.info(f"✅ Successfully pushed image: {registry_image_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error pushing image {image_name}: {e}")
            return False

class DockerRegistryManager:
    """Professional Docker registry management"""    
    def __init__(self, registry_config: Dict[str, Any]):
        self.registry_config = registry_config
        self.client = None
        self.authenticated = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self) -> bool:
        """Initialize Docker registry manager"""        try:
            self.client = docker.from_env()
            
            # Authenticate with registry
            if 'username' in self.registry_config and 'password' in self.registry_config:
                await self._authenticate()
            
            self.logger.info("✅ DockerRegistryManager initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing DockerRegistryManager: {e}")
            return False
    
    async def _authenticate(self) -> bool:
        """Authenticate with Docker registry"""        try:
            self.client.login(
                username=self.registry_config['username'],
                password=self.registry_config['password'],
                registry=self.registry_config.get('url', 'https://index.docker.io/v1/')
            )
            
            self.authenticated = True
            self.logger.info("✅ Successfully authenticated with Docker registry")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error authenticating with registry: {e}")
            return False
    
    async def list_images(self, repository: str = None) -> List[Dict[str, Any]]:
        """List images in registry"""        try:
            images = []
            
            if repository:
                # List specific repository images
                repo_images = self.client.images.list(name=repository)
                for img in repo_images:
                    images.append({
                        'id': img.id,
                        'tags': img.tags,
                        'size': img.attrs.get('Size', 0),
                        'created': img.attrs.get('Created', '')
                    })
            else:
                # List all images
                all_images = self.client.images.list()
                for img in all_images:
                    images.append({
                        'id': img.id,
                        'tags': img.tags,
                        'size': img.attrs.get('Size', 0),
                        'created': img.attrs.get('Created', '')
                    })
            
            return images
            
        except Exception as e:
            self.logger.error(f"❌ Error listing images: {e}")
            return []
    
    async def pull_image(self, image_name: str, tag: str = "latest") -> bool:
        """Pull image from registry"""        try:
            full_image_name = f"{image_name}:{tag}"
            self.logger.info(f"📥 Pulling image: {full_image_name}")
            
            self.client.images.pull(image_name, tag=tag)
            
            self.logger.info(f"✅ Successfully pulled image: {full_image_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error pulling image {image_name}: {e}")
            return False
    
    async def delete_image(self, image_name: str, tag: str = "latest") -> bool:
        """Delete image from local registry"""        try:
            full_image_name = f"{image_name}:{tag}"
            self.client.images.remove(full_image_name, force=True)
            
            self.logger.info(f"✅ Successfully deleted image: {full_image_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error deleting image {image_name}: {e}")
            return False


# Utility functions for IA-Influencer-Agent Docker management

async def create_ia_influencer_network() -> bool:
    """Create Docker network for IA-Influencer services"""    try:
        client = docker.from_env()
        
        # Check if network already exists
        try:
            network = client.networks.get("ia-influencer-network")
            logger.info("✅ IA-Influencer network already exists")
            return True
        except docker.errors.NotFound:
            pass
        
        # Create network
        network = client.networks.create(
            "ia-influencer-network",
            driver="bridge",
            options={
                "com.docker.network.bridge.name": "ia-influencer0",
                "com.docker.network.bridge.enable_ip_masquerade": "true"
            },
            labels={
                "platform": "IA-Influencer-Agent",
                "creator": "Fahed Mlaiel",
                "purpose": "service-communication"
            }
        )
        
        logger.info("✅ IA-Influencer network created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating IA-Influencer network: {e}")
        return False


async def cleanup_unused_resources() -> Dict[str, int]:
    """Clean up unused Docker resources"""    try:
        client = docker.from_env()
        cleanup_stats = {
            "containers_removed": 0,
            "images_removed": 0,
            "volumes_removed": 0,
            "networks_removed": 0,
            "space_freed_mb": 0
        }
        
        # Remove stopped containers
        stopped_containers = client.containers.list(
            filters={"status": "exited", "label": "platform=IA-Influencer-Agent"}
        )
        for container in stopped_containers:
            container.remove()
            cleanup_stats["containers_removed"] += 1
        
        # Remove unused images
        unused_images = client.images.list(filters={"dangling": True})
        for image in unused_images:
            try:
                size = image.attrs.get('Size', 0)
                client.images.remove(image.id)
                cleanup_stats["images_removed"] += 1
                cleanup_stats["space_freed_mb"] += size / (1024 * 1024)
            except docker.errors.ImageInUse:
                pass
        
        # Remove unused volumes
        unused_volumes = client.volumes.list(filters={"dangling": True})
        for volume in unused_volumes:
            try:
                volume.remove()
                cleanup_stats["volumes_removed"] += 1
            except docker.errors.APIError:
                pass
        
        logger.info(f"✅ Cleanup completed: {cleanup_stats}")
        return cleanup_stats
        
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")
        return {}


async def validate_ia_influencer_requirements() -> Dict[str, bool]:
    """Validate system requirements for IA-Influencer-Agent"""    try:
        client = docker.from_env()
        requirements = {
            "docker_running": False,
            "sufficient_memory": False,
            "sufficient_cpu": False,
            "sufficient_storage": False,
            "gpu_available": False
        }
        
        # Check Docker daemon
        try:
            client.ping()
            requirements["docker_running"] = True
        except:
            pass
        
        # Check system resources
        try:
            system_info = client.info()
            
            # Memory check (8GB minimum)
            total_memory_gb = system_info.get('MemTotal', 0) / (1024**3)
            requirements["sufficient_memory"] = total_memory_gb >= 8
            
            # CPU check (4 cores minimum)
            cpu_count = system_info.get('NCPU', 0)
            requirements["sufficient_cpu"] = cpu_count >= 4
            
            # Storage check (50GB minimum)
            # This is a simplified check - real implementation would check available disk space
            requirements["sufficient_storage"] = True
            
            # GPU check for AI workloads
            try:
                gpu_info = client.containers.run(
                    "nvidia/cuda:11.8-base-ubuntu20.04",
                    "nvidia-smi",
                    remove=True,
                    runtime="nvidia"
                )
                requirements["gpu_available"] = True
            except:
                requirements["gpu_available"] = False
                
        except Exception as e:
            logger.warning(f"⚠️ Error checking system requirements: {e}")
        
        return requirements
        
    except Exception as e:
        logger.error(f"❌ Error validating requirements: {e}")
        return {}


async def get_ia_influencer_status() -> Dict[str, Any]:
    """Get status of all IA-Influencer-Agent containers"""    try:
        client = docker.from_env()
        status = {
            "total_containers": 0,
            "running_containers": 0,
            "stopped_containers": 0,
            "services": {},
            "network_status": "unknown",
            "resource_usage": {}
        }
        
        # Get containers with IA-Influencer label
        containers = client.containers.list(
            all=True,
            filters={"label": "platform=IA-Influencer-Agent"}
        )
        
        status["total_containers"] = len(containers)
        
        for container in containers:
            service_name = container.labels.get("service", container.name)
            container_status = {
                "status": container.status,
                "image": container.image.tags[0] if container.image.tags else "unknown",
                "created": container.attrs["Created"],
                "ports": container.attrs["NetworkSettings"]["Ports"],
                "resource_usage": {}
            }
            
            if container.status == "running":
                status["running_containers"] += 1
                
                # Get resource usage stats
                try:
                    stats = container.stats(stream=False)
                    cpu_percent = calculate_cpu_percentage(stats)
                    memory_usage = stats["memory_usage"]["usage"] / (1024**2)  # MB
                    
                    container_status["resource_usage"] = {
                        "cpu_percent": cpu_percent,
                        "memory_mb": memory_usage
                    }
                except:
                    pass
            else:
                status["stopped_containers"] += 1
            
            status["services"][service_name] = container_status
        
        # Check network status
        try:
            network = client.networks.get("ia-influencer-network")
            status["network_status"] = "healthy"
        except docker.errors.NotFound:
            status["network_status"] = "missing"
        except Exception:
            status["network_status"] = "error"
        
        return status
        
    except Exception as e:
        logger.error(f"❌ Error getting IA-Influencer status: {e}")
        return {}


def calculate_cpu_percentage(stats: Dict[str, Any]) -> float:
    """Calculate CPU usage percentage from Docker stats"""    try:
        cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                   stats["precpu_stats"]["cpu_usage"]["total_usage"]
        system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                      stats["precpu_stats"]["system_cpu_usage"]
        
        if system_delta > 0 and cpu_delta > 0:
            cpu_percent = (cpu_delta / system_delta) * \
                         len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"]) * 100.0
            return round(cpu_percent, 2)
    except (KeyError, ZeroDivisionError):
        pass
    
    return 0.0


# Module exports
__all__ = [
    # Enums
    "DockerImageType",
    "DockerBuildTarget", 
    "DockerRegistry",
    
    # Data classes
    "DockerConfig",
    "DockerBuildResult",
    "DockerRegistryCredentials",
    
    # Main classes
    "DockerConfigManager",
    "DockerImageBuilder",
    "DockerRegistryManager",
    
    # Utility functions
    "create_ia_influencer_network",
    "cleanup_unused_resources",
    "validate_ia_influencer_requirements",
    "get_ia_influencer_status",
    "calculate_cpu_percentage"
]
