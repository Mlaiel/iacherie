"""
IA Influencer Agent - Real-time Alert Configuration
Enterprise alerting system for content protection network infrastructure

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
Project: IA Influencer Agent Platform - Content Protection & Monetization
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  AVERTISSEMENT SÉVÈRE ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact autorisations: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp
import redis.asyncio as aioredis
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Alert notification channels"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    PUSH = "push"


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    condition: str
    severity: AlertSeverity
    description: str
    enabled: bool = True
    channels: List[AlertChannel] = None
    cooldown_minutes: int = 15
    auto_resolve: bool = False
    escalation_rules: Dict[str, Any] = None


@dataclass
class Alert:
    """Alert instance"""
    id: str
    rule_name: str
    severity: AlertSeverity
    title: str
    description: str
    timestamp: datetime
    resolved: bool = False
    resolved_timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = None


class NetworkAlertManager:
    """
    Real-time alert management for IA Influencer Agent Network Module
    Provides intelligent alerting with escalation and noise reduction
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        email_config: Dict[str, str] = None,
        slack_webhook: str = None
    ):
        self.redis_url = redis_url
        self.email_config = email_config or {}
        self.slack_webhook = slack_webhook
        
        # Alert management
        self.alert_rules = {}
        self.active_alerts = {}
        self.alert_history = []
        self.escalation_chains = {}
        
        # Communication clients
        self.redis_client = None
        self.notification_channels = {}
        
        # Initialize default alert rules for IA platform
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default alert rules for IA platform"""
        
        default_rules = [
            # Content Protection Alerts
            AlertRule(
                name="high_content_violation_rate",
                condition="rate(content_violations_detected[5m]) > 10",
                severity=AlertSeverity.HIGH,
                description="High rate of content violations detected",
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=10
            ),
            
            AlertRule(
                name="fingerprint_processing_failure",
                condition="rate(fingerprint_failures[1m]) > 5",
                severity=AlertSeverity.CRITICAL,
                description="Multiple fingerprint processing failures",
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.SMS],
                cooldown_minutes=5
            ),
            
            AlertRule(
                name="copyright_infringement_detected",
                condition="copyright_violations > 0",
                severity=AlertSeverity.CRITICAL,
                description="Copyright infringement detected",
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                auto_resolve=False
            ),
            
            # Network Performance Alerts
            AlertRule(
                name="high_network_latency",
                condition="p95(network_latency) > 500ms",
                severity=AlertSeverity.HIGH,
                description="95th percentile network latency exceeds 500ms",
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=15
            ),
            
            AlertRule(
                name="low_cdn_cache_hit_ratio",
                condition="cdn_cache_hit_ratio < 0.8",
                severity=AlertSeverity.MEDIUM,
                description="CDN cache hit ratio below 80%",
                channels=[AlertChannel.SLACK],
                cooldown_minutes=30
            ),
            
            AlertRule(
                name="bandwidth_usage_spike",
                condition="bandwidth_usage > baseline * 3",
                severity=AlertSeverity.HIGH,
                description="Bandwidth usage 3x above baseline",
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=10
            ),
            
            AlertRule(
                name="geographic_distribution_failure",
                condition="geo_distribution_errors > 0",
                severity=AlertSeverity.HIGH,
                description="Geographic distribution system errors",
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=15
            ),
            
            # Security Alerts
            AlertRule(
                name="ddos_attack_detected",
                condition="ddos_indicators > threshold",
                severity=AlertSeverity.CRITICAL,
                description="DDoS attack detected",
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.SMS],
                cooldown_minutes=5
            ),
            
            AlertRule(
                name="suspicious_traffic_pattern",
                condition="anomaly_score > 0.8",
                severity=AlertSeverity.HIGH,
                description="Suspicious traffic pattern detected",
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=10
            ),
            
            AlertRule(
                name="unauthorized_access_attempt",
                condition="failed_auth_attempts > 100/min",
                severity=AlertSeverity.HIGH,
                description="Multiple unauthorized access attempts",
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=5
            ),
            
            # Business Critical Alerts
            AlertRule(
                name="revenue_collection_failure",
                condition="revenue_processing_errors > 0",
                severity=AlertSeverity.CRITICAL,
                description="Revenue collection system failure",
                channels=[AlertChannel.EMAIL, AlertChannel.SMS],
                auto_resolve=False
            ),
            
            AlertRule(
                name="creator_platform_unavailable",
                condition="creator_api_availability < 0.99",
                severity=AlertSeverity.CRITICAL,
                description="Creator platform API unavailable",
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.SMS],
                cooldown_minutes=5
            ),
            
            AlertRule(
                name="content_delivery_degraded",
                condition="content_delivery_success_rate < 0.95",
                severity=AlertSeverity.HIGH,
                description="Content delivery success rate below 95%",
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=10
            ),
            
            # Infrastructure Alerts
            AlertRule(
                name="database_connection_pool_exhausted",
                condition="db_connection_pool_usage > 0.9",
                severity=AlertSeverity.HIGH,
                description="Database connection pool near exhaustion",
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=15
            ),
            
            AlertRule(
                name="redis_memory_usage_high",
                condition="redis_memory_usage > 0.85",
                severity=AlertSeverity.MEDIUM,
                description="Redis memory usage above 85%",
                channels=[AlertChannel.SLACK],
                cooldown_minutes=30
            ),
            
            AlertRule(
                name="microservice_health_check_failure",
                condition="health_check_failures > 3",
                severity=AlertSeverity.HIGH,
                description="Multiple microservice health check failures",
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=10
            )
        ]
        
        # Convert to dictionary for easy access
        for rule in default_rules:
            self.alert_rules[rule.name] = rule
    
    async def initialize(self) -> bool:
        """Initialize alert manager"""
        try:
            logger.info("Initializing Network Alert Manager...")
            
            # Initialize Redis for alert storage
            self.redis_client = aioredis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Setup notification channels
            await self._setup_notification_channels()
            
            # Load existing alerts from storage
            await self._load_active_alerts()
            
            # Start background alert processing
            asyncio.create_task(self._alert_processing_loop())
            asyncio.create_task(self._alert_cleanup_loop())
            
            logger.info(f"Network Alert Manager initialized with {len(self.alert_rules)} rules")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize alert manager: {e}")
            return False
    
    async def trigger_alert(
        self,
        rule_name: str,
        title: str,
        description: str,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Trigger an alert based on rule"""
        try:
            # Check if rule exists
            if rule_name not in self.alert_rules:
                logger.error(f"Alert rule not found: {rule_name}")
                return None
            
            rule = self.alert_rules[rule_name]
            
            # Check if rule is enabled
            if not rule.enabled:
                logger.debug(f"Alert rule disabled: {rule_name}")
                return None
            
            # Check cooldown period
            if await self._is_in_cooldown(rule_name):
                logger.debug(f"Alert rule in cooldown: {rule_name}")
                return None
            
            # Create alert
            alert_id = f"{rule_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            alert = Alert(
                id=alert_id,
                rule_name=rule_name,
                severity=rule.severity,
                title=title,
                description=description,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            # Store alert
            self.active_alerts[alert_id] = alert
            await self._store_alert(alert)
            
            # Send notifications
            await self._send_notifications(alert, rule)
            
            # Update cooldown
            await self._set_cooldown(rule_name, rule.cooldown_minutes)
            
            logger.info(f"Alert triggered: {alert_id} - {title}")
            return alert_id
            
        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
            return None
    
    async def resolve_alert(self, alert_id: str, resolution_note: str = None) -> bool:
        """Resolve an active alert"""
        try:
            if alert_id not in self.active_alerts:
                logger.error(f"Alert not found: {alert_id}")
                return False
            
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_timestamp = datetime.now()
            
            if resolution_note:
                if not alert.metadata:
                    alert.metadata = {}
                alert.metadata['resolution_note'] = resolution_note
            
            # Move to history
            self.alert_history.append(alert)
            del self.active_alerts[alert_id]
            
            # Update storage
            await self._update_alert_storage(alert)
            
            # Send resolution notification
            await self._send_resolution_notification(alert)
            
            logger.info(f"Alert resolved: {alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False
    
    async def get_active_alerts(self, severity: AlertSeverity = None) -> List[Alert]:
        """Get list of active alerts"""
        try:
            alerts = list(self.active_alerts.values())
            
            if severity:
                alerts = [alert for alert in alerts if alert.severity == severity]
            
            # Sort by severity and timestamp
            severity_order = {
                AlertSeverity.CRITICAL: 0,
                AlertSeverity.HIGH: 1,
                AlertSeverity.MEDIUM: 2,
                AlertSeverity.LOW: 3
            }
            
            alerts.sort(key=lambda x: (severity_order[x.severity], x.timestamp), reverse=True)
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
    
    async def get_alert_statistics(self, time_range: timedelta = timedelta(days=7)) -> Dict[str, Any]:
        """Get alert statistics for time range"""
        try:
            end_time = datetime.now()
            start_time = end_time - time_range
            
            # Filter alerts by time range
            relevant_alerts = [
                alert for alert in self.alert_history
                if start_time <= alert.timestamp <= end_time
            ]
            
            # Add active alerts
            relevant_alerts.extend(self.active_alerts.values())
            
            # Calculate statistics
            stats = {
                'total_alerts': len(relevant_alerts),
                'active_alerts': len(self.active_alerts),
                'resolved_alerts': len([a for a in relevant_alerts if a.resolved]),
                'alerts_by_severity': {},
                'alerts_by_rule': {},
                'average_resolution_time': None,
                'top_alert_rules': []
            }
            
            # Count by severity
            for alert in relevant_alerts:
                severity_name = alert.severity.value
                stats['alerts_by_severity'][severity_name] = \
                    stats['alerts_by_severity'].get(severity_name, 0) + 1
            
            # Count by rule
            for alert in relevant_alerts:
                rule_name = alert.rule_name
                stats['alerts_by_rule'][rule_name] = \
                    stats['alerts_by_rule'].get(rule_name, 0) + 1
            
            # Calculate average resolution time
            resolved_alerts = [a for a in relevant_alerts if a.resolved and a.resolved_timestamp]
            if resolved_alerts:
                total_resolution_time = sum([
                    (alert.resolved_timestamp - alert.timestamp).total_seconds()
                    for alert in resolved_alerts
                ])
                stats['average_resolution_time'] = total_resolution_time / len(resolved_alerts)
            
            # Top alert rules
            stats['top_alert_rules'] = sorted(
                stats['alerts_by_rule'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get alert statistics: {e}")
            return {}
    
    async def create_custom_rule(self, rule: AlertRule) -> bool:
        """Create a custom alert rule"""
        try:
            # Validate rule
            if not rule.name or not rule.condition:
                logger.error("Alert rule missing required fields")
                return False
            
            # Store rule
            self.alert_rules[rule.name] = rule
            await self._store_alert_rule(rule)
            
            logger.info(f"Custom alert rule created: {rule.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create custom rule: {e}")
            return False
    
    async def update_rule_status(self, rule_name: str, enabled: bool) -> bool:
        """Enable or disable an alert rule"""
        try:
            if rule_name not in self.alert_rules:
                logger.error(f"Alert rule not found: {rule_name}")
                return False
            
            self.alert_rules[rule_name].enabled = enabled
            await self._store_alert_rule(self.alert_rules[rule_name])
            
            logger.info(f"Alert rule {'enabled' if enabled else 'disabled'}: {rule_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update rule status: {e}")
            return False
    
    # Private methods for internal functionality
    
    async def _setup_notification_channels(self):
        """Setup notification channels"""
        try:
            # Email channel
            if self.email_config:
                self.notification_channels[AlertChannel.EMAIL] = self.email_config
            
            # Slack channel
            if self.slack_webhook:
                self.notification_channels[AlertChannel.SLACK] = {
                    'webhook_url': self.slack_webhook
                }
            
            logger.info(f"Setup {len(self.notification_channels)} notification channels")
            
        except Exception as e:
            logger.error(f"Failed to setup notification channels: {e}")
    
    async def _send_notifications(self, alert: Alert, rule: AlertRule):
        """Send alert notifications through configured channels"""
        try:
            if not rule.channels:
                return
            
            for channel in rule.channels:
                if channel in self.notification_channels:
                    await self._send_channel_notification(alert, channel)
            
        except Exception as e:
            logger.error(f"Failed to send notifications: {e}")
    
    async def _send_channel_notification(self, alert: Alert, channel: AlertChannel):
        """Send notification through specific channel"""
        try:
            if channel == AlertChannel.EMAIL:
                await self._send_email_notification(alert)
            elif channel == AlertChannel.SLACK:
                await self._send_slack_notification(alert)
            elif channel == AlertChannel.WEBHOOK:
                await self._send_webhook_notification(alert)
            
        except Exception as e:
            logger.error(f"Failed to send {channel.value} notification: {e}")
    
    async def _alert_processing_loop(self):
        """Background alert processing loop"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self._process_auto_resolve()
                await self._check_escalations()
                
            except Exception as e:
                logger.error(f"Alert processing loop error: {e}")
                await asyncio.sleep(30)


# Example usage and testing
async def demo_alert_manager():
    """Demonstrate alert manager functionality"""
    
    print("🚨 IA Influencer Agent - Network Alert Manager Demo")
    print("=" * 60)
    
    # Initialize alert manager
    alert_manager = NetworkAlertManager()
    success = await alert_manager.initialize()
    
    if not success:
        print("❌ Failed to initialize alert manager")
        return
    
    print("✅ Alert Manager Initialized")
    print(f"📋 Default Rules: {len(alert_manager.alert_rules)}")
    
    # Trigger some test alerts
    print("\n🚨 Triggering Test Alerts...")
    
    # High content violation rate
    await alert_manager.trigger_alert(
        rule_name="high_content_violation_rate",
        title="High Content Violation Rate Detected",
        description="Detected 15 content violations in the last 5 minutes",
        metadata={'violation_count': 15, 'time_window': '5m'}
    )
    
    # Network latency alert
    await alert_manager.trigger_alert(
        rule_name="high_network_latency",
        title="Network Latency Spike",
        description="95th percentile latency reached 750ms",
        metadata={'p95_latency': 750, 'threshold': 500}
    )
    
    # Security alert
    await alert_manager.trigger_alert(
        rule_name="ddos_attack_detected",
        title="DDoS Attack in Progress",
        description="Detected coordinated attack from multiple IPs",
        metadata={'attack_type': 'volumetric', 'source_ips': 247}
    )
    
    print("✅ Test Alerts Triggered")
    
    # Get active alerts
    print("\n📊 Active Alerts Summary:")
    active_alerts = await alert_manager.get_active_alerts()
    
    for alert in active_alerts:
        print(f"   🚨 {alert.severity.value.upper()}: {alert.title}")
        print(f"      Rule: {alert.rule_name}")
        print(f"      Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get alert statistics
    print("\n📈 Alert Statistics:")
    stats = await alert_manager.get_alert_statistics()
    
    if stats:
        print(f"   📊 Total Alerts: {stats['total_alerts']}")
        print(f"   🔴 Active Alerts: {stats['active_alerts']}")
        print(f"   ✅ Resolved Alerts: {stats['resolved_alerts']}")
        print(f"   📋 By Severity: {stats['alerts_by_severity']}")
    
    # Create custom rule
    print("\n🔧 Creating Custom Alert Rule...")
    
    custom_rule = AlertRule(
        name="custom_creator_engagement_drop",
        condition="creator_engagement_score < 0.3",
        severity=AlertSeverity.MEDIUM,
        description="Creator engagement score dropped below 30%",
        channels=[AlertChannel.EMAIL]
    )
    
    success = await alert_manager.create_custom_rule(custom_rule)
    if success:
        print("✅ Custom Alert Rule Created")
    
    print(f"\n📋 Total Rules: {len(alert_manager.alert_rules)}")
    
    print("\n🎯 Alert Manager Demo Completed!")
    print("🚨 Real-time alerting active for all IA platform components")
    print("📧 Notifications configured for critical events")
    print("📊 Alert analytics and trending available")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(demo_alert_manager())
