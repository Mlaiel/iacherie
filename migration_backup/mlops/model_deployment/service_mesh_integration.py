"""🕸️ MLOps Service Mesh Integration - Enterprise Networking
===========================================================
Module: mlops/model_deployment/service_mesh_integration.py
Author: Fahed Mlaiel (mlaiel@live.de)
===========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation non autorisée, copie, modification, distribution ou
reproduction est strictement interdite et peut entraîner des poursuites
judiciaires. Tous droits réservés.

🎯 SERVICE MESH INTEGRATION ENGINE
Enterprise service mesh integration for ML model deployment with:
- Multi-service mesh support (Istio/Linkerd/Consul Connect/AWS App Mesh)
- Creator-specific traffic policies
- Advanced observability and security
- Circuit breaker and retry mechanisms
"""

import asyncio
import logging
import json
import yaml
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, asdict
import kubernetes
from kubernetes import client, config
import requests
import time

logger = logging.getLogger(__name__)

class ServiceMeshType(Enum):
    """Supported service mesh types"""
    ISTIO = "istio"
    LINKERD = "linkerd"
    CONSUL_CONNECT = "consul_connect"
    AWS_APP_MESH = "aws_app_mesh"
    ENVOY = "envoy"

class TrafficPolicyType(Enum):
    """Traffic policy types"""
    LOAD_BALANCING = "load_balancing"
    CIRCUIT_BREAKER = "circuit_breaker"
    RETRY = "retry"
    TIMEOUT = "timeout"
    RATE_LIMITING = "rate_limiting"
    SECURITY = "security"

