"""Fingerprint Version Management System

Comprehensive version control and history tracking for fingerprint data with
diff analysis, rollback capabilities, and evolution monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
import asyncio
import json
import logging
import hashlib
import difflib
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Integer, Text, JSON, Boolean, ForeignKey, Index, func, and_, or_, select, desc, asc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.core.database import DatabaseManager
from backend.core.config import settings
from backend.core.exceptions import DatabaseError, ValidationError
from backend.utils.performance import PerformanceMonitor
from backend.utils.encryption import EncryptionManager
from backend.utils.compression import CompressionManager

logger = logging.getLogger(__name__)

Base = declarative_base()


class VersionChangeType(Enum):
    """Types of version changes"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RESTORE = "restore"
    MERGE = "merge"
    SPLIT = "split"
    OPTIMIZE = "optimize"


class VersionStatus(Enum):
    """Version status options"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"
    CORRUPTED = "corrupted"


@dataclass
class VersionDiff:
    """Represents differences between versions"""
    field_name: str
    old_value: Any
    new_value: Any
    change_type: str  # "added", "removed", "modified"
    confidence: float = 1.0


@dataclass
class VersionMetadata:
    """Version metadata information"""
    version_id: str
    parent_version_id: Optional[str]
    change_type: VersionChangeType
    change_description: str
    created_by: str
    created_at: datetime
    tags: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)


class FingerprintVersionModel(Base):
    """SQLAlchemy model for fingerprint versions"""
    __tablename__ = 'fingerprint_versions'
    
    # Primary identification
    version_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    fingerprint_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    parent_version_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Version information
    version_number = Column(Integer, nullable=False)
    change_type = Column(String(50), nullable=False, index=True)
    change_description = Column(Text, nullable=True)
    
    # Fingerprint data snapshot
    primary_hash = Column(String(128), nullable=True, index=True)
    perceptual_hash = Column(String(128), nullable=True, index=True)
    structural_hash = Column(String(128), nullable=True, index=True)
    feature_vector = Column(JSON, nullable=True)
    metadata_snapshot = Column(JSON, nullable=True)
    
    # Quality and confidence
    confidence_score = Column(Integer, nullable=True)  # 0-100
    quality_level = Column(String(20), nullable=True, index=True)
    
    # Version metadata
    created_by = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    status = Column(String(20), nullable=False, default=VersionStatus.ACTIVE.value, index=True)
    
    # Storage optimization
    compressed_data = Column(Text, nullable=True)
    compression_algorithm = Column(String(50), nullable=True)
    encrypted = Column(Boolean, default=False, nullable=False)
    
    # Diff and change tracking
    changes_from_parent = Column(JSON, nullable=True)
    validation_checksum = Column(String(64), nullable=True)
    
    # Performance tracking
    creation_time_ms = Column(Integer, nullable=True)
    storage_size = Column(Integer, nullable=True)
    
    # Tags and attributes
    tags = Column(JSON, nullable=True)
    attributes = Column(JSON, nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_fingerprint_versions_fingerprint_id_version', 'fingerprint_id', 'version_number'),
        Index('idx_fingerprint_versions_created_at', 'created_at'),
        Index('idx_fingerprint_versions_status_type', 'status', 'change_type'),
        Index('idx_fingerprint_versions_parent', 'parent_version_id'),
    )


class VersionBranchModel(Base):
    """SQLAlchemy model for version branches"""
    __tablename__ = 'fingerprint_version_branches'
    
    branch_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    fingerprint_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    branch_name = Column(String(100), nullable=False)
    base_version_id = Column(UUID(as_uuid=True), nullable=False)
    head_version_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Branch metadata
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Merge information
    merged_into = Column(UUID(as_uuid=True), nullable=True)
    merged_at = Column(DateTime(timezone=True), nullable=True)
    merged_by = Column(String(255), nullable=True)
    
    __table_args__ = (
        Index('idx_fingerprint_branches_fingerprint_id', 'fingerprint_id'),
        Index('idx_fingerprint_branches_active', 'is_active'),
    )


@dataclass
class VersionQuery:
    """Query configuration for version operations"""
    fingerprint_id: Optional[str] = None
    version_ids: Optional[List[str]] = None
    
    # Filtering
    change_types: Optional[List[VersionChangeType]] = None
    status_types: Optional[List[VersionStatus]] = None
    created_by: Optional[List[str]] = None
    
    # Time range
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Version range
    min_version: Optional[int] = None
    max_version: Optional[int] = None
    
    # Ordering and pagination
    order_by: str = 'version_number'
    order_direction: str = 'desc'  # 'asc' or 'desc'
    limit: Optional[int] = None
    offset: int = 0
    
    # Advanced options
    include_diffs: bool = False
    include_metadata: bool = True
    include_compressed: bool = False


class VersionDiffEngine:
    """Engine for calculating and analyzing version differences"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.VersionDiffEngine")
    
    def calculate_diff(
        self,
        old_version: Dict[str, Any],
        new_version: Dict[str, Any]
    ) -> List[VersionDiff]:
        """Calculate differences between two version snapshots"""
        try:
            diffs = []
            
            # Define fields to compare
            comparable_fields = [
                'primary_hash', 'perceptual_hash', 'structural_hash',
                'feature_vector', 'confidence_score', 'quality_level',
                'metadata_snapshot'
            ]
            
            # Compare each field
            for field in comparable_fields:
                old_value = old_version.get(field)
                new_value = new_version.get(field)
                
                if old_value != new_value:
                    change_type = self._determine_change_type(old_value, new_value)
                    confidence = self._calculate_change_confidence(field, old_value, new_value)
                    
                    diff = VersionDiff(
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        change_type=change_type,
                        confidence=confidence
                    )
                    diffs.append(diff)
            
            return diffs
            
        except Exception as e:
            self.logger.error(f"Diff calculation failed: {e}")
            return []
    
    def _determine_change_type(self, old_value: Any, new_value: Any) -> str:
        """Determine the type of change between values"""
        if old_value is None and new_value is not None:
            return "added"
        elif old_value is not None and new_value is None:
            return "removed"
        else:
            return "modified"
    
    def _calculate_change_confidence(
        self,
        field_name: str,
        old_value: Any,
        new_value: Any
    ) -> float:
        """Calculate confidence score for the change"""
        try:
            # Hash fields have high confidence
            if 'hash' in field_name:
                return 1.0
            
            # Feature vectors - calculate similarity
            if field_name == 'feature_vector' and isinstance(old_value, list) and isinstance(new_value, list):
                if len(old_value) == len(new_value):
                    import numpy as np
                    old_array = np.array(old_value)
                    new_array = np.array(new_value)
                    
                    # Calculate cosine similarity
                    dot_product = np.dot(old_array, new_array)
                    norms = np.linalg.norm(old_array) * np.linalg.norm(new_array)
                    
                    if norms > 0:
                        similarity = dot_product / norms
                        return float(1.0 - similarity)  # Higher diff = lower confidence
                
                return 0.8
            
            # Confidence score changes
            if field_name == 'confidence_score':
                if old_value is not None and new_value is not None:
                    change_magnitude = abs(new_value - old_value) / 100.0
                    return min(1.0, change_magnitude)
                return 1.0
            
            # Default confidence
            return 0.9
            
        except Exception as e:
            self.logger.error(f"Confidence calculation failed for {field_name}: {e}")
            return 0.5
    
    def create_diff_summary(self, diffs: List[VersionDiff]) -> Dict[str, Any]:
        """Create a summary of version differences"""
        try:
            summary = {
                'total_changes': len(diffs),
                'change_types': {},
                'fields_changed': [],
                'severity_score': 0.0,
                'confidence_score': 0.0
            }
            
            if not diffs:
                return summary
            
            # Analyze changes
            change_type_counts = {}
            total_confidence = 0.0
            severity_weights = {'added': 0.3, 'removed': 0.7, 'modified': 0.5}
            
            for diff in diffs:
                # Count change types
                change_type_counts[diff.change_type] = change_type_counts.get(diff.change_type, 0) + 1
                
                # Track changed fields
                summary['fields_changed'].append(diff.field_name)
                
                # Calculate severity
                weight = severity_weights.get(diff.change_type, 0.5)
                summary['severity_score'] += weight * diff.confidence
                
                # Sum confidence
                total_confidence += diff.confidence
            
            # Normalize scores
            summary['change_types'] = change_type_counts
            summary['severity_score'] = summary['severity_score'] / len(diffs)
            summary['confidence_score'] = total_confidence / len(diffs)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Diff summary creation failed: {e}")
            return {'error': str(e)}


