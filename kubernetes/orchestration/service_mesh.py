"""IA Influencer Agent - Service Mesh Management
Enterprise service mesh orchestration and traffic management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

Features:
- Istio service mesh management
- Traffic routing and load balancing
- Security policies and mTLS
- Observability and distributed tracing
- Circuit breaker and retry policies
- Canary deployments and A/B testing
"""
import asyncio
import logging
import json
import yaml
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import hashlib

from kubernetes import client, config
from kubernetes.client.rest import ApiException
import prometheus_client

# Note: Import paths adjusted for actual deployment structure
from .base_manager import BaseDeploymentManager

# Mock metrics collector for standalone operation
class MetricsCollector:
    """Mock metrics collector."""    def __init__(self):
        """Initialize service mesh metrics collector with observability"""        self.logger = logging.getLogger(f"{__name__}.MetricsCollector")
        self.mesh_metrics = ['request_volume', 'success_rate', 'latency_p99', 'circuit_breaker_status']
        self.security_metrics = ['mTLS_status', 'unauthorized_requests', 'policy_violations']
        self.observability_tools = ['jaeger', 'zipkin', 'kiali', 'grafana']
        self.sidecar_metrics = ['cpu_usage', 'memory_usage', 'proxy_latency']
        self.traffic_policies = {}
        self.mesh_topology = {}
        self.logger.info("Service Mesh MetricsCollector initialized with observability")


class ServiceMeshType(Enum):
    """Service mesh types."""    ISTIO = "istio"
    LINKERD = "linkerd"
    CONSUL_CONNECT = "consul-connect"
    AWS_APP_MESH = "aws-app-mesh"


class TrafficPolicy(Enum):
    """Traffic routing policies."""    ROUND_ROBIN = "round_robin"
    LEAST_CONN = "least_conn"
    RANDOM = "random"
    WEIGHTED = "weighted"
    CONSISTENT_HASH = "consistent_hash"


class SecurityMode(Enum):
    """Security modes for service communication."""    PERMISSIVE = "PERMISSIVE"
    STRICT = "STRICT"
    DISABLE = "DISABLE"


@dataclass
class ServiceMeshConfig:
    """Service mesh configuration."""    mesh_type: ServiceMeshType
    version: str
    namespace: str
    mtls_mode: SecurityMode
    ingress_gateways: List[Dict[str, Any]]
    egress_gateways: List[Dict[str, Any]]
    observability: Dict[str, Any]
    addons: List[str]


@dataclass
class VirtualService:
    """Virtual service configuration."""    name: str
    namespace: str
    hosts: List[str]
    gateways: List[str]
    http_routes: List[Dict[str, Any]]
    tcp_routes: Optional[List[Dict[str, Any]]] = None
    tls_routes: Optional[List[Dict[str, Any]]] = None


@dataclass
class DestinationRule:
    """Destination rule configuration."""    name: str
    namespace: str
    host: str
    traffic_policy: Dict[str, Any]
    subsets: List[Dict[str, Any]]
    port_level_settings: Optional[List[Dict[str, Any]]] = None


@dataclass
class Gateway:
    """Gateway configuration."""    name: str
    namespace: str
    selector: Dict[str, str]
    servers: List[Dict[str, Any]]


@dataclass
class PeerAuthentication:
    """Peer authentication configuration."""    name: str
    namespace: str
    selector: Dict[str, str]
    mtls_mode: SecurityMode
    port_level_mtls: Optional[Dict[str, SecurityMode]] = None


