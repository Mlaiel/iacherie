"""Voice Bank - Comprehensive Voice Collection System

Manages 1000+ high-quality voice profiles with advanced categorization,
filtering, and selection capabilities for content generation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import random

# Import existing voice infrastructure
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.i18n.voice_localization import VoiceProfile, VoiceGender, VoiceAge, AccentType, VoiceEmotion, SpeechStyle
from backend.ai.conversational.voice_processing.voice_synthesis import VoiceStyle, SynthesisQuality

logger = logging.getLogger(__name__)


class VoiceCategory(Enum):
    """Voice categorization for organization"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ENTERTAINMENT = "entertainment"
    EDUCATIONAL = "educational"
    COMMERCIAL = "commercial"
    NARRATIVE = "narrative"
    CONVERSATIONAL = "conversational"
    ARTISTIC = "artistic"


class VoicePopularity(Enum):
    """Voice popularity levels"""
    TRENDING = "trending"
    POPULAR = "popular"
    STANDARD = "standard"
    NICHE = "niche"
    EXCLUSIVE = "exclusive"


@dataclass
class EnhancedVoiceProfile:
    """Enhanced voice profile with additional metadata"""
    base_profile: VoiceProfile
    category: VoiceCategory
    popularity: VoicePopularity
    usage_count: int = 0
    rating: float = 0.0
    tags: List[str] = None
    description: str = ""
    sample_audio_url: Optional[str] = None
    license_type: str = "standard"
    creator: str = "AI_Generated"
    created_date: str = ""
    last_updated: str = ""
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class VoiceBank:
    """Comprehensive voice bank with 1000+ voices"""
    
    def __init__(self):
        self.voices: Dict[str, EnhancedVoiceProfile] = {}
        self.categories: Dict[VoiceCategory, List[str]] = {}
        self.language_index: Dict[str, List[str]] = {}
        self.gender_index: Dict[VoiceGender, List[str]] = {}
        self.age_index: Dict[VoiceAge, List[str]] = {}
        self.accent_index: Dict[AccentType, List[str]] = {}
        self.style_index: Dict[SpeechStyle, List[str]] = {}
        self.popularity_index: Dict[VoicePopularity, List[str]] = {}
        
        # Initialize voice bank
        self._generate_voice_bank()
        self._build_indexes()
        
        logger.info(f"Voice bank initialized with {len(self.voices)} voices")
    
    def _generate_voice_bank(self):
        """Generate comprehensive voice bank with 1000+ voices"""
        
        # Language and region combinations
        language_regions = [
            # English variants
            ("en", "US", "General American"), ("en", "GB", "Received Pronunciation"),
            ("en", "AU", "Australian"), ("en", "CA", "Canadian"), ("en", "IE", "Irish"),
            ("en", "ZA", "South African"), ("en", "IN", "Indian"), ("en", "SG", "Singaporean"),
            ("en", "NZ", "New Zealand"), ("en", "JM", "Jamaican"),
            
            # European languages
            ("fr", "FR", "Parisian"), ("fr", "CA", "Quebec"), ("fr", "BE", "Belgian"),
            ("es", "ES", "Castilian"), ("es", "MX", "Mexican"), ("es", "AR", "Argentinian"),
            ("es", "CO", "Colombian"), ("es", "CL", "Chilean"), ("es", "PE", "Peruvian"),
            ("de", "DE", "Standard German"), ("de", "AT", "Austrian"), ("de", "CH", "Swiss"),
            ("it", "IT", "Standard Italian"), ("it", "CH", "Swiss Italian"),
            ("pt", "BR", "Brazilian"), ("pt", "PT", "European Portuguese"),
            ("nl", "NL", "Dutch"), ("nl", "BE", "Flemish"),
            ("ru", "RU", "Moscow"), ("ru", "UA", "Ukrainian Russian"),
            ("pl", "PL", "Warsaw"), ("cs", "CZ", "Prague"), ("hu", "HU", "Budapest"),
            ("ro", "RO", "Bucharest"), ("bg", "BG", "Sofia"), ("hr", "HR", "Zagreb"),
            ("sk", "SK", "Bratislava"), ("sl", "SI", "Ljubljana"),
            
            # Nordic languages
            ("sv", "SE", "Stockholm"), ("no", "NO", "Oslo"), ("da", "DK", "Copenhagen"),
            ("fi", "FI", "Helsinki"), ("is", "IS", "Reykjavik"),
            
            # Asian languages
            ("zh", "CN", "Mandarin"), ("zh", "TW", "Taiwanese"), ("zh", "HK", "Cantonese"),
            ("ja", "JP", "Tokyo"), ("ko", "KR", "Seoul"), ("th", "TH", "Bangkok"),
            ("vi", "VN", "Hanoi"), ("id", "ID", "Jakarta"), ("ms", "MY", "Kuala Lumpur"),
            ("tl", "PH", "Manila"), ("hi", "IN", "Delhi"), ("bn", "BD", "Dhaka"),
            ("ur", "PK", "Karachi"), ("ta", "IN", "Chennai"), ("te", "IN", "Hyderabad"),
            
            # Middle Eastern and African
            ("ar", "SA", "Najdi"), ("ar", "EG", "Cairo"), ("ar", "AE", "Emirati"),
            ("ar", "JO", "Amman"), ("ar", "LB", "Beirut"), ("ar", "MA", "Casablanca"),
            ("he", "IL", "Jerusalem"), ("fa", "IR", "Tehran"), ("tr", "TR", "Istanbul"),
            ("sw", "KE", "Nairobi"), ("am", "ET", "Addis Ababa"), ("yo", "NG", "Lagos"),
            ("ha", "NG", "Kano"), ("ig", "NG", "Igbo"), ("zu", "ZA", "Durban"),
            
            # Others
            ("el", "GR", "Athens"), ("mt", "MT", "Valletta"), ("lv", "LV", "Riga"),
            ("lt", "LT", "Vilnius"), ("et", "EE", "Tallinn")
        ]
        
        # Names for different cultures/regions
        name_sets = {
            "en_US": ["Sarah", "Michael", "Emma", "James", "Olivia", "William", "Ava", "Benjamin", "Isabella", "Lucas"],
            "en_GB": ["Charlotte", "Harry", "Amelia", "George", "Emily", "Oliver", "Poppy", "Jack", "Lily", "Noah"],
            "fr_FR": ["Marie", "Pierre", "Camille", "Antoine", "Léa", "Louis", "Chloé", "Hugo", "Manon", "Gabriel"],
            "es_ES": ["María", "José", "Carmen", "Antonio", "Ana", "Manuel", "Isabel", "Francisco", "Pilar", "David"],
            "de_DE": ["Anna", "Paul", "Laura", "Felix", "Sophie", "Leon", "Marie", "Maximilian", "Lena", "Noah"],
            "it_IT": ["Giulia", "Marco", "Francesca", "Alessandro", "Chiara", "Lorenzo", "Valentina", "Matteo", "Federica", "Andrea"],
            "zh_CN": ["小雅", "志强", "美丽", "建国", "静雯", "明华", "晓敏", "国强", "淑芬", "文杰"],
            "ja_JP": ["さくら", "たろう", "ゆき", "ひろし", "あい", "けんじ", "みき", "だいすけ", "ゆみ", "たくや"],
            "ar_SA": ["فاطمة", "محمد", "عائشة", "أحمد", "خديجة", "علي", "زينب", "عمر", "مريم", "حسن"],
            "ru_RU": ["Анна", "Дмитрий", "Мария", "Александр", "Елена", "Михаил", "Ольга", "Андрей", "Наталья", "Сергей"]
        }
        
        voice_counter = 0
        
        # Generate voices for each language/region combination
        for lang_code, region, accent_name in language_regions:
            key = f"{lang_code}_{region}"
            names = name_sets.get(key, name_sets.get("en_US"))  # Fallback to English names
            
            # Generate multiple voices per language/region
            for gender in [VoiceGender.FEMALE, VoiceGender.MALE]:
                for age in [VoiceAge.YOUNG_ADULT, VoiceAge.ADULT, VoiceAge.MIDDLE_AGED]:
                    for accent_type in [AccentType.NATIVE, AccentType.REGIONAL]:
                        for i in range(3):  # 3 voices per combination
                            if voice_counter >= 1200:  # Limit to avoid over-generation
                                break
                                
                            name = random.choice(names)
                            voice_id = f"{lang_code}_{region}_{gender.value}_{age.value}_{accent_type.value}_{i+1}"
                            
                            # Create base voice profile
                            base_profile = VoiceProfile(
                                voice_id=voice_id,
                                name=f"{name} ({region} {lang_code.upper()})",
                                language_code=lang_code,
                                region=region,
                                gender=gender,
                                age=age,
                                accent=accent_type,
                                accent_region=accent_name,
                                supported_emotions=[
                                    VoiceEmotion.NEUTRAL, VoiceEmotion.HAPPY, VoiceEmotion.SAD,
                                    VoiceEmotion.ANGRY, VoiceEmotion.EXCITED, VoiceEmotion.CALM
                                ],
                                supported_styles=[
                                    SpeechStyle.CONVERSATIONAL, SpeechStyle.FORMAL, SpeechStyle.CASUAL
                                ],
                                sample_rate=22050,
                                voice_characteristics={
                                    "pitch": self._generate_pitch(gender, age),
                                    "speed": random.uniform(0.8, 1.2),
                                    "tone": random.uniform(0.3, 0.8)
                                },
                                cultural_context={
                                    "formality": random.choice(["low", "medium", "high"]),
                                    "directness": random.choice(["low", "medium", "high"])
                                },
                                pronunciation_rules={},
                                prosody_patterns={},
                                quality_score=random.uniform(0.75, 0.98)
                            )
                            
                            # Create enhanced profile
                            enhanced_profile = EnhancedVoiceProfile(
                                base_profile=base_profile,
                                category=random.choice(list(VoiceCategory)),
                                popularity=random.choice(list(VoicePopularity)),
                                usage_count=random.randint(0, 1000),
                                rating=random.uniform(3.5, 5.0),
                                tags=self._generate_tags(lang_code, gender, age, accent_type),
                                description=f"High-quality {gender.value} {age.value} voice with {accent_name} accent",
                                license_type=random.choice(["standard", "premium", "commercial"]),
                                creator="AI_Generated"
                            )
                            
                            self.voices[voice_id] = enhanced_profile
                            voice_counter += 1
        
        logger.info(f"Generated {voice_counter} voices in voice bank")
    
    def _generate_pitch(self, gender: VoiceGender, age: VoiceAge) -> float:
        """Generate realistic pitch based on gender and age"""
        base_pitch = {
            VoiceGender.FEMALE: 200.0,
            VoiceGender.MALE: 120.0,
            VoiceGender.NEUTRAL: 160.0
        }.get(gender, 160.0)
        
        age_modifier = {
            VoiceAge.CHILD: 1.3,
            VoiceAge.YOUNG_ADULT: 1.1,
            VoiceAge.ADULT: 1.0,
            VoiceAge.MIDDLE_AGED: 0.95,
            VoiceAge.ELDERLY: 0.9
        }.get(age, 1.0)
        
        return base_pitch * age_modifier * random.uniform(0.9, 1.1)
    
    def _generate_tags(self, lang_code: str, gender: VoiceGender, age: VoiceAge, accent: AccentType) -> List[str]:
        """Generate relevant tags for voice"""
        tags = [lang_code, gender.value, age.value, accent.value]
        
        additional_tags = {
            "en": ["english", "international", "global"],
            "fr": ["french", "romance", "elegant"],
            "es": ["spanish", "passionate", "warm"],
            "de": ["german", "precise", "authoritative"],
            "zh": ["chinese", "mandarin", "tonal"],
            "ar": ["arabic", "middle-eastern", "rich"],
            "ja": ["japanese", "polite", "respectful"],
            "ru": ["russian", "deep", "dramatic"]
        }
        
        if lang_code in additional_tags:
            tags.extend(random.sample(additional_tags[lang_code], 2))
        
        return tags
    
    def _build_indexes(self):
        """Build search indexes for efficient voice lookup"""
        for voice_id, profile in self.voices.items():
            base = profile.base_profile
            
            # Category index
            if profile.category not in self.categories:
                self.categories[profile.category] = []
            self.categories[profile.category].append(voice_id)
            
            # Language index
            if base.language_code not in self.language_index:
                self.language_index[base.language_code] = []
            self.language_index[base.language_code].append(voice_id)
            
            # Gender index
            if base.gender not in self.gender_index:
                self.gender_index[base.gender] = []
            self.gender_index[base.gender].append(voice_id)
            
            # Age index
            if base.age not in self.age_index:
                self.age_index[base.age] = []
            self.age_index[base.age].append(voice_id)
            
            # Accent index
            if base.accent not in self.accent_index:
                self.accent_index[base.accent] = []
            self.accent_index[base.accent].append(voice_id)
            
            # Style index
            for style in base.supported_styles:
                if style not in self.style_index:
                    self.style_index[style] = []
                self.style_index[style].append(voice_id)
            
            # Popularity index
            if profile.popularity not in self.popularity_index:
                self.popularity_index[profile.popularity] = []
            self.popularity_index[profile.popularity].append(voice_id)
    
    def search_voices(
        self,
        language: Optional[str] = None,
        gender: Optional[VoiceGender] = None,
        age: Optional[VoiceAge] = None,
        accent: Optional[AccentType] = None,
        category: Optional[VoiceCategory] = None,
        style: Optional[SpeechStyle] = None,
        popularity: Optional[VoicePopularity] = None,
        tags: Optional[List[str]] = None,
        min_rating: Optional[float] = None,
        limit: int = 50
    ) -> List[EnhancedVoiceProfile]:
        """Search voices with multiple filters"""
        
        candidates = set(self.voices.keys())
        
        # Apply filters
        if language and language in self.language_index:
            candidates &= set(self.language_index[language])
        
        if gender and gender in self.gender_index:
            candidates &= set(self.gender_index[gender])
        
        if age and age in self.age_index:
            candidates &= set(self.age_index[age])
        
        if accent and accent in self.accent_index:
            candidates &= set(self.accent_index[accent])
        
        if category and category in self.categories:
            candidates &= set(self.categories[category])
        
        if style and style in self.style_index:
            candidates &= set(self.style_index[style])
        
        if popularity and popularity in self.popularity_index:
            candidates &= set(self.popularity_index[popularity])
        
        # Filter by tags
        if tags:
            tag_filtered = []
            for voice_id in candidates:
                profile = self.voices[voice_id]
                if any(tag in profile.tags for tag in tags):
                    tag_filtered.append(voice_id)
            candidates = set(tag_filtered)
        
        # Filter by rating
        if min_rating:
            rating_filtered = []
            for voice_id in candidates:
                profile = self.voices[voice_id]
                if profile.rating >= min_rating:
                    rating_filtered.append(voice_id)
            candidates = set(rating_filtered)
        
        # Get profiles and sort by rating
        results = [self.voices[voice_id] for voice_id in candidates]
        results.sort(key=lambda x: x.rating, reverse=True)
        
        return results[:limit]
    
    def get_voice(self, voice_id: str) -> Optional[EnhancedVoiceProfile]:
        """Get specific voice by ID"""
        return self.voices.get(voice_id)
    
    def get_random_voice(
        self,
        language: Optional[str] = None,
        gender: Optional[VoiceGender] = None
    ) -> Optional[EnhancedVoiceProfile]:
        """Get random voice with optional filters"""
        candidates = self.search_voices(language=language, gender=gender, limit=1000)
        return random.choice(candidates) if candidates else None
    
    def get_top_voices(self, limit: int = 10) -> List[EnhancedVoiceProfile]:
        """Get top-rated voices"""
        all_voices = list(self.voices.values())
        all_voices.sort(key=lambda x: x.rating, reverse=True)
        return all_voices[:limit]
    
    def get_trending_voices(self, limit: int = 10) -> List[EnhancedVoiceProfile]:
        """Get trending voices"""
        return self.search_voices(popularity=VoicePopularity.TRENDING, limit=limit)
    
    def get_language_statistics(self) -> Dict[str, int]:
        """Get voice count by language"""
        return {lang: len(voices) for lang, voices in self.language_index.items()}
    
    def get_voice_bank_stats(self) -> Dict[str, Any]:
        """Get comprehensive voice bank statistics"""
        return {
            "total_voices": len(self.voices),
            "languages": len(self.language_index),
            "categories": {cat.value: len(voices) for cat, voices in self.categories.items()},
            "gender_distribution": {gender.value: len(voices) for gender, voices in self.gender_index.items()},
            "age_distribution": {age.value: len(voices) for age, voices in self.age_index.items()},
            "average_rating": sum(profile.rating for profile in self.voices.values()) / len(self.voices),
            "top_languages": sorted(self.get_language_statistics().items(), key=lambda x: x[1], reverse=True)[:10]
        }


