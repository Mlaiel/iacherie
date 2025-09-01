"""📊 Monitoring Service - IA-Influencer-Agent  
==================================================================
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
==================================================================

⚠️  COPYRIGHT NOTICE & LEGAL WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copy, distribution, or modification of this code
without explicit written permission is strictly prohibited and will be
prosecuted to the full extent of the law.

Advanced real-time monitoring system for content protection.
Provides comprehensive surveillance, alerting, and analytics
for multi-platform content piracy detection.
"""

from typing import Dict, List, Optional, Any, Union, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from datetime import datetime, timezone, timedelta
import asyncio
import logging
import json
import uuid
import time
from pathlib import Path
import statistics

# Monitoring and alerting imports
import smtplib
import aiohttp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

logger = logging.getLogger(__name__)

# =============== ENUMS & CONFIGURATION ===============

class MonitoringStatus(Enum):
    """
Monitoring service operational status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    MONITORING = "monitoring"
    ALERTING = "alerting"
    PROCESSING = "processing"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class AlertSeverity(IntEnum):
    """Alert severity levels"""

    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5
    EMERGENCY = 6

class AlertType(Enum):
    """
Types of alerts"""

    PIRACY_DETECTED = "piracy_detected"
    HIGH_SIMILARITY_MATCH = "high_similarity_match"
    MASSIVE_INFRINGEMENT = "massive_infringement"
    PLATFORM_UNAVAILABLE = "platform_unavailable"
    SYSTEM_ERROR = "system_error"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    REVENUE_LOSS = "revenue_loss"
    TAKEDOWN_SUCCESS = "takedown_success"
    TAKEDOWN_FAILURE = "takedown_failure"

class NotificationChannel(Enum):
    """Notification delivery channels"""

    EMAIL = "email"
    WEBHOOK = "webhook"
    SMS = "sms"
    SLACK = "slack"
    DISCORD = "discord"
    PUSH_NOTIFICATION = "push_notification"
    DASHBOARD = "dashboard"

class MetricType(Enum):
    """Types of monitoring metrics"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"

@dataclass
class MonitoringConfig:
    """Configuration for monitoring service"""
    enabled: bool = True
    check_interval_seconds: int = 60
    alert_batch_size: int = 100
    max_concurrent_checks: int = 50
    retention_days: int = 30
    email_enabled: bool = True
    webhook_enabled: bool = True
    dashboard_enabled: bool = True
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    webhook_urls: List[str] = field(default_factory=list)
    notification_channels: List[NotificationChannel] = field(default_factory=list)
    alert_thresholds: Dict[str, float] = field(default_factory=dict)

@dataclass
class Alert:
    """Monitoring alert with comprehensive details"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: AlertType = AlertType.PIRACY_DETECTED
    severity: AlertSeverity = AlertSeverity.MEDIUM
    title: str = ""
    message: str = ""
    source_platform: str = ""
    affected_content_id: str = ""
    detection_data: Dict[str, Any] = field(default_factory=dict)
    evidence_urls: List[str] = field(default_factory=list)
    screenshot_urls: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    assignee: Optional[str] = None
    status: str = "open"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MonitoringMetrics:
    """System monitoring metrics"""
    metrics_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Performance metrics
    total_scans_today: int = 0
    successful_scans: int = 0
    failed_scans: int = 0
    average_scan_time_ms: float = 0.0
    
    # Detection metrics
    total_violations_detected: int = 0
    high_severity_violations: int = 0
    new_violations_today: int = 0
    resolved_violations_today: int = 0
    
    # Platform metrics
    platform_availability: Dict[str, float] = field(default_factory=dict)
    platform_response_times: Dict[str, float] = field(default_factory=dict)
    
    # System metrics
    cpu_usage_percent: float = 0.0
    memory_usage_percent: float = 0.0
    disk_usage_percent: float = 0.0
    network_latency_ms: float = 0.0
    
    # Alert metrics
    total_alerts_sent: int = 0
    critical_alerts_active: int = 0
    alert_response_time_minutes: float = 0.0

# =============== CORE INTERFACES ===============

class IMonitoringService(ABC):
    """
Interface for monitoring service"""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
Initialize monitoring service"""
        pass
    
    @abstractmethod
    async def send_alert(self, alert: Alert) -> bool:
        """
Send alert through configured channels"""
        pass
    
    @abstractmethod
    async def collect_metrics(self) -> MonitoringMetrics:
        """
Collect current system metrics"""
        pass
    
    @abstractmethod
    async def check_system_health(self) -> Dict[str, Any]:
        """
Perform comprehensive system health check"""
        pass

