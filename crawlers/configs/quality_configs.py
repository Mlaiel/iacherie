"""
Quality Assurance and Validation Configurations
===============================================

Advanced quality control system for crawler operations and content validation.
Ensures data integrity, accuracy, and reliability across all crawling activities.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Engineer + DevOps + DBA + Security + Microservices Expert
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Project: IA Influencer Agent - Advanced Content Protection Platform
Contact: mlaiel@live.de | www.fahed-mlaiel.de

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, modification, or distribution is strictly prohibited.
Legal action will be taken against violators.
"""

import os
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
from pathlib import Path

class QualityLevel(Enum):
    """Quality levels for different validation requirements."""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    BLOCKER = "blocker"

class DataQualityMetric(Enum):
    """Data quality metrics."""
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"
    INTEGRITY = "integrity"
    PRECISION = "precision"

class ValidationRule(Enum):
    """Types of validation rules."""
    REQUIRED_FIELD = "required_field"
    DATA_TYPE = "data_type"
    FORMAT_PATTERN = "format_pattern"
    VALUE_RANGE = "value_range"
    ENUM_VALUES = "enum_values"
    CUSTOM_LOGIC = "custom_logic"
    CROSS_REFERENCE = "cross_reference"
    BUSINESS_RULE = "business_rule"

@dataclass
class QualityMetric:
    """Configuration for individual quality metrics."""
    name: str
    metric_type: DataQualityMetric
    threshold: float  # 0.0 to 1.0
    weight: float = 1.0
    enabled: bool = True
    description: str = ""
    
    # Calculation method
    calculation_method: str = "percentage"  # percentage, count, ratio
    aggregation_period: str = "daily"  # hourly, daily, weekly, monthly
    
    # Alert settings
    alert_threshold: float = 0.8
    critical_threshold: float = 0.6
    alert_enabled: bool = True
    
    # Trend analysis
    trend_analysis: bool = True
    baseline_period_days: int = 30
    deviation_threshold: float = 0.1

@dataclass
class ValidationRuleConfig:
    """Configuration for validation rules."""
    rule_id: str
    rule_type: ValidationRule
    field_name: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    enabled: bool = True
    
    # Rule parameters
    required: bool = False
    data_type: Optional[str] = None
    format_pattern: Optional[str] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: List[Any] = field(default_factory=list)
    custom_validator: Optional[str] = None
    
    # Error handling
    error_message: str = "Validation failed"
    auto_fix_enabled: bool = False
    fix_strategy: str = "none"  # none, default_value, skip, transform
    default_value: Any = None
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)
    conditional_logic: Optional[str] = None

@dataclass
class ContentQualityConfig:
    """Configuration for content quality assessment."""
    enabled: bool = True
    
    # Audio quality checks
    audio_quality_enabled: bool = True
    min_audio_bitrate: int = 128  # kbps
    max_audio_duration: int = 3600  # seconds
    supported_audio_formats: List[str] = field(default_factory=lambda: [
        "mp3", "wav", "flac", "aac", "ogg", "m4a"
    ])
    
    # Video quality checks
    video_quality_enabled: bool = True
    min_video_resolution: str = "720p"
    max_video_size_mb: int = 500
    supported_video_formats: List[str] = field(default_factory=lambda: [
        "mp4", "avi", "mov", "webm", "mkv", "flv"
    ])
    
    # Image quality checks
    image_quality_enabled: bool = True
    min_image_resolution: str = "800x600"
    max_image_size_mb: int = 10
    supported_image_formats: List[str] = field(default_factory=lambda: [
        "jpg", "jpeg", "png", "gif", "webp", "bmp"
    ])
    
    # Text quality checks
    text_quality_enabled: bool = True
    min_text_length: int = 10
    max_text_length: int = 10000
    language_detection: bool = True
    sentiment_analysis: bool = True
    
    # Content verification
    duplicate_detection: bool = True
    plagiarism_check: bool = True
    copyright_verification: bool = True
    content_safety_check: bool = True

@dataclass
class DataIntegrityConfig:
    """Configuration for data integrity checks."""
    enabled: bool = True
    
    # Database integrity
    referential_integrity: bool = True
    foreign_key_checks: bool = True
    constraint_validation: bool = True
    data_consistency_checks: bool = True
    
    # Data transformation integrity
    transformation_validation: bool = True
    schema_validation: bool = True
    data_lineage_tracking: bool = True
    checksum_verification: bool = True
    
    # Backup and recovery
    backup_integrity_checks: bool = True
    recovery_testing: bool = True
    data_corruption_detection: bool = True
    
    # Real-time monitoring
    real_time_integrity_checks: bool = True
    integrity_alert_threshold: float = 0.95
    auto_repair_enabled: bool = False

