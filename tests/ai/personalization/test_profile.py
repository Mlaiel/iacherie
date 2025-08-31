# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""User Profile Management Tests

Comprehensive tests for user profile creation, management, and personalization.
Tests profile building, preference learning, demographic analysis, and behavioral modeling.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest import IsolatedAsyncioTestCase
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import time
import os
import sys
from collections import defaultdict
import json

# Import the profile modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from ai.personalization.profile import (
    UserProfileAnalyzer,
    BehaviorAnalyzer,
    PreferenceExtractor,
    ContentInteractionTracker,
    BehaviorPattern,
    PersonalityTrait,
    BehaviorAnalysis,
    DemographicProfile,
    PsychographicProfile
)
from ai.personalization.exceptions import (
    ProfileNotFoundError,
    PersonalizationError,
    ValidationError
)


class TestUserProfile(IsolatedAsyncioTestCase):
    """Comprehensive tests for UserProfile class"""
    async def asyncSetUp(self):
        """Set up test environment"""        self.user_id = 'user_12345'
        self.profile_data = self._generate_profile_data()
        self.profile = UserProfile(
            user_id=self.user_id,
            profile_data=self.profile_data,
            privacy_level=PrivacyLevel.MEDIUM
        )

    def _generate_profile_data(self) -> Dict[str, Any]:
        """Generate comprehensive profile data"""        return {
            'demographics': {
                'age': 28,
                'gender': 'F',
                'location': 'Berlin, Germany',
                'language': 'de',
                'timezone': 'Europe/Berlin',
                'occupation': 'Software Engineer',
                'education': 'Masters',
                'income_bracket': 'middle'
            },
            'preferences': {
                'music_genres': {
                    'electronic': 0.8,
                    'indie': 0.6,
                    'pop': 0.4,
                    'classical': 0.2
                },
                'content_types': {
                    'music': 0.9,
                    'podcasts': 0.7,
                    'audiobooks': 0.3
                },
                'audio_features': {
                    'energy': 0.7,
                    'valence': 0.6,
                    'danceability': 0.8,
                    'acousticness': 0.3,
                    'instrumentalness': 0.2
                }
            },
            'behavior': {
                'listening_patterns': {
                    'daily_hours': 4.5,
                    'peak_hours': [18, 19, 20, 21],
                    'weekend_vs_weekday': 1.3,
                    'session_length': 45.5
                },
                'interaction_patterns': {
                    'skip_rate': 0.15,
                    'repeat_rate': 0.25,
                    'like_rate': 0.08,
                    'share_rate': 0.02,
                    'playlist_creation_rate': 0.1
                },
                'device_usage': {
                    'mobile': 0.7,
                    'desktop': 0.2,
                    'smart_speaker': 0.1
                }
            },
            'context': {
                'current_mood': 'energetic',
                'activity': 'working',
                'location_type': 'home',
                'social_context': 'alone'
            },
            'history': {
                'total_listening_time': 15678,  # minutes
                'favorite_artists': ['Artist_A', 'Artist_B', 'Artist_C'],
                'recently_played': ['track_1', 'track_2', 'track_3'],
                'created_playlists': ['playlist_1', 'playlist_2']
            }
        }

    async def test_profile_initialization(self):
        """Test profile proper initialization"""        self.assertEqual(self.profile.user_id, self.user_id)
        self.assertEqual(self.profile.privacy_level, PrivacyLevel.MEDIUM)
        self.assertIsNotNone(self.profile.created_at)
        self.assertIsNotNone(self.profile.updated_at)
        self.assertTrue(self.profile.is_valid)

    async def test_profile_data_access(self):
        """Test profile data access methods"""        # Test demographics access
        age = self.profile.get_demographic('age')
        self.assertEqual(age, 28)
        
        gender = self.profile.get_demographic('gender')
        self.assertEqual(gender, 'F')
        
        # Test preferences access
        music_prefs = self.profile.get_preferences('music_genres')
        self.assertIn('electronic', music_prefs)
        self.assertEqual(music_prefs['electronic'], 0.8)
        
        # Test behavior access
        skip_rate = self.profile.get_behavior('interaction_patterns.skip_rate')
        self.assertEqual(skip_rate, 0.15)

    async def test_profile_updates(self):
        """Test profile data updates"""        # Update demographic
        await self.profile.update_demographic('age', 29)
        self.assertEqual(self.profile.get_demographic('age'), 29)
        
        # Update preference
        await self.profile.update_preference('music_genres.jazz', 0.5)
        self.assertEqual(self.profile.get_preferences('music_genres')['jazz'], 0.5)
        
        # Update behavior
        await self.profile.update_behavior('interaction_patterns.skip_rate', 0.12)
        self.assertEqual(self.profile.get_behavior('interaction_patterns.skip_rate'), 0.12)

    async def test_profile_privacy_filtering(self):
        """Test privacy-aware data filtering"""        # Set high privacy level
        self.profile.privacy_level = PrivacyLevel.HIGH
        
        # Request sensitive data
        filtered_data = await self.profile.get_privacy_filtered_data()
        
        # Sensitive demographic data should be filtered/anonymized
        self.assertNotIn('location', filtered_data.get('demographics', {}))
        self.assertNotIn('income_bracket', filtered_data.get('demographics', {}))

    async def test_profile_serialization(self):
        """Test profile serialization and deserialization"""        # Serialize profile
        serialized = await self.profile.to_dict()
        
        self.assertIsInstance(serialized, dict)
        self.assertIn('user_id', serialized)
        self.assertIn('profile_data', serialized)
        self.assertIn('privacy_level', serialized)
        self.assertIn('created_at', serialized)
        
        # Deserialize profile
        new_profile = UserProfile.from_dict(serialized)
        
        self.assertEqual(new_profile.user_id, self.profile.user_id)
        self.assertEqual(new_profile.privacy_level, self.profile.privacy_level)

    async def test_profile_similarity(self):
        """Test profile similarity computation"""        # Create similar profile
        similar_profile_data = self.profile_data.copy()
        similar_profile_data['preferences']['music_genres']['electronic'] = 0.75
        
        similar_profile = UserProfile(
            user_id='user_similar',
            profile_data=similar_profile_data
        )
        
        # Compute similarity
        similarity = await self.profile.compute_similarity(similar_profile)
        
        self.assertIsInstance(similarity, (int, float))
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
        self.assertGreater(similarity, 0.8)  # Should be highly similar

    async def test_profile_validation(self):
        """Test profile data validation"""        # Test valid profile
        is_valid = await self.profile.validate()
        self.assertTrue(is_valid)
        
        # Test invalid profile
        invalid_data = self.profile_data.copy()
        invalid_data['demographics']['age'] = -5  # Invalid age
        
        invalid_profile = UserProfile(
            user_id='user_invalid',
            profile_data=invalid_data
        )
        
        is_valid = await invalid_profile.validate()
        self.assertFalse(is_valid)

    async def test_profile_metrics(self):
        """Test profile metrics computation"""        metrics = await self.profile.compute_metrics()
        
        self.assertIsInstance(metrics, ProfileMetrics)
        self.assertIn('completeness_score', metrics.__dict__)
        self.assertIn('diversity_score', metrics.__dict__)
        self.assertIn('consistency_score', metrics.__dict__)
        
        # Scores should be between 0 and 1
        self.assertGreaterEqual(metrics.completeness_score, 0.0)
        self.assertLessEqual(metrics.completeness_score, 1.0)


