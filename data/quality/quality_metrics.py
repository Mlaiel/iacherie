"""Quality Metrics - Quality Scoring and Analytics System
======================================================

Enterprise-grade quality metrics calculation and analytics for data quality management.
Provides comprehensive scoring algorithms, trend analysis, and quality reporting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""
from typing import Dict, Any, List, Optional, Union, Tuple
import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics
import json

logger = logging.getLogger(__name__)

class QualityDimension(Enum):
    """Quality dimensions for comprehensive assessment"""    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"
    INTEGRITY = "integrity"
    COMPLIANCE = "compliance"

@dataclass
class QualityScore:
    """Quality score container with detailed breakdown"""    overall_score: float
    dimension_scores: Dict[str, float]
    confidence_level: float
    sample_size: int
    calculation_method: str
    timestamp: datetime
    metadata: Dict[str, Any]

class QualityTrend:
    """Quality trend analysis container"""    
    def __init__(self):
        self.trend_direction: str = "stable"  # improving, declining, stable
        self.trend_strength: float = 0.0  # 0-100
"""Quality Metrics - Quality Scoring and Analytics System
======================================================

Enterprise-grade quality metrics calculation and analytics for data quality management.
Provides comprehensive scoring algorithms, trend analysis, and quality reporting.

⚠️  COPYRIGHT WARNING ⚠️
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or theft of this code or concept without explicit 
written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and 
will result in immediate legal action under German and international copyright law.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
                Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import statistics
import json
import numpy as np
from collections import defaultdict, deque
import math
from scipy import stats
import pandas as pd

logger = logging.getLogger(__name__)

class QualityDimension(Enum):
    """Quality dimensions for comprehensive assessment"""    ACCURACY = "accuracy"                    # Correctness of data
    COMPLETENESS = "completeness"            # Data presence and fullness
    CONSISTENCY = "consistency"              # Internal coherence
    TIMELINESS = "timeliness"               # Freshness and currency
    VALIDITY = "validity"                   # Format and constraint compliance
    UNIQUENESS = "uniqueness"               # Absence of duplicates
    INTEGRITY = "integrity"                 # Referential integrity
    COMPLIANCE = "compliance"               # Regulatory compliance
    USABILITY = "usability"                 # Fitness for purpose
    RELEVANCE = "relevance"                 # Business value alignment

class MetricType(Enum):
    """Types of quality metrics"""    PERCENTAGE = "percentage"               # 0-100 scale
    RATIO = "ratio"                        # 0-1 scale  
    COUNT = "count"                        # Absolute numbers
    DURATION = "duration"                  # Time measurements
    SCORE = "score"                        # Custom scoring

class TrendDirection(Enum):
    """Quality trend directions"""    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"

