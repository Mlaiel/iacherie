"""Emotion Voice Generator - Advanced Emotional Voice Synthesis

Generates emotionally expressive voices with dynamic emotion control,
mood adaptation, and psychological voice modeling.

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

from core.i18n.voice_localization import VoiceProfile, VoiceEmotion
from backend.ai.conversational.intelligence_algorithms.emotional_intelligence_processor import EmotionType, SentimentLevel, MoodState
from .voice_bank import VoiceBank, EnhancedVoiceProfile

logger = logging.getLogger(__name__)


class EmotionIntensity(Enum):
    """Emotion intensity levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MILD = "mild"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    EXTREME = "extreme"


class EmotionDuration(Enum):
    """Emotion duration types"""
    MOMENTARY = "momentary"
    SHORT = "short"
    SUSTAINED = "sustained"
    LONG_TERM = "long_term"
    PERSISTENT = "persistent"


class EmotionTransition(Enum):
    """Emotion transition styles"""
    INSTANT = "instant"
    QUICK = "quick"
    GRADUAL = "gradual"
    SMOOTH = "smooth"
    DRAMATIC = "dramatic"


@dataclass
class EmotionProfile:
    """Comprehensive emotion profile for voice synthesis"""
    emotion_id: str
    primary_emotion: EmotionType
    secondary_emotions: List[EmotionType]
    intensity: EmotionIntensity
    valence: float  # -1.0 (negative) to +1.0 (positive)
    arousal: float  # 0.0 (calm) to 1.0 (excited)
    dominance: float  # 0.0 (submissive) to 1.0 (dominant)
    
    # Voice characteristics modifiers
    pitch_modifier: float
    speed_modifier: float
    volume_modifier: float
    tone_modifier: float
    breathiness: float
    vocal_fry: float
    tremor: float
    
    # Prosodic features
    stress_patterns: Dict[str, float]
    intonation_patterns: Dict[str, float]
    pause_patterns: Dict[str, float]
    rhythm_variations: Dict[str, float]
    
    # Cultural and contextual
    cultural_expression: Dict[str, float]
    contextual_appropriateness: Dict[str, float]
    
    description: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class EmotionTransformation:
    """Emotion transformation parameters"""
    source_emotion: EmotionType
    target_emotion: EmotionType
    transition_style: EmotionTransition
    duration: EmotionDuration
    intensity_curve: List[float]
    smoothing_factor: float
    preservation_aspects: List[str]


@dataclass
class EmotionalVoiceRequest:
    """Request for emotional voice generation"""
    base_voice_id: str
    target_emotion: EmotionType
    intensity: EmotionIntensity
    context: str = ""
    mood_state: Optional[MoodState] = None
    cultural_adaptation: bool = True
    preserve_identity: bool = True
    duration_hint: Optional[EmotionDuration] = None