class TestUserProfileManager(IsolatedAsyncioTestCase):
    """Comprehensive tests for UserProfileManager"""
    async def asyncSetUp(self):
        """Set up test environment"""        self.manager = UserProfileManager(
            storage_backend='memory',  # Use in-memory storage for tests
            cache_size=100,
            auto_backup=False
        )
        self.test_users = self._generate_test_users(20)

    def _generate_test_users(self, n_users: int) -> List[Dict[str, Any]]:
        """Generate test user data"""        users = []
        for i in range(n_users):
            user_data = {
                'user_id': f'user_{i}',
                'demographics': {
                    'age': np.random.randint(18, 65),
                    'gender': np.random.choice(['M', 'F', 'O']),
                    'location': np.random.choice(['Berlin', 'Munich', 'Hamburg', 'Frankfurt']),
                    'language': np.random.choice(['de', 'en', 'fr'])
                },
                'preferences': {
                    'music_genres': {
                        'pop': np.random.uniform(0.0, 1.0),
                        'rock': np.random.uniform(0.0, 1.0),
                        'electronic': np.random.uniform(0.0, 1.0),
                        'classical': np.random.uniform(0.0, 1.0)
                    }
                },
                'behavior': {
                    'listening_patterns': {
                        'daily_hours': np.random.uniform(1.0, 8.0),
                        'session_length': np.random.uniform(15.0, 120.0)
                    }
                }
            }
            users.append(user_data)
        return users

    async def test_profile_creation(self):
        """Test profile creation and storage"""        user_data = self.test_users[0]
        
        profile = await self.manager.create_profile(
            user_id=user_data['user_id'],
            profile_data=user_data
        )
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user_id, user_data['user_id'])
        self.assertTrue(profile.is_valid)

    async def test_profile_retrieval(self):
        """Test profile retrieval"""        # Create profile
        user_data = self.test_users[0]
        created_profile = await self.manager.create_profile(
            user_id=user_data['user_id'],
            profile_data=user_data
        )
        
        # Retrieve profile
        retrieved_profile = await self.manager.get_profile(user_data['user_id'])
        
        self.assertIsNotNone(retrieved_profile)
        self.assertEqual(retrieved_profile.user_id, created_profile.user_id)

    async def test_profile_not_found(self):
        """Test handling of non-existent profiles"""        with self.assertRaises(ProfileNotFoundError):
            await self.manager.get_profile('non_existent_user')

    async def test_batch_profile_operations(self):
        """Test batch profile operations"""        # Create multiple profiles
        created_profiles = await self.manager.create_profiles_batch(self.test_users)
        
        self.assertEqual(len(created_profiles), len(self.test_users))
        
        # Retrieve multiple profiles
        user_ids = [user['user_id'] for user in self.test_users]
        retrieved_profiles = await self.manager.get_profiles_batch(user_ids)
        
        self.assertEqual(len(retrieved_profiles), len(self.test_users))

    async def test_profile_updates(self):
        """Test profile update functionality"""        user_data = self.test_users[0]
        profile = await self.manager.create_profile(
            user_id=user_data['user_id'],
            profile_data=user_data
        )
        
        # Update profile
        updates = {
            'demographics': {'age': 30},
            'preferences': {'music_genres': {'jazz': 0.8}}
        }
        
        updated_profile = await self.manager.update_profile(
            user_id=user_data['user_id'],
            updates=updates
        )
        
        self.assertEqual(updated_profile.get_demographic('age'), 30)
        self.assertEqual(updated_profile.get_preferences('music_genres')['jazz'], 0.8)

    async def test_profile_deletion(self):
        """Test profile deletion"""        user_data = self.test_users[0]
        await self.manager.create_profile(
            user_id=user_data['user_id'],
            profile_data=user_data
        )
        
        # Delete profile
        success = await self.manager.delete_profile(user_data['user_id'])
        self.assertTrue(success)
        
        # Verify deletion
        with self.assertRaises(ProfileNotFoundError):
            await self.manager.get_profile(user_data['user_id'])

    async def test_profile_search(self):
        """Test profile search functionality"""        # Create profiles
        await self.manager.create_profiles_batch(self.test_users)
        
        # Search by demographics
        berlin_users = await self.manager.search_profiles({
            'demographics.location': 'Berlin'
        })
        
        self.assertIsInstance(berlin_users, list)
        for profile in berlin_users:
            self.assertEqual(profile.get_demographic('location'), 'Berlin')

    async def test_profile_clustering(self):
        """Test user profile clustering"""        # Create profiles
        await self.manager.create_profiles_batch(self.test_users)
        
        # Perform clustering
        clusters = await self.manager.cluster_profiles(
            n_clusters=3,
            features=['demographics.age', 'preferences.music_genres']
        )
        
        self.assertIsInstance(clusters, dict)
        self.assertEqual(len(clusters), 3)
        
        # Check that all users are assigned to clusters
        total_users = sum(len(cluster_users) for cluster_users in clusters.values())
        self.assertEqual(total_users, len(self.test_users))

    async def test_profile_statistics(self):
        """Test profile statistics computation"""        # Create profiles
        await self.manager.create_profiles_batch(self.test_users)
        
        stats = await self.manager.compute_profile_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_profiles', stats)
        self.assertIn('demographic_distribution', stats)
        self.assertIn('preference_trends', stats)
        self.assertIn('behavior_patterns', stats)


