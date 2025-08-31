"""Processors Index Module - IA-Influencer-Agent Platform

Central export module for all content processors in the IA-Influencer-Agent platform.
Provides unified access to all industrial-grade processing capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Any unauthorized use, copying, 
distribution, or commercialization without explicit written permission is 
strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
================================================================================
"""
import logging
from typing import Dict, Any, Optional, Type, Union

# Import all processor classes
from .audio_processor import AudioProcessor, create_audio_processor
from .video_processor import VideoProcessor, create_video_processor
from .image_processor import ImageProcessor, create_image_processor
from .text_processor import TextProcessor, create_text_processor
from .document_processor import DocumentProcessor, create_document_processor
from .multimedia_processor import MultimediaProcessor, create_multimedia_processor
from .content_processor import ContentProcessor, create_content_processor
from .batch_processor import BatchProcessor, create_batch_processor
from .realtime_processor import RealtimeProcessor, create_realtime_processor
from .quality_processor import QualityProcessor, create_quality_processor
from .metadata_processor import MetadataProcessor, create_metadata_processor
from .format_processor import FormatProcessor, create_format_processor
from .protection_processor import ProtectionProcessor, create_protection_processor
from .monetization_processor import MonetizationProcessor, create_monetization_processor
from .crawler_processor import CrawlerProcessor, create_crawler_processor
from .workflow_processor import WorkflowProcessor, create_workflow_processor

# Import processor registry
from . import ProcessorRegistry

logger = logging.getLogger(__name__)

# Processor factory mapping
PROCESSOR_FACTORIES = {
    "audio": create_audio_processor,
    "video": create_video_processor,
    "image": create_image_processor,
    "text": create_text_processor,
    "document": create_document_processor,
    "multimedia": create_multimedia_processor,
    "content": create_content_processor,
    "batch": create_batch_processor,
    "realtime": create_realtime_processor,
    "quality": create_quality_processor,
    "metadata": create_metadata_processor,
    "format": create_format_processor,
    "protection": create_protection_processor,
    "monetization": create_monetization_processor,
    "crawler": create_crawler_processor,
    "workflow": create_workflow_processor,
}

# Processor class mapping
PROCESSOR_CLASSES = {
    "audio": AudioProcessor,
    "video": VideoProcessor,
    "image": ImageProcessor,
    "text": TextProcessor,
    "document": DocumentProcessor,
    "multimedia": MultimediaProcessor,
    "content": ContentProcessor,
    "batch": BatchProcessor,
    "realtime": RealtimeProcessor,
    "quality": QualityProcessor,
    "metadata": MetadataProcessor,
    "format": FormatProcessor,
    "protection": ProtectionProcessor,
    "monetization": MonetizationProcessor,
    "crawler": CrawlerProcessor,
    "workflow": WorkflowProcessor,
}


