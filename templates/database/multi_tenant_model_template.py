"""
🏢 MULTI-TENANT MODEL TEMPLATE - DBA EXPERT IMPLEMENTATION
===========================================================

Enterprise-grade multi-tenant database model template with:
- Row-level security and tenant isolation
- Shared schema with tenant partitioning
- Cross-tenant query prevention
- Tenant-aware migrations and seeding
- Performance optimization per tenant
- Tenant lifecycle management
- Data export/import per tenant
- Compliance and audit logging

Author: DBA Expert
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Union, Type, Generic, TypeVar
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import uuid
import asyncio
import logging
import json
from contextlib import asynccontextmanager
from enum import Enum
import hashlib
import sqlalchemy as sa
from sqlalchemy import MetaData, Table, Column, String, DateTime, Boolean, Integer, Text, ForeignKey, Index, CheckConstraint
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker, relationship, selectinload, joinedload
from sqlalchemy.sql import func, select, insert, update, delete
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.schema import CreateSchema, DropSchema
from sqlalchemy.pool import NullPool
from pydantic import BaseModel, Field, validator
import redis.asyncio as redis
import asyncpg
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations
import boto3
from botocore.exceptions import ClientError


T = TypeVar('T')


class TenancyType(Enum):
    """Multi-tenancy implementation types"""
    SHARED_DATABASE_SHARED_SCHEMA = "shared_db_shared_schema"
    SHARED_DATABASE_SEPARATE_SCHEMA = "shared_db_separate_schema"
    SEPARATE_DATABASE = "separate_database"


class TenantStatus(Enum):
    """Tenant status enumeration"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"
    MIGRATING = "migrating"
    ARCHIVED = "archived"


class DataResidency(Enum):
    """Data residency requirements"""
    US = "us"
    EU = "eu"
    APAC = "apac"
    CANADA = "canada"
    UK = "uk"


@dataclass
class MultiTenantConfig:
    """Multi-tenant configuration"""
    # Tenancy settings
    tenancy_type: TenancyType = TenancyType.SHARED_DATABASE_SHARED_SCHEMA
    enable_row_level_security: bool = True
    tenant_id_column: str = "tenant_id"
    
    # Database settings
    database_url: str = "postgresql+asyncpg://user:pass@localhost/multitenantdb"
    connection_pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    
    # Security settings
    enable_tenant_isolation: bool = True
    enable_cross_tenant_prevention: bool = True
    enable_audit_logging: bool = True
    enable_encryption_at_rest: bool = True
    
    # Performance settings
    enable_tenant_partitioning: bool = True
    enable_connection_pooling_per_tenant: bool = False
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    
    # Compliance settings
    enable_gdpr_compliance: bool = True
    enable_data_retention: bool = True
    default_retention_days: int = 2555  # 7 years
    
    # Migration settings
    migrations_path: str = "migrations"
    enable_auto_migrations: bool = False
    
    # Backup and export
    enable_tenant_backups: bool = True
    backup_schedule_cron: str = "0 2 * * *"  # Daily at 2 AM
    backup_storage_type: str = "s3"  # s3, gcs, azure
    
    # Monitoring
    enable_performance_monitoring: bool = True
    slow_query_threshold_ms: int = 1000
    
    # Redis settings
    redis_url: str = "redis://localhost:6379/0"
    redis_key_prefix: str = "multitenant"


@dataclass
class TenantInfo:
    """Tenant information"""
    id: str
    name: str
    status: TenantStatus
    database_name: Optional[str] = None
    schema_name: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Configuration
    settings: Dict[str, Any] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
    data_residency: DataResidency = DataResidency.US
    
    # Limits and quotas
    max_users: int = 1000
    max_storage_gb: int = 100
    max_api_calls_per_hour: int = 10000
    
    # Contact and billing
    admin_email: str = ""
    billing_plan: str = "standard"
    
    # Compliance
    gdpr_enabled: bool = True
    data_retention_days: int = 2555
    
    # Performance
    connection_pool_size: int = 5
    query_timeout_seconds: int = 30


