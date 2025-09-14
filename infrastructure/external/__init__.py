"""Infrastructure External Integrations - Ainflue Enterprise Platform
=====================================================================
External service integrations for the infrastructure module

Author: Fahed Mlaiel <mlaiel@live.de>
Project: Ainflue Infrastructure Enterprise
License: Proprietary - All rights reserved

This module provides integrations with external services:
- AI Prompt Optimization (from root)
- AI Services (OpenAI, Anthropic, etc.)
- Blockchain Networks (Ethereum, Polygon, etc.)
- Payment Gateways (Stripe, PayPal, etc.)
- Social Media APIs (65+ platforms)
"""

# AI Prompt Optimization (from root ai_prompt_optimizer.py)
try:
    from .ai_prompt_optimizer import (
        AIPromptOptimizer, PromptEngineering, PromptTemplateManager,
        LanguageOptimizer, ContextualPromptBuilder, PromptAnalyzer,
        ai_prompt_optimizer, prompt_engineering, prompt_template_manager
    )
except ImportError:
    AIPromptOptimizer = PromptEngineering = PromptTemplateManager = None
    LanguageOptimizer = ContextualPromptBuilder = PromptAnalyzer = None
    ai_prompt_optimizer = prompt_engineering = prompt_template_manager = None

# Import all external integration modules
try:
    from .ai_services import *
except ImportError:
    pass

try:
    from .blockchain_networks import *
except ImportError:
    pass

try:
    from .payment_gateways import *
except ImportError:
    pass

try:
    from .social_media_apis import *
except ImportError:
    pass

try:
    from .social_media_connectors import *
except ImportError:
    pass

try:
    from .music_streaming_connectors import *
except ImportError:
    pass

try:
    from .creator_economy_connectors import *
except ImportError:
    pass

# Advanced platform integration components (Expert Implementation)
try:
    from .platform_integration_manager import *
except ImportError:
    pass

try:
    from .seo_optimization import *
except ImportError:
    pass

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

# Collect all exports from submodules
__all__ = []

# Add AI prompt optimization exports
try:
    from . import ai_prompt_optimizer
    if hasattr(ai_prompt_optimizer, '__all__'):
        __all__.extend(ai_prompt_optimizer.__all__)
except ImportError:
    pass

# Add exports from each submodule if they exist
for module_name in ['ai_services', 'blockchain_networks', 'payment_gateways', 'social_media_apis', 'social_media_connectors', 'music_streaming_connectors', 'creator_economy_connectors', 'platform_integration_manager', 'seo_optimization']:
    try:
        module = getattr(__import__(__name__ + '.' + module_name, fromlist=[module_name]), module_name)
        if hasattr(module, '__all__'):
            __all__.extend(module.__all__)
    except (ImportError, AttributeError):
        pass