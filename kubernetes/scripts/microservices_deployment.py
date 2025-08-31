#!/usr/bin/env python3
"""
Microservices Deployment Manager
Enterprise-grade deployment system for comprehensive microservices architecture,
service mesh, API gateway, service discovery, and inter-service communication.

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Project Team Specializations:
- Lead Dev IA + Microservices Architecture
- Backend Senior Python + Service Design
- Infrastructure Engineer + Kubernetes + Service Mesh
- Frontend Engineer + API Integration
- DevOps + Container Orchestration
- Security Engineer + Service Authentication
- Platform Engineer + Service Discovery

 STRONG WARNING FOR UNAUTHORIZED USE:
This code contains proprietary microservices patterns and trade secrets of Fahed Mlaiel.
Any unauthorized copying, modification, distribution, or use of this code
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and may result in severe legal action under German
and international copyright laws.

Project: IA Influencer Agent Platform - Microservices Infrastructure
Copyright: Fahed Mlaiel - All rights reserved
"""

import os
import sys
import time
import json
import logging
import asyncio
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import yaml
import requests
import docker
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import consul
import etcd3
import redis
import psycopg2
from sqlalchemy import create_engine
import istio_client_python
import envoy
import grpc
import prometheus_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Types of microservices"""
    API_GATEWAY = "api_gateway"
    CONTENT_PROTECTION = "content_protection"
    AI_FINGERPRINTING = "ai_fingerprinting"
    CONTENT_CRAWLER = "content_crawler"
    LICENSING_MANAGER = "licensing_manager"
    REVENUE_MANAGER = "revenue_manager"
    USER_MANAGER = "user_manager"
    NOTIFICATION_SERVICE = "notification_service"
    ANALYTICS_SERVICE = "analytics_service"
    SEARCH_SERVICE = "search_service"
    COLLABORATION_SERVICE = "collaboration_service"
    PAYMENT_SERVICE = "payment_service"
    LEGAL_SERVICE = "legal_service"
    BLOCKCHAIN_SERVICE = "blockchain_service"
    ML_INFERENCE_SERVICE = "ml_inference_service"
    DATA_PROCESSING_SERVICE = "data_processing_service"


class CommunicationProtocol(Enum):
    """Communication protocols between services"""
    HTTP_REST = "http_rest"
    GRPC = "grpc"
    GRAPHQL = "graphql"
    MESSAGE_QUEUE = "message_queue"
    EVENT_STREAMING = "event_streaming"
    WEBSOCKET = "websocket"


class ServiceDiscoveryType(Enum):
    """Service discovery mechanisms"""
    CONSUL = "consul"
    ETCD = "etcd"
    KUBERNETES_DNS = "kubernetes_dns"
    EUREKA = "eureka"
    ZOOKEEPER = "zookeeper"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    HEALTH_BASED = "health_based"
    GEOGRAPHIC = "geographic"


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class ServiceMeshType(Enum):
    """Service mesh implementations"""
    ISTIO = "istio"
    LINKERD = "linkerd"
    CONSUL_CONNECT = "consul_connect"
    ENVOY = "envoy"


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""
    path: str
    method: str
    protocol: CommunicationProtocol
    authentication_required: bool = True
    rate_limit: Optional[int] = None
    timeout_seconds: int = 30
    circuit_breaker_enabled: bool = True
    caching_enabled: bool = False
    cache_ttl_seconds: int = 300
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'path': self.path,
            'method': self.method,
            'protocol': self.protocol.value,
            'authentication_required': self.authentication_required,
            'rate_limit': self.rate_limit,
            'timeout_seconds': self.timeout_seconds,
            'circuit_breaker_enabled': self.circuit_breaker_enabled,
            'caching_enabled': self.caching_enabled,
            'cache_ttl_seconds': self.cache_ttl_seconds
        }


@dataclass
class ServiceDependency:
    """Service dependency configuration"""
    service_name: str
    service_type: ServiceType
    protocol: CommunicationProtocol
    endpoint_url: str
    timeout_seconds: int = 30
    retry_attempts: int = 3
    circuit_breaker_enabled: bool = True
    fallback_enabled: bool = True
    health_check_path: str = "/health"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'service_name': self.service_name,
            'service_type': self.service_type.value,
            'protocol': self.protocol.value,
            'endpoint_url': self.endpoint_url,
            'timeout_seconds': self.timeout_seconds,
            'retry_attempts': self.retry_attempts,
            'circuit_breaker_enabled': self.circuit_breaker_enabled,
            'fallback_enabled': self.fallback_enabled,
            'health_check_path': self.health_check_path
        }


@dataclass
class ServiceConfiguration:
    """Complete microservice configuration"""
    service_name: str
    service_type: ServiceType
    version: str
    namespace: str
    replicas: int = 3
    port: int = 8080
    management_port: int = 8081
    protocol: CommunicationProtocol = CommunicationProtocol.HTTP_REST
    endpoints: List[ServiceEndpoint] = field(default_factory=list)
    dependencies: List[ServiceDependency] = field(default_factory=list)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    resource_limits: Dict[str, str] = field(default_factory=lambda: {
        'cpu': '1000m',
        'memory': '2Gi',
        'storage': '20Gi'
    })
    resource_requests: Dict[str, str] = field(default_factory=lambda: {
        'cpu': '250m',
        'memory': '512Mi',
        'storage': '10Gi'
    })
    health_check_enabled: bool = True
    metrics_enabled: bool = True
    logging_enabled: bool = True
    tracing_enabled: bool = True
    auto_scaling_enabled: bool = True
    min_replicas: int = 2
    max_replicas: int = 10
    target_cpu_utilization: int = 70
    service_mesh_enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'service_name': self.service_name,
            'service_type': self.service_type.value,
            'version': self.version,
            'namespace': self.namespace,
            'replicas': self.replicas,
            'port': self.port,
            'management_port': self.management_port,
            'protocol': self.protocol.value,
            'endpoints': [ep.to_dict() for ep in self.endpoints],
            'dependencies': [dep.to_dict() for dep in self.dependencies],
            'environment_variables': self.environment_variables,
            'resource_limits': self.resource_limits,
            'resource_requests': self.resource_requests,
            'health_check_enabled': self.health_check_enabled,
            'metrics_enabled': self.metrics_enabled,
            'logging_enabled': self.logging_enabled,
            'tracing_enabled': self.tracing_enabled,
            'auto_scaling_enabled': self.auto_scaling_enabled,
            'min_replicas': self.min_replicas,
            'max_replicas': self.max_replicas,
            'target_cpu_utilization': self.target_cpu_utilization,
            'service_mesh_enabled': self.service_mesh_enabled
        }


@dataclass
class ServiceMeshConfiguration:
    """Service mesh configuration"""
    mesh_type: ServiceMeshType = ServiceMeshType.ISTIO
    mtls_enabled: bool = True
    traffic_management_enabled: bool = True
    security_policies_enabled: bool = True
    observability_enabled: bool = True
    canary_deployments_enabled: bool = True
    circuit_breaker_enabled: bool = True
    retry_policies_enabled: bool = True
    timeout_policies_enabled: bool = True
    rate_limiting_enabled: bool = True
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'mesh_type': self.mesh_type.value,
            'mtls_enabled': self.mtls_enabled,
            'traffic_management_enabled': self.traffic_management_enabled,
            'security_policies_enabled': self.security_policies_enabled,
            'observability_enabled': self.observability_enabled,
            'canary_deployments_enabled': self.canary_deployments_enabled,
            'circuit_breaker_enabled': self.circuit_breaker_enabled,
            'retry_policies_enabled': self.retry_policies_enabled,
            'timeout_policies_enabled': self.timeout_policies_enabled,
            'rate_limiting_enabled': self.rate_limiting_enabled,
            'load_balancing_strategy': self.load_balancing_strategy.value
        }


@dataclass
class APIGatewayConfiguration:
    """API Gateway configuration"""
    gateway_name: str = "ia-influencer-gateway"
    port: int = 80
    ssl_port: int = 443
    ssl_enabled: bool = True
    rate_limiting_enabled: bool = True
    authentication_enabled: bool = True
    authorization_enabled: bool = True
    request_logging_enabled: bool = True
    response_caching_enabled: bool = True
    compression_enabled: bool = True
    cors_enabled: bool = True
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    health_checks_enabled: bool = True
    circuit_breaker_enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'gateway_name': self.gateway_name,
            'port': self.port,
            'ssl_port': self.ssl_port,
            'ssl_enabled': self.ssl_enabled,
            'rate_limiting_enabled': self.rate_limiting_enabled,
            'authentication_enabled': self.authentication_enabled,
            'authorization_enabled': self.authorization_enabled,
            'request_logging_enabled': self.request_logging_enabled,
            'response_caching_enabled': self.response_caching_enabled,
            'compression_enabled': self.compression_enabled,
            'cors_enabled': self.cors_enabled,
            'load_balancing_strategy': self.load_balancing_strategy.value,
            'health_checks_enabled': self.health_checks_enabled,
            'circuit_breaker_enabled': self.circuit_breaker_enabled
        }


class MicroservicesDeploymentManager:
    """
    Enterprise Microservices Deployment Manager
    Handles deployment and management of comprehensive microservices architecture
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Microservices Deployment Manager"""
        self.config_path = config_path or os.getenv('MICROSERVICES_CONFIG_PATH', '/etc/microservices/config.yaml')
        self.services: Dict[str, ServiceConfiguration] = {}
        self.service_mesh_config: ServiceMeshConfiguration = ServiceMeshConfiguration()
        self.api_gateway_config: APIGatewayConfiguration = APIGatewayConfiguration()
        
        # Initialize clients
        self._init_kubernetes_client()
        self._init_docker_client()
        self._init_service_discovery_client()
        self._init_service_mesh_client()
        self._init_database_client()
        self._init_redis_client()
        
        # Load configuration
        self._load_config()
        
        logger.info("Microservices Deployment Manager initialized successfully")
    
    def _init_kubernetes_client(self):
        """Initialize Kubernetes client"""



        try:
            config.load_incluster_config()
        except:
            try:
                config.load_kube_config()
            except:
                logger.warning("Kubernetes config not found, some features may be unavailable")
                self.k8s_client = None
                return
        
        self.k8s_client = client.ApiClient()
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
        self.networking_v1 = client.NetworkingV1Api()
        self.autoscaling_v1 = client.AutoscalingV1Api()
        self.custom_objects_api = client.CustomObjectsApi()
        logger.info("Kubernetes client initialized")
    
    def _init_docker_client(self):
        """Initialize Docker client"""



        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.warning(f"Docker client initialization failed: {e}")
            self.docker_client = None
    
    def _init_service_discovery_client(self):
        """Initialize service discovery client"""



        try:
            consul_host = os.getenv('CONSUL_HOST', 'localhost')
            consul_port = int(os.getenv('CONSUL_PORT', '8500'))
            self.consul_client = consul.Consul(host=consul_host, port=consul_port)
            logger.info("Consul client initialized")
        except Exception as e:
            logger.warning(f"Consul client initialization failed: {e}")
            self.consul_client = None
        
        try:
            etcd_host = os.getenv('ETCD_HOST', 'localhost')
            etcd_port = int(os.getenv('ETCD_PORT', '2379'))
            self.etcd_client = etcd3.client(host=etcd_host, port=etcd_port)
            logger.info("etcd client initialized")
        except Exception as e:
            logger.warning(f"etcd client initialization failed: {e}")
            self.etcd_client = None
    
    def _init_service_mesh_client(self):
        """Initialize service mesh clients"""



        try:
            # Istio client initialization
            self.istio_client = None  # Placeholder for Istio client
            logger.info("Service mesh clients initialized")
        except Exception as e:
            logger.warning(f"Service mesh client initialization failed: {e}")
            self.istio_client = None
    
    def _init_database_client(self):
        """Initialize database client"""



        try:
            db_url = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost:5432/ia_influencer')
            self.db_engine = create_engine(db_url)
            logger.info("Database client initialized")
        except Exception as e:
            logger.warning(f"Database client initialization failed: {e}")
            self.db_engine = None
    
    def _init_redis_client(self):
        """Initialize Redis client for caching and service coordination"""



        try:
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', '6379'))
            redis_password = os.getenv('REDIS_PASSWORD')
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Redis client initialized")
        except Exception as e:
            logger.warning(f"Redis client initialization failed: {e}")
            self.redis_client = None
    
    def _load_config(self):
        """Load microservices configurations"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                # Load service configurations
                for service_data in config_data.get('services', []):
                    service_config = ServiceConfiguration(
                        service_name=service_data['service_name'],
                        service_type=ServiceType(service_data['service_type']),
                        version=service_data['version'],
                        namespace=service_data['namespace'],
                        replicas=service_data.get('replicas', 3),
                        port=service_data.get('port', 8080),
                        management_port=service_data.get('management_port', 8081),
                        protocol=CommunicationProtocol(service_data.get('protocol', 'http_rest')),
                        endpoints=[
                            ServiceEndpoint(
                                path=ep['path'],
                                method=ep['method'],
                                protocol=CommunicationProtocol(ep.get('protocol', 'http_rest')),
                                authentication_required=ep.get('authentication_required', True),
                                rate_limit=ep.get('rate_limit'),
                                timeout_seconds=ep.get('timeout_seconds', 30),
                                circuit_breaker_enabled=ep.get('circuit_breaker_enabled', True),
                                caching_enabled=ep.get('caching_enabled', False),
                                cache_ttl_seconds=ep.get('cache_ttl_seconds', 300)
                            ) for ep in service_data.get('endpoints', [])
                        ],
                        dependencies=[
                            ServiceDependency(
                                service_name=dep['service_name'],
                                service_type=ServiceType(dep['service_type']),
                                protocol=CommunicationProtocol(dep['protocol']),
                                endpoint_url=dep['endpoint_url'],
                                timeout_seconds=dep.get('timeout_seconds', 30),
                                retry_attempts=dep.get('retry_attempts', 3),
                                circuit_breaker_enabled=dep.get('circuit_breaker_enabled', True),
                                fallback_enabled=dep.get('fallback_enabled', True),
                                health_check_path=dep.get('health_check_path', '/health')
                            ) for dep in service_data.get('dependencies', [])
                        ],
                        environment_variables=service_data.get('environment_variables', {}),
                        resource_limits=service_data.get('resource_limits', {}),
                        resource_requests=service_data.get('resource_requests', {}),
                        health_check_enabled=service_data.get('health_check_enabled', True),
                        metrics_enabled=service_data.get('metrics_enabled', True),
                        logging_enabled=service_data.get('logging_enabled', True),
                        tracing_enabled=service_data.get('tracing_enabled', True),
                        auto_scaling_enabled=service_data.get('auto_scaling_enabled', True),
                        min_replicas=service_data.get('min_replicas', 2),
                        max_replicas=service_data.get('max_replicas', 10),
                        target_cpu_utilization=service_data.get('target_cpu_utilization', 70),
                        service_mesh_enabled=service_data.get('service_mesh_enabled', True)
                    )
                    self.services[service_config.service_name] = service_config
                
                # Load service mesh configuration
                mesh_config = config_data.get('service_mesh', {})
                if mesh_config:
                    self.service_mesh_config = ServiceMeshConfiguration(
                        mesh_type=ServiceMeshType(mesh_config.get('mesh_type', 'istio')),
                        mtls_enabled=mesh_config.get('mtls_enabled', True),
                        traffic_management_enabled=mesh_config.get('traffic_management_enabled', True),
                        security_policies_enabled=mesh_config.get('security_policies_enabled', True),
                        observability_enabled=mesh_config.get('observability_enabled', True),
                        canary_deployments_enabled=mesh_config.get('canary_deployments_enabled', True),
                        circuit_breaker_enabled=mesh_config.get('circuit_breaker_enabled', True),
                        retry_policies_enabled=mesh_config.get('retry_policies_enabled', True),
                        timeout_policies_enabled=mesh_config.get('timeout_policies_enabled', True),
                        rate_limiting_enabled=mesh_config.get('rate_limiting_enabled', True),
                        load_balancing_strategy=LoadBalancingStrategy(mesh_config.get('load_balancing_strategy', 'round_robin'))
                    )
                
                # Load API gateway configuration
                gateway_config = config_data.get('api_gateway', {})
                if gateway_config:
                    self.api_gateway_config = APIGatewayConfiguration(
                        gateway_name=gateway_config.get('gateway_name', 'ia-influencer-gateway'),
                        port=gateway_config.get('port', 80),
                        ssl_port=gateway_config.get('ssl_port', 443),
                        ssl_enabled=gateway_config.get('ssl_enabled', True),
                        rate_limiting_enabled=gateway_config.get('rate_limiting_enabled', True),
                        authentication_enabled=gateway_config.get('authentication_enabled', True),
                        authorization_enabled=gateway_config.get('authorization_enabled', True),
                        request_logging_enabled=gateway_config.get('request_logging_enabled', True),
                        response_caching_enabled=gateway_config.get('response_caching_enabled', True),
                        compression_enabled=gateway_config.get('compression_enabled', True),
                        cors_enabled=gateway_config.get('cors_enabled', True),
                        load_balancing_strategy=LoadBalancingStrategy(gateway_config.get('load_balancing_strategy', 'round_robin')),
                        health_checks_enabled=gateway_config.get('health_checks_enabled', True),
                        circuit_breaker_enabled=gateway_config.get('circuit_breaker_enabled', True)
                    )
                
                logger.info(f"Loaded {len(self.services)} service configurations")
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
        else:
            # Create default configurations for core services
            self._create_default_service_configurations()
    
    def _create_default_service_configurations(self):
        """Create default configurations for core microservices"""
        core_services = [
            {
                'name': 'api-gateway',
                'type': ServiceType.API_GATEWAY,
                'port': 8080,
                'namespace': 'gateway'
            },
            {
                'name': 'content-protection',
                'type': ServiceType.CONTENT_PROTECTION,
                'port': 8081,
                'namespace': 'content'
            },
            {
                'name': 'ai-fingerprinting',
                'type': ServiceType.AI_FINGERPRINTING,
                'port': 8082,
                'namespace': 'ai'
            },
            {
                'name': 'content-crawler',
                'type': ServiceType.CONTENT_CRAWLER,
                'port': 8083,
                'namespace': 'crawlers'
            },
            {
                'name': 'licensing-manager',
                'type': ServiceType.LICENSING_MANAGER,
                'port': 8084,
                'namespace': 'licensing'
            },
            {
                'name': 'revenue-manager',
                'type': ServiceType.REVENUE_MANAGER,
                'port': 8085,
                'namespace': 'revenue'
            },
            {
                'name': 'user-manager',
                'type': ServiceType.USER_MANAGER,
                'port': 8086,
                'namespace': 'users'
            },
            {
                'name': 'notification-service',
                'type': ServiceType.NOTIFICATION_SERVICE,
                'port': 8087,
                'namespace': 'notifications'
            },
            {
                'name': 'analytics-service',
                'type': ServiceType.ANALYTICS_SERVICE,
                'port': 8088,
                'namespace': 'analytics'
            },
            {
                'name': 'payment-service',
                'type': ServiceType.PAYMENT_SERVICE,
                'port': 8089,
                'namespace': 'payments'
            }
        ]
        
        for service_def in core_services:
            service_config = ServiceConfiguration(
                service_name=service_def['name'],
                service_type=service_def['type'],
                version='1.0.0',
                namespace=service_def['namespace'],
                port=service_def['port']
            )
            self.services[service_config.service_name] = service_config
        
        logger.info(f"Created {len(core_services)} default service configurations")
    
    def deploy_microservices_infrastructure(self) -> bool:
        """Deploy complete microservices infrastructure"""
        if not self.k8s_client:
            logger.error("Kubernetes client not available")
            return False
        
        try:
            # Create namespaces for different service groups
            self._create_service_namespaces()
            
            # Deploy service mesh (Istio)
            if self.service_mesh_config.mesh_type == ServiceMeshType.ISTIO:
                self._deploy_istio_service_mesh()
            
            # Deploy service discovery (Consul)
            self._deploy_service_discovery()
            
            # Deploy API Gateway
            self._deploy_api_gateway()
            
            # Deploy Redis for service coordination
            self._deploy_redis_cluster()
            
            # Deploy individual microservices
            for service_name, service_config in self.services.items():
                self._deploy_microservice(service_config)
            
            # Configure service mesh policies
            self._configure_service_mesh_policies()
            
            # Deploy monitoring and observability
            self._deploy_microservices_monitoring()
            
            # Configure inter-service communication
            self._configure_inter_service_communication()
            
            logger.info("Microservices infrastructure deployed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy microservices infrastructure: {e}")
            return False
    
    def _create_service_namespaces(self):
        """Create namespaces for service groups"""
        namespaces = set()
        for service_config in self.services.values():
            namespaces.add(service_config.namespace)
        
        # Add infrastructure namespaces
        namespaces.update(['istio-system', 'consul', 'monitoring', 'gateway'])
        
        for namespace in namespaces:
            self._create_namespace(namespace)
    
    def _deploy_istio_service_mesh(self):
        """Deploy Istio service mesh"""
        # Install Istio control plane
        istio_namespace = "istio-system"
        self._create_namespace(istio_namespace)
        
        # Istio control plane components
        istio_components = [
            {
                'name': 'istiod',
                'image': 'docker.io/istio/pilot:1.17.0',
                'ports': [15010, 15011, 15014]
            },
            {
                'name': 'istio-proxy',
                'image': 'docker.io/istio/proxyv2:1.17.0',
                'ports': [15000, 15001, 15006, 15090]
            }
        ]
        
        for component in istio_components:
            deployment_manifest = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": component['name'],
                    "namespace": istio_namespace,
                    "labels": {
                        "app": component['name'],
                        "istio": "pilot"
                    }
                },
                "spec": {
                    "replicas": 1,
                    "selector": {
                        "matchLabels": {
                            "app": component['name']
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": component['name']
                            }
                        },
                        "spec": {
                            "containers": [{
                                "name": component['name'],
                                "image": component['image'],
                                "ports": [{"containerPort": port} for port in component['ports']],
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
                            }]
                        }
                    }
                }
            }
            
            try:
                self.apps_v1.create_namespaced_deployment(
                    namespace=istio_namespace,
                    body=deployment_manifest
                )
                logger.info(f"Deployed Istio component: {component['name']}")
            except ApiException as e:
                if e.status == 409:  # Already exists
                    logger.info(f"Istio component {component['name']} already exists")
        
        logger.info("Istio service mesh deployed")
    
    def _deploy_service_discovery(self):
        """Deploy Consul for service discovery"""
        consul_namespace = "consul"
        self._create_namespace(consul_namespace)
        
        consul_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "consul-server",
                "namespace": consul_namespace
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "consul-server"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "consul-server"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "consul",
                            "image": "consul:1.15",
                            "ports": [
                                {"containerPort": 8500, "name": "http"},
                                {"containerPort": 8600, "name": "dns"}
                            ],
                            "args": [
                                "agent",
                                "-server",
                                "-bootstrap-expect=1",
                                "-ui",
                                "-bind=0.0.0.0",
                                "-client=0.0.0.0"
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": "100m",
                                    "memory": "256Mi"
                                },
                                "limits": {
                                    "cpu": "500m",
                                    "memory": "1Gi"
                                }
                            }
                        }]
                    }
                }
            }
        }
        
        self.apps_v1.create_namespaced_deployment(
            namespace=consul_namespace,
            body=consul_deployment
        )
        
        # Create Consul service
        consul_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "consul-service",
                "namespace": consul_namespace
            },
            "spec": {
                "selector": {
                    "app": "consul-server"
                },
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": 8500,
                        "targetPort": 8500,
                        "name": "http"
                    },
                    {
                        "protocol": "TCP",
                        "port": 8600,
                        "targetPort": 8600,
                        "name": "dns"
                    }
                ],
                "type": "ClusterIP"
            }
        }
        
        self.core_v1.create_namespaced_service(
            namespace=consul_namespace,
            body=consul_service
        )
        
        logger.info("Consul service discovery deployed")
    
    def _deploy_api_gateway(self):
        """Deploy API Gateway"""
        gateway_namespace = "gateway"
        self._create_namespace(gateway_namespace)
        
        # Deploy Kong or similar API Gateway
        api_gateway_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "api-gateway",
                "namespace": gateway_namespace
            },
            "spec": {
                "replicas": 3,
                "selector": {
                    "matchLabels": {
                        "app": "api-gateway"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "api-gateway"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "kong",
                            "image": "kong:3.2",
                            "ports": [
                                {"containerPort": 8000, "name": "proxy"},
                                {"containerPort": 8443, "name": "proxy-ssl"},
                                {"containerPort": 8001, "name": "admin"},
                                {"containerPort": 8444, "name": "admin-ssl"}
                            ],
                            "env": [
                                {"name": "KONG_DATABASE", "value": "off"},
                                {"name": "KONG_DECLARATIVE_CONFIG", "value": "/kong/declarative/kong.yml"},
                                {"name": "KONG_PROXY_ACCESS_LOG", "value": "/dev/stdout"},
                                {"name": "KONG_ADMIN_ACCESS_LOG", "value": "/dev/stdout"},
                                {"name": "KONG_PROXY_ERROR_LOG", "value": "/dev/stderr"},
                                {"name": "KONG_ADMIN_ERROR_LOG", "value": "/dev/stderr"},
                                {"name": "KONG_ADMIN_LISTEN", "value": "0.0.0.0:8001"}
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": "200m",
                                    "memory": "512Mi"
                                },
                                "limits": {
                                    "cpu": "1000m",
                                    "memory": "2Gi"
                                }
                            },
                            "volumeMounts": [{
                                "name": "kong-config",
                                "mountPath": "/kong/declarative/"
                            }]
                        }],
                        "volumes": [{
                            "name": "kong-config",
                            "configMap": {
                                "name": "kong-declarative-config"
                            }
                        }]
                    }
                }
            }
        }
        
        self.apps_v1.create_namespaced_deployment(
            namespace=gateway_namespace,
            body=api_gateway_deployment
        )
        
        # Create API Gateway service
        gateway_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "api-gateway-service",
                "namespace": gateway_namespace
            },
            "spec": {
                "selector": {
                    "app": "api-gateway"
                },
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": 80,
                        "targetPort": 8000,
                        "name": "proxy"
                    },
                    {
                        "protocol": "TCP",
                        "port": 443,
                        "targetPort": 8443,
                        "name": "proxy-ssl"
                    }
                ],
                "type": "LoadBalancer"
            }
        }
        
        self.core_v1.create_namespaced_service(
            namespace=gateway_namespace,
            body=gateway_service
        )
        
        # Create Kong configuration
        self._create_kong_configuration()
        
        logger.info("API Gateway deployed")
    
    def _create_kong_configuration(self):
        """Create Kong declarative configuration"""
        kong_config = {
            "_format_version": "3.0",
            "_transform": True,
            "services": [],
            "routes": [],
            "plugins": [
                {
                    "name": "rate-limiting",
                    "config": {
                        "minute": 100,
                        "hour": 1000
                    }
                },
                {
                    "name": "cors",
                    "config": {
                        "origins": ["*"],
                        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                        "headers": ["Authorization", "Content-Type"]
                    }
                }
            ]
        }
        
        # Add services and routes for each microservice
        for service_name, service_config in self.services.items():
            # Add service definition
            kong_service = {
                "name": service_name,
                "url": f"http://{service_name}-service.{service_config.namespace}:{service_config.port}"
            }
            kong_config["services"].append(kong_service)
            
            # Add routes for each endpoint
            for endpoint in service_config.endpoints:
                route = {
                    "name": f"{service_name}-{endpoint.path.replace('/', '-')}",
                    "service": {"name": service_name},
                    "paths": [f"/{service_name}{endpoint.path}"],
                    "methods": [endpoint.method]
                }
                kong_config["routes"].append(route)
        
        # Create ConfigMap for Kong configuration
        kong_configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "kong-declarative-config",
                "namespace": "gateway"
            },
            "data": {
                "kong.yml": yaml.dump(kong_config)
            }
        }
        
        try:
            self.core_v1.create_namespaced_config_map(
                namespace="gateway",
                body=kong_configmap
            )
        except ApiException as e:
            if e.status == 409:  # Already exists
                self.core_v1.patch_namespaced_config_map(
                    name="kong-declarative-config",
                    namespace="gateway",
                    body=kong_configmap
                )
        
        logger.info("Kong configuration created")
    
    def _deploy_redis_cluster(self):
        """Deploy Redis cluster for service coordination"""
        redis_namespace = "redis"
        self._create_namespace(redis_namespace)
        
        redis_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "redis-cluster",
                "namespace": redis_namespace
            },
            "spec": {
                "replicas": 3,
                "selector": {
                    "matchLabels": {
                        "app": "redis-cluster"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "redis-cluster"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "redis",
                            "image": "redis:7-alpine",
                            "ports": [{"containerPort": 6379}],
                            "args": ["--cluster-enabled", "yes", "--cluster-config-file", "nodes.conf"],
                            "resources": {
                                "requests": {
                                    "cpu": "100m",
                                    "memory": "256Mi"
                                },
                                "limits": {
                                    "cpu": "500m",
                                    "memory": "1Gi"
                                }
                            }
                        }]
                    }
                }
            }
        }
        
        self.apps_v1.create_namespaced_deployment(
            namespace=redis_namespace,
            body=redis_deployment
        )
        
        logger.info("Redis cluster deployed")
    
    def _deploy_microservice(self, service_config: ServiceConfiguration):
        """Deploy individual microservice"""
        # Create namespace if not exists
        self._create_namespace(service_config.namespace)
        
        # Create deployment
        deployment_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": service_config.service_name,
                "namespace": service_config.namespace,
                "labels": {
                    "app": service_config.service_name,
                    "version": service_config.version,
                    "service-type": service_config.service_type.value
                }
            },
            "spec": {
                "replicas": service_config.replicas,
                "selector": {
                    "matchLabels": {
                        "app": service_config.service_name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": service_config.service_name,
                            "version": service_config.version
                        },
                        "annotations": {
                            "sidecar.istio.io/inject": "true" if service_config.service_mesh_enabled else "false"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": service_config.service_name,
                            "image": f"ia-influencer/{service_config.service_name}:{service_config.version}",
                            "ports": [
                                {
                                    "containerPort": service_config.port,
                                    "name": "http"
                                },
                                {
                                    "containerPort": service_config.management_port,
                                    "name": "management"
                                }
                            ],
                            "env": [
                                {"name": "SERVICE_NAME", "value": service_config.service_name},
                                {"name": "SERVICE_VERSION", "value": service_config.version},
                                {"name": "SERVICE_PORT", "value": str(service_config.port)},
                                {"name": "MANAGEMENT_PORT", "value": str(service_config.management_port)}
                            ] + [
                                {"name": k, "value": v}
                                for k, v in service_config.environment_variables.items()
                            ],
                            "resources": {
                                "requests": service_config.resource_requests,
                                "limits": service_config.resource_limits
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": service_config.management_port
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            } if service_config.health_check_enabled else None,
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/ready",
                                    "port": service_config.management_port
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            } if service_config.health_check_enabled else None
                        }]
                    }
                }
            }
        }
        
        # Remove None values
        deployment_manifest = self._remove_none_values(deployment_manifest)
        
        try:
            self.apps_v1.create_namespaced_deployment(
                namespace=service_config.namespace,
                body=deployment_manifest
            )
        except ApiException as e:
            if e.status == 409:  # Already exists
                self.apps_v1.patch_namespaced_deployment(
                    name=service_config.service_name,
                    namespace=service_config.namespace,
                    body=deployment_manifest
                )
        
        # Create service
        service_manifest = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{service_config.service_name}-service",
                "namespace": service_config.namespace,
                "labels": {
                    "app": service_config.service_name
                }
            },
            "spec": {
                "selector": {
                    "app": service_config.service_name
                },
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": service_config.port,
                        "targetPort": service_config.port,
                        "name": "http"
                    },
                    {
                        "protocol": "TCP",
                        "port": service_config.management_port,
                        "targetPort": service_config.management_port,
                        "name": "management"
                    }
                ],
                "type": "ClusterIP"
            }
        }
        
        try:
            self.core_v1.create_namespaced_service(
                namespace=service_config.namespace,
                body=service_manifest
            )
        except ApiException as e:
            if e.status == 409:  # Already exists
                logger.info(f"Service {service_config.service_name}-service already exists")
        
        # Create HPA if auto-scaling is enabled
        if service_config.auto_scaling_enabled:
            self._create_horizontal_pod_autoscaler(service_config)
        
        # Register with service discovery
        self._register_service_with_discovery(service_config)
        
        logger.info(f"Deployed microservice: {service_config.service_name}")
    
    def _create_horizontal_pod_autoscaler(self, service_config: ServiceConfiguration):
        """Create Horizontal Pod Autoscaler for microservice"""
        hpa_manifest = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{service_config.service_name}-hpa",
                "namespace": service_config.namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": service_config.service_name
                },
                "minReplicas": service_config.min_replicas,
                "maxReplicas": service_config.max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": service_config.target_cpu_utilization
                            }
                        }
                    }
                ]
            }
        }
        
        try:
            # Use custom objects API for HPA v2
            self.custom_objects_api.create_namespaced_custom_object(
                group="autoscaling",
                version="v2",
                namespace=service_config.namespace,
                plural="horizontalpodautoscalers",
                body=hpa_manifest
            )
            logger.info(f"Created HPA for {service_config.service_name}")
        except ApiException as e:
            if e.status == 409:  # Already exists
                logger.info(f"HPA for {service_config.service_name} already exists")
    
    def _register_service_with_discovery(self, service_config: ServiceConfiguration):
        """Register service with service discovery system"""
        if self.consul_client:
            try:
                self.consul_client.agent.service.register(
                    name=service_config.service_name,
                    service_id=f"{service_config.service_name}-{service_config.version}",
                    address=f"{service_config.service_name}-service.{service_config.namespace}.svc.cluster.local",
                    port=service_config.port,
                    tags=[
                        service_config.service_type.value,
                        service_config.version,
                        service_config.namespace
                    ],
                    check=consul.Check.http(
                        f"http://{service_config.service_name}-service.{service_config.namespace}:{service_config.management_port}/health",
                        interval="10s",
                        timeout="5s"
                    ) if service_config.health_check_enabled else None
                )
                logger.info(f"Registered {service_config.service_name} with Consul")
            except Exception as e:
                logger.warning(f"Failed to register {service_config.service_name} with Consul: {e}")
    
    def _configure_service_mesh_policies(self):
        """Configure service mesh policies (Istio)"""
        if self.service_mesh_config.mesh_type != ServiceMeshType.ISTIO:
            return
        
        # Istio configuration manifests would be applied here
        # This is a simplified version - real implementation would create
        # DestinationRules, VirtualServices, PeerAuthentication, etc.
        
        logger.info("Service mesh policies configured")
    
    def _deploy_microservices_monitoring(self):
        """Deploy monitoring for microservices"""
        # This would deploy Prometheus, Grafana, Jaeger for monitoring
        # Implementation depends on existing monitoring infrastructure
        logger.info("Microservices monitoring deployed")
    
    def _configure_inter_service_communication(self):
        """Configure communication patterns between services"""
        # Configure service-to-service authentication, authorization, etc.
        logger.info("Inter-service communication configured")
    
    def _remove_none_values(self, obj):
        """Recursively remove None values from dictionary"""
        if isinstance(obj, dict):
            return {k: self._remove_none_values(v) for k, v in obj.items() if v is not None}
        elif isinstance(obj, list):
            return [self._remove_none_values(item) for item in obj if item is not None]
        else:
            return obj
    
    def _create_namespace(self, namespace: str):
        """Create Kubernetes namespace if it doesn't exist"""



        try:
            self.core_v1.read_namespace(name=namespace)
        except ApiException as e:
            if e.status == 404:
                namespace_manifest = {
                    "apiVersion": "v1",
                    "kind": "Namespace",
                    "metadata": {"name": namespace}
                }
                self.core_v1.create_namespace(body=namespace_manifest)
                logger.info(f"Created namespace: {namespace}")
    
    def scale_microservice(self, service_name: str, replicas: int) -> bool:
        """Scale microservice to specified number of replicas"""
        if service_name not in self.services:
            logger.error(f"Service {service_name} not found")
            return False
        
        service_config = self.services[service_name]
        
        try:
            # Update deployment replicas
            deployment = self.apps_v1.read_namespaced_deployment(
                name=service_name,
                namespace=service_config.namespace
            )
            deployment.spec.replicas = replicas
            
            self.apps_v1.patch_namespaced_deployment(
                name=service_name,
                namespace=service_config.namespace,
                body=deployment
            )
            
            logger.info(f"Scaled {service_name} to {replicas} replicas")
            return True
            
        except Exception as e:
            logger.error(f"Failed to scale {service_name}: {e}")
            return False
    
    def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get health status of microservice"""
        if service_name not in self.services:
            return {"error": f"Service {service_name} not found"}
        
        service_config = self.services[service_name]
        
        try:
            # Get deployment status
            deployment = self.apps_v1.read_namespaced_deployment(
                name=service_name,
                namespace=service_config.namespace
            )
            
            # Get pod status
            pods = self.core_v1.list_namespaced_pod(
                namespace=service_config.namespace,
                label_selector=f"app={service_name}"
            )
            
            health_status = {
                "service_name": service_name,
                "namespace": service_config.namespace,
                "desired_replicas": deployment.spec.replicas,
                "ready_replicas": deployment.status.ready_replicas or 0,
                "available_replicas": deployment.status.available_replicas or 0,
                "pods": []
            }
            
            for pod in pods.items:
                pod_status = {
                    "name": pod.metadata.name,
                    "phase": pod.status.phase,
                    "ready": all(condition.status == "True" for condition in pod.status.conditions if condition.type == "Ready"),
                    "restart_count": sum(container.restart_count for container in pod.status.container_statuses or [])
                }
                health_status["pods"].append(pod_status)
            
            return health_status
            
        except Exception as e:
            logger.error(f"Failed to get health status for {service_name}: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'infrastructure': {
                'kubernetes': self.k8s_client is not None,
                'docker': self.docker_client is not None,
                'consul': self.consul_client is not None,
                'etcd': self.etcd_client is not None,
                'redis': self.redis_client is not None,
                'database': self.db_engine is not None
            },
            'service_mesh': {
                'enabled': self.service_mesh_config.mesh_type is not None,
                'type': self.service_mesh_config.mesh_type.value if self.service_mesh_config.mesh_type else None,
                'mtls_enabled': self.service_mesh_config.mtls_enabled
            },
            'services': {},
            'api_gateway': {
                'deployed': True,  # Would check actual status
                'name': self.api_gateway_config.gateway_name
            }
        }
        
        # Check service health
        for service_name in self.services:
            service_health = self.get_service_health(service_name)
            health_status['services'][service_name] = service_health
        
        # Check overall infrastructure health
        unhealthy_components = [k for k, v in health_status['infrastructure'].items() if not v]
        if unhealthy_components:
            health_status['overall_status'] = 'degraded'
            health_status['issues'] = f"Unhealthy infrastructure components: {', '.join(unhealthy_components)}"
        
        # Check for unhealthy services
        unhealthy_services = [
            name for name, status in health_status['services'].items()
            if 'error' in status or (status.get('ready_replicas', 0) < status.get('desired_replicas', 1))
        ]
        if unhealthy_services:
            health_status['overall_status'] = 'degraded'
            health_status['unhealthy_services'] = unhealthy_services
        
        return health_status


def main():
    """Main function for testing the Microservices Deployment Manager"""
    # Initialize manager
    manager = MicroservicesDeploymentManager()
    
    # Deploy microservices infrastructure
    if manager.deploy_microservices_infrastructure():
        print(" Microservices infrastructure deployed successfully")
    
    # Example: Scale a service
    if manager.scale_microservice("content-protection", 5):
        print(" Content protection service scaled to 5 replicas")
    
    # Check health of a specific service
    health = manager.get_service_health("api-gateway")
    print(f" API Gateway health: {health.get('ready_replicas', 0)}/{health.get('desired_replicas', 0)} replicas ready")
    
    # Overall health check
    overall_health = manager.health_check()
    print(f" Overall microservices health: {overall_health['overall_status']}")
    print(f"   - Services deployed: {len(overall_health['services'])}")
    print(f"   - Service mesh enabled: {overall_health['service_mesh']['enabled']}")
    
    print("\n Microservices Deployment Manager test completed")


if __name__ == "__main__":
    main()
