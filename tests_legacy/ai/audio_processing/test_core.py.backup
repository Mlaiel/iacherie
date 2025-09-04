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

"""🧪 Core Audio Processing Tests - Industrial-Grade Test Suite

Comprehensive testing for core audio processing functionality including:
- AudioProcessor class testing
- AudioAnalyzer validation  
- AudioEnhancer quality assurance
- Feature extraction accuracy testing
- Performance benchmarking
- Memory management validation

Created by Expert Team: Audio Developer + Backend Senior + ML Engineer
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
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the audio processing module
try:
    from ai.audio_processing.core import (
        AudioProcessor, AudioAnalyzer, AudioEnhancer, 
        AudioMetadata, AudioFeatures
    )
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    from ai.audio_processing.core import (
        AudioProcessor, AudioAnalyzer, AudioEnhancer, 
        AudioMetadata, AudioFeatures
    )

from . import TEST_CONFIG, setup_test_environment


class TestAudioProcessor:
    """
    Industrial-grade testing for AudioProcessor class
    
    Test Coverage:
    - Audio loading from various formats
    - Sample rate conversion
    - Bit depth handling  
    - Stereo/mono conversion
    - Large file processing
    - Memory management
    - Error handling
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test"""
        setup_test_environment()
        self.processor = AudioProcessor()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
        self.temp_output_dir = TEST_CONFIG["temp_output_dir"]
    
    def test_initialization(self):
        """Test AudioProcessor initialization"""
        processor = AudioProcessor()
        assert processor is not None
        assert hasattr(processor, 'sample_rate')
        assert hasattr(processor, 'chunk_size')
        assert processor.sample_rate == 44100  # Default
    
    def test_load_audio_wav_format(self):
        """Test loading WAV audio files"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        assert audio_data is not None
        assert isinstance(audio_data, np.ndarray)
        assert sample_rate == TEST_CONFIG["sample_rate"]
        assert len(audio_data) > 0
        assert audio_data.dtype == np.float32
    
    def test_load_audio_nonexistent_file(self):
        """Test error handling for non-existent files"""
        with pytest.raises(FileNotFoundError):
            self.processor.load_audio("nonexistent_file.wav")
    
    def test_load_audio_invalid_format(self):
        """Test error handling for invalid audio formats"""
        # Create a fake audio file with invalid content
        fake_file = self.temp_output_dir / "fake_audio.wav"
        with open(fake_file, 'w') as f:
            f.write("This is not audio data")
        
        with pytest.raises(Exception):  # Should raise audio loading exception
            self.processor.load_audio(str(fake_file))
    
    def test_resample_audio(self):
        """Test audio resampling functionality"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, _ = self.processor.load_audio(str(audio_file))
        
        # Resample to different rates
        resampled_22k = self.processor.resample_audio(audio_data, 44100, 22050)
        resampled_48k = self.processor.resample_audio(audio_data, 44100, 48000)
        
        assert len(resampled_22k) == len(audio_data) // 2  # Half sample rate
        assert len(resampled_48k) > len(audio_data)  # Higher sample rate
        assert resampled_22k.dtype == np.float32
        assert resampled_48k.dtype == np.float32
    
    def test_normalize_audio(self):
        """Test audio normalization"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, _ = self.processor.load_audio(str(audio_file))
        
        normalized = self.processor.normalize_audio(audio_data)
        
        assert np.max(np.abs(normalized)) <= 1.0
        assert np.max(np.abs(normalized)) >= 0.95  # Should be close to 1.0
        assert normalized.dtype == np.float32
    
    def test_trim_silence(self):
        """Test silence trimming functionality"""
        # Create audio with silence padding
        silence = np.zeros(1000)
        signal = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 4410))  # 0.1 second tone
        audio_with_silence = np.concatenate([silence, signal, silence])
        
        trimmed = self.processor.trim_silence(audio_with_silence)
        
        assert len(trimmed) < len(audio_with_silence)
        assert len(trimmed) >= len(signal) * 0.9  # Should preserve most of the signal
    
    def test_convert_to_mono(self):
        """Test stereo to mono conversion"""
        # Create stereo audio data
        mono_signal = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 4410))
        stereo_signal = np.column_stack([mono_signal, mono_signal * 0.8])
        
        mono_converted = self.processor.convert_to_mono(stereo_signal)
        
        assert mono_converted.ndim == 1
        assert len(mono_converted) == len(mono_signal)
        assert mono_converted.dtype == np.float32
    
    def test_save_audio(self):
        """Test audio saving functionality"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        output_file = self.temp_output_dir / "test_output.wav"
        self.processor.save_audio(str(output_file), audio_data, sample_rate)
        
        assert output_file.exists()
        
        # Verify saved audio by loading it back
        loaded_audio, loaded_sr = self.processor.load_audio(str(output_file))
        assert loaded_sr == sample_rate
        assert np.allclose(loaded_audio, audio_data, atol=1e-6)
    
    def test_memory_management_large_files(self):
        """Test memory management with large audio files"""
        # Create large audio data (simulate 10MB file)
        large_audio = np.random.randn(2205000)  # ~50 seconds at 44.1kHz
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process large audio
        normalized = self.processor.normalize_audio(large_audio)
        trimmed = self.processor.trim_silence(normalized)
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        assert memory_increase < TEST_CONFIG["memory_limit_mb"]
        assert trimmed is not None
    
    def test_performance_benchmarking(self):
        """Test processing performance meets requirements"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        
        start_time = time.time()
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        normalized = self.processor.normalize_audio(audio_data)
        trimmed = self.processor.trim_silence(normalized)
        end_time = time.time()
        
        processing_time_ms = (end_time - start_time) * 1000
        
        assert processing_time_ms < TEST_CONFIG["performance_threshold_ms"]
        assert trimmed is not None


