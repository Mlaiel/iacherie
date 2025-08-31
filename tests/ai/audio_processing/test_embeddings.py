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

"""🧪 Audio Embeddings Tests - Industrial-Grade ML Testing Suite

Comprehensive testing for audio embeddings and similarity matching including:
- AudioEmbeddingModel validation
- AudioEmbeddingGenerator testing
- SimilarityMatcher accuracy testing
- Vector space validation
- Performance benchmarking
- Memory efficiency testing

Created by Expert Team: ML Engineer + AI Architect + Audio Developer
© 2025 Fahed Mlaiel. All rights reserved.
"""import pytest
import sys
import os
from pathlib import Path
import numpy as np
import tempfile
import time
import psutil
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from sklearn.metrics.pairwise import cosine_similarity

# Import the audio processing module
try:
    from ai.audio_processing.embeddings import (
        AudioEmbeddingModel, AudioEmbeddingGenerator, 
        SimilarityMatcher, SimilarityResult
    )
    from ai.audio_processing.core import AudioProcessor
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))
    from ai.audio_processing.embeddings import (
        AudioEmbeddingModel, AudioEmbeddingGenerator, 
        SimilarityMatcher, SimilarityResult
    )
    from ai.audio_processing.core import AudioProcessor

from . import TEST_CONFIG, setup_test_environment


