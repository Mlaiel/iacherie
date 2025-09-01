"""Intelligent Fingerprint Cleanup Service

Advanced cleanup and maintenance system for fingerprint data with automated
lifecycle management, intelligent retention policies, and performance optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import logging
import json
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum

from sqlalchemy import and_, or_, func, text, select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import DatabaseManager
from backend.core.config import settings
from backend.core.exceptions import DatabaseError, ValidationError
from backend.database.fingerprinting.fingerprint_storage import (
    FingerprintStorageModel, FingerprintMatchModel
)
from backend.database.fingerprinting.fingerprint_indexing import FingerprintIndexManager
from backend.database.fingerprinting.fingerprint_cache import FingerprintCacheManager
from backend.utils.performance import PerformanceMonitor
from backend.utils.scheduling import SchedulerManager

logger = logging.getLogger(__name__)


class CleanupAction(Enum):
    """
Types of cleanup actions"""

    SOFT_DELETE = "soft_delete"
    HARD_DELETE = "hard_delete"
    ARCHIVE = "archive"
    COMPRESS = "compress"
    OPTIMIZE = "optimize"


class RetentionPolicyType(Enum):
    """Types of retention policies"""

    TIME_BASED = "time_based"
    SIZE_BASED = "size_based"
    ACCESS_BASED = "access_based"
    QUALITY_BASED = "quality_based"
    CUSTOM = "custom"


@dataclass
class RetentionPolicy:
    """Configuration for data retention"""
    policy_type: RetentionPolicyType
    name: str
    description: str
    
    # Time-based settings
    max_age_days: Optional[int] = None
    inactive_threshold_days: Optional[int] = None
    
    # Size-based settings
    max_storage_gb: Optional[float] = None
    max_items_per_user: Optional[int] = None
    
    # Access-based settings
    min_access_count: Optional[int] = None
    last_access_threshold_days: Optional[int] = None
    
    # Quality-based settings
    min_confidence_score: Optional[float] = None
    min_quality_level: Optional[str] = None
    
    # Actions
    primary_action: CleanupAction = CleanupAction.ARCHIVE
    fallback_action: CleanupAction = CleanupAction.SOFT_DELETE
    
    # Filters
    content_types: Optional[List[str]] = None
    user_groups: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    
    # Settings
    enabled: bool = True
    dry_run: bool = False
    batch_size: int = 1000


@dataclass
class CleanupReport:
    """
Report of cleanup operations"""
    policy_name: str
    start_time: datetime
    end_time: datetime
    
    # Counts
    items_processed: int = 0
    items_deleted: int = 0
    items_archived: int = 0
    items_compressed: int = 0
    items_optimized: int = 0
    items_skipped: int = 0
    errors: int = 0
    
    # Storage impact
    storage_freed_bytes: int = 0
    storage_freed_gb: float = 0.0
    
    # Performance
    processing_time_seconds: float = 0.0
    average_item_time_ms: float = 0.0
    
    # Details
    error_details: List[str] = None
    statistics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.error_details is None:
            self.error_details = []
        if self.statistics is None:
            self.statistics = {}
        
        # Calculate derived fields
        self.processing_time_seconds = (self.end_time - self.start_time).total_seconds()
        self.storage_freed_gb = self.storage_freed_bytes / (1024**3)
        
        if self.items_processed > 0:
            self.average_item_time_ms = (self.processing_time_seconds * 1000) / self.items_processed


class FingerprintAnalyzer:
    """
