"""
IA Influencer Agent - Email & SMS Notification Manager
Enterprise notification delivery system for multi-channel communication

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

STRICT WARNING: This code is proprietary and confidential.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Legal action will be taken against violators.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + DevOps 
- Audio Processing + Security + Microservices + IA Prompt Engineering
"""

import asyncio
import logging
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional, Union

import aiofiles
import aiohttp
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field
from twilio.rest import Client as TwilioClient

from ...core.config import get_settings
from ...core.logging import get_logger
from ...database.models import User
from ...utils.template_renderer import TemplateRenderer

logger = get_logger(__name__)
settings = get_settings()


class EmailTemplate(BaseModel):
    """Email template configuration"""
    name: str = Field(..., description="Template name")
    subject: str = Field(..., description="Email subject")
    html_template: str = Field(..., description="HTML template path")
    text_template: Optional[str] = Field(None, description="Text template path")
    sender_name: str = Field(default="IA Influencer Agent", description="Sender name")
    priority: str = Field(default="normal", description="Email priority")


class SMSTemplate(BaseModel):
    """SMS template configuration"""
    name: str = Field(..., description="Template name")
    message: str = Field(..., description="SMS message template")
    max_length: int = Field(default=160, description="Maximum message length")


class NotificationPreferences(BaseModel):
    """User notification preferences"""
    user_id: str = Field(..., description="User ID")
    email_enabled: bool = Field(default=True, description="Email notifications enabled")
    sms_enabled: bool = Field(default=False, description="SMS notifications enabled")
    push_enabled: bool = Field(default=True, description="Push notifications enabled")
    protection_alerts: bool = Field(default=True, description="Content protection alerts")
    ai_updates: bool = Field(default=True, description="AI processing updates")
    revenue_notifications: bool = Field(default=True, description="Revenue notifications")
    collaboration_invites: bool = Field(default=True, description="Collaboration invites")
    marketing_emails: bool = Field(default=False, description="Marketing emails")
    frequency: str = Field(default="immediate", description="Notification frequency")


