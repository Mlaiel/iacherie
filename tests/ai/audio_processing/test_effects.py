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

"""🧪 Audio Effects Tests - Industrial-Grade Effects Testing Suite

Comprehensive testing for professional audio effects and restoration including:
- EffectsProcessor validation
- AudioRestoration testing
- Professional effects quality assurance
- Real-time effects performance
- Audio quality preservation
- Effects chain validation

Created by Expert Team: Audio Developer + Backend Senior + ML Engineer
(c) 2025 Fahed Mlaiel. All rights reserved.
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
from scipy import signal
from scipy.signal import hilbert

# Import the audio processing module
try:
    from ai.audio_processing.effects import (
        EffectsProcessor, AudioRestoration, ReverbType, FilterType
    )
    from ai.audio_processing.core import AudioProcessor
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))
    from ai.audio_processing.effects import (
        EffectsProcessor, AudioRestoration, ReverbType, FilterType
    )
    from ai.audio_processing.core import AudioProcessor

from . import TEST_CONFIG, setup_test_environment


class TestEffectsProcessor:
    """
    Industrial-grade testing for EffectsProcessor class
    
    Test Coverage:
    - Reverb effects validation
    - Delay effects testing
    - Compression quality assurance
    - EQ frequency response
    - Distortion effects
    - Modulation effects
    - Effects chain processing
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """
Setup test environment before each test"""
        setup_test_environment()
        self.effects = EffectsProcessor()
        self.processor = AudioProcessor()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
    
    def test_initialization(self):
        """Test EffectsProcessor initialization"""
        effects = EffectsProcessor()
        assert effects is not None
        assert hasattr(effects, 'sample_rate')
        assert hasattr(effects, 'effects_chain')
        assert effects.sample_rate == 44100  # Default
    
    def test_apply_reverb_hall(self):
        """
Test hall reverb effect"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        reverb_audio = self.effects.apply_reverb(
            audio_data, 
            reverb_type=ReverbType.HALL,
            room_size=0.8,
            damping=0.5,
            wet_level=0.3,
            dry_level=0.7
        )
        
        assert reverb_audio is not None
        assert isinstance(reverb_audio, np.ndarray)
        assert len(reverb_audio) >= len(audio_data)  # May be longer due to reverb tail
        assert reverb_audio.dtype == np.float32
        assert not np.isnan(reverb_audio).any()
        assert not np.isinf(reverb_audio).any()
        
        # Reverb should increase the signal's duration/energy spread
        original_rms = np.sqrt(np.mean(audio_data**2))
        reverb_rms = np.sqrt(np.mean(reverb_audio[:len(audio_data)]**2))
        assert reverb_rms > original_rms * 0.8  # Should preserve most energy
    
    def test_apply_reverb_plate(self):
        """Test plate reverb effect"""
        audio_file = self.test_data_dir / "chirp_sweep.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        reverb_audio = self.effects.apply_reverb(
            audio_data,
            reverb_type=ReverbType.PLATE,
            room_size=0.6,
            damping=0.3,
            wet_level=0.4
        )
        
        assert reverb_audio is not None
        assert len(reverb_audio) >= len(audio_data)
        assert not np.array_equal(reverb_audio[:len(audio_data)], audio_data)  # Should be different
    
    def test_apply_delay(self):
        """Test delay effect"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        delay_audio = self.effects.apply_delay(
            audio_data,
            delay_time=0.25,  # 250ms delay
            feedback=0.3,
            wet_level=0.4,
            dry_level=0.6
        )
        
        assert delay_audio is not None
        assert len(delay_audio) >= len(audio_data)
        assert delay_audio.dtype == np.float32
        assert not np.isnan(delay_audio).any()
        
        # Check for delayed repetition in the signal
        delay_samples = int(0.25 * sample_rate)
        if len(audio_data) + delay_samples < len(delay_audio):
            delayed_portion = delay_audio[delay_samples:delay_samples + len(audio_data)]
            # There should be some correlation with the delayed signal
            correlation = np.corrcoef(audio_data, delayed_portion)[0, 1]
            assert correlation > 0.1  # Some similarity due to delay effect
    
    def test_apply_compression(self):
        """Test compression effect"""
        # Create audio with varying amplitude
        t = np.linspace(0, 2, 88200)  # 2 seconds
        varying_audio = np.concatenate([
            np.sin(2 * np.pi * 440 * t[:44100]) * 0.8,  # Loud part
            np.sin(2 * np.pi * 440 * t[44100:]) * 0.2   # Quiet part
        ])
        
        compressed_audio = self.effects.apply_compression(
            varying_audio,
            ratio=4.0,
            threshold=-20,  # dB
            attack=0.003,   # seconds
            release=0.1     # seconds
        )
        
        assert compressed_audio is not None
        assert len(compressed_audio) == len(varying_audio)
        assert compressed_audio.dtype == np.float32
        assert not np.isnan(compressed_audio).any()
        
        # Compression should reduce dynamic range
        original_dynamic_range = np.max(np.abs(varying_audio)) - np.min(np.abs(varying_audio))
        compressed_dynamic_range = np.max(np.abs(compressed_audio)) - np.min(np.abs(compressed_audio))
        assert compressed_dynamic_range <= original_dynamic_range
    
    def test_apply_eq_low_pass(self):
        """
Test low-pass EQ filter"""
        audio_file = self.test_data_dir / "white_noise.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        eq_audio = self.effects.apply_eq(
            audio_data,
            filter_type=FilterType.LOW_PASS,
            cutoff_freq=1000,  # Hz
            q_factor=0.707
        )
        
        assert eq_audio is not None
        assert len(eq_audio) == len(audio_data)
        assert eq_audio.dtype == np.float32
        assert not np.isnan(eq_audio).any()
        
        # Low-pass should reduce high-frequency content
        original_spectrum = np.abs(np.fft.fft(audio_data))
        eq_spectrum = np.abs(np.fft.fft(eq_audio))
        
        # Check high-frequency attenuation
        freqs = np.fft.fftfreq(len(audio_data), 1/sample_rate)
        high_freq_idx = freqs > 2000  # Above cutoff
        
        original_high_energy = np.mean(original_spectrum[high_freq_idx])
        eq_high_energy = np.mean(eq_spectrum[high_freq_idx])
        
        assert eq_high_energy < original_high_energy
    
    def test_apply_eq_high_pass(self):
        """Test high-pass EQ filter"""
        audio_file = self.test_data_dir / "white_noise.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        eq_audio = self.effects.apply_eq(
            audio_data,
            filter_type=FilterType.HIGH_PASS,
            cutoff_freq=1000,  # Hz
            q_factor=0.707
        )
        
        assert eq_audio is not None
        assert len(eq_audio) == len(audio_data)
        
        # High-pass should reduce low-frequency content
        original_spectrum = np.abs(np.fft.fft(audio_data))
        eq_spectrum = np.abs(np.fft.fft(eq_audio))
        
        freqs = np.fft.fftfreq(len(audio_data), 1/sample_rate)
        low_freq_idx = (freqs > 0) & (freqs < 500)  # Below cutoff
        
        original_low_energy = np.mean(original_spectrum[low_freq_idx])
        eq_low_energy = np.mean(eq_spectrum[low_freq_idx])
        
        assert eq_low_energy < original_low_energy
    
    def test_apply_parametric_eq(self):
        """Test parametric EQ"""
        audio_file = self.test_data_dir / "white_noise.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        # Boost at 1kHz
        eq_audio = self.effects.apply_parametric_eq(
            audio_data,
            center_freq=1000,
            gain_db=6.0,
            q_factor=2.0
        )
        
        assert eq_audio is not None
        assert len(eq_audio) == len(audio_data)
        assert eq_audio.dtype == np.float32
        
        # Should have more energy around 1kHz
        original_spectrum = np.abs(np.fft.fft(audio_data))
        eq_spectrum = np.abs(np.fft.fft(eq_audio))
        
        freqs = np.fft.fftfreq(len(audio_data), 1/sample_rate)
        target_freq_idx = (freqs > 950) & (freqs < 1050)
        
        original_target_energy = np.mean(original_spectrum[target_freq_idx])
        eq_target_energy = np.mean(eq_spectrum[target_freq_idx])
        
        assert eq_target_energy > original_target_energy
    
    def test_apply_distortion(self):
        """Test distortion effect"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        distorted_audio = self.effects.apply_distortion(
            audio_data,
            drive=0.5,
            tone=0.7,
            level=0.8
        )
        
        assert distorted_audio is not None
        assert len(distorted_audio) == len(audio_data)
        assert distorted_audio.dtype == np.float32
        assert not np.isnan(distorted_audio).any()
        
        # Distortion should add harmonic content
        original_spectrum = np.abs(np.fft.fft(audio_data))
        distorted_spectrum = np.abs(np.fft.fft(distorted_audio))
        
        # Check for increased harmonic content
        freqs = np.fft.fftfreq(len(audio_data), 1/sample_rate)
        harmonic_freqs = [880, 1320, 1760]  # 2nd, 3rd, 4th harmonics of 440Hz
        
        for harm_freq in harmonic_freqs:
            harm_idx = np.argmin(np.abs(freqs - harm_freq))
            if distorted_spectrum[harm_idx] > original_spectrum[harm_idx]:
                break
        else:
            # At least one harmonic should be enhanced
            assert False, "No harmonic enhancement detected"
    
    def test_apply_chorus(self):
        """Test chorus effect"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        chorus_audio = self.effects.apply_chorus(
            audio_data,
            rate=1.5,      # Hz
            depth=0.002,   # seconds
            feedback=0.1,
            wet_level=0.5
        )
        
        assert chorus_audio is not None
        assert len(chorus_audio) >= len(audio_data)
        assert chorus_audio.dtype == np.float32
        assert not np.isnan(chorus_audio).any()
        
        # Chorus should add slight modulation
        assert not np.array_equal(chorus_audio[:len(audio_data)], audio_data)
    
    def test_effects_chain(self):
        """Test effects chain processing"""
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        # Create effects chain: EQ -> Compression -> Reverb
        effects_chain = [
            ('eq', {'filter_type': FilterType.HIGH_PASS, 'cutoff_freq': 100}),
            ('compression', {'ratio': 3.0, 'threshold': -15}),
            ('reverb', {'reverb_type': ReverbType.HALL, 'wet_level': 0.2})
        ]
        
        processed_audio = self.effects.apply_effects_chain(audio_data, effects_chain)
        
        assert processed_audio is not None
        assert processed_audio.dtype == np.float32
        assert not np.isnan(processed_audio).any()
        assert not np.array_equal(processed_audio[:len(audio_data)], audio_data)
    
    def test_limiter(self):
        """Test limiter effect"""
        # Create audio with potential clipping
        loud_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100)) * 1.5
        
        limited_audio = self.effects.apply_limiter(
            loud_audio,
            threshold=-1.0,  # dB
            release=0.05     # seconds
        )
        
        assert limited_audio is not None
        assert len(limited_audio) == len(loud_audio)
        assert limited_audio.dtype == np.float32
        assert np.max(np.abs(limited_audio)) <= 1.0  # Should prevent clipping
        assert not np.isnan(limited_audio).any()
    
    def test_performance_benchmarking(self):
        """
Test effects processing performance"""
        audio_file = self.test_data_dir / "white_noise.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        start_time = time.time()
        
        # Apply multiple effects
        reverb_audio = self.effects.apply_reverb(audio_data, wet_level=0.3)
        compressed_audio = self.effects.apply_compression(reverb_audio, ratio=3.0)
        eq_audio = self.effects.apply_eq(compressed_audio, FilterType.LOW_PASS, 8000)
        
        end_time = time.time()
        processing_time_ms = (end_time - start_time) * 1000
        
        assert processing_time_ms < TEST_CONFIG["performance_threshold_ms"] * 3  # Allow 3x for effects
        assert eq_audio is not None


