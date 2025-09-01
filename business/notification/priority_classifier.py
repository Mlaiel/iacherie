"""Priority Classifier - AI-Powered Notification Priority Classification Engine

Advanced AI-driven notification priority classification system for IA Influencer Agent.
Uses machine learning models to intelligently classify notification priority and urgency
based on content analysis, user behavior, business context, and real-time factors.

Key Features:
- Machine learning-based priority classification using neural networks
- Real-time urgency detection with contextual analysis
- Business rule integration with adaptive learning
- Multi-factor priority scoring with confidence metrics
- Dynamic priority adjustment based on feedback loops
- Advanced pattern recognition for notification optimization

Classification Factors:
- Content importance and business impact assessment
- User engagement history and behavioral patterns
- Temporal factors and business hours optimization
- Platform urgency indicators and competitive analysis
- Revenue opportunity scoring and monetization potential
- Collaboration opportunity matching and partnership scoring

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

LEGAL NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission from the author is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing and usage rights.
"""

from typing import Dict, List, Optional, Any, Tuple, Union
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np
import json
import pickle
from pathlib import Path

from .notification_models import NotificationRequest, NotificationMetrics
from .config import NotificationConfig
from .constants import PRIORITY_LEVELS, BUSINESS_RULES, URGENCY_FACTORS

logger = logging.getLogger(__name__)


class PriorityLevel(Enum):
    """
Enhanced priority levels for notification classification."""

    CRITICAL = "critical"          # System failures, security breaches, immediate threats
    URGENT = "urgent"              # Revenue opportunities, collaboration matches
    HIGH = "high"                  # Content protection alerts, performance issues
    MEDIUM = "medium"              # SEO recommendations, routine updates
    LOW = "low"                    # General notifications, periodic reports
    DEFERRED = "deferred"          # Non-time-sensitive information


class UrgencyContext(Enum):
    """Contextual urgency factors for enhanced classification."""

    REVENUE_IMPACT = "revenue_impact"          # Direct revenue implications
    LEGAL_COMPLIANCE = "legal_compliance"      # Legal or compliance requirements
    SECURITY_THREAT = "security_threat"        # Security-related notifications
    COLLABORATION = "collaboration"            # Partnership opportunities
    CONTENT_PROTECTION = "content_protection"  # Copyright infringement
    PERFORMANCE = "performance"                # System performance issues
    USER_ENGAGEMENT = "user_engagement"        # User interaction requirements
    MARKETING = "marketing"                    # Marketing and growth opportunities


@dataclass
class PriorityScore:
    """Priority classification result with confidence metrics."""
    level: PriorityLevel
    score: float                    # Normalized score 0.0-1.0
    confidence: float              # Classification confidence 0.0-1.0
    urgency_context: List[UrgencyContext]
    factors: Dict[str, float]      # Contributing factors and weights
    reasoning: str                 # Human-readable explanation
    processing_time: float         # Classification processing time
    timestamp: datetime


@dataclass
class ClassificationFeatures:
    """
Feature vector for priority classification."""
    content_importance: float      # Content business importance
    user_engagement_score: float   # User historical engagement
    temporal_urgency: float        # Time-sensitive factors
    business_impact: float         # Potential business impact
    revenue_potential: float       # Revenue opportunity score
    collaboration_score: float     # Partnership potential
    competition_urgency: float     # Competitive timing factors
    platform_priority: float      # Platform-specific importance
    historical_performance: float  # Historical notification success
    user_preferences: float        # User notification preferences


