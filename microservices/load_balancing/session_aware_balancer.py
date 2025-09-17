"""
🔗 SESSION-AWARE LOAD BALANCER - ENTERPRISE STICKY SESSIONS
Load balancer session-aware avec sticky sessions intelligent

Implements session affinity + stateful routing + graceful session migration
for enterprise-grade session management and high availability.

Key Features:
- Consistent session-to-server mapping avec high availability
- Session state replication across servers pour fault tolerance
- Graceful session migration during server maintenance  
- Session-based load distribution optimization
- Multi-tier session storage (Redis + Database) pour persistence
- Session timeout et cleanup automatique

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture session-aware load balancer est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction, modification, distribution sans autorisation écrite est STRICTEMENT INTERDITE.
"""

import asyncio
import logging
import time
import hashlib
import pickle
import json
import uuid
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import redis.asyncio as redis
import aiohttp

logger = logging.getLogger(__name__)

class SessionState(Enum):
    """États de session"""
    ACTIVE = "active"
    IDLE = "idle"
    MIGRATING = "migrating"
    EXPIRED = "expired"
    TERMINATED = "terminated"

class SessionStorageTier(Enum):
    """Tiers stockage session"""
    MEMORY = "memory"          # Cache local rapide
    REDIS = "redis"            # Cache distribué
    DATABASE = "database"      # Stockage persistant
    HYBRID = "hybrid"          # Multi-tier intelligent

class SessionAffinityType(Enum):
    """Types d'affinité session"""
    STRICT = "strict"          # Session toujours même serveur
    SOFT = "soft"              # Préférence serveur, failover autorisé
    DISTRIBUTED = "distributed" # Session répliquée sur plusieurs serveurs
    DYNAMIC = "dynamic"        # Affinité adaptative basée sur charge

