#!/usr/bin/env python3
"""
IA Influencer Agent - Algorithms Index Module
=============================================

Centralized access point for all algorithm modules and engines.
Provides a unified interface for algorithm discovery, instantiation, and management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, distribution, or modification without explicit 
written permission is strictly prohibited and will result in legal action.

Project Team Specialties:
- Lead AI Developer & ML Engineer: Fahed Mlaiel
- Backend Senior Developer: Fahed Mlaiel  
- Database Administrator: Fahed Mlaiel
- Security Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Processing Specialist: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- AI Prompt Engineer: Fahed Mlaiel
"""

import logging
from typing import Dict, List, Any, Optional, Type, Union
from dataclasses import dataclass
from enum import Enum
import importlib
import inspect

# Import all algorithm modules
from .audio_analysis import AudioAnalysisEngine
from .video_processing import VideoProcessingEngine  
from .image_recognition import ImageRecognitionEngine
from .text_processing import TextProcessingEngine
from .similarity_matching import SimilarityMatchingEngine
from .collaboration_matching import CollaborationMatchingEngine
from .content_distribution import ContentDistributionEngine
from .feature_extraction import FeatureExtractionEngine
from .pattern_recognition import PatternRecognitionEngine
from .quality_assessment import QualityAssessmentEngine
from .rights_protection import RightsProtectionEngine
from .seo_enhancement import SEOEnhancementEngine
from .revenue_calculation import RevenueCalculationEngine
from .ml_optimization import MLOptimizationEngine

logger = logging.getLogger(__name__)


class AlgorithmCategory(Enum):
    """Algorithm categories for better organization."""
    CONTENT_ANALYSIS = "content_analysis"
    MEDIA_PROCESSING = "media_processing"
    BUSINESS_LOGIC = "business_logic"
    PROTECTION = "protection"
    OPTIMIZATION = "optimization"
    COLLABORATION = "collaboration"


@dataclass
class AlgorithmMetadata:
    """Metadata for algorithm engines."""
    name: str
    category: AlgorithmCategory
    description: str
    version: str
    supported_formats: List[str]
    requires_gpu: bool = False
    performance_level: str = "high"
    author: str = "Fahed Mlaiel"


