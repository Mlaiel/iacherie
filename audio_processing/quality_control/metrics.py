"""🎯 Quality Metrics - Professional Quality Measurement System

Comprehensive quality metrics system for detailed audio quality measurement,
scoring, and reporting. Provides structured quality data and analysis.

Created by: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Developer + DevOps + DBA + Security + Microservices
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT STRICT ⚠️
Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification, distribution ou reproduction sans 
autorisation écrite explicite de Fahed Mlaiel (mlaiel@live.de) est strictement 
interdite et passible de poursuites judiciaires selon la loi allemande et internationale.
"""

import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import numpy as np
import statistics

logger = logging.getLogger(__name__)


class MetricCategory(Enum):
    """
Quality metric categories"""

    TECHNICAL = "technical"
    PERCEPTUAL = "perceptual"
    CONTENT = "content"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"


class ScoreType(Enum):
    """Quality score types"""

    NORMALIZED = "normalized"      # 0.0 to 1.0
    PERCENTAGE = "percentage"      # 0 to 100
    DB_SCALE = "db_scale"         # dB values
    RATING = "rating"             # 1 to 5 stars
    PASS_FAIL = "pass_fail"       # Boolean


class QualityGrade(Enum):
    """Quality grade classifications"""

    EXCELLENT = "excellent"       # 90-100%
    VERY_GOOD = "very_good"      # 80-89%
    GOOD = "good"                # 70-79%
    ACCEPTABLE = "acceptable"    # 60-69%
    POOR = "poor"                # 40-59%
    UNACCEPTABLE = "unacceptable" # 0-39%


@dataclass
class QualityScore:
    """Individual quality score measurement"""
    name: str
    category: MetricCategory
    value: float
    score_type: ScoreType
    max_value: float = 1.0
    min_value: float = 0.0
    threshold: Optional[float] = None
    passed: bool = True
    weight: float = 1.0
    description: str = ""
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass 
class QualityMetrics:
    """Comprehensive quality metrics collection"""
    
    # Overall scores
    overall_score: float = 0.0
    overall_grade: QualityGrade = QualityGrade.UNACCEPTABLE
    
    # Category scores
    technical_score: float = 0.0
    perceptual_score: float = 0.0
    content_score: float = 0.0
    compliance_score: float = 0.0
    performance_score: float = 0.0
    
    # Individual metrics
    scores: List[QualityScore] = field(default_factory=list)
    
    # Statistical data
    score_distribution: Dict[QualityGrade, int] = field(default_factory=dict)
    confidence_level: float = 0.0
    reliability_index: float = 0.0
    
    # Processing metadata
    processing_time: float = 0.0
    samples_analyzed: int = 0
    errors_encountered: int = 0
    warnings_generated: int = 0
    
    # Timestamps
    timestamp: datetime = field(default_factory=datetime.now)
    analysis_duration: float = 0.0
    
    def add_score(self, score: QualityScore):
        """
Add individual quality score"""
        self.scores.append(score)
    
    def get_scores_by_category(self, category: MetricCategory) -> List[QualityScore]:
        """
Get scores filtered by category"""
        return [score for score in self.scores if score.category == category]
    
    def calculate_category_score(self, category: MetricCategory) -> float:
        """
Calculate weighted average score for category"""
        category_scores = self.get_scores_by_category(category)
        if not category_scores:
            return 0.0
        
        total_weighted = sum(score.value * score.weight for score in category_scores)
        total_weights = sum(score.weight for score in category_scores)
        
        return total_weighted / max(total_weights, 1.0)
    
    def update_category_scores(self):
        """
Update all category scores"""
        self.technical_score = self.calculate_category_score(MetricCategory.TECHNICAL)
        self.perceptual_score = self.calculate_category_score(MetricCategory.PERCEPTUAL)
        self.content_score = self.calculate_category_score(MetricCategory.CONTENT)
        self.compliance_score = self.calculate_category_score(MetricCategory.COMPLIANCE)
        self.performance_score = self.calculate_category_score(MetricCategory.PERFORMANCE)
    
    def calculate_overall_score(self, weights: Dict[MetricCategory, float] = None) -> float:
        """
Calculate weighted overall score"""
        if weights is None:
            weights = {
                MetricCategory.TECHNICAL: 0.35,
                MetricCategory.PERCEPTUAL: 0.30,
                MetricCategory.CONTENT: 0.20,
                MetricCategory.COMPLIANCE: 0.15,
                MetricCategory.PERFORMANCE: 0.0  # Usually not included in quality score
            }
        
        self.update_category_scores()
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        category_scores = {
            MetricCategory.TECHNICAL: self.technical_score,
            MetricCategory.PERCEPTUAL: self.perceptual_score,
            MetricCategory.CONTENT: self.content_score,
            MetricCategory.COMPLIANCE: self.compliance_score,
            MetricCategory.PERFORMANCE: self.performance_score
        }
        
        for category, weight in weights.items():
            if weight > 0 and category in category_scores:
                weighted_sum += category_scores[category] * weight
                total_weight += weight
        
        self.overall_score = weighted_sum / max(total_weight, 1.0)
        self.overall_grade = self.score_to_grade(self.overall_score)
        
        return self.overall_score
    
    @staticmethod
    def score_to_grade(score: float) -> QualityGrade:
        """
Convert numeric score to quality grade"""
        if score >= 0.90:
            return QualityGrade.EXCELLENT
        elif score >= 0.80:
            return QualityGrade.VERY_GOOD
        elif score >= 0.70:
            return QualityGrade.GOOD
        elif score >= 0.60:
            return QualityGrade.ACCEPTABLE
        elif score >= 0.40:
            return QualityGrade.POOR
        else:
            return QualityGrade.UNACCEPTABLE
    
    def get_failed_metrics(self) -> List[QualityScore]:
        """
Get metrics that failed their thresholds"""
        return [score for score in self.scores if not score.passed]
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
Get summary statistics"""
        if not self.scores:
            return {}
        
        values = [score.value for score in self.scores]
        
        return {
            'total_metrics': len(self.scores),
            'passed_metrics': len([s for s in self.scores if s.passed]),
            'failed_metrics': len([s for s in self.scores if not s.passed]),
            'average_score': statistics.mean(values),
            'median_score': statistics.median(values),
            'std_deviation': statistics.stdev(values) if len(values) > 1 else 0.0,
            'min_score': min(values),
            'max_score': max(values),
            'score_range': max(values) - min(values)
        }


@dataclass
class QualityReport:
    """
