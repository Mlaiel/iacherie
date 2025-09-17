"""🚀 Live Chat System - Real-time IA/Human Hybrid Enterprise
==============================================================
Module: backend/platform_core/support/live_chat_system.py
Author: Fahed Mlaiel (mlaiel@live.de)
==============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🏗️ SYSTÈME CHAT TEMPS RÉEL IA/HUMAIN ENTERPRISE
Chat hybride intelligent avec transition seamless
- WebSocket communication ultra-rapide et sécurisée
- Transition fluide IA → Agent humain spécialisé
- File d'attente intelligente avec priorité dynamique
- Support multilingue avec traduction temps réel
- Analytics conversation et satisfaction temps réel
"""

import asyncio
import logging
import json
import uuid
import time
from typing import Dict, List, Optional, Any, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import websockets
import redis.asyncio as redis
from fastapi import WebSocket, WebSocketDisconnect
import openai

logger = logging.getLogger(__name__)


class ChatSessionStatus(Enum):
    """Statuts session chat"""
    WAITING = "waiting"
    AI_ACTIVE = "ai_active"
    HUMAN_ACTIVE = "human_active"
    TRANSFERRING = "transferring"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class MessageType(Enum):
    """Types messages chat"""
    USER_MESSAGE = "user_message"
    AI_RESPONSE = "ai_response"
    AGENT_MESSAGE = "agent_message"
    SYSTEM_NOTIFICATION = "system_notification"
    TYPING_INDICATOR = "typing_indicator"
    TRANSFER_NOTICE = "transfer_notice"
    SESSION_END = "session_end"


