"""
Real-time Alert Infrastructure Manager

Enterprise-grade real-time alerting system for content protection violations,
system monitoring, security incidents, and business intelligence.

Project: IA Influencer Agent + Content Protection Platform
Author: Fahed Mlaiel <mlaiel@live.de>

  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED 
  This software is protected by international copyright laws.         
  Unauthorized reproduction, distribution, or use is strictly        
  prohibited and may result in severe civil and criminal penalties.  
  All rights reserved to Fahed Mlaiel (mlaiel@live.de).             
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Union, Callable, Set
import json
import uuid
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import websockets
import requests
import redis
import aioredis
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertCategory(Enum):
    """Alert categories"""
    CONTENT_VIOLATION = "content_violation"
    SECURITY_INCIDENT = "security_incident"
    SYSTEM_FAILURE = "system_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    BUSINESS_ANOMALY = "business_anomaly"
    LEGAL_NOTICE = "legal_notice"
    REVENUE_LOSS = "revenue_loss"
    USER_ACTIVITY = "user_activity"

class AlertChannel(Enum):
    """Alert delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    WEBSOCKET = "websocket"
    SLACK = "slack"
    TEAMS = "teams"
    DISCORD = "discord"
    PUSH_NOTIFICATION = "push_notification"
    TELEGRAM = "telegram"

