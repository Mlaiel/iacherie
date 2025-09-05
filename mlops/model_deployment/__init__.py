"""
MLOps Model Deployment Module
Handles model deployment and serving
"""

# This module provides model deployment functionality
# Currently using the main platform orchestrator

try:
    from ..platform_orchestrator import MLOpsConfig, create_mlops_platform
    __all__ = ["MLOpsConfig", "create_mlops_platform"]
except ImportError:
    __all__ = []

__version__ = "1.0.0"
