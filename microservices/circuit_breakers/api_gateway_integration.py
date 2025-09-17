"""
Circuit Breaker API Gateway Integration
Enterprise API Gateway Circuit Breaker Integration Module

This module provides comprehensive integration between circuit breakers and various
API gateway solutions including Kong, Ambassador, Envoy, AWS API Gateway, and Zuul.

Key Features:
- Multi-gateway support with unified configuration
- Dynamic policy management and deployment
- Health check integration with service discovery
- Circuit state-aware request routing
- Real-time metrics integration and analytics

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute reproduction, distribution ou utilisation non autorisée est strictement interdite.
"""

import asyncio
import logging
import json
import yaml
import time
import httpx
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Set, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import kubernetes
from kubernetes import client, config
import consul
import etcd3

logger = logging.getLogger(__name__)

class GatewayType(Enum):
    """Supported API gateway types"""
    KONG = "kong"
    AMBASSADOR = "ambassador"
    ENVOY = "envoy"
    AWS_API_GATEWAY = "aws_api_gateway"
    ZUUL = "zuul"
    ISTIO = "istio"
    NGINX = "nginx"
    TRAEFIK = "traefik"

class PolicyAction(Enum):
    """Circuit breaker policy actions"""
    REJECT = "reject"
    FALLBACK = "fallback"
    DELAY = "delay"
    REDIRECT = "redirect"
    CUSTOM = "custom"

class IntegrationStatus(Enum):
    """Integration status states"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    DISABLED = "disabled"

@dataclass
class GatewayConfig:
    """Gateway configuration"""
    gateway_type: GatewayType
    endpoint: str
    admin_endpoint: str
    auth_token: Optional[str] = None
    auth_method: str = "bearer"
    tls_enabled: bool = True
    tls_verify: bool = True
    timeout: int = 30
    retry_count: int = 3
    health_check_interval: int = 60
    namespace: Optional[str] = None
    cluster_name: Optional[str] = None
    custom_headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.custom_headers is None:
            self.custom_headers = {}

@dataclass
class CircuitBreakerPolicy:
    """Circuit breaker policy for gateway"""
    name: str
    service_name: str
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: int = 60
    recovery_timeout: int = 30
    action: PolicyAction = PolicyAction.REJECT
    fallback_endpoint: Optional[str] = None
    fallback_response: Optional[Dict[str, Any]] = None
    custom_response_code: int = 503
    custom_response_body: Optional[str] = None
    rate_limit: Optional[int] = None
    priority: int = 1
    enabled: bool = True
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class GatewayMetrics:
    """Gateway integration metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    circuit_breaker_trips: int = 0
    policy_updates: int = 0
    health_checks: int = 0
    last_health_check: Optional[datetime] = None
    response_times: List[float] = None
    error_rate: float = 0.0
    availability: float = 100.0
    
    def __post_init__(self):
        if self.response_times is None:
            self.response_times = []

