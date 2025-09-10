# Ainflue Infrastructure Module - Service Mesh Configuration
# ==========================================================
# 
# Enterprise-grade service mesh configuration for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Service Mesh Configuration - Enterprise Service Communication

Provides comprehensive service mesh capabilities including:
- Service discovery and registration
- Load balancing and traffic routing
- Security policies and mTLS
- Observability and monitoring
- Circuit breaker and fault tolerance
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import yaml
import json
import hashlib
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceMeshProvider(Enum):
    """Service mesh provider enumeration"""
    ISTIO = "istio"
    LINKERD = "linkerd"
    CONSUL_CONNECT = "consul-connect"
    AWS_APP_MESH = "aws-app-mesh"
    AZURE_SERVICE_MESH = "azure-service-mesh"
    GCP_TRAFFIC_DIRECTOR = "gcp-traffic-director"

class TrafficPolicy(Enum):
    """Traffic routing policy enumeration"""
    ROUND_ROBIN = "round_robin"
    LEAST_REQUEST = "least_request"
    RANDOM = "random"
    WEIGHTED = "weighted"
    HASH = "hash"

class SecurityMode(Enum):
    """Security mode enumeration"""
    STRICT = "strict"
    PERMISSIVE = "permissive"
    DISABLED = "disabled"

@dataclass
class ServiceConfig:
    """Service configuration dataclass"""
    name: str
    namespace: str = "default"
    version: str = "v1"
    port: int = 80
    protocol: str = "HTTP"
    endpoints: List[str] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    health_check_path: str = "/health"
    metrics_path: str = "/metrics"

@dataclass
class TrafficRouting:
    """Traffic routing configuration"""
    source_service: str
    destination_service: str
    weight: int = 100
    headers: Dict[str, str] = field(default_factory=dict)
    match_criteria: Dict[str, Any] = field(default_factory=dict)
    fault_injection: Optional[Dict[str, Any]] = None
    timeout: Optional[str] = None
    retries: Optional[Dict[str, Any]] = None

@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    name: str
    namespace: str = "default"
    source_principals: List[str] = field(default_factory=list)
    destination_ports: List[int] = field(default_factory=list)
    allowed_methods: List[str] = field(default_factory=list)
    jwt_rules: List[Dict[str, Any]] = field(default_factory=list)
    mtls_mode: SecurityMode = SecurityMode.STRICT

