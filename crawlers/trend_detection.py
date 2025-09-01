"""Trend Detection Engine
=====================

Professional trend detection and market intelligence system.
Implements advanced AI for identifying emerging trends, viral patterns, and market opportunities.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
from collections import defaultdict, Counter
import statistics
import math

import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from textblob import TextBlob
import yfinance as yf
from pytrends.request import TrendReq

from ..core.config import get_settings
from ..core.exceptions import TrendAnalysisError
from ..database.models import TrendData, MarketIntelligence
from ..utils.cache_manager import CacheManager
from ..utils.metrics_collector import MetricsCollector
from ..utils.time_series_analyzer import TimeSeriesAnalyzer

logger = logging.getLogger(__name__)
settings = get_settings()

class TrendType(Enum):
    """
Trend type classification."""

    VIRAL = "viral"
    EMERGING = "emerging"
    DECLINING = "declining"
    STABLE = "stable"
    SEASONAL = "seasonal"
    BREAKING = "breaking"

class TrendScope(Enum):
    """Trend scope classification."""

    GLOBAL = "global"
    REGIONAL = "regional"
    NICHE = "niche"
    PLATFORM_SPECIFIC = "platform_specific"
    DEMOGRAPHIC_SPECIFIC = "demographic_specific"

class TrendCategory(Enum):
    """Trend category classification."""

    MUSIC = "music"
    ENTERTAINMENT = "entertainment"
    TECHNOLOGY = "technology"
    FASHION = "fashion"
    LIFESTYLE = "lifestyle"
    NEWS = "news"
    SPORTS = "sports"
    GAMING = "gaming"
    BUSINESS = "business"
    EDUCATION = "education"

@dataclass
class TrendSignal:
    """Individual trend signal data."""
    signal_id: str
    content: str
    source_platform: str
    timestamp: datetime
    engagement_metrics: Dict[str, int]
    sentiment_score: float
    reach_estimate: int
    influence_score: float
    hashtags: List[str]
    mentions: List[str]
    geographic_data: Optional[Dict[str, Any]]

@dataclass
class TrendPattern:
    """
Detected trend pattern."""
    trend_id: str
    trend_type: TrendType
    trend_scope: TrendScope
    category: TrendCategory
    keywords: List[str]
    confidence_score: float
    growth_rate: float
    peak_prediction: Optional[datetime]
    duration_estimate: int  # days
    audience_demographics: Dict[str, Any]
    related_trends: List[str]
    monetization_opportunities: List[Dict[str, Any]]
    risk_factors: List[str]

@dataclass
class MarketOpportunity:
    """
Market opportunity identification."""
    opportunity_id: str
    title: str
    description: str
    market_size_estimate: float
    competition_level: str
    entry_barriers: List[str]
    success_probability: float
    roi_estimate: float
    time_to_market: int  # days
    required_resources: Dict[str, Any]
    key_metrics: Dict[str, float]

@dataclass
class ViralPrediction:
    """
Viral content prediction."""
    content_id: str
    viral_probability: float
    peak_reach_estimate: int
    viral_timeline: Dict[str, int]  # hour -> engagement
    amplification_factors: List[str]
    critical_mass_threshold: int
    decay_rate: float
    geographic_spread: Dict[str, float]

class TrendDetectionEngine:
    """
    Advanced trend detection and market intelligence engine.
    
    Features:
    - Real-time trend identification
    - Viral pattern prediction
    - Market opportunity analysis
    - Cross-platform trend correlation
    - Demographic trend analysis
    - Monetization opportunity detection
    """
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.metrics_collector = MetricsCollector()
        self.time_series_analyzer = TimeSeriesAnalyzer()
        self._initialize_trend_models()
        
    def _initialize_trend_models(self):
        """
