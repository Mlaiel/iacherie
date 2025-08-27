"""
IA-Influencer-Agent - Notification Channels System
Module: backend/core/events/notification_channels.py
Architecture: Multi-Channel Notification Delivery
Auteur: Fahed Mlaiel <mlaiel@live.de>

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT STRICT ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.

Description:
    Système de canaux de notification multi-plateformes pour la distribution
    temps réel des notifications dans la plateforme IA-Influencer-Agent.
"""

from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import asyncio
import json
import logging
import uuid
import aiohttp
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import websockets
import firebase_admin
from firebase_admin import messaging

from .event_bus import Event
from .event_types import EventType

logger = logging.getLogger(__name__)


class ChannelType(Enum):
    """Types de canaux de notification"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBSOCKET = "websocket"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    WEBHOOK = "webhook"


class NotificationPriority(Enum):
    """Priorité des notifications"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class DeliveryStatus(Enum):
    """Statut de livraison"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    CANCELLED = "cancelled"


@dataclass
class NotificationMessage:
    """Message de notification"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    recipient: str = ""
    subject: str = ""
    content: str = ""
    channel_type: ChannelType = ChannelType.EMAIL
    priority: NotificationPriority = NotificationPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    template_id: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Planification
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Tracking
    status: DeliveryStatus = DeliveryStatus.PENDING
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "recipient": self.recipient,
            "subject": self.subject,
            "content": self.content,
            "channel_type": self.channel_type.value,
            "priority": self.priority.value,
            "metadata": self.metadata,
            "attachments": self.attachments,
            "template_id": self.template_id,
            "variables": self.variables,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "status": self.status.value,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat()
        }


