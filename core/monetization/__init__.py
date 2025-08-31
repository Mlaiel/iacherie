"""Advanced Monetization Core Module for IA Influencer Agent Platform
Enterprise-grade revenue tracking, licensing, and payment processing system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Warning: Unauthorized use, reproduction, or distribution is strictly prohibited.

Expert Team Specialties:
- Lead AI Developer & Platform Architect
- Backend Senior Engineer  
- ML/AI Engineering Specialist
- Database Administrator
- Security & Compliance Expert
- Microservices Architecture Specialist
- Audio Processing Engineer
- DevOps & Infrastructure Engineer
- IA Prompt Engineering Specialist
"""
from .payment_processor import PaymentProcessor, PaymentConfig
from .revenue_calculator import RevenueCalculator, RevenueMetrics
from .platform_connector import PlatformConnector, PlatformManager
from .licensing_engine import LicensingEngine, LicenseManager
from .distribution_engine import DistributionEngine, PayoutManager
from .analytics_engine import MonetizationAnalytics, RevenueAnalyzer
from .commission_calculator import CommissionCalculator, CommissionStructure
from .withdrawal_manager import WithdrawalManager, WithdrawalRequest
from .tax_calculator import TaxCalculator, TaxConfiguration
from .financial_reporter import FinancialReporter, ReportGenerator

# New advanced monetization modules
from .platform_revenue_integration import (
    PlatformRevenueAggregator, SpotifyRevenueIntegration, 
    YouTubeRevenueIntegration, InstagramRevenueIntegration, 
    TikTokRevenueIntegration, RevenueSync, PlatformType, RevenueType
)
from .content_licensing_system import (
    LicensingEngine as AdvancedLicensingEngine, PricingEngine, 
    LicenseMonitor, LicenseType, ContentType, LicenseStatus
)
from .automated_payout_engine import (
    PayoutEngine, PayoutOptimizer, PayoutScheduler, 
    PayoutStatus, PayoutMethod, PayoutFrequency
)
from .performance_analytics_engine import (
    PerformanceAnalyticsEngine, RevenueAnalyzer as AdvancedRevenueAnalyzer,
    EngagementAnalyzer, MetricType, InsightType
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Core monetization components
    "PaymentProcessor",
    "PaymentConfig", 
    "RevenueCalculator",
    "RevenueMetrics",
    "PlatformConnector",
    "PlatformManager",
    "LicensingEngine",
    "LicenseManager",
    "DistributionEngine",
    "PayoutManager",
    "MonetizationAnalytics",
    "RevenueAnalyzer",
    "CommissionCalculator",
    "CommissionStructure",
    "WithdrawalManager",
    "WithdrawalRequest",
    "TaxCalculator", 
    "TaxConfiguration",
    "FinancialReporter",
    "ReportGenerator",
    
    # Advanced platform integration
    "PlatformRevenueAggregator",
    "SpotifyRevenueIntegration",
    "YouTubeRevenueIntegration", 
    "InstagramRevenueIntegration",
    "TikTokRevenueIntegration",
    "RevenueSync",
    "PlatformType",
    "RevenueType",
    
    # Advanced licensing system
    "AdvancedLicensingEngine",
    "PricingEngine",
    "LicenseMonitor", 
    "LicenseType",
    "ContentType",
    "LicenseStatus",
    
    # Automated payout engine
    "PayoutEngine",
    "PayoutOptimizer",
    "PayoutScheduler",
    "PayoutStatus", 
    "PayoutMethod",
    "PayoutFrequency",
    
    # Performance analytics
    "PerformanceAnalyticsEngine",
    "AdvancedRevenueAnalyzer",
    "EngagementAnalyzer",
    "MetricType",
    "InsightType"
]