class TestProfileBuilder(IsolatedAsyncioTestCase):
    """Comprehensive tests for ProfileBuilder"""
    async def asyncSetUp(self):
        """Set up test environment"""        self.builder = ProfileBuilder(
            confidence_threshold=0.7,
            min_interactions=10,
            feature_extractors=['demographic', 'behavioral', 'contextual']
        )
        self.interaction_data = self._generate_interaction_data()

    def _generate_interaction_data(self) -> List[Dict[str, Any]]:
        """Generate interaction data for profile building"""        interactions = []
        user_id = 'user_builder_test'
        
        for i in range(100):
            interaction = {
                'user_id': user_id,
                'item_id': f'track_{i % 30}',
                'item_type': 'music',
                'action': np.random.choice(['play', 'skip', 'like', 'share']),
                'duration': np.random.randint(30, 300),
                'rating': np.random.uniform(1.0, 5.0) if np.random.random() < 0.3 else None,
                'timestamp': datetime.utcnow() - timedelta(days=np.random.randint(0, 30)),
                'context': {
                    'device': np.random.choice(['mobile', 'desktop', 'smart_speaker']),
                    'location': np.random.choice(['home', 'work', 'commute']),
                    'time_of_day': np.random.randint(0, 24),
                    'day_of_week': np.random.randint(0, 7)
                },
                'item_features': {
                    'genre': np.random.choice(['pop', 'rock', 'electronic', 'classical']),
                    'energy': np.random.uniform(0.0, 1.0),
                    'valence': np.random.uniform(0.0, 1.0),
                    'danceability': np.random.uniform(0.0, 1.0)
                }
            }
            interactions.append(interaction)
        
        return interactions

    async def test_profile_building_from_interactions(self):
        """Test building profile from interaction data"""        profile = await self.builder.build_from_interactions(self.interaction_data)
        
        self.assertIsNotNone(profile)
        self.assertIsInstance(profile, UserProfile)
        self.assertEqual(profile.user_id, 'user_builder_test')

    async def test_preference_extraction(self):
        """Test preference extraction from interactions"""        preferences = await self.builder.extract_preferences(self.interaction_data)
        
        self.assertIsInstance(preferences, dict)
        self.assertIn('music_genres', preferences)
        self.assertIn('audio_features', preferences)
        
        # Check that preferences are normalized
        genre_prefs = preferences['music_genres']
        for genre, weight in genre_prefs.items():
            self.assertGreaterEqual(weight, 0.0)
            self.assertLessEqual(weight, 1.0)

    async def test_behavioral_pattern_extraction(self):
        """Test behavioral pattern extraction"""        patterns = await self.builder.extract_behavioral_patterns(self.interaction_data)
        
        self.assertIsInstance(patterns, dict)
        self.assertIn('listening_patterns', patterns)
        self.assertIn('interaction_patterns', patterns)
        self.assertIn('device_usage', patterns)

    async def test_temporal_pattern_analysis(self):
        """Test temporal pattern analysis"""        temporal_patterns = await self.builder.analyze_temporal_patterns(self.interaction_data)
        
        self.assertIsInstance(temporal_patterns, dict)
        self.assertIn('hourly_distribution', temporal_patterns)
        self.assertIn('daily_distribution', temporal_patterns)
        self.assertIn('peak_hours', temporal_patterns)

    async def test_contextual_feature_extraction(self):
        """Test contextual feature extraction"""        contextual_features = await self.builder.extract_contextual_features(self.interaction_data)
        
        self.assertIsInstance(contextual_features, dict)
        self.assertIn('location_preferences', contextual_features)
        self.assertIn('device_preferences', contextual_features)
        self.assertIn('temporal_preferences', contextual_features)

    async def test_incremental_profile_building(self):
        """Test incremental profile building"""        # Build initial profile from first half of interactions
        initial_interactions = self.interaction_data[:50]
        initial_profile = await self.builder.build_from_interactions(initial_interactions)
        
        # Update profile with remaining interactions
        remaining_interactions = self.interaction_data[50:]
        updated_profile = await self.builder.update_profile_incrementally(
            initial_profile,
            remaining_interactions
        )
        
        self.assertIsNotNone(updated_profile)
        self.assertEqual(updated_profile.user_id, initial_profile.user_id)
        
        # Updated profile should have different data
        initial_prefs = initial_profile.get_preferences('music_genres')
        updated_prefs = updated_profile.get_preferences('music_genres')
        
        # At least some preferences should have changed
        self.assertNotEqual(initial_prefs, updated_prefs)

    async def test_confidence_scoring(self):
        """Test confidence scoring for profile elements"""        profile = await self.builder.build_from_interactions(self.interaction_data)
        
        confidence_scores = await self.builder.compute_confidence_scores(
            profile,
            self.interaction_data
        )
        
        self.assertIsInstance(confidence_scores, dict)
        self.assertIn('preferences', confidence_scores)
        self.assertIn('behavioral_patterns', confidence_scores)
        
        # All confidence scores should be between 0 and 1
        for category, scores in confidence_scores.items():
            for feature, score in scores.items():
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)


