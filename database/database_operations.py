"""🔧 Database Operations - Consolidated CRUD, Migrations & Advanced Operations
===============================================================================
Module: database/database_operations.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Consolidated Database Operations - Enterprise-Ready
Responsibility: Complete database operations management and business logic

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This consolidated module provides comprehensive database operations including:
- Advanced CRUD operations with transaction management
- Database schema migrations and versioning
- Query optimization and performance monitoring
- Multi-database support (PostgreSQL, Redis, MongoDB, Elasticsearch)
- Business logic integration for creator workflow
- Audit logging and compliance management
"""

import os
import logging
import asyncio
import datetime
from typing import List, Dict, Any, Optional, Type, Union, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
import json
import hashlib

# Optional imports for production features
try:
    import sqlalchemy
    from sqlalchemy import text, inspect, and_, or_, desc, asc, func, create_engine
    from sqlalchemy.orm import Session, sessionmaker
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.exc import SQLAlchemyError
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    sqlalchemy = None

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import pymongo
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

try:
    from elasticsearch import Elasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseType(Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    REDIS = "redis"
    MONGODB = "mongodb"
    ELASTICSEARCH = "elasticsearch"

class OperationType(Enum):
    """Database operation types"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    QUERY = "query"
    BATCH = "batch"
    MIGRATION = "migration"
    OPTIMIZATION = "optimization"

@dataclass
class DatabaseOperation:
    """Represents a database operation for audit and monitoring"""
    operation_id: str
    operation_type: OperationType
    database_type: DatabaseType
    table_name: str
    user_id: Optional[str] = None
    timestamp: datetime.datetime = None
    duration_ms: float = 0.0
    affected_rows: int = 0
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

class Migration:
    """Represents a database migration"""
    
    def __init__(self, version: str, name: str, up_func: Callable = None, down_func: Callable = None):
        self.version = version
        self.name = name
        self.up_func = up_func
        self.down_func = down_func
        self.created_at = datetime.datetime.utcnow()
        self.applied_at = None
        self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate migration checksum for integrity validation"""
        content = f"{self.version}{self.name}{str(self.up_func)}{str(self.down_func)}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def apply(self, connection=None) -> bool:
        """Apply the migration"""
        try:
            if self.up_func:
                if asyncio.iscoroutinefunction(self.up_func):
                    await self.up_func(connection)
                else:
                    self.up_func(connection)
            self.applied_at = datetime.datetime.utcnow()
            logger.info(f"Applied migration {self.version}: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to apply migration {self.version}: {e}")
            return False
    
    async def rollback(self, connection=None) -> bool:
        """Rollback the migration"""
        try:
            if self.down_func:
                if asyncio.iscoroutinefunction(self.down_func):
                    await self.down_func(connection)
                else:
                    self.down_func(connection)
            self.applied_at = None
            logger.info(f"Rolled back migration {self.version}: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to rollback migration {self.version}: {e}")
            return False

class DatabaseOperations:
    """Enterprise database operations manager"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.connections = {}
        self.session_makers = {}
        self.migrations = []
        self.operation_history = []
        self.performance_metrics = {}
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Initialize database connections"""
        try:
            # PostgreSQL/SQLite connection
            if SQLALCHEMY_AVAILABLE:
                db_url = self.config.get('database_url', os.getenv('DATABASE_URL', 'sqlite:///./database.db'))
                engine = create_engine(db_url, echo=self.config.get('echo', False))
                self.connections[DatabaseType.POSTGRESQL] = engine
                self.session_makers[DatabaseType.POSTGRESQL] = sessionmaker(bind=engine)
                
            # Redis connection
            if REDIS_AVAILABLE and 'redis' in self.config:
                redis_config = self.config['redis']
                self.connections[DatabaseType.REDIS] = redis.Redis(
                    host=redis_config.get('host', 'localhost'),
                    port=redis_config.get('port', 6379),
                    db=redis_config.get('db', 0),
                    decode_responses=True
                )
            
            # MongoDB connection
            if MONGODB_AVAILABLE and 'mongodb' in self.config:
                mongo_config = self.config['mongodb']
                self.connections[DatabaseType.MONGODB] = pymongo.MongoClient(
                    mongo_config.get('url', 'mongodb://localhost:27017/')
                )
            
            # Elasticsearch connection
            if ELASTICSEARCH_AVAILABLE and 'elasticsearch' in self.config:
                es_config = self.config['elasticsearch']
                self.connections[DatabaseType.ELASTICSEARCH] = Elasticsearch(
                    [es_config.get('url', 'http://localhost:9200')]
                )
                
        except Exception as e:
            logger.error(f"Failed to initialize database connections: {e}")
    
    @asynccontextmanager
    async def get_session(self, db_type: DatabaseType = DatabaseType.POSTGRESQL):
        """Get database session with automatic cleanup"""
        if db_type not in self.session_makers:
            raise ValueError(f"No session maker available for {db_type}")
        
        session = self.session_makers[db_type]()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def _record_operation(self, operation: DatabaseOperation):
        """Record operation for audit and monitoring"""
        self.operation_history.append(operation)
        
        # Keep only last 1000 operations in memory
        if len(self.operation_history) > 1000:
            self.operation_history = self.operation_history[-1000:]
        
        # Update performance metrics
        op_type = operation.operation_type.value
        if op_type not in self.performance_metrics:
            self.performance_metrics[op_type] = {
                'count': 0,
                'total_duration': 0.0,
                'avg_duration': 0.0,
                'success_rate': 0.0,
                'last_operation': None
            }
        
        metrics = self.performance_metrics[op_type]
        metrics['count'] += 1
        metrics['total_duration'] += operation.duration_ms
        metrics['avg_duration'] = metrics['total_duration'] / metrics['count']
        
        success_count = sum(1 for op in self.operation_history 
                          if op.operation_type == operation.operation_type and op.success)
        total_count = sum(1 for op in self.operation_history 
                         if op.operation_type == operation.operation_type)
        metrics['success_rate'] = success_count / total_count if total_count > 0 else 0.0
        metrics['last_operation'] = operation.timestamp
    
    async def create(self, model_class: Type, data: Dict[str, Any], 
                    user_id: Optional[str] = None) -> Any:
        """Create a new record"""
        start_time = datetime.datetime.utcnow()
        operation_id = f"create_{model_class.__name__}_{start_time.timestamp()}"
        
        try:
            async with self.get_session() as session:
                # Create instance
                instance = model_class(**data)
                session.add(instance)
                session.flush()  # Get the ID without committing
                
                # Record operation
                duration = (datetime.datetime.utcnow() - start_time).total_seconds() * 1000
                operation = DatabaseOperation(
                    operation_id=operation_id,
                    operation_type=OperationType.CREATE,
                    database_type=DatabaseType.POSTGRESQL,
                    table_name=model_class.__tablename__ if hasattr(model_class, '__tablename__') else model_class.__name__,
                    user_id=user_id,
                    duration_ms=duration,
                    affected_rows=1,
                    success=True,
                    metadata={'data_keys': list(data.keys())}
                )
                self._record_operation(operation)
                
                logger.info(f"Created {model_class.__name__} with ID: {instance.id}")
                return instance
                
        except Exception as e:
            duration = (datetime.datetime.utcnow() - start_time).total_seconds() * 1000
            operation = DatabaseOperation(
                operation_id=operation_id,
                operation_type=OperationType.CREATE,
                database_type=DatabaseType.POSTGRESQL,
                table_name=model_class.__tablename__ if hasattr(model_class, '__tablename__') else model_class.__name__,
                user_id=user_id,
                duration_ms=duration,
                affected_rows=0,
                success=False,
                error_message=str(e)
            )
            self._record_operation(operation)
            logger.error(f"Failed to create {model_class.__name__}: {e}")
            raise
    
    async def read(self, model_class: Type, obj_id: Any, 
                  user_id: Optional[str] = None) -> Optional[Any]:
        """Read a record by ID"""
        start_time = datetime.datetime.utcnow()
        operation_id = f"read_{model_class.__name__}_{obj_id}_{start_time.timestamp()}"
        
        try:
            async with self.get_session() as session:
                instance = session.query(model_class).filter(
                    model_class.id == obj_id
                ).first()
                
                duration = (datetime.datetime.utcnow() - start_time).total_seconds() * 1000
                operation = DatabaseOperation(
                    operation_id=operation_id,
                    operation_type=OperationType.READ,
                    database_type=DatabaseType.POSTGRESQL,
                    table_name=model_class.__tablename__ if hasattr(model_class, '__tablename__') else model_class.__name__,
                    user_id=user_id,
                    duration_ms=duration,
                    affected_rows=1 if instance else 0,
                    success=True,
                    metadata={'object_id': str(obj_id)}
                )
                self._record_operation(operation)
                
                return instance
                
        except Exception as e:
            duration = (datetime.datetime.utcnow() - start_time).total_seconds() * 1000
            operation = DatabaseOperation(
                operation_id=operation_id,
                operation_type=OperationType.READ,
                database_type=DatabaseType.POSTGRESQL,
                table_name=model_class.__tablename__ if hasattr(model_class, '__tablename__') else model_class.__name__,
                user_id=user_id,
                duration_ms=duration,
                affected_rows=0,
                success=False,
                error_message=str(e)
            )
            self._record_operation(operation)
            logger.error(f"Failed to read {model_class.__name__} with ID {obj_id}: {e}")
            raise
    
    async def update(self, model_class: Type, obj_id: Any, data: Dict[str, Any],
                    user_id: Optional[str] = None) -> Optional[Any]:
        """Update a record"""
        start_time = datetime.datetime.utcnow()
        operation_id = f"update_{model_class.__name__}_{obj_id}_{start_time.timestamp()}"
        
        try:
            async with self.get_session() as session:
                instance = session.query(model_class).filter(
                    model_class.id == obj_id
                ).first()
                
                if not instance:
                    duration = (datetime.datetime.utcnow() - start_time).total_seconds() * 1000
                    operation = DatabaseOperation(
                        operation_id=operation_id,
                        operation_type=OperationType.UPDATE,
                        database_type=DatabaseType.POSTGRESQL,
                        table_name=model_class.__tablename__ if hasattr(model_class, '__tablename__') else model_class.__name__,
                        user_id=user_id,
                        duration_ms=duration,
                        affected_rows=0,
                        success=False,
                        error_message="Record not found"
                    )
                    self._record_operation(operation)
                    return None
                
                # Update fields
                for key, value in data.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
                
                # Update timestamp if available
                if hasattr(instance, 'updated_at'):
                    instance.updated_at = datetime.datetime.utcnow()
                
                duration = (datetime.datetime.utcnow() - start_time).total_seconds() * 1000
                operation = DatabaseOperation(
                    operation_id=operation_id,
                    operation_type=OperationType.UPDATE,
                    database_type=DatabaseType.POSTGRESQL,
                    table_name=model_class.__tablename__ if hasattr(model_class, '__tablename__') else model_class.__name__,
                    user_id=user_id,
                    duration_ms=duration,
                    affected_rows=1,
                    success=True,
                    metadata={'updated_fields': list(data.keys())}
                )
                self._record_operation(operation)
                
                logger.info(f"Updated {model_class.__name__} with ID: {obj_id}")
                return instance
                
        except Exception as e:
            duration = (datetime.datetime.utcnow() - start_time).total_seconds() * 1000
            operation = DatabaseOperation(
                operation_id=operation_id,
                operation_type=OperationType.UPDATE,
                database_type=DatabaseType.POSTGRESQL,
                table_name=model_class.__tablename__ if hasattr(model_class, '__tablename__') else model_class.__name__,
                user_id=user_id,
                duration_ms=duration,
                affected_rows=0,
                success=False,
                error_message=str(e)
            )
            self._record_operation(operation)
            logger.error(f"Failed to update {model_class.__name__} with ID {obj_id}: {e}")
            raise
    
    async def delete(self, model_class: Type, obj_id: Any,
                    user_id: Optional[str] = None) -> bool:
        """Delete a record"""
        start_time = datetime.datetime.utcnow()
        operation_id = f"delete_{model_class.__name__}_{obj_id}_{start_time.timestamp()}"
        
        try:
            async with self.get_session() as session:
                instance = session.query(model_class).filter(
                    model_class.id == obj_id
                ).first()
                
                if not instance:
                    duration = (datetime.datetime.utcnow() - start_time).total_seconds() * 1000
                    operation = DatabaseOperation(
                        operation_id=operation_id,
                        operation_type=OperationType.DELETE,
                        database_type=DatabaseType.POSTGRESQL,
                        table_name=model_class.__tablename__ if hasattr(model_class, '__tablename__') else model_class.__name__,
                        user_id=user_id,
                        duration_ms=duration,
                        affected_rows=0,
                        success=False,
                        error_message="Record not found"
                    )
                    self._record_operation(operation)
                    return False
                
                session.delete(instance)
                
                duration = (datetime.datetime.utcnow() - start_time).total_seconds() * 1000
                operation = DatabaseOperation(
                    operation_id=operation_id,
                    operation_type=OperationType.DELETE,
                    database_type=DatabaseType.POSTGRESQL,
                    table_name=model_class.__tablename__ if hasattr(model_class, '__tablename__') else model_class.__name__,
                    user_id=user_id,
                    duration_ms=duration,
                    affected_rows=1,
                    success=True
                )
                self._record_operation(operation)
                
                logger.info(f"Deleted {model_class.__name__} with ID: {obj_id}")
                return True
                
        except Exception as e:
            duration = (datetime.datetime.utcnow() - start_time).total_seconds() * 1000
            operation = DatabaseOperation(
                operation_id=operation_id,
                operation_type=OperationType.DELETE,
                database_type=DatabaseType.POSTGRESQL,
                table_name=model_class.__tablename__ if hasattr(model_class, '__tablename__') else model_class.__name__,
                user_id=user_id,
                duration_ms=duration,
                affected_rows=0,
                success=False,
                error_message=str(e)
            )
            self._record_operation(operation)
            logger.error(f"Failed to delete {model_class.__name__} with ID {obj_id}: {e}")
            raise
    
    async def query(self, model_class: Type, filters: Dict[str, Any] = None,
                   order_by: Optional[str] = None, limit: Optional[int] = None,
                   offset: Optional[int] = None, user_id: Optional[str] = None) -> List[Any]:
        """Query records with filters"""
        start_time = datetime.datetime.utcnow()
        operation_id = f"query_{model_class.__name__}_{start_time.timestamp()}"
        
        try:
            async with self.get_session() as session:
                query = session.query(model_class)
                
                # Apply filters
                if filters:
                    for key, value in filters.items():
                        if hasattr(model_class, key):
                            column = getattr(model_class, key)
                            if isinstance(value, dict):
                                # Handle complex filters like {'>=': 100}
                                for op, val in value.items():
                                    if op == '>=':
                                        query = query.filter(column >= val)
                                    elif op == '<=':
                                        query = query.filter(column <= val)
                                    elif op == '>':
                                        query = query.filter(column > val)
                                    elif op == '<':
                                        query = query.filter(column < val)
                                    elif op == 'like':
                                        query = query.filter(column.like(val))
                                    elif op == 'in':
                                        query = query.filter(column.in_(val))
                            else:
                                query = query.filter(column == value)
                
                # Apply ordering
                if order_by:
                    if order_by.startswith('-'):
                        # Descending order
                        column_name = order_by[1:]
                        if hasattr(model_class, column_name):
                            query = query.order_by(desc(getattr(model_class, column_name)))
                    else:
                        # Ascending order
                        if hasattr(model_class, order_by):
                            query = query.order_by(asc(getattr(model_class, order_by)))
                
                # Apply pagination
                if offset:
                    query = query.offset(offset)
                if limit:
                    query = query.limit(limit)
                
                results = query.all()
                
                duration = (datetime.datetime.utcnow() - start_time).total_seconds() * 1000
                operation = DatabaseOperation(
                    operation_id=operation_id,
                    operation_type=OperationType.QUERY,
                    database_type=DatabaseType.POSTGRESQL,
                    table_name=model_class.__tablename__ if hasattr(model_class, '__tablename__') else model_class.__name__,
                    user_id=user_id,
                    duration_ms=duration,
                    affected_rows=len(results),
                    success=True,
                    metadata={
                        'filters': filters or {},
                        'order_by': order_by,
                        'limit': limit,
                        'offset': offset
                    }
                )
                self._record_operation(operation)
                
                return results
                
        except Exception as e:
            duration = (datetime.datetime.utcnow() - start_time).total_seconds() * 1000
            operation = DatabaseOperation(
                operation_id=operation_id,
                operation_type=OperationType.QUERY,
                database_type=DatabaseType.POSTGRESQL,
                table_name=model_class.__tablename__ if hasattr(model_class, '__tablename__') else model_class.__name__,
                user_id=user_id,
                duration_ms=duration,
                affected_rows=0,
                success=False,
                error_message=str(e)
            )
            self._record_operation(operation)
            logger.error(f"Failed to query {model_class.__name__}: {e}")
            raise
    
    async def paginate(self, model_class: Type, page: int = 1, per_page: int = 20,
                      filters: Dict[str, Any] = None, order_by: Optional[str] = None,
                      user_id: Optional[str] = None) -> Dict[str, Any]:
        """Paginate query results"""
        offset = (page - 1) * per_page
        
        # Get total count
        async with self.get_session() as session:
            count_query = session.query(func.count(model_class.id))
            if filters:
                for key, value in filters.items():
                    if hasattr(model_class, key):
                        column = getattr(model_class, key)
                        count_query = count_query.filter(column == value)
            total = count_query.scalar()
        
        # Get page results
        items = await self.query(
            model_class=model_class,
            filters=filters,
            order_by=order_by,
            limit=per_page,
            offset=offset,
            user_id=user_id
        )
        
        total_pages = (total + per_page - 1) // per_page
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page < total_pages else None
        }
    
    # Migration Management
    
    def add_migration(self, migration: Migration):
        """Add a migration to the manager"""
        self.migrations.append(migration)
        self.migrations.sort(key=lambda m: m.version)
    
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        if not SQLALCHEMY_AVAILABLE:
            return []
        
        try:
            async with self.get_session() as session:
                # Ensure migrations table exists
                await self._ensure_migrations_table(session)
                
                result = session.execute(text("SELECT version FROM schema_migrations ORDER BY applied_at"))
                return [row[0] for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []
    
    async def _ensure_migrations_table(self, session):
        """Ensure migrations tracking table exists"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            checksum VARCHAR(64) NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        session.execute(text(create_table_sql))
    
    async def migrate_up(self, target_version: Optional[str] = None) -> bool:
        """Apply migrations up to target version"""
        try:
            applied = await self.get_applied_migrations()
            
            for migration in self.migrations:
                if migration.version in applied:
                    continue
                    
                if target_version and migration.version > target_version:
                    break
                
                logger.info(f"Applying migration {migration.version}: {migration.name}")
                
                async with self.get_session() as session:
                    connection = session.connection()
                    success = await migration.apply(connection)
                    
                    if success:
                        # Record applied migration
                        session.execute(text(
                            "INSERT INTO schema_migrations (version, name, checksum) VALUES (:version, :name, :checksum)"
                        ), {
                            'version': migration.version,
                            'name': migration.name,
                            'checksum': migration.checksum
                        })
                    else:
                        logger.error(f"Failed to apply migration {migration.version}")
                        return False
            
            logger.info("All migrations applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    async def migrate_down(self, target_version: str) -> bool:
        """Rollback migrations down to target version"""
        try:
            applied = await self.get_applied_migrations()
            
            # Find migrations to rollback (in reverse order)
            to_rollback = []
            for migration in reversed(self.migrations):
                if migration.version in applied and migration.version > target_version:
                    to_rollback.append(migration)
            
            for migration in to_rollback:
                logger.info(f"Rolling back migration {migration.version}: {migration.name}")
                
                async with self.get_session() as session:
                    connection = session.connection()
                    success = await migration.rollback(connection)
                    
                    if success:
                        # Remove from applied migrations
                        session.execute(text(
                            "DELETE FROM schema_migrations WHERE version = :version"
                        ), {'version': migration.version})
                    else:
                        logger.error(f"Failed to rollback migration {migration.version}")
                        return False
            
            logger.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    # Performance and Analytics
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics"""
        return {
            'operation_metrics': self.performance_metrics,
            'total_operations': len(self.operation_history),
            'recent_operations': self.operation_history[-10:] if self.operation_history else [],
            'database_connections': {
                db_type.value: 'connected' if db_type in self.connections else 'not_connected'
                for db_type in DatabaseType
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        health_status = {
            'overall_health': 'healthy',
            'databases': {},
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
        
        # Check PostgreSQL/SQLite
        if DatabaseType.POSTGRESQL in self.connections:
            try:
                async with self.get_session() as session:
                    session.execute(text("SELECT 1"))
                health_status['databases']['postgresql'] = 'healthy'
            except Exception as e:
                health_status['databases']['postgresql'] = f'unhealthy: {e}'
                health_status['overall_health'] = 'degraded'
        
        # Check Redis
        if DatabaseType.REDIS in self.connections:
            try:
                redis_conn = self.connections[DatabaseType.REDIS]
                redis_conn.ping()
                health_status['databases']['redis'] = 'healthy'
            except Exception as e:
                health_status['databases']['redis'] = f'unhealthy: {e}'
                health_status['overall_health'] = 'degraded'
        
        # Check MongoDB
        if DatabaseType.MONGODB in self.connections:
            try:
                mongo_conn = self.connections[DatabaseType.MONGODB]
                mongo_conn.admin.command('ping')
                health_status['databases']['mongodb'] = 'healthy'
            except Exception as e:
                health_status['databases']['mongodb'] = f'unhealthy: {e}'
                health_status['overall_health'] = 'degraded'
        
        # Check Elasticsearch
        if DatabaseType.ELASTICSEARCH in self.connections:
            try:
                es_conn = self.connections[DatabaseType.ELASTICSEARCH]
                es_conn.ping()
                health_status['databases']['elasticsearch'] = 'healthy'
            except Exception as e:
                health_status['databases']['elasticsearch'] = f'unhealthy: {e}'
                health_status['overall_health'] = 'degraded'
        
        return health_status
    
    async def optimize_database(self) -> Dict[str, Any]:
        """Perform database optimization"""
        optimization_results = {
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'optimizations_applied': [],
            'recommendations': []
        }
        
        try:
            async with self.get_session() as session:
                # Analyze query performance
                slow_queries = []
                for op in self.operation_history:
                    if op.duration_ms > 1000:  # Queries slower than 1 second
                        slow_queries.append(op)
                
                if slow_queries:
                    optimization_results['recommendations'].append(
                        f"Found {len(slow_queries)} slow queries (>1s). Consider adding indexes."
                    )
                
                # Check for missing indexes
                if SQLALCHEMY_AVAILABLE:
                    # This is a simplified check - in real implementation,
                    # you would analyze query plans and suggest specific indexes
                    optimization_results['recommendations'].append(
                        "Consider adding indexes on frequently queried columns"
                    )
                
                # Vacuum/analyze for PostgreSQL
                if 'postgresql' in str(session.bind.url):
                    try:
                        session.execute(text("ANALYZE"))
                        optimization_results['optimizations_applied'].append("ANALYZE completed")
                    except Exception as e:
                        logger.warning(f"Could not run ANALYZE: {e}")
                
                optimization_results['status'] = 'completed'
                
        except Exception as e:
            optimization_results['status'] = 'failed'
            optimization_results['error'] = str(e)
            logger.error(f"Database optimization failed: {e}")
        
        return optimization_results

# Creator Workflow Integration Functions

async def create_content_record(db_ops: DatabaseOperations, content_data: Dict[str, Any],
                               creator_id: str) -> Any:
    """Create a content record with creator workflow integration"""
    # Enhance content data with workflow metadata
    enhanced_data = {
        **content_data,
        'creator_id': creator_id,
        'status': 'uploaded',
        'created_at': datetime.datetime.utcnow(),
        'workflow_stage': 'initial',
        'protection_enabled': True,
        'monetization_enabled': content_data.get('monetization_enabled', False)
    }
    
    # This would use the actual Content model once it's defined
    # For now, we'll assume a generic model structure
    content = await db_ops.create(
        model_class=dict,  # Placeholder - would be actual Content model
        data=enhanced_data,
        user_id=creator_id
    )
    
    logger.info(f"Created content record for creator {creator_id}")
    return content

async def track_creator_analytics(db_ops: DatabaseOperations, event_type: str,
                                 creator_id: str, data: Dict[str, Any]) -> bool:
    """Track analytics for creator workflow"""
    analytics_data = {
        'event_type': event_type,
        'creator_id': creator_id,
        'timestamp': datetime.datetime.utcnow(),
        'data': data,
        'platform': 'ainflue'
    }
    
    # This would use the actual Analytics model
    try:
        await db_ops.create(
            model_class=dict,  # Placeholder - would be actual Analytics model
            data=analytics_data,
            user_id=creator_id
        )
        return True
    except Exception as e:
        logger.error(f"Failed to track analytics: {e}")
        return False

# Export main class and utility functions
__all__ = [
    'DatabaseOperations',
    'Migration',
    'DatabaseType',
    'OperationType',
    'DatabaseOperation',
    'create_content_record',
    'track_creator_analytics'
]