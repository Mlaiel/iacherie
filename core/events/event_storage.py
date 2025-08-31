"""
IA-Influencer-Agent - Event Storage Management System
Module: backend/core/events/event_storage.py
Architecture: Enterprise Event Persistence & Archival
Auteur: Équipe Backend Senior + ML Engineer + Sécurité + Microservices + DBA + DevOps + IA Prompt Engineer

  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT STRICT 
© 2025 Équipe d'Experts. Tous droits réservés.

SPÉCIALITÉS DE L'ÉQUIPE:
 Lead Dev IA: Architecture & prompt engineering
 Backend Senior: Microservices & performance  
 ML Engineer: Modèles & pipeline d'apprentissage
 DBA Expert: Optimisation & requêtes complexes
 Expert Sécurité: Protection & conformité
 Spécialiste Audio: Traitement signal & formats
 DevOps: Infrastructure & déploiement
 Expert Microservices: Distribution & scalabilité

Description:
    Système de stockage d'événements avec support multi-backend, archivage,
    compression, chiffrement et optimisations de performance.
"""

from typing import Any, Dict, List, Optional, Union, AsyncIterator, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import asyncio
import json
import logging
import uuid
import gzip
import bz2
import lzma
from pathlib import Path
import hashlib
import asyncpg
import aioredis
import motor.motor_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from .event_bus import Event, EventPriority, EventStatus
from .event_types import EventType

logger = logging.getLogger(__name__)


class StorageBackend(Enum):
    """Types de backend de stockage"""
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    MONGODB = "mongodb"
    ELASTICSEARCH = "elasticsearch"
    S3 = "s3"
    FILE_SYSTEM = "filesystem"
    HYBRID = "hybrid"


class CompressionType(Enum):
    """Types de compression"""
    NONE = "none"
    GZIP = "gzip"
    BZIP2 = "bzip2"
    LZMA = "lzma"


class StoragePolicy(Enum):
    """Politiques de stockage"""
    HOT = "hot"          # Accès fréquent, performance maximale
    WARM = "warm"        # Accès occasionnel, équilibre perf/coût
    COLD = "cold"        # Accès rare, optimisation coût
    ARCHIVE = "archive"  # Archivage long terme


@dataclass
class StorageConfiguration:
    """Configuration de stockage"""
    backend: StorageBackend
    connection_string: str
    max_connections: int = 20
    compression: CompressionType = CompressionType.NONE
    encryption_enabled: bool = True
    retention_days: int = 365
    archival_policy: StoragePolicy = StoragePolicy.WARM
    batch_size: int = 1000
    auto_vacuum: bool = True
    replication_factor: int = 1


@dataclass
class StorageMetrics:
    """Métriques de stockage"""
    total_events: int = 0
    storage_size_bytes: int = 0
    compression_ratio: float = 0.0
    avg_write_latency_ms: float = 0.0
    avg_read_latency_ms: float = 0.0
    cache_hit_ratio: float = 0.0
    last_backup_time: Optional[datetime] = None
    storage_utilization: float = 0.0


