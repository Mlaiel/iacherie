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

# New enterprise components - Phase 2: Content Protection Integration
from .protection_workflow_manager import ProtectionWorkflowManager, get_protection_manager

# New enterprise components - Phase 3: SEO & Distribution Pipeline
from .seo_metadata_processor import SEOMetadataProcessor, get_seo_processor

# New enterprise components - Phase 4: Collaboration & Workflow Integration
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
    
    # Content Protection Integration
    'ProtectionWorkflowManager',
    'get_protection_manager',
    
    # SEO & Distribution Pipeline
    'SEOMetadataProcessor',
    'get_seo_processor',
    
    # Collaboration & Workflow Integration
    'CollaborationWorkflowProcessor',
    'get_collaboration_processor',
    'ContentDistributionOrchestrator',
    'get_distribution_orchestrator'
]

__version__ = "2.0.0"  # Enterprise Architecture Version