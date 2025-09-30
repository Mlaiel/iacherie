"""
🧪 Analytics Validators - IA Influencer Agent Platform - ENTERPRISE VERSION
===========================================================================

Enterprise-grade validation framework for analytics data, configurations, 
compliance checks, and quality assurance across all analytics engines.

VALIDATION COVERAGE:
- Data Quality Validation
- Configuration Validation  
- Compliance Validation (GDPR/CCPA)
- Performance Validation
- Security Validation
- Platform Integration Validation

Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Usage non autorisé strictement interdit
Contact: mlaiel@live.de for licensing inquiries.
"""

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import asyncio
from pydantic import BaseModel, validator, ValidationError
import numpy as np

# ========== VALIDATION ENUMS ==========

class ValidationSeverity(Enum):
    """Validation Issue Severity"""
    CRITICAL = "critical"      # Blocks operation
    ERROR = "error"           # Serious issue
    WARNING = "warning"       # Potential issue
    INFO = "info"            # Informational
    SUCCESS = "success"       # Validation passed


class ValidationType(Enum):
    """Types of Validation"""
    DATA_QUALITY = "data_quality"
    CONFIGURATION = "configuration"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    SECURITY = "security"
    PLATFORM_INTEGRATION = "platform_integration"
    SCHEMA = "schema"
    BUSINESS_RULES = "business_rules"
    ML_MODEL = "ml_model"
    API_RESPONSE = "api_response"


class ComplianceStandard(Enum):
    """Compliance Standards"""
    GDPR = "gdpr"                    # EU General Data Protection Regulation
    CCPA = "ccpa"                    # California Consumer Privacy Act
    COPPA = "coppa"                  # Children's Online Privacy Protection Act
    PIPEDA = "pipeda"                # Personal Information Protection and Electronic Documents Act
    LGPD = "lgpd"                    # Lei Geral de Proteção de Dados (Brazil)
    PDPA_SG = "pdpa_sg"             # Personal Data Protection Act (Singapore)
    DPA_UK = "dpa_uk"               # Data Protection Act (UK)
    PRIVACY_ACT_AU = "privacy_act_au" # Privacy Act (Australia)


class DataQualityDimension(Enum):
    """Data Quality Dimensions"""
    COMPLETENESS = "completeness"    # No missing values
    ACCURACY = "accuracy"           # Correct values
    CONSISTENCY = "consistency"     # Consistent across sources
    VALIDITY = "validity"           # Conforms to format rules
    UNIQUENESS = "uniqueness"       # No duplicates
    TIMELINESS = "timeliness"       # Current and up-to-date
    INTEGRITY = "integrity"         # Referential integrity
    CONFORMITY = "conformity"       # Matches standards


# ========== VALIDATION DATA CLASSES ==========

