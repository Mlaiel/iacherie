"""Creator Services Module for Ainflue Platform
Specialized tools and services for different types of content creators.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .index import (
    CreatorType,
    ContentType,
    CreatorProfile,
    ContentProject,
    CreatorServicesOrchestrator,
    creator_services_orchestrator,
    initialize_creator_services,
    shutdown_creator_services
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    'CreatorType',
    'ContentType',
    'CreatorProfile',
    'ContentProject',
    'CreatorServicesOrchestrator',
    'creator_services_orchestrator',
    'initialize_creator_services',
    'shutdown_creator_services'
]