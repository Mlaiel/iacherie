"""🕸️ Microservice Mesh Integration - Service Mesh ML Coordination
================================================================
Module: ml/deployment/microservice_mesh_integration.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🕸️ MICROSERVICE MESH INTEGRATION
Advanced service mesh integration for ML workloads
- Istio/Linkerd service mesh coordination
- ML-aware traffic routing and load balancing
- Cross-service ML pipeline orchestration
- Service discovery for ML components
- Circuit breakers and retry policies for ML services
- Distributed tracing for ML requests
"""

import asyncio
import logging
import json
import yaml
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import uuid
import hashlib
import time
from collections import defaultdict, deque
import aiohttp
import kubernetes
from kubernetes import client, config
import requests

logger = logging.getLogger(__name__)

class ServiceMeshType(Enum):
    """Service mesh implementations"""
    ISTIO = "istio"
    LINKERD = "linkerd"
    CONSUL_CONNECT = "consul_connect"
    AWS_APP_MESH = "aws_app_mesh"
    CUSTOM = "custom"

class MLServiceType(Enum):
    """ML service types in the mesh"""
    INFERENCE_SERVICE = "inference_service"
    TRAINING_SERVICE = "training_service"
    PREPROCESSING_SERVICE = "preprocessing_service"
    FEATURE_SERVICE = "feature_service"
    MODEL_REGISTRY = "model_registry"
    EXPERIMENT_TRACKER = "experiment_tracker"
    MONITORING_SERVICE = "monitoring_service"
    PIPELINE_ORCHESTRATOR = "pipeline_orchestrator"

class TrafficPolicy(Enum):
    """Traffic routing policies for ML services"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    LATENCY_BASED = "latency_based"
    ML_AWARE = "ml_aware"
    CANARY = "canary"
    BLUE_GREEN = "blue_green"

class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class MLService:
    """ML service configuration in the mesh"""
    service_id: str
    name: str
    service_type: MLServiceType
    namespace: str
    version: str
    endpoints: List[str]
    health_check_path: str
    metrics_path: str
    dependencies: List[str] = field(default_factory=list)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    scaling_config: Dict[str, Any] = field(default_factory=dict)
    traffic_config: Dict[str, Any] = field(default_factory=dict)
    security_config: Dict[str, Any] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ServiceMeshConfig:
    """Service mesh configuration"""
    mesh_type: ServiceMeshType
    mesh_namespace: str
    gateway_config: Dict[str, Any]
    ingress_config: Dict[str, Any]
    egress_config: Dict[str, Any]
    security_policies: Dict[str, Any]
    observability_config: Dict[str, Any]
    traffic_management: Dict[str, Any]
    auto_injection: bool = True
    mtls_enabled: bool = True
    telemetry_enabled: bool = True

@dataclass
class MLPipeline:
    """ML pipeline configuration in the mesh"""
    pipeline_id: str
    name: str
    description: str
    services: List[str]  # Service IDs in order
    data_flow: Dict[str, List[str]]  # service_id -> [dependent_services]
    timeout_seconds: int = 300
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    circuit_breaker_config: Dict[str, Any] = field(default_factory=dict)
    monitoring_config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class TrafficSplit:
    """Traffic splitting configuration"""
    split_id: str
    service_id: str
    targets: Dict[str, float]  # version -> weight percentage
    conditions: Dict[str, Any] = field(default_factory=dict)
    duration_minutes: Optional[int] = None
    success_criteria: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration for ML services"""
    service_id: str
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 60
    success_threshold: int = 3
    timeout_seconds: int = 30
    max_concurrent_requests: int = 100
    error_rate_threshold: float = 0.5
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    success_count: int = 0