class TestAudioEmbeddingModel:
    """    Industrial-grade testing for AudioEmbeddingModel class
    
    Test Coverage:
    - Model architecture validation
    - Forward pass testing
    - Embedding dimension consistency
    - Gradient flow validation
    - Model serialization/deserialization
    """    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test"""        setup_test_environment()
        self.embedding_model = AudioEmbeddingModel()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
    
    def test_model_initialization(self):
        """Test AudioEmbeddingModel initialization"""        model = AudioEmbeddingModel()
        assert model is not None
        assert hasattr(model, 'embedding_dim')
        assert hasattr(model, 'model')
        assert model.embedding_dim == 512  # Standard embedding dimension
    
    def test_model_architecture(self):
        """Test model architecture consistency"""        model = AudioEmbeddingModel()
        
        # Test with sample input
        sample_input = np.random.randn(1, 128, 128)  # Batch, freq, time
        embeddings = model.encode(sample_input)
        
        assert embeddings is not None
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (1, 512)  # Batch size, embedding dim
        assert embeddings.dtype == np.float32
    
    def test_embedding_consistency(self):
        """Test embedding consistency for same input"""        model = AudioEmbeddingModel()
        sample_input = np.random.randn(1, 128, 128)
        
        # Generate embeddings multiple times
        embedding1 = model.encode(sample_input)
        embedding2 = model.encode(sample_input)
        
        # Should be identical for same input
        assert np.allclose(embedding1, embedding2, atol=1e-6)
    
    def test_embedding_normalization(self):
        """Test embedding normalization"""        model = AudioEmbeddingModel()
        sample_input = np.random.randn(5, 128, 128)  # Batch of 5
        
        embeddings = model.encode(sample_input)
        
        # Check if embeddings are normalized
        norms = np.linalg.norm(embeddings, axis=1)
        assert np.allclose(norms, 1.0, atol=1e-5)  # Unit norm
    
    def test_batch_processing(self):
        """Test batch processing capabilities"""        model = AudioEmbeddingModel()
        
        # Test different batch sizes
        for batch_size in [1, 4, 8, 16]:
            sample_input = np.random.randn(batch_size, 128, 128)
            embeddings = model.encode(sample_input)
            
            assert embeddings.shape[0] == batch_size
            assert embeddings.shape[1] == 512
    
    def test_model_serialization(self):
        """Test model save/load functionality"""        model = AudioEmbeddingModel()
        
        # Create temporary file for model
        with tempfile.NamedTemporaryFile(suffix='.pth', delete=False) as tmp_file:
            model_path = tmp_file.name
        
        try:
            # Save model
            model.save_model(model_path)
            assert os.path.exists(model_path)
            
            # Load model
            loaded_model = AudioEmbeddingModel()
            loaded_model.load_model(model_path)
            
            # Test consistency
            sample_input = np.random.randn(1, 128, 128)
            original_embedding = model.encode(sample_input)
            loaded_embedding = loaded_model.encode(sample_input)
            
            assert np.allclose(original_embedding, loaded_embedding, atol=1e-6)
            
        finally:
            if os.path.exists(model_path):
                os.unlink(model_path)


class TestAudioEmbeddingGenerator:
    """    Industrial-grade testing for AudioEmbeddingGenerator class
    
    Test Coverage:
    - Audio preprocessing validation
    - Feature extraction testing
    - Embedding generation accuracy
    - Batch processing efficiency
    - Memory management
    """    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test"""        setup_test_environment()
        self.generator = AudioEmbeddingGenerator()
        self.processor = AudioProcessor()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
    
    def test_generator_initialization(self):
        """Test AudioEmbeddingGenerator initialization"""        generator = AudioEmbeddingGenerator()
        assert generator is not None
        assert hasattr(generator, 'model')
        assert hasattr(generator, 'preprocessing')
        assert hasattr(generator, 'embedding_dim')
    
    def test_generate_embeddings_single_audio(self):
        """Test embedding generation for single audio file"""        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        embeddings = self.generator.generate_embeddings(audio_data, sample_rate)
        
        assert embeddings is not None
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == 512  # Embedding dimension
        assert embeddings.dtype == np.float32
        assert not np.isnan(embeddings).any()
        
        # Check normalization
        norm = np.linalg.norm(embeddings)
        assert np.isclose(norm, 1.0, atol=1e-5)
    
    def test_generate_embeddings_batch(self):
        """Test batch embedding generation"""        # Load multiple audio files
        audio_files = [
            "pure_tone_440hz.wav",
            "white_noise.wav", 
            "chirp_sweep.wav",
            "silence.wav"
        ]
        
        audio_data_list = []
        for filename in audio_files:
            audio_file = self.test_data_dir / filename
            audio_data, _ = self.processor.load_audio(str(audio_file))
            audio_data_list.append(audio_data)
        
        batch_embeddings = self.generator.generate_batch_embeddings(
            audio_data_list, 
            sample_rate=44100
        )
        
        assert batch_embeddings is not None
        assert isinstance(batch_embeddings, np.ndarray)
        assert batch_embeddings.shape == (len(audio_files), 512)
        assert batch_embeddings.dtype == np.float32
        assert not np.isnan(batch_embeddings).any()
        
        # Check each embedding is normalized
        for i in range(len(audio_files)):
            norm = np.linalg.norm(batch_embeddings[i])
            assert np.isclose(norm, 1.0, atol=1e-5)
    
    def test_preprocessing_consistency(self):
        """Test preprocessing consistency"""        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        # Generate embeddings multiple times
        embedding1 = self.generator.generate_embeddings(audio_data, sample_rate)
        embedding2 = self.generator.generate_embeddings(audio_data, sample_rate)
        
        # Should be identical for same input
        assert np.allclose(embedding1, embedding2, atol=1e-6)
    
    def test_different_audio_types(self):
        """Test embedding generation for different audio types"""        audio_types = {
            "pure_tone": "pure_tone_440hz.wav",
            "noise": "white_noise.wav",
            "chirp": "chirp_sweep.wav",
            "silence": "silence.wav"
        }
        
        embeddings = {}
        for audio_type, filename in audio_types.items():
            audio_file = self.test_data_dir / filename
            audio_data, sample_rate = self.processor.load_audio(str(audio_file))
            embedding = self.generator.generate_embeddings(audio_data, sample_rate)
            embeddings[audio_type] = embedding
        
        # All embeddings should be different (except potentially silence)
        for type1 in embeddings:
            for type2 in embeddings:
                if type1 != type2 and type1 != "silence" and type2 != "silence":
                    similarity = cosine_similarity(
                        embeddings[type1].reshape(1, -1),
                        embeddings[type2].reshape(1, -1)
                    )[0, 0]
                    assert similarity < 0.9  # Should be distinct
    
    def test_memory_efficiency(self):
        """Test memory efficiency for large batch processing"""        # Create large batch of random audio data
        batch_size = 10
        audio_length = 220500  # 5 seconds at 44.1kHz
        large_batch = [np.random.randn(audio_length) for _ in range(batch_size)]
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate embeddings
        batch_embeddings = self.generator.generate_batch_embeddings(
            large_batch, 
            sample_rate=44100
        )
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        assert memory_increase < TEST_CONFIG["memory_limit_mb"]
        assert batch_embeddings.shape == (batch_size, 512)
    
    def test_performance_benchmarking(self):
        """Test embedding generation performance"""        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        start_time = time.time()
        embeddings = self.generator.generate_embeddings(audio_data, sample_rate)
        end_time = time.time()
        
        processing_time_ms = (end_time - start_time) * 1000
        
        assert processing_time_ms < TEST_CONFIG["performance_threshold_ms"] * 2  # Allow 2x for ML processing
        assert embeddings is not None


