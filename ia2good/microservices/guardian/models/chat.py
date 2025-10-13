"""
Chat Models avec support multilingue (644+ langues)
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class ChatRoomType(str, enum.Enum):
    """Types de salles de chat"""
    PUBLIC = "public"
    PRIVATE = "private"
    MISSION = "mission"
    DIRECT = "direct"
    GROUP = "group"


class MessageType(str, enum.Enum):
    """Types de messages"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    LOCATION = "location"
    SYSTEM = "system"


class ChatRoom(Base):
    """
    Salle de chat avec support multilingue (644+ langues)
    Traduction automatique des messages en temps réel
    """
    __tablename__ = "chat_rooms"
    
    # ID et métadonnées
    id = Column(Integer, primary_key=True, index=True)
    room_code = Column(String(50), unique=True, index=True)  # Ex: "ROOM-2024-001"
    
    # Type de salle
    room_type = Column(SQLEnum(ChatRoomType), default=ChatRoomType.PUBLIC)
    
    # Nom et description (multilingue)
    name_translations = Column(JSON)  # {"EN": "Help Chat", "FR": "Chat d'aide", ...}
    description_translations = Column(JSON)
    original_language = Column(String(10), default="EN")
    
    # Mission associée (si applicable)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=True)
    mission = relationship("Mission", back_populates="chat_rooms")
    
    # Créateur de la salle
    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", foreign_keys=[creator_id])
    
    # Membres
    members = Column(JSON)  # Liste d'IDs de membres
    admins = Column(JSON)  # Liste d'IDs d'admins
    banned_users = Column(JSON)  # Liste d'IDs d'utilisateurs bannis
    
    # Configuration
    max_members = Column(Integer, default=100)
    is_public = Column(Boolean, default=True)
    allow_files = Column(Boolean, default=True)
    allow_voice = Column(Boolean, default=True)
    allow_video = Column(Boolean, default=False)
    
    # Traduction automatique
    auto_translate = Column(Boolean, default=True)  # Traduire automatiquement les messages
    supported_languages = Column(JSON)  # Langues supportées dans cette salle (vide = toutes)
    
    # Modération
    moderation_enabled = Column(Boolean, default=True)
    profanity_filter = Column(Boolean, default=True)
    spam_protection = Column(Boolean, default=True)
    
    # Statistiques
    total_messages = Column(Integer, default=0)
    active_members_count = Column(Integer, default=0)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relations
    messages = relationship("ChatMessage", back_populates="chat_room", cascade="all, delete-orphan")
    
    def get_name(self, language: str = "EN") -> str:
        """Obtient le nom dans la langue demandée"""
        if not self.name_translations:
            return ""
        return self.name_translations.get(language.upper(),
                                          self.name_translations.get("EN", ""))
    
    def to_dict(self, language: str = "EN") -> dict:
        return {
            "id": self.id,
            "room_code": self.room_code,
            "room_type": self.room_type.value if self.room_type else None,
            "name": self.get_name(language),
            "mission_id": self.mission_id,
            "creator_id": self.creator_id,
            "members_count": len(self.members) if self.members else 0,
            "max_members": self.max_members,
            "is_public": self.is_public,
            "auto_translate": self.auto_translate,
            "total_messages": self.total_messages,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ChatMessage(Base):
    """
    Message de chat avec traductions automatiques (644+ langues)
    Chaque message est traduit dans toutes les langues des participants
    """
    __tablename__ = "chat_messages"
    
    # ID et métadonnées
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(50), unique=True, index=True)  # Ex: "MSG-2024-001"
    
    # Salle de chat
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id"))
    chat_room = relationship("ChatRoom", back_populates="messages")
    
    # Expéditeur
    sender_id = Column(Integer, ForeignKey("users.id"))
    sender = relationship("User")
    
    # Type de message
    message_type = Column(SQLEnum(MessageType), default=MessageType.TEXT)
    
    # Contenu original
    original_content = Column(Text)
    original_language = Column(String(10))
    
    # Traductions automatiques (644+ langues)
    # Format: {"EN": "Hello", "FR": "Bonjour", "AR": "مرحبا", ...}
    content_translations = Column(JSON)
    
    # Médias attachés
    attachments = Column(JSON)  # Images, vidéos, fichiers, etc.
    
    # Métadonnées du message
    reply_to_id = Column(Integer, ForeignKey("chat_messages.id"), nullable=True)
    reply_to = relationship("ChatMessage", remote_side=[id])
    
    # Réactions
    reactions = Column(JSON)  # {"❤️": [user_id1, user_id2], "👍": [user_id3]}
    
    # Modération
    is_moderated = Column(Boolean, default=False)
    moderation_result = Column(JSON)  # Résultat de la modération
    is_flagged = Column(Boolean, default=False)
    flagged_by = Column(JSON)  # Liste d'IDs d'utilisateurs qui ont signalé
    flagged_reason_translations = Column(JSON)  # Raison du signalement (multilingue)
    
    # Statut
    is_deleted = Column(Boolean, default=False)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime, nullable=True)
    edit_history = Column(JSON)  # Historique des modifications
    
    # Lu/Non lu
    read_by = Column(JSON)  # Liste d'IDs d'utilisateurs qui ont lu le message
    
    # Métadonnées
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    
    # Géolocalisation (optionnelle)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_name = Column(String(200), nullable=True)
    
    def get_content(self, language: str = "EN") -> str:
        """Obtient le contenu dans la langue demandée"""
        if not self.content_translations:
            return self.original_content or ""
        return self.content_translations.get(language.upper(),
                                             self.content_translations.get("EN", 
                                                                          self.original_content or ""))
    
    def to_dict(self, language: str = "EN") -> dict:
        return {
            "id": self.id,
            "message_id": self.message_id,
            "chat_room_id": self.chat_room_id,
            "sender_id": self.sender_id,
            "message_type": self.message_type.value if self.message_type else None,
            "content": self.get_content(language),
            "original_language": self.original_language,
            "attachments": self.attachments,
            "reply_to_id": self.reply_to_id,
            "reactions": self.reactions,
            "is_flagged": self.is_flagged,
            "is_deleted": self.is_deleted,
            "is_edited": self.is_edited,
            "read_by": self.read_by,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "latitude": self.latitude,
            "longitude": self.longitude
        }


