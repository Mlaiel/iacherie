"""
🎵 AUDIO FINGERPRINT MODEL - ENTERPRISE GRADE
============================================

Modèle pour l'empreinte audio et reconnaissance musicale
Architecture: SQLAlchemy + librosa + ML patterns

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Float, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from .base_ai_model import Base
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid

class AudioFingerprintModel(Base):
    """
    Modèle d'empreinte audio pour reconnaissance et protection
    Support: librosa, chromaprint, audio similarity
    """
    __tablename__ = 'audio_fingerprints'
    
    # Core Identity
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Content Reference
    content_id = Column(Integer, nullable=False, index=True)  # Reference to content
    content_uuid = Column(String(36), nullable=False, index=True)
    
    # Audio Properties
    duration_seconds = Column(Float, nullable=False)
    sample_rate = Column(Integer, nullable=False)
    channels = Column(Integer, nullable=False, default=1)
    bit_depth = Column(Integer, nullable=True)
    file_format = Column(String(20), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    
    # Fingerprint Data
    chromaprint_hash = Column(String(500), nullable=True, index=True)  # Chromaprint fingerprint
    mfcc_features = Column(JSON, nullable=True)  # MFCC features
    spectral_features = Column(JSON, nullable=True)  # Spectral features
    tempo = Column(Float, nullable=True)
    key_signature = Column(String(10), nullable=True)
    time_signature = Column(String(10), nullable=True)
    
    # Advanced Features
    chroma_features = Column(JSON, nullable=True)  # Chroma features
    tonnetz_features = Column(JSON, nullable=True)  # Tonnetz features
    zero_crossing_rate = Column(Float, nullable=True)
    spectral_centroid = Column(Float, nullable=True)
    spectral_rolloff = Column(Float, nullable=True)
    
    # Genre & Style Detection
    detected_genre = Column(String(100), nullable=True)
    genre_confidence = Column(Float, nullable=True)
    detected_style = Column(String(100), nullable=True)
    energy_level = Column(Float, nullable=True)  # 0.0 to 1.0
    danceability = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Similarity Hashes
    perceptual_hash = Column(String(64), nullable=True, index=True)
    audio_hash_md5 = Column(String(32), nullable=True)
    content_hash = Column(String(64), nullable=True)
    
    # Processing Status
    processing_status = Column(String(50), nullable=False, default="pending")  # pending, processing, completed, failed
    extraction_model_version = Column(String(20), nullable=False, default="1.0.0")
    processing_time_seconds = Column(Float, nullable=True)
    
    # Quality Metrics
    signal_quality = Column(Float, nullable=True)  # 0.0 to 1.0
    noise_level = Column(Float, nullable=True)
    dynamic_range = Column(Float, nullable=True)
    
    # Metadata
    original_filename = Column(String(255), nullable=True)
    processing_notes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<AudioFingerprintModel(content_id={self.content_id}, duration={self.duration_seconds}s)>"
    
    @property
    def is_processed(self) -> bool:
        """Vérifie si l'empreinte est traitée"""
        return self.processing_status == "completed" and self.processed_at is not None
    
    @property
    def has_fingerprint(self) -> bool:
        """Vérifie si une empreinte est disponible"""
        return self.chromaprint_hash is not None or self.perceptual_hash is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le modèle en dictionnaire"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'content_id': self.content_id,
            'content_uuid': self.content_uuid,
            'duration_seconds': self.duration_seconds,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'chromaprint_hash': self.chromaprint_hash,
            'tempo': self.tempo,
            'key_signature': self.key_signature,
            'detected_genre': self.detected_genre,
            'genre_confidence': self.genre_confidence,
            'energy_level': self.energy_level,
            'danceability': self.danceability,
            'processing_status': self.processing_status,
            'signal_quality': self.signal_quality,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
    
    def calculate_similarity(self, other_fingerprint: 'AudioFingerprintModel') -> float:
        """Calcule la similarité avec une autre empreinte audio"""
        if not self.has_fingerprint or not other_fingerprint.has_fingerprint:
            return 0.0
        
        # Placeholder for actual similarity calculation
        # Would implement chromaprint comparison, MFCC distance, etc.
        return 0.0
    
    def update_processing_status(self, status: str, notes: Optional[str] = None):
        """Met à jour le statut de traitement"""
        self.processing_status = status
        if notes:
            self.processing_notes = notes
        if status == "completed":
            self.processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def extract_features_from_audio(self, audio_file_path: str):
        """
        Extrait les caractéristiques audio du fichier
        Note: Implémentation placeholder - nécessiterait librosa
        """
        # Placeholder for actual feature extraction
        # Would use librosa, chromaprint, etc.
        self.processing_status = "processing"
        # ... feature extraction logic would go here
        self.processing_status = "completed"
        self.processed_at = datetime.utcnow()

class AudioSimilarityMatch(Base):
    """Modèle pour stocker les correspondances de similarité audio"""
    __tablename__ = 'audio_similarity_matches'
    
    id = Column(Integer, primary_key=True, index=True)
    source_fingerprint_id = Column(Integer, ForeignKey('audio_fingerprints.id'), nullable=False)
    target_fingerprint_id = Column(Integer, ForeignKey('audio_fingerprints.id'), nullable=False)
    similarity_score = Column(Float, nullable=False)  # 0.0 to 1.0
    match_type = Column(String(50), nullable=False)  # exact, high, medium, low
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    source_fingerprint = relationship("AudioFingerprintModel", foreign_keys=[source_fingerprint_id])
    target_fingerprint = relationship("AudioFingerprintModel", foreign_keys=[target_fingerprint_id])