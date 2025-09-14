"""🌐 Distribution Platforms Database Module - Multi-Platform Content Distribution System
============================================================================================
Module: backend/database/distribution_platforms.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Consolidated Distribution Platforms Database - Ultra Enterprise Production-Ready
Responsibility: 35+ platform integrations, automated distribution, cross-platform sync, and analytics
====================================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from datetime import datetime, timezone
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)
Base = declarative_base()

class PlatformType(Enum):
    """PlatformType class implementation"""
    STREAMING_MUSIC = "streaming_music"
    STREAMING_VIDEO = "streaming_video"
    SOCIAL_MEDIA = "social_media"
    PODCAST = "podcast"
    MARKETPLACE = "marketplace"

class DistributionStatus(Enum):
    """DistributionStatus class implementation"""
    PENDING = "pending"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"

class PlatformIntegration(Base):
    """35+ platform integrations and configurations."""
    __tablename__ = 'platform_integrations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_name = Column(String(100), nullable=False, unique=True)
    platform_type = Column(SQLEnum(PlatformType), nullable=False)
    api_endpoint = Column(String(500), nullable=True)
    api_version = Column(String(20), nullable=True)
    authentication_config = Column(JSONB, default={})
    platform_limits = Column(JSONB, default={})
    supported_formats = Column(ARRAY(String), default=[])
    integration_status = Column(String(50), default='active')
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class ContentDistribution(Base):
    """Automated content distribution tracking."""
    __tablename__ = 'content_distributions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(String(255), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform_integration_id = Column(UUID(as_uuid=True), ForeignKey('platform_integrations.id'), nullable=False)
    distribution_status = Column(SQLEnum(DistributionStatus), default=DistributionStatus.PENDING)
    platform_content_id = Column(String(255), nullable=True)
    platform_url = Column(String(500), nullable=True)
    distribution_config = Column(JSONB, default={})
    error_details = Column(JSONB, default={})
    performance_metrics = Column(JSONB, default={})
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    distributed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class CrossPlatformSync(Base):
    """Cross-platform synchronization management."""
    __tablename__ = 'cross_platform_sync'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(String(255), nullable=False, index=True)
    sync_group_id = Column(UUID(as_uuid=True), nullable=False)
    sync_status = Column(String(50), default='pending')
    sync_conflicts = Column(JSONB, default=[])
    resolution_strategy = Column(String(100), nullable=True)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    next_sync_scheduled = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class DistributionAnalytics(Base):
    """Distribution performance analytics."""
    __tablename__ = 'distribution_analytics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_distribution_id = Column(UUID(as_uuid=True), ForeignKey('content_distributions.id'), nullable=False)
    total_reach = Column(BigInteger, default=0)
    engagement_rate = Column(Float, nullable=True)
    conversion_rate = Column(Float, nullable=True)
    revenue_generated = Column(Numeric(12, 2), default=0)
    performance_breakdown = Column(JSONB, default={})
    audience_demographics = Column(JSONB, default={})
    geographic_distribution = Column(JSONB, default={})
    recorded_at = Column(DateTime(timezone=True), default=datetime.utcnow)

def get_distribution_platforms_models() -> None:
    return [PlatformIntegration, ContentDistribution, CrossPlatformSync, DistributionAnalytics]

def create_distribution_platforms_tables(engine) -> None:
    try:
        Base.metadata.create_all(engine, tables=[model.__table__ for model in get_distribution_platforms_models()])
        logger.info("Successfully created distribution platforms tables")
        return True
    except Exception as e:
        logger.error(f"Failed to create distribution platforms tables: {str(e)}")
        return False

__all__ = ['PlatformType', 'DistributionStatus', 'PlatformIntegration', 'ContentDistribution', 'CrossPlatformSync', 'DistributionAnalytics', 'get_distribution_platforms_models', 'create_distribution_platforms_tables']