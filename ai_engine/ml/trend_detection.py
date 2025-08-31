"""
Trend Detection Module

Advanced trend detection and analysis system for identifying emerging patterns
and viral potential in content for the IA Influencer platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  LEGAL WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
Contact: mlaiel@live.de
"""

import asyncio
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple, Set
import logging
from pathlib import Path
import json
import re
from collections import defaultdict, Counter
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.cluster import DBSCAN, KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA, LatentDirichletAllocation
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import silhouette_score
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.sparse import csr_matrix
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.util import ngrams

# Optional financial data and social media libraries
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    yf = None

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    tweepy = None

from textblob import TextBlob
from transformers import pipeline, AutoTokenizer, AutoModel
import requests
from bs4 import BeautifulSoup
import schedule
import time
from threading import Thread
import pickle

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass


class TrendStatus(Enum):
    """Trend status indicators"""
    EMERGING = "emerging"
    GROWING = "growing"
    PEAKED = "peaked"
    DECLINING = "declining"
    STABLE = "stable"
    VIRAL = "viral"
    DEAD = "dead"


class TrendType(Enum):
    """Types of trends"""
    HASHTAG = "hashtag"
    KEYWORD = "keyword"
    TOPIC = "topic"
    MEME = "meme"
    MUSIC = "music"
    CHALLENGE = "challenge"
    NEWS = "news"
    PRODUCT = "product"
    PERSON = "person"
    EVENT = "event"


class TrendScope(Enum):
    """Geographical or demographic scope of trends"""
    GLOBAL = "global"
    REGIONAL = "regional"
    LOCAL = "local"
    NICHE = "niche"
    MAINSTREAM = "mainstream"


class TrendSource(Enum):
    """Sources of trend data"""
    SOCIAL_MEDIA = "social_media"
    NEWS = "news"
    SEARCH_ENGINE = "search_engine"
    PLATFORM_ANALYTICS = "platform_analytics"
    USER_GENERATED = "user_generated"
    EXTERNAL_API = "external_api"


@dataclass
class TrendMetrics:
    """Metrics for trend analysis"""
    volume: float  # Total volume/frequency
    velocity: float  # Rate of change
    acceleration: float  # Rate of velocity change
    reach: float  # Unique users/sources
    engagement: float  # Interaction rate
    sentiment: float  # Overall sentiment
    virality_score: float  # Viral potential
    persistence: float  # How long it lasts
    influence_score: float  # Impact on other trends
    authenticity: float  # Organic vs artificial
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'volume': self.volume,
            'velocity': self.velocity,
            'acceleration': self.acceleration,
            'reach': self.reach,
            'engagement': self.engagement,
            'sentiment': self.sentiment,
            'virality_score': self.virality_score,
            'persistence': self.persistence,
            'influence_score': self.influence_score,
            'authenticity': self.authenticity
        }


@dataclass
class TrendDataPoint:
    """Single trend data point"""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Trend:
    """Trend object with all associated data"""
    trend_id: str
    content: str  # Main trend content (hashtag, keyword, etc.)
    trend_type: TrendType
    status: TrendStatus
    scope: TrendScope
    sources: List[TrendSource]
    metrics: TrendMetrics
    data_points: List[TrendDataPoint]
    related_trends: List[str] = field(default_factory=list)
    peak_timestamp: Optional[datetime] = None
    start_timestamp: datetime = field(default_factory=datetime.now)
    end_timestamp: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'trend_id': self.trend_id,
            'content': self.content,
            'trend_type': self.trend_type.value,
            'status': self.status.value,
            'scope': self.scope.value,
            'sources': [source.value for source in self.sources],
            'metrics': self.metrics.to_dict(),
            'data_points': [
                {
                    'timestamp': dp.timestamp.isoformat(),
                    'value': dp.value,
                    'metadata': dp.metadata
                }
                for dp in self.data_points
            ],
            'related_trends': self.related_trends,
            'peak_timestamp': self.peak_timestamp.isoformat() if self.peak_timestamp else None,
            'start_timestamp': self.start_timestamp.isoformat(),
            'end_timestamp': self.end_timestamp.isoformat() if self.end_timestamp else None,
            'tags': self.tags,
            'confidence': self.confidence
        }


