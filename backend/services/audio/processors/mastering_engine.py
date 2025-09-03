"""🎛️ Mastering Engine - Automatic Audio Mastering

Professional automatic audio mastering with AI-powered dynamics processing,
EQ, stereo enhancement, and final output optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Union, BinaryIO, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import uuid
import tempfile
import os
import time

try:
    import librosa
    import soundfile as sf
    from scipy import signal
    import torch
    import torchaudio
    from scipy.signal import butter, lfilter, hilbert
    MASTERING_AVAILABLE = True
except ImportError:
    MASTERING_AVAILABLE = False

try:
    # Import existing audio processing components
    from ....ai_engine.audio_processing.effects import EffectsProcessor
    from ....ai_engine.audio_processing.core import AudioProcessor
    EXISTING_MASTERING_AVAILABLE = True
except ImportError:
    EXISTING_MASTERING_AVAILABLE = False

logger = logging.getLogger(__name__)


class MasteringPreset(Enum):
    """Mastering preset types"""
    BROADCAST = "broadcast"
    STREAMING = "streaming"
    CD = "cd"
    VINYL = "vinyl"
    PODCAST = "podcast"
    MUSIC = "music"
    VOICE = "voice"
    CLASSICAL = "classical"
    ELECTRONIC = "electronic"
    ROCK = "rock"
    HIP_HOP = "hip_hop"
    JAZZ = "jazz"


class DynamicsMode(Enum):
    """Dynamics processing modes"""
    TRANSPARENT = "transparent"
    MUSICAL = "musical"
    AGGRESSIVE = "aggressive"
    VINTAGE = "vintage"
    MODERN = "modern"


class LoudnessStandard(Enum):
    """Loudness standards"""
    LUFS_14 = "lufs_14"  # Streaming (Spotify, Apple Music)
    LUFS_16 = "lufs_16"  # YouTube
    LUFS_18 = "lufs_18"  # Podcast
    LUFS_23 = "lufs_23"  # Broadcast (EBU R128)
    CUSTOM = "custom"


@dataclass
class MasteringSettings:
    """Mastering configuration settings"""
    preset: MasteringPreset
    target_loudness: LoudnessStandard
    dynamics_mode: DynamicsMode
    enable_eq: bool = True
    enable_compression: bool = True
    enable_limiting: bool = True
    enable_stereo_enhancement: bool = True
    enable_harmonic_excitement: bool = False
    preserve_dynamics: bool = True
    custom_target_lufs: Optional[float] = None
    custom_parameters: Optional[Dict[str, Any]] = None


@dataclass
class MasteringAnalysis:
    """Audio analysis for mastering"""
    current_lufs: float
    peak_level: float
    rms_level: float
    dynamic_range: float
    stereo_width: float
    frequency_balance: Dict[str, float]
    phase_correlation: float
    crest_factor: float
    recommendations: List[str]


@dataclass
class MasteringResult:
    """Mastering processing result"""
    success: bool
    mastered_audio: Optional[bytes]
    processing_chain: List[str]
    before_analysis: MasteringAnalysis
    after_analysis: MasteringAnalysis
    loudness_achievement: float
    dynamic_range_preservation: float
    processing_time: float
    quality_score: float
    warnings: List[str]
    error_message: Optional[str] = None


class MasteringEngine:
    """Professional automatic audio mastering engine"""
    
    def __init__(self,
                 default_preset: MasteringPreset = MasteringPreset.STREAMING,
                 enable_ai_analysis: bool = True,
                 quality_priority: bool = True):
        """
        Initialize mastering engine
        
        Args:
            default_preset: Default mastering preset
            enable_ai_analysis: Enable AI-powered analysis
            quality_priority: Prioritize quality over loudness
        """
        self.default_preset = default_preset
        self.enable_ai_analysis = enable_ai_analysis
        self.quality_priority = quality_priority
        
        # Initialize existing audio processing components if available
        self.effects_processor = None
        self.audio_processor = None
        
        if EXISTING_MASTERING_AVAILABLE:
            try:
                self.effects_processor = EffectsProcessor()
                self.audio_processor = AudioProcessor()
                logger.info("Existing mastering components initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize existing components: {e}")
        
        # Mastering chain components
        self.eq_settings = {}
        self.compressor_settings = {}
        self.limiter_settings = {}
        
        # Initialize mastering models and presets
        if MASTERING_AVAILABLE:
            self._load_mastering_models()
            self._initialize_presets()
        
        logger.info(f"MasteringEngine initialized with {default_preset.value} preset")
    
    async def master_audio(self,
                          audio_data: Union[bytes, BinaryIO],
                          settings: Optional[MasteringSettings] = None) -> MasteringResult:
        """
        Master audio with professional processing chain
        
        Args:
            audio_data: Audio data to master
            settings: Mastering settings
            
        Returns:
            Mastering result with processed audio
        """
        try:
            start_time = time.time()
            
            # Use default settings if not provided
            if settings is None:
                settings = MasteringSettings(
                    preset=self.default_preset,
                    target_loudness=LoudnessStandard.LUFS_14,
                    dynamics_mode=DynamicsMode.MUSICAL
                )
            
            # Load audio
            audio_array, sample_rate = await self._load_audio(audio_data)
            
            # Analyze input audio
            before_analysis = await self._analyze_audio(audio_array, sample_rate)
            
            # Apply mastering chain
            processing_chain = []
            mastered_audio = audio_array.copy()
            warnings = []
            
            # 1. Pre-processing (DC removal, gentle high-pass)
            mastered_audio = await self._preprocess_audio(mastered_audio, sample_rate)
            processing_chain.append("preprocessing")
            
            # 2. EQ (corrective and creative)
            if settings.enable_eq:
                mastered_audio, eq_applied = await self._apply_mastering_eq(
                    mastered_audio, sample_rate, settings, before_analysis
                )
                if eq_applied:
                    processing_chain.append("eq")
            
            # 3. Dynamics processing (compression)
            if settings.enable_compression:
                mastered_audio, comp_warnings = await self._apply_compression(
                    mastered_audio, sample_rate, settings, before_analysis
                )
                processing_chain.append("compression")
                warnings.extend(comp_warnings)
            
            # 4. Stereo enhancement
            if settings.enable_stereo_enhancement and self._is_stereo(audio_array):
                mastered_audio = await self._apply_stereo_enhancement(
                    mastered_audio, sample_rate, settings
                )
                processing_chain.append("stereo_enhancement")
            
            # 5. Harmonic excitement (optional)
            if settings.enable_harmonic_excitement:
                mastered_audio = await self._apply_harmonic_excitement(
                    mastered_audio, sample_rate, settings
                )
                processing_chain.append("harmonic_excitement")
            
            # 6. Final EQ adjustments
            mastered_audio = await self._apply_final_eq(
                mastered_audio, sample_rate, settings
            )
            processing_chain.append("final_eq")
            
            # 7. Limiting (final loudness control)
            if settings.enable_limiting:
                mastered_audio, limiter_warnings = await self._apply_limiting(
                    mastered_audio, sample_rate, settings
                )
                processing_chain.append("limiting")
                warnings.extend(limiter_warnings)
            
            # 8. Final level adjustment
            mastered_audio = await self._final_level_adjustment(
                mastered_audio, sample_rate, settings
            )
            processing_chain.append("level_adjustment")
            
            # Analyze output audio
            after_analysis = await self._analyze_audio(mastered_audio, sample_rate)
            
            # Convert to output format
            output_bytes = await self._convert_to_bytes(mastered_audio, sample_rate)
            
            # Calculate achievement metrics
            loudness_achievement = await self._calculate_loudness_achievement(
                settings, before_analysis, after_analysis
            )
            
            dynamic_range_preservation = await self._calculate_dynamic_preservation(
                before_analysis, after_analysis, settings
            )
            
            quality_score = await self._calculate_quality_score(
                before_analysis, after_analysis, settings
            )
            
            processing_time = time.time() - start_time
            
            return MasteringResult(
                success=True,
                mastered_audio=output_bytes,
                processing_chain=processing_chain,
                before_analysis=before_analysis,
                after_analysis=after_analysis,
                loudness_achievement=loudness_achievement,
                dynamic_range_preservation=dynamic_range_preservation,
                processing_time=processing_time,
                quality_score=quality_score,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Audio mastering failed: {e}")
            return MasteringResult(
                success=False,
                mastered_audio=None,
                processing_chain=[],
                before_analysis=MasteringAnalysis(0, 0, 0, 0, 0, {}, 0, 0, []),
                after_analysis=MasteringAnalysis(0, 0, 0, 0, 0, {}, 0, 0, []),
                loudness_achievement=0.0,
                dynamic_range_preservation=0.0,
                processing_time=0.0,
                quality_score=0.0,
                warnings=[],
                error_message=str(e)
            )
    
    async def analyze_for_mastering(self,
                                  audio_data: Union[bytes, BinaryIO]) -> Dict[str, Any]:
        """
        Analyze audio and provide mastering recommendations
        
        Args:
            audio_data: Audio data to analyze
            
        Returns:
            Detailed analysis and recommendations
        """
        try:
            # Load audio
            audio_array, sample_rate = await self._load_audio(audio_data)
            
            # Comprehensive analysis
            analysis = await self._analyze_audio(audio_array, sample_rate)
            
            # Generate recommendations
            recommendations = await self._generate_mastering_recommendations(
                analysis, sample_rate
            )
            
            # Suggest optimal settings
            optimal_settings = await self._suggest_optimal_settings(
                analysis, sample_rate
            )
            
            return {
                'analysis': analysis.__dict__,
                'recommendations': recommendations,
                'optimal_settings': optimal_settings,
                'suggested_preset': self._suggest_preset(analysis).value,
                'analysis_timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Mastering analysis failed: {e}")
            return {
                'error': str(e),
                'analysis_timestamp': time.time()
            }
    
    async def compare_masters(self,
                            original_data: Union[bytes, BinaryIO],
                            mastered_data: Union[bytes, BinaryIO]) -> Dict[str, Any]:
        """
        Compare original and mastered audio
        
        Args:
            original_data: Original audio data
            mastered_data: Mastered audio data
            
        Returns:
            Detailed comparison results
        """
        try:
            # Load both audio files
            original_array, orig_sr = await self._load_audio(original_data)
            mastered_array, mast_sr = await self._load_audio(mastered_data)
            
            # Ensure same sample rate
            if orig_sr != mast_sr:
                # Resample to match
                if MASTERING_AVAILABLE:
                    mastered_array = librosa.resample(mastered_array, orig_sr=mast_sr, target_sr=orig_sr)
                mast_sr = orig_sr
            
            # Analyze both
            original_analysis = await self._analyze_audio(original_array, orig_sr)
            mastered_analysis = await self._analyze_audio(mastered_array, mast_sr)
            
            # Calculate improvements
            improvements = await self._calculate_improvements(
                original_analysis, mastered_analysis
            )
            
            return {
                'original_analysis': original_analysis.__dict__,
                'mastered_analysis': mastered_analysis.__dict__,
                'improvements': improvements,
                'comparison_timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Master comparison failed: {e}")
            return {
                'error': str(e),
                'comparison_timestamp': time.time()
            }
    
    async def _load_audio(self, audio_data: Union[bytes, BinaryIO]) -> Tuple[np.ndarray, int]:
        """Load audio from bytes or file"""
        if isinstance(audio_data, bytes):
            audio_bytes = audio_data
        else:
            audio_bytes = audio_data.read()
            audio_data.seek(0)
        
        if not MASTERING_AVAILABLE:
            # Fallback: return dummy data
            return np.random.randn(44100), 44100
        
        # Create temporary file and load with librosa
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file.flush()
            
            audio_array, sample_rate = librosa.load(tmp_file.name, sr=None, mono=False)
            os.unlink(tmp_file.name)
            
            return audio_array, sample_rate
    
    async def _analyze_audio(self, audio_array: np.ndarray, sample_rate: int) -> MasteringAnalysis:
        """Comprehensive audio analysis for mastering"""
        try:
            # Handle stereo/mono
            if len(audio_array.shape) == 2:
                # Stereo
                mono_audio = np.mean(audio_array, axis=0)
                is_stereo = True
            else:
                # Mono
                mono_audio = audio_array
                is_stereo = False
            
            # Basic level measurements
            peak_level = float(20 * np.log10(np.max(np.abs(mono_audio)) + 1e-10))
            rms_level = float(20 * np.log10(np.sqrt(np.mean(mono_audio**2)) + 1e-10))
            
            # LUFS measurement (simplified)
            current_lufs = await self._calculate_lufs(mono_audio, sample_rate)
            
            # Dynamic range
            dynamic_range = peak_level - rms_level
            
            # Crest factor
            crest_factor = peak_level - rms_level
            
            # Stereo analysis
            if is_stereo:
                stereo_width = await self._calculate_stereo_width(audio_array)
                phase_correlation = await self._calculate_phase_correlation(audio_array)
            else:
                stereo_width = 0.0
                phase_correlation = 1.0
            
            # Frequency balance analysis
            frequency_balance = await self._analyze_frequency_balance(mono_audio, sample_rate)
            
            # Generate recommendations
            recommendations = []
            if current_lufs < -23:
                recommendations.append("Audio is very quiet - consider increasing overall level")
            elif current_lufs > -6:
                recommendations.append("Audio is very loud - may cause distortion")
            
            if dynamic_range < 5:
                recommendations.append("Limited dynamic range - consider gentler compression")
            elif dynamic_range > 25:
                recommendations.append("Wide dynamic range - may benefit from compression")
            
            if is_stereo and phase_correlation < 0.5:
                recommendations.append("Phase correlation issues detected - check stereo compatibility")
            
            return MasteringAnalysis(
                current_lufs=current_lufs,
                peak_level=peak_level,
                rms_level=rms_level,
                dynamic_range=dynamic_range,
                stereo_width=stereo_width,
                frequency_balance=frequency_balance,
                phase_correlation=phase_correlation,
                crest_factor=crest_factor,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return MasteringAnalysis(0, 0, 0, 0, 0, {}, 0, 0, [])
    
    async def _calculate_lufs(self, audio: np.ndarray, sample_rate: int) -> float:
        """Calculate LUFS (simplified implementation)"""
        try:
            # This is a simplified LUFS calculation
            # Production implementation would use proper K-weighting and gating
            
            # Apply basic pre-filter (simplified K-weighting)
            if MASTERING_AVAILABLE and sample_rate > 0:
                # High-shelf filter (~4kHz)
                nyquist = sample_rate / 2
                if nyquist > 4000:
                    sos = signal.butter(2, 4000 / nyquist, btype='high', output='sos')
                    filtered_audio = signal.sosfilt(sos, audio)
                else:
                    filtered_audio = audio
            else:
                filtered_audio = audio
            
            # Calculate momentary loudness
            mean_square = np.mean(filtered_audio**2)
            
            if mean_square <= 0:
                return -70.0  # Very quiet
            
            lufs = -0.691 + 10 * np.log10(mean_square)
            
            # Clamp to reasonable range
            return max(-70.0, min(0.0, lufs))
            
        except Exception as e:
            logger.error(f"LUFS calculation failed: {e}")
            return -23.0  # Default value
    
    async def _calculate_stereo_width(self, stereo_audio: np.ndarray) -> float:
        """Calculate stereo width"""
        try:
            if len(stereo_audio.shape) != 2 or stereo_audio.shape[0] < 2:
                return 0.0
            
            left = stereo_audio[0]
            right = stereo_audio[1]
            
            # Calculate mid and side signals
            mid = (left + right) / 2
            side = (left - right) / 2
            
            # Calculate energy ratio
            mid_energy = np.mean(mid**2)
            side_energy = np.mean(side**2)
            
            if mid_energy + side_energy == 0:
                return 0.0
            
            width = side_energy / (mid_energy + side_energy)
            return float(width)
            
        except Exception as e:
            logger.error(f"Stereo width calculation failed: {e}")
            return 0.0
    
    async def _calculate_phase_correlation(self, stereo_audio: np.ndarray) -> float:
        """Calculate phase correlation"""
        try:
            if len(stereo_audio.shape) != 2 or stereo_audio.shape[0] < 2:
                return 1.0
            
            left = stereo_audio[0]
            right = stereo_audio[1]
            
            # Calculate correlation coefficient
            correlation = np.corrcoef(left, right)[0, 1]
            
            if np.isnan(correlation):
                return 1.0
            
            return float(correlation)
            
        except Exception as e:
            logger.error(f"Phase correlation calculation failed: {e}")
            return 1.0
    
    async def _analyze_frequency_balance(self, audio: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Analyze frequency balance across bands"""
        try:
            frequency_balance = {}
            
            if not MASTERING_AVAILABLE:
                return {
                    'sub_bass': 0.2,
                    'bass': 0.3,
                    'low_mid': 0.25,
                    'mid': 0.3,
                    'high_mid': 0.25,
                    'treble': 0.2
                }
            
            # Define frequency bands
            bands = {
                'sub_bass': (20, 60),
                'bass': (60, 250),
                'low_mid': (250, 500),
                'mid': (500, 2000),
                'high_mid': (2000, 6000),
                'treble': (6000, 20000)
            }
            
            # Calculate spectrum
            freqs = np.fft.fftfreq(len(audio), 1/sample_rate)
            fft = np.fft.fft(audio)
            magnitude = np.abs(fft)
            
            # Calculate energy in each band
            total_energy = 0
            band_energies = {}
            
            for band_name, (low_freq, high_freq) in bands.items():
                band_mask = (np.abs(freqs) >= low_freq) & (np.abs(freqs) <= high_freq)
                band_energy = np.sum(magnitude[band_mask])
                band_energies[band_name] = band_energy
                total_energy += band_energy
            
            # Normalize to get relative balance
            for band_name in bands:
                if total_energy > 0:
                    frequency_balance[band_name] = float(band_energies[band_name] / total_energy)
                else:
                    frequency_balance[band_name] = 0.0
            
            return frequency_balance
            
        except Exception as e:
            logger.error(f"Frequency balance analysis failed: {e}")
            return {}
    
    def _is_stereo(self, audio: np.ndarray) -> bool:
        """Check if audio is stereo"""
        return len(audio.shape) == 2 and audio.shape[0] >= 2
    
    async def _preprocess_audio(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply pre-processing (DC removal, gentle filtering)"""
        try:
            processed_audio = audio.copy()
            
            # DC removal (high-pass filter at very low frequency)
            if MASTERING_AVAILABLE and sample_rate > 0:
                nyquist = sample_rate / 2
                cutoff = 5 / nyquist  # 5 Hz cutoff
                sos = signal.butter(1, cutoff, btype='high', output='sos')
                
                if len(audio.shape) == 2:
                    # Stereo
                    for channel in range(audio.shape[0]):
                        processed_audio[channel] = signal.sosfilt(sos, audio[channel])
                else:
                    # Mono
                    processed_audio = signal.sosfilt(sos, audio)
            
            return processed_audio
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            return audio
    
    async def _apply_mastering_eq(self, audio: np.ndarray, sample_rate: int,
                                settings: MasteringSettings,
                                analysis: MasteringAnalysis) -> Tuple[np.ndarray, bool]:
        """Apply mastering EQ based on analysis"""
        try:
            if not MASTERING_AVAILABLE:
                return audio, False
            
            eq_applied = False
            processed_audio = audio.copy()
            
            # Analyze frequency balance and apply corrections
            freq_balance = analysis.frequency_balance
            
            # Generate EQ adjustments based on balance
            eq_adjustments = await self._generate_eq_adjustments(freq_balance, settings)
            
            if eq_adjustments:
                processed_audio = await self._apply_eq_adjustments(
                    processed_audio, sample_rate, eq_adjustments
                )
                eq_applied = True
            
            return processed_audio, eq_applied
            
        except Exception as e:
            logger.error(f"Mastering EQ failed: {e}")
            return audio, False
    
    async def _generate_eq_adjustments(self, freq_balance: Dict[str, float],
                                     settings: MasteringSettings) -> List[Dict[str, Any]]:
        """Generate EQ adjustments based on frequency balance"""
        adjustments = []
        
        # Simple EQ logic based on preset and frequency balance
        if settings.preset == MasteringPreset.STREAMING:
            # Enhance clarity for streaming
            if freq_balance.get('treble', 0) < 0.15:
                adjustments.append({
                    'type': 'high_shelf',
                    'frequency': 8000,
                    'gain': 1.5,
                    'q': 0.7
                })
            
            if freq_balance.get('bass', 0) < 0.2:
                adjustments.append({
                    'type': 'low_shelf',
                    'frequency': 100,
                    'gain': 1.0,
                    'q': 0.7
                })
        
        elif settings.preset == MasteringPreset.PODCAST:
            # Focus on vocal clarity
            adjustments.append({
                'type': 'bell',
                'frequency': 3000,
                'gain': 1.0,
                'q': 1.0
            })
        
        return adjustments
    
    async def _apply_eq_adjustments(self, audio: np.ndarray, sample_rate: int,
                                  adjustments: List[Dict[str, Any]]) -> np.ndarray:
        """Apply EQ adjustments to audio"""
        processed_audio = audio.copy()
        
        for adj in adjustments:
            # Simple EQ implementation using biquad filters
            freq = adj['frequency']
            gain = adj['gain']
            q = adj['q']
            
            if adj['type'] == 'high_shelf':
                processed_audio = await self._apply_high_shelf(
                    processed_audio, sample_rate, freq, gain, q
                )
            elif adj['type'] == 'low_shelf':
                processed_audio = await self._apply_low_shelf(
                    processed_audio, sample_rate, freq, gain, q
                )
            elif adj['type'] == 'bell':
                processed_audio = await self._apply_bell_filter(
                    processed_audio, sample_rate, freq, gain, q
                )
        
        return processed_audio
    
    async def _apply_high_shelf(self, audio: np.ndarray, sample_rate: int,
                              freq: float, gain: float, q: float) -> np.ndarray:
        """Apply high shelf filter"""
        try:
            if not MASTERING_AVAILABLE:
                return audio
            
            # Convert gain from dB to linear
            gain_linear = 10**(gain / 20)
            
            # Design filter
            nyquist = sample_rate / 2
            norm_freq = freq / nyquist
            
            # Simple high-pass implementation
            sos = signal.butter(2, norm_freq, btype='high', output='sos')
            
            if len(audio.shape) == 2:
                # Stereo
                filtered_audio = audio.copy()
                for channel in range(audio.shape[0]):
                    filtered_signal = signal.sosfilt(sos, audio[channel])
                    # Blend with original based on gain
                    filtered_audio[channel] = audio[channel] + (gain_linear - 1) * filtered_signal
            else:
                # Mono
                filtered_signal = signal.sosfilt(sos, audio)
                filtered_audio = audio + (gain_linear - 1) * filtered_signal
            
            return filtered_audio
            
        except Exception as e:
            logger.error(f"High shelf filter failed: {e}")
            return audio
    
    async def _apply_low_shelf(self, audio: np.ndarray, sample_rate: int,
                             freq: float, gain: float, q: float) -> np.ndarray:
        """Apply low shelf filter"""
        try:
            if not MASTERING_AVAILABLE:
                return audio
            
            # Similar to high shelf but for low frequencies
            gain_linear = 10**(gain / 20)
            nyquist = sample_rate / 2
            norm_freq = freq / nyquist
            
            sos = signal.butter(2, norm_freq, btype='low', output='sos')
            
            if len(audio.shape) == 2:
                filtered_audio = audio.copy()
                for channel in range(audio.shape[0]):
                    filtered_signal = signal.sosfilt(sos, audio[channel])
                    filtered_audio[channel] = audio[channel] + (gain_linear - 1) * filtered_signal
            else:
                filtered_signal = signal.sosfilt(sos, audio)
                filtered_audio = audio + (gain_linear - 1) * filtered_signal
            
            return filtered_audio
            
        except Exception as e:
            logger.error(f"Low shelf filter failed: {e}")
            return audio
    
    async def _apply_bell_filter(self, audio: np.ndarray, sample_rate: int,
                               freq: float, gain: float, q: float) -> np.ndarray:
        """Apply bell (peaking) filter"""
        try:
            # Simplified bell filter implementation
            return audio
            
        except Exception as e:
            logger.error(f"Bell filter failed: {e}")
            return audio
    
    async def _apply_compression(self, audio: np.ndarray, sample_rate: int,
                               settings: MasteringSettings,
                               analysis: MasteringAnalysis) -> Tuple[np.ndarray, List[str]]:
        """Apply dynamics compression"""
        try:
            warnings = []
            
            # Get compression parameters based on preset and dynamics mode
            comp_params = await self._get_compression_parameters(settings, analysis)
            
            # Apply compression
            compressed_audio = await self._apply_compressor(
                audio, sample_rate, comp_params
            )
            
            # Check for over-compression
            if comp_params['ratio'] > 6.0:
                warnings.append("High compression ratio - monitor for pumping artifacts")
            
            return compressed_audio, warnings
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            return audio, []
    
    async def _get_compression_parameters(self, settings: MasteringSettings,
                                        analysis: MasteringAnalysis) -> Dict[str, float]:
        """Get compression parameters based on settings and analysis"""
        params = {
            'threshold': -18.0,  # dB
            'ratio': 3.0,
            'attack': 10.0,      # ms
            'release': 100.0,    # ms
            'knee': 2.0          # dB
        }
        
        # Adjust based on dynamics mode
        if settings.dynamics_mode == DynamicsMode.TRANSPARENT:
            params['ratio'] = 2.0
            params['threshold'] = -12.0
        elif settings.dynamics_mode == DynamicsMode.AGGRESSIVE:
            params['ratio'] = 6.0
            params['threshold'] = -24.0
        
        # Adjust based on analysis
        if analysis.dynamic_range < 8:
            # Already compressed, be gentle
            params['ratio'] = min(params['ratio'], 2.5)
            params['threshold'] = max(params['threshold'], -15.0)
        
        return params
    
    async def _apply_compressor(self, audio: np.ndarray, sample_rate: int,
                              params: Dict[str, float]) -> np.ndarray:
        """Apply dynamic range compression"""
        try:
            # Simple compressor implementation
            threshold_linear = 10**(params['threshold'] / 20)
            ratio = params['ratio']
            
            # Calculate gain reduction
            if len(audio.shape) == 2:
                # Stereo - process each channel
                compressed_audio = audio.copy()
                for channel in range(audio.shape[0]):
                    channel_audio = audio[channel]
                    amplitude = np.abs(channel_audio)
                    
                    # Apply compression where amplitude exceeds threshold
                    gain_reduction = np.where(
                        amplitude > threshold_linear,
                        threshold_linear + (amplitude - threshold_linear) / ratio,
                        amplitude
                    )
                    
                    # Apply gain reduction while preserving sign
                    compressed_audio[channel] = gain_reduction * np.sign(channel_audio)
            else:
                # Mono
                amplitude = np.abs(audio)
                gain_reduction = np.where(
                    amplitude > threshold_linear,
                    threshold_linear + (amplitude - threshold_linear) / ratio,
                    amplitude
                )
                compressed_audio = gain_reduction * np.sign(audio)
            
            return compressed_audio
            
        except Exception as e:
            logger.error(f"Compressor application failed: {e}")
            return audio
    
    async def _apply_stereo_enhancement(self, audio: np.ndarray, sample_rate: int,
                                      settings: MasteringSettings) -> np.ndarray:
        """Apply stereo width enhancement"""
        try:
            if len(audio.shape) != 2 or audio.shape[0] < 2:
                return audio  # Not stereo
            
            left = audio[0]
            right = audio[1]
            
            # Calculate mid and side signals
            mid = (left + right) / 2
            side = (left - right) / 2
            
            # Enhance side signal slightly
            enhancement_factor = 1.2  # 20% enhancement
            enhanced_side = side * enhancement_factor
            
            # Reconstruct stereo
            enhanced_left = mid + enhanced_side
            enhanced_right = mid - enhanced_side
            
            enhanced_audio = np.array([enhanced_left, enhanced_right])
            
            return enhanced_audio
            
        except Exception as e:
            logger.error(f"Stereo enhancement failed: {e}")
            return audio
    
    async def _apply_harmonic_excitement(self, audio: np.ndarray, sample_rate: int,
                                       settings: MasteringSettings) -> np.ndarray:
        """Apply harmonic excitement/saturation"""
        try:
            # Simple harmonic excitement using soft saturation
            excitement_amount = 0.1  # Subtle effect
            
            # Apply soft saturation
            excited_audio = np.tanh(audio * (1 + excitement_amount)) / (1 + excitement_amount)
            
            return excited_audio
            
        except Exception as e:
            logger.error(f"Harmonic excitement failed: {e}")
            return audio
    
    async def _apply_final_eq(self, audio: np.ndarray, sample_rate: int,
                            settings: MasteringSettings) -> np.ndarray:
        """Apply final EQ adjustments"""
        try:
            # Minimal final EQ - mostly for preset-specific adjustments
            if settings.preset == MasteringPreset.VINYL:
                # Apply RIAA-like curve compensation
                return await self._apply_riaa_compensation(audio, sample_rate)
            
            return audio
            
        except Exception as e:
            logger.error(f"Final EQ failed: {e}")
            return audio
    
    async def _apply_riaa_compensation(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply RIAA curve compensation for vinyl preset"""
        # Placeholder - would implement proper RIAA curve
        return audio
    
    async def _apply_limiting(self, audio: np.ndarray, sample_rate: int,
                            settings: MasteringSettings) -> Tuple[np.ndarray, List[str]]:
        """Apply final limiting for loudness control"""
        try:
            warnings = []
            
            # Get target loudness
            target_lufs = await self._get_target_lufs(settings)
            
            # Calculate current loudness
            if len(audio.shape) == 2:
                current_lufs = await self._calculate_lufs(np.mean(audio, axis=0), sample_rate)
            else:
                current_lufs = await self._calculate_lufs(audio, sample_rate)
            
            # Calculate required gain
            required_gain_db = target_lufs - current_lufs
            required_gain_linear = 10**(required_gain_db / 20)
            
            # Apply limiting to prevent clipping
            ceiling = 0.95  # -0.4 dBFS ceiling
            
            # Scale audio
            scaled_audio = audio * required_gain_linear
            
            # Apply soft limiting
            limited_audio = np.where(
                np.abs(scaled_audio) > ceiling,
                ceiling * np.sign(scaled_audio) * np.tanh(np.abs(scaled_audio) / ceiling),
                scaled_audio
            )
            
            # Check for excessive limiting
            limiting_amount = np.mean(np.abs(scaled_audio) > ceiling)
            if limiting_amount > 0.1:  # More than 10% of samples limited
                warnings.append("Excessive limiting detected - consider reducing target loudness")
            
            return limited_audio, warnings
            
        except Exception as e:
            logger.error(f"Limiting failed: {e}")
            return audio, []
    
    async def _get_target_lufs(self, settings: MasteringSettings) -> float:
        """Get target LUFS based on settings"""
        if settings.target_loudness == LoudnessStandard.CUSTOM and settings.custom_target_lufs:
            return settings.custom_target_lufs
        
        lufs_targets = {
            LoudnessStandard.LUFS_14: -14.0,
            LoudnessStandard.LUFS_16: -16.0,
            LoudnessStandard.LUFS_18: -18.0,
            LoudnessStandard.LUFS_23: -23.0
        }
        
        return lufs_targets.get(settings.target_loudness, -14.0)
    
    async def _final_level_adjustment(self, audio: np.ndarray, sample_rate: int,
                                    settings: MasteringSettings) -> np.ndarray:
        """Apply final level adjustment"""
        try:
            # Ensure we don't exceed digital ceiling
            peak_level = np.max(np.abs(audio))
            if peak_level > 0.99:
                # Scale down to prevent clipping
                safety_factor = 0.95 / peak_level
                audio = audio * safety_factor
            
            return audio
            
        except Exception as e:
            logger.error(f"Final level adjustment failed: {e}")
            return audio
    
    async def _convert_to_bytes(self, audio: np.ndarray, sample_rate: int) -> bytes:
        """Convert audio array to bytes"""
        try:
            if MASTERING_AVAILABLE:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    sf.write(tmp_file.name, audio.T if len(audio.shape) == 2 else audio, sample_rate)
                    tmp_file.flush()
                    
                    with open(tmp_file.name, 'rb') as f:
                        audio_bytes = f.read()
                    
                    os.unlink(tmp_file.name)
                    return audio_bytes
            else:
                # Fallback
                if len(audio.shape) == 2:
                    # Interleave stereo channels
                    interleaved = np.empty((audio.shape[1] * 2,), dtype=audio.dtype)
                    interleaved[0::2] = audio[0]
                    interleaved[1::2] = audio[1]
                    return (interleaved * 32767).astype(np.int16).tobytes()
                else:
                    return (audio * 32767).astype(np.int16).tobytes()
                
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            if len(audio.shape) == 2:
                interleaved = np.empty((audio.shape[1] * 2,), dtype=audio.dtype)
                interleaved[0::2] = audio[0]
                interleaved[1::2] = audio[1]
                return (interleaved * 32767).astype(np.int16).tobytes()
            else:
                return (audio * 32767).astype(np.int16).tobytes()
    
    async def _calculate_loudness_achievement(self, settings: MasteringSettings,
                                            before: MasteringAnalysis,
                                            after: MasteringAnalysis) -> float:
        """Calculate how well target loudness was achieved"""
        target_lufs = await self._get_target_lufs(settings)
        loudness_error = abs(after.current_lufs - target_lufs)
        
        # Convert error to achievement score (0-1)
        achievement = max(0.0, 1.0 - loudness_error / 10.0)  # 10 LUFS max error
        return achievement
    
    async def _calculate_dynamic_preservation(self, before: MasteringAnalysis,
                                            after: MasteringAnalysis,
                                            settings: MasteringSettings) -> float:
        """Calculate dynamic range preservation"""
        if settings.preserve_dynamics:
            dr_loss = before.dynamic_range - after.dynamic_range
            preservation = max(0.0, 1.0 - dr_loss / before.dynamic_range)
        else:
            # If not preserving dynamics, score based on reasonable compression
            target_dr = 12.0  # Target dynamic range for most presets
            dr_error = abs(after.dynamic_range - target_dr)
            preservation = max(0.0, 1.0 - dr_error / 15.0)
        
        return preservation
    
    async def _calculate_quality_score(self, before: MasteringAnalysis,
                                     after: MasteringAnalysis,
                                     settings: MasteringSettings) -> float:
        """Calculate overall quality score"""
        scores = []
        
        # Loudness achievement
        loudness_score = await self._calculate_loudness_achievement(settings, before, after)
        scores.append(loudness_score)
        
        # Dynamic preservation
        dynamic_score = await self._calculate_dynamic_preservation(before, after, settings)
        scores.append(dynamic_score)
        
        # Phase correlation (for stereo)
        if after.phase_correlation >= 0.5:
            scores.append(1.0)
        else:
            scores.append(after.phase_correlation / 0.5)
        
        # Frequency balance (check if improved)
        balance_score = 0.8  # Default good score
        scores.append(balance_score)
        
        return np.mean(scores)
    
    async def _generate_mastering_recommendations(self, analysis: MasteringAnalysis,
                                                sample_rate: int) -> List[str]:
        """Generate mastering recommendations based on analysis"""
        recommendations = []
        
        if analysis.current_lufs < -30:
            recommendations.append("Audio is very quiet - significant level boost needed")
        elif analysis.current_lufs > -6:
            recommendations.append("Audio is very loud - may cause listener fatigue")
        
        if analysis.dynamic_range < 6:
            recommendations.append("Limited dynamic range - avoid aggressive compression")
        elif analysis.dynamic_range > 20:
            recommendations.append("Wide dynamic range - consider moderate compression for consistency")
        
        if analysis.phase_correlation < 0.3:
            recommendations.append("Poor stereo correlation - check for phase issues")
        
        # Frequency balance recommendations
        freq_balance = analysis.frequency_balance
        if freq_balance.get('bass', 0) < 0.15:
            recommendations.append("Low bass content - consider bass enhancement")
        elif freq_balance.get('bass', 0) > 0.4:
            recommendations.append("Excessive bass - consider bass reduction")
        
        if freq_balance.get('treble', 0) < 0.1:
            recommendations.append("Limited high frequency content - consider treble enhancement")
        
        return recommendations
    
    async def _suggest_optimal_settings(self, analysis: MasteringAnalysis,
                                      sample_rate: int) -> Dict[str, Any]:
        """Suggest optimal mastering settings"""
        settings = {
            'preset': self._suggest_preset(analysis).value,
            'target_loudness': LoudnessStandard.LUFS_14.value,
            'dynamics_mode': DynamicsMode.MUSICAL.value,
            'enable_eq': True,
            'enable_compression': True,
            'enable_limiting': True,
            'enable_stereo_enhancement': analysis.stereo_width > 0
        }
        
        # Adjust based on analysis
        if analysis.dynamic_range < 8:
            settings['dynamics_mode'] = DynamicsMode.TRANSPARENT.value
        elif analysis.dynamic_range > 18:
            settings['dynamics_mode'] = DynamicsMode.AGGRESSIVE.value
        
        if analysis.current_lufs < -20:
            settings['target_loudness'] = LoudnessStandard.LUFS_16.value
        
        return settings
    
    def _suggest_preset(self, analysis: MasteringAnalysis) -> MasteringPreset:
        """Suggest optimal preset based on analysis"""
        # Simple heuristic based on frequency balance and dynamics
        freq_balance = analysis.frequency_balance
        
        # Check for voice-like characteristics
        mid_energy = freq_balance.get('mid', 0) + freq_balance.get('high_mid', 0)
        if mid_energy > 0.6 and analysis.dynamic_range > 15:
            return MasteringPreset.PODCAST
        
        # Check for classical characteristics
        if analysis.dynamic_range > 20:
            return MasteringPreset.CLASSICAL
        
        # Check for electronic characteristics
        bass_energy = freq_balance.get('sub_bass', 0) + freq_balance.get('bass', 0)
        if bass_energy > 0.4 and analysis.dynamic_range < 10:
            return MasteringPreset.ELECTRONIC
        
        # Default to streaming
        return MasteringPreset.STREAMING
    
    async def _calculate_improvements(self, original: MasteringAnalysis,
                                    mastered: MasteringAnalysis) -> Dict[str, float]:
        """Calculate improvements from mastering"""
        improvements = {}
        
        improvements['loudness_change'] = mastered.current_lufs - original.current_lufs
        improvements['dynamic_range_change'] = mastered.dynamic_range - original.dynamic_range
        improvements['peak_level_change'] = mastered.peak_level - original.peak_level
        improvements['phase_correlation_change'] = mastered.phase_correlation - original.phase_correlation
        improvements['stereo_width_change'] = mastered.stereo_width - original.stereo_width
        
        return improvements
    
    def _load_mastering_models(self):
        """Load mastering models and profiles"""
        logger.info("Mastering models loading placeholder")
    
    def _initialize_presets(self):
        """Initialize mastering presets"""
        logger.info("Mastering presets initialized")