class ChatPriority(Enum):
    """Priorités file d'attente"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    VIP = 5


@dataclass
class ChatMessage:
    """Message chat avec métadonnées"""
    message_id: str
    session_id: str
    sender_type: str  # user, ai, agent, system
    sender_id: str
    content: str
    message_type: MessageType
    timestamp: datetime
    language: str = "en"
    attachments: List[str] = field(default_factory=list)
    sentiment_score: Optional[float] = None
    confidence_score: Optional[float] = None
    translated_content: Dict[str, str] = field(default_factory=dict)


@dataclass
class ChatSession:
    """Session chat complète"""
    session_id: str
    creator_id: str
    creator_type: str
    creator_tier: str
    language: str
    status: ChatSessionStatus
    started_at: datetime
    ai_agent_id: Optional[str] = None
    human_agent_id: Optional[str] = None
    queue_position: int = 0
    priority: ChatPriority = ChatPriority.NORMAL
    messages: List[ChatMessage] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    satisfaction_score: Optional[float] = None
    ended_at: Optional[datetime] = None
    wait_time: Optional[timedelta] = None
    resolution_time: Optional[timedelta] = None


@dataclass
class AgentConnection:
    """Connexion agent support"""
    agent_id: str
    websocket: WebSocket
    agent_name: str
    specialty: str
    languages: List[str]
    is_active: bool = True
    current_sessions: Set[str] = field(default_factory=set)
    max_concurrent_sessions: int = 5
    last_activity: datetime = field(default_factory=datetime.utcnow)


class LiveChatSystem:
    """💬 Système Chat Temps Réel Enterprise
    
    Plateforme chat hybride IA/humain avec:
    - Communication WebSocket ultra-rapide
    - Routing intelligent et transition seamless
    - Support multilingue avec traduction automatique
    - File d'attente priorisée et analytics temps réel
    - Intégration complète écosystème support
    """
    
    def __init__(self, redis_url: str, openai_api_key: str):
        self.redis_url = redis_url
        self.openai_api_key = openai_api_key
        self.redis_client = None
        
        # Gestion connexions WebSocket
        self.user_connections: Dict[str, WebSocket] = {}
        self.agent_connections: Dict[str, AgentConnection] = {}
        
        # Sessions et files d'attente
        self.active_sessions: Dict[str, ChatSession] = {}
        self.queue_manager = ChatQueueManager()
        self.translation_service = TranslationService(openai_api_key)
        
        # Analytics temps réel
        self.chat_analytics = ChatAnalytics()
        self.performance_metrics = {
            "active_sessions": 0,
            "queued_users": 0,
            "avg_wait_time": timedelta(),
            "avg_response_time": timedelta(),
            "satisfaction_score": 0.0
        }
        
    async def initialize_chat_system(self) -> None:
        """🚀 Initialisation système chat avec Redis"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Nettoyage sessions expirées
            await self._cleanup_expired_sessions()
            
            logger.info("Système chat initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur initialisation chat: {e}")

    async def handle_user_connection(self, websocket: WebSocket, creator_id: str) -> None:
        """👤 Gestion connexion utilisateur WebSocket
        
        Args:
            websocket: Connexion WebSocket utilisateur
            creator_id: ID créateur se connectant
        """
        try:
            await websocket.accept()
            self.user_connections[creator_id] = websocket
            
            # Récupération ou création session
            session = await self._get_or_create_session(creator_id, websocket)
            
            # Message bienvenue
            await self._send_welcome_message(session)
            
            # Boucle écoute messages
            while True:
                try:
                    data = await websocket.receive_text()
                    message_data = json.loads(data)
                    
                    await self._process_user_message(session, message_data)
                    
                except WebSocketDisconnect:
                    logger.info(f"Utilisateur {creator_id} déconnecté")
                    break
                except json.JSONDecodeError:
                    await self._send_error_message(websocket, "Invalid message format")
                except Exception as e:
                    logger.error(f"Erreur traitement message: {e}")
                    await self._send_error_message(websocket, "Message processing error")
                    
        except Exception as e:
            logger.error(f"Erreur connexion utilisateur: {e}")
        finally:
            await self._cleanup_user_connection(creator_id)

    async def handle_agent_connection(
        self, 
        websocket: WebSocket, 
        agent_id: str,
        agent_profile: Dict[str, Any]
    ) -> None:
        """👨‍💼 Gestion connexion agent support WebSocket
        
        Args:
            websocket: Connexion WebSocket agent
            agent_id: ID agent support
            agent_profile: Profil agent avec spécialités
        """
        try:
            await websocket.accept()
            
            # Enregistrement connexion agent
            agent_connection = AgentConnection(
                agent_id=agent_id,
                websocket=websocket,
                agent_name=agent_profile.get("name", "Agent"),
                specialty=agent_profile.get("specialty", "general"),
                languages=agent_profile.get("languages", ["en"])
            )
            
            self.agent_connections[agent_id] = agent_connection
            
            # Notification statut online
            await self._notify_agent_online(agent_connection)
            
            # Boucle traitement messages agent
            while True:
                try:
                    data = await websocket.receive_text()
                    message_data = json.loads(data)
                    
                    await self._process_agent_message(agent_connection, message_data)
                    
                except WebSocketDisconnect:
                    logger.info(f"Agent {agent_id} déconnecté")
                    break
                except Exception as e:
                    logger.error(f"Erreur message agent: {e}")
                    
        except Exception as e:
            logger.error(f"Erreur connexion agent: {e}")
        finally:
            await self._cleanup_agent_connection(agent_id)

    async def _process_user_message(
        self, 
        session: ChatSession, 
        message_data: Dict[str, Any]
    ) -> None:
        """📝 Traitement message utilisateur avec routage intelligent"""
        try:
            # Création objet message
            message = ChatMessage(
                message_id=str(uuid.uuid4()),
                session_id=session.session_id,
                sender_type="user",
                sender_id=session.creator_id,
                content=message_data.get("content", ""),
                message_type=MessageType.USER_MESSAGE,
                timestamp=datetime.utcnow(),
                language=message_data.get("language", session.language)
            )
            
            # Analyse sentiment en temps réel
            message.sentiment_score = await self._analyze_message_sentiment(message.content)
            
            # Ajout à session
            session.messages.append(message)
            
            # Sauvegarde Redis
            await self._save_session_to_redis(session)
            
            # Routage selon statut session
            if session.status == ChatSessionStatus.AI_ACTIVE:
                await self._handle_ai_conversation(session, message)
            elif session.status == ChatSessionStatus.HUMAN_ACTIVE:
                await self._forward_to_human_agent(session, message)
            elif session.status == ChatSessionStatus.WAITING:
                await self._queue_for_human_agent(session, message)
                
            # Analytics temps réel
            await self.chat_analytics.record_message(message, session)
            
        except Exception as e:
            logger.error(f"Erreur traitement message utilisateur: {e}")

    async def _handle_ai_conversation(self, session: ChatSession, message: ChatMessage) -> None:
        """🤖 Gestion conversation IA avec détection besoin escalation"""
        try:
            from .ai_support_agent import AISupportAgent, ConversationContext
            
            # Construction contexte pour agent IA
            context = ConversationContext(
                creator_id=session.creator_id,
                creator_type=session.creator_type,
                conversation_id=session.session_id,
                language=message.language,
                session_start=session.started_at,
                message_count=len(session.messages),
                sentiment_score=message.sentiment_score or 0.0
            )
            
            # Traitement par agent IA
            ai_agent = await self._get_ai_agent()
            ai_response = await ai_agent.process_user_message(message.content, context)
            
            # Création message réponse IA
            ai_message = ChatMessage(
                message_id=str(uuid.uuid4()),
                session_id=session.session_id,
                sender_type="ai",
                sender_id=session.ai_agent_id or "ai_agent",
                content=ai_response.message,
                message_type=MessageType.AI_RESPONSE,
                timestamp=datetime.utcnow(),
                language=message.language,
                confidence_score=ai_response.confidence_score
            )
            
            session.messages.append(ai_message)
            
            # Envoi réponse IA à l'utilisateur
            await self._send_message_to_user(session.creator_id, ai_message)
            
            # Vérification besoin escalation
            if ai_response.escalation_needed:
                await self._initiate_human_transfer(session, ai_response.escalation_reason)
                
        except Exception as e:
            logger.error(f"Erreur conversation IA: {e}")
            await self._send_fallback_response(session)

    async def _forward_to_human_agent(self, session: ChatSession, message: ChatMessage) -> None:
        """👨‍💼 Transmission message à agent humain"""
        try:
            if not session.human_agent_id:
                await self._queue_for_human_agent(session, message)
                return
                
            agent_connection = self.agent_connections.get(session.human_agent_id)
            if not agent_connection or not agent_connection.is_active:
                await self._reassign_human_agent(session)
                return
                
            # Traduction si nécessaire
            translated_message = await self._translate_message_if_needed(
                message, agent_connection.languages
            )
            
            # Envoi à l'agent
            agent_message_data = {
                "type": "user_message",
                "session_id": session.session_id,
                "message": translated_message.model_dump() if hasattr(translated_message, 'model_dump') else translated_message.__dict__,
                "creator_profile": {
                    "creator_id": session.creator_id,
                    "creator_type": session.creator_type,
                    "creator_tier": session.creator_tier
                }
            }
            
            await agent_connection.websocket.send_text(json.dumps(agent_message_data))
            agent_connection.last_activity = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Erreur transmission agent: {e}")

    async def _process_agent_message(
        self, 
        agent_connection: AgentConnection, 
        message_data: Dict[str, Any]
    ) -> None:
        """🎯 Traitement message agent support"""
        try:
            message_type = message_data.get("type")
            session_id = message_data.get("session_id")
            
            if message_type == "agent_response":
                await self._handle_agent_response(agent_connection, session_id, message_data)
            elif message_type == "session_transfer":
                await self._handle_session_transfer(agent_connection, message_data)
            elif message_type == "session_close":
                await self._handle_session_close(agent_connection, session_id, message_data)
            elif message_type == "typing_indicator":
                await self._forward_typing_indicator(session_id, agent_connection.agent_id)
            elif message_type == "status_update":
                await self._update_agent_status(agent_connection, message_data)
                
        except Exception as e:
            logger.error(f"Erreur traitement message agent: {e}")

    async def _handle_agent_response(
        self,
        agent_connection: AgentConnection,
        session_id: str,
        message_data: Dict[str, Any]
    ) -> None:
        """💬 Gestion réponse agent vers utilisateur"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return
                
            # Création message agent
            agent_message = ChatMessage(
                message_id=str(uuid.uuid4()),
                session_id=session_id,
                sender_type="agent",
                sender_id=agent_connection.agent_id,
                content=message_data.get("content", ""),
                message_type=MessageType.AGENT_MESSAGE,
                timestamp=datetime.utcnow(),
                language=message_data.get("language", session.language)
            )
            
            session.messages.append(agent_message)
            
            # Traduction pour utilisateur si nécessaire
            translated_message = await self._translate_message_if_needed(
                agent_message, [session.language]
            )
            
            # Envoi à l'utilisateur
            await self._send_message_to_user(session.creator_id, translated_message)
            
            # Sauvegarde session
            await self._save_session_to_redis(session)
            
        except Exception as e:
            logger.error(f"Erreur réponse agent: {e}")

    async def _initiate_human_transfer(self, session: ChatSession, reason: str) -> None:
        """🔄 Initiation transfert vers agent humain"""
        try:
            session.status = ChatSessionStatus.TRANSFERRING
            
            # Message notification transfert
            transfer_message = ChatMessage(
                message_id=str(uuid.uuid4()),
                session_id=session.session_id,
                sender_type="system",
                sender_id="system",
                content=f"Je vous mets en relation avec un agent spécialisé. Raison: {reason}",
                message_type=MessageType.TRANSFER_NOTICE,
                timestamp=datetime.utcnow(),
                language=session.language
            )
            
            session.messages.append(transfer_message)
            await self._send_message_to_user(session.creator_id, transfer_message)
            
            # Ajout à la file d'attente prioritaire
            await self.queue_manager.add_to_queue(session, priority_boost=True)
            
            # Recherche agent disponible
            await self._find_and_assign_agent(session)
            
        except Exception as e:
            logger.error(f"Erreur transfert humain: {e}")

    async def _find_and_assign_agent(self, session: ChatSession) -> bool:
        """🎯 Recherche et assignation agent optimal"""
        try:
            # Critères recherche agent
            required_languages = [session.language]
            creator_type = session.creator_type
            
            best_agent = None
            best_score = 0
            
            for agent_id, agent_conn in self.agent_connections.items():
                if not agent_conn.is_active:
                    continue
                    
                if len(agent_conn.current_sessions) >= agent_conn.max_concurrent_sessions:
                    continue
                    
                # Scoring agent
                score = 0
                
                # Bonus langue
                if session.language in agent_conn.languages:
                    score += 50
                    
                # Bonus spécialité
                if agent_conn.specialty == "general" or creator_type in agent_conn.specialty:
                    score += 30
                    
                # Bonus disponibilité
                score += (agent_conn.max_concurrent_sessions - len(agent_conn.current_sessions)) * 10
                
                # Bonus activité récente
                time_since_activity = datetime.utcnow() - agent_conn.last_activity
                if time_since_activity < timedelta(minutes=5):
                    score += 20
                    
                if score > best_score:
                    best_score = score
                    best_agent = agent_conn
                    
            # Assignation si agent trouvé
            if best_agent:
                await self._assign_agent_to_session(session, best_agent)
                return True
            else:
                # Ajout file d'attente si aucun agent
                session.status = ChatSessionStatus.WAITING
                await self.queue_manager.add_to_queue(session)
                return False
                
        except Exception as e:
            logger.error(f"Erreur recherche agent: {e}")
            return False

    async def _assign_agent_to_session(
        self, 
        session: ChatSession, 
        agent_connection: AgentConnection
    ) -> None:
        """🔗 Assignation agent à session"""
        try:
            session.human_agent_id = agent_connection.agent_id
            session.status = ChatSessionStatus.HUMAN_ACTIVE
            agent_connection.current_sessions.add(session.session_id)
            
            # Calcul temps d'attente
            if session.status == ChatSessionStatus.WAITING:
                session.wait_time = datetime.utcnow() - session.started_at
                
            # Notification agent - nouvelle session
            session_data = {
                "type": "new_session_assigned",
                "session": session.__dict__,
                "creator_profile": {
                    "creator_id": session.creator_id,
                    "creator_type": session.creator_type,
                    "creator_tier": session.creator_tier,
                    "language": session.language
                },
                "recent_messages": [
                    msg.__dict__ for msg in session.messages[-5:]  # 5 derniers messages
                ]
            }
            
            await agent_connection.websocket.send_text(json.dumps(session_data))
            
            # Notification utilisateur - agent connecté
            agent_connected_msg = ChatMessage(
                message_id=str(uuid.uuid4()),
                session_id=session.session_id,
                sender_type="system",
                sender_id="system",
                content=f"Vous êtes maintenant en contact avec {agent_connection.agent_name}",
                message_type=MessageType.SYSTEM_NOTIFICATION,
                timestamp=datetime.utcnow(),
                language=session.language
            )
            
            session.messages.append(agent_connected_msg)
            await self._send_message_to_user(session.creator_id, agent_connected_msg)
            
            logger.info(f"Agent {agent_connection.agent_id} assigné à session {session.session_id}")
            
        except Exception as e:
            logger.error(f"Erreur assignation agent: {e}")

    async def _send_message_to_user(self, creator_id: str, message: ChatMessage) -> None:
        """📤 Envoi message à utilisateur via WebSocket"""
        try:
            websocket = self.user_connections.get(creator_id)
            if websocket:
                message_data = {
                    "type": "message",
                    "message": message.__dict__,
                    "timestamp": message.timestamp.isoformat()
                }
                await websocket.send_text(json.dumps(message_data))
                
        except Exception as e:
            logger.error(f"Erreur envoi message utilisateur: {e}")

    async def get_chat_analytics(self) -> Dict[str, Any]:
        """📊 Analytics chat temps réel"""
        try:
            # Métriques en temps réel
            active_sessions_count = len([s for s in self.active_sessions.values() 
                                       if s.status in [ChatSessionStatus.AI_ACTIVE, ChatSessionStatus.HUMAN_ACTIVE]])
            
            queued_users_count = len([s for s in self.active_sessions.values() 
                                    if s.status == ChatSessionStatus.WAITING])
            
            active_agents_count = len([a for a in self.agent_connections.values() if a.is_active])
            
            # Temps moyens
            completed_sessions = [s for s in self.active_sessions.values() 
                                if s.status == ChatSessionStatus.COMPLETED and s.wait_time]
            
            avg_wait_time = (
                sum([s.wait_time.total_seconds() for s in completed_sessions], 0) / 
                max(1, len(completed_sessions))
            )
            
            avg_resolution_time = (
                sum([s.resolution_time.total_seconds() for s in completed_sessions if s.resolution_time], 0) /
                max(1, len([s for s in completed_sessions if s.resolution_time]))
            )
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "active_sessions": active_sessions_count,
                "queued_users": queued_users_count,
                "active_agents": active_agents_count,
                "avg_wait_time_seconds": avg_wait_time,
                "avg_resolution_time_seconds": avg_resolution_time,
                "total_messages_today": await self.chat_analytics.get_daily_message_count(),
                "satisfaction_score": await self.chat_analytics.get_avg_satisfaction_score(),
                "chat_volume_trend": await self.chat_analytics.get_volume_trend(),
                "agent_utilization": await self._calculate_agent_utilization()
            }
            
        except Exception as e:
            logger.error(f"Erreur analytics chat: {e}")
            return {}

    async def _calculate_agent_utilization(self) -> Dict[str, float]:
        """📈 Calcul utilisation agents"""
        utilization = {}
        
        for agent_id, agent_conn in self.agent_connections.items():
            if agent_conn.is_active:
                utilization_rate = len(agent_conn.current_sessions) / agent_conn.max_concurrent_sessions
                utilization[agent_id] = round(utilization_rate * 100, 2)
                
        return utilization

    async def _get_ai_agent(self):
        """🤖 Récupération instance agent IA"""
        # Import local pour éviter circular imports
        from .ai_support_agent import create_ai_support_agent
        return await create_ai_support_agent(self.openai_api_key)

    async def _analyze_message_sentiment(self, content: str) -> float:
        """😊 Analyse sentiment message temps réel"""
        try:
            from textblob import TextBlob
            blob = TextBlob(content)
            return blob.sentiment.polarity
        except Exception:
            return 0.0

    async def _save_session_to_redis(self, session: ChatSession) -> None:
        """💾 Sauvegarde session Redis"""
        try:
            if self.redis_client:
                session_data = json.dumps(session.__dict__, default=str)
                await self.redis_client.setex(
                    f"chat_session:{session.session_id}",
                    timedelta(hours=24),
                    session_data
                )
        except Exception as e:
            logger.error(f"Erreur sauvegarde Redis: {e}")


class ChatQueueManager:
    """📋 Gestionnaire file d'attente chat"""
    
    def __init__(self):
        self.queue = []
        self.priority_queue = []
        
    async def add_to_queue(self, session: ChatSession, priority_boost: bool = False) -> None:
        """➕ Ajout session à la file d'attente"""
        if priority_boost or session.creator_tier in ["pro", "enterprise"]:
            self.priority_queue.append(session)
        else:
            self.queue.append(session)
            
        # Mise à jour position queue
        session.queue_position = len(self.queue) + len(self.priority_queue)

    async def get_next_session(self) -> Optional[ChatSession]:
        """⏭️ Récupération prochaine session"""
        if self.priority_queue:
            return self.priority_queue.pop(0)
        elif self.queue:
            return self.queue.pop(0)
        return None


