"""IA-Influencer-Agent - Event Publisher and Notification System
Module: backend/core/events/event_publisher.py
Architecture: Event Publishing and Real-time Notifications
Auteur: Fahed Mlaiel <mlaiel@live.de>

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT STRICT ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.

Description:
    Système de publication d'événements avec notifications temps réel,
    intégrations multi-canaux et orchestration pour la plateforme IA-Influencer-Agent.
"""

from typing import Any, Dict, List, Optional, Union, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod

import aiohttp
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import redis.asyncio as redis
from websockets.server import serve, WebSocketServerProtocol
import slack_sdk.web.async_client as slack

from .event_bus import Event, EventPriority, EventStatus
from .event_types import EventType

logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """
Priorité des notifications"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(Enum):
    """Statut des notifications"""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ChannelType(Enum):
    """Types de canaux de notification"""

    EMAIL = "email"
    WEBSOCKET = "websocket"
    PUSH = "push"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    DISCORD = "discord"


@dataclass
class NotificationTemplate:
    """Modèle de notification"""
    template_id: str
    channel_type: ChannelType
    subject_template: str
    body_template: str
    variables: List[str] = field(default_factory=list)
    locale: str = "en"
    enabled: bool = True


@dataclass
class NotificationMessage:
    """Message de notification"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event: Optional[Event] = None
    channel_type: ChannelType = ChannelType.EMAIL
    recipient: str = ""
    subject: str = ""
    body: str = ""
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    template_id: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "event_id": self.event.id if self.event else None,
            "channel_type": self.channel_type.value,
            "recipient": self.recipient,
            "subject": self.subject,
            "body": self.body,
            "priority": self.priority.value,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata,
            "template_id": self.template_id,
            "variables": self.variables
        }


class NotificationChannel(ABC):
    """Interface pour les canaux de notification"""
    
    def __init__(self, channel_id: str, config: Dict[str, Any]):
        self.channel_id = channel_id
        self.config = config
        self.enabled = config.get("enabled", True)
        self.rate_limit = config.get("rate_limit", 100)  # messages/minute
        self._sent_count = 0
        self._last_reset = datetime.now(timezone.utc)
    
    @abstractmethod
    async def send(self, message: NotificationMessage) -> bool:
        """Envoie une notification"""
        pass
    
    @abstractmethod
    async def validate_config(self) -> bool:
        """
Valide la configuration du canal"""
        pass
    
    def can_send(self) -> bool:
        """
Vérifie si le canal peut envoyer (rate limiting)"""
        if not self.enabled:
            return False
        
        now = datetime.now(timezone.utc)
        if (now - self._last_reset).seconds >= 60:
            self._sent_count = 0
            self._last_reset = now
        
        return self._sent_count < self.rate_limit
    
    def increment_sent(self):
        """
Incrémente le compteur d'envois"""
        self._sent_count += 1


class EmailChannel(NotificationChannel):
    """
Canal de notification par email"""
    
    def __init__(self, channel_id: str, config: Dict[str, Any]):
        super().__init__(channel_id, config)
        self.smtp_host = config.get("smtp_host", "localhost")
        self.smtp_port = config.get("smtp_port", 587)
        self.smtp_user = config.get("smtp_user", "")
        self.smtp_password = config.get("smtp_password", "")
        self.from_email = config.get("from_email", "noreply@ia-influencer-agent.com")
        self.use_tls = config.get("use_tls", True)
    
    async def validate_config(self) -> bool:
        """Valide la configuration SMTP"""
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            if self.use_tls:
                server.starttls()
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            server.quit()
            return True
        except Exception as e:
            logger.error("Email channel validation failed: %s", e)
            return False
    
    async def send(self, message: NotificationMessage) -> bool:
        """Envoie un email"""
        if not self.can_send():
            logger.warning("Email rate limit exceeded for channel %s", self.channel_id)
            return False
        
        try:
            # Création du message
            msg = MimeMultipart()
            msg['From'] = self.from_email
            msg['To'] = message.recipient
            msg['Subject'] = message.subject
            
            # Corps du message
            msg.attach(MimeText(message.body, 'html' if '<' in message.body else 'plain'))
            
            # Envoi
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            if self.use_tls:
                server.starttls()
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            
            server.send_message(msg)
            server.quit()
            
            self.increment_sent()
            logger.debug("Email sent to %s via channel %s", message.recipient, self.channel_id)
            return True
            
        except Exception as e:
            logger.error("Failed to send email via channel %s: %s", self.channel_id, e)
            return False