# =============== ALERT MANAGEMENT SYSTEM ===============

class AlertManager:
    """
Advanced alert management and routing system"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.AlertManager")
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.notification_queue: asyncio.Queue = asyncio.Queue()
        
    async def process_alert(self, alert: Alert) -> bool:
        """Process and route alert to appropriate channels"""
        try:
            # Store alert
            self.active_alerts[alert.alert_id] = alert
            self.alert_history.append(alert)
            
            # Determine notification channels based on severity
            channels = self._get_notification_channels(alert.severity)
            
            # Send notifications
            notification_tasks = []
            for channel in channels:
                task = asyncio.create_task(self._send_notification(alert, channel))
                notification_tasks.append(task)
            
            results = await asyncio.gather(*notification_tasks, return_exceptions=True)
            
            success_count = sum(1 for r in results if r is True)
            total_channels = len(channels)
            
            self.logger.info(f"Alert processed: {alert.alert_id} - {success_count}/{total_channels} notifications sent")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Alert processing failed: {e}")
            return False
    
    async def _send_notification(self, alert: Alert, channel: NotificationChannel) -> bool:
        """Send notification through specific channel"""
        try:
            if channel == NotificationChannel.EMAIL:
                return await self._send_email_alert(alert)
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook_alert(alert)
            elif channel == NotificationChannel.SLACK:
                return await self._send_slack_alert(alert)
            elif channel == NotificationChannel.DISCORD:
                return await self._send_discord_alert(alert)
            else:
                self.logger.warning(f"Unsupported notification channel: {channel}")
                return False
                
        except Exception as e:
            self.logger.error(f"Notification failed for {channel}: {e}")
            return False
    
    async def _send_email_alert(self, alert: Alert) -> bool:
        """Send email alert"""
        try:
            if not self.config.email_enabled or not self.config.smtp_username:
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.config.smtp_username
            msg['To'] = self.config.smtp_username  # Send to self for now
            msg['Subject'] = f"[{alert.severity.name}] {alert.title}"
            
            # Create HTML email body
            html_body = self._generate_email_html(alert)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            server.starttls()
            server.login(self.config.smtp_username, self.config.smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Email alert failed: {e}")
            return False
    
    async def _send_webhook_alert(self, alert: Alert) -> bool:
        """Send webhook alert"""
        try:
            if not self.config.webhook_enabled or not self.config.webhook_urls:
                return False
            
            payload = {
                'alert_id': alert.alert_id,
                'type': alert.alert_type.value,
                'severity': alert.severity.name,
                'title': alert.title,
                'message': alert.message,
                'platform': alert.source_platform,
                'content_id': alert.affected_content_id,
                'timestamp': alert.created_at.isoformat(),
                'evidence': alert.evidence_urls,
                'actions': alert.recommended_actions
            }
            
            success_count = 0
            for webhook_url in self.config.webhook_urls:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(webhook_url, json=payload) as response:
                            if response.status < 300:
                                success_count += 1
                except Exception as e:
                    self.logger.error(f"Webhook failed for {webhook_url}: {e}")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Webhook alert failed: {e}")
            return False
    
    async def _send_slack_alert(self, alert: Alert) -> bool:
        """Send Slack alert (placeholder)"""
        try:
            # Slack integration would go here
            return True
            
        except Exception as e:
            self.logger.error(f"Slack alert failed: {e}")
            return False
    
    async def _send_discord_alert(self, alert: Alert) -> bool:
        """Send Discord alert (placeholder)"""
        try:
            # Discord integration would go here
            return True
            
        except Exception as e:
            self.logger.error(f"Discord alert failed: {e}")
            return False
    
    def _get_notification_channels(self, severity: AlertSeverity) -> List[NotificationChannel]:
        """Determine notification channels based on alert severity"""
        channels = []
        
        if severity >= AlertSeverity.CRITICAL:
            channels.extend([
                NotificationChannel.EMAIL,
                NotificationChannel.WEBHOOK,
                NotificationChannel.SMS
            ])
        elif severity >= AlertSeverity.HIGH:
            channels.extend([
                NotificationChannel.EMAIL,
                NotificationChannel.WEBHOOK
            ])
        elif severity >= AlertSeverity.MEDIUM:
            channels.append(NotificationChannel.EMAIL)
        else:
            channels.append(NotificationChannel.DASHBOARD)
        
        # Filter by configured channels
        configured_channels = self.config.notification_channels
        if configured_channels:
            channels = [c for c in channels if c in configured_channels]
        
        return channels
    
    def _generate_email_html(self, alert: Alert) -> str:
        """
