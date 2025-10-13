"""
File Upload Model avec support multilingue (644+ langues)
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Float, ForeignKey, Enum as SQLEnum, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class FileType(str, enum.Enum):
    """Types de fichiers"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    OTHER = "other"


class FileStatus(str, enum.Enum):
    """Statuts de fichier"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    DELETED = "deleted"


class FileUpload(Base):
    """
    Fichier uploadé avec métadonnées multilingues
    """
    __tablename__ = "file_uploads"
    
    # ID et métadonnées
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(50), unique=True, index=True)
    
    # Utilisateur
    uploader_id = Column(Integer, ForeignKey("users.id"))
    uploader = relationship("User")
    
    # Mission associée (optionnelle)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=True)
    mission = relationship("Mission", back_populates="files")
    
    # Salle de chat associée (optionnelle)
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=True)
    
    # Informations du fichier
    filename = Column(String(500))
    original_filename = Column(String(500))
    file_path = Column(String(1000))
    file_url = Column(String(1000))
    
    # Type et format
    file_type = Column(SQLEnum(FileType))
    mime_type = Column(String(100))
    file_extension = Column(String(10))
    
    # Taille
    file_size = Column(BigInteger)  # En bytes
    file_size_human = Column(String(20))  # Ex: "1.5 MB"
    
    # Description multilingue
    description_translations = Column(JSON)
    tags_translations = Column(JSON)  # Tags dans toutes les langues
    original_language = Column(String(10), default="EN")
    
    # Métadonnées du fichier
    width = Column(Integer, nullable=True)  # Pour images/vidéos
    height = Column(Integer, nullable=True)
    duration = Column(Float, nullable=True)  # Pour vidéos/audios (secondes)
    
    # Statut
    status = Column(SQLEnum(FileStatus), default=FileStatus.UPLOADING)
    
    # Modération
    is_moderated = Column(Boolean, default=False)
    moderation_result = Column(JSON)
    is_safe = Column(Boolean, default=True)
    
    # Visibilité et permissions
    is_public = Column(Boolean, default=False)
    allowed_users = Column(JSON)  # Liste d'IDs autorisés à voir le fichier
    
    # Statistiques
    download_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    
    # Hash pour déduplication
    file_hash = Column(String(64), index=True)  # SHA256
    
    # Métadonnées
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    
    def to_dict(self, language: str = "EN") -> dict:
        description = ""
        if self.description_translations:
            description = self.description_translations.get(
                language.upper(),
                self.description_translations.get("EN", "")
            )
        
        return {
            "id": self.id,
            "file_id": self.file_id,
            "uploader_id": self.uploader_id,
            "mission_id": self.mission_id,
            "filename": self.filename,
            "file_url": self.file_url,
            "file_type": self.file_type.value if self.file_type else None,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "file_size_human": self.file_size_human,
            "description": description,
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "status": self.status.value if self.status else None,
            "is_safe": self.is_safe,
            "is_public": self.is_public,
            "download_count": self.download_count,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None
        }