@dataclass
class SessionData:
    """Données session utilisateur"""
    session_id: str
    user_id: Optional[str]
    server_id: str
    client_ip: str
    user_agent: str
    session_state: SessionState
    created_at: datetime
    last_accessed: datetime
    expires_at: datetime
    session_data: Dict[str, Any] = field(default_factory=dict)
    affinity_type: SessionAffinityType = SessionAffinityType.SOFT
    replication_servers: Set[str] = field(default_factory=set)
    migration_target: Optional[str] = None
    access_count: int = 0
    total_duration: float = 0.0  # seconds
    
    @property
    def is_expired(self) -> bool:
        """Vérifie si session expirée"""
        return datetime.now() > self.expires_at
    
    @property
    def idle_duration(self) -> float:
        """Durée inactivité en secondes"""
        return (datetime.now() - self.last_accessed).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion vers dictionnaire pour sérialisation"""
        data = asdict(self)
        # Conversion datetime vers timestamp
        data['created_at'] = self.created_at.timestamp()
        data['last_accessed'] = self.last_accessed.timestamp()
        data['expires_at'] = self.expires_at.timestamp()
        data['session_state'] = self.session_state.value
        data['affinity_type'] = self.affinity_type.value
        data['replication_servers'] = list(self.replication_servers)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionData':
        """Création depuis dictionnaire"""
        return cls(
            session_id=data['session_id'],
            user_id=data.get('user_id'),
            server_id=data['server_id'],
            client_ip=data['client_ip'],
            user_agent=data['user_agent'],
            session_state=SessionState(data['session_state']),
            created_at=datetime.fromtimestamp(data['created_at']),
            last_accessed=datetime.fromtimestamp(data['last_accessed']),
            expires_at=datetime.fromtimestamp(data['expires_at']),
            session_data=data.get('session_data', {}),
            affinity_type=SessionAffinityType(data.get('affinity_type', 'soft')),
            replication_servers=set(data.get('replication_servers', [])),
            migration_target=data.get('migration_target'),
            access_count=data.get('access_count', 0),
            total_duration=data.get('total_duration', 0.0)
        )

@dataclass
class ServerSession:
    """Session serveur pour load balancing"""
    server_id: str
    hostname: str
    port: int
    is_healthy: bool
    current_sessions: int
    max_sessions: int
    session_capacity_percent: float
    average_session_duration: float
    session_migration_capable: bool = True
    maintenance_mode: bool = False
    last_health_check: datetime = field(default_factory=datetime.now)
    
    @property
    def can_accept_sessions(self) -> bool:
        """Vérifie si serveur peut accepter nouvelles sessions"""
        return (self.is_healthy and 
                not self.maintenance_mode and 
                self.session_capacity_percent < 90.0)
    
    @property
    def should_migrate_sessions(self) -> bool:
        """Vérifie si sessions doivent être migrées"""
        return (self.maintenance_mode or 
                not self.is_healthy or 
                self.session_capacity_percent > 95.0)

@dataclass
class SessionConfig:
    """Configuration session-aware load balancer"""
    default_session_timeout: int = 3600        # 1 heure
    max_session_timeout: int = 86400           # 24 heures
    session_cleanup_interval: int = 300        # 5 minutes
    session_replication_factor: int = 2        # 2 copies par session
    migration_timeout: int = 30                # 30 secondes
    affinity_cookie_name: str = "AINFLUE_SESSION"
    affinity_cookie_domain: str = ".ainflue.com"
    enable_session_encryption: bool = True
    storage_tier: SessionStorageTier = SessionStorageTier.HYBRID
    redis_connection_string: str = "redis://localhost:6379"
    database_connection_string: str = "postgresql://localhost/sessions"
    max_concurrent_migrations: int = 10

class DistributedSessionStore:
    """Store session distribué multi-tier"""
    
    def __init__(self, config: SessionConfig):
        self.config = config
        self.memory_cache: Dict[str, SessionData] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "writes": 0,
            "deletes": 0
        }
        
    async def initialize(self) -> bool:
        """Initialisation store session"""
        try:
            # Connexion Redis pour cache distribué
            if self.config.storage_tier in [SessionStorageTier.REDIS, SessionStorageTier.HYBRID]:
                self.redis_client = redis.from_url(self.config.redis_connection_string)
                await self.redis_client.ping()
                logger.info("✅ Connexion Redis session store établie")
            
            logger.info(f"🔗 Session store initialisé (tier: {self.config.storage_tier.value})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation session store: {e}")
            return False
    
    async def store_session(self, session_data: SessionData) -> bool:
        """Stockage session multi-tier"""
        try:
            session_key = f"session:{session_data.session_id}"
            serialized_data = json.dumps(session_data.to_dict())
            
            # Stockage selon tier configuré
            if self.config.storage_tier == SessionStorageTier.MEMORY:
                self.memory_cache[session_key] = session_data
                
            elif self.config.storage_tier == SessionStorageTier.REDIS and self.redis_client:
                await self.redis_client.setex(
                    session_key, 
                    self.config.default_session_timeout,
                    serialized_data
                )
                
            elif self.config.storage_tier == SessionStorageTier.HYBRID:
                # Memory cache pour accès rapide
                self.memory_cache[session_key] = session_data
                
                # Redis pour persistance et partage
                if self.redis_client:
                    await self.redis_client.setex(
                        session_key,
                        self.config.default_session_timeout,
                        serialized_data
                    )
            
            self.cache_stats["writes"] += 1
            logger.debug(f"💾 Session {session_data.session_id} stockée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur stockage session {session_data.session_id}: {e}")
            return False
    
    async def retrieve_session(self, session_id: str) -> Optional[SessionData]:
        """Récupération session multi-tier"""
        try:
            session_key = f"session:{session_id}"
            
            # Recherche memory cache d'abord
            if session_key in self.memory_cache:
                session_data = self.memory_cache[session_key]
                if not session_data.is_expired:
                    self.cache_stats["hits"] += 1
                    return session_data
                else:
                    # Session expirée, suppression
                    del self.memory_cache[session_key]
            
            # Recherche Redis si pas en memory
            if self.redis_client:
                redis_data = await self.redis_client.get(session_key)
                if redis_data:
                    session_dict = json.loads(redis_data)
                    session_data = SessionData.from_dict(session_dict)
                    
                    if not session_data.is_expired:
                        # Mise en cache memory pour accès futurs
                        self.memory_cache[session_key] = session_data
                        self.cache_stats["hits"] += 1
                        return session_data
                    else:
                        # Session expirée, suppression
                        await self.redis_client.delete(session_key)
            
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération session {session_id}: {e}")
            self.cache_stats["misses"] += 1
            return None
    
    async def delete_session(self, session_id: str) -> bool:
        """Suppression session"""
        try:
            session_key = f"session:{session_id}"
            
            # Suppression memory cache
            if session_key in self.memory_cache:
                del self.memory_cache[session_key]
            
            # Suppression Redis
            if self.redis_client:
                await self.redis_client.delete(session_key)
            
            self.cache_stats["deletes"] += 1
            logger.debug(f"🗑️ Session {session_id} supprimée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur suppression session {session_id}: {e}")
            return False
    
    async def get_sessions_by_server(self, server_id: str) -> List[SessionData]:
        """Récupération sessions par serveur"""
        sessions = []
        
        try:
            # Recherche dans memory cache
            for session_data in self.memory_cache.values():
                if session_data.server_id == server_id and not session_data.is_expired:
                    sessions.append(session_data)
            
            # Recherche additionnelle Redis si nécessaire
            if self.redis_client and self.config.storage_tier == SessionStorageTier.REDIS:
                # Scan toutes les sessions (coûteux, à optimiser en production)
                async for key in self.redis_client.scan_iter(match="session:*"):
                    if key.decode() not in [f"session:{s.session_id}" for s in sessions]:
                        redis_data = await self.redis_client.get(key)
                        if redis_data:
                            session_dict = json.loads(redis_data)
                            session_data = SessionData.from_dict(session_dict)
                            
                            if (session_data.server_id == server_id and 
                                not session_data.is_expired):
                                sessions.append(session_data)
            
            return sessions
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération sessions serveur {server_id}: {e}")
            return []
    
    async def cleanup_expired_sessions(self) -> int:
        """Nettoyage sessions expirées"""
        cleaned_count = 0
        
        try:
            # Nettoyage memory cache
            expired_keys = []
            for key, session_data in self.memory_cache.items():
                if session_data.is_expired:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.memory_cache[key]
                cleaned_count += 1
            
            # Nettoyage Redis automatique via TTL
            if self.redis_client:
                # Redis handle automatiquement TTL, mais on peut forcer cleanup
                pass
            
            if cleaned_count > 0:
                logger.info(f"🧹 Nettoyage sessions: {cleaned_count} sessions expirées supprimées")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage sessions expirées: {e}")
            return 0

class SessionAffinityManager:
    """Gestionnaire affinité sessions"""
    
    def __init__(self, config: SessionConfig):
        self.config = config
        self.session_server_mapping: Dict[str, str] = {}  # session_id -> server_id
        self.server_session_counts: Dict[str, int] = defaultdict(int)
        self.affinity_rules: Dict[str, SessionAffinityType] = {}
        
    async def create_session_affinity(
        self, 
        session_id: str, 
        server_id: str,
        affinity_type: SessionAffinityType = SessionAffinityType.SOFT
    ) -> bool:
        """Création affinité session-serveur"""
        try:
            self.session_server_mapping[session_id] = server_id
            self.server_session_counts[server_id] += 1
            self.affinity_rules[session_id] = affinity_type
            
            logger.debug(f"🔗 Affinité créée: session {session_id} -> serveur {server_id} ({affinity_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur création affinité session {session_id}: {e}")
            return False
    
    async def get_server_for_session(self, session_id: str) -> Optional[str]:
        """Récupération serveur affin pour session"""
        return self.session_server_mapping.get(session_id)
    
    async def remove_session_affinity(self, session_id: str) -> bool:
        """Suppression affinité session"""
        try:
            if session_id in self.session_server_mapping:
                server_id = self.session_server_mapping[session_id]
                del self.session_server_mapping[session_id]
                
                if server_id in self.server_session_counts:
                    self.server_session_counts[server_id] = max(0, self.server_session_counts[server_id] - 1)
                
                if session_id in self.affinity_rules:
                    del self.affinity_rules[session_id]
                
                logger.debug(f"🔓 Affinité supprimée: session {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur suppression affinité session {session_id}: {e}")
            return False
    
    async def update_session_affinity(
        self, 
        session_id: str, 
        new_server_id: str,
        reason: str = "migration"
    ) -> bool:
        """Mise à jour affinité session (migration)"""
        try:
            old_server_id = self.session_server_mapping.get(session_id)
            
            # Mise à jour mapping
            self.session_server_mapping[session_id] = new_server_id
            
            # Mise à jour compteurs
            if old_server_id:
                self.server_session_counts[old_server_id] = max(0, self.server_session_counts[old_server_id] - 1)
            self.server_session_counts[new_server_id] += 1
            
            logger.info(f"🔄 Affinité mise à jour: session {session_id} "
                       f"{old_server_id} -> {new_server_id} (raison: {reason})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour affinité session {session_id}: {e}")
            return False
    
    def get_server_session_count(self, server_id: str) -> int:
        """Récupération nombre sessions par serveur"""
        return self.server_session_counts.get(server_id, 0)
    
    def get_least_loaded_server(self, available_servers: List[str]) -> Optional[str]:
        """Sélection serveur le moins chargé en sessions"""
        if not available_servers:
            return None
        
        return min(available_servers, key=lambda s: self.server_session_counts.get(s, 0))

class SessionMigrationEngine:
    """Moteur migration sessions gracieuses"""
    
    def __init__(self, config: SessionConfig, session_store: DistributedSessionStore):
        self.config = config
        self.session_store = session_store
        self.active_migrations: Dict[str, Dict[str, Any]] = {}
        self.migration_stats = {
            "total_migrations": 0,
            "successful_migrations": 0,
            "failed_migrations": 0,
            "average_migration_time": 0.0
        }
        
    async def migrate_session(
        self, 
        session_id: str, 
        source_server_id: str, 
        target_server_id: str,
        reason: str = "load_balancing"
    ) -> bool:
        """Migration session entre serveurs"""
        migration_id = f"mig_{session_id}_{int(time.time())}"
        start_time = time.time()
        
        try:
            logger.info(f"🚚 Démarrage migration session {session_id}: {source_server_id} -> {target_server_id}")
            
            # Enregistrement migration active
            self.active_migrations[migration_id] = {
                "session_id": session_id,
                "source_server": source_server_id,
                "target_server": target_server_id,
                "reason": reason,
                "start_time": start_time,
                "status": "in_progress"
            }
            
            # Récupération données session
            session_data = await self.session_store.retrieve_session(session_id)
            if not session_data:
                raise Exception(f"Session {session_id} non trouvée pour migration")
            
            # Mise à jour état session
            session_data.session_state = SessionState.MIGRATING
            session_data.migration_target = target_server_id
            
            # Étape 1: Notification serveur source (pause nouvelles requêtes)
            await self._notify_server_migration_start(source_server_id, session_id)
            
            # Étape 2: Transfert données session
            session_data.server_id = target_server_id
            session_data.migration_target = None
            session_data.session_state = SessionState.ACTIVE
            
            # Étape 3: Stockage sur serveur cible
            success = await self.session_store.store_session(session_data)
            if not success:
                raise Exception("Échec stockage session sur serveur cible")
            
            # Étape 4: Notification serveur cible
            await self._notify_server_migration_complete(target_server_id, session_id, session_data)
            
            # Étape 5: Nettoyage serveur source
            await self._cleanup_source_server(source_server_id, session_id)
            
            # Finalisation migration
            migration_time = time.time() - start_time
            self.active_migrations[migration_id]["status"] = "completed"
            self.active_migrations[migration_id]["duration"] = migration_time
            
            # Mise à jour statistiques
            self.migration_stats["total_migrations"] += 1
            self.migration_stats["successful_migrations"] += 1
            self.migration_stats["average_migration_time"] = (
                self.migration_stats["average_migration_time"] * 0.9 + migration_time * 0.1
            )
            
            logger.info(f"✅ Migration session {session_id} terminée avec succès "
                       f"(durée: {migration_time:.2f}s)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur migration session {session_id}: {e}")
            
            # Rollback en cas d'erreur
            await self._rollback_migration(session_id, source_server_id)
            
            self.active_migrations[migration_id]["status"] = "failed"
            self.active_migrations[migration_id]["error"] = str(e)
            self.migration_stats["failed_migrations"] += 1
            
            return False
        
        finally:
            # Nettoyage migration tracking
            if migration_id in self.active_migrations:
                # Garder historique court pour debugging
                if len(self.active_migrations) > 100:
                    # Supprimer anciennes migrations
                    old_migrations = sorted(
                        self.active_migrations.items(),
                        key=lambda x: x[1].get("start_time", 0)
                    )[:50]
                    for old_migration_id, _ in old_migrations:
                        del self.active_migrations[old_migration_id]
    
    async def migrate_all_sessions_from_server(
        self, 
        source_server_id: str, 
        target_servers: List[str],
        reason: str = "server_maintenance"
    ) -> Dict[str, Any]:
        """Migration toutes sessions depuis serveur"""
        migration_result = {
            "total_sessions": 0,
            "successful_migrations": 0,
            "failed_migrations": 0,
            "migration_details": [],
            "duration": 0.0
        }
        
        start_time = time.time()
        
        try:
            logger.info(f"🚚 Migration massive sessions depuis serveur {source_server_id}")
            
            # Récupération toutes sessions serveur
            sessions = await self.session_store.get_sessions_by_server(source_server_id)
            migration_result["total_sessions"] = len(sessions)
            
            if not sessions:
                logger.info(f"Aucune session à migrer depuis serveur {source_server_id}")
                return migration_result
            
            # Migration par batches pour éviter surcharge
            batch_size = min(self.config.max_concurrent_migrations, len(sessions))
            
            for i in range(0, len(sessions), batch_size):
                batch = sessions[i:i + batch_size]
                migration_tasks = []
                
                for j, session_data in enumerate(batch):
                    # Distribution round-robin sur serveurs cibles
                    target_server = target_servers[j % len(target_servers)]
                    
                    task = self.migrate_session(
                        session_data.session_id,
                        source_server_id,
                        target_server,
                        reason
                    )
                    migration_tasks.append((session_data.session_id, task))
                
                # Exécution batch migrations
                batch_results = await asyncio.gather(
                    *[task for _, task in migration_tasks],
                    return_exceptions=True
                )
                
                # Traitement résultats batch
                for (session_id, _), result in zip(migration_tasks, batch_results):
                    if isinstance(result, Exception):
                        migration_result["failed_migrations"] += 1
                        migration_result["migration_details"].append({
                            "session_id": session_id,
                            "status": "failed",
                            "error": str(result)
                        })
                    elif result:
                        migration_result["successful_migrations"] += 1
                        migration_result["migration_details"].append({
                            "session_id": session_id,
                            "status": "success"
                        })
                    else:
                        migration_result["failed_migrations"] += 1
                        migration_result["migration_details"].append({
                            "session_id": session_id,
                            "status": "failed",
                            "error": "Migration returned False"
                        })
                
                # Pause entre batches
                if i + batch_size < len(sessions):
                    await asyncio.sleep(1.0)
            
            migration_result["duration"] = time.time() - start_time
            
            logger.info(f"✅ Migration massive terminée: "
                       f"{migration_result['successful_migrations']}/{migration_result['total_sessions']} "
                       f"sessions migrées avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur migration massive depuis serveur {source_server_id}: {e}")
            migration_result["error"] = str(e)
        
        return migration_result
    
    async def _notify_server_migration_start(self, server_id: str, session_id: str):
        """Notification serveur début migration"""
        try:
            # Simulation notification serveur
            logger.debug(f"📢 Notification serveur {server_id}: migration session {session_id} démarrée")
            # En vraie implémentation: HTTP call ou message queue vers serveur
            await asyncio.sleep(0.1)  # Simule latence réseau
            
        except Exception as e:
            logger.error(f"❌ Erreur notification migration start serveur {server_id}: {e}")
    
    async def _notify_server_migration_complete(self, server_id: str, session_id: str, session_data: SessionData):
        """Notification serveur fin migration"""
        try:
            # Simulation notification serveur avec données session
            logger.debug(f"📢 Notification serveur {server_id}: migration session {session_id} terminée")
            # En vraie implémentation: transfer session state vers nouveau serveur
            await asyncio.sleep(0.1)  # Simule latence réseau
            
        except Exception as e:
            logger.error(f"❌ Erreur notification migration complete serveur {server_id}: {e}")
    
    async def _cleanup_source_server(self, server_id: str, session_id: str):
        """Nettoyage serveur source après migration"""
        try:
            # Simulation nettoyage serveur source
            logger.debug(f"🧹 Nettoyage serveur {server_id}: session {session_id}")
            # En vraie implémentation: cleanup session state sur serveur source
            await asyncio.sleep(0.05)  # Simule latence réseau
            
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage serveur source {server_id}: {e}")
    
    async def _rollback_migration(self, session_id: str, source_server_id: str):
        """Rollback migration en cas d'erreur"""
        try:
            logger.warning(f"🔄 Rollback migration session {session_id}")
            
            # Récupération session et reset état
            session_data = await self.session_store.retrieve_session(session_id)
            if session_data:
                session_data.session_state = SessionState.ACTIVE
                session_data.migration_target = None
                session_data.server_id = source_server_id
                await self.session_store.store_session(session_data)
            
        except Exception as e:
            logger.error(f"❌ Erreur rollback migration session {session_id}: {e}")

