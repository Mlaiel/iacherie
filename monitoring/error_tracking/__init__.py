"""
Error Tracking Module for Ainflue Creator Economy Platform
Enterprise-grade error tracking and reporting system with Creator Economy intelligence

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

# Core error tracking components
from .sentry_integration import SentryErrorTracker, ErrorContext, capture_business_error, capture_ai_processing_error
from .error_aggregator import ErrorAggregator, ErrorEvent, ErrorStatistics, error_aggregator
from .error_analyzer import ErrorAnalyzer, ErrorPattern, ErrorTrend, error_analyzer

# Main orchestrator and entry point
from .index import (
    ErrorTrackingOrchestrator, 
    CreatorErrorContext,
    ErrorTrackingConfiguration,
    CreatorTier,
    ErrorTrackingMode,
    orchestrator,
    track_creator_error,
    get_creator_dashboard,
    get_system_dashboard
)

# Creator Economy specialized components
from .creator_economy_error_intelligence import (
    CreatorEconomyErrorIntelligence,
    CreatorErrorIntelligence,
    CreatorTierIntelligence,
    CreatorErrorCategory,
    CreatorSpecialization,
    creator_intelligence
)

from .ai_processing_error_monitoring_engine import (
    AIProcessingErrorMonitoringEngine,
    AIErrorEvent,
    AIModelType,
    AIProcessingStage,
    AIErrorSeverity,
    ai_monitoring_engine
)

from .creator_workflow_error_tracker import (
    CreatorWorkflowErrorTracker,
    WorkflowErrorEvent,
    WorkflowState,
    CreatorWorkflowStage,
    WorkflowErrorType,
    WorkflowPriority,
    workflow_tracker
)

from .multi_format_content_error_analyzer import (
    MultiFormatContentErrorAnalyzer,
    ContentErrorEvent,
    ContentFormat,
    ContentProcessingStage,
    ContentErrorSeverity,
    content_analyzer
)

__all__ = [
    # Core components
    'SentryErrorTracker',
    'ErrorContext',
    'ErrorAggregator', 
    'ErrorAnalyzer',
    'ErrorEvent',
    'ErrorStatistics',
    'ErrorPattern',
    'ErrorTrend',
    'capture_business_error',
    'capture_ai_processing_error',
    'error_aggregator',
    'error_analyzer',
    
    # Main orchestrator
    'ErrorTrackingOrchestrator',
    'CreatorErrorContext',
    'ErrorTrackingConfiguration',
    'CreatorTier',
    'ErrorTrackingMode',
    'orchestrator',
    'track_creator_error',
    'get_creator_dashboard',
    'get_system_dashboard',
    
    # Creator Economy Intelligence
    'CreatorEconomyErrorIntelligence',
    'CreatorErrorIntelligence',
    'CreatorTierIntelligence',
    'CreatorErrorCategory',
    'CreatorSpecialization',
    'creator_intelligence',
    
    # AI Processing Monitoring
    'AIProcessingErrorMonitoringEngine',
    'AIErrorEvent',
    'AIModelType',
    'AIProcessingStage',
    'AIErrorSeverity',
    'ai_monitoring_engine',
    
    # Workflow Tracking
    'CreatorWorkflowErrorTracker',
    'WorkflowErrorEvent',
    'WorkflowState',
    'CreatorWorkflowStage',
    'WorkflowErrorType',
    'WorkflowPriority',
    'workflow_tracker',
    
    # Content Analysis
    'MultiFormatContentErrorAnalyzer',
    'ContentErrorEvent',
    'ContentFormat',
    'ContentProcessingStage',
    'ContentErrorSeverity',
    'content_analyzer'
]