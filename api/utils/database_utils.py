"""
Database Utilities for IA Influencer Agent Platform
Advanced database operations, connection management, and ORM utilities

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent Platform with Multi-Content Protection
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""

import sqlite3
import asyncpg
import aiosqlite
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple, AsyncGenerator, Type, TypeVar
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging
import json
import pickle
import hashlib
from contextlib import asynccontextmanager, contextmanager
import threading
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Text, Boolean, Float, LargeBinary
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
from sqlalchemy.pool import QueuePool
import redis.asyncio as redis
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import pymongo.errors
from enum import Enum
import os
from pathlib import Path
import time
import uuid

logger = logging.getLogger(__name__)

Base = declarative_base()
T = TypeVar('T')


class DatabaseType(Enum):
    """Supported database types"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    db_type: DatabaseType
    host: str = "localhost"
    port: int = 5432
    database: str = "ia_platform"
    username: Optional[str] = None
    password: Optional[str] = None
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    ssl_mode: Optional[str] = None
    connection_timeout: int = 30
    
    def get_connection_string(self) -> str:
        """Generate connection string"""
        if self.db_type == DatabaseType.SQLITE:
            return f"sqlite:///{self.database}"
        elif self.db_type == DatabaseType.POSTGRESQL:
            auth = f"{self.username}:{self.password}@" if self.username and self.password else ""
            ssl = f"?sslmode={self.ssl_mode}" if self.ssl_mode else ""
            return f"postgresql://{auth}{self.host}:{self.port}/{self.database}{ssl}"
        elif self.db_type == DatabaseType.MYSQL:
            auth = f"{self.username}:{self.password}@" if self.username and self.password else ""
            return f"mysql+pymysql://{auth}{self.host}:{self.port}/{self.database}"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")


@dataclass
class QueryResult:
    """Query result container"""
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    affected_rows: int = 0
    execution_time: float = 0.0
    error: Optional[str] = None
    query_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            'success': self.success,
            'data': self.data,
            'affected_rows': self.affected_rows,
            'execution_time': round(self.execution_time, 4),
            'error': self.error,
            'query_id': self.query_id
        }


@dataclass
class TransactionContext:
    """Transaction context"""
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: datetime = field(default_factory=datetime.utcnow)
    operations: List[str] = field(default_factory=list)
    committed: bool = False
    rolled_back: bool = False
    
    def add_operation(self, operation: str):
        """Add operation to transaction"""
        self.operations.append(f"{datetime.utcnow().isoformat()}: {operation}")


class DatabaseConnectionManager:
    """Manage database connections and connection pools"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = None
        self.session_factory = None
        self.connection_pool = None
        self._lock = threading.Lock()
        self._initialized = False
    
    def initialize(self):
        """Initialize database connection"""
        with self._lock:
            if self._initialized:
                return
            
            try:
                if self.config.db_type in [DatabaseType.POSTGRESQL, DatabaseType.MYSQL, DatabaseType.SQLITE]:
                    self._initialize_sqlalchemy()
                
                self._initialized = True
                logger.info(f"Database connection initialized: {self.config.db_type.value}")
                
            except Exception as e:
                logger.error(f"Failed to initialize database connection: {str(e)}")
                raise
    
    def _initialize_sqlalchemy(self):
        """Initialize SQLAlchemy engine and session factory"""
        connection_string = self.config.get_connection_string()
        
        engine_kwargs = {
            'echo': False,
            'poolclass': QueuePool,
            'pool_size': self.config.pool_size,
            'max_overflow': self.config.max_overflow,
            'pool_timeout': self.config.pool_timeout,
            'pool_recycle': self.config.pool_recycle
        }
        
        self.engine = create_engine(connection_string, **engine_kwargs)
        self.session_factory = sessionmaker(bind=self.engine)
    
    @contextmanager
    def get_session(self):
        """Get database session context manager"""
        if not self._initialized:
            self.initialize()
        
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connection"""



        try:
            if self.config.db_type == DatabaseType.SQLITE:
                return self._test_sqlite_connection()
            elif self.config.db_type == DatabaseType.POSTGRESQL:
                return self._test_postgresql_connection()
            elif self.config.db_type == DatabaseType.MYSQL:
                return self._test_mysql_connection()
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def _test_sqlite_connection(self) -> bool:
        """Test SQLite connection"""



        try:
            with sqlite3.connect(self.config.database, timeout=5) as conn:
                conn.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    def _test_postgresql_connection(self) -> bool:
        """Test PostgreSQL connection"""



        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    
    def _test_mysql_connection(self) -> bool:
        """Test MySQL connection"""



        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    
    def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()
        self._initialized = False


