"""
Backend AI Module - Consolidated AI Agents System
================================================

This module provides a consolidated interface to all AI agents in the Ainflue platform.
Organizes 53+ specialized AI agents into 5 manageable files for improved maintainability.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use is strictly prohibited. Contact: mlaiel@live.de
"""

from .agent_registry import AgentRegistry, get_agent, list_agents
from .core_business_agents import CoreBusinessAgents
from .content import ContentAgents, ContentProcessingResult, create_content_agents
from .technical_agents import TechnicalAgents
from .personality import (
    PersonalityAgents,
    PersonalityType,
    ExpertiseLevel,
    PersonalityTone,
    PersonalityProfile,
    PersonalityResponse,
    BasePersonalityAgent,
    FashionExpertAgent,
    FitnessCoachAgent,
    TechReviewerAgent,
    FoodCriticAgent,
    create_personality_agents,
    create_fashion_expert,
    create_fitness_coach,
    create_tech_reviewer,
    create_food_critic
)
from .analytics import (
    AnalyticsHub,
    TrendAnalyzer,
    EngagementPredictor,
    AudienceAnalyzer,
    CompetitorMonitor,
    AnalyticsRequest,
    AnalyticsResponse,
    analyze_trends,
    predict_engagement,
    analyze_audience,
    monitor_competitors,
    comprehensive_analytics
)
from .specialties import (
    SpecialtyAgents,
    SpecialtyType,
    SpecializationLevel,
    SpecialtyResult,
    AudioSpecialistAgent,
    VideoSpecialistAgent,
    ImageSpecialistAgent,
    TextSpecialistAgent,
    EngagementSpecialistAgent,
    create_specialty_agents
)
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
from .education import (
    EducationAIService,
    IEducationAIService,
    CourseType,
    DifficultyLevel,
    AssessmentType,
    LearningStyle,
    TutoringMode,
    Course,
    StudentProfile,
    Assessment,
    create_education_service,
    create_content_creator_tutor,
    create_business_development_tutor
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
    "ContentProcessingResult",
    "create_content_agents",
    "TechnicalAgents",
    # Personality Agents - Expert AI Personalities
    "PersonalityAgents",
    "PersonalityType",
    "ExpertiseLevel",
    "PersonalityTone",
    "PersonalityProfile",
    "PersonalityResponse",
    "BasePersonalityAgent",
    "FashionExpertAgent",
    "FitnessCoachAgent",
    "TechReviewerAgent",
    "FoodCriticAgent",
    "create_personality_agents",
    "create_fashion_expert",
    "create_fitness_coach",
    "create_tech_reviewer",
    "create_food_critic",
    # Analytics Agents - Data Analysis and Insights
    "AnalyticsHub",
    "TrendAnalyzer",
    "EngagementPredictor",
    "AudienceAnalyzer",
    "CompetitorMonitor",
    "AnalyticsRequest",
    "AnalyticsResponse",
    "analyze_trends",
    "predict_engagement",
    "analyze_audience",
    "monitor_competitors",
    "comprehensive_analytics",
    # Specialty Agents - Human-centric AI Services
    "SpecialtyAgents",
    "SpecialtyType",
    "SpecializationLevel",
    "SpecialtyResult",
    "AudioSpecialistAgent",
    "VideoSpecialistAgent", 
    "ImageSpecialistAgent",
    "TextSpecialistAgent",
    "EngagementSpecialistAgent",
    "create_specialty_agents",
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
    "create_mentor_companion",
    # Education Service - AI Tutor & Learning Management
    "EducationAIService",
    "IEducationAIService",
    "CourseType",
    "DifficultyLevel", 
    "AssessmentType",
    "LearningStyle",
    "TutoringMode",
    "Course",
    "StudentProfile",
    "Assessment",
    "create_education_service",
    "create_content_creator_tutor",
    "create_business_development_tutor"
]