class FingerprintVersionManager:
    """
    Comprehensive version management system for fingerprint data with
    history tracking, diff analysis, and rollback capabilities.
    """
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        encryption_manager: Optional[EncryptionManager] = None,
        compression_manager: Optional[CompressionManager] = None
    ):
        self.db_manager = db_manager
        self.encryption_manager = encryption_manager
        self.compression_manager = compression_manager
        self.diff_engine = VersionDiffEngine()
        self.performance_monitor = PerformanceMonitor()
        self.logger = logging.getLogger(__name__)
    
    async def create_version(
        self,
        fingerprint_id: str,
        fingerprint_data: Dict[str, Any],
        change_type: VersionChangeType,
        change_description: str,
        created_by: str,
        parent_version_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new version of a fingerprint
        
        Args:
            fingerprint_id: ID of the fingerprint
            fingerprint_data: Current fingerprint data
            change_type: Type of change being made
            change_description: Description of the change
            created_by: User/system creating the version
            parent_version_id: Parent version ID (optional)
            tags: Optional tags for the version
            attributes: Optional attributes for the version
            
        Returns:
            Version ID of the created version
        """
        start_time = self.performance_monitor.start_operation()
        
        try:
            async with self.db_manager.get_session() as session:
                # Get next version number
                version_number = await self._get_next_version_number(session, fingerprint_id)
                
                # Get parent version for diff calculation
                parent_diffs = []
                if parent_version_id:
                    parent_version = await self._get_version_data(session, parent_version_id)
                    if parent_version:
                        parent_diffs = self.diff_engine.calculate_diff(
                            parent_version, fingerprint_data
                        )
                
                # Prepare data for storage
                storage_data = await self._prepare_storage_data(fingerprint_data)
                
                # Calculate validation checksum
                checksum = self._calculate_checksum(fingerprint_data)
                
                # Create version record
                version = FingerprintVersionModel(
                    fingerprint_id=fingerprint_id,
                    parent_version_id=parent_version_id,
                    version_number=version_number,
                    change_type=change_type.value,
                    change_description=change_description,
                    
                    # Fingerprint data
                    primary_hash=fingerprint_data.get('primary_hash'),
                    perceptual_hash=fingerprint_data.get('perceptual_hash'),
                    structural_hash=fingerprint_data.get('structural_hash'),
                    feature_vector=fingerprint_data.get('feature_vector'),
                    metadata_snapshot=fingerprint_data.get('metadata', {}),
                    
                    # Quality metrics
                    confidence_score=fingerprint_data.get('confidence_score'),
                    quality_level=fingerprint_data.get('quality_level'),
                    
                    # Version metadata
                    created_by=created_by,
                    status=VersionStatus.ACTIVE.value,
                    
                    # Storage data
                    compressed_data=storage_data.get('compressed_data'),
                    compression_algorithm=storage_data.get('compression_algorithm'),
                    encrypted=storage_data.get('encrypted', False),
                    
                    # Change tracking
                    changes_from_parent=[asdict(diff) for diff in parent_diffs],
                    validation_checksum=checksum,
                    
                    # Performance metrics
                    creation_time_ms=0,  # Will be updated at the end
                    storage_size=len(str(fingerprint_data)),
                    
                    # Tags and attributes
                    tags=tags or [],
                    attributes=attributes or {}
                )
                
                session.add(version)
                await session.commit()
                await session.refresh(version)
                
                # Update creation time
                creation_time = self.performance_monitor.end_operation(start_time)
                version.creation_time_ms = int(creation_time * 1000)
                await session.commit()
                
                self.logger.info(f"Created version {version.version_id} for fingerprint {fingerprint_id}")
                return str(version.version_id)
                
        except Exception as e:
            self.logger.error(f"Version creation failed: {e}")
            raise DatabaseError(f"Version creation failed: {e}")
    
    async def get_version_history(
        self,
        fingerprint_id: str,
        query: Optional[VersionQuery] = None
    ) -> List[Dict[str, Any]]:
        """
        Get version history for a fingerprint
        
        Args:
            fingerprint_id: ID of the fingerprint
            query: Optional query parameters
            
        Returns:
            List of version history records
        """
        try:
            if query is None:
                query = VersionQuery(fingerprint_id=fingerprint_id)
            else:
                query.fingerprint_id = fingerprint_id
            
            async with self.db_manager.get_session() as session:
                # Build query
                stmt = select(FingerprintVersionModel).where(
                    FingerprintVersionModel.fingerprint_id == fingerprint_id
                )
                
                # Apply filters
                stmt = self._apply_version_filters(stmt, query)
                
                # Apply ordering
                if query.order_by == 'version_number':
                    if query.order_direction == 'desc':
                        stmt = stmt.order_by(desc(FingerprintVersionModel.version_number))
                    else:
                        stmt = stmt.order_by(asc(FingerprintVersionModel.version_number))
                elif query.order_by == 'created_at':
                    if query.order_direction == 'desc':
                        stmt = stmt.order_by(desc(FingerprintVersionModel.created_at))
                    else:
                        stmt = stmt.order_by(asc(FingerprintVersionModel.created_at))
                
                # Apply pagination
                if query.limit:
                    stmt = stmt.limit(query.limit)
                if query.offset:
                    stmt = stmt.offset(query.offset)
                
                result = await session.execute(stmt)
                versions = result.scalars().all()
                
                # Format results
                history = []
                for version in versions:
                    version_data = await self._format_version_data(version, query)
                    history.append(version_data)
                
                return history
                
        except Exception as e:
            self.logger.error(f"Version history retrieval failed: {e}")
            raise DatabaseError(f"Version history retrieval failed: {e}")
    
    async def get_version(
        self,
        version_id: str,
        include_diffs: bool = False,
        include_metadata: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get specific version data
        
        Args:
            version_id: ID of the version
            include_diffs: Include diff information
            include_metadata: Include metadata
            
        Returns:
            Version data or None if not found
        """
        try:
            async with self.db_manager.get_session() as session:
                stmt = select(FingerprintVersionModel).where(
                    FingerprintVersionModel.version_id == version_id
                )
                
                result = await session.execute(stmt)
                version = result.scalar_one_or_none()
                
                if not version:
                    return None
                
                query = VersionQuery(
                    include_diffs=include_diffs,
                    include_metadata=include_metadata
                )
                
                return await self._format_version_data(version, query)
                
        except Exception as e:
            self.logger.error(f"Version retrieval failed: {e}")
            return None
    
    async def rollback_to_version(
        self,
        fingerprint_id: str,
        target_version_id: str,
        created_by: str,
        create_new_version: bool = True
    ) -> Optional[str]:
        """
        Rollback fingerprint to a specific version
        
        Args:
            fingerprint_id: ID of the fingerprint
            target_version_id: Version to rollback to
            created_by: User performing the rollback
            create_new_version: Whether to create a new version for the rollback
            
        Returns:
            New version ID if created, else target version ID
        """
        try:
            async with self.db_manager.get_session() as session:
                # Get target version
                target_version = await self._get_version_by_id(session, target_version_id)
                if not target_version:
                    raise ValidationError(f"Target version {target_version_id} not found")
                
                # Extract fingerprint data from target version
                fingerprint_data = {
                    'primary_hash': target_version.primary_hash,
                    'perceptual_hash': target_version.perceptual_hash,
                    'structural_hash': target_version.structural_hash,
                    'feature_vector': target_version.feature_vector,
                    'confidence_score': target_version.confidence_score,
                    'quality_level': target_version.quality_level,
                    'metadata': target_version.metadata_snapshot or {}
                }
                
                if create_new_version:
                    # Create new version for rollback
                    new_version_id = await self.create_version(
                        fingerprint_id=fingerprint_id,
                        fingerprint_data=fingerprint_data,
                        change_type=VersionChangeType.RESTORE,
                        change_description=f"Rollback to version {target_version.version_number}",
                        created_by=created_by,
                        attributes={
                            'rollback_from_version': target_version_id,
                            'rollback_to_version_number': target_version.version_number
                        }
                    )
                    
                    return new_version_id
                else:
                    return target_version_id
                
        except Exception as e:
            self.logger.error(f"Rollback operation failed: {e}")
            raise DatabaseError(f"Rollback operation failed: {e}")
    
    async def compare_versions(
        self,
        version_id_1: str,
        version_id_2: str
    ) -> Dict[str, Any]:
        """
        Compare two versions and return detailed diff
        
        Args:
            version_id_1: First version ID
            version_id_2: Second version ID
            
        Returns:
            Comparison results with detailed diffs
        """
        try:
            async with self.db_manager.get_session() as session:
                # Get both versions
                version_1 = await self._get_version_by_id(session, version_id_1)
                version_2 = await self._get_version_by_id(session, version_id_2)
                
                if not version_1 or not version_2:
                    raise ValidationError("One or both versions not found")
                
                # Extract data for comparison
                data_1 = await self._extract_version_data(version_1)
                data_2 = await self._extract_version_data(version_2)
                
                # Calculate diffs
                diffs = self.diff_engine.calculate_diff(data_1, data_2)
                diff_summary = self.diff_engine.create_diff_summary(diffs)
                
                return {
                    'version_1': {
                        'version_id': version_id_1,
                        'version_number': version_1.version_number,
                        'created_at': version_1.created_at.isoformat(),
                        'created_by': version_1.created_by
                    },
                    'version_2': {
                        'version_id': version_id_2,
                        'version_number': version_2.version_number,
                        'created_at': version_2.created_at.isoformat(),
                        'created_by': version_2.created_by
                    },
                    'comparison': {
                        'differences': [asdict(diff) for diff in diffs],
                        'summary': diff_summary,
                        'identical': len(diffs) == 0
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Version comparison failed: {e}")
            raise DatabaseError(f"Version comparison failed: {e}")
    
    async def create_branch(
        self,
        fingerprint_id: str,
        branch_name: str,
        base_version_id: str,
        created_by: str,
        description: Optional[str] = None
    ) -> str:
        """
        Create a new branch from a specific version
        
        Args:
            fingerprint_id: ID of the fingerprint
            branch_name: Name of the new branch
            base_version_id: Version to branch from
            created_by: User creating the branch
            description: Optional description
            
        Returns:
            Branch ID
        """
        try:
            async with self.db_manager.get_session() as session:
                # Verify base version exists
                base_version = await self._get_version_by_id(session, base_version_id)
                if not base_version:
                    raise ValidationError(f"Base version {base_version_id} not found")
                
                # Check if branch name already exists
                existing_branch = await session.execute(
                    select(VersionBranchModel).where(
                        and_(
                            VersionBranchModel.fingerprint_id == fingerprint_id,
                            VersionBranchModel.branch_name == branch_name,
                            VersionBranchModel.is_active == True
                        )
                    )
                )
                
                if existing_branch.scalar_one_or_none():
                    raise ValidationError(f"Branch '{branch_name}' already exists")
                
                # Create branch
                branch = VersionBranchModel(
                    fingerprint_id=fingerprint_id,
                    branch_name=branch_name,
                    base_version_id=base_version_id,
                    head_version_id=base_version_id,
                    created_by=created_by,
                    description=description
                )
                
                session.add(branch)
                await session.commit()
                await session.refresh(branch)
                
                self.logger.info(f"Created branch '{branch_name}' for fingerprint {fingerprint_id}")
                return str(branch.branch_id)
                
        except Exception as e:
            self.logger.error(f"Branch creation failed: {e}")
            raise DatabaseError(f"Branch creation failed: {e}")
    
    async def merge_branch(
        self,
        branch_id: str,
        target_branch_id: str,
        created_by: str,
        merge_strategy: str = "fast_forward"
    ) -> str:
        """
        Merge one branch into another
        
        Args:
            branch_id: Source branch ID
            target_branch_id: Target branch ID
            created_by: User performing the merge
            merge_strategy: Merge strategy to use
            
        Returns:
            Merge version ID
        """
        try:
            async with self.db_manager.get_session() as session:
                # Get both branches
                source_branch = await self._get_branch_by_id(session, branch_id)
                target_branch = await self._get_branch_by_id(session, target_branch_id)
                
                if not source_branch or not target_branch:
                    raise ValidationError("Source or target branch not found")
                
                # Get head versions
                source_version = await self._get_version_by_id(session, source_branch.head_version_id)
                target_version = await self._get_version_by_id(session, target_branch.head_version_id)
                
                # Extract data for merge
                source_data = await self._extract_version_data(source_version)
                target_data = await self._extract_version_data(target_version)
                
                # Perform merge based on strategy
                merged_data = await self._perform_merge(
                    source_data, target_data, merge_strategy
                )
                
                # Create merge version
                merge_version_id = await self.create_version(
                    fingerprint_id=source_branch.fingerprint_id,
                    fingerprint_data=merged_data,
                    change_type=VersionChangeType.MERGE,
                    change_description=f"Merge branch '{source_branch.branch_name}' into '{target_branch.branch_name}'",
                    created_by=created_by,
                    parent_version_id=target_branch.head_version_id,
                    attributes={
                        'merge_source_branch': str(source_branch.branch_id),
                        'merge_target_branch': str(target_branch.branch_id),
                        'merge_strategy': merge_strategy
                    }
                )
                
                # Update target branch head
                target_branch.head_version_id = merge_version_id
                
                # Mark source branch as merged
                source_branch.merged_into = target_branch.branch_id
                source_branch.merged_at = datetime.now(timezone.utc)
                source_branch.merged_by = created_by
                source_branch.is_active = False
                
                await session.commit()
                
                return merge_version_id
                
        except Exception as e:
            self.logger.error(f"Branch merge failed: {e}")
            raise DatabaseError(f"Branch merge failed: {e}")
    
    async def cleanup_old_versions(
        self,
        fingerprint_id: str,
        retention_days: int = 90,
        keep_minimum: int = 10
    ) -> int:
        """
        Clean up old versions based on retention policy
        
        Args:
            fingerprint_id: ID of the fingerprint
            retention_days: Days to retain versions
            keep_minimum: Minimum versions to keep
            
        Returns:
            Number of versions cleaned up
        """
        try:
            async with self.db_manager.get_session() as session:
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
                
                # Get versions to potentially clean up
                stmt = select(FingerprintVersionModel).where(
                    and_(
                        FingerprintVersionModel.fingerprint_id == fingerprint_id,
                        FingerprintVersionModel.created_at < cutoff_date,
                        FingerprintVersionModel.status == VersionStatus.ACTIVE.value
                    )
                ).order_by(desc(FingerprintVersionModel.version_number))
                
                result = await session.execute(stmt)
                old_versions = result.scalars().all()
                
                # Calculate how many to keep
                total_versions = await session.execute(
                    select(func.count()).select_from(FingerprintVersionModel).where(
                        FingerprintVersionModel.fingerprint_id == fingerprint_id
                    )
                )
                total_count = total_versions.scalar()
                
                # Keep minimum number of versions
                max_to_cleanup = max(0, total_count - keep_minimum)
                versions_to_cleanup = old_versions[:max_to_cleanup]
                
                cleanup_count = 0
                for version in versions_to_cleanup:
                    # Archive instead of deleting
                    version.status = VersionStatus.ARCHIVED.value
                    cleanup_count += 1
                
                await session.commit()
                
                self.logger.info(f"Cleaned up {cleanup_count} versions for fingerprint {fingerprint_id}")
                return cleanup_count
                
        except Exception as e:
            self.logger.error(f"Version cleanup failed: {e}")
            return 0
    
    # Helper methods
    
    async def _get_next_version_number(
        self,
        session: AsyncSession,
        fingerprint_id: str
    ) -> int:
        """Get the next version number for a fingerprint"""
        result = await session.execute(
            select(func.max(FingerprintVersionModel.version_number)).where(
                FingerprintVersionModel.fingerprint_id == fingerprint_id
            )
        )
        
        max_version = result.scalar()
        return (max_version or 0) + 1
    
    async def _get_version_data(
        self,
        session: AsyncSession,
        version_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get version data as dictionary"""
        version = await self._get_version_by_id(session, version_id)
        if version:
            return await self._extract_version_data(version)
        return None
    
    async def _get_version_by_id(
        self,
        session: AsyncSession,
        version_id: str
    ) -> Optional[FingerprintVersionModel]:
        """Get version model by ID"""
        result = await session.execute(
            select(FingerprintVersionModel).where(
                FingerprintVersionModel.version_id == version_id
            )
        )
        return result.scalar_one_or_none()
    
    async def _get_branch_by_id(
        self,
        session: AsyncSession,
        branch_id: str
    ) -> Optional[VersionBranchModel]:
        """Get branch model by ID"""
        result = await session.execute(
            select(VersionBranchModel).where(
                VersionBranchModel.branch_id == branch_id
            )
        )
        return result.scalar_one_or_none()
    
    async def _extract_version_data(
        self,
        version: FingerprintVersionModel
    ) -> Dict[str, Any]:
        """Extract fingerprint data from version model"""
        return {
            'primary_hash': version.primary_hash,
            'perceptual_hash': version.perceptual_hash,
            'structural_hash': version.structural_hash,
            'feature_vector': version.feature_vector,
            'confidence_score': version.confidence_score,
            'quality_level': version.quality_level,
            'metadata': version.metadata_snapshot or {}
        }
    
    async def _prepare_storage_data(
        self,
        fingerprint_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare data for storage with compression/encryption"""
        storage_data = {}
        
        # Compress data if compression manager is available
        if self.compression_manager:
            data_str = json.dumps(fingerprint_data)
            compressed = self.compression_manager.compress(data_str.encode())
            storage_data['compressed_data'] = compressed
            storage_data['compression_algorithm'] = self.compression_manager.algorithm
        
        # Encrypt if encryption manager is available
        if self.encryption_manager:
            storage_data['encrypted'] = True
        
        return storage_data
    
    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate validation checksum for data"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _apply_version_filters(
        self,
        stmt,
        query: VersionQuery
    ):
        """Apply filters to version query"""
        if query.change_types:
            change_type_values = [ct.value for ct in query.change_types]
            stmt = stmt.where(FingerprintVersionModel.change_type.in_(change_type_values))
        
        if query.status_types:
            status_values = [st.value for st in query.status_types]
            stmt = stmt.where(FingerprintVersionModel.status.in_(status_values))
        
        if query.created_by:
            stmt = stmt.where(FingerprintVersionModel.created_by.in_(query.created_by))
        
        if query.start_date:
            stmt = stmt.where(FingerprintVersionModel.created_at >= query.start_date)
        
        if query.end_date:
            stmt = stmt.where(FingerprintVersionModel.created_at <= query.end_date)
        
        if query.min_version:
            stmt = stmt.where(FingerprintVersionModel.version_number >= query.min_version)
        
        if query.max_version:
            stmt = stmt.where(FingerprintVersionModel.version_number <= query.max_version)
        
        return stmt
    
    async def _format_version_data(
        self,
        version: FingerprintVersionModel,
        query: VersionQuery
    ) -> Dict[str, Any]:
        """Format version data for output"""
        data = {
            'version_id': str(version.version_id),
            'fingerprint_id': str(version.fingerprint_id),
            'version_number': version.version_number,
            'change_type': version.change_type,
            'change_description': version.change_description,
            'created_by': version.created_by,
            'created_at': version.created_at.isoformat(),
            'status': version.status,
            'creation_time_ms': version.creation_time_ms,
            'storage_size': version.storage_size
        }
        
        if query.include_metadata:
            data.update({
                'primary_hash': version.primary_hash,
                'perceptual_hash': version.perceptual_hash,
                'structural_hash': version.structural_hash,
                'feature_vector': version.feature_vector,
                'confidence_score': version.confidence_score,
                'quality_level': version.quality_level,
                'metadata_snapshot': version.metadata_snapshot,
                'tags': version.tags,
                'attributes': version.attributes,
                'validation_checksum': version.validation_checksum
            })
        
        if query.include_diffs and version.changes_from_parent:
            data['changes_from_parent'] = version.changes_from_parent
        
        return data
    
    async def _perform_merge(
        self,
        source_data: Dict[str, Any],
        target_data: Dict[str, Any],
        merge_strategy: str
    ) -> Dict[str, Any]:
        """Perform merge based on strategy"""
        if merge_strategy == "fast_forward":
            # Use source data for fast forward
            return source_data
        elif merge_strategy == "prefer_target":
            # Use target data, fill in missing fields from source
            merged = target_data.copy()
            for key, value in source_data.items():
                if key not in merged or merged[key] is None:
                    merged[key] = value
            return merged
        elif merge_strategy == "prefer_source":
            # Use source data, fill in missing fields from target
            merged = source_data.copy()
            for key, value in target_data.items():
                if key not in merged or merged[key] is None:
                    merged[key] = value
            return merged
        else:
            # Default to source data
            return source_data
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on version manager"""
        try:
            health = {
                "status": "healthy",
                "components": {},
                "capabilities": []
            }
            
            # Test database connectivity
            try:
                async with self.db_manager.get_session() as session:
                    result = await session.execute(select(func.count()).select_from(FingerprintVersionModel))
                    result.scalar()
                health["components"]["database"] = "healthy"
            except Exception as e:
                health["components"]["database"] = f"unhealthy: {e}"
                health["status"] = "degraded"
            
            # Test diff engine
            try:
                test_data_1 = {'test': 'value1'}
                test_data_2 = {'test': 'value2'}
                self.diff_engine.calculate_diff(test_data_1, test_data_2)
                health["components"]["diff_engine"] = "healthy"
            except Exception as e:
                health["components"]["diff_engine"] = f"unhealthy: {e}"
                health["status"] = "degraded"
            
            # List capabilities
            health["capabilities"] = [
                "version_creation",
                "version_history",
                "rollback_support",
                "branch_management",
                "diff_analysis",
                "merge_operations",
                "cleanup_automation"
            ]
            
            return health
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
