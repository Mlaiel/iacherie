"""
Advanced Trend Analysis Module for IA Influencer Agent Platform

AI-powered trend detection, prediction, and optimization system for content creators,
influencers, and multi-platform content strategy optimization.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter, defaultdict
import networkx as nx
import pandas as pd
import requests
import json
from textblob import TextBlob
import re

logger = logging.getLogger(__name__)

class TrendType(Enum):
    """Types of trends"""
    CONTENT_THEME = "content_theme"
    HASHTAG = "hashtag"
    MUSIC = "music"
    VISUAL_STYLE = "visual_style"
    COLLABORATION = "collaboration"
    PLATFORM_FEATURE = "platform_feature"
    AUDIENCE_BEHAVIOR = "audience_behavior"
    ENGAGEMENT_PATTERN = "engagement_pattern"

class TrendStatus(Enum):
    """Trend lifecycle status"""
    EMERGING = "emerging"
    RISING = "rising"
    PEAK = "peak"
    DECLINING = "declining"
    STABLE = "stable"
    CYCLICAL = "cyclical"

class Platform(Enum):
    """Supported social media platforms"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"

@dataclass
class TrendData:
    """Trend data point"""
    trend_id: str
    name: str
    trend_type: TrendType
    platforms: List[Platform] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    engagement_metrics: Dict[str, float] = field(default_factory=dict)
    growth_rate: float = 0.0
    peak_engagement: float = 0.0
    geographic_distribution: Dict[str, float] = field(default_factory=dict)
    age_demographics: Dict[str, float] = field(default_factory=dict)
    related_trends: List[str] = field(default_factory=list)
    content_examples: List[str] = field(default_factory=list)
    creators_involved: List[str] = field(default_factory=list)
    status: TrendStatus = TrendStatus.EMERGING
    confidence_score: float = 0.0
    prediction_horizon: timedelta = field(default_factory=lambda: timedelta(days=7))
    first_detected: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TrendPrediction:
    """Trend prediction result"""
    trend_id: str
    predicted_status: TrendStatus
    confidence: float
    growth_prediction: Dict[str, float] = field(default_factory=dict)
    engagement_forecast: Dict[datetime, float] = field(default_factory=dict)
    optimal_timing: Dict[Platform, datetime] = field(default_factory=dict)
    content_recommendations: List[str] = field(default_factory=list)
    hashtag_suggestions: List[str] = field(default_factory=list)
    collaboration_opportunities: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    success_probability: float = 0.0
    recommended_duration: timedelta = field(default_factory=lambda: timedelta(days=3))
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TrendAlert:
    """Trend alert notification"""
    alert_id: str
    trend_id: str
    alert_type: str  # emerging, peak, declining, opportunity
    urgency: str  # low, medium, high, critical
    message: str
    recommended_actions: List[str] = field(default_factory=list)
    target_creators: List[str] = field(default_factory=list)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=6))
    created_at: datetime = field(default_factory=datetime.utcnow)

