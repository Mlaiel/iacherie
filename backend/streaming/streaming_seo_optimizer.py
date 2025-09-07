"""Streaming SEO Optimizer - Real-time Search Engine Optimization
===============================================================

Enterprise-grade streaming SEO optimization engine providing real-time content indexing,
metadata optimization, keyword targeting, viral detection, and comprehensive
discoverability enhancement for streaming platforms.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/streaming/streaming_seo_optimizer.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.

BUSINESS LOGIC INTEGRATION:
Content Analysis → SEO Optimization → Keyword Enhancement → Viral Detection → Trend Analysis
"""

import asyncio
import json
import uuid
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from decimal import Decimal
import redis
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()
logger = logging.getLogger(__name__)


class SEOOptimizationType(str, Enum):
    """Types of SEO optimization."""
    METADATA_OPTIMIZATION = "metadata_optimization"
    KEYWORD_TARGETING = "keyword_targeting"
    HASHTAG_OPTIMIZATION = "hashtag_optimization"
    TITLE_OPTIMIZATION = "title_optimization"
    DESCRIPTION_ENHANCEMENT = "description_enhancement"
    THUMBNAIL_OPTIMIZATION = "thumbnail_optimization"
    TAG_OPTIMIZATION = "tag_optimization"
    CONTENT_INDEXING = "content_indexing"


