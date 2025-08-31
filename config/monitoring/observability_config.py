"""
Observability Configuration Module for IA-Influencer Agent Platform
===================================================================

Professional observability orchestration and unified monitoring configuration for
comprehensive platform insights with advanced observability patterns and practices.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path


class ObservabilityLevel(Enum):
    """Observability depth levels"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    ENTERPRISE = "enterprise"


class ComponentHealth(Enum):
    """Component health states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ObservabilityComponent:
    """Observability component configuration"""
    name: str
    component_type: str
    enabled: bool = True
    health_endpoint: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    monitoring_interval: int = 30
    timeout: int = 10
    retry_count: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceLevelObjective:
    """Service Level Objective definition"""
    name: str
    metric: str
    target_value: float
    threshold: float
    window: str
    error_budget: float
    burn_rate_threshold: float
    alert_channels: List[str] = field(default_factory=list)


@dataclass
class ObservabilityPipeline:
    """Observability data pipeline configuration"""
    name: str
    source: str
    processors: List[str] = field(default_factory=list)
    destinations: List[str] = field(default_factory=list)
    batch_size: int = 1000
    flush_interval: int = 10
    compression_enabled: bool = True
    encryption_enabled: bool = True


class ObservabilityConfig:
    """
    Professional observability configuration orchestrator
    
    Manages unified monitoring, metrics, tracing, and logging configuration
    with enterprise-grade observability patterns and SRE practices.
    """
    
    def __init__(self, 
                 level: ObservabilityLevel = ObservabilityLevel.COMPREHENSIVE,
                 enable_slo: bool = True,
                 enable_distributed_tracing: bool = True,
                 enable_error_tracking: bool = True):
        """Initialize observability configuration"""
        self.level = level
        self.enable_slo = enable_slo
        self.enable_distributed_tracing = enable_distributed_tracing
        self.enable_error_tracking = enable_error_tracking
        
        self._components = {}
        self._slos = {}
        self._pipelines = {}
        self._health_checks = {}
        
        # Load environment configuration
        self.config = {
            "environment": os.getenv("ENVIRONMENT", "development"),
            "service_name": os.getenv("SERVICE_NAME", "ia-influencer-agent"),
            "service_version": os.getenv("SERVICE_VERSION", "1.0.0"),
            "cluster_name": os.getenv("CLUSTER_NAME", "ia-influencer-cluster"),
            "region": os.getenv("AWS_REGION", "eu-central-1"),
            
            # Observability endpoints
            "prometheus_endpoint": os.getenv("PROMETHEUS_ENDPOINT", "http://prometheus:9090"),
            "grafana_endpoint": os.getenv("GRAFANA_ENDPOINT", "http://grafana:3000"),
            "jaeger_endpoint": os.getenv("JAEGER_ENDPOINT", "http://jaeger:14268"),
            "elasticsearch_endpoint": os.getenv("ELASTICSEARCH_ENDPOINT", "http://elasticsearch:9200"),
            
            # Collection intervals
            "metrics_interval": int(os.getenv("METRICS_COLLECTION_INTERVAL", "15")),
            "traces_batch_size": int(os.getenv("TRACES_BATCH_SIZE", "1000")),
            "logs_batch_size": int(os.getenv("LOGS_BATCH_SIZE", "500")),
            
            # Performance settings
            "sampling_rate": float(os.getenv("TRACE_SAMPLING_RATE", "0.1")),
            "max_spans": int(os.getenv("MAX_SPANS_PER_TRACE", "1000")),
            "compression_level": int(os.getenv("COMPRESSION_LEVEL", "6")),
            
            # Retention policies
            "metrics_retention": os.getenv("METRICS_RETENTION", "30d"),
            "traces_retention": os.getenv("TRACES_RETENTION", "7d"),
            "logs_retention": os.getenv("LOGS_RETENTION", "14d"),
            
            # Security settings
            "tls_enabled": os.getenv("TLS_ENABLED", "true").lower() == "true",
            "mutual_tls": os.getenv("MUTUAL_TLS", "false").lower() == "true",
            "api_key_auth": os.getenv("API_KEY_AUTH", "true").lower() == "true",
        }
        
        self._setup_standard_components()
        self._setup_service_level_objectives()
        self._setup_observability_pipelines()
    
    def _setup_standard_components(self):
        """Setup standard observability components"""
        # Core platform components
        self.register_component(ObservabilityComponent(
            name="api_gateway",
            component_type="gateway",
            health_endpoint="/health",
            dependencies=["postgres", "redis"],
            monitoring_interval=10,
            metadata={"service_type": "critical", "tier": 1}
        ))
        
        self.register_component(ObservabilityComponent(
            name="ai_processing_engine",
            component_type="ai_service",
            health_endpoint="/ai/health",
            dependencies=["model_store", "vector_db"],
            monitoring_interval=30,
            metadata={"service_type": "core", "tier": 2}
        ))
        
        self.register_component(ObservabilityComponent(
            name="content_protection_service",
            component_type="protection_service",
            health_endpoint="/protection/health",
            dependencies=["fingerprint_db", "ai_processing_engine"],
            monitoring_interval=15,
            metadata={"service_type": "core", "tier": 2}
        ))
        
        self.register_component(ObservabilityComponent(
            name="audio_processing_engine",
            component_type="audio_service",
            health_endpoint="/audio/health",
            dependencies=["storage", "ai_processing_engine"],
            monitoring_interval=20,
            metadata={"service_type": "specialized", "tier": 3}
        ))
        
        self.register_component(ObservabilityComponent(
            name="monetization_service",
            component_type="business_service",
            health_endpoint="/monetization/health",
            dependencies=["payment_gateway", "analytics_db"],
            monitoring_interval=30,
            metadata={"service_type": "business", "tier": 2}
        ))
        
        # Infrastructure components
        self.register_component(ObservabilityComponent(
            name="postgres_primary",
            component_type="database",
            health_endpoint="/db/health",
            monitoring_interval=15,
            metadata={"database_type": "primary", "tier": 1}
        ))
        
        self.register_component(ObservabilityComponent(
            name="redis_cluster",
            component_type="cache",
            health_endpoint="/cache/health",
            monitoring_interval=10,
            metadata={"cache_type": "distributed", "tier": 1}
        ))
        
        self.register_component(ObservabilityComponent(
            name="elasticsearch_cluster",
            component_type="search_engine",
            health_endpoint="/_cluster/health",
            monitoring_interval=20,
            metadata={"index_count": "auto", "tier": 2}
        ))
    
    def _setup_service_level_objectives(self):
        """Setup Service Level Objectives for the platform"""
        if not self.enable_slo:
            return
            
        # API Gateway SLOs
        self.register_slo(ServiceLevelObjective(
            name="api_gateway_availability",
            metric="http_requests_success_rate",
            target_value=99.9,
            threshold=99.5,
            window="5m",
            error_budget=0.1,
            burn_rate_threshold=5.0,
            alert_channels=["pagerduty", "slack"]
        ))
        
        self.register_slo(ServiceLevelObjective(
            name="api_gateway_latency",
            metric="http_request_duration_p95",
            target_value=500.0,  # milliseconds
            threshold=1000.0,
            window="5m",
            error_budget=5.0,
            burn_rate_threshold=10.0,
            alert_channels=["slack"]
        ))
        
        # AI Processing SLOs
        self.register_slo(ServiceLevelObjective(
            name="ai_processing_throughput",
            metric="ai_processing_requests_per_second",
            target_value=100.0,
            threshold=50.0,
            window="10m",
            error_budget=10.0,
            burn_rate_threshold=20.0,
            alert_channels=["email"]
        ))
        
        # Content Protection SLOs
        self.register_slo(ServiceLevelObjective(
            name="fingerprint_accuracy",
            metric="fingerprint_matching_accuracy",
            target_value=95.0,
            threshold=90.0,
            window="1h",
            error_budget=5.0,
            burn_rate_threshold=15.0,
            alert_channels=["slack", "email"]
        ))
        
        # Audio Processing SLOs
        self.register_slo(ServiceLevelObjective(
            name="audio_processing_quality",
            metric="audio_processing_success_rate",
            target_value=98.0,
            threshold=95.0,
            window="15m",
            error_budget=2.0,
            burn_rate_threshold=8.0,
            alert_channels=["email"]
        ))
        
        # Database SLOs
        self.register_slo(ServiceLevelObjective(
            name="database_availability",
            metric="database_connection_success_rate",
            target_value=99.95,
            threshold=99.9,
            window="5m",
            error_budget=0.05,
            burn_rate_threshold=2.0,
            alert_channels=["pagerduty", "slack"]
        ))
    
    def _setup_observability_pipelines(self):
        """Setup observability data pipelines"""
        # Metrics pipeline
        self.register_pipeline(ObservabilityPipeline(
            name="metrics_collection",
            source="prometheus_scraper",
            processors=["metrics_aggregator", "anomaly_detector"],
            destinations=["prometheus", "grafana"],
            batch_size=5000,
            flush_interval=15
        ))
        
        # Traces pipeline
        self.register_pipeline(ObservabilityPipeline(
            name="traces_collection",
            source="jaeger_collector",
            processors=["trace_enricher", "sampling_processor"],
            destinations=["jaeger_storage", "analytics_db"],
            batch_size=1000,
            flush_interval=10
        ))
        
        # Logs pipeline
        self.register_pipeline(ObservabilityPipeline(
            name="logs_aggregation",
            source="fluentd_collector",
            processors=["log_parser", "sensitive_data_filter", "log_enricher"],
            destinations=["elasticsearch", "s3_archive"],
            batch_size=500,
            flush_interval=5
        ))
        
        # Security events pipeline
        self.register_pipeline(ObservabilityPipeline(
            name="security_events",
            source="security_sensors",
            processors=["threat_analyzer", "event_correlator"],
            destinations=["security_siem", "alert_manager"],
            batch_size=100,
            flush_interval=1
        ))
    
    def register_component(self, component: ObservabilityComponent):
        """Register observability component"""
        self._components[component.name] = component
        logging.info(f"Registered observability component: {component.name}")
    
    def register_slo(self, slo: ServiceLevelObjective):
        """Register Service Level Objective"""
        self._slos[slo.name] = slo
        logging.info(f"Registered SLO: {slo.name} (target: {slo.target_value}%)")
    
    def register_pipeline(self, pipeline: ObservabilityPipeline):
        """Register observability pipeline"""
        self._pipelines[pipeline.name] = pipeline
        logging.info(f"Registered observability pipeline: {pipeline.name}")
    
    def get_component(self, name: str) -> Optional[ObservabilityComponent]:
        """Get observability component by name"""



        return self._components.get(name)
    
    def get_slo(self, name: str) -> Optional[ServiceLevelObjective]:
        """Get SLO by name"""



        return self._slos.get(name)
    
    def get_pipeline(self, name: str) -> Optional[ObservabilityPipeline]:
        """Get pipeline by name"""



        return self._pipelines.get(name)
    
    def get_components_by_type(self, component_type: str) -> List[ObservabilityComponent]:
        """Get components by type"""



        return [comp for comp in self._components.values() 
                if comp.component_type == component_type]
    
    def get_critical_components(self) -> List[ObservabilityComponent]:
        """Get critical components (tier 1)"""



        return [comp for comp in self._components.values()
                if comp.metadata.get("tier", 99) == 1]
    
    async def check_component_health(self, component_name: str) -> ComponentHealth:
        """Check health of specific component"""
        component = self.get_component(component_name)
        if not component:
            return ComponentHealth.UNKNOWN
            
        try:
            # Implementation would make actual health check
            # This is a placeholder for the health check logic
            if component.enabled:
                return ComponentHealth.HEALTHY
            else:
                return ComponentHealth.DEGRADED
        except Exception as e:
            logging.error(f"Health check failed for {component_name}: {e}")
            return ComponentHealth.UNHEALTHY
    
    async def check_system_health(self) -> Dict[str, ComponentHealth]:
        """Check health of all components"""
        health_status = {}
        
        for name in self._components.keys():
            health_status[name] = await self.check_component_health(name)
            
        return health_status
    
    def get_monitoring_dashboard_config(self) -> Dict[str, Any]:
        """Get configuration for monitoring dashboards"""



        return {
            "service_map": {
                "components": list(self._components.keys()),
                "dependencies": {
                    name: comp.dependencies 
                    for name, comp in self._components.items()
                }
            },
            "slos": {
                name: {
                    "metric": slo.metric,
                    "target": slo.target_value,
                    "window": slo.window
                }
                for name, slo in self._slos.items()
            },
            "critical_services": [
                comp.name for comp in self.get_critical_components()
            ]
        }
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export complete observability configuration"""



        return {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "level": self.level.value,
                "version": "1.0.0"
            },
            "config": self.config,
            "components": {
                name: {
                    "name": comp.name,
                    "type": comp.component_type,
                    "enabled": comp.enabled,
                    "dependencies": comp.dependencies,
                    "monitoring_interval": comp.monitoring_interval,
                    "metadata": comp.metadata
                }
                for name, comp in self._components.items()
            },
            "slos": {
                name: {
                    "metric": slo.metric,
                    "target_value": slo.target_value,
                    "threshold": slo.threshold,
                    "window": slo.window,
                    "error_budget": slo.error_budget
                }
                for name, slo in self._slos.items()
            },
            "pipelines": {
                name: {
                    "source": pipeline.source,
                    "processors": pipeline.processors,
                    "destinations": pipeline.destinations,
                    "batch_size": pipeline.batch_size
                }
                for name, pipeline in self._pipelines.items()
            }
        }


# Global observability configuration instance
observability_config = ObservabilityConfig()

# Export key components for easy import
__all__ = [
    'ObservabilityConfig',
    'ObservabilityLevel',
    'ComponentHealth',
    'ObservabilityComponent',
    'ServiceLevelObjective',
    'ObservabilityPipeline',
    'observability_config'
]