class AlertStatus(Enum):
    """Alert processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    category: AlertCategory
    severity: AlertSeverity
    condition: str  # JSON query or condition
    channels: List[AlertChannel]
    recipients: List[str]
    enabled: bool = True
    cooldown_period: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    escalation_rules: Optional[Dict[str, Any]] = None
    custom_message_template: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Alert:
    """Real-time alert data structure"""
    alert_id: str
    rule_id: str
    category: AlertCategory
    severity: AlertSeverity
    title: str
    message: str
    source: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: AlertStatus = AlertStatus.PENDING
    channels: List[AlertChannel] = field(default_factory=list)
    recipients: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    escalated: bool = False
    delivery_attempts: int = 0
    delivery_results: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AlertInfrastructureSpec:
    """Real-time alert infrastructure specification"""
    redis_url: str = "redis://localhost:6379"
    email_config: Dict[str, str] = field(default_factory=dict)
    sms_config: Dict[str, str] = field(default_factory=dict)
    webhook_config: Dict[str, str] = field(default_factory=dict)
    websocket_port: int = 8765
    slack_config: Dict[str, str] = field(default_factory=dict)
    teams_config: Dict[str, str] = field(default_factory=dict)
    max_concurrent_alerts: int = 1000
    alert_retention_days: int = 90
    enable_escalation: bool = True
    enable_acknowledgment: bool = True
    default_timeout: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    rate_limiting: bool = True
    max_alerts_per_minute: int = 100

class EmailAlertChannel:
    """Email alert delivery channel"""
    
    def __init__(self, config: Dict[str, str]):
        self.smtp_server = config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = int(config.get("smtp_port", "587"))
        self.username = config.get("username")
        self.password = config.get("password")
        self.from_email = config.get("from_email", self.username)
        
    async def send_alert(self, alert: Alert) -> Dict[str, Any]:
        """Send alert via email"""



        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(alert.recipients)
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
            
            # Create HTML body
            html_body = self._create_html_email_body(alert)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return {
                "status": "sent",
                "channel": "email",
                "recipients": alert.recipients,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Email alert delivery failed: {e}")
            return {
                "status": "failed",
                "channel": "email",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _create_html_email_body(self, alert: Alert) -> str:
        """Create HTML email body for alert"""
        severity_colors = {
            AlertSeverity.LOW: "#28a745",
            AlertSeverity.MEDIUM: "#ffc107", 
            AlertSeverity.HIGH: "#fd7e14",
            AlertSeverity.CRITICAL: "#dc3545",
            AlertSeverity.EMERGENCY: "#6f42c1"
        }
        
        color = severity_colors.get(alert.severity, "#6c757d")
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, {color}, {color}cc); color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                    <h2 style="margin: 0;">{alert.title}</h2>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">{alert.severity.value.upper()} • {alert.category.value.replace('_', ' ').title()}</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px; border: 1px solid #dee2e6;">
                    <h3 style="color: #495057; margin-top: 0;">Alert Details</h3>
                    <p><strong>Message:</strong> {alert.message}</p>
                    <p><strong>Source:</strong> {alert.source}</p>
                    <p><strong>Timestamp:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                    <p><strong>Alert ID:</strong> {alert.alert_id}</p>
                    
                    {self._format_metadata_html(alert.metadata)}
                    
                    <div style="margin-top: 20px; padding: 15px; background: white; border-radius: 4px; border-left: 4px solid {color};">
                        <h4 style="margin: 0 0 10px 0; color: {color};">Action Required</h4>
                        <p style="margin: 0;">Please investigate this alert and take appropriate action. 
                        Log into the IA Influencer Agent dashboard for more details.</p>
                    </div>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: #e9ecef; border-radius: 4px; font-size: 12px; color: #6c757d;">
                    <p style="margin: 0;">This is an automated alert from IA Influencer Agent Platform.</p>
                    <p style="margin: 5px 0 0 0;">© 2025 Fahed Mlaiel. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _format_metadata_html(self, metadata: Dict[str, Any]) -> str:
        """Format metadata as HTML"""
        if not metadata:
            return ""
        
        html = "<h4>Additional Information</h4><ul>"
        for key, value in metadata.items():
            html += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
        html += "</ul>"
        return html

class WebhookAlertChannel:
    """Webhook alert delivery channel"""
    
    def __init__(self, config: Dict[str, str]):
        self.webhook_urls = config.get("webhook_urls", [])
        self.auth_headers = config.get("auth_headers", {})
        self.timeout = int(config.get("timeout", "30"))
        
    async def send_alert(self, alert: Alert) -> Dict[str, Any]:
        """Send alert via webhook"""
        results = []
        
        for url in self.webhook_urls:
            try:
                payload = {
                    "alert_id": alert.alert_id,
                    "category": alert.category.value,
                    "severity": alert.severity.value,
                    "title": alert.title,
                    "message": alert.message,
                    "source": alert.source,
                    "timestamp": alert.timestamp.isoformat(),
                    "metadata": alert.metadata
                }
                
                headers = {"Content-Type": "application/json"}
                headers.update(self.auth_headers)
                
                response = requests.post(
                    url, 
                    json=payload, 
                    headers=headers, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                results.append({
                    "url": url,
                    "status": "sent",
                    "response_code": response.status_code
                })
                
            except Exception as e:
                logger.error(f"Webhook alert delivery failed for {url}: {e}")
                results.append({
                    "url": url,
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "status": "completed",
            "channel": "webhook",
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }

class WebSocketAlertChannel:
    """WebSocket alert delivery channel"""
    
    def __init__(self, port: int = 8765):
        self.port = port
        self.clients = set()
        self.server = None
        
    async def start_server(self):
        """Start WebSocket server"""
        self.server = await websockets.serve(
            self.handle_client, "localhost", self.port
        )
        logger.info(f"WebSocket alert server started on port {self.port}")
        
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connection"""
        self.clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)
    
    async def send_alert(self, alert: Alert) -> Dict[str, Any]:
        """Send alert via WebSocket to all connected clients"""
        if not self.clients:
            return {
                "status": "no_clients",
                "channel": "websocket",
                "message": "No WebSocket clients connected"
            }
        
        payload = {
            "type": "alert",
            "alert_id": alert.alert_id,
            "category": alert.category.value,
            "severity": alert.severity.value,
            "title": alert.title,
            "message": alert.message,
            "source": alert.source,
            "timestamp": alert.timestamp.isoformat(),
            "metadata": alert.metadata
        }
        
        message = json.dumps(payload)
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"WebSocket alert delivery failed: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected_clients
        
        return {
            "status": "sent",
            "channel": "websocket",
            "clients_notified": len(self.clients) - len(disconnected_clients),
            "clients_failed": len(disconnected_clients),
            "timestamp": datetime.utcnow().isoformat()
        }