Generate HTML email body for alert"""
        severity_color = {
            AlertSeverity.INFO: "#17a2b8",
            AlertSeverity.LOW: "#28a745", 
            AlertSeverity.MEDIUM: "#ffc107",
            AlertSeverity.HIGH: "#fd7e14",
            AlertSeverity.CRITICAL: "#dc3545",
            AlertSeverity.EMERGENCY: "#6f42c1"
        }
        
        color = severity_color.get(alert.severity, "#6c757d")
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="background-color: {color}; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">{alert.title}</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Severity: {alert.severity.name}</p>
                </div>
                
                <div style="padding: 20px;">
                    <h2 style="color: #333; margin-top: 0;">Alert Details</h2>
                    <p><strong>Alert ID:</strong> {alert.alert_id}</p>
                    <p><strong>Type:</strong> {alert.alert_type.value}</p>
                    <p><strong>Platform:</strong> {alert.source_platform}</p>
                    <p><strong>Content ID:</strong> {alert.affected_content_id}</p>
                    <p><strong>Timestamp:</strong> {alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                    
                    <h3 style="color: #333;">Message</h3>
                    <p style="background-color: #f8f9fa; padding: 15px; border-radius: 4px; border-left: 4px solid {color};">
                        {alert.message}
                    </p>
        """
        
        if alert.evidence_urls:
            html += """
                    <h3 style="color: #333;">Evidence</h3>
                    <ul>
            """
            for url in alert.evidence_urls[:5]:  # Limit to 5 URLs
                html += f'<li><a href="{url}" target="_blank">{url}</a></li>'
            html += "</ul>"
        
        if alert.recommended_actions:
            html += """
                    <h3 style="color: #333;">Recommended Actions</h3>
                    <ul>
            """
            for action in alert.recommended_actions:
                html += f"<li>{action}</li>"
            html += "</ul>"
        
        html += """
                </div>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 0 0 8px 8px; text-align: center; color: #6c757d;">
                    <p style="margin: 0;">IA-Influencer-Agent Protection System</p>
                    <p style="margin: 5px 0 0 0; font-size: 12px;">(c) 2025 Fahed Mlaiel - All Rights Reserved</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html

# =============== METRICS COLLECTION SYSTEM ===============

class MetricsCollector:
    """