class TestAudioRestoration:
    """
    Industrial-grade testing for AudioRestoration class
    
    Test Coverage:
    - Noise reduction effectiveness
    - Click and pop removal
    - Spectral repair validation
    - Hum removal testing
    - Clipping restoration
    - Dynamic range restoration
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """
Setup test environment before each test"""
        setup_test_environment()
        self.restoration = AudioRestoration()
        self.processor = AudioProcessor()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
    
    def test_initialization(self):
        """Test AudioRestoration initialization"""
        restoration = AudioRestoration()
        assert restoration is not None
        assert hasattr(restoration, 'sample_rate')
        assert hasattr(restoration, 'noise_profile')
    
    def test_remove_noise_spectral(self):
        """
Test spectral noise reduction"""
        # Load noisy audio
        noisy_file = self.test_data_dir / "white_noise.wav"
        noisy_audio, sample_rate = self.processor.load_audio(str(noisy_file))
        
        # Apply noise reduction
        cleaned_audio = self.restoration.remove_noise(
            noisy_audio,
            method='spectral_subtraction',
            noise_factor=2.0
        )
        
        assert cleaned_audio is not None
        assert len(cleaned_audio) == len(noisy_audio)
        assert cleaned_audio.dtype == np.float32
        assert not np.isnan(cleaned_audio).any()
        
        # Cleaned audio should have lower energy
        original_rms = np.sqrt(np.mean(noisy_audio**2))
        cleaned_rms = np.sqrt(np.mean(cleaned_audio**2))
        assert cleaned_rms <= original_rms
    
    def test_remove_noise_wiener(self):
        """Test Wiener filter noise reduction"""
        noisy_file = self.test_data_dir / "white_noise.wav"
        noisy_audio, sample_rate = self.processor.load_audio(str(noisy_file))
        
        cleaned_audio = self.restoration.remove_noise(
            noisy_audio,
            method='wiener_filter',
            noise_estimate_duration=0.5
        )
        
        assert cleaned_audio is not None
        assert len(cleaned_audio) == len(noisy_audio)
        assert not np.array_equal(cleaned_audio, noisy_audio)  # Should be different
    
    def test_remove_clicks_and_pops(self):
        """Test click and pop removal"""
        # Create audio with artificial clicks
        clean_audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        clean_audio, sample_rate = self.processor.load_audio(str(clean_audio_file))
        
        # Add artificial clicks
        clicked_audio = clean_audio.copy()
        click_positions = [1000, 5000, 10000, 15000]
        for pos in click_positions:
            if pos < len(clicked_audio):
                clicked_audio[pos:pos+10] = 0.9 * np.sign(clicked_audio[pos])
        
        # Remove clicks
        declicked_audio = self.restoration.remove_clicks_and_pops(
            clicked_audio,
            threshold=0.8,
            window_size=20
        )
        
        assert declicked_audio is not None
        assert len(declicked_audio) == len(clicked_audio)
        assert declicked_audio.dtype == np.float32
        
        # Should be closer to original than clicked version
        original_mse = np.mean((clean_audio - clicked_audio)**2)
        restored_mse = np.mean((clean_audio - declicked_audio)**2)
        assert restored_mse < original_mse
    
    def test_remove_hum(self):
        """Test power line hum removal"""
        # Create audio with 50Hz hum
        clean_file = self.test_data_dir / "pure_tone_440hz.wav"
        clean_audio, sample_rate = self.processor.load_audio(str(clean_file))
        
        # Add 50Hz hum
        t = np.arange(len(clean_audio)) / sample_rate
        hum = 0.1 * np.sin(2 * np.pi * 50 * t)
        hummed_audio = clean_audio + hum
        
        # Remove hum
        dehum_audio = self.restoration.remove_hum(
            hummed_audio,
            hum_frequency=50,
            q_factor=30
        )
        
        assert dehum_audio is not None
        assert len(dehum_audio) == len(hummed_audio)
        
        # Should reduce 50Hz component
        hummed_spectrum = np.abs(np.fft.fft(hummed_audio))
        dehum_spectrum = np.abs(np.fft.fft(dehum_audio))
        
        freqs = np.fft.fftfreq(len(hummed_audio), 1/sample_rate)
        hum_freq_idx = np.argmin(np.abs(freqs - 50))
        
        assert dehum_spectrum[hum_freq_idx] < hummed_spectrum[hum_freq_idx]
    
    def test_repair_clipping(self):
        """Test clipping repair"""
        # Create clipped audio
        clean_file = self.test_data_dir / "pure_tone_440hz.wav"
        clean_audio, sample_rate = self.processor.load_audio(str(clean_file))
        
        # Artificially clip the audio
        clipped_audio = np.clip(clean_audio * 2.0, -0.8, 0.8)
        
        # Repair clipping
        repaired_audio = self.restoration.repair_clipping(
            clipped_audio,
            threshold=0.75
        )
        
        assert repaired_audio is not None
        assert len(repaired_audio) == len(clipped_audio)
        assert repaired_audio.dtype == np.float32
        
        # Should reduce clipping artifacts
        clipped_samples = np.sum(np.abs(clipped_audio) >= 0.79)
        repaired_samples = np.sum(np.abs(repaired_audio) >= 0.79)
        assert repaired_samples < clipped_samples
    
    def test_restore_dynamics(self):
        """Test dynamic range restoration"""
        # Create over-compressed audio
        clean_file = self.test_data_dir / "chirp_sweep.wav"
        clean_audio, sample_rate = self.processor.load_audio(str(clean_file))
        
        # Over-compress (reduce dynamics)
        compressed_audio = np.tanh(clean_audio * 5) * 0.3
        
        # Restore dynamics
        restored_audio = self.restoration.restore_dynamics(
            compressed_audio,
            target_dynamic_range=0.8
        )
        
        assert restored_audio is not None
        assert len(restored_audio) == len(compressed_audio)
        
        # Should increase dynamic range
        compressed_range = np.max(compressed_audio) - np.min(compressed_audio)
        restored_range = np.max(restored_audio) - np.min(restored_audio)
        assert restored_range >= compressed_range
    
    def test_spectral_repair(self):
        """Test spectral repair for missing frequencies"""
        audio_file = self.test_data_dir / "white_noise.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        # Create spectral hole (remove frequencies around 2kHz)
        spectrum = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(audio_data), 1/sample_rate)
        
        # Zero out frequencies around 2kHz
        mask = (np.abs(freqs) > 1800) & (np.abs(freqs) < 2200)
        spectrum[mask] = 0
        damaged_audio = np.real(np.fft.ifft(spectrum))
        
        # Repair spectrum
        repaired_audio = self.restoration.spectral_repair(
            damaged_audio.astype(np.float32),
            frequency_range=(1800, 2200)
        )
        
        assert repaired_audio is not None
        assert len(repaired_audio) == len(damaged_audio)
        assert repaired_audio.dtype == np.float32
        
        # Should restore some energy in the repaired band
        repaired_spectrum = np.abs(np.fft.fft(repaired_audio))
        damaged_spectrum = np.abs(np.fft.fft(damaged_audio))
        
        repair_band_energy = np.mean(repaired_spectrum[mask])
        damaged_band_energy = np.mean(damaged_spectrum[mask])
        
        assert repair_band_energy > damaged_band_energy
    
    def test_comprehensive_restoration(self):
        """Test comprehensive audio restoration"""
        audio_file = self.test_data_dir / "white_noise.wav"
        audio_data, sample_rate = self.processor.load_audio(str(audio_file))
        
        # Apply comprehensive restoration
        restored_audio = self.restoration.comprehensive_restore(
            audio_data,
            remove_noise=True,
            remove_clicks=True,
            remove_hum=True,
            repair_clipping=True
        )
        
        assert restored_audio is not None
        assert len(restored_audio) == len(audio_data)
        assert restored_audio.dtype == np.float32
        assert not np.isnan(restored_audio).any()
        assert not np.isinf(restored_audio).any()


class TestReverbType:
    """Test ReverbType enumeration"""
    
    def test_reverb_types(self):
        """
