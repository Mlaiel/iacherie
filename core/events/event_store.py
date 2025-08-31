"""IA-Influencer-Agent - Event Store System
Module: backend/core/events/event_store.py
Architecture: Event Persistence and Stream Management
Auteur: Fahed Mlaiel <mlaiel@live.de>

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT STRICT ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.

Description:
    Système de stockage d'événements avec persistance, streams, snapshots
    et requêtes avancées pour la plateforme IA-Influencer-Agent.
    Support PostgreSQL et Redis pour performance optimale.
"""from typing import Any, Dict, List, Optional, Union, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod

import asyncpg
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.sql import text

from .event_bus import Event, EventStatus, EventPriority

logger = logging.getLogger(__name__)


class StorageBackend(Enum):
    """Types de backend de stockage"""    POSTGRESQL = "postgresql"
    REDIS = "redis"
    MEMORY = "memory"
    HYBRID = "hybrid"


class StreamDirection(Enum):
    """Direction de lecture des streams"""    FORWARD = "forward"
    BACKWARD = "backward"


@dataclass
class EventStreamCursor:
    """Curseur pour navigation dans les streams"""    stream_id: str
    position: int = 0
    timestamp: Optional[datetime] = None
    event_id: Optional[str] = None
    direction: StreamDirection = StreamDirection.FORWARD
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "stream_id": self.stream_id,
            "position": self.position,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "event_id": self.event_id,
            "direction": self.direction.value
        }


@dataclass
class EventQuery:
    """Requête pour recherche d'événements"""    stream_id: Optional[str] = None
    event_types: Optional[List[str]] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    from_timestamp: Optional[datetime] = None
    to_timestamp: Optional[datetime] = None
    from_position: Optional[int] = None
    to_position: Optional[int] = None
    limit: int = 100
    order_by: str = "timestamp"
    order_direction: str = "ASC"
    include_metadata: bool = True


class EventStoreBackend(ABC):
    """Interface pour les backends de stockage"""    
    @abstractmethod
    async def store_event(self, event: Event, stream_id: str) -> bool:
        """Stocke un événement dans un stream"""        pass
    
    @abstractmethod
    async def get_event(self, event_id: str) -> Optional[Event]:
        """Récupère un événement par ID"""        pass
    
    @abstractmethod
    async def query_events(self, query: EventQuery) -> List[Event]:
        """Recherche d'événements selon une requête"""        pass
    
    @abstractmethod
    async def get_stream_events(
        self, 
        stream_id: str, 
        from_position: int = 0, 
        limit: int = 100
    ) -> List[Event]:
        """Récupère les événements d'un stream"""        pass
    
    @abstractmethod
    async def get_stream_info(self, stream_id: str) -> Dict[str, Any]:
        """Informations sur un stream"""        pass


