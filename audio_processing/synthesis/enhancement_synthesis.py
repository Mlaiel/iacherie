"""
 Audio Enhancement Synthesis Engine - Advanced Audio Enhancement and Spatial Processing

This module provides comprehensive audio enhancement capabilities including
upsampling, spatial audio, and immersive audio generation.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

 LEGAL WARNING: Unauthorized use prohibited. Contact mlaiel@live.de for licensing.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from pathlib import Path
import logging
from abc import ABC, abstractmethod
from enum import Enum
import librosa
import scipy.signal
from scipy.spatial.distance import cdist
from scipy.interpolate import interp1d
import math

logger = logging.getLogger(__name__)


class SpatialFormat(Enum):
    """Spatial audio format types."""
    STEREO = "stereo"
    SURROUND_5_1 = "5.1"
    SURROUND_7_1 = "7.1"
    BINAURAL = "binaural"
    AMBISONICS_1ST = "ambisonics_1st"
    AMBISONICS_2ND = "ambisonics_2nd"
    AMBISONICS_3RD = "ambisonics_3rd"


class HRTFDatabase:
    """HRTF (Head-Related Transfer Function) database for spatial audio."""
    
    def __init__(self):
        self.hrtfs: Dict[Tuple[float, float], Dict[str, np.ndarray]] = {}
        self.sample_rate = 44100
        self.hrtf_length = 512
        
        # Generate simplified HRTF database
        self._generate_simplified_hrtf()
        
    def _generate_simplified_hrtf(self) -> None:
        """Generate simplified HRTF responses."""
        # Azimuth angles (degrees)
        azimuths = np.arange(0, 360, 15)
        # Elevation angles (degrees)
        elevations = np.arange(-45, 90, 15)
        
        for azimuth in azimuths:
            for elevation in elevations:
                # Convert to radians
                az_rad = np.radians(azimuth)
                el_rad = np.radians(elevation)
                
                # Generate simplified HRTF responses
                left_hrtf = self._generate_hrtf_response(az_rad, el_rad, 'left')
                right_hrtf = self._generate_hrtf_response(az_rad, el_rad, 'right')
                
                self.hrtfs[(azimuth, elevation)] = {
                    'left': left_hrtf,
                    'right': right_hrtf
                }
                
        logger.info(f"Generated HRTF database with {len(self.hrtfs)} positions")
        
    def _generate_hrtf_response(self, azimuth: float, elevation: float, ear: str) -> np.ndarray:
        """Generate simplified HRTF response for given position and ear."""
        # Simplified HRTF modeling
        freqs = np.fft.fftfreq(self.hrtf_length, 1/self.sample_rate)[:self.hrtf_length//2 + 1]
        
        # Interaural time difference (ITD)
        head_radius = 0.0875  # Average head radius in meters
        sound_speed = 343.0   # Speed of sound in m/s
        
        if ear == 'left':
            angle_diff = azimuth
        else:
            angle_diff = azimuth - np.pi
            
        itd = head_radius * np.sin(angle_diff) / sound_speed
        
        # Interaural level difference (ILD) - frequency dependent
        ild = self._calculate_ild(azimuth, elevation, freqs, ear)
        
        # Create complex HRTF
        magnitude_response = ild
        phase_response = -2 * np.pi * freqs * itd
        
        # Add head shadowing effects
        head_shadow = self._calculate_head_shadow(azimuth, elevation, freqs, ear)
        magnitude_response *= head_shadow
        
        # Create complex spectrum
        complex_response = magnitude_response * np.exp(1j * phase_response)
        
        # Convert to impulse response
        # Mirror spectrum for real IFFT
        full_spectrum = np.concatenate([
            complex_response,
            np.conj(complex_response[-2:0:-1])
        ])
        
        hrtf_ir = np.real(np.fft.ifft(full_spectrum))
        
        # Apply window and truncate
        window = np.hanning(len(hrtf_ir))
        hrtf_ir = hrtf_ir * window
        
        return hrtf_ir[:self.hrtf_length].astype(np.float32)
        
    def _calculate_ild(self, azimuth: float, elevation: float, freqs: np.ndarray, ear: str) -> np.ndarray:
        """Calculate interaural level difference."""
        # Simplified ILD model
        if ear == 'left':
            angle_factor = np.cos(azimuth)
        else:
            angle_factor = np.cos(azimuth - np.pi)
            
        # Frequency-dependent shadowing
        freq_factor = 1 + 0.5 * freqs / (freqs[-1] + 1e-8)
        
        ild = np.abs(angle_factor) * freq_factor
        return np.clip(ild, 0.1, 2.0)
        
    def _calculate_head_shadow(self, azimuth: float, elevation: float, freqs: np.ndarray, ear: str) -> np.ndarray:
        """Calculate head shadowing effects."""
        # Simplified head shadow model
        if ear == 'left':
            shadow_angle = azimuth
        else:
            shadow_angle = azimuth - np.pi
            
        # High frequencies are more affected by head shadowing
        freq_ratio = freqs / (freqs[-1] + 1e-8)
        shadow_factor = 1 - 0.3 * np.abs(np.sin(shadow_angle)) * freq_ratio
        
        return np.clip(shadow_factor, 0.1, 1.0)
        
    def get_hrtf(self, azimuth: float, elevation: float) -> Dict[str, np.ndarray]:
        """Get HRTF for specific direction (with interpolation)."""
        # Find nearest angles
        available_angles = list(self.hrtfs.keys())
        
        if (azimuth, elevation) in self.hrtfs:
            return self.hrtfs[(azimuth, elevation)]
            
        # Find closest match
        distances = [abs(az - azimuth) + abs(el - elevation) 
                    for az, el in available_angles]
        closest_idx = np.argmin(distances)
        closest_angles = available_angles[closest_idx]
        
        return self.hrtfs[closest_angles]


@dataclass
class SpatialConfig:
    """Configuration for spatial audio processing."""
    sample_rate: int = 44100
    format: SpatialFormat = SpatialFormat.STEREO
    room_size: Tuple[float, float, float] = (10.0, 8.0, 3.0)  # width, depth, height in meters
    listener_position: Tuple[float, float, float] = (5.0, 4.0, 1.7)  # x, y, z in meters
    reverb_time: float = 1.2  # seconds
    air_absorption: bool = True
    doppler_effect: bool = True


class AudioUpsampling:
    """Advanced audio upsampling with neural enhancement."""
    
    def __init__(self, target_sample_rate: int = 48000):
        self.target_sample_rate = target_sample_rate
        
        # Neural upsampling network
        self.upsampling_net = self._build_upsampling_network()
        
    def _build_upsampling_network(self) -> nn.Module:
        """Build neural network for upsampling enhancement."""
        class UpsamplingNet(nn.Module):
            def __init__(self):
                super().__init__()
                
                # Encoder layers
                self.encoder = nn.Sequential(
                    nn.Conv1d(1, 64, kernel_size=15, padding=7),
                    nn.ReLU(),
                    nn.Conv1d(64, 128, kernel_size=9, padding=4),
                    nn.ReLU(),
                    nn.Conv1d(128, 256, kernel_size=5, padding=2),
                    nn.ReLU()
                )
                
                # Upsampling layers
                self.upsampler = nn.Sequential(
                    nn.ConvTranspose1d(256, 128, kernel_size=4, stride=2, padding=1),
                    nn.ReLU(),
                    nn.ConvTranspose1d(128, 64, kernel_size=4, stride=2, padding=1),
                    nn.ReLU(),
                    nn.Conv1d(64, 1, kernel_size=7, padding=3),
                    nn.Tanh()
                )
                
            def forward(self, x):
                encoded = self.encoder(x)
                upsampled = self.upsampler(encoded)
                return upsampled
                
        return UpsamplingNet()
        
    def upsample(self, audio: np.ndarray, source_sample_rate: int) -> np.ndarray:
        """Upsample audio with neural enhancement."""
        if source_sample_rate >= self.target_sample_rate:
            return audio
            
        # Calculate upsampling factor
        upsample_factor = self.target_sample_rate / source_sample_rate
        
        # Traditional upsampling first
        upsampled_length = int(len(audio) * upsample_factor)
        upsampled_audio = scipy.signal.resample(audio, upsampled_length)
        
        # Neural enhancement
        if self.upsampling_net is not None:
            upsampled_audio = self._apply_neural_enhancement(upsampled_audio)
            
        return upsampled_audio.astype(np.float32)
        
    def _apply_neural_enhancement(self, audio: np.ndarray) -> np.ndarray:
        """Apply neural enhancement to upsampled audio."""
        # Prepare input tensor
        audio_tensor = torch.FloatTensor(audio).unsqueeze(0).unsqueeze(0)
        
        # Apply neural network
        with torch.no_grad():
            enhanced_tensor = self.upsampling_net(audio_tensor)
            
        # Convert back to numpy
        enhanced_audio = enhanced_tensor.squeeze().cpu().numpy()
        
        return enhanced_audio
        
    def batch_upsample(self, audio_list: List[np.ndarray], 
                      source_sample_rate: int) -> List[np.ndarray]:
        """Batch upsample multiple audio files."""



        return [self.upsample(audio, source_sample_rate) for audio in audio_list]


class StereoEnhancement:
    """Stereo enhancement and widening effects."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
    def enhance_stereo_width(self, stereo_audio: np.ndarray, width: float = 1.5) -> np.ndarray:
        """Enhance stereo width using M-S processing."""
        if stereo_audio.shape[1] != 2:
            raise ValueError("Input must be stereo (2 channels)")
            
        left = stereo_audio[:, 0]
        right = stereo_audio[:, 1]
        
        # Convert to Mid-Side
        mid = (left + right) * 0.5
        side = (left - right) * 0.5
        
        # Enhance side signal
        enhanced_side = side * width
        
        # Convert back to Left-Right
        enhanced_left = mid + enhanced_side
        enhanced_right = mid - enhanced_side
        
        # Combine channels
        enhanced_stereo = np.column_stack([enhanced_left, enhanced_right])
        
        return enhanced_stereo.astype(np.float32)
        
    def pseudo_stereo(self, mono_audio: np.ndarray, separation: float = 0.3) -> np.ndarray:
        """Create pseudo-stereo from mono audio."""
        # Delay-based stereo effect
        delay_samples = int(separation * 0.001 * self.sample_rate)  # separation in ms
        
        left_channel = mono_audio
        right_channel = np.concatenate([
            np.zeros(delay_samples),
            mono_audio[:-delay_samples] if delay_samples < len(mono_audio) else mono_audio
        ])
        
        # Add slight filtering differences
        left_filtered = self._apply_subtle_filter(left_channel, 'high')
        right_filtered = self._apply_subtle_filter(right_channel, 'low')
        
        stereo_audio = np.column_stack([left_filtered, right_filtered])
        
        return stereo_audio.astype(np.float32)
        
    def _apply_subtle_filter(self, audio: np.ndarray, filter_type: str) -> np.ndarray:
        """Apply subtle filtering for stereo separation."""
        nyquist = self.sample_rate / 2
        
        if filter_type == 'high':
            # Slight high-frequency emphasis
            b, a = scipy.signal.butter(2, 5000 / nyquist, 'high')
            filtered = scipy.signal.filtfilt(b, a, audio)
            return 0.95 * audio + 0.05 * filtered
        else:
            # Slight low-frequency emphasis
            b, a = scipy.signal.butter(2, 3000 / nyquist, 'low')
            filtered = scipy.signal.filtfilt(b, a, audio)
            return 0.95 * audio + 0.05 * filtered
            
    def haas_effect(self, stereo_audio: np.ndarray, delay_ms: float = 15.0,
                   mix: float = 0.5) -> np.ndarray:
        """Apply Haas effect for spatial enhancement."""
        if stereo_audio.shape[1] != 2:
            raise ValueError("Input must be stereo")
            
        delay_samples = int(delay_ms * 0.001 * self.sample_rate)
        
        left = stereo_audio[:, 0]
        right = stereo_audio[:, 1]
        
        # Create delayed versions
        delayed_left = np.concatenate([np.zeros(delay_samples), left[:-delay_samples]])
        delayed_right = np.concatenate([np.zeros(delay_samples), right[:-delay_samples]])
        
        # Mix original with delayed
        enhanced_left = (1 - mix) * left + mix * delayed_right
        enhanced_right = (1 - mix) * right + mix * delayed_left
        
        return np.column_stack([enhanced_left, enhanced_right]).astype(np.float32)


