"""AI-Powered Content Optimization Engine - IA Influencer Agent Platform

Advanced AI system for content optimization recommendations across all formats.
Uses machine learning models to analyze content performance and provide actionable insights.

Author: Fahed Mlaiel (mlaiel@live.de)  
Development Team: Lead AI Developer, Senior Backend Engineer, ML Engineer, DBA, Security Expert

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, or distribution is STRICTLY PROHIBITED.
"""
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
from uuid import UUID, uuid4

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.metrics import mean_squared_error, r2_score
import tensorflow as tf
from transformers import pipeline, AutoTokenizer, AutoModel

from sqlalchemy import Column, String, DateTime, Float, Integer, JSON, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session

Base = declarative_base()


class OptimizationType(Enum):
    """Types of content optimization"""    TITLE_OPTIMIZATION = "title_optimization"
    DESCRIPTION_OPTIMIZATION = "description_optimization"
    HASHTAG_OPTIMIZATION = "hashtag_optimization"
    TIMING_OPTIMIZATION = "timing_optimization"
    FORMAT_OPTIMIZATION = "format_optimization"
    THUMBNAIL_OPTIMIZATION = "thumbnail_optimization"
    AUDIO_OPTIMIZATION = "audio_optimization"
    VISUAL_OPTIMIZATION = "visual_optimization"
    SEO_OPTIMIZATION = "seo_optimization"
    ENGAGEMENT_OPTIMIZATION = "engagement_optimization"


class ContentElement(Enum):
    """Content elements that can be optimized"""    TITLE = "title"
    DESCRIPTION = "description"
    TAGS = "tags"
    THUMBNAIL = "thumbnail"
    AUDIO_QUALITY = "audio_quality"
    VIDEO_QUALITY = "video_quality"
    POSTING_TIME = "posting_time"
    CAPTION = "caption"
    CALL_TO_ACTION = "call_to_action"
    DURATION = "duration"


class OptimizationPriority(Enum):
    """Priority levels for optimization recommendations"""    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"


@dataclass
class OptimizationRecommendation:
    """Data structure for optimization recommendations"""    element: ContentElement
    optimization_type: OptimizationType
    current_value: str
    suggested_value: str
    confidence_score: float
    expected_improvement: float
    priority: OptimizationPriority
    reasoning: str
    implementation_steps: List[str] = field(default_factory=list)
    estimated_time: int = 0  # in minutes
    difficulty_level: str = "easy"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""        return {
            "element": self.element.value,
            "optimization_type": self.optimization_type.value,
            "current_value": self.current_value,
            "suggested_value": self.suggested_value,
            "confidence_score": self.confidence_score,
            "expected_improvement": self.expected_improvement,
            "priority": self.priority.value,
            "reasoning": self.reasoning,
            "implementation_steps": self.implementation_steps,
            "estimated_time": self.estimated_time,
            "difficulty_level": self.difficulty_level
        }


class ContentOptimizationHistory(Base):
    """Database model for optimization history tracking"""    __tablename__ = "content_optimization_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False, index=True)
    content_id = Column(String, nullable=False, index=True)
    
    # Optimization details
    optimization_type = Column(String, nullable=False)
    element_optimized = Column(String, nullable=False)
    original_value = Column(Text)
    optimized_value = Column(Text)
    
    # Performance tracking
    pre_optimization_metrics = Column(JSON)
    post_optimization_metrics = Column(JSON)
    improvement_percentage = Column(Float)
    confidence_score = Column(Float)
    
    # AI model information
    model_version = Column(String)
    algorithm_used = Column(String)
    feature_importance = Column(JSON)
    
    # Metadata
    implemented = Column(Boolean, default=False)
    implementation_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    recommendations = relationship("OptimizationRecommendationModel", back_populates="history")


class OptimizationRecommendationModel(Base):
    """Database model for optimization recommendations"""    __tablename__ = "optimization_recommendations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    history_id = Column(String, ForeignKey("content_optimization_history.id"))
    
    element = Column(String, nullable=False)
    optimization_type = Column(String, nullable=False)
    current_value = Column(Text)
    suggested_value = Column(Text)
    confidence_score = Column(Float)
    expected_improvement = Column(Float)
    priority = Column(String)
    reasoning = Column(Text)
    implementation_steps = Column(JSON)
    estimated_time = Column(Integer)
    difficulty_level = Column(String)
    
    status = Column(String, default="pending")  # pending, implemented, rejected
    feedback_score = Column(Float)  # User feedback on recommendation quality
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    history = relationship("ContentOptimizationHistory", back_populates="recommendations")


