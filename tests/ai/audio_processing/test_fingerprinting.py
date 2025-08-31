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
🧪 Audio Fingerprinting Tests - Industrial-Grade Copyright Protection Testing

Comprehensive testing for audio fingerprinting and content identification including:
- SpectralLandmarkExtractor validation
- AudioFingerprinter testing
- ContentMatcher accuracy testing
- Copyright protection validation
- Database operations testing
- Performance benchmarking

Created by Expert Team: Security Specialist + ML Engineer + Audio Developer
© 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import sys
import os
from pathlib import Path
import numpy as np
import tempfile
import time
import psutil
import os
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the audio processing module
try:
    from ai.audio_processing.fingerprinting import (
        SpectralLandmarkExtractor, AudioFingerprinter, 
        ContentMatcher, FingerprintResult, MatchResult
    )
    from ai.audio_processing.core import AudioProcessor
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))
    from ai.audio_processing.fingerprinting import (
        SpectralLandmarkExtractor, AudioFingerprinter, 
        ContentMatcher, FingerprintResult, MatchResult
    )
    from ai.audio_processing.core import AudioProcessor

from . import TEST_CONFIG, setup_test_environment


class TestSpectralLandmarkExtractor:
    """
    Industrial-grade testing for SpectralLandmarkExtractor class
    
    Test Coverage:
    - Spectrogram computation validation
    - Peak detection accuracy
    - Landmark extraction consistency
    - Noise robustness testing
    - Performance optimization
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test"""
        setup_test_environment()
        self.extractor = SpectralLandmarkExtractor()
        self.processor = AudioProcessor()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
    
    def test_initialization(self):
        """Test SpectralLandmarkExtractor initialization"""
        extractor = SpectralLandmarkExtractor()
        assert extractor is not None
        assert hasattr(extractor, 'sample_rate')
        assert hasattr(extractor, 'window_size')
        assert hasattr(extractor, 'hop_size')
        assert hasattr(extractor, 'peak_threshold')
    
    def test_compute_spectrogram(self):
        """Test spectrogram computation"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        spectrogram = self.extractor.compute_spectrogram(audio_data, sample_rate)
        
        assert spectrogram is not None
        assert isinstance(spectrogram, np.ndarray)
        assert spectrogram.ndim == 2  # Frequency x Time
        assert spectrogram.dtype == np.float32
        assert not np.isnan(spectrogram).any()
        assert not np.isinf(spectrogram).any()
        assert spectrogram.shape[0] > 0  # Frequency bins
        assert spectrogram.shape[1] > 0  # Time frames
    
    def test_find_peaks(self):
        """Test peak detection in spectrogram"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        spectrogram = self.extractor.compute_spectrogram(audio_data, sample_rate)
        peaks = self.extractor.find_peaks(spectrogram)
        
        assert peaks is not None
        assert isinstance(peaks, list)
        assert len(peaks) > 0  # Should find peaks in pure tone
        
        # Each peak should have frequency and time coordinates
        for peak in peaks:
            assert isinstance(peak, tuple)
            assert len(peak) == 2  # (freq_bin, time_frame)
            assert isinstance(peak[0], int)
            assert isinstance(peak[1], int)
            assert 0 <= peak[0] < spectrogram.shape[0]
            assert 0 <= peak[1] < spectrogram.shape[1]
    
    def test_extract_landmarks(self):
        """Test landmark extraction"""
        audio_file = self.test_data_dir / "chirp_sweep.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        landmarks = self.extractor.extract_landmarks(audio_data, sample_rate)
        
        assert landmarks is not None
        assert isinstance(landmarks, list)
        assert len(landmarks) > 0  # Should extract landmarks from chirp
        
        # Each landmark should have required fields
        for landmark in landmarks:
            assert isinstance(landmark, dict)
            assert 'freq1' in landmark
            assert 'freq2' in landmark
            assert 'time_delta' in landmark
            assert 'time_anchor' in landmark
            
            # Validate landmark values
            assert isinstance(landmark['freq1'], int)
            assert isinstance(landmark['freq2'], int)
            assert isinstance(landmark['time_delta'], int)
            assert isinstance(landmark['time_anchor'], int)
            assert landmark['freq1'] >= 0
            assert landmark['freq2'] >= 0
            assert landmark['time_delta'] > 0
            assert landmark['time_anchor'] >= 0
    
    def test_landmark_consistency(self):
        """Test landmark extraction consistency"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        # Extract landmarks multiple times
        landmarks1 = self.extractor.extract_landmarks(audio_data, sample_rate)
        landmarks2 = self.extractor.extract_landmarks(audio_data, sample_rate)
        
        assert len(landmarks1) == len(landmarks2)
        
        # Landmarks should be identical for same input
        for lm1, lm2 in zip(landmarks1, landmarks2):
            assert lm1['freq1'] == lm2['freq1']
            assert lm1['freq2'] == lm2['freq2']
            assert lm1['time_delta'] == lm2['time_delta']
            assert lm1['time_anchor'] == lm2['time_anchor']
    
    def test_noise_robustness(self):
        """Test robustness to noise"""
        # Load clean audio
        clean_file = self.test_data_dir / "pure_tone_440hz.wav"
        clean_audio, sample_rate = self.processor.load_audio(str(clean_file))
        
        # Add noise
        noise = np.random.normal(0, 0.1, len(clean_audio))
        noisy_audio = clean_audio + noise
        
        # Extract landmarks from both
        clean_landmarks = self.extractor.extract_landmarks(clean_audio, sample_rate)
        noisy_landmarks = self.extractor.extract_landmarks(noisy_audio, sample_rate)
        
        # Should still extract significant landmarks from noisy version
        assert len(noisy_landmarks) > 0
        assert len(noisy_landmarks) >= len(clean_landmarks) * 0.5  # At least 50% preserved
    
    def test_different_audio_types(self):
        """Test landmark extraction for different audio types"""
        audio_files = {
            "tone": "pure_tone_440hz.wav",
            "noise": "white_noise.wav",
            "chirp": "chirp_sweep.wav"
        }
        
        landmarks_counts = {}
        for audio_type, filename in audio_files.items():
            audio_file = self.test_data_dir / filename
            audio_data, sample_rate = self.processor.load_audio(str(audio_file))
            landmarks = self.extractor.extract_landmarks(audio_data, sample_rate)
            landmarks_counts[audio_type] = len(landmarks)
        
        # Different audio types should have different landmark counts
        assert landmarks_counts["tone"] > 0
        assert landmarks_counts["chirp"] > landmarks_counts["tone"]  # Chirp should have more landmarks
        assert landmarks_counts["noise"] > 0
    
    def test_performance_benchmarking(self):
        """Test landmark extraction performance"""
        audio_file = self.test_data_dir / "chirp_sweep.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        start_time = time.time()
        landmarks = self.extractor.extract_landmarks(audio_data, sample_rate)
        end_time = time.time()
        
        processing_time_ms = (end_time - start_time) * 1000
        
        assert processing_time_ms < TEST_CONFIG["performance_threshold_ms"] * 2  # Allow 2x for fingerprinting
        assert len(landmarks) > 0


class TestAudioFingerprinter:
    """
    Industrial-grade testing for AudioFingerprinter class
    
    Test Coverage:
    - Fingerprint generation validation
    - Hash computation accuracy
    - Database storage testing
    - Fingerprint uniqueness
    - Collision detection
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test"""
        setup_test_environment()
        
        # Create temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        
        self.fingerprinter = AudioFingerprinter(database_path=self.temp_db_path)
        self.processor = AudioProcessor()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
    
    def teardown_method(self):
        """Cleanup test environment"""
        if os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)
    
    def test_initialization(self):
        """Test AudioFingerprinter initialization"""
        fingerprinter = AudioFingerprinter(database_path=self.temp_db_path)
        assert fingerprinter is not None
        assert hasattr(fingerprinter, 'database_path')
        assert hasattr(fingerprinter, 'extractor')
        assert os.path.exists(self.temp_db_path)
    
    def test_generate_fingerprint(self):
        """Test fingerprint generation"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        fingerprint_result = self.fingerprinter.generate_fingerprint(
            audio_data, 
            sample_rate,
            track_id="test_track_001"
        )
        
        assert fingerprint_result is not None
        assert isinstance(fingerprint_result, FingerprintResult)
        assert fingerprint_result.track_id == "test_track_001"
        assert fingerprint_result.num_hashes > 0
        assert fingerprint_result.duration > 0
        assert isinstance(fingerprint_result.hashes, list)
        assert len(fingerprint_result.hashes) == fingerprint_result.num_hashes
        
        # Each hash should be valid
        for hash_item in fingerprint_result.hashes:
            assert isinstance(hash_item, dict)
            assert 'hash' in hash_item
            assert 'time_offset' in hash_item
            assert isinstance(hash_item['hash'], int)
            assert isinstance(hash_item['time_offset'], (int, float))
            assert hash_item['time_offset'] >= 0
    
    def test_store_fingerprint(self):
        """Test fingerprint storage in database"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        fingerprint_result = self.fingerprinter.generate_fingerprint(
            audio_data, 
            sample_rate,
            track_id="test_store_001"
        )
        
        # Store fingerprint
        success = self.fingerprinter.store_fingerprint(fingerprint_result)
        assert success is True
        
        # Verify storage in database
        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()
        
        # Check tracks table
        cursor.execute("SELECT * FROM tracks WHERE track_id = ?", ("test_store_001",))
        track_row = cursor.fetchone()
        assert track_row is not None
        
        # Check fingerprints table
        cursor.execute("SELECT COUNT(*) FROM fingerprints WHERE track_id = ?", ("test_store_001",))
        count = cursor.fetchone()[0]
        assert count == fingerprint_result.num_hashes
        
        conn.close()
    
    def test_fingerprint_uniqueness(self):
        """Test fingerprint uniqueness for different audio"""
        audio_files = [
            ("pure_tone_440hz.wav", "track_001"),
            ("white_noise.wav", "track_002"),
            ("chirp_sweep.wav", "track_003")
        ]
        
        fingerprints = {}
        for filename, track_id in audio_files:
            audio_file = self.test_data_dir / filename
            audio_data, sample_rate = self.processor.load_audio(str(audio_file))
            
            fingerprint_result = self.fingerprinter.generate_fingerprint(
                audio_data, 
                sample_rate,
                track_id=track_id
            )
            fingerprints[track_id] = set(hash_item['hash'] for hash_item in fingerprint_result.hashes)
        
        # Check that fingerprints are different
        track_ids = list(fingerprints.keys())
        for i in range(len(track_ids)):
            for j in range(i + 1, len(track_ids)):
                track1, track2 = track_ids[i], track_ids[j]
                
                # Calculate overlap
                overlap = len(fingerprints[track1] & fingerprints[track2])
                total = len(fingerprints[track1] | fingerprints[track2])
                overlap_ratio = overlap / total if total > 0 else 0
                
                # Different audio should have low fingerprint overlap
                assert overlap_ratio < 0.1  # Less than 10% overlap
    
    def test_fingerprint_reproducibility(self):
        """Test fingerprint reproducibility"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        # Generate fingerprint multiple times
        fingerprint1 = self.fingerprinter.generate_fingerprint(
            audio_data, sample_rate, track_id="repro_test_1"
        )
        fingerprint2 = self.fingerprinter.generate_fingerprint(
            audio_data, sample_rate, track_id="repro_test_2"
        )
        
        # Should be identical
        assert fingerprint1.num_hashes == fingerprint2.num_hashes
        
        hashes1 = set(hash_item['hash'] for hash_item in fingerprint1.hashes)
        hashes2 = set(hash_item['hash'] for hash_item in fingerprint2.hashes)
        assert hashes1 == hashes2
    
    def test_fingerprint_with_noise(self):
        """Test fingerprint robustness with noise"""
        # Load clean audio
        clean_file = self.test_data_dir / "pure_tone_440hz.wav"
        clean_audio, sample_rate = self.processor.load_audio(str(clean_file))
        
        # Add noise
        noise_levels = [0.05, 0.1, 0.2]
        
        clean_fingerprint = self.fingerprinter.generate_fingerprint(
            clean_audio, sample_rate, track_id="clean"
        )
        clean_hashes = set(hash_item['hash'] for hash_item in clean_fingerprint.hashes)
        
        for noise_level in noise_levels:
            noise = np.random.normal(0, noise_level, len(clean_audio))
            noisy_audio = clean_audio + noise
            
            noisy_fingerprint = self.fingerprinter.generate_fingerprint(
                noisy_audio, sample_rate, track_id=f"noisy_{noise_level}"
            )
            noisy_hashes = set(hash_item['hash'] for hash_item in noisy_fingerprint.hashes)
            
            # Should maintain substantial overlap with clean version
            overlap = len(clean_hashes & noisy_hashes)
            total = len(clean_hashes)
            overlap_ratio = overlap / total if total > 0 else 0
            
            # Even with noise, should maintain > 30% overlap for robustness
            assert overlap_ratio > 0.3, f"Overlap ratio {overlap_ratio} too low for noise level {noise_level}"
    
    def test_database_operations(self):
        """Test database operations"""
        # Store multiple fingerprints
        audio_files = [
            ("pure_tone_440hz.wav", "db_test_001"),
            ("white_noise.wav", "db_test_002")
        ]
        
        for filename, track_id in audio_files:
            audio_file = self.test_data_dir / filename
            audio_data, sample_rate = self.processor.load_audio(str(audio_file))
            
            fingerprint_result = self.fingerprinter.generate_fingerprint(
                audio_data, sample_rate, track_id=track_id
            )
            success = self.fingerprinter.store_fingerprint(fingerprint_result)
            assert success is True
        
        # Test database integrity
        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()
        
        # Check total tracks
        cursor.execute("SELECT COUNT(*) FROM tracks")
        track_count = cursor.fetchone()[0]
        assert track_count == len(audio_files)
        
        # Check total fingerprints
        cursor.execute("SELECT COUNT(*) FROM fingerprints")
        fingerprint_count = cursor.fetchone()[0]
        assert fingerprint_count > 0
        
        conn.close()


