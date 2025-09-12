"""{{repository_name}} Repository Template for Ainflue Platform
{{repository_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
DBA Role: Enterprise Repository Pattern with advanced data access features
"""

import logging
from typing import Dict, Any, Optional, List, Union, Tuple, Type, Generic, TypeVar
from datetime import datetime, timezone
from uuid import UUID
from abc import ABC, abstractmethod
import asyncio
from contextlib import asynccontextmanager

from sqlalchemy import (
    select, insert, update, delete, func, and_, or_, not_, exists,
    text, case, cast, literal_column, desc, asc
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload, joinedload, contains_eager
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.sql import Select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from core.database import get_session
from core.config import get_settings
from utils.exceptions import (
    NotFoundError, 
    DuplicateError,
    ValidationError,
    DatabaseError,
    PermissionError
)

logger = logging.getLogger(__name__)
settings = get_settings()

# Type variables for generic repository
ModelType = TypeVar('ModelType')
CreateSchemaType = TypeVar('CreateSchemaType')
UpdateSchemaType = TypeVar('UpdateSchemaType')


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """Abstract base repository with common data access patterns
    
    Provides enterprise-grade data access layer with:
    - CRUD operations with advanced filtering
    - Bulk operations for performance
    - Transaction management
    - Audit trail support
    - Soft delete functionality
    - Multi-tenant support
    - Caching integration
    - Search capabilities
    - Performance optimization
    - Error handling and logging
    """
    
    def __init__(self, model: Type[ModelType], session_factory: async_sessionmaker):
        self.model = model
        self.session_factory = session_factory
        self._cache = {}  # Simple in-memory cache
    
    @asynccontextmanager
    async def get_session(self):
        """Get database session with proper cleanup"""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    # Core CRUD Operations
    
    async def create(
        self,
        obj_in: CreateSchemaType,
        created_by: Optional[UUID] = None,
        commit: bool = True
    ) -> ModelType:
        """Create a new record"""
        try:
            async with self.get_session() as session:
                # Convert Pydantic model to dict
                if hasattr(obj_in, 'model_dump'):
                    db_data = obj_in.model_dump(exclude_unset=True)
                elif hasattr(obj_in, 'dict'):
                    db_data = obj_in.dict(exclude_unset=True)
                else:
                    db_data = dict(obj_in)
                
                # Add audit information
                if created_by:
                    db_data['created_by'] = created_by
                    db_data['updated_by'] = created_by
                
                # Create model instance
                db_obj = self.model(**db_data)
                
                # Add to session
                session.add(db_obj)
                
                if commit:
                    await session.commit()
                    await session.refresh(db_obj)
                
                logger.info(f"Created {self.model.__name__} with id: {db_obj.id}")
                return db_obj
                
        except IntegrityError as e:
            logger.error(f"Integrity error creating {self.model.__name__}: {e}")
            raise DuplicateError(f"Record already exists or violates constraints")
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to create record: {str(e)}")
    
    async def get(self, id: UUID, include_deleted: bool = False) -> Optional[ModelType]:
        """Get record by ID"""
        try:
            async with self.get_session() as session:
                query = select(self.model).where(self.model.id == id)
                
                # Filter out soft deleted records unless explicitly requested
                if hasattr(self.model, 'is_deleted') and not include_deleted:
                    query = query.where(self.model.is_deleted == False)
                
                result = await session.execute(query)
                record = result.scalar_one_or_none()
                
                if record:
                    logger.debug(f"Retrieved {self.model.__name__} with id: {id}")
                else:
                    logger.debug(f"No {self.model.__name__} found with id: {id}")
                
                return record
                
        except Exception as e:
            logger.error(f"Error retrieving {self.model.__name__} {id}: {e}")
            raise DatabaseError(f"Failed to retrieve record: {str(e)}")
    
    async def get_by_field(
        self, 
        field_name: str, 
        field_value: Any,
        include_deleted: bool = False
    ) -> Optional[ModelType]:
        """Get record by specific field"""
        try:
            async with self.get_session() as session:
                query = select(self.model).where(
                    getattr(self.model, field_name) == field_value
                )
                
                if hasattr(self.model, 'is_deleted') and not include_deleted:
                    query = query.where(self.model.is_deleted == False)
                
                result = await session.execute(query)
                return result.scalar_one_or_none()
                
        except Exception as e:
            logger.error(f"Error retrieving {self.model.__name__} by {field_name}: {e}")
            raise DatabaseError(f"Failed to retrieve record: {str(e)}")
    
    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = 'asc',
        include_deleted: bool = False
    ) -> Tuple[List[ModelType], int]:
        """Get multiple records with pagination and filtering"""
        try:
            async with self.get_session() as session:
                # Base query
                query = select(self.model)
                count_query = select(func.count(self.model.id))
                
                # Apply soft delete filter
                if hasattr(self.model, 'is_deleted') and not include_deleted:
                    query = query.where(self.model.is_deleted == False)
                    count_query = count_query.where(self.model.is_deleted == False)
                
                # Apply filters
                if filters:
                    filter_conditions = self._build_filters(filters)
                    if filter_conditions:
                        query = query.where(and_(*filter_conditions))
                        count_query = count_query.where(and_(*filter_conditions))
                
                # Get total count
                count_result = await session.execute(count_query)
                total = count_result.scalar()
                
                # Apply sorting
                if sort_by and hasattr(self.model, sort_by):
                    sort_column = getattr(self.model, sort_by)
                    if sort_order.lower() == 'desc':
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))
                else:
                    # Default sorting by created_at desc
                    if hasattr(self.model, 'created_at'):
                        query = query.order_by(desc(self.model.created_at))
                
                # Apply pagination
                query = query.offset(skip).limit(limit)
                
                # Execute query
                result = await session.execute(query)
                records = result.scalars().all()
                
                logger.debug(f"Retrieved {len(records)} {self.model.__name__} records")
                return list(records), total
                
        except Exception as e:
            logger.error(f"Error retrieving {self.model.__name__} records: {e}")
            raise DatabaseError(f"Failed to retrieve records: {str(e)}")
    
    async def update(
        self,
        id: UUID,
        obj_in: UpdateSchemaType,
        updated_by: Optional[UUID] = None,
        commit: bool = True
    ) -> Optional[ModelType]:
        """Update record by ID"""
        try:
            async with self.get_session() as session:
                # Get existing record
                db_obj = await self.get(id)
                if not db_obj:
                    raise NotFoundError(f"{self.model.__name__} not found")
                
                # Prepare update data
                if hasattr(obj_in, 'model_dump'):
                    update_data = obj_in.model_dump(exclude_unset=True)
                elif hasattr(obj_in, 'dict'):
                    update_data = obj_in.dict(exclude_unset=True)
                else:
                    update_data = dict(obj_in)
                
                # Remove None values and handle special fields
                update_data = {k: v for k, v in update_data.items() if v is not None}
                
                # Add audit information
                if updated_by:
                    update_data['updated_by'] = updated_by
                
                # Always update timestamp
                update_data['updated_at'] = datetime.now(timezone.utc)
                
                # Increment version for optimistic locking
                if hasattr(self.model, 'version'):
                    update_data['version'] = (db_obj.version or 0) + 1
                
                # Update record
                query = (
                    update(self.model)
                    .where(self.model.id == id)
                    .values(**update_data)
                    .returning(self.model)
                )
                
                result = await session.execute(query)
                updated_obj = result.scalar_one_or_none()
                
                if commit:
                    await session.commit()
                
                logger.info(f"Updated {self.model.__name__} with id: {id}")
                return updated_obj
                
        except NotFoundError:
            raise
        except IntegrityError as e:
            logger.error(f"Integrity error updating {self.model.__name__}: {e}")
            raise DuplicateError(f"Update violates constraints")
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__} {id}: {e}")
            raise DatabaseError(f"Failed to update record: {str(e)}")
    
    async def delete(
        self, 
        id: UUID, 
        deleted_by: Optional[UUID] = None,
        soft_delete: bool = True
    ) -> bool:
        """Delete record (soft or hard delete)"""
        try:
            async with self.get_session() as session:
                # Check if record exists
                db_obj = await self.get(id)
                if not db_obj:
                    raise NotFoundError(f"{self.model.__name__} not found")
                
                if soft_delete and hasattr(self.model, 'is_deleted'):
                    # Soft delete
                    update_data = {
                        'is_deleted': True,
                        'deleted_at': datetime.now(timezone.utc),
                        'updated_at': datetime.now(timezone.utc)
                    }
                    
                    if deleted_by:
                        update_data['deleted_by'] = deleted_by
                        update_data['updated_by'] = deleted_by
                    
                    query = (
                        update(self.model)
                        .where(self.model.id == id)
                        .values(**update_data)
                    )
                    
                    await session.execute(query)
                    logger.info(f"Soft deleted {self.model.__name__} with id: {id}")
                    
                else:
                    # Hard delete
                    query = delete(self.model).where(self.model.id == id)
                    await session.execute(query)
                    logger.info(f"Hard deleted {self.model.__name__} with id: {id}")
                
                await session.commit()
                return True
                
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting {self.model.__name__} {id}: {e}")
            raise DatabaseError(f"Failed to delete record: {str(e)}")
    
    # Advanced operations
    
    async def bulk_create(
        self,
        objects: List[CreateSchemaType],
        created_by: Optional[UUID] = None,
        batch_size: int = 1000
    ) -> List[ModelType]:
        """Bulk create records for performance"""
        try:
            created_records = []
            
            async with self.get_session() as session:
                for i in range(0, len(objects), batch_size):
                    batch = objects[i:i + batch_size]
                    batch_data = []
                    
                    for obj in batch:
                        if hasattr(obj, 'model_dump'):
                            data = obj.model_dump(exclude_unset=True)
                        elif hasattr(obj, 'dict'):
                            data = obj.dict(exclude_unset=True)
                        else:
                            data = dict(obj)
                        
                        if created_by:
                            data['created_by'] = created_by
                            data['updated_by'] = created_by
                        
                        batch_data.append(data)
                    
                    # Use PostgreSQL RETURNING clause for better performance
                    if hasattr(session.bind.dialect, 'name') and session.bind.dialect.name == 'postgresql':
                        query = (
                            pg_insert(self.model)
                            .values(batch_data)
                            .returning(self.model)
                        )
                        result = await session.execute(query)
                        batch_records = result.scalars().all()
                        created_records.extend(batch_records)
                    else:
                        # Fallback for other databases
                        for data in batch_data:
                            db_obj = self.model(**data)
                            session.add(db_obj)
                            created_records.append(db_obj)
                
                await session.commit()
                
                logger.info(f"Bulk created {len(created_records)} {self.model.__name__} records")
                return created_records
                
        except Exception as e:
            logger.error(f"Error bulk creating {self.model.__name__} records: {e}")
            raise DatabaseError(f"Failed to bulk create records: {str(e)}")
    
    async def bulk_update(
        self,
        updates: List[Tuple[UUID, UpdateSchemaType]],
        updated_by: Optional[UUID] = None
    ) -> int:
        """Bulk update records"""
        try:
            updated_count = 0
            
            async with self.get_session() as session:
                for record_id, update_obj in updates:
                    if hasattr(update_obj, 'model_dump'):
                        update_data = update_obj.model_dump(exclude_unset=True)
                    elif hasattr(update_obj, 'dict'):
                        update_data = update_obj.dict(exclude_unset=True)
                    else:
                        update_data = dict(update_obj)
                    
                    # Remove None values
                    update_data = {k: v for k, v in update_data.items() if v is not None}
                    
                    if update_data:
                        if updated_by:
                            update_data['updated_by'] = updated_by
                        update_data['updated_at'] = datetime.now(timezone.utc)
                        
                        query = (
                            update(self.model)
                            .where(self.model.id == record_id)
                            .values(**update_data)
                        )
                        
                        result = await session.execute(query)
                        updated_count += result.rowcount
                
                await session.commit()
                
                logger.info(f"Bulk updated {updated_count} {self.model.__name__} records")
                return updated_count
                
        except Exception as e:
            logger.error(f"Error bulk updating {self.model.__name__} records: {e}")
            raise DatabaseError(f"Failed to bulk update records: {str(e)}")
    
    async def bulk_delete(
        self,
        ids: List[UUID],
        deleted_by: Optional[UUID] = None,
        soft_delete: bool = True
    ) -> int:
        """Bulk delete records"""
        try:
            async with self.get_session() as session:
                if soft_delete and hasattr(self.model, 'is_deleted'):
                    # Soft delete
                    update_data = {
                        'is_deleted': True,
                        'deleted_at': datetime.now(timezone.utc),
                        'updated_at': datetime.now(timezone.utc)
                    }
                    
                    if deleted_by:
                        update_data['deleted_by'] = deleted_by
                        update_data['updated_by'] = deleted_by
                    
                    query = (
                        update(self.model)
                        .where(self.model.id.in_(ids))
                        .values(**update_data)
                    )
                    
                else:
                    # Hard delete
                    query = delete(self.model).where(self.model.id.in_(ids))
                
                result = await session.execute(query)
                deleted_count = result.rowcount
                
                await session.commit()
                
                logger.info(f"Bulk deleted {deleted_count} {self.model.__name__} records")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error bulk deleting {self.model.__name__} records: {e}")
            raise DatabaseError(f"Failed to bulk delete records: {str(e)}")
    
    # Search and filtering
    
    async def search(
        self,
        query: str,
        fields: List[str],
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[ModelType], int]:
        """Full-text search across specified fields"""
        try:
            async with self.get_session() as session:
                # Build search conditions
                search_conditions = []
                search_terms = query.lower().split()
                
                for field in fields:
                    if hasattr(self.model, field):
                        column = getattr(self.model, field)
                        for term in search_terms:
                            search_conditions.append(
                                func.lower(column).contains(term)
                            )
                
                # Base query with search
                base_query = select(self.model)
                count_query = select(func.count(self.model.id))
                
                if search_conditions:
                    search_filter = or_(*search_conditions)
                    base_query = base_query.where(search_filter)
                    count_query = count_query.where(search_filter)
                
                # Apply additional filters
                if filters:
                    filter_conditions = self._build_filters(filters)
                    if filter_conditions:
                        base_query = base_query.where(and_(*filter_conditions))
                        count_query = count_query.where(and_(*filter_conditions))
                
                # Apply soft delete filter
                if hasattr(self.model, 'is_deleted'):
                    base_query = base_query.where(self.model.is_deleted == False)
                    count_query = count_query.where(self.model.is_deleted == False)
                
                # Get count
                count_result = await session.execute(count_query)
                total = count_result.scalar()
                
                # Apply pagination and execute
                base_query = base_query.offset(skip).limit(limit)
                result = await session.execute(base_query)
                records = result.scalars().all()
                
                logger.debug(f"Search found {total} {self.model.__name__} records")
                return list(records), total
                
        except Exception as e:
            logger.error(f"Error searching {self.model.__name__} records: {e}")
            raise DatabaseError(f"Failed to search records: {str(e)}")
    
    async def exists(self, id: UUID) -> bool:
        """Check if record exists"""
        try:
            async with self.get_session() as session:
                query = select(exists().where(self.model.id == id))
                
                if hasattr(self.model, 'is_deleted'):
                    query = select(exists().where(
                        and_(
                            self.model.id == id,
                            self.model.is_deleted == False
                        )
                    ))
                
                result = await session.execute(query)
                return result.scalar()
                
        except Exception as e:
            logger.error(f"Error checking existence of {self.model.__name__} {id}: {e}")
            raise DatabaseError(f"Failed to check record existence: {str(e)}")
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filters"""
        try:
            async with self.get_session() as session:
                query = select(func.count(self.model.id))
                
                # Apply soft delete filter
                if hasattr(self.model, 'is_deleted'):
                    query = query.where(self.model.is_deleted == False)
                
                # Apply filters
                if filters:
                    filter_conditions = self._build_filters(filters)
                    if filter_conditions:
                        query = query.where(and_(*filter_conditions))
                
                result = await session.execute(query)
                return result.scalar()
                
        except Exception as e:
            logger.error(f"Error counting {self.model.__name__} records: {e}")
            raise DatabaseError(f"Failed to count records: {str(e)}")
    
    # Helper methods
    
    def _build_filters(self, filters: Dict[str, Any]) -> List:
        """Build SQLAlchemy filter conditions from dictionary"""
        conditions = []
        
        for field, value in filters.items():
            if not hasattr(self.model, field) or value is None:
                continue
            
            column = getattr(self.model, field)
            
            # Handle different filter types
            if isinstance(value, dict):
                # Range or comparison filters
                if 'gte' in value:
                    conditions.append(column >= value['gte'])
                if 'gt' in value:
                    conditions.append(column > value['gt'])
                if 'lte' in value:
                    conditions.append(column <= value['lte'])
                if 'lt' in value:
                    conditions.append(column < value['lt'])
                if 'ne' in value:
                    conditions.append(column != value['ne'])
                if 'like' in value:
                    conditions.append(column.like(f"%{value['like']}%"))
                if 'ilike' in value:
                    conditions.append(column.ilike(f"%{value['ilike']}%"))
                if 'in' in value:
                    conditions.append(column.in_(value['in']))
                if 'not_in' in value:
                    conditions.append(~column.in_(value['not_in']))
                    
            elif isinstance(value, list):
                # IN filter
                conditions.append(column.in_(value))
                
            else:
                # Exact match
                conditions.append(column == value)
        
        return conditions


class {{repository_name}}Repository(BaseRepository):
    """{{repository_description}}
    
    Specialized repository for {{model_name}} with business-specific operations
    """
    
    def __init__(self, session_factory: async_sessionmaker):
        from templates.database.{{model_file}} import {{model_name}}Model
        from templates.database.{{model_file}} import {{model_name}}Create, {{model_name}}Update
        
        super().__init__({{model_name}}Model, session_factory)
        self.create_schema = {{model_name}}Create
        self.update_schema = {{model_name}}Update
    
    # Business-specific methods
    
    async def get_by_name(self, name: str, tenant_id: Optional[UUID] = None) -> Optional[ModelType]:
        """Get record by name (with optional tenant filtering)"""
        filters = {'name': name}
        if tenant_id:
            filters['tenant_id'] = tenant_id
        
        try:
            async with self.get_session() as session:
                query = select(self.model)
                filter_conditions = self._build_filters(filters)
                
                if filter_conditions:
                    query = query.where(and_(*filter_conditions))
                
                if hasattr(self.model, 'is_deleted'):
                    query = query.where(self.model.is_deleted == False)
                
                result = await session.execute(query)
                return result.scalar_one_or_none()
                
        except Exception as e:
            logger.error(f"Error retrieving {self.model.__name__} by name: {e}")
            raise DatabaseError(f"Failed to retrieve record by name: {str(e)}")
    
    async def get_by_owner(
        self,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[List[str]] = None
    ) -> Tuple[List[ModelType], int]:
        """Get records by owner with optional status filtering"""
        filters = {'owner_id': owner_id}
        
        if status_filter:
            filters['status'] = status_filter
        
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            sort_by='created_at',
            sort_order='desc'
        )
    
    async def get_featured(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None
    ) -> Tuple[List[ModelType], int]:
        """Get featured records"""
        filters = {'is_featured': True, 'is_public': True}
        
        if category:
            filters['category'] = category
        
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            sort_by='priority',
            sort_order='desc'
        )
    
    async def get_by_tags(
        self,
        tags: List[str],
        match_all: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ModelType], int]:
        """Get records by tags"""
        try:
            async with self.get_session() as session:
                query = select(self.model)
                
                if hasattr(self.model, 'tags'):
                    if match_all:
                        # All tags must be present
                        for tag in tags:
                            query = query.where(
                                func.jsonb_extract_path_text(self.model.tags, text("*")).contains(tag)
                            )
                    else:
                        # Any tag matches
                        tag_conditions = []
                        for tag in tags:
                            tag_conditions.append(
                                func.jsonb_extract_path_text(self.model.tags, text("*")).contains(tag)
                            )
                        query = query.where(or_(*tag_conditions))
                
                # Apply soft delete filter
                if hasattr(self.model, 'is_deleted'):
                    query = query.where(self.model.is_deleted == False)
                
                # Count query
                count_query = select(func.count()).select_from(query.subquery())
                count_result = await session.execute(count_query)
                total = count_result.scalar()
                
                # Apply pagination
                query = query.offset(skip).limit(limit)
                result = await session.execute(query)
                records = result.scalars().all()
                
                return list(records), total
                
        except Exception as e:
            logger.error(f"Error retrieving {self.model.__name__} by tags: {e}")
            raise DatabaseError(f"Failed to retrieve records by tags: {str(e)}")
    
    async def update_status(
        self,
        id: UUID,
        status: str,
        updated_by: Optional[UUID] = None
    ) -> Optional[ModelType]:
        """Update record status"""
        from templates.database.{{model_file}} import {{model_name}}Update
        
        update_data = {{model_name}}Update(status=status)
        return await self.update(id, update_data, updated_by)
    
    async def toggle_featured(
        self,
        id: UUID,
        updated_by: Optional[UUID] = None
    ) -> Optional[ModelType]:
        """Toggle featured status"""
        record = await self.get(id)
        if not record:
            raise NotFoundError(f"{self.model.__name__} not found")
        
        from templates.database.{{model_file}} import {{model_name}}Update
        
        update_data = {{model_name}}Update(is_featured=not record.is_featured)
        return await self.update(id, update_data, updated_by)
    
    async def get_analytics(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        tenant_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Get analytics data for records"""
        try:
            async with self.get_session() as session:
                base_query = select(self.model)
                
                # Apply date filters
                if date_from:
                    base_query = base_query.where(self.model.created_at >= date_from)
                if date_to:
                    base_query = base_query.where(self.model.created_at <= date_to)
                
                # Apply tenant filter
                if tenant_id and hasattr(self.model, 'tenant_id'):
                    base_query = base_query.where(self.model.tenant_id == tenant_id)
                
                # Soft delete filter
                if hasattr(self.model, 'is_deleted'):
                    base_query = base_query.where(self.model.is_deleted == False)
                
                # Total count
                total_result = await session.execute(
                    select(func.count()).select_from(base_query.subquery())
                )
                total_count = total_result.scalar()
                
                # Status distribution
                status_query = (
                    select(
                        self.model.status,
                        func.count(self.model.id).label('count')
                    )
                    .select_from(base_query.subquery())
                    .group_by(self.model.status)
                )
                status_result = await session.execute(status_query)
                status_distribution = {row.status: row.count for row in status_result}
                
                # Category distribution
                category_distribution = {}
                if hasattr(self.model, 'category'):
                    category_query = (
                        select(
                            self.model.category,
                            func.count(self.model.id).label('count')
                        )
                        .select_from(base_query.subquery())
                        .where(self.model.category.isnot(None))
                        .group_by(self.model.category)
                    )
                    category_result = await session.execute(category_query)
                    category_distribution = {row.category: row.count for row in category_result}
                
                # Featured count
                featured_count = 0
                if hasattr(self.model, 'is_featured'):
                    featured_result = await session.execute(
                        select(func.count())
                        .select_from(base_query.subquery())
                        .where(self.model.is_featured == True)
                    )
                    featured_count = featured_result.scalar()
                
                return {
                    'total_count': total_count,
                    'status_distribution': status_distribution,
                    'category_distribution': category_distribution,
                    'featured_count': featured_count,
                    'date_range': {
                        'from': date_from.isoformat() if date_from else None,
                        'to': date_to.isoformat() if date_to else None
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting analytics for {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to get analytics: {str(e)}")


# Factory function for creating repository instances
def create_{{repository_name.lower()}}_repository(session_factory: async_sessionmaker = None) -> {{repository_name}}Repository:
    """Factory function to create repository instance"""
    if session_factory is None:
        session_factory = get_session()
    
    return {{repository_name}}Repository(session_factory)


# Export for easy import
__all__ = [
    'BaseRepository',
    '{{repository_name}}Repository',
    'create_{{repository_name.lower()}}_repository'
]