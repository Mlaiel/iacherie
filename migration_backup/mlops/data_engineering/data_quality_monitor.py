#!/usr/bin/env python3
"""
📊 MLOps Data Quality Monitor - Real-Time Data Validation System

Monitor de qualité de données en temps réel avec correction automatique.
Système de validation enterprise pour pipelines ML avec alertes et remédiation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Role: ML Engineer + DBA + Data Engineer + Backend Senior
"""

import asyncio
import json
import hashlib
import time
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
import logging
import re
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataQualityLevel(Enum):
    """Niveaux de qualité des données"""
    EXCELLENT = "excellent"      # 95-100%
    GOOD = "good"               # 85-94%
    ACCEPTABLE = "acceptable"   # 70-84%
    POOR = "poor"              # 50-69%
    CRITICAL = "critical"      # <50%


class IssueType(Enum):
    """Types de problèmes de qualité"""
    MISSING_VALUES = "missing_values"
    OUTLIERS = "outliers"
    DUPLICATES = "duplicates"
    INCONSISTENT_FORMAT = "inconsistent_format"
    INVALID_VALUES = "invalid_values"
    SCHEMA_VIOLATION = "schema_violation"
    RANGE_VIOLATION = "range_violation"
    DATA_DRIFT = "data_drift"
    FRESHNESS = "freshness"
    COMPLETENESS = "completeness"