class DirectMessage(Base):
    """
    Messages directs entre utilisateurs avec traduction automatique
    """
    __tablename__ = "direct_messages"
    
    # ID et métadonnées
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(50), unique=True, index=True)
    
    # Expéditeur et destinataire
    sender_id = Column(Integer, ForeignKey("users.id"))
    sender = relationship("User", foreign_keys=[sender_id])
    
    recipient_id = Column(Integer, ForeignKey("users.id"))
    recipient = relationship("User", foreign_keys=[recipient_id])
    
    # Type de message
    message_type = Column(SQLEnum(MessageType), default=MessageType.TEXT)
    
    # Contenu
    original_content = Column(Text)
    original_language = Column(String(10))
    content_translations = Column(JSON)  # Traductions dans 644+ langues
    
    # Pièces jointes
    attachments = Column(JSON)
    
    # Statut
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    
    is_deleted_by_sender = Column(Boolean, default=False)
    is_deleted_by_recipient = Column(Boolean, default=False)
    
    # Modération
    is_moderated = Column(Boolean, default=False)
    moderation_result = Column(JSON)
    
    # Métadonnées
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    
    def get_content(self, language: str = "EN") -> str:
        """Obtient le contenu dans la langue demandée"""
        if not self.content_translations:
            return self.original_content or ""
        return self.content_translations.get(language.upper(),
                                             self.content_translations.get("EN",
                                                                          self.original_content or ""))
    
    def to_dict(self, language: str = "EN") -> dict:
        return {
            "id": self.id,
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type.value if self.message_type else None,
            "content": self.get_content(language),
            "original_language": self.original_language,
            "attachments": self.attachments,
            "is_read": self.is_read,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None
        }
