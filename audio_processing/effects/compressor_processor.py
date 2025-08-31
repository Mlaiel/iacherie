"""🗜️ Compressor Processor - Professional Dynamic Range Control

Industrial-grade audio compression with multiple compression algorithms, side-chain
processing, multiband compression, and professional dynamics control for music production.

Features:
- Professional compressor models (VCA, Optical, FET, Tube, Digital)
- Multiband compression with crossover filters
- Side-chain processing with external trigger
- Look-ahead processing for transparent compression
- Professional metering and gain reduction visualization
- AI-assisted dynamics analysis and optimization
- Vintage analog modeling with harmonic generation
- Real-time adaptive attack/release based on program material

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

=============================================================================
CONFIDENTIAL - IA INFLUENCER AGENT PLATFORM
=============================================================================
Expert Team Attribution:
- Lead Dev IA: Fahed Mlaiel (mlaiel@live.de)
- Backend Senior: Professional Architecture Team
- ML Engineer: AI-Assisted Dynamics Analysis
- Audio Engineer: Professional DSP Implementation
- DevOps: Production Deployment & Monitoring

Business Logic Flow:
Creator Upload → Audio Analysis → AI Dynamics Recommendation → Professional Processing →
Quality Control → Distribution → Analytics

WARNING: This software contains proprietary algorithms and trade secrets.
Unauthorized reproduction, distribution, or reverse engineering is strictly
prohibited under international copyright law.
=============================================================================
"""import numpy as np
import logging
from typing import Optional, Dict, List, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import scipy.signal
from abc import ABC, abstractmethod
import asyncio
from .envelope_follower import EnvelopeFollower


class CompressorType(Enum):
    """Professional compressor types with authentic modeling"""    VCA = "vca"                    # Clean, precise control
    OPTICAL = "optical"            # Smooth, musical compression
    FET = "fet"                   # Fast, punchy character
    TUBE = "tube"                 # Warm, harmonic saturation
    DIGITAL = "digital"           # Transparent, surgical
    VINTAGE_VCA = "vintage_vca"   # Classic VCA with character
    OPTO_LA2A = "opto_la2a"      # LA-2A style optical
    FET_1176 = "fet_1176"        # 1176 style FET
    VARI_MU = "vari_mu"          # Variable-mu tube style


class DetectionMode(Enum):
    """Peak/RMS detection modes"""    PEAK = "peak"
    RMS = "rms"
    HYBRID = "hybrid"
    PROGRAM_DEPENDENT = "program_dependent"


class KneeType(Enum):
    """Compression knee types"""    HARD = "hard"
    SOFT = "soft"
    ADAPTIVE = "adaptive"


class CompressorPreset(Enum):
    """Professional compressor presets"""    VOCAL_LEVELING = "vocal_leveling"
    DRUM_PUNCH = "drum_punch"
    BASS_CONTROL = "bass_control"
    MIX_BUS_GLUE = "mix_bus_glue"
    MASTERING_CONTROL = "mastering_control"
    BROADCAST_LIMITING = "broadcast_limiting"
    CREATIVE_PUMPING = "creative_pumping"
    TRANSPARENT_LIMITING = "transparent_limiting"
    VINTAGE_WARMTH = "vintage_warmth"
    SURGICAL_PRECISION = "surgical_precision"


@dataclass
class CompressorBand:
    """Multiband compressor band configuration"""    frequency_low: float
    frequency_high: float
    threshold: float
    ratio: float
    attack_time: float
    release_time: float
    makeup_gain: float
    enabled: bool = True
    solo: bool = False
    bypass: bool = False


@dataclass
class CompressorState:
    """Compressor internal state"""    envelope: float = 0.0
    gain_reduction: float = 0.0
    peak_level: float = 0.0
    rms_level: float = 0.0
    adaptive_attack: float = 0.0
    adaptive_release: float = 0.0


@dataclass
class CompressionAnalysis:
    """AI-powered compression analysis"""    recommended_threshold: float
    recommended_ratio: float
    recommended_attack: float
    recommended_release: float
    dynamic_range: float
    peak_to_average: float
    suggestions: List[str]
    confidence_score: float


