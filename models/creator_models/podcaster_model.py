"""🎙️ Podcaster Model - Audio Content Creator Specialization
=========================================================
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import uuid

from .user_model import UserProfile, UserModel

class PodcastCategory(Enum):
    NEWS = "news"
    COMEDY = "comedy"
    EDUCATION = "education"
    BUSINESS = "business"
    TECHNOLOGY = "technology"
    HEALTH = "health"
    ENTERTAINMENT = "entertainment"

@dataclass
class PodcastChannel:
    id: str
    title: str
    podcaster_id: str
    category: PodcastCategory
    episodes: int = 0
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

@dataclass
class PodcasterProfile:
    user_profile: UserProfile
    show_name: Optional[str] = None
    categories: List[PodcastCategory] = field(default_factory=list)
    channels: List[PodcastChannel] = field(default_factory=list)

class PodcasterModel:
    @staticmethod
    def create_profile(user_data: Dict[str, Any]) -> PodcasterProfile:
        user_profile = UserModel.create_profile(user_data)
        podcaster_data = user_data.get("podcaster_data", {})
        
        return PodcasterProfile(
            user_profile=user_profile,
            show_name=podcaster_data.get("show_name"),
            categories=[PodcastCategory(c) for c in podcaster_data.get("categories", []) if c in [e.value for e in PodcastCategory]]
        )

__all__ = ['PodcasterModel', 'PodcasterProfile', 'PodcastChannel', 'PodcastCategory']