class ProcessorManager:
    """
    🏭 ENTERPRISE PROCESSOR MANAGER
    
    Central management system for all content processors with unified
    initialization, health monitoring, and resource management.
    """
    
    def __init__(self, db_session, redis_client):
        self.db_session = db_session
        self.redis_client = redis_client
        self.logger = logging.getLogger(f"{__name__}.ProcessorManager")
        
        # Active processor instances
        self._processors: Dict[str, Any] = {}
        self._processor_configs: Dict[str, Dict[str, Any]] = {}
        
        # Manager state
        self._initialized = False
        self._registry = ProcessorRegistry()
    
    async def initialize_processor(
        self,
        processor_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initialize a specific processor
        
        Args:
            processor_type: Type of processor to initialize
            config: Processor configuration
            
        Returns:
            Initialization result
        """
        try:
            if processor_type not in PROCESSOR_FACTORIES:
                return {
                    "success": False,
                    "error_message": f"Processor type '{processor_type}' not supported"
                }
            
            if processor_type in self._processors:
                return {
                    "success": True,
                    "message": f"Processor '{processor_type}' already initialized",
                    "processor": self._processors[processor_type]
                }
            
            # Create processor using factory function
            factory_func = PROCESSOR_FACTORIES[processor_type]
            processor = await factory_func(
                db_session=self.db_session,
                redis_client=self.redis_client,
                config=config
            )
            
            # Store processor and config
            self._processors[processor_type] = processor
            self._processor_configs[processor_type] = config or {}
            
            # Register with registry
            self._registry.register_processor(processor_type, processor)
            
            self.logger.info(f"✅ Processor '{processor_type}' initialized successfully")
            
            return {
                "success": True,
                "processor_type": processor_type,
                "processor": processor,
                "message": f"Processor '{processor_type}' initialized successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize processor '{processor_type}': {e}")
            return {
                "success": False,
                "processor_type": processor_type,
                "error_message": str(e)
            }
    
    async def initialize_all_processors(
        self,
        global_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initialize all available processors
        
        Args:
            global_config: Global configuration for all processors
            
        Returns:
            Initialization results for all processors
        """
        try:
            results = {}
            successful_inits = 0
            failed_inits = 0
            
            for processor_type in PROCESSOR_FACTORIES.keys():
                try:
                    # Get processor-specific config from global config
                    processor_config = None
                    if global_config:
                        processor_config = global_config.get(f"{processor_type}_config")
                    
                    result = await self.initialize_processor(processor_type, processor_config)
                    results[processor_type] = result
                    
                    if result["success"]:
                        successful_inits += 1
                    else:
                        failed_inits += 1
                        
                except Exception as e:
                    results[processor_type] = {
                        "success": False,
                        "error_message": str(e)
                    }
                    failed_inits += 1
            
            self._initialized = True
            
            return {
                "success": True,
                "total_processors": len(PROCESSOR_FACTORIES),
                "successful_initializations": successful_inits,
                "failed_initializations": failed_inits,
                "results": results
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initialize all processors: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    def get_processor(self, processor_type: str) -> Optional[Any]:
        """
        Get a processor instance
        
        Args:
            processor_type: Type of processor to retrieve
            
        Returns:
            Processor instance or None
        """
        return self._processors.get(processor_type)
    
    def get_all_processors(self) -> Dict[str, Any]:
        """
        Get all processor instances
        
        Returns:
            Dictionary of all processor instances
        """
        return self._processors.copy()
    
    async def health_check_all(self) -> Dict[str, Any]:
        """
        Perform health check on all processors
        
        Returns:
            Health check results for all processors
        """
        try:
            health_results = {}
            healthy_count = 0
            unhealthy_count = 0
            
            for processor_type, processor in self._processors.items():
                try:
                    if hasattr(processor, 'health_check'):
                        health_result = await processor.health_check()
                        health_results[processor_type] = health_result
                        
                        if health_result.get("status") == "healthy":
                            healthy_count += 1
                        else:
                            unhealthy_count += 1
                    else:
                        health_results[processor_type] = {
                            "status": "unknown",
                            "message": "Health check not available"
                        }
                        unhealthy_count += 1
                        
                except Exception as e:
                    health_results[processor_type] = {
                        "status": "error",
                        "error_message": str(e)
                    }
                    unhealthy_count += 1
            
            return {
                "success": True,
                "overall_status": "healthy" if unhealthy_count == 0 else "degraded",
                "total_processors": len(self._processors),
                "healthy_processors": healthy_count,
                "unhealthy_processors": unhealthy_count,
                "processor_health": health_results
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def shutdown_all(self) -> Dict[str, Any]:
        """
        Shutdown all processors gracefully
        
        Returns:
            Shutdown results
        """
        try:
            shutdown_results = {}
            successful_shutdowns = 0
            failed_shutdowns = 0
            
            for processor_type, processor in self._processors.items():
                try:
                    if hasattr(processor, 'shutdown'):
                        await processor.shutdown()
                        shutdown_results[processor_type] = {
                            "success": True,
                            "message": "Shutdown completed"
                        }
                        successful_shutdowns += 1
                    else:
                        shutdown_results[processor_type] = {
                            "success": True,
                            "message": "No shutdown method available"
                        }
                        successful_shutdowns += 1
                        
                except Exception as e:
                    shutdown_results[processor_type] = {
                        "success": False,
                        "error_message": str(e)
                    }
                    failed_shutdowns += 1
            
            # Clear processor instances
            self._processors.clear()
            self._processor_configs.clear()
            self._initialized = False
            
            return {
                "success": True,
                "total_processors": successful_shutdowns + failed_shutdowns,
                "successful_shutdowns": successful_shutdowns,
                "failed_shutdowns": failed_shutdowns,
                "shutdown_results": shutdown_results
            }
            
        except Exception as e:
            self.logger.error(f"Shutdown failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    def get_processor_info(self) -> Dict[str, Any]:
        """
        Get information about available processors
        
        Returns:
            Processor information
        """
        return {
            "available_processors": list(PROCESSOR_FACTORIES.keys()),
            "initialized_processors": list(self._processors.keys()),
            "processor_classes": {
                name: cls.__name__ for name, cls in PROCESSOR_CLASSES.items()
            },
            "manager_initialized": self._initialized,
            "total_available": len(PROCESSOR_FACTORIES),
            "total_initialized": len(self._processors)
        }


# Convenience functions for easy access
async def create_processor_manager(
    db_session,
    redis_client,
    auto_initialize: bool = False,
    global_config: Optional[Dict[str, Any]] = None
) -> ProcessorManager:
    """
    Create and optionally initialize a processor manager
    
    Args:
        db_session: Database session
        redis_client: Redis client
        auto_initialize: Whether to automatically initialize all processors
        global_config: Global configuration for processors
        
    Returns:
        ProcessorManager instance
    """
    manager = ProcessorManager(db_session, redis_client)
    
    if auto_initialize:
        await manager.initialize_all_processors(global_config)
    
    return manager


async def get_processor_by_type(
    processor_type: str,
    db_session,
    redis_client,
    config: Optional[Dict[str, Any]] = None
) -> Optional[Any]:
    """
    Get a specific processor instance
    
    Args:
        processor_type: Type of processor
        db_session: Database session
        redis_client: Redis client
        config: Processor configuration
        
    Returns:
        Processor instance
    """
    if processor_type not in PROCESSOR_FACTORIES:
        return None
    
    factory_func = PROCESSOR_FACTORIES[processor_type]
    return await factory_func(db_session, redis_client, config)


# Export all processor classes and functions
__all__ = [
    # Processor classes
    "AudioProcessor",
    "VideoProcessor", 
    "ImageProcessor",
    "TextProcessor",
    "DocumentProcessor",
    "MultimediaProcessor",
    "ContentProcessor",
    "BatchProcessor",
    "RealtimeProcessor",
    "QualityProcessor",
    "MetadataProcessor",
    "FormatProcessor",
    "ProtectionProcessor",
    "MonetizationProcessor",
    "CrawlerProcessor",
    "WorkflowProcessor",
    
    # Factory functions
    "create_audio_processor",
    "create_video_processor",
    "create_image_processor", 
    "create_text_processor",
    "create_document_processor",
    "create_multimedia_processor",
    "create_content_processor",
    "create_batch_processor",
    "create_realtime_processor",
    "create_quality_processor",
    "create_metadata_processor",
    "create_format_processor",
    "create_protection_processor",
    "create_monetization_processor",
    "create_crawler_processor",
    "create_workflow_processor",
    
    # Management classes
    "ProcessorManager",
    "ProcessorRegistry",
    
    # Management functions
    "create_processor_manager",
    "get_processor_by_type",
    
    # Constants
    "PROCESSOR_FACTORIES",
    "PROCESSOR_CLASSES",
]


# Module information
MODULE_INFO = {
    "name": "IA-Influencer-Agent Processors",
    "version": "1.0.0",
    "author": "Fahed Mlaiel",
    "description": "Industrial-grade content processing engine for creators and influencers",
    "processors": {
        "audio": "Advanced audio processing with AI-powered analysis and enhancement",
        "video": "Comprehensive video processing with computer vision and transcoding",
        "image": "Professional image processing with AI enhancement and optimization",
        "text": "Advanced NLP processing with sentiment analysis and content optimization",
        "document": "Multi-format document processing with OCR and structure analysis",
        "multimedia": "Cross-modal multimedia analysis and synchronization",
        "content": "Complete content pipeline orchestration and workflow management",
        "batch": "Industrial batch processing with parallel execution and monitoring",
        "realtime": "Ultra-low latency real-time processing for live streams",
        "quality": "Comprehensive quality assessment and automated enhancement",
        "metadata": "Advanced metadata extraction, management, and enrichment",
        "protection": "AI-powered content protection with fingerprinting and surveillance",
        "monetization": "Advanced revenue tracking, payments, and monetization automation",
        "crawler": "Multi-platform content surveillance and automated monitoring",
        "workflow": "Enterprise workflow orchestration and multi-stage pipeline management"
    },
    "capabilities": [
        "Multi-format content processing",
        "AI-powered analysis and enhancement", 
        "Real-time and batch processing",
        "Quality assessment and optimization",
        "Metadata extraction and management",
        "Format conversion and transcoding",
        "Platform-specific optimization",
        "Cross-modal content analysis",
        "Industrial-grade reliability",
        "Comprehensive monitoring and analytics"
    ]
}


def get_module_info() -> Dict[str, Any]:
    """Get module information"""
    return MODULE_INFO.copy()


def list_available_processors() -> List[str]:
    """List all available processor types"""
    return list(PROCESSOR_FACTORIES.keys())


def get_processor_class(processor_type: str) -> Optional[Type]:
    """Get processor class by type"""
    return PROCESSOR_CLASSES.get(processor_type)


def is_processor_available(processor_type: str) -> bool:
    """Check if a processor type is available"""
    return processor_type in PROCESSOR_FACTORIES


# Print module loading confirmation
logger.info("🏭 IA-Influencer-Agent Processors Module Loaded Successfully")
logger.info(f"📊 Available Processors: {', '.join(list_available_processors())}")
logger.info("⚡ Ready for industrial-grade content processing")
