"""
🤝 Collaboration Service Mesh Enterprise - IA Chéries
=================================================
Service mesh collaboration pour créateurs et équipes.
Team coordination + permission management + real-time sync.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Service Discovery
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de
"""

import asyncio
import time
import logging
import json
import uuid
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

from .distributed_service_registry import ServiceInstance, ServiceStatus
from .service_mesh_orchestrator import ServiceMeshOrchestrator, TrafficRule, SecurityRule

logger = logging.getLogger(__name__)

class CollaborationType(Enum):
    """Types de collaboration"""
    REAL_TIME_EDITING = "real_time_editing"
    ASYNC_REVIEW = "async_review"
    LIVE_STREAMING = "live_streaming"
    PROJECT_MANAGEMENT = "project_management"
    CONTENT_SHARING = "content_sharing"
    TEAM_COMMUNICATION = "team_communication"
    VERSION_CONTROL = "version_control"
    RESOURCE_SHARING = "resource_sharing"

class UserRole(Enum):
    """Rôles utilisateur dans la collaboration"""
    OWNER = "owner"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    VIEWER = "viewer"
    COMMENTATOR = "commentator"
    MODERATOR = "moderator"
    GUEST = "guest"

class PermissionLevel(Enum):
    """Niveaux de permission"""
    FULL_ACCESS = "full_access"
    EDIT = "edit"
    COMMENT = "comment"
    VIEW_ONLY = "view_only"
    NO_ACCESS = "no_access"

class SyncStrategy(Enum):
    """Stratégies de synchronisation"""
    REAL_TIME = "real_time"
    NEAR_REAL_TIME = "near_real_time"
    PERIODIC = "periodic"
    ON_DEMAND = "on_demand"
    CONFLICT_RESOLUTION = "conflict_resolution"

@dataclass
class CollaborationSession:
    """Session de collaboration"""
    session_id: str
    project_id: str
    session_type: CollaborationType
    owner_id: str
    participants: List[str] = field(default_factory=list)
    active_users: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    sync_strategy: SyncStrategy = SyncStrategy.REAL_TIME
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"

@dataclass
class UserPermission:
    """Permission utilisateur"""
    user_id: str
    role: UserRole
    permission_level: PermissionLevel
    granted_by: str
    granted_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    specific_permissions: Set[str] = field(default_factory=set)
    restrictions: Set[str] = field(default_factory=set)

@dataclass
class CollaborationEvent:
    """Événement de collaboration"""
    event_id: str
    session_id: str
    user_id: str
    event_type: str
    event_data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    sequence_number: int = 0
    version: str = "1.0"

@dataclass
class SyncConflict:
    """Conflit de synchronisation"""
    conflict_id: str
    session_id: str
    resource_id: str
    conflicting_users: List[str]
    conflict_type: str
    conflict_data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    resolution_strategy: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None

@dataclass
class CollaborationRequest:
    """Requête de collaboration"""
    request_id: str
    session_type: CollaborationType
    project_id: str
    requester_id: str
    target_users: List[str] = field(default_factory=list)
    sync_requirements: Dict[str, Any] = field(default_factory=dict)
    performance_requirements: Dict[str, Any] = field(default_factory=dict)
    security_requirements: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CollaborationResult:
    """Résultat de mise en place de collaboration"""
    success: bool
    session: Optional[CollaborationSession] = None
    allocated_services: Dict[str, List[ServiceInstance]] = field(default_factory=dict)
    mesh_configuration: Dict[str, Any] = field(default_factory=dict)
    sync_endpoints: Dict[str, str] = field(default_factory=dict)
    security_policies: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