class MLPriorityModel:
    """
Machine learning model for priority classification."""
    
    def __init__(self, model_path: Optional[Path] = None):
        """
Initialize ML model for priority classification."""
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.feature_importance = {}
        self.is_trained = False
        
        # Model hyperparameters
        self.learning_rate = 0.001
        self.hidden_layers = [128, 64, 32]
        self.dropout_rate = 0.3
        self.batch_size = 32
        
        # Performance metrics
        self.accuracy_score = 0.0
        self.precision_score = 0.0
        self.recall_score = 0.0
        self.f1_score = 0.0
        
        if model_path and model_path.exists():
            self._load_model()
    
    def _load_model(self):
        """
Load pre-trained model from disk."""
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.feature_importance = model_data['feature_importance']
                self.is_trained = True
                
            logger.info(f"ML priority model loaded successfully from {self.model_path}")
            
        except Exception as e:
            logger.error(f"Failed to load ML priority model: {e}")
            self.is_trained = False
    
    def predict_priority(self, features: ClassificationFeatures) -> Tuple[PriorityLevel, float]:
        """Predict priority level using ML model."""
        try:
            if not self.is_trained:
                return self._fallback_classification(features)
            
            # Convert features to numpy array
            feature_vector = np.array([
                features.content_importance,
                features.user_engagement_score,
                features.temporal_urgency,
                features.business_impact,
                features.revenue_potential,
                features.collaboration_score,
                features.competition_urgency,
                features.platform_priority,
                features.historical_performance,
                features.user_preferences
            ]).reshape(1, -1)
            
            # Normalize features
            if self.scaler:
                feature_vector = self.scaler.transform(feature_vector)
            
            # Predict priority
            prediction = self.model.predict_proba(feature_vector)[0]
            priority_idx = np.argmax(prediction)
            confidence = float(prediction[priority_idx])
            
            # Map to priority level
            priority_levels = list(PriorityLevel)
            priority_level = priority_levels[priority_idx]
            
            return priority_level, confidence
            
        except Exception as e:
            logger.error(f"ML priority prediction failed: {e}")
            return self._fallback_classification(features)
    
    def _fallback_classification(self, features: ClassificationFeatures) -> Tuple[PriorityLevel, float]:
        """Fallback rule-based classification when ML model is unavailable."""
        # Calculate weighted score
        weights = {
            'content_importance': 0.2,
            'business_impact': 0.2,
            'revenue_potential': 0.15,
            'temporal_urgency': 0.15,
            'user_engagement_score': 0.1,
            'collaboration_score': 0.1,
            'competition_urgency': 0.05,
            'platform_priority': 0.03,
            'historical_performance': 0.01,
            'user_preferences': 0.01
        }
        
        score = sum(
            getattr(features, feature) * weight
            for feature, weight in weights.items()
        )
        
        # Map score to priority level
        if score >= 0.9:
            return PriorityLevel.CRITICAL, 0.95
        elif score >= 0.7:
            return PriorityLevel.URGENT, 0.85
        elif score >= 0.5:
            return PriorityLevel.HIGH, 0.75
        elif score >= 0.3:
            return PriorityLevel.MEDIUM, 0.65
        elif score >= 0.1:
            return PriorityLevel.LOW, 0.55
        else:
            return PriorityLevel.DEFERRED, 0.45