Initialize trend detection models and data sources."""
        try:
            # Google Trends API
            self.pytrends = TrendReq(hl='en-US', tz=360)
            
            # Clustering models for pattern detection
            self.trend_clusterer = DBSCAN(eps=0.3, min_samples=5)
            self.content_clusterer = KMeans(n_clusters=10, random_state=42)
            
            # Preprocessing tools
            self.scaler = StandardScaler()
            self.pca = PCA(n_components=0.95)  # Keep 95% variance
            
            # Network analysis for influence mapping
            self.influence_graph = nx.DiGraph()
            
            # Trend detection parameters
            self.viral_threshold = 10000  # Minimum reach for viral classification
            self.trending_window = timedelta(hours=24)
            self.emergence_threshold = 5  # Minimum signals for trend emergence
            
            logger.info("Trend detection models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize trend models: {e}")
            raise TrendAnalysisError(f"Trend model initialization failed: {e}")
    
    async def analyze_real_time_trends(
        self,
        platform_data: Dict[str, List[TrendSignal]],
        time_window: Optional[timedelta] = None
    ) -> List[TrendPattern]:
        """
        Analyze real-time trends across multiple platforms.
        
        Args:
            platform_data: Dictionary mapping platform names to trend signals
            time_window: Time window for trend analysis
            
        Returns:
            List of detected trend patterns
        """
        try:
            if time_window is None:
                time_window = self.trending_window
            
            # Aggregate signals from all platforms
            all_signals = []
            for platform, signals in platform_data.items():
                all_signals.extend(signals)
            
            # Filter signals by time window
            cutoff_time = datetime.now() - time_window
            recent_signals = [
                signal for signal in all_signals 
                if signal.timestamp >= cutoff_time
            ]
            
            if len(recent_signals) < self.emergence_threshold:
                return []
            
            # Extract features for clustering
            signal_features = self._extract_signal_features(recent_signals)
            
            # Detect trend clusters
            trend_clusters = self._cluster_trends(signal_features, recent_signals)
            
            # Analyze each cluster for trend patterns
            trend_patterns = []
            for cluster_id, cluster_signals in trend_clusters.items():
                if len(cluster_signals) >= self.emergence_threshold:
                    pattern = await self._analyze_trend_cluster(cluster_signals)
                    if pattern:
                        trend_patterns.append(pattern)
            
            # Rank trends by significance
            trend_patterns.sort(key=lambda x: x.confidence_score, reverse=True)
            
            # Cache results
            await self.cache_manager.set(
                "real_time_trends",
                [asdict(pattern) for pattern in trend_patterns],
                ttl=300  # 5 minutes
            )
            
            self.metrics_collector.increment("trend_analysis_completed")
            self.metrics_collector.gauge("detected_trends_count", len(trend_patterns))
            
            return trend_patterns
            
        except Exception as e:
            logger.error(f"Real-time trend analysis failed: {e}")
            self.metrics_collector.increment("trend_analysis_failed")
            raise TrendAnalysisError(f"Real-time trend analysis failed: {e}")
    
    async def predict_viral_potential(
        self,
        content_data: Dict[str, Any],
        platform_context: str,
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> ViralPrediction:
        """
        Predict viral potential for content.
        
        Args:
            content_data: Content data including text, engagement metrics, etc.
            platform_context: Platform where content will be published
            historical_data: Historical viral content data for training
            
        Returns:
            Viral prediction analysis
        """
        try:
            content_id = content_data.get('id', 'unknown')
            
            # Extract viral indicators
            viral_indicators = self._extract_viral_indicators(content_data, platform_context)
            
            # Calculate base viral probability
            base_probability = self._calculate_base_viral_probability(viral_indicators)
            
            # Apply platform-specific modifiers
            platform_modifier = self._get_platform_viral_modifier(platform_context)
            adjusted_probability = min(1.0, base_probability * platform_modifier)
            
            # Predict timeline and reach
            viral_timeline = self._predict_viral_timeline(viral_indicators, adjusted_probability)
            peak_reach = self._estimate_peak_reach(viral_indicators, adjusted_probability)
            
            # Identify amplification factors
            amplification_factors = self._identify_amplification_factors(viral_indicators)
            
            # Calculate critical mass and decay
            critical_mass = self._calculate_critical_mass(viral_indicators)
            decay_rate = self._calculate_decay_rate(viral_indicators)
            
            # Predict geographic spread
            geographic_spread = self._predict_geographic_spread(viral_indicators)
            
            prediction = ViralPrediction(
                content_id=content_id,
                viral_probability=adjusted_probability,
                peak_reach_estimate=peak_reach,
                viral_timeline=viral_timeline,
                amplification_factors=amplification_factors,
                critical_mass_threshold=critical_mass,
                decay_rate=decay_rate,
                geographic_spread=geographic_spread
            )
            
            # Cache prediction
            await self.cache_manager.set(
                f"viral_prediction:{content_id}",
                asdict(prediction),
                ttl=3600
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Viral prediction failed: {e}")
            raise TrendAnalysisError(f"Viral prediction failed: {e}")
    
    async def identify_market_opportunities(
        self,
        trend_patterns: List[TrendPattern],
        market_data: Optional[Dict[str, Any]] = None
    ) -> List[MarketOpportunity]:
        """
        Identify market opportunities from trend patterns.
        
        Args:
            trend_patterns: Detected trend patterns
            market_data: Additional market intelligence data
            
        Returns:
            List of identified market opportunities
        """
        try:
            opportunities = []
            
            for trend in trend_patterns:
                # Skip declining trends for opportunity analysis
                if trend.trend_type == TrendType.DECLINING:
                    continue
                
                # Analyze market potential
                market_size = self._estimate_market_size(trend)
                competition_level = self._assess_competition_level(trend)
                
                if market_size > 10000:  # Minimum viable market size
                    opportunity = await self._create_market_opportunity(
                        trend, market_size, competition_level
                    )
                    if opportunity:
                        opportunities.append(opportunity)
            
            # Rank opportunities by ROI potential
            opportunities.sort(key=lambda x: x.roi_estimate, reverse=True)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Market opportunity identification failed: {e}")
            raise TrendAnalysisError(f"Market opportunity identification failed: {e}")
    
    async def analyze_trend_correlations(
        self,
        trends: List[TrendPattern],
        external_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[str]]:
        """
        Analyze correlations between trends and external factors.
        
        Args:
            trends: List of trend patterns to analyze
            external_data: External data sources (stock market, weather, events)
            
        Returns:
            Dictionary mapping trends to correlated factors
        """
        try:
            correlations = {}
            
            # Create feature matrix for correlation analysis
            trend_features = self._create_trend_feature_matrix(trends)
            
            # Calculate trend-to-trend correlations
            if len(trend_features) > 1:
                correlation_matrix = np.corrcoef(trend_features)
                
                for i, trend in enumerate(trends):
                    correlated_trends = []
                    for j, other_trend in enumerate(trends):
                        if i != j and abs(correlation_matrix[i][j]) > 0.7:
                            correlated_trends.append(other_trend.trend_id)
                    
                    correlations[trend.trend_id] = correlated_trends
            
            # Analyze external correlations if data provided
            if external_data:
                external_correlations = await self._analyze_external_correlations(
                    trends, external_data
                )
                
                for trend_id, external_factors in external_correlations.items():
                    if trend_id in correlations:
                        correlations[trend_id].extend(external_factors)
                    else:
                        correlations[trend_id] = external_factors
            
            return correlations
            
        except Exception as e:
            logger.error(f"Trend correlation analysis failed: {e}")
            raise TrendAnalysisError(f"Trend correlation analysis failed: {e}")
    
    def _extract_signal_features(self, signals: List[TrendSignal]) -> np.ndarray:
        """Extract features from trend signals for clustering."""
        features = []
        
        for signal in signals:
            feature_vector = [
                signal.engagement_metrics.get('likes', 0),
                signal.engagement_metrics.get('shares', 0),
                signal.engagement_metrics.get('comments', 0),
                signal.sentiment_score,
                signal.reach_estimate,
                signal.influence_score,
                len(signal.hashtags),
                len(signal.mentions),
                len(signal.content.split()),  # Word count
                signal.timestamp.hour,  # Time of day
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def _cluster_trends(
        self, 
        features: np.ndarray, 
        signals: List[TrendSignal]
    ) -> Dict[int, List[TrendSignal]]:
        """