class EmailNotificationManager:
    """
    Enterprise email notification management system
    Handles templated emails, delivery tracking, and bounce management
    """

    def __init__(self):
        self.smtp_config = {
            "server": settings.SMTP_SERVER,
            "port": settings.SMTP_PORT,
            "username": settings.SMTP_USERNAME,
            "password": settings.SMTP_PASSWORD,
            "use_tls": settings.SMTP_USE_TLS,
            "use_ssl": settings.SMTP_USE_SSL
        }
        
        # Template environment
        template_dir = Path(__file__).parent.parent.parent / "templates" / "email"
        self.template_env = Environment(loader=FileSystemLoader(str(template_dir)))
        
        # Delivery tracking
        self.delivery_stats: Dict[str, int] = {
            "sent": 0,
            "delivered": 0,
            "bounced": 0,
            "failed": 0
        }

    async def send_email(
        self,
        recipient: str,
        template_name: str,
        context: Dict[str, any],
        sender_email: Optional[str] = None,
        sender_name: Optional[str] = None
    ) -> Dict[str, Union[bool, str]]:
        """Send templated email"""
        try:
            # Get email template
            template = self._get_email_template(template_name)
            if not template:
                raise ValueError(f"Email template '{template_name}' not found")
            
            # Render email content
            html_content = await self._render_template(template.html_template, context)
            text_content = None
            if template.text_template:
                text_content = await self._render_template(template.text_template, context)
            
            # Render subject
            subject = await self._render_string_template(template.subject, context)
            
            # Send email
            result = await self._send_smtp_email(
                recipient=recipient,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                sender_email=sender_email or settings.DEFAULT_FROM_EMAIL,
                sender_name=sender_name or template.sender_name
            )
            
            # Update stats
            if result["success"]:
                self.delivery_stats["sent"] += 1
            else:
                self.delivery_stats["failed"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            self.delivery_stats["failed"] += 1
            return {"success": False, "error": str(e)}

    async def _send_smtp_email(
        self,
        recipient: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        sender_email: str = None,
        sender_name: str = None
    ) -> Dict[str, Union[bool, str]]:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{sender_name} <{sender_email}>" if sender_name else sender_email
            msg["To"] = recipient
            
            # Add text part if available
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                msg.attach(text_part)
            
            # Add HTML part
            html_part = MIMEText(html_content, "html", "utf-8")
            msg.attach(html_part)
            
            # Send email
            if self.smtp_config["use_ssl"]:
                server = smtplib.SMTP_SSL(self.smtp_config["server"], self.smtp_config["port"])
            else:
                server = smtplib.SMTP(self.smtp_config["server"], self.smtp_config["port"])
                if self.smtp_config["use_tls"]:
                    server.starttls()
            
            server.login(self.smtp_config["username"], self.smtp_config["password"])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {recipient}")
            return {"success": True, "message_id": f"email_{int(time.time())}"}
            
        except Exception as e:
            logger.error(f"SMTP email sending failed: {e}")
            return {"success": False, "error": str(e)}

    async def _render_template(self, template_path: str, context: Dict[str, any]) -> str:
        """Render Jinja2 template"""
        try:
            template = self.template_env.get_template(template_path)
            return template.render(**context)
            
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            raise

    async def _render_string_template(self, template_string: str, context: Dict[str, any]) -> str:
        """Render template string"""
        try:
            template = self.template_env.from_string(template_string)
            return template.render(**context)
            
        except Exception as e:
            logger.error(f"String template rendering failed: {e}")
            return template_string

    def _get_email_template(self, template_name: str) -> Optional[EmailTemplate]:
        """Get email template configuration"""
        templates = {
            "protection_alert": EmailTemplate(
                name="protection_alert",
                subject="🚨 Content Protection Alert - {{ violation_type }}",
                html_template="protection_alert.html",
                text_template="protection_alert.txt",
                priority="high"
            ),
            "ai_processing_complete": EmailTemplate(
                name="ai_processing_complete",
                subject="✅ AI Analysis Complete - {{ content_name }}",
                html_template="ai_processing_complete.html",
                text_template="ai_processing_complete.txt"
            ),
            "revenue_notification": EmailTemplate(
                name="revenue_notification",
                subject="💰 Revenue Update - {{ amount }} {{ currency }}",
                html_template="revenue_notification.html",
                text_template="revenue_notification.txt"
            ),
            "collaboration_invite": EmailTemplate(
                name="collaboration_invite",
                subject="🤝 Collaboration Invitation from {{ inviter_name }}",
                html_template="collaboration_invite.html",
                text_template="collaboration_invite.txt"
            ),
            "account_security": EmailTemplate(
                name="account_security",
                subject="🔒 Account Security Alert",
                html_template="account_security.html",
                text_template="account_security.txt",
                priority="high"
            ),
            "welcome": EmailTemplate(
                name="welcome",
                subject="Welcome to IA Influencer Agent! 🎵",
                html_template="welcome.html",
                text_template="welcome.txt"
            ),
            "payment_notification": EmailTemplate(
                name="payment_notification",
                subject="💳 Payment Processed - {{ amount }} {{ currency }}",
                html_template="payment_notification.html",
                text_template="payment_notification.txt"
            )
        }
        
        return templates.get(template_name)

    async def send_protection_alert(self, user_email: str, violation_data: Dict[str, any]) -> bool:
        """Send content protection alert email"""
        try:
            context = {
                "violation_type": violation_data.get("type", "Unknown"),
                "platform": violation_data.get("platform", "Unknown"),
                "detected_url": violation_data.get("url", ""),
                "similarity_score": violation_data.get("similarity", 0),
                "detection_time": violation_data.get("detected_at", time.time()),
                "content_name": violation_data.get("content_name", "Your content"),
                "action_required": True
            }
            
            result = await self.send_email(user_email, "protection_alert", context)
            return result["success"]
            
        except Exception as e:
            logger.error(f"Error sending protection alert: {e}")
            return False

    async def send_revenue_notification(self, user_email: str, revenue_data: Dict[str, any]) -> bool:
        """Send revenue notification email"""
        try:
            context = {
                "amount": revenue_data.get("amount", 0),
                "currency": revenue_data.get("currency", "EUR"),
                "platform": revenue_data.get("platform", "Unknown"),
                "period": revenue_data.get("period", "this month"),
                "content_name": revenue_data.get("content_name", "Your content"),
                "payment_date": revenue_data.get("payment_date", ""),
                "breakdown": revenue_data.get("breakdown", {})
            }
            
            result = await self.send_email(user_email, "revenue_notification", context)
            return result["success"]
            
        except Exception as e:
            logger.error(f"Error sending revenue notification: {e}")
            return False

    async def send_collaboration_invite(self, recipient_email: str, invite_data: Dict[str, any]) -> bool:
        """Send collaboration invitation email"""
        try:
            context = {
                "inviter_name": invite_data.get("inviter_name", "Someone"),
                "project_name": invite_data.get("project_name", "a project"),
                "project_description": invite_data.get("description", ""),
                "invite_url": invite_data.get("invite_url", ""),
                "expires_at": invite_data.get("expires_at", ""),
                "project_type": invite_data.get("project_type", "collaboration")
            }
            
            result = await self.send_email(recipient_email, "collaboration_invite", context)
            return result["success"]
            
        except Exception as e:
            logger.error(f"Error sending collaboration invite: {e}")
            return False

    def get_delivery_stats(self) -> Dict[str, int]:
        """Get email delivery statistics"""
        return self.delivery_stats.copy()


class SMSNotificationManager:
    """
    Enterprise SMS notification management system
    Handles SMS delivery via Twilio and other providers
    """

    def __init__(self):
        self.twilio_client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.twilio_client = TwilioClient(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
        
        self.delivery_stats: Dict[str, int] = {
            "sent": 0,
            "delivered": 0,
            "failed": 0
        }

    async def send_sms(
        self,
        phone_number: str,
        template_name: str,
        context: Dict[str, any],
        sender_number: Optional[str] = None
    ) -> Dict[str, Union[bool, str]]:
        """Send templated SMS"""
        try:
            if not self.twilio_client:
                raise ValueError("SMS provider not configured")
            
            # Get SMS template
            template = self._get_sms_template(template_name)
            if not template:
                raise ValueError(f"SMS template '{template_name}' not found")
            
            # Render message
            message = await self._render_sms_template(template.message, context)
            
            # Truncate if too long
            if len(message) > template.max_length:
                message = message[:template.max_length - 3] + "..."
            
            # Send SMS
            result = await self._send_twilio_sms(
                phone_number=phone_number,
                message=message,
                sender_number=sender_number or settings.TWILIO_PHONE_NUMBER
            )
            
            # Update stats
            if result["success"]:
                self.delivery_stats["sent"] += 1
            else:
                self.delivery_stats["failed"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            self.delivery_stats["failed"] += 1
            return {"success": False, "error": str(e)}

    async def _send_twilio_sms(
        self,
        phone_number: str,
        message: str,
        sender_number: str
    ) -> Dict[str, Union[bool, str]]:
        """Send SMS via Twilio"""
        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_=sender_number,
                to=phone_number
            )
            
            logger.info(f"SMS sent successfully to {phone_number}")
            return {"success": True, "message_id": message.sid}
            
        except Exception as e:
            logger.error(f"Twilio SMS sending failed: {e}")
            return {"success": False, "error": str(e)}

    async def _render_sms_template(self, template_string: str, context: Dict[str, any]) -> str:
        """Render SMS template"""
        try:
            # Simple string templating for SMS
            message = template_string
            for key, value in context.items():
                message = message.replace(f"{{{{{key}}}}}", str(value))
            return message
            
        except Exception as e:
            logger.error(f"SMS template rendering failed: {e}")
            return template_string

    def _get_sms_template(self, template_name: str) -> Optional[SMSTemplate]:
        """Get SMS template configuration"""
        templates = {
            "protection_alert": SMSTemplate(
                name="protection_alert",
                message="🚨 IA Influencer Alert: Potential violation detected on {{platform}}. Check your dashboard for details.",
                max_length=160
            ),
            "ai_processing_complete": SMSTemplate(
                name="ai_processing_complete",
                message="✅ AI analysis complete for {{content_name}}. View results in your dashboard.",
                max_length=160
            ),
            "revenue_notification": SMSTemplate(
                name="revenue_notification",
                message="💰 New revenue: {{amount}} {{currency}} from {{platform}}. Details in your dashboard.",
                max_length=160
            ),
            "security_alert": SMSTemplate(
                name="security_alert",
                message="🔒 Security alert: {{alert_type}}. Please check your account immediately.",
                max_length=160
            ),
            "collaboration_invite": SMSTemplate(
                name="collaboration_invite",
                message="🤝 {{inviter_name}} invited you to collaborate on {{project_name}}. Check your email for details.",
                max_length=160
            )
        }
        
        return templates.get(template_name)

    async def send_protection_alert_sms(self, phone_number: str, violation_data: Dict[str, any]) -> bool:
        """Send protection alert SMS"""
        try:
            context = {
                "platform": violation_data.get("platform", "unknown platform"),
                "content_name": violation_data.get("content_name", "your content")
            }
            
            result = await self.send_sms(phone_number, "protection_alert", context)
            return result["success"]
            
        except Exception as e:
            logger.error(f"Error sending protection alert SMS: {e}")
            return False

    def get_delivery_stats(self) -> Dict[str, int]:
        """Get SMS delivery statistics"""
        return self.delivery_stats.copy()


class MultiChannelNotificationManager:
    """
    Unified notification manager for email, SMS, and push notifications
    Handles user preferences and delivery orchestration
    """

    def __init__(self):
        self.email_manager = EmailNotificationManager()
        self.sms_manager = SMSNotificationManager()
        self.user_preferences: Dict[str, NotificationPreferences] = {}

    async def send_notification(
        self,
        user_id: str,
        notification_type: str,
        data: Dict[str, any],
        channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """Send notification through multiple channels based on user preferences"""
        try:
            # Get user and preferences
            user = await self._get_user(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            preferences = await self._get_user_preferences(user_id)
            
            # Determine channels to use
            if channels is None:
                channels = self._get_preferred_channels(preferences, notification_type)
            
            results = {}
            
            # Send email
            if "email" in channels and preferences.email_enabled and user.email:
                email_result = await self._send_email_notification(
                    user.email, notification_type, data
                )
                results["email"] = email_result
            
            # Send SMS
            if "sms" in channels and preferences.sms_enabled and user.phone:
                sms_result = await self._send_sms_notification(
                    user.phone, notification_type, data
                )
                results["sms"] = sms_result
            
            # Send push notification (placeholder for future implementation)
            if "push" in channels and preferences.push_enabled:
                # TODO: Implement push notification
                results["push"] = True
            
            return results
            
        except Exception as e:
            logger.error(f"Error sending multi-channel notification: {e}")
            return {"error": str(e)}

    async def _send_email_notification(
        self, email: str, notification_type: str, data: Dict[str, any]
    ) -> bool:
        """Send email notification based on type"""
        try:
            if notification_type == "protection_alert":
                return await self.email_manager.send_protection_alert(email, data)
            elif notification_type == "revenue_notification":
                return await self.email_manager.send_revenue_notification(email, data)
            elif notification_type == "collaboration_invite":
                return await self.email_manager.send_collaboration_invite(email, data)
            else:
                # Generic email
                template_name = data.get("template", "generic")
                result = await self.email_manager.send_email(email, template_name, data)
                return result["success"]
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False

    async def _send_sms_notification(
        self, phone: str, notification_type: str, data: Dict[str, any]
    ) -> bool:
        """Send SMS notification based on type"""
        try:
            if notification_type == "protection_alert":
                return await self.sms_manager.send_protection_alert_sms(phone, data)
            else:
                # Generic SMS
                template_name = data.get("sms_template", notification_type)
                result = await self.sms_manager.send_sms(phone, template_name, data)
                return result["success"]
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {e}")
            return False

    def _get_preferred_channels(
        self, preferences: NotificationPreferences, notification_type: str
    ) -> List[str]:
        """Get preferred notification channels for specific type"""
        channels = []
        
        # Check if this notification type is enabled
        type_enabled = getattr(preferences, notification_type.replace("_", "_"), True)
        if not type_enabled:
            return channels
        
        # Add enabled channels
        if preferences.email_enabled:
            channels.append("email")
        
        # SMS only for critical notifications
        if preferences.sms_enabled and notification_type in ["protection_alert", "security_alert"]:
            channels.append("sms")
        
        if preferences.push_enabled:
            channels.append("push")
        
        return channels

    async def _get_user(self, user_id: str):
        """Get user from database"""
        # This would fetch from database
        # For now, return mock user
        return type('User', (), {
            'id': user_id,
            'email': f"user{user_id}@example.com",
            'phone': "+1234567890"
        })()

    async def _get_user_preferences(self, user_id: str) -> NotificationPreferences:
        """Get user notification preferences"""
        if user_id not in self.user_preferences:
            # Load from database or use defaults
            self.user_preferences[user_id] = NotificationPreferences(user_id=user_id)
        
        return self.user_preferences[user_id]

    async def update_user_preferences(
        self, user_id: str, preferences: NotificationPreferences
    ) -> bool:
        """Update user notification preferences"""
        try:
            self.user_preferences[user_id] = preferences
            # Save to database
            return True
            
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            return False

    def get_delivery_stats(self) -> Dict[str, Dict[str, int]]:
        """Get comprehensive delivery statistics"""
        return {
            "email": self.email_manager.get_delivery_stats(),
            "sms": self.sms_manager.get_delivery_stats()
        }
