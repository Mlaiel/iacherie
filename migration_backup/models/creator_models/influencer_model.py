"""🌟 Influencer Model - Social Creator Specialization
==================================================
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import uuid

from .user_model import UserProfile, UserModel

class Platform(Enum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"

@dataclass
class Campaign:
    id: str
    title: str
    platform: Platform
    influencer_id: str
    start_date: datetime
    end_date: datetime
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

@dataclass
class InfluencerProfile:
    user_profile: UserProfile
    brand_name: Optional[str] = None
    platforms: List[Platform] = field(default_factory=list)
    campaigns: List[Campaign] = field(default_factory=list)
    
    def get_display_name(self) -> str:
        return self.brand_name or self.user_profile.display_name

class InfluencerModel:
    @staticmethod
    def create_profile(user_data: Dict[str, Any]) -> InfluencerProfile:
        user_profile = UserModel.create_profile(user_data)
        influencer_data = user_data.get("influencer_data", {})
        
        return InfluencerProfile(
            user_profile=user_profile,
            brand_name=influencer_data.get("brand_name"),
            platforms=[Platform(p) for p in influencer_data.get("platforms", []) if p in [e.value for e in Platform]]
        )

__all__ = ['InfluencerModel', 'InfluencerProfile', 'Campaign', 'Platform']