Cluster trend signals using machine learning."""
        # Normalize features
        features_scaled = self.scaler.fit_transform(features)
        
        # Apply clustering
        cluster_labels = self.trend_clusterer.fit_predict(features_scaled)
        
        # Group signals by cluster
        clusters = defaultdict(list)
        for i, label in enumerate(cluster_labels):
            if label != -1:  # Ignore noise points
                clusters[label].append(signals[i])
        
        return dict(clusters)
    
    async def _analyze_trend_cluster(self, cluster_signals: List[TrendSignal]) -> Optional[TrendPattern]:
        """
Analyze a cluster of signals to identify trend pattern."""
        if not cluster_signals:
            return None
        
        # Extract common keywords and hashtags
        all_content = ' '.join([signal.content for signal in cluster_signals])
        all_hashtags = []
        for signal in cluster_signals:
            all_hashtags.extend(signal.hashtags)
        
        # Find most common elements
        hashtag_counter = Counter(all_hashtags)
        top_hashtags = [tag for tag, count in hashtag_counter.most_common(10)]
        
        # Analyze temporal pattern
        timestamps = [signal.timestamp for signal in cluster_signals]
        time_span = max(timestamps) - min(timestamps)
        
        # Calculate growth metrics
        engagement_values = []
        for signal in cluster_signals:
            total_engagement = sum(signal.engagement_metrics.values())
            engagement_values.append(total_engagement)
        
        avg_engagement = statistics.mean(engagement_values) if engagement_values else 0
        growth_rate = self._calculate_growth_rate(cluster_signals)
        
        # Determine trend type
        trend_type = self._classify_trend_type(cluster_signals, growth_rate)
        
        # Determine scope and category
        trend_scope = self._determine_trend_scope(cluster_signals)
        category = self._categorize_trend(all_content, top_hashtags)
        
        # Calculate confidence score
        confidence = self._calculate_trend_confidence(cluster_signals, growth_rate)
        
        # Generate predictions
        peak_prediction = self._predict_trend_peak(cluster_signals, trend_type)
        duration_estimate = self._estimate_trend_duration(trend_type, growth_rate)
        
        # Analyze demographics
        demographics = self._analyze_trend_demographics(cluster_signals)
        
        # Find related trends
        related_trends = await self._find_related_trends(top_hashtags, category)
        
        # Identify monetization opportunities
        monetization_ops = self._identify_monetization_opportunities(
            category, avg_engagement, trend_scope
        )
        
        # Assess risk factors
        risk_factors = self._assess_trend_risks(trend_type, category, growth_rate)
        
        trend_id = f"trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(all_content) % 10000}"
        
        return TrendPattern(
            trend_id=trend_id,
            trend_type=trend_type,
            trend_scope=trend_scope,
            category=category,
            keywords=top_hashtags,
            confidence_score=confidence,
            growth_rate=growth_rate,
            peak_prediction=peak_prediction,
            duration_estimate=duration_estimate,
            audience_demographics=demographics,
            related_trends=related_trends,
            monetization_opportunities=monetization_ops,
            risk_factors=risk_factors
        )
    
    def _extract_viral_indicators(self, content_data: Dict[str, Any], platform: str) -> Dict[str, float]:
        """Extract indicators that predict viral potential."""
        indicators = {}
        
        # Content characteristics
        text = content_data.get('text', '')
        indicators['text_length'] = len(text.split())
        indicators['sentiment'] = TextBlob(text).sentiment.polarity
        indicators['hashtag_count'] = len(content_data.get('hashtags', []))
        indicators['mention_count'] = len(content_data.get('mentions', []))
        
        # Engagement signals
        metrics = content_data.get('engagement', {})
        indicators['initial_likes'] = metrics.get('likes', 0)
        indicators['initial_shares'] = metrics.get('shares', 0)
        indicators['initial_comments'] = metrics.get('comments', 0)
        
        # Timing factors
        post_time = content_data.get('timestamp', datetime.now())
        indicators['hour_of_day'] = post_time.hour
        indicators['day_of_week'] = post_time.weekday()
        
        # Creator influence
        creator_data = content_data.get('creator', {})
        indicators['creator_followers'] = creator_data.get('followers', 0)
        indicators['creator_engagement_rate'] = creator_data.get('engagement_rate', 0)
        
        # Platform-specific factors
        indicators['platform_reach'] = self._get_platform_reach_factor(platform)
        
        return indicators
    
    def _calculate_base_viral_probability(self, indicators: Dict[str, float]) -> float:
        """
