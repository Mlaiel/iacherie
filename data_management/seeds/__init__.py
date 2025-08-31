"""IA Influencer Agent - Data Management Seeds Module
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: All rights reserved - Unauthorized use strictly prohibited

Enterprise-grade seed data initialization for comprehensive content protection,
AI-powered analytics, multi-platform integration, and monetization systems.
"""
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime, timezone

# Import all seed managers
from .user_seeds import UserSeedsManager
from .content_seeds import ContentSeedsManager
from .platform_seeds import PlatformSeedsManager
from .analytics_seeds import AnalyticsSeedsManager
from .ai_models_seeds import AIModelsSeedsManager
from .collaboration_seeds import CollaborationSeedsManager
from .monetization_seeds import MonetizationSeedsManager
from .protection_seeds import ProtectionSeedsManager
from .security_seeds import SecuritySeedsManager
from .fingerprint_seeds import FingerprintSeedsManager

# Import orchestrator
from .index import SeedsOrchestrator, initialize_all_seeds, initialize_seed_module

logger = logging.getLogger(__name__)


# Export all classes and functions
__all__ = [
    # Seed Managers
    'UserSeedsManager',
    'ContentSeedsManager', 
    'PlatformSeedsManager',
    'AnalyticsSeedsManager',
    'AIModelsSeedsManager',
    'CollaborationSeedsManager',
    'MonetizationSeedsManager',
    'ProtectionSeedsManager',
    'SecuritySeedsManager',
    'FingerprintSeedsManager',
    
    # Orchestrator
    'SeedsOrchestrator',
    
    # Convenience functions
    'initialize_all_seeds',
    'initialize_seed_module',
    
    # Legacy compatibility
    'SeedManager'
]


class SeedManager:
    """    Legacy compatibility wrapper for the enhanced SeedsOrchestrator.
    
    This class maintains backward compatibility while providing access to
    the new enterprise-grade seeds orchestration system.
    """    
    def __init__(self):
        """Initialize seed manager with orchestrator."""
        self.orchestrator = SeedsOrchestrator()
        
        # Legacy access to individual managers
        self.content_seeds = self.orchestrator.managers['content_seeds']
        self.protection_seeds = self.orchestrator.managers['protection_seeds']
        self.analytics_seeds = self.orchestrator.managers['analytics_seeds']
        self.monetization_seeds = self.orchestrator.managers['monetization_seeds']
        self.ai_models_seeds = self.orchestrator.managers['ai_models_seeds']
        self.platform_seeds = self.orchestrator.managers['platform_seeds']
        self.user_seeds = self.orchestrator.managers['user_seeds']
        self.security_seeds = self.orchestrator.managers['security_seeds']
        self.fingerprint_seeds = self.orchestrator.managers['fingerprint_seeds']
        self.collaboration_seeds = self.orchestrator.managers['collaboration_seeds']
        
        self.initialized_modules = set()
        self.seed_status = {}
    
    async def initialize_all_seeds(self, force_reinitialize: bool = False) -> Dict[str, Any]:
        """Initialize all seed data using the new orchestrator."""
        return await self.orchestrator.initialize_all(parallel=True, validate=True)
    
    async def initialize_content_seeds(self) -> Dict[str, Any]:
        """Initialize content-related seed data."""
        return await self.content_seeds.initialize()
    
    async def initialize_protection_seeds(self) -> Dict[str, Any]:
        """Initialize content protection seed data."""
        return await self.protection_seeds.initialize()
    
    async def initialize_analytics_seeds(self) -> Dict[str, Any]:
        """Initialize analytics and metrics seed data."""
        return await self.analytics_seeds.initialize()
    
    async def initialize_monetization_seeds(self) -> Dict[str, Any]:
        """Initialize monetization and revenue seed data."""
        return await self.monetization_seeds.initialize()
    
    async def initialize_ai_models_seeds(self) -> Dict[str, Any]:
        """Initialize AI/ML models seed data."""
        return await self.ai_models_seeds.initialize()
    
    async def initialize_platform_seeds(self) -> Dict[str, Any]:
        """Initialize external platform integration seed data."""
        return await self.platform_seeds.initialize()
    
    async def initialize_user_seeds(self) -> Dict[str, Any]:
        """Initialize user roles and permissions seed data."""
        return await self.user_seeds.initialize()
    
    async def initialize_security_seeds(self) -> Dict[str, Any]:
        """Initialize security configuration seed data."""
        return await self.security_seeds.initialize()
    
    async def initialize_fingerprint_seeds(self) -> Dict[str, Any]:
        """Initialize AI fingerprinting seed data."""
        return await self.fingerprint_seeds.initialize()
    
    async def initialize_collaboration_seeds(self) -> Dict[str, Any]:
        """Initialize creator collaboration seed data."""
        return await self.collaboration_seeds.initialize()
    
    def get_initialization_status(self) -> Dict[str, Any]:
        """Get current initialization status of all modules."""
        return {
            'initialized_modules': list(self.initialized_modules),
            'total_modules': 10,
            'completion_percentage': len(self.initialized_modules) / 10 * 100,
            'last_status': self.seed_status,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    async def reset_all_seeds(self) -> Dict[str, Any]:
        """Reset all seed data (use with extreme caution in production)."""
        return await self.orchestrator.reset_all()


# Export main classes and functions
__all__ = [
    'SeedManager',
    'ContentSeedsManager',
    'ProtectionSeedsManager',
    'AnalyticsSeedsManager',
    'MonetizationSeedsManager',
    'AIModelsSeedsManager',
    'PlatformSeedsManager',
    'UserSeedsManager',
    'SecuritySeedsManager',
    'FingerprintSeedsManager',
    'CollaborationSeedsManager'
]
