"""
AI Agents Module - IA Influencer Agent Platform
Architecture consolidée avec agents métier regroupés

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE
Cette architecture est la propriété exclusive de Fahed Mlaiel.
Contact: mlaiel@live.de
"""

# Coordinateur et Orchestrateur
from .ai_orchestrator import AIOrchestrator
from .agent_coordinator import AgentCoordinator, create_agent_coordinator

# Agents Métier Consolidés
from .analytics_agent import AnalyticsAgent
from .content_protection_agents import ContentProtectionAgents
from .monetization_agents import MonetizationAgents
from .collaboration_agents import CollaborationAgents
from .content_strategy_agents import ContentStrategyAgents
from .audience_development_agents import AudienceDevelopmentAgents
from .brand_consulting_agents import BrandConsultingAgents
from .trend_analysis_agents import TrendAnalysisAgents
from .seo_optimization_agents import SEOOptimizationAgents

# Agent de Base
from .base_agent import BaseAIAgent

# Agents Spécialisés Techniques
from .audio_specialist import AudioSpecialist
from .video_specialist import VideoSpecialist
from .image_specialist import ImageSpecialist
from .text_specialist import TextSpecialist

# Agents de Gestion
from .social_media_manager import SocialMediaManager
from .content_creator import ContentCreator
from .brand_manager import BrandManager
from .monetization_strategist import MonetizationStrategist
from .growth_hacker import GrowthHacker
from .creative_director import CreativeDirector
from .music_producer import MusicProducer
from .engagement_specialist import EngagementSpecialist
from .crisis_manager import CrisisManager
from .trend_analyzer import TrendAnalyzer

__all__ = [
    # Coordinateur Central
    "AIOrchestrator",
    "AgentCoordinator", 
    "create_agent_coordinator",
    
    # Agents Métier
    "AnalyticsAgent", 
    "ContentProtectionAgents",
    "MonetizationAgents",
    "CollaborationAgents",
    "ContentStrategyAgents",
    "AudienceDevelopmentAgents",
    "BrandConsultingAgents",
    "TrendAnalysisAgents",
    "SEOOptimizationAgents",
    
    # Agent de Base
    "BaseAIAgent",
    
    # Agents Spécialisés
    "AudioSpecialist",
    "VideoSpecialist", 
    "ImageSpecialist",
    "TextSpecialist",
    
    # Agents de Gestion
    "SocialMediaManager",
    "ContentCreator",
    "BrandManager",
    "MonetizationStrategist",
    "GrowthHacker",
    "CreativeDirector",
    "MusicProducer",
    "EngagementSpecialist",
    "CrisisManager",
    "TrendAnalyzer"
]

# Metadata du Module
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - Contact mlaiel@live.de"

# Configuration par défaut
DEFAULT_CONFIG = {
    "max_concurrent_agents": 50,
    "coordination_timeout": 300,
    "health_check_interval": 30,
    "performance_monitoring": True,
    "security_enabled": True
}

# Core AI Agents Components
from .orchestrator import AIAgentsOrchestrator
from .base_agent import (
    BaseAIAgent, 
    AgentCapability, 
    AgentStatus, 
    AgentConfiguration,
    AgentTask,
    AgentMetrics,
    AgentRegistry,
    AgentPriority,
    agent_lifecycle
)

# Content Creation Agents
from .content_creator import (
    ContentCreatorAgent,
    ContentCreationRequest,
    ContentCreationResult
)

# Social Media & Marketing Agents  
from .social_media_manager import (
    SocialMediaManagerAgent,
    SocialMediaPost,
    CrossPlatformCampaign,
    EngagementMetrics,
    PostingStrategy,
    EngagementGoal
)

# Engagement & Community Management
from .engagement_specialist import (
    EngagementSpecialistAgent,
    EngagementOptimizationRequest,
    EngagementAction,
    EngagementStrategy,
    InteractionType
)

# Analytics & Intelligence Agents
from .analytics_agent import (
    AnalyticsAgent,
    AnalyticsQuery,
    AnalyticsInsight,
    PerformanceReport,
    AnalyticsScope,
    TimeRange
)

# Specialized Domain Agents
from .audio_specialist import (
    AudioSpecialistAgent,
    AudioProcessingRequest,
    AudioProcessingResult,
    AudioMetadata,
    AudioFormat,
    AudioQuality,
    ProcessingMode
)

# Crisis Management and Growth
from .crisis_manager import CrisisManagerAgent
from .growth_hacker import GrowthHackerAgent

# Content Creation Specialists  
from .video_specialist import VideoSpecialistAgent
from .image_specialist import ImageSpecialistAgent
from .text_specialist import TextSpecialistAgent
from .music_producer import MusicProducerAgent

