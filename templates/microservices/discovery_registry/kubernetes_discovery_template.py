"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Kubernetes Discovery Template for Ainflue Platform
=================================================

Production-ready Kubernetes native service discovery with:
- Service and endpoint discovery
- Pod health monitoring
- Namespace-aware discovery
- ConfigMap and Secret management
- Kubernetes events watching
- Multi-cluster support

Author: Fahed Mlaiel (mlaiel@live.de)
Kubernetes & Cloud Native Expert
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional, List, Set, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
from prometheus_client import Counter, Histogram, Gauge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
k8s_operations_counter = Counter('k8s_operations_total', 'Total Kubernetes operations', ['operation', 'status'])
k8s_latency_histogram = Histogram('k8s_operation_duration_seconds', 'Kubernetes operation latency', ['operation'])
k8s_services_gauge = Gauge('k8s_discovered_services', 'Number of services discovered in Kubernetes', ['namespace'])

@dataclass
class K8sServiceEndpoint:
    """Kubernetes service endpoint"""
    name: str
    namespace: str
    cluster_ip: str
    external_ip: Optional[str]
    ports: List[Dict[str, Any]]
    endpoints: List[Dict[str, Any]]
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    type: str = "ClusterIP"

@dataclass
class K8sPodInfo:
    """Kubernetes pod information"""
    name: str
    namespace: str
    ip: str
    host_ip: str
    phase: str
    ready: bool
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    containers: List[Dict[str, Any]] = field(default_factory=list)