class IssueSeverity(Enum):
    """Sévérité des problèmes"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFO = 5


@dataclass
class DataQualityRule:
    """Règle de qualité de données"""
    name: str
    description: str
    issue_type: IssueType
    severity: IssueSeverity
    column: Optional[str] = None
    condition: str = ""
    threshold: float = 0.0
    enabled: bool = True
    auto_fix: bool = False
    fix_strategy: Optional[str] = None


@dataclass
class DataQualityIssue:
    """Problème de qualité détecté"""
    id: str
    rule_name: str
    issue_type: IssueType
    severity: IssueSeverity
    column: Optional[str]
    description: str
    affected_rows: int
    total_rows: int
    percentage: float
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    auto_fixed: bool = False
    fix_applied: Optional[str] = None


@dataclass
class DataProfile:
    """Profil de données pour une colonne"""
    column_name: str
    data_type: str
    total_count: int
    non_null_count: int
    null_count: int
    unique_count: int
    duplicate_count: int
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    mean_value: Optional[float] = None
    std_dev: Optional[float] = None
    percentiles: Dict[int, Any] = field(default_factory=dict)
    top_values: List[Tuple[Any, int]] = field(default_factory=list)
    data_format_patterns: List[str] = field(default_factory=list)


@dataclass
class DatasetQualityReport:
    """Rapport de qualité pour un dataset"""
    dataset_id: str
    report_id: str
    generated_at: datetime
    total_rows: int
    total_columns: int
    overall_quality_score: float
    quality_level: DataQualityLevel
    column_profiles: Dict[str, DataProfile] = field(default_factory=dict)
    issues: List[DataQualityIssue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class DataProfiler:
    """Profileur de données pour analyse statistique"""
    
    def __init__(self):
        self.cache = {}
    
    async def profile_dataset(self, data: List[Dict[str, Any]], 
                            dataset_id: str = "unknown") -> Dict[str, DataProfile]:
        """Profile a dataset and return column profiles"""
        
        if not data:
            return {}
        
        column_profiles = {}
        columns = data[0].keys() if data else []
        
        for column in columns:
            profile = await self._profile_column(data, column)
            column_profiles[column] = profile
        
        logger.info(f"📊 Profiled dataset {dataset_id}: {len(columns)} columns, {len(data)} rows")
        return column_profiles
    
    async def _profile_column(self, data: List[Dict[str, Any]], column: str) -> DataProfile:
        """Profile a single column"""
        
        values = [row.get(column) for row in data]
        non_null_values = [v for v in values if v is not None and v != ""]
        
        profile = DataProfile(
            column_name=column,
            data_type=self._infer_data_type(non_null_values),
            total_count=len(values),
            non_null_count=len(non_null_values),
            null_count=len(values) - len(non_null_values),
            unique_count=len(set(non_null_values)),
            duplicate_count=len(non_null_values) - len(set(non_null_values))
        )
        
        if non_null_values:
            # Numerical statistics
            if profile.data_type in ['int', 'float']:
                try:
                    numeric_values = [float(v) for v in non_null_values if self._is_numeric(v)]
                    if numeric_values:
                        profile.min_value = min(numeric_values)
                        profile.max_value = max(numeric_values)
                        profile.mean_value = statistics.mean(numeric_values)
                        if len(numeric_values) > 1:
                            profile.std_dev = statistics.stdev(numeric_values)
                        
                        # Percentiles
                        sorted_values = sorted(numeric_values)
                        profile.percentiles = {
                            25: self._percentile(sorted_values, 25),
                            50: self._percentile(sorted_values, 50),
                            75: self._percentile(sorted_values, 75),
                            95: self._percentile(sorted_values, 95)
                        }
                except (ValueError, TypeError):
                    pass
            
            # String statistics
            elif profile.data_type == 'str':
                try:
                    str_values = [str(v) for v in non_null_values]
                    if str_values:
                        profile.min_value = min(len(s) for s in str_values)
                        profile.max_value = max(len(s) for s in str_values)
                        profile.mean_value = statistics.mean(len(s) for s in str_values)
                        
                        # Common patterns
                        profile.data_format_patterns = self._detect_patterns(str_values)
                except (ValueError, TypeError):
                    pass
            
            # Top values
            value_counts = defaultdict(int)
            for value in non_null_values:
                value_counts[value] += 1
            
            profile.top_values = sorted(
                value_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        
        return profile
    
    def _infer_data_type(self, values: List[Any]) -> str:
        """Infer data type from values"""
        if not values:
            return "unknown"
        
        # Check if all values are integers
        if all(self._is_integer(v) for v in values):
            return "int"
        
        # Check if all values are numeric
        if all(self._is_numeric(v) for v in values):
            return "float"
        
        # Check if all values are booleans
        if all(isinstance(v, bool) or str(v).lower() in ['true', 'false', '1', '0'] for v in values):
            return "bool"
        
        # Check if all values are dates
        if all(self._is_date(v) for v in values):
            return "datetime"
        
        # Default to string
        return "str"
    
    def _is_integer(self, value: Any) -> bool:
        """Check if value is an integer"""
        try:
            int(value)
            return float(value) == int(float(value))
        except (ValueError, TypeError):
            return False
    
    def _is_numeric(self, value: Any) -> bool:
        """Check if value is numeric"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _is_date(self, value: Any) -> bool:
        """Check if value is a date"""
        if isinstance(value, datetime):
            return True
        
        try:
            # Try common date formats
            date_formats = [
                "%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y",
                "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"
            ]
            
            str_value = str(value)
            for fmt in date_formats:
                try:
                    datetime.strptime(str_value, fmt)
                    return True
                except ValueError:
                    continue
        except:
            pass
        
        return False
    
    def _percentile(self, sorted_values: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not sorted_values:
            return 0.0
        
        index = (percentile / 100.0) * (len(sorted_values) - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(sorted_values) - 1)
        
        if lower_index == upper_index:
            return sorted_values[lower_index]
        
        # Linear interpolation
        weight = index - lower_index
        return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight
    
    def _detect_patterns(self, str_values: List[str]) -> List[str]:
        """Detect common patterns in string values"""
        patterns = []
        
        # Email pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if sum(1 for v in str_values if re.match(email_pattern, v)) > len(str_values) * 0.8:
            patterns.append("email")
        
        # Phone pattern
        phone_pattern = r'^\+?1?-?\.?\s?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})$'
        if sum(1 for v in str_values if re.match(phone_pattern, v)) > len(str_values) * 0.8:
            patterns.append("phone")
        
        # URL pattern
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if sum(1 for v in str_values if re.match(url_pattern, v)) > len(str_values) * 0.8:
            patterns.append("url")
        
        # UUID pattern
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if sum(1 for v in str_values if re.match(uuid_pattern, v)) > len(str_values) * 0.8:
            patterns.append("uuid")
        
        return patterns


class DataQualityRuleEngine:
    """Engine de règles de qualité de données"""
    
    def __init__(self):
        self.rules: Dict[str, DataQualityRule] = {}
        self._init_default_rules()
    
    def _init_default_rules(self):
        """Initialize default data quality rules"""
        
        # Completeness rules
        self.add_rule(DataQualityRule(
            name="null_values_check",
            description="Check for excessive null values",
            issue_type=IssueType.MISSING_VALUES,
            severity=IssueSeverity.MEDIUM,
            condition="null_percentage > threshold",
            threshold=0.1,  # 10%
            auto_fix=True,
            fix_strategy="impute_mean"
        ))
        
        # Outlier detection
        self.add_rule(DataQualityRule(
            name="outlier_detection",
            description="Detect statistical outliers using IQR method",
            issue_type=IssueType.OUTLIERS,
            severity=IssueSeverity.MEDIUM,
            condition="value < Q1 - 1.5*IQR or value > Q3 + 1.5*IQR",
            threshold=0.05,  # 5%
            auto_fix=True,
            fix_strategy="cap_outliers"
        ))
        
        # Duplicate detection
        self.add_rule(DataQualityRule(
            name="duplicate_rows",
            description="Check for duplicate rows",
            issue_type=IssueType.DUPLICATES,
            severity=IssueSeverity.LOW,
            condition="duplicate_percentage > threshold",
            threshold=0.02,  # 2%
            auto_fix=True,
            fix_strategy="remove_duplicates"
        ))
        
        # Data freshness
        self.add_rule(DataQualityRule(
            name="data_freshness",
            description="Check if data is fresh enough",
            issue_type=IssueType.FRESHNESS,
            severity=IssueSeverity.HIGH,
            condition="age_hours > threshold",
            threshold=24,  # 24 hours
            auto_fix=False
        ))
        
        # Format consistency
        self.add_rule(DataQualityRule(
            name="format_consistency",
            description="Check for consistent data formats",
            issue_type=IssueType.INCONSISTENT_FORMAT,
            severity=IssueSeverity.MEDIUM,
            condition="format_violation_percentage > threshold",
            threshold=0.05,  # 5%
            auto_fix=True,
            fix_strategy="standardize_format"
        ))
    
    def add_rule(self, rule: DataQualityRule):
        """Add a new quality rule"""
        self.rules[rule.name] = rule
        logger.info(f"✅ Added data quality rule: {rule.name}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a quality rule"""
        if rule_name in self.rules:
            del self.rules[rule_name]
            logger.info(f"🗑️ Removed data quality rule: {rule_name}")
            return True
        return False
    
    def get_rules_for_column(self, column_name: str, data_type: str) -> List[DataQualityRule]:
        """Get applicable rules for a column"""
        applicable_rules = []
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            # Global rules (no specific column)
            if rule.column is None:
                applicable_rules.append(rule)
                continue
            
            # Column-specific rules
            if rule.column == column_name:
                applicable_rules.append(rule)
                continue
            
            # Type-specific rules
            if rule.column == f"type:{data_type}":
                applicable_rules.append(rule)
                continue
        
        return applicable_rules


class DataQualityMonitor:
    """
    📊 Monitor de qualité de données enterprise pour MLOps
    
    Fonctionnalités:
    - Real-time data quality monitoring
    - Automated data profiling et statistical analysis
    - Rule-based quality validation
    - Automated issue detection et correction
    - Data drift detection
    - Quality score calculation
    - Alert system pour degradation
    - Historical quality tracking
    - Business-specific validation rules
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.profiler = DataProfiler()
        self.rule_engine = DataQualityRuleEngine()
        
        # Quality tracking
        self.quality_history: Dict[str, List[DatasetQualityReport]] = defaultdict(list)
        self.baseline_profiles: Dict[str, Dict[str, DataProfile]] = {}
        
        # Monitoring configuration
        self.monitoring_enabled = self.config.get('monitoring_enabled', True)
        self.auto_fix_enabled = self.config.get('auto_fix_enabled', True)
        self.alert_threshold = self.config.get('alert_threshold', 0.7)  # Quality score threshold
        
        # Metrics
        self.metrics = {
            'datasets_monitored': 0,
            'issues_detected': 0,
            'issues_auto_fixed': 0,
            'quality_alerts_sent': 0
        }
        
        logger.info("📊 Data Quality Monitor initialized for enterprise data validation")
    
    async def monitor_dataset(self, data: List[Dict[str, Any]], 
                            dataset_id: str, 
                            baseline: bool = False) -> DatasetQualityReport:
        """Monitor data quality for a dataset"""
        
        if not self.monitoring_enabled:
            logger.warning("⚠️ Data quality monitoring is disabled")
            return DatasetQualityReport(
                dataset_id=dataset_id,
                report_id="disabled",
                generated_at=datetime.now(),
                total_rows=0,
                total_columns=0,
                overall_quality_score=1.0,
                quality_level=DataQualityLevel.EXCELLENT
            )
        
        logger.info(f"🔍 Monitoring data quality for dataset: {dataset_id}")
        
        # Generate data profiles
        column_profiles = await self.profiler.profile_dataset(data, dataset_id)
        
        # Store baseline if requested
        if baseline:
            self.baseline_profiles[dataset_id] = column_profiles
            logger.info(f"📊 Stored baseline profiles for {dataset_id}")
        
        # Detect quality issues
        issues = await self._detect_quality_issues(data, column_profiles, dataset_id)
        
        # Auto-fix issues if enabled
        if self.auto_fix_enabled:
            fixed_data, fixed_issues = await self._auto_fix_issues(data, issues)
            issues = fixed_issues
        
        # Calculate overall quality score
        quality_score = self._calculate_quality_score(column_profiles, issues, len(data))
        quality_level = self._get_quality_level(quality_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues, column_profiles)
        
        # Create quality report
        report = DatasetQualityReport(
            dataset_id=dataset_id,
            report_id=hashlib.md5(f"{dataset_id}_{int(time.time())}".encode()).hexdigest()[:16],
            generated_at=datetime.now(),
            total_rows=len(data),
            total_columns=len(column_profiles),
            overall_quality_score=quality_score,
            quality_level=quality_level,
            column_profiles=column_profiles,
            issues=issues,
            recommendations=recommendations,
            metrics={
                'completeness_score': self._calculate_completeness_score(column_profiles),
                'consistency_score': self._calculate_consistency_score(issues),
                'freshness_score': 1.0,  # Simplified for demo
                'validity_score': self._calculate_validity_score(issues)
            }
        )
        
        # Store quality history
        self.quality_history[dataset_id].append(report)
        
        # Send alerts if quality is below threshold
        if quality_score < self.alert_threshold:
            await self._send_quality_alert(report)
        
        # Update metrics
        self.metrics['datasets_monitored'] += 1
        self.metrics['issues_detected'] += len(issues)
        
        logger.info(f"✅ Quality monitoring complete for {dataset_id}: {quality_score:.2f} score")
        
        return report
    
    async def _detect_quality_issues(self, data: List[Dict[str, Any]], 
                                   column_profiles: Dict[str, DataProfile],
                                   dataset_id: str) -> List[DataQualityIssue]:
        """Detect data quality issues using rules"""
        
        issues = []
        
        for column_name, profile in column_profiles.items():
            # Get applicable rules for this column
            applicable_rules = self.rule_engine.get_rules_for_column(column_name, profile.data_type)
            
            for rule in applicable_rules:
                issue = await self._check_rule(rule, profile, data, column_name)
                if issue:
                    issues.append(issue)
        
        # Check dataset-level issues
        dataset_issues = await self._check_dataset_level_issues(data, dataset_id)
        issues.extend(dataset_issues)
        
        return issues
    
    async def _check_rule(self, rule: DataQualityRule, profile: DataProfile,
                        data: List[Dict[str, Any]], column_name: str) -> Optional[DataQualityIssue]:
        """Check a specific rule against column data"""
        
        try:
            if rule.issue_type == IssueType.MISSING_VALUES:
                null_percentage = profile.null_count / profile.total_count if profile.total_count > 0 else 0
                if null_percentage > rule.threshold:
                    return DataQualityIssue(
                        id=f"{rule.name}_{column_name}_{int(time.time())}",
                        rule_name=rule.name,
                        issue_type=rule.issue_type,
                        severity=rule.severity,
                        column=column_name,
                        description=f"Column {column_name} has {null_percentage:.1%} null values (threshold: {rule.threshold:.1%})",
                        affected_rows=profile.null_count,
                        total_rows=profile.total_count,
                        percentage=null_percentage * 100
                    )
            
            elif rule.issue_type == IssueType.OUTLIERS:
                if profile.data_type in ['int', 'float'] and profile.percentiles:
                    outlier_count = self._count_outliers(data, column_name, profile)
                    outlier_percentage = outlier_count / profile.total_count if profile.total_count > 0 else 0
                    
                    if outlier_percentage > rule.threshold:
                        return DataQualityIssue(
                            id=f"{rule.name}_{column_name}_{int(time.time())}",
                            rule_name=rule.name,
                            issue_type=rule.issue_type,
                            severity=rule.severity,
                            column=column_name,
                            description=f"Column {column_name} has {outlier_percentage:.1%} outliers (threshold: {rule.threshold:.1%})",
                            affected_rows=outlier_count,
                            total_rows=profile.total_count,
                            percentage=outlier_percentage * 100
                        )
            
            elif rule.issue_type == IssueType.DUPLICATES:
                duplicate_percentage = profile.duplicate_count / profile.total_count if profile.total_count > 0 else 0
                if duplicate_percentage > rule.threshold:
                    return DataQualityIssue(
                        id=f"{rule.name}_{column_name}_{int(time.time())}",
                        rule_name=rule.name,
                        issue_type=rule.issue_type,
                        severity=rule.severity,
                        column=column_name,
                        description=f"Column {column_name} has {duplicate_percentage:.1%} duplicates (threshold: {rule.threshold:.1%})",
                        affected_rows=profile.duplicate_count,
                        total_rows=profile.total_count,
                        percentage=duplicate_percentage * 100
                    )
        
        except Exception as e:
            logger.error(f"❌ Error checking rule {rule.name} for column {column_name}: {e}")
        
        return None
    
    def _count_outliers(self, data: List[Dict[str, Any]], column_name: str, 
                       profile: DataProfile) -> int:
        """Count outliers using IQR method"""
        
        if not profile.percentiles or 25 not in profile.percentiles or 75 not in profile.percentiles:
            return 0
        
        q1 = profile.percentiles[25]
        q3 = profile.percentiles[75]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outlier_count = 0
        for row in data:
            value = row.get(column_name)
            if value is not None and self.profiler._is_numeric(value):
                numeric_value = float(value)
                if numeric_value < lower_bound or numeric_value > upper_bound:
                    outlier_count += 1
        
        return outlier_count
    
    async def _check_dataset_level_issues(self, data: List[Dict[str, Any]], 
                                        dataset_id: str) -> List[DataQualityIssue]:
        """Check dataset-level quality issues"""
        
        issues = []
        
        # Check for duplicate rows
        seen_rows = set()
        duplicate_count = 0
        
        for row in data:
            # Create a hashable representation of the row
            row_hash = hashlib.md5(json.dumps(row, sort_keys=True, default=str).encode()).hexdigest()
            if row_hash in seen_rows:
                duplicate_count += 1
            else:
                seen_rows.add(row_hash)
        
        if duplicate_count > 0:
            duplicate_percentage = duplicate_count / len(data)
            rule = self.rule_engine.rules.get("duplicate_rows")
            if rule and duplicate_percentage > rule.threshold:
                issues.append(DataQualityIssue(
                    id=f"duplicate_rows_{dataset_id}_{int(time.time())}",
                    rule_name="duplicate_rows",
                    issue_type=IssueType.DUPLICATES,
                    severity=IssueSeverity.LOW,
                    column=None,
                    description=f"Dataset has {duplicate_percentage:.1%} duplicate rows",
                    affected_rows=duplicate_count,
                    total_rows=len(data),
                    percentage=duplicate_percentage * 100
                ))
        
        return issues
    
    async def _auto_fix_issues(self, data: List[Dict[str, Any]], 
                             issues: List[DataQualityIssue]) -> Tuple[List[Dict[str, Any]], List[DataQualityIssue]]:
        """Auto-fix data quality issues where possible"""
        
        fixed_data = data.copy()
        remaining_issues = []
        
        for issue in issues:
            rule = self.rule_engine.rules.get(issue.rule_name)
            
            if rule and rule.auto_fix and rule.fix_strategy:
                try:
                    fixed_data = await self._apply_fix_strategy(fixed_data, issue, rule.fix_strategy)
                    issue.auto_fixed = True
                    issue.fix_applied = rule.fix_strategy
                    issue.resolved_at = datetime.now()
                    
                    self.metrics['issues_auto_fixed'] += 1
                    logger.info(f"🔧 Auto-fixed issue: {issue.description}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to auto-fix issue {issue.id}: {e}")
                    remaining_issues.append(issue)
            else:
                remaining_issues.append(issue)
        
        return fixed_data, remaining_issues
    
    async def _apply_fix_strategy(self, data: List[Dict[str, Any]], 
                                issue: DataQualityIssue, fix_strategy: str) -> List[Dict[str, Any]]:
        """Apply a fix strategy to resolve an issue"""
        
        if fix_strategy == "impute_mean" and issue.column:
            # Impute missing values with mean
            numeric_values = []
            for row in data:
                value = row.get(issue.column)
                if value is not None and self.profiler._is_numeric(value):
                    numeric_values.append(float(value))
            
            if numeric_values:
                mean_value = statistics.mean(numeric_values)
                for row in data:
                    if row.get(issue.column) is None:
                        row[issue.column] = mean_value
        
        elif fix_strategy == "cap_outliers" and issue.column:
            # Cap outliers at percentile bounds
            numeric_values = []
            for row in data:
                value = row.get(issue.column)
                if value is not None and self.profiler._is_numeric(value):
                    numeric_values.append(float(value))
            
            if len(numeric_values) > 4:  # Need at least 5 values for percentiles
                sorted_values = sorted(numeric_values)
                p5 = self.profiler._percentile(sorted_values, 5)
                p95 = self.profiler._percentile(sorted_values, 95)
                
                for row in data:
                    value = row.get(issue.column)
                    if value is not None and self.profiler._is_numeric(value):
                        numeric_value = float(value)
                        if numeric_value < p5:
                            row[issue.column] = p5
                        elif numeric_value > p95:
                            row[issue.column] = p95
        
        elif fix_strategy == "remove_duplicates":
            # Remove duplicate rows
            seen_rows = set()
            unique_data = []
            
            for row in data:
                row_hash = hashlib.md5(json.dumps(row, sort_keys=True, default=str).encode()).hexdigest()
                if row_hash not in seen_rows:
                    seen_rows.add(row_hash)
                    unique_data.append(row)
            
            return unique_data
        
        return data
    
    def _calculate_quality_score(self, column_profiles: Dict[str, DataProfile],
                               issues: List[DataQualityIssue], total_rows: int) -> float:
        """Calculate overall data quality score"""
        
        if not column_profiles:
            return 0.0
        
        # Base score from completeness
        completeness_score = self._calculate_completeness_score(column_profiles)
        
        # Penalty for issues
        issue_penalty = 0.0
        for issue in issues:
            if issue.severity == IssueSeverity.CRITICAL:
                issue_penalty += 0.3
            elif issue.severity == IssueSeverity.HIGH:
                issue_penalty += 0.2
            elif issue.severity == IssueSeverity.MEDIUM:
                issue_penalty += 0.1
            elif issue.severity == IssueSeverity.LOW:
                issue_penalty += 0.05
        
        # Combine scores
        quality_score = completeness_score - issue_penalty
        return max(0.0, min(1.0, quality_score))
    
    def _calculate_completeness_score(self, column_profiles: Dict[str, DataProfile]) -> float:
        """Calculate completeness score"""
        
        if not column_profiles:
            return 0.0
        
        total_completeness = 0.0
        for profile in column_profiles.values():
            if profile.total_count > 0:
                completeness = profile.non_null_count / profile.total_count
                total_completeness += completeness
        
        return total_completeness / len(column_profiles)
    
    def _calculate_consistency_score(self, issues: List[DataQualityIssue]) -> float:
        """Calculate consistency score based on format and type issues"""
        
        format_issues = [i for i in issues if i.issue_type == IssueType.INCONSISTENT_FORMAT]
        if not format_issues:
            return 1.0
        
        # Simple penalty-based scoring
        penalty = len(format_issues) * 0.1
        return max(0.0, 1.0 - penalty)
    
    def _calculate_validity_score(self, issues: List[DataQualityIssue]) -> float:
        """Calculate validity score based on rule violations"""
        
        validity_issues = [
            i for i in issues 
            if i.issue_type in [IssueType.INVALID_VALUES, IssueType.RANGE_VIOLATION, IssueType.SCHEMA_VIOLATION]
        ]
        
        if not validity_issues:
            return 1.0
        
        # Penalty based on severity
        penalty = 0.0
        for issue in validity_issues:
            if issue.severity == IssueSeverity.CRITICAL:
                penalty += 0.4
            elif issue.severity == IssueSeverity.HIGH:
                penalty += 0.3
            elif issue.severity == IssueSeverity.MEDIUM:
                penalty += 0.2
            else:
                penalty += 0.1
        
        return max(0.0, 1.0 - penalty)
    
    def _get_quality_level(self, quality_score: float) -> DataQualityLevel:
        """Convert quality score to quality level"""
        
        if quality_score >= 0.95:
            return DataQualityLevel.EXCELLENT
        elif quality_score >= 0.85:
            return DataQualityLevel.GOOD
        elif quality_score >= 0.70:
            return DataQualityLevel.ACCEPTABLE
        elif quality_score >= 0.50:
            return DataQualityLevel.POOR
        else:
            return DataQualityLevel.CRITICAL
    
    def _generate_recommendations(self, issues: List[DataQualityIssue],
                                column_profiles: Dict[str, DataProfile]) -> List[str]:
        """Generate recommendations for improving data quality"""
        
        recommendations = []
        
        # Issue-based recommendations
        for issue in issues:
            if issue.issue_type == IssueType.MISSING_VALUES:
                recommendations.append(f"Consider implementing data validation at source for column {issue.column}")
            elif issue.issue_type == IssueType.OUTLIERS:
                recommendations.append(f"Review data collection process for column {issue.column} to reduce outliers")
            elif issue.issue_type == IssueType.DUPLICATES:
                recommendations.append("Implement deduplication logic in data pipeline")
            elif issue.issue_type == IssueType.INCONSISTENT_FORMAT:
                recommendations.append(f"Standardize data format for column {issue.column}")
        
        # Profile-based recommendations
        for column_name, profile in column_profiles.items():
            if profile.unique_count == 1 and profile.non_null_count > 1:
                recommendations.append(f"Column {column_name} has constant values - consider removing")
            
            if profile.data_type == 'str' and profile.unique_count == profile.non_null_count:
                recommendations.append(f"Column {column_name} appears to be a unique identifier - verify if needed")
        
        return list(set(recommendations))  # Remove duplicates
    
    async def _send_quality_alert(self, report: DatasetQualityReport):
        """Send quality alert for poor data quality"""
        
        self.metrics['quality_alerts_sent'] += 1
        
        # In production, this would send to alerting system
        logger.warning(
            f"🚨 DATA QUALITY ALERT: Dataset {report.dataset_id} has quality score "
            f"{report.overall_quality_score:.2f} (threshold: {self.alert_threshold})"
        )
        
        critical_issues = [i for i in report.issues if i.severity == IssueSeverity.CRITICAL]
        if critical_issues:
            logger.critical(f"💥 CRITICAL ISSUES DETECTED: {len(critical_issues)} critical data quality issues")
    
    def get_quality_trends(self, dataset_id: str, days: int = 7) -> Dict[str, Any]:
        """Get quality trends for a dataset"""
        
        if dataset_id not in self.quality_history:
            return {}
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_reports = [
            report for report in self.quality_history[dataset_id]
            if report.generated_at >= cutoff_date
        ]
        
        if not recent_reports:
            return {}
        
        quality_scores = [r.overall_quality_score for r in recent_reports]
        issue_counts = [len(r.issues) for r in recent_reports]
        
        return {
            'dataset_id': dataset_id,
            'period_days': days,
            'total_reports': len(recent_reports),
            'quality_trend': {
                'current_score': quality_scores[-1] if quality_scores else 0,
                'average_score': statistics.mean(quality_scores) if quality_scores else 0,
                'min_score': min(quality_scores) if quality_scores else 0,
                'max_score': max(quality_scores) if quality_scores else 0,
                'score_std_dev': statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0
            },
            'issue_trend': {
                'current_issues': issue_counts[-1] if issue_counts else 0,
                'average_issues': statistics.mean(issue_counts) if issue_counts else 0,
                'total_issues': sum(issue_counts)
            }
        }
    
    def get_monitor_statistics(self) -> Dict[str, Any]:
        """Get data quality monitor statistics"""
        
        total_issues_by_type = defaultdict(int)
        total_issues_by_severity = defaultdict(int)
        
        for reports in self.quality_history.values():
            for report in reports:
                for issue in report.issues:
                    total_issues_by_type[issue.issue_type.value] += 1
                    total_issues_by_severity[issue.severity.value] += 1
        
        return {
            **self.metrics,
            'datasets_tracked': len(self.quality_history),
            'total_reports_generated': sum(len(reports) for reports in self.quality_history.values()),
            'issues_by_type': dict(total_issues_by_type),
            'issues_by_severity': dict(total_issues_by_severity),
            'auto_fix_rate': (self.metrics['issues_auto_fixed'] / max(self.metrics['issues_detected'], 1)) * 100,
            'rules_configured': len(self.rule_engine.rules)
        }


# Demo function
async def demo_data_quality_monitor():
    """Démonstration du data quality monitor"""
    print("📊 MLOps Data Quality Monitor Demo")
    
    # Initialize monitor
    monitor = DataQualityMonitor({
        'monitoring_enabled': True,
        'auto_fix_enabled': True,
        'alert_threshold': 0.8
    })
    
    # Sample data with quality issues
    sample_data = [
        {"user_id": 1, "name": "Alice", "email": "alice@example.com", "age": 25, "score": 85.5},
        {"user_id": 2, "name": "Bob", "email": "bob@test.com", "age": None, "score": 92.0},  # Missing age
        {"user_id": 3, "name": "Charlie", "email": "charlie@domain.com", "age": 30, "score": 1000.0},  # Outlier score
        {"user_id": 4, "name": "Diana", "email": "diana@example.com", "age": 28, "score": 78.2},
        {"user_id": 1, "name": "Alice", "email": "alice@example.com", "age": 25, "score": 85.5},  # Duplicate
        {"user_id": 5, "name": "Eve", "email": None, "age": 35, "score": 88.9},  # Missing email
        {"user_id": 6, "name": "", "age": 40, "score": 95.1},  # Empty name
        {"user_id": 7, "name": "Frank", "email": "frank@test.com", "age": -5, "score": 82.4},  # Invalid age
    ]
    
    # Monitor dataset quality
    print("🔍 Monitoring sample dataset...")
    quality_report = await monitor.monitor_dataset(sample_data, "user_dataset", baseline=True)
    
    print(f"\n📊 Quality Report Summary:")
    print(f"  Dataset: {quality_report.dataset_id}")
    print(f"  Overall Score: {quality_report.overall_quality_score:.2f}")
    print(f"  Quality Level: {quality_report.quality_level.value}")
    print(f"  Total Rows: {quality_report.total_rows}")
    print(f"  Total Columns: {quality_report.total_columns}")
    print(f"  Issues Detected: {len(quality_report.issues)}")
    
    # Show column profiles
    print(f"\n📋 Column Profiles:")
    for column_name, profile in quality_report.column_profiles.items():
        print(f"  {column_name}:")
        print(f"    Type: {profile.data_type}")
        print(f"    Completeness: {profile.non_null_count}/{profile.total_count} ({profile.non_null_count/profile.total_count*100:.1f}%)")
        print(f"    Unique values: {profile.unique_count}")
    
    # Show detected issues
    if quality_report.issues:
        print(f"\n🚨 Quality Issues Detected:")
        for issue in quality_report.issues:
            status = "✅ AUTO-FIXED" if issue.auto_fixed else "❌ NEEDS ATTENTION"
            print(f"  {issue.issue_type.value} in {issue.column or 'dataset'}: {issue.description} {status}")
    
    # Show recommendations
    if quality_report.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in quality_report.recommendations:
            print(f"  - {rec}")
    
    # Monitor second dataset to show trends
    print(f"\n🔄 Monitoring improved dataset...")
    improved_data = [
        {"user_id": 1, "name": "Alice", "email": "alice@example.com", "age": 25, "score": 85.5},
        {"user_id": 2, "name": "Bob", "email": "bob@test.com", "age": 32, "score": 92.0},
        {"user_id": 3, "name": "Charlie", "email": "charlie@domain.com", "age": 30, "score": 87.3},
        {"user_id": 4, "name": "Diana", "email": "diana@example.com", "age": 28, "score": 78.2},
        {"user_id": 5, "name": "Eve", "email": "eve@company.com", "age": 35, "score": 88.9},
    ]
    
    improved_report = await monitor.monitor_dataset(improved_data, "user_dataset")
    
    print(f"📈 Improved Quality Score: {improved_report.overall_quality_score:.2f}")
    print(f"📉 Issues Reduced: {len(quality_report.issues)} → {len(improved_report.issues)}")
    
    # Show quality trends
    print(f"\n📊 Quality Trends:")
    trends = monitor.get_quality_trends("user_dataset")
    if trends:
        print(f"  Current Score: {trends['quality_trend']['current_score']:.2f}")
        print(f"  Average Score: {trends['quality_trend']['average_score']:.2f}")
        print(f"  Total Reports: {trends['total_reports']}")
    
    # Monitor statistics
    print(f"\n📈 Monitor Statistics:")
    stats = monitor.get_monitor_statistics()
    print(f"  Datasets Monitored: {stats['datasets_monitored']}")
    print(f"  Issues Detected: {stats['issues_detected']}")
    print(f"  Auto-fix Rate: {stats['auto_fix_rate']:.1f}%")
    print(f"  Quality Alerts: {stats['quality_alerts_sent']}")


if __name__ == "__main__":
    asyncio.run(demo_data_quality_monitor())