# Content Strategy Agents
from .content_optimizer import ContentOptimizerAgent
from .trend_analyzer import TrendAnalyzerAgent
from .audience_insights import AudienceInsightsAgent
from .brand_manager import BrandManagerAgent
from .scheduling_agent import SchedulingAgent

# Advanced AI Agents
from .conversational_ai import ConversationalAIAgent
from .creative_director import CreativeDirectorAgent
from .collaboration_coordinator import CollaborationCoordinatorAgent
from .monetization_strategist import MonetizationStrategistAgent

# Agent Communication and Workflow
from .communication import (
    AgentCommunicationHub, 
    MessageType, 
    MessagePriority,
    MessageStatus,
    AgentMessage,
    MessageHandler,
    Conversation
)

from .workflow import (
    WorkflowEngine, 
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowStep,
    WorkflowStatus,
    StepType,
    StepStatus
)

# Task Management
from .task_manager import (
    TaskManager,
    Task,
    TaskPriority,
    TaskStatus,
    TaskType,
    TaskBatch,
    ResourceConstraint
)

# System Management
from .index import (
    AIAgentsSystem,
    initialize_system,
    get_system,
    shutdown_system
)

# Configuration Management
from .config import (
    AIAgentsConfig,
    DatabaseConfig,
    RedisConfig,
    AIConfig,
    SecurityConfig,
    MonitoringConfig,
    PerformanceConfig,
    PlatformConfig,
    ConfigManager,
    get_config_manager,
    get_config,
    load_config,
    get_default_config
)

# Export all main classes and utilities
__all__ = [
    # Core framework
    "BaseAIAgent",
    "AgentCapability", 
    "AgentStatus",
    "AgentConfiguration",
    "AgentTask",
    "AgentMetrics",
    "AgentRegistry",
    "AgentPriority",
    "agent_lifecycle",
    
    # Orchestration
    "AIAgentsOrchestrator",
    
    # Specialized agents
    "ContentCreatorAgent",
    "SocialMediaManagerAgent", 
    "EngagementSpecialistAgent",
    "AnalyticsAgent",
    "AudioSpecialistAgent",
    
    # Communication system
    "AgentCommunicationHub",
    "MessageType",
    "MessagePriority", 
    "MessageStatus",
    "AgentMessage",
    "MessageHandler",
    "Conversation",
    
    # Workflow system
    "WorkflowEngine",
    "WorkflowDefinition",
    "WorkflowExecution", 
    "WorkflowStep",
    "WorkflowStatus",
    "StepType",
    "StepStatus",
    
    # Task management
    "TaskManager",
    "Task",
    "TaskPriority",
    "TaskStatus", 
    "TaskType",
    "TaskBatch",
    "ResourceConstraint",
    
    # System management
    "AIAgentsSystem",
    "initialize_system",
    "get_system", 
    "shutdown_system",
    
    # Configuration management
    "AIAgentsConfig",
    "DatabaseConfig",
    "RedisConfig",
    "AIConfig",
    "SecurityConfig",
    "MonitoringConfig",
    "PerformanceConfig",
    "PlatformConfig",
    "ConfigManager",
    "get_config_manager",
    "get_config",
    "load_config",
    "get_default_config",
    
    # Request/Response classes
    "ContentCreationRequest",
    "ContentCreationResult",
    "SocialMediaPost",
    "CrossPlatformCampaign",
    "EngagementMetrics",
    "EngagementOptimizationRequest",
    "EngagementAction",
    "AnalyticsQuery",
    "AnalyticsInsight", 
    "PerformanceReport",
    "AudioProcessingRequest",
    "AudioProcessingResult",
    "AudioMetadata",
    
    # Enums
    "PostingStrategy",
    "EngagementGoal",
    "EngagementStrategy",
    "InteractionType", 
    "AnalyticsScope",
    "TimeRange",
    "AudioFormat",
    "AudioQuality",
    "ProcessingMode"
]

# Module version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Advanced multi-agent AI system for IA Influencer platform"
from .learning import AgentLearningSystem, LearningMode, PersonalizationEngine
from .memory import MemoryManager as AgentMemorySystem, MemoryType, WorkingMemory as KnowledgeBase
from .performance import PerformanceTracker, AgentMetrics, OptimizationEngine

# Security and Compliance
from .security import AgentSecurityManager, SecurityLevel, AccessControl
from .compliance import ComplianceChecker, ComplianceRule, RegulatoryFramework

# Export version and metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary"