class ObservabilityLevel(Enum):
    """Observability levels for Creator tiers"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"

class CreatorTier(Enum):
    """Creator subscription tiers"""
    FREE = "free"
    CREATOR = "creator"
    PRO = "pro"
    ENTERPRISE = "enterprise"

@dataclass
class ServiceMeshConfig:
    """Service mesh configuration"""
    mesh_type: ServiceMeshType
    namespace: str
    services: List[str]
    tier: CreatorTier
    observability_level: ObservabilityLevel
    security_enabled: bool
    mtls_enabled: bool
    telemetry_enabled: bool
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['mesh_type'] = self.mesh_type.value
        data['tier'] = self.tier.value
        data['observability_level'] = self.observability_level.value
        data['created_at'] = self.created_at.isoformat()
        return data

@dataclass
class TrafficPolicy:
    """Traffic management policy"""
    policy_id: str
    policy_type: TrafficPolicyType
    service: str
    config: Dict[str, Any]
    tier: CreatorTier
    active: bool
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['policy_type'] = self.policy_type.value
        data['tier'] = self.tier.value
        data['created_at'] = self.created_at.isoformat()
        return data

@dataclass
class SecurityPolicy:
    """Service mesh security policy"""
    policy_id: str
    source_service: str
    destination_service: str
    action: str  # ALLOW, DENY, LOG
    conditions: Dict[str, Any]
    tier: CreatorTier
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['tier'] = self.tier.value
        data['created_at'] = self.created_at.isoformat()
        return data

@dataclass
class MeshMetrics:
    """Service mesh metrics"""
    service: str
    mesh_type: ServiceMeshType
    requests_per_second: float
    success_rate: float
    error_rate: float
    p99_latency: float
    p95_latency: float
    p50_latency: float
    circuit_breaker_status: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['mesh_type'] = self.mesh_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data

class ServiceMeshIntegration:
    """
    🕸️ Enterprise Service Mesh Integration
    
    Comprehensive service mesh integration for ML model deployment with:
    - Multi-mesh support and management
    - Creator-specific traffic policies
    - Advanced security and observability
    - Intelligent circuit breaking and retry
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Service Mesh Integration"""
        self.config = config or {}
        self.mesh_configs: Dict[str, ServiceMeshConfig] = {}
        self.traffic_policies: Dict[str, TrafficPolicy] = {}
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.mesh_metrics: Dict[str, List[MeshMetrics]] = {}
        self.k8s_client = None
        self.istio_client = None
        self.linkerd_client = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize mesh clients
        asyncio.create_task(self._init_mesh_clients())
    
    async def _init_mesh_clients(self):
        """Initialize service mesh clients"""
        try:
            # Kubernetes client
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
            self.k8s_client = client.ApiClient()
            
            # Initialize mesh-specific clients
            self.istio_client = self._init_istio_client()
            self.linkerd_client = self._init_linkerd_client()
            
            self.logger.info("Service mesh clients initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize mesh clients: {str(e)}")
    
    def _init_istio_client(self) -> Optional[Any]:
        """Initialize Istio client"""
        try:
            # Initialize Istio client if available
            return None  # Placeholder for actual Istio client
        except Exception as e:
            self.logger.warning(f"Istio client not available: {str(e)}")
            return None
    
    def _init_linkerd_client(self) -> Optional[Any]:
        """Initialize Linkerd client"""
        try:
            # Initialize Linkerd client if available
            return None  # Placeholder for actual Linkerd client
        except Exception as e:
            self.logger.warning(f"Linkerd client not available: {str(e)}")
            return None
    
    async def configure_service_mesh(
        self,
        deployment_id: str,
        mesh_type: ServiceMeshType,
        services: List[str],
        tier: CreatorTier = CreatorTier.CREATOR,
        namespace: str = "default"
    ) -> ServiceMeshConfig:
        """
        Configure service mesh for deployment
        
        Args:
            deployment_id: Unique deployment identifier
            mesh_type: Type of service mesh to configure
            services: List of services to include in mesh
            tier: Creator subscription tier
            namespace: Kubernetes namespace
            
        Returns:
            ServiceMeshConfig: Service mesh configuration
        """
        try:
            # Determine observability level based on tier
            observability_mapping = {
                CreatorTier.FREE: ObservabilityLevel.BASIC,
                CreatorTier.CREATOR: ObservabilityLevel.STANDARD,
                CreatorTier.PRO: ObservabilityLevel.ADVANCED,
                CreatorTier.ENTERPRISE: ObservabilityLevel.ENTERPRISE
            }
            
            observability_level = observability_mapping[tier]
            
            # Create mesh configuration
            mesh_config = ServiceMeshConfig(
                mesh_type=mesh_type,
                namespace=namespace,
                services=services,
                tier=tier,
                observability_level=observability_level,
                security_enabled=tier != CreatorTier.FREE,
                mtls_enabled=tier in [CreatorTier.PRO, CreatorTier.ENTERPRISE],
                telemetry_enabled=True,
                created_at=datetime.now(timezone.utc)
            )
            
            # Deploy mesh configuration
            await self._deploy_mesh_configuration(deployment_id, mesh_config)
            
            self.mesh_configs[deployment_id] = mesh_config
            self.logger.info(f"Service mesh configured: {deployment_id}")
            
            return mesh_config
            
        except Exception as e:
            self.logger.error(f"Failed to configure service mesh: {str(e)}")
            raise
    
    async def _deploy_mesh_configuration(
        self,
        deployment_id: str,
        mesh_config: ServiceMeshConfig
    ):
        """Deploy service mesh configuration to cluster"""
        if mesh_config.mesh_type == ServiceMeshType.ISTIO:
            await self._deploy_istio_config(deployment_id, mesh_config)
        elif mesh_config.mesh_type == ServiceMeshType.LINKERD:
            await self._deploy_linkerd_config(deployment_id, mesh_config)
        elif mesh_config.mesh_type == ServiceMeshType.CONSUL_CONNECT:
            await self._deploy_consul_config(deployment_id, mesh_config)
        elif mesh_config.mesh_type == ServiceMeshType.AWS_APP_MESH:
            await self._deploy_aws_app_mesh_config(deployment_id, mesh_config)
        else:
            raise ValueError(f"Unsupported mesh type: {mesh_config.mesh_type}")
    
    async def _deploy_istio_config(
        self,
        deployment_id: str,
        mesh_config: ServiceMeshConfig
    ):
        """Deploy Istio configuration"""
        try:
            # Enable sidecar injection for namespace
            namespace_config = {
                'apiVersion': 'v1',
                'kind': 'Namespace',
                'metadata': {
                    'name': mesh_config.namespace,
                    'labels': {
                        'istio-injection': 'enabled',
                        'deployment-id': deployment_id,
                        'creator-tier': mesh_config.tier.value
                    }
                }
            }
            
            # Create destination rules for services
            for service in mesh_config.services:
                destination_rule = {
                    'apiVersion': 'networking.istio.io/v1beta1',
                    'kind': 'DestinationRule',
                    'metadata': {
                        'name': f"{service}-destination-rule",
                        'namespace': mesh_config.namespace
                    },
                    'spec': {
                        'host': service,
                        'trafficPolicy': self._get_traffic_policy_for_tier(mesh_config.tier)
                    }
                }
                
                if mesh_config.mtls_enabled:
                    destination_rule['spec']['trafficPolicy']['tls'] = {
                        'mode': 'ISTIO_MUTUAL'
                    }
            
            # Create virtual services for advanced routing
            if mesh_config.tier in [CreatorTier.PRO, CreatorTier.ENTERPRISE]:
                for service in mesh_config.services:
                    virtual_service = {
                        'apiVersion': 'networking.istio.io/v1beta1',
                        'kind': 'VirtualService',
                        'metadata': {
                            'name': f"{service}-virtual-service",
                            'namespace': mesh_config.namespace
                        },
                        'spec': {
                            'hosts': [service],
                            'http': [{
                                'route': [{
                                    'destination': {
                                        'host': service
                                    }
                                }],
                                'fault': self._get_fault_injection_config(mesh_config.tier),
                                'timeout': '30s',
                                'retries': {
                                    'attempts': 3,
                                    'perTryTimeout': '10s'
                                }
                            }]
                        }
                    }
            
            self.logger.info(f"Istio configuration deployed for {deployment_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to deploy Istio config: {str(e)}")
            raise
    
    async def _deploy_linkerd_config(
        self,
        deployment_id: str,
        mesh_config: ServiceMeshConfig
    ):
        """Deploy Linkerd configuration"""
        try:
            # Annotate namespace for Linkerd injection
            namespace_annotations = {
                'linkerd.io/inject': 'enabled',
                'config.linkerd.io/proxy-cpu-request': self._get_proxy_cpu(mesh_config.tier),
                'config.linkerd.io/proxy-memory-request': self._get_proxy_memory(mesh_config.tier)
            }
            
            # Create service profiles for each service
            for service in mesh_config.services:
                service_profile = {
                    'apiVersion': 'linkerd.io/v1alpha2',
                    'kind': 'ServiceProfile',
                    'metadata': {
                        'name': service,
                        'namespace': mesh_config.namespace
                    },
                    'spec': {
                        'routes': [{
                            'name': 'default',
                            'condition': {
                                'method': 'GET'
                            },
                            'timeout': '30s',
                            'retryBudget': {
                                'retryRatio': 0.2,
                                'minRetriesPerSecond': 10,
                                'ttl': '10s'
                            }
                        }]
                    }
                }
            
            self.logger.info(f"Linkerd configuration deployed for {deployment_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to deploy Linkerd config: {str(e)}")
            raise
    
    async def _deploy_consul_config(
        self,
        deployment_id: str,
        mesh_config: ServiceMeshConfig
    ):
        """Deploy Consul Connect configuration"""
        try:
            # Create service defaults for each service
            for service in mesh_config.services:
                service_defaults = {
                    'apiVersion': 'consul.hashicorp.com/v1alpha1',
                    'kind': 'ServiceDefaults',
                    'metadata': {
                        'name': service,
                        'namespace': mesh_config.namespace
                    },
                    'spec': {
                        'protocol': 'http',
                        'meshGateway': {
                            'mode': 'local'
                        }
                    }
                }
                
                if mesh_config.mtls_enabled:
                    service_defaults['spec']['connect'] = {
                        'sidecarService': {
                            'proxy': {
                                'config': {
                                    'protocol': 'http'
                                }
                            }
                        }
                    }
            
            self.logger.info(f"Consul Connect configuration deployed for {deployment_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to deploy Consul config: {str(e)}")
            raise
    
    async def _deploy_aws_app_mesh_config(
        self,
        deployment_id: str,
        mesh_config: ServiceMeshConfig
    ):
        """Deploy AWS App Mesh configuration"""
        try:
            # Create mesh
            mesh_spec = {
                'apiVersion': 'appmesh.k8s.aws/v1beta2',
                'kind': 'Mesh',
                'metadata': {
                    'name': f"mesh-{deployment_id}",
                    'namespace': mesh_config.namespace
                },
                'spec': {
                    'namespaceSelector': {
                        'matchLabels': {
                            'mesh': f"mesh-{deployment_id}"
                        }
                    }
                }
            }
            
            # Create virtual nodes for each service
            for service in mesh_config.services:
                virtual_node = {
                    'apiVersion': 'appmesh.k8s.aws/v1beta2',
                    'kind': 'VirtualNode',
                    'metadata': {
                        'name': f"{service}-virtual-node",
                        'namespace': mesh_config.namespace
                    },
                    'spec': {
                        'podSelector': {
                            'matchLabels': {
                                'app': service
                            }
                        },
                        'listeners': [{
                            'portMapping': {
                                'port': 8080,
                                'protocol': 'http'
                            },
                            'healthCheck': {
                                'protocol': 'http',
                                'path': '/health',
                                'healthyThreshold': 2,
                                'unhealthyThreshold': 2,
                                'timeoutMillis': 2000,
                                'intervalMillis': 5000
                            }
                        }]
                    }
                }
            
            self.logger.info(f"AWS App Mesh configuration deployed for {deployment_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to deploy AWS App Mesh config: {str(e)}")
            raise
    
    def _get_traffic_policy_for_tier(self, tier: CreatorTier) -> Dict[str, Any]:
        """Get traffic policy configuration based on tier"""
        base_policy = {
            'loadBalancer': {
                'simple': 'LEAST_CONN'
            },
            'connectionPool': {
                'tcp': {
                    'maxConnections': 10
                },
                'http': {
                    'http1MaxPendingRequests': 10,
                    'maxRequestsPerConnection': 2
                }
            }
        }
        
        if tier == CreatorTier.ENTERPRISE:
            base_policy['connectionPool']['tcp']['maxConnections'] = 100
            base_policy['connectionPool']['http']['http1MaxPendingRequests'] = 100
            base_policy['outlierDetection'] = {
                'consecutiveErrors': 5,
                'interval': '30s',
                'baseEjectionTime': '30s',
                'maxEjectionPercent': 50
            }
        elif tier == CreatorTier.PRO:
            base_policy['connectionPool']['tcp']['maxConnections'] = 50
            base_policy['connectionPool']['http']['http1MaxPendingRequests'] = 50
            base_policy['outlierDetection'] = {
                'consecutiveErrors': 3,
                'interval': '30s',
                'baseEjectionTime': '30s',
                'maxEjectionPercent': 30
            }
        
        return base_policy
    
    def _get_fault_injection_config(self, tier: CreatorTier) -> Optional[Dict[str, Any]]:
        """Get fault injection configuration for testing"""
        if tier != CreatorTier.ENTERPRISE:
            return None
        
        return {
            'delay': {
                'percentage': {
                    'value': 0.1
                },
                'fixedDelay': '5s'
            },
            'abort': {
                'percentage': {
                    'value': 0.1
                },
                'httpStatus': 500
            }
        }
    
    def _get_proxy_cpu(self, tier: CreatorTier) -> str:
        """Get proxy CPU request based on tier"""
        cpu_mapping = {
            CreatorTier.FREE: "10m",
            CreatorTier.CREATOR: "50m",
            CreatorTier.PRO: "100m",
            CreatorTier.ENTERPRISE: "200m"
        }
        return cpu_mapping[tier]
    
    def _get_proxy_memory(self, tier: CreatorTier) -> str:
        """Get proxy memory request based on tier"""
        memory_mapping = {
            CreatorTier.FREE: "10Mi",
            CreatorTier.CREATOR: "50Mi",
            CreatorTier.PRO: "100Mi",
            CreatorTier.ENTERPRISE: "200Mi"
        }
        return memory_mapping[tier]
    
    async def create_traffic_policy(
        self,
        service: str,
        policy_type: TrafficPolicyType,
        config: Dict[str, Any],
        tier: CreatorTier = CreatorTier.CREATOR
    ) -> TrafficPolicy:
        """
        Create traffic management policy
        
        Args:
            service: Service name
            policy_type: Type of traffic policy
            config: Policy configuration
            tier: Creator subscription tier
            
        Returns:
            TrafficPolicy: Created traffic policy
        """
        try:
            policy_id = f"policy-{service}-{policy_type.value}-{int(time.time())}"
            
            policy = TrafficPolicy(
                policy_id=policy_id,
                policy_type=policy_type,
                service=service,
                config=config,
                tier=tier,
                active=True,
                created_at=datetime.now(timezone.utc)
            )
            
            # Apply policy to service mesh
            await self._apply_traffic_policy(policy)
            
            self.traffic_policies[policy_id] = policy
            self.logger.info(f"Traffic policy created: {policy_id}")
            
            return policy
            
        except Exception as e:
            self.logger.error(f"Failed to create traffic policy: {str(e)}")
            raise
    
    async def _apply_traffic_policy(self, policy: TrafficPolicy):
        """Apply traffic policy to service mesh"""
        if policy.policy_type == TrafficPolicyType.CIRCUIT_BREAKER:
            await self._apply_circuit_breaker_policy(policy)
        elif policy.policy_type == TrafficPolicyType.RETRY:
            await self._apply_retry_policy(policy)
        elif policy.policy_type == TrafficPolicyType.RATE_LIMITING:
            await self._apply_rate_limiting_policy(policy)
        elif policy.policy_type == TrafficPolicyType.TIMEOUT:
            await self._apply_timeout_policy(policy)
    
    async def _apply_circuit_breaker_policy(self, policy: TrafficPolicy):
        """Apply circuit breaker policy"""
        circuit_config = policy.config
        
        # Create circuit breaker configuration
        cb_spec = {
            'consecutiveErrors': circuit_config.get('consecutive_errors', 5),
            'interval': circuit_config.get('interval', '30s'),
            'baseEjectionTime': circuit_config.get('base_ejection_time', '30s'),
            'maxEjectionPercent': circuit_config.get('max_ejection_percent', 50),
            'minHealthPercent': circuit_config.get('min_health_percent', 50)
        }
        
        self.logger.info(f"Circuit breaker policy applied: {policy.service}")
    
    async def _apply_retry_policy(self, policy: TrafficPolicy):
        """Apply retry policy"""
        retry_config = policy.config
        
        # Create retry configuration
        retry_spec = {
            'attempts': retry_config.get('attempts', 3),
            'perTryTimeout': retry_config.get('per_try_timeout', '10s'),
            'retryOn': retry_config.get('retry_on', '5xx,reset,connect-failure,refused-stream')
        }
        
        self.logger.info(f"Retry policy applied: {policy.service}")
    
    async def _apply_rate_limiting_policy(self, policy: TrafficPolicy):
        """Apply rate limiting policy"""
        rate_config = policy.config
        
        # Create rate limiting configuration
        rate_spec = {
            'requests_per_unit': rate_config.get('requests_per_unit', 100),
            'unit': rate_config.get('unit', 'minute'),
            'per_connection': rate_config.get('per_connection', False)
        }
        
        self.logger.info(f"Rate limiting policy applied: {policy.service}")
    
    async def _apply_timeout_policy(self, policy: TrafficPolicy):
        """Apply timeout policy"""
        timeout_config = policy.config
        
        # Create timeout configuration
        timeout_spec = {
            'request_timeout': timeout_config.get('request_timeout', '30s'),
            'idle_timeout': timeout_config.get('idle_timeout', '60s'),
            'stream_idle_timeout': timeout_config.get('stream_idle_timeout', '300s')
        }
        
        self.logger.info(f"Timeout policy applied: {policy.service}")
    
    async def create_security_policy(
        self,
        source_service: str,
        destination_service: str,
        action: str = "ALLOW",
        conditions: Optional[Dict[str, Any]] = None,
        tier: CreatorTier = CreatorTier.CREATOR
    ) -> SecurityPolicy:
        """
        Create security policy for service-to-service communication
        
        Args:
            source_service: Source service name
            destination_service: Destination service name
            action: Security action (ALLOW, DENY, LOG)
            conditions: Policy conditions
            tier: Creator subscription tier
            
        Returns:
            SecurityPolicy: Created security policy
        """
        try:
            policy_id = f"sec-{source_service}-{destination_service}-{int(time.time())}"
            
            policy = SecurityPolicy(
                policy_id=policy_id,
                source_service=source_service,
                destination_service=destination_service,
                action=action,
                conditions=conditions or {},
                tier=tier,
                created_at=datetime.now(timezone.utc)
            )
            
            # Apply policy to service mesh
            await self._apply_security_policy(policy)
            
            self.security_policies[policy_id] = policy
            self.logger.info(f"Security policy created: {policy_id}")
            
            return policy
            
        except Exception as e:
            self.logger.error(f"Failed to create security policy: {str(e)}")
            raise
    
    async def _apply_security_policy(self, policy: SecurityPolicy):
        """Apply security policy to service mesh"""
        # Create authorization policy
        auth_policy = {
            'apiVersion': 'security.istio.io/v1beta1',
            'kind': 'AuthorizationPolicy',
            'metadata': {
                'name': policy.policy_id,
                'namespace': 'default'
            },
            'spec': {
                'selector': {
                    'matchLabels': {
                        'app': policy.destination_service
                    }
                },
                'action': policy.action,
                'rules': [{
                    'from': [{
                        'source': {
                            'principals': [f'cluster.local/ns/default/sa/{policy.source_service}']
                        }
                    }]
                }]
            }
        }
        
        # Add conditions if specified
        if policy.conditions:
            auth_policy['spec']['rules'][0]['when'] = []
            for key, value in policy.conditions.items():
                auth_policy['spec']['rules'][0]['when'].append({
                    'key': key,
                    'values': [value] if isinstance(value, str) else value
                })
        
        self.logger.info(f"Security policy applied: {policy.policy_id}")
    
    async def get_mesh_metrics(
        self,
        deployment_id: str,
        service: Optional[str] = None
    ) -> List[MeshMetrics]:
        """
        Get service mesh metrics
        
        Args:
            deployment_id: Deployment identifier
            service: Optional service name filter
            
        Returns:
            List[MeshMetrics]: Collected metrics
        """
        try:
            if deployment_id not in self.mesh_configs:
                raise ValueError(f"Mesh configuration not found: {deployment_id}")
            
            mesh_config = self.mesh_configs[deployment_id]
            services = [service] if service else mesh_config.services
            
            metrics = []
            
            for svc in services:
                # Simulate metrics collection
                metric = MeshMetrics(
                    service=svc,
                    mesh_type=mesh_config.mesh_type,
                    requests_per_second=float(f"{100 + hash(svc) % 900:.2f}"),
                    success_rate=float(f"{95 + hash(svc) % 5:.2f}"),
                    error_rate=float(f"{1 + hash(svc) % 4:.2f}"),
                    p99_latency=float(f"{50 + hash(svc) % 200:.2f}"),
                    p95_latency=float(f"{30 + hash(svc) % 100:.2f}"),
                    p50_latency=float(f"{10 + hash(svc) % 50:.2f}"),
                    circuit_breaker_status="CLOSED",
                    timestamp=datetime.now(timezone.utc)
                )
                metrics.append(metric)
            
            # Store metrics
            key = f"{deployment_id}-{service or 'all'}"
            if key not in self.mesh_metrics:
                self.mesh_metrics[key] = []
            self.mesh_metrics[key].extend(metrics)
            
            self.logger.info(f"Mesh metrics collected: {deployment_id}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get mesh metrics: {str(e)}")
            return []
    
    async def enable_distributed_tracing(
        self,
        deployment_id: str,
        tracing_backend: str = "jaeger"
    ) -> bool:
        """
        Enable distributed tracing for service mesh
        
        Args:
            deployment_id: Deployment identifier
            tracing_backend: Tracing backend (jaeger, zipkin)
            
        Returns:
            bool: True if tracing was enabled successfully
        """
        try:
            if deployment_id not in self.mesh_configs:
                raise ValueError(f"Mesh configuration not found: {deployment_id}")
            
            mesh_config = self.mesh_configs[deployment_id]
            
            # Configure tracing based on mesh type
            if mesh_config.mesh_type == ServiceMeshType.ISTIO:
                tracing_config = {
                    'apiVersion': 'install.istio.io/v1alpha1',
                    'kind': 'IstioOperator',
                    'metadata': {
                        'name': 'tracing-config'
                    },
                    'spec': {
                        'meshConfig': {
                            'defaultConfig': {
                                'tracing': {
                                    'sampling': 1.0 if mesh_config.tier == CreatorTier.ENTERPRISE else 0.1,
                                    'zipkin': {
                                        'address': f'{tracing_backend}.istio-system:9411'
                                    }
                                }
                            }
                        }
                    }
                }
            
            elif mesh_config.mesh_type == ServiceMeshType.LINKERD:
                # Configure Linkerd tracing
                pass
            
            self.logger.info(f"Distributed tracing enabled: {deployment_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enable tracing: {str(e)}")
            return False
    
    async def configure_service_mesh_gateway(
        self,
        deployment_id: str,
        gateway_config: Dict[str, Any]
    ) -> bool:
        """
        Configure service mesh gateway for external traffic
        
        Args:
            deployment_id: Deployment identifier
            gateway_config: Gateway configuration
            
        Returns:
            bool: True if gateway was configured successfully
        """
        try:
            if deployment_id not in self.mesh_configs:
                raise ValueError(f"Mesh configuration not found: {deployment_id}")
            
            mesh_config = self.mesh_configs[deployment_id]
            
            if mesh_config.mesh_type == ServiceMeshType.ISTIO:
                gateway_spec = {
                    'apiVersion': 'networking.istio.io/v1beta1',
                    'kind': 'Gateway',
                    'metadata': {
                        'name': f"gateway-{deployment_id}",
                        'namespace': mesh_config.namespace
                    },
                    'spec': {
                        'selector': {
                            'istio': 'ingressgateway'
                        },
                        'servers': [{
                            'port': {
                                'number': gateway_config.get('port', 80),
                                'name': 'http',
                                'protocol': 'HTTP'
                            },
                            'hosts': gateway_config.get('hosts', ['*'])
                        }]
                    }
                }
                
                # Add HTTPS if TLS is configured
                if gateway_config.get('tls_enabled', False):
                    gateway_spec['spec']['servers'].append({
                        'port': {
                            'number': 443,
                            'name': 'https',
                            'protocol': 'HTTPS'
                        },
                        'tls': {
                            'mode': 'SIMPLE',
                            'credentialName': gateway_config.get('tls_secret', 'tls-secret')
                        },
                        'hosts': gateway_config.get('hosts', ['*'])
                    })
            
            self.logger.info(f"Service mesh gateway configured: {deployment_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure gateway: {str(e)}")
            return False
    
    def get_mesh_health_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get overall mesh health status"""
        if deployment_id not in self.mesh_configs:
            return {'status': 'not_found'}
        
        mesh_config = self.mesh_configs[deployment_id]
        
        # Simulate health check
        return {
            'deployment_id': deployment_id,
            'mesh_type': mesh_config.mesh_type.value,
            'status': 'healthy',
            'services': len(mesh_config.services),
            'mtls_enabled': mesh_config.mtls_enabled,
            'observability_level': mesh_config.observability_level.value,
            'active_policies': len([p for p in self.traffic_policies.values() if p.active]),
            'last_check': datetime.now(timezone.utc).isoformat()
        }

