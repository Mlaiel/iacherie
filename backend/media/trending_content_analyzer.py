"""Trending Content Analyzer - AI-Powered Trend Analysis and Detection

Enterprise-grade trending content analysis system for identifying viral patterns,
trend detection, and content performance analysis across social media platforms.

Author: Fahed Mlaiel (mlaiel@live.de)  
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from pathlib import Path
import hashlib
import uuid
from collections import defaultdict, Counter
import math

# Data analysis imports with graceful fallbacks
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logging.warning("NumPy not available - using basic calculations")

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    logging.warning("Pandas not available - using basic data structures")

# NLP and sentiment analysis imports
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False
    logging.warning("NLTK not available - using basic text processing")

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False
    logging.warning("TextBlob not available - using basic sentiment analysis")


class PlatformType(Enum):
    """Supported platform types for trend analysis"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"


class TrendCategory(Enum):
    """Categories of trending content"""
    HASHTAGS = "hashtags"
    KEYWORDS = "keywords"
    TOPICS = "topics"
    SOUNDS = "sounds"
    CHALLENGES = "challenges"
    MEMES = "memes"
    NEWS = "news"
    SEASONAL = "seasonal"
    VIRAL_CONTENT = "viral_content"


class TrendStrength(Enum):
    """Trend strength levels"""
    EMERGING = "emerging"
    GROWING = "growing"
    VIRAL = "viral"
    PEAK = "peak"
    DECLINING = "declining"
    STABLE = "stable"


@dataclass
class TrendData:
    """Individual trend data point"""
    content: str
    platform: PlatformType
    category: TrendCategory
    engagement_metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    reach: int = 0
    velocity: float = 0.0  # Growth rate
    sentiment: float = 0.0
    related_terms: List[str] = field(default_factory=list)
    source_url: Optional[str] = None


@dataclass
class TrendAnalysis:
    """Analysis results for a trending item"""
    trend_id: str
    content: str
    category: TrendCategory
    platforms: List[PlatformType]
    strength: TrendStrength
    confidence_score: float = 0.0
    
    # Metrics
    total_mentions: int = 0
    total_engagement: int = 0
    growth_rate: float = 0.0
    velocity: float = 0.0
    reach_estimate: int = 0
    
    # Analysis
    sentiment_score: float = 0.0
    demographics: Dict[str, Any] = field(default_factory=dict)
    geographic_data: Dict[str, Any] = field(default_factory=dict)
    temporal_pattern: Dict[str, Any] = field(default_factory=dict)
    
    # Related data
    related_trends: List[str] = field(default_factory=list)
    influencers: List[str] = field(default_factory=list)
    peak_times: List[str] = field(default_factory=list)
    
    # Predictions
    predicted_duration: int = 7  # days
    viral_probability: float = 0.0
    decline_prediction: Optional[datetime] = None
    
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class TrendReport:
    """Comprehensive trend analysis report"""
    report_id: str
    analysis_period: Tuple[datetime, datetime]
    platforms_analyzed: List[PlatformType]
    
    # Top trends by category
    trending_hashtags: List[TrendAnalysis] = field(default_factory=list)
    trending_keywords: List[TrendAnalysis] = field(default_factory=list)
    trending_topics: List[TrendAnalysis] = field(default_factory=list)
    viral_content: List[TrendAnalysis] = field(default_factory=list)
    
    # Insights
    emerging_trends: List[TrendAnalysis] = field(default_factory=list)
    declining_trends: List[TrendAnalysis] = field(default_factory=list)
    cross_platform_trends: List[TrendAnalysis] = field(default_factory=list)
    
    # Statistics
    total_trends_analyzed: int = 0
    accuracy_metrics: Dict[str, float] = field(default_factory=dict)
    platform_activity: Dict[str, int] = field(default_factory=dict)
    
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AnalysisJob:
    """Trend analysis job configuration"""
    job_id: str
    platforms: List[PlatformType]
    categories: List[TrendCategory]
    analysis_period: Tuple[datetime, datetime]
    content_sources: List[str] = field(default_factory=list)
    custom_keywords: List[str] = field(default_factory=list)
    min_engagement_threshold: int = 100
    include_predictions: bool = True
    
    # Job tracking
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"
    progress: float = 0.0
    results: Optional[TrendReport] = None


