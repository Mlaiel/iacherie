"""Dynamic Range Enhancement Engine
Professional dynamic range expansion and compression for optimal audio quality.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from typing import Dict, Optional, Union, List, Tuple
from pathlib import Path
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class DynamicRangeConfig:
    """Configuration for dynamic range enhancement."""
    sample_rate: int = 44100
    enhancement_type: str = "adaptive"  # adaptive, compressor, expander, multiband
    threshold_db: float = -20.0  # dB threshold for processing
    ratio: float = 3.0  # Compression/expansion ratio
    attack_time_ms: float = 5.0  # Attack time in milliseconds
    release_time_ms: float = 50.0  # Release time in milliseconds
    knee_width_db: float = 2.0  # Soft knee width in dB
    makeup_gain_db: float = 0.0  # Makeup gain in dB
    lookahead_ms: float = 5.0  # Lookahead time for peak detection
    multiband_enabled: bool = True  # Enable multiband processing
    frequency_bands: List[float] = None  # Frequency bands for multiband [80, 320, 1280, 5120]
    auto_gain_enabled: bool = True  # Automatic gain compensation
    parallel_compression: float = 0.3  # Parallel compression mix (0-1)

class DynamicProcessor:
    """Advanced dynamic range processor with multiple algorithms."""
    
    def __init__(self, config -> None: DynamicRangeConfig, sample_rate -> None: int) -> None:
        self.config = config
        self.sample_rate = sample_rate
        
        # Convert time constants to samples
        self.attack_samples = int(config.attack_time_ms * sample_rate / 1000)
        self.release_samples = int(config.release_time_ms * sample_rate / 1000)
        self.lookahead_samples = int(config.lookahead_ms * sample_rate / 1000)
        
        # Initialize state variables
        self.envelope = 0.0
        self.gain_reduction = 0.0
        
        # Attack and release coefficients
        self.attack_coeff = np.exp(-1.0 / self.attack_samples) if self.attack_samples > 0 else 0.0
        self.release_coeff = np.exp(-1.0 / self.release_samples) if self.release_samples > 0 else 0.0
        
    def db_to_linear(self, db: float) -> float:
        """Convert dB to linear scale."""
        return 10.0 ** (db / 20.0)
    
    def linear_to_db(self, linear: float) -> float:
        """Convert linear to dB scale."""
        return 20.0 * np.log10(max(linear, 1e-10))
    
    def calculate_gain_reduction(self, input_level_db: float) -> float:
        """Calculate gain reduction based on compressor characteristics."""
        threshold_db = self.config.threshold_db
        ratio = self.config.ratio
        knee_width = self.config.knee_width_db
        
        # Soft knee implementation
        if input_level_db <= (threshold_db - knee_width / 2):
            # Below threshold
            gain_reduction_db = 0.0
        elif input_level_db >= (threshold_db + knee_width / 2):
            # Above threshold
            overshoot = input_level_db - threshold_db
            gain_reduction_db = overshoot * (1 - 1/ratio)
        else:
            # In knee region
            knee_input = input_level_db - threshold_db + knee_width / 2
            knee_ratio = knee_input / knee_width
            knee_output = knee_ratio * knee_ratio / 2
            gain_reduction_db = knee_output * knee_width * (1 - 1/ratio)
        
        return gain_reduction_db
    
    def process_sample(self, input_sample: float) -> float:
        """Process a single audio sample."""
        # Calculate input level in dB
        input_level = abs(input_sample)
        input_level_db = self.linear_to_db(input_level)
        
        # Calculate desired gain reduction
        target_gain_reduction = self.calculate_gain_reduction(input_level_db)
        
        # Apply envelope following
        if target_gain_reduction > self.gain_reduction:
            # Attack
            self.gain_reduction = target_gain_reduction + (self.gain_reduction - target_gain_reduction) * self.attack_coeff
        else:
            # Release
            self.gain_reduction = target_gain_reduction + (self.gain_reduction - target_gain_reduction) * self.release_coeff
        
        # Convert gain reduction to linear and apply
        gain_linear = self.db_to_linear(-self.gain_reduction + self.config.makeup_gain_db)
        
        return input_sample * gain_linear

class MultibandProcessor:
    """Multiband dynamic range processor."""
    
    def __init__(self, config -> None: DynamicRangeConfig, sample_rate -> None: int) -> None:
        self.config = config
        self.sample_rate = sample_rate
        
        # Default frequency bands if not specified
        if config.frequency_bands is None:
            self.frequency_bands = [80, 320, 1280, 5120]
        else:
            self.frequency_bands = config.frequency_bands
        
        # Create processors for each band
        self.processors = []
        for i in range(len(self.frequency_bands) + 1):
            band_config = DynamicRangeConfig(
                sample_rate=sample_rate,
                threshold_db=config.threshold_db,
                ratio=config.ratio * (0.8 + 0.4 * i / len(self.frequency_bands)),  # Vary ratio per band
                attack_time_ms=config.attack_time_ms,
                release_time_ms=config.release_time_ms,
                knee_width_db=config.knee_width_db,
                makeup_gain_db=config.makeup_gain_db
            )
            self.processors.append(DynamicProcessor(band_config, sample_rate))
        
        # Create crossover filters
        self.crossover_filters = self._create_crossover_filters()
    
    def _create_crossover_filters(self) -> List[Tuple[np.ndarray, np.ndarray]]:
        """Create crossover filters for frequency separation."""
        filters = []
        nyquist = self.sample_rate / 2
        
        for i, freq in enumerate(self.frequency_bands):
            if freq < nyquist:
                # Butterworth filters
                if i == 0:
                    # Low-pass for first band
                    b, a = signal.butter(4, freq / nyquist, btype='low')
                else:
                    # Band-pass for middle bands
                    low_freq = self.frequency_bands[i-1] / nyquist
                    high_freq = freq / nyquist
                    b, a = signal.butter(4, [low_freq, high_freq], btype='band')
                filters.append((b, a))
        
        # High-pass for last band
        if self.frequency_bands:
            last_freq = self.frequency_bands[-1] / nyquist
            if last_freq < 1.0:
                b, a = signal.butter(4, last_freq, btype='high')
                filters.append((b, a))
        
        return filters
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """Process audio with multiband dynamics."""
        # Split into frequency bands
        bands = []
        for b, a in self.crossover_filters:
            band_audio = signal.filtfilt(b, a, audio)
            bands.append(band_audio)
        
        # Process each band
        processed_bands = []
        for i, band in enumerate(bands):
            if i < len(self.processors):
                processed_band = np.array([
                    self.processors[i].process_sample(sample) for sample in band
                ])
                processed_bands.append(processed_band)
        
        # Sum processed bands
        output = np.zeros_like(audio)
        for processed_band in processed_bands:
            output += processed_band
        
        return output

class AdaptiveDynamicsProcessor:
    """Adaptive dynamics processor that adjusts parameters based on content."""
    
    def __init__(self, config -> None: DynamicRangeConfig, sample_rate -> None: int) -> None:
        self.config = config
        self.sample_rate = sample_rate
        self.processor = DynamicProcessor(config, sample_rate)
        
        # Analysis parameters
        self.analysis_window = int(sample_rate * 0.1)  # 100ms analysis window
        self.peak_history = []
        self.rms_history = []
        
    def analyze_content(self, audio: np.ndarray) -> Dict[str, float]:
        """Analyze audio content to determine optimal processing parameters."""
        # Calculate peak and RMS over time
        window_size = self.analysis_window
        peaks = []
        rms_values = []
        
        for i in range(0, len(audio) - window_size, window_size // 2):
            window = audio[i:i + window_size]
            peak = np.max(np.abs(window))
            rms = np.sqrt(np.mean(window**2))
            peaks.append(peak)
            rms_values.append(rms)
        
        # Calculate statistics
        peak_to_rms_ratio = np.mean([p / (r + 1e-10) for p, r in zip(peaks, rms_values)])
        dynamic_range = self.linear_to_db(np.max(peaks)) - self.linear_to_db(np.mean(rms_values))
        
        return {
            "peak_to_rms_ratio": peak_to_rms_ratio,
            "dynamic_range_db": dynamic_range,
            "average_level_db": self.linear_to_db(np.mean(rms_values)),
            "peak_level_db": self.linear_to_db(np.max(peaks))
        }
    
    def linear_to_db(self, linear: float) -> float:
        """Convert linear to dB scale."""
        return 20.0 * np.log10(max(linear, 1e-10))
    
    def adapt_parameters(self, analysis -> None: Dict[str, float]) -> None:
        """Adapt processing parameters based on content analysis."""
        # Adjust threshold based on average level
        if analysis["average_level_db"] < -30:
            # Quiet material - lower threshold
            self.processor.config.threshold_db = -25
        elif analysis["average_level_db"] > -10:
            # Loud material - higher threshold
            self.processor.config.threshold_db = -15
        
        # Adjust ratio based on dynamic range
        if analysis["dynamic_range_db"] > 40:
            # High dynamic range - gentle processing
            self.processor.config.ratio = 2.0
        elif analysis["dynamic_range_db"] < 20:
            # Low dynamic range - more aggressive
            self.processor.config.ratio = 4.0
        
        # Recalculate coefficients
        self.processor.attack_coeff = np.exp(-1.0 / self.processor.attack_samples)
        self.processor.release_coeff = np.exp(-1.0 / self.processor.release_samples)

class DynamicRangeEnhancementEngine:
    """Enterprise dynamic range enhancement engine with advanced algorithms."""
    
    def __init__(self) -> None:
        self.config = DynamicRangeConfig()
        
    async def enhance_dynamic_range(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        enhancement_level: float = 0.5,
        config: Optional[DynamicRangeConfig] = None
    ) -> Dict[str, any]:
        """Enhance audio/video dynamic range with professional algorithms."""
        try:
            if config:
                self.config = config
                
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            logger.info(f"Starting dynamic range enhancement: {input_path}")
            
            # Load audio file
            audio, sample_rate = librosa.load(str(input_path), sr=self.config.sample_rate, mono=False)
            
            # Handle mono/stereo
            if audio.ndim == 1:
                is_stereo = False
                channels = [audio]
            else:
                is_stereo = True
                channels = [audio[0], audio[1]]
            
            enhanced_channels = []
            
            for channel in channels:
                enhanced_channel = await self._enhance_channel(
                    channel, sample_rate, enhancement_level
                )
                enhanced_channels.append(enhanced_channel)
            
            # Reconstruct audio
            if is_stereo and len(enhanced_channels) == 2:
                enhanced_audio = np.array([enhanced_channels[0], enhanced_channels[1]])
            else:
                enhanced_audio = enhanced_channels[0]
            
            # Apply auto-gain if enabled
            if self.config.auto_gain_enabled:
                enhanced_audio = self._apply_auto_gain(audio, enhanced_audio)
            
            # Save enhanced audio
            sf.write(
                str(output_path),
                enhanced_audio.T if enhanced_audio.ndim == 2 else enhanced_audio,
                sample_rate,
                subtype='PCM_24'
            )
            
            # Calculate enhancement metrics
            metrics = self._calculate_enhancement_metrics(audio, enhanced_audio)
            
            logger.info("Dynamic range enhancement completed successfully")
            
            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "enhancement_level": enhancement_level,
                "enhancement_type": self.config.enhancement_type,
                "sample_rate": sample_rate,
                "is_stereo": is_stereo,
                "metrics": metrics,
                "parameters_used": {
                    "threshold_db": self.config.threshold_db,
                    "ratio": self.config.ratio,
                    "attack_ms": self.config.attack_time_ms,
                    "release_ms": self.config.release_time_ms
                }
            }
            
        except Exception as e:
            logger.error(f"Dynamic range enhancement failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "input_path": str(input_path),
                "enhancement_level": enhancement_level
            }
    
    async def _enhance_channel(
        self, 
        audio: np.ndarray, 
        sample_rate: int, 
        enhancement_level: float
    ) -> np.ndarray:
        """Enhance dynamic range of a single audio channel."""
        
        # Adjust config based on enhancement level
        adjusted_config = DynamicRangeConfig(
            sample_rate=sample_rate,
            enhancement_type=self.config.enhancement_type,
            threshold_db=self.config.threshold_db,
            ratio=1.0 + (self.config.ratio - 1.0) * enhancement_level,
            attack_time_ms=self.config.attack_time_ms,
            release_time_ms=self.config.release_time_ms,
            knee_width_db=self.config.knee_width_db,
            makeup_gain_db=self.config.makeup_gain_db,
            multiband_enabled=self.config.multiband_enabled,
            frequency_bands=self.config.frequency_bands,
            parallel_compression=self.config.parallel_compression * enhancement_level
        )
        
        if adjusted_config.enhancement_type == "adaptive":
            processor = AdaptiveDynamicsProcessor(adjusted_config, sample_rate)
            
            # Analyze content and adapt parameters
            analysis = processor.analyze_content(audio)
            processor.adapt_parameters(analysis)
            
            # Process audio
            enhanced = np.array([processor.processor.process_sample(sample) for sample in audio])
            
        elif adjusted_config.enhancement_type == "multiband":
            processor = MultibandProcessor(adjusted_config, sample_rate)
            enhanced = processor.process(audio)
            
        elif adjusted_config.enhancement_type == "compressor":
            processor = DynamicProcessor(adjusted_config, sample_rate)
            enhanced = np.array([processor.process_sample(sample) for sample in audio])
            
        elif adjusted_config.enhancement_type == "expander":
            # For expansion, invert the ratio
            adjusted_config.ratio = 1.0 / adjusted_config.ratio
            adjusted_config.threshold_db = -40.0  # Lower threshold for expansion
            processor = DynamicProcessor(adjusted_config, sample_rate)
            enhanced = np.array([processor.process_sample(sample) for sample in audio])
            
        else:  # Default to adaptive
            processor = DynamicProcessor(adjusted_config, sample_rate)
            enhanced = np.array([processor.process_sample(sample) for sample in audio])
        
        # Apply parallel compression if enabled
        if adjusted_config.parallel_compression > 0:
            mix = adjusted_config.parallel_compression
            enhanced = (1 - mix) * audio + mix * enhanced
        
        return enhanced
    
    def _apply_auto_gain(self, original: np.ndarray, enhanced: np.ndarray) -> np.ndarray:
        """Apply automatic gain compensation to match original levels."""
        original_rms = np.sqrt(np.mean(original.flatten()**2))
        enhanced_rms = np.sqrt(np.mean(enhanced.flatten()**2))
        
        if enhanced_rms > 0:
            gain_factor = original_rms / enhanced_rms
            # Limit gain adjustment to prevent extreme corrections
            gain_factor = np.clip(gain_factor, 0.5, 2.0)
            enhanced = enhanced * gain_factor
        
        return enhanced
    
    def _calculate_enhancement_metrics(self, original: np.ndarray, enhanced: np.ndarray) -> Dict[str, float]:
        """Calculate metrics to evaluate enhancement quality."""
        # Ensure same length for comparison
        min_length = min(len(original.flatten()), len(enhanced.flatten()))
        orig_flat = original.flatten()[:min_length]
        enh_flat = enhanced.flatten()[:min_length]
        
        # Dynamic range calculations
        orig_peak = np.max(np.abs(orig_flat))
        orig_rms = np.sqrt(np.mean(orig_flat**2))
        orig_dynamic_range = 20 * np.log10(orig_peak / (orig_rms + 1e-10))
        
        enh_peak = np.max(np.abs(enh_flat))
        enh_rms = np.sqrt(np.mean(enh_flat**2))
        enh_dynamic_range = 20 * np.log10(enh_peak / (enh_rms + 1e-10))
        
        # Loudness change
        loudness_change = 20 * np.log10((enh_rms + 1e-10) / (orig_rms + 1e-10))
        
        # Correlation (preservation of waveform)
        correlation = np.corrcoef(orig_flat, enh_flat)[0, 1]
        
        return {
            "original_dynamic_range_db": float(orig_dynamic_range),
            "enhanced_dynamic_range_db": float(enh_dynamic_range),
            "dynamic_range_change_db": float(enh_dynamic_range - orig_dynamic_range),
            "loudness_change_db": float(loudness_change),
            "waveform_correlation": float(correlation),
            "enhancement_quality": float(min(1.0, max(0.0, correlation)))
        }
    
    async def batch_enhance(
        self,
        input_paths: List[Union[str, Path]],
        output_dir: Union[str, Path],
        enhancement_level: float = 0.5,
        config: Optional[DynamicRangeConfig] = None
    ) -> Dict[str, any]:
        """Batch dynamic range enhancement for multiple files."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        for input_path in input_paths:
            input_path = Path(input_path)
            output_path = output_dir / f"{input_path.stem}_enhanced{input_path.suffix}"
            
            result = await self.enhance_dynamic_range(input_path, output_path, enhancement_level, config)
            results.append(result)
        
        successful = sum(1 for r in results if r.get("success", False))
        
        return {
            "success": True,
            "processed_files": len(input_paths),
            "successful_enhancements": successful,
            "failed_enhancements": len(input_paths) - successful,
            "results": results
        }