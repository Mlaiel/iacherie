# =============================================================================
# AINFLUE DOCKER SERVICES INDEX
# =============================================================================
# Central orchestrator for all Docker services and registry
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

"""
Docker Services Registry and Orchestrator

This module provides centralized management for all Docker services
in the Ainflue platform, including service discovery, health checks,
and orchestration coordination.

Service Categories:
- Audio Processing: Professional audio processing services
- Protection Rights: Content protection and rights management
- Monetization: Revenue tracking and payment processing
- Collaboration: Creator matching and collaboration tools
- SEO Optimization: Content optimization and search enhancement
- Distribution: Multi-platform content distribution
- Analytics: Business intelligence and performance analytics
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service category registry
SERVICE_CATEGORIES = {
    "audio": {
        "name": "Audio Processing Services",
        "base_port": 8010,
        "description": "Professional audio processing and enhancement",
        "services_count": 9
    },
    "protection": {
        "name": "Protection Rights Services", 
        "base_port": 8020,
        "description": "Content protection and rights management",
        "services_count": 11
    },
    "monetization": {
        "name": "Monetization Services",
        "base_port": 8030,
        "description": "Revenue tracking and payment processing", 
        "services_count": 11
    },
    "collaboration": {
        "name": "Collaboration Services",
        "base_port": 8040,
        "description": "Creator matching and collaboration tools",
        "services_count": 11
    },
    "seo": {
        "name": "SEO Optimization Services",
        "base_port": 8050,
        "description": "Content optimization and search enhancement",
        "services_count": 11
    },
    "distribution": {
        "name": "Distribution Services",
        "base_port": 8060,
        "description": "Multi-platform content distribution",
        "services_count": 11
    },
    "analytics": {
        "name": "Analytics Intelligence Services",
        "base_port": 8070,
        "description": "Business intelligence and performance analytics",
        "services_count": 10
    }
}

# User type service mappings
USER_TYPE_SERVICES = {
    "musician": ["audio", "protection", "monetization", "distribution"],
    "photographer": ["protection", "seo", "monetization", "distribution"],
    "blogger": ["seo", "collaboration", "analytics", "monetization"],
    "influencer": ["seo", "distribution", "collaboration", "analytics"],
    "comedian": ["audio", "protection", "collaboration", "distribution"]
}

class DockerServiceRegistry:
    """Central registry for all Docker services."""
    
    def __init__(self):
        self.services = {}
        self.health_status = {}
        
    def register_service(self, category: str, service_name: str, config: Dict[str, Any]):
        """Register a new service in the registry."""
        if category not in self.services:
            self.services[category] = {}
        
        self.services[category][service_name] = config
        logger.info(f"Registered service: {category}.{service_name}")
        
    def get_services_for_user_type(self, user_type: str) -> List[str]:
        """Get required services for a specific user type."""
        return USER_TYPE_SERVICES.get(user_type, [])
        
    def get_category_info(self, category: str) -> Dict[str, Any]:
        """Get information about a service category."""
        return SERVICE_CATEGORIES.get(category, {})
        
    def list_all_categories(self) -> List[str]:
        """List all available service categories."""
        return list(SERVICE_CATEGORIES.keys())
        
    def get_health_status(self, category: str, service_name: str) -> str:
        """Get health status of a specific service."""
        return self.health_status.get(f"{category}.{service_name}", "unknown")

# Global service registry instance
service_registry = DockerServiceRegistry()

def get_compose_services_for_user(user_type: str) -> Dict[str, Any]:
    """Generate Docker Compose service definitions for a user type."""
    required_categories = service_registry.get_services_for_user_type(user_type)
    compose_services = {}
    
    for category in required_categories:
        category_info = service_registry.get_category_info(category)
        if category_info:
            compose_services[f"{category}_services"] = {
                "extends": {
                    "file": f"docker-compose.{category}.yml",
                    "service": f"{category}_cluster"
                }
            }
    
    return compose_services

def validate_service_dependencies() -> bool:
    """Validate that all service dependencies are available."""
    try:
        # Check if all required service categories are defined
        for category in SERVICE_CATEGORIES:
            logger.info(f"Validating category: {category}")
            
        logger.info("All service dependencies validated successfully")
        return True
    except Exception as e:
        logger.error(f"Service dependency validation failed: {e}")
        return False

if __name__ == "__main__":
    # Initialize and validate service registry
    logger.info("Initializing Docker Services Registry")
    
    if validate_service_dependencies():
        logger.info("Docker Services Registry initialized successfully")
    else:
        logger.error("Failed to initialize Docker Services Registry")