class PostgreSQLEventStore(EventStoreBackend):
    """Backend PostgreSQL pour stockage d'événements"""    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.engine = None
        self.pool = None
    
    async def initialize(self):
        """Initialise la connexion PostgreSQL"""        try:
            self.engine = create_async_engine(self.connection_string)
            self.pool = await asyncpg.create_pool(self.connection_string)
            await self._create_tables()
            logger.info("PostgreSQL EventStore initialized")
        except Exception as e:
            logger.error("Failed to initialize PostgreSQL EventStore: %s", e)
            raise
    
    async def _create_tables(self):
        """Crée les tables nécessaires"""        create_events_table = """        CREATE TABLE IF NOT EXISTS events (
            id VARCHAR(36) PRIMARY KEY,
            stream_id VARCHAR(255) NOT NULL,
            event_type VARCHAR(255) NOT NULL,
            event_source VARCHAR(255) NOT NULL,
            event_subject VARCHAR(255) NOT NULL,
            event_data JSONB NOT NULL,
            event_metadata JSONB NOT NULL DEFAULT '{}',
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            priority VARCHAR(20) NOT NULL DEFAULT 'normal',
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            user_id VARCHAR(36),
            tenant_id VARCHAR(36),
            correlation_id VARCHAR(36),
            causation_id VARCHAR(36),
            version INTEGER NOT NULL DEFAULT 1,
            position BIGSERIAL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_events_stream_id ON events(stream_id);
        CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
        CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
        CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);
        CREATE INDEX IF NOT EXISTS idx_events_tenant_id ON events(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_events_position ON events(position);
        
        CREATE TABLE IF NOT EXISTS event_streams (
            stream_id VARCHAR(255) PRIMARY KEY,
            stream_type VARCHAR(100) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_event_at TIMESTAMP WITH TIME ZONE,
            event_count BIGINT DEFAULT 0,
            metadata JSONB DEFAULT '{}'
        );
        """        
        async with self.pool.acquire() as conn:
            await conn.execute(create_events_table)
    
    async def store_event(self, event: Event, stream_id: str) -> bool:
        """Stocke un événement dans PostgreSQL"""        try:
            insert_event = """            INSERT INTO events (
                id, stream_id, event_type, event_source, event_subject,
                event_data, event_metadata, timestamp, priority, status,
                user_id, tenant_id, correlation_id, causation_id, version
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            """            
            update_stream = """            INSERT INTO event_streams (stream_id, stream_type, last_event_at, event_count)
            VALUES ($1, $2, $3, 1)
            ON CONFLICT (stream_id) 
            DO UPDATE SET 
                last_event_at = $3,
                event_count = event_streams.event_count + 1
            """            
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(
                        insert_event,
                        event.id, stream_id, event.type, event.source, event.subject,
                        json.dumps(event.data), json.dumps(event.metadata),
                        event.timestamp, event.priority.value, event.status.value,
                        event.user_id, event.tenant_id, event.correlation_id,
                        event.causation_id, event.version
                    )
                    
                    stream_type = event.type.split('.')[0] if '.' in event.type else 'unknown'
                    await conn.execute(
                        update_stream,
                        stream_id, stream_type, event.timestamp
                    )
            
            return True
            
        except Exception as e:
            logger.error("Failed to store event %s: %s", event.id, e)
            return False
    
    async def get_event(self, event_id: str) -> Optional[Event]:
        """Récupère un événement par ID"""        try:
            query = """            SELECT id, event_type, event_source, event_subject, event_data,
                   event_metadata, timestamp, priority, status, user_id,
                   tenant_id, correlation_id, causation_id, version
            FROM events WHERE id = $1
            """            
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, event_id)
                
                if not row:
                    return None
                
                return Event(
                    id=row['id'],
                    type=row['event_type'],
                    source=row['event_source'],
                    subject=row['event_subject'],
                    data=json.loads(row['event_data']),
                    metadata=json.loads(row['event_metadata']),
                    timestamp=row['timestamp'],
                    priority=EventPriority(row['priority']),
                    status=EventStatus(row['status']),
                    user_id=row['user_id'],
                    tenant_id=row['tenant_id'],
                    correlation_id=row['correlation_id'],
                    causation_id=row['causation_id'],
                    version=row['version']
                )
                
        except Exception as e:
            logger.error("Failed to get event %s: %s", event_id, e)
            return None
    
    async def query_events(self, query: EventQuery) -> List[Event]:
        """Recherche d'événements selon une requête"""        try:
            # Construction de la requête SQL
            sql_parts = ["SELECT * FROM events WHERE 1=1"]
            params = []
            param_count = 0
            
            if query.stream_id:
                param_count += 1
                sql_parts.append(f"AND stream_id = ${param_count}")
                params.append(query.stream_id)
            
            if query.event_types:
                param_count += 1
                type_conditions = " OR ".join([f"event_type LIKE ${param_count}"])
                sql_parts.append(f"AND ({type_conditions})")
                params.append(f"%{query.event_types[0]}%")
            
            if query.user_id:
                param_count += 1
                sql_parts.append(f"AND user_id = ${param_count}")
                params.append(query.user_id)
            
            if query.tenant_id:
                param_count += 1
                sql_parts.append(f"AND tenant_id = ${param_count}")
                params.append(query.tenant_id)
            
            if query.from_timestamp:
                param_count += 1
                sql_parts.append(f"AND timestamp >= ${param_count}")
                params.append(query.from_timestamp)
            
            if query.to_timestamp:
                param_count += 1
                sql_parts.append(f"AND timestamp <= ${param_count}")
                params.append(query.to_timestamp)
            
            # Ordre et limite
            sql_parts.append(f"ORDER BY {query.order_by} {query.order_direction}")
            param_count += 1
            sql_parts.append(f"LIMIT ${param_count}")
            params.append(query.limit)
            
            sql_query = " ".join(sql_parts)
            
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(sql_query, *params)
                
                events = []
                for row in rows:
                    event = Event(
                        id=row['id'],
                        type=row['event_type'],
                        source=row['event_source'],
                        subject=row['event_subject'],
                        data=json.loads(row['event_data']),
                        metadata=json.loads(row['event_metadata']),
                        timestamp=row['timestamp'],
                        priority=EventPriority(row['priority']),
                        status=EventStatus(row['status']),
                        user_id=row['user_id'],
                        tenant_id=row['tenant_id'],
                        correlation_id=row['correlation_id'],
                        causation_id=row['causation_id'],
                        version=row['version']
                    )
                    events.append(event)
                
                return events
                
        except Exception as e:
            logger.error("Failed to query events: %s", e)
            return []
    
    async def get_stream_events(
        self, 
        stream_id: str, 
        from_position: int = 0, 
        limit: int = 100
    ) -> List[Event]:
        """Récupère les événements d'un stream"""        query = EventQuery(
            stream_id=stream_id,
            from_position=from_position,
            limit=limit,
            order_by="position",
            order_direction="ASC"
        )
        return await self.query_events(query)
    
    async def get_stream_info(self, stream_id: str) -> Dict[str, Any]:
        """Informations sur un stream"""        try:
            query = """            SELECT stream_type, created_at, last_event_at, event_count, metadata
            FROM event_streams WHERE stream_id = $1
            """            
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, stream_id)
                
                if not row:
                    return {}
                
                return {
                    "stream_id": stream_id,
                    "stream_type": row['stream_type'],
                    "created_at": row['created_at'],
                    "last_event_at": row['last_event_at'],
                    "event_count": row['event_count'],
                    "metadata": json.loads(row['metadata'])
                }
                
        except Exception as e:
            logger.error("Failed to get stream info for %s: %s", stream_id, e)
            return {}


