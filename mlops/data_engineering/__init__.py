"""
Data Engineering Module
Enterprise data engineering and pipeline management for MLOps

Components:
- ETL engines and data transformation pipelines
- Feature engineering and feature stores
- Data quality monitoring and validation
- Streaming data processing
- Data lineage tracking and governance
- Schema validation and management
- Data catalog and governance
- Privacy and compliance
- Real-time feature serving

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .etl_engine import ETLEngine
from .feature_store_manager import FeatureStoreManager
from .feature_engineering_engine import FeatureEngineeringEngine
from .data_quality_monitor import DataQualityMonitor
from .database_manager import DatabaseManager
from .streaming_data_processor import StreamingDataProcessor
from .schema_validator import SchemaValidator
from .data_lineage_tracker import DataLineageTracker
from .data_pipeline_orchestrator import DataPipelineOrchestrator
from .data_catalog_manager import DataCatalogManager
from .data_privacy_engine import DataPrivacyEngine
from .data_profiling_service import DataProfilingService
from .data_transformation_engine import DataTransformationEngine
from .data_validation_framework import DataValidationFramework
from .data_federation_service import DataFederationService
from .real_time_feature_service import RealTimeFeatureService

__version__ = "1.0.0"
__all__ = [
    "ETLEngine",
    "FeatureStoreManager", 
    "FeatureEngineeringEngine",
    "DataQualityMonitor",
    "DatabaseManager",
    "StreamingDataProcessor",
    "SchemaValidator",
    "DataLineageTracker",
    "DataPipelineOrchestrator",
    "DataCatalogManager",
    "DataPrivacyEngine",
    "DataProfilingService", 
    "DataTransformationEngine",
    "DataValidationFramework",
    "DataFederationService",
    "RealTimeFeatureService"
]