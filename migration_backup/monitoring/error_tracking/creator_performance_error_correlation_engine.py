"""
Creator Performance Error Correlation Engine - Enterprise Creator Economy Platform
Advanced correlation engine between creator performance metrics and error patterns

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import math

logger = logging.getLogger(__name__)


class PerformanceMetricType(Enum):
    """Types de métriques performance"""
    CONTENT_VIEWS = "content_views"
    ENGAGEMENT_RATE = "engagement_rate"
    REVENUE_GENERATED = "revenue_generated"
    UPLOAD_FREQUENCY = "upload_frequency"
    AUDIENCE_GROWTH = "audience_growth"
    CONTENT_QUALITY_SCORE = "content_quality_score"
    COLLABORATION_SUCCESS = "collaboration_success"
    MONETIZATION_EFFICIENCY = "monetization_efficiency"
    PLATFORM_REACH = "platform_reach"
    CREATOR_SATISFACTION = "creator_satisfaction"


class CorrelationStrength(Enum):
    """Force de corrélation"""
    VERY_WEAK = "very_weak"      # 0.0 - 0.2
    WEAK = "weak"                # 0.2 - 0.4
    MODERATE = "moderate"        # 0.4 - 0.6
    STRONG = "strong"            # 0.6 - 0.8
    VERY_STRONG = "very_strong"  # 0.8 - 1.0


class TrendDirection(Enum):
    """Direction tendance"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"


@dataclass
class PerformanceMetric:
    """Métrique performance créateur"""
    creator_id: str
    metric_type: PerformanceMetricType
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 1.0
    trend_indicator: Optional[TrendDirection] = None


@dataclass
class ErrorPerformanceCorrelation:
    """Corrélation erreur-performance"""
    correlation_id: str
    creator_id: str
    error_type: str
    performance_metric: PerformanceMetricType
    correlation_coefficient: float
    correlation_strength: CorrelationStrength
    p_value: float
    confidence_level: float
    sample_size: int
    time_period: Dict[str, datetime]
    lag_time_hours: float
    causal_direction: str  # error_to_performance, performance_to_error, bidirectional
    impact_magnitude: float
    statistical_significance: bool


@dataclass
class PerformanceImpactAssessment:
    """Assessment impact performance"""
    assessment_id: str
    creator_id: str
    error_event_id: str
    pre_error_metrics: Dict[str, float]
    post_error_metrics: Dict[str, float]
    impact_percentage: Dict[str, float]
    recovery_time_hours: Optional[float]
    long_term_effects: Dict[str, Any]
    recommended_actions: List[str]


@dataclass
class PerformancePrediction:
    """Prédiction performance basée erreurs"""
    prediction_id: str
    creator_id: str
    predicted_metric: PerformanceMetricType
    current_value: float
    predicted_value: float
    prediction_confidence: float
    time_horizon_hours: int
    contributing_factors: List[str]
    risk_factors: List[str]
    mitigation_strategies: List[str]