@dataclass
class QualityMeasurement:
    """Individual quality measurement"""    metric_name: str
    value: float
    dimension: QualityDimension
    metric_type: MetricType
    timestamp: datetime
    weight: float = 1.0
    confidence: float = 1.0
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QualityScore:
    """Comprehensive quality score with detailed breakdown"""    overall_score: float
    dimension_scores: Dict[str, float]
    confidence_level: float
    sample_size: int
    calculation_method: str
    timestamp: datetime
    metadata: Dict[str, Any]
    measurements: List[QualityMeasurement] = field(default_factory=list)
    weights: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate score after initialization"""        if not 0 <= self.overall_score <= 100:
            raise ValueError(f"Overall score must be between 0-100, got {self.overall_score}")
        
        for dim, score in self.dimension_scores.items():
            if not 0 <= score <= 100:
                raise ValueError(f"Dimension score for {dim} must be between 0-100, got {score}")

@dataclass 
class QualityTrend:
    """Quality trend analysis results"""    direction: TrendDirection
    strength: float                         # 0-100, strength of trend
    change_rate: float                      # Percentage change per period
    slope: float                           # Linear regression slope
    r_squared: float                       # Correlation coefficient
    volatility: float                      # Standard deviation of changes
    periods_analyzed: int
    forecast_next: Optional[float] = None   # Predicted next value
    confidence_interval: Optional[Tuple[float, float]] = None
    
class QualityBaseline:
    """Quality baseline for comparison"""    
    def __init__(self, name: str, target_scores: Dict[str, float]):
        self.name = name
        self.target_scores = target_scores
        self.created_at = datetime.utcnow()
        self.last_updated = datetime.utcnow()
    
    def update_targets(self, new_targets: Dict[str, float]):
        """Update baseline targets"""        self.target_scores.update(new_targets)
        self.last_updated = datetime.utcnow()
    
    def compare_score(self, actual_score: float, dimension: str) -> Dict[str, Any]:
        """Compare actual score against baseline"""        target = self.target_scores.get(dimension, 80.0)  # Default target
        variance = actual_score - target
        variance_percentage = (variance / target) * 100 if target > 0 else 0
        
        status = "meets_target" if actual_score >= target else "below_target"
        if actual_score >= target * 1.1:  # 10% above target
            status = "exceeds_target"
        
        return {
            'actual': actual_score,
            'target': target,
            'variance': variance,
            'variance_percentage': variance_percentage,
            'status': status
        }

class QualityMetrics:
    """    Enterprise-grade quality metrics calculation and analytics engine.
    
    Provides comprehensive quality scoring, trend analysis, benchmarking,
    and predictive quality analytics for multi-format content.
    """    
    def __init__(self, config: Dict[str, Any]):
        """        Initialize quality metrics engine.
        
        Args:
            config: Configuration settings
        """        self.config = config
        self.logger = logger
        
        # Metrics storage
        self.measurements: deque = deque(maxlen=10000)  # Rolling buffer
        self.dimension_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.baselines: Dict[str, QualityBaseline] = {}
        
        # Configuration
        self.trend_window = config.get('trend_window', 30)  # Days
        self.scoring_method = config.get('scoring_method', 'weighted_average')
        self.confidence_threshold = config.get('confidence_threshold', 0.8)
        
        # Default dimension weights
        self.default_weights = {
            QualityDimension.ACCURACY.value: 0.2,
            QualityDimension.COMPLETENESS.value: 0.15,
            QualityDimension.CONSISTENCY.value: 0.15,
            QualityDimension.VALIDITY.value: 0.15,
            QualityDimension.INTEGRITY.value: 0.1,
            QualityDimension.COMPLIANCE.value: 0.1,
            QualityDimension.TIMELINESS.value: 0.05,
            QualityDimension.UNIQUENESS.value: 0.05,
            QualityDimension.USABILITY.value: 0.03,
            QualityDimension.RELEVANCE.value: 0.02
        }
        
        # Initialize default baselines
        self._initialize_baselines()
        
        self.logger.info("QualityMetrics engine initialized")
    
    def _initialize_baselines(self):
        """Initialize default quality baselines"""        
        # Enterprise baseline (high standards)
        enterprise_targets = {
            QualityDimension.ACCURACY.value: 95.0,
            QualityDimension.COMPLETENESS.value: 90.0,
            QualityDimension.CONSISTENCY.value: 90.0,
            QualityDimension.VALIDITY.value: 95.0,
            QualityDimension.INTEGRITY.value: 100.0,
            QualityDimension.COMPLIANCE.value: 100.0,
            QualityDimension.TIMELINESS.value: 85.0,
            QualityDimension.UNIQUENESS.value: 98.0,
            QualityDimension.USABILITY.value: 80.0,
            QualityDimension.RELEVANCE.value: 75.0
        }
        
        # Standard baseline (moderate standards)
        standard_targets = {
            QualityDimension.ACCURACY.value: 85.0,
            QualityDimension.COMPLETENESS.value: 80.0,
            QualityDimension.CONSISTENCY.value: 80.0,
            QualityDimension.VALIDITY.value: 85.0,
            QualityDimension.INTEGRITY.value: 95.0,
            QualityDimension.COMPLIANCE.value: 100.0,
            QualityDimension.TIMELINESS.value: 75.0,
            QualityDimension.UNIQUENESS.value: 95.0,
            QualityDimension.USABILITY.value: 70.0,
            QualityDimension.RELEVANCE.value: 65.0
        }
        
        self.baselines['enterprise'] = QualityBaseline('enterprise', enterprise_targets)
        self.baselines['standard'] = QualityBaseline('standard', standard_targets)
    
    def record_measurement(self, measurement: QualityMeasurement):
        """Record a quality measurement"""        self.measurements.append(measurement)
        self.dimension_history[measurement.dimension.value].append({
            'value': measurement.value,
            'timestamp': measurement.timestamp,
            'confidence': measurement.confidence,
            'weight': measurement.weight
        })
        
        self.logger.debug(f"Recorded measurement: {measurement.metric_name} = {measurement.value}")
    
    def calculate_overall_score(
        self,
        dimension_scores: Dict[str, float],
        weights: Optional[Dict[str, float]] = None,
        method: str = "weighted_average"
    ) -> float:
        """        Calculate overall quality score from dimension scores.
        
        Args:
            dimension_scores: Scores for each quality dimension
            weights: Custom weights for dimensions
            method: Calculation method
            
        Returns:
            Overall quality score (0-100)
        """        if not dimension_scores:
            return 0.0
        
        weights = weights or self.default_weights
        
        if method == "weighted_average":
            total_weighted_score = 0
            total_weight = 0
            
            for dimension, score in dimension_scores.items():
                weight = weights.get(dimension, 0.1)  # Default weight
                total_weighted_score += score * weight
                total_weight += weight
            
            return total_weighted_score / total_weight if total_weight > 0 else 0.0
        
        elif method == "geometric_mean":
            # Geometric mean - more sensitive to low scores
            scores = list(dimension_scores.values())
            if any(score <= 0 for score in scores):
                return 0.0
            
            product = 1.0
            for score in scores:
                product *= (score / 100.0)
            
            return (product ** (1.0 / len(scores))) * 100
        
        elif method == "harmonic_mean":
            # Harmonic mean - very sensitive to outliers
            scores = [score for score in dimension_scores.values() if score > 0]
            if not scores:
                return 0.0
            
            harmonic_sum = sum(1.0 / score for score in scores)
            return len(scores) / harmonic_sum
        
        elif method == "minimum":
            # Minimum score - most conservative
            return min(dimension_scores.values())
        
        else:
            # Default to simple average
            return sum(dimension_scores.values()) / len(dimension_scores)
    
    def calculate_quality_score(
        self,
        measurements: List[QualityMeasurement],
        weights: Optional[Dict[str, float]] = None,
        baseline: Optional[str] = None
    ) -> QualityScore:
        """        Calculate comprehensive quality score from measurements.
        
        Args:
            measurements: List of quality measurements
            weights: Custom dimension weights
            baseline: Baseline name for comparison
            
        Returns:
            Comprehensive quality score
        """        if not measurements:
            return QualityScore(
                overall_score=0.0,
                dimension_scores={},
                confidence_level=0.0,
                sample_size=0,
                calculation_method=self.scoring_method,
                timestamp=datetime.utcnow(),
                metadata={'error': 'No measurements provided'}
            )
        
        # Group measurements by dimension
        dimension_measurements = defaultdict(list)
        for measurement in measurements:
            dimension_measurements[measurement.dimension.value].append(measurement)
        
        # Calculate dimension scores
        dimension_scores = {}
        total_confidence = 0
        confidence_count = 0
        
        for dimension, dim_measurements in dimension_measurements.items():
            if not dim_measurements:
                continue
            
            # Calculate weighted average for dimension
            total_weighted_value = 0
            total_weight = 0
            dimension_confidence = 0
            
            for measurement in dim_measurements:
                weight = measurement.weight
                confidence = measurement.confidence
                
                total_weighted_value += measurement.value * weight * confidence
                total_weight += weight * confidence
                dimension_confidence += confidence
            
            if total_weight > 0:
                dimension_scores[dimension] = total_weighted_value / total_weight
                total_confidence += dimension_confidence / len(dim_measurements)
                confidence_count += 1
        
        # Calculate overall score
        overall_score = self.calculate_overall_score(
            dimension_scores, 
            weights or self.default_weights,
            self.scoring_method
        )
        
        # Calculate overall confidence
        overall_confidence = total_confidence / confidence_count if confidence_count > 0 else 0.0
        
        # Create metadata
        metadata = {
            'measurement_count': len(measurements),
            'dimensions_measured': len(dimension_scores),
            'calculation_timestamp': datetime.utcnow().isoformat(),
            'weights_used': weights or self.default_weights
        }
        
        # Add baseline comparison if specified
        if baseline and baseline in self.baselines:
            baseline_obj = self.baselines[baseline]
            metadata['baseline_comparison'] = {}
            
            for dimension, score in dimension_scores.items():
                comparison = baseline_obj.compare_score(score, dimension)
                metadata['baseline_comparison'][dimension] = comparison
        
        return QualityScore(
            overall_score=round(overall_score, 2),
            dimension_scores={k: round(v, 2) for k, v in dimension_scores.items()},
            confidence_level=round(overall_confidence, 3),
            sample_size=len(measurements),
            calculation_method=self.scoring_method,
            timestamp=datetime.utcnow(),
            metadata=metadata,
            measurements=measurements,
            weights=weights or self.default_weights
        )
    
    def analyze_trend(
        self,
        dimension: str,
        timeframe: Optional[timedelta] = None,
        method: str = "linear_regression"
    ) -> QualityTrend:
        """        Analyze quality trend for a specific dimension.
        
        Args:
            dimension: Quality dimension to analyze
            timeframe: Time period for analysis
            method: Trend analysis method
            
        Returns:
            Quality trend analysis
        """        if dimension not in self.dimension_history:
            return QualityTrend(
                direction=TrendDirection.UNKNOWN,
                strength=0.0,
                change_rate=0.0,
                slope=0.0,
                r_squared=0.0,
                volatility=0.0,
                periods_analyzed=0
            )
        
        history = list(self.dimension_history[dimension])
        
        # Filter by timeframe if specified
        if timeframe:
            cutoff_time = datetime.utcnow() - timeframe
            history = [h for h in history if h['timestamp'] > cutoff_time]
        
        if len(history) < 3:  # Need minimum data points
            return QualityTrend(
                direction=TrendDirection.UNKNOWN,
                strength=0.0,
                change_rate=0.0,
                slope=0.0,
                r_squared=0.0,
                volatility=0.0,
                periods_analyzed=len(history)
            )
        
        # Extract values and timestamps
        values = [h['value'] for h in history]
        timestamps = [h['timestamp'] for h in history]
        
        # Convert timestamps to numeric values for regression
        time_numeric = [(ts - timestamps[0]).total_seconds() for ts in timestamps]
        
        if method == "linear_regression":
            # Perform linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(time_numeric, values)
            
            # Determine trend direction
            if abs(slope) < 0.01:  # Very small slope
                direction = TrendDirection.STABLE
            elif slope > 0:
                direction = TrendDirection.IMPROVING
            else:
                direction = TrendDirection.DECLINING
            
            # Calculate trend strength (0-100)
            r_squared = r_value ** 2
            strength = min(100, abs(r_squared) * 100)
            
            # Calculate change rate (per day)
            seconds_per_day = 86400
            change_rate = (slope * seconds_per_day / np.mean(values)) * 100 if np.mean(values) > 0 else 0
            
            # Calculate volatility
            residuals = [values[i] - (slope * time_numeric[i] + intercept) for i in range(len(values))]
            volatility = np.std(residuals) if residuals else 0.0
            
            # Predict next value (1 day ahead)
            next_time = time_numeric[-1] + seconds_per_day
            forecast_next = slope * next_time + intercept
            
            # Calculate confidence interval (95%)
            if len(values) > 2:
                t_val = stats.t.ppf(0.975, len(values) - 2)  # 95% confidence
                prediction_std = std_err * np.sqrt(1 + 1/len(values) + 
                                                  (next_time - np.mean(time_numeric))**2 / 
                                                  np.sum([(t - np.mean(time_numeric))**2 for t in time_numeric]))
                margin = t_val * prediction_std
                confidence_interval = (forecast_next - margin, forecast_next + margin)
            else:
                confidence_interval = None
            
            return QualityTrend(
                direction=direction,
                strength=round(strength, 2),
                change_rate=round(change_rate, 4),
                slope=round(slope, 6),
                r_squared=round(r_squared, 4),
                volatility=round(volatility, 2),
                periods_analyzed=len(history),
                forecast_next=round(forecast_next, 2) if forecast_next else None,
                confidence_interval=(round(confidence_interval[0], 2), round(confidence_interval[1], 2)) if confidence_interval else None
            )
        
        elif method == "moving_average":
            # Simple moving average trend
            window_size = min(7, len(values) // 2)  # 7-point or half the data
            if window_size < 2:
                window_size = 2
            
            recent_avg = np.mean(values[-window_size:])
            earlier_avg = np.mean(values[:window_size])
            
            change = recent_avg - earlier_avg
            change_rate = (change / earlier_avg) * 100 if earlier_avg > 0 else 0
            
            if abs(change_rate) < 1:  # Less than 1% change
                direction = TrendDirection.STABLE
            elif change_rate > 0:
                direction = TrendDirection.IMPROVING
            else:
                direction = TrendDirection.DECLINING
            
            strength = min(100, abs(change_rate) * 10)  # Scale to 0-100
            volatility = np.std(values)
            
            return QualityTrend(
                direction=direction,
                strength=round(strength, 2),
                change_rate=round(change_rate, 4),
                slope=change / len(values),
                r_squared=0.0,
                volatility=round(volatility, 2),
                periods_analyzed=len(history)
            )
        
        else:
            raise ValueError(f"Unknown trend analysis method: {method}")
    
    def get_metrics(
        self,
        timeframe: Optional[timedelta] = None,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """        Get comprehensive quality metrics for specified timeframe.
        
        Args:
            timeframe: Time period for metrics
            content_type: Filter by content type
            
        Returns:
            Comprehensive metrics dictionary
        """        if timeframe is None:
            timeframe = timedelta(hours=24)
        
        cutoff_time = datetime.utcnow() - timeframe
        
        # Filter measurements by timeframe
        filtered_measurements = [
            m for m in self.measurements 
            if m.timestamp > cutoff_time
        ]
        
        # Filter by content type if specified
        if content_type:
            filtered_measurements = [
                m for m in filtered_measurements
                if m.context.get('content_type') == content_type
            ]
        
        if not filtered_measurements:
            return {
                'timeframe_hours': timeframe.total_seconds() / 3600,
                'content_type': content_type,
                'total_measurements': 0,
                'message': 'No measurements found for specified criteria'
            }
        
        # Calculate current quality score
        current_score = self.calculate_quality_score(filtered_measurements)
        
        # Analyze trends for each dimension
        trends = {}
        for dimension in QualityDimension:
            if dimension.value in current_score.dimension_scores:
                trend = self.analyze_trend(dimension.value, timeframe)
                trends[dimension.value] = {
                    'direction': trend.direction.value,
                    'strength': trend.strength,
                    'change_rate': trend.change_rate,
                    'forecast_next': trend.forecast_next
                }
        
        # Calculate statistics
        all_scores = [m.value for m in filtered_measurements]
        
        # Group by dimension for detailed analysis
        dimension_stats = {}
        for dimension in QualityDimension:
            dim_measurements = [m for m in filtered_measurements if m.dimension == dimension]
            if dim_measurements:
                dim_values = [m.value for m in dim_measurements]
                dimension_stats[dimension.value] = {
                    'count': len(dim_values),
                    'mean': round(statistics.mean(dim_values), 2),
                    'median': round(statistics.median(dim_values), 2),
                    'std_dev': round(statistics.stdev(dim_values), 2) if len(dim_values) > 1 else 0,
                    'min': min(dim_values),
                    'max': max(dim_values),
                    'range': max(dim_values) - min(dim_values)
                }
        
        # Calculate quality distribution
        score_ranges = {
            'excellent': len([s for s in all_scores if s >= 90]),
            'good': len([s for s in all_scores if 80 <= s < 90]),
            'acceptable': len([s for s in all_scores if 70 <= s < 80]),
            'poor': len([s for s in all_scores if 50 <= s < 70]),
            'critical': len([s for s in all_scores if s < 50])
        }
        
        return {
            'timeframe_hours': timeframe.total_seconds() / 3600,
            'content_type': content_type,
            'current_quality_score': current_score.to_dict(),
            'total_measurements': len(filtered_measurements),
            'dimension_statistics': dimension_stats,
            'quality_distribution': score_ranges,
            'trends': trends,
            'overall_statistics': {
                'mean_score': round(statistics.mean(all_scores), 2) if all_scores else 0,
                'median_score': round(statistics.median(all_scores), 2) if all_scores else 0,
                'std_deviation': round(statistics.stdev(all_scores), 2) if len(all_scores) > 1 else 0,
                'score_range': max(all_scores) - min(all_scores) if all_scores else 0
            },
            'data_freshness': {
                'latest_measurement': max(m.timestamp for m in filtered_measurements).isoformat() if filtered_measurements else None,
                'oldest_measurement': min(m.timestamp for m in filtered_measurements).isoformat() if filtered_measurements else None,
                'measurement_frequency': len(filtered_measurements) / (timeframe.total_seconds() / 3600)  # per hour
            }
        }
    
    def create_baseline(self, name: str, target_scores: Dict[str, float]):
        """Create a new quality baseline"""        self.baselines[name] = QualityBaseline(name, target_scores)
        self.logger.info(f"Created quality baseline: {name}")
    
    def update_baseline(self, name: str, target_scores: Dict[str, float]):
        """Update existing quality baseline"""        if name in self.baselines:
            self.baselines[name].update_targets(target_scores)
            self.logger.info(f"Updated quality baseline: {name}")
        else:
            self.create_baseline(name, target_scores)
    
    def compare_to_baseline(
        self,
        current_scores: Dict[str, float],
        baseline_name: str = "enterprise"
    ) -> Dict[str, Any]:
        """Compare current scores to baseline"""        if baseline_name not in self.baselines:
            return {'error': f'Baseline "{baseline_name}" not found'}
        
        baseline = self.baselines[baseline_name]
        comparisons = {}
        
        for dimension, score in current_scores.items():
            comparison = baseline.compare_score(score, dimension)
            comparisons[dimension] = comparison
        
        # Calculate overall baseline compliance
        total_variance = sum(comp['variance'] for comp in comparisons.values())
        avg_variance = total_variance / len(comparisons) if comparisons else 0
        
        compliance_percentage = len([comp for comp in comparisons.values() if comp['status'] in ['meets_target', 'exceeds_target']]) / len(comparisons) * 100 if comparisons else 0
        
        return {
            'baseline_name': baseline_name,
            'baseline_created': baseline.created_at.isoformat(),
            'comparisons': comparisons,
            'overall_compliance_percentage': round(compliance_percentage, 2),
            'average_variance': round(avg_variance, 2),
            'dimensions_exceeding': len([comp for comp in comparisons.values() if comp['status'] == 'exceeds_target']),
            'dimensions_meeting': len([comp for comp in comparisons.values() if comp['status'] == 'meets_target']),
            'dimensions_below': len([comp for comp in comparisons.values() if comp['status'] == 'below_target'])
        }
    
    def get_quality_insights(self, timeframe: timedelta = timedelta(days=7)) -> Dict[str, Any]:
        """Generate quality insights and recommendations"""        metrics = self.get_metrics(timeframe)
        
        insights = {
            'summary': {},
            'concerns': [],
            'recommendations': [],
            'achievements': []
        }
        
        if 'current_quality_score' in metrics:
            overall_score = metrics['current_quality_score']['overall_score']
            
            # Overall assessment
            if overall_score >= 90:
                insights['summary']['assessment'] = 'Excellent quality levels maintained'
                insights['achievements'].append('Achieving excellent quality standards')
            elif overall_score >= 80:
                insights['summary']['assessment'] = 'Good quality with room for improvement'
            elif overall_score >= 70:
                insights['summary']['assessment'] = 'Acceptable quality but needs attention'
                insights['concerns'].append('Quality levels approaching concerning thresholds')
            else:
                insights['summary']['assessment'] = 'Quality requires immediate attention'
                insights['concerns'].append('Quality levels below acceptable standards')
        
        # Analyze trends for concerns and recommendations
        if 'trends' in metrics:
            for dimension, trend in metrics['trends'].items():
                if trend['direction'] == 'declining' and trend['strength'] > 50:
                    insights['concerns'].append(f'{dimension.title()} quality showing strong declining trend')
                    insights['recommendations'].append(f'Investigate and address {dimension} quality degradation')
                elif trend['direction'] == 'improving' and trend['strength'] > 50:
                    insights['achievements'].append(f'{dimension.title()} quality showing strong improvement')
        
        # Analyze dimension statistics for specific recommendations
        if 'dimension_statistics' in metrics:
            for dimension, stats in metrics['dimension_statistics'].items():
                if stats['std_dev'] > 20:  # High variability
                    insights['concerns'].append(f'{dimension.title()} quality highly variable (std dev: {stats["std_dev"]})')
                    insights['recommendations'].append(f'Standardize {dimension} quality processes to reduce variability')
                
                if stats['min'] < 50:  # Very low minimum
                    insights['concerns'].append(f'{dimension.title()} has very low minimum score: {stats["min"]}')
                    insights['recommendations'].append(f'Implement minimum quality gates for {dimension}')
        
        return insights
    
    def export_metrics(
        self,
        format_type: str = "json",
        timeframe: Optional[timedelta] = None,
        include_raw_data: bool = False
    ) -> Union[str, Dict[str, Any]]:
        """Export quality metrics in specified format"""        
        metrics = self.get_metrics(timeframe)
        
        if include_raw_data:
            raw_measurements = []
            if timeframe:
                cutoff_time = datetime.utcnow() - timeframe
                filtered_measurements = [m for m in self.measurements if m.timestamp > cutoff_time]
            else:
                filtered_measurements = list(self.measurements)
            
            for measurement in filtered_measurements:
                raw_measurements.append({
                    'metric_name': measurement.metric_name,
                    'value': measurement.value,
                    'dimension': measurement.dimension.value,
                    'timestamp': measurement.timestamp.isoformat(),
                    'weight': measurement.weight,
                    'confidence': measurement.confidence,
                    'context': measurement.context
                })
            
            metrics['raw_measurements'] = raw_measurements
        
        metrics['export_timestamp'] = datetime.utcnow().isoformat()
        metrics['export_format'] = format_type
        
        if format_type == "json":
            return json.dumps(metrics, indent=2, default=str)
        elif format_type == "dict":
            return metrics
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def clear_history(self, older_than: Optional[timedelta] = None):
        """Clear measurement history"""        if older_than:
            cutoff_time = datetime.utcnow() - older_than
            # Filter measurements
            self.measurements = deque(
                [m for m in self.measurements if m.timestamp > cutoff_time],
                maxlen=self.measurements.maxlen
            )
            
            # Filter dimension history
            for dimension in self.dimension_history:
                self.dimension_history[dimension] = deque(
                    [h for h in self.dimension_history[dimension] if h['timestamp'] > cutoff_time],
                    maxlen=self.dimension_history[dimension].maxlen
                )
        else:
            # Clear all history
            self.measurements.clear()
            for dimension in self.dimension_history:
                self.dimension_history[dimension].clear()
        
        self.logger.info(f"Cleared quality metrics history {'older than ' + str(older_than) if older_than else 'completely'}")
    
    def get_dimension_weights(self) -> Dict[str, float]:
        """Get current dimension weights"""        return self.default_weights.copy()
    
    def update_dimension_weights(self, new_weights: Dict[str, float]):
        """Update dimension weights"""        # Validate weights sum to 1.0
        total_weight = sum(new_weights.values())
        if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
            raise ValueError(f"Dimension weights must sum to 1.0, got {total_weight}")
        
        self.default_weights.update(new_weights)
        self.logger.info("Updated dimension weights")
    
    def list_baselines(self) -> List[Dict[str, Any]]:
        """List all available baselines"""        return [
            {
                'name': baseline.name,
                'targets': baseline.target_scores,
                'created_at': baseline.created_at.isoformat(),
                'last_updated': baseline.last_updated.isoformat()
            }
            for baseline in self.baselines.values()
        ]
        self.prediction_confidence: float = 0.0
        self.time_series: List[Tuple[datetime, float]] = []

class QualityMetrics:
    """    Comprehensive quality metrics calculation and analytics system.
    
    Provides advanced scoring algorithms, trend analysis, benchmarking,
    and predictive quality analytics for data quality management.
    """    
    def __init__(self, config: Dict[str, Any]):
        """        Initialize the quality metrics system.
        
        Args:
            config: Quality metrics configuration
        """        self.config = config
        self.logger = logger
        
        # Metric weights for different dimensions
        self.dimension_weights = {
            QualityDimension.ACCURACY: 0.20,
            QualityDimension.COMPLETENESS: 0.15,
            QualityDimension.CONSISTENCY: 0.15,
            QualityDimension.TIMELINESS: 0.10,
            QualityDimension.VALIDITY: 0.15,
            QualityDimension.UNIQUENESS: 0.10,
            QualityDimension.INTEGRITY: 0.10,
            QualityDimension.COMPLIANCE: 0.05
        }
        
        # Historical metrics storage
        self.metrics_history: List[QualityScore] = []
        
        # Benchmarks by content type
        self.benchmarks = {
            'audio': {'excellent': 95, 'good': 85, 'acceptable': 75},
            'video': {'excellent': 90, 'good': 80, 'acceptable': 70},
            'image': {'excellent': 92, 'good': 82, 'acceptable': 72},
            'text': {'excellent': 88, 'good': 78, 'acceptable': 68}
        }
        
        # Quality thresholds
        self.thresholds = {
            'critical_threshold': 50,
            'warning_threshold': 70,
            'good_threshold': 85,
            'excellent_threshold': 95
        }
        
        self.logger.info("QualityMetrics initialized")
    
    def calculate_overall_score(
        self,
        dimension_scores: Dict[str, float],
        content_type: Optional[str] = None,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> float:
        """        Calculate overall quality score from dimension scores.
        
        Args:
            dimension_scores: Scores for each quality dimension
            content_type: Optional content type for specific weighting
            custom_weights: Optional custom dimension weights
            
        Returns:
            Overall quality score (0-100)
        """        try:
            # Use custom weights if provided, otherwise use default
            weights = custom_weights or self.dimension_weights
            
            # Adjust weights based on content type
            if content_type:
                weights = self._adjust_weights_for_content_type(weights, content_type)
            
            total_score = 0.0
            total_weight = 0.0
            
            for dimension, score in dimension_scores.items():
                if dimension in weights:
                    weight = weights[dimension]
                    total_score += score * weight
                    total_weight += weight
                elif hasattr(QualityDimension, dimension.upper()):
                    # Handle string dimension names
                    dim_enum = getattr(QualityDimension, dimension.upper())
                    if dim_enum in weights:
                        weight = weights[dim_enum]
                        total_score += score * weight
                        total_weight += weight
            
            # Calculate weighted average
            if total_weight > 0:
                overall_score = total_score / total_weight
            else:
                overall_score = 0.0
            
            # Ensure score is within bounds
            overall_score = max(0.0, min(100.0, overall_score))
            
            return round(overall_score, 2)
            
        except Exception as e:
            self.logger.error(f"Error calculating overall score: {str(e)}")
            return 0.0
    
    def _adjust_weights_for_content_type(
        self,
        base_weights: Dict[QualityDimension, float],
        content_type: str
    ) -> Dict[QualityDimension, float]:
        """Adjust dimension weights based on content type"""        
        adjusted_weights = base_weights.copy()
        
        # Content-specific weight adjustments
        if content_type == 'audio':
            # For audio, integrity and accuracy are more important
            adjusted_weights[QualityDimension.INTEGRITY] *= 1.5
            adjusted_weights[QualityDimension.ACCURACY] *= 1.3
            adjusted_weights[QualityDimension.TIMELINESS] *= 0.7
            
        elif content_type == 'video':
            # For video, consistency and integrity are crucial
            adjusted_weights[QualityDimension.CONSISTENCY] *= 1.4
            adjusted_weights[QualityDimension.INTEGRITY] *= 1.4
            adjusted_weights[QualityDimension.COMPLETENESS] *= 1.2
            
        elif content_type == 'image':
            # For images, accuracy and validity are key
            adjusted_weights[QualityDimension.ACCURACY] *= 1.4
            adjusted_weights[QualityDimension.VALIDITY] *= 1.3
            adjusted_weights[QualityDimension.UNIQUENESS] *= 0.8
            
        elif content_type == 'text':
            # For text, completeness and compliance are important
            adjusted_weights[QualityDimension.COMPLETENESS] *= 1.4
            adjusted_weights[QualityDimension.COMPLIANCE] *= 1.5
            adjusted_weights[QualityDimension.VALIDITY] *= 1.3
        
        # Normalize weights to sum to 1.0
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            for dimension in adjusted_weights:
                adjusted_weights[dimension] /= total_weight
        
        return adjusted_weights
    
    def calculate_dimension_score(
        self,
        dimension: QualityDimension,
        metrics: Dict[str, Any],
        content_type: Optional[str] = None
    ) -> float:
        """        Calculate score for a specific quality dimension.
        
        Args:
            dimension: Quality dimension to calculate
            metrics: Raw metrics data
            content_type: Optional content type
            
        Returns:
            Dimension score (0-100)
        """        try:
            if dimension == QualityDimension.ACCURACY:
                return self._calculate_accuracy_score(metrics, content_type)
            elif dimension == QualityDimension.COMPLETENESS:
                return self._calculate_completeness_score(metrics, content_type)
            elif dimension == QualityDimension.CONSISTENCY:
                return self._calculate_consistency_score(metrics, content_type)
            elif dimension == QualityDimension.TIMELINESS:
                return self._calculate_timeliness_score(metrics, content_type)
            elif dimension == QualityDimension.VALIDITY:
                return self._calculate_validity_score(metrics, content_type)
            elif dimension == QualityDimension.UNIQUENESS:
                return self._calculate_uniqueness_score(metrics, content_type)
            elif dimension == QualityDimension.INTEGRITY:
                return self._calculate_integrity_score(metrics, content_type)
            elif dimension == QualityDimension.COMPLIANCE:
                return self._calculate_compliance_score(metrics, content_type)
            else:
                return 0.0
                
        except Exception as e:
            self.logger.error(f"Error calculating {dimension.value} score: {str(e)}")
            return 0.0
    
    def _calculate_accuracy_score(self, metrics: Dict[str, Any], content_type: Optional[str]) -> float:
        """Calculate accuracy dimension score"""        
        # Example calculation based on validation results
        validation_score = metrics.get('validation_score', 0)
        error_rate = metrics.get('error_rate', 0)
        
        # Accuracy decreases with error rate
        accuracy = max(0, validation_score - (error_rate * 10))
        
        return min(100, accuracy)
    
    def _calculate_completeness_score(self, metrics: Dict[str, Any], content_type: Optional[str]) -> float:
        """Calculate completeness dimension score"""        
        required_fields = metrics.get('required_fields', 0)
        present_fields = metrics.get('present_fields', 0)
        
        if required_fields == 0:
            return 100.0
        
        completeness = (present_fields / required_fields) * 100
        return min(100, completeness)
    
    def _calculate_consistency_score(self, metrics: Dict[str, Any], content_type: Optional[str]) -> float:
        """Calculate consistency dimension score"""        
        format_consistency = metrics.get('format_consistency', 100)
        structure_consistency = metrics.get('structure_consistency', 100)
        
        # Average of consistency metrics
        consistency = (format_consistency + structure_consistency) / 2
        
        return min(100, consistency)
    
    def _calculate_timeliness_score(self, metrics: Dict[str, Any], content_type: Optional[str]) -> float:
        """Calculate timeliness dimension score"""        
        processing_time = metrics.get('processing_time', 0)
        expected_time = metrics.get('expected_processing_time', 1)
        
        # Score decreases if processing takes longer than expected
        if expected_time == 0:
            return 100.0
        
        time_ratio = processing_time / expected_time
        
        if time_ratio <= 1:
            return 100.0
        elif time_ratio <= 2:
            return 80.0
        elif time_ratio <= 3:
            return 60.0
        else:
            return 40.0
    
    def _calculate_validity_score(self, metrics: Dict[str, Any], content_type: Optional[str]) -> float:
        """Calculate validity dimension score"""        
        valid_records = metrics.get('valid_records', 0)
        total_records = metrics.get('total_records', 1)
        
        if total_records == 0:
            return 100.0
        
        validity = (valid_records / total_records) * 100
        return min(100, validity)
    
    def _calculate_uniqueness_score(self, metrics: Dict[str, Any], content_type: Optional[str]) -> float:
        """Calculate uniqueness dimension score"""        
        unique_records = metrics.get('unique_records', 0)
        total_records = metrics.get('total_records', 1)
        
        if total_records == 0:
            return 100.0
        
        uniqueness = (unique_records / total_records) * 100
        return min(100, uniqueness)
    
    def _calculate_integrity_score(self, metrics: Dict[str, Any], content_type: Optional[str]) -> float:
        """Calculate integrity dimension score"""        
        checksum_valid = metrics.get('checksum_valid', True)
        structure_valid = metrics.get('structure_valid', True)
        reference_valid = metrics.get('reference_valid', True)
        
        # Binary scoring for integrity checks
        score = 0
        if checksum_valid:
            score += 40
        if structure_valid:
            score += 30
        if reference_valid:
            score += 30
        
        return min(100, score)
    
    def _calculate_compliance_score(self, metrics: Dict[str, Any], content_type: Optional[str]) -> float:
        """Calculate compliance dimension score"""        
        compliance_checks = metrics.get('compliance_checks', {})
        
        if not compliance_checks:
            return 100.0
        
        passed_checks = sum(1 for check in compliance_checks.values() if check)
        total_checks = len(compliance_checks)
        
        compliance = (passed_checks / total_checks) * 100
        return min(100, compliance)
    
    def create_quality_score(
        self,
        dimension_scores: Dict[str, float],
        content_type: Optional[str] = None,
        sample_size: int = 1,
        calculation_method: str = "weighted_average",
        metadata: Optional[Dict[str, Any]] = None
    ) -> QualityScore:
        """        Create a comprehensive quality score object.
        
        Args:
            dimension_scores: Scores for each dimension
            content_type: Optional content type
            sample_size: Size of the sample evaluated
            calculation_method: Method used for calculation
            metadata: Optional additional metadata
            
        Returns:
            QualityScore object
        """        
        # Calculate overall score
        overall_score = self.calculate_overall_score(dimension_scores, content_type)
        
        # Calculate confidence level
        confidence_level = self._calculate_confidence_level(dimension_scores, sample_size)
        
        quality_score = QualityScore(
            overall_score=overall_score,
            dimension_scores=dimension_scores.copy(),
            confidence_level=confidence_level,
            sample_size=sample_size,
            calculation_method=calculation_method,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        # Store in history
        self.metrics_history.append(quality_score)
        
        return quality_score
    
    def _calculate_confidence_level(
        self,
        dimension_scores: Dict[str, float],
        sample_size: int
    ) -> float:
        """Calculate confidence level for the quality score"""        
        # Base confidence on sample size
        if sample_size >= 1000:
            base_confidence = 95.0
        elif sample_size >= 100:
            base_confidence = 85.0
        elif sample_size >= 10:
            base_confidence = 75.0
        else:
            base_confidence = 60.0
        
        # Adjust based on score variance
        scores = list(dimension_scores.values())
        if len(scores) > 1:
            score_variance = statistics.variance(scores)
            variance_penalty = min(20, score_variance / 5)
            base_confidence -= variance_penalty
        
        return max(50.0, min(100.0, base_confidence))
    
    def analyze_quality_trend(
        self,
        timeframe: timedelta = timedelta(days=7)
    ) -> QualityTrend:
        """        Analyze quality trends over specified timeframe.
        
        Args:
            timeframe: Time period for trend analysis
            
        Returns:
            QualityTrend object with analysis results
        """        
        cutoff_time = datetime.utcnow() - timeframe
        
        # Filter historical scores within timeframe
        recent_scores = [
            score for score in self.metrics_history
            if score.timestamp > cutoff_time
        ]
        
        trend = QualityTrend()
        
        if len(recent_scores) < 2:
            return trend
        
        # Extract time series data
        trend.time_series = [
            (score.timestamp, score.overall_score)
            for score in recent_scores
        ]
        
        # Sort by timestamp
        trend.time_series.sort(key=lambda x: x[0])
        
        # Calculate trend direction and strength
        scores = [score for _, score in trend.time_series]
        
        if len(scores) >= 2:
            first_half = scores[:len(scores)//2]
            second_half = scores[len(scores)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            change = second_avg - first_avg
            change_percentage = (change / first_avg) * 100 if first_avg > 0 else 0
            
            trend.change_rate = round(change_percentage, 2)
            
            # Determine trend direction
            if abs(change_percentage) < 2:
                trend.trend_direction = "stable"
                trend.trend_strength = 10.0
            elif change_percentage > 0:
                trend.trend_direction = "improving"
                trend.trend_strength = min(100.0, abs(change_percentage) * 5)
            else:
                trend.trend_direction = "declining"
                trend.trend_strength = min(100.0, abs(change_percentage) * 5)
            
            # Calculate prediction confidence
            trend.prediction_confidence = min(95.0, len(scores) * 10)
        
        return trend
    
    async def get_metrics(
        self,
        timeframe: Optional[timedelta] = None,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """        Get comprehensive quality metrics.
        
        Args:
            timeframe: Time period for metrics
            content_type: Filter by content type
            
        Returns:
            Comprehensive metrics dictionary
        """        
        if timeframe is None:
            timeframe = timedelta(hours=24)
        
        cutoff_time = datetime.utcnow() - timeframe
        
        # Filter scores
        filtered_scores = [
            score for score in self.metrics_history
            if score.timestamp > cutoff_time
        ]
        
        if content_type:
            filtered_scores = [
                score for score in filtered_scores
                if score.metadata.get('content_type') == content_type
            ]
        
        if not filtered_scores:
            return {"message": "No metrics available for specified criteria"}
        
        # Calculate aggregate metrics
        overall_scores = [score.overall_score for score in filtered_scores]
        
        metrics = {
            'timeframe_hours': timeframe.total_seconds() / 3600,
            'content_type': content_type,
            'total_assessments': len(filtered_scores),
            'average_score': round(statistics.mean(overall_scores), 2),
            'median_score': round(statistics.median(overall_scores), 2),
            'min_score': min(overall_scores),
            'max_score': max(overall_scores),
            'score_distribution': self._calculate_score_distribution(overall_scores),
            'trend_analysis': self.analyze_quality_trend(timeframe),
            'benchmarks': self.benchmarks.get(content_type) if content_type else self.benchmarks
        }
        
        # Add dimension-specific metrics
        if filtered_scores:
            dimension_metrics = {}
            for dimension in QualityDimension:
                dim_scores = []
                for score in filtered_scores:
                    if dimension.value in score.dimension_scores:
                        dim_scores.append(score.dimension_scores[dimension.value])
                
                if dim_scores:
                    dimension_metrics[dimension.value] = {
                        'average': round(statistics.mean(dim_scores), 2),
                        'median': round(statistics.median(dim_scores), 2),
                        'min': min(dim_scores),
                        'max': max(dim_scores)
                    }
            
            metrics['dimension_metrics'] = dimension_metrics
        
        return metrics
    
    def _calculate_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate score distribution by quality levels"""        
        distribution = {
            'excellent': 0,  # 95-100
            'good': 0,       # 85-94
            'acceptable': 0, # 70-84
            'poor': 0,       # 50-69
            'critical': 0    # 0-49
        }
        
        for score in scores:
            if score >= 95:
                distribution['excellent'] += 1
            elif score >= 85:
                distribution['good'] += 1
            elif score >= 70:
                distribution['acceptable'] += 1
            elif score >= 50:
                distribution['poor'] += 1
            else:
                distribution['critical'] += 1
        
        return distribution
