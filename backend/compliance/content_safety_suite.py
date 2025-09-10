"""
Content Safety Suite - Consolidated Content Safety System

Comprehensive content safety system consolidating all content safety functionality
from content_safety/ subdirectory into unified enterprise-grade content protection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: All rights reserved - Proprietary software
"""

import asyncio
import hashlib
import json
import logging
import re
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from uuid import uuid4, UUID

import aioredis
import numpy as np
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Float, Integer, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class ContentType(Enum):
    """Content type enumeration"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    LINK = "link"
    MIXED_MEDIA = "mixed_media"


class ThreatLevel(Enum):
    """Threat level classification"""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    CRITICAL = "critical"
    BLOCKED = "blocked"


class ViolationType(Enum):
    """Content violation types"""
    ADULT_CONTENT = "adult_content"
    HATE_SPEECH = "hate_speech"
    VIOLENCE = "violence"
    HARASSMENT = "harassment"
    CYBERBULLYING = "cyberbullying"
    SPAM = "spam"
    MISINFORMATION = "misinformation"
    SELF_HARM = "self_harm"
    TERRORISM = "terrorism"
    DRUG_CONTENT = "drug_content"
    COPYRIGHT = "copyright"
    PRIVACY_VIOLATION = "privacy_violation"


class ModerationAction(Enum):
    """Moderation action types"""
    APPROVE = "approve"
    FLAG = "flag"
    REVIEW = "review"
    REJECT = "reject"
    REMOVE = "remove"
    SHADOW_BAN = "shadow_ban"
    WARNING = "warning"
    ACCOUNT_RESTRICTION = "account_restriction"


@dataclass
class ContentAnalysisResult:
    """Content analysis result data structure"""
    content_id: str
    content_type: ContentType
    threat_level: ThreatLevel
    confidence_score: float
    violations: List[ViolationType]
    analysis_details: Dict[str, Any]
    recommended_action: ModerationAction
    human_review_required: bool
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)
    processed_by: str = "automated_system"


@dataclass
class SafetyMetrics:
    """Content safety metrics"""
    total_content_analyzed: int
    safe_content_count: int
    flagged_content_count: int
    blocked_content_count: int
    false_positive_rate: float
    false_negative_rate: float
    average_processing_time: float
    accuracy_score: float


class ContentAnalysisRecord(Base):
    """Database model for content analysis"""
    __tablename__ = "content_analysis"
    
    analysis_id = Column(String, primary_key=True)
    content_id = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    threat_level = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    violations = Column(JSON, default=[])
    analysis_details = Column(JSON, default={})
    recommended_action = Column(String, nullable=False)
    human_review_required = Column(Boolean, default=False)
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)
    processed_by = Column(String, default="automated_system")
    reviewed_by = Column(String)
    review_timestamp = Column(DateTime)
    final_action = Column(String)


class SafetyMetricsRecord(Base):
    """Database model for safety metrics"""
    __tablename__ = "safety_metrics"
    
    metric_id = Column(String, primary_key=True)
    date = Column(DateTime, nullable=False)
    total_content_analyzed = Column(Integer, default=0)
    safe_content_count = Column(Integer, default=0)
    flagged_content_count = Column(Integer, default=0)
    blocked_content_count = Column(Integer, default=0)
    false_positive_rate = Column(Float, default=0.0)
    false_negative_rate = Column(Float, default=0.0)
    average_processing_time = Column(Float, default=0.0)
    accuracy_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class AdultContentFilter:
    """Advanced adult content detection and filtering"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.nsfw_keywords = self._load_nsfw_keywords()
        self.adult_patterns = self._compile_adult_patterns()
        
    async def analyze_content(self, content: str, content_type: ContentType = ContentType.TEXT) -> ContentAnalysisResult:
        """Analyze content for adult/NSFW material"""
        try:
            analysis_id = str(uuid4())
            
            if content_type == ContentType.TEXT:
                result = await self._analyze_text_content(content)
            elif content_type == ContentType.IMAGE:
                result = await self._analyze_image_content(content)
            elif content_type == ContentType.VIDEO:
                result = await self._analyze_video_content(content)
            else:
                result = await self._analyze_mixed_content(content)
            
            # Create analysis result
            analysis_result = ContentAnalysisResult(
                content_id=analysis_id,
                content_type=content_type,
                threat_level=result["threat_level"],
                confidence_score=result["confidence"],
                violations=result["violations"],
                analysis_details=result["details"],
                recommended_action=result["action"],
                human_review_required=result["requires_review"]
            )
            
            # Cache result
            await self.redis.setex(f"adult_content_analysis:{analysis_id}", 3600, 
                                 json.dumps(analysis_result.__dict__, default=str))
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Adult content analysis failed: {str(e)}")
            raise
    
    async def _analyze_text_content(self, text: str) -> Dict[str, Any]:
        """Analyze text content for adult material"""
        violations = []
        confidence = 0.0
        details = {"matched_keywords": [], "pattern_matches": []}
        
        # Keyword matching
        text_lower = text.lower()
        for keyword in self.nsfw_keywords:
            if keyword in text_lower:
                violations.append(ViolationType.ADULT_CONTENT)
                details["matched_keywords"].append(keyword)
                confidence += 0.1
        
        # Pattern matching
        for pattern_name, pattern in self.adult_patterns.items():
            matches = pattern.findall(text)
            if matches:
                violations.append(ViolationType.ADULT_CONTENT)
                details["pattern_matches"].append({"pattern": pattern_name, "matches": matches})
                confidence += 0.2
        
        # Determine threat level and action
        if confidence >= 0.8:
            threat_level = ThreatLevel.CRITICAL
            action = ModerationAction.REMOVE
            requires_review = False
        elif confidence >= 0.6:
            threat_level = ThreatLevel.HIGH_RISK
            action = ModerationAction.FLAG
            requires_review = True
        elif confidence >= 0.3:
            threat_level = ThreatLevel.MEDIUM_RISK
            action = ModerationAction.REVIEW
            requires_review = True
        else:
            threat_level = ThreatLevel.SAFE
            action = ModerationAction.APPROVE
            requires_review = False
        
        return {
            "threat_level": threat_level,
            "confidence": min(confidence, 1.0),
            "violations": list(set(violations)),
            "details": details,
            "action": action,
            "requires_review": requires_review
        }
    
    async def _analyze_image_content(self, image_data: str) -> Dict[str, Any]:
        """Analyze image content for adult material"""
        # Mock implementation - would use computer vision models
        return {
            "threat_level": ThreatLevel.SAFE,
            "confidence": 0.1,
            "violations": [],
            "details": {"image_analysis": "safe"},
            "action": ModerationAction.APPROVE,
            "requires_review": False
        }
    
    async def _analyze_video_content(self, video_data: str) -> Dict[str, Any]:
        """Analyze video content for adult material"""
        # Mock implementation - would analyze video frames and audio
        return {
            "threat_level": ThreatLevel.SAFE,
            "confidence": 0.1,
            "violations": [],
            "details": {"video_analysis": "safe"},
            "action": ModerationAction.APPROVE,
            "requires_review": False
        }
    
    async def _analyze_mixed_content(self, content: str) -> Dict[str, Any]:
        """Analyze mixed media content"""
        # Mock implementation - would analyze all content types
        return {
            "threat_level": ThreatLevel.SAFE,
            "confidence": 0.1,
            "violations": [],
            "details": {"mixed_analysis": "safe"},
            "action": ModerationAction.APPROVE,
            "requires_review": False
        }
    
    def _load_nsfw_keywords(self) -> List[str]:
        """Load NSFW keywords for detection"""
        return [
            "explicit", "nsfw", "adult", "xxx", "porn", "sexual", "nude", "naked"
            # Note: In production, this would be a comprehensive database
        ]
    
    def _compile_adult_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for adult content detection"""
        return {
            "explicit_urls": re.compile(r'https?://(?:www\.)?(?:pornhub|xvideos|redtube)\.com', re.IGNORECASE),
            "adult_references": re.compile(r'\b(?:sex|porn|xxx|adult)\s+(?:content|video|image)\b', re.IGNORECASE)
        }


class NSFWDetector:
    """NSFW (Not Safe For Work) content detection"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        
    async def detect_nsfw_content(self, content: str, content_type: ContentType) -> Dict[str, Any]:
        """Detect NSFW content using ML models"""
        try:
            # Mock ML model prediction
            nsfw_probability = await self._predict_nsfw_probability(content, content_type)
            
            # Determine classification
            if nsfw_probability >= 0.9:
                classification = "explicit"
                confidence = "high"
                action = ModerationAction.REMOVE
            elif nsfw_probability >= 0.7:
                classification = "suggestive"
                confidence = "medium"
                action = ModerationAction.FLAG
            elif nsfw_probability >= 0.3:
                classification = "questionable"
                confidence = "low"
                action = ModerationAction.REVIEW
            else:
                classification = "safe"
                confidence = "high"
                action = ModerationAction.APPROVE
            
            result = {
                "nsfw_probability": nsfw_probability,
                "classification": classification,
                "confidence": confidence,
                "recommended_action": action,
                "requires_human_review": nsfw_probability >= 0.3
            }
            
            return result
            
        except Exception as e:
            logger.error(f"NSFW detection failed: {str(e)}")
            raise
    
    async def _predict_nsfw_probability(self, content: str, content_type: ContentType) -> float:
        """Predict NSFW probability using ML model"""
        # Mock implementation - would use actual ML models
        if "nsfw" in content.lower() or "adult" in content.lower():
            return 0.8
        elif "explicit" in content.lower():
            return 0.9
        else:
            return 0.1


