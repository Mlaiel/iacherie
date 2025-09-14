"""
Enterprise Pipeline Validator for MLOps
DevOps + ML Engineer implementation with comprehensive pipeline validation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import yaml
import subprocess
import hashlib
import uuid
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

logger = logging.getLogger(__name__)


class ValidationStage(Enum):
    """Pipeline validation stages"""
    SCHEMA_VALIDATION = "schema_validation"
    DATA_QUALITY = "data_quality"
    MODEL_VALIDATION = "model_validation"
    INTEGRATION_TEST = "integration_test"
    PERFORMANCE_TEST = "performance_test"
    SECURITY_SCAN = "security_scan"
    COMPLIANCE_CHECK = "compliance_check"
    REGRESSION_TEST = "regression_test"


class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ValidationStatus(Enum):
    """Validation execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    """Validation result details"""
    validation_id: str
    stage: ValidationStage
    status: ValidationStatus
    severity: ValidationSeverity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    duration: timedelta = field(default_factory=lambda: timedelta(0))
    metrics: Dict[str, float] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)


@dataclass
class PipelineValidationConfig:
    """Pipeline validation configuration"""
    validation_stages: List[ValidationStage] = field(default_factory=lambda: list(ValidationStage))
    parallel_validation: bool = True
    fail_fast: bool = False
    timeout_minutes: int = 30
    required_accuracy_threshold: float = 0.85
    performance_threshold_ms: float = 100.0
    memory_threshold_mb: int = 1024
    security_scan_enabled: bool = True
    regression_baseline_path: Optional[str] = None
    custom_validators: List[Callable] = field(default_factory=list)


class SchemaValidator:
    """Data schema validation"""
    
    def __init__(self) -> None:
        self.schema_cache = {}
    
    async def validate_data_schema(self, data: Union[pd.DataFrame, Dict], 
                                 expected_schema: Dict[str, Any]) -> ValidationResult:
        """Validate data against expected schema"""
        try:
            validation_id = str(uuid.uuid4())
            start_time = datetime.now()
            
            issues = []
            
            if isinstance(data, pd.DataFrame):
                # Validate DataFrame schema
                for column, expected_type in expected_schema.get('columns', {}).items():
                    if column not in data.columns:
                        issues.append(f"Missing required column: {column}")
                    elif not self._check_column_type(data[column], expected_type):
                        issues.append(f"Column {column} type mismatch. Expected: {expected_type}")
                
                # Check required constraints
                constraints = expected_schema.get('constraints', {})
                for column, constraint in constraints.items():
                    if column in data.columns:
                        if constraint.get('nullable', True) is False and data[column].isnull().any():
                            issues.append(f"Column {column} contains null values but is required")
                        
                        if 'min_value' in constraint and data[column].min() < constraint['min_value']:
                            issues.append(f"Column {column} contains values below minimum: {constraint['min_value']}")
                        
                        if 'max_value' in constraint and data[column].max() > constraint['max_value']:
                            issues.append(f"Column {column} contains values above maximum: {constraint['max_value']}")
            
            elif isinstance(data, dict):
                # Validate dictionary schema
                for key, expected_type in expected_schema.get('fields', {}).items():
                    if key not in data:
                        issues.append(f"Missing required field: {key}")
                    elif not isinstance(data[key], expected_type):
                        issues.append(f"Field {key} type mismatch. Expected: {expected_type}")
            
            duration = datetime.now() - start_time
            
            if issues:
                return ValidationResult(
                    validation_id=validation_id,
                    stage=ValidationStage.SCHEMA_VALIDATION,
                    status=ValidationStatus.FAILED,
                    severity=ValidationSeverity.HIGH,
                    message=f"Schema validation failed with {len(issues)} issues",
                    details={"issues": issues},
                    duration=duration
                )
            else:
                return ValidationResult(
                    validation_id=validation_id,
                    stage=ValidationStage.SCHEMA_VALIDATION,
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.INFO,
                    message="Schema validation passed",
                    duration=duration
                )
        
        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            return ValidationResult(
                validation_id=str(uuid.uuid4()),
                stage=ValidationStage.SCHEMA_VALIDATION,
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"Schema validation error: {e}",
                details={"error": str(e)}
            )
    
    def _check_column_type(self, column: pd.Series, expected_type: str) -> bool:
        """Check if column matches expected type"""
        type_mapping = {
            'int': ['int64', 'int32', 'int16', 'int8'],
            'float': ['float64', 'float32'],
            'string': ['object'],
            'datetime': ['datetime64[ns]'],
            'bool': ['bool']
        }
        
        actual_type = str(column.dtype)
        expected_types = type_mapping.get(expected_type, [expected_type])
        return actual_type in expected_types