class KubernetesDiscoveryClient:
    """
    Kubernetes native service discovery client
    
    Features:
    - Service and endpoint discovery
    - Pod health monitoring
    - Real-time watch mechanisms
    - Multi-namespace support
    - ConfigMap/Secret management
    """
    
    def __init__(self, namespace: str = "default", in_cluster: bool = None):
        self.namespace = namespace
        self.in_cluster = in_cluster or self._detect_in_cluster()
        
        # Initialize Kubernetes client
        try:
            if self.in_cluster:
                config.load_incluster_config()
                logger.info("Loaded in-cluster Kubernetes configuration")
            else:
                config.load_kube_config()
                logger.info("Loaded local Kubernetes configuration")
        except Exception as e:
            logger.error(f"Failed to load Kubernetes configuration: {e}")
            raise
        
        # Create API clients
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.extensions_v1beta1 = client.ExtensionsV1beta1Api()
        
        # Watch objects
        self.watchers: Dict[str, watch.Watch] = {}
        self.watch_tasks: Dict[str, asyncio.Task] = {}
        
        # Discovery cache
        self.services_cache: Dict[str, List[K8sServiceEndpoint]] = {}
        self.pods_cache: Dict[str, List[K8sPodInfo]] = {}
        self.cache_last_updated: Dict[str, datetime] = {}
    
    def _detect_in_cluster(self) -> bool:
        """Detect if running inside Kubernetes cluster"""
        return os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token")
    
    async def discover_services(self, namespace: str = None, label_selector: str = None) -> List[K8sServiceEndpoint]:
        """Discover services in Kubernetes"""
        try:
            with k8s_latency_histogram.labels(operation="discover_services").time():
                target_namespace = namespace or self.namespace
                
                # Get services
                if target_namespace == "all":
                    services = self.v1.list_service_for_all_namespaces(
                        label_selector=label_selector
                    )
                else:
                    services = self.v1.list_namespaced_service(
                        namespace=target_namespace,
                        label_selector=label_selector
                    )
                
                service_endpoints = []
                
                for service in services.items:
                    # Get endpoints for this service
                    try:
                        endpoints = self.v1.read_namespaced_endpoints(
                            name=service.metadata.name,
                            namespace=service.metadata.namespace
                        )
                        
                        endpoint_list = []
                        if endpoints.subsets:
                            for subset in endpoints.subsets:
                                ports = subset.ports or []
                                addresses = subset.addresses or []
                                
                                for address in addresses:
                                    for port in ports:
                                        endpoint_list.append({
                                            "ip": address.ip,
                                            "port": port.port,
                                            "protocol": port.protocol,
                                            "name": port.name,
                                            "target_ref": address.target_ref.to_dict() if address.target_ref else None
                                        })
                        
                    except ApiException as e:
                        if e.status != 404:  # Ignore not found errors
                            logger.warning(f"Failed to get endpoints for service {service.metadata.name}: {e}")
                        endpoint_list = []
                    
                    # Create service endpoint object
                    service_endpoint = K8sServiceEndpoint(
                        name=service.metadata.name,
                        namespace=service.metadata.namespace,
                        cluster_ip=service.spec.cluster_ip,
                        external_ip=None,
                        ports=[{
                            "name": port.name,
                            "port": port.port,
                            "target_port": port.target_port,
                            "protocol": port.protocol
                        } for port in (service.spec.ports or [])],
                        endpoints=endpoint_list,
                        labels=service.metadata.labels or {},
                        annotations=service.metadata.annotations or {},
                        type=service.spec.type
                    )
                    
                    # Add external IP if available
                    if service.spec.type == "LoadBalancer" and service.status.load_balancer.ingress:
                        ingress = service.status.load_balancer.ingress[0]
                        service_endpoint.external_ip = ingress.ip or ingress.hostname
                    
                    service_endpoints.append(service_endpoint)
                
                # Update cache
                cache_key = f"{target_namespace}:{label_selector or 'all'}"
                self.services_cache[cache_key] = service_endpoints
                self.cache_last_updated[cache_key] = datetime.utcnow()
                
                # Update metrics
                k8s_services_gauge.labels(namespace=target_namespace).set(len(service_endpoints))
                k8s_operations_counter.labels(operation="discover_services", status="success").inc()
                
                logger.info(f"Discovered {len(service_endpoints)} services in namespace {target_namespace}")
                return service_endpoints
                
        except Exception as e:
            k8s_operations_counter.labels(operation="discover_services", status="error").inc()
            logger.error(f"Failed to discover services: {e}")
            return []
    
    async def discover_pods(self, namespace: str = None, label_selector: str = None) -> List[K8sPodInfo]:
        """Discover pods in Kubernetes"""
        try:
            with k8s_latency_histogram.labels(operation="discover_pods").time():
                target_namespace = namespace or self.namespace
                
                # Get pods
                if target_namespace == "all":
                    pods = self.v1.list_pod_for_all_namespaces(
                        label_selector=label_selector
                    )
                else:
                    pods = self.v1.list_namespaced_pod(
                        namespace=target_namespace,
                        label_selector=label_selector
                    )
                
                pod_list = []
                
                for pod in pods.items:
                    # Determine if pod is ready
                    ready = False
                    if pod.status.conditions:
                        for condition in pod.status.conditions:
                            if condition.type == "Ready" and condition.status == "True":
                                ready = True
                                break
                    
                    # Get container information
                    containers = []
                    if pod.spec.containers:
                        for container in pod.spec.containers:
                            container_info = {
                                "name": container.name,
                                "image": container.image,
                                "ports": [
                                    {
                                        "name": port.name,
                                        "container_port": port.container_port,
                                        "protocol": port.protocol
                                    }
                                    for port in (container.ports or [])
                                ]
                            }
                            containers.append(container_info)
                    
                    pod_info = K8sPodInfo(
                        name=pod.metadata.name,
                        namespace=pod.metadata.namespace,
                        ip=pod.status.pod_ip or "",
                        host_ip=pod.status.host_ip or "",
                        phase=pod.status.phase,
                        ready=ready,
                        labels=pod.metadata.labels or {},
                        annotations=pod.metadata.annotations or {},
                        containers=containers
                    )
                    
                    pod_list.append(pod_info)
                
                # Update cache
                cache_key = f"pods:{target_namespace}:{label_selector or 'all'}"
                self.pods_cache[cache_key] = pod_list
                self.cache_last_updated[cache_key] = datetime.utcnow()
                
                k8s_operations_counter.labels(operation="discover_pods", status="success").inc()
                logger.info(f"Discovered {len(pod_list)} pods in namespace {target_namespace}")
                return pod_list
                
        except Exception as e:
            k8s_operations_counter.labels(operation="discover_pods", status="error").inc()
            logger.error(f"Failed to discover pods: {e}")
            return []
    
    async def get_service_by_name(self, service_name: str, namespace: str = None) -> Optional[K8sServiceEndpoint]:
        """Get specific service by name"""
        try:
            with k8s_latency_histogram.labels(operation="get_service").time():
                target_namespace = namespace or self.namespace
                
                service = self.v1.read_namespaced_service(
                    name=service_name,
                    namespace=target_namespace
                )
                
                # Get endpoints
                try:
                    endpoints = self.v1.read_namespaced_endpoints(
                        name=service_name,
                        namespace=target_namespace
                    )
                    
                    endpoint_list = []
                    if endpoints.subsets:
                        for subset in endpoints.subsets:
                            ports = subset.ports or []
                            addresses = subset.addresses or []
                            
                            for address in addresses:
                                for port in ports:
                                    endpoint_list.append({
                                        "ip": address.ip,
                                        "port": port.port,
                                        "protocol": port.protocol,
                                        "name": port.name
                                    })
                
                except ApiException:
                    endpoint_list = []
                
                service_endpoint = K8sServiceEndpoint(
                    name=service.metadata.name,
                    namespace=service.metadata.namespace,
                    cluster_ip=service.spec.cluster_ip,
                    external_ip=None,
                    ports=[{
                        "name": port.name,
                        "port": port.port,
                        "target_port": port.target_port,
                        "protocol": port.protocol
                    } for port in (service.spec.ports or [])],
                    endpoints=endpoint_list,
                    labels=service.metadata.labels or {},
                    annotations=service.metadata.annotations or {},
                    type=service.spec.type
                )
                
                k8s_operations_counter.labels(operation="get_service", status="success").inc()
                return service_endpoint
                
        except ApiException as e:
            if e.status == 404:
                k8s_operations_counter.labels(operation="get_service", status="not_found").inc()
                return None
            else:
                k8s_operations_counter.labels(operation="get_service", status="error").inc()
                logger.error(f"Failed to get service {service_name}: {e}")
                return None
    
    async def watch_services(self, callback, namespace: str = None, label_selector: str = None):
        """Watch for service changes"""
        try:
            target_namespace = namespace or self.namespace
            watch_key = f"services:{target_namespace}:{label_selector or 'all'}"
            
            if watch_key in self.watch_tasks:
                logger.info(f"Already watching services for {watch_key}")
                return
            
            async def watch_loop():
                w = watch.Watch()
                self.watchers[watch_key] = w
                
                try:
                    if target_namespace == "all":
                        stream = w.stream(
                            self.v1.list_service_for_all_namespaces,
                            label_selector=label_selector
                        )
                    else:
                        stream = w.stream(
                            self.v1.list_namespaced_service,
                            namespace=target_namespace,
                            label_selector=label_selector
                        )
                    
                    for event in stream:
                        event_type = event['type']
                        service = event['object']
                        
                        try:
                            await callback(event_type, service)
                        except Exception as e:
                            logger.error(f"Service watch callback error: {e}")
                            
                except Exception as e:
                    logger.error(f"Service watch error: {e}")
                finally:
                    if watch_key in self.watchers:
                        del self.watchers[watch_key]
            
            self.watch_tasks[watch_key] = asyncio.create_task(watch_loop())
            logger.info(f"Started watching services: {watch_key}")
            
        except Exception as e:
            logger.error(f"Failed to start watching services: {e}")
    
    async def watch_pods(self, callback, namespace: str = None, label_selector: str = None):
        """Watch for pod changes"""
        try:
            target_namespace = namespace or self.namespace
            watch_key = f"pods:{target_namespace}:{label_selector or 'all'}"
            
            if watch_key in self.watch_tasks:
                logger.info(f"Already watching pods for {watch_key}")
                return
            
            async def watch_loop():
                w = watch.Watch()
                self.watchers[watch_key] = w
                
                try:
                    if target_namespace == "all":
                        stream = w.stream(
                            self.v1.list_pod_for_all_namespaces,
                            label_selector=label_selector
                        )
                    else:
                        stream = w.stream(
                            self.v1.list_namespaced_pod,
                            namespace=target_namespace,
                            label_selector=label_selector
                        )
                    
                    for event in stream:
                        event_type = event['type']
                        pod = event['object']
                        
                        try:
                            await callback(event_type, pod)
                        except Exception as e:
                            logger.error(f"Pod watch callback error: {e}")
                            
                except Exception as e:
                    logger.error(f"Pod watch error: {e}")
                finally:
                    if watch_key in self.watchers:
                        del self.watchers[watch_key]
            
            self.watch_tasks[watch_key] = asyncio.create_task(watch_loop())
            logger.info(f"Started watching pods: {watch_key}")
            
        except Exception as e:
            logger.error(f"Failed to start watching pods: {e}")
    
    async def get_configmap(self, name: str, namespace: str = None) -> Optional[Dict[str, str]]:
        """Get ConfigMap data"""
        try:
            target_namespace = namespace or self.namespace
            
            configmap = self.v1.read_namespaced_config_map(
                name=name,
                namespace=target_namespace
            )
            
            return configmap.data or {}
            
        except ApiException as e:
            if e.status == 404:
                return None
            else:
                logger.error(f"Failed to get ConfigMap {name}: {e}")
                return None
    
    async def get_secret(self, name: str, namespace: str = None) -> Optional[Dict[str, str]]:
        """Get Secret data"""
        try:
            target_namespace = namespace or self.namespace
            
            secret = self.v1.read_namespaced_secret(
                name=name,
                namespace=target_namespace
            )
            
            # Decode base64 values
            if secret.data:
                import base64
                decoded_data = {}
                for key, value in secret.data.items():
                    decoded_data[key] = base64.b64decode(value).decode('utf-8')
                return decoded_data
            
            return {}
            
        except ApiException as e:
            if e.status == 404:
                return None
            else:
                logger.error(f"Failed to get Secret {name}: {e}")
                return None
    
    async def stop_all_watches(self):
        """Stop all active watches"""
        for watch_key, watcher in self.watchers.items():
            try:
                watcher.stop()
            except:
                pass
        
        for watch_key, task in self.watch_tasks.items():
            try:
                task.cancel()
                await task
            except asyncio.CancelledError:
                pass
            except:
                pass
        
        self.watchers.clear()
        self.watch_tasks.clear()
        logger.info("Stopped all Kubernetes watches")