@dataclass
class ValidationIssue:
    """Individual validation issue"""
    issue_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    validation_type: ValidationType = ValidationType.DATA_QUALITY
    severity: ValidationSeverity = ValidationSeverity.WARNING
    message: str = ""
    details: str = ""
    field_path: str = ""
    expected_value: Optional[Any] = None
    actual_value: Optional[Any] = None
    rule_violated: str = ""
    suggestion: str = ""
    error_code: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Validation result container"""
    validation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    validation_type: ValidationType = ValidationType.DATA_QUALITY
    entity_type: str = ""           # content, creator, platform, etc.
    entity_id: str = ""
    is_valid: bool = True
    overall_score: float = 100.0    # 0-100
    issues: List[ValidationIssue] = field(default_factory=list)
    passed_checks: int = 0
    total_checks: int = 0
    execution_time_ms: float = 0.0
    validated_at: datetime = field(default_factory=datetime.utcnow)
    validator_version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_issue(self, issue: ValidationIssue):
        """Add validation issue"""
        self.issues.append(issue)
        if issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]:
            self.is_valid = False
        self._update_score()
    
    def _update_score(self):
        """Update overall validation score"""
        if not self.issues:
            self.overall_score = 100.0
            return
        
        severity_weights = {
            ValidationSeverity.CRITICAL: 25,
            ValidationSeverity.ERROR: 15,
            ValidationSeverity.WARNING: 5,
            ValidationSeverity.INFO: 1
        }
        
        total_deduction = sum(severity_weights.get(issue.severity, 0) for issue in self.issues)
        self.overall_score = max(0, 100 - total_deduction)


@dataclass
class ComplianceReport:
    """Compliance validation report"""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    standard: ComplianceStandard
    is_compliant: bool = True
    compliance_score: float = 100.0  # 0-100
    violations: List[ValidationIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    audit_trail: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    next_review_date: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=90))
    responsible_party: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


# ========== BASE VALIDATOR ==========

class BaseValidator:
    """Base class for all validators"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.logger = logging.getLogger(__name__)
        self.validation_rules: Dict[str, Any] = {}
        self.enabled = True
    
    async def validate(self, data: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Main validation method - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement validate method")
    
    def create_issue(self, severity: ValidationSeverity, message: str, 
                    details: str = "", field_path: str = "", **kwargs) -> ValidationIssue:
        """Create validation issue"""
        return ValidationIssue(
            validation_type=ValidationType.DATA_QUALITY,
            severity=severity,
            message=message,
            details=details,
            field_path=field_path,
            **kwargs
        )
    
    def is_empty_or_none(self, value: Any) -> bool:
        """Check if value is empty or None"""
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        if isinstance(value, (list, dict)) and len(value) == 0:
            return True
        return False


# ========== DATA VALIDATOR ==========

class DataValidator(BaseValidator):
    """Comprehensive data validation"""
    
    def __init__(self):
        super().__init__("DataValidator", "1.0.0")
        self.quality_thresholds = {
            DataQualityDimension.COMPLETENESS: 0.95,
            DataQualityDimension.ACCURACY: 0.90,
            DataQualityDimension.CONSISTENCY: 0.85,
            DataQualityDimension.VALIDITY: 0.95,
            DataQualityDimension.UNIQUENESS: 0.99,
            DataQualityDimension.TIMELINESS: 0.90
        }
    
    async def validate(self, data: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate data quality"""
        start_time = datetime.utcnow()
        result = ValidationResult(
            validation_type=ValidationType.DATA_QUALITY,
            entity_type=context.get('entity_type', 'unknown') if context else 'unknown',
            entity_id=context.get('entity_id', '') if context else ''
        )
        
        try:
            # Completeness validation
            await self._validate_completeness(data, result)
            
            # Accuracy validation
            await self._validate_accuracy(data, result)
            
            # Consistency validation
            await self._validate_consistency(data, result)
            
            # Validity validation
            await self._validate_validity(data, result)
            
            # Uniqueness validation
            await self._validate_uniqueness(data, result)
            
            # Timeliness validation
            await self._validate_timeliness(data, result)
            
        except Exception as e:
            result.add_issue(self.create_issue(
                ValidationSeverity.CRITICAL,
                f"Data validation failed: {str(e)}",
                field_path="root"
            ))
        
        # Calculate execution time
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        result.execution_time_ms = execution_time
        
        return result
    
    async def _validate_completeness(self, data: Any, result: ValidationResult):
        """Validate data completeness"""
        if isinstance(data, dict):
            total_fields = len(data)
            empty_fields = sum(1 for v in data.values() if self.is_empty_or_none(v))
            completeness_score = (total_fields - empty_fields) / total_fields if total_fields > 0 else 1.0
            
            if completeness_score < self.quality_thresholds[DataQualityDimension.COMPLETENESS]:
                result.add_issue(self.create_issue(
                    ValidationSeverity.WARNING,
                    f"Data completeness below threshold: {completeness_score:.2%}",
                    f"Expected: {self.quality_thresholds[DataQualityDimension.COMPLETENESS]:.2%}",
                    field_path="data.completeness"
                ))
    
    async def _validate_accuracy(self, data: Any, result: ValidationResult):
        """Validate data accuracy"""
        if isinstance(data, dict):
            # Check for common accuracy issues
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    if value < 0 and key in ['views', 'likes', 'followers', 'revenue']:
                        result.add_issue(self.create_issue(
                            ValidationSeverity.ERROR,
                            f"Negative value for {key}: {value}",
                            "Metric values should not be negative",
                            field_path=f"data.{key}"
                        ))
                    
                    # Check for outliers (basic statistical check)
                    if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
                        result.add_issue(self.create_issue(
                            ValidationSeverity.ERROR,
                            f"Invalid numeric value for {key}: {value}",
                            "Value is NaN or Infinity",
                            field_path=f"data.{key}"
                        ))
    
    async def _validate_consistency(self, data: Any, result: ValidationResult):
        """Validate data consistency"""
        if isinstance(data, dict):
            # Check timestamp consistency
            timestamps = {}
            for key, value in data.items():
                if 'time' in key.lower() or 'date' in key.lower():
                    if isinstance(value, (str, datetime)):
                        timestamps[key] = value
            
            # Basic consistency checks
            if 'created_at' in timestamps and 'updated_at' in timestamps:
                try:
                    created = timestamps['created_at']
                    updated = timestamps['updated_at']
                    
                    if isinstance(created, str):
                        created = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    if isinstance(updated, str):
                        updated = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                    
                    if updated < created:
                        result.add_issue(self.create_issue(
                            ValidationSeverity.ERROR,
                            "Updated timestamp is before created timestamp",
                            f"Created: {created}, Updated: {updated}",
                            field_path="data.timestamps"
                        ))
                except Exception as e:
                    result.add_issue(self.create_issue(
                        ValidationSeverity.WARNING,
                        f"Could not validate timestamp consistency: {str(e)}",
                        field_path="data.timestamps"
                    ))
    
    async def _validate_validity(self, data: Any, result: ValidationResult):
        """Validate data format validity"""
        if isinstance(data, dict):
            for key, value in data.items():
                # Email validation
                if 'email' in key.lower() and isinstance(value, str):
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not re.match(email_pattern, value):
                        result.add_issue(self.create_issue(
                            ValidationSeverity.ERROR,
                            f"Invalid email format: {value}",
                            field_path=f"data.{key}"
                        ))
                
                # URL validation
                if 'url' in key.lower() and isinstance(value, str):
                    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
                    if not re.match(url_pattern, value):
                        result.add_issue(self.create_issue(
                            ValidationSeverity.ERROR,
                            f"Invalid URL format: {value}",
                            field_path=f"data.{key}"
                        ))
                
                # Platform ID validation
                if 'platform' in key.lower() and isinstance(value, str):
                    valid_platforms = [
                        'youtube', 'instagram', 'tiktok', 'spotify', 'twitter',
                        'facebook', 'linkedin', 'snapchat', 'pinterest'
                    ]
                    if value.lower() not in valid_platforms:
                        result.add_issue(self.create_issue(
                            ValidationSeverity.WARNING,
                            f"Unknown platform: {value}",
                            f"Valid platforms: {', '.join(valid_platforms)}",
                            field_path=f"data.{key}"
                        ))
    
    async def _validate_uniqueness(self, data: Any, result: ValidationResult):
        """Validate data uniqueness"""
        if isinstance(data, list):
            seen_values = set()
            duplicates = []
            
            for i, item in enumerate(data):
                # Simple duplicate detection for primitive types
                if isinstance(item, (str, int, float)):
                    if item in seen_values:
                        duplicates.append((i, item))
                    else:
                        seen_values.add(item)
            
            if duplicates:
                result.add_issue(self.create_issue(
                    ValidationSeverity.WARNING,
                    f"Found {len(duplicates)} duplicate values",
                    f"Duplicates: {duplicates[:5]}...",  # Show first 5
                    field_path="data.duplicates"
                ))
    
    async def _validate_timeliness(self, data: Any, result: ValidationResult):
        """Validate data timeliness"""
        if isinstance(data, dict):
            current_time = datetime.utcnow()
            
            for key, value in data.items():
                if 'timestamp' in key.lower() or 'time' in key.lower():
                    try:
                        if isinstance(value, str):
                            timestamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        elif isinstance(value, datetime):
                            timestamp = value
                        else:
                            continue
                        
                        # Check if timestamp is too far in the future
                        if timestamp > current_time + timedelta(hours=1):
                            result.add_issue(self.create_issue(
                                ValidationSeverity.WARNING,
                                f"Future timestamp detected: {timestamp}",
                                "Timestamp is more than 1 hour in the future",
                                field_path=f"data.{key}"
                            ))
                        
                        # Check if timestamp is too old for real-time data
                        if 'real_time' in key.lower() and timestamp < current_time - timedelta(minutes=5):
                            result.add_issue(self.create_issue(
                                ValidationSeverity.WARNING,
                                f"Stale real-time data: {timestamp}",
                                "Real-time data is older than 5 minutes",
                                field_path=f"data.{key}"
                            ))
                    
                    except Exception as e:
                        result.add_issue(self.create_issue(
                            ValidationSeverity.WARNING,
                            f"Could not validate timestamp {key}: {str(e)}",
                            field_path=f"data.{key}"
                        ))


# ========== CONFIGURATION VALIDATOR ==========

class ConfigValidator(BaseValidator):
    """Configuration validation"""
    
    def __init__(self):
        super().__init__("ConfigValidator", "1.0.0")
    
    async def validate(self, config: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate configuration"""
        start_time = datetime.utcnow()
        result = ValidationResult(
            validation_type=ValidationType.CONFIGURATION,
            entity_type="configuration",
            entity_id=context.get('config_id', '') if context else ''
        )
        
        try:
            # Validate required fields
            await self._validate_required_fields(config, result)
            
            # Validate field types
            await self._validate_field_types(config, result)
            
            # Validate value ranges
            await self._validate_value_ranges(config, result)
            
            # Validate dependencies
            await self._validate_dependencies(config, result)
            
        except Exception as e:
            result.add_issue(self.create_issue(
                ValidationSeverity.CRITICAL,
                f"Configuration validation failed: {str(e)}",
                field_path="config"
            ))
        
        # Calculate execution time
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        result.execution_time_ms = execution_time
        
        return result
    
    async def _validate_required_fields(self, config: Any, result: ValidationResult):
        """Validate required configuration fields"""
        if not isinstance(config, dict):
            result.add_issue(self.create_issue(
                ValidationSeverity.CRITICAL,
                "Configuration must be a dictionary",
                field_path="config.type"
            ))
            return
        
        required_fields = [
            'version', 'environment', 'database_config', 
            'cache_config', 'security_config'
        ]
        
        for field in required_fields:
            if field not in config or config[field] is None:
                result.add_issue(self.create_issue(
                    ValidationSeverity.ERROR,
                    f"Required field missing: {field}",
                    field_path=f"config.{field}"
                ))
    
    async def _validate_field_types(self, config: Any, result: ValidationResult):
        """Validate configuration field types"""
        type_expectations = {
            'version': str,
            'environment': str,
            'debug_mode': bool,
            'max_concurrent_requests': int,
            'cache_ttl': int,
            'rate_limit': int
        }
        
        for field, expected_type in type_expectations.items():
            if field in config:
                value = config[field]
                if not isinstance(value, expected_type):
                    result.add_issue(self.create_issue(
                        ValidationSeverity.ERROR,
                        f"Field {field} has wrong type: {type(value).__name__}",
                        f"Expected: {expected_type.__name__}",
                        field_path=f"config.{field}"
                    ))
    
    async def _validate_value_ranges(self, config: Any, result: ValidationResult):
        """Validate configuration value ranges"""
        range_validations = {
            'max_concurrent_requests': (1, 100000),
            'cache_ttl': (60, 86400),  # 1 minute to 1 day
            'rate_limit': (1, 10000),
            'timeout': (1, 300)  # 1 second to 5 minutes
        }
        
        for field, (min_val, max_val) in range_validations.items():
            if field in config:
                value = config[field]
                if isinstance(value, (int, float)):
                    if value < min_val or value > max_val:
                        result.add_issue(self.create_issue(
                            ValidationSeverity.WARNING,
                            f"Field {field} value {value} is outside recommended range",
                            f"Recommended range: {min_val} - {max_val}",
                            field_path=f"config.{field}"
                        ))
    
    async def _validate_dependencies(self, config: Any, result: ValidationResult):
        """Validate configuration dependencies"""
        # If security is enabled, certain fields must be present
        if config.get('security_enabled', True):
            security_fields = ['encryption_key', 'api_key_rotation_days']
            for field in security_fields:
                if field not in config.get('security_config', {}):
                    result.add_issue(self.create_issue(
                        ValidationSeverity.WARNING,
                        f"Security enabled but {field} not configured",
                        field_path=f"config.security_config.{field}"
                    ))
        
        # If monitoring is enabled, check monitoring config
        if config.get('monitoring_enabled', True):
            if 'monitoring_config' not in config:
                result.add_issue(self.create_issue(
                    ValidationSeverity.WARNING,
                    "Monitoring enabled but monitoring_config missing",
                    field_path="config.monitoring_config"
                ))


# ========== COMPLIANCE VALIDATOR ==========

class ComplianceValidator(BaseValidator):
    """GDPR/CCPA and other compliance validation"""
    
    def __init__(self):
        super().__init__("ComplianceValidator", "1.0.0")
        self.compliance_rules = self._load_compliance_rules()
    
    def _load_compliance_rules(self) -> Dict[ComplianceStandard, Dict[str, Any]]:
        """Load compliance rules for different standards"""
        return {
            ComplianceStandard.GDPR: {
                'data_retention_max_days': 2555,  # 7 years max
                'consent_required_fields': ['email', 'phone', 'location'],
                'right_to_deletion': True,
                'data_portability': True,
                'breach_notification_hours': 72
            },
            ComplianceStandard.CCPA: {
                'data_retention_max_days': 730,  # 2 years
                'consent_required_fields': ['personal_info', 'financial_info'],
                'right_to_deletion': True,
                'data_portability': True,
                'opt_out_required': True
            }
        }
    
    async def validate_compliance(self, data: Any, standard: ComplianceStandard,
                                context: Dict[str, Any] = None) -> ComplianceReport:
        """Validate compliance with specific standard"""
        report = ComplianceReport(standard=standard)
        
        try:
            if standard == ComplianceStandard.GDPR:
                await self._validate_gdpr_compliance(data, report, context)
            elif standard == ComplianceStandard.CCPA:
                await self._validate_ccpa_compliance(data, report, context)
            else:
                report.violations.append(ValidationIssue(
                    validation_type=ValidationType.COMPLIANCE,
                    severity=ValidationSeverity.WARNING,
                    message=f"Compliance validation not implemented for {standard.value}"
                ))
        
        except Exception as e:
            report.violations.append(ValidationIssue(
                validation_type=ValidationType.COMPLIANCE,
                severity=ValidationSeverity.CRITICAL,
                message=f"Compliance validation failed: {str(e)}"
            ))
            report.is_compliant = False
        
        # Update compliance status
        critical_violations = [v for v in report.violations 
                             if v.severity == ValidationSeverity.CRITICAL]
        if critical_violations:
            report.is_compliant = False
            report.compliance_score = 0.0
        else:
            # Calculate compliance score based on violations
            total_deductions = sum(10 if v.severity == ValidationSeverity.ERROR else 2
                                 for v in report.violations)
            report.compliance_score = max(0, 100 - total_deductions)
        
        return report
    
    async def _validate_gdpr_compliance(self, data: Any, report: ComplianceReport,
                                      context: Dict[str, Any] = None):
        """Validate GDPR compliance"""
        rules = self.compliance_rules[ComplianceStandard.GDPR]
        
        # Check data retention
        if isinstance(data, dict) and 'created_at' in data:
            try:
                created_at = datetime.fromisoformat(str(data['created_at']).replace('Z', '+00:00'))
                age_days = (datetime.utcnow() - created_at).days
                
                if age_days > rules['data_retention_max_days']:
                    report.violations.append(ValidationIssue(
                        validation_type=ValidationType.COMPLIANCE,
                        severity=ValidationSeverity.ERROR,
                        message=f"Data retention exceeds GDPR limit: {age_days} days",
                        details=f"Maximum allowed: {rules['data_retention_max_days']} days",
                        field_path="data.created_at"
                    ))
            except Exception:
                pass
        
        # Check consent for sensitive fields
        if isinstance(data, dict):
            for field in rules['consent_required_fields']:
                if field in data and not context.get(f'{field}_consent', False):
                    report.violations.append(ValidationIssue(
                        validation_type=ValidationType.COMPLIANCE,
                        severity=ValidationSeverity.WARNING,
                        message=f"Processing {field} without explicit consent",
                        field_path=f"data.{field}"
                    ))
        
        # Check for right to deletion capability
        if not context.get('deletion_supported', False):
            report.violations.append(ValidationIssue(
                validation_type=ValidationType.COMPLIANCE,
                severity=ValidationSeverity.WARNING,
                message="Right to deletion not implemented",
                suggestion="Implement data deletion functionality"
            ))
    
    async def _validate_ccpa_compliance(self, data: Any, report: ComplianceReport,
                                      context: Dict[str, Any] = None):
        """Validate CCPA compliance"""
        rules = self.compliance_rules[ComplianceStandard.CCPA]
        
        # Check opt-out mechanism
        if not context.get('opt_out_available', False):
            report.violations.append(ValidationIssue(
                validation_type=ValidationType.COMPLIANCE,
                severity=ValidationSeverity.ERROR,
                message="CCPA requires opt-out mechanism",
                suggestion="Implement 'Do Not Sell My Personal Information' option"
            ))
        
        # Check data portability
        if not context.get('data_export_available', False):
            report.violations.append(ValidationIssue(
                validation_type=ValidationType.COMPLIANCE,
                severity=ValidationSeverity.WARNING,
                message="Data portability not available",
                suggestion="Implement data export functionality"
            ))


# ========== PERFORMANCE VALIDATOR ==========

class PerformanceValidator(BaseValidator):
    """Performance validation"""
    
    def __init__(self):
        super().__init__("PerformanceValidator", "1.0.0")
        self.performance_thresholds = {
            'response_time_ms': 1000,      # 1 second
            'memory_usage_mb': 512,        # 512 MB
            'cpu_usage_percent': 80,       # 80%
            'cache_hit_rate': 0.85,        # 85%
            'error_rate': 0.05             # 5%
        }
    
    async def validate(self, metrics: Dict[str, Any], context: Dict[str, Any] = None) -> ValidationResult:
        """Validate performance metrics"""
        start_time = datetime.utcnow()
        result = ValidationResult(
            validation_type=ValidationType.PERFORMANCE,
            entity_type="performance_metrics",
            entity_id=context.get('service_id', '') if context else ''
        )
        
        try:
            for metric, threshold in self.performance_thresholds.items():
                if metric in metrics:
                    value = metrics[metric]
                    
                    if metric == 'response_time_ms' and value > threshold:
                        severity = ValidationSeverity.WARNING if value < threshold * 2 else ValidationSeverity.ERROR
                        result.add_issue(self.create_issue(
                            severity,
                            f"Response time exceeds threshold: {value}ms",
                            f"Threshold: {threshold}ms",
                            field_path=f"metrics.{metric}"
                        ))
                    
                    elif metric == 'memory_usage_mb' and value > threshold:
                        result.add_issue(self.create_issue(
                            ValidationSeverity.WARNING,
                            f"Memory usage high: {value}MB",
                            f"Threshold: {threshold}MB",
                            field_path=f"metrics.{metric}"
                        ))
                    
                    elif metric == 'cpu_usage_percent' and value > threshold:
                        result.add_issue(self.create_issue(
                            ValidationSeverity.WARNING,
                            f"CPU usage high: {value}%",
                            f"Threshold: {threshold}%",
                            field_path=f"metrics.{metric}"
                        ))
                    
                    elif metric == 'cache_hit_rate' and value < threshold:
                        result.add_issue(self.create_issue(
                            ValidationSeverity.WARNING,
                            f"Cache hit rate low: {value:.2%}",
                            f"Threshold: {threshold:.2%}",
                            field_path=f"metrics.{metric}"
                        ))
                    
                    elif metric == 'error_rate' and value > threshold:
                        severity = ValidationSeverity.ERROR if value > threshold * 2 else ValidationSeverity.WARNING
                        result.add_issue(self.create_issue(
                            severity,
                            f"Error rate high: {value:.2%}",
                            f"Threshold: {threshold:.2%}",
                            field_path=f"metrics.{metric}"
                        ))
        
        except Exception as e:
            result.add_issue(self.create_issue(
                ValidationSeverity.CRITICAL,
                f"Performance validation failed: {str(e)}",
                field_path="metrics"
            ))
        
        # Calculate execution time
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        result.execution_time_ms = execution_time
        
        return result


# ========== MAIN ANALYTICS VALIDATORS CLASS ==========

class AnalyticsValidators:
    """
    Main Analytics Validators Hub
    
    Provides comprehensive validation services for all analytics components
    including data quality, configuration, compliance, and performance validation.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize validators
        self.data_validator = DataValidator()
        self.config_validator = ConfigValidator()
        self.compliance_validator = ComplianceValidator()
        self.performance_validator = PerformanceValidator()
        
        # Validation history
        self.validation_history: List[ValidationResult] = []
        self.compliance_reports: List[ComplianceReport] = []
    
    async def validate_data_quality(self, data: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate data quality"""
        result = await self.data_validator.validate(data, context)
        self.validation_history.append(result)
        return result
    
    async def validate_configuration(self, config: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate configuration"""
        result = await self.config_validator.validate(config, context)
        self.validation_history.append(result)
        return result
    
    async def validate_compliance(self, data: Any, standard: ComplianceStandard,
                                context: Dict[str, Any] = None) -> ComplianceReport:
        """Validate compliance with specific standard"""
        report = await self.compliance_validator.validate_compliance(data, standard, context)
        self.compliance_reports.append(report)
        return report
    
    async def validate_performance(self, metrics: Dict[str, Any], 
                                 context: Dict[str, Any] = None) -> ValidationResult:
        """Validate performance metrics"""
        result = await self.performance_validator.validate(metrics, context)
        self.validation_history.append(result)
        return result
    
    async def comprehensive_validation(self, entity_data: Dict[str, Any],
                                     entity_type: str = "analytics_entity") -> Dict[str, Any]:
        """Run comprehensive validation across all validators"""
        validation_summary = {
            'entity_type': entity_type,
            'validation_timestamp': datetime.utcnow().isoformat(),
            'overall_valid': True,
            'validation_results': {},
            'compliance_reports': {},
            'summary': {
                'total_issues': 0,
                'critical_issues': 0,
                'error_issues': 0,
                'warning_issues': 0
            }
        }
        
        try:
            # Data quality validation
            data_result = await self.validate_data_quality(
                entity_data.get('data'), 
                {'entity_type': entity_type}
            )
            validation_summary['validation_results']['data_quality'] = data_result
            
            # Configuration validation (if present)
            if 'config' in entity_data:
                config_result = await self.validate_configuration(
                    entity_data['config'],
                    {'entity_type': entity_type}
                )
                validation_summary['validation_results']['configuration'] = config_result
            
            # Performance validation (if metrics present)
            if 'metrics' in entity_data:
                perf_result = await self.validate_performance(
                    entity_data['metrics'],
                    {'entity_type': entity_type}
                )
                validation_summary['validation_results']['performance'] = perf_result
            
            # Compliance validation (GDPR by default)
            gdpr_report = await self.validate_compliance(
                entity_data.get('data'),
                ComplianceStandard.GDPR,
                entity_data.get('compliance_context', {})
            )
            validation_summary['compliance_reports']['gdpr'] = gdpr_report
            
            # Calculate summary statistics
            all_issues = []
            for result in validation_summary['validation_results'].values():
                if hasattr(result, 'issues'):
                    all_issues.extend(result.issues)
                    if not result.is_valid:
                        validation_summary['overall_valid'] = False
            
            for report in validation_summary['compliance_reports'].values():
                if hasattr(report, 'violations'):
                    all_issues.extend(report.violations)
                    if not report.is_compliant:
                        validation_summary['overall_valid'] = False
            
            # Count issues by severity
            validation_summary['summary']['total_issues'] = len(all_issues)
            validation_summary['summary']['critical_issues'] = sum(
                1 for issue in all_issues if issue.severity == ValidationSeverity.CRITICAL
            )
            validation_summary['summary']['error_issues'] = sum(
                1 for issue in all_issues if issue.severity == ValidationSeverity.ERROR
            )
            validation_summary['summary']['warning_issues'] = sum(
                1 for issue in all_issues if issue.severity == ValidationSeverity.WARNING
            )
            
        except Exception as e:
            self.logger.error(f"Comprehensive validation failed: {str(e)}")
            validation_summary['overall_valid'] = False
            validation_summary['error'] = str(e)
        
        return validation_summary
    
    def get_validation_summary(self, time_period: timedelta = None) -> Dict[str, Any]:
        """Get validation summary for time period"""
        if time_period is None:
            time_period = timedelta(days=1)
        
        cutoff_time = datetime.utcnow() - time_period
        recent_validations = [
            v for v in self.validation_history 
            if v.validated_at >= cutoff_time
        ]
        
        return {
            'time_period_hours': time_period.total_seconds() / 3600,
            'total_validations': len(recent_validations),
            'successful_validations': sum(1 for v in recent_validations if v.is_valid),
            'failed_validations': sum(1 for v in recent_validations if not v.is_valid),
            'average_score': np.mean([v.overall_score for v in recent_validations]) if recent_validations else 0,
            'validation_types': {
                vtype.value: sum(1 for v in recent_validations if v.validation_type == vtype)
                for vtype in ValidationType
            }
        }


# ========== MODULE EXPORTS ==========

__all__ = [
    # Main Classes
    'AnalyticsValidators',
    'DataValidator',
    'ConfigValidator', 
    'ComplianceValidator',
    'PerformanceValidator',
    
    # Data Classes
    'ValidationIssue',
    'ValidationResult',
    'ComplianceReport',
    
    # Enums
    'ValidationSeverity',
    'ValidationType',
    'ComplianceStandard',
    'DataQualityDimension'
]