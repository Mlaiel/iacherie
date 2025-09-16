"""
Data Processing Module - Ainflue Integrations
============================================
Enterprise data processing module providing transformation engines,
caching management, synchronization, and data pipeline orchestration.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

# Data Processing Core Components
from .transformation_engine import TransformationEngine
from .cache_manager import CacheManager
from .sync_manager import SyncManager
from .etl_pipeline_orchestrator import ETLPipelineOrchestrator
from .streaming_data_processor import StreamingDataProcessor
from .data_validation_engine import DataValidationEngine
from .quality_assessment_manager import QualityAssessmentManager

# Public exports
__all__ = [
    'TransformationEngine',
    'CacheManager',
    'SyncManager',
    'ETLPipelineOrchestrator',
    'StreamingDataProcessor',
    'DataValidationEngine',
    'QualityAssessmentManager',
]

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise data processing and transformation for Ainflue platform"

# Configuration logique métier Ainflue
AINFLUE_DATA_PROCESSING = {
    'platforms': 65,
    'processing_features': [
        'transformation', 'caching', 'synchronization', 'validation',
        'etl_orchestration', 'streaming_processing', 'quality_assessment'
    ],
    'workflow': 'connect→auth→extract→transform→validate→load→monitor→improve'
}