class SpatialAudioSynthesis:
    """Spatial audio synthesis with HRTF and room modeling."""
    
    def __init__(self, config: SpatialConfig):
        self.config = config
        self.hrtf_db = HRTFDatabase()
        
        # Room impulse response
        self.room_ir = self._generate_room_impulse_response()
        
    def _generate_room_impulse_response(self) -> np.ndarray:
        """Generate room impulse response for reverb."""
        # Simplified room modeling
        reverb_length = int(self.config.reverb_time * self.config.sample_rate)
        
        # Generate exponentially decaying noise
        decay_envelope = np.exp(-np.linspace(0, 5, reverb_length))
        noise = np.random.randn(reverb_length) * decay_envelope
        
        # Add early reflections
        early_reflections = self._generate_early_reflections()
        
        # Combine
        room_ir = np.zeros(reverb_length)
        room_ir[:len(early_reflections)] = early_reflections
        room_ir += 0.3 * noise
        
        return room_ir.astype(np.float32)
        
    def _generate_early_reflections(self) -> np.ndarray:
        """Generate early reflections based on room geometry."""
        width, depth, height = self.config.room_size
        listener_x, listener_y, listener_z = self.config.listener_position
        
        # Calculate reflection delays
        reflections = []
        
        # Wall reflections
        wall_distances = [
            listener_x,                    # Left wall
            width - listener_x,           # Right wall  
            listener_y,                   # Front wall
            depth - listener_y,          # Back wall
            listener_z,                   # Floor
            height - listener_z          # Ceiling
        ]
        
        for i, distance in enumerate(wall_distances):
            delay_samples = int(2 * distance * self.config.sample_rate / 343.0)  # Round trip
            if delay_samples < 1000:  # Only early reflections
                amplitude = 0.7 ** (i + 1)  # Decay with each reflection
                reflections.append((delay_samples, amplitude))
                
        # Create impulse response
        max_delay = max([delay for delay, _ in reflections]) if reflections else 100
        early_ir = np.zeros(max_delay + 100)
        
        for delay, amplitude in reflections:
            early_ir[delay] = amplitude
            
        return early_ir
        
    def spatialize_mono_source(self, mono_audio: np.ndarray, 
                              azimuth: float, elevation: float = 0.0,
                              distance: float = 1.0) -> np.ndarray:
        """Spatialize mono audio source at specified position."""
        # Get HRTFs for the direction
        hrtfs = self.hrtf_db.get_hrtf(azimuth, elevation)
        
        # Convolve with HRTFs
        left_spatialized = scipy.signal.convolve(mono_audio, hrtfs['left'], mode='same')
        right_spatialized = scipy.signal.convolve(mono_audio, hrtfs['right'], mode='same')
        
        # Apply distance attenuation
        distance_factor = 1.0 / max(distance, 0.1)  # Prevent division by zero
        left_spatialized *= distance_factor
        right_spatialized *= distance_factor
        
        # Apply air absorption for distant sources
        if self.config.air_absorption and distance > 2.0:
            left_spatialized = self._apply_air_absorption(left_spatialized, distance)
            right_spatialized = self._apply_air_absorption(right_spatialized, distance)
            
        # Add room reverb
        if len(self.room_ir) > 0:
            left_reverb = scipy.signal.convolve(left_spatialized, self.room_ir, mode='same')
            right_reverb = scipy.signal.convolve(right_spatialized, self.room_ir, mode='same')
            
            # Mix direct sound with reverb
            reverb_mix = 0.2
            left_spatialized = (1 - reverb_mix) * left_spatialized + reverb_mix * left_reverb
            right_spatialized = (1 - reverb_mix) * right_spatialized + reverb_mix * right_reverb
            
        # Combine channels
        spatialized = np.column_stack([left_spatialized, right_spatialized])
        
        return spatialized.astype(np.float32)
        
    def _apply_air_absorption(self, audio: np.ndarray, distance: float) -> np.ndarray:
        """Apply high-frequency attenuation due to air absorption."""
        # Air absorption is frequency-dependent (higher frequencies attenuated more)
        nyquist = self.config.sample_rate / 2
        
        # Calculate absorption coefficient based on distance
        absorption_coef = min(0.3, distance * 0.01)  # Simple model
        
        # Apply high-frequency rolloff
        cutoff_freq = 8000 * (1 - absorption_coef)  # Lower cutoff for more distant sources
        b, a = scipy.signal.butter(2, cutoff_freq / nyquist, 'low')
        
        return scipy.signal.filtfilt(b, a, audio)
        
    def create_moving_source(self, mono_audio: np.ndarray, 
                           trajectory: List[Tuple[float, float, float]]) -> np.ndarray:
        """Create moving sound source with Doppler effect."""
        if not trajectory:
            return self.spatialize_mono_source(mono_audio, 0, 0, 1)
            
        samples_per_position = len(mono_audio) // len(trajectory)
        output_audio = []
        
        for i, (azimuth, elevation, distance) in enumerate(trajectory):
            start_idx = i * samples_per_position
            end_idx = min((i + 1) * samples_per_position, len(mono_audio))
            
            audio_segment = mono_audio[start_idx:end_idx]
            
            # Apply Doppler effect if enabled
            if self.config.doppler_effect and i > 0:
                prev_distance = trajectory[i-1][2]
                velocity = (distance - prev_distance) / (samples_per_position / self.config.sample_rate)
                audio_segment = self._apply_doppler_effect(audio_segment, velocity)
                
            # Spatialize segment
            spatialized_segment = self.spatialize_mono_source(
                audio_segment, azimuth, elevation, distance
            )
            
            output_audio.append(spatialized_segment)
            
        return np.vstack(output_audio) if output_audio else np.zeros((len(mono_audio), 2))
        
    def _apply_doppler_effect(self, audio: np.ndarray, velocity: float) -> np.ndarray:
        """Apply Doppler effect for moving sources."""
        sound_speed = 343.0  # m/s
        
        # Calculate frequency shift
        doppler_factor = sound_speed / (sound_speed + velocity)
        
        # Apply time stretching to simulate Doppler effect
        if abs(doppler_factor - 1.0) > 0.01:  # Only apply if significant
            stretched = librosa.effects.time_stretch(audio, rate=doppler_factor)
            
            # Ensure same length as input
            if len(stretched) != len(audio):
                stretched = scipy.signal.resample(stretched, len(audio))
                
            return stretched
            
        return audio


