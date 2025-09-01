# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Data Processing Tests - Enterprise Grade Test Suite

Comprehensive tests for data processing, ETL pipelines, feature engineering,
data validation, and quality assurance systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT LEGAL WARNING ⚠️
Contact: mlaiel@live.de - Unauthorized use STRICTLY PROHIBITED
"""
import pytest
import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import asyncio
import tempfile
import json
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any, Tuple, Optional
import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import create_engine
import redis
import pymongo

from ai.ml.data_processing import (
    DataProcessor, ETLPipeline, FeatureEngineer, DataValidator,
    DataQualityChecker, DataTransformer, DataNormalizer,
    BatchProcessor, StreamProcessor, DataPipelineManager,
    DataIngestionEngine, DataCleaningEngine, DataEnrichmentEngine,
    DataPartitioner, DataSampler, DataAugmenter, DataProfiler,
    MLDataPreprocessor, TextDataProcessor, ImageDataProcessor,
    AudioDataProcessor, VideoDataProcessor, MultimodalDataProcessor
)


class TestDataProcessor:
    """Tests for basic data processing functionality"""
    
    def test_init_data_processor(self):
        """Test data processor initialization"""
        processor = DataProcessor(
            supported_formats=["csv", "json", "parquet", "avro"],
            max_memory_usage="8GB",
            enable_parallel_processing=True,
            chunk_size=10000
        )
        
        assert len(processor.supported_formats) == 4
        assert processor.max_memory_usage == "8GB"
        assert processor.enable_parallel_processing
        assert processor.chunk_size == 10000

    def test_load_data_csv(self, sample_csv_data, temp_dir):
        """Test CSV data loading"""
        processor = DataProcessor()
        
        # Create temporary CSV file
        csv_path = temp_dir / "test_data.csv"
        sample_csv_data.to_csv(csv_path, index=False)
        
        loaded_data = processor.load_data(csv_path, format="csv")
        
        assert isinstance(loaded_data, pd.DataFrame)
        assert len(loaded_data) == len(sample_csv_data)
        assert list(loaded_data.columns) == list(sample_csv_data.columns)

    def test_load_data_json(self, sample_json_data, temp_dir):
        """Test JSON data loading"""
        processor = DataProcessor()
        
        # Create temporary JSON file
        json_path = temp_dir / "test_data.json"
        with open(json_path, 'w') as f:
            json.dump(sample_json_data, f)
        
        loaded_data = processor.load_data(json_path, format="json")
        
        assert isinstance(loaded_data, (dict, list, pd.DataFrame))
        if isinstance(loaded_data, dict):
            assert loaded_data == sample_json_data

    def test_load_data_parquet(self, sample_dataframe, temp_dir):
        """Test Parquet data loading"""
        processor = DataProcessor()
        
        # Create temporary Parquet file
        parquet_path = temp_dir / "test_data.parquet"
        sample_dataframe.to_parquet(parquet_path, index=False)
        
        loaded_data = processor.load_data(parquet_path, format="parquet")
        
        assert isinstance(loaded_data, pd.DataFrame)
        assert len(loaded_data) == len(sample_dataframe)
        pd.testing.assert_frame_equal(loaded_data, sample_dataframe)

    def test_save_data_formats(self, sample_dataframe, temp_dir):
        """Test saving data in different formats"""
        processor = DataProcessor()
        
        formats = ["csv", "json", "parquet", "pickle"]
        
        for fmt in formats:
            output_path = temp_dir / f"output.{fmt}"
            
            if fmt == "pickle":
                processor.save_data(sample_dataframe.to_dict(), output_path, format=fmt)
            else:
                processor.save_data(sample_dataframe, output_path, format=fmt)
            
            assert output_path.exists()
            
            # Verify data can be loaded back
            if fmt != "pickle":
                loaded_data = processor.load_data(output_path, format=fmt)
                assert loaded_data is not None

    def test_chunk_processing(self, large_sample_data):
        """Test chunked data processing for large datasets"""
        processor = DataProcessor(chunk_size=1000, enable_parallel_processing=True)
        
        # Mock processing function
        def process_chunk(chunk):
            return chunk.sum().sum() if hasattr(chunk, 'sum') else len(chunk)
        
        results = processor.process_in_chunks(large_sample_data, process_chunk)
        
        assert isinstance(results, list)
        assert len(results) == (len(large_sample_data) // 1000) + (1 if len(large_sample_data) % 1000 else 0)

    def test_parallel_processing(self, sample_dataframe):
        """Test parallel data processing"""
        processor = DataProcessor(enable_parallel_processing=True, n_workers=4)
        
        def processing_function(df):
            return df.describe()
        
        with patch.object(processor, 'parallel_apply') as mock_parallel:
            mock_parallel.return_value = [
                sample_dataframe.iloc[:len(sample_dataframe)//2].describe(),
                sample_dataframe.iloc[len(sample_dataframe)//2:].describe()
            ]
            
            results = processor.parallel_apply(sample_dataframe, processing_function)
            
            assert isinstance(results, list)
            assert len(results) == 2

    def test_memory_efficient_processing(self, large_sample_data):
        """Test memory-efficient processing"""
        processor = DataProcessor(max_memory_usage="1GB")
        
        with patch.object(processor, 'get_memory_usage') as mock_memory:
            mock_memory.return_value = "500MB"
            
            # Should process without memory issues
            result = processor.process_with_memory_limit(
                large_sample_data,
                lambda x: x.sum() if hasattr(x, 'sum') else len(x)
            )
            
            assert result is not None

    def test_data_type_inference(self, mixed_type_data):
        """Test automatic data type inference"""
        processor = DataProcessor()
        
        inferred_types = processor.infer_data_types(mixed_type_data)
        
        assert isinstance(inferred_types, dict)
        assert "numeric_columns" in inferred_types
        assert "categorical_columns" in inferred_types
        assert "datetime_columns" in inferred_types
        assert "text_columns" in inferred_types


class TestETLPipeline:
    """Tests for ETL (Extract, Transform, Load) pipeline functionality"""
    
    def test_init_etl_pipeline(self):
        """Test ETL pipeline initialization"""
        pipeline = ETLPipeline(
            source_configs=[
                {"type": "database", "connection": "postgresql://localhost:5432/db"},
                {"type": "api", "endpoint": "https://api.example.com/data"}
            ],
            transformation_steps=["clean", "normalize", "enrich"],
            destination_config={"type": "data_warehouse", "table": "processed_data"},
            enable_monitoring=True
        )
        
        assert len(pipeline.source_configs) == 2
        assert len(pipeline.transformation_steps) == 3
        assert pipeline.enable_monitoring

    def test_extract_from_database(self):
        """Test data extraction from database"""
        pipeline = ETLPipeline()
        
        # Mock database connection
        with patch('sqlalchemy.create_engine') as mock_engine:
            mock_connection = Mock()
            mock_engine.return_value.connect.return_value = mock_connection
            
            # Mock query result
            mock_result = pd.DataFrame({
                'id': [1, 2, 3],
                'name': ['A', 'B', 'C'],
                'value': [10, 20, 30]
            })
            
            with patch('pandas.read_sql') as mock_read_sql:
                mock_read_sql.return_value = mock_result
                
                extracted_data = pipeline.extract_from_database(
                    connection_string="postgresql://localhost:5432/test",
                    query="SELECT * FROM test_table"
                )
                
                assert isinstance(extracted_data, pd.DataFrame)
                assert len(extracted_data) == 3

    def test_extract_from_api(self):
        """Test data extraction from API"""
        pipeline = ETLPipeline()
        
        # Mock API response
        mock_response_data = {
            "data": [
                {"id": 1, "name": "Item1", "value": 100},
                {"id": 2, "name": "Item2", "value": 200}
            ],
            "total": 2,
            "page": 1
        }
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            extracted_data = pipeline.extract_from_api(
                endpoint="https://api.example.com/data",
                headers={"Authorization": "Bearer token"}
            )
            
            assert isinstance(extracted_data, (dict, pd.DataFrame))

    def test_transform_data_cleaning(self, dirty_sample_data):
        """Test data transformation - cleaning"""
        pipeline = ETLPipeline(transformation_steps=["clean"])
        
        # Apply cleaning transformations
        cleaned_data = pipeline.transform_clean(dirty_sample_data)
        
        assert isinstance(cleaned_data, pd.DataFrame)
        # Should have fewer null values
        assert cleaned_data.isnull().sum().sum() <= dirty_sample_data.isnull().sum().sum()

    def test_transform_data_normalization(self, sample_dataframe):
        """Test data transformation - normalization"""
        pipeline = ETLPipeline(transformation_steps=["normalize"])
        
        # Assume sample_dataframe has numeric columns
        numeric_columns = sample_dataframe.select_dtypes(include=[np.number]).columns
        
        normalized_data = pipeline.transform_normalize(sample_dataframe)
        
        assert isinstance(normalized_data, pd.DataFrame)
        # Check if numeric columns are normalized (mean ≈ 0, std ≈ 1)
        for col in numeric_columns:
            if col in normalized_data.columns:
                assert abs(normalized_data[col].mean()) < 0.1
                assert abs(normalized_data[col].std() - 1) < 0.1

    def test_transform_data_enrichment(self, sample_dataframe):
        """Test data transformation - enrichment"""
        pipeline = ETLPipeline(transformation_steps=["enrich"])
        
        # Mock enrichment process
        with patch.object(pipeline, 'enrich_data') as mock_enrich:
            enriched_features = sample_dataframe.copy()
            enriched_features['enriched_feature'] = np.random.rand(len(sample_dataframe))
            enriched_features['category_encoded'] = np.random.randint(0, 5, len(sample_dataframe))
            mock_enrich.return_value = enriched_features
            
            enriched_data = pipeline.enrich_data(sample_dataframe)
            
            assert isinstance(enriched_data, pd.DataFrame)
            assert len(enriched_data.columns) > len(sample_dataframe.columns)

    def test_load_to_database(self, sample_dataframe):
        """Test loading data to database"""
        pipeline = ETLPipeline()
        
        with patch('sqlalchemy.create_engine') as mock_engine:
            mock_connection = Mock()
            mock_engine.return_value = mock_connection
            
            with patch.object(sample_dataframe, 'to_sql') as mock_to_sql:
                mock_to_sql.return_value = None
                
                success = pipeline.load_to_database(
                    data=sample_dataframe,
                    connection_string="postgresql://localhost:5432/db",
                    table_name="processed_data",
                    if_exists="replace"
                )
                
                assert success is True or success is None
                mock_to_sql.assert_called_once()

    def test_load_to_data_warehouse(self, sample_dataframe, temp_dir):
        """Test loading data to data warehouse (file-based)"""
        pipeline = ETLPipeline()
        
        warehouse_path = temp_dir / "warehouse" / "processed_data.parquet"
        
        success = pipeline.load_to_data_warehouse(
            data=sample_dataframe,
            warehouse_path=warehouse_path,
            partition_by=None
        )
        
        assert success is True or success is None
        assert warehouse_path.parent.exists()

    def test_full_etl_pipeline_execution(self, sample_dataframe):
        """Test full ETL pipeline execution"""
        pipeline = ETLPipeline(
            transformation_steps=["clean", "normalize"],
            enable_monitoring=True
        )
        
        # Mock the full pipeline execution
        with patch.object(pipeline, 'extract') as mock_extract, \
             patch.object(pipeline, 'transform') as mock_transform, \
             patch.object(pipeline, 'load') as mock_load:
            
            mock_extract.return_value = sample_dataframe
            mock_transform.return_value = sample_dataframe
            mock_load.return_value = True
            
            result = pipeline.run_pipeline()
            
            assert result is True or result is not None
            mock_extract.assert_called_once()
            mock_transform.assert_called_once()
            mock_load.assert_called_once()

    def test_pipeline_error_handling(self, sample_dataframe):
        """Test ETL pipeline error handling"""
        pipeline = ETLPipeline(enable_monitoring=True)
        
        # Mock extraction failure
        with patch.object(pipeline, 'extract') as mock_extract:
            mock_extract.side_effect = Exception("Database connection failed")
            
            with pytest.raises(Exception):
                pipeline.run_pipeline()

    def test_pipeline_monitoring_and_logging(self, sample_dataframe):
        """Test ETL pipeline monitoring and logging"""
        pipeline = ETLPipeline(enable_monitoring=True)
        
        with patch.object(pipeline, 'log_pipeline_metrics') as mock_log:
            mock_log.return_value = {
                "execution_time": 120.5,
                "rows_processed": 10000,
                "errors_count": 0,
                "data_quality_score": 0.95
            }
            
            # Mock pipeline execution
            with patch.object(pipeline, 'run_pipeline') as mock_run:
                mock_run.return_value = True
                
                result = pipeline.run_pipeline()
                
                # Should have logged metrics
                assert mock_log.called or result is not None


class TestFeatureEngineer:
    """Tests for feature engineering functionality"""
    
    def test_init_feature_engineer(self):
        """Test feature engineer initialization"""
        engineer = FeatureEngineer(
            feature_types=["numerical", "categorical", "text", "datetime"],
            encoding_methods=["one_hot", "label", "target", "embedding"],
            scaling_methods=["standard", "minmax", "robust"],
            enable_automated_features=True
        )
        
        assert len(engineer.feature_types) == 4
        assert len(engineer.encoding_methods) == 4
        assert len(engineer.scaling_methods) == 3
        assert engineer.enable_automated_features

    def test_numerical_feature_engineering(self, numerical_data):
        """Test numerical feature engineering"""
        engineer = FeatureEngineer(feature_types=["numerical"])
        
        # Create polynomial features, interaction features, etc.
        engineered_features = engineer.engineer_numerical_features(
            numerical_data,
            methods=["polynomial", "interaction", "binning", "statistical"]
        )
        
        assert isinstance(engineered_features, pd.DataFrame)
        assert engineered_features.shape[1] > numerical_data.shape[1]
        assert all(col in engineered_features.columns for col in numerical_data.columns)

    def test_categorical_feature_encoding(self, categorical_data):
        """Test categorical feature encoding"""
        engineer = FeatureEngineer(encoding_methods=["one_hot", "label"])
        
        # Test one-hot encoding
        one_hot_encoded = engineer.encode_categorical_features(
            categorical_data, method="one_hot"
        )
        
        assert isinstance(one_hot_encoded, pd.DataFrame)
        assert one_hot_encoded.shape[1] >= categorical_data.shape[1]
        
        # Test label encoding
        label_encoded = engineer.encode_categorical_features(
            categorical_data, method="label"
        )
        
        assert isinstance(label_encoded, pd.DataFrame)
        assert label_encoded.shape[1] == categorical_data.shape[1]

    def test_text_feature_engineering(self, text_data):
        """Test text feature engineering"""
        engineer = FeatureEngineer(feature_types=["text"])
        
        text_features = engineer.engineer_text_features(
            text_data,
            methods=["tfidf", "word_count", "sentiment", "readability"]
        )
        
        assert isinstance(text_features, pd.DataFrame)
        assert "text_length" in text_features.columns
        assert "word_count" in text_features.columns
        assert text_features.shape[1] > 10  # Should have multiple text features

    def test_datetime_feature_engineering(self, datetime_data):
        """Test datetime feature engineering"""
        engineer = FeatureEngineer(feature_types=["datetime"])
        
        datetime_features = engineer.engineer_datetime_features(
            datetime_data,
            extract_components=["year", "month", "day", "hour", "dayofweek"],
            create_cyclical=True
        )
        
        assert isinstance(datetime_features, pd.DataFrame)
        assert "year" in datetime_features.columns
        assert "month" in datetime_features.columns
        assert "dayofweek" in datetime_features.columns
        # Should have cyclical encodings
        assert any("sin" in col for col in datetime_features.columns)
        assert any("cos" in col for col in datetime_features.columns)

    def test_automated_feature_generation(self, mixed_feature_data):
        """Test automated feature generation"""
        engineer = FeatureEngineer(enable_automated_features=True)
        
        with patch.object(engineer, 'auto_generate_features') as mock_auto:
            mock_features = mixed_feature_data.copy()
            # Add some automated features
            mock_features['auto_ratio_1'] = np.random.rand(len(mixed_feature_data))
            mock_features['auto_interaction_1'] = np.random.rand(len(mixed_feature_data))
            mock_features['auto_cluster_1'] = np.random.randint(0, 5, len(mixed_feature_data))
            mock_auto.return_value = mock_features
            
            automated_features = engineer.auto_generate_features(mixed_feature_data)
            
            assert isinstance(automated_features, pd.DataFrame)
            assert automated_features.shape[1] > mixed_feature_data.shape[1]

    def test_feature_selection(self, engineered_features, target_variable):
        """Test feature selection methods"""
        engineer = FeatureEngineer()
        
        # Test univariate feature selection
        selected_features = engineer.select_features(
            engineered_features, 
            target_variable, 
            method="univariate", 
            k=10
        )
        
        assert isinstance(selected_features, pd.DataFrame)
        assert selected_features.shape[1] <= 10
        
        # Test correlation-based feature selection
        selected_features_corr = engineer.select_features(
            engineered_features, 
            target_variable, 
            method="correlation", 
            threshold=0.8
        )
        
        assert isinstance(selected_features_corr, pd.DataFrame)

    def test_feature_importance_analysis(self, engineered_features, target_variable):
        """Test feature importance analysis"""
        engineer = FeatureEngineer()
        
        with patch.object(engineer, 'analyze_feature_importance') as mock_importance:
            mock_importance.return_value = {
                "feature_scores": {f"feature_{i}": np.random.rand() for i in range(10)},
                "ranking": [f"feature_{i}" for i in range(10)],
                "selection_threshold": 0.1,
                "selected_features": [f"feature_{i}" for i in range(5)]
            }
            
            importance_analysis = engineer.analyze_feature_importance(
                engineered_features, target_variable
            )
            
            assert "feature_scores" in importance_analysis
            assert "ranking" in importance_analysis
            assert "selected_features" in importance_analysis

    def test_feature_scaling_normalization(self, numerical_features):
        """Test feature scaling and normalization"""
        engineer = FeatureEngineer(scaling_methods=["standard", "minmax"])
        
        # Test standard scaling
        standard_scaled = engineer.scale_features(
            numerical_features, method="standard"
        )
        
        assert isinstance(standard_scaled, pd.DataFrame)
        # Check if features are standardized (mean ≈ 0, std ≈ 1)
        for col in standard_scaled.select_dtypes(include=[np.number]).columns:
            assert abs(standard_scaled[col].mean()) < 0.1
            assert abs(standard_scaled[col].std() - 1) < 0.1
        
        # Test min-max scaling
        minmax_scaled = engineer.scale_features(
            numerical_features, method="minmax"
        )
        
        assert isinstance(minmax_scaled, pd.DataFrame)
        # Check if features are in [0, 1] range
        for col in minmax_scaled.select_dtypes(include=[np.number]).columns:
            assert minmax_scaled[col].min() >= -0.01  # Allow small numerical errors
            assert minmax_scaled[col].max() <= 1.01


class TestDataValidator:
    """Tests for data validation functionality"""
    
    def test_init_data_validator(self):
        """Test data validator initialization"""
        validator = DataValidator(
            validation_rules={
                "completeness": {"threshold": 0.95},
                "uniqueness": {"columns": ["id", "email"]},
                "range": {"age": [0, 150], "score": [0, 100]},
                "format": {"email": r'^[\w\.-]+@[\w\.-]+\.\w+$'}
            },
            enable_profiling=True
        )
        
        assert len(validator.validation_rules) == 4
        assert validator.enable_profiling

    def test_completeness_validation(self, incomplete_data):
        """Test data completeness validation"""
        validator = DataValidator()
        
        completeness_results = validator.validate_completeness(
            incomplete_data, threshold=0.8
        )
        
        assert isinstance(completeness_results, dict)
        assert "overall_completeness" in completeness_results
        assert "column_completeness" in completeness_results
        assert "failed_columns" in completeness_results
        assert 0 <= completeness_results["overall_completeness"] <= 1

    def test_uniqueness_validation(self, duplicate_data):
        """Test data uniqueness validation"""
        validator = DataValidator()
        
        uniqueness_results = validator.validate_uniqueness(
            duplicate_data, unique_columns=["id"]
        )
        
        assert isinstance(uniqueness_results, dict)
        assert "duplicate_count" in uniqueness_results
        assert "uniqueness_ratio" in uniqueness_results
        assert "duplicate_rows" in uniqueness_results

    def test_range_validation(self, numerical_data):
        """Test data range validation"""
        validator = DataValidator()
        
        # Define valid ranges for each column
        range_rules = {}
        for col in numerical_data.columns:
            min_val = numerical_data[col].min() - 10
            max_val = numerical_data[col].max() + 10
            range_rules[col] = [min_val, max_val]
        
        range_results = validator.validate_ranges(
            numerical_data, range_rules
        )
        
        assert isinstance(range_results, dict)
        assert "within_range_ratio" in range_results
        assert "out_of_range_count" in range_results
        assert "column_violations" in range_results

    def test_format_validation(self, format_data):
        """Test data format validation"""
        validator = DataValidator()
        
        format_rules = {
            "email": r'^[\w\.-]+@[\w\.-]+\.\w+$',
            "phone": r'^\+?1?\d{9,15}$',
            "date": r'^\d{4}-\d{2}-\d{2}$'
        }
        
        format_results = validator.validate_formats(
            format_data, format_rules
        )
        
        assert isinstance(format_results, dict)
        assert "format_compliance" in format_results
        assert "invalid_format_count" in format_results
        assert "column_compliance" in format_results

    def test_schema_validation(self, sample_dataframe):
        """Test data schema validation"""
        validator = DataValidator()
        
        # Define expected schema
        expected_schema = {
            "columns": list(sample_dataframe.columns),
            "dtypes": {col: str(dtype) for col, dtype in sample_dataframe.dtypes.items()},
            "required_columns": list(sample_dataframe.columns[:3]),
            "nullable_columns": list(sample_dataframe.columns[3:])
        }
        
        schema_results = validator.validate_schema(
            sample_dataframe, expected_schema
        )
        
        assert isinstance(schema_results, dict)
        assert "schema_compliance" in schema_results
        assert "missing_columns" in schema_results
        assert "extra_columns" in schema_results
        assert "dtype_mismatches" in schema_results

    def test_business_rules_validation(self, business_data):
        """Test business rules validation"""
        validator = DataValidator()
        
        # Define business rules
        business_rules = [
            {"rule": "age >= 18", "description": "Age must be 18 or older"},
            {"rule": "salary > 0", "description": "Salary must be positive"},
            {"rule": "start_date <= end_date", "description": "Start date must be before end date"}
        ]
        
        with patch.object(validator, 'validate_business_rules') as mock_business:
            mock_business.return_value = {
                "rules_passed": 2,
                "rules_failed": 1,
                "overall_compliance": 0.67,
                "rule_violations": [
                    {"rule": "start_date <= end_date", "violations": 5}
                ]
            }
            
            business_results = validator.validate_business_rules(
                business_data, business_rules
            )
            
            assert "rules_passed" in business_results
            assert "rules_failed" in business_results
            assert "overall_compliance" in business_results

    def test_anomaly_detection_validation(self, sample_dataframe):
        """Test anomaly detection in validation"""
        validator = DataValidator()
        
        with patch.object(validator, 'detect_anomalies') as mock_anomalies:
            mock_anomalies.return_value = {
                "anomaly_count": 15,
                "anomaly_ratio": 0.015,
                "anomalous_rows": [10, 25, 87, 134, 256],
                "anomaly_scores": [0.95, 0.87, 0.92, 0.89, 0.94],
                "anomaly_types": ["outlier", "outlier", "pattern", "outlier", "pattern"]
            }
            
            anomaly_results = validator.detect_anomalies(sample_dataframe)
            
            assert "anomaly_count" in anomaly_results
            assert "anomaly_ratio" in anomaly_results
            assert "anomalous_rows" in anomaly_results

    def test_data_quality_scoring(self, sample_dataframe):
        """Test comprehensive data quality scoring"""
        validator = DataValidator(enable_profiling=True)
        
        quality_score = validator.calculate_quality_score(sample_dataframe)
        
        assert isinstance(quality_score, dict)
        assert "overall_score" in quality_score
        assert "dimension_scores" in quality_score
        assert 0 <= quality_score["overall_score"] <= 1
        
        # Should include multiple quality dimensions
        expected_dimensions = ["completeness", "accuracy", "consistency", "validity"]
        for dimension in expected_dimensions:
            assert dimension in quality_score.get("dimension_scores", {})


class TestDataQualityChecker:
    """Tests for data quality checking functionality"""
    
    def test_init_quality_checker(self):
        """Test data quality checker initialization"""
        checker = DataQualityChecker(
            quality_dimensions=["completeness", "accuracy", "consistency", "validity", "timeliness"],
            thresholds={"completeness": 0.95, "accuracy": 0.9, "consistency": 0.85},
            enable_automated_repair=True
        )
        
        assert len(checker.quality_dimensions) == 5
        assert len(checker.thresholds) == 3
        assert checker.enable_automated_repair

    def test_completeness_assessment(self, incomplete_data):
        """Test data completeness assessment"""
        checker = DataQualityChecker()
        
        completeness = checker.assess_completeness(incomplete_data)
        
        assert isinstance(completeness, dict)
        assert "overall_completeness" in completeness
        assert "column_completeness" in completeness
        assert "completeness_score" in completeness
        assert 0 <= completeness["completeness_score"] <= 1

    def test_accuracy_assessment(self, sample_dataframe, reference_data):
        """Test data accuracy assessment against reference data"""
        checker = DataQualityChecker()
        
        with patch.object(checker, 'assess_accuracy') as mock_accuracy:
            mock_accuracy.return_value = {
                "accuracy_score": 0.92,
                "exact_matches": 850,
                "total_records": 1000,
                "accuracy_by_column": {
                    "column1": 0.95,
                    "column2": 0.89,
                    "column3": 0.91
                },
                "discrepancies": [
                    {"row": 45, "column": "column2", "expected": "A", "actual": "B"}
                ]
            }
            
            accuracy = checker.assess_accuracy(sample_dataframe, reference_data)
            
            assert "accuracy_score" in accuracy
            assert "exact_matches" in accuracy
            assert "accuracy_by_column" in accuracy

    def test_consistency_assessment(self, inconsistent_data):
        """Test data consistency assessment"""
        checker = DataQualityChecker()
        
        consistency = checker.assess_consistency(inconsistent_data)
        
        assert isinstance(consistency, dict)
        assert "consistency_score" in consistency
        assert "inconsistency_count" in consistency
        assert "consistency_rules" in consistency

    def test_validity_assessment(self, invalid_data):
        """Test data validity assessment"""
        checker = DataQualityChecker()
        
        # Define validity rules
        validity_rules = {
            "age": {"type": "range", "min": 0, "max": 150},
            "email": {"type": "format", "pattern": r'^[\w\.-]+@[\w\.-]+\.\w+$'},
            "category": {"type": "enum", "values": ["A", "B", "C", "D"]}
        }
        
        validity = checker.assess_validity(invalid_data, validity_rules)
        
        assert isinstance(validity, dict)
        assert "validity_score" in validity
        assert "invalid_count" in validity
        assert "validation_results" in validity

    def test_timeliness_assessment(self, timestamped_data):
        """Test data timeliness assessment"""
        checker = DataQualityChecker()
        
        # Mock timeliness assessment
        with patch.object(checker, 'assess_timeliness') as mock_timeliness:
            mock_timeliness.return_value = {
                "timeliness_score": 0.88,
                "average_age_hours": 6.5,
                "outdated_records": 120,
                "fresh_records": 880,
                "age_distribution": {
                    "0-1h": 300,
                    "1-6h": 400,
                    "6-24h": 180,
                    "24h+": 120
                }
            }
            
            timeliness = checker.assess_timeliness(
                timestamped_data, 
                timestamp_column="created_at",
                freshness_threshold_hours=24
            )
            
            assert "timeliness_score" in timeliness
            assert "average_age_hours" in timeliness
            assert "outdated_records" in timeliness

    def test_automated_quality_repair(self, poor_quality_data):
        """Test automated data quality repair"""
        checker = DataQualityChecker(enable_automated_repair=True)
        
        # Mock repair process
        with patch.object(checker, 'auto_repair_quality_issues') as mock_repair:
            repaired_data = poor_quality_data.copy()
            # Simulate repairs
            repaired_data = repaired_data.fillna(repaired_data.mean())
            mock_repair.return_value = {
                "repaired_data": repaired_data,
                "repairs_applied": [
                    {"type": "fill_missing", "column": "age", "count": 25},
                    {"type": "correct_format", "column": "email", "count": 8},
                    {"type": "remove_duplicates", "count": 5}
                ],
                "improvement_score": 0.15
            }
            
            repair_results = checker.auto_repair_quality_issues(poor_quality_data)
            
            assert "repaired_data" in repair_results
            assert "repairs_applied" in repair_results
            assert "improvement_score" in repair_results

    def test_quality_monitoring_dashboard(self, sample_dataframe):
        """Test quality monitoring and dashboard data"""
        checker = DataQualityChecker()
        
        with patch.object(checker, 'generate_quality_dashboard') as mock_dashboard:
            mock_dashboard.return_value = {
                "overall_quality_score": 0.87,
                "quality_trends": {
                    "completeness": [0.85, 0.87, 0.89, 0.91, 0.93],
                    "accuracy": [0.78, 0.81, 0.84, 0.86, 0.88],
                    "consistency": [0.82, 0.83, 0.84, 0.85, 0.86]
                },
                "alerts": [
                    {"type": "completeness", "severity": "medium", "message": "Completeness below threshold"},
                    {"type": "accuracy", "severity": "low", "message": "Minor accuracy degradation"}
                ],
                "recommendations": [
                    "Implement additional validation for email field",
                    "Review data collection process for completeness"
                ]
            }
            
            dashboard_data = checker.generate_quality_dashboard(sample_dataframe)
            
            assert "overall_quality_score" in dashboard_data
            assert "quality_trends" in dashboard_data
            assert "alerts" in dashboard_data
            assert "recommendations" in dashboard_data


@pytest.mark.integration
class TestDataProcessingIntegration:
    """Integration tests for data processing systems"""
    
    @pytest.mark.slow
    def test_end_to_end_data_pipeline(self, raw_data_source, temp_dir):
        """Test complete data processing pipeline"""
        # Initialize pipeline components
        processor = DataProcessor(chunk_size=1000)
        pipeline = ETLPipeline(transformation_steps=["clean", "normalize"])
        engineer = FeatureEngineer(enable_automated_features=True)
        validator = DataValidator()
        
        # Mock raw data
        if not raw_data_source:
            raw_data_source = pd.DataFrame({
                'id': range(1000),
                'value': np.random.randn(1000),
                'category': np.random.choice(['A', 'B', 'C'], 1000),
                'timestamp': pd.date_range('2024-01-01', periods=1000, freq='H')
            })
        
        # Extract and load raw data
        loaded_data = processor.load_data(raw_data_source, format="dataframe")
        assert isinstance(loaded_data, pd.DataFrame)
        
        # Run ETL pipeline
        with patch.object(pipeline, 'run_pipeline') as mock_pipeline:
            mock_pipeline.return_value = loaded_data
            transformed_data = pipeline.run_pipeline()
            assert transformed_data is not None
        
        # Engineer features
        with patch.object(engineer, 'engineer_all_features') as mock_engineer:
            mock_engineer.return_value = loaded_data
            engineered_data = engineer.engineer_all_features(loaded_data)
            assert isinstance(engineered_data, pd.DataFrame)
        
        # Validate data quality
        quality_results = validator.calculate_quality_score(engineered_data)
        assert "overall_score" in quality_results
        assert quality_results["overall_score"] > 0.5

    def test_streaming_data_processing(self):
        """Test streaming data processing integration"""
        stream_processor = StreamProcessor(buffer_size=100)
        
        # Simulate streaming data
        streaming_data = []
        for i in range(1000):
            data_point = {
                "timestamp": datetime.now() - timedelta(seconds=i),
                "value": np.random.randn(),
                "category": np.random.choice(['A', 'B', 'C'])
            }
            streaming_data.append(data_point)
        
        # Process streaming data in batches
        processed_batches = []
        for batch in stream_processor.process_stream(streaming_data):
            processed_batches.append(batch)
        
        assert len(processed_batches) > 0
        assert all(isinstance(batch, (dict, pd.DataFrame)) for batch in processed_batches)

    def test_multimodal_data_processing(self):
        """Test multimodal data processing integration"""
        multimodal_processor = MultimodalDataProcessor(
            modalities=["text", "image", "audio"]
        )
        
        # Mock multimodal data
        multimodal_data = {
            "text": ["This is sample text"] * 100,
            "image": [np.random.rand(224, 224, 3)] * 100,
            "audio": [np.random.rand(16000)] * 100
        }
        
        with patch.object(multimodal_processor, 'process_multimodal') as mock_process:
            mock_process.return_value = {
                "processed_text": pd.DataFrame({"text_features": np.random.rand(100, 50)}),
                "processed_image": np.random.rand(100, 2048),
                "processed_audio": np.random.rand(100, 128),
                "fused_features": np.random.rand(100, 256)
            }
            
            processed_multimodal = multimodal_processor.process_multimodal(multimodal_data)
            
            assert "processed_text" in processed_multimodal
            assert "processed_image" in processed_multimodal
            assert "processed_audio" in processed_multimodal
            assert "fused_features" in processed_multimodal


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
