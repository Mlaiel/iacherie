"""Sfrom sqlalchemy import (
    Column, String, Text, Integer, Boolean,
    DateTime, ARRAY, JSON, Index, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
import enum

from models.base import Base model for Events (Événements collectifs)"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean,
    DateTime, ARRAY, JSON, Index, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
import enum

from .base import Base


class EventType(str, enum.Enum):
    """Types d'événements"""
    CLEANUP = "cleanup"  # Nettoyage
    PROTEST = "protest"  # Manifestation
    WORKSHOP = "workshop"  # Atelier, formation
    FUNDRAISER = "fundraiser"  # Collecte de fonds
    AWARENESS = "awareness"  # Sensibilisation
    TREE_PLANTING = "tree_planting"  # Plantation d'arbres
    FOOD_DISTRIBUTION = "food_distribution"  # Distribution alimentaire
    COMMUNITY_GATHERING = "community_gathering"  # Rassemblement
    OTHER = "other"


class EventStatus(str, enum.Enum):
    """Statut de l'événement"""
    DRAFT = "draft"  # Brouillon
    PUBLISHED = "published"  # Publié
    ONGOING = "ongoing"  # En cours
    COMPLETED = "completed"  # Terminé
    CANCELLED = "cancelled"  # Annulé


class Event(Base):
    """Event (Événement) model"""
    
    __tablename__ = 'ia2good_events'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Type et statut
    type = Column(SQLEnum(EventType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    status = Column(SQLEnum(EventStatus, values_callable=lambda x: [e.value for e in x]), default=EventStatus.DRAFT)
    
    # Contenu
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    objectives = Column(Text)  # Objectifs de l'événement
    tags = Column(ARRAY(String(50)), default=[])
    
    # Organisateur
    organizer_id = Column(UUID(as_uuid=True), nullable=False)  # Foreign key to users
    co_organizers = Column(ARRAY(UUID(as_uuid=True)), default=[])
    
    # Localisation
    location = Column(Geography('POINT', srid=4326), nullable=True)
    address = Column(String(500))
    venue_name = Column(String(200))
    
    # Dates
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    registration_deadline = Column(DateTime)
    
    # Capacité et participation
    capacity = Column(Integer)  # Capacité maximale (null = illimité)
    participants_count = Column(Integer, default=0)
    checked_in_count = Column(Integer, default=0)
    min_participants = Column(Integer)  # Minimum pour maintenir l'événement
    
    # Médias
    cover_image = Column(String(500))
    images = Column(ARRAY(String(500)), default=[])
    videos = Column(ARRAY(String(500)), default=[])
    
    # Exigences pour participer
    required_skills = Column(ARRAY(String(50)), default=[])
    age_minimum = Column(Integer)
    equipment_needed = Column(ARRAY(String(100)), default=[])  # Matériel à apporter
    
    # Résultats (après l'événement)
    attendance_count = Column(Integer, default=0)  # Présence réelle
    impact_summary = Column(Text)  # Résumé de l'impact
    impact_metrics = Column(JSON, default={})  # Métriques (kg déchets, arbres plantés, etc.)
    photos_after = Column(ARRAY(String(500)), default=[])
    
    # Métadonnées
    extra_metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)
    
    # Indexes
    __table_args__ = (
        Index('idx_ia2good_events_type', 'type'),
        Index('idx_ia2good_events_status', 'status'),
        Index('idx_ia2good_events_organizer_id', 'organizer_id'),
        Index('idx_ia2good_events_location', 'location', postgresql_using='gist'),
        Index('idx_ia2good_events_start_date', 'start_date'),
        Index('idx_ia2good_events_tags', 'tags', postgresql_using='gin'),
    )
    
    def __repr__(self):
        return f"<Event(id={self.id}, type='{self.type}', title='{self.title}')>"


class EventParticipant(Base):
    """Participants aux événements"""
    
    __tablename__ = 'ia2good_event_participants'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Statut
    status = Column(String(20), default='registered')  # registered, approved, declined, attended, absent
    
    # Check-in
    checked_in = Column(Boolean, default=False)
    checked_in_at = Column(DateTime)
    
    # Rôle dans l'événement
    role = Column(String(50))  # 'participant', 'helper', 'coordinator'
    tasks_assigned = Column(ARRAY(String(100)), default=[])
    
    # Notes
    registration_notes = Column(Text)  # Message lors de l'inscription
    organizer_notes = Column(Text)  # Notes de l'organisateur
    
    # Feedback après l'événement
    attended = Column(Boolean)
    rating = Column(Integer)  # 1-5
    feedback = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_ia2good_event_participants_event_id', 'event_id'),
        Index('idx_ia2good_event_participants_user_id', 'user_id'),
        Index('idx_ia2good_event_participants_status', 'status'),
    )
    
    def __repr__(self):
        return f"<EventParticipant(event_id={self.event_id}, user_id={self.user_id})>"


class EventUpdate(Base):
    """Mises à jour et annonces pour événements"""
    
    __tablename__ = 'ia2good_event_updates'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    author_id = Column(UUID(as_uuid=True), nullable=False)
    
    title = Column(String(200))
    content = Column(Text, nullable=False)
    media_urls = Column(ARRAY(String(500)), default=[])
    
    # Type d'update
    update_type = Column(String(50), default='general')  # general, important, reminder, cancellation
    
    # Notifications
    notify_participants = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_ia2good_event_updates_event_id', 'event_id'),
    )
    
    def __repr__(self):
        return f"<EventUpdate(id={self.id}, event_id={self.event_id})>"
