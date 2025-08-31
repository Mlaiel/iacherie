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
 Quality Tests - Industrial-Grade Audio Quality Assessment Testing Suite

Comprehensive testing for audio quality evaluation including:
- QualityAnalyzer validation
- Perceptual quality metrics
- Objective quality measurements
- Audio degradation detection
- Quality enhancement validation

Created by Expert Team: Audio Quality Engineer + DSP Specialist + Testing Expert
© 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import sys
import os
from pathlib import Path
import numpy as np
import tempfile
import time
import os
import librosa
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from scipy import signal
from scipy.stats import pearsonr

# Import the audio processing module
try:
    from ai.audio_processing.quality import (
        AudioQualityAssessor, PerceptualQualityAnalyzer, 
        TechnicalQualityAnalyzer, QualityReport, QualityMetric, 
        QualityAspect, QualityGrade
    )
    from ai.audio_processing.core import AudioProcessor
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))
    from ai.audio_processing.quality import (
        AudioQualityAssessor, PerceptualQualityAnalyzer,
        TechnicalQualityAnalyzer, QualityReport, QualityMetric, 
        QualityAspect, QualityGrade
    )
    from ai.audio_processing.core import AudioProcessor

from . import TEST_CONFIG, setup_test_environment


class TestQualityAnalyzer:
    """
    Industrial-grade testing for QualityAnalyzer class
    
    Test Coverage:
    - Quality analysis initialization
    - Comprehensive quality assessment
    - Multiple quality metrics computation
    - Quality scoring and rating
    - Performance optimization
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test"""
        setup_test_environment()
        
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
        self.processor = AudioProcessor()
        
        # Create quality analyzer with default config
        self.config = QualityConfig(
            enable_perceptual=True,
            enable_objective=True,
            enable_enhancement=True,
            sample_rate=44100
        )
        self.analyzer = QualityAnalyzer(config=self.config)
    
    def test_initialization(self):
        """Test QualityAnalyzer initialization"""
        analyzer = QualityAnalyzer()
        
        assert analyzer is not None
        assert hasattr(analyzer, 'config')
        assert hasattr(analyzer, 'perceptual_assessor')
        assert hasattr(analyzer, 'objective_measurement')
        assert hasattr(analyzer, 'enhancer')
        assert hasattr(analyzer, 'degradation_detector')
    
    def test_analyze_quality_clean_audio(self):
        """Test quality analysis on clean audio"""
        # Load clean test audio
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        # Analyze quality
        quality_result = self.analyzer.analyze_quality(audio_data, sample_rate)
        
        # Verify results
        assert isinstance(quality_result, QualityMetrics)
        assert quality_result.overall_score >= 0.0
        assert quality_result.overall_score <= 1.0
        
        # Clean audio should have high quality
        assert quality_result.overall_score > 0.7
        assert quality_result.snr_db > 40  # Good SNR for clean audio
        assert quality_result.thd_percent < 1.0  # Low distortion
    
    def test_analyze_quality_noisy_audio(self):
        """Test quality analysis on noisy audio"""
        # Create noisy audio
        clean_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        noise = np.random.normal(0, 0.1, len(clean_audio))
        noisy_audio = clean_audio + noise
        
        # Analyze quality
        quality_result = self.analyzer.analyze_quality(noisy_audio, 44100)
        
        # Verify results
        assert isinstance(quality_result, QualityMetrics)
        assert quality_result.overall_score < 0.8  # Should be lower than clean
        assert quality_result.snr_db < 30  # Lower SNR due to noise
        assert quality_result.noise_level > 0.05  # Detectable noise
    
    def test_analyze_quality_distorted_audio(self):
        """Test quality analysis on distorted audio"""
        # Create distorted audio (clipping)
        clean_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        distorted_audio = np.clip(clean_audio * 2, -0.8, 0.8)  # Clipping distortion
        
        # Analyze quality
        quality_result = self.analyzer.analyze_quality(distorted_audio, 44100)
        
        # Verify results
        assert isinstance(quality_result, QualityMetrics)
        assert quality_result.overall_score < 0.7  # Should be lower due to distortion
        assert quality_result.thd_percent > 1.0  # Higher THD due to clipping
        assert quality_result.dynamic_range < 40  # Reduced dynamic range
    
    def test_batch_quality_analysis(self):
        """Test batch quality analysis"""
        # Create multiple audio samples
        audio_samples = []
        for freq in [220, 440, 880]:
            audio = np.sin(2 * np.pi * freq * np.linspace(0, 1, 22050))
            audio_samples.append(audio)
        
        # Batch analysis
        results = self.analyzer.analyze_batch(audio_samples, sample_rate=44100)
        
        # Verify results
        assert len(results) == 3
        for result in results:
            assert isinstance(result, QualityMetrics)
            assert 0.0 <= result.overall_score <= 1.0
    
    def test_quality_comparison(self):
        """Test quality comparison between audio samples"""
        # Create reference and test audio
        reference = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        
        # Create degraded version
        degraded = reference + np.random.normal(0, 0.05, len(reference))
        
        # Compare quality
        comparison = self.analyzer.compare_quality(reference, degraded, 44100)
        
        # Verify comparison
        assert comparison is not None
        assert hasattr(comparison, 'reference_score')
        assert hasattr(comparison, 'test_score')
        assert hasattr(comparison, 'quality_difference')
        assert hasattr(comparison, 'degradation_factors')
        
        # Reference should have better quality
        assert comparison.reference_score > comparison.test_score
        assert comparison.quality_difference > 0
    
    def test_quality_enhancement_recommendation(self):
        """Test quality enhancement recommendations"""
        # Create audio with known issues
        noisy_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        noisy_audio += np.random.normal(0, 0.1, len(noisy_audio))
        
        # Get enhancement recommendations
        recommendations = self.analyzer.get_enhancement_recommendations(
            noisy_audio, 44100
        )
        
        # Verify recommendations
        assert recommendations is not None
        assert isinstance(recommendations, dict)
        assert "noise_reduction" in recommendations
        assert "suggested_filters" in recommendations
        assert "enhancement_priority" in recommendations


