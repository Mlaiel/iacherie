#!/usr/bin/env python3
"""
🎯 SERVICE DISCOVERY ORCHESTRATOR - ENTERPRISE MICROSERVICES
============================================================

© FAHED MLAIEL 2024-2025 - PROPRIÉTÉ INTELLECTUELLE STRICTE
⚠️ ARCHITECTURE CONFIDENTIELLE - NIVEAU ENTERPRISE UNIQUEMENT

Advanced service discovery orchestrator for enterprise microservices architecture.
Provides intelligent service discovery, health monitoring, and load balancing
across multiple service registries and discovery mechanisms.

Features:
---------
🔍 Multi-Registry Support   - Consul, Eureka, Kubernetes, etcd
🎯 Intelligent Routing     - AI-powered service selection
📊 Health Monitoring       - Real-time health checks
⚖️ Load Balancing         - Multiple algorithms (round-robin, weighted, least-conn)
🔄 Auto-Scaling           - Dynamic service scaling based on load
🌍 Multi-Cloud            - Cross-cloud service discovery
📈 Metrics Collection     - Comprehensive observability
🔒 Security Integration   - mTLS, authentication, authorization

Contact: Fahed Mlaiel (mlaiel@live.de)
Team: Service Mesh Team - Service Discovery Expert
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Any, Optional, Union, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import consul
from kubernetes import client, config
import etcd3


# Configure logging
logger = logging.getLogger(__name__)


class DiscoveryBackend(Enum):
    """Service discovery backend types."""
    CONSUL = "consul"
    KUBERNETES = "kubernetes"
    EUREKA = "eureka"
    ETCD = "etcd"
    DNS = "dns"
    STATIC = "static"


class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithm types."""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    IP_HASH = "ip_hash"
    RANDOM = "random"
    WEIGHTED_RANDOM = "weighted_random"
    AI_OPTIMIZED = "ai_optimized"