Complete quality assessment report"""
    
    # Core metrics
    metrics: QualityMetrics
    
    # Validation results (from validator)
    validation_results: List[Any] = field(default_factory=list)
    
    # Analysis results
    overall_score: float = 0.0
    overall_grade: QualityGrade = QualityGrade.UNACCEPTABLE
    confidence: float = 0.0
    
    # Recommendations and insights
    recommendations: List[str] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Technical details
    audio_properties: Dict[str, Any] = field(default_factory=dict)
    processing_details: Dict[str, Any] = field(default_factory=dict)
    
    # Report metadata
    report_id: str = ""
    profile_name: str = ""
    validation_level: str = ""
    processing_time: float = 0.0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    analysis_start: Optional[datetime] = None
    analysis_end: Optional[datetime] = None
    
    def generate_summary(self) -> str:
        """Generate human-readable report summary"""
        summary_parts = []
        
        # Overall assessment
        summary_parts.append(f"Overall Quality: {self.overall_grade.value.title()} ({self.overall_score:.1%})")
        
        if self.confidence > 0:
            summary_parts.append(f"Confidence: {self.confidence:.1%}")
        
        # Category breakdown
        if self.metrics.technical_score > 0:
            summary_parts.append(f"Technical: {self.metrics.technical_score:.1%}")
        if self.metrics.perceptual_score > 0:
            summary_parts.append(f"Perceptual: {self.metrics.perceptual_score:.1%}")
        if self.metrics.content_score > 0:
            summary_parts.append(f"Content: {self.metrics.content_score:.1%}")
        if self.metrics.compliance_score > 0:
            summary_parts.append(f"Compliance: {self.metrics.compliance_score:.1%}")
        
        # Issues summary
        failed_metrics = self.metrics.get_failed_metrics()
        if failed_metrics:
            summary_parts.append(f"Failed Checks: {len(failed_metrics)}")
        
        if self.critical_issues:
            summary_parts.append(f"Critical Issues: {len(self.critical_issues)}")
        
        if self.warnings:
            summary_parts.append(f"Warnings: {len(self.warnings)}")
        
        return " | ".join(summary_parts)
    
    def get_detailed_analysis(self) -> Dict[str, Any]:
        """Get detailed analysis breakdown"""
        return {
            'overall_assessment': {
                'score': self.overall_score,
                'grade': self.overall_grade.value,
                'confidence': self.confidence,
                'summary': self.generate_summary()
            },
            'category_scores': {
                'technical': self.metrics.technical_score,
                'perceptual': self.metrics.perceptual_score,
                'content': self.metrics.content_score,
                'compliance': self.metrics.compliance_score,
                'performance': self.metrics.performance_score
            },
            'metric_details': [
                {
                    'name': score.name,
                    'category': score.category.value,
                    'value': score.value,
                    'passed': score.passed,
                    'threshold': score.threshold,
                    'description': score.description,
                    'unit': score.unit
                }
                for score in self.metrics.scores
            ],
            'validation_summary': {
                'total_validations': len(self.validation_results),
                'passed_validations': len([r for r in self.validation_results if getattr(r, 'passed', True)]),
                'failed_validations': len([r for r in self.validation_results if not getattr(r, 'passed', True)])
            },
            'issues_and_recommendations': {
                'critical_issues': self.critical_issues,
                'warnings': self.warnings,
                'recommendations': self.recommendations
            },
            'processing_info': {
                'processing_time': self.processing_time,
                'profile_used': self.profile_name,
                'validation_level': self.validation_level,
                'created_at': self.created_at.isoformat()
            }
        }
    
    def export_json(self, file_path: Optional[str] = None) -> str:
        """
