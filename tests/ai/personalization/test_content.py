# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Content Personalization Tests

Comprehensive tests for content personalization, recommendation, and delivery.
Tests content filtering, ranking, diversity, and real-time adaptation.

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
from typing import Dict, List, Any, Optional, Tuple, Set
import time
import os
import sys
from collections import defaultdict
import json

# Import the content modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from ai.personalization.content import (
    ContentRecommender,
    ContentMatcher,
    PersonalizedContentGenerator,
    ContentAdaptationEngine,
    ContentRankingEngine,
    ContentFilteringEngine,
    RecommendationStrategy,
    ContentMatchingType,
    ContentItem,
    RecommendationResult
)
from ai.personalization.exceptions import (
    ContentFilteringError,
    PersonalizationError,
    RecommendationError,
    ValidationError
)


class TestContentItem(IsolatedAsyncioTestCase):
    """Comprehensive tests for ContentItem class"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.content_data = self._generate_content_data()
        self.content_item = ContentItem(
            item_id='track_12345',
            content_type=ContentType.MUSIC,
            metadata=self.content_data['metadata'],
            features=self.content_data['features'],
            quality_score=self.content_data['quality_score']
        )

    def _generate_content_data(self) -> Dict[str, Any]:
        """Generate comprehensive content data"""



        return {
            'metadata': {
                'title': 'Test Track Title',
                'artist': 'Test Artist',
                'album': 'Test Album',
                'genre': 'Electronic',
                'subgenre': 'Deep House',
                'release_date': '2024-01-15',
                'duration': 285,  # seconds
                'language': 'en',
                'explicit': False,
                'tags': ['danceable', 'energetic', 'nighttime'],
                'label': 'Test Records'
            },
            'features': {
                # Audio features
                'energy': 0.75,
                'valence': 0.68,
                'danceability': 0.82,
                'acousticness': 0.15,
                'instrumentalness': 0.85,
                'liveness': 0.12,
                'speechiness': 0.04,
                'tempo': 125.4,
                'key': 'C#',
                'mode': 'minor',
                'time_signature': 4,
                
                # Derived features
                'mood': 'energetic',
                'intensity': 0.78,
                'complexity': 0.65,
                'familiarity': 0.45
            },
            'quality_score': QualityScore(
                audio_quality=0.92,
                metadata_completeness=0.88,
                popularity_score=0.34,
                freshness_score=0.76,
                overall_score=0.75
            )
        }

    async def test_content_item_initialization(self):
        """Test content item proper initialization"""
        self.assertEqual(self.content_item.item_id, 'track_12345')
        self.assertEqual(self.content_item.content_type, ContentType.MUSIC)
        self.assertIsNotNone(self.content_item.metadata)
        self.assertIsNotNone(self.content_item.features)
        self.assertIsNotNone(self.content_item.quality_score)

    async def test_metadata_access(self):
        """Test metadata access methods"""
        title = self.content_item.get_metadata('title')
        self.assertEqual(title, 'Test Track Title')
        
        genre = self.content_item.get_metadata('genre')
        self.assertEqual(genre, 'Electronic')
        
        tags = self.content_item.get_metadata('tags')
        self.assertIn('danceable', tags)

    async def test_feature_access(self):
        """Test feature access methods"""
        energy = self.content_item.get_feature('energy')
        self.assertEqual(energy, 0.75)
        
        tempo = self.content_item.get_feature('tempo')
        self.assertEqual(tempo, 125.4)
        
        # Test non-existent feature
        non_existent = self.content_item.get_feature('non_existent')
        self.assertIsNone(non_existent)

    async def test_feature_vector_generation(self):
        """Test feature vector generation"""
        feature_vector = await self.content_item.get_feature_vector()
        
        self.assertIsInstance(feature_vector, np.ndarray)
        self.assertGreater(len(feature_vector), 0)
        
        # All values should be normalized between 0 and 1
        self.assertTrue(np.all(feature_vector >= 0.0))
        self.assertTrue(np.all(feature_vector <= 1.0))

    async def test_similarity_computation(self):
        """Test similarity computation between content items"""
        # Create similar content item
        similar_data = self.content_data.copy()
        similar_data['features']['energy'] = 0.73  # Slightly different
        similar_data['features']['valence'] = 0.70
        
        similar_item = ContentItem(
            item_id='track_similar',
            content_type=ContentType.MUSIC,
            metadata=similar_data['metadata'],
            features=similar_data['features'],
            quality_score=similar_data['quality_score']
        )
        
        similarity = await self.content_item.compute_similarity(similar_item)
        
        self.assertIsInstance(similarity, (int, float))
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
        self.assertGreater(similarity, 0.8)  # Should be highly similar

    async def test_content_serialization(self):
        """Test content item serialization"""
        serialized = await self.content_item.to_dict()
        
        self.assertIsInstance(serialized, dict)
        self.assertIn('item_id', serialized)
        self.assertIn('content_type', serialized)
        self.assertIn('metadata', serialized)
        self.assertIn('features', serialized)

    async def test_content_validation(self):
        """Test content item validation"""
        is_valid = await self.content_item.validate()
        self.assertTrue(is_valid)
        
        # Test invalid content
        invalid_item = ContentItem(
            item_id='',  # Invalid empty ID
            content_type=ContentType.MUSIC,
            metadata={},
            features={},
            quality_score=QualityScore(0, 0, 0, 0, 0)
        )
        
        is_valid = await invalid_item.validate()
        self.assertFalse(is_valid)


class TestContentCatalog(IsolatedAsyncioTestCase):
    """Comprehensive tests for ContentCatalog"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.catalog = ContentCatalog(
            index_features=['genre', 'energy', 'valence', 'tempo'],
            similarity_threshold=0.1,
            auto_update=True
        )
        self.content_items = self._generate_content_catalog()

    def _generate_content_catalog(self) -> List[ContentItem]:
        """Generate content catalog for testing"""
        items = []
        genres = ['Electronic', 'Pop', 'Rock', 'Classical', 'Jazz']
        
        for i in range(100):
            genre = np.random.choice(genres)
            
            metadata = {
                'title': f'Track {i}',
                'artist': f'Artist {i % 20}',
                'genre': genre,
                'duration': np.random.randint(120, 360),
                'release_date': f'202{np.random.randint(0, 5)}-{np.random.randint(1, 13):02d}-01'
            }
            
            features = {
                'energy': np.random.uniform(0.0, 1.0),
                'valence': np.random.uniform(0.0, 1.0),
                'danceability': np.random.uniform(0.0, 1.0),
                'tempo': np.random.uniform(60.0, 180.0),
                'acousticness': np.random.uniform(0.0, 1.0)
            }
            
            quality_score = QualityScore(
                audio_quality=np.random.uniform(0.5, 1.0),
                metadata_completeness=np.random.uniform(0.7, 1.0),
                popularity_score=np.random.uniform(0.0, 1.0),
                freshness_score=np.random.uniform(0.0, 1.0),
                overall_score=np.random.uniform(0.5, 1.0)
            )
            
            item = ContentItem(
                item_id=f'track_{i}',
                content_type=ContentType.MUSIC,
                metadata=metadata,
                features=features,
                quality_score=quality_score
            )
            items.append(item)
        
        return items

    async def test_catalog_initialization(self):
        """Test catalog initialization"""
        self.assertIsNotNone(self.catalog.index_features)
        self.assertEqual(len(self.catalog.index_features), 4)
        self.assertTrue(self.catalog.auto_update)

    async def test_content_addition(self):
        """Test adding content to catalog"""
        initial_size = len(self.catalog)
        
        for item in self.content_items[:10]:
            await self.catalog.add_item(item)
        
        self.assertEqual(len(self.catalog), initial_size + 10)

    async def test_content_retrieval(self):
        """Test content retrieval from catalog"""
        # Add items to catalog
        await self.catalog.add_items_batch(self.content_items)
        
        # Retrieve specific item
        item = await self.catalog.get_item('track_5')
        self.assertIsNotNone(item)
        self.assertEqual(item.item_id, 'track_5')

    async def test_content_search(self):
        """Test content search functionality"""
        await self.catalog.add_items_batch(self.content_items)
        
        # Search by genre
        electronic_tracks = await self.catalog.search({
            'genre': 'Electronic'
        })
        
        self.assertIsInstance(electronic_tracks, list)
        for track in electronic_tracks:
            self.assertEqual(track.get_metadata('genre'), 'Electronic')

    async def test_content_filtering(self):
        """Test content filtering"""
        await self.catalog.add_items_batch(self.content_items)
        
        # Filter by energy level
        high_energy_tracks = await self.catalog.filter_items(
            filter_func=lambda item: item.get_feature('energy') > 0.7
        )
        
        self.assertIsInstance(high_energy_tracks, list)
        for track in high_energy_tracks:
            self.assertGreater(track.get_feature('energy'), 0.7)

    async def test_similarity_search(self):
        """Test similarity-based content search"""
        await self.catalog.add_items_batch(self.content_items)
        
        # Find similar items to first track
        seed_item = self.content_items[0]
        similar_items = await self.catalog.find_similar_items(
            seed_item,
            top_k=10,
            min_similarity=0.5
        )
        
        self.assertIsInstance(similar_items, list)
        self.assertLessEqual(len(similar_items), 10)
        
        for item in similar_items:
            self.assertNotEqual(item.item_id, seed_item.item_id)

    async def test_catalog_statistics(self):
        """Test catalog statistics computation"""
        await self.catalog.add_items_batch(self.content_items)
        
        stats = await self.catalog.compute_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_items', stats)
        self.assertIn('genre_distribution', stats)
        self.assertIn('feature_statistics', stats)
        self.assertIn('quality_distribution', stats)

    async def test_catalog_indexing(self):
        """Test catalog indexing for fast retrieval"""
        await self.catalog.add_items_batch(self.content_items)
        
        # Build index
        await self.catalog.build_index()
        
        # Test indexed search
        start_time = time.time()
        results = await self.catalog.search({'energy': {'min': 0.8}})
        search_time = time.time() - start_time
        
        # Should be fast with index
        self.assertLess(search_time, 1.0)
        self.assertIsInstance(results, list)


