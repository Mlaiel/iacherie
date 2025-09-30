"""🧠 Personality Model - AI-Driven Creator Personality Analysis
============================================================
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid

class PersonalityTrait(Enum):
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    SOCIAL = "social"
    DETAIL_ORIENTED = "detail_oriented"
    INNOVATIVE = "innovative"

@dataclass
class BehaviorPattern:
    trait: PersonalityTrait
    score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0

@dataclass
class PersonalityModel:
    user_id: str
    traits: List[BehaviorPattern] = field(default_factory=list)
    personality_type: Optional[str] = None
    
    @staticmethod
    def analyze_personality(user_data: Dict[str, Any]) -> 'PersonalityModel':
        """Analyze personality from user data"""
        user_id = user_data.get("id", str(uuid.uuid4()))
        
        # Simple personality analysis based on interests/skills
        traits = []
        interests = user_data.get("interests", [])
        skills = user_data.get("skills", [])
        
        # Basic trait scoring
        creative_score = 0.5
        if any(interest in ["art", "music", "design", "writing"] for interest in interests):
            creative_score = 0.8
        
        traits.append(BehaviorPattern(PersonalityTrait.CREATIVE, creative_score, 0.7))
        
        return PersonalityModel(
            user_id=user_id,
            traits=traits,
            personality_type="Creative"
        )

__all__ = ['PersonalityModel', 'PersonalityTrait', 'BehaviorPattern']