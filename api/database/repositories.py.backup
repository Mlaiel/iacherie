"""Database Repositories - IA Influencer Agent Platform
Enterprise-grade repository pattern implementation with advanced features

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead AI Developer, Senior Backend Engineer, ML Engineer, 
Database Administrator, Security Expert, Microservices Architect, Audio Engineer, 
DevOps Engineer, AI Prompt Engineer

WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Union, Type, Tuple, Generic, TypeVar
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_, func, text, select, insert, update, delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.sql import Select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
from contextlib import asynccontextmanager

from ..core.logging import get_logger
from ..models.database import (
    User, Creator, Content, Media, Copyright, License, 
    Collaboration, Project, Revenue, Distribution, 
    Analytics, Notification, ContentFingerprint, 
    ProtectionAlert, RevenueTracking
)
from ..schemas.database import (
    UserCreate, UserUpdate, CreatorCreate, CreatorUpdate,
    ContentCreate, ContentUpdate, MediaCreate, MediaUpdate,
    CopyrightCreate, CopyrightUpdate, LicenseCreate, LicenseUpdate
)
from .connection import DatabaseConnection, SessionManager, TransactionManager

logger = get_logger(__name__)

T = TypeVar('T')  # Generic type for model
CreateSchemaType = TypeVar('CreateSchemaType')
UpdateSchemaType = TypeVar('UpdateSchemaType')


class SortOrder(Enum):
    """Sort order enumeration"""
    ASC = "asc"
    DESC = "desc"


@dataclass
class QueryFilter:
    """Query filter definition"""
    field: str
    operator: str  # eq, ne, gt, gte, lt, lte, in, not_in, like, ilike, is_null, is_not_null
    value: Any
    table_alias: Optional[str] = None


@dataclass
class QuerySort:
    """Query sort definition"""
    field: str
    order: SortOrder = SortOrder.ASC
    table_alias: Optional[str] = None


@dataclass
class QueryPagination:
    """Query pagination definition"""
    page: int = 1
    page_size: int = 50
    max_page_size: int = 1000


@dataclass
class RepositoryResult:
    """Repository operation result"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseRepository(ABC, Generic[T, CreateSchemaType, UpdateSchemaType]):
    """
    Abstract base repository with enterprise features:
    - Async/sync operations
    - Advanced querying with filters, sorting, pagination
    - Bulk operations
    - Caching integration
    - Audit logging
    - Multi-tenant support
    """
    
    def __init__(self, model: Type[T]):
        self.model = model
        self.model_name = model.__name__
        self.session_manager = SessionManager()
        self.transaction_manager = TransactionManager()
        self.db_connection = None
        self.cache = None
        self.audit_enabled = True
        
    async def initialize_integrations(self, services: Dict[str, Any]):
        """Initialize repository with external services"""
        self.db_connection = services.get('connection')
        self.cache = services.get('cache')
        await self.session_manager.initialize()
        
    # === CRUD Operations ===
    
    async def create(self, 
                    data: CreateSchemaType, 
                    user_id: Optional[str] = None,
                    commit: bool = True) -> RepositoryResult:
        """Create a new record"""
        try:
            async with self.session_manager.get_async_session() as session:
                # Convert schema to model
                create_data = data.model_dump() if hasattr(data, 'model_dump') else data
                
                # Add audit fields
                if hasattr(self.model, 'created_at'):
                    create_data['created_at'] = datetime.utcnow()
                if hasattr(self.model, 'created_by') and user_id:
                    create_data['created_by'] = user_id
                if hasattr(self.model, 'id') and 'id' not in create_data:
                    create_data['id'] = str(uuid.uuid4())
                
                # Create instance
                instance = self.model(**create_data)
                session.add(instance)
                
                if commit:
                    await session.commit()
                    await session.refresh(instance)
                
                # Log audit event
                await self._log_audit_event('create', instance.id, user_id, create_data)
                
                return RepositoryResult(
                    success=True,
                    data=instance,
                    metadata={'operation': 'create', 'record_id': instance.id}
                )
                
        except IntegrityError as e:
            logger.error(f"Integrity error creating {self.model_name}: {e}")
            return RepositoryResult(
                success=False,
                error=f"Duplicate or constraint violation: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error creating {self.model_name}: {e}")
            return RepositoryResult(
                success=False,
                error=f"Creation failed: {str(e)}"
            )
    
    async def get_by_id(self, 
                       record_id: str,
                       include_deleted: bool = False,
                       use_cache: bool = True) -> RepositoryResult:
        """Get record by ID with caching support"""
        try:
            # Check cache first
            cache_key = f"{self.model_name}:{record_id}"
            if use_cache and self.cache:
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    return RepositoryResult(success=True, data=cached_result)
            
            async with self.session_manager.get_async_session() as session:
                query = select(self.model).where(self.model.id == record_id)
                
                # Handle soft deletes
                if hasattr(self.model, 'deleted_at') and not include_deleted:
                    query = query.where(self.model.deleted_at.is_(None))
                
                result = await session.execute(query)
                instance = result.scalar_one_or_none()
                
                if instance:
                    # Cache result
                    if use_cache and self.cache:
                        await self.cache.set(cache_key, instance, expire=300)
                    
                    return RepositoryResult(success=True, data=instance)
                else:
                    return RepositoryResult(
                        success=False,
                        error=f"{self.model_name} with id {record_id} not found"
                    )
                    
        except Exception as e:
            logger.error(f"Error getting {self.model_name} by id {record_id}: {e}")
            return RepositoryResult(
                success=False,
                error=f"Retrieval failed: {str(e)}"
            )
    
    async def update(self, 
                    record_id: str,
                    data: UpdateSchemaType,
                    user_id: Optional[str] = None,
                    commit: bool = True) -> RepositoryResult:
        """Update record with audit logging"""
        try:
            async with self.session_manager.get_async_session() as session:
                # Get existing record
                existing_result = await self.get_by_id(record_id, use_cache=False)
                if not existing_result.success:
                    return existing_result
                
                existing_instance = existing_result.data
                
                # Update data
                update_data = data.model_dump(exclude_unset=True) if hasattr(data, 'model_dump') else data
                
                # Add audit fields
                if hasattr(self.model, 'updated_at'):
                    update_data['updated_at'] = datetime.utcnow()
                if hasattr(self.model, 'updated_by') and user_id:
                    update_data['updated_by'] = user_id
                
                # Apply updates
                for field, value in update_data.items():
                    if hasattr(existing_instance, field):
                        setattr(existing_instance, field, value)
                
                if commit:
                    await session.commit()
                    await session.refresh(existing_instance)
                
                # Invalidate cache
                if self.cache:
                    cache_key = f"{self.model_name}:{record_id}"
                    await self.cache.delete(cache_key)
                
                # Log audit event
                await self._log_audit_event('update', record_id, user_id, update_data)
                
                return RepositoryResult(
                    success=True,
                    data=existing_instance,
                    metadata={'operation': 'update', 'record_id': record_id}
                )
                
        except Exception as e:
            logger.error(f"Error updating {self.model_name} {record_id}: {e}")
            return RepositoryResult(
                success=False,
                error=f"Update failed: {str(e)}"
            )
    
    async def delete(self, 
                    record_id: str,
                    user_id: Optional[str] = None,
                    soft_delete: bool = True,
                    commit: bool = True) -> RepositoryResult:
        """Delete record (soft or hard)"""
        try:
            async with self.session_manager.get_async_session() as session:
                # Get existing record
                existing_result = await self.get_by_id(record_id, use_cache=False)
                if not existing_result.success:
                    return existing_result
                
                existing_instance = existing_result.data
                
                if soft_delete and hasattr(self.model, 'deleted_at'):
                    # Soft delete
                    existing_instance.deleted_at = datetime.utcnow()
                    if hasattr(self.model, 'deleted_by') and user_id:
                        existing_instance.deleted_by = user_id
                else:
                    # Hard delete
                    await session.delete(existing_instance)
                
                if commit:
                    await session.commit()
                
                # Invalidate cache
                if self.cache:
                    cache_key = f"{self.model_name}:{record_id}"
                    await self.cache.delete(cache_key)
                
                # Log audit event
                delete_type = 'soft_delete' if soft_delete else 'hard_delete'
                await self._log_audit_event(delete_type, record_id, user_id)
                
                return RepositoryResult(
                    success=True,
                    metadata={'operation': delete_type, 'record_id': record_id}
                )
                
        except Exception as e:
            logger.error(f"Error deleting {self.model_name} {record_id}: {e}")
            return RepositoryResult(
                success=False,
                error=f"Deletion failed: {str(e)}"
            )
    
    # === Query Operations ===
    
    async def find_many(self,
                       filters: Optional[List[QueryFilter]] = None,
                       sorting: Optional[List[QuerySort]] = None,
                       pagination: Optional[QueryPagination] = None,
                       include_deleted: bool = False,
                       include_count: bool = False) -> RepositoryResult:
        """Advanced query with filters, sorting, and pagination"""
        try:
            async with self.session_manager.get_async_session() as session:
                # Build base query
                query = select(self.model)
                
                # Apply filters
                query = self._apply_filters(query, filters)
                
                # Handle soft deletes
                if hasattr(self.model, 'deleted_at') and not include_deleted:
                    query = query.where(self.model.deleted_at.is_(None))
                
                # Get total count if needed
                total_count = None
                if include_count:
                    count_query = select(func.count()).select_from(query.alias())
                    count_result = await session.execute(count_query)
                    total_count = count_result.scalar()
                
                # Apply sorting
                query = self._apply_sorting(query, sorting)
                
                # Apply pagination
                if pagination:
                    offset = (pagination.page - 1) * pagination.page_size
                    query = query.offset(offset).limit(pagination.page_size)
                
                # Execute query
                result = await session.execute(query)
                instances = result.scalars().all()
                
                metadata = {'operation': 'find_many'}
                if total_count is not None:
                    metadata['total_count'] = total_count
                if pagination:
                    metadata.update({
                        'page': pagination.page,
                        'page_size': pagination.page_size,
                        'has_next': len(instances) == pagination.page_size
                    })
                
                return RepositoryResult(
                    success=True,
                    data=instances,
                    metadata=metadata
                )
                
        except Exception as e:
            logger.error(f"Error finding {self.model_name} records: {e}")
            return RepositoryResult(
                success=False,
                error=f"Query failed: {str(e)}"
            )
    
    async def find_one(self,
                      filters: List[QueryFilter],
                      include_deleted: bool = False) -> RepositoryResult:
        """Find single record by filters"""
        try:
            async with self.session_manager.get_async_session() as session:
                query = select(self.model)
                
                # Apply filters
                query = self._apply_filters(query, filters)
                
                # Handle soft deletes
                if hasattr(self.model, 'deleted_at') and not include_deleted:
                    query = query.where(self.model.deleted_at.is_(None))
                
                result = await session.execute(query)
                instance = result.scalar_one_or_none()
                
                if instance:
                    return RepositoryResult(success=True, data=instance)
                else:
                    return RepositoryResult(
                        success=False,
                        error=f"No {self.model_name} found matching criteria"
                    )
                    
        except Exception as e:
            logger.error(f"Error finding {self.model_name} record: {e}")
            return RepositoryResult(
                success=False,
                error=f"Query failed: {str(e)}"
            )
    
    # === Bulk Operations ===
    
    async def bulk_create(self,
                         data_list: List[CreateSchemaType],
                         user_id: Optional[str] = None,
                         batch_size: int = 1000) -> RepositoryResult:
        """Bulk create records with batching"""
        try:
            created_records = []
            total_batches = (len(data_list) + batch_size - 1) // batch_size
            
            async with self.transaction_manager.transaction() as session:
                for batch_num in range(total_batches):
                    start_idx = batch_num * batch_size
                    end_idx = min(start_idx + batch_size, len(data_list))
                    batch_data = data_list[start_idx:end_idx]
                    
                    # Process batch
                    batch_records = []
                    for data in batch_data:
                        create_data = data.model_dump() if hasattr(data, 'model_dump') else data
                        
                        # Add audit fields
                        if hasattr(self.model, 'created_at'):
                            create_data['created_at'] = datetime.utcnow()
                        if hasattr(self.model, 'created_by') and user_id:
                            create_data['created_by'] = user_id
                        if hasattr(self.model, 'id') and 'id' not in create_data:
                            create_data['id'] = str(uuid.uuid4())
                        
                        instance = self.model(**create_data)
                        batch_records.append(instance)
                    
                    # Add batch to session
                    session.add_all(batch_records)
                    created_records.extend(batch_records)
                
                # Commit all batches
                await session.commit()
                
                # Log audit event
                await self._log_audit_event(
                    'bulk_create', 
                    'multiple', 
                    user_id, 
                    {'count': len(created_records)}
                )
                
                return RepositoryResult(
                    success=True,
                    data=created_records,
                    metadata={
                        'operation': 'bulk_create',
                        'total_created': len(created_records),
                        'batch_count': total_batches
                    }
                )
                
        except Exception as e:
            logger.error(f"Error bulk creating {self.model_name} records: {e}")
            return RepositoryResult(
                success=False,
                error=f"Bulk creation failed: {str(e)}"
            )
    
    async def bulk_update(self,
                         updates: List[Dict[str, Any]],
                         user_id: Optional[str] = None,
                         batch_size: int = 1000) -> RepositoryResult:
        """Bulk update records"""
        try:
            updated_count = 0
            total_batches = (len(updates) + batch_size - 1) // batch_size
            
            async with self.transaction_manager.transaction() as session:
                for batch_num in range(total_batches):
                    start_idx = batch_num * batch_size
                    end_idx = min(start_idx + batch_size, len(updates))
                    batch_updates = updates[start_idx:end_idx]
                    
                    for update_data in batch_updates:
                        record_id = update_data.pop('id')
                        
                        # Add audit fields
                        if hasattr(self.model, 'updated_at'):
                            update_data['updated_at'] = datetime.utcnow()
                        if hasattr(self.model, 'updated_by') and user_id:
                            update_data['updated_by'] = user_id
                        
                        # Execute update
                        query = update(self.model).where(
                            self.model.id == record_id
                        ).values(**update_data)
                        
                        result = await session.execute(query)
                        updated_count += result.rowcount
                
                await session.commit()
                
                # Log audit event
                await self._log_audit_event(
                    'bulk_update',
                    'multiple',
                    user_id,
                    {'count': updated_count}
                )
                
                return RepositoryResult(
                    success=True,
                    metadata={
                        'operation': 'bulk_update',
                        'total_updated': updated_count,
                        'batch_count': total_batches
                    }
                )
                
        except Exception as e:
            logger.error(f"Error bulk updating {self.model_name} records: {e}")
            return RepositoryResult(
                success=False,
                error=f"Bulk update failed: {str(e)}"
            )
    
    async def bulk_delete(self,
                         record_ids: List[str],
                         user_id: Optional[str] = None,
                         soft_delete: bool = True) -> RepositoryResult:
        """Bulk delete records"""
        try:
            async with self.transaction_manager.transaction() as session:
                if soft_delete and hasattr(self.model, 'deleted_at'):
                    # Soft delete
                    update_data = {'deleted_at': datetime.utcnow()}
                    if hasattr(self.model, 'deleted_by') and user_id:
                        update_data['deleted_by'] = user_id
                    
                    query = update(self.model).where(
                        self.model.id.in_(record_ids)
                    ).values(**update_data)
                    
                    result = await session.execute(query)
                    deleted_count = result.rowcount
                else:
                    # Hard delete
                    query = delete(self.model).where(
                        self.model.id.in_(record_ids)
                    )
                    
                    result = await session.execute(query)
                    deleted_count = result.rowcount
                
                await session.commit()
                
                # Log audit event
                delete_type = 'bulk_soft_delete' if soft_delete else 'bulk_hard_delete'
                await self._log_audit_event(
                    delete_type,
                    'multiple',
                    user_id,
                    {'count': deleted_count, 'record_ids': record_ids}
                )
                
                return RepositoryResult(
                    success=True,
                    metadata={
                        'operation': delete_type,
                        'total_deleted': deleted_count
                    }
                )
                
        except Exception as e:
            logger.error(f"Error bulk deleting {self.model_name} records: {e}")
            return RepositoryResult(
                success=False,
                error=f"Bulk deletion failed: {str(e)}"
            )
    
    # === Utility Methods ===
    
    def _apply_filters(self, query: Select, filters: Optional[List[QueryFilter]]) -> Select:
        """Apply filters to query"""
        if not filters:
            return query
        
        for filter_item in filters:
            field = getattr(self.model, filter_item.field)
            
            if filter_item.operator == 'eq':
                query = query.where(field == filter_item.value)
            elif filter_item.operator == 'ne':
                query = query.where(field != filter_item.value)
            elif filter_item.operator == 'gt':
                query = query.where(field > filter_item.value)
            elif filter_item.operator == 'gte':
                query = query.where(field >= filter_item.value)
            elif filter_item.operator == 'lt':
                query = query.where(field < filter_item.value)
            elif filter_item.operator == 'lte':
                query = query.where(field <= filter_item.value)
            elif filter_item.operator == 'in':
                query = query.where(field.in_(filter_item.value))
            elif filter_item.operator == 'not_in':
                query = query.where(~field.in_(filter_item.value))
            elif filter_item.operator == 'like':
                query = query.where(field.like(filter_item.value))
            elif filter_item.operator == 'ilike':
                query = query.where(field.ilike(filter_item.value))
            elif filter_item.operator == 'is_null':
                query = query.where(field.is_(None))
            elif filter_item.operator == 'is_not_null':
                query = query.where(field.is_not(None))
        
        return query
    
    def _apply_sorting(self, query: Select, sorting: Optional[List[QuerySort]]) -> Select:
        """Apply sorting to query"""
        if not sorting:
            return query
        
        for sort_item in sorting:
            field = getattr(self.model, sort_item.field)
            
            if sort_item.order == SortOrder.DESC:
                query = query.order_by(field.desc())
            else:
                query = query.order_by(field.asc())
        
        return query
    
    async def _log_audit_event(self,
                              operation: str,
                              record_id: str,
                              user_id: Optional[str] = None,
                              data: Optional[Dict[str, Any]] = None):
        """Log audit event"""
        if not self.audit_enabled:
            return
        
        try:
            audit_data = {
                'operation': operation,
                'table_name': self.model.__tablename__,
                'record_id': record_id,
                'user_id': user_id,
                'data': data,
                'timestamp': datetime.utcnow()
            }
            
            # Log to audit system (implement based on requirements)
            logger.info(f"Audit: {operation} on {self.model_name}", extra=audit_data)
            
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")


