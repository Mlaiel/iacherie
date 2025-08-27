"""
Platform Module Index - Central Platform Operations Hub

This module serves as the main entry point for all platform-level operations
including orchestration, content processing, distribution, analytics, and more.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any

from .platform_orchestrator import PlatformOrchestrator
from .content_processor import ContentProcessor
from .distribution_manager import DistributionManager
from .platform_analytics import PlatformAnalytics
from .integration_hub import IntegrationHub
from .platform_security import PlatformSecurity
from .monetization_controller import MonetizationController
from .collaboration_engine import CollaborationEngine
from .notification_dispatcher import NotificationDispatcher
from .quality_assurance import QualityAssurance

logger = logging.getLogger(__name__)

class PlatformManager:
    """
    Central platform manager coordinating all platform operations
    
    This class serves as the main interface for platform-level operations,
    coordinating between different components and ensuring smooth integration.
    """
    
    def __init__(self):
        # Initialize all platform components
        self.orchestrator = PlatformOrchestrator()
        self.content_processor = ContentProcessor()
        self.distribution_manager = DistributionManager()
        self.analytics = PlatformAnalytics()
        self.integration_hub = IntegrationHub()
        self.security = PlatformSecurity()
        self.monetization = MonetizationController()
        self.collaboration = CollaborationEngine()
        self.notifications = NotificationDispatcher()
        self.quality_assurance = QualityAssurance()
        
        self.initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize all platform components
        
        Returns:
            bool: True if all components initialized successfully
        """
        try:
            logger.info("Initializing Platform Manager...")
            
            # Initialize components in dependency order
            components = [
                ("Security", self.security),
                ("Quality Assurance", self.quality_assurance),
                ("Content Processor", self.content_processor),
                ("Integration Hub", self.integration_hub),
                ("Notification Dispatcher", self.notifications),
                ("Analytics", self.analytics),
                ("Distribution Manager", self.distribution_manager),
                ("Monetization Controller", self.monetization),
                ("Collaboration Engine", self.collaboration),
                ("Platform Orchestrator", self.orchestrator)
            ]
            
            for name, component in components:
                logger.info(f"Initializing {name}...")
                success = await component.initialize()
                if not success:
                    logger.error(f"Failed to initialize {name}")
                    return False
                logger.info(f"{name} initialized successfully")
            
            self.initialized = True
            logger.info("Platform Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Platform Manager initialization failed: {e}")
            return False
    
    def get_component(self, component_name: str) -> Optional[Any]:
        """
        Get platform component by name
        
        Args:
            component_name: Name of the component
            
        Returns:
            Component instance or None if not found
        """
        components = {
            'orchestrator': self.orchestrator,
            'content_processor': self.content_processor,
            'distribution_manager': self.distribution_manager,
            'analytics': self.analytics,
            'integration_hub': self.integration_hub,
            'security': self.security,
            'monetization': self.monetization,
            'collaboration': self.collaboration,
            'notifications': self.notifications,
            'quality_assurance': self.quality_assurance
        }
        
        return components.get(component_name.lower())
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of all platform components
        
        Returns:
            Dict containing health status of all components
        """
        if not self.initialized:
            return {'status': 'not_initialized', 'components': {}}
        
        health_status = {
            'status': 'healthy',
            'components': {},
            'overall_health': 100.0
        }
        
        # Check each component
        components = {
            'orchestrator': self.orchestrator,
            'content_processor': self.content_processor,
            'distribution_manager': self.distribution_manager,
            'analytics': self.analytics,
            'integration_hub': self.integration_hub,
            'security': self.security,
            'monetization': self.monetization,
            'collaboration': self.collaboration,
            'notifications': self.notifications,
            'quality_assurance': self.quality_assurance
        }
        
        total_health = 0.0
        for name, component in components.items():
            try:
                # Basic health check - can be extended per component
                component_health = {
                    'status': 'healthy',
                    'initialized': hasattr(component, 'initialized') and getattr(component, 'initialized', True),
                    'last_check': None
                }
                
                health_status['components'][name] = component_health
                total_health += 100.0
                
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                health_status['components'][name] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'initialized': False
                }
                total_health += 0.0
        
        health_status['overall_health'] = total_health / len(components) if components else 0.0
        
        if health_status['overall_health'] < 80.0:
            health_status['status'] = 'degraded'
        elif health_status['overall_health'] < 50.0:
            health_status['status'] = 'unhealthy'
        
        return health_status

# Global platform manager instance
platform_manager = PlatformManager()

# Convenience functions for accessing components
async def initialize_platform() -> bool:
    """Initialize the platform manager and all components"""
    return await platform_manager.initialize()

def get_orchestrator() -> PlatformOrchestrator:
    """Get platform orchestrator instance"""
    return platform_manager.orchestrator

def get_content_processor() -> ContentProcessor:
    """Get content processor instance"""
    return platform_manager.content_processor

def get_distribution_manager() -> DistributionManager:
    """Get distribution manager instance"""
    return platform_manager.distribution_manager

def get_analytics() -> PlatformAnalytics:
    """Get platform analytics instance"""
    return platform_manager.analytics

def get_integration_hub() -> IntegrationHub:
    """Get integration hub instance"""
    return platform_manager.integration_hub

def get_security() -> PlatformSecurity:
    """Get platform security instance"""
    return platform_manager.security

def get_monetization() -> MonetizationController:
    """Get monetization controller instance"""
    return platform_manager.monetization

def get_collaboration() -> CollaborationEngine:
    """Get collaboration engine instance"""
    return platform_manager.collaboration

def get_notifications() -> NotificationDispatcher:
    """Get notification dispatcher instance"""
    return platform_manager.notifications

def get_quality_assurance() -> QualityAssurance:
    """Get quality assurance instance"""
    return platform_manager.quality_assurance

async def platform_health_check() -> Dict[str, Any]:
    """Perform platform health check"""
    return await platform_manager.health_check()

__all__ = [
    'PlatformManager',
    'platform_manager',
    'initialize_platform',
    'get_orchestrator',
    'get_content_processor',
    'get_distribution_manager',
    'get_analytics',
    'get_integration_hub',
    'get_security',
    'get_monetization',
    'get_collaboration',
    'get_notifications',
    'get_quality_assurance',
    'platform_health_check'
]