class PriorityClassifier:
    """
    AI-powered notification priority classification engine.
    
    Provides intelligent priority classification using machine learning models,
    business rule integration, temporal analysis, and user behavior patterns.
    """
    
    def __init__(self, config: NotificationConfig):
        """
Initialize priority classifier with configuration."""
        self.config = config
        self.business_rules = BUSINESS_RULES
        self.urgency_factors = URGENCY_FACTORS
        
        # Initialize ML model
        model_path = getattr(config, 'priority_model_path', None)
        self.ml_model = MLPriorityModel(model_path)
        
        # Classification cache
        self._classification_cache: Dict[str, PriorityScore] = {}
        self._cache_ttl = timedelta(minutes=15)
        
        # Performance metrics
        self.classification_stats = {
            "total_classifications": 0,
            "average_processing_time": 0.0,
            "accuracy_score": 0.0,
            "cache_hit_rate": 0.0,
            "ml_model_usage": 0.0
        }
        
        logger.info("Priority classifier initialized successfully")
    
    async def classify_priority(self, request: NotificationRequest) -> PriorityScore:
        """
        Classify notification priority using AI-powered analysis.
        
        Args:
            request: Notification request to classify
            
        Returns:
            PriorityScore with classification details
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            if cache_key in self._classification_cache:
                cached_result = self._classification_cache[cache_key]
                if self._is_cache_valid(cached_result):
                    self.classification_stats["cache_hit_rate"] += 1
                    return cached_result
            
            # Extract features for classification
            features = await self._extract_classification_features(request)
            
            # Get ML model prediction
            priority_level, ml_confidence = self.ml_model.predict_priority(features)
            
            # Apply business rules adjustment
            adjusted_priority, rule_confidence = self._apply_business_rules(
                request, priority_level, features
            )
            
            # Determine urgency context
            urgency_context = self._analyze_urgency_context(request, features)
            
            # Calculate final confidence score
            final_confidence = (ml_confidence * 0.7) + (rule_confidence * 0.3)
            
            # Generate reasoning explanation
            reasoning = self._generate_classification_reasoning(
                adjusted_priority, features, urgency_context
            )
            
            # Calculate processing time
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Create priority score result
            priority_score = PriorityScore(
                level=adjusted_priority,
                score=self._priority_to_score(adjusted_priority),
                confidence=final_confidence,
                urgency_context=urgency_context,
                factors=self._extract_factor_scores(features),
                reasoning=reasoning,
                processing_time=processing_time,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Cache result
            self._classification_cache[cache_key] = priority_score
            
            # Update statistics
            self._update_classification_stats(processing_time)
            
            logger.debug(
                f"Priority classified: {adjusted_priority.value} "
                f"(confidence: {final_confidence:.3f}, time: {processing_time:.3f}s)"
            )
            
            return priority_score
            
        except Exception as e:
            logger.error(f"Priority classification failed: {e}")
            
            # Fallback to default priority
            return PriorityScore(
                level=PriorityLevel.MEDIUM,
                score=0.5,
                confidence=0.3,
                urgency_context=[],
                factors={},
                reasoning="Fallback classification due to processing error",
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
                timestamp=datetime.now(timezone.utc)
            )
    
    async def _extract_classification_features(self, request: NotificationRequest) -> ClassificationFeatures:
        """Extract features from notification request for classification."""
        try:
            # Initialize features with defaults
            features = ClassificationFeatures(
                content_importance=0.5,
                user_engagement_score=0.5,
                temporal_urgency=0.5,
                business_impact=0.5,
                revenue_potential=0.5,
                collaboration_score=0.5,
                competition_urgency=0.5,
                platform_priority=0.5,
                historical_performance=0.5,
                user_preferences=0.5
            )
            
            # Extract content importance
            features.content_importance = self._analyze_content_importance(request)
            
            # Extract user engagement score
            features.user_engagement_score = await self._get_user_engagement_score(request.recipient_id)
            
            # Extract temporal urgency
            features.temporal_urgency = self._analyze_temporal_urgency(request)
            
            # Extract business impact
            features.business_impact = self._analyze_business_impact(request)
            
            # Extract revenue potential
            features.revenue_potential = self._analyze_revenue_potential(request)
            
            # Extract collaboration score
            features.collaboration_score = self._analyze_collaboration_potential(request)
            
            # Extract competition urgency
            features.competition_urgency = self._analyze_competition_urgency(request)
            
            # Extract platform priority
            features.platform_priority = self._analyze_platform_priority(request)
            
            # Extract historical performance
            features.historical_performance = await self._get_historical_performance(request)
            
            # Extract user preferences
            features.user_preferences = await self._get_user_preferences(request.recipient_id)
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            # Return default features
            return ClassificationFeatures(
                content_importance=0.5,
                user_engagement_score=0.5,
                temporal_urgency=0.5,
                business_impact=0.5,
                revenue_potential=0.5,
                collaboration_score=0.5,
                competition_urgency=0.5,
                platform_priority=0.5,
                historical_performance=0.5,
                user_preferences=0.5
            )
    
    def _analyze_content_importance(self, request: NotificationRequest) -> float:
        """Analyze content importance for priority classification."""
        try:
            importance_score = 0.5  # Base score
            
            # Check notification type importance
            type_weights = {
                "security_alert": 0.95,
                "content_protection": 0.9,
                "revenue_opportunity": 0.85,
                "collaboration_match": 0.8,
                "seo_alert": 0.7,
                "distribution_status": 0.6,
                "performance_update": 0.5,
                "general_notification": 0.3
            }
            
            notification_type = request.type
            if notification_type in type_weights:
                importance_score = type_weights[notification_type]
            
            # Adjust based on content keywords
            high_importance_keywords = [
                "urgent", "critical", "immediate", "security", "breach",
                "copyright", "infringement", "revenue", "opportunity",
                "collaboration", "partnership", "trending", "viral"
            ]
            
            content_text = request.content.message.lower()
            keyword_matches = sum(1 for keyword in high_importance_keywords if keyword in content_text)
            keyword_boost = min(0.2, keyword_matches * 0.05)
            
            importance_score = min(1.0, importance_score + keyword_boost)
            
            return importance_score
            
        except Exception as e:
            logger.error(f"Content importance analysis failed: {e}")
            return 0.5
    
    async def _get_user_engagement_score(self, user_id: str) -> float:
        """Get user engagement score for priority adjustment."""
        try:
            # Simulate user engagement analysis
            # In production, this would query user analytics data
            
            # Default engagement score
            engagement_score = 0.5
            
            # Factors that could influence engagement:
            # - Historical notification interaction rate
            # - Recent platform activity
            # - Content creation frequency
            # - Collaboration participation
            # - Revenue generation patterns
            
            # Mock engagement calculation
            # This would be replaced with actual analytics queries
            base_score = 0.5
            activity_boost = 0.0  # Based on recent activity
            interaction_boost = 0.0  # Based on notification interactions
            
            engagement_score = min(1.0, base_score + activity_boost + interaction_boost)
            
            return engagement_score
            
        except Exception as e:
            logger.error(f"User engagement score calculation failed: {e}")
            return 0.5
    
    def _analyze_temporal_urgency(self, request: NotificationRequest) -> float:
        """Analyze temporal urgency factors."""
        try:
            urgency_score = 0.5  # Base score
            current_time = datetime.now(timezone.utc)
            
            # Time-sensitive factor analysis
            if hasattr(request, 'deadline') and request.deadline:
                time_to_deadline = (request.deadline - current_time).total_seconds()
                
                if time_to_deadline <= 3600:  # 1 hour
                    urgency_score = 0.95
                elif time_to_deadline <= 21600:  # 6 hours
                    urgency_score = 0.8
                elif time_to_deadline <= 86400:  # 24 hours
                    urgency_score = 0.7
                elif time_to_deadline <= 259200:  # 3 days
                    urgency_score = 0.6
                else:
                    urgency_score = 0.4
            
            # Business hours adjustment
            is_business_hours = self._is_business_hours(current_time)
            if not is_business_hours:
                urgency_score *= 0.8  # Reduce urgency outside business hours
            
            # Weekend adjustment
            is_weekend = current_time.weekday() >= 5
            if is_weekend:
                urgency_score *= 0.7  # Reduce urgency on weekends
            
            return min(1.0, urgency_score)
            
        except Exception as e:
            logger.error(f"Temporal urgency analysis failed: {e}")
            return 0.5
    
    def _analyze_business_impact(self, request: NotificationRequest) -> float:
        """Analyze potential business impact."""
        try:
            impact_score = 0.5  # Base score
            
            # Business impact keywords and weights
            impact_keywords = {
                "revenue": 0.9,
                "income": 0.85,
                "profit": 0.8,
                "loss": 0.9,
                "copyright": 0.85,
                "infringement": 0.9,
                "legal": 0.8,
                "compliance": 0.75,
                "partnership": 0.7,
                "collaboration": 0.65,
                "opportunity": 0.6,
                "growth": 0.55,
                "marketing": 0.5,
                "brand": 0.45
            }
            
            content_text = request.content.message.lower()
            
            # Find highest impact keyword
            max_impact = 0.0
            for keyword, impact in impact_keywords.items():
                if keyword in content_text:
                    max_impact = max(max_impact, impact)
            
            if max_impact > 0:
                impact_score = max_impact
            
            # Additional business context analysis
            if hasattr(request, 'metadata') and request.metadata:
                # Check for revenue amounts
                if 'revenue_amount' in request.metadata:
                    try:
                        revenue = float(request.metadata['revenue_amount'])
                        if revenue > 10000:  # High revenue impact
                            impact_score = min(1.0, impact_score + 0.2)
                        elif revenue > 1000:  # Medium revenue impact
                            impact_score = min(1.0, impact_score + 0.1)
                    except (ValueError, TypeError):
                        pass
                
                # Check for legal implications
                if request.metadata.get('legal_implications', False):
                    impact_score = min(1.0, impact_score + 0.15)
            
            return impact_score
            
        except Exception as e:
            logger.error(f"Business impact analysis failed: {e}")
            return 0.5
    
    def _analyze_revenue_potential(self, request: NotificationRequest) -> float:
        """Analyze revenue opportunity potential."""
        try:
            revenue_score = 0.0  # Default no revenue potential
            
            # Revenue-related notification types
            revenue_types = {
                "monetization_opportunity": 0.9,
                "revenue_alert": 0.85,
                "partnership_offer": 0.8,
                "collaboration_match": 0.75,
                "licensing_request": 0.7,
                "brand_deal": 0.85,
                "sponsorship": 0.8
            }
            
            if request.type in revenue_types:
                revenue_score = revenue_types[request.type]
            
            # Revenue keywords analysis
            revenue_keywords = [
                "monetize", "revenue", "income", "profit", "earn",
                "payment", "sponsor", "brand deal", "licensing",
                "royalty", "commission", "partnership"
            ]
            
            content_text = request.content.message.lower()
            keyword_matches = sum(1 for keyword in revenue_keywords if keyword in content_text)
            
            if keyword_matches > 0:
                revenue_score = max(revenue_score, 0.6 + (keyword_matches * 0.1))
            
            # Check metadata for revenue indicators
            if hasattr(request, 'metadata') and request.metadata:
                if 'estimated_revenue' in request.metadata:
                    try:
                        estimated = float(request.metadata['estimated_revenue'])
                        if estimated > 5000:
                            revenue_score = min(1.0, revenue_score + 0.3)
                        elif estimated > 1000:
                            revenue_score = min(1.0, revenue_score + 0.2)
                        elif estimated > 100:
                            revenue_score = min(1.0, revenue_score + 0.1)
                    except (ValueError, TypeError):
                        pass
            
            return min(1.0, revenue_score)
            
        except Exception as e:
            logger.error(f"Revenue potential analysis failed: {e}")
            return 0.0
    
    def _analyze_collaboration_potential(self, request: NotificationRequest) -> float:
        """Analyze collaboration opportunity potential."""
        try:
            collab_score = 0.0  # Default no collaboration potential
            
            # Collaboration notification types
            collab_types = {
                "collaboration_match": 0.9,
                "partnership_opportunity": 0.85,
                "network_invitation": 0.7,
                "joint_project": 0.8,
                "cross_promotion": 0.75,
                "feature_request": 0.65,
                "remix_opportunity": 0.6
            }
            
            if request.type in collab_types:
                collab_score = collab_types[request.type]
            
            # Collaboration keywords
            collab_keywords = [
                "collaborate", "partnership", "together", "joint",
                "feature", "remix", "cross-promote", "network",
                "connect", "work together", "team up"
            ]
            
            content_text = request.content.message.lower()
            keyword_matches = sum(1 for keyword in collab_keywords if keyword in content_text)
            
            if keyword_matches > 0:
                collab_score = max(collab_score, 0.5 + (keyword_matches * 0.1))
            
            return min(1.0, collab_score)
            
        except Exception as e:
            logger.error(f"Collaboration potential analysis failed: {e}")
            return 0.0
    
    def _analyze_competition_urgency(self, request: NotificationRequest) -> float:
        """Analyze competitive timing urgency."""
        try:
            competition_score = 0.5  # Base score
            
            # Competition-related keywords
            competition_keywords = [
                "trending", "viral", "competitor", "market share",
                "first to market", "limited time", "exclusive",
                "before others", "time-sensitive", "deadline"
            ]
            
            content_text = request.content.message.lower()
            keyword_matches = sum(1 for keyword in competition_keywords if keyword in content_text)
            
            if keyword_matches > 0:
                competition_score = min(1.0, 0.6 + (keyword_matches * 0.1))
            
            # Check for trending content indicators
            if hasattr(request, 'metadata') and request.metadata:
                if request.metadata.get('trending_score', 0) > 0.7:
                    competition_score = min(1.0, competition_score + 0.2)
                
                if request.metadata.get('viral_potential', False):
                    competition_score = min(1.0, competition_score + 0.15)
            
            return competition_score
            
        except Exception as e:
            logger.error(f"Competition urgency analysis failed: {e}")
            return 0.5
    
    def _analyze_platform_priority(self, request: NotificationRequest) -> float:
        """Analyze platform-specific priority."""
        try:
            # Platform priority weights
            platform_weights = {
                "youtube": 0.9,      # High revenue potential
                "spotify": 0.85,     # Music-focused platform
                "instagram": 0.8,    # High engagement
                "tiktok": 0.85,      # Viral potential
                "twitter": 0.7,      # Real-time engagement
                "facebook": 0.6,     # Broad reach
                "linkedin": 0.5,     # Professional network
                "website": 0.4,      # Owned media
                "email": 0.3         # Direct communication
            }
            
            # Get platform from metadata or content
            platform = "unknown"
            if hasattr(request, 'metadata') and request.metadata:
                platform = request.metadata.get('platform', 'unknown').lower()
            
            # Check content for platform mentions
            if platform == "unknown":
                content_text = request.content.message.lower()
                for platform_name in platform_weights.keys():
                    if platform_name in content_text:
                        platform = platform_name
                        break
            
            return platform_weights.get(platform, 0.5)
            
        except Exception as e:
            logger.error(f"Platform priority analysis failed: {e}")
            return 0.5
    
    async def _get_historical_performance(self, request: NotificationRequest) -> float:
        """Get historical performance for similar notifications."""
        try:
            # This would query historical notification performance data
            # For now, return a mock score based on notification type
            
            performance_scores = {
                "security_alert": 0.95,
                "content_protection": 0.9,
                "revenue_opportunity": 0.85,
                "collaboration_match": 0.8,
                "seo_alert": 0.7,
                "distribution_status": 0.6,
                "performance_update": 0.5,
                "general_notification": 0.4
            }
            
            return performance_scores.get(request.type, 0.5)
            
        except Exception as e:
            logger.error(f"Historical performance lookup failed: {e}")
            return 0.5
    
    async def _get_user_preferences(self, user_id: str) -> float:
        """Get user notification preferences for priority adjustment."""
        try:
            # This would query user preference data
            # For now, return default preference score
            return 0.5
            
        except Exception as e:
            logger.error(f"User preferences lookup failed: {e}")
            return 0.5
    
    def _apply_business_rules(
        self,
        request: NotificationRequest,
        ml_priority: PriorityLevel,
        features: ClassificationFeatures
    ) -> Tuple[PriorityLevel, float]:
        """Apply business rules to adjust ML classification."""
        try:
            adjusted_priority = ml_priority
            rule_confidence = 0.8
            
            # Critical business rules (override ML classification)
            if self._is_security_critical(request):
                adjusted_priority = PriorityLevel.CRITICAL
                rule_confidence = 0.95
            
            elif self._is_legal_urgent(request):
                adjusted_priority = PriorityLevel.URGENT
                rule_confidence = 0.9
            
            elif self._is_revenue_critical(request, features):
                if adjusted_priority.value in ["low", "deferred"]:
                    adjusted_priority = PriorityLevel.HIGH
                    rule_confidence = 0.85
            
            # Time-sensitive adjustments
            elif self._is_time_critical(request):
                if adjusted_priority.value in ["low", "medium"]:
                    adjusted_priority = PriorityLevel.HIGH
                    rule_confidence = 0.8
            
            # Business hours adjustments
            if not self._is_business_hours(datetime.now(timezone.utc)):
                if adjusted_priority == PriorityLevel.MEDIUM:
                    adjusted_priority = PriorityLevel.LOW
                    rule_confidence = 0.7
            
            return adjusted_priority, rule_confidence
            
        except Exception as e:
            logger.error(f"Business rules application failed: {e}")
            return ml_priority, 0.5
    
    def _is_security_critical(self, request: NotificationRequest) -> bool:
        """Check if notification is security critical."""
        security_keywords = [
            "security breach", "hack", "unauthorized access", "data leak",
            "suspicious activity", "malware", "phishing", "fraud"
        ]
        
        content_text = request.content.message.lower()
        return any(keyword in content_text for keyword in security_keywords)
    
    def _is_legal_urgent(self, request: NotificationRequest) -> bool:
        """Check if notification is legally urgent."""
        legal_keywords = [
            "copyright infringement", "dmca", "takedown", "cease and desist",
            "legal action", "lawsuit", "compliance violation", "intellectual property"
        ]
        
        content_text = request.content.message.lower()
        return any(keyword in content_text for keyword in legal_keywords)
    
    def _is_revenue_critical(self, request: NotificationRequest, features: ClassificationFeatures) -> bool:
        """Check if notification is revenue critical."""
        return (
            features.revenue_potential > 0.8 or
            request.type in ["revenue_opportunity", "monetization_alert", "partnership_offer"]
        )
    
    def _is_time_critical(self, request: NotificationRequest) -> bool:
        """Check if notification is time critical."""
        if hasattr(request, 'deadline') and request.deadline:
            time_to_deadline = (request.deadline - datetime.now(timezone.utc)).total_seconds()
            return time_to_deadline <= 3600  # 1 hour
        
        time_keywords = ["urgent", "immediate", "asap", "deadline", "expires"]
        content_text = request.content.message.lower()
        return any(keyword in content_text for keyword in time_keywords)
    
    def _is_business_hours(self, timestamp: datetime) -> bool:
        """Check if timestamp falls within business hours."""
        # Assume business hours: Monday-Friday, 9 AM - 6 PM UTC
        return (
            timestamp.weekday() < 5 and
            9 <= timestamp.hour < 18
        )
    
    def _analyze_urgency_context(
        self,
        request: NotificationRequest,
        features: ClassificationFeatures
    ) -> List[UrgencyContext]:
        """
