"""
Dialect Processor Engine - Ainflue Platform
================================================================================
Module: core/i18n/dialect_processor.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Dialect Processing Engine - Advanced Linguistic Analysis
Responsibility: Multi-dialect detection, processing and regional variant support
Technologies: Python, NLP, Linguistic Models, Regional Dialect Analysis
================================================================================

  PROPRIETARY SOFTWARE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Text input → Dialect detection → Regional analysis → Variant identification → 
Linguistic features → Cultural markers → Processing recommendations
"""

import logging
import asyncio
import re
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class DialectFamily(Enum):
    """Major dialect families"""
    ARABIC = "arabic"
    ENGLISH = "english"
    SPANISH = "spanish"
    FRENCH = "french"
    CHINESE = "chinese"
    GERMAN = "german"
    ITALIAN = "italian"
    PORTUGUESE = "portuguese"
    BERBER_AMAZIGH = "berber_amazigh"
    KURDISH = "kurdish"
    PERSIAN = "persian"


class RegionalVariant(Enum):
    """Regional variants for dialects"""
    NORTHERN = "northern"
    SOUTHERN = "southern"
    EASTERN = "eastern"
    WESTERN = "western"
    CENTRAL = "central"
    COASTAL = "coastal"
    MOUNTAIN = "mountain"
    URBAN = "urban"
    RURAL = "rural"


class LinguisticFeature(Enum):
    """Linguistic features for dialect identification"""
    PHONETIC = "phonetic"
    LEXICAL = "lexical"
    GRAMMATICAL = "grammatical"
    SYNTACTIC = "syntactic"
    MORPHOLOGICAL = "morphological"
    SEMANTIC = "semantic"
    PROSODIC = "prosodic"


@dataclass
class DialectMarker:
    """Dialect identification marker"""
    pattern: str
    feature_type: LinguisticFeature
    confidence_weight: float
    regions: List[str]
    examples: List[str]
    context: str = ""


@dataclass
class DialectVariant:
    """Dialect variant information"""
    code: str
    name: str
    family: DialectFamily
    region: str
    country_codes: List[str]
    speakers_count: int
    regional_variant: RegionalVariant
    linguistic_features: Dict[LinguisticFeature, List[str]]
    typical_markers: List[DialectMarker]
    parent_language: str
    iso_codes: List[str]
    writing_system: str
    formality_levels: List[str]
    cultural_context: Dict[str, Any]


@dataclass
class DialectDetection:
    """Dialect detection result"""
    detected_dialect: str
    confidence_score: float
    detected_features: List[LinguisticFeature]
    matching_markers: List[DialectMarker]
    regional_indicators: List[str]
    alternative_dialects: List[Tuple[str, float]]
    linguistic_analysis: Dict[str, Any]
    processing_recommendations: List[str]


