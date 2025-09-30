"""🎵 Audio Content Model - Music and Audio Specialization
======================================================
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import uuid

from .base_content_model import BaseContentModel, ContentItem, ContentMetadata

class AudioFormat(Enum):
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    M4A = "m4a"
    OGG = "ogg"

@dataclass
class AudioContent(ContentItem):
    duration_seconds: int = 0
    bitrate_kbps: int = 0
    sample_rate_hz: int = 44100
    channels: int = 2
    format: AudioFormat = AudioFormat.MP3
    bpm: Optional[int] = None
    key: Optional[str] = None
    genre: Optional[str] = None
    album: Optional[str] = None
    track_number: Optional[int] = None
    
    def get_duration_formatted(self) -> str:
        """Get formatted duration"""
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"

class AudioContentModel:
    @staticmethod
    def create_content(content_data: Dict[str, Any]) -> AudioContent:
        """Create audio content"""
        base_content = BaseContentModel.create_content(content_data)
        
        # Convert to AudioContent
        audio_content = AudioContent(
            id=base_content.id,
            creator_id=base_content.creator_id,
            content_type="audio",
            metadata=base_content.metadata,
            file_path=base_content.file_path,
            file_size_bytes=base_content.file_size_bytes,
            file_hash=base_content.file_hash,
            mime_type=base_content.mime_type,
            status=base_content.status,
            visibility=base_content.visibility,
            duration_seconds=content_data.get("duration_seconds", 0),
            bitrate_kbps=content_data.get("bitrate_kbps", 128),
            sample_rate_hz=content_data.get("sample_rate_hz", 44100),
            channels=content_data.get("channels", 2),
            format=AudioFormat(content_data.get("format", "mp3")),
            bpm=content_data.get("bpm"),
            key=content_data.get("key"),
            genre=content_data.get("genre"),
            album=content_data.get("album"),
            track_number=content_data.get("track_number")
        )
        
        return audio_content

__all__ = ['AudioContentModel', 'AudioContent', 'AudioFormat']
