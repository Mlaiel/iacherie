"""
Enterprise Anomaly Detector for ML Systems
ML Engineer + Security implementation with advanced anomaly detection
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import uuid
import statistics
from collections import defaultdict, deque
import math

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of anomalies"""
    STATISTICAL = "statistical"
    TEMPORAL = "temporal"
    BEHAVIORAL = "behavioral"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DATA_QUALITY = "data_quality"
    BUSINESS_LOGIC = "business_logic"


class AnomalySeverity(Enum):
    """Anomaly severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DetectionMethod(Enum):
    """Anomaly detection methods"""
    ISOLATION_FOREST = "isolation_forest"
    STATISTICAL_OUTLIER = "statistical_outlier"
    LSTM_AUTOENCODER = "lstm_autoencoder"
    DENSITY_CLUSTERING = "density_clustering"
    THRESHOLD_BASED = "threshold_based"
    ENSEMBLE = "ensemble"


@dataclass
class AnomalyAlert:
    """Anomaly detection alert"""
    alert_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    detection_method: DetectionMethod
    description: str
    affected_service: str
    metric_name: str
    anomaly_score: float
    baseline_value: float
    actual_value: float
    deviation_percentage: float
    detection_time: datetime
    creator_impact: str = "unknown"
    resolution_status: str = "open"
    tags: List[str] = field(default_factory=list)


@dataclass
class DetectionRule:
    """Anomaly detection rule"""
    rule_id: str
    name: str
    description: str
    anomaly_type: AnomalyType
    detection_method: DetectionMethod
    metric_pattern: str
    threshold_config: Dict[str, Any]
    is_enabled: bool = True
    creator_types: List[str] = field(default_factory=list)
    severity_mapping: Dict[str, AnomalySeverity] = field(default_factory=dict)


@dataclass
class MetricTimeSeries:
    """Time series data for metrics"""
    metric_name: str
    service_name: str
    timestamps: List[datetime]
    values: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)


class AnomalyDetector:
    """Enterprise anomaly detection system for ML operations"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.detection_rules: Dict[str, DetectionRule] = {}
        self.alerts: List[AnomalyAlert] = []
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.baseline_models: Dict[str, Dict[str, Any]] = {}
        self.alert_handlers: List[Callable] = []
        
        # Creator-specific anomaly thresholds
        self.creator_thresholds = {
            'musicians': {
                'audio_processing_latency': {'threshold': 500, 'severity': 'high'},
                'model_accuracy': {'threshold': 0.85, 'severity': 'critical'},
                'upload_success_rate': {'threshold': 0.95, 'severity': 'high'},
                'collaboration_response_time': {'threshold': 1000, 'severity': 'medium'}
            },
            'photographers': {
                'image_processing_latency': {'threshold': 2000, 'severity': 'high'},
                'storage_availability': {'threshold': 0.99, 'severity': 'critical'},
                'cdn_response_time': {'threshold': 200, 'severity': 'medium'},
                'portfolio_load_time': {'threshold': 3000, 'severity': 'high'}
            },
            'bloggers': {
                'content_generation_time': {'threshold': 5000, 'severity': 'medium'},
                'seo_analysis_accuracy': {'threshold': 0.90, 'severity': 'high'},
                'publishing_success_rate': {'threshold': 0.98, 'severity': 'high'},
                'analytics_processing_time': {'threshold': 1500, 'severity': 'medium'}
            },
            'influencers': {
                'multi_platform_sync_time': {'threshold': 10000, 'severity': 'high'},
                'analytics_freshness': {'threshold': 300, 'severity': 'medium'},
                'engagement_prediction_accuracy': {'threshold': 0.80, 'severity': 'medium'},
                'brand_matching_precision': {'threshold': 0.85, 'severity': 'high'}
            },
            'comedians': {
                'video_processing_time': {'threshold': 30000, 'severity': 'high'},
                'timing_analysis_accuracy': {'threshold': 0.75, 'severity': 'medium'},
                'performance_prediction_latency': {'threshold': 2000, 'severity': 'medium'},
                'venue_matching_success_rate': {'threshold': 0.70, 'severity': 'low'}
            }
        }
        
        # Detection sensitivity by environment
        self.sensitivity_config = {
            'production': {'multiplier': 1.0, 'confidence_threshold': 0.95},
            'staging': {'multiplier': 0.8, 'confidence_threshold': 0.85},
            'development': {'multiplier': 0.6, 'confidence_threshold': 0.75}
        }
        
    async def initialize(self) -> bool:
        """Initialize anomaly detector"""
        try:
            logger.info("Initializing Anomaly Detector...")
            
            # Setup default detection rules
            await self._setup_default_rules()
            
            # Initialize baseline models
            await self._initialize_baseline_models()
            
            # Start continuous monitoring
            asyncio.create_task(self._continuous_monitoring())
            
            # Setup alert handlers
            await self._setup_alert_handlers()
            
            logger.info("Anomaly Detector initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Anomaly Detector: {e}")
            return False
    
    async def add_detection_rule(self, rule: DetectionRule) -> bool:
        """Add new anomaly detection rule"""
        try:
            self.detection_rules[rule.rule_id] = rule
            
            logger.info(f"Added detection rule: {rule.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add detection rule: {e}")
            return False
    
    async def record_metric(self, 
                          metric_name: str,
                          value: float,
                          service_name: str,
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Record metric for anomaly detection"""
        try:
            metric_key = f"{service_name}_{metric_name}"
            timestamp = datetime.utcnow()
            
            # Store metric value
            metric_data = {
                'timestamp': timestamp,
                'value': value,
                'service_name': service_name,
                'metadata': metadata or {}
            }
            
            self.metric_history[metric_key].append(metric_data)
            
            # Check for anomalies
            await self._check_for_anomalies(metric_key, value, timestamp, metadata)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
            return False
    
    async def detect_anomalies(self, 
                             metric_name: str,
                             service_name: str,
                             time_window: Optional[timedelta] = None) -> List[AnomalyAlert]:
        """Detect anomalies in specific metric"""
        try:
            metric_key = f"{service_name}_{metric_name}"
            
            if metric_key not in self.metric_history:
                return []
            
            # Get data within time window
            if time_window:
                cutoff_time = datetime.utcnow() - time_window
                metric_data = [
                    d for d in self.metric_history[metric_key]
                    if d['timestamp'] >= cutoff_time
                ]
            else:
                metric_data = list(self.metric_history[metric_key])
            
            if len(metric_data) < 10:  # Need minimum data points
                return []
            
            # Apply different detection methods
            anomalies = []
            
            # Statistical outlier detection
            statistical_anomalies = await self._detect_statistical_outliers(
                metric_key, metric_data
            )
            anomalies.extend(statistical_anomalies)
            
            # Temporal pattern detection
            temporal_anomalies = await self._detect_temporal_anomalies(
                metric_key, metric_data
            )
            anomalies.extend(temporal_anomalies)
            
            # Threshold-based detection
            threshold_anomalies = await self._detect_threshold_anomalies(
                metric_key, metric_data
            )
            anomalies.extend(threshold_anomalies)
            
            # Business logic anomalies
            business_anomalies = await self._detect_business_logic_anomalies(
                metric_key, metric_data
            )
            anomalies.extend(business_anomalies)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {e}")
            return []
    
    async def get_anomaly_summary(self, 
                                time_period: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get summary of detected anomalies"""
        try:
            if time_period:
                cutoff_time = datetime.utcnow() - time_period
                relevant_alerts = [
                    a for a in self.alerts
                    if a.detection_time >= cutoff_time
                ]
            else:
                relevant_alerts = self.alerts
            
            summary = {
                'total_anomalies': len(relevant_alerts),
                'by_severity': defaultdict(int),
                'by_type': defaultdict(int),
                'by_service': defaultdict(int),
                'by_creator_impact': defaultdict(int),
                'resolution_status': defaultdict(int),
                'trends': await self._analyze_anomaly_trends(relevant_alerts),
                'top_affected_services': await self._get_top_affected_services(relevant_alerts)
            }
            
            for alert in relevant_alerts:
                summary['by_severity'][alert.severity.value] += 1
                summary['by_type'][alert.anomaly_type.value] += 1
                summary['by_service'][alert.affected_service] += 1
                summary['by_creator_impact'][alert.creator_impact] += 1
                summary['resolution_status'][alert.resolution_status] += 1
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get anomaly summary: {e}")
            return {}
    
    async def resolve_anomaly(self, alert_id: str, resolution_notes: str = "") -> bool:
        """Mark anomaly as resolved"""
        try:
            for alert in self.alerts:
                if alert.alert_id == alert_id:
                    alert.resolution_status = "resolved"
                    logger.info(f"Resolved anomaly: {alert_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to resolve anomaly: {e}")
            return False
    
    async def get_baseline_metrics(self, 
                                 metric_name: str,
                                 service_name: str) -> Optional[Dict[str, Any]]:
        """Get baseline metrics for comparison"""
        try:
            metric_key = f"{service_name}_{metric_name}"
            
            if metric_key not in self.baseline_models:
                # Calculate baseline if not exists
                await self._calculate_baseline(metric_key)
            
            return self.baseline_models.get(metric_key)
            
        except Exception as e:
            logger.error(f"Failed to get baseline metrics: {e}")
            return None
    
    async def add_alert_handler(self, handler: Callable) -> bool:
        """Add alert handler for anomaly notifications"""
        try:
            self.alert_handlers.append(handler)
            return True
            
        except Exception as e:
            logger.error(f"Failed to add alert handler: {e}")
            return False
    
    async def _setup_default_rules(self) -> None:
        """Setup default anomaly detection rules"""
        
        # Performance anomaly rule
        performance_rule = DetectionRule(
            rule_id="performance_anomaly",
            name="Performance Anomaly Detection",
            description="Detect performance degradations in ML services",
            anomaly_type=AnomalyType.PERFORMANCE,
            detection_method=DetectionMethod.STATISTICAL_OUTLIER,
            metric_pattern="*_latency,*_response_time",
            threshold_config={'std_dev_multiplier': 3.0, 'min_samples': 30}
        )
        await self.add_detection_rule(performance_rule)
        
        # Data quality rule
        data_quality_rule = DetectionRule(
            rule_id="data_quality_anomaly",
            name="Data Quality Anomaly Detection",
            description="Detect data quality issues",
            anomaly_type=AnomalyType.DATA_QUALITY,
            detection_method=DetectionMethod.THRESHOLD_BASED,
            metric_pattern="*_accuracy,*_precision,*_recall",
            threshold_config={'min_threshold': 0.8}
        )
        await self.add_detection_rule(data_quality_rule)
        
        # Security anomaly rule
        security_rule = DetectionRule(
            rule_id="security_anomaly",
            name="Security Anomaly Detection",
            description="Detect security-related anomalies",
            anomaly_type=AnomalyType.SECURITY,
            detection_method=DetectionMethod.ENSEMBLE,
            metric_pattern="*_failed_logins,*_unauthorized_access",
            threshold_config={'threshold_multiplier': 2.0}
        )
        await self.add_detection_rule(security_rule)
    
    async def _initialize_baseline_models(self) -> None:
        """Initialize baseline models for metrics"""
        # Baseline models will be calculated when sufficient data is available
        pass
    
    async def _continuous_monitoring(self) -> None:
        """Continuous monitoring task"""
        while True:
            try:
                # Run periodic anomaly detection
                await self._periodic_anomaly_check()
                
                # Update baseline models
                await self._update_baseline_models()
                
                # Cleanup old data
                await self._cleanup_old_data()
                
                # Sleep for monitoring interval (5 minutes)
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Continuous monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _setup_alert_handlers(self) -> None:
        """Setup default alert handlers"""
        async def default_alert_handler(alert -> None: AnomalyAlert) -> None:
            logger.warning(f"Anomaly detected: {alert.description} (Severity: {alert.severity.value})")
        
        await self.add_alert_handler(default_alert_handler)
    
    async def _check_for_anomalies(self, 
                                 metric_key -> None: str,
                                 value -> None: float,
                                 timestamp -> None: datetime,
                                 metadata -> None: Optional[Dict[str, Any]]) -> None:
        """Check for anomalies in real-time"""
        try:
            # Get recent data for comparison
            recent_data = list(self.metric_history[metric_key])[-100:]  # Last 100 points
            
            if len(recent_data) < 10:
                return  # Need minimum data points
            
            # Quick statistical check
            values = [d['value'] for d in recent_data[:-1]]  # Exclude current value
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values) if len(values) > 1 else 0
            
            # Check for statistical anomaly
            if std_val > 0:
                z_score = abs(value - mean_val) / std_val
                if z_score > 3.0:  # 3 sigma rule
                    await self._create_anomaly_alert(
                        metric_key, value, mean_val, timestamp,
                        AnomalyType.STATISTICAL, AnomalySeverity.MEDIUM,
                        f"Statistical outlier detected (Z-score: {z_score:.2f})"
                    )
            
            # Check creator-specific thresholds
            await self._check_creator_thresholds(metric_key, value, timestamp)
            
        except Exception as e:
            logger.error(f"Failed to check for anomalies: {e}")
    
    async def _detect_statistical_outliers(self, 
                                         metric_key: str,
                                         metric_data: List[Dict[str, Any]]) -> List[AnomalyAlert]:
        """Detect statistical outliers using various methods"""
        anomalies = []
        
        try:
            values = [d['value'] for d in metric_data]
            
            if len(values) < 30:
                return anomalies
            
            # IQR method
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            for i, data_point in enumerate(metric_data):
                value = data_point['value']
                if value < lower_bound or value > upper_bound:
                    deviation = ((value - np.mean(values)) / np.std(values)) * 100
                    
                    alert = AnomalyAlert(
                        alert_id=str(uuid.uuid4()),
                        anomaly_type=AnomalyType.STATISTICAL,
                        severity=self._calculate_severity(abs(deviation)),
                        detection_method=DetectionMethod.STATISTICAL_OUTLIER,
                        description=f"IQR outlier detected in {metric_key}",
                        affected_service=data_point.get('service_name', 'unknown'),
                        metric_name=metric_key,
                        anomaly_score=abs(deviation),
                        baseline_value=np.mean(values),
                        actual_value=value,
                        deviation_percentage=deviation,
                        detection_time=data_point['timestamp']
                    )
                    anomalies.append(alert)
            
        except Exception as e:
            logger.error(f"Failed to detect statistical outliers: {e}")
        
        return anomalies
    
    async def _detect_temporal_anomalies(self, 
                                       metric_key: str,
                                       metric_data: List[Dict[str, Any]]) -> List[AnomalyAlert]:
        """Detect temporal pattern anomalies"""
        anomalies = []
        
        try:
            if len(metric_data) < 50:
                return anomalies
            
            # Convert to time series
            timestamps = [d['timestamp'] for d in metric_data]
            values = [d['value'] for d in metric_data]
            
            # Simple trend detection
            if len(values) >= 20:
                recent_trend = np.polyfit(range(len(values[-20:])), values[-20:], 1)[0]
                historical_trend = np.polyfit(range(len(values[:-20])), values[:-20], 1)[0]
                
                # Significant trend change detection
                if abs(recent_trend - historical_trend) > abs(historical_trend) * 2:
                    alert = AnomalyAlert(
                        alert_id=str(uuid.uuid4()),
                        anomaly_type=AnomalyType.TEMPORAL,
                        severity=AnomalySeverity.MEDIUM,
                        detection_method=DetectionMethod.STATISTICAL_OUTLIER,
                        description=f"Significant trend change detected in {metric_key}",
                        affected_service=metric_data[-1].get('service_name', 'unknown'),
                        metric_name=metric_key,
                        anomaly_score=abs(recent_trend - historical_trend),
                        baseline_value=historical_trend,
                        actual_value=recent_trend,
                        deviation_percentage=((recent_trend - historical_trend) / abs(historical_trend)) * 100 if historical_trend != 0 else 0,
                        detection_time=timestamps[-1]
                    )
                    anomalies.append(alert)
            
        except Exception as e:
            logger.error(f"Failed to detect temporal anomalies: {e}")
        
        return anomalies
    
    async def _detect_threshold_anomalies(self, 
                                        metric_key: str,
                                        metric_data: List[Dict[str, Any]]) -> List[AnomalyAlert]:
        """Detect threshold-based anomalies"""
        anomalies = []
        
        try:
            # Check against predefined thresholds
            service_name = metric_data[-1].get('service_name', 'unknown') if metric_data else 'unknown'
            
            for creator_type, thresholds in self.creator_thresholds.items():
                for threshold_metric, config in thresholds.items():
                    if threshold_metric in metric_key:
                        threshold = config['threshold']
                        severity_str = config['severity']
                        
                        for data_point in metric_data[-10:]:  # Check last 10 points
                            value = data_point['value']
                            
                            # Check if value exceeds threshold
                            if ('latency' in threshold_metric or 'time' in threshold_metric) and value > threshold:
                                deviation = ((value - threshold) / threshold) * 100
                                
                                alert = AnomalyAlert(
                                    alert_id=str(uuid.uuid4()),
                                    anomaly_type=AnomalyType.PERFORMANCE,
                                    severity=AnomalySeverity(severity_str),
                                    detection_method=DetectionMethod.THRESHOLD_BASED,
                                    description=f"Threshold exceeded for {threshold_metric}",
                                    affected_service=service_name,
                                    metric_name=metric_key,
                                    anomaly_score=deviation,
                                    baseline_value=threshold,
                                    actual_value=value,
                                    deviation_percentage=deviation,
                                    detection_time=data_point['timestamp'],
                                    creator_impact=creator_type
                                )
                                anomalies.append(alert)
                            
                            elif ('rate' in threshold_metric or 'accuracy' in threshold_metric) and value < threshold:
                                deviation = ((threshold - value) / threshold) * 100
                                
                                alert = AnomalyAlert(
                                    alert_id=str(uuid.uuid4()),
                                    anomaly_type=AnomalyType.DATA_QUALITY,
                                    severity=AnomalySeverity(severity_str),
                                    detection_method=DetectionMethod.THRESHOLD_BASED,
                                    description=f"Below threshold for {threshold_metric}",
                                    affected_service=service_name,
                                    metric_name=metric_key,
                                    anomaly_score=deviation,
                                    baseline_value=threshold,
                                    actual_value=value,
                                    deviation_percentage=-deviation,
                                    detection_time=data_point['timestamp'],
                                    creator_impact=creator_type
                                )
                                anomalies.append(alert)
            
        except Exception as e:
            logger.error(f"Failed to detect threshold anomalies: {e}")
        
        return anomalies
    
    async def _detect_business_logic_anomalies(self, 
                                             metric_key: str,
                                             metric_data: List[Dict[str, Any]]) -> List[AnomalyAlert]:
        """Detect business logic anomalies"""
        anomalies = []
        
        try:
            # Business-specific anomaly detection
            if 'revenue' in metric_key.lower():
                # Sudden revenue drops
                values = [d['value'] for d in metric_data[-30:]]  # Last 30 points
                if len(values) >= 10:
                    recent_avg = statistics.mean(values[-5:])
                    historical_avg = statistics.mean(values[:-5])
                    
                    if recent_avg < historical_avg * 0.7:  # 30% drop
                        alert = AnomalyAlert(
                            alert_id=str(uuid.uuid4()),
                            anomaly_type=AnomalyType.BUSINESS_LOGIC,
                            severity=AnomalySeverity.HIGH,
                            detection_method=DetectionMethod.STATISTICAL_OUTLIER,
                            description="Significant revenue drop detected",
                            affected_service=metric_data[-1].get('service_name', 'unknown'),
                            metric_name=metric_key,
                            anomaly_score=((historical_avg - recent_avg) / historical_avg) * 100,
                            baseline_value=historical_avg,
                            actual_value=recent_avg,
                            deviation_percentage=-30.0,
                            detection_time=metric_data[-1]['timestamp']
                        )
                        anomalies.append(alert)
            
            elif 'user' in metric_key.lower() and 'count' in metric_key.lower():
                # Unusual user activity patterns
                values = [d['value'] for d in metric_data[-24:]]  # Last 24 points (hours)
                if len(values) >= 12:
                    # Check for sudden spikes (could indicate bot activity)
                    max_val = max(values[-6:])
                    avg_val = statistics.mean(values[:-6])
                    
                    if max_val > avg_val * 5:  # 5x spike
                        alert = AnomalyAlert(
                            alert_id=str(uuid.uuid4()),
                            anomaly_type=AnomalyType.SECURITY,
                            severity=AnomalySeverity.MEDIUM,
                            detection_method=DetectionMethod.STATISTICAL_OUTLIER,
                            description="Unusual user activity spike detected",
                            affected_service=metric_data[-1].get('service_name', 'unknown'),
                            metric_name=metric_key,
                            anomaly_score=(max_val / avg_val) * 100,
                            baseline_value=avg_val,
                            actual_value=max_val,
                            deviation_percentage=((max_val - avg_val) / avg_val) * 100,
                            detection_time=metric_data[-1]['timestamp']
                        )
                        anomalies.append(alert)
            
        except Exception as e:
            logger.error(f"Failed to detect business logic anomalies: {e}")
        
        return anomalies
    
    async def _check_creator_thresholds(self, 
                                      metric_key -> None: str,
                                      value -> None: float,
                                      timestamp -> None: datetime) -> None:
        """Check creator-specific thresholds"""
        try:
            for creator_type, thresholds in self.creator_thresholds.items():
                for threshold_metric, config in thresholds.items():
                    if threshold_metric in metric_key:
                        threshold = config['threshold']
                        severity_str = config['severity']
                        
                        should_alert = False
                        deviation = 0.0
                        
                        if 'latency' in threshold_metric or 'time' in threshold_metric:
                            if value > threshold:
                                should_alert = True
                                deviation = ((value - threshold) / threshold) * 100
                        elif 'rate' in threshold_metric or 'accuracy' in threshold_metric:
                            if value < threshold:
                                should_alert = True
                                deviation = ((threshold - value) / threshold) * 100
                        
                        if should_alert:
                            await self._create_anomaly_alert(
                                metric_key, value, threshold, timestamp,
                                AnomalyType.PERFORMANCE, AnomalySeverity(severity_str),
                                f"Creator threshold exceeded: {threshold_metric}",
                                creator_impact=creator_type
                            )
        
        except Exception as e:
            logger.error(f"Failed to check creator thresholds: {e}")
    
    async def _create_anomaly_alert(self, 
                                  metric_key -> None: str,
                                  actual_value -> None: float,
                                  baseline_value -> None: float,
                                  timestamp -> None: datetime,
                                  anomaly_type -> None: AnomalyType,
                                  severity -> None: AnomalySeverity,
                                  description -> None: str,
                                  creator_impact -> None: str = "unknown") -> None:
        """Create and process anomaly alert"""
        try:
            deviation = ((actual_value - baseline_value) / baseline_value) * 100 if baseline_value != 0 else 0
            
            alert = AnomalyAlert(
                alert_id=str(uuid.uuid4()),
                anomaly_type=anomaly_type,
                severity=severity,
                detection_method=DetectionMethod.STATISTICAL_OUTLIER,
                description=description,
                affected_service=metric_key.split('_')[0] if '_' in metric_key else 'unknown',
                metric_name=metric_key,
                anomaly_score=abs(deviation),
                baseline_value=baseline_value,
                actual_value=actual_value,
                deviation_percentage=deviation,
                detection_time=timestamp,
                creator_impact=creator_impact
            )
            
            self.alerts.append(alert)
            
            # Trigger alert handlers
            for handler in self.alert_handlers:
                asyncio.create_task(handler(alert))
            
            # Keep only recent alerts (last 7 days)
            cutoff = datetime.utcnow() - timedelta(days=7)
            self.alerts = [a for a in self.alerts if a.detection_time >= cutoff]
            
        except Exception as e:
            logger.error(f"Failed to create anomaly alert: {e}")
    
    async def _calculate_severity(self, deviation_percentage: float) -> AnomalySeverity:
        """Calculate severity based on deviation percentage"""
        if deviation_percentage >= 50:
            return AnomalySeverity.CRITICAL
        elif deviation_percentage >= 30:
            return AnomalySeverity.HIGH
        elif deviation_percentage >= 15:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW
    
    async def _periodic_anomaly_check(self) -> None:
        """Periodic comprehensive anomaly check"""
        try:
            # Run detection on all metrics
            for metric_key in self.metric_history:
                if len(self.metric_history[metric_key]) >= 30:
                    service_name = metric_key.split('_')[0] if '_' in metric_key else 'unknown'
                    metric_name = '_'.join(metric_key.split('_')[1:]) if '_' in metric_key else metric_key
                    
                    anomalies = await self.detect_anomalies(metric_name, service_name)
                    
                    # Process new anomalies
                    for anomaly in anomalies:
                        # Check if similar anomaly already exists
                        if not any(a.metric_name == anomaly.metric_name and 
                                 a.detection_time > datetime.utcnow() - timedelta(minutes=30)
                                 for a in self.alerts):
                            self.alerts.append(anomaly)
                            
                            # Trigger alert handlers
                            for handler in self.alert_handlers:
                                asyncio.create_task(handler(anomaly))
            
        except Exception as e:
            logger.error(f"Periodic anomaly check failed: {e}")
    
    async def _update_baseline_models(self) -> None:
        """Update baseline models with recent data"""
        try:
            for metric_key in self.metric_history:
                if len(self.metric_history[metric_key]) >= 100:
                    await self._calculate_baseline(metric_key)
        except Exception as e:
            logger.error(f"Failed to update baseline models: {e}")
    
    async def _calculate_baseline(self, metric_key -> None: str) -> None:
        """Calculate baseline statistics for a metric"""
        try:
            data = list(self.metric_history[metric_key])
            values = [d['value'] for d in data]
            
            if len(values) < 30:
                return
            
            # Calculate baseline statistics
            baseline = {
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
                'min': min(values),
                'max': max(values),
                'q1': np.percentile(values, 25),
                'q3': np.percentile(values, 75),
                'last_updated': datetime.utcnow(),
                'sample_size': len(values)
            }
            
            self.baseline_models[metric_key] = baseline
            
        except Exception as e:
            logger.error(f"Failed to calculate baseline for {metric_key}: {e}")
    
    async def _cleanup_old_data(self) -> None:
        """Cleanup old metric data to prevent memory issues"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=7)
            
            for metric_key in list(self.metric_history.keys()):
                # Remove old data points
                self.metric_history[metric_key] = deque(
                    [d for d in self.metric_history[metric_key] if d['timestamp'] >= cutoff_time],
                    maxlen=10000
                )
                
                # Remove empty metric histories
                if not self.metric_history[metric_key]:
                    del self.metric_history[metric_key]
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
    
    async def _analyze_anomaly_trends(self, alerts: List[AnomalyAlert]) -> Dict[str, Any]:
        """Analyze trends in anomaly patterns"""
        try:
            if not alerts:
                return {}
            
            # Group by day
            daily_counts = defaultdict(int)
            for alert in alerts:
                day_key = alert.detection_time.strftime('%Y-%m-%d')
                daily_counts[day_key] += 1
            
            # Calculate trend
            counts = list(daily_counts.values())
            if len(counts) >= 2:
                recent_avg = statistics.mean(counts[-3:]) if len(counts) >= 3 else counts[-1]
                overall_avg = statistics.mean(counts)
                
                if recent_avg > overall_avg * 1.2:
                    trend = 'increasing'
                elif recent_avg < overall_avg * 0.8:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'
            
            return {
                'trend': trend,
                'daily_average': statistics.mean(counts) if counts else 0,
                'peak_day': max(daily_counts, key=daily_counts.get) if daily_counts else None
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze anomaly trends: {e}")
            return {}
    
    async def _get_top_affected_services(self, alerts: List[AnomalyAlert]) -> List[Dict[str, Any]]:
        """Get services most affected by anomalies"""
        try:
            service_counts = defaultdict(int)
            service_severities = defaultdict(list)
            
            for alert in alerts:
                service_counts[alert.affected_service] += 1
                service_severities[alert.affected_service].append(alert.severity.value)
            
            # Sort by count and add severity info
            top_services = []
            for service, count in sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                severities = service_severities[service]
                critical_count = severities.count('critical')
                high_count = severities.count('high')
                
                top_services.append({
                    'service': service,
                    'anomaly_count': count,
                    'critical_anomalies': critical_count,
                    'high_anomalies': high_count
                })
            
            return top_services
            
        except Exception as e:
            logger.error(f"Failed to get top affected services: {e}")
            return []


# Example usage and testing
async def main() -> None:
    """Example usage of Anomaly Detector"""
    detector = AnomalyDetector()
    
    # Initialize
    await detector.initialize()
    
    # Simulate metric recording
    for i in range(100):
        # Normal values
        normal_value = 100 + np.random.normal(0, 10)
        await detector.record_metric(
            "response_time", normal_value, "api_service"
        )
        
        # Inject anomaly
        if i == 50:
            anomaly_value = 300  # Clear anomaly
            await detector.record_metric(
                "response_time", anomaly_value, "api_service"
            )
    
    # Get summary
    summary = await detector.get_anomaly_summary()
    print(f"Anomaly Summary: {json.dumps(summary, indent=2, default=str)}")


if __name__ == "__main__":
    asyncio.run(main())