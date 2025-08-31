"""Microservices Configuration Module for IA-Influencer Agent Platform
===================================================================

Professional microservices architecture configuration management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
# Core microservices configurations
from .service_discovery import (
    ServiceDiscoveryConfig, 
    ServiceRegistry, 
    MICROSERVICE_REGISTRATIONS,
    service_discovery_config
)
from .load_balancer_config import (
    LoadBalancerConfig, 
    LoadBalancer, 
    BackendServer,
    UpstreamConfig,
    MICROSERVICE_UPSTREAMS,
    load_balancer_config
)
from .message_broker_config import (
    MessageBrokerConfig, 
    MICROSERVICE_EXCHANGES,
    MICROSERVICE_QUEUES,
    MICROSERVICE_BINDINGS,
    message_broker_config
)
from .circuit_breaker_config import (
    CircuitBreakerConfig, 
    CircuitBreaker,
    CircuitBreakerRegistry,
    MICROSERVICE_CIRCUIT_BREAKER_RULES,
    circuit_breaker_config
)
from .service_mesh_config import (
    ServiceMeshConfig, 
    MICROSERVICE_MESH_SERVICES,
    MICROSERVICE_VIRTUAL_SERVICES,
    MICROSERVICE_DESTINATION_RULES,
    MAIN_GATEWAY,
    service_mesh_config
)
from .api_gateway_config import (
    APIGatewayConfig, 
    MICROSERVICE_ROUTES,
    MICROSERVICE_UPSTREAMS as GATEWAY_UPSTREAMS,
    api_gateway_config
)
from .health_check_config import (
    HealthCheckConfig, 
    HealthChecker,
    MICROSERVICE_HEALTH_CHECKS,
    health_check_config
)
from .distributed_tracing_config import (
    DistributedTracingConfig, 
    MICROSERVICE_TRACING_CONFIGS,
    COMMON_SPAN_ATTRIBUTES,
    distributed_tracing_config
)

# New microservice configurations
from .content_protection_config import (
    ContentProtectionConfig,
    FingerprintingEngineConfig,
    WebCrawlerConfig,
    MonetizationEngineConfig,
    LicensingEngineConfig,
    ContentProtectionOrchestrator,
    CONTENT_PROTECTION_CONFIGS,
    content_protection_config,
    fingerprinting_engine_config,
    web_crawler_config,
    monetization_engine_config,
    licensing_engine_config,
    content_protection_orchestrator
)
from .platform_integration_config import (
    PlatformIntegrationConfig,
    PlatformAPIConfig,
    PlatformType,
    APIAuthType,
    PlatformIntegrationOrchestrator,
    PLATFORM_CONFIGS,
    platform_integration_config,
    platform_integration_orchestrator
)
from .realtime_analytics_config import (
    AnalyticsEngineConfig,
    MetricDefinition,
    MetricType,
    AnalyticsScope,
    RealTimeAnalyticsOrchestrator,
    ANALYTICS_METRICS,
    analytics_engine_config,
    analytics_orchestrator
)
from .event_driven_config import (
    EventDrivenConfig,
    EventSchema,
    EventType,
    EventPriority,
    EventStreamConfig,
    EventPublisher,
    EventConsumer,
    EventDrivenOrchestrator,
    EVENT_SCHEMAS,
    STREAM_CONFIGS,
    event_driven_config,
    event_orchestrator
)

__all__ = [
    # Configuration classes
    'ServiceDiscoveryConfig',
    'LoadBalancerConfig', 
    'MessageBrokerConfig',
    'CircuitBreakerConfig',
    'ServiceMeshConfig',
    'APIGatewayConfig',
    'HealthCheckConfig',
    'DistributedTracingConfig',
    
    # New configuration classes
    'ContentProtectionConfig',
    'FingerprintingEngineConfig',
    'WebCrawlerConfig',
    'MonetizationEngineConfig',
    'LicensingEngineConfig',
    'PlatformIntegrationConfig',
    'PlatformAPIConfig',
    'AnalyticsEngineConfig',
    'EventDrivenConfig',
    
    # Implementation classes
    'ServiceRegistry',
    'LoadBalancer',
    'CircuitBreaker',
    'CircuitBreakerRegistry', 
    'HealthChecker',
    
    # New orchestrator classes
    'ContentProtectionOrchestrator',
    'PlatformIntegrationOrchestrator',
    'RealTimeAnalyticsOrchestrator',
    'EventDrivenOrchestrator',
    'EventPublisher',
    'EventConsumer',
    
    # Data classes
    'BackendServer',
    'UpstreamConfig',
    'EventSchema',
    'MetricDefinition',
    
    # Enums
    'PlatformType',
    'APIAuthType',
    'MetricType',
    'AnalyticsScope',
    'EventType',
    'EventPriority',
    
    # Pre-configured instances
    'MICROSERVICE_REGISTRATIONS',
    'MICROSERVICE_UPSTREAMS',
    'MICROSERVICE_EXCHANGES',
    'MICROSERVICE_QUEUES', 
    'MICROSERVICE_BINDINGS',
    'MICROSERVICE_CIRCUIT_BREAKER_RULES',
    'MICROSERVICE_MESH_SERVICES',
    'MICROSERVICE_VIRTUAL_SERVICES',
    'MICROSERVICE_DESTINATION_RULES',
    'MAIN_GATEWAY',
    'MICROSERVICE_ROUTES',
    'GATEWAY_UPSTREAMS',
    'MICROSERVICE_HEALTH_CHECKS',
    'MICROSERVICE_TRACING_CONFIGS',
    'COMMON_SPAN_ATTRIBUTES',
    
    # New pre-configured instances
    'CONTENT_PROTECTION_CONFIGS',
    'PLATFORM_CONFIGS',
    'ANALYTICS_METRICS',
    'EVENT_SCHEMAS',
    'STREAM_CONFIGS',
    
    # Configuration instances
    'service_discovery_config',
    'load_balancer_config',
    'message_broker_config',
    'circuit_breaker_config',
    'service_mesh_config', 
    'api_gateway_config',
    'health_check_config',
    'distributed_tracing_config',
    
    # New configuration instances
    'content_protection_config',
    'fingerprinting_engine_config',
    'web_crawler_config',
    'monetization_engine_config',
    'licensing_engine_config',
    'platform_integration_config',
    'analytics_engine_config',
    'event_driven_config',
    
    # Orchestrator instances
    'content_protection_orchestrator',
    'platform_integration_orchestrator',
    'analytics_orchestrator',
    'event_orchestrator',
    
    # Orchestrator functions
    'orchestrator',
    'initialize_microservices',
    'get_system_status',
    'get_configuration_summary',
    'is_system_ready',
    'CONFIGURATION_SUMMARY'
]

# Export validation and testing tools (optional)
try:
    from .validate import run_full_validation
    __all__.append('run_full_validation')
except ImportError:
    pass  # Validation module is optional
