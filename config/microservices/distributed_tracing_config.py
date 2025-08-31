"""
Distributed Tracing Configuration for IA-Influencer Agent Platform
==================================================================

Professional distributed tracing configuration for microservices observability.

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
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseSettings, Field, validator


class TracingBackend(str, Enum):
    """Distributed tracing backend types."""
    JAEGER = "jaeger"
    ZIPKIN = "zipkin"
    OPENTELEMETRY = "opentelemetry"
    AWS_XRAY = "aws_xray"
    DATADOG = "datadog"
    NEW_RELIC = "new_relic"
    ELASTIC_APM = "elastic_apm"


class SamplingStrategy(str, Enum):
    """Trace sampling strategies."""
    CONST = "const"              # Constant sampling rate
    PROBABILISTIC = "probabilistic"  # Probabilistic sampling
    RATE_LIMITING = "rate_limiting"  # Rate-limited sampling
    ADAPTIVE = "adaptive"        # Adaptive sampling
    REMOTE = "remote"           # Remote sampling configuration


class SpanKind(str, Enum):
    """OpenTelemetry span kinds."""
    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


@dataclass
class SamplingConfig:
    """Sampling configuration for different services."""
    strategy: SamplingStrategy = SamplingStrategy.PROBABILISTIC
    param: float = 0.1  # Sampling rate (0.0-1.0)
    max_traces_per_second: int = 100
    operation_sampling: Dict[str, float] = field(default_factory=dict)
    service_sampling: Dict[str, float] = field(default_factory=dict)


@dataclass
class SpanProcessorConfig:
    """Span processor configuration."""
    processor_type: str = "batch"  # batch or simple
    max_queue_size: int = 2048
    schedule_delay_millis: int = 5000
    export_timeout_millis: int = 30000
    max_export_batch_size: int = 512


@dataclass
class ResourceConfig:
    """Resource configuration for tracing."""
    service_name: str
    service_version: str = "1.0.0"
    service_namespace: str = "ia-influencer"
    service_instance_id: Optional[str] = None
    deployment_environment: str = "production"
    attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class InstrumentationConfig:
    """Instrumentation configuration for different libraries."""
    enabled: bool = True
    http_client: bool = True
    http_server: bool = True
    database: bool = True
    redis: bool = True
    message_queue: bool = True
    celery: bool = True
    requests: bool = True
    aiohttp: bool = True
    sqlalchemy: bool = True
    fastapi: bool = True
    custom_spans: Dict[str, Any] = field(default_factory=dict)


class DistributedTracingConfig(BaseSettings):
    """
    Centralized distributed tracing configuration for microservices observability.
    Supports Jaeger, Zipkin, OpenTelemetry, AWS X-Ray, and other tracing backends.
    """
    
    # Global tracing settings
    enabled: bool = Field(True, env="TRACING_ENABLED")
    backend: TracingBackend = Field(TracingBackend.JAEGER, env="TRACING_BACKEND")
    service_name: str = Field("ia-influencer-agent", env="TRACING_SERVICE_NAME")
    service_version: str = Field("1.0.0", env="TRACING_SERVICE_VERSION")
    service_namespace: str = Field("ia-influencer", env="TRACING_SERVICE_NAMESPACE")
    deployment_environment: str = Field("production", env="TRACING_DEPLOYMENT_ENVIRONMENT")
    
    # Sampling configuration
    sampling_strategy: SamplingStrategy = Field(
        SamplingStrategy.PROBABILISTIC, 
        env="TRACING_SAMPLING_STRATEGY"
    )
    sampling_rate: float = Field(0.1, env="TRACING_SAMPLING_RATE")
    max_traces_per_second: int = Field(100, env="TRACING_MAX_TRACES_PER_SECOND")
    
    # Jaeger configuration
    jaeger_agent_host: str = Field("localhost", env="JAEGER_AGENT_HOST")
    jaeger_agent_port: int = Field(6831, env="JAEGER_AGENT_PORT")
    jaeger_collector_endpoint: Optional[str] = Field(None, env="JAEGER_COLLECTOR_ENDPOINT")
    jaeger_user: Optional[str] = Field(None, env="JAEGER_USER")
    jaeger_password: Optional[str] = Field(None, env="JAEGER_PASSWORD")
    
    # Zipkin configuration
    zipkin_endpoint: str = Field("http://localhost:9411/api/v2/spans", env="ZIPKIN_ENDPOINT")
    
    # OpenTelemetry configuration
    otel_exporter_otlp_endpoint: str = Field("http://localhost:4317", env="OTEL_EXPORTER_OTLP_ENDPOINT")
    otel_exporter_otlp_headers: Optional[str] = Field(None, env="OTEL_EXPORTER_OTLP_HEADERS")
    otel_exporter_otlp_timeout: int = Field(10, env="OTEL_EXPORTER_OTLP_TIMEOUT")
    
    # AWS X-Ray configuration
    aws_xray_tracing_name: Optional[str] = Field(None, env="AWS_XRAY_TRACING_NAME")
    aws_xray_context_missing: str = Field("LOG_ERROR", env="AWS_XRAY_CONTEXT_MISSING")
    aws_region: Optional[str] = Field(None, env="AWS_REGION")
    
    # Datadog configuration
    datadog_agent_host: str = Field("localhost", env="DD_AGENT_HOST")
    datadog_trace_agent_port: int = Field(8126, env="DD_TRACE_AGENT_PORT")
    datadog_service: Optional[str] = Field(None, env="DD_SERVICE")
    datadog_env: Optional[str] = Field(None, env="DD_ENV")
    datadog_version: Optional[str] = Field(None, env="DD_VERSION")
    
    # Span processor configuration
    span_processor_type: str = Field("batch", env="TRACING_SPAN_PROCESSOR_TYPE")
    span_processor_max_queue_size: int = Field(2048, env="TRACING_SPAN_PROCESSOR_MAX_QUEUE_SIZE")
    span_processor_schedule_delay_millis: int = Field(5000, env="TRACING_SPAN_PROCESSOR_SCHEDULE_DELAY_MILLIS")
    span_processor_export_timeout_millis: int = Field(30000, env="TRACING_SPAN_PROCESSOR_EXPORT_TIMEOUT_MILLIS")
    span_processor_max_export_batch_size: int = Field(512, env="TRACING_SPAN_PROCESSOR_MAX_EXPORT_BATCH_SIZE")
    
    # Instrumentation settings
    trace_http_client: bool = Field(True, env="TRACING_HTTP_CLIENT")
    trace_http_server: bool = Field(True, env="TRACING_HTTP_SERVER")
    trace_database: bool = Field(True, env="TRACING_DATABASE")
    trace_redis: bool = Field(True, env="TRACING_REDIS")
    trace_message_queue: bool = Field(True, env="TRACING_MESSAGE_QUEUE")
    trace_celery: bool = Field(True, env="TRACING_CELERY")
    trace_requests: bool = Field(True, env="TRACING_REQUESTS")
    trace_aiohttp: bool = Field(True, env="TRACING_AIOHTTP")
    trace_sqlalchemy: bool = Field(True, env="TRACING_SQLALCHEMY")
    trace_fastapi: bool = Field(True, env="TRACING_FASTAPI")
    
    # Custom attributes and tags
    global_tags: Dict[str, str] = Field({}, env="TRACING_GLOBAL_TAGS")
    resource_attributes: Dict[str, str] = Field({}, env="TRACING_RESOURCE_ATTRIBUTES")
    
    # Performance settings
    max_tag_value_length: int = Field(1024, env="TRACING_MAX_TAG_VALUE_LENGTH")
    max_logs_per_span: int = Field(100, env="TRACING_MAX_LOGS_PER_SPAN")
    span_attribute_count_limit: int = Field(1000, env="TRACING_SPAN_ATTRIBUTE_COUNT_LIMIT")
    span_event_count_limit: int = Field(1000, env="TRACING_SPAN_EVENT_COUNT_LIMIT")
    span_link_count_limit: int = Field(1000, env="TRACING_SPAN_LINK_COUNT_LIMIT")
    
    # Security settings
    disable_trace_id_injection: bool = Field(False, env="TRACING_DISABLE_TRACE_ID_INJECTION")
    sanitize_sql_queries: bool = Field(True, env="TRACING_SANITIZE_SQL_QUERIES")
    redact_sensitive_data: bool = Field(True, env="TRACING_REDACT_SENSITIVE_DATA")
    sensitive_keys: List[str] = Field(
        ["password", "secret", "token", "key", "auth", "credential"], 
        env="TRACING_SENSITIVE_KEYS"
    )
    
    # Error handling
    ignore_exceptions: List[str] = Field([], env="TRACING_IGNORE_EXCEPTIONS")
    error_capture_enabled: bool = Field(True, env="TRACING_ERROR_CAPTURE_ENABLED")
    error_capture_source: bool = Field(True, env="TRACING_ERROR_CAPTURE_SOURCE")
    
    # B3 propagation (for Zipkin compatibility)
    b3_propagation: bool = Field(False, env="TRACING_B3_PROPAGATION")
    b3_single_header: bool = Field(False, env="TRACING_B3_SINGLE_HEADER")
    
    class Config:
        env_prefix = "DISTRIBUTED_TRACING_"
        case_sensitive = False
        
    def get_sampling_config(self, service_name: Optional[str] = None) -> SamplingConfig:
        """Get sampling configuration for a service."""
        service_sampling = {}
        operation_sampling = {}
        
        # Service-specific sampling rates
        if service_name:
            service_sampling[service_name] = self.sampling_rate
        
        # Operation-specific sampling rates for different microservices
        if service_name == "fingerprinting-engine":
            operation_sampling.update({
                "fingerprint_audio": 0.5,
                "fingerprint_video": 0.3,
                "fingerprint_image": 0.8,
                "fingerprint_text": 1.0
            })
        elif service_name == "web-crawler":
            operation_sampling.update({
                "crawl_youtube": 0.2,
                "crawl_instagram": 0.2,
                "crawl_tiktok": 0.2,
                "crawl_generic": 0.1
            })
        elif service_name == "spotify-agent":
            operation_sampling.update({
                "get_analytics": 0.3,
                "get_recommendations": 0.5,
                "sync_profile": 0.8
            })
        
        return SamplingConfig(
            strategy=self.sampling_strategy,
            param=self.sampling_rate,
            max_traces_per_second=self.max_traces_per_second,
            service_sampling=service_sampling,
            operation_sampling=operation_sampling
        )
    
    def get_span_processor_config(self) -> SpanProcessorConfig:
        """Get span processor configuration."""



        return SpanProcessorConfig(
            processor_type=self.span_processor_type,
            max_queue_size=self.span_processor_max_queue_size,
            schedule_delay_millis=self.span_processor_schedule_delay_millis,
            export_timeout_millis=self.span_processor_export_timeout_millis,
            max_export_batch_size=self.span_processor_max_export_batch_size
        )
    
    def get_resource_config(self, service_name: Optional[str] = None) -> ResourceConfig:
        """Get resource configuration."""
        attributes = {
            "deployment.environment": self.deployment_environment,
            **self.resource_attributes,
            **self.global_tags
        }
        
        return ResourceConfig(
            service_name=service_name or self.service_name,
            service_version=self.service_version,
            service_namespace=self.service_namespace,
            deployment_environment=self.deployment_environment,
            attributes=attributes
        )
    
    def get_instrumentation_config(self) -> InstrumentationConfig:
        """Get instrumentation configuration."""



        return InstrumentationConfig(
            enabled=self.enabled,
            http_client=self.trace_http_client,
            http_server=self.trace_http_server,
            database=self.trace_database,
            redis=self.trace_redis,
            message_queue=self.trace_message_queue,
            celery=self.trace_celery,
            requests=self.trace_requests,
            aiohttp=self.trace_aiohttp,
            sqlalchemy=self.trace_sqlalchemy,
            fastapi=self.trace_fastapi
        )
    
    def get_jaeger_config(self) -> Dict[str, Any]:
        """Get Jaeger-specific configuration."""
        config = {
            "service_name": self.service_name,
            "agent_host_name": self.jaeger_agent_host,
            "agent_port": self.jaeger_agent_port,
            "sampling": {
                "type": self.sampling_strategy.value,
                "param": self.sampling_rate
            }
        }
        
        if self.jaeger_collector_endpoint:
            config["collector_endpoint"] = self.jaeger_collector_endpoint
        
        if self.jaeger_user and self.jaeger_password:
            config["username"] = self.jaeger_user
            config["password"] = self.jaeger_password
        
        return config
    
    def get_zipkin_config(self) -> Dict[str, Any]:
        """Get Zipkin-specific configuration."""



        return {
            "service_name": self.service_name,
            "zipkin_endpoint": self.zipkin_endpoint,
            "sample_rate": self.sampling_rate
        }
    
    def get_opentelemetry_config(self) -> Dict[str, Any]:
        """Get OpenTelemetry-specific configuration."""



        return {
            "service_name": self.service_name,
            "service_version": self.service_version,
            "service_namespace": self.service_namespace,
            "otlp_endpoint": self.otel_exporter_otlp_endpoint,
            "otlp_headers": self.otel_exporter_otlp_headers,
            "otlp_timeout": self.otel_exporter_otlp_timeout,
            "resource_attributes": self.get_resource_config().attributes,
            "span_processor": self.get_span_processor_config(),
            "sampling": self.get_sampling_config()
        }
    
    def get_tracing_config(self) -> Dict[str, Any]:
        """Get complete distributed tracing configuration."""



        return {
            "enabled": self.enabled,
            "backend": self.backend,
            "service": {
                "name": self.service_name,
                "version": self.service_version,
                "namespace": self.service_namespace,
                "environment": self.deployment_environment
            },
            "sampling": {
                "strategy": self.sampling_strategy,
                "rate": self.sampling_rate,
                "max_traces_per_second": self.max_traces_per_second
            },
            "instrumentation": self.get_instrumentation_config(),
            "resource": self.get_resource_config(),
            "span_processor": self.get_span_processor_config(),
            "backend_config": {
                "jaeger": self.get_jaeger_config(),
                "zipkin": self.get_zipkin_config(),
                "opentelemetry": self.get_opentelemetry_config()
            },
            "security": {
                "disable_trace_id_injection": self.disable_trace_id_injection,
                "sanitize_sql_queries": self.sanitize_sql_queries,
                "redact_sensitive_data": self.redact_sensitive_data,
                "sensitive_keys": self.sensitive_keys
            },
            "performance": {
                "max_tag_value_length": self.max_tag_value_length,
                "max_logs_per_span": self.max_logs_per_span,
                "span_attribute_count_limit": self.span_attribute_count_limit,
                "span_event_count_limit": self.span_event_count_limit,
                "span_link_count_limit": self.span_link_count_limit
            }
        }


# Pre-configured tracing settings for IA-Influencer Agent microservices
MICROSERVICE_TRACING_CONFIGS = {
    "api-gateway": {
        "service_name": "api-gateway",
        "sampling_rate": 0.5,  # Higher sampling for gateway
        "trace_all_requests": True,
        "custom_tags": {
            "component": "gateway",
            "tier": "frontend"
        },
        "instrumentation": {
            "http_server": True,
            "http_client": True,
            "fastapi": True,
            "redis": True
        }
    },
    "spotify-agent": {
        "service_name": "spotify-agent",
        "sampling_rate": 0.3,
        "custom_tags": {
            "component": "ai-agent",
            "tier": "backend",
            "integration": "spotify"
        },
        "operation_sampling": {
            "get_analytics": 0.5,
            "get_recommendations": 0.8,
            "sync_profile": 0.3
        },
        "instrumentation": {
            "http_server": True,
            "http_client": True,
            "database": True,
            "redis": True,
            "celery": True
        }
    },
    "content-protection": {
        "service_name": "content-protection",
        "sampling_rate": 0.4,
        "custom_tags": {
            "component": "protection",
            "tier": "backend"
        },
        "instrumentation": {
            "http_server": True,
            "database": True,
            "message_queue": True,
            "celery": True
        }
    },
    "fingerprinting-engine": {
        "service_name": "fingerprinting-engine",
        "sampling_rate": 0.2,  # Lower sampling due to high volume
        "custom_tags": {
            "component": "fingerprinting",
            "tier": "backend",
            "type": "ai-processing"
        },
        "operation_sampling": {
            "fingerprint_audio": 0.3,
            "fingerprint_video": 0.2,
            "fingerprint_image": 0.5,
            "fingerprint_text": 0.8
        },
        "instrumentation": {
            "http_server": True,
            "database": True,
            "redis": True,
            "message_queue": True
        }
    },
    "web-crawler": {
        "service_name": "web-crawler",
        "sampling_rate": 0.1,  # Low sampling due to high volume
        "custom_tags": {
            "component": "crawler",
            "tier": "backend"
        },
        "operation_sampling": {
            "crawl_youtube": 0.2,
            "crawl_instagram": 0.2,
            "crawl_tiktok": 0.2,
            "crawl_generic": 0.1
        },
        "instrumentation": {
            "http_server": True,
            "http_client": True,
            "database": True,
            "message_queue": True,
            "celery": True
        }
    },
    "monetization-engine": {
        "service_name": "monetization-engine",
        "sampling_rate": 0.8,  # High sampling for financial operations
        "custom_tags": {
            "component": "monetization",
            "tier": "backend",
            "type": "financial"
        },
        "instrumentation": {
            "http_server": True,
            "http_client": True,
            "database": True,
            "message_queue": True
        }
    },
    "notification-service": {
        "service_name": "notification-service",
        "sampling_rate": 0.3,
        "custom_tags": {
            "component": "notifications",
            "tier": "backend"
        },
        "instrumentation": {
            "http_server": True,
            "database": True,
            "message_queue": True,
            "redis": True
        }
    },
    "analytics-engine": {
        "service_name": "analytics-engine",
        "sampling_rate": 0.2,
        "custom_tags": {
            "component": "analytics",
            "tier": "backend"
        },
        "instrumentation": {
            "http_server": True,
            "database": True,
            "redis": True,
            "message_queue": True
        }
    }
}

# Common span tags and attributes for all services
COMMON_SPAN_ATTRIBUTES = {
    "platform": "ia-influencer",
    "language": "python",
    "framework": "fastapi",
    "version": "1.0.0"
}

# Security-sensitive attributes to redact
SENSITIVE_ATTRIBUTES = [
    "password", "secret", "token", "key", "auth", "credential",
    "jwt", "bearer", "authorization", "api_key", "client_secret",
    "access_token", "refresh_token", "session_id", "user_password"
]

# Standard HTTP attributes to capture
HTTP_ATTRIBUTES = [
    "http.method", "http.url", "http.scheme", "http.host", "http.target",
    "http.status_code", "http.status_text", "http.user_agent",
    "http.request_content_length", "http.response_content_length"
]

# Database attributes to capture
DATABASE_ATTRIBUTES = [
    "db.system", "db.connection_string", "db.user", "db.name",
    "db.statement", "db.operation", "db.sql.table"
]

# Message queue attributes to capture
MESSAGE_QUEUE_ATTRIBUTES = [
    "messaging.system", "messaging.destination", "messaging.destination_kind",
    "messaging.operation", "messaging.message_id", "messaging.conversation_id"
]


# Export configuration instance
distributed_tracing_config = DistributedTracingConfig()