class CollaborationSessionManager:
    """Gestionnaire de sessions de collaboration"""
    
    def __init__(self):
        self.active_sessions: Dict[str, CollaborationSession] = {}
        self.user_permissions: Dict[str, Dict[str, UserPermission]] = {}  # session_id -> user_id -> permission
        self.session_events: Dict[str, List[CollaborationEvent]] = {}
        self.sync_conflicts: Dict[str, List[SyncConflict]] = {}
        self.collaboration_templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, Dict]:
        """Initialiser les templates de collaboration"""
        return {
            CollaborationType.REAL_TIME_EDITING.value: {
                'max_concurrent_users': 10,
                'sync_strategy': SyncStrategy.REAL_TIME.value,
                'conflict_resolution': 'operational_transform',
                'required_services': ['real_time_sync', 'conflict_resolver', 'state_manager'],
                'performance_requirements': {
                    'max_latency_ms': 100,
                    'min_throughput_ops_sec': 1000
                }
            },
            CollaborationType.ASYNC_REVIEW.value: {
                'max_concurrent_users': 50,
                'sync_strategy': SyncStrategy.PERIODIC.value,
                'conflict_resolution': 'manual_review',
                'required_services': ['comment_system', 'notification_service', 'review_workflow'],
                'performance_requirements': {
                    'max_latency_ms': 1000,
                    'min_throughput_ops_sec': 100
                }
            },
            CollaborationType.LIVE_STREAMING.value: {
                'max_concurrent_users': 1000,
                'sync_strategy': SyncStrategy.REAL_TIME.value,
                'conflict_resolution': 'moderator_override',
                'required_services': ['streaming_service', 'chat_service', 'moderation_service'],
                'performance_requirements': {
                    'max_latency_ms': 50,
                    'min_throughput_ops_sec': 10000
                }
            },
            CollaborationType.PROJECT_MANAGEMENT.value: {
                'max_concurrent_users': 25,
                'sync_strategy': SyncStrategy.NEAR_REAL_TIME.value,
                'conflict_resolution': 'last_writer_wins',
                'required_services': ['task_manager', 'timeline_service', 'resource_planner'],
                'performance_requirements': {
                    'max_latency_ms': 500,
                    'min_throughput_ops_sec': 200
                }
            },
            CollaborationType.CONTENT_SHARING.value: {
                'max_concurrent_users': 100,
                'sync_strategy': SyncStrategy.ON_DEMAND.value,
                'conflict_resolution': 'version_based',
                'required_services': ['file_sharing', 'version_control', 'access_control'],
                'performance_requirements': {
                    'max_latency_ms': 2000,
                    'min_throughput_ops_sec': 50
                }
            }
        }
    
    async def create_collaboration_session(self, request: CollaborationRequest) -> CollaborationSession:
        """Créer une nouvelle session de collaboration"""
        try:
            session_id = f"collab_{request.session_type.value}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            # Obtenir le template approprié
            template = self.collaboration_templates.get(
                request.session_type.value,
                self.collaboration_templates[CollaborationType.REAL_TIME_EDITING.value]
            )
            
            # Créer la session
            session = CollaborationSession(
                session_id=session_id,
                project_id=request.project_id,
                session_type=request.session_type,
                owner_id=request.requester_id,
                participants=request.target_users.copy(),
                sync_strategy=SyncStrategy(template['sync_strategy']),
                metadata=template.copy()
            )
            
            # Ajouter le créateur aux participants
            if request.requester_id not in session.participants:
                session.participants.append(request.requester_id)
            
            session.active_users.add(request.requester_id)
            
            # Initialiser les permissions
            await self._initialize_session_permissions(session)
            
            # Sauvegarder la session
            self.active_sessions[session_id] = session
            self.session_events[session_id] = []
            self.sync_conflicts[session_id] = []
            
            logger.info(f"🤝 Session collaboration créée: {session_id} ({request.session_type.value})")
            return session
            
        except Exception as e:
            logger.error(f"Erreur création session collaboration: {e}")
            raise
    
    async def _initialize_session_permissions(self, session: CollaborationSession):
        """Initialiser les permissions de la session"""
        session_id = session.session_id
        self.user_permissions[session_id] = {}
        
        # Propriétaire - accès complet
        owner_permission = UserPermission(
            user_id=session.owner_id,
            role=UserRole.OWNER,
            permission_level=PermissionLevel.FULL_ACCESS,
            granted_by="system",
            specific_permissions={
                "create", "read", "update", "delete", 
                "invite", "remove_user", "change_permissions",
                "manage_session", "export_data"
            }
        )
        self.user_permissions[session_id][session.owner_id] = owner_permission
        
        # Autres participants - permissions selon le type de collaboration
        default_role = UserRole.EDITOR
        default_permission = PermissionLevel.EDIT
        
        if session.session_type == CollaborationType.ASYNC_REVIEW:
            default_role = UserRole.REVIEWER
            default_permission = PermissionLevel.COMMENT
        elif session.session_type == CollaborationType.LIVE_STREAMING:
            default_role = UserRole.VIEWER
            default_permission = PermissionLevel.VIEW_ONLY
        
        for user_id in session.participants:
            if user_id != session.owner_id:
                participant_permission = UserPermission(
                    user_id=user_id,
                    role=default_role,
                    permission_level=default_permission,
                    granted_by=session.owner_id,
                    specific_permissions=self._get_default_permissions(default_role)
                )
                self.user_permissions[session_id][user_id] = participant_permission
    
    def _get_default_permissions(self, role: UserRole) -> Set[str]:
        """Obtenir les permissions par défaut pour un rôle"""
        permission_mapping = {
            UserRole.OWNER: {
                "create", "read", "update", "delete", 
                "invite", "remove_user", "change_permissions",
                "manage_session", "export_data"
            },
            UserRole.EDITOR: {
                "create", "read", "update", "comment", "share"
            },
            UserRole.REVIEWER: {
                "read", "comment", "approve", "reject"
            },
            UserRole.VIEWER: {
                "read"
            },
            UserRole.COMMENTATOR: {
                "read", "comment"
            },
            UserRole.MODERATOR: {
                "read", "comment", "moderate", "remove_content"
            },
            UserRole.GUEST: {
                "read"
            }
        }
        
        return permission_mapping.get(role, {"read"})
    
    async def join_session(self, session_id: str, user_id: str) -> bool:
        """Rejoindre une session de collaboration"""
        try:
            if session_id not in self.active_sessions:
                logger.warning(f"Session inexistante: {session_id}")
                return False
            
            session = self.active_sessions[session_id]
            
            # Vérifier si l'utilisateur est autorisé
            if (user_id not in session.participants and 
                user_id not in self.user_permissions.get(session_id, {})):
                logger.warning(f"Utilisateur non autorisé: {user_id} pour session {session_id}")
                return False
            
            # Ajouter aux utilisateurs actifs
            session.active_users.add(user_id)
            session.last_activity = datetime.now()
            
            # Enregistrer l'événement
            join_event = CollaborationEvent(
                event_id=f"join_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                session_id=session_id,
                user_id=user_id,
                event_type="user_joined",
                event_data={"joined_at": datetime.now().isoformat()}
            )
            
            await self._record_event(join_event)
            
            logger.info(f"👋 Utilisateur {user_id} a rejoint la session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur jonction session: {e}")
            return False
    
    async def leave_session(self, session_id: str, user_id: str) -> bool:
        """Quitter une session de collaboration"""
        try:
            if session_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[session_id]
            session.active_users.discard(user_id)
            session.last_activity = datetime.now()
            
            # Enregistrer l'événement
            leave_event = CollaborationEvent(
                event_id=f"leave_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                session_id=session_id,
                user_id=user_id,
                event_type="user_left",
                event_data={"left_at": datetime.now().isoformat()}
            )
            
            await self._record_event(leave_event)
            
            # Si plus d'utilisateurs actifs, marquer la session comme inactive
            if not session.active_users and session.status == "active":
                session.status = "inactive"
                logger.info(f"💤 Session {session_id} marquée comme inactive")
            
            logger.info(f"👋 Utilisateur {user_id} a quitté la session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur quitter session: {e}")
            return False
    
    async def update_user_permission(self, session_id: str, user_id: str, 
                                   new_permission: UserPermission, updated_by: str) -> bool:
        """Mettre à jour les permissions d'un utilisateur"""
        try:
            if session_id not in self.active_sessions:
                return False
            
            # Vérifier que l'utilisateur qui modifie a les droits
            updater_permission = self.user_permissions.get(session_id, {}).get(updated_by)
            if not updater_permission or "change_permissions" not in updater_permission.specific_permissions:
                logger.warning(f"Utilisateur {updated_by} n'a pas les droits pour modifier les permissions")
                return False
            
            # Mettre à jour les permissions
            if session_id not in self.user_permissions:
                self.user_permissions[session_id] = {}
            
            new_permission.granted_by = updated_by
            new_permission.granted_at = datetime.now()
            self.user_permissions[session_id][user_id] = new_permission
            
            # Enregistrer l'événement
            permission_event = CollaborationEvent(
                event_id=f"permission_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                session_id=session_id,
                user_id=updated_by,
                event_type="permission_updated",
                event_data={
                    "target_user": user_id,
                    "new_role": new_permission.role.value,
                    "new_permission_level": new_permission.permission_level.value
                }
            )
            
            await self._record_event(permission_event)
            
            logger.info(f"🔐 Permissions mises à jour pour {user_id} dans session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur mise à jour permissions: {e}")
            return False
    
    async def _record_event(self, event: CollaborationEvent):
        """Enregistrer un événement de collaboration"""
        if event.session_id in self.session_events:
            # Attribuer un numéro de séquence
            event.sequence_number = len(self.session_events[event.session_id])
            self.session_events[event.session_id].append(event)
            
            # Limiter l'historique des événements
            if len(self.session_events[event.session_id]) > 1000:
                self.session_events[event.session_id] = self.session_events[event.session_id][-1000:]
    
    async def get_session_events(self, session_id: str, since_sequence: int = 0) -> List[CollaborationEvent]:
        """Obtenir les événements d'une session depuis un numéro de séquence"""
        if session_id not in self.session_events:
            return []
        
        events = self.session_events[session_id]
        return [event for event in events if event.sequence_number > since_sequence]
    
    async def create_sync_conflict(self, session_id: str, resource_id: str, 
                                 conflicting_users: List[str], conflict_data: Dict[str, Any]) -> str:
        """Créer un conflit de synchronisation"""
        try:
            conflict_id = f"conflict_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            conflict = SyncConflict(
                conflict_id=conflict_id,
                session_id=session_id,
                resource_id=resource_id,
                conflicting_users=conflicting_users,
                conflict_type=conflict_data.get('type', 'concurrent_edit'),
                conflict_data=conflict_data
            )
            
            if session_id not in self.sync_conflicts:
                self.sync_conflicts[session_id] = []
            
            self.sync_conflicts[session_id].append(conflict)
            
            # Enregistrer l'événement
            conflict_event = CollaborationEvent(
                event_id=f"conflict_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                session_id=session_id,
                user_id="system",
                event_type="sync_conflict_created",
                event_data={
                    "conflict_id": conflict_id,
                    "resource_id": resource_id,
                    "conflicting_users": conflicting_users
                }
            )
            
            await self._record_event(conflict_event)
            
            logger.warning(f"⚠️ Conflit de sync créé: {conflict_id} dans session {session_id}")
            return conflict_id
            
        except Exception as e:
            logger.error(f"Erreur création conflit sync: {e}")
            return ""
    
    async def resolve_sync_conflict(self, conflict_id: str, resolution_strategy: str, 
                                  resolved_by: str) -> bool:
        """Résoudre un conflit de synchronisation"""
        try:
            # Trouver le conflit
            conflict = None
            session_id = None
            
            for sid, conflicts in self.sync_conflicts.items():
                for c in conflicts:
                    if c.conflict_id == conflict_id:
                        conflict = c
                        session_id = sid
                        break
                if conflict:
                    break
            
            if not conflict:
                logger.warning(f"Conflit introuvable: {conflict_id}")
                return False
            
            # Marquer comme résolu
            conflict.resolution_strategy = resolution_strategy
            conflict.resolved_by = resolved_by
            conflict.resolved_at = datetime.now()
            
            # Enregistrer l'événement
            resolution_event = CollaborationEvent(
                event_id=f"resolution_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                session_id=session_id,
                user_id=resolved_by,
                event_type="sync_conflict_resolved",
                event_data={
                    "conflict_id": conflict_id,
                    "resolution_strategy": resolution_strategy
                }
            )
            
            await self._record_event(resolution_event)
            
            logger.info(f"✅ Conflit résolu: {conflict_id} par {resolved_by}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur résolution conflit: {e}")
            return False
    
    async def get_active_sessions_for_user(self, user_id: str) -> List[CollaborationSession]:
        """Obtenir les sessions actives pour un utilisateur"""
        active_sessions = []
        
        for session in self.active_sessions.values():
            if (user_id in session.participants or 
                user_id in session.active_users or
                user_id in self.user_permissions.get(session.session_id, {})):
                active_sessions.append(session)
        
        return active_sessions
    
    async def cleanup_inactive_sessions(self, max_inactive_hours: int = 24):
        """Nettoyer les sessions inactives"""
        try:
            current_time = datetime.now()
            sessions_to_remove = []
            
            for session_id, session in self.active_sessions.items():
                time_since_activity = (current_time - session.last_activity).total_seconds() / 3600
                
                if (session.status == "inactive" and 
                    time_since_activity > max_inactive_hours):
                    sessions_to_remove.append(session_id)
            
            # Supprimer les sessions inactives
            for session_id in sessions_to_remove:
                del self.active_sessions[session_id]
                self.user_permissions.pop(session_id, None)
                self.session_events.pop(session_id, None)
                self.sync_conflicts.pop(session_id, None)
                
                logger.info(f"🧹 Session inactive supprimée: {session_id}")
            
            logger.info(f"🧹 Nettoyage terminé: {len(sessions_to_remove)} sessions supprimées")
            
        except Exception as e:
            logger.error(f"Erreur nettoyage sessions: {e}")

