"""Intelligence Monitoring Module
===============================

Comprehensive Creator Economy Intelligence Monitoring System for Ainflue platform.
Provides enterprise-grade intelligence monitoring capabilities including:

- Creator Economy Intelligence Orchestration
- Artificial Intelligence Monitoring Hub
- Machine Learning Intelligence Engine
- Business Intelligence System
- Predictive Analytics and Forecasting
- Creator Performance Intelligence
- Collaboration Intelligence Matching
- Monetization Intelligence Optimization

This module implements sophisticated intelligence monitoring with AI/ML-powered
analytics for the Creator Economy ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates provided
- Team technical training included
"""

# Core Intelligence Orchestrator
from .index import (
    IntelligenceOrchestrator,
    CreatorType,
    IntelligenceStatus,
    IntelligenceConfig,
    CreatorIntelligenceMetrics,
    IntelligenceComponent,
    create_intelligence_orchestrator
)

# Creator Economy Intelligence Orchestrator
from .creator_economy_intelligence_orchestrator import (
    CreatorEconomyIntelligenceOrchestrator,
    CreatorTier,
    CreatorEconomyMetricType,
    CollaborationType,
    CreatorProfile,
    CollaborationOpportunity,
    RevenueOptimizationStrategy
)

# Artificial Intelligence Monitoring Hub
from .artificial_intelligence_monitoring_hub import (
    ArtificialIntelligenceMonitoringHub,
    AIModelType,
    AIPerformanceMetric,
    AIHealthStatus,
    AIModelMetrics,
    AIUsageAnalytics,
    AIOptimizationRecommendation
)

# Machine Learning Intelligence Engine
from .machine_learning_intelligence_engine import (
    MachineLearningIntelligenceEngine,
    MLModelCategory,
    MLTaskType,
    MLModelStatus,
    MLModelConfiguration,
    MLTrainingMetrics,
    MLPredictionResult,
    CreatorMLProfile
)

# Business Intelligence System (existing)
from .business_intelligence_system import (
    BusinessMonitor,
    BusinessMetric
)

# Module version and metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."

# Main exports for Creator Economy Intelligence
__all__ = [
    # Core Intelligence Orchestrator
    'IntelligenceOrchestrator',
    'CreatorType',
    'IntelligenceStatus',
    'IntelligenceConfig',
    'CreatorIntelligenceMetrics',
    'IntelligenceComponent',
    'create_intelligence_orchestrator',
    
    # Creator Economy Intelligence
    'CreatorEconomyIntelligenceOrchestrator',
    'CreatorTier',
    'CreatorEconomyMetricType',
    'CollaborationType',
    'CreatorProfile',
    'CollaborationOpportunity',
    'RevenueOptimizationStrategy',
    
    # AI Monitoring Hub
    'ArtificialIntelligenceMonitoringHub',
    'AIModelType',
    'AIPerformanceMetric',
    'AIHealthStatus',
    'AIModelMetrics',
    'AIUsageAnalytics',
    'AIOptimizationRecommendation',
    
    # ML Intelligence Engine
    'MachineLearningIntelligenceEngine',
    'MLModelCategory',
    'MLTaskType',
    'MLModelStatus',
    'MLModelConfiguration',
    'MLTrainingMetrics',
    'MLPredictionResult',
    'CreatorMLProfile',
    
    # Business Intelligence (existing)
    'BusinessMonitor',
    'BusinessMetric',
    
    # Module metadata
    '__version__',
    '__author__',
    '__email__',
    '__copyright__'
]