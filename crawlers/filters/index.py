"""
IA Influencer Agent - Filters Module Index
==========================================

Professional module indexing and discovery system for content filters.
Provides centralized access to all filtering capabilities and components.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ STRICT COPYRIGHT PROTECTION ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.

Technical Team Expertise:
- Lead IA Developer: Advanced AI/ML algorithms and neural networks
- Backend Senior: Enterprise architecture and microservices
- ML Engineer: Machine learning pipelines and model optimization
- Database Administrator: Data architecture and optimization
- Security Specialist: Cybersecurity and data protection
- Microservices Architect: Distributed systems and scalability
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: Infrastructure automation and deployment
- IA Prompt Engineer: Prompt optimization and AI interaction

Project Owner: Fahed Mlaiel - mlaiel@live.de
"""

import asyncio
import logging
import inspect
from typing import Dict, List, Optional, Type, Any, Callable
from dataclasses import dataclass
from enum import Enum
import importlib
import sys
from pathlib import Path

from .filter_engine import ContentFilterEngine, FilterResponse, FilterType, ContentItem
from .config import FilterConfigManager


class FilterCategory(Enum):
    """Filter categories for organization."""
    CONTENT_ANALYSIS = "content_analysis"
    QUALITY_ASSURANCE = "quality_assurance"
    SECURITY_VALIDATION = "security_validation"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    MONETIZATION_ANALYSIS = "monetization_analysis"
    COLLABORATION_MATCHING = "collaboration_matching"
    MEDIA_PROCESSING = "media_processing"
    METADATA_EXTRACTION = "metadata_extraction"


class FilterCapability(Enum):
    """Filter capabilities for matching."""
    AUDIO_PROCESSING = "audio_processing"
    VIDEO_PROCESSING = "video_processing"
    IMAGE_PROCESSING = "image_processing"
    TEXT_PROCESSING = "text_processing"
    REAL_TIME_ANALYSIS = "real_time_analysis"
    BATCH_PROCESSING = "batch_processing"
    ML_CLASSIFICATION = "ml_classification"
    FINGERPRINTING = "fingerprinting"
    THREAT_DETECTION = "threat_detection"
    QUALITY_SCORING = "quality_scoring"
    MARKET_ANALYSIS = "market_analysis"
    COLLABORATION_MATCHING = "collaboration_matching"


@dataclass
class FilterModuleInfo:
    """Information about a filter module."""
    name: str
    class_type: Type
    category: FilterCategory
    capabilities: List[FilterCapability]
    description: str
    version: str
    author: str
    dependencies: List[str]
    performance_rating: float
    reliability_score: float
    supported_formats: List[str]
    enterprise_ready: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "class_name": self.class_type.__name__,
            "category": self.category.value,
            "capabilities": [cap.value for cap in self.capabilities],
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "dependencies": self.dependencies,
            "performance_rating": self.performance_rating,
            "reliability_score": self.reliability_score,
            "supported_formats": self.supported_formats,
            "enterprise_ready": self.enterprise_ready
        }