# === Specific Repository Implementations ===

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """User repository with specific user operations"""
    
    def __init__(self):
        super().__init__(User)
    
    async def find_by_email(self, email: str) -> RepositoryResult:
        """Find user by email"""
        filters = [QueryFilter(field='email', operator='eq', value=email)]
        return await self.find_one(filters)
    
    async def find_by_username(self, username: str) -> RepositoryResult:
        """Find user by username"""
        filters = [QueryFilter(field='username', operator='eq', value=username)]
        return await self.find_one(filters)
    
    async def find_active_users(self, pagination: Optional[QueryPagination] = None) -> RepositoryResult:
        """Find all active users"""
        filters = [QueryFilter(field='is_active', operator='eq', value=True)]
        return await self.find_many(filters=filters, pagination=pagination)
    
    async def update_last_login(self, user_id: str) -> RepositoryResult:
        """Update user's last login timestamp"""
        update_data = {'last_login_at': datetime.utcnow()}
        return await self.update(user_id, update_data)


class CreatorRepository(BaseRepository[Creator, CreatorCreate, CreatorUpdate]):
    """Creator repository with creator-specific operations"""
    
    def __init__(self):
        super().__init__(Creator)
    
    async def find_by_user_id(self, user_id: str) -> RepositoryResult:
        """Find creator by user ID"""
        filters = [QueryFilter(field='user_id', operator='eq', value=user_id)]
        return await self.find_one(filters)
    
    async def find_verified_creators(self, pagination: Optional[QueryPagination] = None) -> RepositoryResult:
        """Find all verified creators"""
        filters = [QueryFilter(field='is_verified', operator='eq', value=True)]
        return await self.find_many(filters=filters, pagination=pagination)
    
    async def find_by_content_type(self, content_type: str, pagination: Optional[QueryPagination] = None) -> RepositoryResult:
        """Find creators by content type"""
        filters = [QueryFilter(field='content_types', operator='like', value=f'%{content_type}%')]
        return await self.find_many(filters=filters, pagination=pagination)


