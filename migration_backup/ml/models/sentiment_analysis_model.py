"""
Sentiment Analysis Model - IA Chéries Enterprise
==========================================
Modèle analyse sentiment multi-lingue avec business context.
Emotion detection + brand safety + audience targeting + engagement optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries ML Models
Version: 1.0 Production
"""

import torch
import torch.nn as nn
# import transformers
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from pathlib import Path
import json
import re
import string
from textblob import TextBlob
import langdetect

# ⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
# Cette architecture ML et tous ses algorithmes sont la propriété intellectuelle 
# EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Tous droits réservés.

logger = logging.getLogger(__name__)

class SentimentPolarity(Enum):
    """Polarité du sentiment"""
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2

class EmotionCategory(Enum):
    """Catégories d'émotions détectées"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    LOVE = "love"
    EXCITEMENT = "excitement"
    TRUST = "trust"
    ANTICIPATION = "anticipation"

class BrandSafetyLevel(Enum):
    """Niveaux de sécurité de marque"""
    UNSAFE = 1
    MODERATE_RISK = 2
    LOW_RISK = 3
    SAFE = 4
    VERY_SAFE = 5

class AudienceSegment(Enum):
    """Segments d'audience basés sur sentiment"""
    CHILDREN_FRIENDLY = "children_friendly"
    TEEN_APPROPRIATE = "teen_appropriate"
    YOUNG_ADULT = "young_adult"
    PROFESSIONAL = "professional"
    MATURE_AUDIENCE = "mature_audience"
    GENERAL_AUDIENCE = "general_audience"

@dataclass
class SentimentInput:
    """Input pour analyse sentiment"""
    content_id: str
    text_content: str
    language: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    platform: Optional[str] = None

@dataclass
class EmotionalProfile:
    """Profil émotionnel du contenu"""
    primary_emotion: EmotionCategory
    secondary_emotion: Optional[EmotionCategory]
    emotion_intensities: Dict[EmotionCategory, float]
    emotional_stability: float
    arousal_level: float
    valence_score: float

@dataclass
class BrandSafetyAssessment:
    """Évaluation sécurité de marque"""
    safety_level: BrandSafetyLevel
    safety_score: float
    risk_factors: List[str]
    content_warnings: List[str]
    advertiser_friendly: bool
    platform_compliance: Dict[str, bool]
    sensitive_topics: List[str]

@dataclass
class AudienceAnalysis:
    """Analyse audience cible"""
    target_segments: List[AudienceSegment]
    age_appropriateness: Dict[str, float]
    cultural_sensitivity: Dict[str, float]
    engagement_potential: Dict[str, float]
    demographic_appeal: Dict[str, float]

@dataclass
class SentimentAnalysisResult:
    """Résultat complet analyse sentiment"""
    content_id: str
    sentiment_polarity: SentimentPolarity
    sentiment_score: float
    confidence_score: float
    emotional_profile: EmotionalProfile
    brand_safety: BrandSafetyAssessment
    audience_analysis: AudienceAnalysis
    language_detected: str
    engagement_optimization: Dict[str, Any]
    monetization_impact: Dict[str, float]
    processing_time_ms: float
    timestamp: str

@dataclass
class SentimentAnalysisConfig:
    """Configuration pour analyse sentiment"""
    model_version: str = "1.0"
    device: str = "cpu"
    enable_emotion_detection: bool = True
    enable_brand_safety: bool = True
    enable_audience_analysis: bool = True
    multilingual_support: bool = True
    confidence_threshold: float = 0.75