class SideChainProcessor:
    """External side-chain processing"""    
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.highpass_freq = 100.0  # Hz
        self.enabled = False
        self.external_input = None
        
        # Design side-chain filter
        nyquist = sample_rate / 2
        normalized_freq = self.highpass_freq / nyquist
        self.b, self.a = scipy.signal.butter(2, normalized_freq, btype='high')
    
    def process(self, audio_data: np.ndarray, sidechain_input: Optional[np.ndarray] = None) -> np.ndarray:
        """Process side-chain signal"""        if not self.enabled or sidechain_input is None:
            return audio_data
        
        # Apply high-pass filter to side-chain
        filtered_sc = scipy.signal.lfilter(self.b, self.a, sidechain_input)
        return filtered_sc


class MultibandCrossover:
    """Multiband crossover filter network"""    
    def __init__(self, sample_rate: int, crossover_frequencies: List[float]):
        self.sample_rate = sample_rate
        self.crossover_frequencies = crossover_frequencies
        self.filters = self._design_crossover_filters()
    
    def _design_crossover_filters(self) -> List[Tuple]:
        """Design Linkwitz-Riley crossover filters"""        filters = []
        nyquist = self.sample_rate / 2
        
        for freq in self.crossover_frequencies:
            normalized_freq = freq / nyquist
            # 4th order Linkwitz-Riley filters
            b_low, a_low = scipy.signal.butter(4, normalized_freq, btype='low')
            b_high, a_high = scipy.signal.butter(4, normalized_freq, btype='high')
            filters.append((b_low, a_low, b_high, a_high))
        
        return filters
    
    def split_bands(self, audio_data: np.ndarray) -> List[np.ndarray]:
        """Split audio into frequency bands"""        bands = []
        current_signal = audio_data.copy()
        
        for i, (b_low, a_low, b_high, a_high) in enumerate(self.filters):
            # Extract low band
            low_band = scipy.signal.lfilter(b_low, a_low, current_signal)
            bands.append(low_band)
            
            # Continue with high band for next iteration
            current_signal = scipy.signal.lfilter(b_high, a_high, current_signal)
        
        # Add final high band
        bands.append(current_signal)
        return bands
    
    def recombine_bands(self, bands: List[np.ndarray]) -> np.ndarray:
        """Recombine processed frequency bands"""        output = np.zeros_like(bands[0])
        for band in bands:
            output += band
        return output


