"""Data Processing Utilities for IA Influencer Agent Platform
Advanced data transformation, validation, and processing pipelines

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent Platform with Multi-Content Protection
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import csv
import logging
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import hashlib
import pickle
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, chi2
import joblib

logger = logging.getLogger(__name__)


class DataFormat(Enum):
    """
Data format enumeration"""

    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    EXCEL = "excel"
    XML = "xml"
    YAML = "yaml"


class ProcessingMode(Enum):
    """Data processing mode"""

    BATCH = "batch"
    STREAM = "stream"
    REAL_TIME = "real_time"


class ValidationLevel(Enum):
    """Data validation level"""

    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    ENTERPRISE = "enterprise"


@dataclass
class ProcessingStats:
    """Data processing statistics"""
    records_processed: int = 0
    records_validated: int = 0
    records_rejected: int = 0
    processing_time: float = 0.0
    memory_usage: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def success_rate(self) -> float:
        """
Calculate processing success rate"""
        total = self.records_processed
        return (self.records_validated / total) if total > 0 else 0.0


@dataclass
class DataSchema:
    """
Data schema definition"""
    fields: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    required_fields: List[str] = field(default_factory=list)
    validation_rules: Dict[str, List[Callable]] = field(default_factory=dict)
    transformations: Dict[str, Callable] = field(default_factory=dict)
    
    def add_field(self, name: str, field_type: Type, required: bool = False, 
                  validators: Optional[List[Callable]] = None):
        """
Add field definition to schema"""
        self.fields[name] = {
            'type': field_type,
            'required': required,
            'validators': validators or []
        }
        
        if required:
            self.required_fields.append(name)
        
        if validators:
            self.validation_rules[name] = validators


class DataTransformer:
    """
Advanced data transformation engine"""
    
    def __init__(self):
        self.transformation_cache = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_selectors = {}
        
    async def transform_dataset(self, data: pd.DataFrame, 
                              transformations: Dict[str, Any]) -> pd.DataFrame:
        """