class AsyncDatabaseManager:
    """Asynchronous database operations manager"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool = None
        self._lock = asyncio.Lock()
        self._initialized = False
    
    async def initialize(self):
        """Initialize async database connection"""
        async with self._lock:
            if self._initialized:
                return
            
            try:
                if self.config.db_type == DatabaseType.POSTGRESQL:
                    await self._initialize_postgresql()
                elif self.config.db_type == DatabaseType.SQLITE:
                    await self._initialize_sqlite()
                
                self._initialized = True
                logger.info(f"Async database connection initialized: {self.config.db_type.value}")
                
            except Exception as e:
                logger.error(f"Failed to initialize async database connection: {str(e)}")
                raise
    
    async def _initialize_postgresql(self):
        """Initialize PostgreSQL async connection pool"""
        self.pool = await asyncpg.create_pool(
            host=self.config.host,
            port=self.config.port,
            database=self.config.database,
            user=self.config.username,
            password=self.config.password,
            min_size=1,
            max_size=self.config.pool_size,
            command_timeout=self.config.connection_timeout
        )
    
    async def _initialize_sqlite(self):
        """Initialize SQLite async connection"""
        # For SQLite, we don't have a traditional pool
        self.pool = self.config.database
    
    @asynccontextmanager
    async def get_connection(self):
        """Get async database connection"""
        if not self._initialized:
            await self.initialize()
        
        if self.config.db_type == DatabaseType.POSTGRESQL:
            async with self.pool.acquire() as connection:
                yield connection
        elif self.config.db_type == DatabaseType.SQLITE:
            async with aiosqlite.connect(self.pool) as connection:
                yield connection
    
    async def execute_query(self, query: str, parameters: Optional[List[Any]] = None) -> QueryResult:
        """Execute async query"""
        start_time = time.time()
        query_id = str(uuid.uuid4())
        
        try:
            async with self.get_connection() as conn:
                if self.config.db_type == DatabaseType.POSTGRESQL:
                    if parameters:
                        result = await conn.fetch(query, *parameters)
                    else:
                        result = await conn.fetch(query)
                    
                    data = [dict(row) for row in result]
                    
                elif self.config.db_type == DatabaseType.SQLITE:
                    if parameters:
                        cursor = await conn.execute(query, parameters)
                    else:
                        cursor = await conn.execute(query)
                    
                    rows = await cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    data = [dict(zip(columns, row)) for row in rows]
                    
                    await conn.commit()
                
                execution_time = time.time() - start_time
                
                return QueryResult(
                    success=True,
                    data=data,
                    affected_rows=len(data),
                    execution_time=execution_time,
                    query_id=query_id
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Query execution failed: {str(e)}")
            
            return QueryResult(
                success=False,
                error=str(e),
                execution_time=execution_time,
                query_id=query_id
            )
    
    async def execute_transaction(self, operations: List[Tuple[str, Optional[List[Any]]]]) -> QueryResult:
        """Execute multiple operations in a transaction"""
        start_time = time.time()
        transaction_id = str(uuid.uuid4())
        
        try:
            async with self.get_connection() as conn:
                if self.config.db_type == DatabaseType.POSTGRESQL:
                    async with conn.transaction():
                        results = []
                        for query, params in operations:
                            if params:
                                result = await conn.fetch(query, *params)
                            else:
                                result = await conn.fetch(query)
                            results.extend([dict(row) for row in result])
                
                elif self.config.db_type == DatabaseType.SQLITE:
                    await conn.execute("BEGIN")
                    
                    try:
                        results = []
                        for query, params in operations:
                            if params:
                                cursor = await conn.execute(query, params)
                            else:
                                cursor = await conn.execute(query)
                            
                            rows = await cursor.fetchall()
                            if cursor.description:
                                columns = [desc[0] for desc in cursor.description]
                                results.extend([dict(zip(columns, row)) for row in rows])
                        
                        await conn.commit()
                        
                    except Exception:
                        await conn.rollback()
                        raise
                
                execution_time = time.time() - start_time
                
                return QueryResult(
                    success=True,
                    data=results,
                    affected_rows=len(results),
                    execution_time=execution_time,
                    query_id=transaction_id
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Transaction execution failed: {str(e)}")
            
            return QueryResult(
                success=False,
                error=str(e),
                execution_time=execution_time,
                query_id=transaction_id
            )
    
    async def close(self):
        """Close async database connections"""
        if self.pool and hasattr(self.pool, 'close'):
            await self.pool.close()
        self._initialized = False


class RedisManager:
    """Redis connection and operations manager"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, 
                 db: int = 0, password: Optional[str] = None,
                 max_connections: int = 10):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.max_connections = max_connections
        self.redis_client = None
        self._lock = asyncio.Lock()
        self._initialized = False
    
    async def initialize(self):
        """Initialize Redis connection"""
        async with self._lock:
            if self._initialized:
                return
            
            try:
                self.redis_client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    password=self.password,
                    max_connections=self.max_connections,
                    decode_responses=True
                )
                
                # Test connection
                await self.redis_client.ping()
                self._initialized = True
                logger.info("Redis connection initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize Redis connection: {str(e)}")
                raise
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        if not self._initialized:
            await self.initialize()
        
        try:
            value = await self.redis_client.get(key)
            if value:
                # Try to deserialize JSON
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            return None
            
        except Exception as e:
            logger.error(f"Redis GET failed for key {key}: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set value in Redis"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Serialize complex objects to JSON
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            result = await self.redis_client.set(key, value, ex=expire)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Redis SET failed for key {key}: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self._initialized:
            await self.initialize()
        
        try:
            result = await self.redis_client.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Redis DELETE failed for key {key}: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        if not self._initialized:
            await self.initialize()
        
        try:
            result = await self.redis_client.exists(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Redis EXISTS failed for key {key}: {str(e)}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment value in Redis"""
        if not self._initialized:
            await self.initialize()
        
        try:
            result = await self.redis_client.incrby(key, amount)
            return result
            
        except Exception as e:
            logger.error(f"Redis INCRBY failed for key {key}: {str(e)}")
            return None
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key"""
        if not self._initialized:
            await self.initialize()
        
        try:
            result = await self.redis_client.expire(key, seconds)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Redis EXPIRE failed for key {key}: {str(e)}")
            return False
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern"""
        if not self._initialized:
            await self.initialize()
        
        try:
            keys = await self.redis_client.keys(pattern)
            return keys
            
        except Exception as e:
            logger.error(f"Redis KEYS failed for pattern {pattern}: {str(e)}")
            return []
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
        self._initialized = False


class MongoDBManager:
    """MongoDB connection and operations manager"""
    
    def __init__(self, connection_string: str, database_name: str):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.database = None
        self._lock = asyncio.Lock()
        self._initialized = False
    
    async def initialize(self):
        """Initialize MongoDB connection"""
        async with self._lock:
            if self._initialized:
                return
            
            try:
                self.client = AsyncIOMotorClient(self.connection_string)
                self.database = self.client[self.database_name]
                
                # Test connection
                await self.client.admin.command('ping')
                self._initialized = True
                logger.info("MongoDB connection initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize MongoDB connection: {str(e)}")
                raise
    
    async def insert_document(self, collection: str, document: Dict[str, Any]) -> Optional[str]:
        """Insert document into collection"""
        if not self._initialized:
            await self.initialize()
        
        try:
            result = await self.database[collection].insert_one(document)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"MongoDB insert failed: {str(e)}")
            return None
    
    async def find_documents(self, collection: str, query: Dict[str, Any] = None, 
                           limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Find documents in collection"""
        if not self._initialized:
            await self.initialize()
        
        try:
            cursor = self.database[collection].find(query or {})
            
            if limit:
                cursor = cursor.limit(limit)
            
            documents = []
            async for doc in cursor:
                # Convert ObjectId to string
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"MongoDB find failed: {str(e)}")
            return []
    
    async def update_document(self, collection: str, query: Dict[str, Any], 
                            update: Dict[str, Any]) -> int:
        """Update documents in collection"""
        if not self._initialized:
            await self.initialize()
        
        try:
            result = await self.database[collection].update_many(query, {"$set": update})
            return result.modified_count
            
        except Exception as e:
            logger.error(f"MongoDB update failed: {str(e)}")
            return 0
    
    async def delete_documents(self, collection: str, query: Dict[str, Any]) -> int:
        """Delete documents from collection"""
        if not self._initialized:
            await self.initialize()
        
        try:
            result = await self.database[collection].delete_many(query)
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"MongoDB delete failed: {str(e)}")
            return 0
    
    async def create_index(self, collection: str, index_spec: Union[str, List[Tuple[str, int]]]):
        """Create index on collection"""
        if not self._initialized:
            await self.initialize()
        
        try:
            await self.database[collection].create_index(index_spec)
            logger.info(f"Index created on collection {collection}")
            
        except Exception as e:
            logger.error(f"MongoDB index creation failed: {str(e)}")
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
        self._initialized = False


