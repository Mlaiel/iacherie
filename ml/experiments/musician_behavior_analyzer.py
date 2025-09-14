"""🎵 Musician Behavior Analyzer - Creator-Specific Research
=========================================================
Module: ml/experiments/musician_behavior_analyzer.py
Author: Fahed Mlaiel (mlaiel@live.de)
=========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MUSICIAN BEHAVIOR ANALYSIS & OPTIMIZATION
Deep analysis of musician content patterns and audience engagement
- Music content pattern recognition
- Audience engagement prediction
- Creator behavior modeling
- Revenue optimization strategies
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import pickle
import torch
import torch.nn as nn
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, precision_score
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

class MusicGenre(Enum):
    """Music genre categories"""
    POP = "pop"
    ROCK = "rock"
    HIP_HOP = "hip_hop"
    ELECTRONIC = "electronic"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    COUNTRY = "country"
    R_AND_B = "r_and_b"
    INDIE = "indie"
    ALTERNATIVE = "alternative"
    FOLK = "folk"
    METAL = "metal"

class ContentType(Enum):
    """Musician content types"""
    ORIGINAL_SONG = "original_song"
    COVER_SONG = "cover_song"
    INSTRUMENTAL = "instrumental"
    BEHIND_SCENES = "behind_scenes"
    LIVE_PERFORMANCE = "live_performance"
    MUSIC_VIDEO = "music_video"
    STUDIO_SESSION = "studio_session"
    COLLABORATION = "collaboration"
    TUTORIAL = "tutorial"
    FREESTYLE = "freestyle"

class EngagementMetric(Enum):
    """Engagement measurement types"""
    VIEWS = "views"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    SAVES = "saves"
    PLAYLIST_ADDS = "playlist_adds"
    DOWNLOADS = "downloads"
    STREAM_TIME = "stream_time"

@dataclass
class MusicContent:
    """Individual music content piece"""
    content_id: str
    musician_id: str
    title: str
    genre: MusicGenre
    content_type: ContentType
    duration_seconds: float
    upload_date: datetime
    audio_features: Dict[str, float] = field(default_factory=dict)
    engagement_metrics: Dict[EngagementMetric, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MusicianProfile:
    """Musician profile and behavior patterns"""
    musician_id: str
    name: str
    primary_genre: MusicGenre
    secondary_genres: List[MusicGenre] = field(default_factory=list)
    follower_count: int = 0
    content_count: int = 0
    total_views: int = 0
    average_engagement_rate: float = 0.0
    posting_frequency: float = 0.0  # posts per week
    peak_activity_hours: List[int] = field(default_factory=list)
    collaboration_network: List[str] = field(default_factory=list)
    revenue_streams: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AudioFeatures:
    """Audio feature extraction results"""
    tempo: float
    key: str
    mode: str  # major/minor
    danceability: float
    energy: float
    loudness: float
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float  # positivity
    time_signature: int

class AudioFeatureExtractor:
    """Extract audio features from music content"""
    
    def __init__(self) -> None:
        self.sample_rate = 22050
        self.hop_length = 512
        
    async def extract_features(self, audio_file_path: str) -> AudioFeatures:
        """Extract comprehensive audio features"""
        try:
            # Simulate audio feature extraction (in real implementation would use librosa)
            # This is a placeholder that generates realistic values
            
            # Simulate tempo detection
            tempo = np.random.uniform(60, 180)
            
            # Simulate key detection
            keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            key = np.random.choice(keys)
            
            # Simulate mode detection
            mode = np.random.choice(['major', 'minor'])
            
            # Simulate various audio characteristics (0-1 scale)
            features = AudioFeatures(
                tempo=tempo,
                key=key,
                mode=mode,
                danceability=np.random.uniform(0, 1),
                energy=np.random.uniform(0, 1),
                loudness=np.random.uniform(-60, 0),  # dB
                speechiness=np.random.uniform(0, 1),
                acousticness=np.random.uniform(0, 1),
                instrumentalness=np.random.uniform(0, 1),
                liveness=np.random.uniform(0, 1),
                valence=np.random.uniform(0, 1),
                time_signature=np.random.choice([3, 4, 5, 6, 7])
            )
            
            logger.info(f"Extracted audio features: tempo={tempo:.1f}, key={key}, energy={features.energy:.3f}")
            return features
            
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {e}")
            raise

class EngagementPredictor:
    """Predict engagement based on content and musician features"""
    
    def __init__(self) -> None:
        self.model = None
        self.feature_scaler = None
        self.trained = False
        
    async def train_engagement_model(
        self,
        content_data: List[MusicContent],
        musician_profiles: List[MusicianProfile]
    ) -> Dict[str, Any]:
        """Train engagement prediction model"""
        try:
            # Prepare training data
            features, targets = await self._prepare_training_data(content_data, musician_profiles)
            
            # Build neural network model
            self.model = self._build_engagement_model(features.shape[1])
            
            # Train model
            training_results = await self._train_model(features, targets)
            
            self.trained = True
            logger.info(f"Engagement prediction model trained: {training_results['accuracy']:.4f} accuracy")
            
            return training_results
            
        except Exception as e:
            logger.error(f"Engagement model training failed: {e}")
            raise
    
    async def _prepare_training_data(
        self,
        content_data: List[MusicContent],
        musician_profiles: List[MusicianProfile]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and targets for training"""
        features = []
        targets = []
        
        # Create musician lookup
        musician_dict = {p.musician_id: p for p in musician_profiles}
        
        for content in content_data:
            musician = musician_dict.get(content.musician_id)
            if not musician:
                continue
            
            # Content features
            content_features = [
                content.duration_seconds / 300,  # Normalized duration
                len(content.title) / 100,  # Title length
                content.genre.value.__hash__() % 100 / 100,  # Genre encoding
                content.content_type.value.__hash__() % 100 / 100,  # Type encoding
            ]
            
            # Audio features
            audio_features = list(content.audio_features.values())[:10]  # First 10 features
            while len(audio_features) < 10:
                audio_features.append(0.0)
            
            # Musician features
            musician_features = [
                np.log1p(musician.follower_count) / 20,  # Log-normalized followers
                musician.posting_frequency / 10,  # Posts per week
                musician.average_engagement_rate,
                len(musician.collaboration_network) / 50,  # Collaboration count
            ]
            
            # Temporal features
            days_since_upload = (datetime.utcnow() - content.upload_date).days
            temporal_features = [
                days_since_upload / 365,  # Normalized age
                content.upload_date.hour / 24,  # Upload time
                content.upload_date.weekday() / 7,  # Day of week
            ]
            
            # Combine all features
            sample_features = content_features + audio_features + musician_features + temporal_features
            features.append(sample_features)
            
            # Target: total engagement score
            total_engagement = sum(content.engagement_metrics.values())
            normalized_engagement = np.log1p(total_engagement) / 15  # Log-normalized
            targets.append(normalized_engagement)
        
        return np.array(features), np.array(targets)
    
    def _build_engagement_model(self, input_size: int) -> nn.Module:
        """Build neural network for engagement prediction"""
        model = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        return model
    
    async def _train_model(self, features: np.ndarray, targets: np.ndarray) -> Dict[str, Any]:
        """Train the engagement prediction model"""
        try:
            # Convert to PyTorch tensors
            X = torch.FloatTensor(features)
            y = torch.FloatTensor(targets).unsqueeze(1)
            
            # Split data
            split_idx = int(0.8 * len(X))
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Training setup
            criterion = nn.MSELoss()
            optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001, weight_decay=1e-5)
            
            # Training loop
            epochs = 100
            train_losses = []
            
            self.model.train()
            for epoch in range(epochs):
                optimizer.zero_grad()
                outputs = self.model(X_train)
                loss = criterion(outputs, y_train)
                loss.backward()
                optimizer.step()
                
                train_losses.append(loss.item())
                
                if epoch % 20 == 0:
                    logger.info(f"Epoch {epoch}: Loss = {loss.item():.6f}")
            
            # Evaluation
            self.model.eval()
            with torch.no_grad():
                test_outputs = self.model(X_test)
                test_loss = criterion(test_outputs, y_test).item()
                
                # Calculate R² score
                y_test_np = y_test.numpy()
                test_outputs_np = test_outputs.numpy()
                ss_res = np.sum((y_test_np - test_outputs_np) ** 2)
                ss_tot = np.sum((y_test_np - np.mean(y_test_np)) ** 2)
                r2_score = 1 - (ss_res / ss_tot)
            
            return {
                'train_loss': train_losses[-1],
                'test_loss': test_loss,
                'accuracy': r2_score,
                'epochs': epochs,
                'train_history': train_losses
            }
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise
    
    async def predict_engagement(
        self,
        content: MusicContent,
        musician: MusicianProfile
    ) -> Dict[str, Any]:
        """Predict engagement for new content"""
        try:
            if not self.trained:
                raise ValueError("Model must be trained before prediction")
            
            # Prepare features (same as training)
            content_features = [
                content.duration_seconds / 300,
                len(content.title) / 100,
                content.genre.value.__hash__() % 100 / 100,
                content.content_type.value.__hash__() % 100 / 100,
            ]
            
            audio_features = list(content.audio_features.values())[:10]
            while len(audio_features) < 10:
                audio_features.append(0.0)
            
            musician_features = [
                np.log1p(musician.follower_count) / 20,
                musician.posting_frequency / 10,
                musician.average_engagement_rate,
                len(musician.collaboration_network) / 50,
            ]
            
            temporal_features = [
                0.0,  # New content
                content.upload_date.hour / 24,
                content.upload_date.weekday() / 7,
            ]
            
            sample_features = content_features + audio_features + musician_features + temporal_features
            
            # Make prediction
            self.model.eval()
            with torch.no_grad():
                X = torch.FloatTensor(sample_features).unsqueeze(0)
                prediction = self.model(X).item()
            
            # Convert back to interpretable metrics
            expected_engagement = np.expm1(prediction * 15)
            confidence_score = min(1.0, max(0.0, prediction))
            
            return {
                'predicted_engagement': expected_engagement,
                'confidence_score': confidence_score,
                'engagement_category': self._categorize_engagement(prediction),
                'recommendations': await self._generate_engagement_recommendations(content, prediction)
            }
            
        except Exception as e:
            logger.error(f"Engagement prediction failed: {e}")
            raise
    
    def _categorize_engagement(self, predicted_score: float) -> str:
        """Categorize engagement level"""
        if predicted_score >= 0.8:
            return "viral_potential"
        elif predicted_score >= 0.6:
            return "high_engagement"
        elif predicted_score >= 0.4:
            return "moderate_engagement"
        elif predicted_score >= 0.2:
            return "low_engagement"
        else:
            return "minimal_engagement"
    
    async def _generate_engagement_recommendations(
        self,
        content: MusicContent,
        predicted_score: float
    ) -> List[str]:
        """Generate recommendations to improve engagement"""
        recommendations = []
        
        if predicted_score < 0.3:
            recommendations.append("Consider optimizing upload timing for peak audience activity")
            recommendations.append("Enhance audio quality and production value")
            recommendations.append("Add more descriptive and engaging title")
        
        if content.duration_seconds > 240:  # 4 minutes
            recommendations.append("Consider shorter content for better retention")
        
        if content.content_type == ContentType.ORIGINAL_SONG:
            recommendations.append("Share behind-the-scenes content for deeper connection")
        
        recommendations.append("Engage with comments and community interaction")
        recommendations.append("Cross-promote on other social platforms")
        
        return recommendations