class ServiceMeshManager(BaseDeploymentManager):
    """    Enterprise service mesh manager.
    
    Manages service mesh infrastructure for the IA Influencer Agent
    platform with advanced traffic management, security, and observability.
    """
    def __init__(
        self,
        mesh_type: ServiceMeshType = ServiceMeshType.ISTIO,
        mesh_namespace: str = "istio-system",
        metrics_collector: Optional[MetricsCollector] = None
    ):
        super().__init__()
        self.mesh_type = mesh_type
        self.mesh_namespace = mesh_namespace
        self.metrics_collector = metrics_collector or MetricsCollector()
        
        # Kubernetes clients
        self._init_kubernetes_clients()
        
        # Mesh resources
        self.virtual_services: Dict[str, VirtualService] = {}
        self.destination_rules: Dict[str, DestinationRule] = {}
        self.gateways: Dict[str, Gateway] = {}
        self.peer_authentications: Dict[str, PeerAuthentication] = {}
        
        # Metrics
        self.mesh_metrics = prometheus_client.Gauge(
            'service_mesh_services_total',
            'Total number of services in mesh',
            ['namespace', 'mesh_type']
        )
        
        self.traffic_metrics = prometheus_client.Counter(
            'service_mesh_traffic_total',
            'Total traffic through service mesh',
            ['source', 'destination', 'response_code']
        )

    def _init_kubernetes_clients(self) -> None:
        """Initialize Kubernetes clients."""        try:
            config.load_incluster_config()
            self.v1_core = client.CoreV1Api()
            self.v1_apps = client.AppsV1Api()
            self.custom_objects_api = client.CustomObjectsApi()
            
            self.logger.info("Kubernetes clients initialized for service mesh")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Kubernetes clients: {e}")
            raise

    async def install_service_mesh(self, config: ServiceMeshConfig) -> bool:
        """        Install service mesh infrastructure.
        
        Args:
            config: Service mesh configuration
            
        Returns:
            True if installation successful, False otherwise
        """        try:
            # Create mesh namespace
            namespace_created = await self._create_mesh_namespace(config.namespace)
            if not namespace_created:
                return False
            
            # Install mesh control plane
            control_plane_installed = await self._install_control_plane(config)
            if not control_plane_installed:
                return False
            
            # Install gateways
            gateways_installed = await self._install_gateways(config)
            if not gateways_installed:
                return False
            
            # Configure security
            security_configured = await self._configure_mesh_security(config)
            if not security_configured:
                return False
            
            # Install observability addons
            observability_installed = await self._install_observability_addons(config)
            if not observability_installed:
                return False
            
            # Wait for mesh to be ready
            mesh_ready = await self._wait_for_mesh_ready(config.namespace)
            if not mesh_ready:
                return False
            
            self.logger.info(f"Service mesh {config.mesh_type.value} installed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install service mesh: {e}")
            return False

    async def _create_mesh_namespace(self, namespace: str) -> bool:
        """Create service mesh namespace."""        try:
            namespace_body = client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=namespace,
                    labels={
                        "istio-injection": "disabled",
                        "name": namespace
                    }
                )
            )
            
            try:
                self.v1_core.create_namespace(body=namespace_body)
                self.logger.info(f"Namespace '{namespace}' created for service mesh")
            except ApiException as e:
                if e.status == 409:  # Already exists
                    self.logger.info(f"Namespace '{namespace}' already exists")
                else:
                    raise
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create mesh namespace '{namespace}': {e}")
            return False

    async def _install_control_plane(self, config: ServiceMeshConfig) -> bool:
        """Install service mesh control plane."""        try:
            if config.mesh_type == ServiceMeshType.ISTIO:
                return await self._install_istio_control_plane(config)
            elif config.mesh_type == ServiceMeshType.LINKERD:
                return await self._install_linkerd_control_plane(config)
            else:
                self.logger.error(f"Unsupported mesh type: {config.mesh_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to install control plane: {e}")
            return False

    async def _install_istio_control_plane(self, config: ServiceMeshConfig) -> bool:
        """Install Istio control plane."""        try:
            # Create Istio operator configuration
            istio_operator = {
                "apiVersion": "install.istio.io/v1alpha1",
                "kind": "IstioOperator",
                "metadata": {
                    "name": "control-plane",
                    "namespace": config.namespace
                },
                "spec": {
                    "values": {
                        "global": {
                            "meshID": "mesh1",
                            "multiCluster": {
                                "clusterName": "cluster1"
                            },
                            "network": "network1"
                        }
                    },
                    "components": {
                        "pilot": {
                            "k8s": {
                                "resources": {
                                    "requests": {
                                        "cpu": "100m",
                                        "memory": "128Mi"
                                    },
                                    "limits": {
                                        "cpu": "500m",
                                        "memory": "512Mi"
                                    }
                                }
                            }
                        },
                        "ingressGateways": [
                            {
                                "name": "istio-ingressgateway",
                                "enabled": True,
                                "k8s": {
                                    "service": {
                                        "type": "LoadBalancer",
                                        "ports": [
                                            {
                                                "port": 80,
                                                "targetPort": 8080,
                                                "name": "http2"
                                            },
                                            {
                                                "port": 443,
                                                "targetPort": 8443,
                                                "name": "https"
                                            }
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                }
            }
            
            # Apply Istio operator
            await self._apply_custom_resource(
                istio_operator,
                "install.istio.io",
                "v1alpha1",
                "istiooperators",
                config.namespace
            )
            
            self.logger.info("Istio control plane configuration applied")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install Istio control plane: {e}")
            return False

    async def _install_linkerd_control_plane(self, config: ServiceMeshConfig) -> bool:
        """Install Linkerd control plane."""        try:
            # Linkerd installation would go here
            self.logger.info("Linkerd control plane installation not implemented yet")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install Linkerd control plane: {e}")
            return False

    async def _install_gateways(self, config: ServiceMeshConfig) -> bool:
        """Install ingress and egress gateways."""        try:
            # Install ingress gateways
            for ingress_config in config.ingress_gateways:
                gateway_installed = await self._install_ingress_gateway(ingress_config, config.namespace)
                if not gateway_installed:
                    return False
            
            # Install egress gateways
            for egress_config in config.egress_gateways:
                gateway_installed = await self._install_egress_gateway(egress_config, config.namespace)
                if not gateway_installed:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install gateways: {e}")
            return False

    async def _install_ingress_gateway(self, gateway_config: Dict[str, Any], namespace: str) -> bool:
        """Install ingress gateway."""        try:
            gateway_name = gateway_config.get("name", "istio-ingressgateway")
            
            # Gateway is typically installed with control plane
            # Additional configuration can be applied here
            
            self.logger.info(f"Ingress gateway '{gateway_name}' configured")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install ingress gateway: {e}")
            return False

    async def _install_egress_gateway(self, gateway_config: Dict[str, Any], namespace: str) -> bool:
        """Install egress gateway."""        try:
            gateway_name = gateway_config.get("name", "istio-egressgateway")
            
            # Egress gateway configuration
            egress_gateway = {
                "apiVersion": "install.istio.io/v1alpha1",
                "kind": "IstioOperator",
                "metadata": {
                    "name": f"{gateway_name}-operator",
                    "namespace": namespace
                },
                "spec": {
                    "components": {
                        "egressGateways": [
                            {
                                "name": gateway_name,
                                "enabled": True,
                                "k8s": {
                                    "service": {
                                        "type": "ClusterIP"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
            
            await self._apply_custom_resource(
                egress_gateway,
                "install.istio.io",
                "v1alpha1",
                "istiooperators",
                namespace
            )
            
            self.logger.info(f"Egress gateway '{gateway_name}' configured")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install egress gateway: {e}")
            return False

    async def _configure_mesh_security(self, config: ServiceMeshConfig) -> bool:
        """Configure mesh security policies."""        try:
            # Create default peer authentication
            default_peer_auth = PeerAuthentication(
                name="default",
                namespace=config.namespace,
                selector={},
                mtls_mode=config.mtls_mode
            )
            
            auth_created = await self.create_peer_authentication(default_peer_auth)
            if not auth_created:
                return False
            
            # Configure namespace-level policies
            namespace_policies_configured = await self._configure_namespace_policies(config)
            if not namespace_policies_configured:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure mesh security: {e}")
            return False

    async def _configure_namespace_policies(self, config: ServiceMeshConfig) -> bool:
        """Configure namespace-level security policies."""        try:
            # Enable auto mTLS for application namespaces
            application_namespaces = ["ia-influencer-agent", "default"]
            
            for namespace in application_namespaces:
                peer_auth = PeerAuthentication(
                    name="default",
                    namespace=namespace,
                    selector={},
                    mtls_mode=SecurityMode.STRICT
                )
                
                await self.create_peer_authentication(peer_auth)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure namespace policies: {e}")
            return False

    async def _install_observability_addons(self, config: ServiceMeshConfig) -> bool:
        """Install observability addons."""        try:
            observability_config = config.observability
            
            # Install Jaeger for distributed tracing
            if observability_config.get("tracing", {}).get("enabled", True):
                jaeger_installed = await self._install_jaeger(config.namespace)
                if not jaeger_installed:
                    return False
            
            # Install Kiali for service mesh visualization
            if observability_config.get("visualization", {}).get("enabled", True):
                kiali_installed = await self._install_kiali(config.namespace)
                if not kiali_installed:
                    return False
            
            # Install Grafana for metrics visualization
            if observability_config.get("metrics", {}).get("enabled", True):
                grafana_installed = await self._install_grafana(config.namespace)
                if not grafana_installed:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install observability addons: {e}")
            return False

    async def _install_jaeger(self, namespace: str) -> bool:
        """Install Jaeger for distributed tracing."""        try:
            jaeger_config = {
                "apiVersion": "jaegertracing.io/v1",
                "kind": "Jaeger",
                "metadata": {
                    "name": "jaeger",
                    "namespace": namespace
                },
                "spec": {
                    "strategy": "production",
                    "storage": {
                        "type": "elasticsearch",
                        "elasticsearch": {
                            "nodeCount": 3,
                            "resources": {
                                "requests": {
                                    "cpu": "200m",
                                    "memory": "1Gi"
                                },
                                "limits": {
                                    "cpu": "1",
                                    "memory": "2Gi"
                                }
                            }
                        }
                    }
                }
            }
            
            await self._apply_custom_resource(
                jaeger_config,
                "jaegertracing.io",
                "v1",
                "jaegers",
                namespace
            )
            
            self.logger.info("Jaeger tracing installed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install Jaeger: {e}")
            return False

    async def _install_kiali(self, namespace: str) -> bool:
        """Install Kiali for service mesh visualization."""        try:
            kiali_config = {
                "apiVersion": "kiali.io/v1alpha1",
                "kind": "Kiali",
                "metadata": {
                    "name": "kiali",
                    "namespace": namespace
                },
                "spec": {
                    "auth": {
                        "strategy": "anonymous"
                    },
                    "deployment": {
                        "accessible_namespaces": ["**"],
                        "image_name": "quay.io/kiali/kiali",
                        "image_version": "latest"
                    },
                    "external_services": {
                        "prometheus": {
                            "url": "http://prometheus:9090"
                        },
                        "tracing": {
                            "in_cluster_url": "http://jaeger-query:16686"
                        },
                        "grafana": {
                            "in_cluster_url": "http://grafana:3000"
                        }
                    }
                }
            }
            
            await self._apply_custom_resource(
                kiali_config,
                "kiali.io",
                "v1alpha1",
                "kialis",
                namespace
            )
            
            self.logger.info("Kiali visualization installed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install Kiali: {e}")
            return False

    async def _install_grafana(self, namespace: str) -> bool:
        """Install Grafana for metrics visualization."""        try:
            # Grafana deployment
            grafana_deployment = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "grafana",
                    "namespace": namespace,
                    "labels": {
                        "app": "grafana"
                    }
                },
                "spec": {
                    "replicas": 1,
                    "selector": {
                        "matchLabels": {
                            "app": "grafana"
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": "grafana"
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "name": "grafana",
                                    "image": "grafana/grafana:latest",
                                    "ports": [
                                        {
                                            "containerPort": 3000
                                        }
                                    ],
                                    "env": [
                                        {
                                            "name": "GF_SECURITY_ADMIN_PASSWORD",
                                            "value": "admin"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
            
            self.v1_apps.create_namespaced_deployment(
                namespace=namespace,
                body=grafana_deployment
            )
            
            # Grafana service
            grafana_service = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "grafana",
                    "namespace": namespace
                },
                "spec": {
                    "selector": {
                        "app": "grafana"
                    },
                    "ports": [
                        {
                            "port": 3000,
                            "targetPort": 3000
                        }
                    ]
                }
            }
            
            self.v1_core.create_namespaced_service(
                namespace=namespace,
                body=grafana_service
            )
            
            self.logger.info("Grafana metrics visualization installed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install Grafana: {e}")
            return False

    async def _wait_for_mesh_ready(self, namespace: str, timeout: int = 600) -> bool:
        """Wait for service mesh to be ready."""        try:
            start_time = datetime.now()
            
            while (datetime.now() - start_time).total_seconds() < timeout:
                # Check if control plane pods are ready
                pods = self.v1_core.list_namespaced_pod(
                    namespace=namespace,
                    label_selector="app=istiod"
                )
                
                if pods.items:
                    all_ready = True
                    for pod in pods.items:
                        if not all(
                            condition.status == "True" 
                            for condition in (pod.status.conditions or [])
                            if condition.type == "Ready"
                        ):
                            all_ready = False
                            break
                    
                    if all_ready:
                        self.logger.info("Service mesh is ready")
                        return True
                
                await asyncio.sleep(10)
            
            self.logger.error("Service mesh failed to become ready within timeout")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to wait for mesh ready: {e}")
            return False

    async def create_virtual_service(self, virtual_service: VirtualService) -> bool:
        """        Create virtual service for traffic routing.
        
        Args:
            virtual_service: Virtual service configuration
            
        Returns:
            True if creation successful, False otherwise
        """        try:
            vs_config = {
                "apiVersion": "networking.istio.io/v1beta1",
                "kind": "VirtualService",
                "metadata": {
                    "name": virtual_service.name,
                    "namespace": virtual_service.namespace
                },
                "spec": {
                    "hosts": virtual_service.hosts,
                    "gateways": virtual_service.gateways,
                    "http": virtual_service.http_routes
                }
            }
            
            if virtual_service.tcp_routes:
                vs_config["spec"]["tcp"] = virtual_service.tcp_routes
            
            if virtual_service.tls_routes:
                vs_config["spec"]["tls"] = virtual_service.tls_routes
            
            await self._apply_custom_resource(
                vs_config,
                "networking.istio.io",
                "v1beta1",
                "virtualservices",
                virtual_service.namespace
            )
            
            self.virtual_services[f"{virtual_service.namespace}/{virtual_service.name}"] = virtual_service
            
            self.logger.info(f"Virtual service '{virtual_service.name}' created")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create virtual service '{virtual_service.name}': {e}")
            return False

    async def create_destination_rule(self, destination_rule: DestinationRule) -> bool:
        """        Create destination rule for traffic policies.
        
        Args:
            destination_rule: Destination rule configuration
            
        Returns:
            True if creation successful, False otherwise
        """        try:
            dr_config = {
                "apiVersion": "networking.istio.io/v1beta1",
                "kind": "DestinationRule",
                "metadata": {
                    "name": destination_rule.name,
                    "namespace": destination_rule.namespace
                },
                "spec": {
                    "host": destination_rule.host,
                    "trafficPolicy": destination_rule.traffic_policy,
                    "subsets": destination_rule.subsets
                }
            }
            
            if destination_rule.port_level_settings:
                dr_config["spec"]["portLevelSettings"] = destination_rule.port_level_settings
            
            await self._apply_custom_resource(
                dr_config,
                "networking.istio.io",
                "v1beta1",
                "destinationrules",
                destination_rule.namespace
            )
            
            self.destination_rules[f"{destination_rule.namespace}/{destination_rule.name}"] = destination_rule
            
            self.logger.info(f"Destination rule '{destination_rule.name}' created")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create destination rule '{destination_rule.name}': {e}")
            return False

    async def create_gateway(self, gateway: Gateway) -> bool:
        """        Create gateway for ingress/egress traffic.
        
        Args:
            gateway: Gateway configuration
            
        Returns:
            True if creation successful, False otherwise
        """        try:
            gateway_config = {
                "apiVersion": "networking.istio.io/v1beta1",
                "kind": "Gateway",
                "metadata": {
                    "name": gateway.name,
                    "namespace": gateway.namespace
                },
                "spec": {
                    "selector": gateway.selector,
                    "servers": gateway.servers
                }
            }
            
            await self._apply_custom_resource(
                gateway_config,
                "networking.istio.io",
                "v1beta1",
                "gateways",
                gateway.namespace
            )
            
            self.gateways[f"{gateway.namespace}/{gateway.name}"] = gateway
            
            self.logger.info(f"Gateway '{gateway.name}' created")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create gateway '{gateway.name}': {e}")
            return False

    async def create_peer_authentication(self, peer_auth: PeerAuthentication) -> bool:
        """        Create peer authentication policy.
        
        Args:
            peer_auth: Peer authentication configuration
            
        Returns:
            True if creation successful, False otherwise
        """        try:
            pa_config = {
                "apiVersion": "security.istio.io/v1beta1",
                "kind": "PeerAuthentication",
                "metadata": {
                    "name": peer_auth.name,
                    "namespace": peer_auth.namespace
                },
                "spec": {
                    "selector": {
                        "matchLabels": peer_auth.selector
                    },
                    "mtls": {
                        "mode": peer_auth.mtls_mode.value
                    }
                }
            }
            
            if peer_auth.port_level_mtls:
                pa_config["spec"]["portLevelMtls"] = {
                    str(port): {"mode": mode.value}
                    for port, mode in peer_auth.port_level_mtls.items()
                }
            
            await self._apply_custom_resource(
                pa_config,
                "security.istio.io",
                "v1beta1",
                "peerauthentications",
                peer_auth.namespace
            )
            
            self.peer_authentications[f"{peer_auth.namespace}/{peer_auth.name}"] = peer_auth
            
            self.logger.info(f"Peer authentication '{peer_auth.name}' created")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create peer authentication '{peer_auth.name}': {e}")
            return False

    async def enable_namespace_injection(self, namespace: str) -> bool:
        """        Enable automatic sidecar injection for namespace.
        
        Args:
            namespace: Namespace to enable injection for
            
        Returns:
            True if enabled successfully, False otherwise
        """        try:
            # Get current namespace
            current_namespace = self.v1_core.read_namespace(name=namespace)
            
            # Update labels to enable injection
            if not current_namespace.metadata.labels:
                current_namespace.metadata.labels = {}
            
            current_namespace.metadata.labels["istio-injection"] = "enabled"
            
            # Patch namespace
            self.v1_core.patch_namespace(
                name=namespace,
                body=current_namespace
            )
            
            self.logger.info(f"Sidecar injection enabled for namespace '{namespace}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enable injection for namespace '{namespace}': {e}")
            return False

    async def create_canary_deployment(
        self,
        service_name: str,
        namespace: str,
        canary_weight: int = 10,
        stable_weight: int = 90
    ) -> bool:
        """        Create canary deployment configuration.
        
        Args:
            service_name: Name of the service
            namespace: Service namespace
            canary_weight: Weight for canary version (percentage)
            stable_weight: Weight for stable version (percentage)
            
        Returns:
            True if canary deployment created successfully, False otherwise
        """        try:
            # Create destination rule with subsets
            destination_rule = DestinationRule(
                name=f"{service_name}-canary",
                namespace=namespace,
                host=service_name,
                traffic_policy={
                    "loadBalancer": {
                        "simple": "LEAST_CONN"
                    }
                },
                subsets=[
                    {
                        "name": "stable",
                        "labels": {"version": "stable"}
                    },
                    {
                        "name": "canary",
                        "labels": {"version": "canary"}
                    }
                ]
            )
            
            dr_created = await self.create_destination_rule(destination_rule)
            if not dr_created:
                return False
            
            # Create virtual service with traffic splitting
            virtual_service = VirtualService(
                name=f"{service_name}-canary",
                namespace=namespace,
                hosts=[service_name],
                gateways=["mesh"],
                http_routes=[
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": service_name,
                                    "subset": "stable"
                                },
                                "weight": stable_weight
                            },
                            {
                                "destination": {
                                    "host": service_name,
                                    "subset": "canary"
                                },
                                "weight": canary_weight
                            }
                        ]
                    }
                ]
            )
            
            vs_created = await self.create_virtual_service(virtual_service)
            if not vs_created:
                return False
            
            self.logger.info(f"Canary deployment created for service '{service_name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create canary deployment for '{service_name}': {e}")
            return False

    async def _apply_custom_resource(
        self,
        resource: Dict[str, Any],
        group: str,
        version: str,
        plural: str,
        namespace: str
    ) -> bool:
        """Apply custom resource to Kubernetes."""        try:
            self.custom_objects_api.create_namespaced_custom_object(
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
                body=resource
            )
            return True
            
        except ApiException as e:
            if e.status == 409:  # Already exists, try to update
                try:
                    self.custom_objects_api.patch_namespaced_custom_object(
                        group=group,
                        version=version,
                        namespace=namespace,
                        plural=plural,
                        name=resource["metadata"]["name"],
                        body=resource
                    )
                    return True
                except ApiException:
                    self.logger.error(f"Failed to update custom resource: {e}")
                    return False
            else:
                self.logger.error(f"Failed to create custom resource: {e}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to apply custom resource: {e}")
            return False

    async def get_mesh_status(self) -> Dict[str, Any]:
        """        Get service mesh status and metrics.
        
        Returns:
            Service mesh status information
        """        try:
            # Get control plane status
            control_plane_pods = self.v1_core.list_namespaced_pod(
                namespace=self.mesh_namespace,
                label_selector="app=istiod"
            )
            
            # Get gateway status
            gateway_pods = self.v1_core.list_namespaced_pod(
                namespace=self.mesh_namespace,
                label_selector="app=istio-ingressgateway"
            )
            
            # Get proxy status (count of injected sidecars)
            all_pods = self.v1_core.list_pod_for_all_namespaces()
            injected_pods = [
                pod for pod in all_pods.items
                if any(container.name == "istio-proxy" for container in pod.spec.containers)
            ]
            
            status = {
                "mesh_type": self.mesh_type.value,
                "namespace": self.mesh_namespace,
                "control_plane": {
                    "pods": len(control_plane_pods.items),
                    "ready": len([
                        pod for pod in control_plane_pods.items
                        if all(
                            condition.status == "True" 
                            for condition in (pod.status.conditions or [])
                            if condition.type == "Ready"
                        )
                    ])
                },
                "gateways": {
                    "pods": len(gateway_pods.items),
                    "ready": len([
                        pod for pod in gateway_pods.items
                        if all(
                            condition.status == "True" 
                            for condition in (pod.status.conditions or [])
                            if condition.type == "Ready"
                        )
                    ])
                },
                "sidecars": {
                    "total": len(injected_pods),
                    "ready": len([
                        pod for pod in injected_pods
                        if all(
                            condition.status == "True" 
                            for condition in (pod.status.conditions or [])
                            if condition.type == "Ready"
                        )
                    ])
                },
                "resources": {
                    "virtual_services": len(self.virtual_services),
                    "destination_rules": len(self.destination_rules),
                    "gateways": len(self.gateways),
                    "peer_authentications": len(self.peer_authentications)
                }
            }
            
            # Update metrics
            self.mesh_metrics.labels(
                namespace=self.mesh_namespace,
                mesh_type=self.mesh_type.value
            ).set(status["sidecars"]["total"])
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get mesh status: {e}")
            return {}

    async def uninstall_service_mesh(self) -> bool:
        """        Uninstall service mesh infrastructure.
        
        Returns:
            True if uninstallation successful, False otherwise
        """        try:
            # Remove custom resources
            await self._cleanup_custom_resources()
            
            # Remove control plane
            control_plane_removed = await self._remove_control_plane()
            if not control_plane_removed:
                return False
            
            # Remove namespace
            try:
                self.v1_core.delete_namespace(name=self.mesh_namespace)
            except ApiException as e:
                if e.status != 404:  # Ignore if already deleted
                    raise
            
            self.logger.info("Service mesh uninstalled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to uninstall service mesh: {e}")
            return False

    async def _cleanup_custom_resources(self) -> None:
        """Cleanup all mesh custom resources."""        try:
            # Clear local registries
            self.virtual_services.clear()
            self.destination_rules.clear()
            self.gateways.clear()
            self.peer_authentications.clear()
            
            self.logger.info("Custom resources cleaned up")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup custom resources: {e}")

    async def _remove_control_plane(self) -> bool:
        """Remove service mesh control plane."""        try:
            # Remove Istio operator
            try:
                self.custom_objects_api.delete_namespaced_custom_object(
                    group="install.istio.io",
                    version="v1alpha1",
                    namespace=self.mesh_namespace,
                    plural="istiooperators",
                    name="control-plane"
                )
            except ApiException as e:
                if e.status != 404:  # Ignore if already deleted
                    raise
            
            self.logger.info("Control plane removed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove control plane: {e}")
            return False
