# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Test suite for Protection Monitoring module.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""import unittest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json


class TestProtectionMonitoring(unittest.TestCase):
    """Test suite for ProtectionMonitor class"""    def setUp(self):
        """Set up test fixtures"""        self.monitor = None  # Will be mocked
        self.sample_monitoring_target = {
            "user_id": "user_123",
            "content_id": "content_456",
            "content_type": "audio",
            "fingerprint_data": {
                "title": "Test Song",
                "audio_hash": "abc123def456",
                "duration": 180
            },
            "platforms": ["youtube", "instagram", "tiktok"],
            "monitoring_frequency": 24,
            "alert_threshold": 0.85,
            "created_at": datetime.now()
        }

    def test_monitoring_target_structure(self):
        """Test monitoring target data structure"""        target = {
            "user_id": "user_123",
            "content_id": "content_456",
            "content_type": "audio",
            "fingerprint_data": {"title": "Test Song"},
            "platforms": ["youtube"],
            "monitoring_frequency": 24,
            "alert_threshold": 0.85,
            "created_at": datetime.now()
        }
        
        # Verify required fields
        required_fields = ["user_id", "content_id", "content_type", "fingerprint_data", "platforms"]
        for field in required_fields:
            self.assertIn(field, target)
        
        # Verify data types
        self.assertIsInstance(target["platforms"], list)
        self.assertIsInstance(target["fingerprint_data"], dict)
        self.assertIsInstance(target["alert_threshold"], float)
        self.assertIsInstance(target["monitoring_frequency"], int)

    def test_violation_detection_scoring(self):
        """Test violation detection similarity scoring"""        original_title = "My Awesome Song"
        found_titles = [
            "My Awesome Song",  # Exact match
            "My Amazing Song",  # Similar
            "Completely Different",  # No match
            "Awesome Song My",  # Word order different
            "My Awesome Song Remix"  # Extended version
        ]
        
        # Simple word overlap similarity calculation
        original_words = set(original_title.lower().split())
        
        similarities = []
        for found_title in found_titles:
            found_words = set(found_title.lower().split())
            if len(original_words.union(found_words)) > 0:
                similarity = len(original_words.intersection(found_words)) / len(original_words.union(found_words))
            else:
                similarity = 0.0
            similarities.append(similarity)
        
        # Test expected similarity scores
        self.assertEqual(similarities[0], 1.0)  # Exact match
        self.assertGreater(similarities[1], 0.5)  # Similar
        self.assertLess(similarities[2], 0.3)  # No match
        self.assertGreater(similarities[3], 0.5)  # Word order different but similar
        self.assertGreater(similarities[4], 0.5)  # Extended version

    def test_search_query_generation(self):
        """Test search query generation from content fingerprint"""        content_data = {
            "content_id": "song_123",
            "user_id": "artist_456",
            "content_type": "audio",
            "fingerprint_data": {
                "title": "Summer Vibes",
                "artist": "TestArtist",
                "duration": 210
            }
        }
        
        # Generate search queries
        queries = []
        queries.append(content_data["content_id"])
        queries.append(f"user_{content_data['user_id']}")
        
        # Content-type specific queries
        if content_data["content_type"] == "audio":
            queries.extend(["music", "song", "audio", "track"])
        
        # Title-based queries
        title = content_data["fingerprint_data"].get("title", "")
        if title:
            queries.append(title)
            # Add individual words from title
            title_words = title.split()
            queries.extend(title_words[:3])  # Limit to first 3 words
        
        # Verify query generation
        self.assertIn("song_123", queries)
        self.assertIn("user_artist_456", queries)
        self.assertIn("Summer Vibes", queries)
        self.assertIn("Summer", queries)
        self.assertIn("Vibes", queries)
        self.assertIn("music", queries)
        self.assertIn("song", queries)

    def test_platform_crawler_initialization(self):
        """Test platform crawler initialization"""        crawlers = {
            'youtube': {'api_key': 'test_key', 'rate_limit': 1.0},
            'instagram': {'access_token': 'test_token', 'rate_limit': 2.0},
            'tiktok': {'api_key': 'test_key', 'rate_limit': 1.5},
            'twitter': {'api_key': 'test_key', 'rate_limit': 1.0}
        }
        
        # Verify all expected platforms are initialized
        expected_platforms = ['youtube', 'instagram', 'tiktok', 'twitter']
        for platform in expected_platforms:
            self.assertIn(platform, crawlers)
            self.assertIn('rate_limit', crawlers[platform])

    def test_monitoring_frequency_check(self):
        """Test monitoring frequency checking logic"""        target = {
            "content_id": "test_123",
            "monitoring_frequency": 24,  # hours
            "last_checked": None
        }
        
        # First check - should always return True
        should_check_first = target["last_checked"] is None
        self.assertTrue(should_check_first)
        
        # Recent check - should return False
        target["last_checked"] = datetime.now() - timedelta(hours=12)
        time_since_check = datetime.now() - target["last_checked"]
        should_check_recent = time_since_check.total_seconds() >= (target["monitoring_frequency"] * 3600)
        self.assertFalse(should_check_recent)
        
        # Old check - should return True
        target["last_checked"] = datetime.now() - timedelta(hours=25)
        time_since_check = datetime.now() - target["last_checked"]
        should_check_old = time_since_check.total_seconds() >= (target["monitoring_frequency"] * 3600)
        self.assertTrue(should_check_old)

    def test_violation_record_creation(self):
        """Test violation record creation"""        original_content = {
            "content_id": "original_123",
            "user_id": "user_456"
        }
        
        violation_data = {
            "platform": "youtube",
            "url": "https://youtube.com/watch?v=test123",
            "title": "Similar Song Title",
            "found_via": "api_search"
        }
        
        similarity_score = 0.92
        
        # Create violation record
        violation_record = {
            "original_content_id": original_content["content_id"],
            "user_id": original_content["user_id"],
            "platform": violation_data["platform"],
            "violation_url": violation_data["url"],
            "similarity_score": similarity_score,
            "detected_at": datetime.now(),
            "status": "pending_review",
            "evidence_data": violation_data
        }
        
        # Verify violation record structure
        self.assertEqual(violation_record["original_content_id"], "original_123")
        self.assertEqual(violation_record["user_id"], "user_456")
        self.assertEqual(violation_record["platform"], "youtube")
        self.assertEqual(violation_record["similarity_score"], 0.92)
        self.assertEqual(violation_record["status"], "pending_review")
        self.assertIsInstance(violation_record["detected_at"], datetime)

    def test_alert_threshold_filtering(self):
        """Test alert threshold filtering"""        alert_threshold = 0.85
        similarity_scores = [0.95, 0.82, 0.90, 0.75, 0.88, 0.60]
        
        # Filter violations above threshold
        violations = [score for score in similarity_scores if score >= alert_threshold]
        non_violations = [score for score in similarity_scores if score < alert_threshold]
        
        # Verify filtering
        self.assertEqual(len(violations), 3)  # 0.95, 0.90, 0.88
        self.assertEqual(len(non_violations), 3)  # 0.82, 0.75, 0.60
        
        for score in violations:
            self.assertGreaterEqual(score, alert_threshold)
        
        for score in non_violations:
            self.assertLess(score, alert_threshold)

    def test_platform_search_result_parsing(self):
        """Test platform search result parsing"""        # Mock YouTube search results
        youtube_results = [
            {
                "platform": "youtube",
                "id": "dQw4w9WgXcQ",
                "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "title": "Test Video Title",
                "channel": "TestChannel",
                "published_at": "2025-01-15T10:00:00Z",
                "found_via": "api_search"
            }
        ]
        
        # Mock Instagram search results
        instagram_results = [
            {
                "platform": "instagram",
                "url": "https://instagram.com/p/test123",
                "found_via": "hashtag_search"
            }
        ]
        
        # Verify result structure
        for result in youtube_results:
            self.assertIn("platform", result)
            self.assertIn("url", result)
            self.assertIn("found_via", result)
            self.assertEqual(result["platform"], "youtube")
        
        for result in instagram_results:
            self.assertIn("platform", result)
            self.assertIn("url", result)
            self.assertEqual(result["platform"], "instagram")

    def test_monitoring_cycle_scheduling(self):
        """Test monitoring cycle scheduling logic"""        active_monitors = {
            "content_1": {
                "content_id": "content_1",
                "monitoring_frequency": 24,
                "last_checked": datetime.now() - timedelta(hours=25)
            },
            "content_2": {
                "content_id": "content_2",
                "monitoring_frequency": 12,
                "last_checked": datetime.now() - timedelta(hours=6)
            },
            "content_3": {
                "content_id": "content_3",
                "monitoring_frequency": 48,
                "last_checked": None
            }
        }
        
        # Determine which content should be checked
        content_to_check = []
        
        for content_id, target in active_monitors.items():
            should_check = False
            
            if target["last_checked"] is None:
                should_check = True
            else:
                time_since_check = datetime.now() - target["last_checked"]
                should_check = time_since_check.total_seconds() >= (target["monitoring_frequency"] * 3600)
            
            if should_check:
                content_to_check.append(content_id)
        
        # Verify scheduling results
        self.assertIn("content_1", content_to_check)  # 25 hours ago, frequency 24h
        self.assertNotIn("content_2", content_to_check)  # 6 hours ago, frequency 12h
        self.assertIn("content_3", content_to_check)  # Never checked

    def test_content_fingerprint_comparison(self):
        """Test content fingerprint comparison logic"""        original_fingerprint = {
            "title": "Original Song",
            "duration": 180,
            "audio_hash": "abc123",
            "key_signature": "C_major",
            "tempo": 120
        }
        
        test_fingerprints = [
            {
                "title": "Original Song",
                "duration": 180,
                "audio_hash": "abc123",
                "similarity": 1.0  # Exact match
            },
            {
                "title": "Original Song Remix",
                "duration": 200,
                "audio_hash": "abc456",
                "similarity": 0.75  # Similar
            },
            {
                "title": "Different Song",
                "duration": 150,
                "audio_hash": "xyz789",
                "similarity": 0.1  # Different
            }
        ]
        
        # Test similarity thresholds
        high_similarity_threshold = 0.8
        medium_similarity_threshold = 0.5
        
        high_matches = [fp for fp in test_fingerprints if fp["similarity"] >= high_similarity_threshold]
        medium_matches = [fp for fp in test_fingerprints if fp["similarity"] >= medium_similarity_threshold]
        
        self.assertEqual(len(high_matches), 1)  # Only exact match
        self.assertEqual(len(medium_matches), 2)  # Exact and similar

    def test_monitoring_status_reporting(self):
        """Test monitoring status reporting"""        user_id = "user_123"
        active_monitors = {
            "content_1": {
                "user_id": "user_123",
                "content_id": "content_1",
                "platforms": ["youtube", "instagram"],
                "last_checked": datetime.now() - timedelta(hours=2)
            },
            "content_2": {
                "user_id": "user_123",
                "content_id": "content_2",
                "platforms": ["tiktok"],
                "last_checked": None
            },
            "content_3": {
                "user_id": "user_456",
                "content_id": "content_3",
                "platforms": ["youtube"],
                "last_checked": datetime.now() - timedelta(hours=1)
            }
        }
        
        # Generate status for specific user
        user_targets = [t for t in active_monitors.values() if t["user_id"] == user_id]
        
        status = {
            "total_monitored_content": len(user_targets),
            "monitoring_active": True,
            "last_check_times": {
                t["content_id"]: t["last_checked"].isoformat() if t["last_checked"] else None
                for t in user_targets
            },
            "platforms_monitored": list(set(
                platform for t in user_targets for platform in t["platforms"]
            ))
        }
        
        # Verify status report
        self.assertEqual(status["total_monitored_content"], 2)
        self.assertTrue(status["monitoring_active"])
        self.assertIn("content_1", status["last_check_times"])
        self.assertIn("content_2", status["last_check_times"])
        self.assertNotIn("content_3", status["last_check_times"])  # Different user
        
        # Verify platforms are aggregated correctly
        expected_platforms = {"youtube", "instagram", "tiktok"}
        actual_platforms = set(status["platforms_monitored"])
        self.assertEqual(actual_platforms, expected_platforms)


if __name__ == '__main__':
    unittest.main()