Advanced metrics collection and analysis system"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.MetricsCollector")
        self.metrics_history: List[MonitoringMetrics] = []
        self.current_metrics = MonitoringMetrics()
        
    async def collect_system_metrics(self) -> MonitoringMetrics:
        """Collect comprehensive system metrics"""
        metrics = MonitoringMetrics()
        
        try:
            # Collect performance metrics
            metrics = await self._collect_performance_metrics(metrics)
            
            # Collect detection metrics
            metrics = await self._collect_detection_metrics(metrics)
            
            # Collect platform metrics
            metrics = await self._collect_platform_metrics(metrics)
            
            # Collect system resource metrics
            metrics = await self._collect_resource_metrics(metrics)
            
            # Store metrics
            self.current_metrics = metrics
            self.metrics_history.append(metrics)
            
            # Cleanup old metrics
            self._cleanup_old_metrics()
            
            self.logger.info(f"Metrics collected: {metrics.total_scans_today} scans, {metrics.total_violations_detected} violations")
            
        except Exception as e:
            self.logger.error(f"Metrics collection failed: {e}")
            
        return metrics
    
    async def _collect_performance_metrics(self, metrics: MonitoringMetrics) -> MonitoringMetrics:
        """Collect performance-related metrics"""
        try:
            # These would be populated from actual system data
            metrics.total_scans_today = self._get_daily_scan_count()
            metrics.successful_scans = self._get_successful_scan_count()
            metrics.failed_scans = self._get_failed_scan_count()
            metrics.average_scan_time_ms = self._calculate_average_scan_time()
            
        except Exception as e:
            self.logger.error(f"Performance metrics collection failed: {e}")
            
        return metrics
    
    async def _collect_detection_metrics(self, metrics: MonitoringMetrics) -> MonitoringMetrics:
        """Collect detection-related metrics"""
        try:
            metrics.total_violations_detected = self._get_total_violations()
            metrics.high_severity_violations = self._get_high_severity_violations()
            metrics.new_violations_today = self._get_new_violations_today()
            metrics.resolved_violations_today = self._get_resolved_violations_today()
            
        except Exception as e:
            self.logger.error(f"Detection metrics collection failed: {e}")
            
        return metrics
    
    async def _collect_platform_metrics(self, metrics: MonitoringMetrics) -> MonitoringMetrics:
        """Collect platform-specific metrics"""
        try:
            platforms = ['youtube', 'instagram', 'tiktok', 'spotify']
            
            for platform in platforms:
                # Simulate platform availability check
                availability = await self._check_platform_availability(platform)
                response_time = await self._check_platform_response_time(platform)
                
                metrics.platform_availability[platform] = availability
                metrics.platform_response_times[platform] = response_time
                
        except Exception as e:
            self.logger.error(f"Platform metrics collection failed: {e}")
            
        return metrics
    
    async def _collect_resource_metrics(self, metrics: MonitoringMetrics) -> MonitoringMetrics:
        """Collect system resource metrics"""
        try:
            import psutil
            
            metrics.cpu_usage_percent = psutil.cpu_percent(interval=1)
            metrics.memory_usage_percent = psutil.virtual_memory().percent
            metrics.disk_usage_percent = psutil.disk_usage('/').percent
            
            # Network latency (simplified)
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get('https://www.google.com', timeout=aiohttp.ClientTimeout(total=5)) as response:
                    metrics.network_latency_ms = (time.time() - start_time) * 1000
                    
        except Exception as e:
            self.logger.error(f"Resource metrics collection failed: {e}")
            # Set default values if collection fails
            metrics.cpu_usage_percent = 0.0
            metrics.memory_usage_percent = 0.0
            metrics.disk_usage_percent = 0.0
            metrics.network_latency_ms = 0.0
            
        return metrics
    
    async def _check_platform_availability(self, platform: str) -> float:
        """Check platform availability"""
        try:
            platform_urls = {
                'youtube': 'https://www.youtube.com',
                'instagram': 'https://www.instagram.com',
                'tiktok': 'https://www.tiktok.com',
                'spotify': 'https://www.spotify.com'
            }
            
            url = platform_urls.get(platform)
            if not url:
                return 0.0
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    return 1.0 if response.status < 400 else 0.0
                    
        except Exception:
            return 0.0
    
    async def _check_platform_response_time(self, platform: str) -> float:
        """
Check platform response time"""
        try:
            platform_urls = {
                'youtube': 'https://www.youtube.com',
                'instagram': 'https://www.instagram.com',
                'tiktok': 'https://www.tiktok.com',
                'spotify': 'https://www.spotify.com'
            }
            
            url = platform_urls.get(platform)
            if not url:
                return 0.0
            
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    return (time.time() - start_time) * 1000
                    
        except Exception:
            return 0.0
    
    def _get_daily_scan_count(self) -> int:
        """
Get daily scan count (placeholder)"""
        return 150  # Mock data
    
    def _get_successful_scan_count(self) -> int:
        """
Get successful scan count (placeholder)"""
        return 142  # Mock data
    
    def _get_failed_scan_count(self) -> int:
        """
Get failed scan count (placeholder)"""
        return 8  # Mock data
    
    def _calculate_average_scan_time(self) -> float:
        """
Calculate average scan time (placeholder)"""
        return 2500.0  # Mock data in milliseconds
    
    def _get_total_violations(self) -> int:
        """
Get total violations detected (placeholder)"""
        return 23  # Mock data
    
    def _get_high_severity_violations(self) -> int:
        """
Get high severity violations (placeholder)"""
        return 5  # Mock data
    
    def _get_new_violations_today(self) -> int:
        """
Get new violations today (placeholder)"""
        return 7  # Mock data
    
    def _get_resolved_violations_today(self) -> int:
        """
Get resolved violations today (placeholder)"""
        return 12  # Mock data
    
    def _cleanup_old_metrics(self) -> None:
        """
Remove old metrics beyond retention period"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.config.retention_days)
        self.metrics_history = [m for m in self.metrics_history if m.timestamp > cutoff_date]

# =============== MAIN SERVICE IMPLEMENTATION ===============

class MonitoringService(IMonitoringService):
    """