class DialectProcessor:
    """Advanced dialect processing and detection engine"""
    
    def __init__(self):
        self.dialect_variants: Dict[str, DialectVariant] = {}
        self.dialect_markers: Dict[str, List[DialectMarker]] = {}
        self.detection_cache: Dict[str, DialectDetection] = {}
        self.linguistic_patterns: Dict[str, re.Pattern] = {}
        
        # Initialize dialect data
        self._initialize_dialect_variants()
        self._initialize_dialect_markers()
        self._compile_linguistic_patterns()
        
        logger.info("Dialect Processor Engine initialized")
    
    def _initialize_dialect_variants(self):
        """Initialize major dialect variants"""
        
        # Arabic dialects
        self.dialect_variants["ar-eg"] = DialectVariant(
            code="ar-eg",
            name="Egyptian Arabic",
            family=DialectFamily.ARABIC,
            region="North Africa",
            country_codes=["EG"],
            speakers_count=70000000,
            regional_variant=RegionalVariant.NORTHERN,
            linguistic_features={
                LinguisticFeature.PHONETIC: ["j_pronunciation", "qaf_variation"],
                LinguisticFeature.LEXICAL: ["egyptian_vocabulary", "coptic_loanwords"],
                LinguisticFeature.GRAMMATICAL: ["verb_conjugation_patterns"]
            },
            typical_markers=[],
            parent_language="ar",
            iso_codes=["arz"],
            writing_system="arabic",
            formality_levels=["informal", "formal", "literary"],
            cultural_context={"media_influence": "high", "regional_prestige": "high"}
        )
        
        self.dialect_variants["ar-ma"] = DialectVariant(
            code="ar-ma",
            name="Moroccan Arabic (Darija)",
            family=DialectFamily.ARABIC,
            region="North Africa",
            country_codes=["MA"],
            speakers_count=35000000,
            regional_variant=RegionalVariant.WESTERN,
            linguistic_features={
                LinguisticFeature.PHONETIC: ["berber_influence", "unique_vowel_system"],
                LinguisticFeature.LEXICAL: ["berber_loanwords", "french_influence", "spanish_influence"],
                LinguisticFeature.GRAMMATICAL: ["simplified_conjugation"]
            },
            typical_markers=[],
            parent_language="ar",
            iso_codes=["ary"],
            writing_system="arabic",
            formality_levels=["colloquial", "formal"],
            cultural_context={"berber_influence": "high", "colonial_influence": "french_spanish"}
        )
        
        self.dialect_variants["ar-sy"] = DialectVariant(
            code="ar-sy",
            name="Levantine Arabic (Syrian)",
            family=DialectFamily.ARABIC,
            region="Middle East",
            country_codes=["SY", "LB", "JO", "PS"],
            speakers_count=40000000,
            regional_variant=RegionalVariant.CENTRAL,
            linguistic_features={
                LinguisticFeature.PHONETIC: ["qaf_glottal", "soft_pronunciation"],
                LinguisticFeature.LEXICAL: ["turkish_loanwords", "aramaic_substrate"],
                LinguisticFeature.GRAMMATICAL: ["present_tense_markers"]
            },
            typical_markers=[],
            parent_language="ar",
            iso_codes=["apc", "ajp"],
            writing_system="arabic",
            formality_levels=["informal", "formal"],
            cultural_context={"historical_importance": "high", "literary_tradition": "strong"}
        )
        
        # Berber/Amazigh dialects
        self.dialect_variants["tzm"] = DialectVariant(
            code="tzm",
            name="Central Atlas Tamazight",
            family=DialectFamily.BERBER_AMAZIGH,
            region="North Africa",
            country_codes=["MA"],
            speakers_count=3000000,
            regional_variant=RegionalVariant.MOUNTAIN,
            linguistic_features={
                LinguisticFeature.PHONETIC: ["pharyngeal_consonants", "gemination"],
                LinguisticFeature.LEXICAL: ["berber_root_system", "trilateral_roots"],
                LinguisticFeature.GRAMMATICAL: ["verb_aspect_system", "noun_state"]
            },
            typical_markers=[],
            parent_language="ber",
            iso_codes=["tzm"],
            writing_system="tifinagh",
            formality_levels=["oral", "literary"],
            cultural_context={"indigenous_status": "native", "revitalization": "active"}
        )
        
        self.dialect_variants["rif"] = DialectVariant(
            code="rif",
            name="Riff Berber (Tarifit)",
            family=DialectFamily.BERBER_AMAZIGH,
            region="North Africa",
            country_codes=["MA"],
            speakers_count=1500000,
            regional_variant=RegionalVariant.NORTHERN,
            linguistic_features={
                LinguisticFeature.PHONETIC: ["distinctive_consonants"],
                LinguisticFeature.LEXICAL: ["arabic_loanwords", "spanish_influence"],
                LinguisticFeature.GRAMMATICAL: ["complex_verb_system"]
            },
            typical_markers=[],
            parent_language="ber",
            iso_codes=["rif"],
            writing_system="tifinagh",
            formality_levels=["oral", "written"],
            cultural_context={"geographical_isolation": "mountain", "cultural_preservation": "strong"}
        )
        
        # English dialects
        self.dialect_variants["en-us"] = DialectVariant(
            code="en-us",
            name="American English",
            family=DialectFamily.ENGLISH,
            region="North America",
            country_codes=["US"],
            speakers_count=300000000,
            regional_variant=RegionalVariant.WESTERN,
            linguistic_features={
                LinguisticFeature.PHONETIC: ["rhotic_accent", "vowel_mergers"],
                LinguisticFeature.LEXICAL: ["american_vocabulary", "native_loanwords"],
                LinguisticFeature.GRAMMATICAL: ["past_participle_gotten"]
            },
            typical_markers=[],
            parent_language="en",
            iso_codes=["en-US"],
            writing_system="latin",
            formality_levels=["informal", "formal", "academic"],
            cultural_context={"global_influence": "dominant", "media_presence": "high"}
        )
        
        self.dialect_variants["en-gb"] = DialectVariant(
            code="en-gb",
            name="British English",
            family=DialectFamily.ENGLISH,
            region="Europe",
            country_codes=["GB"],
            speakers_count=65000000,
            regional_variant=RegionalVariant.CENTRAL,
            linguistic_features={
                LinguisticFeature.PHONETIC: ["non_rhotic", "received_pronunciation"],
                LinguisticFeature.LEXICAL: ["british_vocabulary", "formal_register"],
                LinguisticFeature.GRAMMATICAL: ["present_perfect_usage"]
            },
            typical_markers=[],
            parent_language="en",
            iso_codes=["en-GB"],
            writing_system="latin",
            formality_levels=["informal", "formal", "royal"],
            cultural_context={"historical_prestige": "high", "standard_reference": "traditional"}
        )
        
        # Spanish dialects
        self.dialect_variants["es-mx"] = DialectVariant(
            code="es-mx",
            name="Mexican Spanish",
            family=DialectFamily.SPANISH,
            region="North America",
            country_codes=["MX"],
            speakers_count=130000000,
            regional_variant=RegionalVariant.CENTRAL,
            linguistic_features={
                LinguisticFeature.PHONETIC: ["seseo", "distinctive_intonation"],
                LinguisticFeature.LEXICAL: ["nahuatl_loanwords", "mexicanisms"],
                LinguisticFeature.GRAMMATICAL: ["diminutive_usage"]
            },
            typical_markers=[],
            parent_language="es",
            iso_codes=["es-MX"],
            writing_system="latin",
            formality_levels=["informal", "formal", "ceremonial"],
            cultural_context={"indigenous_influence": "strong", "cultural_pride": "high"}
        )
        
        self.dialect_variants["es-ar"] = DialectVariant(
            code="es-ar",
            name="Argentinian Spanish",
            family=DialectFamily.SPANISH,
            region="South America",
            country_codes=["AR"],
            speakers_count=45000000,
            regional_variant=RegionalVariant.SOUTHERN,
            linguistic_features={
                LinguisticFeature.PHONETIC: ["yeismo_with_zh", "distinctive_intonation"],
                LinguisticFeature.LEXICAL: ["italian_influence", "lunfardo_slang"],
                LinguisticFeature.GRAMMATICAL: ["voseo_usage"]
            },
            typical_markers=[],
            parent_language="es",
            iso_codes=["es-AR"],
            writing_system="latin",
            formality_levels=["informal", "formal", "literary"],
            cultural_context={"european_influence": "strong", "tango_culture": "distinctive"}
        )
        
        logger.info(f"Initialized {len(self.dialect_variants)} dialect variants")
    
    def _initialize_dialect_markers(self):
        """Initialize dialect identification markers"""
        
        # Arabic dialect markers
        arabic_markers = {
            "ar-eg": [
                DialectMarker(
                    pattern=r"\b(عايز|عاوز)\b",
                    feature_type=LinguisticFeature.LEXICAL,
                    confidence_weight=0.8,
                    regions=["EG"],
                    examples=["عايز أروح", "عاوز أشوف"],
                    context="wanting/desiring"
                ),
                DialectMarker(
                    pattern=r"\b(إيه|أيه)\b",
                    feature_type=LinguisticFeature.LEXICAL,
                    confidence_weight=0.7,
                    regions=["EG"],
                    examples=["إيه ده؟", "أيه اللي حصل؟"],
                    context="what (interrogative)"
                )
            ],
            "ar-ma": [
                DialectMarker(
                    pattern=r"\b(بغيت|بغا)\b",
                    feature_type=LinguisticFeature.LEXICAL,
                    confidence_weight=0.8,
                    regions=["MA"],
                    examples=["بغيت نمشي", "بغا يجي"],
                    context="wanting (Moroccan)"
                ),
                DialectMarker(
                    pattern=r"\b(فين|وين)\b",
                    feature_type=LinguisticFeature.LEXICAL,
                    confidence_weight=0.7,
                    regions=["MA", "DZ", "TN"],
                    examples=["فين راك؟", "وين غادي؟"],
                    context="where (Maghrebi)"
                )
            ],
            "ar-sy": [
                DialectMarker(
                    pattern=r"\b(بدي|بده)\b",
                    feature_type=LinguisticFeature.LEXICAL,
                    confidence_weight=0.8,
                    regions=["SY", "LB", "JO", "PS"],
                    examples=["بدي أروح", "بده يجي"],
                    context="wanting (Levantine)"
                ),
                DialectMarker(
                    pattern=r"\b(شو|أيش)\b",
                    feature_type=LinguisticFeature.LEXICAL,
                    confidence_weight=0.7,
                    regions=["SY", "LB", "JO", "PS"],
                    examples=["شو هادا؟", "أيش بدك؟"],
                    context="what (Levantine)"
                )
            ]
        }
        
        # Berber/Amazigh markers
        berber_markers = {
            "tzm": [
                DialectMarker(
                    pattern=r"\b(|argaz)\b",
                    feature_type=LinguisticFeature.LEXICAL,
                    confidence_weight=0.9,
                    regions=["MA"],
                    examples=[" "],
                    context="man (Tamazight)"
                ),
                DialectMarker(
                    pattern=r"\b(|tamttut)\b",
                    feature_type=LinguisticFeature.LEXICAL,
                    confidence_weight=0.9,
                    regions=["MA"],
                    examples=[" "],
                    context="woman (Tamazight)"
                )
            ],
            "rif": [
                DialectMarker(
                    pattern=r"\b(aryaz|argaz)\b",
                    feature_type=LinguisticFeature.LEXICAL,
                    confidence_weight=0.8,
                    regions=["MA-north"],
                    examples=["aryaz amenzu"],
                    context="man (Tarifit)"
                )
            ]
        }
        
        # English dialect markers
        english_markers = {
            "en-us": [
                DialectMarker(
                    pattern=r"\b(gotten|fall|apartment|elevator|truck)\b",
                    feature_type=LinguisticFeature.LEXICAL,
                    confidence_weight=0.7,
                    regions=["US"],
                    examples=["I have gotten", "fall season", "apartment building"],
                    context="American vocabulary"
                ),
                DialectMarker(
                    pattern=r"\b(y'all|gonna|wanna)\b",
                    feature_type=LinguisticFeature.GRAMMATICAL,
                    confidence_weight=0.6,
                    regions=["US"],
                    examples=["y'all come", "gonna go", "wanna see"],
                    context="American informal contractions"
                )
            ],
            "en-gb": [
                DialectMarker(
                    pattern=r"\b(got|autumn|flat|lift|lorry|brilliant|lovely)\b",
                    feature_type=LinguisticFeature.LEXICAL,
                    confidence_weight=0.7,
                    regions=["GB"],
                    examples=["I have got", "autumn season", "flat rental"],
                    context="British vocabulary"
                ),
                DialectMarker(
                    pattern=r"\b(whilst|amongst|colour|honour)\b",
                    feature_type=LinguisticFeature.LEXICAL,
                    confidence_weight=0.8,
                    regions=["GB"],
                    examples=["whilst waiting", "amongst friends"],
                    context="British spelling and vocabulary"
                )
            ]
        }
        
        # Spanish dialect markers
        spanish_markers = {
            "es-mx": [
                DialectMarker(
                    pattern=r"\b(órale|ándale|güey|chido|padre)\b",
                    feature_type=LinguisticFeature.LEXICAL,
                    confidence_weight=0.8,
                    regions=["MX"],
                    examples=["órale pues", "ándale güey"],
                    context="Mexican slang"
                ),
                DialectMarker(
                    pattern=r"\b(ahorita|mero|nomás)\b",
                    feature_type=LinguisticFeature.LEXICAL,
                    confidence_weight=0.7,
                    regions=["MX"],
                    examples=["ahorita vengo", "mero aquí"],
                    context="Mexican temporal/spatial expressions"
                )
            ],
            "es-ar": [
                DialectMarker(
                    pattern=r"\b(vos|che|boludo|laburo|bondi)\b",
                    feature_type=LinguisticFeature.LEXICAL,
                    confidence_weight=0.8,
                    regions=["AR"],
                    examples=["vos sabés", "che boludo"],
                    context="Argentinian vocabulary"
                ),
                DialectMarker(
                    pattern=r"\b(tenés|querés|podés)\b",
                    feature_type=LinguisticFeature.GRAMMATICAL,
                    confidence_weight=0.9,
                    regions=["AR"],
                    examples=["vos tenés", "querés venir"],
                    context="Voseo conjugation"
                )
            ]
        }
        
        # Combine all markers
        self.dialect_markers.update(arabic_markers)
        self.dialect_markers.update(berber_markers)
        self.dialect_markers.update(english_markers)
        self.dialect_markers.update(spanish_markers)
        
        logger.info(f"Initialized dialect markers for {len(self.dialect_markers)} dialects")
    
    def _compile_linguistic_patterns(self):
        """Compile linguistic patterns for efficient matching"""



        try:
            # Compile regex patterns for all markers
            for dialect_code, markers in self.dialect_markers.items():
                patterns = []
                for marker in markers:
                    try:
                        compiled_pattern = re.compile(marker.pattern, re.IGNORECASE | re.UNICODE)
                        patterns.append((compiled_pattern, marker))
                    except re.error as e:
                        logger.warning(f"Invalid regex pattern for {dialect_code}: {marker.pattern} - {e}")
                
                self.linguistic_patterns[dialect_code] = patterns
            
            logger.info(f"Compiled linguistic patterns for {len(self.linguistic_patterns)} dialects")
            
        except Exception as e:
            logger.error(f"Error compiling linguistic patterns: {e}")
    
    async def detect_dialect(
        self,
        text: str,
        base_language: str = None,
        region_hint: str = None
    ) -> DialectDetection:
        """Detect dialect from text input"""



        try:
            # Check cache first
            cache_key = f"{text[:100]}_{base_language}_{region_hint}"
            if cache_key in self.detection_cache:
                return self.detection_cache[cache_key]
            
            # Initialize detection scores
            dialect_scores: Dict[str, float] = {}
            matching_markers: Dict[str, List[DialectMarker]] = {}
            detected_features: Set[LinguisticFeature] = set()
            
            # Filter dialects by base language if provided
            target_dialects = self.dialect_variants.keys()
            if base_language:
                target_dialects = [
                    code for code in target_dialects 
                    if self.dialect_variants[code].parent_language == base_language
                ]
            
            # Analyze text against each dialect
            for dialect_code in target_dialects:
                if dialect_code not in self.linguistic_patterns:
                    continue
                
                score = 0.0
                markers_found = []
                
                # Check linguistic patterns
                for pattern, marker in self.linguistic_patterns[dialect_code]:
                    matches = pattern.findall(text)
                    if matches:
                        # Calculate score based on frequency and confidence weight
                        match_count = len(matches)
                        marker_score = marker.confidence_weight * min(match_count / 10.0, 1.0)
                        score += marker_score
                        markers_found.append(marker)
                        detected_features.add(marker.feature_type)
                
                # Apply region bonus if hint matches
                if region_hint and region_hint.upper() in self.dialect_variants[dialect_code].country_codes:
                    score *= 1.2
                
                # Normalize score
                if markers_found:
                    dialect_scores[dialect_code] = score / len(self.dialect_markers.get(dialect_code, [1]))
                    matching_markers[dialect_code] = markers_found
            
            # Determine best match
            if not dialect_scores:
                # No specific dialect detected, return base language
                detected_dialect = base_language or "unknown"
                confidence = 0.0
                alternatives = []
                best_markers = []
            else:
                # Sort by score
                sorted_dialects = sorted(dialect_scores.items(), key=lambda x: x[1], reverse=True)
                detected_dialect = sorted_dialects[0][0]
                confidence = min(sorted_dialects[0][1], 1.0)
                alternatives = sorted_dialects[1:6]  # Top 5 alternatives
                best_markers = matching_markers.get(detected_dialect, [])
            
            # Generate processing recommendations
            recommendations = self._generate_processing_recommendations(
                detected_dialect, confidence, list(detected_features)
            )
            
            # Create detection result
            detection = DialectDetection(
                detected_dialect=detected_dialect,
                confidence_score=confidence,
                detected_features=list(detected_features),
                matching_markers=best_markers,
                regional_indicators=self._extract_regional_indicators(text, detected_dialect),
                alternative_dialects=alternatives,
                linguistic_analysis=self._perform_linguistic_analysis(text, detected_dialect),
                processing_recommendations=recommendations
            )
            
            # Cache result
            self.detection_cache[cache_key] = detection
            
            return detection
            
        except Exception as e:
            logger.error(f"Error detecting dialect: {e}")
            return DialectDetection(
                detected_dialect="unknown",
                confidence_score=0.0,
                detected_features=[],
                matching_markers=[],
                regional_indicators=[],
                alternative_dialects=[],
                linguistic_analysis={"error": str(e)},
                processing_recommendations=["error_in_detection"]
            )
    
    def _extract_regional_indicators(self, text: str, dialect: str) -> List[str]:
        """Extract regional indicators from text"""
        indicators = []
        
        if dialect in self.dialect_variants:
            variant = self.dialect_variants[dialect]
            
            # Check for country/region names
            for country in variant.country_codes:
                if country.lower() in text.lower():
                    indicators.append(f"country_reference_{country}")
            
            # Check for regional variant indicators
            if variant.regional_variant == RegionalVariant.MOUNTAIN:
                mountain_words = ["mountain", "hill", "peak", "جبل", ""]
                if any(word in text.lower() for word in mountain_words):
                    indicators.append("mountain_reference")
            
            if variant.regional_variant == RegionalVariant.COASTAL:
                coastal_words = ["sea", "coast", "beach", "بحر", "ساحل"]
                if any(word in text.lower() for word in coastal_words):
                    indicators.append("coastal_reference")
        
        return indicators
    
    def _perform_linguistic_analysis(self, text: str, dialect: str) -> Dict[str, Any]:
        """Perform linguistic analysis of the text"""
        analysis = {
            "text_length": len(text),
            "word_count": len(text.split()),
            "script_analysis": self._analyze_script(text),
            "formality_estimate": "medium",
            "complexity_score": 0.5
        }
        
        if dialect in self.dialect_variants:
            variant = self.dialect_variants[dialect]
            analysis["writing_system"] = variant.writing_system
            analysis["family"] = variant.family.value
            analysis["regional_variant"] = variant.regional_variant.value
        
        return analysis
    
    def _analyze_script(self, text: str) -> Dict[str, Any]:
        """Analyze the writing script used in text"""
        scripts = {
            "latin": 0,
            "arabic": 0,
            "tifinagh": 0,
            "other": 0
        }
        
        for char in text:
            if '\u0041' <= char <= '\u007A' or '\u00C0' <= char <= '\u024F':  # Latin
                scripts["latin"] += 1
            elif '\u0600' <= char <= '\u06FF' or '\u0750' <= char <= '\u077F':  # Arabic
                scripts["arabic"] += 1
            elif '\u2D30' <= char <= '\u2D7F':  # Tifinagh
                scripts["tifinagh"] += 1
            elif char.isalpha():
                scripts["other"] += 1
        
        total_chars = sum(scripts.values())
        if total_chars > 0:
            return {script: count/total_chars for script, count in scripts.items()}
        else:
            return scripts
    
    def _generate_processing_recommendations(
        self,
        dialect: str,
        confidence: float,
        features: List[LinguisticFeature]
    ) -> List[str]:
        """Generate processing recommendations based on detection"""
        recommendations = []
        
        if confidence < 0.3:
            recommendations.append("low_confidence_detection")
            recommendations.append("requires_human_verification")
        
        if confidence > 0.8:
            recommendations.append("high_confidence_detection")
            recommendations.append("suitable_for_automated_processing")
        
        if dialect in self.dialect_variants:
            variant = self.dialect_variants[dialect]
            
            if variant.writing_system == "tifinagh":
                recommendations.append("requires_tifinagh_support")
            
            if variant.writing_system == "arabic":
                recommendations.append("requires_rtl_support")
            
            if variant.family == DialectFamily.BERBER_AMAZIGH:
                recommendations.append("indigenous_language_sensitivity")
            
            if "informal" in variant.formality_levels:
                recommendations.append("informal_register_detected")
            
            if variant.regional_variant == RegionalVariant.MOUNTAIN:
                recommendations.append("mountain_dialect_consideration")
        
        if LinguisticFeature.GRAMMATICAL in features:
            recommendations.append("grammatical_patterns_detected")
        
        if LinguisticFeature.LEXICAL in features:
            recommendations.append("lexical_variants_identified")
        
        return recommendations
    
    async def get_dialect_info(self, dialect_code: str) -> Optional[DialectVariant]:
        """Get detailed information about a dialect"""



        return self.dialect_variants.get(dialect_code)
    
    async def list_supported_dialects(
        self,
        family: DialectFamily = None,
        region: str = None
    ) -> List[DialectVariant]:
        """List supported dialects with optional filtering"""
        dialects = list(self.dialect_variants.values())
        
        if family:
            dialects = [d for d in dialects if d.family == family]
        
        if region:
            dialects = [d for d in dialects if region.upper() in d.country_codes or region.lower() in d.region.lower()]
        
        return dialects
    
    async def process_multilingual_text(
        self,
        text: str,
        expected_languages: List[str] = None
    ) -> Dict[str, Any]:
        """Process text that may contain multiple dialects"""



        try:
            # Split text into segments (simple sentence-based splitting)
            sentences = re.split(r'[.!?]+', text)
            
            results = []
            overall_dialects = {}
            
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    detection = await self.detect_dialect(sentence.strip())
                    
                    results.append({
                        "segment": i,
                        "text": sentence.strip(),
                        "detection": detection
                    })
                    
                    # Track overall dialect frequencies
                    dialect = detection.detected_dialect
                    if dialect in overall_dialects:
                        overall_dialects[dialect] += detection.confidence_score
                    else:
                        overall_dialects[dialect] = detection.confidence_score
            
            # Determine primary dialect
            primary_dialect = max(overall_dialects, key=overall_dialects.get) if overall_dialects else "unknown"
            
            return {
                "primary_dialect": primary_dialect,
                "dialect_distribution": overall_dialects,
                "segment_analysis": results,
                "multilingual": len(set(r["detection"].detected_dialect for r in results)) > 1,
                "processing_complexity": "high" if len(overall_dialects) > 2 else "medium"
            }
            
        except Exception as e:
            logger.error(f"Error processing multilingual text: {e}")
            return {
                "error": str(e),
                "primary_dialect": "unknown",
                "processing_complexity": "error"
            }
    
    async def health_check(self) -> bool:
        """Health check for dialect processor"""



        try:
            # Check if dialect variants are loaded
            if not self.dialect_variants:
                return False
            
            # Test basic detection
            test_detection = await self.detect_dialect("Hello world", "en")
            
            return test_detection.detected_dialect is not None
            
        except Exception as e:
            logger.error(f"Dialect processor health check failed: {e}")
            return False