"""Vision Agent Module - Enterprise Computer Vision System
=======================================================

Comprehensive computer vision system for content creators and influencers
with advanced image/video processing, AI-powered analysis, and privacy protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
from .vision_orchestrator import VisionOrchestrator
from .image_processor import ImageProcessor
from .video_analyzer import VideoAnalyzer
from .object_detector import ObjectDetector
from .visual_similarity import VisualSimilarityMatcher
from .face_recognition import FaceRecognitionSystem
from .optical_character_reader import OpticalCharacterReader
from .scene_analyzer import SceneAnalyzer
from .metadata_extractor import MetadataExtractor
from .config import VisionAgentConfig, vision_config

# Version information
__version__ = "2.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary - All Rights Reserved"

# Module exports
__all__ = [
    # Core orchestrator
    'VisionOrchestrator',
    
    # Processing components
    'ImageProcessor',
    'VideoAnalyzer', 
    'ObjectDetector',
    'VisualSimilarityMatcher',
    'FaceRecognitionSystem',
    'OpticalCharacterReader',
    'SceneAnalyzer',
    'MetadataExtractor',
    
    # Configuration
    'VisionAgentConfig',
    'vision_config',
    
    # Module info
    '__version__',
    '__author__',
    '__email__',
    '__license__'
]

# Module metadata
MODULE_INFO = {
    'name': 'IA Influencer Agent - Vision System',
    'version': __version__,
    'author': __author__,
    'email': __email__,
    'license': __license__,
    'description': 'Enterprise computer vision system for content creators',
    'capabilities': [
        'Advanced Image Processing',
        'Video Analysis & Scene Detection',
        'AI-Powered Object Detection',
        'Visual Similarity Matching',
        'Privacy-Protected Face Recognition',
        'Multi-Language OCR',
        'Scene Understanding & Context Recognition',
        'Comprehensive Metadata Extraction',
        'Content Forensics & Authenticity Analysis',
        'Batch Processing & Performance Optimization'
    ],
    'technologies': [
        'OpenCV', 'PyTorch', 'PIL/Pillow', 'scikit-image',
        'YOLO v8', 'SSD MobileNet', 'ResNet50', 'Tesseract OCR',
        'FAISS Vector Database', 'ImageHash', 'ExifRead'
    ],
    'privacy_features': [
        'Automatic EXIF Removal',
        'Face Anonymization',
        'GPS Data Protection', 
        'Content Filtering',
        'Secure Data Handling'
    ]
}

def get_module_info():
    """Get comprehensive module information"""    return MODULE_INFO.copy()

def get_version():
    """Get module version"""    return __version__

def get_available_components():
    """Get list of available vision processing components"""    return [
        {
            'name': 'VisionOrchestrator',
            'description': 'Main coordination system for all vision operations',
            'capabilities': ['Task Orchestration', 'Pipeline Management', 'Result Aggregation']
        },
        {
            'name': 'ImageProcessor', 
            'description': 'Advanced image processing and enhancement',
            'capabilities': ['Quality Assessment', 'Enhancement', 'Format Conversion', 'Watermarking']
        },
        {
            'name': 'VideoAnalyzer',
            'description': 'Comprehensive video analysis system',
            'capabilities': ['Scene Detection', 'Motion Analysis', 'Quality Assessment', 'Thumbnails']
        },
        {
            'name': 'ObjectDetector',
            'description': 'AI-powered object detection using multiple models',
            'capabilities': ['YOLO Detection', 'SSD Detection', 'Multi-Model Ensemble', 'Custom Training']
        },
        {
            'name': 'VisualSimilarityMatcher',
            'description': 'Advanced visual similarity and duplicate detection',
            'capabilities': ['Deep Feature Matching', 'Perceptual Hashing', 'FAISS Search', 'Similarity Scoring']
        },
        {
            'name': 'FaceRecognitionSystem',
            'description': 'Privacy-first facial recognition and analysis',
            'capabilities': ['Face Detection', 'Privacy Protection', 'Emotion Analysis', 'Anonymization']
        },
        {
            'name': 'OpticalCharacterReader',
            'description': 'Multi-language OCR with document analysis',
            'capabilities': ['Text Extraction', '10+ Languages', 'Document Structure', 'Data Extraction']
        },
        {
            'name': 'SceneAnalyzer',
            'description': 'Advanced scene understanding and context recognition',
            'capabilities': ['Scene Classification', 'Aesthetic Analysis', 'Composition Rules', 'Color Harmony']
        },
        {
            'name': 'MetadataExtractor',
            'description': 'Comprehensive metadata extraction and forensics',
            'capabilities': ['EXIF Processing', 'Privacy Protection', 'Forensic Analysis', 'Data Sanitization']
        }
    ]

def create_vision_system(config_path=None):
    """    Factory function to create a complete vision processing system
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Configured VisionOrchestrator instance
    """    try:
        # Load configuration
        if config_path:
            config = VisionAgentConfig(config_path)
        else:
            config = vision_config
        
        # Create orchestrator with configuration
        orchestrator = VisionOrchestrator()
        
        return orchestrator
        
    except Exception as e:
        raise RuntimeError(f"Failed to create vision system: {e}")

def create_vision_agent():
    """Legacy factory function for backward compatibility"""    return create_vision_system()

# Legal and licensing information
LEGAL_NOTICE = """⚠️  CRITICAL LEGAL NOTICE - PROPRIETARY SOFTWARE ⚠️

This software and all associated intellectual property are the exclusive property of:

    Fahed Mlaiel
    Email: mlaiel@live.de
    
COPYRIGHT NOTICE:
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

INTELLECTUAL PROPERTY WARNING:
This code, its architecture, algorithms, and design patterns are protected intellectual property.
Any unauthorized use, copying, modification, distribution, or commercialization is strictly 
prohibited and will be prosecuted to the full extent of the law.

LICENSING:
This software is proprietary and confidential. No part of this software may be:
- Copied, modified, or distributed without explicit written permission
- Reverse engineered, decompiled, or disassembled
- Used for commercial purposes without a valid commercial license
- Integrated into other software without authorization

For licensing inquiries, commercial use, or partnership opportunities, contact:
mlaiel@live.de

VIOLATION CONSEQUENCES:
Unauthorized use may result in:
- Legal action for copyright infringement
- Financial damages and penalties
- Injunctive relief
- Recovery of attorney fees and costs

By accessing this code, you acknowledge that you have read, understood, and agree to 
be bound by these terms.
"""
def print_legal_notice():
    """Print the legal notice and licensing information"""    print(LEGAL_NOTICE)

def get_legal_notice():
    """Get the legal notice text"""    return LEGAL_NOTICE

# Module initialization
import logging
logger = logging.getLogger(__name__)

logger.info(f"IA Influencer Agent Vision System v{__version__} initialized")
logger.info(f"Author: {__author__} <{__email__}>")
logger.info("⚠️  Proprietary software - Unauthorized use prohibited")

# Export legal notice for documentation
__doc__ += "\n\n" + LEGAL_NOTICE
