"""⚡ Infrastructure Performance Database Module - High-Performance Database Optimization
=========================================================================================
Module: backend/database/infrastructure_performance.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Consolidated Infrastructure Performance Database - Ultra Enterprise Production-Ready
Responsibility: Database sharding, performance tuning, connection management, health monitoring, and automatic scaling
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

class ShardStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MIGRATING = "migrating"
    MAINTENANCE = "maintenance"

class PerformanceLevel(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

class DatabaseSharding(Base):
    """Intelligent database sharding management."""
    __tablename__ = 'database_sharding'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shard_name = Column(String(255), nullable=False, unique=True)
    shard_key = Column(String(255), nullable=False)
    shard_range_start = Column(String(255), nullable=True)
    shard_range_end = Column(String(255), nullable=True)
    database_host = Column(String(255), nullable=False)
    database_port = Column(Integer, default=5432)
    database_name = Column(String(255), nullable=False)
    connection_pool_size = Column(Integer, default=10)
    max_connections = Column(Integer, default=100)
    shard_status = Column(SQLEnum(ShardStatus), default=ShardStatus.ACTIVE)
    data_size_gb = Column(Float, default=0.0)
    record_count = Column(BigInteger, default=0)
    read_operations_per_second = Column(Float, default=0.0)
    write_operations_per_second = Column(Float, default=0.0)
    average_response_time_ms = Column(Float, nullable=True)
    cpu_utilization_percentage = Column(Float, nullable=True)
    memory_utilization_percentage = Column(Float, nullable=True)
    disk_utilization_percentage = Column(Float, nullable=True)
    last_maintenance_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class QueryPerformanceTuning(Base):
    """Automated query performance optimization."""
    __tablename__ = 'query_performance_tuning'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_hash = Column(String(255), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    query_type = Column(String(50), nullable=False)  # SELECT, INSERT, UPDATE, DELETE
    table_names = Column(ARRAY(String), default=[])
    execution_count = Column(BigInteger, default=0)
    total_execution_time_ms = Column(Float, default=0.0)
    average_execution_time_ms = Column(Float, nullable=True)
    min_execution_time_ms = Column(Float, nullable=True)
    max_execution_time_ms = Column(Float, nullable=True)
    rows_examined = Column(BigInteger, nullable=True)
    rows_returned = Column(BigInteger, nullable=True)
    index_usage = Column(JSONB, default={})
    execution_plan = Column(JSONB, default={})
    optimization_suggestions = Column(JSONB, default=[])
    performance_level = Column(SQLEnum(PerformanceLevel), nullable=True)
    optimization_applied = Column(Boolean, default=False)
    optimization_impact = Column(JSONB, default={})
    last_executed_at = Column(DateTime(timezone=True), nullable=True)
    first_seen_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_analyzed_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class ConnectionLoadBalancing(Base):
    """Connection pool and load balancing management."""
    __tablename__ = 'connection_load_balancing'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pool_name = Column(String(255), nullable=False, unique=True)
    database_host = Column(String(255), nullable=False)
    database_port = Column(Integer, default=5432)
    pool_size = Column(Integer, default=10)
    max_overflow = Column(Integer, default=20)
    active_connections = Column(Integer, default=0)
    idle_connections = Column(Integer, default=0)
    connection_timeouts = Column(Integer, default=0)
    connection_failures = Column(Integer, default=0)
    average_connection_time_ms = Column(Float, nullable=True)
    peak_connections = Column(Integer, default=0)
    load_balancing_algorithm = Column(String(50), default='round_robin')
    health_check_interval_seconds = Column(Integer, default=30)
    failover_threshold = Column(Integer, default=3)
    auto_scaling_enabled = Column(Boolean, default=True)
    scaling_triggers = Column(JSONB, default={})
    last_health_check = Column(DateTime(timezone=True), nullable=True)
    last_scaled_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class DatabaseHealthMonitoring(Base):
    """Real-time database health and performance monitoring."""
    __tablename__ = 'database_health_monitoring'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    database_instance_id = Column(String(255), nullable=False, index=True)
    instance_name = Column(String(255), nullable=False)
    database_type = Column(String(50), nullable=False)  # postgresql, mysql, mongodb, etc.
    health_status = Column(String(50), default='healthy')
    overall_performance_score = Column(Float, nullable=True)  # 0-100
    cpu_usage_percentage = Column(Float, nullable=True)
    memory_usage_percentage = Column(Float, nullable=True)
    disk_usage_percentage = Column(Float, nullable=True)
    network_io_mbps = Column(Float, nullable=True)
    disk_io_operations_per_second = Column(Float, nullable=True)
    active_connections_count = Column(Integer, nullable=True)
    slow_queries_count = Column(Integer, default=0)
    deadlocks_count = Column(Integer, default=0)
    replication_lag_seconds = Column(Float, nullable=True)
    backup_status = Column(String(50), nullable=True)
    last_backup_at = Column(DateTime(timezone=True), nullable=True)
    error_rate = Column(Float, nullable=True)
    availability_percentage = Column(Float, nullable=True)
    response_time_p95_ms = Column(Float, nullable=True)
    response_time_p99_ms = Column(Float, nullable=True)
    alert_conditions = Column(JSONB, default=[])
    performance_trends = Column(JSONB, default={})
    capacity_forecasting = Column(JSONB, default={})
    recorded_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class AutomaticScaling(Base):
    """Automatic scaling configuration and history."""
    __tablename__ = 'automatic_scaling'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_type = Column(String(100), nullable=False)  # database, connection_pool, storage
    resource_id = Column(String(255), nullable=False, index=True)
    scaling_policy = Column(JSONB, default={})
    current_capacity = Column(Integer, nullable=False)
    target_capacity = Column(Integer, nullable=True)
    min_capacity = Column(Integer, default=1)
    max_capacity = Column(Integer, default=100)
    scaling_triggers = Column(JSONB, default={})
    scaling_metrics = Column(JSONB, default={})
    cooldown_period_seconds = Column(Integer, default=300)
    scaling_action = Column(String(50), nullable=True)  # scale_up, scale_down, no_action
    scaling_reason = Column(Text, nullable=True)
    scaling_magnitude = Column(Integer, nullable=True)
    scaling_success = Column(Boolean, nullable=True)
    scaling_duration_seconds = Column(Integer, nullable=True)
    pre_scaling_metrics = Column(JSONB, default={})
    post_scaling_metrics = Column(JSONB, default={})
    cost_impact = Column(Numeric(10, 2), nullable=True)
    performance_impact = Column(JSONB, default={})
    last_scaling_event_at = Column(DateTime(timezone=True), nullable=True)
    next_evaluation_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class DisasterRecoveryAutomation(Base):
    """Automated disaster recovery management."""
    __tablename__ = 'disaster_recovery_automation'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recovery_plan_name = Column(String(255), nullable=False)
    primary_site = Column(String(255), nullable=False)
    backup_sites = Column(ARRAY(String), default=[])
    recovery_time_objective_minutes = Column(Integer, nullable=False)
    recovery_point_objective_minutes = Column(Integer, nullable=False)
    automated_failover_enabled = Column(Boolean, default=True)
    failover_triggers = Column(JSONB, default={})
    health_check_frequency_seconds = Column(Integer, default=60)
    backup_frequency_hours = Column(Integer, default=24)
    last_backup_verification = Column(DateTime(timezone=True), nullable=True)
    last_failover_test = Column(DateTime(timezone=True), nullable=True)
    failover_test_results = Column(JSONB, default={})
    current_active_site = Column(String(255), nullable=False)
    failover_status = Column(String(50), default='normal')
    data_replication_status = Column(JSONB, default={})
    recovery_procedures = Column(JSONB, default=[])
    contact_information = Column(JSONB, default={})
    compliance_requirements = Column(JSONB, default={})
    last_recovery_drill = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

def get_infrastructure_performance_models():
    return [DatabaseSharding, QueryPerformanceTuning, ConnectionLoadBalancing, DatabaseHealthMonitoring, AutomaticScaling, DisasterRecoveryAutomation]

def create_infrastructure_performance_tables(engine):
    try:
        Base.metadata.create_all(engine, tables=[model.__table__ for model in get_infrastructure_performance_models()])
        logger.info("Successfully created infrastructure performance tables")
        return True
    except Exception as e:
        logger.error(f"Failed to create infrastructure performance tables: {str(e)}")
        return False

__all__ = ['ShardStatus', 'PerformanceLevel', 'DatabaseSharding', 'QueryPerformanceTuning', 'ConnectionLoadBalancing', 'DatabaseHealthMonitoring', 'AutomaticScaling', 'DisasterRecoveryAutomation', 'get_infrastructure_performance_models', 'create_infrastructure_performance_tables']