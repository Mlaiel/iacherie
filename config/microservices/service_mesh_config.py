"""Service Mesh Configuration for IA-Influencer Agent Platform
===========================================================

Professional service mesh configuration for microservices communication.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseSettings, Field, validator
import yaml


class ServiceMeshType(str, Enum):
    """Service mesh implementation types."""    ISTIO = "istio"
    LINKERD = "linkerd"
    CONSUL_CONNECT = "consul_connect"
    AWS_APP_MESH = "aws_app_mesh"
    NGINX_SERVICE_MESH = "nginx_service_mesh"


class TrafficPolicyType(str, Enum):
    """Traffic policy types."""    ROUND_ROBIN = "round_robin"
    LEAST_CONN = "least_conn"
    RANDOM = "random"
    PASSTHROUGH = "passthrough"


class SecurityMode(str, Enum):
    """Security modes for service communication."""    PERMISSIVE = "permissive"
    STRICT = "strict"
    DISABLE = "disable"


@dataclass
class ServiceMeshService:
    """Service configuration for service mesh."""    name: str
    namespace: str = "default"
    version: str = "v1"
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    ports: List[Dict[str, Any]] = field(default_factory=list)
    health_check_path: str = "/health"
    metrics_path: str = "/metrics"
    
    def to_kubernetes_service(self) -> Dict[str, Any]:
        """Convert to Kubernetes service manifest."""        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace,
                "labels": {
                    "app": self.name,
                    "version": self.version,
                    **self.labels
                },
                "annotations": self.annotations
            },
            "spec": {
                "selector": {
                    "app": self.name
                },
                "ports": self.ports
            }
        }


@dataclass
class VirtualService:
    """Virtual service configuration for traffic routing."""    name: str
    namespace: str = "default"
    hosts: List[str] = field(default_factory=list)
    gateways: List[str] = field(default_factory=list)
    http_routes: List[Dict[str, Any]] = field(default_factory=list)
    tcp_routes: List[Dict[str, Any]] = field(default_factory=list)
    tls_routes: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_istio_virtual_service(self) -> Dict[str, Any]:
        """Convert to Istio VirtualService manifest."""        spec = {
            "hosts": self.hosts
        }
        
        if self.gateways:
            spec["gateways"] = self.gateways
        
        if self.http_routes:
            spec["http"] = self.http_routes
        
        if self.tcp_routes:
            spec["tcp"] = self.tcp_routes
        
        if self.tls_routes:
            spec["tls"] = self.tls_routes
        
        return {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace
            },
            "spec": spec
        }


@dataclass
class DestinationRule:
    """Destination rule configuration for traffic policies."""    name: str
    host: str
    namespace: str = "default"
    traffic_policy: Optional[Dict[str, Any]] = None
    subsets: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_istio_destination_rule(self) -> Dict[str, Any]:
        """Convert to Istio DestinationRule manifest."""        spec = {
            "host": self.host
        }
        
        if self.traffic_policy:
            spec["trafficPolicy"] = self.traffic_policy
        
        if self.subsets:
            spec["subsets"] = self.subsets
        
        return {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "DestinationRule",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace
            },
            "spec": spec
        }


@dataclass
class Gateway:
    """Gateway configuration for ingress traffic."""    name: str
    namespace: str = "default"
    selector: Dict[str, str] = field(default_factory=dict)
    servers: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_istio_gateway(self) -> Dict[str, Any]:
        """Convert to Istio Gateway manifest."""        return {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "Gateway",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace
            },
            "spec": {
                "selector": self.selector,
                "servers": self.servers
            }
        }


@dataclass
class PeerAuthentication:
    """Peer authentication configuration for mTLS."""    name: str
    namespace: str = "default"
    selector: Optional[Dict[str, str]] = None
    mtls_mode: SecurityMode = SecurityMode.STRICT
    port_level_mtls: Dict[int, SecurityMode] = field(default_factory=dict)
    
    def to_istio_peer_authentication(self) -> Dict[str, Any]:
        """Convert to Istio PeerAuthentication manifest."""        spec = {
            "mtls": {
                "mode": self.mtls_mode.value.upper()
            }
        }
        
        if self.selector:
            spec["selector"] = {"matchLabels": self.selector}
        
        if self.port_level_mtls:
            spec["portLevelMtls"] = {
                str(port): {"mode": mode.value.upper()}
                for port, mode in self.port_level_mtls.items()
            }
        
        return {
            "apiVersion": "security.istio.io/v1beta1",
            "kind": "PeerAuthentication",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace
            },
            "spec": spec
        }


@dataclass
class AuthorizationPolicy:
    """Authorization policy configuration for access control."""    name: str
    namespace: str = "default"
    selector: Optional[Dict[str, str]] = None
    action: str = "ALLOW"  # ALLOW, DENY, AUDIT, CUSTOM
    rules: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_istio_authorization_policy(self) -> Dict[str, Any]:
        """Convert to Istio AuthorizationPolicy manifest."""        spec = {
            "action": self.action,
            "rules": self.rules
        }
        
        if self.selector:
            spec["selector"] = {"matchLabels": self.selector}
        
        return {
            "apiVersion": "security.istio.io/v1beta1",
            "kind": "AuthorizationPolicy",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace
            },
            "spec": spec
        }


class ServiceMeshConfig(BaseSettings):
    """    Centralized service mesh configuration for microservices architecture.
    Supports Istio, Linkerd, Consul Connect, and AWS App Mesh.
    """    
    # Service mesh type
    mesh_type: ServiceMeshType = Field(ServiceMeshType.ISTIO, env="SERVICE_MESH_TYPE")
    
    # Global settings
    enabled: bool = Field(True, env="SERVICE_MESH_ENABLED")
    namespace: str = Field("ia-influencer", env="SERVICE_MESH_NAMESPACE")
    cluster_domain: str = Field("cluster.local", env="SERVICE_MESH_CLUSTER_DOMAIN")
    
    # Istio configuration
    istio_namespace: str = Field("istio-system", env="ISTIO_NAMESPACE")
    istio_gateway_name: str = Field("ia-influencer-gateway", env="ISTIO_GATEWAY_NAME")
    istio_ingress_gateway: str = Field("istio-ingressgateway", env="ISTIO_INGRESS_GATEWAY")
    
    # Traffic management
    default_traffic_policy: TrafficPolicyType = Field(
        TrafficPolicyType.ROUND_ROBIN, 
        env="SERVICE_MESH_DEFAULT_TRAFFIC_POLICY"
    )
    
    # Security settings
    mtls_mode: SecurityMode = Field(SecurityMode.STRICT, env="SERVICE_MESH_MTLS_MODE")
    enable_authorization: bool = Field(True, env="SERVICE_MESH_ENABLE_AUTHORIZATION")
    enable_peer_authentication: bool = Field(True, env="SERVICE_MESH_ENABLE_PEER_AUTH")
    
    # Observability
    enable_tracing: bool = Field(True, env="SERVICE_MESH_ENABLE_TRACING")
    enable_metrics: bool = Field(True, env="SERVICE_MESH_ENABLE_METRICS")
    enable_access_logs: bool = Field(True, env="SERVICE_MESH_ENABLE_ACCESS_LOGS")
    tracing_sampling_rate: float = Field(1.0, env="SERVICE_MESH_TRACING_SAMPLING_RATE")
    
    # Circuit breaker settings
    enable_circuit_breaker: bool = Field(True, env="SERVICE_MESH_ENABLE_CIRCUIT_BREAKER")
    circuit_breaker_consecutive_errors: int = Field(5, env="SERVICE_MESH_CB_CONSECUTIVE_ERRORS")
    circuit_breaker_interval: str = Field("30s", env="SERVICE_MESH_CB_INTERVAL")
    circuit_breaker_base_ejection_time: str = Field("30s", env="SERVICE_MESH_CB_BASE_EJECTION_TIME")
    
    # Retry settings
    enable_retries: bool = Field(True, env="SERVICE_MESH_ENABLE_RETRIES")
    retry_attempts: int = Field(3, env="SERVICE_MESH_RETRY_ATTEMPTS")
    retry_timeout: str = Field("5s", env="SERVICE_MESH_RETRY_TIMEOUT")
    
    # Timeout settings
    default_timeout: str = Field("30s", env="SERVICE_MESH_DEFAULT_TIMEOUT")
    connect_timeout: str = Field("10s", env="SERVICE_MESH_CONNECT_TIMEOUT")
    
    # Load balancing
    enable_load_balancing: bool = Field(True, env="SERVICE_MESH_ENABLE_LOAD_BALANCING")
    load_balancer_simple: TrafficPolicyType = Field(
        TrafficPolicyType.ROUND_ROBIN, 
        env="SERVICE_MESH_LOAD_BALANCER_SIMPLE"
    )
    
    # TLS settings
    enable_tls: bool = Field(True, env="SERVICE_MESH_ENABLE_TLS")
    tls_cert_path: Optional[str] = Field(None, env="SERVICE_MESH_TLS_CERT_PATH")
    tls_key_path: Optional[str] = Field(None, env="SERVICE_MESH_TLS_KEY_PATH")
    tls_ca_cert_path: Optional[str] = Field(None, env="SERVICE_MESH_TLS_CA_CERT_PATH")
    
    # Rate limiting
    enable_rate_limiting: bool = Field(True, env="SERVICE_MESH_ENABLE_RATE_LIMITING")
    rate_limit_requests_per_minute: int = Field(1000, env="SERVICE_MESH_RATE_LIMIT_RPM")
    
    # Fault injection (for testing)
    enable_fault_injection: bool = Field(False, env="SERVICE_MESH_ENABLE_FAULT_INJECTION")
    fault_delay_percentage: float = Field(0.1, env="SERVICE_MESH_FAULT_DELAY_PERCENTAGE")
    fault_abort_percentage: float = Field(0.1, env="SERVICE_MESH_FAULT_ABORT_PERCENTAGE")
    
    class Config:
        env_prefix = "SERVICE_MESH_"
        case_sensitive = False
    
    def get_default_traffic_policy(self) -> Dict[str, Any]:
        """Get default traffic policy configuration."""        policy = {
            "loadBalancer": {
                "simple": self.load_balancer_simple.value.upper()
            },
            "connectionPool": {
                "tcp": {
                    "connectTimeout": self.connect_timeout
                },
                "http": {
                    "http1MaxPendingRequests": 100,
                    "http2MaxRequests": 1000,
                    "maxRequestsPerConnection": 10,
                    "maxRetries": self.retry_attempts
                }
            }
        }
        
        if self.enable_circuit_breaker:
            policy["outlierDetection"] = {
                "consecutiveErrors": self.circuit_breaker_consecutive_errors,
                "interval": self.circuit_breaker_interval,
                "baseEjectionTime": self.circuit_breaker_base_ejection_time,
                "maxEjectionPercent": 50
            }
        
        return policy
    
    def get_default_retry_policy(self) -> Dict[str, Any]:
        """Get default retry policy configuration."""        if not self.enable_retries:
            return {}
        
        return {
            "attempts": self.retry_attempts,
            "perTryTimeout": self.retry_timeout,
            "retryOn": "gateway-error,connect-failure,refused-stream"
        }
    
    def get_mesh_config(self) -> Dict[str, Any]:
        """Get complete service mesh configuration."""        return {
            "mesh_type": self.mesh_type,
            "enabled": self.enabled,
            "namespace": self.namespace,
            "cluster_domain": self.cluster_domain,
            "traffic": {
                "default_policy": self.default_traffic_policy,
                "timeout": self.default_timeout,
                "retry_policy": self.get_default_retry_policy(),
                "load_balancing": self.enable_load_balancing
            },
            "security": {
                "mtls_mode": self.mtls_mode,
                "enable_authorization": self.enable_authorization,
                "enable_peer_authentication": self.enable_peer_authentication,
                "tls_enabled": self.enable_tls
            },
            "observability": {
                "tracing": self.enable_tracing,
                "metrics": self.enable_metrics,
                "access_logs": self.enable_access_logs,
                "sampling_rate": self.tracing_sampling_rate
            },
            "resilience": {
                "circuit_breaker": self.enable_circuit_breaker,
                "retries": self.enable_retries,
                "rate_limiting": self.enable_rate_limiting
            }
        }


# Pre-configured services for IA-Influencer Agent microservices
MICROSERVICE_MESH_SERVICES = {
    "api-gateway": ServiceMeshService(
        name="api-gateway",
        namespace="ia-influencer",
        version="v1",
        labels={"tier": "gateway", "component": "api"},
        ports=[
            {"name": "http", "port": 8000, "targetPort": 8000, "protocol": "TCP"},
            {"name": "https", "port": 8443, "targetPort": 8443, "protocol": "TCP"}
        ]
    ),
    "spotify-agent": ServiceMeshService(
        name="spotify-agent",
        namespace="ia-influencer",
        version="v1",
        labels={"tier": "backend", "component": "ai"},
        ports=[
            {"name": "http", "port": 8001, "targetPort": 8001, "protocol": "TCP"}
        ]
    ),
    "content-protection": ServiceMeshService(
        name="content-protection",
        namespace="ia-influencer",
        version="v1",
        labels={"tier": "backend", "component": "protection"},
        ports=[
            {"name": "http", "port": 8002, "targetPort": 8002, "protocol": "TCP"}
        ]
    ),
    "fingerprinting-engine": ServiceMeshService(
        name="fingerprinting-engine",
        namespace="ia-influencer",
        version="v1",
        labels={"tier": "backend", "component": "ai"},
        ports=[
            {"name": "http", "port": 8003, "targetPort": 8003, "protocol": "TCP"}
        ]
    ),
    "web-crawler": ServiceMeshService(
        name="web-crawler",
        namespace="ia-influencer",
        version="v1",
        labels={"tier": "backend", "component": "crawler"},
        ports=[
            {"name": "http", "port": 8004, "targetPort": 8004, "protocol": "TCP"}
        ]
    ),
    "monetization-engine": ServiceMeshService(
        name="monetization-engine",
        namespace="ia-influencer",
        version="v1",
        labels={"tier": "backend", "component": "monetization"},
        ports=[
            {"name": "http", "port": 8005, "targetPort": 8005, "protocol": "TCP"}
        ]
    ),
    "notification-service": ServiceMeshService(
        name="notification-service",
        namespace="ia-influencer",
        version="v1",
        labels={"tier": "backend", "component": "notification"},
        ports=[
            {"name": "http", "port": 8006, "targetPort": 8006, "protocol": "TCP"},
            {"name": "websocket", "port": 8007, "targetPort": 8007, "protocol": "TCP"}
        ]
    ),
    "analytics-engine": ServiceMeshService(
        name="analytics-engine",
        namespace="ia-influencer",
        version="v1",
        labels={"tier": "backend", "component": "analytics"},
        ports=[
            {"name": "http", "port": 8008, "targetPort": 8008, "protocol": "TCP"}
        ]
    )
}

# Pre-configured virtual services for routing
MICROSERVICE_VIRTUAL_SERVICES = {
    "api-gateway": VirtualService(
        name="api-gateway",
        namespace="ia-influencer",
        hosts=["api.ia-influencer.com", "api-gateway"],
        gateways=["ia-influencer-gateway", "mesh"],
        http_routes=[
            {
                "match": [{"uri": {"prefix": "/api/v1/"}}],
                "route": [{"destination": {"host": "api-gateway", "port": {"number": 8000}}}],
                "timeout": "30s",
                "retries": {
                    "attempts": 3,
                    "perTryTimeout": "10s",
                    "retryOn": "gateway-error,connect-failure,refused-stream"
                }
            }
        ]
    ),
    "spotify-agent": VirtualService(
        name="spotify-agent",
        namespace="ia-influencer",
        hosts=["spotify-agent"],
        http_routes=[
            {
                "match": [{"headers": {"x-service": {"exact": "spotify-agent"}}}],
                "route": [{"destination": {"host": "spotify-agent", "port": {"number": 8001}}}],
                "timeout": "60s"
            }
        ]
    ),
    "content-protection": VirtualService(
        name="content-protection",
        namespace="ia-influencer",
        hosts=["content-protection"],
        http_routes=[
            {
                "match": [{"headers": {"x-service": {"exact": "content-protection"}}}],
                "route": [{"destination": {"host": "content-protection", "port": {"number": 8002}}}],
                "timeout": "120s"
            }
        ]
    )
}

# Pre-configured destination rules for traffic policies
MICROSERVICE_DESTINATION_RULES = {
    "api-gateway": DestinationRule(
        name="api-gateway",
        host="api-gateway",
        namespace="ia-influencer",
        traffic_policy={
            "loadBalancer": {"simple": "ROUND_ROBIN"},
            "connectionPool": {
                "tcp": {"connectTimeout": "10s"},
                "http": {
                    "http1MaxPendingRequests": 100,
                    "http2MaxRequests": 1000,
                    "maxRequestsPerConnection": 10
                }
            },
            "outlierDetection": {
                "consecutiveErrors": 3,
                "interval": "30s",
                "baseEjectionTime": "30s",
                "maxEjectionPercent": 50
            }
        }
    ),
    "fingerprinting-engine": DestinationRule(
        name="fingerprinting-engine",
        host="fingerprinting-engine",
        namespace="ia-influencer",
        traffic_policy={
            "loadBalancer": {"simple": "LEAST_CONN"},
            "connectionPool": {
                "tcp": {"connectTimeout": "30s"},
                "http": {
                    "http1MaxPendingRequests": 50,
                    "http2MaxRequests": 100,
                    "maxRequestsPerConnection": 5
                }
            },
            "outlierDetection": {
                "consecutiveErrors": 10,
                "interval": "60s",
                "baseEjectionTime": "120s",
                "maxEjectionPercent": 30
            }
        }
    )
}

# Main gateway configuration
MAIN_GATEWAY = Gateway(
    name="ia-influencer-gateway",
    namespace="ia-influencer",
    selector={"istio": "ingressgateway"},
    servers=[
        {
            "port": {"number": 80, "name": "http", "protocol": "HTTP"},
            "hosts": ["api.ia-influencer.com", "*"],
            "tls": {"httpsRedirect": True}
        },
        {
            "port": {"number": 443, "name": "https", "protocol": "HTTPS"},
            "hosts": ["api.ia-influencer.com", "*"],
            "tls": {
                "mode": "SIMPLE",
                "credentialName": "ia-influencer-tls-cert"
            }
        }
    ]
)

# Namespace-wide peer authentication
NAMESPACE_PEER_AUTHENTICATION = PeerAuthentication(
    name="default",
    namespace="ia-influencer",
    mtls_mode=SecurityMode.STRICT
)

# Default authorization policy (allow all)
DEFAULT_AUTHORIZATION_POLICY = AuthorizationPolicy(
    name="default-allow",
    namespace="ia-influencer",
    action="ALLOW",
    rules=[{}]  # Allow all traffic by default
)

# Export configuration instance
service_mesh_config = ServiceMeshConfig()