class SlackAlertChannel:
    """Slack alert delivery channel"""
    
    def __init__(self, config: Dict[str, str]):
        self.webhook_url = config.get("webhook_url")
        self.bot_token = config.get("bot_token")
        self.default_channel = config.get("default_channel", "#alerts")
        
    async def send_alert(self, alert: Alert) -> Dict[str, Any]:
        """Send alert to Slack"""



        try:
            color_map = {
                AlertSeverity.LOW: "good",
                AlertSeverity.MEDIUM: "warning",
                AlertSeverity.HIGH: "danger",
                AlertSeverity.CRITICAL: "danger",
                AlertSeverity.EMERGENCY: "#800080"
            }
            
            payload = {
                "text": f" {alert.severity.value.upper()} Alert",
                "attachments": [
                    {
                        "color": color_map.get(alert.severity, "good"),
                        "title": alert.title,
                        "text": alert.message,
                        "fields": [
                            {
                                "title": "Category",
                                "value": alert.category.value.replace('_', ' ').title(),
                                "short": True
                            },
                            {
                                "title": "Source",
                                "value": alert.source,
                                "short": True
                            },
                            {
                                "title": "Alert ID",
                                "value": alert.alert_id,
                                "short": True
                            },
                            {
                                "title": "Timestamp",
                                "value": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'),
                                "short": True
                            }
                        ],
                        "footer": "IA Influencer Agent Platform",
                        "ts": int(alert.timestamp.timestamp())
                    }
                ]
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            
            return {
                "status": "sent",
                "channel": "slack",
                "response_code": response.status_code,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Slack alert delivery failed: {e}")
            return {
                "status": "failed",
                "channel": "slack",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

class RealTimeAlertInfrastructureManager:
    """
    Enterprise Real-time Alert Infrastructure Manager
    
    Manages comprehensive real-time alerting system with multiple delivery channels,
    escalation rules, acknowledgment workflows, and intelligent alert routing.
    """
    
    def __init__(self, spec: AlertInfrastructureSpec):
        self.spec = spec
        self.redis_client = None
        self.alert_rules: Dict[str, AlertRule] = {}
        self.channels: Dict[AlertChannel, Any] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.rate_limiter = {}
        self._initialize_channels()
        
    async def initialize_alert_infrastructure(self) -> Dict[str, Any]:
        """Initialize complete real-time alert infrastructure"""



        try:
            logger.info("Initializing real-time alert infrastructure...")
            
            # Initialize Redis for alert queuing
            self.redis_client = await aioredis.from_url(self.spec.redis_url)
            
            # Setup alert channels
            channel_results = await self._setup_alert_channels()
            
            # Initialize alert processing workers
            worker_results = await self._setup_alert_workers()
            
            # Setup alert rules engine
            rules_results = await self._setup_alert_rules_engine()
            
            # Initialize monitoring and metrics
            monitoring_results = await self._setup_alert_monitoring()
            
            results = {
                "status": "success",
                "infrastructure_id": str(uuid.uuid4()),
                "channels": channel_results,
                "workers": worker_results,
                "rules_engine": rules_results,
                "monitoring": monitoring_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info("Real-time alert infrastructure initialized successfully")
            return results
            
        except Exception as e:
            logger.error(f"Failed to initialize alert infrastructure: {e}")
            raise

    async def create_alert_rule(self, rule: AlertRule) -> Dict[str, Any]:
        """Create new alert rule"""



        try:
            # Validate rule
            validation_result = await self._validate_alert_rule(rule)
            if not validation_result["is_valid"]:
                return {"status": "failed", "errors": validation_result["errors"]}
            
            # Store rule
            self.alert_rules[rule.rule_id] = rule
            
            # Persist to Redis
            await self.redis_client.hset(
                "alert_rules", 
                rule.rule_id, 
                json.dumps(rule.__dict__, default=str)
            )
            
            logger.info(f"Created alert rule: {rule.name} ({rule.rule_id})")
            return {
                "status": "created",
                "rule_id": rule.rule_id,
                "rule_name": rule.name
            }
            
        except Exception as e:
            logger.error(f"Failed to create alert rule: {e}")
            raise

    async def trigger_alert(self, 
                           category: AlertCategory,
                           severity: AlertSeverity,
                           title: str,
                           message: str,
                           source: str,
                           metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Trigger new alert"""



        try:
            alert = Alert(
                alert_id=str(uuid.uuid4()),
                rule_id="manual",
                category=category,
                severity=severity,
                title=title,
                message=message,
                source=source,
                metadata=metadata or {}
            )
            
            # Apply rate limiting
            if not await self._check_rate_limit(alert):
                return {
                    "status": "rate_limited",
                    "message": "Alert rate limit exceeded"
                }
            
            # Find matching rules
            matching_rules = await self._find_matching_rules(alert)
            
            if not matching_rules:
                logger.warning(f"No matching rules for alert: {alert.title}")
                return {
                    "status": "no_rules",
                    "message": "No matching alert rules found"
                }
            
            # Process alert with all matching rules
            results = []
            for rule in matching_rules:
                result = await self._process_alert_with_rule(alert, rule)
                results.append(result)
            
            # Store active alert
            self.active_alerts[alert.alert_id] = alert
            
            return {
                "status": "triggered",
                "alert_id": alert.alert_id,
                "matching_rules": len(matching_rules),
                "processing_results": results
            }
            
        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
            raise

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> Dict[str, Any]:
        """Acknowledge alert"""



        try:
            if alert_id not in self.active_alerts:
                return {"status": "not_found", "message": "Alert not found"}
            
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.utcnow()
            
            # Update in Redis
            await self.redis_client.hset(
                "active_alerts", 
                alert_id, 
                json.dumps(alert.__dict__, default=str)
            )
            
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
            return {
                "status": "acknowledged",
                "alert_id": alert_id,
                "acknowledged_by": acknowledged_by,
                "acknowledged_at": alert.acknowledged_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            raise

    async def resolve_alert(self, alert_id: str, resolved_by: str) -> Dict[str, Any]:
        """Resolve alert"""



        try:
            if alert_id not in self.active_alerts:
                return {"status": "not_found", "message": "Alert not found"}
            
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()
            
            # Move from active to resolved
            await self.redis_client.hdel("active_alerts", alert_id)
            await self.redis_client.hset(
                "resolved_alerts", 
                alert_id, 
                json.dumps(alert.__dict__, default=str)
            )
            
            del self.active_alerts[alert_id]
            
            logger.info(f"Alert {alert_id} resolved by {resolved_by}")
            return {
                "status": "resolved",
                "alert_id": alert_id,
                "resolved_by": resolved_by,
                "resolved_at": alert.resolved_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            raise

    async def get_active_alerts(self, 
                               category: Optional[AlertCategory] = None,
                               severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get active alerts with optional filtering"""
        alerts = list(self.active_alerts.values())
        
        if category:
            alerts = [a for a in alerts if a.category == category]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)

    async def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert system statistics"""



        try:
            active_count = len(self.active_alerts)
            
            # Count by severity
            severity_counts = {}
            for severity in AlertSeverity:
                count = len([a for a in self.active_alerts.values() if a.severity == severity])
                severity_counts[severity.value] = count
            
            # Count by category
            category_counts = {}
            for category in AlertCategory:
                count = len([a for a in self.active_alerts.values() if a.category == category])
                category_counts[category.value] = count
            
            # Redis statistics
            redis_stats = await self._get_redis_statistics()
            
            return {
                "active_alerts": active_count,
                "severity_breakdown": severity_counts,
                "category_breakdown": category_counts,
                "alert_rules": len(self.alert_rules),
                "channels_configured": len(self.channels),
                "redis_statistics": redis_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get alert statistics: {e}")
            raise

    # Private helper methods
    
    def _initialize_channels(self):
        """Initialize alert delivery channels"""
        if self.spec.email_config:
            self.channels[AlertChannel.EMAIL] = EmailAlertChannel(self.spec.email_config)
        
        if self.spec.webhook_config:
            self.channels[AlertChannel.WEBHOOK] = WebhookAlertChannel(self.spec.webhook_config)
        
        if self.spec.websocket_port:
            self.channels[AlertChannel.WEBSOCKET] = WebSocketAlertChannel(self.spec.websocket_port)
        
        if self.spec.slack_config:
            self.channels[AlertChannel.SLACK] = SlackAlertChannel(self.spec.slack_config)

    async def _setup_alert_channels(self) -> Dict[str, Any]:
        """Setup all alert delivery channels"""
        results = {}
        
        for channel_type, channel in self.channels.items():
            try:
                if channel_type == AlertChannel.WEBSOCKET:
                    await channel.start_server()
                
                results[channel_type.value] = {
                    "status": "initialized",
                    "type": channel.__class__.__name__
                }
            except Exception as e:
                results[channel_type.value] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        return results

    async def _setup_alert_workers(self) -> Dict[str, Any]:
        """Setup alert processing workers"""



        return {
            "status": "configured",
            "max_concurrent_alerts": self.spec.max_concurrent_alerts,
            "worker_threads": 20
        }

    async def _setup_alert_rules_engine(self) -> Dict[str, Any]:
        """Setup alert rules engine"""



        return {
            "status": "configured",
            "rules_loaded": len(self.alert_rules),
            "escalation_enabled": self.spec.enable_escalation
        }

    async def _setup_alert_monitoring(self) -> Dict[str, Any]:
        """Setup alert system monitoring"""



        return {
            "status": "configured",
            "retention_days": self.spec.alert_retention_days,
            "rate_limiting": self.spec.rate_limiting
        }

    async def _validate_alert_rule(self, rule: AlertRule) -> Dict[str, Any]:
        """Validate alert rule configuration"""
        errors = []
        
        if not rule.name:
            errors.append("Rule name is required")
        
        if not rule.channels:
            errors.append("At least one alert channel is required")
        
        if not rule.recipients:
            errors.append("At least one recipient is required")
        
        for channel in rule.channels:
            if channel not in self.channels:
                errors.append(f"Channel {channel.value} is not configured")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }

    async def _check_rate_limit(self, alert: Alert) -> bool:
        """Check if alert passes rate limiting"""
        if not self.spec.rate_limiting:
            return True
        
        current_minute = datetime.utcnow().replace(second=0, microsecond=0)
        key = f"{alert.category.value}:{current_minute}"
        
        current_count = self.rate_limiter.get(key, 0)
        if current_count >= self.spec.max_alerts_per_minute:
            return False
        
        self.rate_limiter[key] = current_count + 1
        return True

    async def _find_matching_rules(self, alert: Alert) -> List[AlertRule]:
        """Find alert rules that match the alert"""
        matching_rules = []
        
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue
            
            # Check cooldown period
            if await self._is_rule_in_cooldown(rule, alert):
                continue
            
            # Check if rule matches alert
            if await self._rule_matches_alert(rule, alert):
                matching_rules.append(rule)
        
        return matching_rules

    async def _rule_matches_alert(self, rule: AlertRule, alert: Alert) -> bool:
        """Check if alert rule matches alert"""
        # Basic matching by category
        if rule.category != alert.category:
            return False
        
        # Check severity threshold
        severity_levels = {
            AlertSeverity.LOW: 1,
            AlertSeverity.MEDIUM: 2,
            AlertSeverity.HIGH: 3,
            AlertSeverity.CRITICAL: 4,
            AlertSeverity.EMERGENCY: 5
        }
        
        if severity_levels[alert.severity] < severity_levels[rule.severity]:
            return False
        
        return True

    async def _is_rule_in_cooldown(self, rule: AlertRule, alert: Alert) -> bool:
        """Check if rule is in cooldown period"""
        cooldown_key = f"cooldown:{rule.rule_id}:{alert.category.value}"
        last_triggered = await self.redis_client.get(cooldown_key)
        
        if last_triggered:
            last_time = datetime.fromisoformat(last_triggered.decode())
            if datetime.utcnow() - last_time < rule.cooldown_period:
                return True
        
        return False

    async def _process_alert_with_rule(self, alert: Alert, rule: AlertRule) -> Dict[str, Any]:
        """Process alert using specific rule"""



        try:
            # Update alert with rule information
            alert.rule_id = rule.rule_id
            alert.channels = rule.channels
            alert.recipients = rule.recipients
            
            # Send alert through all configured channels
            delivery_results = {}
            for channel in rule.channels:
                if channel in self.channels:
                    result = await self.channels[channel].send_alert(alert)
                    delivery_results[channel.value] = result
            
            alert.delivery_results = delivery_results
            alert.status = AlertStatus.SENT
            
            # Update cooldown
            cooldown_key = f"cooldown:{rule.rule_id}:{alert.category.value}"
            await self.redis_client.setex(
                cooldown_key, 
                int(rule.cooldown_period.total_seconds()),
                datetime.utcnow().isoformat()
            )
            
            return {
                "status": "processed",
                "rule_id": rule.rule_id,
                "channels_sent": len(delivery_results),
                "delivery_results": delivery_results
            }
            
        except Exception as e:
            logger.error(f"Failed to process alert with rule {rule.rule_id}: {e}")
            return {
                "status": "failed",
                "rule_id": rule.rule_id,
                "error": str(e)
            }

    async def _get_redis_statistics(self) -> Dict[str, Any]:
        """Get Redis statistics"""



        try:
            info = await self.redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0)
            }
        except Exception:
            return {"status": "unavailable"}

# Export main class
__all__ = [
    'RealTimeAlertInfrastructureManager',
    'AlertSeverity',
    'AlertCategory',
    'AlertChannel',
    'AlertStatus',
    'AlertRule',
    'Alert',
    'AlertInfrastructureSpec'
]
