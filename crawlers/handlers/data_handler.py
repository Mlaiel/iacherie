"""Data Handler Module
==================

Professional data handling system for processing, validation, transformation and storage operations.
Manages structured and unstructured data with enterprise-grade reliability and performance.

Data Types Supported:
- Structured Data (JSON, XML, CSV)
- Media Metadata (Audio, Video, Image)
- Platform API Responses 
- User Generated Content
- Analytics Data
- Financial/Revenue Data
- System Metrics

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Project Team:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel
- ML Engineer: Fahed Mlaiel
- DBA: Fahed Mlaiel
- Security Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Specialist: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

WARNING: This code is protected intellectual property. Any attempt to steal, copy, or use 
without explicit written authorization from Fahed Mlaiel (mlaiel@live.de) will result 
in legal action under German law.
"""

import asyncio
import logging
import json
import uuid
import hashlib
from typing import Dict, List, Optional, Any, Union, Type, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np
from decimal import Decimal, InvalidOperation
import re
from pathlib import Path
import aiofiles
import aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel, ValidationError, validator

from backend.core.exceptions import (
    DataHandlingError,
    DataValidationError,
    DataTransformationError,
    DataStorageError,
    SchemaValidationError
)
from backend.core.logging import get_logger
from backend.core.config import settings
from backend.database.models import (
    DataRecord, ContentFingerprint, User, RevenueTracking,
    AnalyticsData, ProcessedContent
)
from backend.database.session import async_session
from backend.utils.encryption_utils import EncryptionManager
from backend.utils.compression_utils import CompressionManager
from backend.utils.validation_utils import DataValidator
from backend.utils.redis_client import get_redis_client

logger = get_logger(__name__)


class DataType(Enum):
    """
Data type enumeration."""

    STRUCTURED = "structured"
    UNSTRUCTURED = "unstructured"
    MEDIA_METADATA = "media_metadata"
    PLATFORM_RESPONSE = "platform_response"
    USER_CONTENT = "user_content"
    ANALYTICS = "analytics"
    FINANCIAL = "financial"
    METRICS = "metrics"
    FINGERPRINT = "fingerprint"


class DataFormat(Enum):
    """Data format enumeration."""

    JSON = "json"
    XML = "xml"
    CSV = "csv"
    PARQUET = "parquet"
    BINARY = "binary"
    TEXT = "text"
    PICKLE = "pickle"


class DataOperation(Enum):
    """Data operation types."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    TRANSFORM = "transform"
    VALIDATE = "validate"
    AGGREGATE = "aggregate"
    EXPORT = "export"


@dataclass
class DataSchema:
    """Data schema definition."""
    
    name: str
    version: str
    fields: Dict[str, Dict[str, Any]]
    required_fields: List[str]
    optional_fields: List[str]
    validation_rules: Dict[str, Any]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle___post_init___request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler __post_init__ failed: {e}")
                    return {"status": "error", "message": str(e)}
            self.metadata = {}


@dataclass
class DataMetrics:
    """
Data processing metrics."""
    
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    processing_time: float = 0.0
    data_size_bytes: int = 0
    compression_ratio: float = 0.0
    validation_errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []
        if self.warnings is None:
            self.warnings = []
    
    @property
    def success_rate(self) -> float:
        """
Calculate success rate."""
        if self.total_records == 0:
            return 0.0
        return self.valid_records / self.total_records
    
    @property
    def error_rate(self) -> float:
        """
Calculate error rate."""
        return 1.0 - self.success_rate


class ContentMetadataModel(BaseModel):
    """
Content metadata validation model."""
    
    content_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = []
    duration: Optional[float] = None
    file_size: Optional[int] = None
    format: Optional[str] = None
    resolution: Optional[str] = None
    bitrate: Optional[int] = None
    frame_rate: Optional[float] = None
    created_at: Optional[datetime] = None
    platform_metadata: Dict[str, Any] = {}
    
    @validator('tags')
    def validate_tags(cls, v):
        if not isinstance(v, list):
            return []
        return [tag.strip().lower() for tag in v if tag.strip()]
    
    @validator('duration')
    def validate_duration(cls, v):
        if v is not None and v < 0:
            raise ValueError('Duration cannot be negative')
        return v
    
    @validator('file_size')
    def validate_file_size(cls, v):
        if v is not None and v < 0:
            raise ValueError('File size cannot be negative')
        return v


class FinancialDataModel(BaseModel):
    """
