"""Trend Analysis and Prediction Parsers Module
============================================

Ultra-advanced parsers for trend analysis, viral content prediction,
and market intelligence across social media platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de

Development Team Specialties:
- Lead AI Developer & Architect: Fahed Mlaiel
- Backend Senior Engineer: Advanced Python/FastAPI systems
- ML Engineer: Content analysis and fingerprinting
- Audio Processing Specialist: Multi-format audio analysis  
- DevOps Engineer: Infrastructure and deployment
- Database Administrator: Performance optimization
- Security Expert: Content protection and compliance
- Microservices Architect: Scalable system design
"""import asyncio
import json
import logging
import re
import math
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
import scipy.stats as stats

from .exceptions import TrendAnalysisError, PredictionError, AnalysisError
from .parser_config import ParserConfig


class TrendCategory(Enum):
    """Trend category types"""    HASHTAG = "hashtag"
    MUSIC_TRACK = "music_track"
    CHALLENGE = "challenge"
    MEME = "meme"
    PRODUCT = "product"
    TOPIC = "topic"
    CREATOR = "creator"
    BRAND = "brand"
    EVENT = "event"
    TECHNOLOGY = "technology"


class TrendStage(Enum):
    """Trend lifecycle stages"""    EMERGING = "emerging"      # Just starting to gain traction
    GROWING = "growing"        # Rapidly gaining popularity
    VIRAL = "viral"           # At peak virality
    MAINSTREAM = "mainstream"  # Widely adopted
    DECLINING = "declining"    # Losing popularity
    DORMANT = "dormant"       # No longer trending


class ViralityLevel(Enum):
    """Virality potential levels"""    EXTREMELY_HIGH = "extremely_high"  # 90%+ chance to go viral
    HIGH = "high"                      # 70-90% chance
    MODERATE = "moderate"              # 40-70% chance
    LOW = "low"                        # 10-40% chance
    VERY_LOW = "very_low"             # <10% chance


@dataclass
class TrendData:
    """Core trend data structure"""    trend_id: str
    name: str
    category: TrendCategory
    stage: TrendStage
    virality_level: ViralityLevel
    platforms: List[str]
    first_detected: datetime
    peak_timestamp: Optional[datetime] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    geographical_data: Dict[str, Any] = field(default_factory=dict)
    demographics: Dict[str, Any] = field(default_factory=dict)
    related_trends: List[str] = field(default_factory=list)
    influencers: List[Dict[str, Any]] = field(default_factory=list)
    momentum_score: float = 0.0
    engagement_velocity: float = 0.0
    predicted_lifespan_days: int = 0


@dataclass
class ViralityPrediction:
    """Virality prediction results"""    content_id: str
    virality_score: float
    confidence_level: float
    predicted_peak_time: Optional[datetime] = None
    estimated_reach: int = 0
    optimal_posting_time: Optional[datetime] = None
    recommended_platforms: List[str] = field(default_factory=list)
    success_factors: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    enhancement_suggestions: List[str] = field(default_factory=list)


@dataclass
class MarketIntelligence:
    """Comprehensive market intelligence"""    trending_topics: List[TrendData] = field(default_factory=list)
    emerging_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    competitor_analysis: Dict[str, Any] = field(default_factory=dict)
    content_gaps: List[Dict[str, Any]] = field(default_factory=list)
    seasonal_patterns: Dict[str, Any] = field(default_factory=dict)
    platform_insights: Dict[str, Any] = field(default_factory=dict)
    audience_shifts: Dict[str, Any] = field(default_factory=dict)
    revenue_opportunities: List[Dict[str, Any]] = field(default_factory=list)


