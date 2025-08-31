"""IA-Influencer-Agent - Event Replication and Multi-Tenant Synchronization
Module: backend/core/events/event_replication.py
Architecture: Event Replication and Cross-Tenant Synchronization System
Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT STRICT ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
INTERDIT : Copie, reproduction, modification, ou usage sans autorisation écrite explicite.
Toute violation sera poursuivie selon la loi allemande et française.
Contact autorisations : mlaiel@live.de

Description:
    Système avancé de réplication d'événements pour multi-tenant, disaster recovery,
    synchronisation cross-region et intégrations externes pour IA-Influencer-Agent.
"""
from typing import Any, Dict, List, Optional, Union, Set, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import asyncio
import json
import logging
import uuid
import hashlib
import time
from collections import defaultdict, deque

import redis.asyncio as redis
import aiohttp
import asyncpg
from websockets.client import connect as ws_connect

from .event_bus import Event, EventBus, EventPriority, EventStatus
from .event_store import EventStore

logger = logging.getLogger(__name__)


class ReplicationStrategy(Enum):
    """Stratégies de réplication"""    SYNCHRONOUS = "synchronous"  # Réplication synchrone
    ASYNCHRONOUS = "asynchronous"  # Réplication asynchrone
    EVENTUAL = "eventual"  # Cohérence éventuelle
    PRIORITY_BASED = "priority_based"  # Basée sur la priorité


class ReplicationStatus(Enum):
    """Statut de réplication"""    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"  # Réplication partielle réussie
    CONFLICTED = "conflicted"  # Conflit détecté


class ConflictResolution(Enum):
    """Stratégies de résolution de conflits"""    LATEST_WINS = "latest_wins"  # Le plus récent gagne
    SOURCE_WINS = "source_wins"  # La source gagne
    MANUAL = "manual"  # Résolution manuelle
    CUSTOM = "custom"  # Logique personnalisée


class ReplicationType(Enum):
    """Types de réplication"""    FULL = "full"  # Réplication complète
    INCREMENTAL = "incremental"  # Réplication incrémentale
    SELECTIVE = "selective"  # Réplication sélective
    ON_DEMAND = "on_demand"  # À la demande


@dataclass
class ReplicationTarget:
    """Cible de réplication"""    target_id: str
    name: str
    type: str  # database, api, queue, websocket
    connection_config: Dict[str, Any] = field(default_factory=dict)
    replication_strategy: ReplicationStrategy = ReplicationStrategy.ASYNCHRONOUS
    replication_type: ReplicationType = ReplicationType.INCREMENTAL
    conflict_resolution: ConflictResolution = ConflictResolution.LATEST_WINS
    enabled: bool = True
    filters: Dict[str, Any] = field(default_factory=dict)  # Filtres d'événements
    last_sync: Optional[datetime] = None
    health_check_url: Optional[str] = None
    retry_policy: Dict[str, Any] = field(default_factory=lambda: {
        "max_retries": 3,
        "retry_delay": 5,
        "exponential_backoff": True
    })
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_id": self.target_id,
            "name": self.name,
            "type": self.type,
            "connection_config": self.connection_config,
            "replication_strategy": self.replication_strategy.value,
            "replication_type": self.replication_type.value,
            "conflict_resolution": self.conflict_resolution.value,
            "enabled": self.enabled,
            "filters": self.filters,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "health_check_url": self.health_check_url,
            "retry_policy": self.retry_policy
        }


@dataclass
class ReplicationLog:
    """Log de réplication"""    log_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    target_id: str = ""
    event_id: str = ""
    status: ReplicationStatus = ReplicationStatus.PENDING
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "log_id": self.log_id,
            "target_id": self.target_id,
            "event_id": self.event_id,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "error_message": self.error_message,
            "metadata": self.metadata
        }