class WebSocketChannel(NotificationChannel):
    """Canal de notification par WebSocket"""
    
    def __init__(self, channel_id: str, config: Dict[str, Any]):
        super().__init__(channel_id, config)
        self.connections: Dict[str, WebSocketServerProtocol] = {}
        self.user_connections: Dict[str, Set[str]] = {}
        self.port = config.get("port", 8765)
        self.host = config.get("host", "0.0.0.0")
        self.server = None
    
    async def start_server(self):
        """Démarre le serveur WebSocket"""
        self.server = await serve(
            self.handle_connection,
            self.host,
            self.port
        )
        logger.info("WebSocket server started on %s:%d", self.host, self.port)
    
    async def stop_server(self):
        """Arrête le serveur WebSocket"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
    
    async def handle_connection(self, websocket, path):
        """
Gère une nouvelle connexion WebSocket"""
        connection_id = str(uuid.uuid4())
        self.connections[connection_id] = websocket
        
        try:
            # Authentification (simplifiée)
            auth_message = await websocket.recv()
            auth_data = json.loads(auth_message)
            user_id = auth_data.get("user_id")
            
            if user_id:
                if user_id not in self.user_connections:
                    self.user_connections[user_id] = set()
                self.user_connections[user_id].add(connection_id)
                logger.debug("WebSocket connection established for user %s", user_id)
            
            # Maintien de la connexion
            await websocket.wait_closed()
            
        except Exception as e:
            logger.error("WebSocket connection error: %s", e)
        finally:
            # Nettoyage
            if connection_id in self.connections:
                del self.connections[connection_id]
            
            for user_id, connections in self.user_connections.items():
                connections.discard(connection_id)
    
    async def validate_config(self) -> bool:
        """Valide la configuration WebSocket"""
        return True  # Configuration simple
    
    async def send(self, message: NotificationMessage) -> bool:
        """
