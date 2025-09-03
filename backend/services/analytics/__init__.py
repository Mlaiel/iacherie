"""Analytics & SEO Engine - Comprehensive Analytics and SEO Services

Advanced analytics and SEO optimization services for the IA Influencer Agent platform.
Provides comprehensive tracking, optimization, and reporting capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .seo import (
    ContentOptimizer,
    MetaGenerator,
    SitemapBuilder
)

from .tracking import (
    UserBehaviorTracker,
    ContentPerformanceTracker,
    EngagementMetrics
)

from .reporting import (
    ReportGenerator,
    ExportManager
)

# Module version
__version__ = "1.0.0"

# Module description
__description__ = "Analytics & SEO Engine for comprehensive platform optimization"

# Export all main classes
__all__ = [
    # SEO Module
    'ContentOptimizer',
    'MetaGenerator', 
    'SitemapBuilder',
    
    # Tracking Module
    'UserBehaviorTracker',
    'ContentPerformanceTracker',
    'EngagementMetrics',
    
    # Reporting Module
    'ReportGenerator',
    'ExportManager'
]