class ServiceMeshConfigurator:
    """
    Enterprise Service Mesh Configurator
    
    Manages service mesh configuration, traffic routing, and security policies
    across multi-cloud environments for the Ainflue platform.
    """
    
    def __init__(self, provider: ServiceMeshProvider = ServiceMeshProvider.ISTIO):
        """Initialize service mesh configurator"""
        self.provider = provider
        self.services: Dict[str, ServiceConfig] = {}
        self.traffic_routes: List[TrafficRouting] = []
        self.security_policies: List[SecurityPolicy] = []
        self.mesh_config: Dict[str, Any] = {}
        
        # Enterprise configuration
        self.default_timeout = "30s"
        self.default_retries = {"attempts": 3, "per_try_timeout": "10s"}
        self.mtls_enabled = True
        self.observability_enabled = True
        
        # Initialize mesh configuration
        self._initialize_mesh_config()
    
    def _initialize_mesh_config(self) -> None:
        """Initialize service mesh configuration"""
        try:
            self.mesh_config = {
                "provider": self.provider.value,
                "global_settings": {
                    "mtls": {
                        "auto": self.mtls_enabled,
                        "mode": SecurityMode.STRICT.value
                    },
                    "tracing": {
                        "enabled": self.observability_enabled,
                        "sampling": 1.0,
                        "jaeger_endpoint": "http://jaeger-collector:14268/api/traces"
                    },
                    "metrics": {
                        "enabled": self.observability_enabled,
                        "prometheus_endpoint": "http://prometheus:9090"
                    },
                    "access_logs": {
                        "enabled": True,
                        "format": "json"
                    }
                },
                "circuit_breaker": {
                    "consecutive_errors": 5,
                    "interval": "30s",
                    "base_ejection_time": "30s",
                    "max_ejection_percent": 50
                },
                "rate_limiting": {
                    "enabled": True,
                    "requests_per_unit": 1000,
                    "unit": "minute"
                }
            }
            
            logger.info(f"Service mesh configured with provider: {self.provider.value}")
            
        except Exception as e:
            logger.error(f"Failed to initialize mesh config: {e}")
            raise
    
    def register_service(self, service_config: ServiceConfig) -> bool:
        """Register a service in the mesh"""
        try:
            service_key = f"{service_config.namespace}/{service_config.name}"
            self.services[service_key] = service_config
            
            # Generate service mesh manifests
            manifests = self._generate_service_manifests(service_config)
            
            # Save manifests to file
            self._save_manifests(service_config.name, manifests)
            
            logger.info(f"Service registered: {service_config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {service_config.name}: {e}")
            return False
    
    def _generate_service_manifests(self, config: ServiceConfig) -> Dict[str, Any]:
        """Generate service mesh manifests"""
        manifests = {}
        
        if self.provider == ServiceMeshProvider.ISTIO:
            manifests.update(self._generate_istio_manifests(config))
        elif self.provider == ServiceMeshProvider.LINKERD:
            manifests.update(self._generate_linkerd_manifests(config))
        elif self.provider == ServiceMeshProvider.CONSUL_CONNECT:
            manifests.update(self._generate_consul_manifests(config))
        
        return manifests
    
    def _generate_istio_manifests(self, config: ServiceConfig) -> Dict[str, Any]:
        """Generate Istio service mesh manifests"""
        # Virtual Service
        virtual_service = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": config.name,
                "namespace": config.namespace,
                "labels": config.labels
            },
            "spec": {
                "hosts": [config.name],
                "http": [{
                    "route": [{
                        "destination": {
                            "host": config.name,
                            "subset": config.version
                        }
                    }],
                    "timeout": self.default_timeout,
                    "retries": self.default_retries
                }]
            }
        }
        
        # Destination Rule
        destination_rule = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "DestinationRule",
            "metadata": {
                "name": config.name,
                "namespace": config.namespace
            },
            "spec": {
                "host": config.name,
                "trafficPolicy": {
                    "loadBalancer": {
                        "simple": TrafficPolicy.ROUND_ROBIN.value.upper()
                    },
                    "circuitBreaker": {
                        "consecutiveErrors": self.mesh_config["circuit_breaker"]["consecutive_errors"],
                        "interval": self.mesh_config["circuit_breaker"]["interval"],
                        "baseEjectionTime": self.mesh_config["circuit_breaker"]["base_ejection_time"],
                        "maxEjectionPercent": self.mesh_config["circuit_breaker"]["max_ejection_percent"]
                    }
                },
                "subsets": [{
                    "name": config.version,
                    "labels": {"version": config.version}
                }]
            }
        }
        
        # Service Entry for external services
        service_entry = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "ServiceEntry",
            "metadata": {
                "name": f"{config.name}-external",
                "namespace": config.namespace
            },
            "spec": {
                "hosts": config.endpoints,
                "ports": [{
                    "number": config.port,
                    "name": config.protocol.lower(),
                    "protocol": config.protocol
                }],
                "location": "MESH_EXTERNAL",
                "resolution": "DNS"
            }
        } if config.endpoints else None
        
        manifests = {
            "virtual_service": virtual_service,
            "destination_rule": destination_rule
        }
        
        if service_entry:
            manifests["service_entry"] = service_entry
        
        return manifests
    
    def _generate_linkerd_manifests(self, config: ServiceConfig) -> Dict[str, Any]:
        """Generate Linkerd service mesh manifests"""
        # Traffic Split
        traffic_split = {
            "apiVersion": "split.smi-spec.io/v1alpha1",
            "kind": "TrafficSplit",
            "metadata": {
                "name": config.name,
                "namespace": config.namespace
            },
            "spec": {
                "service": config.name,
                "backends": [{
                    "service": f"{config.name}-{config.version}",
                    "weight": 100
                }]
            }
        }
        
        # Traffic Target
        traffic_target = {
            "apiVersion": "access.smi-spec.io/v1alpha1",
            "kind": "TrafficTarget",
            "metadata": {
                "name": f"{config.name}-target",
                "namespace": config.namespace
            },
            "spec": {
                "destination": {
                    "kind": "ServiceAccount",
                    "name": config.name,
                    "namespace": config.namespace
                },
                "rules": [{
                    "kind": "HTTPRouteGroup",
                    "name": f"{config.name}-routes",
                    "matches": ["GET", "POST", "PUT", "DELETE"]
                }],
                "sources": [{
                    "kind": "ServiceAccount",
                    "name": "default",
                    "namespace": config.namespace
                }]
            }
        }
        
        return {
            "traffic_split": traffic_split,
            "traffic_target": traffic_target
        }
    
    def _generate_consul_manifests(self, config: ServiceConfig) -> Dict[str, Any]:
        """Generate Consul Connect manifests"""
        # Service Defaults
        service_defaults = {
            "apiVersion": "consul.hashicorp.com/v1alpha1",
            "kind": "ServiceDefaults",
            "metadata": {
                "name": config.name,
                "namespace": config.namespace
            },
            "spec": {
                "protocol": config.protocol.lower(),
                "connect": {
                    "sidecarService": {
                        "proxy": {
                            "config": {
                                "envoy_prometheus_bind_addr": "0.0.0.0:9102"
                            }
                        }
                    }
                }
            }
        }
        
        # Service Resolver
        service_resolver = {
            "apiVersion": "consul.hashicorp.com/v1alpha1",
            "kind": "ServiceResolver",
            "metadata": {
                "name": config.name,
                "namespace": config.namespace
            },
            "spec": {
                "defaultSubset": config.version,
                "subsets": {
                    config.version: {
                        "filter": f"Service.Meta.version == {config.version}"
                    }
                },
                "connectTimeout": self.default_timeout,
                "requestTimeout": self.default_timeout
            }
        }
        
        return {
            "service_defaults": service_defaults,
            "service_resolver": service_resolver
        }
    
    def configure_traffic_routing(self, routing: TrafficRouting) -> bool:
        """Configure traffic routing between services"""
        try:
            self.traffic_routes.append(routing)
            
            # Generate routing manifests
            routing_manifests = self._generate_routing_manifests(routing)
            
            # Save routing manifests
            route_name = f"{routing.source_service}-to-{routing.destination_service}"
            self._save_manifests(f"route-{route_name}", routing_manifests)
            
            logger.info(f"Traffic routing configured: {route_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure traffic routing: {e}")
            return False
    
    def _generate_routing_manifests(self, routing: TrafficRouting) -> Dict[str, Any]:
        """Generate traffic routing manifests"""
        if self.provider == ServiceMeshProvider.ISTIO:
            return self._generate_istio_routing(routing)
        elif self.provider == ServiceMeshProvider.LINKERD:
            return self._generate_linkerd_routing(routing)
        elif self.provider == ServiceMeshProvider.CONSUL_CONNECT:
            return self._generate_consul_routing(routing)
        
        return {}
    
    def _generate_istio_routing(self, routing: TrafficRouting) -> Dict[str, Any]:
        """Generate Istio traffic routing"""
        virtual_service = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": f"{routing.source_service}-routing",
                "namespace": "default"
            },
            "spec": {
                "hosts": [routing.destination_service],
                "http": [{
                    "match": [routing.match_criteria] if routing.match_criteria else [],
                    "headers": routing.headers,
                    "route": [{
                        "destination": {
                            "host": routing.destination_service
                        },
                        "weight": routing.weight
                    }],
                    "timeout": routing.timeout or self.default_timeout,
                    "retries": routing.retries or self.default_retries,
                    "fault": routing.fault_injection
                }]
            }
        }
        
        return {"virtual_service": virtual_service}
    
    def _generate_linkerd_routing(self, routing: TrafficRouting) -> Dict[str, Any]:
        """Generate Linkerd traffic routing"""
        traffic_split = {
            "apiVersion": "split.smi-spec.io/v1alpha1",
            "kind": "TrafficSplit",
            "metadata": {
                "name": f"{routing.source_service}-split",
                "namespace": "default"
            },
            "spec": {
                "service": routing.destination_service,
                "backends": [{
                    "service": routing.destination_service,
                    "weight": routing.weight
                }]
            }
        }
        
        return {"traffic_split": traffic_split}
    
    def _generate_consul_routing(self, routing: TrafficRouting) -> Dict[str, Any]:
        """Generate Consul Connect routing"""
        service_splitter = {
            "apiVersion": "consul.hashicorp.com/v1alpha1",
            "kind": "ServiceSplitter",
            "metadata": {
                "name": routing.destination_service,
                "namespace": "default"
            },
            "spec": {
                "splits": [{
                    "weight": routing.weight / 100.0,
                    "service": routing.destination_service
                }]
            }
        }
        
        return {"service_splitter": service_splitter}
    
    def configure_security_policy(self, policy: SecurityPolicy) -> bool:
        """Configure security policies"""
        try:
            self.security_policies.append(policy)
            
            # Generate security manifests
            security_manifests = self._generate_security_manifests(policy)
            
            # Save security manifests
            self._save_manifests(f"policy-{policy.name}", security_manifests)
            
            logger.info(f"Security policy configured: {policy.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure security policy {policy.name}: {e}")
            return False
    
    def _generate_security_manifests(self, policy: SecurityPolicy) -> Dict[str, Any]:
        """Generate security policy manifests"""
        if self.provider == ServiceMeshProvider.ISTIO:
            return self._generate_istio_security(policy)
        elif self.provider == ServiceMeshProvider.LINKERD:
            return self._generate_linkerd_security(policy)
        elif self.provider == ServiceMeshProvider.CONSUL_CONNECT:
            return self._generate_consul_security(policy)
        
        return {}
    
    def _generate_istio_security(self, policy: SecurityPolicy) -> Dict[str, Any]:
        """Generate Istio security policies"""
        # PeerAuthentication
        peer_auth = {
            "apiVersion": "security.istio.io/v1beta1",
            "kind": "PeerAuthentication",
            "metadata": {
                "name": policy.name,
                "namespace": policy.namespace
            },
            "spec": {
                "mtls": {
                    "mode": policy.mtls_mode.value.upper()
                }
            }
        }
        
        # AuthorizationPolicy
        auth_policy = {
            "apiVersion": "security.istio.io/v1beta1",
            "kind": "AuthorizationPolicy",
            "metadata": {
                "name": f"{policy.name}-authz",
                "namespace": policy.namespace
            },
            "spec": {
                "rules": [{
                    "from": [{
                        "source": {
                            "principals": policy.source_principals
                        }
                    }],
                    "to": [{
                        "operation": {
                            "methods": policy.allowed_methods,
                            "ports": [str(p) for p in policy.destination_ports]
                        }
                    }]
                }]
            }
        }
        
        # RequestAuthentication for JWT
        jwt_auth = {
            "apiVersion": "security.istio.io/v1beta1",
            "kind": "RequestAuthentication",
            "metadata": {
                "name": f"{policy.name}-jwt",
                "namespace": policy.namespace
            },
            "spec": {
                "jwtRules": policy.jwt_rules
            }
        } if policy.jwt_rules else None
        
        manifests = {
            "peer_authentication": peer_auth,
            "authorization_policy": auth_policy
        }
        
        if jwt_auth:
            manifests["request_authentication"] = jwt_auth
        
        return manifests
    
    def _generate_linkerd_security(self, policy: SecurityPolicy) -> Dict[str, Any]:
        """Generate Linkerd security policies"""
        # Server
        server = {
            "apiVersion": "policy.linkerd.io/v1beta1",
            "kind": "Server",
            "metadata": {
                "name": policy.name,
                "namespace": policy.namespace
            },
            "spec": {
                "podSelector": {
                    "matchLabels": {"app": policy.name}
                },
                "port": policy.destination_ports[0] if policy.destination_ports else 80,
                "proxyProtocol": "HTTP/2"
            }
        }
        
        # ServerAuthorization
        server_authz = {
            "apiVersion": "policy.linkerd.io/v1beta1",
            "kind": "ServerAuthorization",
            "metadata": {
                "name": f"{policy.name}-authz",
                "namespace": policy.namespace
            },
            "spec": {
                "server": {
                    "name": policy.name
                },
                "client": {
                    "serviceAccount": {
                        "name": "default"
                    }
                }
            }
        }
        
        return {
            "server": server,
            "server_authorization": server_authz
        }
    
    def _generate_consul_security(self, policy: SecurityPolicy) -> Dict[str, Any]:
        """Generate Consul Connect security policies"""
        # ServiceIntentions
        service_intentions = {
            "apiVersion": "consul.hashicorp.com/v1alpha1",
            "kind": "ServiceIntentions",
            "metadata": {
                "name": policy.name,
                "namespace": policy.namespace
            },
            "spec": {
                "destination": {
                    "name": policy.name,
                    "namespace": policy.namespace
                },
                "sources": [{
                    "name": principal.split("/")[-1],
                    "action": "allow"
                } for principal in policy.source_principals]
            }
        }
        
        return {"service_intentions": service_intentions}
    
    def _save_manifests(self, name: str, manifests: Dict[str, Any]) -> None:
        """Save manifests to files"""
        try:
            # Create output directory
            output_dir = Path(f"/home/runner/work/Ainflue/Ainflue/infra/kubernetes/manifests/{self.provider.value}")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            for manifest_type, manifest in manifests.items():
                if manifest:
                    filename = output_dir / f"{name}-{manifest_type}.yaml"
                    with open(filename, 'w') as f:
                        yaml.dump(manifest, f, default_flow_style=False)
            
            logger.info(f"Manifests saved for {name}")
            
        except Exception as e:
            logger.error(f"Failed to save manifests for {name}: {e}")
    
    def enable_observability(self, namespace: str = "default") -> Dict[str, Any]:
        """Enable observability features"""
        try:
            observability_config = {
                "tracing": {
                    "enabled": True,
                    "sampling_rate": 1.0,
                    "jaeger_endpoint": "http://jaeger-collector.istio-system:14268/api/traces"
                },
                "metrics": {
                    "enabled": True,
                    "prometheus_endpoint": "http://prometheus.istio-system:9090",
                    "scrape_interval": "15s"
                },
                "access_logs": {
                    "enabled": True,
                    "format": "json",
                    "providers": ["envoy"]
                }
            }
            
            # Generate observability manifests
            observability_manifests = self._generate_observability_manifests(observability_config, namespace)
            
            # Save observability manifests
            self._save_manifests("observability", observability_manifests)
            
            logger.info("Observability features enabled")
            return observability_config
            
        except Exception as e:
            logger.error(f"Failed to enable observability: {e}")
            return {}
    
    def _generate_observability_manifests(self, config: Dict[str, Any], namespace: str) -> Dict[str, Any]:
        """Generate observability manifests"""
        manifests = {}
        
        if self.provider == ServiceMeshProvider.ISTIO:
            # Telemetry v2 configuration
            telemetry = {
                "apiVersion": "telemetry.istio.io/v1alpha1",
                "kind": "Telemetry",
                "metadata": {
                    "name": "default",
                    "namespace": namespace
                },
                "spec": {
                    "tracing": [{
                        "providers": [{
                            "name": "jaeger"
                        }]
                    }],
                    "metrics": [{
                        "providers": [{
                            "name": "prometheus"
                        }]
                    }],
                    "accessLogging": [{
                        "providers": [{
                            "name": "envoy"
                        }]
                    }]
                }
            }
            manifests["telemetry"] = telemetry
        
        return manifests
    
    def get_mesh_status(self) -> Dict[str, Any]:
        """Get service mesh status"""
        return {
            "provider": self.provider.value,
            "services_registered": len(self.services),
            "traffic_routes": len(self.traffic_routes),
            "security_policies": len(self.security_policies),
            "mtls_enabled": self.mtls_enabled,
            "observability_enabled": self.observability_enabled,
            "mesh_config": self.mesh_config
        }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate service mesh configuration"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Validate services
            for service_key, service in self.services.items():
                if not service.name:
                    validation_results["errors"].append(f"Service {service_key} missing name")
                    validation_results["valid"] = False
                
                if not service.endpoints and service.protocol.upper() != "HTTP":
                    validation_results["warnings"].append(f"Service {service.name} has no endpoints defined")
            
            # Validate traffic routes
            for route in self.traffic_routes:
                source_key = f"default/{route.source_service}"
                dest_key = f"default/{route.destination_service}"
                
                if source_key not in self.services:
                    validation_results["warnings"].append(f"Source service {route.source_service} not registered")
                
                if dest_key not in self.services:
                    validation_results["errors"].append(f"Destination service {route.destination_service} not registered")
                    validation_results["valid"] = False
            
            # Validate security policies
            for policy in self.security_policies:
                if not policy.source_principals and policy.mtls_mode != SecurityMode.DISABLED:
                    validation_results["warnings"].append(f"Security policy {policy.name} has no source principals defined")
            
            logger.info(f"Configuration validation completed. Valid: {validation_results['valid']}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Failed to validate configuration: {e}")
            validation_results["valid"] = False
            validation_results["errors"].append(str(e))
            return validation_results

# Enterprise Service Mesh Configurator instance
service_mesh = ServiceMeshConfigurator()

# Export for use in other modules
__all__ = [
    "ServiceMeshConfigurator",
    "ServiceConfig",
    "TrafficRouting", 
    "SecurityPolicy",
    "ServiceMeshProvider",
    "TrafficPolicy",
    "SecurityMode",
    "service_mesh"
]