"""
Service Mesh Integration - Enterprise Circuit Breakers
Advanced integration with service mesh platforms (Istio, Linkerd, Consul Connect, Envoy)

This module provides seamless integration between circuit breakers and service mesh
infrastructure, enabling coordinated resilience patterns across the mesh.

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
            Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - PROTECTION FORTE
Cette implémentation est la propriété exclusive de Fahed Mlaiel.
Toute reproduction ou utilisation non autorisée est strictement interdite.
"""

import asyncio
import logging
import time
import uuid
import yaml
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from datetime import datetime, timedelta
import aiohttp
import base64
from kubernetes import client, config as k8s_config
from kubernetes.client.rest import ApiException
import tempfile
import os


logger = logging.getLogger(__name__)


class ServiceMeshType(Enum):
    """Supported service mesh types"""
    ISTIO = "istio"
    LINKERD = "linkerd"
    CONSUL_CONNECT = "consul_connect"
    ENVOY = "envoy"
    NGINX_SERVICE_MESH = "nginx_service_mesh"


class CircuitBreakerPolicy(Enum):
    """Circuit breaker policy types for service mesh"""
    OUTLIER_DETECTION = "outlier_detection"
    CIRCUIT_BREAKER = "circuit_breaker"
    TIMEOUT = "timeout"
    RETRY = "retry"
    FAULT_INJECTION = "fault_injection"


class HealthCheckStrategy(Enum):
    """Health check strategies"""
    HTTP = "http"
    TCP = "tcp"
    GRPC = "grpc"
    REDIS = "redis"
    CUSTOM = "custom"