Professional monitoring service implementation"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.status = MonitoringStatus.INACTIVE
        self.logger = logging.getLogger(f"{__name__}.Service")
        
        # Initialize components
        self.alert_manager = AlertManager(config)
        self.metrics_collector = MetricsCollector(config)
        
        # Monitoring tasks
        self.monitoring_task: Optional[asyncio.Task] = None
        self.health_check_task: Optional[asyncio.Task] = None
        
    async def initialize(self) -> bool:
        """Initialize monitoring service"""
        try:
            self.logger.info("🚀 Initializing Monitoring Service")
            
            # Start background monitoring tasks
            await self._start_monitoring_tasks()
            
            self.status = MonitoringStatus.ACTIVE
            self.logger.info("✅ Monitoring Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Monitoring Service initialization failed: {e}")
            self.status = MonitoringStatus.ERROR
            return False
    
    async def send_alert(self, alert: Alert) -> bool:
        """Send alert through configured channels"""
        try:
            self.status = MonitoringStatus.ALERTING
            
            success = await self.alert_manager.process_alert(alert)
            
            self.status = MonitoringStatus.ACTIVE
            return success
            
        except Exception as e:
            self.logger.error(f"Alert sending failed: {e}")
            self.status = MonitoringStatus.ERROR
            return False
    
    async def collect_metrics(self) -> MonitoringMetrics:
        """Collect current system metrics"""
        try:
            metrics = await self.metrics_collector.collect_system_metrics()
            return metrics
            
        except Exception as e:
            self.logger.error(f"Metrics collection failed: {e}")
            return MonitoringMetrics()
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        health_status = {
            'overall_status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'components': {},
            'alerts': [],
            'metrics': {}
        }
        
        try:
            # Check individual components
            components = {
                'anti_piracy_engine': await self._check_component_health('anti_piracy_engine'),
                'fingerprinting_engine': await self._check_component_health('fingerprinting_engine'),
                'crawler_manager': await self._check_component_health('crawler_manager'),
                'database': await self._check_component_health('database'),
                'cache': await self._check_component_health('cache')
            }
            
            health_status['components'] = components
            
            # Determine overall health
            unhealthy_components = [name for name, status in components.items() if not status['healthy']]
            if unhealthy_components:
                health_status['overall_status'] = 'degraded' if len(unhealthy_components) < 3 else 'unhealthy'
                health_status['issues'] = unhealthy_components
            
            # Collect current metrics
            metrics = await self.collect_metrics()
            health_status['metrics'] = {
                'total_scans_today': metrics.total_scans_today,
                'violations_detected': metrics.total_violations_detected,
                'system_performance': {
                    'cpu_usage': metrics.cpu_usage_percent,
                    'memory_usage': metrics.memory_usage_percent,
                    'disk_usage': metrics.disk_usage_percent
                }
            }
            
            # Check for active critical alerts
            critical_alerts = [alert for alert in self.alert_manager.active_alerts.values() 
                             if alert.severity >= AlertSeverity.HIGH and alert.status == 'open']
            health_status['active_critical_alerts'] = len(critical_alerts)
            
        except Exception as e:
            self.logger.error(f"System health check failed: {e}")
            health_status['overall_status'] = 'error'
            health_status['error'] = str(e)
            
        return health_status

    # =============== PRIVATE HELPER METHODS ===============
    
    async def _start_monitoring_tasks(self) -> None:
        """Start background monitoring tasks"""
        # Start periodic monitoring
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        # Start health check task
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        self.logger.info("Background monitoring tasks started")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.status != MonitoringStatus.INACTIVE:
            try:
                # Collect metrics
                metrics = await self.collect_metrics()
                
                # Check for alert conditions
                await self._check_alert_conditions(metrics)
                
                # Wait for next check
                await asyncio.sleep(self.config.check_interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _health_check_loop(self) -> None:
        """Periodic health check loop"""
        while self.status != MonitoringStatus.INACTIVE:
            try:
                health = await self.check_system_health()
                
                if health['overall_status'] != 'healthy':
                    # Send health alert
                    alert = Alert(
                        alert_type=AlertType.SYSTEM_ERROR,
                        severity=AlertSeverity.HIGH,
                        title="System Health Degraded",
                        message=f"System health status: {health['overall_status']}",
                        detection_data=health
                    )
                    await self.send_alert(alert)
                
                # Health checks every 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                self.logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(300)
    
    async def _check_component_health(self, component_name: str) -> Dict[str, Any]:
        """Check health of individual component"""
        health_info = {
            'healthy': True,
            'status': 'operational',
            'last_check': datetime.now(timezone.utc).isoformat(),
            'response_time_ms': 0.0
        }
        
        try:
            start_time = time.time()
            
            # Component-specific health checks would go here
            if component_name == 'database':
                # Database connectivity check
                health_info['healthy'] = True  # Placeholder
            elif component_name == 'cache':
                # Cache connectivity check
                health_info['healthy'] = True  # Placeholder
            else:
                # Generic service health check
                health_info['healthy'] = True  # Placeholder
            
            health_info['response_time_ms'] = (time.time() - start_time) * 1000
            
        except Exception as e:
            health_info.update({
                'healthy': False,
                'status': 'error',
                'error': str(e)
            })
            
        return health_info
    
    async def _check_alert_conditions(self, metrics: MonitoringMetrics) -> None:
        """
Check metrics for alert conditions"""
        try:
            # Check system resource alerts
            if metrics.cpu_usage_percent > 90:
                await self._create_resource_alert("High CPU Usage", metrics.cpu_usage_percent, "CPU")
            
            if metrics.memory_usage_percent > 90:
                await self._create_resource_alert("High Memory Usage", metrics.memory_usage_percent, "Memory")
            
            if metrics.disk_usage_percent > 85:
                await self._create_resource_alert("High Disk Usage", metrics.disk_usage_percent, "Disk")
            
            # Check detection performance alerts
            if metrics.failed_scans > metrics.successful_scans * 0.1:  # More than 10% failure rate
                alert = Alert(
                    alert_type=AlertType.SYSTEM_ERROR,
                    severity=AlertSeverity.MEDIUM,
                    title="High Scan Failure Rate",
                    message=f"Scan failure rate: {metrics.failed_scans}/{metrics.total_scans_today}"
                )
                await self.send_alert(alert)
            
            # Check for mass infringement
            if metrics.new_violations_today > 50:
                alert = Alert(
                    alert_type=AlertType.MASSIVE_INFRINGEMENT,
                    severity=AlertSeverity.HIGH,
                    title="Massive Content Infringement Detected",
                    message=f"{metrics.new_violations_today} new violations detected today"
                )
                await self.send_alert(alert)
                
        except Exception as e:
            self.logger.error(f"Alert condition check failed: {e}")
    
    async def _create_resource_alert(self, title: str, usage: float, resource_type: str) -> None:
        """Create resource usage alert"""
        alert = Alert(
            alert_type=AlertType.SYSTEM_ERROR,
            severity=AlertSeverity.HIGH if usage > 95 else AlertSeverity.MEDIUM,
            title=title,
            message=f"{resource_type} usage at {usage:.1f}%",
            recommended_actions=[
                f"Monitor {resource_type.lower()} usage",
                "Consider scaling resources",
                "Check for resource leaks"
            ]
        )
        await self.send_alert(alert)


# =============== FACTORY & UTILITIES ===============

class MonitoringServiceFactory:
    """Factory for creating monitoring service instances"""
    
    @staticmethod
    def create_service(config: Optional[MonitoringConfig] = None) -> MonitoringService:
        """
Create configured monitoring service"""
        if config is None:
            config = MonitoringConfig()
        
        return MonitoringService(config)
    
    @staticmethod
    def create_config(
        check_interval_seconds: int = 60,
        email_enabled: bool = True,
        **kwargs
    ) -> MonitoringConfig:
        """
Create monitoring configuration"""
        return MonitoringConfig(
            check_interval_seconds=check_interval_seconds,
            email_enabled=email_enabled,
            **kwargs
        )


def format_alert_for_display(alert: Alert) -> str:
    """
Format alert for display purposes"""
    return f"[{alert.severity.name}] {alert.title} - {alert.message}"


def calculate_uptime_percentage(total_checks: int, successful_checks: int) -> float:
    """Calculate uptime percentage"""
    if total_checks == 0:
        return 0.0
    return (successful_checks / total_checks) * 100.0


# Export public classes
__all__ = [
    'MonitoringService',
    'IMonitoringService',
    'MonitoringStatus',
    'MonitoringConfig',
    'Alert',
    'MonitoringMetrics',
    'AlertSeverity',
    'AlertType',
    'NotificationChannel',
    'MonitoringServiceFactory',
    'format_alert_for_display',
    'calculate_uptime_percentage'
]