class TestPreferenceAnalyzer(IsolatedAsyncioTestCase):
    """Comprehensive tests for PreferenceAnalyzer"""
    async def asyncSetUp(self):
        """Set up test environment"""        self.analyzer = PreferenceAnalyzer(
            weight_decay=0.95,
            novelty_factor=0.1,
            diversity_bonus=0.05
        )
        self.preference_data = self._generate_preference_data()

    def _generate_preference_data(self) -> List[Dict[str, Any]]:
        """Generate preference data for analysis"""        data = []
        user_id = 'user_preference_test'
        
        # Simulate evolving preferences over time
        base_preferences = {
            'electronic': 0.8,
            'pop': 0.6,
            'rock': 0.4,
            'classical': 0.2
        }
        
        for day in range(30):
            for interaction in range(5):
                # Add some noise and evolution to preferences
                current_prefs = {}
                for genre, base_pref in base_preferences.items():
                    evolution = np.sin(day * 0.1) * 0.1  # Slow evolution
                    noise = np.random.normal(0, 0.05)
                    current_prefs[genre] = np.clip(base_pref + evolution + noise, 0.0, 1.0)
                
                data.append({
                    'user_id': user_id,
                    'timestamp': datetime.utcnow() - timedelta(days=29-day),
                    'preferences': current_prefs,
                    'interaction_type': np.random.choice(['implicit', 'explicit']),
                    'confidence': np.random.uniform(0.7, 1.0)
                })
        
        return data

    async def test_preference_evolution_tracking(self):
        """Test tracking of preference evolution over time"""        evolution = await self.analyzer.track_preference_evolution(self.preference_data)
        
        self.assertIsInstance(evolution, dict)
        self.assertIn('timeline', evolution)
        self.assertIn('trends', evolution)
        self.assertIn('volatility', evolution)

    async def test_preference_stability_analysis(self):
        """Test preference stability analysis"""        stability = await self.analyzer.analyze_preference_stability(self.preference_data)
        
        self.assertIsInstance(stability, dict)
        
        for genre, stability_score in stability.items():
            self.assertIsInstance(stability_score, (int, float))
            self.assertGreaterEqual(stability_score, 0.0)
            self.assertLessEqual(stability_score, 1.0)

    async def test_preference_clustering(self):
        """Test preference clustering"""        clusters = await self.analyzer.cluster_preferences(
            self.preference_data,
            n_clusters=3
        )
        
        self.assertIsInstance(clusters, dict)
        self.assertIn('cluster_assignments', clusters)
        self.assertIn('cluster_centers', clusters)
        self.assertIn('cluster_descriptions', clusters)

    async def test_preference_anomaly_detection(self):
        """Test preference anomaly detection"""        # Add some anomalous preferences
        anomalous_data = self.preference_data.copy()
        anomalous_data.append({
            'user_id': 'user_preference_test',
            'timestamp': datetime.utcnow(),
            'preferences': {'death_metal': 1.0, 'noise': 0.9},  # Very different
            'interaction_type': 'explicit',
            'confidence': 0.8
        })
        
        anomalies = await self.analyzer.detect_preference_anomalies(anomalous_data)
        
        self.assertIsInstance(anomalies, list)
        self.assertGreater(len(anomalies), 0)  # Should detect the anomaly

    async def test_preference_prediction(self):
        """Test preference prediction"""        # Use historical data to predict future preferences
        historical_data = self.preference_data[:-5]  # All but last 5
        
        predicted_prefs = await self.analyzer.predict_future_preferences(
            historical_data,
            prediction_horizon=7  # 7 days
        )
        
        self.assertIsInstance(predicted_prefs, dict)
        
        for genre, predicted_value in predicted_prefs.items():
            self.assertIsInstance(predicted_value, (int, float))
            self.assertGreaterEqual(predicted_value, 0.0)
            self.assertLessEqual(predicted_value, 1.0)

    async def test_preference_diversity_analysis(self):
        """Test preference diversity analysis"""        diversity = await self.analyzer.analyze_preference_diversity(self.preference_data)
        
        self.assertIsInstance(diversity, dict)
        self.assertIn('shannon_entropy', diversity)
        self.assertIn('gini_coefficient', diversity)
        self.assertIn('effective_preferences', diversity)

    async def test_preference_weight_computation(self):
        """Test preference weight computation"""        weights = await self.analyzer.compute_preference_weights(
            self.preference_data,
            method='frequency_inverse'
        )
        
        self.assertIsInstance(weights, dict)
        
        # Weights should sum to approximately 1
        total_weight = sum(weights.values())
        self.assertAlmostEqual(total_weight, 1.0, places=2)


