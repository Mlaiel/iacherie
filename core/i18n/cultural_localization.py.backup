"""Cultural Localization Engine - Ainflue Platform
================================================================================
Module: core/i18n/cultural_localization.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Localization Engine - Cultural Adaptation
Responsibility: Advanced cultural context adaptation and regional customization
Technologies: Python, Cultural AI, Anthropological Models, Regional Data
================================================================================

⚠️  PROPRIETARY SOFTWARE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Content analysis → Cultural context detection → Regional preferences → 
Hofstede dimensions → Communication style adaptation → Cultural compliance
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import json
import re

logger = logging.getLogger(__name__)


class CommunicationStyle(Enum):
    """Communication style preferences by culture"""
    DIRECT = "direct"
    INDIRECT = "indirect"
    HIGH_CONTEXT = "high_context"
    LOW_CONTEXT = "low_context"
    FORMAL = "formal"
    INFORMAL = "informal"
    HIERARCHICAL = "hierarchical"
    EGALITARIAN = "egalitarian"


class CulturalDimension(Enum):
    """Hofstede cultural dimensions"""
    POWER_DISTANCE = "power_distance"
    INDIVIDUALISM = "individualism"
    MASCULINITY = "masculinity"
    UNCERTAINTY_AVOIDANCE = "uncertainty_avoidance"
    LONG_TERM_ORIENTATION = "long_term_orientation"
    INDULGENCE = "indulgence"


class ColorCulturalMeaning(Enum):
    """Cultural color meanings"""
    LUCK = "luck"
    DEATH = "death"
    CELEBRATION = "celebration"
    MOURNING = "mourning"
    PROSPERITY = "prosperity"
    DANGER = "danger"
    PURITY = "purity"
    PASSION = "passion"


@dataclass
class CulturalContext:
    """Cultural context information"""
    region: str
    country_code: str
    language_code: str
    communication_style: CommunicationStyle
    hofstede_scores: Dict[CulturalDimension, float]
    color_meanings: Dict[str, List[ColorCulturalMeaning]]
    taboo_subjects: List[str]
    business_etiquette: Dict[str, str]
    greeting_customs: List[str]
    gift_customs: Dict[str, str]
    dining_etiquette: List[str]
    religious_considerations: List[str]
    gender_norms: Dict[str, str]
    age_respect_level: float  # 0-1 scale
    hierarchy_importance: float  # 0-1 scale
    time_orientation: str  # "monochronic" or "polychronic"
    personal_space_preference: float  # meters
    touch_tolerance: str  # "high", "medium", "low"
    eye_contact_norms: str
    silence_interpretation: str
    conflict_resolution_style: str


@dataclass
class CulturalAdaptation:
    """Cultural adaptation instructions"""
    content_modifications: Dict[str, str]
    style_adjustments: Dict[str, Any]
    color_replacements: Dict[str, str]
    image_suggestions: List[str]
    tone_adjustments: Dict[str, str]
    formality_level: str
    cultural_references: List[str]
    avoided_content: List[str]
    recommended_additions: List[str]
    compliance_notes: List[str]


class CulturalLocalization:
    """Advanced cultural localization and adaptation engine"""
    
    def __init__(self):
        self.cultural_contexts: Dict[str, CulturalContext] = {}
        self.adaptation_cache: Dict[str, CulturalAdaptation] = {}
        self.cultural_rules: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize cultural data
        self._initialize_cultural_contexts()
        self._initialize_adaptation_rules()
        
        logger.info("Cultural Localization Engine initialized")
    
    def _initialize_cultural_contexts(self):
        """Initialize cultural context data for major regions"""
        
        # Western cultures
        self.cultural_contexts["US"] = CulturalContext(
            region="North America",
            country_code="US",
            language_code="en",
            communication_style=CommunicationStyle.DIRECT,
            hofstede_scores={
                CulturalDimension.POWER_DISTANCE: 0.40,
                CulturalDimension.INDIVIDUALISM: 0.91,
                CulturalDimension.MASCULINITY: 0.62,
                CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.46,
                CulturalDimension.LONG_TERM_ORIENTATION: 0.26,
                CulturalDimension.INDULGENCE: 0.68
            },
            color_meanings={
                "red": [ColorCulturalMeaning.PASSION, ColorCulturalMeaning.DANGER],
                "white": [ColorCulturalMeaning.PURITY],
                "black": [ColorCulturalMeaning.MOURNING],
                "green": [ColorCulturalMeaning.PROSPERITY]
            },
            taboo_subjects=["personal income", "weight", "age"],
            business_etiquette={
                "punctuality": "extremely_important",
                "dress_code": "business_professional",
                "meeting_style": "agenda_driven"
            },
            greeting_customs=["handshake", "eye_contact", "smile"],
            gift_customs={
                "business": "avoid_expensive_gifts",
                "personal": "thoughtful_gestures"
            },
            dining_etiquette=["wait_for_host", "use_utensils", "finish_plate"],
            religious_considerations=["secular_approach", "respect_diversity"],
            gender_norms={"workplace": "equality_expected", "social": "informal"},
            age_respect_level=0.6,
            hierarchy_importance=0.4,
            time_orientation="monochronic",
            personal_space_preference=1.2,
            touch_tolerance="low",
            eye_contact_norms="direct_and_confident",
            silence_interpretation="awkward",
            conflict_resolution_style="direct_discussion"
        )
        
        # East Asian cultures
        self.cultural_contexts["JP"] = CulturalContext(
            region="East Asia",
            country_code="JP",
            language_code="ja",
            communication_style=CommunicationStyle.INDIRECT,
            hofstede_scores={
                CulturalDimension.POWER_DISTANCE: 0.54,
                CulturalDimension.INDIVIDUALISM: 0.46,
                CulturalDimension.MASCULINITY: 0.95,
                CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.92,
                CulturalDimension.LONG_TERM_ORIENTATION: 0.88,
                CulturalDimension.INDULGENCE: 0.42
            },
            color_meanings={
                "red": [ColorCulturalMeaning.LUCK, ColorCulturalMeaning.CELEBRATION],
                "white": [ColorCulturalMeaning.DEATH, ColorCulturalMeaning.MOURNING],
                "black": [ColorCulturalMeaning.MOURNING],
                "gold": [ColorCulturalMeaning.PROSPERITY]
            },
            taboo_subjects=["personal failure", "direct_criticism", "number_4"],
            business_etiquette={
                "punctuality": "absolutely_critical",
                "dress_code": "conservative_formal",
                "meeting_style": "hierarchical_respect"
            },
            greeting_customs=["bow", "business_card_ceremony", "formal_address"],
            gift_customs={
                "business": "modest_quality_gifts",
                "wrapping": "presentation_critical"
            },
            dining_etiquette=["wait_for_elder", "chopstick_etiquette", "no_waste"],
            religious_considerations=["shinto_buddhist_respect", "spiritual_harmony"],
            gender_norms={"workplace": "traditional_roles", "respect": "high"},
            age_respect_level=0.95,
            hierarchy_importance=0.9,
            time_orientation="monochronic",
            personal_space_preference=0.8,
            touch_tolerance="very_low",
            eye_contact_norms="respectful_brief",
            silence_interpretation="respectful_contemplation",
            conflict_resolution_style="indirect_harmony"
        )
        
        # Arabic cultures
        self.cultural_contexts["AE"] = CulturalContext(
            region="Middle East",
            country_code="AE",
            language_code="ar",
            communication_style=CommunicationStyle.HIGH_CONTEXT,
            hofstede_scores={
                CulturalDimension.POWER_DISTANCE: 0.90,
                CulturalDimension.INDIVIDUALISM: 0.25,
                CulturalDimension.MASCULINITY: 0.50,
                CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.80,
                CulturalDimension.LONG_TERM_ORIENTATION: 0.12,
                CulturalDimension.INDULGENCE: 0.34
            },
            color_meanings={
                "green": [ColorCulturalMeaning.LUCK, ColorCulturalMeaning.PROSPERITY],
                "white": [ColorCulturalMeaning.PURITY],
                "black": [ColorCulturalMeaning.MOURNING],
                "gold": [ColorCulturalMeaning.PROSPERITY]
            },
            taboo_subjects=["alcohol", "pork", "inappropriate_dress", "criticism_of_religion"],
            business_etiquette={
                "punctuality": "flexible_time",
                "dress_code": "modest_conservative",
                "meeting_style": "relationship_first"
            },
            greeting_customs=["salaam", "right_hand_only", "respect_for_elders"],
            gift_customs={
                "business": "avoid_leather_alcohol",
                "presentation": "right_hand_only"
            },
            dining_etiquette=["halal_only", "right_hand_eating", "hospitality_acceptance"],
            religious_considerations=["islamic_principles", "prayer_times", "ramadan_respect"],
            gender_norms={"interaction": "respectful_boundaries", "dress": "modesty"},
            age_respect_level=0.95,
            hierarchy_importance=0.85,
            time_orientation="polychronic",
            personal_space_preference=0.6,
            touch_tolerance="gender_dependent",
            eye_contact_norms="respectful_brief",
            silence_interpretation="respect_contemplation",
            conflict_resolution_style="mediation_honor"
        )
        
        # European cultures
        self.cultural_contexts["DE"] = CulturalContext(
            region="Western Europe",
            country_code="DE",
            language_code="de",
            communication_style=CommunicationStyle.DIRECT,
            hofstede_scores={
                CulturalDimension.POWER_DISTANCE: 0.35,
                CulturalDimension.INDIVIDUALISM: 0.67,
                CulturalDimension.MASCULINITY: 0.66,
                CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.65,
                CulturalDimension.LONG_TERM_ORIENTATION: 0.83,
                CulturalDimension.INDULGENCE: 0.40
            },
            color_meanings={
                "red": [ColorCulturalMeaning.PASSION],
                "white": [ColorCulturalMeaning.PURITY],
                "black": [ColorCulturalMeaning.MOURNING],
                "green": [ColorCulturalMeaning.PROSPERITY]
            },
            taboo_subjects=["nazi_period", "personal_income", "private_life"],
            business_etiquette={
                "punctuality": "absolutely_essential",
                "dress_code": "conservative_professional",
                "meeting_style": "structured_efficient"
            },
            greeting_customs=["firm_handshake", "direct_eye_contact", "formal_address"],
            gift_customs={
                "business": "quality_over_quantity",
                "occasions": "appropriate_timing"
            },
            dining_etiquette=["wait_for_host", "proper_utensils", "finish_meal"],
            religious_considerations=["secular_respect", "christian_heritage"],
            gender_norms={"workplace": "equality_strong", "respect": "mutual"},
            age_respect_level=0.7,
            hierarchy_importance=0.6,
            time_orientation="monochronic",
            personal_space_preference=1.0,
            touch_tolerance="low",
            eye_contact_norms="direct_professional",
            silence_interpretation="thinking_time",
            conflict_resolution_style="direct_logical"
        )
        
        # African cultures (Morocco example)
        self.cultural_contexts["MA"] = CulturalContext(
            region="North Africa",
            country_code="MA",
            language_code="ar",
            communication_style=CommunicationStyle.HIGH_CONTEXT,
            hofstede_scores={
                CulturalDimension.POWER_DISTANCE: 0.70,
                CulturalDimension.INDIVIDUALISM: 0.46,
                CulturalDimension.MASCULINITY: 0.53,
                CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.68,
                CulturalDimension.LONG_TERM_ORIENTATION: 0.14,
                CulturalDimension.INDULGENCE: 0.25
            },
            color_meanings={
                "green": [ColorCulturalMeaning.LUCK, ColorCulturalMeaning.PROSPERITY],
                "red": [ColorCulturalMeaning.CELEBRATION],
                "white": [ColorCulturalMeaning.PURITY],
                "blue": [ColorCulturalMeaning.PROSPERITY]
            },
            taboo_subjects=["politics", "religion_criticism", "alcohol", "inappropriate_dress"],
            business_etiquette={
                "punctuality": "relationship_over_time",
                "dress_code": "modest_professional",
                "meeting_style": "relationship_building"
            },
            greeting_customs=["salaam", "inquire_about_family", "tea_hospitality"],
            gift_customs={
                "business": "thoughtful_modest",
                "hospitality": "always_appreciated"
            },
            dining_etiquette=["right_hand_only", "share_meals", "accept_hospitality"],
            religious_considerations=["islamic_respect", "prayer_consideration", "halal_food"],
            gender_norms={"interaction": "respectful_boundaries", "family": "important"},
            age_respect_level=0.9,
            hierarchy_importance=0.8,
            time_orientation="polychronic",
            personal_space_preference=0.7,
            touch_tolerance="same_gender_acceptable",
            eye_contact_norms="respectful_moderate",
            silence_interpretation="contemplation_respect",
            conflict_resolution_style="family_community_mediation"
        )
        
        logger.info(f"Initialized {len(self.cultural_contexts)} cultural contexts")
    
    def _initialize_adaptation_rules(self):
        """Initialize cultural adaptation rules"""
        
        # Communication style adaptations
        self.cultural_rules["communication"] = [
            {
                "condition": {"communication_style": "indirect"},
                "adaptations": {
                    "tone": "softer",
                    "directness": "reduced",
                    "implications": "increased",
                    "context": "expanded"
                }
            },
            {
                "condition": {"communication_style": "formal"},
                "adaptations": {
                    "formality": "increased",
                    "titles": "required",
                    "courtesy": "enhanced",
                    "respect_markers": "added"
                }
            }
        ]
        
        # Color adaptations
        self.cultural_rules["colors"] = [
            {
                "condition": {"color": "white", "meaning": "death"},
                "adaptations": {
                    "replacement_color": "blue",
                    "warning": "white_associated_with_death",
                    "alternative_colors": ["blue", "green", "gold"]
                }
            },
            {
                "condition": {"color": "red", "context": "business", "region": "asia"},
                "adaptations": {
                    "enhancement": "luck_prosperity",
                    "usage": "encouraged",
                    "meaning": "positive"
                }
            }
        ]
        
        # Business etiquette adaptations
        self.cultural_rules["business"] = [
            {
                "condition": {"hierarchy_importance": ">0.8"},
                "adaptations": {
                    "titles": "mandatory",
                    "respect_language": "enhanced",
                    "decision_making": "top_down",
                    "communication_flow": "hierarchical"
                }
            }
        ]
        
        logger.info("Cultural adaptation rules initialized")
    
    async def get_cultural_context(self, country_code: str, language_code: str = None) -> Optional[CulturalContext]:
        """Get cultural context for a country/region"""
        try:
            # Direct lookup
            context = self.cultural_contexts.get(country_code.upper())
            
            if not context and language_code:
                # Fallback to language-based lookup
                for ctx in self.cultural_contexts.values():
                    if ctx.language_code == language_code:
                        context = ctx
                        break
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting cultural context for {country_code}: {e}")
            return None
    
    async def analyze_cultural_content(
        self,
        content: str,
        source_culture: str,
        target_culture: str,
        content_type: str = "text"
    ) -> Dict[str, Any]:
        """Analyze content for cultural appropriateness"""
        try:
            source_ctx = await self.get_cultural_context(source_culture)
            target_ctx = await self.get_cultural_context(target_culture)
            
            if not source_ctx or not target_ctx:
                return {"error": "Cultural context not available"}
            
            analysis = {
                "cultural_conflicts": [],
                "sensitive_content": [],
                "recommended_changes": [],
                "color_issues": [],
                "communication_style_mismatch": False,
                "taboo_violations": [],
                "adaptation_required": False
            }
            
            # Check for taboo subjects
            content_lower = content.lower()
            for taboo in target_ctx.taboo_subjects:
                if taboo.lower() in content_lower:
                    analysis["taboo_violations"].append({
                        "subject": taboo,
                        "severity": "high",
                        "recommendation": "remove_or_rephrase"
                    })
                    analysis["adaptation_required"] = True
            
            # Check communication style compatibility
            if source_ctx.communication_style != target_ctx.communication_style:
                analysis["communication_style_mismatch"] = True
                analysis["recommended_changes"].append({
                    "type": "communication_style",
                    "from": source_ctx.communication_style.value,
                    "to": target_ctx.communication_style.value,
                    "priority": "medium"
                })
                analysis["adaptation_required"] = True
            
            # Check for color references (basic implementation)
            colors = ["red", "white", "black", "green", "blue", "yellow", "purple"]
            for color in colors:
                if color in content_lower:
                    source_meaning = source_ctx.color_meanings.get(color, [])
                    target_meaning = target_ctx.color_meanings.get(color, [])
                    
                    if source_meaning != target_meaning:
                        analysis["color_issues"].append({
                            "color": color,
                            "source_meaning": [m.value for m in source_meaning],
                            "target_meaning": [m.value for m in target_meaning],
                            "requires_adaptation": True
                        })
                        analysis["adaptation_required"] = True
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing cultural content: {e}")
            return {"error": str(e)}
    
    async def create_cultural_adaptation(
        self,
        content: str,
        analysis: Dict[str, Any],
        target_culture: str,
        content_type: str = "text"
    ) -> CulturalAdaptation:
        """Create cultural adaptation based on analysis"""
        try:
            target_ctx = await self.get_cultural_context(target_culture)
            
            adaptation = CulturalAdaptation(
                content_modifications={},
                style_adjustments={},
                color_replacements={},
                image_suggestions=[],
                tone_adjustments={},
                formality_level="medium",
                cultural_references=[],
                avoided_content=[],
                recommended_additions=[],
                compliance_notes=[]
            )
            
            # Handle taboo violations
            for violation in analysis.get("taboo_violations", []):
                adaptation.avoided_content.append(violation["subject"])
                adaptation.compliance_notes.append(
                    f"Remove references to {violation['subject']} - culturally inappropriate"
                )
            
            # Handle communication style
            if analysis.get("communication_style_mismatch"):
                if target_ctx.communication_style == CommunicationStyle.INDIRECT:
                    adaptation.tone_adjustments["directness"] = "reduced"
                    adaptation.tone_adjustments["implication"] = "increased"
                    adaptation.style_adjustments["approach"] = "subtle"
                elif target_ctx.communication_style == CommunicationStyle.FORMAL:
                    adaptation.formality_level = "high"
                    adaptation.tone_adjustments["courtesy"] = "enhanced"
                    adaptation.style_adjustments["titles"] = "required"
            
            # Handle color issues
            for color_issue in analysis.get("color_issues", []):
                if color_issue["requires_adaptation"]:
                    # Simple color replacement logic
                    problematic_color = color_issue["color"]
                    safe_colors = ["blue", "green"]  # Generally safe colors
                    adaptation.color_replacements[problematic_color] = safe_colors[0]
            
            # Add cultural context considerations
            if target_ctx.hierarchy_importance > 0.7:
                adaptation.recommended_additions.append("respect_hierarchical_structure")
            
            if target_ctx.age_respect_level > 0.8:
                adaptation.recommended_additions.append("emphasize_respect_for_elders")
            
            # Business context adaptations
            if "business" in content.lower():
                business_etiquette = target_ctx.business_etiquette
                if business_etiquette.get("punctuality") == "absolutely_critical":
                    adaptation.recommended_additions.append("emphasize_punctuality_importance")
                if business_etiquette.get("dress_code") == "conservative_formal":
                    adaptation.recommended_additions.append("mention_formal_dress_expectations")
            
            return adaptation
            
        except Exception as e:
            logger.error(f"Error creating cultural adaptation: {e}")
            return CulturalAdaptation(
                content_modifications={},
                style_adjustments={},
                color_replacements={},
                image_suggestions=[],
                tone_adjustments={},
                formality_level="medium",
                cultural_references=[],
                avoided_content=[],
                recommended_additions=[],
                compliance_notes=[f"Error in adaptation: {str(e)}"]
            )
    
    async def adapt_content_culturally(
        self,
        content: str,
        source_culture: str,
        target_culture: str,
        content_type: str = "text"
    ) -> Dict[str, Any]:
        """Complete cultural adaptation pipeline"""
        try:
            # Analyze content
            analysis = await self.analyze_cultural_content(
                content, source_culture, target_culture, content_type
            )
            
            # Create adaptation
            adaptation = await self.create_cultural_adaptation(
                content, analysis, target_culture, content_type
            )
            
            # Apply adaptations (basic implementation)
            adapted_content = content
            
            # Apply color replacements
            for old_color, new_color in adaptation.color_replacements.items():
                adapted_content = adapted_content.replace(old_color, new_color)
            
            # Remove avoided content (basic implementation)
            for avoided in adaptation.avoided_content:
                # Simple removal - in production, this would be more sophisticated
                adapted_content = adapted_content.replace(avoided, "[content_adapted]")
            
            result = {
                "original_content": content,
                "adapted_content": adapted_content,
                "analysis": analysis,
                "adaptation": adaptation,
                "cultural_confidence": self._calculate_adaptation_confidence(analysis, adaptation),
                "requires_human_review": analysis.get("adaptation_required", False)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in cultural adaptation pipeline: {e}")
            return {
                "error": str(e),
                "original_content": content,
                "adapted_content": content,
                "requires_human_review": True
            }
    
    def _calculate_adaptation_confidence(
        self,
        analysis: Dict[str, Any],
        adaptation: CulturalAdaptation
    ) -> float:
        """Calculate confidence score for cultural adaptation"""
        try:
            confidence = 1.0
            
            # Reduce confidence based on issues found
            if analysis.get("taboo_violations"):
                confidence -= 0.3
            
            if analysis.get("communication_style_mismatch"):
                confidence -= 0.2
            
            if analysis.get("color_issues"):
                confidence -= 0.1
            
            # Increase confidence if adaptations were applied
            if adaptation.content_modifications:
                confidence += 0.1
            
            if adaptation.tone_adjustments:
                confidence += 0.1
            
            return max(0.0, min(1.0, confidence))
            
        except Exception:
            return 0.5  # Default moderate confidence
    
    async def get_cultural_recommendations(self, target_culture: str) -> Dict[str, Any]:
        """Get cultural recommendations for content creation"""
        try:
            context = await self.get_cultural_context(target_culture)
            
            if not context:
                return {"error": "Cultural context not available"}
            
            recommendations = {
                "communication_style": {
                    "preferred": context.communication_style.value,
                    "description": self._get_communication_style_description(context.communication_style)
                },
                "formality_level": self._determine_formality_level(context),
                "cultural_colors": {
                    "recommended": self._get_recommended_colors(context),
                    "avoid": self._get_colors_to_avoid(context)
                },
                "business_etiquette": context.business_etiquette,
                "taboo_subjects": context.taboo_subjects,
                "greeting_customs": context.greeting_customs,
                "cultural_values": {
                    "hierarchy_importance": context.hierarchy_importance,
                    "age_respect": context.age_respect_level,
                    "time_orientation": context.time_orientation
                },
                "hofstede_profile": {
                    dim.value: score for dim, score in context.hofstede_scores.items()
                }
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting cultural recommendations: {e}")
            return {"error": str(e)}
    
    def _get_communication_style_description(self, style: CommunicationStyle) -> str:
        """Get description for communication style"""
        descriptions = {
            CommunicationStyle.DIRECT: "Clear, straightforward communication preferred",
            CommunicationStyle.INDIRECT: "Subtle, context-dependent communication",
            CommunicationStyle.HIGH_CONTEXT: "Meaning derived from context and relationships",
            CommunicationStyle.LOW_CONTEXT: "Explicit, detailed information required",
            CommunicationStyle.FORMAL: "Structured, respectful, title-based communication",
            CommunicationStyle.INFORMAL: "Casual, friendly, first-name basis",
            CommunicationStyle.HIERARCHICAL: "Respect for authority and seniority",
            CommunicationStyle.EGALITARIAN: "Equal treatment regardless of status"
        }
        return descriptions.get(style, "Standard communication")
    
    def _determine_formality_level(self, context: CulturalContext) -> str:
        """Determine appropriate formality level"""
        if context.hierarchy_importance > 0.8:
            return "very_high"
        elif context.hierarchy_importance > 0.6:
            return "high"
        elif context.hierarchy_importance > 0.4:
            return "medium"
        else:
            return "low"
    
    def _get_recommended_colors(self, context: CulturalContext) -> List[str]:
        """Get culturally appropriate colors"""
        recommended = []
        for color, meanings in context.color_meanings.items():
            if any(m in [ColorCulturalMeaning.LUCK, ColorCulturalMeaning.PROSPERITY, 
                        ColorCulturalMeaning.CELEBRATION] for m in meanings):
                recommended.append(color)
        return recommended
    
    def _get_colors_to_avoid(self, context: CulturalContext) -> List[str]:
        """Get colors to avoid culturally"""
        avoid = []
        for color, meanings in context.color_meanings.items():
            if any(m in [ColorCulturalMeaning.DEATH, ColorCulturalMeaning.MOURNING, 
                        ColorCulturalMeaning.DANGER] for m in meanings):
                avoid.append(color)
        return avoid
    
    async def health_check(self) -> bool:
        """Health check for cultural localization service"""
        try:
            # Check if cultural contexts are loaded
            if not self.cultural_contexts:
                return False
            
            # Test a simple cultural analysis
            test_analysis = await self.analyze_cultural_content(
                "test content", "US", "JP", "text"
            )
            
            return "error" not in test_analysis
            
        except Exception as e:
            logger.error(f"Cultural localization health check failed: {e}")
            return False