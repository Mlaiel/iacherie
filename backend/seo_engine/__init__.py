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

from .creator_seo_intelligence import (
    CreatorSEOIntelligence,
    CreatorProfile,
    CreatorSEOAnalysis,
    CreatorSEOMetrics,
    CreatorType,
    SEOStrategy
)

from .multi_format_content_seo_optimizer import (
    MultiFormatContentSEOOptimizer,
    MultiFormatSEOAnalysis,
    FormatOptimizationStrategy,
    OptimizationRecommendation,
    ContentMetadata,
    SEOObjective
)

from .creator_type_seo_engine import (
    CreatorTypeSEOEngine,
    CreatorSEOProfile,
    CreatorTypeSEOStrategy,
    CreatorSEOAnalysisResult,
    CreatorCareerStage,
    MonetizationModel
)

from .creator_audience_seo_matcher import (
    CreatorAudienceSEOMatcher,
    AudienceSEOMatchResult,
    AudienceProfile,
    SEOMatchingStrategy,
    AudienceSegment,
    ContentAudienceAlignment
)

from .viral_content_seo_predictor import (
    ViralContentSEOPredictor,
    ViralPredictionResult,
    ViralSEOStrategy,
    ViralityPrediction,
    ViralityType,
    ViralContentSignal
)

from .creator_brand_seo_optimizer import (
    CreatorBrandSEOOptimizer,
    BrandSEOOptimizationResult,
    BrandSEOStrategy,
    CreatorBrandProfile,
    BrandSEOObjective,
    BrandingStage
)

from .multi_platform_creator_seo_coordinator import (
    MultiPlatformCreatorSEOCoordinator,
    CoordinationResult,
    CrossPlatformSEOStrategy,
    PlatformSEOConfig,
    SEOCoordinationStrategy,
    Platform
)