Financial data validation model."""
    
    user_id: int
    platform: str
    revenue_amount: Decimal
    currency: str = "EUR"
    period_start: datetime
    period_end: datetime
    revenue_type: str
    metadata: Dict[str, Any] = {}
    
    @validator('revenue_amount')
    def validate_revenue_amount(cls, v):
        if v < 0:
            raise ValueError('Revenue amount cannot be negative')
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        if not re.match(r'^[A-Z]{3}$', v):
            raise ValueError('Currency must be 3-letter ISO code')
        return v.upper()
    
    @validator('period_end')
    def validate_period_end(cls, v, values):
        if 'period_start' in values and v <= values['period_start']:
            raise ValueError('Period end must be after period start')
        return v


class AnalyticsDataModel(BaseModel):
    """Analytics data validation model."""
    
    metric_name: str
    metric_value: Union[int, float, str]
    timestamp: datetime
    user_id: Optional[int] = None
    content_id: Optional[int] = None
    platform: Optional[str] = None
    dimensions: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    @validator('metric_name')
    def validate_metric_name(cls, v):
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v):
            raise ValueError('Invalid metric name format')
        return v


class DataTransformer:
    """
Professional data transformation system."""
    
    def __init__(self):
        self.transformations = self._load_transformations()
    
    def _load_transformations(self) -> Dict[str, Any]:
        """
Load transformation configurations."""
        return {
            'platform_standardization': {
                'youtube': {
                    'id': 'video_id',
                    'snippet.title': 'title',
                    'snippet.description': 'description',
                    'statistics.viewCount': 'view_count',
                    'statistics.likeCount': 'like_count'
                },
                'instagram': {
                    'id': 'media_id',
                    'media_type': 'content_type',
                    'permalink': 'url',
                    'like_count': 'like_count'
                },
                'tiktok': {
                    'id': 'video_id',
                    'desc': 'description',
                    'stats.play_count': 'view_count',
                    'stats.digg_count': 'like_count'
                }
            },
            'data_cleaning': {
                'remove_nulls': True,
                'trim_strings': True,
                'normalize_numbers': True,
                'standardize_dates': True
            },
            'aggregation_rules': {
                'revenue_by_platform': ['platform', 'currency'],
                'engagement_metrics': ['content_type', 'platform'],
                'user_analytics': ['user_id', 'metric_type']
            }
        }
    
    async def transform_platform_data(
        self, 
        data: Dict[str, Any], 
        platform: str
    ) -> Dict[str, Any]:
        """