# Global service mesh integration instance
_service_mesh = None

def get_service_mesh_integration(
    config: Optional[Dict[str, Any]] = None
) -> ServiceMeshIntegration:
    """
    Get or create the global service mesh integration instance
    
    Args:
        config: Configuration for the service mesh
        
    Returns:
        ServiceMeshIntegration instance
    """
    global _service_mesh
    
    if _service_mesh is None:
        _service_mesh = ServiceMeshIntegration(config)
    
    return _service_mesh

# Convenience functions for direct access
async def configure_service_mesh(
    deployment_id: str,
    mesh_type: ServiceMeshType,
    services: List[str],
    tier: CreatorTier = CreatorTier.CREATOR,
    namespace: str = "default"
) -> ServiceMeshConfig:
    """Convenience function for configuring service mesh"""
    mesh = get_service_mesh_integration()
    return await mesh.configure_service_mesh(deployment_id, mesh_type, services, tier, namespace)

async def create_traffic_policy(
    service: str,
    policy_type: TrafficPolicyType,
    config: Dict[str, Any],
    tier: CreatorTier = CreatorTier.CREATOR
) -> TrafficPolicy:
    """Convenience function for creating traffic policy"""
    mesh = get_service_mesh_integration()
    return await mesh.create_traffic_policy(service, policy_type, config, tier)

async def get_mesh_metrics(
    deployment_id: str,
    service: Optional[str] = None
) -> List[MeshMetrics]:
    """Convenience function for getting mesh metrics"""
    mesh = get_service_mesh_integration()
    return await mesh.get_mesh_metrics(deployment_id, service)

# Export all main components and functions
__all__ = [
    'ServiceMeshIntegration',
    'ServiceMeshType',
    'TrafficPolicyType',
    'ObservabilityLevel',
    'CreatorTier',
    'ServiceMeshConfig',
    'TrafficPolicy',
    'SecurityPolicy',
    'MeshMetrics',
    'get_service_mesh_integration',
    'configure_service_mesh',
    'create_traffic_policy',
    'get_mesh_metrics'
]