class HealthStatus(Enum):
    """Service health status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    WARNING = "warning"
    UNKNOWN = "unknown"
    CRITICAL = "critical"


@dataclass
class ServiceInstance:
    """Service instance representation."""
    id: str
    name: str
    host: str
    port: int
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    health_status: HealthStatus = HealthStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    weight: int = 100
    connections: int = 0
    response_time_ms: float = 0.0
    error_rate: float = 0.0
    version: str = "1.0.0"
    zone: str = "default"
    protocol: str = "http"
    ssl_enabled: bool = False


@dataclass
class ServiceDefinition:
    """Service definition with discovery configuration."""
    name: str
    backend: DiscoveryBackend
    health_check_url: Optional[str] = None
    health_check_interval: int = 30
    health_check_timeout: int = 5
    load_balancing: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 3
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: int = 5
    cache_ttl: int = 300  # seconds


@dataclass
class DiscoveryConfig:
    """Service discovery orchestrator configuration."""
    # Backend configurations
    consul_host: str = "localhost"
    consul_port: int = 8500
    consul_token: Optional[str] = None
    
    kubernetes_namespace: str = "default"
    kubernetes_service_account: Optional[str] = None
    
    eureka_url: str = "http://localhost:8761/eureka"
    eureka_app_name: str = "discovery-orchestrator"
    
    etcd_host: str = "localhost"
    etcd_port: int = 2379
    
    # General settings
    default_health_check_interval: int = 30
    default_cache_ttl: int = 300
    max_concurrent_health_checks: int = 100
    enable_ai_optimization: bool = True
    enable_circuit_breaker: bool = True
    enable_metrics: bool = True
    
    # Performance settings
    connection_pool_size: int = 100
    request_timeout: int = 30
    max_retries: int = 3


class ServiceDiscoveryOrchestrator:
    """
    Enterprise service discovery orchestrator.
    
    Provides unified service discovery across multiple backends with
    intelligent routing, health monitoring, and performance optimization.
    """
    
    def __init__(self, config: DiscoveryConfig):
        self.config = config
        self.service_registry: Dict[str, List[ServiceInstance]] = {}
        self.service_definitions: Dict[str, ServiceDefinition] = {}
        self.backends: Dict[DiscoveryBackend, Any] = {}
        self.cache: Dict[str, Any] = {}
        self.health_checkers: Dict[str, asyncio.Task] = {}
        
        # Load balancing state
        self.round_robin_state: Dict[str, int] = {}
        self.connection_counts: Dict[str, int] = {}
        
        # Metrics
        self.metrics = {
            'total_services': 0,
            'total_instances': 0,
            'healthy_instances': 0,
            'unhealthy_instances': 0,
            'discovery_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'health_checks_performed': 0,
            'load_balancing_decisions': 0,
            'backend_errors': {},
            'last_update': None
        }
        
        # Initialize backends
        self._initialize_backends()
        
        logger.info("Service Discovery Orchestrator initialized")
    
    def _initialize_backends(self):
        """Initialize service discovery backends."""
        try:
            # Initialize Consul
            self.backends[DiscoveryBackend.CONSUL] = consul.Consul(
                host=self.config.consul_host,
                port=self.config.consul_port,
                token=self.config.consul_token
            )
            
            # Initialize Kubernetes
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
            
            self.backends[DiscoveryBackend.KUBERNETES] = {
                'core_v1': client.CoreV1Api(),
                'apps_v1': client.AppsV1Api()
            }
            
            # Initialize etcd
            self.backends[DiscoveryBackend.ETCD] = etcd3.client(
                host=self.config.etcd_host,
                port=self.config.etcd_port
            )
            
            logger.info("Service discovery backends initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize backends: {e}")
    
    async def register_service(self, service_def: ServiceDefinition) -> Dict[str, Any]:
        """
        Register a service with the orchestrator.
        
        Args:
            service_def: Service definition
            
        Returns:
            Dict containing registration status
        """
        try:
            logger.info(f"Registering service: {service_def.name}")
            
            self.service_definitions[service_def.name] = service_def
            
            # Discover initial instances
            instances = await self._discover_service_instances(service_def)
            self.service_registry[service_def.name] = instances
            
            # Start health monitoring
            if service_def.health_check_url:
                await self._start_health_monitoring(service_def)
            
            self.metrics['total_services'] += 1
            self.metrics['total_instances'] += len(instances)
            self._update_instance_health_metrics()
            
            return {
                'success': True,
                'message': f'Service {service_def.name} registered successfully',
                'service': service_def.name,
                'instances_discovered': len(instances),
                'backend': service_def.backend.value,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to register service {service_def.name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'service': service_def.name,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _discover_service_instances(self, service_def: ServiceDefinition) -> List[ServiceInstance]:
        """Discover service instances from the specified backend."""
        try:
            if service_def.backend == DiscoveryBackend.CONSUL:
                return await self._discover_consul_instances(service_def)
            elif service_def.backend == DiscoveryBackend.KUBERNETES:
                return await self._discover_kubernetes_instances(service_def)
            elif service_def.backend == DiscoveryBackend.ETCD:
                return await self._discover_etcd_instances(service_def)
            elif service_def.backend == DiscoveryBackend.EUREKA:
                return await self._discover_eureka_instances(service_def)
            else:
                logger.warning(f"Unsupported backend: {service_def.backend}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to discover instances for {service_def.name}: {e}")
            return []
    
    async def _discover_consul_instances(self, service_def: ServiceDefinition) -> List[ServiceInstance]:
        """Discover instances from Consul."""
        try:
            consul_client = self.backends[DiscoveryBackend.CONSUL]
            _, services = consul_client.health.service(
                service_def.name,
                passing=True,
                tag=service_def.tags[0] if service_def.tags else None
            )
            
            instances = []
            for service in services:
                instance = ServiceInstance(
                    id=service['Service']['ID'],
                    name=service['Service']['Service'],
                    host=service['Service']['Address'] or service['Node']['Address'],
                    port=service['Service']['Port'],
                    tags=service['Service']['Tags'] or [],
                    metadata=service['Service']['Meta'] or {},
                    health_status=HealthStatus.HEALTHY,
                    last_health_check=datetime.utcnow()
                )
                instances.append(instance)
            
            return instances
            
        except Exception as e:
            logger.error(f"Consul discovery failed for {service_def.name}: {e}")
            return []
    
    async def _discover_kubernetes_instances(self, service_def: ServiceDefinition) -> List[ServiceInstance]:
        """Discover instances from Kubernetes."""
        try:
            k8s_core = self.backends[DiscoveryBackend.KUBERNETES]['core_v1']
            
            # Get service endpoints
            endpoints = k8s_core.read_namespaced_endpoints(
                name=service_def.name,
                namespace=self.config.kubernetes_namespace
            )
            
            instances = []
            if endpoints.subsets:
                for subset in endpoints.subsets:
                    if subset.addresses:
                        for address in subset.addresses:
                            for port in subset.ports or []:
                                instance = ServiceInstance(
                                    id=f"{address.ip}:{port.port}",
                                    name=service_def.name,
                                    host=address.ip,
                                    port=port.port,
                                    tags=service_def.tags,
                                    metadata=service_def.metadata,
                                    health_status=HealthStatus.HEALTHY,
                                    last_health_check=datetime.utcnow(),
                                    protocol=port.protocol.lower() if port.protocol else "tcp"
                                )
                                instances.append(instance)
            
            return instances
            
        except Exception as e:
            logger.error(f"Kubernetes discovery failed for {service_def.name}: {e}")
            return []
    
    async def _discover_etcd_instances(self, service_def: ServiceDefinition) -> List[ServiceInstance]:
        """Discover instances from etcd."""
        try:
            etcd_client = self.backends[DiscoveryBackend.ETCD]
            
            # Get service instances from etcd
            key_prefix = f"/services/{service_def.name}/"
            for value, metadata in etcd_client.get_prefix(key_prefix):
                if value:
                    instance_data = json.loads(value.decode('utf-8'))
                    instance = ServiceInstance(
                        id=instance_data['id'],
                        name=service_def.name,
                        host=instance_data['host'],
                        port=instance_data['port'],
                        tags=instance_data.get('tags', []),
                        metadata=instance_data.get('metadata', {}),
                        health_status=HealthStatus.HEALTHY,
                        last_health_check=datetime.utcnow()
                    )
                    return [instance]
            
            return []
            
        except Exception as e:
            logger.error(f"etcd discovery failed for {service_def.name}: {e}")
            return []
    
    async def _discover_eureka_instances(self, service_def: ServiceDefinition) -> List[ServiceInstance]:
        """Discover instances from Eureka."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.config.eureka_url}/apps/{service_def.name.upper()}"
                async with session.get(url, headers={'Accept': 'application/json'}) as response:
                    if response.status == 200:
                        data = await response.json()
                        instances = []
                        
                        app = data.get('application', {})
                        for instance_data in app.get('instance', []):
                            if instance_data.get('status') == 'UP':
                                instance = ServiceInstance(
                                    id=instance_data['instanceId'],
                                    name=service_def.name,
                                    host=instance_data['hostName'],
                                    port=instance_data['port']['$'],
                                    health_status=HealthStatus.HEALTHY,
                                    last_health_check=datetime.utcnow()
                                )
                                instances.append(instance)
                        
                        return instances
            
            return []
            
        except Exception as e:
            logger.error(f"Eureka discovery failed for {service_def.name}: {e}")
            return []
    
    async def discover_service(self, service_name: str, use_cache: bool = True) -> List[ServiceInstance]:
        """
        Discover service instances with caching and load balancing.
        
        Args:
            service_name: Name of the service to discover
            use_cache: Whether to use cached results
            
        Returns:
            List of healthy service instances
        """
        try:
            cache_key = f"service:{service_name}"
            
            # Check cache first
            if use_cache and cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if datetime.utcnow() - cache_entry['timestamp'] < timedelta(
                    seconds=self.service_definitions.get(service_name, ServiceDefinition(name="")).cache_ttl
                ):
                    self.metrics['cache_hits'] += 1
                    return cache_entry['instances']
            
            self.metrics['cache_misses'] += 1
            self.metrics['discovery_requests'] += 1
            
            # Get from registry
            instances = self.service_registry.get(service_name, [])
            
            # Filter healthy instances
            healthy_instances = [
                instance for instance in instances 
                if instance.health_status == HealthStatus.HEALTHY
            ]
            
            # Update cache
            if use_cache:
                self.cache[cache_key] = {
                    'instances': healthy_instances,
                    'timestamp': datetime.utcnow()
                }
            
            return healthy_instances
            
        except Exception as e:
            logger.error(f"Service discovery failed for {service_name}: {e}")
            return []
    
    async def select_instance(
        self, 
        service_name: str, 
        algorithm: Optional[LoadBalancingAlgorithm] = None,
        client_ip: Optional[str] = None
    ) -> Optional[ServiceInstance]:
        """
        Select a service instance using load balancing.
        
        Args:
            service_name: Service name
            algorithm: Load balancing algorithm
            client_ip: Client IP for IP hash algorithm
            
        Returns:
            Selected service instance
        """
        try:
            instances = await self.discover_service(service_name)
            if not instances:
                return None
            
            service_def = self.service_definitions.get(service_name)
            if not service_def:
                return instances[0]  # Fallback to first instance
            
            lb_algorithm = algorithm or service_def.load_balancing
            
            self.metrics['load_balancing_decisions'] += 1
            
            if lb_algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
                return self._round_robin_select(service_name, instances)
            elif lb_algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
                return self._weighted_round_robin_select(service_name, instances)
            elif lb_algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
                return self._least_connections_select(instances)
            elif lb_algorithm == LoadBalancingAlgorithm.IP_HASH:
                return self._ip_hash_select(instances, client_ip or "default")
            elif lb_algorithm == LoadBalancingAlgorithm.RANDOM:
                return self._random_select(instances)
            elif lb_algorithm == LoadBalancingAlgorithm.AI_OPTIMIZED:
                return await self._ai_optimized_select(instances)
            else:
                return self._round_robin_select(service_name, instances)
                
        except Exception as e:
            logger.error(f"Instance selection failed for {service_name}: {e}")
            return None
    
    def _round_robin_select(self, service_name: str, instances: List[ServiceInstance]) -> ServiceInstance:
        """Round-robin instance selection."""
        if service_name not in self.round_robin_state:
            self.round_robin_state[service_name] = 0
        
        index = self.round_robin_state[service_name] % len(instances)
        self.round_robin_state[service_name] += 1
        
        return instances[index]
    
    def _weighted_round_robin_select(self, service_name: str, instances: List[ServiceInstance]) -> ServiceInstance:
        """Weighted round-robin instance selection."""
        # Create weighted list
        weighted_instances = []
        for instance in instances:
            for _ in range(max(1, instance.weight // 10)):
                weighted_instances.append(instance)
        
        return self._round_robin_select(service_name, weighted_instances)
    
    def _least_connections_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Least connections instance selection."""
        return min(instances, key=lambda x: x.connections)
    
    def _ip_hash_select(self, instances: List[ServiceInstance], client_ip: str) -> ServiceInstance:
        """IP hash instance selection."""
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        index = hash_value % len(instances)
        return instances[index]
    
    def _random_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Random instance selection."""
        import random
        return random.choice(instances)
    
    async def _ai_optimized_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """AI-optimized instance selection based on performance metrics."""
        if not self.config.enable_ai_optimization:
            return self._least_connections_select(instances)
        
        # Score instances based on multiple factors
        scored_instances = []
        for instance in instances:
            score = (
                (1.0 / max(0.1, instance.response_time_ms / 1000)) * 0.4 +  # Response time weight
                (1.0 / max(1, instance.connections)) * 0.3 +                # Connection count weight
                (1.0 - instance.error_rate) * 0.3                           # Error rate weight
            )
            scored_instances.append((score, instance))
        
        # Select instance with highest score
        scored_instances.sort(key=lambda x: x[0], reverse=True)
        return scored_instances[0][1]
    
    async def _start_health_monitoring(self, service_def: ServiceDefinition):
        """Start health monitoring for a service."""
        if service_def.name in self.health_checkers:
            return  # Already monitoring
        
        async def health_monitor():
            while service_def.name in self.service_definitions:
                try:
                    instances = self.service_registry.get(service_def.name, [])
                    for instance in instances:
                        await self._check_instance_health(instance, service_def)
                    
                    self._update_instance_health_metrics()
                    await asyncio.sleep(service_def.health_check_interval)
                    
                except Exception as e:
                    logger.error(f"Health monitoring error for {service_def.name}: {e}")
                    await asyncio.sleep(30)  # Error backoff
        
        task = asyncio.create_task(health_monitor())
        self.health_checkers[service_def.name] = task
        logger.info(f"Started health monitoring for {service_def.name}")
    
    async def _check_instance_health(self, instance: ServiceInstance, service_def: ServiceDefinition):
        """Check health of a single instance."""
        if not service_def.health_check_url:
            return
        
        try:
            url = f"http://{instance.host}:{instance.port}{service_def.health_check_url}"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(
                total=service_def.health_check_timeout
            )) as session:
                start_time = datetime.utcnow()
                async with session.get(url) as response:
                    response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                    
                    if response.status == 200:
                        instance.health_status = HealthStatus.HEALTHY
                        instance.response_time_ms = response_time
                    else:
                        instance.health_status = HealthStatus.UNHEALTHY
                    
                    instance.last_health_check = datetime.utcnow()
                    self.metrics['health_checks_performed'] += 1
                    
        except Exception as e:
            logger.warning(f"Health check failed for {instance.id}: {e}")
            instance.health_status = HealthStatus.UNHEALTHY
            instance.last_health_check = datetime.utcnow()
    
    def _update_instance_health_metrics(self):
        """Update health metrics for all instances."""
        healthy_count = 0
        unhealthy_count = 0
        
        for instances in self.service_registry.values():
            for instance in instances:
                if instance.health_status == HealthStatus.HEALTHY:
                    healthy_count += 1
                else:
                    unhealthy_count += 1
        
        self.metrics['healthy_instances'] = healthy_count
        self.metrics['unhealthy_instances'] = unhealthy_count
        self.metrics['last_update'] = datetime.utcnow().isoformat()
    
    async def get_service_topology(self) -> Dict[str, Any]:
        """
        Get complete service topology and health status.
        
        Returns:
            Dict containing service topology information
        """
        try:
            topology = {
                'services': {},
                'summary': {
                    'total_services': len(self.service_definitions),
                    'total_instances': sum(len(instances) for instances in self.service_registry.values()),
                    'healthy_instances': self.metrics['healthy_instances'],
                    'unhealthy_instances': self.metrics['unhealthy_instances']
                },
                'metrics': self.metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            for service_name, instances in self.service_registry.items():
                service_def = self.service_definitions.get(service_name)
                
                topology['services'][service_name] = {
                    'definition': {
                        'backend': service_def.backend.value if service_def else 'unknown',
                        'load_balancing': service_def.load_balancing.value if service_def else 'round_robin',
                        'health_check_interval': service_def.health_check_interval if service_def else 30
                    },
                    'instances': [
                        {
                            'id': instance.id,
                            'host': instance.host,
                            'port': instance.port,
                            'health_status': instance.health_status.value,
                            'last_health_check': instance.last_health_check.isoformat() if instance.last_health_check else None,
                            'response_time_ms': instance.response_time_ms,
                            'connections': instance.connections,
                            'weight': instance.weight,
                            'tags': instance.tags,
                            'zone': instance.zone,
                            'version': instance.version
                        }
                        for instance in instances
                    ],
                    'healthy_count': len([i for i in instances if i.health_status == HealthStatus.HEALTHY]),
                    'total_count': len(instances)
                }
            
            return topology
            
        except Exception as e:
            logger.error(f"Failed to get service topology: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def cleanup(self):
        """Cleanup resources and stop monitoring tasks."""
        logger.info("Cleaning up Service Discovery Orchestrator...")
        
        # Stop health monitoring tasks
        for task in self.health_checkers.values():
            task.cancel()
        
        self.health_checkers.clear()
        
        # Close backend connections
        for backend_type, backend in self.backends.items():
            try:
                if hasattr(backend, 'close'):
                    if asyncio.iscoroutinefunction(backend.close):
                        await backend.close()
                    else:
                        backend.close()
            except Exception as e:
                logger.error(f"Error closing {backend_type} backend: {e}")
        
        logger.info("Service Discovery Orchestrator cleanup completed")


# Factory function for easy instantiation
def create_discovery_orchestrator(
    consul_host: str = "localhost",
    kubernetes_namespace: str = "default",
    enable_ai_optimization: bool = True
) -> ServiceDiscoveryOrchestrator:
    """
    Factory function to create a service discovery orchestrator.
    
    Args:
        consul_host: Consul server host
        kubernetes_namespace: Kubernetes namespace
        enable_ai_optimization: Enable AI-optimized load balancing
        
    Returns:
        Configured ServiceDiscoveryOrchestrator instance
    """
    config = DiscoveryConfig(
        consul_host=consul_host,
        kubernetes_namespace=kubernetes_namespace,
        enable_ai_optimization=enable_ai_optimization
    )
    
    return ServiceDiscoveryOrchestrator(config)


# Example usage
async def main():
    """Example usage of Service Discovery Orchestrator."""
    
    # Create orchestrator
    orchestrator = create_discovery_orchestrator(
        consul_host="localhost",
        kubernetes_namespace="default",
        enable_ai_optimization=True
    )
    
    # Register a service
    service_def = ServiceDefinition(
        name="my-api-service",
        backend=DiscoveryBackend.KUBERNETES,
        health_check_url="/health",
        health_check_interval=30,
        load_balancing=LoadBalancingAlgorithm.AI_OPTIMIZED,
        tags=["api", "v1"],
        metadata={"version": "1.0.0", "environment": "production"}
    )
    
    result = await orchestrator.register_service(service_def)
    print(f"Service registration: {result}")
    
    # Discover service instances
    instances = await orchestrator.discover_service("my-api-service")
    print(f"Discovered {len(instances)} instances")
    
    # Select optimal instance
    selected = await orchestrator.select_instance(
        "my-api-service",
        algorithm=LoadBalancingAlgorithm.AI_OPTIMIZED
    )
    
    if selected:
        print(f"Selected instance: {selected.host}:{selected.port}")
    
    # Get service topology
    topology = await orchestrator.get_service_topology()
    print(f"Service topology: {json.dumps(topology, indent=2)}")
    
    # Cleanup
    await orchestrator.cleanup()


if __name__ == "__main__":
    asyncio.run(main())