Transform platform-specific data to standardized format."""
        try:
            if platform not in self.transformations['platform_standardization']:
                return data
            
            mapping = self.transformations['platform_standardization'][platform]
            transformed = {}
            
            # Apply field mappings
            for source_path, target_field in mapping.items():
                value = self._extract_nested_value(data, source_path)
                if value is not None:
                    transformed[target_field] = self._normalize_value(value, target_field)
            
            # Preserve original data
            transformed['_original'] = data
            transformed['_platform'] = platform
            transformed['_transformed_at'] = datetime.utcnow().isoformat()
            
            return transformed
            
        except Exception as e:
            logger.error(f"Platform data transformation failed: {e}")
            raise DataTransformationError(f"Failed to transform {platform} data: {e}")
    
    def _extract_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Extract value from nested dictionary using dot notation."""
        try:
            keys = path.split('.')
            value = data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            
            return value
            
        except Exception:
            return None
    
    def _normalize_value(self, value: Any, field_name: str) -> Any:
        """
Normalize individual field values."""
        try:
            # Numeric fields
            if field_name.endswith('_count') or 'count' in field_name:
                return self._normalize_count(value)
            
            # Date fields
            if field_name.endswith('_at') or 'date' in field_name:
                return self._normalize_date(value)
            
            # Text fields
            if isinstance(value, str):
                return self._normalize_text(value)
            
            return value
            
        except Exception as e:
            logger.warning(f"Value normalization failed for {field_name}: {e}")
            return value
    
    def _normalize_count(self, value: Any) -> int:
        """Normalize count values to integers."""
        if isinstance(value, str):
            # Handle string numbers like "1,234" or "1.2K"
            value = value.replace(',', '')
            
            # Handle abbreviated numbers (K, M, B)
            multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
            for suffix, multiplier in multipliers.items():
                if value.upper().endswith(suffix):
                    number = float(value[:-1])
                    return int(number * multiplier)
        
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0
    
    def _normalize_date(self, value: Any) -> Optional[datetime]:
        """Normalize date values to datetime objects."""
        if isinstance(value, datetime):
            return value
        
        if isinstance(value, str):
            # Common date formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%m/%d/%Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
        
        return None
    
    def _normalize_text(self, value: str) -> str:
        """
Normalize text values."""
        if not isinstance(value, str):
            return str(value)
        
        # Clean and normalize text
        text = value.strip()
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text
    
    async def aggregate_data(
        self, 
        data: List[Dict[str, Any]], 
        aggregation_type: str
    ) -> Dict[str, Any]:
        """
Aggregate data based on predefined rules."""
        try:
            if aggregation_type not in self.transformations['aggregation_rules']:
                raise DataTransformationError(f"Unknown aggregation type: {aggregation_type}")
            
            grouping_fields = self.transformations['aggregation_rules'][aggregation_type]
            
            # Convert to DataFrame for easier aggregation
            df = pd.DataFrame(data)
            
            if df.empty:
                return {}
            
            # Group by specified fields
            if all(field in df.columns for field in grouping_fields):
                grouped = df.groupby(grouping_fields)
                
                # Calculate aggregations
                result = {
                    'total_records': len(df),
                    'groups': {},
                    'summary': self._calculate_summary_stats(df)
                }
                
                for name, group in grouped:
                    group_key = str(name) if isinstance(name, (str, int)) else '_'.join(map(str, name))
                    result['groups'][group_key] = {
                        'count': len(group),
                        'data': group.to_dict('records')
                    }
                
                return result
            else:
                # Basic aggregation without grouping
                return {
                    'total_records': len(df),
                    'summary': self._calculate_summary_stats(df)
                }
                
        except Exception as e:
            logger.error(f"Data aggregation failed: {e}")
            raise DataTransformationError(f"Failed to aggregate data: {e}")
    
    def _calculate_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate summary statistics for DataFrame."""
        try:
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            summary = {}
            
            for col in numeric_columns:
                summary[col] = {
                    'mean': float(df[col].mean()) if not df[col].empty else 0,
                    'median': float(df[col].median()) if not df[col].empty else 0,
                    'std': float(df[col].std()) if not df[col].empty else 0,
                    'min': float(df[col].min()) if not df[col].empty else 0,
                    'max': float(df[col].max()) if not df[col].empty else 0,
                    'count': int(df[col].count())
                }
            
            return summary
            
        except Exception as e:
            logger.warning(f"Summary statistics calculation failed: {e}")
            return {}


class DataValidator:
    """Professional data validation system."""
    
    def __init__(self):
        self.schemas = self._load_schemas()
        self.validation_rules = self._load_validation_rules()
    
    def _load_schemas(self) -> Dict[str, DataSchema]:
        """
