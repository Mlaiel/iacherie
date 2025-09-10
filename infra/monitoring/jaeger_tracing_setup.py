# Ainflue Infrastructure Module - Jaeger Tracing Setup
# ===================================================
# 
# Enterprise-grade distributed tracing setup for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Jaeger Tracing Setup - Enterprise Distributed Tracing

Provides comprehensive distributed tracing capabilities including:
- Jaeger collector and agent configuration
- Trace sampling and storage management
- Service mesh integration
- Performance monitoring and alerting
- Trace analytics and visualization
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml
import requests
from pathlib import Path
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TracingBackend(Enum):
    """Tracing backend enumeration"""
    ELASTICSEARCH = "elasticsearch"
    CASSANDRA = "cassandra"
    KAFKA = "kafka"
    MEMORY = "memory"
    BADGER = "badger"

class SamplingStrategy(Enum):
    """Sampling strategy enumeration"""
    CONST = "const"
    PROBABILISTIC = "probabilistic"
    RATE_LIMITING = "ratelimiting"
    ADAPTIVE = "adaptive"

class SpanKind(Enum):
    """Span kind enumeration"""
    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"

@dataclass
class TracingConfig:
    """Tracing configuration dataclass"""
    service_name: str
    collector_endpoint: str = "http://jaeger-collector:14268/api/traces"
    agent_endpoint: str = "jaeger-agent:6831"
    sampling_strategy: SamplingStrategy = SamplingStrategy.PROBABILISTIC
    sampling_rate: float = 0.1
    max_tag_value_length: int = 256
    max_traces_per_second: int = 100
    enabled: bool = True

@dataclass
class JaegerComponent:
    """Jaeger component configuration"""
    name: str
    image: str
    version: str
    ports: List[int] = field(default_factory=list)
    environment_vars: Dict[str, str] = field(default_factory=dict)
    resources: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True

@dataclass
class TraceMetrics:
    """Trace metrics dataclass"""
    service_name: str
    operation_name: str
    trace_count: int
    error_count: int
    avg_duration_ms: float
    p95_duration_ms: float
    p99_duration_ms: float
    timestamp: datetime = field(default_factory=datetime.now)

