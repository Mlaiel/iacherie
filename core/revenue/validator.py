"""Revenue Validator - Advanced data validation and quality assurance system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, reproduction, modification, or distribution without explicit 
written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REVENUE VALIDATOR - ENTERPRISE EDITION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Developed by Expert Team:
🎯 Lead Dev IA: Fahed Mlaiel (Advanced AI/ML Architecture)
🛠️  Backend Senior: System Architecture & Performance Optimization  
🤖 ML Engineer: Revenue Forecasting & Optimization Algorithms
🗄️  DBA: Advanced Data Management & Analytics
🔒 Security Expert: Enterprise-Grade Security & Encryption
🚀 Microservices: Scalable Distributed Architecture
🎵 Audio Expert: Audio Revenue Stream Optimization
⚙️  DevOps: Production Infrastructure & Monitoring
🧠 IA Prompt Engineer: AI-Powered Decision Making
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
import uuid
import re
import statistics
import json

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pydantic
from pydantic import BaseModel, validator, ValidationError

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """
Severity levels for validation issues"""

    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationCategory(Enum):
    """Categories of validation rules"""

    DATA_INTEGRITY = "data_integrity"
    BUSINESS_LOGIC = "business_logic"
    STATISTICAL_ANOMALY = "statistical_anomaly"
    TEMPORAL_CONSISTENCY = "temporal_consistency"
    CROSS_VALIDATION = "cross_validation"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"


class DataQualityDimension(Enum):
    """Data quality dimensions"""

    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"


@dataclass
class ValidationIssue:
    """Individual validation issue"""
    issue_id: str
    rule_name: str
    category: ValidationCategory
    severity: ValidationSeverity
    dimension: DataQualityDimension
    description: str
    affected_fields: List[str]
    current_value: Any
    expected_value: Any
    suggestion: str
    confidence_score: float
    data_source: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_blocking(self) -> bool:
        """
Check if issue is blocking"""
        return self.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]


@dataclass
class ValidationRule:
    """
Validation rule definition"""
    rule_id: str
    name: str
    description: str
    category: ValidationCategory
    severity: ValidationSeverity
    dimension: DataQualityDimension
    validation_function: str
    parameters: Dict[str, Any]
    is_active: bool = True
    execution_order: int = 0


@dataclass
class ValidationReport:
    """
Comprehensive validation report"""
    report_id: str
    data_source: str
    validation_timestamp: datetime
    total_records: int
    issues: List[ValidationIssue]
    summary: Dict[str, Any]
    quality_score: float
    recommendations: List[str]
    passed_rules: List[str]
    failed_rules: List[str]
    
    @property
    def has_critical_issues(self) -> bool:
        """
Check if report has critical issues"""
        return any(issue.severity == ValidationSeverity.CRITICAL for issue in self.issues)
    
    @property
    def has_blocking_issues(self) -> bool:
        """
Check if report has blocking issues"""
        return any(issue.is_blocking for issue in self.issues)


# Pydantic models for data structure validation
class RevenueStreamModel(BaseModel):
    """
Revenue stream data model"""
    platform: str
    revenue: Decimal
    currency: str = "EUR"
    period_start: datetime
    period_end: datetime
    
    @validator('revenue')
    def revenue_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('Revenue must be non-negative')
        return v
    
    @validator('currency')
    def currency_must_be_valid(cls, v):
        valid_currencies = ['EUR', 'USD', 'GBP', 'CAD', 'AUD']
        if v not in valid_currencies:
            raise ValueError(f'Currency must be one of {valid_currencies}')
        return v
    
    @validator('period_end')
    def period_end_after_start(cls, v, values):
        if 'period_start' in values and v <= values['period_start']:
            raise ValueError('Period end must be after period start')
        return v


class EngagementMetricsModel(BaseModel):
    """Engagement metrics data model"""
    platform: str
    views: int
    likes: int
    shares: int
    comments: int
    engagement_rate: float
    follower_count: int
    measurement_date: datetime
    
    @validator('engagement_rate')
    def engagement_rate_valid_range(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Engagement rate must be between 0 and 100')
        return v
    
    @validator('views', 'likes', 'shares', 'comments', 'follower_count')
    def counts_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('Count metrics must be non-negative')
        return v


class RevenueDataModel(BaseModel):
    """
Complete revenue data model"""
    user_id: str
    reporting_period: str
    total_revenue: Decimal
    revenue_streams: List[RevenueStreamModel]
    engagement_metrics: List[EngagementMetricsModel]
    expenses: Optional[Decimal] = None
    metadata: Dict[str, Any] = {}
    
    @validator('total_revenue')
    def total_revenue_consistency(cls, v, values):
        if 'revenue_streams' in values and values['revenue_streams']:
            calculated_total = sum(stream.revenue for stream in values['revenue_streams'])
            tolerance = Decimal('0.01')
            if abs(v - calculated_total) > tolerance:
                raise ValueError(f'Total revenue {v} does not match sum of streams {calculated_total}')
        return v


class RevenueValidator:
    """
