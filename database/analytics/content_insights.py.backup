"""Content Insights Module - IA Influencer Agent + Content Protection Platform

Advanced content analysis and insights system for multi-format content creators with
AI-powered content optimization, trend analysis, and performance prediction.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""
import uuid
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Index, BigInteger, Numeric, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import logging
import numpy as np
from collections import defaultdict, Counter
import statistics
import re

Base = declarative_base()
logger = logging.getLogger(__name__)


class ContentCategory(Enum):
    """Content category types"""
    MUSIC = "music"
    VIDEO = "video"
    PHOTO = "photo"
    BLOG_POST = "blog_post"
    PODCAST = "podcast"
    STORY = "story"
    REEL = "reel"
    LIVE_STREAM = "live_stream"
    TUTORIAL = "tutorial"
    BEHIND_SCENES = "behind_scenes"


class TrendStatus(Enum):
    """Trend status types"""
    EMERGING = "emerging"
    TRENDING = "trending"
    STABLE = "stable"
    DECLINING = "declining"
    VIRAL = "viral"


class ContentElement(Enum):
    """Content element types for analysis"""
    HASHTAGS = "hashtags"
    MENTIONS = "mentions"
    LOCATION = "location"
    MUSIC_TRACK = "music_track"
    VISUAL_STYLE = "visual_style"
    CAPTION_STYLE = "caption_style"
    CALL_TO_ACTION = "call_to_action"
    BRAND_ELEMENTS = "brand_elements"


class ContentInsightModel(Base):
    """
    Enterprise-grade content insights model
    
    Stores comprehensive content analysis data with AI-powered insights
    for content optimization and performance prediction.
    """
    __tablename__ = "content_insights"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False, index=True)
    content_id = Column(String(255), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)
    
    # Content metadata
    content_type = Column(String(50), nullable=False)
    content_category = Column(String(50))
    content_title = Column(Text)
    content_description = Column(Text)
    content_url = Column(Text)
    
    # Performance metrics
    views = Column(BigInteger, default=0)
    likes = Column(BigInteger, default=0)
    comments = Column(BigInteger, default=0)
    shares = Column(BigInteger, default=0)
    saves = Column(BigInteger, default=0)
    engagement_rate = Column(Numeric(10, 6))
    reach = Column(BigInteger, default=0)
    impressions = Column(BigInteger, default=0)
    
    # Content analysis
    content_elements = Column(JSON)  # Hashtags, mentions, music, etc.
    visual_features = Column(JSON)   # Colors, composition, style
    audio_features = Column(JSON)    # For music/video content
    text_analysis = Column(JSON)     # Caption analysis, keywords
    
    # AI insights
    ai_content_score = Column(Numeric(5, 2))
    ai_virality_prediction = Column(Numeric(5, 2))
    ai_optimization_suggestions = Column(JSON)
    ai_trend_alignment = Column(Numeric(5, 2))
    ai_audience_match = Column(Numeric(5, 2))
    
    # Trend analysis
    trend_score = Column(Numeric(10, 4))
    trend_keywords = Column(ARRAY(Text))
    trend_category = Column(String(50))
    trend_momentum = Column(Numeric(8, 4))
    
    # Performance benchmarking
    industry_percentile = Column(Numeric(5, 2))
    competitor_comparison = Column(JSON)
    historical_performance = Column(JSON)
    
    # Time-based analysis
    publication_timestamp = Column(DateTime(timezone=True), nullable=False)
    analysis_timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    performance_lifecycle_stage = Column(String(20))  # growth, peak, decline
    
    # Optimization tracking
    optimization_applied = Column(JSON)
    optimization_results = Column(JSON)
    next_optimization_suggestions = Column(JSON)
    
    # Metadata
    data_source = Column(String(100))
    confidence_score = Column(Numeric(5, 2))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_content_user_platform', 'user_id', 'platform'),
        Index('idx_content_category_trend', 'content_category', 'trend_score'),
        Index('idx_content_performance', 'engagement_rate', 'ai_content_score'),
        Index('idx_content_publication_time', 'publication_timestamp'),
    )


@dataclass
class ContentTrend:
    """Data class for content trends"""
    trend_id: str
    trend_name: str
    trend_category: str
    trend_score: float
    momentum: float
    status: TrendStatus
    related_keywords: List[str]
    estimated_reach: int
    duration_prediction: str
    platforms: List[str]
    demographic_appeal: Dict[str, float]
    content_examples: List[str]
    optimization_tips: List[str]
    risk_level: str  # low, medium, high
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "trend_id": self.trend_id,
            "trend_name": self.trend_name,
            "trend_category": self.trend_category,
            "trend_score": self.trend_score,
            "momentum": self.momentum,
            "status": self.status.value,
            "related_keywords": self.related_keywords,
            "estimated_reach": self.estimated_reach,
            "duration_prediction": self.duration_prediction,
            "platforms": self.platforms,
            "demographic_appeal": self.demographic_appeal,
            "content_examples": self.content_examples,
            "optimization_tips": self.optimization_tips,
            "risk_level": self.risk_level
        }


@dataclass
class ContentOptimizationRecommendation:
    """Data class for content optimization recommendations"""
    recommendation_id: str
    title: str
    description: str
    category: str
    priority: str  # high, medium, low
    expected_impact: float
    implementation_effort: str
    specific_actions: List[str]
    success_metrics: List[str]
    timeline: str
    examples: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "recommendation_id": self.recommendation_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority,
            "expected_impact": self.expected_impact,
            "implementation_effort": self.implementation_effort,
            "specific_actions": self.specific_actions,
            "success_metrics": self.success_metrics,
            "timeline": self.timeline,
            "examples": self.examples
        }


class ContentInsights:
    """
    Enterprise-grade content insights and analysis engine
    
    Provides comprehensive content analysis with AI-powered insights,
    trend detection, and optimization recommendations for content creators.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize content insights analyzer with database session
        
        Args:
            db_session: Database session for analytics operations
        """
        self.db = db_session
        self.logger = logging.getLogger(__name__)
    
    async def analyze_content(
        self,
        user_id: int,
        content_id: str,
        platform: str,
        content_data: Dict[str, Any]
    ) -> ContentInsightModel:
        """
        Perform comprehensive content analysis with AI insights
        
        Args:
            user_id: User identifier
            content_id: Content identifier
            platform: Platform name
            content_data: Content data and metadata
            
        Returns:
            Content insights model with analysis results
        """
        try:
            self.logger.info(f"Analyzing content {content_id} for user {user_id}")
            
            # Extract content elements
            content_elements = await self._extract_content_elements(content_data)
            
            # Analyze visual features (for images/videos)
            visual_features = await self._analyze_visual_features(content_data)
            
            # Analyze audio features (for audio/video content)
            audio_features = await self._analyze_audio_features(content_data)
            
            # Analyze text content
            text_analysis = await self._analyze_text_content(content_data)
            
            # Calculate AI scores
            ai_scores = await self._calculate_ai_scores(
                content_elements, visual_features, audio_features, text_analysis
            )
            
            # Analyze trends
            trend_analysis = await self._analyze_content_trends(content_elements, content_data)
            
            # Generate optimization suggestions
            optimization_suggestions = await self._generate_optimization_suggestions(
                content_elements, ai_scores, trend_analysis
            )
            
            # Create content insights record
            content_insight = ContentInsightModel(
                user_id=user_id,
                content_id=content_id,
                platform=platform,
                content_type=content_data.get("type", "unknown"),
                content_category=content_data.get("category"),
                content_title=content_data.get("title"),
                content_description=content_data.get("description"),
                content_url=content_data.get("url"),
                views=content_data.get("views", 0),
                likes=content_data.get("likes", 0),
                comments=content_data.get("comments", 0),
                shares=content_data.get("shares", 0),
                saves=content_data.get("saves", 0),
                engagement_rate=content_data.get("engagement_rate"),
                reach=content_data.get("reach", 0),
                impressions=content_data.get("impressions", 0),
                content_elements=content_elements,
                visual_features=visual_features,
                audio_features=audio_features,
                text_analysis=text_analysis,
                ai_content_score=ai_scores.get("content_score"),
                ai_virality_prediction=ai_scores.get("virality_prediction"),
                ai_optimization_suggestions=optimization_suggestions,
                ai_trend_alignment=ai_scores.get("trend_alignment"),
                ai_audience_match=ai_scores.get("audience_match"),
                trend_score=trend_analysis.get("trend_score"),
                trend_keywords=trend_analysis.get("keywords", []),
                trend_category=trend_analysis.get("category"),
                trend_momentum=trend_analysis.get("momentum"),
                publication_timestamp=content_data.get("publication_timestamp", datetime.utcnow()),
                performance_lifecycle_stage=content_data.get("lifecycle_stage", "growth"),
                data_source=content_data.get("data_source", "api"),
                confidence_score=0.85
            )
            
            self.db.add(content_insight)
            self.db.commit()
            
            self.logger.info(f"Content analysis completed for {content_id}")
            return content_insight
            
        except Exception as e:
            self.logger.error(f"Failed to analyze content: {str(e)}")
            self.db.rollback()
            raise
    
    async def _extract_content_elements(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and analyze content elements"""
        
        elements = {
            "hashtags": [],
            "mentions": [],
            "locations": [],
            "music_tracks": [],
            "visual_style": {},
            "caption_style": {},
            "call_to_action": {},
            "brand_elements": []
        }
        
        # Extract hashtags from text content
        if content_data.get("caption") or content_data.get("description"):
            text_content = content_data.get("caption", "") + " " + content_data.get("description", "")
            elements["hashtags"] = self._extract_hashtags(text_content)
            elements["mentions"] = self._extract_mentions(text_content)
            elements["call_to_action"] = self._analyze_call_to_action(text_content)
        
        # Extract music information
        if content_data.get("music_info"):
            elements["music_tracks"] = [content_data["music_info"]]
        
        # Extract location information
        if content_data.get("location"):
            elements["locations"] = [content_data["location"]]
        
        # Analyze visual style (simplified)
        if content_data.get("visual_metadata"):
            elements["visual_style"] = self._analyze_visual_style(content_data["visual_metadata"])
        
        return elements
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text content"""
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, text.lower())
        return [tag[1:] for tag in hashtags]  # Remove # symbol
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract user mentions from text content"""
        mention_pattern = r'@\w+'
        mentions = re.findall(mention_pattern, text.lower())
        return [mention[1:] for mention in mentions]  # Remove @ symbol
    
    def _analyze_call_to_action(self, text: str) -> Dict[str, Any]:
        """Analyze call-to-action elements in text"""
        cta_keywords = [
            "click", "link", "bio", "comment", "share", "tag", "follow",
            "subscribe", "like", "save", "swipe", "watch", "listen",
            "visit", "shop", "buy", "download", "sign up"
        ]
        
        text_lower = text.lower()
        found_ctas = [cta for cta in cta_keywords if cta in text_lower]
        
        cta_strength = len(found_ctas) * 0.2  # Simple scoring
        cta_placement = "end" if any(cta in text_lower[-100:] for cta in found_ctas) else "beginning"
        
        return {
            "cta_keywords": found_ctas,
            "cta_strength": min(1.0, cta_strength),
            "cta_placement": cta_placement,
            "has_multiple_ctas": len(found_ctas) > 2
        }
    
    async def _analyze_visual_features(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze visual features of content"""
        
        visual_features = {
            "dominant_colors": [],
            "composition": {},
            "style_elements": {},
            "quality_score": 0.0,
            "visual_complexity": 0.0
        }
        
        # Placeholder for actual computer vision analysis
        # In a real implementation, this would use CV libraries like OpenCV, PIL
        if content_data.get("image_url") or content_data.get("video_url"):
            # Simulated analysis
            visual_features = {
                "dominant_colors": ["blue", "white", "gold"],
                "composition": {
                    "rule_of_thirds": True,
                    "symmetry": False,
                    "leading_lines": True
                },
                "style_elements": {
                    "filter_style": "natural",
                    "brightness": "high",
                    "contrast": "medium",
                    "saturation": "medium"
                },
                "quality_score": 8.5,
                "visual_complexity": 6.2
            }
        
        return visual_features
    
    async def _analyze_audio_features(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze audio features for music/video content"""
        
        audio_features = {
            "tempo": 0,
            "key": None,
            "genre": None,
            "mood": None,
            "energy_level": 0.0,
            "audio_quality": 0.0
        }
        
        # Placeholder for actual audio analysis
        # In a real implementation, this would use audio processing libraries
        if content_data.get("audio_url") or content_data.get("music_info"):
            # Simulated analysis
            audio_features = {
                "tempo": 120,
                "key": "C major",
                "genre": "pop",
                "mood": "upbeat",
                "energy_level": 7.8,
                "audio_quality": 9.2
            }
        
        return audio_features
    
    async def _analyze_text_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze text content with NLP"""
        
        text_analysis = {
            "word_count": 0,
            "readability_score": 0.0,
            "sentiment_score": 0.0,
            "key_topics": [],
            "language_style": "casual",
            "emoji_usage": 0,
            "question_count": 0
        }
        
        # Get text content
        text_content = ""
        if content_data.get("caption"):
            text_content += content_data["caption"]
        if content_data.get("description"):
            text_content += " " + content_data["description"]
        
        if text_content.strip():
            # Basic text analysis
            words = text_content.split()
            text_analysis["word_count"] = len(words)
            text_analysis["emoji_usage"] = len(re.findall(r'[^\w\s,]', text_content))
            text_analysis["question_count"] = text_content.count("?")
            
            # Simulated advanced analysis (would use NLP libraries in real implementation)
            text_analysis.update({
                "readability_score": 7.5,
                "sentiment_score": 0.6,  # Positive sentiment
                "key_topics": ["lifestyle", "inspiration", "creativity"],
                "language_style": "casual" if len(words) < 50 else "formal"
            })
        
        return text_analysis
    
    async def _calculate_ai_scores(
        self,
        content_elements: Dict[str, Any],
        visual_features: Dict[str, Any],
        audio_features: Dict[str, Any],
        text_analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate AI-powered content scores"""
        
        # Content quality score (0-10)
        content_score = 0.0
        
        # Visual quality contribution (40%)
        if visual_features.get("quality_score"):
            content_score += visual_features["quality_score"] * 0.4
        
        # Text quality contribution (30%)
        if text_analysis.get("readability_score"):
            content_score += text_analysis["readability_score"] * 0.3
        
        # Audio quality contribution (20%)
        if audio_features.get("audio_quality"):
            content_score += audio_features["audio_quality"] * 0.2
        
        # Elements quality contribution (10%)
        hashtag_quality = min(1.0, len(content_elements.get("hashtags", [])) / 10) * 10
        cta_quality = content_elements.get("call_to_action", {}).get("cta_strength", 0) * 10
        element_score = (hashtag_quality + cta_quality) / 2
        content_score += element_score * 0.1
        
        # Virality prediction (0-10)
        virality_factors = []
        
        # Trend alignment
        hashtag_trend_score = self._calculate_hashtag_trend_score(content_elements.get("hashtags", []))
        virality_factors.append(hashtag_trend_score)
        
        # Emotional appeal
        sentiment_impact = abs(text_analysis.get("sentiment_score", 0)) * 5
        virality_factors.append(sentiment_impact)
        
        # Visual appeal
        visual_appeal = visual_features.get("quality_score", 0)
        virality_factors.append(visual_appeal)
        
        # Engagement potential
        cta_strength = content_elements.get("call_to_action", {}).get("cta_strength", 0) * 10
        virality_factors.append(cta_strength)
        
        virality_prediction = statistics.mean(virality_factors) if virality_factors else 0
        
        # Trend alignment score
        trend_alignment = hashtag_trend_score
        
        # Audience match score (simplified)
        audience_match = (content_score + virality_prediction) / 2
        
        return {
            "content_score": content_score,
            "virality_prediction": virality_prediction,
            "trend_alignment": trend_alignment,
            "audience_match": audience_match
        }
    
    def _calculate_hashtag_trend_score(self, hashtags: List[str]) -> float:
        """Calculate trend alignment score based on hashtags"""
        # Simulated trending hashtag database
        trending_hashtags = {
            "viral", "trending", "fyp", "explore", "reels", "love", "instagood",
            "photooftheday", "beautiful", "happy", "fashion", "art", "music"
        }
        
        if not hashtags:
            return 0.0
        
        trending_count = sum(1 for tag in hashtags if tag in trending_hashtags)
        trend_score = (trending_count / len(hashtags)) * 10
        
        return min(10.0, trend_score)
    
    async def _analyze_content_trends(
        self,
        content_elements: Dict[str, Any],
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze content alignment with current trends"""
        
        trend_analysis = {
            "trend_score": 0.0,
            "keywords": [],
            "category": "general",
            "momentum": 0.0
        }
        
        # Analyze hashtag trends
        hashtags = content_elements.get("hashtags", [])
        if hashtags:
            trend_analysis["keywords"] = hashtags
            trend_analysis["trend_score"] = self._calculate_hashtag_trend_score(hashtags)
        
        # Determine content category
        if content_data.get("type"):
            trend_analysis["category"] = content_data["type"]
        
        # Calculate momentum (simplified)
        recent_performance = content_data.get("recent_performance", {})
        if recent_performance:
            momentum = recent_performance.get("growth_rate", 0) * 2
            trend_analysis["momentum"] = min(10.0, max(0.0, momentum))
        
        return trend_analysis
    
    async def _generate_optimization_suggestions(
        self,
        content_elements: Dict[str, Any],
        ai_scores: Dict[str, float],
        trend_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered optimization suggestions"""
        
        suggestions = []
        
        # Hashtag optimization
        hashtag_count = len(content_elements.get("hashtags", []))
        if hashtag_count < 5:
            suggestions.append({
                "category": "hashtags",
                "priority": "high",
                "suggestion": "Add more relevant hashtags",
                "details": f"Current: {hashtag_count} hashtags. Recommended: 8-15 for optimal reach.",
                "expected_impact": "15-25% increase in discoverability"
            })
        elif hashtag_count > 20:
            suggestions.append({
                "category": "hashtags",
                "priority": "medium",
                "suggestion": "Reduce hashtag count for better engagement",
                "details": f"Current: {hashtag_count} hashtags. Recommended: 8-15 for optimal engagement.",
                "expected_impact": "10-15% improvement in engagement rate"
            })
        
        # Call-to-action optimization
        cta_strength = content_elements.get("call_to_action", {}).get("cta_strength", 0)
        if cta_strength < 0.3:
            suggestions.append({
                "category": "engagement",
                "priority": "high",
                "suggestion": "Add clear call-to-action",
                "details": "Include specific instructions like 'Comment below', 'Share if you agree', or 'Tag a friend'.",
                "expected_impact": "20-35% increase in engagement"
            })
        
        # Content quality optimization
        content_score = ai_scores.get("content_score", 0)
        if content_score < 6:
            suggestions.append({
                "category": "quality",
                "priority": "high",
                "suggestion": "Improve content production quality",
                "details": "Focus on better lighting, composition, and audio quality.",
                "expected_impact": "25-40% improvement in performance"
            })
        
        # Trend alignment optimization
        trend_score = trend_analysis.get("trend_score", 0)
        if trend_score < 3:
            suggestions.append({
                "category": "trends",
                "priority": "medium",
                "suggestion": "Align with current trends",
                "details": "Research and incorporate trending hashtags and themes relevant to your niche.",
                "expected_impact": "30-50% increase in reach"
            })
        
        return suggestions
    
    async def get_content_insights(
        self,
        user_id: int,
        days_back: int = 30,
        limit: int = 20
    ) -> List[ContentInsightModel]:
        """
        Get content insights for user within specified timeframe
        
        Args:
            user_id: User identifier
            days_back: Number of days to look back
            limit: Maximum number of insights to return
            
        Returns:
            List of content insights
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days_back)
            
            insights = self.db.query(ContentInsightModel).filter(
                ContentInsightModel.user_id == user_id,
                ContentInsightModel.analysis_timestamp >= start_date
            ).order_by(
                ContentInsightModel.analysis_timestamp.desc()
            ).limit(limit).all()
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Failed to get content insights: {str(e)}")
            raise


class TrendAnalyzer:
    """
    Enterprise-grade trend analysis engine
    
    Provides comprehensive trend detection, analysis, and prediction
    capabilities for content optimization and strategy planning.
    """
    
    def __init__(self, db_session: Session):
        """Initialize trend analyzer with database session"""
        self.db = db_session
        self.logger = logging.getLogger(__name__)
    
    async def detect_emerging_trends(
        self,
        platform: Optional[str] = None,
        category: Optional[str] = None,
        timeframe_hours: int = 24
    ) -> List[ContentTrend]:
        """
        Detect emerging trends across platforms and categories
        
        Args:
            platform: Specific platform filter
            category: Content category filter
            timeframe_hours: Analysis timeframe in hours
            
        Returns:
            List of detected trends
        """
        try:
            # Build query filters
            filters = []
            start_time = datetime.utcnow() - timedelta(hours=timeframe_hours)
            filters.append(ContentInsightModel.analysis_timestamp >= start_time)
            
            if platform:
                filters.append(ContentInsightModel.platform == platform)
            if category:
                filters.append(ContentInsightModel.content_category == category)
            
            # Get recent content data
            recent_content = self.db.query(ContentInsightModel).filter(*filters).all()
            
            if not recent_content:
                return []
            
            # Analyze hashtag trends
            hashtag_trends = await self._analyze_hashtag_trends(recent_content)
            
            # Analyze content type trends
            content_type_trends = await self._analyze_content_type_trends(recent_content)
            
            # Analyze performance trends
            performance_trends = await self._analyze_performance_trends(recent_content)
            
            # Combine and rank trends
            all_trends = hashtag_trends + content_type_trends + performance_trends
            
            # Sort by trend score and momentum
            ranked_trends = sorted(
                all_trends, 
                key=lambda t: (t.trend_score * t.momentum), 
                reverse=True
            )
            
            return ranked_trends[:20]  # Return top 20 trends
            
        except Exception as e:
            self.logger.error(f"Failed to detect emerging trends: {str(e)}")
            raise
    
    async def _analyze_hashtag_trends(self, content_data: List[ContentInsightModel]) -> List[ContentTrend]:
        """Analyze hashtag usage trends"""
        
        hashtag_usage = defaultdict(list)
        hashtag_performance = defaultdict(list)
        
        for content in content_data:
            if content.trend_keywords:
                for hashtag in content.trend_keywords:
                    hashtag_usage[hashtag].append(content.analysis_timestamp)
                    if content.engagement_rate:
                        hashtag_performance[hashtag].append(float(content.engagement_rate))
        
        trends = []
        
        for hashtag, timestamps in hashtag_usage.items():
            if len(timestamps) < 5:  # Need minimum usage
                continue
            
            # Calculate trend metrics
            usage_count = len(timestamps)
            performance_avg = statistics.mean(hashtag_performance.get(hashtag, [0]))
            
            # Calculate momentum (usage frequency over time)
            recent_usage = len([t for t in timestamps if t >= datetime.utcnow() - timedelta(hours=6)])
            momentum = recent_usage / max(1, usage_count) * 10
            
            # Determine trend status
            if momentum > 7:
                status = TrendStatus.VIRAL
            elif momentum > 5:
                status = TrendStatus.TRENDING
            elif momentum > 3:
                status = TrendStatus.EMERGING
            else:
                status = TrendStatus.STABLE
            
            trend = ContentTrend(
                trend_id=f"hashtag_{hashtag}",
                trend_name=f"#{hashtag}",
                trend_category="hashtag",
                trend_score=performance_avg * 100,
                momentum=momentum,
                status=status,
                related_keywords=[hashtag],
                estimated_reach=usage_count * 1000,  # Estimated
                duration_prediction="3-7 days",
                platforms=["instagram", "tiktok", "twitter"],  # Simplified
                demographic_appeal={"18-24": 0.4, "25-34": 0.35, "35-44": 0.25},
                content_examples=[],
                optimization_tips=[
                    f"Use #{hashtag} in relevant content",
                    "Post during peak hours",
                    "Combine with complementary hashtags"
                ],
                risk_level="low" if status in [TrendStatus.STABLE, TrendStatus.EMERGING] else "medium"
            )
            
            trends.append(trend)
        
        return trends
    
    async def _analyze_content_type_trends(self, content_data: List[ContentInsightModel]) -> List[ContentTrend]:
        """Analyze content type performance trends"""
        
        content_type_performance = defaultdict(list)
        content_type_usage = defaultdict(int)
        
        for content in content_data:
            content_type = content.content_type
            content_type_usage[content_type] += 1
            
            if content.engagement_rate:
                content_type_performance[content_type].append(float(content.engagement_rate))
        
        trends = []
        
        for content_type, performances in content_type_performance.items():
            if len(performances) < 3:  # Need minimum data
                continue
            
            avg_performance = statistics.mean(performances)
            usage_count = content_type_usage[content_type]
            
            # Calculate trend score based on performance and adoption
            trend_score = avg_performance * 100 * (1 + (usage_count / 100))
            momentum = min(10, usage_count / 5)  # Normalize momentum
            
            # Determine status
            if avg_performance > 0.05:  # 5% engagement rate threshold
                status = TrendStatus.TRENDING
            elif avg_performance > 0.03:
                status = TrendStatus.EMERGING
            else:
                status = TrendStatus.STABLE
            
            trend = ContentTrend(
                trend_id=f"content_type_{content_type}",
                trend_name=f"{content_type.title()} Content",
                trend_category="content_type",
                trend_score=trend_score,
                momentum=momentum,
                status=status,
                related_keywords=[content_type],
                estimated_reach=usage_count * 2000,
                duration_prediction="1-2 weeks",
                platforms=["instagram", "tiktok", "youtube"],
                demographic_appeal={"all_ages": 1.0},
                content_examples=[],
                optimization_tips=[
                    f"Create more {content_type} content",
                    "Focus on high-quality production",
                    "Test different variations"
                ],
                risk_level="low"
            )
            
            trends.append(trend)
        
        return trends
    
    async def _analyze_performance_trends(self, content_data: List[ContentInsightModel]) -> List[ContentTrend]:
        """Analyze overall performance trends"""
        
        trends = []
        
        # Analyze engagement rate trends over time
        time_buckets = defaultdict(list)
        
        for content in content_data:
            if content.engagement_rate:
                # Group by hour buckets
                hour_bucket = content.analysis_timestamp.replace(minute=0, second=0, microsecond=0)
                time_buckets[hour_bucket].append(float(content.engagement_rate))
        
        if len(time_buckets) >= 3:  # Need minimum time points
            # Calculate trend direction
            sorted_times = sorted(time_buckets.keys())
            early_performance = statistics.mean(time_buckets[sorted_times[0]])
            recent_performance = statistics.mean(time_buckets[sorted_times[-1]])
            
            performance_change = (recent_performance - early_performance) / early_performance * 100 if early_performance > 0 else 0
            
            if abs(performance_change) > 10:  # Significant change
                if performance_change > 0:
                    trend_name = "Rising Engagement Trend"
                    status = TrendStatus.TRENDING
                    optimization_tips = [
                        "Maintain current content strategy",
                        "Increase posting frequency",
                        "Analyze successful content elements"
                    ]
                else:
                    trend_name = "Declining Engagement Trend"
                    status = TrendStatus.DECLINING
                    optimization_tips = [
                        "Review recent content strategy",
                        "Test new content formats",
                        "Analyze audience feedback"
                    ]
                
                trend = ContentTrend(
                    trend_id="engagement_trend",
                    trend_name=trend_name,
                    trend_category="performance",
                    trend_score=abs(performance_change),
                    momentum=min(10, abs(performance_change) / 5),
                    status=status,
                    related_keywords=["engagement", "performance"],
                    estimated_reach=len(content_data) * 1500,
                    duration_prediction="ongoing",
                    platforms=["all"],
                    demographic_appeal={"all_ages": 1.0},
                    content_examples=[],
                    optimization_tips=optimization_tips,
                    risk_level="medium" if performance_change < 0 else "low"
                )
                
                trends.append(trend)
        
        return trends
    
    async def get_trend_recommendations(
        self,
        user_id: int,
        content_category: Optional[str] = None
    ) -> List[ContentOptimizationRecommendation]:
        """
        Get personalized trend-based recommendations for user
        
        Args:
            user_id: User identifier
            content_category: Specific content category
            
        Returns:
            List of optimization recommendations
        """
        try:
            # Get current trends
            current_trends = await self.detect_emerging_trends(
                category=content_category,
                timeframe_hours=48
            )
            
            # Get user's recent content performance
            user_content = await self._get_user_recent_content(user_id)
            
            # Generate personalized recommendations
            recommendations = []
            
            # Trend alignment recommendations
            for trend in current_trends[:5]:  # Top 5 trends
                if trend.status in [TrendStatus.EMERGING, TrendStatus.TRENDING]:
                    rec = ContentOptimizationRecommendation(
                        recommendation_id=f"trend_{trend.trend_id}",
                        title=f"Capitalize on {trend.trend_name}",
                        description=f"Leverage the trending {trend.trend_category} for increased reach",
                        category="trend_adoption",
                        priority="high" if trend.status == TrendStatus.TRENDING else "medium",
                        expected_impact=min(50, trend.momentum * 5),
                        implementation_effort="low" if trend.trend_category == "hashtag" else "medium",
                        specific_actions=trend.optimization_tips,
                        success_metrics=["engagement_rate", "reach", "impressions"],
                        timeline="immediate",
                        examples=trend.content_examples
                    )
                    recommendations.append(rec)
            
            # Content optimization recommendations based on user data
            if user_content:
                user_recommendations = await self._generate_user_specific_recommendations(user_content)
                recommendations.extend(user_recommendations)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to get trend recommendations: {str(e)}")
            raise
    
    async def _get_user_recent_content(self, user_id: int) -> List[ContentInsightModel]:
        """Get user's recent content for analysis"""
        
        start_date = datetime.utcnow() - timedelta(days=14)
        
        return self.db.query(ContentInsightModel).filter(
            ContentInsightModel.user_id == user_id,
            ContentInsightModel.analysis_timestamp >= start_date
        ).order_by(ContentInsightModel.analysis_timestamp.desc()).limit(20).all()
    
    async def _generate_user_specific_recommendations(
        self,
        user_content: List[ContentInsightModel]
    ) -> List[ContentOptimizationRecommendation]:
        """Generate user-specific optimization recommendations"""
        
        recommendations = []
        
        if not user_content:
            return recommendations
        
        # Analyze user's content patterns
        avg_engagement = statistics.mean([
            float(c.engagement_rate) for c in user_content 
            if c.engagement_rate
        ])
        
        avg_ai_score = statistics.mean([
            float(c.ai_content_score) for c in user_content 
            if c.ai_content_score
        ])
        
        # Content quality recommendation
        if avg_ai_score < 6:
            rec = ContentOptimizationRecommendation(
                recommendation_id="quality_improvement",
                title="Improve Content Quality",
                description=f"Your average content score ({avg_ai_score:.1f}/10) has room for improvement",
                category="quality",
                priority="high",
                expected_impact=30,
                implementation_effort="medium",
                specific_actions=[
                    "Focus on better visual composition",
                    "Improve lighting and audio quality",
                    "Create more engaging captions",
                    "Use trending hashtags strategically"
                ],
                success_metrics=["ai_content_score", "engagement_rate"],
                timeline="2-4 weeks",
                examples=[]
            )
            recommendations.append(rec)
        
        # Engagement optimization recommendation
        if avg_engagement < 0.03:  # Less than 3%
            rec = ContentOptimizationRecommendation(
                recommendation_id="engagement_boost",
                title="Boost Engagement Rate",
                description=f"Your average engagement rate ({avg_engagement:.2%}) is below optimal levels",
                category="engagement",
                priority="high",
                expected_impact=40,
                implementation_effort="low",
                specific_actions=[
                    "Add clear calls-to-action",
                    "Post during peak audience hours",
                    "Engage more with your audience",
                    "Create interactive content (polls, questions)"
                ],
                success_metrics=["engagement_rate", "comments", "shares"],
                timeline="1-2 weeks",
                examples=[]
            )
            recommendations.append(rec)
        
        return recommendations


# Export classes and functions
__all__ = [
    "ContentInsights",
    "TrendAnalyzer",
    "ContentInsightModel",
    "ContentTrend",
    "ContentOptimizationRecommendation",
    "ContentCategory",
    "TrendStatus",
    "ContentElement"
]
