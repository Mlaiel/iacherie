"""MongoDB AI Integration Layer Module
===================================

AI model data storage, training sets, and ML pipeline integration.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"

# Track loaded AI modules
_loaded_modules = []
_failed_modules = []

def _safe_import(module_name: str) -> bool:
    try:
        module = __import__(f"mongodb.ai.{module_name}", fromlist=[module_name])
        globals().update(getattr(module, '__dict__', {}))
        _loaded_modules.append(module_name)
        logger.info(f"Successfully loaded ai.{module_name}")
        return True
    except Exception as e:
        _failed_modules.append((module_name, str(e)))
        logger.warning(f"Failed to load ai.{module_name}: {e}")
        return False

# Import AI modules
_safe_import('model_storage')
_safe_import('training_data_manager')
_safe_import('feature_store')
_safe_import('prediction_cache')
_safe_import('model_monitoring')
_safe_import('pipeline_integrator')
_safe_import('ai_analytics')

__all__ = [
    'ModelStorage', 'TrainingDataManager', 'FeatureStore', 'PredictionCache',
    'ModelMonitoring', 'PipelineIntegrator', 'AIAnalytics',
    'get_model_storage', 'get_feature_store', 'get_prediction_cache'
]

logger.info(f"MongoDB AI Integration module initialized - Version {__version__}")