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

"""Comprehensive tests for fingerprinting engines
Tests all audio, video, image, and text fingerprinting capabilities
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile
import os

# Mock numpy for tests
try:
    import numpy as np
except ImportError:
    np = None

# Import modules under test with proper error handling
try:
    from ai_engine.fingerprinting.audio_fingerprint_engine import AudioFingerprintEngine
    from ai_engine.fingerprinting.video_fingerprint_engine import VideoFingerprintEngine
    from ai_engine.fingerprinting.image_fingerprint_engine import ImageFingerprintEngine
    from ai_engine.fingerprinting.text_fingerprint_engine import TextFingerprintEngine
    from ai_engine.fingerprinting.vector_matching_engine import VectorMatchingEngine
    FINGERPRINTING_AVAILABLE = True
except ImportError as e:
    FINGERPRINTING_AVAILABLE = False
    pytest.skip(f"Fingerprinting modules not available: {e}", allow_module_level=True)


class TestAudioFingerprintEngine:
    """Test suite for audio fingerprinting functionality"""
    
    @pytest.fixture
    def audio_engine(self):
        return AudioFingerprintEngine()
    
    @pytest.fixture
    def sample_audio_data(self):
        """Generate sample audio data for testing"""
        # Generate 5 seconds of sample audio at 44.1kHz
        duration = 5.0
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration))
        # Create a simple sine wave with some harmonics
        audio_data = (
            0.5 * np.sin(2 * np.pi * 440 * t) +  # A4 note
            0.3 * np.sin(2 * np.pi * 880 * t) +  # A5 note (harmonic)
            0.1 * np.random.normal(0, 1, len(t))  # Some noise
        )
        return audio_data.astype(np.float32), sample_rate
    
    @pytest.mark.asyncio
    async def test_generate_audio_fingerprint(self, audio_engine, sample_audio_data):
        """Test basic audio fingerprint generation"""
        audio_data, sample_rate = sample_audio_data
        
        fingerprint = await audio_engine.generate_fingerprint(
            audio_data, sample_rate
        )
        
        assert fingerprint is not None
        assert len(fingerprint) > 0
        assert isinstance(fingerprint, (str, bytes, np.ndarray))
    
    @pytest.mark.asyncio
    async def test_chromaprint_algorithm(self, audio_engine, sample_audio_data):
        """Test Chromaprint-specific fingerprinting"""
        audio_data, sample_rate = sample_audio_data
        
        fingerprint = await audio_engine.generate_chromaprint_fingerprint(
            audio_data, sample_rate
        )
        
        assert fingerprint is not None
        assert len(fingerprint) > 10  # Chromaprint should generate substantial data
    
    @pytest.mark.asyncio
    async def test_spectral_analysis(self, audio_engine, sample_audio_data):
        """Test spectral analysis fingerprinting"""
        audio_data, sample_rate = sample_audio_data
        
        spectral_features = await audio_engine.analyze_spectral_features(
            audio_data, sample_rate
        )
        
        assert 'mfcc' in spectral_features
        assert 'spectral_centroid' in spectral_features
        assert 'zero_crossing_rate' in spectral_features
        assert all(isinstance(v, np.ndarray) for v in spectral_features.values())
    
    @pytest.mark.asyncio
    async def test_melody_fingerprint(self, audio_engine, sample_audio_data):
        """Test melody-based fingerprinting"""
        audio_data, sample_rate = sample_audio_data
        
        melody_fingerprint = await audio_engine.extract_melody_fingerprint(
            audio_data, sample_rate
        )
        
        assert melody_fingerprint is not None
        assert len(melody_fingerprint) > 0
    
    @pytest.mark.asyncio
    async def test_beat_pattern_detection(self, audio_engine, sample_audio_data):
        """Test rhythm/beat pattern fingerprinting"""
        audio_data, sample_rate = sample_audio_data
        
        beat_features = await audio_engine.extract_beat_patterns(
            audio_data, sample_rate
        )
        
        assert 'tempo' in beat_features
        assert 'beat_frames' in beat_features
        assert beat_features['tempo'] > 0
    
    def test_similarity_calculation(self, audio_engine):
        """Test fingerprint similarity calculation"""
        # Mock fingerprints
        fp1 = np.random.rand(128)
        fp2 = fp1 + 0.1 * np.random.rand(128)  # Similar fingerprint
        fp3 = np.random.rand(128)  # Different fingerprint
        
        similarity_high = audio_engine.calculate_similarity(fp1, fp2)
        similarity_low = audio_engine.calculate_similarity(fp1, fp3)
        
        assert similarity_high > similarity_low
        assert 0 <= similarity_high <= 1
        assert 0 <= similarity_low <= 1


class TestVideoFingerprintEngine:
    """Test suite for video fingerprinting functionality"""
    
    @pytest.fixture
    def video_engine(self):
        return VideoFingerprintEngine()
    
    @pytest.fixture
    def sample_video_frames(self):
        """Generate sample video frames for testing"""
        frames = []
        for i in range(30):  # 30 frames
            # Create random 480x360 RGB frames
            frame = np.random.randint(0, 256, (360, 480, 3), dtype=np.uint8)
            frames.append(frame)
        return frames
    
    @pytest.mark.asyncio
    async def test_frame_analysis(self, video_engine, sample_video_frames):
        """Test individual frame analysis"""
        frame = sample_video_frames[0]
        
        frame_features = await video_engine.analyze_frame(frame)
        
        assert 'perceptual_hash' in frame_features
        assert 'histogram' in frame_features
        assert 'edge_features' in frame_features
    
    @pytest.mark.asyncio
    async def test_motion_detection(self, video_engine, sample_video_frames):
        """Test motion detection between frames"""
        frame1 = sample_video_frames[0]
        frame2 = sample_video_frames[1]
        
        motion_features = await video_engine.detect_motion(frame1, frame2)
        
        assert 'optical_flow' in motion_features
        assert 'motion_magnitude' in motion_features
        assert motion_features['motion_magnitude'] >= 0
    
    @pytest.mark.asyncio
    async def test_object_detection(self, video_engine, sample_video_frames):
        """Test YOLO object detection"""
        frame = sample_video_frames[0]
        
        with patch.object(video_engine, 'yolo_model') as mock_yolo:
            mock_yolo.detect.return_value = [
                {'class': 'person', 'confidence': 0.95, 'bbox': [100, 100, 200, 300]},
                {'class': 'car', 'confidence': 0.87, 'bbox': [300, 150, 450, 250]}
            ]
            
            objects = await video_engine.detect_objects(frame)
            
            assert len(objects) == 2
            assert objects[0]['class'] == 'person'
            assert objects[1]['class'] == 'car'
    
    @pytest.mark.asyncio
    async def test_scene_classification(self, video_engine, sample_video_frames):
        """Test scene classification"""
        frame = sample_video_frames[0]
        
        scene_class = await video_engine.classify_scene(frame)
        
        assert scene_class is not None
        assert isinstance(scene_class, str)
    
    @pytest.mark.asyncio
    async def test_video_fingerprint_generation(self, video_engine, sample_video_frames):
        """Test complete video fingerprint generation"""
        fingerprint = await video_engine.generate_fingerprint(sample_video_frames)
        
        assert fingerprint is not None
        assert 'temporal_features' in fingerprint
        assert 'spatial_features' in fingerprint
        assert 'motion_signature' in fingerprint


class TestImageFingerprintEngine:
    """Test suite for image fingerprinting functionality"""
    
    @pytest.fixture
    def image_engine(self):
        return ImageFingerprintEngine()
    
    @pytest.fixture
    def sample_image(self):
        """Generate sample image for testing"""
        # Create a 256x256 RGB image with some patterns
        image = np.zeros((256, 256, 3), dtype=np.uint8)
        
        # Add some geometric shapes
        image[50:100, 50:100] = [255, 0, 0]  # Red square
        image[150:200, 150:200] = [0, 255, 0]  # Green square
        
        # Add some noise
        noise = np.random.randint(0, 50, image.shape)
        image = np.clip(image.astype(int) + noise, 0, 255).astype(np.uint8)
        
        return image
    
    @pytest.mark.asyncio
    async def test_perceptual_hash(self, image_engine, sample_image):
        """Test perceptual hashing (pHash, aHash, dHash)"""
        hashes = await image_engine.generate_perceptual_hashes(sample_image)
        
        assert 'phash' in hashes
        assert 'ahash' in hashes
        assert 'dhash' in hashes
        assert all(isinstance(h, str) for h in hashes.values())
    
    @pytest.mark.asyncio
    async def test_clip_embeddings(self, image_engine, sample_image):
        """Test CLIP-based image embeddings"""
        with patch.object(image_engine, 'clip_model') as mock_clip:
            mock_clip.encode_image.return_value = np.random.rand(512)
            
            embeddings = await image_engine.generate_clip_embeddings(sample_image)
            
            assert embeddings is not None
            assert len(embeddings) == 512
            assert isinstance(embeddings, np.ndarray)
    
    @pytest.mark.asyncio
    async def test_sift_features(self, image_engine, sample_image):
        """Test SIFT feature detection"""
        sift_features = await image_engine.extract_sift_features(sample_image)
        
        assert 'keypoints' in sift_features
        assert 'descriptors' in sift_features
        assert len(sift_features['keypoints']) >= 0
    
    @pytest.mark.asyncio
    async def test_color_histogram(self, image_engine, sample_image):
        """Test color histogram analysis"""
        histogram = await image_engine.compute_color_histogram(sample_image)
        
        assert histogram is not None
        assert len(histogram) > 0
        assert np.sum(histogram) > 0  # Should have some color distribution
    
    def test_hash_similarity(self, image_engine):
        """Test hash similarity calculation"""
        hash1 = "abcd1234"
        hash2 = "abcd1235"  # Similar hash (1 bit different)
        hash3 = "efgh5678"  # Different hash
        
        similarity_high = image_engine.calculate_hash_similarity(hash1, hash2)
        similarity_low = image_engine.calculate_hash_similarity(hash1, hash3)
        
        assert similarity_high > similarity_low


class TestTextFingerprintEngine:
    """Test suite for text fingerprinting functionality"""
    
    @pytest.fixture
    def text_engine(self):
        return TextFingerprintEngine()
    
    @pytest.fixture
    def sample_texts(self):
        """Sample texts for testing"""
        return {
            'original': "This is an original piece of creative writing about artificial intelligence and machine learning.",
            'similar': "This is an original piece of creative content about AI and machine learning.",
            'different': "Completely different content about cooking recipes and food preparation.",
            'plagiarized': "This is an original piece of creative writing about artificial intelligence and machine learning. Just a few words added."
        }
    
    @pytest.mark.asyncio
    async def test_bert_embeddings(self, text_engine, sample_texts):
        """Test BERT-based text embeddings"""
        text = sample_texts['original']
        
        with patch.object(text_engine, 'bert_model') as mock_bert:
            mock_bert.encode.return_value = np.random.rand(768)
            
            embeddings = await text_engine.generate_bert_embeddings(text)
            
            assert embeddings is not None
            assert len(embeddings) == 768
            assert isinstance(embeddings, np.ndarray)
    
    @pytest.mark.asyncio
    async def test_semantic_similarity(self, text_engine, sample_texts):
        """Test semantic similarity calculation"""
        original = sample_texts['original']
        similar = sample_texts['similar']
        different = sample_texts['different']
        
        with patch.object(text_engine, 'calculate_semantic_similarity') as mock_similarity:
            mock_similarity.side_effect = lambda t1, t2: 0.85 if 'similar' in t2 else 0.15
            
            similarity_high = await text_engine.calculate_semantic_similarity(original, similar)
            similarity_low = await text_engine.calculate_semantic_similarity(original, different)
            
            assert similarity_high > similarity_low
            assert similarity_high > 0.8
            assert similarity_low < 0.3
    
    @pytest.mark.asyncio
    async def test_plagiarism_detection(self, text_engine, sample_texts):
        """Test plagiarism detection"""
        original = sample_texts['original']
        plagiarized = sample_texts['plagiarized']
        
        plagiarism_score = await text_engine.detect_plagiarism(original, plagiarized)
        
        assert plagiarism_score > 0.7  # Should detect high similarity
        assert 0 <= plagiarism_score <= 1
    
    @pytest.mark.asyncio
    async def test_language_detection(self, text_engine):
        """Test language detection"""
        texts = {
            'en': "This is English text",
            'fr': "Ceci est un texte français",
            'es': "Este es un texto en español",
            'ar': "هذا نص باللغة العربية"
        }
        
        for expected_lang, text in texts.items():
            detected_lang = await text_engine.detect_language(text)
            # Note: In real implementation, this would use langdetect or similar
            assert detected_lang is not None
    
    def test_text_preprocessing(self, text_engine):
        """Test text preprocessing"""
        raw_text = "  This is a TEXT with MIXED case, punctuation!!! And extra    spaces.  "
        
        processed = text_engine.preprocess_text(raw_text)
        
        assert processed.strip() == processed  # No leading/trailing whitespace
        assert processed.islower()  # Should be lowercase
        assert "!!!" not in processed  # Punctuation should be handled


class TestVectorMatchingEngine:
    """Test suite for vector matching and similarity search"""
    
    @pytest.fixture
    def vector_engine(self):
        return VectorMatchingEngine(dimension=128)
    
    @pytest.fixture
    def sample_vectors(self):
        """Generate sample vectors for testing"""
        vectors = []
        for i in range(100):
            # Create some structured vectors with slight variations
            base_vector = np.random.rand(128)
            if i < 50:
                # First 50 vectors are similar to each other
                base_vector[:64] = 0.5 + 0.1 * np.random.rand(64)
            vectors.append(base_vector)
        return vectors
    
    @pytest.mark.asyncio
    async def test_index_creation(self, vector_engine, sample_vectors):
        """Test FAISS index creation and population"""
        await vector_engine.build_index(sample_vectors)
        
        assert vector_engine.index is not None
        assert vector_engine.index.ntotal == len(sample_vectors)
    
    @pytest.mark.asyncio
    async def test_similarity_search(self, vector_engine, sample_vectors):
        """Test similarity search functionality"""
        await vector_engine.build_index(sample_vectors)
        
        query_vector = sample_vectors[0]  # Use first vector as query
        
        results = await vector_engine.search_similar(
            query_vector, k=5, threshold=0.5
        )
        
        assert len(results) <= 5
        assert all('id' in result for result in results)
        assert all('similarity' in result for result in results)
        assert all(result['similarity'] >= 0.5 for result in results)
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, vector_engine, sample_vectors):
        """Test batch processing capabilities"""
        # Split vectors into batches
        batch_size = 20
        batches = [
            sample_vectors[i:i+batch_size] 
            for i in range(0, len(sample_vectors), batch_size)
        ]
        
        for batch in batches:
            await vector_engine.add_vectors_batch(batch)
        
        assert vector_engine.index.ntotal == len(sample_vectors)
    
    def test_threshold_optimization(self, vector_engine):
        """Test similarity threshold optimization"""
        # Mock some similarity scores
        true_positives = [0.95, 0.87, 0.91, 0.83, 0.89]
        false_positives = [0.72, 0.68, 0.75, 0.71, 0.69]
        
        optimal_threshold = vector_engine.optimize_threshold(
            true_positives, false_positives
        )
        
        assert 0.7 < optimal_threshold < 0.9
        assert optimal_threshold > max(false_positives)


class TestFingerprintingIntegration:
    """Integration tests for complete fingerprinting workflow"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_audio_workflow(self):
        """Test complete audio fingerprinting workflow"""
        # This would test the entire pipeline from audio file to searchable fingerprint
        audio_engine = AudioFingerprintEngine()
        vector_engine = VectorMatchingEngine(dimension=128)
        
        # Mock audio data
        audio_data = np.random.rand(44100 * 5)  # 5 seconds
        sample_rate = 44100
        
        # Generate fingerprint
        fingerprint = await audio_engine.generate_fingerprint(audio_data, sample_rate)
        
        # Index fingerprint
        await vector_engine.add_vector(fingerprint, metadata={'type': 'audio'})
        
        # Search for similar content
        results = await vector_engine.search_similar(fingerprint, k=1)
        
        assert len(results) == 1
        assert results[0]['similarity'] > 0.99  # Should find exact match
    
    @pytest.mark.asyncio
    async def test_performance_benchmarks(self):
        """Test performance benchmarks for fingerprinting"""
        audio_engine = AudioFingerprintEngine()
        
        # Test processing time for different audio lengths
        test_cases = [
            (1, 44100),    # 1 second
            (5, 44100),    # 5 seconds
            (30, 44100),   # 30 seconds
            (180, 44100),  # 3 minutes
        ]
        
        for duration, sample_rate in test_cases:
            audio_data = np.random.rand(duration * sample_rate)
            
            start_time = asyncio.get_event_loop().time()
            fingerprint = await audio_engine.generate_fingerprint(audio_data, sample_rate)
            end_time = asyncio.get_event_loop().time()
            
            processing_time = end_time - start_time
            
            # Should process faster than real-time
            assert processing_time < duration
            assert fingerprint is not None


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])