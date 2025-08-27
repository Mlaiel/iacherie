"""
IA Influencer Agent - Core Optimization Module
Copyright (C) 2025 Fahed Mlaiel <mlaiel@live.de>

UNAUTHORIZED ACCESS, COPYING, DISTRIBUTION, OR MODIFICATION 
OF THIS CODE IS STRICTLY PROHIBITED.

This module provides advanced optimization capabilities for:
- Performance optimization (AI models, fingerprinting, ML pipelines)
- Content distribution optimization
- Revenue optimization algorithms
- SEO optimization intelligence
- Resource allocation optimization
- Collaboration matching optimization

Lead Developer: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent with Content Protection
"""

from .performance import (
    ModelOptimizer,
    FingerprintingOptimizer,
    CacheOptimizer,
    QueryOptimizer
)

from .content import (
    ContentDistributionOptimizer,
    SEOOptimizer,
    MetadataOptimizer,
    FormatOptimizer
)

from .revenue import (
    RevenueOptimizer,
    MonetizationOptimizer,
    PricingOptimizer,
    PayoutOptimizer
)

from .resource import (
    ResourceOptimizer,
    LoadBalancer,
    StorageOptimizer,
    BandwidthOptimizer
)

from .matching import (
    CollaborationOptimizer,
    PartnershipMatcher,
    RecommendationOptimizer,
    AudienceOptimizer
)

from .pipeline import (
    WorkflowOptimizer,
    ProcessOptimizer,
    ScheduleOptimizer,
    PriorityOptimizer
)

__all__ = [
    # Performance Optimization
    "ModelOptimizer",
    "FingerprintingOptimizer", 
    "CacheOptimizer",
    "QueryOptimizer",
    
    # Content Optimization
    "ContentDistributionOptimizer",
    "SEOOptimizer",
    "MetadataOptimizer",
    "FormatOptimizer",
    
    # Revenue Optimization
    "RevenueOptimizer",
    "MonetizationOptimizer",
    "PricingOptimizer",
    "PayoutOptimizer",
    
    # Resource Optimization
    "ResourceOptimizer",
    "LoadBalancer",
    "StorageOptimizer",
    "BandwidthOptimizer",
    
    # Matching Optimization
    "CollaborationOptimizer",
    "PartnershipMatcher",
    "RecommendationOptimizer",
    "AudienceOptimizer",
    
    # Pipeline Optimization
    "WorkflowOptimizer",
    "ProcessOptimizer",
    "ScheduleOptimizer",
    "PriorityOptimizer"
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
