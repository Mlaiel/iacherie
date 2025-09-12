"""Audio Restoration Engine
Professional audio restoration for vintage and damaged recordings.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from scipy.fftpack import fft, ifft
from typing import Dict, Optional, Union, List, Tuple
from pathlib import Path
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class AudioRestorationConfig:
    """Configuration for audio restoration."""
    sample_rate: int = 44100
    noise_reduction_strength: float = 0.7  # 0.0 to 1.0
    declicking_enabled: bool = True
    dehumming_enabled: bool = True
    harmonic_enhancement: bool = True
    dynamic_range_expansion: float = 1.2  # 1.0 to 2.0
    spectral_smoothing: bool = True
    vintage_warmth: float = 0.3  # 0.0 to 1.0
    stereo_enhancement: bool = True
    output_format: str = "wav"
    bit_depth: int = 24

class SpectralSubtractionFilter:
    """Spectral subtraction for noise reduction."""
    
    def __init__(self, alpha: float = 2.0, beta: float = 0.01):
        self.alpha = alpha  # Over-subtraction factor
        self.beta = beta    # Spectral floor factor
        
    def estimate_noise_spectrum(self, audio: np.ndarray, noise_duration: float = 0.5) -> np.ndarray:
        """Estimate noise spectrum from the beginning of the audio."""
        noise_samples = int(noise_duration * len(audio))
        noise_segment = audio[:noise_samples]
        noise_fft = np.abs(fft(noise_segment))
        return noise_fft
    
    def reduce_noise(self, audio: np.ndarray, noise_spectrum: np.ndarray) -> np.ndarray:
        """Apply spectral subtraction noise reduction."""
        audio_fft = fft(audio)
        magnitude = np.abs(audio_fft)
        phase = np.angle(audio_fft)
        
        # Spectral subtraction
        cleaned_magnitude = magnitude - self.alpha * noise_spectrum[:len(magnitude)]
        
        # Apply spectral floor
        spectral_floor = self.beta * magnitude
        cleaned_magnitude = np.maximum(cleaned_magnitude, spectral_floor)
        
        # Reconstruct signal
        cleaned_fft = cleaned_magnitude * np.exp(1j * phase)
        cleaned_audio = np.real(ifft(cleaned_fft))
        
        return cleaned_audio

class ClickRemovalFilter:
    """Click and pop removal filter."""
    
    def __init__(self, threshold: float = 0.1, window_size: int = 5):
        self.threshold = threshold
        self.window_size = window_size
    
    def detect_clicks(self, audio: np.ndarray) -> List[int]:
        """Detect click positions in audio."""
        # Calculate derivative to find sudden changes
        diff = np.abs(np.diff(audio))
        
        # Find peaks that exceed threshold
        clicks = []
        for i in range(1, len(diff) - 1):
            if diff[i] > self.threshold and diff[i] > diff[i-1] and diff[i] > diff[i+1]:
                clicks.append(i)
        
        return clicks
    
    def remove_clicks(self, audio: np.ndarray) -> np.ndarray:
        """Remove detected clicks by interpolation."""
        clicks = self.detect_clicks(audio)
        cleaned_audio = audio.copy()
        
        for click_pos in clicks:
            start = max(0, click_pos - self.window_size)
            end = min(len(audio), click_pos + self.window_size + 1)
            
            # Linear interpolation
            if start < click_pos < end - 1:
                cleaned_audio[click_pos] = (cleaned_audio[start] + cleaned_audio[end-1]) / 2
        
        return cleaned_audio

class HumRemovalFilter:
    """Remove electrical hum (50Hz/60Hz and harmonics)."""
    
    def __init__(self, fundamental_freq: float = 50.0, sample_rate: int = 44100):
        self.fundamental_freq = fundamental_freq
        self.sample_rate = sample_rate
        self.harmonics = [1, 2, 3, 4, 5]  # Fundamental and first 4 harmonics
    
    def create_notch_filter(self, freq: float, q_factor: float = 30.0) -> Tuple[np.ndarray, np.ndarray]:
        """Create a notch filter for specific frequency."""
        nyquist = self.sample_rate / 2
        normalized_freq = freq / nyquist
        
        # Design notch filter
        b, a = signal.iirnotch(normalized_freq, q_factor)
        return b, a
    
    def remove_hum(self, audio: np.ndarray) -> np.ndarray:
        """Remove hum and its harmonics."""
        cleaned_audio = audio.copy()
        
        for harmonic in self.harmonics:
            target_freq = self.fundamental_freq * harmonic
            
            if target_freq < self.sample_rate / 2:  # Ensure frequency is below Nyquist
                b, a = self.create_notch_filter(target_freq)
                cleaned_audio = signal.filtfilt(b, a, cleaned_audio)
        
        return cleaned_audio

class HarmonicEnhancer:
    """Enhance harmonic content for warmth and presence."""
    
    def __init__(self, enhancement_factor: float = 0.3):
        self.enhancement_factor = enhancement_factor
    
    def enhance_harmonics(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Add subtle harmonic enhancement."""
        # Generate harmonics using non-linear processing
        enhanced = audio.copy()
        
        # Add gentle saturation
        saturation_amount = self.enhancement_factor * 0.1
        saturated = np.tanh(audio * (1 + saturation_amount))
        
        # Blend with original
        enhanced = (1 - self.enhancement_factor) * audio + self.enhancement_factor * saturated
        
        return enhanced