Analyze urgency context factors."""
        contexts = []
        
        # Revenue impact
        if features.revenue_potential > 0.7:
            contexts.append(UrgencyContext.REVENUE_IMPACT)
        
        # Security threat
        if self._is_security_critical(request):
            contexts.append(UrgencyContext.SECURITY_THREAT)
        
        # Legal compliance
        if self._is_legal_urgent(request):
            contexts.append(UrgencyContext.LEGAL_COMPLIANCE)
        
        # Content protection
        if request.type == "content_protection":
            contexts.append(UrgencyContext.CONTENT_PROTECTION)
        
        # Collaboration opportunity
        if features.collaboration_score > 0.7:
            contexts.append(UrgencyContext.COLLABORATION)
        
        # Performance issues
        if request.type in ["performance_alert", "system_error"]:
            contexts.append(UrgencyContext.PERFORMANCE)
        
        # User engagement
        if features.user_engagement_score > 0.8:
            contexts.append(UrgencyContext.USER_ENGAGEMENT)
        
        # Marketing opportunities
        if request.type in ["marketing_opportunity", "trend_alert"]:
            contexts.append(UrgencyContext.MARKETING)
        
        return contexts
    
    def _priority_to_score(self, priority: PriorityLevel) -> float:
        """Convert priority level to numerical score."""
        priority_scores = {
            PriorityLevel.CRITICAL: 1.0,
            PriorityLevel.URGENT: 0.8,
            PriorityLevel.HIGH: 0.6,
            PriorityLevel.MEDIUM: 0.4,
            PriorityLevel.LOW: 0.2,
            PriorityLevel.DEFERRED: 0.0
        }
        return priority_scores.get(priority, 0.4)
    
    def _extract_factor_scores(self, features: ClassificationFeatures) -> Dict[str, float]:
        """