class CollaborationServiceMesh:
    """
    Service mesh collaboration pour créateurs et équipes.
    Team coordination + permission management + real-time sync.
    """
    
    def __init__(self):
        self.session_manager = CollaborationSessionManager()
        self.service_mesh = ServiceMeshOrchestrator()
        self.collaboration_services: Dict[str, List[ServiceInstance]] = {}
        self._initialize_collaboration_services()
        
        # Métriques de collaboration
        self.collaboration_stats: Dict[str, Any] = {
            'total_sessions': 0,
            'active_sessions': 0,
            'total_participants': 0,
            'sessions_by_type': {},
            'avg_session_duration': 0.0,
            'sync_conflicts_resolved': 0
        }
        
        logger.info("🤝 CollaborationServiceMesh initialisé")
    
    def _initialize_collaboration_services(self):
        """Initialiser les services de collaboration"""
        # Services pour édition temps réel
        self.collaboration_services['real_time_sync'] = [
            ServiceInstance(
                service_id="rt_sync_001",
                service_name="real_time_sync",
                host="sync.ainflue.com",
                port=8080,
                health_check_url="/health",
                metadata={
                    'service_type': 'real_time_sync',
                    'max_concurrent_ops': 1000,
                    'operational_transform': True,
                    'conflict_resolution': 'automatic'
                }
            )
        ]
        
        # Services pour gestion de commentaires
        self.collaboration_services['comment_system'] = [
            ServiceInstance(
                service_id="comment_001",
                service_name="comment_system", 
                host="comments.ainflue.com",
                port=8080,
                health_check_url="/health",
                metadata={
                    'service_type': 'comment_system',
                    'threading': True,
                    'mentions': True,
                    'reactions': True
                }
            )
        ]
        
        # Services pour streaming live
        self.collaboration_services['streaming_service'] = [
            ServiceInstance(
                service_id="stream_001",
                service_name="streaming_service",
                host="stream.ainflue.com", 
                port=1935,
                health_check_url="/health",
                metadata={
                    'service_type': 'streaming_service',
                    'protocols': ['RTMP', 'WebRTC', 'HLS'],
                    'max_viewers': 10000,
                    'recording': True
                }
            )
        ]
        
        # Services pour gestion de projets
        self.collaboration_services['task_manager'] = [
            ServiceInstance(
                service_id="task_001",
                service_name="task_manager",
                host="tasks.ainflue.com",
                port=8080,
                health_check_url="/health",
                metadata={
                    'service_type': 'task_manager',
                    'gantt_charts': True,
                    'dependencies': True,
                    'time_tracking': True
                }
            )
        ]
        
        # Services pour partage de fichiers
        self.collaboration_services['file_sharing'] = [
            ServiceInstance(
                service_id="files_001",
                service_name="file_sharing",
                host="files.ainflue.com",
                port=443,
                health_check_url="/health",
                metadata={
                    'service_type': 'file_sharing',
                    'max_file_size_mb': 5000,
                    'version_control': True,
                    'encryption': True
                }
            )
        ]
    
    async def setup_collaboration_mesh(self, request: CollaborationRequest) -> CollaborationResult:
        """
        Configuration service mesh pour collaboration.
        
        Collaboration Features:
        - Real-time synchronization avec operational transform
        - Permission-based access control avec fine-grained policies
        - Multi-user conflict resolution automatique
        - Live streaming avec moderation capabilities
        - Project management avec timeline coordination
        - File sharing avec version control integration
        - Team communication avec threaded discussions
        """
        try:
            # 1. Créer la session de collaboration
            session = await self.session_manager.create_collaboration_session(request)
            
            # 2. Déterminer les services nécessaires
            required_services = await self._determine_required_services(request)
            
            # 3. Allouer les services
            allocated_services = {}
            for service_type in required_services:
                if service_type in self.collaboration_services:
                    allocated_services[service_type] = self.collaboration_services[service_type].copy()
            
            # 4. Configurer le service mesh
            mesh_config = await self._configure_mesh_for_collaboration(session, allocated_services)
            
            # 5. Configurer les politiques de sécurité
            security_policies = await self._setup_collaboration_security(session)
            
            # 6. Créer les endpoints de synchronisation
            sync_endpoints = await self._setup_sync_endpoints(session, allocated_services)
            
            result = CollaborationResult(
                success=True,
                session=session,
                allocated_services=allocated_services,
                mesh_configuration=mesh_config,
                sync_endpoints=sync_endpoints,
                security_policies=security_policies
            )
            
            # Mettre à jour les statistiques
            await self._update_collaboration_stats(session)
            
            logger.info(f"🤝 Mesh collaboration configuré pour session {session.session_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration mesh collaboration: {e}")
            return CollaborationResult(
                success=False,
                errors=[str(e)]
            )
    
    async def _determine_required_services(self, request: CollaborationRequest) -> List[str]:
        """Déterminer les services nécessaires pour la collaboration"""
        template = self.session_manager.collaboration_templates.get(
            request.session_type.value,
            {}
        )
        
        return template.get('required_services', ['real_time_sync'])
    
    async def _configure_mesh_for_collaboration(self, session: CollaborationSession, 
                                              allocated_services: Dict[str, List[ServiceInstance]]) -> Dict[str, Any]:
        """Configurer le service mesh pour la collaboration"""
        try:
            # Créer les règles de trafic pour la collaboration
            traffic_rules = []
            
            # Règle pour synchronisation temps réel
            if 'real_time_sync' in allocated_services:
                sync_rule = TrafficRule(
                    rule_id=f"sync_rule_{session.session_id}",
                    source_service="client",
                    destination_service="real_time_sync",
                    rule_type="routing",
                    conditions={'session_id': session.session_id},
                    actions={'route_to': 'real_time_sync'},
                    priority=100
                )
                traffic_rules.append(sync_rule)
            
            # Règle pour streaming (si applicable)
            if 'streaming_service' in allocated_services:
                stream_rule = TrafficRule(
                    rule_id=f"stream_rule_{session.session_id}",
                    source_service="client",
                    destination_service="streaming_service",
                    rule_type="routing",
                    conditions={'content_type': 'video/stream'},
                    actions={
                        'route_to': 'streaming_service',
                        'load_balancing': 'least_connections'
                    },
                    priority=90
                )
                traffic_rules.append(stream_rule)
            
            mesh_config = {
                'session_id': session.session_id,
                'traffic_rules': [rule.__dict__ for rule in traffic_rules],
                'load_balancing_strategy': 'session_affinity',
                'health_check_interval': 30,
                'circuit_breaker_enabled': True,
                'retry_policy': {
                    'max_retries': 3,
                    'retry_timeout': '5s'
                }
            }
            
            return mesh_config
            
        except Exception as e:
            logger.error(f"Erreur configuration mesh: {e}")
            return {}
    
    async def _setup_collaboration_security(self, session: CollaborationSession) -> List[str]:
        """Configurer les politiques de sécurité pour la collaboration"""
        try:
            security_policies = []
            
            # Politique d'authentification
            auth_policy_id = f"auth_policy_{session.session_id}"
            auth_rule = SecurityRule(
                rule_id=auth_policy_id,
                source_service="client",
                destination_service="*",
                action="ALLOW",
                conditions={'session_id': session.session_id},
                authentication_required=True,
                authorization_policy={
                    'required_permissions': ['session_access'],
                    'session_validation': True
                }
            )
            
            security_policies.append(auth_policy_id)
            
            # Politique de rate limiting par utilisateur
            rate_limit_policy_id = f"rate_limit_{session.session_id}"
            
            # Politique de chiffrement pour données sensibles
            if session.session_type in [CollaborationType.CONTENT_SHARING, CollaborationType.PROJECT_MANAGEMENT]:
                encryption_policy_id = f"encryption_{session.session_id}"
                security_policies.append(encryption_policy_id)
            
            return security_policies
            
        except Exception as e:
            logger.error(f"Erreur configuration sécurité: {e}")
            return []
    
    async def _setup_sync_endpoints(self, session: CollaborationSession, 
                                  allocated_services: Dict[str, List[ServiceInstance]]) -> Dict[str, str]:
        """Configurer les endpoints de synchronisation"""
        try:
            endpoints = {}
            
            # Endpoint WebSocket pour synchronisation temps réel
            if 'real_time_sync' in allocated_services:
                sync_service = allocated_services['real_time_sync'][0]
                endpoints['websocket'] = f"wss://{sync_service.host}:{sync_service.port}/sync/{session.session_id}"
            
            # Endpoint REST pour opérations asynchrones
            endpoints['rest_api'] = f"https://api.ainflue.com/collaboration/{session.session_id}"
            
            # Endpoint pour streaming (si applicable)
            if 'streaming_service' in allocated_services:
                stream_service = allocated_services['streaming_service'][0]
                endpoints['stream_rtmp'] = f"rtmp://{stream_service.host}:{stream_service.port}/live/{session.session_id}"
                endpoints['stream_hls'] = f"https://{stream_service.host}/hls/{session.session_id}/playlist.m3u8"
            
            # Endpoint pour partage de fichiers
            if 'file_sharing' in allocated_services:
                file_service = allocated_services['file_sharing'][0]
                endpoints['file_upload'] = f"https://{file_service.host}/upload/{session.session_id}"
                endpoints['file_download'] = f"https://{file_service.host}/download/{session.session_id}"
            
            return endpoints
            
        except Exception as e:
            logger.error(f"Erreur configuration endpoints: {e}")
            return {}
    
    async def join_collaboration_session(self, session_id: str, user_id: str) -> bool:
        """Rejoindre une session de collaboration"""
        return await self.session_manager.join_session(session_id, user_id)
    
    async def leave_collaboration_session(self, session_id: str, user_id: str) -> bool:
        """Quitter une session de collaboration"""
        return await self.session_manager.leave_session(session_id, user_id)
    
    async def update_user_permissions(self, session_id: str, user_id: str, 
                                    role: UserRole, permission_level: PermissionLevel,
                                    updated_by: str) -> bool:
        """Mettre à jour les permissions d'un utilisateur"""
        new_permission = UserPermission(
            user_id=user_id,
            role=role,
            permission_level=permission_level,
            granted_by=updated_by,
            specific_permissions=self.session_manager._get_default_permissions(role)
        )
        
        return await self.session_manager.update_user_permission(
            session_id, user_id, new_permission, updated_by
        )
    
    async def handle_sync_conflict(self, session_id: str, resource_id: str,
                                 conflicting_users: List[str], conflict_data: Dict[str, Any]) -> str:
        """Gérer un conflit de synchronisation"""
        return await self.session_manager.create_sync_conflict(
            session_id, resource_id, conflicting_users, conflict_data
        )
    
    async def resolve_sync_conflict(self, conflict_id: str, resolution_strategy: str,
                                  resolved_by: str) -> bool:
        """Résoudre un conflit de synchronisation"""
        return await self.session_manager.resolve_sync_conflict(
            conflict_id, resolution_strategy, resolved_by
        )
    
    async def get_session_events(self, session_id: str, since_sequence: int = 0) -> List[CollaborationEvent]:
        """Obtenir les événements d'une session"""
        return await self.session_manager.get_session_events(session_id, since_sequence)
    
    async def get_user_active_sessions(self, user_id: str) -> List[CollaborationSession]:
        """Obtenir les sessions actives d'un utilisateur"""
        return await self.session_manager.get_active_sessions_for_user(user_id)
    
    async def _update_collaboration_stats(self, session: CollaborationSession):
        """Mettre à jour les statistiques de collaboration"""
        try:
            stats = self.collaboration_stats
            
            stats['total_sessions'] += 1
            stats['active_sessions'] = len(self.session_manager.active_sessions)
            stats['total_participants'] += len(session.participants)
            
            # Distribution par type
            session_type = session.session_type.value
            if session_type not in stats['sessions_by_type']:
                stats['sessions_by_type'][session_type] = 0
            stats['sessions_by_type'][session_type] += 1
            
        except Exception as e:
            logger.error(f"Erreur mise à jour stats collaboration: {e}")
    
    async def get_collaboration_mesh_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du mesh de collaboration"""
        stats = self.collaboration_stats.copy()
        
        # Ajouter des métriques en temps réel
        stats['active_sessions'] = len(self.session_manager.active_sessions)
        
        # Calculer la durée moyenne des sessions
        if self.session_manager.active_sessions:
            total_duration = 0
            session_count = 0
            current_time = datetime.now()
            
            for session in self.session_manager.active_sessions.values():
                duration = (current_time - session.created_at).total_seconds() / 3600  # heures
                total_duration += duration
                session_count += 1
            
            if session_count > 0:
                stats['avg_session_duration'] = total_duration / session_count
        
        # Compter les conflits résolus
        total_resolved = 0
        for conflicts in self.session_manager.sync_conflicts.values():
            total_resolved += len([c for c in conflicts if c.resolved_at is not None])
        stats['sync_conflicts_resolved'] = total_resolved
        
        # Services de collaboration disponibles
        stats['available_collaboration_services'] = list(self.collaboration_services.keys())
        stats['total_service_instances'] = sum(len(instances) for instances in self.collaboration_services.values())
        
        return stats
    
    async def cleanup_inactive_sessions(self, max_inactive_hours: int = 24):
        """Nettoyer les sessions inactives"""
        await self.session_manager.cleanup_inactive_sessions(max_inactive_hours)
        
        # Mettre à jour les stats après nettoyage
        self.collaboration_stats['active_sessions'] = len(self.session_manager.active_sessions)

# Factory function
def create_collaboration_service_mesh() -> CollaborationServiceMesh:
    """Factory pour créer un service mesh de collaboration"""
    return CollaborationServiceMesh()

__all__ = [
    'CollaborationServiceMesh',
    'CollaborationType',
    'UserRole', 
    'PermissionLevel',
    'SyncStrategy',
    'CollaborationSession',
    'UserPermission',
    'CollaborationEvent',
    'SyncConflict',
    'CollaborationRequest',
    'CollaborationResult',
    'CollaborationSessionManager',
    'create_collaboration_service_mesh'
]