class TestBehavioralAnalyzer(IsolatedAsyncioTestCase):
    """Comprehensive tests for BehavioralAnalyzer"""
    async def asyncSetUp(self):
        """Set up test environment"""        self.analyzer = BehavioralAnalyzer(
            session_timeout=30,  # minutes
            behavior_types=['listening', 'interaction', 'navigation'],
            pattern_detection_window=14  # days
        )
        self.behavioral_data = self._generate_behavioral_data()

    def _generate_behavioral_data(self) -> List[Dict[str, Any]]:
        """Generate behavioral data for analysis"""        data = []
        user_id = 'user_behavior_test'
        
        # Simulate 30 days of behavior
        for day in range(30):
            # Weekday vs weekend behavior
            is_weekend = day % 7 in [5, 6]
            
            if is_weekend:
                n_sessions = np.random.poisson(3)  # Fewer sessions on weekends
                session_lengths = np.random.normal(90, 20, n_sessions)  # Longer sessions
            else:
                n_sessions = np.random.poisson(5)  # More sessions on weekdays
                session_lengths = np.random.normal(45, 15, n_sessions)  # Shorter sessions
            
            for session in range(max(1, n_sessions)):
                session_start = datetime.utcnow() - timedelta(days=29-day) + timedelta(
                    hours=np.random.randint(6, 23),
                    minutes=np.random.randint(0, 60)
                )
                
                session_length = max(5, session_lengths[session % len(session_lengths)])
                
                # Generate interactions within session
                n_interactions = max(1, int(session_length / 3))  # ~1 interaction per 3 minutes
                
                for interaction in range(n_interactions):
                    interaction_time = session_start + timedelta(
                        minutes=interaction * (session_length / n_interactions)
                    )
                    
                    data.append({
                        'user_id': user_id,
                        'timestamp': interaction_time,
                        'session_id': f'session_{day}_{session}',
                        'action': np.random.choice(['play', 'skip', 'pause', 'seek', 'like']),
                        'item_id': f'track_{np.random.randint(0, 100)}',
                        'duration': np.random.randint(30, 300),
                        'device': np.random.choice(['mobile', 'desktop', 'smart_speaker']),
                        'location': np.random.choice(['home', 'work', 'commute']),
                        'context': {
                            'is_weekend': is_weekend,
                            'hour_of_day': interaction_time.hour,
                            'session_position': interaction / n_interactions
                        }
                    })
        
        return data

    async def test_session_analysis(self):
        """Test session analysis"""        sessions = await self.analyzer.analyze_sessions(self.behavioral_data)
        
        self.assertIsInstance(sessions, dict)
        self.assertIn('session_statistics', sessions)
        self.assertIn('session_patterns', sessions)
        
        stats = sessions['session_statistics']
        self.assertIn('avg_session_length', stats)
        self.assertIn('avg_sessions_per_day', stats)
        self.assertIn('total_sessions', stats)

    async def test_temporal_behavior_patterns(self):
        """Test temporal behavior pattern analysis"""        patterns = await self.analyzer.analyze_temporal_patterns(self.behavioral_data)
        
        self.assertIsInstance(patterns, dict)
        self.assertIn('hourly_activity', patterns)
        self.assertIn('daily_activity', patterns)
        self.assertIn('weekend_vs_weekday', patterns)

    async def test_interaction_pattern_analysis(self):
        """Test interaction pattern analysis"""        interaction_patterns = await self.analyzer.analyze_interaction_patterns(
            self.behavioral_data
        )
        
        self.assertIsInstance(interaction_patterns, dict)
        self.assertIn('action_frequencies', interaction_patterns)
        self.assertIn('sequence_patterns', interaction_patterns)
        self.assertIn('transition_probabilities', interaction_patterns)

    async def test_device_usage_analysis(self):
        """Test device usage pattern analysis"""        device_patterns = await self.analyzer.analyze_device_usage(self.behavioral_data)
        
        self.assertIsInstance(device_patterns, dict)
        self.assertIn('device_distribution', device_patterns)
        self.assertIn('device_temporal_patterns', device_patterns)
        
        # Device distribution should sum to approximately 1
        device_dist = device_patterns['device_distribution']
        total_usage = sum(device_dist.values())
        self.assertAlmostEqual(total_usage, 1.0, places=2)

    async def test_behavior_change_detection(self):
        """Test behavior change point detection"""        # Introduce a behavior change in the middle of the data
        modified_data = self.behavioral_data.copy()
        
        # Change behavior for last 10 days (simulate change in listening habits)
        cutoff_date = datetime.utcnow() - timedelta(days=10)
        
        for interaction in modified_data:
            if interaction['timestamp'] > cutoff_date:
                # Simulate change: more skipping, different devices
                if interaction['action'] == 'play':
                    interaction['action'] = 'skip' if np.random.random() < 0.3 else 'play'
                interaction['device'] = 'smart_speaker'  # Switch to smart speaker
        
        change_points = await self.analyzer.detect_behavior_changes(modified_data)
        
        self.assertIsInstance(change_points, list)
        # Should detect at least one change point
        self.assertGreater(len(change_points), 0)

    async def test_behavior_segmentation(self):
        """Test behavior-based user segmentation"""        segments = await self.analyzer.segment_behavior(
            self.behavioral_data,
            segmentation_features=['session_frequency', 'interaction_diversity', 'temporal_consistency']
        )
        
        self.assertIsInstance(segments, dict)
        self.assertIn('segment_id', segments)
        self.assertIn('segment_characteristics', segments)
        self.assertIn('confidence', segments)

    async def test_behavior_prediction(self):
        """Test behavior prediction"""        # Use historical data to predict future behavior
        historical_data = self.behavioral_data[:-20]  # All but last 20 interactions
        
        predicted_behavior = await self.analyzer.predict_future_behavior(
            historical_data,
            prediction_window=7  # 7 days
        )
        
        self.assertIsInstance(predicted_behavior, dict)
        self.assertIn('predicted_actions', predicted_behavior)
        self.assertIn('predicted_session_patterns', predicted_behavior)
        self.assertIn('confidence_intervals', predicted_behavior)

    async def test_behavior_anomaly_detection(self):
        """Test behavioral anomaly detection"""        # Add some anomalous behavior
        anomalous_data = self.behavioral_data.copy()
        
        # Add unusual behavior: playing same track 100 times in a row
        anomaly_start = datetime.utcnow()
        for i in range(100):
            anomalous_data.append({
                'user_id': 'user_behavior_test',
                'timestamp': anomaly_start + timedelta(minutes=i*3),
                'session_id': 'anomalous_session',
                'action': 'play',
                'item_id': 'same_track_id',
                'duration': 180,
                'device': 'mobile',
                'location': 'home',
                'context': {}
            })
        
        anomalies = await self.analyzer.detect_behavioral_anomalies(anomalous_data)
        
        self.assertIsInstance(anomalies, list)
        self.assertGreater(len(anomalies), 0)  # Should detect anomalies


