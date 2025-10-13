"""
Guardian Services Package
Auto-amélioration IA et services métier
"""

from .ai_learning_service import (
    AILearningService,
    get_learning_service,
    start_continuous_learning
)

__all__ = [
    "AILearningService",
    "get_learning_service",
    "start_continuous_learning"
]
