"""
SEO Optimization Module - Ultra-Advanced Edition

This module provides comprehensive SEO optimization capabilities including
content optimization, keyword generation, meta-data optimization, and
ultra-advanced features like API integrations, real-time trending analysis,
and automated SEO management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Core SEO optimization modules
from .content_seo_optimizer import ContentSEOOptimizer, OptimizationLevel, ContentAnalysis, SEOOptimizationResult
from .platform_seo_adapter import PlatformSEOAdapter, Platform, PlatformSEOConfig, PlatformOptimizationResult
from .keyword_generator_ai import KeywordGeneratorAI, KeywordType, SearchIntent, KeywordResearchResult
from .meta_optimizer import MetaOptimizer, MetaTagType, ContentType, MetaOptimizationResult
from .hashtag_intelligence import HashtagIntelligence, HashtagCategory, HashtagStrategy
from .multilingual_seo import MultilingualSEO, Language, Region, LocalizationLevel, MultilingualSEOResult
from .trending_analyzer import TrendingAnalyzer, TrendType, TimeFrame, TrendAnalysis
from .competitor_intelligence import CompetitorIntelligence, CompetitorType, AnalysisType, CompetitiveIntelligenceResult
from .seo_performance_tracker import SEOPerformanceTracker, MetricType, TimeRange, PerformanceReport

# Ultra-Advanced SEO modules
from .api_integrations import (
    APIProvider, APICredentials, KeywordData, CompetitorData,
    GoogleKeywordPlannerAPI, SEMrushAPI, AhrefsAPI, APIIntegrationManager,
    load_api_credentials
)
from .ultra_advanced_research import (
    UltraAdvancedKeywordResearch, ResearchParameters, ResearchDepth,
    ResearchStrategy, KeywordOpportunity, CompetitorGapAnalysis,
    UltraAdvancedResearchResult
)
from .real_time_trending import (
    RealTimeTrendingSystem, TrendSource, AlertSeverity, RealTimeTrendData,
    TrendAlert, TrendingOpportunity
)
from .seo_automation_manager import (
    UltraAdvancedSEOManager, AutomationConfig, AutomationMode,
    NotificationChannel, SEOInsight, AutomationReport,
    create_seo_automation_manager
)

__all__ = [
    # Core SEO classes
    "ContentSEOOptimizer",
    "PlatformSEOAdapter", 
    "KeywordGeneratorAI",
    "MetaOptimizer",
    "HashtagIntelligence",
    "MultilingualSEO",
    "TrendingAnalyzer",
    "CompetitorIntelligence",
    "SEOPerformanceTracker",
    
    # Ultra-Advanced SEO classes
    "UltraAdvancedKeywordResearch",
    "RealTimeTrendingSystem",
    "UltraAdvancedSEOManager",
    "APIIntegrationManager",
    "GoogleKeywordPlannerAPI",
    "SEMrushAPI",
    "AhrefsAPI",
    
    # Configuration and factory functions
    "create_seo_automation_manager",
    "load_api_credentials",
    
    # Core enums and utility classes
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
    
    # Ultra-Advanced enums
    "APIProvider",
    "ResearchDepth",
    "ResearchStrategy",
    "TrendSource",
    "AlertSeverity",
    "AutomationMode",
    "NotificationChannel",
    
    # Core result classes
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
    
    # Ultra-Advanced result classes
    "UltraAdvancedResearchResult",
    "KeywordOpportunity",
    "CompetitorGapAnalysis",
    "TrendingOpportunity",
    "AutomationReport",
    "SEOInsight",
    
    # Data classes
    "APICredentials",
    "KeywordData",
    "CompetitorData",
    "ResearchParameters",
    "RealTimeTrendData",
    "TrendAlert",
    "AutomationConfig"
]