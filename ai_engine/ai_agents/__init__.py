"""AI Agents Module - IA Influencer Agent Platform
Architecture consolidée avec agents métier regroupés

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE
Cette architecture est la propriété exclusive de Fahed Mlaiel.
Contact: mlaiel@live.de
"""# Agent de Base - Core Framework
from .base_agent import (
    BaseAIAgent,
    AgentCapability, 
    AgentStatus,
    AgentConfiguration,
    AgentTask,
    AgentMetrics,
    AgentRegistry,
    AgentPriority,
    agent_lifecycle,
    AgentFactory,
    create_agent_config,
    deploy_agent
)

__all__ = [
    # Core Framework
    "BaseAIAgent",
    "AgentCapability", 
    "AgentStatus",
    "AgentConfiguration",
    "AgentTask",
    "AgentMetrics",
    "AgentRegistry",
    "AgentPriority",
    "agent_lifecycle",
    "AgentFactory",
    "create_agent_config",
    "deploy_agent"
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
        "Growth hacking strategies"
    ],
    "supported_platforms": [
        "YouTube", "TikTok", "Instagram", "Twitter", "Facebook",
        "LinkedIn", "Snapchat", "Twitch", "Discord", "Clubhouse"
    ]
}

def get_module_info():
    """Get module information"""    return MODULE_INFO.copy()

def get_default_config():
    """Get default configuration"""    return DEFAULT_CONFIG.copy()