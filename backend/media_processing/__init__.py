"""Media Processing Module - Enterprise Architecture

Advanced multi-format media processing capabilities with enterprise-grade IA processing,
content protection, SEO optimization, and collaboration workflows.

Business Logic Pipeline: Creator Multi-format → IA Processing → Protection → SEO → Collaboration → Distribution

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

# Existing processors
from .audio_processor import AudioProcessor
from .video_processor import VideoProcessor
from .image_optimizer import ImageOptimizer
from .format_converter import FormatConverter
from .quality_analyzer import QualityAnalyzer

# New enterprise components - Phase 1: IA Processing Core
from .ai_content_orchestrator import AIContentOrchestrator, get_orchestrator
from .intelligent_content_analyzer import IntelligentContentAnalyzer, get_content_analyzer
from .multimodal_ai_processor import MultimodalAIProcessor, get_multimodal_processor

# New enterprise components - Phase 2: Content Protection Integration (Priority 1)
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
    # Existing processors
    'AudioProcessor',
    'VideoProcessor', 
    'ImageOptimizer',
    'FormatConverter',
    'QualityAnalyzer',
    
    # Enterprise IA Processing Core
    'AIContentOrchestrator',
    'get_orchestrator',
    'IntelligentContentAnalyzer', 
    'get_content_analyzer',
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