class TestDemographicAnalyzer(IsolatedAsyncioTestCase):
    """Comprehensive tests for DemographicAnalyzer"""
    async def asyncSetUp(self):
        """Set up test environment"""        self.analyzer = DemographicAnalyzer(
            privacy_level=PrivacyLevel.MEDIUM,
            anonymization_threshold=5
        )
        self.demographic_data = self._generate_demographic_data()

    def _generate_demographic_data(self) -> List[Dict[str, Any]]:
        """Generate demographic data for analysis"""        data = []
        
        for i in range(200):
            data.append({
                'user_id': f'user_{i}',
                'age': np.random.randint(18, 65),
                'gender': np.random.choice(['M', 'F', 'O']),
                'location': np.random.choice(['Berlin', 'Munich', 'Hamburg', 'Frankfurt', 'Cologne']),
                'language': np.random.choice(['de', 'en', 'fr']),
                'education': np.random.choice(['High School', 'Bachelor', 'Masters', 'PhD']),
                'occupation': np.random.choice(['Student', 'Engineer', 'Teacher', 'Artist', 'Manager']),
                'income_bracket': np.random.choice(['low', 'middle', 'high']),
                'family_status': np.random.choice(['single', 'married', 'divorced']),
                'registration_date': datetime.utcnow() - timedelta(days=np.random.randint(0, 365))
            })
        
        return data

    async def test_demographic_distribution_analysis(self):
        """Test demographic distribution analysis"""        distribution = await self.analyzer.analyze_demographic_distribution(
            self.demographic_data
        )
        
        self.assertIsInstance(distribution, dict)
        self.assertIn('age_distribution', distribution)
        self.assertIn('gender_distribution', distribution)
        self.assertIn('location_distribution', distribution)
        
        # Distributions should sum to approximately 1
        gender_dist = distribution['gender_distribution']
        total_gender = sum(gender_dist.values())
        self.assertAlmostEqual(total_gender, 1.0, places=2)

    async def test_demographic_correlations(self):
        """Test demographic correlation analysis"""        correlations = await self.analyzer.analyze_demographic_correlations(
            self.demographic_data
        )
        
        self.assertIsInstance(correlations, dict)
        self.assertIn('correlation_matrix', correlations)
        self.assertIn('significant_correlations', correlations)

    async def test_demographic_segmentation(self):
        """Test demographic-based segmentation"""        segments = await self.analyzer.create_demographic_segments(
            self.demographic_data,
            segmentation_features=['age', 'location', 'education']
        )
        
        self.assertIsInstance(segments, dict)
        
        # Check that all users are assigned to segments
        total_users = sum(len(segment_users) for segment_users in segments.values())
        self.assertEqual(total_users, len(self.demographic_data))

    async def test_privacy_aware_analysis(self):
        """Test privacy-aware demographic analysis"""        # Set high privacy level
        self.analyzer.privacy_level = PrivacyLevel.HIGH
        
        anonymized_analysis = await self.analyzer.analyze_with_privacy_protection(
            self.demographic_data
        )
        
        self.assertIsInstance(anonymized_analysis, dict)
        
        # Sensitive data should be anonymized or aggregated
        self.assertNotIn('individual_incomes', anonymized_analysis)
        self.assertNotIn('specific_locations', anonymized_analysis)

    async def test_demographic_trends(self):
        """Test demographic trend analysis"""        trends = await self.analyzer.analyze_demographic_trends(
            self.demographic_data,
            time_period='monthly'
        )
        
        self.assertIsInstance(trends, dict)
        self.assertIn('growth_trends', trends)
        self.assertIn('demographic_shifts', trends)

    async def test_demographic_inference(self):
        """Test demographic inference from behavior"""        # Generate behavior data without explicit demographics
        behavior_data = []
        for i in range(50):
            behavior_data.append({
                'user_id': f'user_inference_{i}',
                'listening_times': [np.random.randint(0, 24) for _ in range(20)],
                'music_preferences': {
                    'pop': np.random.uniform(0.0, 1.0),
                    'classical': np.random.uniform(0.0, 1.0),
                    'electronic': np.random.uniform(0.0, 1.0)
                },
                'device_usage': np.random.choice(['mobile', 'desktop', 'smart_speaker'])
            })
        
        inferred_demographics = await self.analyzer.infer_demographics_from_behavior(
            behavior_data
        )
        
        self.assertIsInstance(inferred_demographics, dict)
        
        for user_id, demographics in inferred_demographics.items():
            self.assertIn('predicted_age_range', demographics)
            self.assertIn('confidence', demographics)