class ContentRepository(BaseRepository[Content, ContentCreate, ContentUpdate]):
    """Content repository with content-specific operations"""
    
    def __init__(self):
        super().__init__(Content)
    
    async def find_by_creator_id(self, creator_id: str, pagination: Optional[QueryPagination] = None) -> RepositoryResult:
        """Find content by creator ID"""
        filters = [QueryFilter(field='creator_id', operator='eq', value=creator_id)]
        return await self.find_many(filters=filters, pagination=pagination)
    
    async def find_by_type(self, content_type: str, pagination: Optional[QueryPagination] = None) -> RepositoryResult:
        """Find content by type"""
        filters = [QueryFilter(field='content_type', operator='eq', value=content_type)]
        return await self.find_many(filters=filters, pagination=pagination)
    
    async def find_published_content(self, pagination: Optional[QueryPagination] = None) -> RepositoryResult:
        """Find all published content"""
        filters = [QueryFilter(field='status', operator='eq', value='published')]
        return await self.find_many(filters=filters, pagination=pagination)
    
    async def find_recent_content(self, days: int = 7, pagination: Optional[QueryPagination] = None) -> RepositoryResult:
        """Find recent content within specified days"""
        since_date = datetime.utcnow() - timedelta(days=days)
        filters = [QueryFilter(field='created_at', operator='gte', value=since_date)]
        return await self.find_many(filters=filters, pagination=pagination)