class KubernetesDiscoveryTemplate:
    """
    Kubernetes Discovery Template for Ainflue Platform
    
    A comprehensive Kubernetes native service discovery that provides:
    - Service and endpoint discovery
    - Pod health monitoring
    - Real-time change notifications
    - ConfigMap and Secret management
    """
    
    def __init__(self):
        self.service_name = "kubernetes-discovery"
        self.service_version = "1.0.0"
        self.description = "Production-ready Kubernetes native service discovery"
    
    def create_client(self, config: Dict[str, Any]) -> KubernetesDiscoveryClient:
        """Create a Kubernetes discovery client"""
        return KubernetesDiscoveryClient(
            namespace=config.get("namespace", "default"),
            in_cluster=config.get("in_cluster")
        )
    
    def get_template_info(self) -> Dict[str, Any]:
        """Get Kubernetes discovery template information"""
        return {
            "name": self.service_name,
            "version": self.service_version,
            "description": self.description,
            "features": [
                "Kubernetes native service discovery",
                "Pod health and readiness monitoring",
                "Real-time watch mechanisms",
                "Multi-namespace support",
                "ConfigMap and Secret management",
                "Label and annotation filtering",
                "In-cluster and external operation",
                "Load balancer integration"
            ],
            "kubernetes_features": [
                "Service API integration",
                "Endpoints API for pod discovery",
                "Watch API for real-time updates",
                "ConfigMap configuration",
                "Secret management",
                "Multi-cluster support",
                "RBAC compatibility",
                "Health check integration"
            ],
            "dependencies": ["kubernetes", "prometheus"],
            "endpoints": [
                "/k8s/services",
                "/k8s/service/{name}",
                "/k8s/pods",
                "/k8s/configmap/{name}",
                "/k8s/secret/{name}"
            ]
        }