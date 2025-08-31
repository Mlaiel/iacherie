"""IA Influencer Agent - Data Processors Module
============================================

Professional multi-format content processing engine for the IA Influencer Agent platform.
Handles audio, video, image, and text processing with enterprise-grade performance.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  COPYRIGHT WARNING ⚠️
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or theft of this code or concept without explicit 
written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and 
will result in immediate legal action under German and international copyright law.

Components:
-----------
- AudioProcessor: Professional audio processing for music creators
- VideoProcessor: Professional video analysis and transformation  
- ImageProcessor: High-performance image processing and enhancement
- TextProcessor: NLP and content analysis for creators
- MetadataProcessor: Content metadata extraction and enhancement
- QualityProcessor: Content quality assessment and optimization
- FormatProcessor: Multi-format conversion and standardization
- CompressionProcessor: Intelligent content compression
- OrchestrationProcessor: Professional workflow orchestration
"""
from typing import Dict, Any, List, Optional, Union
import asyncio
import logging

# Core processor imports
from .audio_processor import AudioProcessor
from .video_processor import VideoProcessor
from .image_processor import ImageProcessor
from .text_processor import TextProcessor
from .metadata_processor import MetadataProcessor
from .quality_processor import QualityProcessor
from .format_processor import FormatProcessor
from .compression_processor import CompressionProcessor
from .orchestration_processor import OrchestrationProcessor

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "Copyright 2025 Fahed Mlaiel. All rights reserved."

# Configure logging
logger = logging.getLogger(__name__)

# Supported content formats
SUPPORTED_FORMATS = {
    'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
    'video': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'],
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'],
    'text': ['.txt', '.md', '.pdf', '.doc', '.docx', '.rtf', '.html', '.xml']
}

# Default processing configurations
DEFAULT_CONFIG = {
    'audio': {
        'sample_rate': 44100,
        'bit_depth': 16,
        'channels': 2,
        'format': 'wav'
    },
    'video': {
        'resolution': '1920x1080',
        'fps': 30,
        'codec': 'h264',
        'bitrate': '5000k'
    },
    'image': {
        'max_width': 1920,
        'max_height': 1080,
        'quality': 85,
        'format': 'jpg'
    },
    'text': {
        'encoding': 'utf-8',
        'max_length': 100000,
        'language': 'auto'
    }
}

class ProcessorRegistry:
    """Registry for all available processors in the system"""
    
    def __init__(self):
        self._processors = {}
        self._initialize_processors()
    
    def _initialize_processors(self):
        """Initialize all processor instances"""
        self._processors = {
            'audio': AudioProcessor(),
            'video': VideoProcessor(),
            'image': ImageProcessor(),
            'text': TextProcessor(),
            'metadata': MetadataProcessor(),
            'quality': QualityProcessor(),
            'format': FormatProcessor(),
            'compression': CompressionProcessor(),
            'orchestration': OrchestrationProcessor()
        }
        
        logger.info(f"Initialized {len(self._processors)} processors")
    
    def get_processor(self, processor_type: str):
        """Get processor instance by type"""
        return self._processors.get(processor_type)
    
    def list_processors(self) -> List[str]:
        """List all available processor types"""
        return list(self._processors.keys())

# Global processor registry
processor_registry = ProcessorRegistry()

def get_processor(processor_type: str):
    """Get processor instance by type"""
    return processor_registry.get_processor(processor_type)

def list_processors() -> List[str]:
    """List all available processor types"""
    return processor_registry.list_processors()

async def process_content(
    content_data: bytes,
    content_type: str,
    format_hint: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process content using appropriate processor
    
    Args:
        content_data: Raw content bytes
        content_type: Type of content (audio, video, image, text)
        format_hint: Optional format hint for processing
        config: Optional processing configuration
    
    Returns:
        Dict containing processed content and metadata
    """
    processor = get_processor(content_type)
    if not processor:
        raise ValueError(f"No processor available for content type: {content_type}")
    
    # Merge default config with provided config
    processing_config = DEFAULT_CONFIG.get(content_type, {}).copy()
    if config:
        processing_config.update(config)
    
    try:
        result = await processor.process(
            content_data, 
            format_hint=format_hint,
            config=processing_config
        )
        
        logger.info(f"Successfully processed {content_type} content")
        return result
        
    except Exception as e:
        logger.error(f"Error processing {content_type} content: {str(e)}")
        raise

# Export all public components
__all__ = [
    # Core processors
    'AudioProcessor',
    'VideoProcessor', 
    'ImageProcessor',
    'TextProcessor',
    'MetadataProcessor',
    'QualityProcessor',
    'FormatProcessor',
    'CompressionProcessor',
    'OrchestrationProcessor',
    
    # Registry and functions
    'ProcessorRegistry',
    'processor_registry',
    'get_processor',
    'list_processors',
    'process_content',
    
    # Constants
    'SUPPORTED_FORMATS',
    'DEFAULT_CONFIG'
]