Calculate base viral probability from indicators."""
        # Weighted scoring system
        score = 0.0
        
        # Content quality indicators
        if 10 <= indicators.get('text_length', 0) <= 100:  # Optimal length
            score += 0.15
        
        if indicators.get('sentiment', 0) > 0.2:  # Positive sentiment
            score += 0.1
        
        if indicators.get('hashtag_count', 0) >= 3:  # Good hashtag usage
            score += 0.1
        
        # Early engagement indicators (most important)
        initial_engagement = (
            indicators.get('initial_likes', 0) + 
            indicators.get('initial_shares', 0) * 3 +  # Shares weighted more
            indicators.get('initial_comments', 0) * 2
        )
        
        if initial_engagement > 100:
            score += 0.3
        elif initial_engagement > 50:
            score += 0.2
        elif initial_engagement > 20:
            score += 0.1
        
        # Creator influence
        followers = indicators.get('creator_followers', 0)
        if followers > 100000:
            score += 0.15
        elif followers > 10000:
            score += 0.1
        elif followers > 1000:
            score += 0.05
        
        # Timing optimization
        hour = indicators.get('hour_of_day', 12)
        if hour in [19, 20, 21]:  # Peak engagement hours
            score += 0.05
        
        return min(1.0, score)
    
    def _get_platform_viral_modifier(self, platform: str) -> float:
        """
Get platform-specific viral potential modifier."""
        modifiers = {
            'tiktok': 1.5,      # High viral potential
            'instagram': 1.2,    # Good viral potential
            'twitter': 1.3,      # Good for rapid spread
            'youtube': 1.1,      # Slower but lasting viral content
            'facebook': 1.0,     # Baseline
            'linkedin': 0.8,     # Lower viral potential
            'reddit': 1.4,       # High viral potential in niches
        }
        return modifiers.get(platform.lower(), 1.0)
    
    def _predict_viral_timeline(self, indicators: Dict[str, float], probability: float) -> Dict[str, int]:
        """
Predict viral content timeline."""
        timeline = {}
        
        if probability < 0.3:
            # Low viral potential - minimal engagement
            for hour in range(24):
                timeline[str(hour)] = int(indicators.get('initial_likes', 10) * (1 + hour * 0.1))
        else:
            # High viral potential - exponential then decay
            peak_hour = 6 + int(probability * 10)  # Peak between 6-16 hours
            peak_engagement = int(10000 * probability)
            
            for hour in range(24):
                if hour <= peak_hour:
                    # Growth phase
                    growth_factor = (hour / peak_hour) ** 2
                    engagement = int(peak_engagement * growth_factor)
                else:
                    # Decay phase
                    decay_factor = math.exp(-(hour - peak_hour) * 0.3)
                    engagement = int(peak_engagement * decay_factor)
                
                timeline[str(hour)] = max(10, engagement)
        
        return timeline
    
    def _estimate_peak_reach(self, indicators: Dict[str, float], probability: float) -> int:
        """
Estimate peak reach for viral content."""
        base_reach = indicators.get('creator_followers', 1000)
        viral_multiplier = 1 + (probability * 50)  # Up to 50x multiplier
        platform_factor = indicators.get('platform_reach', 1.0)
        
        peak_reach = int(base_reach * viral_multiplier * platform_factor)
        return min(10000000, peak_reach)  # Cap at 10M
    
    def _identify_amplification_factors(self, indicators: Dict[str, float]) -> List[str]:
        """
Identify factors that could amplify viral spread."""
        factors = []
        
        if indicators.get('sentiment', 0) > 0.5:
            factors.append("high_positive_sentiment")
        
        if indicators.get('hashtag_count', 0) >= 5:
            factors.append("effective_hashtag_strategy")
        
        if indicators.get('creator_followers', 0) > 50000:
            factors.append("influential_creator")
        
        if indicators.get('initial_shares', 0) > indicators.get('initial_likes', 0) * 0.1:
            factors.append("high_shareability")
        
        hour = indicators.get('hour_of_day', 12)
        if hour in [19, 20, 21]:
            factors.append("optimal_posting_time")
        
        return factors
    
    def _calculate_critical_mass(self, indicators: Dict[str, float]) -> int:
        """Calculate critical mass threshold for viral acceleration."""
        base_threshold = 1000
        creator_factor = min(5.0, indicators.get('creator_followers', 1000) / 10000)
        platform_factor = indicators.get('platform_reach', 1.0)
        
        return int(base_threshold * creator_factor * platform_factor)
    
    def _calculate_decay_rate(self, indicators: Dict[str, float]) -> float:
        """
