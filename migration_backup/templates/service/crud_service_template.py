"""{{service_name}} CRUD Service Template for Ainflue Platform
{{service_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
from typing import Dict, Any, Optional, List, Union, Generic, TypeVar
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload

from core.database import get_async_session
from core.config import get_settings
from utils.exceptions import ServiceException, ValidationError, NotFoundError
from utils.pagination import PaginationParams, PaginatedResponse
from utils.filtering import FilterParams, SortParams
from monitoring.service_metrics import ServiceMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()

# Generic types
ModelType = TypeVar('ModelType')
CreateSchemaType = TypeVar('CreateSchemaType')
UpdateSchemaType = TypeVar('UpdateSchemaType')


class CRUDOperation(Enum):
    """CRUD operation types"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"
    BULK_CREATE = "bulk_create"
    BULK_UPDATE = "bulk_update"
    BULK_DELETE = "bulk_delete"


class ServiceResult(BaseModel):
    """Service operation result"""
    success: bool = Field(..., description="Whether the operation succeeded")
    data: Optional[Any] = Field(default=None, description="Result data")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    operation: CRUDOperation = Field(..., description="Type of operation performed")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    affected_rows: Optional[int] = Field(default=None, description="Number of affected rows")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True


class CRUDServiceConfig(BaseModel):
    """CRUD service configuration"""
    enable_soft_delete: bool = Field(default=True, description="Enable soft delete")
    enable_audit: bool = Field(default=True, description="Enable audit logging")
    enable_caching: bool = Field(default=True, description="Enable caching")
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    max_batch_size: int = Field(default=1000, description="Maximum batch size for bulk operations")
    enable_validation: bool = Field(default=True, description="Enable input validation")
    enable_permissions: bool = Field(default=True, description="Enable permission checks")
    default_page_size: int = Field(default=20, description="Default page size for listing")
    max_page_size: int = Field(default=100, description="Maximum page size for listing")


