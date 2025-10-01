"""
IA Chéries ML Module - Enterprise Machine Learning Infrastructure
============================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 1.2.0 - Enterprise Production Ready
"""

__version__ = "1.2.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Production-ready imports with fallback handling
try:
    from .automl_pipeline import AutoMLPipeline
    from .model_development_orchestrator import ModelDevelopmentOrchestrator
    from .deployment.deployment_manager import DeploymentManager
    from .inference.real_time_inference_engine import RealTimeInferenceEngine
    from .monitoring.performance_monitor import PerformanceMonitor
    
    __all__ = [
        "AutoMLPipeline",
        "ModelDevelopmentOrchestrator", 
        "DeploymentManager",
        "RealTimeInferenceEngine",
        "PerformanceMonitor",
        "__version__"
    ]
    
except ImportError as e:
    # Graceful fallback for missing dependencies
    print(f"ML module: Some components not available due to missing dependencies: {e}")
    __all__ = ["__version__"]