Calculate viral content decay rate."""
        # Base decay rate
        decay = 0.3
        
        # Content quality affects longevity
        if indicators.get('text_length', 0) > 50:  # Substantial content
            decay -= 0.1
        
        if indicators.get('sentiment', 0) > 0.3:  # Positive content lasts longer
            decay -= 0.05
        
        return max(0.1, decay)
    
    def _predict_geographic_spread(self, indicators: Dict[str, float]) -> Dict[str, float]:
        """
Predict geographic spread of viral content."""
        # Simplified geographic spread model
        base_spread = {
            'local': 0.4,
            'national': 0.3,
            'international': 0.2,
            'global': 0.1
        }
        
        # Adjust based on creator influence
        followers = indicators.get('creator_followers', 1000)
        if followers > 1000000:  # Global influencer
            base_spread['global'] += 0.3
            base_spread['local'] -= 0.2
        elif followers > 100000:  # National influencer
            base_spread['national'] += 0.2
            base_spread['local'] -= 0.1
        
        # Normalize to sum to 1.0
        total = sum(base_spread.values())
        return {k: v/total for k, v in base_spread.items()}
    
    def _calculate_growth_rate(self, signals: List[TrendSignal]) -> float:
        """
Calculate trend growth rate from signals."""
        if len(signals) < 2:
            return 0.0
        
        # Sort by timestamp
        sorted_signals = sorted(signals, key=lambda x: x.timestamp)
        
        # Calculate engagement over time
        engagement_over_time = []
        for signal in sorted_signals:
            total_engagement = sum(signal.engagement_metrics.values())
            engagement_over_time.append(total_engagement)
        
        # Simple growth rate calculation
        if len(engagement_over_time) >= 2:
            start_engagement = engagement_over_time[0] or 1
            end_engagement = engagement_over_time[-1] or 1
            time_diff = (sorted_signals[-1].timestamp - sorted_signals[0].timestamp).total_seconds() / 3600  # hours
            
            if time_diff > 0:
                growth_rate = (end_engagement - start_engagement) / (start_engagement * time_diff)
                return max(-1.0, min(10.0, growth_rate))  # Clamp between -100% and 1000% per hour
        
        return 0.0
    
    def _classify_trend_type(self, signals: List[TrendSignal], growth_rate: float) -> TrendType:
        """
Classify trend type based on signals and growth rate."""
        total_reach = sum(signal.reach_estimate for signal in signals)
        
        if total_reach > self.viral_threshold and growth_rate > 2.0:
            return TrendType.VIRAL
        elif growth_rate > 0.5:
            return TrendType.EMERGING
        elif growth_rate < -0.2:
            return TrendType.DECLINING
        elif abs(growth_rate) < 0.1:
            return TrendType.STABLE
        else:
            # Check for seasonal patterns
            timestamps = [signal.timestamp for signal in signals]
            if self._detect_seasonal_pattern(timestamps):
                return TrendType.SEASONAL
            else:
                return TrendType.BREAKING
    
    def _detect_seasonal_pattern(self, timestamps: List[datetime]) -> bool:
        """
Detect if timestamps show seasonal patterns."""
        # Simplified seasonal detection
        hours = [ts.hour for ts in timestamps]
        days = [ts.weekday() for ts in timestamps]
        
        # Check for consistent timing patterns
        hour_variance = statistics.variance(hours) if len(hours) > 1 else 0
        day_variance = statistics.variance(days) if len(days) > 1 else 0
        
        return hour_variance < 10 and day_variance < 2  # Low variance indicates pattern
    
    def _determine_trend_scope(self, signals: List[TrendSignal]) -> TrendScope:
        """
Determine the scope of a trend."""
        total_reach = sum(signal.reach_estimate for signal in signals)
        platforms = set(signal.source_platform for signal in signals)
        
        if total_reach > 1000000 and len(platforms) > 3:
            return TrendScope.GLOBAL
        elif total_reach > 100000:
            return TrendScope.REGIONAL
        elif len(platforms) == 1:
            return TrendScope.PLATFORM_SPECIFIC
        else:
            return TrendScope.NICHE
    
    def _categorize_trend(self, content: str, hashtags: List[str]) -> TrendCategory:
        """
