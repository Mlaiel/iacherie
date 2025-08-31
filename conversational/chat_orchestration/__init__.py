"""Chat Orchestration Module - Enterprise conversational AI orchestration
======================================================================

Advanced chat orchestration capabilities for multi-format content creators 
with integrated content protection, monetization intelligence, real-time
analytics, fingerprinting, and enterprise monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are proprietary intellectual property of Fahed Mlaiel.
Unauthorized copying, modification, distribution, or use without explicit written
permission is strictly prohibited and will result in legal action.
"""# Core chat orchestration components
from .chat_manager import ChatManager
from .conversation_router import ConversationRouter
from .message_processor import MessageProcessor
from .session_controller import SessionController
from .response_generator import ResponseGenerator
from .context_analyzer import ContextAnalyzer
from .intent_classifier import IntentClassifier
from .chat_analytics import ChatAnalytics

# Advanced enterprise modules
from .content_fingerprinting import (
    EnterpriseContentFingerprinting,
    ContentFingerprint,
    SimilarityMatch,
    FingerprintingResult,
    ContentType,
    FingerprintAlgorithm
)
from .advanced_content_protection import (
    EnterpriseContentProtection,
    ContentThreat,
    ProtectionRule,
    LegalDocument,
    ProtectionReport,
    ProtectionLevel,
    ThreatSeverity,
    ProtectionAction
)
from .enterprise_monitoring_engine import (
    EnterpriseMonitoringEngine,
    MonitoringEvent,
    AlertRule,
    SystemHealth,
    CreatorInsights as MonitoringCreatorInsights,
    MonitoringType,
    AlertSeverity,
    EventType
)
from .realtime_creator_analytics import (
    RealTimeCreatorAnalytics,
    AnalyticsDataPoint,
    EngagementMetrics,
    AudienceMetrics,
    RevenueMetrics,
    ContentMetrics,
    CompetitorAnalysis,
    CreatorInsights,
    RealTimeAlert,
    AnalyticsMetricType,
    CreatorCategory
)

# Backward compatibility aliases
ContentFingerprinting = EnterpriseContentFingerprinting
ContentProtection = EnterpriseContentProtection
MonitoringEngine = EnterpriseMonitoringEngine
CreatorAnalytics = RealTimeCreatorAnalytics

__all__ = [
    # Core components
    'ChatManager',
    'ConversationRouter', 
    'MessageProcessor',
    'SessionController',
    'ResponseGenerator',
    'ContextAnalyzer',
    'IntentClassifier',
    'ChatAnalytics',
    
    # Enterprise modules
    'EnterpriseContentFingerprinting',
    'EnterpriseContentProtection',
    'EnterpriseMonitoringEngine',
    'RealTimeCreatorAnalytics',
    
    # Data structures
    'ContentFingerprint',
    'SimilarityMatch',
    'FingerprintingResult',
    'ContentThreat',
    'ProtectionRule',
    'LegalDocument',
    'ProtectionReport',
    'MonitoringEvent',
    'AlertRule',
    'SystemHealth',
    'AnalyticsDataPoint',
    'EngagementMetrics',
    'AudienceMetrics',
    'RevenueMetrics',
    'ContentMetrics',
    'CompetitorAnalysis',
    'CreatorInsights',
    'RealTimeAlert',
    
    # Enums
    'ContentType',
    'FingerprintAlgorithm',
    'ProtectionLevel',
    'ThreatSeverity',
    'ProtectionAction',
    'MonitoringType',
    'AlertSeverity',
    'EventType',
    'AnalyticsMetricType',
    'CreatorCategory',
    
    # Backward compatibility
    'ContentFingerprinting',
    'ContentProtection',
    'MonitoringEngine',
    'CreatorAnalytics'
]

# Module version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise chat orchestration with advanced content protection and analytics"

from .chat_manager import ChatManager
from .conversation_router import ConversationRouter
from .message_processor import MessageProcessor
from .session_controller import SessionController
from .response_generator import ResponseGenerator
from .context_analyzer import ContextAnalyzer
from .intent_classifier import IntentClassifier
from .chat_analytics import ChatAnalytics

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    "ChatManager",
    "ConversationRouter", 
    "MessageProcessor",
    "SessionController",
    "ResponseGenerator",
    "ContextAnalyzer",
    "IntentClassifier",
    "ChatAnalytics"
]
