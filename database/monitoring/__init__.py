"""Database Monitoring Module - Enterprise Grade Database Intelligence

This module provides comprehensive database monitoring, performance tracking, and intelligent alerting
for the IA Influencer Agent + Content Protection Platform. Features real-time metrics collection,
AI-powered query optimization, predictive capacity planning, automated performance tuning, and
specialized monitoring for content processing pipelines and monetization performance.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

⚠️  AVERTISSEMENT STRICT - PROPRIÉTÉ INTELLECTUELLE ⚠️
Toute utilisation, modification ou distribution non autorisée de ce code est strictement interdite.
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute violation sera poursuivie selon les lois en vigueur.
"""
from .performance_monitor import DatabasePerformanceMonitor
from .query_analyzer import QueryAnalyzer, QueryOptimizer, ExecutionPlanAnalyzer
from .connection_monitor import ConnectionMonitor, ConnectionPoolManager
from .metrics_collector import MetricsCollector, TimeSeriesMetrics, RealTimeMetrics
from .alert_manager import DatabaseAlertManager, EscalationManager, NotificationRouter
from .health_checker import DatabaseHealthChecker, HealthScoreCalculator, DiagnosticsEngine
from .slow_query_detector import SlowQueryDetector, QueryPatternAnalyzer, PerformanceProfiler
from .resource_monitor import ResourceMonitor, CapacityPlanner, SystemResourceTracker
from .backup_monitor import BackupMonitor, ReplicationHealthChecker, DataIntegrityValidator
from .security_monitor import DatabaseSecurityMonitor, AccessPatternAnalyzer, ThreatDetector
from .compliance_monitor import ComplianceMonitor, AuditTrail, DataGovernanceTracker
from .cost_monitor import DatabaseCostMonitor, ResourceOptimizer, CostAnalyzer
from .ai_insights import DatabaseAIInsights, PredictiveAnalyzer, AnomalyDetector
from .content_pipeline_monitor import ContentPipelineMonitor, ContentType, PipelineStage, PipelineStatus
from .monetization_performance_monitor import MonetizationPerformanceMonitor, RevenueSource, MonetizationStage
from .index import create_monitoring_index

__all__ = [
    "DatabasePerformanceMonitor",
    "QueryAnalyzer",
    "QueryOptimizer", 
    "ExecutionPlanAnalyzer",
    "ConnectionMonitor",
    "ConnectionPoolManager",
    "MetricsCollector",
    "TimeSeriesMetrics",
    "RealTimeMetrics",
    "DatabaseAlertManager",
    "EscalationManager",
    "NotificationRouter",
    "DatabaseHealthChecker",
    "HealthScoreCalculator",
    "DiagnosticsEngine",
    "SlowQueryDetector",
    "QueryPatternAnalyzer",
    "PerformanceProfiler",
    "ResourceMonitor",
    "CapacityPlanner",
    "SystemResourceTracker",
    "BackupMonitor",
    "ReplicationHealthChecker", 
    "DataIntegrityValidator",
    "DatabaseSecurityMonitor",
    "AccessPatternAnalyzer",
    "ThreatDetector",
    "ComplianceMonitor",
    "AuditTrail",
    "DataGovernanceTracker",
    "DatabaseCostMonitor",
    "ResourceOptimizer",
    "CostAnalyzer",
    "DatabaseAIInsights",
    "PredictiveAnalyzer",
    "AnomalyDetector",
    "ContentPipelineMonitor",
    "ContentType",
    "PipelineStage", 
    "PipelineStatus",
    "MonetizationPerformanceMonitor",
    "RevenueSource",
    "MonetizationStage",
    "create_monitoring_index"
]

__version__ = "3.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__team__ = "Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer"