Load data schemas for validation."""
        return {
            'content_metadata': DataSchema(
                name='content_metadata',
                version='1.0',
                fields={
                    'content_id': {'type': 'integer', 'nullable': True},
                    'title': {'type': 'string', 'max_length': 500},
                    'description': {'type': 'string', 'max_length': 5000},
                    'tags': {'type': 'array', 'items': 'string'},
                    'duration': {'type': 'number', 'minimum': 0},
                    'file_size': {'type': 'integer', 'minimum': 0}
                },
                required_fields=['title'],
                optional_fields=['content_id', 'description', 'tags', 'duration', 'file_size'],
                validation_rules={}
            ),
            'financial_data': DataSchema(
                name='financial_data',
                version='1.0',
                fields={
                    'user_id': {'type': 'integer', 'minimum': 1},
                    'platform': {'type': 'string', 'enum': ['youtube', 'instagram', 'tiktok', 'spotify']},
                    'revenue_amount': {'type': 'number', 'minimum': 0},
                    'currency': {'type': 'string', 'pattern': '^[A-Z]{3}$'},
                    'period_start': {'type': 'datetime'},
                    'period_end': {'type': 'datetime'}
                },
                required_fields=['user_id', 'platform', 'revenue_amount', 'period_start', 'period_end'],
                optional_fields=['currency'],
                validation_rules={
                    'period_validation': 'period_end > period_start'
                }
            )
        }
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """
Load custom validation rules."""
        return {
            'content_rules': {
                'title_length': {'min': 1, 'max': 500},
                'description_length': {'min': 0, 'max': 5000},
                'allowed_formats': ['mp4', 'mp3', 'jpg', 'png', 'txt', 'pdf']
            },
            'financial_rules': {
                'max_revenue_per_day': 1000000,  # 1M currency units
                'supported_currencies': ['EUR', 'USD', 'GBP', 'JPY', 'CAD'],
                'max_period_days': 365
            },
            'user_rules': {
                'min_user_id': 1,
                'max_user_id': 999999999
            }
        }
    
    async def validate_data(
        self, 
        data: Union[Dict[str, Any], List[Dict[str, Any]]], 
        schema_name: str
    ) -> Tuple[bool, List[str], DataMetrics]:
        """
        Validate data against schema.
        
        Args:
            data: Data to validate
            schema_name: Schema to validate against
            
        Returns:
            Tuple of (is_valid, errors, metrics)
        """
        try:
            start_time = datetime.utcnow()
            errors = []
            warnings = []
            
            if schema_name not in self.schemas:
                raise SchemaValidationError(f"Unknown schema: {schema_name}")
            
            schema = self.schemas[schema_name]
            
            # Handle single record vs list of records
            if isinstance(data, dict):
                records = [data]
            else:
                records = data
            
            valid_count = 0
            total_count = len(records)
            
            for i, record in enumerate(records):
                record_errors = await self._validate_record(record, schema)
                if record_errors:
                    errors.extend([f"Record {i}: {error}" for error in record_errors])
                else:
                    valid_count += 1
            
            # Calculate metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            data_size = len(json.dumps(data).encode('utf-8'))
            
            metrics = DataMetrics(
                total_records=total_count,
                valid_records=valid_count,
                invalid_records=total_count - valid_count,
                processing_time=processing_time,
                data_size_bytes=data_size,
                validation_errors=errors,
                warnings=warnings
            )
            
            is_valid = len(errors) == 0
            
            logger.info(
                f"Data validation completed: {valid_count}/{total_count} records valid "
                f"({metrics.success_rate:.2%} success rate)"
            )
            
            return is_valid, errors, metrics
            
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            raise DataValidationError(f"Validation failed: {e}")
    
    async def _validate_record(
        self, 
        record: Dict[str, Any], 
        schema: DataSchema
    ) -> List[str]:
        """Validate a single record against schema."""
        errors = []
        
        try:
            # Check required fields
            for field in schema.required_fields:
                if field not in record or record[field] is None:
                    errors.append(f"Missing required field: {field}")
            
            # Validate field types and constraints
            for field_name, field_config in schema.fields.items():
                if field_name in record:
                    value = record[field_name]
                    field_errors = await self._validate_field(
                        field_name, value, field_config
                    )
                    errors.extend(field_errors)
            
            # Apply custom validation rules
            for rule_name, rule_config in schema.validation_rules.items():
                rule_errors = await self._apply_validation_rule(
                    record, rule_name, rule_config
                )
                errors.extend(rule_errors)
            
        except Exception as e:
            errors.append(f"Record validation error: {e}")
        
        return errors
    
    async def _validate_field(
        self, 
        field_name: str, 
        value: Any, 
        field_config: Dict[str, Any]
    ) -> List[str]:
        """Validate a single field."""
        errors = []
        
        try:
            field_type = field_config.get('type')
            nullable = field_config.get('nullable', False)
            
            # Handle null values
            if value is None:
                if not nullable:
                    errors.append(f"Field {field_name} cannot be null")
                return errors
            
            # Type validation
            if field_type == 'string' and not isinstance(value, str):
                errors.append(f"Field {field_name} must be string")
            elif field_type == 'integer' and not isinstance(value, int):
                errors.append(f"Field {field_name} must be integer")
            elif field_type == 'number' and not isinstance(value, (int, float)):
                errors.append(f"Field {field_name} must be number")
            elif field_type == 'array' and not isinstance(value, list):
                errors.append(f"Field {field_name} must be array")
            elif field_type == 'datetime' and not isinstance(value, datetime):
                errors.append(f"Field {field_name} must be datetime")
            
            # Constraint validation
            if isinstance(value, str):
                max_length = field_config.get('max_length')
                if max_length and len(value) > max_length:
                    errors.append(f"Field {field_name} exceeds max length {max_length}")
                
                pattern = field_config.get('pattern')
                if pattern and not re.match(pattern, value):
                    errors.append(f"Field {field_name} does not match pattern {pattern}")
                
                enum_values = field_config.get('enum')
                if enum_values and value not in enum_values:
                    errors.append(f"Field {field_name} must be one of {enum_values}")
            
            if isinstance(value, (int, float)):
                minimum = field_config.get('minimum')
                if minimum is not None and value < minimum:
                    errors.append(f"Field {field_name} must be >= {minimum}")
                
                maximum = field_config.get('maximum')
                if maximum is not None and value > maximum:
                    errors.append(f"Field {field_name} must be <= {maximum}")
            
        except Exception as e:
            errors.append(f"Field validation error for {field_name}: {e}")
        
        return errors
    
    async def _apply_validation_rule(
        self, 
        record: Dict[str, Any], 
        rule_name: str, 
        rule_config: str
    ) -> List[str]:
        """Apply custom validation rule."""
        errors = []
        
        try:
            # Simple rule evaluation (can be extended)
            if rule_name == 'period_validation':
                if 'period_start' in record and 'period_end' in record:
                    if record['period_end'] <= record['period_start']:
                        errors.append("Period end must be after period start")
            
        except Exception as e:
            errors.append(f"Validation rule {rule_name} failed: {e}")
        
        return errors


class DataStorage:
    """Professional data storage management system."""
    
    def __init__(
        self,
        encryption_manager: EncryptionManager,
        compression_manager: CompressionManager
    ):
        self.encryption_manager = encryption_manager
        self.compression_manager = compression_manager
    
    async def store_data(
        self,
        data: Any,
        storage_key: str,
        data_type: DataType,
        compress: bool = True,
        encrypt: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store data with optional compression and encryption.
        
        Args:
            data: Data to store
            storage_key: Unique storage identifier
            data_type: Type of data being stored
            compress: Whether to compress data
            encrypt: Whether to encrypt data
            metadata: Additional metadata
            
        Returns:
            Storage information
        """
        try:
            start_time = datetime.utcnow()
            
            # Serialize data
            if isinstance(data, (dict, list)):
                serialized_data = json.dumps(data, default=str).encode('utf-8')
            elif isinstance(data, str):
                serialized_data = data.encode('utf-8')
            else:
                serialized_data = str(data).encode('utf-8')
            
            original_size = len(serialized_data)
            processed_data = serialized_data
            
            # Compress if requested
            compression_ratio = 1.0
            if compress:
                processed_data = await self.compression_manager.compress(processed_data)
                compression_ratio = len(processed_data) / original_size
            
            # Encrypt if requested
            if encrypt:
                processed_data = await self.encryption_manager.encrypt(processed_data)
            
            # Store in database
            async with async_session() as session:
                data_record = DataRecord(
                    storage_key=storage_key,
                    data_type=data_type.value,
                    data_content=processed_data,
                    original_size=original_size,
                    compressed_size=len(processed_data),
                    compression_ratio=compression_ratio,
                    is_encrypted=encrypt,
                    is_compressed=compress,
                    metadata=metadata or {},
                    created_at=datetime.utcnow()
                )
                
                session.add(data_record)
                await session.commit()
                await session.refresh(data_record)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            storage_info = {
                'storage_key': storage_key,
                'data_type': data_type.value,
                'original_size': original_size,
                'stored_size': len(processed_data),
                'compression_ratio': compression_ratio,
                'is_encrypted': encrypt,
                'is_compressed': compress,
                'processing_time': processing_time,
                'record_id': data_record.id
            }
            
            logger.info(f"Data stored successfully: {storage_key} ({original_size} → {len(processed_data)} bytes)")
            return storage_info
            
        except Exception as e:
            logger.error(f"Data storage failed for {storage_key}: {e}")
            raise DataStorageError(f"Failed to store data: {e}")
    
    async def retrieve_data(
        self,
        storage_key: str,
        decrypt: bool = False,
        decompress: bool = True
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Retrieve and process stored data.
        
        Args:
            storage_key: Storage identifier
            decrypt: Whether to decrypt data
            decompress: Whether to decompress data
            
        Returns:
            Tuple of (data, metadata)
        """
        try:
            # Retrieve from database
            async with async_session() as session:
                result = await session.execute(
                    text("SELECT * FROM data_records WHERE storage_key = :key"),
                    {"key": storage_key}
                )
                record = result.fetchone()
                
                if not record:
                    raise DataStorageError(f"Data not found for key: {storage_key}")
                
                data_content = record.data_content
                is_encrypted = record.is_encrypted
                is_compressed = record.is_compressed
                metadata = record.metadata
            
            # Decrypt if needed
            if decrypt and is_encrypted:
                data_content = await self.encryption_manager.decrypt(data_content)
            
            # Decompress if needed
            if decompress and is_compressed:
                data_content = await self.compression_manager.decompress(data_content)
            
            # Deserialize
            try:
                # Try JSON first
                data = json.loads(data_content.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Fall back to string
                data = data_content.decode('utf-8')
            
            logger.info(f"Data retrieved successfully: {storage_key}")
            return data, metadata
            
        except Exception as e:
            logger.error(f"Data retrieval failed for {storage_key}: {e}")
            raise DataStorageError(f"Failed to retrieve data: {e}")


class DataHandler:
    """Main data handler orchestrating all data operations."""
    
    def __init__(
        self,
        encryption_manager: Optional[EncryptionManager] = None,
        compression_manager: Optional[CompressionManager] = None
    ):
        self.transformer = DataTransformer()
        self.validator = DataValidator()
        self.storage = DataStorage(
            encryption_manager or EncryptionManager(),
            compression_manager or CompressionManager()
        )
        logger.info("Data Handler initialized successfully")
    
    async def process_data(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        data_type: DataType,
        operation: DataOperation,
        schema_name: Optional[str] = None,
        transform_platform: Optional[str] = None,
        storage_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process data through validation, transformation, and storage.
        
        Args:
            data: Data to process
            data_type: Type of data
            operation: Operation to perform
            schema_name: Schema for validation
            transform_platform: Platform for transformation
            storage_options: Storage configuration
            
        Returns:
            Processing result
        """
        try:
            start_time = datetime.utcnow()
            result = {
                'operation': operation.value,
                'data_type': data_type.value,
                'timestamp': start_time.isoformat(),
                'success': False
            }
            
            # Transform data if platform specified
            if transform_platform and operation in [DataOperation.CREATE, DataOperation.TRANSFORM]:
                data = await self.transformer.transform_platform_data(data, transform_platform)
                result['transformed'] = True
            
            # Validate data if schema specified
            if schema_name and operation in [DataOperation.CREATE, DataOperation.VALIDATE]:
                is_valid, errors, metrics = await self.validator.validate_data(data, schema_name)
                result['validation'] = {
                    'is_valid': is_valid,
                    'errors': errors,
                    'metrics': asdict(metrics)
                }
                
                if not is_valid:
                    result['success'] = False
                    return result
            
            # Store data if requested
            if operation in [DataOperation.CREATE, DataOperation.UPDATE] and storage_options:
                storage_key = storage_options.get('key', str(uuid.uuid4()))
                storage_info = await self.storage.store_data(
                    data, storage_key, data_type, **storage_options
                )
                result['storage'] = storage_info
            
            # Process specific operations
            if operation == DataOperation.AGGREGATE:
                aggregation_type = storage_options.get('aggregation_type', 'basic') if storage_options else 'basic'
                aggregated_data = await self.transformer.aggregate_data(data, aggregation_type)
                result['aggregated_data'] = aggregated_data
            
            result['success'] = True
            result['processing_time'] = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"Data processing completed successfully: {operation.value}")
            return result
            
        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            raise DataHandlingError(f"Failed to process data: {e}")
    
    async def handle_content_metadata(
        self,
        metadata: Dict[str, Any],
        content_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Handle content metadata processing."""
        try:
            # Validate with Pydantic model
            content_model = ContentMetadataModel(**metadata)
            
            # Process through data handler
            result = await self.process_data(
                data=content_model.dict(),
                data_type=DataType.MEDIA_METADATA,
                operation=DataOperation.CREATE,
                schema_name='content_metadata',
                storage_options={
                    'key': f"content_metadata_{content_id or uuid.uuid4()}",
                    'compress': True,
                    'encrypt': False
                }
            )
            
            return result
            
        except ValidationError as e:
            logger.error(f"Content metadata validation failed: {e}")
            raise DataValidationError(f"Invalid content metadata: {e}")
    
    async def handle_financial_data(
        self,
        financial_data: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """Handle financial data processing."""
        try:
            # Validate with Pydantic model
            financial_model = FinancialDataModel(**financial_data)
            
            # Process through data handler
            result = await self.process_data(
                data=financial_model.dict(),
                data_type=DataType.FINANCIAL,
                operation=DataOperation.CREATE,
                schema_name='financial_data',
                storage_options={
                    'key': f"financial_{user_id}_{uuid.uuid4()}",
                    'compress': True,
                    'encrypt': True  # Financial data should be encrypted
                }
            )
            
            return result
            
        except ValidationError as e:
            logger.error(f"Financial data validation failed: {e}")
            raise DataValidationError(f"Invalid financial data: {e}")
    
    async def handle_analytics_data(
        self,
        analytics_data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Handle analytics data processing."""
        try:
            # Handle single record or batch
            if isinstance(analytics_data, dict):
                analytics_model = AnalyticsDataModel(**analytics_data)
                data_to_process = analytics_model.dict()
            else:
                validated_records = []
                for record in analytics_data:
                    analytics_model = AnalyticsDataModel(**record)
                    validated_records.append(analytics_model.dict())
                data_to_process = validated_records
            
            # Process through data handler
            result = await self.process_data(
                data=data_to_process,
                data_type=DataType.ANALYTICS,
                operation=DataOperation.CREATE,
                storage_options={
                    'key': f"analytics_{uuid.uuid4()}",
                    'compress': True,
                    'encrypt': False,
                    'aggregation_type': 'user_analytics'
                }
            )
            
            return result
            
        except ValidationError as e:
            logger.error(f"Analytics data validation failed: {e}")
            raise DataValidationError(f"Invalid analytics data: {e}")
    
    async def retrieve_data(
        self,
        storage_key: str,
        data_type: Optional[DataType] = None
    ) -> Dict[str, Any]:
        """Retrieve processed data."""
        try:
            data, metadata = await self.storage.retrieve_data(
                storage_key, decrypt=True, decompress=True
            )
            
            return {
                'storage_key': storage_key,
                'data': data,
                'metadata': metadata,
                'retrieved_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Data retrieval failed: {e}")
            raise


# Factory function
def create_data_handler(
    encryption_manager: Optional[EncryptionManager] = None,
    compression_manager: Optional[CompressionManager] = None
) -> DataHandler:
    """Create and return a DataHandler instance."""
    return DataHandler(
        encryption_manager=encryption_manager,
        compression_manager=compression_manager
    )
