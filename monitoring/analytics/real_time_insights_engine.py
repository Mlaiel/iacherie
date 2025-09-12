"""
Ainflue Platform - Real-Time Insights Engine
===========================================

Advanced real-time analytics insights engine for the Ainflue platform.
Processes streaming data to generate immediate insights, detect anomalies,
and provide actionable recommendations for content creators and marketers.

Features:
- Real-time data processing
- Anomaly detection and alerting
- Trend identification
- Performance optimization insights
- Predictive analytics
- Automated recommendations

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import statistics
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import math
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InsightType(Enum):
    """Types of real-time insights."""
    PERFORMANCE_SPIKE = "performance_spike"
    PERFORMANCE_DROP = "performance_drop"
    TRENDING_CONTENT = "trending_content"
    AUDIENCE_BEHAVIOR = "audience_behavior"
    ENGAGEMENT_ANOMALY = "engagement_anomaly"
    VIRAL_POTENTIAL = "viral_potential"
    COMPETITIVE_MOVEMENT = "competitive_movement"
    OPTIMIZATION_OPPORTUNITY = "optimization_opportunity"

class InsightPriority(Enum):
    """Priority levels for insights."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"

class AlertType(Enum):
    """Types of real-time alerts."""
    ANOMALY_DETECTED = "anomaly_detected"
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    TREND_CHANGE = "trend_change"
    OPPORTUNITY_IDENTIFIED = "opportunity_identified"
    PERFORMANCE_DEGRADATION = "performance_degradation"

@dataclass
class RealTimeMetric:
    """Real-time metric data point."""
    metric_id: str
    source: str
    metric_name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RealTimeInsight:
    """Real-time insight generated from data analysis."""
    insight_id: str
    insight_type: InsightType
    title: str
    description: str
    priority: InsightPriority
    confidence_score: float
    impact_score: float
    data_points: List[str]  # Source metrics
    recommendations: List[str]
    expiry_time: datetime
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class RealTimeAlert:
    """Real-time alert for immediate attention."""
    alert_id: str
    alert_type: AlertType
    title: str
    message: str
    severity: InsightPriority
    affected_entities: List[str]
    threshold_value: Optional[float] = None
    current_value: Optional[float] = None
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False

@dataclass
class TrendAnalysis:
    """Real-time trend analysis result."""
    trend_id: str
    trend_name: str
    metric_name: str
    direction: str  # increasing, decreasing, stable, volatile
    strength: float  # 0.0 to 1.0
    velocity: float  # Rate of change
    duration_minutes: int
    confidence: float
    predicted_peak_time: Optional[datetime] = None
    related_factors: List[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.now)

@dataclass
class AnomalyDetection:
    """Anomaly detection result."""
    anomaly_id: str
    metric_name: str
    anomaly_type: str  # spike, drop, pattern_break, outlier
    severity: float  # 0.0 to 1.0
    expected_value: float
    actual_value: float
    deviation_score: float
    detection_method: str
    context: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.now)

