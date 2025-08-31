"""IA Influencer Agent - Data Processors Index
===========================================

Central index and registry for all content processing components.
Provides unified access patterns and processor discovery mechanisms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

This module serves as the central registry and discovery mechanism for all
content processors in the IA Influencer Agent platform. It provides:

- Processor factory and instantiation
- Configuration management
- Performance monitoring
- Resource allocation
- Error handling and recovery
"""
import logging
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass, field
import asyncio
import time

# Import all processors
from .audio_processor import AudioProcessor
from .video_processor import VideoProcessor
from .image_processor import ImageProcessor
from .text_processor import TextProcessor
from .metadata_processor import MetadataProcessor
from .quality_processor import QualityProcessor
from .format_processor import FormatProcessor
from .compression_processor import CompressionProcessor
from .orchestration_processor import OrchestrationProcessor

logger = logging.getLogger(__name__)

@dataclass
class ProcessorInfo:
    """Information about a registered processor"""    name: str
    class_type: Type
    category: str
    description: str
    supported_formats: List[str] = field(default_factory=list)
    processing_capabilities: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    is_active: bool = True

@dataclass
class ProcessorMetrics:
    """Performance metrics for a processor"""    processor_name: str
    total_processed: int = 0
    successful_processed: int = 0
    failed_processed: int = 0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    last_used: Optional[float] = None
    error_rate: float = 0.0