class MediaRepository(BaseRepository[Media, MediaCreate, MediaUpdate]):
    """Media repository with media-specific operations"""
    
    def __init__(self):
        super().__init__(Media)
    
    async def find_by_content_id(self, content_id: str) -> RepositoryResult:
        """Find media by content ID"""
        filters = [QueryFilter(field='content_id', operator='eq', value=content_id)]
        return await self.find_many(filters=filters)
    
    async def find_by_media_type(self, media_type: str, pagination: Optional[QueryPagination] = None) -> RepositoryResult:
        """Find media by type"""
        filters = [QueryFilter(field='media_type', operator='eq', value=media_type)]
        return await self.find_many(filters=filters, pagination=pagination)
    
    async def get_total_storage_size(self) -> RepositoryResult:
        """Get total storage size across all media"""
        try:
            async with self.session_manager.get_async_session() as session:
                query = select(func.sum(Media.file_size))
                result = await session.execute(query)
                total_size = result.scalar() or 0
                
                return RepositoryResult(
                    success=True,
                    data=total_size,
                    metadata={'operation': 'storage_calculation'}
                )
        except Exception as e:
            logger.error(f"Error calculating total storage size: {e}")
            return RepositoryResult(success=False, error=str(e))


class CopyrightRepository(BaseRepository[Copyright, CopyrightCreate, CopyrightUpdate]):
    """Copyright repository with copyright-specific operations"""
    
    def __init__(self):
        super().__init__(Copyright)
    
    async def find_by_content_id(self, content_id: str) -> RepositoryResult:
        """Find copyright by content ID"""
        filters = [QueryFilter(field='content_id', operator='eq', value=content_id)]
        return await self.find_one(filters)
    
    async def find_expiring_copyrights(self, days_ahead: int = 30) -> RepositoryResult:
        """Find copyrights expiring within specified days"""
        expiry_date = datetime.utcnow() + timedelta(days=days_ahead)
        filters = [
            QueryFilter(field='expiry_date', operator='lte', value=expiry_date),
            QueryFilter(field='expiry_date', operator='gt', value=datetime.utcnow())
        ]
        return await self.find_many(filters=filters)