Test all reverb types are available"""
        assert hasattr(ReverbType, 'HALL')
        assert hasattr(ReverbType, 'ROOM')
        assert hasattr(ReverbType, 'PLATE')
        assert hasattr(ReverbType, 'SPRING')
        assert hasattr(ReverbType, 'CHAMBER')


class TestFilterType:
    """
Test FilterType enumeration"""
    
    def test_filter_types(self):
        """
Test all filter types are available"""
        assert hasattr(FilterType, 'LOW_PASS')
        assert hasattr(FilterType, 'HIGH_PASS')
        assert hasattr(FilterType, 'BAND_PASS')
        assert hasattr(FilterType, 'BAND_STOP')
        assert hasattr(FilterType, 'NOTCH')


class TestEffectsIntegration:
    """
    Integration tests for effects workflow
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """
Setup test environment"""
        setup_test_environment()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
    
    def test_effects_and_restoration_workflow(self):
        """Test complete effects and restoration workflow"""
        # Load audio
        processor = AudioProcessor()
        audio_file = self.test_data_dir / "white_noise.wav"
        audio_data, sample_rate = processor.load_audio(str(audio_file))
        
        # First restore
        restoration = AudioRestoration()
        cleaned_audio = restoration.remove_noise(audio_data)
        
        # Then apply effects
        effects = EffectsProcessor()
        enhanced_audio = effects.apply_compression(cleaned_audio, ratio=2.0)
        final_audio = effects.apply_reverb(enhanced_audio, wet_level=0.2)
        
        # Verify workflow
        assert cleaned_audio is not None
        assert enhanced_audio is not None
        assert final_audio is not None
        assert len(final_audio) >= len(audio_data)
    
    def test_real_time_effects_simulation(self):
        """Test real-time effects processing simulation"""
        processor = AudioProcessor()
        effects = EffectsProcessor()
        
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = processor.load_audio(str(audio_file))
        
        # Simulate chunk-based processing
        chunk_size = 1024
        processed_chunks = []
        
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            if len(chunk) < chunk_size:
                # Pad last chunk
                chunk = np.pad(chunk, (0, chunk_size - len(chunk)))
            
            # Apply real-time effects
            processed_chunk = effects.apply_compression(chunk, ratio=2.0)
            processed_chunks.append(processed_chunk)
        
        # Reconstruct processed audio
        processed_audio = np.concatenate(processed_chunks)[:len(audio_data)]
        
        assert processed_audio is not None
        assert len(processed_audio) == len(audio_data)
        assert not np.array_equal(processed_audio, audio_data)


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
