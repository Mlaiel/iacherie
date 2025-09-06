"""Security Analytics Dashboard for Events Security

Real-time security monitoring and analytics dashboard for Ainflue platform.
Provides comprehensive visibility into security events and threat landscape.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of security metrics"""
    THREAT_LEVEL = "threat_level"
    ACCESS_VIOLATIONS = "access_violations"
    COMPLIANCE_VIOLATIONS = "compliance_violations"
    INTRUSION_ATTEMPTS = "intrusion_attempts"
    AUDIT_EVENTS = "audit_events"
    RESPONSE_TIME = "response_time"
    SECURITY_SCORE = "security_score"


class TimeRange(Enum):
    """Time range options for analytics"""
    LAST_HOUR = "last_hour"
    LAST_24_HOURS = "last_24_hours"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    CUSTOM = "custom"


@dataclass
class SecurityMetric:
    """Security metric data point"""
    metric_type: MetricType
    timestamp: datetime
    value: float
    details: Dict[str, Any]
    tags: List[str]
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.tags is None:
            self.tags = []


@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    widget_id: str
    title: str
    metric_type: MetricType
    chart_type: str  # line, bar, pie, gauge, etc.
    time_range: TimeRange
    refresh_interval_seconds: int
    enabled: bool = True


@dataclass
class SecurityAlert:
    """Security alert for dashboard"""
    alert_id: str
    title: str
    description: str
    severity: str
    timestamp: datetime
    source: str
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class DashboardData:
    """Complete dashboard data"""
    widgets: List[Dict[str, Any]]
    alerts: List[SecurityAlert]
    summary_stats: Dict[str, Any]
    threat_map: Dict[str, Any]
    timeline: List[Dict[str, Any]]
    last_updated: datetime


