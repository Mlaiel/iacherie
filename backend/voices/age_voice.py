"""Age Voice Generator - Advanced Age-Specific Voice Synthesis

Generates age-appropriate voices with realistic aging effects,
developmental characteristics, and age-related voice changes.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
import random
from datetime import datetime

# Import existing infrastructure
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.i18n.voice_localization import VoiceProfile, VoiceAge, VoiceGender
from .voice_bank import VoiceBank, EnhancedVoiceProfile

logger = logging.getLogger(__name__)


class AgeCategory(Enum):
    """Detailed age categories for voice generation"""
    INFANT = "infant"           # 0-2 years
    TODDLER = "toddler"         # 2-4 years
    PRESCHOOL = "preschool"     # 4-6 years
    CHILD = "child"             # 6-12 years
    TEENAGER = "teenager"       # 12-18 years
    YOUNG_ADULT = "young_adult" # 18-30 years
    ADULT = "adult"             # 30-50 years
    MIDDLE_AGED = "middle_aged" # 50-65 years
    SENIOR = "senior"           # 65-80 years
    ELDERLY = "elderly"         # 80+ years


class VoiceMaturity(Enum):
    """Voice maturity levels"""
    DEVELOPING = "developing"
    JUVENILE = "juvenile"
    MATURE = "mature"
    DECLINING = "declining"


class AgeTransitionType(Enum):
    """Age transition types"""
    NATURAL = "natural"
    ACCELERATED = "accelerated"
    GRADUAL = "gradual"
    DRAMATIC = "dramatic"


@dataclass
class AgeProfile:
    """Comprehensive age profile for voice characteristics"""
    age_id: str
    category: AgeCategory
    age_range: Tuple[int, int]
    maturity: VoiceMaturity
    
    # Physical characteristics
    fundamental_frequency_range: Tuple[float, float]
    formant_frequencies: List[float]
    vocal_tract_length: float
    lung_capacity: float
    articulation_precision: float
    
    # Voice quality characteristics
    voice_stability: float
    vocal_strength: float
    breathiness: float
    roughness: float
    tremor: float
    hoarseness: float
    
    # Speech characteristics
    speech_rate: float
    pause_frequency: float
    articulation_clarity: float
    pronunciation_accuracy: float
    vocabulary_complexity: float
    
    # Prosodic characteristics
    intonation_variability: float
    stress_patterns: Dict[str, float]
    rhythm_regularity: float
    pitch_range: float
    
    # Cognitive and linguistic
    cognitive_processing_speed: float
    linguistic_complexity: float
    semantic_fluency: float
    pragmatic_competence: float
    
    # Emotional characteristics
    emotional_expression_range: float
    emotional_control: float
    spontaneity: float
    
    description: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class AgeTransformation:
    """Age transformation parameters"""
    source_age: AgeCategory
    target_age: AgeCategory
    transition_type: AgeTransitionType
    preservation_aspects: List[str]
    transformation_intensity: float
    quality_retention: float


class AgeVoiceGenerator:
    """Advanced age-specific voice generation system"""
    
    def __init__(self):
        self.age_profiles: Dict[str, AgeProfile] = {}
        self.gender_modifiers: Dict[VoiceGender, Dict[str, float]] = {}
        self.transformation_cache: Dict[str, AgeTransformation] = {}
        self.voice_bank: Optional[VoiceBank] = None
        
        # Initialize age profiles
        self._initialize_age_profiles()
        self._initialize_gender_modifiers()
        
        logger.info(f"Age voice generator initialized with {len(self.age_profiles)} age profiles")
    
    def _initialize_age_profiles(self):
        """Initialize comprehensive age profiles"""
        
        # Infant (0-2 years)
        self.age_profiles["infant"] = AgeProfile(
            age_id="infant",
            category=AgeCategory.INFANT,
            age_range=(0, 2),
            maturity=VoiceMaturity.DEVELOPING,
            fundamental_frequency_range=(300.0, 600.0),
            formant_frequencies=[1100, 3300, 4900],
            vocal_tract_length=6.5,
            lung_capacity=0.2,
            articulation_precision=0.1,
            voice_stability=0.3,
            vocal_strength=0.2,
            breathiness=0.8,
            roughness=0.1,
            tremor=0.2,
            hoarseness=0.1,
            speech_rate=0.3,
            pause_frequency=0.9,
            articulation_clarity=0.2,
            pronunciation_accuracy=0.1,
            vocabulary_complexity=0.1,
            intonation_variability=0.9,
            stress_patterns={"primary": 0.3, "secondary": 0.1},
            rhythm_regularity=0.2,
            pitch_range=2.5,
            cognitive_processing_speed=0.3,
            linguistic_complexity=0.1,
            semantic_fluency=0.1,
            pragmatic_competence=0.1,
            emotional_expression_range=0.9,
            emotional_control=0.1,
            spontaneity=0.9,
            description="Infant voice with high pitch, limited articulation, and developing speech patterns",
            tags=["infant", "baby", "developing", "high_pitch", "limited_vocabulary"]
        )
        
        # Toddler (2-4 years)
        self.age_profiles["toddler"] = AgeProfile(
            age_id="toddler",
            category=AgeCategory.TODDLER,
            age_range=(2, 4),
            maturity=VoiceMaturity.DEVELOPING,
            fundamental_frequency_range=(250.0, 500.0),
            formant_frequencies=[1000, 3000, 4500],
            vocal_tract_length=7.5,
            lung_capacity=0.3,
            articulation_precision=0.3,
            voice_stability=0.5,
            vocal_strength=0.4,
            breathiness=0.6,
            roughness=0.1,
            tremor=0.1,
            hoarseness=0.1,
            speech_rate=0.5,
            pause_frequency=0.7,
            articulation_clarity=0.4,
            pronunciation_accuracy=0.3,
            vocabulary_complexity=0.3,
            intonation_variability=0.8,
            stress_patterns={"primary": 0.5, "secondary": 0.2},
            rhythm_regularity=0.4,
            pitch_range=2.0,
            cognitive_processing_speed=0.5,
            linguistic_complexity=0.3,
            semantic_fluency=0.3,
            pragmatic_competence=0.3,
            emotional_expression_range=0.9,
            emotional_control=0.3,
            spontaneity=0.8,
            description="Toddler voice with developing articulation and expanding vocabulary",
            tags=["toddler", "child", "developing", "learning", "expressive"]
        )
        
        # Preschool (4-6 years)
        self.age_profiles["preschool"] = AgeProfile(
            age_id="preschool",
            category=AgeCategory.PRESCHOOL,
            age_range=(4, 6),
            maturity=VoiceMaturity.DEVELOPING,
            fundamental_frequency_range=(220.0, 450.0),
            formant_frequencies=[950, 2800, 4200],
            vocal_tract_length=8.5,
            lung_capacity=0.4,
            articulation_precision=0.5,
            voice_stability=0.6,
            vocal_strength=0.5,
            breathiness=0.4,
            roughness=0.1,
            tremor=0.1,
            hoarseness=0.1,
            speech_rate=0.6,
            pause_frequency=0.6,
            articulation_clarity=0.6,
            pronunciation_accuracy=0.5,
            vocabulary_complexity=0.5,
            intonation_variability=0.7,
            stress_patterns={"primary": 0.6, "secondary": 0.3},
            rhythm_regularity=0.5,
            pitch_range=1.8,
            cognitive_processing_speed=0.6,
            linguistic_complexity=0.5,
            semantic_fluency=0.5,
            pragmatic_competence=0.5,
            emotional_expression_range=0.8,
            emotional_control=0.4,
            spontaneity=0.7,
            description="Preschool voice with improving articulation and growing language skills",
            tags=["preschool", "child", "learning", "articulate", "curious"]
        )
        
        # Child (6-12 years)
        self.age_profiles["child"] = AgeProfile(
            age_id="child",
            category=AgeCategory.CHILD,
            age_range=(6, 12),
            maturity=VoiceMaturity.JUVENILE,
            fundamental_frequency_range=(200.0, 400.0),
            formant_frequencies=[900, 2600, 4000],
            vocal_tract_length=10.0,
            lung_capacity=0.6,
            articulation_precision=0.7,
            voice_stability=0.7,
            vocal_strength=0.6,
            breathiness=0.3,
            roughness=0.1,
            tremor=0.05,
            hoarseness=0.05,
            speech_rate=0.7,
            pause_frequency=0.5,
            articulation_clarity=0.7,
            pronunciation_accuracy=0.7,
            vocabulary_complexity=0.7,
            intonation_variability=0.6,
            stress_patterns={"primary": 0.7, "secondary": 0.4},
            rhythm_regularity=0.6,
            pitch_range=1.6,
            cognitive_processing_speed=0.7,
            linguistic_complexity=0.7,
            semantic_fluency=0.7,
            pragmatic_competence=0.6,
            emotional_expression_range=0.8,
            emotional_control=0.5,
            spontaneity=0.7,
            description="Child voice with clear articulation and developing complexity",
            tags=["child", "clear", "energetic", "developing", "playful"]
        )
        
        # Teenager (12-18 years)
        self.age_profiles["teenager"] = AgeProfile(
            age_id="teenager",
            category=AgeCategory.TEENAGER,
            age_range=(12, 18),
            maturity=VoiceMaturity.DEVELOPING,
            fundamental_frequency_range=(150.0, 350.0),
            formant_frequencies=[850, 2400, 3800],
            vocal_tract_length=12.0,
            lung_capacity=0.8,
            articulation_precision=0.8,
            voice_stability=0.6,  # Voice changes during puberty
            vocal_strength=0.7,
            breathiness=0.2,
            roughness=0.2,  # Voice breaking
            tremor=0.1,
            hoarseness=0.2,
            speech_rate=0.8,
            pause_frequency=0.4,
            articulation_clarity=0.8,
            pronunciation_accuracy=0.8,
            vocabulary_complexity=0.8,
            intonation_variability=0.7,
            stress_patterns={"primary": 0.8, "secondary": 0.5},
            rhythm_regularity=0.7,
            pitch_range=1.5,
            cognitive_processing_speed=0.8,
            linguistic_complexity=0.8,
            semantic_fluency=0.8,
            pragmatic_competence=0.7,
            emotional_expression_range=0.9,
            emotional_control=0.6,
            spontaneity=0.8,
            description="Teenager voice with puberty-related changes and emotional expressiveness",
            tags=["teenager", "adolescent", "changing", "expressive", "energetic"]
        )
        
        # Young Adult (18-30 years)
        self.age_profiles["young_adult"] = AgeProfile(
            age_id="young_adult",
            category=AgeCategory.YOUNG_ADULT,
            age_range=(18, 30),
            maturity=VoiceMaturity.MATURE,
            fundamental_frequency_range=(120.0, 280.0),
            formant_frequencies=[800, 2200, 3600],
            vocal_tract_length=14.0,
            lung_capacity=1.0,
            articulation_precision=0.9,
            voice_stability=0.9,
            vocal_strength=0.9,
            breathiness=0.1,
            roughness=0.05,
            tremor=0.02,
            hoarseness=0.05,
            speech_rate=1.0,
            pause_frequency=0.3,
            articulation_clarity=0.9,
            pronunciation_accuracy=0.9,
            vocabulary_complexity=0.9,
            intonation_variability=0.6,
            stress_patterns={"primary": 0.9, "secondary": 0.6},
            rhythm_regularity=0.8,
            pitch_range=1.4,
            cognitive_processing_speed=1.0,
            linguistic_complexity=0.9,
            semantic_fluency=0.9,
            pragmatic_competence=0.8,
            emotional_expression_range=0.8,
            emotional_control=0.7,
            spontaneity=0.6,
            description="Young adult voice at peak vocal development and clarity",
            tags=["young_adult", "mature", "clear", "strong", "confident"]
        )
        
        # Adult (30-50 years)
        self.age_profiles["adult"] = AgeProfile(
            age_id="adult",
            category=AgeCategory.ADULT,
            age_range=(30, 50),
            maturity=VoiceMaturity.MATURE,
            fundamental_frequency_range=(110.0, 260.0),
            formant_frequencies=[780, 2100, 3500],
            vocal_tract_length=14.5,
            lung_capacity=0.95,
            articulation_precision=0.95,
            voice_stability=0.95,
            vocal_strength=0.9,
            breathiness=0.1,
            roughness=0.05,
            tremor=0.02,
            hoarseness=0.05,
            speech_rate=1.0,
            pause_frequency=0.3,
            articulation_clarity=0.95,
            pronunciation_accuracy=0.95,
            vocabulary_complexity=1.0,
            intonation_variability=0.5,
            stress_patterns={"primary": 0.95, "secondary": 0.7},
            rhythm_regularity=0.9,
            pitch_range=1.3,
            cognitive_processing_speed=0.95,
            linguistic_complexity=1.0,
            semantic_fluency=1.0,
            pragmatic_competence=0.9,
            emotional_expression_range=0.7,
            emotional_control=0.8,
            spontaneity=0.5,
            description="Adult voice with peak linguistic competence and stable characteristics",
            tags=["adult", "mature", "professional", "stable", "experienced"]
        )
        
        # Middle-aged (50-65 years)
        self.age_profiles["middle_aged"] = AgeProfile(
            age_id="middle_aged",
            category=AgeCategory.MIDDLE_AGED,
            age_range=(50, 65),
            maturity=VoiceMaturity.MATURE,
            fundamental_frequency_range=(105.0, 250.0),
            formant_frequencies=[770, 2050, 3400],
            vocal_tract_length=14.8,
            lung_capacity=0.9,
            articulation_precision=0.9,
            voice_stability=0.9,
            vocal_strength=0.85,
            breathiness=0.15,
            roughness=0.1,
            tremor=0.05,
            hoarseness=0.1,
            speech_rate=0.95,
            pause_frequency=0.35,
            articulation_clarity=0.9,
            pronunciation_accuracy=0.95,
            vocabulary_complexity=1.0,
            intonation_variability=0.45,
            stress_patterns={"primary": 0.9, "secondary": 0.7},
            rhythm_regularity=0.85,
            pitch_range=1.2,
            cognitive_processing_speed=0.9,
            linguistic_complexity=1.0,
            semantic_fluency=1.0,
            pragmatic_competence=0.95,
            emotional_expression_range=0.6,
            emotional_control=0.9,
            spontaneity=0.4,
            description="Middle-aged voice with wisdom and slight aging characteristics",
            tags=["middle_aged", "experienced", "wise", "stable", "authoritative"]
        )
        
        # Senior (65-80 years)
        self.age_profiles["senior"] = AgeProfile(
            age_id="senior",
            category=AgeCategory.SENIOR,
            age_range=(65, 80),
            maturity=VoiceMaturity.DECLINING,
            fundamental_frequency_range=(100.0, 240.0),
            formant_frequencies=[760, 2000, 3300],
            vocal_tract_length=15.0,
            lung_capacity=0.8,
            articulation_precision=0.85,
            voice_stability=0.8,
            vocal_strength=0.75,
            breathiness=0.25,
            roughness=0.15,
            tremor=0.1,
            hoarseness=0.15,
            speech_rate=0.85,
            pause_frequency=0.4,
            articulation_clarity=0.85,
            pronunciation_accuracy=0.9,
            vocabulary_complexity=1.0,
            intonation_variability=0.4,
            stress_patterns={"primary": 0.85, "secondary": 0.6},
            rhythm_regularity=0.8,
            pitch_range=1.1,
            cognitive_processing_speed=0.85,
            linguistic_complexity=1.0,
            semantic_fluency=0.95,
            pragmatic_competence=1.0,
            emotional_expression_range=0.5,
            emotional_control=0.95,
            spontaneity=0.3,
            description="Senior voice with accumulated wisdom and age-related changes",
            tags=["senior", "wise", "experienced", "gentle", "thoughtful"]
        )
        
        # Elderly (80+ years)
        self.age_profiles["elderly"] = AgeProfile(
            age_id="elderly",
            category=AgeCategory.ELDERLY,
            age_range=(80, 100),
            maturity=VoiceMaturity.DECLINING,
            fundamental_frequency_range=(95.0, 230.0),
            formant_frequencies=[750, 1950, 3200],
            vocal_tract_length=15.2,
            lung_capacity=0.7,
            articulation_precision=0.75,
            voice_stability=0.7,
            vocal_strength=0.65,
            breathiness=0.35,
            roughness=0.2,
            tremor=0.2,
            hoarseness=0.2,
            speech_rate=0.75,
            pause_frequency=0.5,
            articulation_clarity=0.8,
            pronunciation_accuracy=0.85,
            vocabulary_complexity=1.0,
            intonation_variability=0.35,
            stress_patterns={"primary": 0.8, "secondary": 0.5},
            rhythm_regularity=0.75,
            pitch_range=1.0,
            cognitive_processing_speed=0.75,
            linguistic_complexity=0.95,
            semantic_fluency=0.9,
            pragmatic_competence=1.0,
            emotional_expression_range=0.4,
            emotional_control=1.0,
            spontaneity=0.2,
            description="Elderly voice with lifetime wisdom and significant aging characteristics",
            tags=["elderly", "wise", "gentle", "slow", "thoughtful"]
        )
    
    def _initialize_gender_modifiers(self):
        """Initialize gender-specific modifiers for age profiles"""
        
        self.gender_modifiers[VoiceGender.MALE] = {
            "fundamental_frequency_multiplier": 0.7,
            "formant_shift": -0.1,
            "vocal_tract_length_multiplier": 1.15,
            "lung_capacity_multiplier": 1.2,
            "vocal_strength_multiplier": 1.1,
            "roughness_tendency": 0.1,
            "breathiness_reduction": -0.05
        }
        
        self.gender_modifiers[VoiceGender.FEMALE] = {
            "fundamental_frequency_multiplier": 1.3,
            "formant_shift": 0.1,
            "vocal_tract_length_multiplier": 0.9,
            "lung_capacity_multiplier": 0.85,
            "vocal_strength_multiplier": 0.9,
            "roughness_tendency": -0.05,
            "breathiness_tendency": 0.05
        }
        
        self.gender_modifiers[VoiceGender.NEUTRAL] = {
            "fundamental_frequency_multiplier": 1.0,
            "formant_shift": 0.0,
            "vocal_tract_length_multiplier": 1.0,
            "lung_capacity_multiplier": 1.0,
            "vocal_strength_multiplier": 1.0,
            "roughness_tendency": 0.0,
            "breathiness_tendency": 0.0
        }
    
    def get_age_profile(self, age_id: str) -> Optional[AgeProfile]:
        """Get age profile by ID"""
        return self.age_profiles.get(age_id)
    
    def get_age_profile_by_category(self, category: AgeCategory) -> Optional[AgeProfile]:
        """Get age profile by category"""
        for profile in self.age_profiles.values():
            if profile.category == category:
                return profile
        return None
    
    def get_age_profile_by_age(self, age: int) -> Optional[AgeProfile]:
        """Get appropriate age profile for specific age"""
        for profile in self.age_profiles.values():
            min_age, max_age = profile.age_range
            if min_age <= age <= max_age:
                return profile
        return None
    
    def search_age_profiles(
        self,
        category: Optional[AgeCategory] = None,
        maturity: Optional[VoiceMaturity] = None,
        age_range: Optional[Tuple[int, int]] = None,
        min_stability: Optional[float] = None,
        max_breathiness: Optional[float] = None,
        limit: int = 20
    ) -> List[AgeProfile]:
        """Search age profiles with filters"""
        results = []
        
        for profile in self.age_profiles.values():
            # Category filter
            if category and profile.category != category:
                continue
            
            # Maturity filter
            if maturity and profile.maturity != maturity:
                continue
            
            # Age range filter
            if age_range:
                req_min, req_max = age_range
                prof_min, prof_max = profile.age_range
                if not (prof_min <= req_max and prof_max >= req_min):
                    continue
            
            # Stability filter
            if min_stability and profile.voice_stability < min_stability:
                continue
            
            # Breathiness filter
            if max_breathiness and profile.breathiness > max_breathiness:
                continue
            
            results.append(profile)
        
        return results[:limit]
    
    async def apply_age_to_voice(
        self,
        voice_profile: VoiceProfile,
        target_age: AgeCategory,
        target_gender: Optional[VoiceGender] = None,
        preserve_identity: bool = True
    ) -> Optional[VoiceProfile]:
        """Apply age transformation to voice profile"""
        
        age_profile = self.get_age_profile_by_category(target_age)
        if not age_profile:
            logger.error(f"Age profile not found: {target_age}")
            return None
        
        # Use target gender or keep original
        gender = target_gender or voice_profile.gender
        
        # Create age-modified voice profile
        modified_profile = VoiceProfile(
            voice_id=f"{voice_profile.voice_id}_age_{target_age.value}_{gender.value}",
            name=f"{voice_profile.name} ({age_profile.description})",
            language_code=voice_profile.language_code,
            region=voice_profile.region,
            gender=gender,
            age=self._map_age_category_to_voice_age(target_age),
            accent=voice_profile.accent,
            accent_region=voice_profile.accent_region,
            supported_emotions=voice_profile.supported_emotions,
            supported_styles=voice_profile.supported_styles,
            sample_rate=voice_profile.sample_rate,
            voice_characteristics=self._apply_age_characteristics(
                voice_profile.voice_characteristics,
                age_profile,
                gender,
                preserve_identity
            ),
            cultural_context=voice_profile.cultural_context,
            pronunciation_rules=self._apply_age_pronunciation_rules(
                voice_profile.pronunciation_rules,
                age_profile
            ),
            prosody_patterns=self._apply_age_prosody(
                voice_profile.prosody_patterns,
                age_profile
            ),
            quality_score=voice_profile.quality_score * age_profile.voice_stability
        )
        
        return modified_profile
    
    def _apply_age_characteristics(
        self,
        base_characteristics: Dict[str, float],
        age_profile: AgeProfile,
        gender: VoiceGender,
        preserve_identity: bool
    ) -> Dict[str, float]:
        """Apply age and gender modifications to voice characteristics"""
        
        modified = base_characteristics.copy()
        gender_mods = self.gender_modifiers.get(gender, self.gender_modifiers[VoiceGender.NEUTRAL])
        
        # Identity preservation factor
        preservation_factor = 0.6 if preserve_identity else 0.2
        age_factor = 1.0 - preservation_factor
        
        # Apply fundamental frequency changes
        base_pitch = modified.get("pitch", 200.0)
        age_f0_min, age_f0_max = age_profile.fundamental_frequency_range
        age_f0_target = (age_f0_min + age_f0_max) / 2
        
        # Apply gender modifier to age target
        age_f0_target *= gender_mods["fundamental_frequency_multiplier"]
        
        modified["pitch"] = base_pitch * preservation_factor + age_f0_target * age_factor
        
        # Apply speech rate changes
        base_speed = modified.get("speed", 1.0)
        age_speed = base_speed * age_profile.speech_rate
        modified["speed"] = base_speed * preservation_factor + age_speed * age_factor
        
        # Apply volume/strength changes
        base_volume = modified.get("volume", 1.0)
        age_volume = base_volume * age_profile.vocal_strength * gender_mods["vocal_strength_multiplier"]
        modified["volume"] = base_volume * preservation_factor + age_volume * age_factor
        
        # Apply tone modifications
        base_tone = modified.get("tone", 0.5)
        age_tone = base_tone * (1.0 - age_profile.breathiness)
        modified["tone"] = base_tone * preservation_factor + age_tone * age_factor
        
        # Add age-specific voice qualities
        modified["breathiness"] = age_profile.breathiness + gender_mods.get("breathiness_tendency", 0.0)
        modified["roughness"] = age_profile.roughness + gender_mods.get("roughness_tendency", 0.0)
        modified["tremor"] = age_profile.tremor
        modified["hoarseness"] = age_profile.hoarseness
        modified["voice_stability"] = age_profile.voice_stability
        modified["articulation_clarity"] = age_profile.articulation_clarity
        
        # Age and gender specific adjustments
        modified["vocal_tract_length"] = age_profile.vocal_tract_length * gender_mods["vocal_tract_length_multiplier"]
        modified["lung_capacity"] = age_profile.lung_capacity * gender_mods["lung_capacity_multiplier"]
        modified["articulation_precision"] = age_profile.articulation_precision
        
        # Cognitive and linguistic characteristics
        modified["cognitive_speed"] = age_profile.cognitive_processing_speed
        modified["linguistic_complexity"] = age_profile.linguistic_complexity
        modified["vocabulary_complexity"] = age_profile.vocabulary_complexity
        
        return modified
    
    def _apply_age_pronunciation_rules(
        self,
        base_rules: Dict[str, str],
        age_profile: AgeProfile
    ) -> Dict[str, str]:
        """Apply age-specific pronunciation rules"""
        
        modified_rules = base_rules.copy()
        
        # Age-specific pronunciation patterns
        if age_profile.category in [AgeCategory.INFANT, AgeCategory.TODDLER]:
            # Simplified consonant clusters
            modified_rules.update({
                "consonant_clusters": "simplified",
                "r_sound": "w_substitution",
                "th_sound": "f_substitution",
                "final_consonants": "deleted"
            })
        
        elif age_profile.category == AgeCategory.PRESCHOOL:
            # Developing pronunciation
            modified_rules.update({
                "r_sound": "partial_development",
                "th_sound": "inconsistent",
                "complex_clusters": "simplified"
            })
        
        elif age_profile.category == AgeCategory.CHILD:
            # Near-adult pronunciation with some variations
            modified_rules.update({
                "pronunciation_consistency": "high",
                "articulation_effort": "conscious"
            })
        
        elif age_profile.category == AgeCategory.TEENAGER:
            # Adult pronunciation with voice changes
            modified_rules.update({
                "voice_breaks": "occasional",
                "pitch_instability": "present"
            })
        
        elif age_profile.category in [AgeCategory.SENIOR, AgeCategory.ELDERLY]:
            # Age-related pronunciation changes
            modified_rules.update({
                "articulation_precision": "reduced",
                "consonant_weakening": "present",
                "dental_considerations": "possible"
            })
        
        return modified_rules
    
    def _apply_age_prosody(
        self,
        base_prosody: Dict[str, Any],
        age_profile: AgeProfile
    ) -> Dict[str, Any]:
        """Apply age-specific prosody patterns"""
        
        modified = base_prosody.copy()
        
        # Apply stress patterns
        if "stress" not in modified:
            modified["stress"] = {}
        modified["stress"].update(age_profile.stress_patterns)
        
        # Apply intonation characteristics
        if "intonation" not in modified:
            modified["intonation"] = {}
        modified["intonation"]["variability"] = age_profile.intonation_variability
        modified["intonation"]["pitch_range"] = age_profile.pitch_range
        
        # Apply rhythm characteristics
        if "rhythm" not in modified:
            modified["rhythm"] = {}
        modified["rhythm"]["regularity"] = age_profile.rhythm_regularity
        modified["rhythm"]["speech_rate"] = age_profile.speech_rate
        
        # Apply pause patterns
        if "pauses" not in modified:
            modified["pauses"] = {}
        modified["pauses"]["frequency"] = age_profile.pause_frequency
        modified["pauses"]["cognitive_processing"] = 1.0 - age_profile.cognitive_processing_speed
        
        return modified
    
    def _map_age_category_to_voice_age(self, category: AgeCategory) -> VoiceAge:
        """Map AgeCategory to VoiceAge enum"""
        mapping = {
            AgeCategory.INFANT: VoiceAge.CHILD,
            AgeCategory.TODDLER: VoiceAge.CHILD,
            AgeCategory.PRESCHOOL: VoiceAge.CHILD,
            AgeCategory.CHILD: VoiceAge.CHILD,
            AgeCategory.TEENAGER: VoiceAge.YOUNG_ADULT,
            AgeCategory.YOUNG_ADULT: VoiceAge.YOUNG_ADULT,
            AgeCategory.ADULT: VoiceAge.ADULT,
            AgeCategory.MIDDLE_AGED: VoiceAge.MIDDLE_AGED,
            AgeCategory.SENIOR: VoiceAge.ELDERLY,
            AgeCategory.ELDERLY: VoiceAge.ELDERLY
        }
        return mapping.get(category, VoiceAge.ADULT)
    
    async def create_age_progression(
        self,
        voice_profile: VoiceProfile,
        start_age: AgeCategory,
        end_age: AgeCategory,
        steps: int = 10
    ) -> List[VoiceProfile]:
        """Create age progression from one age to another"""
        
        start_profile = self.get_age_profile_by_category(start_age)
        end_profile = self.get_age_profile_by_category(end_age)
        
        if not start_profile or not end_profile:
            logger.error("Start or end age profile not found")
            return []
        
        progression_voices = []
        
        for i in range(steps + 1):
            # Calculate interpolation factor
            factor = i / steps
            
            # Interpolate age characteristics
            interpolated_age = self._interpolate_age_profiles(
                start_profile, end_profile, factor
            )
            
            # Apply to voice
            aged_voice = await self.apply_interpolated_age_to_voice(
                voice_profile, interpolated_age, i
            )
            
            if aged_voice:
                progression_voices.append(aged_voice)
        
        return progression_voices
    
    def _interpolate_age_profiles(
        self,
        start_age: AgeProfile,
        end_age: AgeProfile,
        factor: float
    ) -> AgeProfile:
        """Interpolate between two age profiles"""
        
        # Calculate interpolated fundamental frequency range
        start_f0_min, start_f0_max = start_age.fundamental_frequency_range
        end_f0_min, end_f0_max = end_age.fundamental_frequency_range
        
        interp_f0_min = start_f0_min * (1 - factor) + end_f0_min * factor
        interp_f0_max = start_f0_max * (1 - factor) + end_f0_max * factor
        
        # Interpolate formant frequencies
        interp_formants = []
        for start_f, end_f in zip(start_age.formant_frequencies, end_age.formant_frequencies):
            interp_formants.append(start_f * (1 - factor) + end_f * factor)
        
        return AgeProfile(
            age_id=f"interpolated_{start_age.age_id}_to_{end_age.age_id}_{factor:.2f}",
            category=end_age.category if factor > 0.5 else start_age.category,
            age_range=(
                int(start_age.age_range[0] * (1 - factor) + end_age.age_range[0] * factor),
                int(start_age.age_range[1] * (1 - factor) + end_age.age_range[1] * factor)
            ),
            maturity=end_age.maturity if factor > 0.5 else start_age.maturity,
            fundamental_frequency_range=(interp_f0_min, interp_f0_max),
            formant_frequencies=interp_formants,
            vocal_tract_length=start_age.vocal_tract_length * (1 - factor) + end_age.vocal_tract_length * factor,
            lung_capacity=start_age.lung_capacity * (1 - factor) + end_age.lung_capacity * factor,
            articulation_precision=start_age.articulation_precision * (1 - factor) + end_age.articulation_precision * factor,
            voice_stability=start_age.voice_stability * (1 - factor) + end_age.voice_stability * factor,
            vocal_strength=start_age.vocal_strength * (1 - factor) + end_age.vocal_strength * factor,
            breathiness=start_age.breathiness * (1 - factor) + end_age.breathiness * factor,
            roughness=start_age.roughness * (1 - factor) + end_age.roughness * factor,
            tremor=start_age.tremor * (1 - factor) + end_age.tremor * factor,
            hoarseness=start_age.hoarseness * (1 - factor) + end_age.hoarseness * factor,
            speech_rate=start_age.speech_rate * (1 - factor) + end_age.speech_rate * factor,
            pause_frequency=start_age.pause_frequency * (1 - factor) + end_age.pause_frequency * factor,
            articulation_clarity=start_age.articulation_clarity * (1 - factor) + end_age.articulation_clarity * factor,
            pronunciation_accuracy=start_age.pronunciation_accuracy * (1 - factor) + end_age.pronunciation_accuracy * factor,
            vocabulary_complexity=start_age.vocabulary_complexity * (1 - factor) + end_age.vocabulary_complexity * factor,
            intonation_variability=start_age.intonation_variability * (1 - factor) + end_age.intonation_variability * factor,
            stress_patterns=self._interpolate_dict(start_age.stress_patterns, end_age.stress_patterns, factor),
            rhythm_regularity=start_age.rhythm_regularity * (1 - factor) + end_age.rhythm_regularity * factor,
            pitch_range=start_age.pitch_range * (1 - factor) + end_age.pitch_range * factor,
            cognitive_processing_speed=start_age.cognitive_processing_speed * (1 - factor) + end_age.cognitive_processing_speed * factor,
            linguistic_complexity=start_age.linguistic_complexity * (1 - factor) + end_age.linguistic_complexity * factor,
            semantic_fluency=start_age.semantic_fluency * (1 - factor) + end_age.semantic_fluency * factor,
            pragmatic_competence=start_age.pragmatic_competence * (1 - factor) + end_age.pragmatic_competence * factor,
            emotional_expression_range=start_age.emotional_expression_range * (1 - factor) + end_age.emotional_expression_range * factor,
            emotional_control=start_age.emotional_control * (1 - factor) + end_age.emotional_control * factor,
            spontaneity=start_age.spontaneity * (1 - factor) + end_age.spontaneity * factor,
            description=f"Age progression from {start_age.description} to {end_age.description}",
            tags=list(set(start_age.tags + end_age.tags))
        )
    
    def _interpolate_dict(self, dict1: Dict[str, float], dict2: Dict[str, float], factor: float) -> Dict[str, float]:
        """Interpolate between two dictionaries"""
        result = {}
        all_keys = set(dict1.keys()) | set(dict2.keys())
        
        for key in all_keys:
            val1 = dict1.get(key, 0.0)
            val2 = dict2.get(key, 0.0)
            result[key] = val1 * (1 - factor) + val2 * factor
        
        return result
    
    async def apply_interpolated_age_to_voice(
        self,
        voice_profile: VoiceProfile,
        age_profile: AgeProfile,
        step: int
    ) -> Optional[VoiceProfile]:
        """Apply interpolated age profile to voice"""
        
        modified_profile = VoiceProfile(
            voice_id=f"{voice_profile.voice_id}_age_progression_step_{step}",
            name=f"{voice_profile.name} ({age_profile.description})",
            language_code=voice_profile.language_code,
            region=voice_profile.region,
            gender=voice_profile.gender,
            age=self._map_age_category_to_voice_age(age_profile.category),
            accent=voice_profile.accent,
            accent_region=voice_profile.accent_region,
            supported_emotions=voice_profile.supported_emotions,
            supported_styles=voice_profile.supported_styles,
            sample_rate=voice_profile.sample_rate,
            voice_characteristics=self._apply_age_characteristics(
                voice_profile.voice_characteristics,
                age_profile,
                voice_profile.gender,
                preserve_identity=True
            ),
            cultural_context=voice_profile.cultural_context,
            pronunciation_rules=self._apply_age_pronunciation_rules(
                voice_profile.pronunciation_rules,
                age_profile
            ),
            prosody_patterns=self._apply_age_prosody(
                voice_profile.prosody_patterns,
                age_profile
            ),
            quality_score=voice_profile.quality_score * age_profile.voice_stability
        )
        
        return modified_profile
    
    async def generate_family_voices(
        self,
        base_voice_profile: VoiceProfile,
        family_ages: List[AgeCategory],
        preserve_family_traits: bool = True
    ) -> List[VoiceProfile]:
        """Generate family member voices with shared characteristics"""
        
        family_voices = []
        
        for age_category in family_ages:
            family_voice = await self.apply_age_to_voice(
                base_voice_profile,
                age_category,
                preserve_identity=preserve_family_traits
            )
            
            if family_voice:
                # Add family resemblance markers
                family_voice.voice_id = f"{base_voice_profile.voice_id}_family_{age_category.value}"
                family_voice.name = f"Family {age_category.value.title()} - {base_voice_profile.name}"
                
                family_voices.append(family_voice)
        
        return family_voices
    
    def get_age_statistics(self) -> Dict[str, Any]:
        """Get age profile statistics"""
        categories = {}
        maturities = {}
        
        for profile in self.age_profiles.values():
            # Category stats
            cat_name = profile.category.value
            if cat_name not in categories:
                categories[cat_name] = 0
            categories[cat_name] += 1
            
            # Maturity stats
            mat_name = profile.maturity.value
            if mat_name not in maturities:
                maturities[mat_name] = 0
            maturities[mat_name] += 1
        
        avg_stability = sum(p.voice_stability for p in self.age_profiles.values()) / len(self.age_profiles)
        avg_strength = sum(p.vocal_strength for p in self.age_profiles.values()) / len(self.age_profiles)
        avg_clarity = sum(p.articulation_clarity for p in self.age_profiles.values()) / len(self.age_profiles)
        
        return {
            "total_age_profiles": len(self.age_profiles),
            "categories": categories,
            "maturities": maturities,
            "average_voice_stability": avg_stability,
            "average_vocal_strength": avg_strength,
            "average_articulation_clarity": avg_clarity,
            "age_range_coverage": {
                "min_age": min(p.age_range[0] for p in self.age_profiles.values()),
                "max_age": max(p.age_range[1] for p in self.age_profiles.values())
            }
        }
    
    def get_recommended_age_for_context(self, context: str) -> List[AgeCategory]:
        """Get recommended ages for specific contexts"""
        recommendations = {
            "children_content": [AgeCategory.CHILD, AgeCategory.TEENAGER],
            "educational": [AgeCategory.YOUNG_ADULT, AgeCategory.ADULT],
            "professional": [AgeCategory.ADULT, AgeCategory.MIDDLE_AGED],
            "storytelling": [AgeCategory.MIDDLE_AGED, AgeCategory.SENIOR],
            "family_friendly": [AgeCategory.YOUNG_ADULT, AgeCategory.ADULT],
            "authoritative": [AgeCategory.MIDDLE_AGED, AgeCategory.SENIOR],
            "friendly": [AgeCategory.YOUNG_ADULT, AgeCategory.ADULT],
            "wise": [AgeCategory.SENIOR, AgeCategory.ELDERLY],
            "energetic": [AgeCategory.TEENAGER, AgeCategory.YOUNG_ADULT],
            "calming": [AgeCategory.MIDDLE_AGED, AgeCategory.SENIOR]
        }
        
        return recommendations.get(context.lower(), [AgeCategory.ADULT])