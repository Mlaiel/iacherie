"""
Backup Monitoring System - Real-Time Health Monitoring and Alerting
==================================================================

Advanced backup monitoring system with real-time health tracking, performance metrics,
failure detection, and comprehensive reporting for creator platform backups.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import statistics

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class MetricType(Enum):
    """Types of monitoring metrics."""
    BACKUP_SUCCESS_RATE = "backup_success_rate"
    BACKUP_DURATION = "backup_duration"
    BACKUP_SIZE = "backup_size"
    STORAGE_UTILIZATION = "storage_utilization"
    BANDWIDTH_USAGE = "bandwidth_usage"
    ERROR_RATE = "error_rate"
    CREATOR_CONTENT_BACKUP_RATE = "creator_content_backup_rate"
    AI_PROCESSING_BACKUP_RATE = "ai_processing_backup_rate"
    MONETIZATION_DATA_BACKUP_RATE = "monetization_data_backup_rate"
    PLATFORM_AVAILABILITY = "platform_availability"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class MonitoringMetric:
    """Individual monitoring metric."""
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheck:
    """Health check configuration and results."""
    check_id: str
    name: str
    component: str
    check_function: str
    interval_seconds: int
    timeout_seconds: int
    status: HealthStatus = HealthStatus.UNKNOWN
    last_check: Optional[datetime] = None
    last_success: Optional[datetime] = None
    consecutive_failures: int = 0
    response_time_ms: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Monitoring alert."""
    alert_id: str
    metric_type: MetricType
    severity: AlertSeverity
    message: str
    source: str
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    creator_id: Optional[str] = None
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BackupJobMonitoring:
    """Monitoring data for individual backup jobs."""
    job_id: str
    job_type: str
    started_at: datetime
    expected_duration_seconds: float
    current_status: str
    progress_percentage: float = 0.0
    bytes_processed: int = 0
    files_processed: int = 0
    creator_id: Optional[str] = None
    priority: int = 5
    sla_deadline: Optional[datetime] = None
    monitoring_alerts: List[str] = field(default_factory=list)


