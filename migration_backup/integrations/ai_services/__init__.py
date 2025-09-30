"""AI Services Integration Module
=============================

Enterprise AI services integration for Ainflue platform providing comprehensive
artificial intelligence capabilities across 53+ AI agents and models for
content generation, analysis, optimization, and multi-provider orchestration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .ai_cost_optimizer import AICostOptimizer
from .ai_model_router import AIModelRouter
from .ai_performance_monitor import AIPerformanceMonitor
from .ai_response_processor import AIResponseProcessor
from .anthropic_integration import AnthropicIntegration
from .aws_ai_integration import AWSAIIntegration
from .azure_ai_integration import AzureAIIntegration
from .cohere_integration import CohereIntegration
from .elevenlabs_integration import ElevenLabsIntegration
from .google_ai_integration import GoogleAIIntegration
from .huggingface_integration import HuggingFaceIntegration
from .midjourney_integration import MidjourneyIntegration
from .openai_integration import OpenAIIntegration
from .replicate_integration import ReplicateIntegration
from .stability_ai_integration import StabilityAIIntegration

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
__description__ = "Enterprise AI services for multi-provider content generation and optimization"

# Configuration logique métier Ainflue
AINFLUE_AI_SERVICES = {
    'platforms': 65,
    'ai_agents': 53,
    'ai_providers': 15,
    'workflow': 'connect→auth→transform→process→distribute→monitor'
}