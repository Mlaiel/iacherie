"""
Ainflue Core Platform - Email Service Core
==========================================

Enterprise-grade email service with template management, delivery tracking,
bounce handling, and multi-provider support. Provides reliable email
communication for all Ainflue platform needs.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import smtplib
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import uuid
import re

logger = logging.getLogger(__name__)

class EmailStatus(str, Enum):
    """Email delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    BOUNCED = "bounced"
    FAILED = "failed"
    OPENED = "opened"
    CLICKED = "clicked"

class EmailPriority(str, Enum):
    """Email priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class EmailProvider(str, Enum):
    """Supported email providers"""
    SMTP = "smtp"
    SENDGRID = "sendgrid"
    MAILGUN = "mailgun"
    AWS_SES = "aws_ses"
    POSTMARK = "postmark"

@dataclass
class EmailAttachment:
    """Email attachment"""
    filename: str
    content: bytes
    mime_type: str
    content_id: Optional[str] = None

@dataclass
class EmailTemplate:
    """Email template"""
    template_id: str
    name: str
    subject: str
    html_content: str
    text_content: str
    variables: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class EmailMessage:
    """Email message"""
    message_id: str
    to_addresses: List[str]
    from_address: str
    subject: str
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    cc_addresses: List[str] = field(default_factory=list)
    bcc_addresses: List[str] = field(default_factory=list)
    reply_to: Optional[str] = None
    attachments: List[EmailAttachment] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    priority: EmailPriority = EmailPriority.NORMAL
    status: EmailStatus = EmailStatus.PENDING
    template_id: Optional[str] = None
    template_variables: Dict[str, Any] = field(default_factory=dict)
    scheduled_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EmailMetrics:
    """Email service metrics"""
    emails_sent: int = 0
    emails_delivered: int = 0
    emails_bounced: int = 0
    emails_failed: int = 0
    emails_opened: int = 0
    emails_clicked: int = 0
    delivery_rate: float = 0.0
    bounce_rate: float = 0.0
    open_rate: float = 0.0
    click_rate: float = 0.0

class EmailServiceCore:
    """Enterprise email service system"""
    
    def __init__(self, level -> None: str = "enterprise") -> None:
        """Initialize email service core"""
        self.level = level
        self.messages: Dict[str, EmailMessage] = {}
        self.templates: Dict[str, EmailTemplate] = {}
        self.metrics = EmailMetrics()
        
        # Provider configurations
        self.providers: Dict[str, Dict[str, Any]] = {}
        self.active_provider = EmailProvider.SMTP
        
        # Email queues
        self.send_queue: asyncio.Queue = asyncio.Queue()
        self.retry_queue: asyncio.Queue = asyncio.Queue()
        
        # Configuration
        self.config = {
            "max_retries": 3,
            "retry_delay": 300,  # 5 minutes
            "batch_size": 100,
            "rate_limit": 10,  # emails per second
            "bounce_threshold": 0.05,  # 5%
            "tracking_enabled": True,
            "default_from": "noreply@ainflue.com",
            "default_timeout": 30
        }
        
        # Processing tasks
        self.processing_tasks: List[asyncio.Task] = []
        self._shutdown_event = asyncio.Event()
        
        # Initialize default templates
        self._initialize_default_templates()
        
        # Start email processors
        self._start_email_processors()
        
        logger.info(f"📧 Email Service Core initialized - Level: {level}")

    def _initialize_default_templates(self) -> None:
        """Initialize default email templates"""
        
        # Welcome email template
        welcome_template = EmailTemplate(
            template_id="welcome",
            name="Welcome Email",
            subject="Welcome to Ainflue, {{name}}!",
            html_content="""
            <h1>Welcome to Ainflue!</h1>
            <p>Hi {{name}},</p>
            <p>Welcome to the Ainflue platform! We're excited to have you on board.</p>
            <p>Get started by exploring our features:</p>
            <ul>
                <li>Create amazing content</li>
                <li>Connect with other creators</li>
                <li>Monetize your creativity</li>
            </ul>
            <p>Best regards,<br>The Ainflue Team</p>
            """,
            text_content="""
            Welcome to Ainflue!
            
            Hi {{name}},
            
            Welcome to the Ainflue platform! We're excited to have you on board.
            
            Get started by exploring our features:
            - Create amazing content
            - Connect with other creators
            - Monetize your creativity
            
            Best regards,
            The Ainflue Team
            """,
            variables=["name"]
        )
        
        self.templates[welcome_template.template_id] = welcome_template
        
        # Password reset template
        reset_template = EmailTemplate(
            template_id="password_reset",
            name="Password Reset",
            subject="Reset Your Ainflue Password",
            html_content="""
            <h1>Password Reset Request</h1>
            <p>Hi {{name}},</p>
            <p>You requested a password reset for your Ainflue account.</p>
            <p>Click the button below to reset your password:</p>
            <p><a href="{{reset_link}}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this reset, please ignore this email.</p>
            <p>Best regards,<br>The Ainflue Team</p>
            """,
            text_content="""
            Password Reset Request
            
            Hi {{name}},
            
            You requested a password reset for your Ainflue account.
            
            Click the link below to reset your password:
            {{reset_link}}
            
            This link will expire in 1 hour.
            
            If you didn't request this reset, please ignore this email.
            
            Best regards,
            The Ainflue Team
            """,
            variables=["name", "reset_link"]
        )
        
        self.templates[reset_template.template_id] = reset_template

    def _start_email_processors(self) -> None:
        """Start background email processing tasks"""
        
        # Main email sender
        sender_task = asyncio.create_task(self._email_sender_loop())
        self.processing_tasks.append(sender_task)
        
        # Retry processor
        retry_task = asyncio.create_task(self._retry_processor_loop())
        self.processing_tasks.append(retry_task)
        
        # Metrics updater
        metrics_task = asyncio.create_task(self._metrics_updater_loop())
        self.processing_tasks.append(metrics_task)

    async def configure_provider(
        self,
        provider -> None: EmailProvider,
        config -> None: Dict[str, Any]
    ) -> None:
        """Configure email provider"""
        
        self.providers[provider.value] = config
        
        if provider == EmailProvider.SMTP:
            required_keys = ["host", "port", "username", "password"]
        elif provider == EmailProvider.SENDGRID:
            required_keys = ["api_key"]
        elif provider == EmailProvider.MAILGUN:
            required_keys = ["api_key", "domain"]
        elif provider == EmailProvider.AWS_SES:
            required_keys = ["access_key_id", "secret_access_key", "region"]
        else:
            required_keys = []
        
        # Validate configuration
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")
        
        self.active_provider = provider
        logger.info(f"Configured email provider: {provider.value}")

    async def create_template(
        self,
        name: str,
        subject: str,
        html_content: str,
        text_content: str,
        variables: Optional[List[str]] = None
    ) -> str:
        """Create email template"""
        
        template_id = f"template_{int(time.time())}_{len(self.templates)}"
        
        template = EmailTemplate(
            template_id=template_id,
            name=name,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            variables=variables or []
        )
        
        self.templates[template_id] = template
        
        logger.info(f"Created email template: {name}")
        return template_id

    async def send_email(
        self,
        to_addresses: Union[str, List[str]],
        subject: str,
        content: str,
        from_address: Optional[str] = None,
        html_content: Optional[str] = None,
        cc_addresses: Optional[List[str]] = None,
        bcc_addresses: Optional[List[str]] = None,
        attachments: Optional[List[EmailAttachment]] = None,
        priority: EmailPriority = EmailPriority.NORMAL,
        scheduled_at: Optional[datetime] = None
    ) -> str:
        """Send email message"""
        
        # Normalize to_addresses
        if isinstance(to_addresses, str):
            to_addresses = [to_addresses]
        
        # Create message
        message_id = str(uuid.uuid4())
        
        message = EmailMessage(
            message_id=message_id,
            to_addresses=to_addresses,
            from_address=from_address or self.config["default_from"],
            subject=subject,
            text_content=content,
            html_content=html_content,
            cc_addresses=cc_addresses or [],
            bcc_addresses=bcc_addresses or [],
            attachments=attachments or [],
            priority=priority,
            scheduled_at=scheduled_at
        )
        
        # Store message
        self.messages[message_id] = message
        
        # Queue for sending
        if scheduled_at and scheduled_at > datetime.utcnow():
            # Schedule for later
            message.status = EmailStatus.PENDING
        else:
            # Send immediately
            await self.send_queue.put(message)
        
        logger.debug(f"Queued email message {message_id}")
        return message_id

    async def send_template_email(
        self,
        template_id: str,
        to_addresses: Union[str, List[str]],
        variables: Dict[str, Any],
        from_address: Optional[str] = None,
        priority: EmailPriority = EmailPriority.NORMAL
    ) -> str:
        """Send email using template"""
        
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Process template
        subject = self._process_template(template.subject, variables)
        html_content = self._process_template(template.html_content, variables)
        text_content = self._process_template(template.text_content, variables)
        
        # Normalize to_addresses
        if isinstance(to_addresses, str):
            to_addresses = [to_addresses]
        
        # Create message
        message_id = str(uuid.uuid4())
        
        message = EmailMessage(
            message_id=message_id,
            to_addresses=to_addresses,
            from_address=from_address or self.config["default_from"],
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            priority=priority,
            template_id=template_id,
            template_variables=variables
        )
        
        # Store and queue
        self.messages[message_id] = message
        await self.send_queue.put(message)
        
        logger.debug(f"Queued template email {message_id} using template {template_id}")
        return message_id

    def _process_template(self, template_text: str, variables: Dict[str, Any]) -> str:
        """Process template with variables"""
        
        result = template_text
        
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        
        return result

    async def _email_sender_loop(self) -> None:
        """Main email sending loop"""
        
        while not self._shutdown_event.is_set():
            try:
                # Get message from queue
                message = await asyncio.wait_for(
                    self.send_queue.get(),
                    timeout=1.0
                )
                
                await self._send_message(message)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Email sender error: {str(e)}")

    async def _send_message(self, message -> None: EmailMessage) -> None:
        """Send individual email message"""
        
        try:
            # Validate email addresses
            for email in message.to_addresses:
                if not self._is_valid_email(email):
                    raise ValueError(f"Invalid email address: {email}")
            
            # Send based on active provider
            if self.active_provider == EmailProvider.SMTP:
                await self._send_via_smtp(message)
            else:
                # For other providers, would implement specific APIs
                await self._send_via_api(message)
            
            # Update message status
            message.status = EmailStatus.SENT
            message.sent_at = datetime.utcnow()
            
            # Update metrics
            self.metrics.emails_sent += len(message.to_addresses)
            
            logger.debug(f"Sent email {message.message_id}")
            
        except Exception as e:
            logger.error(f"Failed to send email {message.message_id}: {str(e)}")
            
            # Update status
            message.status = EmailStatus.FAILED
            message.metadata["error"] = str(e)
            
            # Retry if not exceeded max attempts
            retry_count = message.metadata.get("retry_count", 0)
            if retry_count < self.config["max_retries"]:
                message.metadata["retry_count"] = retry_count + 1
                await self.retry_queue.put(message)
            else:
                self.metrics.emails_failed += len(message.to_addresses)

    async def _send_via_smtp(self, message -> None: EmailMessage) -> None:
        """Send email via SMTP"""
        
        smtp_config = self.providers.get("smtp", {})
        if not smtp_config:
            raise ValueError("SMTP not configured")
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = message.subject
        msg['From'] = message.from_address
        msg['To'] = ', '.join(message.to_addresses)
        
        if message.cc_addresses:
            msg['Cc'] = ', '.join(message.cc_addresses)
        
        if message.reply_to:
            msg['Reply-To'] = message.reply_to
        
        # Add custom headers
        for key, value in message.headers.items():
            msg[key] = value
        
        # Add content
        if message.text_content:
            text_part = MIMEText(message.text_content, 'plain')
            msg.attach(text_part)
        
        if message.html_content:
            html_part = MIMEText(message.html_content, 'html')
            msg.attach(html_part)
        
        # Add attachments
        for attachment in message.attachments:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.content)
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment.filename}'
            )
            msg.attach(part)
        
        # Send email
        try:
            with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
                if smtp_config.get('use_tls', True):
                    server.starttls()
                
                if smtp_config.get('username') and smtp_config.get('password'):
                    server.login(smtp_config['username'], smtp_config['password'])
                
                all_recipients = (
                    message.to_addresses + 
                    message.cc_addresses + 
                    message.bcc_addresses
                )
                
                server.send_message(msg, to_addrs=all_recipients)
                
        except Exception as e:
            raise Exception(f"SMTP send failed: {str(e)}")

    async def _send_via_api(self, message -> None: EmailMessage) -> None:
        """Send email via API provider"""
        
        # Placeholder for API-based providers
        # In production, would implement specific provider APIs
        
        logger.info(f"API send not implemented for {self.active_provider.value}")
        raise NotImplementedError(f"API sending not implemented for {self.active_provider.value}")

    def _is_valid_email(self, email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    async def _retry_processor_loop(self) -> None:
        """Process retry queue"""
        
        while not self._shutdown_event.is_set():
            try:
                # Get message from retry queue
                message = await asyncio.wait_for(
                    self.retry_queue.get(),
                    timeout=5.0
                )
                
                # Wait before retry
                await asyncio.sleep(self.config["retry_delay"])
                
                # Re-queue for sending
                await self.send_queue.put(message)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Retry processor error: {str(e)}")

    async def _metrics_updater_loop(self) -> None:
        """Update email metrics"""
        
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Update every minute
                
                # Calculate rates
                total_sent = self.metrics.emails_sent
                
                if total_sent > 0:
                    self.metrics.delivery_rate = self.metrics.emails_delivered / total_sent
                    self.metrics.bounce_rate = self.metrics.emails_bounced / total_sent
                    self.metrics.open_rate = self.metrics.emails_opened / total_sent
                    self.metrics.click_rate = self.metrics.emails_clicked / total_sent
                
            except Exception as e:
                logger.error(f"Metrics updater error: {str(e)}")

    async def track_delivery(self, message_id -> None: str) -> None:
        """Track email delivery"""
        
        message = self.messages.get(message_id)
        if message:
            message.status = EmailStatus.DELIVERED
            message.delivered_at = datetime.utcnow()
            self.metrics.emails_delivered += 1

    async def track_bounce(self, message_id -> None: str, reason -> None: str) -> None:
        """Track email bounce"""
        
        message = self.messages.get(message_id)
        if message:
            message.status = EmailStatus.BOUNCED
            message.metadata["bounce_reason"] = reason
            self.metrics.emails_bounced += 1

    async def track_open(self, message_id -> None: str) -> None:
        """Track email open"""
        
        message = self.messages.get(message_id)
        if message:
            if message.status == EmailStatus.DELIVERED:
                message.status = EmailStatus.OPENED
            message.metadata["opened_at"] = datetime.utcnow().isoformat()
            self.metrics.emails_opened += 1

    async def track_click(self, message_id -> None: str, link_url -> None: str) -> None:
        """Track email link click"""
        
        message = self.messages.get(message_id)
        if message:
            message.status = EmailStatus.CLICKED
            clicks = message.metadata.get("clicks", [])
            clicks.append({
                "url": link_url,
                "clicked_at": datetime.utcnow().isoformat()
            })
            message.metadata["clicks"] = clicks
            self.metrics.emails_clicked += 1

    def get_message(self, message_id: str) -> Optional[EmailMessage]:
        """Get email message by ID"""
        return self.messages.get(message_id)

    def get_template(self, template_id: str) -> Optional[EmailTemplate]:
        """Get email template by ID"""
        return self.templates.get(template_id)

    def list_messages(
        self,
        status: Optional[EmailStatus] = None,
        limit: int = 100
    ) -> List[EmailMessage]:
        """List email messages"""
        
        messages = list(self.messages.values())
        
        if status:
            messages = [msg for msg in messages if msg.status == status]
        
        # Sort by creation date (newest first)
        messages.sort(key=lambda x: x.created_at, reverse=True)
        
        return messages[:limit]

    def get_metrics(self) -> EmailMetrics:
        """Get email service metrics"""
        return self.metrics

    async def health_check(self) -> bool:
        """Health check for email service"""
        try:
            # Check if any provider is configured
            if not self.providers:
                logger.warning("No email providers configured")
                return False
            
            # Test queue operations
            test_message = EmailMessage(
                message_id="health_check",
                to_addresses=["test@example.com"],
                from_address="health@test.com",
                subject="Health Check",
                text_content="Test"
            )
            
            # Test template processing
            if "welcome" in self.templates:
                self._process_template("Hello {{name}}", {"name": "Test"})
            
            return True
            
        except Exception as e:
            logger.error(f"Email service health check failed: {str(e)}")
            return False

    async def shutdown(self) -> None:
        """Shutdown email service"""
        logger.info("🛑 Shutting down email service")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel processing tasks
        for task in self.processing_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.processing_tasks:
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)

# Module exports
__all__ = [
    "EmailServiceCore", "EmailMessage", "EmailTemplate", "EmailAttachment",
    "EmailStatus", "EmailPriority", "EmailProvider", "EmailMetrics"
]

logger.info("📧 Email Service Core module loaded")