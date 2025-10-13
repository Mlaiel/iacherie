"""
IA2GOOD Shared Services Package

Provides shared functionality across all IA2GOOD microservices:
- IACherie AI Client: Client for IACherie's 27 AI models
- AI Orchestrator: High-level orchestration for Guardian, EduVerify, MedCare
"""

__version__ = "1.0.0"
__all__ = [
    "get_ai_client",
    "close_ai_client",
    "IAcherieAIClient",
    "IAModelType",
    "IAcheriePriority",
    "get_orchestrator",
    "close_orchestrator",
    "AIOrchestrator"
]

# Make the main classes and functions available at package level
from .iacherie_ai_client import (
    get_ai_client,
    close_ai_client,
    IAcherieAIClient,
    IAModelType,
    IAcheriePriority
)

from .ai_orchestrator import (
    get_orchestrator,
    close_orchestrator,
    AIOrchestrator
)
