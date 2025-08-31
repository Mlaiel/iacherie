"""Advanced Personalization Engine - AI-Driven Content Personalization System

Enterprise-grade personalization engine providing intelligent content adaptation,
behavioral analysis, preference learning, and contextual optimization for IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE - INTELLECTUAL PROPERTY PROTECTION:
This code, concept, and intellectual property are the EXCLUSIVE PROPERTY of Fahed Mlaiel.

STRICTLY PROHIBITED WITHOUT EXPLICIT WRITTEN AUTHORIZATION:
- Copying, cloning, reproducing, or distributing this code
- Using concepts, methodologies, or approaches in other projects
- Commercial exploitation, monetization, or resale
- Reverse engineering, decompilation, or adaptation
- Creating derivative works based on this intellectual property

Contact for licensing inquiries: mlaiel@live.de

Violation of these terms will result in immediate legal action.
All usage is monitored, logged, and legally protected.

Team Specialties & Expertise:
- Lead AI Developer & Backend Senior Engineer: Fahed Mlaiel
- Machine Learning Engineer & Audio Processing Specialist
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
import pickle
from collections import defaultdict, Counter
import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
import openai
from langdetect import detect
import holidays

# Internal imports
from ...core.base import BaseComponent
from ...models.personalization_models import (
    UserProfile, PersonalizationContext, ContentTemplate,
    BehaviorAnalysis, PreferenceProfile, EngagementMetrics
)
from ...ai.nlp import NLPProcessor
from ...ai.recommendation import RecommendationEngine
from ...utils.caching import CacheManager
from ...monitoring.metrics import MetricsCollector
from ...security.privacy import PrivacyManager

logger = logging.getLogger(__name__)


class PersonalizationType(Enum):
    """Types of personalization strategies"""    DEMOGRAPHIC = "demographic"
    BEHAVIORAL = "behavioral"
    CONTEXTUAL = "contextual"
    COLLABORATIVE = "collaborative"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    REAL_TIME = "real_time"
    PREDICTIVE = "predictive"


class EngagementLevel(Enum):
    """User engagement level classification"""    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"
    INACTIVE = "inactive"


class ContentStyle(Enum):
    """Content style preferences"""    FORMAL = "formal"
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    HUMOROUS = "humorous"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    MINIMALIST = "minimalist"


@dataclass
class PersonalizationConfiguration:
    """Advanced personalization configuration"""    enable_demographic_targeting: bool = True
    enable_behavioral_analysis: bool = True
    enable_contextual_adaptation: bool = True
    enable_sentiment_analysis: bool = True
    enable_language_detection: bool = True
    enable_timezone_awareness: bool = True
    enable_device_optimization: bool = True
    enable_a_b_testing: bool = True
    enable_real_time_learning: bool = True
    enable_privacy_protection: bool = True
    max_personalization_factors: int = 50
    min_data_points_for_learning: int = 10
    cache_duration_minutes: int = 60
    model_update_frequency_hours: int = 24


@dataclass
class UserBehaviorData:
    """Comprehensive user behavior tracking data"""    user_id: str
    session_data: Dict[str, Any] = field(default_factory=dict)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    content_preferences: Dict[str, float] = field(default_factory=dict)
    engagement_patterns: Dict[str, Any] = field(default_factory=dict)
    channel_preferences: Dict[str, float] = field(default_factory=dict)
    temporal_patterns: Dict[str, Any] = field(default_factory=dict)
    device_preferences: Dict[str, Any] = field(default_factory=dict)
    demographic_data: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PersonalizationRequest:
    """Request for content personalization"""    user_id: str
    content_template: Dict[str, Any]
    context: Dict[str, Any]
    channel_id: str
    personalization_types: List[PersonalizationType]
    constraints: Dict[str, Any] = field(default_factory=dict)
    a_b_test_variant: Optional[str] = None
    urgency_level: float = 0.5
    business_context: Dict[str, Any] = field(default_factory=dict)


class BehaviorAnalyzer:
    """Advanced behavioral analysis and pattern recognition"""    
    def __init__(self, config: PersonalizationConfiguration):
        self.config = config
        self.behavior_models = {}
        self.pattern_detectors = {}
        self.engagement_classifier = None
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize machine learning models for behavior analysis"""        try:
            # Engagement level classifier
            self.engagement_classifier = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                random_state=42
            )
            
            # Pattern detection models
            self.pattern_detectors = {
                'temporal': KMeans(n_clusters=5, random_state=42),
                'content': KMeans(n_clusters=8, random_state=42),
                'channel': KMeans(n_clusters=4, random_state=42)
            }
            
            # Behavior prediction models
            self.behavior_models = {
                'next_action': RandomForestClassifier(n_estimators=50, random_state=42),
                'churn_prediction': GradientBoostingClassifier(n_estimators=100, random_state=42),
                'preference_evolution': RandomForestClassifier(n_estimators=75, random_state=42)
            }
            
        except Exception as e:
            logger.error(f"Error initializing behavior analysis models: {str(e)}")
            
    async def analyze_user_behavior(self, user_behavior_data: UserBehaviorData) -> Dict[str, Any]:
        """Perform comprehensive behavioral analysis"""        try:
            analysis_results = {
                'user_id': user_behavior_data.user_id,
                'engagement_level': await self._classify_engagement_level(user_behavior_data),
                'temporal_patterns': await self._analyze_temporal_patterns(user_behavior_data),
                'content_preferences': await self._analyze_content_preferences(user_behavior_data),
                'channel_preferences': await self._analyze_channel_preferences(user_behavior_data),
                'interaction_patterns': await self._analyze_interaction_patterns(user_behavior_data),
                'behavioral_clusters': await self._identify_behavioral_clusters(user_behavior_data),
                'prediction_insights': await self._generate_prediction_insights(user_behavior_data),
                'anomaly_detection': await self._detect_behavioral_anomalies(user_behavior_data),
                'personalization_opportunities': await self._identify_personalization_opportunities(user_behavior_data)
            }
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing user behavior: {str(e)}")
            return {}
            
    async def _classify_engagement_level(self, behavior_data: UserBehaviorData) -> Dict[str, Any]:
        """Classify user engagement level using ML"""        try:
            # Extract engagement features
            features = self._extract_engagement_features(behavior_data)
            
            if not features:
                return {'level': EngagementLevel.MEDIUM, 'confidence': 0.5}
                
            # Use trained model or rule-based fallback
            if hasattr(self.engagement_classifier, 'predict_proba'):
                try:
                    feature_array = np.array([features])
                    probabilities = self.engagement_classifier.predict_proba(feature_array)[0]
                    level_index = np.argmax(probabilities)
                    confidence = probabilities[level_index]
                    
                    engagement_levels = list(EngagementLevel)
                    level = engagement_levels[level_index] if level_index < len(engagement_levels) else EngagementLevel.MEDIUM
                    
                    return {
                        'level': level,
                        'confidence': float(confidence),
                        'features': features
                    }
                except:
                    # Fallback to rule-based classification
                    pass
                    
            # Rule-based engagement classification
            return self._rule_based_engagement_classification(behavior_data)
            
        except Exception as e:
            logger.error(f"Error classifying engagement level: {str(e)}")
            return {'level': EngagementLevel.MEDIUM, 'confidence': 0.5}
            
    def _extract_engagement_features(self, behavior_data: UserBehaviorData) -> List[float]:
        """Extract numerical features for engagement classification"""        try:
            features = []
            
            # Interaction frequency features
            recent_interactions = [
                interaction for interaction in behavior_data.interaction_history
                if (datetime.utcnow() - datetime.fromisoformat(interaction.get('timestamp', '2025-01-01'))).days <= 7
            ]
            features.append(len(recent_interactions))  # Interactions per week
            
            # Session duration features
            session_durations = [
                session.get('duration', 0) for session in behavior_data.session_data.get('sessions', [])
            ]
            features.append(np.mean(session_durations) if session_durations else 0)
            
            # Content engagement features
            engagement_scores = list(behavior_data.engagement_patterns.get('content_scores', {}).values())
            features.append(np.mean(engagement_scores) if engagement_scores else 0.5)
            
            # Channel diversity
            features.append(len(behavior_data.channel_preferences))
            
            # Recency of last interaction
            if behavior_data.interaction_history:
                last_interaction = max(
                    behavior_data.interaction_history,
                    key=lambda x: x.get('timestamp', '2025-01-01')
                )
                days_since_last = (datetime.utcnow() - datetime.fromisoformat(
                    last_interaction.get('timestamp', '2025-01-01')
                )).days
                features.append(days_since_last)
            else:
                features.append(999)  # Very high recency score for inactive users
                
            return features
            
        except Exception as e:
            logger.error(f"Error extracting engagement features: {str(e)}")
            return []
            
    def _rule_based_engagement_classification(self, behavior_data: UserBehaviorData) -> Dict[str, Any]:
        """Rule-based engagement level classification"""        try:
            # Calculate engagement score based on multiple factors
            score = 0
            factors = []
            
            # Recent interaction frequency (40% weight)
            recent_interactions = len([
                i for i in behavior_data.interaction_history
                if (datetime.utcnow() - datetime.fromisoformat(i.get('timestamp', '2025-01-01'))).days <= 7
            ])
            
            if recent_interactions >= 10:
                score += 40
                factors.append("High interaction frequency")
            elif recent_interactions >= 5:
                score += 30
            elif recent_interactions >= 2:
                score += 20
            elif recent_interactions >= 1:
                score += 10
                
            # Content engagement quality (30% weight)
            engagement_scores = list(behavior_data.engagement_patterns.get('content_scores', {}).values())
            avg_engagement = np.mean(engagement_scores) if engagement_scores else 0.5
            
            if avg_engagement >= 0.8:
                score += 30
                factors.append("High content engagement")
            elif avg_engagement >= 0.6:
                score += 20
            elif avg_engagement >= 0.4:
                score += 10
                
            # Session quality (20% weight)
            sessions = behavior_data.session_data.get('sessions', [])
            if sessions:
                avg_duration = np.mean([s.get('duration', 0) for s in sessions])
                if avg_duration >= 300:  # 5+ minutes
                    score += 20
                    factors.append("Long session duration")
                elif avg_duration >= 120:  # 2+ minutes
                    score += 15
                elif avg_duration >= 60:  # 1+ minute
                    score += 10
                    
            # Channel diversity (10% weight)
            channel_count = len(behavior_data.channel_preferences)
            if channel_count >= 3:
                score += 10
                factors.append("Multi-channel engagement")
            elif channel_count >= 2:
                score += 5
                
            # Determine engagement level
            if score >= 80:
                level = EngagementLevel.VERY_HIGH
            elif score >= 60:
                level = EngagementLevel.HIGH
            elif score >= 40:
                level = EngagementLevel.MEDIUM
            elif score >= 20:
                level = EngagementLevel.LOW
            elif score >= 10:
                level = EngagementLevel.VERY_LOW
            else:
                level = EngagementLevel.INACTIVE
                
            return {
                'level': level,
                'confidence': min(score / 100, 1.0),
                'score': score,
                'factors': factors
            }
            
        except Exception as e:
            logger.error(f"Error in rule-based engagement classification: {str(e)}")
            return {'level': EngagementLevel.MEDIUM, 'confidence': 0.5}
            
    async def _analyze_temporal_patterns(self, behavior_data: UserBehaviorData) -> Dict[str, Any]:
        """Analyze temporal engagement patterns"""        try:
            if not behavior_data.interaction_history:
                return {'patterns': [], 'peak_hours': [], 'peak_days': []}
                
            # Extract temporal features
            timestamps = []
            for interaction in behavior_data.interaction_history:
                try:
                    timestamp = datetime.fromisoformat(interaction.get('timestamp', '2025-01-01'))
                    timestamps.append(timestamp)
                except:
                    continue
                    
            if not timestamps:
                return {'patterns': [], 'peak_hours': [], 'peak_days': []}
                
            # Analyze hourly patterns
            hourly_activity = defaultdict(int)
            daily_activity = defaultdict(int)
            
            for timestamp in timestamps:
                hourly_activity[timestamp.hour] += 1
                daily_activity[timestamp.strftime('%A')] += 1
                
            # Find peak hours and days
            peak_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)[:3]
            peak_days = sorted(daily_activity.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Identify patterns
            patterns = []
            
            # Morning person vs night owl
            morning_activity = sum(hourly_activity[h] for h in range(6, 12))
            evening_activity = sum(hourly_activity[h] for h in range(18, 24))
            
            if morning_activity > evening_activity * 1.5:
                patterns.append("morning_person")
            elif evening_activity > morning_activity * 1.5:
                patterns.append("night_owl")
                
            # Weekday vs weekend preference
            weekday_activity = sum(hourly_activity[h] for h in range(9, 17))  # Business hours
            if weekday_activity > sum(hourly_activity.values()) * 0.6:
                patterns.append("business_hours_active")
                
            return {
                'patterns': patterns,
                'peak_hours': [{'hour': h, 'activity': a} for h, a in peak_hours],
                'peak_days': [{'day': d, 'activity': a} for d, a in peak_days],
                'hourly_distribution': dict(hourly_activity),
                'daily_distribution': dict(daily_activity)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing temporal patterns: {str(e)}")
            return {'patterns': [], 'peak_hours': [], 'peak_days': []}
            
    async def _analyze_content_preferences(self, behavior_data: UserBehaviorData) -> Dict[str, Any]:
        """Analyze content preferences and affinities"""        try:
            content_scores = behavior_data.content_preferences
            
            if not content_scores:
                return {'top_categories': [], 'content_style': ContentStyle.CASUAL, 'preferences': {}}
                
            # Sort preferences by score
            sorted_preferences = sorted(content_scores.items(), key=lambda x: x[1], reverse=True)
            top_categories = sorted_preferences[:5]
            
            # Infer content style preferences
            style_indicators = {
                ContentStyle.FORMAL: ['business', 'professional', 'corporate', 'official'],
                ContentStyle.CASUAL: ['lifestyle', 'personal', 'informal', 'relaxed'],
                ContentStyle.TECHNICAL: ['tutorial', 'howto', 'technical', 'educational'],
                ContentStyle.CREATIVE: ['art', 'design', 'creative', 'inspiration'],
                ContentStyle.HUMOROUS: ['funny', 'humor', 'memes', 'entertainment']
            }
            
            style_scores = defaultdict(float)
            for category, score in content_scores.items():
                for style, keywords in style_indicators.items():
                    if any(keyword in category.lower() for keyword in keywords):
                        style_scores[style] += score
                        
            preferred_style = max(style_scores.items(), key=lambda x: x[1])[0] if style_scores else ContentStyle.CASUAL
            
            return {
                'top_categories': [{'category': cat, 'score': score} for cat, score in top_categories],
                'content_style': preferred_style,
                'preferences': dict(content_scores),
                'style_confidence': style_scores[preferred_style] if style_scores else 0.5
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content preferences: {str(e)}")
            return {'top_categories': [], 'content_style': ContentStyle.CASUAL, 'preferences': {}}
            
    async def _analyze_channel_preferences(self, behavior_data: UserBehaviorData) -> Dict[str, Any]:
        """Analyze communication channel preferences"""        try:
            channel_prefs = behavior_data.channel_preferences
            
            if not channel_prefs:
                return {'preferred_channels': [], 'channel_ranking': {}}
                
            # Sort channels by preference score
            sorted_channels = sorted(channel_prefs.items(), key=lambda x: x[1], reverse=True)
            
            # Calculate channel affinity categories
            primary_channels = [ch for ch, score in sorted_channels if score >= 0.7]
            secondary_channels = [ch for ch, score in sorted_channels if 0.4 <= score < 0.7]
            low_preference_channels = [ch for ch, score in sorted_channels if score < 0.4]
            
            return {
                'preferred_channels': sorted_channels,
                'primary_channels': primary_channels,
                'secondary_channels': secondary_channels,
                'low_preference_channels': low_preference_channels,
                'channel_ranking': dict(channel_prefs)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing channel preferences: {str(e)}")
            return {'preferred_channels': [], 'channel_ranking': {}}
            
    async def _analyze_interaction_patterns(self, behavior_data: UserBehaviorData) -> Dict[str, Any]:
        """Analyze interaction patterns and behaviors"""        try:
            if not behavior_data.interaction_history:
                return {'patterns': [], 'interaction_types': {}, 'response_patterns': {}}
                
            # Analyze interaction types
            interaction_types = Counter()
            response_times = []
            
            for interaction in behavior_data.interaction_history:
                interaction_type = interaction.get('type', 'unknown')
                interaction_types[interaction_type] += 1
                
                if 'response_time' in interaction:
                    response_times.append(interaction['response_time'])
                    
            # Analyze response patterns
            response_patterns = {}
            if response_times:
                response_patterns = {
                    'avg_response_time': np.mean(response_times),
                    'median_response_time': np.median(response_times),
                    'quick_responder': np.mean(response_times) < 300,  # 5 minutes
                    'response_consistency': np.std(response_times)
                }
                
            return {
                'interaction_types': dict(interaction_types),
                'response_patterns': response_patterns,
                'total_interactions': len(behavior_data.interaction_history),
                'interaction_frequency': len(behavior_data.interaction_history) / max(
                    (datetime.utcnow() - behavior_data.last_updated).days, 1
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing interaction patterns: {str(e)}")
            return {'patterns': [], 'interaction_types': {}, 'response_patterns': {}}
            
    async def _identify_behavioral_clusters(self, behavior_data: UserBehaviorData) -> Dict[str, Any]:
        """Identify behavioral clusters and user segments"""        try:
            # This would typically use clustering algorithms on user behavior data
            # For now, return rule-based behavioral segments
            
            segments = []
            
            # Analyze engagement level
            engagement = await self._classify_engagement_level(behavior_data)
            if engagement['level'] in [EngagementLevel.VERY_HIGH, EngagementLevel.HIGH]:
                segments.append("highly_engaged")
            elif engagement['level'] == EngagementLevel.MEDIUM:
                segments.append("moderately_engaged")
            else:
                segments.append("low_engagement")
                
            # Analyze content preferences
            if len(behavior_data.content_preferences) >= 5:
                segments.append("diverse_interests")
            elif len(behavior_data.content_preferences) <= 2:
                segments.append("focused_interests")
                
            # Analyze channel preferences
            if len(behavior_data.channel_preferences) >= 3:
                segments.append("multi_channel_user")
            else:
                segments.append("single_channel_user")
                
            return {
                'primary_segment': segments[0] if segments else "undefined",
                'all_segments': segments,
                'segment_confidence': 0.8 if len(segments) >= 2 else 0.5
            }
            
        except Exception as e:
            logger.error(f"Error identifying behavioral clusters: {str(e)}")
            return {'primary_segment': 'undefined', 'all_segments': [], 'segment_confidence': 0.0}
            
    async def _generate_prediction_insights(self, behavior_data: UserBehaviorData) -> Dict[str, Any]:
        """Generate predictive insights about user behavior"""        try:
            predictions = {}
            
            # Predict next likely action
            if behavior_data.interaction_history:
                recent_actions = [i.get('type') for i in behavior_data.interaction_history[-10:]]
                action_frequency = Counter(recent_actions)
                most_likely_action = action_frequency.most_common(1)[0][0] if action_frequency else "view_content"
                predictions['next_likely_action'] = most_likely_action
                
            # Predict optimal engagement time
            temporal_analysis = await self._analyze_temporal_patterns(behavior_data)
            if temporal_analysis['peak_hours']:
                predictions['optimal_engagement_hour'] = temporal_analysis['peak_hours'][0]['hour']
                
            # Predict churn risk
            days_since_last_interaction = (datetime.utcnow() - behavior_data.last_updated).days
            if days_since_last_interaction > 14:
                predictions['churn_risk'] = "high"
            elif days_since_last_interaction > 7:
                predictions['churn_risk'] = "medium"
            else:
                predictions['churn_risk'] = "low"
                
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating prediction insights: {str(e)}")
            return {}
            
    async def _detect_behavioral_anomalies(self, behavior_data: UserBehaviorData) -> Dict[str, Any]:
        """Detect anomalies in user behavior patterns"""        try:
            anomalies = []
            
            # Check for sudden changes in interaction frequency
            if len(behavior_data.interaction_history) >= 10:
                recent_interactions = behavior_data.interaction_history[-5:]
                older_interactions = behavior_data.interaction_history[-10:-5]
                
                recent_freq = len(recent_interactions)
                older_freq = len(older_interactions)
                
                if recent_freq > older_freq * 3:
                    anomalies.append({
                        'type': 'sudden_activity_increase',
                        'severity': 'medium',
                        'details': f'Activity increased from {older_freq} to {recent_freq}'
                    })
                elif recent_freq < older_freq * 0.3:
                    anomalies.append({
                        'type': 'sudden_activity_decrease', 
                        'severity': 'high',
                        'details': f'Activity decreased from {older_freq} to {recent_freq}'
                    })
                    
            # Check for unusual temporal patterns
            current_hour = datetime.utcnow().hour
            temporal_analysis = await self._analyze_temporal_patterns(behavior_data)
            peak_hours = [h['hour'] for h in temporal_analysis['peak_hours']]
            
            if peak_hours and abs(current_hour - peak_hours[0]) > 6:
                anomalies.append({
                    'type': 'unusual_time_activity',
                    'severity': 'low',
                    'details': f'Active at {current_hour}, usual peak at {peak_hours[0]}'
                })
                
            return {
                'anomalies_detected': len(anomalies),
                'anomalies': anomalies,
                'risk_level': 'high' if any(a['severity'] == 'high' for a in anomalies) else 'low'
            }
            
        except Exception as e:
            logger.error(f"Error detecting behavioral anomalies: {str(e)}")
            return {'anomalies_detected': 0, 'anomalies': [], 'risk_level': 'low'}
            
    async def _identify_personalization_opportunities(self, behavior_data: UserBehaviorData) -> Dict[str, Any]:
        """Identify opportunities for improved personalization"""        try:
            opportunities = []
            
            # Check for content personalization opportunities
            if len(behavior_data.content_preferences) < 3:
                opportunities.append({
                    'type': 'content_preference_learning',
                    'priority': 'high',
                    'suggestion': 'Collect more content interaction data to improve recommendations'
                })
                
            # Check for channel optimization opportunities
            if len(behavior_data.channel_preferences) == 1:
                opportunities.append({
                    'type': 'channel_diversification',
                    'priority': 'medium', 
                    'suggestion': 'Introduce user to additional communication channels'
                })
                
            # Check for temporal optimization
            temporal_analysis = await self._analyze_temporal_patterns(behavior_data)
            if not temporal_analysis['peak_hours']:
                opportunities.append({
                    'type': 'temporal_pattern_learning',
                    'priority': 'medium',
                    'suggestion': 'Learn user\'s preferred engagement times for better timing'
                })
                
            # Check engagement level opportunities
            engagement = await self._classify_engagement_level(behavior_data)
            if engagement['level'] in [EngagementLevel.LOW, EngagementLevel.VERY_LOW]:
                opportunities.append({
                    'type': 'engagement_improvement',
                    'priority': 'high',
                    'suggestion': 'Implement engagement recovery strategies'
                })
                
            return {
                'total_opportunities': len(opportunities),
                'opportunities': opportunities,
                'priority_opportunities': [o for o in opportunities if o['priority'] == 'high']
            }
            
        except Exception as e:
            logger.error(f"Error identifying personalization opportunities: {str(e)}")
            return {'total_opportunities': 0, 'opportunities': []}


class PersonalizationEngine:
    """Advanced AI-driven personalization engine"""    
    def __init__(self, config: PersonalizationConfiguration):
        self.config = config
        self.behavior_analyzer = BehaviorAnalyzer(config)
        self.nlp_processor = NLPProcessor()
        self.cache_manager = CacheManager()
        self.metrics_collector = MetricsCollector()
        self.privacy_manager = PrivacyManager()
        
        # AI models
        self.sentiment_analyzer = None
        self.language_detector = None
        self.content_embedder = None
        
        # User data storage
        self.user_profiles = {}
        self.user_behavior_data = {}
        self.personalization_history = defaultdict(list)
        
        self._initialize_ai_models()
        
    def _initialize_ai_models(self):
        """Initialize AI models for personalization"""        try:
            # Sentiment analysis
            if self.config.enable_sentiment_analysis:
                try:
                    self.sentiment_analyzer = SentimentIntensityAnalyzer()
                except:
                    logger.warning("Could not initialize VADER sentiment analyzer")
                    
            # Language detection is already handled by langdetect
            
            # Content embedding model (would use actual transformers in production)
            if self.config.enable_contextual_adaptation:
                try:
                    # This would be initialized with actual transformer models
                    pass
                except Exception as e:
                    logger.warning(f"Could not initialize content embedder: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error initializing AI models: {str(e)}")
            
    async def personalize_content(self, request: PersonalizationRequest) -> Dict[str, Any]:
        """Personalize content using advanced AI techniques"""        try:
            start_time = datetime.utcnow()
            
            # Get or create user behavior data
            behavior_data = await self._get_user_behavior_data(request.user_id)
            
            # Perform behavioral analysis
            behavior_analysis = await self.behavior_analyzer.analyze_user_behavior(behavior_data)
            
            # Apply different personalization strategies
            personalized_content = request.content_template.copy()
            personalization_metadata = {
                'strategies_applied': [],
                'confidence_scores': {},
                'personalization_factors': {}
            }
            
            for personalization_type in request.personalization_types:
                if personalization_type == PersonalizationType.DEMOGRAPHIC:
                    result = await self._apply_demographic_personalization(
                        personalized_content, behavior_data, request.context
                    )
                elif personalization_type == PersonalizationType.BEHAVIORAL:
                    result = await self._apply_behavioral_personalization(
                        personalized_content, behavior_analysis, request.context
                    )
                elif personalization_type == PersonalizationType.CONTEXTUAL:
                    result = await self._apply_contextual_personalization(
                        personalized_content, request.context, behavior_data
                    )
                elif personalization_type == PersonalizationType.COLLABORATIVE:
                    result = await self._apply_collaborative_personalization(
                        personalized_content, behavior_data, request.context
                    )
                elif personalization_type == PersonalizationType.CONTENT_BASED:
                    result = await self._apply_content_based_personalization(
                        personalized_content, behavior_analysis, request.context
                    )
                elif personalization_type == PersonalizationType.HYBRID:
                    result = await self._apply_hybrid_personalization(
                        personalized_content, behavior_analysis, request.context
                    )
                elif personalization_type == PersonalizationType.REAL_TIME:
                    result = await self._apply_real_time_personalization(
                        personalized_content, request.context, behavior_data
                    )
                elif personalization_type == PersonalizationType.PREDICTIVE:
                    result = await self._apply_predictive_personalization(
                        personalized_content, behavior_analysis, request.context
                    )
                else:
                    continue
                    
                # Update content and metadata
                personalized_content = result.get('content', personalized_content)
                personalization_metadata['strategies_applied'].append(personalization_type.value)
                personalization_metadata['confidence_scores'][personalization_type.value] = result.get('confidence', 0.5)
                
            # Apply privacy protection if enabled
            if self.config.enable_privacy_protection:
                personalized_content = await self.privacy_manager.apply_privacy_protection(
                    personalized_content, request.user_id
                )
                
            # Record personalization for learning
            await self._record_personalization(request, personalized_content, personalization_metadata)
            
            # Calculate overall personalization quality score
            overall_confidence = np.mean(list(personalization_metadata['confidence_scores'].values())) if personalization_metadata['confidence_scores'] else 0.5
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                'personalized_content': personalized_content,
                'personalization_metadata': personalization_metadata,
                'behavior_insights': behavior_analysis,
                'confidence_score': overall_confidence,
                'processing_time_seconds': processing_time,
                'user_segment': behavior_analysis.get('behavioral_clusters', {}).get('primary_segment', 'undefined'),
                'personalization_opportunities': behavior_analysis.get('personalization_opportunities', {}),
                'privacy_applied': self.config.enable_privacy_protection
            }
            
        except Exception as e:
            logger.error(f"Error personalizing content: {str(e)}")
            return {
                'personalized_content': request.content_template,
                'personalization_metadata': {'error': str(e)},
                'confidence_score': 0.0,
                'processing_time_seconds': 0
            }
            
    async def _get_user_behavior_data(self, user_id: str) -> UserBehaviorData:
        """Get or initialize user behavior data"""        try:
            if user_id not in self.user_behavior_data:
                self.user_behavior_data[user_id] = UserBehaviorData(user_id=user_id)
                
            return self.user_behavior_data[user_id]
            
        except Exception as e:
            logger.error(f"Error getting user behavior data: {str(e)}")
            return UserBehaviorData(user_id=user_id)
            
    async def _apply_demographic_personalization(self, content: Dict[str, Any],
                                               behavior_data: UserBehaviorData,
                                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply demographic-based personalization"""        try:
            personalized_content = content.copy()
            confidence = 0.5
            
            # Extract demographic information
            demographics = behavior_data.demographic_data
            
            # Age-based personalization
            age = demographics.get('age')
            if age:
                if age < 25:
                    # Younger audience - more casual, emoji usage
                    personalized_content = self._adjust_tone_for_young_audience(personalized_content)
                    confidence += 0.2
                elif age > 55:
                    # Older audience - more formal, detailed explanations
                    personalized_content = self._adjust_tone_for_mature_audience(personalized_content)
                    confidence += 0.2
                    
            # Location-based personalization
            location = demographics.get('location') or context.get('location')
            if location:
                personalized_content = await self._apply_location_personalization(
                    personalized_content, location
                )
                confidence += 0.1
                
            # Language preference
            language = demographics.get('language') or context.get('language')
            if language and language != 'en':
                # Would apply translation or language-specific adaptations
                confidence += 0.1
                
            return {
                'content': personalized_content,
                'confidence': min(confidence, 1.0),
                'factors_applied': ['age', 'location', 'language']
            }
            
        except Exception as e:
            logger.error(f"Error applying demographic personalization: {str(e)}")
            return {'content': content, 'confidence': 0.5}
            
    def _adjust_tone_for_young_audience(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust content tone for younger audience"""        adjusted_content = content.copy()
        
        # Make text more casual and add emojis where appropriate
        if 'message' in adjusted_content:
            message = adjusted_content['message']
            
            # Replace formal phrases with casual ones
            replacements = {
                'Hello': 'Hey',
                'Thank you': 'Thanks',
                'Please note': 'Just so you know',
                'We are pleased to inform you': 'Great news!',
                'Sincerely': 'Cheers'
            }
            
            for formal, casual in replacements.items():
                message = message.replace(formal, casual)
                
            adjusted_content['message'] = message
            
        return adjusted_content
        
    def _adjust_tone_for_mature_audience(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust content tone for mature audience"""        adjusted_content = content.copy()
        
        # Make text more formal and detailed
        if 'message' in adjusted_content:
            message = adjusted_content['message']
            
            # Replace casual phrases with formal ones
            replacements = {
                'Hey': 'Hello',
                'Thanks': 'Thank you',
                'Just so you know': 'Please note',
                'Great news!': 'We are pleased to inform you',
                'Cheers': 'Best regards'
            }
            
            for casual, formal in replacements.items():
                message = message.replace(casual, formal)
                
            adjusted_content['message'] = message
            
        return adjusted_content
        
    async def _apply_location_personalization(self, content: Dict[str, Any], 
                                            location: str) -> Dict[str, Any]:
        """Apply location-based personalization"""        try:
            personalized_content = content.copy()
            
            # Timezone awareness
            if self.config.enable_timezone_awareness:
                # Would adjust time-sensitive content based on user's timezone
                pass
                
            # Local holidays and events
            try:
                country = location.split(',')[-1].strip() if ',' in location else location
                country_holidays = holidays.country_holidays(country)
                today = datetime.now().date()
                
                if today in country_holidays:
                    holiday_name = country_holidays[today]
                    # Add holiday greeting if appropriate
                    if 'message' in personalized_content:
                        personalized_content['message'] = f"Happy {holiday_name}! " + personalized_content['message']
            except:
                pass  # Holiday detection failed, continue without modification
                
            return personalized_content
            
        except Exception as e:
            logger.error(f"Error applying location personalization: {str(e)}")
            return content
            
    async def _apply_behavioral_personalization(self, content: Dict[str, Any],
                                              behavior_analysis: Dict[str, Any],
                                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply behavioral-based personalization"""        try:
            personalized_content = content.copy()
            confidence = 0.5
            
            # Engagement level adaptation
            engagement_info = behavior_analysis.get('engagement_level', {})
            engagement_level = engagement_info.get('level', EngagementLevel.MEDIUM)
            
            if engagement_level == EngagementLevel.VERY_HIGH:
                # Highly engaged users - can handle more detailed content
                personalized_content = self._enhance_content_detail(personalized_content)
                confidence += 0.3
            elif engagement_level in [EngagementLevel.LOW, EngagementLevel.VERY_LOW]:
                # Low engagement users - simplify and make more engaging
                personalized_content = self._simplify_content(personalized_content)
                confidence += 0.2
                
            # Content style adaptation
            content_analysis = behavior_analysis.get('content_preferences', {})
            preferred_style = content_analysis.get('content_style', ContentStyle.CASUAL)
            
            if preferred_style == ContentStyle.FORMAL:
                personalized_content = self._apply_formal_style(personalized_content)
                confidence += 0.2
            elif preferred_style == ContentStyle.HUMOROUS:
                personalized_content = self._apply_humorous_style(personalized_content)
                confidence += 0.2
                
            # Temporal personalization based on patterns
            temporal_patterns = behavior_analysis.get('temporal_patterns', {})
            if temporal_patterns.get('patterns'):
                personalized_content = self._apply_temporal_personalization(
                    personalized_content, temporal_patterns
                )
                confidence += 0.1
                
            return {
                'content': personalized_content,
                'confidence': min(confidence, 1.0),
                'factors_applied': ['engagement_level', 'content_style', 'temporal_patterns']
            }
            
        except Exception as e:
            logger.error(f"Error applying behavioral personalization: {str(e)}")
            return {'content': content, 'confidence': 0.5}
            
    def _enhance_content_detail(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance content with more details for highly engaged users"""        enhanced_content = content.copy()
        
        # Add more detailed explanations, additional context, etc.
        if 'message' in enhanced_content:
            message = enhanced_content['message']
            # Could add more detailed information, links, resources
            enhanced_content['additional_details'] = True
            
        return enhanced_content
        
    def _simplify_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify content for low engagement users"""        simplified_content = content.copy()
        
        # Make content more concise and engaging
        if 'message' in simplified_content:
            message = simplified_content['message']
            # Shorten sentences, use bullet points, add call-to-action
            simplified_content['simplified'] = True
            
        return simplified_content
        
    def _apply_formal_style(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply formal communication style"""        return self._adjust_tone_for_mature_audience(content)
        
    def _apply_humorous_style(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply humorous communication style"""        humorous_content = content.copy()
        
        # Add light humor where appropriate
        if 'message' in humorous_content:
            # Could add appropriate emojis, light jokes, etc.
            humorous_content['style'] = 'humorous'
            
        return humorous_content
        
    def _apply_temporal_personalization(self, content: Dict[str, Any],
                                      temporal_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Apply temporal-based personalization"""        temporal_content = content.copy()
        
        # Adjust content timing and urgency based on user patterns
        patterns = temporal_patterns.get('patterns', [])
        
        if 'morning_person' in patterns:
            # Morning person - energetic tone
            temporal_content['timing_optimized'] = 'morning'
        elif 'night_owl' in patterns:
            # Night owl - more relaxed tone
            temporal_content['timing_optimized'] = 'evening'
            
        return temporal_content
        
    async def _apply_contextual_personalization(self, content: Dict[str, Any],
                                              context: Dict[str, Any],
                                              behavior_data: UserBehaviorData) -> Dict[str, Any]:
        """Apply contextual personalization based on current context"""        try:
            personalized_content = content.copy()
            confidence = 0.5
            
            # Device-based personalization
            device = context.get('device')
            if device:
                if device == 'mobile':
                    personalized_content = self._optimize_for_mobile(personalized_content)
                    confidence += 0.1
                elif device == 'desktop':
                    personalized_content = self._optimize_for_desktop(personalized_content)
                    confidence += 0.1
                    
            # Time-based personalization
            current_time = datetime.utcnow()
            hour = current_time.hour
            
            if 5 <= hour < 12:
                # Morning
                personalized_content = self._apply_morning_context(personalized_content)
                confidence += 0.1
            elif 17 <= hour < 21:
                # Evening
                personalized_content = self._apply_evening_context(personalized_content)
                confidence += 0.1
                
            # Urgency-based personalization
            urgency = context.get('urgency_level', 0.5)
            if urgency > 0.8:
                personalized_content = self._apply_high_urgency_styling(personalized_content)
                confidence += 0.2
                
            return {
                'content': personalized_content,
                'confidence': min(confidence, 1.0),
                'factors_applied': ['device', 'time_context', 'urgency']
            }
            
        except Exception as e:
            logger.error(f"Error applying contextual personalization: {str(e)}")
            return {'content': content, 'confidence': 0.5}
            
    def _optimize_for_mobile(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for mobile devices"""        mobile_content = content.copy()
        
        # Shorter messages, concise formatting
        if 'message' in mobile_content:
            mobile_content['mobile_optimized'] = True
            
        return mobile_content
        
    def _optimize_for_desktop(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for desktop devices"""        desktop_content = content.copy()
        
        # Can include more detailed content, richer formatting
        if 'message' in desktop_content:
            desktop_content['desktop_optimized'] = True
            
        return desktop_content
        
    def _apply_morning_context(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply morning-appropriate context"""        morning_content = content.copy()
        
        if 'message' in morning_content:
            # Could add morning greetings, energy-focused language
            morning_content['time_context'] = 'morning'
            
        return morning_content
        
    def _apply_evening_context(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply evening-appropriate context"""        evening_content = content.copy()
        
        if 'message' in evening_content:
            # More relaxed tone, wind-down messaging
            evening_content['time_context'] = 'evening'
            
        return evening_content
        
    def _apply_high_urgency_styling(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply high urgency styling to content"""        urgent_content = content.copy()
        
        if 'message' in urgent_content:
            # Add urgency indicators, call-to-action prominence
            urgent_content['urgency'] = 'high'
            urgent_content['priority'] = True
            
        return urgent_content
        
    async def _apply_collaborative_personalization(self, content: Dict[str, Any],
                                                 behavior_data: UserBehaviorData,
                                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply collaborative filtering personalization"""        try:
            # This would use collaborative filtering based on similar users
            # For now, return basic personalization
            return {
                'content': content,
                'confidence': 0.4,
                'factors_applied': ['collaborative_filtering']
            }
            
        except Exception as e:
            logger.error(f"Error applying collaborative personalization: {str(e)}")
            return {'content': content, 'confidence': 0.3}
            
    async def _apply_content_based_personalization(self, content: Dict[str, Any],
                                                 behavior_analysis: Dict[str, Any],
                                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply content-based personalization"""        try:
            personalized_content = content.copy()
            confidence = 0.5
            
            # Use content preferences to adapt messaging
            content_prefs = behavior_analysis.get('content_preferences', {})
            top_categories = content_prefs.get('top_categories', [])
            
            if top_categories:
                # Adapt content based on user's preferred content categories
                preferred_category = top_categories[0]['category']
                personalized_content['content_category_matched'] = preferred_category
                confidence += 0.2
                
            return {
                'content': personalized_content,
                'confidence': min(confidence, 1.0),
                'factors_applied': ['content_preferences']
            }
            
        except Exception as e:
            logger.error(f"Error applying content-based personalization: {str(e)}")
            return {'content': content, 'confidence': 0.4}
            
    async def _apply_hybrid_personalization(self, content: Dict[str, Any],
                                          behavior_analysis: Dict[str, Any],
                                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply hybrid personalization combining multiple strategies"""        try:
            # Combine demographic, behavioral, and contextual personalization
            result = await self._apply_behavioral_personalization(content, behavior_analysis, context)
            hybrid_content = result['content']
            confidence = result['confidence']
            
            # Add contextual elements
            contextual_result = await self._apply_contextual_personalization(
                hybrid_content, context, UserBehaviorData(user_id="temp")
            )
            
            return {
                'content': contextual_result['content'],
                'confidence': min((confidence + contextual_result['confidence']) / 2, 1.0),
                'factors_applied': ['hybrid_behavioral_contextual']
            }
            
        except Exception as e:
            logger.error(f"Error applying hybrid personalization: {str(e)}")
            return {'content': content, 'confidence': 0.5}
            
    async def _apply_real_time_personalization(self, content: Dict[str, Any],
                                             context: Dict[str, Any],
                                             behavior_data: UserBehaviorData) -> Dict[str, Any]:
        """Apply real-time personalization based on current context"""        try:
            real_time_content = content.copy()
            confidence = 0.6
            
            # Current session behavior
            current_session = context.get('current_session', {})
            if current_session:
                # Adapt based on current session activity
                real_time_content['session_adapted'] = True
                confidence += 0.2
                
            # Recent interaction context
            if behavior_data.interaction_history:
                recent_interaction = behavior_data.interaction_history[-1]
                interaction_type = recent_interaction.get('type')
                
                if interaction_type:
                    real_time_content['last_interaction_type'] = interaction_type
                    confidence += 0.1
                    
            return {
                'content': real_time_content,
                'confidence': min(confidence, 1.0),
                'factors_applied': ['real_time_session', 'recent_interactions']
            }
            
        except Exception as e:
            logger.error(f"Error applying real-time personalization: {str(e)}")
            return {'content': content, 'confidence': 0.5}
            
    async def _apply_predictive_personalization(self, content: Dict[str, Any],
                                              behavior_analysis: Dict[str, Any],
                                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply predictive personalization based on predicted user behavior"""        try:
            predictive_content = content.copy()
            confidence = 0.4
            
            # Use prediction insights
            predictions = behavior_analysis.get('prediction_insights', {})
            
            # Predict next likely action and optimize for it
            next_action = predictions.get('next_likely_action')
            if next_action:
                predictive_content['optimized_for_action'] = next_action
                confidence += 0.2
                
            # Use optimal engagement time prediction
            optimal_hour = predictions.get('optimal_engagement_hour')
            if optimal_hour:
                current_hour = datetime.utcnow().hour
                if abs(current_hour - optimal_hour) <= 2:
                    # We're in the optimal engagement window
                    predictive_content['optimal_timing'] = True
                    confidence += 0.2
                    
            return {
                'content': predictive_content,
                'confidence': min(confidence, 1.0),
                'factors_applied': ['predicted_actions', 'optimal_timing']
            }
            
        except Exception as e:
            logger.error(f"Error applying predictive personalization: {str(e)}")
            return {'content': content, 'confidence': 0.4}
            
    async def _record_personalization(self, request: PersonalizationRequest,
                                    personalized_content: Dict[str, Any],
                                    metadata: Dict[str, Any]):
        """Record personalization for learning and optimization"""        try:
            record = {
                'timestamp': datetime.utcnow(),
                'user_id': request.user_id,
                'channel_id': request.channel_id,
                'original_content': request.content_template,
                'personalized_content': personalized_content,
                'personalization_types': [pt.value for pt in request.personalization_types],
                'metadata': metadata,
                'context': request.context
            }
            
            self.personalization_history[request.user_id].append(record)
            
            # Maintain sliding window of records
            cutoff_time = datetime.utcnow() - timedelta(days=30)
            self.personalization_history[request.user_id] = [
                r for r in self.personalization_history[request.user_id]
                if r['timestamp'] > cutoff_time
            ]
            
            # Update metrics
            await self.metrics_collector.record_personalization_event(record)
            
        except Exception as e:
            logger.error(f"Error recording personalization: {str(e)}")
            
    async def update_user_behavior(self, user_id: str, interaction_data: Dict[str, Any]):
        """Update user behavior data based on new interactions"""        try:
            if user_id not in self.user_behavior_data:
                self.user_behavior_data[user_id] = UserBehaviorData(user_id=user_id)
                
            behavior_data = self.user_behavior_data[user_id]
            
            # Add new interaction
            interaction_record = {
                'timestamp': interaction_data.get('timestamp', datetime.utcnow().isoformat()),
                'type': interaction_data.get('type', 'unknown'),
                'channel': interaction_data.get('channel'),
                'content_type': interaction_data.get('content_type'),
                'engagement_score': interaction_data.get('engagement_score', 0.5),
                'response_time': interaction_data.get('response_time'),
                'metadata': interaction_data.get('metadata', {})
            }
            
            behavior_data.interaction_history.append(interaction_record)
            
            # Update preferences based on interaction
            content_type = interaction_data.get('content_type')
            engagement_score = interaction_data.get('engagement_score', 0.5)
            
            if content_type:
                # Update content preferences with exponential smoothing
                current_pref = behavior_data.content_preferences.get(content_type, 0.5)
                alpha = 0.3  # Learning rate
                new_pref = alpha * engagement_score + (1 - alpha) * current_pref
                behavior_data.content_preferences[content_type] = new_pref
                
            # Update channel preferences
            channel = interaction_data.get('channel')
            if channel:
                current_channel_pref = behavior_data.channel_preferences.get(channel, 0.5)
                new_channel_pref = alpha * engagement_score + (1 - alpha) * current_channel_pref
                behavior_data.channel_preferences[channel] = new_channel_pref
                
            # Update last updated timestamp
            behavior_data.last_updated = datetime.utcnow()
            
            # Maintain sliding window of interactions
            cutoff_time = datetime.utcnow() - timedelta(days=90)
            behavior_data.interaction_history = [
                interaction for interaction in behavior_data.interaction_history
                if datetime.fromisoformat(interaction['timestamp']) > cutoff_time
            ]
            
        except Exception as e:
            logger.error(f"Error updating user behavior: {str(e)}")
            
    def get_personalization_analytics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get personalization analytics and performance metrics"""        try:
            if user_id:
                # User-specific analytics
                user_history = self.personalization_history.get(user_id, [])
                if not user_history:
                    return {'user_id': user_id, 'total_personalizations': 0}
                    
                # Calculate user-specific metrics
                total_personalizations = len(user_history)
                avg_confidence = np.mean([
                    record['metadata'].get('confidence_score', 0.5) 
                    for record in user_history
                ])
                
                strategies_used = Counter()
                for record in user_history:
                    for strategy in record['personalization_types']:
                        strategies_used[strategy] += 1
                        
                return {
                    'user_id': user_id,
                    'total_personalizations': total_personalizations,
                    'average_confidence': avg_confidence,
                    'strategies_used': dict(strategies_used),
                    'most_used_strategy': strategies_used.most_common(1)[0][0] if strategies_used else None
                }
            else:
                # Global analytics
                total_users = len(self.personalization_history)
                total_personalizations = sum(len(history) for history in self.personalization_history.values())
                
                if total_personalizations == 0:
                    return {
                        'total_users': total_users,
                        'total_personalizations': 0,
                        'average_confidence': 0
                    }
                    
                all_confidences = []
                all_strategies = Counter()
                
                for user_history in self.personalization_history.values():
                    for record in user_history:
                        confidence = record['metadata'].get('confidence_score', 0.5)
                        all_confidences.append(confidence)
                        
                        for strategy in record['personalization_types']:
                            all_strategies[strategy] += 1
                            
                return {
                    'total_users': total_users,
                    'total_personalizations': total_personalizations,
                    'average_confidence': np.mean(all_confidences),
                    'confidence_std': np.std(all_confidences),
                    'top_strategies': all_strategies.most_common(5),
                    'personalization_rate': total_personalizations / total_users if total_users > 0 else 0
                }
                
        except Exception as e:
            logger.error(f"Error getting personalization analytics: {str(e)}")
            return {}


# Export main classes
__all__ = [
    'PersonalizationEngine',
    'BehaviorAnalyzer',
    'PersonalizationConfiguration',
    'PersonalizationRequest',
    'UserBehaviorData',
    'PersonalizationType',
    'EngagementLevel',
    'ContentStyle'
]