class TestAudioAnalyzer:
    """
    Industrial-grade testing for AudioAnalyzer class
    
    Test Coverage:
    - Feature extraction accuracy
    - MFCC computation validation
    - Spectral feature analysis
    - Temporal feature extraction
    - Onset detection testing
    - Pitch estimation validation
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test"""
        setup_test_environment()
        self.analyzer = AudioAnalyzer()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
    
    def test_initialization(self):
        """Test AudioAnalyzer initialization"""
        analyzer = AudioAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'sample_rate')
        assert hasattr(analyzer, 'frame_size')
    
    def test_extract_mfcc_features(self):
        """Test MFCC feature extraction"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        processor = AudioProcessor()
        audio_data, sample_rate = processor.load_audio(str(audio_file))
        
        mfcc_features = self.analyzer.extract_mfcc(audio_data, sample_rate)
        
        assert mfcc_features is not None
        assert isinstance(mfcc_features, np.ndarray)
        assert mfcc_features.shape[0] == 13  # Standard MFCC coefficients
        assert mfcc_features.shape[1] > 0  # Should have time frames
        assert not np.isnan(mfcc_features).any()
    
    def test_extract_spectral_features(self):
        """Test spectral feature extraction"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        processor = AudioProcessor()
        audio_data, sample_rate = processor.load_audio(str(audio_file))
        
        spectral_features = self.analyzer.extract_spectral_features(audio_data, sample_rate)
        
        assert spectral_features is not None
        assert isinstance(spectral_features, dict)
        
        # Check required spectral features
        required_features = [
            'spectral_centroid', 'spectral_bandwidth', 'spectral_rolloff',
            'zero_crossing_rate', 'spectral_flatness'
        ]
        
        for feature in required_features:
            assert feature in spectral_features
            assert not np.isnan(spectral_features[feature]).any()
    
    def test_extract_temporal_features(self):
        """Test temporal feature extraction"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        processor = AudioProcessor()
        audio_data, sample_rate = processor.load_audio(str(audio_file))
        
        temporal_features = self.analyzer.extract_temporal_features(audio_data, sample_rate)
        
        assert temporal_features is not None
        assert isinstance(temporal_features, dict)
        
        # Check required temporal features
        required_features = ['rms_energy', 'tempo', 'rhythm_patterns']
        
        for feature in required_features:
            assert feature in temporal_features
            assert temporal_features[feature] is not None
    
    def test_detect_onsets(self):
        """Test onset detection"""
        audio_file = self.test_data_dir / "chirp_sweep.wav"  # Use chirp for onset testing
        processor = AudioProcessor()
        audio_data, sample_rate = processor.load_audio(str(audio_file))
        
        onsets = self.analyzer.detect_onsets(audio_data, sample_rate)
        
        assert onsets is not None
        assert isinstance(onsets, np.ndarray)
        assert len(onsets) >= 0  # Could be empty for pure tones
        assert all(onset >= 0 for onset in onsets)
    
    def test_estimate_pitch(self):
        """Test pitch estimation"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        processor = AudioProcessor()
        audio_data, sample_rate = processor.load_audio(str(audio_file))
        
        pitch_estimate = self.analyzer.estimate_pitch(audio_data, sample_rate)
        
        assert pitch_estimate is not None
        assert isinstance(pitch_estimate, (float, np.floating))
        assert 435 <= pitch_estimate <= 445  # Should be close to 440Hz
    
    def test_analyze_silence_vs_signal(self):
        """Test analysis of silence vs signal"""
        # Test silence
        silence_file = self.test_data_dir / "silence.wav"
        processor = AudioProcessor()
        silence_data, sample_rate = processor.load_audio(str(silence_file))
        
        silence_features = self.analyzer.extract_spectral_features(silence_data, sample_rate)
        
        # Test signal
        signal_file = self.test_data_dir / "pure_tone_440hz.wav"
        signal_data, _ = processor.load_audio(str(signal_file))
        
        signal_features = self.analyzer.extract_spectral_features(signal_data, sample_rate)
        
        # Signal should have higher energy than silence
        assert signal_features['rms_energy'] > silence_features['rms_energy']
        assert signal_features['spectral_centroid'] > silence_features['spectral_centroid']
    
    def test_comprehensive_analysis(self):
        """Test comprehensive audio analysis"""
        audio_file = self.test_data_dir / "white_noise.wav"
        processor = AudioProcessor()
        audio_data, sample_rate = processor.load_audio(str(audio_file))
        
        analysis_result = self.analyzer.analyze_audio(audio_data, sample_rate)
        
        assert analysis_result is not None
        assert isinstance(analysis_result, AudioFeatures)
        assert hasattr(analysis_result, 'mfcc')
        assert hasattr(analysis_result, 'spectral_features')
        assert hasattr(analysis_result, 'temporal_features')
        assert hasattr(analysis_result, 'metadata')


