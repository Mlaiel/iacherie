"""Notification Helper for IA Influencer Agent Platform
Advanced notification system with multi-channel delivery and template management

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent Platform with Multi-Content Protection
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
import jinja2
from jinja2 import Template
import requests
import sqlite3
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
import time
from enum import Enum
import re
import html
import markdown

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Notification delivery channels"""    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    IN_APP = "in_app"


class NotificationPriority(Enum):
    """Notification priority levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationStatus(Enum):
    """Notification delivery status"""    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"
    CANCELLED = "cancelled"


@dataclass
class NotificationTemplate:
    """Notification template structure"""    template_id: str
    name: str
    subject_template: str
    body_template: str
    channel: NotificationChannel
    content_type: str = "text/html"  # text/html, text/plain, application/json
    variables: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'template_id': self.template_id,
            'name': self.name,
            'subject_template': self.subject_template,
            'body_template': self.body_template,
            'channel': self.channel.value,
            'content_type': self.content_type,
            'variables': self.variables,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }


@dataclass
class NotificationMessage:
    """Individual notification message"""    message_id: str
    recipient: str
    channel: NotificationChannel
    priority: NotificationPriority
    subject: str
    body: str
    template_id: Optional[str] = None
    template_data: Dict[str, Any] = field(default_factory=dict)
    attachments: List[str] = field(default_factory=list)
    scheduled_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: NotificationStatus = NotificationStatus.PENDING
    attempts: int = 0
    max_attempts: int = 3
    last_attempt_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'message_id': self.message_id,
            'recipient': self.recipient,
            'channel': self.channel.value,
            'priority': self.priority.value,
            'subject': self.subject,
            'body': self.body,
            'template_id': self.template_id,
            'template_data': self.template_data,
            'attachments': self.attachments,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'created_at': self.created_at.isoformat(),
            'status': self.status.value,
            'attempts': self.attempts,
            'max_attempts': self.max_attempts,
            'last_attempt_at': self.last_attempt_at.isoformat() if self.last_attempt_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'error_message': self.error_message,
            'metadata': self.metadata
        }


@dataclass
class DeliveryResult:
    """Notification delivery result"""    success: bool
    message_id: str
    channel: NotificationChannel
    recipient: str
    delivery_time: float
    external_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    retry_after: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class TemplateEngine:
    """Advanced template engine for notifications"""    
    def __init__(self):
        self.jinja_env = jinja2.Environment(
            loader=jinja2.DictLoader({}),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # Add custom filters
        self.jinja_env.filters['datetime'] = self._datetime_filter
        self.jinja_env.filters['currency'] = self._currency_filter
        self.jinja_env.filters['truncate'] = self._truncate_filter
        self.jinja_env.filters['markdown'] = self._markdown_filter
        
        # Add custom functions
        self.jinja_env.globals['now'] = datetime.utcnow
        self.jinja_env.globals['format_number'] = self._format_number
    
    def render_template(self, template_content: str, 
                       template_data: Dict[str, Any]) -> str:
        """Render template with provided data"""        try:
            template = Template(template_content, environment=self.jinja_env)
            return template.render(**template_data)
        except Exception as e:
            logger.error(f"Template rendering failed: {str(e)}")
            raise
    
    def validate_template(self, template_content: str) -> Dict[str, Any]:
        """Validate template syntax and extract variables"""        try:
            template = Template(template_content, environment=self.jinja_env)
            
            # Extract undefined variables
            undeclared = template.environment.parse(template_content).find_all(
                jinja2.nodes.Name
            )
            variables = [node.name for node in undeclared]
            
            return {
                'valid': True,
                'variables': list(set(variables)),
                'error': None
            }
        except Exception as e:
            return {
                'valid': False,
                'variables': [],
                'error': str(e)
            }
    
    def _datetime_filter(self, value: Union[str, datetime], 
                        format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format datetime values"""        if isinstance(value, str):
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return value.strftime(format_string)
    
    def _currency_filter(self, value: Union[int, float], 
                        currency: str = "USD") -> str:
        """Format currency values"""        return f"{value:.2f} {currency}"
    
    def _truncate_filter(self, value: str, length: int = 100, 
                        end: str = "...") -> str:
        """Truncate text to specified length"""        if len(value) <= length:
            return value
        return value[:length - len(end)] + end
    
    def _markdown_filter(self, value: str) -> str:
        """Convert markdown to HTML"""        return markdown.markdown(value)
    
    def _format_number(self, value: Union[int, float], 
                      decimal_places: int = 0) -> str:
        """Format numbers with thousand separators"""        if decimal_places > 0:
            return f"{value:,.{decimal_places}f}"
        else:
            return f"{int(value):,}"


