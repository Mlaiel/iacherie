"""
Backend AI Module - Consolidated AI Agents System
================================================

This module provides a consolidated interface to all AI agents in the Ainflue platform.
Organizes 53+ specialized AI agents into 4 manageable files for improved maintainability.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use is strictly prohibited. Contact: mlaiel@live.de
"""

from .agent_registry import AgentRegistry, get_agent, list_agents
from .core_business_agents import CoreBusinessAgents
from .content_agents import ContentAgents  
from .technical_agents import TechnicalAgents
from .therapy import TherapyAIService, create_therapy_service
from .companion import (
    CompanionService, 
    ICompanionService,
    CompanionPersonalityType,
    ConversationContext,
    create_companion_service,
    create_friendly_companion,
    create_professional_companion,
    create_creative_companion,
    create_mentor_companion
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    "AgentRegistry",
    "get_agent", 
    "list_agents",
    "CoreBusinessAgents",
    "ContentAgents",
    "TechnicalAgents",
    "TherapyAIService",
    "create_therapy_service",
    # Companion Service - Virtual AI Companion
    "CompanionService",
    "ICompanionService",
    "CompanionPersonalityType", 
    "ConversationContext",
    "create_companion_service",
    "create_friendly_companion",
    "create_professional_companion",
    "create_creative_companion",
    "create_mentor_companion"
]