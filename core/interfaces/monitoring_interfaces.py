"""
Monitoring interfaces for IA Influencer Agent.

Defines interfaces for system monitoring, alerting, performance tracking,
health monitoring and compliance monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
© 2025 - All rights reserved. Unauthorized use prohibited.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
from enum import Enum


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MonitoringType(Enum):
    """Types of monitoring operations."""
    REAL_TIME = "real_time"
    BATCH = "batch"
    SCHEDULED = "scheduled"
    CONTINUOUS = "continuous"
    EVENT_DRIVEN = "event_driven"


class MonitoringMetric(Enum):
    """System monitoring metrics."""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_TRAFFIC = "network_traffic"
    API_RESPONSE_TIME = "api_response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    AVAILABILITY = "availability"


class HealthStatus(Enum):
    """System health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


class MonitoringInterface(ABC):
    """Core interface for system monitoring operations."""
    
    @abstractmethod
    async def collect_system_metrics(
        self,
        metric_types: List[MonitoringMetric],
        collection_interval: int
    ) -> Dict[str, Any]:
        """
        Collect system performance metrics.
        
        Args:
            metric_types: Types of metrics to collect
            collection_interval: Collection interval in seconds
            
        Returns:
            Collected metrics data with timestamps
        """
        pass
    
    @abstractmethod
    async def monitor_application_performance(
        self,
        application_id: str,
        performance_thresholds: Dict[str, float]
    ) -> Dict[str, Any]:
        """Monitor application performance against thresholds."""
        pass
    
    @abstractmethod
    async def track_user_activity(
        self,
        tracking_scope: List[str],
        tracking_period: str
    ) -> Dict[str, Any]:
        """Track user activity patterns and trends."""
        pass
    
    @abstractmethod
    async def monitor_content_processing(
        self,
        processing_pipeline: str,
        monitoring_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Monitor content processing pipeline performance."""
        pass
    
    @abstractmethod
    async def analyze_system_trends(
        self,
        metric_history: Dict[str, List[float]],
        analysis_period: str
    ) -> Dict[str, Any]:
        """Analyze system performance trends and patterns."""
        pass
    
    @abstractmethod
    async def generate_monitoring_dashboard(
        self,
        dashboard_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate real-time monitoring dashboard data."""
        pass


class AlertManagerInterface(ABC):
    """Interface for alert management and notification."""
    
    @abstractmethod
    async def create_alert_rule(
        self,
        rule_name: str,
        condition: Dict[str, Any],
        alert_config: Dict[str, Any]
    ) -> str:
        """
        Create new alert rule.
        
        Args:
            rule_name: Name of the alert rule
            condition: Alert triggering condition
            alert_config: Alert configuration and notification settings
            
        Returns:
            Created alert rule ID
        """
        pass
    
    @abstractmethod
    async def trigger_alert(
        self,
        alert_type: str,
        severity: AlertSeverity,
        alert_data: Dict[str, Any]
    ) -> str:
        """Trigger alert based on detected condition."""
        pass
    
    @abstractmethod
    async def manage_alert_escalation(
        self,
        alert_id: str,
        escalation_policy: Dict[str, Any]
    ) -> bool:
        """Manage alert escalation according to policy."""
        pass
    
    @abstractmethod
    async def acknowledge_alert(
        self,
        alert_id: str,
        acknowledger_id: str,
        acknowledgment_note: Optional[str] = None
    ) -> bool:
        """Acknowledge alert and stop notifications."""
        pass
    
    @abstractmethod
    async def resolve_alert(
        self,
        alert_id: str,
        resolver_id: str,
        resolution_details: Dict[str, Any]
    ) -> bool:
        """Mark alert as resolved with details."""
        pass
    
    @abstractmethod
    async def configure_notification_channels(
        self,
        channel_config: Dict[str, Any]
    ) -> List[str]:
        """Configure alert notification channels."""
        pass


class PerformanceTrackerInterface(ABC):
    """Interface for performance tracking and optimization."""
    
    @abstractmethod
    async def track_api_performance(
        self,
        endpoint: str,
        request_data: Dict[str, Any],
        response_time: float
    ) -> bool:
        """
        Track API endpoint performance.
        
        Args:
            endpoint: API endpoint being tracked
            request_data: Request metadata
            response_time: Response time in milliseconds
            
        Returns:
            Success status of performance tracking
        """
        pass
    
    @abstractmethod
    async def analyze_performance_bottlenecks(
        self,
        system_component: str,
        analysis_period: str
    ) -> List[Dict[str, Any]]:
        """Analyze and identify performance bottlenecks."""
        pass
    
    @abstractmethod
    async def generate_performance_recommendations(
        self,
        performance_data: Dict[str, Any],
        optimization_goals: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate performance optimization recommendations."""
        pass
    
    @abstractmethod
    async def track_resource_utilization(
        self,
        resource_types: List[str],
        tracking_duration: int
    ) -> Dict[str, Any]:
        """Track system resource utilization patterns."""
        pass
    
    @abstractmethod
    async def benchmark_system_performance(
        self,
        benchmark_suite: str,
        comparison_baseline: Dict[str, float]
    ) -> Dict[str, Any]:
        """Benchmark system performance against baseline."""
        pass
    
    @abstractmethod
    async def optimize_cache_performance(
        self,
        cache_system: str,
        optimization_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize cache performance and hit rates."""
        pass


class SystemHealthInterface(ABC):
    """Interface for system health monitoring."""
    
    @abstractmethod
    async def check_system_health(
        self,
        health_check_config: Dict[str, Any]
    ) -> Dict[str, HealthStatus]:
        """
        Perform comprehensive system health check.
        
        Args:
            health_check_config: Health check configuration
            
        Returns:
            Health status for each system component
        """
        pass
    
    @abstractmethod
    async def monitor_service_dependencies(
        self,
        service_map: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Monitor health of service dependencies."""
        pass
    
    @abstractmethod
    async def detect_system_anomalies(
        self,
        anomaly_detection_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect system anomalies using ML algorithms."""
        pass
    
    @abstractmethod
    async def predict_system_failures(
        self,
        prediction_model: str,
        system_metrics: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """Predict potential system failures."""
        pass
    
    @abstractmethod
    async def generate_health_report(
        self,
        report_scope: List[str],
        report_period: str
    ) -> Dict[str, Any]:
        """Generate comprehensive system health report."""
        pass
    
    @abstractmethod
    async def implement_auto_recovery(
        self,
        failure_scenario: str,
        recovery_procedures: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Implement automated system recovery procedures."""
        pass


class ComplianceMonitorInterface(ABC):
    """Interface for compliance monitoring and reporting."""
    
    @abstractmethod
    async def monitor_data_privacy_compliance(
        self,
        privacy_regulations: List[str],
        monitoring_scope: List[str]
    ) -> Dict[str, Any]:
        """
        Monitor compliance with data privacy regulations.
        
        Args:
            privacy_regulations: List of applicable regulations (GDPR, CCPA, etc.)
            monitoring_scope: Scope of compliance monitoring
            
        Returns:
            Compliance status and violation reports
        """
        pass
    
    @abstractmethod
    async def audit_security_compliance(
        self,
        security_frameworks: List[str],
        audit_scope: List[str]
    ) -> Dict[str, Any]:
        """Audit compliance with security frameworks."""
        pass
    
    @abstractmethod
    async def track_content_licensing_compliance(
        self,
        content_usage_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Track compliance with content licensing terms."""
        pass
    
    @abstractmethod
    async def monitor_financial_compliance(
        self,
        financial_regulations: List[str],
        transaction_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Monitor compliance with financial regulations."""
        pass
    
    @abstractmethod
    async def generate_compliance_report(
        self,
        compliance_framework: str,
        reporting_period: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """Generate compliance report for specified framework."""
        pass
    
    @abstractmethod
    async def implement_compliance_controls(
        self,
        control_requirements: List[Dict[str, Any]]
    ) -> Dict[str, bool]:
        """Implement automated compliance controls."""
        pass
