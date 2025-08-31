"""IA Influencer Agent - Data Management Pipeline Module
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

 AVERTISSEMENT DE PROPRIÉTÉ INTELLECTUELLE 
Ce code et tous les concepts associés sont la propriété exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation écrite 
explicite de l'auteur est strictement interdite et constitue une violation du 
droit d'auteur. Contact: mlaiel@live.de

Industrial-grade data pipeline management for multi-format content processing,
AI-powered content protection, monetization tracking, and cross-platform collaboration.

Complete Creator Monetization Pipeline:
User (musician/blogger/photographer/influencer/comedian) → Upload multi-format → 
AI protection rights → SEO professional → Collaboration matching → Distribution multi-platforms → Revenue tracking

This module provides:
- Advanced ETL pipeline orchestration
- Real-time stream processing
- Content transformation engines
- Quality assurance automation
- Performance monitoring systems
- Error handling and recovery
- Creator-specific workflow orchestration
- Multi-platform content distribution
- AI-powered monetization analytics
- Brand collaboration matching
- Revenue tracking and optimization
"""
from .coordinators import (
    ContentPipelineCoordinator,
    ProcessingOrchestrator,
    QualityAssuranceCoordinator
)

from .engines import (
    StreamProcessingEngine,
    BatchProcessingEngine,
    TransformationEngine,
    ValidationEngine
)

from .extractors import (
    MultiFormatExtractor,
    MetadataExtractor,
    FeatureExtractor,
    ContentExtractor
)

from .loaders import (
    DistributedLoader,
    PlatformLoader,
    StorageLoader,
    AnalyticsLoader
)

from .monitors import (
    PipelineHealthMonitor,
    PerformanceMetricsCollector,
    ErrorTrackingSystem,
    ResourceUsageMonitor
)

from .orchestration import (
    WorkflowOrchestrator,
    TaskScheduler,
    DependencyResolver,
    ExecutionPlanner,
    CreatorWorkflow,
    CreatorWorkflowType
)

# Enhanced processors with creator workflows
from .processors import (
    BaseProcessor,
    ContentProcessor,
    CreatorContentProcessor,
    AudioProcessor,
    VideoProcessor,
    ImageProcessor,
    TextProcessor
)

# Enhanced transformers with platform optimization
from .transformers import (
    BaseTransformer,
    DataTransformer,
    CreatorContentTransformer,
    FormatConverter,
    QualityEnhancer,
    OptimizationEngine,
    PlatformOptimizer
)

# Creator-specific modules
from .creator_workflows import (
    CreatorWorkflowOrchestrator
)

from .platform_integrations import (
    CreatorPlatformManager,
    SpotifyIntegration,
    InstagramIntegration,
    YouTubeIntegration,
    TikTokIntegration,
    LinkedInIntegration,
    MediumIntegration
)

from .monetization_analytics import (
    CreatorMonetizationAnalyzer,
    RevenueStream,
    MonetizationGoal,
    RevenueData,
    MonetizationOpportunity
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "Copyright (c) 2025 Fahed Mlaiel"

# Module versions
PIPELINE_VERSION = "2.0.0"
CREATOR_WORKFLOW_VERSION = "1.0.0"
MONETIZATION_ANALYTICS_VERSION = "1.0.0"

# Supported creator types
SUPPORTED_CREATOR_TYPES = [
    'musician',
    'blogger', 
    'photographer',
    'influencer',
    'comedian'
]

# Supported platforms
SUPPORTED_PLATFORMS = [
    'spotify',
    'apple_music',
    'youtube_music',
    'youtube',
    'instagram',
    'tiktok',
    'twitter',
    'linkedin',
    'medium',
    'substack',
    'flickr',
    'shutterstock',
    'getty',
    'soundcloud',
    'bandcamp'
]

# Revenue streams
SUPPORTED_REVENUE_STREAMS = [
    'streaming',
    'advertising', 
    'sponsorships',
    'affiliate',
    'merchandise',
    'subscriptions',
    'licensing',
    'live_events',
    'courses',
    'tips',
    'freelance',
    'stock_sales'
]

__all__ = [
    # Coordinators
    "ContentPipelineCoordinator",
    "ProcessingOrchestrator", 
    "QualityAssuranceCoordinator",
    
    # Engines
    "StreamProcessingEngine",
    "BatchProcessingEngine",
    "TransformationEngine",
    "ValidationEngine",
    
    # Extractors
    "MultiFormatExtractor",
    "MetadataExtractor",
    "FeatureExtractor", 
    "ContentExtractor",
    
    # Loaders
    "DistributedLoader",
    "PlatformLoader",
    "StorageLoader",
    "AnalyticsLoader",
    
    # Monitors
    "PipelineHealthMonitor",
    "PerformanceMetricsCollector",
    "ErrorTrackingSystem",
    "ResourceUsageMonitor",
    
    # Orchestration
    "WorkflowOrchestrator",
    "TaskScheduler",
    "DependencyResolver",
    "ExecutionPlanner",
    "CreatorWorkflow",
    "CreatorWorkflowType",
    
    # Enhanced Processors
    "ContentProcessor",
    "CreatorContentProcessor",
    "AudioProcessor",
    "VideoProcessor", 
    "ImageProcessor",
    "TextProcessor",
    
    # Enhanced Transformers
    "DataTransformer",
    "CreatorContentTransformer",
    "FormatConverter",
    "QualityEnhancer",
    "OptimizationEngine",
    "PlatformOptimizer",
    
    # Creator Workflows
    "CreatorWorkflowOrchestrator",
    
    # Platform Integrations
    "CreatorPlatformManager",
    "SpotifyIntegration",
    "InstagramIntegration",
    "YouTubeIntegration",
    "TikTokIntegration",
    "LinkedInIntegration",
    "MediumIntegration",
    
    # Monetization Analytics
    "CreatorMonetizationAnalyzer",
    "RevenueStream",
    "MonetizationGoal",
    "RevenueData",
    "MonetizationOpportunity"
]
