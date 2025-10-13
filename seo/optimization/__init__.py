"""SEO Optimization Module

This module provides comprehensive SEO optimization capabilities including
content optimization, keyword generation, meta-data optimization, AMP pages,
Core Web Vitals optimization, multilingual SEO, and dynamic sitemap generation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Existing SEO optimization components
from .content_seo_optimizer import ContentSEOOptimizer, OptimizationLevel, ContentAnalysis, SEOOptimizationResult
from .platform_seo_adapter import PlatformSEOAdapter, Platform, PlatformSEOConfig, PlatformOptimizationResult
from .keyword_generator_ai import KeywordGeneratorAI, KeywordType, SearchIntent, KeywordResearchResult
from .meta_optimizer import MetaOptimizer, MetaTagType, ContentType, MetaOptimizationResult
from .hashtag_intelligence import HashtagIntelligence, HashtagCategory, HashtagStrategy
from .multilingual_seo import MultilingualSEO, Language, Region, LocalizationLevel, MultilingualSEOResult
from .trending_analyzer import TrendingAnalyzer, TrendType, TimeFrame, TrendAnalysis
from .competitor_intelligence import CompetitorIntelligence, CompetitorType, AnalysisType, CompetitiveIntelligenceResult
from .seo_performance_tracker import SEOPerformanceTracker, MetricType, TimeRange, PerformanceReport

# New automated SEO components  
from .amp_optimizer import AMPOptimizer, AMPComponentType, AMPValidationResult, AMPPageResult
from .core_web_vitals_optimizer import CoreWebVitalsOptimizer, WebVitalMetric, CoreWebVitalsResult
from .sitemap_generator import SitemapGenerator, SitemapType, ChangeFrequency, Priority, SitemapEntry, SitemapResult

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
    
    # New automated SEO classes
    "AMPOptimizer",
    "CoreWebVitalsOptimizer", 
    "SitemapGenerator",
    
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
    
    # New automated SEO enums
    "AMPComponentType",
    "WebVitalMetric",
    "SitemapType",
    "ChangeFrequency",
    "Priority",
    
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
    "PerformanceReport",
    
    # New automated SEO result classes
    "AMPValidationResult",
    "AMPPageResult", 
    "CoreWebVitalsResult",
    "SitemapEntry",
    "SitemapResult"
]
# Additional platform optimizers
from .twitter_seo_engine import TwitterSEOEngine
from .spotify_seo_optimizer import SpotifySEOOptimizer
