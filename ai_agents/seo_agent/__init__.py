"""
SEO Agent Module - AI-Powered Search Engine Optimization

Advanced SEO optimization system that enhances content discoverability through intelligent
keyword optimization, metadata enhancement, and search ranking improvements.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Project Team Specializations:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + AI Prompt Engineer
- Expert: Fahed Mlaiel <mlaiel@live.de>

🚨 STRONG WARNING FOR COPYRIGHT VIOLATORS:
Any attempt to steal, copy, reverse-engineer, or commercialize this code without explicit written authorization 
will result in immediate legal action under German and international intellectual property law.
Contact mlaiel@live.de for licensing inquiries only.
"""

# Core SEO Agent Components
from .seo_agent import (
    SEOAgent, 
    OptimizationType, 
    ContentType, 
    SEOAnalysis, 
    KeywordData
)

# SEO Campaign Management
from .seo_manager import (
    SEOAgentManager,
    SEOCampaign,
    CampaignStatus,
    CampaignType,
    SEOPerformanceMetrics
)

# Keyword Research & Analysis
from .keyword_research import (
    KeywordAnalyzer,
    TrendAnalyzer,
    CompetitorAnalyzer,
    KeywordMetrics,
    TrendData,
    CompetitorKeywords,
    KeywordDifficulty,
    KeywordIntent,
    TrendDirection
)

# Content Optimization
from .content_optimization import (
    MetadataOptimizer,
    ContentStructureOptimizer,
    LinkBuilder,
    OptimizationSuggestion,
    ContentAnalysis,
    MetadataOptimization,
    OptimizationLevel,
    ContentFormat,
    SchemaType
)

# Metrics & Monitoring
from .metrics import (
    SEOMetricsCollector,
    MetricType,
    MetricCategory,
    MetricPoint,
    MetricSeries
)

# Reporting System
from .reporting import (
    SEOReportGenerator,
    ReportType,
    ReportFormat,
    ReportSection,
    ReportConfig
)

# Configuration Management
from .config import (
    SEOAgentConfig
)

# Main System Entry Point
from .index import (
    SEOSystem,
    analyze_content,
    optimize_content,
    research_keywords
)

# Export all public components
__all__ = [
    # Core Agent
    'SEOAgent',
    'OptimizationType',
    'ContentType',
    'SEOAnalysis',
    'KeywordData',
    
    # Campaign Management
    'SEOAgentManager',
    'SEOCampaign',
    'CampaignStatus',
    'CampaignType',
    'SEOPerformanceMetrics',
    
    # Keyword Research
    'KeywordAnalyzer',
    'TrendAnalyzer',
    'CompetitorAnalyzer',
    'KeywordMetrics',
    'TrendData',
    'CompetitorKeywords',
    'KeywordDifficulty',
    'KeywordIntent',
    'TrendDirection',
    
    # Content Optimization
    'MetadataOptimizer',
    'ContentStructureOptimizer',
    'LinkBuilder',
    'OptimizationSuggestion',
    'ContentAnalysis',
    'MetadataOptimization',
    'OptimizationLevel',
    'ContentFormat',
    'SchemaType',
    
    # Metrics & Monitoring
    'SEOMetricsCollector',
    'MetricType',
    'MetricCategory',
    'MetricPoint',
    'MetricSeries',
    
    # Reporting System
    'SEOReportGenerator',
    'ReportType',
    'ReportFormat',
    'ReportSection',
    'ReportConfig',
    
    # Configuration
    'SEOAgentConfig',
    
    # Main System
    'SEOSystem',
    'analyze_content',
    'optimize_content',
    'research_keywords'
]

# Module metadata
__version__ = '1.2.0'
__author__ = 'Fahed Mlaiel'
__email__ = 'mlaiel@live.de'
__copyright__ = 'Copyright (c) 2025 Fahed Mlaiel. All rights reserved.'
__license__ = 'Proprietary - Unauthorized use strictly prohibited'

# SEO Agent Configuration
SEO_AGENT_INFO = {
    'name': 'SEO Agent - Advanced Search Engine Optimization System',
    'version': __version__,
    'author': __author__,
    'specializations': [
        'Lead Dev IA',
        'Backend Senior', 
        'ML Engineer',
        'DBA',
        'Security Expert',
        'Microservices Architect',
        'Audio Processing',
        'DevOps Engineer',
        'AI Prompt Engineer'
    ],
    'capabilities': [
        'AI-Powered Content Analysis',
        'Intelligent Keyword Research',
        'Competitive Intelligence',
        'Technical SEO Auditing',
        'Metadata Optimization',
        'Content Structure Enhancement',
        'Trend Analysis & Prediction',
        'Campaign Management',
        'Multi-language Support',
        'Real-time Performance Tracking',
        'Advanced Metrics Collection',
        'Automated Report Generation',
        'Interactive Data Visualization',
        'ROI Analysis & Projections',
        'Scheduled Performance Reports',
        'Alert & Notification System'
    ],
    'supported_content_types': [
        'Music Tracks & Albums',
        'Video Content',
        'Blog Posts & Articles', 
        'Social Media Posts',
        'Portfolio Pages',
        'E-commerce Products',
        'Podcast Episodes',
        'Event Pages'
    ],
    'contact': {
        'email': __email__,
        'licensing': 'Contact for commercial licensing inquiries',
        'support': 'Technical support available for licensed users'
    }
}
