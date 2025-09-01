"""Enterprise SLA Monitoring & Service Level Management

Comprehensive SLA monitoring system for tracking service level agreements,
availability metrics, and performance guarantees in the IA Influencer platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DevOps + Security

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, copying, or implementation without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import json
import logging


class SLAStatus(Enum):
    """SLA compliance status."""
    COMPLIANT = "compliant"
    AT_RISK = "at_risk"
    VIOLATED = "violated"
    NOT_MEASURED = "not_measured"


class ServiceTier(Enum):
    """Service tier definitions."""
    PREMIUM = "premium"
    STANDARD = "standard"
    BASIC = "basic"


@dataclass
class SLATarget:
    """SLA target definition."""
    name: str
    description: str
    target_value: float
    measurement_unit: str
    measurement_period: str
    service_tier: ServiceTier
    critical: bool = True
    warning_threshold: float = 0.95  # 95% of target before warning


@dataclass
class SLAMeasurement:
    """Individual SLA measurement point."""
    timestamp: datetime
    sla_name: str
    measured_value: float
    target_value: float
    compliant: bool
    service_tier: ServiceTier
    metadata: Dict = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['service_tier'] = self.service_tier.value
        return data


@dataclass 
class SLAReport:
    """SLA compliance report."""
    sla_name: str
    service_tier: ServiceTier
    measurement_period: str
    total_measurements: int
    compliant_measurements: int
    compliance_percentage: float
    current_value: float
    target_value: float
    status: SLAStatus
    violations: List[Dict]
    recommendations: List[str]
    generated_at: datetime

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['service_tier'] = self.service_tier.value
        data['status'] = self.status.value
        data['generated_at'] = self.generated_at.isoformat()
        return data


class ServiceLevelTracker:
    """Tracks service level metrics and compliance."""
    
    def __init__(self, retention_days: int = 30):
        self.retention_days = retention_days
        self.measurements = defaultdict(lambda: deque(maxlen=10000))
        self.sla_targets = {}
        self.violation_history = deque(maxlen=1000)
        
        # Initialize default SLA targets for IA Influencer platform
        self._initialize_default_slas()
    
    def _initialize_default_slas(self):
        """Initialize default SLA targets for the platform."""
        
        # Content Upload SLAs
        self.sla_targets['content_upload_success_rate'] = SLATarget(
            name="content_upload_success_rate",
            description="Content upload success rate",
            target_value=99.5,  # 99.5%
            measurement_unit="percentage",
            measurement_period="daily",
            service_tier=ServiceTier.PREMIUM,
            critical=True,
            warning_threshold=0.98
        )
        
        self.sla_targets['content_upload_response_time'] = SLATarget(
            name="content_upload_response_time",
            description="Content upload response time",
            target_value=5000,  # 5 seconds
            measurement_unit="milliseconds",
            measurement_period="hourly",
            service_tier=ServiceTier.PREMIUM,
            critical=True,
            warning_threshold=0.8  # 80% of target (4 seconds)
        )
        
        # AI Processing SLAs
        self.sla_targets['ai_processing_time'] = SLATarget(
            name="ai_processing_time",
            description="AI content analysis processing time",
            target_value=30000,  # 30 seconds
            measurement_unit="milliseconds", 
            measurement_period="hourly",
            service_tier=ServiceTier.STANDARD,
            critical=True,
            warning_threshold=0.8  # 24 seconds
        )
        
        self.sla_targets['ai_accuracy_rate'] = SLATarget(
            name="ai_accuracy_rate",
            description="AI content protection accuracy",
            target_value=95.0,  # 95%
            measurement_unit="percentage",
            measurement_period="daily",
            service_tier=ServiceTier.PREMIUM,
            critical=True,
            warning_threshold=0.9  # 85.5%
        )
        
        # Protection System SLAs
        self.sla_targets['protection_scan_time'] = SLATarget(
            name="protection_scan_time", 
            description="Content protection scan completion time",
            target_value=60000,  # 1 minute
            measurement_unit="milliseconds",
            measurement_period="hourly",
            service_tier=ServiceTier.STANDARD,
            critical=False,
            warning_threshold=0.8  # 48 seconds
        )
        
        self.sla_targets['violation_detection_time'] = SLATarget(
            name="violation_detection_time",
            description="Time to detect content violations",
            target_value=600000,  # 10 minutes
            measurement_unit="milliseconds",
            measurement_period="hourly",
            service_tier=ServiceTier.PREMIUM,
            critical=True,
            warning_threshold=0.7  # 7 minutes
        )
        
        # System Availability SLAs
        self.sla_targets['system_uptime'] = SLATarget(
            name="system_uptime",
            description="Overall system uptime",
            target_value=99.9,  # 99.9%
            measurement_unit="percentage",
            measurement_period="monthly",
            service_tier=ServiceTier.PREMIUM,
            critical=True,
            warning_threshold=0.995  # 99.4%
        )
        
        self.sla_targets['api_availability'] = SLATarget(
            name="api_availability",
            description="API endpoint availability",
            target_value=99.95,  # 99.95%
            measurement_unit="percentage",
            measurement_period="daily",
            service_tier=ServiceTier.PREMIUM,
            critical=True,
            warning_threshold=0.998  # 99.75%
        )
        
        # Collaboration Matching SLAs
        self.sla_targets['collaboration_match_time'] = SLATarget(
            name="collaboration_match_time",
            description="Time to find collaboration matches",
            target_value=120000,  # 2 minutes
            measurement_unit="milliseconds",
            measurement_period="hourly",
            service_tier=ServiceTier.STANDARD,
            critical=False,
            warning_threshold=0.75  # 1.5 minutes
        )
    
    def record_measurement(self, sla_name: str, measured_value: float, metadata: Dict = None):
        """Record an SLA measurement."""
        if sla_name not in self.sla_targets:
            logging.warning(f"Unknown SLA target: {sla_name}")
            return
        
        target = self.sla_targets[sla_name]
        
        # Determine compliance based on measurement type
        if target.measurement_unit == "percentage":
            compliant = measured_value >= target.target_value
        elif target.measurement_unit == "milliseconds":
            compliant = measured_value <= target.target_value
        else:
            compliant = measured_value >= target.target_value
        
        measurement = SLAMeasurement(
            timestamp=datetime.utcnow(),
            sla_name=sla_name,
            measured_value=measured_value,
            target_value=target.target_value,
            compliant=compliant,
            service_tier=target.service_tier,
            metadata=metadata or {}
        )
        
        self.measurements[sla_name].append(measurement)
        
        # Record violation if not compliant
        if not compliant:
            self._record_violation(measurement)
    
    def _record_violation(self, measurement: SLAMeasurement):
        """Record SLA violation."""
        violation = {
            'timestamp': measurement.timestamp,
            'sla_name': measurement.sla_name,
            'measured_value': measurement.measured_value,
            'target_value': measurement.target_value,
            'service_tier': measurement.service_tier.value,
            'metadata': measurement.metadata
        }
        
        self.violation_history.append(violation)
        logging.warning(f"SLA violation: {measurement.sla_name} = {measurement.measured_value} (target: {measurement.target_value})")
    
    def get_sla_status(self, sla_name: str, period_hours: int = 24) -> SLAStatus:
        """Get current SLA compliance status."""
        if sla_name not in self.sla_targets:
            return SLAStatus.NOT_MEASURED
        
        cutoff_time = datetime.utcnow() - timedelta(hours=period_hours)
        recent_measurements = [
            m for m in self.measurements[sla_name]
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_measurements:
            return SLAStatus.NOT_MEASURED
        
        compliance_rate = sum(1 for m in recent_measurements if m.compliant) / len(recent_measurements)
        target = self.sla_targets[sla_name]
        
        if compliance_rate >= 1.0:
            return SLAStatus.COMPLIANT
        elif compliance_rate >= target.warning_threshold:
            return SLAStatus.AT_RISK
        else:
            return SLAStatus.VIOLATED
    
    def generate_sla_report(self, sla_name: str, period_hours: int = 24) -> Optional[SLAReport]:
        """Generate comprehensive SLA report."""
        if sla_name not in self.sla_targets:
            return None
        
        target = self.sla_targets[sla_name]
        cutoff_time = datetime.utcnow() - timedelta(hours=period_hours)
        
        recent_measurements = [
            m for m in self.measurements[sla_name]
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_measurements:
            return SLAReport(
                sla_name=sla_name,
                service_tier=target.service_tier,
                measurement_period=f"last_{period_hours}_hours",
                total_measurements=0,
                compliant_measurements=0,
                compliance_percentage=0.0,
                current_value=0.0,
                target_value=target.target_value,
                status=SLAStatus.NOT_MEASURED,
                violations=[],
                recommendations=["No measurements available for this period"],
                generated_at=datetime.utcnow()
            )
        
        compliant_count = sum(1 for m in recent_measurements if m.compliant)
        compliance_percentage = (compliant_count / len(recent_measurements)) * 100
        current_value = recent_measurements[-1].measured_value
        
        # Get violations in this period
        violations = [
            {
                'timestamp': m.timestamp.isoformat(),
                'measured_value': m.measured_value,
                'target_value': m.target_value,
                'deviation': abs(m.measured_value - m.target_value)
            }
            for m in recent_measurements if not m.compliant
        ]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(sla_name, recent_measurements, violations)
        
        # Determine status
        status = self.get_sla_status(sla_name, period_hours)
        
        return SLAReport(
            sla_name=sla_name,
            service_tier=target.service_tier,
            measurement_period=f"last_{period_hours}_hours",
            total_measurements=len(recent_measurements),
            compliant_measurements=compliant_count,
            compliance_percentage=compliance_percentage,
            current_value=current_value,
            target_value=target.target_value,
            status=status,
            violations=violations,
            recommendations=recommendations,
            generated_at=datetime.utcnow()
        )
    
    def _generate_recommendations(self, sla_name: str, measurements: List[SLAMeasurement], violations: List[Dict]) -> List[str]:
        """Generate actionable recommendations based on SLA performance."""
        recommendations = []
        
        if not violations:
            recommendations.append("SLA is performing well. Continue current practices.")
            return recommendations
        
        violation_count = len(violations)
        total_measurements = len(measurements)
        
        # General recommendations based on violation rate
        if violation_count / total_measurements > 0.1:  # More than 10% violations
            recommendations.append("High violation rate detected. Consider reviewing system capacity and performance.")
        
        # Specific recommendations based on SLA type
        if "upload" in sla_name.lower():
            if violation_count > 5:
                recommendations.extend([
                    "Consider increasing upload server capacity",
                    "Review file size limits and compression algorithms",
                    "Implement client-side upload optimization"
                ])
        
        elif "ai" in sla_name.lower():
            if violation_count > 3:
                recommendations.extend([
                    "Consider scaling AI processing resources",
                    "Review model optimization opportunities",
                    "Implement request queuing and prioritization"
                ])
        
        elif "protection" in sla_name.lower():
            if violation_count > 2:
                recommendations.extend([
                    "Scale content scanning infrastructure",
                    "Optimize fingerprinting algorithms",
                    "Consider parallel processing implementation"
                ])
        
        elif "collaboration" in sla_name.lower():
            if violation_count > 5:
                recommendations.extend([
                    "Optimize matching algorithms",
                    "Consider caching frequent matches",
                    "Review database query performance"
                ])
        
        elif "uptime" in sla_name.lower() or "availability" in sla_name.lower():
            if violation_count > 1:
                recommendations.extend([
                    "Review system stability and error rates",
                    "Consider implementing redundancy",
                    "Review monitoring and alerting configuration"
                ])
        
        return recommendations
    
    def cleanup_old_measurements(self):
        """Clean up old measurements beyond retention period."""
        cutoff_time = datetime.utcnow() - timedelta(days=self.retention_days)
        
        for sla_name in self.measurements:
            measurements = self.measurements[sla_name]
            while measurements and measurements[0].timestamp < cutoff_time:
                measurements.popleft()


class AvailabilityCalculator:
    """Calculates system availability and uptime metrics."""
    
    def __init__(self):
        self.uptime_events = deque(maxlen=10000)
        self.downtime_events = deque(maxlen=1000)
        
    def record_uptime_event(self, service_name: str, timestamp: datetime = None):
        """Record a service uptime event."""
        event = {
            'timestamp': timestamp or datetime.utcnow(),
            'service': service_name,
            'event_type': 'up'
        }
        self.uptime_events.append(event)
    
    def record_downtime_event(self, service_name: str, duration_seconds: int, reason: str = None, timestamp: datetime = None):
        """Record a service downtime event."""
        event = {
            'timestamp': timestamp or datetime.utcnow(),
            'service': service_name,
            'event_type': 'down',
            'duration_seconds': duration_seconds,
            'reason': reason or 'Unknown'
        }
        self.downtime_events.append(event)
    
    def calculate_availability(self, service_name: str, period_hours: int = 24) -> Dict:
        """Calculate availability metrics for a service."""
        cutoff_time = datetime.utcnow() - timedelta(hours=period_hours)
        
        # Get relevant events for the period
        relevant_downtime = [
            event for event in self.downtime_events
            if event['service'] == service_name and event['timestamp'] >= cutoff_time
        ]
        
        # Calculate total downtime in the period
        total_downtime_seconds = sum(event['duration_seconds'] for event in relevant_downtime)
        total_period_seconds = period_hours * 3600
        
        # Calculate availability
        uptime_seconds = total_period_seconds - total_downtime_seconds
        availability_percentage = (uptime_seconds / total_period_seconds) * 100
        
        # Calculate downtime breakdown by reason
        downtime_by_reason = defaultdict(int)
        for event in relevant_downtime:
            downtime_by_reason[event['reason']] += event['duration_seconds']
        
        return {
            'service_name': service_name,
            'period_hours': period_hours,
            'availability_percentage': round(availability_percentage, 3),
            'uptime_seconds': uptime_seconds,
            'downtime_seconds': total_downtime_seconds,
            'downtime_events_count': len(relevant_downtime),
            'downtime_by_reason': dict(downtime_by_reason),
            'mtbf_hours': self._calculate_mtbf(service_name, period_hours),  # Mean Time Between Failures
            'mttr_minutes': self._calculate_mttr(service_name, period_hours),  # Mean Time To Recovery
            'calculated_at': datetime.utcnow().isoformat()
        }
    
    def _calculate_mtbf(self, service_name: str, period_hours: int) -> float:
        """Calculate Mean Time Between Failures."""
        cutoff_time = datetime.utcnow() - timedelta(hours=period_hours)
        
        failures = [
            event for event in self.downtime_events
            if event['service'] == service_name and event['timestamp'] >= cutoff_time
        ]
        
        if len(failures) <= 1:
            return period_hours  # If 0 or 1 failure, MTBF is the entire period
        
        # Calculate time between consecutive failures
        failure_times = sorted([event['timestamp'] for event in failures])
        intervals = []
        
        for i in range(1, len(failure_times)):
            interval_seconds = (failure_times[i] - failure_times[i-1]).total_seconds()
            intervals.append(interval_seconds / 3600)  # Convert to hours
        
        return sum(intervals) / len(intervals) if intervals else period_hours
    
    def _calculate_mttr(self, service_name: str, period_hours: int) -> float:
        """Calculate Mean Time To Recovery."""
        cutoff_time = datetime.utcnow() - timedelta(hours=period_hours)
        
        downtimes = [
            event['duration_seconds'] for event in self.downtime_events
            if event['service'] == service_name and event['timestamp'] >= cutoff_time
        ]
        
        if not downtimes:
            return 0.0
        
        return (sum(downtimes) / len(downtimes)) / 60  # Convert to minutes
    
    def get_service_availability_summary(self, period_hours: int = 24) -> Dict:
        """Get availability summary for all services."""
        # Get unique service names
        all_services = set()
        for event in list(self.uptime_events) + list(self.downtime_events):
            all_services.add(event['service'])
        
        summary = {}
        for service in all_services:
            summary[service] = self.calculate_availability(service, period_hours)
        
        # Calculate overall system availability
        if summary:
            total_availability = sum(data['availability_percentage'] for data in summary.values())
            overall_availability = total_availability / len(summary)
        else:
            overall_availability = 100.0
        
        return {
            'services': summary,
            'overall_availability': round(overall_availability, 3),
            'period_hours': period_hours,
            'total_services_monitored': len(all_services),
            'generated_at': datetime.utcnow().isoformat()
        }


class SLAMonitor:
    """Main SLA monitoring orchestrator."""
    
    def __init__(self, retention_days: int = 30):
        self.service_tracker = ServiceLevelTracker(retention_days)
        self.availability_calculator = AvailabilityCalculator()
        self.monitoring_active = False
        
    def start_monitoring(self):
        """Start SLA monitoring."""
        self.monitoring_active = True
        logging.info("SLA monitoring started")
    
    def stop_monitoring(self):
        """Stop SLA monitoring."""
        self.monitoring_active = False
        logging.info("SLA monitoring stopped")
    
    async def record_content_upload_metrics(self, success: bool, response_time_ms: float):
        """Record content upload SLA metrics."""
        # Record success rate
        success_rate = 100.0 if success else 0.0
        self.service_tracker.record_measurement("content_upload_success_rate", success_rate)
        
        # Record response time
        self.service_tracker.record_measurement("content_upload_response_time", response_time_ms)
        
        # Record availability event
        if success:
            self.availability_calculator.record_uptime_event("content_upload")
        else:
            # If this is a failure, it could indicate downtime
            self.availability_calculator.record_downtime_event(
                "content_upload", 
                duration_seconds=max(1, int(response_time_ms / 1000)),
                reason="Upload failure"
            )
    
    async def record_ai_processing_metrics(self, processing_time_ms: float, accuracy_score: float = None):
        """Record AI processing SLA metrics."""
        self.service_tracker.record_measurement("ai_processing_time", processing_time_ms)
        
        if accuracy_score is not None:
            self.service_tracker.record_measurement("ai_accuracy_rate", accuracy_score * 100)
        
        self.availability_calculator.record_uptime_event("ai_processing")
    
    async def record_protection_metrics(self, scan_time_ms: float, violation_detected: bool, detection_time_ms: float = None):
        """Record content protection SLA metrics."""
        self.service_tracker.record_measurement("protection_scan_time", scan_time_ms)
        
        if violation_detected and detection_time_ms:
            self.service_tracker.record_measurement("violation_detection_time", detection_time_ms)
        
        self.availability_calculator.record_uptime_event("content_protection")
    
    async def record_system_availability(self, uptime_percentage: float):
        """Record overall system availability."""
        self.service_tracker.record_measurement("system_uptime", uptime_percentage)
        
        if uptime_percentage >= 99.0:
            self.availability_calculator.record_uptime_event("system")
        else:
            downtime_seconds = int((100 - uptime_percentage) * 36)  # Approximate downtime in last hour
            self.availability_calculator.record_downtime_event(
                "system",
                duration_seconds=downtime_seconds,
                reason="System degradation"
            )
    
    def get_sla_dashboard_data(self) -> Dict:
        """Get comprehensive SLA dashboard data."""
        dashboard_data = {
            'overview': {
                'monitoring_active': self.monitoring_active,
                'total_sla_targets': len(self.service_tracker.sla_targets),
                'recent_violations': len([
                    v for v in self.service_tracker.violation_history
                    if v['timestamp'] >= datetime.utcnow() - timedelta(hours=24)
                ])
            },
            'sla_status': {},
            'availability_summary': self.availability_calculator.get_service_availability_summary(),
            'recent_reports': {},
            'recommendations': []
        }
        
        # Get status for all SLA targets
        for sla_name in self.service_tracker.sla_targets:
            dashboard_data['sla_status'][sla_name] = {
                'status': self.service_tracker.get_sla_status(sla_name).value,
                'target_value': self.service_tracker.sla_targets[sla_name].target_value,
                'service_tier': self.service_tracker.sla_targets[sla_name].service_tier.value
            }
        
        # Generate recent reports for critical SLAs
        critical_slas = [
            name for name, target in self.service_tracker.sla_targets.items()
            if target.critical
        ]
        
        for sla_name in critical_slas:
            report = self.service_tracker.generate_sla_report(sla_name, period_hours=24)
            if report:
                dashboard_data['recent_reports'][sla_name] = report.to_dict()
        
        # Aggregate recommendations
        all_recommendations = set()
        for report_data in dashboard_data['recent_reports'].values():
            all_recommendations.update(report_data.get('recommendations', []))
        
        dashboard_data['recommendations'] = list(all_recommendations)
        dashboard_data['generated_at'] = datetime.utcnow().isoformat()
        
        return dashboard_data
    
    async def cleanup_old_data(self):
        """Clean up old monitoring data."""
        self.service_tracker.cleanup_old_measurements()
        logging.info("SLA monitoring data cleanup completed")
