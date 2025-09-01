"""🏪 Creator Marketplace Module - Advanced Service Marketplace
============================================================

Professional marketplace system for creator services with:
- AI-powered service matching and discovery
- Real-time bidding and auction system  
- Secure escrow integration
- Performance analytics and quality assurance

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

from .creator_marketplace import (
    CreatorMarketplace,
    ServiceListing,
    ServiceBid,
    ServiceOrder,
    ServiceCategory,
    ServiceStatus,
    BidStatus,
    OrderStatus,
    create_marketplace_instance,
    calculate_marketplace_commission
)

# Keep existing imports for compatibility
from .content_manager import ContentManager, ContentMetadata
from .creator_profile import CreatorProfileManager, CreatorProfile
from .collaboration_engine import CollaborationEngine, CollaborationOpportunity
from .monetization_engine import MonetizationEngine, MonetizationStrategy
from .distribution_manager import DistributionManager, DistributionChannel
from .quality_monitor import QualityMonitor, QualityMetrics
from .performance_tracker import PerformanceTracker, PerformanceReport
from .metrics_collector import MetricsCollector, MarketplaceMetrics
from .index import MarketplaceIndex, MarketplaceServiceRegistry, marketplace_index, service_registry, router

__all__ = [
    # New Advanced Marketplace
    'CreatorMarketplace',
    'ServiceListing',
    'ServiceBid', 
    'ServiceOrder',
    'ServiceCategory',
    'ServiceStatus',
    'BidStatus',
    'OrderStatus',
    'create_marketplace_instance',
    'calculate_marketplace_commission',
    
    # Existing Content Management
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

__version__ = "3.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