class ModelValidator:
    """ML model validation"""
    
    def __init__(self) -> None:
        self.baseline_metrics = {}
    
    async def validate_model_performance(self, model: Any, test_data: pd.DataFrame, 
                                       target_column: str, 
                                       threshold_config: Dict[str, float]) -> ValidationResult:
        """Validate model performance against thresholds"""
        try:
            validation_id = str(uuid.uuid4())
            start_time = datetime.now()
            
            # Extract features and target
            X_test = test_data.drop(columns=[target_column])
            y_test = test_data[target_column]
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
                'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
                'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=0)
            }
            
            # Check thresholds
            failed_metrics = []
            for metric, value in metrics.items():
                threshold = threshold_config.get(metric, 0.0)
                if value < threshold:
                    failed_metrics.append(f"{metric}: {value:.3f} < {threshold}")
            
            duration = datetime.now() - start_time
            
            if failed_metrics:
                return ValidationResult(
                    validation_id=validation_id,
                    stage=ValidationStage.MODEL_VALIDATION,
                    status=ValidationStatus.FAILED,
                    severity=ValidationSeverity.HIGH,
                    message=f"Model performance below thresholds: {'; '.join(failed_metrics)}",
                    details={"failed_metrics": failed_metrics},
                    metrics=metrics,
                    duration=duration
                )
            else:
                return ValidationResult(
                    validation_id=validation_id,
                    stage=ValidationStage.MODEL_VALIDATION,
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.INFO,
                    message="Model performance validation passed",
                    metrics=metrics,
                    duration=duration
                )
        
        except Exception as e:
            logger.error(f"Model validation error: {e}")
            return ValidationResult(
                validation_id=str(uuid.uuid4()),
                stage=ValidationStage.MODEL_VALIDATION,
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"Model validation error: {e}",
                details={"error": str(e)}
            )


class PerformanceValidator:
    """Performance validation for ML pipelines"""
    
    async def validate_inference_performance(self, model: Any, test_data: pd.DataFrame,
                                           performance_config: Dict[str, float]) -> ValidationResult:
        """Validate inference performance"""
        try:
            validation_id = str(uuid.uuid4())
            start_time = datetime.now()
            
            # Measure inference time
            inference_times = []
            batch_sizes = [1, 10, 100] if len(test_data) >= 100 else [1, min(10, len(test_data))]
            
            for batch_size in batch_sizes:
                sample_data = test_data.sample(n=batch_size, random_state=42)
                
                inference_start = datetime.now()
                _ = model.predict(sample_data)
                inference_end = datetime.now()
                
                inference_time_ms = (inference_end - inference_start).total_seconds() * 1000
                inference_times.append({
                    'batch_size': batch_size,
                    'inference_time_ms': inference_time_ms,
                    'per_sample_ms': inference_time_ms / batch_size
                })
            
            # Check performance thresholds
            max_latency_ms = performance_config.get('max_latency_ms', 1000.0)
            failed_checks = []
            
            for timing in inference_times:
                if timing['per_sample_ms'] > max_latency_ms:
                    failed_checks.append(
                        f"Batch size {timing['batch_size']}: {timing['per_sample_ms']:.2f}ms > {max_latency_ms}ms"
                    )
            
            duration = datetime.now() - start_time
            
            performance_metrics = {
                'avg_inference_time_ms': np.mean([t['per_sample_ms'] for t in inference_times]),
                'max_inference_time_ms': max([t['per_sample_ms'] for t in inference_times]),
                'batch_performance': inference_times
            }
            
            if failed_checks:
                return ValidationResult(
                    validation_id=validation_id,
                    stage=ValidationStage.PERFORMANCE_TEST,
                    status=ValidationStatus.FAILED,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"Performance validation failed: {'; '.join(failed_checks)}",
                    details={"failed_checks": failed_checks},
                    metrics=performance_metrics,
                    duration=duration
                )
            else:
                return ValidationResult(
                    validation_id=validation_id,
                    stage=ValidationStage.PERFORMANCE_TEST,
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.INFO,
                    message="Performance validation passed",
                    metrics=performance_metrics,
                    duration=duration
                )
        
        except Exception as e:
            logger.error(f"Performance validation error: {e}")
            return ValidationResult(
                validation_id=str(uuid.uuid4()),
                stage=ValidationStage.PERFORMANCE_TEST,
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"Performance validation error: {e}",
                details={"error": str(e)}
            )