# Module metadata
MODULE_INFO = {
    "name": "AI Agents Management System",
    "version": __version__,
    "description": "Comprehensive AI agents orchestration and management platform",
    "capabilities": [
        "Multi-agent coordination",
        "Content creation automation",
        "Social media management",
        "Audience engagement optimization",
        "Performance analytics",
        "Music production assistance",
        "Brand management",
        "Trend analysis",
        "Crisis management",
        "Growth hacking strategies",
        "Conversational AI",
        "Creative direction",
        "Collaboration coordination",
        "Monetization strategies"
    ],
    "supported_platforms": [
        "YouTube", "TikTok", "Instagram", "Twitter", "Facebook",
        "LinkedIn", "Snapchat", "Twitch", "Discord", "Clubhouse"
    ],
    "ai_models": [
        "GPT-4", "Claude", "Gemini", "Llama", "Mistral",
        "DALL-E", "Midjourney", "Stable Diffusion",
        "Whisper", "ElevenLabs", "Mubert"
    ],
    "features": {
        "content_creation": {
            "text": ["articles", "captions", "scripts", "descriptions"],
            "audio": ["music", "voice", "sound_effects", "podcasts"],
            "video": ["editing", "generation", "thumbnails", "shorts"],
            "image": ["generation", "editing", "optimization", "branding"]
        },
        "automation": {
            "posting": "Multi-platform scheduling",
            "engagement": "Automated responses and interactions",
            "analytics": "Real-time performance tracking",
            "optimization": "AI-driven content optimization"
        },
        "intelligence": {
            "trend_analysis": "Real-time trend detection",
            "audience_insights": "Deep audience analytics",
            "performance_prediction": "AI-powered performance forecasting",
            "sentiment_analysis": "Brand sentiment monitoring"
        }
    },
    "security": {
        "encryption": "End-to-end content encryption",
        "access_control": "Role-based access management",
        "audit_logging": "Complete action audit trails",
        "compliance": "GDPR, CCPA, platform ToS compliance"
    }
}

# Available agents registry
AVAILABLE_AGENTS = {
    # Core Content Creation Agents
    "content_creator": ContentCreatorAgent,
    "social_media_manager": SocialMediaManagerAgent,
    "engagement_specialist": EngagementSpecialistAgent,
    "analytics_agent": AnalyticsAgent,
    "content_optimizer": ContentOptimizerAgent,
    
    # Intelligence & Analysis Agents
    "trend_analyzer": TrendAnalyzerAgent,
    "audience_insights": AudienceInsightsAgent,
    "brand_manager": BrandManagerAgent,
    "scheduling_agent": SchedulingAgent,
    
    # Advanced Strategy Agents
    "conversational_ai": ConversationalAIAgent,
    "creative_director": CreativeDirectorAgent,
    "collaboration_coordinator": CollaborationCoordinatorAgent,
    "monetization_strategist": MonetizationStrategistAgent,
    "crisis_manager": CrisisManagerAgent,
    "growth_hacker": GrowthHackerAgent,
    
    # Specialized Domain Agents
    "audio_specialist": AudioSpecialistAgent,
    "video_specialist": VideoSpecialistAgent, 
    "image_specialist": ImageSpecialistAgent,
    "text_specialist": TextSpecialistAgent,
    "music_producer": MusicProducerAgent,
    "content_optimizer": ContentOptimizerAgent,
    "trend_analyzer": TrendAnalyzerAgent,
    "audience_insights": AudienceInsightsAgent,
    "brand_manager": BrandManagerAgent,
    "scheduling_agent": SchedulingAgent,
    "conversational_ai": ConversationalAIAgent,
    "creative_director": CreativeDirectorAgent,
    "collaboration_coordinator": CollaborationCoordinatorAgent,
    "monetization_strategist": MonetizationStrategistAgent
}

# Agent capabilities matrix
AGENT_CAPABILITIES = {
    "content_creation": [
        "content_creator", "music_producer", "creative_director",
        "audio_specialist", "video_specialist", "image_specialist", "text_specialist"
    ],
    "social_management": [
        "social_media_manager", "engagement_specialist", "scheduling_agent",
        "brand_manager", "crisis_manager"
    ],
    "analytics_intelligence": [
        "analytics_agent", "trend_analyzer", "audience_insights",
        "performance_tracker"
    ],
    "strategy_optimization": [
        "content_optimizer", "monetization_strategist", "growth_hacker",
        "collaboration_coordinator"
    ],
    "interaction_communication": [
        "conversational_ai", "engagement_specialist", "crisis_manager"
    ]
}