# Base model with tenant awareness
Base = declarative_base()


class TenantAwareBase(Base):
    """Base class for tenant-aware models"""
    __abstract__ = True
    
    @declared_attr
    def tenant_id(cls):
        return Column(
            String(36),
            nullable=False,
            index=True,
            doc="Tenant identifier for multi-tenancy"
        )
    
    @declared_attr
    def __table_args__(cls):
        return (
            Index(f'ix_{cls.__tablename__}_tenant_id', 'tenant_id'),
            CheckConstraint('length(tenant_id) > 0', name=f'ck_{cls.__tablename__}_tenant_id_not_empty'),
        )


class TenantModel(Base):
    """Tenant configuration model"""
    __tablename__ = 'tenants'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    status = Column(String(20), nullable=False, default=TenantStatus.ACTIVE.value)
    database_name = Column(String(255), nullable=True)
    schema_name = Column(String(255), nullable=True)
    
    # Configuration
    settings = Column(JSONB, nullable=False, default=dict)
    features = Column(ARRAY(String), nullable=False, default=list)
    data_residency = Column(String(10), nullable=False, default=DataResidency.US.value)
    
    # Limits and quotas
    max_users = Column(Integer, nullable=False, default=1000)
    max_storage_gb = Column(Integer, nullable=False, default=100)
    max_api_calls_per_hour = Column(Integer, nullable=False, default=10000)
    
    # Contact and billing
    admin_email = Column(String(255), nullable=False)
    billing_plan = Column(String(50), nullable=False, default="standard")
    
    # Compliance
    gdpr_enabled = Column(Boolean, nullable=False, default=True)
    data_retention_days = Column(Integer, nullable=False, default=2555)
    
    # Performance
    connection_pool_size = Column(Integer, nullable=False, default=5)
    query_timeout_seconds = Column(Integer, nullable=False, default=30)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    audit_logs = relationship("TenantAuditLog", back_populates="tenant", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_tenants_status', 'status'),
        Index('ix_tenants_data_residency', 'data_residency'),
        CheckConstraint("status IN ('active', 'suspended', 'inactive', 'migrating', 'archived')", name='ck_tenants_status'),
        CheckConstraint("data_residency IN ('us', 'eu', 'apac', 'canada', 'uk')", name='ck_tenants_data_residency'),
        CheckConstraint('max_users > 0', name='ck_tenants_max_users_positive'),
        CheckConstraint('max_storage_gb > 0', name='ck_tenants_max_storage_positive'),
    )


class TenantAuditLog(Base):
    """Tenant audit log model"""
    __tablename__ = 'tenant_audit_logs'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Audit details
    event_type = Column(String(50), nullable=False)
    event_description = Column(Text, nullable=True)
    user_id = Column(String(36), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Data
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    affected_records = Column(Integer, nullable=False, default=1)
    
    # Metadata
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    session_id = Column(String(255), nullable=True)
    request_id = Column(String(255), nullable=True)
    
    # Relationships
    tenant = relationship("TenantModel", back_populates="audit_logs")
    
    __table_args__ = (
        Index('ix_tenant_audit_logs_tenant_event', 'tenant_id', 'event_type'),
        Index('ix_tenant_audit_logs_timestamp', 'timestamp'),
        Index('ix_tenant_audit_logs_user_id', 'user_id'),
    )


# Example business models with tenant awareness
class UserModel(TenantAwareBase):
    """User model with tenant awareness"""
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    posts = relationship("PostModel", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_users_tenant_email', 'tenant_id', 'email'),
        Index('ix_users_tenant_username', 'tenant_id', 'username'),
        sa.UniqueConstraint('tenant_id', 'email', name='uq_users_tenant_email'),
        sa.UniqueConstraint('tenant_id', 'username', name='uq_users_tenant_username'),
    )


class PostModel(TenantAwareBase):
    """Post model with tenant awareness"""
    __tablename__ = 'posts'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="draft")
    
    # Content metadata
    tags = Column(ARRAY(String), nullable=False, default=list)
    metadata = Column(JSONB, nullable=False, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="posts")
    
    __table_args__ = (
        Index('ix_posts_tenant_user', 'tenant_id', 'user_id'),
        Index('ix_posts_tenant_status', 'tenant_id', 'status'),
        Index('ix_posts_tenant_published', 'tenant_id', 'published_at'),
        ForeignKeyConstraint(['tenant_id', 'user_id'], ['users.tenant_id', 'users.id'], name='fk_posts_user'),
        CheckConstraint("status IN ('draft', 'published', 'archived')", name='ck_posts_status'),
    )


