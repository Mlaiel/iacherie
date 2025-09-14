#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔐 Session Store Manager - Gestionnaire Stockage Sessions Enterprise
===================================================================

Gestionnaire enterprise de stockage sessions avec sécurité avancée,
persistance distribuée et gestion intelligente du cycle de vie.

**Rôles Experts:**
- **Backend Senior**: Architecture sessions haute performance distribuée
- **Sécurité**: Chiffrement sessions, validation tokens, protection CSRF
- **DBA**: Optimisation stockage, indexation, persistance sessions
- **Microservices**: Coordination sessions multi-services

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import json
import hashlib
import secrets
import uuid
from typing import Dict, Any, Optional, List, Union, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta, timezone
import yaml
from collections import defaultdict, deque
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes

# Optional Redis imports for enterprise environment
try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    # Fallback pour environnement sans Redis
    REDIS_AVAILABLE = False
    aioredis = None
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import jwt

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionState(Enum):
    """États de session"""
    ACTIVE = "active"
    EXPIRED = "expired"
    INVALIDATED = "invalidated"
    SUSPENDED = "suspended"
    PENDING = "pending"
    TERMINATED = "terminated"

class SessionType(Enum):
    """Types de session"""
    USER = "user"  # Session utilisateur
    API = "api"  # Session API
    ADMIN = "admin"  # Session administrateur
    GUEST = "guest"  # Session invité
    SERVICE = "service"  # Session service
    TEMPORARY = "temporary"  # Session temporaire

class SecurityLevel(Enum):
    """Niveaux de sécurité session"""
    LOW = "low"  # Basique
    MEDIUM = "medium"  # Standard
    HIGH = "high"  # Élevé
    CRITICAL = "critical"  # Critique

@dataclass
class SessionData:
    """Données de session"""
    session_id: str
    user_id: Optional[str]
    session_type: SessionType
    state: SessionState
    security_level: SecurityLevel
    created_at: datetime
    last_accessed: datetime
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Sécurité
    csrf_token: Optional[str] = None
    fingerprint: Optional[str] = None
    encrypted: bool = False
    
    # Métriques
    access_count: int = 0
    data_size_bytes: int = 0

@dataclass
class SessionMetrics:
    """Métriques sessions"""
    total_sessions: int = 0
    active_sessions: int = 0
    expired_sessions: int = 0
    total_users: int = 0
    average_session_duration: float = 0.0
    peak_concurrent_sessions: int = 0
    security_violations: int = 0
    session_hijack_attempts: int = 0

