"""
MLOps Model Versioning Module
Implements complete model versioning with MLflow integration
"""

try:
    from .model_registry import ModelRegistry, ModelVersionComparator
    __all__ = ["ModelRegistry", "ModelVersionComparator"]
except ImportError:
    # Graceful degradation when dependencies are missing
    __all__ = []

__version__ = "1.0.0"