class TestAudioEnhancer:
    """
    Industrial-grade testing for AudioEnhancer class
    
    Test Coverage:
    - Noise reduction effectiveness
    - Dynamic range enhancement
    - Frequency response correction
    - Harmonic enhancement
    - Quality improvement validation
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test"""
        setup_test_environment()
        self.enhancer = AudioEnhancer()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
    
    def test_initialization(self):
        """Test AudioEnhancer initialization"""
        enhancer = AudioEnhancer()
        assert enhancer is not None
        assert hasattr(enhancer, 'sample_rate')
        assert hasattr(enhancer, 'enhancement_settings')
    
    def test_noise_reduction(self):
        """Test noise reduction effectiveness"""
        # Load noisy audio
        noisy_file = self.test_data_dir / "white_noise.wav"
        processor = AudioProcessor()
        noisy_audio, sample_rate = processor.load_audio(str(noisy_file))
        
        # Apply noise reduction
        enhanced_audio = self.enhancer.reduce_noise(noisy_audio, sample_rate)
        
        assert enhanced_audio is not None
        assert len(enhanced_audio) == len(noisy_audio)
        assert enhanced_audio.dtype == np.float32
        
        # Enhanced audio should have lower RMS energy (less noise)
        original_rms = np.sqrt(np.mean(noisy_audio**2))
        enhanced_rms = np.sqrt(np.mean(enhanced_audio**2))
        assert enhanced_rms <= original_rms
    
    def test_dynamic_range_enhancement(self):
        """Test dynamic range enhancement"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        processor = AudioProcessor()
        audio_data, sample_rate = processor.load_audio(str(audio_file))
        
        # Reduce dynamic range first (simulate compressed audio)
        compressed_audio = audio_data * 0.5
        
        # Enhance dynamic range
        enhanced_audio = self.enhancer.enhance_dynamic_range(compressed_audio, sample_rate)
        
        assert enhanced_audio is not None
        assert len(enhanced_audio) == len(compressed_audio)
        
        # Enhanced audio should have better dynamic range
        enhanced_peak = np.max(np.abs(enhanced_audio))
        compressed_peak = np.max(np.abs(compressed_audio))
        assert enhanced_peak >= compressed_peak
    
    def test_frequency_response_correction(self):
        """Test frequency response correction"""
        audio_file = self.test_data_dir / "chirp_sweep.wav"
        processor = AudioProcessor()
        audio_data, sample_rate = processor.load_audio(str(audio_file))
        
        # Apply frequency response correction
        corrected_audio = self.enhancer.correct_frequency_response(audio_data, sample_rate)
        
        assert corrected_audio is not None
        assert len(corrected_audio) == len(audio_data)
        assert corrected_audio.dtype == np.float32
        assert not np.isnan(corrected_audio).any()
    
    def test_harmonic_enhancement(self):
        """Test harmonic enhancement"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        processor = AudioProcessor()
        audio_data, sample_rate = processor.load_audio(str(audio_file))
        
        # Apply harmonic enhancement
        enhanced_audio = self.enhancer.enhance_harmonics(audio_data, sample_rate)
        
        assert enhanced_audio is not None
        assert len(enhanced_audio) == len(audio_data)
        assert enhanced_audio.dtype == np.float32
        
        # Enhanced audio should preserve fundamental frequency
        analyzer = AudioAnalyzer()
        original_pitch = analyzer.estimate_pitch(audio_data, sample_rate)
        enhanced_pitch = analyzer.estimate_pitch(enhanced_audio, sample_rate)
        
        assert abs(enhanced_pitch - original_pitch) < 5  # Within 5Hz tolerance
    
    def test_comprehensive_enhancement(self):
        """Test comprehensive audio enhancement"""
        audio_file = self.test_data_dir / "white_noise.wav"
        processor = AudioProcessor()
        audio_data, sample_rate = processor.load_audio(str(audio_file))
        
        # Apply comprehensive enhancement
        enhanced_audio = self.enhancer.enhance_audio(audio_data, sample_rate)
        
        assert enhanced_audio is not None
        assert len(enhanced_audio) == len(audio_data)
        assert enhanced_audio.dtype == np.float32
        
        # Verify enhancement improves quality metrics
        analyzer = AudioAnalyzer()
        original_features = analyzer.extract_spectral_features(audio_data, sample_rate)
        enhanced_features = analyzer.extract_spectral_features(enhanced_audio, sample_rate)
        
        # Enhanced audio should have better spectral characteristics
        assert enhanced_features['spectral_flatness'] <= original_features['spectral_flatness']
    
    def test_enhancement_preserves_length(self):
        """Test that enhancement preserves audio length"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        processor = AudioProcessor()
        audio_data, sample_rate = processor.load_audio(str(audio_file))
        
        enhanced_audio = self.enhancer.enhance_audio(audio_data, sample_rate)
        
        assert len(enhanced_audio) == len(audio_data)
    
    def test_enhancement_stability(self):
        """Test enhancement stability (no artifacts)"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        processor = AudioProcessor()
        audio_data, sample_rate = processor.load_audio(str(audio_file))
        
        enhanced_audio = self.enhancer.enhance_audio(audio_data, sample_rate)
        
        # Check for artifacts (NaN, inf, extreme values)
        assert not np.isnan(enhanced_audio).any()
        assert not np.isinf(enhanced_audio).any()
        assert np.max(np.abs(enhanced_audio)) <= 1.0  # No clipping


