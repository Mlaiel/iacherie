"""
Service Mesh Integration for PagerDuty - IA Chéries Platform
Microservices topology monitoring and distributed tracing

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid
import hashlib

try:
    import requests
    import networkx as nx
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    requests = None
    nx = None

logger = logging.getLogger(__name__)


class ServiceHealthStatus(Enum):
    """Service health status in mesh"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class TrafficDirection(Enum):
    """Traffic direction in service mesh"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class ServiceNode:
    """Service node in mesh topology"""
    service_name: str
    namespace: str
    version: str
    endpoint: str
    health_status: ServiceHealthStatus
    cpu_usage: float
    memory_usage: float
    request_rate: float
    error_rate: float
    latency_p99: float
    created_at: datetime
    last_health_check: datetime
    metadata: Dict[str, Any]


@dataclass
class ServiceDependency:
    """Service dependency relationship"""
    source_service: str
    target_service: str
    dependency_type: str
    traffic_direction: TrafficDirection
    request_volume: int
    success_rate: float
    avg_latency: float
    circuit_breaker_state: CircuitBreakerState
    last_updated: datetime


@dataclass
class ServiceMeshAlert:
    """Service mesh alert definition"""
    alert_id: str
    alert_type: str
    service_name: str
    namespace: str
    severity: str
    message: str
    details: Dict[str, Any]
    affected_services: List[str]
    root_cause_service: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]
    pagerduty_incident_id: Optional[str]


@dataclass
class TraceSpan:
    """Distributed trace span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    service_name: str
    operation_name: str
    start_time: datetime
    duration_ms: float
    status_code: int
    error: bool
    tags: Dict[str, Any]
    logs: List[Dict[str, Any]]