class QueryBuilder:
    """SQL query builder utility"""
    
    def __init__(self, db_type: DatabaseType = DatabaseType.POSTGRESQL):
        self.db_type = db_type
        self.reset()
    
    def reset(self):
        """Reset query builder"""
        self._select_fields = []
        self._from_table = None
        self._joins = []
        self._where_conditions = []
        self._group_by = []
        self._having_conditions = []
        self._order_by = []
        self._limit_value = None
        self._offset_value = None
        self._parameters = []
        return self
    
    def select(self, fields: Union[str, List[str]]):
        """Add SELECT fields"""
        if isinstance(fields, str):
            self._select_fields.append(fields)
        else:
            self._select_fields.extend(fields)
        return self
    
    def from_table(self, table: str):
        """Set FROM table"""
        self._from_table = table
        return self
    
    def join(self, table: str, condition: str, join_type: str = "INNER"):
        """Add JOIN clause"""
        self._joins.append(f"{join_type} JOIN {table} ON {condition}")
        return self
    
    def where(self, condition: str, *params):
        """Add WHERE condition"""
        self._where_conditions.append(condition)
        self._parameters.extend(params)
        return self
    
    def group_by(self, fields: Union[str, List[str]]):
        """Add GROUP BY fields"""
        if isinstance(fields, str):
            self._group_by.append(fields)
        else:
            self._group_by.extend(fields)
        return self
    
    def having(self, condition: str, *params):
        """Add HAVING condition"""
        self._having_conditions.append(condition)
        self._parameters.extend(params)
        return self
    
    def order_by(self, field: str, direction: str = "ASC"):
        """Add ORDER BY clause"""
        self._order_by.append(f"{field} {direction}")
        return self
    
    def limit(self, count: int):
        """Add LIMIT clause"""
        self._limit_value = count
        return self
    
    def offset(self, count: int):
        """Add OFFSET clause"""
        self._offset_value = count
        return self
    
    def build(self) -> Tuple[str, List[Any]]:
        """Build the SQL query"""
        if not self._select_fields or not self._from_table:
            raise ValueError("SELECT fields and FROM table are required")
        
        query_parts = []
        
        # SELECT
        select_clause = "SELECT " + ", ".join(self._select_fields)
        query_parts.append(select_clause)
        
        # FROM
        query_parts.append(f"FROM {self._from_table}")
        
        # JOINs
        query_parts.extend(self._joins)
        
        # WHERE
        if self._where_conditions:
            where_clause = "WHERE " + " AND ".join(self._where_conditions)
            query_parts.append(where_clause)
        
        # GROUP BY
        if self._group_by:
            group_clause = "GROUP BY " + ", ".join(self._group_by)
            query_parts.append(group_clause)
        
        # HAVING
        if self._having_conditions:
            having_clause = "HAVING " + " AND ".join(self._having_conditions)
            query_parts.append(having_clause)
        
        # ORDER BY
        if self._order_by:
            order_clause = "ORDER BY " + ", ".join(self._order_by)
            query_parts.append(order_clause)
        
        # LIMIT
        if self._limit_value:
            if self.db_type == DatabaseType.POSTGRESQL:
                query_parts.append(f"LIMIT {self._limit_value}")
            elif self.db_type == DatabaseType.MYSQL:
                query_parts.append(f"LIMIT {self._limit_value}")
            elif self.db_type == DatabaseType.SQLITE:
                query_parts.append(f"LIMIT {self._limit_value}")
        
        # OFFSET
        if self._offset_value:
            if self.db_type == DatabaseType.POSTGRESQL:
                query_parts.append(f"OFFSET {self._offset_value}")
            elif self.db_type == DatabaseType.MYSQL:
                query_parts.append(f"OFFSET {self._offset_value}")
            elif self.db_type == DatabaseType.SQLITE:
                query_parts.append(f"OFFSET {self._offset_value}")
        
        query = " ".join(query_parts)
        return query, self._parameters


