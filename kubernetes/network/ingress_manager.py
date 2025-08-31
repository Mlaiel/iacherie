"""IA Influencer Agent - Ingress Network Manager
Enterprise ingress configuration and load balancing for multi-tenant platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
Project: IA Influencer Agent Platform - Content Protection & Monetization
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  AVERTISSEMENT SÉVÈRE ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact autorisations: mlaiel@live.de
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import yaml
import ssl
import socket
from datetime import datetime, timedelta

from kubernetes import client, config
from prometheus_client import Counter, Histogram, Gauge
import consul
import nginx
from haproxy_config import HAProxyConfig

# Metrics
ingress_requests_total = Counter('ingress_requests_total', 'Total ingress requests', ['method', 'status', 'path'])
ingress_request_duration = Histogram('ingress_request_duration_seconds', 'Request duration')
active_connections = Gauge('ingress_active_connections', 'Active connections count')

logger = logging.getLogger(__name__)


class IngressProtocol(Enum):
    """Supported ingress protocols"""    HTTP = "http"
    HTTPS = "https" 
    GRPC = "grpc"
    WEBSOCKET = "ws"
    TCP = "tcp"
    UDP = "udp"


class LoadBalancingMethod(Enum):
    """Load balancing algorithms"""    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_conn"
    IP_HASH = "ip_hash"
    WEIGHTED_ROUND_ROBIN = "weighted_rr"
    CONSISTENT_HASH = "consistent_hash"


@dataclass
class BackendService:
    """Backend service configuration"""    name: str
    host: str
    port: int
    weight: int = 100
    max_connections: int = 1000
    health_check_path: str = "/health"
    ssl_verify: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IngressRule:
    """Ingress routing rule"""    host: str
    path: str
    service_name: str
    port: int
    protocol: IngressProtocol = IngressProtocol.HTTP
    ssl_enabled: bool = True
    rate_limit: Optional[int] = None
    auth_required: bool = True
    tenant_isolation: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SSLCertificate:
    """SSL certificate configuration"""    name: str
    cert_file: str
    key_file: str
    ca_file: Optional[str] = None
    domains: List[str] = field(default_factory=list)
    auto_renew: bool = True
    provider: str = "letsencrypt"
    expires_at: Optional[datetime] = None


class IngressManager:
    """    Enterprise ingress manager for IA Influencer Agent Platform
    Handles load balancing, SSL termination, routing, and security
    """    
    def __init__(
        self,
        config_path: str = "/etc/ingress/config.yaml",
        kubernetes_config: Optional[str] = None,
        consul_config: Optional[Dict] = None
    ):
        self.config_path = config_path
        self.rules: Dict[str, IngressRule] = {}
        self.services: Dict[str, List[BackendService]] = {}
        self.certificates: Dict[str, SSLCertificate] = {}
        self.load_balancer_config = {}
        
        # Initialize Kubernetes client
        if kubernetes_config:
            config.load_kube_config(config_file=kubernetes_config)
        else:
            config.load_incluster_config()
        self.k8s_client = client.ApiClient()
        self.k8s_networking = client.NetworkingV1Api()
        
        # Initialize service discovery
        self.consul_client = None
        if consul_config:
            self.consul_client = consul.Consul(**consul_config)
        
        # Initialize load balancers
        self.nginx_config = None
        self.haproxy_config = None
        
        self._load_configuration()
        
    async def initialize(self) -> None:
        """Initialize ingress manager"""        try:
            logger.info("Initializing Ingress Manager...")
            
            # Load existing configuration
            await self._load_ingress_configuration()
            
            # Initialize SSL certificates
            await self._initialize_ssl_certificates()
            
            # Setup load balancers
            await self._setup_load_balancers()
            
            # Start health checks
            await self._start_health_checks()
            
            # Start metrics collection
            await self._start_metrics_collection()
            
            logger.info("Ingress Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Ingress Manager: {e}")
            raise
    
    async def add_ingress_rule(self, rule: IngressRule) -> bool:
        """Add new ingress rule"""        try:
            logger.info(f"Adding ingress rule for {rule.host}{rule.path}")
            
            # Validate rule
            if not await self._validate_rule(rule):
                return False
            
            # Add rule to configuration
            rule_key = f"{rule.host}{rule.path}"
            self.rules[rule_key] = rule
            
            # Update load balancer configuration
            await self._update_load_balancer_config()
            
            # Apply Kubernetes ingress
            await self._apply_kubernetes_ingress(rule)
            
            # Update SSL configuration if needed
            if rule.ssl_enabled:
                await self._update_ssl_configuration(rule)
            
            logger.info(f"Ingress rule added successfully: {rule_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add ingress rule: {e}")
            return False
    
    async def remove_ingress_rule(self, host: str, path: str) -> bool:
        """Remove ingress rule"""        try:
            rule_key = f"{host}{path}"
            
            if rule_key not in self.rules:
                logger.warning(f"Ingress rule not found: {rule_key}")
                return False
            
            # Remove from configuration
            del self.rules[rule_key]
            
            # Update load balancer
            await self._update_load_balancer_config()
            
            # Remove Kubernetes ingress
            await self._remove_kubernetes_ingress(host, path)
            
            logger.info(f"Ingress rule removed: {rule_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove ingress rule: {e}")
            return False
    
    async def register_backend_service(
        self,
        service_name: str,
        services: List[BackendService]
    ) -> bool:
        """Register backend services for load balancing"""        try:
            logger.info(f"Registering backend services for {service_name}")
            
            # Validate services
            for service in services:
                if not await self._validate_backend_service(service):
                    return False
            
            # Register services
            self.services[service_name] = services
            
            # Update load balancer pools
            await self._update_service_pools(service_name, services)
            
            # Register in service discovery
            if self.consul_client:
                await self._register_consul_services(service_name, services)
            
            logger.info(f"Backend services registered: {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register backend services: {e}")
            return False
    
    async def configure_ssl_certificate(self, certificate: SSLCertificate) -> bool:
        """Configure SSL certificate"""        try:
            logger.info(f"Configuring SSL certificate: {certificate.name}")
            
            # Validate certificate
            if not await self._validate_ssl_certificate(certificate):
                return False
            
            # Store certificate
            self.certificates[certificate.name] = certificate
            
            # Generate Kubernetes secret
            await self._create_kubernetes_ssl_secret(certificate)
            
            # Update load balancer SSL configuration
            await self._update_ssl_load_balancer_config(certificate)
            
            # Schedule auto-renewal if enabled
            if certificate.auto_renew:
                await self._schedule_certificate_renewal(certificate)
            
            logger.info(f"SSL certificate configured: {certificate.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure SSL certificate: {e}")
            return False
    
    async def update_load_balancing_method(
        self,
        service_name: str,
        method: LoadBalancingMethod
    ) -> bool:
        """Update load balancing method for service"""        try:
            if service_name not in self.services:
                logger.error(f"Service not found: {service_name}")
                return False
            
            # Update configuration
            if service_name not in self.load_balancer_config:
                self.load_balancer_config[service_name] = {}
            
            self.load_balancer_config[service_name]['method'] = method.value
            
            # Apply to load balancers
            await self._apply_load_balancing_method(service_name, method)
            
            logger.info(f"Load balancing method updated: {service_name} -> {method.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update load balancing method: {e}")
            return False
    
    async def get_ingress_status(self) -> Dict[str, Any]:
        """Get comprehensive ingress status"""        try:
            status = {
                'total_rules': len(self.rules),
                'total_services': len(self.services),
                'total_certificates': len(self.certificates),
                'active_connections': active_connections._value._value,
                'rules': {},
                'services': {},
                'certificates': {},
                'load_balancer_status': {},
                'health_checks': {}
            }
            
            # Rule status
            for rule_key, rule in self.rules.items():
                status['rules'][rule_key] = {
                    'host': rule.host,
                    'path': rule.path,
                    'service': rule.service_name,
                    'protocol': rule.protocol.value,
                    'ssl_enabled': rule.ssl_enabled,
                    'auth_required': rule.auth_required
                }
            
            # Service status
            for service_name, backends in self.services.items():
                health_status = await self._check_service_health(service_name)
                status['services'][service_name] = {
                    'backend_count': len(backends),
                    'healthy_backends': health_status['healthy'],
                    'unhealthy_backends': health_status['unhealthy'],
                    'load_balancing_method': self.load_balancer_config.get(
                        service_name, {}
                    ).get('method', 'round_robin')
                }
            
            # Certificate status
            for cert_name, cert in self.certificates.items():
                status['certificates'][cert_name] = {
                    'domains': cert.domains,
                    'expires_at': cert.expires_at.isoformat() if cert.expires_at else None,
                    'auto_renew': cert.auto_renew,
                    'provider': cert.provider
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get ingress status: {e}")
            return {}
    
    # Private methods
    
    async def _load_ingress_configuration(self) -> None:
        """Load ingress configuration from file"""        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Load rules
            if 'rules' in config_data:
                for rule_data in config_data['rules']:
                    rule = IngressRule(**rule_data)
                    rule_key = f"{rule.host}{rule.path}"
                    self.rules[rule_key] = rule
            
            # Load services
            if 'services' in config_data:
                for service_name, backends_data in config_data['services'].items():
                    backends = [BackendService(**backend) for backend in backends_data]
                    self.services[service_name] = backends
            
            # Load certificates
            if 'certificates' in config_data:
                for cert_data in config_data['certificates']:
                    cert = SSLCertificate(**cert_data)
                    self.certificates[cert.name] = cert
            
        except FileNotFoundError:
            logger.info("Configuration file not found, starting with empty configuration")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
    
    async def _validate_rule(self, rule: IngressRule) -> bool:
        """Validate ingress rule"""        if not rule.host or not rule.path:
            logger.error("Host and path are required")
            return False
        
        if rule.service_name not in self.services:
            logger.error(f"Service not found: {rule.service_name}")
            return False
        
        if rule.rate_limit and rule.rate_limit <= 0:
            logger.error("Rate limit must be positive")
            return False
        
        return True
    
    async def _validate_backend_service(self, service: BackendService) -> bool:
        """Validate backend service"""        if not service.name or not service.host:
            logger.error("Service name and host are required")
            return False
        
        if service.port <= 0 or service.port > 65535:
            logger.error("Invalid port number")
            return False
        
        if service.weight <= 0:
            logger.error("Service weight must be positive")
            return False
        
        return True
    
    async def _validate_ssl_certificate(self, certificate: SSLCertificate) -> bool:
        """Validate SSL certificate"""        if not certificate.name or not certificate.cert_file or not certificate.key_file:
            logger.error("Certificate name, cert_file and key_file are required")
            return False
        
        # Validate certificate files exist
        import os
        if not os.path.exists(certificate.cert_file):
            logger.error(f"Certificate file not found: {certificate.cert_file}")
            return False
        
        if not os.path.exists(certificate.key_file):
            logger.error(f"Key file not found: {certificate.key_file}")
            return False
        
        return True
    
    async def _update_load_balancer_config(self) -> None:
        """Update load balancer configuration"""        # Update NGINX configuration
        if self.nginx_config:
            await self._update_nginx_config()
        
        # Update HAProxy configuration
        if self.haproxy_config:
            await self._update_haproxy_config()
    
    async def _apply_kubernetes_ingress(self, rule: IngressRule) -> None:
        """Apply Kubernetes ingress configuration"""        try:
            ingress_name = f"ingress-{rule.service_name}"
            namespace = "default"
            
            # Create ingress manifest
            ingress_manifest = {
                'apiVersion': 'networking.k8s.io/v1',
                'kind': 'Ingress',
                'metadata': {
                    'name': ingress_name,
                    'namespace': namespace,
                    'annotations': {
                        'kubernetes.io/ingress.class': 'nginx',
                        'nginx.ingress.kubernetes.io/ssl-redirect': str(rule.ssl_enabled).lower()
                    }
                },
                'spec': {
                    'rules': [{
                        'host': rule.host,
                        'http': {
                            'paths': [{
                                'path': rule.path,
                                'pathType': 'Prefix',
                                'backend': {
                                    'service': {
                                        'name': rule.service_name,
                                        'port': {
                                            'number': rule.port
                                        }
                                    }
                                }
                            }]
                        }
                    }]
                }
            }
            
            # Add TLS if SSL enabled
            if rule.ssl_enabled:
                ingress_manifest['spec']['tls'] = [{
                    'hosts': [rule.host],
                    'secretName': f"tls-{rule.service_name}"
                }]
            
            # Apply ingress
            try:
                self.k8s_networking.read_namespaced_ingress(
                    name=ingress_name,
                    namespace=namespace
                )
                # Update existing
                self.k8s_networking.patch_namespaced_ingress(
                    name=ingress_name,
                    namespace=namespace,
                    body=ingress_manifest
                )
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    # Create new
                    self.k8s_networking.create_namespaced_ingress(
                        namespace=namespace,
                        body=ingress_manifest
                    )
                else:
                    raise
            
        except Exception as e:
            logger.error(f"Failed to apply Kubernetes ingress: {e}")
            raise
    
    async def _initialize_ssl_certificates(self) -> None:
        """Initialize SSL certificates"""        for cert_name, certificate in self.certificates.items():
            await self._create_kubernetes_ssl_secret(certificate)
    
    async def _setup_load_balancers(self) -> None:
        """Setup load balancer configurations"""        # Initialize NGINX if available
        try:
            self.nginx_config = nginx.NginxConfig()
            await self._update_nginx_config()
        except Exception:
            logger.warning("NGINX not available")
        
        # Initialize HAProxy if available
        try:
            self.haproxy_config = HAProxyConfig()
            await self._update_haproxy_config()
        except Exception:
            logger.warning("HAProxy not available")
    
    async def _start_health_checks(self) -> None:
        """Start periodic health checks"""        asyncio.create_task(self._health_check_loop())
    
    async def _start_metrics_collection(self) -> None:
        """Start metrics collection"""        asyncio.create_task(self._metrics_collection_loop())
    
    async def _health_check_loop(self) -> None:
        """Periodic health check loop"""        while True:
            try:
                for service_name in self.services:
                    await self._check_service_health(service_name)
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(60)
    
    async def _metrics_collection_loop(self) -> None:
        """Metrics collection loop"""        while True:
            try:
                # Update active connections metric
                # This would be implemented based on actual load balancer stats
                await asyncio.sleep(60)  # Collect every minute
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)
    
    def _load_configuration(self) -> None:
        """Load initial configuration"""        try:
            asyncio.create_task(self._load_ingress_configuration())
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