class ServiceMeshIntegration:
    """
    Service mesh integration for Creator Economy microservices
    Monitors topology, dependencies, and distributed traces
    """
    
    def __init__(self, pagerduty_client=None):
        """Initialize service mesh integration"""
        self.pagerduty_client = pagerduty_client
        self.service_topology = {}
        self.dependency_graph = None
        self.active_alerts = {}
        self.trace_storage = {}
        self.health_checks = {}
        
        # Configuration
        self.config = {
            "health_check_interval": 30,  # seconds
            "topology_refresh_interval": 300,  # seconds
            "trace_retention_hours": 24,
            "alert_thresholds": {
                "error_rate": 0.05,  # 5%
                "latency_p99": 1000,  # 1s
                "cpu_usage": 0.80,  # 80%
                "memory_usage": 0.85  # 85%
            },
            "circuit_breaker": {
                "failure_threshold": 10,
                "timeout_duration": 60,
                "half_open_max_requests": 3
            }
        }
        
        # Service mesh integrations
        self.mesh_integrations = {
            "istio": self._setup_istio_integration(),
            "envoy": self._setup_envoy_integration(),
            "jaeger": self._setup_jaeger_integration(),
            "opentelemetry": self._setup_otel_integration()
        }
        
        logger.info("Service Mesh Integration initialized")
    
    def _setup_istio_integration(self) -> Dict[str, Any]:
        """Setup Istio service mesh integration"""
        return {
            "enabled": True,
            "api_endpoint": "http://istio-pilot:15010",
            "metrics_endpoint": "http://prometheus:9090",
            "telemetry_v2": True,
            "mtls_enabled": True
        }
    
    def _setup_envoy_integration(self) -> Dict[str, Any]:
        """Setup Envoy proxy integration"""
        return {
            "enabled": True,
            "admin_endpoint": "http://envoy:9901",
            "stats_endpoint": "http://envoy:9901/stats",
            "config_dump_endpoint": "http://envoy:9901/config_dump"
        }
    
    def _setup_jaeger_integration(self) -> Dict[str, Any]:
        """Setup Jaeger tracing integration"""
        return {
            "enabled": True,
            "query_endpoint": "http://jaeger:16686",
            "collector_endpoint": "http://jaeger:14268",
            "agent_endpoint": "http://jaeger:6831"
        }
    
    def _setup_otel_integration(self) -> Dict[str, Any]:
        """Setup OpenTelemetry integration"""
        return {
            "enabled": True,
            "collector_endpoint": "http://otel-collector:4317",
            "metrics_endpoint": "http://otel-collector:8889/metrics",
            "traces_endpoint": "http://otel-collector:55680/v1/traces"
        }
    
    async def discover_service_topology(self) -> Dict[str, ServiceNode]:
        """Discover service mesh topology"""
        try:
            services = {}
            
            # Discover services from Istio
            if self.mesh_integrations["istio"]["enabled"]:
                istio_services = await self._discover_istio_services()
                services.update(istio_services)
            
            # Add Kubernetes service discovery
            k8s_services = await self._discover_kubernetes_services()
            services.update(k8s_services)
            
            # Update topology
            self.service_topology = services
            
            # Build dependency graph
            await self._build_dependency_graph()
            
            logger.info(f"Discovered {len(services)} services in topology")
            return services
            
        except Exception as e:
            logger.error(f"Service topology discovery failed: {e}")
            return {}
    
    async def _discover_istio_services(self) -> Dict[str, ServiceNode]:
        """Discover services from Istio"""
        services = {}
        
        try:
            # Mock Istio service discovery
            istio_endpoint = self.mesh_integrations["istio"]["api_endpoint"]
            
            # Creator Economy specific services
            creator_services = [
                "creator-api", "content-processor", "ai-protection",
                "monetization-engine", "collaboration-matcher", 
                "gamification-service", "seo-optimizer", "distribution-hub"
            ]
            
            for service_name in creator_services:
                service_node = ServiceNode(
                    service_name=service_name,
                    namespace="creator-platform",
                    version="v1.0.0",
                    endpoint=f"http://{service_name}:8080",
                    health_status=ServiceHealthStatus.HEALTHY,
                    cpu_usage=0.45,
                    memory_usage=0.60,
                    request_rate=150.0,
                    error_rate=0.01,
                    latency_p99=250.0,
                    created_at=datetime.utcnow(),
                    last_health_check=datetime.utcnow(),
                    metadata={
                        "mesh": "istio",
                        "sidecar_version": "1.18.0",
                        "mtls_enabled": True
                    }
                )
                services[service_name] = service_node
                
        except Exception as e:
            logger.error(f"Istio service discovery failed: {e}")
            
        return services
    
    async def _discover_kubernetes_services(self) -> Dict[str, ServiceNode]:
        """Discover services from Kubernetes"""
        services = {}
        
        try:
            # Mock Kubernetes service discovery
            # In real implementation, use kubernetes client
            
            monitoring_services = [
                "prometheus", "grafana", "alertmanager", 
                "jaeger", "elasticsearch", "kibana"
            ]
            
            for service_name in monitoring_services:
                service_node = ServiceNode(
                    service_name=service_name,
                    namespace="monitoring",
                    version="latest",
                    endpoint=f"http://{service_name}:9090",
                    health_status=ServiceHealthStatus.HEALTHY,
                    cpu_usage=0.30,
                    memory_usage=0.40,
                    request_rate=50.0,
                    error_rate=0.001,
                    latency_p99=100.0,
                    created_at=datetime.utcnow(),
                    last_health_check=datetime.utcnow(),
                    metadata={
                        "mesh": "kubernetes",
                        "monitoring": True
                    }
                )
                services[service_name] = service_node
                
        except Exception as e:
            logger.error(f"Kubernetes service discovery failed: {e}")
            
        return services
    
    async def _build_dependency_graph(self):
        """Build service dependency graph"""
        try:
            if not DEPENDENCIES_AVAILABLE:
                logger.warning("NetworkX not available for dependency graph")
                return
                
            # Create dependency graph
            self.dependency_graph = nx.DiGraph()
            
            # Add service nodes
            for service_name, service_node in self.service_topology.items():
                self.dependency_graph.add_node(service_name, **asdict(service_node))
            
            # Add dependency edges (Creator Economy workflow)
            dependencies = [
                ("creator-api", "content-processor"),
                ("content-processor", "ai-protection"),
                ("ai-protection", "monetization-engine"),
                ("monetization-engine", "collaboration-matcher"),
                ("collaboration-matcher", "gamification-service"),
                ("gamification-service", "seo-optimizer"),
                ("seo-optimizer", "distribution-hub"),
                ("creator-api", "prometheus"),
                ("content-processor", "elasticsearch")
            ]
            
            for source, target in dependencies:
                if source in self.service_topology and target in self.service_topology:
                    dependency = ServiceDependency(
                        source_service=source,
                        target_service=target,
                        dependency_type="http",
                        traffic_direction=TrafficDirection.OUTBOUND,
                        request_volume=100,
                        success_rate=0.99,
                        avg_latency=150.0,
                        circuit_breaker_state=CircuitBreakerState.CLOSED,
                        last_updated=datetime.utcnow()
                    )
                    
                    self.dependency_graph.add_edge(
                        source, target, **asdict(dependency)
                    )
            
            logger.info("Service dependency graph built successfully")
            
        except Exception as e:
            logger.error(f"Dependency graph building failed: {e}")
    
    async def monitor_service_health(self) -> Dict[str, ServiceMeshAlert]:
        """Monitor service health and generate alerts"""
        alerts = {}
        
        try:
            for service_name, service_node in self.service_topology.items():
                # Check health thresholds
                issues = []
                
                if service_node.error_rate > self.config["alert_thresholds"]["error_rate"]:
                    issues.append(f"High error rate: {service_node.error_rate:.2%}")
                
                if service_node.latency_p99 > self.config["alert_thresholds"]["latency_p99"]:
                    issues.append(f"High latency: {service_node.latency_p99}ms")
                
                if service_node.cpu_usage > self.config["alert_thresholds"]["cpu_usage"]:
                    issues.append(f"High CPU usage: {service_node.cpu_usage:.1%}")
                
                if service_node.memory_usage > self.config["alert_thresholds"]["memory_usage"]:
                    issues.append(f"High memory usage: {service_node.memory_usage:.1%}")
                
                # Create alert if issues found
                if issues:
                    alert = ServiceMeshAlert(
                        alert_id=str(uuid.uuid4()),
                        alert_type="service_health",
                        service_name=service_name,
                        namespace=service_node.namespace,
                        severity="high" if len(issues) > 2 else "medium",
                        message=f"Service {service_name} health issues: {', '.join(issues)}",
                        details={
                            "issues": issues,
                            "metrics": {
                                "error_rate": service_node.error_rate,
                                "latency_p99": service_node.latency_p99,
                                "cpu_usage": service_node.cpu_usage,
                                "memory_usage": service_node.memory_usage
                            }
                        },
                        affected_services=await self._get_dependent_services(service_name),
                        root_cause_service=service_name,
                        created_at=datetime.utcnow(),
                        resolved_at=None,
                        pagerduty_incident_id=None
                    )
                    
                    alerts[alert.alert_id] = alert
                    self.active_alerts[alert.alert_id] = alert
                    
                    # Trigger PagerDuty incident
                    if self.pagerduty_client:
                        await self._trigger_pagerduty_incident(alert)
            
            logger.info(f"Health monitoring completed, {len(alerts)} alerts generated")
            return alerts
            
        except Exception as e:
            logger.error(f"Service health monitoring failed: {e}")
            return {}
    
    async def _get_dependent_services(self, service_name: str) -> List[str]:
        """Get services dependent on given service"""
        dependent_services = []
        
        try:
            if self.dependency_graph and service_name in self.dependency_graph:
                # Get downstream dependencies
                dependent_services = list(self.dependency_graph.successors(service_name))
                
                # Get upstream dependencies that might be affected
                upstream = list(self.dependency_graph.predecessors(service_name))
                dependent_services.extend(upstream)
                
        except Exception as e:
            logger.error(f"Getting dependent services failed: {e}")
            
        return dependent_services
    
    async def _trigger_pagerduty_incident(self, alert: ServiceMeshAlert):
        """Trigger PagerDuty incident for service mesh alert"""
        try:
            if not self.pagerduty_client:
                return
                
            incident_details = {
                "summary": f"Service Mesh Alert: {alert.service_name} - {alert.message}",
                "source": f"service-mesh/{alert.service_name}",
                "severity": alert.severity,
                "component": alert.service_name,
                "group": "service-mesh",
                "class": "service_health",
                "custom_details": {
                    "alert_id": alert.alert_id,
                    "namespace": alert.namespace,
                    "affected_services": alert.affected_services,
                    "details": alert.details
                }
            }
            
            incident_key = await self.pagerduty_client.trigger_incident(
                incident_details, 
                dedup_key=f"service-mesh-{alert.service_name}"
            )
            
            if incident_key:
                alert.pagerduty_incident_id = incident_key
                logger.info(f"PagerDuty incident {incident_key} created for alert {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"PagerDuty incident creation failed: {e}")
    
    async def analyze_distributed_trace(self, trace_id: str) -> Dict[str, Any]:
        """Analyze distributed trace for performance issues"""
        try:
            spans = await self._get_trace_spans(trace_id)
            
            if not spans:
                return {"error": "Trace not found"}
            
            analysis = {
                "trace_id": trace_id,
                "total_duration": 0,
                "service_count": len(set(span.service_name for span in spans)),
                "span_count": len(spans),
                "error_count": sum(1 for span in spans if span.error),
                "critical_path": [],
                "bottlenecks": [],
                "recommendations": []
            }
            
            # Calculate total duration and critical path
            root_spans = [span for span in spans if not span.parent_span_id]
            if root_spans:
                analysis["total_duration"] = max(span.duration_ms for span in root_spans)
            
            # Identify bottlenecks
            for span in spans:
                if span.duration_ms > 1000:  # > 1s
                    analysis["bottlenecks"].append({
                        "service": span.service_name,
                        "operation": span.operation_name,
                        "duration_ms": span.duration_ms
                    })
            
            # Generate recommendations
            if analysis["error_count"] > 0:
                analysis["recommendations"].append("Investigate error spans for root cause")
            
            if analysis["bottlenecks"]:
                analysis["recommendations"].append("Optimize high-latency operations")
            
            logger.info(f"Distributed trace analysis completed for {trace_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Distributed trace analysis failed: {e}")
            return {"error": str(e)}
    
    async def _get_trace_spans(self, trace_id: str) -> List[TraceSpan]:
        """Get spans for trace from Jaeger"""
        spans = []
        
        try:
            # Mock trace data for Creator Economy workflow
            mock_spans = [
                {
                    "trace_id": trace_id,
                    "span_id": "span1",
                    "parent_span_id": None,
                    "service_name": "creator-api",
                    "operation_name": "POST /api/content/upload",
                    "start_time": datetime.utcnow(),
                    "duration_ms": 1500.0,
                    "status_code": 200,
                    "error": False,
                    "tags": {"http.method": "POST", "http.url": "/api/content/upload"},
                    "logs": []
                },
                {
                    "trace_id": trace_id,
                    "span_id": "span2", 
                    "parent_span_id": "span1",
                    "service_name": "content-processor",
                    "operation_name": "process_content",
                    "start_time": datetime.utcnow(),
                    "duration_ms": 800.0,
                    "status_code": 200,
                    "error": False,
                    "tags": {"content.type": "video", "ai.processing": "true"},
                    "logs": []
                },
                {
                    "trace_id": trace_id,
                    "span_id": "span3",
                    "parent_span_id": "span2", 
                    "service_name": "ai-protection",
                    "operation_name": "protect_content",
                    "start_time": datetime.utcnow(),
                    "duration_ms": 300.0,
                    "status_code": 200,
                    "error": False,
                    "tags": {"protection.type": "copyright", "blockchain.enabled": "true"},
                    "logs": []
                }
            ]
            
            for span_data in mock_spans:
                span = TraceSpan(**span_data)
                spans.append(span)
                
        except Exception as e:
            logger.error(f"Getting trace spans failed: {e}")
            
        return spans
    
    async def get_service_topology_metrics(self) -> Dict[str, Any]:
        """Get service mesh topology metrics"""
        try:
            metrics = {
                "total_services": len(self.service_topology),
                "healthy_services": 0,
                "degraded_services": 0,
                "unhealthy_services": 0,
                "total_dependencies": 0,
                "circuit_breakers_open": 0,
                "average_latency": 0.0,
                "total_request_rate": 0.0,
                "overall_error_rate": 0.0
            }
            
            total_latency = 0.0
            total_requests = 0.0
            total_errors = 0.0
            
            for service_name, service_node in self.service_topology.items():
                # Count by health status
                if service_node.health_status == ServiceHealthStatus.HEALTHY:
                    metrics["healthy_services"] += 1
                elif service_node.health_status == ServiceHealthStatus.DEGRADED:
                    metrics["degraded_services"] += 1
                else:
                    metrics["unhealthy_services"] += 1
                
                # Aggregate metrics
                total_latency += service_node.latency_p99
                total_requests += service_node.request_rate
                total_errors += service_node.request_rate * service_node.error_rate
            
            # Calculate averages
            if len(self.service_topology) > 0:
                metrics["average_latency"] = total_latency / len(self.service_topology)
                metrics["total_request_rate"] = total_requests
                metrics["overall_error_rate"] = total_errors / total_requests if total_requests > 0 else 0.0
            
            # Count dependencies
            if self.dependency_graph:
                metrics["total_dependencies"] = self.dependency_graph.number_of_edges()
            
            logger.info("Service topology metrics calculated")
            return metrics
            
        except Exception as e:
            logger.error(f"Getting topology metrics failed: {e}")
            return {}
    
    async def check_circuit_breakers(self) -> Dict[str, Any]:
        """Check circuit breaker states across service mesh"""
        try:
            circuit_breaker_status = {
                "total_circuit_breakers": 0,
                "closed": 0,
                "open": 0,
                "half_open": 0,
                "unhealthy_services": []
            }
            
            for service_name, service_node in self.service_topology.items():
                # Mock circuit breaker check
                cb_state = CircuitBreakerState.CLOSED
                
                # Determine state based on metrics
                if service_node.error_rate > 0.1:  # 10% error rate
                    cb_state = CircuitBreakerState.OPEN
                elif service_node.error_rate > 0.05:  # 5% error rate
                    cb_state = CircuitBreakerState.HALF_OPEN
                
                circuit_breaker_status["total_circuit_breakers"] += 1
                circuit_breaker_status[cb_state.value] += 1
                
                if cb_state != CircuitBreakerState.CLOSED:
                    circuit_breaker_status["unhealthy_services"].append({
                        "service": service_name,
                        "state": cb_state.value,
                        "error_rate": service_node.error_rate
                    })
            
            logger.info("Circuit breaker status checked")
            return circuit_breaker_status
            
        except Exception as e:
            logger.error(f"Circuit breaker check failed: {e}")
            return {}


# Global service mesh integration instance
_service_mesh_integration = None


def get_service_mesh_integration(pagerduty_client=None) -> ServiceMeshIntegration:
    """Get service mesh integration instance"""
    global _service_mesh_integration
    if _service_mesh_integration is None:
        _service_mesh_integration = ServiceMeshIntegration(pagerduty_client)
    return _service_mesh_integration


def create_service_mesh_integration(pagerduty_client=None) -> ServiceMeshIntegration:
    """Create new service mesh integration instance"""
    return ServiceMeshIntegration(pagerduty_client)


# Export main classes and functions
__all__ = [
    'ServiceMeshIntegration',
    'ServiceNode',
    'ServiceDependency', 
    'ServiceMeshAlert',
    'TraceSpan',
    'ServiceHealthStatus',
    'TrafficDirection',
    'CircuitBreakerState',
    'get_service_mesh_integration',
    'create_service_mesh_integration'
]