class NotificationChannel(ABC):
    """
    Classe de base pour les canaux de notification
    """
    
    def __init__(
        self,
        channel_id: str,
        channel_type: ChannelType,
        config: Dict[str, Any]
    ):
        self.channel_id = channel_id
        self.channel_type = channel_type
        self.config = config
        self.enabled = config.get("enabled", True)
        
        # Rate limiting
        self.rate_limit = config.get("rate_limit", 100)  # par minute
        self.rate_counter = 0
        self.rate_reset_time = datetime.now(timezone.utc)
        
        # Statistiques
        self.stats = {
            "sent": 0,
            "delivered": 0,
            "failed": 0,
            "total_time": 0.0
        }
    
    @abstractmethod
    async def send(self, message: NotificationMessage) -> bool:
        """Envoie une notification"""
        pass
    
    @abstractmethod
    async def validate_config(self) -> bool:
        """Valide la configuration du canal"""
        pass
    
    def can_send(self) -> bool:
        """Vérifie si le canal peut envoyer (rate limiting)"""
        if not self.enabled:
            return False
        
        now = datetime.now(timezone.utc)
        
        # Reset du compteur chaque minute
        if (now - self.rate_reset_time).seconds >= 60:
            self.rate_counter = 0
            self.rate_reset_time = now
        
        return self.rate_counter < self.rate_limit
    
    def _increment_counter(self):
        """Incrémente le compteur de rate limiting"""
        self.rate_counter += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du canal"""
        return {
            "channel_id": self.channel_id,
            "channel_type": self.channel_type.value,
            "enabled": self.enabled,
            "rate_limit": self.rate_limit,
            "rate_counter": self.rate_counter,
            "stats": self.stats.copy()
        }


class EmailChannel(NotificationChannel):
    """Canal de notification par email"""
    
    def __init__(self, channel_id: str, config: Dict[str, Any]):
        super().__init__(channel_id, ChannelType.EMAIL, config)
        
        # Configuration SMTP
        self.smtp_host = config.get("smtp_host", "localhost")
        self.smtp_port = config.get("smtp_port", 587)
        self.smtp_user = config.get("smtp_user", "")
        self.smtp_password = config.get("smtp_password", "")
        self.from_email = config.get("from_email", "noreply@ia-influencer-agent.com")
        self.from_name = config.get("from_name", "IA-Influencer-Agent")
        self.use_tls = config.get("use_tls", True)
        self.use_ssl = config.get("use_ssl", False)
    
    async def validate_config(self) -> bool:
        """Valide la configuration SMTP"""
        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
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
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Création du message email
            msg = MimeMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = message.recipient
            
            # Ajout des headers personnalisés
            if message.metadata:
                for key, value in message.metadata.items():
                    if key.startswith('X-'):
                        msg[key] = str(value)
            
            # Corps du message (HTML ou texte)
            if '<' in message.content:
                msg.attach(MimeText(message.content, 'html'))
            else:
                msg.attach(MimeText(message.content, 'plain'))
            
            # Connexion SMTP
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                if self.use_tls:
                    server.starttls()
            
            # Authentification
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            
            # Envoi
            text = msg.as_string()
            server.sendmail(self.from_email, [message.recipient], text)
            server.quit()
            
            # Mise à jour des statistiques
            self._increment_counter()
            self.stats["sent"] += 1
            
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            self.stats["total_time"] += duration
            
            message.status = DeliveryStatus.SENT
            message.sent_at = end_time
            
            logger.debug("Email sent to %s via channel %s", message.recipient, self.channel_id)
            return True
            
        except Exception as e:
            self.stats["failed"] += 1
            message.status = DeliveryStatus.FAILED
            message.error_message = str(e)
            
            logger.error("Failed to send email via channel %s: %s", self.channel_id, e)
            return False


class WebSocketChannel(NotificationChannel):
    """Canal de notification par WebSocket"""
    
    def __init__(self, channel_id: str, config: Dict[str, Any]):
        super().__init__(channel_id, ChannelType.WEBSOCKET, config)
        
        # Configuration WebSocket
        self.host = config.get("host", "0.0.0.0")
        self.port = config.get("port", 8765)
        self.path = config.get("path", "/notifications")
        
        # Connexions actives
        self.connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.user_connections: Dict[str, Set[str]] = {}
        
        # Serveur WebSocket
        self.server = None
    
    async def start_server(self):
        """Démarre le serveur WebSocket"""
        try:
            self.server = await websockets.serve(
                self.handle_connection,
                self.host,
                self.port
            )
            logger.info("WebSocket server started on %s:%d", self.host, self.port)
            
        except Exception as e:
            logger.error("Failed to start WebSocket server: %s", e)
            raise
    
    async def stop_server(self):
        """Arrête le serveur WebSocket"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("WebSocket server stopped")
    
    async def handle_connection(self, websocket, path):
        """Gère une nouvelle connexion WebSocket"""
        connection_id = str(uuid.uuid4())
        self.connections[connection_id] = websocket
        
        try:
            # Attente du message d'authentification
            auth_message = await asyncio.wait_for(websocket.recv(), timeout=30)
            auth_data = json.loads(auth_message)
            
            user_id = auth_data.get("user_id")
            if not user_id:
                await websocket.close(4001, "Authentication required")
                return
            
            # Association utilisateur-connexion
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
            
            # Confirmation de connexion
            await websocket.send(json.dumps({
                "type": "connection_established",
                "connection_id": connection_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))
            
            logger.debug("WebSocket connection established for user %s", user_id)
            
            # Maintien de la connexion
            async for message in websocket:
                # Traitement des messages clients (ping/pong, etc.)
                try:
                    data = json.loads(message)
                    if data.get("type") == "ping":
                        await websocket.send(json.dumps({"type": "pong"}))
                except json.JSONDecodeError:
                    pass
        
        except asyncio.TimeoutError:
            await websocket.close(4000, "Authentication timeout")
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error("WebSocket connection error: %s", e)
        finally:
            # Nettoyage
            self._cleanup_connection(connection_id)
    
    def _cleanup_connection(self, connection_id: str):
        """Nettoie une connexion fermée"""
        if connection_id in self.connections:
            del self.connections[connection_id]
        
        # Nettoyage des associations utilisateur
        for user_id, connections in self.user_connections.items():
            connections.discard(connection_id)
    
    async def validate_config(self) -> bool:
        """Valide la configuration WebSocket"""
        # Vérification basique de la configuration
        return isinstance(self.port, int) and 1 <= self.port <= 65535
    
    async def send(self, message: NotificationMessage) -> bool:
        """Envoie une notification WebSocket"""
        if not self.can_send():
            return False
        
        try:
            # Extraction de l'utilisateur destinataire
            user_id = message.metadata.get("user_id") or message.recipient
            
            if not user_id or user_id not in self.user_connections:
                logger.debug("No WebSocket connections for user %s", user_id)
                return False
            
            # Préparation du message
            ws_message = {
                "type": "notification",
                "id": message.message_id,
                "subject": message.subject,
                "content": message.content,
                "priority": message.priority.value,
                "metadata": message.metadata,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            message_json = json.dumps(ws_message)
            sent_count = 0
            
            # Envoi à toutes les connexions de l'utilisateur
            connections_to_remove = []
            for connection_id in self.user_connections[user_id]:
                try:
                    websocket = self.connections.get(connection_id)
                    if websocket:
                        await websocket.send(message_json)
                        sent_count += 1
                except websockets.exceptions.ConnectionClosed:
                    connections_to_remove.append(connection_id)
                except Exception as e:
                    logger.error("Failed to send WebSocket message to %s: %s", connection_id, e)
                    connections_to_remove.append(connection_id)
            
            # Nettoyage des connexions fermées
            for connection_id in connections_to_remove:
                self._cleanup_connection(connection_id)
            
            if sent_count > 0:
                self._increment_counter()
                self.stats["sent"] += 1
                message.status = DeliveryStatus.DELIVERED
                message.delivered_at = datetime.now(timezone.utc)
                
                logger.debug("WebSocket notification sent to %d connections for user %s", 
                           sent_count, user_id)
                return True
            
            return False
            
        except Exception as e:
            self.stats["failed"] += 1
            message.status = DeliveryStatus.FAILED
            message.error_message = str(e)
            
            logger.error("Failed to send WebSocket notification: %s", e)
            return False


class PushNotificationChannel(NotificationChannel):
    """Canal de notifications push (Firebase)"""
    
    def __init__(self, channel_id: str, config: Dict[str, Any]):
        super().__init__(channel_id, ChannelType.PUSH, config)
        
        # Configuration Firebase
        self.service_account_path = config.get("service_account_path")
        self.project_id = config.get("project_id")
        
        # Initialisation Firebase
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialise Firebase Admin SDK"""
        try:
            if not firebase_admin._apps:
                if self.service_account_path:
                    cred = firebase_admin.credentials.Certificate(self.service_account_path)
                    firebase_admin.initialize_app(cred)
                else:
                    # Utilisation des credentials par défaut
                    firebase_admin.initialize_app()
            
            logger.info("Firebase Admin SDK initialized")
            
        except Exception as e:
            logger.error("Failed to initialize Firebase: %s", e)
    
    async def validate_config(self) -> bool:
        """Valide la configuration Firebase"""
        try:
            # Test simple d'accès à Firebase
            if firebase_admin._apps:
                return True
            return False
            
        except Exception as e:
            logger.error("Push notification validation failed: %s", e)
            return False
    
    async def send(self, message: NotificationMessage) -> bool:
        """Envoie une notification push"""
        if not self.can_send():
            return False
        
        try:
            # Le recipient doit être un token FCM
            fcm_token = message.recipient
            
            # Construction du message Firebase
            firebase_message = messaging.Message(
                notification=messaging.Notification(
                    title=message.subject,
                    body=message.content
                ),
                data=message.metadata,
                token=fcm_token
            )
            
            # Envoi
            response = messaging.send(firebase_message)
            
            self._increment_counter()
            self.stats["sent"] += 1
            message.status = DeliveryStatus.SENT
            message.sent_at = datetime.now(timezone.utc)
            
            logger.debug("Push notification sent with response: %s", response)
            return True
            
        except Exception as e:
            self.stats["failed"] += 1
            message.status = DeliveryStatus.FAILED
            message.error_message = str(e)
            
            logger.error("Failed to send push notification: %s", e)
            return False


class SlackChannel(NotificationChannel):
    """Canal de notification Slack"""
    
    def __init__(self, channel_id: str, config: Dict[str, Any]):
        super().__init__(channel_id, ChannelType.SLACK, config)
        
        # Configuration Slack
        self.webhook_url = config.get("webhook_url")
        self.bot_token = config.get("bot_token")
        self.default_channel = config.get("default_channel", "#general")
        self.username = config.get("username", "IA-Influencer-Agent")
        self.icon_emoji = config.get("icon_emoji", ":robot_face:")
    
    async def validate_config(self) -> bool:
        """Valide la configuration Slack"""
        if not self.webhook_url and not self.bot_token:
            return False
        
        try:
            # Test avec webhook URL
            if self.webhook_url:
                async with aiohttp.ClientSession() as session:
                    test_payload = {"text": "Test connection"}
                    async with session.post(self.webhook_url, json=test_payload) as response:
                        return response.status == 200
            
            return True
            
        except Exception as e:
            logger.error("Slack channel validation failed: %s", e)
            return False
    
    async def send(self, message: NotificationMessage) -> bool:
        """Envoie une notification Slack"""
        if not self.can_send():
            return False
        
        try:
            # Détermination du canal
            channel = message.metadata.get("slack_channel", self.default_channel)
            
            # Construction du payload
            payload = {
                "channel": channel,
                "username": self.username,
                "icon_emoji": self.icon_emoji,
                "text": message.subject,
                "attachments": [
                    {
                        "color": self._get_color_for_priority(message.priority),
                        "text": message.content,
                        "footer": "IA-Influencer-Agent",
                        "ts": int(datetime.now(timezone.utc).timestamp())
                    }
                ]
            }
            
            # Envoi via webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        self._increment_counter()
                        self.stats["sent"] += 1
                        message.status = DeliveryStatus.SENT
                        message.sent_at = datetime.now(timezone.utc)
                        
                        logger.debug("Slack notification sent to %s", channel)
                        return True
                    else:
                        raise Exception(f"Slack API returned status {response.status}")
            
        except Exception as e:
            self.stats["failed"] += 1
            message.status = DeliveryStatus.FAILED
            message.error_message = str(e)
            
            logger.error("Failed to send Slack notification: %s", e)
            return False
    
    def _get_color_for_priority(self, priority: NotificationPriority) -> str:
        """Retourne la couleur Slack selon la priorité"""
        color_map = {
            NotificationPriority.LOW: "#36a64f",      # Vert
            NotificationPriority.NORMAL: "#ffaa00",   # Orange
            NotificationPriority.HIGH: "#ff6600",     # Orange foncé
            NotificationPriority.URGENT: "#ff0000"    # Rouge
        }
        return color_map.get(priority, "#36a64f")


class TelegramChannel(NotificationChannel):
    """Canal de notification Telegram"""
    
    def __init__(self, channel_id: str, config: Dict[str, Any]):
        super().__init__(channel_id, ChannelType.TELEGRAM, config)
        
        # Configuration Telegram
        self.bot_token = config.get("bot_token")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def validate_config(self) -> bool:
        """Valide la configuration Telegram"""
        if not self.bot_token:
            return False
        
        try:
            # Test de l'API Telegram
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/getMe") as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error("Telegram channel validation failed: %s", e)
            return False
    
    async def send(self, message: NotificationMessage) -> bool:
        """Envoie une notification Telegram"""
        if not self.can_send():
            return False
        
        try:
            # Le recipient doit être un chat_id
            chat_id = message.recipient
            
            # Construction du message
            text = f"*{message.subject}*\n\n{message.content}"
            
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            
            # Envoi via API Telegram
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/sendMessage",
                    json=payload
                ) as response:
                    
                    if response.status == 200:
                        self._increment_counter()
                        self.stats["sent"] += 1
                        message.status = DeliveryStatus.SENT
                        message.sent_at = datetime.now(timezone.utc)
                        
                        logger.debug("Telegram notification sent to %s", chat_id)
                        return True
                    else:
                        error_data = await response.json()
                        raise Exception(f"Telegram API error: {error_data}")
            
        except Exception as e:
            self.stats["failed"] += 1
            message.status = DeliveryStatus.FAILED
            message.error_message = str(e)
            
            logger.error("Failed to send Telegram notification: %s", e)
            return False


# Registry des canaux disponibles
CHANNEL_CLASSES = {
    ChannelType.EMAIL: EmailChannel,
    ChannelType.WEBSOCKET: WebSocketChannel,
    ChannelType.PUSH: PushNotificationChannel,
    ChannelType.SLACK: SlackChannel,
    ChannelType.TELEGRAM: TelegramChannel
}


def create_channel(
    channel_type: ChannelType,
    channel_id: str,
    config: Dict[str, Any]
) -> NotificationChannel:
    """Factory pour créer un canal de notification"""
    channel_class = CHANNEL_CLASSES.get(channel_type)
    
    if not channel_class:
        raise ValueError(f"Unsupported channel type: {channel_type}")
    
    return channel_class(channel_id, config)