Analyze fingerprint data for cleanup decisions"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(f"{__name__}.FingerprintAnalyzer")
    
    async def analyze_storage_usage(
        self,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze storage usage patterns"""
        try:
            async with self.db_manager.get_session() as session:
                base_query = select(FingerprintStorageModel)
                if user_id:
                    base_query = base_query.where(FingerprintStorageModel.user_id == user_id)
                
                # Total storage size
                size_query = select(func.sum(FingerprintStorageModel.storage_size)).select_from(base_query.subquery())
                size_result = await session.execute(size_query)
                total_size = size_result.scalar() or 0
                
                # Content type distribution
                content_dist_query = select(
                    FingerprintStorageModel.content_type,
                    func.count().label('count'),
                    func.sum(FingerprintStorageModel.storage_size).label('size')
                ).select_from(base_query.subquery()).group_by(FingerprintStorageModel.content_type)
                
                content_dist_result = await session.execute(content_dist_query)
                content_distribution = {}
                for content_type, count, size in content_dist_result.fetchall():
                    content_distribution[content_type] = {
                        'count': count,
                        'size_bytes': size or 0,
                        'size_gb': (size or 0) / (1024**3)
                    }
                
                # Age distribution
                now = datetime.now(timezone.utc)
                age_ranges = [
                    ('0-7 days', 7),
                    ('8-30 days', 30),
                    ('31-90 days', 90),
                    ('91-365 days', 365),
                    ('1+ years', None)
                ]
                
                age_distribution = {}
                for label, days in age_ranges:
                    if days:
                        threshold = now - timedelta(days=days)
                        prev_threshold = now - timedelta(days=days-7 if days > 7 else 0)
                        
                        age_query = select(func.count()).select_from(base_query.subquery()).where(
                            and_(
                                FingerprintStorageModel.created_at >= threshold,
                                FingerprintStorageModel.created_at < prev_threshold
                            )
                        )
                    else:
                        threshold = now - timedelta(days=365)
                        age_query = select(func.count()).select_from(base_query.subquery()).where(
                            FingerprintStorageModel.created_at < threshold
                        )
                    
                    age_result = await session.execute(age_query)
                    age_distribution[label] = age_result.scalar()
                
                return {
                    'total_size_bytes': total_size,
                    'total_size_gb': total_size / (1024**3),
                    'content_type_distribution': content_distribution,
                    'age_distribution': age_distribution,
                    'analysis_timestamp': now.isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Storage usage analysis failed: {e}")
            raise DatabaseError(f"Storage analysis failed: {e}")
    
    async def identify_cleanup_candidates(
        self,
        policy: RetentionPolicy
    ) -> List[str]:
        """Identify fingerprints that match cleanup criteria"""
        try:
            async with self.db_manager.get_session() as session:
                conditions = []
                
                # Build conditions based on policy type
                if policy.policy_type == RetentionPolicyType.TIME_BASED:
                    if policy.max_age_days:
                        threshold = datetime.now(timezone.utc) - timedelta(days=policy.max_age_days)
                        conditions.append(FingerprintStorageModel.created_at < threshold)
                    
                    if policy.inactive_threshold_days:
                        inactive_threshold = datetime.now(timezone.utc) - timedelta(days=policy.inactive_threshold_days)
                        conditions.append(
                            or_(
                                FingerprintStorageModel.last_accessed.is_(None),
                                FingerprintStorageModel.last_accessed < inactive_threshold
                            )
                        )
                
                elif policy.policy_type == RetentionPolicyType.QUALITY_BASED:
                    if policy.min_confidence_score:
                        conditions.append(FingerprintStorageModel.confidence_score < policy.min_confidence_score)
                    
                    if policy.min_quality_level:
                        # Assuming quality levels: 'low' < 'standard' < 'high' < 'premium'
                        quality_order = {'low': 1, 'standard': 2, 'high': 3, 'premium': 4}
                        min_level_value = quality_order.get(policy.min_quality_level, 2)
                        
                        # This would need a custom function or case statement
                        # For now, we'll use a simple text comparison
                        if policy.min_quality_level == 'standard':
                            conditions.append(FingerprintStorageModel.quality_level == 'low')
                        elif policy.min_quality_level == 'high':
                            conditions.append(FingerprintStorageModel.quality_level.in_(['low', 'standard']))
                
                elif policy.policy_type == RetentionPolicyType.ACCESS_BASED:
                    if policy.last_access_threshold_days:
                        access_threshold = datetime.now(timezone.utc) - timedelta(days=policy.last_access_threshold_days)
                        conditions.append(
                            or_(
                                FingerprintStorageModel.last_accessed.is_(None),
                                FingerprintStorageModel.last_accessed < access_threshold
                            )
                        )
                
                # Apply content type filters
                if policy.content_types:
                    conditions.append(FingerprintStorageModel.content_type.in_(policy.content_types))
                
                # Only process active fingerprints (not already deleted)
                conditions.append(FingerprintStorageModel.status != 'deleted')
                
                # Build and execute query
                if conditions:
                    query = select(FingerprintStorageModel.fingerprint_id).where(and_(*conditions))
                    
                    # Apply limit for batch processing
                    if policy.batch_size:
                        query = query.limit(policy.batch_size)
                    
                    result = await session.execute(query)
                    fingerprint_ids = [str(row[0]) for row in result.fetchall()]
                    
                    return fingerprint_ids
                
                return []
                
        except Exception as e:
            self.logger.error(f"Cleanup candidate identification failed: {e}")
            raise DatabaseError(f"Candidate identification failed: {e}")
    
    async def analyze_fingerprint_quality(
        self,
        fingerprint_id: str
    ) -> Dict[str, Any]:
        """Analyze quality metrics for a specific fingerprint"""
        try:
            async with self.db_manager.get_session() as session:
                query = select(FingerprintStorageModel).where(
                    FingerprintStorageModel.fingerprint_id == fingerprint_id
                )
                result = await session.execute(query)
                fingerprint = result.scalar_one_or_none()
                
                if not fingerprint:
                    return {"error": "Fingerprint not found"}
                
                # Calculate quality metrics
                quality_score = 0.0
                quality_factors = {}
                
                # Confidence score factor (0-40 points)
                confidence_factor = min(fingerprint.confidence_score * 40, 40)
                quality_score += confidence_factor
                quality_factors['confidence'] = confidence_factor
                
                # Age factor (0-20 points, newer is better)
                if fingerprint.created_at:
                    age_days = (datetime.now(timezone.utc) - fingerprint.created_at).days
                    age_factor = max(20 - (age_days / 30), 0)  # Decrease by 1 point per 1.5 days
                    quality_score += age_factor
                    quality_factors['age'] = age_factor
                
                # Access frequency factor (0-20 points)
                access_factor = 10  # Default if no access data
                if fingerprint.last_accessed:
                    days_since_access = (datetime.now(timezone.utc) - fingerprint.last_accessed).days
                    access_factor = max(20 - days_since_access, 0)
                quality_score += access_factor
                quality_factors['access'] = access_factor
                
                # Completeness factor (0-20 points)
                completeness_factor = 0
                if fingerprint.primary_hash:
                    completeness_factor += 5
                if fingerprint.perceptual_hash:
                    completeness_factor += 5
                if fingerprint.structural_hash:
                    completeness_factor += 5
                if fingerprint.feature_vector:
                    completeness_factor += 5
                
                quality_score += completeness_factor
                quality_factors['completeness'] = completeness_factor
                
                # Determine quality level
                if quality_score >= 80:
                    quality_level = "premium"
                elif quality_score >= 60:
                    quality_level = "high"
                elif quality_score >= 40:
                    quality_level = "standard"
                else:
                    quality_level = "low"
                
                return {
                    'fingerprint_id': fingerprint_id,
                    'overall_quality_score': quality_score,
                    'quality_level': quality_level,
                    'quality_factors': quality_factors,
                    'recommendations': self._generate_quality_recommendations(quality_score, quality_factors)
                }
                
        except Exception as e:
            self.logger.error(f"Quality analysis failed for fingerprint {fingerprint_id}: {e}")
            return {"error": str(e)}
    
    def _generate_quality_recommendations(
        self,
        quality_score: float,
        quality_factors: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations based on quality analysis"""
        recommendations = []
        
        if quality_score < 40:
            recommendations.append("Consider deleting this low-quality fingerprint")
        elif quality_score < 60:
            recommendations.append("Archive this fingerprint to cold storage")
        
        if quality_factors.get('confidence', 0) < 20:
            recommendations.append("Low confidence score - verify fingerprint accuracy")
        
        if quality_factors.get('access', 0) < 5:
            recommendations.append("Rarely accessed - candidate for archival")
        
        if quality_factors.get('completeness', 0) < 15:
            recommendations.append("Incomplete fingerprint data - consider regeneration")
        
        return recommendations


class FingerprintCleanupService:
    """
    Intelligent fingerprint cleanup service with automated lifecycle management,
    retention policies, and performance optimization.
    """
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        index_manager: FingerprintIndexManager,
        cache_manager: FingerprintCacheManager
    ):
        self.db_manager = db_manager
        self.index_manager = index_manager
        self.cache_manager = cache_manager
        self.analyzer = FingerprintAnalyzer(db_manager)
        self.logger = logging.getLogger(__name__)
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        
        # Default retention policies
        self.default_policies = self._create_default_policies()
        
        # Cleanup history
        self.cleanup_history: List[CleanupReport] = []
    
    async def execute_cleanup_policy(
        self,
        policy: RetentionPolicy,
        progress_callback: Optional[callable] = None
    ) -> CleanupReport:
        """
        Execute a cleanup policy
        
        Args:
            policy: RetentionPolicy to execute
            progress_callback: Optional callback for progress updates
            
        Returns:
            CleanupReport with execution results
        """
        start_time = datetime.now(timezone.utc)
        report = CleanupReport(
            policy_name=policy.name,
            start_time=start_time,
            end_time=start_time  # Will be updated at the end
        )
        
        try:
            self.logger.info(f"Starting cleanup policy execution: {policy.name}")
            
            # Identify cleanup candidates
            candidate_ids = await self.analyzer.identify_cleanup_candidates(policy)
            report.items_processed = len(candidate_ids)
            
            if not candidate_ids:
                self.logger.info(f"No cleanup candidates found for policy {policy.name}")
                report.end_time = datetime.now(timezone.utc)
                return report
            
            self.logger.info(f"Found {len(candidate_ids)} cleanup candidates")
            
            # Process candidates in batches
            batch_size = min(policy.batch_size, 100)
            
            for i in range(0, len(candidate_ids), batch_size):
                batch = candidate_ids[i:i + batch_size]
                
                try:
                    await self._process_cleanup_batch(batch, policy, report)
                    
                    # Call progress callback if provided
                    if progress_callback:
                        progress = (i + len(batch)) / len(candidate_ids)
                        await progress_callback(progress, report)
                        
                except Exception as e:
                    self.logger.error(f"Batch cleanup failed: {e}")
                    report.errors += len(batch)
                    report.error_details.append(f"Batch {i}-{i+len(batch)}: {e}")
            
            # Generate statistics
            report.statistics = await self._generate_cleanup_statistics(policy, report)
            
            self.logger.info(
                f"Cleanup policy {policy.name} completed: "
                f"{report.items_processed} processed, {report.items_deleted} deleted, "
                f"{report.items_archived} archived"
            )
            
        except Exception as e:
            self.logger.error(f"Cleanup policy execution failed: {e}")
            report.errors += 1
            report.error_details.append(f"Policy execution error: {e}")
        
        finally:
            report.end_time = datetime.now(timezone.utc)
            self.cleanup_history.append(report)
            
            # Keep only last 100 reports
            if len(self.cleanup_history) > 100:
                self.cleanup_history = self.cleanup_history[-100:]
        
        return report
    
    async def _process_cleanup_batch(
        self,
        fingerprint_ids: List[str],
        policy: RetentionPolicy,
        report: CleanupReport
    ) -> None:
        """Process a batch of fingerprints for cleanup"""
        try:
            async with self.db_manager.get_session() as session:
                for fingerprint_id in fingerprint_ids:
                    try:
                        success = await self._process_single_fingerprint(
                            fingerprint_id, policy, session
                        )
                        
                        if success:
                            if policy.primary_action == CleanupAction.SOFT_DELETE:
                                report.items_deleted += 1
                            elif policy.primary_action == CleanupAction.HARD_DELETE:
                                report.items_deleted += 1
                            elif policy.primary_action == CleanupAction.ARCHIVE:
                                report.items_archived += 1
                            elif policy.primary_action == CleanupAction.COMPRESS:
                                report.items_compressed += 1
                            elif policy.primary_action == CleanupAction.OPTIMIZE:
                                report.items_optimized += 1
                        else:
                            report.items_skipped += 1
                            
                    except Exception as e:
                        self.logger.error(f"Failed to process fingerprint {fingerprint_id}: {e}")
                        report.errors += 1
                        report.error_details.append(f"Fingerprint {fingerprint_id}: {e}")
                
                # Commit batch
                if not policy.dry_run:
                    await session.commit()
                
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            raise
    
    async def _process_single_fingerprint(
        self,
        fingerprint_id: str,
        policy: RetentionPolicy,
        session: AsyncSession
    ) -> bool:
        """Process a single fingerprint according to policy"""
        try:
            # Get fingerprint details
            query = select(FingerprintStorageModel).where(
                FingerprintStorageModel.fingerprint_id == fingerprint_id
            )
            result = await session.execute(query)
            fingerprint = result.scalar_one_or_none()
            
            if not fingerprint:
                return False
            
            # Skip if dry run
            if policy.dry_run:
                self.logger.debug(f"DRY RUN: Would process fingerprint {fingerprint_id}")
                return True
            
            # Execute primary action
            if policy.primary_action == CleanupAction.SOFT_DELETE:
                return await self._soft_delete_fingerprint(fingerprint_id, session)
            
            elif policy.primary_action == CleanupAction.HARD_DELETE:
                return await self._hard_delete_fingerprint(fingerprint_id, session)
            
            elif policy.primary_action == CleanupAction.ARCHIVE:
                return await self._archive_fingerprint(fingerprint, session)
            
            elif policy.primary_action == CleanupAction.COMPRESS:
                return await self._compress_fingerprint(fingerprint, session)
            
            elif policy.primary_action == CleanupAction.OPTIMIZE:
                return await self._optimize_fingerprint(fingerprint, session)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Single fingerprint processing failed: {e}")
            return False
    
    async def _soft_delete_fingerprint(
        self,
        fingerprint_id: str,
        session: AsyncSession
    ) -> bool:
        """Mark fingerprint as deleted (soft delete)"""
        try:
            # Update status to deleted
            update_query = update(FingerprintStorageModel).where(
                FingerprintStorageModel.fingerprint_id == fingerprint_id
            ).values(
                status='deleted',
                updated_at=datetime.now(timezone.utc)
            )
            
            result = await session.execute(update_query)
            
            # Invalidate cache
            await self.cache_manager.invalidate_fingerprint(fingerprint_id)
            
            return result.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"Soft delete failed for fingerprint {fingerprint_id}: {e}")
            return False
    
    async def _hard_delete_fingerprint(
        self,
        fingerprint_id: str,
        session: AsyncSession
    ) -> bool:
        """Permanently delete fingerprint and related data"""
        try:
            # Delete matches first (foreign key constraint)
            match_delete_query = delete(FingerprintMatchModel).where(
                or_(
                    FingerprintMatchModel.fingerprint_id == fingerprint_id,
                    FingerprintMatchModel.matched_fingerprint_id == fingerprint_id
                )
            )
            await session.execute(match_delete_query)
            
            # Delete fingerprint
            fingerprint_delete_query = delete(FingerprintStorageModel).where(
                FingerprintStorageModel.fingerprint_id == fingerprint_id
            )
            result = await session.execute(fingerprint_delete_query)
            
            # Remove from indexes (after session commit)
            # This would need to be done in a separate transaction
            
            # Invalidate cache
            await self.cache_manager.invalidate_fingerprint(fingerprint_id)
            
            return result.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"Hard delete failed for fingerprint {fingerprint_id}: {e}")
            return False
    
    async def _archive_fingerprint(
        self,
        fingerprint: FingerprintStorageModel,
        session: AsyncSession
    ) -> bool:
        """Archive fingerprint to cold storage"""
        try:
            # Update status to archived
            update_query = update(FingerprintStorageModel).where(
                FingerprintStorageModel.fingerprint_id == fingerprint.fingerprint_id
            ).values(
                status='archived',
                updated_at=datetime.now(timezone.utc)
            )
            
            result = await session.execute(update_query)
            
            # Clear from hot cache
            await self.cache_manager.invalidate_fingerprint(str(fingerprint.fingerprint_id))
            
            # Here you would typically move vector data to cold storage
            # and keep only essential metadata in the main database
            
            return result.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"Archive failed for fingerprint {fingerprint.fingerprint_id}: {e}")
            return False
    
    async def _compress_fingerprint(
        self,
        fingerprint: FingerprintStorageModel,
        session: AsyncSession
    ) -> bool:
        """Compress fingerprint vector data"""
        try:
            # This would involve compressing the vector data
            # For now, we'll just mark it as compressed
            
            if fingerprint.metadata is None:
                fingerprint.metadata = {}
            
            fingerprint.metadata['compressed'] = True
            fingerprint.metadata['compression_timestamp'] = datetime.now(timezone.utc).isoformat()
            
            update_query = update(FingerprintStorageModel).where(
                FingerprintStorageModel.fingerprint_id == fingerprint.fingerprint_id
            ).values(
                metadata=fingerprint.metadata,
                updated_at=datetime.now(timezone.utc)
            )
            
            result = await session.execute(update_query)
            
            return result.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"Compression failed for fingerprint {fingerprint.fingerprint_id}: {e}")
            return False
    
    async def _optimize_fingerprint(
        self,
        fingerprint: FingerprintStorageModel,
        session: AsyncSession
    ) -> bool:
        """Optimize fingerprint storage and indexes"""
        try:
            # This could involve various optimizations:
            # - Recompute hashes if needed
            # - Update quality metrics
            # - Refresh access patterns
            
            update_data = {
                'updated_at': datetime.now(timezone.utc)
            }
            
            # Update quality metrics if available
            if fingerprint.metadata:
                quality_analysis = await self.analyzer.analyze_fingerprint_quality(
                    str(fingerprint.fingerprint_id)
                )
                
                if 'quality_level' in quality_analysis:
                    update_data['quality_level'] = quality_analysis['quality_level']
            
            update_query = update(FingerprintStorageModel).where(
                FingerprintStorageModel.fingerprint_id == fingerprint.fingerprint_id
            ).values(**update_data)
            
            result = await session.execute(update_query)
            
            return result.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"Optimization failed for fingerprint {fingerprint.fingerprint_id}: {e}")
            return False
    
    async def _generate_cleanup_statistics(
        self,
        policy: RetentionPolicy,
        report: CleanupReport
    ) -> Dict[str, Any]:
        """Generate detailed cleanup statistics"""
        try:
            stats = {
                'policy_details': asdict(policy),
                'execution_summary': {
                    'total_candidates': report.items_processed,
                    'successful_operations': (
                        report.items_deleted + report.items_archived + 
                        report.items_compressed + report.items_optimized
                    ),
                    'failed_operations': report.errors,
                    'skipped_items': report.items_skipped,
                    'success_rate': 0.0
                }
            }
            
            total_operations = report.items_processed
            if total_operations > 0:
                successful = stats['execution_summary']['successful_operations']
                stats['execution_summary']['success_rate'] = successful / total_operations
            
            # Storage impact analysis
            if policy.policy_type == RetentionPolicyType.SIZE_BASED:
                storage_analysis = await self.analyzer.analyze_storage_usage()
                stats['storage_impact'] = storage_analysis
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to generate cleanup statistics: {e}")
            return {"error": str(e)}
    
    def _create_default_policies(self) -> List[RetentionPolicy]:
        """Create default retention policies"""
        return [
            # Old fingerprints cleanup
            RetentionPolicy(
                policy_type=RetentionPolicyType.TIME_BASED,
                name="old_fingerprints_cleanup",
                description="Remove fingerprints older than 2 years",
                max_age_days=730,
                primary_action=CleanupAction.ARCHIVE,
                fallback_action=CleanupAction.SOFT_DELETE,
                batch_size=1000
            ),
            
            # Low quality cleanup
            RetentionPolicy(
                policy_type=RetentionPolicyType.QUALITY_BASED,
                name="low_quality_cleanup",
                description="Remove low confidence fingerprints",
                min_confidence_score=0.3,
                primary_action=CleanupAction.SOFT_DELETE,
                batch_size=500
            ),
            
            # Inactive fingerprints
            RetentionPolicy(
                policy_type=RetentionPolicyType.ACCESS_BASED,
                name="inactive_fingerprints",
                description="Archive fingerprints not accessed in 6 months",
                last_access_threshold_days=180,
                primary_action=CleanupAction.ARCHIVE,
                batch_size=1000
            ),
            
            # Temporary fingerprints
            RetentionPolicy(
                policy_type=RetentionPolicyType.TIME_BASED,
                name="temporary_cleanup",
                description="Remove temporary/test fingerprints after 30 days",
                max_age_days=30,
                content_types=["test", "temporary"],
                primary_action=CleanupAction.HARD_DELETE,
                batch_size=100
            )
        ]
    
    async def get_cleanup_recommendations(
        self,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get cleanup recommendations based on current data"""
        try:
            recommendations = []
            
            # Analyze storage usage
            storage_analysis = await self.analyzer.analyze_storage_usage(user_id)
            
            # Check if storage is getting full
            total_size_gb = storage_analysis.get('total_size_gb', 0)
            if total_size_gb > 100:  # Example threshold
                recommendations.append({
                    'type': 'storage_warning',
                    'priority': 'high',
                    'message': f"Storage usage is high ({total_size_gb:.2f} GB)",
                    'suggested_policy': 'old_fingerprints_cleanup',
                    'estimated_savings_gb': total_size_gb * 0.2  # Estimate 20% savings
                })
            
            # Check age distribution
            age_dist = storage_analysis.get('age_distribution', {})
            old_items = age_dist.get('1+ years', 0)
            if old_items > 1000:
                recommendations.append({
                    'type': 'age_cleanup',
                    'priority': 'medium',
                    'message': f"Found {old_items} fingerprints older than 1 year",
                    'suggested_policy': 'old_fingerprints_cleanup',
                    'estimated_items': old_items
                })
            
            # Check for low quality fingerprints
            # This would require a more detailed query
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to get cleanup recommendations: {e}")
            return [{"error": str(e)}]
    
    async def schedule_cleanup_policy(
        self,
        policy: RetentionPolicy,
        schedule: str,  # Cron expression
        scheduler_manager: SchedulerManager
    ) -> bool:
        """Schedule a cleanup policy for automatic execution"""
        try:
            job_id = f"cleanup_policy_{policy.name}"
            
            async def cleanup_job():
                try:
                    report = await self.execute_cleanup_policy(policy)
                    self.logger.info(f"Scheduled cleanup completed: {policy.name}")
                    return report
                except Exception as e:
                    self.logger.error(f"Scheduled cleanup failed: {e}")
                    raise
            
            success = await scheduler_manager.schedule_job(
                job_id,
                cleanup_job,
                schedule,
                description=f"Cleanup policy: {policy.description}"
            )
            
            if success:
                self.logger.info(f"Scheduled cleanup policy {policy.name} with schedule {schedule}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to schedule cleanup policy: {e}")
            return False
    
    def get_cleanup_history(
        self,
        limit: int = 10
    ) -> List[CleanupReport]:
        """Get recent cleanup history"""
        return self.cleanup_history[-limit:] if self.cleanup_history else []
    
    async def health_check(self) -> Dict[str, Any]:
        """
Perform health check on cleanup service"""
        try:
            health = {
                "status": "healthy",
                "components": {},
                "metrics": {}
            }
            
            # Check database connectivity
            try:
                async with self.db_manager.get_session() as session:
                    result = await session.execute(text("SELECT 1"))
                    result.scalar()
                health["components"]["database"] = "healthy"
            except Exception as e:
                health["components"]["database"] = f"unhealthy: {e}"
                health["status"] = "degraded"
            
            # Check recent cleanup operations
            recent_cleanups = len([r for r in self.cleanup_history 
                                 if r.end_time > datetime.now(timezone.utc) - timedelta(hours=24)])
            
            health["metrics"]["recent_cleanups_24h"] = recent_cleanups
            health["metrics"]["total_cleanup_history"] = len(self.cleanup_history)
            
            # Check for any failed recent operations
            recent_failures = len([r for r in self.cleanup_history[-10:] if r.errors > 0])
            if recent_failures > 0:
                health["status"] = "degraded"
                health["warnings"] = [f"{recent_failures} recent cleanup operations had errors"]
            
            return health
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
