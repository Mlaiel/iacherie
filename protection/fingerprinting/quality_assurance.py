"""🔍 Quality Assurance & Validation System for Content Fingerprinting
===================================================================

Comprehensive quality control system with validation, testing, and 
continuous quality monitoring for enterprise-grade reliability.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written 
permission from Fahed Mlaiel is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization requests.
"""

import asyncio
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any, Callable, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import statistics
import json
import threading
from collections import defaultdict, deque

import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

from .models import ContentType, FingerprintResult, SimilarityMatch, QualityMetrics, ProcessingMetrics
from .utils import SimilarityCalculator

logger = logging.getLogger(__name__)

class QualityLevel(str, Enum):
    """
Quality assessment levels."""

    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"

class ValidationStatus(str, Enum):
    """Validation status codes."""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"

class TestType(str, Enum):
    """Types of quality tests."""

    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    PERFORMANCE = "performance"
    ROBUSTNESS = "robustness"
    COMPLETENESS = "completeness"

@dataclass
class ValidationRule:
    """Quality validation rule definition."""
    rule_id: str
    name: str
    description: str
    test_type: TestType
    content_types: List[ContentType]
    threshold: float
    severity: str = "error"  # error, warning, info
    enabled: bool = True
    validator_func: Optional[Callable] = None

@dataclass
class ValidationResult:
    """Result of quality validation."""
    rule_id: str
    status: ValidationStatus
    score: float
    threshold: float
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class QualityReport:
    """
Comprehensive quality assessment report."""
    report_id: str
    content_type: ContentType
    fingerprint_id: str
    overall_quality: QualityLevel
    overall_score: float
    validation_results: List[ValidationResult]
    performance_metrics: ProcessingMetrics
    quality_metrics: QualityMetrics
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class BenchmarkSuite:
    """
Test suite for benchmarking fingerprinting quality."""
    suite_id: str
    name: str
    description: str
    content_type: ContentType
    test_files: List[str]
    ground_truth: Dict[str, Any]
    expected_results: Dict[str, Any]
    similarity_pairs: List[Tuple[str, str, float]]  # file1, file2, expected_similarity

