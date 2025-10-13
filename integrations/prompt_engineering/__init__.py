# 🤖 Init: Configuration module prompt engineering
"""
Prompt Engineering Module - IA Chérie Integrations
================================================
Enterprise prompt engineering avec optimisation IA, sécurité avancée,
templates intelligents et automation prompt generation.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie Integrations
Version: 1.0 Production
"""

from .enterprise_prompt_engineering import *
from .prompt_template_manager import PromptTemplateManager
from .prompt_optimization_engine import PromptOptimizationEngine
from .prompt_security_validator import PromptSecurityValidator
from .prompt_analytics import PromptAnalytics

__all__ = [
    'EnterprisePromptSecurityValidator',
    'EnterprisePromptOptimizer',
    'PromptTemplateManager',
    'PromptOptimizationEngine',
    'PromptSecurityValidator',
    'PromptAnalytics'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary - All Rights Reserved"