class ImmersiveAudioGenerator:
    """Generate immersive audio experiences."""
    
    def __init__(self, config: SpatialConfig):
        self.config = config
        self.spatial_synthesizer = SpatialAudioSynthesis(config)
        
    def create_soundscape(self, audio_sources: Dict[str, Dict]) -> np.ndarray:
        """Create immersive soundscape from multiple sources.
        
        Args:
            audio_sources: Dict with source_name -> {
                'audio': np.ndarray,
                'position': (azimuth, elevation, distance),
                'trajectory': optional list of positions for movement
            }
        """
        if not audio_sources:
            return np.zeros((1000, 2), dtype=np.float32)
            
        # Find maximum length
        max_length = max(len(source['audio']) for source in audio_sources.values())
        
        # Initialize output
        output = np.zeros((max_length, 2), dtype=np.float32)
        
        # Process each source
        for source_name, source_info in audio_sources.items():
            audio = source_info['audio']
            
            if 'trajectory' in source_info:
                # Moving source
                spatialized = self.spatial_synthesizer.create_moving_source(
                    audio, source_info['trajectory']
                )
            else:
                # Static source
                azimuth, elevation, distance = source_info['position']
                spatialized = self.spatial_synthesizer.spatialize_mono_source(
                    audio, azimuth, elevation, distance
                )
                
            # Add to mix (pad if necessary)
            if len(spatialized) < max_length:
                padding = np.zeros((max_length - len(spatialized), 2))
                spatialized = np.vstack([spatialized, padding])
            elif len(spatialized) > max_length:
                spatialized = spatialized[:max_length]
                
            output += spatialized
            
        # Normalize to prevent clipping
        max_amplitude = np.max(np.abs(output))
        if max_amplitude > 1.0:
            output /= max_amplitude
            
        return output.astype(np.float32)
        
    def create_reverb_zones(self, audio: np.ndarray, zones: List[Dict]) -> np.ndarray:
        """Create different reverb zones in the soundscape."""
        # Simplified implementation - would be more complex in practice
        output = audio.copy()
        
        for zone in zones:
            reverb_type = zone.get('type', 'hall')
            mix_level = zone.get('mix', 0.3)
            
            # Generate zone-specific reverb
            zone_reverb = self._generate_zone_reverb(audio, reverb_type)
            
            # Mix with original
            output = (1 - mix_level) * output + mix_level * zone_reverb
            
        return output.astype(np.float32)
        
    def _generate_zone_reverb(self, audio: np.ndarray, reverb_type: str) -> np.ndarray:
        """Generate reverb for specific acoustic zone."""
        reverb_configs = {
            'hall': {'reverb_time': 2.5, 'damping': 0.7},
            'room': {'reverb_time': 1.0, 'damping': 0.8},
            'cathedral': {'reverb_time': 4.0, 'damping': 0.5},
            'chamber': {'reverb_time': 0.8, 'damping': 0.9}
        }
        
        config = reverb_configs.get(reverb_type, reverb_configs['room'])
        
        # Generate impulse response
        reverb_length = int(config['reverb_time'] * self.config.sample_rate)
        decay = np.exp(-np.linspace(0, 8, reverb_length)) * config['damping']
        reverb_ir = np.random.randn(reverb_length) * decay
        
        # Apply reverb to each channel
        if len(audio.shape) == 1:
            # Mono
            return scipy.signal.convolve(audio, reverb_ir, mode='same')
        else:
            # Stereo
            left_reverb = scipy.signal.convolve(audio[:, 0], reverb_ir, mode='same')
            right_reverb = scipy.signal.convolve(audio[:, 1], reverb_ir, mode='same')
            return np.column_stack([left_reverb, right_reverb])


