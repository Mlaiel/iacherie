"""Accent Generator - Advanced Accent Synthesis System

Generates and applies various accents to voices using linguistic analysis,
phonetic transformation, and cultural adaptation.

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

# Import existing infrastructure
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.i18n.voice_localization import VoiceProfile, AccentType
from .voice_bank import VoiceBank, EnhancedVoiceProfile

logger = logging.getLogger(__name__)


class AccentStrength(Enum):
    """Accent strength levels"""
    SUBTLE = "subtle"
    MILD = "mild"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


class AccentFamily(Enum):
    """Accent family classifications"""
    GERMANIC = "germanic"
    ROMANCE = "romance"
    SLAVIC = "slavic"
    SEMITIC = "semitic"
    SINO_TIBETAN = "sino_tibetan"
    INDO_ARYAN = "indo_aryan"
    ALTAIC = "altaic"
    AFROASIATIC = "afroasiatic"
    NIGER_CONGO = "niger_congo"
    AUSTRONESIAN = "austronesian"


@dataclass
class AccentProfile:
    """Comprehensive accent profile"""
    accent_id: str
    name: str
    family: AccentFamily
    base_language: str
    region: str
    country: str
    phonetic_features: Dict[str, Any]
    prosodic_patterns: Dict[str, float]
    vowel_shifts: Dict[str, str]
    consonant_modifications: Dict[str, str]
    stress_patterns: Dict[str, Any]
    intonation_contours: Dict[str, float]
    rhythm_characteristics: Dict[str, float]
    cultural_markers: Dict[str, Any]
    difficulty_level: int  # 1-10
    popularity_score: float
    compatibility_languages: List[str]


@dataclass
class AccentTransformation:
    """Accent transformation parameters"""
    source_accent: str
    target_accent: str
    strength: AccentStrength
    phonetic_adjustments: Dict[str, float]
    prosodic_adjustments: Dict[str, float]
    quality_preservation: float
    naturalness_score: float


class AccentGenerator:
    """Advanced accent generation and synthesis system"""
    
    def __init__(self):
        self.accent_profiles: Dict[str, AccentProfile] = {}
        self.transformation_cache: Dict[str, AccentTransformation] = {}
        self.voice_bank: Optional[VoiceBank] = None
        
        # Initialize accent profiles
        self._initialize_accent_profiles()
        
        logger.info(f"Accent generator initialized with {len(self.accent_profiles)} accents")
    
    def _initialize_accent_profiles(self):
        """Initialize comprehensive accent profiles"""
        
        # English accents
        self._add_english_accents()
        
        # European accents
        self._add_european_accents()
        
        # Asian accents
        self._add_asian_accents()
        
        # Middle Eastern accents
        self._add_middle_eastern_accents()
        
        # African accents
        self._add_african_accents()
        
        # American accents
        self._add_american_accents()
    
    def _add_english_accents(self):
        """Add English accent variations"""
        english_accents = [
            {
                "accent_id": "en_us_general",
                "name": "General American",
                "region": "General",
                "country": "United States",
                "phonetic_features": {
                    "rhotic": True,
                    "vowel_system": "general_american",
                    "consonant_clusters": "simplified"
                },
                "vowel_shifts": {
                    "æ": "æ",
                    "ɑ": "ɑ",
                    "ɔ": "ɔ"
                },
                "difficulty_level": 3,
                "popularity_score": 9.5
            },
            {
                "accent_id": "en_gb_rp",
                "name": "Received Pronunciation",
                "region": "London",
                "country": "United Kingdom",
                "phonetic_features": {
                    "rhotic": False,
                    "vowel_system": "rp",
                    "h_dropping": False
                },
                "vowel_shifts": {
                    "æ": "a",
                    "ɑ": "ɑː",
                    "ɔ": "ɔː"
                },
                "difficulty_level": 6,
                "popularity_score": 8.5
            },
            {
                "accent_id": "en_au_general",
                "name": "General Australian",
                "region": "General",
                "country": "Australia",
                "phonetic_features": {
                    "rhotic": False,
                    "vowel_system": "australian",
                    "final_consonants": "weakened"
                },
                "vowel_shifts": {
                    "eɪ": "aɪ",
                    "aɪ": "ɑɪ",
                    "i": "ɪ"
                },
                "difficulty_level": 5,
                "popularity_score": 7.0
            },
            {
                "accent_id": "en_ie_dublin",
                "name": "Dublin Irish",
                "region": "Dublin",
                "country": "Ireland",
                "phonetic_features": {
                    "rhotic": True,
                    "vowel_system": "irish",
                    "th_sounds": "modified"
                },
                "vowel_shifts": {
                    "eɪ": "eː",
                    "oʊ": "oː",
                    "aɪ": "ɑɪ"
                },
                "difficulty_level": 7,
                "popularity_score": 6.5
            },
            {
                "accent_id": "en_za_general",
                "name": "South African English",
                "region": "General",
                "country": "South Africa",
                "phonetic_features": {
                    "rhotic": False,
                    "vowel_system": "south_african",
                    "consonant_clusters": "retained"
                },
                "vowel_shifts": {
                    "ɪ": "ɪ",
                    "e": "ɛ",
                    "æ": "ɛ"
                },
                "difficulty_level": 6,
                "popularity_score": 5.5
            }
        ]
        
        for accent_data in english_accents:
            profile = self._create_accent_profile(accent_data, AccentFamily.GERMANIC, "en")
            self.accent_profiles[profile.accent_id] = profile
    
    def _add_european_accents(self):
        """Add European accent variations"""
        european_accents = [
            # French accents
            {
                "accent_id": "fr_fr_parisian",
                "name": "Parisian French",
                "region": "Paris",
                "country": "France",
                "base_language": "fr",
                "family": AccentFamily.ROMANCE,
                "difficulty_level": 7,
                "popularity_score": 8.0
            },
            {
                "accent_id": "fr_ca_quebec",
                "name": "Quebec French",
                "region": "Quebec",
                "country": "Canada",
                "base_language": "fr",
                "family": AccentFamily.ROMANCE,
                "difficulty_level": 8,
                "popularity_score": 6.0
            },
            # Spanish accents
            {
                "accent_id": "es_es_castilian",
                "name": "Castilian Spanish",
                "region": "Castile",
                "country": "Spain",
                "base_language": "es",
                "family": AccentFamily.ROMANCE,
                "difficulty_level": 6,
                "popularity_score": 7.5
            },
            {
                "accent_id": "es_mx_central",
                "name": "Central Mexican Spanish",
                "region": "Central",
                "country": "Mexico",
                "base_language": "es",
                "family": AccentFamily.ROMANCE,
                "difficulty_level": 5,
                "popularity_score": 8.5
            },
            # German accents
            {
                "accent_id": "de_de_standard",
                "name": "Standard German",
                "region": "Standard",
                "country": "Germany",
                "base_language": "de",
                "family": AccentFamily.GERMANIC,
                "difficulty_level": 6,
                "popularity_score": 7.0
            },
            {
                "accent_id": "de_at_viennese",
                "name": "Viennese German",
                "region": "Vienna",
                "country": "Austria",
                "base_language": "de",
                "family": AccentFamily.GERMANIC,
                "difficulty_level": 7,
                "popularity_score": 5.5
            },
            # Italian accents
            {
                "accent_id": "it_it_standard",
                "name": "Standard Italian",
                "region": "Standard",
                "country": "Italy",
                "base_language": "it",
                "family": AccentFamily.ROMANCE,
                "difficulty_level": 6,
                "popularity_score": 7.5
            },
            # Russian accents
            {
                "accent_id": "ru_ru_moscow",
                "name": "Moscow Russian",
                "region": "Moscow",
                "country": "Russia",
                "base_language": "ru",
                "family": AccentFamily.SLAVIC,
                "difficulty_level": 8,
                "popularity_score": 6.5
            }
        ]
        
        for accent_data in european_accents:
            if "base_language" not in accent_data:
                continue
            
            profile = self._create_accent_profile(
                accent_data, 
                accent_data["family"], 
                accent_data["base_language"]
            )
            self.accent_profiles[profile.accent_id] = profile
    
    def _add_asian_accents(self):
        """Add Asian accent variations"""
        asian_accents = [
            {
                "accent_id": "zh_cn_beijing",
                "name": "Beijing Mandarin",
                "region": "Beijing",
                "country": "China",
                "base_language": "zh",
                "family": AccentFamily.SINO_TIBETAN,
                "difficulty_level": 9,
                "popularity_score": 8.0
            },
            {
                "accent_id": "ja_jp_tokyo",
                "name": "Tokyo Japanese",
                "region": "Tokyo",
                "country": "Japan",
                "base_language": "ja",
                "family": AccentFamily.ALTAIC,
                "difficulty_level": 9,
                "popularity_score": 7.5
            },
            {
                "accent_id": "ko_kr_seoul",
                "name": "Seoul Korean",
                "region": "Seoul",
                "country": "South Korea",
                "base_language": "ko",
                "family": AccentFamily.ALTAIC,
                "difficulty_level": 8,
                "popularity_score": 7.0
            },
            {
                "accent_id": "hi_in_delhi",
                "name": "Delhi Hindi",
                "region": "Delhi",
                "country": "India",
                "base_language": "hi",
                "family": AccentFamily.INDO_ARYAN,
                "difficulty_level": 7,
                "popularity_score": 8.5
            },
            {
                "accent_id": "th_th_bangkok",
                "name": "Bangkok Thai",
                "region": "Bangkok",
                "country": "Thailand",
                "base_language": "th",
                "family": AccentFamily.SINO_TIBETAN,
                "difficulty_level": 9,
                "popularity_score": 6.0
            }
        ]
        
        for accent_data in asian_accents:
            profile = self._create_accent_profile(
                accent_data, 
                accent_data["family"], 
                accent_data["base_language"]
            )
            self.accent_profiles[profile.accent_id] = profile
    
    def _add_middle_eastern_accents(self):
        """Add Middle Eastern accent variations"""
        middle_eastern_accents = [
            {
                "accent_id": "ar_sa_najdi",
                "name": "Najdi Arabic",
                "region": "Najd",
                "country": "Saudi Arabia",
                "base_language": "ar",
                "family": AccentFamily.SEMITIC,
                "difficulty_level": 8,
                "popularity_score": 7.0
            },
            {
                "accent_id": "ar_eg_cairene",
                "name": "Cairene Arabic",
                "region": "Cairo",
                "country": "Egypt",
                "base_language": "ar",
                "family": AccentFamily.SEMITIC,
                "difficulty_level": 7,
                "popularity_score": 8.0
            },
            {
                "accent_id": "fa_ir_tehrani",
                "name": "Tehrani Persian",
                "region": "Tehran",
                "country": "Iran",
                "base_language": "fa",
                "family": AccentFamily.INDO_ARYAN,
                "difficulty_level": 8,
                "popularity_score": 6.5
            },
            {
                "accent_id": "tr_tr_istanbul",
                "name": "Istanbul Turkish",
                "region": "Istanbul",
                "country": "Turkey",
                "base_language": "tr",
                "family": AccentFamily.ALTAIC,
                "difficulty_level": 7,
                "popularity_score": 6.0
            }
        ]
        
        for accent_data in middle_eastern_accents:
            profile = self._create_accent_profile(
                accent_data, 
                accent_data["family"], 
                accent_data["base_language"]
            )
            self.accent_profiles[profile.accent_id] = profile
    
    def _add_african_accents(self):
        """Add African accent variations"""
        african_accents = [
            {
                "accent_id": "sw_ke_nairobi",
                "name": "Nairobi Swahili",
                "region": "Nairobi",
                "country": "Kenya",
                "base_language": "sw",
                "family": AccentFamily.NIGER_CONGO,
                "difficulty_level": 6,
                "popularity_score": 5.0
            },
            {
                "accent_id": "yo_ng_lagos",
                "name": "Lagos Yoruba",
                "region": "Lagos",
                "country": "Nigeria",
                "base_language": "yo",
                "family": AccentFamily.NIGER_CONGO,
                "difficulty_level": 7,
                "popularity_score": 5.5
            },
            {
                "accent_id": "am_et_addis",
                "name": "Addis Ababa Amharic",
                "region": "Addis Ababa",
                "country": "Ethiopia",
                "base_language": "am",
                "family": AccentFamily.AFROASIATIC,
                "difficulty_level": 8,
                "popularity_score": 4.5
            }
        ]
        
        for accent_data in african_accents:
            profile = self._create_accent_profile(
                accent_data, 
                accent_data["family"], 
                accent_data["base_language"]
            )
            self.accent_profiles[profile.accent_id] = profile
    
    def _add_american_accents(self):
        """Add American regional accents"""
        american_accents = [
            {
                "accent_id": "en_us_southern",
                "name": "Southern American",
                "region": "South",
                "country": "United States",
                "base_language": "en",
                "family": AccentFamily.GERMANIC,
                "difficulty_level": 6,
                "popularity_score": 7.0
            },
            {
                "accent_id": "en_us_boston",
                "name": "Boston",
                "region": "New England",
                "country": "United States",
                "base_language": "en",
                "family": AccentFamily.GERMANIC,
                "difficulty_level": 7,
                "popularity_score": 6.5
            },
            {
                "accent_id": "en_us_midwest",
                "name": "Midwestern",
                "region": "Midwest",
                "country": "United States",
                "base_language": "en",
                "family": AccentFamily.GERMANIC,
                "difficulty_level": 4,
                "popularity_score": 8.0
            },
            {
                "accent_id": "es_ar_porteno",
                "name": "Porteño Spanish",
                "region": "Buenos Aires",
                "country": "Argentina",
                "base_language": "es",
                "family": AccentFamily.ROMANCE,
                "difficulty_level": 8,
                "popularity_score": 6.5
            },
            {
                "accent_id": "pt_br_paulista",
                "name": "Paulista Portuguese",
                "region": "São Paulo",
                "country": "Brazil",
                "base_language": "pt",
                "family": AccentFamily.ROMANCE,
                "difficulty_level": 7,
                "popularity_score": 7.5
            }
        ]
        
        for accent_data in american_accents:
            profile = self._create_accent_profile(
                accent_data, 
                accent_data["family"], 
                accent_data["base_language"]
            )
            self.accent_profiles[profile.accent_id] = profile
    
    def _create_accent_profile(
        self, 
        accent_data: Dict[str, Any], 
        family: AccentFamily, 
        base_language: str
    ) -> AccentProfile:
        """Create complete accent profile from data"""
        
        return AccentProfile(
            accent_id=accent_data["accent_id"],
            name=accent_data["name"],
            family=family,
            base_language=base_language,
            region=accent_data["region"],
            country=accent_data["country"],
            phonetic_features=accent_data.get("phonetic_features", {}),
            prosodic_patterns=self._generate_prosodic_patterns(family),
            vowel_shifts=accent_data.get("vowel_shifts", {}),
            consonant_modifications=self._generate_consonant_modifications(family),
            stress_patterns=self._generate_stress_patterns(family),
            intonation_contours=self._generate_intonation_contours(family),
            rhythm_characteristics=self._generate_rhythm_characteristics(family),
            cultural_markers=self._generate_cultural_markers(accent_data["country"]),
            difficulty_level=accent_data["difficulty_level"],
            popularity_score=accent_data["popularity_score"],
            compatibility_languages=self._get_compatibility_languages(base_language, family)
        )
    
    def _generate_prosodic_patterns(self, family: AccentFamily) -> Dict[str, float]:
        """Generate prosodic patterns based on accent family"""
        base_patterns = {
            AccentFamily.GERMANIC: {"stress_timing": 0.8, "syllable_timing": 0.2},
            AccentFamily.ROMANCE: {"stress_timing": 0.3, "syllable_timing": 0.7},
            AccentFamily.SLAVIC: {"stress_timing": 0.7, "syllable_timing": 0.3},
            AccentFamily.SEMITIC: {"stress_timing": 0.5, "syllable_timing": 0.5},
            AccentFamily.SINO_TIBETAN: {"stress_timing": 0.1, "syllable_timing": 0.9},
            AccentFamily.ALTAIC: {"stress_timing": 0.4, "syllable_timing": 0.6}
        }
        
        return base_patterns.get(family, {"stress_timing": 0.5, "syllable_timing": 0.5})
    
    def _generate_consonant_modifications(self, family: AccentFamily) -> Dict[str, str]:
        """Generate consonant modifications for accent family"""
        modifications = {
            AccentFamily.GERMANIC: {"θ": "f", "ð": "v"},
            AccentFamily.ROMANCE: {"h": "∅", "ŋ": "n"},
            AccentFamily.SLAVIC: {"w": "v", "θ": "s"},
            AccentFamily.SEMITIC: {"p": "b", "v": "f"},
            AccentFamily.SINO_TIBETAN: {"r": "l", "θ": "s"},
            AccentFamily.ALTAIC: {"f": "p", "v": "b"}
        }
        
        return modifications.get(family, {})
    
    def _generate_stress_patterns(self, family: AccentFamily) -> Dict[str, Any]:
        """Generate stress patterns for accent family"""
        patterns = {
            AccentFamily.GERMANIC: {"primary_stress": "initial", "secondary_stress": "weak"},
            AccentFamily.ROMANCE: {"primary_stress": "penultimate", "secondary_stress": "moderate"},
            AccentFamily.SLAVIC: {"primary_stress": "variable", "secondary_stress": "strong"},
            AccentFamily.SEMITIC: {"primary_stress": "final", "secondary_stress": "weak"},
            AccentFamily.SINO_TIBETAN: {"primary_stress": "syllabic", "secondary_stress": "tonal"},
            AccentFamily.ALTAIC: {"primary_stress": "initial", "secondary_stress": "moderate"}
        }
        
        return patterns.get(family, {"primary_stress": "initial", "secondary_stress": "weak"})
    
    def _generate_intonation_contours(self, family: AccentFamily) -> Dict[str, float]:
        """Generate intonation contours for accent family"""
        contours = {
            AccentFamily.GERMANIC: {"rise": 0.6, "fall": 0.7, "rise_fall": 0.5},
            AccentFamily.ROMANCE: {"rise": 0.8, "fall": 0.6, "rise_fall": 0.7},
            AccentFamily.SLAVIC: {"rise": 0.5, "fall": 0.8, "rise_fall": 0.6},
            AccentFamily.SEMITIC: {"rise": 0.7, "fall": 0.5, "rise_fall": 0.8},
            AccentFamily.SINO_TIBETAN: {"rise": 0.9, "fall": 0.9, "rise_fall": 0.9},
            AccentFamily.ALTAIC: {"rise": 0.6, "fall": 0.6, "rise_fall": 0.6}
        }
        
        return contours.get(family, {"rise": 0.6, "fall": 0.6, "rise_fall": 0.6})
    
    def _generate_rhythm_characteristics(self, family: AccentFamily) -> Dict[str, float]:
        """Generate rhythm characteristics for accent family"""
        rhythms = {
            AccentFamily.GERMANIC: {"tempo": 1.0, "variation": 0.7, "regularity": 0.8},
            AccentFamily.ROMANCE: {"tempo": 1.1, "variation": 0.8, "regularity": 0.9},
            AccentFamily.SLAVIC: {"tempo": 0.9, "variation": 0.6, "regularity": 0.7},
            AccentFamily.SEMITIC: {"tempo": 1.0, "variation": 0.9, "regularity": 0.6},
            AccentFamily.SINO_TIBETAN: {"tempo": 0.8, "variation": 0.5, "regularity": 0.9},
            AccentFamily.ALTAIC: {"tempo": 1.0, "variation": 0.7, "regularity": 0.8}
        }
        
        return rhythms.get(family, {"tempo": 1.0, "variation": 0.7, "regularity": 0.8})
    
    def _generate_cultural_markers(self, country: str) -> Dict[str, Any]:
        """Generate cultural markers for country"""
        return {
            "formality_level": random.uniform(0.3, 0.9),
            "directness": random.uniform(0.2, 0.8),
            "emotional_expression": random.uniform(0.4, 0.9),
            "pace_preference": random.uniform(0.7, 1.3),
            "volume_tendency": random.uniform(0.8, 1.2)
        }
    
    def _get_compatibility_languages(self, base_language: str, family: AccentFamily) -> List[str]:
        """Get compatible languages for accent application"""
        family_languages = {
            AccentFamily.GERMANIC: ["en", "de", "nl", "sv", "no", "da"],
            AccentFamily.ROMANCE: ["es", "fr", "it", "pt", "ro", "ca"],
            AccentFamily.SLAVIC: ["ru", "pl", "cs", "sk", "uk", "bg"],
            AccentFamily.SEMITIC: ["ar", "he", "am"],
            AccentFamily.SINO_TIBETAN: ["zh", "th", "my"],
            AccentFamily.ALTAIC: ["ja", "ko", "tr", "mn"],
            AccentFamily.INDO_ARYAN: ["hi", "ur", "bn", "pa", "gu"],
            AccentFamily.NIGER_CONGO: ["sw", "yo", "ig", "zu"],
            AccentFamily.AFROASIATIC: ["ar", "he", "am", "so"],
            AccentFamily.AUSTRONESIAN: ["id", "ms", "tl", "mg"]
        }
        
        compatible = family_languages.get(family, [base_language])
        
        # Always include the base language and English (as universal)
        if base_language not in compatible:
            compatible.append(base_language)
        if "en" not in compatible:
            compatible.append("en")
        
        return compatible
    
    def get_accent_profile(self, accent_id: str) -> Optional[AccentProfile]:
        """Get accent profile by ID"""
        return self.accent_profiles.get(accent_id)
    
    def search_accents(
        self,
        language: Optional[str] = None,
        family: Optional[AccentFamily] = None,
        country: Optional[str] = None,
        region: Optional[str] = None,
        min_popularity: Optional[float] = None,
        max_difficulty: Optional[int] = None,
        limit: int = 50
    ) -> List[AccentProfile]:
        """Search accents with filters"""
        results = []
        
        for profile in self.accent_profiles.values():
            # Apply filters
            if language and profile.base_language != language:
                continue
            if family and profile.family != family:
                continue
            if country and profile.country.lower() != country.lower():
                continue
            if region and profile.region.lower() != region.lower():
                continue
            if min_popularity and profile.popularity_score < min_popularity:
                continue
            if max_difficulty and profile.difficulty_level > max_difficulty:
                continue
            
            results.append(profile)
        
        # Sort by popularity
        results.sort(key=lambda x: x.popularity_score, reverse=True)
        
        return results[:limit]
    
    def get_popular_accents(self, limit: int = 10) -> List[AccentProfile]:
        """Get most popular accents"""
        all_accents = list(self.accent_profiles.values())
        all_accents.sort(key=lambda x: x.popularity_score, reverse=True)
        return all_accents[:limit]
    
    def get_accents_by_family(self, family: AccentFamily) -> List[AccentProfile]:
        """Get accents by language family"""
        return [profile for profile in self.accent_profiles.values() 
                if profile.family == family]
    
    def get_compatible_accents(self, language: str) -> List[AccentProfile]:
        """Get accents compatible with a language"""
        return [profile for profile in self.accent_profiles.values() 
                if language in profile.compatibility_languages]
    
    async def apply_accent_to_voice(
        self,
        voice_profile: VoiceProfile,
        accent_id: str,
        strength: AccentStrength = AccentStrength.MODERATE
    ) -> Optional[VoiceProfile]:
        """Apply accent transformation to voice profile"""
        
        accent_profile = self.get_accent_profile(accent_id)
        if not accent_profile:
            logger.error(f"Accent profile not found: {accent_id}")
            return None
        
        # Check compatibility
        if voice_profile.language_code not in accent_profile.compatibility_languages:
            logger.warning(f"Language {voice_profile.language_code} not compatible with accent {accent_id}")
            # Continue anyway but with reduced quality
        
        # Create modified voice profile
        modified_profile = VoiceProfile(
            voice_id=f"{voice_profile.voice_id}_accent_{accent_id}_{strength.value}",
            name=f"{voice_profile.name} ({accent_profile.name} accent)",
            language_code=voice_profile.language_code,
            region=accent_profile.region,
            gender=voice_profile.gender,
            age=voice_profile.age,
            accent=AccentType.REGIONAL,
            accent_region=accent_profile.region,
            supported_emotions=voice_profile.supported_emotions,
            supported_styles=voice_profile.supported_styles,
            sample_rate=voice_profile.sample_rate,
            voice_characteristics=self._apply_accent_characteristics(
                voice_profile.voice_characteristics,
                accent_profile,
                strength
            ),
            cultural_context=accent_profile.cultural_markers,
            pronunciation_rules=self._generate_pronunciation_rules(accent_profile),
            prosody_patterns=accent_profile.prosodic_patterns,
            quality_score=voice_profile.quality_score * self._get_quality_modifier(strength)
        )
        
        return modified_profile
    
    def _apply_accent_characteristics(
        self,
        base_characteristics: Dict[str, float],
        accent_profile: AccentProfile,
        strength: AccentStrength
    ) -> Dict[str, float]:
        """Apply accent modifications to voice characteristics"""
        
        strength_multiplier = {
            AccentStrength.SUBTLE: 0.2,
            AccentStrength.MILD: 0.4,
            AccentStrength.MODERATE: 0.6,
            AccentStrength.STRONG: 0.8,
            AccentStrength.VERY_STRONG: 1.0
        }[strength]
        
        modified = base_characteristics.copy()
        
        # Apply rhythm modifications
        rhythm = accent_profile.rhythm_characteristics
        modified["speed"] = modified.get("speed", 1.0) * rhythm["tempo"] * strength_multiplier + \
                           modified.get("speed", 1.0) * (1 - strength_multiplier)
        
        # Apply pitch modifications based on accent family
        pitch_modifier = self._get_pitch_modifier(accent_profile.family)
        modified["pitch"] = modified.get("pitch", 200.0) * pitch_modifier * strength_multiplier + \
                           modified.get("pitch", 200.0) * (1 - strength_multiplier)
        
        # Apply tone modifications
        tone_modifier = accent_profile.cultural_markers.get("emotional_expression", 0.7)
        modified["tone"] = modified.get("tone", 0.5) * tone_modifier * strength_multiplier + \
                          modified.get("tone", 0.5) * (1 - strength_multiplier)
        
        return modified
    
    def _get_pitch_modifier(self, family: AccentFamily) -> float:
        """Get pitch modifier for accent family"""
        modifiers = {
            AccentFamily.GERMANIC: 1.0,
            AccentFamily.ROMANCE: 1.1,
            AccentFamily.SLAVIC: 0.95,
            AccentFamily.SEMITIC: 1.05,
            AccentFamily.SINO_TIBETAN: 1.2,
            AccentFamily.ALTAIC: 1.0,
            AccentFamily.INDO_ARYAN: 1.1,
            AccentFamily.NIGER_CONGO: 1.15,
            AccentFamily.AFROASIATIC: 1.05,
            AccentFamily.AUSTRONESIAN: 1.1
        }
        
        return modifiers.get(family, 1.0)
    
    def _get_quality_modifier(self, strength: AccentStrength) -> float:
        """Get quality modifier based on accent strength"""
        modifiers = {
            AccentStrength.SUBTLE: 0.98,
            AccentStrength.MILD: 0.95,
            AccentStrength.MODERATE: 0.92,
            AccentStrength.STRONG: 0.88,
            AccentStrength.VERY_STRONG: 0.85
        }
        
        return modifiers[strength]
    
    def _generate_pronunciation_rules(self, accent_profile: AccentProfile) -> Dict[str, str]:
        """Generate pronunciation rules from accent profile"""
        rules = {}
        
        # Add vowel shifts
        rules.update(accent_profile.vowel_shifts)
        
        # Add consonant modifications
        rules.update(accent_profile.consonant_modifications)
        
        # Add phonetic features as rules
        for feature, value in accent_profile.phonetic_features.items():
            if isinstance(value, bool):
                rules[feature] = str(value).lower()
            else:
                rules[feature] = str(value)
        
        return rules
    
    async def generate_accent_variations(
        self,
        base_voice_id: str,
        target_accents: List[str],
        strengths: Optional[List[AccentStrength]] = None
    ) -> List[VoiceProfile]:
        """Generate multiple accent variations of a voice"""
        
        if not self.voice_bank:
            from .voice_bank import VoiceBank
            self.voice_bank = VoiceBank()
        
        # Get base voice
        base_enhanced = self.voice_bank.get_voice(base_voice_id)
        if not base_enhanced:
            logger.error(f"Base voice not found: {base_voice_id}")
            return []
        
        base_voice = base_enhanced.base_profile
        
        if strengths is None:
            strengths = [AccentStrength.MODERATE] * len(target_accents)
        elif len(strengths) != len(target_accents):
            strengths = [AccentStrength.MODERATE] * len(target_accents)
        
        variations = []
        
        for accent_id, strength in zip(target_accents, strengths):
            variation = await self.apply_accent_to_voice(base_voice, accent_id, strength)
            if variation:
                variations.append(variation)
        
        return variations
    
    def get_accent_statistics(self) -> Dict[str, Any]:
        """Get accent statistics"""
        families = {}
        languages = {}
        countries = {}
        
        for profile in self.accent_profiles.values():
            # Family stats
            family_name = profile.family.value
            if family_name not in families:
                families[family_name] = 0
            families[family_name] += 1
            
            # Language stats
            if profile.base_language not in languages:
                languages[profile.base_language] = 0
            languages[profile.base_language] += 1
            
            # Country stats
            if profile.country not in countries:
                countries[profile.country] = 0
            countries[profile.country] += 1
        
        return {
            "total_accents": len(self.accent_profiles),
            "families": families,
            "languages": languages,
            "countries": countries,
            "average_difficulty": sum(p.difficulty_level for p in self.accent_profiles.values()) / len(self.accent_profiles),
            "average_popularity": sum(p.popularity_score for p in self.accent_profiles.values()) / len(self.accent_profiles)
        }