@dataclass
class PerformanceQualityConfig:
    """Configuration for performance quality monitoring."""
    enabled: bool = True
    
    # Response time monitoring
    response_time_monitoring: bool = True
    max_response_time_ms: int = 5000
    average_response_time_threshold: int = 2000
    
    # Throughput monitoring
    throughput_monitoring: bool = True
    min_requests_per_second: int = 10
    max_requests_per_second: int = 1000
    
    # Resource utilization
    cpu_monitoring: bool = True
    memory_monitoring: bool = True
    disk_monitoring: bool = True
    network_monitoring: bool = True
    
    # Error rate monitoring
    error_rate_monitoring: bool = True
    max_error_rate_percent: float = 5.0
    critical_error_rate_percent: float = 10.0
    
    # Availability monitoring
    availability_monitoring: bool = True
    min_availability_percent: float = 99.0
    downtime_alert_threshold_minutes: int = 5

@dataclass
class QualityReportConfig:
    """Configuration for quality reporting."""
    enabled: bool = True
    
    # Report types
    daily_reports: bool = True
    weekly_reports: bool = True
    monthly_reports: bool = True
    on_demand_reports: bool = True
    
    # Report content
    quality_metrics_summary: bool = True
    trend_analysis: bool = True
    issue_breakdown: bool = True
    recommendations: bool = True
    
    # Report delivery
    email_reports: bool = True
    dashboard_reports: bool = True
    api_reports: bool = True
    file_exports: bool = True
    
    # Report formats
    supported_formats: List[str] = field(default_factory=lambda: [
        "html", "pdf", "csv", "json", "xml"
    ])
    
    # Recipients
    report_recipients: List[str] = field(default_factory=list)
    escalation_recipients: List[str] = field(default_factory=list)

