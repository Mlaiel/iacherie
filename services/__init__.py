"""
Enterprise Services Module - 3-Tier Architecture
===============================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Roles**: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + DevOps + Microservices + Audio Engineer + IA Prompt Engineer
**Module**: Enterprise Services Architecture
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Enterprise-grade 3-tier services architecture with comprehensive business logic,
security, monitoring, and intelligent orchestration.

**Architecture:**
- Core Services: Foundation layer (service registry, health, events, config, lifecycle, metrics)
- Processing Services: Business logic layer (content, AI, media, recommendations, validation, transformation)
- Orchestration Services: Coordination layer (workflows, business intelligence, automation, collaboration, analytics)

⚠️  STRICT INTELLECTUAL PROPERTY WARNING ⚠️
This software and all associated code are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
UNAUTHORIZED ACCESS, COPYING, MODIFICATION, DISTRIBUTION, REVERSE ENGINEERING, 
OR COMMERCIALIZATION without explicit written permission is STRICTLY PROHIBITED
and will result in immediate legal action under German and International copyright laws.

For legitimate licensing inquiries: mlaiel@live.de
"""

# Core Services Layer - Foundation Infrastructure
from .core import (
    # Service Discovery & Registry
    ServiceRegistry, ServiceInstance, ServiceStatus, ServiceType, DiscoveryStrategy,
    
    # Health Monitoring & Circuit Breakers
    HealthMonitor, HealthStatus, HealthCheck, CircuitBreakerState, ServiceHealthMetrics,
    
    # Event-Driven Architecture
    EventBus, Event, EventType, EventHandler, Subscription,
    
    # Configuration Management
    ConfigManager, ConfigSource, ConfigUpdate, SecretManager,
    
    # Lifecycle Management
    LifecycleManager, ServiceLifecycle, LifecycleEvent, LifecycleState,
    
    # Metrics & Observability
    MetricsCollector, Metric, MetricType, TimeSeriesData, PerformanceMetrics
)

# Processing Services Layer - Business Logic
from .processing import (
    # Content Processing
    ContentProcessor, ContentType, ProcessingResult, ProcessingStatus, ContentMetadata,
    
    # AI Orchestration
    AIOrchestrator, AIProvider, AIModel, AITask, AIResponse, ProviderConfig,
    
    # Media Processing Pipeline
    MediaPipeline, MediaType, MediaFormat, ProcessingStage, MediaAsset, TranscodingProfile,
    
    # Recommendation Engine
    RecommendationEngine, RecommendationType, RecommendationScore, UserProfile, ContentSimilarity, RecommendationResult,
    
    # Validation Services
    ValidationService, ValidationRule, ValidationResult, ValidationSeverity, ContentValidator, SchemaValidator,
    
    # Content Transformation
    TransformationEngine, TransformationType, TransformationRule, TransformationResult, ContentTransformer, DataTransformer
)

# Legacy Services (Import what's available for backward compatibility)
try:
    from .content_matching_engine import (
        AdvancedMatchingService, MatchingStrategy, CreativeMatchType,
        CreatorProfile, CompatibilityScore, CollaborationPrediction, ProactiveSuggestion
    )
except ImportError:
    AdvancedMatchingService = MatchingStrategy = CreativeMatchType = None
    CreatorProfile = CompatibilityScore = CollaborationPrediction = ProactiveSuggestion = None

try:
    from .graph_database import (
        CreatorGraphDatabase, RelationshipType, NetworkNode, RelationshipEdge, NetworkCommunity
    )
except ImportError:
    CreatorGraphDatabase = RelationshipType = NetworkNode = RelationshipEdge = NetworkCommunity = None

try:
    from .collaboration_engine import CollaborationEngine
except ImportError:
    CollaborationEngine = None

try:
    from .remix_generator import RemixGenerator
except ImportError:
    RemixGenerator = None

try:
    from .gamification_system import GamificationSystem
except ImportError:
    GamificationSystem = None

__all__ = [
    # Core Services Foundation
    "ServiceRegistry", "ServiceInstance", "ServiceStatus", "ServiceType", "DiscoveryStrategy",
    "HealthMonitor", "HealthStatus", "HealthCheck", "CircuitBreakerState", "ServiceHealthMetrics",
    "EventBus", "Event", "EventType", "EventHandler", "Subscription",
    "ConfigManager", "ConfigSource", "ConfigUpdate", "SecretManager",
    "LifecycleManager", "ServiceLifecycle", "LifecycleEvent", "LifecycleState",
    "MetricsCollector", "Metric", "MetricType", "TimeSeriesData", "PerformanceMetrics",
    
    # Processing Services Business Logic
    "ContentProcessor", "ContentType", "ProcessingResult", "ProcessingStatus", "ContentMetadata",
    "AIOrchestrator", "AIProvider", "AIModel", "AITask", "AIResponse", "ProviderConfig",
    "MediaPipeline", "MediaType", "MediaFormat", "ProcessingStage", "MediaAsset", "TranscodingProfile",
    "RecommendationEngine", "RecommendationType", "RecommendationScore", "UserProfile", "ContentSimilarity", "RecommendationResult",
    "ValidationService", "ValidationRule", "ValidationResult", "ValidationSeverity", "ContentValidator", "SchemaValidator",
    "TransformationEngine", "TransformationType", "TransformationRule", "TransformationResult", "ContentTransformer", "DataTransformer",
    
    # Legacy Services (Backward Compatibility)
    "AdvancedMatchingService", "MatchingStrategy", "CreativeMatchType", "CreatorProfile", 
    "CompatibilityScore", "CollaborationPrediction", "ProactiveSuggestion",
    "CreatorGraphDatabase", "RelationshipType", "NetworkNode", "RelationshipEdge", "NetworkCommunity",
    "CollaborationEngine", "RemixGenerator", "GamificationSystem"
]