# Default configurations for agent types
DEFAULT_AGENT_CONFIGS = {
    "content_creator": {
        "creativity_level": 0.8,
        "quality_threshold": 0.85,
        "content_types": ["text", "video", "image", "audio"],
        "platforms": ["all"],
        "language_support": ["en", "fr", "de", "es", "it"]
    },
    "social_media_manager": {
        "posting_frequency": "optimal",
        "engagement_strategy": "authentic",
        "platform_optimization": True,
        "hashtag_strategy": "trending_relevant",
        "cross_platform_sync": True
    },
    "analytics_agent": {
        "reporting_frequency": "daily",
        "metrics_tracking": ["engagement", "reach", "growth", "conversion"],
        "real_time_monitoring": True,
        "predictive_analytics": True,
        "competitor_analysis": True
    },
    "music_producer": {
        "genre_flexibility": 0.9,
        "collaboration_mode": True,
        "copyright_protection": True,
        "ai_generation": True,
        "human_collaboration": True
    }
}

# Agent communication protocols
COMMUNICATION_PROTOCOLS = {
    "message_types": [
        "task_assignment", "status_update", "resource_request",
        "collaboration_invite", "performance_report", "alert",
        "recommendation", "approval_request"
    ],
    "priority_levels": ["low", "medium", "high", "urgent", "critical"],
    "response_timeouts": {
        "low": 3600,      # 1 hour
        "medium": 1800,   # 30 minutes
        "high": 600,      # 10 minutes
        "urgent": 300,    # 5 minutes
        "critical": 60    # 1 minute
    }
}

# Performance metrics and KPIs
PERFORMANCE_METRICS = {
    "content_quality": [
        "engagement_rate", "sentiment_score", "virality_potential",
        "brand_alignment", "audience_resonance"
    ],
    "efficiency": [
        "task_completion_time", "resource_utilization",
        "automation_success_rate", "error_rate"
    ],
    "business_impact": [
        "follower_growth", "revenue_generation", "brand_awareness",
        "conversion_rate", "customer_satisfaction"
    ],
    "collaboration": [
        "inter_agent_efficiency", "workflow_optimization",
        "knowledge_sharing", "conflict_resolution"
    ]
}

def get_available_agents() -> dict:
    """Get dictionary of all available AI agents"""
    return AVAILABLE_AGENTS.copy()

def get_agent_capabilities(agent_type: str) -> list:
    """Get capabilities for a specific agent type"""
    for capability, agents in AGENT_CAPABILITIES.items():
        if agent_type in agents:
            return [capability]
    return []

def get_default_config(agent_type: str) -> dict:
    """Get default configuration for an agent type"""
    return DEFAULT_AGENT_CONFIGS.get(agent_type, {})

def create_agent(agent_type: str, config: dict = None):
    """Factory function to create an agent instance"""
    if agent_type not in AVAILABLE_AGENTS:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    agent_class = AVAILABLE_AGENTS[agent_type]
    agent_config = get_default_config(agent_type)
    
    if config:
        agent_config.update(config)
    
    return agent_class(config=agent_config)

# Quality assurance and compliance
__all__ = [
    # Core Classes
    "AIAgentsOrchestrator", "BaseAIAgent", "AgentCapability", "AgentStatus",
    
    # Content Agents
    "ContentCreatorAgent", "SocialMediaManagerAgent", "EngagementSpecialistAgent",
    "AnalyticsAgent", "MusicProducerAgent", "ContentOptimizerAgent",
    
    # Intelligence Agents
    "TrendAnalyzerAgent", "AudienceInsightsAgent", "BrandManagerAgent",
    "SchedulingAgent",
    
    # Advanced Agents
    "ConversationalAIAgent", "CreativeDirectorAgent", "CollaborationCoordinatorAgent",
    "MonetizationStrategistAgent", "CrisisManagerAgent", "GrowthHackerAgent",
    
    # Specialized Agents
    "AudioSpecialistAgent", "VideoSpecialistAgent", "ImageSpecialistAgent",
    "TextSpecialistAgent",
    
    # Communication and Workflow
    "AgentCommunicationHub", "MessageType", "AgentMessage",
    "WorkflowEngine", "WorkflowStep", "WorkflowResult",
    "TaskManager", "Task", "TaskPriority", "TaskStatus",
    
    # Learning and Memory
    "AgentLearningSystem", "LearningMode", "PersonalizationEngine",
    "AgentMemorySystem", "MemoryType", "KnowledgeBase",
    
    # Performance and Security
    "PerformanceTracker", "AgentMetrics", "OptimizationEngine",
    "AgentSecurityManager", "SecurityLevel", "AccessControl",
    "ComplianceChecker", "ComplianceRule", "RegulatoryFramework",
    
    # Utility Functions
    "get_available_agents", "get_agent_capabilities", "get_default_config",
    "create_agent",
    
    # Constants
    "MODULE_INFO", "AVAILABLE_AGENTS", "AGENT_CAPABILITIES",
    "DEFAULT_AGENT_CONFIGS", "COMMUNICATION_PROTOCOLS", "PERFORMANCE_METRICS"
]