class TrendingContentAnalyzer:
    """Enterprise trending content analysis and detection system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Data storage
        self.trend_data: List[TrendData] = []
        self.trend_analyses: Dict[str, TrendAnalysis] = {}
        
        # Active analysis jobs
        self.active_jobs: Dict[str, AnalysisJob] = {}
        
        # Trend tracking
        self.hashtag_tracker: Dict[str, List[TrendData]] = defaultdict(list)
        self.keyword_tracker: Dict[str, List[TrendData]] = defaultdict(list)
        self.platform_trends: Dict[PlatformType, Dict[str, Any]] = {}
        
        # Analysis configuration
        self.trending_thresholds = self._initialize_trending_thresholds()
        self.stop_words = self._initialize_stop_words()
        
        # Statistics
        self.analysis_stats = {
            "total_analyses": 0,
            "trends_identified": 0,
            "viral_predictions": 0,
            "accuracy_rate": 0.0,
            "data_points_processed": 0,
            "last_analysis": None
        }
        
        # Initialize background tasks
        self._start_background_tasks()
        
        self.logger.info("Trending Content Analyzer initialized")
    
    def _initialize_trending_thresholds(self) -> Dict[PlatformType, Dict[str, Any]]:
        """Initialize platform-specific trending thresholds"""
        
        thresholds = {}
        
        # Instagram thresholds
        thresholds[PlatformType.INSTAGRAM] = {
            "viral_likes": 10000,
            "viral_comments": 500,
            "viral_shares": 1000,
            "hashtag_trending_mentions": 1000,
            "keyword_trending_mentions": 500,
            "growth_rate_threshold": 2.0,  # 200% growth
            "velocity_threshold": 100,  # mentions per hour
            "engagement_rate_viral": 0.1  # 10%
        }
        
        # TikTok thresholds
        thresholds[PlatformType.TIKTOK] = {
            "viral_views": 100000,
            "viral_likes": 5000,
            "viral_shares": 2000,
            "hashtag_trending_mentions": 5000,
            "keyword_trending_mentions": 2000,
            "growth_rate_threshold": 3.0,  # 300% growth
            "velocity_threshold": 500,  # mentions per hour
            "engagement_rate_viral": 0.15  # 15%
        }
        
        # YouTube thresholds
        thresholds[PlatformType.YOUTUBE] = {
            "viral_views": 1000000,
            "viral_likes": 50000,
            "viral_comments": 5000,
            "hashtag_trending_mentions": 10000,
            "keyword_trending_mentions": 5000,
            "growth_rate_threshold": 1.5,  # 150% growth
            "velocity_threshold": 50,  # mentions per hour
            "engagement_rate_viral": 0.05  # 5%
        }
        
        # Add default thresholds for other platforms
        self._add_default_thresholds(thresholds)
        
        return thresholds
    
    def _add_default_thresholds(self, thresholds: Dict[PlatformType, Dict[str, Any]]) -> None:
        """Add default thresholds for remaining platforms"""
        
        default_threshold = {
            "viral_likes": 5000,
            "viral_comments": 200,
            "viral_shares": 500,
            "hashtag_trending_mentions": 1000,
            "keyword_trending_mentions": 500,
            "growth_rate_threshold": 2.0,
            "velocity_threshold": 100,
            "engagement_rate_viral": 0.08
        }
        
        platforms_without_thresholds = [
            PlatformType.FACEBOOK, PlatformType.TWITTER, 
            PlatformType.LINKEDIN, PlatformType.PINTEREST,
            PlatformType.SNAPCHAT, PlatformType.REDDIT
        ]
        
        for platform in platforms_without_thresholds:
            thresholds[platform] = default_threshold.copy()
    
    def _initialize_stop_words(self) -> Set[str]:
        """Initialize stop words for text analysis"""
        
        basic_stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "this", "that", "these", "those", "is", "are",
            "was", "were", "be", "been", "being", "have", "has", "had", "do",
            "does", "did", "will", "would", "could", "should", "may", "might",
            "must", "can", "i", "you", "he", "she", "it", "we", "they", "me",
            "him", "her", "us", "them", "my", "your", "his", "her", "its",
            "our", "their", "mine", "yours", "hers", "ours", "theirs"
        }
        
        if HAS_NLTK:
            try:
                nltk_stop_words = set(stopwords.words('english'))
                return basic_stop_words.union(nltk_stop_words)
            except Exception:
                pass
        
        return basic_stop_words
    
    def _start_background_tasks(self) -> None:
        """Start background analysis tasks"""
        
        # Trend monitoring task
        asyncio.create_task(self._trend_monitoring_worker())
        
        # Data cleanup task
        asyncio.create_task(self._data_cleanup_worker())
        
        # Real-time analysis task
        asyncio.create_task(self._real_time_analysis_worker())
    
    async def _trend_monitoring_worker(self) -> None:
        """Background worker for continuous trend monitoring"""
        
        while True:
            try:
                # Update existing trend analyses
                await self._update_trend_analyses()
                
                # Detect new emerging trends
                await self._detect_emerging_trends()
                
                # Update trend strengths
                await self._update_trend_strengths()
                
                # Sleep for 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                self.logger.error(f"Error in trend monitoring worker: {str(e)}")
                await asyncio.sleep(60)
    
    async def _data_cleanup_worker(self) -> None:
        """Background worker for data cleanup"""
        
        while True:
            try:
                # Remove old trend data (older than 30 days)
                cutoff_date = datetime.now() - timedelta(days=30)
                
                self.trend_data = [
                    data for data in self.trend_data 
                    if data.timestamp > cutoff_date
                ]
                
                # Clean up old analyses
                old_analyses = []
                for trend_id, analysis in self.trend_analyses.items():
                    if analysis.last_updated < cutoff_date:
                        old_analyses.append(trend_id)
                
                for trend_id in old_analyses:
                    del self.trend_analyses[trend_id]
                
                self.logger.info(f"Cleaned up old data: {len(old_analyses)} analyses removed")
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                self.logger.error(f"Error in data cleanup worker: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _real_time_analysis_worker(self) -> None:
        """Background worker for real-time trend analysis"""
        
        while True:
            try:
                # Analyze recent data for immediate trends
                await self._analyze_real_time_trends()
                
                # Update viral probability predictions
                await self._update_viral_predictions()
                
                # Sleep for 1 minute
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in real-time analysis worker: {str(e)}")
                await asyncio.sleep(60)
    
    async def create_analysis_job(
        self,
        platforms: List[PlatformType],
        categories: List[TrendCategory],
        analysis_period: Optional[Tuple[datetime, datetime]] = None,
        **kwargs
    ) -> str:
        """Create a new trend analysis job"""
        
        job_id = str(uuid.uuid4())
        
        # Default to last 24 hours if no period specified
        if not analysis_period:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)
            analysis_period = (start_time, end_time)
        
        job = AnalysisJob(
            job_id=job_id,
            platforms=platforms,
            categories=categories,
            analysis_period=analysis_period,
            content_sources=kwargs.get("content_sources", []),
            custom_keywords=kwargs.get("custom_keywords", []),
            min_engagement_threshold=kwargs.get("min_engagement_threshold", 100),
            include_predictions=kwargs.get("include_predictions", True)
        )
        
        self.active_jobs[job_id] = job
        
        self.logger.info(f"Created analysis job {job_id} for {len(platforms)} platforms")
        
        return job_id
    
    async def process_analysis_job(self, job_id: str) -> TrendReport:
        """Process a trend analysis job"""
        
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.active_jobs[job_id]
        job.status = "processing"
        job.started_at = datetime.now()
        
        try:
            self.logger.info(f"Processing analysis job {job_id}")
            
            report = TrendReport(
                report_id=job_id,
                analysis_period=job.analysis_period,
                platforms_analyzed=job.platforms
            )
            
            total_categories = len(job.categories)
            completed_categories = 0
            
            # Analyze each category
            for category in job.categories:
                try:
                    trends = await self._analyze_category(
                        category,
                        job.platforms,
                        job.analysis_period,
                        job.min_engagement_threshold
                    )
                    
                    # Categorize results
                    if category == TrendCategory.HASHTAGS:
                        report.trending_hashtags = trends
                    elif category == TrendCategory.KEYWORDS:
                        report.trending_keywords = trends
                    elif category == TrendCategory.TOPICS:
                        report.trending_topics = trends
                    elif category == TrendCategory.VIRAL_CONTENT:
                        report.viral_content = trends
                    
                    completed_categories += 1
                    job.progress = completed_categories / total_categories
                    
                except Exception as e:
                    self.logger.error(f"Failed to analyze category {category.value}: {str(e)}")
            
            # Generate insights
            await self._generate_trend_insights(report, job)
            
            # Calculate statistics
            await self._calculate_report_statistics(report)
            
            # Update job completion
            job.completed_at = datetime.now()
            job.status = "completed"
            job.results = report
            
            # Update global statistics
            self.analysis_stats["total_analyses"] += 1
            self.analysis_stats["trends_identified"] += report.total_trends_analyzed
            self.analysis_stats["last_analysis"] = datetime.now().isoformat()
            
            self.logger.info(
                f"Completed analysis job {job_id} with {report.total_trends_analyzed} trends identified"
            )
            
            return report
            
        except Exception as e:
            job.status = "failed"
            job.completed_at = datetime.now()
            self.logger.error(f"Error processing analysis job {job_id}: {str(e)}")
            raise
    
    async def _analyze_category(
        self,
        category: TrendCategory,
        platforms: List[PlatformType],
        analysis_period: Tuple[datetime, datetime],
        min_threshold: int
    ) -> List[TrendAnalysis]:
        """Analyze trends for a specific category"""
        
        start_time, end_time = analysis_period
        
        # Filter relevant data
        relevant_data = [
            data for data in self.trend_data
            if (data.platform in platforms and
                start_time <= data.timestamp <= end_time and
                data.category == category)
        ]
        
        if not relevant_data:
            self.logger.warning(f"No data found for category {category.value}")
            return []
        
        # Group data by content
        content_groups = defaultdict(list)
        for data in relevant_data:
            content_groups[data.content].append(data)
        
        trends = []
        
        for content, data_points in content_groups.items():
            try:
                # Calculate trend metrics
                total_engagement = sum(
                    sum(dp.engagement_metrics.values()) for dp in data_points
                )
                
                if total_engagement < min_threshold:
                    continue
                
                # Create trend analysis
                trend_analysis = await self._create_trend_analysis(
                    content, category, data_points, platforms
                )
                
                if trend_analysis:
                    trends.append(trend_analysis)
                    
            except Exception as e:
                self.logger.error(f"Error analyzing trend for '{content}': {str(e)}")
        
        # Sort by engagement and return top trends
        trends.sort(key=lambda x: x.total_engagement, reverse=True)
        return trends[:50]  # Return top 50 trends
    
    async def _create_trend_analysis(
        self,
        content: str,
        category: TrendCategory,
        data_points: List[TrendData],
        platforms: List[PlatformType]
    ) -> Optional[TrendAnalysis]:
        """Create comprehensive trend analysis"""
        
        try:
            trend_id = hashlib.md5(f"{content}_{category.value}".encode()).hexdigest()
            
            # Calculate basic metrics
            total_mentions = len(data_points)
            total_engagement = sum(sum(dp.engagement_metrics.values()) for dp in data_points)
            total_reach = sum(dp.reach for dp in data_points)
            
            # Calculate growth rate
            growth_rate = await self._calculate_growth_rate(data_points)
            
            # Calculate velocity (mentions per hour)
            if data_points:
                time_span = (max(dp.timestamp for dp in data_points) - 
                           min(dp.timestamp for dp in data_points)).total_seconds() / 3600
                velocity = total_mentions / max(1, time_span)
            else:
                velocity = 0.0
            
            # Determine trend strength
            strength = self._determine_trend_strength(
                total_engagement, growth_rate, velocity, data_points[0].platform
            )
            
            # Calculate sentiment
            sentiment_score = sum(dp.sentiment for dp in data_points) / len(data_points)
            
            # Extract related terms
            related_terms = self._extract_related_terms(data_points)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                total_mentions, total_engagement, growth_rate, len(platforms)
            )
            
            # Generate predictions
            viral_probability = self._calculate_viral_probability(
                total_engagement, growth_rate, velocity, sentiment_score
            )
            
            predicted_duration = self._predict_trend_duration(
                strength, growth_rate, category
            )
            
            # Estimate decline
            decline_prediction = None
            if strength in [TrendStrength.PEAK, TrendStrength.VIRAL]:
                decline_prediction = datetime.now() + timedelta(days=predicted_duration)
            
            return TrendAnalysis(
                trend_id=trend_id,
                content=content,
                category=category,
                platforms=[dp.platform for dp in data_points],
                strength=strength,
                confidence_score=confidence_score,
                total_mentions=total_mentions,
                total_engagement=int(total_engagement),
                growth_rate=growth_rate,
                velocity=velocity,
                reach_estimate=total_reach,
                sentiment_score=sentiment_score,
                related_trends=related_terms[:10],
                viral_probability=viral_probability,
                predicted_duration=predicted_duration,
                decline_prediction=decline_prediction
            )
            
        except Exception as e:
            self.logger.error(f"Error creating trend analysis: {str(e)}")
            return None
    
    async def _calculate_growth_rate(self, data_points: List[TrendData]) -> float:
        """Calculate growth rate for trend data"""
        
        if len(data_points) < 2:
            return 0.0
        
        # Sort by timestamp
        sorted_data = sorted(data_points, key=lambda x: x.timestamp)
        
        # Calculate hourly engagement totals
        hourly_data = defaultdict(float)
        for dp in sorted_data:
            hour_key = dp.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_data[hour_key] += sum(dp.engagement_metrics.values())
        
        if len(hourly_data) < 2:
            return 0.0
        
        # Calculate growth between first and last periods
        hours = sorted(hourly_data.keys())
        initial_engagement = hourly_data[hours[0]]
        final_engagement = hourly_data[hours[-1]]
        
        if initial_engagement == 0:
            return final_engagement * 10  # High growth rate for new trends
        
        growth_rate = (final_engagement - initial_engagement) / initial_engagement
        return max(0.0, growth_rate)
    
    def _determine_trend_strength(
        self,
        total_engagement: float,
        growth_rate: float,
        velocity: float,
        platform: PlatformType
    ) -> TrendStrength:
        """Determine the strength of a trend"""
        
        thresholds = self.trending_thresholds.get(platform, {})
        
        viral_threshold = thresholds.get("viral_likes", 10000)
        growth_threshold = thresholds.get("growth_rate_threshold", 2.0)
        velocity_threshold = thresholds.get("velocity_threshold", 100)
        
        # Check for viral status
        if total_engagement >= viral_threshold * 2 and growth_rate >= growth_threshold * 2:
            return TrendStrength.VIRAL
        
        # Check for peak status
        if total_engagement >= viral_threshold and growth_rate >= growth_threshold:
            return TrendStrength.PEAK
        
        # Check for growing status
        if growth_rate >= growth_threshold and velocity >= velocity_threshold:
            return TrendStrength.GROWING
        
        # Check for emerging status
        if growth_rate >= 1.0 and velocity >= velocity_threshold / 2:
            return TrendStrength.EMERGING
        
        # Check for declining status
        if growth_rate < 0:
            return TrendStrength.DECLINING
        
        return TrendStrength.STABLE
    
    def _extract_related_terms(self, data_points: List[TrendData]) -> List[str]:
        """Extract related terms from trend data"""
        
        all_related_terms = []
        for dp in data_points:
            all_related_terms.extend(dp.related_terms)
        
        # Count term frequencies
        term_counts = Counter(all_related_terms)
        
        # Return most common terms
        return [term for term, count in term_counts.most_common(20)]
    
    def _calculate_confidence_score(
        self,
        mentions: int,
        engagement: float,
        growth_rate: float,
        platform_count: int
    ) -> float:
        """Calculate confidence score for trend analysis"""
        
        score = 0.0
        
        # Mentions factor (0-0.3)
        if mentions >= 1000:
            score += 0.3
        elif mentions >= 100:
            score += 0.2
        elif mentions >= 10:
            score += 0.1
        
        # Engagement factor (0-0.3)
        if engagement >= 100000:
            score += 0.3
        elif engagement >= 10000:
            score += 0.2
        elif engagement >= 1000:
            score += 0.1
        
        # Growth rate factor (0-0.2)
        if growth_rate >= 5.0:
            score += 0.2
        elif growth_rate >= 2.0:
            score += 0.15
        elif growth_rate >= 1.0:
            score += 0.1
        
        # Platform coverage factor (0-0.2)
        score += min(0.2, platform_count * 0.05)
        
        return min(1.0, score)
    
    def _calculate_viral_probability(
        self,
        engagement: float,
        growth_rate: float,
        velocity: float,
        sentiment: float
    ) -> float:
        """Calculate probability of content going viral"""
        
        probability = 0.0
        
        # Engagement factor
        if engagement >= 100000:
            probability += 0.4
        elif engagement >= 10000:
            probability += 0.3
        elif engagement >= 1000:
            probability += 0.2
        
        # Growth rate factor
        if growth_rate >= 5.0:
            probability += 0.3
        elif growth_rate >= 2.0:
            probability += 0.2
        elif growth_rate >= 1.0:
            probability += 0.1
        
        # Velocity factor
        if velocity >= 1000:
            probability += 0.2
        elif velocity >= 100:
            probability += 0.15
        elif velocity >= 10:
            probability += 0.1
        
        # Sentiment factor
        if sentiment > 0.5:
            probability += 0.1
        elif sentiment > 0:
            probability += 0.05
        
        return min(1.0, probability)
    
    def _predict_trend_duration(
        self,
        strength: TrendStrength,
        growth_rate: float,
        category: TrendCategory
    ) -> int:
        """Predict how long a trend will last (in days)"""
        
        base_duration = {
            TrendStrength.EMERGING: 3,
            TrendStrength.GROWING: 7,
            TrendStrength.VIRAL: 14,
            TrendStrength.PEAK: 10,
            TrendStrength.STABLE: 30,
            TrendStrength.DECLINING: 2
        }
        
        category_multiplier = {
            TrendCategory.HASHTAGS: 1.0,
            TrendCategory.KEYWORDS: 1.2,
            TrendCategory.TOPICS: 1.5,
            TrendCategory.SOUNDS: 0.8,
            TrendCategory.CHALLENGES: 0.9,
            TrendCategory.MEMES: 0.7,
            TrendCategory.NEWS: 0.5,
            TrendCategory.SEASONAL: 3.0,
            TrendCategory.VIRAL_CONTENT: 1.1
        }
        
        duration = base_duration.get(strength, 7)
        duration *= category_multiplier.get(category, 1.0)
        
        # Adjust based on growth rate
        if growth_rate > 10:
            duration *= 0.7  # Fast growth = shorter duration
        elif growth_rate > 5:
            duration *= 0.8
        elif growth_rate < 1:
            duration *= 1.5  # Slow growth = longer duration
        
        return max(1, int(duration))
    
    async def _generate_trend_insights(self, report: TrendReport, job: AnalysisJob) -> None:
        """Generate insights for the trend report"""
        
        all_trends = (report.trending_hashtags + report.trending_keywords + 
                     report.trending_topics + report.viral_content)
        
        # Identify emerging trends
        report.emerging_trends = [
            trend for trend in all_trends
            if trend.strength == TrendStrength.EMERGING
        ][:10]
        
        # Identify declining trends
        report.declining_trends = [
            trend for trend in all_trends
            if trend.strength == TrendStrength.DECLINING
        ][:10]
        
        # Identify cross-platform trends
        platform_trend_map = defaultdict(list)
        for trend in all_trends:
            for platform in trend.platforms:
                platform_trend_map[trend.content].append(platform)
        
        report.cross_platform_trends = [
            trend for trend in all_trends
            if len(set(trend.platforms)) >= 2
        ][:10]
        
        # Calculate total trends
        report.total_trends_analyzed = len(all_trends)
    
    async def _calculate_report_statistics(self, report: TrendReport) -> None:
        """Calculate statistics for the trend report"""
        
        # Platform activity
        for platform in report.platforms_analyzed:
            platform_trends = []
            for trend_list in [report.trending_hashtags, report.trending_keywords, 
                             report.trending_topics, report.viral_content]:
                platform_trends.extend([t for t in trend_list if platform in t.platforms])
            
            report.platform_activity[platform.value] = len(platform_trends)
        
        # Accuracy metrics (placeholder - would be calculated against known data)
        report.accuracy_metrics = {
            "prediction_accuracy": 0.85,
            "trend_detection_rate": 0.92,
            "false_positive_rate": 0.08
        }
    
    async def add_trend_data(self, trend_data: TrendData) -> None:
        """Add new trend data for analysis"""
        
        self.trend_data.append(trend_data)
        
        # Update trackers
        if trend_data.category == TrendCategory.HASHTAGS:
            self.hashtag_tracker[trend_data.content].append(trend_data)
        elif trend_data.category == TrendCategory.KEYWORDS:
            self.keyword_tracker[trend_data.content].append(trend_data)
        
        # Update statistics
        self.analysis_stats["data_points_processed"] += 1
        
        # Trigger real-time analysis for high-engagement content
        total_engagement = sum(trend_data.engagement_metrics.values())
        if total_engagement > 1000:  # High engagement threshold
            await self._analyze_high_engagement_content(trend_data)
    
    async def _analyze_high_engagement_content(self, trend_data: TrendData) -> None:
        """Analyze high-engagement content in real-time"""
        
        try:
            # Check if this creates a new trending item
            similar_data = [
                data for data in self.trend_data
                if (data.content == trend_data.content and
                    data.platform == trend_data.platform and
                    data.timestamp > datetime.now() - timedelta(hours=24))
            ]
            
            if len(similar_data) >= 5:  # Threshold for trend consideration
                trend_analysis = await self._create_trend_analysis(
                    trend_data.content,
                    trend_data.category,
                    similar_data,
                    [trend_data.platform]
                )
                
                if trend_analysis and trend_analysis.confidence_score > 0.7:
                    self.trend_analyses[trend_analysis.trend_id] = trend_analysis
                    self.logger.info(f"New high-confidence trend detected: {trend_data.content}")
                    
        except Exception as e:
            self.logger.error(f"Error analyzing high-engagement content: {str(e)}")
    
    async def _update_trend_analyses(self) -> None:
        """Update existing trend analyses with new data"""
        
        for trend_id, analysis in self.trend_analyses.items():
            try:
                # Get updated data for this trend
                updated_data = [
                    data for data in self.trend_data
                    if (data.content == analysis.content and
                        data.timestamp > analysis.last_updated - timedelta(hours=1))
                ]
                
                if updated_data:
                    # Recalculate metrics
                    updated_analysis = await self._create_trend_analysis(
                        analysis.content,
                        analysis.category,
                        updated_data,
                        analysis.platforms
                    )
                    
                    if updated_analysis:
                        # Update existing analysis
                        analysis.total_engagement += updated_analysis.total_engagement
                        analysis.growth_rate = updated_analysis.growth_rate
                        analysis.velocity = updated_analysis.velocity
                        analysis.viral_probability = updated_analysis.viral_probability
                        analysis.last_updated = datetime.now()
                        
            except Exception as e:
                self.logger.error(f"Error updating trend analysis {trend_id}: {str(e)}")
    
    async def _detect_emerging_trends(self) -> None:
        """Detect new emerging trends from recent data"""
        
        # Analyze data from the last 2 hours
        recent_cutoff = datetime.now() - timedelta(hours=2)
        recent_data = [data for data in self.trend_data if data.timestamp > recent_cutoff]
        
        if not recent_data:
            return
        
        # Group by content and platform
        content_groups = defaultdict(lambda: defaultdict(list))
        for data in recent_data:
            content_groups[data.content][data.platform].append(data)
        
        # Look for emerging patterns
        for content, platform_data in content_groups.items():
            for platform, data_points in platform_data.items():
                if len(data_points) >= 3:  # Minimum mentions for emerging trend
                    total_engagement = sum(sum(dp.engagement_metrics.values()) for dp in data_points)
                    
                    if total_engagement > 500:  # Threshold for emerging trend
                        # Check if we already have this trend
                        trend_id = hashlib.md5(f"{content}_{data_points[0].category.value}".encode()).hexdigest()
                        
                        if trend_id not in self.trend_analyses:
                            trend_analysis = await self._create_trend_analysis(
                                content,
                                data_points[0].category,
                                data_points,
                                [platform]
                            )
                            
                            if (trend_analysis and 
                                trend_analysis.strength in [TrendStrength.EMERGING, TrendStrength.GROWING]):
                                self.trend_analyses[trend_id] = trend_analysis
                                self.analysis_stats["trends_identified"] += 1
                                self.logger.info(f"Emerging trend detected: {content}")
    
    async def _update_trend_strengths(self) -> None:
        """Update trend strengths based on latest data"""
        
        for trend_id, analysis in self.trend_analyses.items():
            try:
                # Get recent data for this trend
                recent_data = [
                    data for data in self.trend_data
                    if (data.content == analysis.content and
                        data.timestamp > datetime.now() - timedelta(hours=6))
                ]
                
                if recent_data:
                    # Recalculate strength
                    total_engagement = sum(sum(dp.engagement_metrics.values()) for dp in recent_data)
                    growth_rate = await self._calculate_growth_rate(recent_data)
                    
                    time_span = 6  # hours
                    velocity = len(recent_data) / time_span
                    
                    new_strength = self._determine_trend_strength(
                        total_engagement, growth_rate, velocity, recent_data[0].platform
                    )
                    
                    if new_strength != analysis.strength:
                        analysis.strength = new_strength
                        analysis.last_updated = datetime.now()
                        self.logger.debug(f"Updated trend strength for '{analysis.content}': {new_strength.value}")
                        
            except Exception as e:
                self.logger.error(f"Error updating trend strength {trend_id}: {str(e)}")
    
    async def _analyze_real_time_trends(self) -> None:
        """Analyze trends in real-time from recent data"""
        
        # Get data from the last 10 minutes
        recent_cutoff = datetime.now() - timedelta(minutes=10)
        recent_data = [data for data in self.trend_data if data.timestamp > recent_cutoff]
        
        if len(recent_data) < 5:
            return
        
        # Quick analysis for immediate trending detection
        content_engagement = defaultdict(float)
        for data in recent_data:
            content_engagement[data.content] += sum(data.engagement_metrics.values())
        
        # Sort by engagement
        top_content = sorted(content_engagement.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for content, engagement in top_content:
            if engagement > 2000:  # High immediate engagement
                self.logger.info(f"Real-time trending content detected: {content} (engagement: {engagement})")
    
    async def _update_viral_predictions(self) -> None:
        """Update viral probability predictions for existing trends"""
        
        for analysis in self.trend_analyses.values():
            try:
                # Get recent engagement data
                recent_data = [
                    data for data in self.trend_data
                    if (data.content == analysis.content and
                        data.timestamp > datetime.now() - timedelta(hours=3))
                ]
                
                if recent_data:
                    recent_engagement = sum(sum(dp.engagement_metrics.values()) for dp in recent_data)
                    recent_growth = await self._calculate_growth_rate(recent_data)
                    recent_velocity = len(recent_data) / 3  # per hour
                    
                    # Update viral probability
                    analysis.viral_probability = self._calculate_viral_probability(
                        recent_engagement, recent_growth, recent_velocity, analysis.sentiment_score
                    )
                    
                    # Update prediction count
                    if analysis.viral_probability > 0.8:
                        self.analysis_stats["viral_predictions"] += 1
                        
            except Exception as e:
                self.logger.error(f"Error updating viral prediction: {str(e)}")
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an analysis job"""
        
        if job_id not in self.active_jobs:
            return None
        
        job = self.active_jobs[job_id]
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "progress": job.progress,
            "platforms": [p.value for p in job.platforms],
            "categories": [c.value for c in job.categories],
            "analysis_period": [
                job.analysis_period[0].isoformat(),
                job.analysis_period[1].isoformat()
            ],
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "results_available": job.results is not None
        }
    
    def get_trending_content(
        self,
        platform: Optional[PlatformType] = None,
        category: Optional[TrendCategory] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get current trending content"""
        
        filtered_trends = []
        
        for analysis in self.trend_analyses.values():
            if platform and platform not in analysis.platforms:
                continue
            if category and analysis.category != category:
                continue
            
            filtered_trends.append({
                "content": analysis.content,
                "category": analysis.category.value,
                "platforms": [p.value for p in analysis.platforms],
                "strength": analysis.strength.value,
                "total_engagement": analysis.total_engagement,
                "growth_rate": analysis.growth_rate,
                "viral_probability": analysis.viral_probability,
                "sentiment_score": analysis.sentiment_score,
                "confidence_score": analysis.confidence_score
            })
        
        # Sort by engagement and return top results
        filtered_trends.sort(key=lambda x: x["total_engagement"], reverse=True)
        return filtered_trends[:limit]
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get analysis system statistics"""
        
        return {
            **self.analysis_stats,
            "active_jobs": len(self.active_jobs),
            "active_trends": len(self.trend_analyses),
            "data_points_stored": len(self.trend_data),
            "platforms_supported": len(PlatformType),
            "categories_supported": len(TrendCategory)
        }


# Global instance for easy access
_trending_content_analyzer = None

def get_trending_content_analyzer(config: Optional[Dict[str, Any]] = None) -> TrendingContentAnalyzer:
    """Get or create global trending content analyzer instance"""
    global _trending_content_analyzer
    
    if _trending_content_analyzer is None:
        _trending_content_analyzer = TrendingContentAnalyzer(config)
    
    return _trending_content_analyzer


# Example usage and testing
if __name__ == "__main__":
    async def example_usage():
        """Example usage of the Trending Content Analyzer"""
        
        # Initialize the system
        analyzer = get_trending_content_analyzer()
        
        # Add some sample trend data
        sample_data = [
            TrendData(
                content="#sunset",
                platform=PlatformType.INSTAGRAM,
                category=TrendCategory.HASHTAGS,
                engagement_metrics={"likes": 1500, "comments": 200, "shares": 300},
                reach=10000,
                sentiment=0.8
            ),
            TrendData(
                content="AI technology",
                platform=PlatformType.TWITTER,
                category=TrendCategory.KEYWORDS,
                engagement_metrics={"likes": 2000, "retweets": 500, "replies": 150},
                reach=15000,
                sentiment=0.6
            )
        ]
        
        for data in sample_data:
            await analyzer.add_trend_data(data)
        
        # Create analysis job
        job_id = await analyzer.create_analysis_job(
            platforms=[PlatformType.INSTAGRAM, PlatformType.TWITTER],
            categories=[TrendCategory.HASHTAGS, TrendCategory.KEYWORDS]
        )
        
        print(f"Created analysis job: {job_id}")
        
        # Process the job
        report = await analyzer.process_analysis_job(job_id)
        
        print(f"\nAnalysis Report:")
        print(f"Total trends analyzed: {report.total_trends_analyzed}")
        print(f"Trending hashtags: {len(report.trending_hashtags)}")
        print(f"Trending keywords: {len(report.trending_keywords)}")
        print(f"Emerging trends: {len(report.emerging_trends)}")
        
        # Get current trending content
        trending = analyzer.get_trending_content(limit=5)
        print(f"\nCurrent trending content:")
        for trend in trending:
            print(f"- {trend['content']} ({trend['category']}) - Engagement: {trend['total_engagement']}")
        
        # Get statistics
        stats = analyzer.get_analysis_statistics()
        print(f"\nSystem statistics: {json.dumps(stats, indent=2)}")
    
    # Run example if this file is executed directly
    asyncio.run(example_usage())