class AlgorithmRegistry:
    """
    Central registry for all algorithm engines.
    Provides discovery, instantiation, and management capabilities.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._engines: Dict[str, Type] = {}
        self._metadata: Dict[str, AlgorithmMetadata] = {}
        self._instances: Dict[str, Any] = {}
        self._initialize_registry()
    
    def _initialize_registry(self) -> None:
        """Initialize the algorithm registry with all available engines."""
        try:
            # Register all algorithm engines
            self._register_engine(
                "audio_analysis", 
                AudioAnalysisEngine,
                AlgorithmMetadata(
                    name="Audio Analysis Engine",
                    category=AlgorithmCategory.CONTENT_ANALYSIS,
                    description="Advanced audio content analysis and feature extraction",
                    version="2.1.0",
                    supported_formats=["mp3", "wav", "flac", "aac", "m4a"],
                    requires_gpu=True,
                    performance_level="ultra_high"
                )
            )
            
            self._register_engine(
                "video_processing",
                VideoProcessingEngine,
                AlgorithmMetadata(
                    name="Video Processing Engine",
                    category=AlgorithmCategory.MEDIA_PROCESSING,
                    description="Comprehensive video analysis and processing",
                    version="2.1.0",
                    supported_formats=["mp4", "avi", "mov", "mkv", "webm"],
                    requires_gpu=True,
                    performance_level="ultra_high"
                )
            )
            
            self._register_engine(
                "image_recognition",
                ImageRecognitionEngine,
                AlgorithmMetadata(
                    name="Image Recognition Engine",
                    category=AlgorithmCategory.CONTENT_ANALYSIS,
                    description="AI-powered image analysis and recognition",
                    version="2.1.0",
                    supported_formats=["jpg", "jpeg", "png", "gif", "bmp", "tiff"],
                    requires_gpu=True,
                    performance_level="ultra_high"
                )
            )
            
            self._register_engine(
                "text_processing",
                TextProcessingEngine,
                AlgorithmMetadata(
                    name="Text Processing Engine",
                    category=AlgorithmCategory.CONTENT_ANALYSIS,
                    description="Natural language processing and analysis",
                    version="2.1.0",
                    supported_formats=["txt", "md", "docx", "pdf"],
                    performance_level="high"
                )
            )
            
            self._register_engine(
                "similarity_matching",
                SimilarityMatchingEngine,
                AlgorithmMetadata(
                    name="Similarity Matching Engine",
                    category=AlgorithmCategory.COLLABORATION,
                    description="Content similarity and matching algorithms",
                    version="2.1.0",
                    supported_formats=["all"],
                    performance_level="high"
                )
            )
            
            self._register_engine(
                "collaboration_matching",
                CollaborationMatchingEngine,
                AlgorithmMetadata(
                    name="Collaboration Matching Engine",
                    category=AlgorithmCategory.COLLABORATION,
                    description="Intelligent creator collaboration matching",
                    version="2.1.0",
                    supported_formats=["profile", "content"],
                    performance_level="high"
                )
            )
            
            self._register_engine(
                "content_distribution",
                ContentDistributionEngine,
                AlgorithmMetadata(
                    name="Content Distribution Engine",
                    category=AlgorithmCategory.BUSINESS_LOGIC,
                    description="Multi-platform content distribution optimization",
                    version="2.1.0",
                    supported_formats=["all"],
                    performance_level="high"
                )
            )
            
            self._register_engine(
                "feature_extraction",
                FeatureExtractionEngine,
                AlgorithmMetadata(
                    name="Feature Extraction Engine",
                    category=AlgorithmCategory.CONTENT_ANALYSIS,
                    description="Advanced feature extraction for all media types",
                    version="2.1.0",
                    supported_formats=["all"],
                    requires_gpu=True,
                    performance_level="ultra_high"
                )
            )
            
            self._register_engine(
                "pattern_recognition",
                PatternRecognitionEngine,
                AlgorithmMetadata(
                    name="Pattern Recognition Engine",
                    category=AlgorithmCategory.CONTENT_ANALYSIS,
                    description="AI pattern recognition and trend analysis",
                    version="2.1.0",
                    supported_formats=["all"],
                    requires_gpu=True,
                    performance_level="ultra_high"
                )
            )
            
            self._register_engine(
                "quality_assessment",
                QualityAssessmentEngine,
                AlgorithmMetadata(
                    name="Quality Assessment Engine",
                    category=AlgorithmCategory.OPTIMIZATION,
                    description="Content quality analysis and scoring",
                    version="2.1.0",
                    supported_formats=["all"],
                    performance_level="high"
                )
            )
            
            self._register_engine(
                "rights_protection",
                RightsProtectionEngine,
                AlgorithmMetadata(
                    name="Rights Protection Engine",
                    category=AlgorithmCategory.PROTECTION,
                    description="Intellectual property protection and anti-piracy",
                    version="2.1.0",
                    supported_formats=["all"],
                    performance_level="ultra_high"
                )
            )
            
            self._register_engine(
                "seo_enhancement",
                SEOEnhancementEngine,
                AlgorithmMetadata(
                    name="SEO Enhancement Engine",
                    category=AlgorithmCategory.OPTIMIZATION,
                    description="SEO optimization and content enhancement",
                    version="2.1.0",
                    supported_formats=["all"],
                    performance_level="high"
                )
            )
            
            self._register_engine(
                "revenue_calculation",
                RevenueCalculationEngine,
                AlgorithmMetadata(
                    name="Revenue Calculation Engine",
                    category=AlgorithmCategory.BUSINESS_LOGIC,
                    description="Revenue and monetization calculations",
                    version="2.1.0",
                    supported_formats=["financial_data"],
                    performance_level="high"
                )
            )
            
            self._register_engine(
                "ml_optimization",
                MLOptimizationEngine,
                AlgorithmMetadata(
                    name="ML Optimization Engine",
                    category=AlgorithmCategory.OPTIMIZATION,
                    description="Machine learning model optimization",
                    version="2.1.0",
                    supported_formats=["models"],
                    requires_gpu=True,
                    performance_level="ultra_high"
                )
            )
            
            self.logger.info(f"✅ Successfully registered {len(self._engines)} algorithm engines")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize algorithm registry: {e}")
            raise
    
    def _register_engine(self, name: str, engine_class: Type, metadata: AlgorithmMetadata) -> None:
        """Register an algorithm engine with metadata."""
        self._engines[name] = engine_class
        self._metadata[name] = metadata
        self.logger.debug(f"Registered engine: {name}")
    
    def get_engine(self, name: str, **kwargs) -> Any:
        """Get an algorithm engine instance."""
        if name not in self._engines:
            raise ValueError(f"Unknown algorithm engine: {name}")
        
        # Return cached instance if available and no new kwargs
        if name in self._instances and not kwargs:
            return self._instances[name]
        
        try:
            engine_class = self._engines[name]
            instance = engine_class(**kwargs)
            
            # Cache instance if no custom kwargs
            if not kwargs:
                self._instances[name] = instance
            
            self.logger.info(f"✅ Created engine instance: {name}")
            return instance
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create engine {name}: {e}")
            raise
    
    def get_engines_by_category(self, category: AlgorithmCategory) -> List[str]:
        """Get all engine names in a specific category."""
        return [
            name for name, metadata in self._metadata.items()
            if metadata.category == category
        ]
    
    def get_engines_by_format(self, file_format: str) -> List[str]:
        """Get all engines that support a specific file format."""
        compatible_engines = []
        for name, metadata in self._metadata.items():
            if "all" in metadata.supported_formats or file_format.lower() in metadata.supported_formats:
                compatible_engines.append(name)
        return compatible_engines
    
    def get_gpu_engines(self) -> List[str]:
        """Get all engines that require GPU."""
        return [
            name for name, metadata in self._metadata.items()
            if metadata.requires_gpu
        ]
    
    def get_engine_metadata(self, name: str) -> Optional[AlgorithmMetadata]:
        """Get metadata for a specific engine."""
        return self._metadata.get(name)
    
    def list_engines(self) -> List[str]:
        """List all available engine names."""
        return list(self._engines.keys())
    
    def get_registry_info(self) -> Dict[str, Any]:
        """Get comprehensive registry information."""
        return {
            "total_engines": len(self._engines),
            "categories": {
                category.value: len(self.get_engines_by_category(category))
                for category in AlgorithmCategory
            },
            "gpu_engines": len(self.get_gpu_engines()),
            "cached_instances": len(self._instances),
            "supported_formats": list(set(
                fmt for metadata in self._metadata.values()
                for fmt in metadata.supported_formats
            )),
            "version": "2.1.0",
            "author": "Fahed Mlaiel"
        }


# Global registry instance
_registry = AlgorithmRegistry()


def get_algorithm_engine(name: str, **kwargs) -> Any:
    """
    Get an algorithm engine instance.
    
    Args:
        name: Engine name
        **kwargs: Engine initialization parameters
        
    Returns:
        Algorithm engine instance
        
    Example:
        >>> audio_engine = get_algorithm_engine("audio_analysis")
        >>> result = audio_engine.analyze_audio("path/to/file.mp3")
    """
    return _registry.get_engine(name, **kwargs)


def list_available_algorithms() -> List[str]:
    """List all available algorithm engine names."""
    return _registry.list_engines()


def get_algorithms_by_category(category: Union[str, AlgorithmCategory]) -> List[str]:
    """Get algorithms by category."""
    if isinstance(category, str):
        category = AlgorithmCategory(category)
    return _registry.get_engines_by_category(category)


def get_algorithms_for_format(file_format: str) -> List[str]:
    """Get compatible algorithms for a file format."""
    return _registry.get_engines_by_format(file_format)


def get_algorithm_metadata(name: str) -> Optional[AlgorithmMetadata]:
    """Get metadata for an algorithm."""
    return _registry.get_engine_metadata(name)


def get_registry_statistics() -> Dict[str, Any]:
    """Get algorithm registry statistics."""
    return _registry.get_registry_info()


class AlgorithmPipeline:
    """
    Pipeline for chaining multiple algorithm engines.
    Enables complex processing workflows.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.steps: List[Dict[str, Any]] = []
    
    def add_step(self, engine_name: str, method: str, **kwargs) -> 'AlgorithmPipeline':
        """Add a processing step to the pipeline."""
        self.steps.append({
            "engine": engine_name,
            "method": method,
            "kwargs": kwargs
        })
        return self
    
    def execute(self, input_data: Any) -> Any:
        """Execute the pipeline on input data."""
        result = input_data
        
        for i, step in enumerate(self.steps):
            try:
                engine = get_algorithm_engine(step["engine"])
                method = getattr(engine, step["method"])
                result = method(result, **step["kwargs"])
                
                self.logger.debug(f"Pipeline step {i+1}/{len(self.steps)} completed")
                
            except Exception as e:
                self.logger.error(f"Pipeline step {i+1} failed: {e}")
                raise
        
        self.logger.info(f"✅ Pipeline completed with {len(self.steps)} steps")
        return result
    
    def clear(self) -> None:
        """Clear all pipeline steps."""
        self.steps.clear()