class LicenseRepository(BaseRepository[License, LicenseCreate, LicenseUpdate]):
    """License repository with licensing operations"""
    
    def __init__(self):
        super().__init__(License)
    
    async def find_by_content_id(self, content_id: str) -> RepositoryResult:
        """Find licenses by content ID"""
        filters = [QueryFilter(field='content_id', operator='eq', value=content_id)]
        return await self.find_many(filters=filters)
    
    async def find_active_licenses(self, pagination: Optional[QueryPagination] = None) -> RepositoryResult:
        """Find all active licenses"""
        filters = [QueryFilter(field='is_active', operator='eq', value=True)]
        return await self.find_many(filters=filters, pagination=pagination)


class CollaborationRepository(BaseRepository[Collaboration, Dict[str, Any], Dict[str, Any]]):
    """Collaboration repository"""
    
    def __init__(self):
        super().__init__(Collaboration)
    
    async def find_by_creator_id(self, creator_id: str, pagination: Optional[QueryPagination] = None) -> RepositoryResult:
        """Find collaborations by creator ID"""
        filters = [
            QueryFilter(field='initiator_id', operator='eq', value=creator_id)
        ]
        return await self.find_many(filters=filters, pagination=pagination)
    
    async def find_pending_collaborations(self, creator_id: str) -> RepositoryResult:
        """Find pending collaborations for a creator"""
        filters = [
            QueryFilter(field='collaborator_id', operator='eq', value=creator_id),
            QueryFilter(field='status', operator='eq', value='pending')
        ]
        return await self.find_many(filters=filters)