class SessionStoreManager:
    """
    🔐 Gestionnaire Stockage Sessions Enterprise
    
    **Backend Senior**: Architecture stockage sessions haute performance
    **Sécurité**: Chiffrement, validation, protection contre attaques
    **DBA**: Optimisation persistance et indexation sessions
    **Microservices**: Coordination sessions distribuées multi-services
    """
    
    def __init__(self, redis_pool, config: Optional[Dict[str, Any]] = None):
        self.redis_pool = redis_pool
        self.config = config or self._get_default_config()
        
        # Stockage sessions
        self.active_sessions: Dict[str, SessionData] = {}
        self.user_sessions: Dict[str, Set[str]] = defaultdict(set)  # user_id -> session_ids
        
        # Sécurité
        self.encryption_key = self._generate_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        self.jwt_secret = self.config.get('jwt_secret', secrets.token_urlsafe(32))
        
        # Métriques et monitoring
        self.metrics = SessionMetrics()
        self.session_history: deque = deque(maxlen=10000)
        self.security_events: deque = deque(maxlen=1000)
        
        # Configuration TTL par type
        self.session_ttl = {
            SessionType.USER: self.config.get('user_session_ttl', 3600),  # 1h
            SessionType.API: self.config.get('api_session_ttl', 7200),  # 2h
            SessionType.ADMIN: self.config.get('admin_session_ttl', 1800),  # 30min
            SessionType.GUEST: self.config.get('guest_session_ttl', 900),  # 15min
            SessionType.SERVICE: self.config.get('service_session_ttl', 86400),  # 24h
            SessionType.TEMPORARY: self.config.get('temp_session_ttl', 300)  # 5min
        }
        
        # Tâches background
        self.cleanup_task: Optional[asyncio.Task] = None
        self.metrics_task: Optional[asyncio.Task] = None
        
        logger.info("🔐 Session Store Manager initialisé")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """**DBA**: Configuration par défaut optimisée"""
        return {
            'max_sessions_per_user': 5,
            'session_cleanup_interval': 300,  # 5 minutes
            'enable_encryption': True,
            'enable_csrf_protection': True,
            'enable_fingerprinting': True,
            'security_monitoring': True,
            'user_session_ttl': 3600,
            'api_session_ttl': 7200,
            'admin_session_ttl': 1800,
            'guest_session_ttl': 900,
            'service_session_ttl': 86400,
            'temp_session_ttl': 300,
            'jwt_algorithm': 'HS256',
            'redis_key_prefix': 'session:',
            'redis_user_prefix': 'user_sessions:',
            'enable_distributed_sessions': True
        }
    
    def _generate_encryption_key(self) -> bytes:
        """**Sécurité**: Génération clé chiffrement sécurisée"""
        password = self.config.get('encryption_password', 'ainflue_sessions_key').encode()
        salt = self.config.get('encryption_salt', b'ainflue_salt_2025')
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    async def start_background_tasks(self):
        """**Backend Senior**: Démarrage tâches arrière-plan"""
        if self.cleanup_task is None or self.cleanup_task.done():
            self.cleanup_task = asyncio.create_task(self._session_cleanup_loop())
        
        if self.metrics_task is None or self.metrics_task.done():
            self.metrics_task = asyncio.create_task(self._metrics_collection_loop())
        
        logger.info("🚀 Tâches background sessions démarrées")
    
    async def stop_background_tasks(self):
        """**Backend Senior**: Arrêt tâches arrière-plan"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
        if self.metrics_task:
            self.metrics_task.cancel()
        
        logger.info("🛑 Tâches background sessions arrêtées")
    
    async def create_session(
        self,
        user_id: Optional[str] = None,
        session_type: SessionType = SessionType.USER,
        security_level: SecurityLevel = SecurityLevel.MEDIUM,
        ttl_override: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> SessionData:
        """**Backend Senior**: Création nouvelle session sécurisée"""
        
        # Génération ID session unique
        session_id = self._generate_session_id()
        current_time = datetime.now(timezone.utc)
        
        # Calcul TTL
        ttl = ttl_override or self.session_ttl.get(session_type, 3600)
        expires_at = current_time + timedelta(seconds=ttl)
        
        # Vérification limites utilisateur
        if user_id and not await self._check_user_session_limit(user_id):
            raise ValueError(f"Limite sessions dépassée pour utilisateur {user_id}")
        
        # Création données session
        session_data = SessionData(
            session_id=session_id,
            user_id=user_id,
            session_type=session_type,
            state=SessionState.ACTIVE,
            security_level=security_level,
            created_at=current_time,
            last_accessed=current_time,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            data=initial_data or {},
            csrf_token=self._generate_csrf_token() if self.config.get('enable_csrf_protection') else None,
            fingerprint=self._generate_fingerprint(ip_address, user_agent) if self.config.get('enable_fingerprinting') else None,
            encrypted=self.config.get('enable_encryption', True)
        )
        
        # Stockage session
        await self._store_session(session_data)
        
        # Enregistrement métriques
        self.metrics.total_sessions += 1
        self.metrics.active_sessions += 1
        if user_id:
            self.user_sessions[user_id].add(session_id)
        
        # Historique
        self.session_history.append({
            'action': 'create',
            'session_id': session_id,
            'user_id': user_id,
            'type': session_type.value,
            'timestamp': current_time.timestamp()
        })
        
        logger.info(f"✅ Session créée: {session_id} (user: {user_id}, type: {session_type.value})")
        return session_data
    
    def _generate_session_id(self) -> str:
        """**Sécurité**: Génération ID session sécurisé"""
        # Combinaison UUID + timestamp + random pour unicité garantie
        timestamp = str(int(time.time() * 1000000))  # microseconds
        random_part = secrets.token_urlsafe(16)
        unique_part = str(uuid.uuid4().hex[:8])
        
        session_id = f"{timestamp}_{unique_part}_{random_part}"
        return hashlib.sha256(session_id.encode()).hexdigest()[:32]
    
    def _generate_csrf_token(self) -> str:
        """**Sécurité**: Génération token CSRF"""
        return secrets.token_urlsafe(32)
    
    def _generate_fingerprint(self, ip_address: Optional[str], user_agent: Optional[str]) -> str:
        """**Sécurité**: Génération empreinte session"""
        fingerprint_data = f"{ip_address or 'unknown'}:{user_agent or 'unknown'}:{time.time()}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
    
    async def _check_user_session_limit(self, user_id: str) -> bool:
        """**Backend Senior**: Vérification limite sessions utilisateur"""
        max_sessions = self.config.get('max_sessions_per_user', 5)
        current_sessions = len(self.user_sessions.get(user_id, set()))
        
        if current_sessions >= max_sessions:
            # Nettoyage sessions expirées
            await self._cleanup_user_expired_sessions(user_id)
            current_sessions = len(self.user_sessions.get(user_id, set()))
        
        return current_sessions < max_sessions
    
    async def _cleanup_user_expired_sessions(self, user_id: str):
        """**DBA**: Nettoyage sessions expirées utilisateur"""
        if user_id not in self.user_sessions:
            return
        
        current_time = datetime.now(timezone.utc)
        expired_sessions = []
        
        for session_id in list(self.user_sessions[user_id]):
            session = await self.get_session(session_id)
            if session and (session.expires_at <= current_time or session.state != SessionState.ACTIVE):
                expired_sessions.append(session_id)
        
        # Suppression sessions expirées
        for session_id in expired_sessions:
            await self.delete_session(session_id)
    
    async def _store_session(self, session_data: SessionData):
        """**DBA**: Stockage session avec optimisation"""
        
        # Sérialisation données
        session_dict = asdict(session_data)
        
        # Conversion datetime pour JSON
        session_dict['created_at'] = session_data.created_at.isoformat()
        session_dict['last_accessed'] = session_data.last_accessed.isoformat()
        session_dict['expires_at'] = session_data.expires_at.isoformat()
        session_dict['session_type'] = session_data.session_type.value
        session_dict['state'] = session_data.state.value
        session_dict['security_level'] = session_data.security_level.value
        
        # Chiffrement si activé
        if session_data.encrypted and self.config.get('enable_encryption'):
            sensitive_data = json.dumps({
                'data': session_data.data,
                'metadata': session_data.metadata
            })
            session_dict['encrypted_data'] = self.fernet.encrypt(sensitive_data.encode()).decode()
            session_dict['data'] = {}
            session_dict['metadata'] = {}
        
        session_json = json.dumps(session_dict)
        session_data.data_size_bytes = len(session_json.encode())
        
        # Stockage Redis
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                redis_key = f"{self.config['redis_key_prefix']}{session_data.session_id}"
                ttl = int((session_data.expires_at - datetime.now(timezone.utc)).total_seconds())
                
                await redis_conn.setex(redis_key, ttl, session_json)
                
                # Index utilisateur si applicable
                if session_data.user_id:
                    user_key = f"{self.config['redis_user_prefix']}{session_data.user_id}"
                    await redis_conn.sadd(user_key, session_data.session_id)
                    await redis_conn.expire(user_key, ttl)
                
                # Cache local
                self.active_sessions[session_data.session_id] = session_data
                
        except Exception as e:
            logger.error(f"❌ Erreur stockage session {session_data.session_id}: {e}")
            raise
    
    async def get_session(
        self, 
        session_id: str, 
        validate_security: bool = True,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[SessionData]:
        """**Backend Senior**: Récupération session avec validation sécurité"""
        
        try:
            # Vérification cache local d'abord
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                
                # Vérification expiration
                if session.expires_at <= datetime.now(timezone.utc):
                    await self.delete_session(session_id)
                    return None
                
                # Validation sécurité si demandée
                if validate_security and not await self._validate_session_security(session, ip_address, user_agent):
                    await self._handle_security_violation(session, "Security validation failed")
                    return None
                
                # Mise à jour dernier accès
                await self._update_last_access(session)
                return session
            
            # Récupération depuis Redis
            async with self.redis_pool.get_connection() as redis_conn:
                redis_key = f"{self.config['redis_key_prefix']}{session_id}"
                session_json = await redis_conn.get(redis_key)
                
                if not session_json:
                    return None
                
                # Désérialisation
                session_dict = json.loads(session_json)
                session = await self._deserialize_session(session_dict)
                
                # Validation et retour
                if validate_security and not await self._validate_session_security(session, ip_address, user_agent):
                    await self._handle_security_violation(session, "Security validation failed")
                    return None
                
                # Cache local et mise à jour accès
                self.active_sessions[session_id] = session
                await self._update_last_access(session)
                
                return session
                
        except Exception as e:
            logger.error(f"❌ Erreur récupération session {session_id}: {e}")
            return None
    
    async def _deserialize_session(self, session_dict: Dict[str, Any]) -> SessionData:
        """**Backend Senior**: Désérialisation session"""
        
        # Déchiffrement si nécessaire
        if 'encrypted_data' in session_dict and session_dict['encrypted_data']:
            try:
                decrypted = self.fernet.decrypt(session_dict['encrypted_data'].encode())
                sensitive_data = json.loads(decrypted.decode())
                session_dict['data'] = sensitive_data.get('data', {})
                session_dict['metadata'] = sensitive_data.get('metadata', {})
            except Exception as e:
                logger.error(f"❌ Erreur déchiffrement session: {e}")
                session_dict['data'] = {}
                session_dict['metadata'] = {}
        
        # Conversion datetime
        session_dict['created_at'] = datetime.fromisoformat(session_dict['created_at'])
        session_dict['last_accessed'] = datetime.fromisoformat(session_dict['last_accessed'])
        session_dict['expires_at'] = datetime.fromisoformat(session_dict['expires_at'])
        session_dict['session_type'] = SessionType(session_dict['session_type'])
        session_dict['state'] = SessionState(session_dict['state'])
        session_dict['security_level'] = SecurityLevel(session_dict['security_level'])
        
        return SessionData(**session_dict)
    
    async def _validate_session_security(
        self, 
        session: SessionData, 
        ip_address: Optional[str], 
        user_agent: Optional[str]
    ) -> bool:
        """**Sécurité**: Validation sécurité session"""
        
        # Validation état
        if session.state != SessionState.ACTIVE:
            return False
        
        # Validation expiration
        if session.expires_at <= datetime.now(timezone.utc):
            return False
        
        # Validation empreinte si configurée
        if (self.config.get('enable_fingerprinting') and 
            session.fingerprint and 
            ip_address and user_agent):
            
            current_fingerprint = self._generate_fingerprint(ip_address, user_agent)
            # Comparaison partielle pour tolérer certains changements
            if not self._compare_fingerprints(session.fingerprint, current_fingerprint):
                return False
        
        # Validation IP pour sessions critiques
        if (session.security_level == SecurityLevel.CRITICAL and 
            session.ip_address and 
            ip_address and 
            session.ip_address != ip_address):
            return False
        
        return True
    
    def _compare_fingerprints(self, stored: str, current: str) -> bool:
        """**Sécurité**: Comparaison empreintes avec tolérance"""
        # Comparaison exacte pour démo - en production, implémenter logique plus sophistiquée
        return stored == current
    
    async def _handle_security_violation(self, session: SessionData, reason: str):
        """**Sécurité**: Gestion violation sécurité"""
        
        # Enregistrement événement sécurité
        self.security_events.append({
            'timestamp': time.time(),
            'session_id': session.session_id,
            'user_id': session.user_id,
            'violation_type': 'session_security',
            'reason': reason,
            'ip_address': session.ip_address
        })
        
        self.metrics.security_violations += 1
        
        # Actions selon niveau sécurité
        if session.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            # Invalidation immédiate pour sessions critiques
            await self.invalidate_session(session.session_id, reason="Security violation")
        
        logger.warning(f"🚨 Violation sécurité session {session.session_id}: {reason}")
    
    async def _update_last_access(self, session: SessionData):
        """**DBA**: Mise à jour dernier accès optimisée"""
        current_time = datetime.now(timezone.utc)
        session.last_accessed = current_time
        session.access_count += 1
        
        # Mise à jour Redis périodique (pas à chaque accès pour performance)
        time_since_update = (current_time - session.last_accessed).total_seconds()
        if time_since_update > 60:  # Mise à jour max 1x par minute
            await self._store_session(session)
    
    async def update_session_data(
        self, 
        session_id: str, 
        data_updates: Dict[str, Any],
        metadata_updates: Optional[Dict[str, Any]] = None
    ) -> bool:
        """**Backend Senior**: Mise à jour données session"""
        
        session = await self.get_session(session_id)
        if not session:
            return False
        
        try:
            # Mise à jour données
            session.data.update(data_updates)
            
            if metadata_updates:
                session.metadata.update(metadata_updates)
            
            # Stockage mis à jour
            await self._store_session(session)
            
            logger.debug(f"📝 Session mise à jour: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour session {session_id}: {e}")
            return False
    
    async def extend_session(self, session_id: str, additional_seconds: int) -> bool:
        """**Backend Senior**: Extension durée session"""
        
        session = await self.get_session(session_id)
        if not session or session.state != SessionState.ACTIVE:
            return False
        
        try:
            # Extension expiration
            session.expires_at += timedelta(seconds=additional_seconds)
            
            # Mise à jour stockage
            await self._store_session(session)
            
            logger.info(f"⏱️ Session étendue: {session_id} (+{additional_seconds}s)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur extension session {session_id}: {e}")
            return False
    
    async def invalidate_session(self, session_id: str, reason: str = "Manual invalidation") -> bool:
        """**Sécurité**: Invalidation session sécurisée"""
        
        session = await self.get_session(session_id, validate_security=False)
        if not session:
            return False
        
        try:
            # Changement état
            session.state = SessionState.INVALIDATED
            session.metadata['invalidation_reason'] = reason
            session.metadata['invalidated_at'] = datetime.now(timezone.utc).isoformat()
            
            # Suppression effective
            await self.delete_session(session_id)
            
            # Historique
            self.session_history.append({
                'action': 'invalidate',
                'session_id': session_id,
                'user_id': session.user_id,
                'reason': reason,
                'timestamp': time.time()
            })
            
            logger.info(f"🚫 Session invalidée: {session_id} - {reason}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur invalidation session {session_id}: {e}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """**DBA**: Suppression session complète"""
        
        try:
            # Récupération pour nettoyage index utilisateur
            session = self.active_sessions.get(session_id)
            
            async with self.redis_pool.get_connection() as redis_conn:
                # Suppression Redis
                redis_key = f"{self.config['redis_key_prefix']}{session_id}"
                deleted = await redis_conn.delete(redis_key)
                
                # Nettoyage index utilisateur
                if session and session.user_id:
                    user_key = f"{self.config['redis_user_prefix']}{session.user_id}"
                    await redis_conn.srem(user_key, session_id)
                    self.user_sessions[session.user_id].discard(session_id)
                
                # Suppression cache local
                self.active_sessions.pop(session_id, None)
                
                # Mise à jour métriques
                if session and session.state == SessionState.ACTIVE:
                    self.metrics.active_sessions = max(0, self.metrics.active_sessions - 1)
                
                return bool(deleted)
                
        except Exception as e:
            logger.error(f"❌ Erreur suppression session {session_id}: {e}")
            return False
    
    async def get_user_sessions(self, user_id: str) -> List[SessionData]:
        """**Backend Senior**: Récupération sessions utilisateur"""
        
        sessions = []
        
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                user_key = f"{self.config['redis_user_prefix']}{user_id}"
                session_ids = await redis_conn.smembers(user_key)
                
                for session_id in session_ids:
                    session = await self.get_session(session_id, validate_security=False)
                    if session:
                        sessions.append(session)
                
                return sessions
                
        except Exception as e:
            logger.error(f"❌ Erreur récupération sessions utilisateur {user_id}: {e}")
            return []
    
    async def invalidate_user_sessions(
        self, 
        user_id: str, 
        exclude_session_id: Optional[str] = None,
        reason: str = "User sessions invalidation"
    ) -> int:
        """**Sécurité**: Invalidation toutes sessions utilisateur"""
        
        user_sessions = await self.get_user_sessions(user_id)
        invalidated_count = 0
        
        for session in user_sessions:
            if exclude_session_id and session.session_id == exclude_session_id:
                continue
            
            if await self.invalidate_session(session.session_id, reason):
                invalidated_count += 1
        
        logger.info(f"🚫 {invalidated_count} sessions invalidées pour utilisateur {user_id}")
        return invalidated_count
    
    async def _session_cleanup_loop(self):
        """**DBA**: Boucle nettoyage sessions expirées"""
        while True:
            try:
                await self._cleanup_expired_sessions()
                interval = self.config.get('session_cleanup_interval', 300)
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"❌ Erreur nettoyage sessions: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_expired_sessions(self):
        """**DBA**: Nettoyage sessions expirées"""
        current_time = datetime.now(timezone.utc)
        expired_sessions = []
        
        # Identification sessions expirées dans cache local
        for session_id, session in list(self.active_sessions.items()):
            if session.expires_at <= current_time or session.state != SessionState.ACTIVE:
                expired_sessions.append(session_id)
        
        # Suppression sessions expirées
        cleanup_count = 0
        for session_id in expired_sessions:
            if await self.delete_session(session_id):
                cleanup_count += 1
        
        if cleanup_count > 0:
            logger.info(f"🧹 {cleanup_count} sessions expirées nettoyées")
            self.metrics.expired_sessions += cleanup_count
    
    async def _metrics_collection_loop(self):
        """**DevOps**: Boucle collecte métriques"""
        while True:
            try:
                await self._collect_metrics()
                await asyncio.sleep(60)  # Collecte chaque minute
            except Exception as e:
                logger.error(f"❌ Erreur collecte métriques sessions: {e}")
                await asyncio.sleep(60)
    
    async def _collect_metrics(self):
        """**DevOps**: Collecte métriques détaillées"""
        
        # Comptage sessions actives
        active_count = len([s for s in self.active_sessions.values() if s.state == SessionState.ACTIVE])
        self.metrics.active_sessions = active_count
        
        # Pic concurrent
        self.metrics.peak_concurrent_sessions = max(self.metrics.peak_concurrent_sessions, active_count)
        
        # Utilisateurs uniques
        unique_users = len(set(s.user_id for s in self.active_sessions.values() if s.user_id))
        self.metrics.total_users = unique_users
        
        # Durée moyenne session
        if self.session_history:
            durations = []
            for record in list(self.session_history)[-100:]:  # 100 dernières
                if record.get('action') == 'create':
                    # Calcul approximatif durée
                    durations.append(self.session_ttl.get(SessionType.USER, 3600))
            
            if durations:
                self.metrics.average_session_duration = sum(durations) / len(durations)
    
    async def generate_jwt_token(self, session: SessionData) -> str:
        """**Sécurité**: Génération token JWT pour session"""
        
        payload = {
            'session_id': session.session_id,
            'user_id': session.user_id,
            'type': session.session_type.value,
            'exp': int(session.expires_at.timestamp()),
            'iat': int(session.created_at.timestamp()),
            'csrf': session.csrf_token
        }
        
        token = jwt.encode(
            payload, 
            self.jwt_secret, 
            algorithm=self.config.get('jwt_algorithm', 'HS256')
        )
        
        return token
    
    async def validate_jwt_token(self, token: str) -> Optional[SessionData]:
        """**Sécurité**: Validation token JWT"""
        
        try:
            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=[self.config.get('jwt_algorithm', 'HS256')]
            )
            
            session_id = payload.get('session_id')
            if not session_id:
                return None
            
            session = await self.get_session(session_id)
            
            # Validation CSRF si présent
            if session and session.csrf_token and payload.get('csrf') != session.csrf_token:
                return None
            
            return session
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"⚠️ Token JWT invalide: {e}")
            return None
    
    async def get_session_analytics(self) -> Dict[str, Any]:
        """**DevOps**: Analytics détaillées sessions"""
        
        # Distribution par type
        type_distribution = defaultdict(int)
        state_distribution = defaultdict(int)
        security_distribution = defaultdict(int)
        
        for session in self.active_sessions.values():
            type_distribution[session.session_type.value] += 1
            state_distribution[session.state.value] += 1
            security_distribution[session.security_level.value] += 1
        
        # Sessions par utilisateur
        sessions_per_user = {
            user_id: len(session_ids) 
            for user_id, session_ids in self.user_sessions.items()
            if session_ids
        }
        
        return {
            'global_metrics': {
                'total_sessions': self.metrics.total_sessions,
                'active_sessions': self.metrics.active_sessions,
                'expired_sessions': self.metrics.expired_sessions,
                'total_users': self.metrics.total_users,
                'average_session_duration': self.metrics.average_session_duration,
                'peak_concurrent_sessions': self.metrics.peak_concurrent_sessions,
                'security_violations': self.metrics.security_violations
            },
            'distributions': {
                'by_type': dict(type_distribution),
                'by_state': dict(state_distribution),
                'by_security_level': dict(security_distribution)
            },
            'user_statistics': {
                'total_users_with_sessions': len(sessions_per_user),
                'average_sessions_per_user': sum(sessions_per_user.values()) / max(1, len(sessions_per_user)),
                'max_sessions_per_user': max(sessions_per_user.values()) if sessions_per_user else 0
            },
            'security_events': list(self.security_events)[-20:],  # 20 derniers
            'recent_history': list(self.session_history)[-20:],
            'configuration': {
                'encryption_enabled': self.config.get('enable_encryption'),
                'csrf_protection': self.config.get('enable_csrf_protection'),
                'fingerprinting': self.config.get('enable_fingerprinting'),
                'max_sessions_per_user': self.config.get('max_sessions_per_user'),
                'session_ttl': dict(self.session_ttl)
            }
        }

# Factory function
async def create_session_store_manager(redis_pool, config: Optional[Dict[str, Any]] = None):
    """**Backend Senior**: Factory création gestionnaire sessions"""
    manager = SessionStoreManager(redis_pool, config)
    await manager.start_background_tasks()
    return manager

if __name__ == "__main__":
    async def demo():
        """Démonstration Session Store Manager"""
        
        # Configuration Redis simulée
        class MockRedisPool:
            def get_connection(self):
                from unittest.mock import AsyncMock
                mock = AsyncMock()
                mock.setex.return_value = True
                mock.get.return_value = None
                mock.delete.return_value = 1
                mock.sadd.return_value = 1
                mock.srem.return_value = 1
                mock.smembers.return_value = set()
                return mock
        
        # Création manager
        manager = await create_session_store_manager(MockRedisPool())
        
        # Création session
        session = await manager.create_session(
            user_id="user123",
            session_type=SessionType.USER,
            security_level=SecurityLevel.HIGH,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0..."
        )
        
        print(f"Session créée: {session.session_id}")
        
        # Génération JWT
        jwt_token = await manager.generate_jwt_token(session)
        print(f"JWT généré: {jwt_token[:50]}...")
        
        # Analytics
        analytics = await manager.get_session_analytics()
        print(f"Analytics sessions: {analytics}")
        
        # Nettoyage
        await manager.stop_background_tasks()
    
    asyncio.run(demo())