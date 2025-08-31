"""
Enhanced Amazigh (Berber) Linguistic Support Engine - Ainflue Platform
================================================================================
Module: core/i18n/amazigh_enhanced_support.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Advanced Amazigh/Berber Linguistic Processing Engine
Responsibility: Comprehensive Amazigh dialect support, cultural adaptation, and linguistic processing
Technologies: Python, Amazigh Linguistics, Cultural Processing, Dialect Analysis
================================================================================

⚠️  PROPRIETARY SOFTWARE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Text analysis → Dialect detection → Amazigh linguistic processing → Cultural context integration → 
Script conversion → Regional adaptation → Cultural preservation → Modern integration
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from collections import defaultdict
import os

logger = logging.getLogger(__name__)


class AmazighDialect(Enum):
    """Major Amazigh/Berber dialects"""
    KABYLE = "kabyle"                    # Algeria (Taqbaylit)
    TAMAZIGHT_CENTRAL = "tamazight_central"  # Morocco Central Atlas
    TASHELHIT = "tashelhit"             # Morocco Souss region
    TARIFIT = "tarifit"                 # Morocco Rif region
    TAMAZIGHT_STANDARD = "tamazight_standard"  # Standard Tamazight
    TUAREG = "tuareg"                   # Sahara region
    CHENOUA = "chenoua"                 # Algeria coastal
    MZAB = "mzab"                       # Algeria M'zab valley
    SHENWA = "shenwa"                   # Algeria
    CHAOUIA = "chaouia"                 # Algeria Aurès


class AmazighScript(Enum):
    """Amazigh writing systems"""
    TIFINAGH = "tifinagh"               # Traditional Berber script
    LATIN = "latin"                     # Latin alphabet adaptation
    ARABIC = "arabic"                   # Arabic script adaptation
    NEO_TIFINAGH = "neo_tifinagh"       # Modern standardized Tifinagh


class CulturalContext(Enum):
    """Amazigh cultural contexts"""
    TRADITIONAL = "traditional"         # Traditional cultural context
    MODERN = "modern"                   # Contemporary usage
    ACADEMIC = "academic"               # Scholarly/educational
    LITERARY = "literary"               # Poetry and literature
    CEREMONIAL = "ceremonial"           # Religious/ceremonial
    COMMERCIAL = "commercial"           # Business context
    DIGITAL = "digital"                 # Online/social media


@dataclass
class AmazighWord:
    """Amazigh word with linguistic information"""
    word: str
    dialect: AmazighDialect
    script: AmazighScript
    meaning: str
    root: Optional[str] = None
    grammatical_info: Dict[str, str] = field(default_factory=dict)
    cultural_context: List[CulturalContext] = field(default_factory=list)
    regional_variants: Dict[AmazighDialect, str] = field(default_factory=dict)
    pronunciation: Optional[str] = None
    etymology: Optional[str] = None
    usage_frequency: float = 0.5  # 0-1 frequency score
    modern_relevance: float = 0.5  # 0-1 relevance in modern context


@dataclass
class AmazighPhrase:
    """Amazigh phrase with cultural information"""
    phrase: str
    dialect: AmazighDialect
    meaning: str
    cultural_significance: str
    usage_context: List[str]
    similar_phrases: List[str] = field(default_factory=list)
    ceremony_usage: Optional[str] = None
    seasonal_relevance: Optional[str] = None


@dataclass
class DialectMapping:
    """Mapping between Amazigh dialects"""
    source_dialect: AmazighDialect
    target_dialect: AmazighDialect
    word_mappings: Dict[str, str]
    phonetic_rules: List[Tuple[str, str]]  # (pattern, replacement)
    cultural_adaptations: Dict[str, str]
    confidence_score: float


@dataclass
class AmazighProcessingResult:
    """Result of Amazigh text processing"""
    original_text: str
    processed_text: str
    detected_dialect: AmazighDialect
    script_type: AmazighScript
    words_analyzed: List[AmazighWord]
    cultural_elements: List[str]
    suggested_improvements: List[str]
    regional_adaptations: Dict[AmazighDialect, str]
    confidence_score: float
    metadata: Dict[str, Any]


class AmazighEnhancedSupport:
    """Advanced Amazigh/Berber linguistic support and cultural adaptation engine"""
    
    def __init__(self):
        self.dialect_vocabularies: Dict[AmazighDialect, Dict[str, AmazighWord]] = {}
        self.cultural_phrases: Dict[AmazighDialect, List[AmazighPhrase]] = {}
        self.dialect_mappings: Dict[Tuple[AmazighDialect, AmazighDialect], DialectMapping] = {}
        self.script_converters: Dict[Tuple[AmazighScript, AmazighScript], Dict[str, str]] = {}
        
        # Initialize linguistic data
        self._initialize_vocabularies()
        self._initialize_cultural_phrases()
        self._initialize_dialect_mappings()
        self._initialize_script_converters()
        
        logger.info("Enhanced Amazigh Support Engine initialized")
    
    def _initialize_vocabularies(self):
        """Initialize comprehensive Amazigh vocabularies"""
        
        # Kabyle (Taqbaylit) vocabulary - Algeria
        kabyle_words = {
            # Basic greetings and social
            "azul": AmazighWord("azul", AmazighDialect.KABYLE, AmazighScript.LATIN, "hello/peace", 
                               cultural_context=[CulturalContext.TRADITIONAL, CulturalContext.MODERN]),
            "ansuf": AmazighWord("ansuf", AmazighDialect.KABYLE, AmazighScript.LATIN, "welcome",
                                cultural_context=[CulturalContext.TRADITIONAL, CulturalContext.CEREMONIAL]),
            "tanemmirt": AmazighWord("tanemmirt", AmazighDialect.KABYLE, AmazighScript.LATIN, "thank you",
                                   cultural_context=[CulturalContext.TRADITIONAL, CulturalContext.MODERN]),
            "ar tiklit": AmazighWord("ar tiklit", AmazighDialect.KABYLE, AmazighScript.LATIN, "see you later",
                                    cultural_context=[CulturalContext.MODERN]),
            
            # Family and relationships
            "tawacult": AmazighWord("tawacult", AmazighDialect.KABYLE, AmazighScript.LATIN, "family",
                                   cultural_context=[CulturalContext.TRADITIONAL, CulturalContext.MODERN]),
            "tayemmatt": AmazighWord("tayemmatt", AmazighDialect.KABYLE, AmazighScript.LATIN, "mother",
                                    cultural_context=[CulturalContext.TRADITIONAL]),
            "baba": AmazighWord("baba", AmazighDialect.KABYLE, AmazighScript.LATIN, "father",
                               cultural_context=[CulturalContext.TRADITIONAL]),
            "gma": AmazighWord("gma", AmazighDialect.KABYLE, AmazighScript.LATIN, "brother",
                              cultural_context=[CulturalContext.TRADITIONAL]),
            
            # Technology and modern terms
            "aseɣzaf": AmazighWord("aseɣzaf", AmazighDialect.KABYLE, AmazighScript.LATIN, "computer",
                                  cultural_context=[CulturalContext.MODERN, CulturalContext.DIGITAL]),
            "anɣar": AmazighWord("anɣar", AmazighDialect.KABYLE, AmazighScript.LATIN, "internet",
                                cultural_context=[CulturalContext.MODERN, CulturalContext.DIGITAL]),
            "asedda": AmazighWord("asedda", AmazighDialect.KABYLE, AmazighScript.LATIN, "website",
                                 cultural_context=[CulturalContext.DIGITAL]),
            
            # Business and commerce
            "lɣerc": AmazighWord("lɣerc", AmazighDialect.KABYLE, AmazighScript.LATIN, "work/job",
                                cultural_context=[CulturalContext.MODERN, CulturalContext.COMMERCIAL]),
            "zzenz": AmazighWord("zzenz", AmazighDialect.KABYLE, AmazighScript.LATIN, "sell",
                                cultural_context=[CuzturalContext.COMMERCIAL]),
            "sɣu": AmazighWord("sɣu", AmazighDialect.KABYLE, AmazighScript.LATIN, "buy",
                              cultural_context=[CulturalContext.COMMERCIAL]),
            
            # Cultural and traditional terms
            "tifinagh": AmazighWord("tifinagh", AmazighDialect.KABYLE, AmazighScript.LATIN, "tifinagh script",
                                   cultural_context=[CulturalContext.TRADITIONAL, CulturalContext.ACADEMIC]),
            "amɣar": AmazighWord("amɣar", AmazighDialect.KABYLE, AmazighScript.LATIN, "elder/wise man",
                                cultural_context=[CulturalContext.TRADITIONAL, CulturalContext.CEREMONIAL]),
            "tigejda": AmazighWord("tigejda", AmazighDialect.KABYLE, AmazighScript.LATIN, "traditional decoration",
                                  cultural_context=[CulturalContext.TRADITIONAL]),
            
            # Nature and environment
            "adrar": AmazighWord("adrar", AmazighDialect.KABYLE, AmazighScript.LATIN, "mountain",
                                cultural_context=[CulturalContext.TRADITIONAL]),
            "asif": AmazighWord("asif", AmazighDialect.KABYLE, AmazighScript.LATIN, "river",
                               cultural_context=[CulturalContext.TRADITIONAL]),
            "tafukt": AmazighWord("tafukt", AmazighDialect.KABYLE, AmazighScript.LATIN, "sun",
                                 cultural_context=[CulturalContext.TRADITIONAL, CulturalContext.LITERARY])
        }
        
        # Central Atlas Tamazight vocabulary - Morocco
        central_tamazight_words = {
            "azul": AmazighWord("azul", AmazighDialect.TAMAZIGHT_CENTRAL, AmazighScript.LATIN, "hello/peace"),
            "ansuf": AmazighWord("ansuf", AmazighDialect.TAMAZIGHT_CENTRAL, AmazighScript.LATIN, "welcome"),
            "tanammert": AmazighWord("tanammert", AmazighDialect.TAMAZIGHT_CENTRAL, AmazighScript.LATIN, "thank you"),
            "tawacult": AmazighWord("tawacult", AmazighDialect.TAMAZIGHT_CENTRAL, AmazighScript.LATIN, "family"),
            "yemma": AmazighWord("yemma", AmazighDialect.TAMAZIGHT_CENTRAL, AmazighScript.LATIN, "mother"),
            "baba": AmazighWord("baba", AmazighDialect.TAMAZIGHT_CENTRAL, AmazighScript.LATIN, "father"),
            "adrar": AmazighWord("adrar", AmazighDialect.TAMAZIGHT_CENTRAL, AmazighScript.LATIN, "mountain"),
            "aman": AmazighWord("aman", AmazighDialect.TAMAZIGHT_CENTRAL, AmazighScript.LATIN, "water"),
            "tafukt": AmazighWord("tafukt", AmazighDialect.TAMAZIGHT_CENTRAL, AmazighScript.LATIN, "sun"),
            "ayur": AmazighWord("ayur", AmazighDialect.TAMAZIGHT_CENTRAL, AmazighScript.LATIN, "moon")
        }
        
        # Tashelhit vocabulary - Morocco Souss
        tashelhit_words = {
            "azul": AmazighWord("azul", AmazighDialect.TASHELHIT, AmazighScript.LATIN, "hello/peace"),
            "ansuf": AmazighWord("ansuf", AmazighDialect.TASHELHIT, AmazighScript.LATIN, "welcome"),
            "tanammirt": AmazighWord("tanammirt", AmazighDialect.TASHELHIT, AmazighScript.LATIN, "thank you"),
            "tawacult": AmazighWord("tawacult", AmazighDialect.TASHELHIT, AmazighScript.LATIN, "family"),
            "yemma": AmazighWord("yemma", AmazighDialect.TASHELHIT, AmazighScript.LATIN, "mother"),
            "baba": AmazighWord("baba", AmazighDialect.TASHELHIT, AmazighScript.LATIN, "father"),
            "adrar": AmazighWord("adrar", AmazighDialect.TASHELHIT, AmazighScript.LATIN, "mountain"),
            "aman": AmazighWord("aman", AmazighDialect.TASHELHIT, AmazighScript.LATIN, "water"),
            "tafukt": AmazighWord("tafukt", AmazighDialect.TASHELHIT, AmazighScript.LATIN, "sun"),
            "ayur": AmazighWord("ayur", AmazighDialect.TASHELHIT, AmazighScript.LATIN, "moon"),
            "argaz": AmazighWord("argaz", AmazighDialect.TASHELHIT, AmazighScript.LATIN, "man"),
            "tamtut": AmazighWord("tamtut", AmazighDialect.TASHELHIT, AmazighScript.LATIN, "woman")
        }
        
        # Store vocabularies
        self.dialect_vocabularies[AmazighDialect.KABYLE] = kabyle_words
        self.dialect_vocabularies[AmazighDialect.TAMAZIGHT_CENTRAL] = central_tamazight_words
        self.dialect_vocabularies[AmazighDialect.TASHELHIT] = tashelhit_words
        
        logger.info(f"Initialized vocabularies for {len(self.dialect_vocabularies)} Amazigh dialects")
    
    def _initialize_cultural_phrases(self):
        """Initialize cultural phrases and expressions"""
        
        # Kabyle cultural phrases
        kabyle_phrases = [
            AmazighPhrase(
                phrase="Azul fell-ak a gma",
                dialect=AmazighDialect.KABYLE,
                meaning="Peace be upon you, brother",
                cultural_significance="Traditional greeting showing respect and brotherhood",
                usage_context=["greeting", "respect", "brotherhood"],
                ceremony_usage="Used in traditional gatherings and ceremonies"
            ),
            AmazighPhrase(
                phrase="Akal d amawal",
                dialect=AmazighDialect.KABYLE,
                meaning="Land and language",
                cultural_significance="Emphasizes the connection between territory and linguistic identity",
                usage_context=["cultural_identity", "nationalism", "heritage"],
                ceremony_usage="Cultural events and identity discussions"
            ),
            AmazighPhrase(
                phrase="Tifinagh n medden",
                dialect=AmazighDialect.KABYLE,
                meaning="Tifinagh of the people",
                cultural_significance="Refers to the traditional writing system as belonging to all Amazigh people",
                usage_context=["writing", "heritage", "education"],
                ceremony_usage="Educational and cultural preservation contexts"
            ),
            AmazighPhrase(
                phrase="Tamurt n leqbayel",
                dialect=AmazighDialect.KABYLE,
                meaning="Land of the Kabyles",
                cultural_significance="References the traditional homeland and cultural territory",
                usage_context=["territorial_identity", "cultural_pride", "homeland"],
                ceremony_usage="Cultural celebrations and heritage events"
            )
        ]
        
        # Central Atlas Tamazight cultural phrases
        central_phrases = [
            AmazighPhrase(
                phrase="Tamazight n Atlas",
                dialect=AmazighDialect.TAMAZIGHT_CENTRAL,
                meaning="Tamazight of the Atlas",
                cultural_significance="Identifies the specific regional variety and its connection to the Atlas Mountains",
                usage_context=["regional_identity", "geographic_pride", "dialect_distinction"],
                ceremony_usage="Regional cultural events"
            ),
            AmazighPhrase(
                phrase="Adrar n baba",
                dialect=AmazighDialect.TAMAZIGHT_CENTRAL,
                meaning="Mountain of the father",
                cultural_significance="Shows respect for ancestral land and patriarchal heritage",
                usage_context=["ancestral_respect", "land_connection", "family_heritage"],
                ceremony_usage="Family gatherings and ancestral honoring"
            )
        ]
        
        # Tashelhit cultural phrases
        tashelhit_phrases = [
            AmazighPhrase(
                phrase="Souss n imazighen",
                dialect=AmazighDialect.TASHELHIT,
                meaning="Souss of the Berbers",
                cultural_significance="References the Souss valley as an important Amazigh cultural region",
                usage_context=["regional_pride", "cultural_territory", "identity"],
                ceremony_usage="Regional celebrations and cultural events"
            ),
            AmazighPhrase(
                phrase="Tifawin n tmurt",
                dialect=AmazighDialect.TASHELHIT,
                meaning="Lights of the land",
                cultural_significance="Metaphor for cultural knowledge and wisdom illuminating the community",
                usage_context=["wisdom", "cultural_enlightenment", "education"],
                ceremony_usage="Educational ceremonies and wisdom sharing"
            )
        ]
        
        # Store cultural phrases
        self.cultural_phrases[AmazighDialect.KABYLE] = kabyle_phrases
        self.cultural_phrases[AmazighDialect.TAMAZIGHT_CENTRAL] = central_phrases
        self.cultural_phrases[AmazighDialect.TASHELHIT] = tashelhit_phrases
        
        logger.info(f"Initialized cultural phrases for {len(self.cultural_phrases)} dialects")
    
    def _initialize_dialect_mappings(self):
        """Initialize mappings between Amazigh dialects"""
        
        # Kabyle to Central Atlas Tamazight
        kabyle_to_central = DialectMapping(
            source_dialect=AmazighDialect.KABYLE,
            target_dialect=AmazighDialect.TAMAZIGHT_CENTRAL,
            word_mappings={
                "tanemmirt": "tanammert",  # thank you
                "tayemmatt": "yemma",     # mother  
                "tiklit": "tamurt",       # time/place
                "lɣerc": "tafelwit",      # work
                "aseɣzaf": "aselkim"      # computer
            },
            phonetic_rules=[
                (r"mm", "m"),      # Double m becomes single m
                (r"ɣz", "lk"),     # ɣz sound change to lk
                (r"ye", "y")       # ye simplification
            ],
            cultural_adaptations={
                "ceremonial_forms": "more_arabic_influence",
                "modern_terms": "french_borrowings"
            },
            confidence_score=0.7
        )
        
        # Central Atlas to Tashelhit
        central_to_tashelhit = DialectMapping(
            source_dialect=AmazighDialect.TAMAZIGHT_CENTRAL,
            target_dialect=AmazighDialect.TASHELHIT,
            word_mappings={
                "tanammert": "tanammirt",  # thank you
                "yemma": "yemma",         # mother (same)
                "baba": "baba",           # father (same)
                "tawacult": "tawacult"    # family (same)
            },
            phonetic_rules=[
                (r"mm", "mm"),     # Preserves double consonants
                (r"a$", "a")       # Final vowels preserved
            ],
            cultural_adaptations={
                "traditional_forms": "more_conservative",
                "social_structure": "tribal_emphasis"
            },
            confidence_score=0.8
        )
        
        # Store mappings
        self.dialect_mappings[(AmazighDialect.KABYLE, AmazighDialect.TAMAZIGHT_CENTRAL)] = kabyle_to_central
        self.dialect_mappings[(AmazighDialect.TAMAZIGHT_CENTRAL, AmazighDialect.TASHELHIT)] = central_to_tashelhit
        
        logger.info(f"Initialized {len(self.dialect_mappings)} dialect mappings")
    
    def _initialize_script_converters(self):
        """Initialize script conversion tables"""
        
        # Latin to Tifinagh conversion (basic mapping)
        latin_to_tifinagh = {
            "a": "ⴰ", "b": "ⴱ", "c": "ⵛ", "d": "ⴷ", "e": "ⴻ", "f": "ⴼ",
            "g": "ⴳ", "h": "ⵀ", "i": "ⵉ", "j": "ⵊ", "k": "ⴽ", "l": "ⵍ",
            "m": "ⵎ", "n": "ⵏ", "o": "ⵓ", "p": "ⵒ", "q": "ⵇ", "r": "ⵔ",
            "s": "ⵙ", "t": "ⵜ", "u": "ⵓ", "v": "ⵠ", "w": "ⵡ", "x": "ⵅ",
            "y": "ⵢ", "z": "ⵣ",
            # Special Amazigh characters
            "ɣ": "ⵖ", "ḥ": "ⵃ", "ṛ": "ⵕ", "ṣ": "ⵚ", "ṭ": "ⵟ", "ẓ": "ⵥ",
            "č": "ⵛ", "š": "ⵛ", "ž": "ⵊ"
        }
        
        # Tifinagh to Latin (reverse mapping)
        tifinagh_to_latin = {v: k for k, v in latin_to_tifinagh.items()}
        
        # Store converters
        self.script_converters[(AmazighScript.LATIN, AmazighScript.TIFINAGH)] = latin_to_tifinagh
        self.script_converters[(AmazighScript.TIFINAGH, AmazighScript.LATIN)] = tifinagh_to_latin
        
        logger.info("Initialized script converters")
    
    async def detect_amazigh_dialect(self, text: str) -> Tuple[AmazighDialect, float]:
        """Detect Amazigh dialect from text"""
        
        try:
            # Analyze text for dialect-specific features
            dialect_scores = {}
            
            for dialect, vocabulary in self.dialect_vocabularies.items():
                score = 0.0
                word_count = 0
                
                # Check for dialect-specific words
                words = text.lower().split()
                for word in words:
                    if word in vocabulary:
                        score += vocabulary[word].usage_frequency
                        word_count += 1
                
                # Normalize score
                if word_count > 0:
                    dialect_scores[dialect] = score / word_count
                else:
                    dialect_scores[dialect] = 0.0
            
            # Find dialect with highest score
            if dialect_scores:
                best_dialect = max(dialect_scores, key=dialect_scores.get)
                confidence = dialect_scores[best_dialect]
                return best_dialect, confidence
            
            # Default to Kabyle if no matches
            return AmazighDialect.KABYLE, 0.0
            
        except Exception as e:
            logger.error(f"Error detecting Amazigh dialect: {e}")
            return AmazighDialect.KABYLE, 0.0
    
    async def detect_script_type(self, text: str) -> AmazighScript:
        """Detect script type of Amazigh text"""
        
        # Check for Tifinagh characters
        tifinagh_chars = "ⴰⴱⵛⴷⴻⴼⴳⵀⵉⵊⴽⵍⵎⵏⵓⵒⵇⵔⵙⵜⵓⵠⵡⵅⵢⵣⵖⵃⵕⵚⵟⵥ"
        if any(char in tifinagh_chars for char in text):
            return AmazighScript.TIFINAGH
        
        # Check for Arabic characters
        arabic_chars = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"
        if any(char in arabic_chars for char in text):
            return AmazighScript.ARABIC
        
        # Default to Latin
        return AmazighScript.LATIN
    
    async def convert_script(
        self,
        text: str,
        source_script: AmazighScript,
        target_script: AmazighScript
    ) -> str:
        """Convert between Amazigh scripts"""
        
        try:
            converter_key = (source_script, target_script)
            
            if converter_key in self.script_converters:
                converter = self.script_converters[converter_key]
                converted_text = ""
                
                for char in text:
                    converted_text += converter.get(char.lower(), char)
                
                return converted_text
            
            # If no converter available, return original text
            logger.warning(f"No converter available for {source_script} to {target_script}")
            return text
            
        except Exception as e:
            logger.error(f"Error converting script: {e}")
            return text
    
    async def translate_between_dialects(
        self,
        text: str,
        source_dialect: AmazighDialect,
        target_dialect: AmazighDialect
    ) -> str:
        """Translate between Amazigh dialects"""
        
        try:
            mapping_key = (source_dialect, target_dialect)
            
            if mapping_key in self.dialect_mappings:
                mapping = self.dialect_mappings[mapping_key]
                
                # Apply word mappings
                translated_text = text
                for source_word, target_word in mapping.word_mappings.items():
                    translated_text = re.sub(
                        r'\b' + re.escape(source_word) + r'\b',
                        target_word,
                        translated_text,
                        flags=re.IGNORECASE
                    )
                
                # Apply phonetic rules
                for pattern, replacement in mapping.phonetic_rules:
                    translated_text = re.sub(pattern, replacement, translated_text)
                
                return translated_text
            
            # If no mapping available, try reverse mapping
            reverse_key = (target_dialect, source_dialect)
            if reverse_key in self.dialect_mappings:
                # Use reverse mapping (less accurate)
                mapping = self.dialect_mappings[reverse_key]
                translated_text = text
                
                # Reverse word mappings
                for target_word, source_word in mapping.word_mappings.items():
                    translated_text = re.sub(
                        r'\b' + re.escape(source_word) + r'\b',
                        target_word,
                        translated_text,
                        flags=re.IGNORECASE
                    )
                
                return translated_text
            
            logger.warning(f"No translation mapping for {source_dialect} to {target_dialect}")
            return text
            
        except Exception as e:
            logger.error(f"Error translating between dialects: {e}")
            return text
    
    async def process_amazigh_text(
        self,
        text: str,
        target_dialect: Optional[AmazighDialect] = None,
        target_script: Optional[AmazighScript] = None,
        cultural_context: Optional[CulturalContext] = None
    ) -> AmazighProcessingResult:
        """Comprehensive Amazigh text processing"""
        
        try:
            # Detect source dialect and script
            detected_dialect, dialect_confidence = await self.detect_amazigh_dialect(text)
            detected_script = await self.detect_script_type(text)
            
            processed_text = text
            words_analyzed = []
            cultural_elements = []
            suggested_improvements = []
            regional_adaptations = {}
            
            # Analyze words
            words = text.split()
            for word in words:
                word_lower = word.lower().strip('.,!?;:')
                
                # Check if word exists in vocabulary
                if detected_dialect in self.dialect_vocabularies:
                    vocab = self.dialect_vocabularies[detected_dialect]
                    if word_lower in vocab:
                        amazigh_word = vocab[word_lower]
                        words_analyzed.append(amazigh_word)
                        
                        # Extract cultural elements
                        for context in amazigh_word.cultural_context:
                            if context.value not in cultural_elements:
                                cultural_elements.append(context.value)
            
            # Convert to target dialect if specified
            if target_dialect and target_dialect != detected_dialect:
                processed_text = await self.translate_between_dialects(
                    processed_text, detected_dialect, target_dialect
                )
                regional_adaptations[target_dialect] = processed_text
            
            # Convert to target script if specified
            if target_script and target_script != detected_script:
                processed_text = await self.convert_script(
                    processed_text, detected_script, target_script
                )
            
            # Generate suggestions
            if cultural_context:
                suggested_improvements = await self._generate_cultural_suggestions(
                    text, detected_dialect, cultural_context
                )
            
            # Generate regional adaptations
            for dialect in [AmazighDialect.KABYLE, AmazighDialect.TAMAZIGHT_CENTRAL, AmazighDialect.TASHELHIT]:
                if dialect != detected_dialect:
                    adapted_text = await self.translate_between_dialects(
                        text, detected_dialect, dialect
                    )
                    regional_adaptations[dialect] = adapted_text
            
            return AmazighProcessingResult(
                original_text=text,
                processed_text=processed_text,
                detected_dialect=detected_dialect,
                script_type=detected_script,
                words_analyzed=words_analyzed,
                cultural_elements=cultural_elements,
                suggested_improvements=suggested_improvements,
                regional_adaptations=regional_adaptations,
                confidence_score=dialect_confidence,
                metadata={
                    "processing_timestamp": datetime.now(timezone.utc).isoformat(),
                    "target_dialect": target_dialect.value if target_dialect else None,
                    "target_script": target_script.value if target_script else None,
                    "cultural_context": cultural_context.value if cultural_context else None
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing Amazigh text: {e}")
            return AmazighProcessingResult(
                original_text=text,
                processed_text=text,
                detected_dialect=AmazighDialect.KABYLE,
                script_type=AmazighScript.LATIN,
                words_analyzed=[],
                cultural_elements=[],
                suggested_improvements=[f"Processing error: {str(e)}"],
                regional_adaptations={},
                confidence_score=0.0,
                metadata={"error": str(e)}
            )
    
    async def _generate_cultural_suggestions(
        self,
        text: str,
        dialect: AmazighDialect,
        context: CulturalContext
    ) -> List[str]:
        """Generate cultural improvement suggestions"""
        
        suggestions = []
        
        # Context-specific suggestions
        if context == CulturalContext.TRADITIONAL:
            suggestions.extend([
                "Consider using traditional greetings like 'azul fell-ak'",
                "Include references to ancestral wisdom",
                "Use formal respectful language for elders"
            ])
        
        elif context == CulturalContext.MODERN:
            suggestions.extend([
                "Consider modern Amazigh terminology for technology",
                "Balance traditional and contemporary expressions",
                "Include relevant cultural adaptations for digital contexts"
            ])
        
        elif context == CulturalContext.CEREMONIAL:
            suggestions.extend([
                "Use elevated, respectful language",
                "Include traditional ceremonial phrases",
                "Reference cultural and spiritual elements appropriately"
            ])
        
        elif context == CulturalContext.COMMERCIAL:
            suggestions.extend([
                "Use clear, professional Amazigh terminology",
                "Include cultural trust-building elements",
                "Consider regional business customs"
            ])
        
        # Dialect-specific suggestions
        if dialect == AmazighDialect.KABYLE:
            suggestions.append("Consider Kabyle-specific cultural references")
        elif dialect == AmazighDialect.TAMAZIGHT_CENTRAL:
            suggestions.append("Include Atlas Mountain cultural elements")
        elif dialect == AmazighDialect.TASHELHIT:
            suggestions.append("Reference Souss valley cultural traditions")
        
        return suggestions
    
    async def get_cultural_phrases(self, dialect: AmazighDialect) -> List[AmazighPhrase]:
        """Get cultural phrases for specific dialect"""
        return self.cultural_phrases.get(dialect, [])
    
    async def suggest_amazigh_content_enhancements(
        self,
        content: str,
        target_audience: str,
        platform: str
    ) -> Dict[str, Any]:
        """Suggest Amazigh-specific content enhancements"""
        
        try:
            # Detect dialect and process content
            processing_result = await self.process_amazigh_text(content)
            
            enhancements = {
                "dialect_suggestions": [],
                "cultural_adaptations": [],
                "script_options": [],
                "platform_optimizations": [],
                "audience_targeting": []
            }
            
            # Dialect suggestions
            for dialect, adapted_text in processing_result.regional_adaptations.items():
                enhancements["dialect_suggestions"].append({
                    "dialect": dialect.value,
                    "adapted_text": adapted_text,
                    "target_region": self._get_dialect_region(dialect)
                })
            
            # Cultural adaptations
            if processing_result.cultural_elements:
                enhancements["cultural_adaptations"] = [
                    f"Content includes {element} cultural elements" 
                    for element in processing_result.cultural_elements
                ]
            
            # Script options
            if processing_result.script_type == AmazighScript.LATIN:
                tifinagh_version = await self.convert_script(
                    content, AmazighScript.LATIN, AmazighScript.TIFINAGH
                )
                enhancements["script_options"].append({
                    "script": "tifinagh",
                    "text": tifinagh_version,
                    "use_case": "Traditional and cultural authenticity"
                })
            
            # Platform optimizations
            platform_advice = self._get_platform_advice(platform, processing_result.detected_dialect)
            enhancements["platform_optimizations"] = platform_advice
            
            # Audience targeting
            audience_advice = self._get_audience_advice(target_audience, processing_result.detected_dialect)
            enhancements["audience_targeting"] = audience_advice
            
            return enhancements
            
        except Exception as e:
            logger.error(f"Error suggesting Amazigh content enhancements: {e}")
            return {"error": str(e)}
    
    def _get_dialect_region(self, dialect: AmazighDialect) -> str:
        """Get primary region for dialect"""
        region_mapping = {
            AmazighDialect.KABYLE: "Algeria (Kabylie)",
            AmazighDialect.TAMAZIGHT_CENTRAL: "Morocco (Central Atlas)",
            AmazighDialect.TASHELHIT: "Morocco (Souss-Massa)",
            AmazighDialect.TARIFIT: "Morocco (Rif)",
            AmazighDialect.TUAREG: "Sahara (Niger, Mali, Algeria)",
            AmazighDialect.CHENOUA: "Algeria (Coastal)",
            AmazighDialect.MZAB: "Algeria (M'zab Valley)",
            AmazighDialect.SHENWA: "Algeria (Central)",
            AmazighDialect.CHAOUIA: "Algeria (Aurès Mountains)"
        }
        return region_mapping.get(dialect, "Unknown region")
    
    def _get_platform_advice(self, platform: str, dialect: AmazighDialect) -> List[str]:
        """Get platform-specific advice for Amazigh content"""
        
        base_advice = [
            "Use hashtags in both Amazigh and regional languages",
            "Include cultural visual elements",
            "Tag relevant Amazigh cultural accounts"
        ]
        
        platform_specific = {
            "instagram": [
                "Use Tifinagh script in visual posts for authenticity",
                "Share traditional crafts and cultural practices",
                "Use #tamazight #berber hashtags"
            ],
            "facebook": [
                "Create bilingual posts (Amazigh + Arabic/French)",
                "Share cultural stories and heritage",
                "Engage with Amazigh community groups"
            ],
            "youtube": [
                "Create educational content about Amazigh culture",
                "Include subtitles in multiple scripts",
                "Focus on cultural preservation themes"
            ],
            "tiktok": [
                "Use traditional music and sounds",
                "Create cultural dance and craft content",
                "Engage with younger Amazigh diaspora"
            ]
        }
        
        return base_advice + platform_specific.get(platform.lower(), [])
    
    def _get_audience_advice(self, audience: str, dialect: AmazighDialect) -> List[str]:
        """Get audience-specific advice for Amazigh content"""
        
        audience_specific = {
            "young_adults": [
                "Mix traditional and modern elements",
                "Use contemporary Amazigh terminology",
                "Focus on cultural pride and identity"
            ],
            "families": [
                "Include family-oriented cultural content",
                "Use traditional storytelling elements",
                "Emphasize cultural transmission to children"
            ],
            "diaspora": [
                "Focus on cultural connection and nostalgia",
                "Provide cultural education and language learning",
                "Connect to homeland and traditions"
            ],
            "scholars": [
                "Use formal academic Amazigh terminology",
                "Include historical and linguistic references",
                "Focus on cultural preservation and research"
            ]
        }
        
        return audience_specific.get(audience.lower(), [
            "Use clear, respectful Amazigh language",
            "Include cultural context and explanations",
            "Respect traditional values and customs"
        ])
    
    async def health_check(self) -> bool:
        """Health check for Amazigh enhanced support"""
        try:
            # Check if vocabularies are loaded
            if not self.dialect_vocabularies:
                return False
            
            # Check if cultural phrases are loaded
            if not self.cultural_phrases:
                return False
            
            # Test dialect detection
            test_text = "azul fell-ak a gma"
            dialect, confidence = await self.detect_amazigh_dialect(test_text)
            
            if dialect and confidence >= 0:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Amazigh enhanced support health check failed: {e}")
            return False