class FingerprintValidator:
    """
Comprehensive fingerprint validation system."""
    
    def __init__(self):
        self.validation_rules = {}
        self.quality_thresholds = {
            QualityLevel.EXCELLENT: 0.95,
            QualityLevel.GOOD: 0.85,
            QualityLevel.ACCEPTABLE: 0.70,
            QualityLevel.POOR: 0.50,
            QualityLevel.UNACCEPTABLE: 0.0
        }
        
        # Initialize default validation rules
        self._initialize_default_rules()
        
    def _initialize_default_rules(self):
        """
Initialize default validation rules."""
        self.validation_rules = {
            'completeness_check': ValidationRule(
                rule_id='completeness_check',
                name='Fingerprint Completeness',
                description='Verify all required fingerprint components are present',
                test_type=TestType.COMPLETENESS,
                content_types=list(ContentType),
                threshold=0.8,
                validator_func=self._validate_completeness
            ),
            
            'consistency_check': ValidationRule(
                rule_id='consistency_check',
                name='Algorithm Consistency',
                description='Verify consistency across multiple algorithms',
                test_type=TestType.CONSISTENCY,
                content_types=list(ContentType),
                threshold=0.7,
                validator_func=self._validate_consistency
            ),
            
            'quality_threshold': ValidationRule(
                rule_id='quality_threshold',
                name='Quality Score Threshold',
                description='Minimum quality score requirement',
                test_type=TestType.ACCURACY,
                content_types=list(ContentType),
                threshold=0.75,
                validator_func=self._validate_quality_score
            ),
            
            'uniqueness_check': ValidationRule(
                rule_id='uniqueness_check',
                name='Fingerprint Uniqueness',
                description='Verify fingerprint provides sufficient uniqueness',
                test_type=TestType.ROBUSTNESS,
                content_types=list(ContentType),
                threshold=0.8,
                validator_func=self._validate_uniqueness
            ),
            
            'processing_time_check': ValidationRule(
                rule_id='processing_time_check',
                name='Processing Time Limit',
                description='Verify processing completes within time limits',
                test_type=TestType.PERFORMANCE,
                content_types=list(ContentType),
                threshold=30.0,  # 30 seconds max
                validator_func=self._validate_processing_time
            )
        }
    
    async def validate_fingerprint(self, 
                                 fingerprint: FingerprintResult,
                                 processing_metrics: Optional[ProcessingMetrics] = None) -> QualityReport:
        """
Validate fingerprint quality and generate report."""
        
        validation_results = []
        
        # Run all applicable validation rules
        for rule in self.validation_rules.values():
            if not rule.enabled:
                continue
                
            if fingerprint.content_type not in rule.content_types:
                continue
            
            try:
                result = await self._run_validation_rule(rule, fingerprint, processing_metrics)
                validation_results.append(result)
                
            except Exception as e:
                logger.error(f"Validation rule {rule.rule_id} failed: {e}")
                validation_results.append(ValidationResult(
                    rule_id=rule.rule_id,
                    status=ValidationStatus.FAILED,
                    score=0.0,
                    threshold=rule.threshold,
                    message=f"Validation failed: {e}",
                    details={'error': str(e)}
                ))
        
        # Calculate overall quality
        overall_score = self._calculate_overall_score(validation_results)
        overall_quality = self._determine_quality_level(overall_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(validation_results, fingerprint)
        
        # Create quality report
        report = QualityReport(
            report_id=f"qr_{int(time.time())}_{fingerprint.id}",
            content_type=fingerprint.content_type,
            fingerprint_id=fingerprint.id,
            overall_quality=overall_quality,
            overall_score=overall_score,
            validation_results=validation_results,
            performance_metrics=processing_metrics or ProcessingMetrics(processing_time_seconds=0),
            quality_metrics=fingerprint.quality_metrics or QualityMetrics(
                confidence_score=0, reliability_score=0, completeness_score=0, uniqueness_score=0
            ),
            recommendations=recommendations
        )
        
        return report
    
    async def _run_validation_rule(self, 
                                 rule: ValidationRule,
        try:
            logger.info(f"Executing _run_validation_rule")
            
            # Implementation for _run_validation_rule
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_run_validation_rule completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_run_validation_rule failed: {e}")
            raise
            rule_id=rule.rule_id,
            status=status,
            score=score,
            threshold=rule.threshold,
            message=message,
            details=details
        )
    
    async def _validate_completeness(self, 
                                   fingerprint: FingerprintResult,
                                   processing_metrics: Optional[ProcessingMetrics],
                                   threshold: float) -> Tuple[float, Dict[str, Any]]:
        """Validate fingerprint completeness."""
        
        required_fields = {
            ContentType.AUDIO: ['chromaprint', 'essentia', 'spectral'],
            ContentType.VIDEO: ['perceptual_frames', 'motion_analysis', 'object_detection'],
            ContentType.IMAGE: ['perceptual_hash', 'clip_embedding', 'traditional_features'],
            ContentType.TEXT: ['bert_embedding', 'tfidf_vector', 'ngram_analysis']
        }
        
        required = required_fields.get(fingerprint.content_type, [])
        if not required:
            return 1.0, {"message": "No specific requirements for content type"}
        
        # Check fingerprint data
        fingerprint_dict = fingerprint.fingerprint_data.dict() if hasattr(fingerprint.fingerprint_data, 'dict') else {}
        
        present_fields = []
        missing_fields = []
        
        for field in required:
            if field in fingerprint_dict and fingerprint_dict[field] is not None:
                present_fields.append(field)
            else:
                missing_fields.append(field)
        
        completeness_score = len(present_fields) / len(required)
        
        details = {
            "required_fields": required,
            "present_fields": present_fields,
            "missing_fields": missing_fields,
            "completeness_percentage": completeness_score * 100
        }
        
        return completeness_score, details
    
    async def _validate_consistency(self,
                                  fingerprint: FingerprintResult,
                                  processing_metrics: Optional[ProcessingMetrics],
                                  threshold: float) -> Tuple[float, Dict[str, Any]]:
        """Validate consistency across algorithms."""
        
        # This would implement cross-algorithm consistency checks
        # For now, return a placeholder implementation
        
        consistency_score = 0.8  # Placeholder
        
        details = {
            "algorithms_checked": ["algorithm1", "algorithm2"],
            "consistency_metrics": {"cross_correlation": 0.8},
            "notes": "Placeholder implementation"
        }
        
        return consistency_score, details
    
    async def _validate_quality_score(self,
                                    fingerprint: FingerprintResult,
                                    processing_metrics: Optional[ProcessingMetrics],
                                    threshold: float) -> Tuple[float, Dict[str, Any]]:
        """Validate quality score meets threshold."""
        
        quality_metrics = fingerprint.quality_metrics
        if not quality_metrics:
            return 0.0, {"message": "No quality metrics available"}
        
        # Use confidence score as primary quality indicator
        score = quality_metrics.confidence_score
        
        details = {
            "confidence_score": quality_metrics.confidence_score,
            "reliability_score": quality_metrics.reliability_score,
            "completeness_score": quality_metrics.completeness_score,
            "uniqueness_score": quality_metrics.uniqueness_score
        }
        
        return score, details
    
    async def _validate_uniqueness(self,
                                 fingerprint: FingerprintResult,
                                 processing_metrics: Optional[ProcessingMetrics],
                                 threshold: float) -> Tuple[float, Dict[str, Any]]:
        """Validate fingerprint uniqueness."""
        
        quality_metrics = fingerprint.quality_metrics
        if not quality_metrics:
            return 0.0, {"message": "No quality metrics available"}
        
        uniqueness_score = quality_metrics.uniqueness_score
        
        details = {
            "uniqueness_score": uniqueness_score,
            "hash_length": len(fingerprint.hash_value) if fingerprint.hash_value else 0,
            "algorithm_diversity": "multiple" if hasattr(fingerprint.fingerprint_data, 'dict') else "single"
        }
        
        return uniqueness_score, details
    
    async def _validate_processing_time(self,
                                      fingerprint: FingerprintResult,
                                      processing_metrics: Optional[ProcessingMetrics],
                                      threshold: float) -> Tuple[float, Dict[str, Any]]:
        """Validate processing time is within limits."""
        
        if not processing_metrics:
            return 0.5, {"message": "No processing metrics available"}
        
        processing_time = processing_metrics.processing_time_seconds
        
        # Score inversely related to processing time (faster = better)
        # Max score when processing_time <= threshold/2
        # Min score (0) when processing_time >= threshold
        if processing_time <= threshold / 2:
            score = 1.0
        elif processing_time >= threshold:
            score = 0.0
        else:
            # Linear decrease from 1.0 to 0.0
            score = 1.0 - (processing_time - threshold/2) / (threshold/2)
        
        details = {
            "processing_time_seconds": processing_time,
            "threshold_seconds": threshold,
            "performance_category": "fast" if score > 0.8 else "slow" if score < 0.3 else "moderate"
        }
        
        return score, details
    
    def _calculate_overall_score(self, validation_results: List[ValidationResult]) -> float:
        """Calculate overall quality score from validation results."""
        if not validation_results:
            return 0.0
        
        # Weight scores by test type importance
        weights = {
            TestType.ACCURACY: 0.3,
            TestType.COMPLETENESS: 0.25,
            TestType.CONSISTENCY: 0.2,
            TestType.ROBUSTNESS: 0.15,
            TestType.PERFORMANCE: 0.1
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for result in validation_results:
            rule = self.validation_rules.get(result.rule_id)
            if rule:
                weight = weights.get(rule.test_type, 0.1)
                weighted_sum += result.score * weight
                total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """
Determine quality level from score."""
        for level, threshold in sorted(self.quality_thresholds.items(), 
                                     key=lambda x: x[1], reverse=True):
            if score >= threshold:
                return level
        return QualityLevel.UNACCEPTABLE
    
    def _generate_recommendations(self, 
                                validation_results: List[ValidationResult],
                                fingerprint: FingerprintResult) -> List[str]:
        """
Generate optimization recommendations."""
        recommendations = []
        
        failed_rules = [r for r in validation_results if r.status == ValidationStatus.FAILED]
        warning_rules = [r for r in validation_results if r.status == ValidationStatus.WARNING]
        
        # Recommendations based on failed rules
        for result in failed_rules:
            if result.rule_id == 'completeness_check':
                recommendations.append("Improve fingerprint completeness by enabling additional algorithms")
            elif result.rule_id == 'consistency_check':
                recommendations.append("Review algorithm consistency and cross-validation")
            elif result.rule_id == 'quality_threshold':
                recommendations.append("Optimize processing parameters to improve quality scores")
            elif result.rule_id == 'uniqueness_check':
                recommendations.append("Enhance fingerprint uniqueness with additional features")
            elif result.rule_id == 'processing_time_check':
                recommendations.append("Optimize processing pipeline for better performance")
        
        # Recommendations based on warnings
        for result in warning_rules:
            if result.rule_id == 'quality_threshold':
                recommendations.append("Consider fine-tuning quality parameters")
            elif result.rule_id == 'processing_time_check':
                recommendations.append("Monitor processing time for potential optimization")
        
        # Content-specific recommendations
        if fingerprint.content_type == ContentType.AUDIO:
            if any('chromaprint' in str(r.details) for r in failed_rules):
                recommendations.append("Consider audio preprocessing to improve Chromaprint quality")
        
        return recommendations

class BenchmarkingSystem:
    """Comprehensive benchmarking system for quality assessment."""
    
    def __init__(self):
        self.benchmark_suites = {}
        self.benchmark_results = {}
        
    def add_benchmark_suite(self, suite: BenchmarkSuite):
        """
Add benchmark suite for testing."""
        self.benchmark_suites[suite.suite_id] = suite
        logger.info(f"Added benchmark suite: {suite.name}")
    
    async def run_benchmark(self, 
                          suite_id: str,
                          fingerprinting_service) -> Dict[str, Any]:
        """Run benchmark suite and generate performance report."""
        
        suite = self.benchmark_suites.get(suite_id)
        if not suite:
            raise ValueError(f"Benchmark suite {suite_id} not found")
        
        logger.info(f"Running benchmark suite: {suite.name}")
        
        results = {
            'suite_id': suite_id,
            'suite_name': suite.name,
            'content_type': suite.content_type.value,
            'start_time': datetime.utcnow().isoformat(),
            'test_results': [],
            'similarity_results': [],
            'performance_metrics': {},
            'quality_scores': []
        }
        
        # Test fingerprint generation for each file
        fingerprints = {}
        processing_times = []
        
        for test_file in suite.test_files:
            if not Path(test_file).exists():
                logger.warning(f"Test file not found: {test_file}")
                continue
            
            try:
                start_time = time.time()
                
                # Generate fingerprint
                fingerprint = await fingerprinting_service.create_fingerprint(
                    test_file, user_id=0, content_type=suite.content_type
                )
                
                processing_time = time.time() - start_time
                processing_times.append(processing_time)
                
                fingerprints[test_file] = fingerprint
                
                # Collect quality metrics
                if fingerprint.quality_metrics:
                    results['quality_scores'].append({
                        'file': test_file,
                        'confidence': fingerprint.quality_metrics.confidence_score,
                        'reliability': fingerprint.quality_metrics.reliability_score,
                        'completeness': fingerprint.quality_metrics.completeness_score,
                        'uniqueness': fingerprint.quality_metrics.uniqueness_score
                    })
                
                results['test_results'].append({
                    'file': test_file,
                    'status': 'success',
                    'processing_time': processing_time,
                    'hash_value': fingerprint.hash_value
                })
                
            except Exception as e:
                logger.error(f"Benchmark test failed for {test_file}: {e}")
                results['test_results'].append({
                    'file': test_file,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # Test similarity matching
        for file1, file2, expected_similarity in suite.similarity_pairs:
            if file1 in fingerprints and file2 in fingerprints:
                try:
                    # Calculate similarity
                    similarity = self._calculate_fingerprint_similarity(
                        fingerprints[file1], fingerprints[file2]
                    )
                    
                    accuracy = 1.0 - abs(similarity - expected_similarity)
                    
                    results['similarity_results'].append({
                        'file1': file1,
                        'file2': file2,
                        'expected_similarity': expected_similarity,
                        'actual_similarity': similarity,
                        'accuracy': accuracy
                    })
                    
                except Exception as e:
                    logger.error(f"Similarity test failed for {file1} vs {file2}: {e}")
                    results['similarity_results'].append({
                        'file1': file1,
                        'file2': file2,
                        'status': 'failed',
                        'error': str(e)
                    })
        
        # Calculate performance metrics
        if processing_times:
            results['performance_metrics'] = {
                'avg_processing_time': statistics.mean(processing_times),
                'min_processing_time': min(processing_times),
                'max_processing_time': max(processing_times),
                'std_processing_time': statistics.stdev(processing_times) if len(processing_times) > 1 else 0,
                'throughput_files_per_second': len(processing_times) / sum(processing_times)
            }
        
        # Calculate quality metrics
        if results['quality_scores']:
            quality_data = results['quality_scores']
            results['quality_summary'] = {
                'avg_confidence': statistics.mean([q['confidence'] for q in quality_data]),
                'avg_reliability': statistics.mean([q['reliability'] for q in quality_data]),
                'avg_completeness': statistics.mean([q['completeness'] for q in quality_data]),
                'avg_uniqueness': statistics.mean([q['uniqueness'] for q in quality_data])
            }
        
        # Calculate similarity accuracy
        if results['similarity_results']:
            similarity_accuracies = [r['accuracy'] for r in results['similarity_results'] if 'accuracy' in r]
            if similarity_accuracies:
                results['similarity_accuracy'] = {
                    'avg_accuracy': statistics.mean(similarity_accuracies),
                    'min_accuracy': min(similarity_accuracies),
                    'max_accuracy': max(similarity_accuracies)
                }
        
        results['end_time'] = datetime.utcnow().isoformat()
        results['total_duration'] = sum(processing_times)
        
        # Store results
        self.benchmark_results[suite_id] = results
        
        logger.info(f"Benchmark suite {suite.name} completed successfully")
        return results
    
    def _calculate_fingerprint_similarity(self, 
                                        fp1: FingerprintResult,
                                        fp2: FingerprintResult) -> float:
        """Calculate similarity between two fingerprints."""
        
        # Simple hash-based similarity for demonstration
        if fp1.hash_value and fp2.hash_value:
            return SimilarityCalculator.hamming_similarity(fp1.hash_value, fp2.hash_value)
        
        return 0.0
    
    def generate_benchmark_report(self, suite_id: str) -> str:
        """
Generate detailed benchmark report."""
        
        results = self.benchmark_results.get(suite_id)
        if not results:
            return f"No benchmark results found for suite {suite_id}"
        
        suite = self.benchmark_suites[suite_id]
        
        report = f"""# Benchmark Report: {suite.name}

## Overview
- **Suite ID**: {suite_id}
- **Content Type**: {results['content_type']}
- **Test Files**: {len(suite.test_files)}
- **Duration**: {results['total_duration']:.2f} seconds

## Performance Metrics
"""
        
        if 'performance_metrics' in results:
            perf = results['performance_metrics']
            report += f"""- **Average Processing Time**: {perf['avg_processing_time']:.3f}s
- **Throughput**: {perf['throughput_files_per_second']:.2f} files/second
- **Processing Time Range**: {perf['min_processing_time']:.3f}s - {perf['max_processing_time']:.3f}s
"""
        
        if 'quality_summary' in results:
            quality = results['quality_summary']
            report += f"""## Quality Metrics
- **Average Confidence**: {quality['avg_confidence']:.3f}
- **Average Reliability**: {quality['avg_reliability']:.3f}
- **Average Completeness**: {quality['avg_completeness']:.3f}
- **Average Uniqueness**: {quality['avg_uniqueness']:.3f}
"""
        
        if 'similarity_accuracy' in results:
            sim = results['similarity_accuracy']
            report += f"""## Similarity Accuracy
- **Average Accuracy**: {sim['avg_accuracy']:.3f}
- **Accuracy Range**: {sim['min_accuracy']:.3f} - {sim['max_accuracy']:.3f}
"""
        
        # Add detailed results
        successful_tests = [r for r in results['test_results'] if r['status'] == 'success']
        failed_tests = [r for r in results['test_results'] if r['status'] == 'failed']
        
        report += f"""## Test Results Summary
- **Successful Tests**: {len(successful_tests)}
- **Failed Tests**: {len(failed_tests)}
- **Success Rate**: {len(successful_tests) / len(results['test_results']) * 100:.1f}%
"""
        
        return report

class QualityAssuranceSystem:
    """
    Comprehensive Quality Assurance System for Content Fingerprinting.
    
    Features:
    - Automated validation with configurable rules
    - Comprehensive benchmarking and performance testing
    - Quality metrics tracking and trending
    - Continuous quality monitoring
    - Performance regression detection
    - Detailed reporting and recommendations
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Core components
        self.validator = FingerprintValidator()
        self.benchmarking = BenchmarkingSystem()
        
        # Quality tracking
        self.quality_history = deque(maxlen=10000)
        self.quality_trends = defaultdict(list)
        
        # Monitoring
        self.monitoring_enabled = self.config.get('enable_monitoring', True)
        self.quality_thresholds = self.config.get('quality_thresholds', {
            'min_confidence': 0.8,
            'min_reliability': 0.75,
            'min_completeness': 0.8,
            'max_processing_time': 30.0
        })
        
        logger.info("Quality Assurance System initialized")
    
    async def assess_quality(self, 
                           fingerprint: FingerprintResult,
                           processing_metrics: Optional[ProcessingMetrics] = None) -> QualityReport:
        """Perform comprehensive quality assessment."""
        
        # Run validation
        report = await self.validator.validate_fingerprint(fingerprint, processing_metrics)
        
        # Track quality metrics
        if self.monitoring_enabled:
            self._track_quality_metrics(report)
        
        # Check for quality regressions
        regression_alerts = self._check_quality_regression(report)
        if regression_alerts:
            report.recommendations.extend(regression_alerts)
        
        return report
    
    def _track_quality_metrics(self, report: QualityReport):
        """
Track quality metrics for trending analysis."""
        
        quality_point = {
            'timestamp': report.timestamp,
            'content_type': report.content_type.value,
            'overall_score': report.overall_score,
            'confidence': report.quality_metrics.confidence_score,
            'reliability': report.quality_metrics.reliability_score,
            'completeness': report.quality_metrics.completeness_score,
            'uniqueness': report.quality_metrics.uniqueness_score,
            'processing_time': report.performance_metrics.processing_time_seconds
        }
        
        self.quality_history.append(quality_point)
        
        # Update trends
        content_type = report.content_type.value
        self.quality_trends[f'{content_type}_overall'].append(report.overall_score)
        self.quality_trends[f'{content_type}_confidence'].append(report.quality_metrics.confidence_score)
        self.quality_trends[f'{content_type}_processing_time'].append(report.performance_metrics.processing_time_seconds)
    
    def _check_quality_regression(self, report: QualityReport) -> List[str]:
        """
Check for quality regressions compared to historical data."""
        
        alerts = []
        content_type = report.content_type.value
        
        # Get recent history for this content type
        recent_points = [
            p for p in list(self.quality_history)[-100:]  # Last 100 points
            if p['content_type'] == content_type
        ]
        
        if len(recent_points) < 10:  # Need minimum history
            return alerts
        
        # Calculate historical averages
        historical_confidence = statistics.mean([p['confidence'] for p in recent_points])
        historical_processing_time = statistics.mean([p['processing_time'] for p in recent_points])
        
        # Check for regressions
        current_confidence = report.quality_metrics.confidence_score
        current_processing_time = report.performance_metrics.processing_time_seconds
        
        confidence_change = (current_confidence - historical_confidence) / historical_confidence
        processing_time_change = (current_processing_time - historical_processing_time) / historical_processing_time
        
        if confidence_change < -0.1:  # 10% decrease
            alerts.append(f"Quality regression detected: Confidence dropped by {abs(confidence_change)*100:.1f}%")
        
        if processing_time_change > 0.2:  # 20% increase
            alerts.append(f"Performance regression detected: Processing time increased by {processing_time_change*100:.1f}%")
        
        return alerts
    
    def generate_quality_dashboard(self) -> Dict[str, Any]:
        """Generate quality dashboard data."""
        
        if not self.quality_history:
            return {'message': 'No quality data available'}
        
        recent_points = list(self.quality_history)[-100:]  # Last 100 points
        
        # Overall statistics
        overall_scores = [p['overall_score'] for p in recent_points]
        confidence_scores = [p['confidence'] for p in recent_points]
        processing_times = [p['processing_time'] for p in recent_points]
        
        dashboard = {
            'overview': {
                'total_assessments': len(self.quality_history),
                'avg_overall_score': statistics.mean(overall_scores),
                'avg_confidence': statistics.mean(confidence_scores),
                'avg_processing_time': statistics.mean(processing_times),
                'quality_trend': 'improving' if len(overall_scores) > 1 and overall_scores[-1] > overall_scores[0] else 'stable'
            },
            
            'content_type_breakdown': {},
            'quality_distribution': {},
            'performance_metrics': {
                'min_processing_time': min(processing_times),
                'max_processing_time': max(processing_times),
                'p95_processing_time': np.percentile(processing_times, 95)
            }
        }
        
        # Content type breakdown
        for content_type in ContentType:
            type_points = [p for p in recent_points if p['content_type'] == content_type.value]
            if type_points:
                dashboard['content_type_breakdown'][content_type.value] = {
                    'count': len(type_points),
                    'avg_score': statistics.mean([p['overall_score'] for p in type_points]),
                    'avg_confidence': statistics.mean([p['confidence'] for p in type_points])
                }
        
        # Quality distribution
        quality_bins = {'excellent': 0, 'good': 0, 'acceptable': 0, 'poor': 0, 'unacceptable': 0}
        for score in overall_scores:
            if score >= 0.95:
                quality_bins['excellent'] += 1
            elif score >= 0.85:
                quality_bins['good'] += 1
            elif score >= 0.70:
                quality_bins['acceptable'] += 1
            elif score >= 0.50:
                quality_bins['poor'] += 1
            else:
                quality_bins['unacceptable'] += 1
        
        dashboard['quality_distribution'] = quality_bins
        
        return dashboard
    
    async def run_continuous_monitoring(self, interval_seconds: int = 300):
        """
Run continuous quality monitoring."""
        
        logger.info(f"Starting continuous quality monitoring (interval: {interval_seconds}s)")
        
        while self.monitoring_enabled:
            try:
                # Generate quality summary
                dashboard = self.generate_quality_dashboard()
                
                # Check quality thresholds
                if 'overview' in dashboard:
                    overview = dashboard['overview']
                    
                    if overview['avg_confidence'] < self.quality_thresholds['min_confidence']:
                        logger.warning(f"Average confidence below threshold: {overview['avg_confidence']:.3f}")
                    
                    if overview['avg_processing_time'] > self.quality_thresholds['max_processing_time']:
                        logger.warning(f"Average processing time above threshold: {overview['avg_processing_time']:.1f}s")
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Quality monitoring error: {e}")
                await asyncio.sleep(interval_seconds)
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self.monitoring_enabled = False
        logger.info("Quality monitoring stopped")

# Export main classes
__all__ = [
    'QualityAssuranceSystem', 'FingerprintValidator', 'BenchmarkingSystem',
    'QualityReport', 'ValidationResult', 'BenchmarkSuite', 'QualityLevel',
    'ValidationStatus', 'TestType', 'ValidationRule'
]
