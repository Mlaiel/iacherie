"""
Anomaly Detection Engine for Ainflue Distribution Monitoring
Provides intelligent anomaly detection for content performance and system metrics

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import statistics
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

import numpy as np
from scipy import stats
from pydantic import BaseModel, Field, validator

# Configure logging
logger = logging.getLogger(__name__)


class AnomalyType(str, Enum):
    """Types of anomalies that can be detected"""
    PERFORMANCE_DROP = "performance_drop"
    ENGAGEMENT_SPIKE = "engagement_spike"
    ENGAGEMENT_DROP = "engagement_drop"
    REACH_ANOMALY = "reach_anomaly"
    CONVERSION_ANOMALY = "conversion_anomaly"
    TRAFFIC_SPIKE = "traffic_spike"
    TRAFFIC_DROP = "traffic_drop"
    ERROR_RATE_SPIKE = "error_rate_spike"
    LATENCY_SPIKE = "latency_spike"
    RESOURCE_USAGE_SPIKE = "resource_usage_spike"
    VIRAL_OPPORTUNITY = "viral_opportunity"
    PLATFORM_ALGORITHM_CHANGE = "platform_algorithm_change"
    COMPETITOR_SURGE = "competitor_surge"
    SEASONAL_ANOMALY = "seasonal_anomaly"
    FRAUD_DETECTION = "fraud_detection"


class AnomalySeverity(str, Enum):
    """Severity levels for anomalies"""
    LOW = "low"           # Minor deviation, informational
    MEDIUM = "medium"     # Moderate deviation, attention needed
    HIGH = "high"         # Significant deviation, action required
    CRITICAL = "critical" # Severe deviation, immediate action required


class DetectionMethod(str, Enum):
    """Anomaly detection methods"""
    STATISTICAL_OUTLIER = "statistical_outlier"      # Z-score, IQR-based
    ISOLATION_FOREST = "isolation_forest"           # Machine learning
    LOCAL_OUTLIER_FACTOR = "local_outlier_factor"   # Density-based
    TIME_SERIES = "time_series"                     # Seasonal decomposition
    THRESHOLD_BASED = "threshold_based"             # Simple threshold
    PATTERN_MATCHING = "pattern_matching"           # Pattern recognition
    ENSEMBLE = "ensemble"                           # Multiple methods


@dataclass
class AnomalyPattern:
    """Pattern definition for anomaly detection"""
    pattern_id: str
    anomaly_type: AnomalyType
    metric_name: str
    detection_method: DetectionMethod
    threshold_config: Dict[str, Any]
    sensitivity: float = 0.8  # 0.0 = low sensitivity, 1.0 = high sensitivity
    enabled: bool = True
    created_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AnomalyAlert(BaseModel):
    """Anomaly alert model"""
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    anomaly_type: AnomalyType = Field(..., description="Type of anomaly detected")
    severity: AnomalySeverity = Field(..., description="Severity level")
    metric_name: str = Field(..., description="Affected metric")
    current_value: float = Field(..., description="Current metric value")
    expected_value: float = Field(..., description="Expected metric value")
    deviation_score: float = Field(..., description="Deviation magnitude")
    confidence: float = Field(..., description="Detection confidence (0-1)")
    detection_method: DetectionMethod = Field(..., description="Detection method used")
    platform: Optional[str] = Field(None, description="Affected platform")
    content_id: Optional[str] = Field(None, description="Affected content")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    action_taken: Optional[str] = Field(None, description="Action taken")
    
    @validator('detected_at', 'resolved_at')
    def validate_timestamps(cls, v) -> None:
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class MetricHistory:
    """Time series data storage for metrics"""
    
    def __init__(self, metric_name -> None: str, max_history -> None: int = 10000) -> None:
        self.metric_name = metric_name
        self.max_history = max_history
        self.timestamps: List[datetime] = []
        self.values: List[float] = []
        self.metadata: List[Dict[str, Any]] = []
        
    def add_value(self, value -> None: float, timestamp -> None: Optional[datetime] = None, 
                 metadata -> None: Optional[Dict[str, Any]] = None) -> None:
        """Add a new metric value"""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
            
        self.timestamps.append(timestamp)
        self.values.append(value)
        self.metadata.append(metadata or {})
        
        # Maintain history limit
        if len(self.values) > self.max_history:
            self.timestamps.pop(0)
            self.values.pop(0)
            self.metadata.pop(0)
            
    def get_recent_values(self, hours: int = 24) -> Tuple[List[datetime], List[float]]:
        """Get values from the last N hours"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        recent_timestamps = []
        recent_values = []
        
        for timestamp, value in zip(self.timestamps, self.values):
            if timestamp >= cutoff:
                recent_timestamps.append(timestamp)
                recent_values.append(value)
                
        return recent_timestamps, recent_values
        
    def get_statistics(self, hours: int = 24) -> Dict[str, float]:
        """Get statistical summary of recent values"""
        _, values = self.get_recent_values(hours)
        
        if not values:
            return {}
            
        return {
            'count': len(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
            'min': min(values),
            'max': max(values),
            'q25': np.percentile(values, 25),
            'q75': np.percentile(values, 75)
        }


class AnomalyDetector:
    """
    Advanced anomaly detection engine for distribution monitoring
    Uses multiple detection methods and machine learning for accurate anomaly detection
    """
    
    def __init__(self) -> None:
        self.patterns: Dict[str, AnomalyPattern] = {}
        self.metric_histories: Dict[str, MetricHistory] = {}
        self.active_alerts: Dict[str, AnomalyAlert] = {}
        self.alert_handlers: List[Callable] = []
        self.monitoring_active = False
        
        # Detection parameters
        self.z_score_threshold = 3.0
        self.iqr_multiplier = 1.5
        self.min_data_points = 10
        self.baseline_hours = 24
        self.sensitivity_adjustment = 1.0
        
        # Initialize default patterns
        self._initialize_default_patterns()
        
    async def initialize(self) -> bool:
        """Initialize the anomaly detection engine"""
        try:
            # Start monitoring
            await self.start_monitoring()
            
            logger.info("Anomaly detection engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize anomaly detector: {e}")
            return False
            
    def _initialize_default_patterns(self) -> None:
        """Initialize default anomaly detection patterns"""
        default_patterns = [
            AnomalyPattern(
                pattern_id="engagement_drop",
                anomaly_type=AnomalyType.ENGAGEMENT_DROP,
                metric_name="engagement_rate",
                detection_method=DetectionMethod.STATISTICAL_OUTLIER,
                threshold_config={'z_score_threshold': 2.5, 'direction': 'below'},
                sensitivity=0.8
            ),
            AnomalyPattern(
                pattern_id="engagement_spike",
                anomaly_type=AnomalyType.ENGAGEMENT_SPIKE,
                metric_name="engagement_rate",
                detection_method=DetectionMethod.STATISTICAL_OUTLIER,
                threshold_config={'z_score_threshold': 3.0, 'direction': 'above'},
                sensitivity=0.7
            ),
            AnomalyPattern(
                pattern_id="reach_anomaly",
                anomaly_type=AnomalyType.REACH_ANOMALY,
                metric_name="reach",
                detection_method=DetectionMethod.TIME_SERIES,
                threshold_config={'seasonal_threshold': 0.3, 'trend_threshold': 0.4},
                sensitivity=0.6
            ),
            AnomalyPattern(
                pattern_id="viral_opportunity",
                anomaly_type=AnomalyType.VIRAL_OPPORTUNITY,
                metric_name="viral_score",
                detection_method=DetectionMethod.THRESHOLD_BASED,
                threshold_config={'threshold': 0.8, 'direction': 'above'},
                sensitivity=0.9
            ),
            AnomalyPattern(
                pattern_id="traffic_spike",
                anomaly_type=AnomalyType.TRAFFIC_SPIKE,
                metric_name="traffic_volume",
                detection_method=DetectionMethod.STATISTICAL_OUTLIER,
                threshold_config={'z_score_threshold': 3.5, 'direction': 'above'},
                sensitivity=0.7
            ),
            AnomalyPattern(
                pattern_id="error_rate_spike",
                anomaly_type=AnomalyType.ERROR_RATE_SPIKE,
                metric_name="error_rate",
                detection_method=DetectionMethod.THRESHOLD_BASED,
                threshold_config={'threshold': 0.05, 'direction': 'above'},
                sensitivity=0.9
            ),
            AnomalyPattern(
                pattern_id="latency_spike",
                anomaly_type=AnomalyType.LATENCY_SPIKE,
                metric_name="response_time",
                detection_method=DetectionMethod.STATISTICAL_OUTLIER,
                threshold_config={'z_score_threshold': 2.0, 'direction': 'above'},
                sensitivity=0.8
            )
        ]
        
        for pattern in default_patterns:
            self.patterns[pattern.pattern_id] = pattern
            
        logger.info(f"Initialized {len(default_patterns)} default detection patterns")
        
    async def start_monitoring(self) -> None:
        """Start anomaly monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            asyncio.create_task(self._monitoring_loop())
            logger.info("Anomaly monitoring started")
            
    async def stop_monitoring(self) -> None:
        """Stop anomaly monitoring"""
        self.monitoring_active = False
        logger.info("Anomaly monitoring stopped")
        
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Run anomaly detection on all metrics
                await self._run_detection_cycle()
                
                # Clean up resolved alerts
                await self._cleanup_resolved_alerts()
                
                # Wait before next cycle
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Anomaly monitoring error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
                
    async def _run_detection_cycle(self) -> None:
        """Run anomaly detection on all monitored metrics"""
        for metric_name, history in self.metric_histories.items():
            # Get relevant patterns for this metric
            relevant_patterns = [
                pattern for pattern in self.patterns.values()
                if pattern.metric_name == metric_name and pattern.enabled
            ]
            
            if not relevant_patterns:
                continue
                
            # Get recent data
            timestamps, values = history.get_recent_values(self.baseline_hours)
            
            if len(values) < self.min_data_points:
                continue
                
            # Check each pattern
            for pattern in relevant_patterns:
                anomaly = await self._detect_anomaly(pattern, values, timestamps)
                if anomaly:
                    await self._handle_anomaly(anomaly)
                    
    async def _detect_anomaly(self, pattern: AnomalyPattern, values: List[float], 
                            timestamps: List[datetime]) -> Optional[AnomalyAlert]:
        """Detect anomaly using specified pattern"""
        try:
            current_value = values[-1] if values else 0.0
            
            if pattern.detection_method == DetectionMethod.STATISTICAL_OUTLIER:
                return await self._detect_statistical_outlier(pattern, values, current_value)
            elif pattern.detection_method == DetectionMethod.TIME_SERIES:
                return await self._detect_time_series_anomaly(pattern, values, timestamps, current_value)
            elif pattern.detection_method == DetectionMethod.THRESHOLD_BASED:
                return await self._detect_threshold_anomaly(pattern, current_value)
            elif pattern.detection_method == DetectionMethod.ISOLATION_FOREST:
                return await self._detect_isolation_forest_anomaly(pattern, values, current_value)
            elif pattern.detection_method == DetectionMethod.ENSEMBLE:
                return await self._detect_ensemble_anomaly(pattern, values, timestamps, current_value)
                
        except Exception as e:
            logger.error(f"Anomaly detection error for pattern {pattern.pattern_id}: {e}")
            
        return None
        
    async def _detect_statistical_outlier(self, pattern: AnomalyPattern, values: List[float], 
                                        current_value: float) -> Optional[AnomalyAlert]:
        """Detect anomalies using statistical methods (Z-score, IQR)"""
        if len(values) < self.min_data_points:
            return None
            
        # Calculate statistics
        mean = statistics.mean(values[:-1])  # Exclude current value
        std_dev = statistics.stdev(values[:-1]) if len(values) > 2 else 0.0
        
        if std_dev == 0:
            return None
            
        # Calculate Z-score
        z_score = abs(current_value - mean) / std_dev
        
        # Check threshold
        threshold = pattern.threshold_config.get('z_score_threshold', self.z_score_threshold)
        threshold *= pattern.sensitivity * self.sensitivity_adjustment
        
        if z_score > threshold:
            # Check direction if specified
            direction = pattern.threshold_config.get('direction', 'both')
            if direction == 'above' and current_value <= mean:
                return None
            elif direction == 'below' and current_value >= mean:
                return None
                
            # Calculate severity based on deviation magnitude
            severity = self._calculate_severity(z_score, threshold)
            
            return AnomalyAlert(
                anomaly_type=pattern.anomaly_type,
                severity=severity,
                metric_name=pattern.metric_name,
                current_value=current_value,
                expected_value=mean,
                deviation_score=z_score,
                confidence=min(z_score / threshold, 1.0),
                detection_method=pattern.detection_method,
                context={
                    'z_score': z_score,
                    'threshold': threshold,
                    'mean': mean,
                    'std_dev': std_dev,
                    'pattern_id': pattern.pattern_id
                }
            )
            
        return None
        
    async def _detect_time_series_anomaly(self, pattern: AnomalyPattern, values: List[float],
                                        timestamps: List[datetime], current_value: float) -> Optional[AnomalyAlert]:
        """Detect anomalies using time series analysis"""
        if len(values) < 24:  # Need at least 24 data points for time series
            return None
            
        try:
            # Simple seasonal decomposition (in production, use more sophisticated methods)
            # Calculate moving average (trend)
            window = min(7, len(values) // 3)
            if window < 2:
                return None
                
            moving_avg = []
            for i in range(len(values)):
                start = max(0, i - window // 2)
                end = min(len(values), i + window // 2 + 1)
                moving_avg.append(statistics.mean(values[start:end]))
                
            # Calculate residuals
            residuals = [v - ma for v, ma in zip(values, moving_avg)]
            
            # Check if current residual is anomalous
            if len(residuals) > 1:
                residual_std = statistics.stdev(residuals[:-1])
                current_residual = residuals[-1]
                
                if residual_std > 0:
                    residual_z_score = abs(current_residual) / residual_std
                    
                    threshold = pattern.threshold_config.get('seasonal_threshold', 2.0)
                    threshold *= pattern.sensitivity
                    
                    if residual_z_score > threshold:
                        severity = self._calculate_severity(residual_z_score, threshold)
                        
                        return AnomalyAlert(
                            anomaly_type=pattern.anomaly_type,
                            severity=severity,
                            metric_name=pattern.metric_name,
                            current_value=current_value,
                            expected_value=moving_avg[-1],
                            deviation_score=residual_z_score,
                            confidence=min(residual_z_score / threshold, 1.0),
                            detection_method=pattern.detection_method,
                            context={
                                'residual_z_score': residual_z_score,
                                'threshold': threshold,
                                'trend': moving_avg[-1],
                                'residual': current_residual,
                                'pattern_id': pattern.pattern_id
                            }
                        )
                        
        except Exception as e:
            logger.error(f"Time series anomaly detection error: {e}")
            
        return None
        
    async def _detect_threshold_anomaly(self, pattern: AnomalyPattern, 
                                      current_value: float) -> Optional[AnomalyAlert]:
        """Detect anomalies using simple threshold comparison"""
        threshold = pattern.threshold_config.get('threshold', 0.0)
        direction = pattern.threshold_config.get('direction', 'above')
        
        is_anomaly = False
        if direction == 'above' and current_value > threshold:
            is_anomaly = True
        elif direction == 'below' and current_value < threshold:
            is_anomaly = True
        elif direction == 'both' and abs(current_value) > threshold:
            is_anomaly = True
            
        if is_anomaly:
            # Calculate deviation as ratio
            if threshold != 0:
                deviation_score = abs(current_value - threshold) / abs(threshold)
            else:
                deviation_score = abs(current_value)
                
            severity = self._calculate_severity(deviation_score, 1.0)
            
            return AnomalyAlert(
                anomaly_type=pattern.anomaly_type,
                severity=severity,
                metric_name=pattern.metric_name,
                current_value=current_value,
                expected_value=threshold,
                deviation_score=deviation_score,
                confidence=pattern.sensitivity,
                detection_method=pattern.detection_method,
                context={
                    'threshold': threshold,
                    'direction': direction,
                    'pattern_id': pattern.pattern_id
                }
            )
            
        return None
        
    async def _detect_isolation_forest_anomaly(self, pattern: AnomalyPattern, values: List[float], 
                                             current_value: float) -> Optional[AnomalyAlert]:
        """Detect anomalies using Isolation Forest (simplified implementation)"""
        if len(values) < 20:
            return None
            
        try:
            # Simplified isolation score calculation
            # In production, use sklearn.ensemble.IsolationForest
            
            # Calculate isolation score based on how different current value is
            sorted_values = sorted(values[:-1])
            
            # Find position of current value in sorted array
            position = 0
            for i, val in enumerate(sorted_values):
                if current_value <= val:
                    position = i
                    break
            else:
                position = len(sorted_values)
                
            # Calculate isolation score (0 = normal, 1 = anomaly)
            isolation_score = abs(position - len(sorted_values) / 2) / (len(sorted_values) / 2)
            
            threshold = pattern.threshold_config.get('isolation_threshold', 0.7)
            threshold *= pattern.sensitivity
            
            if isolation_score > threshold:
                severity = self._calculate_severity(isolation_score, threshold)
                
                return AnomalyAlert(
                    anomaly_type=pattern.anomaly_type,
                    severity=severity,
                    metric_name=pattern.metric_name,
                    current_value=current_value,
                    expected_value=statistics.median(values[:-1]),
                    deviation_score=isolation_score,
                    confidence=isolation_score,
                    detection_method=pattern.detection_method,
                    context={
                        'isolation_score': isolation_score,
                        'threshold': threshold,
                        'position': position,
                        'pattern_id': pattern.pattern_id
                    }
                )
                
        except Exception as e:
            logger.error(f"Isolation forest detection error: {e}")
            
        return None
        
    async def _detect_ensemble_anomaly(self, pattern: AnomalyPattern, values: List[float],
                                     timestamps: List[datetime], current_value: float) -> Optional[AnomalyAlert]:
        """Detect anomalies using ensemble of multiple methods"""
        # Run multiple detection methods
        results = []
        
        # Statistical outlier
        stat_result = await self._detect_statistical_outlier(pattern, values, current_value)
        if stat_result:
            results.append(('statistical', stat_result.deviation_score, stat_result.confidence))
            
        # Time series
        ts_result = await self._detect_time_series_anomaly(pattern, values, timestamps, current_value)
        if ts_result:
            results.append(('time_series', ts_result.deviation_score, ts_result.confidence))
            
        # Isolation forest
        if_result = await self._detect_isolation_forest_anomaly(pattern, values, current_value)
        if if_result:
            results.append(('isolation_forest', if_result.deviation_score, if_result.confidence))
            
        # Ensemble decision
        if len(results) >= 2:  # At least 2 methods agree
            # Weighted average of scores
            total_weight = sum(confidence for _, _, confidence in results)
            weighted_score = sum(score * confidence for _, score, confidence in results) / total_weight
            ensemble_confidence = len(results) / 3.0  # Max 3 methods
            
            severity = self._calculate_severity(weighted_score, 1.0)
            
            return AnomalyAlert(
                anomaly_type=pattern.anomaly_type,
                severity=severity,
                metric_name=pattern.metric_name,
                current_value=current_value,
                expected_value=statistics.mean(values[:-1]) if len(values) > 1 else current_value,
                deviation_score=weighted_score,
                confidence=ensemble_confidence,
                detection_method=DetectionMethod.ENSEMBLE,
                context={
                    'ensemble_results': results,
                    'methods_count': len(results),
                    'weighted_score': weighted_score,
                    'pattern_id': pattern.pattern_id
                }
            )
            
        return None
        
    def _calculate_severity(self, deviation_score: float, threshold: float) -> AnomalySeverity:
        """Calculate anomaly severity based on deviation magnitude"""
        ratio = deviation_score / threshold
        
        if ratio >= 3.0:
            return AnomalySeverity.CRITICAL
        elif ratio >= 2.0:
            return AnomalySeverity.HIGH
        elif ratio >= 1.5:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW
            
    async def _handle_anomaly(self, anomaly -> None: AnomalyAlert) -> None:
        """Handle detected anomaly"""
        try:
            # Check for duplicate alerts
            similar_alerts = [
                alert for alert in self.active_alerts.values()
                if (alert.anomaly_type == anomaly.anomaly_type and
                    alert.metric_name == anomaly.metric_name and
                    alert.platform == anomaly.platform and
                    not alert.resolved_at)
            ]
            
            if similar_alerts:
                # Update existing alert instead of creating new one
                existing_alert = similar_alerts[0]
                existing_alert.current_value = anomaly.current_value
                existing_alert.deviation_score = max(existing_alert.deviation_score, anomaly.deviation_score)
                existing_alert.confidence = max(existing_alert.confidence, anomaly.confidence)
                existing_alert.detected_at = anomaly.detected_at
                logger.debug(f"Updated existing anomaly alert: {existing_alert.alert_id}")
                return
                
            # Store new alert
            self.active_alerts[anomaly.alert_id] = anomaly
            
            logger.warning(
                f"Anomaly detected: {anomaly.anomaly_type.value} - "
                f"{anomaly.metric_name} = {anomaly.current_value:.2f} "
                f"(expected: {anomaly.expected_value:.2f}, "
                f"deviation: {anomaly.deviation_score:.2f}, "
                f"severity: {anomaly.severity.value})"
            )
            
            # Notify alert handlers
            for handler in self.alert_handlers:
                try:
                    await handler(anomaly)
                except Exception as e:
                    logger.error(f"Alert handler error: {e}")
                    
        except Exception as e:
            logger.error(f"Anomaly handling error: {e}")
            
    async def _cleanup_resolved_alerts(self) -> None:
        """Clean up alerts that have been resolved"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        
        alerts_to_remove = [
            alert_id for alert_id, alert in self.active_alerts.items()
            if alert.resolved_at and alert.resolved_at < cutoff_time
        ]
        
        for alert_id in alerts_to_remove:
            del self.active_alerts[alert_id]
            
        if alerts_to_remove:
            logger.debug(f"Cleaned up {len(alerts_to_remove)} resolved alerts")
            
    async def add_metric_value(self, metric_name -> None: str, value -> None: float, 
                             timestamp -> None: Optional[datetime] = None,
                             metadata -> None: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a new metric value for anomaly detection
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            timestamp: Value timestamp (optional)
            metadata: Additional metadata (optional)
        """
        try:
            if metric_name not in self.metric_histories:
                self.metric_histories[metric_name] = MetricHistory(metric_name)
                
            self.metric_histories[metric_name].add_value(value, timestamp, metadata)
            
        except Exception as e:
            logger.error(f"Failed to add metric value: {e}")
            
    def add_detection_pattern(self, pattern: AnomalyPattern) -> bool:
        """
        Add a new anomaly detection pattern
        
        Args:
            pattern: Detection pattern configuration
            
        Returns:
            Success status
        """
        try:
            self.patterns[pattern.pattern_id] = pattern
            logger.info(f"Added detection pattern: {pattern.pattern_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add detection pattern: {e}")
            return False
            
    def remove_detection_pattern(self, pattern_id: str) -> bool:
        """
        Remove an anomaly detection pattern
        
        Args:
            pattern_id: Pattern identifier
            
        Returns:
            Success status
        """
        try:
            if pattern_id in self.patterns:
                del self.patterns[pattern_id]
                logger.info(f"Removed detection pattern: {pattern_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove detection pattern: {e}")
            return False
            
    def add_alert_handler(self, handler -> None: Callable[[AnomalyAlert], None]) -> None:
        """Add alert handler function"""
        self.alert_handlers.append(handler)
        
    def remove_alert_handler(self, handler -> None: Callable[[AnomalyAlert], None]) -> None:
        """Remove alert handler function"""
        if handler in self.alert_handlers:
            self.alert_handlers.remove(handler)
            
    async def resolve_alert(self, alert_id: str, action_taken: str = None) -> bool:
        """
        Mark an alert as resolved
        
        Args:
            alert_id: Alert identifier
            action_taken: Description of action taken
            
        Returns:
            Success status
        """
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved_at = datetime.now(timezone.utc)
                alert.action_taken = action_taken
                
                logger.info(f"Resolved alert: {alert_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False
            
    def get_active_alerts(self, severity: Optional[AnomalySeverity] = None,
                         anomaly_type: Optional[AnomalyType] = None) -> List[AnomalyAlert]:
        """
        Get active alerts with optional filtering
        
        Args:
            severity: Filter by severity level
            anomaly_type: Filter by anomaly type
            
        Returns:
            List of matching alerts
        """
        alerts = [
            alert for alert in self.active_alerts.values()
            if not alert.resolved_at
        ]
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
            
        if anomaly_type:
            alerts = [alert for alert in alerts if alert.anomaly_type == anomaly_type]
            
        return sorted(alerts, key=lambda x: x.detected_at, reverse=True)
        
    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get anomaly detection statistics"""
        total_alerts = len(self.active_alerts)
        resolved_alerts = len([a for a in self.active_alerts.values() if a.resolved_at])
        active_alerts = total_alerts - resolved_alerts
        
        # Count by severity
        severity_counts = {}
        for alert in self.active_alerts.values():
            if not alert.resolved_at:
                severity = alert.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
        # Count by type
        type_counts = {}
        for alert in self.active_alerts.values():
            if not alert.resolved_at:
                anomaly_type = alert.anomaly_type.value
                type_counts[anomaly_type] = type_counts.get(anomaly_type, 0) + 1
                
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'resolved_alerts': resolved_alerts,
            'alerts_by_severity': severity_counts,
            'alerts_by_type': type_counts,
            'active_patterns': len([p for p in self.patterns.values() if p.enabled]),
            'monitored_metrics': len(self.metric_histories),
            'total_patterns': len(self.patterns)
        }


# Export main classes
__all__ = [
    'AnomalyDetector',
    'AnomalyPattern',
    'AnomalyAlert',
    'MetricHistory',
    'AnomalyType',
    'AnomalySeverity', 
    'DetectionMethod'
]