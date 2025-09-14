"""
Real-Time Collaboration - Collaboration Module
==============================================
Système de collaboration temps réel pour créateurs Ainflue.
Support WebSocket, synchronisation multi-utilisateurs.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class CollaborationEventType(Enum):
    """Types d'événements de collaboration."""
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    CONTENT_UPDATED = "content_updated"
    MESSAGE_SENT = "message_sent"
    PROJECT_STATUS_CHANGED = "project_status_changed"
    SYNC_REQUEST = "sync_request"

@dataclass
class CollaborationUser:
    """Utilisateur dans une session de collaboration."""
    user_id: str
    name: str
    role: str
    avatar: Optional[str] = None
    last_seen: Optional[datetime] = None
    is_active: bool = True

@dataclass
class CollaborationEvent:
    """Événement de collaboration."""
    event_id: str
    event_type: CollaborationEventType
    user_id: str
    project_id: str
    timestamp: datetime
    data: Dict[str, Any]

@dataclass
class CollaborationSession:
    """Session de collaboration active."""
    session_id: str
    project_id: str
    users: List[CollaborationUser]
    created_at: datetime
    last_activity: datetime
    status: str = "active"

class RealTimeCollaboration:
    """
    Gestionnaire de collaboration temps réel.
    WebSocket management et synchronisation état.
    """
    
    def __init__(self, config -> None: Optional[Dict] = None) -> None:
        """Initialise le système de collaboration."""
        self.config = config or {}
        self.active_sessions: Dict[str, CollaborationSession] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> session_ids
        self.event_handlers: Dict[CollaborationEventType, List] = {}
        self.websocket_connections: Dict[str, Any] = {}
        logger.info("Real-Time Collaboration initialisé")
    
    async def create_session(
        self,
        project_id: str,
        creator_user: CollaborationUser
    ) -> CollaborationSession:
        """Crée une nouvelle session de collaboration."""
        session_id = str(uuid.uuid4())
        
        session = CollaborationSession(
            session_id=session_id,
            project_id=project_id,
            users=[creator_user],
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        self.active_sessions[session_id] = session
        
        # Track user sessions
        if creator_user.user_id not in self.user_connections:
            self.user_connections[creator_user.user_id] = set()
        self.user_connections[creator_user.user_id].add(session_id)
        
        logger.info(f"Session créée: {session_id} pour projet {project_id}")
        return session
    
    async def join_session(
        self,
        session_id: str,
        user: CollaborationUser
    ) -> bool:
        """Ajoute un utilisateur à une session."""
        if session_id not in self.active_sessions:
            logger.error(f"Session {session_id} introuvable")
            return False
        
        session = self.active_sessions[session_id]
        
        # Vérifier si utilisateur déjà dans la session
        for existing_user in session.users:
            if existing_user.user_id == user.user_id:
                existing_user.is_active = True
                existing_user.last_seen = datetime.now()
                break
        else:
            session.users.append(user)
        
        # Track user connection
        if user.user_id not in self.user_connections:
            self.user_connections[user.user_id] = set()
        self.user_connections[user.user_id].add(session_id)
        
        session.last_activity = datetime.now()
        
        # Émettre événement user joined
        await self._emit_event(
            session_id,
            CollaborationEventType.USER_JOINED,
            user.user_id,
            {"user": asdict(user)}
        )
        
        logger.info(f"Utilisateur {user.user_id} rejoint session {session_id}")
        return True
    
    async def leave_session(
        self,
        session_id: str,
        user_id: str
    ) -> bool:
        """Retire un utilisateur d'une session."""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        
        # Marquer utilisateur comme inactif
        for user in session.users:
            if user.user_id == user_id:
                user.is_active = False
                user.last_seen = datetime.now()
                break
        
        # Retirer de tracking
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(session_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        session.last_activity = datetime.now()
        
        # Émettre événement user left
        await self._emit_event(
            session_id,
            CollaborationEventType.USER_LEFT,
            user_id,
            {"user_id": user_id}
        )
        
        logger.info(f"Utilisateur {user_id} quitte session {session_id}")
        return True
    
    async def update_content(
        self,
        session_id: str,
        user_id: str,
        content_data: Dict[str, Any]
    ) -> bool:
        """Met à jour le contenu collaboratif."""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        session.last_activity = datetime.now()
        
        # Émettre événement content updated
        await self._emit_event(
            session_id,
            CollaborationEventType.CONTENT_UPDATED,
            user_id,
            {
                "content": content_data,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        logger.info(f"Contenu mis à jour par {user_id} dans session {session_id}")
        return True
    
    async def send_message(
        self,
        session_id: str,
        user_id: str,
        message: str,
        message_type: str = "text"
    ) -> bool:
        """Envoie un message dans une session."""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        session.last_activity = datetime.now()
        
        message_data = {
            "message": message,
            "type": message_type,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        }
        
        # Émettre événement message
        await self._emit_event(
            session_id,
            CollaborationEventType.MESSAGE_SENT,
            user_id,
            message_data
        )
        
        logger.info(f"Message envoyé par {user_id} dans session {session_id}")
        return True
    
    async def sync_session_state(
        self,
        session_id: str,
        requesting_user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Synchronise l'état complet d'une session."""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        state = {
            "session": asdict(session),
            "active_users": [
                asdict(user) for user in session.users if user.is_active
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        # Émettre événement sync
        await self._emit_event(
            session_id,
            CollaborationEventType.SYNC_REQUEST,
            requesting_user_id,
            {"requesting_user": requesting_user_id}
        )
        
        return state
    
    async def _emit_event(
        self,
        session_id -> None: str,
        event_type -> None: CollaborationEventType,
        user_id -> None: str,
        data -> None: Dict[str, Any]
    ) -> None:
        """Émet un événement à tous les participants."""
        event = CollaborationEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            user_id=user_id,
            project_id=self.active_sessions[session_id].project_id,
            timestamp=datetime.now(),
            data=data
        )
        
        # Traiter avec handlers personnalisés
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Erreur handler événement: {e}")
        
        # Broadcast WebSocket (simulation)
        await self._broadcast_to_session(session_id, event)
    
    async def _broadcast_to_session(
        self,
        session_id -> None: str,
        event -> None: CollaborationEvent
    ) -> None:
        """Broadcast un événement à tous les utilisateurs de la session."""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        
        event_data = {
            "event_id": event.event_id,
            "type": event.event_type.value,
            "user_id": event.user_id,
            "project_id": event.project_id,
            "timestamp": event.timestamp.isoformat(),
            "data": event.data
        }
        
        # Envoyer à tous les utilisateurs actifs
        for user in session.users:
            if user.is_active:
                await self._send_to_user(user.user_id, event_data)
    
    async def _send_to_user(self, user_id -> None: str, data -> None: Dict[str, Any]) -> None:
        """Envoie des données à un utilisateur spécifique."""
        # Simulation WebSocket send
        if user_id in self.websocket_connections:
            try:
                # En production: await websocket.send(json.dumps(data))
                logger.debug(f"Envoi événement à {user_id}: {data['type']}")
            except Exception as e:
                logger.error(f"Erreur envoi WebSocket à {user_id}: {e}")
    
    def register_event_handler(
        self,
        event_type -> None: CollaborationEventType,
        handler
    ) -> None:
        """Enregistre un handler pour un type d'événement."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def get_session_analytics(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retourne analytics d'une session."""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        total_users = len(session.users)
        active_users = len([u for u in session.users if u.is_active])
        duration = datetime.now() - session.created_at
        
        return {
            "session_id": session_id,
            "project_id": session.project_id,
            "total_users": total_users,
            "active_users": active_users,
            "duration_minutes": duration.total_seconds() / 60,
            "last_activity": session.last_activity.isoformat(),
            "status": session.status
        }
    
    async def cleanup_inactive_sessions(self, inactive_threshold_minutes -> None: int = 30) -> None:
        """Nettoie les sessions inactives."""
        current_time = datetime.now()
        threshold = current_time.timestamp() - (inactive_threshold_minutes * 60)
        
        sessions_to_remove = []
        
        for session_id, session in self.active_sessions.items():
            if session.last_activity.timestamp() < threshold:
                # Vérifier s'il y a des utilisateurs actifs
                has_active_users = any(user.is_active for user in session.users)
                
                if not has_active_users:
                    sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            await self._cleanup_session(session_id)
            del self.active_sessions[session_id]
            logger.info(f"Session inactive supprimée: {session_id}")
    
    async def _cleanup_session(self, session_id -> None: str) -> None:
        """Nettoie les ressources d'une session."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            # Retirer de user_connections
            for user in session.users:
                if user.user_id in self.user_connections:
                    self.user_connections[user.user_id].discard(session_id)
                    if not self.user_connections[user.user_id]:
                        del self.user_connections[user.user_id]

# Factory function
def create_realtime_collaboration(config: Optional[Dict] = None) -> RealTimeCollaboration:
    """Crée une instance du système de collaboration temps réel."""
    return RealTimeCollaboration(config)