@dataclass
class ConflictRecord:
    """Enregistrement de conflit"""    conflict_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str = ""
    target_id: str = ""
    source_event: Optional[Dict[str, Any]] = None
    target_event: Optional[Dict[str, Any]] = None
    conflict_type: str = ""  # timestamp, data, version
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    resolution_strategy: Optional[ConflictResolution] = None
    resolved_event: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReplicationConnector(ABC):
    """Interface pour les connecteurs de réplication"""    
    @abstractmethod
    async def connect(self) -> bool:
        """Établit la connexion"""        pass
    
    @abstractmethod
    async def disconnect(self):
        """Ferme la connexion"""        pass
    
    @abstractmethod
    async def replicate_event(self, event: Event) -> bool:
        """Réplique un événement"""        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Vérifie la santé de la connexion"""        pass
    
    @abstractmethod
    async def get_last_event_timestamp(self) -> Optional[datetime]:
        """Retourne le timestamp du dernier événement répliqué"""        pass


class DatabaseReplicationConnector(ReplicationConnector):
    """Connecteur de réplication vers base de données"""    
    def __init__(self, target: ReplicationTarget):
        self.target = target
        self.connection: Optional[asyncpg.Connection] = None
        self.connection_pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> bool:
        """Établit la connexion à la base de données"""        try:
            config = self.target.connection_config
            self.connection_pool = await asyncpg.create_pool(
                host=config.get("host", "localhost"),
                port=config.get("port", 5432),
                user=config.get("user", "postgres"),
                password=config.get("password", ""),
                database=config.get("database", "events_replica"),
                min_size=config.get("min_connections", 1),
                max_size=config.get("max_connections", 10)
            )
            
            # Vérification de la table events
            async with self.connection_pool.acquire() as conn:
                await conn.execute("""                    CREATE TABLE IF NOT EXISTS replicated_events (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        source TEXT,
                        subject TEXT,
                        data JSONB,
                        metadata JSONB,
                        timestamp TIMESTAMPTZ,
                        priority TEXT,
                        status TEXT,
                        user_id TEXT,
                        tenant_id TEXT,
                        correlation_id TEXT,
                        causation_id TEXT,
                        version INTEGER,
                        replicated_at TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
                
                await conn.execute("""                    CREATE INDEX IF NOT EXISTS idx_replicated_events_timestamp 
                    ON replicated_events(timestamp)
                """)
                
                await conn.execute("""                    CREATE INDEX IF NOT EXISTS idx_replicated_events_type 
                    ON replicated_events(type)
                """)
            
            logger.info("Database replication connector established for %s", self.target.target_id)
            return True
            
        except Exception as e:
            logger.error("Failed to establish database connection for %s: %s", 
                        self.target.target_id, e)
            return False
    
    async def disconnect(self):
        """Ferme la connexion"""        if self.connection_pool:
            await self.connection_pool.close()
            self.connection_pool = None
    
    async def replicate_event(self, event: Event) -> bool:
        """Réplique un événement vers la base de données"""        if not self.connection_pool:
            return False
        
        try:
            async with self.connection_pool.acquire() as conn:
                await conn.execute("""                    INSERT INTO replicated_events (
                        id, type, source, subject, data, metadata, timestamp,
                        priority, status, user_id, tenant_id, correlation_id,
                        causation_id, version
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                    ON CONFLICT (id) DO UPDATE SET
                        data = EXCLUDED.data,
                        metadata = EXCLUDED.metadata,
                        timestamp = EXCLUDED.timestamp,
                        replicated_at = NOW()
                """, 
                event.id, event.type, event.source, event.subject,
                json.dumps(event.data), json.dumps(event.metadata),
                event.timestamp, event.priority.value, event.status.value,
                event.user_id, event.tenant_id, event.correlation_id,
                event.causation_id, event.version
                )
            
            return True
            
        except Exception as e:
            logger.error("Failed to replicate event %s to database %s: %s",
                        event.id, self.target.target_id, e)
            return False
    
    async def health_check(self) -> bool:
        """Vérifie la santé de la connexion"""        if not self.connection_pool:
            return False
        
        try:
            async with self.connection_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except:
            return False
    
    async def get_last_event_timestamp(self) -> Optional[datetime]:
        """Retourne le timestamp du dernier événement"""        if not self.connection_pool:
            return None
        
        try:
            async with self.connection_pool.acquire() as conn:
                result = await conn.fetchval("""                    SELECT MAX(timestamp) FROM replicated_events
                """)
                return result
        except:
            return None


class APIReplicationConnector(ReplicationConnector):
    """Connecteur de réplication via API REST"""    
    def __init__(self, target: ReplicationTarget):
        self.target = target
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = target.connection_config.get("base_url", "")
        self.api_key = target.connection_config.get("api_key", "")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
    
    async def connect(self) -> bool:
        """Établit la session HTTP"""        try:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=timeout
            )
            
            # Test de connexion
            health_check = await self.health_check()
            if health_check:
                logger.info("API replication connector established for %s", self.target.target_id)
                return True
            else:
                await self.disconnect()
                return False
                
        except Exception as e:
            logger.error("Failed to establish API connection for %s: %s",
                        self.target.target_id, e)
            return False
    
    async def disconnect(self):
        """Ferme la session"""        if self.session:
            await self.session.close()
            self.session = None
    
    async def replicate_event(self, event: Event) -> bool:
        """Réplique un événement via API"""        if not self.session:
            return False
        
        try:
            endpoint = f"{self.base_url}/events"
            payload = event.to_dict()
            
            async with self.session.post(endpoint, json=payload) as response:
                success = response.status < 400
                if not success:
                    error_text = await response.text()
                    logger.error("API replication failed for event %s: %s (status: %d)",
                               event.id, error_text, response.status)
                
                return success
                
        except Exception as e:
            logger.error("Failed to replicate event %s via API %s: %s",
                        event.id, self.target.target_id, e)
            return False
    
    async def health_check(self) -> bool:
        """Vérifie la santé de l'API"""        if not self.session:
            return False
        
        try:
            health_url = self.target.health_check_url or f"{self.base_url}/health"
            async with self.session.get(health_url) as response:
                return response.status == 200
        except:
            return False
    
    async def get_last_event_timestamp(self) -> Optional[datetime]:
        """Retourne le timestamp du dernier événement"""        if not self.session:
            return None
        
        try:
            endpoint = f"{self.base_url}/events/last"
            async with self.session.get(endpoint) as response:
                if response.status == 200:
                    data = await response.json()
                    timestamp_str = data.get("timestamp")
                    if timestamp_str:
                        return datetime.fromisoformat(timestamp_str)
        except:
            pass
        
        return None