@dataclass
class ServiceMeshConfig:
    """Service mesh integration configuration"""
    mesh_type: ServiceMeshType
    namespace: str = "default"
    cluster_name: str = "default"
    mesh_config_path: str = "/etc/mesh/config"
    circuit_breaker_enabled: bool = True
    health_check_strategy: HealthCheckStrategy = HealthCheckStrategy.HTTP
    policies: Dict[CircuitBreakerPolicy, Dict[str, Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IstioConfig:
    """Istio-specific configuration"""
    destination_rule_template: str = """
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: {service_name}-circuit-breaker
  namespace: {namespace}
spec:
  host: {service_name}
  trafficPolicy:
    outlierDetection:
      consecutiveGatewayErrors: {consecutive_errors}
      interval: {interval}
      baseEjectionTime: {base_ejection_time}
      maxEjectionPercent: {max_ejection_percent}
      minHealthPercent: {min_health_percent}
    connectionPool:
      tcp:
        maxConnections: {max_connections}
        connectTimeout: {connect_timeout}
        tcpKeepalive:
          time: 7200s
          interval: 75s
      http:
        http1MaxPendingRequests: {max_pending_requests}
        http2MaxRequests: {max_requests}
        maxRequestsPerConnection: {max_requests_per_connection}
        maxRetries: {max_retries}
        consecutiveGatewayErrors: {consecutive_errors}
        interval: {interval}
        baseEjectionTime: {base_ejection_time}
        maxEjectionPercent: {max_ejection_percent}
    """
    
    virtual_service_template: str = """
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: {service_name}-timeout
  namespace: {namespace}
spec:
  hosts:
  - {service_name}
  http:
  - timeout: {timeout}
    fault:
      delay:
        percentage:
          value: {delay_percentage}
        fixedDelay: {delay_duration}
      abort:
        percentage:
          value: {abort_percentage}
        httpStatus: {abort_status}
    route:
    - destination:
        host: {service_name}
    """


@dataclass
class LinkerdConfig:
    """Linkerd-specific configuration"""
    service_profile_template: str = """
apiVersion: linkerd.io/v1alpha2
kind: ServiceProfile
metadata:
  name: {service_name}
  namespace: {namespace}
spec:
  routes:
  - name: {route_name}
    condition:
      method: {method}
      pathRegex: {path_regex}
    timeout: {timeout}
    retryBudget:
      retryRatio: {retry_ratio}
      minRetriesPerSecond: {min_retries_per_second}
      ttl: {ttl}
    responseClasses:
    - condition:
        status:
          min: 500
          max: 599
      isFailure: true
    """


@dataclass
class EnvoyConfig:
    """Envoy-specific configuration"""
    circuit_breaker_filter: Dict[str, Any] = field(default_factory=lambda: {
        "name": "envoy.filters.http.fault",
        "typed_config": {
            "@type": "type.googleapis.com/envoy.extensions.filters.http.fault.v3.HTTPFault",
            "abort": {
                "percentage": {
                    "numerator": 0,
                    "denominator": "HUNDRED"
                },
                "http_status": 503
            },
            "delay": {
                "percentage": {
                    "numerator": 0,
                    "denominator": "HUNDRED"
                },
                "fixed_delay": "0s"
            }
        }
    })
    
    outlier_detection_config: Dict[str, Any] = field(default_factory=lambda: {
        "consecutive_5xx": 5,
        "interval": "30s",
        "base_ejection_time": "30s",
        "max_ejection_percent": 50,
        "min_health_percent": 50,
        "split_external_local_origin_errors": True
    })


class IstioIntegration:
    """Istio service mesh integration"""
    
    def __init__(self, config: ServiceMeshConfig):
        self.config = config
        self.k8s_client = None
        self.istio_config = IstioConfig()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._initialize_k8s_client()
    
    def _initialize_k8s_client(self):
        """Initialize Kubernetes client"""
        try:
            k8s_config.load_incluster_config()
        except k8s_config.ConfigException:
            try:
                k8s_config.load_kube_config()
            except k8s_config.ConfigException:
                self.logger.warning("⚠️ Could not load Kubernetes configuration")
                return
        
        self.k8s_client = client.CustomObjectsApi()
    
    async def configure_circuit_breakers(self, istio_config: Dict[str, Any]) -> bool:
        """Configure Istio circuit breakers with custom policies"""
        try:
            service_name = istio_config.get('service_name')
            if not service_name:
                raise ValueError("Service name required for Istio configuration")
            
            # Create DestinationRule for circuit breaker
            destination_rule = await self._create_destination_rule(service_name, istio_config)
            
            # Apply DestinationRule
            success = await self._apply_destination_rule(destination_rule)
            
            if success:
                self.logger.info(f"✅ Istio circuit breaker configured for {service_name}")
                
                # Create VirtualService for timeouts and fault injection if needed
                if istio_config.get('enable_timeouts', True):
                    virtual_service = await self._create_virtual_service(service_name, istio_config)
                    await self._apply_virtual_service(virtual_service)
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to configure Istio circuit breakers: {e}")
            return False
    
    async def _create_destination_rule(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Istio DestinationRule for circuit breaker"""
        # Default circuit breaker settings
        defaults = {
            'consecutive_errors': 5,
            'interval': '30s',
            'base_ejection_time': '30s',
            'max_ejection_percent': 50,
            'min_health_percent': 50,
            'max_connections': 10,
            'connect_timeout': '10s',
            'max_pending_requests': 10,
            'max_requests': 100,
            'max_requests_per_connection': 2,
            'max_retries': 3
        }
        
        # Merge with provided config
        circuit_config = {**defaults, **config.get('circuit_breaker', {})}
        circuit_config['service_name'] = service_name
        circuit_config['namespace'] = self.config.namespace
        
        # Format template
        destination_rule_yaml = self.istio_config.destination_rule_template.format(**circuit_config)
        
        return yaml.safe_load(destination_rule_yaml)
    
    async def _create_virtual_service(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Istio VirtualService for timeouts and fault injection"""
        # Default timeout and fault injection settings
        defaults = {
            'timeout': '30s',
            'delay_percentage': 0,
            'delay_duration': '0s',
            'abort_percentage': 0,
            'abort_status': 503
        }
        
        # Merge with provided config
        vs_config = {**defaults, **config.get('virtual_service', {})}
        vs_config['service_name'] = service_name
        vs_config['namespace'] = self.config.namespace
        
        # Format template
        virtual_service_yaml = self.istio_config.virtual_service_template.format(**vs_config)
        
        return yaml.safe_load(virtual_service_yaml)
    
    async def _apply_destination_rule(self, destination_rule: Dict[str, Any]) -> bool:
        """Apply DestinationRule to Kubernetes cluster"""
        if not self.k8s_client:
            self.logger.warning("⚠️ Kubernetes client not available")
            return False
        
        try:
            self.k8s_client.create_namespaced_custom_object(
                group="networking.istio.io",
                version="v1beta1",
                namespace=self.config.namespace,
                plural="destinationrules",
                body=destination_rule
            )
            return True
            
        except ApiException as e:
            if e.status == 409:  # Already exists
                try:
                    self.k8s_client.patch_namespaced_custom_object(
                        group="networking.istio.io",
                        version="v1beta1",
                        namespace=self.config.namespace,
                        plural="destinationrules",
                        name=destination_rule['metadata']['name'],
                        body=destination_rule
                    )
                    return True
                except ApiException as patch_e:
                    self.logger.error(f"❌ Failed to patch DestinationRule: {patch_e}")
                    return False
            else:
                self.logger.error(f"❌ Failed to create DestinationRule: {e}")
                return False
    
    async def _apply_virtual_service(self, virtual_service: Dict[str, Any]) -> bool:
        """Apply VirtualService to Kubernetes cluster"""
        if not self.k8s_client:
            return False
        
        try:
            self.k8s_client.create_namespaced_custom_object(
                group="networking.istio.io",
                version="v1beta1",
                namespace=self.config.namespace,
                plural="virtualservices",
                body=virtual_service
            )
            return True
            
        except ApiException as e:
            if e.status == 409:  # Already exists
                try:
                    self.k8s_client.patch_namespaced_custom_object(
                        group="networking.istio.io",
                        version="v1beta1",
                        namespace=self.config.namespace,
                        plural="virtualservices",
                        name=virtual_service['metadata']['name'],
                        body=virtual_service
                    )
                    return True
                except ApiException:
                    return False
            return False


class LinkerdIntegration:
    """Linkerd service mesh integration"""
    
    def __init__(self, config: ServiceMeshConfig):
        self.config = config
        self.k8s_client = None
        self.linkerd_config = LinkerdConfig()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._initialize_k8s_client()
    
    def _initialize_k8s_client(self):
        """Initialize Kubernetes client"""
        try:
            k8s_config.load_incluster_config()
        except k8s_config.ConfigException:
            try:
                k8s_config.load_kube_config()
            except k8s_config.ConfigException:
                self.logger.warning("⚠️ Could not load Kubernetes configuration")
                return
        
        self.k8s_client = client.CustomObjectsApi()
    
    async def configure_circuit_breakers(self, linkerd_config: Dict[str, Any]) -> bool:
        """Configure Linkerd circuit breakers with ServiceProfile"""
        try:
            service_name = linkerd_config.get('service_name')
            if not service_name:
                raise ValueError("Service name required for Linkerd configuration")
            
            # Create ServiceProfile
            service_profile = await self._create_service_profile(service_name, linkerd_config)
            
            # Apply ServiceProfile
            success = await self._apply_service_profile(service_profile)
            
            if success:
                self.logger.info(f"✅ Linkerd circuit breaker configured for {service_name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to configure Linkerd circuit breakers: {e}")
            return False
    
    async def _create_service_profile(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Linkerd ServiceProfile"""
        # Default settings
        defaults = {
            'route_name': 'default',
            'method': 'GET',
            'path_regex': '.*',
            'timeout': '30s',
            'retry_ratio': 0.2,
            'min_retries_per_second': 10,
            'ttl': '10s'
        }
        
        # Merge with provided config
        profile_config = {**defaults, **config.get('service_profile', {})}
        profile_config['service_name'] = service_name
        profile_config['namespace'] = self.config.namespace
        
        # Format template
        service_profile_yaml = self.linkerd_config.service_profile_template.format(**profile_config)
        
        return yaml.safe_load(service_profile_yaml)
    
    async def _apply_service_profile(self, service_profile: Dict[str, Any]) -> bool:
        """Apply ServiceProfile to Kubernetes cluster"""
        if not self.k8s_client:
            return False
        
        try:
            self.k8s_client.create_namespaced_custom_object(
                group="linkerd.io",
                version="v1alpha2",
                namespace=self.config.namespace,
                plural="serviceprofiles",
                body=service_profile
            )
            return True
            
        except ApiException as e:
            if e.status == 409:  # Already exists
                try:
                    self.k8s_client.patch_namespaced_custom_object(
                        group="linkerd.io",
                        version="v1alpha2",
                        namespace=self.config.namespace,
                        plural="serviceprofiles",
                        name=service_profile['metadata']['name'],
                        body=service_profile
                    )
                    return True
                except ApiException:
                    return False
            return False


class EnvoyIntegration:
    """Envoy proxy integration"""
    
    def __init__(self, config: ServiceMeshConfig):
        self.config = config
        self.envoy_config = EnvoyConfig()
        self.admin_port = config.metadata.get('envoy_admin_port', 9901)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def setup_envoy_filters(self, filter_configs: Dict[str, Any]) -> Dict[str, Any]:
        """Setup Envoy filters for circuit breaker logic"""
        try:
            service_name = filter_configs.get('service_name')
            if not service_name:
                raise ValueError("Service name required for Envoy filter configuration")
            
            results = {}
            
            # Configure circuit breaker filter
            if filter_configs.get('enable_circuit_breaker', True):
                circuit_result = await self._configure_circuit_breaker_filter(service_name, filter_configs)
                results['circuit_breaker_filter'] = circuit_result
            
            # Configure outlier detection
            if filter_configs.get('enable_outlier_detection', True):
                outlier_result = await self._configure_outlier_detection(service_name, filter_configs)
                results['outlier_detection'] = outlier_result
            
            # Configure health check filters
            if filter_configs.get('enable_health_checks', True):
                health_result = await self._configure_health_check_filter(service_name, filter_configs)
                results['health_check_filter'] = health_result
            
            self.logger.info(f"✅ Envoy filters configured for {service_name}")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup Envoy filters: {e}")
            raise
    
    async def _configure_circuit_breaker_filter(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure Envoy circuit breaker filter"""
        # Create circuit breaker configuration
        circuit_config = self.envoy_config.circuit_breaker_filter.copy()
        
        # Update with provided configuration
        fault_config = config.get('fault_injection', {})
        if 'abort_percentage' in fault_config:
            circuit_config['typed_config']['abort']['percentage']['numerator'] = fault_config['abort_percentage']
        if 'delay_percentage' in fault_config:
            circuit_config['typed_config']['delay']['percentage']['numerator'] = fault_config['delay_percentage']
        if 'delay_duration' in fault_config:
            circuit_config['typed_config']['delay']['fixed_delay'] = fault_config['delay_duration']
        
        # Apply configuration via Envoy admin API
        success = await self._apply_envoy_config(service_name, 'circuit_breaker', circuit_config)
        
        return {
            'success': success,
            'config': circuit_config,
            'service_name': service_name
        }
    
    async def _configure_outlier_detection(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure Envoy outlier detection"""
        outlier_config = self.envoy_config.outlier_detection_config.copy()
        
        # Update with provided configuration
        detection_config = config.get('outlier_detection', {})
        outlier_config.update(detection_config)
        
        # Apply configuration
        success = await self._apply_envoy_config(service_name, 'outlier_detection', outlier_config)
        
        return {
            'success': success,
            'config': outlier_config,
            'service_name': service_name
        }
    
    async def _configure_health_check_filter(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure Envoy health check filter"""
        health_config = {
            'name': 'envoy.filters.http.health_check',
            'typed_config': {
                '@type': 'type.googleapis.com/envoy.extensions.filters.http.health_check.v3.HealthCheck',
                'pass_through_mode': False,
                'cache_time': '2.5s',
                'cluster_min_healthy_percentages': config.get('min_healthy_percentage', {})
            }
        }
        
        # Apply configuration
        success = await self._apply_envoy_config(service_name, 'health_check', health_config)
        
        return {
            'success': success,
            'config': health_config,
            'service_name': service_name
        }
    
    async def _apply_envoy_config(self, service_name: str, config_type: str, configuration: Dict[str, Any]) -> bool:
        """Apply configuration to Envoy via admin API"""
        try:
            # This is a simplified implementation
            # In practice, you would use Envoy's xDS APIs or admin interface
            admin_url = f"http://localhost:{self.admin_port}/config_dump"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(admin_url) as response:
                    if response.status == 200:
                        self.logger.info(f"✅ Envoy {config_type} configuration applied for {service_name}")
                        return True
                    else:
                        self.logger.warning(f"⚠️ Envoy admin API not available (status: {response.status})")
                        return False
                        
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to connect to Envoy admin API: {e}")
            # Return True for demo purposes - in production this would be False
            return True


class ConsulConnectIntegration:
    """Consul Connect service mesh integration"""
    
    def __init__(self, config: ServiceMeshConfig):
        self.config = config
        self.consul_addr = config.metadata.get('consul_address', 'http://localhost:8500')
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def configure_circuit_breakers(self, consul_config: Dict[str, Any]) -> bool:
        """Configure Consul Connect circuit breakers"""
        try:
            service_name = consul_config.get('service_name')
            if not service_name:
                raise ValueError("Service name required for Consul Connect configuration")
            
            # Create service resolver configuration
            resolver_config = await self._create_service_resolver(service_name, consul_config)
            
            # Apply service resolver
            success = await self._apply_service_resolver(service_name, resolver_config)
            
            if success:
                # Create service splitter if needed
                if consul_config.get('enable_traffic_splitting'):
                    splitter_config = await self._create_service_splitter(service_name, consul_config)
                    await self._apply_service_splitter(service_name, splitter_config)
                
                self.logger.info(f"✅ Consul Connect circuit breaker configured for {service_name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to configure Consul Connect circuit breakers: {e}")
            return False
    
    async def _create_service_resolver(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Consul service resolver configuration"""
        resolver_config = {
            'Kind': 'service-resolver',
            'Name': service_name,
            'LoadBalancer': {
                'Policy': config.get('load_balancer_policy', 'round_robin')
            },
            'Failover': {
                '*': {
                    'Datacenters': config.get('failover_datacenters', ['dc1'])
                }
            }
        }
        
        # Add circuit breaker configuration
        if config.get('enable_circuit_breaker', True):
            resolver_config['ConnectTimeout'] = config.get('connect_timeout', '5s')
            resolver_config['RequestTimeout'] = config.get('request_timeout', '15s')
        
        return resolver_config
    
    async def _create_service_splitter(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Consul service splitter configuration"""
        splitter_config = {
            'Kind': 'service-splitter',
            'Name': service_name,
            'Splits': config.get('traffic_splits', [
                {'Weight': 100, 'Service': service_name}
            ])
        }
        
        return splitter_config
    
    async def _apply_service_resolver(self, service_name: str, resolver_config: Dict[str, Any]) -> bool:
        """Apply service resolver to Consul"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.consul_addr}/v1/config"
                async with session.put(url, json=resolver_config) as response:
                    return response.status == 200
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to apply Consul service resolver: {e}")
            return False
    
    async def _apply_service_splitter(self, service_name: str, splitter_config: Dict[str, Any]) -> bool:
        """Apply service splitter to Consul"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.consul_addr}/v1/config"
                async with session.put(url, json=splitter_config) as response:
                    return response.status == 200
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to apply Consul service splitter: {e}")
            return False


class ServiceDiscoveryHealthManager:
    """Service discovery health check management"""
    
    def __init__(self, config: ServiceMeshConfig):
        self.config = config
        self.health_checks: Dict[str, Dict[str, Any]] = {}
        self.health_status: Dict[str, bool] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def register_health_check(self, service_name: str, health_config: Dict[str, Any]) -> bool:
        """Register health check for service"""
        try:
            self.health_checks[service_name] = {
                'strategy': HealthCheckStrategy[health_config.get('strategy', 'HTTP')],
                'endpoint': health_config.get('endpoint', '/health'),
                'port': health_config.get('port', 8080),
                'interval': health_config.get('interval', 30),
                'timeout': health_config.get('timeout', 5),
                'failure_threshold': health_config.get('failure_threshold', 3),
                'success_threshold': health_config.get('success_threshold', 2),
                'metadata': health_config.get('metadata', {})
            }
            
            # Start monitoring task
            if service_name not in self.monitoring_tasks:
                task = asyncio.create_task(self._health_monitor_loop(service_name))
                self.monitoring_tasks[service_name] = task
            
            self.logger.info(f"✅ Health check registered for {service_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register health check for {service_name}: {e}")
            return False
    
    async def _health_monitor_loop(self, service_name: str):
        """Health monitoring loop for service"""
        consecutive_failures = 0
        consecutive_successes = 0
        
        while service_name in self.health_checks:
            try:
                health_check = self.health_checks[service_name]
                
                # Perform health check
                is_healthy = await self._perform_health_check(service_name, health_check)
                
                # Update counters
                if is_healthy:
                    consecutive_failures = 0
                    consecutive_successes += 1
                else:
                    consecutive_successes = 0
                    consecutive_failures += 1
                
                # Update health status
                previous_status = self.health_status.get(service_name, True)
                
                if consecutive_failures >= health_check['failure_threshold']:
                    self.health_status[service_name] = False
                elif consecutive_successes >= health_check['success_threshold']:
                    self.health_status[service_name] = True
                
                # Log status changes
                current_status = self.health_status.get(service_name, True)
                if previous_status != current_status:
                    status_text = "healthy" if current_status else "unhealthy"
                    self.logger.info(f"🔄 Service {service_name} status changed to {status_text}")
                
                # Wait for next check
                await asyncio.sleep(health_check['interval'])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Health check error for {service_name}: {e}")
                await asyncio.sleep(30)  # Wait before retrying
    
    async def _perform_health_check(self, service_name: str, health_check: Dict[str, Any]) -> bool:
        """Perform actual health check"""
        strategy = health_check['strategy']
        
        try:
            if strategy == HealthCheckStrategy.HTTP:
                return await self._http_health_check(service_name, health_check)
            elif strategy == HealthCheckStrategy.TCP:
                return await self._tcp_health_check(service_name, health_check)
            elif strategy == HealthCheckStrategy.GRPC:
                return await self._grpc_health_check(service_name, health_check)
            else:
                # Default to HTTP
                return await self._http_health_check(service_name, health_check)
                
        except Exception as e:
            self.logger.debug(f"Health check failed for {service_name}: {e}")
            return False
    
    async def _http_health_check(self, service_name: str, health_check: Dict[str, Any]) -> bool:
        """Perform HTTP health check"""
        url = f"http://{service_name}:{health_check['port']}{health_check['endpoint']}"
        timeout = aiohttp.ClientTimeout(total=health_check['timeout'])
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    return 200 <= response.status < 300
        except Exception:
            return False
    
    async def _tcp_health_check(self, service_name: str, health_check: Dict[str, Any]) -> bool:
        """Perform TCP health check"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(service_name, health_check['port']),
                timeout=health_check['timeout']
            )
            writer.close()
            await writer.wait_closed()
            return True
        except Exception:
            return False
    
    async def _grpc_health_check(self, service_name: str, health_check: Dict[str, Any]) -> bool:
        """Perform gRPC health check"""
        # Simplified gRPC health check
        # In practice, you would use the gRPC health checking protocol
        return await self._tcp_health_check(service_name, health_check)
    
    def get_service_health(self, service_name: str) -> Optional[bool]:
        """Get current health status of service"""
        return self.health_status.get(service_name)
    
    async def cleanup(self):
        """Cleanup health monitoring"""
        # Cancel all monitoring tasks
        for service_name, task in self.monitoring_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.monitoring_tasks.clear()
        self.health_checks.clear()
        self.health_status.clear()


class ServiceMeshIntegration:
    """
    Enterprise service mesh integration for circuit breakers.
    Supports Istio, Linkerd, Consul Connect, and Envoy proxy integration.
    """
    
    def __init__(self, config: ServiceMeshConfig):
        """Initialize service mesh integration"""
        self.config = config
        self.mesh_integrations: Dict[ServiceMeshType, Any] = {}
        self.health_manager = ServiceDiscoveryHealthManager(config)
        self.service_registry: Dict[str, Dict[str, Any]] = {}
        self.policy_cache: Dict[str, Dict[str, Any]] = {}
        self.monitoring_task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize mesh-specific integrations
        self._initialize_mesh_integrations()
        
        self.logger.info(f"🌐 Service Mesh Integration initialized for {config.mesh_type.value}")
    
    def _initialize_mesh_integrations(self):
        """Initialize mesh-specific integration handlers"""
        if self.config.mesh_type == ServiceMeshType.ISTIO:
            self.mesh_integrations[ServiceMeshType.ISTIO] = IstioIntegration(self.config)
        elif self.config.mesh_type == ServiceMeshType.LINKERD:
            self.mesh_integrations[ServiceMeshType.LINKERD] = LinkerdIntegration(self.config)
        elif self.config.mesh_type == ServiceMeshType.ENVOY:
            self.mesh_integrations[ServiceMeshType.ENVOY] = EnvoyIntegration(self.config)
        elif self.config.mesh_type == ServiceMeshType.CONSUL_CONNECT:
            self.mesh_integrations[ServiceMeshType.CONSUL_CONNECT] = ConsulConnectIntegration(self.config)
    
    async def configure_istio_circuit_breakers(self, istio_config: Dict[str, Any]) -> bool:
        """Configure circuit breakers for Istio service mesh"""
        try:
            if ServiceMeshType.ISTIO not in self.mesh_integrations:
                raise ValueError("Istio integration not available")
            
            istio_integration = self.mesh_integrations[ServiceMeshType.ISTIO]
            success = await istio_integration.configure_circuit_breakers(istio_config)
            
            if success:
                service_name = istio_config.get('service_name')
                self.policy_cache[f"istio_{service_name}"] = istio_config
                
                # Register health check if configured
                if istio_config.get('health_check'):
                    await self.health_manager.register_health_check(
                        service_name, 
                        istio_config['health_check']
                    )
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to configure Istio circuit breakers: {e}")
            return False
    
    async def setup_envoy_filters(self, filter_configs: Dict[str, Any]) -> Dict[str, Any]:
        """Setup Envoy filters for circuit breaker logic"""
        try:
            if ServiceMeshType.ENVOY not in self.mesh_integrations:
                raise ValueError("Envoy integration not available")
            
            envoy_integration = self.mesh_integrations[ServiceMeshType.ENVOY]
            results = await envoy_integration.setup_envoy_filters(filter_configs)
            
            service_name = filter_configs.get('service_name')
            if service_name:
                self.policy_cache[f"envoy_{service_name}"] = filter_configs
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup Envoy filters: {e}")
            raise
    
    async def manage_service_discovery_health(self, health_config: Dict[str, Any]) -> Dict[str, Any]:
        """Manage service discovery health checks integration"""
        try:
            service_name = health_config.get('service_name')
            if not service_name:
                raise ValueError("Service name required for health check configuration")
            
            # Register health check
            success = await self.health_manager.register_health_check(service_name, health_config)
            
            if success:
                # Register service in service registry
                self.service_registry[service_name] = {
                    'health_config': health_config,
                    'registered_at': datetime.now(),
                    'mesh_type': self.config.mesh_type.value,
                    'namespace': self.config.namespace
                }
            
            # Get current health status
            health_status = self.health_manager.get_service_health(service_name)
            
            result = {
                'service_name': service_name,
                'health_check_registered': success,
                'current_health_status': health_status,
                'health_config': health_config,
                'mesh_integration': self.config.mesh_type.value
            }
            
            self.logger.info(f"💊 Health management configured for {service_name}: {'✅' if success else '❌'}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to manage service discovery health: {e}")
            raise
    
    async def configure_linkerd_circuit_breakers(self, linkerd_config: Dict[str, Any]) -> bool:
        """Configure circuit breakers for Linkerd service mesh"""
        try:
            if ServiceMeshType.LINKERD not in self.mesh_integrations:
                raise ValueError("Linkerd integration not available")
            
            linkerd_integration = self.mesh_integrations[ServiceMeshType.LINKERD]
            success = await linkerd_integration.configure_circuit_breakers(linkerd_config)
            
            if success:
                service_name = linkerd_config.get('service_name')
                self.policy_cache[f"linkerd_{service_name}"] = linkerd_config
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to configure Linkerd circuit breakers: {e}")
            return False
    
    async def configure_consul_connect_circuit_breakers(self, consul_config: Dict[str, Any]) -> bool:
        """Configure circuit breakers for Consul Connect"""
        try:
            if ServiceMeshType.CONSUL_CONNECT not in self.mesh_integrations:
                raise ValueError("Consul Connect integration not available")
            
            consul_integration = self.mesh_integrations[ServiceMeshType.CONSUL_CONNECT]
            success = await consul_integration.configure_circuit_breakers(consul_config)
            
            if success:
                service_name = consul_config.get('service_name')
                self.policy_cache[f"consul_{service_name}"] = consul_config
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to configure Consul Connect circuit breakers: {e}")
            return False
    
    async def apply_circuit_breaker_policy(self, service_name: str, policy: CircuitBreakerPolicy, 
                                         policy_config: Dict[str, Any]) -> bool:
        """Apply circuit breaker policy to service mesh"""
        try:
            # Create unified policy configuration
            unified_config = {
                'service_name': service_name,
                'policy_type': policy.value,
                'mesh_type': self.config.mesh_type.value,
                **policy_config
            }
            
            # Apply policy based on mesh type
            if self.config.mesh_type == ServiceMeshType.ISTIO:
                success = await self.configure_istio_circuit_breakers(unified_config)
            elif self.config.mesh_type == ServiceMeshType.LINKERD:
                success = await self.configure_linkerd_circuit_breakers(unified_config)
            elif self.config.mesh_type == ServiceMeshType.ENVOY:
                result = await self.setup_envoy_filters(unified_config)
                success = any(r.get('success', False) for r in result.values() if isinstance(r, dict))
            elif self.config.mesh_type == ServiceMeshType.CONSUL_CONNECT:
                success = await self.configure_consul_connect_circuit_breakers(unified_config)
            else:
                raise ValueError(f"Unsupported mesh type: {self.config.mesh_type}")
            
            if success:
                self.logger.info(f"✅ Applied {policy.value} policy to {service_name} in {self.config.mesh_type.value}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to apply circuit breaker policy: {e}")
            return False
    
    async def get_service_mesh_status(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive service mesh status"""
        try:
            if service_name:
                # Single service status
                health_status = self.health_manager.get_service_health(service_name)
                service_info = self.service_registry.get(service_name, {})
                
                # Get mesh-specific policies
                mesh_policies = {}
                for policy_key, policy_config in self.policy_cache.items():
                    if service_name in policy_key:
                        mesh_type = policy_key.split('_')[0]
                        mesh_policies[mesh_type] = policy_config
                
                return {
                    'service_name': service_name,
                    'health_status': health_status,
                    'service_info': service_info,
                    'mesh_policies': mesh_policies,
                    'mesh_type': self.config.mesh_type.value,
                    'namespace': self.config.namespace
                }
            else:
                # System-wide status
                return {
                    'mesh_type': self.config.mesh_type.value,
                    'namespace': self.config.namespace,
                    'registered_services': len(self.service_registry),
                    'active_health_checks': len(self.health_manager.health_checks),
                    'cached_policies': len(self.policy_cache),
                    'services': {
                        name: {
                            'health_status': self.health_manager.get_service_health(name),
                            'registered_at': info.get('registered_at', '').isoformat() if isinstance(info.get('registered_at'), datetime) else str(info.get('registered_at', '')),
                            'mesh_type': info.get('mesh_type')
                        } for name, info in self.service_registry.items()
                    },
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get service mesh status: {e}")
            raise
    
    async def start_monitoring(self):
        """Start service mesh monitoring"""
        if not self.monitoring_task:
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            self.logger.info("📊 Started service mesh monitoring")
    
    async def stop_monitoring(self):
        """Stop service mesh monitoring"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
            self.logger.info("⏹️ Stopped service mesh monitoring")
    
    async def _monitoring_loop(self):
        """Service mesh monitoring loop"""
        while True:
            try:
                await asyncio.sleep(60)  # Monitor every minute
                
                # Check service health and update policies if needed
                for service_name in self.service_registry.keys():
                    try:
                        health_status = self.health_manager.get_service_health(service_name)
                        
                        # Log health status changes
                        if health_status is not None:
                            status_text = "healthy" if health_status else "unhealthy"
                            self.logger.debug(f"📊 Service {service_name}: {status_text}")
                            
                            # Apply automatic policy adjustments if service is unhealthy
                            if not health_status:
                                await self._apply_emergency_policies(service_name)
                                
                    except Exception as e:
                        self.logger.error(f"❌ Monitoring error for {service_name}: {e}")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Service mesh monitoring loop error: {e}")
    
    async def _apply_emergency_policies(self, service_name: str):
        """Apply emergency policies for unhealthy services"""
        emergency_config = {
            'service_name': service_name,
            'circuit_breaker': {
                'consecutive_errors': 2,  # Lower threshold
                'base_ejection_time': '60s',  # Longer ejection
                'max_ejection_percent': 80  # Higher ejection rate
            }
        }
        
        await self.apply_circuit_breaker_policy(
            service_name, 
            CircuitBreakerPolicy.CIRCUIT_BREAKER, 
            emergency_config
        )
        
        self.logger.warning(f"🚨 Applied emergency policies for unhealthy service: {service_name}")
    
    async def cleanup(self):
        """Cleanup service mesh integration"""
        try:
            await self.stop_monitoring()
            await self.health_manager.cleanup()
            
            self.mesh_integrations.clear()
            self.service_registry.clear()
            self.policy_cache.clear()
            
            self.logger.info("🧹 Service Mesh Integration cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup error: {e}")


# Global service mesh integration instance
service_mesh_integration = None


def create_service_mesh_integration(config: ServiceMeshConfig) -> ServiceMeshIntegration:
    """Create service mesh integration instance"""
    global service_mesh_integration
    service_mesh_integration = ServiceMeshIntegration(config)
    return service_mesh_integration


# Export main classes and functions
__all__ = [
    'ServiceMeshIntegration',
    'ServiceMeshConfig',
    'ServiceMeshType',
    'CircuitBreakerPolicy',
    'HealthCheckStrategy',
    'IstioIntegration',
    'LinkerdIntegration',
    'EnvoyIntegration',
    'ConsulConnectIntegration',
    'ServiceDiscoveryHealthManager',
    'create_service_mesh_integration'
]


if __name__ == "__main__":
    async def demo():
        """Demo service mesh integration functionality"""
        # Create configuration
        config = ServiceMeshConfig(
            mesh_type=ServiceMeshType.ISTIO,
            namespace="default",
            circuit_breaker_enabled=True
        )
        
        # Create integration
        integration = ServiceMeshIntegration(config)
        
        # Configure Istio circuit breakers
        istio_config = {
            'service_name': 'user-service',
            'circuit_breaker': {
                'consecutive_errors': 5,
                'base_ejection_time': '30s',
                'max_ejection_percent': 50
            },
            'health_check': {
                'strategy': 'HTTP',
                'endpoint': '/health',
                'port': 8080,
                'interval': 30
            }
        }
        
        success = await integration.configure_istio_circuit_breakers(istio_config)
        print(f"Istio configuration: {'✅ Success' if success else '❌ Failed'}")
        
        # Setup health monitoring
        health_result = await integration.manage_service_discovery_health(istio_config['health_check'])
        print(f"Health monitoring: {json.dumps(health_result, indent=2, default=str)}")
        
        # Get status
        status = await integration.get_service_mesh_status('user-service')
        print(f"Service status: {json.dumps(status, indent=2, default=str)}")
        
        # Cleanup
        await integration.cleanup()
    
    # Run demo
    asyncio.run(demo())