Envoie via WebSocket"""
        if not self.can_send():
            return False
        
        try:
            # Extraction user_id depuis event ou metadata
            user_id = None
            if message.event:
                user_id = message.event.user_id
            if not user_id and "user_id" in message.metadata:
                user_id = message.metadata["user_id"]
            
            if not user_id:
                logger.warning("No user_id found for WebSocket message")
                return False
            
            # Recherche des connexions utilisateur
            if user_id not in self.user_connections:
                logger.debug("No WebSocket connections for user %s", user_id)
                return False
            
            # Préparation du message
            ws_message = {
                "type": "notification",
                "message_id": message.message_id,
                "subject": message.subject,
                "body": message.body,
                "priority": message.priority.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metadata": message.metadata
            }
            
            message_json = json.dumps(ws_message)
            sent_count = 0
            
            # Envoi à toutes les connexions de l'utilisateur
            for connection_id in self.user_connections[user_id].copy():
                try:
                    websocket = self.connections.get(connection_id)
                    if websocket:
                        await websocket.send(message_json)
                        sent_count += 1
                except Exception as e:
                    logger.error("Failed to send WebSocket message to connection %s: %s", 
                               connection_id, e)
                    # Nettoyage connexion fermée
                    self.user_connections[user_id].discard(connection_id)
                    if connection_id in self.connections:
                        del self.connections[connection_id]
            
            if sent_count > 0:
                self.increment_sent()
                logger.debug("WebSocket message sent to %d connections for user %s", 
                           sent_count, user_id)
                return True
            
            return False
            
        except Exception as e:
            logger.error("Failed to send WebSocket message: %s", e)
            return False


class SlackChannel(NotificationChannel):
    """Canal de notification Slack"""
    
    def __init__(self, channel_id: str, config: Dict[str, Any]):
        super().__init__(channel_id, config)
        self.bot_token = config.get("bot_token", "")
        self.default_channel = config.get("default_channel", "#general")
        self.client = slack.AsyncWebClient(token=self.bot_token)
    
    async def validate_config(self) -> bool:
        """Valide la configuration Slack"""
        try:
            response = await self.client.auth_test()
            return response["ok"]
        except Exception as e:
            logger.error("Slack channel validation failed: %s", e)
            return False
    
    async def send(self, message: NotificationMessage) -> bool:
        """Envoie via Slack"""
        if not self.can_send():
            return False
        
        try:
            # Détermination du canal
            channel = message.metadata.get("slack_channel", self.default_channel)
            
            # Formatage du message
            slack_message = {
                "channel": channel,
                "text": message.subject,
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{message.subject}*\n{message.body}"
                        }
                    }
                ]
            }
            
            # Ajout de métadonnées
            if message.event:
                slack_message["blocks"].append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Event ID: `{message.event.id}` | Type: `{message.event.type}`"
                        }
                    ]
                })
            
            response = await self.client.chat_postMessage(**slack_message)
            
            if response["ok"]:
                self.increment_sent()
                logger.debug("Slack message sent to %s", channel)
                return True
            else:
                logger.error("Slack API error: %s", response.get("error"))
                return False
                
        except Exception as e:
            logger.error("Failed to send Slack message: %s", e)
            return False


class WebhookChannel(NotificationChannel):
    """Canal de notification par webhook"""
    
    def __init__(self, channel_id: str, config: Dict[str, Any]):
        super().__init__(channel_id, config)
        self.webhook_url = config.get("webhook_url", "")
        self.headers = config.get("headers", {})
        self.timeout = config.get("timeout", 10)
        self.verify_ssl = config.get("verify_ssl", True)
    
    async def validate_config(self) -> bool:
        """Valide la configuration webhook"""
        if not self.webhook_url:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(
                    self.webhook_url,
                    timeout=aiohttp.ClientTimeout(total=5),
                    ssl=self.verify_ssl
                ) as response:
                    return response.status < 500
        except Exception as e:
            logger.error("Webhook validation failed: %s", e)
            return False
    
    async def send(self, message: NotificationMessage) -> bool:
        """Envoie via webhook"""
        if not self.can_send():
            return False
        
        try:
            # Préparation du payload
            payload = {
                "message_id": message.message_id,
                "channel_type": message.channel_type.value,
                "subject": message.subject,
                "body": message.body,
                "priority": message.priority.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metadata": message.metadata
            }
            
            if message.event:
                payload["event"] = message.event.to_dict()
            
            # Envoi HTTP
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    ssl=self.verify_ssl
                ) as response:
                    success = response.status < 400
                    
                    if success:
                        self.increment_sent()
                        logger.debug("Webhook sent to %s (status: %d)", 
                                   self.webhook_url, response.status)
                    else:
                        logger.error("Webhook failed with status %d", response.status)
                    
                    return success
                    
        except Exception as e:
            logger.error("Failed to send webhook: %s", e)
            return False


class EventPublisher:
    """
    Système principal de publication d'événements avec notifications
    """
    
    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        enable_persistence: bool = True
    ):
        self.redis_client = redis_client
        self.enable_persistence = enable_persistence
        
        # Stockage des canaux et templates
        self._channels: Dict[str, NotificationChannel] = {}
        self._templates: Dict[str, NotificationTemplate] = {}
        self._subscriptions: Dict[str, List[str]] = {}  # event_type -> channel_ids
        
        # Queue de messages
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._processing = False
        
        # Statistiques
        self._stats = {
            "events_published": 0,
            "notifications_sent": 0,
            "notifications_failed": 0,
            "channels_count": 0,
            "templates_count": 0
        }
        
        logger.info("EventPublisher initialized")
    
    async def start(self):
        """Démarre le système de publication"""
        if self._processing:
            return
        
        self._processing = True
        asyncio.create_task(self._process_messages())
        logger.info("EventPublisher started")
    
    async def stop(self):
        """Arrête le système de publication"""
        self._processing = False
        
        # Arrêt des serveurs WebSocket
        for channel in self._channels.values():
            if isinstance(channel, WebSocketChannel) and channel.server:
                await channel.stop_server()
        
        logger.info("EventPublisher stopped")
    
    def register_channel(self, channel: NotificationChannel) -> bool:
        """Enregistre un canal de notification"""
        try:
            self._channels[channel.channel_id] = channel
            self._stats["channels_count"] += 1
            logger.info("Channel registered: %s (%s)", 
                       channel.channel_id, type(channel).__name__)
            return True
        except Exception as e:
            logger.error("Failed to register channel %s: %s", channel.channel_id, e)
            return False
    
    def register_template(self, template: NotificationTemplate) -> bool:
        """Enregistre un template de notification"""
        try:
            self._templates[template.template_id] = template
            self._stats["templates_count"] += 1
            logger.info("Template registered: %s", template.template_id)
            return True
        except Exception as e:
            logger.error("Failed to register template %s: %s", template.template_id, e)
            return False
    
    def subscribe_channel(self, event_type: str, channel_id: str):
        """Abonne un canal à un type d'événement"""
        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = []
        
        if channel_id not in self._subscriptions[event_type]:
            self._subscriptions[event_type].append(channel_id)
            logger.debug("Channel %s subscribed to %s", channel_id, event_type)
    
    async def publish_event(self, event: Event) -> Dict[str, Any]:
        """Publie un événement avec notifications"""
        self._stats["events_published"] += 1
        
        # Recherche des canaux abonnés
        subscribed_channels = self._get_subscribed_channels(event.type)
        
        if not subscribed_channels:
            logger.debug("No channels subscribed to event type %s", event.type)
            return {"event_id": event.id, "notifications_sent": 0}
        
        # Création des messages de notification
        messages = await self._create_notification_messages(event, subscribed_channels)
        
        # Ajout à la queue de traitement
        for message in messages:
            await self._message_queue.put(message)
        
        return {
            "event_id": event.id,
            "notifications_queued": len(messages),
            "channels": [ch.channel_id for ch in subscribed_channels]
        }
    
    async def send_notification(self, message: NotificationMessage) -> bool:
        """Envoie une notification directement"""
        await self._message_queue.put(message)
        return True
    
    def _get_subscribed_channels(self, event_type: str) -> List[NotificationChannel]:
        """
Trouve les canaux abonnés à un type d'événement"""
        channels = []
        
        # Recherche exacte et wildcard
        for subscription_type, channel_ids in self._subscriptions.items():
            if (subscription_type == "*" or 
                event_type.startswith(subscription_type) or
                subscription_type == event_type):
                
                for channel_id in channel_ids:
                    if channel_id in self._channels:
                        channels.append(self._channels[channel_id])
        
        return channels
    
    async def _create_notification_messages(
        self, 
        event: Event, 
        channels: List[NotificationChannel]
    ) -> List[NotificationMessage]:
        """Crée les messages de notification pour un événement"""
        messages = []
        
        for channel in channels:
            try:
                # Recherche d'un template approprié
                template = self._find_template(event.type, channel.channel_id)
                
                if template:
                    message = await self._create_from_template(event, template, channel)
                else:
                    message = await self._create_default_message(event, channel)
                
                if message:
                    messages.append(message)
                    
            except Exception as e:
                logger.error("Failed to create notification message for channel %s: %s",
                           channel.channel_id, e)
        
        return messages
    
    def _find_template(self, event_type: str, channel_id: str) -> Optional[NotificationTemplate]:
        """Trouve un template approprié"""
        # Logic simplifiée - amélioration possible avec système de matching avancé
        for template in self._templates.values():
            if template.enabled and event_type.startswith(template.template_id.split('.')[0]):
                return template
        return None
    
    async def _create_from_template(
        self, 
        event: Event, 
        template: NotificationTemplate,
        channel: NotificationChannel
    ) -> Optional[NotificationMessage]:
        """
Crée un message depuis un template"""
        try:
            # Variables pour le template
            variables = {
                "event_id": event.id,
                "event_type": event.type,
                "user_id": event.user_id or "unknown",
                "timestamp": event.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                **event.data,
                **event.metadata
            }
            
            # Remplacement des variables
            subject = template.subject_template
            body = template.body_template
            
            for var, value in variables.items():
                subject = subject.replace(f"{{{{{var}}}}}", str(value))
                body = body.replace(f"{{{{{var}}}}}", str(value))
            
            return NotificationMessage(
                event=event,
                channel_type=template.channel_type,
                recipient=event.user_id or "",
                subject=subject,
                body=body,
                template_id=template.template_id,
                variables=variables
            )
            
        except Exception as e:
            logger.error("Failed to create message from template %s: %s", 
                        template.template_id, e)
            return None
    
    async def _create_default_message(
        self, 
        event: Event, 
        channel: NotificationChannel
    ) -> NotificationMessage:
        """Crée un message par défaut"""
        subject = f"IA-Influencer-Agent: {event.type}"
        body = f"Event {event.id} occurred at {event.timestamp}\nType: {event.type}\nData: {json.dumps(event.data, indent=2)}"
        
        return NotificationMessage(
            event=event,
            channel_type=ChannelType(channel.channel_id.split('_')[0]),
            recipient=event.user_id or "",
            subject=subject,
            body=body
        )
    
    async def _process_messages(self):
        """Traitement continu des messages en queue"""
        while self._processing:
            try:
                message = await asyncio.wait_for(
                    self._message_queue.get(), timeout=1.0
                )
                
                await self._send_message(message)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error("Error in message processing: %s", e)
    
    async def _send_message(self, message: NotificationMessage):
        """Envoie un message via le canal approprié"""
        try:
            # Recherche du canal approprié
            channel = None
            for ch in self._channels.values():
                if isinstance(ch, EmailChannel) and message.channel_type == ChannelType.EMAIL:
                    channel = ch
                    break
                elif isinstance(ch, WebSocketChannel) and message.channel_type == ChannelType.WEBSOCKET:
                    channel = ch
                    break
                elif isinstance(ch, SlackChannel) and message.channel_type == ChannelType.SLACK:
                    channel = ch
                    break
                elif isinstance(ch, WebhookChannel) and message.channel_type == ChannelType.WEBHOOK:
                    channel = ch
                    break
            
            if not channel:
                logger.warning("No channel found for type %s", message.channel_type.value)
                return
            
            # Envoi
            success = await channel.send(message)
            
            if success:
                self._stats["notifications_sent"] += 1
                logger.debug("Notification sent: %s via %s", 
                           message.message_id, channel.channel_id)
            else:
                self._stats["notifications_failed"] += 1
                logger.warning("Failed to send notification %s", message.message_id)
                
        except Exception as e:
            self._stats["notifications_failed"] += 1
            logger.error("Error sending message %s: %s", message.message_id, e)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques"""
        return {
            "stats": self._stats.copy(),
            "queue_size": self._message_queue.qsize(),
            "channels": list(self._channels.keys()),
            "templates": list(self._templates.keys()),
            "subscriptions": len(self._subscriptions)
        }


# Service de notification global
class NotificationService:
    """Service global de notifications"""
    
    def __init__(self):
        self.publisher = EventPublisher()
        self._initialized = False
    
    async def initialize(self, config: Dict[str, Any]):
        """