class MLServiceRegistry:
    """Registry for ML services in the mesh"""
    
    def __init__(self) -> None:
        self.services: Dict[str, MLService] = {}
        self.service_instances: Dict[str, List[Dict[str, Any]]] = {}
        self.health_status: Dict[str, bool] = {}
        self.metrics_cache: Dict[str, Dict[str, Any]] = {}
        
    def register_service(self, service: MLService) -> None:
        """Register ML service in the registry"""
        self.services[service.service_id] = service
        self.service_instances[service.service_id] = []
        self.health_status[service.service_id] = False
        logger.info(f"ML service registered: {service.service_id}")
    
    def discover_services(self, service_type: Optional[MLServiceType] = None) -> List[MLService]:
        """Discover ML services by type"""
        if service_type is None:
            return list(self.services.values())
        
        return [
            service for service in self.services.values()
            if service.service_type == service_type
        ]
    
    def get_healthy_instances(self, service_id: str) -> List[Dict[str, Any]]:
        """Get healthy instances of a service"""
        if service_id not in self.service_instances:
            return []
        
        return [
            instance for instance in self.service_instances[service_id]
            if instance.get('healthy', False)
        ]
    
    def update_health_status(self, service_id: str, healthy: bool) -> None:
        """Update service health status"""
        self.health_status[service_id] = healthy

