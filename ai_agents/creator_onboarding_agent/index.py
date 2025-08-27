"""
Creator Onboarding Agent - Module Index and Router

Central routing and module management for the Creator Onboarding Agent system.
Provides unified access to all onboarding components and services.

Author: Fahed Mlaiel <mlaiel@live.de>
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

# Module version and metadata
__version__ = "2.1.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__description__ = "Advanced Creator Onboarding Agent System with AI-powered workflow management"

# Export all main classes
__all__ = [
    'CreatorOnboardingAgent',
    'OnboardingManager',
    'ProfileBuilder',
    'ContentAnalyzer',
    'RightsValidator',
    'PlatformConnector',
    'MonetizationSetup',
    'QualityAssessor',
    'CollaborationMatcher',
    'VerificationEngine',
    'OnboardingWorkflow',
    'OnboardingRouter'
]

class OnboardingRouter:
    """
    Central router for creator onboarding services.
    
    Provides unified access to all onboarding components with
    intelligent routing, load balancing, and service management.
    """
    
    def __init__(self):
        # Initialize all components
        self.onboarding_agent = CreatorOnboardingAgent()
        self.onboarding_manager = OnboardingManager()
        self.profile_builder = ProfileBuilder()
        self.content_analyzer = ContentAnalyzer()
        self.rights_validator = RightsValidator()
        self.platform_connector = PlatformConnector()
        self.monetization_setup = MonetizationSetup()
        self.quality_assessor = QualityAssessor()
        self.collaboration_matcher = CollaborationMatcher()
        self.verification_engine = VerificationEngine()
        self.onboarding_workflow = OnboardingWorkflow()
        
        # Service registry
        self.services = {
            'agent': self.onboarding_agent,
            'manager': self.onboarding_manager,
            'profile': self.profile_builder,
            'content': self.content_analyzer,
            'rights': self.rights_validator,
            'platforms': self.platform_connector,
            'monetization': self.monetization_setup,
            'quality': self.quality_assessor,
            'collaboration': self.collaboration_matcher,
            'verification': self.verification_engine,
            'workflow': self.onboarding_workflow
        }
    
    def get_service(self, service_name: str):
        """Get a specific service by name."""
        return self.services.get(service_name)
    
    def get_all_services(self):
        """Get all available services."""
        return self.services
    
    async def start_onboarding(self, user_id: str, creator_type: str, initial_data: dict = None):
        """Start comprehensive onboarding workflow."""
        return await self.onboarding_workflow.start_onboarding_workflow(
            user_id, creator_type, initial_data
        )
    
    async def continue_onboarding(self, session_id: str, user_input: dict = None):
        """Continue existing onboarding workflow."""
        return await self.onboarding_workflow.continue_workflow(session_id, user_input)
    
    async def get_onboarding_status(self, session_id: str):
        """Get current onboarding status."""
        return await self.onboarding_workflow.get_workflow_status(session_id)

# Create default router instance
default_router = OnboardingRouter()

# Convenience functions using default router
async def start_creator_onboarding(user_id: str, creator_type: str, initial_data: dict = None):
    """Start creator onboarding workflow."""
    return await default_router.start_onboarding(user_id, creator_type, initial_data)

async def continue_creator_onboarding(session_id: str, user_input: dict = None):
    """Continue creator onboarding workflow."""
    return await default_router.continue_onboarding(session_id, user_input)

async def get_creator_onboarding_status(session_id: str):
    """Get creator onboarding status."""
    return await default_router.get_onboarding_status(session_id)

def get_onboarding_service(service_name: str):
    """Get specific onboarding service."""
    return default_router.get_service(service_name)

# Quick access to main components
def get_onboarding_agent():
    """Get the main onboarding agent."""
    return default_router.onboarding_agent

def get_profile_builder():
    """Get the profile builder service."""
    return default_router.profile_builder

def get_content_analyzer():
    """Get the content analyzer service."""
    return default_router.content_analyzer

def get_quality_assessor():
    """Get the quality assessor service."""
    return default_router.quality_assessor

def get_verification_engine():
    """Get the verification engine service."""
    return default_router.verification_engine

def get_workflow_manager():
    """Get the workflow manager service."""
    return default_router.onboarding_workflow
