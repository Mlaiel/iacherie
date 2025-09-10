"""Media Processing Module - Enterprise Architecture v3.0.0

CONSOLIDATED ARCHITECTURE (18 FILES MAX):
Advanced multi-format media processing capabilities with enterprise-grade IA processing,
content protection, SEO optimization, and collaboration workflows.

Business Logic Pipeline: Creator Multi-format → IA Processing → Protection → SEO → Collaboration → Distribution

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ CRITICAL LEGAL WARNING ⚠️
This consolidated media processing system contains advanced algorithms and trade secrets
belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED USE IS STRICTLY PROHIBITED.
"""

# ============================================================================
# CORE INFRASTRUCTURE (3 files)
# ============================================================================
from .main_processor import (
    MainProcessor,
    ProcessingRequest,
    ProcessingResult,
    MediaProcessingConfig,
    ProcessingStage,
    ContentType,
    ProcessingPriority,
    ProcessingStatus,
    get_main_processor,
    process_content
)

from .processing_exceptions import (
    MediaProcessingError,
    AIProcessingError,
    ContentProcessingError,
    ProtectionError,
    ValidationError,
    BusinessLogicError,
    ErrorSeverity,
    ErrorCategory,
    ErrorHandler,
    handle_processing_errors,
    error_metrics
)

# ============================================================================
# EXISTING MEDIA PROCESSORS (3 files) - TO BE ENRICHED
# ============================================================================
from .audio_processor import AudioProcessor
from .video_processor import VideoProcessor
try:
    from .image_processor import ImageProcessor
except ImportError:
    # Fallback to existing image optimizer during migration
    from .image_optimizer import ImageOptimizer as ImageProcessor

# ============================================================================
# EXISTING AI PROCESSORS - NOW CONSOLIDATED INTO 4 FILES ✅ PHASE 2 COMPLÉTÉE
# ============================================================================

# ✅ CONSOLIDATED AI PROCESSORS (Phase 2 completed)
from .ai_orchestrator import (
    AIOrchestrator,
    AIModelManager,
    AIProcessingRequest,
    AIProcessingResult,
    get_ai_orchestrator
)
from .multimodal_processor import (
    MultimodalProcessor,
    FusionStrategy,
    MultimodalRequest,
    MultimodalResult,
    get_multimodal_processor
)
from .content_classifier import (
    ContentClassifier,
    ImageClassifier,
    AudioClassifier,
    TextClassifier,
    MetadataExtractor,
    ClassificationResult,
    MetadataExtractionResult,
    ContentAnalysisResult,
    ContentCategory,
    QualityLevel,
    AudienceType,
    ContentMood,
    get_content_classifier
)
from .enhancement_pipeline import (
    EnhancementPipeline,
    QualityAssessor,
    ImageEnhancer,
    AudioEnhancer,
    SRResNet,
    DenoisingAutoEncoder,
    EnhancementParams,
    EnhancementResult,
    QualityAssessment,
    EnhancementMode,
    EnhancementType,
    QualityMetric,
    get_enhancement_pipeline
)

# Legacy support for transition period
try:
    from .ai_content_orchestrator import AIContentOrchestrator, get_orchestrator
    from .intelligent_content_analyzer import IntelligentContentAnalyzer, get_content_analyzer
    from .multimodal_ai_processor import MultimodalAIProcessor, get_multimodal_processor
    _LEGACY_AI_AVAILABLE = True
except ImportError:
    _LEGACY_AI_AVAILABLE = False

_CONSOLIDATED_AI_AVAILABLE = True

# ============================================================================
# EXISTING PROTECTION PROCESSORS - TO BE CONSOLIDATED INTO 3 FILES  
# ============================================================================
from .watermark_processor import WatermarkProcessor

# Try consolidated protection processors
try:
    from .protection_manager import ProtectionManager
    from .anti_piracy_engine import AntiPiracyEngine
    _CONSOLIDATED_PROTECTION_AVAILABLE = True
except ImportError:
    _CONSOLIDATED_PROTECTION_AVAILABLE = False

# ============================================================================
# EXISTING PROCESSING COMPONENTS - TO BE CONSOLIDATED
# ============================================================================
from .protection_workflow_manager import ProtectionWorkflowManager, get_protection_manager
from .rights_validation_processor import RightsValidationProcessor, get_rights_processor
from .fingerprint_generation_engine import FingerprintGenerationEngine, get_fingerprint_engine
from .watermark_processor import WatermarkProcessor, get_watermark_processor
from .copyright_compliance_checker import CopyrightComplianceChecker, get_compliance_checker
from .anti_piracy_processor import AntiPiracyProcessor, get_anti_piracy_processor
from .blockchain_registration_handler import BlockchainRegistrationHandler, get_blockchain_handler