class DatabaseMigrationManager:
    """Database migration management"""
    
    def __init__(self, connection_manager: DatabaseConnectionManager):
        self.connection_manager = connection_manager
        self.migrations_dir = Path("migrations")
        self.migrations_dir.mkdir(exist_ok=True)
    
    def create_migration(self, name: str, up_sql: str, down_sql: str) -> str:
        """Create a new migration file"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.sql"
        filepath = self.migrations_dir / filename
        
        migration_content = f"""-- Migration: {name}
-- Created: {datetime.utcnow().isoformat()}

-- UP
{up_sql}

-- DOWN (Rollback)
{down_sql}
"""
        
        with open(filepath, 'w') as f:
            f.write(migration_content)
        
        logger.info(f"Migration created: {filename}")
        return str(filepath)
    
    def get_pending_migrations(self) -> List[str]:
        """Get list of pending migrations"""
        with self.connection_manager.get_session() as session:
            # Create migrations table if it doesn't exist
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(255) PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Get applied migrations
            result = session.execute(text("SELECT version FROM schema_migrations"))
            applied = {row[0] for row in result.fetchall()}
            
            # Get all migration files
            migration_files = sorted([f.stem for f in self.migrations_dir.glob("*.sql")])
            
            # Return pending migrations
            return [m for m in migration_files if m not in applied]
    
    def apply_migrations(self) -> Dict[str, Any]:
        """Apply pending migrations"""
        pending = self.get_pending_migrations()
        
        if not pending:
            return {"applied": 0, "migrations": [], "message": "No pending migrations"}
        
        applied_migrations = []
        
        with self.connection_manager.get_session() as session:
            for migration in pending:
                try:
                    migration_file = self.migrations_dir / f"{migration}.sql"
                    
                    with open(migration_file, 'r') as f:
                        content = f.read()
                    
                    # Extract UP section
                    up_section = self._extract_migration_section(content, "UP")
                    
                    if up_section:
                        # Execute migration
                        session.execute(text(up_section))
                        
                        # Record migration
                        session.execute(
                            text("INSERT INTO schema_migrations (version) VALUES (:version)"),
                            {"version": migration}
                        )
                        
                        applied_migrations.append(migration)
                        logger.info(f"Applied migration: {migration}")
                
                except Exception as e:
                    logger.error(f"Failed to apply migration {migration}: {str(e)}")
                    session.rollback()
                    break
        
        return {
            "applied": len(applied_migrations),
            "migrations": applied_migrations,
            "message": f"Applied {len(applied_migrations)} migrations"
        }
    
    def rollback_migration(self, version: str) -> bool:
        """Rollback a specific migration"""
        migration_file = self.migrations_dir / f"{version}.sql"
        
        if not migration_file.exists():
            logger.error(f"Migration file not found: {version}")
            return False
        
        try:
            with open(migration_file, 'r') as f:
                content = f.read()
            
            # Extract DOWN section
            down_section = self._extract_migration_section(content, "DOWN")
            
            if down_section:
                with self.connection_manager.get_session() as session:
                    # Execute rollback
                    session.execute(text(down_section))
                    
                    # Remove migration record
                    session.execute(
                        text("DELETE FROM schema_migrations WHERE version = :version"),
                        {"version": version}
                    )
                    
                    logger.info(f"Rolled back migration: {version}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to rollback migration {version}: {str(e)}")
            return False
    
    def _extract_migration_section(self, content: str, section: str) -> Optional[str]:
        """Extract UP or DOWN section from migration content"""
        lines = content.split('\n')
        section_start = None
        section_end = None
        
        for i, line in enumerate(lines):
            if line.strip().startswith(f"-- {section}"):
                section_start = i + 1
            elif section_start is not None and line.strip().startswith("-- ") and section not in line:
                section_end = i
                break
        
        if section_start is not None:
            section_lines = lines[section_start:section_end]
            return '\n'.join(section_lines).strip()
        
        return None


class DatabaseUtils:
    """Database utility functions"""
    
    @staticmethod
    def sanitize_table_name(name: str) -> str:
        """Sanitize table name for SQL safety"""
        # Remove dangerous characters and ensure valid identifier
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', name)
        return sanitized[:63]  # PostgreSQL limit
    
    @staticmethod
    def generate_uuid() -> str:
        """Generate UUID for database records"""



        return str(uuid.uuid4())
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> str:
        """Hash password for database storage"""
        if salt is None:
            salt = os.urandom(32).hex()
        
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${password_hash.hex()}"
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""



        try:
            salt, password_hash = hashed.split('$')
            new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_hash == new_hash.hex()
        except Exception:
            return False
    
    @staticmethod
    def serialize_json(obj: Any) -> str:
        """Serialize object to JSON for database storage"""



        return json.dumps(obj, default=str, ensure_ascii=False)
    
    @staticmethod
    def deserialize_json(json_str: str) -> Any:
        """Deserialize JSON from database"""



        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return None


class DatabaseError(Exception):
    """Custom database exception"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 query: Optional[str] = None):
        super().__init__(message)
        self.error_code = error_code
        self.query = query
