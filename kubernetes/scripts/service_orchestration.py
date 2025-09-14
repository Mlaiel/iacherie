"""
Service Orchestration module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""Service Orchestration Manager
Container orchestration and microservices management for the IA Influencer Agent platform
"""

import os
import sys
import time
import json
import logging
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

import yaml
import requests
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """
Service status enumeration"""

    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"
    SCALING = "scaling"
    UPDATING = "updating"


class OrchestrationAction(Enum):
    """Orchestration action enumeration"""

    DEPLOY = "deploy"
    SCALE = "scale"
    UPDATE = "update"
    ROLLBACK = "rollback"
    STOP = "stop"
    RESTART = "restart"


class HealthStatus(Enum):
    """Health status enumeration"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class ServiceDefinition:
    """Service definition data class"""
    name: str
    image: str
    version: str
    replicas: int
    cpu_request: str
    cpu_limit: str
    memory_request: str
    memory_limit: str
    environment_variables: Dict[str, str]
    ports: List[Dict[str, Any]]
    dependencies: List[str]
    health_check: Dict[str, Any]
    volumes: List[Dict[str, Any]]
    config_maps: List[str]
    secrets: List[str]


@dataclass
class ServiceInstance:
    """
Service instance data class"""
    name: str
    definition: ServiceDefinition
    status: ServiceStatus
    health_status: HealthStatus
    current_replicas: int
    desired_replicas: int
    created_at: datetime
    last_updated: datetime
    pod_instances: List[str]
    metrics: Dict[str, float]


@dataclass
class OrchestrationTask:
    """
