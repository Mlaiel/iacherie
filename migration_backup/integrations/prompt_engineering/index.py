# 🚀 Index: Point d'entrée prompt engineering avec factory pattern
"""
Prompt Engineering - IA Chéries Integrations
=========================================
Enterprise prompt engineering providing intelligent prompt optimization,
security validation, template management, and advanced AI prompt generation
for creators across music, video, photography, and blog content.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Integrations
Version: 1.0 Production
"""

from .enterprise_prompt_engineering import *
from .prompt_template_manager import *
from .prompt_optimization_engine import *
from .prompt_security_validator import *
from .prompt_analytics import *

# Configuration logique métier IA Chéries
PROMPT_ENGINEERING_CONFIG = {
    'ai_models': ['gpt-4', 'claude-3', 'gemini-pro', 'llama-2'],
    'prompt_types': ['content_generation', 'seo_optimization', 'collaboration_matching', 'protection_analysis'],
    'security_levels': ['low', 'medium', 'high', 'critical'],
    'optimization_metrics': ['relevance', 'creativity', 'safety', 'engagement'],
    'template_categories': ['music', 'video', 'photography', 'blog', 'social'],
    'languages': 644,
    'creators_supported': ['musician', 'video_creator', 'photographer', 'blogger', 'influencer']
}

def get_prompt_engineering_manager():
    """Factory pour créer le gestionnaire principal de prompt engineering."""
    return {
        'enterprise': EnterprisePromptSecurityValidator(),
        'templates': PromptTemplateManager(),
        'optimization': PromptOptimizationEngine(),
        'security': PromptSecurityValidator(),
        'analytics': PromptAnalytics()
    }

def initialize_prompt_engineering_system():
    """Initialise le système complet de prompt engineering."""
    manager = get_prompt_engineering_manager()
    
    # Configuration des systèmes
    for component_name, component in manager.items():
        if hasattr(component, 'initialize'):
            component.initialize()
    
    return manager

# Export principal
__all__ = [
    'PROMPT_ENGINEERING_CONFIG',
    'get_prompt_engineering_manager',
    'initialize_prompt_engineering_system'
]