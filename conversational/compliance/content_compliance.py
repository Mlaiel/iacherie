"""Content Compliance Engine - Advanced Content Safety and Compliance System

This module provides comprehensive content compliance validation for conversational AI,
including harmful content detection, age-appropriate filtering, and brand safety compliance.

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum

from ..core.database import DatabaseManager
from ..core.cache import CacheManager
from ..ml.toxicity_detector import ToxicityDetector
from ..ml.sentiment_analyzer import SentimentAnalyzer
from ..ml.content_classifier import ContentClassifier


class ContentRiskLevel(Enum):
    """
Content risk severity levels"""

    SAFE = "safe"
    LOW_RISK = "low_risk"
    MODERATE_RISK = "moderate_risk"
    HIGH_RISK = "high_risk"
    HARMFUL = "harmful"


class ContentCategory(Enum):
    """Content safety categories"""

    TOXICITY = "toxicity"
    HARASSMENT = "harassment"
    HATE_SPEECH = "hate_speech"
    VIOLENCE = "violence"
    SEXUAL_CONTENT = "sexual_content"
    PROFANITY = "profanity"
    SELF_HARM = "self_harm"
    ILLEGAL_ACTIVITY = "illegal_activity"
    MISINFORMATION = "misinformation"
    SPAM = "spam"
    PERSONAL_ATTACKS = "personal_attacks"
    DISCRIMINATION = "discrimination"


class AgeRating(Enum):
    """Age appropriateness ratings"""

    ALL_AGES = "all_ages"
    TEEN = "teen"
    MATURE = "mature"
    ADULT_ONLY = "adult_only"
    RESTRICTED = "restricted"


class BrandSafetyLevel(Enum):
    """Brand safety compliance levels"""

    BRAND_SAFE = "brand_safe"
    LOW_RISK = "low_risk"
    MODERATE_RISK = "moderate_risk"
    HIGH_RISK = "high_risk"
    BRAND_UNSAFE = "brand_unsafe"


@dataclass
class ContentViolation:
    """Content safety violation structure"""
    category: ContentCategory
    risk_level: ContentRiskLevel
    confidence_score: float
    description: str
    evidence: List[str]
    severity: str
    auto_actionable: bool
    recommended_actions: List[str]
    affected_segments: List[Tuple[int, int]]
    context_analysis: Dict[str, Any]


@dataclass
class ContentSafetyResult:
    """
Content safety assessment result"""
    overall_safety_score: float
    risk_level: ContentRiskLevel
    age_rating: AgeRating
    brand_safety_level: BrandSafetyLevel
    violations: List[ContentViolation]
    warnings: List[str]
    recommendations: List[str]
    content_filtering_applied: bool
    moderation_required: bool
    processing_time_ms: int
    confidence_score: float


@dataclass
class ContentModerationAction:
    """
