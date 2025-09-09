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
- UnifiedConverter: Universal format conversion and intelligent compression
- WorkflowOrchestrator: Professional workflow orchestration with quality management
"""

from typing import Dict, Any, List, Optional, Union
import asyncio
import logging

# Core processor imports with graceful error handling
_available_processors = {}

def _safe_import_processor(module_name, class_name):
    """Safely import a processor with error handling"""
    try:
        module = __import__(f".{module_name}", package=__name__, fromlist=[class_name])
        processor_class = getattr(module, class_name)
        globals()[class_name] = processor_class
        _available_processors[class_name] = processor_class
        logger.info(f"Successfully loaded {class_name}")
        return processor_class
    except Exception as e:
        logger.warning(f"Failed to load {class_name}: {e}")
        return None

# Import processors safely
AudioProcessor = _safe_import_processor("audio_processor", "AudioProcessor")
VideoProcessor = _safe_import_processor("video_processor", "VideoProcessor")
ImageProcessor = _safe_import_processor("image_processor", "ImageProcessor")
TextProcessor = _safe_import_processor("text_processor", "TextProcessor")
MetadataProcessor = _safe_import_processor("metadata_processor", "MetadataProcessor")
UnifiedConverter = _safe_import_processor("unified_converter", "UnifiedConverter")
WorkflowOrchestrator = _safe_import_processor("workflow_orchestrator", "WorkflowOrchestrator")

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
        self._processors = {}
        
        # Only initialize available processors
        if AudioProcessor:
            try:
                self._processors['audio'] = AudioProcessor()
            except Exception as e:
                logger.warning(f"Failed to initialize AudioProcessor: {e}")
        
        if VideoProcessor:
            try:
                self._processors['video'] = VideoProcessor()
            except Exception as e:
                logger.warning(f"Failed to initialize VideoProcessor: {e}")
        
        if ImageProcessor:
            try:
                self._processors['image'] = ImageProcessor()
            except Exception as e:
                logger.warning(f"Failed to initialize ImageProcessor: {e}")
        
        if TextProcessor:
            try:
                self._processors['text'] = TextProcessor()
            except Exception as e:
                logger.warning(f"Failed to initialize TextProcessor: {e}")
        
        if MetadataProcessor:
            try:
                self._processors['metadata'] = MetadataProcessor()
            except Exception as e:
                logger.warning(f"Failed to initialize MetadataProcessor: {e}")
        
        if UnifiedConverter:
            try:
                self._processors['unified_converter'] = UnifiedConverter()
            except Exception as e:
                logger.warning(f"Failed to initialize UnifiedConverter: {e}")
        
        if WorkflowOrchestrator:
            try:
                self._processors['workflow_orchestrator'] = WorkflowOrchestrator()
            except Exception as e:
                logger.warning(f"Failed to initialize WorkflowOrchestrator: {e}")
        
        logger.info(f"Initialized {len(self._processors)} processors")
    
    def get_processor(self, processor_type: str):
        """Get processor instance by type"""
        return self._processors.get(processor_type)
    
    def list_processors(self) -> List[str]:
        """
List all available processor types"""
        return list(self._processors.keys())

# Global processor registry
processor_registry = ProcessorRegistry()

def get_processor(processor_type: str):
    """
Get processor instance by type"""
    return processor_registry.get_processor(processor_type)

def list_processors() -> List[str]:
    """
List all available processor types"""
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

# Export all available components
__all__ = []

# Add available processors to exports
for processor_name in ['AudioProcessor', 'VideoProcessor', 'ImageProcessor', 
                      'TextProcessor', 'MetadataProcessor', 'UnifiedConverter', 
                      'WorkflowOrchestrator']:
    if globals().get(processor_name):
        __all__.append(processor_name)

# Always export these components
__all__.extend([
    'ProcessorRegistry',
    'processor_registry', 
    'get_processor',
    'list_processors',
    'process_content',
    'SUPPORTED_FORMATS',
    'DEFAULT_CONFIG'
])