class TestAudioMetadata:
    """
    Industrial-grade testing for AudioMetadata class
    
    Test Coverage:
    - Metadata extraction accuracy
    - Format compatibility
    - Encoding information
    - Duration calculation
    """
    
    def test_metadata_creation(self):
        """Test AudioMetadata creation"""
        metadata = AudioMetadata(
            duration=5.0,
            sample_rate=44100,
            channels=2,
            bit_depth=16,
            format="WAV"
        )
        
        assert metadata.duration == 5.0
        assert metadata.sample_rate == 44100
        assert metadata.channels == 2
        assert metadata.bit_depth == 16
        assert metadata.format == "WAV"
    
    def test_metadata_validation(self):
        """Test metadata validation"""
        # Valid metadata
        valid_metadata = AudioMetadata(
            duration=5.0,
            sample_rate=44100,
            channels=2,
            bit_depth=16,
            format="WAV"
        )
        assert valid_metadata.is_valid()
        
        # Invalid metadata (negative duration)
        with pytest.raises(ValueError):
            AudioMetadata(
                duration=-1.0,
                sample_rate=44100,
                channels=2,
                bit_depth=16,
                format="WAV"
            )


class TestAudioFeatures:
    """
    Industrial-grade testing for AudioFeatures class
    
    Test Coverage:
    - Feature container functionality
    - Data serialization
    - Feature access methods
    """
    
    def test_features_creation(self):
        """Test AudioFeatures creation"""
        mfcc = np.random.randn(13, 100)
        spectral_features = {"spectral_centroid": np.random.randn(100)}
        temporal_features = {"rms_energy": np.random.randn(100)}
        
        features = AudioFeatures(
            mfcc=mfcc,
            spectral_features=spectral_features,
            temporal_features=temporal_features
        )
        
        assert np.array_equal(features.mfcc, mfcc)
        assert features.spectral_features == spectral_features
        assert features.temporal_features == temporal_features
    
    def test_features_serialization(self):
        """Test feature serialization to dict"""
        mfcc = np.random.randn(13, 100)
        spectral_features = {"spectral_centroid": np.random.randn(100)}
        temporal_features = {"rms_energy": np.random.randn(100)}
        
        features = AudioFeatures(
            mfcc=mfcc,
            spectral_features=spectral_features,
            temporal_features=temporal_features
        )
        
        serialized = features.to_dict()
        
        assert isinstance(serialized, dict)
        assert 'mfcc' in serialized
        assert 'spectral_features' in serialized
        assert 'temporal_features' in serialized