class RealTimeInsightsEngine:
    """
    Advanced real-time insights engine for the Ainflue platform.
    
    Processes streaming analytics data to generate immediate insights,
    detect anomalies, and provide actionable recommendations.
    """
    
    def __init__(self, buffer_size: int = 10000):
        """Initialize the real-time insights engine."""
        self.buffer_size = buffer_size
        self.metric_buffer: deque = deque(maxlen=buffer_size)
        self.insights: List[RealTimeInsight] = []
        self.alerts: List[RealTimeAlert] = []
        self.trend_analyses: List[TrendAnalysis] = []
        self.anomaly_detections: List[AnomalyDetection] = []
        
        # Analysis components
        self.baseline_models: Dict[str, Dict[str, Any]] = {}
        self.threshold_rules: Dict[str, Dict[str, float]] = {}
        self.pattern_detectors: Dict[str, Any] = {}
        self.trend_trackers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Configuration
        self.insight_expiry_minutes = 60
        self.anomaly_sensitivity = 0.8
        self.trend_detection_window = 30  # minutes
        self.processing_interval = 30  # seconds
        
        logger.info("Initializing Real-Time Insights Engine")
        self._initialize_baseline_models()
        self._setup_threshold_rules()
        self._setup_pattern_detectors()
        
        # Start real-time processing
        asyncio.create_task(self._start_real_time_processing())
    
    def _initialize_baseline_models(self):
        """Initialize baseline models for anomaly detection."""
        
        # Common metrics baseline models
        self.baseline_models = {
            "engagement_rate": {
                "model_type": "rolling_average",
                "window_size": 100,
                "expected_range": (0.02, 0.15),
                "volatility_threshold": 0.3
            },
            "reach": {
                "model_type": "exponential_smoothing",
                "alpha": 0.3,
                "expected_growth_rate": 0.05,
                "anomaly_threshold": 2.5
            },
            "conversions": {
                "model_type": "seasonal_decomposition",
                "seasonality_period": 24,  # hours
                "trend_strength_threshold": 0.6,
                "anomaly_threshold": 3.0
            },
            "revenue": {
                "model_type": "time_series",
                "forecast_horizon": 24,
                "confidence_interval": 0.95,
                "significant_change_threshold": 0.2
            },
            "video_views": {
                "model_type": "growth_curve",
                "growth_phases": ["initial", "growth", "plateau", "decline"],
                "phase_thresholds": [100, 1000, 10000, 50000],
                "anomaly_threshold": 2.0
            }
        }
    
    def _setup_threshold_rules(self):
        """Setup threshold rules for alerts."""
        
        self.threshold_rules = {
            "engagement_rate": {
                "low_threshold": 0.01,
                "high_threshold": 0.20,
                "critical_low": 0.005,
                "critical_high": 0.30
            },
            "reach": {
                "low_threshold": 1000,
                "high_threshold": 1000000,
                "growth_rate_threshold": 0.5,
                "decline_rate_threshold": -0.3
            },
            "conversions": {
                "low_threshold": 1,
                "high_threshold": 1000,
                "conversion_rate_threshold": 0.05,
                "drop_threshold": -0.5
            },
            "revenue": {
                "low_threshold": 10,
                "high_threshold": 10000,
                "growth_threshold": 0.2,
                "decline_threshold": -0.15
            },
            "video_completion_rate": {
                "low_threshold": 0.3,
                "high_threshold": 0.9,
                "critical_low": 0.2,
                "target_rate": 0.7
            }
        }
    
    def _setup_pattern_detectors(self):
        """Setup pattern detection algorithms."""
        
        self.pattern_detectors = {
            "viral_detection": {
                "growth_rate_threshold": 2.0,  # 200% growth
                "acceleration_threshold": 1.5,
                "sustained_growth_periods": 3,
                "engagement_quality_threshold": 0.8
            },
            "trend_reversal": {
                "direction_change_threshold": 0.3,
                "momentum_shift_threshold": 0.5,
                "confirmation_periods": 2
            },
            "seasonal_pattern": {
                "cycle_detection_window": 168,  # 7 days in hours
                "pattern_strength_threshold": 0.6,
                "deviation_tolerance": 0.2
            },
            "competitive_impact": {
                "correlation_threshold": 0.7,
                "response_time_window": 24,  # hours
                "impact_significance": 0.15
            }
        }
    
    async def _start_real_time_processing(self):
        """Start the real-time data processing loop."""
        
        while True:
            try:
                await self._process_real_time_data()
                await asyncio.sleep(self.processing_interval)
            except Exception as e:
                logger.error(f"Error in real-time processing: {e}")
                await asyncio.sleep(5)  # Brief pause on error
    
    async def _process_real_time_data(self):
        """Process real-time data and generate insights."""
        
        if len(self.metric_buffer) < 10:  # Need minimum data
            return
        
        # Get recent metrics
        recent_metrics = list(self.metric_buffer)[-100:]  # Last 100 data points
        
        # Perform analysis
        await self._detect_anomalies(recent_metrics)
        await self._analyze_trends(recent_metrics)
        await self._generate_insights(recent_metrics)
        await self._check_thresholds(recent_metrics)
        
        # Cleanup expired items
        await self._cleanup_expired_items()
    
    def ingest_metric(self, metric: RealTimeMetric):
        """Ingest a real-time metric for processing."""
        
        # Add to buffer
        self.metric_buffer.append(metric)
        
        # Update trend tracker
        self.trend_trackers[metric.metric_name].append({
            "timestamp": metric.timestamp,
            "value": metric.value,
            "tags": metric.tags
        })
        
        # Immediate processing for critical metrics
        if self._is_critical_metric(metric):
            asyncio.create_task(self._process_critical_metric(metric))
    
    def _is_critical_metric(self, metric: RealTimeMetric) -> bool:
        """Check if a metric requires immediate processing."""
        
        critical_metrics = [
            "revenue", "conversions", "engagement_rate", 
            "error_rate", "system_health"
        ]
        
        return metric.metric_name in critical_metrics
    
    async def _process_critical_metric(self, metric: RealTimeMetric):
        """Process critical metric immediately."""
        
        # Check for immediate anomalies
        anomaly = await self._detect_single_metric_anomaly(metric)
        if anomaly and anomaly.severity > 0.8:
            alert = self._create_critical_alert(metric, anomaly)
            self.alerts.append(alert)
            logger.warning(f"Critical alert created: {alert.title}")
    
    async def _detect_anomalies(self, metrics: List[RealTimeMetric]):
        """Detect anomalies in the metric stream."""
        
        # Group metrics by name
        metric_groups = defaultdict(list)
        for metric in metrics:
            metric_groups[metric.metric_name].append(metric)
        
        # Analyze each metric group
        for metric_name, metric_list in metric_groups.items():
            if len(metric_list) < 5:  # Need minimum data for anomaly detection
                continue
            
            anomalies = await self._analyze_metric_anomalies(metric_name, metric_list)
            self.anomaly_detections.extend(anomalies)
    
    async def _analyze_metric_anomalies(
        self,
        metric_name: str,
        metrics: List[RealTimeMetric]
    ) -> List[AnomalyDetection]:
        """Analyze anomalies for a specific metric."""
        
        anomalies = []
        values = [m.value for m in metrics]
        timestamps = [m.timestamp for m in metrics]
        
        if len(values) < 5:
            return anomalies
        
        # Get baseline model
        baseline_model = self.baseline_models.get(metric_name, self.baseline_models["engagement_rate"])
        
        # Statistical anomaly detection
        statistical_anomalies = await self._detect_statistical_anomalies(
            metric_name, values, timestamps, baseline_model
        )
        anomalies.extend(statistical_anomalies)
        
        # Pattern-based anomaly detection
        pattern_anomalies = await self._detect_pattern_anomalies(
            metric_name, values, timestamps
        )
        anomalies.extend(pattern_anomalies)
        
        return anomalies
    
    async def _detect_statistical_anomalies(
        self,
        metric_name: str,
        values: List[float],
        timestamps: List[datetime],
        baseline_model: Dict[str, Any]
    ) -> List[AnomalyDetection]:
        """Detect statistical anomalies using baseline models."""
        
        anomalies = []
        
        if baseline_model["model_type"] == "rolling_average":
            anomalies.extend(await self._rolling_average_anomaly_detection(
                metric_name, values, timestamps, baseline_model
            ))
        elif baseline_model["model_type"] == "exponential_smoothing":
            anomalies.extend(await self._exponential_smoothing_anomaly_detection(
                metric_name, values, timestamps, baseline_model
            ))
        elif baseline_model["model_type"] == "time_series":
            anomalies.extend(await self._time_series_anomaly_detection(
                metric_name, values, timestamps, baseline_model
            ))
        
        return anomalies
    
    async def _rolling_average_anomaly_detection(
        self,
        metric_name: str,
        values: List[float],
        timestamps: List[datetime],
        model_config: Dict[str, Any]
    ) -> List[AnomalyDetection]:
        """Detect anomalies using rolling average method."""
        
        anomalies = []
        window_size = min(model_config["window_size"], len(values) - 1)
        
        if window_size < 3:
            return anomalies
        
        # Calculate rolling statistics
        for i in range(window_size, len(values)):
            window_values = values[i-window_size:i]
            current_value = values[i]
            
            # Calculate expected value and deviation
            expected_value = statistics.mean(window_values)
            std_dev = statistics.stdev(window_values) if len(window_values) > 1 else 0
            
            if std_dev > 0:
                z_score = abs(current_value - expected_value) / std_dev
                
                if z_score > 2.5:  # Significant deviation
                    severity = min(1.0, z_score / 5.0)
                    anomaly_type = "spike" if current_value > expected_value else "drop"
                    
                    anomaly = AnomalyDetection(
                        anomaly_id=f"anomaly_{uuid.uuid4().hex[:8]}",
                        metric_name=metric_name,
                        anomaly_type=anomaly_type,
                        severity=severity,
                        expected_value=expected_value,
                        actual_value=current_value,
                        deviation_score=z_score,
                        detection_method="rolling_average",
                        context={"window_size": window_size, "std_dev": std_dev}
                    )
                    anomalies.append(anomaly)
        
        return anomalies
    
    async def _exponential_smoothing_anomaly_detection(
        self,
        metric_name: str,
        values: List[float],
        timestamps: List[datetime],
        model_config: Dict[str, Any]
    ) -> List[AnomalyDetection]:
        """Detect anomalies using exponential smoothing."""
        
        anomalies = []
        alpha = model_config["alpha"]
        threshold = model_config["anomaly_threshold"]
        
        if len(values) < 3:
            return anomalies
        
        # Initialize with first value
        smoothed_value = values[0]
        
        for i in range(1, len(values)):
            current_value = values[i]
            
            # Calculate prediction error
            error = abs(current_value - smoothed_value)
            relative_error = error / max(smoothed_value, 0.1)  # Avoid division by zero
            
            if relative_error > threshold:
                anomaly_type = "spike" if current_value > smoothed_value else "drop"
                severity = min(1.0, relative_error / (threshold * 2))
                
                anomaly = AnomalyDetection(
                    anomaly_id=f"anomaly_{uuid.uuid4().hex[:8]}",
                    metric_name=metric_name,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    expected_value=smoothed_value,
                    actual_value=current_value,
                    deviation_score=relative_error,
                    detection_method="exponential_smoothing",
                    context={"alpha": alpha, "relative_error": relative_error}
                )
                anomalies.append(anomaly)
            
            # Update smoothed value
            smoothed_value = alpha * current_value + (1 - alpha) * smoothed_value
        
        return anomalies
    
    async def _time_series_anomaly_detection(
        self,
        metric_name: str,
        values: List[float],
        timestamps: List[datetime],
        model_config: Dict[str, Any]
    ) -> List[AnomalyDetection]:
        """Detect anomalies using time series analysis."""
        
        anomalies = []
        
        if len(values) < 10:
            return anomalies
        
        # Simple trend analysis
        trend_values = []
        for i in range(3, len(values)):
            trend = statistics.mean(values[i-3:i])
            trend_values.append(trend)
        
        # Detect significant deviations from trend
        for i, (actual, trend) in enumerate(zip(values[3:], trend_values)):
            if trend > 0:
                deviation = abs(actual - trend) / trend
                
                if deviation > 0.5:  # 50% deviation from trend
                    anomaly_type = "trend_break"
                    severity = min(1.0, deviation)
                    
                    anomaly = AnomalyDetection(
                        anomaly_id=f"anomaly_{uuid.uuid4().hex[:8]}",
                        metric_name=metric_name,
                        anomaly_type=anomaly_type,
                        severity=severity,
                        expected_value=trend,
                        actual_value=actual,
                        deviation_score=deviation,
                        detection_method="time_series",
                        context={"trend_window": 3}
                    )
                    anomalies.append(anomaly)
        
        return anomalies
    
    async def _detect_pattern_anomalies(
        self,
        metric_name: str,
        values: List[float],
        timestamps: List[datetime]
    ) -> List[AnomalyDetection]:
        """Detect pattern-based anomalies."""
        
        anomalies = []
        
        # Check for pattern breaks
        if len(values) >= 20:
            # Look for cyclical patterns
            cycles = await self._detect_cycles(values)
            if cycles:
                cycle_anomalies = await self._detect_cycle_anomalies(
                    metric_name, values, timestamps, cycles
                )
                anomalies.extend(cycle_anomalies)
        
        return anomalies
    
    async def _detect_cycles(self, values: List[float]) -> List[Dict[str, Any]]:
        """Detect cyclical patterns in the data."""
        
        # Simplified cycle detection
        # In production, would use more sophisticated methods like FFT
        cycles = []
        
        # Check for daily patterns (assuming hourly data)
        if len(values) >= 24:
            daily_correlation = self._calculate_periodicity(values, 24)
            if daily_correlation > 0.6:
                cycles.append({
                    "period": 24,
                    "strength": daily_correlation,
                    "type": "daily"
                })
        
        # Check for weekly patterns
        if len(values) >= 168:  # 7 days * 24 hours
            weekly_correlation = self._calculate_periodicity(values, 168)
            if weekly_correlation > 0.5:
                cycles.append({
                    "period": 168,
                    "strength": weekly_correlation,
                    "type": "weekly"
                })
        
        return cycles
    
    def _calculate_periodicity(self, values: List[float], period: int) -> float:
        """Calculate periodicity strength for a given period."""
        
        if len(values) < period * 2:
            return 0.0
        
        # Compare values at periodic intervals
        correlations = []
        for offset in range(period):
            sequence1 = values[offset::period]
            sequence2 = values[offset+period::period]
            
            min_length = min(len(sequence1), len(sequence2))
            if min_length >= 3:
                seq1 = sequence1[:min_length]
                seq2 = sequence2[:min_length]
                
                if statistics.stdev(seq1) > 0 and statistics.stdev(seq2) > 0:
                    correlation = self._calculate_correlation(seq1, seq2)
                    correlations.append(correlation)
        
        return statistics.mean(correlations) if correlations else 0.0
    
    def _calculate_correlation(self, seq1: List[float], seq2: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        
        if len(seq1) != len(seq2) or len(seq1) < 2:
            return 0.0
        
        mean1 = statistics.mean(seq1)
        mean2 = statistics.mean(seq2)
        
        numerator = sum((x - mean1) * (y - mean2) for x, y in zip(seq1, seq2))
        
        sum_sq1 = sum((x - mean1) ** 2 for x in seq1)
        sum_sq2 = sum((y - mean2) ** 2 for y in seq2)
        
        denominator = math.sqrt(sum_sq1 * sum_sq2)
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    async def _detect_cycle_anomalies(
        self,
        metric_name: str,
        values: List[float],
        timestamps: List[datetime],
        cycles: List[Dict[str, Any]]
    ) -> List[AnomalyDetection]:
        """Detect anomalies in cyclical patterns."""
        
        anomalies = []
        
        for cycle in cycles:
            period = cycle["period"]
            strength = cycle["strength"]
            
            # Check recent values against expected cyclical pattern
            if len(values) >= period:
                recent_values = values[-period:]
                expected_pattern = self._calculate_expected_cycle_values(values, period)
                
                for i, (actual, expected) in enumerate(zip(recent_values, expected_pattern)):
                    if expected > 0:
                        deviation = abs(actual - expected) / expected
                        
                        if deviation > 0.3:  # 30% deviation from expected pattern
                            anomaly = AnomalyDetection(
                                anomaly_id=f"anomaly_{uuid.uuid4().hex[:8]}",
                                metric_name=metric_name,
                                anomaly_type="pattern_break",
                                severity=min(1.0, deviation * strength),
                                expected_value=expected,
                                actual_value=actual,
                                deviation_score=deviation,
                                detection_method="cycle_analysis",
                                context={
                                    "cycle_period": period,
                                    "cycle_strength": strength,
                                    "cycle_type": cycle["type"]
                                }
                            )
                            anomalies.append(anomaly)
        
        return anomalies
    
    def _calculate_expected_cycle_values(self, values: List[float], period: int) -> List[float]:
        """Calculate expected values based on cyclical pattern."""
        
        if len(values) < period * 2:
            return values[-period:] if len(values) >= period else values
        
        # Average values at each position in the cycle
        expected_values = []
        for pos in range(period):
            position_values = []
            for i in range(pos, len(values) - period, period):
                position_values.append(values[i])
            
            if position_values:
                expected_values.append(statistics.mean(position_values))
            else:
                expected_values.append(0.0)
        
        return expected_values
    
    async def _analyze_trends(self, metrics: List[RealTimeMetric]):
        """Analyze trends in the metric stream."""
        
        # Group metrics by name
        metric_groups = defaultdict(list)
        for metric in metrics:
            metric_groups[metric.metric_name].append(metric)
        
        # Analyze trends for each metric
        for metric_name, metric_list in metric_groups.items():
            if len(metric_list) >= 5:
                trend = await self._analyze_metric_trend(metric_name, metric_list)
                if trend:
                    self.trend_analyses.append(trend)
    
    async def _analyze_metric_trend(
        self,
        metric_name: str,
        metrics: List[RealTimeMetric]
    ) -> Optional[TrendAnalysis]:
        """Analyze trend for a specific metric."""
        
        if len(metrics) < 5:
            return None
        
        # Sort by timestamp
        sorted_metrics = sorted(metrics, key=lambda x: x.timestamp)
        values = [m.value for m in sorted_metrics]
        timestamps = [m.timestamp for m in sorted_metrics]
        
        # Calculate trend direction and strength
        direction, strength = self._calculate_trend_direction_strength(values)
        
        # Calculate velocity (rate of change)
        velocity = self._calculate_trend_velocity(values, timestamps)
        
        # Calculate confidence
        confidence = self._calculate_trend_confidence(values)
        
        # Duration
        duration_minutes = int((timestamps[-1] - timestamps[0]).total_seconds() / 60)
        
        # Predict peak time for growing trends
        predicted_peak = None
        if direction == "increasing" and velocity > 0:
            predicted_peak = self._predict_trend_peak(timestamps, values, velocity)
        
        # Identify related factors
        related_factors = self._identify_trend_factors(metric_name, direction, strength)
        
        return TrendAnalysis(
            trend_id=f"trend_{uuid.uuid4().hex[:8]}",
            trend_name=f"{metric_name}_{direction}_trend",
            metric_name=metric_name,
            direction=direction,
            strength=strength,
            velocity=velocity,
            duration_minutes=duration_minutes,
            confidence=confidence,
            predicted_peak_time=predicted_peak,
            related_factors=related_factors
        )
    
    def _calculate_trend_direction_strength(self, values: List[float]) -> Tuple[str, float]:
        """Calculate trend direction and strength."""
        
        if len(values) < 3:
            return "stable", 0.0
        
        # Linear regression to find trend
        n = len(values)
        x = list(range(n))
        
        # Calculate slope
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable", 0.0
        
        slope = numerator / denominator
        
        # Determine direction
        if abs(slope) < 0.1:
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"
        
        # Calculate strength (R-squared)
        y_pred = [y_mean + slope * (i - x_mean) for i in x]
        ss_res = sum((values[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((values[i] - y_mean) ** 2 for i in range(n))
        
        if ss_tot == 0:
            strength = 0.0
        else:
            r_squared = 1 - (ss_res / ss_tot)
            strength = max(0.0, min(1.0, r_squared))
        
        return direction, strength
    
    def _calculate_trend_velocity(self, values: List[float], timestamps: List[datetime]) -> float:
        """Calculate trend velocity (rate of change per hour)."""
        
        if len(values) < 2:
            return 0.0
        
        # Calculate change rate
        total_change = values[-1] - values[0]
        time_diff_hours = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
        
        if time_diff_hours == 0:
            return 0.0
        
        # Velocity as change per hour
        velocity = total_change / time_diff_hours
        return velocity
    
    def _calculate_trend_confidence(self, values: List[float]) -> float:
        """Calculate confidence in trend analysis."""
        
        if len(values) < 3:
            return 0.0
        
        # Factors affecting confidence
        factors = []
        
        # Sample size factor
        sample_size_factor = min(1.0, len(values) / 20)
        factors.append(("sample_size", sample_size_factor, 0.3))
        
        # Consistency factor (low variance indicates consistent trend)
        if len(values) > 1:
            cv = statistics.stdev(values) / max(statistics.mean(values), 0.1)
            consistency_factor = max(0.0, 1.0 - cv)
            factors.append(("consistency", consistency_factor, 0.4))
        
        # Monotonicity factor (how consistently the trend moves in one direction)
        monotonicity = self._calculate_monotonicity(values)
        factors.append(("monotonicity", monotonicity, 0.3))
        
        # Calculate weighted confidence
        total_weighted_confidence = sum(score * weight for _, score, weight in factors)
        return round(total_weighted_confidence, 3)
    
    def _calculate_monotonicity(self, values: List[float]) -> float:
        """Calculate how monotonic the sequence is."""
        
        if len(values) < 2:
            return 1.0
        
        # Count directional changes
        changes = 0
        for i in range(1, len(values)):
            if i == 1:
                continue
            
            prev_diff = values[i-1] - values[i-2]
            curr_diff = values[i] - values[i-1]
            
            # Check if direction changed
            if (prev_diff > 0 and curr_diff < 0) or (prev_diff < 0 and curr_diff > 0):
                changes += 1
        
        max_changes = len(values) - 2
        if max_changes == 0:
            return 1.0
        
        # Higher monotonicity means fewer direction changes
        monotonicity = 1.0 - (changes / max_changes)
        return monotonicity
    
    def _predict_trend_peak(
        self,
        timestamps: List[datetime],
        values: List[float],
        velocity: float
    ) -> Optional[datetime]:
        """Predict when an increasing trend might peak."""
        
        if velocity <= 0:
            return None
        
        # Simple prediction based on velocity decay
        # Assume velocity will decrease and trend will peak
        current_value = values[-1]
        current_time = timestamps[-1]
        
        # Predict peak when velocity becomes zero (simplified model)
        # Assuming exponential decay of velocity
        decay_rate = 0.1  # Per hour
        time_to_peak_hours = math.log(2) / decay_rate  # Time to half velocity
        
        predicted_peak_time = current_time + timedelta(hours=time_to_peak_hours)
        return predicted_peak_time
    
    def _identify_trend_factors(self, metric_name: str, direction: str, strength: float) -> List[str]:
        """Identify factors that might be influencing the trend."""
        
        factors = []
        
        # Common factors by metric type
        factor_mapping = {
            "engagement_rate": ["content_quality", "posting_time", "audience_activity", "algorithm_changes"],
            "reach": ["hashtag_performance", "shares", "algorithm_boost", "trending_topics"],
            "conversions": ["landing_page_optimization", "call_to_action", "target_audience", "market_conditions"],
            "revenue": ["pricing_changes", "promotional_campaigns", "market_demand", "competitive_actions"],
            "video_views": ["thumbnail_optimization", "title_effectiveness", "recommendation_algorithm", "trending_status"]
        }
        
        base_factors = factor_mapping.get(metric_name, ["content_strategy", "audience_behavior", "external_factors"])
        
        # Add direction-specific factors
        if direction == "increasing":
            factors.extend(["positive_feedback_loop", "viral_mechanics", "algorithm_favor"])
        elif direction == "decreasing":
            factors.extend(["audience_fatigue", "increased_competition", "algorithm_penalty"])
        
        # Add strength-specific factors
        if strength > 0.8:
            factors.append("strong_market_signal")
        elif strength < 0.3:
            factors.append("mixed_signals")
        
        # Combine and limit
        all_factors = base_factors + factors
        return all_factors[:5]  # Return top 5 factors
    
    async def _generate_insights(self, metrics: List[RealTimeMetric]):
        """Generate insights from analyzed data."""
        
        insights = []
        
        # Generate insights from anomalies
        recent_anomalies = [a for a in self.anomaly_detections if (datetime.now() - a.detected_at).minutes <= 30]
        for anomaly in recent_anomalies:
            insight = await self._create_anomaly_insight(anomaly)
            if insight:
                insights.append(insight)
        
        # Generate insights from trends
        recent_trends = [t for t in self.trend_analyses if (datetime.now() - t.detected_at).minutes <= 30]
        for trend in recent_trends:
            insight = await self._create_trend_insight(trend)
            if insight:
                insights.append(insight)
        
        # Generate performance insights
        performance_insights = await self._generate_performance_insights(metrics)
        insights.extend(performance_insights)
        
        # Store insights
        self.insights.extend(insights)
    
    async def _create_anomaly_insight(self, anomaly: AnomalyDetection) -> Optional[RealTimeInsight]:
        """Create insight from anomaly detection."""
        
        if anomaly.severity < 0.5:  # Only significant anomalies
            return None
        
        # Determine insight type and priority
        if anomaly.anomaly_type in ["spike", "drop"]:
            insight_type = InsightType.PERFORMANCE_SPIKE if anomaly.anomaly_type == "spike" else InsightType.PERFORMANCE_DROP
            priority = InsightPriority.HIGH if anomaly.severity > 0.8 else InsightPriority.MEDIUM
        else:
            insight_type = InsightType.ENGAGEMENT_ANOMALY
            priority = InsightPriority.MEDIUM
        
        # Generate description
        description = f"{anomaly.metric_name} shows {anomaly.anomaly_type} with {anomaly.severity:.1%} severity. "
        description += f"Expected: {anomaly.expected_value:.2f}, Actual: {anomaly.actual_value:.2f}"
        
        # Generate recommendations
        recommendations = self._generate_anomaly_recommendations(anomaly)
        
        return RealTimeInsight(
            insight_id=f"insight_{uuid.uuid4().hex[:8]}",
            insight_type=insight_type,
            title=f"{anomaly.metric_name.title()} {anomaly.anomaly_type.title()} Detected",
            description=description,
            priority=priority,
            confidence_score=min(1.0, anomaly.severity + 0.2),
            impact_score=anomaly.severity,
            data_points=[anomaly.anomaly_id],
            recommendations=recommendations,
            expiry_time=datetime.now() + timedelta(minutes=self.insight_expiry_minutes),
            tags=[anomaly.anomaly_type, anomaly.detection_method]
        )
    
    def _generate_anomaly_recommendations(self, anomaly: AnomalyDetection) -> List[str]:
        """Generate recommendations based on anomaly type."""
        
        recommendations = []
        
        if anomaly.anomaly_type == "spike":
            recommendations.extend([
                f"Investigate cause of {anomaly.metric_name} spike",
                "Monitor for sustainability of increased performance",
                "Analyze contributing factors for replication"
            ])
        elif anomaly.anomaly_type == "drop":
            recommendations.extend([
                f"Immediately investigate {anomaly.metric_name} decline",
                "Check for technical issues or external factors",
                "Implement corrective measures to restore performance"
            ])
        elif anomaly.anomaly_type == "pattern_break":
            recommendations.extend([
                f"Analyze change in {anomaly.metric_name} pattern",
                "Review recent strategic or operational changes",
                "Adjust expectations and monitoring thresholds"
            ])
        
        return recommendations[:3]  # Return top 3 recommendations
    
    async def _create_trend_insight(self, trend: TrendAnalysis) -> Optional[RealTimeInsight]:
        """Create insight from trend analysis."""
        
        if trend.strength < 0.5 or trend.confidence < 0.6:  # Only strong, confident trends
            return None
        
        # Determine insight type
        if trend.direction == "increasing" and trend.strength > 0.8:
            insight_type = InsightType.VIRAL_POTENTIAL
            priority = InsightPriority.HIGH
        elif trend.direction == "decreasing":
            insight_type = InsightType.PERFORMANCE_DROP
            priority = InsightPriority.HIGH
        else:
            insight_type = InsightType.TRENDING_CONTENT
            priority = InsightPriority.MEDIUM
        
        # Generate description
        description = f"{trend.metric_name} showing {trend.direction} trend with {trend.strength:.1%} strength. "
        description += f"Velocity: {trend.velocity:.2f} per hour over {trend.duration_minutes} minutes."
        
        # Generate recommendations
        recommendations = self._generate_trend_recommendations(trend)
        
        return RealTimeInsight(
            insight_id=f"insight_{uuid.uuid4().hex[:8]}",
            insight_type=insight_type,
            title=f"{trend.metric_name.title()} {trend.direction.title()} Trend",
            description=description,
            priority=priority,
            confidence_score=trend.confidence,
            impact_score=trend.strength,
            data_points=[trend.trend_id],
            recommendations=recommendations,
            expiry_time=datetime.now() + timedelta(minutes=self.insight_expiry_minutes),
            tags=[trend.direction, "trend_analysis"] + trend.related_factors[:2]
        )
    
    def _generate_trend_recommendations(self, trend: TrendAnalysis) -> List[str]:
        """Generate recommendations based on trend analysis."""
        
        recommendations = []
        
        if trend.direction == "increasing":
            recommendations.extend([
                f"Capitalize on growing {trend.metric_name} trend",
                "Increase content production in successful format",
                "Monitor for peak timing and optimization opportunities"
            ])
            
            if trend.predicted_peak_time:
                recommendations.append(f"Prepare for potential peak around {trend.predicted_peak_time.strftime('%H:%M')}")
        
        elif trend.direction == "decreasing":
            recommendations.extend([
                f"Address declining {trend.metric_name} trend",
                "Analyze root causes and implement corrections",
                "Consider strategy pivot or content refresh"
            ])
        
        # Add factor-specific recommendations
        if "algorithm_changes" in trend.related_factors:
            recommendations.append("Adapt strategy to recent algorithm changes")
        if "audience_behavior" in trend.related_factors:
            recommendations.append("Study and respond to changing audience preferences")
        
        return recommendations[:4]  # Return top 4 recommendations
    
    async def _generate_performance_insights(self, metrics: List[RealTimeMetric]) -> List[RealTimeInsight]:
        """Generate general performance insights."""
        
        insights = []
        
        # Group metrics by source/entity
        entity_metrics = defaultdict(list)
        for metric in metrics:
            entity = metric.tags.get("entity", "unknown")
            entity_metrics[entity].append(metric)
        
        # Analyze each entity's performance
        for entity, entity_metric_list in entity_metrics.items():
            if len(entity_metric_list) >= 5:  # Need minimum data
                performance_insight = await self._analyze_entity_performance(entity, entity_metric_list)
                if performance_insight:
                    insights.append(performance_insight)
        
        return insights[:3]  # Return top 3 performance insights
    
    async def _analyze_entity_performance(
        self,
        entity: str,
        metrics: List[RealTimeMetric]
    ) -> Optional[RealTimeInsight]:
        """Analyze performance for a specific entity."""
        
        # Calculate performance score
        performance_score = self._calculate_entity_performance_score(metrics)
        
        if performance_score is None:
            return None
        
        # Determine insight type and priority
        if performance_score > 0.8:
            insight_type = InsightType.PERFORMANCE_SPIKE
            priority = InsightPriority.MEDIUM
            title = f"Strong Performance: {entity}"
        elif performance_score < 0.3:
            insight_type = InsightType.PERFORMANCE_DROP
            priority = InsightPriority.HIGH
            title = f"Performance Alert: {entity}"
        else:
            return None  # Average performance, no insight needed
        
        # Generate description
        description = f"{entity} showing {'excellent' if performance_score > 0.8 else 'poor'} performance "
        description += f"with score of {performance_score:.2f}"
        
        # Generate recommendations
        recommendations = self._generate_performance_recommendations(entity, performance_score, metrics)
        
        return RealTimeInsight(
            insight_id=f"insight_{uuid.uuid4().hex[:8]}",
            insight_type=insight_type,
            title=title,
            description=description,
            priority=priority,
            confidence_score=0.8,
            impact_score=abs(performance_score - 0.5) * 2,  # Distance from average
            data_points=[m.metric_id for m in metrics[-5:]],  # Recent metrics
            recommendations=recommendations,
            expiry_time=datetime.now() + timedelta(minutes=self.insight_expiry_minutes),
            tags=["performance_analysis", entity]
        )
    
    def _calculate_entity_performance_score(self, metrics: List[RealTimeMetric]) -> Optional[float]:
        """Calculate performance score for an entity."""
        
        if not metrics:
            return None
        
        # Group by metric type
        metric_values = defaultdict(list)
        for metric in metrics:
            metric_values[metric.metric_name].append(metric.value)
        
        # Calculate normalized scores for each metric type
        normalized_scores = []
        
        for metric_name, values in metric_values.items():
            if values:
                avg_value = statistics.mean(values)
                
                # Normalize based on metric type (simplified)
                if metric_name == "engagement_rate":
                    normalized_score = min(1.0, avg_value / 0.15)  # 15% is excellent
                elif metric_name == "reach":
                    normalized_score = min(1.0, avg_value / 100000)  # 100k reach is excellent
                elif metric_name == "conversions":
                    normalized_score = min(1.0, avg_value / 100)  # 100 conversions is excellent
                else:
                    # Generic normalization
                    normalized_score = min(1.0, avg_value / 1000)
                
                normalized_scores.append(normalized_score)
        
        if normalized_scores:
            return statistics.mean(normalized_scores)
        
        return None
    
    def _generate_performance_recommendations(
        self,
        entity: str,
        performance_score: float,
        metrics: List[RealTimeMetric]
    ) -> List[str]:
        """Generate performance-based recommendations."""
        
        recommendations = []
        
        if performance_score > 0.8:
            recommendations.extend([
                f"Analyze successful strategies for {entity}",
                "Scale successful tactics to other entities",
                "Document best practices for replication"
            ])
        else:
            recommendations.extend([
                f"Investigate performance issues for {entity}",
                "Review and optimize current strategy",
                "Consider A/B testing new approaches"
            ])
        
        # Add metric-specific recommendations
        metric_types = set(metric.metric_name for metric in metrics)
        if "engagement_rate" in metric_types:
            recommendations.append("Focus on improving audience engagement")
        if "conversions" in metric_types:
            recommendations.append("Optimize conversion funnel")
        
        return recommendations[:3]
    
    async def _check_thresholds(self, metrics: List[RealTimeMetric]):
        """Check metrics against threshold rules and generate alerts."""
        
        for metric in metrics[-20:]:  # Check recent metrics
            threshold_rule = self.threshold_rules.get(metric.metric_name)
            if threshold_rule:
                alert = self._check_metric_threshold(metric, threshold_rule)
                if alert:
                    self.alerts.append(alert)
    
    def _check_metric_threshold(
        self,
        metric: RealTimeMetric,
        threshold_rule: Dict[str, float]
    ) -> Optional[RealTimeAlert]:
        """Check a single metric against threshold rule."""
        
        value = metric.value
        alerts = []
        
        # Check critical thresholds
        if "critical_low" in threshold_rule and value < threshold_rule["critical_low"]:
            severity = InsightPriority.CRITICAL
            alert_type = AlertType.THRESHOLD_EXCEEDED
            message = f"{metric.metric_name} critically low: {value} < {threshold_rule['critical_low']}"
        elif "critical_high" in threshold_rule and value > threshold_rule["critical_high"]:
            severity = InsightPriority.CRITICAL
            alert_type = AlertType.THRESHOLD_EXCEEDED
            message = f"{metric.metric_name} critically high: {value} > {threshold_rule['critical_high']}"
        
        # Check regular thresholds
        elif "low_threshold" in threshold_rule and value < threshold_rule["low_threshold"]:
            severity = InsightPriority.HIGH
            alert_type = AlertType.THRESHOLD_EXCEEDED
            message = f"{metric.metric_name} below threshold: {value} < {threshold_rule['low_threshold']}"
        elif "high_threshold" in threshold_rule and value > threshold_rule["high_threshold"]:
            severity = InsightPriority.MEDIUM
            alert_type = AlertType.THRESHOLD_EXCEEDED
            message = f"{metric.metric_name} above threshold: {value} > {threshold_rule['high_threshold']}"
        else:
            return None  # No threshold violation
        
        # Create alert
        return RealTimeAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            alert_type=alert_type,
            title=f"Threshold Alert: {metric.metric_name}",
            message=message,
            severity=severity,
            affected_entities=[metric.tags.get("entity", "unknown")],
            threshold_value=threshold_rule.get("low_threshold", threshold_rule.get("high_threshold")),
            current_value=value,
            recommendations=self._generate_threshold_recommendations(metric.metric_name, value, threshold_rule)
        )
    
    def _generate_threshold_recommendations(
        self,
        metric_name: str,
        current_value: float,
        threshold_rule: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations for threshold violations."""
        
        recommendations = []
        
        # Determine if it's a low or high threshold issue
        is_low_issue = current_value < threshold_rule.get("low_threshold", float('inf'))
        
        if is_low_issue:
            recommendations.extend([
                f"Immediately address low {metric_name}",
                "Review and optimize current strategies",
                "Consider emergency intervention measures"
            ])
        else:
            recommendations.extend([
                f"Monitor high {metric_name} levels",
                "Ensure sustainability of current performance",
                "Prepare for potential scaling needs"
            ])
        
        return recommendations[:3]
    
    async def _detect_single_metric_anomaly(self, metric: RealTimeMetric) -> Optional[AnomalyDetection]:
        """Detect anomaly for a single metric (for critical processing)."""
        
        # Get recent history for this metric
        recent_metrics = [
            m for m in list(self.metric_buffer)[-50:]
            if m.metric_name == metric.metric_name
        ]
        
        if len(recent_metrics) < 5:
            return None
        
        values = [m.value for m in recent_metrics]
        
        # Simple statistical check
        if len(values) >= 10:
            recent_avg = statistics.mean(values[-10:])
            recent_std = statistics.stdev(values[-10:]) if len(values) > 1 else 0
            
            if recent_std > 0:
                z_score = abs(metric.value - recent_avg) / recent_std
                
                if z_score > 3.0:  # Very significant deviation
                    return AnomalyDetection(
                        anomaly_id=f"critical_anomaly_{uuid.uuid4().hex[:8]}",
                        metric_name=metric.metric_name,
                        anomaly_type="spike" if metric.value > recent_avg else "drop",
                        severity=min(1.0, z_score / 5.0),
                        expected_value=recent_avg,
                        actual_value=metric.value,
                        deviation_score=z_score,
                        detection_method="critical_single_point"
                    )
        
        return None
    
    def _create_critical_alert(self, metric: RealTimeMetric, anomaly: AnomalyDetection) -> RealTimeAlert:
        """Create critical alert for immediate anomaly."""
        
        return RealTimeAlert(
            alert_id=f"critical_alert_{uuid.uuid4().hex[:8]}",
            alert_type=AlertType.ANOMALY_DETECTED,
            title=f"CRITICAL: {metric.metric_name} Anomaly",
            message=f"Critical {anomaly.anomaly_type} detected in {metric.metric_name}: {anomaly.actual_value} vs expected {anomaly.expected_value:.2f}",
            severity=InsightPriority.CRITICAL,
            affected_entities=[metric.tags.get("entity", "unknown")],
            current_value=anomaly.actual_value,
            recommendations=[
                "Immediate investigation required",
                "Check system health and external factors",
                "Implement emergency response if needed"
            ]
        )
    
    async def _cleanup_expired_items(self):
        """Clean up expired insights and old data."""
        
        current_time = datetime.now()
        
        # Remove expired insights
        self.insights = [
            insight for insight in self.insights
            if insight.expiry_time > current_time
        ]
        
        # Keep only recent alerts (last 24 hours)
        cutoff_time = current_time - timedelta(hours=24)
        self.alerts = [
            alert for alert in self.alerts
            if alert.created_at > cutoff_time
        ]
        
        # Keep only recent trend analyses (last 2 hours)
        trend_cutoff = current_time - timedelta(hours=2)
        self.trend_analyses = [
            trend for trend in self.trend_analyses
            if trend.detected_at > trend_cutoff
        ]
        
        # Keep only recent anomaly detections (last 4 hours)
        anomaly_cutoff = current_time - timedelta(hours=4)
        self.anomaly_detections = [
            anomaly for anomaly in self.anomaly_detections
            if anomaly.detected_at > anomaly_cutoff
        ]
    
    def get_real_time_dashboard(self) -> Dict[str, Any]:
        """Get real-time insights dashboard."""
        
        current_time = datetime.now()
        
        # Recent insights
        recent_insights = [
            {
                "insight_id": insight.insight_id,
                "type": insight.insight_type.value,
                "title": insight.title,
                "priority": insight.priority.value,
                "confidence": insight.confidence_score,
                "impact": insight.impact_score,
                "created_at": insight.created_at.isoformat(),
                "expires_at": insight.expiry_time.isoformat()
            }
            for insight in sorted(self.insights, key=lambda x: x.created_at, reverse=True)[:10]
        ]
        
        # Active alerts
        active_alerts = [
            {
                "alert_id": alert.alert_id,
                "type": alert.alert_type.value,
                "title": alert.title,
                "severity": alert.severity.value,
                "created_at": alert.created_at.isoformat(),
                "acknowledged": alert.acknowledged
            }
            for alert in sorted(self.alerts, key=lambda x: x.created_at, reverse=True)
            if not alert.acknowledged
        ]
        
        # Recent trends
        recent_trends = [
            {
                "trend_id": trend.trend_id,
                "metric": trend.metric_name,
                "direction": trend.direction,
                "strength": round(trend.strength, 3),
                "velocity": round(trend.velocity, 3),
                "confidence": round(trend.confidence, 3),
                "duration_minutes": trend.duration_minutes
            }
            for trend in sorted(self.trend_analyses, key=lambda x: x.detected_at, reverse=True)[:5]
        ]
        
        # Recent anomalies
        recent_anomalies = [
            {
                "anomaly_id": anomaly.anomaly_id,
                "metric": anomaly.metric_name,
                "type": anomaly.anomaly_type,
                "severity": round(anomaly.severity, 3),
                "deviation": round(anomaly.deviation_score, 3),
                "detected_at": anomaly.detected_at.isoformat()
            }
            for anomaly in sorted(self.anomaly_detections, key=lambda x: x.detected_at, reverse=True)[:5]
        ]
        
        # System status
        system_status = {
            "buffer_utilization": len(self.metric_buffer) / self.buffer_size,
            "processing_lag_seconds": 0,  # Real-time processing
            "insights_generated_last_hour": len([i for i in self.insights if (current_time - i.created_at).seconds <= 3600]),
            "alerts_active": len(active_alerts),
            "anomalies_detected_last_hour": len([a for a in self.anomaly_detections if (current_time - a.detected_at).seconds <= 3600])
        }
        
        return {
            "dashboard_type": "real_time_insights",
            "generated_at": current_time.isoformat(),
            "system_status": system_status,
            "recent_insights": recent_insights,
            "active_alerts": active_alerts,
            "recent_trends": recent_trends,
            "recent_anomalies": recent_anomalies,
            "insights_summary": {
                "total_active_insights": len(self.insights),
                "critical_alerts": len([a for a in active_alerts if a["severity"] == "critical"]),
                "trending_metrics": len(recent_trends),
                "anomaly_rate": len(recent_anomalies) / max(len(self.metric_buffer), 1)
            }
        }

# Initialize the global real-time insights engine
real_time_insights_engine = RealTimeInsightsEngine()

def create_insights_engine_config() -> Dict[str, Any]:
    """Create default configuration for real-time insights engine."""
    return {
        "insight_types": [insight_type.value for insight_type in InsightType],
        "alert_types": [alert_type.value for alert_type in AlertType],
        "priority_levels": [priority.value for priority in InsightPriority],
        "buffer_size": real_time_insights_engine.buffer_size,
        "processing_interval_seconds": real_time_insights_engine.processing_interval,
        "insight_expiry_minutes": real_time_insights_engine.insight_expiry_minutes,
        "anomaly_sensitivity": real_time_insights_engine.anomaly_sensitivity,
        "threshold_rules": real_time_insights_engine.threshold_rules,
        "baseline_models": real_time_insights_engine.baseline_models
    }

# Export main components
__all__ = [
    'RealTimeInsightsEngine',
    'InsightType',
    'InsightPriority',
    'AlertType',
    'RealTimeMetric',
    'RealTimeInsight',
    'RealTimeAlert',
    'TrendAnalysis',
    'AnomalyDetection',
    'real_time_insights_engine',
    'create_insights_engine_config'
]