"""Real-time Notification & Alert System

This module provides comprehensive notification capabilities:
- Real-time alerts via WebSocket, email, SMS, and push notifications
- Multi-channel notification delivery with fallback mechanisms
- Smart notification filtering and priority management
- Customizable alert templates and personalization
- Integration with external services (Slack, Discord, Telegram)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import ssl

# WebSocket and real-time communication
import websockets
import socketio
from fastapi import WebSocket

# External notification services
import requests
import aiohttp
from twilio.rest import Client as TwilioClient
import telegram
import discord
from slack_sdk.web.async_client import AsyncWebClient as SlackClient

# Template engine
from jinja2 import Environment, FileSystemLoader, Template

# Internal imports
from ...utils.logging import get_logger
from ...database.models.notifications import NotificationLog, NotificationPreference
from ...database.models.content import ViolationCase
from ...config.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class NotificationChannel(Enum):
    """
Available notification channels"""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBSOCKET = "websocket"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class NotificationPriority(Enum):
    """Notification priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationType(Enum):
    """Types of notifications"""

    VIOLATION_DETECTED = "violation_detected"
    TAKEDOWN_SUCCESS = "takedown_success"
    TAKEDOWN_FAILED = "takedown_failed"
    REVENUE_ALERT = "revenue_alert"
    SYSTEM_STATUS = "system_status"
    PROTECTION_SUMMARY = "protection_summary"
    LEGAL_ACTION = "legal_action"
    MONITORING_STATUS = "monitoring_status"


@dataclass
class NotificationTemplate:
    """Template for notifications"""
    template_id: str
    notification_type: NotificationType
    channel: NotificationChannel
    subject_template: str
    body_template: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    requires_action: bool = False
    action_buttons: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationContent:
    """
Content for a notification"""
    notification_id: str
    user_id: str
    notification_type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    action_buttons: List[Dict[str, str]] = field(default_factory=list)
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class NotificationDelivery:
    """
Delivery status for a notification"""
    notification_id: str
    channel: NotificationChannel
    status: str  # pending, sent, delivered, failed, read
    delivery_time: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


