"""Mobile Violation Alert System

Real-time mobile content violation detection and alert system optimized for
mobile devices with push notifications and battery-efficient monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid

# Import mobile notification service
from .push_notifications import PushNotificationService, NotificationPriority, NotificationType

logger = logging.getLogger(__name__)


class MobileViolationType(Enum):
    """Mobile violation types"""
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    UNAUTHORIZED_DISTRIBUTION = "unauthorized_distribution"
    WATERMARK_REMOVAL = "watermark_removal"
    CONTENT_TAMPERING = "content_tampering"
    PIRACY_DETECTED = "piracy_detected"
    LICENSE_VIOLATION = "license_violation"
    FRAUDULENT_CLAIM = "fraudulent_claim"
    IMPERSONATION = "impersonation"


class MobileAlertSeverity(Enum):
    """Mobile alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MobileAlertChannel(Enum):
    """Mobile alert delivery channels"""
    PUSH_NOTIFICATION = "push_notification"
    IN_APP_ALERT = "in_app_alert"
    SMS_ALERT = "sms_alert"
    EMAIL_ALERT = "email_alert"
    WEBHOOK_ALERT = "webhook_alert"
    SYSTEM_NOTIFICATION = "system_notification"


@dataclass
class MobileViolationEvent:
    """Mobile content violation event"""
    event_id: str
    content_id: str
    creator_id: str
    violation_type: MobileViolationType
    severity: MobileAlertSeverity
    detected_at: datetime
    location: str  # URL, platform, etc.
    evidence: Dict[str, Any]
    confidence_score: float  # 0.0-1.0
    source: str  # Detection source
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())


@dataclass
class MobileAlertConfiguration:
    """Mobile alert configuration"""
    enabled_channels: List[MobileAlertChannel]
    severity_threshold: MobileAlertSeverity
    battery_optimization: bool = True
    quiet_hours_start: int = 22  # 10 PM
    quiet_hours_end: int = 8     # 8 AM
    rate_limiting: bool = True
    max_alerts_per_hour: int = 10
    group_similar_alerts: bool = True
    enable_real_time: bool = True
    enable_batch_alerts: bool = True
    network_aware: bool = True
    offline_queuing: bool = True


@dataclass
class MobileAlertRequest:
    """Mobile alert request"""
    request_id: str
    violation_event: MobileViolationEvent
    creator_id: str
    device_tokens: List[str]
    config: MobileAlertConfiguration
    custom_message: Optional[str] = None
    action_buttons: List[str] = None
    deep_link: Optional[str] = None
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())
        if self.action_buttons is None:
            self.action_buttons = []


@dataclass
class MobileAlertResult:
    """Mobile alert delivery result"""
    request_id: str
    success: bool
    channels_used: List[MobileAlertChannel]
    delivery_time_ms: int
    battery_usage_percent: float
    recipients_reached: int
    failed_deliveries: int
    queued_for_retry: int
    error_message: Optional[str] = None
    delivery_details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.delivery_details is None:
            self.delivery_details = {}