Advanced revenue data validation and quality assurance system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.validation_rules = {}
        self.ml_models = {}
        self.historical_patterns = {}
        
        # Validation thresholds
        self.quality_score_threshold = self.config.get('quality_score_threshold', 0.8)
        self.anomaly_threshold = self.config.get('anomaly_threshold', 0.05)
        
        # Cached validation results
        self.validation_cache = {}
        
    async def initialize(self) -> None:
        """
Initialize revenue validator"""
        try:
            # Setup validation rules
            await self._setup_validation_rules()
            
            # Initialize ML models for anomaly detection
            await self._initialize_ml_models()
            
            # Load historical patterns
            await self._load_historical_patterns()
            
            logger.info("Revenue validator initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing revenue validator: {e}")
            raise
    
    async def _setup_validation_rules(self) -> None:
        """Setup comprehensive validation rules"""
        rules = [
            # Data Integrity Rules
            ValidationRule(
                rule_id="revenue_non_negative",
                name="Revenue Non-Negative",
                description="Revenue values must be non-negative",
                category=ValidationCategory.DATA_INTEGRITY,
                severity=ValidationSeverity.CRITICAL,
                dimension=DataQualityDimension.VALIDITY,
                validation_function="validate_revenue_non_negative",
                parameters={}
            ),
            
            ValidationRule(
                rule_id="required_fields_present",
                name="Required Fields Present",
                description="All required fields must be present",
                category=ValidationCategory.DATA_INTEGRITY,
                severity=ValidationSeverity.CRITICAL,
                dimension=DataQualityDimension.COMPLETENESS,
                validation_function="validate_required_fields",
                parameters={
                    'required_fields': ['user_id', 'reporting_period', 'total_revenue']
                }
            ),
            
            ValidationRule(
                rule_id="data_types_valid",
                name="Data Types Valid",
                description="Data types must match expected formats",
                category=ValidationCategory.DATA_INTEGRITY,
                severity=ValidationSeverity.ERROR,
                dimension=DataQualityDimension.VALIDITY,
                validation_function="validate_data_types",
                parameters={}
            ),
            
            # Business Logic Rules
            ValidationRule(
                rule_id="revenue_stream_sum_consistency",
                name="Revenue Stream Sum Consistency",
                description="Total revenue must equal sum of revenue streams",
                category=ValidationCategory.BUSINESS_LOGIC,
                severity=ValidationSeverity.ERROR,
                dimension=DataQualityDimension.CONSISTENCY,
                validation_function="validate_revenue_sum_consistency",
                parameters={'tolerance': Decimal('0.01')}
            ),
            
            ValidationRule(
                rule_id="engagement_rate_logical",
                name="Engagement Rate Logical",
                description="Engagement rate must be logical given follower count and interactions",
                category=ValidationCategory.BUSINESS_LOGIC,
                severity=ValidationSeverity.WARNING,
                dimension=DataQualityDimension.ACCURACY,
                validation_function="validate_engagement_rate_logic",
                parameters={}
            ),
            
            ValidationRule(
                rule_id="platform_revenue_positive",
                name="Platform Revenue Positive",
                description="Platform revenue should be positive if engagement exists",
                category=ValidationCategory.BUSINESS_LOGIC,
                severity=ValidationSeverity.WARNING,
                dimension=DataQualityDimension.ACCURACY,
                validation_function="validate_platform_revenue_logic",
                parameters={}
            ),
            
            # Temporal Consistency Rules
            ValidationRule(
                rule_id="temporal_sequence_valid",
                name="Temporal Sequence Valid",
                description="Data timestamps must be in logical sequence",
                category=ValidationCategory.TEMPORAL_CONSISTENCY,
                severity=ValidationSeverity.ERROR,
                dimension=DataQualityDimension.CONSISTENCY,
                validation_function="validate_temporal_sequence",
                parameters={}
            ),
            
            ValidationRule(
                rule_id="reporting_period_valid",
                name="Reporting Period Valid",
                description="Reporting period must be valid and consistent",
                category=ValidationCategory.TEMPORAL_CONSISTENCY,
                severity=ValidationSeverity.ERROR,
                dimension=DataQualityDimension.VALIDITY,
                validation_function="validate_reporting_period",
                parameters={}
            ),
            
            # Statistical Anomaly Rules
            ValidationRule(
                rule_id="revenue_anomaly_detection",
                name="Revenue Anomaly Detection",
                description="Detect unusual revenue patterns",
                category=ValidationCategory.STATISTICAL_ANOMALY,
                severity=ValidationSeverity.WARNING,
                dimension=DataQualityDimension.ACCURACY,
                validation_function="validate_revenue_anomalies",
                parameters={'sensitivity': 0.05}
            ),
            
            ValidationRule(
                rule_id="engagement_anomaly_detection",
                name="Engagement Anomaly Detection",
                description="Detect unusual engagement patterns",
                category=ValidationCategory.STATISTICAL_ANOMALY,
                severity=ValidationSeverity.INFO,
                dimension=DataQualityDimension.ACCURACY,
                validation_function="validate_engagement_anomalies",
                parameters={'sensitivity': 0.05}
            ),
            
            # Cross-Validation Rules
            ValidationRule(
                rule_id="revenue_engagement_correlation",
                name="Revenue Engagement Correlation",
                description="Revenue should correlate with engagement metrics",
                category=ValidationCategory.CROSS_VALIDATION,
                severity=ValidationSeverity.WARNING,
                dimension=DataQualityDimension.CONSISTENCY,
                validation_function="validate_revenue_engagement_correlation",
                parameters={'min_correlation': 0.3}
            ),
            
            # Compliance Rules
            ValidationRule(
                rule_id="currency_compliance",
                name="Currency Compliance",
                description="Currency codes must be valid ISO 4217",
                category=ValidationCategory.COMPLIANCE,
                severity=ValidationSeverity.ERROR,
                dimension=DataQualityDimension.VALIDITY,
                validation_function="validate_currency_compliance",
                parameters={'valid_currencies': ['EUR', 'USD', 'GBP', 'CAD', 'AUD']}
            ),
            
            # Performance Rules
            ValidationRule(
                rule_id="data_freshness",
                name="Data Freshness",
                description="Data should be reasonably fresh",
                category=ValidationCategory.PERFORMANCE,
                severity=ValidationSeverity.WARNING,
                dimension=DataQualityDimension.TIMELINESS,
                validation_function="validate_data_freshness",
                parameters={'max_age_days': 30}
            )
        ]
        
        # Store rules
        for rule in rules:
            self.validation_rules[rule.rule_id] = rule
    
    async def _initialize_ml_models(self) -> None:
        """Initialize ML models for advanced validation"""
        # Isolation Forest for anomaly detection
        self.ml_models['anomaly_detector'] = IsolationForest(
            contamination=self.anomaly_threshold,
            random_state=42
        )
        
        # Scaler for normalization
        self.ml_models['scaler'] = StandardScaler()
        
        # Pattern recognition model (placeholder)
        self.ml_models['pattern_detector'] = None
    
    async def _load_historical_patterns(self) -> None:
        """
Load historical patterns for validation"""
        # Expected revenue patterns by platform
        self.historical_patterns = {
            'platform_revenue_ranges': {
                'youtube': {'min': 100, 'max': 50000, 'typical': 2000},
                'instagram': {'min': 50, 'max': 20000, 'typical': 1000},
                'tiktok': {'min': 20, 'max': 15000, 'typical': 500},
                'twitch': {'min': 200, 'max': 30000, 'typical': 2500}
            },
            'engagement_benchmarks': {
                'youtube': {'engagement_rate': 3.5, 'views_per_subscriber': 0.05},
                'instagram': {'engagement_rate': 1.8, 'views_per_follower': 0.1},
                'tiktok': {'engagement_rate': 8.5, 'views_per_follower': 0.2},
                'twitch': {'engagement_rate': 5.0, 'concurrent_viewers_ratio': 0.03}
            },
            'seasonal_patterns': {
                'q4_boost': 1.3,  # Holiday season boost
                'summer_dip': 0.85,  # Summer engagement dip
                'back_to_school': 1.15  # September boost
            }
        }
    
    async def validate_revenue_data(
        self,
        data: Dict[str, Any],
        data_source: str = "api",
        skip_cache: bool = False
    ) -> ValidationReport:
        """Comprehensive revenue data validation"""
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(data, data_source)
            
            # Check cache
            if not skip_cache and cache_key in self.validation_cache:
                cached_result = self.validation_cache[cache_key]
                if (datetime.utcnow() - cached_result.validation_timestamp).seconds < 300:  # 5 min cache
                    return cached_result
            
            # Initialize report
            report_id = f"validation_{uuid.uuid4().hex[:8]}"
            issues = []
            
            # Structural validation using Pydantic
            pydantic_issues = await self._validate_with_pydantic(data, data_source)
            issues.extend(pydantic_issues)
            
            # If critical structural issues, return early
            if any(issue.severity == ValidationSeverity.CRITICAL for issue in pydantic_issues):
                return ValidationReport(
                    report_id=report_id,
                    data_source=data_source,
                    validation_timestamp=datetime.utcnow(),
                    total_records=1,
                    issues=issues,
                    summary={'critical_structural_issues': True},
                    quality_score=0.0,
                    recommendations=["Fix critical structural issues before proceeding"],
                    passed_rules=[],
                    failed_rules=[rule.rule_id for rule in self.validation_rules.values()]
                )
            
            # Run validation rules
            passed_rules = []
            failed_rules = []
            
            # Sort rules by execution order
            sorted_rules = sorted(
                self.validation_rules.values(),
                key=lambda r: r.execution_order
            )
            
            for rule in sorted_rules:
                if not rule.is_active:
                    continue
                
                try:
                    rule_issues = await self._execute_validation_rule(rule, data, data_source)
                    
                    if rule_issues:
                        issues.extend(rule_issues)
                        failed_rules.append(rule.rule_id)
                    else:
                        passed_rules.append(rule.rule_id)
                        
                except Exception as e:
                    logger.warning(f"Error executing validation rule {rule.rule_id}: {e}")
                    # Create issue for rule execution failure
                    issues.append(ValidationIssue(
                        issue_id=str(uuid.uuid4()),
                        rule_name=rule.name,
                        category=rule.category,
                        severity=ValidationSeverity.WARNING,
                        dimension=DataQualityDimension.VALIDITY,
                        description=f"Rule execution failed: {str(e)}",
                        affected_fields=[],
                        current_value=None,
                        expected_value=None,
                        suggestion="Check rule implementation",
                        confidence_score=1.0,
                        data_source=data_source
                    ))
                    failed_rules.append(rule.rule_id)
            
            # Calculate quality score
            quality_score = await self._calculate_quality_score(issues, passed_rules, failed_rules)
            
            # Generate summary
            summary = await self._generate_validation_summary(issues, data)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(issues, quality_score)
            
            # Create report
            report = ValidationReport(
                report_id=report_id,
                data_source=data_source,
                validation_timestamp=datetime.utcnow(),
                total_records=self._count_records(data),
                issues=issues,
                summary=summary,
                quality_score=quality_score,
                recommendations=recommendations,
                passed_rules=passed_rules,
                failed_rules=failed_rules
            )
            
            # Cache result
            self.validation_cache[cache_key] = report
            
            return report
            
        except Exception as e:
            logger.error(f"Error validating revenue data: {e}")
            raise
    
    def _generate_cache_key(self, data: Dict[str, Any], data_source: str) -> str:
        """Generate cache key for validation result"""
        # Create a hash of the data for caching
        data_str = json.dumps(data, sort_keys=True, default=str)
        import hashlib
        return hashlib.md5(f"{data_source}_{data_str}".encode()).hexdigest()
    
    async def _validate_with_pydantic(
        self,
        data: Dict[str, Any],
        data_source: str
    ) -> List[ValidationIssue]:
        """Validate data structure using Pydantic models"""
        issues = []
        
        try:
            # Validate main revenue data model
            RevenueDataModel(**data)
            
        except ValidationError as e:
            for error in e.errors():
                issues.append(ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_name="Pydantic Structure Validation",
                    category=ValidationCategory.DATA_INTEGRITY,
                    severity=ValidationSeverity.CRITICAL,
                    dimension=DataQualityDimension.VALIDITY,
                    description=f"Structure validation failed: {error['msg']}",
                    affected_fields=error.get('loc', []),
                    current_value=error.get('input'),
                    expected_value=error.get('type'),
                    suggestion="Fix data structure according to schema",
                    confidence_score=1.0,
                    data_source=data_source
                ))
        
        return issues
    
    async def _execute_validation_rule(
        self,
        rule: ValidationRule,
        data: Dict[str, Any],
        data_source: str
    ) -> List[ValidationIssue]:
        """Execute individual validation rule"""
        validation_function = getattr(self, rule.validation_function, None)
        
        if not validation_function:
            logger.warning(f"Validation function {rule.validation_function} not found")
            return []
        
        try:
            return await validation_function(rule, data, data_source)
        except Exception as e:
            logger.error(f"Error in validation function {rule.validation_function}: {e}")
            return []
    
    # Validation Functions
    
    async def validate_revenue_non_negative(
        self,
        rule: ValidationRule,
        data: Dict[str, Any],
        data_source: str
    ) -> List[ValidationIssue]:
        """Validate that revenue values are non-negative"""
        issues = []
        
        # Check total revenue
        total_revenue = data.get('total_revenue')
        if total_revenue is not None and Decimal(str(total_revenue)) < 0:
            issues.append(ValidationIssue(
                issue_id=str(uuid.uuid4()),
                rule_name=rule.name,
                category=rule.category,
                severity=rule.severity,
                dimension=rule.dimension,
                description="Total revenue is negative",
                affected_fields=['total_revenue'],
                current_value=total_revenue,
                expected_value="≥ 0",
                suggestion="Revenue values must be non-negative",
                confidence_score=1.0,
                data_source=data_source
            ))
        
        # Check revenue streams
        revenue_streams = data.get('revenue_streams', [])
        for i, stream in enumerate(revenue_streams):
            if 'revenue' in stream and Decimal(str(stream['revenue'])) < 0:
                issues.append(ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    dimension=rule.dimension,
                    description=f"Revenue stream {i} has negative revenue",
                    affected_fields=[f'revenue_streams[{i}].revenue'],
                    current_value=stream['revenue'],
                    expected_value="≥ 0",
                    suggestion="Revenue stream values must be non-negative",
                    confidence_score=1.0,
                    data_source=data_source
                ))
        
        return issues
    
    async def validate_required_fields(
        self,
        rule: ValidationRule,
        data: Dict[str, Any],
        data_source: str
    ) -> List[ValidationIssue]:
        """Validate that required fields are present"""
        issues = []
        required_fields = rule.parameters.get('required_fields', [])
        
        for field in required_fields:
            if field not in data or data[field] is None:
                issues.append(ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    dimension=rule.dimension,
                    description=f"Required field '{field}' is missing",
                    affected_fields=[field],
                    current_value=None,
                    expected_value="Present and non-null",
                    suggestion=f"Provide value for required field '{field}'",
                    confidence_score=1.0,
                    data_source=data_source
                ))
        
        return issues
    
    async def validate_data_types(
        self,
        rule: ValidationRule,
        data: Dict[str, Any],
        data_source: str
    ) -> List[ValidationIssue]:
        """Validate data types"""
        issues = []
        
        # Define expected types
        expected_types = {
            'user_id': str,
            'reporting_period': str,
            'total_revenue': (int, float, Decimal, str),  # Allow string for Decimal conversion
            'expenses': (int, float, Decimal, str, type(None))
        }
        
        for field, expected_type in expected_types.items():
            if field in data:
                value = data[field]
                if not isinstance(value, expected_type):
                    # Special handling for numeric fields
                    if field in ['total_revenue', 'expenses'] and value is not None:
                        try:
                            Decimal(str(value))
                            continue  # Valid numeric conversion
                        except (InvalidOperation, ValueError):
                            pass
                    
                    issues.append(ValidationIssue(
                        issue_id=str(uuid.uuid4()),
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        dimension=rule.dimension,
                        description=f"Field '{field}' has invalid type",
                        affected_fields=[field],
                        current_value=type(value).__name__,
                        expected_value=str(expected_type),
                        suggestion=f"Convert '{field}' to expected type",
                        confidence_score=1.0,
                        data_source=data_source
                    ))
        
        return issues
    
    async def validate_revenue_sum_consistency(
        self,
        rule: ValidationRule,
        data: Dict[str, Any],
        data_source: str
    ) -> List[ValidationIssue]:
        """Validate that total revenue equals sum of revenue streams"""
        issues = []
        
        total_revenue = data.get('total_revenue')
        revenue_streams = data.get('revenue_streams', [])
        tolerance = rule.parameters.get('tolerance', Decimal('0.01'))
        
        if total_revenue is not None and revenue_streams:
            total_revenue_decimal = Decimal(str(total_revenue))
            
            calculated_total = Decimal('0')
            for stream in revenue_streams:
                if 'revenue' in stream:
                    calculated_total += Decimal(str(stream['revenue']))
            
            difference = abs(total_revenue_decimal - calculated_total)
            
            if difference > tolerance:
                issues.append(ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    dimension=rule.dimension,
                    description="Total revenue does not match sum of revenue streams",
                    affected_fields=['total_revenue', 'revenue_streams'],
                    current_value=f"Total: {total_revenue_decimal}, Sum: {calculated_total}",
                    expected_value=f"Difference ≤ {tolerance}",
                    suggestion="Ensure total revenue equals sum of all revenue streams",
                    confidence_score=1.0,
                    data_source=data_source
                ))
        
        return issues
    
    async def validate_engagement_rate_logic(
        self,
        rule: ValidationRule,
        data: Dict[str, Any],
        data_source: str
    ) -> List[ValidationIssue]:
        """Validate engagement rate logic"""
        issues = []
        
        engagement_metrics = data.get('engagement_metrics', [])
        
        for i, metrics in enumerate(engagement_metrics):
            engagement_rate = metrics.get('engagement_rate', 0)
            follower_count = metrics.get('follower_count', 0)
            total_interactions = (
                metrics.get('likes', 0) +
                metrics.get('shares', 0) +
                metrics.get('comments', 0)
            )
            
            if follower_count > 0 and total_interactions > 0:
                # Calculate theoretical engagement rate
                theoretical_rate = (total_interactions / follower_count) * 100
                
                # Allow some tolerance for different calculation methods
                tolerance = 2.0  # 2% tolerance
                
                if abs(engagement_rate - theoretical_rate) > tolerance:
                    issues.append(ValidationIssue(
                        issue_id=str(uuid.uuid4()),
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        dimension=rule.dimension,
                        description=f"Engagement rate {engagement_rate}% doesn't match calculated rate {theoretical_rate:.1f}%",
                        affected_fields=[f'engagement_metrics[{i}].engagement_rate'],
                        current_value=engagement_rate,
                        expected_value=f"~{theoretical_rate:.1f}%",
                        suggestion="Verify engagement rate calculation",
                        confidence_score=0.8,
                        data_source=data_source
                    ))
        
        return issues
    
    async def validate_platform_revenue_logic(
        self,
        rule: ValidationRule,
        data: Dict[str, Any],
        data_source: str
    ) -> List[ValidationIssue]:
        """Validate platform revenue logic"""
        issues = []
        
        revenue_streams = data.get('revenue_streams', [])
        engagement_metrics = data.get('engagement_metrics', [])
        
        # Create platform mapping
        engagement_by_platform = {
            metrics.get('platform'): metrics
            for metrics in engagement_metrics
        }
        
        for i, stream in enumerate(revenue_streams):
            platform = stream.get('platform')
            revenue = Decimal(str(stream.get('revenue', 0)))
            
            if platform in engagement_by_platform:
                metrics = engagement_by_platform[platform]
                engagement_rate = metrics.get('engagement_rate', 0)
                follower_count = metrics.get('follower_count', 0)
                
                # If significant engagement but no revenue, flag as potential issue
                if engagement_rate > 1.0 and follower_count > 1000 and revenue == 0:
                    issues.append(ValidationIssue(
                        issue_id=str(uuid.uuid4()),
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        dimension=rule.dimension,
                        description=f"Platform {platform} has good engagement but no revenue",
                        affected_fields=[f'revenue_streams[{i}].revenue'],
                        current_value=revenue,
                        expected_value="> 0",
                        suggestion="Consider monetization opportunities for this platform",
                        confidence_score=0.6,
                        data_source=data_source
                    ))
        
        return issues
    
    async def validate_temporal_sequence(
        self,
        rule: ValidationRule,
        data: Dict[str, Any],
        data_source: str
    ) -> List[ValidationIssue]:
        """Validate temporal sequence consistency"""
        issues = []
        
        # Check revenue streams temporal consistency
        revenue_streams = data.get('revenue_streams', [])
        
        for i, stream in enumerate(revenue_streams):
            start_date = stream.get('period_start')
            end_date = stream.get('period_end')
            
            if start_date and end_date:
                try:
                    if isinstance(start_date, str):
                        start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    if isinstance(end_date, str):
                        end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    
                    if end_date <= start_date:
                        issues.append(ValidationIssue(
                            issue_id=str(uuid.uuid4()),
                            rule_name=rule.name,
                            category=rule.category,
                            severity=rule.severity,
                            dimension=rule.dimension,
                            description=f"Revenue stream {i} has invalid date sequence",
                            affected_fields=[f'revenue_streams[{i}].period_start', f'revenue_streams[{i}].period_end'],
                            current_value=f"Start: {start_date}, End: {end_date}",
                            expected_value="End date > Start date",
                            suggestion="Ensure end date is after start date",
                            confidence_score=1.0,
                            data_source=data_source
                        ))
                except (ValueError, TypeError) as e:
                    issues.append(ValidationIssue(
                        issue_id=str(uuid.uuid4()),
                        rule_name=rule.name,
                        category=rule.category,
                        severity=ValidationSeverity.ERROR,
                        dimension=DataQualityDimension.VALIDITY,
                        description=f"Invalid date format in revenue stream {i}",
                        affected_fields=[f'revenue_streams[{i}].period_start', f'revenue_streams[{i}].period_end'],
                        current_value=f"Start: {start_date}, End: {end_date}",
                        expected_value="Valid ISO datetime format",
                        suggestion="Use valid ISO datetime format",
                        confidence_score=1.0,
                        data_source=data_source
                    ))
        
        return issues
    
    async def validate_reporting_period(
        self,
        rule: ValidationRule,
        data: Dict[str, Any],
        data_source: str
    ) -> List[ValidationIssue]:
        """Validate reporting period format and consistency"""
        issues = []
        
        reporting_period = data.get('reporting_period')
        
        if reporting_period:
            # Validate format (expected: YYYY-MM or YYYY-MM-DD)
            valid_formats = [
                r'^\d{4}-\d{2}$',  # YYYY-MM
                r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
                r'^\d{4}-Q[1-4]$',  # YYYY-Q1, YYYY-Q2, etc.
                r'^\d{4}$'  # YYYY (yearly)
            ]
            
            if not any(re.match(pattern, reporting_period) for pattern in valid_formats):
                issues.append(ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    dimension=rule.dimension,
                    description="Invalid reporting period format",
                    affected_fields=['reporting_period'],
                    current_value=reporting_period,
                    expected_value="YYYY-MM, YYYY-MM-DD, YYYY-Q[1-4], or YYYY",
                    suggestion="Use valid reporting period format",
                    confidence_score=1.0,
                    data_source=data_source
                ))
        
        return issues
    
    async def validate_revenue_anomalies(
        self,
        rule: ValidationRule,
        data: Dict[str, Any],
        data_source: str
    ) -> List[ValidationIssue]:
        """Detect revenue anomalies using statistical methods"""
        issues = []
        
        total_revenue = data.get('total_revenue')
        revenue_streams = data.get('revenue_streams', [])
        
        if total_revenue is not None:
            total_revenue_float = float(Decimal(str(total_revenue)))
            
            # Get historical context from patterns
            platform_ranges = self.historical_patterns.get('platform_revenue_ranges', {})
            
            # Check if revenue is unusually high or low
            for stream in revenue_streams:
                platform = stream.get('platform', '').lower()
                revenue_value = float(Decimal(str(stream.get('revenue', 0))))
                
                if platform in platform_ranges:
                    range_info = platform_ranges[platform]
                    min_expected = range_info['min']
                    max_expected = range_info['max']
                    typical = range_info['typical']
                    
                    # Flag if revenue is outside reasonable bounds
                    if revenue_value > max_expected * 2:  # More than 2x max
                        issues.append(ValidationIssue(
                            issue_id=str(uuid.uuid4()),
                            rule_name=rule.name,
                            category=rule.category,
                            severity=ValidationSeverity.WARNING,
                            dimension=DataQualityDimension.ACCURACY,
                            description=f"Unusually high revenue for {platform}",
                            affected_fields=[f'revenue_streams[{platform}].revenue'],
                            current_value=revenue_value,
                            expected_value=f"Typically ≤ {max_expected}",
                            suggestion="Verify this exceptionally high revenue value",
                            confidence_score=0.7,
                            data_source=data_source
                        ))
                    elif revenue_value < min_expected * 0.1 and revenue_value > 0:  # Less than 10% of min
                        issues.append(ValidationIssue(
                            issue_id=str(uuid.uuid4()),
                            rule_name=rule.name,
                            category=rule.category,
                            severity=ValidationSeverity.INFO,
                            dimension=DataQualityDimension.ACCURACY,
                            description=f"Unusually low revenue for {platform}",
                            affected_fields=[f'revenue_streams[{platform}].revenue'],
                            current_value=revenue_value,
                            expected_value=f"Typically ≥ {min_expected}",
                            suggestion="Verify this low revenue value",
                            confidence_score=0.6,
                            data_source=data_source
                        ))
        
        return issues
    
    async def validate_engagement_anomalies(
        self,
        rule: ValidationRule,
        data: Dict[str, Any],
        data_source: str
    ) -> List[ValidationIssue]:
        """Detect engagement anomalies"""
        issues = []
        
        engagement_metrics = data.get('engagement_metrics', [])
        benchmarks = self.historical_patterns.get('engagement_benchmarks', {})
        
        for metrics in engagement_metrics:
            platform = metrics.get('platform', '').lower()
            engagement_rate = metrics.get('engagement_rate', 0)
            
            if platform in benchmarks:
                benchmark_rate = benchmarks[platform]['engagement_rate']
                
                # Flag unusual engagement rates
                if engagement_rate > benchmark_rate * 3:  # 3x above benchmark
                    issues.append(ValidationIssue(
                        issue_id=str(uuid.uuid4()),
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        dimension=rule.dimension,
                        description=f"Unusually high engagement rate for {platform}",
                        affected_fields=[f'engagement_metrics[{platform}].engagement_rate'],
                        current_value=engagement_rate,
                        expected_value=f"Typically ~{benchmark_rate}%",
                        suggestion="Verify this exceptional engagement rate",
                        confidence_score=0.6,
                        data_source=data_source
                    ))
        
        return issues
    
    async def validate_revenue_engagement_correlation(
        self,
        rule: ValidationRule,
        data: Dict[str, Any],
        data_source: str
    ) -> List[ValidationIssue]:
        """Validate correlation between revenue and engagement"""
        issues = []
        
        revenue_streams = data.get('revenue_streams', [])
        engagement_metrics = data.get('engagement_metrics', [])
        min_correlation = rule.parameters.get('min_correlation', 0.3)
        
        # Create platform mapping
        engagement_by_platform = {
            metrics.get('platform'): metrics
            for metrics in engagement_metrics
        }
        
        revenue_engagement_pairs = []
        
        for stream in revenue_streams:
            platform = stream.get('platform')
            revenue = float(Decimal(str(stream.get('revenue', 0))))
            
            if platform in engagement_by_platform:
                metrics = engagement_by_platform[platform]
                engagement_score = (
                    metrics.get('engagement_rate', 0) *
                    metrics.get('follower_count', 0) / 100
                )
                
                revenue_engagement_pairs.append((revenue, engagement_score))
        
        # Calculate correlation if we have enough data points
        if len(revenue_engagement_pairs) >= 3:
            revenues = [pair[0] for pair in revenue_engagement_pairs]
            engagements = [pair[1] for pair in revenue_engagement_pairs]
            
            if all(r == revenues[0] for r in revenues) or all(e == engagements[0] for e in engagements):
                # No variation in data
                return issues
            
            try:
                correlation, p_value = stats.pearsonr(revenues, engagements)
                
                if abs(correlation) < min_correlation:
                    issues.append(ValidationIssue(
                        issue_id=str(uuid.uuid4()),
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        dimension=rule.dimension,
                        description=f"Low correlation between revenue and engagement: {correlation:.2f}",
                        affected_fields=['revenue_streams', 'engagement_metrics'],
                        current_value=f"{correlation:.2f}",
                        expected_value=f"≥ {min_correlation}",
                        suggestion="Review monetization effectiveness across platforms",
                        confidence_score=0.7,
                        data_source=data_source
                    ))
            except ValueError:
                # Correlation calculation failed (e.g., constant values)
                pass
        
        return issues
    
    async def validate_currency_compliance(
        self,
        rule: ValidationRule,
        data: Dict[str, Any],
        data_source: str
    ) -> List[ValidationIssue]:
        """Validate currency code compliance"""
        issues = []
        
        valid_currencies = rule.parameters.get('valid_currencies', ['EUR', 'USD', 'GBP'])
        revenue_streams = data.get('revenue_streams', [])
        
        for i, stream in enumerate(revenue_streams):
            currency = stream.get('currency')
            
            if currency and currency not in valid_currencies:
                issues.append(ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    dimension=rule.dimension,
                    description=f"Invalid currency code: {currency}",
                    affected_fields=[f'revenue_streams[{i}].currency'],
                    current_value=currency,
                    expected_value=f"One of: {', '.join(valid_currencies)}",
                    suggestion="Use valid ISO 4217 currency code",
                    confidence_score=1.0,
                    data_source=data_source
                ))
        
        return issues
    
    async def validate_data_freshness(
        self,
        rule: ValidationRule,
        data: Dict[str, Any],
        data_source: str
    ) -> List[ValidationIssue]:
        """Validate data freshness"""
        issues = []
        
        max_age_days = rule.parameters.get('max_age_days', 30)
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(days=max_age_days)
        
        # Check engagement metrics dates
        engagement_metrics = data.get('engagement_metrics', [])
        
        for i, metrics in enumerate(engagement_metrics):
            measurement_date = metrics.get('measurement_date')
            
            if measurement_date:
                try:
                    if isinstance(measurement_date, str):
                        measurement_date = datetime.fromisoformat(measurement_date.replace('Z', '+00:00'))
                    
                    if measurement_date < cutoff_time:
                        days_old = (current_time - measurement_date).days
                        
                        issues.append(ValidationIssue(
                            issue_id=str(uuid.uuid4()),
                            rule_name=rule.name,
                            category=rule.category,
                            severity=rule.severity,
                            dimension=rule.dimension,
                            description=f"Engagement metrics are {days_old} days old",
                            affected_fields=[f'engagement_metrics[{i}].measurement_date'],
                            current_value=measurement_date.isoformat(),
                            expected_value=f"Within {max_age_days} days",
                            suggestion="Update with more recent engagement data",
                            confidence_score=0.8,
                            data_source=data_source
                        ))
                except (ValueError, TypeError):
                    # Invalid date format already handled by other rules
                    pass
        
        return issues
    
    async def _calculate_quality_score(
        self,
        issues: List[ValidationIssue],
        passed_rules: List[str],
        failed_rules: List[str]
    ) -> float:
        """Calculate overall data quality score"""
        if not passed_rules and not failed_rules:
            return 0.0
        
        total_rules = len(passed_rules) + len(failed_rules)
        
        # Base score from rule success rate
        rule_success_rate = len(passed_rules) / total_rules if total_rules > 0 else 0
        
        # Penalty based on issue severity
        severity_penalties = {
            ValidationSeverity.CRITICAL: 0.3,
            ValidationSeverity.ERROR: 0.2,
            ValidationSeverity.WARNING: 0.1,
            ValidationSeverity.INFO: 0.05
        }
        
        total_penalty = 0
        for issue in issues:
            penalty = severity_penalties.get(issue.severity, 0.05)
            confidence_weight = issue.confidence_score
            total_penalty += penalty * confidence_weight
        
        # Cap penalty at 0.8 (don't let it exceed 80% reduction)
        total_penalty = min(total_penalty, 0.8)
        
        # Calculate final score
        quality_score = rule_success_rate * (1 - total_penalty)
        
        return max(0.0, min(1.0, quality_score))
    
    async def _generate_validation_summary(
        self,
        issues: List[ValidationIssue],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Generate validation summary statistics"""
        summary = {
            'total_issues': len(issues),
            'issues_by_severity': {},
            'issues_by_category': {},
            'issues_by_dimension': {},
            'most_common_issues': [],
            'data_completeness': await self._calculate_completeness(data),
            'blocking_issues_count': len([i for i in issues if i.is_blocking])
        }
        
        # Group by severity
        for severity in ValidationSeverity:
            count = len([i for i in issues if i.severity == severity])
            summary['issues_by_severity'][severity.value] = count
        
        # Group by category
        for category in ValidationCategory:
            count = len([i for i in issues if i.category == category])
            summary['issues_by_category'][category.value] = count
        
        # Group by dimension
        for dimension in DataQualityDimension:
            count = len([i for i in issues if i.dimension == dimension])
            summary['issues_by_dimension'][dimension.value] = count
        
        # Find most common issue types
        rule_counts = {}
        for issue in issues:
            rule_counts[issue.rule_name] = rule_counts.get(issue.rule_name, 0) + 1
        
        summary['most_common_issues'] = sorted(
            rule_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return summary
    
    async def _calculate_completeness(self, data: Dict[str, Any]) -> float:
        """
Calculate data completeness score"""
        # Expected fields
        expected_fields = [
            'user_id', 'reporting_period', 'total_revenue',
            'revenue_streams', 'engagement_metrics'
        ]
        
        present_fields = 0
        for field in expected_fields:
            if field in data and data[field] is not None:
                if isinstance(data[field], list):
                    if len(data[field]) > 0:
                        present_fields += 1
                else:
                    present_fields += 1
        
        return present_fields / len(expected_fields)
    
    async def _generate_recommendations(
        self,
        issues: List[ValidationIssue],
        quality_score: float
    ) -> List[str]:
        """
Generate actionable recommendations"""
        recommendations = []
        
        # Priority-based recommendations
        critical_issues = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
        error_issues = [i for i in issues if i.severity == ValidationSeverity.ERROR]
        
        if critical_issues:
            recommendations.append(f"URGENT: Fix {len(critical_issues)} critical data integrity issues immediately")
        
        if error_issues:
            recommendations.append(f"Fix {len(error_issues)} error-level validation issues")
        
        # Quality score based recommendations
        if quality_score < 0.5:
            recommendations.append("Data quality is poor - comprehensive data cleanup required")
        elif quality_score < 0.7:
            recommendations.append("Data quality needs improvement - address key validation issues")
        elif quality_score < 0.9:
            recommendations.append("Good data quality - minor improvements needed")
        else:
            recommendations.append("Excellent data quality - maintain current standards")
        
        # Category-specific recommendations
        category_counts = {}
        for issue in issues:
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
        
        if category_counts.get(ValidationCategory.DATA_INTEGRITY, 0) > 2:
            recommendations.append("Implement stricter data entry validation")
        
        if category_counts.get(ValidationCategory.STATISTICAL_ANOMALY, 0) > 1:
            recommendations.append("Review anomalous data points for accuracy")
        
        if category_counts.get(ValidationCategory.TEMPORAL_CONSISTENCY, 0) > 0:
            recommendations.append("Verify date/time consistency across data sources")
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def _count_records(self, data: Dict[str, Any]) -> int:
        """Count number of records in data"""
        # Simple count - in practice this would be more sophisticated
        record_counts = []
        
        if 'revenue_streams' in data and isinstance(data['revenue_streams'], list):
            record_counts.append(len(data['revenue_streams']))
        
        if 'engagement_metrics' in data and isinstance(data['engagement_metrics'], list):
            record_counts.append(len(data['engagement_metrics']))
        
        return max(record_counts) if record_counts else 1


async def create_revenue_validator(config: Optional[Dict[str, Any]] = None) -> RevenueValidator:
    """
Factory function to create and initialize revenue validator"""
    validator = RevenueValidator(config)
    await validator.initialize()
    return validator
