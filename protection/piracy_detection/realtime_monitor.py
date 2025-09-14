"""📡 Real-time Violation Monitor
=============================

Advanced real-time monitoring system for content violation detection and alerting.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚖️ LEGAL WARNING: This software is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or reverse engineering is strictly prohibited
and will result in immediate legal action under German and international copyright law.

Team Specialties:
- Lead Dev IA: Advanced AI algorithms and machine learning models
- Backend Senior: Scalable microservices architecture  
- ML Engineer: Deep learning and neural network optimization
- DBA: High-performance database design and optimization
- Security Expert: Enterprise-grade security and encryption
- Microservices Architect: Distributed systems and API design
- Audio Engineer: Advanced audio processing and fingerprinting
- DevOps Engineer: CI/CD, monitoring, and infrastructure automation
- IA Prompt Engineer: Intelligent prompt design and optimization

Contact: mlaiel@live.de for licensing inquiries.

This module provides:
- Real-time violation detection and alerting
- WebSocket-based live monitoring dashboard
- Automated escalation and response systems
- Multi-channel notification delivery
- Advanced threat intelligence integration
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import websockets
from websockets.server import WebSocketServerProtocol
import aiohttp
import aioredis
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """
Alert severity levels."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ViolationType(Enum):
    """Types of violations detected."""

    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    TRADEMARK_VIOLATION = "trademark_violation"
    UNAUTHORIZED_DISTRIBUTION = "unauthorized_distribution"
    CONTENT_THEFT = "content_theft"
    DEEP_FAKE_DETECTION = "deep_fake_detection"
    WATERMARK_REMOVAL = "watermark_removal"
    METADATA_TAMPERING = "metadata_tampering"

class NotificationChannel(Enum):
    """Notification delivery channels."""

    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    PUSH_NOTIFICATION = "push_notification"
    WEBSOCKET = "websocket"

class MonitoringStatus(Enum):
    """Monitoring system status."""

    ACTIVE = "active"
    PAUSED = "paused"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    INITIALIZING = "initializing"

@dataclass
class ViolationAlert:
    """Real-time violation alert."""
    alert_id: str
    violation_type: ViolationType
    severity: AlertSeverity
    content_id: str
    platform: str
    detected_url: str
    confidence_score: float
    detection_timestamp: datetime
    alert_timestamp: datetime
    evidence_data: Dict[str, Any]
    affected_rights_holder: str
    estimated_impact: Dict[str, Any]
    recommended_actions: List[str]
    escalation_level: int

@dataclass
class MonitoringRule:
    """
Rule for monitoring and alerting."""
    rule_id: str
    rule_name: str
    description: str
    conditions: Dict[str, Any]
    severity: AlertSeverity
    notification_channels: List[NotificationChannel]
    escalation_rules: List[Dict[str, Any]]
    cooldown_minutes: int
    active: bool
    created_by: str
    created_at: datetime

@dataclass
class NotificationTemplate:
    """
Template for notifications."""
    template_id: str
    channel: NotificationChannel
    severity: AlertSeverity
    subject_template: str
    body_template: str
    variables: List[str]
    format_type: str  # 'text', 'html', 'json'

@dataclass
class EscalationPolicy:
    """
Escalation policy for alerts."""
    policy_id: str
    name: str
    levels: List[Dict[str, Any]]
    max_escalation_level: int
    escalation_interval_minutes: int
    notification_channels: Dict[int, List[NotificationChannel]]
    active: bool

