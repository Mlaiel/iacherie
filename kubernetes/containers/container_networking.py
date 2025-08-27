"""
🌐 Container Networking Manager - IA-Influencer-Agent Infrastructure
====================================================================
Expert: Network Engineer + DevOps + Service Mesh Specialist
Creator: Fahed Mlaiel <mlaiel@live.de>
====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Professional container networking management with service discovery,
load balancing, and advanced networking policies.
"""

import asyncio
import logging
import json
import yaml
import ipaddress
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import kubernetes
from kubernetes import client, config
import consul
import etcd3

logger = logging.getLogger(__name__)

class NetworkProtocol(Enum):
    """Network protocols"""
    TCP = "TCP"
    UDP = "UDP"
    SCTP = "SCTP"
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    GRPC = "GRPC"

class LoadBalancerType(Enum):
    """Load balancer types"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"

class ServiceMeshType(Enum):
    """Service mesh types"""
    ISTIO = "istio"
    LINKERD = "linkerd"
    CONSUL_CONNECT = "consul_connect"
    ENVOY = "envoy"

class NetworkPolicyAction(Enum):
    """Network policy actions"""
    ALLOW = "allow"
    DENY = "deny"
    LOG = "log"

@dataclass
class NetworkPort:
    """Network port configuration"""
    name: str
    port: int
    target_port: Union[int, str]
    protocol: NetworkProtocol = NetworkProtocol.TCP
    node_port: Optional[int] = None

@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""
    name: str
    ip: str
    port: int
    protocol: NetworkProtocol = NetworkProtocol.TCP
    weight: int = 100
    health_check_path: str = "/health"
    metadata: Dict[str, str] = field(default_factory=dict)

@dataclass
class LoadBalancerConfig:
    """Load balancer configuration"""
    name: str
    algorithm: LoadBalancerType
    sticky_sessions: bool = False
    session_affinity_timeout: int = 3600
    health_check_interval: int = 30
    health_check_timeout: int = 5
    health_check_retries: int = 3
    connection_timeout: int = 60
    keep_alive: bool = True

@dataclass
class ServiceConfig:
    """Service configuration"""
    name: str
    namespace: str
    selector: Dict[str, str]
    ports: List[NetworkPort]
    service_type: str = "ClusterIP"
    cluster_ip: Optional[str] = None
    external_ips: List[str] = field(default_factory=list)
    load_balancer_config: Optional[LoadBalancerConfig] = None
    annotations: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class IngressRule:
    """Ingress rule configuration"""
    host: str
    paths: List[Dict[str, Any]]
    tls_secret: Optional[str] = None

@dataclass
class IngressConfig:
    """Ingress configuration"""
    name: str
    namespace: str
    ingress_class: str = "nginx"
    rules: List[IngressRule] = field(default_factory=list)
    annotations: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class NetworkPolicy:
    """Network policy configuration"""
    name: str
    namespace: str
    pod_selector: Dict[str, str]
    policy_types: List[str]  # ["Ingress", "Egress"]
    ingress_rules: List[Dict[str, Any]] = field(default_factory=list)
    egress_rules: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ServiceMeshConfig:
    """Service mesh configuration"""
    name: str
    mesh_type: ServiceMeshType
    namespace: str = "istio-system"
    gateway_config: Dict[str, Any] = field(default_factory=dict)
    virtual_service_config: Dict[str, Any] = field(default_factory=dict)
    destination_rule_config: Dict[str, Any] = field(default_factory=dict)
    mtls_mode: str = "STRICT"
    traffic_splitting: Dict[str, int] = field(default_factory=dict)

class ContainerNetworkingManager:
    """Professional container networking manager"""
    
    def __init__(self, config_path: str = "/app/config/networking"):
        self.config_path = Path(config_path)
        self.k8s_client = None
        self.consul_client = None
        self.etcd_client = None
        self.services = {}
        self.ingresses = {}
        self.network_policies = {}
        self.service_mesh_configs = {}
        self.endpoints = {}
        self.dns_records = {}
        self.load_balancers = {}
        self.initialized = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    async def initialize(self) -> bool:
        """Initialize container networking manager"""
        try:
            # Initialize Kubernetes client
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
            
            self.k8s_client = client.ApiClient()
            
            # Create config directory
            self.config_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize service discovery clients
            await self._initialize_service_discovery()
            
            # Load existing configurations
            await self._load_configurations()
            
            # Setup default networking for IA-Influencer
            await self._setup_default_networking()
            
            # Start monitoring tasks
            asyncio.create_task(self._monitor_endpoints())
            asyncio.create_task(self._health_check_task())
            
            self.initialized = True
            self.logger.info("✅ ContainerNetworkingManager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing ContainerNetworkingManager: {e}")
            return False
    
    async def _initialize_service_discovery(self) -> None:
        """Initialize service discovery clients"""
        try:
            # Initialize Consul client
            try:
                self.consul_client = consul.Consul(
                    host=os.getenv('CONSUL_HOST', 'localhost'),
                    port=int(os.getenv('CONSUL_PORT', 8500))
                )
                self.logger.info("✅ Consul client initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not initialize Consul client: {e}")
            
            # Initialize etcd client
            try:
                self.etcd_client = etcd3.client(
                    host=os.getenv('ETCD_HOST', 'localhost'),
                    port=int(os.getenv('ETCD_PORT', 2379))
                )
                self.logger.info("✅ etcd client initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not initialize etcd client: {e}")
                
        except Exception as e:
            self.logger.error(f"❌ Error initializing service discovery: {e}")
    
    async def _load_configurations(self) -> None:
        """Load existing networking configurations"""
        try:
            # Load services
            services_file = self.config_path / "services.yml"
            if services_file.exists():
                with open(services_file, 'r') as f:
                    services_data = yaml.safe_load(f)
                    for service_data in services_data.get('services', []):
                        service_config = ServiceConfig(**service_data)
                        self.services[f"{service_config.namespace}/{service_config.name}"] = service_config
            
            # Load ingresses
            ingresses_file = self.config_path / "ingresses.yml"
            if ingresses_file.exists():
                with open(ingresses_file, 'r') as f:
                    ingresses_data = yaml.safe_load(f)
                    for ingress_data in ingresses_data.get('ingresses', []):
                        ingress_config = IngressConfig(**ingress_data)
                        self.ingresses[f"{ingress_config.namespace}/{ingress_config.name}"] = ingress_config
            
            # Load network policies
            policies_file = self.config_path / "network_policies.yml"
            if policies_file.exists():
                with open(policies_file, 'r') as f:
                    policies_data = yaml.safe_load(f)
                    for policy_data in policies_data.get('policies', []):
                        policy = NetworkPolicy(**policy_data)
                        self.network_policies[f"{policy.namespace}/{policy.name}"] = policy
                        
        except Exception as e:
            self.logger.warning(f"⚠️ Error loading configurations: {e}")
    
    async def _setup_default_networking(self) -> None:
        """Setup default networking for IA-Influencer platform"""
        try:
            # Web API Service
            web_api_service = ServiceConfig(
                name="ia-influencer-web-api",
                namespace="ia-influencer",
                selector={"app": "ia-influencer-web-api"},
                ports=[
                    NetworkPort(
                        name="http",
                        port=80,
                        target_port=8000,
                        protocol=NetworkProtocol.HTTP
                    ),
                    NetworkPort(
                        name="https",
                        port=443,
                        target_port=8443,
                        protocol=NetworkProtocol.HTTPS
                    )
                ],
                service_type="ClusterIP",
                load_balancer_config=LoadBalancerConfig(
                    name="web-api-lb",
                    algorithm=LoadBalancerType.ROUND_ROBIN,
                    sticky_sessions=True,
                    health_check_interval=15
                ),
                annotations={
                    "service.beta.kubernetes.io/aws-load-balancer-type": "nlb",
                    "prometheus.io/scrape": "true",
                    "prometheus.io/port": "8000",
                    "prometheus.io/path": "/metrics"
                }
            )
            
            # AI Engine Service
            ai_engine_service = ServiceConfig(
                name="ia-influencer-ai-engine",
                namespace="ia-influencer",
                selector={"app": "ia-influencer-ai-engine"},
                ports=[
                    NetworkPort(
                        name="grpc",
                        port=9090,
                        target_port=9090,
                        protocol=NetworkProtocol.GRPC
                    ),
                    NetworkPort(
                        name="metrics",
                        port=8080,
                        target_port=8080,
                        protocol=NetworkProtocol.HTTP
                    )
                ],
                service_type="ClusterIP",
                load_balancer_config=LoadBalancerConfig(
                    name="ai-engine-lb",
                    algorithm=LoadBalancerType.LEAST_CONNECTIONS,
                    health_check_interval=30
                )
            )
            
            # Database Service
            database_service = ServiceConfig(
                name="ia-influencer-database",
                namespace="ia-influencer",
                selector={"app": "postgresql"},
                ports=[
                    NetworkPort(
                        name="postgresql",
                        port=5432,
                        target_port=5432,
                        protocol=NetworkProtocol.TCP
                    )
                ],
                service_type="ClusterIP"
            )
            
            # Redis Service
            redis_service = ServiceConfig(
                name="ia-influencer-redis",
                namespace="ia-influencer",
                selector={"app": "redis"},
                ports=[
                    NetworkPort(
                        name="redis",
                        port=6379,
                        target_port=6379,
                        protocol=NetworkProtocol.TCP
                    )
                ],
                service_type="ClusterIP"
            )
            
            # Store services
            services_to_create = [
                web_api_service,
                ai_engine_service,
                database_service,
                redis_service
            ]
            
            for service in services_to_create:
                service_key = f"{service.namespace}/{service.name}"
                self.services[service_key] = service
            
            # Web API Ingress
            web_api_ingress = IngressConfig(
                name="ia-influencer-web-api",
                namespace="ia-influencer",
                ingress_class="nginx",
                rules=[
                    IngressRule(
                        host="api.ia-influencer-agent.com",
                        paths=[
                            {
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": "ia-influencer-web-api",
                                        "port": {"number": 80}
                                    }
                                }
                            }
                        ],
                        tls_secret="api-tls-cert"
                    ),
                    IngressRule(
                        host="app.ia-influencer-agent.com",
                        paths=[
                            {
                                "path": "/api",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": "ia-influencer-web-api",
                                        "port": {"number": 80}
                                    }
                                }
                            }
                        ],
                        tls_secret="app-tls-cert"
                    )
                ],
                annotations={
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/rate-limit": "100",
                    "nginx.ingress.kubernetes.io/rate-limit-window": "1m",
                    "nginx.ingress.kubernetes.io/ssl-redirect": "true",
                    "nginx.ingress.kubernetes.io/force-ssl-redirect": "true",
                    "nginx.ingress.kubernetes.io/proxy-body-size": "50m",
                    "nginx.ingress.kubernetes.io/cors-allow-origin": "*",
                    "nginx.ingress.kubernetes.io/cors-allow-methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "nginx.ingress.kubernetes.io/cors-allow-headers": "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization"
                }
            )
            
            ingress_key = f"{web_api_ingress.namespace}/{web_api_ingress.name}"
            self.ingresses[ingress_key] = web_api_ingress
            
            # Network Policies
            await self._setup_network_policies()
            
            # Service Mesh Configuration
            await self._setup_service_mesh()
            
            # Save configurations
            await self._save_configurations()
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up default networking: {e}")
    
    async def _setup_network_policies(self) -> None:
        """Setup network policies for IA-Influencer"""
        try:
            # Web API ingress policy
            web_api_policy = NetworkPolicy(
                name="ia-influencer-web-api-policy",
                namespace="ia-influencer",
                pod_selector={"app": "ia-influencer-web-api"},
                policy_types=["Ingress", "Egress"],
                ingress_rules=[
                    {
                        "from": [
                            {"namespaceSelector": {"matchLabels": {"name": "ingress-nginx"}}},
                            {"podSelector": {"matchLabels": {"app": "nginx-ingress"}}}
                        ],
                        "ports": [
                            {"protocol": "TCP", "port": 8000},
                            {"protocol": "TCP", "port": 8443}
                        ]
                    }
                ],
                egress_rules=[
                    {
                        "to": [
                            {"podSelector": {"matchLabels": {"app": "ia-influencer-ai-engine"}}},
                            {"podSelector": {"matchLabels": {"app": "postgresql"}}},
                            {"podSelector": {"matchLabels": {"app": "redis"}}}
                        ],
                        "ports": [
                            {"protocol": "TCP", "port": 9090},
                            {"protocol": "TCP", "port": 5432},
                            {"protocol": "TCP", "port": 6379}
                        ]
                    },
                    {
                        "to": [],
                        "ports": [
                            {"protocol": "TCP", "port": 53},
                            {"protocol": "UDP", "port": 53},
                            {"protocol": "TCP", "port": 443}
                        ]
                    }
                ]
            )
            
            # AI Engine policy
            ai_engine_policy = NetworkPolicy(
                name="ia-influencer-ai-engine-policy",
                namespace="ia-influencer",
                pod_selector={"app": "ia-influencer-ai-engine"},
                policy_types=["Ingress", "Egress"],
                ingress_rules=[
                    {
                        "from": [
                            {"podSelector": {"matchLabels": {"app": "ia-influencer-web-api"}}}
                        ],
                        "ports": [
                            {"protocol": "TCP", "port": 9090},
                            {"protocol": "TCP", "port": 8080}
                        ]
                    }
                ],
                egress_rules=[
                    {
                        "to": [
                            {"podSelector": {"matchLabels": {"app": "postgresql"}}},
                            {"podSelector": {"matchLabels": {"app": "redis"}}}
                        ],
                        "ports": [
                            {"protocol": "TCP", "port": 5432},
                            {"protocol": "TCP", "port": 6379}
                        ]
                    },
                    {
                        "to": [],
                        "ports": [
                            {"protocol": "TCP", "port": 53},
                            {"protocol": "UDP", "port": 53},
                            {"protocol": "TCP", "port": 443}
                        ]
                    }
                ]
            )
            
            # Database policy (deny all except from app services)
            database_policy = NetworkPolicy(
                name="ia-influencer-database-policy",
                namespace="ia-influencer",
                pod_selector={"app": "postgresql"},
                policy_types=["Ingress"],
                ingress_rules=[
                    {
                        "from": [
                            {"podSelector": {"matchLabels": {"app": "ia-influencer-web-api"}}},
                            {"podSelector": {"matchLabels": {"app": "ia-influencer-ai-engine"}}}
                        ],
                        "ports": [
                            {"protocol": "TCP", "port": 5432}
                        ]
                    }
                ]
            )
            
            # Redis policy
            redis_policy = NetworkPolicy(
                name="ia-influencer-redis-policy",
                namespace="ia-influencer",
                pod_selector={"app": "redis"},
                policy_types=["Ingress"],
                ingress_rules=[
                    {
                        "from": [
                            {"podSelector": {"matchLabels": {"app": "ia-influencer-web-api"}}},
                            {"podSelector": {"matchLabels": {"app": "ia-influencer-ai-engine"}}}
                        ],
                        "ports": [
                            {"protocol": "TCP", "port": 6379}
                        ]
                    }
                ]
            )
            
            # Store policies
            policies = [web_api_policy, ai_engine_policy, database_policy, redis_policy]
            for policy in policies:
                policy_key = f"{policy.namespace}/{policy.name}"
                self.network_policies[policy_key] = policy
                
        except Exception as e:
            self.logger.error(f"❌ Error setting up network policies: {e}")
    
    async def _setup_service_mesh(self) -> None:
        """Setup service mesh configuration"""
        try:
            # Istio service mesh for IA-Influencer
            istio_config = ServiceMeshConfig(
                name="ia-influencer-mesh",
                mesh_type=ServiceMeshType.ISTIO,
                namespace="ia-influencer",
                gateway_config={
                    "hosts": [
                        "api.ia-influencer-agent.com",
                        "app.ia-influencer-agent.com"
                    ],
                    "tls": {
                        "mode": "SIMPLE",
                        "credentialName": "ia-influencer-tls"
                    }
                },
                virtual_service_config={
                    "http": [
                        {
                            "match": [{"uri": {"prefix": "/api/v1"}}],
                            "route": [
                                {
                                    "destination": {
                                        "host": "ia-influencer-web-api",
                                        "port": {"number": 80}
                                    },
                                    "weight": 100
                                }
                            ],
                            "fault": {
                                "delay": {
                                    "percentage": {"value": 0.1},
                                    "fixedDelay": "5s"
                                }
                            },
                            "retries": {
                                "attempts": 3,
                                "perTryTimeout": "10s"
                            }
                        }
                    ]
                },
                destination_rule_config={
                    "host": "ia-influencer-web-api",
                    "trafficPolicy": {
                        "loadBalancer": {
                            "simple": "ROUND_ROBIN"
                        },
                        "connectionPool": {
                            "tcp": {
                                "maxConnections": 100
                            },
                            "http": {
                                "http1MaxPendingRequests": 50,
                                "maxRequestsPerConnection": 10
                            }
                        },
                        "circuitBreaker": {
                            "consecutiveGatewayErrors": 5,
                            "interval": "30s",
                            "baseEjectionTime": "30s"
                        }
                    }
                },
                mtls_mode="STRICT",
                traffic_splitting={
                    "v1": 90,
                    "v2": 10
                }
            )
            
            self.service_mesh_configs["ia-influencer-mesh"] = istio_config
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up service mesh: {e}")
    
    async def _save_configurations(self) -> None:
        """Save networking configurations"""
        try:
            # Save services
            services_data = {
                "services": [asdict(service) for service in self.services.values()]
            }
            with open(self.config_path / "services.yml", 'w') as f:
                yaml.dump(services_data, f, default_flow_style=False)
            
            # Save ingresses
            ingresses_data = {
                "ingresses": [asdict(ingress) for ingress in self.ingresses.values()]
            }
            with open(self.config_path / "ingresses.yml", 'w') as f:
                yaml.dump(ingresses_data, f, default_flow_style=False)
            
            # Save network policies
            policies_data = {
                "policies": [asdict(policy) for policy in self.network_policies.values()]
            }
            with open(self.config_path / "network_policies.yml", 'w') as f:
                yaml.dump(policies_data, f, default_flow_style=False)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving configurations: {e}")
    
    async def create_service(self, service_config: ServiceConfig) -> bool:
        """Create Kubernetes service"""
        try:
            v1 = client.CoreV1Api()
            
            # Create service manifest
            service_manifest = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": service_config.name,
                    "namespace": service_config.namespace,
                    "labels": service_config.labels,
                    "annotations": service_config.annotations
                },
                "spec": {
                    "selector": service_config.selector,
                    "type": service_config.service_type,
                    "ports": [
                        {
                            "name": port.name,
                            "port": port.port,
                            "targetPort": port.target_port,
                            "protocol": port.protocol.value,
                            **({"nodePort": port.node_port} if port.node_port else {})
                        }
                        for port in service_config.ports
                    ]
                }
            }
            
            if service_config.cluster_ip:
                service_manifest["spec"]["clusterIP"] = service_config.cluster_ip
            
            if service_config.external_ips:
                service_manifest["spec"]["externalIPs"] = service_config.external_ips
            
            # Create service
            try:
                v1.create_namespaced_service(
                    namespace=service_config.namespace,
                    body=service_manifest
                )
                
                # Store service configuration
                service_key = f"{service_config.namespace}/{service_config.name}"
                self.services[service_key] = service_config
                
                self.logger.info(f"✅ Created service: {service_config.name}")
                
                # Register with service discovery
                await self._register_service(service_config)
                
                return True
                
            except client.rest.ApiException as e:
                if e.status == 409:  # Already exists
                    self.logger.info(f"ℹ️ Service {service_config.name} already exists")
                    return True
                else:
                    raise e
                    
        except Exception as e:
            self.logger.error(f"❌ Error creating service: {e}")
            return False
    
    async def create_ingress(self, ingress_config: IngressConfig) -> bool:
        """Create Kubernetes ingress"""
        try:
            networking_v1 = client.NetworkingV1Api()
            
            # Create ingress manifest
            ingress_manifest = {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "Ingress",
                "metadata": {
                    "name": ingress_config.name,
                    "namespace": ingress_config.namespace,
                    "labels": ingress_config.labels,
                    "annotations": ingress_config.annotations
                },
                "spec": {
                    "ingressClassName": ingress_config.ingress_class,
                    "rules": [],
                    "tls": []
                }
            }
            
            # Add rules
            for rule in ingress_config.rules:
                rule_manifest = {
                    "host": rule.host,
                    "http": {
                        "paths": rule.paths
                    }
                }
                ingress_manifest["spec"]["rules"].append(rule_manifest)
                
                # Add TLS configuration
                if rule.tls_secret:
                    tls_config = {
                        "hosts": [rule.host],
                        "secretName": rule.tls_secret
                    }
                    ingress_manifest["spec"]["tls"].append(tls_config)
            
            # Create ingress
            try:
                networking_v1.create_namespaced_ingress(
                    namespace=ingress_config.namespace,
                    body=ingress_manifest
                )
                
                # Store ingress configuration
                ingress_key = f"{ingress_config.namespace}/{ingress_config.name}"
                self.ingresses[ingress_key] = ingress_config
                
                self.logger.info(f"✅ Created ingress: {ingress_config.name}")
                return True
                
            except client.rest.ApiException as e:
                if e.status == 409:  # Already exists
                    self.logger.info(f"ℹ️ Ingress {ingress_config.name} already exists")
                    return True
                else:
                    raise e
                    
        except Exception as e:
            self.logger.error(f"❌ Error creating ingress: {e}")
            return False
    
    async def create_network_policy(self, policy: NetworkPolicy) -> bool:
        """Create Kubernetes network policy"""
        try:
            networking_v1 = client.NetworkingV1Api()
            
            # Create network policy manifest
            policy_manifest = {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": policy.name,
                    "namespace": policy.namespace
                },
                "spec": {
                    "podSelector": {
                        "matchLabels": policy.pod_selector
                    },
                    "policyTypes": policy.policy_types
                }
            }
            
            if policy.ingress_rules:
                policy_manifest["spec"]["ingress"] = policy.ingress_rules
            
            if policy.egress_rules:
                policy_manifest["spec"]["egress"] = policy.egress_rules
            
            # Create network policy
            try:
                networking_v1.create_namespaced_network_policy(
                    namespace=policy.namespace,
                    body=policy_manifest
                )
                
                # Store policy
                policy_key = f"{policy.namespace}/{policy.name}"
                self.network_policies[policy_key] = policy
                
                self.logger.info(f"✅ Created network policy: {policy.name}")
                return True
                
            except client.rest.ApiException as e:
                if e.status == 409:  # Already exists
                    self.logger.info(f"ℹ️ Network policy {policy.name} already exists")
                    return True
                else:
                    raise e
                    
        except Exception as e:
            self.logger.error(f"❌ Error creating network policy: {e}")
            return False
    
    async def _register_service(self, service_config: ServiceConfig) -> None:
        """Register service with service discovery"""
        try:
            # Register with Consul
            if self.consul_client:
                for port in service_config.ports:
                    service_id = f"{service_config.name}-{port.name}"
                    
                    self.consul_client.agent.service.register(
                        name=service_config.name,
                        service_id=service_id,
                        port=port.port,
                        tags=[
                            f"protocol:{port.protocol.value.lower()}",
                            f"namespace:{service_config.namespace}",
                            "ia-influencer"
                        ],
                        check=consul.Check.http(
                            f"http://{service_config.name}:{port.port}/health",
                            interval="30s",
                            timeout="10s"
                        )
                    )
                    
                    self.logger.debug(f"📝 Registered service {service_id} with Consul")
            
            # Register with etcd
            if self.etcd_client:
                service_key = f"/services/{service_config.namespace}/{service_config.name}"
                service_data = {
                    "name": service_config.name,
                    "namespace": service_config.namespace,
                    "ports": [asdict(port) for port in service_config.ports],
                    "selector": service_config.selector,
                    "service_type": service_config.service_type
                }
                
                self.etcd_client.put(service_key, json.dumps(service_data))
                self.logger.debug(f"📝 Registered service with etcd: {service_key}")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error registering service: {e}")
    
    async def _monitor_endpoints(self) -> None:
        """Monitor service endpoints"""
        while True:
            try:
                v1 = client.CoreV1Api()
                
                # Get all endpoints
                endpoints_list = v1.list_endpoint_for_all_namespaces()
                
                current_endpoints = {}
                
                for endpoint in endpoints_list.items:
                    endpoint_key = f"{endpoint.metadata.namespace}/{endpoint.metadata.name}"
                    
                    endpoint_info = {
                        "name": endpoint.metadata.name,
                        "namespace": endpoint.metadata.namespace,
                        "addresses": [],
                        "ports": []
                    }
                    
                    if endpoint.subsets:
                        for subset in endpoint.subsets:
                            if subset.addresses:
                                for address in subset.addresses:
                                    endpoint_info["addresses"].append({
                                        "ip": address.ip,
                                        "hostname": address.hostname,
                                        "target_ref": address.target_ref.name if address.target_ref else None
                                    })
                            
                            if subset.ports:
                                for port in subset.ports:
                                    endpoint_info["ports"].append({
                                        "name": port.name,
                                        "port": port.port,
                                        "protocol": port.protocol
                                    })
                    
                    current_endpoints[endpoint_key] = endpoint_info
                
                # Update endpoints
                self.endpoints = current_endpoints
                
                # Check for changes and update service discovery
                await self._update_service_discovery()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"❌ Error monitoring endpoints: {e}")
                await asyncio.sleep(60)
    
    async def _update_service_discovery(self) -> None:
        """Update service discovery with current endpoints"""
        try:
            for endpoint_key, endpoint_info in self.endpoints.items():
                service_name = endpoint_info["name"]
                namespace = endpoint_info["namespace"]
                
                # Update Consul
                if self.consul_client:
                    try:
                        for address in endpoint_info["addresses"]:
                            for port in endpoint_info["ports"]:
                                service_id = f"{service_name}-{address['ip']}-{port['port']}"
                                
                                self.consul_client.agent.service.register(
                                    name=service_name,
                                    service_id=service_id,
                                    address=address["ip"],
                                    port=port["port"],
                                    tags=[
                                        f"protocol:{port['protocol'].lower()}",
                                        f"namespace:{namespace}",
                                        "ia-influencer",
                                        "endpoint"
                                    ]
                                )
                    except Exception as e:
                        self.logger.warning(f"⚠️ Error updating Consul for {endpoint_key}: {e}")
                
                # Update etcd
                if self.etcd_client:
                    try:
                        endpoint_key_etcd = f"/endpoints/{namespace}/{service_name}"
                        self.etcd_client.put(endpoint_key_etcd, json.dumps(endpoint_info))
                    except Exception as e:
                        self.logger.warning(f"⚠️ Error updating etcd for {endpoint_key}: {e}")
                        
        except Exception as e:
            self.logger.error(f"❌ Error updating service discovery: {e}")
    
    async def _health_check_task(self) -> None:
        """Health check task for services"""
        while True:
            try:
                for service_key, service_config in self.services.items():
                    await self._check_service_health(service_config)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"❌ Error in health check task: {e}")
                await asyncio.sleep(60)
    
    async def _check_service_health(self, service_config: ServiceConfig) -> None:
        """Check health of a service"""
        try:
            endpoint_key = f"{service_config.namespace}/{service_config.name}"
            
            if endpoint_key not in self.endpoints:
                self.logger.warning(f"⚠️ No endpoints found for service {service_config.name}")
                return
            
            endpoint_info = self.endpoints[endpoint_key]
            healthy_addresses = []
            
            for address in endpoint_info["addresses"]:
                ip = address["ip"]
                
                # Check health for HTTP services
                for port in service_config.ports:
                    if port.protocol in [NetworkProtocol.HTTP, NetworkProtocol.HTTPS]:
                        health_url = f"http://{ip}:{port.port}/health"
                        
                        try:
                            import aiohttp
                            async with aiohttp.ClientSession() as session:
                                async with session.get(health_url, timeout=10) as response:
                                    if response.status == 200:
                                        healthy_addresses.append(address)
                                        break
                        except Exception:
                            continue
            
            # Update health status in service discovery
            if self.consul_client:
                try:
                    # Update health checks in Consul
                    for address in endpoint_info["addresses"]:
                        if address in healthy_addresses:
                            # Service is healthy
                            pass
                        else:
                            # Mark service as unhealthy
                            pass
                except Exception as e:
                    self.logger.warning(f"⚠️ Error updating health status in Consul: {e}")
                    
        except Exception as e:
            self.logger.error(f"❌ Error checking service health: {e}")
    
    async def setup_load_balancer(self, service_name: str, namespace: str, lb_config: LoadBalancerConfig) -> bool:
        """Setup load balancer for service"""
        try:
            # This would integrate with cloud provider LB or ingress controller
            # For now, we'll store the configuration
            
            lb_key = f"{namespace}/{service_name}"
            self.load_balancers[lb_key] = lb_config
            
            # Update service annotations for load balancer
            v1 = client.CoreV1Api()
            
            # Get existing service
            service = v1.read_namespaced_service(
                name=service_name,
                namespace=namespace
            )
            
            # Update annotations based on load balancer config
            if not service.metadata.annotations:
                service.metadata.annotations = {}
            
            service.metadata.annotations.update({
                "service.beta.kubernetes.io/aws-load-balancer-type": "nlb",
                "service.beta.kubernetes.io/aws-load-balancer-backend-protocol": "tcp",
                f"service.beta.kubernetes.io/aws-load-balancer-healthcheck-interval": str(lb_config.health_check_interval),
                f"service.beta.kubernetes.io/aws-load-balancer-healthcheck-timeout": str(lb_config.health_check_timeout),
                f"service.beta.kubernetes.io/aws-load-balancer-healthy-threshold": str(lb_config.health_check_retries)
            })
            
            if lb_config.sticky_sessions:
                service.metadata.annotations["service.beta.kubernetes.io/aws-load-balancer-backend-protocol"] = "http"
                service.metadata.annotations["service.beta.kubernetes.io/aws-load-balancer-ssl-negotiation-policy"] = "ELBSecurityPolicy-TLS-1-2-2017-01"
            
            # Update service
            v1.patch_namespaced_service(
                name=service_name,
                namespace=namespace,
                body=service
            )
            
            self.logger.info(f"✅ Setup load balancer for service: {service_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up load balancer: {e}")
            return False
    
    async def discover_services(self, namespace: str = None) -> List[Dict[str, Any]]:
        """Discover services in cluster"""
        try:
            v1 = client.CoreV1Api()
            
            if namespace:
                services_list = v1.list_namespaced_service(namespace=namespace)
            else:
                services_list = v1.list_service_for_all_namespaces()
            
            discovered_services = []
            
            for service in services_list.items:
                service_info = {
                    "name": service.metadata.name,
                    "namespace": service.metadata.namespace,
                    "type": service.spec.type,
                    "cluster_ip": service.spec.cluster_ip,
                    "external_ips": service.spec.external_i_ps or [],
                    "ports": [
                        {
                            "name": port.name,
                            "port": port.port,
                            "target_port": port.target_port,
                            "protocol": port.protocol,
                            "node_port": port.node_port
                        }
                        for port in service.spec.ports or []
                    ],
                    "selector": service.spec.selector or {},
                    "labels": service.metadata.labels or {},
                    "annotations": service.metadata.annotations or {}
                }
                
                discovered_services.append(service_info)
            
            return discovered_services
            
        except Exception as e:
            self.logger.error(f"❌ Error discovering services: {e}")
            return []
    
    async def get_service_topology(self, namespace: str = None) -> Dict[str, Any]:
        """Get service topology and dependencies"""
        try:
            services = await self.discover_services(namespace)
            
            topology = {
                "nodes": [],
                "edges": [],
                "clusters": {}
            }
            
            # Add services as nodes
            for service in services:
                node = {
                    "id": f"{service['namespace']}/{service['name']}",
                    "name": service["name"],
                    "namespace": service["namespace"],
                    "type": "service",
                    "metadata": {
                        "service_type": service["type"],
                        "ports": service["ports"],
                        "labels": service["labels"]
                    }
                }
                topology["nodes"].append(node)
                
                # Group by namespace
                if service["namespace"] not in topology["clusters"]:
                    topology["clusters"][service["namespace"]] = []
                topology["clusters"][service["namespace"]].append(node["id"])
            
            # Add endpoints as nodes and create edges
            for endpoint_key, endpoint_info in self.endpoints.items():
                for address in endpoint_info["addresses"]:
                    pod_id = f"{endpoint_info['namespace']}/{address.get('target_ref', address['ip'])}"
                    
                    pod_node = {
                        "id": pod_id,
                        "name": address.get("target_ref", address["ip"]),
                        "namespace": endpoint_info["namespace"],
                        "type": "pod",
                        "metadata": {
                            "ip": address["ip"],
                            "hostname": address.get("hostname")
                        }
                    }
                    topology["nodes"].append(pod_node)
                    
                    # Create edge from service to pod
                    service_id = f"{endpoint_info['namespace']}/{endpoint_info['name']}"
                    edge = {
                        "source": service_id,
                        "target": pod_id,
                        "type": "routes_to",
                        "metadata": {
                            "ports": endpoint_info["ports"]
                        }
                    }
                    topology["edges"].append(edge)
            
            return topology
            
        except Exception as e:
            self.logger.error(f"❌ Error getting service topology: {e}")
            return {"nodes": [], "edges": [], "clusters": {}}
    
    async def cleanup_networking(self, namespace: str) -> bool:
        """Cleanup networking resources in namespace"""
        try:
            v1 = client.CoreV1Api()
            networking_v1 = client.NetworkingV1Api()
            
            # Delete services
            services = v1.list_namespaced_service(namespace=namespace)
            for service in services.items:
                if service.metadata.labels and service.metadata.labels.get("app", "").startswith("ia-influencer"):
                    try:
                        v1.delete_namespaced_service(
                            name=service.metadata.name,
                            namespace=namespace
                        )
                        self.logger.info(f"🗑️ Deleted service: {service.metadata.name}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Error deleting service {service.metadata.name}: {e}")
            
            # Delete ingresses
            ingresses = networking_v1.list_namespaced_ingress(namespace=namespace)
            for ingress in ingresses.items:
                if ingress.metadata.labels and ingress.metadata.labels.get("app", "").startswith("ia-influencer"):
                    try:
                        networking_v1.delete_namespaced_ingress(
                            name=ingress.metadata.name,
                            namespace=namespace
                        )
                        self.logger.info(f"🗑️ Deleted ingress: {ingress.metadata.name}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Error deleting ingress {ingress.metadata.name}: {e}")
            
            # Delete network policies
            policies = networking_v1.list_namespaced_network_policy(namespace=namespace)
            for policy in policies.items:
                if policy.metadata.name.startswith("ia-influencer"):
                    try:
                        networking_v1.delete_namespaced_network_policy(
                            name=policy.metadata.name,
                            namespace=namespace
                        )
                        self.logger.info(f"🗑️ Deleted network policy: {policy.metadata.name}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Error deleting network policy {policy.metadata.name}: {e}")
            
            # Cleanup service discovery entries
            if self.consul_client:
                try:
                    # Get services in Consul
                    services = self.consul_client.agent.services()
                    for service_id, service_info in services.items():
                        if "ia-influencer" in service_info.get("tags", []):
                            self.consul_client.agent.service.deregister(service_id)
                            self.logger.info(f"🗑️ Deregistered service from Consul: {service_id}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Error cleaning up Consul services: {e}")
            
            if self.etcd_client:
                try:
                    # Delete service and endpoint entries
                    for key_prefix in [f"/services/{namespace}/", f"/endpoints/{namespace}/"]:
                        for key, _ in self.etcd_client.get_prefix(key_prefix):
                            self.etcd_client.delete(key)
                            self.logger.info(f"🗑️ Deleted etcd key: {key}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Error cleaning up etcd entries: {e}")
            
            self.logger.info(f"✅ Cleaned up networking resources in namespace: {namespace}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up networking: {e}")
            return False

class ServiceDiscoveryManager:
    """Service discovery manager for container networking"""
    
    def __init__(self, networking_manager: ContainerNetworkingManager):
        self.networking_manager = networking_manager
        self.service_registry = {}
        self.health_status = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def register_service(self, service_endpoint: ServiceEndpoint) -> bool:
        """Register service endpoint"""
        try:
            service_key = f"{service_endpoint.name}:{service_endpoint.port}"
            self.service_registry[service_key] = service_endpoint
            
            # Initialize health status
            self.health_status[service_key] = {
                "healthy": True,
                "last_check": datetime.now(),
                "consecutive_failures": 0
            }
            
            self.logger.info(f"✅ Registered service endpoint: {service_endpoint.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error registering service endpoint: {e}")
            return False
    
    async def discover_service(self, service_name: str) -> List[ServiceEndpoint]:
        """Discover service endpoints"""
        try:
            endpoints = []
            
            for service_key, endpoint in self.service_registry.items():
                if endpoint.name == service_name:
                    # Check if endpoint is healthy
                    if self.health_status[service_key]["healthy"]:
                        endpoints.append(endpoint)
            
            return endpoints
            
        except Exception as e:
            self.logger.error(f"❌ Error discovering service: {e}")
            return []
    
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get service health status"""
        try:
            health_info = {
                "service_name": service_name,
                "total_endpoints": 0,
                "healthy_endpoints": 0,
                "unhealthy_endpoints": 0,
                "endpoints": []
            }
            
            for service_key, endpoint in self.service_registry.items():
                if endpoint.name == service_name:
                    health_info["total_endpoints"] += 1
                    
                    endpoint_health = self.health_status[service_key]
                    
                    if endpoint_health["healthy"]:
                        health_info["healthy_endpoints"] += 1
                    else:
                        health_info["unhealthy_endpoints"] += 1
                    
                    health_info["endpoints"].append({
                        "ip": endpoint.ip,
                        "port": endpoint.port,
                        "healthy": endpoint_health["healthy"],
                        "last_check": endpoint_health["last_check"].isoformat(),
                        "consecutive_failures": endpoint_health["consecutive_failures"]
                    })
            
            return health_info
            
        except Exception as e:
            self.logger.error(f"❌ Error getting service health: {e}")
            return {}

__all__ = [
    "ContainerNetworkingManager",
    "ServiceDiscoveryManager",
    "ServiceConfig",
    "IngressConfig",
    "NetworkPolicy",
    "ServiceMeshConfig",
    "LoadBalancerConfig",
    "ServiceEndpoint",
    "NetworkPort",
    "IngressRule",
    "NetworkProtocol",
    "LoadBalancerType",
    "ServiceMeshType",
    "NetworkPolicyAction"
]
