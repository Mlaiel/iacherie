"""Tracing Configuration Module for IA-Influencer Agent Platform
=============================================================

Professional distributed tracing configuration using OpenTelemetry
for comprehensive request tracking across microservices.

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
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class TracingBackend(Enum):
    """Supported tracing backends"""    JAEGER = "jaeger"
    ZIPKIN = "zipkin"
    OTLP = "otlp"
    CONSOLE = "console"


class SamplingStrategy(Enum):
    """Sampling strategies for trace collection"""    ALWAYS_ON = "always_on"
    ALWAYS_OFF = "always_off"
    RATIO_BASED = "ratio_based"
    RATE_LIMITING = "rate_limiting"
    PARENT_BASED = "parent_based"


@dataclass
class SpanAttribute:
    """Span attribute configuration"""    key: str
    value: Any
    namespace: Optional[str] = None


@dataclass
class InstrumentationConfig:
    """Service instrumentation configuration"""    service_name: str
    service_version: str
    environment: str
    attributes: List[SpanAttribute] = field(default_factory=list)
    resource_detectors: List[str] = field(default_factory=list)


class TracingConfig:
    """Professional distributed tracing configuration for IA-Influencer platform"""    
    def __init__(self):
        self.tracing_enabled = os.getenv("TRACING_ENABLED", "true").lower() == "true"
        self.service_name = os.getenv("SERVICE_NAME", "ia-influencer-agent")
        self.service_version = os.getenv("SERVICE_VERSION", "1.0.0")
        self.environment = os.getenv("ENVIRONMENT", "production")
        self.tracing_backend = TracingBackend(os.getenv("TRACING_BACKEND", "jaeger"))
        self.sampling_ratio = float(os.getenv("TRACING_SAMPLING_RATIO", "0.1"))
        self.jaeger_endpoint = os.getenv("JAEGER_ENDPOINT", "http://jaeger:14268/api/traces")
        self.zipkin_endpoint = os.getenv("ZIPKIN_ENDPOINT", "http://zipkin:9411/api/v2/spans")
        self.otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://otel-collector:4317")
        self.max_spans_per_trace = int(os.getenv("MAX_SPANS_PER_TRACE", "1000"))
        self.max_attributes_per_span = int(os.getenv("MAX_ATTRIBUTES_PER_SPAN", "128"))
    
    def get_global_config(self) -> Dict[str, Any]:
        """Get global tracing configuration"""        return {
            "enabled": self.tracing_enabled,
            "service_name": self.service_name,
            "service_version": self.service_version,
            "environment": self.environment,
            "sampling_ratio": self.sampling_ratio,
            "max_spans_per_trace": self.max_spans_per_trace,
            "max_attributes_per_span": self.max_attributes_per_span
        }
    
    def get_exporter_config(self) -> Dict[str, Any]:
        """Get trace exporter configuration"""        if self.tracing_backend == TracingBackend.JAEGER:
            return {
                "type": "jaeger",
                "endpoint": self.jaeger_endpoint,
                "headers": {},
                "timeout": 30,
                "compression": "gzip"
            }
        elif self.tracing_backend == TracingBackend.ZIPKIN:
            return {
                "type": "zipkin",
                "endpoint": self.zipkin_endpoint,
                "timeout": 30
            }
        elif self.tracing_backend == TracingBackend.OTLP:
            return {
                "type": "otlp",
                "endpoint": self.otlp_endpoint,
                "headers": {},
                "timeout": 30,
                "compression": "gzip"
            }
        else:
            return {
                "type": "console",
                "pretty_print": True
            }
    
    def get_instrumentation_configs(self) -> Dict[str, InstrumentationConfig]:
        """Get instrumentation configurations for different services"""        base_attributes = [
            SpanAttribute("service.namespace", "ia-influencer"),
            SpanAttribute("deployment.environment", self.environment),
            SpanAttribute("service.instance.id", os.getenv("HOSTNAME", "unknown"))
        ]
        
        return {
            "api-gateway": InstrumentationConfig(
                service_name="ia-influencer-api-gateway",
                service_version=self.service_version,
                environment=self.environment,
                attributes=base_attributes + [
                    SpanAttribute("service.type", "api-gateway"),
                    SpanAttribute("service.layer", "frontend")
                ],
                resource_detectors=["env", "host", "process"]
            ),
            "user-service": InstrumentationConfig(
                service_name="ia-influencer-user-service",
                service_version=self.service_version,
                environment=self.environment,
                attributes=base_attributes + [
                    SpanAttribute("service.type", "microservice"),
                    SpanAttribute("service.domain", "user-management")
                ]
            ),
            "content-service": InstrumentationConfig(
                service_name="ia-influencer-content-service",
                service_version=self.service_version,
                environment=self.environment,
                attributes=base_attributes + [
                    SpanAttribute("service.type", "microservice"),
                    SpanAttribute("service.domain", "content-management")
                ]
            ),
            "ai-service": InstrumentationConfig(
                service_name="ia-influencer-ai-service",
                service_version=self.service_version,
                environment=self.environment,
                attributes=base_attributes + [
                    SpanAttribute("service.type", "ai-service"),
                    SpanAttribute("service.domain", "machine-learning")
                ]
            ),
            "protection-service": InstrumentationConfig(
                service_name="ia-influencer-protection-service",
                service_version=self.service_version,
                environment=self.environment,
                attributes=base_attributes + [
                    SpanAttribute("service.type", "protection-service"),
                    SpanAttribute("service.domain", "content-protection")
                ]
            ),
            "audio-service": InstrumentationConfig(
                service_name="ia-influencer-audio-service",
                service_version=self.service_version,
                environment=self.environment,
                attributes=base_attributes + [
                    SpanAttribute("service.type", "audio-service"),
                    SpanAttribute("service.domain", "audio-processing")
                ]
            ),
            "monetization-service": InstrumentationConfig(
                service_name="ia-influencer-monetization-service",
                service_version=self.service_version,
                environment=self.environment,
                attributes=base_attributes + [
                    SpanAttribute("service.type", "monetization-service"),
                    SpanAttribute("service.domain", "revenue-tracking")
                ]
            ),
            "security-service": InstrumentationConfig(
                service_name="ia-influencer-security-service",
                service_version=self.service_version,
                environment=self.environment,
                attributes=base_attributes + [
                    SpanAttribute("service.type", "security-service"),
                    SpanAttribute("service.domain", "security-monitoring")
                ]
            )
        }
    
    def get_sampling_config(self) -> Dict[str, Any]:
        """Get sampling configuration"""        return {
            "default_strategy": SamplingStrategy.PARENT_BASED.value,
            "strategies": {
                "always_on": {
                    "type": "always_on"
                },
                "always_off": {
                    "type": "always_off"
                },
                "ratio_based": {
                    "type": "ratio_based",
                    "sampling_ratio": self.sampling_ratio
                },
                "rate_limiting": {
                    "type": "rate_limiting",
                    "max_traces_per_second": 100
                },
                "parent_based": {
                    "type": "parent_based",
                    "root_strategy": "ratio_based",
                    "root_sampling_ratio": self.sampling_ratio,
                    "remote_parent_sampled": "always_on",
                    "remote_parent_not_sampled": "always_off",
                    "local_parent_sampled": "always_on",
                    "local_parent_not_sampled": "always_off"
                }
            },
            "per_service_overrides": {
                "ia-influencer-ai-service": {
                    "strategy": "ratio_based",
                    "sampling_ratio": 0.5  # Higher sampling for AI services
                },
                "ia-influencer-protection-service": {
                    "strategy": "ratio_based",
                    "sampling_ratio": 0.3  # Higher sampling for protection
                },
                "ia-influencer-security-service": {
                    "strategy": "always_on"  # Always trace security events
                }
            }
        }
    
    def get_propagation_config(self) -> Dict[str, Any]:
        """Get context propagation configuration"""        return {
            "propagators": [
                "tracecontext",
                "baggage",
                "b3",
                "b3multi",
                "jaeger",
                "xray"
            ],
            "default_propagator": "tracecontext"
        }
    
    def get_span_processor_config(self) -> Dict[str, Any]:
        """Get span processor configuration"""        return {
            "batch_processor": {
                "max_queue_size": 2048,
                "max_export_batch_size": 512,
                "export_timeout_millis": 30000,
                "schedule_delay_millis": 5000
            },
            "simple_processor": {
                "enabled": False  # Use batch processor for production
            }
        }
    
    def get_instrumentation_libraries(self) -> List[str]:
        """Get list of auto-instrumentation libraries"""        return [
            "opentelemetry-instrumentation-fastapi",
            "opentelemetry-instrumentation-requests",
            "opentelemetry-instrumentation-sqlalchemy",
            "opentelemetry-instrumentation-redis",
            "opentelemetry-instrumentation-celery",
            "opentelemetry-instrumentation-psycopg2",
            "opentelemetry-instrumentation-pymongo",
            "opentelemetry-instrumentation-elasticsearch",
            "opentelemetry-instrumentation-boto3sqs",
            "opentelemetry-instrumentation-botocore",
            "opentelemetry-instrumentation-aiohttp-client",
            "opentelemetry-instrumentation-httpx"
        ]
    
    def get_custom_span_attributes(self) -> Dict[str, List[SpanAttribute]]:
        """Get custom span attributes for different operations"""        return {
            "http_requests": [
                SpanAttribute("http.route", ""),
                SpanAttribute("http.user_agent", ""),
                SpanAttribute("http.remote_addr", ""),
                SpanAttribute("user.id", ""),
                SpanAttribute("user.role", "")
            ],
            "database_operations": [
                SpanAttribute("db.operation", ""),
                SpanAttribute("db.table.name", ""),
                SpanAttribute("db.rows_affected", 0),
                SpanAttribute("db.connection_pool.usage", 0)
            ],
            "ai_operations": [
                SpanAttribute("ai.model.name", ""),
                SpanAttribute("ai.model.version", ""),
                SpanAttribute("ai.input.size", 0),
                SpanAttribute("ai.output.size", 0),
                SpanAttribute("ai.confidence.score", 0.0),
                SpanAttribute("ai.processing.type", "")
            ],
            "content_protection": [
                SpanAttribute("content.type", ""),
                SpanAttribute("content.size", 0),
                SpanAttribute("fingerprint.algorithm", ""),
                SpanAttribute("protection.confidence", 0.0),
                SpanAttribute("match.platform", "")
            ],
            "audio_processing": [
                SpanAttribute("audio.format", ""),
                SpanAttribute("audio.duration", 0.0),
                SpanAttribute("audio.sample_rate", 0),
                SpanAttribute("audio.channels", 0),
                SpanAttribute("processing.algorithm", "")
            ],
            "monetization": [
                SpanAttribute("revenue.amount", 0.0),
                SpanAttribute("revenue.currency", ""),
                SpanAttribute("platform.name", ""),
                SpanAttribute("payment.provider", ""),
                SpanAttribute("license.type", "")
            ],
            "security": [
                SpanAttribute("security.threat.level", ""),
                SpanAttribute("security.incident.type", ""),
                SpanAttribute("auth.method", ""),
                SpanAttribute("user.session.id", ""),
                SpanAttribute("security.rule.triggered", "")
            ]
        }
    
    def get_trace_filters(self) -> Dict[str, Any]:
        """Get trace filtering configuration"""        return {
            "exclude_endpoints": [
                "/health",
                "/metrics",
                "/ping",
                "/favicon.ico",
                "/robots.txt"
            ],
            "exclude_user_agents": [
                "kube-probe",
                "health-check",
                "prometheus",
                "grafana"
            ],
            "include_headers": [
                "x-request-id",
                "x-correlation-id",
                "x-user-id",
                "x-tenant-id"
            ],
            "exclude_sensitive_headers": [
                "authorization",
                "cookie",
                "x-api-key",
                "x-auth-token"
            ],
            "max_attribute_length": 256,
            "truncate_long_attributes": True
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance optimization configuration"""        return {
            "memory_limits": {
                "max_spans_in_memory": 10000,
                "max_attributes_per_span": self.max_attributes_per_span,
                "max_events_per_span": 128,
                "max_links_per_span": 128
            },
            "export_optimization": {
                "batch_size": 512,
                "export_interval_seconds": 5,
                "max_queue_size": 2048,
                "worker_threads": 4
            },
            "sampling_optimization": {
                "adaptive_sampling": True,
                "sampling_refresh_interval": 300,
                "target_spans_per_second": 1000
            }
        }
    
    def get_jaeger_config(self) -> Dict[str, Any]:
        """Get Jaeger-specific configuration"""        return {
            "collector_endpoint": self.jaeger_endpoint,
            "agent_host": os.getenv("JAEGER_AGENT_HOST", "jaeger-agent"),
            "agent_port": int(os.getenv("JAEGER_AGENT_PORT", "6831")),
            "sampling_server_url": os.getenv("JAEGER_SAMPLING_ENDPOINT", "http://jaeger:5778/sampling"),
            "tags": {
                "version": self.service_version,
                "environment": self.environment,
                "cluster": os.getenv("CLUSTER_NAME", "ia-influencer")
            },
            "process_tags": {
                "hostname": os.getenv("HOSTNAME", "unknown"),
                "pid": str(os.getpid())
            },
            "max_packet_size": 65000,
            "flush_interval": 1000
        }
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete tracing configuration"""        return {
            "global": self.get_global_config(),
            "exporter": self.get_exporter_config(),
            "sampling": self.get_sampling_config(),
            "propagation": self.get_propagation_config(),
            "span_processor": self.get_span_processor_config(),
            "instrumentation": {
                "libraries": self.get_instrumentation_libraries(),
                "services": self.get_instrumentation_configs(),
                "custom_attributes": self.get_custom_span_attributes()
            },
            "filters": self.get_trace_filters(),
            "performance": self.get_performance_config(),
            "backend_specific": {
                "jaeger": self.get_jaeger_config()
            }
        }