class EventStream:
    """Stream d'événements avec curseur et navigation"""    
    def __init__(
        self,
        stream_id: str,
        store: "EventStore",
        buffer_size: int = 100
    ):
        self.stream_id = stream_id
        self.store = store
        self.buffer_size = buffer_size
        self._cursor = EventStreamCursor(stream_id)
        self._buffer: List[Event] = []
        self._buffer_position = 0
    
    async def read_forward(
        self, 
        count: int = 10,
        from_position: Optional[int] = None
    ) -> List[Event]:
        """Lit les événements vers l'avant"""        if from_position is not None:
            self._cursor.position = from_position
        
        events = await self.store.get_stream_events(
            self.stream_id,
            self._cursor.position,
            count
        )
        
        if events:
            self._cursor.position += len(events)
            self._cursor.timestamp = events[-1].timestamp
            self._cursor.event_id = events[-1].id
        
        return events
    
    async def read_backward(
        self, 
        count: int = 10,
        from_position: Optional[int] = None
    ) -> List[Event]:
        """Lit les événements vers l'arrière"""        # Implementation simplifiée - nécessiterait optimisation pour production
        if from_position is not None:
            self._cursor.position = from_position
        
        start_pos = max(0, self._cursor.position - count)
        events = await self.store.get_stream_events(
            self.stream_id,
            start_pos,
            self._cursor.position - start_pos
        )
        
        if events:
            self._cursor.position = start_pos
            self._cursor.timestamp = events[0].timestamp
            self._cursor.event_id = events[0].id
        
        return list(reversed(events))
    
    async def append(self, event: Event) -> bool:
        """Ajoute un événement au stream"""        return await self.store.store_event(event, self.stream_id)
    
    def get_cursor(self) -> EventStreamCursor:
        """Retourne le curseur actuel"""        return self._cursor
    
    def set_cursor(self, cursor: EventStreamCursor):
        """Définit le curseur"""        if cursor.stream_id != self.stream_id:
            raise ValueError("Cursor stream_id must match stream_id")
        self._cursor = cursor