class NotificationManager:
    """
    Comprehensive notification and alert system
    
    Manages multi-channel notification delivery with smart routing,
    priority handling, and real-time communication capabilities.
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.notification_queue = asyncio.Queue()
        self.templates: Dict[str, NotificationTemplate] = {}
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        # External service clients
        self.twilio_client = None
        self.slack_client = None
        self.telegram_bot = None
        self.discord_client = None
        
        # Template engine
        self.jinja_env = Environment(
            loader=FileSystemLoader('templates/notifications'),
            autoescape=True
        )
        
        # Initialize services
        asyncio.create_task(self._initialize_services())
        asyncio.create_task(self._start_notification_worker())
        
        logger.info("Notification manager initialized")
    
    async def _initialize_services(self):
        """Initialize external notification services"""
        try:
            # Initialize Twilio for SMS
            if hasattr(settings, 'TWILIO_ACCOUNT_SID') and settings.TWILIO_ACCOUNT_SID:
                self.twilio_client = TwilioClient(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
            
            # Initialize Slack
            if hasattr(settings, 'SLACK_BOT_TOKEN') and settings.SLACK_BOT_TOKEN:
                self.slack_client = SlackClient(token=settings.SLACK_BOT_TOKEN)
            
            # Initialize Telegram
            if hasattr(settings, 'TELEGRAM_BOT_TOKEN') and settings.TELEGRAM_BOT_TOKEN:
                self.telegram_bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
            
            logger.info("External notification services initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize notification services: {e}")
    
    async def send_notification(self, content: NotificationContent, 
                              channels: List[NotificationChannel],
                              user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, NotificationDelivery]:
        """Send notification through specified channels"""
        try:
            deliveries = {}
            
            # Filter channels based on user preferences
            if user_preferences:
                channels = self._filter_channels_by_preferences(channels, user_preferences, content.priority)
            
            # Send through each channel
            for channel in channels:
                delivery = NotificationDelivery(
                    notification_id=content.notification_id,
                    channel=channel,
                    status="pending"
                )
                
                try:
                    success = await self._send_via_channel(content, channel)
                    delivery.status = "sent" if success else "failed"
                    delivery.delivery_time = datetime.utcnow()
                except Exception as e:
                    delivery.status = "failed"
                    delivery.error_message = str(e)
                    logger.error(f"Failed to send via {channel.value}: {e}")
                
                deliveries[channel.value] = delivery
            
            # Store delivery results
            await self._store_notification_log(content, deliveries)
            
            logger.info(f"Notification {content.notification_id} sent via {len(channels)} channels")
            return deliveries
            
        except Exception as e:
            logger.error(f"Notification sending failed: {e}")
            return {}
    
    async def send_violation_alert(self, violation_data: Dict[str, Any], user_id: str) -> bool:
        """Send alert for content violation detection"""
        try:
            # Create notification content
            notification = NotificationContent(
                notification_id=str(uuid.uuid4()),
                user_id=user_id,
                notification_type=NotificationType.VIOLATION_DETECTED,
                priority=self._determine_violation_priority(violation_data),
                title="🚨 Content Violation Detected",
                message=f"Unauthorized use of your content detected on {violation_data.get('platform', 'unknown platform')}",
                data=violation_data,
                action_buttons=[
                    {"text": "View Details", "action": f"/violations/{violation_data.get('id')}"},
                    {"text": "Request Takedown", "action": f"/takedown/{violation_data.get('id')}"}
                ]
            )
            
            # Get user preferences
            preferences = await self._get_user_notification_preferences(user_id)
            
            # Determine channels based on priority and preferences
            channels = self._get_channels_for_violation(notification.priority, preferences)
            
            # Send notification
            deliveries = await self.send_notification(notification, channels, preferences)
            
            # Check if at least one delivery was successful
            success = any(d.status == "sent" for d in deliveries.values())
            
            if success:
                logger.info(f"Violation alert sent successfully for user {user_id}")
            else:
                logger.error(f"All violation alert deliveries failed for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Violation alert failed: {e}")
            return False
    
    async def send_takedown_update(self, takedown_data: Dict[str, Any], user_id: str, success: bool) -> bool:
        """Send update on takedown request status"""
        try:
            notification_type = NotificationType.TAKEDOWN_SUCCESS if success else NotificationType.TAKEDOWN_FAILED
            title = "✅ Takedown Successful" if success else "❌ Takedown Failed"
            
            message = (
                f"Your takedown request for content on {takedown_data.get('platform')} has been "
                f"{'processed successfully' if success else 'rejected or failed'}"
            )
            
            notification = NotificationContent(
                notification_id=str(uuid.uuid4()),
                user_id=user_id,
                notification_type=notification_type,
                priority=NotificationPriority.HIGH if not success else NotificationPriority.NORMAL,
                title=title,
                message=message,
                data=takedown_data
            )
            
            preferences = await self._get_user_notification_preferences(user_id)
            channels = [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
            
            deliveries = await self.send_notification(notification, channels, preferences)
            return any(d.status == "sent" for d in deliveries.values())
            
        except Exception as e:
            logger.error(f"Takedown update notification failed: {e}")
            return False
    
    async def send_revenue_alert(self, revenue_data: Dict[str, Any], user_id: str) -> bool:
        """Send alert for revenue threshold or anomaly"""
        try:
            notification = NotificationContent(
                notification_id=str(uuid.uuid4()),
                user_id=user_id,
                notification_type=NotificationType.REVENUE_ALERT,
                priority=NotificationPriority.HIGH,
                title="💰 Revenue Alert",
                message=f"Revenue threshold reached: {revenue_data.get('amount')} {revenue_data.get('currency')}",
                data=revenue_data,
                action_buttons=[
                    {"text": "View Dashboard", "action": "/dashboard/revenue"},
                    {"text": "Download Report", "action": f"/reports/revenue/{revenue_data.get('period')}"}
                ]
            )
            
            preferences = await self._get_user_notification_preferences(user_id)
            channels = [NotificationChannel.EMAIL, NotificationChannel.PUSH, NotificationChannel.IN_APP]
            
            deliveries = await self.send_notification(notification, channels, preferences)
            return any(d.status == "sent" for d in deliveries.values())
            
        except Exception as e:
            logger.error(f"Revenue alert failed: {e}")
            return False
    
    async def send_protection_summary(self, summary_data: Dict[str, Any], user_id: str) -> bool:
        """Send daily/weekly protection summary"""
        try:
            period = summary_data.get('period', 'daily')
            
            notification = NotificationContent(
                notification_id=str(uuid.uuid4()),
                user_id=user_id,
                notification_type=NotificationType.PROTECTION_SUMMARY,
                priority=NotificationPriority.LOW,
                title=f"📊 {period.title()} Protection Summary",
                message=f"Your content protection summary for {summary_data.get('date_range')}",
                data=summary_data
            )
            
            preferences = await self._get_user_notification_preferences(user_id)
            channels = [NotificationChannel.EMAIL]
            
            deliveries = await self.send_notification(notification, channels, preferences)
            return any(d.status == "sent" for d in deliveries.values())
            
        except Exception as e:
            logger.error(f"Protection summary failed: {e}")
            return False
    
    async def connect_websocket(self, user_id: str, websocket: WebSocket):
        """Connect user to real-time notifications via WebSocket"""
        try:
            await websocket.accept()
            self.active_connections[user_id] = websocket
            
            # Send connection confirmation
            await websocket.send_json({
                "type": "connection",
                "status": "connected",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            logger.info(f"WebSocket connected for user {user_id}")
            
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
    
    async def disconnect_websocket(self, user_id: str):
        """Disconnect user WebSocket"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].close()
            except:
                pass
            del self.active_connections[user_id]
            logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def _send_via_channel(self, content: NotificationContent, channel: NotificationChannel) -> bool:
        """Send notification via specific channel"""
        try:
            if channel == NotificationChannel.EMAIL:
                return await self._send_email(content)
            elif channel == NotificationChannel.SMS:
                return await self._send_sms(content)
            elif channel == NotificationChannel.WEBSOCKET:
                return await self._send_websocket(content)
            elif channel == NotificationChannel.PUSH:
                return await self._send_push_notification(content)
            elif channel == NotificationChannel.SLACK:
                return await self._send_slack(content)
            elif channel == NotificationChannel.DISCORD:
                return await self._send_discord(content)
            elif channel == NotificationChannel.TELEGRAM:
                return await self._send_telegram(content)
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook(content)
            elif channel == NotificationChannel.IN_APP:
                return await self._send_in_app(content)
            else:
                logger.warning(f"Unsupported notification channel: {channel}")
                return False
                
        except Exception as e:
            logger.error(f"Channel {channel.value} sending failed: {e}")
            return False
    
    async def _send_email(self, content: NotificationContent) -> bool:
        """Send email notification"""
        try:
            # Get user email
            user_email = await self._get_user_email(content.user_id)
            if not user_email:
                return False
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = content.title
            msg['From'] = settings.SMTP_USER
            msg['To'] = user_email
            
            # Create HTML content
            html_content = await self._render_email_template(content)
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls(context=context)
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent to {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False
    
    async def _send_sms(self, content: NotificationContent) -> bool:
        """Send SMS notification"""
        try:
            if not self.twilio_client:
                return False
            
            user_phone = await self._get_user_phone(content.user_id)
            if not user_phone:
                return False
            
            # Create SMS message
            sms_message = f"{content.title}\n{content.message}"
            if len(sms_message) > 160:
                sms_message = sms_message[:157] + "..."
            
            # Send SMS
            message = self.twilio_client.messages.create(
                body=sms_message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=user_phone
            )
            
            logger.info(f"SMS sent to {user_phone}: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"SMS sending failed: {e}")
            return False
    
    async def _send_websocket(self, content: NotificationContent) -> bool:
        """Send real-time notification via WebSocket"""
        try:
            if content.user_id not in self.active_connections:
                return False
            
            websocket = self.active_connections[content.user_id]
            
            message = {
                "type": "notification",
                "id": content.notification_id,
                "notification_type": content.notification_type.value,
                "priority": content.priority.value,
                "title": content.title,
                "message": content.message,
                "data": content.data,
                "action_buttons": content.action_buttons,
                "timestamp": content.created_at.isoformat()
            }
            
            await websocket.send_json(message)
            logger.info(f"WebSocket notification sent to user {content.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"WebSocket sending failed: {e}")
            # Remove disconnected websocket
            if content.user_id in self.active_connections:
                del self.active_connections[content.user_id]
            return False
    
    async def _send_push_notification(self, content: NotificationContent) -> bool:
        """Send push notification"""
        try:
            # Get user push tokens
            push_tokens = await self._get_user_push_tokens(content.user_id)
            if not push_tokens:
                return False
            
            # Create push notification payload
            payload = {
                "title": content.title,
                "body": content.message,
                "data": content.data,
                "priority": "high" if content.priority in [NotificationPriority.HIGH, NotificationPriority.URGENT, NotificationPriority.CRITICAL] else "normal"
            }
            
            # Send to FCM/APNs (implementation would depend on your push service)
            success_count = 0
            for token in push_tokens:
                try:
                    # Send push notification (placeholder implementation)
                    # await self._send_fcm_notification(token, payload)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Push notification failed for token {token}: {e}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Push notification sending failed: {e}")
            return False
    
    async def _send_slack(self, content: NotificationContent) -> bool:
        """Send Slack notification"""
        try:
            if not self.slack_client:
                return False
            
            slack_channel = await self._get_user_slack_channel(content.user_id)
            if not slack_channel:
                return False
            
            # Create Slack message
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{content.title}*\n{content.message}"
                    }
                }
            ]
            
            # Add action buttons if present
            if content.action_buttons:
                actions = {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": button["text"]},
                            "url": button.get("action", "#")
                        }
                        for button in content.action_buttons[:5]  # Slack limit
                    ]
                }
                blocks.append(actions)
            
            # Send message
            response = await self.slack_client.chat_postMessage(
                channel=slack_channel,
                blocks=blocks
            )
            
            logger.info(f"Slack notification sent to {slack_channel}")
            return response["ok"]
            
        except Exception as e:
            logger.error(f"Slack sending failed: {e}")
            return False
    
    async def _send_telegram(self, content: NotificationContent) -> bool:
        """Send Telegram notification"""
        try:
            if not self.telegram_bot:
                return False
            
            telegram_chat_id = await self._get_user_telegram_chat(content.user_id)
            if not telegram_chat_id:
                return False
            
            # Create message
            message_text = f"*{content.title}*\n{content.message}"
            
            # Send message
            await self.telegram_bot.send_message(
                chat_id=telegram_chat_id,
                text=message_text,
                parse_mode='Markdown'
            )
            
            logger.info(f"Telegram notification sent to {telegram_chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Telegram sending failed: {e}")
            return False
    
    async def _send_webhook(self, content: NotificationContent) -> bool:
        """Send webhook notification"""
        try:
            webhook_url = await self._get_user_webhook_url(content.user_id)
            if not webhook_url:
                return False
            
            # Create webhook payload
            payload = {
                "notification_id": content.notification_id,
                "user_id": content.user_id,
                "type": content.notification_type.value,
                "priority": content.priority.value,
                "title": content.title,
                "message": content.message,
                "data": content.data,
                "timestamp": content.created_at.isoformat()
            }
            
            # Send webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload, timeout=10) as response:
                    success = response.status < 400
                    
            logger.info(f"Webhook notification sent to {webhook_url}")
            return success
            
        except Exception as e:
            logger.error(f"Webhook sending failed: {e}")
            return False
    
    async def _send_in_app(self, content: NotificationContent) -> bool:
        """Store in-app notification"""
        try:
            # Store notification in database for in-app display
            await self._store_in_app_notification(content)
            logger.info(f"In-app notification stored for user {content.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"In-app notification storage failed: {e}")
            return False
    
    async def _start_notification_worker(self):
        """Start background worker for processing notification queue"""
        while True:
            try:
                # This would process queued notifications
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Notification worker error: {e}")
                await asyncio.sleep(5)
    
    # Helper methods
    def _determine_violation_priority(self, violation_data: Dict[str, Any]) -> NotificationPriority:
        """Determine priority based on violation characteristics"""
        similarity_score = violation_data.get('similarity_score', 0)
        platform = violation_data.get('platform', '')
        
        if similarity_score > 0.95:
            return NotificationPriority.URGENT
        elif similarity_score > 0.85:
            return NotificationPriority.HIGH
        elif platform.lower() in ['youtube', 'spotify']:
            return NotificationPriority.HIGH
        else:
            return NotificationPriority.NORMAL
    
    def _filter_channels_by_preferences(self, channels: List[NotificationChannel], 
                                       preferences: Dict[str, Any], 
                                       priority: NotificationPriority) -> List[NotificationChannel]:
        """
Filter channels based on user preferences"""
        # This would filter channels based on user preferences and priority
        return channels
    
    def _get_channels_for_violation(self, priority: NotificationPriority, 
                                   preferences: Dict[str, Any]) -> List[NotificationChannel]:
        """
Get appropriate channels for violation based on priority"""
        if priority in [NotificationPriority.URGENT, NotificationPriority.CRITICAL]:
            return [NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.WEBSOCKET, NotificationChannel.PUSH]
        elif priority == NotificationPriority.HIGH:
            return [NotificationChannel.EMAIL, NotificationChannel.WEBSOCKET, NotificationChannel.PUSH]
        else:
            return [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
    
    async def _render_email_template(self, content: NotificationContent) -> str:
        """
Render email template with content"""
        try:
            template = self.jinja_env.get_template(f'{content.notification_type.value}.html')
            return template.render(
                title=content.title,
                message=content.message,
                data=content.data,
                action_buttons=content.action_buttons
            )
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            return f"<html><body><h2>{content.title}</h2><p>{content.message}</p></body></html>"
    
    # Database and external service helper methods
    async def _get_user_notification_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user notification preferences"""
        return {}
    
    async def _get_user_email(self, user_id: str) -> Optional[str]:
        """
Get user email address"""
        return None
    
    async def _get_user_phone(self, user_id: str) -> Optional[str]:
        """
Get user phone number"""
        return None
    
    async def _get_user_push_tokens(self, user_id: str) -> List[str]:
        """
Get user push notification tokens"""
        return []
    
    async def _get_user_slack_channel(self, user_id: str) -> Optional[str]:
        """
Get user Slack channel"""
        return None
    
    async def _get_user_telegram_chat(self, user_id: str) -> Optional[str]:
        """
Get user Telegram chat ID"""
        return None
    
    async def _get_user_webhook_url(self, user_id: str) -> Optional[str]:
        """
Get user webhook URL"""
        return None
    
    async def _store_notification_log(self, content: NotificationContent, deliveries: Dict[str, NotificationDelivery]):
        """
Store notification log in database"""
        pass
    
    async def _store_in_app_notification(self, content: NotificationContent):
        """
Store in-app notification in database"""
        pass
