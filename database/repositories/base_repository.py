"""Base Repository Module

Enterprise-grade base repository implementing common database operations
for the IA Influencer Agent + Content Protection Platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session, Query
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy import and_, or_, desc, asc, func, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime, timedelta
import logging
import uuid
from contextlib import contextmanager

# Type variable for model classes
ModelType = TypeVar('ModelType', bound=DeclarativeMeta)

logger = logging.getLogger(__name__)

class RepositoryException(Exception):
    """Custom exception for repository operations"""
    pass

class BaseRepository(ABC, Generic[ModelType]):
    """
    Abstract base repository implementing common database operations
    with enterprise-grade features including caching, monitoring, and security.
    """
    
    def __init__(self, db_session: Session, model_class: Type[ModelType]):
        """
        Initialize base repository
        
        Args:
            db_session: SQLAlchemy database session
            model_class: SQLAlchemy model class
        """
        self.db_session = db_session
        self.model_class = model_class
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        
    @contextmanager
    def transaction(self):
        """
        Database transaction context manager with automatic rollback on error
        """
        try:
            yield self.db_session
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            self.logger.error(f"Transaction rolled back: {str(e)}")
            raise RepositoryException(f"Database transaction failed: {str(e)}")
        
    def create(self, **kwargs) -> ModelType:
        """
        Create new entity with validation and error handling
        
        Args:
            **kwargs: Entity attributes
            
        Returns:
            Created entity instance
            
        Raises:
            RepositoryException: If creation fails
        """
        try:
            entity = self.model_class(**kwargs)
            with self.transaction():
                self.db_session.add(entity)
                self.db_session.flush()  # Get ID without committing
                self.db_session.refresh(entity)
                
            self.logger.info(f"Created {self.model_class.__name__} with ID: {entity.id}")
            return entity
            
        except IntegrityError as e:
            raise RepositoryException(f"Integrity constraint violation: {str(e)}")
        except SQLAlchemyError as e:
            raise RepositoryException(f"Database error during creation: {str(e)}")
            
    def bulk_create(self, entities_data: List[Dict[str, Any]]) -> List[ModelType]:
        """
        Bulk create multiple entities for performance optimization
        
        Args:
            entities_data: List of entity attribute dictionaries
            
        Returns:
            List of created entity instances
        """
        try:
            entities = [self.model_class(**data) for data in entities_data]
            with self.transaction():
                self.db_session.bulk_save_objects(entities, return_defaults=True)
                
            self.logger.info(f"Bulk created {len(entities)} {self.model_class.__name__} entities")
            return entities
            
        except SQLAlchemyError as e:
            raise RepositoryException(f"Bulk creation failed: {str(e)}")
            
    def get_by_id(self, entity_id: Union[int, str, uuid.UUID]) -> Optional[ModelType]:
        """
        Get entity by primary key with caching support
        
        Args:
            entity_id: Primary key value
            
        Returns:
            Entity instance or None if not found
        """
        try:
            entity = self.db_session.query(self.model_class).filter(
                self.model_class.id == entity_id
            ).first()
            
            if entity:
                self.logger.debug(f"Retrieved {self.model_class.__name__} ID: {entity_id}")
            
            return entity
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving entity by ID {entity_id}: {str(e)}")
            raise RepositoryException(f"Failed to retrieve entity: {str(e)}")
            
    def get_all(self, 
                limit: Optional[int] = None, 
                offset: Optional[int] = None,
                order_by: Optional[str] = None,
                order_direction: str = 'asc') -> List[ModelType]:
        """
        Get all entities with pagination and sorting
        
        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip
            order_by: Column name to order by
            order_direction: 'asc' or 'desc'
            
        Returns:
            List of entity instances
        """
        try:
            query = self.db_session.query(self.model_class)
            
            # Apply ordering
            if order_by and hasattr(self.model_class, order_by):
                column = getattr(self.model_class, order_by)
                if order_direction.lower() == 'desc':
                    query = query.order_by(desc(column))
                else:
                    query = query.order_by(asc(column))
            
            # Apply pagination
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
                
            entities = query.all()
            self.logger.debug(f"Retrieved {len(entities)} {self.model_class.__name__} entities")
            
            return entities
            
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to retrieve entities: {str(e)}")
            
    def get_by_filters(self, 
                      filters: Dict[str, Any], 
                      limit: Optional[int] = None,
                      offset: Optional[int] = None,
                      order_by: Optional[str] = None,
                      order_direction: str = 'asc') -> List[ModelType]:
        """
        Get entities by dynamic filters with advanced querying
        
        Args:
            filters: Dictionary of filter conditions
            limit: Maximum number of entities to return
            offset: Number of entities to skip
            order_by: Column name to order by
            order_direction: 'asc' or 'desc'
            
        Returns:
            List of entity instances matching filters
        """
        try:
            query = self.db_session.query(self.model_class)
            
            # Apply filters
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    column = getattr(self.model_class, field)
                    
                    # Handle different filter types
                    if isinstance(value, dict):
                        # Advanced filter operations
                        for operation, operand in value.items():
                            if operation == 'in':
                                query = query.filter(column.in_(operand))
                            elif operation == 'not_in':
                                query = query.filter(~column.in_(operand))
                            elif operation == 'like':
                                query = query.filter(column.like(f"%{operand}%"))
                            elif operation == 'ilike':
                                query = query.filter(column.ilike(f"%{operand}%"))
                            elif operation == 'gt':
                                query = query.filter(column > operand)
                            elif operation == 'gte':
                                query = query.filter(column >= operand)
                            elif operation == 'lt':
                                query = query.filter(column < operand)
                            elif operation == 'lte':
                                query = query.filter(column <= operand)
                            elif operation == 'between':
                                query = query.filter(column.between(operand[0], operand[1]))
                            elif operation == 'is_null':
                                query = query.filter(column.is_(None) if operand else column.isnot(None))
                    elif isinstance(value, list):
                        query = query.filter(column.in_(value))
                    else:
                        query = query.filter(column == value)
            
            # Apply ordering
            if order_by and hasattr(self.model_class, order_by):
                column = getattr(self.model_class, order_by)
                if order_direction.lower() == 'desc':
                    query = query.order_by(desc(column))
                else:
                    query = query.order_by(asc(column))
            
            # Apply pagination
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
                
            entities = query.all()
            self.logger.debug(f"Retrieved {len(entities)} {self.model_class.__name__} entities with filters")
            
            return entities
            
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to retrieve entities by filters: {str(e)}")
            
    def update(self, entity_id: Union[int, str, uuid.UUID], **kwargs) -> Optional[ModelType]:
        """
        Update entity by ID with optimistic locking support
        
        Args:
            entity_id: Primary key value
            **kwargs: Updated attributes
            
        Returns:
            Updated entity instance or None if not found
        """
        try:
            entity = self.get_by_id(entity_id)
            if not entity:
                return None
                
            # Update attributes
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            # Update timestamp if available
            if hasattr(entity, 'updated_at'):
                entity.updated_at = datetime.utcnow()
                
            with self.transaction():
                self.db_session.flush()
                self.db_session.refresh(entity)
                
            self.logger.info(f"Updated {self.model_class.__name__} ID: {entity_id}")
            return entity
            
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to update entity: {str(e)}")
            
    def bulk_update(self, filters: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """
        Bulk update entities matching filters
        
        Args:
            filters: Filter conditions
            updates: Updated attributes
            
        Returns:
            Number of updated entities
        """
        try:
            query = self.db_session.query(self.model_class)
            
            # Apply filters
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    column = getattr(self.model_class, field)
                    query = query.filter(column == value)
            
            # Add timestamp if available
            if hasattr(self.model_class, 'updated_at'):
                updates['updated_at'] = datetime.utcnow()
                
            with self.transaction():
                updated_count = query.update(updates, synchronize_session=False)
                
            self.logger.info(f"Bulk updated {updated_count} {self.model_class.__name__} entities")
            return updated_count
            
        except SQLAlchemyError as e:
            raise RepositoryException(f"Bulk update failed: {str(e)}")
            
    def delete(self, entity_id: Union[int, str, uuid.UUID]) -> bool:
        """
        Delete entity by ID with soft delete support
        
        Args:
            entity_id: Primary key value
            
        Returns:
            True if deleted, False if not found
        """
        try:
            entity = self.get_by_id(entity_id)
            if not entity:
                return False
            
            # Soft delete if supported
            if hasattr(entity, 'deleted_at'):
                entity.deleted_at = datetime.utcnow()
                if hasattr(entity, 'is_deleted'):
                    entity.is_deleted = True
            else:
                # Hard delete
                self.db_session.delete(entity)
                
            with self.transaction():
                pass  # Changes are committed in transaction context
                
            self.logger.info(f"Deleted {self.model_class.__name__} ID: {entity_id}")
            return True
            
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to delete entity: {str(e)}")
            
    def bulk_delete(self, filters: Dict[str, Any]) -> int:
        """
        Bulk delete entities matching filters
        
        Args:
            filters: Filter conditions
            
        Returns:
            Number of deleted entities
        """
        try:
            query = self.db_session.query(self.model_class)
            
            # Apply filters
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    column = getattr(self.model_class, field)
                    query = query.filter(column == value)
            
            # Soft delete if supported
            if hasattr(self.model_class, 'deleted_at'):
                updates = {
                    'deleted_at': datetime.utcnow(),
                    'is_deleted': True
                }
                deleted_count = query.update(updates, synchronize_session=False)
            else:
                deleted_count = query.delete(synchronize_session=False)
                
            with self.transaction():
                pass  # Changes are committed in transaction context
                
            self.logger.info(f"Bulk deleted {deleted_count} {self.model_class.__name__} entities")
            return deleted_count
            
        except SQLAlchemyError as e:
            raise RepositoryException(f"Bulk delete failed: {str(e)}")
            
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities with optional filters
        
        Args:
            filters: Optional filter conditions
            
        Returns:
            Number of entities matching criteria
        """
        try:
            query = self.db_session.query(func.count(self.model_class.id))
            
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model_class, field):
                        column = getattr(self.model_class, field)
                        query = query.filter(column == value)
            
            count = query.scalar()
            self.logger.debug(f"Counted {count} {self.model_class.__name__} entities")
            
            return count
            
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to count entities: {str(e)}")
            
    def exists(self, entity_id: Union[int, str, uuid.UUID]) -> bool:
        """
        Check if entity exists by ID
        
        Args:
            entity_id: Primary key value
            
        Returns:
            True if entity exists, False otherwise
        """
        try:
            exists = self.db_session.query(
                self.db_session.query(self.model_class).filter(
                    self.model_class.id == entity_id
                ).exists()
            ).scalar()
            
            return exists
            
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to check entity existence: {str(e)}")
            
    def execute_raw_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute raw SQL query with parameter binding
        
        Args:
            query: Raw SQL query string
            params: Query parameters
            
        Returns:
            Query result
        """
        try:
            result = self.db_session.execute(text(query), params or {})
            self.logger.debug(f"Executed raw query: {query}")
            
            return result
            
        except SQLAlchemyError as e:
            raise RepositoryException(f"Raw query execution failed: {str(e)}")
            
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get repository statistics and health metrics
        
        Returns:
            Dictionary containing statistics
        """
        try:
            stats = {
                'total_count': self.count(),
                'table_name': self.model_class.__tablename__,
                'model_name': self.model_class.__name__
            }
            
            # Add timestamp statistics if available
            if hasattr(self.model_class, 'created_at'):
                today = datetime.utcnow().date()
                yesterday = today - timedelta(days=1)
                
                stats['created_today'] = self.count({
                    'created_at': {'gte': today}
                })
                stats['created_yesterday'] = self.count({
                    'created_at': {'between': [yesterday, today]}
                })
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {str(e)}")
            return {'error': str(e)}
            
    def optimize_table(self) -> Dict[str, Any]:
        """
        Perform table optimization and maintenance
        
        Returns:
            Optimization results
        """
        try:
            # Analyze table statistics
            analyze_query = f"ANALYZE {self.model_class.__tablename__}"
            self.execute_raw_query(analyze_query)
            
            # Get table size information
            size_query = """
                SELECT 
                    pg_size_pretty(pg_total_relation_size(%s)) as total_size,
                    pg_size_pretty(pg_relation_size(%s)) as table_size,
                    pg_size_pretty(pg_indexes_size(%s)) as indexes_size
            """
            
            result = self.execute_raw_query(size_query, {
                'table_name': self.model_class.__tablename__
            })
            
            size_info = result.fetchone()
            
            optimization_result = {
                'table_analyzed': True,
                'total_size': size_info[0] if size_info else 'Unknown',
                'table_size': size_info[1] if size_info else 'Unknown',
                'indexes_size': size_info[2] if size_info else 'Unknown',
                'optimization_timestamp': datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Optimized table {self.model_class.__tablename__}")
            return optimization_result
            
        except Exception as e:
            self.logger.error(f"Table optimization failed: {str(e)}")
            return {'error': str(e)}

    def health_check(self) -> Dict[str, Any]:
        """
        Perform repository health check
        
        Returns:
            Health check results
        """
        try:
            # Test basic connectivity
            connection_test = self.db_session.execute(text("SELECT 1")).scalar()
            
            # Get basic statistics
            stats = self.get_statistics()
            
            health_status = {
                'status': 'healthy' if connection_test == 1 else 'unhealthy',
                'connection_test': connection_test == 1,
                'repository_class': self.__class__.__name__,
                'model_class': self.model_class.__name__,
                'statistics': stats,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
