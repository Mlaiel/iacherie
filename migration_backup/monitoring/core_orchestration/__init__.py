"""
🚀 Core Orchestration - Enterprise Monitoring Ainflue
=====================================================

Module central d'orchestration pour le système de surveillance enterprise.
Coordonne tous les agents de monitoring et fournit l'intelligence globale.

Architecture: monitoring/core_orchestration/ (NIVEAU 2)
Responsabilité: Orchestration maître et coordination intelligente

© 2025 Fahed Mlaiel - Architecture Monitoring Propriétaire Ultra-Avancée
"""

# Core monitoring hub
from .index import (
    EnterpriseMonitoringHub,
    MonitoringConfig,
    MonitoringEvent,
    MonitoringEventType,
    create_monitoring_app
)

# Creator Economy Orchestration
try:
    from .creator_economy_orchestration_engine import (
        CreatorEconomyOrchestrationEngine,
        CreatorType,
        CreatorTier,
        CreatorProfile,
        CreatorEconomyWorkflow
    )
    CREATOR_ECONOMY_AVAILABLE = True
except ImportError:
    CREATOR_ECONOMY_AVAILABLE = False

# Multi-Agent Coordination
try:
    from .multi_agent_coordination_hub import (
        MultiAgentCoordinationHub,
        AgentStatus,
        AgentCapability,
        AgentConfiguration,
        AgentTask,
        MonitoringAgent
    )
    MULTI_AGENT_AVAILABLE = True
except ImportError:
    MULTI_AGENT_AVAILABLE = False

# Intelligent Event Dispatcher
try:
    from .intelligent_event_dispatcher import (
        IntelligentEventDispatcher,
        EventPriority,
        EventPattern,
        ProcessingStrategy,
        IntelligentEvent,
        EventMetadata
    )
    EVENT_DISPATCHER_AVAILABLE = True
except ImportError:
    EVENT_DISPATCHER_AVAILABLE = False

# Real-Time Analytics Orchestrator
try:
    from .real_time_analytics_orchestrator import (
        RealTimeAnalyticsOrchestrator,
        AnalyticsScope,
        MetricType,
        AggregationFunction,
        TimeWindow,
        MetricDefinition,
        MetricValue
    )
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

# Core exports always available
__all__ = [
    'EnterpriseMonitoringHub',
    'MonitoringConfig', 
    'MonitoringEvent',
    'MonitoringEventType',
    'create_monitoring_app'
]

# Conditional exports based on availability
if CREATOR_ECONOMY_AVAILABLE:
    __all__.extend([
        'CreatorEconomyOrchestrationEngine',
        'CreatorType',
        'CreatorTier',
        'CreatorProfile',
        'CreatorEconomyWorkflow'
    ])

if MULTI_AGENT_AVAILABLE:
    __all__.extend([
        'MultiAgentCoordinationHub',
        'AgentStatus',
        'AgentCapability',
        'AgentConfiguration',
        'AgentTask',
        'MonitoringAgent'
    ])

if EVENT_DISPATCHER_AVAILABLE:
    __all__.extend([
        'IntelligentEventDispatcher',
        'EventPriority',
        'EventPattern',
        'ProcessingStrategy',
        'IntelligentEvent',
        'EventMetadata'
    ])

if ANALYTICS_AVAILABLE:
    __all__.extend([
        'RealTimeAnalyticsOrchestrator',
        'AnalyticsScope',
        'MetricType',
        'AggregationFunction',
        'TimeWindow',
        'MetricDefinition',
        'MetricValue'
    ])

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Feature availability flags
FEATURES = {
    'core_monitoring': True,
    'creator_economy_orchestration': CREATOR_ECONOMY_AVAILABLE,
    'multi_agent_coordination': MULTI_AGENT_AVAILABLE,
    'intelligent_event_dispatcher': EVENT_DISPATCHER_AVAILABLE,
    'real_time_analytics': ANALYTICS_AVAILABLE
}