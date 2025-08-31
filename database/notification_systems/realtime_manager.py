"""Real-time Communication Manager

Gestionnaire avancé des communications temps réel via WebSocket, Socket.IO et Server-Sent Events.
Support multi-rooms, broadcast ciblé, présence utilisateur et messaging temps réel.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead AI Developer, Backend Senior, Real-time Systems Expert
Copyright © 2025 Fahed Mlaiel. Tous droits réservés.

AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et constitue une violation des droits d'auteur.
Les contrevenants s'exposent à des poursuites judiciaires.
"""from typing import Dict, List, Optional, Any, Set, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import json
import uuid
import weakref
from collections import defaultdict
import aioredis
import asyncpg
from fastapi import WebSocket, WebSocketDisconnect
import socketio
from broadcasters import Broadcaster

logger = logging.getLogger(__name__)


class ConnectionType(Enum):
    """Types de connexion temps réel"""    WEBSOCKET = "websocket"
    SOCKET_IO = "socketio"
    SSE = "sse"
    WEBHOOK = "webhook"


class MessageType(Enum):
    """Types de messages temps réel"""    CHAT = "chat"
    NOTIFICATION = "notification"
    COLLABORATION_UPDATE = "collaboration_update"
    CONTENT_STATUS = "content_status"
    REVENUE_UPDATE = "revenue_update"
    SYSTEM_ALERT = "system_alert"
    PRESENCE_UPDATE = "presence_update"
    TYPING_INDICATOR = "typing_indicator"
    FILE_UPLOAD = "file_upload"
    STREAM_DATA = "stream_data"


class MessagePriority(Enum):
    """Priorités des messages"""    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class UserStatus(Enum):
    """Statuts de présence utilisateur"""    ONLINE = "online"
    AWAY = "away"
    BUSY = "busy"
    OFFLINE = "offline"
    INVISIBLE = "invisible"


@dataclass
class Connection:
    """Connexion temps réel"""    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    session_id: str = ""
    connection_type: ConnectionType = ConnectionType.WEBSOCKET
    socket: Optional[Any] = None
    rooms: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class Room:
    """Salle de communication"""    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: str = "general"
    owner_id: str = ""
    members: Set[str] = field(default_factory=set)
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class RealtimeMessage:
    """Message temps réel"""    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.CHAT
    sender_id: str = ""
    target_type: str = "user"  # user, room, broadcast
    target_id: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    ttl: Optional[int] = None
    delivery_receipt: bool = False
    read_receipt: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


@dataclass
class UserPresence:
    """Présence utilisateur"""    user_id: str = ""
    status: UserStatus = UserStatus.OFFLINE
    status_message: Optional[str] = None
    location: Optional[str] = None
    device_info: Dict[str, Any] = field(default_factory=dict)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    connections: List[str] = field(default_factory=list)
    custom_data: Dict[str, Any] = field(default_factory=dict)