class BehaviorPatternAnalyzer:
    """Analyze musician behavior patterns and trends"""
    
    def __init__(self) -> None:
        self.clustering_model = None
        self.pattern_history: List[Dict[str, Any]] = []
    
    async def analyze_posting_patterns(
        self,
        musician_profiles: List[MusicianProfile],
        content_data: List[MusicContent]
    ) -> Dict[str, Any]:
        """Analyze posting patterns and optimal timing"""
        try:
            # Group content by musician
            musician_content = {}
            for content in content_data:
                if content.musician_id not in musician_content:
                    musician_content[content.musician_id] = []
                musician_content[content.musician_id].append(content)
            
            posting_analysis = {}
            
            for musician in musician_profiles:
                if musician.musician_id not in musician_content:
                    continue
                
                contents = musician_content[musician.musician_id]
                
                # Analyze posting times
                posting_hours = [c.upload_date.hour for c in contents]
                posting_days = [c.upload_date.weekday() for c in contents]
                
                # Calculate posting frequency
                if len(contents) > 1:
                    date_range = (max(c.upload_date for c in contents) - 
                                 min(c.upload_date for c in contents)).days
                    frequency = len(contents) / max(1, date_range / 7)  # posts per week
                else:
                    frequency = 0
                
                # Engagement by posting time
                hourly_engagement = {}
                for content in contents:
                    hour = content.upload_date.hour
                    engagement = sum(content.engagement_metrics.values())
                    if hour not in hourly_engagement:
                        hourly_engagement[hour] = []
                    hourly_engagement[hour].append(engagement)
                
                # Average engagement by hour
                avg_hourly_engagement = {
                    hour: np.mean(engagements) 
                    for hour, engagements in hourly_engagement.items()
                }
                
                optimal_hours = sorted(avg_hourly_engagement.items(), 
                                     key=lambda x: x[1], reverse=True)[:3]
                
                posting_analysis[musician.musician_id] = {
                    'posting_frequency': frequency,
                    'peak_hours': [h for h, _ in optimal_hours],
                    'preferred_hours': posting_hours,
                    'preferred_days': posting_days,
                    'optimal_engagement_times': optimal_hours,
                    'consistency_score': self._calculate_consistency_score(contents)
                }
            
            # Global patterns
            all_hours = [c.upload_date.hour for c in content_data]
            all_days = [c.upload_date.weekday() for c in content_data]
            
            global_patterns = {
                'peak_posting_hours': list(np.bincount(all_hours).argsort()[-3:]),
                'peak_posting_days': list(np.bincount(all_days).argsort()[-3:]),
                'average_posting_frequency': np.mean([
                    analysis['posting_frequency'] 
                    for analysis in posting_analysis.values()
                ])
            }
            
            return {
                'individual_patterns': posting_analysis,
                'global_patterns': global_patterns,
                'recommendations': await self._generate_posting_recommendations(posting_analysis)
            }
            
        except Exception as e:
            logger.error(f"Posting pattern analysis failed: {e}")
            raise
    
    def _calculate_consistency_score(self, contents: List[MusicContent]) -> float:
        """Calculate posting consistency score"""
        if len(contents) < 2:
            return 0.0
        
        # Calculate intervals between posts
        sorted_contents = sorted(contents, key=lambda c: c.upload_date)
        intervals = []
        
        for i in range(1, len(sorted_contents)):
            interval = (sorted_contents[i].upload_date - sorted_contents[i-1].upload_date).days
            intervals.append(interval)
        
        # Consistency based on variance of intervals
        if len(intervals) == 0:
            return 0.0
        
        interval_std = np.std(intervals)
        interval_mean = np.mean(intervals)
        
        # Lower variance = higher consistency
        consistency = max(0.0, 1.0 - (interval_std / max(1.0, interval_mean)))
        return consistency
    
    async def _generate_posting_recommendations(
        self,
        posting_analysis: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Generate posting strategy recommendations"""
        recommendations = []
        
        # Analyze patterns across all musicians
        all_frequencies = [a['posting_frequency'] for a in posting_analysis.values()]
        avg_frequency = np.mean(all_frequencies)
        
        if avg_frequency < 2:
            recommendations.append("Increase posting frequency to 2-3 times per week for better visibility")
        
        # Common optimal hours
        all_peak_hours = []
        for analysis in posting_analysis.values():
            all_peak_hours.extend(analysis['peak_hours'])
        
        if all_peak_hours:
            most_common_hour = max(set(all_peak_hours), key=all_peak_hours.count)
            recommendations.append(f"Consider posting around {most_common_hour}:00 for optimal engagement")
        
        recommendations.append("Maintain consistent posting schedule to build audience expectations")
        recommendations.append("Analyze individual engagement patterns for personalized timing")
        
        return recommendations
    
    async def cluster_musician_behavior(
        self,
        musician_profiles: List[MusicianProfile]
    ) -> Dict[str, Any]:
        """Cluster musicians by behavior patterns"""
        try:
            # Prepare features for clustering
            features = []
            musician_ids = []
            
            for musician in musician_profiles:
                feature_vector = [
                    np.log1p(musician.follower_count),
                    musician.posting_frequency,
                    musician.average_engagement_rate,
                    len(musician.collaboration_network),
                    len(musician.secondary_genres),
                    musician.primary_genre.value.__hash__() % 100,
                ]
                
                features.append(feature_vector)
                musician_ids.append(musician.musician_id)
            
            features_array = np.array(features)
            
            # Perform clustering
            n_clusters = min(5, max(1, len(musician_profiles) // 3))  # Ensure at least 1 cluster
            if len(musician_profiles) < 2:
                # Handle case with very few musicians
                cluster_analysis = {
                    'cluster_0': {
                        'musician_count': len(musician_profiles),
                        'musicians': musician_ids,
                        'characteristics': {
                            'avg_followers': np.mean(features_array[:, 0]) if len(features_array) > 0 else 0,
                            'avg_posting_frequency': np.mean(features_array[:, 1]) if len(features_array) > 0 else 0,
                            'avg_engagement_rate': np.mean(features_array[:, 2]) if len(features_array) > 0 else 0,
                            'avg_collaborations': np.mean(features_array[:, 3]) if len(features_array) > 0 else 0,
                        },
                        'profile': 'single_cluster'
                    }
                }
                cluster_labels = [0] * len(musician_profiles)
            else:
                self.clustering_model = KMeans(n_clusters=n_clusters, random_state=42)
                cluster_labels = self.clustering_model.fit_predict(features_array)
                
                # Analyze clusters
                cluster_analysis = {}
                for i in range(n_clusters):
                    cluster_mask = cluster_labels == i
                    cluster_musicians = [musician_ids[j] for j in range(len(musician_ids)) if cluster_mask[j]]
                    cluster_features = features_array[cluster_mask]
                    
                    cluster_analysis[f"cluster_{i}"] = {
                        'musician_count': len(cluster_musicians),
                        'musicians': cluster_musicians,
                        'characteristics': {
                            'avg_followers': np.mean(cluster_features[:, 0]) if len(cluster_features) > 0 else 0,
                            'avg_posting_frequency': np.mean(cluster_features[:, 1]) if len(cluster_features) > 0 else 0,
                            'avg_engagement_rate': np.mean(cluster_features[:, 2]) if len(cluster_features) > 0 else 0,
                            'avg_collaborations': np.mean(cluster_features[:, 3]) if len(cluster_features) > 0 else 0,
                        },
                        'profile': self._generate_cluster_profile(cluster_features)
                    }
            
            return {
                'clusters': cluster_analysis,
                'cluster_labels': cluster_labels.tolist(),
                'insights': await self._generate_clustering_insights(cluster_analysis)
            }
            
        except Exception as e:
            logger.error(f"Musician clustering failed: {e}")
            raise
    
    def _generate_cluster_profile(self, cluster_features: np.ndarray) -> str:
        """Generate descriptive profile for cluster"""
        if len(cluster_features) == 0:
            return "empty_cluster"
        
        avg_followers = np.mean(cluster_features[:, 0])
        avg_frequency = np.mean(cluster_features[:, 1])
        avg_engagement = np.mean(cluster_features[:, 2])
        
        if avg_followers > 10 and avg_engagement > 0.1:
            return "established_creators"
        elif avg_frequency > 3 and avg_engagement > 0.05:
            return "active_emerging"
        elif avg_followers < 5 and avg_frequency < 1:
            return "new_creators"
        elif avg_engagement > 0.15:
            return "high_engagement_niche"
        else:
            return "developing_creators"
    
    async def _generate_clustering_insights(
        self,
        cluster_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate insights from clustering analysis"""
        insights = []
        
        cluster_count = len(cluster_analysis)
        insights.append(f"Identified {cluster_count} distinct musician behavior clusters")
        
        # Find largest cluster
        largest_cluster = max(cluster_analysis.values(), key=lambda c: c['musician_count'])
        insights.append(f"Largest cluster: {largest_cluster['profile']} ({largest_cluster['musician_count']} musicians)")
        
        # Identify high-engagement cluster
        high_engagement_clusters = [
            c for c in cluster_analysis.values() 
            if c['characteristics']['avg_engagement_rate'] > 0.1
        ]
        
        if high_engagement_clusters:
            insights.append("High-engagement clusters identified - analyze for best practices")
        
        insights.append("Use cluster profiles for targeted content strategies")
        insights.append("Cross-cluster collaboration opportunities available")
        
        return insights

class MusicianBehaviorAnalyzer:
    """Main musician behavior analysis system"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        self.audio_extractor = AudioFeatureExtractor()
        self.engagement_predictor = EngagementPredictor()
        self.pattern_analyzer = BehaviorPatternAnalyzer()
        
        self.musicians: Dict[str, MusicianProfile] = {}
        self.content_database: List[MusicContent] = []
        self.analysis_history: List[Dict[str, Any]] = []
        
        logger.info("Musician Behavior Analyzer initialized")
    
    async def add_musician_profile(self, profile: MusicianProfile) -> bool:
        """Add or update musician profile"""
        try:
            self.musicians[profile.musician_id] = profile
            logger.info(f"Added musician profile: {profile.name} ({profile.musician_id})")
            return True
        except Exception as e:
            logger.error(f"Failed to add musician profile: {e}")
            return False
    
    async def add_music_content(
        self,
        content: MusicContent,
        audio_file_path: Optional[str] = None
    ) -> bool:
        """Add music content with optional audio analysis"""
        try:
            # Extract audio features if file provided
            if audio_file_path:
                audio_features = await self.audio_extractor.extract_features(audio_file_path)
                content.audio_features = {
                    'tempo': audio_features.tempo,
                    'danceability': audio_features.danceability,
                    'energy': audio_features.energy,
                    'valence': audio_features.valence,
                    'acousticness': audio_features.acousticness,
                    'speechiness': audio_features.speechiness,
                    'liveness': audio_features.liveness,
                    'loudness': audio_features.loudness,
                }
            
            self.content_database.append(content)
            logger.info(f"Added content: {content.title} by {content.musician_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add music content: {e}")
            return False
    
    async def analyze_musician_behavior(self, musician_id: str) -> Dict[str, Any]:
        """Comprehensive behavior analysis for a musician"""
        try:
            if musician_id not in self.musicians:
                raise ValueError(f"Musician {musician_id} not found")
            
            musician = self.musicians[musician_id]
            musician_content = [c for c in self.content_database if c.musician_id == musician_id]
            
            if not musician_content:
                return {"error": "No content found for musician"}
            
            # Content analysis
            content_analysis = await self._analyze_content_patterns(musician_content)
            
            # Engagement analysis
            engagement_analysis = await self._analyze_engagement_patterns(musician, musician_content)
            
            # Growth analysis
            growth_analysis = await self._analyze_growth_trends(musician, musician_content)
            
            # Recommendations
            recommendations = await self._generate_musician_recommendations(
                musician, musician_content, content_analysis, engagement_analysis
            )
            
            analysis_result = {
                'musician_profile': {
                    'musician_id': musician.musician_id,
                    'name': musician.name,
                    'primary_genre': musician.primary_genre.value,
                    'follower_count': musician.follower_count,
                    'content_count': len(musician_content)
                },
                'content_analysis': content_analysis,
                'engagement_analysis': engagement_analysis,
                'growth_analysis': growth_analysis,
                'recommendations': recommendations,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            self.analysis_history.append(analysis_result)
            return analysis_result
            
        except Exception as e:
            logger.error(f"Musician behavior analysis failed: {e}")
            raise
    
    async def _analyze_content_patterns(self, content: List[MusicContent]) -> Dict[str, Any]:
        """Analyze content creation patterns"""
        if not content:
            return {}
        
        # Genre distribution
        genres = [c.genre for c in content]
        genre_counts = {genre.value: genres.count(genre) for genre in set(genres)}
        
        # Content type distribution
        content_types = [c.content_type for c in content]
        type_counts = {ctype.value: content_types.count(ctype) for ctype in set(content_types)}
        
        # Duration analysis
        durations = [c.duration_seconds for c in content]
        avg_duration = np.mean(durations)
        
        # Upload frequency
        if len(content) > 1:
            sorted_content = sorted(content, key=lambda c: c.upload_date)
            intervals = [
                (sorted_content[i].upload_date - sorted_content[i-1].upload_date).days
                for i in range(1, len(sorted_content))
            ]
            avg_interval = np.mean(intervals) if intervals else 0
        else:
            avg_interval = 0
        
        return {
            'genre_distribution': genre_counts,
            'content_type_distribution': type_counts,
            'average_duration_seconds': avg_duration,
            'average_posting_interval_days': avg_interval,
            'total_content_count': len(content),
            'content_diversity_score': len(set(genres)) / len(genres) if genres else 0
        }
    
    async def _analyze_engagement_patterns(
        self,
        musician: MusicianProfile,
        content: List[MusicContent]
    ) -> Dict[str, Any]:
        """Analyze engagement patterns"""
        if not content:
            return {}
        
        # Calculate engagement metrics
        total_engagement = {}
        for metric in EngagementMetric:
            total_engagement[metric.value] = sum(
                c.engagement_metrics.get(metric, 0) for c in content
            )
        
        # Engagement per content
        avg_engagement = {
            metric.value: total_engagement[metric.value] / len(content)
            for metric in EngagementMetric
        }
        
        # Engagement trends over time
        sorted_content = sorted(content, key=lambda c: c.upload_date)
        if len(sorted_content) >= 3:
            recent_content = sorted_content[-3:]
            older_content = sorted_content[:-3] if len(sorted_content) > 3 else []
            
            if older_content:
                recent_avg = np.mean([sum(c.engagement_metrics.values()) for c in recent_content])
                older_avg = np.mean([sum(c.engagement_metrics.values()) for c in older_content])
                trend = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
            else:
                trend = 0
        else:
            trend = 0
        
        # Best performing content
        best_content = max(content, key=lambda c: sum(c.engagement_metrics.values()))
        
        return {
            'total_engagement': total_engagement,
            'average_engagement_per_content': avg_engagement,
            'engagement_trend': trend,
            'best_performing_content': {
                'title': best_content.title,
                'engagement_score': sum(best_content.engagement_metrics.values()),
                'content_type': best_content.content_type.value,
                'genre': best_content.genre.value
            }
        }
    
    async def _analyze_growth_trends(
        self,
        musician: MusicianProfile,
        content: List[MusicContent]
    ) -> Dict[str, Any]:
        """Analyze growth trends and projections"""
        if len(content) < 2:
            return {"insufficient_data": True}
        
        # Sort content by date
        sorted_content = sorted(content, key=lambda c: c.upload_date)
        
        # Calculate cumulative metrics over time
        cumulative_views = []
        cumulative_engagement = []
        dates = []
        
        running_views = 0
        running_engagement = 0
        
        for content_item in sorted_content:
            running_views += content_item.engagement_metrics.get(EngagementMetric.VIEWS, 0)
            running_engagement += sum(content_item.engagement_metrics.values())
            
            cumulative_views.append(running_views)
            cumulative_engagement.append(running_engagement)
            dates.append(content_item.upload_date)
        
        # Calculate growth rate
        if len(cumulative_engagement) >= 2:
            recent_growth = cumulative_engagement[-1] - cumulative_engagement[-2]
            earlier_growth = cumulative_engagement[-2] - cumulative_engagement[0] if len(cumulative_engagement) > 2 else cumulative_engagement[-2]
            growth_acceleration = recent_growth - earlier_growth
        else:
            growth_acceleration = 0
        
        # Project future growth (simple linear projection)
        if len(cumulative_engagement) >= 3:
            growth_rate = (cumulative_engagement[-1] - cumulative_engagement[0]) / len(cumulative_engagement)
            projected_30_days = cumulative_engagement[-1] + (growth_rate * 4)  # ~4 weeks
        else:
            projected_30_days = cumulative_engagement[-1] if cumulative_engagement else 0
        
        return {
            'cumulative_views': cumulative_views,
            'cumulative_engagement': cumulative_engagement,
            'growth_acceleration': growth_acceleration,
            'projected_30_day_engagement': projected_30_days,
            'content_timeline': [d.isoformat() for d in dates]
        }
    
    async def _generate_musician_recommendations(
        self,
        musician: MusicianProfile,
        content: List[MusicContent],
        content_analysis: Dict[str, Any],
        engagement_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Content frequency recommendations
        if content_analysis.get('average_posting_interval_days', 0) > 14:
            recommendations.append("Increase posting frequency - aim for weekly releases")
        
        # Content diversity recommendations
        diversity_score = content_analysis.get('content_diversity_score', 0)
        if diversity_score < 0.3:
            recommendations.append("Experiment with different genres to expand audience")
        
        # Duration recommendations
        avg_duration = content_analysis.get('average_duration_seconds', 0)
        if avg_duration > 300:  # 5 minutes
            recommendations.append("Consider shorter content for better engagement")
        elif avg_duration < 120:  # 2 minutes
            recommendations.append("Slightly longer content might improve depth")
        
        # Engagement trends
        trend = engagement_analysis.get('engagement_trend', 0)
        if trend < -0.1:
            recommendations.append("Engagement declining - analyze successful past content")
        elif trend > 0.1:
            recommendations.append("Growing engagement - maintain current strategy")
        
        # Best content analysis
        best_content = engagement_analysis.get('best_performing_content', {})
        if best_content:
            best_type = best_content.get('content_type')
            recommendations.append(f"Create more {best_type} content - it performs well")
        
        # Collaboration recommendations
        if len(musician.collaboration_network) < 3:
            recommendations.append("Build collaboration network for cross-promotion")
        
        recommendations.append("Analyze optimal posting times for your audience")
        recommendations.append("Engage with your audience through comments and interactions")
        
        return recommendations
    
    async def generate_behavior_report(self) -> Dict[str, Any]:
        """Generate comprehensive behavior analysis report"""
        try:
            if not self.musicians or not self.content_database:
                return {"error": "Insufficient data for report generation"}
            
            # Platform-wide statistics
            total_musicians = len(self.musicians)
            total_content = len(self.content_database)
            
            # Genre distribution across platform
            all_genres = [c.genre for c in self.content_database]
            genre_popularity = {
                genre.value: all_genres.count(genre) 
                for genre in set(all_genres)
            }
            
            # Engagement statistics
            all_engagement = [sum(c.engagement_metrics.values()) for c in self.content_database]
            avg_platform_engagement = np.mean(all_engagement) if all_engagement else 0
            
            # Top performers
            top_content = sorted(
                self.content_database,
                key=lambda c: sum(c.engagement_metrics.values()),
                reverse=True
            )[:5]
            
            # Musician clustering
            musician_list = list(self.musicians.values())
            clustering_results = await self.pattern_analyzer.cluster_musician_behavior(musician_list)
            
            # Posting patterns
            posting_patterns = await self.pattern_analyzer.analyze_posting_patterns(
                musician_list, self.content_database
            )
            
            report = {
                'platform_overview': {
                    'total_musicians': total_musicians,
                    'total_content': total_content,
                    'average_engagement': avg_platform_engagement,
                    'genre_popularity': genre_popularity
                },
                'top_performing_content': [
                    {
                        'title': c.title,
                        'musician_id': c.musician_id,
                        'genre': c.genre.value,
                        'engagement_score': sum(c.engagement_metrics.values())
                    }
                    for c in top_content
                ],
                'musician_clusters': clustering_results,
                'posting_patterns': posting_patterns,
                'platform_insights': [
                    f"Most popular genre: {max(genre_popularity, key=genre_popularity.get)}",
                    f"Average content per musician: {total_content / total_musicians:.1f}",
                    f"Platform engagement rate: {avg_platform_engagement:.2f}",
                ],
                'generated_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Generated behavior report: {total_musicians} musicians, {total_content} content items")
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise

# Example usage and testing
async def main() -> None:
    """Test musician behavior analyzer"""
    try:
        # Initialize analyzer
        analyzer = MusicianBehaviorAnalyzer()
        
        # Create test musician profiles
        musicians = [
            MusicianProfile(
                musician_id="musician_001",
                name="Alex Electronic",
                primary_genre=MusicGenre.ELECTRONIC,
                follower_count=5000,
                posting_frequency=2.5
            ),
            MusicianProfile(
                musician_id="musician_002",
                name="Sarah Acoustic",
                primary_genre=MusicGenre.FOLK,
                follower_count=1200,
                posting_frequency=1.8
            )
        ]
        
        # Add musicians
        for musician in musicians:
            await analyzer.add_musician_profile(musician)
        
        # Create test content
        test_content = [
            MusicContent(
                content_id="content_001",
                musician_id="musician_001",
                title="Midnight Synthwave",
                genre=MusicGenre.ELECTRONIC,
                content_type=ContentType.ORIGINAL_SONG,
                duration_seconds=240,
                upload_date=datetime.utcnow() - timedelta(days=7),
                engagement_metrics={
                    EngagementMetric.VIEWS: 1500,
                    EngagementMetric.LIKES: 120,
                    EngagementMetric.SHARES: 25
                }
            ),
            MusicContent(
                content_id="content_002",
                musician_id="musician_002",
                title="Campfire Sessions",
                genre=MusicGenre.FOLK,
                content_type=ContentType.LIVE_PERFORMANCE,
                duration_seconds=180,
                upload_date=datetime.utcnow() - timedelta(days=3),
                engagement_metrics={
                    EngagementMetric.VIEWS: 800,
                    EngagementMetric.LIKES: 85,
                    EngagementMetric.COMMENTS: 15
                }
            )
        ]
        
        # Add content
        for content in test_content:
            await analyzer.add_music_content(content)
        
        # Analyze individual musician
        musician_analysis = await analyzer.analyze_musician_behavior("musician_001")
        print(f"Musician analysis completed: {len(musician_analysis)} sections")
        print(f"Content count: {musician_analysis['musician_profile']['content_count']}")
        
        # Generate platform report
        platform_report = await analyzer.generate_behavior_report()
        print(f"Platform report: {platform_report['platform_overview']['total_musicians']} musicians")
        print(f"Top genre: {max(platform_report['platform_overview']['genre_popularity'], key=platform_report['platform_overview']['genre_popularity'].get)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Musician behavior analyzer test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(main())