class CreatorPerformanceErrorCorrelationEngine:
    """
    📊 MOTEUR CORRÉLATION ERREURS PERFORMANCE CRÉATEURS ENTERPRISE
    
    Architecture corrélation Backend Senior avec:
    - Corrélation statistique avancée erreurs-performance
    - Prédiction impact performance temps réel
    - Analysis causal patterns intelligente
    - Optimisation performance basée erreurs
    """
    
    def __init__(self):
        """Initialize Creator Performance Error Correlation Engine"""
        self.performance_metrics: Dict[str, List[PerformanceMetric]] = defaultdict(list)
        self.error_events: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.correlations: Dict[str, ErrorPerformanceCorrelation] = {}
        self.impact_assessments: Dict[str, PerformanceImpactAssessment] = {}
        self.performance_predictions: Dict[str, List[PerformancePrediction]] = defaultdict(list)
        self.correlation_cache: Dict[str, Any] = {}
        self.ml_models: Dict[str, Any] = {}
        self.statistical_cache: Dict[str, Any] = {}
        
        # Configuration moteur corrélation
        self.config = {
            'max_metrics_history': 50000,
            'correlation_window_hours': 168,  # 7 days
            'min_sample_size': 10,
            'significance_threshold': 0.05,
            'correlation_update_interval': 3600,  # 1 hour
            'prediction_horizon_hours': 72,  # 3 days
            'impact_assessment_enabled': True,
            'real_time_correlation': True,
            'ml_prediction_enabled': True
        }
        
        # Initialize correlation models
        self._initialize_correlation_models()
        
        logger.info("Creator Performance Error Correlation Engine initialized")
    
    def _initialize_correlation_models(self):
        """Initialize correlation and prediction models"""
        try:
            # Initialize basic statistical models
            self.ml_models = {
                'linear_regression': {},
                'correlation_matrix': {},
                'time_series_analysis': {},
                'causal_inference': {}
            }
            
            # Initialize correlation calculation methods
            self.correlation_methods = {
                'pearson': self._calculate_pearson_correlation,
                'spearman': self._calculate_spearman_correlation,
                'kendall': self._calculate_kendall_correlation,
                'time_lagged': self._calculate_time_lagged_correlation
            }
            
        except Exception as e:
            logger.error(f"Error initializing correlation models: {e}")
    
    async def record_performance_metric(self,
                                      creator_id: str,
                                      metric_type: PerformanceMetricType,
                                      value: float,
                                      metadata: Optional[Dict[str, Any]] = None,
                                      auto_correlate: bool = True) -> str:
        """
        Record performance metric for creator
        
        Args:
            creator_id: ID créateur
            metric_type: Type métrique
            value: Valeur métrique
            metadata: Métadonnées optionnelles
            auto_correlate: Corrélation automatique
            
        Returns:
            Metric ID
        """
        try:
            # Create performance metric
            metric = PerformanceMetric(
                creator_id=creator_id,
                metric_type=metric_type,
                value=value,
                timestamp=datetime.utcnow(),
                metadata=metadata or {},
                quality_score=await self._assess_metric_quality(value, metric_type),
                trend_indicator=await self._determine_trend_indicator(creator_id, metric_type, value)
            )
            
            # Store metric
            self.performance_metrics[creator_id].append(metric)
            
            # Maintain history limit
            if len(self.performance_metrics[creator_id]) > self.config['max_metrics_history']:
                self.performance_metrics[creator_id] = self.performance_metrics[creator_id][-self.config['max_metrics_history']:]
            
            # Auto-correlate if enabled
            if auto_correlate:
                await self._update_correlations(creator_id)
                await self._assess_immediate_impact(creator_id, metric)
            
            metric_id = f"metric_{creator_id}_{metric.timestamp.strftime('%Y%m%d_%H%M%S_%f')}"
            
            logger.debug(f"Performance metric recorded: {metric_id}")
            return metric_id
            
        except Exception as e:
            logger.error(f"Error recording performance metric: {e}")
            raise
    
    async def record_error_event(self,
                                creator_id: str,
                                error_event: Dict[str, Any],
                                auto_correlate: bool = True) -> str:
        """
        Record error event for correlation analysis
        
        Args:
            creator_id: ID créateur
            error_event: Événement erreur
            auto_correlate: Corrélation automatique
            
        Returns:
            Event ID
        """
        try:
            # Enrich error event with timestamp if not present
            if 'timestamp' not in error_event:
                error_event['timestamp'] = datetime.utcnow()
            elif isinstance(error_event['timestamp'], str):
                error_event['timestamp'] = datetime.fromisoformat(error_event['timestamp'])
            
            # Store error event
            self.error_events[creator_id].append(error_event)
            
            # Maintain history limit
            if len(self.error_events[creator_id]) > self.config['max_metrics_history']:
                self.error_events[creator_id] = self.error_events[creator_id][-self.config['max_metrics_history']:]
            
            # Auto-correlate if enabled
            if auto_correlate:
                await self._update_correlations(creator_id)
                await self._assess_error_impact(creator_id, error_event)
            
            event_id = f"error_{creator_id}_{error_event['timestamp'].strftime('%Y%m%d_%H%M%S_%f')}"
            
            logger.debug(f"Error event recorded for correlation: {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Error recording error event: {e}")
            raise
    
    async def _assess_metric_quality(self, value: float, metric_type: PerformanceMetricType) -> float:
        """Assess quality of performance metric"""
        try:
            quality_score = 1.0
            
            # Check for reasonable value ranges
            if metric_type == PerformanceMetricType.ENGAGEMENT_RATE:
                if 0 <= value <= 1:
                    quality_score = 1.0
                elif value > 1:
                    quality_score = 0.8  # Possibly percentage instead of ratio
                else:
                    quality_score = 0.5  # Negative engagement rate is suspicious
            
            elif metric_type == PerformanceMetricType.CONTENT_QUALITY_SCORE:
                if 0 <= value <= 10:
                    quality_score = 1.0
                else:
                    quality_score = 0.6  # Out of expected range
            
            elif metric_type in [PerformanceMetricType.CONTENT_VIEWS, PerformanceMetricType.REVENUE_GENERATED]:
                if value >= 0:
                    quality_score = 1.0
                else:
                    quality_score = 0.3  # Negative values are suspicious
            
            return quality_score
            
        except Exception as e:
            logger.error(f"Error assessing metric quality: {e}")
            return 0.5
    
    async def _determine_trend_indicator(self,
                                       creator_id: str,
                                       metric_type: PerformanceMetricType,
                                       current_value: float) -> Optional[TrendDirection]:
        """Determine trend indicator for metric"""
        try:
            creator_metrics = self.performance_metrics.get(creator_id, [])
            same_type_metrics = [m for m in creator_metrics if m.metric_type == metric_type]
            
            if len(same_type_metrics) < 3:
                return None
            
            # Get last few values
            recent_values = [m.value for m in same_type_metrics[-5:]]
            recent_values.append(current_value)
            
            # Calculate trend
            if len(recent_values) >= 3:
                # Simple linear regression to determine trend
                x = list(range(len(recent_values)))
                y = recent_values
                
                slope, _, r_value, _, _ = stats.linregress(x, y)
                
                # Determine trend direction
                if abs(r_value) < 0.3:  # Low correlation with time
                    return TrendDirection.VOLATILE
                elif slope > 0.1:
                    return TrendDirection.IMPROVING
                elif slope < -0.1:
                    return TrendDirection.DECLINING
                else:
                    return TrendDirection.STABLE
            
            return None
            
        except Exception as e:
            logger.error(f"Error determining trend indicator: {e}")
            return None
    
    async def _update_correlations(self, creator_id: str):
        """Update correlations for creator"""
        try:
            creator_metrics = self.performance_metrics.get(creator_id, [])
            creator_errors = self.error_events.get(creator_id, [])
            
            if len(creator_metrics) < self.config['min_sample_size'] or len(creator_errors) < 3:
                return
            
            # Calculate correlations for each metric type and error type combination
            metric_types = set(m.metric_type for m in creator_metrics)
            error_types = set(e.get('error_type', 'unknown') for e in creator_errors)
            
            for metric_type in metric_types:
                for error_type in error_types:
                    correlation = await self._calculate_error_performance_correlation(
                        creator_id, metric_type, error_type
                    )
                    
                    if correlation and correlation.statistical_significance:
                        correlation_key = f"{creator_id}_{metric_type.value}_{error_type}"
                        self.correlations[correlation_key] = correlation
            
            logger.debug(f"Correlations updated for creator: {creator_id}")
            
        except Exception as e:
            logger.error(f"Error updating correlations: {e}")
    
    async def _calculate_error_performance_correlation(self,
                                                     creator_id: str,
                                                     metric_type: PerformanceMetricType,
                                                     error_type: str) -> Optional[ErrorPerformanceCorrelation]:
        """Calculate correlation between errors and performance"""
        try:
            # Get relevant data
            creator_metrics = [m for m in self.performance_metrics.get(creator_id, []) 
                             if m.metric_type == metric_type]
            creator_errors = [e for e in self.error_events.get(creator_id, []) 
                            if e.get('error_type') == error_type]
            
            if len(creator_metrics) < self.config['min_sample_size'] or len(creator_errors) < 3:
                return None
            
            # Prepare time series data
            correlation_window = timedelta(hours=self.config['correlation_window_hours'])
            end_time = datetime.utcnow()
            start_time = end_time - correlation_window
            
            # Filter data to correlation window
            recent_metrics = [m for m in creator_metrics if start_time <= m.timestamp <= end_time]
            recent_errors = [e for e in creator_errors if start_time <= e['timestamp'] <= end_time]
            
            if len(recent_metrics) < self.config['min_sample_size']:
                return None
            
            # Calculate correlation using multiple methods
            correlations = await self._calculate_multiple_correlations(recent_metrics, recent_errors)
            
            if not correlations:
                return None
            
            # Use Pearson correlation as primary
            primary_correlation = correlations.get('pearson', {})
            
            if not primary_correlation:
                return None
            
            # Determine correlation strength
            corr_coef = abs(primary_correlation['correlation'])
            if corr_coef >= 0.8:
                strength = CorrelationStrength.VERY_STRONG
            elif corr_coef >= 0.6:
                strength = CorrelationStrength.STRONG
            elif corr_coef >= 0.4:
                strength = CorrelationStrength.MODERATE
            elif corr_coef >= 0.2:
                strength = CorrelationStrength.WEAK
            else:
                strength = CorrelationStrength.VERY_WEAK
            
            # Determine causal direction (simplified)
            causal_direction = await self._determine_causal_direction(recent_metrics, recent_errors)
            
            # Calculate impact magnitude
            impact_magnitude = await self._calculate_impact_magnitude(recent_metrics, recent_errors)
            
            # Create correlation object
            correlation = ErrorPerformanceCorrelation(
                correlation_id=f"corr_{creator_id}_{metric_type.value}_{error_type}_{datetime.utcnow().strftime('%Y%m%d')}",
                creator_id=creator_id,
                error_type=error_type,
                performance_metric=metric_type,
                correlation_coefficient=primary_correlation['correlation'],
                correlation_strength=strength,
                p_value=primary_correlation['p_value'],
                confidence_level=1 - primary_correlation['p_value'],
                sample_size=len(recent_metrics),
                time_period={'start': start_time, 'end': end_time},
                lag_time_hours=primary_correlation.get('lag_hours', 0),
                causal_direction=causal_direction,
                impact_magnitude=impact_magnitude,
                statistical_significance=primary_correlation['p_value'] < self.config['significance_threshold']
            )
            
            return correlation
            
        except Exception as e:
            logger.error(f"Error calculating error-performance correlation: {e}")
            return None
    
    async def _calculate_multiple_correlations(self,
                                             metrics: List[PerformanceMetric],
                                             errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate correlations using multiple methods"""
        try:
            correlations = {}
            
            # Prepare time series
            metric_values, error_indicators = await self._prepare_time_series(metrics, errors)
            
            if len(metric_values) != len(error_indicators) or len(metric_values) < 3:
                return correlations
            
            # Pearson correlation
            pearson_result = await self._calculate_pearson_correlation(metric_values, error_indicators)
            if pearson_result:
                correlations['pearson'] = pearson_result
            
            # Spearman correlation (rank-based)
            spearman_result = await self._calculate_spearman_correlation(metric_values, error_indicators)
            if spearman_result:
                correlations['spearman'] = spearman_result
            
            # Time-lagged correlation
            lagged_result = await self._calculate_time_lagged_correlation(metrics, errors)
            if lagged_result:
                correlations['time_lagged'] = lagged_result
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error calculating multiple correlations: {e}")
            return {}
    
    async def _prepare_time_series(self,
                                 metrics: List[PerformanceMetric],
                                 errors: List[Dict[str, Any]]) -> Tuple[List[float], List[int]]:
        """Prepare aligned time series for correlation analysis"""
        try:
            # Create hourly buckets
            if not metrics:
                return [], []
            
            start_time = min(m.timestamp for m in metrics)
            end_time = max(m.timestamp for m in metrics)
            
            # Create hourly intervals
            current_time = start_time.replace(minute=0, second=0, microsecond=0)
            intervals = []
            
            while current_time <= end_time:
                intervals.append(current_time)
                current_time += timedelta(hours=1)
            
            # Aggregate metrics and errors by hour
            metric_values = []
            error_indicators = []
            
            for interval_start in intervals:
                interval_end = interval_start + timedelta(hours=1)
                
                # Get metrics in this interval
                interval_metrics = [m for m in metrics 
                                  if interval_start <= m.timestamp < interval_end]
                
                # Get errors in this interval
                interval_errors = [e for e in errors 
                                 if interval_start <= e['timestamp'] < interval_end]
                
                # Calculate average metric value for interval
                if interval_metrics:
                    avg_metric = statistics.mean(m.value for m in interval_metrics)
                    metric_values.append(avg_metric)
                else:
                    # Use previous value or skip
                    if metric_values:
                        metric_values.append(metric_values[-1])
                    else:
                        metric_values.append(0.0)
                
                # Count errors in interval
                error_count = len(interval_errors)
                error_indicators.append(error_count)
            
            return metric_values, error_indicators
            
        except Exception as e:
            logger.error(f"Error preparing time series: {e}")
            return [], []
    
    async def _calculate_pearson_correlation(self,
                                           metric_values: List[float],
                                           error_indicators: List[int]) -> Optional[Dict[str, Any]]:
        """Calculate Pearson correlation coefficient"""
        try:
            if len(metric_values) != len(error_indicators) or len(metric_values) < 3:
                return None
            
            # Calculate correlation manually
            n = len(metric_values)
            mean_x = statistics.mean(metric_values)
            mean_y = statistics.mean(error_indicators)
            
            numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(metric_values, error_indicators))
            sum_sq_x = sum((x - mean_x) ** 2 for x in metric_values)
            sum_sq_y = sum((y - mean_y) ** 2 for y in error_indicators)
            
            denominator = math.sqrt(sum_sq_x * sum_sq_y)
            
            if denominator == 0:
                return None
            
            correlation = numerator / denominator
            
            # Simple p-value approximation
            t_stat = correlation * math.sqrt((n - 2) / (1 - correlation ** 2)) if abs(correlation) < 1 else 0
            p_value = 0.05 if abs(t_stat) > 2 else 0.1  # Simplified
            
            return {
                'correlation': correlation,
                'p_value': p_value,
                'method': 'pearson'
            }
            
        except Exception as e:
            logger.error(f"Error calculating Pearson correlation: {e}")
            return None
    
    async def _calculate_spearman_correlation(self,
                                            metric_values: List[float],
                                            error_indicators: List[int]) -> Optional[Dict[str, Any]]:
        """Calculate Spearman rank correlation"""
        try:
            if len(metric_values) != len(error_indicators) or len(metric_values) < 3:
                return None
            
            # Convert to ranks
            def rank_values(values):
                sorted_values = sorted(set(values))
                rank_map = {v: i + 1 for i, v in enumerate(sorted_values)}
                return [rank_map[v] for v in values]
            
            ranked_x = rank_values(metric_values)
            ranked_y = rank_values(error_indicators)
            
            # Calculate Pearson correlation on ranks
            result = await self._calculate_pearson_correlation(ranked_x, ranked_y)
            if result:
                result['method'] = 'spearman'
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating Spearman correlation: {e}")
            return None
    
    async def _calculate_kendall_correlation(self,
                                           metric_values: List[float],
                                           error_indicators: List[int]) -> Optional[Dict[str, Any]]:
        """Calculate Kendall tau correlation"""
        try:
            if len(metric_values) != len(error_indicators) or len(metric_values) < 3:
                return None
            
            # Simplified Kendall tau calculation
            n = len(metric_values)
            concordant = 0
            discordant = 0
            
            for i in range(n):
                for j in range(i + 1, n):
                    sign_x = 1 if metric_values[i] < metric_values[j] else -1 if metric_values[i] > metric_values[j] else 0
                    sign_y = 1 if error_indicators[i] < error_indicators[j] else -1 if error_indicators[i] > error_indicators[j] else 0
                    
                    if sign_x * sign_y > 0:
                        concordant += 1
                    elif sign_x * sign_y < 0:
                        discordant += 1
            
            total_pairs = n * (n - 1) // 2
            correlation = (concordant - discordant) / total_pairs if total_pairs > 0 else 0
            
            # Simple p-value approximation
            p_value = 0.05 if abs(correlation) > 0.3 else 0.1
            
            return {
                'correlation': correlation,
                'p_value': p_value,
                'method': 'kendall'
            }
            
        except Exception as e:
            logger.error(f"Error calculating Kendall correlation: {e}")
            return None
    
    async def _calculate_time_lagged_correlation(self,
                                               metrics: List[PerformanceMetric],
                                               errors: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Calculate time-lagged correlation"""
        try:
            # Try different lag times (0-48 hours)
            best_correlation = 0
            best_lag = 0
            best_p_value = 1.0
            
            for lag_hours in range(0, 49, 2):  # Test every 2 hours
                # Shift error times by lag
                shifted_errors = []
                for error in errors:
                    shifted_error = error.copy()
                    shifted_error['timestamp'] = error['timestamp'] + timedelta(hours=lag_hours)
                    shifted_errors.append(shifted_error)
                
                # Calculate correlation with shifted errors
                metric_values, error_indicators = await self._prepare_time_series(metrics, shifted_errors)
                
                if len(metric_values) >= 3:
                    correlation, p_value = stats.pearsonr(metric_values, error_indicators)
                    
                    if abs(correlation) > abs(best_correlation) and p_value < 0.1:
                        best_correlation = correlation
                        best_lag = lag_hours
                        best_p_value = p_value
            
            if abs(best_correlation) > 0.1:  # Minimum threshold
                return {
                    'correlation': best_correlation,
                    'p_value': best_p_value,
                    'lag_hours': best_lag,
                    'method': 'time_lagged'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating time-lagged correlation: {e}")
            return None
    
    async def _determine_causal_direction(self,
                                        metrics: List[PerformanceMetric],
                                        errors: List[Dict[str, Any]]) -> str:
        """Determine causal direction between errors and performance"""
        try:
            # Simplified causal analysis using temporal ordering
            error_to_perf_correlation = 0
            perf_to_error_correlation = 0
            
            # Test error -> performance direction
            lagged_result = await self._calculate_time_lagged_correlation(metrics, errors)
            if lagged_result and lagged_result['lag_hours'] > 0:
                error_to_perf_correlation = abs(lagged_result['correlation'])
            
            # Test performance -> error direction (reverse lag)
            reversed_errors = []
            for error in errors:
                reversed_error = error.copy()
                reversed_error['timestamp'] = error['timestamp'] - timedelta(hours=12)
                reversed_errors.append(reversed_error)
            
            reverse_result = await self._calculate_time_lagged_correlation(metrics, reversed_errors)
            if reverse_result:
                perf_to_error_correlation = abs(reverse_result['correlation'])
            
            # Determine direction
            if error_to_perf_correlation > perf_to_error_correlation + 0.1:
                return "error_to_performance"
            elif perf_to_error_correlation > error_to_perf_correlation + 0.1:
                return "performance_to_error"
            else:
                return "bidirectional"
            
        except Exception as e:
            logger.error(f"Error determining causal direction: {e}")
            return "unknown"
    
    async def _calculate_impact_magnitude(self,
                                        metrics: List[PerformanceMetric],
                                        errors: List[Dict[str, Any]]) -> float:
        """Calculate impact magnitude of errors on performance"""
        try:
            if not metrics or not errors:
                return 0.0
            
            # Calculate average performance before and after errors
            impact_magnitudes = []
            
            for error in errors:
                error_time = error['timestamp']
                
                # Get metrics before error (24 hours before)
                before_start = error_time - timedelta(hours=24)
                before_end = error_time
                before_metrics = [m for m in metrics 
                                if before_start <= m.timestamp < before_end]
                
                # Get metrics after error (24 hours after)
                after_start = error_time
                after_end = error_time + timedelta(hours=24)
                after_metrics = [m for m in metrics 
                               if after_start <= m.timestamp < after_end]
                
                if before_metrics and after_metrics:
                    before_avg = statistics.mean(m.value for m in before_metrics)
                    after_avg = statistics.mean(m.value for m in after_metrics)
                    
                    if before_avg > 0:
                        impact = abs(after_avg - before_avg) / before_avg
                        impact_magnitudes.append(impact)
            
            return statistics.mean(impact_magnitudes) if impact_magnitudes else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating impact magnitude: {e}")
            return 0.0
    
    async def _assess_immediate_impact(self,
                                     creator_id: str,
                                     metric: PerformanceMetric):
        """Assess immediate impact of new metric"""
        try:
            # Get recent errors (last 24 hours)
            recent_time = metric.timestamp - timedelta(hours=24)
            recent_errors = [e for e in self.error_events.get(creator_id, []) 
                           if e['timestamp'] >= recent_time]
            
            if not recent_errors:
                return
            
            # Check for significant performance drops
            creator_metrics = [m for m in self.performance_metrics.get(creator_id, []) 
                             if m.metric_type == metric.metric_type]
            
            if len(creator_metrics) >= 2:
                previous_metric = creator_metrics[-2]
                
                # Calculate performance change
                if previous_metric.value > 0:
                    change_percentage = (metric.value - previous_metric.value) / previous_metric.value
                    
                    # If significant drop (>20%) and recent errors
                    if change_percentage < -0.2 and recent_errors:
                        await self._create_impact_assessment(creator_id, metric, recent_errors[-1], change_percentage)
            
        except Exception as e:
            logger.error(f"Error assessing immediate impact: {e}")
    
    async def _assess_error_impact(self,
                                 creator_id: str,
                                 error_event: Dict[str, Any]):
        """Assess impact of error event on performance"""
        try:
            # Get recent metrics to establish baseline
            baseline_end = error_event['timestamp']
            baseline_start = baseline_end - timedelta(hours=24)
            
            baseline_metrics = {}
            for metric_type in PerformanceMetricType:
                type_metrics = [m for m in self.performance_metrics.get(creator_id, []) 
                              if m.metric_type == metric_type and baseline_start <= m.timestamp < baseline_end]
                
                if type_metrics:
                    baseline_metrics[metric_type.value] = statistics.mean(m.value for m in type_metrics)
            
            if baseline_metrics:
                # Schedule impact assessment for later (after post-error data available)
                error_event['impact_assessment_scheduled'] = True
                logger.debug(f"Impact assessment scheduled for error: {error_event.get('error_type', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error assessing error impact: {e}")
    
    async def _create_impact_assessment(self,
                                      creator_id: str,
                                      metric: PerformanceMetric,
                                      error_event: Dict[str, Any],
                                      impact_percentage: float):
        """Create impact assessment"""
        try:
            assessment_id = f"impact_{creator_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Get pre-error metrics
            pre_error_time = error_event['timestamp'] - timedelta(hours=24)
            pre_error_metrics = {}
            
            for metric_type in PerformanceMetricType:
                type_metrics = [m for m in self.performance_metrics.get(creator_id, []) 
                              if m.metric_type == metric_type and m.timestamp >= pre_error_time and m.timestamp < error_event['timestamp']]
                
                if type_metrics:
                    pre_error_metrics[metric_type.value] = statistics.mean(m.value for m in type_metrics)
            
            # Current metrics (post-error)
            post_error_metrics = {metric.metric_type.value: metric.value}
            
            # Calculate impact percentages
            impact_percentages = {}
            if metric.metric_type.value in pre_error_metrics:
                pre_value = pre_error_metrics[metric.metric_type.value]
                if pre_value > 0:
                    impact_percentages[metric.metric_type.value] = (metric.value - pre_value) / pre_value
            
            # Generate recommendations
            recommendations = await self._generate_impact_recommendations(impact_percentages, error_event)
            
            # Create assessment
            assessment = PerformanceImpactAssessment(
                assessment_id=assessment_id,
                creator_id=creator_id,
                error_event_id=error_event.get('error_id', 'unknown'),
                pre_error_metrics=pre_error_metrics,
                post_error_metrics=post_error_metrics,
                impact_percentage=impact_percentages,
                recovery_time_hours=None,  # To be calculated later
                long_term_effects={},
                recommended_actions=recommendations
            )
            
            self.impact_assessments[assessment_id] = assessment
            
            logger.info(f"Impact assessment created: {assessment_id}")
            
        except Exception as e:
            logger.error(f"Error creating impact assessment: {e}")
    
    async def _generate_impact_recommendations(self,
                                             impact_percentages: Dict[str, float],
                                             error_event: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on impact assessment"""
        try:
            recommendations = []
            
            # Analyze impact severity
            max_impact = max(abs(impact) for impact in impact_percentages.values()) if impact_percentages else 0
            
            if max_impact > 0.5:  # >50% impact
                recommendations.extend([
                    "URGENT: Implement immediate recovery measures",
                    "Escalate to creator success team",
                    "Consider emergency content promotion"
                ])
            elif max_impact > 0.2:  # >20% impact
                recommendations.extend([
                    "Monitor performance closely",
                    "Implement targeted recovery strategy",
                    "Review content strategy"
                ])
            
            # Error-specific recommendations
            error_type = error_event.get('error_type', 'unknown')
            
            if error_type in ['payment_error', 'monetization_error']:
                recommendations.extend([
                    "Review monetization settings",
                    "Check payment processor status",
                    "Verify revenue tracking accuracy"
                ])
            elif error_type in ['upload_error', 'content_error']:
                recommendations.extend([
                    "Check content upload pipeline",
                    "Verify content processing status",
                    "Review content quality standards"
                ])
            elif error_type in ['engagement_error', 'algorithm_error']:
                recommendations.extend([
                    "Analyze engagement patterns",
                    "Review content optimization strategies",
                    "Check algorithm updates impact"
                ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating impact recommendations: {e}")
            return []
    
    async def predict_performance_impact(self,
                                       creator_id: str,
                                       error_scenarios: List[Dict[str, Any]],
                                       time_horizon_hours: int = 72) -> List[PerformancePrediction]:
        """
        Predict performance impact of potential error scenarios
        
        Args:
            creator_id: ID créateur
            error_scenarios: Scénarios erreurs à analyser
            time_horizon_hours: Horizon prédiction
            
        Returns:
            List of performance predictions
        """
        try:
            predictions = []
            
            for scenario in error_scenarios:
                for metric_type in PerformanceMetricType:
                    prediction = await self._predict_metric_impact(
                        creator_id, scenario, metric_type, time_horizon_hours
                    )
                    
                    if prediction:
                        predictions.append(prediction)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting performance impact: {e}")
            return []
    
    async def _predict_metric_impact(self,
                                   creator_id: str,
                                   error_scenario: Dict[str, Any],
                                   metric_type: PerformanceMetricType,
                                   time_horizon_hours: int) -> Optional[PerformancePrediction]:
        """Predict impact on specific metric"""
        try:
            # Get historical correlation
            error_type = error_scenario.get('error_type', 'unknown')
            correlation_key = f"{creator_id}_{metric_type.value}_{error_type}"
            correlation = self.correlations.get(correlation_key)
            
            if not correlation or not correlation.statistical_significance:
                return None
            
            # Get current metric value
            creator_metrics = [m for m in self.performance_metrics.get(creator_id, []) 
                             if m.metric_type == metric_type]
            
            if not creator_metrics:
                return None
            
            current_value = creator_metrics[-1].value
            
            # Predict impact based on correlation and historical patterns
            predicted_impact = correlation.impact_magnitude * correlation.correlation_coefficient
            predicted_value = current_value * (1 + predicted_impact)
            
            # Calculate prediction confidence
            confidence = min(0.95, correlation.confidence_level * 0.8)  # Reduce confidence for prediction
            
            # Generate contributing factors
            contributing_factors = [
                f"Historical correlation strength: {correlation.correlation_strength.value}",
                f"Previous impact magnitude: {correlation.impact_magnitude:.2%}",
                f"Error type: {error_type}"
            ]
            
            # Generate risk factors
            risk_factors = []
            if correlation.correlation_strength in [CorrelationStrength.STRONG, CorrelationStrength.VERY_STRONG]:
                risk_factors.append("High correlation indicates significant impact risk")
            
            if correlation.impact_magnitude > 0.3:
                risk_factors.append("Historical data shows high impact magnitude")
            
            # Generate mitigation strategies
            mitigation_strategies = await self._generate_mitigation_strategies(metric_type, error_scenario)
            
            # Create prediction
            prediction = PerformancePrediction(
                prediction_id=f"pred_{creator_id}_{metric_type.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                creator_id=creator_id,
                predicted_metric=metric_type,
                current_value=current_value,
                predicted_value=predicted_value,
                prediction_confidence=confidence,
                time_horizon_hours=time_horizon_hours,
                contributing_factors=contributing_factors,
                risk_factors=risk_factors,
                mitigation_strategies=mitigation_strategies
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting metric impact: {e}")
            return None
    
    async def _generate_mitigation_strategies(self,
                                            metric_type: PerformanceMetricType,
                                            error_scenario: Dict[str, Any]) -> List[str]:
        """Generate mitigation strategies for predicted impact"""
        try:
            strategies = []
            
            # General strategies
            strategies.extend([
                "Monitor performance metrics closely",
                "Implement proactive error prevention",
                "Prepare contingency plans"
            ])
            
            # Metric-specific strategies
            if metric_type == PerformanceMetricType.CONTENT_VIEWS:
                strategies.extend([
                    "Increase content promotion budget",
                    "Optimize content for discoverability",
                    "Engage with audience more actively"
                ])
            elif metric_type == PerformanceMetricType.ENGAGEMENT_RATE:
                strategies.extend([
                    "Focus on high-engagement content types",
                    "Improve content quality standards",
                    "Optimize posting schedule"
                ])
            elif metric_type == PerformanceMetricType.REVENUE_GENERATED:
                strategies.extend([
                    "Diversify revenue streams",
                    "Review monetization strategies",
                    "Implement backup payment methods"
                ])
            
            # Error-specific strategies
            error_type = error_scenario.get('error_type', 'unknown')
            if error_type in ['upload_error', 'content_error']:
                strategies.extend([
                    "Implement redundant upload systems",
                    "Pre-validate content before upload",
                    "Use multiple content distribution channels"
                ])
            elif error_type in ['payment_error', 'monetization_error']:
                strategies.extend([
                    "Set up payment method redundancy",
                    "Monitor payment processor health",
                    "Implement revenue recovery procedures"
                ])
            
            return strategies
            
        except Exception as e:
            logger.error(f"Error generating mitigation strategies: {e}")
            return []
    
    async def get_creator_correlations(self, creator_id: str) -> List[ErrorPerformanceCorrelation]:
        """Get all correlations for a creator"""
        try:
            creator_correlations = [corr for corr in self.correlations.values() 
                                  if corr.creator_id == creator_id]
            
            # Sort by correlation strength
            creator_correlations.sort(key=lambda x: abs(x.correlation_coefficient), reverse=True)
            
            return creator_correlations
            
        except Exception as e:
            logger.error(f"Error getting creator correlations: {e}")
            return []
    
    async def get_performance_insights(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive performance insights for creator"""
        try:
            insights = {
                'creator_id': creator_id,
                'timestamp': datetime.utcnow().isoformat(),
                'correlations': [],
                'impact_assessments': [],
                'predictions': [],
                'trends': {},
                'recommendations': []
            }
            
            # Get correlations
            correlations = await self.get_creator_correlations(creator_id)
            insights['correlations'] = [asdict(corr) for corr in correlations[:10]]  # Top 10
            
            # Get impact assessments
            creator_assessments = [assessment for assessment in self.impact_assessments.values() 
                                 if assessment.creator_id == creator_id]
            insights['impact_assessments'] = [asdict(assessment) for assessment in creator_assessments[-5:]]  # Last 5
            
            # Get predictions
            creator_predictions = self.performance_predictions.get(creator_id, [])
            insights['predictions'] = [asdict(pred) for pred in creator_predictions[-5:]]  # Last 5
            
            # Get trends
            insights['trends'] = await self._calculate_performance_trends(creator_id)
            
            # Generate recommendations
            insights['recommendations'] = await self._generate_performance_recommendations(creator_id, correlations)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting performance insights: {e}")
            return {}
    
    async def _calculate_performance_trends(self, creator_id: str) -> Dict[str, Any]:
        """Calculate performance trends for creator"""
        try:
            trends = {}
            
            for metric_type in PerformanceMetricType:
                creator_metrics = [m for m in self.performance_metrics.get(creator_id, []) 
                                 if m.metric_type == metric_type]
                
                if len(creator_metrics) >= 5:  # Need minimum data points
                    recent_metrics = creator_metrics[-30:]  # Last 30 measurements
                    values = [m.value for m in recent_metrics]
                    
                    # Calculate trend
                    x = list(range(len(values)))
                    
                    # Simple linear regression
                    n = len(values)
                    mean_x = statistics.mean(x)
                    mean_y = statistics.mean(values)
                    
                    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, values))
                    denominator = sum((xi - mean_x) ** 2 for xi in x)
                    
                    slope = numerator / denominator if denominator != 0 else 0
                    
                    # Calculate R-squared
                    y_pred = [slope * xi + (mean_y - slope * mean_x) for xi in x]
                    ss_res = sum((yi - y_pred_i) ** 2 for yi, y_pred_i in zip(values, y_pred))
                    ss_tot = sum((yi - mean_y) ** 2 for yi in values)
                    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                    r_value = math.sqrt(abs(r_squared)) * (1 if slope > 0 else -1)
                    
                    trends[metric_type.value] = {
                        'slope': slope,
                        'r_squared': r_value ** 2,
                        'direction': 'improving' if slope > 0 else 'declining' if slope < 0 else 'stable',
                        'strength': 'strong' if abs(r_value) > 0.7 else 'moderate' if abs(r_value) > 0.4 else 'weak'
                    }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error calculating performance trends: {e}")
            return {}
    
    async def _generate_performance_recommendations(self,
                                                  creator_id: str,
                                                  correlations: List[ErrorPerformanceCorrelation]) -> List[str]:
        """Generate performance recommendations based on correlations"""
        try:
            recommendations = []
            
            # Analyze strongest correlations
            strong_correlations = [corr for corr in correlations 
                                 if corr.correlation_strength in [CorrelationStrength.STRONG, CorrelationStrength.VERY_STRONG]]
            
            if strong_correlations:
                recommendations.append("Focus on preventing errors with strong performance correlations")
                
                for corr in strong_correlations[:3]:  # Top 3
                    if corr.correlation_coefficient < 0:  # Negative correlation (errors hurt performance)
                        recommendations.append(f"Prioritize preventing {corr.error_type} errors - strong negative impact on {corr.performance_metric.value}")
            
            # Analyze impact magnitudes
            high_impact_correlations = [corr for corr in correlations if corr.impact_magnitude > 0.3]
            
            if high_impact_correlations:
                recommendations.append("Implement enhanced monitoring for high-impact error types")
            
            # General recommendations
            if len(correlations) > 5:
                recommendations.append("Consider implementing predictive error prevention system")
            
            if not recommendations:
                recommendations.append("Continue monitoring performance-error relationships")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating performance recommendations: {e}")
            return []
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide correlation metrics"""
        try:
            metrics = {
                'total_creators_tracked': len(self.performance_metrics),
                'total_correlations': len(self.correlations),
                'significant_correlations': len([c for c in self.correlations.values() if c.statistical_significance]),
                'strong_correlations': len([c for c in self.correlations.values() 
                                          if c.correlation_strength in [CorrelationStrength.STRONG, CorrelationStrength.VERY_STRONG]]),
                'impact_assessments': len(self.impact_assessments),
                'predictions_generated': sum(len(preds) for preds in self.performance_predictions.values()),
                'last_updated': datetime.utcnow().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}


# Global instance
performance_correlation_engine = CreatorPerformanceErrorCorrelationEngine()