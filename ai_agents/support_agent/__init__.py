"""
Support Agent Module - Ultra-Advanced AI Customer Support & Assistance System

Enterprise-grade intelligent customer support agent providing comprehensive help,
troubleshooting, onboarding assistance, and 24/7 automated customer service.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Core Features:
- Intelligent conversation handling with context awareness
- Multi-language support and translation (6 languages)
- Intent classification and automatic routing  
- Knowledge base integration with semantic search
- Automated troubleshooting and guided solutions
- Escalation management to human agents
- Real-time sentiment analysis and emotion detection
- Proactive support based on user behavior
- Advanced ticket management with SLA tracking
- Load-balanced agent pool with health monitoring
- Comprehensive analytics and performance metrics
- Enterprise-grade security and compliance
"""

from .support_agent import (
    SupportAgent,
    SupportAgentManager,
    SupportCategory,
    Priority,
    SupportChannel,
    TicketStatus,
    SupportTicket,
    ConversationMessage,
    RoundRobinLoadBalancer
)

from .conversation_flow import (
    ConversationFlowManager,
    ConversationState,
    ConversationIntent,
    ConversationContext,
    FlowTransition,
    FlowNode,
    FlowDirection
)

from .knowledge_base import (
    KnowledgeBaseManager,
    KnowledgeArticle,
    KnowledgeCategory,
    ContentType,
    ContentStatus,
    SearchQuery,
    SearchResult
)

from .escalation_manager import (
    EscalationManager,
    EscalationRequest,
    EscalationTrigger,
    EscalationPriority,
    HumanAgent,
    AgentStatus,
    AgentSpecialty,
    EscalationQueue
)

from .performance_analytics import (
    SupportAnalytics,
    PerformanceMetric,
    MetricType,
    TimeInterval,
    AnalyticsReport
)

# Version and metadata
__version__ = "2.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary"

__all__ = [
    # Core classes
    'SupportAgent',
    'SupportAgentManager',
    'SupportCategory',
    'Priority', 
    'SupportChannel',
    'TicketStatus',
    'SupportTicket',
    'ConversationMessage',
    'RoundRobinLoadBalancer',
    
    # Conversation Flow
    'ConversationFlowManager',
    'ConversationState',
    'ConversationIntent',
    'ConversationContext',
    'FlowTransition',
    'FlowNode',
    'FlowDirection',
    
    # Knowledge Base
    'KnowledgeBaseManager',
    'KnowledgeArticle',
    'KnowledgeCategory',
    'ContentType',
    'ContentStatus',
    'SearchQuery',
    'SearchResult',
    
    # Escalation Management
    'EscalationManager',
    'EscalationRequest',
    'EscalationTrigger',
    'EscalationPriority',
    'HumanAgent',
    'AgentStatus',
    'AgentSpecialty',
    'EscalationQueue',
    
    # Performance Analytics
    'SupportAnalytics',
    'PerformanceMetric',
    'MetricType',
    'TimeInterval',
    'AnalyticsReport'
]
    'SupportAgentManager', 
    'RoundRobinLoadBalancer',
    
    # Data structures
    'SupportTicket',
    'ConversationMessage',
    
    # Enums
    'SupportCategory',
    'Priority',
    'SupportChannel', 
    'TicketStatus',
    
    # Module metadata
    '__version__',
    '__author__',
    '__email__',
    '__license__'
]