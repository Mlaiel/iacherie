"""📝 Blogger Model - Content Creator Specialization
==============================================
Module: models/creator_models/blogger_model.py
Author: Fahed Mlaiel (mlaiel@live.de)
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import uuid

from .user_model import UserProfile, UserModel

class BlogCategory(Enum):
    TECHNOLOGY = "technology"
    LIFESTYLE = "lifestyle"
    TRAVEL = "travel"
    FOOD = "food"
    FASHION = "fashion"
    BUSINESS = "business"
    HEALTH = "health"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    OTHER = "other"

@dataclass
class BlogPost:
    id: str
    title: str
    content: str
    author_id: str
    category: BlogCategory
    tags: List[str] = field(default_factory=list)
    published: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

@dataclass
class Category:
    id: str
    name: str
    description: str
    posts_count: int = 0

@dataclass
class BloggerProfile:
    user_profile: UserProfile
    blog_name: Optional[str] = None
    niche: List[BlogCategory] = field(default_factory=list)
    posts: List[BlogPost] = field(default_factory=list)
    
    def get_display_name(self) -> str:
        return self.blog_name or self.user_profile.display_name

class BloggerModel:
    @staticmethod
    def create_profile(user_data: Dict[str, Any]) -> BloggerProfile:
        user_profile = UserModel.create_profile(user_data)
        blogger_data = user_data.get("blogger_data", {})
        
        return BloggerProfile(
            user_profile=user_profile,
            blog_name=blogger_data.get("blog_name"),
            niche=[BlogCategory(n) for n in blogger_data.get("niche", []) if n in [e.value for e in BlogCategory]]
        )

__all__ = ['BloggerModel', 'BloggerProfile', 'BlogPost', 'Category', 'BlogCategory']