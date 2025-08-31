"""
IA Influencer Agent - Recovery Metrics Collector
Comprehensive disaster recovery metrics collection and analysis

This module provides detailed metrics collection for disaster recovery:
- RTO/RPO compliance tracking and reporting
- Recovery performance analytics and trends
- Business impact assessment and cost analysis
- SLA compliance monitoring and penalties tracking
- Recovery efficiency optimization recommendations

Author: Fahed Mlaiel <mlaiel@live.de>
License: Proprietary - All rights reserved
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, deque

from backend.core.database import DatabaseManager
from backend.core.config import Config
from backend.utils.metrics import MetricsCollector


class MetricType(Enum):
    """Types of recovery metrics"""
    RTO_COMPLIANCE = "rto_compliance"
    RPO_COMPLIANCE = "rpo_compliance"
    RECOVERY_TIME = "recovery_time"
    BUSINESS_IMPACT = "business_impact"
    COST_ANALYSIS = "cost_analysis"
    SLA_COMPLIANCE = "sla_compliance"
    AVAILABILITY = "availability"
    PERFORMANCE = "performance"


class MetricGranularity(Enum):
    """Metric collection granularity"""
    REAL_TIME = "real_time"      # Every minute
    HIGH_FREQUENCY = "high_frequency"  # Every 5 minutes
    STANDARD = "standard"        # Every 15 minutes
    LOW_FREQUENCY = "low_frequency"    # Every hour
    DAILY = "daily"             # Once per day


@dataclass
class RecoveryMetric:
    """Recovery metric definition and configuration"""
    metric_id: str
    name: str
    description: str
    metric_type: MetricType
    granularity: MetricGranularity
    aggregation_method: str  # sum, average, max, min, count
    unit: str
    target_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    enabled: bool = True
    retention_days: int = 365


@dataclass
class MetricDataPoint:
    """Individual metric data point"""
    metric_id: str
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricSummary:
    """Metric summary and statistics"""
    metric_id: str
    period_start: datetime
    period_end: datetime
    count: int
    sum_value: float
    min_value: float
    max_value: float
    avg_value: float
    std_deviation: float
    percentiles: Dict[str, float]
    trend_direction: str  # "increasing", "decreasing", "stable"


class RecoveryMetricsCollector:
    """
    Comprehensive recovery metrics collection and analysis system
    
    Features:
    - Multi-granularity metric collection (real-time to daily)
    - RTO/RPO compliance tracking with automated alerting
    - Business impact cost analysis and trend prediction
    - SLA compliance monitoring with penalty calculation
    - Recovery performance optimization recommendations
    - Historical trend analysis and forecasting
    """

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.db_manager = DatabaseManager(config)
        self.metrics = MetricsCollector()
        
        # Metrics collection state
        self.metric_definitions: Dict[str, RecoveryMetric] = {}
        self.metric_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.collection_tasks: Dict[str, asyncio.Task] = {}
        
        # Aggregated metrics storage
        self.hourly_aggregates: Dict[str, List[MetricSummary]] = defaultdict(list)
        self.daily_aggregates: Dict[str, List[MetricSummary]] = defaultdict(list)
        self.weekly_aggregates: Dict[str, List[MetricSummary]] = defaultdict(list)
        
        # Performance tracking
        self.collection_performance = {
            'total_metrics_collected': 0,
            'collection_errors': 0,
            'average_collection_time': 0.0,
            'storage_efficiency': 0.0,
            'alert_accuracy': 0.0
        }
        
        # Alert thresholds and configurations
        self.alert_configurations = self._initialize_alert_configurations()
        
        # Initialize core recovery metrics
        self._initialize_core_metrics()

    def _initialize_core_metrics(self):
        """Initialize core disaster recovery metrics"""
        core_metrics = [
            {
                'metric_id': 'rto_compliance_percentage',
                'name': 'RTO Compliance Percentage',
                'description': 'Percentage of recovery operations meeting RTO requirements',
                'metric_type': MetricType.RTO_COMPLIANCE,
                'granularity': MetricGranularity.STANDARD,
                'aggregation_method': 'average',
                'unit': 'percentage',
                'target_value': 99.0,
                'warning_threshold': 95.0,
                'critical_threshold': 90.0
            },
            {
                'metric_id': 'rpo_compliance_percentage',
                'name': 'RPO Compliance Percentage',
                'description': 'Percentage of recovery operations meeting RPO requirements',
                'metric_type': MetricType.RPO_COMPLIANCE,
                'granularity': MetricGranularity.STANDARD,
                'aggregation_method': 'average',
                'unit': 'percentage',
                'target_value': 99.5,
                'warning_threshold': 97.0,
                'critical_threshold': 95.0
            },
            {
                'metric_id': 'mean_time_to_recovery',
                'name': 'Mean Time to Recovery (MTTR)',
                'description': 'Average time to complete recovery operations',
                'metric_type': MetricType.RECOVERY_TIME,
                'granularity': MetricGranularity.HIGH_FREQUENCY,
                'aggregation_method': 'average',
                'unit': 'seconds',
                'target_value': 1800.0,  # 30 minutes
                'warning_threshold': 3600.0,  # 1 hour
                'critical_threshold': 7200.0   # 2 hours
            },
            {
                'metric_id': 'recovery_success_rate',
                'name': 'Recovery Success Rate',
                'description': 'Percentage of successful recovery operations',
                'metric_type': MetricType.PERFORMANCE,
                'granularity': MetricGranularity.STANDARD,
                'aggregation_method': 'average',
                'unit': 'percentage',
                'target_value': 99.9,
                'warning_threshold': 98.0,
                'critical_threshold': 95.0
            },
            {
                'metric_id': 'business_impact_cost_per_hour',
                'name': 'Business Impact Cost per Hour',
                'description': 'Financial cost of business impact during outages',
                'metric_type': MetricType.BUSINESS_IMPACT,
                'granularity': MetricGranularity.REAL_TIME,
                'aggregation_method': 'sum',
                'unit': 'EUR',
                'warning_threshold': 10000.0,  # €10k/hour
                'critical_threshold': 50000.0   # €50k/hour
            },
            {
                'metric_id': 'system_availability_percentage',
                'name': 'System Availability Percentage',
                'description': 'Overall system availability including recovery periods',
                'metric_type': MetricType.AVAILABILITY,
                'granularity': MetricGranularity.HIGH_FREQUENCY,
                'aggregation_method': 'average',
                'unit': 'percentage',
                'target_value': 99.99,
                'warning_threshold': 99.9,
                'critical_threshold': 99.5
            },
            {
                'metric_id': 'data_loss_incidents',
                'name': 'Data Loss Incidents',
                'description': 'Number of incidents involving data loss',
                'metric_type': MetricType.PERFORMANCE,
                'granularity': MetricGranularity.REAL_TIME,
                'aggregation_method': 'count',
                'unit': 'count',
                'target_value': 0.0,
                'warning_threshold': 1.0,
                'critical_threshold': 3.0
            },
            {
                'metric_id': 'sla_penalty_cost',
                'name': 'SLA Penalty Cost',
                'description': 'Financial penalties due to SLA breaches',
                'metric_type': MetricType.SLA_COMPLIANCE,
                'granularity': MetricGranularity.DAILY,
                'aggregation_method': 'sum',
                'unit': 'EUR',
                'target_value': 0.0,
                'warning_threshold': 1000.0,
                'critical_threshold': 5000.0
            },
            {
                'metric_id': 'backup_success_rate',
                'name': 'Backup Success Rate',
                'description': 'Percentage of successful backup operations',
                'metric_type': MetricType.PERFORMANCE,
                'granularity': MetricGranularity.STANDARD,
                'aggregation_method': 'average',
                'unit': 'percentage',
                'target_value': 100.0,
                'warning_threshold': 98.0,
                'critical_threshold': 95.0
            },
            {
                'metric_id': 'failover_trigger_time',
                'name': 'Failover Trigger Time',
                'description': 'Time to detect failure and trigger failover',
                'metric_type': MetricType.PERFORMANCE,
                'granularity': MetricGranularity.HIGH_FREQUENCY,
                'aggregation_method': 'average',
                'unit': 'seconds',
                'target_value': 30.0,   # 30 seconds
                'warning_threshold': 60.0,  # 1 minute
                'critical_threshold': 300.0  # 5 minutes
            }
        ]
        
        for metric_config in core_metrics:
            recovery_metric = RecoveryMetric(
                metric_id=metric_config['metric_id'],
                name=metric_config['name'],
                description=metric_config['description'],
                metric_type=metric_config['metric_type'],
                granularity=metric_config['granularity'],
                aggregation_method=metric_config['aggregation_method'],
                unit=metric_config['unit'],
                target_value=metric_config.get('target_value'),
                warning_threshold=metric_config.get('warning_threshold'),
                critical_threshold=metric_config.get('critical_threshold')
            )
            
            self.metric_definitions[metric_config['metric_id']] = recovery_metric

    def _initialize_alert_configurations(self) -> Dict[str, Dict[str, Any]]:
        """Initialize alert configurations for metrics"""



        return {
            'rto_breach': {
                'metric_id': 'rto_compliance_percentage',
                'condition': 'below_threshold',
                'threshold': 95.0,
                'severity': 'critical',
                'notification_channels': ['email', 'slack', 'pagerduty']
            },
            'rpo_breach': {
                'metric_id': 'rpo_compliance_percentage',
                'condition': 'below_threshold',
                'threshold': 97.0,
                'severity': 'critical',
                'notification_channels': ['email', 'slack', 'pagerduty']
            },
            'high_business_impact': {
                'metric_id': 'business_impact_cost_per_hour',
                'condition': 'above_threshold',
                'threshold': 25000.0,
                'severity': 'high',
                'notification_channels': ['email', 'slack']
            },
            'availability_degradation': {
                'metric_id': 'system_availability_percentage',
                'condition': 'below_threshold',
                'threshold': 99.9,
                'severity': 'medium',
                'notification_channels': ['email', 'slack']
            },
            'data_loss_detected': {
                'metric_id': 'data_loss_incidents',
                'condition': 'above_threshold',
                'threshold': 0.0,
                'severity': 'emergency',
                'notification_channels': ['email', 'slack', 'pagerduty', 'sms']
            }
        }

    async def register_metric(self, metric_config: Dict[str, Any]) -> str:
        """
        Register new recovery metric for collection
        
        Args:
            metric_config: Metric configuration
            
        Returns:
            str: Metric ID
        """



        try:
            metric_id = metric_config['metric_id']
            
            recovery_metric = RecoveryMetric(
                metric_id=metric_id,
                name=metric_config['name'],
                description=metric_config.get('description', ''),
                metric_type=MetricType(metric_config['metric_type']),
                granularity=MetricGranularity(metric_config.get('granularity', 'standard')),
                aggregation_method=metric_config.get('aggregation_method', 'average'),
                unit=metric_config.get('unit', 'count'),
                target_value=metric_config.get('target_value'),
                warning_threshold=metric_config.get('warning_threshold'),
                critical_threshold=metric_config.get('critical_threshold'),
                enabled=metric_config.get('enabled', True),
                retention_days=metric_config.get('retention_days', 365)
            )
            
            self.metric_definitions[metric_id] = recovery_metric
            
            # Start collection task if enabled
            if recovery_metric.enabled:
                collection_task = asyncio.create_task(
                    self._collect_metric_data(recovery_metric)
                )
                self.collection_tasks[metric_id] = collection_task
            
            self.logger.info(f"Recovery metric {metric_id} registered")
            return metric_id
            
        except Exception as e:
            self.logger.error(f"Failed to register recovery metric: {e}")
            raise

    async def _collect_metric_data(self, metric: RecoveryMetric):
        """Collect data for a specific metric"""
        metric_id = metric.metric_id
        collection_interval = self._get_collection_interval(metric.granularity)
        
        while metric_id in self.metric_definitions and metric.enabled:
            try:
                collection_start = datetime.utcnow()
                
                # Collect metric value based on type
                metric_value = await self._get_metric_value(metric)
                
                if metric_value is not None:
                    # Create data point
                    data_point = MetricDataPoint(
                        metric_id=metric_id,
                        timestamp=collection_start,
                        value=metric_value,
                        tags={'granularity': metric.granularity.value}
                    )
                    
                    # Store data point
                    self.metric_data[metric_id].append(data_point)
                    
                    # Check alert thresholds
                    await self._check_metric_alerts(metric, data_point)
                    
                    # Update collection performance
                    collection_time = (datetime.utcnow() - collection_start).total_seconds()
                    self._update_collection_performance(collection_time)
                
                await asyncio.sleep(collection_interval)
                
            except Exception as e:
                self.logger.error(f"Metric collection error for {metric_id}: {e}")
                self.collection_performance['collection_errors'] += 1
                await asyncio.sleep(collection_interval)

    async def _get_metric_value(self, metric: RecoveryMetric) -> Optional[float]:
        """Get current value for a specific metric"""



        try:
            metric_id = metric.metric_id
            
            if metric_id == 'rto_compliance_percentage':
                return await self._calculate_rto_compliance()
            elif metric_id == 'rpo_compliance_percentage':
                return await self._calculate_rpo_compliance()
            elif metric_id == 'mean_time_to_recovery':
                return await self._calculate_mean_recovery_time()
            elif metric_id == 'recovery_success_rate':
                return await self._calculate_recovery_success_rate()
            elif metric_id == 'business_impact_cost_per_hour':
                return await self._calculate_business_impact_cost()
            elif metric_id == 'system_availability_percentage':
                return await self._calculate_system_availability()
            elif metric_id == 'data_loss_incidents':
                return await self._count_data_loss_incidents()
            elif metric_id == 'sla_penalty_cost':
                return await self._calculate_sla_penalty_cost()
            elif metric_id == 'backup_success_rate':
                return await self._calculate_backup_success_rate()
            elif metric_id == 'failover_trigger_time':
                return await self._calculate_failover_trigger_time()
            else:
                # Custom metric - try to get from external source
                return await self._get_custom_metric_value(metric_id)
                
        except Exception as e:
            self.logger.error(f"Failed to get metric value for {metric.metric_id}: {e}")
            return None

    async def _calculate_rto_compliance(self) -> float:
        """Calculate RTO compliance percentage"""



        try:
            # Get recovery operations from last 24 hours
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            recoveries = await self.db_manager.get_recovery_operations_since(cutoff_time)
            
            if not recoveries:
                return 100.0  # No recoveries = 100% compliance
            
            compliant_recoveries = 0
            for recovery in recoveries:
                rto_target = recovery.get('rto_target_seconds', 1800)  # Default 30 min
                actual_time = recovery.get('recovery_time_seconds', 0)
                
                if actual_time <= rto_target:
                    compliant_recoveries += 1
            
            return (compliant_recoveries / len(recoveries)) * 100.0
            
        except Exception as e:
            self.logger.error(f"RTO compliance calculation failed: {e}")
            return None

    async def _calculate_rpo_compliance(self) -> float:
        """Calculate RPO compliance percentage"""



        try:
            # Get data loss incidents from last 24 hours
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            incidents = await self.db_manager.get_data_loss_incidents_since(cutoff_time)
            
            compliant_incidents = 0
            for incident in incidents:
                rpo_target = incident.get('rpo_target_seconds', 300)  # Default 5 min
                actual_loss = incident.get('data_loss_seconds', 0)
                
                if actual_loss <= rpo_target:
                    compliant_incidents += 1
            
            if not incidents:
                return 100.0  # No incidents = 100% compliance
            
            return (compliant_incidents / len(incidents)) * 100.0
            
        except Exception as e:
            self.logger.error(f"RPO compliance calculation failed: {e}")
            return None

    async def _calculate_business_impact_cost(self) -> float:
        """Calculate current business impact cost per hour"""



        try:
            # Get current outages and their business impact
            active_outages = await self.db_manager.get_active_outages()
            total_cost_per_hour = 0.0
            
            for outage in active_outages:
                # Calculate cost based on affected services and users
                affected_services = outage.get('affected_services', [])
                affected_users = outage.get('affected_users', 0)
                
                # Base cost calculation
                service_cost = len(affected_services) * 1000  # €1k per service per hour
                user_cost = affected_users * 0.1  # €0.1 per user per hour
                
                # Apply severity multiplier
                severity_multiplier = {
                    'low': 0.5,
                    'medium': 1.0,
                    'high': 2.0,
                    'critical': 5.0,
                    'emergency': 10.0
                }.get(outage.get('severity', 'medium'), 1.0)
                
                outage_cost = (service_cost + user_cost) * severity_multiplier
                total_cost_per_hour += outage_cost
            
            return total_cost_per_hour
            
        except Exception as e:
            self.logger.error(f"Business impact cost calculation failed: {e}")
            return 0.0

    async def generate_metrics_report(self, period_start: datetime, 
                                    period_end: datetime,
                                    metric_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive metrics report for specified period
        
        Args:
            period_start: Report period start
            period_end: Report period end
            metric_ids: Specific metrics to include (all if None)
            
        Returns:
            Dict[str, Any]: Comprehensive metrics report
        """



        try:
            if metric_ids is None:
                metric_ids = list(self.metric_definitions.keys())
            
            report = {
                'report_id': f"recovery_metrics_{int(period_start.timestamp())}_{int(period_end.timestamp())}",
                'period_start': period_start.isoformat(),
                'period_end': period_end.isoformat(),
                'metrics': {},
                'summary': {},
                'alerts_triggered': [],
                'recommendations': []
            }
            
            # Generate metrics summaries
            for metric_id in metric_ids:
                if metric_id in self.metric_definitions:
                    metric_summary = await self._generate_metric_summary(
                        metric_id, period_start, period_end
                    )
                    report['metrics'][metric_id] = metric_summary
            
            # Generate overall summary
            report['summary'] = await self._generate_overall_summary(report['metrics'])
            
            # Get alerts for period
            report['alerts_triggered'] = await self._get_alerts_for_period(period_start, period_end)
            
            # Generate recommendations
            report['recommendations'] = self._generate_recommendations(report['metrics'])
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate metrics report: {e}")
            return {'error': str(e)}

    async def _generate_metric_summary(self, metric_id: str, 
                                     period_start: datetime,
                                     period_end: datetime) -> Dict[str, Any]:
        """Generate summary for a specific metric"""



        try:
            metric_data = self.metric_data.get(metric_id, [])
            metric_def = self.metric_definitions[metric_id]
            
            # Filter data for period
            period_data = [
                dp for dp in metric_data
                if period_start <= dp.timestamp <= period_end
            ]
            
            if not period_data:
                return {
                    'metric_id': metric_id,
                    'no_data': True,
                    'period_start': period_start.isoformat(),
                    'period_end': period_end.isoformat()
                }
            
            values = [dp.value for dp in period_data]
            
            # Calculate statistics
            summary = {
                'metric_id': metric_id,
                'name': metric_def.name,
                'unit': metric_def.unit,
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'average': statistics.mean(values),
                'sum': sum(values),
                'target_value': metric_def.target_value,
                'warning_threshold': metric_def.warning_threshold,
                'critical_threshold': metric_def.critical_threshold
            }
            
            if len(values) > 1:
                summary['std_deviation'] = statistics.stdev(values)
                summary['median'] = statistics.median(values)
                
                # Calculate percentiles
                summary['percentiles'] = {
                    'p50': statistics.median(values),
                    'p90': self._calculate_percentile(values, 90),
                    'p95': self._calculate_percentile(values, 95),
                    'p99': self._calculate_percentile(values, 99)
                }
                
                # Determine trend
                summary['trend'] = self._calculate_trend(values)
            
            # Calculate compliance if applicable
            if metric_def.target_value:
                if metric_def.aggregation_method == 'average':
                    compliance_value = summary['average']
                elif metric_def.aggregation_method == 'min':
                    compliance_value = summary['min']
                elif metric_def.aggregation_method == 'max':
                    compliance_value = summary['max']
                else:
                    compliance_value = summary['average']
                
                if metric_id.endswith('_percentage') or metric_id.endswith('_rate'):
                    summary['target_compliance'] = compliance_value >= metric_def.target_value
                else:
                    summary['target_compliance'] = compliance_value <= metric_def.target_value
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate summary for metric {metric_id}: {e}")
            return {'error': str(e)}

    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        sorted_values = sorted(values)
        index = (percentile / 100.0) * (len(sorted_values) - 1)
        
        if index == int(index):
            return sorted_values[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            weight = index - lower_index
            return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for values"""
        if len(values) < 3:
            return "insufficient_data"
        
        # Simple linear trend calculation
        x = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(xi * yi for xi, yi in zip(x, values))
        sum_x2 = sum(xi * xi for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        if abs(slope) < 0.01:  # Threshold for "stable"
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"

    def _generate_recommendations(self, metrics_data: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on metrics"""
        recommendations = []
        
        # RTO compliance recommendations
        rto_metric = metrics_data.get('rto_compliance_percentage', {})
        if rto_metric.get('average', 100) < 95:
            recommendations.append(
                "RTO compliance is below target. Consider optimizing recovery procedures and increasing automation."
            )
        
        # RPO compliance recommendations
        rpo_metric = metrics_data.get('rpo_compliance_percentage', {})
        if rpo_metric.get('average', 100) < 97:
            recommendations.append(
                "RPO compliance needs improvement. Consider more frequent backups and faster replication."
            )
        
        # Recovery time recommendations
        mttr_metric = metrics_data.get('mean_time_to_recovery', {})
        if mttr_metric.get('average', 0) > 3600:  # > 1 hour
            recommendations.append(
                "Mean Time to Recovery is high. Review and automate recovery procedures."
            )
        
        # Business impact recommendations
        impact_metric = metrics_data.get('business_impact_cost_per_hour', {})
        if impact_metric.get('max', 0) > 25000:  # > €25k/hour
            recommendations.append(
                "High business impact costs detected. Prioritize critical system redundancy and faster failover."
            )
        
        # Availability recommendations
        availability_metric = metrics_data.get('system_availability_percentage', {})
        if availability_metric.get('average', 100) < 99.9:
            recommendations.append(
                "System availability is below target. Investigate frequent causes of downtime."
            )
        
        return recommendations

    def _get_collection_interval(self, granularity: MetricGranularity) -> int:
        """Get collection interval in seconds for granularity"""
        intervals = {
            MetricGranularity.REAL_TIME: 60,        # 1 minute
            MetricGranularity.HIGH_FREQUENCY: 300,  # 5 minutes
            MetricGranularity.STANDARD: 900,        # 15 minutes
            MetricGranularity.LOW_FREQUENCY: 3600,  # 1 hour
            MetricGranularity.DAILY: 86400          # 24 hours
        }
        return intervals.get(granularity, 900)

    def _update_collection_performance(self, collection_time: float):
        """Update collection performance metrics"""
        self.collection_performance['total_metrics_collected'] += 1
        
        # Update average collection time
        total_collections = self.collection_performance['total_metrics_collected']
        current_avg = self.collection_performance['average_collection_time']
        
        self.collection_performance['average_collection_time'] = (
            (current_avg * (total_collections - 1) + collection_time) / total_collections
        )

    async def get_metrics_status(self) -> Dict[str, Any]:
        """Get comprehensive metrics collection status"""



        return {
            'registered_metrics': len(self.metric_definitions),
            'active_collectors': len(self.collection_tasks),
            'total_data_points': sum(len(data) for data in self.metric_data.values()),
            'collection_performance': self.collection_performance.copy(),
            'metric_health': {
                metric_id: {
                    'enabled': metric.enabled,
                    'last_collection': self.metric_data[metric_id][-1].timestamp.isoformat() 
                                     if self.metric_data[metric_id] else None,
                    'data_points': len(self.metric_data[metric_id])
                }
                for metric_id, metric in self.metric_definitions.items()
            }
        }

    async def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive recovery metrics for disaster recovery coordinator"""



        try:
            current_time = datetime.utcnow()
            
            # Calculate current metrics
            availability = await self._calculate_system_availability()
            rto_compliance = await self._calculate_rto_compliance()
            rpo_compliance = await self._calculate_rpo_compliance()
            backup_success = await self._calculate_backup_success_rate()
            business_impact = await self._calculate_business_impact_cost()
            recovery_success = await self._calculate_recovery_success_rate()
            
            # Get recent recovery operations
            recent_recoveries = await self._get_recent_recovery_operations()
            last_backup = await self._get_last_backup_info()
            next_backup = await self._get_next_backup_info()
            
            # Calculate risk level based on various factors
            risk_level = await self._calculate_risk_level()
            
            # Count active incidents
            active_incidents = await self._count_active_incidents()
            
            return {
                "availability": availability,
                "current_rto": await self._calculate_current_rto(),
                "current_rpo": await self._calculate_current_rpo(),
                "backup_success_rate": backup_success,
                "integrity_score": await self._calculate_integrity_score(),
                "risk_level": risk_level,
                "active_incidents": active_incidents,
                "last_backup": last_backup,
                "next_backup": next_backup,
                "rto_compliance": rto_compliance,
                "rpo_compliance": rpo_compliance,
                "business_impact_cost": business_impact,
                "recovery_success_rate": recovery_success,
                "collection_timestamp": current_time.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get comprehensive metrics: {e}")
            return {
                "error": str(e),
                "availability": 0.0,
                "current_rto": 0.0,
                "current_rpo": 0.0,
                "risk_level": 1.0,
                "active_incidents": 0
            }

    async def get_sla_compliance(self) -> Dict[str, bool]:
        """Get SLA compliance status for disaster recovery coordinator"""



        try:
            rto_compliance = await self._calculate_rto_compliance()
            rpo_compliance = await self._calculate_rpo_compliance()
            availability = await self._calculate_system_availability()
            backup_success = await self._calculate_backup_success_rate()
            
            return {
                "rto_compliance": rto_compliance >= 95.0,
                "rpo_compliance": rpo_compliance >= 97.0,
                "availability_sla": availability >= 99.9,
                "backup_sla": backup_success >= 99.0,
                "overall_sla_compliance": all([
                    rto_compliance >= 95.0,
                    rpo_compliance >= 97.0,
                    availability >= 99.9,
                    backup_success >= 99.0
                ])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get SLA compliance: {e}")
            return {
                "rto_compliance": False,
                "rpo_compliance": False,
                "availability_sla": False,
                "backup_sla": False,
                "overall_sla_compliance": False,
                "error": str(e)
            }

    # Helper methods for metric calculations
    async def _calculate_system_availability(self) -> float:
        """Calculate current system availability percentage"""



        try:
            # Get uptime data from last 24 hours
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            downtime_incidents = await self.db_manager.get_downtime_incidents_since(cutoff_time)
            
            total_downtime_seconds = sum(
                incident.get('duration_seconds', 0) for incident in downtime_incidents
            )
            
            # Calculate availability (24 hours = 86400 seconds)
            uptime_percentage = ((86400 - total_downtime_seconds) / 86400) * 100
            return max(0.0, min(100.0, uptime_percentage))
            
        except Exception as e:
            self.logger.error(f"System availability calculation failed: {e}")
            return 99.9  # Default to high availability

    async def _calculate_mean_recovery_time(self) -> float:
        """Calculate mean time to recovery"""



        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            recoveries = await self.db_manager.get_recovery_operations_since(cutoff_time)
            
            if not recoveries:
                return 0.0
            
            total_time = sum(r.get('recovery_time_seconds', 0) for r in recoveries)
            return total_time / len(recoveries)
            
        except Exception as e:
            self.logger.error(f"Mean recovery time calculation failed: {e}")
            return 1800.0  # Default 30 minutes

    async def _calculate_recovery_success_rate(self) -> float:
        """Calculate recovery success rate percentage"""



        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            recoveries = await self.db_manager.get_recovery_operations_since(cutoff_time)
            
            if not recoveries:
                return 100.0
            
            successful = len([r for r in recoveries if r.get('status') == 'completed'])
            return (successful / len(recoveries)) * 100.0
            
        except Exception as e:
            self.logger.error(f"Recovery success rate calculation failed: {e}")
            return 99.0  # Default high success rate

    async def _calculate_backup_success_rate(self) -> float:
        """Calculate backup success rate percentage"""



        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            backups = await self.db_manager.get_backup_operations_since(cutoff_time)
            
            if not backups:
                return 100.0
            
            successful = len([b for b in backups if b.get('status') == 'completed'])
            return (successful / len(backups)) * 100.0
            
        except Exception as e:
            self.logger.error(f"Backup success rate calculation failed: {e}")
            return 99.5  # Default high success rate

    async def _calculate_current_rto(self) -> float:
        """Calculate current Recovery Time Objective"""



        try:
            # Get most recent recovery operation
            recent_recovery = await self.db_manager.get_most_recent_recovery()
            
            if recent_recovery:
                return recent_recovery.get('recovery_time_seconds', 0.0)
            else:
                return 0.0  # No recent recoveries
                
        except Exception as e:
            self.logger.error(f"Current RTO calculation failed: {e}")
            return 0.0

    async def _calculate_current_rpo(self) -> float:
        """Calculate current Recovery Point Objective"""



        try:
            # Get most recent data loss incident
            recent_incident = await self.db_manager.get_most_recent_data_loss()
            
            if recent_incident:
                return recent_incident.get('data_loss_seconds', 0.0)
            else:
                return 0.0  # No recent data loss
                
        except Exception as e:
            self.logger.error(f"Current RPO calculation failed: {e}")
            return 0.0

    async def _calculate_integrity_score(self) -> float:
        """Calculate data integrity score percentage"""



        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            integrity_checks = await self.db_manager.get_integrity_checks_since(cutoff_time)
            
            if not integrity_checks:
                return 100.0
            
            passed_checks = len([c for c in integrity_checks if c.get('status') == 'passed'])
            return (passed_checks / len(integrity_checks)) * 100.0
            
        except Exception as e:
            self.logger.error(f"Integrity score calculation failed: {e}")
            return 99.9  # Default high integrity

    async def _calculate_risk_level(self) -> float:
        """Calculate current risk level (0.0 = no risk, 1.0 = maximum risk)"""



        try:
            # Assess various risk factors
            availability = await self._calculate_system_availability()
            backup_success = await self._calculate_backup_success_rate()
            integrity_score = await self._calculate_integrity_score()
            
            # Calculate risk based on performance degradation
            availability_risk = max(0, (99.9 - availability) / 99.9)  # Risk increases as availability drops
            backup_risk = max(0, (99.0 - backup_success) / 99.0)      # Risk increases as backup fails
            integrity_risk = max(0, (99.9 - integrity_score) / 99.9)  # Risk increases with integrity issues
            
            # Combine risk factors (weighted average)
            overall_risk = (availability_risk * 0.4 + backup_risk * 0.3 + integrity_risk * 0.3)
            
            return min(1.0, overall_risk)
            
        except Exception as e:
            self.logger.error(f"Risk level calculation failed: {e}")
            return 0.1  # Default low risk

    async def _count_active_incidents(self) -> int:
        """Count active incidents"""



        try:
            active_incidents = await self.db_manager.get_active_incidents()
            return len(active_incidents)
            
        except Exception as e:
            self.logger.error(f"Active incidents count failed: {e}")
            return 0

    async def _count_data_loss_incidents(self) -> float:
        """Count data loss incidents in last hour"""



        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            incidents = await self.db_manager.get_data_loss_incidents_since(cutoff_time)
            return float(len(incidents))
            
        except Exception as e:
            self.logger.error(f"Data loss incidents count failed: {e}")
            return 0.0

    async def _calculate_sla_penalty_cost(self) -> float:
        """Calculate SLA penalty costs for today"""



        try:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            sla_breaches = await self.db_manager.get_sla_breaches_since(today_start)
            
            total_penalty = 0.0
            for breach in sla_breaches:
                penalty_amount = breach.get('penalty_cost', 0.0)
                total_penalty += penalty_amount
            
            return total_penalty
            
        except Exception as e:
            self.logger.error(f"SLA penalty calculation failed: {e}")
            return 0.0

    async def _calculate_failover_trigger_time(self) -> float:
        """Calculate latest failover trigger time"""



        try:
            recent_failover = await self.db_manager.get_most_recent_failover()
            
            if recent_failover:
                return recent_failover.get('trigger_time_seconds', 30.0)
            else:
                return 30.0  # Default good trigger time
                
        except Exception as e:
            self.logger.error(f"Failover trigger time calculation failed: {e}")
            return 30.0

    async def _get_custom_metric_value(self, metric_id: str) -> Optional[float]:
        """Get value for custom metric"""



        try:
            # Placeholder for custom metric retrieval
            # In real implementation, would query external systems
            return None
            
        except Exception as e:
            self.logger.error(f"Custom metric {metric_id} retrieval failed: {e}")
            return None

    async def _check_metric_alerts(self, metric: RecoveryMetric, data_point: MetricDataPoint):
        """Check metric against alert thresholds"""



        try:
            value = data_point.value
            
            # Check critical threshold
            if (metric.critical_threshold is not None and 
                ((metric.metric_id.endswith('_percentage') or metric.metric_id.endswith('_rate')) and value < metric.critical_threshold) or
                (not (metric.metric_id.endswith('_percentage') or metric.metric_id.endswith('_rate')) and value > metric.critical_threshold)):
                
                await self._trigger_alert(metric, data_point, 'critical')
            
            # Check warning threshold
            elif (metric.warning_threshold is not None and 
                  ((metric.metric_id.endswith('_percentage') or metric.metric_id.endswith('_rate')) and value < metric.warning_threshold) or
                  (not (metric.metric_id.endswith('_percentage') or metric.metric_id.endswith('_rate')) and value > metric.warning_threshold)):
                
                await self._trigger_alert(metric, data_point, 'warning')
                
        except Exception as e:
            self.logger.error(f"Alert check failed for metric {metric.metric_id}: {e}")

    async def _trigger_alert(self, metric: RecoveryMetric, data_point: MetricDataPoint, severity: str):
        """Trigger alert for metric threshold breach"""



        try:
            alert_data = {
                'alert_id': f"metric_alert_{metric.metric_id}_{int(data_point.timestamp.timestamp())}",
                'metric_id': metric.metric_id,
                'metric_name': metric.name,
                'current_value': data_point.value,
                'threshold_breached': metric.critical_threshold if severity == 'critical' else metric.warning_threshold,
                'severity': severity,
                'timestamp': data_point.timestamp.isoformat(),
                'unit': metric.unit
            }
            
            self.logger.warning(f"METRIC ALERT [{severity.upper()}]: {alert_data}")
            
            # Record alert (in real implementation, would send to alerting system)
            self.metrics.record_metric(
                metric_name="recovery_metric_alert_triggered",
                value=1,
                tags={
                    'metric_id': metric.metric_id,
                    'severity': severity
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to trigger alert: {e}")

    async def _get_recent_recovery_operations(self) -> List[Dict[str, Any]]:
        """Get recent recovery operations"""



        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            return await self.db_manager.get_recovery_operations_since(cutoff_time)
        except Exception:
            return []

    async def _get_last_backup_info(self) -> str:
        """Get last backup timestamp"""



        try:
            last_backup = await self.db_manager.get_most_recent_backup()
            if last_backup:
                return last_backup.get('timestamp', datetime.utcnow().isoformat())
            else:
                return datetime.utcnow().isoformat()
        except Exception:
            return datetime.utcnow().isoformat()

    async def _get_next_backup_info(self) -> str:
        """Get next scheduled backup timestamp"""



        try:
            next_backup = await self.db_manager.get_next_scheduled_backup()
            if next_backup:
                return next_backup.get('scheduled_time', (datetime.utcnow() + timedelta(hours=1)).isoformat())
            else:
                return (datetime.utcnow() + timedelta(hours=1)).isoformat()
        except Exception:
            return (datetime.utcnow() + timedelta(hours=1)).isoformat()

    async def _get_alerts_for_period(self, period_start: datetime, period_end: datetime) -> List[Dict[str, Any]]:
        """Get alerts triggered during specified period"""



        try:
            return await self.db_manager.get_alerts_for_period(period_start, period_end)
        except Exception:
            return []

    async def _generate_overall_summary(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall summary from metrics data"""



        try:
            # Calculate overall health score
            health_factors = []
            
            for metric_id, metric_summary in metrics_data.items():
                if isinstance(metric_summary, dict) and 'target_compliance' in metric_summary:
                    if metric_summary['target_compliance']:
                        health_factors.append(1.0)
                    else:
                        health_factors.append(0.0)
            
            overall_health = statistics.mean(health_factors) if health_factors else 1.0
            
            return {
                'overall_health_score': overall_health * 100,
                'metrics_analyzed': len(metrics_data),
                'compliant_metrics': sum(health_factors),
                'non_compliant_metrics': len(health_factors) - sum(health_factors),
                'health_status': 'healthy' if overall_health > 0.95 else 'degraded' if overall_health > 0.8 else 'critical'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate overall summary: {e}")
            return {'error': str(e)}