class EmailChannel:
    """Email notification channel handler"""    
    def __init__(self, smtp_host: str, smtp_port: int, 
                 username: str, password: str, use_tls: bool = True):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.from_address = username
        
    async def send_notification(self, message: NotificationMessage) -> DeliveryResult:
        """Send email notification"""        start_time = time.time()
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_address
            msg['To'] = message.recipient
            msg['Subject'] = message.subject
            
            # Add body
            msg.attach(MIMEText(message.body, 'html' if 'html' in message.body.lower() else 'plain'))
            
            # Add attachments
            for attachment_path in message.attachments:
                if Path(attachment_path).exists():
                    with open(attachment_path, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                    
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {Path(attachment_path).name}'
                    )
                    msg.attach(part)
            
            # Send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                server.login(self.username, self.password)
                server.send_message(msg)
            
            delivery_time = time.time() - start_time
            
            return DeliveryResult(
                success=True,
                message_id=message.message_id,
                channel=NotificationChannel.EMAIL,
                recipient=message.recipient,
                delivery_time=delivery_time
            )
            
        except Exception as e:
            logger.error(f"Email delivery failed: {str(e)}")
            
            return DeliveryResult(
                success=False,
                message_id=message.message_id,
                channel=NotificationChannel.EMAIL,
                recipient=message.recipient,
                delivery_time=time.time() - start_time,
                error_message=str(e)
            )


class WebhookChannel:
    """Webhook notification channel handler"""    
    def __init__(self, default_timeout: int = 30):
        self.default_timeout = default_timeout
        
    async def send_notification(self, message: NotificationMessage,
                              webhook_url: str, 
                              headers: Optional[Dict[str, str]] = None,
                              method: str = "POST") -> DeliveryResult:
        """Send webhook notification"""        start_time = time.time()
        
        try:
            # Prepare payload
            payload = {
                'message_id': message.message_id,
                'recipient': message.recipient,
                'subject': message.subject,
                'body': message.body,
                'priority': message.priority.value,
                'channel': message.channel.value,
                'created_at': message.created_at.isoformat(),
                'metadata': message.metadata
            }
            
            # Set default headers
            if headers is None:
                headers = {'Content-Type': 'application/json'}
            
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.default_timeout)
                ) as response:
                    
                    delivery_time = time.time() - start_time
                    
                    if response.status < 400:
                        response_text = await response.text()
                        
                        return DeliveryResult(
                            success=True,
                            message_id=message.message_id,
                            channel=NotificationChannel.WEBHOOK,
                            recipient=webhook_url,
                            delivery_time=delivery_time,
                            external_id=response.headers.get('X-Request-ID'),
                            metadata={'response': response_text[:500]}
                        )
                    else:
                        error_text = await response.text()
                        
                        return DeliveryResult(
                            success=False,
                            message_id=message.message_id,
                            channel=NotificationChannel.WEBHOOK,
                            recipient=webhook_url,
                            delivery_time=delivery_time,
                            error_code=str(response.status),
                            error_message=error_text[:500]
                        )
                        
        except Exception as e:
            logger.error(f"Webhook delivery failed: {str(e)}")
            
            return DeliveryResult(
                success=False,
                message_id=message.message_id,
                channel=NotificationChannel.WEBHOOK,
                recipient=webhook_url,
                delivery_time=time.time() - start_time,
                error_message=str(e)
            )


