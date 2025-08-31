"""SEO Optimization Module

This module provides comprehensive SEO optimization capabilities including
content optimization, keyword generation, meta-data optimization, and more.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .content_seo_optimizer import ContentSEOOptimizer, OptimizationLevel, ContentAnalysis, SEOOptimizationResult
from .platform_seo_adapter import PlatformSEOAdapter, Platform, PlatformSEOConfig, PlatformOptimizationResult
from .keyword_generator_ai import KeywordGeneratorAI, KeywordType, SearchIntent, KeywordResearchResult
from .meta_optimizer import MetaOptimizer, MetaTagType, ContentType, MetaOptimizationResult
from .hashtag_intelligence import HashtagIntelligence, HashtagCategory, HashtagStrategy
from .multilingual_seo import MultilingualSEO, Language, Region, LocalizationLevel, MultilingualSEOResult
from .trending_analyzer import TrendingAnalyzer, TrendType, TimeFrame, TrendAnalysis
from .competitor_intelligence import CompetitorIntelligence, CompetitorType, AnalysisType, CompetitiveIntelligenceResult
from .seo_performance_tracker import SEOPerformanceTracker, MetricType, TimeRange, PerformanceReport

__all__ = [
    # Main classes
    "ContentSEOOptimizer",
    "PlatformSEOAdapter", 
    "KeywordGeneratorAI",
    "MetaOptimizer",
    "HashtagIntelligence",
    "MultilingualSEO",
    "TrendingAnalyzer",
    "CompetitorIntelligence",
    "SEOPerformanceTracker",
    
    # Enums and utility classes
    "OptimizationLevel",
    "Platform",
    "KeywordType",
    "SearchIntent", 
    "MetaTagType",
    "ContentType",
    "HashtagCategory",
    "Language",
    "Region",
    "LocalizationLevel",
    "TrendType",
    "TimeFrame",
    "CompetitorType",
    "AnalysisType",
    "MetricType",
    "TimeRange",
    
    # Result classes
    "ContentAnalysis",
    "SEOOptimizationResult",
    "PlatformSEOConfig",
    "PlatformOptimizationResult",
    "KeywordResearchResult",
    "MetaOptimizationResult",
    "HashtagStrategy",
    "MultilingualSEOResult",
    "TrendAnalysis",
    "CompetitiveIntelligenceResult",
    "PerformanceReport"
]