class MobileViolationAlertSystem:
    """Mobile Violation Alert System
    
    Detects and alerts about content violations optimized for mobile devices.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize push notification service
        self.push_service = PushNotificationService()
        
        # Mobile optimization settings
        self.mobile_optimizations = {
            "battery_aware": True,
            "network_efficient": True,
            "quiet_hours_respect": True,
            "rate_limiting": True,
            "grouping_enabled": True,
            "offline_queuing": True
        }
        
        # Alert queue for offline scenarios
        self.alert_queue = []
        self.max_queue_size = 100
        
        # Rate limiting
        self.alert_rate_tracker = {}
        
        # Performance tracking
        self.performance_metrics = {
            "total_alerts": 0,
            "successful_alerts": 0,
            "failed_alerts": 0,
            "queued_alerts": 0,
            "average_delivery_time_ms": 0,
            "total_battery_usage": 0.0,
            "violations_detected": 0
        }
        
        # Violation detection patterns
        self.violation_patterns = {
            MobileViolationType.COPYRIGHT_INFRINGEMENT: self._detect_copyright_violation,
            MobileViolationType.UNAUTHORIZED_DISTRIBUTION: self._detect_unauthorized_distribution,
            MobileViolationType.WATERMARK_REMOVAL: self._detect_watermark_removal,
            MobileViolationType.CONTENT_TAMPERING: self._detect_content_tampering,
            MobileViolationType.PIRACY_DETECTED: self._detect_piracy,
            MobileViolationType.LICENSE_VIOLATION: self._detect_license_violation,
            MobileViolationType.FRAUDULENT_CLAIM: self._detect_fraudulent_claim,
            MobileViolationType.IMPERSONATION: self._detect_impersonation
        }
        
        # Alert templates for mobile
        self.mobile_alert_templates = {
            MobileViolationType.COPYRIGHT_INFRINGEMENT: {
                "title": "🚨 Copyright Violation Detected",
                "body": "Your content may be used without permission",
                "icon": "copyright_alert",
                "actions": ["View Details", "Take Action", "Dismiss"]
            },
            MobileViolationType.WATERMARK_REMOVAL: {
                "title": "⚠️ Watermark Tampered",
                "body": "Someone removed your content watermark",
                "icon": "watermark_alert",
                "actions": ["Investigate", "Report", "Ignore"]
            },
            MobileViolationType.PIRACY_DETECTED: {
                "title": "🏴‍☠️ Piracy Alert",
                "body": "Your content found on unauthorized platform",
                "icon": "piracy_alert",
                "actions": ["Take Down", "Legal Action", "Monitor"]
            }
        }
        
        self.logger.info("Mobile Violation Alert System initialized")
    
    async def monitor_violations(self, content_id: str, creator_id: str, monitoring_config: Dict[str, Any] = None) -> str:
        """Start mobile violation monitoring for content"""
        monitoring_config = monitoring_config or {}
        
        monitoring_id = str(uuid.uuid4())
        
        try:
            self.logger.info(f"Starting mobile violation monitoring for content {content_id}")
            
            # Setup mobile-optimized monitoring
            monitoring_task = asyncio.create_task(
                self._mobile_violation_monitoring_loop(content_id, creator_id, monitoring_config)
            )
            
            # Store monitoring task reference
            if not hasattr(self, 'monitoring_tasks'):
                self.monitoring_tasks = {}
            self.monitoring_tasks[monitoring_id] = monitoring_task
            
            return monitoring_id
            
        except Exception as e:
            self.logger.error(f"Failed to start violation monitoring: {str(e)}")
            raise
    
    async def _mobile_violation_monitoring_loop(self, content_id: str, creator_id: str, config: Dict[str, Any]):
        """Mobile-optimized violation monitoring loop"""
        monitoring_interval = config.get("interval_seconds", 300)  # 5 minutes default
        battery_optimization = config.get("battery_optimization", True)
        
        while True:
            try:
                # Check for violations
                violations = await self._scan_for_violations(content_id, creator_id)
                
                # Process detected violations
                for violation in violations:
                    await self._process_violation_event(violation, creator_id)
                
                # Battery-aware sleep interval
                if battery_optimization:
                    # Increase interval during low battery scenarios
                    sleep_time = monitoring_interval
                else:
                    sleep_time = monitoring_interval
                
                await asyncio.sleep(sleep_time)
                
            except asyncio.CancelledError:
                self.logger.info(f"Monitoring cancelled for content {content_id}")
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _scan_for_violations(self, content_id: str, creator_id: str) -> List[MobileViolationEvent]:
        """Scan for content violations using mobile-optimized detection"""
        violations = []
        
        try:
            # Simulate violation detection
            for violation_type, detector in self.violation_patterns.items():
                if await detector(content_id, creator_id):
                    violation = MobileViolationEvent(
                        event_id=str(uuid.uuid4()),
                        content_id=content_id,
                        creator_id=creator_id,
                        violation_type=violation_type,
                        severity=self._determine_severity(violation_type),
                        detected_at=datetime.now(),
                        location="mobile_detected",
                        evidence={"detection_method": "mobile_scan"},
                        confidence_score=0.85,
                        source="mobile_violation_scanner",
                        metadata={"scan_time": datetime.now().isoformat()}
                    )
                    violations.append(violation)
                    self.performance_metrics["violations_detected"] += 1
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Violation scan failed: {str(e)}")
            return []
    
    async def _detect_copyright_violation(self, content_id: str, creator_id: str) -> bool:
        """Detect copyright violations (mobile-optimized)"""
        # Simulate copyright detection
        await asyncio.sleep(0.1)
        return False  # No violation detected in this simulation
    
    async def _detect_unauthorized_distribution(self, content_id: str, creator_id: str) -> bool:
        """Detect unauthorized distribution (mobile-optimized)"""
        await asyncio.sleep(0.05)
        return False
    
    async def _detect_watermark_removal(self, content_id: str, creator_id: str) -> bool:
        """Detect watermark removal (mobile-optimized)"""
        await asyncio.sleep(0.05)
        return False
    
    async def _detect_content_tampering(self, content_id: str, creator_id: str) -> bool:
        """Detect content tampering (mobile-optimized)"""
        await asyncio.sleep(0.05)
        return False
    
    async def _detect_piracy(self, content_id: str, creator_id: str) -> bool:
        """Detect piracy (mobile-optimized)"""
        await asyncio.sleep(0.1)
        return False
    
    async def _detect_license_violation(self, content_id: str, creator_id: str) -> bool:
        """Detect license violations (mobile-optimized)"""
        await asyncio.sleep(0.05)
        return False
    
    async def _detect_fraudulent_claim(self, content_id: str, creator_id: str) -> bool:
        """Detect fraudulent claims (mobile-optimized)"""
        await asyncio.sleep(0.05)
        return False
    
    async def _detect_impersonation(self, content_id: str, creator_id: str) -> bool:
        """Detect impersonation (mobile-optimized)"""
        await asyncio.sleep(0.05)
        return False
    
    def _determine_severity(self, violation_type: MobileViolationType) -> MobileAlertSeverity:
        """Determine alert severity based on violation type"""
        severity_map = {
            MobileViolationType.COPYRIGHT_INFRINGEMENT: MobileAlertSeverity.HIGH,
            MobileViolationType.UNAUTHORIZED_DISTRIBUTION: MobileAlertSeverity.HIGH,
            MobileViolationType.WATERMARK_REMOVAL: MobileAlertSeverity.MEDIUM,
            MobileViolationType.CONTENT_TAMPERING: MobileAlertSeverity.MEDIUM,
            MobileViolationType.PIRACY_DETECTED: MobileAlertSeverity.CRITICAL,
            MobileViolationType.LICENSE_VIOLATION: MobileAlertSeverity.HIGH,
            MobileViolationType.FRAUDULENT_CLAIM: MobileAlertSeverity.CRITICAL,
            MobileViolationType.IMPERSONATION: MobileAlertSeverity.EMERGENCY
        }
        return severity_map.get(violation_type, MobileAlertSeverity.MEDIUM)
    
    async def _process_violation_event(self, violation: MobileViolationEvent, creator_id: str):
        """Process detected violation event"""
        try:
            # Create default alert configuration
            alert_config = MobileAlertConfiguration(
                enabled_channels=[MobileAlertChannel.PUSH_NOTIFICATION, MobileAlertChannel.IN_APP_ALERT],
                severity_threshold=MobileAlertSeverity.LOW,
                battery_optimization=True,
                rate_limiting=True,
                max_alerts_per_hour=10
            )
            
            # Create alert request
            alert_request = MobileAlertRequest(
                request_id=str(uuid.uuid4()),
                violation_event=violation,
                creator_id=creator_id,
                device_tokens=["mobile_device_token"],  # Would be retrieved from user preferences
                config=alert_config
            )
            
            # Send alert
            await self.send_violation_alert(alert_request)
            
        except Exception as e:
            self.logger.error(f"Failed to process violation event: {str(e)}")
    
    async def send_violation_alert(self, request: MobileAlertRequest) -> MobileAlertResult:
        """Send mobile violation alert"""
        start_time = time.time()
        
        try:
            self.logger.info(f"Sending mobile violation alert for {request.request_id}")
            
            # Check rate limiting
            if not await self._check_rate_limit(request.creator_id, request.config):
                return MobileAlertResult(
                    request_id=request.request_id,
                    success=False,
                    channels_used=[],
                    delivery_time_ms=0,
                    battery_usage_percent=0.0,
                    recipients_reached=0,
                    failed_deliveries=0,
                    queued_for_retry=0,
                    error_message="Rate limit exceeded"
                )
            
            # Check quiet hours
            if await self._is_quiet_hours(request.config):
                await self._queue_alert_for_later(request)
                return MobileAlertResult(
                    request_id=request.request_id,
                    success=True,
                    channels_used=[],
                    delivery_time_ms=0,
                    battery_usage_percent=0.0,
                    recipients_reached=0,
                    failed_deliveries=0,
                    queued_for_retry=len(request.device_tokens)
                )
            
            # Send alerts through configured channels
            channels_used = []
            battery_usage = 0.0
            recipients_reached = 0
            failed_deliveries = 0
            
            for channel in request.config.enabled_channels:
                if channel == MobileAlertChannel.PUSH_NOTIFICATION:
                    success = await self._send_push_notification(request)
                    if success:
                        channels_used.append(channel)
                        recipients_reached += len(request.device_tokens)
                        battery_usage += 0.1
                    else:
                        failed_deliveries += len(request.device_tokens)
                
                elif channel == MobileAlertChannel.IN_APP_ALERT:
                    success = await self._send_in_app_alert(request)
                    if success:
                        channels_used.append(channel)
                        recipients_reached += 1
                        battery_usage += 0.05
                    else:
                        failed_deliveries += 1
            
            processing_time = int((time.time() - start_time) * 1000)
            
            result = MobileAlertResult(
                request_id=request.request_id,
                success=len(channels_used) > 0,
                channels_used=channels_used,
                delivery_time_ms=processing_time,
                battery_usage_percent=battery_usage,
                recipients_reached=recipients_reached,
                failed_deliveries=failed_deliveries,
                queued_for_retry=0
            )
            
            await self._update_performance_metrics(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Mobile alert failed for {request.request_id}: {str(e)}")
            processing_time = int((time.time() - start_time) * 1000)
            
            return MobileAlertResult(
                request_id=request.request_id,
                success=False,
                channels_used=[],
                delivery_time_ms=processing_time,
                battery_usage_percent=0.1,
                recipients_reached=0,
                failed_deliveries=len(request.device_tokens),
                queued_for_retry=0,
                error_message=str(e)
            )
    
    async def _check_rate_limit(self, creator_id: str, config: MobileAlertConfiguration) -> bool:
        """Check mobile alert rate limiting"""
        if not config.rate_limiting:
            return True
        
        current_hour = datetime.now().hour
        rate_key = f"{creator_id}_{current_hour}"
        
        current_count = self.alert_rate_tracker.get(rate_key, 0)
        if current_count >= config.max_alerts_per_hour:
            return False
        
        self.alert_rate_tracker[rate_key] = current_count + 1
        return True
    
    async def _is_quiet_hours(self, config: MobileAlertConfiguration) -> bool:
        """Check if current time is within quiet hours"""
        current_hour = datetime.now().hour
        
        if config.quiet_hours_start <= config.quiet_hours_end:
            # Same day quiet hours
            return config.quiet_hours_start <= current_hour <= config.quiet_hours_end
        else:
            # Overnight quiet hours
            return current_hour >= config.quiet_hours_start or current_hour <= config.quiet_hours_end
    
    async def _queue_alert_for_later(self, request: MobileAlertRequest):
        """Queue alert for delivery outside quiet hours"""
        if len(self.alert_queue) < self.max_queue_size:
            self.alert_queue.append((request, datetime.now()))
            self.performance_metrics["queued_alerts"] += 1
    
    async def _send_push_notification(self, request: MobileAlertRequest) -> bool:
        """Send push notification for violation alert"""
        try:
            violation_type = request.violation_event.violation_type
            template = self.mobile_alert_templates.get(violation_type, {
                "title": "Content Alert",
                "body": "Your content requires attention",
                "actions": ["View Details"]
            })
            
            notification_data = {
                "title": template["title"],
                "body": request.custom_message or template["body"],
                "data": {
                    "violation_id": request.violation_event.event_id,
                    "content_id": request.violation_event.content_id,
                    "violation_type": violation_type.value,
                    "severity": request.violation_event.severity.value,
                    "deep_link": request.deep_link
                },
                "actions": request.action_buttons or template["actions"]
            }
            
            # Send through push notification service
            success = await self.push_service.send_notification(
                device_tokens=request.device_tokens,
                notification_data=notification_data,
                priority=NotificationPriority.HIGH if request.violation_event.severity in [
                    MobileAlertSeverity.CRITICAL, MobileAlertSeverity.EMERGENCY
                ] else NotificationPriority.NORMAL
            )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Push notification failed: {str(e)}")
            return False
    
    async def _send_in_app_alert(self, request: MobileAlertRequest) -> bool:
        """Send in-app alert for violation"""
        try:
            # Simulate in-app alert
            await asyncio.sleep(0.05)
            return True
        except Exception:
            return False
    
    async def _update_performance_metrics(self, result: MobileAlertResult):
        """Update mobile alert performance metrics"""
        self.performance_metrics["total_alerts"] += 1
        
        if result.success:
            self.performance_metrics["successful_alerts"] += 1
        else:
            self.performance_metrics["failed_alerts"] += 1
        
        # Update averages
        total = self.performance_metrics["total_alerts"]
        current_avg = self.performance_metrics["average_delivery_time_ms"]
        self.performance_metrics["average_delivery_time_ms"] = (
            (current_avg * (total - 1) + result.delivery_time_ms) / total
        )
        
        self.performance_metrics["total_battery_usage"] += result.battery_usage_percent
    
    async def stop_monitoring(self, monitoring_id: str) -> bool:
        """Stop mobile violation monitoring"""
        try:
            if hasattr(self, 'monitoring_tasks') and monitoring_id in self.monitoring_tasks:
                task = self.monitoring_tasks[monitoring_id]
                task.cancel()
                del self.monitoring_tasks[monitoring_id]
                self.logger.info(f"Stopped monitoring {monitoring_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {str(e)}")
            return False
    
    async def get_violation_history(self, creator_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get mobile violation history for creator"""
        # Simulate violation history retrieval
        return [
            {
                "violation_id": str(uuid.uuid4()),
                "content_id": "sample_content",
                "violation_type": "copyright_infringement",
                "severity": "high",
                "detected_at": datetime.now().isoformat(),
                "status": "resolved",
                "mobile_detected": True
            }
        ]
    
    async def get_mobile_performance_metrics(self) -> Dict[str, Any]:
        """Get mobile violation alert performance metrics"""
        return {
            **self.performance_metrics,
            "mobile_optimizations_enabled": self.mobile_optimizations,
            "queue_size": len(self.alert_queue),
            "active_monitoring_sessions": len(getattr(self, 'monitoring_tasks', {})),
            "timestamp": datetime.now().isoformat()
        }


# Factory function
def create_mobile_violation_alert_system(config: Optional[Dict[str, Any]] = None) -> MobileViolationAlertSystem:
    """Create and configure mobile violation alert system"""
    return MobileViolationAlertSystem(config)