class SecurityAnalyticsDashboard:
    """
    Real-time security analytics dashboard for monitoring and visualization.
    Aggregates data from all security modules for comprehensive visibility.
    """
    
    def __init__(self):
        self.enabled = True
        self.widgets = self._initialize_default_widgets()
        self.metrics_history = []  # In-memory storage for demo
        self.alerts = []
        self.security_modules = {}
        self.update_interval_seconds = 30
        self.max_metrics_history = 10000
        self.dashboard_sessions = {}  # session_id -> user_preferences
        logger.info("SecurityAnalyticsDashboard initialized")
    
    def register_security_modules(self,
                                threat_engine=None,
                                access_manager=None,
                                compliance_validator=None,
                                audit_collector=None,
                                intrusion_prevention=None):
        """Register security modules for data collection"""
        
        if threat_engine:
            self.security_modules['threat_engine'] = threat_engine
            logger.info("Threat engine registered with dashboard")
        
        if access_manager:
            self.security_modules['access_manager'] = access_manager
            logger.info("Access manager registered with dashboard")
        
        if compliance_validator:
            self.security_modules['compliance_validator'] = compliance_validator
            logger.info("Compliance validator registered with dashboard")
        
        if audit_collector:
            self.security_modules['audit_collector'] = audit_collector
            logger.info("Audit collector registered with dashboard")
        
        if intrusion_prevention:
            self.security_modules['intrusion_prevention'] = intrusion_prevention
            logger.info("Intrusion prevention registered with dashboard")
    
    async def get_dashboard_data(self,
                               time_range: TimeRange = TimeRange.LAST_24_HOURS,
                               user_preferences: Dict[str, Any] = None) -> DashboardData:
        """
        Get complete dashboard data for specified time range.
        
        Args:
            time_range: Time range for data collection
            user_preferences: User-specific dashboard preferences
            
        Returns:
            DashboardData with all dashboard information
        """
        if not self.enabled:
            return self._create_empty_dashboard()
        
        try:
            user_preferences = user_preferences or {}
            
            # Collect data from all security modules
            await self._collect_security_metrics()
            
            # Get time range boundaries
            start_time, end_time = self._get_time_boundaries(time_range)
            
            # Generate widget data
            widgets = await self._generate_widget_data(start_time, end_time, user_preferences)
            
            # Get current alerts
            current_alerts = await self._get_current_alerts()
            
            # Generate summary statistics
            summary_stats = await self._generate_summary_stats(start_time, end_time)
            
            # Generate threat map
            threat_map = await self._generate_threat_map(start_time, end_time)
            
            # Generate timeline
            timeline = await self._generate_security_timeline(start_time, end_time)
            
            dashboard_data = DashboardData(
                widgets=widgets,
                alerts=current_alerts,
                summary_stats=summary_stats,
                threat_map=threat_map,
                timeline=timeline,
                last_updated=datetime.utcnow()
            )
            
            logger.debug(f"Dashboard data generated for {time_range.value}")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error generating dashboard data: {str(e)}")
            return self._create_error_dashboard(str(e))
    
    async def _collect_security_metrics(self):
        """Collect current metrics from all security modules"""
        
        current_time = datetime.utcnow()
        
        # Collect threat detection metrics
        if 'threat_engine' in self.security_modules:
            threat_stats = self.security_modules['threat_engine'].get_detection_stats()
            
            self._add_metric(SecurityMetric(
                metric_type=MetricType.THREAT_LEVEL,
                timestamp=current_time,
                value=threat_stats.get('avg_risk_score', 0.0),
                details=threat_stats,
                tags=['threat_detection']
            ))
        
        # Collect access control metrics
        if 'access_manager' in self.security_modules:
            # Simulate access control metrics
            self._add_metric(SecurityMetric(
                metric_type=MetricType.ACCESS_VIOLATIONS,
                timestamp=current_time,
                value=5.0,  # Simulated value
                details={'denied_requests': 5, 'total_requests': 100},
                tags=['access_control']
            ))
        
        # Collect compliance metrics
        if 'compliance_validator' in self.security_modules:
            compliance_stats = self.security_modules['compliance_validator'].get_violation_statistics()
            
            self._add_metric(SecurityMetric(
                metric_type=MetricType.COMPLIANCE_VIOLATIONS,
                timestamp=current_time,
                value=float(compliance_stats.get('total_violations', 0)),
                details=compliance_stats,
                tags=['compliance']
            ))
        
        # Collect audit metrics
        if 'audit_collector' in self.security_modules:
            audit_stats = self.security_modules['audit_collector'].get_audit_statistics()
            
            self._add_metric(SecurityMetric(
                metric_type=MetricType.AUDIT_EVENTS,
                timestamp=current_time,
                value=float(audit_stats.get('total_records', 0)),
                details=audit_stats,
                tags=['audit']
            ))
        
        # Collect intrusion prevention metrics
        if 'intrusion_prevention' in self.security_modules:
            intrusion_stats = self.security_modules['intrusion_prevention'].get_intrusion_statistics()
            
            self._add_metric(SecurityMetric(
                metric_type=MetricType.INTRUSION_ATTEMPTS,
                timestamp=current_time,
                value=float(intrusion_stats.get('total_intrusions', 0)),
                details=intrusion_stats,
                tags=['intrusion_prevention']
            ))
        
        # Calculate overall security score
        security_score = await self._calculate_overall_security_score()
        self._add_metric(SecurityMetric(
            metric_type=MetricType.SECURITY_SCORE,
            timestamp=current_time,
            value=security_score,
            details={'calculation_method': 'weighted_average'},
            tags=['overall_security']
        ))
    
    async def _generate_widget_data(self,
                                  start_time: datetime,
                                  end_time: datetime,
                                  user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate data for all dashboard widgets"""
        
        widget_data = []
        
        for widget in self.widgets.values():
            if not widget.enabled:
                continue
            
            try:
                data = await self._generate_single_widget_data(widget, start_time, end_time)
                widget_data.append(data)
            except Exception as e:
                logger.error(f"Error generating widget data for {widget.widget_id}: {str(e)}")
        
        return widget_data
    
    async def _generate_single_widget_data(self,
                                         widget: DashboardWidget,
                                         start_time: datetime,
                                         end_time: datetime) -> Dict[str, Any]:
        """Generate data for a single widget"""
        
        # Filter metrics by type and time range
        filtered_metrics = [
            m for m in self.metrics_history
            if (m.metric_type == widget.metric_type and
                start_time <= m.timestamp <= end_time)
        ]
        
        # Sort by timestamp
        filtered_metrics.sort(key=lambda x: x.timestamp)
        
        if widget.chart_type == "line":
            chart_data = {
                'labels': [m.timestamp.isoformat() for m in filtered_metrics],
                'values': [m.value for m in filtered_metrics],
                'datasets': [{
                    'label': widget.title,
                    'data': [m.value for m in filtered_metrics]
                }]
            }
        
        elif widget.chart_type == "gauge":
            latest_value = filtered_metrics[-1].value if filtered_metrics else 0.0
            chart_data = {
                'current_value': latest_value,
                'max_value': 1.0 if widget.metric_type == MetricType.SECURITY_SCORE else 100.0,
                'thresholds': self._get_gauge_thresholds(widget.metric_type)
            }
        
        elif widget.chart_type == "bar":
            # Group by hour/day depending on time range
            grouped_data = self._group_metrics_by_time(filtered_metrics, widget.time_range)
            chart_data = {
                'labels': list(grouped_data.keys()),
                'values': list(grouped_data.values())
            }
        
        elif widget.chart_type == "pie":
            # Use details from latest metric for pie chart
            latest_metric = filtered_metrics[-1] if filtered_metrics else None
            if latest_metric and 'by_type' in latest_metric.details:
                by_type = latest_metric.details['by_type']
                chart_data = {
                    'labels': list(by_type.keys()),
                    'values': list(by_type.values())
                }
            else:
                chart_data = {'labels': [], 'values': []}
        
        else:
            chart_data = {'error': f'Unsupported chart type: {widget.chart_type}'}
        
        return {
            'widget_id': widget.widget_id,
            'title': widget.title,
            'chart_type': widget.chart_type,
            'data': chart_data,
            'last_updated': datetime.utcnow().isoformat(),
            'metric_count': len(filtered_metrics)
        }
    
    async def _get_current_alerts(self) -> List[SecurityAlert]:
        """Get current unresolved security alerts"""
        
        return [alert for alert in self.alerts if not alert.resolved]
    
    async def _generate_summary_stats(self,
                                    start_time: datetime,
                                    end_time: datetime) -> Dict[str, Any]:
        """Generate summary statistics for the dashboard"""
        
        # Filter metrics for time range
        filtered_metrics = [
            m for m in self.metrics_history
            if start_time <= m.timestamp <= end_time
        ]
        
        # Calculate summary statistics
        stats = {
            'total_events': len(filtered_metrics),
            'threat_level': 'Low',
            'security_score': 0.85,
            'compliance_status': 'Compliant',
            'active_alerts': len(await self._get_current_alerts()),
            'blocked_ips': 0,
            'blocked_users': 0
        }
        
        # Get latest threat level
        threat_metrics = [m for m in filtered_metrics if m.metric_type == MetricType.THREAT_LEVEL]
        if threat_metrics:
            latest_threat = threat_metrics[-1].value
            if latest_threat > 0.8:
                stats['threat_level'] = 'Critical'
            elif latest_threat > 0.6:
                stats['threat_level'] = 'High'
            elif latest_threat > 0.4:
                stats['threat_level'] = 'Medium'
            else:
                stats['threat_level'] = 'Low'
        
        # Get latest security score
        score_metrics = [m for m in filtered_metrics if m.metric_type == MetricType.SECURITY_SCORE]
        if score_metrics:
            stats['security_score'] = score_metrics[-1].value
        
        # Get compliance status
        compliance_metrics = [m for m in filtered_metrics if m.metric_type == MetricType.COMPLIANCE_VIOLATIONS]
        if compliance_metrics:
            latest_violations = compliance_metrics[-1].value
            stats['compliance_status'] = 'Non-Compliant' if latest_violations > 0 else 'Compliant'
        
        # Get intrusion prevention stats
        if 'intrusion_prevention' in self.security_modules:
            intrusion_stats = self.security_modules['intrusion_prevention'].get_intrusion_statistics()
            stats['blocked_ips'] = intrusion_stats.get('blocked_ips', 0)
            stats['blocked_users'] = intrusion_stats.get('blocked_users', 0)
        
        return stats
    
    async def _generate_threat_map(self,
                                 start_time: datetime,
                                 end_time: datetime) -> Dict[str, Any]:
        """Generate threat landscape map"""
        
        # Simulated threat map data
        threat_map = {
            'regions': [
                {'name': 'North America', 'threat_level': 0.3, 'events': 45},
                {'name': 'Europe', 'threat_level': 0.5, 'events': 32},
                {'name': 'Asia Pacific', 'threat_level': 0.7, 'events': 28},
                {'name': 'Other', 'threat_level': 0.2, 'events': 15}
            ],
            'threat_types': [
                {'type': 'Brute Force', 'percentage': 35, 'trend': 'increasing'},
                {'type': 'Injection Attacks', 'percentage': 25, 'trend': 'stable'},
                {'type': 'DDoS', 'percentage': 20, 'trend': 'decreasing'},
                {'type': 'Data Exfiltration', 'percentage': 15, 'trend': 'increasing'},
                {'type': 'Other', 'percentage': 5, 'trend': 'stable'}
            ],
            'top_sources': [
                {'ip': '192.168.1.100', 'attempts': 45, 'blocked': True},
                {'ip': '10.0.0.1', 'attempts': 32, 'blocked': True},
                {'ip': '172.16.0.1', 'attempts': 28, 'blocked': False}
            ]
        }
        
        return threat_map
    
    async def _generate_security_timeline(self,
                                        start_time: datetime,
                                        end_time: datetime) -> List[Dict[str, Any]]:
        """Generate security events timeline"""
        
        timeline = []
        
        # Get recent security events from metrics
        recent_metrics = [
            m for m in self.metrics_history
            if start_time <= m.timestamp <= end_time
        ]
        
        # Convert metrics to timeline events
        for metric in recent_metrics[-20:]:  # Last 20 events
            severity = 'info'
            if metric.metric_type == MetricType.THREAT_LEVEL and metric.value > 0.7:
                severity = 'warning'
            elif metric.metric_type == MetricType.INTRUSION_ATTEMPTS and metric.value > 0:
                severity = 'danger'
            
            timeline.append({
                'timestamp': metric.timestamp.isoformat(),
                'title': f"{metric.metric_type.value.title()} Event",
                'description': f"Value: {metric.value:.2f}",
                'severity': severity,
                'tags': metric.tags
            })
        
        # Add alerts to timeline
        for alert in self.alerts[-10:]:  # Last 10 alerts
            timeline.append({
                'timestamp': alert.timestamp.isoformat(),
                'title': alert.title,
                'description': alert.description,
                'severity': alert.severity,
                'tags': ['alert']
            })
        
        # Sort by timestamp (newest first)
        timeline.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return timeline[:50]  # Return last 50 events
    
    async def _calculate_overall_security_score(self) -> float:
        """Calculate overall security score from all modules"""
        
        scores = []
        weights = []
        
        # Threat detection score (inverse of risk)
        if 'threat_engine' in self.security_modules:
            threat_stats = self.security_modules['threat_engine'].get_detection_stats()
            avg_risk = threat_stats.get('avg_risk_score', 0.5)
            threat_score = 1.0 - avg_risk
            scores.append(threat_score)
            weights.append(0.3)  # 30% weight
        
        # Compliance score
        if 'compliance_validator' in self.security_modules:
            compliance_stats = self.security_modules['compliance_validator'].get_violation_statistics()
            total_violations = compliance_stats.get('total_violations', 0)
            compliance_score = max(0.0, 1.0 - (total_violations * 0.1))  # Each violation reduces score
            scores.append(compliance_score)
            weights.append(0.25)  # 25% weight
        
        # Intrusion prevention score
        if 'intrusion_prevention' in self.security_modules:
            intrusion_stats = self.security_modules['intrusion_prevention'].get_intrusion_statistics()
            recent_intrusions = intrusion_stats.get('recent_intrusions', 0)
            intrusion_score = max(0.0, 1.0 - (recent_intrusions * 0.05))  # Each recent intrusion reduces score
            scores.append(intrusion_score)
            weights.append(0.25)  # 25% weight
        
        # Audit completeness score
        if 'audit_collector' in self.security_modules:
            audit_stats = self.security_modules['audit_collector'].get_audit_statistics()
            integrity = audit_stats.get('storage_integrity', True)
            audit_score = 1.0 if integrity else 0.5
            scores.append(audit_score)
            weights.append(0.2)  # 20% weight
        
        # Calculate weighted average
        if scores and weights:
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            total_weight = sum(weights)
            return weighted_sum / total_weight
        
        return 0.5  # Default neutral score
    
    def _add_metric(self, metric: SecurityMetric):
        """Add a metric to the history"""
        
        self.metrics_history.append(metric)
        
        # Maintain maximum history size
        if len(self.metrics_history) > self.max_metrics_history:
            self.metrics_history = self.metrics_history[-self.max_metrics_history:]
    
    def _get_time_boundaries(self, time_range: TimeRange) -> Tuple[datetime, datetime]:
        """Get start and end time for given time range"""
        
        end_time = datetime.utcnow()
        
        if time_range == TimeRange.LAST_HOUR:
            start_time = end_time - timedelta(hours=1)
        elif time_range == TimeRange.LAST_24_HOURS:
            start_time = end_time - timedelta(hours=24)
        elif time_range == TimeRange.LAST_7_DAYS:
            start_time = end_time - timedelta(days=7)
        elif time_range == TimeRange.LAST_30_DAYS:
            start_time = end_time - timedelta(days=30)
        else:
            start_time = end_time - timedelta(hours=24)  # Default to 24 hours
        
        return start_time, end_time
    
    def _group_metrics_by_time(self,
                             metrics: List[SecurityMetric],
                             time_range: TimeRange) -> Dict[str, float]:
        """Group metrics by time intervals"""
        
        grouped = {}
        
        for metric in metrics:
            if time_range == TimeRange.LAST_HOUR:
                # Group by 5-minute intervals
                interval = metric.timestamp.replace(minute=(metric.timestamp.minute // 5) * 5, second=0, microsecond=0)
                key = interval.strftime('%H:%M')
            elif time_range == TimeRange.LAST_24_HOURS:
                # Group by hour
                interval = metric.timestamp.replace(minute=0, second=0, microsecond=0)
                key = interval.strftime('%H:00')
            else:
                # Group by day
                interval = metric.timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
                key = interval.strftime('%Y-%m-%d')
            
            if key not in grouped:
                grouped[key] = 0.0
            grouped[key] += metric.value
        
        return grouped
    
    def _get_gauge_thresholds(self, metric_type: MetricType) -> Dict[str, float]:
        """Get thresholds for gauge widgets"""
        
        if metric_type == MetricType.SECURITY_SCORE:
            return {'green': 0.8, 'yellow': 0.6, 'red': 0.4}
        elif metric_type == MetricType.THREAT_LEVEL:
            return {'green': 0.3, 'yellow': 0.6, 'red': 0.8}
        else:
            return {'green': 70, 'yellow': 85, 'red': 95}
    
    def add_security_alert(self,
                          title: str,
                          description: str,
                          severity: str,
                          source: str):
        """Add a new security alert"""
        
        alert = SecurityAlert(
            alert_id=f"alert_{datetime.utcnow().timestamp()}",
            title=title,
            description=description,
            severity=severity,
            timestamp=datetime.utcnow(),
            source=source
        )
        
        self.alerts.append(alert)
        logger.info(f"Security alert added: {title}")
    
    def acknowledge_alert(self, alert_id: str, user_id: str):
        """Acknowledge a security alert"""
        
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                logger.info(f"Alert {alert_id} acknowledged by {user_id}")
                return True
        
        return False
    
    def resolve_alert(self, alert_id: str, user_id: str):
        """Resolve a security alert"""
        
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                logger.info(f"Alert {alert_id} resolved by {user_id}")
                return True
        
        return False
    
    def _initialize_default_widgets(self) -> Dict[str, DashboardWidget]:
        """Initialize default dashboard widgets"""
        
        widgets = [
            DashboardWidget(
                widget_id="threat_level_gauge",
                title="Current Threat Level",
                metric_type=MetricType.THREAT_LEVEL,
                chart_type="gauge",
                time_range=TimeRange.LAST_HOUR,
                refresh_interval_seconds=30
            ),
            DashboardWidget(
                widget_id="security_score_gauge",
                title="Security Score",
                metric_type=MetricType.SECURITY_SCORE,
                chart_type="gauge",
                time_range=TimeRange.LAST_HOUR,
                refresh_interval_seconds=60
            ),
            DashboardWidget(
                widget_id="threat_timeline",
                title="Threat Level Timeline",
                metric_type=MetricType.THREAT_LEVEL,
                chart_type="line",
                time_range=TimeRange.LAST_24_HOURS,
                refresh_interval_seconds=60
            ),
            DashboardWidget(
                widget_id="intrusion_attempts",
                title="Intrusion Attempts",
                metric_type=MetricType.INTRUSION_ATTEMPTS,
                chart_type="bar",
                time_range=TimeRange.LAST_24_HOURS,
                refresh_interval_seconds=120
            ),
            DashboardWidget(
                widget_id="compliance_violations",
                title="Compliance Violations by Type",
                metric_type=MetricType.COMPLIANCE_VIOLATIONS,
                chart_type="pie",
                time_range=TimeRange.LAST_7_DAYS,
                refresh_interval_seconds=300
            ),
            DashboardWidget(
                widget_id="access_violations",
                title="Access Control Violations",
                metric_type=MetricType.ACCESS_VIOLATIONS,
                chart_type="line",
                time_range=TimeRange.LAST_24_HOURS,
                refresh_interval_seconds=120
            )
        ]
        
        return {widget.widget_id: widget for widget in widgets}
    
    def _create_empty_dashboard(self) -> DashboardData:
        """Create empty dashboard when disabled"""
        
        return DashboardData(
            widgets=[],
            alerts=[],
            summary_stats={'status': 'disabled'},
            threat_map={'regions': [], 'threat_types': [], 'top_sources': []},
            timeline=[],
            last_updated=datetime.utcnow()
        )
    
    def _create_error_dashboard(self, error_message: str) -> DashboardData:
        """Create error dashboard when generation fails"""
        
        error_alert = SecurityAlert(
            alert_id=f"dashboard_error_{datetime.utcnow().timestamp()}",
            title="Dashboard Error",
            description=f"Failed to generate dashboard data: {error_message}",
            severity="warning",
            timestamp=datetime.utcnow(),
            source="dashboard"
        )
        
        return DashboardData(
            widgets=[],
            alerts=[error_alert],
            summary_stats={'status': 'error', 'message': error_message},
            threat_map={'regions': [], 'threat_types': [], 'top_sources': []},
            timeline=[],
            last_updated=datetime.utcnow()
        )
    
    def export_dashboard_data(self, format: str = "json") -> str:
        """Export dashboard data in specified format"""
        
        try:
            dashboard_data = asyncio.run(self.get_dashboard_data())
            
            if format.lower() == "json":
                return json.dumps(asdict(dashboard_data), default=str, indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format}")
        
        except Exception as e:
            logger.error(f"Error exporting dashboard data: {str(e)}")
            return json.dumps({"error": str(e)})
    
    def get_dashboard_statistics(self) -> Dict[str, Any]:
        """Get dashboard usage and performance statistics"""
        
        return {
            'total_widgets': len(self.widgets),
            'active_widgets': len([w for w in self.widgets.values() if w.enabled]),
            'total_metrics': len(self.metrics_history),
            'total_alerts': len(self.alerts),
            'unresolved_alerts': len([a for a in self.alerts if not a.resolved]),
            'active_sessions': len(self.dashboard_sessions),
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def enable_dashboard(self):
        """Enable security analytics dashboard"""
        self.enabled = True
        logger.info("Security analytics dashboard enabled")
    
    def disable_dashboard(self):
        """Disable security analytics dashboard"""
        self.enabled = False
        logger.info("Security analytics dashboard disabled")


# Export for module use
__all__ = ['SecurityAnalyticsDashboard', 'SecurityMetric', 'DashboardWidget', 'SecurityAlert', 'DashboardData', 'MetricType']