Orchestration task data class"""
    id: str
    action: OrchestrationAction
    service_name: str
    parameters: Dict[str, Any]
    status: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]


class ServiceOrchestrator:
    """
    Enterprise-grade service orchestration manager
    Manages container orchestration and microservices lifecycle
    """
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        """
Initialize service orchestrator"""
        self.config_path = config_path or "/etc/orchestration/config.yaml"
        self.services = {}
        self.tasks = {}
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        self._load_configuration()
        self._initialize_kubernetes()
        self._load_service_definitions()
    
    def _load_configuration(self) -> None:
        """Load orchestration configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                logger.info(f"Loaded orchestration configuration from {self.config_path}")
            else:
                self.config = self._get_default_config()
                logger.warning("Using default orchestration configuration")
        except Exception as e:
            logger.error(f"Failed to load orchestration configuration: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default orchestration configuration"""
        return {
            "kubernetes": {
                "namespace": "ia-influencer",
                "kubeconfig_path": None,
                "context": None
            },
            "monitoring": {
                "health_check_interval": 30,
                "metrics_collection_interval": 60,
                "auto_scaling_enabled": True,
                "auto_healing_enabled": True
            },
            "deployment": {
                "strategy": "rolling_update",
                "max_surge": "25%",
                "max_unavailable": "25%",
                "progress_deadline_seconds": 600,
                "revision_history_limit": 10
            },
            "auto_scaling": {
                "enabled": True,
                "min_replicas": 1,
                "max_replicas": 10,
                "target_cpu_utilization": 70,
                "target_memory_utilization": 80,
                "scale_up_cooldown": 300,
                "scale_down_cooldown": 300
            },
            "load_balancing": {
                "algorithm": "round_robin",
                "session_affinity": False,
                "health_check_path": "/health",
                "health_check_interval": 10
            },
            "service_mesh": {
                "enabled": True,
                "provider": "istio",
                "mutual_tls": True,
                "traffic_management": True
            },
            "registry": {
                "type": "docker",
                "url": "registry.hub.docker.com",
                "username": None,
                "password": None
            }
        }
    
    def _initialize_kubernetes(self) -> None:
        """Initialize Kubernetes client"""
        try:
            kubeconfig_path = self.config.get("kubernetes", {}).get("kubeconfig_path")
            context = self.config.get("kubernetes", {}).get("context")
            
            if kubeconfig_path:
                config.load_kube_config(config_file=kubeconfig_path, context=context)
            else:
                try:
                    config.load_incluster_config()
                except:
                    config.load_kube_config(context=context)
            
            self.k8s_apps_v1 = client.AppsV1Api()
            self.k8s_core_v1 = client.CoreV1Api()
            self.k8s_networking_v1 = client.NetworkingV1Api()
            self.k8s_autoscaling_v1 = client.AutoscalingV1Api()
            
            # Get namespace
            self.namespace = self.config.get("kubernetes", {}).get("namespace", "default")
            
            # Ensure namespace exists
            self._ensure_namespace_exists()
            
            logger.info("Kubernetes client initialized successfully")
            
        except Exception as e:
            logger.error(f"Kubernetes initialization error: {e}")
            raise
    
    def _ensure_namespace_exists(self) -> None:
        """Ensure namespace exists"""
        try:
            self.k8s_core_v1.read_namespace(name=self.namespace)
        except ApiException as e:
            if e.status == 404:
                # Create namespace
                namespace = client.V1Namespace(
                    metadata=client.V1ObjectMeta(name=self.namespace)
                )
                self.k8s_core_v1.create_namespace(body=namespace)
                logger.info(f"Created namespace: {self.namespace}")
            else:
                raise
    
    def _load_service_definitions(self) -> None:
        """Load service definitions"""
        try:
            services_dir = "/etc/orchestration/services"
            if os.path.exists(services_dir):
                for file_path in Path(services_dir).glob("*.yaml"):
                    with open(file_path, 'r') as f:
                        service_config = yaml.safe_load(f)
                        service_def = self._parse_service_definition(service_config)
                        if service_def:
                            self.services[service_def.name] = ServiceInstance(
                                name=service_def.name,
                                definition=service_def,
                                status=ServiceStatus.STOPPED,
                                health_status=HealthStatus.UNKNOWN,
                                current_replicas=0,
                                desired_replicas=service_def.replicas,
                                created_at=datetime.now(),
                                last_updated=datetime.now(),
                                pod_instances=[],
                                metrics={}
                            )
            
            logger.info(f"Loaded {len(self.services)} service definitions")
            
        except Exception as e:
            logger.error(f"Failed to load service definitions: {e}")
    
    def _parse_service_definition(self, config: Dict[str, Any]) -> Optional[ServiceDefinition]:
        """Parse service definition from configuration"""
        try:
            return ServiceDefinition(
                name=config["name"],
                image=config["image"],
                version=config.get("version", "latest"),
                replicas=config.get("replicas", 1),
                cpu_request=config.get("resources", {}).get("requests", {}).get("cpu", "100m"),
                cpu_limit=config.get("resources", {}).get("limits", {}).get("cpu", "500m"),
                memory_request=config.get("resources", {}).get("requests", {}).get("memory", "128Mi"),
                memory_limit=config.get("resources", {}).get("limits", {}).get("memory", "512Mi"),
                environment_variables=config.get("environment", {}),
                ports=config.get("ports", []),
                dependencies=config.get("dependencies", []),
                health_check=config.get("health_check", {}),
                volumes=config.get("volumes", []),
                config_maps=config.get("config_maps", []),
                secrets=config.get("secrets", [])
            )
        except Exception as e:
            logger.error(f"Service definition parsing error: {e}")
            return None
    
    def start_orchestration(self) -> None:
        """Start service orchestration"""
        try:
            logger.info("Starting service orchestration")
            self.running = True
            
            # Start monitoring threads
            self.executor.submit(self._monitoring_loop)
            self.executor.submit(self._health_check_loop)
            self.executor.submit(self._auto_scaling_loop)
            self.executor.submit(self._task_processor_loop)
            
            logger.info("Service orchestration started")
            
        except Exception as e:
            logger.error(f"Orchestration startup error: {e}")
    
    def stop_orchestration(self) -> None:
        """Stop service orchestration"""
        self.running = False
        self.executor.shutdown(wait=True)
        logger.info("Service orchestration stopped")
    
    def deploy_service(self, service_name: str, **kwargs) -> str:
        """Deploy a service"""
        try:
            if service_name not in self.services:
                raise ValueError(f"Service not found: {service_name}")
            
            task_id = f"deploy_{service_name}_{int(time.time())}"
            task = OrchestrationTask(
                id=task_id,
                action=OrchestrationAction.DEPLOY,
                service_name=service_name,
                parameters=kwargs,
                status="pending",
                created_at=datetime.now(),
                started_at=None,
                completed_at=None,
                error_message=None
            )
            
            self.tasks[task_id] = task
            logger.info(f"Deployment task created: {task_id}")
            
            return task_id
            
        except Exception as e:
            logger.error(f"Service deployment error: {e}")
            raise
    
    def scale_service(self, service_name: str, replicas: int) -> str:
        """Scale a service"""
        try:
            if service_name not in self.services:
                raise ValueError(f"Service not found: {service_name}")
            
            task_id = f"scale_{service_name}_{int(time.time())}"
            task = OrchestrationTask(
                id=task_id,
                action=OrchestrationAction.SCALE,
                service_name=service_name,
                parameters={"replicas": replicas},
                status="pending",
                created_at=datetime.now(),
                started_at=None,
                completed_at=None,
                error_message=None
            )
            
            self.tasks[task_id] = task
            logger.info(f"Scaling task created: {task_id}")
            
            return task_id
            
        except Exception as e:
            logger.error(f"Service scaling error: {e}")
            raise
    
    def update_service(self, service_name: str, **kwargs) -> str:
        """Update a service"""
        try:
            if service_name not in self.services:
                raise ValueError(f"Service not found: {service_name}")
            
            task_id = f"update_{service_name}_{int(time.time())}"
            task = OrchestrationTask(
                id=task_id,
                action=OrchestrationAction.UPDATE,
                service_name=service_name,
                parameters=kwargs,
                status="pending",
                created_at=datetime.now(),
                started_at=None,
                completed_at=None,
                error_message=None
            )
            
            self.tasks[task_id] = task
            logger.info(f"Update task created: {task_id}")
            
            return task_id
            
        except Exception as e:
            logger.error(f"Service update error: {e}")
            raise
    
    def rollback_service(self, service_name: str, revision: Optional[int] = None) -> str:
        """Rollback a service to previous version"""
        try:
            if service_name not in self.services:
                raise ValueError(f"Service not found: {service_name}")
            
            task_id = f"rollback_{service_name}_{int(time.time())}"
            task = OrchestrationTask(
                id=task_id,
                action=OrchestrationAction.ROLLBACK,
                service_name=service_name,
                parameters={"revision": revision},
                status="pending",
                created_at=datetime.now(),
                started_at=None,
                completed_at=None,
                error_message=None
            )
            
            self.tasks[task_id] = task
            logger.info(f"Rollback task created: {task_id}")
            
            return task_id
            
        except Exception as e:
            logger.error(f"Service rollback error: {e}")
            raise
    
    def stop_service(self, service_name: str) -> str:
        """Stop a service"""
        try:
            if service_name not in self.services:
                raise ValueError(f"Service not found: {service_name}")
            
            task_id = f"stop_{service_name}_{int(time.time())}"
            task = OrchestrationTask(
                id=task_id,
                action=OrchestrationAction.STOP,
                service_name=service_name,
                parameters={},
                status="pending",
                created_at=datetime.now(),
                started_at=None,
                completed_at=None,
                error_message=None
            )
            
            self.tasks[task_id] = task
            logger.info(f"Stop task created: {task_id}")
            
            return task_id
            
        except Exception as e:
            logger.error(f"Service stop error: {e}")
            raise
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        try:
            interval = self.config.get("monitoring", {}).get("metrics_collection_interval", 60)
            
            while self.running:
                try:
                    # Update service status and metrics
                    for service_name, service in self.services.items():
                        self._update_service_status(service)
                        self._collect_service_metrics(service)
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"Monitoring loop error: {e}")
                    time.sleep(interval)
                    
        except Exception as e:
            logger.error(f"Monitoring loop fatal error: {e}")
    
    def _health_check_loop(self) -> None:
        """Health check monitoring loop"""
        try:
            interval = self.config.get("monitoring", {}).get("health_check_interval", 30)
            
            while self.running:
                try:
                    # Perform health checks
                    for service_name, service in self.services.items():
                        if service.status == ServiceStatus.RUNNING:
                            health_status = self._check_service_health(service)
                            service.health_status = health_status
                            
                            # Auto-healing if enabled
                            if (health_status == HealthStatus.UNHEALTHY and
                                self.config.get("monitoring", {}).get("auto_healing_enabled", True)):
                                self._trigger_auto_healing(service)
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"Health check loop error: {e}")
                    time.sleep(interval)
                    
        except Exception as e:
            logger.error(f"Health check loop fatal error: {e}")
    
    def _auto_scaling_loop(self) -> None:
        """Auto-scaling monitoring loop"""
        try:
            if not self.config.get("auto_scaling", {}).get("enabled", True):
                return
            
            while self.running:
                try:
                    for service_name, service in self.services.items():
                        if service.status == ServiceStatus.RUNNING:
                            self._check_auto_scaling(service)
                    
                    time.sleep(60)  # Check every minute
                    
                except Exception as e:
                    logger.error(f"Auto-scaling loop error: {e}")
                    time.sleep(60)
                    
        except Exception as e:
            logger.error(f"Auto-scaling loop fatal error: {e}")
    
    def _task_processor_loop(self) -> None:
        """Task processor loop"""
        try:
            while self.running:
                try:
                    # Process pending tasks
                    for task_id, task in self.tasks.items():
                        if task.status == "pending":
                            self.executor.submit(self._execute_task, task)
                    
                    time.sleep(5)  # Check every 5 seconds
                    
                except Exception as e:
                    logger.error(f"Task processor loop error: {e}")
                    time.sleep(5)
                    
        except Exception as e:
            logger.error(f"Task processor loop fatal error: {e}")
    
    def _execute_task(self, task: OrchestrationTask) -> None:
        """Execute orchestration task"""
        try:
            logger.info(f"Executing task: {task.id}")
            task.status = "running"
            task.started_at = datetime.now()
            
            if task.action == OrchestrationAction.DEPLOY:
                self._execute_deploy_task(task)
            elif task.action == OrchestrationAction.SCALE:
                self._execute_scale_task(task)
            elif task.action == OrchestrationAction.UPDATE:
                self._execute_update_task(task)
            elif task.action == OrchestrationAction.ROLLBACK:
                self._execute_rollback_task(task)
            elif task.action == OrchestrationAction.STOP:
                self._execute_stop_task(task)
            elif task.action == OrchestrationAction.RESTART:
                self._execute_restart_task(task)
            
            task.status = "completed"
            task.completed_at = datetime.now()
            logger.info(f"Task completed: {task.id}")
            
        except Exception as e:
            logger.error(f"Task execution error: {e}")
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.now()
    
    def _execute_deploy_task(self, task: OrchestrationTask) -> None:
        """Execute deployment task"""
        try:
            service = self.services[task.service_name]
            service_def = service.definition
            
            # Create deployment
            deployment = self._create_deployment_spec(service_def)
            self.k8s_apps_v1.create_namespaced_deployment(
                namespace=self.namespace,
                body=deployment
            )
            
            # Create service
            k8s_service = self._create_service_spec(service_def)
            self.k8s_core_v1.create_namespaced_service(
                namespace=self.namespace,
                body=k8s_service
            )
            
            # Create ingress if needed
            if service_def.ports and any(p.get("expose", False) for p in service_def.ports):
                ingress = self._create_ingress_spec(service_def)
                self.k8s_networking_v1.create_namespaced_ingress(
                    namespace=self.namespace,
                    body=ingress
                )
            
            # Set up auto-scaling if enabled
            if self.config.get("auto_scaling", {}).get("enabled", True):
                hpa = self._create_hpa_spec(service_def)
                self.k8s_autoscaling_v1.create_namespaced_horizontal_pod_autoscaler(
                    namespace=self.namespace,
                    body=hpa
                )
            
            service.status = ServiceStatus.RUNNING
            service.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"Deployment execution error: {e}")
            raise
    
    def _execute_scale_task(self, task: OrchestrationTask) -> None:
        """Execute scaling task"""
        try:
            service = self.services[task.service_name]
            replicas = task.parameters["replicas"]
            
            # Update deployment replica count
            deployment = self.k8s_apps_v1.read_namespaced_deployment(
                name=service.name,
                namespace=self.namespace
            )
            
            deployment.spec.replicas = replicas
            
            self.k8s_apps_v1.patch_namespaced_deployment(
                name=service.name,
                namespace=self.namespace,
                body=deployment
            )
            
            service.desired_replicas = replicas
            service.status = ServiceStatus.SCALING
            service.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"Scaling execution error: {e}")
            raise
    
    def _execute_update_task(self, task: OrchestrationTask) -> None:
        """Execute update task"""
        try:
            service = self.services[task.service_name]
            
            # Update deployment with new parameters
            deployment = self.k8s_apps_v1.read_namespaced_deployment(
                name=service.name,
                namespace=self.namespace
            )
            
            # Update image if provided
            if "image" in task.parameters:
                for container in deployment.spec.template.spec.containers:
                    if container.name == service.name:
                        container.image = task.parameters["image"]
            
            # Update environment variables if provided
            if "environment" in task.parameters:
                for container in deployment.spec.template.spec.containers:
                    if container.name == service.name:
                        env_vars = []
                        for key, value in task.parameters["environment"].items():
                            env_vars.append(client.V1EnvVar(name=key, value=value))
                        container.env = env_vars
            
            self.k8s_apps_v1.patch_namespaced_deployment(
                name=service.name,
                namespace=self.namespace,
                body=deployment
            )
            
            service.status = ServiceStatus.UPDATING
            service.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"Update execution error: {e}")
            raise
    
    def _execute_rollback_task(self, task: OrchestrationTask) -> None:
        """Execute rollback task"""
        try:
            service = self.services[task.service_name]
            revision = task.parameters.get("revision")
            
            # Rollback deployment
            if revision:
                # Rollback to specific revision
                rollback_body = {
                    "spec": {
                        "rollbackTo": {
                            "revision": revision
                        }
                    }
                }
            else:
                # Rollback to previous revision
                rollback_body = {
                    "spec": {
                        "rollbackTo": {}
                    }
                }
            
            self.k8s_apps_v1.patch_namespaced_deployment(
                name=service.name,
                namespace=self.namespace,
                body=rollback_body
            )
            
            service.status = ServiceStatus.UPDATING
            service.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"Rollback execution error: {e}")
            raise
    
    def _execute_stop_task(self, task: OrchestrationTask) -> None:
        """Execute stop task"""
        try:
            service = self.services[task.service_name]
            
            # Scale deployment to 0 replicas
            deployment = self.k8s_apps_v1.read_namespaced_deployment(
                name=service.name,
                namespace=self.namespace
            )
            
            deployment.spec.replicas = 0
            
            self.k8s_apps_v1.patch_namespaced_deployment(
                name=service.name,
                namespace=self.namespace,
                body=deployment
            )
            
            service.status = ServiceStatus.STOPPED
            service.current_replicas = 0
            service.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"Stop execution error: {e}")
            raise
    
    def _execute_restart_task(self, task: OrchestrationTask) -> None:
        """Execute restart task"""
        try:
            service = self.services[task.service_name]
            
            # Restart by updating deployment annotation
            deployment = self.k8s_apps_v1.read_namespaced_deployment(
                name=service.name,
                namespace=self.namespace
            )
            
            if not deployment.spec.template.metadata.annotations:
                deployment.spec.template.metadata.annotations = {}
            
            deployment.spec.template.metadata.annotations["kubectl.kubernetes.io/restartedAt"] = datetime.now().isoformat()
            
            self.k8s_apps_v1.patch_namespaced_deployment(
                name=service.name,
                namespace=self.namespace,
                body=deployment
            )
            
            service.status = ServiceStatus.UPDATING
            service.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"Restart execution error: {e}")
            raise
    
    def _create_deployment_spec(self, service_def: ServiceDefinition) -> client.V1Deployment:
        """Create Kubernetes deployment specification"""
        try:
            # Container specification
            container = client.V1Container(
                name=service_def.name,
                image=f"{service_def.image}:{service_def.version}",
                ports=[
                    client.V1ContainerPort(container_port=port["port"])
                    for port in service_def.ports
                ],
                env=[
                    client.V1EnvVar(name=key, value=value)
                    for key, value in service_def.environment_variables.items()
                ],
                resources=client.V1ResourceRequirements(
                    requests={
                        "cpu": service_def.cpu_request,
                        "memory": service_def.memory_request
                    },
                    limits={
                        "cpu": service_def.cpu_limit,
                        "memory": service_def.memory_limit
                    }
                )
            )
            
            # Add health checks if defined
            if service_def.health_check:
                if "readiness" in service_def.health_check:
                    readiness = service_def.health_check["readiness"]
                    container.readiness_probe = client.V1Probe(
                        http_get=client.V1HTTPGetAction(
                            path=readiness.get("path", "/health"),
                            port=readiness.get("port", 8080)
                        ),
                        initial_delay_seconds=readiness.get("initial_delay", 10),
                        period_seconds=readiness.get("period", 10)
                    )
                
                if "liveness" in service_def.health_check:
                    liveness = service_def.health_check["liveness"]
                    container.liveness_probe = client.V1Probe(
                        http_get=client.V1HTTPGetAction(
                            path=liveness.get("path", "/health"),
                            port=liveness.get("port", 8080)
                        ),
                        initial_delay_seconds=liveness.get("initial_delay", 30),
                        period_seconds=liveness.get("period", 30)
                    )
            
            # Pod template specification
            pod_template = client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={"app": service_def.name}
                ),
                spec=client.V1PodSpec(
                    containers=[container]
                )
            )
            
            # Deployment specification
            deployment_spec = client.V1DeploymentSpec(
                replicas=service_def.replicas,
                selector=client.V1LabelSelector(
                    match_labels={"app": service_def.name}
                ),
                template=pod_template,
                strategy=client.V1DeploymentStrategy(
                    type="RollingUpdate",
                    rolling_update=client.V1RollingUpdateDeployment(
                        max_surge=self.config.get("deployment", {}).get("max_surge", "25%"),
                        max_unavailable=self.config.get("deployment", {}).get("max_unavailable", "25%")
                    )
                )
            )
            
            # Deployment object
            deployment = client.V1Deployment(
                api_version="apps/v1",
                kind="Deployment",
                metadata=client.V1ObjectMeta(name=service_def.name),
                spec=deployment_spec
            )
            
            return deployment
            
        except Exception as e:
            logger.error(f"Deployment spec creation error: {e}")
            raise
    
    def _create_service_spec(self, service_def: ServiceDefinition) -> client.V1Service:
        """Create Kubernetes service specification"""
        try:
            service_ports = [
                client.V1ServicePort(
                    port=port["port"],
                    target_port=port["port"],
                    protocol=port.get("protocol", "TCP"),
                    name=port.get("name", f"port-{port['port']}")
                )
                for port in service_def.ports
            ]
            
            service_spec = client.V1ServiceSpec(
                selector={"app": service_def.name},
                ports=service_ports,
                type="ClusterIP"
            )
            
            service = client.V1Service(
                api_version="v1",
                kind="Service",
                metadata=client.V1ObjectMeta(name=service_def.name),
                spec=service_spec
            )
            
            return service
            
        except Exception as e:
            logger.error(f"Service spec creation error: {e}")
            raise
    
    def _create_ingress_spec(self, service_def: ServiceDefinition) -> client.V1Ingress:
        """Create Kubernetes ingress specification"""
        try:
            # This would create ingress specification for external access
            # Simplified implementation
            ingress = client.V1Ingress(
                api_version="networking.k8s.io/v1",
                kind="Ingress",
                metadata=client.V1ObjectMeta(name=f"{service_def.name}-ingress"),
                spec=client.V1IngressSpec(
                    rules=[
                        client.V1IngressRule(
                            http=client.V1HTTPIngressRuleValue(
                                paths=[
                                    client.V1HTTPIngressPath(
                                        path="/",
                                        path_type="Prefix",
                                        backend=client.V1IngressBackend(
                                            service=client.V1IngressServiceBackend(
                                                name=service_def.name,
                                                port=client.V1ServiceBackendPort(
                                                    number=service_def.ports[0]["port"]
                                                )
                                            )
                                        )
                                    )
                                ]
                            )
                        )
                    ]
                )
            )
            
            return ingress
            
        except Exception as e:
            logger.error(f"Ingress spec creation error: {e}")
            raise
    
    def _create_hpa_spec(self, service_def: ServiceDefinition) -> client.V1HorizontalPodAutoscaler:
        """Create Horizontal Pod Autoscaler specification"""
        try:
            auto_scaling_config = self.config.get("auto_scaling", {})
            
            hpa = client.V1HorizontalPodAutoscaler(
                api_version="autoscaling/v1",
                kind="HorizontalPodAutoscaler",
                metadata=client.V1ObjectMeta(name=f"{service_def.name}-hpa"),
                spec=client.V1HorizontalPodAutoscalerSpec(
                    scale_target_ref=client.V1CrossVersionObjectReference(
                        api_version="apps/v1",
                        kind="Deployment",
                        name=service_def.name
                    ),
                    min_replicas=auto_scaling_config.get("min_replicas", 1),
                    max_replicas=auto_scaling_config.get("max_replicas", 10),
                    target_cpu_utilization_percentage=auto_scaling_config.get("target_cpu_utilization", 70)
                )
            )
            
            return hpa
            
        except Exception as e:
            logger.error(f"HPA spec creation error: {e}")
            raise
    
    def _update_service_status(self, service: ServiceInstance) -> None:
        """Update service status from Kubernetes"""
        try:
            try:
                deployment = self.k8s_apps_v1.read_namespaced_deployment(
                    name=service.name,
                    namespace=self.namespace
                )
                
                service.current_replicas = deployment.status.ready_replicas or 0
                service.desired_replicas = deployment.spec.replicas or 0
                
                # Determine status
                if deployment.status.ready_replicas == deployment.spec.replicas:
                    if deployment.spec.replicas > 0:
                        service.status = ServiceStatus.RUNNING
                    else:
                        service.status = ServiceStatus.STOPPED
                else:
                    service.status = ServiceStatus.SCALING
                
                # Get pod instances
                pods = self.k8s_core_v1.list_namespaced_pod(
                    namespace=self.namespace,
                    label_selector=f"app={service.name}"
                )
                
                service.pod_instances = [pod.metadata.name for pod in pods.items]
                
            except ApiException as e:
                if e.status == 404:
                    service.status = ServiceStatus.STOPPED
                    service.current_replicas = 0
                    service.pod_instances = []
                else:
                    service.status = ServiceStatus.FAILED
                    
        except Exception as e:
            logger.error(f"Service status update error: {e}")
    
    def _collect_service_metrics(self, service: ServiceInstance) -> None:
        """Collect service metrics"""
        try:
            # This would collect actual metrics from monitoring system
            # Simplified implementation with mock metrics
            service.metrics = {
                "cpu_usage": 45.5,
                "memory_usage": 60.2,
                "request_rate": 120.0,
                "error_rate": 0.5,
                "response_time": 250.0
            }
            
        except Exception as e:
            logger.error(f"Metrics collection error: {e}")
    
    def _check_service_health(self, service: ServiceInstance) -> HealthStatus:
        """Check service health"""
        try:
            # Check if all pods are ready
            if service.current_replicas == service.desired_replicas and service.current_replicas > 0:
                # Additional health checks could be implemented here
                return HealthStatus.HEALTHY
            elif service.current_replicas > 0:
                return HealthStatus.DEGRADED
            else:
                return HealthStatus.UNHEALTHY
                
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return HealthStatus.UNKNOWN
    
    def _trigger_auto_healing(self, service: ServiceInstance) -> None:
        """Trigger auto-healing for unhealthy service"""
        try:
            logger.info(f"Triggering auto-healing for service: {service.name}")
            
            # Restart unhealthy service
            task_id = f"restart_{service.name}_{int(time.time())}"
            task = OrchestrationTask(
                id=task_id,
                action=OrchestrationAction.RESTART,
                service_name=service.name,
                parameters={},
                status="pending",
                created_at=datetime.now(),
                started_at=None,
                completed_at=None,
                error_message=None
            )
            
            self.tasks[task_id] = task
            
        except Exception as e:
            logger.error(f"Auto-healing error: {e}")
    
    def _check_auto_scaling(self, service: ServiceInstance) -> None:
        """Check if service needs auto-scaling"""
        try:
            auto_scaling_config = self.config.get("auto_scaling", {})
            
            cpu_threshold = auto_scaling_config.get("target_cpu_utilization", 70)
            memory_threshold = auto_scaling_config.get("target_memory_utilization", 80)
            
            cpu_usage = service.metrics.get("cpu_usage", 0)
            memory_usage = service.metrics.get("memory_usage", 0)
            
            current_replicas = service.current_replicas
            min_replicas = auto_scaling_config.get("min_replicas", 1)
            max_replicas = auto_scaling_config.get("max_replicas", 10)
            
            # Scale up if resource usage is high
            if (cpu_usage > cpu_threshold or memory_usage > memory_threshold) and current_replicas < max_replicas:
                new_replicas = min(current_replicas + 1, max_replicas)
                self.scale_service(service.name, new_replicas)
                logger.info(f"Auto-scaling up {service.name}: {current_replicas} -> {new_replicas}")
            
            # Scale down if resource usage is low
            elif (cpu_usage < cpu_threshold * 0.5 and memory_usage < memory_threshold * 0.5) and current_replicas > min_replicas:
                new_replicas = max(current_replicas - 1, min_replicas)
                self.scale_service(service.name, new_replicas)
                logger.info(f"Auto-scaling down {service.name}: {current_replicas} -> {new_replicas}")
            
        except Exception as e:
            logger.error(f"Auto-scaling check error: {e}")
    
    def get_service_status(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get service status"""
        try:
            if service_name:
                if service_name not in self.services:
                    return {"error": "Service not found"}
                
                service = self.services[service_name]
                return {
                    "name": service.name,
                    "status": service.status.value,
                    "health_status": service.health_status.value,
                    "current_replicas": service.current_replicas,
                    "desired_replicas": service.desired_replicas,
                    "pod_instances": service.pod_instances,
                    "metrics": service.metrics,
                    "last_updated": service.last_updated.isoformat()
                }
            else:
                # Return status of all services
                return {
                    "services": {
                        name: {
                            "status": service.status.value,
                            "health_status": service.health_status.value,
                            "current_replicas": service.current_replicas,
                            "desired_replicas": service.desired_replicas
                        }
                        for name, service in self.services.items()
                    },
                    "total_services": len(self.services),
                    "running_services": len([s for s in self.services.values() if s.status == ServiceStatus.RUNNING]),
                    "healthy_services": len([s for s in self.services.values() if s.health_status == HealthStatus.HEALTHY])
                }
                
        except Exception as e:
            logger.error(f"Service status error: {e}")
            return {"error": str(e)}
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status"""
        try:
            if task_id not in self.tasks:
                return {"error": "Task not found"}
            
            task = self.tasks[task_id]
            return {
                "id": task.id,
                "action": task.action.value,
                "service_name": task.service_name,
                "status": task.status,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "error_message": task.error_message
            }
            
        except Exception as e:
            logger.error(f"Task status error: {e}")
            return {"error": str(e)}


def main() -> None:
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Service Orchestration Manager")
    parser.add_argument("--action", required=True, 
                       choices=["start", "deploy", "scale", "update", "stop", "status"])
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--service", help="Service name")
    parser.add_argument("--replicas", type=int, help="Number of replicas")
    parser.add_argument("--image", help="Container image")
    
    args = parser.parse_args()
    
    orchestrator = ServiceOrchestrator(config_path=args.config)
    
    if args.action == "start":
        try:
            orchestrator.start_orchestration()
            # Keep running until interrupted
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            orchestrator.stop_orchestration()
    
    elif args.action == "deploy":
        if not args.service:
            print("Service name required for deployment")
            sys.exit(1)
        
        task_id = orchestrator.deploy_service(args.service)
        print(f"Deployment task created: {task_id}")
    
    elif args.action == "scale":
        if not args.service or args.replicas is None:
            print("Service name and replicas required for scaling")
            sys.exit(1)
        
        task_id = orchestrator.scale_service(args.service, args.replicas)
        print(f"Scaling task created: {task_id}")
    
    elif args.action == "update":
        if not args.service:
            print("Service name required for update")
            sys.exit(1)
        
        params = {}
        if args.image:
            params["image"] = args.image
        
        task_id = orchestrator.update_service(args.service, **params)
        print(f"Update task created: {task_id}")
    
    elif args.action == "stop":
        if not args.service:
            print("Service name required for stop")
            sys.exit(1)
        
        task_id = orchestrator.stop_service(args.service)
        print(f"Stop task created: {task_id}")
    
    elif args.action == "status":
        status = orchestrator.get_service_status(args.service)
        print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
