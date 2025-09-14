"""📱 Social Content Model - Enterprise Social Media Management"""
from typing import Dict, Any
from datetime import datetime
from enum import Enum

class SocialPlatform(Enum):
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"

class SocialContent:
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id")
        self.text = data.get("text")
        self.platform = data.get("platform", SocialPlatform.INSTAGRAM.value)
        self.created_at = datetime.utcnow()

class SocialContentModel:
    @staticmethod
    def create_content(content_data: Dict[str, Any]) -> SocialContent:
        return SocialContent(content_data)