class WebSocketReplicationConnector(ReplicationConnector):
    """Connecteur de réplication via WebSocket"""    
    def __init__(self, target: ReplicationTarget):
        self.target = target
        self.websocket = None
        self.ws_url = target.connection_config.get("ws_url", "")
        self.auth_token = target.connection_config.get("auth_token", "")
        self._connected = False
    
    async def connect(self) -> bool:
        """Établit la connexion WebSocket"""        try:
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            self.websocket = await ws_connect(self.ws_url, extra_headers=headers)
            self._connected = True
            
            # Authentification si nécessaire
            if self.auth_token:
                auth_message = {
                    "type": "auth",
                    "token": self.auth_token
                }
                await self.websocket.send(json.dumps(auth_message))
            
            logger.info("WebSocket replication connector established for %s", self.target.target_id)
            return True
            
        except Exception as e:
            logger.error("Failed to establish WebSocket connection for %s: %s",
                        self.target.target_id, e)
            return False
    
    async def disconnect(self):
        """Ferme la connexion WebSocket"""        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            self._connected = False
    
    async def replicate_event(self, event: Event) -> bool:
        """Réplique un événement via WebSocket"""        if not self.websocket or not self._connected:
            return False
        
        try:
            message = {
                "type": "event_replication",
                "event": event.to_dict()
            }
            
            await self.websocket.send(json.dumps(message))
            return True
            
        except Exception as e:
            logger.error("Failed to replicate event %s via WebSocket %s: %s",
                        event.id, self.target.target_id, e)
            self._connected = False
            return False
    
    async def health_check(self) -> bool:
        """Vérifie la santé de la connexion WebSocket"""        return self._connected and self.websocket and not self.websocket.closed
    
    async def get_last_event_timestamp(self) -> Optional[datetime]:
        """Retourne le timestamp du dernier événement"""        # WebSocket ne maintient pas d'historique par défaut
        return None


