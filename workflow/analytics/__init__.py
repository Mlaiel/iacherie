"""Analytics Workflows Module - Advanced Data Analytics for Ainflue Platform.

This module provides comprehensive analytics workflow orchestration including performance tracking,
engagement analysis, revenue analytics, user behavior analysis, and predictive insights
for multi-platform content creators and influencers.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Ainflue Platform. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime
from dataclasses import dataclass
import asyncio

# Core Analytics Workflow Classes
from .performance_tracking_workflow import PerformanceTrackingWorkflow, PerformanceMetrics, TrackingResult
from .engagement_analysis_workflow import EngagementAnalysisWorkflow, EngagementMetrics, AnalysisResult
from .revenue_analytics_workflow import RevenueAnalyticsWorkflow, RevenueMetrics, MonetizationInsights
from .user_behavior_workflow import UserBehaviorWorkflow, BehaviorMetrics, UserInsights
from .content_performance_workflow import ContentPerformanceWorkflow, ContentMetrics, PerformanceReport
from .viral_detection_workflow import ViralDetectionWorkflow, ViralMetrics, ViralityScore
from .trend_analysis_workflow import TrendAnalysisWorkflow, TrendMetrics, TrendInsights
from .competitive_intelligence_workflow import CompetitiveIntelligenceWorkflow, CompetitorMetrics, MarketAnalysis
from .predictive_analytics_workflow import PredictiveAnalyticsWorkflow, PredictiveModels, ForecastResults
from .cohort_analysis_workflow import CohortAnalysisWorkflow, CohortMetrics, RetentionAnalysis
from .attribution_modeling_workflow import AttributionModelingWorkflow, AttributionMetrics, ConversionPaths
from .real_time_insights_workflow import RealTimeInsightsWorkflow, RealTimeMetrics, LiveInsights
from .reporting_automation_workflow import ReportingAutomationWorkflow, ReportTemplates, AutomatedReports


class AnalyticsWorkflowType(Enum):
    """Analytics workflow types for comprehensive data analysis."""
    PERFORMANCE_TRACKING = "performance_tracking"
    ENGAGEMENT_ANALYSIS = "engagement_analysis"
    REVENUE_ANALYTICS = "revenue_analytics"
    USER_BEHAVIOR = "user_behavior"
    CONTENT_PERFORMANCE = "content_performance"
    VIRAL_DETECTION = "viral_detection"
    TREND_ANALYSIS = "trend_analysis"
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"
    PREDICTIVE_ANALYTICS = "predictive_analytics"
    COHORT_ANALYSIS = "cohort_analysis"
    ATTRIBUTION_MODELING = "attribution_modeling"
    REAL_TIME_INSIGHTS = "real_time_insights"
    REPORTING_AUTOMATION = "reporting_automation"


@dataclass
class AnalyticsConfig:
    """Configuration for analytics workflows."""
    tracking_interval: int = 3600  # 1 hour
    data_retention_days: int = 365
    real_time_enabled: bool = True
    predictive_models_enabled: bool = True
    competitive_tracking_enabled: bool = True
    automated_reporting: bool = True


class AnalyticsOrchestrator:
    """
    Master orchestrator for all analytics workflows.
    
    Provides unified interface for managing and coordinating all analytics
    workflows including performance tracking, engagement analysis, revenue analytics,
    and predictive insights.
    """
    
    def __init__(self, config: AnalyticsConfig = None):
        """Initialize analytics orchestrator with configuration."""
        self.config = config or AnalyticsConfig()
        self.workflows = {}
        self._initialize_workflows()
    
    def _initialize_workflows(self):
        """Initialize all analytics workflow instances."""
        self.workflows = {
            AnalyticsWorkflowType.PERFORMANCE_TRACKING: PerformanceTrackingWorkflow(),
            AnalyticsWorkflowType.ENGAGEMENT_ANALYSIS: EngagementAnalysisWorkflow(),
            AnalyticsWorkflowType.REVENUE_ANALYTICS: RevenueAnalyticsWorkflow(),
            AnalyticsWorkflowType.USER_BEHAVIOR: UserBehaviorWorkflow(),
            AnalyticsWorkflowType.CONTENT_PERFORMANCE: ContentPerformanceWorkflow(),
            AnalyticsWorkflowType.VIRAL_DETECTION: ViralDetectionWorkflow(),
            AnalyticsWorkflowType.TREND_ANALYSIS: TrendAnalysisWorkflow(),
            AnalyticsWorkflowType.COMPETITIVE_INTELLIGENCE: CompetitiveIntelligenceWorkflow(),
            AnalyticsWorkflowType.PREDICTIVE_ANALYTICS: PredictiveAnalyticsWorkflow(),
            AnalyticsWorkflowType.COHORT_ANALYSIS: CohortAnalysisWorkflow(),
            AnalyticsWorkflowType.ATTRIBUTION_MODELING: AttributionModelingWorkflow(),
            AnalyticsWorkflowType.REAL_TIME_INSIGHTS: RealTimeInsightsWorkflow(),
            AnalyticsWorkflowType.REPORTING_AUTOMATION: ReportingAutomationWorkflow()
        }
    
    async def execute_workflow(
        self, 
        workflow_type: AnalyticsWorkflowType,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute specific analytics workflow with parameters."""
        
        if workflow_type not in self.workflows:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
        
        workflow = self.workflows[workflow_type]
        
        # Execute workflow based on type
        if workflow_type == AnalyticsWorkflowType.PERFORMANCE_TRACKING:
            return await workflow.track_performance(**parameters)
        elif workflow_type == AnalyticsWorkflowType.ENGAGEMENT_ANALYSIS:
            return await workflow.analyze_engagement(**parameters)
        elif workflow_type == AnalyticsWorkflowType.REVENUE_ANALYTICS:
            return await workflow.analyze_revenue(**parameters)
        # Add more workflow executions as needed
        
        return {"status": "executed", "workflow": workflow_type.value}
    
    async def get_comprehensive_analytics(
        self, 
        user_id: str, 
        time_period: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive analytics across all workflows for a user."""
        
        results = {}
        
        # Execute all relevant workflows
        for workflow_type, workflow in self.workflows.items():
            try:
                if hasattr(workflow, 'get_user_analytics'):
                    results[workflow_type.value] = await workflow.get_user_analytics(
                        user_id, time_period
                    )
            except Exception as e:
                results[workflow_type.value] = {"error": str(e)}
        
        return {
            "user_id": user_id,
            "time_period_days": time_period,
            "analytics": results,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def get_workflow(self, workflow_type: AnalyticsWorkflowType):
        """Get specific workflow instance."""
        return self.workflows.get(workflow_type)


# Workflow factory function
def create_analytics_workflow(workflow_type: AnalyticsWorkflowType):
    """Factory function to create specific analytics workflow."""
    workflow_classes = {
        AnalyticsWorkflowType.PERFORMANCE_TRACKING: PerformanceTrackingWorkflow,
        AnalyticsWorkflowType.ENGAGEMENT_ANALYSIS: EngagementAnalysisWorkflow,
        AnalyticsWorkflowType.REVENUE_ANALYTICS: RevenueAnalyticsWorkflow,
        AnalyticsWorkflowType.USER_BEHAVIOR: UserBehaviorWorkflow,
        AnalyticsWorkflowType.CONTENT_PERFORMANCE: ContentPerformanceWorkflow,
        AnalyticsWorkflowType.VIRAL_DETECTION: ViralDetectionWorkflow,
        AnalyticsWorkflowType.TREND_ANALYSIS: TrendAnalysisWorkflow,
        AnalyticsWorkflowType.COMPETITIVE_INTELLIGENCE: CompetitiveIntelligenceWorkflow,
        AnalyticsWorkflowType.PREDICTIVE_ANALYTICS: PredictiveAnalyticsWorkflow,
        AnalyticsWorkflowType.COHORT_ANALYSIS: CohortAnalysisWorkflow,
        AnalyticsWorkflowType.ATTRIBUTION_MODELING: AttributionModelingWorkflow,
        AnalyticsWorkflowType.REAL_TIME_INSIGHTS: RealTimeInsightsWorkflow,
        AnalyticsWorkflowType.REPORTING_AUTOMATION: ReportingAutomationWorkflow
    }
    
    workflow_class = workflow_classes.get(workflow_type)
    if not workflow_class:
        raise ValueError(f"Unknown workflow type: {workflow_type}")
    
    return workflow_class()


# Export main classes and functions
__all__ = [
    # Core orchestrator
    'AnalyticsOrchestrator',
    'AnalyticsConfig',
    'AnalyticsWorkflowType',
    
    # Workflow classes
    'PerformanceTrackingWorkflow',
    'EngagementAnalysisWorkflow', 
    'RevenueAnalyticsWorkflow',
    'UserBehaviorWorkflow',
    'ContentPerformanceWorkflow',
    'ViralDetectionWorkflow',
    'TrendAnalysisWorkflow',
    'CompetitiveIntelligenceWorkflow',
    'PredictiveAnalyticsWorkflow',
    'CohortAnalysisWorkflow',
    'AttributionModelingWorkflow',
    'RealTimeInsightsWorkflow',
    'ReportingAutomationWorkflow',
    
    # Data classes
    'PerformanceMetrics',
    'EngagementMetrics',
    'RevenueMetrics',
    'BehaviorMetrics',
    'ContentMetrics',
    'ViralMetrics',
    'TrendMetrics',
    'CompetitorMetrics',
    'PredictiveModels',
    'CohortMetrics',
    'AttributionMetrics',
    'RealTimeMetrics',
    'ReportTemplates',
    
    # Factory function
    'create_analytics_workflow'
]


# Module metadata
__version__ = "3.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Advanced Analytics Workflows for Ainflue Creator Platform"