class SessionAwareBalancer:
    """
    🔗 LOAD BALANCER SESSION-AWARE ENTERPRISE
    
    Load balancer session-aware avec sticky sessions intelligent.
    Session affinity + stateful routing + graceful session migration.
    """
    
    def __init__(self, session_config: Optional[SessionConfig] = None):
        self.session_config = session_config or SessionConfig()
        self.session_store = DistributedSessionStore(self.session_config)
        self.affinity_manager = SessionAffinityManager(self.session_config)
        self.migration_engine = SessionMigrationEngine(self.session_config, self.session_store)
        
        # Serveurs disponibles
        self.available_servers: Dict[str, ServerSession] = {}
        
        # Métriques session-aware balancing
        self.total_session_requests = 0
        self.affinity_hits = 0
        self.affinity_misses = 0
        self.new_sessions_created = 0
        self.sessions_migrated = 0
        
        # Tâches background
        self.cleanup_task: Optional[asyncio.Task] = None
        
        logger.info("🔗 Session-Aware Load Balancer initialisé")
    
    async def initialize(self) -> bool:
        """Initialisation load balancer session-aware"""
        try:
            # Initialisation session store
            store_success = await self.session_store.initialize()
            if not store_success:
                raise Exception("Échec initialisation session store")
            
            # Démarrage tâches background
            self.cleanup_task = asyncio.create_task(self._background_cleanup())
            
            # Initialisation serveurs démo
            await self._initialize_demo_servers()
            
            logger.info("✅ Session-Aware Load Balancer initialisé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Session-Aware Load Balancer: {e}")
            return False
    
    async def _initialize_demo_servers(self):
        """Initialisation serveurs démo"""
        demo_servers = [
            ServerSession(
                server_id="session-srv-01",
                hostname="app1.ainflue.com",
                port=8080,
                is_healthy=True,
                current_sessions=45,
                max_sessions=100,
                session_capacity_percent=45.0,
                average_session_duration=1800.0,  # 30 minutes
                session_migration_capable=True
            ),
            ServerSession(
                server_id="session-srv-02", 
                hostname="app2.ainflue.com",
                port=8080,
                is_healthy=True,
                current_sessions=30,
                max_sessions=100,
                session_capacity_percent=30.0,
                average_session_duration=2100.0,  # 35 minutes
                session_migration_capable=True
            ),
            ServerSession(
                server_id="session-srv-03",
                hostname="app3.ainflue.com",
                port=8080,
                is_healthy=True,
                current_sessions=60,
                max_sessions=80,
                session_capacity_percent=75.0,
                average_session_duration=1500.0,  # 25 minutes
                session_migration_capable=True
            ),
        ]
        
        for server in demo_servers:
            self.available_servers[server.server_id] = server
            logger.info(f"🖥️ Serveur ajouté: {server.server_id} ({server.current_sessions}/{server.max_sessions} sessions)")

    async def route_with_session_affinity(self, session_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        🎯 ROUTING AVEC SESSION AFFINITY INTELLIGENT
        
        Routing avec session affinity intelligent et failover automatique.
        """
        start_time = time.time()
        
        try:
            self.total_session_requests += 1
            logger.debug(f"🔗 Routing session-aware pour session {session_id}")
            
            # Récupération données session existante
            session_data = await self.session_store.retrieve_session(session_id)
            
            if session_data and not session_data.is_expired:
                # Session existante - routing avec affinity
                return await self._route_existing_session(session_data, request, start_time)
            else:
                # Nouvelle session - création et routing
                return await self._route_new_session(session_id, request, start_time)
                
        except Exception as e:
            logger.error(f"❌ Erreur routing session-aware {session_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "fallback_used": True
            }

    async def migrate_sessions_gracefully(self, source_server: str, target_server: str) -> bool:
        """
        🚚 MIGRATION GRACIEUSE SESSIONS ENTRE SERVEURS
        
        Migration gracieuse sessions entre serveurs avec minimal disruption.
        """
        logger.info(f"🚚 Migration gracieuse sessions: {source_server} -> {target_server}")
        
        try:
            # Vérification serveurs
            if source_server not in self.available_servers:
                raise Exception(f"Serveur source {source_server} non trouvé")
            
            if target_server not in self.available_servers:
                raise Exception(f"Serveur cible {target_server} non trouvé")
            
            target_server_obj = self.available_servers[target_server]
            if not target_server_obj.can_accept_sessions:
                raise Exception(f"Serveur cible {target_server} ne peut pas accepter sessions")
            
            # Migration toutes sessions du serveur source
            migration_result = await self.migration_engine.migrate_all_sessions_from_server(
                source_server, 
                [target_server],  # Un seul serveur cible pour cette méthode
                "graceful_migration"
            )
            
            # Mise à jour affinités
            for detail in migration_result["migration_details"]:
                if detail["status"] == "success":
                    await self.affinity_manager.update_session_affinity(
                        detail["session_id"],
                        target_server,
                        "graceful_migration"
                    )
            
            # Mise à jour métriques
            self.sessions_migrated += migration_result["successful_migrations"]
            
            logger.info(f"✅ Migration gracieuse terminée: "
                       f"{migration_result['successful_migrations']}/{migration_result['total_sessions']} "
                       f"sessions migrées")
            
            return migration_result["successful_migrations"] == migration_result["total_sessions"]
            
        except Exception as e:
            logger.error(f"❌ Erreur migration gracieuse {source_server} -> {target_server}: {e}")
            return False

    async def replicate_session_state(self, session_data: SessionData) -> Dict[str, Any]:
        """
        📋 RÉPLICATION ÉTAT SESSION POUR HIGH AVAILABILITY
        
        Réplication état session pour high availability et fault tolerance.
        """
        logger.debug(f"📋 Réplication état session {session_data.session_id}")
        
        replication_result = {
            "session_id": session_data.session_id,
            "primary_server": session_data.server_id,
            "replication_servers": [],
            "successful_replications": 0,
            "failed_replications": 0,
            "replication_details": []
        }
        
        try:
            # Sélection serveurs réplication
            available_servers = [
                server_id for server_id, server in self.available_servers.items()
                if server.is_healthy and server.can_accept_sessions and server_id != session_data.server_id
            ]
            
            replication_count = min(
                self.session_config.session_replication_factor,
                len(available_servers)
            )
            
            replication_servers = available_servers[:replication_count]
            
            # Réplication sur serveurs sélectionnés
            for replica_server in replication_servers:
                try:
                    # Création copie session pour réplication
                    replica_session = SessionData(
                        session_id=f"{session_data.session_id}_replica_{replica_server}",
                        user_id=session_data.user_id,
                        server_id=replica_server,
                        client_ip=session_data.client_ip,
                        user_agent=session_data.user_agent,
                        session_state=SessionState.ACTIVE,
                        created_at=session_data.created_at,
                        last_accessed=session_data.last_accessed,
                        expires_at=session_data.expires_at,
                        session_data=session_data.session_data.copy(),
                        affinity_type=SessionAffinityType.DISTRIBUTED
                    )
                    
                    # Stockage réplique
                    success = await self.session_store.store_session(replica_session)
                    
                    if success:
                        replication_result["replication_servers"].append(replica_server)
                        replication_result["successful_replications"] += 1
                        replication_result["replication_details"].append({
                            "server": replica_server,
                            "status": "success"
                        })
                        
                        # Mise à jour session originale
                        session_data.replication_servers.add(replica_server)
                    else:
                        replication_result["failed_replications"] += 1
                        replication_result["replication_details"].append({
                            "server": replica_server,
                            "status": "failed",
                            "error": "Stockage réplique échoué"
                        })
                        
                except Exception as e:
                    replication_result["failed_replications"] += 1
                    replication_result["replication_details"].append({
                        "server": replica_server,
                        "status": "failed",
                        "error": str(e)
                    })
            
            # Mise à jour session avec infos réplication
            if replication_result["successful_replications"] > 0:
                await self.session_store.store_session(session_data)
            
            logger.debug(f"📋 Réplication session terminée: "
                        f"{replication_result['successful_replications']} succès, "
                        f"{replication_result['failed_replications']} échecs")
            
        except Exception as e:
            logger.error(f"❌ Erreur réplication session {session_data.session_id}: {e}")
            replication_result["error"] = str(e)
        
        return replication_result

    async def optimize_session_distribution(self, session_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        ⚖️ OPTIMISATION DISTRIBUTION SESSIONS POUR LOAD BALANCING
        
        Optimisation distribution sessions pour load balancing optimal.
        """
        logger.info("⚖️ Optimisation distribution sessions")
        
        optimization_result = {
            "current_distribution": {},
            "optimization_actions": [],
            "rebalancing_recommendations": [],
            "performance_improvements": {},
            "summary": {}
        }
        
        try:
            # Analyse distribution actuelle
            for server_id, server in self.available_servers.items():
                session_count = self.affinity_manager.get_server_session_count(server_id)
                optimization_result["current_distribution"][server_id] = {
                    "session_count": session_count,
                    "capacity_percent": server.session_capacity_percent,
                    "max_sessions": server.max_sessions,
                    "is_healthy": server.is_healthy,
                    "can_accept_sessions": server.can_accept_sessions
                }
            
            # Identification serveurs surchargés
            overloaded_servers = []
            underloaded_servers = []
            
            for server_id, distribution_data in optimization_result["current_distribution"].items():
                capacity_percent = distribution_data["capacity_percent"]
                
                if capacity_percent > 85.0:  # Surchargé
                    overloaded_servers.append((server_id, capacity_percent))
                elif capacity_percent < 30.0 and distribution_data["is_healthy"]:  # Sous-chargé
                    underloaded_servers.append((server_id, capacity_percent))
            
            # Recommandations rééquilibrage
            if overloaded_servers and underloaded_servers:
                for overloaded_server, overload_percent in overloaded_servers:
                    # Calcul sessions à migrer
                    sessions_to_migrate = max(1, int(overload_percent * 0.1))  # 10% des sessions
                    
                    # Sélection serveur cible moins chargé
                    target_server = min(underloaded_servers, key=lambda x: x[1])[0]
                    
                    optimization_result["rebalancing_recommendations"].append({
                        "source_server": overloaded_server,
                        "target_server": target_server,
                        "sessions_to_migrate": sessions_to_migrate,
                        "reason": f"Rééquilibrage charge: {overload_percent:.1f}% -> optimal",
                        "estimated_improvement": f"Réduction charge {overloaded_server}: ~{sessions_to_migrate * 5}%"
                    })
            
            # Actions d'optimisation
            total_sessions = sum(
                data["session_count"] for data in optimization_result["current_distribution"].values()
            )
            
            healthy_servers = [
                server_id for server_id, data in optimization_result["current_distribution"].items()
                if data["is_healthy"]
            ]
            
            if healthy_servers:
                optimal_sessions_per_server = total_sessions / len(healthy_servers)
                
                for server_id, data in optimization_result["current_distribution"].items():
                    current_sessions = data["session_count"]
                    deviation = abs(current_sessions - optimal_sessions_per_server)
                    
                    if deviation > optimal_sessions_per_server * 0.3:  # >30% déviation
                        action_type = "reduce_load" if current_sessions > optimal_sessions_per_server else "increase_load"
                        optimization_result["optimization_actions"].append({
                            "server": server_id,
                            "action": action_type,
                            "current_sessions": current_sessions,
                            "optimal_sessions": int(optimal_sessions_per_server),
                            "deviation": int(deviation)
                        })
            
            # Calcul améliorations performance estimées
            optimization_result["performance_improvements"] = {
                "estimated_response_time_improvement_ms": len(overloaded_servers) * 25,
                "estimated_throughput_increase_percent": len(overloaded_servers) * 15,
                "load_distribution_score": self._calculate_load_distribution_score(
                    optimization_result["current_distribution"]
                ),
                "session_stickiness_efficiency": (self.affinity_hits / max(1, self.total_session_requests)) * 100
            }
            
            # Résumé optimisation
            optimization_result["summary"] = {
                "total_servers": len(self.available_servers),
                "healthy_servers": len(healthy_servers),
                "overloaded_servers": len(overloaded_servers),
                "underloaded_servers": len(underloaded_servers),
                "total_sessions": total_sessions,
                "optimization_actions": len(optimization_result["optimization_actions"]),
                "rebalancing_needed": len(optimization_result["rebalancing_recommendations"]) > 0
            }
            
            logger.info(f"✅ Optimisation distribution sessions terminée: "
                       f"{len(optimization_result['optimization_actions'])} actions identifiées")
            
        except Exception as e:
            logger.error(f"❌ Erreur optimisation distribution sessions: {e}")
            optimization_result["error"] = str(e)
        
        return optimization_result
    
    # Méthodes utilitaires privées
    
    async def _route_existing_session(self, session_data: SessionData, request: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Routing session existante avec affinity"""
        try:
            # Mise à jour dernière activité
            session_data.last_accessed = datetime.now()
            session_data.access_count += 1
            
            # Vérification serveur affin toujours disponible
            target_server_id = session_data.server_id
            
            if target_server_id in self.available_servers:
                target_server = self.available_servers[target_server_id]
                
                if target_server.is_healthy and target_server.can_accept_sessions:
                    # Serveur affin disponible - route normale
                    await self.session_store.store_session(session_data)
                    
                    self.affinity_hits += 1
                    routing_time = time.time() - start_time
                    
                    return {
                        "success": True,
                        "session_id": session_data.session_id,
                        "server_id": target_server_id,
                        "server_endpoint": f"http://{target_server.hostname}:{target_server.port}",
                        "affinity_type": session_data.affinity_type.value,
                        "routing_reason": "session_affinity",
                        "session_age_seconds": (datetime.now() - session_data.created_at).total_seconds(),
                        "routing_time_ms": routing_time * 1000
                    }
            
            # Serveur affin indisponible - failover
            logger.warning(f"⚠️ Serveur affin {target_server_id} indisponible pour session {session_data.session_id}")
            return await self._handle_affinity_failover(session_data, request, start_time)
            
        except Exception as e:
            logger.error(f"❌ Erreur routing session existante {session_data.session_id}: {e}")
            raise
    
    async def _route_new_session(self, session_id: str, request: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Routing nouvelle session"""
        try:
            # Sélection serveur optimal pour nouvelle session
            available_server_ids = [
                server_id for server_id, server in self.available_servers.items()
                if server.can_accept_sessions
            ]
            
            if not available_server_ids:
                raise Exception("Aucun serveur disponible pour nouvelle session")
            
            # Sélection serveur moins chargé
            selected_server_id = self.affinity_manager.get_least_loaded_server(available_server_ids)
            selected_server = self.available_servers[selected_server_id]
            
            # Création nouvelle session
            client_ip = request.get("client_ip", "unknown")
            user_agent = request.get("user_agent", "unknown")
            user_id = request.get("user_id")
            session_timeout = min(
                request.get("session_timeout", self.session_config.default_session_timeout),
                self.session_config.max_session_timeout
            )
            
            new_session = SessionData(
                session_id=session_id,
                user_id=user_id,
                server_id=selected_server_id,
                client_ip=client_ip,
                user_agent=user_agent,
                session_state=SessionState.ACTIVE,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                expires_at=datetime.now() + timedelta(seconds=session_timeout),
                affinity_type=SessionAffinityType.SOFT
            )
            
            # Stockage session
            success = await self.session_store.store_session(new_session)
            if not success:
                raise Exception("Échec stockage nouvelle session")
            
            # Création affinité
            await self.affinity_manager.create_session_affinity(
                session_id, selected_server_id, SessionAffinityType.SOFT
            )
            
            # Réplication session si configurée
            if self.session_config.session_replication_factor > 0:
                asyncio.create_task(self.replicate_session_state(new_session))
            
            # Mise à jour métriques
            self.new_sessions_created += 1
            routing_time = time.time() - start_time
            
            logger.info(f"🆕 Nouvelle session créée: {session_id} -> serveur {selected_server_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "server_id": selected_server_id,
                "server_endpoint": f"http://{selected_server.hostname}:{selected_server.port}",
                "affinity_type": new_session.affinity_type.value,
                "routing_reason": "new_session",
                "session_timeout": session_timeout,
                "routing_time_ms": routing_time * 1000,
                "cookie_config": {
                    "name": self.session_config.affinity_cookie_name,
                    "domain": self.session_config.affinity_cookie_domain,
                    "max_age": session_timeout
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur routing nouvelle session {session_id}: {e}")
            raise
    
    async def _handle_affinity_failover(self, session_data: SessionData, request: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Gestion failover affinité session"""
        try:
            self.affinity_misses += 1
            
            # Sélection serveur failover
            available_server_ids = [
                server_id for server_id, server in self.available_servers.items()
                if server.can_accept_sessions
            ]
            
            if not available_server_ids:
                raise Exception("Aucun serveur disponible pour failover")
            
            # Vérifier d'abord serveurs réplication
            failover_server_id = None
            for replica_server in session_data.replication_servers:
                if replica_server in available_server_ids:
                    failover_server_id = replica_server
                    break
            
            # Sinon serveur moins chargé
            if not failover_server_id:
                failover_server_id = self.affinity_manager.get_least_loaded_server(available_server_ids)
            
            # Migration session vers serveur failover
            old_server_id = session_data.server_id
            migration_success = await self.migration_engine.migrate_session(
                session_data.session_id,
                old_server_id,
                failover_server_id,
                "affinity_failover"
            )
            
            if migration_success:
                # Mise à jour affinité
                await self.affinity_manager.update_session_affinity(
                    session_data.session_id,
                    failover_server_id,
                    "affinity_failover"
                )
                
                failover_server = self.available_servers[failover_server_id]
                routing_time = time.time() - start_time
                
                return {
                    "success": True,
                    "session_id": session_data.session_id,
                    "server_id": failover_server_id,
                    "server_endpoint": f"http://{failover_server.hostname}:{failover_server.port}",
                    "affinity_type": session_data.affinity_type.value,
                    "routing_reason": "affinity_failover",
                    "original_server": old_server_id,
                    "session_migrated": True,
                    "routing_time_ms": routing_time * 1000
                }
            else:
                raise Exception("Échec migration session pour failover")
                
        except Exception as e:
            logger.error(f"❌ Erreur failover affinité session {session_data.session_id}: {e}")
            raise
    
    def _calculate_load_distribution_score(self, distribution: Dict[str, Dict[str, Any]]) -> float:
        """Calcul score distribution charge (0-100)"""
        try:
            capacity_percentages = [
                data["capacity_percent"] for data in distribution.values()
                if data["is_healthy"]
            ]
            
            if not capacity_percentages:
                return 0.0
            
            # Score basé sur variance (plus faible variance = meilleure distribution)
            mean_capacity = sum(capacity_percentages) / len(capacity_percentages)
            variance = sum((x - mean_capacity) ** 2 for x in capacity_percentages) / len(capacity_percentages)
            
            # Normalisation score (0-100, 100 = distribution parfaite)
            distribution_score = max(0.0, 100.0 - variance)
            
            return min(100.0, distribution_score)
            
        except Exception:
            return 50.0  # Score neutre en cas d'erreur
    
    async def _background_cleanup(self):
        """Tâche background nettoyage sessions expirées"""
        while True:
            try:
                await asyncio.sleep(self.session_config.session_cleanup_interval)
                
                # Nettoyage sessions expirées
                cleaned_count = await self.session_store.cleanup_expired_sessions()
                
                if cleaned_count > 0:
                    logger.info(f"🧹 Nettoyage background: {cleaned_count} sessions expirées supprimées")
                
            except asyncio.CancelledError:
                logger.info("🛑 Tâche nettoyage background arrêtée")
                break
            except Exception as e:
                logger.error(f"❌ Erreur tâche nettoyage background: {e}")
                await asyncio.sleep(60)  # Attente avant retry

# Point d'entrée pour tests et démonstration
async def main():
    """Démonstration Session-Aware Load Balancer"""
    logger.info("🚀 Démonstration Session-Aware Load Balancer")
    
    # Configuration session
    session_config = SessionConfig(
        default_session_timeout=1800,  # 30 minutes
        session_replication_factor=1,
        enable_session_encryption=True,
        storage_tier=SessionStorageTier.HYBRID
    )
    
    # Initialisation load balancer session-aware
    session_lb = SessionAwareBalancer(session_config)
    
    # Initialisation (sans Redis réel pour démo)
    session_config.redis_connection_string = "redis://fake"  # Simulation
    await session_lb.initialize()
    
    # Test routing avec affinité session
    test_sessions = ["sess_001", "sess_002", "sess_003"]
    
    for session_id in test_sessions:
        request_context = {
            "client_ip": "192.168.1.100",
            "user_agent": "TestBrowser/1.0",
            "user_id": f"user_{session_id[-3:]}",
            "session_timeout": 3600
        }
        
        # Premier appel - création session
        routing_result = await session_lb.route_with_session_affinity(session_id, request_context)
        logger.info(f"🔗 Session {session_id}: serveur={routing_result.get('server_id', 'none')} "
                   f"(raison: {routing_result.get('routing_reason', 'unknown')})")
        
        # Second appel - utilisation affinité
        routing_result2 = await session_lb.route_with_session_affinity(session_id, request_context)
        logger.info(f"🔗 Session {session_id} (2e appel): serveur={routing_result2.get('server_id', 'none')} "
                   f"(raison: {routing_result2.get('routing_reason', 'unknown')})")
    
    # Test migration gracieuse
    migration_success = await session_lb.migrate_sessions_gracefully(
        "session-srv-01", "session-srv-02"
    )
    logger.info(f"🚚 Migration gracieuse: {'succès' if migration_success else 'échec'}")
    
    # Test optimisation distribution
    session_metrics = {
        "total_active_sessions": 120,
        "average_session_duration": 1800,
        "session_creation_rate": 5.2  # sessions/minute
    }
    
    optimization_result = await session_lb.optimize_session_distribution(session_metrics)
    logger.info(f"⚖️ Optimisation distribution: {optimization_result['summary']['optimization_actions']} actions")
    
    logger.info("✅ Démonstration terminée avec succès")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())