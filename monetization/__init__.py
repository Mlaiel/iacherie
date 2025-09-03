"""Enterprise Monetization Module - Complete System
=================================================

Advanced AI-powered monetization platform with comprehensive business logic integration.
Complete implementation of multi-currency payments, automated billing, subscription management,
revenue intelligence, smart payment orchestration, and compliance automation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Core Licensing & Rights Management
from .licensing_manager import LicensingManager
from .royalty_engine import RoyaltyEngine
from .usage_tracker import UsageTracker
from .contract_generator import ContractGenerator
from .rights_validator import RightsValidator

# Payment Processing & Distribution
from .payment_processor import PaymentProcessor, PaymentProvider, PaymentStatus, PaymentType
from .enhanced_payment_providers import EnhancedPaymentProviderManager
from .distribution_engine import DistributionEngine

# Enterprise Revenue Intelligence
from .revenue_intelligence_engine import (
    RevenueIntelligenceEngine, 
    RevenueMetric, 
    CustomerLifetimeValue,
    ChurnRiskAssessment,
    RevenueForcast,
    RevenueMetricType,
    ChurnRiskLevel
)

# Smart Payment Orchestration
from .smart_payment_orchestrator import (
    SmartPaymentOrchestrator,
    PaymentRoute,
    PaymentAttempt,
    FraudAssessment,
    PaymentOptimization,
    PaymentMethod,
    FraudRiskLevel
)

# Advanced Compliance & Regulatory
from .compliance_automation_engine import (
    ComplianceAutomationEngine,
    ComplianceRule,
    ComplianceAssessment,
    AuditTrailEntry,
    RevenueRecognitionEntry,
    TaxComplianceRecord,
    ComplianceFramework,
    TaxJurisdiction,
    ComplianceStatus,
    AuditTrailEventType
)

# Business Logic Integration
from .business_logic_integrator import (
    BusinessLogicIntegrator,
    ContentMonetizationProfile,
    WorkflowMonetizationEvent,
    DynamicPricingModel,
    WorkflowStage,
    ContentType,
    MonetizationStrategy
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Core Licensing & Rights
    "LicensingManager",
    "RoyaltyEngine", 
    "UsageTracker",
    "ContractGenerator",
    "RightsValidator",
    
    # Payment Processing
    "PaymentProcessor",
    "PaymentProvider",
    "PaymentStatus", 
    "PaymentType",
    "EnhancedPaymentProviderManager",
    "DistributionEngine",
    
    # Revenue Intelligence
    "RevenueIntelligenceEngine",
    "RevenueMetric",
    "CustomerLifetimeValue",
    "ChurnRiskAssessment",
    "RevenueForcast",
    "RevenueMetricType",
    "ChurnRiskLevel",
    
    # Payment Orchestration
    "SmartPaymentOrchestrator",
    "PaymentRoute",
    "PaymentAttempt", 
    "FraudAssessment",
    "PaymentOptimization",
    "PaymentMethod",
    "FraudRiskLevel",
    
    # Compliance & Regulatory
    "ComplianceAutomationEngine",
    "ComplianceRule",
    "ComplianceAssessment",
    "AuditTrailEntry",
    "RevenueRecognitionEntry", 
    "TaxComplianceRecord",
    "ComplianceFramework",
    "TaxJurisdiction",
    "ComplianceStatus",
    "AuditTrailEventType",
    
    # Business Logic Integration
    "BusinessLogicIntegrator",
    "ContentMonetizationProfile",
    "WorkflowMonetizationEvent", 
    "DynamicPricingModel",
    "WorkflowStage",
    "ContentType",
    "MonetizationStrategy",
]

# Licensing configuration
LICENSING_CONFIG = {
    "licensing_tiers": {
        "basic": {
            "price": 10.0,
            "duration_days": 30,
            "usage_limits": {"downloads": 100, "streams": 1000},
            "commercial_use": False
        },
        "standard": {
            "price": 50.0,
            "duration_days": 90,
            "usage_limits": {"downloads": 500, "streams": 10000},
            "commercial_use": True
        },
        "premium": {
            "price": 200.0,
            "duration_days": 365,
            "usage_limits": {"downloads": 2000, "streams": 50000},
            "commercial_use": True,
            "exclusive": True
        }
    },
    "royalty_rates": {
        "streaming": 0.004,  # per stream
        "download": 0.1,     # per download
        "sync": 0.15,        # sync licensing
        "commercial": 0.25   # commercial usage
    },
    "auto_licensing": {
        "enabled": True,
        "approval_threshold": 100.0,  # Auto-approve under this amount
        "payment_terms": "net_30",
        "default_territory": "worldwide"
    }
}

# Global licensing manager instance
_licensing_manager = None

def get_licensing_manager():
    """Get global licensing manager instance."""
    global _licensing_manager
    if _licensing_manager is None:
        _licensing_manager = LicensingManager()
    return _licensing_manager

async def create_license(content_id: int, licensee_id: int, license_type: str, terms: dict):
    """
Create new content license."""
    manager = get_licensing_manager()
    return await manager.create_license(content_id, licensee_id, license_type, terms)

async def track_usage(license_id: int, usage_type: str, usage_data: dict):
    """
Track license usage."""
    manager = get_licensing_manager()
    return await manager.track_usage(license_id, usage_type, usage_data)

async def calculate_royalties(license_id: int, period_start: str, period_end: str):
    """
Calculate royalties for license period."""
    manager = get_licensing_manager()
    return await manager.calculate_royalties(license_id, period_start, period_end)
