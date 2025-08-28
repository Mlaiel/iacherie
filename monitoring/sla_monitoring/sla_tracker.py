"""
SLA Monitoring and Tracking System
Implements performance requirements tracking with automated alerting
"""

import asyncio
import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import deque, defaultdict
import json

@dataclass
class SLAMetric:
    """SLA metric definition"""
    name: str
    target_value: float
    current_value: float = 0.0
    unit: str = ""
    threshold_critical: float = 0.0
    threshold_warning: float = 0.0
    measurement_window_minutes: int = 60
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class SLATarget:
    """SLA target configuration"""
    response_time_p95_ms: float = 2000.0  # <2s for 95% of API calls
    throughput_rps: float = 10000.0  # 10,000+ requests/second
    uptime_percentage: float = 99.9  # 99.9% uptime
    max_downtime_hours_yearly: float = 8.77  # 8.77 hours max downtime/year
    availability_percentage: float = 99.9

class SLATracker:
    """
    Comprehensive SLA tracking and monitoring system
    Tracks performance against production requirements
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sla_targets = SLATarget()
        self.metrics: Dict[str, SLAMetric] = {}
        self.response_times: deque = deque(maxlen=10000)
        self.request_counts: deque = deque(maxlen=1000)
        self.downtime_events: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []
        self.monitoring_active = False
        
        # Initialize core SLA metrics
        self._initialize_sla_metrics()
        
    def _initialize_sla_metrics(self):
        """Initialize SLA metrics with targets"""
        self.metrics = {
            "response_time_p95": SLAMetric(
                name="API Response Time P95",
                target_value=self.sla_targets.response_time_p95_ms,
                unit="ms",
                threshold_critical=2500.0,  # 25% over target
                threshold_warning=2200.0,   # 10% over target
                measurement_window_minutes=5
            ),
            "throughput_rps": SLAMetric(
                name="Requests Per Second",
                target_value=self.sla_targets.throughput_rps,
                unit="rps",
                threshold_critical=8000.0,   # 20% below target
                threshold_warning=9000.0,    # 10% below target
                measurement_window_minutes=1
            ),
            "uptime_percentage": SLAMetric(
                name="System Uptime",
                target_value=self.sla_targets.uptime_percentage,
                unit="%",
                threshold_critical=99.5,     # Below 99.5%
                threshold_warning=99.8,      # Below 99.8%
                measurement_window_minutes=60
            ),
            "availability_percentage": SLAMetric(
                name="Service Availability",
                target_value=self.sla_targets.availability_percentage,
                unit="%",
                threshold_critical=99.5,
                threshold_warning=99.8,
                measurement_window_minutes=60
            )
        }
        
    async def record_api_request(self, response_time_ms: float, success: bool = True):
        """Record API request metrics for SLA tracking"""
        timestamp = datetime.now()
        
        # Record response time
        self.response_times.append({
            'timestamp': timestamp,
            'response_time': response_time_ms,
            'success': success
        })
        
        # Update response time P95 metric
        await self._update_response_time_p95()
        
        # Check SLA violations
        await self._check_sla_violations()
        
    async def record_throughput(self, request_count: int, time_window_seconds: int = 1):
        """Record throughput metrics"""
        timestamp = datetime.now()
        rps = request_count / time_window_seconds
        
        self.request_counts.append({
            'timestamp': timestamp,
            'rps': rps,
            'request_count': request_count
        })
        
        # Update throughput metric
        self.metrics["throughput_rps"].current_value = rps
        self.metrics["throughput_rps"].last_updated = timestamp
        
        await self._check_sla_violations()
        
    async def record_downtime_event(self, start_time: datetime, end_time: datetime, 
                                   reason: str = "Unknown"):
        """Record system downtime event"""
        duration_minutes = (end_time - start_time).total_seconds() / 60
        duration_hours = duration_minutes / 60
        
        downtime_event = {
            'start_time': start_time,
            'end_time': end_time,
            'duration_minutes': duration_minutes,
            'duration_hours': duration_hours,
            'reason': reason
        }
        
        self.downtime_events.append(downtime_event)
        
        # Update uptime metrics
        await self._update_uptime_metrics()
        
        self.logger.warning(f"Downtime event recorded: {duration_minutes:.2f} minutes - {reason}")
        
    async def _update_response_time_p95(self):
        """Update P95 response time metric"""
        if len(self.response_times) < 20:  # Need minimum data points
            return
            
        # Get recent response times (last 5 minutes)
        cutoff_time = datetime.now() - timedelta(minutes=5)
        recent_times = [
            record['response_time'] for record in self.response_times
            if record['timestamp'] >= cutoff_time and record['success']
        ]
        
        if recent_times:
            p95_value = statistics.quantiles(recent_times, n=20)[18]  # 95th percentile
            self.metrics["response_time_p95"].current_value = p95_value
            self.metrics["response_time_p95"].last_updated = datetime.now()
            
    async def _update_uptime_metrics(self):
        """Update uptime and availability metrics"""
        now = datetime.now()
        
        # Calculate uptime for last 24 hours
        start_time = now - timedelta(hours=24)
        
        # Sum downtime in the last 24 hours
        total_downtime_minutes = sum([
            event['duration_minutes'] for event in self.downtime_events
            if event['start_time'] >= start_time
        ])
        
        # Calculate uptime percentage
        total_minutes_24h = 24 * 60
        uptime_percentage = ((total_minutes_24h - total_downtime_minutes) / total_minutes_24h) * 100
        
        self.metrics["uptime_percentage"].current_value = uptime_percentage
        self.metrics["availability_percentage"].current_value = uptime_percentage
        
        # Update timestamps
        for metric_name in ["uptime_percentage", "availability_percentage"]:
            self.metrics[metric_name].last_updated = now
            
    async def _check_sla_violations(self):
        """Check for SLA violations and generate alerts"""
        violations = []
        
        for metric_name, metric in self.metrics.items():
            if self._is_critical_violation(metric):
                violations.append({
                    'level': 'CRITICAL',
                    'metric': metric_name,
                    'current_value': metric.current_value,
                    'target_value': metric.target_value,
                    'threshold': metric.threshold_critical,
                    'timestamp': datetime.now()
                })
            elif self._is_warning_violation(metric):
                violations.append({
                    'level': 'WARNING',
                    'metric': metric_name,
                    'current_value': metric.current_value,
                    'target_value': metric.target_value,
                    'threshold': metric.threshold_warning,
                    'timestamp': datetime.now()
                })
                
        # Process violations
        for violation in violations:
            await self._process_sla_violation(violation)
            
    def _is_critical_violation(self, metric: SLAMetric) -> bool:
        """Check if metric is in critical violation"""
        if metric.name in ["API Response Time P95"]:
            return metric.current_value > metric.threshold_critical
        elif metric.name in ["Requests Per Second"]:
            return metric.current_value < metric.threshold_critical
        elif metric.name in ["System Uptime", "Service Availability"]:
            return metric.current_value < metric.threshold_critical
        return False
        
    def _is_warning_violation(self, metric: SLAMetric) -> bool:
        """Check if metric is in warning state"""
        if metric.name in ["API Response Time P95"]:
            return metric.current_value > metric.threshold_warning
        elif metric.name in ["Requests Per Second"]:
            return metric.current_value < metric.threshold_warning
        elif metric.name in ["System Uptime", "Service Availability"]:
            return metric.current_value < metric.threshold_warning
        return False
        
    async def _process_sla_violation(self, violation: Dict[str, Any]):
        """Process SLA violation and generate alert"""
        self.alerts.append(violation)
        
        self.logger.error(
            f"SLA {violation['level']} VIOLATION: {violation['metric']} = "
            f"{violation['current_value']:.2f} (target: {violation['target_value']:.2f})"
        )
        
        # In production, this would integrate with alerting systems
        # (Slack, PagerDuty, email, etc.)
        
    async def get_sla_status(self) -> Dict[str, Any]:
        """Get current SLA status and compliance"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'overall_compliance': True,
            'metrics': {},
            'violations': len([a for a in self.alerts if a['level'] == 'CRITICAL']),
            'warnings': len([a for a in self.alerts if a['level'] == 'WARNING']),
            'yearly_downtime_budget': {
                'total_hours': self.sla_targets.max_downtime_hours_yearly,
                'used_hours': sum([e['duration_hours'] for e in self.downtime_events]),
                'remaining_hours': self.sla_targets.max_downtime_hours_yearly - 
                                 sum([e['duration_hours'] for e in self.downtime_events])
            }
        }
        
        for metric_name, metric in self.metrics.items():
            compliance = not (self._is_critical_violation(metric) or self._is_warning_violation(metric))
            if not compliance:
                status['overall_compliance'] = False
                
            status['metrics'][metric_name] = {
                'current_value': metric.current_value,
                'target_value': metric.target_value,
                'unit': metric.unit,
                'compliance': compliance,
                'last_updated': metric.last_updated.isoformat()
            }
            
        return status
        
    async def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        now = datetime.now()
        
        # Calculate statistics for last 24 hours
        start_24h = now - timedelta(hours=24)
        
        recent_response_times = [
            r['response_time'] for r in self.response_times
            if r['timestamp'] >= start_24h and r['success']
        ]
        
        recent_throughput = [
            r['rps'] for r in self.request_counts
            if r['timestamp'] >= start_24h
        ]
        
        report = {
            'report_timestamp': now.isoformat(),
            'period': '24_hours',
            'performance_summary': {
                'response_time': {
                    'p50': statistics.median(recent_response_times) if recent_response_times else 0,
                    'p95': statistics.quantiles(recent_response_times, n=20)[18] if len(recent_response_times) > 20 else 0,
                    'p99': statistics.quantiles(recent_response_times, n=100)[98] if len(recent_response_times) > 100 else 0,
                    'avg': statistics.mean(recent_response_times) if recent_response_times else 0,
                    'max': max(recent_response_times) if recent_response_times else 0
                },
                'throughput': {
                    'avg_rps': statistics.mean(recent_throughput) if recent_throughput else 0,
                    'max_rps': max(recent_throughput) if recent_throughput else 0,
                    'total_requests': sum([r['request_count'] for r in self.request_counts if r['timestamp'] >= start_24h])
                }
            },
            'sla_compliance': await self.get_sla_status(),
            'downtime_events': [
                {
                    'start_time': e['start_time'].isoformat(),
                    'duration_minutes': e['duration_minutes'],
                    'reason': e['reason']
                }
                for e in self.downtime_events
                if e['start_time'] >= start_24h
            ]
        }
        
        return report

# Global SLA tracker instance
sla_tracker = SLATracker()