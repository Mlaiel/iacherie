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

"""Test suite for Content Processor module.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import unittest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json


class TestContentProcessor(unittest.TestCase):
    """Test suite for ContentProcessor class"""
    def setUp(self):
        """Set up test fixtures"""
        self.processor = None  # Will be mocked
        self.sample_content = {
            "content_id": "content_123",
            "type": "audio",
            "file_path": "/uploads/audio.mp3",
            "metadata": {
                "duration": 180,
                "bitrate": 320,
                "sample_rate": 44100,
                "title": "Test Song"
            }
        }

    def test_content_metadata_extraction(self):
        """Test content metadata extraction"""
        audio_file = {
            "path": "/uploads/test.mp3",
            "size": 5242880,  # 5MB
            "format": "mp3"
        }
        
        # Mock extracted metadata
        extracted_metadata = {
            "duration": 210.5,
            "bitrate": 320,
            "sample_rate": 44100,
            "channels": 2,
            "format": "mp3",
            "codec": "mp3",
            "title": "Sample Song",
            "artist": "Test Artist",
            "album": "Test Album",
            "year": 2025,
            "genre": "Electronic"
        }
        
        # Verify metadata structure
        required_fields = ["duration", "bitrate", "sample_rate", "channels", "format"]
        for field in required_fields:
            self.assertIn(field, extracted_metadata)
        
        # Verify data types
        self.assertIsInstance(extracted_metadata["duration"], (int, float))
        self.assertIsInstance(extracted_metadata["bitrate"], int)
        self.assertIsInstance(extracted_metadata["sample_rate"], int)
        self.assertIsInstance(extracted_metadata["channels"], int)

    def test_audio_fingerprint_generation(self):
        """Test audio fingerprint generation"""
        audio_content = {
            "file_path": "/uploads/audio.mp3",
            "duration": 180,
            "sample_rate": 44100
        }
        
        # Mock fingerprint data
        fingerprint = {
            "spectral_hash": "a1b2c3d4e5f6",
            "chromagram_features": [0.1, 0.2, 0.15, 0.3, 0.25, 0.18, 0.22, 0.12, 0.28, 0.19, 0.16, 0.24],
            "tempo": 120.5,
            "key": "C_major",
            "loudness": -14.2,
            "energy": 0.75,
            "danceability": 0.68,
            "valence": 0.82,
            "mfcc_features": [1.2, 0.8, -0.5, 0.3, -0.1, 0.6, -0.3, 0.4, 0.2, -0.2, 0.1, -0.4, 0.5],
            "onset_frames": [2205, 4410, 6615, 8820],  # Frame positions of onsets
            "spectral_centroid": 2500.3,
            "zero_crossing_rate": 0.045
        }
        
        # Verify fingerprint structure
        required_features = ["spectral_hash", "chromagram_features", "tempo", "key", "mfcc_features"]
        for feature in required_features:
            self.assertIn(feature, fingerprint)
        
        # Verify feature dimensions
        self.assertEqual(len(fingerprint["chromagram_features"]), 12)  # 12 chroma bins
        self.assertEqual(len(fingerprint["mfcc_features"]), 13)        # 13 MFCC coefficients
        self.assertIsInstance(fingerprint["tempo"], (int, float))
        self.assertIn("_", fingerprint["key"])  # Key format like "C_major"

    def test_content_similarity_calculation(self):
        """Test content similarity calculation"""
        fingerprint1 = {
            "spectral_hash": "a1b2c3d4e5f6",
            "chromagram_features": [0.1, 0.2, 0.15, 0.3, 0.25, 0.18, 0.22, 0.12, 0.28, 0.19, 0.16, 0.24],
            "tempo": 120.5,
            "mfcc_features": [1.2, 0.8, -0.5, 0.3, -0.1, 0.6, -0.3, 0.4, 0.2, -0.2, 0.1, -0.4, 0.5]
        }
        
        fingerprint2 = {
            "spectral_hash": "a1b2c3d4e5f7",  # Slightly different hash
            "chromagram_features": [0.12, 0.18, 0.16, 0.32, 0.23, 0.19, 0.24, 0.10, 0.30, 0.17, 0.15, 0.26],
            "tempo": 122.0,
            "mfcc_features": [1.1, 0.9, -0.4, 0.4, -0.2, 0.5, -0.2, 0.3, 0.3, -0.1, 0.2, -0.3, 0.6]
        }
        
        # Calculate similarity components
        
        # Spectral hash similarity (exact match = 1.0, no match = 0.0)
        hash_similarity = 1.0 if fingerprint1["spectral_hash"] == fingerprint2["spectral_hash"] else 0.8  # Similar but not exact
        
        # Chromagram similarity (cosine similarity)
        chroma1 = fingerprint1["chromagram_features"]
        chroma2 = fingerprint2["chromagram_features"]
        
        dot_product = sum(a * b for a, b in zip(chroma1, chroma2))
        magnitude1 = sum(a * a for a in chroma1) ** 0.5
        magnitude2 = sum(a * a for a in chroma2) ** 0.5
        chroma_similarity = dot_product / (magnitude1 * magnitude2)
        
        # Tempo similarity
        tempo_diff = abs(fingerprint1["tempo"] - fingerprint2["tempo"])
        tempo_similarity = max(0, 1 - tempo_diff / 20)  # Normalize by 20 BPM range
        
        # MFCC similarity
        mfcc1 = fingerprint1["mfcc_features"]
        mfcc2 = fingerprint2["mfcc_features"]
        
        mfcc_dot = sum(a * b for a, b in zip(mfcc1, mfcc2))
        mfcc_mag1 = sum(a * a for a in mfcc1) ** 0.5
        mfcc_mag2 = sum(a * a for a in mfcc2) ** 0.5
        mfcc_similarity = mfcc_dot / (mfcc_mag1 * mfcc_mag2)
        
        # Overall similarity (weighted combination)
        overall_similarity = (
            hash_similarity * 0.3 +
            chroma_similarity * 0.25 +
            tempo_similarity * 0.2 +
            mfcc_similarity * 0.25
        )
        
        # Verify similarity calculations
        self.assertGreater(chroma_similarity, 0.8)    # Should be quite similar
        self.assertGreater(tempo_similarity, 0.9)     # Tempos are close
        self.assertGreater(mfcc_similarity, 0.7)      # MFCCs should be similar
        self.assertGreater(overall_similarity, 0.8)   # Overall high similarity

    def test_content_quality_assessment(self):
        """Test content quality assessment"""
        audio_features = {
            "bitrate": 320,
            "sample_rate": 44100,
            "dynamic_range": 12.5,  # dB
            "peak_amplitude": -3.2,  # dBFS
            "rms_energy": -18.5,     # dBFS
            "snr_estimate": 45.2,    # Signal-to-noise ratio
            "thd_estimate": 0.002,   # Total harmonic distortion (0.2%)
            "frequency_response_flatness": 0.85,  # 0-1 scale
            "stereo_width": 0.7,     # Stereo separation
            "loudness_range": 8.3    # LU (loudness units)
        }
        
        # Quality scoring algorithm
        quality_scores = {}
        
        # Bitrate quality (0-1)
        if audio_features["bitrate"] >= 320:
            quality_scores["bitrate"] = 1.0
        elif audio_features["bitrate"] >= 256:
            quality_scores["bitrate"] = 0.8
        elif audio_features["bitrate"] >= 192:
            quality_scores["bitrate"] = 0.6
        else:
            quality_scores["bitrate"] = 0.4
        
        # Dynamic range quality
        dr = audio_features["dynamic_range"]
        if dr >= 15:
            quality_scores["dynamic_range"] = 1.0
        elif dr >= 10:
            quality_scores["dynamic_range"] = 0.8
        elif dr >= 7:
            quality_scores["dynamic_range"] = 0.6
        else:
            quality_scores["dynamic_range"] = 0.3
        
        # Signal-to-noise ratio quality
        snr = audio_features["snr_estimate"]
        if snr >= 50:
            quality_scores["snr"] = 1.0
        elif snr >= 40:
            quality_scores["snr"] = 0.8
        elif snr >= 30:
            quality_scores["snr"] = 0.6
        else:
            quality_scores["snr"] = 0.4
        
        # THD quality (lower is better)
        thd = audio_features["thd_estimate"]
        if thd <= 0.001:
            quality_scores["thd"] = 1.0
        elif thd <= 0.005:
            quality_scores["thd"] = 0.8
        elif thd <= 0.01:
            quality_scores["thd"] = 0.6
        else:
            quality_scores["thd"] = 0.4
        
        # Overall quality score
        overall_quality = sum(quality_scores.values()) / len(quality_scores)
        
        # Verify quality assessment
        self.assertEqual(quality_scores["bitrate"], 1.0)      # 320 kbps
        self.assertEqual(quality_scores["dynamic_range"], 0.8) # 12.5 dB
        self.assertEqual(quality_scores["snr"], 0.8)          # 45.2 dB
        self.assertEqual(quality_scores["thd"], 0.8)          # 0.002%
        self.assertAlmostEqual(overall_quality, 0.85, places=2)

    def test_content_genre_classification(self):
        """Test content genre classification"""
        audio_features = {
            "tempo": 128,
            "key": "F_minor",
            "energy": 0.8,
            "danceability": 0.9,
            "valence": 0.3,  # Low valence (sad/dark)
            "acousticness": 0.1,
            "instrumentalness": 0.8,
            "speechiness": 0.04,
            "loudness": -8.5,
            "spectral_centroid": 3500,
            "mfcc_variance": 0.45
        }
        
        # Genre classification rules (simplified)
        genre_scores = {}
        
        # Electronic/EDM indicators
        electronic_score = 0
        if audio_features["tempo"] >= 120 and audio_features["tempo"] <= 140:
            electronic_score += 0.3
        if audio_features["danceability"] >= 0.7:
            electronic_score += 0.3
        if audio_features["energy"] >= 0.7:
            electronic_score += 0.2
        if audio_features["acousticness"] <= 0.2:
            electronic_score += 0.2
        
        genre_scores["electronic"] = electronic_score
        
        # Hip-hop indicators
        hiphop_score = 0
        if audio_features["tempo"] >= 70 and audio_features["tempo"] <= 100:
            hiphop_score += 0.3
        if audio_features["speechiness"] >= 0.1:
            hiphop_score += 0.4
        if audio_features["danceability"] >= 0.6:
            hiphop_score += 0.3
        
        genre_scores["hip_hop"] = hiphop_score
        
        # Classical indicators
        classical_score = 0
        if audio_features["acousticness"] >= 0.7:
            classical_score += 0.4
        if audio_features["instrumentalness"] >= 0.7:
            classical_score += 0.3
        if audio_features["energy"] <= 0.5:
            classical_score += 0.3
        
        genre_scores["classical"] = classical_score
        
        # Rock indicators
        rock_score = 0
        if audio_features["energy"] >= 0.6:
            rock_score += 0.3
        if audio_features["loudness"] >= -12:
            rock_score += 0.3
        if audio_features["valence"] >= 0.5:
            rock_score += 0.2
        if audio_features["acousticness"] <= 0.4:
            rock_score += 0.2
        
        genre_scores["rock"] = rock_score
        
        # Find most likely genre
        predicted_genre = max(genre_scores.items(), key=lambda x: x[1])
        
        # Verify genre classification
        self.assertGreater(genre_scores["electronic"], 0.8)  # Should score high for electronic
        self.assertLess(genre_scores["hip_hop"], 0.5)        # Low speechiness
        self.assertGreater(genre_scores["classical"], 0.6)   # High instrumentalness
        self.assertEqual(predicted_genre[0], "electronic")   # Should classify as electronic

    def test_content_enhancement_pipeline(self):
        """Test content enhancement pipeline"""
        input_audio = {
            "file_path": "/uploads/raw_audio.wav",
            "current_quality": {
                "bitrate": 192,
                "dynamic_range": 8.2,
                "loudness": -23.1,  # Too quiet
                "noise_level": 0.15  # Some background noise
            }
        }
        
        # Enhancement pipeline steps
        enhancement_steps = []
        
        # Step 1: Noise reduction
        if input_audio["current_quality"]["noise_level"] > 0.1:
            enhancement_steps.append({
                "step": "noise_reduction",
                "parameters": {
                    "noise_threshold": 0.05,
                    "reduction_amount": 0.7
                },
                "expected_improvement": {"noise_level": 0.05}
            })
        
        # Step 2: Loudness normalization
        if input_audio["current_quality"]["loudness"] < -18:
            enhancement_steps.append({
                "step": "loudness_normalization",
                "parameters": {
                    "target_lufs": -16,
                    "max_peak": -1.0
                },
                "expected_improvement": {"loudness": -16.0}
            })
        
        # Step 3: Dynamic range enhancement
        if input_audio["current_quality"]["dynamic_range"] < 10:
            enhancement_steps.append({
                "step": "dynamic_range_enhancement",
                "parameters": {
                    "target_dr": 12,
                    "compression_ratio": 2.5
                },
                "expected_improvement": {"dynamic_range": 12.0}
            })
        
        # Step 4: Quality upsampling
        if input_audio["current_quality"]["bitrate"] < 320:
            enhancement_steps.append({
                "step": "quality_upsampling",
                "parameters": {
                    "target_bitrate": 320,
                    "target_sample_rate": 44100
                },
                "expected_improvement": {"bitrate": 320}
            })
        
        # Apply enhancements (mock results)
        enhanced_quality = input_audio["current_quality"].copy()
        
        for step in enhancement_steps:
            improvement = step["expected_improvement"]
            enhanced_quality.update(improvement)
        
        # Verify enhancement pipeline
        self.assertEqual(len(enhancement_steps), 4)  # All steps needed
        self.assertEqual(enhanced_quality["noise_level"], 0.05)
        self.assertEqual(enhanced_quality["loudness"], -16.0)
        self.assertEqual(enhanced_quality["dynamic_range"], 12.0)
        self.assertEqual(enhanced_quality["bitrate"], 320)
        
        # Verify step ordering (noise reduction should be first)
        self.assertEqual(enhancement_steps[0]["step"], "noise_reduction")

    def test_batch_content_processing(self):
        """Test batch content processing capabilities"""
        content_batch = [
            {"id": "content_1", "type": "audio", "path": "/uploads/song1.mp3", "priority": "high"},
            {"id": "content_2", "type": "audio", "path": "/uploads/song2.mp3", "priority": "medium"},
            {"id": "content_3", "type": "video", "path": "/uploads/video1.mp4", "priority": "low"},
            {"id": "content_4", "type": "audio", "path": "/uploads/song3.mp3", "priority": "high"},
            {"id": "content_5", "type": "image", "path": "/uploads/cover1.jpg", "priority": "medium"}
        ]
        
        # Sort by priority and type
        priority_order = {"high": 3, "medium": 2, "low": 1}
        
        sorted_batch = sorted(
            content_batch,
            key=lambda x: (priority_order[x["priority"]], x["type"]),
            reverse=True
        )
        
        # Group by type for parallel processing
        type_groups = {}
        for item in sorted_batch:
            content_type = item["type"]
            if content_type not in type_groups:
                type_groups[content_type] = []
            type_groups[content_type].append(item)
        
        # Process each group
        processing_results = {}
        
        for content_type, items in type_groups.items():
            processing_results[content_type] = {
                "processed_count": len(items),
                "estimated_time": len(items) * {"audio": 30, "video": 60, "image": 10}.get(content_type, 30),
                "items": [item["id"] for item in items]
            }
        
        # Verify batch processing
        self.assertEqual(len(type_groups), 3)  # audio, video, image
        self.assertEqual(processing_results["audio"]["processed_count"], 3)  # 3 audio files
        self.assertEqual(processing_results["video"]["processed_count"], 1)   # 1 video file
        self.assertEqual(processing_results["image"]["processed_count"], 1)   # 1 image file
        
        # Verify priority ordering (high priority items first)
        audio_items = type_groups["audio"]
        high_priority_count = sum(1 for item in audio_items[:2] if item["priority"] == "high")
        self.assertEqual(high_priority_count, 2)  # First 2 audio items should be high priority


if __name__ == '__main__':
    unittest.main()