Categorize trend based on content and hashtags."""
        content_lower = content.lower()
        hashtags_lower = [tag.lower() for tag in hashtags]
        
        # Category keywords
        category_keywords = {
            TrendCategory.MUSIC: ['music', 'song', 'album', 'artist', 'concert', 'spotify'],
            TrendCategory.TECHNOLOGY: ['tech', 'ai', 'software', 'app', 'digital', 'coding'],
            TrendCategory.ENTERTAINMENT: ['movie', 'tv', 'show', 'celebrity', 'entertainment'],
            TrendCategory.SPORTS: ['sports', 'game', 'team', 'player', 'match', 'championship'],
            TrendCategory.NEWS: ['news', 'breaking', 'update', 'report', 'announcement'],
            TrendCategory.LIFESTYLE: ['lifestyle', 'health', 'fitness', 'food', 'travel'],
            TrendCategory.FASHION: ['fashion', 'style', 'clothing', 'outfit', 'trend'],
            TrendCategory.GAMING: ['gaming', 'game', 'esports', 'streamer', 'twitch'],
            TrendCategory.BUSINESS: ['business', 'startup', 'entrepreneur', 'investment'],
            TrendCategory.EDUCATION: ['education', 'learning', 'course', 'tutorial', 'study']
        }
        
        # Score each category
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in content_lower:
                    score += 2
                if any(keyword in hashtag for hashtag in hashtags_lower):
                    score += 1
            category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return TrendCategory.ENTERTAINMENT  # Default
    
    def _calculate_trend_confidence(self, signals: List[TrendSignal], growth_rate: float) -> float:
        """
Calculate confidence score for trend detection."""
        # Base confidence from signal count
        signal_confidence = min(1.0, len(signals) / 20)  # Max confidence at 20 signals
        
        # Engagement consistency
        engagement_values = [sum(signal.engagement_metrics.values()) for signal in signals]
        if len(engagement_values) > 1:
            avg_engagement = statistics.mean(engagement_values)
            engagement_variance = statistics.variance(engagement_values)
            consistency_score = 1.0 / (1.0 + engagement_variance / max(avg_engagement, 1))
        else:
            consistency_score = 0.5
        
        # Growth rate confidence
        growth_confidence = min(1.0, abs(growth_rate) / 2.0)  # Higher growth = higher confidence
        
        # Platform diversity
        platforms = set(signal.source_platform for signal in signals)
        platform_confidence = min(1.0, len(platforms) / 5)  # Max confidence at 5 platforms
        
        # Weighted average
        confidence = (
            signal_confidence * 0.3 +
            consistency_score * 0.25 +
            growth_confidence * 0.25 +
            platform_confidence * 0.2
        )
        
        return confidence
    
    def _predict_trend_peak(self, signals: List[TrendSignal], trend_type: TrendType) -> Optional[datetime]:
        """
Predict when trend will reach its peak."""
        if trend_type == TrendType.DECLINING:
            return None
        
        # Get trend start time
        start_time = min(signal.timestamp for signal in signals)
        
        # Estimate peak based on trend type
        peak_hours = {
            TrendType.VIRAL: 12,      # 12 hours to peak
            TrendType.EMERGING: 72,   # 3 days to peak
            TrendType.BREAKING: 6,    # 6 hours to peak
            TrendType.SEASONAL: 168,  # 1 week to peak
            TrendType.STABLE: None    # No clear peak
        }
        
        hours_to_peak = peak_hours.get(trend_type)
        if hours_to_peak:
            return start_time + timedelta(hours=hours_to_peak)
        
        return None
    
    def _estimate_trend_duration(self, trend_type: TrendType, growth_rate: float) -> int:
        """
Estimate trend duration in days."""
        base_durations = {
            TrendType.VIRAL: 3,
            TrendType.EMERGING: 14,
            TrendType.BREAKING: 1,
            TrendType.SEASONAL: 30,
            TrendType.STABLE: 90,
            TrendType.DECLINING: 7
        }
        
        base_duration = base_durations.get(trend_type, 7)
        
        # Adjust based on growth rate
        if growth_rate > 1.0:
            return max(1, int(base_duration * 0.7))  # Faster growth = shorter duration
        elif growth_rate < 0.1:
            return int(base_duration * 1.5)  # Slower growth = longer duration
        
        return base_duration
    
    def _analyze_trend_demographics(self, signals: List[TrendSignal]) -> Dict[str, Any]:
        """
Analyze demographic patterns in trend signals."""
        # Simplified demographic analysis
        demographics = {
            'age_groups': {'18-24': 0.3, '25-34': 0.4, '35-44': 0.2, '45+': 0.1},
            'geographic_distribution': {'urban': 0.6, 'suburban': 0.3, 'rural': 0.1},
            'interests': []
        }
        
        # Extract interests from hashtags
        all_hashtags = []
        for signal in signals:
            all_hashtags.extend(signal.hashtags)
        
        hashtag_counter = Counter(all_hashtags)
        demographics['interests'] = [tag for tag, count in hashtag_counter.most_common(5)]
        
        return demographics
    
    async def _find_related_trends(self, keywords: List[str], category: TrendCategory) -> List[str]:
        """