class SlackChannel:
    """Slack notification channel handler"""    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.api_url = "https://slack.com/api"
        
    async def send_notification(self, message: NotificationMessage) -> DeliveryResult:
        """Send Slack notification"""        start_time = time.time()
        
        try:
            # Prepare Slack message
            slack_message = {
                'channel': message.recipient,  # Channel ID or user ID
                'text': message.subject,
                'blocks': [
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': f"*{message.subject}*"
                        }
                    },
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': message.body
                        }
                    }
                ]
            }
            
            # Add priority indicator
            if message.priority in [NotificationPriority.HIGH, NotificationPriority.URGENT, NotificationPriority.CRITICAL]:
                slack_message['blocks'].insert(0, {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f":warning: *{message.priority.value.upper()} PRIORITY*"
                    }
                })
            
            headers = {
                'Authorization': f'Bearer {self.bot_token}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/chat.postMessage",
                    json=slack_message,
                    headers=headers
                ) as response:
                    
                    delivery_time = time.time() - start_time
                    response_data = await response.json()
                    
                    if response_data.get('ok'):
                        return DeliveryResult(
                            success=True,
                            message_id=message.message_id,
                            channel=NotificationChannel.SLACK,
                            recipient=message.recipient,
                            delivery_time=delivery_time,
                            external_id=response_data.get('ts'),
                            metadata={'channel': response_data.get('channel')}
                        )
                    else:
                        return DeliveryResult(
                            success=False,
                            message_id=message.message_id,
                            channel=NotificationChannel.SLACK,
                            recipient=message.recipient,
                            delivery_time=delivery_time,
                            error_message=response_data.get('error', 'Unknown Slack API error')
                        )
                        
        except Exception as e:
            logger.error(f"Slack delivery failed: {str(e)}")
            
            return DeliveryResult(
                success=False,
                message_id=message.message_id,
                channel=NotificationChannel.SLACK,
                recipient=message.recipient,
                delivery_time=time.time() - start_time,
                error_message=str(e)
            )


class TelegramChannel:
    """Telegram notification channel handler"""    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        
    async def send_notification(self, message: NotificationMessage) -> DeliveryResult:
        """Send Telegram notification"""        start_time = time.time()
        
        try:
            # Prepare message text
            text = f"*{html.escape(message.subject)}*\n\n{html.escape(message.body)}"
            
            # Add priority indicator
            if message.priority in [NotificationPriority.HIGH, NotificationPriority.URGENT, NotificationPriority.CRITICAL]:
                text = f"🚨 *{message.priority.value.upper()} PRIORITY*\n\n{text}"
            
            payload = {
                'chat_id': message.recipient,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/sendMessage",
                    json=payload
                ) as response:
                    
                    delivery_time = time.time() - start_time
                    response_data = await response.json()
                    
                    if response_data.get('ok'):
                        return DeliveryResult(
                            success=True,
                            message_id=message.message_id,
                            channel=NotificationChannel.TELEGRAM,
                            recipient=message.recipient,
                            delivery_time=delivery_time,
                            external_id=str(response_data['result']['message_id']),
                            metadata={'chat_id': response_data['result']['chat']['id']}
                        )
                    else:
                        return DeliveryResult(
                            success=False,
                            message_id=message.message_id,
                            channel=NotificationChannel.TELEGRAM,
                            recipient=message.recipient,
                            delivery_time=delivery_time,
                            error_code=str(response_data.get('error_code')),
                            error_message=response_data.get('description', 'Unknown Telegram API error')
                        )
                        
        except Exception as e:
            logger.error(f"Telegram delivery failed: {str(e)}")
            
            return DeliveryResult(
                success=False,
                message_id=message.message_id,
                channel=NotificationChannel.TELEGRAM,
                recipient=message.recipient,
                delivery_time=time.time() - start_time,
                error_message=str(e)
            )


