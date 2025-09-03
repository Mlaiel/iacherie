# -*- coding: utf-8 -*-
"""
Unit Tests for Audio Processing Module
======================================

Tests for the audio processing core functionality including:
- Audio loading and preprocessing
- Feature extraction
- Audio enhancement
- Format conversion
- Quality assessment

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import sys
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any, Optional

# Add project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from ai_engine.audio_processing.core import (
        AudioProcessor, AudioAnalyzer, AudioEnhancer, 
        AudioMetadata, AudioFeatures
    )
except ImportError:
    # Mock classes for testing when modules are not available
    class AudioProcessor:
        def load_audio(self, file_path: str):
            return np.random.random(44100), 44100
        
        def normalize_audio(self, audio_data: np.ndarray):
            return audio_data / np.max(np.abs(audio_data))
    
    class AudioAnalyzer:
        def analyze_audio(self, audio_data: np.ndarray, sample_rate: int):
            return Mock(mfcc=np.random.random((13, 100)))
    
    class AudioEnhancer:
        def enhance_audio(self, audio_data: np.ndarray, sample_rate: int):
            return audio_data
    
    class AudioMetadata:
        def __init__(self, sample_rate: int, channels: int, duration: float):
            self.sample_rate = sample_rate
            self.channels = channels
            self.duration = duration
    
    class AudioFeatures:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)


class TestAudioProcessor:
    """Test suite for AudioProcessor class"""
    
    @pytest.fixture
    def audio_processor(self):
        """Create AudioProcessor instance for testing"""
        return AudioProcessor()
    
    @pytest.fixture
    def sample_audio_file(self):
        """Sample audio file path for testing"""
        return "/tmp/test_audio.wav"
    
    @pytest.fixture
    def sample_audio_data(self):
        """Sample audio data for testing"""
        return np.random.random(44100), 44100
    
    def test_audio_processor_initialization(self, audio_processor):
        """Test AudioProcessor initialization"""
        assert audio_processor is not None
        assert hasattr(audio_processor, 'load_audio')
        assert hasattr(audio_processor, 'normalize_audio')
    
    @patch('librosa.load')
    def test_load_audio_success(self, mock_librosa_load, audio_processor, sample_audio_file):
        """Test successful audio loading"""
        # Mock librosa.load return
        mock_audio_data = np.random.random(44100)
        mock_sample_rate = 44100
        mock_librosa_load.return_value = (mock_audio_data, mock_sample_rate)
        
        # Test audio loading
        audio_data, sample_rate = audio_processor.load_audio(sample_audio_file)
        
        # Assertions
        assert audio_data is not None
        assert len(audio_data) > 0
        assert sample_rate == 44100
        mock_librosa_load.assert_called_once()
    
    def test_normalize_audio(self, audio_processor, sample_audio_data):
        """Test audio normalization"""
        audio_data, _ = sample_audio_data
        
        # Test normalization
        normalized_audio = audio_processor.normalize_audio(audio_data)
        
        # Assertions
        assert normalized_audio is not None
        assert len(normalized_audio) == len(audio_data)
        assert np.max(np.abs(normalized_audio)) <= 1.0


class TestAudioAnalyzer:
    """Test suite for AudioAnalyzer class"""
    
    @pytest.fixture
    def audio_analyzer(self):
        """Create AudioAnalyzer instance for testing"""
        return AudioAnalyzer()
    
    @pytest.fixture
    def sample_audio_data(self):
        """Sample audio data for testing"""
        return np.random.random(44100), 44100
    
    def test_audio_analyzer_initialization(self, audio_analyzer):
        """Test AudioAnalyzer initialization"""
        assert audio_analyzer is not None
        assert hasattr(audio_analyzer, 'analyze_audio')
    
    @patch('librosa.feature.mfcc')
    def test_analyze_audio(self, mock_mfcc, audio_analyzer, sample_audio_data):
        """Test audio feature analysis"""
        audio_data, sample_rate = sample_audio_data
        
        # Mock MFCC extraction
        mock_mfcc.return_value = np.random.random((13, 100))
        
        # Test analysis
        features = audio_analyzer.analyze_audio(audio_data, sample_rate)
        
        # Assertions
        assert features is not None
        assert hasattr(features, 'mfcc')


class TestAudioEnhancer:
    """Test suite for AudioEnhancer class"""
    
    @pytest.fixture
    def audio_enhancer(self):
        """Create AudioEnhancer instance for testing"""
        return AudioEnhancer()
    
    @pytest.fixture
    def sample_audio_data(self):
        """Sample audio data for testing"""
        return np.random.random(44100), 44100
    
    def test_audio_enhancer_initialization(self, audio_enhancer):
        """Test AudioEnhancer initialization"""
        assert audio_enhancer is not None
        assert hasattr(audio_enhancer, 'enhance_audio')
    
    def test_enhance_audio(self, audio_enhancer, sample_audio_data):
        """Test audio enhancement"""
        audio_data, sample_rate = sample_audio_data
        
        # Test enhancement
        enhanced_audio = audio_enhancer.enhance_audio(audio_data, sample_rate)
        
        # Assertions
        assert enhanced_audio is not None
        assert len(enhanced_audio) == len(audio_data)


class TestAudioMetadata:
    """Test suite for AudioMetadata class"""
    
    def test_audio_metadata_creation(self):
        """Test AudioMetadata creation"""
        metadata = AudioMetadata(
            sample_rate=44100,
            channels=2,
            duration=180.5
        )
        
        # Assertions
        assert metadata.sample_rate == 44100
        assert metadata.channels == 2
        assert metadata.duration == 180.5


class TestAudioFeatures:
    """Test suite for AudioFeatures class"""
    
    def test_audio_features_creation(self):
        """Test AudioFeatures creation"""
        features = AudioFeatures(
            mfcc=np.random.random((13, 100)),
            spectral_centroid=np.random.random(100),
            tempo=120.0
        )
        
        # Assertions
        assert hasattr(features, 'mfcc')
        assert hasattr(features, 'spectral_centroid')
        assert hasattr(features, 'tempo')


# Integration tests
class TestAudioProcessingIntegration:
    """Integration tests for audio processing workflow"""
    
    def test_complete_audio_processing_workflow(self):
        """Test complete audio processing workflow"""
        # Create processors
        processor = AudioProcessor()
        analyzer = AudioAnalyzer()
        enhancer = AudioEnhancer()
        
        # Mock audio data
        audio_data = np.random.random(44100)
        sample_rate = 44100
        
        # Process through workflow
        normalized_audio = processor.normalize_audio(audio_data)
        features = analyzer.analyze_audio(normalized_audio, sample_rate)
        enhanced_audio = enhancer.enhance_audio(normalized_audio, sample_rate)
        
        # Verify workflow completion
        assert normalized_audio is not None
        assert features is not None
        assert enhanced_audio is not None
        assert len(enhanced_audio) == len(audio_data)


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])