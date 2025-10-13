"""🚀 WebSocket Manager - IA Influencer Agent Platform Enterprise
============================================================
Module: backend/platform_core/communication/websocket_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 GESTIONNAIRE WEBSOCKET REAL-TIME
Gestion des connexions WebSocket pour communication temps réel
- Connexions persistantes sécurisées
- Broadcasting intelligent multi-client
- Reconnexion automatique et heartbeat
- Gestion d'état avancée par session
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Set, Any, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import weakref

import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException
from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as redis
from pydantic import BaseModel, Field

# Configuration
logger = logging.getLogger(__name__)

class ConnectionState(Enum):
    """États des connexions WebSocket"""

    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    ERROR = "error"

class MessageType(Enum):
    """Types de messages WebSocket"""

    HEARTBEAT = "heartbeat"
    AUTH = "auth"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    BROADCAST = "broadcast"
    DIRECT = "direct"
    NOTIFICATION = "notification"
    STATUS = "status"
    ERROR = "error"

@dataclass
class WebSocketMessage:
    """Structure des messages WebSocket"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.DIRECT
    sender_id: Optional[str] = None
    recipient_id: Optional[str] = None
    channel: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: int = 1  # 1=low, 5=high
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convertit le message en dictionnaire"""
        return {
            "message_id": self.message_id,
            "type": self.type.value,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "channel": self.channel,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }

@dataclass
class ConnectionInfo:
    """Informations de connexion WebSocket"""
    connection_id: str
    user_id: Optional[str]
    websocket: WebSocket
    state: ConnectionState
    connected_at: datetime
    last_heartbeat: datetime
    subscriptions: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    message_queue: List[WebSocketMessage] = field(default_factory=list)
    
class ConnectionManager:
    """
