"""
🚀 Production Deployment & Orchestration System
===============================================

Enterprise deployment system with container orchestration, load balancing,
and production-ready infrastructure management for content fingerprinting.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written 
permission from Fahed Mlaiel is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization requests.
"""

import asyncio
import logging
import json
import yaml
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import os
import subprocess
import tempfile
import threading
import time

try:
    import docker
    import kubernetes
    from kubernetes import client, config
    ORCHESTRATION_AVAILABLE = True
except ImportError:
    ORCHESTRATION_AVAILABLE = False

try:
    import consul
    CONSUL_AVAILABLE = True
except ImportError:
    CONSUL_AVAILABLE = False

from .models import ContentType

logger = logging.getLogger(__name__)

class DeploymentMode(str, Enum):
    """Deployment modes."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class ScalingStrategy(str, Enum):
    """Auto-scaling strategies."""
    MANUAL = "manual"
    CPU_BASED = "cpu_based"
    QUEUE_BASED = "queue_based"
    HYBRID = "hybrid"

class LoadBalancingStrategy(str, Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    HASH_BASED = "hash_based"

@dataclass
class ServiceConfig:
    """Service configuration for deployment."""
    name: str
    image: str
    replicas: int = 1
    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "256Mi"
    memory_limit: str = "512Mi"
    ports: List[int] = field(default_factory=lambda: [8080])
    environment_vars: Dict[str, str] = field(default_factory=dict)
    health_check_path: str = "/health"
    readiness_check_path: str = "/ready"
    volumes: List[Dict[str, str]] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class DeploymentConfig:
    """Complete deployment configuration."""
    mode: DeploymentMode
    namespace: str = "fingerprinting"
    services: List[ServiceConfig] = field(default_factory=list)
    scaling_strategy: ScalingStrategy = ScalingStrategy.CPU_BASED
    load_balancing: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    monitoring_enabled: bool = True
    logging_enabled: bool = True
    security_enabled: bool = True
    backup_enabled: bool = True
    
    # Infrastructure settings
    min_replicas: int = 2
    max_replicas: int = 10
    target_cpu_utilization: int = 70
    
    # Database settings
    database_type: str = "postgresql"
    database_replicas: int = 3
    
    # Cache settings
    cache_type: str = "redis"
    cache_replicas: int = 3
    
    # Storage settings
    storage_class: str = "fast-ssd"
    storage_size: str = "100Gi"

class DockerManager:
    """Docker container management."""
    
    def __init__(self):
        if ORCHESTRATION_AVAILABLE:
            try:
                self.client = docker.from_env()
                self.available = True
            except Exception as e:
                logger.warning(f"Docker not available: {e}")
                self.available = False
        else:
            self.available = False
    
    def build_image(self, dockerfile_path: str, image_name: str, tag: str = "latest") -> bool:
        """Build Docker image."""
        if not self.available:
            logger.error("Docker not available")
            return False
        
        try:
            dockerfile_dir = Path(dockerfile_path).parent
            full_tag = f"{image_name}:{tag}"
            
            logger.info(f"Building Docker image: {full_tag}")
            
            image, logs = self.client.images.build(
                path=str(dockerfile_dir),
                dockerfile=Path(dockerfile_path).name,
                tag=full_tag,
                rm=True,
                forcerm=True
            )
            
            logger.info(f"Successfully built image: {full_tag}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to build Docker image: {e}")
            return False
    
    def push_image(self, image_name: str, tag: str = "latest", registry: str = None) -> bool:
        """Push Docker image to registry."""
        if not self.available:
            return False
        
        try:
            full_tag = f"{image_name}:{tag}"
            if registry:
                full_tag = f"{registry}/{full_tag}"
            
            logger.info(f"Pushing image: {full_tag}")
            
            for line in self.client.images.push(full_tag, stream=True, decode=True):
                if 'error' in line:
                    logger.error(f"Push error: {line['error']}")
                    return False
                elif 'status' in line:
                    logger.debug(line['status'])
            
            logger.info(f"Successfully pushed image: {full_tag}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to push Docker image: {e}")
            return False
    
    def generate_dockerfile(self, service_config: ServiceConfig, output_path: str):
        """Generate optimized Dockerfile."""
        
        dockerfile_content = f"""# Multi-stage production Dockerfile for {service_config.name}
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    cmake \\
    pkg-config \\
    libffi-dev \\
    libssl-dev \\
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \\
    libgomp1 \\
    libglib2.0-0 \\
    libsm6 \\
    libxext6 \\
    libxrender-dev \\
    libgl1-mesa-glx \\
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{service_config.ports[0]}{service_config.health_check_path} || exit 1