class TestContentRecommender(IsolatedAsyncioTestCase):
    """Comprehensive tests for ContentRecommender"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.recommender = ContentRecommender(
            strategy=PersonalizationStrategy.HYBRID,
            diversity_weight=0.3,
            freshness_weight=0.2,
            quality_threshold=0.6
        )
        self.user_profile = self._generate_user_profile()
        self.content_catalog = self._generate_content_catalog()

    def _generate_user_profile(self) -> Dict[str, Any]:
        """Generate user profile for recommendation testing"""



        return {
            'user_id': 'test_user_123',
            'preferences': {
                'music_genres': {
                    'Electronic': 0.8,
                    'Pop': 0.6,
                    'Jazz': 0.4,
                    'Classical': 0.2
                },
                'audio_features': {
                    'energy': 0.7,
                    'valence': 0.6,
                    'danceability': 0.8,
                    'acousticness': 0.3
                }
            },
            'behavior': {
                'listening_patterns': {
                    'daily_hours': 4.5,
                    'preferred_session_length': 45,
                    'skip_rate': 0.15
                },
                'interaction_patterns': {
                    'like_rate': 0.08,
                    'repeat_rate': 0.25
                }
            },
            'context': {
                'current_mood': 'energetic',
                'activity': 'working',
                'time_of_day': 'afternoon'
            },
            'history': {
                'recently_played': ['track_5', 'track_12', 'track_33'],
                'liked_tracks': ['track_7', 'track_19', 'track_45'],
                'disliked_tracks': ['track_2', 'track_28']
            }
        }

    def _generate_content_catalog(self) -> List[ContentItem]:
        """Generate content catalog for recommendation testing"""
        # Reuse the catalog generation from previous test
        items = []
        genres = ['Electronic', 'Pop', 'Rock', 'Classical', 'Jazz']
        
        for i in range(200):
            genre = np.random.choice(genres, p=[0.3, 0.25, 0.2, 0.15, 0.1])  # Weighted by user preferences
            
            metadata = {
                'title': f'Recommendation Track {i}',
                'artist': f'Artist {i % 30}',
                'genre': genre,
                'duration': np.random.randint(120, 360),
                'popularity': np.random.uniform(0.1, 1.0)
            }
            
            # Generate features correlated with genre
            if genre == 'Electronic':
                energy = np.random.uniform(0.6, 1.0)
                danceability = np.random.uniform(0.7, 1.0)
                acousticness = np.random.uniform(0.0, 0.3)
            elif genre == 'Classical':
                energy = np.random.uniform(0.0, 0.4)
                danceability = np.random.uniform(0.0, 0.3)
                acousticness = np.random.uniform(0.7, 1.0)
            else:
                energy = np.random.uniform(0.3, 0.8)
                danceability = np.random.uniform(0.4, 0.8)
                acousticness = np.random.uniform(0.2, 0.6)
            
            features = {
                'energy': energy,
                'valence': np.random.uniform(0.0, 1.0),
                'danceability': danceability,
                'acousticness': acousticness,
                'tempo': np.random.uniform(80.0, 160.0)
            }
            
            quality_score = QualityScore(
                audio_quality=np.random.uniform(0.6, 1.0),
                metadata_completeness=np.random.uniform(0.8, 1.0),
                popularity_score=metadata['popularity'],
                freshness_score=np.random.uniform(0.3, 1.0),
                overall_score=np.random.uniform(0.6, 1.0)
            )
            
            item = ContentItem(
                item_id=f'rec_track_{i}',
                content_type=ContentType.MUSIC,
                metadata=metadata,
                features=features,
                quality_score=quality_score
            )
            items.append(item)
        
        return items

    async def test_recommendation_generation(self):
        """Test basic recommendation generation"""
        recommendations = await self.recommender.generate_recommendations(
            user_profile=self.user_profile,
            content_catalog=self.content_catalog,
            num_recommendations=20,
            context={'session_type': 'discovery'}
        )
        
        self.assertIsInstance(recommendations, RecommendationSet)
        self.assertLessEqual(len(recommendations.items), 20)
        
        # All recommendations should meet quality threshold
        for item in recommendations.items:
            self.assertGreaterEqual(item.quality_score.overall_score, 0.6)

    async def test_collaborative_filtering_recommendations(self):
        """Test collaborative filtering recommendations"""
        self.recommender.strategy = PersonalizationStrategy.COLLABORATIVE
        
        # Add similar users' data
        similar_users = [
            {
                'user_id': 'similar_user_1',
                'liked_tracks': ['rec_track_5', 'rec_track_15', 'rec_track_25'],
                'similarity_score': 0.85
            },
            {
                'user_id': 'similar_user_2',
                'liked_tracks': ['rec_track_8', 'rec_track_18', 'rec_track_28'],
                'similarity_score': 0.72
            }
        ]
        
        recommendations = await self.recommender.generate_collaborative_recommendations(
            user_profile=self.user_profile,
            similar_users=similar_users,
            content_catalog=self.content_catalog,
            num_recommendations=15
        )
        
        self.assertIsInstance(recommendations, RecommendationSet)
        self.assertLessEqual(len(recommendations.items), 15)

    async def test_content_based_recommendations(self):
        """Test content-based recommendations"""
        self.recommender.strategy = PersonalizationStrategy.CONTENT_BASED
        
        recommendations = await self.recommender.generate_content_based_recommendations(
            user_profile=self.user_profile,
            content_catalog=self.content_catalog,
            num_recommendations=25
        )
        
        self.assertIsInstance(recommendations, RecommendationSet)
        self.assertLessEqual(len(recommendations.items), 25)
        
        # Recommendations should align with user preferences
        for item in recommendations.items:
            genre = item.get_metadata('genre')
            if genre in self.user_profile['preferences']['music_genres']:
                user_genre_pref = self.user_profile['preferences']['music_genres'][genre]
                self.assertGreater(user_genre_pref, 0.0)  # User should have some preference

    async def test_hybrid_recommendations(self):
        """Test hybrid recommendation strategy"""
        self.recommender.strategy = PersonalizationStrategy.HYBRID
        
        recommendations = await self.recommender.generate_hybrid_recommendations(
            user_profile=self.user_profile,
            content_catalog=self.content_catalog,
            collaborative_weight=0.6,
            content_weight=0.4,
            num_recommendations=30
        )
        
        self.assertIsInstance(recommendations, RecommendationSet)
        self.assertLessEqual(len(recommendations.items), 30)

    async def test_contextual_recommendations(self):
        """Test contextual recommendations"""
        # Test different contexts
        contexts = [
            {'activity': 'working', 'time_of_day': 'morning'},
            {'activity': 'exercising', 'mood': 'energetic'},
            {'activity': 'relaxing', 'time_of_day': 'evening'}
        ]
        
        for context in contexts:
            recommendations = await self.recommender.generate_contextual_recommendations(
                user_profile=self.user_profile,
                content_catalog=self.content_catalog,
                context=context,
                num_recommendations=15
            )
            
            self.assertIsInstance(recommendations, RecommendationSet)
            self.assertLessEqual(len(recommendations.items), 15)

    async def test_diversity_optimization(self):
        """Test recommendation diversity optimization"""
        self.recommender.diversity_weight = 0.8  # High diversity
        
        recommendations = await self.recommender.generate_recommendations(
            user_profile=self.user_profile,
            content_catalog=self.content_catalog,
            num_recommendations=20,
            optimize_diversity=True
        )
        
        # Calculate diversity
        genres = [item.get_metadata('genre') for item in recommendations.items]
        unique_genres = set(genres)
        diversity_ratio = len(unique_genres) / len(genres)
        
        self.assertGreater(diversity_ratio, 0.5)  # Should have good diversity

    async def test_recommendation_explanation(self):
        """Test recommendation explanation generation"""
        recommendations = await self.recommender.generate_recommendations(
            user_profile=self.user_profile,
            content_catalog=self.content_catalog,
            num_recommendations=10,
            include_explanations=True
        )
        
        for item in recommendations.items:
            explanation = recommendations.get_explanation(item.item_id)
            self.assertIsNotNone(explanation)
            self.assertIsInstance(explanation, dict)
            self.assertIn('reason', explanation)
            self.assertIn('confidence', explanation)

    async def test_recommendation_filtering(self):
        """Test recommendation filtering"""
        # Filter out recently played tracks
        recently_played = set(self.user_profile['history']['recently_played'])
        
        recommendations = await self.recommender.generate_recommendations(
            user_profile=self.user_profile,
            content_catalog=self.content_catalog,
            num_recommendations=20,
            exclude_items=recently_played
        )
        
        # No recently played tracks should be in recommendations
        rec_item_ids = {item.item_id for item in recommendations.items}
        overlap = rec_item_ids.intersection(recently_played)
        self.assertEqual(len(overlap), 0)

    async def test_recommendation_ranking(self):
        """Test recommendation ranking"""
        recommendations = await self.recommender.generate_recommendations(
            user_profile=self.user_profile,
            content_catalog=self.content_catalog,
            num_recommendations=20,
            ranking_method=RankingMethod.RELEVANCE_SCORE
        )
        
        # Recommendations should be ordered by relevance
        relevance_scores = [rec.relevance_score for rec in recommendations.items]
        
        # Check if sorted in descending order
        is_sorted = all(relevance_scores[i] >= relevance_scores[i+1] 
                       for i in range(len(relevance_scores)-1))
        self.assertTrue(is_sorted)


class TestContentFilter(IsolatedAsyncioTestCase):
    """Comprehensive tests for ContentFilter"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.filter = ContentFilter(
            filter_types=[FilterType.QUALITY, FilterType.CONTENT, FilterType.BEHAVIORAL],
            quality_threshold=0.6,
            content_safety_level='medium'
        )
        self.content_items = self._generate_filterable_content()
        self.user_profile = self._generate_user_profile_for_filtering()

    def _generate_filterable_content(self) -> List[ContentItem]:
        """Generate content items for filtering tests"""
        items = []
        
        for i in range(50):
            metadata = {
                'title': f'Filter Test Track {i}',
                'artist': f'Artist {i % 10}',
                'genre': np.random.choice(['Pop', 'Rock', 'Electronic', 'Explicit_Content']),
                'explicit': i % 10 == 0,  # Every 10th track is explicit
                'language': np.random.choice(['en', 'de', 'fr']),
                'release_date': f'202{np.random.randint(0, 5)}-01-01'
            }
            
            quality_score = QualityScore(
                audio_quality=np.random.uniform(0.3, 1.0),
                metadata_completeness=np.random.uniform(0.5, 1.0),
                popularity_score=np.random.uniform(0.1, 1.0),
                freshness_score=np.random.uniform(0.2, 1.0),
                overall_score=np.random.uniform(0.3, 1.0)
            )
            
            item = ContentItem(
                item_id=f'filter_track_{i}',
                content_type=ContentType.MUSIC,
                metadata=metadata,
                features={'energy': np.random.uniform(0.0, 1.0)},
                quality_score=quality_score
            )
            items.append(item)
        
        return items

    def _generate_user_profile_for_filtering(self) -> Dict[str, Any]:
        """Generate user profile for filtering tests"""



        return {
            'user_id': 'filter_test_user',
            'preferences': {
                'languages': ['en', 'de'],
                'explicit_content': False,
                'min_quality': 0.6,
                'genres': ['Pop', 'Electronic']
            },
            'demographics': {
                'age': 17,  # Minor
                'location': 'Germany'
            },
            'restrictions': {
                'parental_controls': True,
                'content_rating': 'PG'
            }
        }

    async def test_quality_filtering(self):
        """Test quality-based content filtering"""
        filtered_items = await self.filter.apply_quality_filter(
            items=self.content_items,
            min_quality=0.7
        )
        
        for item in filtered_items:
            self.assertGreaterEqual(item.quality_score.overall_score, 0.7)

    async def test_content_safety_filtering(self):
        """Test content safety filtering"""
        filtered_items = await self.filter.apply_content_filter(
            items=self.content_items,
            user_profile=self.user_profile
        )
        
        # Should filter out explicit content for minor
        for item in filtered_items:
            self.assertFalse(item.get_metadata('explicit'))

    async def test_language_filtering(self):
        """Test language-based filtering"""
        filtered_items = await self.filter.apply_language_filter(
            items=self.content_items,
            preferred_languages=['en', 'de']
        )
        
        for item in filtered_items:
            language = item.get_metadata('language')
            self.assertIn(language, ['en', 'de'])

    async def test_behavioral_filtering(self):
        """Test behavioral filtering based on user history"""
        user_history = {
            'disliked_genres': ['Rock'],
            'blocked_artists': ['Artist 3'],
            'preferred_duration': {'min': 120, 'max': 300}
        }
        
        filtered_items = await self.filter.apply_behavioral_filter(
            items=self.content_items,
            user_history=user_history
        )
        
        for item in filtered_items:
            genre = item.get_metadata('genre')
            artist = item.get_metadata('artist')
            
            self.assertNotEqual(genre, 'Rock')
            self.assertNotEqual(artist, 'Artist 3')

    async def test_temporal_filtering(self):
        """Test temporal filtering (freshness, recency)"""
        filtered_items = await self.filter.apply_temporal_filter(
            items=self.content_items,
            max_age_days=365,  # Only content from last year
            min_freshness=0.5
        )
        
        for item in filtered_items:
            self.assertGreaterEqual(item.quality_score.freshness_score, 0.5)

    async def test_composite_filtering(self):
        """Test composite filtering with multiple criteria"""
        filtered_items = await self.filter.apply_composite_filter(
            items=self.content_items,
            user_profile=self.user_profile,
            criteria={
                'min_quality': 0.7,
                'max_explicit': False,
                'preferred_languages': ['en', 'de'],
                'excluded_genres': ['Explicit_Content']
            }
        )
        
        for item in filtered_items:
            self.assertGreaterEqual(item.quality_score.overall_score, 0.7)
            self.assertFalse(item.get_metadata('explicit'))
            self.assertIn(item.get_metadata('language'), ['en', 'de'])
            self.assertNotEqual(item.get_metadata('genre'), 'Explicit_Content')

    async def test_adaptive_filtering(self):
        """Test adaptive filtering based on user feedback"""
        user_feedback = [
            {'item_id': 'filter_track_1', 'feedback': 'dislike', 'reason': 'too_low_quality'},
            {'item_id': 'filter_track_5', 'feedback': 'like', 'reason': 'good_quality'},
            {'item_id': 'filter_track_8', 'feedback': 'skip', 'reason': 'wrong_genre'}
        ]
        
        # Apply adaptive filtering
        await self.filter.update_from_feedback(user_feedback)
        
        filtered_items = await self.filter.apply_adaptive_filter(
            items=self.content_items,
            user_profile=self.user_profile
        )
        
        # Should learn from feedback and adjust filtering
        self.assertIsInstance(filtered_items, list)


