"""
MLOps A/B Testing Module
Implements A/B testing for AI models with business metrics tracking
"""

try:
    from .ab_engine import ABTestingEngine, ModelVariant, BusinessMetric, ExperimentStatus, TestType
    __all__ = ["ABTestingEngine", "ModelVariant", "BusinessMetric", "ExperimentStatus", "TestType"]
except ImportError:
    # Graceful degradation when dependencies are missing
    __all__ = []

__version__ = "1.0.0"