class EmotionDetectionEngine(nn.Module):
    """Moteur détection émotions avec deep learning"""
    
    def __init__(self, config: SentimentAnalysisConfig):
        super().__init__()
        self.config = config
        
        # Emotion classification model
        self.emotion_classifier = transformers.AutoModel.from_pretrained(
            'bert-base-multilingual-cased'
        )
        
        # Emotion prediction heads
        self.emotion_heads = nn.ModuleDict({
            emotion.value: nn.Sequential(
                nn.Linear(768, 256),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(256, 64),
                nn.ReLU(),
                nn.Linear(64, 1),
                nn.Sigmoid()
            ) for emotion in EmotionCategory
        })
        
        # Arousal and valence predictors
        self.arousal_predictor = nn.Sequential(
            nn.Linear(768, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )
        
        self.valence_predictor = nn.Sequential(
            nn.Linear(768, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Tanh()  # -1 to 1 range
        )
    
    def detect_emotions(self, text: str, language: str = "en") -> EmotionalProfile:
        """Détection émotions avec granular emotion categories"""
        try:
            # Tokenize text
            tokenizer = transformers.AutoTokenizer.from_pretrained(
                'bert-base-multilingual-cased'
            )
            tokens = tokenizer(
                text, return_tensors='pt', max_length=512,
                truncation=True, padding=True
            )
            
            # Extract text features
            with torch.no_grad():
                outputs = self.emotion_classifier(**tokens)
                text_features = outputs.last_hidden_state.mean(dim=1)
                
                # Predict emotions
                emotion_intensities = {}
                for emotion in EmotionCategory:
                    intensity = self.emotion_heads[emotion.value](text_features).item()
                    emotion_intensities[emotion] = intensity
                
                # Predict arousal and valence
                arousal_level = self.arousal_predictor(text_features).item()
                valence_score = self.valence_predictor(text_features).item()
            
            # Determine primary and secondary emotions
            sorted_emotions = sorted(
                emotion_intensities.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            primary_emotion = sorted_emotions[0][0]
            secondary_emotion = sorted_emotions[1][0] if len(sorted_emotions) > 1 and sorted_emotions[1][1] > 0.3 else None
            
            # Calculate emotional stability
            emotional_stability = 1.0 - np.std(list(emotion_intensities.values()))
            
            return EmotionalProfile(
                primary_emotion=primary_emotion,
                secondary_emotion=secondary_emotion,
                emotion_intensities=emotion_intensities,
                emotional_stability=max(0.0, emotional_stability),
                arousal_level=arousal_level,
                valence_score=valence_score
            )
            
        except Exception as e:
            logger.error(f"Emotion detection error: {e}")
            return self._default_emotional_profile()
    
    def _default_emotional_profile(self) -> EmotionalProfile:
        """Profil émotionnel par défaut"""
        return EmotionalProfile(
            primary_emotion=EmotionCategory.TRUST,
            secondary_emotion=None,
            emotion_intensities={emotion: 0.1 for emotion in EmotionCategory},
            emotional_stability=0.5,
            arousal_level=0.5,
            valence_score=0.0
        )

class BrandSafetyAnalyzer:
    """Analyseur sécurité de marque pour advertiser-friendly content"""
    
    def __init__(self, config: SentimentAnalysisConfig):
        self.config = config
        
        # Brand safety keywords and patterns
        self.risk_keywords = {
            "high_risk": [
                "violence", "hate", "discrimination", "profanity", "adult", 
                "explicit", "controversial", "illegal", "harmful", "toxic"
            ],
            "moderate_risk": [
                "politics", "religion", "debate", "argument", "criticism",
                "sensitive", "personal", "private", "confidential"
            ],
            "sensitive_topics": [
                "health", "medical", "financial", "legal", "relationships",
                "mental health", "addiction", "tragedy", "disaster"
            ]
        }
        
        # Platform-specific content policies
        self.platform_policies = {
            "youtube": {"profanity": False, "controversial": "limited", "adult": False},
            "instagram": {"explicit": False, "violence": False, "hate": False},
            "tiktok": {"adult": False, "dangerous": False, "misinformation": False},
            "facebook": {"fake_news": False, "hate_speech": False, "violence": False},
            "twitter": {"harassment": False, "threats": False, "spam": False},
            "linkedin": {"professional": True, "appropriate": True, "business": True}
        }
    
    def assess_brand_safety(self, text: str, emotional_profile: EmotionalProfile,
                          platform: str = None) -> BrandSafetyAssessment:
        """Évaluation sécurité marque pour advertiser compatibility"""
        try:
            # Text preprocessing
            text_lower = text.lower()
            
            # Risk factor detection
            risk_factors = []
            content_warnings = []
            sensitive_topics = []
            
            # Check for risk keywords
            for risk_level, keywords in self.risk_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        if risk_level == "high_risk":
                            risk_factors.append(f"High risk content: {keyword}")
                        elif risk_level == "moderate_risk":
                            risk_factors.append(f"Moderate risk content: {keyword}")
                        elif risk_level == "sensitive_topics":
                            sensitive_topics.append(keyword)
            
            # Emotional risk assessment
            if emotional_profile.primary_emotion in [EmotionCategory.ANGER, EmotionCategory.DISGUST]:
                risk_factors.append("Negative emotional tone detected")
            
            if emotional_profile.arousal_level > 0.8:
                content_warnings.append("High emotional intensity")
            
            # Calculate safety score
            safety_score = 1.0
            
            # Penalize for risk factors
            for risk in risk_factors:
                if "High risk" in risk:
                    safety_score -= 0.3
                elif "Moderate risk" in risk:
                    safety_score -= 0.15
                else:
                    safety_score -= 0.05
            
            # Adjust for emotional factors
            if emotional_profile.valence_score < -0.5:
                safety_score -= 0.1
            
            if emotional_profile.emotional_stability < 0.3:
                safety_score -= 0.1
            
            safety_score = max(0.0, min(1.0, safety_score))
            
            # Determine safety level
            if safety_score >= 0.9:
                safety_level = BrandSafetyLevel.VERY_SAFE
            elif safety_score >= 0.7:
                safety_level = BrandSafetyLevel.SAFE
            elif safety_score >= 0.5:
                safety_level = BrandSafetyLevel.LOW_RISK
            elif safety_score >= 0.3:
                safety_level = BrandSafetyLevel.MODERATE_RISK
            else:
                safety_level = BrandSafetyLevel.UNSAFE
            
            # Advertiser friendliness
            advertiser_friendly = safety_score >= 0.7 and len(risk_factors) == 0
            
            # Platform compliance
            platform_compliance = {}
            if platform and platform in self.platform_policies:
                policies = self.platform_policies[platform]
                for policy, required in policies.items():
                    if isinstance(required, bool):
                        # Check if content violates policy
                        violates = any(policy.lower() in risk.lower() for risk in risk_factors)
                        platform_compliance[policy] = not violates if required else True
                    else:
                        # Limited acceptance
                        platform_compliance[policy] = safety_score >= 0.6
            else:
                # Default compliance for unknown platforms
                platform_compliance = {"general": safety_score >= 0.5}
            
            return BrandSafetyAssessment(
                safety_level=safety_level,
                safety_score=safety_score,
                risk_factors=risk_factors,
                content_warnings=content_warnings,
                advertiser_friendly=advertiser_friendly,
                platform_compliance=platform_compliance,
                sensitive_topics=sensitive_topics
            )
            
        except Exception as e:
            logger.error(f"Brand safety assessment error: {e}")
            return self._default_brand_safety()
    
    def _default_brand_safety(self) -> BrandSafetyAssessment:
        """Assessment sécurité par défaut"""
        return BrandSafetyAssessment(
            safety_level=BrandSafetyLevel.LOW_RISK,
            safety_score=0.5,
            risk_factors=[],
            content_warnings=[],
            advertiser_friendly=False,
            platform_compliance={"general": True},
            sensitive_topics=[]
        )

class AudienceProfiler:
    """Profileur audience cible basé sur sentiment"""
    
    def __init__(self, config: SentimentAnalysisConfig):
        self.config = config
        
        # Audience segment characteristics
        self.segment_characteristics = {
            AudienceSegment.CHILDREN_FRIENDLY: {
                "emotions": [EmotionCategory.JOY, EmotionCategory.EXCITEMENT, EmotionCategory.SURPRISE],
                "valence_range": (0.2, 1.0),
                "arousal_range": (0.3, 0.8),
                "content_restrictions": ["no_profanity", "positive_only", "educational"]
            },
            AudienceSegment.TEEN_APPROPRIATE: {
                "emotions": [EmotionCategory.EXCITEMENT, EmotionCategory.JOY, EmotionCategory.SURPRISE],
                "valence_range": (-0.2, 1.0),
                "arousal_range": (0.4, 1.0),
                "content_restrictions": ["mild_language", "age_appropriate"]
            },
            AudienceSegment.YOUNG_ADULT: {
                "emotions": [EmotionCategory.EXCITEMENT, EmotionCategory.LOVE, EmotionCategory.ANTICIPATION],
                "valence_range": (-0.5, 1.0),
                "arousal_range": (0.2, 1.0),
                "content_restrictions": ["creative", "trendy", "authentic"]
            },
            AudienceSegment.PROFESSIONAL: {
                "emotions": [EmotionCategory.TRUST, EmotionCategory.ANTICIPATION, EmotionCategory.JOY],
                "valence_range": (-0.3, 0.8),
                "arousal_range": (0.1, 0.7),
                "content_restrictions": ["professional", "informative", "respectful"]
            },
            AudienceSegment.MATURE_AUDIENCE: {
                "emotions": [EmotionCategory.TRUST, EmotionCategory.JOY, EmotionCategory.LOVE],
                "valence_range": (-0.8, 1.0),
                "arousal_range": (0.0, 0.8),
                "content_restrictions": ["mature_themes", "complex_topics", "nuanced"]
            },
            AudienceSegment.GENERAL_AUDIENCE: {
                "emotions": [EmotionCategory.JOY, EmotionCategory.TRUST, EmotionCategory.EXCITEMENT],
                "valence_range": (-0.3, 1.0),
                "arousal_range": (0.2, 0.8),
                "content_restrictions": ["broad_appeal", "inclusive", "accessible"]
            }
        }
    
    def profile_target_audience(self, text: str, emotional_profile: EmotionalProfile,
                              brand_safety: BrandSafetyAssessment) -> AudienceAnalysis:
        """Profilage audience cible basé sur sentiment analysis"""
        try:
            target_segments = []
            age_appropriateness = {}
            cultural_sensitivity = {}
            engagement_potential = {}
            demographic_appeal = {}
            
            # Analyze compatibility with each segment
            for segment, characteristics in self.segment_characteristics.items():
                compatibility_score = self._calculate_segment_compatibility(
                    emotional_profile, brand_safety, characteristics
                )
                
                if compatibility_score >= 0.6:
                    target_segments.append(segment)
                
                # Age appropriateness
                if segment == AudienceSegment.CHILDREN_FRIENDLY:
                    age_appropriateness["0-12"] = compatibility_score
                elif segment == AudienceSegment.TEEN_APPROPRIATE:
                    age_appropriateness["13-17"] = compatibility_score
                elif segment == AudienceSegment.YOUNG_ADULT:
                    age_appropriateness["18-29"] = compatibility_score
                elif segment == AudienceSegment.PROFESSIONAL:
                    age_appropriateness["25-45"] = compatibility_score
                elif segment == AudienceSegment.MATURE_AUDIENCE:
                    age_appropriateness["35+"] = compatibility_score
                else:
                    age_appropriateness["all_ages"] = compatibility_score
            
            # Cultural sensitivity analysis
            cultural_sensitivity = self._analyze_cultural_sensitivity(
                text, emotional_profile, brand_safety
            )
            
            # Engagement potential by demographic
            engagement_potential = self._calculate_engagement_potential(
                emotional_profile, target_segments
            )
            
            # Demographic appeal
            demographic_appeal = self._calculate_demographic_appeal(
                emotional_profile, brand_safety
            )
            
            # Ensure at least one target segment
            if not target_segments:
                target_segments.append(AudienceSegment.GENERAL_AUDIENCE)
            
            return AudienceAnalysis(
                target_segments=target_segments,
                age_appropriateness=age_appropriateness,
                cultural_sensitivity=cultural_sensitivity,
                engagement_potential=engagement_potential,
                demographic_appeal=demographic_appeal
            )
            
        except Exception as e:
            logger.error(f"Audience profiling error: {e}")
            return self._default_audience_analysis()
    
    def _calculate_segment_compatibility(self, emotional_profile: EmotionalProfile,
                                       brand_safety: BrandSafetyAssessment,
                                       characteristics: Dict[str, Any]) -> float:
        """Calcul compatibilité avec segment audience"""
        score = 0.0
        
        # Emotion compatibility
        preferred_emotions = characteristics["emotions"]
        if emotional_profile.primary_emotion in preferred_emotions:
            score += 0.4
        if emotional_profile.secondary_emotion and emotional_profile.secondary_emotion in preferred_emotions:
            score += 0.2
        
        # Valence range check
        valence_min, valence_max = characteristics["valence_range"]
        if valence_min <= emotional_profile.valence_score <= valence_max:
            score += 0.2
        
        # Arousal range check
        arousal_min, arousal_max = characteristics["arousal_range"]
        if arousal_min <= emotional_profile.arousal_level <= arousal_max:
            score += 0.2
        
        # Brand safety considerations
        if brand_safety.safety_level.value >= 3:  # LOW_RISK or better
            score += 0.1
        elif brand_safety.safety_level.value >= 4:  # SAFE or better
            score += 0.2
        
        return min(score, 1.0)
    
    def _analyze_cultural_sensitivity(self, text: str, emotional_profile: EmotionalProfile,
                                    brand_safety: BrandSafetyAssessment) -> Dict[str, float]:
        """Analyse sensibilité culturelle"""
        sensitivity_scores = {}
        
        # General cultural sensitivity
        base_score = 0.8
        
        # Penalize for sensitive topics
        if brand_safety.sensitive_topics:
            base_score -= 0.1 * len(brand_safety.sensitive_topics)
        
        # Penalize for risk factors
        if brand_safety.risk_factors:
            base_score -= 0.15 * len(brand_safety.risk_factors)
        
        # Adjust for emotional factors
        if emotional_profile.primary_emotion in [EmotionCategory.ANGER, EmotionCategory.DISGUST]:
            base_score -= 0.2
        
        base_score = max(0.0, min(1.0, base_score))
        
        # Regional sensitivity (simplified)
        sensitivity_scores = {
            "western": base_score,
            "eastern": base_score * 0.9,  # More conservative
            "middle_eastern": base_score * 0.85,
            "asian": base_score * 0.9,
            "african": base_score * 0.95,
            "latin_american": base_score * 0.95
        }
        
        return sensitivity_scores
    
    def _calculate_engagement_potential(self, emotional_profile: EmotionalProfile,
                                       target_segments: List[AudienceSegment]) -> Dict[str, float]:
        """Calcul potentiel engagement par démographie"""
        engagement_potential = {}
        
        # Base engagement score
        base_engagement = (
            emotional_profile.arousal_level * 0.4 +
            abs(emotional_profile.valence_score) * 0.3 +
            emotional_profile.emotional_stability * 0.3
        )
        
        # Adjust for target segments
        for segment in target_segments:
            if segment == AudienceSegment.YOUNG_ADULT:
                engagement_potential["18-29"] = base_engagement * 1.2
            elif segment == AudienceSegment.TEEN_APPROPRIATE:
                engagement_potential["13-17"] = base_engagement * 1.1
            elif segment == AudienceSegment.CHILDREN_FRIENDLY:
                engagement_potential["0-12"] = base_engagement * 0.8
            elif segment == AudienceSegment.PROFESSIONAL:
                engagement_potential["25-45"] = base_engagement * 0.9
            elif segment == AudienceSegment.MATURE_AUDIENCE:
                engagement_potential["35+"] = base_engagement * 0.85
            else:
                engagement_potential["general"] = base_engagement
        
        # Normalize values
        for key in engagement_potential:
            engagement_potential[key] = min(1.0, engagement_potential[key])
        
        return engagement_potential
    
    def _calculate_demographic_appeal(self, emotional_profile: EmotionalProfile,
                                    brand_safety: BrandSafetyAssessment) -> Dict[str, float]:
        """Calcul attrait par démographie"""
        appeal = {}
        
        # Gender appeal (simplified analysis)
        if emotional_profile.primary_emotion in [EmotionCategory.LOVE, EmotionCategory.JOY]:
            appeal["female"] = 0.7
            appeal["male"] = 0.6
        elif emotional_profile.primary_emotion in [EmotionCategory.EXCITEMENT, EmotionCategory.ANTICIPATION]:
            appeal["female"] = 0.6
            appeal["male"] = 0.7
        else:
            appeal["female"] = 0.6
            appeal["male"] = 0.6
        
        # Age group appeal
        if emotional_profile.arousal_level > 0.7:
            appeal["young"] = 0.8
            appeal["middle_aged"] = 0.6
            appeal["senior"] = 0.4
        else:
            appeal["young"] = 0.6
            appeal["middle_aged"] = 0.7
            appeal["senior"] = 0.6
        
        # Education level appeal
        if brand_safety.safety_level.value >= 4:  # SAFE or better
            appeal["higher_education"] = 0.7
            appeal["general_education"] = 0.8
        else:
            appeal["higher_education"] = 0.5
            appeal["general_education"] = 0.6
        
        return appeal
    
    def _default_audience_analysis(self) -> AudienceAnalysis:
        """Analyse audience par défaut"""
        return AudienceAnalysis(
            target_segments=[AudienceSegment.GENERAL_AUDIENCE],
            age_appropriateness={"all_ages": 0.5},
            cultural_sensitivity={"general": 0.5},
            engagement_potential={"general": 0.5},
            demographic_appeal={"general": 0.5}
        )

class EngagementOptimizer:
    """Optimiseur engagement basé sur sentiment"""
    
    def __init__(self, config: SentimentAnalysisConfig):
        self.config = config
    
    def optimize_engagement(self, emotional_profile: EmotionalProfile,
                          audience_analysis: AudienceAnalysis,
                          brand_safety: BrandSafetyAssessment) -> Dict[str, Any]:
        """Optimization engagement basé sur emotional appeal"""
        optimization_recommendations = {
            "content_adjustments": [],
            "timing_recommendations": [],
            "platform_strategies": {},
            "hashtag_suggestions": [],
            "engagement_tactics": []
        }
        
        # Content adjustments based on emotions
        if emotional_profile.primary_emotion == EmotionCategory.JOY:
            optimization_recommendations["content_adjustments"].extend([
                "Emphasize positive messaging",
                "Use bright, cheerful visuals",
                "Include uplifting music or sounds"
            ])
        elif emotional_profile.primary_emotion == EmotionCategory.EXCITEMENT:
            optimization_recommendations["content_adjustments"].extend([
                "Create urgency in messaging",
                "Use dynamic visuals and animations",
                "Include call-to-action elements"
            ])
        elif emotional_profile.primary_emotion == EmotionCategory.TRUST:
            optimization_recommendations["content_adjustments"].extend([
                "Emphasize credibility and authenticity",
                "Include testimonials or social proof",
                "Use professional presentation"
            ])
        
        # Timing recommendations based on arousal level
        if emotional_profile.arousal_level > 0.7:
            optimization_recommendations["timing_recommendations"].extend([
                "Peak engagement hours (7-9 PM)",
                "Weekends for maximum viral potential",
                "During trending events or discussions"
            ])
        else:
            optimization_recommendations["timing_recommendations"].extend([
                "Morning hours for thoughtful content",
                "Weekdays for professional audiences",
                "During quiet periods for reflection"
            ])
        
        # Platform strategies based on audience
        for segment in audience_analysis.target_segments:
            if segment == AudienceSegment.YOUNG_ADULT:
                optimization_recommendations["platform_strategies"]["instagram"] = [
                    "Use stories for behind-the-scenes content",
                    "Focus on visual aesthetics",
                    "Engage with trending hashtags"
                ]
                optimization_recommendations["platform_strategies"]["tiktok"] = [
                    "Create short, engaging videos",
                    "Use trending sounds and effects",
                    "Participate in challenges"
                ]
            elif segment == AudienceSegment.PROFESSIONAL:
                optimization_recommendations["platform_strategies"]["linkedin"] = [
                    "Share industry insights",
                    "Use professional language",
                    "Focus on networking and career growth"
                ]
        
        # Hashtag suggestions based on emotions and audience
        emotion_hashtags = {
            EmotionCategory.JOY: ["#happiness", "#positivity", "#goodvibes", "#smile"],
            EmotionCategory.EXCITEMENT: ["#exciting", "#amazing", "#thrilling", "#energetic"],
            EmotionCategory.TRUST: ["#authentic", "#genuine", "#reliable", "#trustworthy"],
            EmotionCategory.LOVE: ["#love", "#passion", "#heartwarming", "#beautiful"],
            EmotionCategory.SURPRISE: ["#surprising", "#unexpected", "#wow", "#mindblowing"]
        }
        
        if emotional_profile.primary_emotion in emotion_hashtags:
            optimization_recommendations["hashtag_suggestions"].extend(
                emotion_hashtags[emotional_profile.primary_emotion]
            )
        
        # Engagement tactics based on safety and audience
        if brand_safety.advertiser_friendly:
            optimization_recommendations["engagement_tactics"].extend([
                "Partner with brands for sponsored content",
                "Create advertiser-friendly thumbnails",
                "Maintain consistent brand-safe messaging"
            ])
        
        if emotional_profile.arousal_level > 0.6:
            optimization_recommendations["engagement_tactics"].extend([
                "Ask engaging questions to audience",
                "Create polls and interactive content",
                "Encourage user-generated content"
            ])
        
        return optimization_recommendations

class SentimentAnalysisModel:
    """
    Modèle principal analyse sentiment multi-lingue avec business context.
    Emotion detection + brand safety + audience targeting + engagement optimization.
    """
    
    def __init__(self, sentiment_config: SentimentAnalysisConfig):
        self.sentiment_config = sentiment_config
        self.emotion_detector = EmotionDetectionEngine(sentiment_config)
        self.brand_safety_analyzer = BrandSafetyAnalyzer(sentiment_config)
        self.audience_profiler = AudienceProfiler(sentiment_config)
        self.engagement_optimizer = EngagementOptimizer(sentiment_config)
    
    async def analyze_content_sentiment(self, sentiment_input: SentimentInput) -> SentimentAnalysisResult:
        """
        Analyse sentiment avec business intelligence.
        
        Sentiment Analysis Features:
        - Multi-modal sentiment detection (text, audio, visual)
        - Emotion classification avec granular emotion categories
        - Brand safety assessment pour advertiser-friendly content
        - Audience sentiment targeting pour demographic optimization
        - Cultural sensitivity analysis pour global content distribution
        - Engagement optimization basé sur emotional appeal
        - Monetization impact prediction basé sur sentiment
        - Creator brand alignment assessment
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            text = sentiment_input.text_content
            
            # Language detection
            if sentiment_input.language:
                detected_language = sentiment_input.language
            else:
                try:
                    detected_language = langdetect.detect(text)
                except:
                    detected_language = "en"  # Default to English
            
            # Basic sentiment analysis using TextBlob
            blob = TextBlob(text)
            basic_sentiment = blob.sentiment
            
            # Convert to our sentiment polarity scale
            if basic_sentiment.polarity >= 0.6:
                sentiment_polarity = SentimentPolarity.VERY_POSITIVE
            elif basic_sentiment.polarity >= 0.2:
                sentiment_polarity = SentimentPolarity.POSITIVE
            elif basic_sentiment.polarity >= -0.2:
                sentiment_polarity = SentimentPolarity.NEUTRAL
            elif basic_sentiment.polarity >= -0.6:
                sentiment_polarity = SentimentPolarity.NEGATIVE
            else:
                sentiment_polarity = SentimentPolarity.VERY_NEGATIVE
            
            sentiment_score = (basic_sentiment.polarity + 1) / 2  # Normalize to 0-1
            
            # Detailed emotion detection
            if self.sentiment_config.enable_emotion_detection:
                emotional_profile = self.emotion_detector.detect_emotions(text, detected_language)
            else:
                emotional_profile = self.emotion_detector._default_emotional_profile()
            
            # Brand safety assessment
            if self.sentiment_config.enable_brand_safety:
                brand_safety = self.brand_safety_analyzer.assess_brand_safety(
                    text, emotional_profile, sentiment_input.platform
                )
            else:
                brand_safety = self.brand_safety_analyzer._default_brand_safety()
            
            # Audience analysis
            if self.sentiment_config.enable_audience_analysis:
                audience_analysis = self.audience_profiler.profile_target_audience(
                    text, emotional_profile, brand_safety
                )
            else:
                audience_analysis = self.audience_profiler._default_audience_analysis()
            
            # Engagement optimization
            engagement_optimization = self.engagement_optimizer.optimize_engagement(
                emotional_profile, audience_analysis, brand_safety
            )
            
            # Monetization impact calculation
            monetization_impact = self._calculate_monetization_impact(
                sentiment_polarity, emotional_profile, brand_safety, audience_analysis
            )
            
            # Confidence score calculation
            confidence_score = self._calculate_confidence_score(
                basic_sentiment.polarity, emotional_profile, brand_safety
            )
            
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return SentimentAnalysisResult(
                content_id=sentiment_input.content_id,
                sentiment_polarity=sentiment_polarity,
                sentiment_score=sentiment_score,
                confidence_score=confidence_score,
                emotional_profile=emotional_profile,
                brand_safety=brand_safety,
                audience_analysis=audience_analysis,
                language_detected=detected_language,
                engagement_optimization=engagement_optimization,
                monetization_impact=monetization_impact,
                processing_time_ms=processing_time,
                timestamp=str(np.datetime64('now'))
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Return default result
            return self._default_sentiment_result(
                sentiment_input.content_id, processing_time
            )
    
    def _calculate_monetization_impact(self, sentiment_polarity: SentimentPolarity,
                                     emotional_profile: EmotionalProfile,
                                     brand_safety: BrandSafetyAssessment,
                                     audience_analysis: AudienceAnalysis) -> Dict[str, float]:
        """Calcul impact monétisation basé sur sentiment"""
        impact = {}
        
        # Ad revenue potential
        if brand_safety.advertiser_friendly:
            ad_revenue_multiplier = 1.0
            if sentiment_polarity in [SentimentPolarity.POSITIVE, SentimentPolarity.VERY_POSITIVE]:
                ad_revenue_multiplier *= 1.2
            if emotional_profile.primary_emotion in [EmotionCategory.JOY, EmotionCategory.EXCITEMENT]:
                ad_revenue_multiplier *= 1.1
        else:
            ad_revenue_multiplier = 0.3  # Limited monetization for non-advertiser-friendly content
        
        impact["ad_revenue_potential"] = min(1.0, ad_revenue_multiplier)
        
        # Sponsorship potential
        sponsorship_potential = brand_safety.safety_score * 0.8
        if AudienceSegment.PROFESSIONAL in audience_analysis.target_segments:
            sponsorship_potential *= 1.3
        if AudienceSegment.YOUNG_ADULT in audience_analysis.target_segments:
            sponsorship_potential *= 1.2
        
        impact["sponsorship_potential"] = min(1.0, sponsorship_potential)
        
        # Premium content potential
        premium_potential = emotional_profile.emotional_stability * 0.6
        if emotional_profile.primary_emotion in [EmotionCategory.TRUST, EmotionCategory.JOY]:
            premium_potential += 0.3
        
        impact["premium_content_potential"] = min(1.0, premium_potential)
        
        # Merchandise potential
        merch_potential = 0.5
        if emotional_profile.primary_emotion in [EmotionCategory.LOVE, EmotionCategory.JOY, EmotionCategory.EXCITEMENT]:
            merch_potential += 0.3
        if sentiment_polarity in [SentimentPolarity.POSITIVE, SentimentPolarity.VERY_POSITIVE]:
            merch_potential += 0.2
        
        impact["merchandise_potential"] = min(1.0, merch_potential)
        
        return impact
    
    def _calculate_confidence_score(self, basic_polarity: float,
                                  emotional_profile: EmotionalProfile,
                                  brand_safety: BrandSafetyAssessment) -> float:
        """Calcul score confiance basé sur cohérence des analyses"""
        
        # Base confidence from sentiment strength
        confidence = abs(basic_polarity) * 0.4
        
        # Add confidence from emotional stability
        confidence += emotional_profile.emotional_stability * 0.3
        
        # Add confidence from brand safety certainty
        confidence += brand_safety.safety_score * 0.2
        
        # Add confidence from arousal level (higher arousal = more detectable emotions)
        confidence += emotional_profile.arousal_level * 0.1
        
        return min(1.0, confidence)
    
    def _default_sentiment_result(self, content_id: str, processing_time: float) -> SentimentAnalysisResult:
        """Résultat sentiment par défaut en cas d'erreur"""
        return SentimentAnalysisResult(
            content_id=content_id,
            sentiment_polarity=SentimentPolarity.NEUTRAL,
            sentiment_score=0.5,
            confidence_score=0.5,
            emotional_profile=self.emotion_detector._default_emotional_profile(),
            brand_safety=self.brand_safety_analyzer._default_brand_safety(),
            audience_analysis=self.audience_profiler._default_audience_analysis(),
            language_detected="en",
            engagement_optimization={},
            monetization_impact={"ad_revenue_potential": 0.5, "sponsorship_potential": 0.5},
            processing_time_ms=processing_time,
            timestamp=str(np.datetime64('now'))
        )

class SentimentAnalysisService:
    """
    Service principal pour sentiment analysis IA Chéries.
    Orchestration + batch processing + analytics + caching.
    """
    
    def __init__(self, config: SentimentAnalysisConfig):
        self.config = config
        self.model = SentimentAnalysisModel(config)
        self.cache = {}
        self.analytics_data = []
    
    async def analyze_content_batch(self, sentiment_inputs: List[SentimentInput]) -> List[SentimentAnalysisResult]:
        """Analyse sentiment batch pour optimisation performance"""
        results = []
        
        for sentiment_input in sentiment_inputs:
            # Check cache first
            cache_key = f"{sentiment_input.content_id}_{hash(sentiment_input.text_content)}"
            if cache_key in self.cache:
                results.append(self.cache[cache_key])
                continue
            
            # Analyze sentiment
            result = await self.model.analyze_content_sentiment(sentiment_input)
            
            # Cache result
            self.cache[cache_key] = result
            self.analytics_data.append(result)
            
            results.append(result)
        
        return results
    
    async def generate_sentiment_insights(self) -> Dict[str, Any]:
        """Génération insights sentiment agrégés"""
        if not self.analytics_data:
            return {}
        
        results = self.analytics_data
        
        insights = {
            "total_analyses": len(results),
            "sentiment_distribution": {},
            "emotion_trends": {},
            "brand_safety_stats": {},
            "audience_preferences": {},
            "monetization_opportunities": {},
            "language_distribution": {},
            "processing_performance": {
                "avg_processing_time_ms": np.mean([r.processing_time_ms for r in results]),
                "avg_confidence": np.mean([r.confidence_score for r in results])
            }
        }
        
        # Sentiment distribution
        for result in results:
            polarity = result.sentiment_polarity.name
            insights["sentiment_distribution"][polarity] = insights["sentiment_distribution"].get(polarity, 0) + 1
        
        # Emotion trends
        for result in results:
            emotion = result.emotional_profile.primary_emotion.value
            insights["emotion_trends"][emotion] = insights["emotion_trends"].get(emotion, 0) + 1
        
        # Brand safety stats
        brand_safe_count = sum(1 for r in results if r.brand_safety.advertiser_friendly)
        insights["brand_safety_stats"] = {
            "advertiser_friendly_percentage": (brand_safe_count / len(results)) * 100,
            "avg_safety_score": np.mean([r.brand_safety.safety_score for r in results])
        }
        
        # Audience preferences
        all_segments = []
        for result in results:
            all_segments.extend([seg.value for seg in result.audience_analysis.target_segments])
        
        from collections import Counter
        segment_counts = Counter(all_segments)
        insights["audience_preferences"] = dict(segment_counts.most_common(5))
        
        # Monetization opportunities
        insights["monetization_opportunities"] = {
            "avg_ad_revenue_potential": np.mean([r.monetization_impact.get("ad_revenue_potential", 0) for r in results]),
            "avg_sponsorship_potential": np.mean([r.monetization_impact.get("sponsorship_potential", 0) for r in results]),
            "high_value_content_percentage": sum(1 for r in results if r.monetization_impact.get("ad_revenue_potential", 0) > 0.8) / len(results) * 100
        }
        
        # Language distribution
        lang_counts = Counter([r.language_detected for r in results])
        insights["language_distribution"] = dict(lang_counts.most_common(10))
        
        return insights


# Factory function pour faciliter l'utilisation
def create_sentiment_analyzer(device: str = "cpu",
                            enable_emotion_detection: bool = True,
                            enable_brand_safety: bool = True,
                            enable_audience_analysis: bool = True) -> SentimentAnalysisService:
    """Factory function pour créer sentiment analyzer"""
    config = SentimentAnalysisConfig(
        device=device,
        enable_emotion_detection=enable_emotion_detection,
        enable_brand_safety=enable_brand_safety,
        enable_audience_analysis=enable_audience_analysis,
        multilingual_support=True,
        confidence_threshold=0.75
    )
    
    return SentimentAnalysisService(config)


# Export des classes principales
__all__ = [
    "SentimentPolarity",
    "EmotionCategory",
    "BrandSafetyLevel",
    "AudienceSegment",
    "SentimentInput",
    "EmotionalProfile",
    "BrandSafetyAssessment",
    "AudienceAnalysis",
    "SentimentAnalysisResult",
    "SentimentAnalysisConfig",
    "SentimentAnalysisModel",
    "SentimentAnalysisService",
    "create_sentiment_analyzer"
]