class TranslationService:
    """🌍 Service traduction temps réel"""
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        
    async def translate_message(self, content: str, target_language: str) -> str:
        """🔄 Traduction message"""
        try:
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": f"Translate to {target_language}: {content}"
                }],
                temperature=0.1,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erreur traduction: {e}")
            return content  # Fallback: message original


class ChatAnalytics:
    """📊 Analytics chat en temps réel"""
    
    def __init__(self):
        self.daily_messages = 0
        self.satisfaction_scores = []
        self.volume_history = []
        
    async def record_message(self, message: ChatMessage, session: ChatSession) -> None:
        """📝 Enregistrement message pour analytics"""
        self.daily_messages += 1
        
        # Enregistrement volume par heure
        current_hour = datetime.utcnow().hour
        if not self.volume_history or self.volume_history[-1]["hour"] != current_hour:
            self.volume_history.append({
                "hour": current_hour,
                "count": 1,
                "timestamp": datetime.utcnow()
            })
        else:
            self.volume_history[-1]["count"] += 1

    async def get_daily_message_count(self) -> int:
        """📈 Compteur messages quotidien"""
        return self.daily_messages

    async def get_avg_satisfaction_score(self) -> float:
        """⭐ Score satisfaction moyen"""
        if not self.satisfaction_scores:
            return 0.0
        return sum(self.satisfaction_scores) / len(self.satisfaction_scores)

    async def get_volume_trend(self) -> str:
        """📊 Tendance volume chat"""
        if len(self.volume_history) < 2:
            return "stable"
            
        recent = self.volume_history[-3:]  # 3 dernières heures
        older = self.volume_history[-6:-3] if len(self.volume_history) >= 6 else []
        
        if not older:
            return "stable"
            
        recent_avg = sum(h["count"] for h in recent) / len(recent)
        older_avg = sum(h["count"] for h in older) / len(older)
        
        if recent_avg > older_avg * 1.2:
            return "increasing"
        elif recent_avg < older_avg * 0.8:
            return "decreasing"
        else:
            return "stable"