from .content_format_seo_analyzer import (
    ContentFormatSEOAnalyzer,
    FormatSEOAnalysisResult,
    ContentFormatProfile,
    FormatOptimizationRecommendation,
    FormatSEOMetrics,
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
    'ContentFormat',
    
    # Creator SEO Intelligence
    'CreatorSEOIntelligence',
    'CreatorProfile',
    'CreatorSEOAnalysis',
    'CreatorSEOMetrics',
    'CreatorType',
    'SEOStrategy',
    
    # Multi-Format Content SEO Optimizer
    'MultiFormatContentSEOOptimizer',
    'MultiFormatSEOAnalysis',
    'FormatOptimizationStrategy',
    'ContentMetadata',
    'SEOObjective',
    
    # Creator Type SEO Engine
    'CreatorTypeSEOEngine',
    'CreatorSEOProfile',
    'CreatorTypeSEOStrategy',
    'CreatorSEOAnalysisResult',
    'CreatorCareerStage',
    'MonetizationModel',
    
    # Creator Audience SEO Matcher
    'CreatorAudienceSEOMatcher',
    'AudienceSEOMatchResult',
    'AudienceProfile',
    'SEOMatchingStrategy',
    'AudienceSegment',
    'ContentAudienceAlignment',
    
    # Viral Content SEO Predictor
    'ViralContentSEOPredictor',
    'ViralPredictionResult',
    'ViralSEOStrategy',
    'ViralityPrediction',
    'ViralityType',
    'ViralContentSignal',
    
    # Creator Brand SEO Optimizer
    'CreatorBrandSEOOptimizer',
    'BrandSEOOptimizationResult',
    'BrandSEOStrategy',
    'CreatorBrandProfile',
    'BrandSEOObjective',
    'BrandingStage',
    
    # Multi-Platform Creator SEO Coordinator
    'MultiPlatformCreatorSEOCoordinator',
    'CoordinationResult',
    'CrossPlatformSEOStrategy',
    'PlatformSEOConfig',
    'SEOCoordinationStrategy',
    'Platform',
    
    # Content Format SEO Analyzer
    'ContentFormatSEOAnalyzer',
    'FormatSEOAnalysisResult',
    'ContentFormatProfile',
    'FormatOptimizationRecommendation',
    'FormatSEOMetrics'
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
        
        # Initialize new creator-specific components
        self.creator_seo_intelligence = CreatorSEOIntelligence(config)
        self.multi_format_optimizer = MultiFormatContentSEOOptimizer(config)
        self.creator_type_engine = CreatorTypeSEOEngine(config)
        self.audience_matcher = CreatorAudienceSEOMatcher(config)
        
        # Initialize Priority 1: Creator SEO Intelligence Core components
        self.viral_content_predictor = ViralContentSEOPredictor(config)
        self.brand_seo_optimizer = CreatorBrandSEOOptimizer(config)
        self.platform_coordinator = MultiPlatformCreatorSEOCoordinator(config)
        self.format_analyzer = ContentFormatSEOAnalyzer(config)
    
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
    
    async def creator_specific_seo_analysis(
        self,
        creator_profile: CreatorProfile,
        content_samples: list = None,
        competitor_analysis: dict = None
    ):
        """
        Perform creator-specific SEO analysis
        
        Args:
            creator_profile: Creator profile information
            content_samples: Sample content for analysis
            competitor_analysis: Competitive landscape data
            
        Returns:
            Creator-specific SEO analysis and recommendations
        """
        return await self.creator_seo_intelligence.analyze_creator_seo_profile(
            creator_profile, content_samples, competitor_analysis
        )
    
    async def multi_format_content_analysis(
        self,
        content_id: str,
        content_formats: list,
        content_metadata: dict,
        seo_objective: SEOObjective = SEOObjective.DISCOVERY
    ):
        """
        Perform multi-format content SEO analysis
        
        Args:
            content_id: Unique content identifier
            content_formats: List of content formats
            content_metadata: Metadata for each format
            seo_objective: Primary SEO objective
            
        Returns:
            Multi-format SEO analysis and optimization plan
        """
        return await self.multi_format_optimizer.analyze_multi_format_content(
            content_id, content_formats, content_metadata, seo_objective
        )
    
    async def creator_type_analysis(
        self,
        creator_profile: CreatorSEOProfile,
        current_performance: dict = None,
        competitive_landscape: list = None
    ):
        """
        Perform creator type-specific SEO analysis
        
        Args:
            creator_profile: Detailed creator profile
            current_performance: Current performance metrics
            competitive_landscape: Competitive analysis data
            
        Returns:
            Creator type-specific SEO strategy and recommendations
        """
        return await self.creator_type_engine.analyze_creator_type_seo(
            creator_profile, current_performance, competitive_landscape
        )
    
    async def audience_matching_analysis(
        self,
        creator_id: str,
        target_audience_segments: list,
        creator_content_analysis: dict,
        current_performance: dict = None
    ):
        """
        Perform audience-SEO matching analysis
        
        Args:
            creator_id: Creator identifier
            target_audience_segments: Target audience segments
            creator_content_analysis: Content analysis data
            current_performance: Current performance metrics
            
        Returns:
            Audience-specific SEO matching strategies
        """
        return await self.audience_matcher.analyze_audience_seo_matching(
            creator_id, target_audience_segments, creator_content_analysis, current_performance
        )
    
    async def viral_content_prediction(
        self,
        content_id: str,
        content_data: dict,
        creator_profile: dict,
        platform_targets: list = None
    ):
        """
        Predict viral potential and generate SEO optimization strategy
        
        Args:
            content_id: Unique content identifier
            content_data: Content analysis data
            creator_profile: Creator profile information
            platform_targets: Target platforms for viral optimization
            
        Returns:
            Viral prediction analysis with SEO optimization strategy
        """
        return await self.viral_content_predictor.predict_viral_potential(
            content_id, content_data, creator_profile, platform_targets
        )
    
    async def brand_seo_optimization(
        self,
        creator_brand_profile: CreatorBrandProfile,
        competitive_analysis: dict = None,
        current_performance: dict = None
    ):
        """
        Optimize creator brand SEO strategy comprehensively
        
        Args:
            creator_brand_profile: Detailed creator brand profile
            competitive_analysis: Competitive landscape analysis
            current_performance: Current brand performance metrics
            
        Returns:
            Comprehensive brand SEO optimization strategy
        """
        return await self.brand_seo_optimizer.optimize_creator_brand_seo(
            creator_brand_profile, competitive_analysis, current_performance
        )
    
    async def multi_platform_coordination(
        self,
        creator_id: str,
        target_platforms: list,
        creator_profile: dict,
        coordination_objectives: list,
        coordination_strategy: SEOCoordinationStrategy = None
    ):
        """
        Coordinate SEO strategy across multiple platforms
        
        Args:
            creator_id: Creator identifier
            target_platforms: List of target platforms
            creator_profile: Creator profile information
            coordination_objectives: SEO coordination objectives
            coordination_strategy: Coordination strategy type
            
        Returns:
            Multi-platform SEO coordination strategy and implementation plan
        """
        return await self.platform_coordinator.coordinate_multi_platform_seo(
            creator_id, target_platforms, creator_profile, coordination_objectives, coordination_strategy
        )
    
    async def content_format_analysis(
        self,
        content_format_profiles: list,
        creator_objectives: list,
        resource_constraints: dict = None,
        competitive_analysis: dict = None
    ):
        """
        Analyze SEO performance and optimization opportunities for content formats
        
        Args:
            content_format_profiles: List of content format profiles
            creator_objectives: Creator's SEO objectives
            resource_constraints: Resource availability constraints
            competitive_analysis: Competitive landscape analysis
            
        Returns:
            Content format SEO analysis and optimization recommendations
        """
        return await self.format_analyzer.analyze_content_format_seo(
            content_format_profiles, creator_objectives, resource_constraints, competitive_analysis
        )


# Add SEOEngine to exports
__all__.append('SEOEngine')