# Performance and integration tests
class TestCoreIntegration:
    """
    Integration tests for core audio processing workflow
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
    
    def test_complete_processing_workflow(self):
        """Test complete audio processing workflow"""
        # Load audio
        processor = AudioProcessor()
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = processor.load_audio(str(audio_file))
        
        # Analyze audio
        analyzer = AudioAnalyzer()
        features = analyzer.analyze_audio(audio_data, sample_rate)
        
        # Enhance audio
        enhancer = AudioEnhancer()
        enhanced_audio = enhancer.enhance_audio(audio_data, sample_rate)
        
        # Verify workflow completion
        assert audio_data is not None
        assert features is not None
        assert enhanced_audio is not None
        assert len(enhanced_audio) == len(audio_data)
    
    def test_cross_module_compatibility(self):
        """Test compatibility between all core modules"""
        processor = AudioProcessor()
        analyzer = AudioAnalyzer()
        enhancer = AudioEnhancer()
        
        audio_file = self.test_data_dir / "chirp_sweep.wav"
        
        # Process through all modules
        audio_data, sample_rate = processor.load_audio(str(audio_file))
        normalized_audio = processor.normalize_audio(audio_data)
        features = analyzer.analyze_audio(normalized_audio, sample_rate)
        enhanced_audio = enhancer.enhance_audio(normalized_audio, sample_rate)
        
        # Verify all outputs are compatible
        assert len(normalized_audio) == len(enhanced_audio)
        assert features.mfcc.shape[1] > 0
        assert not np.isnan(enhanced_audio).any()


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