Content moderation action structure"""
    action_type: str
    content_segment: str
    replacement_text: Optional[str]
    warning_message: Optional[str]
    justification: str
    automated: bool
    human_review_required: bool


class ContentComplianceEngine:
    """
    Advanced content safety and compliance validation system.
    
    Provides comprehensive content safety assessment including toxicity detection,
    age-appropriate filtering, brand safety validation, and automated content moderation.
    """
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        cache_manager: CacheManager,
        toxicity_detector: Optional[ToxicityDetector] = None,
        sentiment_analyzer: Optional[SentimentAnalyzer] = None,
        content_classifier: Optional[ContentClassifier] = None
    ):
        self.db_manager = db_manager
        self.cache_manager = cache_manager
        self.toxicity_detector = toxicity_detector or ToxicityDetector()
        self.sentiment_analyzer = sentiment_analyzer or SentimentAnalyzer()
        self.content_classifier = content_classifier or ContentClassifier()
        self.logger = logging.getLogger(__name__)
        
        # Content safety configuration
        self.safety_thresholds = self._load_safety_thresholds()
        self.content_patterns = self._load_content_patterns()
        self.brand_safety_rules = self._load_brand_safety_rules()
        self.age_rating_rules = self._load_age_rating_rules()
        
        # Moderation configuration
        self.auto_moderation_enabled = True
        self.human_review_threshold = 0.7
        
        self.logger.info("ContentComplianceEngine initialized with safety detection systems")
    
    def _load_safety_thresholds(self) -> Dict[ContentCategory, Dict[str, float]]:
        """Load content safety thresholds"""
        return {
            ContentCategory.TOXICITY: {
                "safe": 0.2,
                "low_risk": 0.4,
                "moderate_risk": 0.6,
                "high_risk": 0.8,
                "harmful": 0.9
            },
            ContentCategory.HARASSMENT: {
                "safe": 0.15,
                "low_risk": 0.3,
                "moderate_risk": 0.5,
                "high_risk": 0.7,
                "harmful": 0.85
            },
            ContentCategory.HATE_SPEECH: {
                "safe": 0.1,
                "low_risk": 0.25,
                "moderate_risk": 0.45,
                "high_risk": 0.65,
                "harmful": 0.8
            },
            ContentCategory.VIOLENCE: {
                "safe": 0.2,
                "low_risk": 0.35,
                "moderate_risk": 0.55,
                "high_risk": 0.75,
                "harmful": 0.9
            },
            ContentCategory.SEXUAL_CONTENT: {
                "safe": 0.25,
                "low_risk": 0.4,
                "moderate_risk": 0.6,
                "high_risk": 0.8,
                "harmful": 0.95
            }
        }
    
    def _load_content_patterns(self) -> Dict[ContentCategory, List[Dict[str, Any]]]:
        """Load content detection patterns"""
        return {
            ContentCategory.PROFANITY: [
                {
                    "pattern": r"\b(damn|hell|crap|shit|fuck|bitch|asshole|bastard)\b",
                    "severity": "moderate",
                    "confidence": 0.9,
                    "auto_filter": True
                }
            ],
            ContentCategory.HARASSMENT: [
                {
                    "pattern": r"\b(you are (stupid|idiot|moron|loser))\b",
                    "severity": "high",
                    "confidence": 0.8,
                    "auto_filter": True
                },
                {
                    "pattern": r"\b(kill yourself|harm yourself|end it all)\b",
                    "severity": "critical",
                    "confidence": 0.95,
                    "auto_filter": True
                }
            ],
            ContentCategory.HATE_SPEECH: [
                {
                    "pattern": r"\b(terrorist|nazi|hitler|genocide)\b",
                    "severity": "critical",
                    "confidence": 0.9,
                    "auto_filter": True
                }
            ],
            ContentCategory.VIOLENCE: [
                {
                    "pattern": r"\b(murder|kill|violence|assault|weapon|bomb|explosive)\b",
                    "severity": "high",
                    "confidence": 0.7,
                    "auto_filter": False
                }
            ],
            ContentCategory.ILLEGAL_ACTIVITY: [
                {
                    "pattern": r"\b(drugs|cocaine|heroin|marijuana|illegal|fraud|scam)\b",
                    "severity": "high",
                    "confidence": 0.6,
                    "auto_filter": False
                }
            ],
            ContentCategory.SELF_HARM: [
                {
                    "pattern": r"\b(suicide|self-harm|cutting|overdose|depression)\b",
                    "severity": "critical",
                    "confidence": 0.8,
                    "auto_filter": False
                }
            ]
        }
    
    def _load_brand_safety_rules(self) -> Dict[str, Any]:
        """Load brand safety rules"""
        return {
            "unsafe_topics": [
                "controversial_politics", "extremism", "adult_content", 
                "violence", "illegal_activities", "hate_speech"
            ],
            "contextual_risks": [
                "negative_sentiment_brands", "competitor_mentions", 
                "crisis_situations", "inappropriate_humor"
            ],
            "brand_safe_score_threshold": 0.7,
            "advertiser_friendly_threshold": 0.8
        }
    
    def _load_age_rating_rules(self) -> Dict[AgeRating, Dict[str, Any]]:
        """Load age rating classification rules"""
        return {
            AgeRating.ALL_AGES: {
                "max_toxicity": 0.1,
                "allowed_topics": ["education", "entertainment", "general"],
                "forbidden_content": ["violence", "sexual_content", "profanity"]
            },
            AgeRating.TEEN: {
                "max_toxicity": 0.3,
                "allowed_topics": ["education", "entertainment", "mild_romance", "adventure"],
                "forbidden_content": ["explicit_violence", "sexual_content", "strong_profanity"]
            },
            AgeRating.MATURE: {
                "max_toxicity": 0.6,
                "allowed_topics": ["complex_themes", "mature_discussions", "mild_violence"],
                "forbidden_content": ["explicit_sexual_content", "extreme_violence"]
            },
            AgeRating.ADULT_ONLY: {
                "max_toxicity": 0.8,
                "allowed_topics": ["adult_themes", "complex_mature_content"],
                "forbidden_content": ["illegal_content", "extreme_harm"]
            }
        }
    
    async def validate_content_safety(
        self,
        user_input: str,
        ai_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive content safety validation.
        
        Args:
            user_input: User's input text
            ai_response: AI's generated response
            context: Additional context information
            
        Returns:
            Dict containing content safety assessment
        """
        start_time = datetime.now()
        
        try:
            self.logger.debug("Starting content safety validation")
            
            # Check cache for recent validation
            cache_key = f"content_safety_{hash(user_input + ai_response)}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Initialize safety result
            result = ContentSafetyResult(
                overall_safety_score=1.0,
                risk_level=ContentRiskLevel.SAFE,
                age_rating=AgeRating.ALL_AGES,
                brand_safety_level=BrandSafetyLevel.BRAND_SAFE,
                violations=[],
                warnings=[],
                recommendations=[],
                content_filtering_applied=False,
                moderation_required=False,
                processing_time_ms=0,
                confidence_score=1.0
            )
            
            # Combine content for analysis
            combined_content = f"{user_input} {ai_response}"
            
            # Pattern-based safety detection
            pattern_violations = await self._detect_pattern_violations(combined_content)
            result.violations.extend(pattern_violations)
            
            # ML-based toxicity detection
            toxicity_result = await self._detect_toxicity(combined_content, context)
            if toxicity_result["violations"]:
                result.violations.extend(toxicity_result["violations"])
            
            # Sentiment analysis for context
            sentiment_analysis = await self._analyze_content_sentiment(combined_content)
            
            # Content classification
            content_classification = await self._classify_content(combined_content, context)
            
            # Age rating assessment
            result.age_rating = self._assess_age_rating(result.violations, content_classification)
            
            # Brand safety assessment
            result.brand_safety_level = self._assess_brand_safety(
                result.violations, sentiment_analysis, content_classification
            )
            
            # Calculate overall safety score
            result.overall_safety_score = self._calculate_safety_score(
                result.violations, sentiment_analysis, content_classification
            )
            
            # Determine risk level
            result.risk_level = self._determine_risk_level(result.overall_safety_score)
            
            # Generate recommendations
            result.recommendations = self._generate_safety_recommendations(result)
            
            # Apply content filtering if needed
            if self.auto_moderation_enabled:
                moderation_actions = self._apply_content_moderation(result.violations)
                result.content_filtering_applied = bool(moderation_actions)
            
            # Determine if human review is required
            result.moderation_required = (
                result.risk_level in [ContentRiskLevel.HIGH_RISK, ContentRiskLevel.HARMFUL] or
                result.overall_safety_score < self.human_review_threshold
            )
            
            # Calculate confidence score
            result.confidence_score = self._calculate_confidence_score(result.violations)
            
            # Calculate processing time
            processing_time = datetime.now() - start_time
            result.processing_time_ms = int(processing_time.total_seconds() * 1000)
            
            # Store safety assessment
            await self._store_safety_assessment(result, user_input, ai_response)
            
            # Cache result
            await self.cache_manager.set(cache_key, result, ttl=1800)  # 30 minutes
            
            return {
                "safety_score": result.overall_safety_score,
                "risk_level": result.risk_level.value,
                "age_rating": result.age_rating.value,
                "brand_safety": result.brand_safety_level.value,
                "violations": [
                    {
                        "category": v.category.value,
                        "severity": v.severity,
                        "confidence": v.confidence_score,
                        "description": v.description
                    }
                    for v in result.violations
                ],
                "recommendations": result.recommendations,
                "moderation_required": result.moderation_required,
                "content_filtered": result.content_filtering_applied
            }
            
        except Exception as e:
            self.logger.error(f"Error in content safety validation: {str(e)}")
            return {
                "safety_score": 0.0,
                "risk_level": "unknown",
                "violations": [{"type": "validation_error", "message": str(e)}],
                "recommendations": ["Manual content review required due to validation error"]
            }
    
    async def _detect_pattern_violations(self, content: str) -> List[ContentViolation]:
        """Detect content violations using pattern matching"""
        violations = []
        
        for category, patterns in self.content_patterns.items():
            for pattern_config in patterns:
                pattern = pattern_config["pattern"]
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                
                if matches:
                    evidence = [match.group() for match in matches]
                    affected_segments = [(match.start(), match.end()) for match in matches]
                    
                    # Determine risk level based on severity
                    severity = pattern_config["severity"]
                    if severity == "critical":
                        risk_level = ContentRiskLevel.HARMFUL
                    elif severity == "high":
                        risk_level = ContentRiskLevel.HIGH_RISK
                    elif severity == "moderate":
                        risk_level = ContentRiskLevel.MODERATE_RISK
                    else:
                        risk_level = ContentRiskLevel.LOW_RISK
                    
                    violation = ContentViolation(
                        category=category,
                        risk_level=risk_level,
                        confidence_score=pattern_config["confidence"],
                        description=f"{category.value} content detected",
                        evidence=evidence,
                        severity=severity,
                        auto_actionable=pattern_config.get("auto_filter", False),
                        recommended_actions=self._get_category_actions(category),
                        affected_segments=affected_segments,
                        context_analysis={}
                    )
                    
                    violations.append(violation)
        
        return violations
    
    async def _detect_toxicity(
        self,
        content: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detect toxicity using ML models"""
        violations = []
        
        try:
            # Get toxicity scores for different categories
            toxicity_scores = await self.toxicity_detector.analyze_content(content)
            
            for category_name, score in toxicity_scores.items():
                try:
                    category = ContentCategory(category_name.lower())
                    thresholds = self.safety_thresholds.get(category, {})
                    
                    # Determine risk level based on score
                    if score >= thresholds.get("harmful", 0.9):
                        risk_level = ContentRiskLevel.HARMFUL
                    elif score >= thresholds.get("high_risk", 0.8):
                        risk_level = ContentRiskLevel.HIGH_RISK
                    elif score >= thresholds.get("moderate_risk", 0.6):
                        risk_level = ContentRiskLevel.MODERATE_RISK
                    elif score >= thresholds.get("low_risk", 0.4):
                        risk_level = ContentRiskLevel.LOW_RISK
                    else:
                        continue  # Score too low to be a violation
                    
                    violation = ContentViolation(
                        category=category,
                        risk_level=risk_level,
                        confidence_score=score,
                        description=f"ML-detected {category.value} (score: {score:.2f})",
                        evidence=[f"Toxicity score: {score:.2f}"],
                        severity=risk_level.value,
                        auto_actionable=score > 0.8,
                        recommended_actions=self._get_category_actions(category),
                        affected_segments=[],
                        context_analysis={"ml_model": "toxicity_detector", "score": score}
                    )
                    
                    violations.append(violation)
                    
                except ValueError:
                    # Skip unknown categories
                    continue
            
        except Exception as e:
            self.logger.error(f"Error in toxicity detection: {str(e)}")
        
        return {"violations": violations}
    
    async def _analyze_content_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze content sentiment for context"""
        try:
            sentiment_result = await self.sentiment_analyzer.analyze(content)
            return {
                "sentiment_score": sentiment_result.get("score", 0.0),
                "sentiment_label": sentiment_result.get("label", "neutral"),
                "confidence": sentiment_result.get("confidence", 0.0),
                "emotional_indicators": sentiment_result.get("emotions", [])
            }
        except Exception as e:
            self.logger.error(f"Error in sentiment analysis: {str(e)}")
            return {"sentiment_score": 0.0, "sentiment_label": "neutral"}
    
    async def _classify_content(
        self,
        content: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Classify content for safety assessment"""
        try:
            classification_result = await self.content_classifier.classify(content)
            return {
                "primary_topic": classification_result.get("topic", "general"),
                "content_type": classification_result.get("type", "conversational"),
                "themes": classification_result.get("themes", []),
                "intent": classification_result.get("intent", "informational"),
                "confidence": classification_result.get("confidence", 0.0)
            }
        except Exception as e:
            self.logger.error(f"Error in content classification: {str(e)}")
            return {"primary_topic": "general", "content_type": "conversational"}
    
    def _assess_age_rating(
        self,
        violations: List[ContentViolation],
        content_classification: Dict[str, Any]
    ) -> AgeRating:
        """Assess age appropriateness rating"""
        # Start with most permissive rating
        current_rating = AgeRating.ALL_AGES
        
        # Check violations against age rating rules
        for violation in violations:
            if violation.category in [ContentCategory.PROFANITY]:
                if violation.risk_level in [ContentRiskLevel.HIGH_RISK, ContentRiskLevel.HARMFUL]:
                    current_rating = max(current_rating, AgeRating.MATURE, key=lambda x: list(AgeRating).index(x))
                else:
                    current_rating = max(current_rating, AgeRating.TEEN, key=lambda x: list(AgeRating).index(x))
            
            elif violation.category in [ContentCategory.VIOLENCE, ContentCategory.SEXUAL_CONTENT]:
                if violation.risk_level == ContentRiskLevel.HARMFUL:
                    current_rating = AgeRating.ADULT_ONLY
                elif violation.risk_level == ContentRiskLevel.HIGH_RISK:
                    current_rating = max(current_rating, AgeRating.MATURE, key=lambda x: list(AgeRating).index(x))
                else:
                    current_rating = max(current_rating, AgeRating.TEEN, key=lambda x: list(AgeRating).index(x))
            
            elif violation.category in [ContentCategory.HATE_SPEECH, ContentCategory.HARASSMENT]:
                if violation.risk_level in [ContentRiskLevel.HIGH_RISK, ContentRiskLevel.HARMFUL]:
                    current_rating = AgeRating.ADULT_ONLY
                else:
                    current_rating = max(current_rating, AgeRating.MATURE, key=lambda x: list(AgeRating).index(x))
        
        return current_rating
    
    def _assess_brand_safety(
        self,
        violations: List[ContentViolation],
        sentiment_analysis: Dict[str, Any],
        content_classification: Dict[str, Any]
    ) -> BrandSafetyLevel:
        """
Assess brand safety compliance level"""
        # Check for brand-unsafe content
        brand_unsafe_categories = [
            ContentCategory.HATE_SPEECH,
            ContentCategory.HARASSMENT,
            ContentCategory.ILLEGAL_ACTIVITY,
            ContentCategory.SELF_HARM
        ]
        
        for violation in violations:
            if violation.category in brand_unsafe_categories:
                if violation.risk_level in [ContentRiskLevel.HIGH_RISK, ContentRiskLevel.HARMFUL]:
                    return BrandSafetyLevel.BRAND_UNSAFE
                else:
                    return BrandSafetyLevel.HIGH_RISK
        
        # Check sentiment for brand safety
        sentiment_score = sentiment_analysis.get("sentiment_score", 0.0)
        if sentiment_score < -0.7:
            return BrandSafetyLevel.MODERATE_RISK
        
        # Check content topic for brand safety
        primary_topic = content_classification.get("primary_topic", "")
        unsafe_topics = self.brand_safety_rules.get("unsafe_topics", [])
        
        if primary_topic in unsafe_topics:
            return BrandSafetyLevel.HIGH_RISK
        
        # Default to brand safe if no issues found
        return BrandSafetyLevel.BRAND_SAFE
    
    def _calculate_safety_score(
        self,
        violations: List[ContentViolation],
        sentiment_analysis: Dict[str, Any],
        content_classification: Dict[str, Any]
    ) -> float:
        """Calculate overall content safety score"""
        base_score = 1.0
        
        # Deduct for violations
        for violation in violations:
            if violation.risk_level == ContentRiskLevel.HARMFUL:
                base_score -= 0.4 * violation.confidence_score
            elif violation.risk_level == ContentRiskLevel.HIGH_RISK:
                base_score -= 0.3 * violation.confidence_score
            elif violation.risk_level == ContentRiskLevel.MODERATE_RISK:
                base_score -= 0.2 * violation.confidence_score
            elif violation.risk_level == ContentRiskLevel.LOW_RISK:
                base_score -= 0.1 * violation.confidence_score
        
        # Adjust for sentiment
        sentiment_score = sentiment_analysis.get("sentiment_score", 0.0)
        if sentiment_score < -0.5:
            base_score -= 0.1 * abs(sentiment_score)
        
        # Ensure score is within bounds
        return max(0.0, min(1.0, base_score))
    
    def _determine_risk_level(self, safety_score: float) -> ContentRiskLevel:
        """Determine risk level from safety score"""
        if safety_score >= 0.8:
            return ContentRiskLevel.SAFE
        elif safety_score >= 0.6:
            return ContentRiskLevel.LOW_RISK
        elif safety_score >= 0.4:
            return ContentRiskLevel.MODERATE_RISK
        elif safety_score >= 0.2:
            return ContentRiskLevel.HIGH_RISK
        else:
            return ContentRiskLevel.HARMFUL
    
    def _generate_safety_recommendations(self, result: ContentSafetyResult) -> List[str]:
        """
Generate safety compliance recommendations"""
        recommendations = []
        
        if result.violations:
            recommendations.append("Review and moderate flagged content")
            
            # Category-specific recommendations
            categories = set(v.category for v in result.violations)
            
            if ContentCategory.TOXICITY in categories:
                recommendations.append("Implement toxicity filtering")
            
            if ContentCategory.HARASSMENT in categories:
                recommendations.append("Add harassment prevention measures")
            
            if ContentCategory.HATE_SPEECH in categories:
                recommendations.append("Remove hate speech content")
            
            if ContentCategory.SELF_HARM in categories:
                recommendations.append("Provide mental health resources")
        
        if result.age_rating in [AgeRating.MATURE, AgeRating.ADULT_ONLY]:
            recommendations.append("Implement age verification")
        
        if result.brand_safety_level in [BrandSafetyLevel.HIGH_RISK, BrandSafetyLevel.BRAND_UNSAFE]:
            recommendations.append("Review content for brand safety compliance")
        
        if result.moderation_required:
            recommendations.append("Queue for human moderation review")
        
        return recommendations
    
    def _apply_content_moderation(self, violations: List[ContentViolation]) -> List[ContentModerationAction]:
        """Apply automated content moderation"""
        actions = []
        
        for violation in violations:
            if violation.auto_actionable:
                # Apply content filtering/replacement
                for segment_start, segment_end in violation.affected_segments:
                    action = ContentModerationAction(
                        action_type="filter",
                        content_segment=f"Position {segment_start}-{segment_end}",
                        replacement_text="[FILTERED]",
                        warning_message=f"Content filtered due to {violation.category.value}",
                        justification=violation.description,
                        automated=True,
                        human_review_required=violation.risk_level == ContentRiskLevel.HARMFUL
                    )
                    actions.append(action)
        
        return actions
    
    def _calculate_confidence_score(self, violations: List[ContentViolation]) -> float:
        """Calculate confidence score for safety assessment"""
        if not violations:
            return 1.0
        
        total_confidence = sum(v.confidence_score for v in violations)
        return total_confidence / len(violations)
    
    def _get_category_actions(self, category: ContentCategory) -> List[str]:
        """
Get recommended actions for violation category"""
        actions = {
            ContentCategory.TOXICITY: [
                "Filter toxic content",
                "Warn user about toxic language",
                "Provide alternative phrasing suggestions"
            ],
            ContentCategory.HARASSMENT: [
                "Remove harassing content",
                "Block user if repeated violations",
                "Report to authorities if necessary"
            ],
            ContentCategory.HATE_SPEECH: [
                "Remove hate speech content",
                "Educate user on community guidelines",
                "Escalate to human moderators"
            ],
            ContentCategory.SELF_HARM: [
                "Remove harmful content",
                "Provide mental health resources",
                "Alert crisis intervention services"
            ],
            ContentCategory.ILLEGAL_ACTIVITY: [
                "Remove illegal content",
                "Report to authorities",
                "Suspend user account"
            ]
        }
        
        return actions.get(category, ["Review content for compliance"])
    
    async def _store_safety_assessment(
        self,
        result: ContentSafetyResult,
        user_input: str,
        ai_response: str
    ) -> None:
        """Store content safety assessment results"""
        try:
            query = """
                INSERT INTO content_safety_assessments 
                (safety_score, risk_level, age_rating, brand_safety_level,
                 violations_count, moderation_required, processing_time_ms, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """
            
            await self.db_manager.execute(
                query,
                result.overall_safety_score,
                result.risk_level.value,
                result.age_rating.value,
                result.brand_safety_level.value,
                len(result.violations),
                result.moderation_required,
                result.processing_time_ms,
                datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error storing safety assessment: {str(e)}")
    
    async def update_safety_thresholds(
        self,
        category: ContentCategory,
        new_thresholds: Dict[str, float]
    ) -> None:
        """Update safety thresholds for specific category"""
        self.safety_thresholds[category] = new_thresholds
        await self.cache_manager.clear_pattern("content_safety_*")
        self.logger.info(f"Safety thresholds updated for {category.value}")
    
    async def add_content_pattern(
        self,
        category: ContentCategory,
        pattern_config: Dict[str, Any]
    ) -> None:
        """Add new content detection pattern"""
        if category not in self.content_patterns:
            self.content_patterns[category] = []
        
        self.content_patterns[category].append(pattern_config)
        await self.cache_manager.clear_pattern("content_safety_*")
        self.logger.info(f"Content pattern added for {category.value}")
    
    async def get_safety_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get content safety statistics"""
        try:
            # Overall safety metrics
            safety_query = """
                SELECT 
                    risk_level,
                    age_rating,
                    brand_safety_level,
                    COUNT(*) as count,
                    AVG(safety_score) as avg_safety_score,
                    AVG(violations_count) as avg_violations
                FROM content_safety_assessments 
                WHERE created_at >= $1
                GROUP BY risk_level, age_rating, brand_safety_level
            """
            
            safety_stats = await self.db_manager.fetch_all(
                safety_query,
                datetime.now() - timedelta(days=days)
            )
            
            # Moderation metrics
            moderation_query = """
                SELECT 
                    moderation_required,
                    COUNT(*) as count
                FROM content_safety_assessments 
                WHERE created_at >= $1
                GROUP BY moderation_required
            """
            
            moderation_stats = await self.db_manager.fetch_all(
                moderation_query,
                datetime.now() - timedelta(days=days)
            )
            
            return {
                "period_days": days,
                "safety_distribution": {
                    f"{stat['risk_level']}_{stat['age_rating']}_{stat['brand_safety_level']}": stat["count"] 
                    for stat in safety_stats
                },
                "average_safety_score": sum(stat["avg_safety_score"] or 0 for stat in safety_stats),
                "average_violations_per_assessment": sum(stat["avg_violations"] or 0 for stat in safety_stats),
                "moderation_distribution": {
                    stat["moderation_required"]: stat["count"] for stat in moderation_stats
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching safety statistics: {str(e)}")
            return {}
    
    def get_supported_categories(self) -> List[str]:
        """Get list of supported content categories"""
        return [category.value for category in ContentCategory]
    
    def get_category_thresholds(self, category: ContentCategory) -> Dict[str, float]:
        """
Get safety thresholds for specific category"""
        return self.safety_thresholds.get(category, {})