class ProjectRepository(BaseRepository[Project, Dict[str, Any], Dict[str, Any]]):
    """Project repository"""
    
    def __init__(self):
        super().__init__(Project)


class RevenueRepository(BaseRepository[Revenue, Dict[str, Any], Dict[str, Any]]):
    """Revenue repository with financial operations"""
    
    def __init__(self):
        super().__init__(Revenue)
    
    async def get_total_revenue_by_creator(self, creator_id: str, start_date: Optional[datetime] = None) -> RepositoryResult:
        """Get total revenue for a creator"""
        try:
            async with self.session_manager.get_async_session() as session:
                query = select(func.sum(Revenue.amount)).where(Revenue.creator_id == creator_id)
                
                if start_date:
                    query = query.where(Revenue.created_at >= start_date)
                
                result = await session.execute(query)
                total_revenue = result.scalar() or 0
                
                return RepositoryResult(
                    success=True,
                    data=total_revenue,
                    metadata={'creator_id': creator_id, 'start_date': start_date}
                )
        except Exception as e:
            logger.error(f"Error calculating revenue for creator {creator_id}: {e}")
            return RepositoryResult(success=False, error=str(e))


class DistributionRepository(BaseRepository[Distribution, Dict[str, Any], Dict[str, Any]]):
    """Distribution repository"""
    
    def __init__(self):
        super().__init__(Distribution)


