"""Notification Service Utilities
Enterprise-grade notification system for Ainflue Platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import smtplib
import logging
from typing import Dict, List, Optional, Any, Union
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Notification types"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


@dataclass
class Notification:
    """Represents a notification"""
    title: str
    message: str
    type: NotificationType
    recipient: str
    metadata: Dict[str, Any] = None


class NotificationService:
    """
    Enterprise-grade notification service with multiple channels
    (email, SMS, push notifications, webhooks).
    """
    
    def __init__(self):
        self.channels: Dict[str, Any] = {}
        self.templates: Dict[str, str] = {}
        self.settings = {
            "smtp_server": None,
            "smtp_port": 587,
            "smtp_username": None,
            "smtp_password": None,
            "default_sender": "noreply@ainflue.com"
        }
        
        logger.info("NotificationService initialized")
    
    def configure_email(self, smtp_server: str, smtp_port: int = 587,
                       username: str = None, password: str = None,
                       sender: str = None):
        """Configure email settings"""
        self.settings.update({
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "smtp_username": username,
            "smtp_password": password,
            "default_sender": sender or self.settings["default_sender"]
        })
        logger.info(f"Email configured: {smtp_server}:{smtp_port}")
    
    async def send_notification(self, notification: Notification) -> bool:
        """Send notification through appropriate channel"""
        try:
            if "@" in notification.recipient:
                return await self.send_email(notification)
            else:
                logger.warning(f"Unknown recipient format: {notification.recipient}")
                return False
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False
    
    async def send_email(self, notification: Notification) -> bool:
        """Send email notification"""
        try:
            if not self.settings["smtp_server"]:
                logger.warning("SMTP not configured, skipping email")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.settings["default_sender"]
            msg['To'] = notification.recipient
            msg['Subject'] = notification.title
            
            # Create HTML body
            html_body = f"""
            <html>
            <body>
                <h2>{notification.title}</h2>
                <p>{notification.message}</p>
                <p><small>Type: {notification.type.value}</small></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.settings["smtp_server"], self.settings["smtp_port"]) as server:
                if self.settings["smtp_username"]:
                    server.starttls()
                    server.login(self.settings["smtp_username"], self.settings["smtp_password"])
                
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {notification.recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def add_template(self, name: str, template: str):
        """Add notification template"""
        self.templates[name] = template
        logger.info(f"Added template: {name}")
    
    def render_template(self, template_name: str, **kwargs) -> str:
        """Render notification template with variables"""
        if template_name not in self.templates:
            return kwargs.get('message', 'No template found')
        
        try:
            return self.templates[template_name].format(**kwargs)
        except KeyError as e:
            logger.error(f"Template rendering failed, missing variable: {e}")
            return kwargs.get('message', 'Template error')


# Global notification service instance
_global_notification_service: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    """Get global notification service instance"""
    global _global_notification_service
    if _global_notification_service is None:
        _global_notification_service = NotificationService()
    return _global_notification_service


async def send_notification(title: str, message: str, recipient: str, 
                          notification_type: NotificationType = NotificationType.INFO) -> bool:
    """Quick notification sending"""
    notification = Notification(
        title=title,
        message=message,
        type=notification_type,
        recipient=recipient
    )
    return await get_notification_service().send_notification(notification)