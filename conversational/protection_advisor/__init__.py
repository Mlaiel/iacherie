"""Protection Advisor Module - Enterprise-grade content protection advisory system.

This module provides intelligent, AI-powered recommendations and strategies
for protecting digital content across multiple platforms and jurisdictions.

Key Features:
- Multi-format content protection analysis (audio, video, image, text)
- Real-time threat detection and vulnerability assessment
- AI-powered protection strategy recommendations
- Cross-platform compliance monitoring
- Revenue impact analysis and optimization
- Advanced risk scoring with machine learning
- Enterprise-grade security and encryption

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This code is proprietary and confidential. Unauthorized copying, distribution,
or use is strictly prohibited and may result in severe legal consequences.
"""from .advisor_core import (
    ProtectionAdvisorCore,
    ContentAnalysis,
    ProtectionAdvice,
    ThreatDetail,
    ComplianceAssessment,
    ProtectionGap,
    RevenueImpactAnalysis,
    ContentType,
    RiskLevel,
    ProtectionStatus,
    ThreatCategory,
    ComplianceFramework,
    create_protection_advisor
)

from .risk_analyzer import (
    RiskAnalyzer,
    RiskAssessment,
    RiskFactor,
    ThreatIntelligence,
    MarketRiskProfile,
    RiskMetrics,
    RiskCategory,
    ThreatSeverity,
    RiskTimeframe,
    MarketSegment,
    create_risk_analyzer
)

from .recommendation_engine import (
    RecommendationEngine,
    Recommendation,
    CostBenefitAnalysis,
    ImplementationPlan,
    RecommendationMetrics,
    PersonalizationFactors,
    RecommendationType,
    Priority,
    ImplementationComplexity,
    ROICategory,
    IndustrySegment,
    create_recommendation_engine
)

from .threat_detector import (
    ThreatDetector,
    DetectedThreat,
    ThreatEvidence,
    ThreatContext,
    ThreatImpactAssessment,
    ThreatIntelligence as ThreatIntel,
    ThreatType,
    ThreatSource,
    ThreatStatus,
    DetectionMethod,
    create_threat_detector
)

from .protection_strategies import ProtectionStrategies
from .compliance_checker import ComplianceChecker
from .protection_metrics import ProtectionMetrics
from .alert_manager import AlertManager
from .policy_engine import PolicyEngine
from .advisory_orchestrator import AdvisoryOrchestrator
from .fingerprinting_integration import FingerprintingIntegration
from .content_surveillance import ContentSurveillance

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

__all__ = [
    # Core components
    "ProtectionAdvisorCore",
    "create_protection_advisor",
    
    # Risk analysis
    "RiskAnalyzer",
    "RiskAssessment",
    "RiskFactor",
    "MarketRiskProfile",
    "RiskMetrics",
    "create_risk_analyzer",
    
    # Recommendations
    "RecommendationEngine",
    "Recommendation",
    "CostBenefitAnalysis",
    "ImplementationPlan",
    "RecommendationMetrics",
    "PersonalizationFactors",
    "create_recommendation_engine",
    
    # Threat detection
    "ThreatDetector",
    "DetectedThreat",
    "ThreatEvidence",
    "ThreatContext",
    "ThreatImpactAssessment",
    "create_threat_detector",
    
    # Content analysis
    "ContentAnalysis",
    "ProtectionAdvice",
    "ThreatDetail",
    "ComplianceAssessment",
    "ProtectionGap",
    "RevenueImpactAnalysis",
    
    # Enums and types
    "ContentType",
    "RiskLevel",
    "ProtectionStatus",
    "ThreatCategory",
    "ComplianceFramework",
    "RiskCategory",
    "ThreatSeverity",
    "RiskTimeframe",
    "MarketSegment",
    "RecommendationType",
    "Priority",
    "ImplementationComplexity",
    "ROICategory",
    "IndustrySegment",
    "ThreatType",
    "ThreatSource",
    "ThreatStatus",
    "DetectionMethod",
    
    # Additional components
    "ProtectionStrategies",
    "ComplianceChecker",
    "ProtectionMetrics",
    "AlertManager",
    "PolicyEngine",
    "AdvisoryOrchestrator",
    "FingerprintingIntegration",
    "ContentSurveillance"
]
from .policy_engine import PolicyEngine
from .fingerprinting_integration import FingerprintingIntegration
from .content_surveillance import ContentSurveillance
from .index import ProtectionAdvisorIndex

__all__ = [
    "ProtectionAdvisorCore",
    "RiskAnalyzer",
    "RecommendationEngine", 
    "ProtectionStrategies",
    "ThreatDetector",
    "ComplianceChecker",
    "AdvisoryOrchestrator",
    "ProtectionMetrics",
    "AlertManager",
    "PolicyEngine",
    "FingerprintingIntegration",
    "ContentSurveillance",
    "ProtectionAdvisorIndex"
]

__version__ = "3.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
