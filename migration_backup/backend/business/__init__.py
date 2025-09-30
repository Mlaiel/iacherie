"""Backend Business Module - IA Influencer Agent Platform
========================================================

Consolidated business logic module providing comprehensive enterprise-grade
business rules, workflow orchestration, and process automation for content
creators and influencer management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

POST-CONSOLIDATION ARCHITECTURE:
- 16 consolidated modules (compliant with 18-file limit)
- Preserved enterprise functionality
- Optimized imports and exports
- Optimized maintainability
"""

# === CORE BUSINESS MODULES ===
from .rules import BusinessRulesEngine
from .workflows import WorkflowOrchestrator  
from .validation import BusinessValidator
from .automation import ProcessAutomation

# === ENTERPRISE OPERATIONS ===
from .orchestration import ServiceOrchestrator
from .integration import SystemIntegrator
from .monitoring import BusinessMonitor
from .compliance import ComplianceManager

# === ANALYTICS & INTELLIGENCE (CONSOLIDATED) ===
# analytics.py now includes: market_intelligence + reporting
from .analytics import (
    BusinessAnalytics,
    BusinessReporter,
    MarketTrendAnalyzer,
    ForecastingEngine,
    CompetitiveIntelligenceGatherer,
    PricingStrategyOptimizer
)

# === OPTIMIZATION (CONSOLIDATED) ===
# optimization.py now includes: performance_optimization + customer_lifecycle
from .optimization import (
    PerformanceOptimizer,
    CustomerLifecycleManager,
    ProcessOptimizer,
    ResourceOptimizer
)

# === MONETIZATION (CONSOLIDATED) ===
# monetization_engine.py now includes: basic_monetization + revenue_management
from .monetization_engine import (
    MonetizationEngine,
    BiddingSystem,
    AuctionEngine,
    DisputeResolver,
    ConflictMediation,
    EnterpriseBilling,
    InvoiceAutomation,
    ProjectBid,
    AuctionConfig,
    AttributionTracker,
    RevenueAttribution,
    ForecastingModel,
    RevenueProjection,
    CommissionManager,
    FeeCalculation,
    CryptocurrencyProcessor,
    CryptoPayments,
    PaymentStatus,
    PaymentMethod,
    ContentMonetizationManager,
    RevenueStreamManager,
    PaymentProcessor
)

# === LEGACY MONETIZATION (CONSOLIDATED) ===
# legacy_monetization.py includes: crypto_processor + payment_router + revenue_tracking
from .legacy_monetization import (
    EnterpriseCryptoProcessor,
    CryptoAnalytics,
    CryptoNetwork,
    enterprise_crypto_processor,
    crypto_analytics,
    AIRevenueTracker,
    RevenueForecastingEngine,
    ai_revenue_tracker,
    revenue_forecasting_engine,
    IntelligentPaymentRouter,
    PaymentOptimizer,
    intelligent_payment_router,
    payment_optimizer
)

# === RISK & PROTECTION (CONSOLIDATED) ===
# risk_protection.py includes: risk_management + protection_suite + quality_assurance
from .risk_protection import (
    BusinessRiskAssessmentAutomator,
    RiskMitigationStrategyImplementer,
    BlockchainNotary,
    ImmutableRecords,
    ViolationDetector,
    InfringementScanner,
    DMCAProcessor,
    TakedownAutomation,
    FingerprintAnalyzer,
    ContentIdentification,
    QualityAssuranceManager,
    QualityMetricsTracker
)

# === STRATEGY & INNOVATION (CONSOLIDATED) ===
# strategy_innovation.py includes: strategic_planning + innovation_management
from .strategy_innovation import (
    StrategicBusinessPlanningEngine,
    BusinessInnovationEngine,
    InnovationMetricsTracker,
    StrategicGoalManager
)

# === PARTNERSHIPS (RENAMED) ===
# partnerships.py (formerly partnership_management.py)
from .partnerships import (
    PartnershipLifecycleManager,
    BrandCollaborationOrchestrator,
    InfluencerBrandMatcher,
    PartnershipPerformanceAnalyzer
)

