"""
Content Ingestion module __init__.py
===================================

Professional multi-format content ingestion for IA Influencer Agent platform.
Complete enterprise-grade content ingestion system with batch processing,
metadata extraction, and AI-powered content analysis.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

  INTELLECTUAL PROPERTY WARNING 
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.

PROJECT TEAM SPECIALTIES:
- Lead Dev IA & ML Engineer: Advanced AI/ML algorithms and model integration
- Backend Senior Developer: Enterprise architecture and scalable systems
- DBA & Data Engineer: Database optimization and data pipeline management  
- Security Specialist: Content protection and security validation
- DevOps Engineer: Infrastructure automation and deployment
- Audio/Video Specialist: Multimedia processing and codec optimization
- Microservices Architect: Distributed systems and service orchestration
- IA Prompt Engineer: AI model fine-tuning and content analysis
"""

# Core ingestion components
from .content_ingestion_manager import (
    ContentIngestionManager,
    IngestionRequest,
    IngestionResult,
    IngestionStatus,
    IngestionPriority,
    ProcessingMode,
    ContentSource,
    ContentType,
    ProcessingMetrics,
    QualityMetrics,
    SecurityAssessment
)

from .multi_format_processor import (
    MultiFormatProcessor,
    ProcessingOptions,
    ProcessingQuality,
    ProcessingResult,
    OutputFormat
)

from .metadata_extractor import (
    MetadataExtractor,
    MetadataCollection,
    MetadataType,
    ContentFormat
)

from .batch_ingestion_processor import (
    BatchIngestionProcessor,
    BatchConfiguration,
    BatchItem,
    BatchResult,
    BatchStatus,
    BatchPriority,
    ProcessingMode
)

# Advanced ingestion engines
from .real_time_ingestion_engine import (
    RealTimeIngestionEngine,
    StreamingSession,
    StreamingChunk,
    StreamingResult,
    StreamingMode,
    StreamingQuality,
    StreamingPriority
)

from .content_validation_engine import (
    ContentValidationEngine,
    ValidationResult,
    ValidationIssue,
    ValidationMetrics,
    ValidationSeverity,
    ValidationCategory,
    ContentPolicy
)

from .intelligent_content_router import (
    IntelligentContentRouter,
    RoutingPlan,
    RoutingDecision,
    RoutingResult,
    Platform,
    RoutingRule,
    RoutingStrategy,
    RoutingPriority,
    PlatformType,
    ContentCategory
)

# Orchestration and utilities
from .index import (
    DataIngestionOrchestrator,
    IngestionCapabilities,
    create_ingestion_orchestrator
)

# Version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary - All Rights Reserved"

# Export all public classes and functions
__all__ = [
    # Core managers
    "ContentIngestionManager",
    "MultiFormatProcessor", 
    "MetadataExtractor",
    "BatchIngestionProcessor",
    
    # Advanced engines
    "RealTimeIngestionEngine",
    "ContentValidationEngine",
    "IntelligentContentRouter",
    
    # Data classes and enums - Content Ingestion
    "IngestionRequest",
    "IngestionResult", 
    "IngestionStatus",
    "IngestionPriority",
    "ProcessingMode",
    "ContentSource",
    "ContentType",
    "ProcessingMetrics",
    "QualityMetrics",
    "SecurityAssessment",
    
    # Data classes - Multi-format Processing
    "ProcessingOptions",
    "ProcessingQuality",
    "ProcessingResult",
    "OutputFormat",
    
    # Data classes - Metadata Extraction
    "MetadataCollection",
    "MetadataType",
    "ContentFormat",
    
    # Data classes - Batch Processing
    "BatchConfiguration",
    "BatchItem",
    "BatchResult",
    "BatchStatus",
    "BatchPriority",
    
    # Data classes - Real-time Ingestion
    "StreamingSession",
    "StreamingChunk", 
    "StreamingResult",
    "StreamingMode",
    "StreamingQuality",
    "StreamingPriority",
    
    # Data classes - Content Validation
    "ValidationResult",
    "ValidationIssue",
    "ValidationMetrics", 
    "ValidationSeverity",
    "ValidationCategory",
    "ContentPolicy",
    
    # Data classes - Intelligent Routing
    "RoutingPlan",
    "RoutingDecision",
    "RoutingResult",
    "Platform",
    "RoutingRule",
    "RoutingStrategy", 
    "RoutingPriority",
    "PlatformType",
    "ContentCategory",
    
    # Orchestration
    "DataIngestionOrchestrator",
    "IngestionCapabilities",
    "create_ingestion_orchestrator",
    
    # Module metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__"
]