class RedisReplicationConnector(ReplicationConnector):
    """Connecteur de réplication via Redis"""    
    def __init__(self, target: ReplicationTarget):
        self.target = target
        self.redis_client: Optional[redis.Redis] = None
        self.stream_name = target.connection_config.get("stream_name", "events")
    
    async def connect(self) -> bool:
        """Établit la connexion Redis"""        try:
            config = self.target.connection_config
            self.redis_client = redis.Redis(
                host=config.get("host", "localhost"),
                port=config.get("port", 6379),
                db=config.get("db", 0),
                password=config.get("password"),
                decode_responses=True
            )
            
            # Test de connexion
            await self.redis_client.ping()
            
            logger.info("Redis replication connector established for %s", self.target.target_id)
            return True
            
        except Exception as e:
            logger.error("Failed to establish Redis connection for %s: %s",
                        self.target.target_id, e)
            return False
    
    async def disconnect(self):
        """Ferme la connexion Redis"""        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
    
    async def replicate_event(self, event: Event) -> bool:
        """Réplique un événement vers Redis Stream"""        if not self.redis_client:
            return False
        
        try:
            event_data = event.to_dict()
            # Flatten dict for Redis Stream
            flattened = {}
            for key, value in event_data.items():
                if isinstance(value, (dict, list)):
                    flattened[key] = json.dumps(value)
                else:
                    flattened[key] = str(value)
            
            await self.redis_client.xadd(self.stream_name, flattened)
            return True
            
        except Exception as e:
            logger.error("Failed to replicate event %s to Redis %s: %s",
                        event.id, self.target.target_id, e)
            return False
    
    async def health_check(self) -> bool:
        """Vérifie la santé de Redis"""        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.ping()
            return True
        except:
            return False
    
    async def get_last_event_timestamp(self) -> Optional[datetime]:
        """Retourne le timestamp du dernier événement"""        if not self.redis_client:
            return None
        
        try:
            # Récupère le dernier message du stream
            messages = await self.redis_client.xrevrange(self.stream_name, count=1)
            if messages:
                message_data = messages[0][1]
                timestamp_str = message_data.get("timestamp")
                if timestamp_str:
                    return datetime.fromisoformat(timestamp_str)
        except:
            pass
        
        return None