@dataclass
class TrendPrediction:
    """Prediction about future trend behavior"""
    trend_id: str
    predicted_status: TrendStatus
    predicted_peak: Optional[datetime]
    predicted_end: Optional[datetime]
    confidence: float
    supporting_factors: List[str]
    risk_factors: List[str]
    prediction_horizon: timedelta
    model_used: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'trend_id': self.trend_id,
            'predicted_status': self.predicted_status.value,
            'predicted_peak': self.predicted_peak.isoformat() if self.predicted_peak else None,
            'predicted_end': self.predicted_end.isoformat() if self.predicted_end else None,
            'confidence': self.confidence,
            'supporting_factors': self.supporting_factors,
            'risk_factors': self.risk_factors,
            'prediction_horizon': str(self.prediction_horizon),
            'model_used': self.model_used
        }


class TrendDetector(ABC):
    """Abstract base class for trend detectors"""
    
    def __init__(self, detector_name: str):
        self.detector_name = detector_name
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def detect_trends(self, data: Any, timeframe: timedelta = None) -> List[Trend]:
        """Detect trends in data"""
        pass
    
    @abstractmethod
    async def update_trend(self, trend: Trend, new_data: Any) -> Trend:
        """Update existing trend with new data"""
        pass


class StatisticalTrendDetector(TrendDetector):
    """Statistical trend detector using various algorithms"""
    
    def __init__(self, 
                 min_volume_threshold: float = 10.0,
                 min_velocity_threshold: float = 0.1,
                 significance_level: float = 0.05):
        super().__init__("statistical_detector")
        self.min_volume_threshold = min_volume_threshold
        self.min_velocity_threshold = min_velocity_threshold
        self.significance_level = significance_level
    
    async def detect_trends(self, 
                          data: pd.DataFrame, 
                          timeframe: timedelta = None) -> List[Trend]:
        """Detect trends using statistical methods"""
        trends = []
        
        # Ensure data has required columns
        if not all(col in data.columns for col in ['timestamp', 'content', 'value']):
            raise ValueError("Data must contain 'timestamp', 'content', and 'value' columns")
        
        # Group by content to analyze each potential trend
        grouped = data.groupby('content')
        
        for content, group in grouped:
            trend = await self._analyze_content_trend(content, group)
            if trend and self._passes_threshold_filters(trend):
                trends.append(trend)
        
        # Sort by virality score
        trends.sort(key=lambda t: t.metrics.virality_score, reverse=True)
        
        return trends
    
    async def _analyze_content_trend(self, content: str, data: pd.DataFrame) -> Optional[Trend]:
        """Analyze trend for specific content"""
        if len(data) < 3:  # Need minimum data points
            return None
        
        # Sort by timestamp
        data = data.sort_values('timestamp')
        
        # Calculate time series metrics
        values = data['value'].values
        timestamps = pd.to_datetime(data['timestamp'])
        
        # Volume (total)
        volume = float(np.sum(values))
        
        # Velocity (rate of change)
        time_diffs = (timestamps.diff().dt.total_seconds() / 3600).fillna(1)  # hours
        velocity_values = np.diff(values) / time_diffs[1:].values
        velocity = float(np.mean(velocity_values)) if len(velocity_values) > 0 else 0.0
        
        # Acceleration (change in velocity)
        acceleration = float(np.mean(np.diff(velocity_values))) if len(velocity_values) > 1 else 0.0
        
        # Reach (unique sources/users)
        reach = float(data['source'].nunique() if 'source' in data.columns else 1.0)
        
        # Engagement (if available)
        engagement = float(data['engagement'].mean() if 'engagement' in data.columns else 0.5)
        
        # Sentiment (if available)
        sentiment = float(data['sentiment'].mean() if 'sentiment' in data.columns else 0.0)
        
        # Virality score calculation
        virality_score = self._calculate_virality_score(
            volume, velocity, acceleration, reach, engagement
        )
        
        # Persistence (time span)
        time_span = (timestamps.max() - timestamps.min()).total_seconds() / 3600  # hours
        persistence = float(min(time_span / 168, 1.0))  # Normalize to weekly scale
        
        # Influence score (placeholder)
        influence_score = float(virality_score * 0.5)  # Simplified
        
        # Authenticity score (detect artificial trends)
        authenticity = await self._calculate_authenticity_score(data)
        
        # Create metrics
        metrics = TrendMetrics(
            volume=volume,
            velocity=velocity,
            acceleration=acceleration,
            reach=reach,
            engagement=engagement,
            sentiment=sentiment,
            virality_score=virality_score,
            persistence=persistence,
            influence_score=influence_score,
            authenticity=authenticity
        )
        
        # Determine trend status
        status = self._determine_trend_status(values, velocity, acceleration)
        
        # Determine trend type
        trend_type = self._classify_trend_type(content)
        
        # Create data points
        data_points = [
            TrendDataPoint(
                timestamp=timestamp,
                value=value,
                metadata=row.to_dict()
            )
            for timestamp, (_, row) in zip(timestamps, data.iterrows())
            for value in [row['value']]
        ]
        
        # Find peak timestamp
        peak_idx = np.argmax(values)
        peak_timestamp = timestamps.iloc[peak_idx]
        
        # Create trend
        trend = Trend(
            trend_id=f"trend_{hash(content)}_{int(timestamps.min().timestamp())}",
            content=content,
            trend_type=trend_type,
            status=status,
            scope=TrendScope.GLOBAL,  # Default, could be determined by data
            sources=[TrendSource.PLATFORM_ANALYTICS],  # Default
            metrics=metrics,
            data_points=data_points,
            peak_timestamp=peak_timestamp,
            start_timestamp=timestamps.min(),
            confidence=float(min(len(data) / 10, 1.0))  # More data = higher confidence
        )
        
        return trend
    
    def _calculate_virality_score(self, 
                                 volume: float, 
                                 velocity: float, 
                                 acceleration: float, 
                                 reach: float, 
                                 engagement: float) -> float:
        """Calculate virality score using multiple factors"""
        # Normalize factors
        norm_volume = min(volume / 1000, 1.0)  # Normalize to 0-1
        norm_velocity = min(max(velocity, 0) / 100, 1.0)  # Positive velocity only
        norm_acceleration = min(max(acceleration, 0) / 10, 1.0)  # Positive acceleration
        norm_reach = min(reach / 1000, 1.0)
        norm_engagement = min(max(engagement, 0), 1.0)
        
        # Weighted combination
        weights = {
            'volume': 0.2,
            'velocity': 0.3,
            'acceleration': 0.2,
            'reach': 0.2,
            'engagement': 0.1
        }
        
        virality_score = (
            weights['volume'] * norm_volume +
            weights['velocity'] * norm_velocity +
            weights['acceleration'] * norm_acceleration +
            weights['reach'] * norm_reach +
            weights['engagement'] * norm_engagement
        )
        
        return float(virality_score)
    
    async def _calculate_authenticity_score(self, data: pd.DataFrame) -> float:
        """Calculate authenticity score to detect artificial trends"""
        # Check for suspicious patterns
        authenticity_factors = []
        
        # Time pattern analysis
        timestamps = pd.to_datetime(data['timestamp'])
        time_diffs = timestamps.diff().dt.total_seconds().dropna()
        
        # Very regular posting intervals suggest bots
        if len(time_diffs) > 2:
            cv = np.std(time_diffs) / np.mean(time_diffs) if np.mean(time_diffs) > 0 else 1
            time_regularity = min(cv, 1.0)  # Higher CV = more authentic
            authenticity_factors.append(time_regularity * 0.3)
        
        # Source diversity
        if 'source' in data.columns:
            source_entropy = stats.entropy(data['source'].value_counts().values)
            max_entropy = np.log(len(data['source'].unique()))
            source_diversity = source_entropy / max_entropy if max_entropy > 0 else 0
            authenticity_factors.append(source_diversity * 0.4)
        
        # Content variation (if multiple content pieces)
        if 'full_content' in data.columns:
            unique_content_ratio = len(data['full_content'].unique()) / len(data)
            authenticity_factors.append(unique_content_ratio * 0.3)
        
        # Default to moderate authenticity if not enough data
        if not authenticity_factors:
            return 0.7
        
        return float(np.mean(authenticity_factors))
    
    def _determine_trend_status(self, values: np.ndarray, velocity: float, acceleration: float) -> TrendStatus:
        """Determine current trend status"""
        if len(values) < 2:
            return TrendStatus.EMERGING
        
        recent_trend = np.mean(values[-3:]) if len(values) >= 3 else values[-1]
        earlier_trend = np.mean(values[:-3]) if len(values) > 3 else values[0]
        
        # Check if viral (very high recent values)
        if recent_trend > 1000 and velocity > 50:
            return TrendStatus.VIRAL
        
        # Check growth patterns
        if velocity > self.min_velocity_threshold:
            if acceleration > 0:
                return TrendStatus.GROWING
            else:
                return TrendStatus.PEAKED
        elif velocity < -self.min_velocity_threshold:
            return TrendStatus.DECLINING
        else:
            if recent_trend > earlier_trend * 1.5:
                return TrendStatus.STABLE
            else:
                return TrendStatus.DEAD
    
    def _classify_trend_type(self, content: str) -> TrendType:
        """Classify the type of trend based on content"""
        content_lower = content.lower()
        
        # Simple pattern matching (could be enhanced with ML)
        if content.startswith('#'):
            return TrendType.HASHTAG
        elif any(word in content_lower for word in ['challenge', 'dance', 'trend']):
            return TrendType.CHALLENGE
        elif any(word in content_lower for word in ['song', 'music', 'artist', 'album']):
            return TrendType.MUSIC
        elif any(word in content_lower for word in ['meme', 'funny', 'joke']):
            return TrendType.MEME
        elif any(word in content_lower for word in ['news', 'breaking', 'update']):
            return TrendType.NEWS
        elif len(content.split()) == 1 and content.isalpha():
            return TrendType.KEYWORD
        else:
            return TrendType.TOPIC
    
    def _passes_threshold_filters(self, trend: Trend) -> bool:
        """Check if trend passes minimum thresholds"""



        return (trend.metrics.volume >= self.min_volume_threshold and 
                abs(trend.metrics.velocity) >= self.min_velocity_threshold)
    
    async def update_trend(self, trend: Trend, new_data: pd.DataFrame) -> Trend:
        """Update existing trend with new data"""
        # Combine old and new data
        old_data = pd.DataFrame([
            {
                'timestamp': dp.timestamp,
                'content': trend.content,
                'value': dp.value,
                **dp.metadata
            }
            for dp in trend.data_points
        ])
        
        combined_data = pd.concat([old_data, new_data], ignore_index=True)
        combined_data = combined_data.sort_values('timestamp')
        
        # Re-analyze with combined data
        updated_trend = await self._analyze_content_trend(trend.content, combined_data)
        
        if updated_trend:
            # Preserve original trend ID and creation time
            updated_trend.trend_id = trend.trend_id
            updated_trend.start_timestamp = trend.start_timestamp
            updated_trend.related_trends = trend.related_trends
            updated_trend.tags = trend.tags
            
            return updated_trend
        
        return trend


