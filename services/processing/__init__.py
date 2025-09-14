"""
Processing Services Module - Enterprise Processing Layer
=======================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Roles**: Lead Dev IA + Backend Senior + ML Engineer + Audio Engineer + DBA
**Module**: Processing Services Layer
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Enterprise-grade processing services for content, AI orchestration, media pipeline,
recommendations, validation, and transformation.
"""

from .content_processor import (
    ContentProcessor,
    ContentType,
    ProcessingResult,
    ProcessingStatus,
    ContentMetadata
)

from .ai_orchestrator import (
    AIOrchestrator,
    AIProvider,
    AIModel,
    AITask,
    AIResponse,
    ProviderConfig
)

from .media_pipeline import (
    MediaPipeline,
    MediaType,
    MediaFormat,
    ProcessingStage,
    MediaAsset,
    TranscodingProfile
)

from .recommendation_engine import (
    RecommendationEngine,
    RecommendationType,
    RecommendationScore,
    UserProfile,
    ContentSimilarity,
    RecommendationResult
)

from .validation_service import (
    ValidationService,
    ValidationRule,
    ValidationResult,
    ValidationSeverity,
    ContentValidator,
    SchemaValidator
)

from .transformation_engine import (
    TransformationEngine,
    TransformationType,
    TransformationRule,
    TransformationResult,
    ContentTransformer,
    DataTransformer
)

__all__ = [
    # Content Processing
    "ContentProcessor",
    "ContentType",
    "ProcessingResult", 
    "ProcessingStatus",
    "ContentMetadata",
    
    # AI Orchestration
    "AIOrchestrator",
    "AIProvider",
    "AIModel",
    "AITask",
    "AIResponse",
    "ProviderConfig",
    
    # Media Processing
    "MediaPipeline",
    "MediaType",
    "MediaFormat",
    "ProcessingStage",
    "MediaAsset",
    "TranscodingProfile",
    
    # Recommendations
    "RecommendationEngine",
    "RecommendationType",
    "RecommendationScore",
    "UserProfile",
    "ContentSimilarity",
    "RecommendationResult",
    
    # Validation
    "ValidationService",
    "ValidationRule",
    "ValidationResult",
    "ValidationSeverity",
    "ContentValidator",
    "SchemaValidator",
    
    # Transformation
    "TransformationEngine",
    "TransformationType",
    "TransformationRule",
    "TransformationResult",
    "ContentTransformer",
    "DataTransformer"
]