class WebSocketManager:
    """Gestionnaire WebSocket natif"""    
    def __init__(self):
        self.connections: Dict[str, Connection] = {}
        self.user_connections: Dict[str, Set[str]] = defaultdict(set)
        self.room_connections: Dict[str, Set[str]] = defaultdict(set)
        
    async def connect(self, websocket: WebSocket, user_id: str, session_id: str) -> str:
        """Connecter un WebSocket"""        try:
            await websocket.accept()
            
            connection = Connection(
                user_id=user_id,
                session_id=session_id,
                connection_type=ConnectionType.WEBSOCKET,
                socket=websocket
            )
            
            self.connections[connection.id] = connection
            self.user_connections[user_id].add(connection.id)
            
            logger.info(f"WebSocket connecté: {connection.id} pour utilisateur {user_id}")
            return connection.id
            
        except Exception as e:
            logger.error(f"Erreur connexion WebSocket: {e}")
            raise
    
    async def disconnect(self, connection_id: str):
        """Déconnecter un WebSocket"""        try:
            connection = self.connections.get(connection_id)
            if not connection:
                return
            
            # Supprimer des rooms
            for room_id in connection.rooms:
                self.room_connections[room_id].discard(connection_id)
            
            # Supprimer des mappings utilisateur
            self.user_connections[connection.user_id].discard(connection_id)
            
            # Supprimer la connexion
            del self.connections[connection_id]
            
            logger.info(f"WebSocket déconnecté: {connection_id}")
            
        except Exception as e:
            logger.error(f"Erreur déconnexion WebSocket: {e}")
    
    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """Envoyer un message à une connexion"""        try:
            connection = self.connections.get(connection_id)
            if not connection or not connection.socket:
                return False
            
            await connection.socket.send_text(json.dumps(message))
            connection.last_seen = datetime.utcnow()
            return True
            
        except WebSocketDisconnect:
            await self.disconnect(connection_id)
            return False
        except Exception as e:
            logger.error(f"Erreur envoi WebSocket {connection_id}: {e}")
            return False
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]) -> int:
        """Envoyer un message à toutes les connexions d'un utilisateur"""        sent_count = 0
        connection_ids = list(self.user_connections[user_id])
        
        for connection_id in connection_ids:
            if await self.send_to_connection(connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def send_to_room(self, room_id: str, message: Dict[str, Any], exclude_user: Optional[str] = None) -> int:
        """Envoyer un message à toutes les connexions d'une room"""        sent_count = 0
        connection_ids = list(self.room_connections[room_id])
        
        for connection_id in connection_ids:
            connection = self.connections.get(connection_id)
            if connection and (not exclude_user or connection.user_id != exclude_user):
                if await self.send_to_connection(connection_id, message):
                    sent_count += 1
        
        return sent_count
    
    async def join_room(self, connection_id: str, room_id: str):
        """Joindre une room"""        connection = self.connections.get(connection_id)
        if connection:
            connection.rooms.add(room_id)
            self.room_connections[room_id].add(connection_id)
    
    async def leave_room(self, connection_id: str, room_id: str):
        """Quitter une room"""        connection = self.connections.get(connection_id)
        if connection:
            connection.rooms.discard(room_id)
            self.room_connections[room_id].discard(connection_id)


class SocketIOManager:
    """Gestionnaire Socket.IO"""    
    def __init__(self, cors_allowed_origins: List[str] = None):
        self.sio = socketio.AsyncServer(
            cors_allowed_origins=cors_allowed_origins or ["*"],
            logger=True,
            engineio_logger=True
        )
        self.connections: Dict[str, Connection] = {}
        self.user_connections: Dict[str, Set[str]] = defaultdict(set)
        
        self._setup_events()
    
    def _setup_events(self):
        """Configurer les événements Socket.IO"""        
        @self.sio.event
        async def connect(sid, environ, auth):
            """Événement de connexion"""            try:
                user_id = auth.get("user_id") if auth else None
                session_id = auth.get("session_id") if auth else str(uuid.uuid4())
                
                if not user_id:
                    await self.sio.disconnect(sid)
                    return False
                
                connection = Connection(
                    id=sid,
                    user_id=user_id,
                    session_id=session_id,
                    connection_type=ConnectionType.SOCKET_IO,
                    socket=sid
                )
                
                self.connections[sid] = connection
                self.user_connections[user_id].add(sid)
                
                # Notifier la connexion
                await self.sio.emit("connected", {"status": "connected", "sid": sid}, to=sid)
                
                logger.info(f"Socket.IO connecté: {sid} pour utilisateur {user_id}")
                return True
                
            except Exception as e:
                logger.error(f"Erreur connexion Socket.IO: {e}")
                return False
        
        @self.sio.event
        async def disconnect(sid):
            """Événement de déconnexion"""            try:
                connection = self.connections.get(sid)
                if connection:
                    self.user_connections[connection.user_id].discard(sid)
                    del self.connections[sid]
                
                logger.info(f"Socket.IO déconnecté: {sid}")
                
            except Exception as e:
                logger.error(f"Erreur déconnexion Socket.IO: {e}")
        
        @self.sio.event
        async def join_room(sid, data):
            """Rejoindre une room"""            try:
                room_id = data.get("room_id")
                if room_id:
                    await self.sio.enter_room(sid, room_id)
                    connection = self.connections.get(sid)
                    if connection:
                        connection.rooms.add(room_id)
                    
                    await self.sio.emit("room_joined", {"room_id": room_id}, to=sid)
                
            except Exception as e:
                logger.error(f"Erreur join room Socket.IO: {e}")
        
        @self.sio.event
        async def leave_room(sid, data):
            """Quitter une room"""            try:
                room_id = data.get("room_id")
                if room_id:
                    await self.sio.leave_room(sid, room_id)
                    connection = self.connections.get(sid)
                    if connection:
                        connection.rooms.discard(room_id)
                    
                    await self.sio.emit("room_left", {"room_id": room_id}, to=sid)
                
            except Exception as e:
                logger.error(f"Erreur leave room Socket.IO: {e}")
        
        @self.sio.event
        async def send_message(sid, data):
            """Envoyer un message"""            try:
                connection = self.connections.get(sid)
                if not connection:
                    return
                
                message = RealtimeMessage(
                    type=MessageType(data.get("type", "chat")),
                    sender_id=connection.user_id,
                    target_type=data.get("target_type", "user"),
                    target_id=data.get("target_id"),
                    content=data.get("content", {}),
                    priority=MessagePriority(data.get("priority", "normal"))
                )
                
                # Router le message
                if message.target_type == "room":
                    await self.sio.emit("message", message.__dict__, room=message.target_id)
                elif message.target_type == "user":
                    user_sids = self.user_connections[message.target_id]
                    for user_sid in user_sids:
                        await self.sio.emit("message", message.__dict__, to=user_sid)
                
            except Exception as e:
                logger.error(f"Erreur envoi message Socket.IO: {e}")
    
    async def send_to_user(self, user_id: str, event: str, data: Dict[str, Any]) -> int:
        """Envoyer un événement à un utilisateur"""        sent_count = 0
        user_sids = list(self.user_connections[user_id])
        
        for sid in user_sids:
            try:
                await self.sio.emit(event, data, to=sid)
                sent_count += 1
            except Exception as e:
                logger.error(f"Erreur envoi Socket.IO {sid}: {e}")
        
        return sent_count
    
    async def send_to_room(self, room_id: str, event: str, data: Dict[str, Any]):
        """Envoyer un événement à une room"""        try:
            await self.sio.emit(event, data, room=room_id)
        except Exception as e:
            logger.error(f"Erreur envoi room Socket.IO {room_id}: {e}")


class PresenceManager:
    """Gestionnaire de présence utilisateur"""    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.presence_ttl = 300  # 5 minutes
        
    async def update_presence(self, user_id: str, status: UserStatus, 
                            status_message: Optional[str] = None,
                            location: Optional[str] = None,
                            device_info: Optional[Dict[str, Any]] = None):
        """Mettre à jour la présence d'un utilisateur"""        try:
            presence = UserPresence(
                user_id=user_id,
                status=status,
                status_message=status_message,
                location=location,
                device_info=device_info or {},
                last_activity=datetime.utcnow()
            )
            
            # Sauvegarder dans Redis
            key = f"presence:{user_id}"
            await self.redis.hset(key, mapping={
                "status": status.value,
                "status_message": status_message or "",
                "location": location or "",
                "device_info": json.dumps(device_info or {}),
                "last_activity": presence.last_activity.isoformat(),
                "custom_data": json.dumps({})
            })
            
            # Définir l'expiration
            await self.redis.expire(key, self.presence_ttl)
            
            return presence
            
        except Exception as e:
            logger.error(f"Erreur mise à jour présence {user_id}: {e}")
            raise
    
    async def get_presence(self, user_id: str) -> Optional[UserPresence]:
        """Récupérer la présence d'un utilisateur"""        try:
            key = f"presence:{user_id}"
            data = await self.redis.hgetall(key)
            
            if not data:
                return None
            
            return UserPresence(
                user_id=user_id,
                status=UserStatus(data.get("status", "offline")),
                status_message=data.get("status_message") or None,
                location=data.get("location") or None,
                device_info=json.loads(data.get("device_info", "{}")),
                last_activity=datetime.fromisoformat(data.get("last_activity")),
                custom_data=json.loads(data.get("custom_data", "{}"))
            )
            
        except Exception as e:
            logger.error(f"Erreur récupération présence {user_id}: {e}")
            return None
    
    async def get_online_users(self) -> List[str]:
        """Récupérer la liste des utilisateurs en ligne"""        try:
            pattern = "presence:*"
            keys = await self.redis.keys(pattern)
            
            online_users = []
            for key in keys:
                user_id = key.decode().split(":")[1]
                presence = await self.get_presence(user_id)
                
                if presence and presence.status != UserStatus.OFFLINE:
                    online_users.append(user_id)
            
            return online_users
            
        except Exception as e:
            logger.error(f"Erreur récupération utilisateurs en ligne: {e}")
            return []
    
    async def cleanup_expired_presence(self):
        """Nettoyer les présences expirées"""        try:
            pattern = "presence:*"
            keys = await self.redis.keys(pattern)
            
            expired_count = 0
            for key in keys:
                ttl = await self.redis.ttl(key)
                if ttl == -1:  # Pas d'expiration définie
                    await self.redis.expire(key, self.presence_ttl)
                elif ttl == -2:  # Clé expirée
                    await self.redis.delete(key)
                    expired_count += 1
            
            if expired_count > 0:
                logger.info(f"Nettoyé {expired_count} présences expirées")
                
        except Exception as e:
            logger.error(f"Erreur nettoyage présences: {e}")


class MessageBroker:
    """Courtier de messages pour distribution multi-instances"""    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.subscribers: Dict[str, Set[Callable]] = defaultdict(set)
        self.pubsub = None
        
    async def start(self):
        """Démarrer le courtier"""        try:
            self.pubsub = self.redis.pubsub()
            await self.pubsub.subscribe("realtime:messages")
            
            # Démarrer la boucle d'écoute
            asyncio.create_task(self._listen_loop())
            
        except Exception as e:
            logger.error(f"Erreur démarrage broker: {e}")
            raise
    
    async def stop(self):
        """Arrêter le courtier"""        try:
            if self.pubsub:
                await self.pubsub.unsubscribe("realtime:messages")
                await self.pubsub.close()
                
        except Exception as e:
            logger.error(f"Erreur arrêt broker: {e}")
    
    async def publish_message(self, message: RealtimeMessage):
        """Publier un message"""        try:
            message_data = {
                "id": message.id,
                "type": message.type.value,
                "sender_id": message.sender_id,
                "target_type": message.target_type,
                "target_id": message.target_id,
                "content": message.content,
                "priority": message.priority.value,
                "created_at": message.created_at.isoformat(),
                "metadata": message.metadata
            }
            
            await self.redis.publish("realtime:messages", json.dumps(message_data))
            
        except Exception as e:
            logger.error(f"Erreur publication message: {e}")
    
    def subscribe_to_messages(self, callback: Callable[[RealtimeMessage], None]):
        """S'abonner aux messages"""        self.subscribers["messages"].add(callback)
    
    def unsubscribe_from_messages(self, callback: Callable[[RealtimeMessage], None]):
        """Se désabonner des messages"""        self.subscribers["messages"].discard(callback)
    
    async def _listen_loop(self):
        """Boucle d'écoute des messages"""        try:
            while True:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                if message and message["type"] == "message":
                    await self._handle_message(message["data"])
                    
        except Exception as e:
            logger.error(f"Erreur boucle écoute broker: {e}")
    
    async def _handle_message(self, data: bytes):
        """Traiter un message reçu"""        try:
            message_data = json.loads(data.decode())
            message = RealtimeMessage(
                id=message_data["id"],
                type=MessageType(message_data["type"]),
                sender_id=message_data["sender_id"],
                target_type=message_data["target_type"],
                target_id=message_data["target_id"],
                content=message_data["content"],
                priority=MessagePriority(message_data["priority"]),
                created_at=datetime.fromisoformat(message_data["created_at"]),
                metadata=message_data["metadata"]
            )
            
            # Notifier les abonnés
            for callback in self.subscribers["messages"]:
                try:
                    await callback(message)
                except Exception as e:
                    logger.error(f"Erreur callback message: {e}")
                    
        except Exception as e:
            logger.error(f"Erreur traitement message broker: {e}")


class RealtimeCommunicationManager:
    """Gestionnaire principal des communications temps réel"""    
    def __init__(self, db_pool: asyncpg.Pool, redis_client: aioredis.Redis, config: Dict[str, Any]):
        self.db_pool = db_pool
        self.redis = redis_client
        self.config = config
        
        # Gestionnaires de connexion
        self.websocket_manager = WebSocketManager()
        self.socketio_manager = SocketIOManager(config.get("cors_origins", ["*"]))
        
        # Services
        self.presence_manager = PresenceManager(redis_client)
        self.message_broker = MessageBroker(redis_client)
        
        # Rooms et permissions
        self.rooms: Dict[str, Room] = {}
        
        # S'abonner aux messages distribués
        self.message_broker.subscribe_to_messages(self._handle_distributed_message)
    
    async def start(self):
        """Démarrer le gestionnaire"""        try:
            await self.message_broker.start()
            logger.info("Gestionnaire communications temps réel démarré")
        except Exception as e:
            logger.error(f"Erreur démarrage communications temps réel: {e}")
            raise
    
    async def stop(self):
        """Arrêter le gestionnaire"""        try:
            await self.message_broker.stop()
            logger.info("Gestionnaire communications temps réel arrêté")
        except Exception as e:
            logger.error(f"Erreur arrêt communications temps réel: {e}")
    
    async def connect_websocket(self, websocket: WebSocket, user_id: str, session_id: str) -> str:
        """Connecter un WebSocket"""        connection_id = await self.websocket_manager.connect(websocket, user_id, session_id)
        await self.presence_manager.update_presence(user_id, UserStatus.ONLINE)
        return connection_id
    
    async def disconnect_websocket(self, connection_id: str):
        """Déconnecter un WebSocket"""        connection = self.websocket_manager.connections.get(connection_id)
        if connection:
            await self.websocket_manager.disconnect(connection_id)
            
            # Vérifier s'il reste des connexions pour cet utilisateur
            if not self.websocket_manager.user_connections[connection.user_id]:
                await self.presence_manager.update_presence(connection.user_id, UserStatus.OFFLINE)
    
    async def send_message(self, message: RealtimeMessage) -> bool:
        """Envoyer un message temps réel"""        try:
            # Sauvegarder le message en base si nécessaire
            if message.delivery_receipt or message.read_receipt:
                await self._save_message(message)
            
            # Publier via le broker pour distribution
            await self.message_broker.publish_message(message)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi message: {e}")
            return False
    
    async def _handle_distributed_message(self, message: RealtimeMessage):
        """Traiter un message distribué"""        try:
            if message.target_type == "user":
                # Envoyer à un utilisateur spécifique
                await self._send_to_user(message.target_id, message)
                
            elif message.target_type == "room":
                # Envoyer à une room
                await self._send_to_room(message.target_id, message)
                
            elif message.target_type == "broadcast":
                # Diffusion générale
                await self._broadcast_message(message)
                
        except Exception as e:
            logger.error(f"Erreur traitement message distribué: {e}")
    
    async def _send_to_user(self, user_id: str, message: RealtimeMessage):
        """Envoyer un message à un utilisateur"""        message_data = self._serialize_message(message)
        
        # WebSocket
        await self.websocket_manager.send_to_user(user_id, message_data)
        
        # Socket.IO
        await self.socketio_manager.send_to_user(user_id, "message", message_data)
    
    async def _send_to_room(self, room_id: str, message: RealtimeMessage):
        """Envoyer un message à une room"""        message_data = self._serialize_message(message)
        
        # WebSocket
        await self.websocket_manager.send_to_room(room_id, message_data, exclude_user=message.sender_id)
        
        # Socket.IO
        await self.socketio_manager.send_to_room(room_id, "message", message_data)
    
    async def _broadcast_message(self, message: RealtimeMessage):
        """Diffuser un message à tous les utilisateurs connectés"""        message_data = self._serialize_message(message)
        
        # Diffuser sur toutes les connexions WebSocket
        for connection in self.websocket_manager.connections.values():
            if connection.user_id != message.sender_id:
                await self.websocket_manager.send_to_connection(connection.id, message_data)
        
        # Diffuser sur Socket.IO
        await self.socketio_manager.sio.emit("message", message_data)
    
    def _serialize_message(self, message: RealtimeMessage) -> Dict[str, Any]:
        """Sérialiser un message pour l'envoi"""        return {
            "id": message.id,
            "type": message.type.value,
            "sender_id": message.sender_id,
            "content": message.content,
            "priority": message.priority.value,
            "created_at": message.created_at.isoformat(),
            "metadata": message.metadata
        }
    
    async def create_room(self, room: Room) -> str:
        """Créer une room"""        try:
            # Sauvegarder en base
            room_id = await self._save_room(room)
            
            # Ajouter au cache local
            self.rooms[room_id] = room
            
            return room_id
            
        except Exception as e:
            logger.error(f"Erreur création room: {e}")
            raise
    
    async def join_room(self, user_id: str, room_id: str) -> bool:
        """Rejoindre une room"""        try:
            # Vérifier les permissions
            room = await self._get_room(room_id)
            if not room or not self._check_room_permission(user_id, room, "join"):
                return False
            
            # Ajouter l'utilisateur aux membres
            room.members.add(user_id)
            await self._update_room(room)
            
            # Joindre toutes les connexions de l'utilisateur
            for connection_id in self.websocket_manager.user_connections[user_id]:
                await self.websocket_manager.join_room(connection_id, room_id)
            
            # Notifier les autres membres
            message = RealtimeMessage(
                type=MessageType.SYSTEM_ALERT,
                sender_id="system",
                target_type="room",
                target_id=room_id,
                content={"action": "user_joined", "user_id": user_id}
            )
            await self.send_message(message)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur join room {room_id}: {e}")
            return False
    
    async def leave_room(self, user_id: str, room_id: str) -> bool:
        """Quitter une room"""        try:
            room = await self._get_room(room_id)
            if not room:
                return False
            
            # Supprimer l'utilisateur des membres
            room.members.discard(user_id)
            await self._update_room(room)
            
            # Quitter toutes les connexions de l'utilisateur
            for connection_id in self.websocket_manager.user_connections[user_id]:
                await self.websocket_manager.leave_room(connection_id, room_id)
            
            # Notifier les autres membres
            message = RealtimeMessage(
                type=MessageType.SYSTEM_ALERT,
                sender_id="system",
                target_type="room",
                target_id=room_id,
                content={"action": "user_left", "user_id": user_id}
            )
            await self.send_message(message)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur leave room {room_id}: {e}")
            return False
    
    def _check_room_permission(self, user_id: str, room: Room, action: str) -> bool:
        """Vérifier les permissions sur une room"""        # Le propriétaire a tous les droits
        if room.owner_id == user_id:
            return True
        
        # Vérifier les permissions spécifiques
        user_permissions = room.permissions.get(user_id, [])
        return action in user_permissions or "all" in user_permissions
    
    async def _save_message(self, message: RealtimeMessage):
        """Sauvegarder un message en base"""        async with self.db_pool.acquire() as conn:
            query = """                INSERT INTO realtime_messages (
                    id, type, sender_id, target_type, target_id,
                    content, priority, ttl, delivery_receipt,
                    read_receipt, metadata, created_at, expires_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            """            
            await conn.execute(
                query,
                message.id, message.type.value, message.sender_id,
                message.target_type, message.target_id, json.dumps(message.content),
                message.priority.value, message.ttl, message.delivery_receipt,
                message.read_receipt, json.dumps(message.metadata),
                message.created_at, message.expires_at
            )
    
    async def _save_room(self, room: Room) -> str:
        """Sauvegarder une room en base"""        async with self.db_pool.acquire() as conn:
            query = """                INSERT INTO communication_rooms (
                    id, name, type, owner_id, members, permissions,
                    settings, created_at, is_active
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id
            """            
            result = await conn.fetchval(
                query,
                room.id, room.name, room.type, room.owner_id,
                json.dumps(list(room.members)), json.dumps(room.permissions),
                json.dumps(room.settings), room.created_at, room.is_active
            )
            
            return result
    
    async def _update_room(self, room: Room):
        """Mettre à jour une room en base"""        async with self.db_pool.acquire() as conn:
            query = """                UPDATE communication_rooms SET
                    name = $2, members = $3, permissions = $4,
                    settings = $5, is_active = $6
                WHERE id = $1
            """            
            await conn.execute(
                query,
                room.id, room.name, json.dumps(list(room.members)),
                json.dumps(room.permissions), json.dumps(room.settings),
                room.is_active
            )
    
    async def _get_room(self, room_id: str) -> Optional[Room]:
        """Récupérer une room"""        # Vérifier le cache local d'abord
        if room_id in self.rooms:
            return self.rooms[room_id]
        
        # Charger depuis la base
        async with self.db_pool.acquire() as conn:
            query = "SELECT * FROM communication_rooms WHERE id = $1 AND is_active = true"
            row = await conn.fetchrow(query, room_id)
            
            if not row:
                return None
            
            room = Room(
                id=row["id"],
                name=row["name"],
                type=row["type"],
                owner_id=row["owner_id"],
                members=set(json.loads(row["members"])),
                permissions=json.loads(row["permissions"]),
                settings=json.loads(row["settings"]),
                created_at=row["created_at"],
                is_active=row["is_active"]
            )
            
            # Mettre en cache
            self.rooms[room_id] = room
            return room
    
    async def get_user_presence(self, user_id: str) -> Optional[UserPresence]:
        """Récupérer la présence d'un utilisateur"""        return await self.presence_manager.get_presence(user_id)
    
    async def get_online_users(self) -> List[str]:
        """Récupérer les utilisateurs en ligne"""        return await self.presence_manager.get_online_users()
    
    async def get_room_members(self, room_id: str) -> List[str]:
        """Récupérer les membres d'une room"""        room = await self._get_room(room_id)
        return list(room.members) if room else []
    
    async def cleanup_expired_data(self):
        """Nettoyer les données expirées"""        try:
            # Nettoyer les présences expirées
            await self.presence_manager.cleanup_expired_presence()
            
            # Nettoyer les messages expirés
            async with self.db_pool.acquire() as conn:
                query = "DELETE FROM realtime_messages WHERE expires_at < $1"
                result = await conn.execute(query, datetime.utcnow())
                
                if result != "DELETE 0":
                    logger.info(f"Nettoyé les messages expirés: {result}")
                    
        except Exception as e:
            logger.error(f"Erreur nettoyage données expirées: {e}")