class MachineLearningTrendDetector(TrendDetector):
    """ML-based trend detector using clustering and NLP"""
    
    def __init__(self, device: str = "auto"):
        super().__init__("ml_detector")
        self.device = device
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        self.topic_model = LatentDirichletAllocation(n_components=20, random_state=42)
        self.clustering_model = DBSCAN(eps=0.3, min_samples=5)
        self.scaler = MinMaxScaler()
        self.nlp_pipeline = None
        self.is_loaded = False
    
    async def load_models(self):
        """Load ML models"""



        try:
            # Load sentence transformer for semantic similarity
            self.nlp_pipeline = pipeline(
                "feature-extraction",
                model="sentence-transformers/all-MiniLM-L6-v2",
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.is_loaded = True
            self.logger.info("ML trend detector loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load ML models: {e}")
            raise
    
    async def detect_trends(self, 
                          data: List[Dict[str, Any]], 
                          timeframe: timedelta = None) -> List[Trend]:
        """Detect trends using ML clustering and topic modeling"""
        if not self.is_loaded:
            await self.load_models()
        
        if not data:
            return []
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Text clustering for similar content
        text_clusters = await self._cluster_content(df)
        
        # Topic modeling for thematic trends
        topic_trends = await self._extract_topic_trends(df)
        
        # Semantic similarity grouping
        semantic_groups = await self._group_by_semantic_similarity(df)
        
        # Combine and rank trends
        all_trends = text_clusters + topic_trends + semantic_groups
        
        # Remove duplicates and rank
        unique_trends = self._deduplicate_trends(all_trends)
        unique_trends.sort(key=lambda t: t.metrics.virality_score, reverse=True)
        
        return unique_trends[:50]  # Return top 50 trends
    
    async def _cluster_content(self, df: pd.DataFrame) -> List[Trend]:
        """Cluster similar content to identify trends"""
        if 'content' not in df.columns:
            return []
        
        # Vectorize content
        try:
            content_vectors = self.vectorizer.fit_transform(df['content'])
            
            # Cluster
            clusters = self.clustering_model.fit_predict(content_vectors.toarray())
            df['cluster'] = clusters
            
            trends = []
            
            # Analyze each cluster
            for cluster_id in set(clusters):
                if cluster_id == -1:  # Skip noise cluster
                    continue
                
                cluster_data = df[df['cluster'] == cluster_id]
                
                if len(cluster_data) < 3:  # Skip small clusters
                    continue
                
                # Find representative content
                cluster_content = self._get_cluster_representative(
                    cluster_data['content'].tolist()
                )
                
                # Create trend from cluster
                trend = await self._create_trend_from_cluster(cluster_content, cluster_data)
                if trend:
                    trends.append(trend)
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Content clustering failed: {e}")
            return []
    
    async def _extract_topic_trends(self, df: pd.DataFrame) -> List[Trend]:
        """Extract trends using topic modeling"""
        if 'content' not in df.columns or len(df) < 10:
            return []
        
        try:
            # Vectorize for topic modeling
            content_vectors = self.vectorizer.fit_transform(df['content'])
            
            # Fit topic model
            self.topic_model.fit(content_vectors)
            
            # Get topic distributions
            topic_distributions = self.topic_model.transform(content_vectors)
            
            # Get top topics
            feature_names = self.vectorizer.get_feature_names_out()
            
            trends = []
            
            for topic_idx, topic in enumerate(self.topic_model.components_):
                # Get top words for topic
                top_words = [feature_names[i] for i in topic.argsort()[-10:]]
                topic_content = ' '.join(top_words)
                
                # Find documents belonging to this topic
                topic_docs = np.where(topic_distributions.argmax(axis=1) == topic_idx)[0]
                
                if len(topic_docs) < 5:  # Skip small topics
                    continue
                
                # Create topic trend
                topic_data = df.iloc[topic_docs]
                trend = await self._create_trend_from_cluster(topic_content, topic_data)
                if trend:
                    trend.trend_type = TrendType.TOPIC
                    trends.append(trend)
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Topic modeling failed: {e}")
            return []
    
    async def _group_by_semantic_similarity(self, df: pd.DataFrame) -> List[Trend]:
        """Group content by semantic similarity"""
        if not self.nlp_pipeline or len(df) < 5:
            return []
        
        try:
            # Get embeddings for all content
            embeddings = []
            contents = df['content'].tolist()
            
            for content in contents:
                try:
                    embedding = self.nlp_pipeline(content[:512])  # Limit length
                    # Average pool the embeddings
                    avg_embedding = np.mean(embedding[0], axis=0)
                    embeddings.append(avg_embedding)
                except:
                    embeddings.append(np.zeros(384))  # Default embedding size
            
            embeddings = np.array(embeddings)
            
            # Cluster embeddings
            kmeans = KMeans(n_clusters=min(10, len(embeddings)//3), random_state=42)
            semantic_clusters = kmeans.fit_predict(embeddings)
            
            df['semantic_cluster'] = semantic_clusters
            
            trends = []
            
            for cluster_id in set(semantic_clusters):
                cluster_data = df[df['semantic_cluster'] == cluster_id]
                
                if len(cluster_data) < 3:
                    continue
                
                # Get cluster representative
                cluster_content = self._get_cluster_representative(
                    cluster_data['content'].tolist()
                )
                
                trend = await self._create_trend_from_cluster(cluster_content, cluster_data)
                if trend:
                    trends.append(trend)
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Semantic clustering failed: {e}")
            return []
    
    def _get_cluster_representative(self, contents: List[str]) -> str:
        """Get representative content for a cluster"""
        # Simple approach: return most frequent content or longest
        counter = Counter(contents)
        most_common = counter.most_common(1)
        
        if most_common and most_common[0][1] > 1:
            return most_common[0][0]
        
        # Return longest content
        return max(contents, key=len)
    
    async def _create_trend_from_cluster(self, content: str, data: pd.DataFrame) -> Optional[Trend]:
        """Create trend object from cluster data"""
        if len(data) < 2:
            return None
        
        # Calculate basic metrics
        volume = float(len(data))
        
        # Time-based metrics if timestamp available
        if 'timestamp' in data.columns:
            timestamps = pd.to_datetime(data['timestamp'])
            time_span = (timestamps.max() - timestamps.min()).total_seconds() / 3600
            velocity = volume / max(time_span, 1)
            start_time = timestamps.min()
        else:
            velocity = volume
            start_time = datetime.now()
        
        # Other metrics
        reach = float(data['source'].nunique() if 'source' in data.columns else volume)
        engagement = float(data['engagement'].mean() if 'engagement' in data.columns else 0.5)
        sentiment = float(data['sentiment'].mean() if 'sentiment' in data.columns else 0.0)
        
        # Calculate virality score
        virality_score = min((velocity * reach * engagement) / 1000, 1.0)
        
        metrics = TrendMetrics(
            volume=volume,
            velocity=velocity,
            acceleration=0.0,  # Would need time series for this
            reach=reach,
            engagement=engagement,
            sentiment=sentiment,
            virality_score=virality_score,
            persistence=min(time_span / 24, 1.0) if 'timestamp' in data.columns else 0.5,
            influence_score=virality_score * 0.7,
            authenticity=0.8  # Default for ML-detected trends
        )
        
        # Create data points
        data_points = []
        if 'timestamp' in data.columns:
            for _, row in data.iterrows():
                data_points.append(TrendDataPoint(
                    timestamp=pd.to_datetime(row['timestamp']),
                    value=row.get('value', 1.0),
                    metadata=row.to_dict()
                ))
        
        trend = Trend(
            trend_id=f"ml_trend_{hash(content)}_{int(start_time.timestamp())}",
            content=content,
            trend_type=TrendType.TOPIC,
            status=TrendStatus.GROWING,  # Default for newly detected
            scope=TrendScope.GLOBAL,
            sources=[TrendSource.PLATFORM_ANALYTICS],
            metrics=metrics,
            data_points=data_points,
            start_timestamp=start_time,
            confidence=min(len(data) / 20, 1.0)
        )
        
        return trend
    
    def _deduplicate_trends(self, trends: List[Trend]) -> List[Trend]:
        """Remove duplicate or very similar trends"""
        if not trends:
            return []
        
        unique_trends = []
        seen_contents = set()
        
        for trend in trends:
            # Simple deduplication by content similarity
            similar_found = False
            
            for seen_content in seen_contents:
                # Calculate simple similarity
                similarity = self._calculate_content_similarity(trend.content, seen_content)
                if similarity > 0.8:  # High similarity threshold
                    similar_found = True
                    break
            
            if not similar_found:
                unique_trends.append(trend)
                seen_contents.add(trend.content)
        
        return unique_trends
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content strings"""
        # Simple Jaccard similarity
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def update_trend(self, trend: Trend, new_data: Any) -> Trend:
        """Update trend with new data"""
        # For ML trends, we'd need to re-run the clustering
        # This is a simplified update
        if hasattr(new_data, '__iter__') and not isinstance(new_data, str):
            trend.metrics.volume += len(new_data)
            trend.confidence = min(trend.confidence + 0.1, 1.0)
        
        return trend


class TrendPredictor:
    """Predict future trend behavior using various models"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.models = {}
    
    async def predict_trend_future(self, trend: Trend, horizon: timedelta = None) -> TrendPrediction:
        """Predict future behavior of a trend"""
        if not horizon:
            horizon = timedelta(days=7)  # Default 1 week prediction
        
        # Extract time series data
        if not trend.data_points:
            return self._create_low_confidence_prediction(trend, horizon)
        
        # Prepare time series
        timestamps = [dp.timestamp for dp in trend.data_points]
        values = [dp.value for dp in trend.data_points]
        
        if len(values) < 3:
            return self._create_low_confidence_prediction(trend, horizon)
        
        # Simple trend analysis
        predicted_status = await self._predict_status(trend, values)
        predicted_peak, predicted_end = await self._predict_lifecycle(trend, timestamps, values, horizon)
        
        # Confidence based on data quality and trend clarity
        confidence = self._calculate_prediction_confidence(trend, values)
        
        # Supporting and risk factors
        supporting_factors, risk_factors = await self._analyze_trend_factors(trend)
        
        return TrendPrediction(
            trend_id=trend.trend_id,
            predicted_status=predicted_status,
            predicted_peak=predicted_peak,
            predicted_end=predicted_end,
            confidence=confidence,
            supporting_factors=supporting_factors,
            risk_factors=risk_factors,
            prediction_horizon=horizon,
            model_used="statistical_analysis"
        )
    
    def _create_low_confidence_prediction(self, trend: Trend, horizon: timedelta) -> TrendPrediction:
        """Create low confidence prediction for trends with insufficient data"""



        return TrendPrediction(
            trend_id=trend.trend_id,
            predicted_status=TrendStatus.STABLE,
            predicted_peak=None,
            predicted_end=None,
            confidence=0.2,
            supporting_factors=["Insufficient data"],
            risk_factors=["Limited historical data", "High uncertainty"],
            prediction_horizon=horizon,
            model_used="default_prediction"
        )
    
    async def _predict_status(self, trend: Trend, values: List[float]) -> TrendStatus:
        """Predict future trend status"""
        recent_values = values[-3:] if len(values) >= 3 else values
        trend_direction = np.mean(np.diff(recent_values)) if len(recent_values) > 1 else 0
        
        current_status = trend.status
        
        # Simple state transitions
        if current_status == TrendStatus.EMERGING:
            return TrendStatus.GROWING if trend_direction > 0 else TrendStatus.STABLE
        elif current_status == TrendStatus.GROWING:
            if trend_direction > trend.metrics.velocity * 0.5:
                return TrendStatus.VIRAL
            elif trend_direction < 0:
                return TrendStatus.PEAKED
            else:
                return TrendStatus.GROWING
        elif current_status == TrendStatus.PEAKED:
            return TrendStatus.DECLINING if trend_direction < 0 else TrendStatus.STABLE
        elif current_status == TrendStatus.VIRAL:
            return TrendStatus.DECLINING  # Viral trends typically decline
        else:
            return current_status
    
    async def _predict_lifecycle(self, 
                               trend: Trend, 
                               timestamps: List[datetime], 
                               values: List[float],
                               horizon: timedelta) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Predict peak and end times"""
        if len(values) < 3:
            return None, None
        
        # Find current peak
        current_peak_idx = np.argmax(values)
        current_peak_time = timestamps[current_peak_idx]
        
        # Simple lifecycle model
        trend_age = datetime.now() - trend.start_timestamp
        
        # Predict peak (if not already peaked)
        predicted_peak = None
        if trend.status not in [TrendStatus.PEAKED, TrendStatus.DECLINING, TrendStatus.DEAD]:
            # Estimate peak based on growth rate
            if trend.metrics.velocity > 0:
                days_to_peak = max(1, min(30, 100 / (trend.metrics.velocity + 1)))
                predicted_peak = datetime.now() + timedelta(days=days_to_peak)
        
        # Predict end
        predicted_end = None
        if trend.status in [TrendStatus.DECLINING, TrendStatus.PEAKED]:
            # Estimate end based on decline rate
            if trend.metrics.velocity < 0:
                days_to_end = max(1, min(90, abs(100 / trend.metrics.velocity)))
                predicted_end = datetime.now() + timedelta(days=days_to_end)
        elif trend.status not in [TrendStatus.DEAD]:
            # Estimate typical trend lifetime
            typical_lifetime_days = 30  # Default trend lifetime
            predicted_end = trend.start_timestamp + timedelta(days=typical_lifetime_days)
        
        return predicted_peak, predicted_end
    
    def _calculate_prediction_confidence(self, trend: Trend, values: List[float]) -> float:
        """Calculate confidence in predictions"""
        confidence_factors = []
        
        # Data quantity factor
        data_quantity = min(len(values) / 20, 1.0)
        confidence_factors.append(data_quantity * 0.3)
        
        # Trend clarity factor (how consistent the trend is)
        if len(values) > 2:
            trend_consistency = 1.0 - (np.std(values) / (np.mean(values) + 1e-6))
            trend_consistency = max(0, min(trend_consistency, 1))
            confidence_factors.append(trend_consistency * 0.3)
        
        # Metrics quality
        metrics_confidence = (trend.metrics.authenticity + trend.confidence) / 2
        confidence_factors.append(metrics_confidence * 0.4)
        
        return float(np.mean(confidence_factors)) if confidence_factors else 0.3
    
    async def _analyze_trend_factors(self, trend: Trend) -> Tuple[List[str], List[str]]:
        """Analyze supporting and risk factors for trend"""
        supporting_factors = []
        risk_factors = []
        
        # Supporting factors
        if trend.metrics.virality_score > 0.7:
            supporting_factors.append("High virality score")
        
        if trend.metrics.engagement > 0.6:
            supporting_factors.append("Strong engagement")
        
        if trend.metrics.authenticity > 0.7:
            supporting_factors.append("Authentic organic growth")
        
        if trend.metrics.reach > 1000:
            supporting_factors.append("Wide reach")
        
        # Risk factors
        if trend.metrics.authenticity < 0.5:
            risk_factors.append("Potentially artificial trend")
        
        if trend.metrics.sentiment < -0.3:
            risk_factors.append("Negative sentiment")
        
        if trend.status == TrendStatus.VIRAL:
            risk_factors.append("Viral trends typically have short lifespans")
        
        if len(trend.data_points) < 5:
            risk_factors.append("Limited historical data")
        
        return supporting_factors, risk_factors


class TrendAnalyticsEngine:
    """Main engine orchestrating trend detection and analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.statistical_detector = StatisticalTrendDetector()
        self.ml_detector = MachineLearningTrendDetector()
        self.predictor = TrendPredictor()
        self.active_trends = {}  # trend_id -> Trend
        self.trend_history = []
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the analytics engine"""



        try:
            await self.ml_detector.load_models()
            self.is_initialized = True
            self.logger.info("Trend analytics engine initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize trend engine: {e}")
            raise
    
    async def analyze_trends(self, data: Any, method: str = "combined") -> Dict[str, Any]:
        """Analyze trends using specified method"""
        if not self.is_initialized:
            await self.initialize()
        
        results = {
            'trends': [],
            'predictions': [],
            'summary': {},
            'processing_time_ms': 0
        }
        
        start_time = datetime.now()
        
        try:
            detected_trends = []
            
            if method in ["statistical", "combined"]:
                if isinstance(data, pd.DataFrame):
                    stat_trends = await self.statistical_detector.detect_trends(data)
                    detected_trends.extend(stat_trends)
            
            if method in ["ml", "combined"]:
                if isinstance(data, list):
                    ml_trends = await self.ml_detector.detect_trends(data)
                    detected_trends.extend(ml_trends)
            
            # Update active trends
            for trend in detected_trends:
                if trend.trend_id in self.active_trends:
                    # Update existing trend
                    self.active_trends[trend.trend_id] = trend
                else:
                    # Add new trend
                    self.active_trends[trend.trend_id] = trend
            
            # Generate predictions for top trends
            predictions = []
            top_trends = sorted(detected_trends, key=lambda t: t.metrics.virality_score, reverse=True)[:10]
            
            for trend in top_trends:
                prediction = await self.predictor.predict_trend_future(trend)
                predictions.append(prediction)
            
            # Create summary
            summary = self._create_analysis_summary(detected_trends, predictions)
            
            results['trends'] = [trend.to_dict() for trend in detected_trends]
            results['predictions'] = [pred.to_dict() for pred in predictions]
            results['summary'] = summary
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {e}")
            results['error'] = str(e)
        
        # Processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        results['processing_time_ms'] = processing_time
        
        return results
    
    def _create_analysis_summary(self, trends: List[Trend], predictions: List[TrendPrediction]) -> Dict[str, Any]:
        """Create summary of trend analysis"""
        if not trends:
            return {'total_trends': 0, 'message': 'No trends detected'}
        
        # Status distribution
        status_dist = Counter(trend.status.value for trend in trends)
        
        # Type distribution
        type_dist = Counter(trend.trend_type.value for trend in trends)
        
        # Top trends
        top_trends = sorted(trends, key=lambda t: t.metrics.virality_score, reverse=True)[:5]
        
        # Viral trends
        viral_trends = [t for t in trends if t.status == TrendStatus.VIRAL]
        
        # Emerging trends
        emerging_trends = [t for t in trends if t.status == TrendStatus.EMERGING]
        
        return {
            'total_trends': len(trends),
            'status_distribution': dict(status_dist),
            'type_distribution': dict(type_dist),
            'viral_trends_count': len(viral_trends),
            'emerging_trends_count': len(emerging_trends),
            'top_trends': [
                {
                    'content': trend.content,
                    'virality_score': trend.metrics.virality_score,
                    'status': trend.status.value
                }
                for trend in top_trends
            ],
            'average_virality_score': np.mean([t.metrics.virality_score for t in trends]),
            'prediction_confidence_avg': np.mean([p.confidence for p in predictions]) if predictions else 0,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    async def get_trend_by_id(self, trend_id: str) -> Optional[Trend]:
        """Get specific trend by ID"""



        return self.active_trends.get(trend_id)
    
    async def get_trending_now(self, limit: int = 20) -> List[Trend]:
        """Get currently trending items"""
        # Filter for active, high-scoring trends
        current_trends = [
            trend for trend in self.active_trends.values()
            if trend.status in [TrendStatus.VIRAL, TrendStatus.GROWING, TrendStatus.EMERGING]
        ]
        
        # Sort by virality score
        current_trends.sort(key=lambda t: t.metrics.virality_score, reverse=True)
        
        return current_trends[:limit]
    
    async def export_trends(self, filepath: str, format: str = "json"):
        """Export trends to file"""



        try:
            trends_data = {
                'active_trends': {tid: trend.to_dict() for tid, trend in self.active_trends.items()},
                'export_timestamp': datetime.now().isoformat(),
                'total_trends': len(self.active_trends)
            }
            
            if format.lower() == "json":
                with open(filepath, 'w') as f:
                    json.dump(trends_data, f, indent=2, default=str)
            elif format.lower() == "pickle":
                with open(filepath, 'wb') as f:
                    pickle.dump(trends_data, f)
            
            self.logger.info(f"Trends exported to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to export trends: {e}")
            raise


# Export main classes
__all__ = [
    'TrendAnalyticsEngine',
    'StatisticalTrendDetector',
    'MachineLearningTrendDetector',
    'TrendPredictor',
    'Trend',
    'TrendMetrics',
    'TrendPrediction',
    'TrendDataPoint',
    'TrendStatus',
    'TrendType',
    'TrendScope',
    'TrendSource'
]
