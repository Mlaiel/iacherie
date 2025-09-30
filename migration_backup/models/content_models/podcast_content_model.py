"""🎙️ Podcast Content Model - Enterprise Podcast Management"""
from typing import Dict, Any
from datetime import datetime
from enum import Enum

class PodcastFormat(Enum):
    MP3 = "mp3"
    WAV = "wav"

class PodcastContent:
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id")
        self.title = data.get("title")
        self.format = data.get("format", PodcastFormat.MP3.value)
        self.created_at = datetime.utcnow()

class PodcastContentModel:
    @staticmethod
    def create_content(content_data: Dict[str, Any]) -> PodcastContent:
        return PodcastContent(content_data)
