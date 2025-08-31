"""IA Influencer Agent - Data Management Indexing Module
====================================================

Advanced indexing system for multi-format content protection and search vectorization.
Supports audio, video, image, text fingerprinting with enterprise-grade performance.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Content Protection Platform
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or reproduction
without explicit written permission is strictly prohibited
and will result in legal action.

Contact: mlaiel@live.de for licensing inquiries.
"""
from .engines import (
    VectorSearchEngine,
    ContentIndexEngine,
    FingerprintIndexEngine,
    MetadataIndexEngine
)

from .processors import (
    AudioIndexProcessor,
    VideoIndexProcessor,
    ImageIndexProcessor,
    TextIndexProcessor,
    MultiFormatProcessor
)

from .repositories import (
    IndexRepository,
    VectorRepository,
    FingerprintRepository,
    SearchRepository
)

from .services import (
    IndexingService,
    SearchService,
    VectorService,
    RealtimeIndexService
)

from .strategies import (
    ContentIndexingStrategy,
    VectorEmbeddingStrategy,
    SimilaritySearchStrategy,
    RankingStrategy
)

from .monitoring import (
    MetricsCollector,
    AlertManager,
    PerformanceAnalyzer,
    PerformanceMetrics,
    IndexingMetrics,
    AlertRule
)

from .analytics import (
    ContentAnalyticsEngine,
    SearchAnalyticsEngine,
    VisualizationEngine,
    ContentAnalytics,
    SearchAnalytics,
    BusinessInsights
)

from .optimization import (
    OptimizationEngine,
    IntelligentCache,
    WorkloadBalancer,
    BatchProcessor,
    OptimizationConfig,
    OptimizationResult
)

from .security import (
    EncryptionManager,
    AccessControlManager,
    AuditLogger,
    ThreatDetector,
    SecurityConfig,
    UserCredentials,
    SecurityThreat
)

from .business_workflows import (
    WorkflowStage,
    WorkflowStatus,
    WorkflowContext,
    WorkflowResult,
    BusinessWorkflowOrchestrator,
    WorkflowManager
)

from .creator_configurations import (
    CreatorConfigPreset,
    CreatorConfigurations,
    PlatformOptimizations
)

from .specialized_services import (
    CreatorType,
    ContentCategory,
    CreatorProfile,
    ContentMetadata,
    SpecializedIndexingService,
    MusicianIndexingService,
    BloggerIndexingService,
    PhotographerIndexingService,
    InfluencerIndexingService,
    ComedianIndexingService,
    CreatorServiceFactory
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Core Engines
    "VectorSearchEngine",
    "ContentIndexEngine",
    "FingerprintIndexEngine", 
    "MetadataIndexEngine",
    
    # Content Processors
    "AudioIndexProcessor",
    "VideoIndexProcessor",
    "ImageIndexProcessor",
    "TextIndexProcessor",
    "MultiFormatProcessor",
    
    # Data Repositories
    "IndexRepository",
    "VectorRepository",
    "FingerprintRepository",
    "SearchRepository",
    
    # Business Services
    "IndexingService",
    "SearchService",
    "VectorService",
    "RealtimeIndexService",
    
    # Strategy Patterns
    "ContentIndexingStrategy",
    "VectorEmbeddingStrategy",
    "SimilaritySearchStrategy",
    "RankingStrategy",
    
    # Monitoring & Analytics
    "MetricsCollector",
    "AlertManager",
    "PerformanceAnalyzer",
    "PerformanceMetrics",
    "IndexingMetrics",
    "AlertRule",
    "ContentAnalyticsEngine",
    "SearchAnalyticsEngine",
    "VisualizationEngine",
    "ContentAnalytics",
    "SearchAnalytics",
    "BusinessInsights",
    
    # Optimization
    "OptimizationEngine",
    "IntelligentCache",
    "WorkloadBalancer",
    "BatchProcessor",
    "OptimizationConfig",
    "OptimizationResult",
    
    # Security
    "EncryptionManager",
    "AccessControlManager",
    "AuditLogger",
    "ThreatDetector",
    "SecurityConfig",
    "UserCredentials",
    "SecurityThreat",
    
    # Specialized Creator Services
    "CreatorType",
    "ContentCategory",
    "CreatorProfile",
    "ContentMetadata",
    "SpecializedIndexingService",
    "MusicianIndexingService",
    "BloggerIndexingService",
    "PhotographerIndexingService",
    "InfluencerIndexingService",
    "ComedianIndexingService",
    "CreatorServiceFactory",
    
    # Creator Configurations
    "CreatorConfigPreset",
    "CreatorConfigurations",
    "PlatformOptimizations",
    
    # Business Workflows
    "WorkflowStage",
    "WorkflowStatus",
    "WorkflowContext",
    "WorkflowResult",
    "BusinessWorkflowOrchestrator",
    "WorkflowManager"
]