class TestProfilePerformanceAndScalability(IsolatedAsyncioTestCase):
    """Performance and scalability tests for profile management"""
    async def test_large_scale_profile_operations(self):
        """Test profile operations at scale"""        manager = UserProfileManager(storage_backend='memory')
        
        # Generate large number of profiles
        n_profiles = 1000
        large_dataset = []
        
        for i in range(n_profiles):
            large_dataset.append({
                'user_id': f'user_{i}',
                'demographics': {
                    'age': np.random.randint(18, 65),
                    'location': f'location_{i % 10}'
                },
                'preferences': {
                    'music_genres': {
                        f'genre_{j}': np.random.uniform(0.0, 1.0)
                        for j in range(5)
                    }
                }
            })
        
        # Measure creation time
        start_time = time.time()
        await manager.create_profiles_batch(large_dataset)
        creation_time = time.time() - start_time
        
        # Should create 1000 profiles within reasonable time
        self.assertLess(creation_time, 10.0)  # 10 seconds max
        
        # Measure retrieval time
        user_ids = [f'user_{i}' for i in range(0, n_profiles, 10)]  # Every 10th user
        
        start_time = time.time()
        retrieved_profiles = await manager.get_profiles_batch(user_ids)
        retrieval_time = time.time() - start_time
        
        self.assertEqual(len(retrieved_profiles), len(user_ids))
        self.assertLess(retrieval_time, 2.0)  # 2 seconds max

    async def test_profile_memory_efficiency(self):
        """Test memory efficiency of profile storage"""        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        manager = UserProfileManager(storage_backend='memory')
        
        # Create many detailed profiles
        for i in range(500):
            profile_data = {
                'user_id': f'memory_test_user_{i}',
                'demographics': {f'demo_{j}': f'value_{j}' for j in range(20)},
                'preferences': {f'pref_{j}': np.random.uniform(0.0, 1.0) for j in range(50)},
                'behavior': {f'behavior_{j}': np.random.random() for j in range(30)},
                'history': [f'item_{j}' for j in range(100)]
            }
            await manager.create_profile(f'memory_test_user_{i}', profile_data)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        self.assertLess(memory_increase, 100)  # Less than 100MB for 500 profiles

    async def test_concurrent_profile_operations(self):
        """Test concurrent profile operations"""        manager = UserProfileManager(storage_backend='memory')
        
        async def create_profile_task(task_id: int):
            for i in range(20):
                user_id = f'concurrent_user_{task_id}_{i}'
                profile_data = {
                    'user_id': user_id,
                    'demographics': {'task_id': task_id, 'index': i},
                    'preferences': {'test_pref': np.random.uniform(0.0, 1.0)}
                }
                await manager.create_profile(user_id, profile_data)
        
        # Run 10 concurrent tasks
        tasks = [create_profile_task(i) for i in range(10)]
        await asyncio.gather(*tasks)
        
        # Verify all profiles were created
        stats = await manager.compute_profile_statistics()
        self.assertEqual(stats['total_profiles'], 200)  # 10 tasks * 20 profiles


