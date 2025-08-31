"""Enterprise Creator Collaboration Matching System

Advanced AI-powered matching engine for creator collaborations with comprehensive
business intelligence, revenue optimization, and enterprise-grade security.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This module contains proprietary algorithms and business logic developed
by Fahed Mlaiel. Unauthorized use, reproduction, or distribution is prohibited.

Team Specialties:
- AI/ML Engineering: Advanced neural networks and ensemble learning
- Business Intelligence: Revenue optimization and risk assessment
- Security Engineering: Military-grade encryption and compliance
- Performance Engineering: High-throughput distributed systems
- Data Science: Predictive analytics and behavioral modeling
"""
from .scoring import (
    MatchingScoringService,
    ScoreComponent,
    MLEnsembleScorer,
    BusinessIntelligenceScorer,
    SecurityAwareScorer
)

from .engine import (
    MatchingEngine,
    MatchingResult,
    AdvancedMatchingStrategy,
    AIOptimizedMatcher,
    CollaborativeFilteringMatcher,
    BusinessIntelligenceMatcher
)

from .preferences import (
    UserPreferences,
    PreferenceManager,
    AIPreferenceLearning,
    BehavioralAnalyzer,
    PreferenceEvolutionTracker
)

from .compatibility import (
    CompatibilityAnalyzer,
    CompatibilityResult,
    MultiDimensionalCompatibility,
    AdvancedCompatibilityMetrics,
    PredictiveCompatibilityAssessment
)

from .recommendation import (
    RecommendationEngine,
    Recommendation,
    NeuralRecommendationSystem,
    CollaborativeRecommendationFilter,
    BusinessOptimizedRecommendations
)

from .criteria import (
    MatchingCriteria,
    CriteriaBuilder,
    AdvancedCriteriaEngine,
    IntelligentCriteriaOptimizer,
    DynamicCriteriaAdjustment
)

from .validator import (
    MatchingValidator,
    ValidationResult,
    ComprehensiveMatchingValidator,
    BusinessLogicValidator,
    SecurityComplianceValidator
)

from .processor import (
    MatchingProcessor,
    ProcessingResult,
    DistributedMatchingProcessor,
    ParallelProcessingEngine,
    OptimizedWorkflowProcessor
)

from .workflow import (
    MatchingWorkflow,
    WorkflowStep,
    WorkflowResult,
    EnterpriseMatchingWorkflow,
    AdaptiveWorkflowEngine,
    IntelligentWorkflowOptimizer
)

from .index import (
    MatchingService,
    ServiceHealth,
    get_matching_service
)

from .config import (
    MatchingModuleConfig,
    ConfigurationManager,
    EnvironmentType,
    AIModelType,
    get_config_manager,
    get_config,
    update_config
)

from .metrics import (
    MonitoringService,
    MetricsCollector,
    PerformanceMonitor,
    AlertManager,
    BusinessMetricsCollector,
    PerformanceStats,
    BusinessMetrics,
    Alert,
    AlertSeverity,
    timer_decorator,
    counter_decorator,
    get_monitoring_service,
    get_metrics_collector,
    get_performance_monitor,
    get_alert_manager,
    get_business_metrics
)

# Version information
__version__ = "3.2.1"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "2025 Fahed Mlaiel. All rights reserved."

# Module metadata
__all__ = [
    # Core matching components
    "MatchingScoringService", "ScoreComponent", "MLEnsembleScorer",
    "BusinessIntelligenceScorer", "SecurityAwareScorer",
    
    # Matching engine
    "MatchingEngine", "MatchingResult", "AdvancedMatchingStrategy",
    "AIOptimizedMatcher", "CollaborativeFilteringMatcher", "BusinessIntelligenceMatcher",
    
    # User preferences
    "UserPreferences", "PreferenceManager", "AIPreferenceLearning",
    "BehavioralAnalyzer", "PreferenceEvolutionTracker",
    
    # Compatibility analysis
    "CompatibilityAnalyzer", "CompatibilityResult", "MultiDimensionalCompatibility",
    "AdvancedCompatibilityMetrics", "PredictiveCompatibilityAssessment",
    
    # Recommendation system
    "RecommendationEngine", "Recommendation", "NeuralRecommendationSystem",
    "CollaborativeRecommendationFilter", "BusinessOptimizedRecommendations",
    
    # Matching criteria
    "MatchingCriteria", "CriteriaBuilder", "AdvancedCriteriaEngine",
    "IntelligentCriteriaOptimizer", "DynamicCriteriaAdjustment",
    
    # Validation
    "MatchingValidator", "ValidationResult", "ComprehensiveMatchingValidator",
    "BusinessLogicValidator", "SecurityComplianceValidator",
    
    # Processing
    "MatchingProcessor", "ProcessingResult", "DistributedMatchingProcessor",
    "ParallelProcessingEngine", "OptimizedWorkflowProcessor",
    
    # Workflow management
    "MatchingWorkflow", "WorkflowStep", "WorkflowResult", "EnterpriseMatchingWorkflow",
    "AdaptiveWorkflowEngine", "IntelligentWorkflowOptimizer",
    
    # Service orchestration
    "MatchingService", "ServiceHealth", "get_matching_service",
    
    # Configuration management
    "MatchingModuleConfig", "ConfigurationManager", "EnvironmentType", "AIModelType",
    "get_config_manager", "get_config", "update_config",
    
    # Monitoring and metrics
    "MonitoringService", "MetricsCollector", "PerformanceMonitor", "AlertManager",
    "BusinessMetricsCollector", "PerformanceStats", "BusinessMetrics", "Alert",
    "AlertSeverity", "timer_decorator", "counter_decorator", "get_monitoring_service",
    "get_metrics_collector", "get_performance_monitor", "get_alert_manager", "get_business_metrics",
]
