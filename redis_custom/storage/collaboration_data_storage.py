"""🤝 Collaboration Data Storage - Enterprise Grade
=================================================
Expert: BACKEND SENIOR + ML ENGINEER + IA PROMPT ENGINEER + MICROSERVICES
Technologies: Real-Time Collaboration + WebSocket + Event Sourcing + CRDT
Architecture: Level 2 - Storage Layer - Creator Economy  
Date: 2025-01-14

Enterprise storage solution for creator collaboration with real-time sync,
conflict resolution, event sourcing and distributed collaboration features.
=================================================
"""

import asyncio
import logging
import time
import hashlib
import json
import uuid
from typing import Dict, Any, Optional, List, Union, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque

# Optional imports with fallbacks
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

logger = logging.getLogger(__name__)

class CollaborationType(Enum):
    """Types de collaboration"""
    PROJECT = "project"
    CONTENT_CREATION = "content_creation"
    REVIEW = "review"
    LIVE_EDITING = "live_editing"
    BRAINSTORMING = "brainstorming"
    FEEDBACK = "feedback"
    MENTORSHIP = "mentorship"
    TEAM_PROJECT = "team_project"

class CollaborationStatus(Enum):
    """États de collaboration"""
    INITIATED = "initiated"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"

class ParticipantRole(Enum):
    """Rôles des participants"""
    OWNER = "owner"
    COLLABORATOR = "collaborator"
    REVIEWER = "reviewer"
    VIEWER = "viewer"
    MENTOR = "mentor"
    APPRENTICE = "apprentice"
    GUEST = "guest"

class EventType(Enum):
    """Types d'événements collaboration"""
    JOIN = "join"
    LEAVE = "leave"
    EDIT = "edit"
    COMMENT = "comment"
    APPROVE = "approve"
    REJECT = "reject"
    SHARE = "share"
    LOCK = "lock"
    UNLOCK = "unlock"
    SYNC = "sync"

@dataclass
class CollaborationConfig:
    """Configuration stockage collaboration"""
    redis_url: str = "redis://localhost:6379"
    max_pool_size: int = 25
    session_ttl: int = 3600  # 1 heure
    event_ttl: int = 86400 * 7  # 7 jours
    max_participants: int = 50
    enable_real_time: bool = True
    enable_conflict_resolution: bool = True
    sync_interval: int = 5  # secondes
    max_concurrent_edits: int = 10
    enable_version_control: bool = True

@dataclass
class CollaborationParticipant:
    """Participant à une collaboration"""
    user_id: str
    username: str
    role: ParticipantRole
    joined_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    permissions: Set[str] = field(default_factory=set)
    status: str = "online"
    cursor_position: Optional[Dict[str, Any]] = None
    editing_section: Optional[str] = None