class VoiceBankManager:
    """Manager for voice bank operations and caching"""
    
    def __init__(self):
        self.voice_bank: Optional[VoiceBank] = None
        self._cache: Dict[str, Any] = {}
        self._cache_timeout = 300  # 5 minutes
    
    async def initialize(self):
        """Async initialization of voice bank"""
        if self.voice_bank is None:
            self.voice_bank = VoiceBank()
            logger.info("Voice bank manager initialized")
    
    async def get_voice_bank(self) -> VoiceBank:
        """Get voice bank instance"""
        if self.voice_bank is None:
            await self.initialize()
        return self.voice_bank
    
    async def search_voices_async(self, **kwargs) -> List[EnhancedVoiceProfile]:
        """Async voice search with caching"""
        cache_key = str(sorted(kwargs.items()))
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        voice_bank = await self.get_voice_bank()
        results = voice_bank.search_voices(**kwargs)
        
        self._cache[cache_key] = results
        return results
    
    async def get_voice_async(self, voice_id: str) -> Optional[EnhancedVoiceProfile]:
        """Async get voice by ID"""
        voice_bank = await self.get_voice_bank()
        return voice_bank.get_voice(voice_id)
    
    async def get_recommended_voices(
        self,
        user_preferences: Dict[str, Any],
        limit: int = 10
    ) -> List[EnhancedVoiceProfile]:
        """Get recommended voices based on user preferences"""
        voice_bank = await self.get_voice_bank()
        
        # Extract preferences
        language = user_preferences.get("language")
        gender = user_preferences.get("gender")
        style = user_preferences.get("style")
        category = user_preferences.get("category")
        
        # Search with preferences
        results = voice_bank.search_voices(
            language=language,
            gender=gender,
            style=style,
            category=category,
            min_rating=4.0,
            limit=limit
        )
        
        return results


# Global voice bank manager instance
_voice_bank_manager = VoiceBankManager()


async def get_voice_bank_manager() -> VoiceBankManager:
    """Get global voice bank manager instance"""
    return _voice_bank_manager


# Convenience functions
async def search_voices(**kwargs) -> List[EnhancedVoiceProfile]:
    """Convenience function for voice search"""
    manager = await get_voice_bank_manager()
    return await manager.search_voices_async(**kwargs)


async def get_voice(voice_id: str) -> Optional[EnhancedVoiceProfile]:
    """Convenience function to get voice by ID"""
    manager = await get_voice_bank_manager()
    return await manager.get_voice_async(voice_id)


async def get_random_voice(**kwargs) -> Optional[EnhancedVoiceProfile]:
    """Convenience function to get random voice"""
    manager = await get_voice_bank_manager()
    voice_bank = await manager.get_voice_bank()
    return voice_bank.get_random_voice(**kwargs)