class AnalyticsRepository(BaseRepository[Analytics, Dict[str, Any], Dict[str, Any]]):
    """Analytics repository with analytics-specific operations"""
    
    def __init__(self):
        super().__init__(Analytics)
    
    async def get_content_analytics(self, content_id: str, metric_type: Optional[str] = None) -> RepositoryResult:
        """Get analytics for specific content"""
        filters = [QueryFilter(field='content_id', operator='eq', value=content_id)]
        
        if metric_type:
            filters.append(QueryFilter(field='metric_type', operator='eq', value=metric_type))
        
        return await self.find_many(filters=filters)


class NotificationRepository(BaseRepository[Notification, Dict[str, Any], Dict[str, Any]]):
    """Notification repository"""
    
    def __init__(self):
        super().__init__(Notification)
    
    async def find_unread_notifications(self, user_id: str) -> RepositoryResult:
        """Find unread notifications for a user"""
        filters = [
            QueryFilter(field='user_id', operator='eq', value=user_id),
            QueryFilter(field='read_at', operator='is_null', value=None)
        ]
        return await self.find_many(filters=filters)
    
    async def mark_as_read(self, notification_id: str) -> RepositoryResult:
        """Mark notification as read"""
        update_data = {'read_at': datetime.utcnow()}
        return await self.update(notification_id, update_data)