# New enterprise components - Phase 3: Advanced IA Processing (Priority 2)
from .content_intelligence_engine import ContentIntelligenceEngine, get_intelligence_engine
from .ai_enhancement_pipeline import AIEnhancementPipeline, get_enhancement_pipeline
from .smart_quality_optimizer import SmartQualityOptimizer, get_quality_optimizer
from .content_classification_ai import ContentClassificationAI, get_classification_ai
from .intelligent_metadata_extractor import IntelligentMetadataExtractor, get_metadata_extractor

# New enterprise components - Phase 4: SEO & Distribution Pipeline
from .seo_metadata_processor import SEOMetadataProcessor, get_seo_processor

# New enterprise components - Phase 5: Collaboration & Workflow Integration
from .collaboration_workflow_processor import CollaborationWorkflowProcessor, get_collaboration_processor
from .content_distribution_orchestrator import ContentDistributionOrchestrator, get_distribution_orchestrator

__all__ = [
    # ✅ PHASE 1: Core Infrastructure (3/3 COMPLETED)
    'MainProcessor',
    'get_main_processor',
    'ProcessingRequest',
    'ProcessingResult',
    'ProcessingMode',
    'ProcessingStage',
    
    # Exception handling
    'ProcessingError',
    'AIProcessingError',
    'ModelInferenceError',
    'ValidationError',
    'ProtectionError',
    'BusinessLogicError',
    'ErrorSeverity',
    'ErrorCategory',
    'ErrorHandler',
    'handle_processing_errors',
    'error_metrics',
    
    # ✅ PHASE 2: AI Processing (4/4 COMPLETED)
    'AIOrchestrator',
    'AIModelManager',
    'AIProcessingRequest',
    'AIProcessingResult',
    'get_ai_orchestrator',
    
    'MultimodalProcessor',
    'FusionStrategy',
    'MultimodalRequest',
    'MultimodalResult',
    'get_multimodal_processor',
    
    'ContentClassifier',
    'ImageClassifier',
    'AudioClassifier',
    'TextClassifier',
    'MetadataExtractor',
    'ClassificationResult',
    'MetadataExtractionResult',
    'ContentAnalysisResult',
    'ContentCategory',
    'QualityLevel',
    'AudienceType',
    'ContentMood',
    'get_content_classifier',
    
    'EnhancementPipeline',
    'QualityAssessor',
    'ImageEnhancer',
    'AudioEnhancer',
    'SRResNet',
    'DenoisingAutoEncoder',
    'EnhancementParams',
    'EnhancementResult',
    'QualityAssessment',
    'EnhancementMode',
    'EnhancementType',
    'QualityMetric',
    'get_enhancement_pipeline',
    
    # Existing processors
    'AudioProcessor',
    'VideoProcessor', 
    'ImageProcessor',
    'FormatConverter',
    'QualityAnalyzer',
    'MultimodalAIProcessor',
    'get_multimodal_processor',
    
    # Content Protection Integration (Priority 1)
    'ProtectionWorkflowManager',
    'get_protection_manager',
    'RightsValidationProcessor',
    'get_rights_processor',
    'FingerprintGenerationEngine',
    'get_fingerprint_engine',
    'WatermarkProcessor',
    'get_watermark_processor',
    'CopyrightComplianceChecker',
    'get_compliance_checker',
    'AntiPiracyProcessor',
    'get_anti_piracy_processor',
    'BlockchainRegistrationHandler',
    'get_blockchain_handler',
    
    # Advanced IA Processing (Priority 2)
    'ContentIntelligenceEngine',
    'get_intelligence_engine',
    'AIEnhancementPipeline',
    'get_enhancement_pipeline',
    'SmartQualityOptimizer',
    'get_quality_optimizer',
    'ContentClassificationAI',
    'get_classification_ai',
    'IntelligentMetadataExtractor',
    'get_metadata_extractor',
    
    # SEO & Distribution Pipeline
    'SEOMetadataProcessor',
    'get_seo_processor',
    
    # Collaboration & Workflow Integration
    'CollaborationWorkflowProcessor',
    'get_collaboration_processor',
    'ContentDistributionOrchestrator',
    'get_distribution_orchestrator'
]

__version__ = "2.1.0"  # Advanced IA Processing & Content Protection Complete