@dataclass
class EventQuery:
    """Requête d'événements"""
    event_types: Optional[List[EventType]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    status: Optional[EventStatus] = None
    priority: Optional[EventPriority] = None
    limit: int = 100
    offset: int = 0
    sort_by: str = "timestamp"
    sort_order: str = "desc"
    include_metadata: bool = True


@dataclass
class ArchivalRequest:
    """Demande d'archivage"""
    query: EventQuery
    destination: StorageBackend
    compression: CompressionType = CompressionType.GZIP
    encryption: bool = True
    delete_after_archive: bool = False
    retention_metadata: Dict[str, Any] = field(default_factory=dict)


class EventStorageInterface(ABC):
    """Interface pour le stockage d'événements"""
    
    @abstractmethod
    async def store_event(self, event: Event) -> str:
        """Stocker un événement"""
        pass
    
    @abstractmethod
    async def store_events_batch(self, events: List[Event]) -> List[str]:
        """Stocker un lot d'événements"""
        pass
    
    @abstractmethod
    async def get_event(self, event_id: str) -> Optional[Event]:
        """Récupérer un événement par ID"""
        pass
    
    @abstractmethod
    async def query_events(self, query: EventQuery) -> List[Event]:
        """Requête d'événements"""
        pass
    
    @abstractmethod
    async def count_events(self, query: EventQuery) -> int:
        """Compter les événements"""
        pass
    
    @abstractmethod
    async def delete_event(self, event_id: str) -> bool:
        """Supprimer un événement"""
        pass
    
    @abstractmethod
    async def get_storage_metrics(self) -> StorageMetrics:
        """Récupérer les métriques de stockage"""
        pass


class PostgreSQLEventStorage(EventStorageInterface):
    """Stockage PostgreSQL pour événements"""
    
    def __init__(self, config: StorageConfiguration):
        self.config = config
        self.engine = None
        self.session_factory = None
        self.compression_handler = self._get_compression_handler()
        
    async def initialize(self):
        """Initialiser la connexion PostgreSQL"""



        try:
            self.engine = create_async_engine(
                self.config.connection_string,
                pool_size=self.config.max_connections,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=3600
            )
            
            self.session_factory = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
            
            # Création des tables si nécessaire
            await self._create_tables()
            
            logger.info("PostgreSQL storage initialized")
            
        except Exception as e:
            logger.error(f"PostgreSQL initialization failed: {e}")
            raise
    
    async def store_event(self, event: Event) -> str:
        """Stocker un événement"""



        try:
            async with self.session_factory() as session:
                # Sérialisation et compression
                event_data = self._serialize_event(event)
                compressed_data = self._compress_data(event_data)
                
                # Insertion
                query = text("""
                    INSERT INTO events (
                        id, event_type, data, metadata, priority, status,
                        tenant_id, user_id, timestamp, created_at
                    ) VALUES (
                        :id, :event_type, :data, :metadata, :priority, :status,
                        :tenant_id, :user_id, :timestamp, :created_at
                    )
                """)
                
                await session.execute(query, {
                    'id': event.id,
                    'event_type': event.event_type.value,
                    'data': compressed_data,
                    'metadata': json.dumps(event.metadata),
                    'priority': event.priority.value,
                    'status': event.status.value,
                    'tenant_id': event.tenant_id,
                    'user_id': event.user_id,
                    'timestamp': event.timestamp,
                    'created_at': datetime.now(timezone.utc)
                })
                
                await session.commit()
                return event.id
                
        except Exception as e:
            logger.error(f"Event storage failed: {e}")
            raise
    
    async def store_events_batch(self, events: List[Event]) -> List[str]:
        """Stocker un lot d'événements"""



        try:
            async with self.session_factory() as session:
                values = []
                for event in events:
                    event_data = self._serialize_event(event)
                    compressed_data = self._compress_data(event_data)
                    
                    values.append({
                        'id': event.id,
                        'event_type': event.event_type.value,
                        'data': compressed_data,
                        'metadata': json.dumps(event.metadata),
                        'priority': event.priority.value,
                        'status': event.status.value,
                        'tenant_id': event.tenant_id,
                        'user_id': event.user_id,
                        'timestamp': event.timestamp,
                        'created_at': datetime.now(timezone.utc)
                    })
                
                # Insertion en lot
                query = text("""
                    INSERT INTO events (
                        id, event_type, data, metadata, priority, status,
                        tenant_id, user_id, timestamp, created_at
                    ) VALUES (
                        :id, :event_type, :data, :metadata, :priority, :status,
                        :tenant_id, :user_id, :timestamp, :created_at
                    )
                """)
                
                await session.execute(query, values)
                await session.commit()
                
                return [event.id for event in events]
                
        except Exception as e:
            logger.error(f"Batch storage failed: {e}")
            raise
    
    async def get_event(self, event_id: str) -> Optional[Event]:
        """Récupérer un événement par ID"""



        try:
            async with self.session_factory() as session:
                query = text("""
                    SELECT id, event_type, data, metadata, priority, status,
                           tenant_id, user_id, timestamp, created_at
                    FROM events WHERE id = :event_id
                """)
                
                result = await session.execute(query, {'event_id': event_id})
                row = result.fetchone()
                
                if row:
                    return self._deserialize_event(row)
                return None
                
        except Exception as e:
            logger.error(f"Event retrieval failed: {e}")
            return None
    
    async def query_events(self, query: EventQuery) -> List[Event]:
        """Requête d'événements"""



        try:
            async with self.session_factory() as session:
                # Construction de la requête
                sql_query, params = self._build_query(query)
                
                result = await session.execute(sql_query, params)
                rows = result.fetchall()
                
                return [self._deserialize_event(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Event query failed: {e}")
            return []
    
    async def count_events(self, query: EventQuery) -> int:
        """Compter les événements"""



        try:
            async with self.session_factory() as session:
                sql_query, params = self._build_count_query(query)
                
                result = await session.execute(sql_query, params)
                count = result.scalar()
                
                return count or 0
                
        except Exception as e:
            logger.error(f"Event count failed: {e}")
            return 0
    
    async def delete_event(self, event_id: str) -> bool:
        """Supprimer un événement"""



        try:
            async with self.session_factory() as session:
                query = text("DELETE FROM events WHERE id = :event_id")
                result = await session.execute(query, {'event_id': event_id})
                await session.commit()
                
                return result.rowcount > 0
                
        except Exception as e:
            logger.error(f"Event deletion failed: {e}")
            return False
    
    async def get_storage_metrics(self) -> StorageMetrics:
        """Récupérer les métriques de stockage"""



        try:
            async with self.session_factory() as session:
                metrics_query = text("""
                    SELECT 
                        COUNT(*) as total_events,
                        SUM(LENGTH(data)) as total_size
                    FROM events
                """)
                
                result = await session.execute(metrics_query)
                row = result.fetchone()
                
                return StorageMetrics(
                    total_events=row[0] or 0,
                    storage_size_bytes=row[1] or 0,
                    compression_ratio=self._calculate_compression_ratio(),
                    avg_write_latency_ms=0.0,  # À implémenter avec monitoring
                    avg_read_latency_ms=0.0,   # À implémenter avec monitoring
                    cache_hit_ratio=0.0,       # À implémenter avec cache
                    storage_utilization=0.0    # À implémenter
                )
                
        except Exception as e:
            logger.error(f"Metrics retrieval failed: {e}")
            return StorageMetrics()
    
    def _serialize_event(self, event: Event) -> str:
        """Sérialiser un événement"""



        return json.dumps({
            'id': event.id,
            'event_type': event.event_type.value,
            'data': event.data,
            'metadata': event.metadata,
            'priority': event.priority.value,
            'status': event.status.value,
            'tenant_id': event.tenant_id,
            'user_id': event.user_id,
            'timestamp': event.timestamp.isoformat(),
            'retry_count': event.retry_count,
            'max_retries': event.max_retries,
            'correlation_id': event.correlation_id,
            'source': event.source,
            'destination': event.destination,
            'headers': event.headers
        })
    
    def _deserialize_event(self, row: Tuple) -> Event:
        """Désérialiser un événement depuis une ligne de base"""
        data = self._decompress_data(row[2])
        event_dict = json.loads(data)
        
        return Event(
            event_type=EventType(row[1]),
            data=event_dict['data'],
            metadata=json.loads(row[3]),
            priority=EventPriority(row[4]),
            tenant_id=row[6],
            user_id=row[7],
            timestamp=row[8],
            correlation_id=event_dict.get('correlation_id'),
            source=event_dict.get('source'),
            destination=event_dict.get('destination'),
            headers=event_dict.get('headers', {}),
            retry_count=event_dict.get('retry_count', 0),
            max_retries=event_dict.get('max_retries', 3)
        )
    
    def _compress_data(self, data: str) -> bytes:
        """Compresser les données"""
        if self.config.compression == CompressionType.NONE:
            return data.encode('utf-8')
        elif self.config.compression == CompressionType.GZIP:
            return gzip.compress(data.encode('utf-8'))
        elif self.config.compression == CompressionType.BZIP2:
            return bz2.compress(data.encode('utf-8'))
        elif self.config.compression == CompressionType.LZMA:
            return lzma.compress(data.encode('utf-8'))
        else:
            return data.encode('utf-8')
    
    def _decompress_data(self, data: bytes) -> str:
        """Décompresser les données"""
        if self.config.compression == CompressionType.NONE:
            return data.decode('utf-8')
        elif self.config.compression == CompressionType.GZIP:
            return gzip.decompress(data).decode('utf-8')
        elif self.config.compression == CompressionType.BZIP2:
            return bz2.decompress(data).decode('utf-8')
        elif self.config.compression == CompressionType.LZMA:
            return lzma.decompress(data).decode('utf-8')
        else:
            return data.decode('utf-8')
    
    def _get_compression_handler(self):
        """Récupérer le gestionnaire de compression"""



        return {
            CompressionType.GZIP: (gzip.compress, gzip.decompress),
            CompressionType.BZIP2: (bz2.compress, bz2.decompress),
            CompressionType.LZMA: (lzma.compress, lzma.decompress)
        }.get(self.config.compression)
    
    def _calculate_compression_ratio(self) -> float:
        """Calculer le ratio de compression"""
        # À implémenter avec des statistiques réelles
        return 0.75
    
    def _build_query(self, query: EventQuery) -> Tuple[text, Dict[str, Any]]:
        """Construire une requête SQL"""
        conditions = []
        params = {}
        
        base_sql = """
            SELECT id, event_type, data, metadata, priority, status,
                   tenant_id, user_id, timestamp, created_at
            FROM events
        """
        
        if query.event_types:
            conditions.append("event_type = ANY(:event_types)")
            params['event_types'] = [et.value for et in query.event_types]
        
        if query.start_time:
            conditions.append("timestamp >= :start_time")
            params['start_time'] = query.start_time
        
        if query.end_time:
            conditions.append("timestamp <= :end_time")
            params['end_time'] = query.end_time
        
        if query.user_id:
            conditions.append("user_id = :user_id")
            params['user_id'] = query.user_id
        
        if query.tenant_id:
            conditions.append("tenant_id = :tenant_id")
            params['tenant_id'] = query.tenant_id
        
        if query.status:
            conditions.append("status = :status")
            params['status'] = query.status.value
        
        if query.priority:
            conditions.append("priority = :priority")
            params['priority'] = query.priority.value
        
        if conditions:
            base_sql += " WHERE " + " AND ".join(conditions)
        
        base_sql += f" ORDER BY {query.sort_by} {query.sort_order.upper()}"
        base_sql += f" LIMIT {query.limit} OFFSET {query.offset}"
        
        return text(base_sql), params
    
    def _build_count_query(self, query: EventQuery) -> Tuple[text, Dict[str, Any]]:
        """Construire une requête de comptage"""
        conditions = []
        params = {}
        
        base_sql = "SELECT COUNT(*) FROM events"
        
        # Même logique que _build_query pour les conditions
        if query.event_types:
            conditions.append("event_type = ANY(:event_types)")
            params['event_types'] = [et.value for et in query.event_types]
        
        # ... autres conditions similaires
        
        if conditions:
            base_sql += " WHERE " + " AND ".join(conditions)
        
        return text(base_sql), params
    
    async def _create_tables(self):
        """Créer les tables nécessaires"""



        try:
            async with self.session_factory() as session:
                create_table_sql = text("""
                    CREATE TABLE IF NOT EXISTS events (
                        id UUID PRIMARY KEY,
                        event_type VARCHAR(100) NOT NULL,
                        data BYTEA NOT NULL,
                        metadata JSONB,
                        priority VARCHAR(20) NOT NULL,
                        status VARCHAR(20) NOT NULL,
                        tenant_id VARCHAR(100),
                        user_id VARCHAR(100),
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                        CONSTRAINT events_priority_check CHECK (priority IN ('low', 'medium', 'high', 'critical')),
                        CONSTRAINT events_status_check CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled'))
                    )
                """)
                
                # Index pour les performances
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)",
                    "CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type)",
                    "CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id)",
                    "CREATE INDEX IF NOT EXISTS idx_events_tenant_id ON events(tenant_id)",
                    "CREATE INDEX IF NOT EXISTS idx_events_status ON events(status)",
                    "CREATE INDEX IF NOT EXISTS idx_events_composite ON events(event_type, timestamp, status)"
                ]
                
                await session.execute(create_table_sql)
                
                for index_sql in indexes:
                    await session.execute(text(index_sql))
                
                await session.commit()
                logger.info("Event tables and indexes created")
                
        except Exception as e:
            logger.error(f"Table creation failed: {e}")
            raise


class RedisEventStorage(EventStorageInterface):
    """Stockage Redis pour événements (cache/temporaire)"""
    
    def __init__(self, config: StorageConfiguration):
        self.config = config
        self.redis = None
        
    async def initialize(self):
        """Initialiser la connexion Redis"""



        try:
            self.redis = aioredis.from_url(
                self.config.connection_string,
                max_connections=self.config.max_connections,
                retry_on_timeout=True
            )
            
            # Test de connexion
            await self.redis.ping()
            logger.info("Redis storage initialized")
            
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            raise
    
    async def store_event(self, event: Event) -> str:
        """Stocker un événement dans Redis"""



        try:
            event_data = self._serialize_event(event)
            
            # Stockage avec TTL
            ttl = self.config.retention_days * 24 * 3600
            await self.redis.setex(
                f"event:{event.id}",
                ttl,
                event_data
            )
            
            # Index par type
            await self.redis.zadd(
                f"events:{event.event_type.value}",
                {event.id: event.timestamp.timestamp()}
            )
            
            return event.id
            
        except Exception as e:
            logger.error(f"Redis event storage failed: {e}")
            raise
    
    async def store_events_batch(self, events: List[Event]) -> List[str]:
        """Stocker un lot d'événements"""



        try:
            pipe = self.redis.pipeline()
            ttl = self.config.retention_days * 24 * 3600
            
            for event in events:
                event_data = self._serialize_event(event)
                pipe.setex(f"event:{event.id}", ttl, event_data)
                pipe.zadd(
                    f"events:{event.event_type.value}",
                    {event.id: event.timestamp.timestamp()}
                )
            
            await pipe.execute()
            return [event.id for event in events]
            
        except Exception as e:
            logger.error(f"Redis batch storage failed: {e}")
            raise
    
    async def get_event(self, event_id: str) -> Optional[Event]:
        """Récupérer un événement depuis Redis"""



        try:
            event_data = await self.redis.get(f"event:{event_id}")
            if event_data:
                return self._deserialize_event(event_data)
            return None
            
        except Exception as e:
            logger.error(f"Redis event retrieval failed: {e}")
            return None
    
    async def query_events(self, query: EventQuery) -> List[Event]:
        """Requête d'événements depuis Redis"""



        try:
            events = []
            
            if query.event_types:
                for event_type in query.event_types:
                    # Récupération par index temporel
                    min_score = query.start_time.timestamp() if query.start_time else 0
                    max_score = query.end_time.timestamp() if query.end_time else "+inf"
                    
                    event_ids = await self.redis.zrangebyscore(
                        f"events:{event_type.value}",
                        min_score,
                        max_score,
                        offset=query.offset,
                        count=query.limit
                    )
                    
                    for event_id in event_ids:
                        event = await self.get_event(event_id.decode())
                        if event:
                            events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Redis event query failed: {e}")
            return []
    
    async def count_events(self, query: EventQuery) -> int:
        """Compter les événements"""



        try:
            count = 0
            
            if query.event_types:
                for event_type in query.event_types:
                    min_score = query.start_time.timestamp() if query.start_time else 0
                    max_score = query.end_time.timestamp() if query.end_time else "+inf"
                    
                    type_count = await self.redis.zcount(
                        f"events:{event_type.value}",
                        min_score,
                        max_score
                    )
                    count += type_count
            
            return count
            
        except Exception as e:
            logger.error(f"Redis event count failed: {e}")
            return 0
    
    async def delete_event(self, event_id: str) -> bool:
        """Supprimer un événement"""



        try:
            result = await self.redis.delete(f"event:{event_id}")
            return result > 0
            
        except Exception as e:
            logger.error(f"Redis event deletion failed: {e}")
            return False
    
    async def get_storage_metrics(self) -> StorageMetrics:
        """Récupérer les métriques Redis"""



        try:
            info = await self.redis.info("memory")
            keyspace = await self.redis.info("keyspace")
            
            total_events = 0
            for db_info in keyspace.values():
                if isinstance(db_info, dict):
                    total_events += db_info.get('keys', 0)
            
            return StorageMetrics(
                total_events=total_events,
                storage_size_bytes=info.get('used_memory', 0),
                compression_ratio=0.0,
                avg_write_latency_ms=0.0,
                avg_read_latency_ms=0.0,
                cache_hit_ratio=info.get('keyspace_hit_ratio', 0.0),
                storage_utilization=info.get('used_memory_percentage', 0.0)
            )
            
        except Exception as e:
            logger.error(f"Redis metrics retrieval failed: {e}")
            return StorageMetrics()
    
    def _serialize_event(self, event: Event) -> str:
        """Sérialiser un événement"""



        return json.dumps({
            'id': event.id,
            'event_type': event.event_type.value,
            'data': event.data,
            'metadata': event.metadata,
            'priority': event.priority.value,
            'status': event.status.value,
            'tenant_id': event.tenant_id,
            'user_id': event.user_id,
            'timestamp': event.timestamp.isoformat(),
            'retry_count': event.retry_count,
            'max_retries': event.max_retries,
            'correlation_id': event.correlation_id,
            'source': event.source,
            'destination': event.destination,
            'headers': event.headers
        })
    
    def _deserialize_event(self, data: Union[str, bytes]) -> Event:
        """Désérialiser un événement"""
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        
        event_dict = json.loads(data)
        
        return Event(
            event_type=EventType(event_dict['event_type']),
            data=event_dict['data'],
            metadata=event_dict['metadata'],
            priority=EventPriority(event_dict['priority']),
            tenant_id=event_dict['tenant_id'],
            user_id=event_dict['user_id'],
            timestamp=datetime.fromisoformat(event_dict['timestamp'].replace('Z', '+00:00')),
            correlation_id=event_dict.get('correlation_id'),
            source=event_dict.get('source'),
            destination=event_dict.get('destination'),
            headers=event_dict.get('headers', {}),
            retry_count=event_dict.get('retry_count', 0),
            max_retries=event_dict.get('max_retries', 3)
        )


class HybridEventStorage(EventStorageInterface):
    """Stockage hybride combinant plusieurs backends"""
    
    def __init__(self, primary_config: StorageConfiguration, cache_config: StorageConfiguration):
        self.primary_storage = self._create_storage(primary_config)
        self.cache_storage = self._create_storage(cache_config)
        
    async def initialize(self):
        """Initialiser les stockages"""
        await self.primary_storage.initialize()
        await self.cache_storage.initialize()
    
    async def store_event(self, event: Event) -> str:
        """Stocker dans primary et cache"""
        # Stockage primaire
        event_id = await self.primary_storage.store_event(event)
        
        # Cache pour accès rapide
        try:
            await self.cache_storage.store_event(event)
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
        
        return event_id
    
    async def get_event(self, event_id: str) -> Optional[Event]:
        """Récupérer depuis cache puis primary"""
        # Tentative cache d'abord
        event = await self.cache_storage.get_event(event_id)
        if event:
            return event
        
        # Fallback vers stockage primaire
        event = await self.primary_storage.get_event(event_id)
        if event:
            # Mise en cache
            try:
                await self.cache_storage.store_event(event)
            except Exception as e:
                logger.warning(f"Cache update failed: {e}")
        
        return event
    
    async def store_events_batch(self, events: List[Event]) -> List[str]:
        """Déléguer au stockage primaire"""



        return await self.primary_storage.store_events_batch(events)
    
    async def query_events(self, query: EventQuery) -> List[Event]:
        """Déléguer au stockage primaire"""



        return await self.primary_storage.query_events(query)
    
    async def count_events(self, query: EventQuery) -> int:
        """Déléguer au stockage primaire"""



        return await self.primary_storage.count_events(query)
    
    async def delete_event(self, event_id: str) -> bool:
        """Supprimer des deux stockages"""
        primary_deleted = await self.primary_storage.delete_event(event_id)
        
        try:
            await self.cache_storage.delete_event(event_id)
        except Exception as e:
            logger.warning(f"Cache deletion failed: {e}")
        
        return primary_deleted
    
    async def get_storage_metrics(self) -> StorageMetrics:
        """Combiner les métriques"""
        primary_metrics = await self.primary_storage.get_storage_metrics()
        cache_metrics = await self.cache_storage.get_storage_metrics()
        
        return StorageMetrics(
            total_events=primary_metrics.total_events,
            storage_size_bytes=primary_metrics.storage_size_bytes,
            compression_ratio=primary_metrics.compression_ratio,
            avg_write_latency_ms=primary_metrics.avg_write_latency_ms,
            avg_read_latency_ms=primary_metrics.avg_read_latency_ms,
            cache_hit_ratio=cache_metrics.cache_hit_ratio,
            storage_utilization=primary_metrics.storage_utilization
        )
    
    def _create_storage(self, config: StorageConfiguration) -> EventStorageInterface:
        """Factory pour créer un stockage"""
        if config.backend == StorageBackend.POSTGRESQL:
            return PostgreSQLEventStorage(config)
        elif config.backend == StorageBackend.REDIS:
            return RedisEventStorage(config)
        else:
            raise ValueError(f"Unsupported storage backend: {config.backend}")


class EventArchiver:
    """Gestionnaire d'archivage d'événements"""
    
    def __init__(self, source_storage: EventStorageInterface):
        self.source_storage = source_storage
        
    async def archive_events(self, request: ArchivalRequest) -> bool:
        """Archiver des événements"""



        try:
            # Récupération des événements à archiver
            events = await self.source_storage.query_events(request.query)
            
            if not events:
                logger.info("No events to archive")
                return True
            
            # Création du stockage de destination
            destination_storage = self._create_archive_storage(request)
            await destination_storage.initialize()
            
            # Archivage en lots
            batch_size = 1000
            for i in range(0, len(events), batch_size):
                batch = events[i:i + batch_size]
                await destination_storage.store_events_batch(batch)
                
                # Suppression si demandée
                if request.delete_after_archive:
                    for event in batch:
                        await self.source_storage.delete_event(event.id)
            
            logger.info(f"Archived {len(events)} events")
            return True
            
        except Exception as e:
            logger.error(f"Archival failed: {e}")
            return False
    
    def _create_archive_storage(self, request: ArchivalRequest) -> EventStorageInterface:
        """Créer le stockage d'archive"""
        config = StorageConfiguration(
            backend=request.destination,
            connection_string="",  # À configurer selon le backend
            compression=request.compression,
            encryption_enabled=request.encryption
        )
        
        if request.destination == StorageBackend.POSTGRESQL:
            return PostgreSQLEventStorage(config)
        elif request.destination == StorageBackend.REDIS:
            return RedisEventStorage(config)
        else:
            raise ValueError(f"Unsupported archive backend: {request.destination}")


def create_default_storage() -> EventStorageInterface:
    """Créer un stockage par défaut"""
    config = StorageConfiguration(
        backend=StorageBackend.POSTGRESQL,
        connection_string="postgresql://user:pass@localhost/events",
        compression=CompressionType.GZIP,
        encryption_enabled=True,
        retention_days=365
    )
    
    return PostgreSQLEventStorage(config)


def create_hybrid_storage() -> EventStorageInterface:
    """Créer un stockage hybride PostgreSQL + Redis"""
    primary_config = StorageConfiguration(
        backend=StorageBackend.POSTGRESQL,
        connection_string="postgresql://user:pass@localhost/events",
        compression=CompressionType.GZIP,
        encryption_enabled=True
    )
    
    cache_config = StorageConfiguration(
        backend=StorageBackend.REDIS,
        connection_string="redis://localhost:6379/0",
        retention_days=7  # Cache plus court
    )
    
    return HybridEventStorage(primary_config, cache_config)
