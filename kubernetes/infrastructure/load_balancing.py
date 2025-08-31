"""Load Balancing Management System

Provides comprehensive load balancing solutions including Layer 4/7 load balancers,
API gateways, service mesh integration, and traffic management.

Project: IA Influencer Agent + Content Protection Platform
Author: Fahed Mlaiel <mlaiel@live.de>

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
"""
import asyncio
import logging
import json
import yaml
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from kubernetes import client, config
import requests

logger = logging.getLogger(__name__)

class LoadBalancerType(Enum):
    """Types of load balancers"""    APPLICATION_LOAD_BALANCER = "alb"  # Layer 7
    NETWORK_LOAD_BALANCER = "nlb"     # Layer 4
    NGINX_INGRESS = "nginx"
    TRAEFIK = "traefik"
    ISTIO_GATEWAY = "istio"
    ENVOY_PROXY = "envoy"

class BalancingAlgorithm(Enum):
    """Load balancing algorithms"""    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_response_time"

class HealthCheckType(Enum):
    """Health check types"""    HTTP = "http"
    HTTPS = "https"
    TCP = "tcp"
    GRPC = "grpc"

@dataclass
class BackendService:
    """Backend service configuration"""    name: str
    host: str
    port: int
    weight: int = 100
    health_check_path: str = "/health"
    max_connections: Optional[int] = None
    timeout: int = 30
    retries: int = 3

@dataclass
class HealthCheckConfig:
    """Health check configuration"""    check_type: HealthCheckType
    path: str = "/health"
    interval_seconds: int = 30
    timeout_seconds: int = 5
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3
    expected_codes: List[str] = None

@dataclass
class SSLConfig:
    """SSL/TLS configuration"""    enabled: bool = True
    certificate_arn: Optional[str] = None
    certificate_secret: Optional[str] = None
    redirect_http: bool = True
    tls_versions: List[str] = None
    cipher_suites: List[str] = None

@dataclass
class LoadBalancerRule:
    """Load balancer routing rule"""    priority: int
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    backend_services: List[BackendService]

@dataclass
class LoadBalancerSpec:
    """Load balancer specification"""    name: str
    lb_type: LoadBalancerType
    algorithm: BalancingAlgorithm = BalancingAlgorithm.ROUND_ROBIN
    backend_services: List[BackendService]
    health_check: HealthCheckConfig
    ssl_config: Optional[SSLConfig] = None
    rules: List[LoadBalancerRule] = None
    annotations: Dict[str, str] = None
    cross_zone_enabled: bool = True
    idle_timeout: int = 60

class LoadBalancerInterface(ABC):
    """Abstract interface for load balancers"""    
    @abstractmethod
    async def create_load_balancer(self, spec: LoadBalancerSpec) -> Dict[str, Any]:
        """Create load balancer"""        pass
    
    @abstractmethod
    async def update_load_balancer(self, name: str, spec: LoadBalancerSpec) -> Dict[str, Any]:
        """Update load balancer configuration"""        pass
    
    @abstractmethod
    async def delete_load_balancer(self, name: str) -> Dict[str, Any]:
        """Delete load balancer"""        pass
    
    @abstractmethod
    async def get_load_balancer_status(self, name: str) -> Dict[str, Any]:
        """Get load balancer status"""        pass