def create_content_analysis_pipeline() -> AlgorithmPipeline:
    """Create a standard content analysis pipeline."""
    pipeline = AlgorithmPipeline()
    return (pipeline
            .add_step("feature_extraction", "extract_features")
            .add_step("quality_assessment", "assess_quality")
            .add_step("pattern_recognition", "recognize_patterns")
            .add_step("rights_protection", "protect_content"))


def create_monetization_pipeline() -> AlgorithmPipeline:
    """Create a standard monetization pipeline."""
    pipeline = AlgorithmPipeline()
    return (pipeline
            .add_step("seo_enhancement", "enhance_seo")
            .add_step("content_distribution", "optimize_distribution")
            .add_step("revenue_calculation", "calculate_revenue"))


def create_collaboration_pipeline() -> AlgorithmPipeline:
    """Create a standard collaboration pipeline."""
    pipeline = AlgorithmPipeline()
    return (pipeline
            .add_step("similarity_matching", "find_similar_content")
            .add_step("collaboration_matching", "match_creators")
            .add_step("quality_assessment", "assess_collaboration_potential"))


# Algorithm shortcuts for common use cases
class AlgorithmShortcuts:
    """Convenient shortcuts for common algorithm operations."""
    
    @staticmethod
    def analyze_audio_file(file_path: str) -> Dict[str, Any]:
        """Quick audio analysis."""
        engine = get_algorithm_engine("audio_analysis")
        return engine.analyze_audio(file_path)
    
    @staticmethod
    def process_video_file(file_path: str) -> Dict[str, Any]:
        """Quick video processing."""
        engine = get_algorithm_engine("video_processing")
        return engine.process_video(file_path)
    
    @staticmethod
    def recognize_image(file_path: str) -> Dict[str, Any]:
        """Quick image recognition."""
        engine = get_algorithm_engine("image_recognition")
        return engine.recognize_objects(file_path)
    
    @staticmethod
    def protect_content(content_data: Any) -> Dict[str, Any]:
        """Quick content protection."""
        engine = get_algorithm_engine("rights_protection")
        return engine.protect_content(content_data)
    
    @staticmethod
    def optimize_seo(content: str, metadata: Dict) -> Dict[str, Any]:
        """Quick SEO optimization."""
        engine = get_algorithm_engine("seo_enhancement")
        return engine.optimize_content(content, metadata)
    
    @staticmethod
    def find_collaborators(creator_profile: Dict) -> List[Dict]:
        """Quick collaboration matching."""
        engine = get_algorithm_engine("collaboration_matching")
        return engine.find_matches(creator_profile)


