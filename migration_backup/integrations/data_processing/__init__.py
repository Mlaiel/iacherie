"""
Data Processing Module - IA Chéries Integrations
============================================
Enterprise data processing module providing transformation engines,
caching management, synchronization, and data pipeline orchestration.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Integrations
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
from .warehouse_integration_manager import WarehouseIntegrationManager
from .analytics_query_engine import AnalyticsQueryEngine
from .machine_learning_processor import MachineLearningProcessor
from .data_governance_controller import DataGovernanceController

# Public exports
__all__ = [
    'TransformationEngine',
    'CacheManager',
    'SyncManager',
    'ETLPipelineOrchestrator',
    'StreamingDataProcessor',
    'DataValidationEngine',
    'QualityAssessmentManager',
    'WarehouseIntegrationManager',
    'AnalyticsQueryEngine',
    'MachineLearningProcessor',
    'DataGovernanceController',
]

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise data processing and transformation for IA Chéries platform"

# Configuration logique métier IA Chéries
IA CHÉRIES_DATA_PROCESSING = {
    'platforms': 65,
    'processing_features': [
        'transformation', 'caching', 'synchronization', 'validation',
        'etl_orchestration', 'streaming_processing', 'quality_assessment',
        'warehouse_integration', 'analytics_query', 'machine_learning', 'data_governance'
    ],
    'workflow': 'connect→auth→extract→transform→validate→load→analyze→govern→monitor→improve'
}