Initialise le service avec la configuration"""
        if self._initialized:
            return
        
        # Configuration des canaux
        if "email" in config:
            email_channel = EmailChannel("email_default", config["email"])
            self.publisher.register_channel(email_channel)
        
        if "websocket" in config:
            ws_channel = WebSocketChannel("websocket_default", config["websocket"])
            await ws_channel.start_server()
            self.publisher.register_channel(ws_channel)
        
        if "slack" in config:
            slack_channel = SlackChannel("slack_default", config["slack"])
            self.publisher.register_channel(slack_channel)
        
        if "webhook" in config:
            webhook_channel = WebhookChannel("webhook_default", config["webhook"])
            self.publisher.register_channel(webhook_channel)
        
        # Templates par défaut
        self._register_default_templates()
        
        # Abonnements par défaut
        self._setup_default_subscriptions()
        
        await self.publisher.start()
        self._initialized = True
        logger.info("NotificationService initialized")
    
    def _register_default_templates(self):
        """Enregistre les templates par défaut"""
        templates = [
            NotificationTemplate(
                template_id="content_uploaded",
                channel_type=ChannelType.EMAIL,
                subject_template="Content Uploaded - {{event_type}}",
                body_template="Your content {{content_id}} has been uploaded successfully.\nTimestamp: {{timestamp}}"
            ),
            NotificationTemplate(
                template_id="protection_violation",
                channel_type=ChannelType.EMAIL,
                subject_template="URGENT: Content Violation Detected",
                body_template="A violation of your content has been detected:\nURL: {{violation_url}}\nSimilarity: {{similarity_score}}%"
            ),
            NotificationTemplate(
                template_id="monetization_revenue",
                channel_type=ChannelType.EMAIL,
                subject_template="Revenue Detected - {{platform}}",
                body_template="Revenue of {{revenue_amount}} {{currency}} detected on {{platform}}"
            )
        ]
        
        for template in templates:
            self.publisher.register_template(template)
    
    def _setup_default_subscriptions(self):
        """Configure les abonnements par défaut"""
        subscriptions = {
            "content.*": ["email_default", "websocket_default"],
            "protection.violation.*": ["email_default", "slack_default", "websocket_default"],
            "monetization.*": ["email_default", "websocket_default"],
            "system.error.*": ["slack_default", "webhook_default"]
        }
        
        for event_type, channels in subscriptions.items():
            for channel_id in channels:
                self.publisher.subscribe_channel(event_type, channel_id)
    
    async def notify(self, event: Event) -> Dict[str, Any]:
        """Envoie les notifications pour un événement"""
        return await self.publisher.publish_event(event)
    
    async def send_direct(self, message: NotificationMessage) -> bool:
        """
Envoie une notification directe"""
        return await self.publisher.send_notification(message)


# Instance globale
notification_service = NotificationService()