class TestContentRanker(IsolatedAsyncioTestCase):
    """Comprehensive tests for ContentRanker"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.ranker = ContentRanker(
            ranking_method=RankingMethod.HYBRID,
            relevance_weight=0.4,
            quality_weight=0.3,
            diversity_weight=0.2,
            freshness_weight=0.1
        )
        self.content_items = self._generate_rankable_content()
        self.user_profile = self._generate_ranking_user_profile()

    def _generate_rankable_content(self) -> List[ContentItem]:
        """Generate content items for ranking tests"""
        items = []
        
        for i in range(30):
            metadata = {
                'title': f'Ranking Track {i}',
                'artist': f'Artist {i % 8}',
                'genre': np.random.choice(['Electronic', 'Pop', 'Jazz']),
                'popularity': np.random.uniform(0.1, 1.0),
                'play_count': np.random.randint(100, 10000)
            }
            
            features = {
                'energy': np.random.uniform(0.0, 1.0),
                'valence': np.random.uniform(0.0, 1.0),
                'danceability': np.random.uniform(0.0, 1.0)
            }
            
            quality_score = QualityScore(
                audio_quality=np.random.uniform(0.5, 1.0),
                metadata_completeness=np.random.uniform(0.7, 1.0),
                popularity_score=metadata['popularity'],
                freshness_score=np.random.uniform(0.3, 1.0),
                overall_score=np.random.uniform(0.5, 1.0)
            )
            
            item = ContentItem(
                item_id=f'rank_track_{i}',
                content_type=ContentType.MUSIC,
                metadata=metadata,
                features=features,
                quality_score=quality_score
            )
            items.append(item)
        
        return items

    def _generate_ranking_user_profile(self) -> Dict[str, Any]:
        """Generate user profile for ranking tests"""



        return {
            'user_id': 'ranking_test_user',
            'preferences': {
                'music_genres': {
                    'Electronic': 0.8,
                    'Pop': 0.5,
                    'Jazz': 0.3
                },
                'audio_features': {
                    'energy': 0.7,
                    'valence': 0.6
                }
            },
            'context': {
                'current_mood': 'energetic',
                'listening_goal': 'discovery'
            }
        }

    async def test_relevance_based_ranking(self):
        """Test relevance-based ranking"""
        ranked_items = await self.ranker.rank_by_relevance(
            items=self.content_items,
            user_profile=self.user_profile
        )
        
        self.assertEqual(len(ranked_items), len(self.content_items))
        
        # Check ranking order based on relevance scores
        relevance_scores = []
        for item in ranked_items:
            # Calculate expected relevance based on user preferences
            genre = item.get_metadata('genre')
            genre_pref = self.user_profile['preferences']['music_genres'].get(genre, 0.0)
            relevance_scores.append(genre_pref)
        
        # Should be in descending order of relevance
        is_sorted = all(relevance_scores[i] >= relevance_scores[i+1] 
                       for i in range(len(relevance_scores)-1))
        self.assertTrue(is_sorted)

    async def test_quality_based_ranking(self):
        """Test quality-based ranking"""
        ranked_items = await self.ranker.rank_by_quality(self.content_items)
        
        quality_scores = [item.quality_score.overall_score for item in ranked_items]
        
        # Should be sorted by quality in descending order
        is_sorted = all(quality_scores[i] >= quality_scores[i+1] 
                       for i in range(len(quality_scores)-1))
        self.assertTrue(is_sorted)

    async def test_popularity_based_ranking(self):
        """Test popularity-based ranking"""
        ranked_items = await self.ranker.rank_by_popularity(self.content_items)
        
        popularity_scores = [item.get_metadata('popularity') for item in ranked_items]
        
        # Should be sorted by popularity in descending order
        is_sorted = all(popularity_scores[i] >= popularity_scores[i+1] 
                       for i in range(len(popularity_scores)-1))
        self.assertTrue(is_sorted)

    async def test_hybrid_ranking(self):
        """Test hybrid ranking combining multiple factors"""
        ranked_items = await self.ranker.rank_hybrid(
            items=self.content_items,
            user_profile=self.user_profile,
            weights={
                'relevance': 0.4,
                'quality': 0.3,
                'popularity': 0.2,
                'freshness': 0.1
            }
        )
        
        self.assertEqual(len(ranked_items), len(self.content_items))
        
        # Calculate composite scores to verify ranking
        composite_scores = []
        for item in ranked_items:
            genre = item.get_metadata('genre')
            relevance = self.user_profile['preferences']['music_genres'].get(genre, 0.0)
            quality = item.quality_score.overall_score
            popularity = item.get_metadata('popularity')
            freshness = item.quality_score.freshness_score
            
            composite = (0.4 * relevance + 0.3 * quality + 
                        0.2 * popularity + 0.1 * freshness)
            composite_scores.append(composite)
        
        # Should be sorted by composite score
        is_sorted = all(composite_scores[i] >= composite_scores[i+1] 
                       for i in range(len(composite_scores)-1))
        self.assertTrue(is_sorted)

    async def test_contextual_ranking(self):
        """Test contextual ranking based on user context"""
        context = {
            'time_of_day': 'morning',
            'activity': 'working',
            'energy_level': 'medium'
        }
        
        ranked_items = await self.ranker.rank_contextual(
            items=self.content_items,
            user_profile=self.user_profile,
            context=context
        )
        
        self.assertEqual(len(ranked_items), len(self.content_items))
        
        # Context should influence ranking
        # For working context, moderate energy tracks should be preferred
        top_items = ranked_items[:5]
        avg_energy = np.mean([item.get_feature('energy') for item in top_items])
        self.assertGreater(avg_energy, 0.4)  # Not too low energy
        self.assertLess(avg_energy, 0.8)     # Not too high energy

    async def test_diversity_aware_ranking(self):
        """Test diversity-aware ranking"""
        ranked_items = await self.ranker.rank_with_diversity(
            items=self.content_items,
            user_profile=self.user_profile,
            diversity_factor=0.5
        )
        
        # Check that top results have good diversity
        top_10_genres = [item.get_metadata('genre') for item in ranked_items[:10]]
        unique_genres = set(top_10_genres)
        
        diversity_ratio = len(unique_genres) / len(top_10_genres)
        self.assertGreater(diversity_ratio, 0.3)  # Should have reasonable diversity

    async def test_ranking_explanation(self):
        """Test ranking explanation generation"""
        ranked_items = await self.ranker.rank_with_explanation(
            items=self.content_items,
            user_profile=self.user_profile
        )
        
        # Each item should have ranking explanation
        for item in ranked_items[:5]:  # Check top 5
            explanation = await self.ranker.get_ranking_explanation(
                item=item,
                user_profile=self.user_profile
            )
            
            self.assertIsInstance(explanation, dict)
            self.assertIn('ranking_factors', explanation)
            self.assertIn('score_breakdown', explanation)


class TestContentDiversifier(IsolatedAsyncioTestCase):
    """Comprehensive tests for ContentDiversifier"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.diversifier = ContentDiversifier(
            strategy=DiversityStrategy.FEATURE_BASED,
            diversity_threshold=0.3,
            max_similarity=0.7
        )
        self.content_items = self._generate_diverse_content()

    def _generate_diverse_content(self) -> List[ContentItem]:
        """Generate content for diversity testing"""
        items = []
        genres = ['Electronic', 'Pop', 'Rock', 'Jazz', 'Classical']
        
        for i in range(40):
            genre = np.random.choice(genres)
            
            # Create feature clusters for diversity testing
            if genre == 'Electronic':
                energy = np.random.uniform(0.7, 1.0)
                valence = np.random.uniform(0.5, 0.9)
            elif genre == 'Classical':
                energy = np.random.uniform(0.1, 0.4)
                valence = np.random.uniform(0.2, 0.7)
            else:
                energy = np.random.uniform(0.3, 0.8)
                valence = np.random.uniform(0.3, 0.8)
            
            metadata = {
                'title': f'Diverse Track {i}',
                'genre': genre,
                'artist': f'Artist {i % 12}',
                'subgenre': f'{genre}_subgenre_{i % 3}'
            }
            
            features = {
                'energy': energy,
                'valence': valence,
                'danceability': np.random.uniform(0.0, 1.0),
                'acousticness': np.random.uniform(0.0, 1.0),
                'tempo': np.random.uniform(80.0, 160.0)
            }
            
            item = ContentItem(
                item_id=f'diverse_track_{i}',
                content_type=ContentType.MUSIC,
                metadata=metadata,
                features=features,
                quality_score=QualityScore(0.8, 0.9, 0.5, 0.7, 0.75)
            )
            items.append(item)
        
        return items

    async def test_feature_based_diversification(self):
        """Test feature-based diversification"""
        diversified_items = await self.diversifier.diversify_by_features(
            items=self.content_items,
            target_size=15,
            feature_weights={'energy': 0.3, 'valence': 0.3, 'genre': 0.4}
        )
        
        self.assertLessEqual(len(diversified_items), 15)
        
        # Check feature diversity
        energies = [item.get_feature('energy') for item in diversified_items]
        valences = [item.get_feature('valence') for item in diversified_items]
        
        energy_std = np.std(energies)
        valence_std = np.std(valences)
        
        # Should have good spread in features
        self.assertGreater(energy_std, 0.1)
        self.assertGreater(valence_std, 0.1)

    async def test_genre_based_diversification(self):
        """Test genre-based diversification"""
        diversified_items = await self.diversifier.diversify_by_genre(
            items=self.content_items,
            target_size=20,
            max_per_genre=5
        )
        
        self.assertLessEqual(len(diversified_items), 20)
        
        # Count items per genre
        genre_counts = {}
        for item in diversified_items:
            genre = item.get_metadata('genre')
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        # No genre should exceed the limit
        for count in genre_counts.values():
            self.assertLessEqual(count, 5)

    async def test_artist_based_diversification(self):
        """Test artist-based diversification"""
        diversified_items = await self.diversifier.diversify_by_artist(
            items=self.content_items,
            target_size=18,
            max_per_artist=2
        )
        
        self.assertLessEqual(len(diversified_items), 18)
        
        # Count items per artist
        artist_counts = {}
        for item in diversified_items:
            artist = item.get_metadata('artist')
            artist_counts[artist] = artist_counts.get(artist, 0) + 1
        
        # No artist should exceed the limit
        for count in artist_counts.values():
            self.assertLessEqual(count, 2)

    async def test_temporal_diversification(self):
        """Test temporal diversification"""
        # Add release dates to items
        for i, item in enumerate(self.content_items):
            item.metadata['release_date'] = f'20{10 + (i % 15)}-01-01'
        
        diversified_items = await self.diversifier.diversify_by_time(
            items=self.content_items,
            target_size=16,
            time_window_years=3
        )
        
        self.assertLessEqual(len(diversified_items), 16)
        
        # Should have spread across different years
        years = [int(item.get_metadata('release_date')[:4]) for item in diversified_items]
        unique_years = set(years)
        
        self.assertGreater(len(unique_years), 3)

    async def test_similarity_based_diversification(self):
        """Test similarity-based diversification"""
        diversified_items = await self.diversifier.diversify_by_similarity(
            items=self.content_items,
            target_size=12,
            min_distance=0.3
        )
        
        self.assertLessEqual(len(diversified_items), 12)
        
        # Check pairwise similarities
        for i in range(len(diversified_items)):
            for j in range(i + 1, len(diversified_items)):
                similarity = await diversified_items[i].compute_similarity(diversified_items[j])
                self.assertLessEqual(similarity, 0.7)  # Max similarity threshold

    async def test_adaptive_diversification(self):
        """Test adaptive diversification based on user feedback"""
        user_feedback = {
            'diversity_preference': 0.8,  # High diversity preference
            'genre_exploration': True,
            'artist_exploration': True,
            'recent_interactions': ['diverse_track_5', 'diverse_track_15']
        }
        
        diversified_items = await self.diversifier.adaptive_diversify(
            items=self.content_items,
            target_size=20,
            user_feedback=user_feedback
        )
        
        self.assertLessEqual(len(diversified_items), 20)
        
        # Should have high diversity due to user preference
        genres = [item.get_metadata('genre') for item in diversified_items]
        unique_genres = set(genres)
        diversity_ratio = len(unique_genres) / len(genres)
        
        self.assertGreater(diversity_ratio, 0.6)

    async def test_diversity_metrics(self):
        """Test diversity metrics computation"""
        subset = self.content_items[:10]
        
        metrics = await self.diversifier.compute_diversity_metrics(subset)
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('intra_list_diversity', metrics)
        self.assertIn('genre_diversity', metrics)
        self.assertIn('feature_diversity', metrics)
        self.assertIn('temporal_diversity', metrics)
        
        # All metrics should be between 0 and 1
        for metric_value in metrics.values():
            if isinstance(metric_value, (int, float)):
                self.assertGreaterEqual(metric_value, 0.0)
                self.assertLessEqual(metric_value, 1.0)