# Export shortcuts
shortcuts = AlgorithmShortcuts()

# Export main classes and functions
__all__ = [
    # Core classes
    'AlgorithmRegistry',
    'AlgorithmCategory', 
    'AlgorithmMetadata',
    'AlgorithmPipeline',
    'AlgorithmShortcuts',
    
    # Main functions
    'get_algorithm_engine',
    'list_available_algorithms',
    'get_algorithms_by_category',
    'get_algorithms_for_format',
    'get_algorithm_metadata',
    'get_registry_statistics',
    
    # Pipeline creators
    'create_content_analysis_pipeline',
    'create_monetization_pipeline',
    'create_collaboration_pipeline',
    
    # Shortcuts
    'shortcuts',
    
    # Global registry
    '_registry'
]


if __name__ == "__main__":
    # Demo usage
    print("🚀 IA Influencer Agent - Algorithm Index")
    print("=" * 50)
    
    stats = get_registry_statistics()
    print(f"📊 Total Engines: {stats['total_engines']}")
    print(f"🎯 Version: {stats['version']}")
    print(f"👨‍💻 Author: {stats['author']}")
    
    print("\n📂 Categories:")
    for category, count in stats['categories'].items():
        print(f"  - {category}: {count} engines")
    
    print(f"\n🖥️  GPU Engines: {stats['gpu_engines']}")
    print(f"📁 Supported Formats: {len(stats['supported_formats'])}")
    
    print("\n🚀 Available Engines:")
    for engine in list_available_algorithms():
        metadata = get_algorithm_metadata(engine)
        print(f"  - {metadata.name} ({metadata.performance_level})")