class FilterModuleRegistry:
    """Registry for all available filter modules."""
    
    def __init__(self):
        """Initialize the filter module registry."""
        self.logger = logging.getLogger(__name__)
        self._modules: Dict[str, FilterModuleInfo] = {}
        self._categories: Dict[FilterCategory, List[str]] = {}
        self._capabilities: Dict[FilterCapability, List[str]] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the registry with all available modules."""
        try:
            if self._initialized:
                return
            
            await self._register_core_modules()
            await self._register_specialized_modules()
            await self._register_advanced_modules()
            await self._build_indexes()
            
            self._initialized = True
            self.logger.info(f"Filter registry initialized with {len(self._modules)} modules")
            
        except Exception as e:
            self.logger.error(f"Registry initialization failed: {str(e)}")
            raise
    
    async def _register_core_modules(self) -> None:
        """Register core filter modules."""
        try:
            # Core engine
            from .filter_engine import ContentFilterEngine
            await self._register_module(
                "content_filter_engine",
                ContentFilterEngine,
                FilterCategory.CONTENT_ANALYSIS,
                [FilterCapability.BATCH_PROCESSING, FilterCapability.ML_CLASSIFICATION],
                "Core content filtering engine with advanced processing capabilities",
                "2.0.0",
                "Fahed Mlaiel",
                [],
                9.5,
                9.8,
                ["audio", "video", "image", "text"],
                True
            )
            
            # Configuration manager
            from .config import FilterConfigManager
            await self._register_module(
                "filter_config_manager",
                FilterConfigManager,
                FilterCategory.CONTENT_ANALYSIS,
                [FilterCapability.BATCH_PROCESSING],
                "Advanced configuration management for filter systems",
                "2.0.0",
                "Fahed Mlaiel",
                [],
                9.0,
                9.9,
                ["json", "yaml", "toml"],
                True
            )
            
        except Exception as e:
            self.logger.error(f"Core module registration failed: {str(e)}")
    
    async def _register_specialized_modules(self) -> None:
        """Register specialized content filter modules."""
        try:
            # Audio filters
            from .audio_filters import AudioContentFilter, AdvancedAudioAnalyzer
            await self._register_module(
                "audio_content_filter",
                AudioContentFilter,
                FilterCategory.MEDIA_PROCESSING,
                [FilterCapability.AUDIO_PROCESSING, FilterCapability.FINGERPRINTING, 
                 FilterCapability.QUALITY_SCORING],
                "Advanced audio content filtering with AI-powered analysis",
                "2.0.0",
                "Fahed Mlaiel",
                ["librosa", "soundfile", "essentia"],
                9.3,
                9.7,
                ["mp3", "wav", "flac", "aac", "ogg"],
                True
            )
            
            await self._register_module(
                "advanced_audio_analyzer",
                AdvancedAudioAnalyzer,
                FilterCategory.CONTENT_ANALYSIS,
                [FilterCapability.AUDIO_PROCESSING, FilterCapability.ML_CLASSIFICATION,
                 FilterCapability.FINGERPRINTING],
                "Advanced audio analysis using machine learning and signal processing",
                "2.0.0",
                "Fahed Mlaiel",
                ["librosa", "soundfile", "essentia", "numpy"],
                9.5,
                9.8,
                ["mp3", "wav", "flac", "aac"],
                True
            )
            
            # Video filters
            from .video_filters import VideoContentFilter
            await self._register_module(
                "video_content_filter",
                VideoContentFilter,
                FilterCategory.MEDIA_PROCESSING,
                [FilterCapability.VIDEO_PROCESSING, FilterCapability.QUALITY_SCORING],
                "Professional video content validation and analysis",
                "2.0.0",
                "Fahed Mlaiel",
                ["opencv-python", "ffmpeg"],
                9.0,
                9.5,
                ["mp4", "avi", "mkv", "mov", "wmv"],
                True
            )
            
            # Image filters
            from .image_filters import ImageContentFilter
            await self._register_module(
                "image_content_filter",
                ImageContentFilter,
                FilterCategory.MEDIA_PROCESSING,
                [FilterCapability.IMAGE_PROCESSING, FilterCapability.ML_CLASSIFICATION],
                "Advanced image processing and quality assessment",
                "2.0.0",
                "Fahed Mlaiel",
                ["pillow", "opencv-python"],
                8.8,
                9.4,
                ["jpg", "jpeg", "png", "gif", "bmp", "webp"],
                True
            )
            
            # Text filters
            from .text_filters import TextContentFilter
            await self._register_module(
                "text_content_filter",
                TextContentFilter,
                FilterCategory.CONTENT_ANALYSIS,
                [FilterCapability.TEXT_PROCESSING, FilterCapability.ML_CLASSIFICATION],
                "NLP-powered text content analysis and optimization",
                "2.0.0",
                "Fahed Mlaiel",
                ["nltk", "spacy"],
                8.9,
                9.3,
                ["txt", "md", "html", "json"],
                True
            )
            
            # Security filters
            from .security_filters import SecurityContentFilter
            await self._register_module(
                "security_content_filter",
                SecurityContentFilter,
                FilterCategory.SECURITY_VALIDATION,
                [FilterCapability.THREAT_DETECTION, FilterCapability.REAL_TIME_ANALYSIS],
                "Advanced security validation and threat detection",
                "2.0.0",
                "Fahed Mlaiel",
                ["cryptography", "hashlib"],
                9.2,
                9.9,
                ["*"],
                True
            )
            
        except Exception as e:
            self.logger.error(f"Specialized module registration failed: {str(e)}")
    
    async def _register_advanced_modules(self) -> None:
        """Register advanced analysis modules."""
        try:
            # Quality assurance
            from .quality_assurance import QualityAssuranceEngine
            await self._register_module(
                "quality_assurance_engine",
                QualityAssuranceEngine,
                FilterCategory.QUALITY_ASSURANCE,
                [FilterCapability.QUALITY_SCORING, FilterCapability.ML_CLASSIFICATION],
                "Comprehensive quality assessment with multi-dimensional scoring",
                "2.0.0",
                "Fahed Mlaiel",
                ["numpy", "statistics"],
                9.6,
                9.8,
                ["audio", "video", "image", "text"],
                True
            )
            
            # Monetization analysis
            from .monetization_filters import MonetizationEngine
            await self._register_module(
                "monetization_engine",
                MonetizationEngine,
                FilterCategory.MONETIZATION_ANALYSIS,
                [FilterCapability.MARKET_ANALYSIS, FilterCapability.ML_CLASSIFICATION],
                "Revenue optimization and platform analysis engine",
                "2.0.0",
                "Fahed Mlaiel",
                ["decimal", "statistics"],
                9.4,
                9.6,
                ["audio", "video", "image", "text"],
                True
            )
            
            # Collaboration matching
            from .collaboration_filters import CollaborationEngine
            await self._register_module(
                "collaboration_engine",
                CollaborationEngine,
                FilterCategory.COLLABORATION_MATCHING,
                [FilterCapability.COLLABORATION_MATCHING, FilterCapability.ML_CLASSIFICATION],
                "Intelligent partner matching for creative collaborations",
                "2.0.0",
                "Fahed Mlaiel",
                ["numpy", "statistics"],
                9.3,
                9.5,
                ["audio", "video", "image", "text"],
                True
            )
            
            # Content analysis orchestrator
            from .content_filters import ContentFilterOrchestrator
            await self._register_module(
                "content_filter_orchestrator",
                ContentFilterOrchestrator,
                FilterCategory.CONTENT_ANALYSIS,
                [FilterCapability.BATCH_PROCESSING, FilterCapability.ML_CLASSIFICATION,
                 FilterCapability.FINGERPRINTING],
                "Orchestrates all content filtering operations",
                "2.0.0",
                "Fahed Mlaiel",
                ["json", "hashlib"],
                9.7,
                9.9,
                ["audio", "video", "image", "text"],
                True
            )
            
        except Exception as e:
            self.logger.error(f"Advanced module registration failed: {str(e)}")
    
    async def _register_module(self, name: str, class_type: Type, category: FilterCategory,
                             capabilities: List[FilterCapability], description: str,
                             version: str, author: str, dependencies: List[str],
                             performance_rating: float, reliability_score: float,
                             supported_formats: List[str], enterprise_ready: bool) -> None:
        """Register a single module."""
        try:
            module_info = FilterModuleInfo(
                name=name,
                class_type=class_type,
                category=category,
                capabilities=capabilities,
                description=description,
                version=version,
                author=author,
                dependencies=dependencies,
                performance_rating=performance_rating,
                reliability_score=reliability_score,
                supported_formats=supported_formats,
                enterprise_ready=enterprise_ready
            )
            
            self._modules[name] = module_info
            self.logger.debug(f"Registered module: {name}")
            
        except Exception as e:
            self.logger.error(f"Module registration failed for {name}: {str(e)}")
    
    async def _build_indexes(self) -> None:
        """Build category and capability indexes."""
        try:
            # Clear existing indexes
            self._categories.clear()
            self._capabilities.clear()
            
            # Build category index
            for category in FilterCategory:
                self._categories[category] = []
            
            # Build capability index
            for capability in FilterCapability:
                self._capabilities[capability] = []
            
            # Populate indexes
            for name, module_info in self._modules.items():
                # Add to category index
                self._categories[module_info.category].append(name)
                
                # Add to capability indexes
                for capability in module_info.capabilities:
                    self._capabilities[capability].append(name)
            
            self.logger.debug("Indexes built successfully")
            
        except Exception as e:
            self.logger.error(f"Index building failed: {str(e)}")
    
    def get_module_info(self, name: str) -> Optional[FilterModuleInfo]:
        """Get information about a specific module."""
        return self._modules.get(name)
    
    def get_modules_by_category(self, category: FilterCategory) -> List[FilterModuleInfo]:
        """Get all modules in a specific category."""
        module_names = self._categories.get(category, [])
        return [self._modules[name] for name in module_names]
    
    def get_modules_by_capability(self, capability: FilterCapability) -> List[FilterModuleInfo]:
        """Get all modules with a specific capability."""
        module_names = self._capabilities.get(capability, [])
        return [self._modules[name] for name in module_names]
    
    def get_modules_by_format(self, file_format: str) -> List[FilterModuleInfo]:
        """Get all modules that support a specific file format."""
        compatible_modules = []
        for module_info in self._modules.values():
            if file_format.lower() in [fmt.lower() for fmt in module_info.supported_formats] or "*" in module_info.supported_formats:
                compatible_modules.append(module_info)
        return compatible_modules
    
    def get_enterprise_modules(self) -> List[FilterModuleInfo]:
        """Get all enterprise-ready modules."""
        return [info for info in self._modules.values() if info.enterprise_ready]
    
    def get_all_modules(self) -> Dict[str, FilterModuleInfo]:
        """Get all registered modules."""
        return self._modules.copy()
    
    def search_modules(self, query: str) -> List[FilterModuleInfo]:
        """Search modules by name or description."""
        query_lower = query.lower()
        results = []
        
        for module_info in self._modules.values():
            if (query_lower in module_info.name.lower() or 
                query_lower in module_info.description.lower()):
                results.append(module_info)
        
        return results
    
    def get_module_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total_modules = len(self._modules)
        enterprise_modules = len(self.get_enterprise_modules())
        
        category_counts = {}
        for category in FilterCategory:
            category_counts[category.value] = len(self._categories.get(category, []))
        
        capability_counts = {}
        for capability in FilterCapability:
            capability_counts[capability.value] = len(self._capabilities.get(capability, []))
        
        avg_performance = sum(info.performance_rating for info in self._modules.values()) / total_modules if total_modules > 0 else 0
        avg_reliability = sum(info.reliability_score for info in self._modules.values()) / total_modules if total_modules > 0 else 0
        
        return {
            "total_modules": total_modules,
            "enterprise_modules": enterprise_modules,
            "category_distribution": category_counts,
            "capability_distribution": capability_counts,
            "average_performance_rating": round(avg_performance, 2),
            "average_reliability_score": round(avg_reliability, 2),
            "supported_formats": self._get_all_supported_formats()
        }
    
    def _get_all_supported_formats(self) -> List[str]:
        """Get all supported file formats."""
        all_formats = set()
        for module_info in self._modules.values():
            for fmt in module_info.supported_formats:
                if fmt != "*":
                    all_formats.add(fmt)
        return sorted(list(all_formats))


class FilterDiscoveryService:
    """Service for discovering and recommending filters."""
    
    def __init__(self, registry: FilterModuleRegistry):
        """Initialize the discovery service."""
        self.registry = registry
        self.logger = logging.getLogger(__name__)
    
    async def recommend_filters_for_content(self, content_item: ContentItem) -> List[FilterModuleInfo]:
        """Recommend appropriate filters for a content item."""
        try:
            recommendations = []
            
            # Determine content format
            content_format = self._extract_format_from_content(content_item)
            if content_format:
                format_modules = self.registry.get_modules_by_format(content_format)
                recommendations.extend(format_modules)
            
            # Add general purpose modules
            general_modules = self.registry.get_modules_by_capability(FilterCapability.ML_CLASSIFICATION)
            recommendations.extend(general_modules)
            
            # Remove duplicates and sort by performance
            unique_recommendations = list({module.name: module for module in recommendations}.values())
            unique_recommendations.sort(key=lambda x: x.performance_rating, reverse=True)
            
            return unique_recommendations[:10]  # Top 10 recommendations
            
        except Exception as e:
            self.logger.error(f"Filter recommendation failed: {str(e)}")
            return []
    
    def _extract_format_from_content(self, content_item: ContentItem) -> Optional[str]:
        """Extract file format from content item."""
        try:
            if content_item.mime_type:
                # Extract format from MIME type
                if content_item.mime_type.startswith("audio/"):
                    return content_item.mime_type.split("/")[1]
                elif content_item.mime_type.startswith("video/"):
                    return content_item.mime_type.split("/")[1]
                elif content_item.mime_type.startswith("image/"):
                    return content_item.mime_type.split("/")[1]
            
            if content_item.filename:
                # Extract from filename
                return Path(content_item.filename).suffix.lstrip('.').lower()
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Format extraction failed: {str(e)}")
            return None
    
    async def suggest_processing_pipeline(self, content_item: ContentItem) -> List[str]:
        """Suggest an optimal processing pipeline for content."""
        try:
            pipeline = []
            
            # Start with security validation
            security_modules = self.registry.get_modules_by_category(FilterCategory.SECURITY_VALIDATION)
            if security_modules:
                pipeline.append(security_modules[0].name)
            
            # Add format-specific processing
            content_format = self._extract_format_from_content(content_item)
            if content_format:
                format_modules = self.registry.get_modules_by_format(content_format)
                if format_modules:
                    # Add the highest rated module for this format
                    best_module = max(format_modules, key=lambda x: x.performance_rating)
                    pipeline.append(best_module.name)
            
            # Add quality assurance
            qa_modules = self.registry.get_modules_by_category(FilterCategory.QUALITY_ASSURANCE)
            if qa_modules:
                pipeline.append(qa_modules[0].name)
            
            # Add monetization analysis
            monetization_modules = self.registry.get_modules_by_category(FilterCategory.MONETIZATION_ANALYSIS)
            if monetization_modules:
                pipeline.append(monetization_modules[0].name)
            
            # Add collaboration matching
            collaboration_modules = self.registry.get_modules_by_category(FilterCategory.COLLABORATION_MATCHING)
            if collaboration_modules:
                pipeline.append(collaboration_modules[0].name)
            
            return pipeline
            
        except Exception as e:
            self.logger.error(f"Pipeline suggestion failed: {str(e)}")
            return []


# Global registry instance
_registry = FilterModuleRegistry()
_discovery_service = FilterDiscoveryService(_registry)

async def get_filter_registry() -> FilterModuleRegistry:
    """Get the global filter registry instance."""
    if not _registry._initialized:
        await _registry.initialize()
    return _registry

async def get_discovery_service() -> FilterDiscoveryService:
    """Get the global discovery service instance."""
    if not _registry._initialized:
        await _registry.initialize()
    return _discovery_service

# Convenience functions
async def list_available_filters() -> List[str]:
    """List all available filter names."""
    registry = await get_filter_registry()
    return list(registry.get_all_modules().keys())

async def get_filter_info(filter_name: str) -> Optional[Dict[str, Any]]:
    """Get information about a specific filter."""
    registry = await get_filter_registry()
    module_info = registry.get_module_info(filter_name)
    return module_info.to_dict() if module_info else None

async def recommend_filters(content_item: ContentItem) -> List[Dict[str, Any]]:
    """Recommend filters for a content item."""
    discovery = await get_discovery_service()
    recommendations = await discovery.recommend_filters_for_content(content_item)
    return [module.to_dict() for module in recommendations]

async def get_registry_stats() -> Dict[str, Any]:
    """Get registry statistics."""
    registry = await get_filter_registry()
    return registry.get_module_statistics()

from typing import Dict, Type, Union, List
import logging

# Core components
from .filter_engine import ContentFilterEngine, FilterResponse, FilterResult, FilterType, ContentItem
from .config import FilterConfigManager, filter_config

# Specialized filters
from .audio_filters import AudioContentFilter
from .video_filters import VideoContentFilter  
from .image_filters import ImageContentFilter
from .text_filters import TextContentFilter
from .security_filters import SecurityContentFilter
from .performance_filters import (
    PerformanceContentFilter,
    QualityContentFilter,
    RelevanceContentFilter,
    DuplicateContentFilter
)


class FilterRegistry:
    """Registry for all available content filters."""
    
    def __init__(self):
        """Initialize filter registry."""
        self.logger = logging.getLogger(__name__)
        self._filters: Dict[FilterType, Type] = {
            FilterType.AUDIO: AudioContentFilter,
            FilterType.VIDEO: VideoContentFilter,
            FilterType.IMAGE: ImageContentFilter,
            FilterType.TEXT: TextContentFilter,
            FilterType.SECURITY: SecurityContentFilter,
            FilterType.PERFORMANCE: PerformanceContentFilter,
            FilterType.QUALITY: QualityContentFilter,
            FilterType.RELEVANCE: RelevanceContentFilter,
            FilterType.DUPLICATE: DuplicateContentFilter
        }
    
    def get_filter(self, filter_type: FilterType) -> Type:
        """Get filter class by type."""
        if filter_type not in self._filters:
            raise ValueError(f"Unknown filter type: {filter_type}")
        return self._filters[filter_type]
    
    def get_available_filters(self) -> List[FilterType]:
        """Get list of available filter types."""
        return list(self._filters.keys())
    
    def is_filter_available(self, filter_type: FilterType) -> bool:
        """Check if filter type is available."""
        return filter_type in self._filters


class FilterFactory:
    """Factory for creating filter instances."""
    
    def __init__(self, config_manager: FilterConfigManager = None):
        """Initialize filter factory."""
        self.config = config_manager or filter_config
        self.registry = FilterRegistry()
        self.logger = logging.getLogger(__name__)
    
    def create_filter(self, filter_type: FilterType):
        """Create filter instance by type."""
        filter_class = self.registry.get_filter(filter_type)
        
        # Create filter with appropriate configuration
        if filter_type == FilterType.AUDIO:
            return filter_class(self.config.audio_config)
        elif filter_type == FilterType.VIDEO:
            return filter_class(self.config.video_config)
        elif filter_type == FilterType.IMAGE:
            return filter_class(self.config.image_config)
        elif filter_type == FilterType.TEXT:
            return filter_class(self.config.text_config)
        elif filter_type == FilterType.SECURITY:
            return filter_class(self.config.security_config)
        elif filter_type == FilterType.PERFORMANCE:
            return filter_class(self.config.performance_config)
        else:
            # For filters without specific configuration
            return filter_class()
    
    def create_engine(self) -> ContentFilterEngine:
        """Create complete filtering engine."""
        return ContentFilterEngine(self.config)


# Global instances for convenience
filter_registry = FilterRegistry()
filter_factory = FilterFactory()


def get_filter_engine() -> ContentFilterEngine:
    """Get configured filter engine instance."""
    return filter_factory.create_engine()


def get_available_filter_types() -> List[FilterType]:
    """Get list of all available filter types."""
    return filter_registry.get_available_filters()


def create_filter(filter_type: FilterType, config_manager: FilterConfigManager = None):
    """Create specific filter instance."""
    factory = FilterFactory(config_manager)
    return factory.create_filter(filter_type)


# Export convenience functions
__all__ = [
    # Core classes
    'FilterRegistry',
    'FilterFactory',
    'ContentFilterEngine',
    'FilterResponse',
    'FilterResult',
    'FilterType',
    'ContentItem',
    'FilterConfigManager',
    
    # Filter classes
    'AudioContentFilter',
    'VideoContentFilter',
    'ImageContentFilter',
    'TextContentFilter',
    'SecurityContentFilter',
    'PerformanceContentFilter',
    'QualityContentFilter',
    'RelevanceContentFilter',
    'DuplicateContentFilter',
    
    # Global instances
    'filter_registry',
    'filter_factory',
    'filter_config',
    
    # Convenience functions
    'get_filter_engine',
    'get_available_filter_types',
    'create_filter'
]
