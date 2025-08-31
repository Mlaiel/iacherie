"""📊 Monitoring Models and Database Schemas
========================================

Comprehensive database models and schemas for content protection monitoring system.
Includes all entities, relationships, and data structures for monitoring operations.

Technical Specifications:
- SQLAlchemy ORM models with optimized indexing
- Comprehensive data validation and constraints
- Audit trail and versioning support
- Performance-optimized queries and relationships
- Multi-tenant data isolation

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited

⚖️ LEGAL WARNING: This software is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or reverse engineering is strictly prohibited
and will result in immediate legal action under German and international copyright law.
Contact mlaiel@live.de for licensing inquiries.
"""
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, 
    JSON, ForeignKey, Index, UniqueConstraint, CheckConstraint,
    BigInteger, DECIMAL, LargeBinary, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, validator
import uuid

Base = declarative_base()

# Enums for database
class MonitoringStatusEnum(PyEnum):
    ACTIVE = "active"
    PAUSED = "paused" 
    STOPPED = "stopped"
    ERROR = "error"

class PlatformTypeEnum(PyEnum):
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    GENERIC_WEB = "generic_web"

class ThreatLevelEnum(PyEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NOISE = "noise"

class ViolationStatusEnum(PyEnum):
    PENDING = "pending"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

class MonitoringPriorityEnum(PyEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# Core Monitoring Models

class MonitoringSession(Base):
    """Real-time monitoring session tracking."""    __tablename__ = "monitoring_sessions"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    fingerprint_id = Column(String(50), ForeignKey("content_fingerprints.id"), nullable=False, index=True)
    
    # Session configuration
    session_name = Column(String(255))
    priority = Column(Enum(MonitoringPriorityEnum), default=MonitoringPriorityEnum.MEDIUM)
    platforms = Column(ARRAY(String), nullable=False)
    search_keywords = Column(ARRAY(String), default=[])
    
    # Status and timing
    status = Column(Enum(MonitoringStatusEnum), default=MonitoringStatusEnum.ACTIVE, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    started_at = Column(DateTime)
    stopped_at = Column(DateTime)
    last_scan_at = Column(DateTime)
    next_scan_at = Column(DateTime)
    
    # Configuration
    scan_interval_seconds = Column(Integer, default=300)  # 5 minutes
    max_violations_per_scan = Column(Integer, default=100)
    custom_config = Column(JSONB, default={})
    
    # Statistics
    total_scans = Column(BigInteger, default=0)
    violations_detected = Column(BigInteger, default=0)
    false_positives = Column(BigInteger, default=0)
    
    # Relationships
    violations = relationship("ViolationDetection", back_populates="monitoring_session")
    alerts = relationship("MonitoringAlert", back_populates="monitoring_session")
    
    # Indexes
    __table_args__ = (
        Index('ix_monitoring_sessions_user_status', 'user_id', 'status'),
        Index('ix_monitoring_sessions_fingerprint_active', 'fingerprint_id', 'status'),
        Index('ix_monitoring_sessions_next_scan', 'next_scan_at'),
    )

class ViolationDetection(Base):
    """Content violation detection records."""    __tablename__ = "violation_detections"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    monitoring_session_id = Column(String(50), ForeignKey("monitoring_sessions.id"), nullable=False, index=True)
    fingerprint_id = Column(String(50), ForeignKey("content_fingerprints.id"), nullable=False, index=True)
    
    # Platform and detection details
    platform = Column(Enum(PlatformTypeEnum), nullable=False, index=True)
    detected_url = Column(Text, nullable=False)
    content_title = Column(String(500))
    content_description = Column(Text)
    
    # Similarity and confidence scores
    similarity_score = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    threat_level = Column(Enum(ThreatLevelEnum), nullable=False, index=True)
    
    # Detection metadata
    detection_method = Column(String(100))  # audio_fingerprint, video_hash, etc.
    match_segments = Column(JSONB)  # Specific segments that matched
    evidence_data = Column(JSONB, default={})
    
    # Status and resolution
    status = Column(Enum(ViolationStatusEnum), default=ViolationStatusEnum.PENDING, index=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Timestamps
    detected_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    first_seen_at = Column(DateTime, default=func.now())
    last_seen_at = Column(DateTime, default=func.now())
    resolved_at = Column(DateTime)
    
    # Content metadata from platform
    platform_content_id = Column(String(255))
    uploader_info = Column(JSONB, default={})
    view_count = Column(BigInteger)
    like_count = Column(BigInteger)
    duration_seconds = Column(Integer)
    
    # Relationships
    monitoring_session = relationship("MonitoringSession", back_populates="violations")
    enforcement_actions = relationship("EnforcementAction", back_populates="violation")
    
    # Constraints and indexes
    __table_args__ = (
        Index('ix_violations_platform_detected', 'platform', 'detected_at'),
        Index('ix_violations_threat_status', 'threat_level', 'status'),
        Index('ix_violations_similarity', 'similarity_score'),
        Index('ix_violations_url_hash', func.md5('detected_url')),
        CheckConstraint('similarity_score >= 0 AND similarity_score <= 1', name='check_similarity_range'),
        CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='check_confidence_range'),
    )

class MonitoringAlert(Base):
    """Monitoring system alerts and notifications."""    __tablename__ = "monitoring_alerts"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    monitoring_session_id = Column(String(50), ForeignKey("monitoring_sessions.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Alert details
    alert_type = Column(String(100), nullable=False)  # violation_detected, system_error, etc.
    severity = Column(Enum(ThreatLevelEnum), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Alert data and context
    alert_data = Column(JSONB, default={})
    context = Column(JSONB, default={})
    
    # Status and delivery
    is_read = Column(Boolean, default=False, index=True)
    is_delivered = Column(Boolean, default=False)
    delivery_channels = Column(ARRAY(String), default=[])  # email, sms, webhook, etc.
    delivery_attempts = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Relationships
    monitoring_session = relationship("MonitoringSession", back_populates="alerts")
    
    # Indexes
    __table_args__ = (
        Index('ix_alerts_user_unread', 'user_id', 'is_read'),
        Index('ix_alerts_severity_created', 'severity', 'created_at'),
        Index('ix_alerts_type_created', 'alert_type', 'created_at'),
    )

class PlatformMonitoringConfig(Base):
    """Platform-specific monitoring configuration."""    __tablename__ = "platform_monitoring_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    platform = Column(Enum(PlatformTypeEnum), nullable=False, index=True)
    
    # Configuration
    enabled = Column(Boolean, default=True)
    scan_interval_seconds = Column(Integer, default=300)
    max_concurrent_scans = Column(Integer, default=10)
    api_rate_limit = Column(Integer, default=1000)  # requests per hour
    
    # Thresholds
    similarity_threshold = Column(Float, default=0.8)
    confidence_threshold = Column(Float, default=0.75)
    auto_enforcement = Column(Boolean, default=False)
    
    # API configuration
    api_credentials = Column(JSONB, default={})  # Encrypted
    webhook_url = Column(String(500))
    custom_headers = Column(JSONB, default={})
    
    # Performance tracking
    last_scan_at = Column(DateTime)
    total_scans = Column(BigInteger, default=0)
    successful_scans = Column(BigInteger, default=0)
    failed_scans = Column(BigInteger, default=0)
    average_response_time_ms = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'platform', name='uq_user_platform_config'),
        Index('ix_platform_configs_enabled', 'platform', 'enabled'),
    )

class MonitoringMetrics(Base):
    """Time-series monitoring metrics data."""    __tablename__ = "monitoring_metrics"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(50), ForeignKey("monitoring_sessions.id"), index=True)
    
    # Metric identification
    metric_type = Column(String(100), nullable=False, index=True)
    platform = Column(Enum(PlatformTypeEnum), index=True)
    
    # Metric values
    value = Column(Float, nullable=False)
    count = Column(BigInteger, default=1)
    
    # Additional data
    tags = Column(JSONB, default={})
    metadata = Column(JSONB, default={})
    
    # Timestamp
    recorded_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Time-series partitioning and indexing
    __table_args__ = (
        Index('ix_metrics_type_time', 'metric_type', 'recorded_at'),
        Index('ix_metrics_session_time', 'session_id', 'recorded_at'),
        Index('ix_metrics_platform_time', 'platform', 'recorded_at'),
    )

class SystemPerformanceMetrics(Base):
    """System performance and health metrics."""    __tablename__ = "system_performance_metrics"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Resource metrics
    cpu_usage_percent = Column(Float)
    memory_usage_percent = Column(Float)
    disk_usage_percent = Column(Float)
    network_io_mbps = Column(Float)
    
    # Application metrics
    active_monitoring_sessions = Column(Integer, default=0)
    queue_depth = Column(Integer, default=0)
    active_connections = Column(Integer, default=0)
    response_time_ms = Column(Float)
    
    # Throughput metrics
    scans_per_minute = Column(Float, default=0.0)
    violations_per_minute = Column(Float, default=0.0)
    alerts_per_minute = Column(Float, default=0.0)
    
    # Error rates
    error_rate_percent = Column(Float, default=0.0)
    false_positive_rate_percent = Column(Float, default=0.0)
    
    # Timestamp
    recorded_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Indexes for time-series queries
    __table_args__ = (
        Index('ix_system_metrics_time', 'recorded_at'),
    )

class EnforcementAction(Base):
    """Enforcement actions taken against violations."""    __tablename__ = "enforcement_actions"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    violation_id = Column(String(50), ForeignKey("violation_detections.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Action details
    action_type = Column(String(100), nullable=False)  # dmca_takedown, copyright_claim, etc.
    platform = Column(Enum(PlatformTypeEnum), nullable=False)
    
    # Status tracking
    status = Column(String(50), default="pending", index=True)
    external_id = Column(String(255))  # Platform's tracking ID
    
    # Action data
    request_data = Column(JSONB, default={})
    response_data = Column(JSONB, default={})
    evidence_files = Column(ARRAY(String), default=[])
    
    # Timestamps
    initiated_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Success tracking
    is_successful = Column(Boolean, index=True)
    failure_reason = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Relationships
    violation = relationship("ViolationDetection", back_populates="enforcement_actions")
    
    # Indexes
    __table_args__ = (
        Index('ix_enforcement_platform_status', 'platform', 'status'),
        Index('ix_enforcement_initiated', 'initiated_at'),
    )

# Analytics and Reporting Models

class AnalyticsReport(Base):
    """Generated analytics reports."""    __tablename__ = "analytics_reports"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Report metadata
    report_name = Column(String(255), nullable=False)
    report_type = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Time range
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # Report content
    report_data = Column(JSONB, nullable=False)
    summary_metrics = Column(JSONB, default={})
    insights = Column(ARRAY(String), default=[])
    recommendations = Column(ARRAY(String), default=[])
    
    # Generation info
    generated_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    generation_time_seconds = Column(Float)
    file_paths = Column(JSONB, default={})  # format -> file_path
    file_sizes = Column(JSONB, default={})  # format -> size_bytes
    
    # Status
    status = Column(String(50), default="completed")
    error_message = Column(Text)
    
    # Indexes
    __table_args__ = (
        Index('ix_reports_user_generated', 'user_id', 'generated_at'),
        Index('ix_reports_type_generated', 'report_type', 'generated_at'),
    )

class DashboardLayout(Base):
    """User dashboard layout configurations."""    __tablename__ = "dashboard_layouts"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Layout metadata
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    
    # Layout configuration
    widgets = Column(JSONB, nullable=False, default=[])
    layout_settings = Column(JSONB, default={})
    
    # Usage tracking
    usage_count = Column(BigInteger, default=0)
    last_used_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('ix_dashboard_user_default', 'user_id', 'is_default'),
        Index('ix_dashboard_public', 'is_public', 'created_at'),
    )

class PerformanceOptimizationLog(Base):
    """Performance optimization actions log."""    __tablename__ = "performance_optimization_log"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Optimization details
    optimization_type = Column(String(100), nullable=False)
    component = Column(String(100), nullable=False)
    action_taken = Column(String(100), nullable=False)
    
    # Before/after metrics
    metrics_before = Column(JSONB, default={})
    metrics_after = Column(JSONB, default={})
    improvement_percentage = Column(Float)
    
    # Configuration changes
    config_changes = Column(JSONB, default={})
    parameters = Column(JSONB, default={})
    
    # Status and results
    status = Column(String(50), default="completed")
    success = Column(Boolean, index=True)
    error_message = Column(Text)
    
    # Timestamps
    initiated_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    completed_at = Column(DateTime)
    
    # Indexes
    __table_args__ = (
        Index('ix_optimization_type_initiated', 'optimization_type', 'initiated_at'),
        Index('ix_optimization_success', 'success', 'initiated_at'),
    )

# Pydantic models for API

class MonitoringSessionCreate(BaseModel):
    """Create monitoring session request."""    fingerprint_id: str
    session_name: Optional[str] = None
    priority: MonitoringPriorityEnum = MonitoringPriorityEnum.MEDIUM
    platforms: List[str]
    search_keywords: List[str] = Field(default_factory=list)
    scan_interval_seconds: int = Field(300, ge=30, le=3600)
    custom_config: Dict[str, Any] = Field(default_factory=dict)

class MonitoringSessionUpdate(BaseModel):
    """Update monitoring session request."""    session_name: Optional[str] = None
    priority: Optional[MonitoringPriorityEnum] = None
    platforms: Optional[List[str]] = None
    search_keywords: Optional[List[str]] = None
    scan_interval_seconds: Optional[int] = Field(None, ge=30, le=3600)
    custom_config: Optional[Dict[str, Any]] = None

class ViolationDetectionResponse(BaseModel):
    """Violation detection response."""    id: str
    platform: str
    detected_url: str
    content_title: Optional[str] = None
    similarity_score: float
    confidence_score: float
    threat_level: str
    status: str
    detected_at: datetime
    evidence_data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True

class MonitoringMetricsResponse(BaseModel):
    """Monitoring metrics response."""    session_id: Optional[str] = None
    metric_type: str
    platform: Optional[str] = None
    value: float
    count: int = 1
    tags: Dict[str, Any] = Field(default_factory=dict)
    recorded_at: datetime

    class Config:
        from_attributes = True

class SystemHealthResponse(BaseModel):
    """System health metrics response."""    cpu_usage_percent: Optional[float] = None
    memory_usage_percent: Optional[float] = None
    disk_usage_percent: Optional[float] = None
    active_monitoring_sessions: int = 0
    queue_depth: int = 0
    response_time_ms: Optional[float] = None
    error_rate_percent: float = 0.0
    recorded_at: datetime

    class Config:
        from_attributes = True

class PlatformConfigUpdate(BaseModel):
    """Platform configuration update request."""    enabled: Optional[bool] = None
    scan_interval_seconds: Optional[int] = Field(None, ge=30, le=3600)
    similarity_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    auto_enforcement: Optional[bool] = None
    webhook_url: Optional[str] = None

# Database utility functions

def create_monitoring_indexes(engine):
    """Create additional database indexes for performance optimization."""    from sqlalchemy import text
    
    # Time-series partitioning indexes
    indexes = [
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_violations_detected_at_partial ON violation_detections (detected_at) WHERE status IN ('pending', 'investigating')",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_alerts_user_recent ON monitoring_alerts (user_id, created_at) WHERE created_at > NOW() - INTERVAL '7 days'",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_metrics_recent ON monitoring_metrics (metric_type, recorded_at) WHERE recorded_at > NOW() - INTERVAL '24 hours'",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_sessions_active ON monitoring_sessions (user_id, status, next_scan_at) WHERE status = 'active'",
    ]
    
    with engine.connect() as conn:
        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
                conn.commit()
            except Exception as e:
                print(f"Index creation failed: {e}")

def setup_monitoring_database(engine):
    """Set up monitoring database with all tables and indexes."""    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create performance indexes
    create_monitoring_indexes(engine)
    
    # Set up partitioning for time-series tables (PostgreSQL specific)
    setup_time_series_partitioning(engine)

def setup_time_series_partitioning(engine):
    """Set up time-series partitioning for high-volume tables."""    from sqlalchemy import text
    
    # This would set up monthly partitioning for metrics tables
    partitioning_sql = [
        """        -- Create monthly partitions for monitoring_metrics
        CREATE OR REPLACE FUNCTION create_monthly_partitions()
        RETURNS void AS $$
        DECLARE
            start_date date;
            end_date date;
            table_name text;
        BEGIN
            FOR i IN 0..12 LOOP
                start_date := date_trunc('month', CURRENT_DATE) + (i || ' months')::interval;
                end_date := start_date + interval '1 month';
                table_name := 'monitoring_metrics_' || to_char(start_date, 'YYYY_MM');
                
                EXECUTE 'CREATE TABLE IF NOT EXISTS ' || table_name || 
                        ' PARTITION OF monitoring_metrics FOR VALUES FROM (''' || 
                        start_date || ''') TO (''' || end_date || ''')';
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
        """,
        "SELECT create_monthly_partitions();",
    ]
    
    with engine.connect() as conn:
        for sql in partitioning_sql:
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception as e:
                print(f"Partitioning setup failed: {e}")

# Export all models and schemas
__all__ = [
    # SQLAlchemy Models
    'MonitoringSession',
    'ViolationDetection', 
    'MonitoringAlert',
    'PlatformMonitoringConfig',
    'MonitoringMetrics',
    'SystemPerformanceMetrics',
    'EnforcementAction',
    'AnalyticsReport',
    'DashboardLayout',
    'PerformanceOptimizationLog',
    
    # Enums
    'MonitoringStatusEnum',
    'PlatformTypeEnum',
    'ThreatLevelEnum',
    'ViolationStatusEnum',
    'MonitoringPriorityEnum',
    
    # Pydantic Models
    'MonitoringSessionCreate',
    'MonitoringSessionUpdate',
    'ViolationDetectionResponse',
    'MonitoringMetricsResponse',
    'SystemHealthResponse',
    'PlatformConfigUpdate',
    
    # Utility Functions
    'create_monitoring_indexes',
    'setup_monitoring_database',
    'setup_time_series_partitioning',
    
    # Base
    'Base'
]
