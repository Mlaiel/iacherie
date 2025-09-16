"""Quality Assessment Manager - Data Quality Monitoring
=====================================================

Continuous data quality assessment and improvement with real-time monitoring,
quality metrics calculation, SLA tracking, and automated improvement recommendations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import statistics
from collections import defaultdict, deque

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import redis.asyncio as redis


class QualityMetricType(Enum):
    """Types of quality metrics."""
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"
    TIMELINESS = "timeliness"
    CONFORMITY = "conformity"
    INTEGRITY = "integrity"


class AlertSeverity(Enum):
    """Quality alert severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrendDirection(Enum):
    """Quality trend directions."""
    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"
    VOLATILE = "volatile"


@dataclass
class QualityMetric:
    """Data quality metric definition."""
    id: str
    name: str
    metric_type: QualityMetricType
    description: str
    calculation_function: Optional[Callable] = None
    target_value: float = 100.0
    warning_threshold: float = 80.0
    critical_threshold: float = 60.0
    weight: float = 1.0  # Weight in overall quality score
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityMeasurement:
    """Individual quality measurement."""
    id: str
    metric_id: str
    dataset_id: str
    timestamp: datetime
    value: float
    details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityAlert:
    """Data quality alert."""
    id: str
    metric_id: str
    dataset_id: str
    severity: AlertSeverity
    message: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False
    resolution_notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityTrend:
    """Quality trend analysis."""
    metric_id: str
    dataset_id: str
    direction: TrendDirection
    slope: float  # Rate of change
    confidence: float  # Confidence in trend analysis
    period_start: datetime
    period_end: datetime
    measurements_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualitySLA:
    """Quality Service Level Agreement."""
    id: str
    name: str
    dataset_id: str
    metric_requirements: Dict[str, float]  # metric_id -> min_value
    measurement_window: timedelta
    alert_on_breach: bool = True
    escalation_rules: List[Dict[str, Any]] = field(default_factory=list)
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityRecommendation:
    """Quality improvement recommendation."""
    id: str
    dataset_id: str
    metric_id: str
    recommendation_type: str
    title: str
    description: str
    impact_estimate: float
    effort_estimate: str  # "low", "medium", "high"
    priority: int  # 1-5, 1 being highest
    actions: List[str]
    timestamp: datetime
    implemented: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


Base = declarative_base()


class QualityMeasurementModel(Base):
    """Quality measurement database model."""
    __tablename__ = 'quality_measurements'
    
    id = sa.Column(sa.String(36), primary_key=True)
    metric_id = sa.Column(sa.String(36), nullable=False)
    dataset_id = sa.Column(sa.String(100), nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False)
    value = sa.Column(sa.Float, nullable=False)
    details = sa.Column(sa.Text)
    metadata = sa.Column(sa.Text)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)


class QualityAlertModel(Base):
    """Quality alert database model."""
    __tablename__ = 'quality_alerts'
    
    id = sa.Column(sa.String(36), primary_key=True)
    metric_id = sa.Column(sa.String(36), nullable=False)
    dataset_id = sa.Column(sa.String(100), nullable=False)
    severity = sa.Column(sa.String(20), nullable=False)
    message = sa.Column(sa.Text, nullable=False)
    current_value = sa.Column(sa.Float, nullable=False)
    threshold_value = sa.Column(sa.Float, nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False)
    acknowledged = sa.Column(sa.Boolean, default=False)
    resolved = sa.Column(sa.Boolean, default=False)
    resolution_notes = sa.Column(sa.Text)
    metadata = sa.Column(sa.Text)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)


class QualityRecommendationModel(Base):
    """Quality recommendation database model."""
    __tablename__ = 'quality_recommendations'
    
    id = sa.Column(sa.String(36), primary_key=True)
    dataset_id = sa.Column(sa.String(100), nullable=False)
    metric_id = sa.Column(sa.String(36), nullable=False)
    recommendation_type = sa.Column(sa.String(50), nullable=False)
    title = sa.Column(sa.String(200), nullable=False)
    description = sa.Column(sa.Text, nullable=False)
    impact_estimate = sa.Column(sa.Float)
    effort_estimate = sa.Column(sa.String(20))
    priority = sa.Column(sa.Integer)
    actions = sa.Column(sa.Text)
    timestamp = sa.Column(sa.DateTime, nullable=False)
    implemented = sa.Column(sa.Boolean, default=False)
    metadata = sa.Column(sa.Text)


