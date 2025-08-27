"""
Comprehensive Fingerprint Repository

High-level repository interface for fingerprint data operations with advanced
querying, analytics, and enterprise-grade data management capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union, Set
from dataclasses import dataclass, asdict
from enum import Enum

import numpy as np
from sqlalchemy import and_, or_, func, text, select, update, delete, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from backend.core.database import DatabaseManager
from backend.core.config import settings
from backend.core.exceptions import DatabaseError, ValidationError, NotFoundError
from backend.ai.content_protection.models import ContentFingerprint, FingerprintType
from backend.database.fingerprinting.fingerprint_storage import (
    FingerprintStorageManager, FingerprintStorageModel, FingerprintMatchModel
)
from backend.database.fingerprinting.fingerprint_indexing import FingerprintIndexManager
from backend.database.fingerprinting.fingerprint_matching import FingerprintMatchingEngine, MatchResult
from backend.utils.pagination import PaginationParams, PaginatedResponse
from backend.utils.sorting import SortParams
from backend.utils.filtering import FilterParams
from backend.utils.performance import PerformanceMonitor

logger = logging.getLogger(__name__)


class FingerprintStatus(Enum):
    """Fingerprint status types"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    EXPIRED = "expired"
    DELETED = "deleted"


class SortField(Enum):
    """Available sort fields"""
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    CONFIDENCE_SCORE = "confidence_score"
    SIMILARITY_SCORE = "similarity_score"
    CONTENT_TYPE = "content_type"
    USER_ID = "user_id"


@dataclass
class FingerprintQuery:
    """Comprehensive fingerprint query parameters"""
    user_id: Optional[str] = None
    content_ids: Optional[List[str]] = None
    content_types: Optional[List[str]] = None
    fingerprint_types: Optional[List[str]] = None
    quality_levels: Optional[List[str]] = None
    status: Optional[FingerprintStatus] = None
    
    # Date range filters
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    
    # Score filters
    min_confidence: Optional[float] = None
    max_confidence: Optional[float] = None
    
    # Text search
    search_text: Optional[str] = None
    metadata_search: Optional[Dict[str, Any]] = None
    
    # Hash filters
    primary_hash: Optional[str] = None
    perceptual_hash: Optional[str] = None
    structural_hash: Optional[str] = None
    semantic_hash: Optional[str] = None
    
    # Pagination and sorting
    pagination: Optional[PaginationParams] = None
    sorting: Optional[SortParams] = None
    
    # Advanced options
    include_expired: bool = False
    include_vectors: bool = False
    include_matches: bool = False


@dataclass
class FingerprintStatistics:
    """Comprehensive fingerprint statistics"""
    total_count: int
    active_count: int
    content_type_distribution: Dict[str, int]
    quality_distribution: Dict[str, int]
    average_confidence: float
    creation_trends: Dict[str, int]  # Date -> count
    storage_metrics: Dict[str, Any]
    performance_metrics: Dict[str, Any]


@dataclass
class MatchStatistics:
    """Match operation statistics"""
    total_matches: int
    exact_matches: int
    similar_matches: int
    partial_matches: int
    algorithm_distribution: Dict[str, int]
    average_similarity: float
    processing_time_stats: Dict[str, float]