class IstioMeshIntegrator:
    """Istio service mesh integration for ML workloads"""
    
    def __init__(self, kubernetes_config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.k8s_config = kubernetes_config or {}
        self.istio_namespace = self.k8s_config.get('istio_namespace', 'istio-system')
        
        # Initialize Kubernetes client
        try:
            if 'kubeconfig_path' in self.k8s_config:
                config.load_kube_config(self.k8s_config['kubeconfig_path'])
            else:
                config.load_incluster_config()
            
            self.k8s_client = client.ApiClient()
            self.custom_objects_api = client.CustomObjectsApi()
            self.apps_v1_api = client.AppsV1Api()
            
        except Exception as e:
            logger.warning(f"Could not initialize Kubernetes client: {e}")
            self.k8s_client = None
    
    async def create_virtual_service(
        self,
        service: MLService,
        traffic_policy: TrafficPolicy,
        routing_rules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create Istio VirtualService for ML service"""
        try:
            virtual_service = {
                'apiVersion': 'networking.istio.io/v1beta1',
                'kind': 'VirtualService',
                'metadata': {
                    'name': f"{service.name}-vs",
                    'namespace': service.namespace,
                    'labels': {
                        'ml-service': service.service_id,
                        'ml-type': service.service_type.value
                    }
                },
                'spec': {
                    'hosts': [service.name],
                    'http': self._build_http_routes(routing_rules, traffic_policy)
                }
            }
            
            if self.k8s_client:
                # Apply VirtualService to Kubernetes
                try:
                    await self._apply_k8s_resource(virtual_service)
                    logger.info(f"VirtualService created for {service.service_id}")
                except Exception as e:
                    logger.error(f"Failed to apply VirtualService: {e}")
            
            return virtual_service
            
        except Exception as e:
            logger.error(f"Error creating VirtualService: {e}")
            raise
    
    async def create_destination_rule(
        self,
        service: MLService,
        circuit_breaker_config: CircuitBreakerConfig,
        load_balancer_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create Istio DestinationRule for ML service"""
        try:
            destination_rule = {
                'apiVersion': 'networking.istio.io/v1beta1',
                'kind': 'DestinationRule',
                'metadata': {
                    'name': f"{service.name}-dr",
                    'namespace': service.namespace,
                    'labels': {
                        'ml-service': service.service_id,
                        'ml-type': service.service_type.value
                    }
                },
                'spec': {
                    'host': service.name,
                    'trafficPolicy': {
                        'loadBalancer': self._build_load_balancer_config(load_balancer_config),
                        'connectionPool': {
                            'tcp': {
                                'maxConnections': circuit_breaker_config.max_concurrent_requests
                            },
                            'http': {
                                'http1MaxPendingRequests': circuit_breaker_config.max_concurrent_requests,
                                'maxRequestsPerConnection': 10
                            }
                        },
                        'circuitBreaker': {
                            'consecutiveErrors': circuit_breaker_config.failure_threshold,
                            'interval': f"{circuit_breaker_config.recovery_timeout_seconds}s",
                            'baseEjectionTime': f"{circuit_breaker_config.recovery_timeout_seconds}s"
                        }
                    }
                }
            }
            
            if self.k8s_client:
                await self._apply_k8s_resource(destination_rule)
                logger.info(f"DestinationRule created for {service.service_id}")
            
            return destination_rule
            
        except Exception as e:
            logger.error(f"Error creating DestinationRule: {e}")
            raise
    
    async def setup_ml_gateway(
        self,
        gateway_name: str,
        namespace: str,
        hosts: List[str],
        tls_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Setup Istio Gateway for ML services"""
        try:
            gateway = {
                'apiVersion': 'networking.istio.io/v1beta1',
                'kind': 'Gateway',
                'metadata': {
                    'name': gateway_name,
                    'namespace': namespace,
                    'labels': {
                        'gateway-type': 'ml-services'
                    }
                },
                'spec': {
                    'selector': {
                        'istio': 'ingressgateway'
                    },
                    'servers': [
                        {
                            'port': {
                                'number': 443 if tls_config else 80,
                                'name': 'https' if tls_config else 'http',
                                'protocol': 'HTTPS' if tls_config else 'HTTP'
                            },
                            'hosts': hosts
                        }
                    ]
                }
            }
            
            if tls_config:
                gateway['spec']['servers'][0]['tls'] = tls_config
            
            if self.k8s_client:
                await self._apply_k8s_resource(gateway)
                logger.info(f"Gateway created: {gateway_name}")
            
            return gateway
            
        except Exception as e:
            logger.error(f"Error creating Gateway: {e}")
            raise
    
    def _build_http_routes(
        self,
        routing_rules: List[Dict[str, Any]],
        traffic_policy: TrafficPolicy
    ) -> List[Dict[str, Any]]:
        """Build HTTP routes for VirtualService"""
        routes = []
        
        for rule in routing_rules:
            route = {
                'match': [rule.get('match', [{'uri': {'prefix': '/'}}])],
                'route': []
            }
            
            # Build destination based on traffic policy
            if traffic_policy == TrafficPolicy.WEIGHTED:
                for destination in rule.get('destinations', []):
                    route['route'].append({
                        'destination': {
                            'host': destination['host'],
                            'subset': destination.get('subset')
                        },
                        'weight': destination.get('weight', 100)
                    })
            else:
                # Single destination for other policies
                destination = rule.get('destinations', [{}])[0]
                route['route'].append({
                    'destination': {
                        'host': destination.get('host'),
                        'subset': destination.get('subset')
                    }
                })
            
            # Add timeout and retry policies
            if 'timeout' in rule:
                route['timeout'] = rule['timeout']
            
            if 'retries' in rule:
                route['retries'] = rule['retries']
            
            routes.append(route)
        
        return routes
    
    def _build_load_balancer_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build load balancer configuration"""
        lb_config = {}
        
        policy = config.get('policy', 'ROUND_ROBIN')
        lb_config['simple'] = policy
        
        if policy == 'CONSISTENT_HASH':
            hash_config = config.get('hash_config', {})
            lb_config['consistentHash'] = hash_config
        
        return lb_config
    
    async def _apply_k8s_resource(self, resource: Dict[str, Any]) -> None:
        """Apply Kubernetes resource"""
        try:
            group = resource['apiVersion'].split('/')[0]
            version = resource['apiVersion'].split('/')[1]
            kind = resource['kind'].lower()
            namespace = resource['metadata']['namespace']
            name = resource['metadata']['name']
            
            # Check if resource exists
            try:
                existing = self.custom_objects_api.get_namespaced_custom_object(
                    group=group,
                    version=version,
                    namespace=namespace,
                    plural=f"{kind}s",
                    name=name
                )
                
                # Update existing resource
                self.custom_objects_api.patch_namespaced_custom_object(
                    group=group,
                    version=version,
                    namespace=namespace,
                    plural=f"{kind}s",
                    name=name,
                    body=resource
                )
                
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    # Create new resource
                    self.custom_objects_api.create_namespaced_custom_object(
                        group=group,
                        version=version,
                        namespace=namespace,
                        plural=f"{kind}s",
                        body=resource
                    )
                else:
                    raise e
                    
        except Exception as e:
            logger.error(f"Error applying Kubernetes resource: {e}")
            raise

class MicroserviceMeshIntegration:
    """Advanced microservice mesh integration for ML workloads"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize microservice mesh integration"""
        self.config = config or {}
        
        # Mesh configuration
        self.integration_id = str(uuid.uuid4())
        self.mesh_type = ServiceMeshType(self.config.get('mesh_type', 'istio'))
        self.mesh_namespace = self.config.get('mesh_namespace', 'istio-system')
        
        # Service management
        self.service_registry = MLServiceRegistry()
        self.pipelines: Dict[str, MLPipeline] = {}
        self.traffic_splits: Dict[str, TrafficSplit] = {}
        self.circuit_breakers: Dict[str, CircuitBreakerConfig] = {}
        
        # Mesh integrators
        self.istio_integrator = IstioMeshIntegrator(self.config.get('kubernetes', {}))
        
        # Monitoring and metrics
        self.mesh_metrics = defaultdict(dict)
        self.service_latencies = defaultdict(list)
        self.error_rates = defaultdict(float)
        
        # Request tracking
        self.active_requests: Dict[str, Dict[str, Any]] = {}
        self.request_traces: deque = deque(maxlen=10000)
        
        logger.info(f"Microservice Mesh Integration initialized: {self.integration_id}")

    async def register_ml_service(
        self,
        name: str,
        service_type: MLServiceType,
        namespace: str,
        version: str,
        endpoints: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register ML service in the mesh"""
        try:
            service_id = f"ml_service_{uuid.uuid4().hex[:12]}"
            
            # Create ML service configuration
            service = MLService(
                service_id=service_id,
                name=name,
                service_type=service_type,
                namespace=namespace,
                version=version,
                endpoints=endpoints,
                health_check_path=config.get('health_check_path', '/health') if config else '/health',
                metrics_path=config.get('metrics_path', '/metrics') if config else '/metrics',
                dependencies=config.get('dependencies', []) if config else [],
                resource_requirements=config.get('resource_requirements', {}) if config else {},
                scaling_config=config.get('scaling_config', {}) if config else {},
                traffic_config=config.get('traffic_config', {}) if config else {},
                security_config=config.get('security_config', {}) if config else {},
                labels=config.get('labels', {}) if config else {},
                annotations=config.get('annotations', {}) if config else {}
            )
            
            # Register in service registry
            self.service_registry.register_service(service)
            
            # Setup circuit breaker
            circuit_breaker = CircuitBreakerConfig(
                service_id=service_id,
                failure_threshold=config.get('circuit_breaker_failure_threshold', 5) if config else 5,
                recovery_timeout_seconds=config.get('circuit_breaker_timeout', 60) if config else 60
            )
            self.circuit_breakers[service_id] = circuit_breaker
            
            # Configure mesh integration based on type
            if self.mesh_type == ServiceMeshType.ISTIO:
                await self._setup_istio_integration(service, circuit_breaker)
            
            logger.info(f"ML service registered in mesh: {service_id}")
            return service_id
            
        except Exception as e:
            logger.error(f"Error registering ML service: {e}")
            raise

    async def _setup_istio_integration(
        self,
        service: MLService,
        circuit_breaker: CircuitBreakerConfig
    ) -> None:
        """Setup Istio integration for ML service"""
        try:
            # Create VirtualService for traffic routing
            routing_rules = [{
                'match': [{'uri': {'prefix': '/'}}],
                'destinations': [{'host': service.name, 'subset': service.version}],
                'timeout': '30s',
                'retries': {
                    'attempts': 3,
                    'perTryTimeout': '10s'
                }
            }]
            
            await self.istio_integrator.create_virtual_service(
                service=service,
                traffic_policy=TrafficPolicy.ROUND_ROBIN,
                routing_rules=routing_rules
            )
            
            # Create DestinationRule for load balancing and circuit breaking
            load_balancer_config = {
                'policy': 'ROUND_ROBIN'
            }
            
            await self.istio_integrator.create_destination_rule(
                service=service,
                circuit_breaker_config=circuit_breaker,
                load_balancer_config=load_balancer_config
            )
            
        except Exception as e:
            logger.error(f"Error setting up Istio integration: {e}")
            raise

    async def create_ml_pipeline(
        self,
        name: str,
        description: str,
        service_chain: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create ML pipeline with service mesh coordination"""
        try:
            pipeline_id = f"ml_pipeline_{uuid.uuid4().hex[:12]}"
            
            # Validate services exist
            for service_id in service_chain:
                if service_id not in self.service_registry.services:
                    raise ValueError(f"Service not found: {service_id}")
            
            # Build data flow graph
            data_flow = {}
            for i, service_id in enumerate(service_chain):
                if i < len(service_chain) - 1:
                    data_flow[service_id] = [service_chain[i + 1]]
                else:
                    data_flow[service_id] = []
            
            # Create pipeline configuration
            pipeline = MLPipeline(
                pipeline_id=pipeline_id,
                name=name,
                description=description,
                services=service_chain,
                data_flow=data_flow,
                timeout_seconds=config.get('timeout_seconds', 300) if config else 300,
                retry_policy=config.get('retry_policy', {}) if config else {},
                circuit_breaker_config=config.get('circuit_breaker_config', {}) if config else {},
                monitoring_config=config.get('monitoring_config', {}) if config else {}
            )
            
            self.pipelines[pipeline_id] = pipeline
            
            # Setup pipeline monitoring
            await self._setup_pipeline_monitoring(pipeline)
            
            logger.info(f"ML pipeline created: {pipeline_id}")
            return pipeline_id
            
        except Exception as e:
            logger.error(f"Error creating ML pipeline: {e}")
            raise

    async def execute_pipeline(
        self,
        pipeline_id: str,
        input_data: Dict[str, Any],
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute ML pipeline through service mesh"""
        try:
            if pipeline_id not in self.pipelines:
                raise ValueError(f"Pipeline not found: {pipeline_id}")
            
            pipeline = self.pipelines[pipeline_id]
            
            if trace_id is None:
                trace_id = str(uuid.uuid4())
            
            # Initialize request tracking
            request_context = {
                'trace_id': trace_id,
                'pipeline_id': pipeline_id,
                'start_time': datetime.now(),
                'services_called': [],
                'latencies': {},
                'errors': []
            }
            
            self.active_requests[trace_id] = request_context
            
            # Execute pipeline services in order
            current_data = input_data
            
            for service_id in pipeline.services:
                service = self.service_registry.services[service_id]
                
                # Call service through mesh
                service_start_time = time.time()
                
                try:
                    current_data = await self._call_service_through_mesh(
                        service=service,
                        input_data=current_data,
                        trace_id=trace_id
                    )
                    
                    # Record success metrics
                    latency = (time.time() - service_start_time) * 1000
                    request_context['latencies'][service_id] = latency
                    request_context['services_called'].append(service_id)
                    
                    self.service_latencies[service_id].append(latency)
                    
                except Exception as e:
                    # Record error and handle circuit breaker
                    request_context['errors'].append({
                        'service_id': service_id,
                        'error': str(e),
                        'timestamp': datetime.now()
                    })
                    
                    await self._handle_service_failure(service_id, str(e))
                    raise e
            
            # Complete request tracking
            total_latency = (datetime.now() - request_context['start_time']).total_seconds() * 1000
            request_context['total_latency'] = total_latency
            request_context['success'] = True
            
            # Store trace
            self.request_traces.append(request_context)
            
            # Clean up active request
            del self.active_requests[trace_id]
            
            return current_data
            
        except Exception as e:
            # Record failure
            if trace_id in self.active_requests:
                self.active_requests[trace_id]['success'] = False
                self.active_requests[trace_id]['error'] = str(e)
                self.request_traces.append(self.active_requests[trace_id])
                del self.active_requests[trace_id]
            
            logger.error(f"Error executing pipeline: {e}")
            raise

    async def _call_service_through_mesh(
        self,
        service: MLService,
        input_data: Dict[str, Any],
        trace_id: str
    ) -> Dict[str, Any]:
        """Call ML service through service mesh"""
        try:
            # Check circuit breaker
            circuit_breaker = self.circuit_breakers.get(service.service_id)
            if circuit_breaker and circuit_breaker.state == CircuitBreakerState.OPEN:
                if not self._should_attempt_circuit_breaker_reset(circuit_breaker):
                    raise Exception(f"Circuit breaker open for service: {service.service_id}")
                else:
                    circuit_breaker.state = CircuitBreakerState.HALF_OPEN
            
            # Get healthy service instances
            healthy_instances = self.service_registry.get_healthy_instances(service.service_id)
            if not healthy_instances:
                # Fallback to configured endpoints
                healthy_instances = [{'endpoint': ep} for ep in service.endpoints]
            
            if not healthy_instances:
                raise Exception(f"No healthy instances for service: {service.service_id}")
            
            # Select instance (simple round-robin)
            instance = healthy_instances[0]
            endpoint = instance.get('endpoint', service.endpoints[0])
            
            # Prepare request
            headers = {
                'X-Trace-ID': trace_id,
                'Content-Type': 'application/json',
                'X-Service-Mesh': 'true'
            }
            
            # Add service mesh headers for Istio
            if self.mesh_type == ServiceMeshType.ISTIO:
                headers.update({
                    'X-Request-ID': str(uuid.uuid4()),
                    'X-B3-TraceId': trace_id,
                    'X-B3-SpanId': str(uuid.uuid4().hex[:16])
                })
            
            # Simulate service call (in production, use actual HTTP client)
            await asyncio.sleep(0.01)  # Simulate network latency
            
            # Simulate service processing
            if service.service_type == MLServiceType.PREPROCESSING_SERVICE:
                response = {
                    'preprocessed_data': input_data,
                    'preprocessing_metadata': {
                        'service_id': service.service_id,
                        'version': service.version,
                        'timestamp': datetime.now().isoformat()
                    }
                }
            elif service.service_type == MLServiceType.INFERENCE_SERVICE:
                response = {
                    'predictions': [0.8, 0.2],  # Mock predictions
                    'model_metadata': {
                        'service_id': service.service_id,
                        'version': service.version,
                        'confidence': 0.9
                    }
                }
            elif service.service_type == MLServiceType.FEATURE_SERVICE:
                response = {
                    'features': {
                        'feature_1': 1.5,
                        'feature_2': 0.8,
                        'feature_3': -0.3
                    },
                    'feature_metadata': {
                        'service_id': service.service_id,
                        'version': service.version
                    }
                }
            else:
                response = {
                    'processed_data': input_data,
                    'service_metadata': {
                        'service_id': service.service_id,
                        'version': service.version
                    }
                }
            
            # Record successful call
            if circuit_breaker:
                if circuit_breaker.state == CircuitBreakerState.HALF_OPEN:
                    circuit_breaker.success_count += 1
                    if circuit_breaker.success_count >= circuit_breaker.success_threshold:
                        circuit_breaker.state = CircuitBreakerState.CLOSED
                        circuit_breaker.failure_count = 0
                        circuit_breaker.success_count = 0
                elif circuit_breaker.state == CircuitBreakerState.CLOSED:
                    circuit_breaker.failure_count = 0
            
            return response
            
        except Exception as e:
            # Record failure
            if circuit_breaker:
                circuit_breaker.failure_count += 1
                circuit_breaker.last_failure_time = datetime.now()
                
                if circuit_breaker.failure_count >= circuit_breaker.failure_threshold:
                    circuit_breaker.state = CircuitBreakerState.OPEN
            
            logger.error(f"Error calling service through mesh: {e}")
            raise

    def _should_attempt_circuit_breaker_reset(self, circuit_breaker: CircuitBreakerConfig) -> bool:
        """Check if circuit breaker should attempt reset"""
        if circuit_breaker.last_failure_time is None:
            return True
        
        time_since_failure = datetime.now() - circuit_breaker.last_failure_time
        return time_since_failure.seconds >= circuit_breaker.recovery_timeout_seconds

    async def _handle_service_failure(self, service_id: str, error: str) -> None:
        """Handle service failure and update metrics"""
        try:
            # Update error rates
            current_error_rate = self.error_rates.get(service_id, 0.0)
            self.error_rates[service_id] = min(1.0, current_error_rate + 0.1)
            
            # Update service health
            self.service_registry.update_health_status(service_id, False)
            
            # Log failure for monitoring
            failure_event = {
                'service_id': service_id,
                'error': error,
                'timestamp': datetime.now(),
                'error_rate': self.error_rates[service_id]
            }
            
            logger.warning(f"Service failure recorded: {failure_event}")
            
        except Exception as e:
            logger.error(f"Error handling service failure: {e}")

    async def setup_traffic_split(
        self,
        service_id: str,
        targets: Dict[str, float],
        duration_minutes: Optional[int] = None,
        conditions: Optional[Dict[str, Any]] = None
    ) -> str:
        """Setup traffic splitting for A/B testing"""
        try:
            split_id = f"traffic_split_{uuid.uuid4().hex[:12]}"
            
            # Validate service exists
            if service_id not in self.service_registry.services:
                raise ValueError(f"Service not found: {service_id}")
            
            # Validate traffic percentages
            total_percentage = sum(targets.values())
            if abs(total_percentage - 1.0) > 0.01:
                raise ValueError(f"Traffic percentages must sum to 1.0, got {total_percentage}")
            
            # Create traffic split configuration
            traffic_split = TrafficSplit(
                split_id=split_id,
                service_id=service_id,
                targets=targets,
                conditions=conditions or {},
                duration_minutes=duration_minutes
            )
            
            self.traffic_splits[split_id] = traffic_split
            
            # Apply traffic split to mesh
            if self.mesh_type == ServiceMeshType.ISTIO:
                await self._apply_istio_traffic_split(traffic_split)
            
            logger.info(f"Traffic split configured: {split_id}")
            return split_id
            
        except Exception as e:
            logger.error(f"Error setting up traffic split: {e}")
            raise

    async def _apply_istio_traffic_split(self, traffic_split: TrafficSplit) -> None:
        """Apply traffic split configuration to Istio"""
        try:
            service = self.service_registry.services[traffic_split.service_id]
            
            # Build routing rules with weights
            routing_rules = [{
                'match': [{'uri': {'prefix': '/'}}],
                'destinations': [
                    {
                        'host': service.name,
                        'subset': target,
                        'weight': int(weight * 100)
                    }
                    for target, weight in traffic_split.targets.items()
                ]
            }]
            
            # Update VirtualService with weighted routing
            await self.istio_integrator.create_virtual_service(
                service=service,
                traffic_policy=TrafficPolicy.WEIGHTED,
                routing_rules=routing_rules
            )
            
        except Exception as e:
            logger.error(f"Error applying Istio traffic split: {e}")
            raise

    async def _setup_pipeline_monitoring(self, pipeline: MLPipeline) -> None:
        """Setup monitoring for ML pipeline"""
        try:
            # Initialize pipeline metrics
            self.mesh_metrics[pipeline.pipeline_id] = {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'avg_latency_ms': 0.0,
                'service_metrics': {}
            }
            
            # Initialize service metrics within pipeline
            for service_id in pipeline.services:
                self.mesh_metrics[pipeline.pipeline_id]['service_metrics'][service_id] = {
                    'calls': 0,
                    'errors': 0,
                    'avg_latency_ms': 0.0
                }
            
        except Exception as e:
            logger.error(f"Error setting up pipeline monitoring: {e}")

    async def get_service_mesh_analytics(self) -> Dict[str, Any]:
        """Get comprehensive service mesh analytics"""
        try:
            # Calculate aggregate metrics
            total_services = len(self.service_registry.services)
            healthy_services = sum(1 for healthy in self.service_registry.health_status.values() if healthy)
            
            total_pipelines = len(self.pipelines)
            active_traffic_splits = len([ts for ts in self.traffic_splits.values() if ts.duration_minutes is None or 
                                        (datetime.now() - ts.created_at).seconds < ts.duration_minutes * 60])
            
            # Calculate service latencies
            avg_service_latencies = {}
            for service_id, latencies in self.service_latencies.items():
                if latencies:
                    avg_service_latencies[service_id] = sum(latencies) / len(latencies)
            
            # Calculate error rates
            total_error_rate = sum(self.error_rates.values()) / max(len(self.error_rates), 1)
            
            return {
                'integration_id': self.integration_id,
                'mesh_type': self.mesh_type.value,
                'total_services': total_services,
                'healthy_services': healthy_services,
                'unhealthy_services': total_services - healthy_services,
                'total_pipelines': total_pipelines,
                'active_traffic_splits': active_traffic_splits,
                'total_circuit_breakers': len(self.circuit_breakers),
                'open_circuit_breakers': len([cb for cb in self.circuit_breakers.values() 
                                            if cb.state == CircuitBreakerState.OPEN]),
                'avg_service_latencies_ms': avg_service_latencies,
                'service_error_rates': dict(self.error_rates),
                'overall_error_rate': total_error_rate,
                'total_requests_traced': len(self.request_traces),
                'active_requests': len(self.active_requests),
                'mesh_health_score': (healthy_services / max(total_services, 1)) * (1 - total_error_rate)
            }
            
        except Exception as e:
            logger.error(f"Error getting service mesh analytics: {e}")
            return {}

    async def get_pipeline_metrics(self, pipeline_id: str) -> Dict[str, Any]:
        """Get metrics for specific ML pipeline"""
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        if pipeline_id not in self.mesh_metrics:
            return {}
        
        pipeline_metrics = self.mesh_metrics[pipeline_id].copy()
        
        # Add pipeline configuration info
        pipeline = self.pipelines[pipeline_id]
        pipeline_metrics['pipeline_info'] = {
            'name': pipeline.name,
            'services': pipeline.services,
            'created_at': pipeline.created_at.isoformat(),
            'service_count': len(pipeline.services)
        }
        
        return pipeline_metrics

    async def cleanup_expired_traffic_splits(self) -> int:
        """Clean up expired traffic splits"""
        cleaned_count = 0
        current_time = datetime.now()
        
        expired_splits = []
        for split_id, traffic_split in self.traffic_splits.items():
            if traffic_split.duration_minutes is not None:
                duration = (current_time - traffic_split.created_at).seconds / 60
                if duration >= traffic_split.duration_minutes:
                    expired_splits.append(split_id)
        
        for split_id in expired_splits:
            del self.traffic_splits[split_id]
            cleaned_count += 1
            logger.info(f"Expired traffic split cleaned up: {split_id}")
        
        return cleaned_count

# Global mesh integration instance
_mesh_integration_instance = None

def get_mesh_integration() -> MicroserviceMeshIntegration:
    """Get global mesh integration instance"""
    global _mesh_integration_instance
    if _mesh_integration_instance is None:
        _mesh_integration_instance = MicroserviceMeshIntegration()
    return _mesh_integration_instance

# Test and validation functions
async def test_microservice_mesh_integration() -> None:
    """Test microservice mesh integration functionality"""
    mesh = MicroserviceMeshIntegration({
        'mesh_type': 'istio',
        'mesh_namespace': 'istio-system'
    })
    
    # Register ML services
    preprocessing_service_id = await mesh.register_ml_service(
        name="content-preprocessor",
        service_type=MLServiceType.PREPROCESSING_SERVICE,
        namespace="ml-services",
        version="v1",
        endpoints=["http://preprocessor:8080"]
    )
    
    inference_service_id = await mesh.register_ml_service(
        name="content-classifier",
        service_type=MLServiceType.INFERENCE_SERVICE,
        namespace="ml-services",
        version="v1",
        endpoints=["http://classifier:8080"]
    )
    
    # Create ML pipeline
    pipeline_id = await mesh.create_ml_pipeline(
        name="Content Classification Pipeline",
        description="End-to-end content classification",
        service_chain=[preprocessing_service_id, inference_service_id]
    )
    
    # Setup traffic split for A/B testing
    traffic_split_id = await mesh.setup_traffic_split(
        service_id=inference_service_id,
        targets={"v1": 0.8, "v2": 0.2},
        duration_minutes=60
    )
    
    # Execute pipeline
    result = await mesh.execute_pipeline(
        pipeline_id=pipeline_id,
        input_data={"content": "Sample content for classification"}
    )
    
    # Get analytics
    analytics = await mesh.get_service_mesh_analytics()
    pipeline_metrics = await mesh.get_pipeline_metrics(pipeline_id)
    
    logger.info("Microservice mesh integration test completed successfully")
    return {
        'preprocessing_service_id': preprocessing_service_id,
        'inference_service_id': inference_service_id,
        'pipeline_id': pipeline_id,
        'traffic_split_id': traffic_split_id,
        'pipeline_result': result,
        'mesh_health_score': analytics.get('mesh_health_score', 0.0),
        'total_services': analytics.get('total_services', 0)
    }

if __name__ == "__main__":
    # Run test
    asyncio.run(test_microservice_mesh_integration())