Apply comprehensive data transformations"""
        try:
            transformed_data = data.copy()
            
            for transform_name, config in transformations.items():
                transform_func = getattr(self, f"_apply_{transform_name}", None)
                
                if transform_func:
                    transformed_data = await transform_func(transformed_data, config)
                else:
                    logger.warning(f"Unknown transformation: {transform_name}")
            
            return transformed_data
            
        except Exception as e:
            logger.error(f"Data transformation failed: {str(e)}")
            raise DataProcessingError(f"Transformation failed: {str(e)}")
    
    async def _apply_normalization(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Apply data normalization"""
        method = config.get('method', 'standard')
        columns = config.get('columns', data.select_dtypes(include=[np.number]).columns.tolist())
        
        if method == 'standard':
            scaler_key = f"standard_{hash(tuple(columns))}"
            
            if scaler_key not in self.scalers:
                self.scalers[scaler_key] = StandardScaler()
                data[columns] = self.scalers[scaler_key].fit_transform(data[columns])
            else:
                data[columns] = self.scalers[scaler_key].transform(data[columns])
                
        elif method == 'minmax':
            scaler_key = f"minmax_{hash(tuple(columns))}"
            
            if scaler_key not in self.scalers:
                self.scalers[scaler_key] = MinMaxScaler()
                data[columns] = self.scalers[scaler_key].fit_transform(data[columns])
            else:
                data[columns] = self.scalers[scaler_key].transform(data[columns])
        
        return data
    
    async def _apply_encoding(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Apply categorical encoding"""
        method = config.get('method', 'label')
        columns = config.get('columns', data.select_dtypes(include=['object']).columns.tolist())
        
        for column in columns:
            if column not in data.columns:
                continue
                
            encoder_key = f"{method}_{column}"
            
            if method == 'label':
                if encoder_key not in self.encoders:
                    self.encoders[encoder_key] = LabelEncoder()
                    data[column] = self.encoders[encoder_key].fit_transform(data[column].astype(str))
                else:
                    data[column] = self.encoders[encoder_key].transform(data[column].astype(str))
                    
            elif method == 'onehot':
                if encoder_key not in self.encoders:
                    dummies = pd.get_dummies(data[column], prefix=column)
                    self.encoders[encoder_key] = dummies.columns.tolist()
                    data = pd.concat([data.drop(column, axis=1), dummies], axis=1)
                else:
                    # For existing encoder, ensure consistent columns
                    dummies = pd.get_dummies(data[column], prefix=column)
                    for col in self.encoders[encoder_key]:
                        if col not in dummies.columns:
                            dummies[col] = 0
                    dummies = dummies[self.encoders[encoder_key]]
                    data = pd.concat([data.drop(column, axis=1), dummies], axis=1)
        
        return data
    
    async def _apply_feature_selection(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Apply feature selection"""
        method = config.get('method', 'k_best')
        k_features = config.get('k', 10)
        target_column = config.get('target_column')
        
        if not target_column or target_column not in data.columns:
            logger.warning("Feature selection requires valid target column")
            return data
        
        feature_columns = [col for col in data.columns if col != target_column]
        
        if method == 'k_best':
            selector_key = f"kbest_{k_features}_{target_column}"
            
            if selector_key not in self.feature_selectors:
                self.feature_selectors[selector_key] = SelectKBest(chi2, k=k_features)
                X_selected = self.feature_selectors[selector_key].fit_transform(
                    data[feature_columns], data[target_column]
                )
                selected_features = [feature_columns[i] for i in 
                                   self.feature_selectors[selector_key].get_support(indices=True)]
            else:
                X_selected = self.feature_selectors[selector_key].transform(data[feature_columns])
                selected_features = self.feature_selectors[selector_key].feature_names_in_
            
            # Create new dataframe with selected features
            result_data = pd.DataFrame(X_selected, columns=selected_features, index=data.index)
            result_data[target_column] = data[target_column]
            return result_data
        
        return data
    
    async def _apply_outlier_removal(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Remove outliers from dataset"""
        method = config.get('method', 'iqr')
        columns = config.get('columns', data.select_dtypes(include=[np.number]).columns.tolist())
        
        if method == 'iqr':
            for column in columns:
                if column not in data.columns:
                    continue
                    
                Q1 = data[column].quantile(0.25)
                Q3 = data[column].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                data = data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]
        
        elif method == 'zscore':
            threshold = config.get('threshold', 3)
            for column in columns:
                if column not in data.columns:
                    continue
                    
                z_scores = np.abs((data[column] - data[column].mean()) / data[column].std())
                data = data[z_scores < threshold]
        
        return data
    
    def save_transformers(self, filepath: str):
        """
Save trained transformers to disk"""
        transformers = {
            'scalers': self.scalers,
            'encoders': self.encoders,
            'feature_selectors': self.feature_selectors
        }
        
        joblib.dump(transformers, filepath)
        logger.info(f"Transformers saved to {filepath}")
    
    def load_transformers(self, filepath: str):
        """Load trained transformers from disk"""
        if Path(filepath).exists():
            transformers = joblib.load(filepath)
            self.scalers = transformers.get('scalers', {})
            self.encoders = transformers.get('encoders', {})
            self.feature_selectors = transformers.get('feature_selectors', {})
            logger.info(f"Transformers loaded from {filepath}")
        else:
            logger.warning(f"Transformer file not found: {filepath}")


class DataValidator:
    """Comprehensive data validation engine"""
    
    def __init__(self):
        self.validation_rules = {}
        self.custom_validators = {}
        
    def register_validator(self, name: str, validator_func: Callable):
        """
Register custom validator function"""
        self.custom_validators[name] = validator_func
    
    async def validate_dataset(self, data: pd.DataFrame, schema: DataSchema, 
                             level: ValidationLevel = ValidationLevel.STANDARD) -> Dict[str, Any]:
        """
Validate dataset against schema"""
        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'stats': {
                    'total_records': len(data),
                    'valid_records': 0,
                    'invalid_records': 0
                }
            }
            
            # Check required fields
            missing_required = set(schema.required_fields) - set(data.columns)
            if missing_required:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Missing required fields: {list(missing_required)}")
            
            # Validate each field
            valid_mask = pd.Series(True, index=data.index)
            
            for field_name, field_config in schema.fields.items():
                if field_name not in data.columns:
                    continue
                
                field_validation = await self._validate_field(
                    data[field_name], field_config, level
                )
                
                if not field_validation['valid']:
                    validation_result['errors'].extend(field_validation['errors'])
                    valid_mask &= field_validation['valid_mask']
                
                validation_result['warnings'].extend(field_validation.get('warnings', []))
            
            # Update statistics
            validation_result['stats']['valid_records'] = valid_mask.sum()
            validation_result['stats']['invalid_records'] = len(data) - valid_mask.sum()
            
            if validation_result['stats']['invalid_records'] > 0:
                validation_result['valid'] = False
            
            validation_result['valid_data'] = data[valid_mask]
            validation_result['invalid_data'] = data[~valid_mask]
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Data validation failed: {str(e)}")
            raise DataProcessingError(f"Validation failed: {str(e)}")
    
    async def _validate_field(self, series: pd.Series, field_config: Dict[str, Any], 
                            level: ValidationLevel) -> Dict[str, Any]:
        """Validate individual field"""
        field_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'valid_mask': pd.Series(True, index=series.index)
        }
        
        field_type = field_config.get('type')
        validators = field_config.get('validators', [])
        
        # Type validation
        if field_type:
            type_validation = self._validate_type(series, field_type)
            if not type_validation['valid']:
                field_result['valid'] = False
                field_result['errors'].extend(type_validation['errors'])
                field_result['valid_mask'] &= type_validation['valid_mask']
        
        # Custom validators
        for validator in validators:
            if callable(validator):
                try:
                    validator_result = validator(series)
                    if not validator_result.get('valid', True):
                        field_result['valid'] = False
                        field_result['errors'].extend(validator_result.get('errors', []))
                        if 'valid_mask' in validator_result:
                            field_result['valid_mask'] &= validator_result['valid_mask']
                except Exception as e:
                    field_result['warnings'].append(f"Validator error: {str(e)}")
        
        return field_result
    
    def _validate_type(self, series: pd.Series, expected_type: Type) -> Dict[str, Any]:
        """Validate data types"""
        if expected_type == str:
            valid_mask = series.astype(str).notna()
            dtype_name = "string"
        elif expected_type == int:
            try:
                pd.to_numeric(series, errors='raise')
                valid_mask = pd.Series(True, index=series.index)
            except:
                valid_mask = pd.to_numeric(series, errors='coerce').notna()
            dtype_name = "integer"
        elif expected_type == float:
            try:
                pd.to_numeric(series, errors='raise')
                valid_mask = pd.Series(True, index=series.index)
            except:
                valid_mask = pd.to_numeric(series, errors='coerce').notna()
            dtype_name = "float"
        elif expected_type == datetime:
            try:
                pd.to_datetime(series, errors='raise')
                valid_mask = pd.Series(True, index=series.index)
            except:
                valid_mask = pd.to_datetime(series, errors='coerce').notna()
            dtype_name = "datetime"
        else:
            valid_mask = pd.Series(True, index=series.index)
            dtype_name = str(expected_type)
        
        invalid_count = (~valid_mask).sum()
        
        return {
            'valid': invalid_count == 0,
            'errors': [f"Type validation failed for {invalid_count} records, expected {dtype_name}"] if invalid_count > 0 else [],
            'valid_mask': valid_mask
        }
    
    def create_email_validator(self) -> Callable:
        """Create email validation function"""
        import re
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        def validate_email(series: pd.Series) -> Dict[str, Any]:
            valid_mask = series.astype(str).str.match(email_pattern, na=False)
            invalid_count = (~valid_mask).sum()
            
            return {
                'valid': invalid_count == 0,
                'errors': [f"Email format validation failed for {invalid_count} records"] if invalid_count > 0 else [],
                'valid_mask': valid_mask
            }
        
        return validate_email
    
    def create_range_validator(self, min_val: Optional[float] = None, 
                             max_val: Optional[float] = None) -> Callable:
        """Create numeric range validation function"""
        def validate_range(series: pd.Series) -> Dict[str, Any]:
            valid_mask = pd.Series(True, index=series.index)
            
            if min_val is not None:
                valid_mask &= (series >= min_val)
            
            if max_val is not None:
                valid_mask &= (series <= max_val)
            
            invalid_count = (~valid_mask).sum()
            
            return {
                'valid': invalid_count == 0,
                'errors': [f"Range validation failed for {invalid_count} records"] if invalid_count > 0 else [],
                'valid_mask': valid_mask
            }
        
        return validate_range


class DataNormalizer:
    """Advanced data normalization and standardization"""
    
    def __init__(self):
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
    async def normalize_influencer_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
Normalize influencer-specific data"""
        normalized_data = data.copy()
        
        # Normalize follower counts (log transformation)
        follower_columns = [col for col in data.columns if 'follower' in col.lower()]
        for col in follower_columns:
            if col in normalized_data.columns:
                normalized_data[f"{col}_log"] = np.log1p(normalized_data[col].fillna(0))
        
        # Normalize engagement rates (0-1 scale)
        engagement_columns = [col for col in data.columns if 'engagement' in col.lower()]
        for col in engagement_columns:
            if col in normalized_data.columns:
                normalized_data[col] = normalized_data[col].clip(0, 1)
        
        # Normalize content metrics
        metric_columns = ['views', 'likes', 'shares', 'comments']
        for col in metric_columns:
            if col in normalized_data.columns:
                # Z-score normalization
                mean_val = normalized_data[col].mean()
                std_val = normalized_data[col].std()
                
                if std_val > 0:
                    normalized_data[f"{col}_normalized"] = (normalized_data[col] - mean_val) / std_val
                    self.normalization_stats[f"{col}_mean"] = mean_val
                    self.normalization_stats[f"{col}_std"] = std_val
        
        return normalized_data
    
    async def normalize_content_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize content performance metrics"""
        normalized_metrics = metrics.copy()
        
        # Normalize engagement rate
        if 'engagement_rate' in metrics:
            normalized_metrics['engagement_rate'] = max(0, min(1, metrics['engagement_rate']))
        
        # Normalize view counts (log scale)
        if 'views' in metrics and metrics['views'] > 0:
            normalized_metrics['views_log'] = np.log1p(metrics['views'])
        
        # Calculate relative metrics
        total_interactions = sum([
            metrics.get('likes', 0),
            metrics.get('shares', 0),
            metrics.get('comments', 0)
        ])
        
        if total_interactions > 0:
            normalized_metrics['like_ratio'] = metrics.get('likes', 0) / total_interactions
            normalized_metrics['share_ratio'] = metrics.get('shares', 0) / total_interactions
            normalized_metrics['comment_ratio'] = metrics.get('comments', 0) / total_interactions
        
        return normalized_metrics


class BatchProcessor:
    """
High-performance batch data processing"""
    
    def __init__(self, batch_size: int = 1000, max_workers: int = 4):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    async def process_large_dataset(self, data: pd.DataFrame, 
                                  processing_func: Callable,
                                  **kwargs) -> pd.DataFrame:
        """
Process large dataset in batches"""
        try:
            num_batches = (len(data) + self.batch_size - 1) // self.batch_size
            processed_batches = []
            
            tasks = []
            for i in range(num_batches):
                start_idx = i * self.batch_size
                end_idx = min((i + 1) * self.batch_size, len(data))
                batch = data.iloc[start_idx:end_idx]
                
                # Create async task for batch processing
                task = asyncio.create_task(
                    self._process_batch(batch, processing_func, **kwargs)
                )
                tasks.append(task)
            
            # Wait for all batches to complete
            batch_results = await asyncio.gather(*tasks)
            
            # Combine results
            if batch_results:
                processed_data = pd.concat(batch_results, ignore_index=True)
            else:
                processed_data = pd.DataFrame()
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}")
            raise DataProcessingError(f"Batch processing failed: {str(e)}")
    
    async def _process_batch(self, batch: pd.DataFrame, 
                           processing_func: Callable, **kwargs) -> pd.DataFrame:
        """Process individual batch"""
        try:
            if asyncio.iscoroutinefunction(processing_func):
                result = await processing_func(batch, **kwargs)
            else:
                # Run synchronous function in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor, processing_func, batch, **kwargs
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Batch processing error: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on error


class StreamProcessor:
    """Real-time stream data processing"""
    
    def __init__(self, buffer_size: int = 100):
        self.buffer_size = buffer_size
        self.data_buffer = []
        self.processing_stats = ProcessingStats()
        
    async def process_stream_record(self, record: Dict[str, Any], 
                                  processing_func: Callable) -> Dict[str, Any]:
        """
Process individual stream record"""
        try:
            self.data_buffer.append(record)
            self.processing_stats.records_processed += 1
            
            # Process when buffer is full
            if len(self.data_buffer) >= self.buffer_size:
                await self._flush_buffer(processing_func)
            
            # Basic validation
            processed_record = await self._validate_stream_record(record)
            
            if processed_record['valid']:
                self.processing_stats.records_validated += 1
                return processed_record
            else:
                self.processing_stats.records_rejected += 1
                self.processing_stats.errors.extend(processed_record.get('errors', []))
                return processed_record
                
        except Exception as e:
            self.processing_stats.records_rejected += 1
            self.processing_stats.errors.append(str(e))
            logger.error(f"Stream processing error: {str(e)}")
            return {'valid': False, 'error': str(e)}
    
    async def _flush_buffer(self, processing_func: Callable):
        """Flush and process buffer contents"""
        if not self.data_buffer:
            return
        
        try:
            # Convert buffer to DataFrame
            df = pd.DataFrame(self.data_buffer)
            
            # Process batch
            if asyncio.iscoroutinefunction(processing_func):
                await processing_func(df)
            else:
                processing_func(df)
            
            # Clear buffer
            self.data_buffer.clear()
            
        except Exception as e:
            logger.error(f"Buffer flush error: {str(e)}")
            self.processing_stats.errors.append(f"Buffer flush error: {str(e)}")
    
    async def _validate_stream_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual stream record"""
        validation_result = {
            'valid': True,
            'errors': [],
            'record': record
        }
        
        # Basic validation
        if not isinstance(record, dict):
            validation_result['valid'] = False
            validation_result['errors'].append("Record must be a dictionary")
        
        if not record:
            validation_result['valid'] = False
            validation_result['errors'].append("Record cannot be empty")
        
        # Check for required timestamp
        if 'timestamp' not in record:
            record['timestamp'] = datetime.utcnow().isoformat()
            validation_result['warnings'] = ['Added missing timestamp']
        
        return validation_result
    
    def get_processing_stats(self) -> ProcessingStats:
        """Get current processing statistics"""
        self.processing_stats.processing_time = (
            datetime.utcnow() - self.processing_stats.start_time
        ).total_seconds()
        
        return self.processing_stats


class DataAggregator:
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
            datetime.utcnow() - self.processing_stats.start_time
        ).total_seconds()
        
        return self.processing_stats


class DataAggregator:
    """
Advanced data aggregation and summarization"""
    
    def __init__(self):
        self.aggregation_functions = {
            'sum': np.sum,
            'mean': np.mean,
            'median': np.median,
            'std': np.std,
            'min': np.min,
            'max': np.max,
            'count': len,
            'unique_count': lambda x: len(np.unique(x))
        }
    
    async def aggregate_influencer_metrics(self, data: pd.DataFrame, 
                                         group_by: List[str],
                                         metrics: List[str]) -> pd.DataFrame:
        """
Aggregate influencer metrics by specified dimensions"""
        try:
            aggregation_dict = {}
            
            for metric in metrics:
                if metric in data.columns:
                    aggregation_dict[metric] = ['sum', 'mean', 'std', 'count']
            
            aggregated = data.groupby(group_by).agg(aggregation_dict)
            
            # Flatten column names
            aggregated.columns = [f"{col[0]}_{col[1]}" for col in aggregated.columns]
            aggregated = aggregated.reset_index()
            
            return aggregated
            
        except Exception as e:
            logger.error(f"Aggregation failed: {str(e)}")
            raise DataProcessingError(f"Aggregation failed: {str(e)}")
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
    async def create_time_series_aggregation(self, data: pd.DataFrame, 
                                           timestamp_column: str,
                                           metrics: List[str],
                                           frequency: str = 'D') -> pd.DataFrame:
        """Create time series aggregation"""
        try:
            # Ensure timestamp column is datetime
            data[timestamp_column] = pd.to_datetime(data[timestamp_column])
            
            # Set timestamp as index
            data_ts = data.set_index(timestamp_column)
            
            # Resample and aggregate
            aggregated = data_ts[metrics].resample(frequency).agg({
                metric: ['sum', 'mean', 'count'] for metric in metrics
            })
            
            # Flatten columns
            aggregated.columns = [f"{col[0]}_{col[1]}" for col in aggregated.columns]
            aggregated = aggregated.reset_index()
            
            return aggregated
            
        except Exception as e:
            logger.error(f"Time series aggregation failed: {str(e)}")
            raise DataProcessingError(f"Time series aggregation failed: {str(e)}")


class DataExporter:
    """Flexible data export with multiple format support"""
    
    def __init__(self):
        self.supported_formats = [DataFormat.JSON, DataFormat.CSV, DataFormat.PARQUET, DataFormat.EXCEL]
    
    async def export_data(self, data: pd.DataFrame, 
                        filepath: str, 
                        format_type: DataFormat,
                        **kwargs) -> Dict[str, Any]:
        """
Export data to specified format"""
        try:
            export_path = Path(filepath)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format_type == DataFormat.JSON:
                data.to_json(filepath, orient='records', indent=2, **kwargs)
                
            elif format_type == DataFormat.CSV:
                data.to_csv(filepath, index=False, **kwargs)
                
            elif format_type == DataFormat.PARQUET:
                data.to_parquet(filepath, **kwargs)
                
            elif format_type == DataFormat.EXCEL:
                data.to_excel(filepath, index=False, **kwargs)
                
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
            
            # Generate export summary
            export_summary = {
                'success': True,
                'filepath': filepath,
                'format': format_type.value,
                'records_exported': len(data),
                'columns_exported': len(data.columns),
                'file_size_mb': round(export_path.stat().st_size / (1024 * 1024), 2),
                'export_time': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Data exported successfully to {filepath}")
            return export_summary
            
        except Exception as e:
            logger.error(f"Data export failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'filepath': filepath,
                'format': format_type.value
            }
    
    async def export_multiple_formats(self, data: pd.DataFrame, 
                                    base_filepath: str,
                                    formats: List[DataFormat]) -> List[Dict[str, Any]]:
        """Export data to multiple formats"""
        export_results = []
        base_path = Path(base_filepath)
        
        for format_type in formats:
            if format_type == DataFormat.JSON:
                filepath = base_path.with_suffix('.json')
            elif format_type == DataFormat.CSV:
                filepath = base_path.with_suffix('.csv')
            elif format_type == DataFormat.PARQUET:
                filepath = base_path.with_suffix('.parquet')
            elif format_type == DataFormat.EXCEL:
                filepath = base_path.with_suffix('.xlsx')
            else:
                continue
            
            result = await self.export_data(data, str(filepath), format_type)
            export_results.append(result)
        
        return export_results


class DataProcessingError(Exception):
    """
Custom exception for data processing errors"""
    pass