class AudioRestorationEngine:
    """Enterprise audio restoration engine with advanced algorithms."""
    
    def __init__(self):
        self.config = AudioRestorationConfig()
        
    async def restore_audio(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        restoration_type: str = "auto",
        config: Optional[AudioRestorationConfig] = None
    ) -> Dict[str, any]:
        """Restore damaged or vintage audio with professional algorithms."""
        try:
            if config:
                self.config = config
                
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            logger.info(f"Starting audio restoration: {input_path}")
            
            # Load audio file
            audio, original_sr = librosa.load(str(input_path), sr=None, mono=False)
            
            # Handle mono/stereo
            if audio.ndim == 1:
                is_stereo = False
                channels = [audio]
            else:
                is_stereo = True
                channels = [audio[0], audio[1]]
            
            restored_channels = []
            
            for channel in channels:
                restored_channel = await self._restore_channel(
                    channel, original_sr, restoration_type
                )
                restored_channels.append(restored_channel)
            
            # Reconstruct audio
            if is_stereo and len(restored_channels) == 2:
                restored_audio = np.array([restored_channels[0], restored_channels[1]])
                
                # Apply stereo enhancement if enabled
                if self.config.stereo_enhancement:
                    restored_audio = self._enhance_stereo(restored_audio)
            else:
                restored_audio = restored_channels[0]
            
            # Resample if needed
            if original_sr != self.config.sample_rate:
                if restored_audio.ndim == 2:
                    restored_audio = np.array([
                        librosa.resample(restored_audio[0], orig_sr=original_sr, target_sr=self.config.sample_rate),
                        librosa.resample(restored_audio[1], orig_sr=original_sr, target_sr=self.config.sample_rate)
                    ])
                else:
                    restored_audio = librosa.resample(
                        restored_audio, orig_sr=original_sr, target_sr=self.config.sample_rate
                    )
            
            # Save restored audio
            sf.write(
                str(output_path),
                restored_audio.T if restored_audio.ndim == 2 else restored_audio,
                self.config.sample_rate,
                subtype=f'PCM_{self.config.bit_depth}'
            )
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(audio, restored_audio)
            
            logger.info("Audio restoration completed successfully")
            
            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "restoration_type": restoration_type,
                "original_sample_rate": original_sr,
                "output_sample_rate": self.config.sample_rate,
                "is_stereo": is_stereo,
                "quality_metrics": quality_metrics,
                "processing_chain": self._get_processing_chain(restoration_type)
            }
            
        except Exception as e:
            logger.error(f"Audio restoration failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "input_path": str(input_path),
                "restoration_type": restoration_type
            }
    
    async def _restore_channel(
        self, 
        audio: np.ndarray, 
        sample_rate: int, 
        restoration_type: str
    ) -> np.ndarray:
        """Restore a single audio channel."""
        restored = audio.copy()
        
        # Apply restoration chain based on type
        if restoration_type in ["auto", "noise_reduction", "full"]:
            # Noise reduction
            if self.config.noise_reduction_strength > 0:
                noise_filter = SpectralSubtractionFilter()
                noise_spectrum = noise_filter.estimate_noise_spectrum(restored)
                restored = noise_filter.reduce_noise(restored, noise_spectrum)
        
        if restoration_type in ["auto", "declicking", "full"]:
            # Click removal
            if self.config.declicking_enabled:
                click_filter = ClickRemovalFilter()
                restored = click_filter.remove_clicks(restored)
        
        if restoration_type in ["auto", "dehumming", "full"]:
            # Hum removal
            if self.config.dehumming_enabled:
                hum_filter = HumRemovalFilter(sample_rate=sample_rate)
                restored = hum_filter.remove_hum(restored)
        
        if restoration_type in ["auto", "enhancement", "full"]:
            # Harmonic enhancement
            if self.config.harmonic_enhancement:
                enhancer = HarmonicEnhancer(self.config.vintage_warmth)
                restored = enhancer.enhance_harmonics(restored, sample_rate)
        
        if restoration_type in ["auto", "dynamics", "full"]:
            # Dynamic range expansion
            if self.config.dynamic_range_expansion > 1.0:
                restored = self._expand_dynamic_range(restored, self.config.dynamic_range_expansion)
        
        if restoration_type in ["auto", "spectral", "full"]:
            # Spectral smoothing
            if self.config.spectral_smoothing:
                restored = self._apply_spectral_smoothing(restored)
        
        return restored
    
    def _expand_dynamic_range(self, audio: np.ndarray, factor: float) -> np.ndarray:
        """Expand dynamic range while preserving peak levels."""
        # Calculate RMS
        rms = np.sqrt(np.mean(audio**2))
        
        # Apply expansion
        normalized = audio / (rms + 1e-8)
        expanded = np.sign(normalized) * (np.abs(normalized) ** (1/factor))
        
        # Restore original RMS level
        expanded_audio = expanded * rms
        
        # Ensure no clipping
        max_val = np.max(np.abs(expanded_audio))
        if max_val > 1.0:
            expanded_audio = expanded_audio / max_val * 0.95
        
        return expanded_audio
    
    def _apply_spectral_smoothing(self, audio: np.ndarray) -> np.ndarray:
        """Apply spectral smoothing to reduce artifacts."""
        # STFT
        stft = librosa.stft(audio, hop_length=512, n_fft=2048)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Apply smoothing kernel
        from scipy.ndimage import gaussian_filter
        smoothed_magnitude = gaussian_filter(magnitude, sigma=0.5)
        
        # Reconstruct
        smoothed_stft = smoothed_magnitude * np.exp(1j * phase)
        smoothed_audio = librosa.istft(smoothed_stft, hop_length=512)
        
        return smoothed_audio
    
    def _enhance_stereo(self, stereo_audio: np.ndarray) -> np.ndarray:
        """Enhance stereo width and imaging."""
        left, right = stereo_audio[0], stereo_audio[1]
        
        # Mid-side processing
        mid = (left + right) / 2
        side = (left - right) / 2
        
        # Enhance side signal slightly
        enhanced_side = side * 1.1
        
        # Reconstruct left/right
        enhanced_left = mid + enhanced_side
        enhanced_right = mid - enhanced_side
        
        return np.array([enhanced_left, enhanced_right])
    
    def _calculate_quality_metrics(self, original: np.ndarray, restored: np.ndarray) -> Dict[str, float]:
        """Calculate audio quality metrics."""
        # Ensure same length for comparison
        min_length = min(len(original.flatten()), len(restored.flatten()))
        orig_flat = original.flatten()[:min_length]
        rest_flat = restored.flatten()[:min_length]
        
        # Signal-to-noise ratio improvement
        original_noise = np.std(orig_flat)
        restored_noise = np.std(rest_flat)
        snr_improvement = 20 * np.log10(original_noise / (restored_noise + 1e-8))
        
        # Dynamic range
        orig_dynamic_range = 20 * np.log10(np.max(np.abs(orig_flat)) / (np.mean(np.abs(orig_flat)) + 1e-8))
        rest_dynamic_range = 20 * np.log10(np.max(np.abs(rest_flat)) / (np.mean(np.abs(rest_flat)) + 1e-8))
        
        return {
            "snr_improvement_db": float(snr_improvement),
            "original_dynamic_range_db": float(orig_dynamic_range),
            "restored_dynamic_range_db": float(rest_dynamic_range),
            "restoration_quality": min(1.0, max(0.0, snr_improvement / 10.0))
        }
    
    def _get_processing_chain(self, restoration_type: str) -> List[str]:
        """Get list of processing steps applied."""
        chain = []
        
        if restoration_type in ["auto", "noise_reduction", "full"]:
            chain.append("spectral_subtraction")
        if restoration_type in ["auto", "declicking", "full"]:
            chain.append("click_removal")
        if restoration_type in ["auto", "dehumming", "full"]:
            chain.append("hum_removal")
        if restoration_type in ["auto", "enhancement", "full"]:
            chain.append("harmonic_enhancement")
        if restoration_type in ["auto", "dynamics", "full"]:
            chain.append("dynamic_range_expansion")
        if restoration_type in ["auto", "spectral", "full"]:
            chain.append("spectral_smoothing")
        
        return chain
    
    async def batch_restore(
        self,
        input_paths: List[Union[str, Path]],
        output_dir: Union[str, Path],
        restoration_type: str = "auto",
        config: Optional[AudioRestorationConfig] = None
    ) -> Dict[str, any]:
        """Batch audio restoration for multiple files."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        for input_path in input_paths:
            input_path = Path(input_path)
            output_path = output_dir / f"{input_path.stem}_restored{input_path.suffix}"
            
            result = await self.restore_audio(input_path, output_path, restoration_type, config)
            results.append(result)
        
        successful = sum(1 for r in results if r.get("success", False))
        
        return {
            "success": True,
            "processed_files": len(input_paths),
            "successful_restorations": successful,
            "failed_restorations": len(input_paths) - successful,
            "results": results
        }