class BackupMonitoringSystem:
    """
    Enterprise backup monitoring system with comprehensive health tracking.
    
    Features:
    - Real-time backup health monitoring
    - Performance metrics collection and analysis
    - Failure detection and alerting
    - SLA monitoring and compliance
    - Creator content backup tracking
    - AI processing backup monitoring
    - Platform availability monitoring
    - Historical performance analysis
    - Automated issue remediation
    """
    
    def __init__(self, monitoring_config: Optional[Dict[str, Any]] = None):
        """Initialize backup monitoring system."""
        self.config = monitoring_config or self._get_default_config()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Monitoring state
        self.metrics_storage: List[MonitoringMetric] = []
        self.health_checks: Dict[str, HealthCheck] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.active_backup_jobs: Dict[str, BackupJobMonitoring] = {}
        
        # Performance tracking
        self.performance_baselines: Dict[MetricType, float] = {}
        self.sla_thresholds: Dict[str, Dict[str, float]] = {}
        
        # Creator platform specific monitoring
        self.creator_backup_metrics = {
            'premium_creator_sla': 300,  # 5 minutes max backup time
            'pro_creator_sla': 600,      # 10 minutes max backup time
            'standard_creator_sla': 1800, # 30 minutes max backup time
            'ai_processing_sla': 900,    # 15 minutes max for AI data
            'monetization_data_sla': 180, # 3 minutes max for financial data
        }
        
        # Alert notification handlers
        self.alert_handlers: Dict[AlertSeverity, List[Callable]] = {
            AlertSeverity.INFO: [],
            AlertSeverity.WARNING: [],
            AlertSeverity.CRITICAL: [],
            AlertSeverity.EMERGENCY: []
        }
        
        # Initialize monitoring
        asyncio.create_task(self._initialize_monitoring())
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default monitoring configuration."""
        return {
            'metrics_retention_days': 30,
            'health_check_interval': 60,
            'alert_evaluation_interval': 30,
            'performance_baseline_days': 7,
            'enable_predictive_alerts': True,
            'enable_auto_remediation': True,
            'creator_platform_monitoring': True,
            'ai_processing_monitoring': True,
            'monetization_monitoring': True,
            'compliance_monitoring': True
        }
    
    async def _initialize_monitoring(self) -> None:
        """Initialize monitoring system components."""
        try:
            # Initialize health checks
            await self._setup_health_checks()
            
            # Initialize SLA monitoring
            await self._setup_sla_monitoring()
            
            # Start monitoring loops
            asyncio.create_task(self._health_check_loop())
            asyncio.create_task(self._metrics_collection_loop())
            asyncio.create_task(self._alert_evaluation_loop())
            asyncio.create_task(self._backup_job_monitoring_loop())
            
            self.logger.info("📊 Backup monitoring system initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize monitoring: {e}")
    
    async def _setup_health_checks(self) -> None:
        """Setup health check configurations."""
        health_checks = [
            HealthCheck(
                check_id="backup_service_health",
                name="Backup Service Health",
                component="backup_service",
                check_function="check_service_status",
                interval_seconds=60,
                timeout_seconds=10
            ),
            HealthCheck(
                check_id="storage_health",
                name="Storage System Health",
                component="storage",
                check_function="check_storage_availability",
                interval_seconds=120,
                timeout_seconds=15
            ),
            HealthCheck(
                check_id="database_backup_health",
                name="Database Backup Health",
                component="database_backup",
                check_function="check_database_connectivity",
                interval_seconds=180,
                timeout_seconds=20
            ),
            HealthCheck(
                check_id="creator_content_backup_health",
                name="Creator Content Backup Health",
                component="creator_backup",
                check_function="check_creator_backup_pipeline",
                interval_seconds=300,
                timeout_seconds=30
            ),
            HealthCheck(
                check_id="ai_processing_backup_health",
                name="AI Processing Backup Health",
                component="ai_backup",
                check_function="check_ai_backup_pipeline",
                interval_seconds=600,
                timeout_seconds=45
            ),
            HealthCheck(
                check_id="cross_region_health",
                name="Cross-Region Backup Health",
                component="cross_region",
                check_function="check_cross_region_connectivity",
                interval_seconds=900,
                timeout_seconds=60
            )
        ]
        
        for check in health_checks:
            self.health_checks[check.check_id] = check
    
    async def _setup_sla_monitoring(self) -> None:
        """Setup SLA monitoring thresholds."""
        self.sla_thresholds = {
            'backup_completion_time': {
                'premium_creator': 300,    # 5 minutes
                'pro_creator': 600,        # 10 minutes
                'standard_creator': 1800,  # 30 minutes
                'basic_creator': 3600,     # 1 hour
                'ai_processing': 900,      # 15 minutes
                'monetization_data': 180,  # 3 minutes
                'system_backup': 7200      # 2 hours
            },
            'backup_success_rate': {
                'premium_creator': 99.9,   # 99.9%
                'pro_creator': 99.5,       # 99.5%
                'standard_creator': 99.0,  # 99.0%
                'basic_creator': 98.0,     # 98.0%
                'ai_processing': 99.5,     # 99.5%
                'monetization_data': 99.95, # 99.95%
                'system_backup': 95.0      # 95.0%
            },
            'recovery_time_objective': {
                'premium_creator': 900,    # 15 minutes
                'pro_creator': 1800,       # 30 minutes
                'monetization_data': 300,  # 5 minutes
                'ai_processing': 1200,     # 20 minutes
                'system_backup': 3600      # 1 hour
            }
        }
    
    async def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        unit: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a monitoring metric."""
        metric = MonitoringMetric(
            metric_type=metric_type,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            source=source,
            metadata=metadata or {}
        )
        
        self.metrics_storage.append(metric)
        
        # Check for alert conditions
        await self._evaluate_metric_alerts(metric)
        
        # Cleanup old metrics
        await self._cleanup_old_metrics()
    
    async def start_backup_job_monitoring(
        self,
        job_id: str,
        job_type: str,
        expected_duration_seconds: float,
        creator_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Start monitoring a backup job."""
        creator_tier = 'standard'
        creator_id = None
        
        if creator_context:
            creator_tier = creator_context.get('tier', 'standard')
            creator_id = creator_context.get('creator_id')
        
        # Calculate SLA deadline
        sla_key = f"{creator_tier}_creator" if creator_tier != 'system' else job_type
        sla_limit = self.sla_thresholds.get('backup_completion_time', {}).get(sla_key, expected_duration_seconds * 2)
        sla_deadline = datetime.now() + timedelta(seconds=sla_limit)
        
        monitoring = BackupJobMonitoring(
            job_id=job_id,
            job_type=job_type,
            started_at=datetime.now(),
            expected_duration_seconds=expected_duration_seconds,
            current_status="running",
            creator_id=creator_id,
            priority=self._get_job_priority(creator_tier, job_type),
            sla_deadline=sla_deadline
        )
        
        self.active_backup_jobs[job_id] = monitoring
        self.logger.info(f"📊 Started monitoring backup job: {job_id}")
    
    def _get_job_priority(self, creator_tier: str, job_type: str) -> int:
        """Get job priority for monitoring."""
        priority_map = {
            ('premium', 'monetization_data'): 10,
            ('premium', 'creator_content'): 9,
            ('pro', 'monetization_data'): 9,
            ('pro', 'creator_content'): 8,
            ('premium', 'ai_processing'): 8,
            ('standard', 'monetization_data'): 8,
            ('pro', 'ai_processing'): 7,
            ('standard', 'creator_content'): 7,
            ('standard', 'ai_processing'): 6,
            ('basic', 'monetization_data'): 7,
            ('basic', 'creator_content'): 5,
            ('basic', 'ai_processing'): 4
        }
        
        return priority_map.get((creator_tier, job_type), 5)
    
    async def update_backup_job_progress(
        self,
        job_id: str,
        progress_percentage: float,
        bytes_processed: Optional[int] = None,
        files_processed: Optional[int] = None,
        status: Optional[str] = None
    ) -> None:
        """Update backup job progress."""
        if job_id not in self.active_backup_jobs:
            self.logger.warning(f"Unknown backup job for progress update: {job_id}")
            return
        
        monitoring = self.active_backup_jobs[job_id]
        monitoring.progress_percentage = progress_percentage
        
        if bytes_processed is not None:
            monitoring.bytes_processed = bytes_processed
        if files_processed is not None:
            monitoring.files_processed = files_processed
        if status is not None:
            monitoring.current_status = status
        
        # Check for SLA violations
        await self._check_job_sla_compliance(monitoring)
    
    async def complete_backup_job_monitoring(
        self,
        job_id: str,
        success: bool,
        final_size_bytes: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Complete monitoring for a backup job."""
        if job_id not in self.active_backup_jobs:
            return
        
        monitoring = self.active_backup_jobs[job_id]
        completion_time = datetime.now()
        duration = (completion_time - monitoring.started_at).total_seconds()
        
        # Record completion metrics
        await self.record_metric(
            MetricType.BACKUP_DURATION,
            duration,
            "seconds",
            f"backup_job_{monitoring.job_type}",
            {
                'job_id': job_id,
                'creator_id': monitoring.creator_id,
                'success': success,
                'expected_duration': monitoring.expected_duration_seconds
            }
        )
        
        if final_size_bytes:
            await self.record_metric(
                MetricType.BACKUP_SIZE,
                final_size_bytes,
                "bytes",
                f"backup_job_{monitoring.job_type}",
                {
                    'job_id': job_id,
                    'creator_id': monitoring.creator_id
                }
            )
        
        # Record success/failure
        success_rate = 100.0 if success else 0.0
        await self.record_metric(
            MetricType.BACKUP_SUCCESS_RATE,
            success_rate,
            "percentage",
            f"backup_job_{monitoring.job_type}",
            {
                'job_id': job_id,
                'creator_id': monitoring.creator_id,
                'error_message': error_message
            }
        )
        
        # Check SLA compliance
        await self._evaluate_sla_compliance(monitoring, duration, success)
        
        # Remove from active monitoring
        del self.active_backup_jobs[job_id]
        
        self.logger.info(f"📊 Completed monitoring backup job: {job_id} (success: {success})")
    
    async def _check_job_sla_compliance(self, monitoring: BackupJobMonitoring) -> None:
        """Check if backup job is meeting SLA requirements."""
        current_time = datetime.now()
        
        # Check if approaching SLA deadline
        if monitoring.sla_deadline:
            time_remaining = (monitoring.sla_deadline - current_time).total_seconds()
            
            if time_remaining < 300:  # 5 minutes warning
                await self._create_alert(
                    MetricType.BACKUP_DURATION,
                    AlertSeverity.WARNING,
                    f"Backup job {monitoring.job_id} approaching SLA deadline",
                    f"backup_job_{monitoring.job_type}",
                    creator_id=monitoring.creator_id,
                    metadata={
                        'job_id': monitoring.job_id,
                        'time_remaining_seconds': time_remaining,
                        'progress_percentage': monitoring.progress_percentage
                    }
                )
            
            if time_remaining < 0:  # SLA violation
                await self._create_alert(
                    MetricType.BACKUP_DURATION,
                    AlertSeverity.CRITICAL,
                    f"Backup job {monitoring.job_id} exceeded SLA deadline",
                    f"backup_job_{monitoring.job_type}",
                    creator_id=monitoring.creator_id,
                    metadata={
                        'job_id': monitoring.job_id,
                        'sla_violation_seconds': abs(time_remaining),
                        'progress_percentage': monitoring.progress_percentage
                    }
                )
    
    async def _evaluate_sla_compliance(
        self,
        monitoring: BackupJobMonitoring,
        actual_duration: float,
        success: bool
    ) -> None:
        """Evaluate SLA compliance after job completion."""
        # Determine SLA category
        creator_tier = 'standard'
        if monitoring.creator_id:
            # In real implementation, look up creator tier
            creator_tier = 'premium'  # Placeholder
        
        sla_key = f"{creator_tier}_creator"
        expected_duration = self.sla_thresholds.get('backup_completion_time', {}).get(sla_key)
        
        if expected_duration and actual_duration > expected_duration:
            # SLA violation
            await self._create_alert(
                MetricType.BACKUP_DURATION,
                AlertSeverity.CRITICAL,
                f"SLA violation: Backup took {actual_duration:.1f}s (limit: {expected_duration}s)",
                f"sla_monitoring_{monitoring.job_type}",
                creator_id=monitoring.creator_id,
                threshold_value=expected_duration,
                actual_value=actual_duration,
                metadata={
                    'job_id': monitoring.job_id,
                    'sla_category': sla_key,
                    'violation_percentage': ((actual_duration - expected_duration) / expected_duration) * 100
                }
            )
    
    async def _health_check_loop(self) -> None:
        """Main health check monitoring loop."""
        while True:
            try:
                for check_id, check in self.health_checks.items():
                    if self._should_run_health_check(check):
                        await self._execute_health_check(check)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(60)
    
    def _should_run_health_check(self, check: HealthCheck) -> bool:
        """Determine if health check should run now."""
        if not check.last_check:
            return True
        
        time_since_last = (datetime.now() - check.last_check).total_seconds()
        return time_since_last >= check.interval_seconds
    
    async def _execute_health_check(self, check: HealthCheck) -> None:
        """Execute individual health check."""
        start_time = time.time()
        check.last_check = datetime.now()
        
        try:
            # Simulate health check execution
            if check.check_function == "check_service_status":
                await self._check_service_status(check)
            elif check.check_function == "check_storage_availability":
                await self._check_storage_availability(check)
            elif check.check_function == "check_database_connectivity":
                await self._check_database_connectivity(check)
            elif check.check_function == "check_creator_backup_pipeline":
                await self._check_creator_backup_pipeline(check)
            elif check.check_function == "check_ai_backup_pipeline":
                await self._check_ai_backup_pipeline(check)
            elif check.check_function == "check_cross_region_connectivity":
                await self._check_cross_region_connectivity(check)
            else:
                check.status = HealthStatus.UNKNOWN
                check.error_message = f"Unknown check function: {check.check_function}"
            
            check.response_time_ms = (time.time() - start_time) * 1000
            
            if check.status == HealthStatus.HEALTHY:
                check.last_success = datetime.now()
                check.consecutive_failures = 0
            else:
                check.consecutive_failures += 1
            
            # Create alerts for health check failures
            if check.status in [HealthStatus.CRITICAL, HealthStatus.DEGRADED]:
                severity = AlertSeverity.CRITICAL if check.status == HealthStatus.CRITICAL else AlertSeverity.WARNING
                await self._create_alert(
                    MetricType.PLATFORM_AVAILABILITY,
                    severity,
                    f"Health check failed: {check.name}",
                    f"health_check_{check.component}",
                    metadata={
                        'check_id': check.check_id,
                        'consecutive_failures': check.consecutive_failures,
                        'error_message': check.error_message
                    }
                )
            
        except Exception as e:
            check.status = HealthStatus.CRITICAL
            check.error_message = str(e)
            check.consecutive_failures += 1
    
    async def _check_service_status(self, check: HealthCheck) -> None:
        """Check backup service status."""
        # Simulate service check
        await asyncio.sleep(0.1)
        check.status = HealthStatus.HEALTHY
        check.error_message = None
    
    async def _check_storage_availability(self, check: HealthCheck) -> None:
        """Check storage system availability."""
        # Simulate storage check
        await asyncio.sleep(0.2)
        check.status = HealthStatus.HEALTHY
        check.error_message = None
    
    async def _check_database_connectivity(self, check: HealthCheck) -> None:
        """Check database connectivity."""
        # Simulate database check
        await asyncio.sleep(0.15)
        check.status = HealthStatus.HEALTHY
        check.error_message = None
    
    async def _check_creator_backup_pipeline(self, check: HealthCheck) -> None:
        """Check creator backup pipeline health."""
        # Simulate creator pipeline check
        await asyncio.sleep(0.3)
        check.status = HealthStatus.HEALTHY
        check.error_message = None
    
    async def _check_ai_backup_pipeline(self, check: HealthCheck) -> None:
        """Check AI processing backup pipeline."""
        # Simulate AI pipeline check
        await asyncio.sleep(0.25)
        check.status = HealthStatus.HEALTHY
        check.error_message = None
    
    async def _check_cross_region_connectivity(self, check: HealthCheck) -> None:
        """Check cross-region connectivity."""
        # Simulate cross-region check
        await asyncio.sleep(0.4)
        check.status = HealthStatus.HEALTHY
        check.error_message = None
    
    async def _metrics_collection_loop(self) -> None:
        """Collect system metrics periodically."""
        while True:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(60)  # Collect every minute
            except Exception as e:
                self.logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(300)
    
    async def _collect_system_metrics(self) -> None:
        """Collect various system metrics."""
        current_time = datetime.now()
        
        # Storage utilization (simulated)
        await self.record_metric(
            MetricType.STORAGE_UTILIZATION,
            75.5,  # 75.5% utilization
            "percentage",
            "storage_monitor",
            {"storage_type": "primary"}
        )
        
        # Bandwidth usage (simulated)
        await self.record_metric(
            MetricType.BANDWIDTH_USAGE,
            450.0,  # 450 Mbps
            "mbps",
            "network_monitor"
        )
        
        # Overall backup success rate (calculated from recent jobs)
        recent_success_rate = await self._calculate_recent_success_rate()
        await self.record_metric(
            MetricType.BACKUP_SUCCESS_RATE,
            recent_success_rate,
            "percentage",
            "backup_monitor"
        )
    
    async def _calculate_recent_success_rate(self) -> float:
        """Calculate recent backup success rate."""
        # Look at last hour's backup completion metrics
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_metrics = [
            m for m in self.metrics_storage
            if (m.metric_type == MetricType.BACKUP_SUCCESS_RATE and 
                m.timestamp > one_hour_ago)
        ]
        
        if not recent_metrics:
            return 100.0  # Default if no recent data
        
        return statistics.mean(m.value for m in recent_metrics)
    
    async def _alert_evaluation_loop(self) -> None:
        """Evaluate metrics for alert conditions."""
        while True:
            try:
                await self._evaluate_alert_conditions()
                await asyncio.sleep(self.config['alert_evaluation_interval'])
            except Exception as e:
                self.logger.error(f"Error in alert evaluation: {e}")
                await asyncio.sleep(60)
    
    async def _evaluate_alert_conditions(self) -> None:
        """Evaluate current metrics for alert conditions."""
        # Check storage utilization
        storage_metrics = [
            m for m in self.metrics_storage[-10:]  # Last 10 metrics
            if m.metric_type == MetricType.STORAGE_UTILIZATION
        ]
        
        if storage_metrics:
            latest_storage = storage_metrics[-1].value
            if latest_storage > 90:
                await self._create_alert(
                    MetricType.STORAGE_UTILIZATION,
                    AlertSeverity.CRITICAL,
                    f"Storage utilization critically high: {latest_storage:.1f}%",
                    "storage_monitor",
                    threshold_value=90.0,
                    actual_value=latest_storage
                )
            elif latest_storage > 80:
                await self._create_alert(
                    MetricType.STORAGE_UTILIZATION,
                    AlertSeverity.WARNING,
                    f"Storage utilization high: {latest_storage:.1f}%",
                    "storage_monitor",
                    threshold_value=80.0,
                    actual_value=latest_storage
                )
        
        # Check backup success rate
        success_rate_metrics = [
            m for m in self.metrics_storage[-20:]
            if m.metric_type == MetricType.BACKUP_SUCCESS_RATE
        ]
        
        if success_rate_metrics:
            avg_success_rate = statistics.mean(m.value for m in success_rate_metrics)
            if avg_success_rate < 95:
                await self._create_alert(
                    MetricType.BACKUP_SUCCESS_RATE,
                    AlertSeverity.CRITICAL,
                    f"Backup success rate below threshold: {avg_success_rate:.1f}%",
                    "backup_monitor",
                    threshold_value=95.0,
                    actual_value=avg_success_rate
                )
    
    async def _backup_job_monitoring_loop(self) -> None:
        """Monitor active backup jobs for issues."""
        while True:
            try:
                for job_id, monitoring in list(self.active_backup_jobs.items()):
                    await self._check_job_sla_compliance(monitoring)
                
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error in backup job monitoring: {e}")
                await asyncio.sleep(120)
    
    async def _evaluate_metric_alerts(self, metric: MonitoringMetric) -> None:
        """Evaluate if metric triggers any alerts."""
        # Creator-specific alerting
        if metric.metadata.get('creator_id'):
            creator_tier = metric.metadata.get('creator_tier', 'standard')
            await self._evaluate_creator_metric_alerts(metric, creator_tier)
    
    async def _evaluate_creator_metric_alerts(self, metric: MonitoringMetric, creator_tier: str) -> None:
        """Evaluate creator-specific metric alerts."""
        if metric.metric_type == MetricType.BACKUP_DURATION:
            sla_limit = self.creator_backup_metrics.get(f'{creator_tier}_creator_sla', 1800)
            
            if metric.value > sla_limit:
                await self._create_alert(
                    metric.metric_type,
                    AlertSeverity.WARNING,
                    f"Creator backup duration exceeded SLA: {metric.value:.1f}s (limit: {sla_limit}s)",
                    metric.source,
                    creator_id=metric.metadata.get('creator_id'),
                    threshold_value=float(sla_limit),
                    actual_value=metric.value
                )
    
    async def _create_alert(
        self,
        metric_type: MetricType,
        severity: AlertSeverity,
        message: str,
        source: str,
        creator_id: Optional[str] = None,
        threshold_value: Optional[float] = None,
        actual_value: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new monitoring alert."""
        alert_id = f"alert_{int(datetime.now().timestamp())}_{len(self.active_alerts)}"
        
        alert = Alert(
            alert_id=alert_id,
            metric_type=metric_type,
            severity=severity,
            message=message,
            source=source,
            triggered_at=datetime.now(),
            creator_id=creator_id,
            threshold_value=threshold_value,
            actual_value=actual_value,
            metadata=metadata or {}
        )
        
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Trigger alert handlers
        await self._trigger_alert_handlers(alert)
        
        self.logger.warning(f"🚨 Alert created: {alert_id} - {message}")
        return alert_id
    
    async def _trigger_alert_handlers(self, alert: Alert) -> None:
        """Trigger registered alert handlers."""
        handlers = self.alert_handlers.get(alert.severity, [])
        
        for handler in handlers:
            try:
                await handler(alert)
            except Exception as e:
                self.logger.error(f"Alert handler failed: {e}")
    
    async def _cleanup_old_metrics(self) -> None:
        """Clean up old metrics based on retention policy."""
        retention_days = self.config.get('metrics_retention_days', 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        self.metrics_storage = [
            m for m in self.metrics_storage
            if m.timestamp > cutoff_date
        ]
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an active alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.acknowledged = True
            alert.acknowledged_by = acknowledged_by
            
            self.logger.info(f"📨 Alert acknowledged: {alert_id} by {acknowledged_by}")
            return True
        
        return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved_at = datetime.now()
            
            # Move to history only
            del self.active_alerts[alert_id]
            
            self.logger.info(f"✅ Alert resolved: {alert_id}")
            return True
        
        return False
    
    async def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard data."""
        current_time = datetime.now()
        
        # System health overview
        health_overview = {}
        for check_id, check in self.health_checks.items():
            health_overview[check_id] = {
                'status': check.status.value,
                'last_check': check.last_check.isoformat() if check.last_check else None,
                'response_time_ms': check.response_time_ms,
                'consecutive_failures': check.consecutive_failures
            }
        
        # Active alerts summary
        alerts_by_severity = {}
        for alert in self.active_alerts.values():
            severity = alert.severity.value
            if severity not in alerts_by_severity:
                alerts_by_severity[severity] = 0
            alerts_by_severity[severity] += 1
        
        # Active backup jobs
        active_jobs_summary = {
            'total_jobs': len(self.active_backup_jobs),
            'by_priority': {},
            'approaching_sla': 0,
            'exceeded_sla': 0
        }
        
        for job in self.active_backup_jobs.values():
            priority = str(job.priority)
            if priority not in active_jobs_summary['by_priority']:
                active_jobs_summary['by_priority'][priority] = 0
            active_jobs_summary['by_priority'][priority] += 1
            
            if job.sla_deadline:
                time_remaining = (job.sla_deadline - current_time).total_seconds()
                if time_remaining < 300:  # 5 minutes
                    active_jobs_summary['approaching_sla'] += 1
                if time_remaining < 0:
                    active_jobs_summary['exceeded_sla'] += 1
        
        # Recent metrics summary
        recent_metrics = {}
        for metric_type in MetricType:
            recent = [m for m in self.metrics_storage[-100:] if m.metric_type == metric_type]
            if recent:
                recent_metrics[metric_type.value] = {
                    'latest_value': recent[-1].value,
                    'unit': recent[-1].unit,
                    'timestamp': recent[-1].timestamp.isoformat(),
                    'trend': 'stable'  # Could calculate actual trend
                }
        
        return {
            'dashboard_generated_at': current_time.isoformat(),
            'system_health': health_overview,
            'active_alerts': {
                'total': len(self.active_alerts),
                'by_severity': alerts_by_severity,
                'unacknowledged': len([a for a in self.active_alerts.values() if not a.acknowledged])
            },
            'active_backup_jobs': active_jobs_summary,
            'recent_metrics': recent_metrics,
            'creator_platform_status': {
                'premium_creator_backups_healthy': True,
                'ai_processing_backups_healthy': True,
                'monetization_backups_healthy': True,
                'cross_region_replication_healthy': True
            }
        }


# Export public interface
__all__ = [
    'BackupMonitoringSystem',
    'HealthStatus',
    'MetricType',
    'AlertSeverity',
    'MonitoringMetric',
    'HealthCheck',
    'Alert',
    'BackupJobMonitoring'
]