class QualityAssessmentManager:
    """Comprehensive data quality monitoring and assessment manager."""
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        redis_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Database setup
        self.database_url = database_url
        self.engine = None
        self.async_session = None
        
        if database_url:
            self.engine = create_async_engine(database_url)
            self.async_session = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
        
        # Redis setup for real-time data
        self.redis_url = redis_url
        self.redis_client = None
        
        # Quality assessment state
        self.quality_metrics: Dict[str, QualityMetric] = {}
        self.active_measurements: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.quality_slas: Dict[str, QualitySLA] = {}
        self.active_alerts: Dict[str, QualityAlert] = {}
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.measurement_interval = 300  # 5 minutes default
        
        # Performance tracking
        self.assessment_metrics = {
            'total_measurements': 0,
            'total_alerts_generated': 0,
            'average_quality_score': 0.0,
            'sla_compliance_rate': 0.0,
            'recommendations_generated': 0
        }
        
        # Setup built-in quality metrics
        self._setup_built_in_metrics()
    
    async def initialize(self):
        """Initialize the quality assessment manager."""
        # Initialize database if configured
        if self.engine:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        
        # Initialize Redis if configured
        if self.redis_url:
            self.redis_client = redis.from_url(self.redis_url)
        
        self.logger.info("Quality assessment manager initialized")
    
    def _setup_built_in_metrics(self):
        """Setup built-in quality metrics."""
        # Completeness metrics
        completeness_metric = QualityMetric(
            id="field_completeness",
            name="Field Completeness",
            metric_type=QualityMetricType.COMPLETENESS,
            description="Percentage of non-null values in dataset fields",
            calculation_function=self._calculate_completeness,
            target_value=100.0,
            warning_threshold=95.0,
            critical_threshold=90.0,
            weight=1.0
        )
        
        # Accuracy metrics
        accuracy_metric = QualityMetric(
            id="data_accuracy",
            name="Data Accuracy",
            metric_type=QualityMetricType.ACCURACY,
            description="Percentage of values that conform to expected formats and ranges",
            calculation_function=self._calculate_accuracy,
            target_value=100.0,
            warning_threshold=98.0,
            critical_threshold=95.0,
            weight=1.2
        )
        
        # Consistency metrics
        consistency_metric = QualityMetric(
            id="cross_field_consistency",
            name="Cross-field Consistency",
            metric_type=QualityMetricType.CONSISTENCY,
            description="Percentage of records with consistent values across related fields",
            calculation_function=self._calculate_consistency,
            target_value=100.0,
            warning_threshold=98.0,
            critical_threshold=95.0,
            weight=1.1
        )
        
        # Validity metrics
        validity_metric = QualityMetric(
            id="format_validity",
            name="Format Validity",
            metric_type=QualityMetricType.VALIDITY,
            description="Percentage of values that match expected formats",
            calculation_function=self._calculate_validity,
            target_value=100.0,
            warning_threshold=97.0,
            critical_threshold=93.0,
            weight=1.0
        )
        
        # Uniqueness metrics
        uniqueness_metric = QualityMetric(
            id="record_uniqueness",
            name="Record Uniqueness",
            metric_type=QualityMetricType.UNIQUENESS,
            description="Percentage of unique records in dataset",
            calculation_function=self._calculate_uniqueness,
            target_value=100.0,
            warning_threshold=99.0,
            critical_threshold=95.0,
            weight=0.8
        )
        
        # Timeliness metrics
        timeliness_metric = QualityMetric(
            id="data_timeliness",
            name="Data Timeliness",
            metric_type=QualityMetricType.TIMELINESS,
            description="Percentage of records updated within acceptable time window",
            calculation_function=self._calculate_timeliness,
            target_value=100.0,
            warning_threshold=90.0,
            critical_threshold=80.0,
            weight=0.9
        )
        
        # Register built-in metrics
        for metric in [completeness_metric, accuracy_metric, consistency_metric, 
                      validity_metric, uniqueness_metric, timeliness_metric]:
            self.quality_metrics[metric.id] = metric
    
    def register_quality_metric(self, metric: QualityMetric):
        """Register a custom quality metric."""
        self.quality_metrics[metric.id] = metric
        self.logger.info(f"Registered quality metric: {metric.name}")
    
    def register_quality_sla(self, sla: QualitySLA):
        """Register a quality SLA."""
        self.quality_slas[sla.id] = sla
        self.logger.info(f"Registered quality SLA: {sla.name}")
    
    async def start_monitoring(self, datasets: List[str], interval: int = 300):
        """Start continuous quality monitoring for datasets."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.measurement_interval = interval
        
        for dataset_id in datasets:
            task = asyncio.create_task(self._monitor_dataset_quality(dataset_id))
            self.monitoring_tasks[dataset_id] = task
        
        # Start background tasks
        asyncio.create_task(self._alert_processor())
        asyncio.create_task(self._trend_analyzer())
        asyncio.create_task(self._sla_monitor())
        asyncio.create_task(self._recommendation_generator())
        
        self.logger.info(f"Started quality monitoring for {len(datasets)} datasets")
    
    async def stop_monitoring(self):
        """Stop quality monitoring."""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        
        # Cancel all monitoring tasks
        for task in self.monitoring_tasks.values():
            task.cancel()
        
        if self.monitoring_tasks:
            await asyncio.gather(*self.monitoring_tasks.values(), return_exceptions=True)
        
        self.monitoring_tasks.clear()
        self.logger.info("Stopped quality monitoring")
    
    async def _monitor_dataset_quality(self, dataset_id: str):
        """Monitor quality for a specific dataset."""
        while self.monitoring_active:
            try:
                # Measure quality for all enabled metrics
                for metric in self.quality_metrics.values():
                    if metric.enabled:
                        measurement = await self._measure_quality(dataset_id, metric)
                        if measurement:
                            await self._process_measurement(measurement)
                
                await asyncio.sleep(self.measurement_interval)
                
            except Exception as e:
                self.logger.error(f"Error monitoring dataset {dataset_id}: {e}")
                await asyncio.sleep(60)  # Short delay before retry
    
    async def _measure_quality(self, dataset_id: str, metric: QualityMetric) -> Optional[QualityMeasurement]:
        """Measure quality for a specific metric and dataset."""
        try:
            # Get dataset data (this would be implemented based on data source)
            data = await self._get_dataset_data(dataset_id)
            
            if not data:
                return None
            
            # Calculate metric value
            if metric.calculation_function:
                value = await metric.calculation_function(data, metric)
            else:
                value = 0.0  # Default value if no calculation function
            
            # Create measurement
            measurement = QualityMeasurement(
                id=str(uuid.uuid4()),
                metric_id=metric.id,
                dataset_id=dataset_id,
                timestamp=datetime.utcnow(),
                value=value,
                details={
                    'records_analyzed': len(data),
                    'metric_type': metric.metric_type.value
                }
            )
            
            return measurement
            
        except Exception as e:
            self.logger.error(f"Error measuring quality for metric {metric.id}: {e}")
            return None
    
    async def _process_measurement(self, measurement: QualityMeasurement):
        """Process a quality measurement."""
        # Store measurement
        if self.async_session:
            await self._store_measurement(measurement)
        
        # Add to active measurements for trend analysis
        key = f"{measurement.dataset_id}:{measurement.metric_id}"
        self.active_measurements[key].append(measurement)
        
        # Check for alerts
        await self._check_alert_conditions(measurement)
        
        # Update metrics
        self.assessment_metrics['total_measurements'] += 1
        
        # Update average quality score
        total_measurements = self.assessment_metrics['total_measurements']
        current_avg = self.assessment_metrics['average_quality_score']
        self.assessment_metrics['average_quality_score'] = (
            (current_avg * (total_measurements - 1) + measurement.value) / total_measurements
        )
    
    async def _check_alert_conditions(self, measurement: QualityMeasurement):
        """Check if measurement triggers any alerts."""
        metric = self.quality_metrics.get(measurement.metric_id)
        if not metric:
            return
        
        alert_severity = None
        threshold_value = None
        
        if measurement.value <= metric.critical_threshold:
            alert_severity = AlertSeverity.CRITICAL
            threshold_value = metric.critical_threshold
        elif measurement.value <= metric.warning_threshold:
            alert_severity = AlertSeverity.HIGH
            threshold_value = metric.warning_threshold
        
        if alert_severity:
            alert = QualityAlert(
                id=str(uuid.uuid4()),
                metric_id=measurement.metric_id,
                dataset_id=measurement.dataset_id,
                severity=alert_severity,
                message=f"Quality metric '{metric.name}' is below threshold",
                current_value=measurement.value,
                threshold_value=threshold_value,
                timestamp=measurement.timestamp
            )
            
            await self._create_alert(alert)
    
    async def _create_alert(self, alert: QualityAlert):
        """Create and process a quality alert."""
        # Check for duplicate alerts
        alert_key = f"{alert.dataset_id}:{alert.metric_id}:{alert.severity.value}"
        
        # Only create alert if not already active
        if alert_key not in self.active_alerts:
            self.active_alerts[alert_key] = alert
            
            # Store alert
            if self.async_session:
                await self._store_alert(alert)
            
            # Update metrics
            self.assessment_metrics['total_alerts_generated'] += 1
            
            # Send notifications (if configured)
            await self._send_alert_notification(alert)
            
            self.logger.warning(f"Quality alert created: {alert.message} "
                              f"(Value: {alert.current_value:.2f}, "
                              f"Threshold: {alert.threshold_value:.2f})")
    
    async def _send_alert_notification(self, alert: QualityAlert):
        """Send alert notification (placeholder for notification system)."""
        # This would integrate with notification systems like email, Slack, etc.
        notification_data = {
            'alert_id': alert.id,
            'severity': alert.severity.value,
            'message': alert.message,
            'dataset': alert.dataset_id,
            'metric': alert.metric_id,
            'current_value': alert.current_value,
            'threshold': alert.threshold_value,
            'timestamp': alert.timestamp.isoformat()
        }
        
        # Store notification request in Redis for pickup by notification service
        if self.redis_client:
            await self.redis_client.lpush('quality_alerts', json.dumps(notification_data))
    
    async def _alert_processor(self):
        """Background task to process and manage alerts."""
        while self.monitoring_active:
            try:
                # Auto-resolve alerts that are no longer relevant
                current_time = datetime.utcnow()
                resolved_alerts = []
                
                for alert_key, alert in list(self.active_alerts.items()):
                    # Check if alert should be auto-resolved
                    if (current_time - alert.timestamp).total_seconds() > 3600:  # 1 hour
                        # Get latest measurement for this metric/dataset
                        latest_measurement = await self._get_latest_measurement(
                            alert.dataset_id, alert.metric_id
                        )
                        
                        if latest_measurement and latest_measurement.value > alert.threshold_value:
                            alert.resolved = True
                            alert.resolution_notes = "Auto-resolved: metric value improved above threshold"
                            resolved_alerts.append(alert_key)
                            
                            # Update database
                            if self.async_session:
                                await self._update_alert_status(alert)
                
                # Remove resolved alerts from active list
                for alert_key in resolved_alerts:
                    del self.active_alerts[alert_key]
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in alert processor: {e}")
                await asyncio.sleep(60)
    
    async def _trend_analyzer(self):
        """Background task to analyze quality trends."""
        while self.monitoring_active:
            try:
                # Analyze trends for each dataset/metric combination
                for key, measurements in self.active_measurements.items():
                    if len(measurements) >= 10:  # Need minimum measurements for trend analysis
                        dataset_id, metric_id = key.split(':', 1)
                        trend = await self._analyze_trend(dataset_id, metric_id, list(measurements))
                        
                        if trend:
                            await self._process_trend(trend)
                
                await asyncio.sleep(900)  # Analyze trends every 15 minutes
                
            except Exception as e:
                self.logger.error(f"Error in trend analyzer: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_trend(self, dataset_id: str, metric_id: str, measurements: List[QualityMeasurement]) -> Optional[QualityTrend]:
        """Analyze quality trend for specific metric/dataset."""
        if len(measurements) < 10:
            return None
        
        # Sort measurements by timestamp
        sorted_measurements = sorted(measurements, key=lambda m: m.timestamp)
        
        # Calculate trend using linear regression
        values = [m.value for m in sorted_measurements]
        timestamps = [(m.timestamp - sorted_measurements[0].timestamp).total_seconds() for m in sorted_measurements]
        
        # Simple linear regression
        n = len(values)
        sum_x = sum(timestamps)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(timestamps, values))
        sum_x2 = sum(x * x for x in timestamps)
        
        # Calculate slope
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Determine trend direction
        if abs(slope) < 0.01:  # Threshold for stability
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.IMPROVING
        else:
            direction = TrendDirection.DEGRADING
        
        # Calculate confidence (R-squared)
        mean_y = sum_y / n
        ss_tot = sum((y - mean_y) ** 2 for y in values)
        ss_res = sum((values[i] - (slope * timestamps[i] + (sum_y - slope * sum_x) / n)) ** 2 for i in range(n))
        confidence = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Check for volatility
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        mean_value = statistics.mean(values)
        coefficient_of_variation = std_dev / mean_value if mean_value > 0 else 0
        
        if coefficient_of_variation > 0.2:  # High variability
            direction = TrendDirection.VOLATILE
        
        return QualityTrend(
            metric_id=metric_id,
            dataset_id=dataset_id,
            direction=direction,
            slope=slope,
            confidence=confidence,
            period_start=sorted_measurements[0].timestamp,
            period_end=sorted_measurements[-1].timestamp,
            measurements_count=len(measurements)
        )
    
    async def _process_trend(self, trend: QualityTrend):
        """Process quality trend analysis."""
        # Log significant trends
        if trend.direction in [TrendDirection.DEGRADING, TrendDirection.VOLATILE] and trend.confidence > 0.7:
            self.logger.warning(f"Quality trend alert: {trend.metric_id} for {trend.dataset_id} "
                              f"is {trend.direction.value} (confidence: {trend.confidence:.2f})")
            
            # Generate recommendation for degrading trends
            if trend.direction == TrendDirection.DEGRADING:
                await self._generate_trend_based_recommendation(trend)
    
    async def _sla_monitor(self):
        """Background task to monitor SLA compliance."""
        while self.monitoring_active:
            try:
                compliance_results = []
                
                for sla in self.quality_slas.values():
                    if sla.enabled:
                        compliance = await self._check_sla_compliance(sla)
                        compliance_results.append(compliance)
                        
                        if not compliance:
                            await self._handle_sla_breach(sla)
                
                # Update overall SLA compliance rate
                if compliance_results:
                    self.assessment_metrics['sla_compliance_rate'] = (
                        sum(compliance_results) / len(compliance_results) * 100
                    )
                
                await asyncio.sleep(600)  # Check SLA compliance every 10 minutes
                
            except Exception as e:
                self.logger.error(f"Error in SLA monitor: {e}")
                await asyncio.sleep(60)
    
    async def _check_sla_compliance(self, sla: QualitySLA) -> bool:
        """Check if SLA requirements are met."""
        try:
            # Get measurements within the SLA window
            current_time = datetime.utcnow()
            window_start = current_time - sla.measurement_window
            
            for metric_id, min_value in sla.metric_requirements.items():
                # Get recent measurements for this metric
                measurements = await self._get_measurements_in_window(
                    sla.dataset_id, metric_id, window_start, current_time
                )
                
                if not measurements:
                    return False  # No data available
                
                # Check if all measurements meet minimum value
                for measurement in measurements:
                    if measurement.value < min_value:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking SLA compliance: {e}")
            return False
    
    async def _handle_sla_breach(self, sla: QualitySLA):
        """Handle SLA breach."""
        self.logger.error(f"SLA breach detected for {sla.name} (Dataset: {sla.dataset_id})")
        
        if sla.alert_on_breach:
            # Create critical alert for SLA breach
            alert = QualityAlert(
                id=str(uuid.uuid4()),
                metric_id="sla_breach",
                dataset_id=sla.dataset_id,
                severity=AlertSeverity.CRITICAL,
                message=f"SLA breach: {sla.name}",
                current_value=0.0,
                threshold_value=100.0,
                timestamp=datetime.utcnow(),
                metadata={'sla_id': sla.id, 'sla_name': sla.name}
            )
            
            await self._create_alert(alert)
        
        # Execute escalation rules
        for rule in sla.escalation_rules:
            await self._execute_escalation_rule(rule, sla)
    
    async def _execute_escalation_rule(self, rule: Dict[str, Any], sla: QualitySLA):
        """Execute SLA escalation rule."""
        rule_type = rule.get('type')
        
        if rule_type == 'notification':
            # Send escalation notification
            notification_data = {
                'type': 'sla_escalation',
                'sla_id': sla.id,
                'sla_name': sla.name,
                'dataset_id': sla.dataset_id,
                'recipients': rule.get('recipients', []),
                'message': rule.get('message', f"SLA breach escalation for {sla.name}"),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if self.redis_client:
                await self.redis_client.lpush('sla_escalations', json.dumps(notification_data))
        
        elif rule_type == 'auto_remediation':
            # Trigger automated remediation
            remediation_data = {
                'sla_id': sla.id,
                'dataset_id': sla.dataset_id,
                'actions': rule.get('actions', []),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if self.redis_client:
                await self.redis_client.lpush('auto_remediations', json.dumps(remediation_data))
    
    async def _recommendation_generator(self):
        """Background task to generate quality improvement recommendations."""
        while self.monitoring_active:
            try:
                # Generate recommendations based on current quality state
                for dataset_id in set(measurement.dataset_id for measurements in self.active_measurements.values() for measurement in measurements):
                    recommendations = await self._generate_quality_recommendations(dataset_id)
                    
                    for recommendation in recommendations:
                        await self._store_recommendation(recommendation)
                        self.assessment_metrics['recommendations_generated'] += 1
                
                await asyncio.sleep(3600)  # Generate recommendations every hour
                
            except Exception as e:
                self.logger.error(f"Error in recommendation generator: {e}")
                await asyncio.sleep(300)
    
    async def _generate_quality_recommendations(self, dataset_id: str) -> List[QualityRecommendation]:
        """Generate quality improvement recommendations for a dataset."""
        recommendations = []
        
        # Analyze current quality state
        quality_summary = await self._get_quality_summary(dataset_id)
        
        for metric_id, score in quality_summary.items():
            metric = self.quality_metrics.get(metric_id)
            if not metric:
                continue
            
            if score < metric.warning_threshold:
                recommendation = await self._generate_metric_recommendation(dataset_id, metric, score)
                if recommendation:
                    recommendations.append(recommendation)
        
        return recommendations
    
    async def _generate_metric_recommendation(self, dataset_id: str, metric: QualityMetric, current_score: float) -> Optional[QualityRecommendation]:
        """Generate recommendation for specific metric."""
        recommendation_type = f"{metric.metric_type.value}_improvement"
        
        # Generate recommendations based on metric type
        if metric.metric_type == QualityMetricType.COMPLETENESS:
            return QualityRecommendation(
                id=str(uuid.uuid4()),
                dataset_id=dataset_id,
                metric_id=metric.id,
                recommendation_type=recommendation_type,
                title="Improve Data Completeness",
                description=f"Current completeness score is {current_score:.1f}%. Consider implementing data validation rules and mandatory field checks.",
                impact_estimate=min(metric.target_value - current_score, 20.0),
                effort_estimate="medium",
                priority=2,
                actions=[
                    "Add validation rules for required fields",
                    "Implement data entry forms with mandatory field validation",
                    "Review data collection processes",
                    "Set up alerts for incomplete data submissions"
                ],
                timestamp=datetime.utcnow()
            )
        
        elif metric.metric_type == QualityMetricType.ACCURACY:
            return QualityRecommendation(
                id=str(uuid.uuid4()),
                dataset_id=dataset_id,
                metric_id=metric.id,
                recommendation_type=recommendation_type,
                title="Enhance Data Accuracy",
                description=f"Current accuracy score is {current_score:.1f}%. Consider implementing format validation and range checks.",
                impact_estimate=min(metric.target_value - current_score, 15.0),
                effort_estimate="high",
                priority=1,
                actions=[
                    "Implement format validation rules",
                    "Add range and boundary checks",
                    "Create data type validation",
                    "Review and update business rules",
                    "Implement automated data cleansing"
                ],
                timestamp=datetime.utcnow()
            )
        
        elif metric.metric_type == QualityMetricType.CONSISTENCY:
            return QualityRecommendation(
                id=str(uuid.uuid4()),
                dataset_id=dataset_id,
                metric_id=metric.id,
                recommendation_type=recommendation_type,
                title="Improve Data Consistency",
                description=f"Current consistency score is {current_score:.1f}%. Consider implementing cross-field validation rules.",
                impact_estimate=min(metric.target_value - current_score, 18.0),
                effort_estimate="medium",
                priority=2,
                actions=[
                    "Define cross-field validation rules",
                    "Implement referential integrity checks",
                    "Create data standardization procedures",
                    "Review data entry workflows"
                ],
                timestamp=datetime.utcnow()
            )
        
        elif metric.metric_type == QualityMetricType.UNIQUENESS:
            return QualityRecommendation(
                id=str(uuid.uuid4()),
                dataset_id=dataset_id,
                metric_id=metric.id,
                recommendation_type=recommendation_type,
                title="Eliminate Duplicate Records",
                description=f"Current uniqueness score is {current_score:.1f}%. Consider implementing duplicate detection and removal processes.",
                impact_estimate=min(metric.target_value - current_score, 25.0),
                effort_estimate="low",
                priority=3,
                actions=[
                    "Implement duplicate detection algorithms",
                    "Create data deduplication procedures",
                    "Add unique constraints where appropriate",
                    "Review data integration processes"
                ],
                timestamp=datetime.utcnow()
            )
        
        return None
    
    async def _generate_trend_based_recommendation(self, trend: QualityTrend):
        """Generate recommendation based on quality trend."""
        recommendation = QualityRecommendation(
            id=str(uuid.uuid4()),
            dataset_id=trend.dataset_id,
            metric_id=trend.metric_id,
            recommendation_type="trend_improvement",
            title=f"Address Degrading Quality Trend",
            description=f"Quality metric is showing a {trend.direction.value} trend with {trend.confidence:.1%} confidence. Immediate attention required.",
            impact_estimate=abs(trend.slope) * 10,  # Estimated impact based on trend slope
            effort_estimate="high",
            priority=1,
            actions=[
                "Investigate root cause of quality degradation",
                "Review recent changes to data sources or processes",
                "Implement additional monitoring and alerts",
                "Consider temporary data quality checkpoints"
            ],
            timestamp=datetime.utcnow(),
            metadata={
                'trend_slope': trend.slope,
                'trend_confidence': trend.confidence,
                'trend_direction': trend.direction.value
            }
        )
        
        await self._store_recommendation(recommendation)
    
    # Data access methods (these would be implemented based on actual data sources)
    async def _get_dataset_data(self, dataset_id: str) -> List[Dict[str, Any]]:
        """Get dataset data for quality measurement."""
        # This is a placeholder - actual implementation would depend on data source
        # Could fetch from database, file, API, etc.
        return []
    
    async def _get_latest_measurement(self, dataset_id: str, metric_id: str) -> Optional[QualityMeasurement]:
        """Get latest quality measurement."""
        key = f"{dataset_id}:{metric_id}"
        if key in self.active_measurements and self.active_measurements[key]:
            return self.active_measurements[key][-1]
        return None
    
    async def _get_measurements_in_window(self, dataset_id: str, metric_id: str, start_time: datetime, end_time: datetime) -> List[QualityMeasurement]:
        """Get measurements within time window."""
        key = f"{dataset_id}:{metric_id}"
        if key not in self.active_measurements:
            return []
        
        return [
            m for m in self.active_measurements[key]
            if start_time <= m.timestamp <= end_time
        ]
    
    async def _get_quality_summary(self, dataset_id: str) -> Dict[str, float]:
        """Get current quality scores for all metrics in dataset."""
        summary = {}
        
        for metric_id in self.quality_metrics.keys():
            latest_measurement = await self._get_latest_measurement(dataset_id, metric_id)
            if latest_measurement:
                summary[metric_id] = latest_measurement.value
        
        return summary
    
    # Built-in quality calculation functions
    async def _calculate_completeness(self, data: List[Dict[str, Any]], metric: QualityMetric) -> float:
        """Calculate completeness score."""
        if not data:
            return 0.0
        
        total_fields = 0
        non_null_fields = 0
        
        for record in data:
            for field, value in record.items():
                total_fields += 1
                if value is not None and str(value).strip() != "":
                    non_null_fields += 1
        
        return (non_null_fields / total_fields * 100) if total_fields > 0 else 0.0
    
    async def _calculate_accuracy(self, data: List[Dict[str, Any]], metric: QualityMetric) -> float:
        """Calculate accuracy score."""
        if not data:
            return 0.0
        
        # This is a simplified accuracy calculation
        # Real implementation would use validation rules
        return 95.0  # Placeholder
    
    async def _calculate_consistency(self, data: List[Dict[str, Any]], metric: QualityMetric) -> float:
        """Calculate consistency score."""
        if not data:
            return 0.0
        
        # This is a simplified consistency calculation
        # Real implementation would check cross-field relationships
        return 98.0  # Placeholder
    
    async def _calculate_validity(self, data: List[Dict[str, Any]], metric: QualityMetric) -> float:
        """Calculate validity score."""
        if not data:
            return 0.0
        
        # This is a simplified validity calculation
        # Real implementation would use format validation
        return 97.0  # Placeholder
    
    async def _calculate_uniqueness(self, data: List[Dict[str, Any]], metric: QualityMetric) -> float:
        """Calculate uniqueness score."""
        if not data:
            return 0.0
        
        # Calculate uniqueness based on all fields combined
        records_str = [json.dumps(record, sort_keys=True) for record in data]
        unique_records = len(set(records_str))
        total_records = len(records_str)
        
        return (unique_records / total_records * 100) if total_records > 0 else 0.0
    
    async def _calculate_timeliness(self, data: List[Dict[str, Any]], metric: QualityMetric) -> float:
        """Calculate timeliness score."""
        if not data:
            return 0.0
        
        # This is a simplified timeliness calculation
        # Real implementation would check record timestamps
        return 92.0  # Placeholder
    
    # Database operations
    async def _store_measurement(self, measurement: QualityMeasurement):
        """Store quality measurement to database."""
        try:
            async with self.async_session() as session:
                db_measurement = QualityMeasurementModel(
                    id=measurement.id,
                    metric_id=measurement.metric_id,
                    dataset_id=measurement.dataset_id,
                    timestamp=measurement.timestamp,
                    value=measurement.value,
                    details=json.dumps(measurement.details),
                    metadata=json.dumps(measurement.metadata)
                )
                session.add(db_measurement)
                await session.commit()
        except Exception as e:
            self.logger.error(f"Error storing measurement: {e}")
    
    async def _store_alert(self, alert: QualityAlert):
        """Store quality alert to database."""
        try:
            async with self.async_session() as session:
                db_alert = QualityAlertModel(
                    id=alert.id,
                    metric_id=alert.metric_id,
                    dataset_id=alert.dataset_id,
                    severity=alert.severity.value,
                    message=alert.message,
                    current_value=alert.current_value,
                    threshold_value=alert.threshold_value,
                    timestamp=alert.timestamp,
                    acknowledged=alert.acknowledged,
                    resolved=alert.resolved,
                    resolution_notes=alert.resolution_notes,
                    metadata=json.dumps(alert.metadata)
                )
                session.add(db_alert)
                await session.commit()
        except Exception as e:
            self.logger.error(f"Error storing alert: {e}")
    
    async def _store_recommendation(self, recommendation: QualityRecommendation):
        """Store quality recommendation to database."""
        try:
            async with self.async_session() as session:
                db_recommendation = QualityRecommendationModel(
                    id=recommendation.id,
                    dataset_id=recommendation.dataset_id,
                    metric_id=recommendation.metric_id,
                    recommendation_type=recommendation.recommendation_type,
                    title=recommendation.title,
                    description=recommendation.description,
                    impact_estimate=recommendation.impact_estimate,
                    effort_estimate=recommendation.effort_estimate,
                    priority=recommendation.priority,
                    actions=json.dumps(recommendation.actions),
                    timestamp=recommendation.timestamp,
                    implemented=recommendation.implemented,
                    metadata=json.dumps(recommendation.metadata)
                )
                session.add(db_recommendation)
                await session.commit()
        except Exception as e:
            self.logger.error(f"Error storing recommendation: {e}")
    
    async def _update_alert_status(self, alert: QualityAlert):
        """Update alert status in database."""
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    sa.select(QualityAlertModel).where(QualityAlertModel.id == alert.id)
                )
                db_alert = result.scalar_one_or_none()
                
                if db_alert:
                    db_alert.acknowledged = alert.acknowledged
                    db_alert.resolved = alert.resolved
                    db_alert.resolution_notes = alert.resolution_notes
                    await session.commit()
        except Exception as e:
            self.logger.error(f"Error updating alert status: {e}")
    
    def get_assessment_metrics(self) -> Dict[str, Any]:
        """Get assessment performance metrics."""
        return self.assessment_metrics.copy()
    
    async def get_active_alerts(self, dataset_id: Optional[str] = None) -> List[QualityAlert]:
        """Get active quality alerts."""
        alerts = list(self.active_alerts.values())
        
        if dataset_id:
            alerts = [alert for alert in alerts if alert.dataset_id == dataset_id]
        
        return alerts
    
    async def acknowledge_alert(self, alert_id: str, notes: Optional[str] = None) -> bool:
        """Acknowledge a quality alert."""
        for alert in self.active_alerts.values():
            if alert.id == alert_id:
                alert.acknowledged = True
                if notes:
                    alert.resolution_notes = notes
                
                await self._update_alert_status(alert)
                return True
        
        return False
    
    async def resolve_alert(self, alert_id: str, notes: Optional[str] = None) -> bool:
        """Resolve a quality alert."""
        for alert_key, alert in list(self.active_alerts.items()):
            if alert.id == alert_id:
                alert.resolved = True
                if notes:
                    alert.resolution_notes = notes
                
                await self._update_alert_status(alert)
                del self.active_alerts[alert_key]
                return True
        
        return False


# Example usage
if __name__ == "__main__":
    async def main():
        # Initialize quality assessment manager
        manager = QualityAssessmentManager(
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            redis_url="redis://localhost:6379"
        )
        
        await manager.initialize()
        
        # Define quality SLA
        user_data_sla = QualitySLA(
            id="user_data_sla",
            name="User Data Quality SLA",
            dataset_id="user_profiles",
            metric_requirements={
                "field_completeness": 95.0,
                "data_accuracy": 98.0,
                "format_validity": 97.0
            },
            measurement_window=timedelta(hours=1),
            alert_on_breach=True,
            escalation_rules=[
                {
                    "type": "notification",
                    "recipients": ["admin@example.com"],
                    "message": "User data quality SLA breach detected"
                }
            ]
        )
        
        manager.register_quality_sla(user_data_sla)
        
        # Start monitoring
        await manager.start_monitoring(["user_profiles"], interval=300)
        
        # Let it run for a while
        await asyncio.sleep(30)
        
        # Check metrics
        metrics = manager.get_assessment_metrics()
        print(f"Assessment metrics: {metrics}")
        
        # Check active alerts
        alerts = await manager.get_active_alerts()
        print(f"Active alerts: {len(alerts)}")
        
        await manager.stop_monitoring()
    
    asyncio.run(main())