"""
AI Services Module - Ainflue Integrations
========================================
Enterprise-grade AI services providing comprehensive artificial intelligence
capabilities, model routing, performance optimization, and multi-provider
orchestration across 53+ AI agents and models.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

# Import all AI service components
from .ai_cost_optimizer import *
from .ai_model_router import *
from .ai_performance_monitor import *
from .ai_response_processor import *
from .anthropic_integration import *
from .aws_ai_integration import *
from .azure_ai_integration import *
from .cohere_integration import *
from .elevenlabs_integration import *
from .google_ai_integration import *
from .huggingface_integration import *
from .midjourney_integration import *
from .openai_integration import *
from .replicate_integration import *
from .stability_ai_integration import *

# Re-export for convenience
from . import (
    ai_cost_optimizer,
    ai_model_router,
    ai_performance_monitor,
    ai_response_processor,
    anthropic_integration,
    aws_ai_integration,
    azure_ai_integration,
    cohere_integration,
    elevenlabs_integration,
    google_ai_integration,
    huggingface_integration,
    midjourney_integration,
    openai_integration,
    replicate_integration,
    stability_ai_integration
)

# Exports publics
__all__ = [
    'AICostOptimizer',
    'AIModelRouter',
    'AIPerformanceMonitor',
    'AIResponseProcessor',
    'AnthropicIntegration',
    'AWSAIIntegration',
    'AzureAIIntegration',
    'CohereIntegration',
    'ElevenLabsIntegration',
    'GoogleAIIntegration',
    'HuggingFaceIntegration',
    'MidjourneyIntegration',
    'OpenAIIntegration',
    'ReplicateIntegration',
    'StabilityAIIntegration',
]

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise AI services infrastructure for multi-provider content generation and optimization"

# Configuration logique métier Ainflue
AINFLUE_INTEGRATIONS = {
    'platforms': 65,
    'ecosystems': 3,
    'ai_agents': 53,
    'workflow': 'connect→auth→transform→process→distribute→monitor',
    'ai_features': [
        'intelligent_content_generation',
        'multi_provider_orchestration',
        'cost_optimization',
        'performance_monitoring',
        'quality_enhancement'
    ]
}