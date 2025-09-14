"""😂 Comedian Model - Entertainment Creator Specialization
=======================================================
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import uuid

from .user_model import UserProfile, UserModel

class ComedyStyle(Enum):
    STANDUP = "standup"
    SKETCH = "sketch"
    IMPROV = "improv"
    SATIRE = "satire"
    OBSERVATIONAL = "observational"

@dataclass
class SketchSeries:
    id: str
    title: str
    comedian_id: str
    style: ComedyStyle
    episodes: int = 0
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

@dataclass
class ComedianProfile:
    user_profile: UserProfile
    stage_name: Optional[str] = None
    comedy_styles: List[ComedyStyle] = field(default_factory=list)
    series: List[SketchSeries] = field(default_factory=list)

class ComedianModel:
    @staticmethod
    def create_profile(user_data: Dict[str, Any]) -> ComedianProfile:
        user_profile = UserModel.create_profile(user_data)
        comedian_data = user_data.get("comedian_data", {})
        
        return ComedianProfile(
            user_profile=user_profile,
            stage_name=comedian_data.get("stage_name"),
            comedy_styles=[ComedyStyle(s) for s in comedian_data.get("comedy_styles", []) if s in [e.value for e in ComedyStyle]]
        )

__all__ = ['ComedianModel', 'ComedianProfile', 'SketchSeries', 'ComedyStyle']