__all__ = [
    # === Core Business ===
    'BusinessRulesEngine',
    'WorkflowOrchestrator',
    'BusinessValidator',
    'ProcessAutomation',
    
    # === Enterprise Operations ===
    'ServiceOrchestrator',
    'SystemIntegrator',
    'BusinessMonitor',
    'ComplianceManager',
    
    # === Analytics & Intelligence ===
    'BusinessAnalytics',
    'BusinessReporter',
    'MarketTrendAnalyzer',
    'ForecastingEngine',
    'CompetitiveIntelligenceGatherer',
    'PricingStrategyOptimizer',
    
    # === Optimization ===
    'PerformanceOptimizer',
    'CustomerLifecycleManager',
    'ProcessOptimizer',
    'ResourceOptimizer',
    
    # === Monetization ===
    'MonetizationEngine',
    'BiddingSystem',
    'AuctionEngine',
    'DisputeResolver',
    'ConflictMediation',
    'EnterpriseBilling',
    'InvoiceAutomation',
    'ProjectBid',
    'AuctionConfig',
    'AttributionTracker',
    'RevenueAttribution',
    'ForecastingModel',
    'RevenueProjection',
    'CommissionManager',
    'FeeCalculation',
    'CryptocurrencyProcessor',
    'CryptoPayments',
    'PaymentStatus',
    'PaymentMethod',
    'ContentMonetizationManager',
    'RevenueStreamManager',
    'PaymentProcessor',
    
    # === Legacy Monetization ===
    'EnterpriseCryptoProcessor',
    'CryptoAnalytics',
    'CryptoNetwork',
    'enterprise_crypto_processor',
    'crypto_analytics',
    'AIRevenueTracker',
    'RevenueForecastingEngine',
    'ai_revenue_tracker',
    'revenue_forecasting_engine',
    'IntelligentPaymentRouter',
    'PaymentOptimizer',
    'intelligent_payment_router',
    'payment_optimizer',
    
    # === Risk & Protection ===
    'BusinessRiskAssessmentAutomator',
    'RiskMitigationStrategyImplementer',
    'BlockchainNotary',
    'ImmutableRecords',
    'ViolationDetector',
    'InfringementScanner',
    'DMCAProcessor',
    'TakedownAutomation',
    'FingerprintAnalyzer',
    'ContentIdentification',
    'QualityAssuranceManager',
    'QualityMetricsTracker',
    
    # === Strategy & Innovation ===
    'StrategicBusinessPlanningEngine',
    'BusinessInnovationEngine',
    'InnovationMetricsTracker',
    'StrategicGoalManager',
    
    # === Partnerships ===
    'PartnershipLifecycleManager',
    'BrandCollaborationOrchestrator',
    'InfluencerBrandMatcher',
    'PartnershipPerformanceAnalyzer'
]

__version__ = "4.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__consolidation__ = "16 modules (Phase 7 Post-Consolidation)"

# Existing Core Business Modules
from .rules import BusinessRulesEngine
from .workflows import WorkflowOrchestrator  
from .validation import BusinessValidator
from .automation import ProcessAutomation
from .integration import SystemIntegrator
from .analytics import BusinessAnalytics
from .reporting import BusinessReporter
from .compliance import ComplianceManager
from .optimization import PerformanceOptimizer
from .monitoring import BusinessMonitor
from .orchestration import ServiceOrchestrator

# Consolidated Enterprise Modules (Phase 1)
from .monetization_engine import (
    BiddingSystem, AuctionEngine, DisputeResolver, ConflictMediation,
    EnterpriseBilling, InvoiceAutomation, ProjectBid, AuctionConfig
)
from .protection_suite import (
    BlockchainNotary, ImmutableRecords, ViolationDetector, InfringementScanner,
    DMCAProcessor, TakedownAutomation, FingerprintAnalyzer, ContentIdentification
)
from .revenue_management import (
    AttributionTracker, RevenueAttribution, ForecastingModel, RevenueProjection,
    CommissionManager, FeeCalculation, CryptocurrencyProcessor, CryptoPayments
)