Find trends related to the given keywords and category."""
        # Simplified related trend finding
        related = []
        
        # Use cached trend data to find related trends
        cached_trends = await self.cache_manager.get("all_trends")
        if cached_trends:
            for trend_data in cached_trends:
                trend_keywords = trend_data.get('keywords', [])
                trend_category = trend_data.get('category')
                
                # Check for keyword overlap or same category
                keyword_overlap = set(keywords) & set(trend_keywords)
                if keyword_overlap or trend_category == category.value:
                    related.append(trend_data.get('trend_id', 'unknown'))
        
        return related[:5]  # Return top 5 related trends
    
    def _identify_monetization_opportunities(
        self, 
        category: TrendCategory, 
        engagement: float, 
        scope: TrendScope
    ) -> List[Dict[str, Any]]:
        """Identify monetization opportunities for the trend."""
        opportunities = []
        
        if engagement > 10000:  # High engagement threshold
            if category == TrendCategory.MUSIC:
                opportunities.append({
                    'type': 'music_licensing',
                    'description': 'License trending music for commercial use',
                    'revenue_potential': 'high',
                    'implementation': 'contact_artists'
                })
            
            if scope in [TrendScope.GLOBAL, TrendScope.REGIONAL]:
                opportunities.append({
                    'type': 'brand_partnership',
                    'description': 'Partner with brands targeting trend audience',
                    'revenue_potential': 'medium',
                    'implementation': 'influencer_marketing'
                })
            
            opportunities.append({
                'type': 'content_creation',
                'description': 'Create content around trending topics',
                'revenue_potential': 'medium',
                'implementation': 'content_strategy'
            })
        
        return opportunities
    
    def _assess_trend_risks(self, trend_type: TrendType, category: TrendCategory, growth_rate: float) -> List[str]:
        """
Assess potential risks associated with the trend."""
        risks = []
        
        if trend_type == TrendType.VIRAL and growth_rate > 5.0:
            risks.append("extremely_rapid_growth_may_lead_to_quick_decline")
        
        if category == TrendCategory.NEWS:
            risks.append("news_trends_can_be_sensitive_or_controversial")
        
        if trend_type == TrendType.SEASONAL:
            risks.append("seasonal_trends_have_limited_time_windows")
        
        return risks
    
    def _estimate_market_size(self, trend: TrendPattern) -> float:
        """Estimate market size for a trend."""
        # Simplified market size estimation
        base_size = 10000
        
        # Scope multiplier
        scope_multipliers = {
            TrendScope.GLOBAL: 100,
            TrendScope.REGIONAL: 10,
            TrendScope.NICHE: 1,
            TrendScope.PLATFORM_SPECIFIC: 2,
            TrendScope.DEMOGRAPHIC_SPECIFIC: 5
        }
        
        scope_multiplier = scope_multipliers.get(trend.trend_scope, 1)
        
        # Growth rate multiplier
        growth_multiplier = 1 + trend.growth_rate
        
        return base_size * scope_multiplier * growth_multiplier * trend.confidence_score
    
    def _assess_competition_level(self, trend: TrendPattern) -> str:
        """
