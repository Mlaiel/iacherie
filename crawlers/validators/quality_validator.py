"""Data Quality Validation Engine for Crawler System
=================================================

Advanced data quality assessment and validation system for the IA Influencer Agent Platform
providing comprehensive quality metrics, scoring, and improvement recommendations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use, reproduction, or distribution strictly prohibited

Features:
- Multi-dimensional quality assessment
- Content completeness analysis
- Data consistency validation
- Quality scoring and benchmarking
- Automated quality improvement suggestions
"""import re
import math
import statistics
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

from ..utils.exceptions import ValidationException

logger = logging.getLogger(__name__)


class QualityDimension(Enum):
    """Quality assessment dimensions"""    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    ACCURACY = "accuracy"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"
    TIMELINESS = "timeliness"
    RELEVANCE = "relevance"
    COHERENCE = "coherence"


class QualityLevel(Enum):
    """Quality level classifications"""    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"


@dataclass
class QualityMetric:
    """Individual quality metric"""    dimension: QualityDimension
    score: float  # 0.0 to 1.0
    weight: float = 1.0
    description: str = ""
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    benchmark_score: Optional[float] = None
    threshold_passed: bool = True


@dataclass
class QualityProfile:
    """Comprehensive quality profile for content"""    overall_score: float
    quality_level: QualityLevel
    metrics: Dict[QualityDimension, QualityMetric] = field(default_factory=dict)
    assessment_time: datetime = field(default_factory=datetime.utcnow)
    content_type: str = "unknown"
    data_size: int = 0
    processing_time_ms: float = 0.0
    
    # Aggregated statistics
    passed_metrics: int = 0
    failed_metrics: int = 0
    total_metrics: int = 0
    improvement_potential: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate metric success rate"""        if self.total_metrics == 0:
            return 0.0
        return self.passed_metrics / self.total_metrics
    
    @property
    def dimension_scores(self) -> Dict[str, float]:
        """Get scores by dimension"""        return {dim.value: metric.score for dim, metric in self.metrics.items()}
    
    @property
    def critical_issues(self) -> List[str]:
        """Get all critical issues across metrics"""        issues = []
        for metric in self.metrics.values():
            if metric.score < 0.5:  # Critical threshold
                issues.extend(metric.issues)
        return issues
    
    @property
    def improvement_suggestions(self) -> List[str]:
        """Get all improvement suggestions"""        suggestions = []
        for metric in self.metrics.values():
            suggestions.extend(metric.suggestions)
        return list(set(suggestions))  # Remove duplicates


class DataQualityValidator:
    """    Enterprise-grade data quality validation engine for crawler systems.
    
    Provides comprehensive quality assessment including:
    - Completeness analysis (missing data, null values)
    - Consistency validation (format consistency, value consistency)
    - Accuracy assessment (data correctness, validation against sources)
    - Validity checking (constraint satisfaction, business rules)
    - Uniqueness analysis (duplicate detection, redundancy)
    - Timeliness evaluation (data freshness, update frequency)
    - Relevance scoring (business value, user needs)
    - Coherence assessment (logical consistency, relationships)
    """    
    def __init__(self, quality_thresholds: Optional[Dict[str, float]] = None):
        self.quality_thresholds = quality_thresholds or self._default_thresholds()
        self.benchmark_data = {}
        self.quality_rules = self._load_quality_rules()
        self.scoring_weights = self._load_scoring_weights()
        
        # Quality assessment cache
        self.assessment_cache = {}
        self.cache_ttl = timedelta(hours=1)
        
        logger.info("DataQualityValidator initialized")
    
    def assess_quality(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        content_type: str = "unknown",
        benchmark_against: Optional[str] = None,
        custom_rules: Optional[Dict[str, Any]] = None
    ) -> QualityProfile:
        """        Perform comprehensive quality assessment.
        
        Args:
            data: Data to assess (single record or list of records)
            content_type: Type of content being assessed
            benchmark_against: Optional benchmark dataset name
            custom_rules: Optional custom quality rules
            
        Returns:
            QualityProfile: Comprehensive quality assessment
        """        start_time = datetime.utcnow()
        
        # Normalize data to list format
        if isinstance(data, dict):
            data_list = [data]
            single_record = True
        else:
            data_list = data
            single_record = False
        
        # Check cache
        cache_key = self._generate_cache_key(data, content_type)
        if cache_key in self.assessment_cache:
            cached_profile, cached_time = self.assessment_cache[cache_key]
            if datetime.utcnow() - cached_time < self.cache_ttl:
                return cached_profile
        
        profile = QualityProfile(
            overall_score=0.0,
            quality_level=QualityLevel.POOR,
            content_type=content_type,
            data_size=len(data_list)
        )
        
        # Apply custom rules if provided
        rules = self.quality_rules.get(content_type, {})
        if custom_rules:
            rules.update(custom_rules)
        
        try:
            # Assess each quality dimension
            profile.metrics[QualityDimension.COMPLETENESS] = self._assess_completeness(
                data_list, rules.get('completeness', {}), single_record
            )
            
            profile.metrics[QualityDimension.CONSISTENCY] = self._assess_consistency(
                data_list, rules.get('consistency', {}), single_record
            )
            
            profile.metrics[QualityDimension.ACCURACY] = self._assess_accuracy(
                data_list, rules.get('accuracy', {}), single_record
            )
            
            profile.metrics[QualityDimension.VALIDITY] = self._assess_validity(
                data_list, rules.get('validity', {}), single_record
            )
            
            profile.metrics[QualityDimension.UNIQUENESS] = self._assess_uniqueness(
                data_list, rules.get('uniqueness', {}), single_record
            )
            
            profile.metrics[QualityDimension.TIMELINESS] = self._assess_timeliness(
                data_list, rules.get('timeliness', {}), single_record
            )
            
            profile.metrics[QualityDimension.RELEVANCE] = self._assess_relevance(
                data_list, rules.get('relevance', {}), single_record
            )
            
            profile.metrics[QualityDimension.COHERENCE] = self._assess_coherence(
                data_list, rules.get('coherence', {}), single_record
            )
            
            # Calculate overall score and statistics
            self._calculate_overall_score(profile)
            self._calculate_statistics(profile)
            self._determine_quality_level(profile)
            
            # Apply benchmarking if specified
            if benchmark_against and benchmark_against in self.benchmark_data:
                self._apply_benchmarking(profile, benchmark_against)
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {str(e)}")
            profile.metrics[QualityDimension.VALIDITY] = QualityMetric(
                dimension=QualityDimension.VALIDITY,
                score=0.0,
                description="Assessment failed",
                issues=[f"Quality assessment error: {str(e)}"]
            )
        
        # Record processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        profile.processing_time_ms = processing_time
        
        # Cache result
        self.assessment_cache[cache_key] = (profile, datetime.utcnow())
        
        logger.debug(f"Quality assessment completed in {processing_time:.2f}ms")
        return profile
    
    def _assess_completeness(
        self, 
        data_list: List[Dict[str, Any]], 
        rules: Dict[str, Any],
        single_record: bool
    ) -> QualityMetric:
        """Assess data completeness"""        
        metric = QualityMetric(
            dimension=QualityDimension.COMPLETENESS,
            score=1.0,
            description="Data completeness assessment"
        )
        
        if not data_list:
            metric.score = 0.0
            metric.issues.append("No data provided")
            return metric
        
        required_fields = rules.get('required_fields', [])
        optional_fields = rules.get('optional_fields', [])
        all_fields = required_fields + optional_fields
        
        completeness_scores = []
        missing_fields_count = {}
        
        for record in data_list:
            record_score = 0.0
            total_weight = 0.0
            
            # Check required fields (higher weight)
            for field in required_fields:
                total_weight += 1.0
                if field in record and record[field] is not None and str(record[field]).strip():
                    record_score += 1.0
                else:
                    missing_fields_count[field] = missing_fields_count.get(field, 0) + 1
            
            # Check optional fields (lower weight)
            for field in optional_fields:
                total_weight += 0.5
                if field in record and record[field] is not None and str(record[field]).strip():
                    record_score += 0.5
                else:
                    missing_fields_count[field] = missing_fields_count.get(field, 0) + 1
            
            if total_weight > 0:
                completeness_scores.append(record_score / total_weight)
            else:
                # No defined fields, assess based on non-null values
                non_null_count = sum(1 for v in record.values() if v is not None and str(v).strip())
                total_count = len(record)
                completeness_scores.append(non_null_count / total_count if total_count > 0 else 0)
        
        # Calculate overall completeness score
        if completeness_scores:
            metric.score = statistics.mean(completeness_scores)
        
        # Generate issues and suggestions
        if missing_fields_count:
            missing_threshold = len(data_list) * 0.2  # 20% threshold
            critical_missing = [
                field for field, count in missing_fields_count.items() 
                if count > missing_threshold and field in required_fields
            ]
            
            if critical_missing:
                metric.issues.extend([
                    f"Critical field '{field}' missing in {missing_fields_count[field]}/{len(data_list)} records"
                    for field in critical_missing
                ])
                metric.suggestions.append("Ensure all required fields are populated")
        
        if metric.score < 0.8:
            metric.suggestions.append("Improve data collection processes to reduce missing values")
        
        return metric
    
    def _assess_consistency(
        self, 
        data_list: List[Dict[str, Any]], 
        rules: Dict[str, Any],
        single_record: bool
    ) -> QualityMetric:
        """Assess data consistency"""        
        metric = QualityMetric(
            dimension=QualityDimension.CONSISTENCY,
            score=1.0,
            description="Data consistency assessment"
        )
        
        if len(data_list) < 2 and not single_record:
            metric.score = 0.5
            metric.issues.append("Insufficient data for consistency analysis")
            return metric
        
        consistency_scores = []
        format_patterns = rules.get('format_patterns', {})
        
        # Check format consistency
        for field, pattern in format_patterns.items():
            field_values = [
                record.get(field) for record in data_list 
                if field in record and record[field] is not None
            ]
            
            if field_values:
                matching_pattern = sum(
                    1 for value in field_values 
                    if re.match(pattern, str(value))
                )
                consistency_score = matching_pattern / len(field_values)
                consistency_scores.append(consistency_score)
                
                if consistency_score < 0.8:
                    metric.issues.append(f"Field '{field}' has inconsistent format patterns")
        
        # Check value consistency across records
        if not single_record:
            categorical_fields = rules.get('categorical_fields', [])
            for field in categorical_fields:
                field_values = [
                    record.get(field) for record in data_list 
                    if field in record and record[field] is not None
                ]
                
                if field_values:
                    unique_values = set(str(v).lower() for v in field_values)
                    # Check for potential duplicates with different cases/formats
                    normalized_values = set()
                    duplicates = 0
                    
                    for value in unique_values:
                        normalized = re.sub(r'[^\w]', '', value.lower())
                        if normalized in normalized_values:
                            duplicates += 1
                        normalized_values.add(normalized)
                    
                    if duplicates > 0:
                        metric.issues.append(f"Field '{field}' has potential duplicate values with different formats")
        
        # Check numeric consistency
        numeric_fields = rules.get('numeric_fields', [])
        for field in numeric_fields:
            numeric_values = []
            for record in data_list:
                if field in record and record[field] is not None:
                    try:
                        numeric_values.append(float(record[field]))
                    except (ValueError, TypeError):
                        pass
            
            if numeric_values and len(numeric_values) > 1:
                # Check for outliers using IQR method
                q1 = statistics.quantiles(numeric_values, n=4)[0]
                q3 = statistics.quantiles(numeric_values, n=4)[2]
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outliers = [v for v in numeric_values if v < lower_bound or v > upper_bound]
                if outliers:
                    outlier_ratio = len(outliers) / len(numeric_values)
                    if outlier_ratio > 0.1:  # More than 10% outliers
                        metric.issues.append(f"Field '{field}' has significant outliers ({outlier_ratio:.1%})")
                        consistency_scores.append(1.0 - outlier_ratio)
        
        # Calculate overall consistency score
        if consistency_scores:
            metric.score = statistics.mean(consistency_scores)
        elif single_record:
            # For single records, check internal consistency
            metric.score = self._check_internal_consistency(data_list[0], rules)
        
        if metric.score < 0.7:
            metric.suggestions.append("Standardize data formats and validation rules")
        
        return metric
    
    def _assess_accuracy(
        self, 
        data_list: List[Dict[str, Any]], 
        rules: Dict[str, Any],
        single_record: bool
    ) -> QualityMetric:
        """Assess data accuracy"""        
        metric = QualityMetric(
            dimension=QualityDimension.ACCURACY,
            score=0.8,  # Default moderate score
            description="Data accuracy assessment"
        )
        
        accuracy_scores = []
        reference_data = rules.get('reference_data', {})
        validation_rules = rules.get('validation_rules', [])
        
        # Check against reference data
        for field, reference_values in reference_data.items():
            matching_values = 0
            total_values = 0
            
            for record in data_list:
                if field in record and record[field] is not None:
                    total_values += 1
                    if record[field] in reference_values:
                        matching_values += 1
            
            if total_values > 0:
                accuracy_score = matching_values / total_values
                accuracy_scores.append(accuracy_score)
                
                if accuracy_score < 0.8:
                    metric.issues.append(f"Field '{field}' has potential accuracy issues")
        
        # Apply validation rules
        for rule in validation_rules:
            rule_name = rule.get('name', 'unnamed_rule')
            rule_function = rule.get('function')
            
            if callable(rule_function):
                violations = 0
                total_checks = 0
                
                for record in data_list:
                    total_checks += 1
                    try:
                        if not rule_function(record):
                            violations += 1
                    except Exception:
                        violations += 1
                
                if total_checks > 0:
                    rule_score = 1.0 - (violations / total_checks)
                    accuracy_scores.append(rule_score)
                    
                    if rule_score < 0.8:
                        metric.issues.append(f"Validation rule '{rule_name}' failed for {violations}/{total_checks} records")
        
        # Check for known accuracy patterns
        self._check_accuracy_patterns(data_list, metric)
        
        # Calculate overall accuracy score
        if accuracy_scores:
            metric.score = statistics.mean(accuracy_scores)
        
        if metric.score < 0.7:
            metric.suggestions.append("Verify data sources and improve data collection accuracy")
        
        return metric
    
    def _assess_validity(
        self, 
        data_list: List[Dict[str, Any]], 
        rules: Dict[str, Any],
        single_record: bool
    ) -> QualityMetric:
        """Assess data validity against business rules and constraints"""        
        metric = QualityMetric(
            dimension=QualityDimension.VALIDITY,
            score=1.0,
            description="Data validity assessment"
        )
        
        validity_scores = []
        constraints = rules.get('constraints', {})
        business_rules = rules.get('business_rules', [])
        
        # Check field constraints
        for field, constraint_list in constraints.items():
            violations = 0
            total_values = 0
            
            for record in data_list:
                if field in record and record[field] is not None:
                    total_values += 1
                    value = record[field]
                    
                    for constraint in constraint_list:
                        if not self._check_constraint(value, constraint):
                            violations += 1
                            break
            
            if total_values > 0:
                validity_score = 1.0 - (violations / total_values)
                validity_scores.append(validity_score)
                
                if violations > 0:
                    metric.issues.append(f"Field '{field}' has {violations}/{total_values} constraint violations")
        
        # Check business rules
        for rule in business_rules:
            rule_name = rule.get('name', 'unnamed_rule')
            rule_function = rule.get('function')
            
            if callable(rule_function):
                violations = 0
                total_checks = len(data_list)
                
                for record in data_list:
                    try:
                        if not rule_function(record):
                            violations += 1
                    except Exception:
                        violations += 1
                
                if total_checks > 0:
                    rule_score = 1.0 - (violations / total_checks)
                    validity_scores.append(rule_score)
                    
                    if violations > 0:
                        metric.issues.append(f"Business rule '{rule_name}' violated in {violations}/{total_checks} records")
        
        # Calculate overall validity score
        if validity_scores:
            metric.score = statistics.mean(validity_scores)
        
        if metric.score < 0.8:
            metric.suggestions.append("Review and enforce data validation rules")
        
        return metric
    
    def _assess_uniqueness(
        self, 
        data_list: List[Dict[str, Any]], 
        rules: Dict[str, Any],
        single_record: bool
    ) -> QualityMetric:
        """Assess data uniqueness and identify duplicates"""        
        metric = QualityMetric(
            dimension=QualityDimension.UNIQUENESS,
            score=1.0,
            description="Data uniqueness assessment"
        )
        
        if single_record:
            metric.score = 1.0  # Single record is always unique
            return metric
        
        if len(data_list) < 2:
            metric.score = 1.0
            return metric
        
        unique_fields = rules.get('unique_fields', [])
        duplicate_threshold = rules.get('duplicate_threshold', 0.1)  # 10% threshold
        
        total_duplicates = 0
        total_checks = 0
        
        # Check uniqueness of specified fields
        for field in unique_fields:
            field_values = []
            for record in data_list:
                if field in record and record[field] is not None:
                    field_values.append(str(record[field]).lower().strip())
            
            if field_values:
                unique_values = len(set(field_values))
                total_values = len(field_values)
                duplicates = total_values - unique_values
                
                total_duplicates += duplicates
                total_checks += total_values
                
                if duplicates > 0:
                    duplicate_ratio = duplicates / total_values
                    if duplicate_ratio > duplicate_threshold:
                        metric.issues.append(f"Field '{field}' has {duplicates} duplicate values ({duplicate_ratio:.1%})")
        
        # Check for record-level duplicates
        record_hashes = []
        for record in data_list:
            # Create a hash of the record for duplicate detection
            record_str = json.dumps(record, sort_keys=True, default=str)
            record_hash = hash(record_str)
            record_hashes.append(record_hash)
        
        unique_records = len(set(record_hashes))
        total_records = len(record_hashes)
        record_duplicates = total_records - unique_records
        
        if record_duplicates > 0:
            duplicate_ratio = record_duplicates / total_records
            metric.issues.append(f"Found {record_duplicates} duplicate records ({duplicate_ratio:.1%})")
            total_duplicates += record_duplicates
            total_checks += total_records
        
        # Calculate uniqueness score
        if total_checks > 0:
            metric.score = 1.0 - (total_duplicates / total_checks)
        
        if metric.score < 0.9:
            metric.suggestions.append("Implement deduplication processes and unique constraints")
        
        return metric
    
    def _assess_timeliness(
        self, 
        data_list: List[Dict[str, Any]], 
        rules: Dict[str, Any],
        single_record: bool
    ) -> QualityMetric:
        """Assess data timeliness and freshness"""        
        metric = QualityMetric(
            dimension=QualityDimension.TIMELINESS,
            score=0.8,  # Default moderate score
            description="Data timeliness assessment"
        )
        
        timestamp_fields = rules.get('timestamp_fields', ['created_at', 'updated_at', 'timestamp'])
        freshness_threshold = rules.get('freshness_threshold_hours', 24)
        update_frequency = rules.get('expected_update_frequency_hours', 24)
        
        current_time = datetime.utcnow()
        timeliness_scores = []
        
        for record in data_list:
            record_timestamps = []
            
            # Extract timestamps from record
            for field in timestamp_fields:
                if field in record and record[field] is not None:
                    try:
                        if isinstance(record[field], str):
                            # Try to parse common timestamp formats
                            timestamp = self._parse_timestamp(record[field])
                        elif isinstance(record[field], datetime):
                            timestamp = record[field]
                        elif isinstance(record[field], (int, float)):
                            timestamp = datetime.fromtimestamp(record[field])
                        else:
                            continue
                        
                        record_timestamps.append(timestamp)
                    except Exception:
                        continue
            
            if record_timestamps:
                # Use the most recent timestamp
                latest_timestamp = max(record_timestamps)
                age_hours = (current_time - latest_timestamp).total_seconds() / 3600
                
                # Calculate freshness score
                if age_hours <= freshness_threshold:
                    freshness_score = 1.0
                elif age_hours <= freshness_threshold * 3:
                    freshness_score = 1.0 - ((age_hours - freshness_threshold) / (freshness_threshold * 2))
                else:
                    freshness_score = 0.0
                
                timeliness_scores.append(freshness_score)
                
                if freshness_score < 0.7:
                    metric.issues.append(f"Record has stale data (age: {age_hours:.1f} hours)")
        
        # Calculate overall timeliness score
        if timeliness_scores:
            metric.score = statistics.mean(timeliness_scores)
        
        if metric.score < 0.6:
            metric.suggestions.append("Implement more frequent data updates and real-time synchronization")
        
        return metric
    
    def _assess_relevance(
        self, 
        data_list: List[Dict[str, Any]], 
        rules: Dict[str, Any],
        single_record: bool
    ) -> QualityMetric:
        """Assess data relevance to business needs"""        
        metric = QualityMetric(
            dimension=QualityDimension.RELEVANCE,
            score=0.8,  # Default moderate score
            description="Data relevance assessment"
        )
        
        relevance_fields = rules.get('relevance_fields', [])
        business_keywords = rules.get('business_keywords', [])
        context_requirements = rules.get('context_requirements', {})
        
        relevance_scores = []
        
        for record in data_list:
            record_score = 0.0
            total_weight = 0.0
            
            # Check relevance fields
            for field in relevance_fields:
                if field in record and record[field] is not None:
                    total_weight += 1.0
                    field_value = str(record[field]).lower()
                    
                    # Check for business keywords
                    keyword_matches = sum(1 for keyword in business_keywords if keyword.lower() in field_value)
                    if keyword_matches > 0:
                        record_score += min(1.0, keyword_matches / len(business_keywords))
                    
            # Check context requirements
            for requirement, expected_value in context_requirements.items():
                if requirement in record:
                    total_weight += 1.0
                    if record[requirement] == expected_value:
                        record_score += 1.0
            
            if total_weight > 0:
                relevance_scores.append(record_score / total_weight)
            else:
                # Basic relevance check
                non_empty_fields = sum(1 for v in record.values() if v is not None and str(v).strip())
                total_fields = len(record)
                relevance_scores.append(non_empty_fields / total_fields if total_fields > 0 else 0)
        
        # Calculate overall relevance score
        if relevance_scores:
            metric.score = statistics.mean(relevance_scores)
        
        if metric.score < 0.6:
            metric.suggestions.append("Filter data to focus on business-relevant information")
        
        return metric
    
    def _assess_coherence(
        self, 
        data_list: List[Dict[str, Any]], 
        rules: Dict[str, Any],
        single_record: bool
    ) -> QualityMetric:
        """Assess logical coherence and relationship consistency"""        
        metric = QualityMetric(
            dimension=QualityDimension.COHERENCE,
            score=1.0,
            description="Data coherence assessment"
        )
        
        relationship_rules = rules.get('relationship_rules', [])
        logical_constraints = rules.get('logical_constraints', [])
        
        coherence_scores = []
        
        for record in data_list:
            record_score = 1.0
            violations = 0
            total_checks = 0
            
            # Check relationship rules
            for rule in relationship_rules:
                total_checks += 1
                try:
                    if not self._check_relationship_rule(record, rule):
                        violations += 1
                        rule_name = rule.get('name', 'unnamed_rule')
                        metric.issues.append(f"Relationship rule '{rule_name}' violated")
                except Exception:
                    violations += 1
            
            # Check logical constraints
            for constraint in logical_constraints:
                total_checks += 1
                try:
                    if not self._check_logical_constraint(record, constraint):
                        violations += 1
                        constraint_name = constraint.get('name', 'unnamed_constraint')
                        metric.issues.append(f"Logical constraint '{constraint_name}' violated")
                except Exception:
                    violations += 1
            
            if total_checks > 0:
                record_score = 1.0 - (violations / total_checks)
            
            coherence_scores.append(record_score)
        
        # Calculate overall coherence score
        if coherence_scores:
            metric.score = statistics.mean(coherence_scores)
        
        if metric.score < 0.8:
            metric.suggestions.append("Review data relationships and ensure logical consistency")
        
        return metric
    
    # Helper methods
    
    def _calculate_overall_score(self, profile: QualityProfile) -> None:
        """Calculate weighted overall quality score"""        total_score = 0.0
        total_weight = 0.0
        
        for dimension, metric in profile.metrics.items():
            weight = self.scoring_weights.get(dimension.value, 1.0)
            total_score += metric.score * weight
            total_weight += weight
        
        if total_weight > 0:
            profile.overall_score = total_score / total_weight
        else:
            profile.overall_score = 0.0
    
    def _calculate_statistics(self, profile: QualityProfile) -> None:
        """Calculate quality statistics"""        profile.total_metrics = len(profile.metrics)
        profile.passed_metrics = sum(
            1 for metric in profile.metrics.values() 
            if metric.score >= self.quality_thresholds.get(metric.dimension.value, 0.7)
        )
        profile.failed_metrics = profile.total_metrics - profile.passed_metrics
        
        # Calculate improvement potential
        max_possible_score = 1.0
        profile.improvement_potential = max_possible_score - profile.overall_score
    
    def _determine_quality_level(self, profile: QualityProfile) -> None:
        """Determine overall quality level"""        score = profile.overall_score
        
        if score >= 0.9:
            profile.quality_level = QualityLevel.EXCELLENT
        elif score >= 0.8:
            profile.quality_level = QualityLevel.GOOD
        elif score >= 0.6:
            profile.quality_level = QualityLevel.FAIR
        elif score >= 0.4:
            profile.quality_level = QualityLevel.POOR
        else:
            profile.quality_level = QualityLevel.UNACCEPTABLE
    
    def _apply_benchmarking(self, profile: QualityProfile, benchmark_name: str) -> None:
        """Apply benchmarking against reference dataset"""        benchmark_scores = self.benchmark_data.get(benchmark_name, {})
        
        for dimension, metric in profile.metrics.items():
            benchmark_score = benchmark_scores.get(dimension.value)
            if benchmark_score is not None:
                metric.benchmark_score = benchmark_score
                metric.threshold_passed = metric.score >= benchmark_score
    
    def _generate_cache_key(self, data: Any, content_type: str) -> str:
        """Generate cache key for quality assessment"""        import hashlib
        data_hash = hashlib.md5(str(data).encode()).hexdigest()[:16]
        return f"{content_type}_{data_hash}"
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string in various formats"""        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%d',
            '%d/%m/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M:%S'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        # Try ISO format
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError(f"Unable to parse timestamp: {timestamp_str}")
    
    def _check_internal_consistency(self, record: Dict[str, Any], rules: Dict[str, Any]) -> float:
        """Check internal consistency of a single record"""        consistency_checks = rules.get('internal_consistency', [])
        
        if not consistency_checks:
            return 1.0  # No consistency rules defined
        
        passed_checks = 0
        total_checks = len(consistency_checks)
        
        for check in consistency_checks:
            try:
                if callable(check):
                    if check(record):
                        passed_checks += 1
                elif isinstance(check, dict):
                    check_function = check.get('function')
                    if callable(check_function) and check_function(record):
                        passed_checks += 1
            except Exception:
                pass
        
        return passed_checks / total_checks if total_checks > 0 else 1.0
    
    def _check_accuracy_patterns(self, data_list: List[Dict[str, Any]], metric: QualityMetric) -> None:
        """Check for known accuracy patterns and anomalies"""        
        # Check for suspicious patterns
        for record in data_list:
            # Check for placeholder values
            placeholder_patterns = ['test', 'example', 'placeholder', 'dummy', 'sample', 'default']
            for field, value in record.items():
                if isinstance(value, str):
                    value_lower = value.lower()
                    if any(pattern in value_lower for pattern in placeholder_patterns):
                        metric.issues.append(f"Potential placeholder value detected in field '{field}': {value}")
                        metric.score = max(0.0, metric.score - 0.1)
            
            # Check for repeated characters (potential data corruption)
            for field, value in record.items():
                if isinstance(value, str) and len(value) > 5:
                    # Check for 3 or more repeated characters
                    if re.search(r'(.)\1{2,}', value):
                        metric.issues.append(f"Repeated characters detected in field '{field}' (potential corruption)")
                        metric.score = max(0.0, metric.score - 0.05)
    
    def _check_constraint(self, value: Any, constraint: Dict[str, Any]) -> bool:
        """Check if value satisfies constraint"""        constraint_type = constraint.get('type')
        constraint_value = constraint.get('value')
        
        if constraint_type == 'min_length' and isinstance(value, str):
            return len(value) >= constraint_value
        elif constraint_type == 'max_length' and isinstance(value, str):
            return len(value) <= constraint_value
        elif constraint_type == 'pattern' and isinstance(value, str):
            return re.match(constraint_value, value) is not None
        elif constraint_type == 'range' and isinstance(value, (int, float)):
            min_val = constraint.get('min', float('-inf'))
            max_val = constraint.get('max', float('inf'))
            return min_val <= value <= max_val
        elif constraint_type == 'enum':
            return value in constraint_value
        elif constraint_type == 'not_null':
            return value is not None
        
        return True  # Unknown constraint type, pass by default
    
    def _check_relationship_rule(self, record: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """Check relationship rule between fields"""        rule_type = rule.get('type')
        
        if rule_type == 'field_dependency':
            parent_field = rule.get('parent_field')
            child_field = rule.get('child_field')
            
            if parent_field in record and record[parent_field] is not None:
                return child_field in record and record[child_field] is not None
            return True
        
        elif rule_type == 'mutual_exclusion':
            fields = rule.get('fields', [])
            present_fields = [f for f in fields if f in record and record[f] is not None]
            return len(present_fields) <= 1
        
        elif rule_type == 'date_ordering':
            start_field = rule.get('start_field')
            end_field = rule.get('end_field')
            
            if start_field in record and end_field in record:
                try:
                    start_date = self._parse_timestamp(str(record[start_field]))
                    end_date = self._parse_timestamp(str(record[end_field]))
                    return start_date <= end_date
                except Exception:
                    return True
        
        return True
    
    def _check_logical_constraint(self, record: Dict[str, Any], constraint: Dict[str, Any]) -> bool:
        """Check logical constraint"""        constraint_function = constraint.get('function')
        
        if callable(constraint_function):
            try:
                return constraint_function(record)
            except Exception:
                return False
        
        return True
    
    def _default_thresholds(self) -> Dict[str, float]:
        """Default quality thresholds for each dimension"""        return {
            'completeness': 0.8,
            'consistency': 0.7,
            'accuracy': 0.8,
            'validity': 0.9,
            'uniqueness': 0.95,
            'timeliness': 0.6,
            'relevance': 0.7,
            'coherence': 0.8
        }
    
    def _load_quality_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load quality rules for different content types"""        return {
            'user_profile': {
                'completeness': {
                    'required_fields': ['username', 'email'],
                    'optional_fields': ['first_name', 'last_name', 'bio', 'avatar_url']
                },
                'consistency': {
                    'format_patterns': {
                        'email': r'^[^@]+@[^@]+\.[^@]+$',
                        'username': r'^[a-zA-Z0-9_]{3,30}$'
                    },
                    'categorical_fields': ['status', 'role']
                },
                'validity': {
                    'constraints': {
                        'email': [{'type': 'pattern', 'value': r'^[^@]+@[^@]+\.[^@]+$'}],
                        'age': [{'type': 'range', 'min': 13, 'max': 120}]
                    }
                }
            },
            
            'social_media_post': {
                'completeness': {
                    'required_fields': ['content', 'platform', 'author_id'],
                    'optional_fields': ['hashtags', 'mentions', 'media_urls']
                },
                'consistency': {
                    'format_patterns': {
                        'platform': r'^(twitter|instagram|facebook|linkedin|tiktok)$'
                    }
                },
                'relevance': {
                    'business_keywords': ['engagement', 'followers', 'likes', 'shares', 'content'],
                    'relevance_fields': ['content', 'hashtags']
                }
            },
            
            'content_item': {
                'completeness': {
                    'required_fields': ['title', 'content_type', 'status'],
                    'optional_fields': ['description', 'tags', 'thumbnail_url']
                },
                'timeliness': {
                    'timestamp_fields': ['created_at', 'updated_at', 'published_at'],
                    'freshness_threshold_hours': 48
                },
                'coherence': {
                    'relationship_rules': [
                        {
                            'type': 'field_dependency',
                            'parent_field': 'status',
                            'child_field': 'published_at',
                            'name': 'published_status_dependency'
                        }
                    ]
                }
            }
        }
    
    def _load_scoring_weights(self) -> Dict[str, float]:
        """Load scoring weights for quality dimensions"""        return {
            'completeness': 1.2,
            'consistency': 1.0,
            'accuracy': 1.3,
            'validity': 1.4,
            'uniqueness': 0.8,
            'timeliness': 0.9,
            'relevance': 1.1,
            'coherence': 1.0
        }
    
    def add_benchmark_data(self, benchmark_name: str, dimension_scores: Dict[str, float]) -> None:
        """Add benchmark data for comparison"""        self.benchmark_data[benchmark_name] = dimension_scores
        logger.debug(f"Added benchmark data: {benchmark_name}")
    
    def get_quality_summary(self, profile: QualityProfile) -> Dict[str, Any]:
        """Get a summary of quality assessment"""        return {
            'overall_score': profile.overall_score,
            'quality_level': profile.quality_level.value,
            'success_rate': profile.success_rate,
            'dimension_scores': profile.dimension_scores,
            'total_issues': len(profile.critical_issues),
            'improvement_potential': profile.improvement_potential,
            'recommendations': profile.improvement_suggestions[:5],  # Top 5 recommendations
            'assessment_time': profile.assessment_time.isoformat(),
            'processing_time_ms': profile.processing_time_ms
        }
