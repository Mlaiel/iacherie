#!/usr/bin/env python3
"""
Ainflue Platform - Distribution Monitoring - SLA Monitor
Advanced Service Level Agreement monitoring and compliance tracking

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import statistics
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

class SLAMetricType(Enum):
    """Types of SLA metrics"""
    AVAILABILITY = "availability"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    UPTIME = "uptime"
    DATA_INTEGRITY = "data_integrity"
    SECURITY_COMPLIANCE = "security_compliance"

class SLAStatus(Enum):
    """SLA compliance status"""
    COMPLIANT = "compliant"
    WARNING = "warning"
    BREACH = "breach"
    CRITICAL = "critical"

class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SLATarget:
    """SLA target definition"""
    metric_type: SLAMetricType
    target_value: float
    threshold_warning: float
    threshold_critical: float
    measurement_window: timedelta
    unit: str
    description: str

@dataclass
class SLAMeasurement:
    """Individual SLA measurement"""
    timestamp: datetime
    metric_type: SLAMetricType
    value: float
    target: SLATarget
    status: SLAStatus
    metadata: Dict[str, Any] = None

@dataclass
class SLABreach:
    """SLA breach incident"""
    breach_id: str
    metric_type: SLAMetricType
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[timedelta]
    severity: AlertSeverity
    target_value: float
    actual_value: float
    impact_description: str
    root_cause: Optional[str] = None
    resolution_actions: List[str] = None

@dataclass
class SLAReport:
    """SLA compliance report"""
    period_start: datetime
    period_end: datetime
    overall_compliance: float
    metric_compliance: Dict[SLAMetricType, float]
    breaches: List[SLABreach]
    trends: Dict[str, Any]
    recommendations: List[str]

class DistributionSLAMonitor:
    """
    Advanced SLA monitoring system for distribution services
    Tracks compliance, detects breaches, and provides detailed reporting
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.sla_targets: Dict[SLAMetricType, SLATarget] = {}
        self.measurements: Dict[SLAMetricType, deque] = {}
        self.active_breaches: Dict[str, SLABreach] = {}
        self.historical_breaches: List[SLABreach] = []
        self.compliance_history: List[Dict] = []
        
        # Initialize SLA targets
        self._initialize_sla_targets()
        
        # Initialize measurement buffers
        for metric_type in SLAMetricType:
            self.measurements[metric_type] = deque(maxlen=1000)
    
    def _initialize_sla_targets(self):
        """Initialize standard SLA targets for distribution services"""
        
        # Availability SLA: 99.9% uptime
        self.sla_targets[SLAMetricType.AVAILABILITY] = SLATarget(
            metric_type=SLAMetricType.AVAILABILITY,
            target_value=99.9,
            threshold_warning=99.5,
            threshold_critical=99.0,
            measurement_window=timedelta(hours=1),
            unit="%",
            description="Service availability percentage"
        )
        
        # Response Time SLA: 95th percentile < 200ms
        self.sla_targets[SLAMetricType.RESPONSE_TIME] = SLATarget(
            metric_type=SLAMetricType.RESPONSE_TIME,
            target_value=200.0,
            threshold_warning=250.0,
            threshold_critical=500.0,
            measurement_window=timedelta(minutes=5),
            unit="ms",
            description="95th percentile response time"
        )
        
        # Throughput SLA: > 1000 requests per second
        self.sla_targets[SLAMetricType.THROUGHPUT] = SLATarget(
            metric_type=SLAMetricType.THROUGHPUT,
            target_value=1000.0,
            threshold_warning=800.0,
            threshold_critical=500.0,
            measurement_window=timedelta(minutes=1),
            unit="req/s",
            description="Minimum throughput capacity"
        )
        
        # Error Rate SLA: < 0.1%
        self.sla_targets[SLAMetricType.ERROR_RATE] = SLATarget(
            metric_type=SLAMetricType.ERROR_RATE,
            target_value=0.1,
            threshold_warning=0.5,
            threshold_critical=1.0,
            measurement_window=timedelta(minutes=5),
            unit="%",
            description="Error rate percentage"
        )
        
        # Data Integrity SLA: 99.99%
        self.sla_targets[SLAMetricType.DATA_INTEGRITY] = SLATarget(
            metric_type=SLAMetricType.DATA_INTEGRITY,
            target_value=99.99,
            threshold_warning=99.9,
            threshold_critical=99.5,
            measurement_window=timedelta(hours=1),
            unit="%",
            description="Data integrity and consistency"
        )
    
    async def record_measurement(self, metric_type: SLAMetricType, value: float, 
                               metadata: Optional[Dict] = None) -> SLAMeasurement:
        """
        Record an SLA measurement and check compliance
        
        Args:
            metric_type: Type of SLA metric
            value: Measured value
            metadata: Additional measurement metadata
            
        Returns:
            SLA measurement with compliance status
        """
        if metric_type not in self.sla_targets:
            raise ValueError(f"No SLA target defined for {metric_type.value}")
        
        target = self.sla_targets[metric_type]
        status = self._assess_compliance_status(metric_type, value)
        
        measurement = SLAMeasurement(
            timestamp=datetime.utcnow(),
            metric_type=metric_type,
            value=value,
            target=target,
            status=status,
            metadata=metadata or {}
        )
        
        # Store measurement
        self.measurements[metric_type].append(measurement)
        
        # Check for SLA breaches
        await self._check_sla_breach(measurement)
        
        logger.debug(f"Recorded {metric_type.value} measurement: {value} {target.unit} ({status.value})")
        return measurement
    
    def _assess_compliance_status(self, metric_type: SLAMetricType, value: float) -> SLAStatus:
        """Assess compliance status based on value and thresholds"""
        
        target = self.sla_targets[metric_type]
        
        # Different logic for different metrics
        if metric_type in [SLAMetricType.AVAILABILITY, SLAMetricType.DATA_INTEGRITY, SLAMetricType.THROUGHPUT]:
            # Higher is better
            if value >= target.target_value:
                return SLAStatus.COMPLIANT
            elif value >= target.threshold_warning:
                return SLAStatus.WARNING
            elif value >= target.threshold_critical:
                return SLAStatus.BREACH
            else:
                return SLAStatus.CRITICAL
        
        else:
            # Lower is better (response time, error rate)
            if value <= target.target_value:
                return SLAStatus.COMPLIANT
            elif value <= target.threshold_warning:
                return SLAStatus.WARNING
            elif value <= target.threshold_critical:
                return SLAStatus.BREACH
            else:
                return SLAStatus.CRITICAL
    
    async def _check_sla_breach(self, measurement: SLAMeasurement):
        """Check if measurement indicates an SLA breach"""
        
        if measurement.status in [SLAStatus.BREACH, SLAStatus.CRITICAL]:
            breach_id = f"SLA-{measurement.metric_type.value}-{int(time.time() * 1000)}"
            
            # Check if this is a continuation of an existing breach
            existing_breach = None
            for breach in self.active_breaches.values():
                if (breach.metric_type == measurement.metric_type and 
                    breach.end_time is None and
                    (measurement.timestamp - breach.start_time) < timedelta(minutes=15)):
                    existing_breach = breach
                    break
            
            if existing_breach:
                # Update existing breach
                existing_breach.actual_value = measurement.value
                if measurement.status == SLAStatus.CRITICAL:
                    existing_breach.severity = AlertSeverity.CRITICAL
                logger.warning(f"SLA breach continues: {breach_id}")
            
            else:
                # Create new breach
                severity = AlertSeverity.CRITICAL if measurement.status == SLAStatus.CRITICAL else AlertSeverity.HIGH
                
                breach = SLABreach(
                    breach_id=breach_id,
                    metric_type=measurement.metric_type,
                    start_time=measurement.timestamp,
                    end_time=None,
                    duration=None,
                    severity=severity,
                    target_value=measurement.target.target_value,
                    actual_value=measurement.value,
                    impact_description=self._generate_impact_description(measurement)
                )
                
                self.active_breaches[breach_id] = breach
                logger.critical(f"SLA BREACH DETECTED: {breach_id} - {breach.impact_description}")
                
                # Trigger breach notification
                await self._notify_sla_breach(breach)
        
        else:
            # Check if any active breaches for this metric should be resolved
            await self._check_breach_resolution(measurement)
    
    async def _check_breach_resolution(self, measurement: SLAMeasurement):
        """Check if active breaches should be resolved"""
        
        if measurement.status == SLAStatus.COMPLIANT:
            resolved_breaches = []
            
            for breach_id, breach in self.active_breaches.items():
                if breach.metric_type == measurement.metric_type and breach.end_time is None:
                    # Resolve the breach
                    breach.end_time = measurement.timestamp
                    breach.duration = breach.end_time - breach.start_time
                    
                    self.historical_breaches.append(breach)
                    resolved_breaches.append(breach_id)
                    
                    logger.info(f"SLA breach resolved: {breach_id} (Duration: {breach.duration})")
            
            # Remove resolved breaches from active list
            for breach_id in resolved_breaches:
                del self.active_breaches[breach_id]
    
    def _generate_impact_description(self, measurement: SLAMeasurement) -> str:
        """Generate impact description for SLA breach"""
        
        metric_descriptions = {
            SLAMetricType.AVAILABILITY: f"Service availability dropped to {measurement.value:.2f}%",
            SLAMetricType.RESPONSE_TIME: f"Response time increased to {measurement.value:.1f}ms",
            SLAMetricType.THROUGHPUT: f"Throughput decreased to {measurement.value:.1f} req/s",
            SLAMetricType.ERROR_RATE: f"Error rate increased to {measurement.value:.2f}%",
            SLAMetricType.DATA_INTEGRITY: f"Data integrity compromised at {measurement.value:.2f}%"
        }
        
        return metric_descriptions.get(measurement.metric_type, f"{measurement.metric_type.value} SLA breach")
    
    async def _notify_sla_breach(self, breach: SLABreach):
        """Send notifications for SLA breach"""
        
        # In a real implementation, this would send emails, Slack messages, etc.
        notification_message = f"""
        🚨 SLA BREACH ALERT
        
        Breach ID: {breach.breach_id}
        Metric: {breach.metric_type.value}
        Severity: {breach.severity.value}
        Target: {breach.target_value}
        Actual: {breach.actual_value}
        Impact: {breach.impact_description}
        Time: {breach.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}
        
        Immediate attention required!
        """
        
        logger.critical(f"SLA BREACH NOTIFICATION: {notification_message}")
    
    async def calculate_compliance_metrics(self, period_start: datetime, 
                                         period_end: datetime) -> Dict[SLAMetricType, float]:
        """Calculate compliance percentages for each SLA metric over a period"""
        
        compliance_metrics = {}
        
        for metric_type in SLAMetricType:
            if metric_type not in self.measurements:
                continue
            
            # Filter measurements for the period
            period_measurements = [
                m for m in self.measurements[metric_type]
                if period_start <= m.timestamp <= period_end
            ]
            
            if not period_measurements:
                compliance_metrics[metric_type] = 100.0
                continue
            
            # Calculate compliance percentage
            compliant_measurements = [
                m for m in period_measurements
                if m.status == SLAStatus.COMPLIANT
            ]
            
            compliance_percentage = (len(compliant_measurements) / len(period_measurements)) * 100
            compliance_metrics[metric_type] = compliance_percentage
        
        return compliance_metrics
    
    async def generate_sla_report(self, period_start: datetime, 
                                period_end: datetime) -> SLAReport:
        """
        Generate comprehensive SLA compliance report
        
        Args:
            period_start: Report period start
            period_end: Report period end
            
        Returns:
            Detailed SLA compliance report
        """
        logger.info(f"Generating SLA report for period {period_start} to {period_end}")
        
        # Calculate compliance metrics
        metric_compliance = await self.calculate_compliance_metrics(period_start, period_end)
        
        # Calculate overall compliance
        if metric_compliance:
            overall_compliance = statistics.mean(metric_compliance.values())
        else:
            overall_compliance = 100.0
        
        # Get breaches for the period
        period_breaches = [
            breach for breach in self.historical_breaches
            if period_start <= breach.start_time <= period_end
        ]
        
        # Add active breaches that started in the period
        period_breaches.extend([
            breach for breach in self.active_breaches.values()
            if period_start <= breach.start_time <= period_end
        ])
        
        # Calculate trends
        trends = await self._calculate_sla_trends(period_start, period_end)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metric_compliance, period_breaches)
        
        report = SLAReport(
            period_start=period_start,
            period_end=period_end,
            overall_compliance=overall_compliance,
            metric_compliance=metric_compliance,
            breaches=period_breaches,
            trends=trends,
            recommendations=recommendations
        )
        
        logger.info(f"SLA report generated: {overall_compliance:.2f}% overall compliance")
        return report
    
    async def _calculate_sla_trends(self, period_start: datetime, 
                                  period_end: datetime) -> Dict[str, Any]:
        """Calculate SLA trends over the period"""
        
        trends = {}
        
        for metric_type in SLAMetricType:
            if metric_type not in self.measurements:
                continue
            
            # Get measurements for the period
            period_measurements = [
                m for m in self.measurements[metric_type]
                if period_start <= m.timestamp <= period_end
            ]
            
            if len(period_measurements) < 2:
                continue
            
            # Sort by timestamp
            period_measurements.sort(key=lambda x: x.timestamp)
            
            # Calculate trend metrics
            values = [m.value for m in period_measurements]
            
            # Simple linear trend calculation
            n = len(values)
            x = list(range(n))
            x_mean = statistics.mean(x)
            y_mean = statistics.mean(values)
            
            numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            
            if denominator != 0:
                slope = numerator / denominator
                
                trends[metric_type.value] = {
                    'slope': slope,
                    'direction': 'improving' if slope > 0 else 'degrading' if slope < 0 else 'stable',
                    'min_value': min(values),
                    'max_value': max(values),
                    'avg_value': statistics.mean(values),
                    'std_dev': statistics.stdev(values) if len(values) > 1 else 0
                }
        
        return trends
    
    def _generate_recommendations(self, compliance_metrics: Dict[SLAMetricType, float], 
                                breaches: List[SLABreach]) -> List[str]:
        """Generate recommendations based on SLA performance"""
        
        recommendations = []
        
        # Check compliance levels
        for metric_type, compliance in compliance_metrics.items():
            if compliance < 95.0:
                recommendations.append(
                    f"Critical: {metric_type.value} compliance at {compliance:.1f}% - "
                    f"immediate investigation and remediation required"
                )
            elif compliance < 98.0:
                recommendations.append(
                    f"Review {metric_type.value} performance - compliance at {compliance:.1f}%"
                )
        
        # Analyze breach patterns
        if breaches:
            breach_counts = defaultdict(int)
            for breach in breaches:
                breach_counts[breach.metric_type] += 1
            
            for metric_type, count in breach_counts.items():
                if count > 5:
                    recommendations.append(
                        f"High frequency of {metric_type.value} breaches ({count}) - "
                        f"consider infrastructure scaling or optimization"
                    )
        
        # General recommendations
        if not recommendations:
            recommendations.append("SLA performance is meeting targets - continue monitoring")
        else:
            recommendations.append("Implement automated alerting for early breach detection")
            recommendations.append("Review and update SLA targets based on business requirements")
        
        return recommendations
    
    async def get_sla_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time SLA dashboard data"""
        
        current_time = datetime.utcnow()
        hour_ago = current_time - timedelta(hours=1)
        
        # Calculate current compliance
        current_compliance = await self.calculate_compliance_metrics(hour_ago, current_time)
        
        # Get recent measurements
        recent_measurements = {}
        for metric_type in SLAMetricType:
            if metric_type in self.measurements and self.measurements[metric_type]:
                latest = self.measurements[metric_type][-1]
                recent_measurements[metric_type.value] = {
                    'value': latest.value,
                    'status': latest.status.value,
                    'timestamp': latest.timestamp.isoformat(),
                    'target': latest.target.target_value,
                    'unit': latest.target.unit
                }
        
        # Active breaches summary
        active_breaches_summary = []
        for breach in self.active_breaches.values():
            active_breaches_summary.append({
                'id': breach.breach_id,
                'metric': breach.metric_type.value,
                'severity': breach.severity.value,
                'duration': str(current_time - breach.start_time),
                'impact': breach.impact_description
            })
        
        return {
            'timestamp': current_time.isoformat(),
            'overall_status': 'healthy' if len(self.active_breaches) == 0 else 'degraded',
            'compliance_metrics': {k.value: v for k, v in current_compliance.items()},
            'recent_measurements': recent_measurements,
            'active_breaches': active_breaches_summary,
            'total_active_breaches': len(self.active_breaches),
            'sla_targets': {
                k.value: {
                    'target': v.target_value,
                    'warning': v.threshold_warning,
                    'critical': v.threshold_critical,
                    'unit': v.unit
                }
                for k, v in self.sla_targets.items()
            }
        }
    
    async def simulate_sla_impact(self, metric_type: SLAMetricType, 
                                degradation_percent: float, 
                                duration_minutes: int) -> Dict[str, Any]:
        """Simulate the impact of SLA degradation"""
        
        if metric_type not in self.sla_targets:
            raise ValueError(f"No SLA target defined for {metric_type.value}")
        
        target = self.sla_targets[metric_type]
        current_value = target.target_value
        
        # Calculate degraded value
        if metric_type in [SLAMetricType.AVAILABILITY, SLAMetricType.DATA_INTEGRITY, SLAMetricType.THROUGHPUT]:
            degraded_value = current_value * (1 - degradation_percent / 100)
        else:
            degraded_value = current_value * (1 + degradation_percent / 100)
        
        # Assess impact
        status = self._assess_compliance_status(metric_type, degraded_value)
        
        # Calculate compliance impact
        measurements_per_hour = 60 // 5  # Assuming 5-minute intervals
        affected_measurements = (duration_minutes // 5) + 1
        total_measurements_in_hour = measurements_per_hour
        
        compliance_impact = (affected_measurements / total_measurements_in_hour) * 100
        
        return {
            'metric_type': metric_type.value,
            'current_value': current_value,
            'degraded_value': degraded_value,
            'degradation_percent': degradation_percent,
            'duration_minutes': duration_minutes,
            'resulting_status': status.value,
            'compliance_impact_percent': compliance_impact,
            'would_breach_sla': status in [SLAStatus.BREACH, SLAStatus.CRITICAL],
            'estimated_recovery_time': duration_minutes * 1.5  # Assume 50% longer to recover
        }

# Factory function
def create_sla_monitor(config: Optional[Dict] = None) -> DistributionSLAMonitor:
    """Create SLA monitor instance"""
    return DistributionSLAMonitor(config)

# Example usage
async def main():
    """Example usage of SLA monitor"""
    monitor = create_sla_monitor()
    
    # Record some measurements
    await monitor.record_measurement(SLAMetricType.AVAILABILITY, 99.8)
    await monitor.record_measurement(SLAMetricType.RESPONSE_TIME, 180.5)
    await monitor.record_measurement(SLAMetricType.ERROR_RATE, 0.05)
    
    # Simulate an SLA breach
    await monitor.record_measurement(SLAMetricType.RESPONSE_TIME, 600.0)  # This should trigger a breach
    
    # Generate report
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)
    report = await monitor.generate_sla_report(start_time, end_time)
    
    print(f"Overall compliance: {report.overall_compliance:.2f}%")
    print(f"Active breaches: {len(monitor.active_breaches)}")
    
    # Get dashboard data
    dashboard = await monitor.get_sla_dashboard_data()
    print(f"Dashboard status: {dashboard['overall_status']}")

if __name__ == "__main__":
    asyncio.run(main())