"""Advanced Marketplace Module

Comprehensive marketplace system providing auction management, licensing,
revenue sharing, and influencer trading for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .auction_system import AuctionSystem, AuctionEngine, AuctionStatus
from .licensing import LicensingManager, LicenseAgreement, LicenseValidation
from .revenue_sharing import RevenueShareManager, RevenueDistribution, ShareCalculator
from .influencer_trading import InfluencerTradingEngine, TradingTransaction, MarketMaker

__all__ = [
    "AuctionSystem",
    "AuctionEngine", 
    "AuctionStatus",
    "LicensingManager",
    "LicenseAgreement",
    "LicenseValidation",
    "RevenueShareManager",
    "RevenueDistribution",
    "ShareCalculator",
    "InfluencerTradingEngine",
    "TradingTransaction",
    "MarketMaker"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"