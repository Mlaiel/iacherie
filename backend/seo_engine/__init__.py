"""SEO Engine Module - AI-Powered SEO Intelligence System

Main module exports for the backend SEO engine providing comprehensive
SEO optimization capabilities with AI-driven insights and automation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .keyword_analyzer import (
    KeywordAnalyzer,
    KeywordMetrics,
    KeywordAnalysisResult,
    KeywordDifficulty,
    SearchIntent
)

from .content_optimizer import (
    ContentOptimizer,
    OptimizedContent,
    OptimizationRecommendation,
    ContentType,
    OptimizationLevel
)

from .metadata_generator import (
    MetadataGenerator,
    GeneratedMetadata,
    MetaTags,
    OpenGraphTags,
    TwitterCardTags,
    SchemaMarkup,
    MetadataType,
    SchemaType
)

from .trend_predictor import (
    TrendPredictor,
    TrendAnalysisResult,
    TrendPrediction,
    TrendType,
    TrendStatus,
    TrendImpact
)

from .platform_optimizer import (
    PlatformOptimizer,
    OptimizationResult,
    CrossPlatformStrategy,
    Platform,
    ContentFormat
)

# Module version
__version__ = "1.0.0"

# Module description
__description__ = "AI-Powered SEO Intelligence Engine for comprehensive optimization"

# Export all main classes
__all__ = [
    # Keyword Analysis
    'KeywordAnalyzer',
    'KeywordMetrics',
    'KeywordAnalysisResult',
    'KeywordDifficulty',
    'SearchIntent',
    
    # Content Optimization
    'ContentOptimizer',
    'OptimizedContent',
    'OptimizationRecommendation',
    'ContentType',
    'OptimizationLevel',
    
    # Metadata Generation
    'MetadataGenerator',
    'GeneratedMetadata',
    'MetaTags',
    'OpenGraphTags',
    'TwitterCardTags',
    'SchemaMarkup',
    'MetadataType',
    'SchemaType',
    
    # Trend Prediction
    'TrendPredictor',
    'TrendAnalysisResult',
    'TrendPrediction',
    'TrendType',
    'TrendStatus',
    'TrendImpact',
    
    # Platform Optimization
    'PlatformOptimizer',
    'OptimizationResult',
    'CrossPlatformStrategy',
    'Platform',
    'ContentFormat'
]


class SEOEngine:
    """
    Unified SEO Engine that combines all optimization components
    """
    
    def __init__(self, config=None):
        """Initialize the unified SEO engine"""
        self.config = config or {}
        
        # Initialize all components
        self.keyword_analyzer = KeywordAnalyzer(config)
        self.content_optimizer = ContentOptimizer(config)
        self.metadata_generator = MetadataGenerator(config)
        self.trend_predictor = TrendPredictor(config)
        self.platform_optimizer = PlatformOptimizer(config)
    
    async def comprehensive_seo_analysis(
        self,
        content: str,
        target_keywords: list = None,
        target_platforms: list = None,
        content_type: str = "article"
    ):
        """
        Perform comprehensive SEO analysis using all engine components
        
        Args:
            content: The content to optimize
            target_keywords: List of target keywords
            target_platforms: List of target platforms
            content_type: Type of content being optimized
            
        Returns:
            Complete SEO analysis and recommendations
        """
        results = {}
        
        # Keyword analysis
        if target_keywords:
            results['keyword_analysis'] = await self.keyword_analyzer.analyze_keywords(
                target_keywords, {'type': content_type}
            )
        
        # Content optimization
        results['content_optimization'] = await self.content_optimizer.optimize_content(
            content, target_keywords or [], ContentType(content_type)
        )
        
        # Metadata generation
        results['metadata'] = await self.metadata_generator.generate_metadata(
            content, target_keywords or [], content_type
        )
        
        # Trend analysis
        if target_keywords:
            results['trend_analysis'] = await self.trend_predictor.predict_trends(
                target_keywords, content_type
            )
        
        # Platform optimization
        if target_platforms:
            platform_results = {}
            for platform in target_platforms:
                platform_results[platform.value] = await self.platform_optimizer.optimize_for_platform(
                    content, target_keywords or [], platform
                )
            results['platform_optimization'] = platform_results
        
        return results


# Add SEOEngine to exports
__all__.append('SEOEngine')