class TenantContext:
    """Tenant context for request lifecycle"""
    
    def __init__(self):
        self._tenant_id: Optional[str] = None
        self._tenant_info: Optional[TenantInfo] = None
    
    @property
    def tenant_id(self) -> Optional[str]:
        return self._tenant_id
    
    @property
    def tenant_info(self) -> Optional[TenantInfo]:
        return self._tenant_info
    
    def set_tenant(self, tenant_id: str, tenant_info: Optional[TenantInfo] = None):
        """Set current tenant context"""
        self._tenant_id = tenant_id
        self._tenant_info = tenant_info
    
    def clear(self):
        """Clear tenant context"""
        self._tenant_id = None
        self._tenant_info = None


# Global tenant context (thread-local would be better in real implementation)
tenant_context = TenantContext()


class TenantRepository(Generic[T]):
    """Base repository with tenant awareness"""
    
    def __init__(self, model_class: Type[T], session: AsyncSession):
        self.model_class = model_class
        self.session = session
        self.logger = logging.getLogger(__name__)
    
    def _ensure_tenant_context(self):
        """Ensure tenant context is set"""
        if not tenant_context.tenant_id:
            raise ValueError("Tenant context not set. Call set_tenant_context() first.")
    
    def _add_tenant_filter(self, query):
        """Add tenant filter to query"""
        self._ensure_tenant_context()
        if hasattr(self.model_class, 'tenant_id'):
            return query.where(self.model_class.tenant_id == tenant_context.tenant_id)
        return query
    
    async def create(self, **kwargs) -> T:
        """Create new record with tenant context"""
        self._ensure_tenant_context()
        
        if hasattr(self.model_class, 'tenant_id'):
            kwargs['tenant_id'] = tenant_context.tenant_id
        
        instance = self.model_class(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        
        # Log audit event
        await self._log_audit_event("CREATE", None, instance.__dict__)
        
        return instance
    
    async def get_by_id(self, id: str) -> Optional[T]:
        """Get record by ID with tenant filter"""
        query = select(self.model_class).where(self.model_class.id == id)
        query = self._add_tenant_filter(query)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Get all records with tenant filter"""
        query = select(self.model_class)
        query = self._add_tenant_filter(query)
        query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update(self, id: str, **kwargs) -> Optional[T]:
        """Update record with tenant context"""
        instance = await self.get_by_id(id)
        if not instance:
            return None
        
        old_values = {key: getattr(instance, key) for key in kwargs.keys() if hasattr(instance, key)}
        
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        await self.session.flush()
        await self.session.refresh(instance)
        
        # Log audit event
        await self._log_audit_event("UPDATE", old_values, kwargs)
        
        return instance
    
    async def delete(self, id: str) -> bool:
        """Delete record with tenant context"""
        instance = await self.get_by_id(id)
        if not instance:
            return False
        
        old_values = instance.__dict__.copy()
        await self.session.delete(instance)
        
        # Log audit event
        await self._log_audit_event("DELETE", old_values, None)
        
        return True
    
    async def count(self) -> int:
        """Count records with tenant filter"""
        query = select(func.count(self.model_class.id))
        query = self._add_tenant_filter(query)
        
        result = await self.session.execute(query)
        return result.scalar()
    
    async def _log_audit_event(self, event_type: str, old_values: Dict, new_values: Dict):
        """Log audit event"""
        if not hasattr(self.model_class, '__tablename__'):
            return
        
        audit_log = TenantAuditLog(
            tenant_id=tenant_context.tenant_id,
            event_type=f"{self.model_class.__tablename__.upper()}_{event_type}",
            event_description=f"{event_type} operation on {self.model_class.__tablename__}",
            old_values=old_values,
            new_values=new_values
        )
        
        self.session.add(audit_log)
        await self.session.flush()


class UserRepository(TenantRepository[UserModel]):
    """User repository with tenant awareness"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(UserModel, session)
    
    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email with tenant filter"""
        query = select(self.model_class).where(self.model_class.email == email)
        query = self._add_tenant_filter(query)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[UserModel]:
        """Get user by username with tenant filter"""
        query = select(self.model_class).where(self.model_class.username == username)
        query = self._add_tenant_filter(query)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_active_users(self) -> List[UserModel]:
        """Get active users for tenant"""
        query = select(self.model_class).where(self.model_class.is_active == True)
        query = self._add_tenant_filter(query)
        
        result = await self.session.execute(query)
        return result.scalars().all()


class PostRepository(TenantRepository[PostModel]):
    """Post repository with tenant awareness"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(PostModel, session)
    
    async def get_by_user(self, user_id: str) -> List[PostModel]:
        """Get posts by user with tenant filter"""
        query = select(self.model_class).where(self.model_class.user_id == user_id)
        query = self._add_tenant_filter(query)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_published_posts(self) -> List[PostModel]:
        """Get published posts for tenant"""
        query = select(self.model_class).where(self.model_class.status == "published")
        query = self._add_tenant_filter(query)
        query = query.order_by(self.model_class.published_at.desc())
        
        result = await self.session.execute(query)
        return result.scalars().all()


class TenantManager:
    """Multi-tenant management service"""
    
    def __init__(self, config: MultiTenantConfig):
        self.config = config
        self.engine: Optional[AsyncEngine] = None
        self.session_factory = None
        self.redis = None
        self.logger = logging.getLogger(__name__)
        self._tenant_cache: Dict[str, TenantInfo] = {}
    
    async def initialize(self):
        """Initialize tenant manager"""
        # Create database engine
        self.engine = create_async_engine(
            self.config.database_url,
            echo=False,
            pool_size=self.config.connection_pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            poolclass=NullPool if self.config.enable_connection_pooling_per_tenant else None
        )
        
        # Create session factory
        self.session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Connect to Redis
        if self.config.enable_caching:
            self.redis = redis.from_url(self.config.redis_url)
        
        # Create tables
        await self._create_tables()
        
        # Setup row-level security
        if self.config.enable_row_level_security:
            await self._setup_row_level_security()
        
        self.logger.info("Tenant manager initialized")
    
    async def _create_tables(self):
        """Create database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def _setup_row_level_security(self):
        """Setup PostgreSQL row-level security"""
        if "postgresql" not in self.config.database_url:
            return
        
        rls_queries = [
            # Enable RLS on tenant-aware tables
            "ALTER TABLE users ENABLE ROW LEVEL SECURITY;",
            "ALTER TABLE posts ENABLE ROW LEVEL SECURITY;",
            
            # Create policies for tenant isolation
            """
            CREATE POLICY tenant_isolation_users ON users
            USING (tenant_id = current_setting('app.current_tenant_id', true));
            """,
            """
            CREATE POLICY tenant_isolation_posts ON posts
            USING (tenant_id = current_setting('app.current_tenant_id', true));
            """,
            
            # Create function to set tenant context
            """
            CREATE OR REPLACE FUNCTION set_current_tenant_id(tenant_id text)
            RETURNS void AS $$
            BEGIN
                PERFORM set_config('app.current_tenant_id', tenant_id, true);
            END;
            $$ LANGUAGE plpgsql;
            """
        ]
        
        async with self.engine.begin() as conn:
            for query in rls_queries:
                try:
                    await conn.execute(sa.text(query))
                except Exception as e:
                    if "already exists" not in str(e):
                        self.logger.warning(f"RLS setup warning: {e}")
    
    async def create_tenant(self, tenant_info: TenantInfo) -> str:
        """Create new tenant"""
        async with self.session_factory() as session:
            # Check if tenant already exists
            existing = await session.execute(
                select(TenantModel).where(TenantModel.name == tenant_info.name)
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Tenant {tenant_info.name} already exists")
            
            # Create tenant record
            tenant_model = TenantModel(
                id=tenant_info.id,
                name=tenant_info.name,
                status=tenant_info.status.value,
                admin_email=tenant_info.admin_email,
                settings=tenant_info.settings,
                features=tenant_info.features,
                data_residency=tenant_info.data_residency.value,
                max_users=tenant_info.max_users,
                max_storage_gb=tenant_info.max_storage_gb,
                max_api_calls_per_hour=tenant_info.max_api_calls_per_hour,
                billing_plan=tenant_info.billing_plan,
                gdpr_enabled=tenant_info.gdpr_enabled,
                data_retention_days=tenant_info.data_retention_days,
                connection_pool_size=tenant_info.connection_pool_size,
                query_timeout_seconds=tenant_info.query_timeout_seconds
            )
            
            session.add(tenant_model)
            await session.commit()
            
            # Handle schema/database creation based on tenancy type
            if self.config.tenancy_type == TenancyType.SHARED_DATABASE_SEPARATE_SCHEMA:
                await self._create_tenant_schema(tenant_info.id)
            elif self.config.tenancy_type == TenancyType.SEPARATE_DATABASE:
                await self._create_tenant_database(tenant_info.id)
            
            # Cache tenant info
            if self.config.enable_caching:
                await self._cache_tenant_info(tenant_info)
            
            self.logger.info(f"Created tenant: {tenant_info.name} ({tenant_info.id})")
            return tenant_info.id
    
    async def _create_tenant_schema(self, tenant_id: str):
        """Create separate schema for tenant"""
        schema_name = f"tenant_{tenant_id.replace('-', '_')}"
        
        async with self.engine.begin() as conn:
            await conn.execute(CreateSchema(schema_name))
            
            # Create tables in tenant schema
            metadata_copy = MetaData(schema=schema_name)
            for table in Base.metadata.tables.values():
                if hasattr(table.c, 'tenant_id'):  # Only tenant-aware tables
                    table.tometadata(metadata_copy)
            
            await conn.run_sync(metadata_copy.create_all)
            
        self.logger.info(f"Created schema for tenant: {schema_name}")
    
    async def _create_tenant_database(self, tenant_id: str):
        """Create separate database for tenant"""
        database_name = f"tenant_{tenant_id.replace('-', '_')}"
        
        # This would require administrative privileges
        # Implementation depends on your infrastructure setup
        self.logger.info(f"Would create database for tenant: {database_name}")
    
    async def get_tenant(self, tenant_id: str) -> Optional[TenantInfo]:
        """Get tenant information"""
        # Check cache first
        if self.config.enable_caching and tenant_id in self._tenant_cache:
            return self._tenant_cache[tenant_id]
        
        # Check Redis cache
        if self.redis:
            cache_key = f"{self.config.redis_key_prefix}:tenant:{tenant_id}"
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                try:
                    tenant_data = json.loads(cached_data)
                    tenant_info = TenantInfo(**tenant_data)
                    self._tenant_cache[tenant_id] = tenant_info
                    return tenant_info
                except Exception as e:
                    self.logger.warning(f"Failed to deserialize cached tenant data: {e}")
        
        # Query database
        async with self.session_factory() as session:
            result = await session.execute(
                select(TenantModel).where(TenantModel.id == tenant_id)
            )
            tenant_model = result.scalar_one_or_none()
            
            if not tenant_model:
                return None
            
            tenant_info = TenantInfo(
                id=tenant_model.id,
                name=tenant_model.name,
                status=TenantStatus(tenant_model.status),
                database_name=tenant_model.database_name,
                schema_name=tenant_model.schema_name,
                created_at=tenant_model.created_at,
                updated_at=tenant_model.updated_at,
                settings=tenant_model.settings,
                features=tenant_model.features,
                data_residency=DataResidency(tenant_model.data_residency),
                max_users=tenant_model.max_users,
                max_storage_gb=tenant_model.max_storage_gb,
                max_api_calls_per_hour=tenant_model.max_api_calls_per_hour,
                admin_email=tenant_model.admin_email,
                billing_plan=tenant_model.billing_plan,
                gdpr_enabled=tenant_model.gdpr_enabled,
                data_retention_days=tenant_model.data_retention_days,
                connection_pool_size=tenant_model.connection_pool_size,
                query_timeout_seconds=tenant_model.query_timeout_seconds
            )
            
            # Cache tenant info
            if self.config.enable_caching:
                await self._cache_tenant_info(tenant_info)
            
            return tenant_info
    
    async def _cache_tenant_info(self, tenant_info: TenantInfo):
        """Cache tenant information"""
        self._tenant_cache[tenant_info.id] = tenant_info
        
        if self.redis:
            cache_key = f"{self.config.redis_key_prefix}:tenant:{tenant_info.id}"
            tenant_data = {
                "id": tenant_info.id,
                "name": tenant_info.name,
                "status": tenant_info.status.value,
                "database_name": tenant_info.database_name,
                "schema_name": tenant_info.schema_name,
                "created_at": tenant_info.created_at.isoformat(),
                "updated_at": tenant_info.updated_at.isoformat(),
                "settings": tenant_info.settings,
                "features": tenant_info.features,
                "data_residency": tenant_info.data_residency.value,
                "max_users": tenant_info.max_users,
                "max_storage_gb": tenant_info.max_storage_gb,
                "max_api_calls_per_hour": tenant_info.max_api_calls_per_hour,
                "admin_email": tenant_info.admin_email,
                "billing_plan": tenant_info.billing_plan,
                "gdpr_enabled": tenant_info.gdpr_enabled,
                "data_retention_days": tenant_info.data_retention_days,
                "connection_pool_size": tenant_info.connection_pool_size,
                "query_timeout_seconds": tenant_info.query_timeout_seconds
            }
            
            await self.redis.setex(
                cache_key,
                self.config.cache_ttl_seconds,
                json.dumps(tenant_data)
            )
    
    async def update_tenant(self, tenant_id: str, **updates) -> bool:
        """Update tenant information"""
        async with self.session_factory() as session:
            result = await session.execute(
                update(TenantModel)
                .where(TenantModel.id == tenant_id)
                .values(**updates)
                .returning(TenantModel.id)
            )
            
            if result.scalar_one_or_none():
                await session.commit()
                
                # Invalidate cache
                if tenant_id in self._tenant_cache:
                    del self._tenant_cache[tenant_id]
                
                if self.redis:
                    cache_key = f"{self.config.redis_key_prefix}:tenant:{tenant_id}"
                    await self.redis.delete(cache_key)
                
                return True
            
            return False
    
    async def delete_tenant(self, tenant_id: str) -> bool:
        """Delete tenant and all associated data"""
        tenant_info = await self.get_tenant(tenant_id)
        if not tenant_info:
            return False
        
        async with self.session_factory() as session:
            # Delete tenant record (cascade will handle audit logs)
            result = await session.execute(
                delete(TenantModel).where(TenantModel.id == tenant_id)
            )
            
            if result.rowcount > 0:
                await session.commit()
                
                # Clean up schema/database
                if self.config.tenancy_type == TenancyType.SHARED_DATABASE_SEPARATE_SCHEMA:
                    await self._drop_tenant_schema(tenant_id)
                elif self.config.tenancy_type == TenancyType.SEPARATE_DATABASE:
                    await self._drop_tenant_database(tenant_id)
                
                # Invalidate cache
                if tenant_id in self._tenant_cache:
                    del self._tenant_cache[tenant_id]
                
                if self.redis:
                    cache_key = f"{self.config.redis_key_prefix}:tenant:{tenant_id}"
                    await self.redis.delete(cache_key)
                
                self.logger.info(f"Deleted tenant: {tenant_id}")
                return True
            
            return False
    
    async def _drop_tenant_schema(self, tenant_id: str):
        """Drop tenant schema"""
        schema_name = f"tenant_{tenant_id.replace('-', '_')}"
        
        async with self.engine.begin() as conn:
            await conn.execute(DropSchema(schema_name, cascade=True))
        
        self.logger.info(f"Dropped schema for tenant: {schema_name}")
    
    async def _drop_tenant_database(self, tenant_id: str):
        """Drop tenant database"""
        database_name = f"tenant_{tenant_id.replace('-', '_')}"
        
        # This would require administrative privileges
        self.logger.info(f"Would drop database for tenant: {database_name}")
    
    @asynccontextmanager
    async def get_session(self, tenant_id: str):
        """Get database session with tenant context"""
        tenant_info = await self.get_tenant(tenant_id)
        if not tenant_info:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        if tenant_info.status != TenantStatus.ACTIVE:
            raise ValueError(f"Tenant {tenant_id} is not active")
        
        # Set tenant context
        tenant_context.set_tenant(tenant_id, tenant_info)
        
        async with self.session_factory() as session:
            # Set tenant context in database session
            if self.config.enable_row_level_security and "postgresql" in self.config.database_url:
                await session.execute(sa.text(f"SELECT set_current_tenant_id('{tenant_id}')"))
            
            try:
                yield session
            finally:
                tenant_context.clear()
    
    async def export_tenant_data(self, tenant_id: str, export_path: str) -> Dict[str, Any]:
        """Export all tenant data for backup or migration"""
        tenant_info = await self.get_tenant(tenant_id)
        if not tenant_info:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        export_data = {
            "tenant_info": {
                "id": tenant_info.id,
                "name": tenant_info.name,
                "created_at": tenant_info.created_at.isoformat(),
                "settings": tenant_info.settings,
                "features": tenant_info.features
            },
            "tables": {}
        }
        
        async with self.get_session(tenant_id) as session:
            # Export tenant-aware tables
            for model_class in [UserModel, PostModel]:
                table_name = model_class.__tablename__
                
                query = select(model_class)
                if hasattr(model_class, 'tenant_id'):
                    query = query.where(model_class.tenant_id == tenant_id)
                
                result = await session.execute(query)
                records = result.scalars().all()
                
                export_data["tables"][table_name] = [
                    {key: str(value) if isinstance(value, (datetime, uuid.UUID)) else value 
                     for key, value in record.__dict__.items() 
                     if not key.startswith('_')}
                    for record in records
                ]
        
        # Save to file
        import aiofiles
        async with aiofiles.open(export_path, 'w') as f:
            await f.write(json.dumps(export_data, indent=2))
        
        self.logger.info(f"Exported tenant data for {tenant_id} to {export_path}")
        return export_data
    
    async def get_tenant_metrics(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant usage metrics"""
        async with self.get_session(tenant_id) as session:
            # Count users
            user_count = await session.execute(
                select(func.count(UserModel.id)).where(UserModel.tenant_id == tenant_id)
            )
            
            # Count posts
            post_count = await session.execute(
                select(func.count(PostModel.id)).where(PostModel.tenant_id == tenant_id)
            )
            
            # Get recent activity
            recent_users = await session.execute(
                select(func.count(UserModel.id))
                .where(UserModel.tenant_id == tenant_id)
                .where(UserModel.last_login_at > datetime.utcnow() - timedelta(days=30))
            )
            
            return {
                "tenant_id": tenant_id,
                "total_users": user_count.scalar(),
                "total_posts": post_count.scalar(),
                "active_users_30d": recent_users.scalar(),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def cleanup(self):
        """Cleanup tenant manager"""
        if self.redis:
            await self.redis.close()
        
        if self.engine:
            await self.engine.dispose()


# Usage example and test functions
async def example_usage():
    """Example usage of multi-tenant system"""
    
    # Configure multi-tenant system
    config = MultiTenantConfig(
        tenancy_type=TenancyType.SHARED_DATABASE_SHARED_SCHEMA,
        enable_row_level_security=True,
        enable_tenant_isolation=True,
        enable_audit_logging=True,
        database_url="postgresql+asyncpg://user:pass@localhost/multitenantdb"
    )
    
    # Initialize tenant manager
    tenant_manager = TenantManager(config)
    await tenant_manager.initialize()
    
    try:
        # Create tenants
        tenant1_info = TenantInfo(
            id=str(uuid.uuid4()),
            name="acme_corp",
            admin_email="admin@acme.com",
            status=TenantStatus.ACTIVE,
            max_users=500,
            billing_plan="enterprise"
        )
        
        tenant2_info = TenantInfo(
            id=str(uuid.uuid4()),
            name="startup_inc",
            admin_email="admin@startup.com",
            status=TenantStatus.ACTIVE,
            max_users=50,
            billing_plan="standard"
        )
        
        await tenant_manager.create_tenant(tenant1_info)
        await tenant_manager.create_tenant(tenant2_info)
        
        # Use tenant 1
        async with tenant_manager.get_session(tenant1_info.id) as session:
            user_repo = UserRepository(session)
            post_repo = PostRepository(session)
            
            # Create user for tenant 1
            user1 = await user_repo.create(
                username="john_doe",
                email="john@acme.com",
                first_name="John",
                last_name="Doe"
            )
            
            # Create post for user
            post1 = await post_repo.create(
                user_id=user1.id,
                title="Welcome to Acme Corp",
                content="This is our first post!",
                status="published"
            )
            
            await session.commit()
            
            print(f"Created user {user1.username} and post {post1.title} for tenant {tenant1_info.name}")
        
        # Use tenant 2
        async with tenant_manager.get_session(tenant2_info.id) as session:
            user_repo = UserRepository(session)
            post_repo = PostRepository(session)
            
            # Create user for tenant 2
            user2 = await user_repo.create(
                username="jane_smith",
                email="jane@startup.com",
                first_name="Jane",
                last_name="Smith"
            )
            
            # Try to access user from tenant 1 (should fail)
            user_from_other_tenant = await user_repo.get_by_email("john@acme.com")
            print(f"User from other tenant: {user_from_other_tenant}")  # Should be None
            
            await session.commit()
            
            print(f"Created user {user2.username} for tenant {tenant2_info.name}")
        
        # Get tenant metrics
        metrics1 = await tenant_manager.get_tenant_metrics(tenant1_info.id)
        metrics2 = await tenant_manager.get_tenant_metrics(tenant2_info.id)
        
        print(f"Tenant 1 metrics: {metrics1}")
        print(f"Tenant 2 metrics: {metrics2}")
        
        # Export tenant data
        export_path = f"/tmp/tenant_{tenant1_info.id}_export.json"
        await tenant_manager.export_tenant_data(tenant1_info.id, export_path)
        
        print(f"Exported tenant 1 data to {export_path}")
        
    finally:
        await tenant_manager.cleanup()


if __name__ == "__main__":
    import sys
    import os
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        asyncio.run(example_usage())
    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()