class TestContentMatcher:
    """
    Industrial-grade testing for ContentMatcher class
    
    Test Coverage:
    - Content matching accuracy
    - Query processing validation
    - Match ranking testing
    - Performance optimization
    - False positive/negative rates
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test"""
        setup_test_environment()
        
        # Create temporary database with test data
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        
        self.fingerprinter = AudioFingerprinter(database_path=self.temp_db_path)
        self.matcher = ContentMatcher(database_path=self.temp_db_path)
        self.processor = AudioProcessor()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
        
        # Populate database with test fingerprints
        self._populate_test_database()
    
    def teardown_method(self):
        """Cleanup test environment"""
        if os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)
    
    def _populate_test_database(self):
        """Populate database with test fingerprints"""
        audio_files = [
            ("pure_tone_440hz.wav", "reference_tone"),
            ("white_noise.wav", "reference_noise"),
            ("chirp_sweep.wav", "reference_chirp"),
            ("silence.wav", "reference_silence")
        ]
        
        for filename, track_id in audio_files:
            audio_file = self.test_data_dir / filename
            audio_data, sample_rate = self.processor.load_audio(str(audio_file))
            
            fingerprint_result = self.fingerprinter.generate_fingerprint(
                audio_data, sample_rate, track_id=track_id
            )
            self.fingerprinter.store_fingerprint(fingerprint_result)
    
    def test_initialization(self):
        """Test ContentMatcher initialization"""
        matcher = ContentMatcher(database_path=self.temp_db_path)
        assert matcher is not None
        assert hasattr(matcher, 'database_path')
        assert hasattr(matcher, 'threshold')
        assert os.path.exists(self.temp_db_path)
    
    def test_find_matches_exact(self):
        """Test finding exact matches"""
        # Use same audio as in database
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        matches = self.matcher.find_matches(audio_data, sample_rate, threshold=0.1)
        
        assert matches is not None
        assert isinstance(matches, list)
        assert len(matches) > 0
        
        # Should find the exact match
        best_match = matches[0]
        assert isinstance(best_match, MatchResult)
        assert best_match.track_id == "reference_tone"
        assert best_match.confidence > 0.5  # High confidence for exact match
        assert best_match.offset_seconds >= 0
    
    def test_find_matches_partial(self):
        """Test finding matches with partial audio"""
        # Use subset of audio from database
        audio_file = self.test_data_dir / "chirp_sweep.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        # Take middle portion
        start_idx = len(audio_data) // 4
        end_idx = 3 * len(audio_data) // 4
        partial_audio = audio_data[start_idx:end_idx]
        
        matches = self.matcher.find_matches(partial_audio, sample_rate, threshold=0.1)
        
        assert matches is not None
        assert len(matches) > 0
        
        # Should still find the match
        found_reference = any(match.track_id == "reference_chirp" for match in matches)
        assert found_reference, "Should find reference chirp in partial audio"
    
    def test_find_matches_with_noise(self):
        """Test finding matches with noisy audio"""
        # Load clean audio and add noise
        clean_file = self.test_data_dir / "pure_tone_440hz.wav"
        clean_audio, sample_rate = self.processor.load_audio(str(clean_file))
        
        # Add moderate noise
        noise = np.random.normal(0, 0.1, len(clean_audio))
        noisy_audio = clean_audio + noise
        
        matches = self.matcher.find_matches(noisy_audio, sample_rate, threshold=0.05)
        
        assert matches is not None
        # Should still find the match despite noise
        found_reference = any(match.track_id == "reference_tone" for match in matches)
        assert found_reference, "Should find reference tone despite noise"
    
    def test_no_matches_for_new_content(self):
        """Test that new content doesn't produce false matches"""
        # Create completely different audio
        new_audio = np.sin(2 * np.pi * 880 * np.linspace(0, 1, 44100))  # 880Hz tone
        
        matches = self.matcher.find_matches(new_audio, 44100, threshold=0.3)
        
        # Should have few or no high-confidence matches
        high_confidence_matches = [m for m in matches if m.confidence > 0.5]
        assert len(high_confidence_matches) == 0, "Should not find high-confidence matches for new content"
    
    def test_match_ranking(self):
        """Test match result ranking"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        matches = self.matcher.find_matches(audio_data, sample_rate, threshold=0.05)
        
        assert len(matches) > 0
        
        # Matches should be sorted by confidence (descending)
        for i in range(len(matches) - 1):
            assert matches[i].confidence >= matches[i + 1].confidence
        
        # Best match should be the exact reference
        assert matches[0].track_id == "reference_tone"
    
    def test_threshold_filtering(self):
        """Test confidence threshold filtering"""
        audio_file = self.test_data_dir / "white_noise.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        # Test with different thresholds
        low_threshold_matches = self.matcher.find_matches(audio_data, sample_rate, threshold=0.1)
        high_threshold_matches = self.matcher.find_matches(audio_data, sample_rate, threshold=0.5)
        
        # Higher threshold should return fewer matches
        assert len(high_threshold_matches) <= len(low_threshold_matches)
        
        # All matches should meet threshold
        for match in high_threshold_matches:
            assert match.confidence >= 0.5
    
    def test_performance_benchmarking(self):
        """Test matching performance"""
        audio_file = self.test_data_dir / "chirp_sweep.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        start_time = time.time()
        matches = self.matcher.find_matches(audio_data, sample_rate, threshold=0.1)
        end_time = time.time()
        
        search_time_ms = (end_time - start_time) * 1000
        
        assert search_time_ms < TEST_CONFIG["performance_threshold_ms"] * 5  # Allow 5x for database search
        assert matches is not None
    
    def test_batch_matching(self):
        """Test batch content matching"""
        audio_files = [
            "pure_tone_440hz.wav",
            "white_noise.wav", 
            "chirp_sweep.wav"
        ]
        
        batch_audio = []
        for filename in audio_files:
            audio_file = self.test_data_dir / filename
            audio_data, sample_rate = self.processor.load_audio(str(audio_file))
            batch_audio.append(audio_data)
        
        batch_results = self.matcher.find_batch_matches(batch_audio, sample_rate, threshold=0.1)
        
        assert batch_results is not None
        assert len(batch_results) == len(audio_files)
        
        # Each should find its corresponding reference
        expected_references = ["reference_tone", "reference_noise", "reference_chirp"]
        for i, (results, expected_ref) in enumerate(zip(batch_results, expected_references)):
            found_ref = any(match.track_id == expected_ref for match in results)
            assert found_ref, f"Should find {expected_ref} for batch item {i}"


class TestFingerprintResult:
    """Test FingerprintResult data structure"""
    
    def test_fingerprint_result_creation(self):
        """Test FingerprintResult creation"""
        hashes = [
            {'hash': 12345, 'time_offset': 0.5},
            {'hash': 67890, 'time_offset': 1.0}
        ]
        
        result = FingerprintResult(
            track_id="test_track",
            num_hashes=2,
            duration=5.0,
            hashes=hashes
        )
        
        assert result.track_id == "test_track"
        assert result.num_hashes == 2
        assert result.duration == 5.0
        assert result.hashes == hashes
    
    def test_fingerprint_result_serialization(self):
        """Test FingerprintResult serialization"""
        hashes = [{'hash': 12345, 'time_offset': 0.5}]
        
        result = FingerprintResult(
            track_id="test_track",
            num_hashes=1,
            duration=3.0,
            hashes=hashes
        )
        
        serialized = result.to_dict()
        
        assert isinstance(serialized, dict)
        assert serialized['track_id'] == "test_track"
        assert serialized['num_hashes'] == 1
        assert serialized['duration'] == 3.0
        assert serialized['hashes'] == hashes


class TestMatchResult:
    """Test MatchResult data structure"""
    
    def test_match_result_creation(self):
        """Test MatchResult creation"""
        result = MatchResult(
            track_id="matched_track",
            confidence=0.85,
            offset_seconds=2.5,
            num_matches=15
        )
        
        assert result.track_id == "matched_track"
        assert result.confidence == 0.85
        assert result.offset_seconds == 2.5
        assert result.num_matches == 15
    
    def test_match_result_comparison(self):
        """Test MatchResult comparison for sorting"""
        result1 = MatchResult("track1", 0.9, 0.0, 20)
        result2 = MatchResult("track2", 0.7, 1.0, 15)
        result3 = MatchResult("track3", 0.95, 2.0, 25)
        
        results = [result1, result2, result3]
        sorted_results = sorted(results, reverse=True)  # Sort by confidence descending
        
        assert sorted_results[0].track_id == "track3"  # Highest confidence
        assert sorted_results[1].track_id == "track1"
        assert sorted_results[2].track_id == "track2"  # Lowest confidence


class TestFingerprintingIntegration:
    """
    Integration tests for fingerprinting workflow
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
        
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
    
    def teardown_method(self):
        """Cleanup test environment"""
        if os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)
    
    def test_complete_fingerprinting_workflow(self):
        """Test complete fingerprinting workflow"""
        processor = AudioProcessor()
        fingerprinter = AudioFingerprinter(database_path=self.temp_db_path)
        matcher = ContentMatcher(database_path=self.temp_db_path)
        
        # 1. Load and fingerprint reference audio
        ref_file = self.test_data_dir / "pure_tone_440hz.wav"
        ref_audio, sample_rate = processor.load_audio(str(ref_file))
        
        fingerprint_result = fingerprinter.generate_fingerprint(
            ref_audio, sample_rate, track_id="reference_track"
        )
        success = fingerprinter.store_fingerprint(fingerprint_result)
        assert success is True
        
        # 2. Query with same audio
        matches = matcher.find_matches(ref_audio, sample_rate, threshold=0.1)
        
        # 3. Verify workflow
        assert fingerprint_result is not None
        assert matches is not None
        assert len(matches) > 0
        assert matches[0].track_id == "reference_track"
        assert matches[0].confidence > 0.5
    
    def test_copyright_detection_scenario(self):
        """Test realistic copyright detection scenario"""
        processor = AudioProcessor()
        fingerprinter = AudioFingerprinter(database_path=self.temp_db_path)
        matcher = ContentMatcher(database_path=self.temp_db_path)
        
        # Store copyrighted content
        original_file = self.test_data_dir / "chirp_sweep.wav"
        original_audio, sample_rate = processor.load_audio(str(original_file))
        
        fingerprint_result = fingerprinter.generate_fingerprint(
            original_audio, sample_rate, track_id="copyrighted_song"
        )
        fingerprinter.store_fingerprint(fingerprint_result)
        
        # Simulate user upload with slight modifications
        modified_audio = original_audio * 0.8  # Volume change
        noise = np.random.normal(0, 0.05, len(original_audio))
        modified_audio += noise  # Add noise
        
        # Check for copyright match
        matches = matcher.find_matches(modified_audio, sample_rate, threshold=0.1)
        
        # Should detect the copyright violation
        assert len(matches) > 0
        copyright_match = any(match.track_id == "copyrighted_song" for match in matches)
        assert copyright_match, "Should detect copyrighted content despite modifications"


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