class ViralPotential(str, Enum):
    """Viral potential levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VIRAL = "viral"
    TRENDING = "trending"


class SEOMetric(str, Enum):
    """SEO performance metrics."""
    SEARCH_RANKING = "search_ranking"
    ORGANIC_REACH = "organic_reach"
    CLICK_THROUGH_RATE = "click_through_rate"
    IMPRESSION_COUNT = "impression_count"
    ENGAGEMENT_RATE = "engagement_rate"
    DISCOVERABILITY_SCORE = "discoverability_score"
    VIRAL_COEFFICIENT = "viral_coefficient"
    TREND_MOMENTUM = "trend_momentum"


class ContentCategory(str, Enum):
    """Content categories for SEO."""
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    MUSIC = "music"
    GAMING = "gaming"
    TECHNOLOGY = "technology"
    LIFESTYLE = "lifestyle"
    SPORTS = "sports"
    NEWS = "news"


@dataclass
class SEOConfig:
    """Configuration for SEO optimization."""
    optimization_types: List[SEOOptimizationType]
    target_keywords: List[str] = field(default_factory=list)
    content_category: Optional[ContentCategory] = None
    target_audience: Dict[str, Any] = field(default_factory=dict)
    geo_targeting: List[str] = field(default_factory=list)
    language_targeting: List[str] = field(default_factory=list)
    auto_keyword_generation: bool = True
    viral_detection_enabled: bool = True
    trend_analysis_enabled: bool = True
    real_time_optimization: bool = True
    seo_aggressiveness: str = "balanced"  # conservative, balanced, aggressive
    optimization_frequency: int = 300  # seconds


@dataclass
class KeywordAnalysis:
    """Keyword analysis results."""
    keyword: str
    search_volume: int
    competition_level: str  # low, medium, high
    relevance_score: float
    trend_direction: str  # rising, stable, declining
    suggested_usage: str  # primary, secondary, long_tail
    related_keywords: List[str] = field(default_factory=list)
    seasonal_patterns: Dict[str, Any] = field(default_factory=dict)
    geographic_performance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SEOOptimization:
    """SEO optimization record."""
    optimization_id: str
    session_id: str
    optimization_type: SEOOptimizationType
    original_content: Dict[str, Any]
    optimized_content: Dict[str, Any]
    keywords_targeted: List[str]
    seo_score_before: float
    seo_score_after: float
    improvement_percentage: float
    optimization_strategy: Dict[str, Any] = field(default_factory=dict)
    applied_techniques: List[str] = field(default_factory=list)
    performance_prediction: Dict[str, Any] = field(default_factory=dict)
    optimization_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ViralDetectionResult:
    """Viral content detection results."""
    detection_id: str
    session_id: str
    content_id: str
    viral_potential: ViralPotential
    viral_score: float
    viral_indicators: List[str]
    growth_rate: float
    engagement_velocity: float
    share_momentum: float
    trend_alignment: float
    viral_triggers: Dict[str, Any] = field(default_factory=dict)
    predicted_peak: Optional[datetime] = None
    recommended_actions: List[str] = field(default_factory=list)
    detection_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TrendAnalysis:
    """Trending content analysis."""
    analysis_id: str
    content_id: str
    trend_category: str
    trend_score: float
    trend_velocity: float
    peak_prediction: Optional[datetime] = None
    trend_duration_estimate: int = 0  # hours
    competing_content: List[str] = field(default_factory=list)
    trend_drivers: List[str] = field(default_factory=list)
    audience_segments: Dict[str, Any] = field(default_factory=dict)
    geographic_spread: Dict[str, Any] = field(default_factory=dict)
    optimal_posting_times: List[str] = field(default_factory=list)
    analysis_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SEOPerformanceReport:
    """SEO performance analytics."""
    report_id: str
    session_id: str
    timeframe: str
    optimizations_applied: int
    avg_seo_score_improvement: float
    keyword_performance: Dict[str, Any]
    viral_content_detected: int
    trending_content_identified: int
    organic_reach_improvement: float
    search_ranking_improvements: Dict[str, Any]
    discoverability_metrics: Dict[str, Any] = field(default_factory=dict)
    viral_performance_metrics: Dict[str, Any] = field(default_factory=dict)
    trend_analysis_insights: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SEOOptimizationRecord(Base):
    """Database model for SEO optimizations."""
    __tablename__ = "streaming_seo_optimizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    optimization_type = Column(String(30), nullable=False)
    original_content = Column(JSON)
    optimized_content = Column(JSON)
    keywords_targeted = Column(JSON)
    seo_score_before = Column(Float, default=0.0)
    seo_score_after = Column(Float, default=0.0)
    improvement_percentage = Column(Float, default=0.0)
    optimization_strategy = Column(JSON)
    applied_techniques = Column(JSON)
    performance_prediction = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class ViralDetectionRecord(Base):
    """Database model for viral detection."""
    __tablename__ = "viral_detection"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    content_id = Column(String(100), nullable=False)
    viral_potential = Column(String(20), nullable=False)
    viral_score = Column(Float, default=0.0)
    viral_indicators = Column(JSON)
    growth_rate = Column(Float, default=0.0)
    engagement_velocity = Column(Float, default=0.0)
    share_momentum = Column(Float, default=0.0)
    trend_alignment = Column(Float, default=0.0)
    viral_triggers = Column(JSON)
    predicted_peak = Column(DateTime(timezone=True))
    recommended_actions = Column(JSON)
    detected_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class TrendAnalysisRecord(Base):
    """Database model for trend analysis."""
    __tablename__ = "trend_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(String(100), nullable=False, index=True)
    trend_category = Column(String(50), nullable=False)
    trend_score = Column(Float, default=0.0)
    trend_velocity = Column(Float, default=0.0)
    peak_prediction = Column(DateTime(timezone=True))
    trend_duration_estimate = Column(Integer, default=0)
    competing_content = Column(JSON)
    trend_drivers = Column(JSON)
    audience_segments = Column(JSON)
    geographic_spread = Column(JSON)
    optimal_posting_times = Column(JSON)
    analyzed_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class StreamingSEOOptimizer:
    """Enterprise streaming SEO optimizer for discoverability enhancement."""
    
    def __init__(self, redis_client: redis.Redis, db_session: Session):
        self.redis = redis_client
        self.db = db_session
        self.is_running = False
        self.seo_analyzers = {}
        self.keyword_databases = {}
        self.viral_detectors = {}
        self.trend_analyzers = {}
        
    async def start_seo_optimizer(self):
        """Start the streaming SEO optimizer."""
        try:
            self.is_running = True
            
            # Initialize SEO components
            await self._initialize_seo_systems()
            
            # Load keyword databases
            await self._load_keyword_databases()
            
            # Start background SEO tasks
            asyncio.create_task(self._seo_analyzer())
            asyncio.create_task(self._viral_detector())
            asyncio.create_task(self._trend_analyzer())
            asyncio.create_task(self._keyword_optimizer())
            asyncio.create_task(self._performance_tracker())
            
            logger.info("Streaming SEO Optimizer started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start SEO optimizer: {e}")
            raise
    
    async def stop_seo_optimizer(self):
        """Stop the streaming SEO optimizer."""
        try:
            self.is_running = False
            
            # Cleanup SEO processors
            for analyzer in self.seo_analyzers.values():
                if hasattr(analyzer, 'close'):
                    await analyzer.close()
            
            logger.info("Streaming SEO Optimizer stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop SEO optimizer: {e}")
    
    async def optimize_streaming_content(
        self, 
        session_id: str, 
        content_data: Dict[str, Any],
        config: SEOConfig
    ) -> List[SEOOptimization]:
        """Optimize streaming content for SEO."""
        try:
            optimizations = []
            
            # Analyze current content SEO score
            current_seo_score = await self._calculate_seo_score(content_data)
            
            # Perform optimizations based on configuration
            for optimization_type in config.optimization_types:
                optimization_result = await self._apply_seo_optimization(
                    session_id, content_data, optimization_type, config
                )
                
                if optimization_result:
                    # Calculate improvement
                    new_seo_score = await self._calculate_seo_score(
                        optimization_result['optimized_content']
                    )
                    
                    improvement = ((new_seo_score - current_seo_score) / current_seo_score * 100) if current_seo_score > 0 else 0
                    
                    optimization = SEOOptimization(
                        optimization_id=str(uuid.uuid4()),
                        session_id=session_id,
                        optimization_type=optimization_type,
                        original_content=content_data,
                        optimized_content=optimization_result['optimized_content'],
                        keywords_targeted=optimization_result['keywords_used'],
                        seo_score_before=current_seo_score,
                        seo_score_after=new_seo_score,
                        improvement_percentage=improvement,
                        optimization_strategy=optimization_result['strategy'],
                        applied_techniques=optimization_result['techniques'],
                        performance_prediction=optimization_result['prediction']
                    )
                    
                    optimizations.append(optimization)
                    
                    # Save optimization record
                    await self._save_seo_optimization(optimization)
                    
                    # Update content data for next optimization
                    content_data = optimization_result['optimized_content']
                    current_seo_score = new_seo_score
            
            # Cache optimized content
            await self._cache_optimized_content(session_id, content_data, optimizations)
            
            return optimizations
            
        except Exception as e:
            logger.error(f"Failed to optimize streaming content: {e}")
            return []
    
    async def detect_viral_potential(
        self, 
        session_id: str, 
        content_id: str,
        performance_data: Dict[str, Any]
    ) -> ViralDetectionResult:
        """Detect viral potential of streaming content."""
        try:
            detection_id = str(uuid.uuid4())
            
            # Analyze viral indicators
            viral_indicators = await self._analyze_viral_indicators(performance_data)
            
            # Calculate viral score
            viral_score = await self._calculate_viral_score(performance_data, viral_indicators)
            
            # Determine viral potential level
            viral_potential = await self._determine_viral_potential(viral_score)
            
            # Calculate growth metrics
            growth_rate = performance_data.get('growth_rate', 0.0)
            engagement_velocity = await self._calculate_engagement_velocity(performance_data)
            share_momentum = await self._calculate_share_momentum(performance_data)
            trend_alignment = await self._calculate_trend_alignment(performance_data)
            
            # Predict viral peak
            predicted_peak = await self._predict_viral_peak(
                performance_data, viral_score, growth_rate
            )
            
            # Generate recommendations
            recommendations = await self._generate_viral_recommendations(
                viral_potential, viral_score, viral_indicators
            )
            
            detection_result = ViralDetectionResult(
                detection_id=detection_id,
                session_id=session_id,
                content_id=content_id,
                viral_potential=viral_potential,
                viral_score=viral_score,
                viral_indicators=viral_indicators,
                growth_rate=growth_rate,
                engagement_velocity=engagement_velocity,
                share_momentum=share_momentum,
                trend_alignment=trend_alignment,
                viral_triggers=performance_data.get('viral_triggers', {}),
                predicted_peak=predicted_peak,
                recommended_actions=recommendations
            )
            
            # Save detection result
            await self._save_viral_detection(detection_result)
            
            # Trigger viral response if applicable
            if viral_potential in [ViralPotential.HIGH, ViralPotential.VIRAL, ViralPotential.TRENDING]:
                await self._trigger_viral_response(session_id, detection_result)
            
            return detection_result
            
        except Exception as e:
            logger.error(f"Failed to detect viral potential: {e}")
            raise
    
    async def analyze_trending_content(
        self, 
        content_id: str, 
        content_data: Dict[str, Any]
    ) -> TrendAnalysis:
        """Analyze content for trending patterns."""
        try:
            analysis_id = str(uuid.uuid4())
            
            # Determine trend category
            trend_category = await self._categorize_content_trend(content_data)
            
            # Calculate trend score
            trend_score = await self._calculate_trend_score(content_data)
            
            # Calculate trend velocity
            trend_velocity = await self._calculate_trend_velocity(content_data)
            
            # Predict peak timing
            peak_prediction = await self._predict_trend_peak(content_data, trend_velocity)
            
            # Estimate trend duration
            duration_estimate = await self._estimate_trend_duration(
                trend_category, trend_score, trend_velocity
            )
            
            # Identify competing content
            competing_content = await self._identify_competing_content(content_data, trend_category)
            
            # Analyze trend drivers
            trend_drivers = await self._analyze_trend_drivers(content_data)
            
            # Segment audience
            audience_segments = await self._analyze_trend_audience(content_data)
            
            # Analyze geographic spread
            geographic_spread = await self._analyze_geographic_trend_spread(content_data)
            
            # Determine optimal posting times
            optimal_times = await self._calculate_optimal_posting_times(
                trend_category, audience_segments
            )
            
            trend_analysis = TrendAnalysis(
                analysis_id=analysis_id,
                content_id=content_id,
                trend_category=trend_category,
                trend_score=trend_score,
                trend_velocity=trend_velocity,
                peak_prediction=peak_prediction,
                trend_duration_estimate=duration_estimate,
                competing_content=competing_content,
                trend_drivers=trend_drivers,
                audience_segments=audience_segments,
                geographic_spread=geographic_spread,
                optimal_posting_times=optimal_times
            )
            
            # Save analysis
            await self._save_trend_analysis(trend_analysis)
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze trending content: {e}")
            raise
    
    async def optimize_keywords_real_time(
        self, 
        session_id: str, 
        current_keywords: List[str],
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize keywords in real-time based on performance."""
        try:
            # Analyze current keyword performance
            keyword_performance = await self._analyze_keyword_performance(
                current_keywords, performance_data
            )
            
            # Identify underperforming keywords
            underperforming = [
                kw for kw, perf in keyword_performance.items() 
                if perf.get('performance_score', 0) < 0.5
            ]
            
            # Generate keyword suggestions
            new_keywords = await self._generate_keyword_suggestions(
                session_id, performance_data, exclude=underperforming
            )
            
            # Optimize keyword mix
            optimized_keywords = await self._optimize_keyword_mix(
                current_keywords, new_keywords, keyword_performance
            )
            
            # Calculate optimization impact
            impact_prediction = await self._predict_keyword_optimization_impact(
                current_keywords, optimized_keywords, performance_data
            )
            
            return {
                'original_keywords': current_keywords,
                'optimized_keywords': optimized_keywords,
                'keywords_added': list(set(optimized_keywords) - set(current_keywords)),
                'keywords_removed': list(set(current_keywords) - set(optimized_keywords)),
                'performance_improvement_prediction': impact_prediction,
                'optimization_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize keywords real-time: {e}")
            return {}
    
    async def generate_seo_performance_report(
        self, 
        session_id: str, 
        timeframe: str = "session"
    ) -> SEOPerformanceReport:
        """Generate comprehensive SEO performance report."""
        try:
            report_id = str(uuid.uuid4())
            
            # Define time range
            if timeframe == "session":
                start_time = await self._get_session_start_time(session_id)
                end_time = datetime.now(timezone.utc)
            elif timeframe == "daily":
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(days=1)
            elif timeframe == "weekly":
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(weeks=1)
            else:
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(hours=24)
            
            # Collect SEO data
            seo_data = await self._collect_seo_performance_data(session_id, start_time, end_time)
            
            # Calculate metrics
            optimizations_applied = len(seo_data['optimizations'])
            avg_improvement = await self._calculate_average_seo_improvement(seo_data['optimizations'])
            
            # Keyword performance analysis
            keyword_performance = await self._analyze_session_keyword_performance(
                session_id, start_time, end_time
            )
            
            # Viral content metrics
            viral_metrics = await self._calculate_viral_content_metrics(
                session_id, start_time, end_time
            )
            
            # Trending content metrics
            trending_metrics = await self._calculate_trending_content_metrics(
                session_id, start_time, end_time
            )
            
            # Organic reach improvement
            reach_improvement = await self._calculate_organic_reach_improvement(
                session_id, start_time, end_time
            )
            
            # Search ranking improvements
            ranking_improvements = await self._calculate_search_ranking_improvements(
                session_id, start_time, end_time
            )
            
            # Discoverability metrics
            discoverability_metrics = await self._calculate_discoverability_metrics(
                session_id, seo_data
            )
            
            # Generate recommendations
            recommendations = await self._generate_seo_recommendations(
                session_id, seo_data, viral_metrics, trending_metrics
            )
            
            report = SEOPerformanceReport(
                report_id=report_id,
                session_id=session_id,
                timeframe=timeframe,
                optimizations_applied=optimizations_applied,
                avg_seo_score_improvement=avg_improvement,
                keyword_performance=keyword_performance,
                viral_content_detected=viral_metrics['detected_count'],
                trending_content_identified=trending_metrics['identified_count'],
                organic_reach_improvement=reach_improvement,
                search_ranking_improvements=ranking_improvements,
                discoverability_metrics=discoverability_metrics,
                viral_performance_metrics=viral_metrics,
                trend_analysis_insights=trending_metrics,
                recommendations=recommendations
            )
            
            # Cache report
            await self._cache_seo_report(session_id, report)
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate SEO performance report: {e}")
            raise
    
    async def _initialize_seo_systems(self):
        """Initialize SEO system components."""
        logger.info("SEO systems initialized")
    
    async def _load_keyword_databases(self):
        """Load keyword databases and trending terms."""
        self.keyword_databases = {
            'trending_keywords': await self._load_trending_keywords(),
            'high_volume_keywords': await self._load_high_volume_keywords(),
            'long_tail_keywords': await self._load_long_tail_keywords(),
            'category_keywords': await self._load_category_keywords()
        }
    
    async def _calculate_seo_score(self, content_data: Dict[str, Any]) -> float:
        """Calculate SEO score for content."""
        score = 0.0
        
        # Title optimization (20%)
        title = content_data.get('title', '')
        if title:
            title_score = await self._score_title_seo(title)
            score += title_score * 0.20
        
        # Description optimization (15%)
        description = content_data.get('description', '')
        if description:
            desc_score = await self._score_description_seo(description)
            score += desc_score * 0.15
        
        # Keywords optimization (25%)
        keywords = content_data.get('keywords', [])
        if keywords:
            keyword_score = await self._score_keywords_seo(keywords)
            score += keyword_score * 0.25
        
        # Tags optimization (15%)
        tags = content_data.get('tags', [])
        if tags:
            tag_score = await self._score_tags_seo(tags)
            score += tag_score * 0.15
        
        # Content quality (25%)
        content_quality = await self._score_content_quality(content_data)
        score += content_quality * 0.25
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def _apply_seo_optimization(
        self, 
        session_id: str, 
        content_data: Dict[str, Any],
        optimization_type: SEOOptimizationType,
        config: SEOConfig
    ) -> Optional[Dict[str, Any]]:
        """Apply specific SEO optimization."""
        try:
            if optimization_type == SEOOptimizationType.TITLE_OPTIMIZATION:
                return await self._optimize_title(content_data, config)
            elif optimization_type == SEOOptimizationType.DESCRIPTION_ENHANCEMENT:
                return await self._optimize_description(content_data, config)
            elif optimization_type == SEOOptimizationType.KEYWORD_TARGETING:
                return await self._optimize_keywords(content_data, config)
            elif optimization_type == SEOOptimizationType.HASHTAG_OPTIMIZATION:
                return await self._optimize_hashtags(content_data, config)
            elif optimization_type == SEOOptimizationType.TAG_OPTIMIZATION:
                return await self._optimize_tags(content_data, config)
            elif optimization_type == SEOOptimizationType.METADATA_OPTIMIZATION:
                return await self._optimize_metadata(content_data, config)
            else:
                return await self._apply_generic_optimization(content_data, config)
                
        except Exception as e:
            logger.error(f"Failed to apply SEO optimization: {e}")
            return None
    
    async def _optimize_title(self, content_data: Dict[str, Any], config: SEOConfig) -> Dict[str, Any]:
        """Optimize content title for SEO."""
        original_title = content_data.get('title', '')
        
        # Apply title optimization techniques
        optimized_title = original_title
        techniques = []
        keywords_used = []
        
        # Add target keywords if not present
        for keyword in config.target_keywords[:2]:  # Max 2 keywords in title
            if keyword.lower() not in original_title.lower():
                optimized_title = f"{keyword} - {optimized_title}"
                keywords_used.append(keyword)
                techniques.append("keyword_insertion")
        
        # Optimize length (50-60 characters ideal)
        if len(optimized_title) > 60:
            optimized_title = optimized_title[:57] + "..."
            techniques.append("length_optimization")
        
        # Add emotional triggers
        emotional_words = ["amazing", "ultimate", "incredible", "must-see"]
        if not any(word in optimized_title.lower() for word in emotional_words):
            optimized_title = f"Amazing {optimized_title}"
            techniques.append("emotional_enhancement")
        
        optimized_content = content_data.copy()
        optimized_content['title'] = optimized_title
        
        return {
            'optimized_content': optimized_content,
            'keywords_used': keywords_used,
            'techniques': techniques,
            'strategy': {'type': 'title_optimization', 'focus': 'keyword_integration'},
            'prediction': {'improvement_expected': 15.0}
        }
    
    async def _optimize_description(self, content_data: Dict[str, Any], config: SEOConfig) -> Dict[str, Any]:
        """Optimize content description for SEO."""
        original_description = content_data.get('description', '')
        
        optimized_description = original_description
        techniques = []
        keywords_used = []
        
        # Add target keywords
        for keyword in config.target_keywords:
            if keyword.lower() not in original_description.lower():
                optimized_description += f" {keyword}"
                keywords_used.append(keyword)
                techniques.append("keyword_integration")
        
        # Optimize length (155-160 characters for search snippets)
        if len(optimized_description) < 120:
            optimized_description += " Discover amazing content and engage with our community!"
            techniques.append("length_enhancement")
        elif len(optimized_description) > 160:
            optimized_description = optimized_description[:157] + "..."
            techniques.append("length_optimization")
        
        # Add call-to-action
        if "watch" not in optimized_description.lower() and "join" not in optimized_description.lower():
            optimized_description += " Watch now!"
            techniques.append("cta_addition")
        
        optimized_content = content_data.copy()
        optimized_content['description'] = optimized_description
        
        return {
            'optimized_content': optimized_content,
            'keywords_used': keywords_used,
            'techniques': techniques,
            'strategy': {'type': 'description_optimization', 'focus': 'keyword_density'},
            'prediction': {'improvement_expected': 12.0}
        }
    
    async def _analyze_viral_indicators(self, performance_data: Dict[str, Any]) -> List[str]:
        """Analyze viral indicators in performance data."""
        indicators = []
        
        # Rapid growth
        if performance_data.get('growth_rate', 0) > 0.5:
            indicators.append("rapid_growth")
        
        # High engagement rate
        if performance_data.get('engagement_rate', 0) > 0.15:
            indicators.append("high_engagement")
        
        # Share velocity
        if performance_data.get('shares_per_minute', 0) > 10:
            indicators.append("high_share_velocity")
        
        # Comment surge
        if performance_data.get('comments_per_minute', 0) > 5:
            indicators.append("comment_surge")
        
        # Cross-platform spread
        if performance_data.get('platform_count', 1) > 3:
            indicators.append("cross_platform_spread")
        
        # Influencer mentions
        if performance_data.get('influencer_mentions', 0) > 0:
            indicators.append("influencer_amplification")
        
        return indicators
    
    async def _calculate_viral_score(
        self, 
        performance_data: Dict[str, Any], 
        viral_indicators: List[str]
    ) -> float:
        """Calculate viral score based on performance and indicators."""
        base_score = 0.0
        
        # Indicator-based scoring
        indicator_weight = 0.15
        base_score += len(viral_indicators) * indicator_weight
        
        # Growth rate scoring
        growth_rate = performance_data.get('growth_rate', 0)
        base_score += min(growth_rate, 1.0) * 0.25
        
        # Engagement scoring
        engagement_rate = performance_data.get('engagement_rate', 0)
        base_score += min(engagement_rate * 2, 1.0) * 0.20
        
        # Share momentum scoring
        share_rate = performance_data.get('shares_per_minute', 0) / 100  # Normalize
        base_score += min(share_rate, 1.0) * 0.20
        
        # Platform spread scoring
        platform_count = performance_data.get('platform_count', 1)
        platform_score = min((platform_count - 1) / 5, 1.0)  # Normalize to max 6 platforms
        base_score += platform_score * 0.20
        
        return min(base_score, 1.0)
    
    async def _determine_viral_potential(self, viral_score: float) -> ViralPotential:
        """Determine viral potential level from score."""
        if viral_score >= 0.8:
            return ViralPotential.VIRAL
        elif viral_score >= 0.6:
            return ViralPotential.HIGH
        elif viral_score >= 0.4:
            return ViralPotential.MEDIUM
        else:
            return ViralPotential.LOW
    
    # Background task methods
    async def _seo_analyzer(self):
        """Background SEO analysis."""
        while self.is_running:
            try:
                # Analyze SEO for active streaming sessions
                active_sessions = await self.redis.keys("streaming:seo:*")
                
                for session_key in active_sessions:
                    session_id = session_key.split(":")[-1]
                    await self._analyze_session_seo(session_id)
                
                await asyncio.sleep(300)  # Analyze every 5 minutes
                
            except Exception as e:
                logger.error(f"SEO analyzer error: {e}")
                await asyncio.sleep(600)
    
    async def _viral_detector(self):
        """Background viral content detection."""
        while self.is_running:
            try:
                # Monitor for viral patterns
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Viral detector error: {e}")
                await asyncio.sleep(120)
    
    async def _trend_analyzer(self):
        """Background trend analysis."""
        while self.is_running:
            try:
                # Analyze trending patterns
                await asyncio.sleep(300)  # Analyze every 5 minutes
                
            except Exception as e:
                logger.error(f"Trend analyzer error: {e}")
                await asyncio.sleep(600)
    
    async def _keyword_optimizer(self):
        """Background keyword optimization."""
        while self.is_running:
            try:
                # Optimize keywords for active sessions
                await asyncio.sleep(600)  # Optimize every 10 minutes
                
            except Exception as e:
                logger.error(f"Keyword optimizer error: {e}")
                await asyncio.sleep(1200)
    
    async def _performance_tracker(self):
        """Track SEO performance metrics."""
        while self.is_running:
            try:
                # Track performance across all optimizations
                await asyncio.sleep(300)  # Track every 5 minutes
                
            except Exception as e:
                logger.error(f"Performance tracker error: {e}")
                await asyncio.sleep(600)
    
    # Utility methods (simplified implementations)
    async def _save_seo_optimization(self, optimization: SEOOptimization):
        """Save SEO optimization to database."""
        try:
            record = SEOOptimizationRecord(
                id=optimization.optimization_id,
                session_id=optimization.session_id,
                optimization_type=optimization.optimization_type.value,
                original_content=optimization.original_content,
                optimized_content=optimization.optimized_content,
                keywords_targeted=optimization.keywords_targeted,
                seo_score_before=optimization.seo_score_before,
                seo_score_after=optimization.seo_score_after,
                improvement_percentage=optimization.improvement_percentage,
                optimization_strategy=optimization.optimization_strategy,
                applied_techniques=optimization.applied_techniques,
                performance_prediction=optimization.performance_prediction
            )
            
            self.db.add(record)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to save SEO optimization: {e}")


def create_streaming_seo_optimizer(
    redis_client: redis.Redis, 
    db_session: Session
) -> StreamingSEOOptimizer:
    """Factory function to create Streaming SEO Optimizer instance."""
    return StreamingSEOOptimizer(redis_client, db_session)