class TrendDetectionEngine:
    """Advanced AI-powered trend detection engine"""    
    def __init__(self, config: ParserConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        self.trend_predictor = None
        self.historical_data = []
    
    async def detect_emerging_trends(
        self,
        platform_data: Dict[str, List[Dict[str, Any]]],
        time_window_hours: int = 24,
        min_engagement_threshold: int = 1000
    ) -> List[TrendData]:
        """Detect emerging trends across platforms"""        try:
            trends = []
            
            for platform, content_data in platform_data.items():
                platform_trends = await self._analyze_platform_trends(
                    platform, content_data, time_window_hours, min_engagement_threshold
                )
                trends.extend(platform_trends)
            
            # Cross-platform trend correlation
            correlated_trends = await self._correlate_cross_platform_trends(trends)
            
            # Filter and rank trends
            filtered_trends = await self._filter_and_rank_trends(correlated_trends)
            
            return filtered_trends
            
        except Exception as e:
            self.logger.error(f"Trend detection failed: {e}")
            raise TrendAnalysisError(f"Failed to detect emerging trends: {e}")
    
    async def _analyze_platform_trends(
        self,
        platform: str,
        content_data: List[Dict[str, Any]],
        time_window_hours: int,
        min_engagement_threshold: int
    ) -> List[TrendData]:
        """Analyze trends for specific platform"""        trends = []
        
        try:
            # Group content by time intervals
            time_buckets = self._group_content_by_time(content_data, time_window_hours)
            
            # Analyze hashtags, keywords, and content patterns
            hashtag_trends = await self._analyze_hashtag_trends(time_buckets, platform)
            keyword_trends = await self._analyze_keyword_trends(time_buckets, platform)
            audio_trends = await self._analyze_audio_trends(time_buckets, platform)
            creator_trends = await self._analyze_creator_trends(time_buckets, platform)
            
            trends.extend(hashtag_trends)
            trends.extend(keyword_trends)
            trends.extend(audio_trends)
            trends.extend(creator_trends)
            
            # Filter by engagement threshold
            trends = [t for t in trends if t.metrics.get('total_engagement', 0) >= min_engagement_threshold]
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Platform trend analysis failed for {platform}: {e}")
            return []
    
    def _group_content_by_time(self, content_data: List[Dict[str, Any]], window_hours: int) -> Dict[str, List[Dict[str, Any]]]:
        """Group content into time buckets"""        time_buckets = {}
        
        for content in content_data:
            # Parse timestamp
            timestamp_str = content.get('timestamp', '')
            try:
                if isinstance(timestamp_str, str):
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    timestamp = timestamp_str
                
                # Create time bucket key
                bucket_key = timestamp.replace(minute=0, second=0, microsecond=0)
                bucket_key = bucket_key.replace(hour=(bucket_key.hour // window_hours) * window_hours)
                bucket_str = bucket_key.isoformat()
                
                if bucket_str not in time_buckets:
                    time_buckets[bucket_str] = []
                
                time_buckets[bucket_str].append(content)
                
            except Exception as e:
                self.logger.warning(f"Failed to parse timestamp {timestamp_str}: {e}")
                continue
        
        return time_buckets
    
    async def _analyze_hashtag_trends(self, time_buckets: Dict[str, List[Dict[str, Any]]], platform: str) -> List[TrendData]:
        """Analyze hashtag trends"""        hashtag_data = {}
        
        # Extract hashtags from all content
        for bucket_time, content_list in time_buckets.items():
            for content in content_list:
                text = content.get('caption', '') + ' ' + content.get('description', '')
                hashtags = re.findall(r'#(\w+)', text.lower())
                
                for hashtag in hashtags:
                    if hashtag not in hashtag_data:
                        hashtag_data[hashtag] = {
                            'timestamps': [],
                            'engagement': [],
                            'content_count': 0,
                            'first_seen': None,
                            'creators': set()
                        }
                    
                    hashtag_data[hashtag]['timestamps'].append(bucket_time)
                    hashtag_data[hashtag]['engagement'].append(
                        content.get('likes', 0) + content.get('shares', 0) + content.get('comments', 0)
                    )
                    hashtag_data[hashtag]['content_count'] += 1
                    hashtag_data[hashtag]['creators'].add(content.get('creator_id', ''))
                    
                    if not hashtag_data[hashtag]['first_seen']:
                        hashtag_data[hashtag]['first_seen'] = bucket_time
        
        # Analyze each hashtag for trending potential
        trends = []
        for hashtag, data in hashtag_data.items():
            if len(data['timestamps']) >= 3:  # Minimum data points
                trend = await self._create_hashtag_trend(hashtag, data, platform)
                if trend:
                    trends.append(trend)
        
        return trends
    
    async def _create_hashtag_trend(self, hashtag: str, data: Dict[str, Any], platform: str) -> Optional[TrendData]:
        """Create trend data for hashtag"""        try:
            # Calculate momentum
            momentum = self._calculate_momentum(data['engagement'], data['timestamps'])
            
            # Determine trend stage
            stage = self._determine_trend_stage(momentum, data['content_count'], len(data['creators']))
            
            # Calculate virality level
            virality = self._assess_virality_level(momentum, data['engagement'], len(data['creators']))
            
            # Only create trend if it shows significant momentum
            if momentum > 0.1:  # Threshold for trending
                trend_id = f"hashtag_{hashtag}_{platform}_{int(datetime.now().timestamp())}"
                
                return TrendData(
                    trend_id=trend_id,
                    name=f"#{hashtag}",
                    category=TrendCategory.HASHTAG,
                    stage=stage,
                    virality_level=virality,
                    platforms=[platform],
                    first_detected=datetime.fromisoformat(data['first_seen']),
                    metrics={
                        'total_engagement': sum(data['engagement']),
                        'content_count': data['content_count'],
                        'unique_creators': len(data['creators']),
                        'engagement_growth_rate': momentum,
                        'average_engagement': statistics.mean(data['engagement']) if data['engagement'] else 0
                    },
                    momentum_score=momentum,
                    engagement_velocity=self._calculate_velocity(data['engagement'], data['timestamps'])
                )
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Failed to create hashtag trend for {hashtag}: {e}")
            return None
    
    def _calculate_momentum(self, engagement_values: List[int], timestamps: List[str]) -> float:
        """Calculate momentum score for trend"""        if len(engagement_values) < 2:
            return 0.0
        
        try:
            # Sort by timestamp
            time_engagement_pairs = [(datetime.fromisoformat(t), e) for t, e in zip(timestamps, engagement_values)]
            time_engagement_pairs.sort(key=lambda x: x[0])
            
            # Calculate linear regression slope
            x_values = [(pair[0] - time_engagement_pairs[0][0]).total_seconds() / 3600 for pair in time_engagement_pairs]  # Hours
            y_values = [pair[1] for pair in time_engagement_pairs]
            
            if len(x_values) > 1:
                slope, _, r_value, _, _ = stats.linregress(x_values, y_values)
                # Normalize slope by time range and correlation
                momentum = (slope * abs(r_value)) / max(max(x_values) - min(x_values), 1)
                return max(0, min(momentum / 1000, 1.0))  # Normalize to 0-1
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_velocity(self, engagement_values: List[int], timestamps: List[str]) -> float:
        """Calculate engagement velocity"""        if len(engagement_values) < 2:
            return 0.0
        
        try:
            # Calculate average change per hour
            changes = []
            for i in range(1, len(engagement_values)):
                current_time = datetime.fromisoformat(timestamps[i])
                prev_time = datetime.fromisoformat(timestamps[i-1])
                time_diff_hours = (current_time - prev_time).total_seconds() / 3600
                
                if time_diff_hours > 0:
                    change_rate = (engagement_values[i] - engagement_values[i-1]) / time_diff_hours
                    changes.append(change_rate)
            
            return statistics.mean(changes) if changes else 0.0
            
        except Exception:
            return 0.0
    
    def _determine_trend_stage(self, momentum: float, content_count: int, creator_count: int) -> TrendStage:
        """Determine trend lifecycle stage"""        if momentum > 0.8 and content_count > 1000:
            return TrendStage.VIRAL
        elif momentum > 0.6 and content_count > 500:
            return TrendStage.GROWING
        elif momentum > 0.4 and content_count > 100:
            return TrendStage.EMERGING
        elif momentum > 0.2:
            return TrendStage.MAINSTREAM
        elif momentum > 0.0:
            return TrendStage.DECLINING
        else:
            return TrendStage.DORMANT
    
    def _assess_virality_level(self, momentum: float, engagement_values: List[int], creator_count: int) -> ViralityLevel:
        """Assess virality potential level"""        total_engagement = sum(engagement_values)
        avg_engagement = total_engagement / max(creator_count, 1)
        
        # Multi-factor virality assessment
        virality_score = 0.0
        
        # Momentum factor (40%)
        virality_score += momentum * 0.4
        
        # Creator diversity factor (30%)
        creator_diversity = min(creator_count / 100, 1.0)  # Normalize to 0-1
        virality_score += creator_diversity * 0.3
        
        # Engagement factor (30%)
        engagement_factor = min(avg_engagement / 10000, 1.0)  # Normalize to 0-1
        virality_score += engagement_factor * 0.3
        
        # Classify virality level
        if virality_score >= 0.9:
            return ViralityLevel.EXTREMELY_HIGH
        elif virality_score >= 0.7:
            return ViralityLevel.HIGH
        elif virality_score >= 0.4:
            return ViralityLevel.MODERATE
        elif virality_score >= 0.1:
            return ViralityLevel.LOW
        else:
            return ViralityLevel.VERY_LOW
    
    async def _analyze_keyword_trends(self, time_buckets: Dict[str, List[Dict[str, Any]]], platform: str) -> List[TrendData]:
        """Analyze keyword and topic trends"""        # Similar to hashtag analysis but for general keywords/topics
        # This would use NLP to extract meaningful phrases and topics
        return []  # Placeholder
    
    async def _analyze_audio_trends(self, time_buckets: Dict[str, List[Dict[str, Any]]], platform: str) -> List[TrendData]:
        """Analyze trending audio/music"""        # Analyze trending audio clips, songs, or sounds
        return []  # Placeholder
    
    async def _analyze_creator_trends(self, time_buckets: Dict[str, List[Dict[str, Any]]], platform: str) -> List[TrendData]:
        """Analyze trending creators"""        # Analyze creators who are rapidly gaining popularity
        return []  # Placeholder
    
    async def _correlate_cross_platform_trends(self, trends: List[TrendData]) -> List[TrendData]:
        """Correlate trends across multiple platforms"""        # Group similar trends from different platforms
        correlated_trends = []
        processed_names = set()
        
        for trend in trends:
            if trend.name in processed_names:
                continue
            
            # Find similar trends
            similar_trends = [t for t in trends if self._are_trends_similar(trend, t)]
            
            if len(similar_trends) > 1:
                # Merge trends from multiple platforms
                merged_trend = self._merge_trends(similar_trends)
                correlated_trends.append(merged_trend)
                processed_names.add(trend.name)
            else:
                correlated_trends.append(trend)
                processed_names.add(trend.name)
        
        return correlated_trends
    
    def _are_trends_similar(self, trend1: TrendData, trend2: TrendData) -> bool:
        """Check if two trends are similar"""        # Simple similarity check - could be enhanced with NLP
        return (trend1.name.lower() == trend2.name.lower() and 
                trend1.category == trend2.category)
    
    def _merge_trends(self, trends: List[TrendData]) -> TrendData:
        """Merge multiple similar trends"""        if not trends:
            return None
        
        base_trend = trends[0]
        
        # Merge platforms
        all_platforms = []
        for trend in trends:
            all_platforms.extend(trend.platforms)
        base_trend.platforms = list(set(all_platforms))
        
        # Aggregate metrics
        total_engagement = sum(t.metrics.get('total_engagement', 0) for t in trends)
        total_content = sum(t.metrics.get('content_count', 0) for t in trends)
        total_creators = sum(t.metrics.get('unique_creators', 0) for t in trends)
        
        base_trend.metrics.update({
            'total_engagement': total_engagement,
            'content_count': total_content,
            'unique_creators': total_creators
        })
        
        # Update momentum and virality based on cross-platform presence
        platform_bonus = min(len(base_trend.platforms) * 0.1, 0.5)  # Bonus for multi-platform
        base_trend.momentum_score = min(base_trend.momentum_score + platform_bonus, 1.0)
        
        return base_trend
    
    async def _filter_and_rank_trends(self, trends: List[TrendData]) -> List[TrendData]:
        """Filter and rank trends by importance"""        # Filter out low-quality trends
        filtered_trends = [
            t for t in trends 
            if (t.momentum_score > 0.1 and 
                t.metrics.get('content_count', 0) > 10 and
                t.metrics.get('unique_creators', 0) > 3)
        ]
        
        # Rank by composite score
        for trend in filtered_trends:
            trend.composite_score = self._calculate_composite_score(trend)
        
        # Sort by composite score
        filtered_trends.sort(key=lambda t: getattr(t, 'composite_score', 0), reverse=True)
        
        return filtered_trends[:50]  # Return top 50 trends
    
    def _calculate_composite_score(self, trend: TrendData) -> float:
        """Calculate composite ranking score"""        score = 0.0
        
        # Momentum score (40%)
        score += trend.momentum_score * 0.4
        
        # Multi-platform bonus (20%)
        platform_score = min(len(trend.platforms) / 5, 1.0)  # Max 5 platforms
        score += platform_score * 0.2
        
        # Engagement score (25%)
        engagement_score = min(trend.metrics.get('total_engagement', 0) / 100000, 1.0)
        score += engagement_score * 0.25
        
        # Creator diversity (15%)
        creator_score = min(trend.metrics.get('unique_creators', 0) / 100, 1.0)
        score += creator_score * 0.15
        
        return score


class ViralityPredictor:
    """AI-powered virality prediction system"""    
    def __init__(self, config: ParserConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
    
    async def predict_virality(self, content_data: Dict[str, Any]) -> ViralityPrediction:
        """Predict virality potential for content"""        try:
            # Extract features from content
            features = await self._extract_virality_features(content_data)
            
            # Generate prediction
            virality_score = await self._calculate_virality_score(features)
            confidence_level = await self._calculate_confidence_level(features)
            
            # Generate recommendations
            prediction = ViralityPrediction(
                content_id=content_data.get('id', ''),
                virality_score=virality_score,
                confidence_level=confidence_level
            )
            
            # Add detailed analysis
            prediction.success_factors = await self._identify_success_factors(features, content_data)
            prediction.risk_factors = await self._identify_risk_factors(features, content_data)
            prediction.enhancement_suggestions = await self._generate_enhancement_suggestions(features, content_data)
            prediction.recommended_platforms = await self._recommend_platforms(features, content_data)
            prediction.optimal_posting_time = await self._predict_optimal_timing(content_data)
            prediction.estimated_reach = await self._estimate_reach(virality_score, content_data)
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Virality prediction failed: {e}")
            raise PredictionError(f"Failed to predict virality: {e}")
    
    async def _extract_virality_features(self, content_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features that influence virality"""        features = {}
        
        # Content type features
        content_type = content_data.get('type', 'unknown')
        features['is_video'] = 1.0 if content_type == 'video' else 0.0
        features['is_image'] = 1.0 if content_type == 'image' else 0.0
        features['is_audio'] = 1.0 if content_type == 'audio' else 0.0
        
        # Text analysis features
        text_content = content_data.get('caption', '') + ' ' + content_data.get('description', '')
        features['text_length'] = len(text_content)
        features['hashtag_count'] = len(re.findall(r'#\w+', text_content))
        features['mention_count'] = len(re.findall(r'@\w+', text_content))
        features['emoji_count'] = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', text_content))
        
        # Creator features
        creator_data = content_data.get('creator', {})
        features['creator_followers'] = math.log10(max(creator_data.get('followers', 1), 1))
        features['creator_verified'] = 1.0 if creator_data.get('verified', False) else 0.0
        features['creator_engagement_rate'] = creator_data.get('engagement_rate', 0.0)
        
        # Timing features
        timestamp = content_data.get('timestamp')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                features['hour_of_day'] = dt.hour
                features['day_of_week'] = dt.weekday()
                features['is_weekend'] = 1.0 if dt.weekday() >= 5 else 0.0
            except:
                features['hour_of_day'] = 12  # Default to noon
                features['day_of_week'] = 2   # Default to Wednesday
                features['is_weekend'] = 0.0
        
        # Content quality indicators
        features['has_call_to_action'] = 1.0 if any(phrase in text_content.lower() 
                                                   for phrase in ['like', 'share', 'comment', 'follow']) else 0.0
        features['has_trending_hashtags'] = 1.0 if any(tag in text_content.lower() 
                                                      for tag in ['#viral', '#trending', '#fyp']) else 0.0
        
        # Media quality features (if available)
        if 'media_analysis' in content_data:
            media = content_data['media_analysis']
            features['media_quality_score'] = media.get('quality_score', 0.5)
            features['has_music'] = 1.0 if media.get('has_music', False) else 0.0
            features['has_effects'] = 1.0 if media.get('has_effects', False) else 0.0
        
        return features
    
    async def _calculate_virality_score(self, features: Dict[str, float]) -> float:
        """Calculate virality score using heuristic model"""        # In production, this would use a trained ML model
        # For now, using weighted heuristics
        
        score = 0.0
        
        # Creator influence (30%)
        creator_score = min(features.get('creator_followers', 0) / 6, 1.0)  # log10(1M) = 6
        creator_score += features.get('creator_verified', 0) * 0.2
        creator_score += min(features.get('creator_engagement_rate', 0) / 10, 1.0)
        score += (creator_score / 3) * 0.3
        
        # Content engagement potential (25%)
        engagement_score = 0.0
        engagement_score += min(features.get('hashtag_count', 0) / 10, 1.0) * 0.3
        engagement_score += features.get('has_call_to_action', 0) * 0.3
        engagement_score += min(features.get('emoji_count', 0) / 5, 1.0) * 0.2
        engagement_score += features.get('has_trending_hashtags', 0) * 0.2
        score += engagement_score * 0.25
        
        # Media quality (20%)
        media_score = features.get('media_quality_score', 0.5)
        media_score += features.get('has_music', 0) * 0.2
        media_score += features.get('has_effects', 0) * 0.2
        score += (media_score / 1.4) * 0.2
        
        # Timing optimization (15%)
        timing_score = 0.0
        hour = features.get('hour_of_day', 12)
        # Peak hours: 6-9 AM, 12-2 PM, 6-10 PM
        if 6 <= hour <= 9 or 12 <= hour <= 14 or 18 <= hour <= 22:
            timing_score += 0.8
        elif 10 <= hour <= 11 or 15 <= hour <= 17:
            timing_score += 0.6
        else:
            timing_score += 0.3
        
        timing_score += features.get('is_weekend', 0) * 0.2
        score += (timing_score / 1.2) * 0.15
        
        # Content type bonus (10%)
        type_score = max(features.get('is_video', 0) * 0.8, features.get('is_image', 0) * 0.6)
        score += type_score * 0.10
        
        return min(max(score, 0.0), 1.0)
    
    async def _calculate_confidence_level(self, features: Dict[str, float]) -> float:
        """Calculate confidence in prediction"""        # Confidence based on data completeness and creator track record
        confidence = 0.5  # Base confidence
        
        # Data completeness bonus
        feature_completeness = sum(1 for v in features.values() if v > 0) / len(features)
        confidence += feature_completeness * 0.3
        
        # Creator data reliability
        if features.get('creator_followers', 0) > 3:  # log10(1000) = 3
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    async def _identify_success_factors(self, features: Dict[str, float], content_data: Dict[str, Any]) -> List[str]:
        """Identify factors contributing to potential success"""        factors = []
        
        if features.get('creator_verified', 0) > 0:
            factors.append("Verified creator with established credibility")
        
        if features.get('creator_followers', 0) > 4:  # log10(10K) = 4
            factors.append("Large follower base for initial reach")
        
        if features.get('creator_engagement_rate', 0) > 5:
            factors.append("High creator engagement rate")
        
        if features.get('hashtag_count', 0) >= 5:
            factors.append("Optimal hashtag usage for discoverability")
        
        if features.get('has_trending_hashtags', 0) > 0:
            factors.append("Using trending hashtags")
        
        if features.get('has_call_to_action', 0) > 0:
            factors.append("Clear call-to-action for engagement")
        
        if features.get('media_quality_score', 0) > 0.7:
            factors.append("High-quality media content")
        
        # Timing factors
        hour = features.get('hour_of_day', 12)
        if 6 <= hour <= 9 or 12 <= hour <= 14 or 18 <= hour <= 22:
            factors.append("Posted during peak engagement hours")
        
        return factors
    
    async def _identify_risk_factors(self, features: Dict[str, float], content_data: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors"""        risks = []
        
        if features.get('creator_followers', 0) < 2:  # log10(100) = 2
            risks.append("Small follower base may limit initial reach")
        
        if features.get('creator_engagement_rate', 0) < 2:
            risks.append("Low creator engagement rate")
        
        if features.get('hashtag_count', 0) < 3:
            risks.append("Insufficient hashtags for discoverability")
        
        if features.get('text_length', 0) > 1000:
            risks.append("Caption may be too long for optimal engagement")
        
        if features.get('media_quality_score', 0) < 0.4:
            risks.append("Low media quality may reduce engagement")
        
        # Timing risks
        hour = features.get('hour_of_day', 12)
        if 0 <= hour <= 5 or 23 <= hour <= 24:
            risks.append("Posted during low-engagement hours")
        
        return risks
    
    async def _generate_enhancement_suggestions(self, features: Dict[str, float], content_data: Dict[str, Any]) -> List[str]:
        """Generate suggestions to improve virality potential"""        suggestions = []
        
        if features.get('hashtag_count', 0) < 5:
            suggestions.append("Add more relevant hashtags (aim for 5-10)")
        
        if features.get('has_call_to_action', 0) == 0:
            suggestions.append("Include a clear call-to-action (like, share, comment)")
        
        if features.get('emoji_count', 0) < 2:
            suggestions.append("Add relevant emojis to increase engagement")
        
        if features.get('has_trending_hashtags', 0) == 0:
            suggestions.append("Research and include trending hashtags")
        
        if features.get('media_quality_score', 0) < 0.6:
            suggestions.append("Improve media quality (lighting, resolution, editing)")
        
        # Timing suggestions
        hour = features.get('hour_of_day', 12)
        if not (6 <= hour <= 9 or 12 <= hour <= 14 or 18 <= hour <= 22):
            suggestions.append("Consider posting during peak hours (6-9 AM, 12-2 PM, 6-10 PM)")
        
        return suggestions
    
    async def _recommend_platforms(self, features: Dict[str, float], content_data: Dict[str, Any]) -> List[str]:
        """Recommend optimal platforms for content"""        platforms = []
        
        content_type = content_data.get('type', 'unknown')
        
        if content_type == 'video':
            if features.get('has_music', 0) > 0:
                platforms.extend(['tiktok', 'instagram_reels'])
            platforms.extend(['youtube_shorts', 'youtube'])
        
        elif content_type == 'image':
            platforms.extend(['instagram', 'pinterest'])
            if features.get('hashtag_count', 0) > 5:
                platforms.append('twitter')
        
        elif content_type == 'audio':
            platforms.extend(['spotify', 'soundcloud', 'youtube_music'])
        
        # Universal platforms
        platforms.extend(['facebook', 'linkedin'])
        
        return list(set(platforms))  # Remove duplicates
    
    async def _predict_optimal_timing(self, content_data: Dict[str, Any]) -> Optional[datetime]:
        """Predict optimal posting time"""        # This would use historical performance data
        # For now, return next peak hour
        now = datetime.now(timezone.utc)
        peak_hours = [7, 13, 19]  # 7 AM, 1 PM, 7 PM UTC
        
        next_peak = None
        for hour in peak_hours:
            next_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if next_time < now:
                next_time += timedelta(days=1)
            
            if next_peak is None or next_time < next_peak:
                next_peak = next_time
        
        return next_peak
    
    async def _estimate_reach(self, virality_score: float, content_data: Dict[str, Any]) -> int:
        """Estimate potential reach based on virality score"""        creator_data = content_data.get('creator', {})
        base_reach = creator_data.get('followers', 1000)
        
        # Viral multiplier based on score
        if virality_score > 0.8:
            multiplier = 10  # Potential to reach 10x followers
        elif virality_score > 0.6:
            multiplier = 5
        elif virality_score > 0.4:
            multiplier = 2
        elif virality_score > 0.2:
            multiplier = 1.5
        else:
            multiplier = 1
        
        estimated_reach = int(base_reach * multiplier)
        return estimated_reach


__all__ = [
    'TrendDetectionEngine',
    'ViralityPredictor',
    'TrendData',
    'ViralityPrediction',
    'MarketIntelligence',
    'TrendCategory',
    'TrendStage',
    'ViralityLevel'
]