class TestSimilarityMatcher:
    """    Industrial-grade testing for SimilarityMatcher class
    
    Test Coverage:
    - Similarity computation accuracy
    - Distance metric validation
    - Ranking and retrieval testing
    - Performance optimization
    - Large database handling
    """    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test"""        setup_test_environment()
        self.matcher = SimilarityMatcher()
        self.generator = AudioEmbeddingGenerator()
        self.processor = AudioProcessor()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
        
        # Create test database of embeddings
        self._create_test_database()
    
    def _create_test_database(self):
        """Create test database of audio embeddings"""        audio_files = [
            "pure_tone_440hz.wav",
            "white_noise.wav", 
            "chirp_sweep.wav",
            "silence.wav"
        ]
        
        self.test_database = {}
        for filename in audio_files:
            audio_file = self.test_data_dir / filename
            audio_data, sample_rate = self.processor.load_audio(str(audio_file))
            embedding = self.generator.generate_embeddings(audio_data, sample_rate)
            self.test_database[filename] = embedding
    
    def test_matcher_initialization(self):
        """Test SimilarityMatcher initialization"""        matcher = SimilarityMatcher()
        assert matcher is not None
        assert hasattr(matcher, 'distance_metric')
        assert hasattr(matcher, 'threshold')
    
    def test_cosine_similarity_computation(self):
        """Test cosine similarity computation"""        embedding1 = self.test_database["pure_tone_440hz.wav"]
        embedding2 = self.test_database["white_noise.wav"]
        
        # Test self-similarity (should be 1.0)
        self_similarity = self.matcher.compute_similarity(embedding1, embedding1)
        assert np.isclose(self_similarity, 1.0, atol=1e-5)
        
        # Test similarity between different audio
        cross_similarity = self.matcher.compute_similarity(embedding1, embedding2)
        assert 0.0 <= cross_similarity <= 1.0
        assert cross_similarity < 1.0  # Should be less than self-similarity
    
    def test_euclidean_distance_computation(self):
        """Test Euclidean distance computation"""        matcher = SimilarityMatcher(distance_metric='euclidean')
        
        embedding1 = self.test_database["pure_tone_440hz.wav"]
        embedding2 = self.test_database["white_noise.wav"]
        
        # Test self-distance (should be 0.0)
        self_distance = matcher.compute_similarity(embedding1, embedding1)
        assert np.isclose(self_distance, 0.0, atol=1e-5)
        
        # Test distance between different audio
        cross_distance = matcher.compute_similarity(embedding1, embedding2)
        assert cross_distance >= 0.0
        assert cross_distance > 0.0  # Should be greater than self-distance
    
    def test_find_similar_embeddings(self):
        """Test finding similar embeddings"""        query_embedding = self.test_database["pure_tone_440hz.wav"]
        
        # Create database array
        database_embeddings = np.array(list(self.test_database.values()))
        database_labels = list(self.test_database.keys())
        
        similar_results = self.matcher.find_similar(
            query_embedding, 
            database_embeddings,
            labels=database_labels,
            top_k=3
        )
        
        assert similar_results is not None
        assert isinstance(similar_results, list)
        assert len(similar_results) <= 3
        
        # First result should be the query itself (highest similarity)
        if len(similar_results) > 0:
            assert similar_results[0].label == "pure_tone_440hz.wav"
            assert similar_results[0].similarity >= 0.99  # Very high self-similarity
    
    def test_similarity_ranking(self):
        """Test similarity ranking correctness"""        query_embedding = self.test_database["pure_tone_440hz.wav"]
        
        database_embeddings = np.array(list(self.test_database.values()))
        database_labels = list(self.test_database.keys())
        
        results = self.matcher.find_similar(
            query_embedding,
            database_embeddings, 
            labels=database_labels,
            top_k=len(database_labels)
        )
        
        # Results should be sorted by similarity (descending)
        for i in range(len(results) - 1):
            assert results[i].similarity >= results[i + 1].similarity
    
    def test_threshold_filtering(self):
        """Test similarity threshold filtering"""        matcher = SimilarityMatcher(threshold=0.9)  # High threshold
        
        query_embedding = self.test_database["pure_tone_440hz.wav"]
        database_embeddings = np.array(list(self.test_database.values()))
        database_labels = list(self.test_database.keys())
        
        results = matcher.find_similar(
            query_embedding,
            database_embeddings,
            labels=database_labels,
            top_k=10
        )
        
        # All results should meet threshold
        for result in results:
            assert result.similarity >= 0.9
    
    def test_large_database_performance(self):
        """Test performance with large database"""        # Create large database
        large_database_size = 1000
        large_database = np.random.randn(large_database_size, 512)
        large_database = large_database / np.linalg.norm(large_database, axis=1, keepdims=True)
        
        query_embedding = np.random.randn(512)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        start_time = time.time()
        results = self.matcher.find_similar(
            query_embedding,
            large_database,
            top_k=10
        )
        end_time = time.time()
        
        search_time_ms = (end_time - start_time) * 1000
        
        assert search_time_ms < 1000  # Should complete within 1 second
        assert len(results) == 10
    
    def test_batch_similarity_computation(self):
        """Test batch similarity computation"""        query_embeddings = np.array([
            self.test_database["pure_tone_440hz.wav"],
            self.test_database["white_noise.wav"]
        ])
        
        database_embeddings = np.array(list(self.test_database.values()))
        
        batch_similarities = self.matcher.compute_batch_similarity(
            query_embeddings,
            database_embeddings
        )
        
        assert batch_similarities is not None
        assert batch_similarities.shape == (2, len(self.test_database))
        assert not np.isnan(batch_similarities).any()
        
        # Check diagonal for self-similarities
        for i in range(len(query_embeddings)):
            self_sim = batch_similarities[i, i]
            assert self_sim >= 0.99  # High self-similarity


class TestSimilarityResult:
    """    Industrial-grade testing for SimilarityResult class
    
    Test Coverage:
    - Result object creation
    - Sorting functionality
    - Serialization/deserialization
    """    
    def test_result_creation(self):
        """Test SimilarityResult creation"""        result = SimilarityResult(
            label="test_audio.wav",
            similarity=0.85,
            distance=0.15,
            metadata={"duration": 5.0}
        )
        
        assert result.label == "test_audio.wav"
        assert result.similarity == 0.85
        assert result.distance == 0.15
        assert result.metadata["duration"] == 5.0
    
    def test_result_comparison(self):
        """Test result comparison for sorting"""        result1 = SimilarityResult("audio1.wav", 0.9, 0.1)
        result2 = SimilarityResult("audio2.wav", 0.8, 0.2)
        result3 = SimilarityResult("audio3.wav", 0.95, 0.05)
        
        results = [result1, result2, result3]
        sorted_results = sorted(results, reverse=True)  # Sort by similarity descending
        
        assert sorted_results[0].label == "audio3.wav"  # Highest similarity
        assert sorted_results[1].label == "audio1.wav"
        assert sorted_results[2].label == "audio2.wav"  # Lowest similarity
    
    def test_result_serialization(self):
        """Test result serialization to dict"""        result = SimilarityResult(
            label="test_audio.wav",
            similarity=0.85,
            distance=0.15,
            metadata={"duration": 5.0, "genre": "rock"}
        )
        
        serialized = result.to_dict()
        
        assert isinstance(serialized, dict)
        assert serialized["label"] == "test_audio.wav"
        assert serialized["similarity"] == 0.85
        assert serialized["distance"] == 0.15
        assert serialized["metadata"]["duration"] == 5.0
        assert serialized["metadata"]["genre"] == "rock"


class TestEmbeddingIntegration:
    """    Integration tests for embedding workflow
    """    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""        setup_test_environment()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
    
    def test_complete_embedding_workflow(self):
        """Test complete embedding workflow"""        # Load audio
        processor = AudioProcessor()
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = processor.load_audio(str(audio_file))
        
        # Generate embeddings
        generator = AudioEmbeddingGenerator()
        embeddings = generator.generate_embeddings(audio_data, sample_rate)
        
        # Find similar embeddings
        matcher = SimilarityMatcher()
        
        # Create small database
        database_embeddings = np.array([embeddings, embeddings * 0.9])  # Similar and dissimilar
        database_labels = ["original", "modified"]
        
        results = matcher.find_similar(
            embeddings,
            database_embeddings,
            labels=database_labels,
            top_k=2
        )
        
        # Verify workflow
        assert embeddings is not None
        assert len(results) == 2
        assert results[0].label == "original"  # Should find itself first
        assert results[0].similarity >= 0.99
    
    def test_embedding_reproducibility(self):
        """Test embedding reproducibility across sessions"""        # Load same audio multiple times
        processor = AudioProcessor()
        generator = AudioEmbeddingGenerator()
        
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        
        embeddings1 = []
        embeddings2 = []
        
        for _ in range(3):  # Multiple runs
            audio_data, sample_rate = processor.load_audio(str(audio_file))
            embedding = generator.generate_embeddings(audio_data, sample_rate)
            embeddings1.append(embedding)
        
        for _ in range(3):  # Another set of runs
            audio_data, sample_rate = processor.load_audio(str(audio_file))
            embedding = generator.generate_embeddings(audio_data, sample_rate)
            embeddings2.append(embedding)
        
        # All embeddings should be very similar
        for emb1, emb2 in zip(embeddings1, embeddings2):
            similarity = cosine_similarity(emb1.reshape(1, -1), emb2.reshape(1, -1))[0, 0]
            assert similarity >= 0.99
    
    def test_embedding_discriminative_power(self):
        """Test that embeddings can discriminate between different audio"""        processor = AudioProcessor()
        generator = AudioEmbeddingGenerator()
        
        # Load different types of audio
        pure_tone_file = self.test_data_dir / "pure_tone_440hz.wav"
        noise_file = self.test_data_dir / "white_noise.wav"
        
        tone_data, sample_rate = processor.load_audio(str(pure_tone_file))
        noise_data, _ = processor.load_audio(str(noise_file))
        
        tone_embedding = generator.generate_embeddings(tone_data, sample_rate)
        noise_embedding = generator.generate_embeddings(noise_data, sample_rate)
        
        # Similarity should be low between different audio types
        similarity = cosine_similarity(
            tone_embedding.reshape(1, -1),
            noise_embedding.reshape(1, -1)
        )[0, 0]
        
        assert similarity < 0.7  # Should be clearly different


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
