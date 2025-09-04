"""
Backend AI Module - Consolidated AI Agents System
================================================

This module provides a consolidated interface to all AI agents in the Ainflue platform.
Organizes 53+ specialized AI agents into 4 manageable files for improved maintainability.

Consolidation Structure:
- core_business_agents.py (20 agents) - Business operations and strategy
- content_agents.py (15 agents) - Content creation and processing  
- technical_agents.py (18 agents) - Infrastructure and monitoring
- personality.py (53+ agents) - Domain expert personalities

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
from .personality import (
    PersonalityAgentOrchestrator,
    PersonalityDomain,
    PersonalityStyle,
    ContentGenerationRequest,
    PersonalityResponse,
    FashionExpertAgent,
    FitnessCoachAgent,
    TechReviewerAgent,
    FoodCriticAgent,
    TravelGuideAgent,
    GamingExpertAgent,
    MusicCuratorAgent,
    BeautyGuruAgent,
    BusinessConsultantAgent,
    ComedianAgent
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Core Agent System
    "AgentRegistry",
    "get_agent", 
    "list_agents",
    
    # Agent Categories (4 consolidated files)
    "CoreBusinessAgents",
    "ContentAgents",
    "TechnicalAgents",
    "PersonalityAgentOrchestrator",
    
    # Personality Agents
    "PersonalityDomain",
    "PersonalityStyle",
    "ContentGenerationRequest",
    "PersonalityResponse",
    "FashionExpertAgent",
    "FitnessCoachAgent",
    "TechReviewerAgent",
    "FoodCriticAgent",
    "TravelGuideAgent",
    "GamingExpertAgent",
    "MusicCuratorAgent",
    "BeautyGuruAgent",
    "BusinessConsultantAgent",
    "ComedianAgent"
]