class SecurityValidator:
    """Security validation for ML pipelines"""
    
    async def validate_model_security(self, model_path: str, 
                                    security_config: Dict[str, Any]) -> ValidationResult:
        """Validate model security aspects"""
        try:
            validation_id = str(uuid.uuid4())
            start_time = datetime.now()
            
            security_issues = []
            
            # Check for common security vulnerabilities
            if Path(model_path).exists():
                # Check file permissions
                file_stat = Path(model_path).stat()
                if oct(file_stat.st_mode)[-3:] != '644':
                    security_issues.append("Model file has incorrect permissions")
                
                # Check for suspicious file extensions or names
                suspicious_patterns = ['.py', '.sh', '.bat', '.exe']
                if any(pattern in model_path.lower() for pattern in suspicious_patterns):
                    security_issues.append("Model file has suspicious extension")
                
                # Check file size for potential data exfiltration
                max_size_mb = security_config.get('max_model_size_mb', 1000)
                file_size_mb = file_stat.st_size / (1024 * 1024)
                if file_size_mb > max_size_mb:
                    security_issues.append(f"Model file too large: {file_size_mb:.1f}MB > {max_size_mb}MB")
            
            # Additional security checks could be added here
            # - Dependency scanning
            # - Code injection detection
            # - Input validation checks
            
            duration = datetime.now() - start_time
            
            if security_issues:
                return ValidationResult(
                    validation_id=validation_id,
                    stage=ValidationStage.SECURITY_SCAN,
                    status=ValidationStatus.FAILED,
                    severity=ValidationSeverity.HIGH,
                    message=f"Security validation failed: {'; '.join(security_issues)}",
                    details={"security_issues": security_issues},
                    duration=duration
                )
            else:
                return ValidationResult(
                    validation_id=validation_id,
                    stage=ValidationStage.SECURITY_SCAN,
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.INFO,
                    message="Security validation passed",
                    duration=duration
                )
        
        except Exception as e:
            logger.error(f"Security validation error: {e}")
            return ValidationResult(
                validation_id=str(uuid.uuid4()),
                stage=ValidationStage.SECURITY_SCAN,
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"Security validation error: {e}",
                details={"error": str(e)}
            )


