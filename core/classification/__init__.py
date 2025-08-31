"""IA Influencer Agent - Classification Core Module

Enterprise-grade multi-format content classification system for content protection,
monetization, and intelligent routing. Provides advanced AI-powered classification
across audio, video, image, and text content with real-time violation detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent with Content Protection
Team: Lead Dev IA + Backend Senior + ML Engineer + DevOps + DBA + Security + Microservices + Audio + IA Prompt Engineer

Copyright © 2025 Fahed Mlaiel. All rights reserved.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing and collaboration.

WARNING: This code and concept are protected by copyright law. Any unauthorized
copying, modification, distribution, or use of this code without explicit written
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will
result in legal action under German and international copyright law.
"""
from typing import Dict, List, Optional, Union, Any

# Core classification modules
from .audio_classifier import AudioContentClassifier
from .video_classifier import VideoContentClassifier  
from .image_classifier import ImageContentClassifier
from .text_classifier import TextContentClassifier
from .multimodal_classifier import MultimodalContentClassifier

# Factory and orchestration
from .classifier_factory import ClassifierFactory
from .content_categorizer import ContentCategorizer

# Specialized analyzers
from .genre_detector import GenreDetector
from .mood_analyzer import MoodAnalyzer
from .quality_assessor import QualityAssessor

# Protection and monitoring
from .similarity_matcher import SimilarityMatcher
from .violation_detector import ViolationDetector

__all__ = [
    # Core classifiers
    'AudioContentClassifier',
    'VideoContentClassifier', 
    'ImageContentClassifier',
    'TextContentClassifier',
    'MultimodalContentClassifier',
    
    # Factory and orchestration
    'ClassifierFactory',
    'ContentCategorizer',
    
    # Specialized analyzers
    'GenreDetector',
    'MoodAnalyzer',
    'QualityAssessor',
    
    # Protection and monitoring
    'SimilarityMatcher',
    'ViolationDetector',
    
    # Configuration constants
    'CLASSIFICATION_THRESHOLDS',
    'SUPPORTED_FORMATS',
    'DEFAULT_CONFIG'
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Classification confidence thresholds
CLASSIFICATION_THRESHOLDS = {
    'genre_detection': 0.75,
    'mood_analysis': 0.70,
    'quality_assessment': 0.80,
    'similarity_matching': 0.85,
    'violation_detection': 0.75,
    'content_categorization': 0.70
}

# Supported content formats
SUPPORTED_FORMATS = {
    'audio': ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma'],
    'video': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'],
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
    'text': ['.txt', '.md', '.html', '.pdf', '.doc', '.docx', '.rtf']
}

# Default configuration
DEFAULT_CONFIG = {
    'batch_size': 32,
    'max_workers': 4,
    'cache_enabled': True,
    'metrics_tracking': True,
    'real_time_processing': True,
    'multi_model_ensemble': True
}
CLASSIFICATION_THRESHOLDS = {
    'high_confidence': 0.85,
    'medium_confidence': 0.65,
    'low_confidence': 0.45,
    'violation_threshold': 0.80
}

# Supported content types
SUPPORTED_CONTENT_TYPES = {
    'audio': ['mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg'],
    'video': ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'],
    'image': ['jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff'],
    'text': ['txt', 'md', 'rtf', 'docx', 'pdf']
}

# Content categories for classification
CONTENT_CATEGORIES = {
    'music': ['song', 'instrumental', 'beat', 'remix', 'cover'],
    'video': ['music_video', 'vlog', 'tutorial', 'performance', 'interview'],
    'image': ['album_cover', 'artwork', 'photo', 'poster', 'thumbnail'],
    'text': ['lyrics', 'blog_post', 'description', 'script', 'article']
}