Extract factor scores for transparency."""
        return {
            "content_importance": features.content_importance,
            "user_engagement": features.user_engagement_score,
            "temporal_urgency": features.temporal_urgency,
            "business_impact": features.business_impact,
            "revenue_potential": features.revenue_potential,
            "collaboration_score": features.collaboration_score,
            "competition_urgency": features.competition_urgency,
            "platform_priority": features.platform_priority,
            "historical_performance": features.historical_performance,
            "user_preferences": features.user_preferences
        }
    
    def _generate_classification_reasoning(
        self,
        priority: PriorityLevel,
        features: ClassificationFeatures,
        urgency_context: List[UrgencyContext]
    ) -> str:
        """Generate human-readable classification reasoning."""
        try:
            reasoning_parts = []
            
            # Priority explanation
            reasoning_parts.append(f"Classified as {priority.value} priority")
            
            # Top contributing factors
            factor_scores = self._extract_factor_scores(features)
            top_factors = sorted(factor_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            
            if top_factors:
                factor_names = [factor.replace('_', ' ').title() for factor, _ in top_factors]
                reasoning_parts.append(f"based on {', '.join(factor_names)}")
            
            # Urgency context
            if urgency_context:
                context_names = [ctx.value.replace('_', ' ').title() for ctx in urgency_context]
                reasoning_parts.append(f"with {', '.join(context_names)} context")
            
            return ". ".join(reasoning_parts) + "."
            
        except Exception as e:
            logger.error(f"Classification reasoning generation failed: {e}")
            return f"Classified as {priority.value} priority based on automated analysis."
    
    def _generate_cache_key(self, request: NotificationRequest) -> str:
        """Generate cache key for classification result."""
        try:
            key_components = [
                request.type,
                request.recipient_id,
                hash(request.content.message[:100])  # First 100 chars of message
            ]
            
            if hasattr(request, 'metadata') and request.metadata:
                # Include relevant metadata in cache key
                metadata_hash = hash(json.dumps(request.metadata, sort_keys=True))
                key_components.append(metadata_hash)
            
            return "_".join(str(component) for component in key_components)
            
        except Exception as e:
            logger.error(f"Cache key generation failed: {e}")
            return f"fallback_{hash(str(request))}"
    
    def _is_cache_valid(self, cached_result: PriorityScore) -> bool:
        """Check if cached classification result is still valid."""
        time_diff = datetime.now(timezone.utc) - cached_result.timestamp
        return time_diff <= self._cache_ttl
    
    def _update_classification_stats(self, processing_time: float):
        """
Update classification performance statistics."""
        self.classification_stats["total_classifications"] += 1
        
        # Update average processing time
        total_time = (
            self.classification_stats["average_processing_time"] * 
            (self.classification_stats["total_classifications"] - 1) + 
            processing_time
        )
        self.classification_stats["average_processing_time"] = (
            total_time / self.classification_stats["total_classifications"]
        )
    
    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification performance statistics."""
        return self.classification_stats.copy()
    
    def clear_cache(self):
        """
Clear classification cache."""
        self._classification_cache.clear()
        logger.info("Priority classification cache cleared")