class ContentClassifier:
    """Multi-category content classification"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.classification_models = self._load_classification_models()
        
    async def classify_content(self, content: str, content_type: ContentType) -> Dict[str, Any]:
        """Classify content into multiple categories"""
        try:
            classifications = {}
            
            # Run multiple classifiers
            for category, model in self.classification_models.items():
                probability = await self._run_classifier(content, model)
                classifications[category] = {
                    "probability": probability,
                    "predicted": probability > 0.5
                }
            
            # Determine primary category
            primary_category = max(classifications.keys(), 
                                 key=lambda k: classifications[k]["probability"])
            
            result = {
                "primary_category": primary_category,
                "all_classifications": classifications,
                "content_type": content_type.value,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Content classification failed: {str(e)}")
            raise
    
    def _load_classification_models(self) -> Dict[str, Any]:
        """Load content classification models"""
        return {
            "educational": {"keywords": ["learn", "education", "tutorial", "guide"]},
            "entertainment": {"keywords": ["fun", "comedy", "music", "game"]},
            "news": {"keywords": ["news", "breaking", "report", "update"]},
            "promotional": {"keywords": ["buy", "sale", "discount", "offer"]},
            "personal": {"keywords": ["my", "personal", "diary", "experience"]}
        }
    
    async def _run_classifier(self, content: str, model: Dict[str, Any]) -> float:
        """Run individual classifier"""
        # Mock implementation - would use actual ML models
        keywords = model.get("keywords", [])
        content_lower = content.lower()
        
        matches = sum(1 for keyword in keywords if keyword in content_lower)
        probability = min(matches / len(keywords), 1.0) if keywords else 0.0
        
        return probability


class CategoryAnalyzer:
    """Advanced category analysis and tagging"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        
    async def analyze_categories(self, content: str) -> Dict[str, Any]:
        """Analyze content categories and generate tags"""
        try:
            # Extract topics and themes
            topics = await self._extract_topics(content)
            themes = await self._extract_themes(content)
            sentiment = await self._analyze_sentiment(content)
            
            # Generate tags
            tags = await self._generate_tags(content, topics, themes)
            
            # Calculate category confidence scores
            category_scores = await self._calculate_category_scores(content, topics, themes)
            
            analysis_result = {
                "topics": topics,
                "themes": themes,
                "sentiment": sentiment,
                "tags": tags,
                "category_scores": category_scores,
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Category analysis failed: {str(e)}")
            raise
    
    async def _extract_topics(self, content: str) -> List[str]:
        """Extract main topics from content"""
        # Mock implementation - would use NLP topic modeling
        topics = []
        content_lower = content.lower()
        
        topic_keywords = {
            "technology": ["tech", "software", "ai", "computer", "digital"],
            "health": ["health", "medical", "fitness", "wellness", "nutrition"],
            "business": ["business", "finance", "money", "investment", "startup"],
            "education": ["learn", "study", "education", "course", "training"],
            "entertainment": ["movie", "music", "game", "fun", "entertainment"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    async def _extract_themes(self, content: str) -> List[str]:
        """Extract themes from content"""
        # Mock implementation - would use advanced NLP
        return ["innovation", "growth", "community"]
    
    async def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze content sentiment"""
        # Mock implementation - would use sentiment analysis models
        positive_words = ["good", "great", "excellent", "amazing", "wonderful"]
        negative_words = ["bad", "terrible", "awful", "horrible", "disappointing"]
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            score = 0.7
        elif negative_count > positive_count:
            sentiment = "negative"
            score = -0.7
        else:
            sentiment = "neutral"
            score = 0.0
        
        return {
            "sentiment": sentiment,
            "score": score,
            "confidence": 0.8
        }
    
    async def _generate_tags(self, content: str, topics: List[str], themes: List[str]) -> List[str]:
        """Generate relevant tags for content"""
        tags = []
        tags.extend(topics)
        tags.extend(themes)
        
        # Add length-based tags
        word_count = len(content.split())
        if word_count < 50:
            tags.append("short-form")
        elif word_count > 500:
            tags.append("long-form")
        else:
            tags.append("medium-form")
        
        return list(set(tags))
    
    async def _calculate_category_scores(self, content: str, topics: List[str], themes: List[str]) -> Dict[str, float]:
        """Calculate confidence scores for different categories"""
        scores = {}
        
        # Calculate scores based on topics and themes
        all_categories = ["technology", "health", "business", "education", "entertainment", "lifestyle"]
        
        for category in all_categories:
            if category in topics:
                scores[category] = 0.8
            elif any(theme in category for theme in themes):
                scores[category] = 0.6
            else:
                scores[category] = 0.1
        
        return scores


class CyberbullyingDetector:
    """Advanced cyberbullying detection system"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.bullying_patterns = self._load_bullying_patterns()
        
    async def detect_cyberbullying(self, content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Detect cyberbullying behavior in content"""
        try:
            detection_result = {
                "is_cyberbullying": False,
                "confidence": 0.0,
                "bullying_types": [],
                "severity": "none",
                "indicators": [],
                "recommended_action": ModerationAction.APPROVE
            }
            
            # Analyze content for bullying indicators
            indicators = await self._analyze_bullying_indicators(content)
            detection_result["indicators"] = indicators
            
            # Calculate confidence score
            confidence = sum(indicator["weight"] for indicator in indicators)
            detection_result["confidence"] = min(confidence, 1.0)
            
            # Determine if cyberbullying
            if confidence >= 0.7:
                detection_result["is_cyberbullying"] = True
                detection_result["severity"] = "high"
                detection_result["recommended_action"] = ModerationAction.REMOVE
            elif confidence >= 0.5:
                detection_result["is_cyberbullying"] = True
                detection_result["severity"] = "medium"
                detection_result["recommended_action"] = ModerationAction.FLAG
            elif confidence >= 0.3:
                detection_result["severity"] = "low"
                detection_result["recommended_action"] = ModerationAction.REVIEW
            
            # Identify bullying types
            detection_result["bullying_types"] = await self._identify_bullying_types(indicators)
            
            return detection_result
            
        except Exception as e:
            logger.error(f"Cyberbullying detection failed: {str(e)}")
            raise
    
    async def _analyze_bullying_indicators(self, content: str) -> List[Dict[str, Any]]:
        """Analyze content for bullying indicators"""
        indicators = []
        content_lower = content.lower()
        
        # Check for aggressive language
        aggressive_words = ["stupid", "idiot", "loser", "pathetic", "worthless"]
        for word in aggressive_words:
            if word in content_lower:
                indicators.append({
                    "type": "aggressive_language",
                    "indicator": word,
                    "weight": 0.3
                })
        
        # Check for threatening language
        threats = ["kill", "hurt", "destroy", "ruin"]
        for threat in threats:
            if threat in content_lower:
                indicators.append({
                    "type": "threatening_language",
                    "indicator": threat,
                    "weight": 0.5
                })
        
        # Check for exclusionary language
        exclusion = ["nobody likes you", "go away", "not welcome"]
        for phrase in exclusion:
            if phrase in content_lower:
                indicators.append({
                    "type": "exclusionary_language",
                    "indicator": phrase,
                    "weight": 0.4
                })
        
        return indicators
    
    async def _identify_bullying_types(self, indicators: List[Dict[str, Any]]) -> List[str]:
        """Identify types of bullying based on indicators"""
        bullying_types = []
        
        indicator_types = [indicator["type"] for indicator in indicators]
        
        if "threatening_language" in indicator_types:
            bullying_types.append("threatening")
        if "aggressive_language" in indicator_types:
            bullying_types.append("verbal_abuse")
        if "exclusionary_language" in indicator_types:
            bullying_types.append("social_exclusion")
        
        return bullying_types
    
    def _load_bullying_patterns(self) -> Dict[str, List[str]]:
        """Load cyberbullying detection patterns"""
        return {
            "aggressive": ["stupid", "idiot", "loser", "pathetic"],
            "threatening": ["kill", "hurt", "destroy", "ruin"],
            "exclusionary": ["nobody likes you", "go away", "not welcome"]
        }


class HarassmentPredictor:
    """ML-based harassment prediction system"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        
    async def predict_harassment_risk(self, content: str, user_history: Dict[str, Any] = None) -> Dict[str, Any]:
        """Predict harassment risk using ML models"""
        try:
            # Analyze content features
            content_features = await self._extract_content_features(content)
            
            # Analyze user behavior features
            user_features = await self._extract_user_features(user_history or {})
            
            # Combine features for prediction
            combined_features = {**content_features, **user_features}
            
            # Predict harassment risk
            risk_score = await self._predict_risk_score(combined_features)
            
            prediction_result = {
                "harassment_risk_score": risk_score,
                "risk_level": await self._classify_risk_level(risk_score),
                "contributing_factors": await self._identify_risk_factors(combined_features),
                "confidence": 0.85,
                "predicted_at": datetime.utcnow().isoformat()
            }
            
            return prediction_result
            
        except Exception as e:
            logger.error(f"Harassment prediction failed: {str(e)}")
            raise
    
    async def _extract_content_features(self, content: str) -> Dict[str, Any]:
        """Extract features from content for harassment prediction"""
        features = {
            "content_length": len(content),
            "word_count": len(content.split()),
            "caps_ratio": sum(1 for c in content if c.isupper()) / len(content) if content else 0,
            "exclamation_count": content.count("!"),
            "question_count": content.count("?"),
            "negative_words": sum(1 for word in ["hate", "stupid", "ugly"] if word in content.lower())
        }
        
        return features
    
    async def _extract_user_features(self, user_history: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user behavior features"""
        features = {
            "previous_violations": user_history.get("violation_count", 0),
            "account_age_days": user_history.get("account_age_days", 0),
            "post_frequency": user_history.get("posts_per_day", 0),
            "report_ratio": user_history.get("reports_received", 0) / max(user_history.get("total_posts", 1), 1)
        }
        
        return features
    
    async def _predict_risk_score(self, features: Dict[str, Any]) -> float:
        """Predict harassment risk score using ML model"""
        # Mock implementation - would use actual ML model
        risk_factors = [
            features.get("negative_words", 0) * 0.3,
            features.get("caps_ratio", 0) * 0.2,
            features.get("previous_violations", 0) * 0.4,
            features.get("report_ratio", 0) * 0.1
        ]
        
        risk_score = sum(risk_factors)
        return min(risk_score, 1.0)
    
    async def _classify_risk_level(self, risk_score: float) -> str:
        """Classify risk level based on score"""
        if risk_score >= 0.8:
            return "very_high"
        elif risk_score >= 0.6:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        elif risk_score >= 0.2:
            return "low"
        else:
            return "very_low"
    
    async def _identify_risk_factors(self, features: Dict[str, Any]) -> List[str]:
        """Identify contributing risk factors"""
        risk_factors = []
        
        if features.get("negative_words", 0) > 3:
            risk_factors.append("high_negative_language")
        if features.get("caps_ratio", 0) > 0.3:
            risk_factors.append("excessive_caps")
        if features.get("previous_violations", 0) > 0:
            risk_factors.append("violation_history")
        if features.get("report_ratio", 0) > 0.1:
            risk_factors.append("high_report_ratio")
        
        return risk_factors


class DrugContentDetector:
    """Drug and substance abuse content detection"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.drug_keywords = self._load_drug_keywords()
        
    async def detect_drug_content(self, content: str) -> Dict[str, Any]:
        """Detect drug-related content"""
        try:
            detection_result = {
                "contains_drug_content": False,
                "confidence": 0.0,
                "detected_substances": [],
                "content_category": "safe",
                "recommended_action": ModerationAction.APPROVE
            }
            
            content_lower = content.lower()
            detected_substances = []
            confidence = 0.0
            
            # Check for drug keywords
            for category, keywords in self.drug_keywords.items():
                for keyword in keywords:
                    if keyword in content_lower:
                        detected_substances.append({
                            "substance": keyword,
                            "category": category,
                            "context": self._extract_context(content, keyword)
                        })
                        confidence += 0.2
            
            if detected_substances:
                detection_result["contains_drug_content"] = True
                detection_result["detected_substances"] = detected_substances
                detection_result["confidence"] = min(confidence, 1.0)
                
                # Determine content category and action
                if confidence >= 0.8:
                    detection_result["content_category"] = "promotion"
                    detection_result["recommended_action"] = ModerationAction.REMOVE
                elif confidence >= 0.5:
                    detection_result["content_category"] = "reference"
                    detection_result["recommended_action"] = ModerationAction.FLAG
                else:
                    detection_result["content_category"] = "mention"
                    detection_result["recommended_action"] = ModerationAction.REVIEW
            
            return detection_result
            
        except Exception as e:
            logger.error(f"Drug content detection failed: {str(e)}")
            raise
    
    def _load_drug_keywords(self) -> Dict[str, List[str]]:
        """Load drug-related keywords by category"""
        return {
            "illegal_drugs": ["cocaine", "heroin", "marijuana", "meth", "lsd"],
            "prescription_abuse": ["oxycontin", "adderall", "xanax", "vicodin"],
            "alcohol": ["drunk", "wasted", "hammered", "blackout"],
            "drug_paraphernalia": ["bong", "pipe", "needle", "syringe"]
        }
    
    def _extract_context(self, content: str, keyword: str) -> str:
        """Extract context around detected keyword"""
        # Find keyword position and extract surrounding text
        keyword_pos = content.lower().find(keyword)
        if keyword_pos == -1:
            return ""
        
        start = max(0, keyword_pos - 50)
        end = min(len(content), keyword_pos + len(keyword) + 50)
        
        return content[start:end]


class SubstanceAnalyzer:
    """Advanced substance abuse content analysis"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        
    async def analyze_substance_content(self, content: str) -> Dict[str, Any]:
        """Comprehensive substance abuse content analysis"""
        try:
            analysis_result = {
                "substance_risk_score": 0.0,
                "intent_classification": "unknown",
                "harmful_potential": "low",
                "intervention_recommended": False,
                "support_resources": []
            }
            
            # Analyze intent
            intent = await self._classify_intent(content)
            analysis_result["intent_classification"] = intent
            
            # Calculate risk score
            risk_score = await self._calculate_substance_risk(content, intent)
            analysis_result["substance_risk_score"] = risk_score
            
            # Determine harmful potential
            if risk_score >= 0.7:
                analysis_result["harmful_potential"] = "high"
                analysis_result["intervention_recommended"] = True
            elif risk_score >= 0.4:
                analysis_result["harmful_potential"] = "medium"
            
            # Provide support resources if needed
            if analysis_result["intervention_recommended"]:
                analysis_result["support_resources"] = await self._get_support_resources()
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Substance analysis failed: {str(e)}")
            raise
    
    async def _classify_intent(self, content: str) -> str:
        """Classify intent of substance-related content"""
        content_lower = content.lower()
        
        # Check for different intent patterns
        if any(word in content_lower for word in ["selling", "buy", "deal", "supply"]):
            return "distribution"
        elif any(word in content_lower for word in ["how to", "instructions", "recipe"]):
            return "instructional"
        elif any(word in content_lower for word in ["party", "fun", "celebrate"]):
            return "recreational"
        elif any(word in content_lower for word in ["help", "quit", "recovery", "support"]):
            return "seeking_help"
        else:
            return "mention"
    
    async def _calculate_substance_risk(self, content: str, intent: str) -> float:
        """Calculate substance abuse risk score"""
        base_risk = {
            "distribution": 0.9,
            "instructional": 0.8,
            "recreational": 0.5,
            "seeking_help": 0.1,
            "mention": 0.2
        }
        
        risk = base_risk.get(intent, 0.3)
        
        # Adjust based on content severity
        content_lower = content.lower()
        if any(word in content_lower for word in ["overdose", "dangerous", "illegal"]):
            risk += 0.2
        
        return min(risk, 1.0)
    
    async def _get_support_resources(self) -> List[Dict[str, str]]:
        """Get substance abuse support resources"""
        return [
            {
                "name": "National Suicide Prevention Lifeline",
                "phone": "988",
                "description": "24/7 crisis support"
            },
            {
                "name": "SAMHSA National Helpline",
                "phone": "1-800-662-4357",
                "description": "Treatment referral service"
            }
        ]


class HateSpeechDetector:
    """Advanced hate speech detection system"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.hate_speech_models = self._load_hate_speech_models()
        
    async def detect_hate_speech(self, content: str) -> Dict[str, Any]:
        """Detect hate speech in content"""
        try:
            detection_result = {
                "contains_hate_speech": False,
                "confidence": 0.0,
                "hate_categories": [],
                "targeted_groups": [],
                "severity": "none",
                "recommended_action": ModerationAction.APPROVE
            }
            
            # Run multiple hate speech detection models
            model_results = []
            for model_name, model in self.hate_speech_models.items():
                result = await self._run_hate_speech_model(content, model)
                model_results.append(result)
            
            # Aggregate results
            avg_confidence = np.mean([r["confidence"] for r in model_results])
            detected_categories = list(set().union(*[r["categories"] for r in model_results]))
            
            detection_result["confidence"] = avg_confidence
            detection_result["hate_categories"] = detected_categories
            
            if avg_confidence >= 0.7:
                detection_result["contains_hate_speech"] = True
                detection_result["severity"] = "high"
                detection_result["recommended_action"] = ModerationAction.REMOVE
            elif avg_confidence >= 0.5:
                detection_result["contains_hate_speech"] = True
                detection_result["severity"] = "medium"
                detection_result["recommended_action"] = ModerationAction.FLAG
            elif avg_confidence >= 0.3:
                detection_result["severity"] = "low"
                detection_result["recommended_action"] = ModerationAction.REVIEW
            
            # Identify targeted groups
            detection_result["targeted_groups"] = await self._identify_targeted_groups(content)
            
            return detection_result
            
        except Exception as e:
            logger.error(f"Hate speech detection failed: {str(e)}")
            raise
    
    async def _run_hate_speech_model(self, content: str, model: Dict[str, Any]) -> Dict[str, Any]:
        """Run individual hate speech detection model"""
        # Mock implementation - would use actual ML models
        content_lower = content.lower()
        
        categories = []
        confidence = 0.0
        
        for category, keywords in model.get("keywords", {}).items():
            if any(keyword in content_lower for keyword in keywords):
                categories.append(category)
                confidence += 0.3
        
        return {
            "confidence": min(confidence, 1.0),
            "categories": categories
        }
    
    async def _identify_targeted_groups(self, content: str) -> List[str]:
        """Identify groups targeted by hate speech"""
        targeted_groups = []
        content_lower = content.lower()
        
        group_indicators = {
            "racial": ["race", "ethnicity", "color"],
            "religious": ["religion", "faith", "beliefs"],
            "gender": ["gender", "sex", "woman", "man"],
            "sexual_orientation": ["gay", "lesbian", "lgbt", "queer"],
            "disability": ["disabled", "handicapped", "impaired"],
            "nationality": ["country", "nation", "immigrant"]
        }
        
        for group, indicators in group_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                targeted_groups.append(group)
        
        return targeted_groups
    
    def _load_hate_speech_models(self) -> Dict[str, Any]:
        """Load hate speech detection models"""
        return {
            "racial_hate": {
                "keywords": {
                    "racial_slurs": ["racial_slur1", "racial_slur2"],  # Placeholder
                    "racial_stereotypes": ["stereotype1", "stereotype2"]
                }
            },
            "religious_hate": {
                "keywords": {
                    "religious_slurs": ["religious_slur1", "religious_slur2"],
                    "religious_stereotypes": ["stereotype1", "stereotype2"]
                }
            }
        }


class ToxicityAnalyzer:
    """Advanced toxicity analysis system"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        
    async def analyze_toxicity(self, content: str) -> Dict[str, Any]:
        """Analyze content toxicity using multiple metrics"""
        try:
            toxicity_analysis = {
                "overall_toxicity_score": 0.0,
                "toxicity_breakdown": {},
                "toxic_elements": [],
                "severity_level": "none",
                "recommended_intervention": "none"
            }
            
            # Analyze different toxicity dimensions
            dimensions = {
                "identity_attack": await self._analyze_identity_attack(content),
                "insult": await self._analyze_insults(content),
                "profanity": await self._analyze_profanity(content),
                "threat": await self._analyze_threats(content),
                "severe_toxicity": await self._analyze_severe_toxicity(content)
            }
            
            toxicity_analysis["toxicity_breakdown"] = dimensions
            
            # Calculate overall toxicity score
            overall_score = np.mean(list(dimensions.values()))
            toxicity_analysis["overall_toxicity_score"] = overall_score
            
            # Determine severity level
            if overall_score >= 0.8:
                toxicity_analysis["severity_level"] = "severe"
                toxicity_analysis["recommended_intervention"] = "immediate_removal"
            elif overall_score >= 0.6:
                toxicity_analysis["severity_level"] = "high"
                toxicity_analysis["recommended_intervention"] = "flag_for_review"
            elif overall_score >= 0.4:
                toxicity_analysis["severity_level"] = "moderate"
                toxicity_analysis["recommended_intervention"] = "warning"
            elif overall_score >= 0.2:
                toxicity_analysis["severity_level"] = "low"
                toxicity_analysis["recommended_intervention"] = "monitor"
            
            # Identify specific toxic elements
            toxicity_analysis["toxic_elements"] = await self._identify_toxic_elements(content, dimensions)
            
            return toxicity_analysis
            
        except Exception as e:
            logger.error(f"Toxicity analysis failed: {str(e)}")
            raise
    
    async def _analyze_identity_attack(self, content: str) -> float:
        """Analyze identity-based attacks"""
        # Mock implementation - would use specialized models
        identity_terms = ["identity_term1", "identity_term2"]  # Placeholder
        content_lower = content.lower()
        
        matches = sum(1 for term in identity_terms if term in content_lower)
        return min(matches * 0.3, 1.0)
    
    async def _analyze_insults(self, content: str) -> float:
        """Analyze insulting language"""
        insult_words = ["stupid", "idiot", "moron", "loser"]
        content_lower = content.lower()
        
        matches = sum(1 for word in insult_words if word in content_lower)
        return min(matches * 0.2, 1.0)
    
    async def _analyze_profanity(self, content: str) -> float:
        """Analyze profane language"""
        # Mock implementation - would use profanity detection
        profane_indicators = content.lower().count("*") + content.lower().count("#")
        return min(profane_indicators * 0.1, 1.0)
    
    async def _analyze_threats(self, content: str) -> float:
        """Analyze threatening language"""
        threat_words = ["kill", "hurt", "destroy", "attack"]
        content_lower = content.lower()
        
        matches = sum(1 for word in threat_words if word in content_lower)
        return min(matches * 0.4, 1.0)
    
    async def _analyze_severe_toxicity(self, content: str) -> float:
        """Analyze severe toxicity indicators"""
        severe_indicators = ["die", "suicide", "self-harm"]
        content_lower = content.lower()
        
        matches = sum(1 for indicator in severe_indicators if indicator in content_lower)
        return min(matches * 0.5, 1.0)
    
    async def _identify_toxic_elements(self, content: str, dimensions: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify specific toxic elements in content"""
        toxic_elements = []
        
        for dimension, score in dimensions.items():
            if score > 0.3:
                toxic_elements.append({
                    "type": dimension,
                    "score": score,
                    "evidence": f"Detected {dimension} with confidence {score:.2f}"
                })
        
        return toxic_elements


# Main Content Safety Orchestrator
class ContentSafetySuite:
    """Main content safety suite orchestrator"""
    
    def __init__(self, db_session: AsyncSession, redis_client: aioredis.Redis):
        self.db = db_session
        self.redis = redis_client
        
        # Initialize all safety components
        self.adult_content_filter = AdultContentFilter(redis_client)
        self.nsfw_detector = NSFWDetector(redis_client)
        self.content_classifier = ContentClassifier(redis_client)
        self.category_analyzer = CategoryAnalyzer(redis_client)
        self.cyberbullying_detector = CyberbullyingDetector(redis_client)
        self.harassment_predictor = HarassmentPredictor(redis_client)
        self.drug_content_detector = DrugContentDetector(redis_client)
        self.substance_analyzer = SubstanceAnalyzer(redis_client)
        self.hate_speech_detector = HateSpeechDetector(redis_client)
        self.toxicity_analyzer = ToxicityAnalyzer(redis_client)
        
    async def comprehensive_content_analysis(self, content: str, 
                                           content_type: ContentType = ContentType.TEXT,
                                           context: Dict[str, Any] = None) -> ContentAnalysisResult:
        """Perform comprehensive content safety analysis"""
        try:
            analysis_id = str(uuid4())
            
            # Run all safety analyses in parallel
            analysis_tasks = [
                self.adult_content_filter.analyze_content(content, content_type),
                self.nsfw_detector.detect_nsfw_content(content, content_type),
                self.cyberbullying_detector.detect_cyberbullying(content, context),
                self.drug_content_detector.detect_drug_content(content),
                self.hate_speech_detector.detect_hate_speech(content),
                self.toxicity_analyzer.analyze_toxicity(content)
            ]
            
            results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Aggregate results
            violations = []
            confidence_scores = []
            threat_level = ThreatLevel.SAFE
            recommended_action = ModerationAction.APPROVE
            
            # Process each analysis result
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Analysis task {i} failed: {str(result)}")
                    continue
                
                if isinstance(result, ContentAnalysisResult):
                    # Handle adult content filter result
                    violations.extend(result.violations)
                    confidence_scores.append(result.confidence_score)
                    if result.threat_level.value > threat_level.value:
                        threat_level = result.threat_level
                        recommended_action = result.recommended_action
                elif isinstance(result, dict):
                    # Handle other analysis results
                    confidence_scores.append(result.get("confidence", 0))
                    
                    # Check for violations in various result formats
                    if result.get("contains_hate_speech"):
                        violations.append(ViolationType.HATE_SPEECH)
                    if result.get("is_cyberbullying"):
                        violations.append(ViolationType.CYBERBULLYING)
                    if result.get("contains_drug_content"):
                        violations.append(ViolationType.DRUG_CONTENT)
            
            # Calculate overall confidence
            overall_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            
            # Determine final threat level and action
            if violations and overall_confidence > 0.7:
                threat_level = ThreatLevel.HIGH_RISK
                recommended_action = ModerationAction.FLAG
            elif violations and overall_confidence > 0.5:
                threat_level = ThreatLevel.MEDIUM_RISK
                recommended_action = ModerationAction.REVIEW
            
            # Create comprehensive analysis result
            comprehensive_result = ContentAnalysisResult(
                content_id=analysis_id,
                content_type=content_type,
                threat_level=threat_level,
                confidence_score=overall_confidence,
                violations=list(set(violations)),
                analysis_details={
                    "individual_analyses": results,
                    "context": context or {}
                },
                recommended_action=recommended_action,
                human_review_required=overall_confidence > 0.5 or len(violations) > 1
            )
            
            # Store analysis result
            await self._store_analysis_result(comprehensive_result)
            
            return comprehensive_result
            
        except Exception as e:
            logger.error(f"Comprehensive content analysis failed: {str(e)}")
            raise
    
    async def _store_analysis_result(self, result: ContentAnalysisResult) -> None:
        """Store content analysis result in database"""
        try:
            analysis_record = ContentAnalysisRecord(
                analysis_id=result.content_id,
                content_id=result.content_id,
                content_type=result.content_type.value,
                threat_level=result.threat_level.value,
                confidence_score=result.confidence_score,
                violations=[v.value for v in result.violations],
                analysis_details=result.analysis_details,
                recommended_action=result.recommended_action.value,
                human_review_required=result.human_review_required
            )
            
            self.db.add(analysis_record)
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to store analysis result: {str(e)}")


# Export main classes for content safety suite consolidation
__all__ = [
    "ContentSafetySuite",
    "AdultContentFilter",
    "NSFWDetector",
    "ContentClassifier",
    "CategoryAnalyzer",
    "CyberbullyingDetector",
    "HarassmentPredictor",
    "DrugContentDetector",
    "SubstanceAnalyzer",
    "HateSpeechDetector",
    "ToxicityAnalyzer",
    "ContentType",
    "ThreatLevel",
    "ViolationType",
    "ModerationAction",
    "ContentAnalysisResult",
    "SafetyMetrics"
]
