"""
Pod Orchestrator module
Enterprise implementation for Ainflue platform
"""

# Ainflue Infrastructure Module - Kubernetes Pod Orchestrator
# =========================================================
# 
# Enterprise-grade pod orchestration for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Kubernetes Pod Orchestrator - Enterprise Pod Management

Provides comprehensive pod orchestration capabilities including:
- Pod lifecycle management
- Resource allocation and optimization
- Health monitoring and auto-healing
- Multi-container pod coordination
- Security policy enforcement
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import yaml
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PodStatus(Enum):
    """Pod status enumeration"""
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"

class ResourceType(Enum):
    """Resource type enumeration"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    GPU = "nvidia.com/gpu"

@dataclass
class PodSpec:
    """Pod specification dataclass"""
    name: str
    namespace: str = "default"
    image: str = ""
    replicas: int = 1
    resources: Dict[str, str] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    volumes: List[Dict[str, Any]] = field(default_factory=list)
    security_context: Dict[str, Any] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)

@dataclass
class PodMetrics:
    """Pod metrics dataclass"""
    name: str
    namespace: str
    cpu_usage: float
    memory_usage: float
    network_rx: float
    network_tx: float
    timestamp: datetime = field(default_factory=datetime.now)

class PodOrchestrator:
    """
    Enterprise Kubernetes Pod Orchestrator
    
    Manages pod lifecycle, resource allocation, and health monitoring
    across multi-cloud Kubernetes clusters.
    """
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        """Initialize pod orchestrator"""
        self.config_path = config_path
        self.api_client = None
        self.core_v1_api = None
        self.apps_v1_api = None
        self.metrics_api = None
        self.pod_cache: Dict[str, Dict] = {}
        self.health_checks: Dict[str, datetime] = {}
        
        # Enterprise configuration
        self.max_pods_per_node = 110
        self.resource_quotas = {
            "cpu": "100",
            "memory": "200Gi",
            "storage": "1Ti"
        }
        
        # Initialize Kubernetes client
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Kubernetes client"""
        try:
            if self.config_path:
                config.load_kube_config(config_file=self.config_path)
            else:
                # Try in-cluster config first, then local config
                try:
                    config.load_incluster_config()
                except config.ConfigException:
                    config.load_kube_config()
            
            self.api_client = client.ApiClient()
            self.core_v1_api = client.CoreV1Api()
            self.apps_v1_api = client.AppsV1Api()
            
            logger.info("Kubernetes client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {e}")
            raise
    
    async def create_pod(self, pod_spec: PodSpec) -> Dict[str, Any]:
        """Create a new pod"""
        try:
            # Build pod manifest
            pod_manifest = self._build_pod_manifest(pod_spec)
            
            # Create pod
            response = self.core_v1_api.create_namespaced_pod(
                namespace=pod_spec.namespace,
                body=pod_manifest
            )
            
            # Cache pod information
            pod_key = f"{pod_spec.namespace}/{pod_spec.name}"
            self.pod_cache[pod_key] = {
                "spec": pod_spec,
                "status": response.status.phase,
                "created_at": datetime.now(),
                "uid": response.metadata.uid
            }
            
            logger.info(f"Pod created successfully: {pod_spec.name}")
            
            return {
                "name": response.metadata.name,
                "namespace": response.metadata.namespace,
                "uid": response.metadata.uid,
                "status": response.status.phase,
                "node": response.spec.node_name,
                "created_at": response.metadata.creation_timestamp
            }
            
        except ApiException as e:
            logger.error(f"Failed to create pod {pod_spec.name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating pod {pod_spec.name}: {e}")
            raise
    
    def _build_pod_manifest(self, pod_spec: PodSpec) -> client.V1Pod:
        """Build Kubernetes pod manifest"""
        # Container specification
        container = client.V1Container(
            name=pod_spec.name,
            image=pod_spec.image,
            env=[
                client.V1EnvVar(name=k, value=v) 
                for k, v in pod_spec.environment.items()
            ],
            resources=client.V1ResourceRequirements(
                requests=pod_spec.resources,
                limits=pod_spec.resources
            )
        )
        
        # Security context
        security_context = client.V1SecurityContext(
            **pod_spec.security_context
        ) if pod_spec.security_context else None
        
        # Pod security context
        pod_security_context = client.V1PodSecurityContext(
            run_as_non_root=True,
            run_as_user=1000,
            fs_group=2000
        )
        
        # Pod specification
        spec = client.V1PodSpec(
            containers=[container],
            security_context=pod_security_context,
            restart_policy="Always"
        )
        
        # Pod metadata
        metadata = client.V1ObjectMeta(
            name=pod_spec.name,
            namespace=pod_spec.namespace,
            labels=pod_spec.labels,
            annotations=pod_spec.annotations
        )
        
        return client.V1Pod(
            api_version="v1",
            kind="Pod",
            metadata=metadata,
            spec=spec
        )
    
    async def delete_pod(self, name: str, namespace: str = "default") -> bool:
        """Delete a pod"""
        try:
            response = self.core_v1_api.delete_namespaced_pod(
                name=name,
                namespace=namespace,
                body=client.V1DeleteOptions()
            )
            
            # Remove from cache
            pod_key = f"{namespace}/{name}"
            if pod_key in self.pod_cache:
                del self.pod_cache[pod_key]
            
            logger.info(f"Pod deleted successfully: {name}")
            return True
            
        except ApiException as e:
            logger.error(f"Failed to delete pod {name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting pod {name}: {e}")
            return False
    
    async def get_pod_status(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """Get pod status and details"""
        try:
            pod = self.core_v1_api.read_namespaced_pod(
                name=name,
                namespace=namespace
            )
            
            return {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "status": pod.status.phase,
                "conditions": [
                    {
                        "type": condition.type,
                        "status": condition.status,
                        "reason": condition.reason,
                        "message": condition.message
                    }
                    for condition in (pod.status.conditions or [])
                ],
                "container_statuses": [
                    {
                        "name": status.name,
                        "ready": status.ready,
                        "restart_count": status.restart_count,
                        "state": self._get_container_state(status.state)
                    }
                    for status in (pod.status.container_statuses or [])
                ],
                "node": pod.spec.node_name,
                "ip": pod.status.pod_ip,
                "created_at": pod.metadata.creation_timestamp,
                "started_at": pod.status.start_time
            }
            
        except ApiException as e:
            logger.error(f"Failed to get pod status for {name}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error getting pod status for {name}: {e}")
            return {}
    
    def _get_container_state(self, state) -> Dict[str, Any]:
        """Extract container state information"""
        if state.running:
            return {
                "state": "running",
                "started_at": state.running.started_at
            }
        elif state.waiting:
            return {
                "state": "waiting",
                "reason": state.waiting.reason,
                "message": state.waiting.message
            }
        elif state.terminated:
            return {
                "state": "terminated",
                "reason": state.terminated.reason,
                "exit_code": state.terminated.exit_code,
                "finished_at": state.terminated.finished_at
            }
        else:
            return {"state": "unknown"}
    
    async def list_pods(self, namespace: str = "default", label_selector: str = "") -> List[Dict[str, Any]]:
        """List pods in namespace"""
        try:
            pods = self.core_v1_api.list_namespaced_pod(
                namespace=namespace,
                label_selector=label_selector
            )
            
            pod_list = []
            for pod in pods.items:
                pod_info = {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "node": pod.spec.node_name,
                    "ip": pod.status.pod_ip,
                    "created_at": pod.metadata.creation_timestamp,
                    "labels": pod.metadata.labels or {}
                }
                pod_list.append(pod_info)
            
            return pod_list
            
        except ApiException as e:
            logger.error(f"Failed to list pods in namespace {namespace}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing pods: {e}")
            return []
    
    async def scale_pods(self, deployment_name: str, namespace: str, replicas: int) -> bool:
        """Scale deployment pods"""
        try:
            # Update deployment replicas
            deployment = self.apps_v1_api.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            deployment.spec.replicas = replicas
            
            response = self.apps_v1_api.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=deployment
            )
            
            logger.info(f"Scaled deployment {deployment_name} to {replicas} replicas")
            return True
            
        except ApiException as e:
            logger.error(f"Failed to scale deployment {deployment_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error scaling deployment: {e}")
            return False
    
    async def get_pod_metrics(self, name: str, namespace: str = "default") -> Optional[PodMetrics]:
        """Get pod resource metrics"""
        try:
            # This would typically integrate with metrics-server
            # For now, return mock metrics
            return PodMetrics(
                name=name,
                namespace=namespace,
                cpu_usage=0.5,
                memory_usage=256.0,
                network_rx=1024.0,
                network_tx=512.0
            )
            
        except Exception as e:
            logger.error(f"Failed to get metrics for pod {name}: {e}")
            return None
    
    async def health_check_pods(self, namespace: str = "default") -> Dict[str, str]:
        """Perform health checks on pods"""
        try:
            pods = await self.list_pods(namespace)
            health_status = {}
            
            for pod in pods:
                pod_name = pod["name"]
                pod_status = pod["status"]
                
                # Determine health status
                if pod_status == "Running":
                    health_status[pod_name] = "healthy"
                elif pod_status in ["Pending", "ContainerCreating"]:
                    health_status[pod_name] = "starting"
                elif pod_status in ["Failed", "Error"]:
                    health_status[pod_name] = "unhealthy"
                else:
                    health_status[pod_name] = "unknown"
                
                # Update health check timestamp
                self.health_checks[f"{namespace}/{pod_name}"] = datetime.now()
            
            return health_status
            
        except Exception as e:
            logger.error(f"Failed to perform health checks: {e}")
            return {}
    
    async def auto_heal_pods(self, namespace: str = "default") -> Dict[str, str]:
        """Auto-heal unhealthy pods"""
        try:
            health_status = await self.health_check_pods(namespace)
            healing_actions = {}
            
            for pod_name, status in health_status.items():
                if status == "unhealthy":
                    # Attempt to restart the pod
                    success = await self.delete_pod(pod_name, namespace)
                    if success:
                        healing_actions[pod_name] = "restarted"
                        logger.info(f"Auto-healed pod: {pod_name}")
                    else:
                        healing_actions[pod_name] = "restart_failed"
                        logger.error(f"Failed to auto-heal pod: {pod_name}")
            
            return healing_actions
            
        except Exception as e:
            logger.error(f"Failed to auto-heal pods: {e}")
            return {}
    
    async def get_cluster_resources(self) -> Dict[str, Any]:
        """Get cluster resource information"""
        try:
            nodes = self.core_v1_api.list_node()
            
            cluster_info = {
                "total_nodes": len(nodes.items),
                "total_cpu": 0,
                "total_memory": 0,
                "allocatable_cpu": 0,
                "allocatable_memory": 0,
                "nodes": []
            }
            
            for node in nodes.items:
                node_info = {
                    "name": node.metadata.name,
                    "status": "Ready" if any(
                        condition.type == "Ready" and condition.status == "True"
                        for condition in node.status.conditions
                    ) else "NotReady",
                    "cpu_capacity": node.status.capacity.get("cpu", "0"),
                    "memory_capacity": node.status.capacity.get("memory", "0"),
                    "cpu_allocatable": node.status.allocatable.get("cpu", "0"),
                    "memory_allocatable": node.status.allocatable.get("memory", "0")
                }
                cluster_info["nodes"].append(node_info)
            
            return cluster_info
            
        except Exception as e:
            logger.error(f"Failed to get cluster resources: {e}")
            return {}
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get pod orchestrator status"""
        return {
            "status": "active",
            "cached_pods": len(self.pod_cache),
            "health_checks": len(self.health_checks),
            "last_health_check": max(self.health_checks.values()) if self.health_checks else None,
            "resource_quotas": self.resource_quotas,
            "max_pods_per_node": self.max_pods_per_node
        }

# Enterprise Pod Orchestrator instance
pod_orchestrator = PodOrchestrator()

# Export for use in other modules
__all__ = [
    "PodOrchestrator",
    "PodSpec", 
    "PodMetrics",
    "PodStatus",
    "ResourceType",
    "pod_orchestrator"
]