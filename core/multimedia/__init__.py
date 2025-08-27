"""
Core Multimedia Module - Enterprise Multimedia Processing Hub

Advanced multimedia processing engine for IA Influencer Agent platform.
Handles complex multi-format content processing with AI-powered enhancement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

from .orchestrator import MultimediaOrchestrator
from .registry import MultimediaRegistry
from .converter import MultimediaConverter
from .optimizer import MultimediaOptimizer
from .transcoder import MultimediaTranscoder
from .encoder import MultimediaEncoder
from .decoder import MultimediaDecoder
from .analyzer import MultimediaAnalyzer
from .enhancer import MultimediaEnhancer
from .pipeline import MultimediaPipeline
from .factory import MultimediaFactory
from .router import MultimediaRouter
from .cache import MultimediaCache
from .scheduler import MultimediaScheduler
from .validator import MultimediaValidator
from .normalizer import MultimediaNormalizer
from .generator import MultimediaGenerator
from .watermark import MultimediaWatermark
from .compressor import MultimediaCompressor
from .streamer import MultimediaStreamer
from .synchronizer import MultimediaSynchronizer
from .merger import MultimediaMerger
from .splitter import MultimediaSplitter
from .thumbnails import MultimediaThumbnails
from .metadata import MultimediaMetadata
from .fingerprint import MultimediaFingerprint
from .quality import MultimediaQuality
from .format_detector import MultimediaFormatDetector
from .content_extractor import MultimediaContentExtractor
from .batch_processor import MultimediaBatchProcessor
from .realtime_processor import MultimediaRealtimeProcessor
from .ai_processor import MultimediaAIProcessor
from .index import MultimediaIndex

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

__all__ = [
    "MultimediaOrchestrator",
    "MultimediaRegistry", 
    "MultimediaConverter",
    "MultimediaOptimizer",
    "MultimediaTranscoder",
    "MultimediaEncoder",
    "MultimediaDecoder",
    "MultimediaAnalyzer",
    "MultimediaEnhancer",
    "MultimediaPipeline",
    "MultimediaFactory",
    "MultimediaRouter",
    "MultimediaCache",
    "MultimediaScheduler",
    "MultimediaValidator",
    "MultimediaNormalizer",
    "MultimediaGenerator",
    "MultimediaWatermark",
    "MultimediaCompressor",
    "MultimediaStreamer",
    "MultimediaSynchronizer",
    "MultimediaMerger",
    "MultimediaSplitter",
    "MultimediaThumbnails",
    "MultimediaMetadata",
    "MultimediaFingerprint",
    "MultimediaQuality",
    "MultimediaFormatDetector",
    "MultimediaContentExtractor",
    "MultimediaBatchProcessor",
    "MultimediaRealtimeProcessor",
    "MultimediaAIProcessor",
    "MultimediaIndex"
]