# New Enterprise Modules (Phase 2)
from .partnership_management import (
    PartnershipLifecycleManager, BrandCollaborationOrchestrator,
    InfluencerBrandMatcher, PartnershipPerformanceAnalyzer
)
from .market_intelligence import (
    MarketTrendAnalyzer, ForecastingEngine, CompetitiveIntelligenceGatherer,
    PricingStrategyOptimizer
)
from .customer_lifecycle import (
    CustomerAcquisitionOptimizer, OnboardingAutomationWorkflows,
    RetentionStrategyImplementer, ChurnPredictionPreventer
)
from .performance_optimization import (
    BusinessProcessOptimizer, ResourceAllocationOptimizer
)
from .risk_management import (
    BusinessRiskAssessmentAutomator, RiskMitigationStrategyImplementer,
    FraudDetectionPreventer
)
from .strategic_planning import (
    StrategicPlanningOrchestrator, GoalSettingFramework, 
    PerformanceMetricsCalculator, SuccessMetricsTracker
)

# Basic monetization (from business migration)
from .basic_monetization import (
    BusinessRule, MonetizationRule, ContentMonetizationManager,
    RevenueStreamManager, PaymentProcessor
)
from .quality_assurance import (
    QualityControlAutomator, ProcessQualityMonitor,
    StandardsComplianceVerifier
)
from .innovation_management import (
    InnovationPipelineManager, IdeaGenerationEvaluator,
    InnovationProjectTracker
)

# Legacy Monetization (moved from legacy_monetization/)
from .legacy_crypto_processor import (
    EnterpriseCryptoProcessor,
    CryptoAnalytics,
    CryptoNetwork,
    enterprise_crypto_processor,
    crypto_analytics
)
from .legacy_revenue_tracking import (
    AIRevenueTracker,
    RevenueForecastingEngine,
    ai_revenue_tracker,
    revenue_forecasting_engine
)
from .legacy_payment_router import (
    IntelligentPaymentRouter,
    PaymentOptimizer,
    intelligent_payment_router,
    payment_optimizer
)

__all__ = [
    # Core business rules and workflows
    'BusinessRulesEngine',
    'WorkflowOrchestrator',
    'BusinessValidator',
    'ProcessAutomation',
    'SystemIntegrator',
    'BusinessAnalytics',
    'BusinessReporter',
    'ComplianceManager',
    'PerformanceOptimizer', 
    'BusinessMonitor',
    'ServiceOrchestrator',
    
    # Enterprise monetization
    'BiddingSystem',
    'AuctionEngine', 
    'DisputeResolver',
    'ConflictMediation',
    'DealNegotiator',
    'ContractManager',
    'MultiChannelEngine',
    'RevenueDiversifier',
    'LegalComplianceEngine',
    'GlobalTaxManager',
    'BrandProtector',
    'AdRevenueManager',
    'InfluencerMarketplace',
    'ContentLicensing',
    'SubscriptionEngine',
    'DonationManager',
    'SponsorshipEngine',
    'AffiliateManager',
    'MonetizationRule', 
    'ContentMonetizationManager',
    'RevenueStreamManager',
    'PaymentProcessor',
    
    # Legacy monetization (moved from subdirectory)
    'EnterpriseCryptoProcessor',
    'CryptoAnalytics', 
    'CryptoNetwork',
    'enterprise_crypto_processor',
    'crypto_analytics',
    'AIRevenueTracker',
    'RevenueForecastingEngine',
    'ai_revenue_tracker',
    'revenue_forecasting_engine',
    'IntelligentPaymentRouter',
    'PaymentOptimizer',
    'intelligent_payment_router', 
    'payment_optimizer'
]

__version__ = "3.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"