class WebSocketManager:
    """
Manages WebSocket connections for real-time updates."""
    
    def __init__(self) -> None:
        self.connections: Set[WebSocketServerProtocol] = set()
        self.subscriptions: Dict[str, Set[WebSocketServerProtocol]] = defaultdict(set)
    
    def add_connection(self, websocket -> None: WebSocketServerProtocol) -> None:
        """
Add new WebSocket connection."""
        self.connections.add(websocket)
        logger.info(f"WebSocket connection added: {websocket.remote_address}")
    
    def remove_connection(self, websocket -> None: WebSocketServerProtocol) -> None:
        """Remove WebSocket connection."""
        self.connections.discard(websocket)
        
        # Remove from all subscriptions
        for topic_connections in self.subscriptions.values():
            topic_connections.discard(websocket)
        
        logger.info(f"WebSocket connection removed: {websocket.remote_address}")
    
    def subscribe_to_topic(self, websocket -> None: WebSocketServerProtocol, topic -> None: str) -> None:
        """Subscribe connection to specific topic."""
        self.subscriptions[topic].add(websocket)
        logger.info(f"WebSocket subscribed to topic {topic}: {websocket.remote_address}")
    
    def unsubscribe_from_topic(self, websocket -> None: WebSocketServerProtocol, topic -> None: str) -> None:
        """Unsubscribe connection from topic."""
        self.subscriptions[topic].discard(websocket)
    
    async def broadcast_to_all(self, message -> None: Dict[str, Any]) -> None:
        """
Broadcast message to all connected clients."""
        if not self.connections:
            return
        
        message_json = json.dumps(message, default=str)
        disconnected = set()
        
        for websocket in self.connections:
            try:
                await websocket.send(message_json)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(websocket)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            self.remove_connection(websocket)
    
    async def broadcast_to_topic(self, topic -> None: str, message -> None: Dict[str, Any]) -> None:
        """Broadcast message to subscribers of specific topic."""
        topic_connections = self.subscriptions.get(topic, set())
        if not topic_connections:
            return
        
        message_json = json.dumps(message, default=str)
        disconnected = set()
        
        for websocket in topic_connections:
            try:
                await websocket.send(message_json)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(websocket)
            except Exception as e:
                logger.error(f"Error broadcasting to topic {topic}: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            self.remove_connection(websocket)

class NotificationService:
    """Handles multi-channel notifications."""
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        self.config = config
        self.templates = {}
        self._load_notification_templates()
    
    def _load_notification_templates(self) -> None:
        """
Load notification templates."""
        self.templates = {
            'copyright_violation_email': NotificationTemplate(
                template_id='copyright_violation_email',
                channel=NotificationChannel.EMAIL,
                severity=AlertSeverity.HIGH,
                subject_template='Copyright Violation Detected - {content_id}',
                body_template='''
                A copyright violation has been detected:
                
                Content ID: {content_id}
                Platform: {platform}
                Detected URL: {detected_url}
                Confidence Score: {confidence_score}%
                Detection Time: {detection_timestamp}
                
                Recommended Actions:
                {recommended_actions}
                
                Please review this violation and take appropriate action.
                ''',
                variables=['content_id', 'platform', 'detected_url', 'confidence_score', 
                          'detection_timestamp', 'recommended_actions'],
                format_type='text'
            ),
            
            'critical_alert_slack': NotificationTemplate(
                template_id='critical_alert_slack',
                channel=NotificationChannel.SLACK,
                severity=AlertSeverity.CRITICAL,
                subject_template='🚨 CRITICAL: Content Violation Detected',
                body_template='''
                {
                    "text": "🚨 CRITICAL VIOLATION DETECTED",
                    "attachments": [
                        {
                            "color": "danger",
                            "fields": [
                                {"title": "Content ID", "value": "{content_id}", "short": true},
                                {"title": "Platform", "value": "{platform}", "short": true},
                                {"title": "Confidence", "value": "{confidence_score}%", "short": true},
                                {"title": "URL", "value": "{detected_url}", "short": false}
                            ]
                        }
                    ]
                }
                ''',
                variables=['content_id', 'platform', 'detected_url', 'confidence_score'],
                format_type='json'
            )
        }
    
    async def send_notification(self, 
                              channel: NotificationChannel,
                              template_id: str,
                              variables: Dict[str, Any],
                              recipient: str) -> bool:
        """Send notification through specified channel."""
        try:
            template = self.templates.get(template_id)
            if not template or template.channel != channel:
                logger.error(f"Template not found or channel mismatch: {template_id}")
                return False
            
            # Format message
            subject = template.subject_template.format(**variables)
            body = template.body_template.format(**variables)
            
            # Send based on channel
            if channel == NotificationChannel.EMAIL:
                return await self._send_email(recipient, subject, body)
            elif channel == NotificationChannel.SLACK:
                return await self._send_slack_message(recipient, body)
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook(recipient, {'subject': subject, 'body': body})
            else:
                logger.warning(f"Notification channel not implemented: {channel}")
                return False
            
        except Exception as e:
            logger.error(f"Notification sending failed: {e}")
            return False
    
    async def _send_email(self, recipient: str, subject: str, body: str) -> bool:
        """Send email notification."""
        # Implementation would use actual email service
        logger.info(f"EMAIL to {recipient}: {subject}")
        return True
    
    async def _send_slack_message(self, webhook_url: str, message: str) -> bool:
        """Send Slack notification."""
        try:
            async with aiohttp.ClientSession() as session:
                if message.startswith('{'):
                    # JSON format
                    headers = {'Content-Type': 'application/json'}
                    data = message
                else:
                    # Text format
                    headers = {'Content-Type': 'application/json'}
                    data = json.dumps({'text': message})
                
                async with session.post(webhook_url, data=data, headers=headers) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
            return False
    
    async def _send_webhook(self, url: str, payload: Dict[str, Any]) -> bool:
        """Send webhook notification."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")
            return False

class AlertEngine:
    """Processes violations and generates alerts."""
    
    def __init__(self, notification_service -> None: NotificationService) -> None:
        self.notification_service = notification_service
        self.monitoring_rules = {}
        self.escalation_policies = {}
        self.alert_history = {}
        self.active_alerts = {}
    
    def add_monitoring_rule(self, rule -> None: MonitoringRule) -> None:
        """
Add new monitoring rule."""
        self.monitoring_rules[rule.rule_id] = rule
        logger.info(f"Monitoring rule added: {rule.rule_name}")
    
    def add_escalation_policy(self, policy -> None: EscalationPolicy) -> None:
        """Add escalation policy."""
        self.escalation_policies[policy.policy_id] = policy
        logger.info(f"Escalation policy added: {policy.name}")
    
    async def process_violation(self, violation_data: Dict[str, Any]) -> List[ViolationAlert]:
        """Process violation and generate alerts."""
        alerts = []
        
        try:
            # Check against monitoring rules
            for rule_id, rule in self.monitoring_rules.items():
                if not rule.active:
                    continue
                
                if await self._matches_rule_conditions(violation_data, rule):
                    alert = await self._create_alert(violation_data, rule)
                    alerts.append(alert)
                    
                    # Check cooldown
                    if await self._is_in_cooldown(rule_id, violation_data):
                        continue
                    
                    # Send notifications
                    await self._send_rule_notifications(alert, rule)
                    
                    # Store alert
                    self.active_alerts[alert.alert_id] = alert
                    
                    # Start escalation if configured
                    if rule.escalation_rules:
                        await self._start_escalation(alert, rule)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Violation processing failed: {e}")
            return []
    
    async def _matches_rule_conditions(self, violation_data: Dict[str, Any], rule: MonitoringRule) -> bool:
        """Check if violation matches rule conditions."""
        conditions = rule.conditions
        
        # Check violation type
        if 'violation_types' in conditions:
            violation_type = violation_data.get('violation_type')
            if violation_type not in conditions['violation_types']:
                return False
        
        # Check confidence threshold
        if 'min_confidence' in conditions:
            confidence = violation_data.get('confidence_score', 0)
            if confidence < conditions['min_confidence']:
                return False
        
        # Check platform filter
        if 'platforms' in conditions:
            platform = violation_data.get('platform')
            if platform not in conditions['platforms']:
                return False
        
        # Check content filter
        if 'content_ids' in conditions:
            content_id = violation_data.get('content_id')
            if content_id not in conditions['content_ids']:
                return False
        
        return True
    
    async def _create_alert(self, violation_data: Dict[str, Any], rule: MonitoringRule) -> ViolationAlert:
        """
Create violation alert."""
        alert_id = f"alert_{rule.rule_id}_{int(datetime.now().timestamp())}"
        
        # Calculate recommended actions
        recommended_actions = self._generate_recommended_actions(violation_data, rule)
        
        # Estimate impact
        estimated_impact = await self._estimate_violation_impact(violation_data)
        
        alert = ViolationAlert(
            alert_id=alert_id,
            violation_type=ViolationType(violation_data.get('violation_type', 'content_theft')),
            severity=rule.severity,
            content_id=violation_data.get('content_id', ''),
            platform=violation_data.get('platform', ''),
            detected_url=violation_data.get('detected_url', ''),
            confidence_score=violation_data.get('confidence_score', 0.0),
            detection_timestamp=datetime.fromisoformat(violation_data.get('detection_timestamp', datetime.now().isoformat())),
            alert_timestamp=datetime.now(),
            evidence_data=violation_data.get('evidence_data', {}),
            affected_rights_holder=violation_data.get('rights_holder', ''),
            estimated_impact=estimated_impact,
            recommended_actions=recommended_actions,
            escalation_level=0
        )
        
        return alert
    
    def _generate_recommended_actions(self, violation_data: Dict[str, Any], rule: MonitoringRule) -> List[str]:
        """Generate recommended actions based on violation."""
        actions = []
        
        confidence = violation_data.get('confidence_score', 0)
        violation_type = violation_data.get('violation_type')
        
        if confidence > 0.9:
            actions.append("Initiate immediate takedown request")
        elif confidence > 0.7:
            actions.append("Conduct manual review and verification")
        else:
            actions.append("Perform additional analysis to confirm violation")
        
        if violation_type == 'copyright_infringement':
            actions.append("Prepare DMCA takedown notice")
            actions.append("Document evidence for legal proceedings")
        elif violation_type == 'deep_fake_detection':
            actions.append("Alert content authenticity team")
            actions.append("Consider platform-specific reporting mechanisms")
        
        if rule.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            actions.append("Escalate to legal team")
            actions.append("Consider emergency injunction if applicable")
        
        return actions
    
    async def _estimate_violation_impact(self, violation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate impact of violation."""
        # Simplified impact estimation
        confidence = violation_data.get('confidence_score', 0)
        
        impact = {
            'revenue_risk': 'low',
            'brand_risk': 'low',
            'legal_risk': 'low',
            'estimated_monetary_impact': 0
        }
        
        if confidence > 0.8:
            impact['revenue_risk'] = 'high'
            impact['brand_risk'] = 'medium'
            impact['legal_risk'] = 'medium'
            impact['estimated_monetary_impact'] = 1000  # Placeholder
        elif confidence > 0.6:
            impact['revenue_risk'] = 'medium'
            impact['brand_risk'] = 'low'
            impact['legal_risk'] = 'low'
            impact['estimated_monetary_impact'] = 500
        
        return impact
    
    async def _is_in_cooldown(self, rule_id: str, violation_data: Dict[str, Any]) -> bool:
        """
Check if rule is in cooldown period."""
        rule = self.monitoring_rules.get(rule_id)
        if not rule or rule.cooldown_minutes <= 0:
            return False
        
        # Check recent alerts for same content/platform combination
        content_id = violation_data.get('content_id')
        platform = violation_data.get('platform')
        
        cutoff_time = datetime.now() - timedelta(minutes=rule.cooldown_minutes)
        
        for alert in self.active_alerts.values():
            if (alert.content_id == content_id and 
                alert.platform == platform and
                alert.alert_timestamp > cutoff_time):
                return True
        
        return False
    
    async def _send_rule_notifications(self, alert -> None: ViolationAlert, rule -> None: MonitoringRule) -> None:
        """
Send notifications for rule-triggered alert."""
        for channel in rule.notification_channels:
            try:
                template_id = f"{alert.violation_type.value}_{channel.value}"
                
                # Fallback to generic template
                if template_id not in self.notification_service.templates:
                    if channel == NotificationChannel.EMAIL:
                        template_id = 'copyright_violation_email'
                    elif channel == NotificationChannel.SLACK:
                        template_id = 'critical_alert_slack'
                    else:
                        continue
                
                variables = {
                    'content_id': alert.content_id,
                    'platform': alert.platform,
                    'detected_url': alert.detected_url,
                    'confidence_score': int(alert.confidence_score * 100),
                    'detection_timestamp': alert.detection_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'),
                    'recommended_actions': '\n'.join(f"• {action}" for action in alert.recommended_actions)
                }
                
                # Get recipient from rule configuration
                recipient = rule.conditions.get(f'{channel.value}_recipient', 'default@example.com')
                
                await self.notification_service.send_notification(
                    channel, template_id, variables, recipient
                )
                
            except Exception as e:
                logger.error(f"Failed to send {channel.value} notification: {e}")
    
    async def _start_escalation(self, alert -> None: ViolationAlert, rule -> None: MonitoringRule) -> None:
        """Start escalation process for alert."""
        # Implementation would handle escalation logic
        logger.info(f"Starting escalation for alert: {alert.alert_id}")

class RealtimeViolationMonitor:
    """
    Real-time violation monitoring and alerting system.
    
    Provides comprehensive real-time monitoring capabilities for content violations
    with advanced alerting, escalation, and notification features.
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the Real-time Violation Monitor.
        
        Args:
            config: Monitor configuration parameters
        """
        self.config = config or {}
        self._initialized = False
        
        # Initialize components
        self.websocket_manager = WebSocketManager()
        self.notification_service = NotificationService(self.config.get('notifications', {}))
        self.alert_engine = AlertEngine(self.notification_service)
        
        # Redis for real-time data
        self.redis_client = None
        
        # Monitoring state
        self.status = MonitoringStatus.INITIALIZING
        self.monitoring_tasks = {}
        self.violation_queue = asyncio.Queue()
        
        # WebSocket server
        self.websocket_server = None
        self.websocket_port = self.config.get('websocket_port', 8765)
        
        # Statistics
        self.monitor_stats = {
            'total_violations_processed': 0,
            'alerts_generated': 0,
            'notifications_sent': 0,
            'active_connections': 0,
            'uptime_start': datetime.now()
        }
        
        logger.info("Real-time Violation Monitor initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize monitoring components.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Initialize Redis connection
            redis_config = self.config.get('redis', {})
            if redis_config:
                self.redis_client = await aioredis.from_url(
                    redis_config.get('url', 'redis://localhost:6379')
                )
            
            # Start WebSocket server
            await self._start_websocket_server()
            
            # Start violation processing task
            asyncio.create_task(self._process_violation_queue())
            
            self.status = MonitoringStatus.ACTIVE
            self._initialized = True
            
            logger.info("Real-time violation monitor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize violation monitor: {e}")
            self.status = MonitoringStatus.ERROR
            return False
    
    async def start_monitoring(self, content_ids: List[str]) -> bool:
        """
        Start monitoring for specific content.
        
        Args:
            content_ids: List of content IDs to monitor
            
        Returns:
            bool: True if monitoring started successfully
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            for content_id in content_ids:
                if content_id not in self.monitoring_tasks:
                    task = asyncio.create_task(self._monitor_content(content_id))
                    self.monitoring_tasks[content_id] = task
                    logger.info(f"Started monitoring for content: {content_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            return False
    
    async def submit_violation(self, violation_data: Dict[str, Any]) -> str:
        """
        Submit violation for real-time processing.
        
        Args:
            violation_data: Violation information
            
        Returns:
            Processing ID
        """
        try:
            processing_id = f"proc_{int(datetime.now().timestamp())}"
            violation_data['processing_id'] = processing_id
            violation_data['submission_timestamp'] = datetime.now().isoformat()
            
            await self.violation_queue.put(violation_data)
            
            # Broadcast to WebSocket clients
            await self.websocket_manager.broadcast_to_topic('violations', {
                'type': 'violation_submitted',
                'processing_id': processing_id,
                'content_id': violation_data.get('content_id'),
                'timestamp': violation_data['submission_timestamp']
            })
            
            return processing_id
            
        except Exception as e:
            logger.error(f"Violation submission failed: {e}")
            raise
    
    async def _start_websocket_server(self) -> None:
        try:
            logger.info(f"Executing _start_websocket_server")
            
            # Implementation for _start_websocket_server
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_start_websocket_server completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_start_websocket_server failed: {e}")
            raise
    async def _handle_websocket_message(self, websocket -> None: WebSocketServerProtocol, message -> None: str) -> None:
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                topic = data.get('topic', 'violations')
                self.websocket_manager.subscribe_to_topic(websocket, topic)
                await websocket.send(json.dumps({
                    'type': 'subscription_confirmed',
                    'topic': topic
                }))
            
            elif message_type == 'unsubscribe':
                topic = data.get('topic')
                if topic:
                    self.websocket_manager.unsubscribe_from_topic(websocket, topic)
            
            elif message_type == 'ping':
                await websocket.send(json.dumps({'type': 'pong'}))
            
        except Exception as e:
            logger.error(f"WebSocket message handling failed: {e}")
    
    async def _process_violation_queue(self) -> None:
        """Process violations from queue."""
        while True:
            try:
                violation_data = await self.violation_queue.get()
                
                # Process violation through alert engine
                alerts = await self.alert_engine.process_violation(violation_data)
                
                # Update statistics
                self.monitor_stats['total_violations_processed'] += 1
                self.monitor_stats['alerts_generated'] += len(alerts)
                
                # Broadcast alerts to WebSocket clients
                for alert in alerts:
                    await self.websocket_manager.broadcast_to_topic('alerts', {
                        'type': 'alert_generated',
                        'alert': asdict(alert)
                    })
                
                # Store in Redis if available
                if self.redis_client:
                    await self._store_violation_in_redis(violation_data, alerts)
                
                self.violation_queue.task_done()
                
            except Exception as e:
                logger.error(f"Violation processing error: {e}")
                await asyncio.sleep(1)
    
    async def _monitor_content(self, content_id -> None: str) -> None:
        """Monitor specific content for violations."""
        while content_id in self.monitoring_tasks:
            try:
                # This would integrate with detection systems
                # For now, it's a placeholder
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Content monitoring error for {content_id}: {e}")
                await asyncio.sleep(60)
    
    async def _store_violation_in_redis(self, violation_data -> None: Dict[str, Any], alerts -> None: List[ViolationAlert]) -> None:
        """Store violation and alerts in Redis."""
        try:
            # Store violation data
            violation_key = f"violation:{violation_data['processing_id']}"
            await self.redis_client.setex(
                violation_key, 
                timedelta(days=30).total_seconds(),
                json.dumps(violation_data, default=str)
            )
            
            # Store alerts
            for alert in alerts:
                alert_key = f"alert:{alert.alert_id}"
                await self.redis_client.setex(
                    alert_key,
                    timedelta(days=30).total_seconds(),
                    json.dumps(asdict(alert), default=str)
                )
            
        except Exception as e:
            logger.error(f"Redis storage failed: {e}")
    
    async def get_real_time_statistics(self) -> Dict[str, Any]:
        """Get real-time monitoring statistics."""
        uptime = datetime.now() - self.monitor_stats['uptime_start']
        
        return {
            **self.monitor_stats,
            'status': self.status.value,
            'active_connections': len(self.websocket_manager.connections),
            'monitored_content_count': len(self.monitoring_tasks),
            'queue_size': self.violation_queue.qsize(),
            'uptime_hours': uptime.total_seconds() / 3600,
            'initialized': self._initialized
        }
    
    async def shutdown(self) -> None:
        """
Gracefully shutdown monitoring system."""
        try:
            self.status = MonitoringStatus.MAINTENANCE
            
            # Cancel monitoring tasks
            for task in self.monitoring_tasks.values():
                task.cancel()
            
            # Close WebSocket server
            if self.websocket_server:
                self.websocket_server.close()
                await self.websocket_server.wait_closed()
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Real-time violation monitor shutdown complete")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
    
    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return {
            **self.monitor_stats,
            'status': self.status.value,
            'monitoring_rules_count': len(self.alert_engine.monitoring_rules),
            'escalation_policies_count': len(self.alert_engine.escalation_policies),
            'active_alerts_count': len(self.alert_engine.active_alerts),
            'websocket_connections': len(self.websocket_manager.connections),
            'initialized': self._initialized
        }