class BaseCRUDService(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """Base CRUD service with comprehensive functionality"""
    
    def __init__(
        self,
        model: ModelType,
        config: Optional[CRUDServiceConfig] = None,
        session: Optional[AsyncSession] = None
    ):
        self.model = model
        self.config = config or CRUDServiceConfig()
        self.session = session
        self.metrics_collector = ServiceMetricsCollector()
        self._cache = {}
        
    async def _get_session(self) -> AsyncSession:
        """Get database session"""
        if self.session:
            return self.session
        return await get_async_session()
    
    async def create(
        self,
        obj_in: CreateSchemaType,
        user_id: Optional[str] = None,
        **kwargs
    ) -> ServiceResult:
        """Create a new record"""
        start_time = datetime.utcnow()
        
        try:
            session = await self._get_session()
            
            # Validate input
            if self.config.enable_validation:
                await self._validate_create_input(obj_in, user_id)
            
            # Check permissions
            if self.config.enable_permissions:
                await self._check_create_permission(user_id, obj_in)
            
            # Create object
            db_obj = self.model(**obj_in.dict())
            
            # Add audit fields
            if self.config.enable_audit and hasattr(db_obj, 'created_by'):
                db_obj.created_by = user_id
                db_obj.created_at = datetime.utcnow()
            
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            
            # Clear cache
            if self.config.enable_caching:
                await self._clear_cache()
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Record metrics
            await self.metrics_collector.record_operation_metrics(
                service_name=self.__class__.__name__,
                operation=CRUDOperation.CREATE.value,
                execution_time=execution_time,
                success=True
            )
            
            return ServiceResult(
                success=True,
                data=db_obj,
                operation=CRUDOperation.CREATE,
                execution_time=execution_time,
                affected_rows=1
            )
            
        except Exception as e:
            logger.error(f"Create operation failed: {str(e)}")
            await self.metrics_collector.record_operation_metrics(
                service_name=self.__class__.__name__,
                operation=CRUDOperation.CREATE.value,
                execution_time=0,
                success=False
            )
            return ServiceResult(
                success=False,
                error_message=str(e),
                operation=CRUDOperation.CREATE
            )
    
    async def get(
        self,
        id: Union[int, str],
        user_id: Optional[str] = None,
        includes: Optional[List[str]] = None
    ) -> ServiceResult:
        """Get a record by ID"""
        start_time = datetime.utcnow()
        
        try:
            # Check cache first
            cache_key = f"{self.model.__name__}:{id}"
            if self.config.enable_caching and cache_key in self._cache:
                cached_result = self._cache[cache_key]
                if (datetime.utcnow() - cached_result['timestamp']).seconds < self.config.cache_ttl:
                    return ServiceResult(
                        success=True,
                        data=cached_result['data'],
                        operation=CRUDOperation.READ,
                        execution_time=0,
                        metadata={"from_cache": True}
                    )
            
            session = await self._get_session()
            
            # Build query
            query = select(self.model).where(self.model.id == id)
            
            # Add includes/joins
            if includes:
                query = await self._add_includes(query, includes)
            
            # Add soft delete filter
            if self.config.enable_soft_delete and hasattr(self.model, 'deleted_at'):
                query = query.where(self.model.deleted_at.is_(None))
            
            result = await session.execute(query)
            db_obj = result.scalar_one_or_none()
            
            if not db_obj:
                return ServiceResult(
                    success=False,
                    error_message=f"Record not found with id: {id}",
                    operation=CRUDOperation.READ
                )
            
            # Check permissions
            if self.config.enable_permissions:
                await self._check_read_permission(user_id, db_obj)
            
            # Cache result
            if self.config.enable_caching:
                self._cache[cache_key] = {
                    'data': db_obj,
                    'timestamp': datetime.utcnow()
                }
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Record metrics
            await self.metrics_collector.record_operation_metrics(
                service_name=self.__class__.__name__,
                operation=CRUDOperation.READ.value,
                execution_time=execution_time,
                success=True
            )
            
            return ServiceResult(
                success=True,
                data=db_obj,
                operation=CRUDOperation.READ,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Get operation failed: {str(e)}")
            return ServiceResult(
                success=False,
                error_message=str(e),
                operation=CRUDOperation.READ
            )
    
    async def list(
        self,
        pagination: Optional[PaginationParams] = None,
        filters: Optional[FilterParams] = None,
        sort: Optional[SortParams] = None,
        user_id: Optional[str] = None,
        includes: Optional[List[str]] = None
    ) -> ServiceResult:
        """List records with pagination, filtering, and sorting"""
        start_time = datetime.utcnow()
        
        try:
            session = await self._get_session()
            
            # Build base query
            query = select(self.model)
            count_query = select(func.count(self.model.id))
            
            # Add soft delete filter
            if self.config.enable_soft_delete and hasattr(self.model, 'deleted_at'):
                query = query.where(self.model.deleted_at.is_(None))
                count_query = count_query.where(self.model.deleted_at.is_(None))
            
            # Add filters
            if filters:
                filter_conditions = await self._build_filters(filters)
                if filter_conditions:
                    query = query.where(and_(*filter_conditions))
                    count_query = count_query.where(and_(*filter_conditions))
            
            # Add user-specific filters
            user_conditions = await self._add_user_filters(user_id)
            if user_conditions:
                query = query.where(and_(*user_conditions))
                count_query = count_query.where(and_(*user_conditions))
            
            # Get total count
            total_result = await session.execute(count_query)
            total = total_result.scalar()
            
            # Add sorting
            if sort:
                query = await self._add_sorting(query, sort)
            else:
                # Default sorting
                if hasattr(self.model, 'created_at'):
                    query = query.order_by(self.model.created_at.desc())
            
            # Add pagination
            if pagination:
                page_size = min(pagination.page_size or self.config.default_page_size, self.config.max_page_size)
                offset = (pagination.page - 1) * page_size
                query = query.offset(offset).limit(page_size)
            else:
                page_size = self.config.default_page_size
                query = query.limit(page_size)
            
            # Add includes/joins
            if includes:
                query = await self._add_includes(query, includes)
            
            # Execute query
            result = await session.execute(query)
            items = result.scalars().all()
            
            # Build pagination response
            if pagination:
                page_info = {
                    "page": pagination.page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (total + page_size - 1) // page_size,
                    "has_next": pagination.page * page_size < total,
                    "has_previous": pagination.page > 1
                }
            else:
                page_info = {
                    "total": total,
                    "returned": len(items)
                }
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Record metrics
            await self.metrics_collector.record_operation_metrics(
                service_name=self.__class__.__name__,
                operation=CRUDOperation.LIST.value,
                execution_time=execution_time,
                success=True
            )
            
            return ServiceResult(
                success=True,
                data={
                    "items": items,
                    "pagination": page_info
                },
                operation=CRUDOperation.LIST,
                execution_time=execution_time,
                metadata={"total_count": total}
            )
            
        except Exception as e:
            logger.error(f"List operation failed: {str(e)}")
            return ServiceResult(
                success=False,
                error_message=str(e),
                operation=CRUDOperation.LIST
            )
    
    async def update(
        self,
        id: Union[int, str],
        obj_in: UpdateSchemaType,
        user_id: Optional[str] = None
    ) -> ServiceResult:
        """Update a record"""
        start_time = datetime.utcnow()
        
        try:
            session = await self._get_session()
            
            # Get existing object
            get_result = await self.get(id, user_id)
            if not get_result.success:
                return get_result
            
            db_obj = get_result.data
            
            # Validate input
            if self.config.enable_validation:
                await self._validate_update_input(obj_in, db_obj, user_id)
            
            # Check permissions
            if self.config.enable_permissions:
                await self._check_update_permission(user_id, db_obj)
            
            # Update object
            update_data = obj_in.dict(exclude_unset=True)
            
            # Add audit fields
            if self.config.enable_audit and hasattr(db_obj, 'updated_by'):
                update_data['updated_by'] = user_id
                update_data['updated_at'] = datetime.utcnow()
            
            # Perform update
            query = update(self.model).where(self.model.id == id).values(**update_data)
            await session.execute(query)
            await session.commit()
            
            # Get updated object
            await session.refresh(db_obj)
            
            # Clear cache
            if self.config.enable_caching:
                await self._clear_cache()
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Record metrics
            await self.metrics_collector.record_operation_metrics(
                service_name=self.__class__.__name__,
                operation=CRUDOperation.UPDATE.value,
                execution_time=execution_time,
                success=True
            )
            
            return ServiceResult(
                success=True,
                data=db_obj,
                operation=CRUDOperation.UPDATE,
                execution_time=execution_time,
                affected_rows=1
            )
            
        except Exception as e:
            logger.error(f"Update operation failed: {str(e)}")
            return ServiceResult(
                success=False,
                error_message=str(e),
                operation=CRUDOperation.UPDATE
            )
    
    async def delete(
        self,
        id: Union[int, str],
        user_id: Optional[str] = None,
        hard_delete: bool = False
    ) -> ServiceResult:
        """Delete a record (soft or hard delete)"""
        start_time = datetime.utcnow()
        
        try:
            session = await self._get_session()
            
            # Get existing object
            get_result = await self.get(id, user_id)
            if not get_result.success:
                return get_result
            
            db_obj = get_result.data
            
            # Check permissions
            if self.config.enable_permissions:
                await self._check_delete_permission(user_id, db_obj)
            
            if hard_delete or not self.config.enable_soft_delete:
                # Hard delete
                query = delete(self.model).where(self.model.id == id)
                await session.execute(query)
            else:
                # Soft delete
                if hasattr(self.model, 'deleted_at'):
                    update_data = {
                        'deleted_at': datetime.utcnow(),
                        'deleted_by': user_id
                    }
                    query = update(self.model).where(self.model.id == id).values(**update_data)
                    await session.execute(query)
                else:
                    # Fallback to hard delete if no soft delete support
                    query = delete(self.model).where(self.model.id == id)
                    await session.execute(query)
            
            await session.commit()
            
            # Clear cache
            if self.config.enable_caching:
                await self._clear_cache()
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Record metrics
            await self.metrics_collector.record_operation_metrics(
                service_name=self.__class__.__name__,
                operation=CRUDOperation.DELETE.value,
                execution_time=execution_time,
                success=True
            )
            
            return ServiceResult(
                success=True,
                data={"deleted_id": id, "hard_delete": hard_delete},
                operation=CRUDOperation.DELETE,
                execution_time=execution_time,
                affected_rows=1
            )
            
        except Exception as e:
            logger.error(f"Delete operation failed: {str(e)}")
            return ServiceResult(
                success=False,
                error_message=str(e),
                operation=CRUDOperation.DELETE
            )
    
    async def bulk_create(
        self,
        objects: List[CreateSchemaType],
        user_id: Optional[str] = None
    ) -> ServiceResult:
        """Bulk create records"""
        start_time = datetime.utcnow()
        
        try:
            if len(objects) > self.config.max_batch_size:
                return ServiceResult(
                    success=False,
                    error_message=f"Batch size {len(objects)} exceeds maximum {self.config.max_batch_size}",
                    operation=CRUDOperation.BULK_CREATE
                )
            
            session = await self._get_session()
            
            # Validate all inputs
            if self.config.enable_validation:
                for obj_in in objects:
                    await self._validate_create_input(obj_in, user_id)
            
            # Create objects
            db_objects = []
            for obj_in in objects:
                db_obj = self.model(**obj_in.dict())
                
                # Add audit fields
                if self.config.enable_audit and hasattr(db_obj, 'created_by'):
                    db_obj.created_by = user_id
                    db_obj.created_at = datetime.utcnow()
                
                db_objects.append(db_obj)
            
            session.add_all(db_objects)
            await session.commit()
            
            # Clear cache
            if self.config.enable_caching:
                await self._clear_cache()
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Record metrics
            await self.metrics_collector.record_operation_metrics(
                service_name=self.__class__.__name__,
                operation=CRUDOperation.BULK_CREATE.value,
                execution_time=execution_time,
                success=True
            )
            
            return ServiceResult(
                success=True,
                data=db_objects,
                operation=CRUDOperation.BULK_CREATE,
                execution_time=execution_time,
                affected_rows=len(db_objects)
            )
            
        except Exception as e:
            logger.error(f"Bulk create operation failed: {str(e)}")
            return ServiceResult(
                success=False,
                error_message=str(e),
                operation=CRUDOperation.BULK_CREATE
            )
    
    # Abstract methods to be implemented by concrete services
    @abstractmethod
    async def _validate_create_input(self, obj_in: CreateSchemaType, user_id: Optional[str] = None):
        """Validate create input"""
        pass
    
    @abstractmethod
    async def _validate_update_input(self, obj_in: UpdateSchemaType, db_obj: ModelType, user_id: Optional[str] = None):
        """Validate update input"""
        pass
    
    @abstractmethod
    async def _check_create_permission(self, user_id: Optional[str], obj_in: CreateSchemaType):
        """Check create permission"""
        pass
    
    @abstractmethod
    async def _check_read_permission(self, user_id: Optional[str], db_obj: ModelType):
        """Check read permission"""
        pass
    
    @abstractmethod
    async def _check_update_permission(self, user_id: Optional[str], db_obj: ModelType):
        """Check update permission"""
        pass
    
    @abstractmethod
    async def _check_delete_permission(self, user_id: Optional[str], db_obj: ModelType):
        """Check delete permission"""
        pass
    
    async def _add_includes(self, query, includes: List[str]):
        """Add eager loading for relationships"""
        # Default implementation - override in concrete services
        return query
    
    async def _build_filters(self, filters: FilterParams) -> List:
        """Build filter conditions"""
        conditions = []
        
        for field, value in filters.dict(exclude_unset=True).items():
            if hasattr(self.model, field):
                column = getattr(self.model, field)
                
                if isinstance(value, dict):
                    # Complex filter operations
                    for op, op_value in value.items():
                        if op == 'eq':
                            conditions.append(column == op_value)
                        elif op == 'ne':
                            conditions.append(column != op_value)
                        elif op == 'gt':
                            conditions.append(column > op_value)
                        elif op == 'gte':
                            conditions.append(column >= op_value)
                        elif op == 'lt':
                            conditions.append(column < op_value)
                        elif op == 'lte':
                            conditions.append(column <= op_value)
                        elif op == 'in':
                            conditions.append(column.in_(op_value))
                        elif op == 'not_in':
                            conditions.append(~column.in_(op_value))
                        elif op == 'like':
                            conditions.append(column.like(f"%{op_value}%"))
                        elif op == 'ilike':
                            conditions.append(column.ilike(f"%{op_value}%"))
                else:
                    # Simple equality filter
                    conditions.append(column == value)
        
        return conditions
    
    async def _add_sorting(self, query, sort: SortParams):
        """Add sorting to query"""
        if sort.field and hasattr(self.model, sort.field):
            column = getattr(self.model, sort.field)
            if sort.direction == 'desc':
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        
        return query
    
    async def _add_user_filters(self, user_id: Optional[str]) -> List:
        """Add user-specific filters"""
        # Override in concrete services for user-specific filtering
        return []
    
    async def _clear_cache(self):
        """Clear service cache"""
        self._cache.clear()


class {{service_name}}CRUDService(BaseCRUDService):
    """{{service_description}}
    
    Concrete implementation of CRUD service for {{service_name}} with:
    - Full CRUD operations (Create, Read, Update, Delete)
    - Bulk operations support
    - Advanced filtering and sorting
    - Pagination with configurable page sizes
    - Soft delete functionality
    - Audit logging and tracking
    - Permission-based access control
    - Caching for improved performance
    - Comprehensive metrics collection
    - Input validation and error handling
    """
    
    async def _validate_create_input(self, obj_in: CreateSchemaType, user_id: Optional[str] = None):
        """Validate create input for {{service_name}}"""
        # Add specific validation logic here
        if hasattr(obj_in, 'name') and not obj_in.name:
            raise ValidationError("Name is required")
        
        # Add more validation rules as needed
        pass
    
    async def _validate_update_input(self, obj_in: UpdateSchemaType, db_obj: ModelType, user_id: Optional[str] = None):
        """Validate update input for {{service_name}}"""
        # Add specific validation logic here
        if hasattr(obj_in, 'name') and obj_in.name and not obj_in.name.strip():
            raise ValidationError("Name cannot be empty")
        
        # Add more validation rules as needed
        pass
    
    async def _check_create_permission(self, user_id: Optional[str], obj_in: CreateSchemaType):
        """Check create permission for {{service_name}}"""
        # Add permission checking logic here
        if not user_id:
            raise PermissionError("Authentication required")
        
        # Add more permission checks as needed
        pass
    
    async def _check_read_permission(self, user_id: Optional[str], db_obj: ModelType):
        """Check read permission for {{service_name}}"""
        # Add permission checking logic here
        if hasattr(db_obj, 'is_public') and not db_obj.is_public and not user_id:
            raise PermissionError("Authentication required for private records")
        
        # Add more permission checks as needed
        pass
    
    async def _check_update_permission(self, user_id: Optional[str], db_obj: ModelType):
        """Check update permission for {{service_name}}"""
        # Add permission checking logic here
        if not user_id:
            raise PermissionError("Authentication required")
        
        if hasattr(db_obj, 'created_by') and db_obj.created_by != user_id:
            # Check if user has admin permissions
            # This would integrate with your permission system
            pass
        
        # Add more permission checks as needed
        pass
    
    async def _check_delete_permission(self, user_id: Optional[str], db_obj: ModelType):
        """Check delete permission for {{service_name}}"""
        # Add permission checking logic here
        if not user_id:
            raise PermissionError("Authentication required")
        
        if hasattr(db_obj, 'created_by') and db_obj.created_by != user_id:
            # Check if user has admin permissions
            # This would integrate with your permission system
            pass
        
        # Add more permission checks as needed
        pass
    
    async def _add_includes(self, query, includes: List[str]):
        """Add eager loading for {{service_name}} relationships"""
        # Add specific relationship loading here
        for include in includes:
            if include == 'creator' and hasattr(self.model, 'creator'):
                query = query.options(selectinload(self.model.creator))
            elif include == 'tags' and hasattr(self.model, 'tags'):
                query = query.options(selectinload(self.model.tags))
            # Add more relationships as needed
        
        return query
    
    async def _add_user_filters(self, user_id: Optional[str]) -> List:
        """Add user-specific filters for {{service_name}}"""
        conditions = []
        
        if user_id and hasattr(self.model, 'created_by'):
            # User can see their own records
            conditions.append(
                or_(
                    self.model.created_by == user_id,
                    self.model.is_public == True  # Public records
                )
            )
        
        return conditions
    
    # Additional business-specific methods can be added here
    async def get_by_name(self, name: str, user_id: Optional[str] = None) -> ServiceResult:
        """Get {{service_name}} by name"""
        start_time = datetime.utcnow()
        
        try:
            session = await self._get_session()
            
            query = select(self.model).where(self.model.name == name)
            
            if self.config.enable_soft_delete and hasattr(self.model, 'deleted_at'):
                query = query.where(self.model.deleted_at.is_(None))
            
            result = await session.execute(query)
            db_obj = result.scalar_one_or_none()
            
            if not db_obj:
                return ServiceResult(
                    success=False,
                    error_message=f"{{service_name}} not found with name: {name}",
                    operation=CRUDOperation.READ
                )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ServiceResult(
                success=True,
                data=db_obj,
                operation=CRUDOperation.READ,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Get by name operation failed: {str(e)}")
            return ServiceResult(
                success=False,
                error_message=str(e),
                operation=CRUDOperation.READ
            )
    
    async def search(
        self,
        query: str,
        user_id: Optional[str] = None,
        pagination: Optional[PaginationParams] = None
    ) -> ServiceResult:
        """Search {{service_name}} by text"""
        start_time = datetime.utcnow()
        
        try:
            session = await self._get_session()
            
            # Build search query
            search_query = select(self.model)
            
            if hasattr(self.model, 'name'):
                search_query = search_query.where(self.model.name.ilike(f"%{query}%"))
            
            if hasattr(self.model, 'description'):
                search_query = search_query.where(
                    or_(
                        self.model.name.ilike(f"%{query}%"),
                        self.model.description.ilike(f"%{query}%")
                    )
                )
            
            # Add user filters
            user_conditions = await self._add_user_filters(user_id)
            if user_conditions:
                search_query = search_query.where(and_(*user_conditions))
            
            # Add soft delete filter
            if self.config.enable_soft_delete and hasattr(self.model, 'deleted_at'):
                search_query = search_query.where(self.model.deleted_at.is_(None))
            
            # Add pagination
            if pagination:
                page_size = min(pagination.page_size or self.config.default_page_size, self.config.max_page_size)
                offset = (pagination.page - 1) * page_size
                search_query = search_query.offset(offset).limit(page_size)
            
            result = await session.execute(search_query)
            items = result.scalars().all()
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ServiceResult(
                success=True,
                data={
                    "items": items,
                    "query": query,
                    "total_results": len(items)
                },
                operation=CRUDOperation.LIST,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Search operation failed: {str(e)}")
            return ServiceResult(
                success=False,
                error_message=str(e),
                operation=CRUDOperation.LIST
            )