class NotificationStorage:
    """Notification storage and retrieval"""    
    def __init__(self, database_path: str = "notifications.db"):
        self.database_path = database_path
        self._init_database()
        self._lock = threading.Lock()
    
    def _init_database(self):
        """Initialize SQLite database"""        with sqlite3.connect(self.database_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS notification_templates (
                    template_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    subject_template TEXT NOT NULL,
                    body_template TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    content_type TEXT DEFAULT 'text/html',
                    variables TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS notification_messages (
                    message_id TEXT PRIMARY KEY,
                    recipient TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    template_id TEXT,
                    template_data TEXT,
                    attachments TEXT,
                    scheduled_at TEXT,
                    created_at TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    attempts INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 3,
                    last_attempt_at TEXT,
                    delivered_at TEXT,
                    error_message TEXT,
                    metadata TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS delivery_results (
                    result_id TEXT PRIMARY KEY,
                    message_id TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    delivery_time REAL NOT NULL,
                    external_id TEXT,
                    error_code TEXT,
                    error_message TEXT,
                    retry_after INTEGER,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (message_id) REFERENCES notification_messages (message_id)
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_messages_status ON notification_messages (status)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_messages_scheduled ON notification_messages (scheduled_at)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_results_message ON delivery_results (message_id)
            ''')
    
    def save_template(self, template: NotificationTemplate) -> bool:
        """Save notification template"""        try:
            with self._lock:
                with sqlite3.connect(self.database_path) as conn:
                    conn.execute('''
                        INSERT OR REPLACE INTO notification_templates
                        (template_id, name, subject_template, body_template, channel,
                         content_type, variables, created_at, updated_at, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        template.template_id,
                        template.name,
                        template.subject_template,
                        template.body_template,
                        template.channel.value,
                        template.content_type,
                        json.dumps(template.variables),
                        template.created_at.isoformat(),
                        template.updated_at.isoformat(),
                        template.is_active
                    ))
            return True
        except Exception as e:
            logger.error(f"Failed to save template: {str(e)}")
            return False
    
    def get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """Get notification template by ID"""        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    'SELECT * FROM notification_templates WHERE template_id = ? AND is_active = 1',
                    (template_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return NotificationTemplate(
                        template_id=row['template_id'],
                        name=row['name'],
                        subject_template=row['subject_template'],
                        body_template=row['body_template'],
                        channel=NotificationChannel(row['channel']),
                        content_type=row['content_type'],
                        variables=json.loads(row['variables']) if row['variables'] else [],
                        created_at=datetime.fromisoformat(row['created_at']),
                        updated_at=datetime.fromisoformat(row['updated_at']),
                        is_active=bool(row['is_active'])
                    )
        except Exception as e:
            logger.error(f"Failed to get template: {str(e)}")
        
        return None
    
    def save_message(self, message: NotificationMessage) -> bool:
        """Save notification message"""        try:
            with self._lock:
                with sqlite3.connect(self.database_path) as conn:
                    conn.execute('''
                        INSERT OR REPLACE INTO notification_messages
                        (message_id, recipient, channel, priority, subject, body,
                         template_id, template_data, attachments, scheduled_at,
                         created_at, status, attempts, max_attempts, last_attempt_at,
                         delivered_at, error_message, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        message.message_id,
                        message.recipient,
                        message.channel.value,
                        message.priority.value,
                        message.subject,
                        message.body,
                        message.template_id,
                        json.dumps(message.template_data),
                        json.dumps(message.attachments),
                        message.scheduled_at.isoformat() if message.scheduled_at else None,
                        message.created_at.isoformat(),
                        message.status.value,
                        message.attempts,
                        message.max_attempts,
                        message.last_attempt_at.isoformat() if message.last_attempt_at else None,
                        message.delivered_at.isoformat() if message.delivered_at else None,
                        message.error_message,
                        json.dumps(message.metadata)
                    ))
            return True
        except Exception as e:
            logger.error(f"Failed to save message: {str(e)}")
            return False
    
    def get_pending_messages(self, limit: int = 100) -> List[NotificationMessage]:
        """Get pending notification messages"""        messages = []
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT * FROM notification_messages 
                    WHERE status IN ('pending', 'retry')
                    AND (scheduled_at IS NULL OR scheduled_at <= ?)
                    ORDER BY priority DESC, created_at ASC
                    LIMIT ?
                ''', (datetime.utcnow().isoformat(), limit))
                
                for row in cursor:
                    message = NotificationMessage(
                        message_id=row['message_id'],
                        recipient=row['recipient'],
                        channel=NotificationChannel(row['channel']),
                        priority=NotificationPriority(row['priority']),
                        subject=row['subject'],
                        body=row['body'],
                        template_id=row['template_id'],
                        template_data=json.loads(row['template_data']) if row['template_data'] else {},
                        attachments=json.loads(row['attachments']) if row['attachments'] else [],
                        scheduled_at=datetime.fromisoformat(row['scheduled_at']) if row['scheduled_at'] else None,
                        created_at=datetime.fromisoformat(row['created_at']),
                        status=NotificationStatus(row['status']),
                        attempts=row['attempts'],
                        max_attempts=row['max_attempts'],
                        last_attempt_at=datetime.fromisoformat(row['last_attempt_at']) if row['last_attempt_at'] else None,
                        delivered_at=datetime.fromisoformat(row['delivered_at']) if row['delivered_at'] else None,
                        error_message=row['error_message'],
                        metadata=json.loads(row['metadata']) if row['metadata'] else {}
                    )
                    messages.append(message)
                    
        except Exception as e:
            logger.error(f"Failed to get pending messages: {str(e)}")
        
        return messages
    
    def save_delivery_result(self, result: DeliveryResult) -> bool:
        """Save delivery result"""        try:
            with self._lock:
                with sqlite3.connect(self.database_path) as conn:
                    result_id = str(uuid.uuid4())
                    conn.execute('''
                        INSERT INTO delivery_results
                        (result_id, message_id, channel, recipient, success,
                         delivery_time, external_id, error_code, error_message,
                         retry_after, metadata, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        result_id,
                        result.message_id,
                        result.channel.value,
                        result.recipient,
                        result.success,
                        result.delivery_time,
                        result.external_id,
                        result.error_code,
                        result.error_message,
                        result.retry_after,
                        json.dumps(result.metadata),
                        datetime.utcnow().isoformat()
                    ))
            return True
        except Exception as e:
            logger.error(f"Failed to save delivery result: {str(e)}")
            return False


class NotificationManager:
    """Main notification management system"""    
    def __init__(self, storage: NotificationStorage,
                 email_config: Optional[Dict[str, Any]] = None,
                 webhook_config: Optional[Dict[str, Any]] = None,
                 slack_config: Optional[Dict[str, Any]] = None,
                 telegram_config: Optional[Dict[str, Any]] = None):
        
        self.storage = storage
        self.template_engine = TemplateEngine()
        
        # Initialize channels
        self.channels = {}
        
        if email_config:
            self.channels[NotificationChannel.EMAIL] = EmailChannel(**email_config)
        
        if webhook_config:
            self.channels[NotificationChannel.WEBHOOK] = WebhookChannel(**webhook_config)
        
        if slack_config:
            self.channels[NotificationChannel.SLACK] = SlackChannel(**slack_config)
        
        if telegram_config:
            self.channels[NotificationChannel.TELEGRAM] = TelegramChannel(**telegram_config)
        
        # Processing queue
        self.processing = False
        self.process_interval = 5  # seconds
        
        # Rate limiting
        self.rate_limits = {
            NotificationChannel.EMAIL: {'count': 0, 'reset_time': datetime.utcnow(), 'max_per_minute': 60},
            NotificationChannel.WEBHOOK: {'count': 0, 'reset_time': datetime.utcnow(), 'max_per_minute': 600},
            NotificationChannel.SLACK: {'count': 0, 'reset_time': datetime.utcnow(), 'max_per_minute': 100},
            NotificationChannel.TELEGRAM: {'count': 0, 'reset_time': datetime.utcnow(), 'max_per_minute': 30}
        }
    
    def create_template(self, name: str, subject_template: str, 
                       body_template: str, channel: NotificationChannel,
                       content_type: str = "text/html") -> NotificationTemplate:
        """Create new notification template"""        template = NotificationTemplate(
            template_id=str(uuid.uuid4()),
            name=name,
            subject_template=subject_template,
            body_template=body_template,
            channel=channel,
            content_type=content_type
        )
        
        # Validate template syntax
        subject_validation = self.template_engine.validate_template(subject_template)
        body_validation = self.template_engine.validate_template(body_template)
        
        if not subject_validation['valid']:
            raise ValueError(f"Invalid subject template: {subject_validation['error']}")
        
        if not body_validation['valid']:
            raise ValueError(f"Invalid body template: {body_validation['error']}")
        
        # Extract variables
        template.variables = list(set(
            subject_validation['variables'] + body_validation['variables']
        ))
        
        # Save template
        if self.storage.save_template(template):
            return template
        else:
            raise RuntimeError("Failed to save template")
    
    async def send_notification(self, recipient: str, 
                              template_id: Optional[str] = None,
                              template_data: Optional[Dict[str, Any]] = None,
                              channel: Optional[NotificationChannel] = None,
                              priority: NotificationPriority = NotificationPriority.MEDIUM,
                              subject: Optional[str] = None,
                              body: Optional[str] = None,
                              attachments: Optional[List[str]] = None,
                              scheduled_at: Optional[datetime] = None,
                              send_immediately: bool = False) -> NotificationMessage:
        """Send notification message"""        
        message_data = {
            'message_id': str(uuid.uuid4()),
            'recipient': recipient,
            'priority': priority,
            'template_data': template_data or {},
            'attachments': attachments or [],
            'scheduled_at': scheduled_at
        }
        
        if template_id:
            # Use template
            template = self.storage.get_template(template_id)
            if not template:
                raise ValueError(f"Template not found: {template_id}")
            
            # Render template
            rendered_subject = self.template_engine.render_template(
                template.subject_template, template_data or {}
            )
            rendered_body = self.template_engine.render_template(
                template.body_template, template_data or {}
            )
            
            message = NotificationMessage(
                channel=template.channel,
                subject=rendered_subject,
                body=rendered_body,
                template_id=template_id,
                **message_data
            )
        else:
            # Direct message
            if not (channel and subject and body):
                raise ValueError("Channel, subject, and body are required for direct messages")
            
            message = NotificationMessage(
                channel=channel,
                subject=subject,
                body=body,
                **message_data
            )
        
        # Save message
        if not self.storage.save_message(message):
            raise RuntimeError("Failed to save notification message")
        
        # Send immediately if requested
        if send_immediately:
            await self._process_message(message)
        
        return message
    
    async def _process_message(self, message: NotificationMessage) -> DeliveryResult:
        """Process individual notification message"""        # Check rate limiting
        if not self._check_rate_limit(message.channel):
            # Schedule for retry
            message.status = NotificationStatus.RETRY
            message.scheduled_at = datetime.utcnow() + timedelta(minutes=5)
            self.storage.save_message(message)
            
            return DeliveryResult(
                success=False,
                message_id=message.message_id,
                channel=message.channel,
                recipient=message.recipient,
                delivery_time=0,
                error_message="Rate limit exceeded"
            )
        
        # Update attempt count
        message.attempts += 1
        message.last_attempt_at = datetime.utcnow()
        
        try:
            # Get channel handler
            channel_handler = self.channels.get(message.channel)
            if not channel_handler:
                raise RuntimeError(f"No handler configured for channel: {message.channel}")
            
            # Send notification
            if message.channel == NotificationChannel.WEBHOOK:
                # Webhook requires additional parameters
                webhook_url = message.metadata.get('webhook_url')
                if not webhook_url:
                    raise ValueError("Webhook URL not provided in message metadata")
                
                result = await channel_handler.send_notification(
                    message, webhook_url,
                    headers=message.metadata.get('headers'),
                    method=message.metadata.get('method', 'POST')
                )
            else:
                result = await channel_handler.send_notification(message)
            
            # Update message status
            if result.success:
                message.status = NotificationStatus.DELIVERED
                message.delivered_at = datetime.utcnow()
                message.error_message = None
            else:
                if message.attempts >= message.max_attempts:
                    message.status = NotificationStatus.FAILED
                else:
                    message.status = NotificationStatus.RETRY
                    # Exponential backoff
                    retry_delay = min(300, 30 * (2 ** (message.attempts - 1)))  # Max 5 minutes
                    message.scheduled_at = datetime.utcnow() + timedelta(seconds=retry_delay)
                
                message.error_message = result.error_message
            
            # Save updated message
            self.storage.save_message(message)
            
            # Save delivery result
            self.storage.save_delivery_result(result)
            
            # Update rate limit
            self._update_rate_limit(message.channel)
            
            return result
            
        except Exception as e:
            logger.error(f"Message processing failed: {str(e)}")
            
            # Update message status
            if message.attempts >= message.max_attempts:
                message.status = NotificationStatus.FAILED
            else:
                message.status = NotificationStatus.RETRY
                retry_delay = min(300, 30 * (2 ** (message.attempts - 1)))
                message.scheduled_at = datetime.utcnow() + timedelta(seconds=retry_delay)
            
            message.error_message = str(e)
            self.storage.save_message(message)
            
            result = DeliveryResult(
                success=False,
                message_id=message.message_id,
                channel=message.channel,
                recipient=message.recipient,
                delivery_time=0,
                error_message=str(e)
            )
            
            self.storage.save_delivery_result(result)
            
            return result
    
    def _check_rate_limit(self, channel: NotificationChannel) -> bool:
        """Check if channel rate limit allows sending"""        if channel not in self.rate_limits:
            return True
        
        rate_limit = self.rate_limits[channel]
        now = datetime.utcnow()
        
        # Reset counter if a minute has passed
        if (now - rate_limit['reset_time']).total_seconds() >= 60:
            rate_limit['count'] = 0
            rate_limit['reset_time'] = now
        
        return rate_limit['count'] < rate_limit['max_per_minute']
    
    def _update_rate_limit(self, channel: NotificationChannel):
        """Update rate limit counter"""        if channel in self.rate_limits:
            self.rate_limits[channel]['count'] += 1
    
    async def start_processing(self):
        """Start processing notification queue"""        self.processing = True
        
        while self.processing:
            try:
                # Get pending messages
                pending_messages = self.storage.get_pending_messages(limit=50)
                
                if pending_messages:
                    # Process messages concurrently
                    tasks = [self._process_message(msg) for msg in pending_messages]
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                # Wait before next processing cycle
                await asyncio.sleep(self.process_interval)
                
            except Exception as e:
                logger.error(f"Processing cycle failed: {str(e)}")
                await asyncio.sleep(self.process_interval)
    
    def stop_processing(self):
        """Stop processing notification queue"""        self.processing = False
    
    def get_delivery_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get delivery statistics for the specified time period"""        try:
            since_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
            
            with sqlite3.connect(self.storage.database_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Total messages
                cursor = conn.execute(
                    'SELECT COUNT(*) as count FROM notification_messages WHERE created_at >= ?',
                    (since_time,)
                )
                total_messages = cursor.fetchone()['count']
                
                # Status breakdown
                cursor = conn.execute('''
                    SELECT status, COUNT(*) as count 
                    FROM notification_messages 
                    WHERE created_at >= ? 
                    GROUP BY status
                ''', (since_time,))
                status_breakdown = {row['status']: row['count'] for row in cursor}
                
                # Channel breakdown
                cursor = conn.execute('''
                    SELECT channel, COUNT(*) as count 
                    FROM notification_messages 
                    WHERE created_at >= ? 
                    GROUP BY channel
                ''', (since_time,))
                channel_breakdown = {row['channel']: row['count'] for row in cursor}
                
                # Average delivery time
                cursor = conn.execute('''
                    SELECT AVG(delivery_time) as avg_time 
                    FROM delivery_results 
                    WHERE created_at >= ? AND success = 1
                ''', (since_time,))
                avg_delivery_time = cursor.fetchone()['avg_time'] or 0
                
                return {
                    'time_period_hours': hours,
                    'total_messages': total_messages,
                    'status_breakdown': status_breakdown,
                    'channel_breakdown': channel_breakdown,
                    'success_rate': status_breakdown.get('delivered', 0) / total_messages if total_messages > 0 else 0,
                    'average_delivery_time_seconds': avg_delivery_time
                }
                
        except Exception as e:
            logger.error(f"Failed to get delivery stats: {str(e)}")
            return {'error': str(e)}


# Predefined templates for IA Influencer Agent Platform
PLATFORM_TEMPLATES = {
    'content_protection_alert': {
        'name': 'Content Protection Alert',
        'subject': '🛡️ Content Protection Alert for "{{ content_title }}"',
        'body': '''
        <h2>Content Protection Alert</h2>
        <p>Hello {{ influencer_name }},</p>
        
        <p>Our AI protection system has detected potential unauthorized use of your content:</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #dc3545;">
            <strong>Content:</strong> {{ content_title }}<br>
            <strong>Detection Time:</strong> {{ detection_time | datetime }}<br>
            <strong>Violation Type:</strong> {{ violation_type }}<br>
            <strong>Platform:</strong> {{ platform_name }}<br>
            <strong>Similarity Score:</strong> {{ similarity_score }}%
        </div>
        
        <p>We have automatically initiated the following actions:</p>
        <ul>
            {% for action in actions_taken %}
            <li>{{ action }}</li>
            {% endfor %}
        </ul>
        
        <p>View the full report in your dashboard: <a href="{{ dashboard_url }}">{{ dashboard_url }}</a></p>
        
        <p>Best regards,<br>IA Influencer Agent Protection Team</p>
        ''',
        'channel': NotificationChannel.EMAIL
    },
    
    'collaboration_match': {
        'name': 'New Collaboration Match',
        'subject': '🎯 New Collaboration Opportunity with {{ brand_name }}',
        'body': '''
        <h2>New Collaboration Match Found!</h2>
        <p>Hello {{ influencer_name }},</p>
        
        <p>Great news! Our AI has found a perfect collaboration match for you:</p>
        
        <div style="background-color: #e8f5e8; padding: 15px; border-left: 4px solid #28a745;">
            <strong>Brand:</strong> {{ brand_name }}<br>
            <strong>Campaign:</strong> {{ campaign_title }}<br>
            <strong>Estimated Revenue:</strong> {{ estimated_revenue | currency }}<br>
            <strong>Match Score:</strong> {{ match_score }}%<br>
            <strong>Campaign Duration:</strong> {{ campaign_duration }} days
        </div>
        
        <h3>Why this is a great match:</h3>
        <ul>
            {% for reason in match_reasons %}
            <li>{{ reason }}</li>
            {% endfor %}
        </ul>
        
        <p><strong>Action Required:</strong> Review and respond to this opportunity within {{ response_deadline | datetime }} to secure your spot.</p>
        
        <p><a href="{{ collaboration_url }}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Collaboration Details</a></p>
        
        <p>Best regards,<br>IA Influencer Agent Team</p>
        ''',
        'channel': NotificationChannel.EMAIL
    },
    
    'revenue_report': {
        'name': 'Monthly Revenue Report',
        'subject': '📈 Your Monthly Revenue Report - {{ current_month }}',
        'body': '''
        <h2>Monthly Revenue Report</h2>
        <p>Hello {{ influencer_name }},</p>
        
        <p>Here's your performance summary for {{ current_month }}:</p>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
            <h3>Revenue Summary</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Total Revenue:</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{{ total_revenue | currency }}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Active Collaborations:</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{{ active_collaborations | format_number }}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Content Protected:</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{{ protected_content | format_number }}</td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><strong>Growth Rate:</strong></td>
                    <td style="padding: 8px;">{{ growth_rate }}%</td>
                </tr>
            </table>
        </div>
        
        <h3>Top Performing Content</h3>
        <ol>
            {% for content in top_content %}
            <li>{{ content.title }} - {{ content.revenue | currency }}</li>
            {% endfor %}
        </ol>
        
        <p>View your complete analytics dashboard: <a href="{{ dashboard_url }}">{{ dashboard_url }}</a></p>
        
        <p>Keep up the excellent work!</p>
        <p>Best regards,<br>IA Influencer Agent Team</p>
        ''',
        'channel': NotificationChannel.EMAIL
    }
}


class NotificationError(Exception):
    """Custom exception for notification errors"""    pass