class TestPerceptualQualityAssessor:
    """
    Industrial-grade testing for PerceptualQualityAssessor class
    
    Test Coverage:
    - Perceptual quality models
    - Psychoacoustic analysis
    - Loudness measurements
    - Masking threshold analysis
    - Perceptual distortion metrics
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
        self.assessor = PerceptualQualityAssessor()
    
    def test_initialization(self):
        """Test PerceptualQualityAssessor initialization"""
        assessor = PerceptualQualityAssessor()
        
        assert assessor is not None
        assert hasattr(assessor, 'psychoacoustic_model')
        assert hasattr(assessor, 'loudness_model')
        assert hasattr(assessor, 'masking_threshold')
    
    def test_loudness_measurement(self):
        """Test loudness measurement"""
        # Create test tones with different amplitudes
        low_amplitude = 0.1 * np.sin(2 * np.pi * 1000 * np.linspace(0, 1, 44100))
        high_amplitude = 0.8 * np.sin(2 * np.pi * 1000 * np.linspace(0, 1, 44100))
        
        # Measure loudness
        low_loudness = self.assessor.measure_loudness(low_amplitude, 44100)
        high_loudness = self.assessor.measure_loudness(high_amplitude, 44100)
        
        # Verify loudness measurements
        assert low_loudness > 0
        assert high_loudness > 0
        assert high_loudness > low_loudness  # Higher amplitude should be louder
    
    def test_masking_threshold_analysis(self):
        """Test masking threshold analysis"""
        # Create complex audio with masking effects
        fundamental = np.sin(2 * np.pi * 1000 * np.linspace(0, 1, 44100))
        harmonic = 0.3 * np.sin(2 * np.pi * 2000 * np.linspace(0, 1, 44100))
        complex_audio = fundamental + harmonic
        
        # Analyze masking threshold
        masking_result = self.assessor.analyze_masking_threshold(complex_audio, 44100)
        
        # Verify results
        assert masking_result is not None
        assert hasattr(masking_result, 'threshold_curve')
        assert hasattr(masking_result, 'masked_frequencies')
        assert hasattr(masking_result, 'effective_bits')
    
    def test_perceptual_distortion_measurement(self):
        """Test perceptual distortion measurement"""
        # Create reference and distorted signals
        reference = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        
        # Add perceptually noticeable distortion
        distorted = reference + 0.1 * np.sin(2 * np.pi * 440 * 3 * np.linspace(0, 1, 44100))
        
        # Measure perceptual distortion
        distortion_score = self.assessor.measure_perceptual_distortion(
            reference, distorted, 44100
        )
        
        # Verify distortion measurement
        assert 0.0 <= distortion_score <= 1.0
        assert distortion_score > 0.1  # Should detect distortion
    
    def test_frequency_domain_analysis(self):
        """Test frequency domain perceptual analysis"""
        # Create audio with specific frequency content
        frequencies = [220, 440, 880, 1760]
        audio = np.zeros(44100)
        
        for i, freq in enumerate(frequencies):
            amplitude = 0.5 / (i + 1)  # Decreasing amplitude
            audio += amplitude * np.sin(2 * np.pi * freq * np.linspace(0, 1, 44100))
        
        # Analyze frequency domain perception
        freq_analysis = self.assessor.analyze_frequency_perception(audio, 44100)
        
        # Verify analysis
        assert freq_analysis is not None
        assert "bark_spectrum" in freq_analysis
        assert "perceptual_sharpness" in freq_analysis
        assert "spectral_balance" in freq_analysis
    
    def test_temporal_masking_analysis(self):
        """Test temporal masking analysis"""
        # Create audio with temporal masking effects
        mask_duration = 0.1  # 100ms masker
        probe_delay = 0.05   # 50ms probe delay
        
        sample_rate = 44100
        mask_samples = int(mask_duration * sample_rate)
        delay_samples = int(probe_delay * sample_rate)
        
        # Create masker (loud tone)
        masker = 0.8 * np.sin(2 * np.pi * 1000 * np.linspace(0, mask_duration, mask_samples))
        
        # Create probe (quiet tone after delay)
        probe = 0.1 * np.sin(2 * np.pi * 1000 * np.linspace(0, 0.05, int(0.05 * sample_rate)))
        
        # Combine with silence
        total_length = mask_samples + delay_samples + len(probe)
        audio = np.zeros(total_length)
        audio[:mask_samples] = masker
        audio[mask_samples + delay_samples:mask_samples + delay_samples + len(probe)] = probe
        
        # Analyze temporal masking
        temporal_result = self.assessor.analyze_temporal_masking(audio, sample_rate)
        
        # Verify results
        assert temporal_result is not None
        assert "masking_curve" in temporal_result
        assert "probe_audibility" in temporal_result


class TestObjectiveQualityMeasurement:
    """
    Industrial-grade testing for ObjectiveQualityMeasurement class
    
    Test Coverage:
    - Objective quality metrics
    - SNR calculations
    - THD measurements
    - Frequency response analysis
    - Dynamic range evaluation
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
        self.measurement = ObjectiveQualityMeasurement()
    
    def test_initialization(self):
        """Test ObjectiveQualityMeasurement initialization"""
        measurement = ObjectiveQualityMeasurement()
        
        assert measurement is not None
        assert hasattr(measurement, 'snr_analyzer')
        assert hasattr(measurement, 'thd_calculator')
        assert hasattr(measurement, 'frequency_analyzer')
    
    def test_snr_calculation(self):
        """Test Signal-to-Noise Ratio calculation"""
        # Create signal with known SNR
        signal_power = 1.0
        noise_power = 0.01  # -20 dB SNR
        
        signal_amplitude = np.sqrt(signal_power)
        noise_amplitude = np.sqrt(noise_power)
        
        clean_signal = signal_amplitude * np.sin(2 * np.pi * 1000 * np.linspace(0, 1, 44100))
        noise = noise_amplitude * np.random.normal(0, 1, 44100)
        noisy_signal = clean_signal + noise
        
        # Calculate SNR
        calculated_snr = self.measurement.calculate_snr(clean_signal, noisy_signal)
        
        # Expected SNR ≈ 20 dB
        expected_snr = 10 * np.log10(signal_power / noise_power)
        
        assert abs(calculated_snr - expected_snr) < 3  # Allow 3 dB tolerance
        assert calculated_snr > 15  # Should be reasonably high
    
    def test_thd_calculation(self):
        """Test Total Harmonic Distortion calculation"""
        # Create signal with known harmonics
        fundamental_freq = 1000
        sample_rate = 44100
        t = np.linspace(0, 1, sample_rate)
        
        # Pure fundamental
        fundamental = np.sin(2 * np.pi * fundamental_freq * t)
        
        # Add harmonics (2nd and 3rd)
        second_harmonic = 0.1 * np.sin(2 * np.pi * 2 * fundamental_freq * t)
        third_harmonic = 0.05 * np.sin(2 * np.pi * 3 * fundamental_freq * t)
        
        distorted_signal = fundamental + second_harmonic + third_harmonic
        
        # Calculate THD
        thd_percent = self.measurement.calculate_thd(distorted_signal, sample_rate, fundamental_freq)
        
        # Expected THD based on harmonic amplitudes
        # THD = sqrt(H2^2 + H3^2) / H1 * 100%
        expected_thd = np.sqrt(0.1**2 + 0.05**2) / 1.0 * 100
        
        assert abs(thd_percent - expected_thd) < 2  # Allow 2% tolerance
        assert thd_percent > 5  # Should detect harmonics
    
    def test_frequency_response_analysis(self):
        """Test frequency response analysis"""
        # Create broadband signal
        sample_rate = 44100
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # White noise input
        input_signal = np.random.normal(0, 1, len(t))
        
        # Apply simple filter (low-pass)
        from scipy.signal import butter, filtfilt
        nyquist = sample_rate / 2
        cutoff = 5000  # 5 kHz cutoff
        b, a = butter(4, cutoff / nyquist, btype='low')
        output_signal = filtfilt(b, a, input_signal)
        
        # Analyze frequency response
        freq_response = self.measurement.analyze_frequency_response(
            input_signal, output_signal, sample_rate
        )
        
        # Verify response analysis
        assert freq_response is not None
        assert "frequencies" in freq_response
        assert "magnitude_db" in freq_response
        assert "phase_degrees" in freq_response
        
        # Check that high frequencies are attenuated
        freqs = freq_response["frequencies"]
        magnitudes = freq_response["magnitude_db"]
        
        # Find magnitude at cutoff frequency
        cutoff_idx = np.argmin(np.abs(freqs - cutoff))
        high_freq_idx = np.argmin(np.abs(freqs - 10000))  # 10 kHz
        
        if high_freq_idx < len(magnitudes) and cutoff_idx < len(magnitudes):
            assert magnitudes[high_freq_idx] < magnitudes[cutoff_idx]  # High freq should be lower
    
    def test_dynamic_range_measurement(self):
        """Test dynamic range measurement"""
        # Create signal with known dynamic range
        sample_rate = 44100
        
        # Quiet passage
        quiet_level = 0.01
        quiet_signal = quiet_level * np.sin(2 * np.pi * 1000 * np.linspace(0, 0.5, sample_rate // 2))
        
        # Loud passage
        loud_level = 0.8
        loud_signal = loud_level * np.sin(2 * np.pi * 1000 * np.linspace(0, 0.5, sample_rate // 2))
        
        # Combine signals
        combined_signal = np.concatenate([quiet_signal, loud_signal])
        
        # Measure dynamic range
        dynamic_range_db = self.measurement.measure_dynamic_range(combined_signal)
        
        # Expected dynamic range
        expected_range = 20 * np.log10(loud_level / quiet_level)
        
        assert abs(dynamic_range_db - expected_range) < 5  # Allow 5 dB tolerance
        assert dynamic_range_db > 30  # Should be substantial
    
    def test_peak_to_rms_ratio(self):
        """Test peak-to-RMS ratio measurement"""
        # Test with different signal types
        
        # Sine wave (known crest factor = √2 ≈ 1.414, or 3 dB)
        sine_wave = np.sin(2 * np.pi * 1000 * np.linspace(0, 1, 44100))
        sine_crest = self.measurement.calculate_crest_factor(sine_wave)
        expected_sine_crest_db = 20 * np.log10(np.sqrt(2))
        assert abs(sine_crest - expected_sine_crest_db) < 1  # Within 1 dB
        
        # Square wave (crest factor = 1, or 0 dB)
        square_wave = np.sign(sine_wave)
        square_crest = self.measurement.calculate_crest_factor(square_wave)
        assert abs(square_crest - 0) < 1  # Should be close to 0 dB
        
        # White noise (crest factor ≈ 12-15 dB)
        noise = np.random.normal(0, 1, 44100)
        noise_crest = self.measurement.calculate_crest_factor(noise)
        assert 10 < noise_crest < 20  # Typical range for white noise


class TestAudioQualityEnhancer:
    """
    Industrial-grade testing for AudioQualityEnhancer class
    
    Test Coverage:
    - Noise reduction algorithms
    - Dynamic range enhancement
    - Frequency correction
    - Harmonic restoration
    - Adaptive enhancement
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
        self.enhancer = AudioQualityEnhancer()
    
    def test_initialization(self):
        """Test AudioQualityEnhancer initialization"""
        enhancer = AudioQualityEnhancer()
        
        assert enhancer is not None
        assert hasattr(enhancer, 'noise_reducer')
        assert hasattr(enhancer, 'dynamic_processor')
        assert hasattr(enhancer, 'frequency_corrector')
    
    def test_noise_reduction(self):
        """Test noise reduction functionality"""
        # Create noisy signal
        clean_signal = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        noise = 0.1 * np.random.normal(0, 1, len(clean_signal))
        noisy_signal = clean_signal + noise
        
        # Apply noise reduction
        enhanced_signal = self.enhancer.reduce_noise(noisy_signal, 44100)
        
        # Verify noise reduction
        assert len(enhanced_signal) == len(noisy_signal)
        
        # Calculate SNR improvement
        original_snr = 20 * np.log10(np.std(clean_signal) / np.std(noise))
        enhanced_noise = enhanced_signal - clean_signal
        enhanced_snr = 20 * np.log10(np.std(clean_signal) / np.std(enhanced_noise))
        
        # Should improve SNR
        if np.std(enhanced_noise) > 0:
            assert enhanced_snr >= original_snr  # SNR should improve or stay same
    
    def test_dynamic_range_enhancement(self):
        """Test dynamic range enhancement"""
        # Create signal with compressed dynamics
        original_signal = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        
        # Apply compression (reduce dynamic range)
        compressed_signal = np.tanh(original_signal * 2) * 0.5
        
        # Enhance dynamic range
        enhanced_signal = self.enhancer.enhance_dynamics(compressed_signal, 44100)
        
        # Verify enhancement
        assert len(enhanced_signal) == len(compressed_signal)
        
        # Check dynamic range improvement
        original_range = np.max(original_signal) - np.min(original_signal)
        compressed_range = np.max(compressed_signal) - np.min(compressed_signal)
        enhanced_range = np.max(enhanced_signal) - np.min(enhanced_signal)
        
        assert enhanced_range >= compressed_range  # Should maintain or improve range
    
    def test_frequency_correction(self):
        """Test frequency response correction"""
        # Create signal with frequency imbalance
        sample_rate = 44100
        t = np.linspace(0, 1, sample_rate)
        
        # Multi-frequency signal
        signal = (np.sin(2 * np.pi * 100 * t) +     # Bass
                 0.3 * np.sin(2 * np.pi * 1000 * t) + # Mid
                 0.1 * np.sin(2 * np.pi * 5000 * t))  # Treble (weak)
        
        # Apply frequency correction
        corrected_signal = self.enhancer.correct_frequency_response(signal, sample_rate)
        
        # Verify correction
        assert len(corrected_signal) == len(signal)
        
        # Analyze frequency content before and after
        freqs_orig = np.fft.fftfreq(len(signal), 1/sample_rate)
        fft_orig = np.abs(np.fft.fft(signal))
        fft_corrected = np.abs(np.fft.fft(corrected_signal))
        
        # Check that high frequencies are enhanced
        high_freq_idx = np.where((freqs_orig > 3000) & (freqs_orig < 8000))[0]
        if len(high_freq_idx) > 0:
            high_orig = np.mean(fft_orig[high_freq_idx])
            high_corrected = np.mean(fft_corrected[high_freq_idx])
            # High frequencies should be enhanced (or at least not reduced)
            assert high_corrected >= high_orig * 0.8
    
    def test_harmonic_restoration(self):
        """Test harmonic restoration"""
        # Create signal with missing harmonics
        fundamental_freq = 220
        sample_rate = 44100
        t = np.linspace(0, 1, sample_rate)
        
        # Only fundamental (missing harmonics)
        fundamental_only = np.sin(2 * np.pi * fundamental_freq * t)
        
        # Apply harmonic restoration
        restored_signal = self.enhancer.restore_harmonics(fundamental_only, sample_rate)
        
        # Verify harmonic restoration
        assert len(restored_signal) == len(fundamental_only)
        
        # Check for added harmonic content
        freqs = np.fft.fftfreq(len(restored_signal), 1/sample_rate)
        fft_restored = np.abs(np.fft.fft(restored_signal))
        
        # Look for harmonic frequencies
        harmonic_freqs = [2 * fundamental_freq, 3 * fundamental_freq]
        for harm_freq in harmonic_freqs:
            harm_idx = np.argmin(np.abs(freqs - harm_freq))
            if harm_idx < len(fft_restored) // 2:  # Only positive frequencies
                # Should have some energy at harmonic frequencies
                assert fft_restored[harm_idx] > np.mean(fft_restored) * 0.1
    
    def test_adaptive_enhancement(self):
        """Test adaptive enhancement based on content analysis"""
        # Create different types of audio content
        sample_rate = 44100
        
        # Speech-like signal (formants)
        speech_like = (np.sin(2 * np.pi * 400 * np.linspace(0, 1, sample_rate)) +
                      0.7 * np.sin(2 * np.pi * 800 * np.linspace(0, 1, sample_rate)) +
                      0.5 * np.sin(2 * np.pi * 2400 * np.linspace(0, 1, sample_rate)))
        
        # Music-like signal (harmonic series)
        music_like = (np.sin(2 * np.pi * 220 * np.linspace(0, 1, sample_rate)) +
                     0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, sample_rate)) +
                     0.3 * np.sin(2 * np.pi * 660 * np.linspace(0, 1, sample_rate)))
        
        # Apply adaptive enhancement
        enhanced_speech = self.enhancer.adaptive_enhance(speech_like, sample_rate, content_type="speech")
        enhanced_music = self.enhancer.adaptive_enhance(music_like, sample_rate, content_type="music")
        
        # Verify adaptive processing
        assert len(enhanced_speech) == len(speech_like)
        assert len(enhanced_music) == len(music_like)
        
        # Different content types should be processed differently
        assert not np.array_equal(enhanced_speech, enhanced_music)


class TestDegradationDetector:
    """
    Industrial-grade testing for DegradationDetector class
    
    Test Coverage:
    - Degradation type identification
    - Clipping detection
    - Noise floor analysis
    - Bandwidth limitation detection
    - Compression artifact detection
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
        self.detector = DegradationDetector()
    
    def test_initialization(self):
        """Test DegradationDetector initialization"""
        detector = DegradationDetector()
        
        assert detector is not None
        assert hasattr(detector, 'clipping_detector')
        assert hasattr(detector, 'noise_analyzer')
        assert hasattr(detector, 'bandwidth_analyzer')
    
    def test_clipping_detection(self):
        """Test clipping detection"""
        # Create clipped signal
        original = 2 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        clipped = np.clip(original, -0.8, 0.8)
        
        # Detect clipping
        clipping_result = self.detector.detect_clipping(clipped)
        
        # Verify clipping detection
        assert clipping_result["has_clipping"] is True
        assert clipping_result["clipping_percentage"] > 10  # Should be significant
        assert "clipped_samples" in clipping_result
        
        # Test non-clipped signal
        normal_signal = 0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        normal_result = self.detector.detect_clipping(normal_signal)
        assert normal_result["has_clipping"] is False
    
    def test_noise_floor_analysis(self):
        """Test noise floor analysis"""
        # Create signal with known noise floor
        signal = np.sin(2 * np.pi * 1000 * np.linspace(0, 1, 44100))
        noise_level = 0.01  # -40 dB noise floor
        noise = noise_level * np.random.normal(0, 1, len(signal))
        noisy_signal = signal + noise
        
        # Analyze noise floor
        noise_analysis = self.detector.analyze_noise_floor(noisy_signal, 44100)
        
        # Verify analysis
        assert "noise_floor_db" in noise_analysis
        assert "noise_type" in noise_analysis
        assert "noise_characteristics" in noise_analysis
        
        # Noise floor should be around -40 dB
        expected_noise_db = 20 * np.log10(noise_level)
        assert abs(noise_analysis["noise_floor_db"] - expected_noise_db) < 10
    
    def test_bandwidth_limitation_detection(self):
        """Test bandwidth limitation detection"""
        # Create full-bandwidth signal
        sample_rate = 44100
        nyquist = sample_rate / 2
        
        # Generate broadband signal
        full_signal = np.random.normal(0, 1, sample_rate)
        
        # Apply low-pass filter to simulate bandwidth limitation
        from scipy.signal import butter, filtfilt
        cutoff = 8000  # 8 kHz cutoff
        b, a = butter(6, cutoff / nyquist, btype='low')
        limited_signal = filtfilt(b, a, full_signal)
        
        # Detect bandwidth limitation
        bandwidth_result = self.detector.detect_bandwidth_limitation(limited_signal, sample_rate)
        
        # Verify detection
        assert "effective_bandwidth_hz" in bandwidth_result
        assert "is_bandwidth_limited" in bandwidth_result
        assert "cutoff_frequency_hz" in bandwidth_result
        
        # Should detect bandwidth limitation
        assert bandwidth_result["is_bandwidth_limited"] is True
        assert bandwidth_result["effective_bandwidth_hz"] < nyquist * 0.8
    
    def test_compression_artifact_detection(self):
        """Test compression artifact detection"""
        # Create signal with compression artifacts
        original = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        
        # Simulate lossy compression artifacts (pre-echo, quantization noise)
        # Add pre-echo
        pre_echo = np.zeros_like(original)
        pre_echo[1000:1500] = 0.05 * original[2000:2500]  # Shifted and scaled
        
        # Add quantization noise
        quantization_noise = 0.02 * np.random.uniform(-1, 1, len(original))
        
        compressed_signal = original + pre_echo + quantization_noise
        
        # Detect compression artifacts
        compression_result = self.detector.detect_compression_artifacts(compressed_signal, 44100)
        
        # Verify detection
        assert "has_artifacts" in compression_result
        assert "artifact_types" in compression_result
        assert "severity_score" in compression_result
        
        # Should detect artifacts
        assert compression_result["severity_score"] > 0.1
    
    def test_comprehensive_degradation_analysis(self):
        """Test comprehensive degradation analysis"""
        # Create signal with multiple degradations
        original = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        
        # Add multiple degradations
        degraded = original.copy()
        
        # Add noise
        degraded += 0.05 * np.random.normal(0, 1, len(degraded))
        
        # Add clipping
        degraded = np.clip(degraded * 1.5, -0.9, 0.9)
        
        # Apply bandwidth limitation
        from scipy.signal import butter, filtfilt
        b, a = butter(4, 6000 / (44100/2), btype='low')
        degraded = filtfilt(b, a, degraded)
        
        # Comprehensive analysis
        degradation_report = self.detector.analyze_all_degradations(degraded, 44100)
        
        # Verify comprehensive analysis
        assert "overall_quality_score" in degradation_report
        assert "detected_degradations" in degradation_report
        assert "severity_levels" in degradation_report
        assert "recommendations" in degradation_report
        
        # Should detect multiple degradations
        assert len(degradation_report["detected_degradations"]) >= 2
        assert degradation_report["overall_quality_score"] < 0.7  # Poor quality


class TestQualityConfig:
    """Test QualityConfig data structure"""
    
    def test_config_creation(self):
        """Test QualityConfig creation"""
        config = QualityConfig(
            enable_perceptual=True,
            enable_objective=True,
            enable_enhancement=False,
            sample_rate=48000,
            analysis_window_size=2048
        )
        
        assert config.enable_perceptual is True
        assert config.enable_objective is True
        assert config.enable_enhancement is False
        assert config.sample_rate == 48000
        assert config.analysis_window_size == 2048
    
    def test_config_validation(self):
        """Test config validation"""
        # Valid config
        valid_config = QualityConfig(sample_rate=44100)
        assert valid_config.is_valid()
        
        # Invalid config
        with pytest.raises(ValueError):
            QualityConfig(sample_rate=0)  # Invalid sample rate


class TestQualityIntegration:
    """
    Integration tests for complete quality assessment workflows
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
        self.processor = AudioProcessor()
    
    def test_complete_quality_workflow(self):
        """Test complete quality assessment workflow"""
        # Initialize components
        config = QualityConfig(
            enable_perceptual=True,
            enable_objective=True,
            enable_enhancement=True
        )
        analyzer = QualityAnalyzer(config=config)
        enhancer = AudioQualityEnhancer()
        
        # Load test audio
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        # Initial quality assessment
        initial_quality = analyzer.analyze_quality(audio_data, sample_rate)
        
        # Apply degradation for testing
        degraded_audio = audio_data + 0.1 * np.random.normal(0, 1, len(audio_data))
        degraded_quality = analyzer.analyze_quality(degraded_audio, sample_rate)
        
        # Enhance degraded audio
        enhanced_audio = enhancer.reduce_noise(degraded_audio, sample_rate)
        enhanced_quality = analyzer.analyze_quality(enhanced_audio, sample_rate)
        
        # Verify workflow
        assert initial_quality.overall_score > degraded_quality.overall_score
        assert enhanced_quality.overall_score >= degraded_quality.overall_score
    
    def test_quality_monitoring_pipeline(self):
        """Test quality monitoring in processing pipeline"""
        # Create quality monitor
        config = QualityConfig(enable_perceptual=True, enable_objective=True)
        analyzer = QualityAnalyzer(config=config)
        
        # Process multiple audio samples
        quality_scores = []
        
        for i in range(5):
            # Generate test audio with varying quality
            base_signal = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
            noise_level = i * 0.02  # Increasing noise
            noisy_signal = base_signal + noise_level * np.random.normal(0, 1, len(base_signal))
            
            quality = analyzer.analyze_quality(noisy_signal, 44100)
            quality_scores.append(quality.overall_score)
        
        # Quality should decrease with increasing noise
        for i in range(1, len(quality_scores)):
            assert quality_scores[i] <= quality_scores[i-1] + 0.1  # Allow small tolerance


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