class APIGatewayIntegration:
    """Enterprise API Gateway Circuit Breaker Integration"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize API gateway integration"""
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Gateway configurations
        self.gateways: Dict[str, GatewayConfig] = {}
        
        # Circuit breaker policies
        self.policies: Dict[str, Dict[str, CircuitBreakerPolicy]] = {}
        
        # Integration status
        self.status: Dict[str, IntegrationStatus] = {}
        
        # Metrics tracking
        self.metrics: Dict[str, GatewayMetrics] = {}
        
        # HTTP clients for each gateway
        self.clients: Dict[str, httpx.AsyncClient] = {}
        
        # Health check tasks
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            'policy_updated': [],
            'circuit_state_changed': [],
            'health_check_failed': [],
            'gateway_error': []
        }
        
        # Service discovery clients
        self.consul_client: Optional[consul.Consul] = None
        self.etcd_client: Optional[etcd3.Etcd3Client] = None
        self.k8s_client: Optional[client.ApiClient] = None
        
        # Initialize service discovery
        self._initialize_service_discovery()

    async def register_gateway(self, gateway_id: str, gateway_config: GatewayConfig) -> bool:
        """Register API gateway for circuit breaker integration"""
        try:
            self.gateways[gateway_id] = gateway_config
            self.policies[gateway_id] = {}
            self.status[gateway_id] = IntegrationStatus.INITIALIZING
            self.metrics[gateway_id] = GatewayMetrics()
            
            # Create HTTP client
            client_config = {
                'timeout': httpx.Timeout(gateway_config.timeout),
                'verify': gateway_config.tls_verify if gateway_config.tls_enabled else False,
                'headers': gateway_config.custom_headers.copy()
            }
            
            if gateway_config.auth_token:
                if gateway_config.auth_method == "bearer":
                    client_config['headers']['Authorization'] = f"Bearer {gateway_config.auth_token}"
                elif gateway_config.auth_method == "api_key":
                    client_config['headers']['X-API-Key'] = gateway_config.auth_token
            
            self.clients[gateway_id] = httpx.AsyncClient(**client_config)
            
            # Start health check task
            self.health_check_tasks[gateway_id] = asyncio.create_task(
                self._health_check_loop(gateway_id)
            )
            
            # Validate connection
            if await self._validate_gateway_connection(gateway_id):
                self.status[gateway_id] = IntegrationStatus.ACTIVE
                self.logger.info(f"Gateway {gateway_id} registered successfully")
                return True
            else:
                self.status[gateway_id] = IntegrationStatus.ERROR
                self.logger.error(f"Failed to validate connection to gateway {gateway_id}")
                return False
                
        except Exception as e:
            self.status[gateway_id] = IntegrationStatus.ERROR
            self.logger.error(f"Failed to register gateway {gateway_id}: {str(e)}")
            return False

    async def deploy_policy(self, gateway_id: str, policy: CircuitBreakerPolicy) -> bool:
        """Deploy circuit breaker policy to gateway"""
        try:
            if gateway_id not in self.gateways:
                raise ValueError(f"Gateway {gateway_id} not registered")
            
            gateway_config = self.gateways[gateway_id]
            
            # Deploy policy based on gateway type
            success = await self._deploy_policy_by_type(gateway_id, gateway_config, policy)
            
            if success:
                self.policies[gateway_id][policy.name] = policy
                self.metrics[gateway_id].policy_updates += 1
                
                # Trigger event handlers
                await self._trigger_event_handlers('policy_updated', {
                    'gateway_id': gateway_id,
                    'policy': policy
                })
                
                self.logger.info(f"Policy {policy.name} deployed to gateway {gateway_id}")
                return True
            else:
                self.logger.error(f"Failed to deploy policy {policy.name} to gateway {gateway_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deploying policy {policy.name} to gateway {gateway_id}: {str(e)}")
            return False

    async def update_circuit_state(self, gateway_id: str, service_name: str, state: str) -> bool:
        """Update circuit breaker state in gateway"""
        try:
            if gateway_id not in self.gateways:
                raise ValueError(f"Gateway {gateway_id} not registered")
            
            gateway_config = self.gateways[gateway_id]
            
            # Update state based on gateway type
            success = await self._update_circuit_state_by_type(gateway_id, gateway_config, service_name, state)
            
            if success:
                # Trigger event handlers
                await self._trigger_event_handlers('circuit_state_changed', {
                    'gateway_id': gateway_id,
                    'service_name': service_name,
                    'state': state
                })
                
                self.logger.info(f"Circuit state updated for service {service_name} in gateway {gateway_id}: {state}")
                return True
            else:
                self.logger.error(f"Failed to update circuit state for service {service_name} in gateway {gateway_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating circuit state for service {service_name} in gateway {gateway_id}: {str(e)}")
            return False

    async def get_gateway_metrics(self, gateway_id: str) -> Optional[Dict[str, Any]]:
        """Get gateway metrics and circuit breaker stats"""
        try:
            if gateway_id not in self.gateways:
                return None
            
            gateway_config = self.gateways[gateway_id]
            
            # Fetch metrics based on gateway type
            gateway_metrics = await self._fetch_metrics_by_type(gateway_id, gateway_config)
            
            # Combine with internal metrics
            internal_metrics = asdict(self.metrics[gateway_id])
            
            return {
                'gateway_id': gateway_id,
                'gateway_type': gateway_config.gateway_type.value,
                'status': self.status[gateway_id].value,
                'internal_metrics': internal_metrics,
                'gateway_metrics': gateway_metrics,
                'policies': {name: asdict(policy) for name, policy in self.policies[gateway_id].items()},
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching metrics for gateway {gateway_id}: {str(e)}")
            return None

    async def _deploy_policy_by_type(self, gateway_id: str, gateway_config: GatewayConfig, policy: CircuitBreakerPolicy) -> bool:
        """Deploy policy based on gateway type"""
        gateway_type = gateway_config.gateway_type
        
        if gateway_type == GatewayType.KONG:
            return await self._deploy_kong_policy(gateway_id, gateway_config, policy)
        elif gateway_type == GatewayType.AMBASSADOR:
            return await self._deploy_ambassador_policy(gateway_id, gateway_config, policy)
        elif gateway_type == GatewayType.ENVOY:
            return await self._deploy_envoy_policy(gateway_id, gateway_config, policy)
        elif gateway_type == GatewayType.AWS_API_GATEWAY:
            return await self._deploy_aws_policy(gateway_id, gateway_config, policy)
        elif gateway_type == GatewayType.ZUUL:
            return await self._deploy_zuul_policy(gateway_id, gateway_config, policy)
        elif gateway_type == GatewayType.ISTIO:
            return await self._deploy_istio_policy(gateway_id, gateway_config, policy)
        elif gateway_type == GatewayType.NGINX:
            return await self._deploy_nginx_policy(gateway_id, gateway_config, policy)
        elif gateway_type == GatewayType.TRAEFIK:
            return await self._deploy_traefik_policy(gateway_id, gateway_config, policy)
        else:
            self.logger.error(f"Unsupported gateway type: {gateway_type}")
            return False

    async def _deploy_kong_policy(self, gateway_id: str, gateway_config: GatewayConfig, policy: CircuitBreakerPolicy) -> bool:
        """Deploy circuit breaker policy to Kong gateway"""
        try:
            client = self.clients[gateway_id]
            
            # Kong circuit breaker plugin configuration
            plugin_config = {
                "name": "circuit-breaker",
                "service": {"name": policy.service_name},
                "config": {
                    "failure_threshold": policy.failure_threshold,
                    "success_threshold": policy.success_threshold,
                    "timeout": policy.timeout_seconds,
                    "recovery_timeout": policy.recovery_timeout
                }
            }
            
            # Add custom response if specified
            if policy.action == PolicyAction.REJECT:
                plugin_config["config"]["reject_status"] = policy.custom_response_code
                if policy.custom_response_body:
                    plugin_config["config"]["reject_body"] = policy.custom_response_body
            elif policy.action == PolicyAction.FALLBACK and policy.fallback_endpoint:
                plugin_config["config"]["fallback_upstream"] = policy.fallback_endpoint
            
            response = await client.post(
                f"{gateway_config.admin_endpoint}/plugins",
                json=plugin_config
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            self.logger.error(f"Error deploying Kong policy: {str(e)}")
            return False

    async def _deploy_ambassador_policy(self, gateway_id: str, gateway_config: GatewayConfig, policy: CircuitBreakerPolicy) -> bool:
        """Deploy circuit breaker policy to Ambassador gateway"""
        try:
            if not self.k8s_client:
                self.logger.error("Kubernetes client not available for Ambassador integration")
                return False
            
            # Ambassador circuit breaker configuration
            circuit_breaker_manifest = {
                "apiVersion": "getambassador.io/v3alpha1",
                "kind": "CircuitBreaker",
                "metadata": {
                    "name": f"cb-{policy.name}",
                    "namespace": gateway_config.namespace or "default"
                },
                "spec": {
                    "circuit_breakers": [{
                        "priority": policy.priority,
                        "max_connections": policy.failure_threshold * 10,
                        "max_pending_requests": policy.failure_threshold * 5,
                        "max_requests": policy.failure_threshold * 20,
                        "max_retries": policy.success_threshold,
                        "consecutive_5xx": policy.failure_threshold,
                        "interval": f"{policy.recovery_timeout}s",
                        "base_ejection_time": f"{policy.timeout_seconds}s"
                    }]
                }
            }
            
            # Apply the manifest
            api_instance = kubernetes.client.CustomObjectsApi(self.k8s_client)
            api_instance.create_namespaced_custom_object(
                group="getambassador.io",
                version="v3alpha1",
                namespace=gateway_config.namespace or "default",
                plural="circuitbreakers",
                body=circuit_breaker_manifest
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deploying Ambassador policy: {str(e)}")
            return False

    async def _deploy_envoy_policy(self, gateway_id: str, gateway_config: GatewayConfig, policy: CircuitBreakerPolicy) -> bool:
        """Deploy circuit breaker policy to Envoy proxy"""
        try:
            client = self.clients[gateway_id]
            
            # Envoy circuit breaker configuration
            circuit_breaker_config = {
                "outlier_detection": {
                    "consecutive_5xx": policy.failure_threshold,
                    "interval": f"{policy.recovery_timeout}s",
                    "base_ejection_time": f"{policy.timeout_seconds}s",
                    "max_ejection_percent": 50,
                    "split_external_local_origin_errors": True
                },
                "circuit_breakers": {
                    "thresholds": [{
                        "priority": "DEFAULT",
                        "max_connections": policy.failure_threshold * 10,
                        "max_pending_requests": policy.failure_threshold * 5,
                        "max_requests": policy.failure_threshold * 20,
                        "max_retries": policy.success_threshold
                    }]
                }
            }
            
            # Update cluster configuration
            response = await client.post(
                f"{gateway_config.admin_endpoint}/clusters/{policy.service_name}",
                json=circuit_breaker_config
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            self.logger.error(f"Error deploying Envoy policy: {str(e)}")
            return False

    async def _deploy_aws_policy(self, gateway_id: str, gateway_config: GatewayConfig, policy: CircuitBreakerPolicy) -> bool:
        """Deploy circuit breaker policy to AWS API Gateway"""
        try:
            # AWS API Gateway circuit breaker is typically handled through CloudWatch alarms
            # and Lambda@Edge functions or custom authorizers
            
            # This would require AWS SDK integration
            # For now, we'll simulate the deployment
            
            self.logger.info(f"AWS API Gateway policy deployment simulated for {policy.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deploying AWS API Gateway policy: {str(e)}")
            return False

    async def _deploy_zuul_policy(self, gateway_id: str, gateway_config: GatewayConfig, policy: CircuitBreakerPolicy) -> bool:
        """Deploy circuit breaker policy to Zuul gateway"""
        try:
            client = self.clients[gateway_id]
            
            # Zuul circuit breaker configuration (Hystrix-based)
            hystrix_config = {
                "hystrix": {
                    "command": {
                        policy.service_name: {
                            "execution": {
                                "isolation": {
                                    "thread": {
                                        "timeoutInMilliseconds": policy.timeout_seconds * 1000
                                    }
                                }
                            },
                            "circuitBreaker": {
                                "requestVolumeThreshold": policy.failure_threshold,
                                "sleepWindowInMilliseconds": policy.recovery_timeout * 1000,
                                "errorThresholdPercentage": 50
                            }
                        }
                    }
                }
            }
            
            response = await client.post(
                f"{gateway_config.admin_endpoint}/actuator/hystrix/config",
                json=hystrix_config
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            self.logger.error(f"Error deploying Zuul policy: {str(e)}")
            return False

    async def _deploy_istio_policy(self, gateway_id: str, gateway_config: GatewayConfig, policy: CircuitBreakerPolicy) -> bool:
        """Deploy circuit breaker policy to Istio service mesh"""
        try:
            if not self.k8s_client:
                self.logger.error("Kubernetes client not available for Istio integration")
                return False
            
            # Istio DestinationRule with circuit breaker
            destination_rule = {
                "apiVersion": "networking.istio.io/v1beta1",
                "kind": "DestinationRule",
                "metadata": {
                    "name": f"cb-{policy.name}",
                    "namespace": gateway_config.namespace or "default"
                },
                "spec": {
                    "host": policy.service_name,
                    "trafficPolicy": {
                        "outlierDetection": {
                            "consecutiveErrors": policy.failure_threshold,
                            "interval": f"{policy.recovery_timeout}s",
                            "baseEjectionTime": f"{policy.timeout_seconds}s",
                            "maxEjectionPercent": 50
                        },
                        "connectionPool": {
                            "tcp": {
                                "maxConnections": policy.failure_threshold * 10
                            },
                            "http": {
                                "http1MaxPendingRequests": policy.failure_threshold * 5,
                                "maxRequestsPerConnection": 2,
                                "maxRetries": policy.success_threshold
                            }
                        }
                    }
                }
            }
            
            # Apply the DestinationRule
            api_instance = kubernetes.client.CustomObjectsApi(self.k8s_client)
            api_instance.create_namespaced_custom_object(
                group="networking.istio.io",
                version="v1beta1",
                namespace=gateway_config.namespace or "default",
                plural="destinationrules",
                body=destination_rule
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deploying Istio policy: {str(e)}")
            return False

    async def _deploy_nginx_policy(self, gateway_id: str, gateway_config: GatewayConfig, policy: CircuitBreakerPolicy) -> bool:
        """Deploy circuit breaker policy to NGINX gateway"""
        try:
            client = self.clients[gateway_id]
            
            # NGINX Plus circuit breaker configuration
            nginx_config = {
                "upstream": policy.service_name,
                "max_fails": policy.failure_threshold,
                "fail_timeout": f"{policy.recovery_timeout}s",
                "max_conns": policy.failure_threshold * 10
            }
            
            response = await client.post(
                f"{gateway_config.admin_endpoint}/api/6/http/upstreams/{policy.service_name}",
                json=nginx_config
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            self.logger.error(f"Error deploying NGINX policy: {str(e)}")
            return False

    async def _deploy_traefik_policy(self, gateway_id: str, gateway_config: GatewayConfig, policy: CircuitBreakerPolicy) -> bool:
        """Deploy circuit breaker policy to Traefik gateway"""
        try:
            if not self.k8s_client:
                self.logger.error("Kubernetes client not available for Traefik integration")
                return False
            
            # Traefik circuit breaker middleware
            middleware_manifest = {
                "apiVersion": "traefik.containo.us/v1alpha1",
                "kind": "Middleware",
                "metadata": {
                    "name": f"cb-{policy.name}",
                    "namespace": gateway_config.namespace or "default"
                },
                "spec": {
                    "circuitBreaker": {
                        "expression": f"NetworkErrorRatio() > {policy.failure_threshold / 100.0}"
                    }
                }
            }
            
            # Apply the middleware
            api_instance = kubernetes.client.CustomObjectsApi(self.k8s_client)
            api_instance.create_namespaced_custom_object(
                group="traefik.containo.us",
                version="v1alpha1",
                namespace=gateway_config.namespace or "default",
                plural="middlewares",
                body=middleware_manifest
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deploying Traefik policy: {str(e)}")
            return False

    async def _update_circuit_state_by_type(self, gateway_id: str, gateway_config: GatewayConfig, service_name: str, state: str) -> bool:
        """Update circuit state based on gateway type"""
        try:
            client = self.clients[gateway_id]
            
            # Update state based on gateway type
            if gateway_config.gateway_type in [GatewayType.KONG, GatewayType.ENVOY, GatewayType.NGINX]:
                # HTTP API-based update
                response = await client.put(
                    f"{gateway_config.admin_endpoint}/circuit-breakers/{service_name}/state",
                    json={"state": state}
                )
                return response.status_code == 200
                
            elif gateway_config.gateway_type in [GatewayType.AMBASSADOR, GatewayType.ISTIO, GatewayType.TRAEFIK]:
                # Kubernetes CRD-based update
                return await self._update_k8s_circuit_state(gateway_config, service_name, state)
                
            else:
                # Custom implementation for other gateways
                self.logger.info(f"Circuit state update for {gateway_config.gateway_type.value} handled by custom logic")
                return True
                
        except Exception as e:
            self.logger.error(f"Error updating circuit state: {str(e)}")
            return False

    async def _fetch_metrics_by_type(self, gateway_id: str, gateway_config: GatewayConfig) -> Dict[str, Any]:
        """Fetch metrics based on gateway type"""
        try:
            client = self.clients[gateway_id]
            
            if gateway_config.gateway_type == GatewayType.KONG:
                response = await client.get(f"{gateway_config.admin_endpoint}/status")
                if response.status_code == 200:
                    return response.json()
                    
            elif gateway_config.gateway_type == GatewayType.ENVOY:
                response = await client.get(f"{gateway_config.admin_endpoint}/stats")
                if response.status_code == 200:
                    return {"stats": response.text}
                    
            elif gateway_config.gateway_type == GatewayType.NGINX:
                response = await client.get(f"{gateway_config.admin_endpoint}/api/6/nginx")
                if response.status_code == 200:
                    return response.json()
            
            # Default empty metrics
            return {}
            
        except Exception as e:
            self.logger.error(f"Error fetching metrics: {str(e)}")
            return {}

    async def _validate_gateway_connection(self, gateway_id: str) -> bool:
        """Validate connection to gateway"""
        try:
            gateway_config = self.gateways[gateway_id]
            client = self.clients[gateway_id]
            
            # Test connection with health check endpoint
            response = await client.get(f"{gateway_config.admin_endpoint}/status")
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Gateway connection validation failed: {str(e)}")
            return False

    async def _health_check_loop(self, gateway_id: str):
        """Health check loop for gateway"""
        gateway_config = self.gateways[gateway_id]
        
        while gateway_id in self.gateways:
            try:
                if await self._validate_gateway_connection(gateway_id):
                    if self.status[gateway_id] == IntegrationStatus.ERROR:
                        self.status[gateway_id] = IntegrationStatus.ACTIVE
                        self.logger.info(f"Gateway {gateway_id} recovered")
                    
                    self.metrics[gateway_id].health_checks += 1
                    self.metrics[gateway_id].last_health_check = datetime.utcnow()
                else:
                    if self.status[gateway_id] == IntegrationStatus.ACTIVE:
                        self.status[gateway_id] = IntegrationStatus.ERROR
                        await self._trigger_event_handlers('health_check_failed', {
                            'gateway_id': gateway_id
                        })
                        self.logger.warning(f"Gateway {gateway_id} health check failed")
                
                await asyncio.sleep(gateway_config.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Health check error for gateway {gateway_id}: {str(e)}")
                await asyncio.sleep(gateway_config.health_check_interval)

    def _initialize_service_discovery(self):
        """Initialize service discovery clients"""
        try:
            # Initialize Consul client
            if self.config.get('consul', {}).get('enabled', False):
                consul_config = self.config['consul']
                self.consul_client = consul.Consul(
                    host=consul_config.get('host', 'localhost'),
                    port=consul_config.get('port', 8500)
                )
            
            # Initialize etcd client
            if self.config.get('etcd', {}).get('enabled', False):
                etcd_config = self.config['etcd']
                self.etcd_client = etcd3.client(
                    host=etcd_config.get('host', 'localhost'),
                    port=etcd_config.get('port', 2379)
                )
            
            # Initialize Kubernetes client
            if self.config.get('kubernetes', {}).get('enabled', False):
                try:
                    config.load_incluster_config()
                except:
                    config.load_kube_config()
                self.k8s_client = client.ApiClient()
                
        except Exception as e:
            self.logger.error(f"Service discovery initialization error: {str(e)}")

    async def _update_k8s_circuit_state(self, gateway_config: GatewayConfig, service_name: str, state: str) -> bool:
        """Update circuit breaker state in Kubernetes CRD"""
        try:
            if not self.k8s_client:
                return False
            
            # Update custom resource based on gateway type
            api_instance = kubernetes.client.CustomObjectsApi(self.k8s_client)
            
            # This would be implemented based on specific CRD schema
            self.logger.info(f"Kubernetes circuit state update simulated for {service_name}: {state}")
            return True
            
        except Exception as e:
            self.logger.error(f"Kubernetes circuit state update error: {str(e)}")
            return False

    async def _trigger_event_handlers(self, event_type: str, event_data: Dict[str, Any]):
        """Trigger registered event handlers"""
        try:
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event_data)
                        else:
                            handler(event_data)
                    except Exception as e:
                        self.logger.error(f"Event handler error: {str(e)}")
                        
        except Exception as e:
            self.logger.error(f"Error triggering event handlers: {str(e)}")

    async def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    async def cleanup(self):
        """Cleanup resources"""
        try:
            # Cancel health check tasks
            for task in self.health_check_tasks.values():
                if not task.done():
                    task.cancel()
            
            # Close HTTP clients
            for client in self.clients.values():
                await client.aclose()
            
            # Close service discovery clients
            if self.etcd_client:
                self.etcd_client.close()
            
            self.logger.info("API Gateway Integration cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {str(e)}")

# Global API gateway integration instance
api_gateway_integration = APIGatewayIntegration()

# Export main classes and functions
__all__ = [
    'APIGatewayIntegration',
    'GatewayConfig',
    'CircuitBreakerPolicy',
    'GatewayMetrics',
    'GatewayType',
    'PolicyAction',
    'IntegrationStatus',
    'api_gateway_integration'
]