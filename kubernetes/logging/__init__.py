"""
IA Influencer Agent - Logging Deployment Module
Enterprise logging infrastructure and management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit 
written permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

Team Expertise:
- Lead Developer & AI Architect: Fahed Mlaiel
- Backend Senior Engineer: Advanced Python/FastAPI
- ML Engineer: AI/ML Algorithms & Analytics
- DevOps Engineer: Infrastructure & Deployment
- Database Administrator: Performance & Optimization
- Security Specialist: Enterprise Security & Compliance
- Microservices Architect: Distributed Systems
- IA Prompt Engineer: Advanced AI Integration
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

from .log_aggregator import (
    LogAggregator,
    LogEntry,
    LogLevel,
    LogFormat,
    LogProcessor,
    LogBuffer,
    LogDestination
)
from .elasticsearch_manager import (
    ElasticsearchManager,
    ElasticsearchConfig,
    IndexStrategy,
    IndexTemplate,
    QueryBuilder
)
from .fluentd_manager import (
    FluentdManager,
    FluentdConfig,
    FluentdInputType,
    FluentdOutputType,
    FluentdFilterType,
    FluentdConfigBuilder,
    FluentdClient
)
from .log_retention import (
    LogRetentionManager,
    RetentionPolicy,
    RetentionPeriod,
    CompressionType,
    StorageTier,
    LogCompressor,
    S3Archiver
)
from .log_analytics import (
    LogAnalyticsEngine,
    LogAlert,
    LogMetric,
    AlertSeverity,
    TrendDirection,
    AnomalyDetector,
    LogPatternAnalyzer,
    TrendAnalyzer
)
from .log_monitoring import (
    LogMonitoringService,
    MonitoringRule,
    NotificationChannel,
    NotificationConfig,
    NotificationSender,
    EmailNotificationSender,
    SlackNotificationSender,
    WebhookNotificationSender,
    TeamsNotificationSender
)

__all__ = [
    # Core aggregation
    "LogAggregator",
    "LogEntry",
    "LogLevel",
    "LogFormat",
    "LogProcessor",
    "LogBuffer",
    "LogDestination",
    
    # Elasticsearch integration
    "ElasticsearchManager",
    "ElasticsearchConfig",
    "IndexStrategy",
    "IndexTemplate",
    "QueryBuilder",
    
    # Fluentd integration
    "FluentdManager",
    "FluentdConfig",
    "FluentdInputType",
    "FluentdOutputType",
    "FluentdFilterType",
    "FluentdConfigBuilder",
    "FluentdClient",
    
    # Log retention
    "LogRetentionManager",
    "RetentionPolicy",
    "RetentionPeriod",
    "CompressionType",
    "StorageTier",
    "LogCompressor",
    "S3Archiver",
    
    # Analytics & insights
    "LogAnalyticsEngine",
    "LogAlert",
    "LogMetric",
    "AlertSeverity",
    "TrendDirection",
    "AnomalyDetector",
    "LogPatternAnalyzer",
    "TrendAnalyzer",
    
    # Real-time monitoring
    "LogMonitoringService",
    "MonitoringRule",
    "NotificationChannel",
    "NotificationConfig",
    "NotificationSender",
    "EmailNotificationSender",
    "SlackNotificationSender",
    "WebhookNotificationSender",
    "TeamsNotificationSender"
]