class JaegerTracingSetup:
    """
    Enterprise Jaeger Tracing Setup
    
    Manages Jaeger distributed tracing infrastructure including
    collectors, agents, storage backends, and monitoring integration.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Jaeger tracing setup"""
        self.config_path = config_path or "/home/runner/work/Ainflue/Ainflue/infra/monitoring"
        self.jaeger_config: Dict[str, Any] = {}
        self.components: Dict[str, JaegerComponent] = {}
        self.trace_configs: Dict[str, TracingConfig] = {}
        self.metrics_history: List[TraceMetrics] = []
        
        # Enterprise configuration
        self.backend = TracingBackend.ELASTICSEARCH
        self.retention_days = 30
        self.storage_max_traces = 1000000
        self.ui_enabled = True
        
        # Jaeger endpoints
        self.collector_endpoint = "http://jaeger-collector:14268"
        self.query_endpoint = "http://jaeger-query:16686"
        self.agent_endpoint = "jaeger-agent:6831"
        
        # Initialize Jaeger setup
        self._initialize_jaeger()
    
    def _initialize_jaeger(self) -> None:
        """Initialize Jaeger tracing setup"""
        try:
            # Configure Jaeger components
            self._configure_jaeger_components()
            
            # Setup storage backend
            self._configure_storage_backend()
            
            # Configure sampling strategies
            self._configure_sampling_strategies()
            
            # Generate Kubernetes manifests
            self._generate_kubernetes_manifests()
            
            logger.info("Jaeger tracing setup initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Jaeger setup: {e}")
            raise
    
    def _configure_jaeger_components(self) -> None:
        """Configure Jaeger components"""
        try:
            # Jaeger Collector
            collector = JaegerComponent(
                name="jaeger-collector",
                image="jaegertracing/jaeger-collector",
                version="1.53.0",
                ports=[14268, 14250, 9411],
                environment_vars={
                    "SPAN_STORAGE_TYPE": self.backend.value,
                    "COLLECTOR_ZIPKIN_HOST_PORT": ":9411",
                    "COLLECTOR_OTLP_ENABLED": "true"
                },
                resources={
                    "requests": "memory=256Mi,cpu=100m",
                    "limits": "memory=512Mi,cpu=500m"
                }
            )
            
            # Jaeger Query/UI
            query = JaegerComponent(
                name="jaeger-query",
                image="jaegertracing/jaeger-query",
                version="1.53.0",
                ports=[16686, 16687],
                environment_vars={
                    "SPAN_STORAGE_TYPE": self.backend.value,
                    "QUERY_BASE_PATH": "/jaeger"
                },
                resources={
                    "requests": "memory=128Mi,cpu=50m",
                    "limits": "memory=256Mi,cpu=200m"
                }
            )
            
            # Jaeger Agent
            agent = JaegerComponent(
                name="jaeger-agent",
                image="jaegertracing/jaeger-agent",
                version="1.53.0",
                ports=[6831, 6832, 5778, 14271],
                environment_vars={
                    "REPORTER_GRPC_HOST_PORT": "jaeger-collector:14250"
                },
                resources={
                    "requests": "memory=64Mi,cpu=25m",
                    "limits": "memory=128Mi,cpu=100m"
                }
            )
            
            # Store components
            self.components = {
                "collector": collector,
                "query": query,
                "agent": agent
            }
            
            # Add backend-specific components
            if self.backend == TracingBackend.ELASTICSEARCH:
                self._add_elasticsearch_component()
            elif self.backend == TracingBackend.CASSANDRA:
                self._add_cassandra_component()
            
            logger.info(f"Configured {len(self.components)} Jaeger components")
            
        except Exception as e:
            logger.error(f"Failed to configure Jaeger components: {e}")
            raise
    
    def _add_elasticsearch_component(self) -> None:
        """Add Elasticsearch component for storage"""
        elasticsearch = JaegerComponent(
            name="elasticsearch",
            image="docker.elastic.co/elasticsearch/elasticsearch",
            version="8.11.0",
            ports=[9200, 9300],
            environment_vars={
                "discovery.type": "single-node",
                "ES_JAVA_OPTS": "-Xms512m -Xmx512m",
                "xpack.security.enabled": "false"
            },
            resources={
                "requests": "memory=1Gi,cpu=500m",
                "limits": "memory=2Gi,cpu=1000m"
            }
        )
        
        self.components["elasticsearch"] = elasticsearch
        
        # Update collector and query with Elasticsearch config
        es_config = {
            "ES_SERVER_URLS": "http://elasticsearch:9200",
            "ES_NUM_SHARDS": "3",
            "ES_NUM_REPLICAS": "1",
            "ES_INDEX_PREFIX": "jaeger"
        }
        
        self.components["collector"].environment_vars.update(es_config)
        self.components["query"].environment_vars.update(es_config)
    
    def _add_cassandra_component(self) -> None:
        """Add Cassandra component for storage"""
        cassandra = JaegerComponent(
            name="cassandra",
            image="cassandra",
            version="4.1",
            ports=[9042, 7000, 7001],
            environment_vars={
                "CASSANDRA_DC": "dc1",
                "CASSANDRA_RACK": "rack1",
                "CASSANDRA_CLUSTER_NAME": "jaeger"
            },
            resources={
                "requests": "memory=2Gi,cpu=500m",
                "limits": "memory=4Gi,cpu=1000m"
            }
        )
        
        self.components["cassandra"] = cassandra
        
        # Update collector and query with Cassandra config
        cassandra_config = {
            "CASSANDRA_SERVERS": "cassandra:9042",
            "CASSANDRA_KEYSPACE": "jaeger_v1_dc1",
            "CASSANDRA_LOCAL_DC": "dc1"
        }
        
        self.components["collector"].environment_vars.update(cassandra_config)
        self.components["query"].environment_vars.update(cassandra_config)
    
    def _configure_storage_backend(self) -> None:
        """Configure storage backend settings"""
        try:
            storage_config = {
                "backend": self.backend.value,
                "retention_days": self.retention_days,
                "max_traces": self.storage_max_traces
            }
            
            if self.backend == TracingBackend.ELASTICSEARCH:
                storage_config.update({
                    "index_cleaner_enabled": True,
                    "index_cleaner_num_days": self.retention_days,
                    "bulk_size": 5000000,
                    "bulk_workers": 5,
                    "bulk_flush_interval": "200ms"
                })
            elif self.backend == TracingBackend.CASSANDRA:
                storage_config.update({
                    "cassandra_consistency": "LOCAL_QUORUM",
                    "cassandra_local_dc": "dc1",
                    "cassandra_max_connections_per_host": 10
                })
            
            self.jaeger_config["storage"] = storage_config
            
            logger.info(f"Storage backend configured: {self.backend.value}")
            
        except Exception as e:
            logger.error(f"Failed to configure storage backend: {e}")
            raise
    
    def _configure_sampling_strategies(self) -> None:
        """Configure sampling strategies"""
        try:
            # Default sampling strategies
            sampling_strategies = {
                "default_strategy": {
                    "type": SamplingStrategy.PROBABILISTIC.value,
                    "param": 0.1
                },
                "per_service_strategies": [
                    {
                        "service": "ainflue-api",
                        "type": SamplingStrategy.PROBABILISTIC.value,
                        "param": 0.5
                    },
                    {
                        "service": "ainflue-ai-engine",
                        "type": SamplingStrategy.PROBABILISTIC.value,
                        "param": 1.0
                    },
                    {
                        "service": "ainflue-auth",
                        "type": SamplingStrategy.RATE_LIMITING.value,
                        "param": 100
                    }
                ],
                "per_operation_strategies": [
                    {
                        "service": "ainflue-api",
                        "operation": "POST /upload",
                        "type": SamplingStrategy.PROBABILISTIC.value,
                        "param": 1.0
                    },
                    {
                        "service": "ainflue-api",
                        "operation": "GET /health",
                        "type": SamplingStrategy.PROBABILISTIC.value,
                        "param": 0.01
                    }
                ]
            }
            
            self.jaeger_config["sampling"] = sampling_strategies
            
            # Save sampling strategies to file
            self._save_sampling_strategies(sampling_strategies)
            
            logger.info("Sampling strategies configured")
            
        except Exception as e:
            logger.error(f"Failed to configure sampling strategies: {e}")
            raise
    
    def _save_sampling_strategies(self, strategies: Dict[str, Any]) -> None:
        """Save sampling strategies to file"""
        try:
            strategies_file = Path(f"{self.config_path}/jaeger_sampling.json")
            strategies_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(strategies_file, 'w') as f:
                json.dump(strategies, f, indent=2)
            
            logger.debug("Sampling strategies saved")
            
        except Exception as e:
            logger.error(f"Failed to save sampling strategies: {e}")
    
    def _generate_kubernetes_manifests(self) -> None:
        """Generate Kubernetes manifests for Jaeger"""
        try:
            manifests_dir = Path(f"{self.config_path}/jaeger-manifests")
            manifests_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate namespace
            namespace_manifest = {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": "jaeger-system",
                    "labels": {
                        "name": "jaeger-system"
                    }
                }
            }
            
            self._save_manifest("namespace", namespace_manifest, manifests_dir)
            
            # Generate ConfigMap for sampling strategies
            configmap_manifest = {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "name": "jaeger-sampling",
                    "namespace": "jaeger-system"
                },
                "data": {
                    "sampling_strategies.json": json.dumps(self.jaeger_config["sampling"], indent=2)
                }
            }
            
            self._save_manifest("configmap", configmap_manifest, manifests_dir)
            
            # Generate manifests for each component
            for component_name, component in self.components.items():
                if component.enabled:
                    deployment_manifest = self._generate_deployment_manifest(component)
                    service_manifest = self._generate_service_manifest(component)
                    
                    self._save_manifest(f"{component_name}-deployment", deployment_manifest, manifests_dir)
                    self._save_manifest(f"{component_name}-service", service_manifest, manifests_dir)
            
            # Generate Ingress for Query UI
            if self.ui_enabled and "query" in self.components:
                ingress_manifest = self._generate_ingress_manifest()
                self._save_manifest("jaeger-ingress", ingress_manifest, manifests_dir)
            
            logger.info("Kubernetes manifests generated")
            
        except Exception as e:
            logger.error(f"Failed to generate Kubernetes manifests: {e}")
            raise
    
    def _generate_deployment_manifest(self, component: JaegerComponent) -> Dict[str, Any]:
        """Generate deployment manifest for Jaeger component"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": component.name,
                "namespace": "jaeger-system",
                "labels": {
                    "app": component.name,
                    "component": "jaeger"
                }
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": component.name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": component.name,
                            "component": "jaeger"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": component.name,
                            "image": f"{component.image}:{component.version}",
                            "env": [
                                {"name": k, "value": v}
                                for k, v in component.environment_vars.items()
                            ],
                            "ports": [
                                {"containerPort": port}
                                for port in component.ports
                            ],
                            "resources": self._parse_resources(component.resources),
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/",
                                    "port": component.ports[0] if component.ports else 8080
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 10
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/",
                                    "port": component.ports[0] if component.ports else 8080
                                },
                                "initialDelaySeconds": 15,
                                "periodSeconds": 20
                            }
                        }]
                    }
                }
            }
        }
    
    def _generate_service_manifest(self, component: JaegerComponent) -> Dict[str, Any]:
        """Generate service manifest for Jaeger component"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": component.name,
                "namespace": "jaeger-system",
                "labels": {
                    "app": component.name,
                    "component": "jaeger"
                }
            },
            "spec": {
                "selector": {
                    "app": component.name
                },
                "ports": [
                    {
                        "name": f"port-{port}",
                        "port": port,
                        "targetPort": port,
                        "protocol": "TCP"
                    }
                    for port in component.ports
                ],
                "type": "ClusterIP"
            }
        }
    
    def _generate_ingress_manifest(self) -> Dict[str, Any]:
        """Generate ingress manifest for Jaeger UI"""
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": "jaeger-ingress",
                "namespace": "jaeger-system",
                "annotations": {
                    "nginx.ingress.kubernetes.io/rewrite-target": "/$1"
                }
            },
            "spec": {
                "rules": [{
                    "http": {
                        "paths": [{
                            "path": "/jaeger/(.*)",
                            "pathType": "Prefix",
                            "backend": {
                                "service": {
                                    "name": "jaeger-query",
                                    "port": {
                                        "number": 16686
                                    }
                                }
                            }
                        }]
                    }
                }]
            }
        }
    
    def _parse_resources(self, resources: Dict[str, str]) -> Dict[str, Any]:
        """Parse resource requirements"""
        parsed = {}
        
        for resource_type, resource_value in resources.items():
            if resource_type in ["requests", "limits"]:
                resource_dict = {}
                for resource in resource_value.split(","):
                    key, value = resource.split("=")
                    resource_dict[key] = value
                parsed[resource_type] = resource_dict
        
        return parsed
    
    def _save_manifest(self, name: str, manifest: Dict[str, Any], output_dir: Path) -> None:
        """Save manifest to YAML file"""
        try:
            filename = output_dir / f"{name}.yaml"
            with open(filename, 'w') as f:
                yaml.dump(manifest, f, default_flow_style=False)
            
        except Exception as e:
            logger.error(f"Failed to save manifest {name}: {e}")
    
    def register_service_tracing(self, config: TracingConfig) -> bool:
        """Register service for tracing"""
        try:
            self.trace_configs[config.service_name] = config
            
            # Save service tracing config
            self._save_service_config(config)
            
            logger.info(f"Service tracing registered: {config.service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service tracing {config.service_name}: {e}")
            return False
    
    def _save_service_config(self, config: TracingConfig) -> None:
        """Save service tracing configuration"""
        try:
            config_file = Path(f"{self.config_path}/services/{config.service_name}_tracing.json")
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            config_data = {
                "service_name": config.service_name,
                "collector_endpoint": config.collector_endpoint,
                "agent_endpoint": config.agent_endpoint,
                "sampling_strategy": config.sampling_strategy.value,
                "sampling_rate": config.sampling_rate,
                "max_tag_value_length": config.max_tag_value_length,
                "max_traces_per_second": config.max_traces_per_second,
                "enabled": config.enabled
            }
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to save service config: {e}")
    
    async def query_traces(self, service: str = None, operation: str = None, 
                          start_time: datetime = None, end_time: datetime = None,
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Query traces from Jaeger"""
        try:
            # Build query parameters
            params = {
                "limit": limit
            }
            
            if service:
                params["service"] = service
            
            if operation:
                params["operation"] = operation
            
            if start_time:
                params["start"] = int(start_time.timestamp() * 1000000)  # microseconds
            
            if end_time:
                params["end"] = int(end_time.timestamp() * 1000000)  # microseconds
            
            # Query Jaeger API
            response = requests.get(
                f"{self.query_endpoint}/api/traces",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                logger.error(f"Failed to query traces: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to query traces: {e}")
            return []
    
    async def get_service_metrics(self, service: str, 
                                 start_time: datetime = None,
                                 end_time: datetime = None) -> Optional[TraceMetrics]:
        """Get service trace metrics"""
        try:
            # Query traces for the service
            traces = await self.query_traces(
                service=service,
                start_time=start_time or datetime.now() - timedelta(hours=1),
                end_time=end_time or datetime.now(),
                limit=1000
            )
            
            if not traces:
                return None
            
            # Calculate metrics
            durations = []
            error_count = 0
            operation_counts = {}
            
            for trace in traces:
                if "spans" in trace:
                    for span in trace["spans"]:
                        duration = span.get("duration", 0) / 1000  # Convert to milliseconds
                        durations.append(duration)
                        
                        # Count operations
                        operation = span.get("operationName", "unknown")
                        operation_counts[operation] = operation_counts.get(operation, 0) + 1
                        
                        # Check for errors
                        tags = span.get("tags", [])
                        for tag in tags:
                            if tag.get("key") == "error" and tag.get("value") == "true":
                                error_count += 1
                                break
            
            if not durations:
                return None
            
            # Calculate percentiles
            durations.sort()
            p95_index = int(len(durations) * 0.95)
            p99_index = int(len(durations) * 0.99)
            
            # Find most common operation
            most_common_operation = max(operation_counts.items(), key=lambda x: x[1])[0] if operation_counts else "unknown"
            
            metrics = TraceMetrics(
                service_name=service,
                operation_name=most_common_operation,
                trace_count=len(traces),
                error_count=error_count,
                avg_duration_ms=sum(durations) / len(durations),
                p95_duration_ms=durations[p95_index],
                p99_duration_ms=durations[p99_index]
            )
            
            # Add to metrics history
            self.metrics_history.append(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get service metrics: {e}")
            return None
    
    def deploy_jaeger(self) -> bool:
        """Deploy Jaeger to Kubernetes"""
        try:
            manifests_dir = Path(f"{self.config_path}/jaeger-manifests")
            
            if not manifests_dir.exists():
                logger.error("Jaeger manifests not found. Run _generate_kubernetes_manifests first.")
                return False
            
            # Apply manifests
            for manifest_file in manifests_dir.glob("*.yaml"):
                cmd = ["kubectl", "apply", "-f", str(manifest_file)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"Failed to apply manifest {manifest_file}: {result.stderr}")
                    return False
            
            logger.info("Jaeger deployed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy Jaeger: {e}")
            return False
    
    def get_tracing_status(self) -> Dict[str, Any]:
        """Get Jaeger tracing status"""
        return {
            "backend": self.backend.value,
            "components_configured": len(self.components),
            "services_registered": len(self.trace_configs),
            "metrics_collected": len(self.metrics_history),
            "ui_enabled": self.ui_enabled,
            "retention_days": self.retention_days,
            "collector_endpoint": self.collector_endpoint,
            "query_endpoint": self.query_endpoint,
            "agent_endpoint": self.agent_endpoint
        }

# Enterprise Jaeger Tracing Setup instance
jaeger_tracing = JaegerTracingSetup()

# Export for use in other modules
__all__ = [
    "JaegerTracingSetup",
    "TracingConfig",
    "JaegerComponent",
    "TraceMetrics",
    "TracingBackend",
    "SamplingStrategy",
    "SpanKind",
    "jaeger_tracing"
]