class EventStore:
    """    Système principal de stockage d'événements
    """    
    def __init__(
        self,
        backend: EventStoreBackend,
        enable_caching: bool = True,
        cache_ttl: int = 300
    ):
        self.backend = backend
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
        # Statistiques
        self._stats = {
            "events_stored": 0,
            "events_retrieved": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "streams_created": 0
        }
    
    async def store_event(self, event: Event, stream_id: str) -> bool:
        """Stocke un événement"""        success = await self.backend.store_event(event, stream_id)
        
        if success:
            self._stats["events_stored"] += 1
            # Invalidation cache
            self._invalidate_cache(f"stream:{stream_id}")
            self._invalidate_cache(f"event:{event.id}")
        
        return success
    
    async def get_event(self, event_id: str) -> Optional[Event]:
        """Récupère un événement par ID"""        cache_key = f"event:{event_id}"
        
        # Vérification cache
        if self.enable_caching and self._is_cache_valid(cache_key):
            self._stats["cache_hits"] += 1
            return self._cache[cache_key]
        
        # Récupération depuis backend
        event = await self.backend.get_event(event_id)
        
        if event:
            self._stats["events_retrieved"] += 1
            if self.enable_caching:
                self._cache[cache_key] = event
                self._cache_timestamps[cache_key] = datetime.now(timezone.utc)
            self._stats["cache_misses"] += 1
        
        return event
    
    async def query_events(self, query: EventQuery) -> List[Event]:
        """Recherche d'événements"""        events = await self.backend.query_events(query)
        self._stats["events_retrieved"] += len(events)
        return events
    
    async def get_stream(self, stream_id: str) -> EventStream:
        """Crée ou récupère un stream"""        stream = EventStream(stream_id, self)
        
        # Vérification si le stream existe
        info = await self.backend.get_stream_info(stream_id)
        if not info:
            self._stats["streams_created"] += 1
        
        return stream
    
    async def get_stream_events(
        self, 
        stream_id: str, 
        from_position: int = 0, 
        limit: int = 100
    ) -> List[Event]:
        """Récupère les événements d'un stream"""        return await self.backend.get_stream_events(stream_id, from_position, limit)
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Vérifie si une entrée cache est valide"""        if cache_key not in self._cache:
            return False
        
        timestamp = self._cache_timestamps.get(cache_key)
        if not timestamp:
            return False
        
        age = (datetime.now(timezone.utc) - timestamp).total_seconds()
        return age < self.cache_ttl
    
    def _invalidate_cache(self, cache_key: str):
        """Invalide une entrée cache"""        if cache_key in self._cache:
            del self._cache[cache_key]
            del self._cache_timestamps[cache_key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques"""        return {
            "stats": self._stats.copy(),
            "cache_size": len(self._cache),
            "cache_hit_rate": (
                self._stats["cache_hits"] / 
                max(1, self._stats["cache_hits"] + self._stats["cache_misses"])
            )
        }
