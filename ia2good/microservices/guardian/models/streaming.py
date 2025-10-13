"""
Streaming Models avec support multilingue (644+ langues)
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class StreamStatus(str, enum.Enum):
    """Statuts de stream"""
    SCHEDULED = "scheduled"
    LIVE = "live"
    PAUSED = "paused"
    ENDED = "ended"
    FAILED = "failed"


class StreamQuality(str, enum.Enum):
    """Qualités de stream"""
    LOW = "low"  # 360p
    MEDIUM = "medium"  # 720p
    HIGH = "high"  # 1080p
    ULTRA = "ultra"  # 4K


class LiveStream(Base):
    """
    Live streaming avec traduction automatique des sous-titres (644+ langues)
    """
    __tablename__ = "live_streams"
    
    # ID et métadonnées
    id = Column(Integer, primary_key=True, index=True)
    stream_id = Column(String(50), unique=True, index=True)
    
    # Streamer
    streamer_id = Column(Integer, ForeignKey("users.id"))
    streamer = relationship("User")
    
    # Mission associée
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=True)
    mission = relationship("Mission", back_populates="streams")
    
    # Titre et description (multilingue)
    title_translations = Column(JSON)
    description_translations = Column(JSON)
    original_language = Column(String(10), default="EN")
    
    # Configuration technique
    stream_key = Column(String(100), unique=True)
    rtmp_url = Column(String(500))
    hls_url = Column(String(500))
    
    # Qualité
    quality = Column(SQLEnum(StreamQuality), default=StreamQuality.MEDIUM)
    
    # Statut
    status = Column(SQLEnum(StreamStatus), default=StreamStatus.SCHEDULED)
    
    # Dates
    scheduled_start = Column(DateTime, nullable=True)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    duration = Column(Integer, default=0)  # Durée en secondes
    
    # Sous-titres automatiques (644+ langues)
    auto_captions_enabled = Column(Boolean, default=True)
    available_caption_languages = Column(JSON)  # Langues de sous-titres disponibles
    
    # Traduction en temps réel
    real_time_translation_enabled = Column(Boolean, default=True)
    translation_languages = Column(JSON)  # Langues vers lesquelles traduire
    
    # Participants
    viewers_count = Column(Integer, default=0)
    max_viewers = Column(Integer, default=0)
    viewer_list = Column(JSON)  # Liste des viewers connectés
    
    # Modération
    chat_enabled = Column(Boolean, default=True)
    moderation_enabled = Column(Boolean, default=True)
    moderators = Column(JSON)  # Liste d'IDs de modérateurs
    
    # Enregistrement
    is_recorded = Column(Boolean, default=True)
    recording_url = Column(String(500), nullable=True)
    
    # Statistiques
    total_views = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    def get_title(self, language: str = "EN") -> str:
        if not self.title_translations:
            return ""
        return self.title_translations.get(language.upper(),
                                           self.title_translations.get("EN", ""))
    
    def to_dict(self, language: str = "EN") -> dict:
        return {
            "id": self.id,
            "stream_id": self.stream_id,
            "streamer_id": self.streamer_id,
            "mission_id": self.mission_id,
            "title": self.get_title(language),
            "status": self.status.value if self.status else None,
            "quality": self.quality.value if self.quality else None,
            "viewers_count": self.viewers_count,
            "max_viewers": self.max_viewers,
            "chat_enabled": self.chat_enabled,
            "auto_captions_enabled": self.auto_captions_enabled,
            "available_caption_languages": self.available_caption_languages,
            "scheduled_start": self.scheduled_start.isoformat() if self.scheduled_start else None,
            "actual_start": self.actual_start.isoformat() if self.actual_start else None,
            "total_views": self.total_views,
            "likes_count": self.likes_count
        }


class VideoRoom(Base):
    """
    Salle de visioconférence avec traduction automatique (644+ langues)
    """
    __tablename__ = "video_rooms"
    
    # ID et métadonnées
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(String(50), unique=True, index=True)
    
    # Hôte
    host_id = Column(Integer, ForeignKey("users.id"))
    host = relationship("User")
    
    # Mission associée
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=True)
    
    # Nom et description (multilingue)
    name_translations = Column(JSON)
    description_translations = Column(JSON)
    original_language = Column(String(10), default="EN")
    
    # Configuration
    max_participants = Column(Integer, default=10)
    is_public = Column(Boolean, default=False)
    require_approval = Column(Boolean, default=True)
    
    # Participants
    participants = Column(JSON)  # Liste d'IDs de participants
    waiting_room = Column(JSON)  # Liste d'IDs en attente d'approbation
    
    # Traduction en temps réel
    real_time_translation_enabled = Column(Boolean, default=True)
    participant_languages = Column(JSON)  # {"user_id": "language_code"}
    
    # Sous-titres
    captions_enabled = Column(Boolean, default=True)
    
    # Fonctionnalités
    recording_enabled = Column(Boolean, default=False)
    screen_sharing_enabled = Column(Boolean, default=True)
    chat_enabled = Column(Boolean, default=True)
    
    # Statut
    is_active = Column(Boolean, default=False)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_name(self, language: str = "EN") -> str:
        if not self.name_translations:
            return ""
        return self.name_translations.get(language.upper(),
                                          self.name_translations.get("EN", ""))
    
    def to_dict(self, language: str = "EN") -> dict:
        return {
            "id": self.id,
            "room_id": self.room_id,
            "host_id": self.host_id,
            "mission_id": self.mission_id,
            "name": self.get_name(language),
            "max_participants": self.max_participants,
            "is_public": self.is_public,
            "participants_count": len(self.participants) if self.participants else 0,
            "real_time_translation_enabled": self.real_time_translation_enabled,
            "captions_enabled": self.captions_enabled,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