class FingerprintRepository:
    """
    Comprehensive repository for fingerprint data operations with advanced
    querying, analytics, and enterprise-grade data management.
    """
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        storage_manager: FingerprintStorageManager,
        index_manager: FingerprintIndexManager,
        matching_engine: FingerprintMatchingEngine
    ):
        self.db_manager = db_manager
        self.storage_manager = storage_manager
        self.index_manager = index_manager
        self.matching_engine = matching_engine
        self.logger = logging.getLogger(__name__)
        self.performance_monitor = PerformanceMonitor()
    
    async def create_fingerprint(
        self,
        fingerprint: ContentFingerprint,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new fingerprint with full indexing
        
        Args:
            fingerprint: ContentFingerprint object
            user_id: User identifier
            metadata: Additional metadata
            
        Returns:
            Fingerprint ID
        """
        try:
            # Store fingerprint
            fingerprint_id = await self.storage_manager.store_fingerprint(
                fingerprint, user_id, metadata
            )
            
            # Add to indexes
            embedding_vector = None
            if hasattr(fingerprint, 'embedding_vector'):
                embedding_vector = fingerprint.embedding_vector
            
            await self.index_manager.add_fingerprint_indexes(
                fingerprint, user_id, embedding_vector
            )
            
            self.logger.info(f"Created fingerprint {fingerprint_id} for user {user_id}")
            return fingerprint_id
            
        except Exception as e:
            self.logger.error(f"Failed to create fingerprint: {e}")
            raise DatabaseError(f"Fingerprint creation failed: {e}")
    
    async def get_fingerprint(
        self,
        fingerprint_id: str,
        include_vectors: bool = False,
        include_matches: bool = False
    ) -> Optional[ContentFingerprint]:
        """
        Retrieve a fingerprint by ID
        
        Args:
            fingerprint_id: Fingerprint identifier
            include_vectors: Whether to include vector data
            include_matches: Whether to include match history
            
        Returns:
            ContentFingerprint object or None
        """
        try:
            fingerprint = await self.storage_manager.retrieve_fingerprint(
                fingerprint_id, include_vectors
            )
            
            if fingerprint and include_matches:
                # Add match history to metadata
                matches = await self.get_fingerprint_matches(fingerprint_id)
                if fingerprint.metadata is None:
                    fingerprint.metadata = {}
                fingerprint.metadata['match_history'] = [
                    match.to_dict() for match in matches
                ]
            
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve fingerprint {fingerprint_id}: {e}")
            raise DatabaseError(f"Fingerprint retrieval failed: {e}")
    
    async def query_fingerprints(
        self,
        query: FingerprintQuery
    ) -> PaginatedResponse[ContentFingerprint]:
        """
        Advanced fingerprint querying with complex filters
        
        Args:
            query: FingerprintQuery with all filter parameters
            
        Returns:
            Paginated response with matching fingerprints
        """
        try:
            # Build query conditions
            conditions = self._build_query_conditions(query)
            
            # Get pagination parameters
            pagination = query.pagination or PaginationParams()
            sorting = query.sorting or SortParams(field="created_at", ascending=False)
            
            async with self.db_manager.get_session() as session:
                # Build base query
                base_query = select(FingerprintStorageModel)
                
                # Apply conditions
                if conditions:
                    base_query = base_query.where(and_(*conditions))
                
                # Apply sorting
                sort_field = getattr(FingerprintStorageModel, sorting.field)
                if sorting.ascending:
                    base_query = base_query.order_by(asc(sort_field))
                else:
                    base_query = base_query.order_by(desc(sort_field))
                
                # Get total count
                count_query = select(func.count()).select_from(base_query.subquery())
                count_result = await session.execute(count_query)
                total_count = count_result.scalar()
                
                # Apply pagination
                paginated_query = base_query.limit(pagination.limit).offset(pagination.offset)
                
                # Execute query
                result = await session.execute(paginated_query)
                models = result.scalars().all()
                
                # Convert to ContentFingerprint objects
                fingerprints = []
                for model in models:
                    fingerprint = await self.storage_manager._model_to_fingerprint(
                        model, query.include_vectors
                    )
                    fingerprints.append(fingerprint)
                
                # Return paginated response
                return PaginatedResponse(
                    items=fingerprints,
                    total_count=total_count,
                    page=pagination.page,
                    page_size=pagination.limit,
                    has_next=pagination.offset + len(fingerprints) < total_count,
                    has_previous=pagination.offset > 0
                )
        
        except Exception as e:
            self.logger.error(f"Fingerprint query failed: {e}")
            raise DatabaseError(f"Query execution failed: {e}")
    
    async def search_similar_fingerprints(
        self,
        reference_fingerprint: ContentFingerprint,
        similarity_threshold: float = 0.7,
        max_results: int = 50,
        user_id: Optional[str] = None
    ) -> List[Tuple[ContentFingerprint, float]]:
        """
        Search for similar fingerprints using the matching engine
        
        Args:
            reference_fingerprint: Fingerprint to search for
            similarity_threshold: Minimum similarity score
            max_results: Maximum results to return
            user_id: Optional user filter
            
        Returns:
            List of (fingerprint, similarity_score) tuples
        """
        try:
            # Find matches using the matching engine
            match_results = await self.matching_engine.find_matches(
                reference_fingerprint,
                user_id=user_id,
                max_results=max_results
            )
            
            # Filter by similarity threshold
            filtered_matches = [
                match for match in match_results
                if match.similarity_score >= similarity_threshold
            ]
            
            # Retrieve full fingerprint objects
            similar_fingerprints = []
            for match in filtered_matches:
                fingerprint = await self.get_fingerprint(
                    match.matched_fingerprint_id, include_vectors=False
                )
                if fingerprint:
                    similar_fingerprints.append((fingerprint, match.similarity_score))
            
            return similar_fingerprints
            
        except Exception as e:
            self.logger.error(f"Similar fingerprint search failed: {e}")
            raise DatabaseError(f"Similarity search failed: {e}")
    
    async def update_fingerprint(
        self,
        fingerprint_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update fingerprint data
        
        Args:
            fingerprint_id: Fingerprint identifier
            updates: Fields to update
            
        Returns:
            True if updated successfully
        """
        try:
            # Validate updates
            allowed_fields = {
                'metadata', 'quality_level', 'status', 'confidence_score',
                'expires_at', 'updated_at'
            }
            
            filtered_updates = {
                k: v for k, v in updates.items() 
                if k in allowed_fields
            }
            
            if 'updated_at' not in filtered_updates:
                filtered_updates['updated_at'] = datetime.now(timezone.utc)
            
            # Update in storage
            success = await self.storage_manager.update_fingerprint(
                fingerprint_id, filtered_updates
            )
            
            if success:
                self.logger.info(f"Updated fingerprint {fingerprint_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to update fingerprint {fingerprint_id}: {e}")
            raise DatabaseError(f"Fingerprint update failed: {e}")
    
    async def delete_fingerprint(
        self,
        fingerprint_id: str,
        soft_delete: bool = True
    ) -> bool:
        """
        Delete fingerprint (soft or hard delete)
        
        Args:
            fingerprint_id: Fingerprint identifier
            soft_delete: If True, mark as deleted; if False, remove completely
            
        Returns:
            True if deleted successfully
        """
        try:
            if soft_delete:
                # Soft delete - mark as deleted
                success = await self.update_fingerprint(
                    fingerprint_id,
                    {
                        'status': FingerprintStatus.DELETED.value,
                        'updated_at': datetime.now(timezone.utc)
                    }
                )
            else:
                # Hard delete - remove from storage and indexes
                fingerprint = await self.get_fingerprint(fingerprint_id)
                if fingerprint:
                    # Remove from indexes first
                    await self.index_manager.remove_fingerprint_indexes(
                        fingerprint, fingerprint.metadata.get('user_id', '')
                    )
                
                # Remove from storage
                success = await self.storage_manager.delete_fingerprint(fingerprint_id)
            
            if success:
                self.logger.info(f"Deleted fingerprint {fingerprint_id} (soft={soft_delete})")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to delete fingerprint {fingerprint_id}: {e}")
            raise DatabaseError(f"Fingerprint deletion failed: {e}")
    
    async def bulk_create_fingerprints(
        self,
        fingerprints_data: List[Tuple[ContentFingerprint, str, Optional[Dict[str, Any]]]],
        batch_size: int = 100
    ) -> List[str]:
        """
        Bulk create fingerprints with optimized performance
        
        Args:
            fingerprints_data: List of (fingerprint, user_id, metadata) tuples
            batch_size: Number of fingerprints to process per batch
            
        Returns:
            List of created fingerprint IDs
        """
        try:
            created_ids = []
            
            # Process in batches
            for i in range(0, len(fingerprints_data), batch_size):
                batch = fingerprints_data[i:i + batch_size]
                
                async with self.storage_manager.batch_operation() as session:
                    batch_ids = []
                    
                    for fingerprint, user_id, metadata in batch:
                        # Store fingerprint
                        fingerprint_id = await self.storage_manager.store_fingerprint(
                            fingerprint, user_id, metadata
                        )
                        batch_ids.append(fingerprint_id)
                    
                    # Add to indexes in batch
                    for j, (fingerprint, user_id, metadata) in enumerate(batch):
                        embedding_vector = getattr(fingerprint, 'embedding_vector', None)
                        await self.index_manager.add_fingerprint_indexes(
                            fingerprint, user_id, embedding_vector
                        )
                    
                    created_ids.extend(batch_ids)
                
                self.logger.info(f"Created batch of {len(batch)} fingerprints")
            
            self.logger.info(f"Bulk created {len(created_ids)} fingerprints")
            return created_ids
            
        except Exception as e:
            self.logger.error(f"Bulk fingerprint creation failed: {e}")
            raise DatabaseError(f"Bulk creation failed: {e}")
    
    async def get_fingerprint_matches(
        self,
        fingerprint_id: str,
        limit: int = 50
    ) -> List[MatchResult]:
        """
        Get match history for a fingerprint
        
        Args:
            fingerprint_id: Fingerprint identifier
            limit: Maximum matches to return
            
        Returns:
            List of match results
        """
        try:
            async with self.db_manager.get_session() as session:
                query = select(FingerprintMatchModel).where(
                    or_(
                        FingerprintMatchModel.fingerprint_id == fingerprint_id,
                        FingerprintMatchModel.matched_fingerprint_id == fingerprint_id
                    )
                ).order_by(desc(FingerprintMatchModel.detected_at)).limit(limit)
                
                result = await session.execute(query)
                match_models = result.scalars().all()
                
                # Convert to MatchResult objects
                matches = []
                for model in match_models:
                    match_result = MatchResult(
                        query_fingerprint_id=str(model.fingerprint_id),
                        matched_fingerprint_id=str(model.matched_fingerprint_id),
                        similarity_score=model.similarity_score,
                        match_type=model.match_type,
                        algorithm=model.matching_algorithm,
                        confidence_level=model.confidence_level,
                        match_details=model.match_metadata or {},
                        processing_time=0.0,  # Not stored in model
                        timestamp=model.detected_at
                    )
                    matches.append(match_result)
                
                return matches
                
        except Exception as e:
            self.logger.error(f"Failed to get matches for fingerprint {fingerprint_id}: {e}")
            raise DatabaseError(f"Match retrieval failed: {e}")
    
    async def get_fingerprint_statistics(
        self,
        user_id: Optional[str] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> FingerprintStatistics:
        """
        Get comprehensive fingerprint statistics
        
        Args:
            user_id: Optional user filter
            date_range: Optional date range filter (start, end)
            
        Returns:
            FingerprintStatistics object
        """
        try:
            async with self.db_manager.get_session() as session:
                # Base query conditions
                conditions = []
                if user_id:
                    conditions.append(FingerprintStorageModel.user_id == user_id)
                if date_range:
                    conditions.append(FingerprintStorageModel.created_at >= date_range[0])
                    conditions.append(FingerprintStorageModel.created_at <= date_range[1])
                
                base_where = and_(*conditions) if conditions else True
                
                # Total count
                total_query = select(func.count()).select_from(FingerprintStorageModel).where(base_where)
                total_result = await session.execute(total_query)
                total_count = total_result.scalar()
                
                # Active count
                active_query = select(func.count()).select_from(FingerprintStorageModel).where(
                    and_(base_where, FingerprintStorageModel.status == 'active')
                )
                active_result = await session.execute(active_query)
                active_count = active_result.scalar()
                
                # Content type distribution
                content_type_query = select(
                    FingerprintStorageModel.content_type,
                    func.count().label('count')
                ).where(base_where).group_by(FingerprintStorageModel.content_type)
                
                content_type_result = await session.execute(content_type_query)
                content_type_distribution = dict(content_type_result.fetchall())
                
                # Quality distribution
                quality_query = select(
                    FingerprintStorageModel.quality_level,
                    func.count().label('count')
                ).where(base_where).group_by(FingerprintStorageModel.quality_level)
                
                quality_result = await session.execute(quality_query)
                quality_distribution = dict(quality_result.fetchall())
                
                # Average confidence
                confidence_query = select(func.avg(FingerprintStorageModel.confidence_score)).where(base_where)
                confidence_result = await session.execute(confidence_query)
                average_confidence = confidence_result.scalar() or 0.0
                
                # Creation trends (last 30 days)
                thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
                trends_query = select(
                    func.date(FingerprintStorageModel.created_at).label('date'),
                    func.count().label('count')
                ).where(
                    and_(base_where, FingerprintStorageModel.created_at >= thirty_days_ago)
                ).group_by(func.date(FingerprintStorageModel.created_at))
                
                trends_result = await session.execute(trends_query)
                creation_trends = {str(date): count for date, count in trends_result.fetchall()}
                
                # Storage metrics
                storage_metrics = await self.storage_manager.get_storage_stats(user_id)
                
                # Performance metrics
                performance_metrics = {
                    "average_query_time": 0.0,  # Would be tracked separately
                    "index_efficiency": 0.95,  # Would be calculated from index stats
                    "cache_hit_rate": 0.85,    # Would come from cache manager
                }
                
                return FingerprintStatistics(
                    total_count=total_count,
                    active_count=active_count,
                    content_type_distribution=content_type_distribution,
                    quality_distribution=quality_distribution,
                    average_confidence=float(average_confidence),
                    creation_trends=creation_trends,
                    storage_metrics=storage_metrics,
                    performance_metrics=performance_metrics
                )
                
        except Exception as e:
            self.logger.error(f"Failed to get fingerprint statistics: {e}")
            raise DatabaseError(f"Statistics calculation failed: {e}")
    
    async def get_match_statistics(
        self,
        user_id: Optional[str] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> MatchStatistics:
        """
        Get comprehensive match operation statistics
        
        Args:
            user_id: Optional user filter
            date_range: Optional date range filter
            
        Returns:
            MatchStatistics object
        """
        try:
            async with self.db_manager.get_session() as session:
                # Build base conditions
                conditions = []
                if date_range:
                    conditions.append(FingerprintMatchModel.detected_at >= date_range[0])
                    conditions.append(FingerprintMatchModel.detected_at <= date_range[1])
                
                # Join with fingerprints to filter by user
                base_query = select(FingerprintMatchModel)
                if user_id:
                    base_query = base_query.join(
                        FingerprintStorageModel,
                        FingerprintMatchModel.fingerprint_id == FingerprintStorageModel.fingerprint_id
                    ).where(FingerprintStorageModel.user_id == user_id)
                
                if conditions:
                    base_query = base_query.where(and_(*conditions))
                
                # Total matches
                total_query = select(func.count()).select_from(base_query.subquery())
                total_result = await session.execute(total_query)
                total_matches = total_result.scalar()
                
                # Match type distribution
                match_type_query = select(
                    FingerprintMatchModel.match_type,
                    func.count().label('count')
                ).select_from(base_query.subquery()).group_by(FingerprintMatchModel.match_type)
                
                match_type_result = await session.execute(match_type_query)
                match_type_dist = dict(match_type_result.fetchall())
                
                exact_matches = match_type_dist.get('exact', 0)
                similar_matches = match_type_dist.get('similar', 0)
                partial_matches = match_type_dist.get('partial', 0)
                
                # Algorithm distribution
                algorithm_query = select(
                    FingerprintMatchModel.matching_algorithm,
                    func.count().label('count')
                ).select_from(base_query.subquery()).group_by(FingerprintMatchModel.matching_algorithm)
                
                algorithm_result = await session.execute(algorithm_query)
                algorithm_distribution = dict(algorithm_result.fetchall())
                
                # Average similarity
                similarity_query = select(func.avg(FingerprintMatchModel.similarity_score)).select_from(base_query.subquery())
                similarity_result = await session.execute(similarity_query)
                average_similarity = similarity_result.scalar() or 0.0
                
                # Processing time stats (would need to be tracked separately)
                processing_time_stats = {
                    "average": 0.25,  # seconds
                    "median": 0.15,
                    "p95": 1.0,
                    "p99": 2.5
                }
                
                return MatchStatistics(
                    total_matches=total_matches,
                    exact_matches=exact_matches,
                    similar_matches=similar_matches,
                    partial_matches=partial_matches,
                    algorithm_distribution=algorithm_distribution,
                    average_similarity=float(average_similarity),
                    processing_time_stats=processing_time_stats
                )
                
        except Exception as e:
            self.logger.error(f"Failed to get match statistics: {e}")
            raise DatabaseError(f"Match statistics calculation failed: {e}")
    
    async def cleanup_expired_fingerprints(self) -> int:
        """
        Clean up expired fingerprints
        
        Returns:
            Number of fingerprints cleaned up
        """
        try:
            cleaned_count = await self.storage_manager.cleanup_expired_fingerprints()
            self.logger.info(f"Cleaned up {cleaned_count} expired fingerprints")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Fingerprint cleanup failed: {e}")
            raise DatabaseError(f"Cleanup failed: {e}")
    
    async def rebuild_indexes(
        self,
        content_type: Optional[str] = None,
        batch_size: int = 1000
    ) -> None:
        """
        Rebuild fingerprint indexes
        
        Args:
            content_type: Optional content type filter
            batch_size: Batch size for processing
        """
        try:
            await self.index_manager.rebuild_indexes(content_type, batch_size)
            self.logger.info(f"Rebuilt indexes for content_type: {content_type or 'all'}")
            
        except Exception as e:
            self.logger.error(f"Index rebuild failed: {e}")
            raise DatabaseError(f"Index rebuild failed: {e}")
    
    async def export_fingerprints(
        self,
        query: FingerprintQuery,
        format: str = "json",
        include_vectors: bool = False
    ) -> Dict[str, Any]:
        """
        Export fingerprints based on query
        
        Args:
            query: Query parameters
            format: Export format (json, csv)
            include_vectors: Whether to include vector data
            
        Returns:
            Export data
        """
        try:
            # Remove pagination for export
            query.pagination = None
            query.include_vectors = include_vectors
            
            # Query all matching fingerprints
            result = await self.query_fingerprints(query)
            
            # Convert to export format
            if format == "json":
                export_data = {
                    "metadata": {
                        "export_timestamp": datetime.now(timezone.utc).isoformat(),
                        "total_count": result.total_count,
                        "query_parameters": asdict(query)
                    },
                    "fingerprints": [
                        self._fingerprint_to_dict(fp, include_vectors)
                        for fp in result.items
                    ]
                }
            else:
                raise ValidationError(f"Unsupported export format: {format}")
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"Fingerprint export failed: {e}")
            raise DatabaseError(f"Export failed: {e}")
    
    # Private helper methods
    
    def _build_query_conditions(self, query: FingerprintQuery) -> List:
        """Build SQLAlchemy query conditions from FingerprintQuery"""
        conditions = []
        
        # User filter
        if query.user_id:
            conditions.append(FingerprintStorageModel.user_id == query.user_id)
        
        # Content filters
        if query.content_ids:
            conditions.append(FingerprintStorageModel.content_id.in_(query.content_ids))
        
        if query.content_types:
            conditions.append(FingerprintStorageModel.content_type.in_(query.content_types))
        
        if query.fingerprint_types:
            conditions.append(FingerprintStorageModel.fingerprint_type.in_(query.fingerprint_types))
        
        if query.quality_levels:
            conditions.append(FingerprintStorageModel.quality_level.in_(query.quality_levels))
        
        # Status filter
        if query.status:
            conditions.append(FingerprintStorageModel.status == query.status.value)
        elif not query.include_expired:
            # Exclude expired and deleted by default
            conditions.append(FingerprintStorageModel.status.notin_(['expired', 'deleted']))
        
        # Date filters
        if query.created_after:
            conditions.append(FingerprintStorageModel.created_at >= query.created_after)
        
        if query.created_before:
            conditions.append(FingerprintStorageModel.created_at <= query.created_before)
        
        if query.updated_after:
            conditions.append(FingerprintStorageModel.updated_at >= query.updated_after)
        
        if query.updated_before:
            conditions.append(FingerprintStorageModel.updated_at <= query.updated_before)
        
        # Score filters
        if query.min_confidence is not None:
            conditions.append(FingerprintStorageModel.confidence_score >= query.min_confidence)
        
        if query.max_confidence is not None:
            conditions.append(FingerprintStorageModel.confidence_score <= query.max_confidence)
        
        # Hash filters
        if query.primary_hash:
            conditions.append(FingerprintStorageModel.primary_hash == query.primary_hash)
        
        if query.perceptual_hash:
            conditions.append(FingerprintStorageModel.perceptual_hash == query.perceptual_hash)
        
        if query.structural_hash:
            conditions.append(FingerprintStorageModel.structural_hash == query.structural_hash)
        
        if query.semantic_hash:
            conditions.append(FingerprintStorageModel.semantic_hash == query.semantic_hash)
        
        # Text search in metadata
        if query.search_text:
            conditions.append(
                FingerprintStorageModel.metadata.op('?')('search_text') |
                FingerprintStorageModel.metadata.op('->')('tags').astext.contains(query.search_text)
            )
        
        # Metadata search
        if query.metadata_search:
            for key, value in query.metadata_search.items():
                conditions.append(
                    FingerprintStorageModel.metadata.op('->>')(key) == str(value)
                )
        
        return conditions
    
    def _fingerprint_to_dict(
        self,
        fingerprint: ContentFingerprint,
        include_vectors: bool = False
    ) -> Dict[str, Any]:
        """Convert fingerprint to dictionary for export"""
        data = {
            'fingerprint_id': fingerprint.fingerprint_id,
            'content_id': fingerprint.content_id,
            'content_type': str(fingerprint.content_type),
            'fingerprint_type': str(fingerprint.fingerprint_type),
            'primary_hash': fingerprint.primary_hash,
            'perceptual_hash': fingerprint.perceptual_hash,
            'structural_hash': fingerprint.structural_hash,
            'semantic_hash': fingerprint.semantic_hash,
            'temporal_signature': fingerprint.temporal_signature,
            'file_signature': fingerprint.file_signature,
            'confidence_score': fingerprint.confidence_score,
            'metadata': fingerprint.metadata,
            'creation_timestamp': fingerprint.creation_timestamp.isoformat() if fingerprint.creation_timestamp else None
        }
        
        # Include vectors if requested
        if include_vectors:
            if hasattr(fingerprint, 'feature_vector') and fingerprint.feature_vector is not None:
                data['feature_vector'] = fingerprint.feature_vector.tolist()
            
            if hasattr(fingerprint, 'embedding_vector') and fingerprint.embedding_vector is not None:
                data['embedding_vector'] = fingerprint.embedding_vector.tolist()
        
        return data
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the repository and its components
        
        Returns:
            Health status information
        """
        try:
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "components": {}
            }
            
            # Test database connection
            try:
                async with self.db_manager.get_session() as session:
                    result = await session.execute(text("SELECT 1"))
                    result.scalar()
                health_status["components"]["database"] = "healthy"
            except Exception as e:
                health_status["components"]["database"] = f"unhealthy: {e}"
                health_status["status"] = "degraded"
            
            # Test index statistics
            try:
                index_stats = await self.index_manager.get_index_statistics()
                health_status["components"]["indexes"] = "healthy"
                health_status["index_statistics"] = index_stats
            except Exception as e:
                health_status["components"]["indexes"] = f"unhealthy: {e}"
                health_status["status"] = "degraded"
            
            # Test storage manager
            try:
                storage_stats = await self.storage_manager.get_storage_stats()
                health_status["components"]["storage"] = "healthy"
                health_status["storage_statistics"] = storage_stats
            except Exception as e:
                health_status["components"]["storage"] = f"unhealthy: {e}"
                health_status["status"] = "degraded"
            
            return health_status
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
