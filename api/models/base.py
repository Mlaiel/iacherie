"""IA Influencer Agent Platform - Base Models and Mixins
Foundation classes for all data models with enterprise-grade features

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
              Microservices Architect + Audio Engineer + DevOps + IA Prompt Engineer

WARNING: This code and concept are protected by copyright law and intellectual property rights.
Any unauthorized use, reproduction, copying, distribution, or commercial exploitation 
without explicit written permission from Fahed Mlaiel is strictly prohibited and 
will result in legal action.

Contact: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    Column, String, DateTime, Boolean, Text, JSON, Integer,
    BigInteger, Numeric, Index, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func


Base = declarative_base()


class BaseModel(Base):
    """
Base model class with common functionality for all models"""
    
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + 's'
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert model instance to dictionary"""
        return {
            column.name: getattr(self, column.name) 
            for column in self.__table__.columns
        }
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """
Update model instance from dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', None)})>"


class UUIDMixin:
    """Mixin for UUID primary key"""
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )


class TimestampMixin:
    """
Mixin for automatic timestamp tracking"""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True
    )


class SoftDeleteMixin:
    """
Mixin for soft delete functionality"""
    
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    def soft_delete(self) -> None:
        """
Mark record as deleted"""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
    
    def restore(self) -> None:
        """
Restore soft deleted record"""
        self.is_deleted = False
        self.deleted_at = None


class AuditMixin:
    """
Mixin for audit trail functionality"""
    
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True
    )
    
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True
    )
    
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )
    
    audit_trail: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    def increment_version(self) -> None:
        """
Increment version number for optimistic locking"""
        self.version += 1


class MetadataMixin:
    """
Mixin for storing flexible metadata"""
    
    metadata_: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        'metadata',
        JSONB,
        default=dict,
        nullable=True
    )
    
    tags: Mapped[Optional[List[str]]] = mapped_column(
        JSONB,
        default=list,
        nullable=True
    )


class GeoLocationMixin:
    """
Mixin for geographic location data"""
    
    latitude: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 8),
        nullable=True
    )
    
    longitude: Mapped[Optional[float]] = mapped_column(
        Numeric(11, 8),
        nullable=True
    )
    
    location_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        index=True
    )
    
    country_code: Mapped[Optional[str]] = mapped_column(
        String(2),
        nullable=True,
        index=True
    )


class StatusMixin:
    """
Mixin for status tracking"""
    
    status: Mapped[str] = mapped_column(
        String(50),
        default='active',
        nullable=False,
        index=True
    )
    
    status_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    status_changed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    def update_status(self, new_status: str, reason: Optional[str] = None) -> None:
        """
Update status with timestamp and reason"""
        self.status = new_status
        self.status_reason = reason
        self.status_changed_at = datetime.now(timezone.utc)


class PerformanceMetricsMixin:
    """
Mixin for performance tracking"""
    
    view_count: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
        index=True
    )
    
    like_count: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
        index=True
    )
    
    share_count: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
        index=True
    )
    
    comment_count: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
        index=True
    )
    
    engagement_rate: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4),
        nullable=True,
        index=True
    )
    
    def calculate_engagement_rate(self) -> float:
        """
Calculate engagement rate based on interactions"""
        total_interactions = self.like_count + self.share_count + self.comment_count
        if self.view_count > 0:
            return round(total_interactions / self.view_count, 4)
        return 0.0