Assess competition level for a trend."""
        if trend.trend_type == TrendType.VIRAL:
            return "high"  # Viral trends attract many competitors
        elif trend.trend_type == TrendType.EMERGING:
            return "medium"  # Emerging trends have moderate competition
        elif trend.trend_scope == TrendScope.NICHE:
            return "low"  # Niche trends have less competition
        else:
            return "medium"
    
    async def _create_market_opportunity(
        self, 
        trend: TrendPattern, 
        market_size: float, 
        competition_level: str
    ) -> Optional[MarketOpportunity]:
        """Create a market opportunity from trend analysis."""
        # Calculate success probability
        success_factors = {
            "high": 0.3,
            "medium": 0.6,
            "low": 0.8
        }
        base_success = success_factors.get(competition_level, 0.5)
        
        # Adjust for trend confidence and growth
        adjusted_success = base_success * trend.confidence_score * min(1.0, 1 + trend.growth_rate)
        
        # Calculate ROI estimate
        roi_estimate = self._calculate_roi_estimate(market_size, competition_level, trend)
        
        # Determine time to market
        time_to_market = self._estimate_time_to_market(trend.category, competition_level)
        
        # Identify entry barriers
        entry_barriers = self._identify_entry_barriers(trend.category, competition_level)
        
        # Required resources
        required_resources = self._estimate_required_resources(market_size, trend.category)
        
        opportunity_id = f"opp_{trend.trend_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return MarketOpportunity(
            opportunity_id=opportunity_id,
            title=f"{trend.category.value.title()} Trend Opportunity",
            description=f"Market opportunity in {trend.category.value} based on {trend.trend_type.value} trend",
            market_size_estimate=market_size,
            competition_level=competition_level,
            entry_barriers=entry_barriers,
            success_probability=adjusted_success,
            roi_estimate=roi_estimate,
            time_to_market=time_to_market,
            required_resources=required_resources,
            key_metrics={
                'trend_confidence': trend.confidence_score,
                'growth_rate': trend.growth_rate,
                'viral_potential': 1.0 if trend.trend_type == TrendType.VIRAL else 0.5
            }
        )
    
    def _calculate_roi_estimate(self, market_size: float, competition_level: str, trend: TrendPattern) -> float:
        """Calculate ROI estimate for market opportunity."""
        # Base ROI calculation
        base_roi = market_size / 100000  # Simplified calculation
        
        # Competition penalty
        competition_penalties = {"high": 0.5, "medium": 0.7, "low": 1.0}
        competition_factor = competition_penalties.get(competition_level, 0.7)
        
        # Trend type bonus
        trend_bonuses = {
            TrendType.VIRAL: 2.0,
            TrendType.EMERGING: 1.5,
            TrendType.BREAKING: 1.2,
            TrendType.STABLE: 1.0,
            TrendType.SEASONAL: 0.8,
            TrendType.DECLINING: 0.3
        }
        trend_factor = trend_bonuses.get(trend.trend_type, 1.0)
        
        roi = base_roi * competition_factor * trend_factor * trend.confidence_score
        return min(10.0, roi)  # Cap at 1000% ROI
    
    def _estimate_time_to_market(self, category: TrendCategory, competition_level: str) -> int:
        """Estimate time to market in days."""
        base_times = {
            TrendCategory.MUSIC: 30,
            TrendCategory.TECHNOLOGY: 90,
            TrendCategory.ENTERTAINMENT: 45,
            TrendCategory.FASHION: 60,
            TrendCategory.LIFESTYLE: 21,
            TrendCategory.NEWS: 7,
            TrendCategory.SPORTS: 14,
            TrendCategory.GAMING: 75,
            TrendCategory.BUSINESS: 120,
            TrendCategory.EDUCATION: 90
        }
        
        base_time = base_times.get(category, 60)
        
        # Competition affects speed needed
        competition_multipliers = {"high": 0.7, "medium": 1.0, "low": 1.3}
        multiplier = competition_multipliers.get(competition_level, 1.0)
        
        return int(base_time * multiplier)
    
    def _identify_entry_barriers(self, category: TrendCategory, competition_level: str) -> List[str]:
        """Identify entry barriers for market opportunity."""
        barriers = []
        
        if competition_level == "high":
            barriers.append("high_competition")
            barriers.append("established_players")
        
        category_barriers = {
            TrendCategory.MUSIC: ["licensing_requirements", "artist_relationships"],
            TrendCategory.TECHNOLOGY: ["technical_expertise", "development_resources"],
            TrendCategory.ENTERTAINMENT: ["content_creation_skills", "distribution_networks"],
            TrendCategory.FASHION: ["design_capabilities", "manufacturing_partnerships"],
            TrendCategory.NEWS: ["credibility", "real_time_capabilities"]
        }
        
        barriers.extend(category_barriers.get(category, ["market_knowledge"]))
        
        return barriers
    
    def _estimate_required_resources(self, market_size: float, category: TrendCategory) -> Dict[str, Any]:
        """Estimate required resources for market opportunity."""
        # Base resource requirements
        base_budget = min(100000, market_size * 0.1)  # 10% of market size, capped
        
        resources = {
            'budget': base_budget,
            'team_size': max(1, int(base_budget / 50000)),  # 1 person per 50k budget
            'timeline_months': max(1, int(base_budget / 25000)),  # 1 month per 25k budget
            'key_skills': []
        }
        
        # Category-specific skills
        category_skills = {
            TrendCategory.MUSIC: ["music_production", "artist_relations", "licensing"],
            TrendCategory.TECHNOLOGY: ["software_development", "ai_ml", "data_analysis"],
            TrendCategory.ENTERTAINMENT: ["content_creation", "video_editing", "marketing"],
            TrendCategory.FASHION: ["design", "manufacturing", "retail"],
            TrendCategory.NEWS: ["journalism", "fact_checking", "real_time_publishing"]
        }
        
        resources['key_skills'] = category_skills.get(category, ["marketing", "business_development"])
        
        return resources
    
    def _create_trend_feature_matrix(self, trends: List[TrendPattern]) -> np.ndarray:
        """Create feature matrix for trend correlation analysis."""
        features = []
        
        for trend in trends:
            feature_vector = [
                trend.confidence_score,
                trend.growth_rate,
                len(trend.keywords),
                trend.duration_estimate,
                1.0 if trend.trend_type == TrendType.VIRAL else 0.0,
                1.0 if trend.trend_scope == TrendScope.GLOBAL else 0.0,
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    async def _analyze_external_correlations(
        self, 
        trends: List[TrendPattern], 
        external_data: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
Analyze correlations with external data sources."""
        correlations = {}
        
        # Example: Stock market correlation
        if 'stock_data' in external_data:
            # Simplified correlation analysis
            for trend in trends:
                if trend.category == TrendCategory.TECHNOLOGY:
                    correlations[trend.trend_id] = ['tech_stock_performance']
                elif trend.category == TrendCategory.BUSINESS:
                    correlations[trend.trend_id] = ['market_indices']
        
        # Weather correlation for certain categories
        if 'weather_data' in external_data:
            for trend in trends:
                if trend.category in [TrendCategory.LIFESTYLE, TrendCategory.SPORTS]:
                    correlations.setdefault(trend.trend_id, []).append('weather_patterns')
        
        return correlations
    
    def _get_platform_reach_factor(self, platform: str) -> float:
        """
Get platform reach factor for viral prediction."""
        reach_factors = {
            'youtube': 2.0,
            'tiktok': 1.8,
            'instagram': 1.5,
            'twitter': 1.3,
            'facebook': 1.2,
            'linkedin': 0.8,
            'reddit': 1.4,
            'twitch': 1.6
        }
        return reach_factors.get(platform.lower(), 1.0)

# Factory function
def create_trend_detection_engine() -> TrendDetectionEngine:
    """
Create and return a trend detection engine instance."""
    return TrendDetectionEngine()
