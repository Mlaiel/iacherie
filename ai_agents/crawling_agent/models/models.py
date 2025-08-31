"""
Database Models for Web Monitoring Agent

Industrial-grade ORM models for surveillance targets and violation alerts.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
)
try:
    from sqlalchemy.dialects.postgresql import JSONB as JSONType
except Exception:  # Fallback for non-PostgreSQL backends
    from sqlalchemy import JSON as JSONType  # type: ignore

try:
    from core.database import Base
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    Base = DatabaseManager


class SurveillanceTargetModel(Base):
    """Persistent surveillance target configuration."""

    __tablename__ = "ai_surveillance_targets"

    target_id = Column(String(64), primary_key=True, index=True)
    content_fingerprints = Column(JSONType, nullable=False)  # List[str]
    platforms = Column(JSONType, nullable=False)  # List[str]
    keywords = Column(JSONType, nullable=False)  # List[str]
    creator_info = Column(JSONType, nullable=False, default={})
    surveillance_mode = Column(String(32), nullable=False)
    priority = Column(String(32), nullable=False)
    scan_frequency = Column(Integer, nullable=False, default=3600)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_scan = Column(DateTime(timezone=True), nullable=True)


class ViolationAlertModel(Base):
    """Detected potential infringement alert record."""

    __tablename__ = "ai_violation_alerts"

    alert_id = Column(String(64), primary_key=True, index=True)
    target_id = Column(String(64), index=True, nullable=False)
    platform = Column(String(64), nullable=False)
    violation_url = Column(Text, nullable=False)
    violation_type = Column(String(64), nullable=False)
    severity = Column(String(32), nullable=False)
    similarity_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    detected_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    evidence = Column(JSONType, nullable=False, default={})
    status = Column(String(32), nullable=False, default="pending")
    action_taken = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
