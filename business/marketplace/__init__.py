"""
IA Influencer Agent - Marketplace Business Module
Enterprise-grade marketplace system for content creators and AI-powered collaborations.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent
Copyright: All rights reserved - Unauthorized use strictly prohibited

WARNING: This code and concept are proprietary to Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Legal action will be taken against violators.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer: Fahed Mlaiel
- ML Engineer & Data Scientist: Fahed Mlaiel  
- Database Administrator & Security Expert: Fahed Mlaiel
- Microservices & Audio Processing Specialist: Fahed Mlaiel
- DevOps & IA Prompt Engineer: Fahed Mlaiel

This module provides comprehensive marketplace functionality including:
- Content discovery and matching
- Creator collaboration platforms
- AI-powered content optimization
- Multi-format content distribution
- Revenue sharing and monetization
"""

from .content_manager import ContentManager, ContentMetadata
from .creator_profile import CreatorProfileManager, CreatorProfile
from .collaboration_engine import CollaborationEngine, CollaborationOpportunity
from .monetization_engine import MonetizationEngine, MonetizationStrategy
from .distribution_manager import DistributionManager, DistributionChannel
from .quality_monitor import QualityMonitor, QualityMetrics
from .performance_tracker import PerformanceTracker, PerformanceReport
from .metrics_collector import MetricsCollector, MarketplaceMetrics
from .index import MarketplaceIndex, MarketplaceServiceRegistry, marketplace_index, service_registry, router

# Export all main classes and functions
__all__ = [
    # Content Management
    'ContentManager',
    'ContentMetadata',
    
    # Creator Profiles
    'CreatorProfileManager', 
    'CreatorProfile',
    
    # Collaboration
    'CollaborationEngine',
    'CollaborationOpportunity',
    
    # Monetization
    'MonetizationEngine',
    'MonetizationStrategy',
    
    # Distribution
    'DistributionManager',
    'DistributionChannel',
    
    # Quality & Performance
    'QualityMonitor',
    'QualityMetrics',
    'PerformanceTracker',
    'PerformanceReport',
    
    # Metrics
    'MetricsCollector',
    'MarketplaceMetrics',
    
    # Index & Registry
    'MarketplaceIndex',
    'MarketplaceServiceRegistry',
    'marketplace_index',
    'service_registry',
    'router'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