Gestionnaire de connexions WebSocket"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.connections: Dict[str, ConnectionInfo] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.channel_subscribers: Dict[str, Set[str]] = {}  # channel -> connection_ids
        self.redis_client = redis_client
        self.heartbeat_interval = 30  # secondes
        self.message_retention = timedelta(hours=24)
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """
Démarre le gestionnaire de connexions"""
        logger.info("Démarrage du gestionnaire de connexions WebSocket")
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
    async def stop(self):
        """Arrête le gestionnaire de connexions"""
        logger.info("Arrêt du gestionnaire de connexions WebSocket")
        if self._cleanup_task:
            self._cleanup_task.cancel()
            
        # Fermer toutes les connexions
        for connection_id in list(self.connections.keys()):
            await self.disconnect(connection_id)
            
    async def connect(self, websocket: WebSocket, user_id: Optional[str] = None, 
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """Accepte une nouvelle connexion WebSocket"""
        try:
            await websocket.accept()
            
            connection_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            connection_info = ConnectionInfo(
                connection_id=connection_id,
                user_id=user_id,
                websocket=websocket,
                state=ConnectionState.CONNECTED,
                connected_at=now,
                last_heartbeat=now,
                metadata=metadata or {}
            )
            
            self.connections[connection_id] = connection_info
            
            # Associer l'utilisateur à la connexion
            if user_id:
                if user_id not in self.user_connections:
                    self.user_connections[user_id] = set()
                self.user_connections[user_id].add(connection_id)
                
            # Envoyer message de bienvenue
            welcome_msg = WebSocketMessage(
                type=MessageType.STATUS,
                data={
                    "status": "connected",
                    "connection_id": connection_id,
                    "server_time": now.isoformat()
                }
            )
            await self._send_to_connection(connection_id, welcome_msg)
            
            logger.info(f"Nouvelle connexion WebSocket: {connection_id} (user: {user_id})")
            return connection_id
            
        except Exception as e:
            logger.error(f"Erreur lors de la connexion WebSocket: {e}")
            raise
            
    async def disconnect(self, connection_id: str):
        """Ferme une connexion WebSocket"""
        if connection_id not in self.connections:
            return
            
        connection_info = self.connections[connection_id]
        connection_info.state = ConnectionState.DISCONNECTING
        
        try:
            # Désabonner de tous les canaux
            for channel in list(connection_info.subscriptions):
                await self.unsubscribe(connection_id, channel)
                
            # Fermer la connexion
            await connection_info.websocket.close()
            
        except Exception as e:
            logger.warning(f"Erreur lors de la fermeture de connexion {connection_id}: {e}")
            
        finally:
            # Nettoyer les références
            if connection_info.user_id:
                user_connections = self.user_connections.get(connection_info.user_id, set())
                user_connections.discard(connection_id)
                if not user_connections:
                    del self.user_connections[connection_info.user_id]
                    
            connection_info.state = ConnectionState.DISCONNECTED
            del self.connections[connection_id]
            
            logger.info(f"Connexion WebSocket fermée: {connection_id}")
            
    async def subscribe(self, connection_id: str, channel: str) -> bool:
        """Abonne une connexion à un canal"""
        if connection_id not in self.connections:
            return False
            
        connection_info = self.connections[connection_id]
        connection_info.subscriptions.add(channel)
        
        if channel not in self.channel_subscribers:
            self.channel_subscribers[channel] = set()
        self.channel_subscribers[channel].add(connection_id)
        
        # Confirmer l'abonnement
        confirm_msg = WebSocketMessage(
            type=MessageType.STATUS,
            data={
                "action": "subscribed",
                "channel": channel,
                "subscriber_count": len(self.channel_subscribers[channel])
            }
        )
        await self._send_to_connection(connection_id, confirm_msg)
        
        logger.debug(f"Connexion {connection_id} abonnée au canal {channel}")
        return True
        
    async def unsubscribe(self, connection_id: str, channel: str) -> bool:
        """Désabonne une connexion d'un canal"""
        if connection_id not in self.connections:
            return False
            
        connection_info = self.connections[connection_id]
        connection_info.subscriptions.discard(channel)
        
        if channel in self.channel_subscribers:
            self.channel_subscribers[channel].discard(connection_id)
            if not self.channel_subscribers[channel]:
                del self.channel_subscribers[channel]
                
        logger.debug(f"Connexion {connection_id} désabonnée du canal {channel}")
        return True
        
    async def send_to_user(self, user_id: str, message: WebSocketMessage) -> int:
        """Envoie un message à toutes les connexions d'un utilisateur"""
        sent_count = 0
        user_connections = self.user_connections.get(user_id, set())
        
        for connection_id in list(user_connections):
            if await self._send_to_connection(connection_id, message):
                sent_count += 1
                
        return sent_count
        
    async def send_to_channel(self, channel: str, message: WebSocketMessage, 
                            exclude_connection: Optional[str] = None) -> int:
        """
Diffuse un message sur un canal"""
        sent_count = 0
        subscribers = self.channel_subscribers.get(channel, set())
        
        for connection_id in list(subscribers):
            if connection_id != exclude_connection:
                if await self._send_to_connection(connection_id, message):
                    sent_count += 1
                    
        return sent_count
        
    async def broadcast(self, message: WebSocketMessage, 
                       exclude_connection: Optional[str] = None) -> int:
        """
Diffuse un message à toutes les connexions"""
        sent_count = 0
        
        for connection_id in list(self.connections.keys()):
            if connection_id != exclude_connection:
                if await self._send_to_connection(connection_id, message):
                    sent_count += 1
                    
        return sent_count
        
    async def send_direct(self, connection_id: str, message: WebSocketMessage) -> bool:
        """
Envoie un message direct à une connexion spécifique"""
        return await self._send_to_connection(connection_id, message)
        
    async def _send_to_connection(self, connection_id: str, message: WebSocketMessage) -> bool:
        """
Envoie un message à une connexion spécifique"""
        if connection_id not in self.connections:
            logger.warning(f"Tentative d'envoi vers connexion inexistante: {connection_id}")
            return False
            
        connection_info = self.connections[connection_id]
        
        if connection_info.state != ConnectionState.CONNECTED:
            logger.warning(f"Tentative d'envoi vers connexion non active: {connection_id}")
            return False
            
        try:
            # Vérifier expiration du message
            if message.expires_at and datetime.utcnow() > message.expires_at:
                logger.debug(f"Message expiré, non envoyé: {message.message_id}")
                return False
                
            # Sérialiser et envoyer
            message_data = json.dumps(message.to_dict())
            await connection_info.websocket.send_text(message_data)
            
            logger.debug(f"Message envoyé à {connection_id}: {message.type.value}")
            return True
            
        except ConnectionClosed:
            logger.info(f"Connexion fermée détectée: {connection_id}")
            await self.disconnect(connection_id)
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de message à {connection_id}: {e}")
            return False
            
    async def handle_heartbeat(self, connection_id: str):
        """Traite un heartbeat d'une connexion"""
        if connection_id in self.connections:
            self.connections[connection_id].last_heartbeat = datetime.utcnow()
            
            # Répondre au heartbeat
            pong_msg = WebSocketMessage(
                type=MessageType.HEARTBEAT,
                data={"pong": True, "server_time": datetime.utcnow().isoformat()}
            )
            await self._send_to_connection(connection_id, pong_msg)
            
    async def _cleanup_loop(self):
        """Boucle de nettoyage des connexions inactives"""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                await self._cleanup_stale_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur dans la boucle de nettoyage: {e}")
                
    async def _cleanup_stale_connections(self):
        """Nettoie les connexions inactives"""
        now = datetime.utcnow()
        stale_threshold = now - timedelta(seconds=self.heartbeat_interval * 2)
        
        stale_connections = []
        for connection_id, connection_info in self.connections.items():
            if connection_info.last_heartbeat < stale_threshold:
                stale_connections.append(connection_id)
                
        for connection_id in stale_connections:
            logger.info(f"Nettoyage connexion inactive: {connection_id}")
            await self.disconnect(connection_id)
            
    def get_connection_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des connexions"""
        return {
            "total_connections": len(self.connections),
            "connected_users": len(self.user_connections),
            "active_channels": len(self.channel_subscribers),
            "connections_by_state": {
                state.value: sum(1 for conn in self.connections.values() 
                               if conn.state == state)
                for state in ConnectionState
            }
        }

class WebSocketManager:
    """Gestionnaire principal WebSocket avec haute disponibilité"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.connection_manager = ConnectionManager()
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        self.middleware: List[Callable] = []
        self.redis_client = None
        
        if redis_url:
            self.redis_client = redis.from_url(redis_url)
            self.connection_manager.redis_client = self.redis_client
            
    async def start(self):
        """
Démarre le gestionnaire WebSocket"""
        await self.connection_manager.start()
        logger.info("WebSocketManager démarré")
        
    async def stop(self):
        """Arrête le gestionnaire WebSocket"""
        await self.connection_manager.stop()
        if self.redis_client:
            await self.redis_client.close()
        logger.info("WebSocketManager arrêté")
        
    async def handle_connection(self, websocket: WebSocket, user_id: Optional[str] = None):
        """Gère une nouvelle connexion WebSocket"""
        connection_id = await self.connection_manager.connect(websocket, user_id)
        
        try:
            while True:
                # Recevoir les messages
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Créer l'objet message
                message = WebSocketMessage(
                    message_id=message_data.get("message_id", str(uuid.uuid4())),
                    type=MessageType(message_data.get("type", "direct")),
                    sender_id=connection_id,
                    recipient_id=message_data.get("recipient_id"),
                    channel=message_data.get("channel"),
                    data=message_data.get("data", {}),
                    priority=message_data.get("priority", 1)
                )
                
                # Traiter le message
                await self._process_message(connection_id, message)
                
        except WebSocketDisconnect:
            logger.info(f"Connexion WebSocket fermée côté client: {connection_id}")
        except Exception as e:
            logger.error(f"Erreur dans la gestion de connexion {connection_id}: {e}")
        finally:
            await self.connection_manager.disconnect(connection_id)
            
    async def _process_message(self, connection_id: str, message: WebSocketMessage):
        """Traite un message reçu"""
        try:
            # Appliquer le middleware
            for middleware in self.middleware:
                message = await middleware(connection_id, message)
                if message is None:
                    return  # Message bloqué par le middleware
                    
            # Traiter selon le type de message
            if message.type == MessageType.HEARTBEAT:
                await self.connection_manager.handle_heartbeat(connection_id)
                
            elif message.type == MessageType.SUBSCRIBE:
                channel = message.data.get("channel")
                if channel:
                    await self.connection_manager.subscribe(connection_id, channel)
                    
            elif message.type == MessageType.UNSUBSCRIBE:
                channel = message.data.get("channel")
                if channel:
                    await self.connection_manager.unsubscribe(connection_id, channel)
                    
            elif message.type == MessageType.BROADCAST:
                await self.connection_manager.broadcast(message, exclude_connection=connection_id)
                
            elif message.type == MessageType.DIRECT:
                if message.recipient_id:
                    await self.connection_manager.send_direct(message.recipient_id, message)
                elif message.channel:
                    await self.connection_manager.send_to_channel(
                        message.channel, message, exclude_connection=connection_id
                    )
                    
            # Exécuter les handlers personnalisés
            for handler in self.message_handlers.get(message.type, []):
                await handler(connection_id, message)
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement de message {message.message_id}: {e}")
            
            # Envoyer erreur au client
            error_msg = WebSocketMessage(
                type=MessageType.ERROR,
                data={
                    "error": "message_processing_failed",
                    "original_message_id": message.message_id,
                    "error_details": str(e)
                }
            )
            await self.connection_manager.send_direct(connection_id, error_msg)
            
    def add_message_handler(self, message_type: MessageType, handler: Callable):
        """Ajoute un gestionnaire pour un type de message"""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
        
    def add_middleware(self, middleware: Callable):
        """
Ajoute un middleware de traitement des messages"""
        self.middleware.append(middleware)
        
    async def notify_user(self, user_id: str, notification_type: str, data: Dict[str, Any]):
        """
Envoie une notification à un utilisateur"""
        message = WebSocketMessage(
            type=MessageType.NOTIFICATION,
            data={
                "notification_type": notification_type,
                "payload": data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        return await self.connection_manager.send_to_user(user_id, message)
        
    async def broadcast_notification(self, notification_type: str, data: Dict[str, Any]):
        """Diffuse une notification à tous les clients connectés"""
        message = WebSocketMessage(
            type=MessageType.NOTIFICATION,
            data={
                "notification_type": notification_type,
                "payload": data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        return await self.connection_manager.broadcast(message)
        
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du gestionnaire"""
        return {
            "websocket_manager": {
                "handlers_count": {
                    msg_type.value: len(handlers) 
                    for msg_type, handlers in self.message_handlers.items()
                },
                "middleware_count": len(self.middleware)
            },
            "connections": self.connection_manager.get_connection_stats()
        }