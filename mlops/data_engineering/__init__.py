"""
Data Engineering Module
Enterprise data engineering and feature management for MLOps

Components:
- ETL/ELT pipelines and data orchestration
- Feature engineering and feature stores
- Data quality monitoring and validation
- Real-time data processing and streaming
- Data lineage and governance

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

__version__ = "1.0.0"
__all__ = [
    "ETLEngine",
    "FeatureStoreManager",
    "FeatureEngineeringEngine",
    "DataQualityMonitor",
    "DatabaseManager",
    "StreamingDataProcessor",
    "SchemaValidator"
]