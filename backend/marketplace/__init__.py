"""Advanced Marketplace Module

Comprehensive marketplace system providing auction management, licensing,
revenue sharing, influencer trading, and enterprise compliance for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Core marketplace modules
from .auction_system import AuctionSystem, AuctionEngine, AuctionStatus
from .licensing import LicensingManager, LicenseAgreement, LicenseValidation
from .revenue_sharing import RevenueShareManager, RevenueDistribution, ShareCalculator
from .influencer_trading import InfluencerTradingEngine, TradingTransaction, MarketMaker

# Performance & scaling modules
from .marketplace_cache import (
    MarketplaceCacheManager, MarketplaceCacheHelpers, CacheLayer, CacheStrategy,
    InvalidationStrategy, CacheKey, CacheEntry, CacheStats, CacheConfig
)
from .database_optimizer import (
    DatabaseOptimizer, QueryType, PerformanceLevel, OptimizationType,
    QueryMetrics, OptimizationRecommendation, IndexRecommendation,
    TableStatistics, ConnectionPoolStats
)
from .load_balancer import (
    LoadBalancer, LoadBalancingAlgorithm, ServerStatus, CircuitBreakerState,
    ServerInstance, HealthCheckConfig, CircuitBreaker, LoadBalancerStats, TrafficRule
)
from .cdn_integration import (
    CDNIntegrationManager, CDNProvider, ContentType, CacheStrategy as CDNCacheStrategy,
    OptimizationLevel, CDNEndpoint, ContentItem, CacheInvalidationRequest,
    CDNPerformanceMetrics, ContentOptimizationResult
)
from .marketplace_compliance import (
    MarketplaceComplianceManager, ComplianceStatus, GDPRRights, 
    ComplianceRegion, ComplianceRecord, GDPRRequest, LegalFramework
)
from .fraud_detection import (
    FraudDetectionEngine, FraudRiskLevel, FraudType, FraudAction,
    FraudIndicator, FraudScore, FraudAlert, BehaviorPattern
)
from .identity_verification import (
    IdentityVerificationEngine, VerificationLevel, VerificationStatus,
    DocumentType, AMLRiskLevel, BiometricType, IdentityDocument,
    BiometricVerification, AMLScreening, VerificationSession, VerificationResult
)
from .legal_framework import (
    LegalFrameworkEngine, ContractType, ContractStatus, LegalJurisdiction,
    ComplianceType, LegalAction, LegalTemplate, LegalContract,
    ComplianceRule, LegalValidation, LegalDispute
)

__all__ = [
    # Core marketplace
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
    "MarketMaker",
    
    # Performance & scaling
    "MarketplaceCacheManager",
    "MarketplaceCacheHelpers",
    "CacheLayer",
    "CacheStrategy",
    "InvalidationStrategy",
    "CacheKey",
    "CacheEntry",
    "CacheStats",
    "CacheConfig",
    "DatabaseOptimizer",
    "QueryType",
    "PerformanceLevel",
    "OptimizationType",
    "QueryMetrics",
    "OptimizationRecommendation",
    "IndexRecommendation",
    "TableStatistics",
    "ConnectionPoolStats",
    "LoadBalancer",
    "LoadBalancingAlgorithm",
    "ServerStatus",
    "CircuitBreakerState",
    "ServerInstance",
    "HealthCheckConfig",
    "CircuitBreaker",
    "LoadBalancerStats",
    "TrafficRule",
    "CDNIntegrationManager",
    "CDNProvider",
    "ContentType",
    "CDNCacheStrategy",
    "OptimizationLevel",
    "CDNEndpoint",
    "ContentItem",
    "CacheInvalidationRequest",
    "CDNPerformanceMetrics",
    "ContentOptimizationResult",
    
    # Enterprise compliance
    "MarketplaceComplianceManager",
    "ComplianceStatus",
    "GDPRRights",
    "ComplianceRegion",
    "ComplianceRecord",
    "GDPRRequest",
    "LegalFramework",
    
    # Fraud detection
    "FraudDetectionEngine",
    "FraudRiskLevel",
    "FraudType",
    "FraudAction",
    "FraudIndicator",
    "FraudScore",
    "FraudAlert",
    "BehaviorPattern",
    
    # Identity verification
    "IdentityVerificationEngine",
    "VerificationLevel",
    "VerificationStatus",
    "DocumentType",
    "AMLRiskLevel",
    "BiometricType",
    "IdentityDocument",
    "BiometricVerification",
    "AMLScreening",
    "VerificationSession",
    "VerificationResult",
    
    # Legal framework
    "LegalFrameworkEngine",
    "ContractType",
    "ContractStatus",
    "LegalJurisdiction",
    "ComplianceType",
    "LegalAction",
    "LegalTemplate",
    "LegalContract",
    "ComplianceRule",
    "LegalValidation",
    "LegalDispute"
]

__version__ = "3.0.0"
__author__ = "Fahed Mlaiel"