Export report as JSON"""
        export_data = {
            'report_id': self.report_id,
            'created_at': self.created_at.isoformat(),
            'overall_assessment': {
                'score': self.overall_score,
                'grade': self.overall_grade.value,
                'confidence': self.confidence
            },
            'metrics': {
                'overall_score': self.metrics.overall_score,
                'category_scores': {
                    'technical': self.metrics.technical_score,
                    'perceptual': self.metrics.perceptual_score,
                    'content': self.metrics.content_score,
                    'compliance': self.metrics.compliance_score,
                    'performance': self.metrics.performance_score
                },
                'individual_scores': [
                    {
                        'name': score.name,
                        'category': score.category.value,
                        'value': score.value,
                        'score_type': score.score_type.value,
                        'passed': score.passed,
                        'threshold': score.threshold,
                        'weight': score.weight,
                        'description': score.description,
                        'unit': score.unit
                    }
                    for score in self.metrics.scores
                ],
                'summary_statistics': self.metrics.get_summary_stats()
            },
            'validation_results': [
                {
                    'test_name': getattr(result, 'test_name', 'unknown'),
                    'category': getattr(result, 'category', 'unknown'),
                    'passed': getattr(result, 'passed', True),
                    'score': getattr(result, 'score', 0.0),
                    'message': getattr(result, 'message', ''),
                    'severity': getattr(result, 'severity', 'info')
                }
                for result in self.validation_results
            ],
            'recommendations': self.recommendations,
            'critical_issues': self.critical_issues,
            'warnings': self.warnings,
            'audio_properties': self.audio_properties,
            'processing_details': {
                'processing_time': self.processing_time,
                'profile_name': self.profile_name,
                'validation_level': self.validation_level,
                'samples_analyzed': self.metrics.samples_analyzed,
                'errors_encountered': self.metrics.errors_encountered,
                'warnings_generated': self.metrics.warnings_generated
            }
        }
        
        json_str = json.dumps(export_data, indent=2, default=str)
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(json_str)
            logger.info(f"Quality report exported to {file_path}")
        
        return json_str
    
    def export_csv(self, file_path: str):
        """Export metrics as CSV"""
        import csv
        
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Metric Name', 'Category', 'Value', 'Score Type', 
                'Passed', 'Threshold', 'Weight', 'Description', 'Unit'
            ])
            
            # Metrics data
            for score in self.metrics.scores:
                writer.writerow([
                    score.name,
                    score.category.value,
                    score.value,
                    score.score_type.value,
                    score.passed,
                    score.threshold or '',
                    score.weight,
                    score.description,
                    score.unit
                ])
        
        logger.info(f"Quality metrics exported to CSV: {file_path}")


class QualityMetricsCalculator:
    """
    🎯 Quality Metrics Calculator
    
    Advanced quality metrics calculation engine:
    - Technical quality metrics
    - Perceptual quality scoring
    - Content analysis metrics
    - Compliance checking
    - Statistical analysis
    """
    
    def __init__(self):
        self.metric_definitions = self._initialize_metric_definitions()
        logger.info("QualityMetricsCalculator initialized")
    
    def _initialize_metric_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize standard metric definitions"""
        return {
            # Technical metrics
            'sample_rate': {
                'category': MetricCategory.TECHNICAL,
                'score_type': ScoreType.NORMALIZED,
                'description': 'Audio sample rate quality',
                'unit': 'Hz',
                'weight': 1.0
            },
            'bit_depth': {
                'category': MetricCategory.TECHNICAL,
                'score_type': ScoreType.NORMALIZED,
                'description': 'Audio bit depth quality',
                'unit': 'bits',
                'weight': 1.0
            },
            'snr': {
                'category': MetricCategory.TECHNICAL,
                'score_type': ScoreType.DB_SCALE,
                'description': 'Signal-to-noise ratio',
                'unit': 'dB',
                'weight': 2.0
            },
            'thd': {
                'category': MetricCategory.TECHNICAL,
                'score_type': ScoreType.PERCENTAGE,
                'description': 'Total harmonic distortion',
                'unit': '%',
                'weight': 1.5
            },
            'dynamic_range': {
                'category': MetricCategory.TECHNICAL,
                'score_type': ScoreType.DB_SCALE,
                'description': 'Dynamic range',
                'unit': 'dB',
                'weight': 1.2
            },
            'clipping_ratio': {
                'category': MetricCategory.TECHNICAL,
                'score_type': ScoreType.PERCENTAGE,
                'description': 'Audio clipping ratio',
                'unit': '%',
                'weight': 3.0  # High weight for critical issue
            },
            
            # Perceptual metrics
            'loudness': {
                'category': MetricCategory.PERCEPTUAL,
                'score_type': ScoreType.DB_SCALE,
                'description': 'Perceived loudness',
                'unit': 'LUFS',
                'weight': 2.0
            },
            'frequency_balance': {
                'category': MetricCategory.PERCEPTUAL,
                'score_type': ScoreType.NORMALIZED,
                'description': 'Frequency balance quality',
                'unit': '',
                'weight': 1.8
            },
            'stereo_imaging': {
                'category': MetricCategory.PERCEPTUAL,
                'score_type': ScoreType.NORMALIZED,
                'description': 'Stereo imaging quality',
                'unit': '',
                'weight': 1.0
            },
            'temporal_consistency': {
                'category': MetricCategory.PERCEPTUAL,
                'score_type': ScoreType.NORMALIZED,
                'description': 'Temporal consistency',
                'unit': '',
                'weight': 1.3
            },
            
            # Content metrics
            'duration': {
                'category': MetricCategory.CONTENT,
                'score_type': ScoreType.NORMALIZED,
                'description': 'Content duration appropriateness',
                'unit': 's',
                'weight': 1.0
            },
            'silence_ratio': {
                'category': MetricCategory.CONTENT,
                'score_type': ScoreType.PERCENTAGE,
                'description': 'Silence ratio in content',
                'unit': '%',
                'weight': 1.2
            },
            'content_type_match': {
                'category': MetricCategory.CONTENT,
                'score_type': ScoreType.NORMALIZED,
                'description': 'Content type matching',
                'unit': '',
                'weight': 1.5
            },
            
            # Compliance metrics
            'format_compliance': {
                'category': MetricCategory.COMPLIANCE,
                'score_type': ScoreType.PASS_FAIL,
                'description': 'Format compliance',
                'unit': '',
                'weight': 2.0
            },
            'platform_requirements': {
                'category': MetricCategory.COMPLIANCE,
                'score_type': ScoreType.NORMALIZED,
                'description': 'Platform requirements compliance',
                'unit': '',
                'weight': 1.8
            },
            
            # Performance metrics
            'processing_time': {
                'category': MetricCategory.PERFORMANCE,
                'score_type': ScoreType.NORMALIZED,
                'description': 'Processing time efficiency',
                'unit': 's',
                'weight': 0.5
            },
            'memory_usage': {
                'category': MetricCategory.PERFORMANCE,
                'score_type': ScoreType.NORMALIZED,
                'description': 'Memory usage efficiency',
                'unit': 'MB',
                'weight': 0.3
            }
        }
    
    def create_quality_score(
        self,
        name: str,
        value: float,
        threshold: Optional[float] = None,
        custom_weight: Optional[float] = None
    ) -> QualityScore:
        """
Create quality score with standard definition"""
        
        definition = self.metric_definitions.get(name, {})
        
        category = definition.get('category', MetricCategory.TECHNICAL)
        score_type = definition.get('score_type', ScoreType.NORMALIZED)
        description = definition.get('description', name)
        unit = definition.get('unit', '')
        weight = custom_weight or definition.get('weight', 1.0)
        
        # Determine if passed based on threshold and score type
        passed = True
        if threshold is not None:
            if score_type in [ScoreType.NORMALIZED, ScoreType.PERCENTAGE]:
                passed = value >= threshold
            elif score_type == ScoreType.DB_SCALE:
                # For dB metrics, higher is usually better
                passed = value >= threshold
            elif score_type == ScoreType.PASS_FAIL:
                passed = bool(value)
        
        return QualityScore(
            name=name,
            category=category,
            value=value,
            score_type=score_type,
            threshold=threshold,
            passed=passed,
            weight=weight,
            description=description,
            unit=unit
        )
    
    def calculate_normalized_score(
        self,
        value: float,
        min_threshold: float,
        max_threshold: float,
        invert: bool = False
    ) -> float:
        """
Calculate normalized score (0.0 to 1.0)"""
        
        if min_threshold >= max_threshold:
            return 1.0 if value >= min_threshold else 0.0
        
        # Clamp value to range
        clamped_value = max(min_threshold, min(max_threshold, value))
        
        # Normalize to 0-1 range
        normalized = (clamped_value - min_threshold) / (max_threshold - min_threshold)
        
        # Invert if lower values are better
        if invert:
            normalized = 1.0 - normalized
        
        return normalized
    
    def calculate_db_score(
        self,
        value: float,
        target: float,
        tolerance: float = 3.0
    ) -> float:
        """
Calculate score for dB-scale metrics"""
        
        deviation = abs(value - target)
        
        if deviation <= tolerance:
            return 1.0 - (deviation / tolerance) * 0.2  # 80-100% for within tolerance
        else:
            # Exponential decay beyond tolerance
            excess_deviation = deviation - tolerance
            penalty = min(0.8, excess_deviation / (tolerance * 2))  # Max 80% penalty
            return max(0.0, 0.8 - penalty)
    
    def aggregate_scores(
        self,
        scores: List[QualityScore],
        weights: Optional[Dict[MetricCategory, float]] = None
    ) -> Tuple[float, QualityGrade]:
        """
Aggregate multiple scores into overall score and grade"""
        
        if not scores:
            return 0.0, QualityGrade.UNACCEPTABLE
        
        if weights is None:
            weights = {
                MetricCategory.TECHNICAL: 0.35,
                MetricCategory.PERCEPTUAL: 0.30,
                MetricCategory.CONTENT: 0.20,
                MetricCategory.COMPLIANCE: 0.15,
                MetricCategory.PERFORMANCE: 0.0
            }
        
        # Group scores by category
        category_scores = {}
        for category in MetricCategory:
            category_scores[category] = [s for s in scores if s.category == category]
        
        # Calculate weighted category averages
        weighted_sum = 0.0
        total_weight = 0.0
        
        for category, weight in weights.items():
            if weight <= 0 or category not in category_scores:
                continue
            
            cat_scores = category_scores[category]
            if not cat_scores:
                continue
            
            # Calculate weighted average within category
            total_weighted = sum(s.value * s.weight for s in cat_scores)
            total_cat_weight = sum(s.weight for s in cat_scores)
            
            if total_cat_weight > 0:
                category_avg = total_weighted / total_cat_weight
                weighted_sum += category_avg * weight
                total_weight += weight
        
        overall_score = weighted_sum / max(total_weight, 1.0)
        overall_grade = QualityMetrics.score_to_grade(overall_score)
        
        return overall_score, overall_grade
    
    def create_metrics_from_analysis(
        self,
        analysis_results: Dict[str, Any],
        thresholds: Dict[str, float] = None
    ) -> QualityMetrics:
        """
Create quality metrics from analysis results"""
        
        metrics = QualityMetrics()
        thresholds = thresholds or {}
        
        # Create scores for each metric
        for metric_name, value in analysis_results.items():
            if metric_name in self.metric_definitions:
                threshold = thresholds.get(metric_name)
                score = self.create_quality_score(metric_name, value, threshold)
                metrics.add_score(score)
        
        # Calculate overall scores
        metrics.calculate_overall_score()
        
        # Update metadata
        metrics.samples_analyzed = analysis_results.get('samples_analyzed', 0)
        metrics.processing_time = analysis_results.get('processing_time', 0.0)
        
        # Calculate confidence and reliability
        metrics.confidence_level = self._calculate_confidence(metrics.scores)
        metrics.reliability_index = self._calculate_reliability(metrics.scores)
        
        return metrics
    
    def _calculate_confidence(self, scores: List[QualityScore]) -> float:
        """
Calculate confidence level of quality assessment"""
        if not scores:
            return 0.0
        
        # Factors affecting confidence:
        # 1. Number of metrics assessed
        # 2. Consistency of scores
        # 3. Reliability of individual metrics
        
        # Coverage factor (more metrics = higher confidence)
        coverage_factor = min(1.0, len(scores) / 20.0)  # Target: 20 metrics
        
        # Consistency factor (less variance = higher confidence)
        values = [s.value for s in scores]
        if len(values) > 1:
            consistency_factor = 1.0 - min(1.0, statistics.stdev(values))
        else:
            consistency_factor = 1.0
        
        # Reliability factor (weighted by metric reliability)
        total_weight = sum(s.weight for s in scores)
        reliability_factor = min(1.0, total_weight / 10.0)  # Normalized
        
        # Combined confidence
        confidence = (coverage_factor * 0.4 + consistency_factor * 0.4 + reliability_factor * 0.2)
        
        return max(0.0, min(1.0, confidence))
    
    def _calculate_reliability(self, scores: List[QualityScore]) -> float:
        """
Calculate reliability index of quality assessment"""
        if not scores:
            return 0.0
        
        # Reliability based on:
        # 1. Proportion of mandatory metrics that passed
        # 2. Overall pass rate
        # 3. Score distribution
        
        mandatory_scores = [s for s in scores if hasattr(s, 'mandatory') and s.mandatory]
        if mandatory_scores:
            mandatory_pass_rate = len([s for s in mandatory_scores if s.passed]) / len(mandatory_scores)
        else:
            mandatory_pass_rate = 1.0
        
        overall_pass_rate = len([s for s in scores if s.passed]) / len(scores)
        
        # Score distribution factor (prefer balanced scores)
        values = [s.value for s in scores]
        if len(values) > 1:
            distribution_factor = 1.0 - min(1.0, statistics.stdev(values) * 2)
        else:
            distribution_factor = 1.0
        
        reliability = (mandatory_pass_rate * 0.5 + overall_pass_rate * 0.3 + distribution_factor * 0.2)
        
        return max(0.0, min(1.0, reliability))
    
    def compare_metrics(
        self,
        metrics1: QualityMetrics,
        metrics2: QualityMetrics
    ) -> Dict[str, Any]:
        """
Compare two quality metrics"""
        
        comparison = {
            'overall_score_diff': metrics2.overall_score - metrics1.overall_score,
            'grade_change': {
                'from': metrics1.overall_grade.value,
                'to': metrics2.overall_grade.value,
                'improved': metrics2.overall_score > metrics1.overall_score
            },
            'category_changes': {
                'technical': metrics2.technical_score - metrics1.technical_score,
                'perceptual': metrics2.perceptual_score - metrics1.perceptual_score,
                'content': metrics2.content_score - metrics1.content_score,
                'compliance': metrics2.compliance_score - metrics1.compliance_score
            },
            'confidence_change': metrics2.confidence_level - metrics1.confidence_level,
            'reliability_change': metrics2.reliability_index - metrics1.reliability_index,
            'processing_time_diff': metrics2.processing_time - metrics1.processing_time
        }
        
        # Identify significantly changed metrics
        metric_changes = []
        scores1_dict = {s.name: s for s in metrics1.scores}
        scores2_dict = {s.name: s for s in metrics2.scores}
        
        for name in set(scores1_dict.keys()) | set(scores2_dict.keys()):
            if name in scores1_dict and name in scores2_dict:
                diff = scores2_dict[name].value - scores1_dict[name].value
                if abs(diff) > 0.1:  # Significant change threshold
                    metric_changes.append({
                        'metric': name,
                        'change': diff,
                        'category': scores2_dict[name].category.value,
                        'improved': diff > 0
                    })
        
        comparison['metric_changes'] = sorted(metric_changes, key=lambda x: abs(x['change']), reverse=True)
        
        return comparison
