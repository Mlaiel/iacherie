"""SQLAlchemy model for Issues (Signalements citoyens)"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column, String, Text, Integer, Boolean,
    DateTime, ARRAY, JSON, Index, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
import enum

from models.base import Base


class IssueType(str, enum.Enum):
    """Types de signalements"""
    ENVIRONMENTAL = "environmental"  # Pollution, déchets
    INFRASTRUCTURE = "infrastructure"  # Routes, ponts cassés
    SAFETY = "safety"  # Dangers publics
    HERITAGE = "heritage"  # Patrimoine en danger
    ACCESSIBILITY = "accessibility"  # Problèmes PMR
    OTHER = "other"


class IssueStatus(str, enum.Enum):
    """Statut du signalement"""
    REPORTED = "reported"  # Signalé
    VERIFIED = "verified"  # Vérifié par modérateur
    IN_PROGRESS = "in_progress"  # En cours de résolution
    RESOLVED = "resolved"  # Résolu
    REJECTED = "rejected"  # Rejeté (spam, doublon)


class IssueSeverity(str, enum.Enum):
    """Gravité du problème"""
    LOW = "low"  # Faible
    MEDIUM = "medium"  # Moyen
    HIGH = "high"  # Élevé
    CRITICAL = "critical"  # Critique (danger immédiat)


class Issue(Base):
    """Issue (Signalement) model"""
    
    __tablename__ = 'ia2good_issues'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Type et statut
    type = Column(SQLEnum(IssueType, values_callable=lambda x: [e.value for e in x]), nullable=False, default=IssueType.OTHER)
    status = Column(SQLEnum(IssueStatus, values_callable=lambda x: [e.value for e in x]), default=IssueStatus.REPORTED)
    severity = Column(SQLEnum(IssueSeverity, values_callable=lambda x: [e.value for e in x]), default=IssueSeverity.MEDIUM)
    
    # Contenu
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    tags = Column(ARRAY(String(50)), default=[])
    
    # Localisation
    location = Column(Geography('POINT', srid=4326), nullable=True)
    address = Column(String(500))
    
    # Auteur
    reported_by = Column(UUID(as_uuid=True), nullable=False)  # Foreign key to users
    volunteer_id = Column(UUID(as_uuid=True))  # Si signalé par un volunteer
    
    # Médias
    media_urls = Column(ARRAY(String(500)), default=[])  # URLs des photos/vidéos
    media_types = Column(ARRAY(String(20)), default=[])  # 'photo' ou 'video'
    
    # Engagement
    views_count = Column(Integer, default=0)
    followers_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    # Recommandations
    recommended_to = Column(ARRAY(String(50)), default=[])  # Types d'acteurs recommandés
    notified_organizations = Column(ARRAY(UUID(as_uuid=True)), default=[])
    notified_authorities = Column(ARRAY(String(100)), default=[])
    
    # Résolution
    resolved_by = Column(UUID(as_uuid=True))  # Qui a résolu
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    resolution_media = Column(ARRAY(String(500)), default=[])  # Photos "après"
    
    # Métadonnées
    extra_metadata = Column(JSON, default={})  # Données flexibles
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_ia2good_issues_type', 'type'),
        Index('idx_ia2good_issues_status', 'status'),
        Index('idx_ia2good_issues_severity', 'severity'),
        Index('idx_ia2good_issues_location', 'location', postgresql_using='gist'),
        Index('idx_ia2good_issues_reported_by', 'reported_by'),
        Index('idx_ia2good_issues_created_at', 'created_at'),
        Index('idx_ia2good_issues_tags', 'tags', postgresql_using='gin'),
    )
    
    def __repr__(self):
        return f"<Issue(id={self.id}, type='{self.type}', status='{self.status}')>"


class IssueComment(Base):
    """Comments on issues"""
    
    __tablename__ = 'ia2good_issue_comments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    issue_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    
    content = Column(Text, nullable=False)
    media_urls = Column(ARRAY(String(500)), default=[])
    
    # Métadonnées
    is_official = Column(Boolean, default=False)  # Commentaire officiel (autorité, org)
    likes_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_ia2good_issue_comments_issue_id', 'issue_id'),
        Index('idx_ia2good_issue_comments_user_id', 'user_id'),
    )
    
    def __repr__(self):
        return f"<IssueComment(id={self.id}, issue_id={self.issue_id})>"


class IssueFollower(Base):
    """Users following an issue"""
    
    __tablename__ = 'ia2good_issue_followers'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    issue_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Préférences de notification
    notify_on_update = Column(Boolean, default=True)
    notify_on_comment = Column(Boolean, default=True)
    notify_on_resolution = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_ia2good_issue_followers_issue_id', 'issue_id'),
        Index('idx_ia2good_issue_followers_user_id', 'user_id'),
    )
    
    def __repr__(self):
        return f"<IssueFollower(issue_id={self.issue_id}, user_id={self.user_id})>"