class TrendAnalyzer:
    """
    Advanced trend analysis and prediction engine
    
    Capabilities:
    - Real-time trend detection across platforms
    - AI-powered trend prediction
    - Content optimization recommendations
    - Platform-specific trend analysis
    - Geographic and demographic trend mapping
    - Viral content pattern recognition
    - Collaboration opportunity identification
    - Trend lifecycle management
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.trends: Dict[str, TrendData] = {}
        self.trend_history: List[TrendData] = []
        self.predictions: List[TrendPrediction] = []
        self.alerts: List[TrendAlert] = []
        self.platform_apis = {}
        self.ml_models = {}
        self.trend_network = nx.Graph()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'update_interval': timedelta(minutes=15),
            'min_engagement_threshold': 1000,
            'trend_confidence_threshold': 0.6,
            'prediction_window': timedelta(days=14),
            'platforms_enabled': [Platform.INSTAGRAM, Platform.TIKTOK, Platform.YOUTUBE, Platform.TWITTER],
            'geographic_regions': ['US', 'EU', 'ASIA', 'GLOBAL'],
            'age_groups': ['13-17', '18-24', '25-34', '35-44', '45+'],
            'content_languages': ['en', 'es', 'fr', 'de', 'pt'],
            'enable_real_time_monitoring': True,
            'enable_predictive_analytics': True,
            'enable_cross_platform_analysis': True,
            'alert_thresholds': {
                'emerging_trend': 0.7,
                'viral_potential': 0.8,
                'peak_detection': 0.9,
                'decline_warning': 0.6
            }
        }
    
    async def initialize(self):
        """Initialize trend analyzer"""
        try:
            logger.info("Initializing trend analyzer...")
            
            # Initialize platform APIs (placeholder - would need real API keys)
            await self._initialize_platform_apis()
            
            # Initialize ML models for trend prediction
            await self._initialize_ml_models()
            
            # Start real-time monitoring if enabled
            if self.config['enable_real_time_monitoring']:
                asyncio.create_task(self._start_real_time_monitoring())
            
            logger.info("Trend analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing trend analyzer: {e}")
    
    async def detect_emerging_trends(
        self,
        platforms: List[Platform] = None,
        time_window: timedelta = None,
        content_type: Optional[str] = None
    ) -> List[TrendData]:
        """Detect emerging trends across platforms"""
        try:
            platforms = platforms or self.config['platforms_enabled']
            time_window = time_window or timedelta(hours=24)
            
            emerging_trends = []
            
            for platform in platforms:
                platform_trends = await self._detect_platform_trends(platform, time_window, content_type)
                emerging_trends.extend(platform_trends)
            
            # Cross-platform trend correlation
            if self.config['enable_cross_platform_analysis']:
                correlated_trends = await self._correlate_cross_platform_trends(emerging_trends)
                emerging_trends.extend(correlated_trends)
            
            # Filter by confidence threshold
            filtered_trends = [
                trend for trend in emerging_trends
                if trend.confidence_score >= self.config['trend_confidence_threshold']
            ]
            
            # Update trend database
            for trend in filtered_trends:
                self.trends[trend.trend_id] = trend
                self.trend_history.append(trend)
            
            # Generate alerts for high-potential trends
            await self._generate_trend_alerts(filtered_trends)
            
            return filtered_trends
            
        except Exception as e:
            logger.error(f"Error detecting emerging trends: {e}")
            return []
    
    async def predict_trend_evolution(
        self,
        trend_id: str,
        prediction_horizon: timedelta = None
    ) -> TrendPrediction:
        """Predict how a trend will evolve"""
        try:
            if trend_id not in self.trends:
                raise ValueError(f"Trend {trend_id} not found")
            
            trend = self.trends[trend_id]
            prediction_horizon = prediction_horizon or self.config['prediction_window']
            
            # Analyze historical patterns
            historical_patterns = await self._analyze_historical_patterns(trend)
            
            # Predict lifecycle status
            predicted_status = await self._predict_trend_status(trend, historical_patterns)
            
            # Forecast engagement
            engagement_forecast = await self._forecast_engagement(trend, prediction_horizon)
            
            # Calculate growth prediction
            growth_prediction = await self._predict_growth_metrics(trend, historical_patterns)
            
            # Determine optimal timing for content creation
            optimal_timing = await self._calculate_optimal_timing(trend)
            
            # Generate content recommendations
            content_recommendations = await self._generate_content_recommendations(trend)
            
            # Suggest hashtags and collaboration opportunities
            hashtag_suggestions = await self._suggest_hashtags(trend)
            collaboration_opportunities = await self._identify_collaboration_opportunities(trend)
            
            # Assess risks
            risk_factors = await self._assess_trend_risks(trend)
            
            # Calculate success probability
            success_probability = await self._calculate_success_probability(trend, historical_patterns)
            
            # Recommend optimal campaign duration
            recommended_duration = await self._recommend_campaign_duration(trend)
            
            prediction = TrendPrediction(
                trend_id=trend_id,
                predicted_status=predicted_status,
                confidence=trend.confidence_score,
                growth_prediction=growth_prediction,
                engagement_forecast=engagement_forecast,
                optimal_timing=optimal_timing,
                content_recommendations=content_recommendations,
                hashtag_suggestions=hashtag_suggestions,
                collaboration_opportunities=collaboration_opportunities,
                risk_factors=risk_factors,
                success_probability=success_probability,
                recommended_duration=recommended_duration
            )
            
            self.predictions.append(prediction)
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting trend evolution: {e}")
            return TrendPrediction(trend_id=trend_id, predicted_status=TrendStatus.STABLE, confidence=0.0)
    
    async def get_personalized_trend_recommendations(
        self,
        creator_id: str,
        creator_profile: Dict[str, Any],
        max_recommendations: int = 10
    ) -> List[Dict[str, Any]]:
        """Get personalized trend recommendations for a creator"""
        try:
            # Analyze creator profile and past content
            creator_analysis = await self._analyze_creator_profile(creator_id, creator_profile)
            
            # Find matching trends
            matching_trends = await self._find_matching_trends(creator_analysis)
            
            # Score trends based on creator fit
            scored_trends = []
            for trend in matching_trends:
                score = await self._calculate_creator_trend_fit(creator_analysis, trend)
                if score > 0.5:  # Minimum fit threshold
                    prediction = await self.predict_trend_evolution(trend.trend_id)
                    
                    recommendation = {
                        'trend': trend,
                        'prediction': prediction,
                        'fit_score': score,
                        'engagement_potential': prediction.success_probability,
                        'recommended_approach': await self._recommend_creator_approach(creator_analysis, trend),
                        'content_ideas': await self._generate_creator_content_ideas(creator_analysis, trend),
                        'timing_recommendation': prediction.optimal_timing,
                        'expected_results': await self._estimate_creator_results(creator_analysis, trend)
                    }
                    scored_trends.append(recommendation)
            
            # Sort by combined score (fit + engagement potential)
            scored_trends.sort(
                key=lambda x: (x['fit_score'] + x['engagement_potential']) / 2,
                reverse=True
            )
            
            return scored_trends[:max_recommendations]
            
        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {e}")
            return []
    
    async def analyze_trend_network(self) -> Dict[str, Any]:
        """Analyze the network of trend relationships"""
        try:
            # Build trend network graph
            await self._build_trend_network()
            
            # Calculate network metrics
            network_metrics = {
                'total_trends': len(self.trend_network.nodes),
                'trend_connections': len(self.trend_network.edges),
                'network_density': nx.density(self.trend_network),
                'clustering_coefficient': nx.average_clustering(self.trend_network),
                'average_path_length': nx.average_shortest_path_length(self.trend_network) if nx.is_connected(self.trend_network) else 0
            }
            
            # Identify trend clusters
            trend_clusters = await self._identify_trend_clusters()
            
            # Find trending influencers/nodes
            central_trends = await self._find_central_trends()
            
            # Detect trend bridges (trends that connect different clusters)
            bridge_trends = await self._detect_bridge_trends()
            
            return {
                'network_metrics': network_metrics,
                'trend_clusters': trend_clusters,
                'central_trends': central_trends,
                'bridge_trends': bridge_trends,
                'network_evolution': await self._analyze_network_evolution(),
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trend network: {e}")
            return {}
    
    async def _detect_platform_trends(
        self,
        platform: Platform,
        time_window: timedelta,
        content_type: Optional[str] = None
    ) -> List[TrendData]:
        """Detect trends on a specific platform"""
        try:
            trends = []
            
            # Platform-specific trend detection logic
            if platform == Platform.INSTAGRAM:
                trends = await self._detect_instagram_trends(time_window, content_type)
            elif platform == Platform.TIKTOK:
                trends = await self._detect_tiktok_trends(time_window, content_type)
            elif platform == Platform.YOUTUBE:
                trends = await self._detect_youtube_trends(time_window, content_type)
            elif platform == Platform.TWITTER:
                trends = await self._detect_twitter_trends(time_window, content_type)
            # Add more platforms as needed
            
            return trends
            
        except Exception as e:
            logger.error(f"Error detecting {platform.value} trends: {e}")
            return []
    
    async def _detect_instagram_trends(
        self,
        time_window: timedelta,
        content_type: Optional[str] = None
    ) -> List[TrendData]:
        """Detect Instagram-specific trends"""
        try:
            trends = []
            
            # Simulate Instagram trend detection (in production, use Instagram API)
            # This would involve analyzing hashtags, engagement patterns, story content, etc.
            
            # Example trending hashtags (would be fetched from API)
            trending_hashtags = [
                '#aesthetic', '#vibe', '#mood', '#inspiration',
                '#creativity', '#art', '#music', '#style'
            ]
            
            for i, hashtag in enumerate(trending_hashtags[:5]):  # Limit to top 5
                trend_id = f"ig_trend_{hashtag}_{int(datetime.utcnow().timestamp())}"
                
                trend = TrendData(
                    trend_id=trend_id,
                    name=hashtag,
                    trend_type=TrendType.HASHTAG,
                    platforms=[Platform.INSTAGRAM],
                    hashtags=[hashtag],
                    engagement_metrics={
                        'posts_count': np.random.randint(10000, 100000),
                        'avg_likes': np.random.randint(1000, 10000),
                        'avg_comments': np.random.randint(50, 500),
                        'growth_rate': np.random.uniform(0.1, 0.5)
                    },
                    growth_rate=np.random.uniform(0.1, 0.5),
                    confidence_score=np.random.uniform(0.6, 0.9),
                    status=TrendStatus.EMERGING if i < 2 else TrendStatus.RISING
                )
                
                trends.append(trend)
            
            return trends
            
        except Exception as e:
            logger.error(f"Error detecting Instagram trends: {e}")
            return []
    
    async def _detect_tiktok_trends(
        self,
        time_window: timedelta,
        content_type: Optional[str] = None
    ) -> List[TrendData]:
        """Detect TikTok-specific trends"""
        try:
            trends = []
            
            # Simulate TikTok trend detection
            trending_sounds = [
                'trending_audio_1', 'trending_audio_2', 'trending_audio_3',
                'viral_song_1', 'viral_song_2'
            ]
            
            for i, sound in enumerate(trending_sounds):
                trend_id = f"tt_trend_{sound}_{int(datetime.utcnow().timestamp())}"
                
                trend = TrendData(
                    trend_id=trend_id,
                    name=f"TikTok Sound: {sound}",
                    trend_type=TrendType.MUSIC,
                    platforms=[Platform.TIKTOK],
                    keywords=[sound, 'viral', 'trending'],
                    engagement_metrics={
                        'videos_count': np.random.randint(50000, 500000),
                        'total_views': np.random.randint(1000000, 100000000),
                        'avg_likes': np.random.randint(5000, 50000),
                        'share_rate': np.random.uniform(0.1, 0.3)
                    },
                    growth_rate=np.random.uniform(0.2, 0.8),
                    confidence_score=np.random.uniform(0.7, 0.95),
                    status=TrendStatus.RISING if i < 3 else TrendStatus.PEAK
                )
                
                trends.append(trend)
            
            return trends
            
        except Exception as e:
            logger.error(f"Error detecting TikTok trends: {e}")
            return []
    
    async def _detect_youtube_trends(
        self,
        time_window: timedelta,
        content_type: Optional[str] = None
    ) -> List[TrendData]:
        """Detect YouTube-specific trends"""
        try:
            trends = []
            
            # Simulate YouTube trend detection
            trending_topics = [
                'Tutorial', 'Review', 'Vlog', 'Challenge', 'Music Cover',
                'Gaming', 'Technology', 'Lifestyle', 'Comedy', 'Education'
            ]
            
            for i, topic in enumerate(trending_topics[:6]):
                trend_id = f"yt_trend_{topic.lower()}_{int(datetime.utcnow().timestamp())}"
                
                trend = TrendData(
                    trend_id=trend_id,
                    name=f"YouTube {topic} Content",
                    trend_type=TrendType.CONTENT_THEME,
                    platforms=[Platform.YOUTUBE],
                    keywords=[topic.lower(), 'youtube', 'content'],
                    engagement_metrics={
                        'videos_count': np.random.randint(1000, 10000),
                        'avg_views': np.random.randint(10000, 1000000),
                        'avg_likes': np.random.randint(500, 50000),
                        'subscriber_growth': np.random.uniform(0.05, 0.2)
                    },
                    growth_rate=np.random.uniform(0.1, 0.4),
                    confidence_score=np.random.uniform(0.6, 0.85),
                    status=TrendStatus.STABLE if i < 4 else TrendStatus.EMERGING
                )
                
                trends.append(trend)
            
            return trends
            
        except Exception as e:
            logger.error(f"Error detecting YouTube trends: {e}")
            return []
    
    async def _detect_twitter_trends(
        self,
        time_window: timedelta,
        content_type: Optional[str] = None
    ) -> List[TrendData]:
        """Detect Twitter-specific trends"""
        try:
            trends = []
            
            # Simulate Twitter trend detection
            trending_topics = [
                'TechNews', 'AI', 'Crypto', 'Music', 'Art',
                'Politics', 'Sports', 'Entertainment', 'Science'
            ]
            
            for i, topic in enumerate(trending_topics[:5]):
                trend_id = f"tw_trend_{topic.lower()}_{int(datetime.utcnow().timestamp())}"
                
                trend = TrendData(
                    trend_id=trend_id,
                    name=f"#{topic}",
                    trend_type=TrendType.HASHTAG,
                    platforms=[Platform.TWITTER],
                    hashtags=[f"#{topic}"],
                    keywords=[topic.lower(), 'twitter', 'trending'],
                    engagement_metrics={
                        'tweets_count': np.random.randint(10000, 100000),
                        'retweets': np.random.randint(5000, 50000),
                        'likes': np.random.randint(20000, 200000),
                        'mentions': np.random.randint(1000, 10000)
                    },
                    growth_rate=np.random.uniform(0.15, 0.6),
                    confidence_score=np.random.uniform(0.65, 0.9),
                    status=TrendStatus.PEAK if i < 2 else TrendStatus.RISING
                )
                
                trends.append(trend)
            
            return trends
            
        except Exception as e:
            logger.error(f"Error detecting Twitter trends: {e}")
            return []
    
    async def _correlate_cross_platform_trends(
        self,
        platform_trends: List[TrendData]
    ) -> List[TrendData]:
        """Find trends that span multiple platforms"""
        try:
            cross_platform_trends = []
            
            # Group trends by keywords and themes
            keyword_groups = defaultdict(list)
            for trend in platform_trends:
                for keyword in trend.keywords:
                    keyword_groups[keyword].append(trend)
            
            # Find keywords that appear across multiple platforms
            for keyword, trends in keyword_groups.items():
                platforms_involved = set(platform for trend in trends for platform in trend.platforms)
                
                if len(platforms_involved) >= 2:  # Cross-platform trend
                    # Create combined cross-platform trend
                    combined_trend_id = f"cross_platform_{keyword}_{int(datetime.utcnow().timestamp())}"
                    
                    combined_engagement = {}
                    total_confidence = 0
                    for trend in trends:
                        for metric, value in trend.engagement_metrics.items():
                            if metric not in combined_engagement:
                                combined_engagement[metric] = 0
                            combined_engagement[metric] += value
                        total_confidence += trend.confidence_score
                    
                    cross_platform_trend = TrendData(
                        trend_id=combined_trend_id,
                        name=f"Cross-Platform: {keyword}",
                        trend_type=TrendType.CONTENT_THEME,
                        platforms=list(platforms_involved),
                        keywords=[keyword],
                        engagement_metrics=combined_engagement,
                        growth_rate=sum(trend.growth_rate for trend in trends) / len(trends),
                        confidence_score=total_confidence / len(trends),
                        status=TrendStatus.RISING,
                        related_trends=[trend.trend_id for trend in trends]
                    )
                    
                    cross_platform_trends.append(cross_platform_trend)
            
            return cross_platform_trends
            
        except Exception as e:
            logger.error(f"Error correlating cross-platform trends: {e}")
            return []
    
    async def _generate_trend_alerts(self, trends: List[TrendData]):
        """Generate alerts for significant trends"""
        try:
            for trend in trends:
                # Check for alert conditions
                if trend.confidence_score >= self.config['alert_thresholds']['viral_potential']:
                    alert = TrendAlert(
                        alert_id=f"alert_{trend.trend_id}_{int(datetime.utcnow().timestamp())}",
                        trend_id=trend.trend_id,
                        alert_type="viral_potential",
                        urgency="high",
                        message=f"High viral potential detected: {trend.name}",
                        recommended_actions=[
                            "Create content immediately",
                            "Engage with trend hashtags",
                            "Collaborate with trending creators"
                        ]
                    )
                    self.alerts.append(alert)
                
                elif trend.status == TrendStatus.EMERGING and trend.confidence_score >= self.config['alert_thresholds']['emerging_trend']:
                    alert = TrendAlert(
                        alert_id=f"alert_{trend.trend_id}_{int(datetime.utcnow().timestamp())}",
                        trend_id=trend.trend_id,
                        alert_type="emerging_trend",
                        urgency="medium",
                        message=f"Emerging trend detected: {trend.name}",
                        recommended_actions=[
                            "Monitor trend development",
                            "Prepare content strategy",
                            "Research trend context"
                        ]
                    )
                    self.alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error generating trend alerts: {e}")
    
    async def _initialize_platform_apis(self):
        """Initialize platform API connections"""
        # Placeholder for platform API initialization
        # In production, would initialize real API connections
        self.platform_apis = {
            Platform.INSTAGRAM: None,  # Instagram Basic Display API
            Platform.TIKTOK: None,     # TikTok API
            Platform.YOUTUBE: None,    # YouTube Data API
            Platform.TWITTER: None,    # Twitter API v2
            Platform.SPOTIFY: None     # Spotify Web API
        }
    
    async def _initialize_ml_models(self):
        """Initialize ML models for trend prediction"""
        try:
            # Initialize trend classification model
            self.ml_models['trend_classifier'] = None  # Would load trained model
            
            # Initialize engagement prediction model
            self.ml_models['engagement_predictor'] = None  # Would load trained model
            
            # Initialize lifecycle prediction model
            self.ml_models['lifecycle_predictor'] = None  # Would load trained model
            
            logger.info("ML models initialized (placeholder)")
            
        except Exception as e:
            logger.error(f"Error initializing ML models: {e}")
    
    async def _start_real_time_monitoring(self):
        """Start real-time trend monitoring"""
        try:
            while True:
                # Detect new trends
                new_trends = await self.detect_emerging_trends()
                
                # Update existing trends
                await self._update_existing_trends()
                
                # Clean up old trends
                await self._cleanup_old_trends()
                
                # Wait for next update
                await asyncio.sleep(self.config['update_interval'].total_seconds())
                
        except Exception as e:
            logger.error(f"Error in real-time monitoring: {e}")
    
    async def get_trending_report(
        self,
        time_period: timedelta = None,
        platforms: List[Platform] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive trending report"""
        try:
            time_period = time_period or timedelta(days=7)
            platforms = platforms or self.config['platforms_enabled']
            cutoff_time = datetime.utcnow() - time_period
            
            # Filter trends by time period and platforms
            relevant_trends = [
                trend for trend in self.trends.values()
                if trend.last_updated >= cutoff_time and
                any(platform in trend.platforms for platform in platforms)
            ]
            
            # Categorize trends by status
            trends_by_status = defaultdict(list)
            for trend in relevant_trends:
                trends_by_status[trend.status].append(trend)
            
            # Platform analysis
            platform_analysis = {}
            for platform in platforms:
                platform_trends = [t for t in relevant_trends if platform in t.platforms]
                platform_analysis[platform.value] = {
                    'total_trends': len(platform_trends),
                    'emerging_trends': len([t for t in platform_trends if t.status == TrendStatus.EMERGING]),
                    'peak_trends': len([t for t in platform_trends if t.status == TrendStatus.PEAK]),
                    'avg_confidence': np.mean([t.confidence_score for t in platform_trends]) if platform_trends else 0,
                    'top_trends': sorted(platform_trends, key=lambda x: x.confidence_score, reverse=True)[:5]
                }
            
            # Generate recommendations
            recommendations = await self._generate_trending_recommendations(relevant_trends)
            
            return {
                'report_period': {
                    'start': cutoff_time,
                    'end': datetime.utcnow(),
                    'duration': time_period
                },
                'summary': {
                    'total_trends': len(relevant_trends),
                    'emerging_count': len(trends_by_status[TrendStatus.EMERGING]),
                    'rising_count': len(trends_by_status[TrendStatus.RISING]),
                    'peak_count': len(trends_by_status[TrendStatus.PEAK]),
                    'declining_count': len(trends_by_status[TrendStatus.DECLINING])
                },
                'trends_by_status': {status.value: trends for status, trends in trends_by_status.items()},
                'platform_analysis': platform_analysis,
                'top_trends': sorted(relevant_trends, key=lambda x: x.confidence_score, reverse=True)[:10],
                'recommendations': recommendations,
                'alerts_generated': len(self.alerts),
                'generated_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error generating trending report: {e}")
            return {}