class QualityConfigManager:
    """Manager for quality assurance configurations."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize quality configuration manager."""
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent
        self.quality_metrics: Dict[str, QualityMetric] = {}
        self.validation_rules: Dict[str, ValidationRuleConfig] = {}
        self.content_quality = ContentQualityConfig()
        self.data_integrity = DataIntegrityConfig()
        self.performance_quality = PerformanceQualityConfig()
        self.reporting = QualityReportConfig()
        self._load_configurations()
        self._setup_default_metrics()
        self._setup_default_rules()
    
    def _load_configurations(self) -> None:
        """Load quality configurations from files."""



        try:
            config_file = self.config_dir / "quality_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Load configurations from file
                    for metric_id, metric_data in data.get('metrics', {}).items():
                        self.quality_metrics[metric_id] = QualityMetric(**metric_data)
        except Exception as e:
            print(f"Error loading quality configurations: {e}")
    
    def _setup_default_metrics(self) -> None:
        """Setup default quality metrics."""
        default_metrics = [
            QualityMetric(
                name="Data Completeness",
                metric_type=DataQualityMetric.COMPLETENESS,
                threshold=0.95,
                weight=1.0,
                description="Percentage of required fields that are populated"
            ),
            QualityMetric(
                name="Data Accuracy",
                metric_type=DataQualityMetric.ACCURACY,
                threshold=0.98,
                weight=1.2,
                description="Accuracy of data values against known sources"
            ),
            QualityMetric(
                name="Data Consistency",
                metric_type=DataQualityMetric.CONSISTENCY,
                threshold=0.99,
                weight=1.1,
                description="Consistency of data across different sources"
            ),
            QualityMetric(
                name="Data Timeliness",
                metric_type=DataQualityMetric.TIMELINESS,
                threshold=0.90,
                weight=0.8,
                description="Freshness and currency of data"
            )
        ]
        
        for metric in default_metrics:
            if metric.name not in self.quality_metrics:
                self.quality_metrics[metric.name] = metric
    
    def _setup_default_rules(self) -> None:
        """Setup default validation rules."""
        default_rules = [
            ValidationRuleConfig(
                rule_id="content_url_required",
                rule_type=ValidationRule.REQUIRED_FIELD,
                field_name="content_url",
                severity=ValidationSeverity.ERROR,
                required=True,
                error_message="Content URL is required"
            ),
            ValidationRuleConfig(
                rule_id="content_type_enum",
                rule_type=ValidationRule.ENUM_VALUES,
                field_name="content_type",
                severity=ValidationSeverity.ERROR,
                allowed_values=["audio", "video", "image", "text"],
                error_message="Invalid content type"
            ),
            ValidationRuleConfig(
                rule_id="file_size_range",
                rule_type=ValidationRule.VALUE_RANGE,
                field_name="file_size",
                severity=ValidationSeverity.WARNING,
                min_value=1024,  # 1KB
                max_value=104857600,  # 100MB
                error_message="File size must be between 1KB and 100MB"
            )
        ]
        
        for rule in default_rules:
            if rule.rule_id not in self.validation_rules:
                self.validation_rules[rule.rule_id] = rule
    
    def add_quality_metric(self, metric: QualityMetric) -> None:
        """Add a new quality metric."""
        self.quality_metrics[metric.name] = metric
        self._save_configurations()
    
    def add_validation_rule(self, rule: ValidationRuleConfig) -> None:
        """Add a new validation rule."""
        self.validation_rules[rule.rule_id] = rule
        self._save_configurations()
    
    def get_quality_metrics(self, enabled_only: bool = True) -> List[QualityMetric]:
        """Get quality metrics."""
        metrics = list(self.quality_metrics.values())
        if enabled_only:
            metrics = [m for m in metrics if m.enabled]
        return metrics
    
    def get_validation_rules(self, field_name: Optional[str] = None) -> List[ValidationRuleConfig]:
        """Get validation rules, optionally filtered by field name."""
        rules = list(self.validation_rules.values())
        if field_name:
            rules = [r for r in rules if r.field_name == field_name]
        return [r for r in rules if r.enabled]
    
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against configured rules."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "score": 1.0
        }
        
        for rule in self.get_validation_rules():
            result = self._apply_validation_rule(data, rule)
            if not result["valid"]:
                validation_result["valid"] = False
                if rule.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL, ValidationSeverity.BLOCKER]:
                    validation_result["errors"].append(result["message"])
                else:
                    validation_result["warnings"].append(result["message"])
        
        # Calculate quality score
        total_rules = len(self.get_validation_rules())
        if total_rules > 0:
            failed_rules = len(validation_result["errors"]) + len(validation_result["warnings"])
            validation_result["score"] = max(0.0, 1.0 - (failed_rules / total_rules))
        
        return validation_result
    
    def _apply_validation_rule(self, data: Dict[str, Any], rule: ValidationRuleConfig) -> Dict[str, Any]:
        """Apply a single validation rule to data."""
        result = {"valid": True, "message": ""}
        field_value = data.get(rule.field_name)
        
        try:
            if rule.rule_type == ValidationRule.REQUIRED_FIELD and rule.required:
                if field_value is None or field_value == "":
                    result["valid"] = False
                    result["message"] = f"Required field '{rule.field_name}' is missing"
            
            elif rule.rule_type == ValidationRule.DATA_TYPE and field_value is not None:
                if rule.data_type and not isinstance(field_value, eval(rule.data_type)):
                    result["valid"] = False
                    result["message"] = f"Field '{rule.field_name}' must be of type {rule.data_type}"
            
            elif rule.rule_type == ValidationRule.VALUE_RANGE and field_value is not None:
                if rule.min_value is not None and field_value < rule.min_value:
                    result["valid"] = False
                    result["message"] = f"Field '{rule.field_name}' must be >= {rule.min_value}"
                elif rule.max_value is not None and field_value > rule.max_value:
                    result["valid"] = False
                    result["message"] = f"Field '{rule.field_name}' must be <= {rule.max_value}"
            
            elif rule.rule_type == ValidationRule.ENUM_VALUES and field_value is not None:
                if rule.allowed_values and field_value not in rule.allowed_values:
                    result["valid"] = False
                    result["message"] = f"Field '{rule.field_name}' must be one of {rule.allowed_values}"
            
        except Exception as e:
            result["valid"] = False
            result["message"] = f"Validation error for '{rule.field_name}': {str(e)}"
        
        return result
    
    def calculate_quality_score(self, metrics_data: Dict[str, float]) -> float:
        """Calculate overall quality score based on metrics."""
        total_weight = sum(metric.weight for metric in self.get_quality_metrics())
        if total_weight == 0:
            return 1.0
        
        weighted_score = 0.0
        for metric in self.get_quality_metrics():
            metric_value = metrics_data.get(metric.name, 0.0)
            metric_score = min(1.0, metric_value / metric.threshold) if metric.threshold > 0 else 1.0
            weighted_score += metric_score * metric.weight
        
        return weighted_score / total_weight
    
    def get_quality_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive quality report."""
        report = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "overall_score": 0.0,
                "total_issues": 0,
                "critical_issues": 0,
                "resolved_issues": 0
            },
            "metrics": {},
            "issues": [],
            "recommendations": []
        }
        
        # This would be implemented with actual data collection
        # For now, return template structure
        return report
    
    def _save_configurations(self) -> None:
        """Save configurations to file."""



        try:
            config_file = self.config_dir / "quality_config.json"
            config_data = {
                "metrics": {
                    name: {
                        "name": metric.name,
                        "metric_type": metric.metric_type.value,
                        "threshold": metric.threshold,
                        "weight": metric.weight,
                        "enabled": metric.enabled,
                        "description": metric.description
                    }
                    for name, metric in self.quality_metrics.items()
                },
                "rules": {
                    rule_id: {
                        "rule_id": rule.rule_id,
                        "rule_type": rule.rule_type.value,
                        "field_name": rule.field_name,
                        "severity": rule.severity.value,
                        "enabled": rule.enabled,
                        "error_message": rule.error_message
                    }
                    for rule_id, rule in self.validation_rules.items()
                }
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving quality configurations: {e}")

# Global quality configuration manager
quality_config_manager = QualityConfigManager()

# Quality presets for different environments
QUALITY_PRESETS = {
    "development": {
        "validation_enabled": True,
        "strict_validation": False,
        "performance_monitoring": False,
        "detailed_reporting": False
    },
    "staging": {
        "validation_enabled": True,
        "strict_validation": True,
        "performance_monitoring": True,
        "detailed_reporting": True
    },
    "production": {
        "validation_enabled": True,
        "strict_validation": True,
        "performance_monitoring": True,
        "detailed_reporting": True,
        "real_time_alerts": True
    }
}