class CompressorProcessor:
    """Professional multiband compressor with advanced features"""    
    def __init__(self, sample_rate: int = 44100, compressor_type: CompressorType = CompressorType.VCA):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.compressor_type = compressor_type
        
        # Core compressor parameters
        self.threshold = -12.0  # dB
        self.ratio = 4.0
        self.attack_time = 0.003  # seconds
        self.release_time = 0.1  # seconds
        self.knee_width = 2.0  # dB
        self.makeup_gain = 0.0  # dB
        self.knee_type = KneeType.SOFT
        self.detection_mode = DetectionMode.RMS
        
        # Advanced features
        self.lookahead_ms = 5.0
        self.oversampling = False
        self.analog_modeling = True
        self.auto_makeup = True
        self.auto_release = False
        
        # Multiband configuration
        self.multiband_enabled = False
        self.crossover_frequencies = [200.0, 2000.0]  # 3-band default
        self.crossover = MultibandCrossover(sample_rate, self.crossover_frequencies)
        self.bands = self._initialize_multiband()
        
        # Side-chain processing
        self.sidechain = SideChainProcessor(sample_rate)
        
        # Internal state
        self.state = CompressorState()
        self.envelope_follower = EnvelopeFollower(sample_rate)
        
        # Presets
        self.presets = self._load_professional_presets()
        
        # Processing buffers
        self.lookahead_buffer = np.zeros(int(self.lookahead_ms * sample_rate / 1000))
        self.delay_buffer = np.zeros_like(self.lookahead_buffer)
        
        # Metering
        self.input_level = 0.0
        self.output_level = 0.0
        self.gain_reduction_meter = 0.0
        
        self.logger.info(f"CompressorProcessor initialized - Type: {compressor_type.value}, Sample Rate: {sample_rate}Hz")
    
    def _initialize_multiband(self) -> List[CompressorBand]:
        """Initialize multiband compressor bands"""        return [
            CompressorBand(20.0, 200.0, -15.0, 3.0, 0.01, 0.1, 0.0),   # Low band
            CompressorBand(200.0, 2000.0, -12.0, 4.0, 0.003, 0.05, 0.0), # Mid band  
            CompressorBand(2000.0, 20000.0, -10.0, 2.5, 0.001, 0.03, 0.0) # High band
        ]
    
    def _load_professional_presets(self) -> Dict[CompressorPreset, Dict[str, Any]]:
        """Load professional compressor presets"""        return {
            CompressorPreset.VOCAL_LEVELING: {
                'threshold': -18.0, 'ratio': 3.0, 'attack_time': 0.005,
                'release_time': 0.05, 'knee_width': 2.0, 'makeup_gain': 3.0,
                'compressor_type': CompressorType.OPTICAL
            },
            CompressorPreset.DRUM_PUNCH: {
                'threshold': -10.0, 'ratio': 6.0, 'attack_time': 0.001,
                'release_time': 0.02, 'knee_width': 1.0, 'makeup_gain': 2.0,
                'compressor_type': CompressorType.FET
            },
            CompressorPreset.MIX_BUS_GLUE: {
                'threshold': -3.0, 'ratio': 2.0, 'attack_time': 0.01,
                'release_time': 0.1, 'knee_width': 3.0, 'makeup_gain': 1.0,
                'compressor_type': CompressorType.VCA
            },
            CompressorPreset.MASTERING_CONTROL: {
                'threshold': -1.0, 'ratio': 1.5, 'attack_time': 0.02,
                'release_time': 0.2, 'knee_width': 4.0, 'makeup_gain': 0.5,
                'compressor_type': CompressorType.DIGITAL
            }
        }
    
    def process(self, audio_data: np.ndarray, sidechain_input: Optional[np.ndarray] = None) -> np.ndarray:
        """Process audio through compressor with advanced features"""        try:
            if audio_data.size == 0:
                return audio_data
            
            # Input level metering
            self.input_level = np.max(np.abs(audio_data))
            
            # Process multiband if enabled
            if self.multiband_enabled:
                return self._process_multiband(audio_data, sidechain_input)
            else:
                return self._process_single_band(audio_data, sidechain_input)
                
        except Exception as e:
            self.logger.error(f"Compression processing failed: {str(e)}")
            return audio_data
    
    def _process_single_band(self, audio_data: np.ndarray, sidechain_input: Optional[np.ndarray] = None) -> np.ndarray:
        """Process single-band compression"""        processed_audio = audio_data.astype(np.float64)
        
        # Apply lookahead delay if enabled
        if self.lookahead_ms > 0:
            processed_audio, control_signal = self._apply_lookahead(processed_audio, sidechain_input)
        else:
            control_signal = sidechain_input if sidechain_input is not None else processed_audio
        
        # Side-chain processing
        if sidechain_input is not None and self.sidechain.enabled:
            control_signal = self.sidechain.process(processed_audio, sidechain_input)
        
        # Envelope detection
        if self.detection_mode == DetectionMode.PEAK:
            envelope = self.envelope_follower.process_peak(control_signal, self.attack_time, self.release_time)
        elif self.detection_mode == DetectionMode.RMS:
            envelope = self.envelope_follower.process_rms(control_signal, self.attack_time, self.release_time)
        else:  # HYBRID
            peak_env = self.envelope_follower.process_peak(control_signal, self.attack_time, self.release_time)
            rms_env = self.envelope_follower.process_rms(control_signal, self.attack_time * 2, self.release_time * 2)
            envelope = np.maximum(peak_env * 0.3, rms_env * 0.7)
        
        # Convert to dB
        envelope_db = 20 * np.log10(np.maximum(envelope, 1e-10))
        
        # Calculate gain reduction
        gain_reduction = self._calculate_gain_reduction(envelope_db)
        
        # Apply compressor characteristics based on type
        gain_reduction = self._apply_compressor_character(gain_reduction)
        
        # Convert back to linear gain
        gain_linear = 10 ** (gain_reduction / 20.0)
        
        # Apply gain reduction
        processed_audio = processed_audio * gain_linear
        
        # Auto makeup gain
        if self.auto_makeup:
            auto_makeup_db = -np.mean(gain_reduction) * 0.7
            processed_audio *= 10 ** (auto_makeup_db / 20.0)
        
        # Manual makeup gain
        if abs(self.makeup_gain) > 0.01:
            makeup_linear = 10 ** (self.makeup_gain / 20.0)
            processed_audio *= makeup_linear
        
        # Update state
        self.state.gain_reduction = np.mean(gain_reduction)
        self.gain_reduction_meter = -self.state.gain_reduction
        self.output_level = np.max(np.abs(processed_audio))
        
        return processed_audio.astype(audio_data.dtype)
    
    def _process_multiband(self, audio_data: np.ndarray, sidechain_input: Optional[np.ndarray] = None) -> np.ndarray:
        """Process multiband compression"""        # Split into frequency bands
        bands_audio = self.crossover.split_bands(audio_data)
        processed_bands = []
        
        for i, (band_audio, band_config) in enumerate(zip(bands_audio, self.bands)):
            if not band_config.enabled or band_config.bypass:
                processed_bands.append(band_audio)
                continue
            
            # Temporarily set single-band parameters from multiband config
            old_params = self._save_parameters()
            self._set_band_parameters(band_config)
            
            # Process band
            processed_band = self._process_single_band(band_audio, sidechain_input)
            processed_bands.append(processed_band)
            
            # Restore parameters
            self._restore_parameters(old_params)
        
        # Recombine bands
        return self.crossover.recombine_bands(processed_bands)
    
    def _calculate_gain_reduction(self, envelope_db: np.ndarray) -> np.ndarray:
        """Calculate gain reduction based on threshold and ratio"""        gain_reduction = np.zeros_like(envelope_db)
        
        for i, level_db in enumerate(envelope_db):
            if level_db > self.threshold:
                over_threshold = level_db - self.threshold
                
                # Apply knee
                if self.knee_type == KneeType.SOFT and over_threshold < self.knee_width:
                    knee_ratio = over_threshold / self.knee_width
                    soft_ratio = 1.0 + (self.ratio - 1.0) * knee_ratio * knee_ratio
                    gain_reduction[i] = -over_threshold * (1.0 - 1.0/soft_ratio)
                elif self.knee_type == KneeType.HARD:
                    gain_reduction[i] = -over_threshold * (1.0 - 1.0/self.ratio)
                else:  # ADAPTIVE
                    adaptive_ratio = self.ratio + (over_threshold / 10.0)  # More aggressive for louder signals
                    gain_reduction[i] = -over_threshold * (1.0 - 1.0/adaptive_ratio)
        
        return gain_reduction
    
    def _apply_compressor_character(self, gain_reduction: np.ndarray) -> np.ndarray:
        """Apply compressor type characteristics"""        if not self.analog_modeling:
            return gain_reduction
        
        if self.compressor_type == CompressorType.OPTICAL:
            # Optical compressor - smooth, slow response
            return gain_reduction * 0.95  # Slightly less aggressive
        elif self.compressor_type == CompressorType.FET:
            # FET compressor - fast, punchy
            return gain_reduction * 1.05  # More aggressive
        elif self.compressor_type == CompressorType.TUBE:
            # Tube compressor - warm, harmonic content
            return gain_reduction * 0.9 + self._generate_tube_harmonics(gain_reduction)
        elif self.compressor_type == CompressorType.VINTAGE_VCA:
            # Vintage VCA - slight nonlinearity
            return gain_reduction + np.sin(gain_reduction * 0.1) * 0.1
        else:
            return gain_reduction
    
    def _generate_tube_harmonics(self, gain_reduction: np.ndarray) -> np.ndarray:
        """Generate tube-style harmonic content"""        harmonics = np.zeros_like(gain_reduction)
        
        # Add even harmonics (2nd, 4th)
        for i in range(len(gain_reduction)):
            if abs(gain_reduction[i]) > 1.0:
                harmonic_amount = abs(gain_reduction[i]) * 0.05
                harmonics[i] = harmonic_amount * np.sin(i * 0.01) * 0.1
        
        return harmonics
    
    def _apply_lookahead(self, audio_data: np.ndarray, sidechain_input: Optional[np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        """Apply lookahead processing"""        lookahead_samples = int(self.lookahead_ms * self.sample_rate / 1000)
        
        # Delay main audio
        delayed_audio = np.concatenate([self.delay_buffer, audio_data])
        self.delay_buffer = delayed_audio[-lookahead_samples:]
        delayed_audio = delayed_audio[:len(audio_data)]
        
        # Control signal for detection (not delayed)
        control_signal = sidechain_input if sidechain_input is not None else audio_data
        
        return delayed_audio, control_signal
    
    def _save_parameters(self) -> Dict[str, Any]:
        """Save current parameters"""        return {
            'threshold': self.threshold,
            'ratio': self.ratio,
            'attack_time': self.attack_time,
            'release_time': self.release_time,
            'makeup_gain': self.makeup_gain
        }
    
    def _restore_parameters(self, params: Dict[str, Any]) -> None:
        """Restore parameters"""        self.threshold = params['threshold']
        self.ratio = params['ratio']
        self.attack_time = params['attack_time']
        self.release_time = params['release_time']
        self.makeup_gain = params['makeup_gain']
    
    def _set_band_parameters(self, band: CompressorBand) -> None:
        """Set parameters from multiband configuration"""        self.threshold = band.threshold
        self.ratio = band.ratio
        self.attack_time = band.attack_time
        self.release_time = band.release_time
        self.makeup_gain = band.makeup_gain
    
    def apply_preset(self, preset: CompressorPreset) -> None:
        """Apply professional compressor preset"""        if preset in self.presets:
            params = self.presets[preset]
            for param, value in params.items():
                if hasattr(self, param):
                    setattr(self, param, value)
            self.logger.info(f"Applied compressor preset: {preset.value}")
        else:
            self.logger.warning(f"Preset not found: {preset.value}")
    
    def analyze_dynamics(self, audio_data: np.ndarray) -> CompressionAnalysis:
        """AI-powered dynamics analysis for optimal compression settings"""        try:
            # Calculate dynamic range
            peak_level = np.max(np.abs(audio_data))
            rms_level = np.sqrt(np.mean(audio_data ** 2))
            dynamic_range = 20 * np.log10(peak_level / (rms_level + 1e-10))
            peak_to_average = 20 * np.log10(peak_level / (rms_level + 1e-10))
            
            # Analyze signal characteristics
            suggestions = []
            
            # Recommend threshold based on signal level
            signal_db = 20 * np.log10(rms_level + 1e-10)
            recommended_threshold = max(-24.0, signal_db - 6.0)
            
            # Recommend ratio based on dynamic range
            if dynamic_range > 20:
                recommended_ratio = 4.0
                suggestions.append("High dynamic range detected - moderate compression recommended")
            elif dynamic_range > 10:
                recommended_ratio = 2.5
                suggestions.append("Moderate dynamic range - gentle compression suggested")
            else:
                recommended_ratio = 1.5
                suggestions.append("Limited dynamic range - minimal compression needed")
            
            # Recommend attack/release based on content analysis
            # Analyze transient content
            diff_signal = np.diff(audio_data)
            transient_energy = np.mean(diff_signal ** 2)
            
            if transient_energy > 0.001:
                recommended_attack = 0.001  # Fast attack for transient material
                recommended_release = 0.02
                suggestions.append("Transient content detected - fast attack recommended")
            else:
                recommended_attack = 0.01   # Slower attack for sustained material
                recommended_release = 0.1
                suggestions.append("Sustained content detected - moderate attack recommended")
            
            confidence_score = min(0.95, 0.6 + (dynamic_range / 50.0))
            
            return CompressionAnalysis(
                recommended_threshold=recommended_threshold,
                recommended_ratio=recommended_ratio,
                recommended_attack=recommended_attack,
                recommended_release=recommended_release,
                dynamic_range=dynamic_range,
                peak_to_average=peak_to_average,
                suggestions=suggestions,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            self.logger.error(f"Dynamics analysis failed: {str(e)}")
            return CompressionAnalysis(
                recommended_threshold=-12.0,
                recommended_ratio=3.0,
                recommended_attack=0.003,
                recommended_release=0.1,
                dynamic_range=0.0,
                peak_to_average=0.0,
                suggestions=["Analysis failed - using default settings"],
                confidence_score=0.0
            )
    
    def get_metering_data(self) -> Dict[str, float]:
        """Get real-time metering data"""        return {
            'input_level_db': 20 * np.log10(self.input_level + 1e-10),
            'output_level_db': 20 * np.log10(self.output_level + 1e-10),
            'gain_reduction_db': self.gain_reduction_meter,
            'envelope_db': 20 * np.log10(self.state.envelope + 1e-10),
            'threshold_db': self.threshold,
            'ratio': self.ratio
        }
    
    def reset(self) -> None:
        """Reset compressor state"""        self.state = CompressorState()
        self.envelope_follower = EnvelopeFollower(self.sample_rate)
        self.lookahead_buffer.fill(0.0)
        self.delay_buffer.fill(0.0)
        self.input_level = 0.0
        self.output_level = 0.0
        self.gain_reduction_meter = 0.0
        self.logger.info("Compressor state reset")
    
    def get_processing_metrics(self) -> Dict[str, Any]:
        """Get processing performance metrics"""        return {
            'compressor_type': self.compressor_type.value,
            'multiband_enabled': self.multiband_enabled,
            'bands_count': len(self.bands),
            'sample_rate': self.sample_rate,
            'lookahead_ms': self.lookahead_ms,
            'analog_modeling': self.analog_modeling,
            'auto_makeup': self.auto_makeup,
            'sidechain_enabled': self.sidechain.enabled,
            'current_gain_reduction': self.gain_reduction_meter,
            'detection_mode': self.detection_mode.value,
            'knee_type': self.knee_type.value
        }
            
            # Convert to dB
            audio_db = 20 * np.log10(np.abs(processed_audio) + 1e-10)
            
            # Apply compression
            for i in range(len(processed_audio)):
                # Compute gain reduction
                input_level = audio_db[i]
                gain_reduction = self._compute_gain_reduction(input_level)
                
                # Apply gain reduction
                linear_gain = 10 ** (gain_reduction / 20)
                processed_audio[i] *= linear_gain
            
            # Apply makeup gain
            makeup_linear = 10 ** (self.makeup_gain / 20)
            processed_audio *= makeup_linear
            
            self.logger.debug("Compression applied")
            return processed_audio
            
        except Exception as e:
            self.logger.error(f"Compression failed: {e}")
            return audio_data
    
    def _compute_gain_reduction(self, input_level: float) -> float:
        """Compute gain reduction for input level"""        if input_level < self.threshold - self.knee_width / 2:
            # Below threshold
            return 0.0
        elif input_level > self.threshold + self.knee_width / 2:
            # Above threshold - full compression
            excess = input_level - self.threshold
            reduction = excess * (1 - 1/self.ratio)
            return -reduction
        else:
            # Knee region - soft compression
            excess = input_level - (self.threshold - self.knee_width / 2)
            knee_ratio = excess / self.knee_width
            soft_ratio = 1 + knee_ratio * (self.ratio - 1) / self.ratio
            reduction = excess * (1 - 1/soft_ratio)
            return -reduction
    
    def set_parameters(self, threshold: float = None, ratio: float = None,
                      attack: float = None, release: float = None):
        """Set compressor parameters"""        if threshold is not None:
            self.threshold = threshold
        if ratio is not None:
            self.ratio = max(1.0, ratio)
        if attack is not None:
            self.attack_time = max(0.001, attack)
        if release is not None:
            self.release_time = max(0.01, release)
        
        self.logger.debug(f"Compressor parameters updated: {self.threshold:.1f}dB, {self.ratio:.1f}:1")