class EventReplicationManager:
    """Gestionnaire de réplication d'événements"""    
    def __init__(
        self,
        event_bus: EventBus,
        event_store: Optional[EventStore] = None,
        redis_client: Optional[redis.Redis] = None
    ):
        self.event_bus = event_bus
        self.event_store = event_store
        self.redis_client = redis_client
        
        # Gestion des cibles et connecteurs
        self.targets: Dict[str, ReplicationTarget] = {}
        self.connectors: Dict[str, ReplicationConnector] = {}
        
        # Queues de réplication
        self.replication_queues: Dict[str, asyncio.Queue] = {}
        self.priority_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        
        # Logs et conflits
        self.replication_logs: Dict[str, ReplicationLog] = {}
        self.conflict_records: Dict[str, ConflictRecord] = {}
        
        # État et statistiques
        self._replicating = False
        self._replication_tasks: Dict[str, asyncio.Task] = {}
        self.stats = {
            "events_replicated": 0,
            "replication_failures": 0,
            "conflicts_detected": 0,
            "conflicts_resolved": 0,
            "targets_healthy": 0,
            "targets_unhealthy": 0
        }
        
        # Configuration
        self.config = {
            "batch_size": 100,
            "sync_interval": 30,
            "health_check_interval": 60,
            "conflict_resolution_timeout": 300,
            "max_retry_attempts": 3
        }
        
        # Abonnement aux événements
        self.event_bus.subscribe("*", self._handle_event_for_replication)
        
        logger.info("EventReplicationManager initialized")
    
    async def start(self):
        """Démarre le système de réplication"""        if self._replicating:
            return
        
        self._replicating = True
        
        # Démarrage des tâches de réplication
        asyncio.create_task(self._replication_loop())
        asyncio.create_task(self._health_check_loop())
        asyncio.create_task(self._sync_loop())
        
        logger.info("EventReplicationManager started")
    
    async def stop(self):
        """Arrête le système de réplication"""        self._replicating = False
        
        # Arrêt des tâches
        for task in self._replication_tasks.values():
            task.cancel()
        
        # Déconnexion des connecteurs
        for connector in self.connectors.values():
            await connector.disconnect()
        
        logger.info("EventReplicationManager stopped")
    
    def add_target(self, target: ReplicationTarget) -> bool:
        """Ajoute une cible de réplication"""        try:
            # Création du connecteur approprié
            connector = self._create_connector(target)
            if not connector:
                logger.error("Failed to create connector for target %s", target.target_id)
                return False
            
            self.targets[target.target_id] = target
            self.connectors[target.target_id] = connector
            self.replication_queues[target.target_id] = asyncio.Queue()
            
            # Démarrage de la tâche de réplication pour cette cible
            if self._replicating:
                task = asyncio.create_task(self._replicate_to_target(target.target_id))
                self._replication_tasks[target.target_id] = task
            
            logger.info("Replication target added: %s", target.target_id)
            return True
            
        except Exception as e:
            logger.error("Failed to add replication target %s: %s", target.target_id, e)
            return False
    
    def remove_target(self, target_id: str):
        """Supprime une cible de réplication"""        if target_id in self.targets:
            # Arrêt de la tâche
            if target_id in self._replication_tasks:
                self._replication_tasks[target_id].cancel()
                del self._replication_tasks[target_id]
            
            # Déconnexion du connecteur
            if target_id in self.connectors:
                asyncio.create_task(self.connectors[target_id].disconnect())
                del self.connectors[target_id]
            
            # Nettoyage
            del self.targets[target_id]
            if target_id in self.replication_queues:
                del self.replication_queues[target_id]
            
            logger.info("Replication target removed: %s", target_id)
    
    def _create_connector(self, target: ReplicationTarget) -> Optional[ReplicationConnector]:
        """Crée le connecteur approprié pour une cible"""        connector_types = {
            "database": DatabaseReplicationConnector,
            "postgres": DatabaseReplicationConnector,
            "api": APIReplicationConnector,
            "rest": APIReplicationConnector,
            "websocket": WebSocketReplicationConnector,
            "ws": WebSocketReplicationConnector,
            "redis": RedisReplicationConnector
        }
        
        connector_class = connector_types.get(target.type.lower())
        if connector_class:
            return connector_class(target)
        
        logger.error("Unknown connector type: %s", target.type)
        return None
    
    async def _handle_event_for_replication(self, event: Event):
        """Gère la réplication d'un événement"""        if not self._replicating:
            return
        
        # Filtrage des événements selon les cibles
        for target_id, target in self.targets.items():
            if not target.enabled:
                continue
            
            # Vérification des filtres
            if self._event_matches_filters(event, target.filters):
                await self._queue_event_for_target(event, target_id, target)
    
    def _event_matches_filters(self, event: Event, filters: Dict[str, Any]) -> bool:
        """Vérifie si un événement correspond aux filtres"""        if not filters:
            return True
        
        # Filtres par type d'événement
        if "event_types" in filters:
            event_types = filters["event_types"]
            if not any(event.type.startswith(et) for et in event_types):
                return False
        
        # Filtres par tenant
        if "tenant_ids" in filters:
            tenant_ids = filters["tenant_ids"]
            if event.tenant_id not in tenant_ids:
                return False
        
        # Filtres par priorité
        if "min_priority" in filters:
            min_priority = EventPriority(filters["min_priority"])
            event_priority_order = list(EventPriority)
            if event_priority_order.index(event.priority) > event_priority_order.index(min_priority):
                return False
        
        # Filtres personnalisés
        if "custom" in filters:
            custom_filters = filters["custom"]
            for key, expected_value in custom_filters.items():
                if key in event.data and event.data[key] != expected_value:
                    return False
                elif key in event.metadata and event.metadata[key] != expected_value:
                    return False
        
        return True
    
    async def _queue_event_for_target(self, event: Event, target_id: str, target: ReplicationTarget):
        """Met en queue un événement pour une cible"""        try:
            if target.replication_strategy == ReplicationStrategy.SYNCHRONOUS:
                # Réplication synchrone immédiate
                await self._replicate_event_to_target(event, target_id)
            else:
                # Réplication asynchrone via queue
                queue = self.replication_queues.get(target_id)
                if queue:
                    priority = self._get_event_priority_value(event.priority)
                    await queue.put((priority, event))
        
        except Exception as e:
            logger.error("Failed to queue event %s for target %s: %s",
                        event.id, target_id, e)
    
    def _get_event_priority_value(self, priority: EventPriority) -> int:
        """Convertit la priorité en valeur numérique pour la queue"""        priority_values = {
            EventPriority.CRITICAL: 0,
            EventPriority.HIGH: 1,
            EventPriority.NORMAL: 2,
            EventPriority.LOW: 3
        }
        return priority_values.get(priority, 2)
    
    async def _replication_loop(self):
        """Boucle principale de réplication"""        while self._replicating:
            try:
                # Traitement de la queue de priorité
                try:
                    priority, event, target_id = await asyncio.wait_for(
                        self.priority_queue.get(), timeout=1.0
                    )
                    await self._replicate_event_to_target(event, target_id)
                except asyncio.TimeoutError:
                    pass
                
                await asyncio.sleep(0.1)  # Petit délai pour éviter la surcharge
                
            except Exception as e:
                logger.error("Error in replication loop: %s", e)
                await asyncio.sleep(1)
    
    async def _replicate_to_target(self, target_id: str):
        """Tâche de réplication pour une cible spécifique"""        target = self.targets[target_id]
        connector = self.connectors[target_id]
        queue = self.replication_queues[target_id]
        
        # Connexion initiale
        connected = await connector.connect()
        if not connected:
            logger.error("Failed to connect to replication target %s", target_id)
            return
        
        batch = []
        last_batch_time = time.time()
        
        while self._replicating:
            try:
                # Récupération des événements avec timeout
                try:
                    priority, event = await asyncio.wait_for(queue.get(), timeout=1.0)
                    batch.append(event)
                except asyncio.TimeoutError:
                    pass
                
                # Traitement par batch
                current_time = time.time()
                should_process = (
                    len(batch) >= self.config["batch_size"] or
                    (batch and current_time - last_batch_time >= self.config["sync_interval"])
                )
                
                if should_process:
                    await self._process_batch(batch, target_id, connector)
                    batch.clear()
                    last_batch_time = current_time
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error("Error in target replication loop %s: %s", target_id, e)
                await asyncio.sleep(5)
    
    async def _process_batch(
        self,
        events: List[Event],
        target_id: str,
        connector: ReplicationConnector
    ):
        """Traite un batch d'événements"""        target = self.targets[target_id]
        
        for event in events:
            log = ReplicationLog(target_id=target_id, event_id=event.id)
            self.replication_logs[log.log_id] = log
            
            try:
                log.status = ReplicationStatus.IN_PROGRESS
                
                # Vérification de conflit si nécessaire
                if target.conflict_resolution != ConflictResolution.SOURCE_WINS:
                    conflict = await self._detect_conflict(event, target_id, connector)
                    if conflict:
                        await self._handle_conflict(conflict, event, target_id)
                        continue
                
                # Réplication
                success = await connector.replicate_event(event)
                
                if success:
                    log.status = ReplicationStatus.COMPLETED
                    log.completed_at = datetime.now(timezone.utc)
                    target.last_sync = log.completed_at
                    self.stats["events_replicated"] += 1
                else:
                    await self._handle_replication_failure(log, event, target_id)
                
            except Exception as e:
                log.error_message = str(e)
                await self._handle_replication_failure(log, event, target_id)
    
    async def _detect_conflict(
        self,
        event: Event,
        target_id: str,
        connector: ReplicationConnector
    ) -> Optional[ConflictRecord]:
        """Détecte les conflits de réplication"""        # Implémentation simplifiée - peut être étendue
        try:
            # Vérification si l'événement existe déjà avec des données différentes
            if hasattr(connector, 'get_event'):
                existing_event = await connector.get_event(event.id)
                if existing_event:
                    # Comparaison des checksums
                    current_checksum = self._calculate_event_checksum(event)
                    existing_checksum = self._calculate_event_checksum(existing_event)
                    
                    if current_checksum != existing_checksum:
                        conflict = ConflictRecord(
                            event_id=event.id,
                            target_id=target_id,
                            source_event=event.to_dict(),
                            target_event=existing_event.to_dict(),
                            conflict_type="data"
                        )
                        self.conflict_records[conflict.conflict_id] = conflict
                        self.stats["conflicts_detected"] += 1
                        return conflict
        
        except Exception as e:
            logger.error("Error detecting conflict for event %s: %s", event.id, e)
        
        return None
    
    def _calculate_event_checksum(self, event: Event) -> str:
        """Calcule le checksum d'un événement"""        event_str = json.dumps(event.to_dict(), sort_keys=True)
        return hashlib.sha256(event_str.encode()).hexdigest()
    
    async def _handle_conflict(self, conflict: ConflictRecord, event: Event, target_id: str):
        """Gère un conflit de réplication"""        target = self.targets[target_id]
        resolution = target.conflict_resolution
        
        try:
            if resolution == ConflictResolution.LATEST_WINS:
                # Le plus récent gagne
                source_time = event.timestamp
                target_time = datetime.fromisoformat(conflict.target_event["timestamp"])
                
                if source_time >= target_time:
                    conflict.resolved_event = event.to_dict()
                else:
                    conflict.resolved_event = conflict.target_event
                    
            elif resolution == ConflictResolution.SOURCE_WINS:
                # La source gagne toujours
                conflict.resolved_event = event.to_dict()
                
            elif resolution == ConflictResolution.MANUAL:
                # Résolution manuelle - marquage pour intervention
                logger.warning("Manual conflict resolution required for event %s", event.id)
                return
                
            elif resolution == ConflictResolution.CUSTOM:
                # Logique personnalisée
                conflict.resolved_event = await self._custom_conflict_resolution(conflict, event)
            
            conflict.resolved_at = datetime.now(timezone.utc)
            conflict.resolution_strategy = resolution
            self.stats["conflicts_resolved"] += 1
            
            logger.info("Conflict resolved for event %s using strategy %s",
                       event.id, resolution.value)
            
        except Exception as e:
            logger.error("Failed to resolve conflict for event %s: %s", event.id, e)
    
    async def _custom_conflict_resolution(
        self,
        conflict: ConflictRecord,
        event: Event
    ) -> Dict[str, Any]:
        """Logique personnalisée de résolution de conflits"""        # Implémentation par défaut - peut être surchargée
        return event.to_dict()
    
    async def _handle_replication_failure(
        self,
        log: ReplicationLog,
        event: Event,
        target_id: str
    ):
        """Gère les échecs de réplication"""        target = self.targets[target_id]
        retry_policy = target.retry_policy
        
        log.retry_count += 1
        
        if log.retry_count <= retry_policy.get("max_retries", 3):
            # Retry avec délai exponentiel
            delay = retry_policy.get("retry_delay", 5)
            if retry_policy.get("exponential_backoff", True):
                delay *= (2 ** (log.retry_count - 1))
            
            log.status = ReplicationStatus.FAILED
            self.stats["replication_failures"] += 1
            
            # Requeue pour retry
            await asyncio.sleep(delay)
            queue = self.replication_queues.get(target_id)
            if queue:
                priority = self._get_event_priority_value(event.priority)
                await queue.put((priority, event))
        else:
            # Échec définitif
            log.status = ReplicationStatus.FAILED
            log.completed_at = datetime.now(timezone.utc)
            self.stats["replication_failures"] += 1
            
            logger.error("Replication failed permanently for event %s to target %s",
                        event.id, target_id)
    
    async def _replicate_event_to_target(self, event: Event, target_id: str):
        """Réplique un événement vers une cible spécifique"""        if target_id not in self.connectors:
            return
        
        connector = self.connectors[target_id]
        target = self.targets[target_id]
        
        log = ReplicationLog(target_id=target_id, event_id=event.id)
        self.replication_logs[log.log_id] = log
        
        try:
            log.status = ReplicationStatus.IN_PROGRESS
            success = await connector.replicate_event(event)
            
            if success:
                log.status = ReplicationStatus.COMPLETED
                log.completed_at = datetime.now(timezone.utc)
                target.last_sync = log.completed_at
                self.stats["events_replicated"] += 1
            else:
                await self._handle_replication_failure(log, event, target_id)
                
        except Exception as e:
            log.error_message = str(e)
            await self._handle_replication_failure(log, event, target_id)
    
    async def _health_check_loop(self):
        """Boucle de vérification de santé des cibles"""        while self._replicating:
            try:
                healthy_count = 0
                unhealthy_count = 0
                
                for target_id, connector in self.connectors.items():
                    try:
                        is_healthy = await connector.health_check()
                        if is_healthy:
                            healthy_count += 1
                        else:
                            unhealthy_count += 1
                            logger.warning("Replication target %s is unhealthy", target_id)
                            
                            # Tentative de reconnexion
                            await connector.disconnect()
                            await asyncio.sleep(1)
                            await connector.connect()
                            
                    except Exception as e:
                        unhealthy_count += 1
                        logger.error("Health check failed for target %s: %s", target_id, e)
                
                self.stats["targets_healthy"] = healthy_count
                self.stats["targets_unhealthy"] = unhealthy_count
                
                await asyncio.sleep(self.config["health_check_interval"])
                
            except Exception as e:
                logger.error("Error in health check loop: %s", e)
                await asyncio.sleep(5)
    
    async def _sync_loop(self):
        """Boucle de synchronisation incrémentale"""        while self._replicating:
            try:
                for target_id, target in self.targets.items():
                    if (target.replication_type == ReplicationType.INCREMENTAL and
                        target.enabled):
                        await self._perform_incremental_sync(target_id)
                
                await asyncio.sleep(self.config["sync_interval"])
                
            except Exception as e:
                logger.error("Error in sync loop: %s", e)
                await asyncio.sleep(5)
    
    async def _perform_incremental_sync(self, target_id: str):
        """Effectue une synchronisation incrémentale"""        target = self.targets[target_id]
        connector = self.connectors[target_id]
        
        try:
            # Récupération du dernier timestamp répliqué
            last_sync = target.last_sync or await connector.get_last_event_timestamp()
            if not last_sync:
                last_sync = datetime.now(timezone.utc) - timedelta(hours=1)
            
            # Récupération des événements depuis le dernier sync
            if self.event_store:
                events = await self.event_store.get_events_since(last_sync)
                for event in events:
                    if self._event_matches_filters(event, target.filters):
                        await self._queue_event_for_target(event, target_id, target)
            
        except Exception as e:
            logger.error("Incremental sync failed for target %s: %s", target_id, e)
    
    def get_replication_status(self) -> Dict[str, Any]:
        """Retourne le statut de réplication"""        return {
            "replicating": self._replicating,
            "targets": len(self.targets),
            "active_connections": len([c for c in self.connectors.values() 
                                     if asyncio.create_task(c.health_check())]),
            "stats": self.stats.copy(),
            "queue_sizes": {tid: q.qsize() for tid, q in self.replication_queues.items()},
            "conflicts": {
                "active": len([c for c in self.conflict_records.values() 
                             if c.resolved_at is None]),
                "resolved": len([c for c in self.conflict_records.values() 
                               if c.resolved_at is not None])
            }
        }
    
    def get_target_status(self, target_id: str) -> Optional[Dict[str, Any]]:
        """Retourne le statut d'une cible"""        if target_id not in self.targets:
            return None
        
        target = self.targets[target_id]
        connector = self.connectors[target_id]
        
        return {
            "target": target.to_dict(),
            "queue_size": self.replication_queues[target_id].qsize(),
            "recent_logs": [
                log.to_dict() for log in self.replication_logs.values()
                if log.target_id == target_id
            ][-10:],  # Derniers 10 logs
            "health": asyncio.create_task(connector.health_check())
        }


# Instance globale
event_replication_manager: Optional[EventReplicationManager] = None


def initialize_replication_manager(
    event_bus: EventBus,
    event_store: Optional[EventStore] = None,
    redis_client: Optional[redis.Redis] = None
) -> EventReplicationManager:
    """Initialise le gestionnaire de réplication"""    global event_replication_manager
    
    if event_replication_manager is None:
        event_replication_manager = EventReplicationManager(
            event_bus, event_store, redis_client
        )
        logger.info("EventReplicationManager initialized")
    
    return event_replication_manager