class BinauralSynthesis:
    """Binaural synthesis for headphone listening."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.hrtf_db = HRTFDatabase()
        
    def synthesize_binaural_beats(self, base_frequency: float, beat_frequency: float,
                                duration: float, amplitude: float = 0.3) -> np.ndarray:
        """Generate binaural beats for brainwave entrainment."""
        num_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, num_samples)
        
        # Left ear: base frequency
        left_signal = amplitude * np.sin(2 * np.pi * base_frequency * t)
        
        # Right ear: base frequency + beat frequency
        right_frequency = base_frequency + beat_frequency
        right_signal = amplitude * np.sin(2 * np.pi * right_frequency * t)
        
        # Combine channels
        binaural_audio = np.column_stack([left_signal, right_signal])
        
        return binaural_audio.astype(np.float32)
        
    def create_3d_soundfield(self, sources: List[Dict]) -> np.ndarray:
        """Create 3D sound field for binaural listening."""
        if not sources:
            return np.zeros((1000, 2), dtype=np.float32)
            
        max_length = max(len(source['audio']) for source in sources)
        output = np.zeros((max_length, 2), dtype=np.float32)
        
        for source in sources:
            audio = source['audio']
            azimuth = source.get('azimuth', 0)
            elevation = source.get('elevation', 0)
            distance = source.get('distance', 1.0)
            
            # Get HRTFs
            hrtfs = self.hrtf_db.get_hrtf(azimuth, elevation)
            
            # Apply distance attenuation
            distance_factor = 1.0 / max(distance, 0.1)
            
            # Convolve with HRTFs
            left_binauralized = scipy.signal.convolve(audio, hrtfs['left'], mode='same')
            right_binauralized = scipy.signal.convolve(audio, hrtfs['right'], mode='same')
            
            # Apply distance
            left_binauralized *= distance_factor
            right_binauralized *= distance_factor
            
            # Pad or truncate to match output length
            if len(left_binauralized) < max_length:
                padding = np.zeros(max_length - len(left_binauralized))
                left_binauralized = np.concatenate([left_binauralized, padding])
                right_binauralized = np.concatenate([right_binauralized, padding])
            else:
                left_binauralized = left_binauralized[:max_length]
                right_binauralized = right_binauralized[:max_length]
                
            # Add to output
            output[:, 0] += left_binauralized
            output[:, 1] += right_binauralized
            
        # Normalize
        max_amplitude = np.max(np.abs(output))
        if max_amplitude > 1.0:
            output /= max_amplitude
            
        return output.astype(np.float32)


class AmbisonicsGenerator:
    """Ambisonics encoding and decoding for 360-degree audio."""
    
    def __init__(self, order: int = 1, sample_rate: int = 44100):
        self.order = order
        self.sample_rate = sample_rate
        self.num_channels = (order + 1) ** 2
        
    def encode_source(self, mono_audio: np.ndarray, azimuth: float, 
                     elevation: float) -> np.ndarray:
        """Encode mono source to Ambisonics format."""
        # Convert angles to radians
        az_rad = np.radians(azimuth)
        el_rad = np.radians(elevation)
        
        # Calculate spherical harmonics coefficients
        coefficients = self._calculate_spherical_harmonics(az_rad, el_rad)
        
        # Encode audio
        encoded = np.zeros((len(mono_audio), self.num_channels), dtype=np.float32)
        
        for i, coeff in enumerate(coefficients):
            encoded[:, i] = mono_audio * coeff
            
        return encoded
        
    def _calculate_spherical_harmonics(self, azimuth: float, elevation: float) -> List[float]:
        """Calculate spherical harmonics coefficients."""
        coefficients = []
        
        for n in range(self.order + 1):
            for m in range(-n, n + 1):
                # Simplified spherical harmonics calculation
                # In practice, would use proper spherical harmonics formulas
                if n == 0:  # W channel
                    coeff = 1.0
                elif n == 1:
                    if m == -1:  # Y channel
                        coeff = np.sin(azimuth) * np.cos(elevation)
                    elif m == 0:  # Z channel
                        coeff = np.sin(elevation)
                    else:  # X channel
                        coeff = np.cos(azimuth) * np.cos(elevation)
                else:
                    # Higher order terms (simplified)
                    coeff = np.cos(n * azimuth + m * elevation) * 0.5
                    
                coefficients.append(coeff)
                
        return coefficients
        
    def decode_to_stereo(self, ambisonics_audio: np.ndarray) -> np.ndarray:
        """Decode Ambisonics to stereo."""
        if ambisonics_audio.shape[1] < 4:
            raise ValueError("Minimum first-order Ambisonics required (4 channels)")
            
        # Simple stereo decode (for better results, use proper decoder matrices)
        W = ambisonics_audio[:, 0]  # W channel
        X = ambisonics_audio[:, 1]  # X channel
        Y = ambisonics_audio[:, 2]  # Y channel
        
        # Stereo decode
        left = W + 0.707 * (X - Y)
        right = W + 0.707 * (X + Y)
        
        stereo_audio = np.column_stack([left, right])
        
        return stereo_audio.astype(np.float32)
        
    def rotate_soundfield(self, ambisonics_audio: np.ndarray, 
                         rotation_angles: Tuple[float, float, float]) -> np.ndarray:
        """Rotate Ambisonics soundfield."""
        # Simplified rotation - would use proper rotation matrices in practice
        yaw, pitch, roll = rotation_angles
        
        # Apply rotation to higher-order channels
        rotated = ambisonics_audio.copy()
        
        # Simple first-order rotation
        if self.num_channels >= 4:
            cos_yaw = np.cos(np.radians(yaw))
            sin_yaw = np.sin(np.radians(yaw))
            
            # Rotate X and Y channels
            new_x = cos_yaw * ambisonics_audio[:, 1] - sin_yaw * ambisonics_audio[:, 2]
            new_y = sin_yaw * ambisonics_audio[:, 1] + cos_yaw * ambisonics_audio[:, 2]
            
            rotated[:, 1] = new_x
            rotated[:, 2] = new_y
            
        return rotated


class SurroundSoundSynthesis:
    """Surround sound synthesis for multi-channel systems."""
    
    def __init__(self, format: SpatialFormat = SpatialFormat.SURROUND_5_1):
        self.format = format
        self.channel_positions = self._get_channel_positions()
        
    def _get_channel_positions(self) -> Dict[str, Tuple[float, float]]:
        """Get speaker positions for surround format."""
        if self.format == SpatialFormat.SURROUND_5_1:
            return {
                'front_left': (-30, 0),
                'front_right': (30, 0),
                'center': (0, 0),
                'lfe': (0, 0),  # Subwoofer
                'surround_left': (-110, 0),
                'surround_right': (110, 0)
            }
        elif self.format == SpatialFormat.SURROUND_7_1:
            return {
                'front_left': (-30, 0),
                'front_right': (30, 0),
                'center': (0, 0),
                'lfe': (0, 0),
                'side_left': (-90, 0),
                'side_right': (90, 0),
                'rear_left': (-150, 0),
                'rear_right': (150, 0)
            }
        else:
            return {'left': (-30, 0), 'right': (30, 0)}
            
    def encode_to_surround(self, mono_audio: np.ndarray, 
                          source_position: Tuple[float, float]) -> np.ndarray:
        """Encode mono source to surround channels."""
        azimuth, elevation = source_position
        
        # Calculate gain for each channel based on distance to speakers
        channel_gains = {}
        total_gain = 0
        
        for channel, (ch_az, ch_el) in self.channel_positions.items():
            # Calculate angular distance
            distance = abs(azimuth - ch_az)
            if distance > 180:
                distance = 360 - distance
                
            # Convert to gain (inverse relationship)
            gain = 1.0 / (1.0 + distance / 45.0)  # 45 degrees for half gain
            channel_gains[channel] = gain
            total_gain += gain
            
        # Normalize gains
        for channel in channel_gains:
            channel_gains[channel] /= total_gain
            
        # Create surround channels
        num_channels = len(self.channel_positions)
        surround_audio = np.zeros((len(mono_audio), num_channels), dtype=np.float32)
        
        for i, channel in enumerate(self.channel_positions.keys()):
            gain = channel_gains.get(channel, 0)
            
            if channel == 'lfe':
                # Low frequency effects - apply lowpass filter
                lfe_audio = self._extract_lfe(mono_audio)
                surround_audio[:, i] = lfe_audio * gain
            else:
                surround_audio[:, i] = mono_audio * gain
                
        return surround_audio
        
    def _extract_lfe(self, audio: np.ndarray) -> np.ndarray:
        """Extract low frequency effects for subwoofer."""
        # Apply lowpass filter for LFE channel
        nyquist = 22050 / 2  # Assuming 44.1kHz
        cutoff = 120  # LFE cutoff frequency
        
        b, a = scipy.signal.butter(4, cutoff / nyquist, 'low')
        lfe_audio = scipy.signal.filtfilt(b, a, audio)
        
        return lfe_audio * 2.0  # Boost LFE level


class AudioWidening:
    """Advanced audio widening techniques."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
    def harmonic_widening(self, stereo_audio: np.ndarray, amount: float = 0.5) -> np.ndarray:
        """Apply harmonic widening effect."""
        if stereo_audio.shape[1] != 2:
            raise ValueError("Input must be stereo")
            
        left = stereo_audio[:, 0]
        right = stereo_audio[:, 1]
        
        # Extract side signal
        side = (left - right) * 0.5
        
        # Generate harmonics of side signal
        harmonics = self._generate_harmonics(side)
        
        # Mix harmonics with original side signal
        enhanced_side = side + amount * harmonics
        
        # Reconstruct stereo
        mid = (left + right) * 0.5
        enhanced_left = mid + enhanced_side
        enhanced_right = mid - enhanced_side
        
        return np.column_stack([enhanced_left, enhanced_right]).astype(np.float32)
        
    def _generate_harmonics(self, signal: np.ndarray) -> np.ndarray:
        """Generate harmonic content for widening."""
        # Simple harmonic generation using nonlinear processing
        # Apply gentle saturation to generate harmonics
        drive = 2.0
        saturated = np.tanh(drive * signal)
        
        # High-pass filter to remove fundamental
        nyquist = self.sample_rate / 2
        b, a = scipy.signal.butter(2, 200 / nyquist, 'high')
        harmonics = scipy.signal.filtfilt(b, a, saturated)
        
        return harmonics
        
    def chorus_widening(self, stereo_audio: np.ndarray, 
                       delay_ms: float = 25, depth: float = 2, 
                       rate: float = 0.5) -> np.ndarray:
        """Apply chorus-based widening."""
        if stereo_audio.shape[1] != 2:
            raise ValueError("Input must be stereo")
            
        # Generate modulation LFO
        lfo_samples = len(stereo_audio)
        lfo = np.sin(2 * np.pi * rate * np.arange(lfo_samples) / self.sample_rate)
        
        # Create variable delay
        base_delay_samples = int(delay_ms * 0.001 * self.sample_rate)
        depth_samples = int(depth * 0.001 * self.sample_rate)
        
        widened = np.zeros_like(stereo_audio)
        
        for i in range(len(stereo_audio)):
            # Calculate delay for this sample
            delay_offset = int(lfo[i] * depth_samples)
            total_delay = base_delay_samples + delay_offset
            
            if i >= total_delay:
                # Apply delayed version to opposite channel
                widened[i, 0] = stereo_audio[i, 0] + 0.3 * stereo_audio[i - total_delay, 1]
                widened[i, 1] = stereo_audio[i, 1] + 0.3 * stereo_audio[i - total_delay, 0]
            else:
                widened[i] = stereo_audio[i]
                
        return widened.astype(np.float32)