class ProcessorIndex:
    """Central index and registry for all content processors"""    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ProcessorIndex")
        self._processors: Dict[str, ProcessorInfo] = {}
        self._instances: Dict[str, Any] = {}
        self._metrics: Dict[str, ProcessorMetrics] = {}
        
        # Initialize processor registry
        self._initialize_registry()
    
    def _initialize_registry(self):
        """Initialize the processor registry with all available processors"""        try:
            # Register core processors
            self._register_processor(
                "audio",
                AudioProcessor,
                "content_analysis",
                "Professional audio processing for music creators",
                ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
                ['feature_extraction', 'fingerprinting', 'enhancement', 'format_conversion']
            )
            
            self._register_processor(
                "video",
                VideoProcessor,
                "content_analysis",
                "Professional video analysis and transformation",
                ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'],
                ['scene_detection', 'motion_analysis', 'frame_extraction', 'quality_assessment']
            )
            
            self._register_processor(
                "image",
                ImageProcessor,
                "content_analysis",
                "High-performance image processing and enhancement",
                ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'],
                ['enhancement', 'object_detection', 'feature_extraction', 'format_conversion']
            )
            
            self._register_processor(
                "text",
                TextProcessor,
                "content_analysis",
                "NLP and content analysis for creators",
                ['.txt', '.md', '.pdf', '.doc', '.docx', '.rtf', '.html', '.xml'],
                ['sentiment_analysis', 'keyword_extraction', 'language_detection', 'quality_assessment']
            )
            
            self._register_processor(
                "metadata",
                MetadataProcessor,
                "content_management",
                "Universal metadata extraction and enhancement",
                ['*'],  # Supports all formats
                ['extraction', 'validation', 'enrichment', 'standardization']
            )
            
            self._register_processor(
                "quality",
                QualityProcessor,
                "optimization",
                "Content quality assessment and optimization",
                ['*'],  # Supports all formats
                ['quality_scoring', 'benchmark_analysis', 'optimization_recommendations']
            )
            
            self._register_processor(
                "format",
                FormatProcessor,
                "conversion",
                "Universal format conversion and standardization",
                ['*'],  # Supports all formats
                ['format_conversion', 'platform_optimization', 'batch_processing']
            )
            
            self._register_processor(
                "compression",
                CompressionProcessor,
                "optimization",
                "Intelligent content compression and optimization",
                ['*'],  # Supports all formats
                ['compression', 'optimization', 'quality_preservation', 'adaptive_algorithms']
            )
            
            self._register_processor(
                "orchestration",
                OrchestrationProcessor,
                "workflow",
                "Complex workflow orchestration and management",
                ['*'],  # Supports all content types
                ['workflow_management', 'pipeline_execution', 'resource_allocation', 'error_recovery']
            )
            
            self.logger.info(f"Processor registry initialized with {len(self._processors)} processors")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize processor registry: {str(e)}")
            raise
    
    def _register_processor(
        self,
        name: str,
        processor_class: Type,
        category: str,
        description: str,
        supported_formats: List[str],
        capabilities: List[str],
        version: str = "1.0.0"
    ):
        """Register a processor in the index"""        processor_info = ProcessorInfo(
            name=name,
            class_type=processor_class,
            category=category,
            description=description,
            supported_formats=supported_formats,
            processing_capabilities=capabilities,
            version=version
        )
        
        self._processors[name] = processor_info
        self._metrics[name] = ProcessorMetrics(processor_name=name)
    
    def get_processor_info(self, processor_name: str) -> Optional[ProcessorInfo]:
        """Get information about a specific processor"""        return self._processors.get(processor_name)
    
    def list_processors(self, category: Optional[str] = None) -> List[ProcessorInfo]:
        """List all processors, optionally filtered by category"""        processors = list(self._processors.values())
        
        if category:
            processors = [p for p in processors if p.category == category]
        
        return processors
    
    def list_categories(self) -> List[str]:
        """List all processor categories"""        categories = set(p.category for p in self._processors.values())
        return sorted(list(categories))
    
    def get_processor_instance(self, processor_name: str, config: Optional[Dict[str, Any]] = None):
        """Get or create a processor instance"""        try:
            # Check if instance already exists
            if processor_name in self._instances:
                return self._instances[processor_name]
            
            # Get processor info
            processor_info = self._processors.get(processor_name)
            if not processor_info:
                raise ValueError(f"Processor '{processor_name}' not found in registry")
            
            if not processor_info.is_active:
                raise ValueError(f"Processor '{processor_name}' is not active")
            
            # Create new instance
            processor_instance = processor_info.class_type(config)
            self._instances[processor_name] = processor_instance
            
            self.logger.info(f"Created new instance for processor: {processor_name}")
            return processor_instance
            
        except Exception as e:
            self.logger.error(f"Failed to get processor instance '{processor_name}': {str(e)}")
            raise
    
    def find_processors_for_format(self, file_format: str) -> List[str]:
        """Find all processors that support a specific file format"""        compatible_processors = []
        
        for name, info in self._processors.items():
            if '*' in info.supported_formats or file_format in info.supported_formats:
                compatible_processors.append(name)
        
        return compatible_processors
    
    def find_processors_by_capability(self, capability: str) -> List[str]:
        """Find all processors that have a specific capability"""        capable_processors = []
        
        for name, info in self._processors.items():
            if capability in info.processing_capabilities:
                capable_processors.append(name)
        
        return capable_processors
    
    async def process_with_metrics(
        self,
        processor_name: str,
        content_data: Any,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process content while tracking metrics"""        try:
            start_time = time.time()
            
            # Get processor instance
            processor = self.get_processor_instance(processor_name, config)
            
            # Process content
            result = await processor.process(content_data, config)
            
            # Update metrics
            processing_time = time.time() - start_time
            await self._update_metrics(processor_name, True, processing_time)
            
            return {
                'success': True,
                'result': result,
                'processing_time': processing_time,
                'processor': processor_name
            }
            
        except Exception as e:
            # Update metrics for failure
            processing_time = time.time() - start_time
            await self._update_metrics(processor_name, False, processing_time)
            
            self.logger.error(f"Processing failed for '{processor_name}': {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'processing_time': processing_time,
                'processor': processor_name
            }
    
    async def _update_metrics(self, processor_name: str, success: bool, processing_time: float):
        """Update processing metrics for a processor"""        try:
            metrics = self._metrics.get(processor_name)
            if not metrics:
                return
            
            metrics.total_processed += 1
            metrics.total_processing_time += processing_time
            metrics.last_used = time.time()
            
            if success:
                metrics.successful_processed += 1
            else:
                metrics.failed_processed += 1
            
            # Calculate averages
            if metrics.total_processed > 0:
                metrics.average_processing_time = metrics.total_processing_time / metrics.total_processed
                metrics.error_rate = metrics.failed_processed / metrics.total_processed
            
        except Exception as e:
            self.logger.error(f"Failed to update metrics for '{processor_name}': {str(e)}")
    
    def get_processor_metrics(self, processor_name: str) -> Optional[ProcessorMetrics]:
        """Get performance metrics for a specific processor"""        return self._metrics.get(processor_name)
    
    def get_all_metrics(self) -> Dict[str, ProcessorMetrics]:
        """Get performance metrics for all processors"""        return self._metrics.copy()
    
    def reset_metrics(self, processor_name: Optional[str] = None):
        """Reset metrics for a specific processor or all processors"""        if processor_name:
            if processor_name in self._metrics:
                self._metrics[processor_name] = ProcessorMetrics(processor_name=processor_name)
        else:
            for name in self._metrics:
                self._metrics[name] = ProcessorMetrics(processor_name=name)
    
    def deactivate_processor(self, processor_name: str):
        """Deactivate a processor"""        if processor_name in self._processors:
            self._processors[processor_name].is_active = False
            # Remove instance if exists
            if processor_name in self._instances:
                del self._instances[processor_name]
            self.logger.info(f"Deactivated processor: {processor_name}")
    
    def activate_processor(self, processor_name: str):
        """Activate a processor"""        if processor_name in self._processors:
            self._processors[processor_name].is_active = True
            self.logger.info(f"Activated processor: {processor_name}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status and health"""        try:
            active_processors = sum(1 for p in self._processors.values() if p.is_active)
            total_processors = len(self._processors)
            
            total_processed = sum(m.total_processed for m in self._metrics.values())
            total_successful = sum(m.successful_processed for m in self._metrics.values())
            total_failed = sum(m.failed_processed for m in self._metrics.values())
            
            overall_error_rate = total_failed / total_processed if total_processed > 0 else 0.0
            
            return {
                'status': 'healthy' if overall_error_rate < 0.05 else 'warning' if overall_error_rate < 0.1 else 'critical',
                'active_processors': active_processors,
                'total_processors': total_processors,
                'total_processed': total_processed,
                'total_successful': total_successful,
                'total_failed': total_failed,
                'overall_error_rate': overall_error_rate,
                'categories': self.list_categories(),
                'last_updated': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'last_updated': time.time()
            }

# Global processor index instance
processor_index = ProcessorIndex()

# Convenience functions for easy access
def get_processor(processor_name: str, config: Optional[Dict[str, Any]] = None):
    """Get a processor instance"""    return processor_index.get_processor_instance(processor_name, config)

def list_all_processors(category: Optional[str] = None) -> List[ProcessorInfo]:
    """List all available processors"""    return processor_index.list_processors(category)

def find_processors_for_format(file_format: str) -> List[str]:
    """Find processors compatible with a file format"""    return processor_index.find_processors_for_format(file_format)

async def process_content_with_metrics(
    processor_name: str,
    content_data: Any,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process content with automatic metrics tracking"""    return await processor_index.process_with_metrics(processor_name, content_data, config)

def get_system_status() -> Dict[str, Any]:
    """Get overall system health status"""    return processor_index.get_system_status()

# Export main components
__all__ = [
    'ProcessorIndex',
    'ProcessorInfo',
    'ProcessorMetrics',
    'processor_index',
    'get_processor',
    'list_all_processors',
    'find_processors_for_format',
    'process_content_with_metrics',
    'get_system_status'
]