class TestProfileRobustness(IsolatedAsyncioTestCase):
    """Robustness and edge case tests"""
    async def test_invalid_profile_data_handling(self):
        """Test handling of invalid profile data"""        manager = UserProfileManager(storage_backend='memory')
        
        # Test with completely invalid data
        invalid_data = {
            'user_id': None,  # Invalid user ID
            'demographics': 'not_a_dict',  # Should be dict
            'preferences': []  # Should be dict
        }
        
        with self.assertRaises(InvalidProfileDataError):
            await manager.create_profile('invalid_user', invalid_data)

    async def test_missing_required_fields(self):
        """Test handling of missing required fields"""        profile_data = {
            # Missing user_id
            'demographics': {'age': 25}
        }
        
        with self.assertRaises(InvalidProfileDataError):
            UserProfile(user_id=None, profile_data=profile_data)

    async def test_privacy_violation_detection(self):
        """Test detection of privacy violations"""        profile = UserProfile(
            user_id='privacy_test_user',
            profile_data={'demographics': {'ssn': '123-45-6789'}},  # Sensitive data
            privacy_level=PrivacyLevel.HIGH
        )
        
        # Should detect privacy violation when accessing sensitive data
        with self.assertRaises(PrivacyViolationError):
            await profile.get_privacy_filtered_data(request_sensitive_data=True)

    async def test_corrupted_profile_recovery(self):
        """Test recovery from corrupted profile data"""        manager = UserProfileManager(storage_backend='memory')
        
        # Create valid profile
        await manager.create_profile('test_user', {
            'user_id': 'test_user',
            'demographics': {'age': 30}
        })
        
        # Simulate corruption (this would normally come from storage)
        # In a real scenario, this might be disk corruption, network issues, etc.
        corrupted_data = {'corrupted': True}
        
        # Manager should handle corruption gracefully
        try:
            corrupted_profile = UserProfile('test_user', corrupted_data)
            is_valid = await corrupted_profile.validate()
            self.assertFalse(is_valid)
        except InvalidProfileDataError:
            pass  # Expected behavior

    async def test_extreme_data_values(self):
        """Test handling of extreme data values"""        extreme_data = {
            'user_id': 'extreme_user',
            'demographics': {
                'age': 999,  # Unrealistic age
                'location': 'x' * 1000  # Very long location string
            },
            'preferences': {
                'music_genres': {
                    'genre1': 999.0,  # Value outside normal range
                    'genre2': -100.0   # Negative preference
                }
            }
        }
        
        profile = UserProfile('extreme_user', extreme_data)
        
        # Profile should either normalize values or mark as invalid
        is_valid = await profile.validate()
        if is_valid:
            # If valid, values should be normalized
            age = profile.get_demographic('age')
            self.assertLessEqual(age, 120)  # Reasonable maximum age
            
            genre1_pref = profile.get_preferences('music_genres')['genre1']
            self.assertLessEqual(genre1_pref, 1.0)  # Preferences should be capped


# Test runner configuration
if __name__ == '__main__':
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--asyncio-mode=auto',
        '--maxfail=10'
    ])