@dataclass
class CollaborationEvent:
    """Événement de collaboration"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    collaboration_id: str = ""
    user_id: str = ""
    event_type: EventType = EventType.EDIT
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CollaborationSession:
    """Session de collaboration active"""
    session_id: str
    collaboration_id: str
    participants: Dict[str, CollaborationParticipant]
    active_edits: Dict[str, Dict[str, Any]]
    event_history: List[CollaborationEvent]
    current_state: Dict[str, Any]
    sync_state: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    last_sync: datetime = field(default_factory=datetime.now)
    status: CollaborationStatus = CollaborationStatus.ACTIVE

@dataclass
class CollaborationProject:
    """Projet de collaboration"""
    project_id: str
    title: str
    description: str
    creator_id: str
    collaboration_type: CollaborationType
    participants: Dict[str, CollaborationParticipant]
    content_data: Dict[str, Any]
    version_history: List[Dict[str, Any]]
    collaboration_rules: Dict[str, Any]
    monetization_split: Dict[str, float]
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: CollaborationStatus = CollaborationStatus.INITIATED

class CollaborationDataStorage:
    """Gestionnaire stockage données collaboration enterprise"""
    
    def __init__(self, config: CollaborationConfig):
        self.config = config
        self.redis_pool = None
        self.active_sessions = {}
        self.event_queue = asyncio.Queue()
        self.sync_tasks = {}
        self.conflict_resolver = ConflictResolver()
        
        # Métriques de performance
        self.metrics = {
            'active_collaborations': 0,
            'total_events': 0,
            'sync_operations': 0,
            'conflicts_resolved': 0,
            'real_time_connections': 0,
            'data_synchronized': 0
        }
        
        logger.info("CollaborationDataStorage initialisé")
    
    async def initialize(self):
        """Initialisation connexions Redis et processus"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis non disponible - mode dégradé")
            return
        
        try:
            self.redis_pool = redis.ConnectionPool.from_url(
                self.config.redis_url,
                max_connections=self.config.max_pool_size,
                retry_on_timeout=True
            )
            
            # Test connexion
            async with redis.Redis(connection_pool=self.redis_pool) as r:
                await r.ping()
            
            # Démarrage processus de synchronisation
            if self.config.enable_real_time:
                asyncio.create_task(self._sync_manager())
                asyncio.create_task(self._event_processor())
            
            logger.info("Connexion Redis établie pour la collaboration")
            
        except Exception as e:
            logger.error(f"Erreur initialisation Redis collaboration: {e}")
            self.redis_pool = None
    
    async def create_collaboration(self, creator_id: str, project_data: Dict[str, Any]) -> str:
        """Création nouvelle collaboration"""
        try:
            project_id = str(uuid.uuid4())
            
            # Création projet collaboration
            project = CollaborationProject(
                project_id=project_id,
                title=project_data.get('title', ''),
                description=project_data.get('description', ''),
                creator_id=creator_id,
                collaboration_type=CollaborationType(
                    project_data.get('type', CollaborationType.PROJECT.value)
                ),
                participants={
                    creator_id: CollaborationParticipant(
                        user_id=creator_id,
                        username=project_data.get('creator_username', creator_id),
                        role=ParticipantRole.OWNER
                    )
                },
                content_data=project_data.get('content', {}),
                collaboration_rules=project_data.get('rules', {}),
                monetization_split=project_data.get('monetization_split', {creator_id: 1.0})
            )
            
            # Stockage Redis
            if self.redis_pool:
                await self._store_collaboration_project(project)
            
            # Cache local
            self.active_sessions[project_id] = CollaborationSession(
                session_id=str(uuid.uuid4()),
                collaboration_id=project_id,
                participants=project.participants,
                active_edits={},
                event_history=[],
                current_state=project.content_data,
                sync_state={}
            )
            
            # Mise à jour métriques
            self.metrics['active_collaborations'] += 1
            
            logger.info(f"Collaboration créée: {project_id}")
            return project_id
            
        except Exception as e:
            logger.error(f"Erreur création collaboration: {e}")
            raise
    
    async def join_collaboration(self, collaboration_id: str, user_id: str, 
                                user_data: Dict[str, Any]) -> bool:
        """Rejoindre une collaboration"""
        try:
            # Récupération projet
            project = await self._get_collaboration_project(collaboration_id)
            if not project:
                return False
            
            # Vérification capacité
            if len(project.participants) >= self.config.max_participants:
                logger.warning(f"Collaboration {collaboration_id} complète")
                return False
            
            # Ajout participant
            participant = CollaborationParticipant(
                user_id=user_id,
                username=user_data.get('username', user_id),
                role=ParticipantRole(user_data.get('role', ParticipantRole.COLLABORATOR.value)),
                permissions=set(user_data.get('permissions', []))
            )
            
            project.participants[user_id] = participant
            
            # Mise à jour session active
            if collaboration_id in self.active_sessions:
                session = self.active_sessions[collaboration_id]
                session.participants[user_id] = participant
                
                # Événement join
                join_event = CollaborationEvent(
                    collaboration_id=collaboration_id,
                    user_id=user_id,
                    event_type=EventType.JOIN,
                    data={'username': participant.username, 'role': participant.role.value}
                )
                await self._add_event(join_event)
            
            # Sauvegarde
            if self.redis_pool:
                await self._store_collaboration_project(project)
            
            logger.info(f"Utilisateur {user_id} a rejoint collaboration {collaboration_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur join collaboration {collaboration_id}: {e}")
            return False
    
    async def leave_collaboration(self, collaboration_id: str, user_id: str) -> bool:
        """Quitter une collaboration"""
        try:
            # Récupération projet
            project = await self._get_collaboration_project(collaboration_id)
            if not project or user_id not in project.participants:
                return False
            
            # Suppression participant
            participant = project.participants.pop(user_id)
            
            # Mise à jour session active
            if collaboration_id in self.active_sessions:
                session = self.active_sessions[collaboration_id]
                session.participants.pop(user_id, None)
                
                # Événement leave
                leave_event = CollaborationEvent(
                    collaboration_id=collaboration_id,
                    user_id=user_id,
                    event_type=EventType.LEAVE,
                    data={'username': participant.username}
                )
                await self._add_event(leave_event)
                
                # Nettoyage éditions actives
                session.active_edits.pop(user_id, None)
            
            # Sauvegarde
            if self.redis_pool:
                await self._store_collaboration_project(project)
            
            logger.info(f"Utilisateur {user_id} a quitté collaboration {collaboration_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur leave collaboration {collaboration_id}: {e}")
            return False
    
    async def edit_content(self, collaboration_id: str, user_id: str, 
                          edit_data: Dict[str, Any]) -> bool:
        """Édition contenu collaboratif"""
        try:
            # Vérification session active
            if collaboration_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[collaboration_id]
            
            # Vérification participant
            if user_id not in session.participants:
                return False
            
            # Vérification permissions
            participant = session.participants[user_id]
            if not self._has_edit_permission(participant, edit_data):
                return False
            
            # Application édition avec résolution de conflits
            edit_result = await self._apply_edit_with_conflict_resolution(
                session, user_id, edit_data
            )
            
            if edit_result['success']:
                # Événement edit
                edit_event = CollaborationEvent(
                    collaboration_id=collaboration_id,
                    user_id=user_id,
                    event_type=EventType.EDIT,
                    data=edit_data,
                    metadata=edit_result.get('metadata', {})
                )
                await self._add_event(edit_event)
                
                # Mise à jour état actuel
                session.current_state.update(edit_result['new_state'])
                session.last_sync = datetime.now()
                
                # Planification synchronisation
                await self._schedule_sync(collaboration_id)
                
                self.metrics['total_events'] += 1
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur édition collaboration {collaboration_id}: {e}")
            return False
    
    async def get_collaboration_state(self, collaboration_id: str, 
                                    user_id: str) -> Optional[Dict[str, Any]]:
        """Récupération état collaboration"""
        try:
            # Session active d'abord
            if collaboration_id in self.active_sessions:
                session = self.active_sessions[collaboration_id]
                
                # Vérification accès
                if user_id not in session.participants:
                    return None
                
                return {
                    'collaboration_id': collaboration_id,
                    'current_state': session.current_state,
                    'participants': {
                        uid: {
                            'username': p.username,
                            'role': p.role.value,
                            'status': p.status,
                            'last_active': p.last_active.isoformat(),
                            'editing_section': p.editing_section
                        }
                        for uid, p in session.participants.items()
                    },
                    'active_edits': session.active_edits,
                    'last_sync': session.last_sync.isoformat()
                }
            
            # Redis sinon
            if self.redis_pool:
                project = await self._get_collaboration_project(collaboration_id)
                if project and user_id in project.participants:
                    return {
                        'collaboration_id': collaboration_id,
                        'current_state': project.content_data,
                        'participants': {
                            uid: {
                                'username': p.username,
                                'role': p.role.value,
                                'status': 'offline',
                                'last_active': p.last_active.isoformat()
                            }
                            for uid, p in project.participants.items()
                        },
                        'last_sync': project.updated_at.isoformat()
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur récupération état {collaboration_id}: {e}")
            return None
    
    async def get_collaboration_history(self, collaboration_id: str, 
                                       user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Récupération historique collaboration"""
        try:
            # Vérification accès
            project = await self._get_collaboration_project(collaboration_id)
            if not project or user_id not in project.participants:
                return []
            
            events = []
            
            # Session active
            if collaboration_id in self.active_sessions:
                session = self.active_sessions[collaboration_id]
                events.extend(session.event_history[-limit:])
            
            # Redis pour historique complet
            if self.redis_pool:
                redis_events = await self._get_events_from_redis(collaboration_id, limit)
                events.extend(redis_events)
            
            # Tri et limitation
            events.sort(key=lambda x: x.timestamp, reverse=True)
            events = events[:limit]
            
            return [
                {
                    'event_id': event.event_id,
                    'user_id': event.user_id,
                    'event_type': event.event_type.value,
                    'data': event.data,
                    'timestamp': event.timestamp.isoformat(),
                    'metadata': event.metadata
                }
                for event in events
            ]
            
        except Exception as e:
            logger.error(f"Erreur récupération historique {collaboration_id}: {e}")
            return []
    
    async def sync_collaboration(self, collaboration_id: str) -> bool:
        """Synchronisation collaboration"""
        try:
            if collaboration_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[collaboration_id]
            
            # Récupération projet persistant
            project = await self._get_collaboration_project(collaboration_id)
            if not project:
                return False
            
            # Fusion des changements
            merged_state = await self._merge_collaboration_states(
                project.content_data, session.current_state
            )
            
            # Mise à jour projet
            project.content_data = merged_state
            project.updated_at = datetime.now()
            
            # Sauvegarde
            if self.redis_pool:
                await self._store_collaboration_project(project)
            
            # Mise à jour session
            session.current_state = merged_state
            session.last_sync = datetime.now()
            
            # Événement sync
            sync_event = CollaborationEvent(
                collaboration_id=collaboration_id,
                user_id="system",
                event_type=EventType.SYNC,
                data={'synced_at': datetime.now().isoformat()}
            )
            await self._add_event(sync_event)
            
            self.metrics['sync_operations'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Erreur synchronisation {collaboration_id}: {e}")
            return False
    
    async def _store_collaboration_project(self, project: CollaborationProject):
        """Stockage projet collaboration Redis"""
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            project_key = f"collaboration:project:{project.project_id}"
            project_data = {
                'project_id': project.project_id,
                'title': project.title,
                'description': project.description,
                'creator_id': project.creator_id,
                'collaboration_type': project.collaboration_type.value,
                'participants': {
                    uid: {
                        'user_id': p.user_id,
                        'username': p.username,
                        'role': p.role.value,
                        'joined_at': p.joined_at.isoformat(),
                        'last_active': p.last_active.isoformat(),
                        'permissions': list(p.permissions),
                        'status': p.status
                    }
                    for uid, p in project.participants.items()
                },
                'content_data': project.content_data,
                'version_history': project.version_history,
                'collaboration_rules': project.collaboration_rules,
                'monetization_split': project.monetization_split,
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat(),
                'status': project.status.value
            }
            
            await r.setex(project_key, self.config.session_ttl * 24, json.dumps(project_data))
    
    async def _get_collaboration_project(self, collaboration_id: str) -> Optional[CollaborationProject]:
        """Récupération projet collaboration"""
        if not self.redis_pool:
            return None
        
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            project_key = f"collaboration:project:{collaboration_id}"
            project_json = await r.get(project_key)
            
            if not project_json:
                return None
            
            data = json.loads(project_json)
            
            # Reconstruction participants
            participants = {}
            for uid, p_data in data['participants'].items():
                participants[uid] = CollaborationParticipant(
                    user_id=p_data['user_id'],
                    username=p_data['username'],
                    role=ParticipantRole(p_data['role']),
                    joined_at=datetime.fromisoformat(p_data['joined_at']),
                    last_active=datetime.fromisoformat(p_data['last_active']),
                    permissions=set(p_data['permissions']),
                    status=p_data['status']
                )
            
            return CollaborationProject(
                project_id=data['project_id'],
                title=data['title'],
                description=data['description'],
                creator_id=data['creator_id'],
                collaboration_type=CollaborationType(data['collaboration_type']),
                participants=participants,
                content_data=data['content_data'],
                version_history=data['version_history'],
                collaboration_rules=data['collaboration_rules'],
                monetization_split=data['monetization_split'],
                created_at=datetime.fromisoformat(data['created_at']),
                updated_at=datetime.fromisoformat(data['updated_at']),
                status=CollaborationStatus(data['status'])
            )
    
    async def _add_event(self, event: CollaborationEvent):
        """Ajout événement à la queue"""
        await self.event_queue.put(event)
        
        # Ajout à l'historique session
        if event.collaboration_id in self.active_sessions:
            session = self.active_sessions[event.collaboration_id]
            session.event_history.append(event)
            
            # Limitation historique local
            if len(session.event_history) > 1000:
                session.event_history = session.event_history[-1000:]
    
    async def _event_processor(self):
        """Processeur événements asynchrone"""
        while True:
            try:
                event = await self.event_queue.get()
                
                if self.redis_pool:
                    await self._store_event_to_redis(event)
                
                # Notification temps réel (placeholder)
                await self._notify_real_time_participants(event)
                
            except Exception as e:
                logger.error(f"Erreur traitement événement: {e}")
                await asyncio.sleep(1)
    
    async def _store_event_to_redis(self, event: CollaborationEvent):
        """Stockage événement Redis"""
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            event_key = f"collaboration:events:{event.collaboration_id}:{event.event_id}"
            event_data = {
                'event_id': event.event_id,
                'collaboration_id': event.collaboration_id,
                'user_id': event.user_id,
                'event_type': event.event_type.value,
                'data': event.data,
                'timestamp': event.timestamp.isoformat(),
                'metadata': event.metadata
            }
            
            await r.setex(event_key, self.config.event_ttl, json.dumps(event_data))
            
            # Index temporel
            timeline_key = f"collaboration:timeline:{event.collaboration_id}"
            await r.zadd(timeline_key, {event.event_id: event.timestamp.timestamp()})
    
    async def _get_events_from_redis(self, collaboration_id: str, 
                                    limit: int) -> List[CollaborationEvent]:
        """Récupération événements Redis"""
        events = []
        
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            timeline_key = f"collaboration:timeline:{collaboration_id}"
            event_ids = await r.zrevrange(timeline_key, 0, limit-1)
            
            for event_id in event_ids:
                event_key = f"collaboration:events:{collaboration_id}:{event_id}"
                event_json = await r.get(event_key)
                
                if event_json:
                    data = json.loads(event_json)
                    event = CollaborationEvent(
                        event_id=data['event_id'],
                        collaboration_id=data['collaboration_id'],
                        user_id=data['user_id'],
                        event_type=EventType(data['event_type']),
                        data=data['data'],
                        timestamp=datetime.fromisoformat(data['timestamp']),
                        metadata=data['metadata']
                    )
                    events.append(event)
        
        return events
    
    async def _notify_real_time_participants(self, event: CollaborationEvent):
        """Notification temps réel participants (placeholder)"""
        # TODO: Implémentation WebSocket/SSE pour notifications temps réel
        pass
    
    async def _sync_manager(self):
        """Gestionnaire synchronisation périodique"""
        while True:
            try:
                await asyncio.sleep(self.config.sync_interval)
                
                for collaboration_id in list(self.active_sessions.keys()):
                    await self.sync_collaboration(collaboration_id)
                
            except Exception as e:
                logger.error(f"Erreur sync manager: {e}")
                await asyncio.sleep(self.config.sync_interval)
    
    async def _schedule_sync(self, collaboration_id: str):
        """Planification synchronisation"""
        if collaboration_id in self.sync_tasks:
            self.sync_tasks[collaboration_id].cancel()
        
        self.sync_tasks[collaboration_id] = asyncio.create_task(
            self._delayed_sync(collaboration_id, 2)  # 2 secondes de délai
        )
    
    async def _delayed_sync(self, collaboration_id: str, delay: int):
        """Synchronisation retardée"""
        await asyncio.sleep(delay)
        await self.sync_collaboration(collaboration_id)
        self.sync_tasks.pop(collaboration_id, None)
    
    def _has_edit_permission(self, participant: CollaborationParticipant, 
                            edit_data: Dict[str, Any]) -> bool:
        """Vérification permissions édition"""
        if participant.role in [ParticipantRole.OWNER, ParticipantRole.COLLABORATOR]:
            return True
        
        if participant.role == ParticipantRole.REVIEWER and edit_data.get('type') == 'comment':
            return True
        
        return 'edit' in participant.permissions
    
    async def _apply_edit_with_conflict_resolution(self, session: CollaborationSession,
                                                  user_id: str, edit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Application édition avec résolution conflits"""
        try:
            # Détection conflits
            conflicts = await self.conflict_resolver.detect_conflicts(
                session.current_state, edit_data, session.active_edits
            )
            
            if conflicts:
                # Résolution conflits
                resolution = await self.conflict_resolver.resolve_conflicts(
                    conflicts, session.current_state, edit_data
                )
                
                self.metrics['conflicts_resolved'] += 1
                
                return {
                    'success': True,
                    'new_state': resolution['resolved_state'],
                    'metadata': {
                        'conflicts_detected': len(conflicts),
                        'resolution_strategy': resolution['strategy']
                    }
                }
            else:
                # Application directe
                new_state = session.current_state.copy()
                new_state.update(edit_data.get('changes', {}))
                
                return {
                    'success': True,
                    'new_state': new_state,
                    'metadata': {'direct_apply': True}
                }
        
        except Exception as e:
            logger.error(f"Erreur application édition: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _merge_collaboration_states(self, persistent_state: Dict[str, Any],
                                         session_state: Dict[str, Any]) -> Dict[str, Any]:
        """Fusion états collaboration"""
        # Stratégie simple de fusion (last-write-wins pour maintenant)
        merged = persistent_state.copy()
        merged.update(session_state)
        return merged
    
    async def get_collaboration_analytics(self, collaboration_id: str) -> Dict[str, Any]:
        """Analytics collaboration"""
        try:
            session = self.active_sessions.get(collaboration_id)
            project = await self._get_collaboration_project(collaboration_id)
            
            if not session and not project:
                return {}
            
            analytics = {
                'collaboration_id': collaboration_id,
                'participant_count': len(project.participants if project else {}),
                'active_participants': len(session.participants if session else {}),
                'total_events': len(session.event_history if session else []),
                'collaboration_duration': 0,
                'activity_timeline': [],
                'contribution_stats': {},
                'engagement_score': 0
            }
            
            if project:
                duration = (datetime.now() - project.created_at).total_seconds()
                analytics['collaboration_duration'] = duration
                
                # Stats contribution par participant
                for user_id, participant in project.participants.items():
                    analytics['contribution_stats'][user_id] = {
                        'username': participant.username,
                        'role': participant.role.value,
                        'duration': (datetime.now() - participant.joined_at).total_seconds(),
                        'last_active': participant.last_active.isoformat()
                    }
            
            if session:
                # Score engagement basé sur l'activité
                recent_events = len([
                    e for e in session.event_history
                    if (datetime.now() - e.timestamp).total_seconds() < 3600
                ])
                analytics['engagement_score'] = min(recent_events / 10, 1.0)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Erreur analytics collaboration {collaboration_id}: {e}")
            return {}

class ConflictResolver:
    """Résolveur de conflits pour collaboration"""
    
    async def detect_conflicts(self, current_state: Dict[str, Any], 
                              edit_data: Dict[str, Any], 
                              active_edits: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Détection conflits"""
        conflicts = []
        
        changes = edit_data.get('changes', {})
        
        for key, value in changes.items():
            # Conflit si même clé modifiée par autre utilisateur
            for user_id, edit in active_edits.items():
                if key in edit.get('changes', {}):
                    conflicts.append({
                        'type': 'concurrent_edit',
                        'key': key,
                        'current_value': current_state.get(key),
                        'new_value': value,
                        'conflicting_value': edit['changes'][key],
                        'conflicting_user': user_id
                    })
        
        return conflicts
    
    async def resolve_conflicts(self, conflicts: List[Dict[str, Any]], 
                               current_state: Dict[str, Any], 
                               edit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Résolution conflits"""
        resolved_state = current_state.copy()
        strategy = "last_write_wins"  # Stratégie simple
        
        # Application des changements (dernière écriture gagne)
        changes = edit_data.get('changes', {})
        resolved_state.update(changes)
        
        return {
            'resolved_state': resolved_state,
            'strategy': strategy,
            'conflicts_resolved': len(conflicts)
        }

# Factory function
def create_collaboration_data_storage(
    redis_url: str = "redis://localhost:6379",
    **kwargs
) -> CollaborationDataStorage:
    """Factory pour création stockage collaboration"""
    config = CollaborationConfig(redis_url=redis_url, **kwargs)
    return CollaborationDataStorage(config)

# Export classes principales
__all__ = [
    'CollaborationDataStorage',
    'CollaborationConfig',
    'CollaborationParticipant',
    'CollaborationEvent',
    'CollaborationSession',
    'CollaborationProject',
    'CollaborationType',
    'CollaborationStatus',
    'ParticipantRole',
    'EventType',
    'ConflictResolver',
    'create_collaboration_data_storage'
]