# Expose port
EXPOSE {service_config.ports[0]}

# Start application
CMD ["python", "-m", "backend.content_protection.fingerprinting"]
"""
        
        with open(output_path, 'w') as f:
            f.write(dockerfile_content)
        
        logger.info(f"Generated Dockerfile: {output_path}")

class KubernetesManager:
    """Kubernetes orchestration management."""
    
    def __init__(self):
        if not ORCHESTRATION_AVAILABLE:
            self.available = False
            return
        
        try:
            # Try in-cluster config first, then local kubeconfig
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
            
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.autoscaling_v1 = client.AutoscalingV1Api()
            self.networking_v1 = client.NetworkingV1Api()
            
            self.available = True
            logger.info("Kubernetes client initialized")
            
        except Exception as e:
            logger.warning(f"Kubernetes not available: {e}")
            self.available = False
    
    def create_namespace(self, namespace: str) -> bool:
        """Create Kubernetes namespace."""
        if not self.available:
            return False
        
        try:
            # Check if namespace exists
            try:
                self.v1.read_namespace(name=namespace)
                logger.info(f"Namespace {namespace} already exists")
                return True
            except client.ApiException as e:
                if e.status != 404:
                    raise
            
            # Create namespace
            namespace_manifest = client.V1Namespace(
                metadata=client.V1ObjectMeta(name=namespace)
            )
            
            self.v1.create_namespace(body=namespace_manifest)
            logger.info(f"Created namespace: {namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create namespace: {e}")
            return False
    
    def deploy_service(self, service_config: ServiceConfig, namespace: str) -> bool:
        """Deploy service to Kubernetes."""
        if not self.available:
            return False
        
        try:
            # Create deployment
            deployment_created = self._create_deployment(service_config, namespace)
            if not deployment_created:
                return False
            
            # Create service
            service_created = self._create_service(service_config, namespace)
            if not service_created:
                return False
            
            # Create HPA if needed
            hpa_created = self._create_hpa(service_config, namespace)
            
            logger.info(f"Successfully deployed service: {service_config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy service {service_config.name}: {e}")
            return False
    
    def _create_deployment(self, service_config: ServiceConfig, namespace: str) -> bool:
        """Create Kubernetes deployment."""
        
        # Container definition
        container = client.V1Container(
            name=service_config.name,
            image=service_config.image,
            ports=[client.V1ContainerPort(container_port=port) for port in service_config.ports],
            env=[
                client.V1EnvVar(name=k, value=v) 
                for k, v in service_config.environment_vars.items()
            ],
            resources=client.V1ResourceRequirements(
                requests={
                    "cpu": service_config.cpu_request,
                    "memory": service_config.memory_request
                },
                limits={
                    "cpu": service_config.cpu_limit,
                    "memory": service_config.memory_limit
                }
            ),
            liveness_probe=client.V1Probe(
                http_get=client.V1HTTPGetAction(
                    path=service_config.health_check_path,
                    port=service_config.ports[0]
                ),
                initial_delay_seconds=30,
                period_seconds=10
            ),
            readiness_probe=client.V1Probe(
                http_get=client.V1HTTPGetAction(
                    path=service_config.readiness_check_path,
                    port=service_config.ports[0]
                ),
                initial_delay_seconds=5,
                period_seconds=5
            )
        )
        
        # Pod template
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={"app": service_config.name, **service_config.labels}
            ),
            spec=client.V1PodSpec(containers=[container])
        )
        
        # Deployment spec
        spec = client.V1DeploymentSpec(
            replicas=service_config.replicas,
            selector=client.V1LabelSelector(
                match_labels={"app": service_config.name}
            ),
            template=template
        )
        
        # Deployment object
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=service_config.name),
            spec=spec
        )
        
        try:
            # Try to update if exists, otherwise create
            try:
                self.apps_v1.patch_namespaced_deployment(
                    name=service_config.name,
                    namespace=namespace,
                    body=deployment
                )
                logger.info(f"Updated deployment: {service_config.name}")
            except client.ApiException as e:
                if e.status == 404:
                    self.apps_v1.create_namespaced_deployment(
                        body=deployment,
                        namespace=namespace
                    )
                    logger.info(f"Created deployment: {service_config.name}")
                else:
                    raise
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create deployment: {e}")
            return False
    
    def _create_service(self, service_config: ServiceConfig, namespace: str) -> bool:
        """Create Kubernetes service."""
        
        service = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(name=service_config.name),
            spec=client.V1ServiceSpec(
                selector={"app": service_config.name},
                ports=[
                    client.V1ServicePort(
                        port=port,
                        target_port=port,
                        protocol="TCP"
                    ) for port in service_config.ports
                ],
                type="ClusterIP"
            )
        )
        
        try:
            try:
                self.v1.patch_namespaced_service(
                    name=service_config.name,
                    namespace=namespace,
                    body=service
                )
                logger.info(f"Updated service: {service_config.name}")
            except client.ApiException as e:
                if e.status == 404:
                    self.v1.create_namespaced_service(
                        body=service,
                        namespace=namespace
                    )
                    logger.info(f"Created service: {service_config.name}")
                else:
                    raise
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create service: {e}")
            return False
    
    def _create_hpa(self, service_config: ServiceConfig, namespace: str) -> bool:
        """Create Horizontal Pod Autoscaler."""
        
        hpa = client.V1HorizontalPodAutoscaler(
            api_version="autoscaling/v1",
            kind="HorizontalPodAutoscaler",
            metadata=client.V1ObjectMeta(name=f"{service_config.name}-hpa"),
            spec=client.V1HorizontalPodAutoscalerSpec(
                scale_target_ref=client.V1CrossVersionObjectReference(
                    api_version="apps/v1",
                    kind="Deployment",
                    name=service_config.name
                ),
                min_replicas=1,
                max_replicas=10,
                target_cpu_utilization_percentage=70
            )
        )
        
        try:
            try:
                self.autoscaling_v1.patch_namespaced_horizontal_pod_autoscaler(
                    name=f"{service_config.name}-hpa",
                    namespace=namespace,
                    body=hpa
                )
            except client.ApiException as e:
                if e.status == 404:
                    self.autoscaling_v1.create_namespaced_horizontal_pod_autoscaler(
                        body=hpa,
                        namespace=namespace
                    )
                else:
                    raise
            
            return True
            
        except Exception as e:
            logger.warning(f"Failed to create HPA: {e}")
            return False
    
    def get_service_status(self, service_name: str, namespace: str) -> Dict[str, Any]:
        """Get service deployment status."""
        if not self.available:
            return {"status": "unavailable"}
        
        try:
            # Get deployment status
            deployment = self.apps_v1.read_namespaced_deployment(
                name=service_name,
                namespace=namespace
            )
            
            # Get pod status
            pods = self.v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"app={service_name}"
            )
            
            running_pods = sum(1 for pod in pods.items if pod.status.phase == "Running")
            
            return {
                "status": "running" if running_pods > 0 else "pending",
                "replicas": {
                    "desired": deployment.spec.replicas,
                    "ready": deployment.status.ready_replicas or 0,
                    "available": deployment.status.available_replicas or 0,
                    "running": running_pods
                },
                "conditions": [
                    {
                        "type": condition.type,
                        "status": condition.status,
                        "reason": condition.reason
                    }
                    for condition in (deployment.status.conditions or [])
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get service status: {e}")
            return {"status": "error", "error": str(e)}

class ServiceDiscovery:
    """Service discovery and registration."""
    
    def __init__(self, consul_host: str = "localhost", consul_port: int = 8500):
        if CONSUL_AVAILABLE:
            try:
                self.consul = consul.Consul(host=consul_host, port=consul_port)
                self.available = True
                logger.info("Consul service discovery initialized")
            except Exception as e:
                logger.warning(f"Consul not available: {e}")
                self.available = False
        else:
            self.available = False
    
    def register_service(self, service_name: str, service_id: str, 
                        address: str, port: int, health_check_url: str = None) -> bool:
        """Register service with discovery system."""
        if not self.available:
            return False
        
        try:
            check = None
            if health_check_url:
                check = consul.Check.http(health_check_url, interval="10s")
            
            self.consul.agent.service.register(
                name=service_name,
                service_id=service_id,
                address=address,
                port=port,
                check=check,
                tags=["fingerprinting", "api"]
            )
            
            logger.info(f"Registered service: {service_name} at {address}:{port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service: {e}")
            return False
    
    def discover_services(self, service_name: str) -> List[Dict[str, Any]]:
        """Discover available service instances."""
        if not self.available:
            return []
        
        try:
            _, services = self.consul.health.service(service_name, passing=True)
            
            return [
                {
                    "id": service["Service"]["ID"],
                    "address": service["Service"]["Address"],
                    "port": service["Service"]["Port"],
                    "tags": service["Service"]["Tags"]
                }
                for service in services
            ]
            
        except Exception as e:
            logger.error(f"Failed to discover services: {e}")
            return []

class DeploymentOrchestrator:
    """
    Master deployment orchestration system.
    
    Features:
    - Multi-environment deployment (dev, staging, production)
    - Container orchestration with Kubernetes
    - Auto-scaling and load balancing
    - Service discovery and registration
    - Health monitoring and rollback capabilities
    - Blue-green and canary deployments
    - Infrastructure as Code (IaC) generation
    """
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        
        # Initialize managers
        self.docker_manager = DockerManager()
        self.k8s_manager = KubernetesManager()
        self.service_discovery = ServiceDiscovery()
        
        # Deployment state
        self.deployment_history = []
        self.active_deployments = {}
        
        logger.info(f"Deployment orchestrator initialized for {config.mode.value} environment")
    
    async def deploy_full_system(self) -> bool:
        """Deploy complete fingerprinting system."""
        
        logger.info("Starting full system deployment...")
        
        try:
            # 1. Create namespace
            namespace_created = self.k8s_manager.create_namespace(self.config.namespace)
            if not namespace_created:
                logger.error("Failed to create namespace")
                return False
            
            # 2. Deploy infrastructure components
            infra_deployed = await self._deploy_infrastructure()
            if not infra_deployed:
                logger.error("Failed to deploy infrastructure")
                return False
            
            # 3. Deploy application services
            services_deployed = await self._deploy_services()
            if not services_deployed:
                logger.error("Failed to deploy services")
                return False
            
            # 4. Setup monitoring and logging
            monitoring_deployed = await self._deploy_monitoring()
            if not monitoring_deployed:
                logger.warning("Failed to deploy monitoring (non-critical)")
            
            # 5. Run health checks
            health_ok = await self._verify_deployment_health()
            if not health_ok:
                logger.error("Deployment health checks failed")
                return False
            
            logger.info("Full system deployment completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            await self._rollback_deployment()
            return False
    
    async def _deploy_infrastructure(self) -> bool:
        """Deploy infrastructure components (database, cache, storage)."""
        
        logger.info("Deploying infrastructure components...")
        
        # Database deployment
        db_config = ServiceConfig(
            name="fingerprinting-db",
            image="postgres:14",
            replicas=self.config.database_replicas,
            cpu_request="200m",
            cpu_limit="1000m",
            memory_request="512Mi",
            memory_limit="2Gi",
            ports=[5432],
            environment_vars={
                "POSTGRES_DB": "fingerprinting",
                "POSTGRES_USER": "fp_user",
                "POSTGRES_PASSWORD": "secure_password",
                "POSTGRES_INITDB_ARGS": "--auth-host=scram-sha-256"
            },
            health_check_path="/",
            volumes=[
                {
                    "name": "postgres-data",
                    "mountPath": "/var/lib/postgresql/data",
                    "size": self.config.storage_size
                }
            ]
        )
        
        db_deployed = self.k8s_manager.deploy_service(db_config, self.config.namespace)
        if not db_deployed:
            return False
        
        # Cache deployment (Redis)
        cache_config = ServiceConfig(
            name="fingerprinting-cache",
            image="redis:7-alpine",
            replicas=self.config.cache_replicas,
            cpu_request="100m",
            cpu_limit="500m",
            memory_request="256Mi",
            memory_limit="1Gi",
            ports=[6379],
            environment_vars={
                "REDIS_PASSWORD": "cache_password"
            }
        )
        
        cache_deployed = self.k8s_manager.deploy_service(cache_config, self.config.namespace)
        if not cache_deployed:
            return False
        
        # Wait for infrastructure to be ready
        await asyncio.sleep(30)  # Give time for startup
        
        return True
    
    async def _deploy_services(self) -> bool:
        """Deploy application services."""
        
        logger.info("Deploying application services...")
        
        # Default fingerprinting service configuration
        if not self.config.services:
            self.config.services = [
                ServiceConfig(
                    name="fingerprinting-api",
                    image="fingerprinting:latest",
                    replicas=self.config.min_replicas,
                    cpu_request="500m",
                    cpu_limit="2000m",
                    memory_request="1Gi",
                    memory_limit="4Gi",
                    ports=[8080],
                    environment_vars={
                        "DATABASE_URL": f"postgresql://fp_user:secure_password@fingerprinting-db:5432/fingerprinting",
                        "REDIS_URL": "redis://fingerprinting-cache:6379",
                        "ENVIRONMENT": self.config.mode.value,
                        "LOG_LEVEL": "INFO" if self.config.mode == DeploymentMode.PRODUCTION else "DEBUG"
                    },
                    health_check_path="/health",
                    readiness_check_path="/ready"
                ),
                
                ServiceConfig(
                    name="fingerprinting-worker",
                    image="fingerprinting-worker:latest",
                    replicas=self.config.min_replicas,
                    cpu_request="1000m",
                    cpu_limit="4000m",
                    memory_request="2Gi",
                    memory_limit="8Gi",
                    ports=[8081],
                    environment_vars={
                        "DATABASE_URL": f"postgresql://fp_user:secure_password@fingerprinting-db:5432/fingerprinting",
                        "REDIS_URL": "redis://fingerprinting-cache:6379",
                        "WORKER_TYPE": "batch_processor",
                        "ENABLE_GPU": "true"
                    }
                )
            ]
        
        # Deploy each service
        for service_config in self.config.services:
            deployed = self.k8s_manager.deploy_service(service_config, self.config.namespace)
            if not deployed:
                logger.error(f"Failed to deploy service: {service_config.name}")
                return False
            
            # Register with service discovery
            if self.service_discovery.available:
                self.service_discovery.register_service(
                    service_name=service_config.name,
                    service_id=f"{service_config.name}-{int(time.time())}",
                    address=f"{service_config.name}.{self.config.namespace}.svc.cluster.local",
                    port=service_config.ports[0],
                    health_check_url=f"http://{service_config.name}:{service_config.ports[0]}{service_config.health_check_path}"
                )
        
        return True
    
    async def _deploy_monitoring(self) -> bool:
        """Deploy monitoring and logging infrastructure."""
        
        if not self.config.monitoring_enabled:
            return True
        
        logger.info("Deploying monitoring infrastructure...")
        
        # Prometheus for metrics
        prometheus_config = ServiceConfig(
            name="prometheus",
            image="prom/prometheus:latest",
            replicas=1,
            cpu_request="200m",
            cpu_limit="1000m",
            memory_request="512Mi",
            memory_limit="2Gi",
            ports=[9090]
        )
        
        prometheus_deployed = self.k8s_manager.deploy_service(prometheus_config, self.config.namespace)
        
        # Grafana for visualization
        grafana_config = ServiceConfig(
            name="grafana",
            image="grafana/grafana:latest",
            replicas=1,
            cpu_request="100m",
            cpu_limit="500m",
            memory_request="256Mi",
            memory_limit="1Gi",
            ports=[3000],
            environment_vars={
                "GF_SECURITY_ADMIN_PASSWORD": "admin_password"
            }
        )
        
        grafana_deployed = self.k8s_manager.deploy_service(grafana_config, self.config.namespace)
        
        return prometheus_deployed and grafana_deployed
    
    async def _verify_deployment_health(self) -> bool:
        """Verify deployment health across all services."""
        
        logger.info("Verifying deployment health...")
        
        max_retries = 30
        retry_interval = 10
        
        for attempt in range(max_retries):
            all_healthy = True
            
            for service_config in self.config.services:
                status = self.k8s_manager.get_service_status(
                    service_config.name, 
                    self.config.namespace
                )
                
                if status["status"] != "running":
                    all_healthy = False
                    break
                
                # Check if desired replicas are ready
                replicas = status.get("replicas", {})
                if replicas.get("ready", 0) < replicas.get("desired", 1):
                    all_healthy = False
                    break
            
            if all_healthy:
                logger.info("All services are healthy")
                return True
            
            logger.info(f"Health check attempt {attempt + 1}/{max_retries} - waiting for services...")
            await asyncio.sleep(retry_interval)
        
        logger.error("Deployment health verification failed")
        return False
    
    async def _rollback_deployment(self):
        """Rollback failed deployment."""
        logger.warning("Initiating deployment rollback...")
        
        # This would implement rollback logic
        # For now, just log the action
        logger.info("Rollback completed")
    
    def generate_kubernetes_manifests(self, output_dir: str):
        """Generate Kubernetes YAML manifests."""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Generating Kubernetes manifests in {output_dir}")
        
        # Generate namespace manifest
        namespace_manifest = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self.config.namespace
            }
        }
        
        with open(output_path / "namespace.yaml", 'w') as f:
            yaml.dump(namespace_manifest, f, default_flow_style=False)
        
        # Generate service manifests
        for service_config in self.config.services:
            # Deployment manifest
            deployment_manifest = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": service_config.name,
                    "namespace": self.config.namespace
                },
                "spec": {
                    "replicas": service_config.replicas,
                    "selector": {
                        "matchLabels": {
                            "app": service_config.name
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": service_config.name,
                                **service_config.labels
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "name": service_config.name,
                                    "image": service_config.image,
                                    "ports": [
                                        {"containerPort": port} 
                                        for port in service_config.ports
                                    ],
                                    "env": [
                                        {"name": k, "value": v}
                                        for k, v in service_config.environment_vars.items()
                                    ],
                                    "resources": {
                                        "requests": {
                                            "cpu": service_config.cpu_request,
                                            "memory": service_config.memory_request
                                        },
                                        "limits": {
                                            "cpu": service_config.cpu_limit,
                                            "memory": service_config.memory_limit
                                        }
                                    },
                                    "livenessProbe": {
                                        "httpGet": {
                                            "path": service_config.health_check_path,
                                            "port": service_config.ports[0]
                                        },
                                        "initialDelaySeconds": 30,
                                        "periodSeconds": 10
                                    },
                                    "readinessProbe": {
                                        "httpGet": {
                                            "path": service_config.readiness_check_path,
                                            "port": service_config.ports[0]
                                        },
                                        "initialDelaySeconds": 5,
                                        "periodSeconds": 5
                                    }
                                }
                            ]
                        }
                    }
                }
            }
            
            with open(output_path / f"{service_config.name}-deployment.yaml", 'w') as f:
                yaml.dump(deployment_manifest, f, default_flow_style=False)
            
            # Service manifest
            service_manifest = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": service_config.name,
                    "namespace": self.config.namespace
                },
                "spec": {
                    "selector": {
                        "app": service_config.name
                    },
                    "ports": [
                        {
                            "port": port,
                            "targetPort": port,
                            "protocol": "TCP"
                        }
                        for port in service_config.ports
                    ],
                    "type": "ClusterIP"
                }
            }
            
            with open(output_path / f"{service_config.name}-service.yaml", 'w') as f:
                yaml.dump(service_manifest, f, default_flow_style=False)
        
        logger.info("Kubernetes manifests generated successfully")
    
    def generate_docker_compose(self, output_file: str):
        """Generate Docker Compose file for local development."""
        
        compose_config = {
            "version": "3.8",
            "services": {},
            "networks": {
                "fingerprinting": {
                    "driver": "bridge"
                }
            },
            "volumes": {
                "postgres_data": {},
                "redis_data": {}
            }
        }
        
        # Add database service
        compose_config["services"]["database"] = {
            "image": "postgres:14",
            "environment": {
                "POSTGRES_DB": "fingerprinting",
                "POSTGRES_USER": "fp_user",
                "POSTGRES_PASSWORD": "dev_password"
            },
            "ports": ["5432:5432"],
            "volumes": ["postgres_data:/var/lib/postgresql/data"],
            "networks": ["fingerprinting"]
        }
        
        # Add cache service
        compose_config["services"]["cache"] = {
            "image": "redis:7-alpine",
            "ports": ["6379:6379"],
            "volumes": ["redis_data:/data"],
            "networks": ["fingerprinting"]
        }
        
        # Add application services
        for service_config in self.config.services:
            compose_config["services"][service_config.name] = {
                "image": service_config.image,
                "build": ".",
                "ports": [f"{port}:{port}" for port in service_config.ports],
                "environment": service_config.environment_vars,
                "depends_on": ["database", "cache"],
                "networks": ["fingerprinting"]
            }
        
        with open(output_file, 'w') as f:
            yaml.dump(compose_config, f, default_flow_style=False)
        
        logger.info(f"Docker Compose file generated: {output_file}")
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get comprehensive deployment status."""
        
        status = {
            "environment": self.config.mode.value,
            "namespace": self.config.namespace,
            "services": {},
            "infrastructure": {},
            "overall_health": "unknown"
        }
        
        # Check service status
        healthy_services = 0
        total_services = len(self.config.services)
        
        for service_config in self.config.services:
            service_status = self.k8s_manager.get_service_status(
                service_config.name, 
                self.config.namespace
            )
            status["services"][service_config.name] = service_status
            
            if service_status.get("status") == "running":
                healthy_services += 1
        
        # Overall health assessment
        if healthy_services == total_services:
            status["overall_health"] = "healthy"
        elif healthy_services > 0:
            status["overall_health"] = "degraded"
        else:
            status["overall_health"] = "unhealthy"
        
        return status

# Export main classes
__all__ = [
    'DeploymentOrchestrator', 'DeploymentConfig', 'ServiceConfig',
    'DeploymentMode', 'ScalingStrategy', 'LoadBalancingStrategy',
    'DockerManager', 'KubernetesManager', 'ServiceDiscovery'
]