class TestRealTimeAdapter(IsolatedAsyncioTestCase):
    """Comprehensive tests for RealTimeAdapter"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.adapter = RealTimeAdapter(
            adaptation_rate=0.1,
            feedback_window=100,
            min_feedback_count=5
        )
        self.real_time_data = self._generate_real_time_data()

    def _generate_real_time_data(self) -> List[Dict[str, Any]]:
        """Generate real-time interaction data"""
        data = []
        user_id = 'realtime_user'
        
        for i in range(150):
            interaction = {
                'user_id': user_id,
                'item_id': f'rt_track_{i % 30}',
                'action': np.random.choice(['play', 'skip', 'like', 'dislike'], 
                                        p=[0.6, 0.25, 0.1, 0.05]),
                'timestamp': datetime.utcnow() - timedelta(minutes=150-i),
                'session_id': f'session_{i // 20}',
                'context': {
                    'device': np.random.choice(['mobile', 'desktop']),
                    'location': np.random.choice(['home', 'work', 'commute']),
                    'time_of_day': (datetime.utcnow() - timedelta(minutes=150-i)).hour
                },
                'duration': np.random.randint(30, 300) if np.random.random() > 0.25 else 15  # Some skips
            }
            data.append(interaction)
        
        return data

    async def test_real_time_preference_learning(self):
        """Test real-time preference learning"""
        initial_preferences = {
            'energy': 0.5,
            'valence': 0.5,
            'danceability': 0.5
        }
        
        updated_preferences = await self.adapter.update_preferences_realtime(
            current_preferences=initial_preferences,
            recent_interactions=self.real_time_data[-20:]  # Last 20 interactions
        )
        
        self.assertIsInstance(updated_preferences, dict)
        self.assertEqual(set(updated_preferences.keys()), set(initial_preferences.keys()))
        
        # Preferences should have changed based on interactions
        self.assertNotEqual(updated_preferences, initial_preferences)

    async def test_session_adaptation(self):
        """Test adaptation within a listening session"""
        session_interactions = [
            interaction for interaction in self.real_time_data 
            if interaction['session_id'] == 'session_1'
        ]
        
        adaptations = await self.adapter.adapt_within_session(session_interactions)
        
        self.assertIsInstance(adaptations, list)
        self.assertGreater(len(adaptations), 0)
        
        for adaptation in adaptations:
            self.assertIn('timestamp', adaptation)
            self.assertIn('adaptation_type', adaptation)
            self.assertIn('parameters', adaptation)

    async def test_context_aware_adaptation(self):
        """Test context-aware adaptation"""
        current_context = {
            'time_of_day': 'evening',
            'device': 'mobile',
            'location': 'home',
            'activity': 'relaxing'
        }
        
        adapted_params = await self.adapter.adapt_to_context(
            current_context=current_context,
            historical_contexts=self.real_time_data
        )
        
        self.assertIsInstance(adapted_params, dict)
        self.assertIn('content_preferences', adapted_params)
        self.assertIn('interaction_patterns', adapted_params)

    async def test_feedback_incorporation(self):
        """Test incorporation of user feedback"""
        feedback_events = [
            {'item_id': 'rt_track_5', 'feedback': 'thumbs_up', 'timestamp': datetime.utcnow()},
            {'item_id': 'rt_track_12', 'feedback': 'thumbs_down', 'timestamp': datetime.utcnow()},
            {'item_id': 'rt_track_18', 'feedback': 'save_to_playlist', 'timestamp': datetime.utcnow()}
        ]
        
        updated_model = await self.adapter.incorporate_feedback(
            feedback_events=feedback_events,
            current_model_state={'preferences': {'energy': 0.6}}
        )
        
        self.assertIsInstance(updated_model, dict)
        self.assertIn('preferences', updated_model)

    async def test_drift_detection(self):
        """Test concept drift detection"""
        # Create data with a clear shift in behavior
        baseline_period = self.real_time_data[:75]  # First half
        recent_period = self.real_time_data[75:]    # Second half
        
        # Simulate behavior change in recent period
        for interaction in recent_period:
            if interaction['action'] == 'play':
                interaction['action'] = 'skip' if np.random.random() < 0.5 else 'play'
        
        drift_detected = await self.adapter.detect_concept_drift(
            baseline_period=baseline_period,
            recent_period=recent_period
        )
        
        self.assertIsInstance(drift_detected, dict)
        self.assertIn('drift_detected', drift_detected)
        self.assertIn('confidence', drift_detected)
        self.assertIn('drift_type', drift_detected)

    async def test_adaptation_speed_control(self):
        """Test adaptation speed control"""
        # Test different adaptation rates
        fast_adapter = RealTimeAdapter(adaptation_rate=0.5)
        slow_adapter = RealTimeAdapter(adaptation_rate=0.01)
        
        initial_prefs = {'energy': 0.5}
        recent_data = self.real_time_data[-10:]
        
        fast_adapted = await fast_adapter.update_preferences_realtime(initial_prefs, recent_data)
        slow_adapted = await slow_adapter.update_preferences_realtime(initial_prefs, recent_data)
        
        # Fast adapter should change more
        fast_change = abs(fast_adapted['energy'] - initial_prefs['energy'])
        slow_change = abs(slow_adapted['energy'] - initial_prefs['energy'])
        
        self.assertGreater(fast_change, slow_change)

    async def test_real_time_recommendation_adjustment(self):
        """Test real-time recommendation adjustment"""
        # Simulate recommendations that need adjustment
        initial_recommendations = [
            {'item_id': f'rt_track_{i}', 'score': np.random.uniform(0.5, 1.0)}
            for i in range(10)
        ]
        
        # Recent negative feedback on similar items
        recent_feedback = [
            {'item_id': 'rt_track_1', 'action': 'skip', 'reason': 'too_energetic'},
            {'item_id': 'rt_track_3', 'action': 'dislike', 'reason': 'wrong_mood'}
        ]
        
        adjusted_recommendations = await self.adapter.adjust_recommendations_realtime(
            recommendations=initial_recommendations,
            recent_feedback=recent_feedback
        )
        
        self.assertIsInstance(adjusted_recommendations, list)
        self.assertEqual(len(adjusted_recommendations), len(initial_recommendations))
        
        # Scores should be adjusted based on feedback
        for rec in adjusted_recommendations:
            self.assertIn('adjusted_score', rec)


class TestContentPerformanceAndScalability(IsolatedAsyncioTestCase):
    """Performance and scalability tests for content operations"""

    async def test_large_catalog_operations(self):
        """Test operations on large content catalogs"""
        # Generate large catalog
        large_catalog = ContentCatalog()
        n_items = 5000
        
        start_time = time.time()
        
        # Generate and add items in batches
        batch_size = 500
        for batch_start in range(0, n_items, batch_size):
            batch_items = []
            for i in range(batch_start, min(batch_start + batch_size, n_items)):
                item = ContentItem(
                    item_id=f'perf_track_{i}',
                    content_type=ContentType.MUSIC,
                    metadata={'genre': f'genre_{i % 10}'},
                    features={'energy': np.random.uniform(0.0, 1.0)},
                    quality_score=QualityScore(0.8, 0.9, 0.6, 0.7, 0.75)
                )
                batch_items.append(item)
            
            await large_catalog.add_items_batch(batch_items)
        
        catalog_creation_time = time.time() - start_time
        
        # Test search performance
        start_time = time.time()
        search_results = await large_catalog.search({'genre': 'genre_5'})
        search_time = time.time() - start_time
        
        # Performance assertions
        self.assertLess(catalog_creation_time, 30.0)  # Should create within 30 seconds
        self.assertLess(search_time, 2.0)             # Search should be fast
        self.assertGreater(len(search_results), 0)

    async def test_recommendation_generation_speed(self):
        """Test recommendation generation speed"""
        recommender = ContentRecommender()
        
        # Generate test data
        user_profile = {
            'user_id': 'speed_test_user',
            'preferences': {'music_genres': {'Pop': 0.8, 'Electronic': 0.6}}
        }
        
        content_catalog = []
        for i in range(1000):
            item = ContentItem(
                item_id=f'speed_track_{i}',
                content_type=ContentType.MUSIC,
                metadata={'genre': np.random.choice(['Pop', 'Electronic', 'Rock'])},
                features={'energy': np.random.uniform(0.0, 1.0)},
                quality_score=QualityScore(0.7, 0.8, 0.5, 0.6, 0.65)
            )
            content_catalog.append(item)
        
        # Measure recommendation generation time
        start_time = time.time()
        recommendations = await recommender.generate_recommendations(
            user_profile=user_profile,
            content_catalog=content_catalog,
            num_recommendations=50
        )
        generation_time = time.time() - start_time
        
        self.assertLess(generation_time, 5.0)  # Should generate within 5 seconds
        self.assertLessEqual(len(recommendations.items), 50)

    async def test_concurrent_content_operations(self):
        """Test concurrent content operations"""
        catalog = ContentCatalog()
        
        async def add_content_task(task_id: int):
            items = []
            for i in range(100):
                item = ContentItem(
                    item_id=f'concurrent_track_{task_id}_{i}',
                    content_type=ContentType.MUSIC,
                    metadata={'task_id': task_id},
                    features={'energy': np.random.uniform(0.0, 1.0)},
                    quality_score=QualityScore(0.7, 0.8, 0.5, 0.6, 0.65)
                )
                items.append(item)
            
            await catalog.add_items_batch(items)
        
        # Run concurrent tasks
        tasks = [add_content_task(i) for i in range(10)]
        await asyncio.gather(*tasks)
        
        # Verify all items were added
        stats = await catalog.compute_statistics()
        self.assertEqual(stats['total_items'], 1000)  # 10 tasks * 100 items


# Test runner configuration
if __name__ == '__main__':
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--asyncio-mode=auto',
        '--maxfail=15'
    ])
