"""
Marketplace Agent - Enterprise Content Marketplace & Collaboration Platform

This module provides comprehensive marketplace management, creator collaboration,
content distribution, and AI-powered monetization optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited
"""

from .marketplace_agent import MarketplaceAgent
from .listing_manager import ListingManager
from .collaboration_orchestrator import CollaborationOrchestrator
from .marketplace_analytics import MarketplaceAnalytics
from .monetization_engine import MonetizationEngine
from .matching_engine import MatchingEngine
from .transaction_processor import TransactionProcessor
from .content_validator import ContentValidator
from .marketplace_security import MarketplaceSecurity
from .distribution_manager import DistributionManager

__all__ = [
    'MarketplaceAgent',
    'ListingManager',
    'CollaborationOrchestrator',
    'MarketplaceAnalytics',
    'MonetizationEngine',
    'MatchingEngine',
    'TransactionProcessor',
    'ContentValidator',
    'MarketplaceSecurity',
    'DistributionManager',
]

__version__ = '2.0.0'
__author__ = 'Fahed Mlaiel'
__email__ = 'mlaiel@live.de'
__status__ = 'Production'
