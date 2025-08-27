"""
Content Protection Replication Handler - IA Influencer Agent Platform

Specialized replication handler for content protection data including:
- Audio/Video/Image fingerprints
- Copyright violation detection results
- Content creator rights management
- Automated takedown notices
- Revenue tracking and distribution

This module ensures real-time replication of critical content protection
data across multiple regions to enable instant global protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional, List, Set, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import uuid
import numpy as np
from pathlib import Path
import aiofiles
import aioredis
import motor.motor_asyncio
from elasticsearch import AsyncElasticsearch

from .config import ReplicationConfig
from .utils import ReplicationUtils


class ContentType(Enum):
    """Types of content for protection"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED_MEDIA = "mixed_media"


class ProtectionLevel(Enum):
    """Content protection levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class ViolationStatus(Enum):
    """Status of violation detection"""
    DETECTED = "detected"
    UNDER_REVIEW = "under_review"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    TAKEDOWN_ISSUED = "takedown_issued"
    RESOLVED = "resolved"


@dataclass
class ContentFingerprint:
    """Content fingerprint data structure"""
    id: str
    user_id: str
    content_type: ContentType
    fingerprint_hash: str
    vector_embedding: Optional[np.ndarray]
    metadata: Dict[str, Any]
    protection_level: ProtectionLevel
    created_at: datetime
    updated_at: datetime
    region: str = "global"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content_type": self.content_type.value,
            "fingerprint_hash": self.fingerprint_hash,
            "vector_embedding": self.vector_embedding.tolist() if self.vector_embedding is not None else None,
            "metadata": self.metadata,
            "protection_level": self.protection_level.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "region": self.region
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentFingerprint':
        """Create from dictionary"""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            content_type=ContentType(data["content_type"]),
            fingerprint_hash=data["fingerprint_hash"],
            vector_embedding=np.array(data["vector_embedding"]) if data.get("vector_embedding") else None,
            metadata=data["metadata"],
            protection_level=ProtectionLevel(data["protection_level"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            region=data.get("region", "global")
        )


@dataclass
class ViolationAlert:
    """Violation detection alert"""
    id: str
    fingerprint_id: str
    violation_url: str
    platform: str
    similarity_score: float
    status: ViolationStatus
    evidence: Dict[str, Any]
    detected_at: datetime
    reviewed_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    region: str = "global"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "fingerprint_id": self.fingerprint_id,
            "violation_url": self.violation_url,
            "platform": self.platform,
            "similarity_score": self.similarity_score,
            "status": self.status.value,
            "evidence": self.evidence,
            "detected_at": self.detected_at.isoformat(),
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "region": self.region
        }


@dataclass
class RevenueTrackingEntry:
    """Revenue tracking entry for content monetization"""
    id: str
    user_id: str
    content_id: str
    platform: str
    revenue_amount: float
    currency: str
    period_start: datetime
    period_end: datetime
    status: str
    created_at: datetime
    region: str = "global"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content_id": self.content_id,
            "platform": self.platform,
            "revenue_amount": self.revenue_amount,
            "currency": self.currency,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "region": self.region
        }


class ContentProtectionReplicationHandler:
    """
    Specialized replication handler for content protection data.
    
    Manages real-time replication of:
    - Content fingerprints across regions
    - Violation detection alerts
    - Revenue tracking data
    - Content creator rights information
    - Automated protection policies
    """
    
    def __init__(self, config: Dict[str, Any], replication_config: ReplicationConfig):
        """
        Initialize content protection replication handler.
        
        Args:
            config: Content protection specific configuration
            replication_config: Global replication configuration
        """
        self.config = config
        self.replication_config = replication_config
        self.logger = logging.getLogger(f"{__name__}.ContentProtectionReplicationHandler")
        self.utils = ReplicationUtils(replication_config)
        
        # Database connections
        self.redis_primary: Optional[aioredis.Redis] = None
        self.redis_secondaries: List[aioredis.Redis] = []
        self.mongodb_primary: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.mongodb_secondaries: List[motor.motor_asyncio.AsyncIOMotorClient] = []
        self.elasticsearch_primary: Optional[AsyncElasticsearch] = None
        self.elasticsearch_secondaries: List[AsyncElasticsearch] = []
        
        # Collections and indices
        self.fingerprint_collection = "content_fingerprints"
        self.violation_collection = "violation_alerts"
        self.revenue_collection = "revenue_tracking"
        self.fingerprint_index = "ia_fingerprints"
        self.violation_index = "ia_violations"
        
        # Configuration
        self.sync_interval = config.get("sync_interval", 30)  # seconds
        self.batch_size = config.get("batch_size", 100)
        self.priority_regions = config.get("priority_regions", ["eu-west-1", "us-east-1"])
        self.encryption_enabled = config.get("encryption_enabled", True)
        
        # State tracking
        self.is_running = False
        self.last_sync_time: Optional[datetime] = None
        self.replication_tasks: List[asyncio.Task] = []
        self.pending_fingerprints: Set[str] = set()
        self.pending_violations: Set[str] = set()
        
        # Metrics
        self.metrics = {
            "fingerprints_replicated": 0,
            "violations_replicated": 0,
            "revenue_entries_replicated": 0,
            "replication_lag_ms": 0,
            "last_sync_duration_ms": 0,
            "error_count": 0,
            "successful_syncs": 0
        }
        
        self.logger.info("ContentProtectionReplicationHandler initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize content protection replication handler.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("Initializing content protection replication handler...")
            
            # Initialize database connections
            await self._initialize_redis_connections()
            await self._initialize_mongodb_connections()
            await self._initialize_elasticsearch_connections()
            
            # Setup collections and indices
            await self._setup_collections()
            await self._setup_indices()
            
            # Validate connections
            await self._validate_connections()
            
            self.logger.info("Content protection replication handler initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize content protection replication handler: {e}")
            return False
    
    async def _initialize_redis_connections(self) -> None:
        """Initialize Redis connections for real-time data"""
        try:
            # Primary Redis connection
            primary_config = self.config.get("redis", {}).get("primary", {})
            if primary_config:
                self.redis_primary = await aioredis.from_url(
                    f"redis://{primary_config['host']}:{primary_config['port']}",
                    password=primary_config.get("password"),
                    db=primary_config.get("db", 0),
                    encoding="utf-8",
                    decode_responses=True
                )
                
                # Test connection
                await self.redis_primary.ping()
                self.logger.info("Primary Redis connection established")
            
            # Secondary Redis connections
            secondary_configs = self.config.get("redis", {}).get("secondaries", [])
            for idx, secondary_config in enumerate(secondary_configs):
                try:
                    redis_client = await aioredis.from_url(
                        f"redis://{secondary_config['host']}:{secondary_config['port']}",
                        password=secondary_config.get("password"),
                        db=secondary_config.get("db", 0),
                        encoding="utf-8",
                        decode_responses=True
                    )
                    
                    # Test connection
                    await redis_client.ping()
                    self.redis_secondaries.append(redis_client)
                    self.logger.info(f"Secondary Redis connection {idx} established")
                    
                except Exception as e:
                    self.logger.warning(f"Failed to connect to secondary Redis {idx}: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Redis connections: {e}")
            raise
    
    async def _initialize_mongodb_connections(self) -> None:
        """Initialize MongoDB connections for document storage"""
        try:
            # Primary MongoDB connection
            primary_config = self.config.get("mongodb", {}).get("primary", {})
            if primary_config:
                primary_uri = f"mongodb://{primary_config.get('username')}:{primary_config.get('password')}@{primary_config['host']}:{primary_config['port']}/{primary_config['database']}"
                self.mongodb_primary = motor.motor_asyncio.AsyncIOMotorClient(primary_uri)
                
                # Test connection
                await self.mongodb_primary.admin.command('ping')
                self.logger.info("Primary MongoDB connection established")
            
            # Secondary MongoDB connections
            secondary_configs = self.config.get("mongodb", {}).get("secondaries", [])
            for idx, secondary_config in enumerate(secondary_configs):
                try:
                    secondary_uri = f"mongodb://{secondary_config.get('username')}:{secondary_config.get('password')}@{secondary_config['host']}:{secondary_config['port']}/{secondary_config['database']}"
                    mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(secondary_uri)
                    
                    # Test connection
                    await mongodb_client.admin.command('ping')
                    self.mongodb_secondaries.append(mongodb_client)
                    self.logger.info(f"Secondary MongoDB connection {idx} established")
                    
                except Exception as e:
                    self.logger.warning(f"Failed to connect to secondary MongoDB {idx}: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MongoDB connections: {e}")
            raise
    
    async def _initialize_elasticsearch_connections(self) -> None:
        """Initialize Elasticsearch connections for search and indexing"""
        try:
            # Primary Elasticsearch connection
            primary_config = self.config.get("elasticsearch", {}).get("primary", {})
            if primary_config:
                primary_hosts = [
                    {
                        "host": primary_config["host"],
                        "port": primary_config["port"],
                        "use_ssl": primary_config.get("use_ssl", True),
                        "verify_certs": primary_config.get("verify_certs", True)
                    }
                ]
                
                self.elasticsearch_primary = AsyncElasticsearch(
                    hosts=primary_hosts,
                    http_auth=(primary_config.get("username"), primary_config.get("password")),
                    timeout=30,
                    max_retries=3,
                    retry_on_timeout=True
                )
                
                # Test connection
                health = await self.elasticsearch_primary.cluster.health()
                self.logger.info(f"Primary Elasticsearch connection established - Status: {health['status']}")
            
            # Secondary Elasticsearch connections
            secondary_configs = self.config.get("elasticsearch", {}).get("secondaries", [])
            for idx, secondary_config in enumerate(secondary_configs):
                try:
                    secondary_hosts = [
                        {
                            "host": secondary_config["host"],
                            "port": secondary_config["port"],
                            "use_ssl": secondary_config.get("use_ssl", True),
                            "verify_certs": secondary_config.get("verify_certs", True)
                        }
                    ]
                    
                    es_client = AsyncElasticsearch(
                        hosts=secondary_hosts,
                        http_auth=(secondary_config.get("username"), secondary_config.get("password")),
                        timeout=30,
                        max_retries=3,
                        retry_on_timeout=True
                    )
                    
                    # Test connection
                    await es_client.cluster.health()
                    self.elasticsearch_secondaries.append(es_client)
                    self.logger.info(f"Secondary Elasticsearch connection {idx} established")
                    
                except Exception as e:
                    self.logger.warning(f"Failed to connect to secondary Elasticsearch {idx}: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Elasticsearch connections: {e}")
            raise
    
    async def _setup_collections(self) -> None:
        """Setup MongoDB collections for content protection data"""
        try:
            if not self.mongodb_primary:
                return
            
            db = self.mongodb_primary[self.config.get("mongodb", {}).get("primary", {}).get("database", "ia_influencer")]
            
            # Create collections if they don't exist
            collections = await db.list_collection_names()
            
            if self.fingerprint_collection not in collections:
                await db.create_collection(self.fingerprint_collection)
                
                # Create indices for fingerprints
                await db[self.fingerprint_collection].create_index([
                    ("user_id", 1),
                    ("content_type", 1),
                    ("created_at", -1)
                ])
                await db[self.fingerprint_collection].create_index("fingerprint_hash", unique=True)
                await db[self.fingerprint_collection].create_index("region")
                
                self.logger.info(f"Created collection: {self.fingerprint_collection}")
            
            if self.violation_collection not in collections:
                await db.create_collection(self.violation_collection)
                
                # Create indices for violations
                await db[self.violation_collection].create_index([
                    ("fingerprint_id", 1),
                    ("detected_at", -1)
                ])
                await db[self.violation_collection].create_index("platform")
                await db[self.violation_collection].create_index("status")
                await db[self.violation_collection].create_index("region")
                
                self.logger.info(f"Created collection: {self.violation_collection}")
            
            if self.revenue_collection not in collections:
                await db.create_collection(self.revenue_collection)
                
                # Create indices for revenue tracking
                await db[self.revenue_collection].create_index([
                    ("user_id", 1),
                    ("period_start", -1)
                ])
                await db[self.revenue_collection].create_index("content_id")
                await db[self.revenue_collection].create_index("platform")
                await db[self.revenue_collection].create_index("region")
                
                self.logger.info(f"Created collection: {self.revenue_collection}")
            
        except Exception as e:
            self.logger.error(f"Failed to setup MongoDB collections: {e}")
            raise
    
    async def _setup_indices(self) -> None:
        """Setup Elasticsearch indices for search functionality"""
        try:
            if not self.elasticsearch_primary:
                return
            
            # Fingerprint index mapping
            fingerprint_mapping = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                        "content_type": {"type": "keyword"},
                        "fingerprint_hash": {"type": "keyword"},
                        "vector_embedding": {"type": "dense_vector", "dims": 512},
                        "metadata": {"type": "object"},
                        "protection_level": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"},
                        "region": {"type": "keyword"}
                    }
                },
                "settings": {
                    "number_of_shards": 3,
                    "number_of_replicas": 2,
                    "refresh_interval": "5s"
                }
            }
            
            # Create fingerprint index
            if not await self.elasticsearch_primary.indices.exists(index=self.fingerprint_index):
                await self.elasticsearch_primary.indices.create(
                    index=self.fingerprint_index,
                    body=fingerprint_mapping
                )
                self.logger.info(f"Created Elasticsearch index: {self.fingerprint_index}")
            
            # Violation index mapping
            violation_mapping = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "fingerprint_id": {"type": "keyword"},
                        "violation_url": {"type": "text"},
                        "platform": {"type": "keyword"},
                        "similarity_score": {"type": "float"},
                        "status": {"type": "keyword"},
                        "evidence": {"type": "object"},
                        "detected_at": {"type": "date"},
                        "reviewed_at": {"type": "date"},
                        "resolved_at": {"type": "date"},
                        "region": {"type": "keyword"}
                    }
                },
                "settings": {
                    "number_of_shards": 2,
                    "number_of_replicas": 1,
                    "refresh_interval": "1s"  # Faster refresh for violations
                }
            }
            
            # Create violation index
            if not await self.elasticsearch_primary.indices.exists(index=self.violation_index):
                await self.elasticsearch_primary.indices.create(
                    index=self.violation_index,
                    body=violation_mapping
                )
                self.logger.info(f"Created Elasticsearch index: {self.violation_index}")
            
        except Exception as e:
            self.logger.error(f"Failed to setup Elasticsearch indices: {e}")
            raise
    
    async def _validate_connections(self) -> None:
        """Validate all database connections"""
        try:
            # Validate Redis
            if self.redis_primary:
                await self.redis_primary.ping()
            
            # Validate MongoDB
            if self.mongodb_primary:
                await self.mongodb_primary.admin.command('ping')
            
            # Validate Elasticsearch
            if self.elasticsearch_primary:
                await self.elasticsearch_primary.cluster.health()
            
            self.logger.info("All database connections validated successfully")
            
        except Exception as e:
            self.logger.error(f"Connection validation failed: {e}")
            raise
    
    async def start_replication(
        self, 
        source_config: Dict[str, Any], 
        target_config: Dict[str, Any], 
        mode: str = "real_time"
    ) -> bool:
        """
        Start content protection replication.
        
        Args:
            source_config: Source configuration
            target_config: Target configuration
            mode: Replication mode (real_time, batch, hybrid)
            
        Returns:
            bool: True if replication started successfully
        """
        try:
            self.logger.info(f"Starting content protection replication in {mode} mode")
            
            if self.is_running:
                self.logger.warning("Replication already running")
                return True
            
            self.is_running = True
            
            # Start replication tasks based on mode
            if mode == "real_time":
                self.replication_tasks = [
                    asyncio.create_task(self._real_time_fingerprint_sync()),
                    asyncio.create_task(self._real_time_violation_sync()),
                    asyncio.create_task(self._real_time_revenue_sync()),
                    asyncio.create_task(self._health_monitor())
                ]
            elif mode == "batch":
                self.replication_tasks = [
                    asyncio.create_task(self._batch_sync_all_data()),
                    asyncio.create_task(self._health_monitor())
                ]
            elif mode == "hybrid":
                self.replication_tasks = [
                    asyncio.create_task(self._real_time_fingerprint_sync()),
                    asyncio.create_task(self._real_time_violation_sync()),
                    asyncio.create_task(self._batch_revenue_sync()),
                    asyncio.create_task(self._health_monitor())
                ]
            else:
                raise ValueError(f"Unsupported replication mode: {mode}")
            
            self.logger.info(f"Content protection replication started with {len(self.replication_tasks)} tasks")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start content protection replication: {e}")
            self.is_running = False
            return False
    
    async def _real_time_fingerprint_sync(self) -> None:
        """Real-time synchronization of content fingerprints"""
        while self.is_running:
            try:
                # Check for new/updated fingerprints
                await self._sync_pending_fingerprints()
                
                # Small delay for real-time processing
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error in real-time fingerprint sync: {e}")
                self.metrics["error_count"] += 1
                await asyncio.sleep(5)
    
    async def _real_time_violation_sync(self) -> None:
        """Real-time synchronization of violation alerts"""
        while self.is_running:
            try:
                # Check for new/updated violations
                await self._sync_pending_violations()
                
                # Small delay for real-time processing
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error in real-time violation sync: {e}")
                self.metrics["error_count"] += 1
                await asyncio.sleep(5)
    
    async def _real_time_revenue_sync(self) -> None:
        """Real-time synchronization of revenue tracking data"""
        while self.is_running:
            try:
                # Sync revenue data (less frequent than fingerprints/violations)
                await self._sync_revenue_data()
                
                # Longer delay for revenue data
                await asyncio.sleep(self.sync_interval)
                
            except Exception as e:
                self.logger.error(f"Error in real-time revenue sync: {e}")
                self.metrics["error_count"] += 1
                await asyncio.sleep(30)
    
    async def _health_monitor(self) -> None:
        """Monitor replication health and update metrics"""
        while self.is_running:
            try:
                start_time = datetime.utcnow()
                
                # Check connection health
                await self._check_connection_health()
                
                # Update metrics
                self.last_sync_time = datetime.utcnow()
                
                # Calculate sync duration
                sync_duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                self.metrics["last_sync_duration_ms"] = sync_duration
                
                # Log health status
                if self.metrics["error_count"] == 0:
                    self.metrics["successful_syncs"] += 1
                
                await asyncio.sleep(30)  # Health check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(30)
    
    async def _sync_pending_fingerprints(self) -> None:
        """Sync pending fingerprints to secondary stores"""
        if not self.pending_fingerprints:
            return
        
        fingerprint_ids = list(self.pending_fingerprints)[:self.batch_size]
        self.pending_fingerprints -= set(fingerprint_ids)
        
        for fingerprint_id in fingerprint_ids:
            try:
                # Get fingerprint from primary store
                fingerprint_data = await self._get_fingerprint_from_primary(fingerprint_id)
                
                if fingerprint_data:
                    # Replicate to secondary stores
                    await self._replicate_fingerprint_to_secondaries(fingerprint_data)
                    self.metrics["fingerprints_replicated"] += 1
                
            except Exception as e:
                self.logger.error(f"Error syncing fingerprint {fingerprint_id}: {e}")
                self.metrics["error_count"] += 1
    
    async def _sync_pending_violations(self) -> None:
        """Sync pending violations to secondary stores"""
        if not self.pending_violations:
            return
        
        violation_ids = list(self.pending_violations)[:self.batch_size]
        self.pending_violations -= set(violation_ids)
        
        for violation_id in violation_ids:
            try:
                # Get violation from primary store
                violation_data = await self._get_violation_from_primary(violation_id)
                
                if violation_data:
                    # Replicate to secondary stores
                    await self._replicate_violation_to_secondaries(violation_data)
                    self.metrics["violations_replicated"] += 1
                
            except Exception as e:
                self.logger.error(f"Error syncing violation {violation_id}: {e}")
                self.metrics["error_count"] += 1
    
    async def add_content_fingerprint(self, fingerprint: ContentFingerprint) -> bool:
        """
        Add new content fingerprint and trigger replication.
        
        Args:
            fingerprint: Content fingerprint to add
            
        Returns:
            bool: True if added successfully
        """
        try:
            # Store in primary databases
            await self._store_fingerprint_primary(fingerprint)
            
            # Add to pending replication
            self.pending_fingerprints.add(fingerprint.id)
            
            self.logger.info(f"Added content fingerprint: {fingerprint.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add content fingerprint: {e}")
            return False
    
    async def add_violation_alert(self, violation: ViolationAlert) -> bool:
        """
        Add new violation alert and trigger urgent replication.
        
        Args:
            violation: Violation alert to add
            
        Returns:
            bool: True if added successfully
        """
        try:
            # Store in primary databases
            await self._store_violation_primary(violation)
            
            # Add to pending replication with high priority
            self.pending_violations.add(violation.id)
            
            # Trigger immediate replication for critical violations
            if violation.similarity_score > 0.95:
                await self._replicate_violation_immediate(violation)
            
            self.logger.info(f"Added violation alert: {violation.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add violation alert: {e}")
            return False
    
    async def get_replication_metrics(self) -> Dict[str, Any]:
        """
        Get content protection replication metrics.
        
        Returns:
            Dict containing replication metrics
        """
        try:
            # Calculate replication lag
            if self.last_sync_time:
                lag_ms = (datetime.utcnow() - self.last_sync_time).total_seconds() * 1000
                self.metrics["replication_lag_ms"] = lag_ms
            
            # Add runtime metrics
            self.metrics.update({
                "is_running": self.is_running,
                "active_tasks": len(self.replication_tasks),
                "pending_fingerprints": len(self.pending_fingerprints),
                "pending_violations": len(self.pending_violations),
                "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None
            })
            
            return self.metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get replication metrics: {e}")
            return self.metrics
    
    async def stop_replication(self, graceful: bool = True) -> bool:
        """
        Stop content protection replication.
        
        Args:
            graceful: Whether to perform graceful shutdown
            
        Returns:
            bool: True if stopped successfully
        """
        try:
            self.logger.info(f"Stopping content protection replication (graceful={graceful})")
            
            self.is_running = False
            
            if graceful:
                # Process pending items
                await self._sync_pending_fingerprints()
                await self._sync_pending_violations()
            
            # Cancel all tasks
            for task in self.replication_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            self.replication_tasks.clear()
            
            self.logger.info("Content protection replication stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop content protection replication: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the content protection replication handler"""
        try:
            self.logger.info("Shutting down content protection replication handler...")
            
            # Stop replication
            await self.stop_replication(graceful=True)
            
            # Close database connections
            if self.redis_primary:
                await self.redis_primary.close()
            
            for redis_client in self.redis_secondaries:
                await redis_client.close()
            
            if self.mongodb_primary:
                self.mongodb_primary.close()
            
            for mongodb_client in self.mongodb_secondaries:
                mongodb_client.close()
            
            if self.elasticsearch_primary:
                await self.elasticsearch_primary.close()
            
            for es_client in self.elasticsearch_secondaries:
                await es_client.close()
            
            self.logger.info("Content protection replication handler shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    # Helper methods (simplified implementations)
    async def _get_fingerprint_from_primary(self, fingerprint_id: str) -> Optional[Dict[str, Any]]:
        """Get fingerprint data from primary store"""
        # Implementation would fetch from primary MongoDB
        return None
    
    async def _get_violation_from_primary(self, violation_id: str) -> Optional[Dict[str, Any]]:
        """Get violation data from primary store"""
        # Implementation would fetch from primary MongoDB
        return None
    
    async def _store_fingerprint_primary(self, fingerprint: ContentFingerprint) -> None:
        """Store fingerprint in primary databases"""
        # Implementation would store in MongoDB and Elasticsearch
        pass
    
    async def _store_violation_primary(self, violation: ViolationAlert) -> None:
        """Store violation in primary databases"""
        # Implementation would store in MongoDB and Elasticsearch
        pass
    
    async def _replicate_fingerprint_to_secondaries(self, fingerprint_data: Dict[str, Any]) -> None:
        """Replicate fingerprint to secondary stores"""
        # Implementation would replicate to all secondary stores
        pass
    
    async def _replicate_violation_to_secondaries(self, violation_data: Dict[str, Any]) -> None:
        """Replicate violation to secondary stores"""
        # Implementation would replicate to all secondary stores
        pass
    
    async def _replicate_violation_immediate(self, violation: ViolationAlert) -> None:
        """Immediately replicate critical violation"""
        # Implementation for urgent violation replication
        pass
    
    async def _sync_revenue_data(self) -> None:
        """Sync revenue tracking data"""
        # Implementation for revenue data synchronization
        pass
    
    async def _batch_sync_all_data(self) -> None:
        """Batch synchronization of all data"""
        # Implementation for batch sync mode
        pass
    
    async def _batch_revenue_sync(self) -> None:
        """Batch synchronization of revenue data"""
        # Implementation for batch revenue sync
        pass
    
    async def _check_connection_health(self) -> None:
        """Check health of all database connections"""
        # Implementation for connection health checks
        pass
