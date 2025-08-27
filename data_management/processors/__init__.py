"""
⚙️ Data Processors Module - IA Influencer Agent Platform Enterprise
===================================================================
Module: backend/data_management/processors/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Data Processors - Enterprise Production-Ready Ultra Advanced
Responsibility: Traitement avancé des données multi-format pour créateurs, protection contenu et monétisation
========================================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Toute tentative de vol de ce concept, de cette idée ou de ce code sans autorisation personnelle claire 
et écrite de Fahed Mlaiel est strictement interdite et sera poursuivie en justice selon la loi allemande.
Contact obligatoire: mlaiel@live.de

LOGIQUE MÉTIER PROCESSORS COMPLETE:
User Upload → Format Detection → Quality Analysis → Metadata Extraction → Content Analysis → 
Feature Extraction → AI Fingerprinting → Protection Preparation → Optimization → SEO Enhancement → 
Collaboration Matching → Distribution Preparation → Monetization Analytics
"""

__version__ = "4.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

# Core Processor Imports
from .base_processor import BaseProcessor, AsyncBaseProcessor
from .audio_processor import AudioProcessor, AsyncAudioProcessor
from .video_processor import VideoProcessor, AsyncVideoProcessor
from .image_processor import ImageProcessor, AsyncImageProcessor
from .document_processor import DocumentProcessor, AsyncDocumentProcessor
from .metadata_processor import MetadataProcessor, AsyncMetadataProcessor
from .batch_processor import BatchProcessor, AsyncBatchProcessor

# Specialized Content Processors
from .content_fingerprint_processor import ContentFingerprintProcessor, AsyncContentFingerprintProcessor
from .protection_processor import ProtectionProcessor, AsyncProtectionProcessor
from .monetization_processor import MonetizationProcessor, AsyncMonetizationProcessor
from .collaboration_processor import CollaborationProcessor, AsyncCollaborationProcessor
from .distribution_processor import DistributionProcessor, AsyncDistributionProcessor
from .analytics_processor import AnalyticsProcessor, AsyncAnalyticsProcessor
from .seo_processor import SEOProcessor, AsyncSEOProcessor
from .streaming_processor import StreamingProcessor, AsyncStreamingProcessor
from .social_media_processor import SocialMediaProcessor, AsyncSocialMediaProcessor
from .quality_enhancement_processor import QualityEnhancementProcessor, AsyncQualityEnhancementProcessor

__all__ = [
    # Base Processors
    "BaseProcessor", "AsyncBaseProcessor",
    
    # Content Type Processors
    "AudioProcessor", "AsyncAudioProcessor",
    "VideoProcessor", "AsyncVideoProcessor", 
    "ImageProcessor", "AsyncImageProcessor",
    "DocumentProcessor", "AsyncDocumentProcessor",
    
    # Core Specialized Processors
    "MetadataProcessor", "AsyncMetadataProcessor",
    "BatchProcessor", "AsyncBatchProcessor",
    
    # Advanced Content Protection & Monetization Processors
    "ContentFingerprintProcessor", "AsyncContentFingerprintProcessor",
    "ProtectionProcessor", "AsyncProtectionProcessor",
    "MonetizationProcessor", "AsyncMonetizationProcessor",
    
    # Collaboration & Distribution Processors
    "CollaborationProcessor", "AsyncCollaborationProcessor",
    "DistributionProcessor", "AsyncDistributionProcessor",
    
    # Analytics & SEO Processors
    "AnalyticsProcessor", "AsyncAnalyticsProcessor", 
    "SEOProcessor", "AsyncSEOProcessor",
    
    # Platform-Specific Processors
    "StreamingProcessor", "AsyncStreamingProcessor",
    "SocialMediaProcessor", "AsyncSocialMediaProcessor",
    
    # Quality Enhancement Processor
    "QualityEnhancementProcessor", "AsyncQualityEnhancementProcessor"
]