class PipelineValidator:
    """Main pipeline validation orchestrator"""
    
    def __init__(self, config -> None: PipelineValidationConfig) -> None:
        self.config = config
        self.schema_validator = SchemaValidator()
        self.model_validator = ModelValidator()
        self.performance_validator = PerformanceValidator()
        self.security_validator = SecurityValidator()
        self.validation_history = []
    
    async def validate_pipeline(self, pipeline_context: Dict[str, Any]) -> List[ValidationResult]:
        """Execute comprehensive pipeline validation"""
        try:
            logger.info("Starting pipeline validation")
            validation_results = []
            
            # Run validations based on configuration
            validation_tasks = []
            
            for stage in self.config.validation_stages:
                if stage == ValidationStage.SCHEMA_VALIDATION:
                    if 'data' in pipeline_context and 'schema' in pipeline_context:
                        task = self.schema_validator.validate_data_schema(
                            pipeline_context['data'], 
                            pipeline_context['schema']
                        )
                        validation_tasks.append(task)
                
                elif stage == ValidationStage.MODEL_VALIDATION:
                    if 'model' in pipeline_context and 'test_data' in pipeline_context:
                        thresholds = pipeline_context.get('performance_thresholds', {
                            'accuracy': self.config.required_accuracy_threshold
                        })
                        task = self.model_validator.validate_model_performance(
                            pipeline_context['model'],
                            pipeline_context['test_data'],
                            pipeline_context.get('target_column', 'target'),
                            thresholds
                        )
                        validation_tasks.append(task)
                
                elif stage == ValidationStage.PERFORMANCE_TEST:
                    if 'model' in pipeline_context and 'test_data' in pipeline_context:
                        perf_config = {
                            'max_latency_ms': self.config.performance_threshold_ms
                        }
                        task = self.performance_validator.validate_inference_performance(
                            pipeline_context['model'],
                            pipeline_context['test_data'],
                            perf_config
                        )
                        validation_tasks.append(task)
                
                elif stage == ValidationStage.SECURITY_SCAN:
                    if 'model_path' in pipeline_context:
                        security_config = {
                            'max_model_size_mb': self.config.memory_threshold_mb
                        }
                        task = self.security_validator.validate_model_security(
                            pipeline_context['model_path'],
                            security_config
                        )
                        validation_tasks.append(task)
            
            # Execute validations
            if self.config.parallel_validation:
                validation_results = await asyncio.gather(*validation_tasks, return_exceptions=True)
            else:
                for task in validation_tasks:
                    result = await task
                    validation_results.append(result)
                    
                    # Fail fast if configured
                    if self.config.fail_fast and result.status == ValidationStatus.FAILED:
                        logger.warning(f"Validation failed fast at stage: {result.stage}")
                        break
            
            # Process results
            processed_results = []
            for result in validation_results:
                if isinstance(result, Exception):
                    processed_results.append(ValidationResult(
                        validation_id=str(uuid.uuid4()),
                        stage=ValidationStage.INTEGRATION_TEST,
                        status=ValidationStatus.FAILED,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Validation task failed: {result}",
                        details={"error": str(result)}
                    ))
                else:
                    processed_results.append(result)
            
            # Store in history
            self.validation_history.extend(processed_results)
            
            # Log summary
            passed = sum(1 for r in processed_results if r.status == ValidationStatus.PASSED)
            failed = sum(1 for r in processed_results if r.status == ValidationStatus.FAILED)
            logger.info(f"Pipeline validation completed: {passed} passed, {failed} failed")
            
            return processed_results
        
        except Exception as e:
            logger.error(f"Pipeline validation error: {e}")
            return [ValidationResult(
                validation_id=str(uuid.uuid4()),
                stage=ValidationStage.INTEGRATION_TEST,
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"Pipeline validation error: {e}",
                details={"error": str(e)}
            )]
    
    async def validate_regression(self, current_metrics: Dict[str, float], 
                                baseline_metrics: Dict[str, float],
                                tolerance: float = 0.05) -> ValidationResult:
        """Validate against regression from baseline metrics"""
        try:
            validation_id = str(uuid.uuid4())
            start_time = datetime.now()
            
            regressions = []
            
            for metric, current_value in current_metrics.items():
                if metric in baseline_metrics:
                    baseline_value = baseline_metrics[metric]
                    
                    # Check for significant degradation
                    degradation = (baseline_value - current_value) / baseline_value
                    if degradation > tolerance:
                        regressions.append(
                            f"{metric}: {current_value:.3f} vs baseline {baseline_value:.3f} "
                            f"(degradation: {degradation:.1%})"
                        )
            
            duration = datetime.now() - start_time
            
            if regressions:
                return ValidationResult(
                    validation_id=validation_id,
                    stage=ValidationStage.REGRESSION_TEST,
                    status=ValidationStatus.FAILED,
                    severity=ValidationSeverity.HIGH,
                    message=f"Regression detected: {'; '.join(regressions)}",
                    details={"regressions": regressions, "tolerance": tolerance},
                    metrics=current_metrics,
                    duration=duration
                )
            else:
                return ValidationResult(
                    validation_id=validation_id,
                    stage=ValidationStage.REGRESSION_TEST,
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.INFO,
                    message="No regression detected",
                    metrics=current_metrics,
                    duration=duration
                )
        
        except Exception as e:
            logger.error(f"Regression validation error: {e}")
            return ValidationResult(
                validation_id=str(uuid.uuid4()),
                stage=ValidationStage.REGRESSION_TEST,
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"Regression validation error: {e}",
                details={"error": str(e)}
            )
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation results"""
        if not self.validation_history:
            return {"total_validations": 0}
        
        summary = {
            "total_validations": len(self.validation_history),
            "by_status": {},
            "by_stage": {},
            "by_severity": {},
            "average_duration_seconds": 0,
            "latest_validation": self.validation_history[-1].timestamp.isoformat()
        }
        
        # Count by status
        for status in ValidationStatus:
            count = sum(1 for r in self.validation_history if r.status == status)
            summary["by_status"][status.value] = count
        
        # Count by stage
        for stage in ValidationStage:
            count = sum(1 for r in self.validation_history if r.stage == stage)
            summary["by_stage"][stage.value] = count
        
        # Count by severity
        for severity in ValidationSeverity:
            count = sum(1 for r in self.validation_history if r.severity == severity)
            summary["by_severity"][severity.value] = count
        
        # Average duration
        total_seconds = sum(r.duration.total_seconds() for r in self.validation_history)
        summary["average_duration_seconds"] = total_seconds / len(self.validation_history)
        
        return summary


# Factory function
def create_pipeline_validator(
    validation_stages: Optional[List[ValidationStage]] = None,
    parallel_validation: bool = True,
    fail_fast: bool = False,
    timeout_minutes: int = 30,
    required_accuracy_threshold: float = 0.85,
    performance_threshold_ms: float = 100.0
) -> PipelineValidator:
    """Create a configured pipeline validator"""
    
    if validation_stages is None:
        validation_stages = [
            ValidationStage.SCHEMA_VALIDATION,
            ValidationStage.MODEL_VALIDATION,
            ValidationStage.PERFORMANCE_TEST,
            ValidationStage.SECURITY_SCAN
        ]
    
    config = PipelineValidationConfig(
        validation_stages=validation_stages,
        parallel_validation=parallel_validation,
        fail_fast=fail_fast,
        timeout_minutes=timeout_minutes,
        required_accuracy_threshold=required_accuracy_threshold,
        performance_threshold_ms=performance_threshold_ms
    )
    
    return PipelineValidator(config)


# Export main classes
__all__ = [
    "PipelineValidator",
    "PipelineValidationConfig", 
    "ValidationResult",
    "ValidationStage",
    "ValidationStatus",
    "ValidationSeverity",
    "create_pipeline_validator"
]