class EmotionVoiceGenerator:
    """Advanced emotional voice synthesis system"""
    
    def __init__(self):
        self.emotion_profiles: Dict[str, EmotionProfile] = {}
        self.transformation_cache: Dict[str, EmotionTransformation] = {}
        self.voice_bank: Optional[VoiceBank] = None
        
        # Initialize emotion profiles
        self._initialize_emotion_profiles()
        
        logger.info(f"Emotion voice generator initialized with {len(self.emotion_profiles)} emotion profiles")
    
    def _initialize_emotion_profiles(self):
        """Initialize comprehensive emotion profiles"""
        
        # Primary emotions
        self._add_primary_emotions()
        
        # Secondary emotions
        self._add_secondary_emotions()
        
        # Complex emotions
        self._add_complex_emotions()
        
        # Cultural emotion variants
        self._add_cultural_variants()
        
        # Contextual emotions
        self._add_contextual_emotions()
    
    def _add_primary_emotions(self):
        """Add primary emotion profiles"""
        primary_emotions = [
            {
                "emotion_id": "joy_high",
                "primary_emotion": EmotionType.JOY,
                "intensity": EmotionIntensity.HIGH,
                "valence": 0.9,
                "arousal": 0.8,
                "dominance": 0.7,
                "pitch_modifier": 1.2,
                "speed_modifier": 1.1,
                "volume_modifier": 1.1,
                "description": "High-intensity joy with bright, animated expression"
            },
            {
                "emotion_id": "joy_moderate",
                "primary_emotion": EmotionType.JOY,
                "intensity": EmotionIntensity.MODERATE,
                "valence": 0.7,
                "arousal": 0.6,
                "dominance": 0.6,
                "pitch_modifier": 1.1,
                "speed_modifier": 1.05,
                "volume_modifier": 1.0,
                "description": "Moderate joy with warm, pleasant expression"
            },
            {
                "emotion_id": "sadness_high",
                "primary_emotion": EmotionType.SADNESS,
                "intensity": EmotionIntensity.HIGH,
                "valence": -0.8,
                "arousal": 0.3,
                "dominance": 0.2,
                "pitch_modifier": 0.85,
                "speed_modifier": 0.8,
                "volume_modifier": 0.7,
                "description": "Deep sadness with lowered, slower expression"
            },
            {
                "emotion_id": "sadness_mild",
                "primary_emotion": EmotionType.SADNESS,
                "intensity": EmotionIntensity.MILD,
                "valence": -0.4,
                "arousal": 0.4,
                "dominance": 0.4,
                "pitch_modifier": 0.95,
                "speed_modifier": 0.9,
                "volume_modifier": 0.9,
                "description": "Mild sadness with subtle melancholic tone"
            },
            {
                "emotion_id": "anger_high",
                "primary_emotion": EmotionType.ANGER,
                "intensity": EmotionIntensity.HIGH,
                "valence": -0.7,
                "arousal": 0.9,
                "dominance": 0.9,
                "pitch_modifier": 1.15,
                "speed_modifier": 1.2,
                "volume_modifier": 1.3,
                "description": "Intense anger with sharp, forceful expression"
            },
            {
                "emotion_id": "anger_moderate",
                "primary_emotion": EmotionType.ANGER,
                "intensity": EmotionIntensity.MODERATE,
                "valence": -0.5,
                "arousal": 0.7,
                "dominance": 0.7,
                "pitch_modifier": 1.08,
                "speed_modifier": 1.1,
                "volume_modifier": 1.1,
                "description": "Controlled anger with firm, assertive tone"
            },
            {
                "emotion_id": "fear_high",
                "primary_emotion": EmotionType.FEAR,
                "intensity": EmotionIntensity.HIGH,
                "valence": -0.6,
                "arousal": 0.9,
                "dominance": 0.1,
                "pitch_modifier": 1.3,
                "speed_modifier": 1.3,
                "volume_modifier": 0.8,
                "description": "Intense fear with trembling, rapid expression"
            },
            {
                "emotion_id": "fear_mild",
                "primary_emotion": EmotionType.FEAR,
                "intensity": EmotionIntensity.MILD,
                "valence": -0.3,
                "arousal": 0.6,
                "dominance": 0.3,
                "pitch_modifier": 1.1,
                "speed_modifier": 1.1,
                "volume_modifier": 0.9,
                "description": "Mild apprehension with cautious tone"
            },
            {
                "emotion_id": "surprise_high",
                "primary_emotion": EmotionType.SURPRISE,
                "intensity": EmotionIntensity.HIGH,
                "valence": 0.0,
                "arousal": 0.9,
                "dominance": 0.5,
                "pitch_modifier": 1.4,
                "speed_modifier": 0.7,
                "volume_modifier": 1.2,
                "description": "Strong surprise with sudden pitch changes"
            },
            {
                "emotion_id": "disgust_moderate",
                "primary_emotion": EmotionType.DISGUST,
                "intensity": EmotionIntensity.MODERATE,
                "valence": -0.6,
                "arousal": 0.5,
                "dominance": 0.6,
                "pitch_modifier": 0.9,
                "speed_modifier": 0.9,
                "volume_modifier": 0.8,
                "description": "Moderate disgust with restrained, dismissive tone"
            }
        ]
        
        for emotion_data in primary_emotions:
            profile = self._create_emotion_profile(emotion_data)
            self.emotion_profiles[profile.emotion_id] = profile
    
    def _add_secondary_emotions(self):
        """Add secondary emotion profiles"""
        secondary_emotions = [
            {
                "emotion_id": "excitement_high",
                "primary_emotion": EmotionType.EXCITEMENT,
                "intensity": EmotionIntensity.HIGH,
                "valence": 0.8,
                "arousal": 0.9,
                "dominance": 0.8,
                "pitch_modifier": 1.25,
                "speed_modifier": 1.2,
                "volume_modifier": 1.2,
                "description": "High excitement with energetic, vibrant expression"
            },
            {
                "emotion_id": "love_high",
                "primary_emotion": EmotionType.LOVE,
                "intensity": EmotionIntensity.HIGH,
                "valence": 0.9,
                "arousal": 0.7,
                "dominance": 0.5,
                "pitch_modifier": 1.1,
                "speed_modifier": 0.9,
                "volume_modifier": 0.9,
                "description": "Deep love with warm, tender expression"
            },
            {
                "emotion_id": "frustration_high",
                "primary_emotion": EmotionType.FRUSTRATION,
                "intensity": EmotionIntensity.HIGH,
                "valence": -0.6,
                "arousal": 0.8,
                "dominance": 0.4,
                "pitch_modifier": 1.1,
                "speed_modifier": 1.15,
                "volume_modifier": 1.1,
                "description": "High frustration with strained, tense expression"
            },
            {
                "emotion_id": "confusion_moderate",
                "primary_emotion": EmotionType.CONFUSION,
                "intensity": EmotionIntensity.MODERATE,
                "valence": -0.2,
                "arousal": 0.6,
                "dominance": 0.3,
                "pitch_modifier": 1.05,
                "speed_modifier": 0.85,
                "volume_modifier": 0.9,
                "description": "Moderate confusion with uncertain, questioning tone"
            },
            {
                "emotion_id": "confidence_high",
                "primary_emotion": EmotionType.CONFIDENCE,
                "intensity": EmotionIntensity.HIGH,
                "valence": 0.6,
                "arousal": 0.7,
                "dominance": 0.9,
                "pitch_modifier": 1.0,
                "speed_modifier": 1.0,
                "volume_modifier": 1.1,
                "description": "High confidence with strong, assured expression"
            },
            {
                "emotion_id": "anxiety_high",
                "primary_emotion": EmotionType.ANXIETY,
                "intensity": EmotionIntensity.HIGH,
                "valence": -0.5,
                "arousal": 0.8,
                "dominance": 0.2,
                "pitch_modifier": 1.15,
                "speed_modifier": 1.2,
                "volume_modifier": 0.8,
                "description": "High anxiety with nervous, hurried expression"
            },
            {
                "emotion_id": "contentment_moderate",
                "primary_emotion": EmotionType.CONTENTMENT,
                "intensity": EmotionIntensity.MODERATE,
                "valence": 0.6,
                "arousal": 0.3,
                "dominance": 0.6,
                "pitch_modifier": 1.0,
                "speed_modifier": 0.9,
                "volume_modifier": 0.9,
                "description": "Peaceful contentment with calm, satisfied expression"
            }
        ]
        
        for emotion_data in secondary_emotions:
            profile = self._create_emotion_profile(emotion_data)
            self.emotion_profiles[profile.emotion_id] = profile
    
    def _add_complex_emotions(self):
        """Add complex emotion combinations"""
        complex_emotions = [
            {
                "emotion_id": "bittersweet",
                "primary_emotion": EmotionType.SADNESS,
                "secondary_emotions": [EmotionType.JOY],
                "intensity": EmotionIntensity.MODERATE,
                "valence": 0.1,
                "arousal": 0.5,
                "dominance": 0.4,
                "pitch_modifier": 1.0,
                "speed_modifier": 0.9,
                "volume_modifier": 0.9,
                "description": "Bittersweet emotion mixing sadness and joy"
            },
            {
                "emotion_id": "nervous_excitement",
                "primary_emotion": EmotionType.EXCITEMENT,
                "secondary_emotions": [EmotionType.ANXIETY],
                "intensity": EmotionIntensity.HIGH,
                "valence": 0.3,
                "arousal": 0.9,
                "dominance": 0.4,
                "pitch_modifier": 1.2,
                "speed_modifier": 1.15,
                "volume_modifier": 1.0,
                "description": "Nervous excitement with anticipatory energy"
            },
            {
                "emotion_id": "melancholic_nostalgia",
                "primary_emotion": EmotionType.SADNESS,
                "secondary_emotions": [EmotionType.LOVE],
                "intensity": EmotionIntensity.MILD,
                "valence": -0.2,
                "arousal": 0.4,
                "dominance": 0.3,
                "pitch_modifier": 0.95,
                "speed_modifier": 0.85,
                "volume_modifier": 0.8,
                "description": "Melancholic nostalgia with wistful remembrance"
            },
            {
                "emotion_id": "righteous_anger",
                "primary_emotion": EmotionType.ANGER,
                "secondary_emotions": [EmotionType.CONFIDENCE],
                "intensity": EmotionIntensity.HIGH,
                "valence": -0.3,
                "arousal": 0.9,
                "dominance": 0.9,
                "pitch_modifier": 1.1,
                "speed_modifier": 1.1,
                "volume_modifier": 1.2,
                "description": "Righteous anger with moral conviction"
            }
        ]
        
        for emotion_data in complex_emotions:
            profile = self._create_emotion_profile(emotion_data)
            self.emotion_profiles[profile.emotion_id] = profile
    
    def _add_cultural_variants(self):
        """Add culturally adapted emotion variants"""
        cultural_emotions = [
            {
                "emotion_id": "joy_japanese_restrained",
                "primary_emotion": EmotionType.JOY,
                "intensity": EmotionIntensity.MODERATE,
                "valence": 0.7,
                "arousal": 0.4,
                "dominance": 0.3,
                "pitch_modifier": 1.05,
                "speed_modifier": 0.95,
                "volume_modifier": 0.85,
                "description": "Japanese-style restrained joy with subtle expression",
                "cultural_expression": {"restraint": 0.9, "harmony": 0.9}
            },
            {
                "emotion_id": "anger_british_polite",
                "primary_emotion": EmotionType.ANGER,
                "intensity": EmotionIntensity.MODERATE,
                "valence": -0.5,
                "arousal": 0.6,
                "dominance": 0.7,
                "pitch_modifier": 1.02,
                "speed_modifier": 1.0,
                "volume_modifier": 0.9,
                "description": "British-style polite anger with controlled expression",
                "cultural_expression": {"politeness": 0.9, "understatement": 0.8}
            },
            {
                "emotion_id": "enthusiasm_american",
                "primary_emotion": EmotionType.EXCITEMENT,
                "intensity": EmotionIntensity.HIGH,
                "valence": 0.8,
                "arousal": 0.9,
                "dominance": 0.8,
                "pitch_modifier": 1.3,
                "speed_modifier": 1.2,
                "volume_modifier": 1.3,
                "description": "American-style enthusiasm with expressive energy",
                "cultural_expression": {"expressiveness": 0.9, "optimism": 0.9}
            },
            {
                "emotion_id": "melancholy_slavic",
                "primary_emotion": EmotionType.SADNESS,
                "intensity": EmotionIntensity.MODERATE,
                "valence": -0.6,
                "arousal": 0.3,
                "dominance": 0.4,
                "pitch_modifier": 0.9,
                "speed_modifier": 0.8,
                "volume_modifier": 0.8,
                "description": "Slavic-style melancholy with deep, soulful expression",
                "cultural_expression": {"depth": 0.9, "soul": 0.9}
            }
        ]
        
        for emotion_data in cultural_emotions:
            profile = self._create_emotion_profile(emotion_data)
            self.emotion_profiles[profile.emotion_id] = profile
    
    def _add_contextual_emotions(self):
        """Add context-specific emotions"""
        contextual_emotions = [
            {
                "emotion_id": "professional_confidence",
                "primary_emotion": EmotionType.CONFIDENCE,
                "intensity": EmotionIntensity.HIGH,
                "valence": 0.6,
                "arousal": 0.6,
                "dominance": 0.8,
                "pitch_modifier": 1.0,
                "speed_modifier": 1.0,
                "volume_modifier": 1.05,
                "description": "Professional confidence for business contexts",
                "contextual_appropriateness": {"business": 0.9, "formal": 0.9}
            },
            {
                "emotion_id": "intimate_tenderness",
                "primary_emotion": EmotionType.LOVE,
                "intensity": EmotionIntensity.MODERATE,
                "valence": 0.8,
                "arousal": 0.4,
                "dominance": 0.3,
                "pitch_modifier": 0.95,
                "speed_modifier": 0.8,
                "volume_modifier": 0.7,
                "description": "Intimate tenderness for personal contexts",
                "contextual_appropriateness": {"intimate": 0.9, "personal": 0.9}
            },
            {
                "emotion_id": "educational_enthusiasm",
                "primary_emotion": EmotionType.EXCITEMENT,
                "intensity": EmotionIntensity.MODERATE,
                "valence": 0.7,
                "arousal": 0.7,
                "dominance": 0.6,
                "pitch_modifier": 1.1,
                "speed_modifier": 1.05,
                "volume_modifier": 1.0,
                "description": "Educational enthusiasm for teaching contexts",
                "contextual_appropriateness": {"educational": 0.9, "instructional": 0.9}
            },
            {
                "emotion_id": "storytelling_mystery",
                "primary_emotion": EmotionType.ANTICIPATION,
                "intensity": EmotionIntensity.MODERATE,
                "valence": 0.2,
                "arousal": 0.6,
                "dominance": 0.7,
                "pitch_modifier": 0.95,
                "speed_modifier": 0.9,
                "volume_modifier": 0.85,
                "description": "Mysterious anticipation for storytelling",
                "contextual_appropriateness": {"storytelling": 0.9, "narrative": 0.9}
            }
        ]
        
        for emotion_data in contextual_emotions:
            profile = self._create_emotion_profile(emotion_data)
            self.emotion_profiles[profile.emotion_id] = profile
    
    def _create_emotion_profile(self, emotion_data: Dict[str, Any]) -> EmotionProfile:
        """Create complete emotion profile from data"""
        
        return EmotionProfile(
            emotion_id=emotion_data["emotion_id"],
            primary_emotion=emotion_data["primary_emotion"],
            secondary_emotions=emotion_data.get("secondary_emotions", []),
            intensity=emotion_data["intensity"],
            valence=emotion_data["valence"],
            arousal=emotion_data["arousal"],
            dominance=emotion_data["dominance"],
            pitch_modifier=emotion_data["pitch_modifier"],
            speed_modifier=emotion_data["speed_modifier"],
            volume_modifier=emotion_data["volume_modifier"],
            tone_modifier=emotion_data.get("tone_modifier", 1.0),
            breathiness=emotion_data.get("breathiness", 0.0),
            vocal_fry=emotion_data.get("vocal_fry", 0.0),
            tremor=emotion_data.get("tremor", 0.0),
            stress_patterns=self._generate_stress_patterns(emotion_data),
            intonation_patterns=self._generate_intonation_patterns(emotion_data),
            pause_patterns=self._generate_pause_patterns(emotion_data),
            rhythm_variations=self._generate_rhythm_variations(emotion_data),
            cultural_expression=emotion_data.get("cultural_expression", {}),
            contextual_appropriateness=emotion_data.get("contextual_appropriateness", {}),
            description=emotion_data["description"],
            tags=self._generate_emotion_tags(emotion_data)
        )
    
    def _generate_stress_patterns(self, emotion_data: Dict[str, Any]) -> Dict[str, float]:
        """Generate stress patterns based on emotion"""
        arousal = emotion_data["arousal"]
        dominance = emotion_data["dominance"]
        
        return {
            "primary_stress_intensity": dominance * 1.5,
            "secondary_stress_reduction": (1.0 - arousal) * 0.5,
            "stress_variability": arousal * 0.8,
            "stress_timing": dominance * 0.7
        }
    
    def _generate_intonation_patterns(self, emotion_data: Dict[str, Any]) -> Dict[str, float]:
        """Generate intonation patterns based on emotion"""
        valence = emotion_data["valence"]
        arousal = emotion_data["arousal"]
        
        return {
            "pitch_range": arousal * 2.0,
            "pitch_direction": valence,
            "contour_complexity": arousal * 1.5,
            "final_boundary_tone": valence * 0.5
        }
    
    def _generate_pause_patterns(self, emotion_data: Dict[str, Any]) -> Dict[str, float]:
        """Generate pause patterns based on emotion"""
        arousal = emotion_data["arousal"]
        intensity = self._intensity_to_float(emotion_data["intensity"])
        
        return {
            "pause_frequency": (1.0 - arousal) * intensity,
            "pause_duration": (1.0 - arousal) * 1.5,
            "pause_variability": arousal * 0.8,
            "breath_pause_ratio": intensity * 0.6
        }
    
    def _generate_rhythm_variations(self, emotion_data: Dict[str, Any]) -> Dict[str, float]:
        """Generate rhythm variations based on emotion"""
        arousal = emotion_data["arousal"]
        dominance = emotion_data["dominance"]
        
        return {
            "tempo_variability": arousal * 1.2,
            "rhythm_regularity": dominance * 0.8,
            "acceleration_tendency": arousal * dominance,
            "deceleration_tendency": (1.0 - arousal) * (1.0 - dominance)
        }
    
    def _intensity_to_float(self, intensity: EmotionIntensity) -> float:
        """Convert intensity enum to float value"""
        mapping = {
            EmotionIntensity.VERY_LOW: 0.1,
            EmotionIntensity.LOW: 0.25,
            EmotionIntensity.MILD: 0.4,
            EmotionIntensity.MODERATE: 0.6,
            EmotionIntensity.HIGH: 0.8,
            EmotionIntensity.VERY_HIGH: 0.95,
            EmotionIntensity.EXTREME: 1.0
        }
        return mapping.get(intensity, 0.6)
    
    def _generate_emotion_tags(self, emotion_data: Dict[str, Any]) -> List[str]:
        """Generate tags for emotion profile"""
        tags = [
            emotion_data["primary_emotion"].value,
            emotion_data["intensity"].value
        ]
        
        # Add secondary emotion tags
        for emotion in emotion_data.get("secondary_emotions", []):
            tags.append(emotion.value)
        
        # Add valence tags
        valence = emotion_data["valence"]
        if valence > 0.5:
            tags.append("positive")
        elif valence < -0.5:
            tags.append("negative")
        else:
            tags.append("neutral")
        
        # Add arousal tags
        arousal = emotion_data["arousal"]
        if arousal > 0.7:
            tags.append("high_energy")
        elif arousal < 0.3:
            tags.append("low_energy")
        else:
            tags.append("medium_energy")
        
        return tags
    
    def get_emotion_profile(self, emotion_id: str) -> Optional[EmotionProfile]:
        """Get emotion profile by ID"""
        return self.emotion_profiles.get(emotion_id)
    
    def search_emotions(
        self,
        primary_emotion: Optional[EmotionType] = None,
        intensity: Optional[EmotionIntensity] = None,
        valence_range: Optional[Tuple[float, float]] = None,
        arousal_range: Optional[Tuple[float, float]] = None,
        dominance_range: Optional[Tuple[float, float]] = None,
        context: Optional[str] = None,
        cultural_style: Optional[str] = None,
        limit: int = 50
    ) -> List[EmotionProfile]:
        """Search emotions with filters"""
        results = []
        
        for profile in self.emotion_profiles.values():
            # Primary emotion filter
            if primary_emotion and profile.primary_emotion != primary_emotion:
                continue
            
            # Intensity filter
            if intensity and profile.intensity != intensity:
                continue
            
            # Valence range filter
            if valence_range:
                min_val, max_val = valence_range
                if not (min_val <= profile.valence <= max_val):
                    continue
            
            # Arousal range filter
            if arousal_range:
                min_ar, max_ar = arousal_range
                if not (min_ar <= profile.arousal <= max_ar):
                    continue
            
            # Dominance range filter
            if dominance_range:
                min_dom, max_dom = dominance_range
                if not (min_dom <= profile.dominance <= max_dom):
                    continue
            
            # Context filter
            if context and context in profile.contextual_appropriateness:
                if profile.contextual_appropriateness[context] < 0.7:
                    continue
            
            # Cultural style filter
            if cultural_style and cultural_style in profile.cultural_expression:
                if profile.cultural_expression[cultural_style] < 0.7:
                    continue
            
            results.append(profile)
        
        # Sort by appropriateness or intensity
        if context:
            results.sort(key=lambda x: x.contextual_appropriateness.get(context, 0.0), reverse=True)
        else:
            results.sort(key=lambda x: self._intensity_to_float(x.intensity), reverse=True)
        
        return results[:limit]
    
    def get_emotions_by_type(self, emotion_type: EmotionType) -> List[EmotionProfile]:
        """Get all emotions of a specific type"""
        return [profile for profile in self.emotion_profiles.values() 
                if profile.primary_emotion == emotion_type or emotion_type in profile.secondary_emotions]
    
    def get_opposite_emotion(self, emotion_id: str) -> Optional[EmotionProfile]:
        """Get opposite emotion for contrast"""
        profile = self.get_emotion_profile(emotion_id)
        if not profile:
            return None
        
        # Find emotion with opposite valence and similar arousal
        target_valence = -profile.valence
        target_arousal = profile.arousal
        
        best_match = None
        best_score = float('inf')
        
        for candidate in self.emotion_profiles.values():
            if candidate.emotion_id == emotion_id:
                continue
            
            valence_diff = abs(candidate.valence - target_valence)
            arousal_diff = abs(candidate.arousal - target_arousal)
            score = valence_diff + arousal_diff * 0.5
            
            if score < best_score:
                best_score = score
                best_match = candidate
        
        return best_match
    
    async def apply_emotion_to_voice(
        self,
        voice_profile: VoiceProfile,
        emotion_id: str,
        intensity_override: Optional[EmotionIntensity] = None,
        preserve_identity: bool = True
    ) -> Optional[VoiceProfile]:
        """Apply emotion transformation to voice profile"""
        
        emotion_profile = self.get_emotion_profile(emotion_id)
        if not emotion_profile:
            logger.error(f"Emotion profile not found: {emotion_id}")
            return None
        
        # Use override intensity if provided
        intensity = intensity_override or emotion_profile.intensity
        intensity_factor = self._intensity_to_float(intensity)
        
        # Create emotionally modified voice profile
        modified_profile = VoiceProfile(
            voice_id=f"{voice_profile.voice_id}_emotion_{emotion_id}",
            name=f"{voice_profile.name} ({emotion_profile.description})",
            language_code=voice_profile.language_code,
            region=voice_profile.region,
            gender=voice_profile.gender,
            age=voice_profile.age,
            accent=voice_profile.accent,
            accent_region=voice_profile.accent_region,
            supported_emotions=[VoiceEmotion.NEUTRAL] + [self._map_emotion_type_to_voice_emotion(emotion_profile.primary_emotion)],
            supported_styles=voice_profile.supported_styles,
            sample_rate=voice_profile.sample_rate,
            voice_characteristics=self._apply_emotional_characteristics(
                voice_profile.voice_characteristics,
                emotion_profile,
                intensity_factor,
                preserve_identity
            ),
            cultural_context={**voice_profile.cultural_context, **emotion_profile.cultural_expression},
            pronunciation_rules=voice_profile.pronunciation_rules,
            prosody_patterns=self._apply_emotional_prosody(
                voice_profile.prosody_patterns,
                emotion_profile,
                intensity_factor
            ),
            quality_score=voice_profile.quality_score * self._get_emotion_quality_modifier(intensity)
        )
        
        return modified_profile
    
    def _apply_emotional_characteristics(
        self,
        base_characteristics: Dict[str, float],
        emotion_profile: EmotionProfile,
        intensity_factor: float,
        preserve_identity: bool
    ) -> Dict[str, float]:
        """Apply emotional modifications to voice characteristics"""
        
        modified = base_characteristics.copy()
        
        # Identity preservation factor
        preservation_factor = 0.7 if preserve_identity else 0.3
        emotion_factor = intensity_factor * (1.0 - preservation_factor)
        
        # Apply pitch modifications
        base_pitch = modified.get("pitch", 200.0)
        emotion_pitch = base_pitch * emotion_profile.pitch_modifier
        modified["pitch"] = base_pitch * preservation_factor + emotion_pitch * emotion_factor
        
        # Apply speed modifications
        base_speed = modified.get("speed", 1.0)
        emotion_speed = base_speed * emotion_profile.speed_modifier
        modified["speed"] = base_speed * preservation_factor + emotion_speed * emotion_factor
        
        # Apply volume modifications
        base_volume = modified.get("volume", 1.0)
        emotion_volume = base_volume * emotion_profile.volume_modifier
        modified["volume"] = base_volume * preservation_factor + emotion_volume * emotion_factor
        
        # Apply tone modifications
        base_tone = modified.get("tone", 0.5)
        emotion_tone = base_tone * emotion_profile.tone_modifier
        modified["tone"] = base_tone * preservation_factor + emotion_tone * emotion_factor
        
        # Add emotional voice qualities
        modified["breathiness"] = emotion_profile.breathiness * intensity_factor
        modified["vocal_fry"] = emotion_profile.vocal_fry * intensity_factor
        modified["tremor"] = emotion_profile.tremor * intensity_factor
        
        # Emotional prosodic adjustments
        modified["valence"] = emotion_profile.valence
        modified["arousal"] = emotion_profile.arousal
        modified["dominance"] = emotion_profile.dominance
        
        return modified
    
    def _apply_emotional_prosody(
        self,
        base_prosody: Dict[str, Any],
        emotion_profile: EmotionProfile,
        intensity_factor: float
    ) -> Dict[str, Any]:
        """Apply emotional prosody patterns"""
        
        modified = base_prosody.copy()
        
        # Merge stress patterns
        if "stress" not in modified:
            modified["stress"] = {}
        for key, value in emotion_profile.stress_patterns.items():
            modified["stress"][key] = value * intensity_factor
        
        # Merge intonation patterns
        if "intonation" not in modified:
            modified["intonation"] = {}
        for key, value in emotion_profile.intonation_patterns.items():
            modified["intonation"][key] = value * intensity_factor
        
        # Merge pause patterns
        if "pauses" not in modified:
            modified["pauses"] = {}
        for key, value in emotion_profile.pause_patterns.items():
            modified["pauses"][key] = value * intensity_factor
        
        # Merge rhythm variations
        if "rhythm" not in modified:
            modified["rhythm"] = {}
        for key, value in emotion_profile.rhythm_variations.items():
            modified["rhythm"][key] = value * intensity_factor
        
        return modified
    
    def _map_emotion_type_to_voice_emotion(self, emotion_type: EmotionType) -> VoiceEmotion:
        """Map EmotionType to VoiceEmotion"""
        mapping = {
            EmotionType.JOY: VoiceEmotion.HAPPY,
            EmotionType.SADNESS: VoiceEmotion.SAD,
            EmotionType.ANGER: VoiceEmotion.ANGRY,
            EmotionType.FEAR: VoiceEmotion.FEARFUL,
            EmotionType.SURPRISE: VoiceEmotion.SURPRISED,
            EmotionType.EXCITEMENT: VoiceEmotion.EXCITED,
            EmotionType.LOVE: VoiceEmotion.WARM,
            EmotionType.CONFIDENCE: VoiceEmotion.CONFIDENT,
            EmotionType.CONTENTMENT: VoiceEmotion.CALM
        }
        return mapping.get(emotion_type, VoiceEmotion.NEUTRAL)
    
    def _get_emotion_quality_modifier(self, intensity: EmotionIntensity) -> float:
        """Get quality modifier based on emotion intensity"""
        modifiers = {
            EmotionIntensity.VERY_LOW: 0.99,
            EmotionIntensity.LOW: 0.98,
            EmotionIntensity.MILD: 0.97,
            EmotionIntensity.MODERATE: 0.95,
            EmotionIntensity.HIGH: 0.92,
            EmotionIntensity.VERY_HIGH: 0.88,
            EmotionIntensity.EXTREME: 0.85
        }
        return modifiers.get(intensity, 0.95)
    
    async def generate_emotional_voice_variants(
        self,
        base_voice_id: str,
        emotions: List[str],
        intensity: Optional[EmotionIntensity] = None
    ) -> List[VoiceProfile]:
        """Generate multiple emotional variants of a voice"""
        
        if not self.voice_bank:
            from .voice_bank import VoiceBank
            self.voice_bank = VoiceBank()
        
        # Get base voice
        base_enhanced = self.voice_bank.get_voice(base_voice_id)
        if not base_enhanced:
            logger.error(f"Base voice not found: {base_voice_id}")
            return []
        
        base_voice = base_enhanced.base_profile
        variants = []
        
        for emotion_id in emotions:
            variant = await self.apply_emotion_to_voice(
                base_voice, 
                emotion_id, 
                intensity_override=intensity
            )
            if variant:
                variants.append(variant)
        
        return variants
    
    async def create_emotion_transition(
        self,
        voice_profile: VoiceProfile,
        start_emotion: str,
        end_emotion: str,
        transition_style: EmotionTransition = EmotionTransition.GRADUAL,
        steps: int = 10
    ) -> List[VoiceProfile]:
        """Create gradual emotion transition between two emotions"""
        
        start_profile = self.get_emotion_profile(start_emotion)
        end_profile = self.get_emotion_profile(end_emotion)
        
        if not start_profile or not end_profile:
            logger.error("Start or end emotion profile not found")
            return []
        
        transition_voices = []
        
        for i in range(steps + 1):
            # Calculate interpolation factor
            if transition_style == EmotionTransition.INSTANT:
                factor = 1.0 if i == steps else 0.0
            elif transition_style == EmotionTransition.QUICK:
                factor = min(1.0, (i / steps) * 2.0)
            elif transition_style == EmotionTransition.GRADUAL:
                factor = i / steps
            elif transition_style == EmotionTransition.SMOOTH:
                factor = (np.sin((i / steps) * np.pi / 2)) ** 2
            elif transition_style == EmotionTransition.DRAMATIC:
                factor = (i / steps) ** 3
            else:
                factor = i / steps
            
            # Interpolate emotion characteristics
            interpolated_emotion = self._interpolate_emotions(
                start_profile, end_profile, factor
            )
            
            # Apply to voice
            transition_voice = await self.apply_interpolated_emotion_to_voice(
                voice_profile, interpolated_emotion, i
            )
            
            if transition_voice:
                transition_voices.append(transition_voice)
        
        return transition_voices
    
    def _interpolate_emotions(
        self,
        start_emotion: EmotionProfile,
        end_emotion: EmotionProfile,
        factor: float
    ) -> EmotionProfile:
        """Interpolate between two emotion profiles"""
        
        return EmotionProfile(
            emotion_id=f"transition_{start_emotion.emotion_id}_to_{end_emotion.emotion_id}_{factor:.2f}",
            primary_emotion=end_emotion.primary_emotion if factor > 0.5 else start_emotion.primary_emotion,
            secondary_emotions=start_emotion.secondary_emotions + end_emotion.secondary_emotions,
            intensity=end_emotion.intensity if factor > 0.5 else start_emotion.intensity,
            valence=start_emotion.valence * (1 - factor) + end_emotion.valence * factor,
            arousal=start_emotion.arousal * (1 - factor) + end_emotion.arousal * factor,
            dominance=start_emotion.dominance * (1 - factor) + end_emotion.dominance * factor,
            pitch_modifier=start_emotion.pitch_modifier * (1 - factor) + end_emotion.pitch_modifier * factor,
            speed_modifier=start_emotion.speed_modifier * (1 - factor) + end_emotion.speed_modifier * factor,
            volume_modifier=start_emotion.volume_modifier * (1 - factor) + end_emotion.volume_modifier * factor,
            tone_modifier=start_emotion.tone_modifier * (1 - factor) + end_emotion.tone_modifier * factor,
            breathiness=start_emotion.breathiness * (1 - factor) + end_emotion.breathiness * factor,
            vocal_fry=start_emotion.vocal_fry * (1 - factor) + end_emotion.vocal_fry * factor,
            tremor=start_emotion.tremor * (1 - factor) + end_emotion.tremor * factor,
            stress_patterns=self._interpolate_dict(start_emotion.stress_patterns, end_emotion.stress_patterns, factor),
            intonation_patterns=self._interpolate_dict(start_emotion.intonation_patterns, end_emotion.intonation_patterns, factor),
            pause_patterns=self._interpolate_dict(start_emotion.pause_patterns, end_emotion.pause_patterns, factor),
            rhythm_variations=self._interpolate_dict(start_emotion.rhythm_variations, end_emotion.rhythm_variations, factor),
            cultural_expression=self._interpolate_dict(start_emotion.cultural_expression, end_emotion.cultural_expression, factor),
            contextual_appropriateness=self._interpolate_dict(start_emotion.contextual_appropriateness, end_emotion.contextual_appropriateness, factor),
            description=f"Transition from {start_emotion.description} to {end_emotion.description}",
            tags=list(set(start_emotion.tags + end_emotion.tags))
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
    
    async def apply_interpolated_emotion_to_voice(
        self,
        voice_profile: VoiceProfile,
        emotion_profile: EmotionProfile,
        step: int
    ) -> Optional[VoiceProfile]:
        """Apply interpolated emotion to voice profile"""
        
        modified_profile = VoiceProfile(
            voice_id=f"{voice_profile.voice_id}_transition_step_{step}",
            name=f"{voice_profile.name} ({emotion_profile.description})",
            language_code=voice_profile.language_code,
            region=voice_profile.region,
            gender=voice_profile.gender,
            age=voice_profile.age,
            accent=voice_profile.accent,
            accent_region=voice_profile.accent_region,
            supported_emotions=voice_profile.supported_emotions,
            supported_styles=voice_profile.supported_styles,
            sample_rate=voice_profile.sample_rate,
            voice_characteristics=self._apply_emotional_characteristics(
                voice_profile.voice_characteristics,
                emotion_profile,
                1.0,  # Full intensity for interpolated emotion
                preserve_identity=True
            ),
            cultural_context={**voice_profile.cultural_context, **emotion_profile.cultural_expression},
            pronunciation_rules=voice_profile.pronunciation_rules,
            prosody_patterns=self._apply_emotional_prosody(
                voice_profile.prosody_patterns,
                emotion_profile,
                1.0
            ),
            quality_score=voice_profile.quality_score * 0.95  # Slight quality reduction for transitions
        )
        
        return modified_profile
    
    def get_emotion_statistics(self) -> Dict[str, Any]:
        """Get emotion statistics"""
        emotion_types = {}
        intensities = {}
        valence_distribution = {"positive": 0, "neutral": 0, "negative": 0}
        arousal_distribution = {"low": 0, "medium": 0, "high": 0}
        
        for profile in self.emotion_profiles.values():
            # Emotion type stats
            emotion_name = profile.primary_emotion.value
            if emotion_name not in emotion_types:
                emotion_types[emotion_name] = 0
            emotion_types[emotion_name] += 1
            
            # Intensity stats
            intensity_name = profile.intensity.value
            if intensity_name not in intensities:
                intensities[intensity_name] = 0
            intensities[intensity_name] += 1
            
            # Valence distribution
            if profile.valence > 0.3:
                valence_distribution["positive"] += 1
            elif profile.valence < -0.3:
                valence_distribution["negative"] += 1
            else:
                valence_distribution["neutral"] += 1
            
            # Arousal distribution
            if profile.arousal > 0.7:
                arousal_distribution["high"] += 1
            elif profile.arousal < 0.3:
                arousal_distribution["low"] += 1
            else:
                arousal_distribution["medium"] += 1
        
        return {
            "total_emotions": len(self.emotion_profiles),
            "emotion_types": emotion_types,
            "intensities": intensities,
            "valence_distribution": valence_distribution,
            "arousal_distribution": arousal_distribution,
            "average_valence": sum(p.valence for p in self.emotion_profiles.values()) / len(self.emotion_profiles),
            "average_arousal": sum(p.arousal for p in self.emotion_profiles.values()) / len(self.emotion_profiles),
            "average_dominance": sum(p.dominance for p in self.emotion_profiles.values()) / len(self.emotion_profiles)
        }