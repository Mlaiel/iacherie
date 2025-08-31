"""Content Protection Database Connections - IA Influencer Agent Platform

Specialized database connections for content protection operations:
- Content fingerprint storage and retrieval
- Protection alert management
- Cross-platform monitoring coordination
- Evidence collection and storage
- Legal compliance data handling

Business Logic:
Content Upload → Fingerprint Generation → Multi-DB Storage → 
Platform Monitoring → Alert Generation → Evidence Collection → Legal Action

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple, Union
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import base64

from .postgresql import PostgreSQLConnectionHandler
from .mongodb import MongoDBConnectionHandler
from .redis import RedisConnectionHandler
from .vector_stores import VectorStoreConnectionHandler
from .object_storage import ObjectStorageConnectionHandler
from .elasticsearch import ElasticsearchConnectionHandler


logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Supported content types for protection"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED_MEDIA = "mixed_media"


class ProtectionStatus(Enum):
    """Content protection status"""    ACTIVE = "active"
    SUSPENDED = "suspended"
    VIOLATION_DETECTED = "violation_detected"
    TAKEDOWN_REQUESTED = "takedown_requested"
    RESOLVED = "resolved"


class AlertPriority(Enum):
    """Protection alert priority levels"""    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ContentFingerprint:
    """Content fingerprint data structure"""    fingerprint_id: str
    tenant_id: str
    content_type: ContentType
    original_filename: str
    file_hash: str
    ai_fingerprint: bytes
    vector_embedding: List[float]
    metadata: Dict[str, Any]
    created_at: datetime
    protection_status: ProtectionStatus = ProtectionStatus.ACTIVE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""        return {
            "fingerprint_id": self.fingerprint_id,
            "tenant_id": self.tenant_id,
            "content_type": self.content_type.value,
            "original_filename": self.original_filename,
            "file_hash": self.file_hash,
            "ai_fingerprint": base64.b64encode(self.ai_fingerprint).decode(),
            "vector_embedding": self.vector_embedding,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "protection_status": self.protection_status.value
        }


@dataclass 
class ProtectionAlert:
    """Protection alert data structure"""    alert_id: str
    fingerprint_id: str
    tenant_id: str
    detected_url: str
    platform: str
    similarity_score: float
    alert_priority: AlertPriority
    evidence_urls: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""        return {
            "alert_id": self.alert_id,
            "fingerprint_id": self.fingerprint_id, 
            "tenant_id": self.tenant_id,
            "detected_url": self.detected_url,
            "platform": self.platform,
            "similarity_score": self.similarity_score,
            "alert_priority": self.alert_priority.value,
            "evidence_urls": self.evidence_urls,
            "metadata": self.metadata,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }


class ContentProtectionConnections:
    """    Specialized connection manager for content protection operations.
    
    Coordinates multiple databases for:
    - Fingerprint storage (PostgreSQL + Vector DB)
    - Alert management (PostgreSQL + Redis)
    - Evidence collection (Object Storage + MongoDB)
    - Search and discovery (Elasticsearch)
    - Real-time monitoring (Redis + WebSockets)
    """    
    def __init__(self, connection_handlers: Dict[str, Any]):
        self.logger = logging.getLogger(__name__)
        
        # Database connection handlers
        self.postgresql = connection_handlers.get("postgresql")
        self.mongodb = connection_handlers.get("mongodb")
        self.redis = connection_handlers.get("redis")
        self.vector_store = connection_handlers.get("vector_store")
        self.object_storage = connection_handlers.get("object_storage")
        self.elasticsearch = connection_handlers.get("elasticsearch")
        
        # Validate required connections
        required_handlers = ["postgresql", "mongodb", "redis", "vector_store"]
        for handler_name in required_handlers:
            if not connection_handlers.get(handler_name):
                raise ValueError(f"Required connection handler missing: {handler_name}")
        
        # Protection operation stats
        self.operations_count = 0
        self.fingerprints_stored = 0
        self.alerts_generated = 0
        self.evidence_collected = 0
        
        # Cache for frequently accessed data
        self.tenant_cache: Dict[str, Dict[str, Any]] = {}
        self.fingerprint_cache: Dict[str, ContentFingerprint] = {}
    
    async def store_content_fingerprint(
        self,
        tenant_id: str,
        content_type: ContentType,
        original_filename: str,
        file_content: bytes,
        ai_fingerprint: bytes,
        vector_embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """        Store content fingerprint across multiple databases for protection.
        
        Args:
            tenant_id: Content creator tenant ID
            content_type: Type of content being protected
            original_filename: Original file name
            file_content: Raw file content for storage
            ai_fingerprint: AI-generated fingerprint
            vector_embedding: Vector representation for similarity search
            metadata: Additional content metadata
            
        Returns:
            Fingerprint ID for tracking
        """        try:
            # Generate unique fingerprint ID
            fingerprint_id = self._generate_fingerprint_id(tenant_id, file_content)
            
            # Calculate file hash
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            # Create fingerprint object
            fingerprint = ContentFingerprint(
                fingerprint_id=fingerprint_id,
                tenant_id=tenant_id,
                content_type=content_type,
                original_filename=original_filename,
                file_hash=file_hash,
                ai_fingerprint=ai_fingerprint,
                vector_embedding=vector_embedding,
                metadata=metadata or {},
                created_at=datetime.utcnow()
            )
            
            # Store in multiple databases using transaction
            async with self._protection_transaction(tenant_id) as tx:
                # 1. Store metadata in PostgreSQL
                await self._store_fingerprint_metadata(tx.postgresql, fingerprint)
                
                # 2. Store vector embedding in vector database
                await self._store_vector_embedding(tx.vector_store, fingerprint)
                
                # 3. Store full content in object storage
                await self._store_content_file(tx.object_storage, fingerprint, file_content)
                
                # 4. Index in Elasticsearch for search
                if self.elasticsearch:
                    await self._index_content_metadata(tx.elasticsearch, fingerprint)
                
                # 5. Cache fingerprint data in Redis
                await self._cache_fingerprint_data(tx.redis, fingerprint)
                
                # Commit transaction
                await tx.commit()
            
            # Update statistics
            self.fingerprints_stored += 1
            self.operations_count += 1
            
            # Cache fingerprint object
            self.fingerprint_cache[fingerprint_id] = fingerprint
            
            self.logger.info(f"Stored content fingerprint {fingerprint_id} for tenant {tenant_id}")
            return fingerprint_id
            
        except Exception as e:
            self.logger.error(f"Failed to store content fingerprint: {e}")
            raise
    
    async def search_similar_content(
        self,
        tenant_id: str,
        query_vector: List[float],
        similarity_threshold: float = 0.85,
        max_results: int = 100
    ) -> List[Tuple[str, float]]:
        """        Search for similar content using vector similarity.
        
        Args:
            tenant_id: Tenant ID for isolation
            query_vector: Query vector for similarity search
            similarity_threshold: Minimum similarity score
            max_results: Maximum number of results
            
        Returns:
            List of (fingerprint_id, similarity_score) tuples
        """        try:
            # Perform vector similarity search
            similar_vectors = await self.vector_store.similarity_search(
                query_vector=query_vector,
                namespace=f"tenant_{tenant_id}",
                top_k=max_results,
                threshold=similarity_threshold
            )
            
            # Filter and format results
            results = []
            for vector_id, score in similar_vectors:
                if score >= similarity_threshold:
                    results.append((vector_id, score))
            
            self.logger.info(f"Found {len(results)} similar content items for tenant {tenant_id}")
            return results
            
        except Exception as e:
            self.logger.error(f"Similar content search failed: {e}")
            raise
    
    async def create_protection_alert(
        self,
        fingerprint_id: str,
        detected_url: str,
        platform: str,
        similarity_score: float,
        evidence_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """        Create protection alert for detected content violation.
        
        Args:
            fingerprint_id: Original content fingerprint ID
            detected_url: URL where violation was detected
            platform: Platform name (youtube, tiktok, etc.)
            similarity_score: Content similarity score
            evidence_data: Evidence data (screenshots, metadata, etc.)
            
        Returns:
            Alert ID for tracking
        """        try:
            # Get fingerprint data
            fingerprint = await self._get_fingerprint_data(fingerprint_id)
            if not fingerprint:
                raise ValueError(f"Fingerprint {fingerprint_id} not found")
            
            # Generate alert ID
            alert_id = self._generate_alert_id(fingerprint_id, detected_url)
            
            # Determine alert priority based on similarity score
            alert_priority = self._calculate_alert_priority(similarity_score, platform)
            
            # Collect evidence if provided
            evidence_urls = []
            if evidence_data:
                evidence_urls = await self._collect_evidence(
                    alert_id, evidence_data, fingerprint.tenant_id
                )
            
            # Create alert object
            alert = ProtectionAlert(
                alert_id=alert_id,
                fingerprint_id=fingerprint_id,
                tenant_id=fingerprint.tenant_id,
                detected_url=detected_url,
                platform=platform,
                similarity_score=similarity_score,
                alert_priority=alert_priority,
                evidence_urls=evidence_urls,
                metadata=evidence_data or {}
            )
            
            # Store alert in databases
            async with self._protection_transaction(fingerprint.tenant_id) as tx:
                # Store in PostgreSQL for persistence
                await self._store_protection_alert(tx.postgresql, alert)
                
                # Cache in Redis for real-time access
                await self._cache_alert_data(tx.redis, alert)
                
                # Index in Elasticsearch for search
                if self.elasticsearch:
                    await self._index_alert_data(tx.elasticsearch, alert)
                
                # Trigger real-time notification
                await self._trigger_alert_notification(tx.redis, alert)
                
                await tx.commit()
            
            # Update statistics
            self.alerts_generated += 1
            self.operations_count += 1
            
            self.logger.info(f"Created protection alert {alert_id} for fingerprint {fingerprint_id}")
            return alert_id
            
        except Exception as e:
            self.logger.error(f"Failed to create protection alert: {e}")
            raise
    
    async def get_tenant_protection_summary(
        self,
        tenant_id: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """        Get comprehensive protection summary for tenant.
        
        Args:
            tenant_id: Tenant ID
            days_back: Number of days to include in summary
            
        Returns:
            Protection summary with metrics and recent activity
        """        try:
            start_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get fingerprint count
            fingerprint_count = await self._get_tenant_fingerprint_count(
                tenant_id, start_date
            )
            
            # Get alert statistics
            alert_stats = await self._get_tenant_alert_statistics(
                tenant_id, start_date
            )
            
            # Get platform distribution
            platform_distribution = await self._get_platform_distribution(
                tenant_id, start_date
            )
            
            # Get recent alerts
            recent_alerts = await self._get_recent_alerts(tenant_id, limit=10)
            
            # Calculate protection effectiveness
            effectiveness_score = await self._calculate_protection_effectiveness(
                tenant_id, start_date
            )
            
            summary = {
                "tenant_id": tenant_id,
                "period_days": days_back,
                "summary_date": datetime.utcnow().isoformat(),
                "metrics": {
                    "total_fingerprints": fingerprint_count,
                    "total_alerts": alert_stats["total"],
                    "pending_alerts": alert_stats["pending"],
                    "resolved_alerts": alert_stats["resolved"],
                    "critical_alerts": alert_stats["critical"],
                    "effectiveness_score": effectiveness_score
                },
                "platform_distribution": platform_distribution,
                "recent_alerts": recent_alerts,
                "protection_status": self._determine_protection_status(alert_stats)
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get protection summary for tenant {tenant_id}: {e}")
            raise
    
    async def update_alert_status(
        self,
        alert_id: str,
        new_status: str,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """        Update protection alert status.
        
        Args:
            alert_id: Alert ID to update
            new_status: New status (resolved, dismissed, escalated, etc.)
            resolution_notes: Optional notes about resolution
            
        Returns:
            True if update successful
        """        try:
            # Get current alert data
            alert_data = await self._get_alert_data(alert_id)
            if not alert_data:
                raise ValueError(f"Alert {alert_id} not found")
            
            # Update status and resolution time
            update_data = {
                "status": new_status,
                "resolved_at": datetime.utcnow().isoformat() if new_status == "resolved" else None,
                "resolution_notes": resolution_notes
            }
            
            # Update in multiple databases
            tenant_id = alert_data["tenant_id"]
            async with self._protection_transaction(tenant_id) as tx:
                # Update PostgreSQL
                await self._update_alert_status_pg(tx.postgresql, alert_id, update_data)
                
                # Update Redis cache
                await self._update_alert_cache(tx.redis, alert_id, update_data)
                
                # Update Elasticsearch index
                if self.elasticsearch:
                    await self._update_alert_index(tx.elasticsearch, alert_id, update_data)
                
                await tx.commit()
            
            self.logger.info(f"Updated alert {alert_id} status to {new_status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update alert status: {e}")
            return False
    
    @asynccontextmanager
    async def _protection_transaction(self, tenant_id: str):
        """Context manager for protection operations transaction."""        # This would implement distributed transaction logic
        # For now, return a simple namespace object
        class TransactionContext:
            def __init__(self, handlers):
                self.postgresql = handlers["postgresql"]
                self.mongodb = handlers["mongodb"]
                self.redis = handlers["redis"]
                self.vector_store = handlers["vector_store"]
                self.object_storage = handlers["object_storage"]
                self.elasticsearch = handlers.get("elasticsearch")
            
            async def commit(self):
                """Commit transaction across all database connections"""                try:
                    # PostgreSQL commit
                    if hasattr(self.postgresql, 'commit'):
                        await self.postgresql.commit()
                    
                    # MongoDB doesn't have traditional transactions in older versions
                    # but we can use sessions for newer versions
                    if hasattr(self.mongodb, 'commit_transaction'):
                        await self.mongodb.commit_transaction()
                    
                    # Redis operations are atomic by default, no explicit commit needed
                    # Vector store commit (if supported)
                    if hasattr(self.vector_store, 'commit'):
                        await self.vector_store.commit()
                    
                    # Elasticsearch commit/refresh
                    if self.elasticsearch and hasattr(self.elasticsearch, 'indices'):
                        await self.elasticsearch.indices.refresh(index='_all')
                        
                    logger.info("🔒 Content protection transaction committed successfully")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to commit content protection transaction: {e}")
                    await self.rollback()
                    raise
            
            async def rollback(self):
                """Rollback transaction across all database connections"""                try:
                    # PostgreSQL rollback
                    if hasattr(self.postgresql, 'rollback'):
                        await self.postgresql.rollback()
                    
                    # MongoDB rollback
                    if hasattr(self.mongodb, 'abort_transaction'):
                        await self.mongodb.abort_transaction()
                    
                    # Redis operations are harder to rollback - we'd need to implement
                    # compensating transactions or save states
                    if hasattr(self.redis, 'discard'):
                        await self.redis.discard()
                    
                    # Vector store rollback (if supported)
                    if hasattr(self.vector_store, 'rollback'):
                        await self.vector_store.rollback()
                    
                    logger.warning("↩️ Content protection transaction rolled back")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to rollback content protection transaction: {e}")
                    # Log the error but don't raise to avoid masking original error
        
        tx = TransactionContext({
            "postgresql": self.postgresql,
            "mongodb": self.mongodb,
            "redis": self.redis,
            "vector_store": self.vector_store,
            "object_storage": self.object_storage,
            "elasticsearch": self.elasticsearch
        })
        
        try:
            yield tx
        except Exception:
            await tx.rollback()
            raise
    
    def _generate_fingerprint_id(self, tenant_id: str, file_content: bytes) -> str:
        """Generate unique fingerprint ID."""        content_hash = hashlib.sha256(file_content).hexdigest()[:16]
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"fp_{tenant_id}_{timestamp}_{content_hash}"
    
    def _generate_alert_id(self, fingerprint_id: str, detected_url: str) -> str:
        """Generate unique alert ID."""        url_hash = hashlib.md5(detected_url.encode()).hexdigest()[:8]
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"alert_{fingerprint_id}_{timestamp}_{url_hash}"
    
    def _calculate_alert_priority(self, similarity_score: float, platform: str) -> AlertPriority:
        """Calculate alert priority based on similarity and platform."""        if similarity_score >= 0.95:
            return AlertPriority.CRITICAL
        elif similarity_score >= 0.90:
            return AlertPriority.HIGH
        elif similarity_score >= 0.80:
            return AlertPriority.MEDIUM
        else:
            return AlertPriority.LOW
    
    async def _store_fingerprint_metadata(self, pg_handler, fingerprint: ContentFingerprint):
        """Store fingerprint metadata in PostgreSQL."""        query = """        INSERT INTO content_fingerprints (
            fingerprint_id, tenant_id, content_type, original_filename,
            file_hash, ai_fingerprint, metadata, created_at, protection_status
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """        await pg_handler.execute_query(
            query,
            fingerprint.fingerprint_id,
            fingerprint.tenant_id,
            fingerprint.content_type.value,
            fingerprint.original_filename,
            fingerprint.file_hash,
            base64.b64encode(fingerprint.ai_fingerprint).decode(),
            json.dumps(fingerprint.metadata),
            fingerprint.created_at,
            fingerprint.protection_status.value
        )
    
    async def _store_vector_embedding(self, vector_handler, fingerprint: ContentFingerprint):
        """Store vector embedding in vector database."""        await vector_handler.store_vector(
            vector_id=fingerprint.fingerprint_id,
            vector=fingerprint.vector_embedding,
            namespace=f"tenant_{fingerprint.tenant_id}",
            metadata={"content_type": fingerprint.content_type.value}
        )
    
    async def _store_content_file(self, storage_handler, fingerprint: ContentFingerprint, content: bytes):
        """Store original content file in object storage."""        file_key = f"fingerprints/{fingerprint.tenant_id}/{fingerprint.fingerprint_id}"
        await storage_handler.put_object(file_key, content)
    
    async def _cache_fingerprint_data(self, redis_handler, fingerprint: ContentFingerprint):
        """Cache fingerprint data in Redis."""        cache_key = f"fingerprint:{fingerprint.fingerprint_id}"
        await redis_handler.set(cache_key, json.dumps(fingerprint.to_dict()), expire=86400)
    
    async def _store_protection_alert(self, pg_handler, alert: ProtectionAlert):
        """Store protection alert in PostgreSQL."""        query = """        INSERT INTO protection_alerts (
            alert_id, fingerprint_id, tenant_id, detected_url, platform,
            similarity_score, alert_priority, evidence_urls, metadata, 
            status, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        """        await pg_handler.execute_query(
            query,
            alert.alert_id,
            alert.fingerprint_id,
            alert.tenant_id,
            alert.detected_url,
            alert.platform,
            alert.similarity_score,
            alert.alert_priority.value,
            json.dumps(alert.evidence_urls),
            json.dumps(alert.metadata),
            alert.status,
            alert.created_at
        )
    
    # Additional helper methods would be implemented here for:
    # - _cache_alert_data
    # - _index_content_metadata  
    # - _index_alert_data
    # - _trigger_alert_notification
    # - _collect_evidence
    # - _get_fingerprint_data
    # - _get_alert_data
    # - _get_tenant_fingerprint_count
    # - _get_tenant_alert_statistics
    # - _get_platform_distribution
    # - _get_recent_alerts
    # - _calculate_protection_effectiveness
    # - _determine_protection_status
    # - _update_alert_status_pg
    # - _update_alert_cache
    # - _update_alert_index
    
    async def get_protection_metrics(self) -> Dict[str, Any]:
        """Get protection operation metrics."""        return {
            "operations_count": self.operations_count,
            "fingerprints_stored": self.fingerprints_stored,
            "alerts_generated": self.alerts_generated,
            "evidence_collected": self.evidence_collected,
            "cached_fingerprints": len(self.fingerprint_cache),
            "cached_tenants": len(self.tenant_cache)
        }