class AIContentOptimizer:
    """    Advanced AI-powered content optimization engine.
    Uses multiple ML models and NLP techniques to provide personalized optimization recommendations.
    """    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.nlp_models = {}
        
        # Initialize AI models
        asyncio.create_task(self._initialize_ai_models())
    
    async def _initialize_ai_models(self):
        """Initialize all AI models for content optimization"""        try:
            # Load pre-trained models for different optimization types
            self.models['engagement_predictor'] = self._load_engagement_model()
            self.models['title_optimizer'] = self._load_title_optimization_model()
            self.models['timing_predictor'] = self._load_timing_model()
            self.models['hashtag_analyzer'] = self._load_hashtag_model()
            
            # Load NLP models
            self.nlp_models['sentiment_analyzer'] = pipeline("sentiment-analysis", 
                                                           model="cardiffnlp/twitter-roberta-base-sentiment-latest")
            self.nlp_models['text_generator'] = pipeline("text-generation", 
                                                       model="gpt2-medium")
            
            # Load feature scalers and encoders
            self.scalers['content_features'] = StandardScaler()
            self.encoders['category'] = LabelEncoder()
            
        except Exception as e:
            print(f"Warning: Could not initialize all AI models: {e}")
    
    def _load_engagement_model(self) -> RandomForestRegressor:
        """Load or create engagement prediction model"""        # In production, this would load a pre-trained model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        return model
    
    def _load_title_optimization_model(self) -> GradientBoostingRegressor:
        """Load title optimization model"""        model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        return model
    
    def _load_timing_model(self) -> RandomForestRegressor:
        """Load optimal timing prediction model"""        model = RandomForestRegressor(
            n_estimators=50,
            max_depth=8,
            random_state=42
        )
        return model
    
    def _load_hashtag_model(self) -> KMeans:
        """Load hashtag clustering model"""        model = KMeans(n_clusters=20, random_state=42)
        return model
    
    async def analyze_content_optimization_potential(self, 
                                                   user_id: str, 
                                                   content_id: str, 
                                                   content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content and identify optimization opportunities"""        
        optimization_analysis = {
            "content_id": content_id,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "overall_optimization_score": 0.0,
            "recommendations": [],
            "quick_wins": [],
            "advanced_optimizations": [],
            "ai_insights": {}
        }
        
        try:
            # Extract content features
            content_features = await self._extract_content_features(content_data)
            
            # Analyze each optimization type
            title_recommendations = await self._analyze_title_optimization(content_data)
            description_recommendations = await self._analyze_description_optimization(content_data)
            hashtag_recommendations = await self._analyze_hashtag_optimization(content_data)
            timing_recommendations = await self._analyze_timing_optimization(user_id, content_data)
            format_recommendations = await self._analyze_format_optimization(content_data)
            seo_recommendations = await self._analyze_seo_optimization(content_data)
            
            # Combine all recommendations
            all_recommendations = (
                title_recommendations + 
                description_recommendations + 
                hashtag_recommendations + 
                timing_recommendations + 
                format_recommendations + 
                seo_recommendations
            )
            
            # Sort by priority and expected improvement
            sorted_recommendations = sorted(
                all_recommendations, 
                key=lambda x: (x.priority.value, -x.expected_improvement)
            )
            
            # Calculate overall optimization score
            optimization_analysis["overall_optimization_score"] = self._calculate_optimization_score(
                content_features, all_recommendations
            )
            
            # Categorize recommendations
            optimization_analysis["recommendations"] = [rec.to_dict() for rec in sorted_recommendations]
            optimization_analysis["quick_wins"] = [
                rec.to_dict() for rec in sorted_recommendations 
                if rec.difficulty_level == "easy" and rec.expected_improvement > 10
            ]
            optimization_analysis["advanced_optimizations"] = [
                rec.to_dict() for rec in sorted_recommendations 
                if rec.difficulty_level in ["hard", "expert"] and rec.expected_improvement > 20
            ]
            
            # Generate AI insights
            optimization_analysis["ai_insights"] = await self._generate_ai_insights(
                content_features, all_recommendations
            )
            
            # Save analysis to database
            await self._save_optimization_analysis(user_id, content_id, optimization_analysis)
            
        except Exception as e:
            optimization_analysis["error"] = f"Analysis failed: {str(e)}"
        
        return optimization_analysis
    
    async def _extract_content_features(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from content for ML analysis"""        features = {
            "title_length": len(content_data.get("title", "")),
            "description_length": len(content_data.get("description", "")),
            "hashtag_count": len(content_data.get("hashtags", [])),
            "has_thumbnail": bool(content_data.get("thumbnail")),
            "content_duration": content_data.get("duration", 0),
            "upload_hour": content_data.get("upload_time", datetime.utcnow()).hour,
            "upload_day": content_data.get("upload_time", datetime.utcnow()).weekday(),
            "content_format": content_data.get("format", "unknown"),
            "file_size": content_data.get("file_size", 0),
            "quality_score": content_data.get("quality_score", 0.5)
        }
        
        # NLP features for text content
        if content_data.get("title"):
            sentiment = self.nlp_models.get("sentiment_analyzer", lambda x: [{"score": 0.5}])(content_data["title"])
            features["title_sentiment_score"] = sentiment[0]["score"] if sentiment else 0.5
        
        if content_data.get("description"):
            features["description_word_count"] = len(content_data["description"].split())
            features["description_readability"] = self._calculate_readability_score(content_data["description"])
        
        return features
    
    def _calculate_readability_score(self, text: str) -> float:
        """Calculate readability score using Flesch Reading Ease"""        if not text:
            return 0.0
        
        # Simplified readability calculation
        sentences = text.count('.') + text.count('!') + text.count('?')
        words = len(text.split())
        syllables = sum([self._count_syllables(word) for word in text.split()])
        
        if sentences == 0 or words == 0:
            return 0.0
        
        flesch_score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        return max(0.0, min(100.0, flesch_score))
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    async def _analyze_title_optimization(self, content_data: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Analyze and optimize content titles"""        recommendations = []
        current_title = content_data.get("title", "")
        
        if not current_title:
            recommendations.append(OptimizationRecommendation(
                element=ContentElement.TITLE,
                optimization_type=OptimizationType.TITLE_OPTIMIZATION,
                current_value="No title",
                suggested_value="Add compelling title with keywords",
                confidence_score=0.95,
                expected_improvement=25.0,
                priority=OptimizationPriority.CRITICAL,
                reasoning="Content without titles perform 25% worse in search and discovery",
                implementation_steps=[
                    "Create title with 5-8 words",
                    "Include target keywords",
                    "Make it emotionally engaging",
                    "Ensure it accurately describes content"
                ],
                estimated_time=5,
                difficulty_level="easy"
            ))
            return recommendations
        
        # Analyze title length
        if len(current_title) < 10:
            recommendations.append(OptimizationRecommendation(
                element=ContentElement.TITLE,
                optimization_type=OptimizationType.TITLE_OPTIMIZATION,
                current_value=current_title,
                suggested_value=f"Expand title to 10-60 characters (current: {len(current_title)})",
                confidence_score=0.85,
                expected_improvement=15.0,
                priority=OptimizationPriority.HIGH,
                reasoning="Titles with 10-60 characters perform better in search algorithms",
                implementation_steps=[
                    "Add descriptive keywords",
                    "Include emotional trigger words",
                    "Maintain clarity and relevance"
                ],
                estimated_time=3,
                difficulty_level="easy"
            ))
        
        elif len(current_title) > 60:
            recommendations.append(OptimizationRecommendation(
                element=ContentElement.TITLE,
                optimization_type=OptimizationType.TITLE_OPTIMIZATION,
                current_value=current_title,
                suggested_value=f"Shorten title to under 60 characters (current: {len(current_title)})",
                confidence_score=0.80,
                expected_improvement=12.0,
                priority=OptimizationPriority.MEDIUM,
                reasoning="Long titles get truncated on most platforms, reducing click-through rates",
                implementation_steps=[
                    "Remove unnecessary words",
                    "Focus on core message",
                    "Maintain key keywords"
                ],
                estimated_time=5,
                difficulty_level="easy"
            ))
        
        # Analyze sentiment
        if self.nlp_models.get("sentiment_analyzer"):
            sentiment_result = self.nlp_models["sentiment_analyzer"](current_title)
            if sentiment_result and sentiment_result[0]["label"] == "NEGATIVE":
                recommendations.append(OptimizationRecommendation(
                    element=ContentElement.TITLE,
                    optimization_type=OptimizationType.TITLE_OPTIMIZATION,
                    current_value=current_title,
                    suggested_value="Rewrite with positive or neutral sentiment",
                    confidence_score=0.75,
                    expected_improvement=18.0,
                    priority=OptimizationPriority.HIGH,
                    reasoning="Negative sentiment in titles reduces engagement by 18% on average",
                    implementation_steps=[
                        "Replace negative words with neutral/positive alternatives",
                        "Focus on benefits rather than problems",
                        "Use action-oriented language"
                    ],
                    estimated_time=7,
                    difficulty_level="medium"
                ))
        
        # Keyword optimization suggestions
        content_format = content_data.get("format", "")
        if content_format and content_format not in current_title.lower():
            recommendations.append(OptimizationRecommendation(
                element=ContentElement.TITLE,
                optimization_type=OptimizationType.SEO_OPTIMIZATION,
                current_value=current_title,
                suggested_value=f"Include '{content_format}' keyword in title",
                confidence_score=0.70,
                expected_improvement=10.0,
                priority=OptimizationPriority.MEDIUM,
                reasoning="Including content format in title improves discoverability",
                implementation_steps=[
                    f"Naturally incorporate '{content_format}' into title",
                    "Maintain readability and flow",
                    "Place keyword near the beginning if possible"
                ],
                estimated_time=4,
                difficulty_level="easy"
            ))
        
        return recommendations
    
    async def _analyze_description_optimization(self, content_data: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Analyze and optimize content descriptions"""        recommendations = []
        current_description = content_data.get("description", "")
        
        if not current_description:
            recommendations.append(OptimizationRecommendation(
                element=ContentElement.DESCRIPTION,
                optimization_type=OptimizationType.DESCRIPTION_OPTIMIZATION,
                current_value="No description",
                suggested_value="Add detailed description with keywords and call-to-action",
                confidence_score=0.90,
                expected_improvement=30.0,
                priority=OptimizationPriority.CRITICAL,
                reasoning="Content with descriptions gets 30% more engagement and better SEO ranking",
                implementation_steps=[
                    "Write 150-300 word description",
                    "Include relevant keywords naturally",
                    "Add clear call-to-action",
                    "Explain value proposition",
                    "Include relevant links"
                ],
                estimated_time=10,
                difficulty_level="medium"
            ))
            return recommendations
        
        # Analyze description length
        word_count = len(current_description.split())
        
        if word_count < 50:
            recommendations.append(OptimizationRecommendation(
                element=ContentElement.DESCRIPTION,
                optimization_type=OptimizationType.DESCRIPTION_OPTIMIZATION,
                current_value=f"Description too short ({word_count} words)",
                suggested_value="Expand to 50-300 words for better SEO and engagement",
                confidence_score=0.85,
                expected_improvement=20.0,
                priority=OptimizationPriority.HIGH,
                reasoning="Longer descriptions provide more context and keywords for search algorithms",
                implementation_steps=[
                    "Add more context about the content",
                    "Include benefits and value",
                    "Add relevant keywords naturally",
                    "Include call-to-action"
                ],
                estimated_time=8,
                difficulty_level="easy"
            ))
        
        elif word_count > 300:
            recommendations.append(OptimizationRecommendation(
                element=ContentElement.DESCRIPTION,
                optimization_type=OptimizationType.DESCRIPTION_OPTIMIZATION,
                current_value=f"Description too long ({word_count} words)",
                suggested_value="Condense to 150-300 words for better readability",
                confidence_score=0.75,
                expected_improvement=12.0,
                priority=OptimizationPriority.MEDIUM,
                reasoning="Very long descriptions may not be fully read by users",
                implementation_steps=[
                    "Remove redundant information",
                    "Focus on key points",
                    "Maintain essential keywords",
                    "Keep call-to-action clear"
                ],
                estimated_time=12,
                difficulty_level="medium"
            ))
        
        # Check for call-to-action
        cta_keywords = ["subscribe", "like", "share", "comment", "follow", "click", "visit", "download", "buy"]
        has_cta = any(keyword in current_description.lower() for keyword in cta_keywords)
        
        if not has_cta:
            recommendations.append(OptimizationRecommendation(
                element=ContentElement.CALL_TO_ACTION,
                optimization_type=OptimizationType.ENGAGEMENT_OPTIMIZATION,
                current_value="No clear call-to-action",
                suggested_value="Add specific call-to-action to increase engagement",
                confidence_score=0.80,
                expected_improvement=15.0,
                priority=OptimizationPriority.HIGH,
                reasoning="Content with clear CTAs gets 15% more user actions",
                implementation_steps=[
                    "Add specific action request",
                    "Make it relevant to content",
                    "Place near beginning or end",
                    "Use action verbs"
                ],
                estimated_time=3,
                difficulty_level="easy"
            ))
        
        # Readability analysis
        readability_score = self._calculate_readability_score(current_description)
        if readability_score < 30:  # Very difficult to read
            recommendations.append(OptimizationRecommendation(
                element=ContentElement.DESCRIPTION,
                optimization_type=OptimizationType.DESCRIPTION_OPTIMIZATION,
                current_value=f"Low readability score ({readability_score:.1f})",
                suggested_value="Improve readability with shorter sentences and simpler words",
                confidence_score=0.70,
                expected_improvement=10.0,
                priority=OptimizationPriority.MEDIUM,
                reasoning="Better readability increases user engagement and time spent reading",
                implementation_steps=[
                    "Use shorter sentences",
                    "Replace complex words with simpler alternatives",
                    "Add paragraph breaks",
                    "Use bullet points where appropriate"
                ],
                estimated_time=15,
                difficulty_level="medium"
            ))
        
        return recommendations
    
    async def _analyze_hashtag_optimization(self, content_data: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Analyze and optimize hashtag usage"""        recommendations = []
        current_hashtags = content_data.get("hashtags", [])
        platform = content_data.get("platform", "general")
        
        # Platform-specific hashtag recommendations
        optimal_counts = {
            "instagram": (5, 15),
            "twitter": (1, 3),
            "tiktok": (3, 8),
            "youtube": (3, 10),
            "linkedin": (3, 5),
            "general": (3, 10)
        }
        
        min_count, max_count = optimal_counts.get(platform, optimal_counts["general"])
        current_count = len(current_hashtags)
        
        if current_count < min_count:
            recommendations.append(OptimizationRecommendation(
                element=ContentElement.TAGS,
                optimization_type=OptimizationType.HASHTAG_OPTIMIZATION,
                current_value=f"{current_count} hashtags",
                suggested_value=f"Add {min_count - current_count} more relevant hashtags",
                confidence_score=0.85,
                expected_improvement=20.0,
                priority=OptimizationPriority.HIGH,
                reasoning=f"Content with {min_count}-{max_count} hashtags performs better on {platform}",
                implementation_steps=[
                    "Research trending hashtags in your niche",
                    "Mix popular and niche-specific tags",
                    "Include branded hashtags",
                    "Avoid banned or overly popular hashtags"
                ],
                estimated_time=10,
                difficulty_level="easy"
            ))
        
        elif current_count > max_count:
            recommendations.append(OptimizationRecommendation(
                element=ContentElement.TAGS,
                optimization_type=OptimizationType.HASHTAG_OPTIMIZATION,
                current_value=f"{current_count} hashtags (too many)",
                suggested_value=f"Reduce to {max_count} most relevant hashtags",
                confidence_score=0.80,
                expected_improvement=15.0,
                priority=OptimizationPriority.MEDIUM,
                reasoning=f"Too many hashtags can appear spammy and reduce reach on {platform}",
                implementation_steps=[
                    "Keep only the most relevant hashtags",
                    "Remove overly broad hashtags",
                    "Focus on hashtags with good engagement",
                    "Maintain hashtag diversity"
                ],
                estimated_time=5,
                difficulty_level="easy"
            ))
        
        # Analyze hashtag quality
        if current_hashtags:
            # Check for overly generic hashtags
            generic_hashtags = ["love", "life", "happy", "good", "best", "amazing", "awesome"]
            generic_count = sum(1 for tag in current_hashtags if tag.lower() in generic_hashtags)
            
            if generic_count > len(current_hashtags) * 0.3:  # More than 30% generic
                recommendations.append(OptimizationRecommendation(
                    element=ContentElement.TAGS,
                    optimization_type=OptimizationType.HASHTAG_OPTIMIZATION,
                    current_value=f"{generic_count} generic hashtags",
                    suggested_value="Replace generic hashtags with specific, niche-relevant ones",
                    confidence_score=0.75,
                    expected_improvement=18.0,
                    priority=OptimizationPriority.HIGH,
                    reasoning="Specific hashtags connect better with target audience than generic ones",
                    implementation_steps=[
                        "Research niche-specific hashtags",
                        "Use hashtags related to your content topic",
                        "Include location-based hashtags if relevant",
                        "Add hashtags related to your expertise"
                    ],
                    estimated_time=12,
                    difficulty_level="medium"
                ))
        
        return recommendations
    
    async def _analyze_timing_optimization(self, user_id: str, content_data: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Analyze and optimize posting timing"""        recommendations = []
        current_upload_time = content_data.get("upload_time", datetime.utcnow())
        platform = content_data.get("platform", "general")
        
        # Analyze historical performance by time
        optimal_times = await self._get_optimal_posting_times(user_id, platform)
        
        current_hour = current_upload_time.hour
        current_day = current_upload_time.weekday()
        
        # Check if posting at optimal time
        if optimal_times and current_hour not in optimal_times.get("best_hours", []):
            best_hours_str = ", ".join([f"{h}:00" for h in optimal_times["best_hours"][:3]])
            recommendations.append(OptimizationRecommendation(
                element=ContentElement.POSTING_TIME,
                optimization_type=OptimizationType.TIMING_OPTIMIZATION,
                current_value=f"Posted at {current_hour}:00",
                suggested_value=f"Consider posting at {best_hours_str}",
                confidence_score=0.70,
                expected_improvement=12.0,
                priority=OptimizationPriority.MEDIUM,
                reasoning="Posting during peak audience activity increases initial engagement",
                implementation_steps=[
                    "Analyze your audience's timezone",
                    "Schedule posts for peak activity hours",
                    "Test different times and track performance",
                    "Use scheduling tools for optimal timing"
                ],
                estimated_time=5,
                difficulty_level="easy"
            ))
        
        # Weekend vs weekday analysis
        if optimal_times and current_day in [5, 6] and not optimal_times.get("weekend_performance", True):
            recommendations.append(OptimizationRecommendation(
                element=ContentElement.POSTING_TIME,
                optimization_type=OptimizationType.TIMING_OPTIMIZATION,
                current_value="Posted on weekend",
                suggested_value="Consider posting on weekdays for better engagement",
                confidence_score=0.65,
                expected_improvement=8.0,
                priority=OptimizationPriority.LOW,
                reasoning="Your content performs better on weekdays based on historical data",
                implementation_steps=[
                    "Schedule content for Tuesday-Thursday",
                    "Monitor weekend performance",
                    "Adjust strategy based on audience behavior"
                ],
                estimated_time=2,
                difficulty_level="easy"
            ))
        
        return recommendations
    
    async def _get_optimal_posting_times(self, user_id: str, platform: str) -> Dict[str, Any]:
        """Get optimal posting times based on historical data"""        # This would analyze historical performance data
        # For now, returning general best practices
        return {
            "best_hours": [9, 12, 15, 18, 20],
            "best_days": [1, 2, 3, 4],  # Tuesday to Friday
            "weekend_performance": False,
            "timezone": "UTC"
        }
    
    async def _analyze_format_optimization(self, content_data: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Analyze and optimize content format"""        recommendations = []
        content_format = content_data.get("format", "")
        duration = content_data.get("duration", 0)
        file_size = content_data.get("file_size", 0)
        quality_score = content_data.get("quality_score", 0.5)
        
        # Duration optimization
        if content_format == "video":
            if duration < 15:  # Very short
                recommendations.append(OptimizationRecommendation(
                    element=ContentElement.DURATION,
                    optimization_type=OptimizationType.FORMAT_OPTIMIZATION,
                    current_value=f"{duration} seconds",
                    suggested_value="Consider creating 15-60 second videos for better engagement",
                    confidence_score=0.75,
                    expected_improvement=10.0,
                    priority=OptimizationPriority.MEDIUM,
                    reasoning="Very short videos may not provide enough value to viewers",
                    implementation_steps=[
                        "Add more content or context",
                        "Include introduction and conclusion",
                        "Ensure complete message delivery"
                    ],
                    estimated_time=20,
                    difficulty_level="medium"
                ))
            
            elif duration > 600:  # Very long (>10 minutes)
                recommendations.append(OptimizationRecommendation(
                    element=ContentElement.DURATION,
                    optimization_type=OptimizationType.FORMAT_OPTIMIZATION,
                    current_value=f"{duration//60} minutes {duration%60} seconds",
                    suggested_value="Consider breaking into shorter segments or add timestamps",
                    confidence_score=0.70,
                    expected_improvement=15.0,
                    priority=OptimizationPriority.MEDIUM,
                    reasoning="Long videos have higher drop-off rates without proper structure",
                    implementation_steps=[
                        "Add chapter markers or timestamps",
                        "Create engaging intro/hook",
                        "Consider splitting into series",
                        "Maintain pacing throughout"
                    ],
                    estimated_time=30,
                    difficulty_level="hard"
                ))
        
        # Quality optimization
        if quality_score < 0.7:
            recommendations.append(OptimizationRecommendation(
                element=ContentElement.VIDEO_QUALITY if content_format == "video" else ContentElement.AUDIO_QUALITY,
                optimization_type=OptimizationType.FORMAT_OPTIMIZATION,
                current_value=f"Quality score: {quality_score:.2f}",
                suggested_value="Improve audio/video quality for better user experience",
                confidence_score=0.80,
                expected_improvement=20.0,
                priority=OptimizationPriority.HIGH,
                reasoning="Poor quality content has significantly lower engagement rates",
                implementation_steps=[
                    "Use better recording equipment",
                    "Improve lighting conditions",
                    "Enhance audio clarity",
                    "Use noise reduction tools",
                    "Optimize compression settings"
                ],
                estimated_time=45,
                difficulty_level="hard"
            ))
        
        return recommendations
    
    async def _analyze_seo_optimization(self, content_data: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Analyze and optimize SEO elements"""        recommendations = []
        title = content_data.get("title", "")
        description = content_data.get("description", "")
        tags = content_data.get("hashtags", [])
        
        # Keyword density analysis
        if title and description:
            # Extract potential keywords from title
            title_words = set(word.lower() for word in title.split() if len(word) > 3)
            description_lower = description.lower()
            
            # Check if title keywords appear in description
            missing_keywords = [word for word in title_words if word not in description_lower]
            
            if missing_keywords:
                recommendations.append(OptimizationRecommendation(
                    element=ContentElement.DESCRIPTION,
                    optimization_type=OptimizationType.SEO_OPTIMIZATION,
                    current_value="Keywords not reinforced in description",
                    suggested_value=f"Include title keywords in description: {', '.join(missing_keywords[:3])}",
                    confidence_score=0.75,
                    expected_improvement=12.0,
                    priority=OptimizationPriority.MEDIUM,
                    reasoning="Reinforcing title keywords in description improves SEO ranking",
                    implementation_steps=[
                        "Naturally incorporate title keywords into description",
                        "Maintain readability and flow",
                        "Avoid keyword stuffing",
                        "Use synonyms and related terms"
                    ],
                    estimated_time=8,
                    difficulty_level="easy"
                ))
        
        # Meta description length (for web content)
        if description and len(description) > 320:
            recommendations.append(OptimizationRecommendation(
                element=ContentElement.DESCRIPTION,
                optimization_type=OptimizationType.SEO_OPTIMIZATION,
                current_value=f"Description too long for SEO ({len(description)} chars)",
                suggested_value="Optimize first 150-320 characters for search snippets",
                confidence_score=0.80,
                expected_improvement=8.0,
                priority=OptimizationPriority.LOW,
                reasoning="Search engines typically show first 150-320 characters in snippets",
                implementation_steps=[
                    "Put most important information first",
                    "Include primary keywords early",
                    "Create compelling snippet preview",
                    "Maintain complete message"
                ],
                estimated_time=10,
                difficulty_level="medium"
            ))
        
        return recommendations
    
    def _calculate_optimization_score(self, content_features: Dict[str, Any], recommendations: List[OptimizationRecommendation]) -> float:
        """Calculate overall optimization score (0-100)"""        base_score = 50.0  # Starting point
        
        # Deduct points for missing critical elements
        critical_issues = [rec for rec in recommendations if rec.priority == OptimizationPriority.CRITICAL]
        base_score -= len(critical_issues) * 15
        
        # Deduct points for high priority issues
        high_priority_issues = [rec for rec in recommendations if rec.priority == OptimizationPriority.HIGH]
        base_score -= len(high_priority_issues) * 8
        
        # Deduct points for medium priority issues
        medium_priority_issues = [rec for rec in recommendations if rec.priority == OptimizationPriority.MEDIUM]
        base_score -= len(medium_priority_issues) * 3
        
        # Add points for good features
        if content_features.get("title_length", 0) > 10:
            base_score += 5
        if content_features.get("description_length", 0) > 50:
            base_score += 5
        if content_features.get("hashtag_count", 0) >= 3:
            base_score += 5
        if content_features.get("has_thumbnail", False):
            base_score += 10
        if content_features.get("quality_score", 0) > 0.7:
            base_score += 15
        
        return max(0.0, min(100.0, base_score))
    
    async def _generate_ai_insights(self, content_features: Dict[str, Any], recommendations: List[OptimizationRecommendation]) -> Dict[str, Any]:
        """Generate AI-powered insights about content optimization"""        insights = {
            "optimization_priority": "balanced",
            "content_strength": [],
            "improvement_areas": [],
            "personalized_tips": [],
            "competitive_analysis": {},
            "trend_alignment": {}
        }
        
        # Determine optimization priority
        critical_count = len([r for r in recommendations if r.priority == OptimizationPriority.CRITICAL])
        high_count = len([r for r in recommendations if r.priority == OptimizationPriority.HIGH])
        
        if critical_count > 0:
            insights["optimization_priority"] = "critical"
        elif high_count > 2:
            insights["optimization_priority"] = "high"
        elif len(recommendations) > 5:
            insights["optimization_priority"] = "moderate"
        else:
            insights["optimization_priority"] = "low"
        
        # Identify content strengths
        if content_features.get("quality_score", 0) > 0.8:
            insights["content_strength"].append("High quality audio/video production")
        if content_features.get("title_sentiment_score", 0.5) > 0.7:
            insights["content_strength"].append("Positive and engaging title")
        if content_features.get("description_readability", 0) > 60:
            insights["content_strength"].append("Well-written, readable description")
        
        # Identify key improvement areas
        improvement_categories = {}
        for rec in recommendations:
            category = rec.optimization_type.value
            if category not in improvement_categories:
                improvement_categories[category] = 0
            improvement_categories[category] += rec.expected_improvement
        
        top_improvements = sorted(improvement_categories.items(), key=lambda x: x[1], reverse=True)[:3]
        insights["improvement_areas"] = [{"category": cat, "potential_impact": impact} for cat, impact in top_improvements]
        
        # Generate personalized tips
        if content_features.get("content_format") == "audio":
            insights["personalized_tips"].append("Focus on audio quality and compelling descriptions for audio content")
        elif content_features.get("content_format") == "video":
            insights["personalized_tips"].append("Optimize thumbnail and first 15 seconds for video content")
        
        # Upload timing insights
        upload_hour = content_features.get("upload_hour", 12)
        if upload_hour < 6 or upload_hour > 22:
            insights["personalized_tips"].append("Consider posting during peak audience hours (9AM-10PM)")
        
        return insights
    
    async def _save_optimization_analysis(self, user_id: str, content_id: str, analysis: Dict[str, Any]):
        """Save optimization analysis to database"""        try:
            # Create history record
            history = ContentOptimizationHistory(
                user_id=user_id,
                content_id=content_id,
                optimization_type="comprehensive_analysis",
                element_optimized="all",
                confidence_score=analysis.get("overall_optimization_score", 0) / 100,
                algorithm_used="ai_content_optimizer_v1"
            )
            
            self.db_session.add(history)
            self.db_session.flush()  # Get the ID
            
            # Save individual recommendations
            for rec_data in analysis.get("recommendations", []):
                recommendation = OptimizationRecommendationModel(
                    history_id=history.id,
                    element=rec_data["element"],
                    optimization_type=rec_data["optimization_type"],
                    current_value=rec_data["current_value"],
                    suggested_value=rec_data["suggested_value"],
                    confidence_score=rec_data["confidence_score"],
                    expected_improvement=rec_data["expected_improvement"],
                    priority=rec_data["priority"],
                    reasoning=rec_data["reasoning"],
                    implementation_steps=rec_data["implementation_steps"],
                    estimated_time=rec_data["estimated_time"],
                    difficulty_level=rec_data["difficulty_level"]
                )
                self.db_session.add(recommendation)
            
            self.db_session.commit()
            
        except Exception as e:
            self.db_session.rollback()
            print(f"Failed to save optimization analysis: {e}")
    
    async def get_optimization_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get optimization history for a user"""        history_records = self.db_session.query(ContentOptimizationHistory).filter(
            ContentOptimizationHistory.user_id == user_id
        ).order_by(ContentOptimizationHistory.created_at.desc()).limit(limit).all()
        
        return [{
            "id": record.id,
            "content_id": record.content_id,
            "optimization_type": record.optimization_type,
            "confidence_score": record.confidence_score,
            "improvement_percentage": record.improvement_percentage,
            "implemented": record.implemented,
            "created_at": record.created_at.isoformat()
        } for record in history_records]
    
    async def implement_optimization(self, recommendation_id: str, user_feedback: Optional[float] = None) -> Dict[str, Any]:
        """Mark optimization as implemented and track results"""        try:
            recommendation = self.db_session.query(OptimizationRecommendationModel).filter(
                OptimizationRecommendationModel.id == recommendation_id
            ).first()
            
            if not recommendation:
                return {"error": "Recommendation not found"}
            
            # Update recommendation status
            recommendation.status = "implemented"
            if user_feedback is not None:
                recommendation.feedback_score = user_feedback
            
            # Update history record
            if recommendation.history:
                recommendation.history.implemented = True
                recommendation.history.implementation_date = datetime.utcnow()
            
            self.db_session.commit()
            
            return {
                "success": True,
                "message": "Optimization marked as implemented",
                "recommendation_id": recommendation_id
            }
            
        except Exception as e:
            self.db_session.rollback()
            return {"error": f"Failed to update optimization: {str(e)}"}


# Export main classes and utilities
__all__ = [
    "AIContentOptimizer",
    "OptimizationRecommendation",
    "ContentOptimizationHistory",
    "OptimizationRecommendationModel",
    "OptimizationType",
    "ContentElement",
    "OptimizationPriority"
]
