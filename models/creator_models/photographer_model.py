"""📸 Photographer Model - Visual Creator Specialization
====================================================
Module: models/creator_models/photographer_model.py
Author: Fahed Mlaiel (mlaiel@live.de)
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import uuid

from .user_model import UserProfile, UserModel

class PhotographyStyle(Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    WEDDING = "wedding"
    FASHION = "fashion"
    STREET = "street"
    NATURE = "nature"
    COMMERCIAL = "commercial"
    EVENT = "event"
    OTHER = "other"

@dataclass
class PhotoGallery:
    id: str
    title: str
    description: str
    photographer_id: str
    style: PhotographyStyle
    photos: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

@dataclass
class PhotographerProfile:
    user_profile: UserProfile
    portfolio_name: Optional[str] = None
    specializations: List[PhotographyStyle] = field(default_factory=list)
    equipment: List[str] = field(default_factory=list)
    galleries: List[PhotoGallery] = field(default_factory=list)
    
    def get_display_name(self) -> str:
        return self.portfolio_name or self.user_profile.display_name

class PhotographerModel:
    @staticmethod
    def create_profile(user_data: Dict[str, Any]) -> PhotographerProfile:
        user_profile = UserModel.create_profile(user_data)
        photographer_data = user_data.get("photographer_data", {})
        
        return PhotographerProfile(
            user_profile=user_profile,
            portfolio_name=photographer_data.get("portfolio_name"),
            specializations=[PhotographyStyle(s) for s in photographer_data.get("specializations", []) if s in [e.value for e in PhotographyStyle]],
            equipment=photographer_data.get("equipment", [])
        )

__all__ = ['PhotographerModel', 'PhotographerProfile', 'PhotoGallery', 'PhotographyStyle']