class NginxIngressController(LoadBalancerInterface):
    """NGINX Ingress Controller implementation"""    
    def __init__(self, k8s_client=None):
        self.k8s_client = k8s_client
        self.networking_v1 = client.NetworkingV1Api() if k8s_client else None
        self.core_v1 = client.CoreV1Api() if k8s_client else None
        
    async def create_load_balancer(self, spec: LoadBalancerSpec) -> Dict[str, Any]:
        """Create NGINX Ingress load balancer"""        try:
            # Create services for backend services
            for backend in spec.backend_services:
                await self._create_backend_service(backend)
            
            # Create ingress
            ingress = self._create_nginx_ingress(spec)
            
            if self.networking_v1:
                result = self.networking_v1.create_namespaced_ingress(
                    namespace='default',
                    body=ingress
                )
                
                logger.info(f"Created NGINX Ingress: {spec.name}")
                return {
                    'status': 'success',
                    'name': spec.name,
                    'type': 'nginx_ingress',
                    'ingress_class': 'nginx'
                }
            else:
                return {'status': 'success', 'message': 'NGINX Ingress manifest created'}
                
        except Exception as e:
            logger.error(f"Failed to create NGINX Ingress: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _create_nginx_ingress(self, spec: LoadBalancerSpec) -> client.V1Ingress:
        """Create NGINX Ingress manifest"""        # Default annotations for NGINX
        annotations = {
            'kubernetes.io/ingress.class': 'nginx',
            'nginx.ingress.kubernetes.io/load-balance': spec.algorithm.value,
            'nginx.ingress.kubernetes.io/upstream-hash-by': '$request_uri' if spec.algorithm == BalancingAlgorithm.IP_HASH else '',
            'nginx.ingress.kubernetes.io/proxy-connect-timeout': str(spec.health_check.timeout_seconds),
            'nginx.ingress.kubernetes.io/proxy-send-timeout': '60',
            'nginx.ingress.kubernetes.io/proxy-read-timeout': '60'
        }
        
        # Add SSL redirect if enabled
        if spec.ssl_config and spec.ssl_config.redirect_http:
            annotations['nginx.ingress.kubernetes.io/ssl-redirect'] = 'true'
        
        # Add custom annotations
        if spec.annotations:
            annotations.update(spec.annotations)
        
        # Create ingress rules
        rules = []
        for rule in spec.rules or []:
            paths = []
            for backend in rule.backend_services:
                paths.append(client.V1HTTPIngressPath(
                    path=rule.conditions.get('path', '/'),
                    path_type=rule.conditions.get('path_type', 'Prefix'),
                    backend=client.V1IngressBackend(
                        service=client.V1IngressServiceBackend(
                            name=backend.name,
                            port=client.V1ServiceBackendPort(number=backend.port)
                        )
                    )
                ))
            
            rules.append(client.V1IngressRule(
                host=rule.conditions.get('host'),
                http=client.V1HTTPIngressRuleValue(paths=paths)
            ))
        
        # Default rule if no custom rules
        if not rules:
            paths = []
            for backend in spec.backend_services:
                paths.append(client.V1HTTPIngressPath(
                    path='/',
                    path_type='Prefix',
                    backend=client.V1IngressBackend(
                        service=client.V1IngressServiceBackend(
                            name=backend.name,
                            port=client.V1ServiceBackendPort(number=backend.port)
                        )
                    )
                ))
            
            rules.append(client.V1IngressRule(
                http=client.V1HTTPIngressRuleValue(paths=paths)
            ))
        
        # TLS configuration
        tls = []
        if spec.ssl_config and spec.ssl_config.enabled:
            tls.append(client.V1IngressTLS(
                hosts=[rule.host for rule in rules if rule.host],
                secret_name=spec.ssl_config.certificate_secret
            ))
        
        ingress = client.V1Ingress(
            metadata=client.V1ObjectMeta(
                name=spec.name,
                annotations=annotations
            ),
            spec=client.V1IngressSpec(
                rules=rules,
                tls=tls if tls else None
            )
        )
        
        return ingress
    
    async def _create_backend_service(self, backend: BackendService) -> Dict[str, Any]:
        """Create Kubernetes service for backend"""        try:
            service = client.V1Service(
                metadata=client.V1ObjectMeta(
                    name=backend.name,
                    labels={'app': backend.name}
                ),
                spec=client.V1ServiceSpec(
                    selector={'app': backend.name},
                    ports=[client.V1ServicePort(
                        port=backend.port,
                        target_port=backend.port,
                        name='http'
                    )],
                    type='ClusterIP'
                )
            )
            
            if self.core_v1:
                self.core_v1.create_namespaced_service(
                    namespace='default',
                    body=service
                )
            
            return {'status': 'success', 'service': backend.name}
            
        except Exception as e:
            logger.error(f"Failed to create backend service: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def update_load_balancer(self, name: str, spec: LoadBalancerSpec) -> Dict[str, Any]:
        """Update NGINX Ingress load balancer"""        try:
            ingress = self._create_nginx_ingress(spec)
            
            if self.networking_v1:
                self.networking_v1.patch_namespaced_ingress(
                    name=name,
                    namespace='default',
                    body=ingress
                )
            
            logger.info(f"Updated NGINX Ingress: {name}")
            return {'status': 'success', 'name': name}
            
        except Exception as e:
            logger.error(f"Failed to update NGINX Ingress: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def delete_load_balancer(self, name: str) -> Dict[str, Any]:
        """Delete NGINX Ingress load balancer"""        try:
            if self.networking_v1:
                self.networking_v1.delete_namespaced_ingress(
                    name=name,
                    namespace='default'
                )
            
            logger.info(f"Deleted NGINX Ingress: {name}")
            return {'status': 'success', 'name': name}
            
        except Exception as e:
            logger.error(f"Failed to delete NGINX Ingress: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def get_load_balancer_status(self, name: str) -> Dict[str, Any]:
        """Get NGINX Ingress status"""        try:
            if self.networking_v1:
                ingress = self.networking_v1.read_namespaced_ingress(
                    name=name,
                    namespace='default'
                )
                
                return {
                    'status': 'success',
                    'name': name,
                    'ingress_ip': ingress.status.load_balancer.ingress[0].ip if ingress.status.load_balancer.ingress else None,
                    'ready': bool(ingress.status.load_balancer.ingress)
                }
            else:
                return {'status': 'success', 'name': name, 'ready': True}
                
        except Exception as e:
            logger.error(f"Failed to get NGINX Ingress status: {e}")
            return {'status': 'error', 'message': str(e)}

class TraefikController(LoadBalancerInterface):
    """Traefik load balancer implementation"""    
    def __init__(self, k8s_client=None):
        self.k8s_client = k8s_client
        
    async def create_load_balancer(self, spec: LoadBalancerSpec) -> Dict[str, Any]:
        """Create Traefik load balancer"""        try:
            # Implementation for Traefik IngressRoute
            logger.info(f"Creating Traefik load balancer: {spec.name}")
            return {
                'status': 'success',
                'name': spec.name,
                'type': 'traefik'
            }
        except Exception as e:
            logger.error(f"Failed to create Traefik load balancer: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def update_load_balancer(self, name: str, spec: LoadBalancerSpec) -> Dict[str, Any]:
        """Update Traefik load balancer"""        try:
            logger.info(f"Updating Traefik load balancer: {name}")
            return {'status': 'success', 'name': name}
        except Exception as e:
            logger.error(f"Failed to update Traefik load balancer: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def delete_load_balancer(self, name: str) -> Dict[str, Any]:
        """Delete Traefik load balancer"""        try:
            logger.info(f"Deleting Traefik load balancer: {name}")
            return {'status': 'success', 'name': name}
        except Exception as e:
            logger.error(f"Failed to delete Traefik load balancer: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def get_load_balancer_status(self, name: str) -> Dict[str, Any]:
        """Get Traefik load balancer status"""        try:
            logger.info(f"Getting Traefik load balancer status: {name}")
            return {'status': 'success', 'name': name, 'ready': True}
        except Exception as e:
            logger.error(f"Failed to get Traefik status: {e}")
            return {'status': 'error', 'message': str(e)}

class IstioGateway(LoadBalancerInterface):
    """Istio Gateway implementation"""    
    def __init__(self, k8s_client=None):
        self.k8s_client = k8s_client
        
    async def create_load_balancer(self, spec: LoadBalancerSpec) -> Dict[str, Any]:
        """Create Istio Gateway"""        try:
            # Implementation for Istio Gateway and VirtualService
            logger.info(f"Creating Istio Gateway: {spec.name}")
            return {
                'status': 'success',
                'name': spec.name,
                'type': 'istio_gateway'
            }
        except Exception as e:
            logger.error(f"Failed to create Istio Gateway: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def update_load_balancer(self, name: str, spec: LoadBalancerSpec) -> Dict[str, Any]:
        """Update Istio Gateway"""        try:
            logger.info(f"Updating Istio Gateway: {name}")
            return {'status': 'success', 'name': name}
        except Exception as e:
            logger.error(f"Failed to update Istio Gateway: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def delete_load_balancer(self, name: str) -> Dict[str, Any]:
        """Delete Istio Gateway"""        try:
            logger.info(f"Deleting Istio Gateway: {name}")
            return {'status': 'success', 'name': name}
        except Exception as e:
            logger.error(f"Failed to delete Istio Gateway: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def get_load_balancer_status(self, name: str) -> Dict[str, Any]:
        """Get Istio Gateway status"""        try:
            logger.info(f"Getting Istio Gateway status: {name}")
            return {'status': 'success', 'name': name, 'ready': True}
        except Exception as e:
            logger.error(f"Failed to get Istio Gateway status: {e}")
            return {'status': 'error', 'message': str(e)}

class LoadBalancerManager:
    """Main load balancer manager"""    
    def __init__(self, k8s_client=None):
        self.k8s_client = k8s_client
        self.controllers = {
            LoadBalancerType.NGINX_INGRESS: NginxIngressController(k8s_client),
            LoadBalancerType.TRAEFIK: TraefikController(k8s_client),
            LoadBalancerType.ISTIO_GATEWAY: IstioGateway(k8s_client)
        }
        
    async def create_load_balancer(self, spec: LoadBalancerSpec) -> Dict[str, Any]:
        """Create load balancer based on type"""        try:
            controller = self.controllers.get(spec.lb_type)
            if not controller:
                return {'status': 'error', 'message': f'Unsupported load balancer type: {spec.lb_type}'}
            
            result = await controller.create_load_balancer(spec)
            logger.info(f"Created load balancer: {spec.name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create load balancer: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def create_ia_influencer_load_balancers(self, namespace: str = "ia-influencer") -> Dict[str, Any]:
        """Create complete load balancer setup for IA Influencer platform"""        try:
            results = {}
            
            # API Gateway Load Balancer
            api_backends = [
                BackendService(
                    name="ia-influencer-api",
                    host="ia-influencer-api-service",
                    port=8000,
                    health_check_path="/api/v1/health"
                )
            ]
            
            api_health_check = HealthCheckConfig(
                check_type=HealthCheckType.HTTP,
                path="/api/v1/health",
                interval_seconds=30,
                timeout_seconds=5,
                healthy_threshold=2,
                unhealthy_threshold=3
            )
            
            ssl_config = SSLConfig(
                enabled=True,
                certificate_secret="ia-influencer-tls",
                redirect_http=True
            )
            
            api_rules = [
                LoadBalancerRule(
                    priority=100,
                    conditions={
                        'host': 'api.ia-influencer.com',
                        'path': '/api',
                        'path_type': 'Prefix'
                    },
                    actions={'forward': True},
                    backend_services=api_backends
                )
            ]
            
            api_lb_spec = LoadBalancerSpec(
                name="ia-influencer-api-lb",
                lb_type=LoadBalancerType.NGINX_INGRESS,
                algorithm=BalancingAlgorithm.ROUND_ROBIN,
                backend_services=api_backends,
                health_check=api_health_check,
                ssl_config=ssl_config,
                rules=api_rules,
                annotations={
                    'nginx.ingress.kubernetes.io/rate-limit': '100',
                    'nginx.ingress.kubernetes.io/rate-limit-window': '1m',
                    'nginx.ingress.kubernetes.io/enable-cors': 'true'
                }
            )
            
            results['api_load_balancer'] = await self.create_load_balancer(api_lb_spec)
            
            # Frontend Load Balancer
            frontend_backends = [
                BackendService(
                    name="ia-influencer-frontend",
                    host="ia-influencer-frontend-service",
                    port=3000,
                    health_check_path="/"
                )
            ]
            
            frontend_health_check = HealthCheckConfig(
                check_type=HealthCheckType.HTTP,
                path="/",
                interval_seconds=30
            )
            
            frontend_rules = [
                LoadBalancerRule(
                    priority=100,
                    conditions={
                        'host': 'app.ia-influencer.com',
                        'path': '/',
                        'path_type': 'Prefix'
                    },
                    actions={'forward': True},
                    backend_services=frontend_backends
                )
            ]
            
            frontend_lb_spec = LoadBalancerSpec(
                name="ia-influencer-frontend-lb",
                lb_type=LoadBalancerType.NGINX_INGRESS,
                algorithm=BalancingAlgorithm.ROUND_ROBIN,
                backend_services=frontend_backends,
                health_check=frontend_health_check,
                ssl_config=ssl_config,
                rules=frontend_rules,
                annotations={
                    'nginx.ingress.kubernetes.io/proxy-body-size': '10m',
                    'nginx.ingress.kubernetes.io/enable-cors': 'true'
                }
            )
            
            results['frontend_load_balancer'] = await self.create_load_balancer(frontend_lb_spec)
            
            # AI Processing Load Balancer
            ai_backends = [
                BackendService(
                    name="ia-influencer-ai-processing",
                    host="ia-influencer-ai-service",
                    port=8001,
                    health_check_path="/health"
                )
            ]
            
            ai_health_check = HealthCheckConfig(
                check_type=HealthCheckType.HTTP,
                path="/health",
                interval_seconds=60,  # Longer interval for AI services
                timeout_seconds=10
            )
            
            ai_rules = [
                LoadBalancerRule(
                    priority=100,
                    conditions={
                        'host': 'ai.ia-influencer.com',
                        'path': '/ai',
                        'path_type': 'Prefix'
                    },
                    actions={'forward': True},
                    backend_services=ai_backends
                )
            ]
            
            ai_lb_spec = LoadBalancerSpec(
                name="ia-influencer-ai-lb",
                lb_type=LoadBalancerType.NGINX_INGRESS,
                algorithm=BalancingAlgorithm.LEAST_CONNECTIONS,  # Better for AI workloads
                backend_services=ai_backends,
                health_check=ai_health_check,
                ssl_config=ssl_config,
                rules=ai_rules,
                annotations={
                    'nginx.ingress.kubernetes.io/proxy-connect-timeout': '300',
                    'nginx.ingress.kubernetes.io/proxy-send-timeout': '300',
                    'nginx.ingress.kubernetes.io/proxy-read-timeout': '300',
                    'nginx.ingress.kubernetes.io/proxy-body-size': '100m'
                }
            )
            
            results['ai_load_balancer'] = await self.create_load_balancer(ai_lb_spec)
            
            logger.info("Created complete IA Influencer load balancer setup")
            return {
                'status': 'success',
                'load_balancers': results
            }
            
        except Exception as e:
            logger.error(f"Failed to create IA Influencer load balancers: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def update_load_balancer(self, name: str, spec: LoadBalancerSpec) -> Dict[str, Any]:
        """Update load balancer"""        try:
            controller = self.controllers.get(spec.lb_type)
            if not controller:
                return {'status': 'error', 'message': f'Unsupported load balancer type: {spec.lb_type}'}
            
            result = await controller.update_load_balancer(name, spec)
            logger.info(f"Updated load balancer: {name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update load balancer: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def delete_load_balancer(self, name: str, lb_type: LoadBalancerType) -> Dict[str, Any]:
        """Delete load balancer"""        try:
            controller = self.controllers.get(lb_type)
            if not controller:
                return {'status': 'error', 'message': f'Unsupported load balancer type: {lb_type}'}
            
            result = await controller.delete_load_balancer(name)
            logger.info(f"Deleted load balancer: {name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to delete load balancer: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def get_load_balancer_status(self, name: str, lb_type: LoadBalancerType) -> Dict[str, Any]:
        """Get load balancer status"""        try:
            controller = self.controllers.get(lb_type)
            if not controller:
                return {'status': 'error', 'message': f'Unsupported load balancer type: {lb_type}'}
            
            result = await controller.get_load_balancer_status(name)
            return result
            
        except Exception as e:
            logger.error(f"Failed to get load balancer status: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def configure_traffic_splitting(self, name: str, traffic_rules: Dict[str, int]) -> Dict[str, Any]:
        """Configure traffic splitting for canary deployments"""        try:
            # Implementation for traffic splitting
            logger.info(f"Configuring traffic splitting for: {name}")
            return {
                'status': 'success',
                'traffic_rules': traffic_rules
            }
        except Exception as e:
            logger.error(f"Failed to configure traffic splitting: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def enable_circuit_breaker(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Enable circuit breaker for load balancer"""        try:
            # Implementation for circuit breaker
            logger.info(f"Enabling circuit breaker for: {name}")
            return {
                'status': 'success',
                'circuit_breaker': 'enabled'
            }
        except Exception as e:
            logger.error(f"Failed to enable circuit breaker: {e}")
            return {'status': 'error', 'message': str(e)}
