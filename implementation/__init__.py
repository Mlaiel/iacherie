"""Implementation Module

Core implementation components for the Ainflue platform including:
- Content surveillance implementation  
- AI task processing system
- Platform integration management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

from .content_surveillance_implementation import (
    PlatformContentSurveillance,
    ContentType,
    DetectionResult
)

from .ai_task_processor import (
    AITaskProcessor,
    TaskType,
    TaskStatus,
    TaskPriority,
    AITask,
    TaskContext,
    TaskResult
)

from .platform_integration_manager import (
    PlatformIntegrationManager,
    PlatformType,
    APIMethod,
    PlatformConfig,
    APICredentials,
    PlatformResponse
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

__all__ = [
    # Content Surveillance
    'PlatformContentSurveillance',
    'ContentType', 
    'DetectionResult',
    
    # AI Task Processing
    'AITaskProcessor',
    'TaskType',
    'TaskStatus', 
    'TaskPriority',
    'AITask',
    'TaskContext',
    'TaskResult',
    
    # Platform Integration
    'PlatformIntegrationManager',
    'PlatformType',
    'APIMethod',
    'PlatformConfig',
    'APICredentials',
    'PlatformResponse'
]