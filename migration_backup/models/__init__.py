"""Models Module

Basic content models for the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

from .content import ContentItem

# Import enterprise architecture functions
from .index import (
    enterprise_models, EnterpriseModelsManager,
    MODEL_REGISTRY, ENTERPRISE_MODULES_AVAILABLE,
    ainflue_enterprise_workflow, get_enterprise_architecture_info
)

__all__ = ['ContentItem', 'enterprise_models', 'EnterpriseModelsManager', 
           'MODEL_REGISTRY', 'ENTERPRISE_MODULES_AVAILABLE', 
           'ainflue_enterprise_workflow', 'get_enterprise_architecture_info']