"""
Creator Onboarding Agent - Industrial-Grade Multi-Format Creator Onboarding System

Advanced onboarding system for creators (musicians, influencers, content creators)
with AI-powered content processing, rights protection, and monetization setup.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Any violation will result in legal action under German and international copyright law.

Project Team Specialties:
- Lead AI Developer & System Architect: Fahed Mlaiel
- Backend Senior Python Engineer: Expert-level enterprise development
- ML Engineer: Advanced machine learning and AI model integration
- Audio Processing Engineer: Professional audio analysis and processing
- DevOps Engineer: Kubernetes, CI/CD, and infrastructure automation
- DBA & Data Engineer: High-performance database optimization
- Security Specialist: Enterprise-grade security and compliance
- Microservices Architect: Scalable distributed systems design

Contact: Fahed Mlaiel <mlaiel@live.de>
"""

from .creator_onboarding_agent import CreatorOnboardingAgent
from .onboarding_manager import OnboardingManager
from .profile_builder import ProfileBuilder
from .content_analyzer import ContentAnalyzer
from .rights_validator import RightsValidator
from .platform_connector import PlatformConnector
from .monetization_setup import MonetizationSetup
from .quality_assessor import QualityAssessor
from .collaboration_matcher import CollaborationMatcher
from .verification_engine import VerificationEngine
from .onboarding_workflow import OnboardingWorkflow

# Import index/router for easy access
from .index import OnboardingRouter, default_router

__all__ = [
    "CreatorOnboardingAgent",
    "OnboardingManager",
    "ProfileBuilder", 
    "ContentAnalyzer",
    "RightsValidator",
    "PlatformConnector",
    "MonetizationSetup",
    "QualityAssessor",
    "CollaborationMatcher",
    "VerificationEngine",
    "OnboardingWorkflow",
    "OnboardingRouter",
    "default_router"
]

__version__ = "2.1.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

# Convenience access to main components via default router
def get_onboarding_agent():
    """Get the main onboarding agent instance."""
    return default_router.onboarding_agent

def get_workflow_manager():
    """Get the workflow manager instance."""
    return default_router.onboarding_workflow

def get_content_analyzer():
    """Get the content analyzer instance."""
    return default_router.content_analyzer

def get_quality_assessor():
    """Get the quality assessor instance."""
    return default_router.quality_assessor

def get_verification_engine():
    """Get the verification engine instance."""
    return default_router.verification_engine
