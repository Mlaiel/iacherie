"""🎵 Professional Audio Visualization Engine

Advanced waveform and spectrogram generation with professional features for
broadcast, mastering, and analytical applications.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ LEGAL WARNING & COPYRIGHT PROTECTION
=====================================
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
ANY unauthorized use, copying, modification, distribution, or commercialization
of this code WITHOUT explicit written permission is STRICTLY PROHIBITED
and will result in legal action under German and International copyright law.

For licensing inquiries: mlaiel@live.de

Expert Development Team:
- Lead Dev IA: Advanced visualization algorithms
- Backend Senior: Robust architecture and scalable systems  
- ML Engineer: Machine learning-based analysis
- Audio Engineer: Professional audio visualization standards
- DevOps Engineer: Production deployment and optimization
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import librosa
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import scipy.signal
import cv2
from PIL import Image, ImageDraw, ImageFont
import base64
import io


class WaveformStyle(Enum):
    """Waveform visualization styles"""
    CLASSIC = "classic"
    FILLED = "filled"
    GRADIENT = "gradient"
    MIRRORED = "mirrored"
    ENVELOPE = "envelope"
    PEAKS_ONLY = "peaks_only"
    RMS_OVERLAY = "rms_overlay"
    BROADCAST = "broadcast"


class SpectrogramMode(Enum):
    """Spectrogram analysis modes"""
    LINEAR = "linear"
    LOG = "log" 
    MEL = "mel"
    CHROMA = "chroma"
    CONSTANT_Q = "constant_q"
    BROADCAST = "broadcast"
    MASTERING = "mastering"


class ColorScheme(Enum):
    """Professional color schemes"""
    CLASSIC = "classic"
    FIRE = "fire"
    OCEAN = "ocean"
    GRAYSCALE = "grayscale"
    RAINBOW = "rainbow"
    STUDIO = "studio"
    BROADCAST = "broadcast"
    MASTERING = "mastering"


@dataclass
class WaveformConfig:
    """Waveform generation configuration"""
    width: int = 1920
    height: int = 400
    style: WaveformStyle = WaveformStyle.CLASSIC
    color_scheme: ColorScheme = ColorScheme.STUDIO
    show_grid: bool = True
    show_timecode: bool = True
    show_levels: bool = True
    show_peaks: bool = True
    zoom_start: float = 0.0
    zoom_end: float = 1.0
    background_color: str = "#1a1a1a"
    waveform_color: str = "#00ff88"
    peak_color: str = "#ff4444"
    grid_color: str = "#333333"
    text_color: str = "#ffffff"
    sample_reduction_factor: int = 100


@dataclass 
class SpectrogramConfig:
    """Spectrogram generation configuration"""
    width: int = 1920
    height: int = 1080
    mode: SpectrogramMode = SpectrogramMode.LOG
    color_scheme: ColorScheme = ColorScheme.STUDIO
    fft_size: int = 2048
    hop_length: int = 512
    freq_min: float = 20.0
    freq_max: float = 20000.0
    db_min: float = -80.0
    db_max: float = 0.0
    show_colorbar: bool = True
    show_frequency_labels: bool = True
    show_time_labels: bool = True
    window_type: str = "hann"
    mel_bins: int = 128
    chroma_bins: int = 12


@dataclass
class VisualizationResult:
    """Visualization generation result"""
    image_data: np.ndarray
    metadata: Dict[str, Any]
    base64_image: str
    file_path: Optional[str] = None
    analysis_data: Optional[Dict[str, Any]] = None


class ProfessionalAudioVisualizer:
    """🎵 Professional Audio Visualization Engine
    
    Advanced waveform and spectrogram generation with broadcast-quality
    output and comprehensive analytical features.
    """
    
    def __init__(self, sample_rate: int = 44100):
        """Initialize professional audio visualizer.
        
        Args:
            sample_rate: Audio sample rate
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Create professional color schemes
        self._initialize_color_schemes()
        
        self.logger.info("Professional Audio Visualizer initialized")
    
    def _initialize_color_schemes(self) -> None:
        """Initialize professional color schemes."""
        self.color_schemes = {
            ColorScheme.CLASSIC: {
                'colors': ['#000033', '#000066', '#0000ff', '#0066ff', '#00ffff', '#66ff00', '#ffff00', '#ff6600', '#ff0000'],
                'name': 'classic'
            },
            ColorScheme.FIRE: {
                'colors': ['#000000', '#330000', '#660000', '#990000', '#cc0000', '#ff0000', '#ff3300', '#ff6600', '#ff9900', '#ffcc00', '#ffff00'],
                'name': 'fire'
            },
            ColorScheme.OCEAN: {
                'colors': ['#000033', '#000066', '#003366', '#006699', '#0099cc', '#00ccff', '#66ffff'],
                'name': 'ocean'
            },
            ColorScheme.STUDIO: {
                'colors': ['#1a1a1a', '#004400', '#008800', '#00cc00', '#44ff44', '#88ff88', '#ccffcc'],
                'name': 'studio'
            },
            ColorScheme.BROADCAST: {
                'colors': ['#000000', '#1a0033', '#330066', '#4d0099', '#6600cc', '#8000ff', '#9933ff', '#b366ff', '#cc99ff'],
                'name': 'broadcast'
            },
            ColorScheme.MASTERING: {
                'colors': ['#0d0d0d', '#1a1a1a', '#262626', '#333333', '#404040', '#4d4d4d', '#666666', '#808080', '#999999'],
                'name': 'mastering'
            }
        }
    
    async def generate_professional_waveform(self, 
                                           audio_data: np.ndarray, 
                                           config: WaveformConfig = None) -> VisualizationResult:
        """Generate professional-quality waveform visualization.
        
        Args:
            audio_data: Input audio signal
            config: Waveform configuration
            
        Returns:
            Visualization result with image and metadata
        """
        if config is None:
            config = WaveformConfig()
        
        try:
            self.logger.info("Generating professional waveform...")
            
            # Prepare audio data
            if len(audio_data.shape) > 1:
                # Convert stereo to mono for waveform
                audio_mono = np.mean(audio_data, axis=0)
            else:
                audio_mono = audio_data
            
            # Apply zoom if specified
            start_sample = int(config.zoom_start * len(audio_mono))
            end_sample = int(config.zoom_end * len(audio_mono))
            audio_section = audio_mono[start_sample:end_sample]
            
            # Downsample for visualization
            if len(audio_section) > config.width * config.sample_reduction_factor:
                downsample_factor = len(audio_section) // (config.width * config.sample_reduction_factor)
                audio_section = audio_section[::downsample_factor]
            
            # Create figure
            fig, ax = plt.subplots(figsize=(config.width/100, config.height/100), dpi=100)
            fig.patch.set_facecolor(config.background_color)
            ax.set_facecolor(config.background_color)
            
            # Generate time axis
            time_axis = np.linspace(0, len(audio_section) / self.sample_rate, len(audio_section))
            
            # Generate waveform based on style
            if config.style == WaveformStyle.CLASSIC:
                ax.plot(time_axis, audio_section, color=config.waveform_color, linewidth=0.5)
                
            elif config.style == WaveformStyle.FILLED:
                ax.fill_between(time_axis, audio_section, 0, color=config.waveform_color, alpha=0.7)
                
            elif config.style == WaveformStyle.MIRRORED:
                ax.fill_between(time_axis, audio_section, 0, color=config.waveform_color, alpha=0.7)
                ax.fill_between(time_axis, -audio_section, 0, color=config.waveform_color, alpha=0.7)
                
            elif config.style == WaveformStyle.ENVELOPE:
                # Calculate envelope
                envelope = np.abs(scipy.signal.hilbert(audio_section))
                ax.plot(time_axis, envelope, color=config.waveform_color, linewidth=1)
                ax.plot(time_axis, -envelope, color=config.waveform_color, linewidth=1)
                
            elif config.style == WaveformStyle.RMS_OVERLAY:
                # RMS calculation
                window_size = max(1, len(audio_section) // 1000)
                rms = []
                rms_times = []
                
                for i in range(0, len(audio_section) - window_size, window_size):
                    window = audio_section[i:i + window_size]
                    rms_val = np.sqrt(np.mean(window**2))
                    rms.append(rms_val)
                    rms_times.append(time_axis[i])
                
                ax.plot(time_axis, audio_section, color=config.waveform_color, alpha=0.5, linewidth=0.5)
                ax.plot(rms_times, rms, color=config.peak_color, linewidth=2, label='RMS')
                ax.plot(rms_times, [-r for r in rms], color=config.peak_color, linewidth=2)
            
            # Add peak markers if enabled
            if config.show_peaks:
                peaks, _ = scipy.signal.find_peaks(np.abs(audio_section), height=0.7 * np.max(np.abs(audio_section)))
                if len(peaks) > 0:
                    ax.scatter(time_axis[peaks], audio_section[peaks], color=config.peak_color, s=20, zorder=5)
            
            # Customize appearance
            ax.set_xlim(0, time_axis[-1])
            ax.set_ylim(-1.1, 1.1)
            
            if config.show_grid:
                ax.grid(True, color=config.grid_color, alpha=0.3)
            
            if config.show_timecode:
                ax.set_xlabel('Time (seconds)', color=config.text_color)
            
            if config.show_levels:
                ax.set_ylabel('Amplitude', color=config.text_color)
                # Add level markers
                for level in [-1, -0.5, 0, 0.5, 1]:
                    ax.axhline(y=level, color=config.grid_color, alpha=0.5, linewidth=0.5)
            
            # Styling
            ax.tick_params(colors=config.text_color)
            ax.spines['bottom'].set_color(config.text_color)
            ax.spines['top'].set_color(config.text_color)
            ax.spines['right'].set_color(config.text_color)
            ax.spines['left'].set_color(config.text_color)
            
            # Save to bytes
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', facecolor=config.background_color, 
                       bbox_inches='tight', dpi=100)
            buffer.seek(0)
            
            # Convert to array
            img = Image.open(buffer)
            img_array = np.array(img)
            
            # Create base64 encoding
            base64_str = base64.b64encode(buffer.getvalue()).decode()
            
            plt.close(fig)
            
            # Generate metadata
            metadata = {
                'duration': len(audio_section) / self.sample_rate,
                'peak_amplitude': float(np.max(np.abs(audio_section))),
                'rms_amplitude': float(np.sqrt(np.mean(audio_section**2))),
                'crest_factor': float(np.max(np.abs(audio_section)) / (np.sqrt(np.mean(audio_section**2)) + 1e-10)),
                'zero_crossings': int(np.sum(np.diff(np.sign(audio_section)) != 0)),
                'config': config.__dict__
            }
            
            result = VisualizationResult(
                image_data=img_array,
                metadata=metadata,
                base64_image=f"data:image/png;base64,{base64_str}"
            )
            
            self.logger.info("Professional waveform generation completed")
            return result
            
        except Exception as e:
            self.logger.error(f"Waveform generation failed: {e}")
            raise
    
    async def generate_professional_spectrogram(self, 
                                              audio_data: np.ndarray,
                                              config: SpectrogramConfig = None) -> VisualizationResult:
        """Generate professional-quality spectrogram visualization.
        
        Args:
            audio_data: Input audio signal
            config: Spectrogram configuration
            
        Returns:
            Visualization result with image and metadata
        """
        if config is None:
            config = SpectrogramConfig()
        
        try:
            self.logger.info("Generating professional spectrogram...")
            
            # Prepare audio data
            if len(audio_data.shape) > 1:
                # Convert stereo to mono for spectrogram
                audio_mono = np.mean(audio_data, axis=0)
            else:
                audio_mono = audio_data
            
            # Generate spectrogram based on mode
            if config.mode == SpectrogramMode.LINEAR:
                S = librosa.stft(audio_mono, n_fft=config.fft_size, hop_length=config.hop_length, window=config.window_type)
                S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)
                frequencies = librosa.fft_frequencies(sr=self.sample_rate, n_fft=config.fft_size)
                
            elif config.mode == SpectrogramMode.LOG:
                S = librosa.stft(audio_mono, n_fft=config.fft_size, hop_length=config.hop_length, window=config.window_type)
                S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)
                frequencies = librosa.fft_frequencies(sr=self.sample_rate, n_fft=config.fft_size)
                
            elif config.mode == SpectrogramMode.MEL:
                S = librosa.feature.melspectrogram(
                    y=audio_mono, sr=self.sample_rate, n_fft=config.fft_size, 
                    hop_length=config.hop_length, n_mels=config.mel_bins,
                    fmin=config.freq_min, fmax=config.freq_max
                )
                S_db = librosa.power_to_db(S, ref=np.max)
                frequencies = librosa.mel_frequencies(n_mels=config.mel_bins, fmin=config.freq_min, fmax=config.freq_max)
                
            elif config.mode == SpectrogramMode.CHROMA:
                S = librosa.feature.chroma_stft(
                    y=audio_mono, sr=self.sample_rate, n_fft=config.fft_size,
                    hop_length=config.hop_length, n_chroma=config.chroma_bins
                )
                S_db = S  # Chroma is already normalized
                frequencies = np.arange(config.chroma_bins)
                
            elif config.mode == SpectrogramMode.CONSTANT_Q:
                S = librosa.cqt(audio_mono, sr=self.sample_rate, hop_length=config.hop_length,
                               fmin=config.freq_min, n_bins=128)
                S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)
                frequencies = librosa.cqt_frequencies(n_bins=128, fmin=config.freq_min)
            
            # Create time axis
            times = librosa.frames_to_time(np.arange(S_db.shape[1]), sr=self.sample_rate, hop_length=config.hop_length)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(config.width/100, config.height/100), dpi=100)
            
            # Select color scheme
            colormap = self._create_colormap(config.color_scheme)
            
            # Plot spectrogram
            if config.mode in [SpectrogramMode.LINEAR, SpectrogramMode.LOG]:
                # Frequency masking
                freq_mask = (frequencies >= config.freq_min) & (frequencies <= config.freq_max)
                S_db_masked = S_db[freq_mask]
                frequencies_masked = frequencies[freq_mask]
                
                im = ax.imshow(S_db_masked, aspect='auto', origin='lower', 
                              cmap=colormap, vmin=config.db_min, vmax=config.db_max,
                              extent=[times[0], times[-1], frequencies_masked[0], frequencies_masked[-1]])
            else:
                im = ax.imshow(S_db, aspect='auto', origin='lower', cmap=colormap,
                              extent=[times[0], times[-1], 0, len(frequencies)])
            
            # Customize appearance
            if config.show_frequency_labels:
                if config.mode == SpectrogramMode.CHROMA:
                    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                    ax.set_yticks(range(config.chroma_bins))
                    ax.set_yticklabels(note_names)
                    ax.set_ylabel('Pitch Class')
                else:
                    ax.set_ylabel('Frequency (Hz)')
                    
                    # Log scale for better visualization
                    if config.mode in [SpectrogramMode.LINEAR, SpectrogramMode.LOG]:
                        ax.set_yscale('log')
                        ax.set_ylim(config.freq_min, config.freq_max)
            
            if config.show_time_labels:
                ax.set_xlabel('Time (seconds)')
            
            # Add colorbar
            if config.show_colorbar and config.mode != SpectrogramMode.CHROMA:
                cbar = plt.colorbar(im, ax=ax)
                cbar.set_label('Magnitude (dB)', rotation=270, labelpad=15)
            
            # Professional styling
            ax.grid(True, alpha=0.3)
            
            # Save to bytes
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100, facecolor='white')
            buffer.seek(0)
            
            # Convert to array
            img = Image.open(buffer)
            img_array = np.array(img)
            
            # Create base64 encoding
            base64_str = base64.b64encode(buffer.getvalue()).decode()
            
            plt.close(fig)
            
            # Generate advanced analysis
            analysis_data = await self._analyze_spectrogram(S_db, frequencies, times)
            
            # Generate metadata
            metadata = {
                'duration': times[-1],
                'frequency_range': [float(np.min(frequencies)), float(np.max(frequencies))],
                'time_resolution': float(config.hop_length / self.sample_rate),
                'frequency_resolution': float(self.sample_rate / config.fft_size),
                'dynamic_range': float(np.max(S_db) - np.min(S_db)),
                'spectral_centroid': float(np.mean(frequencies)),
                'mode': config.mode.value,
                'config': config.__dict__
            }
            
            result = VisualizationResult(
                image_data=img_array,
                metadata=metadata,
                base64_image=f"data:image/png;base64,{base64_str}",
                analysis_data=analysis_data
            )
            
            self.logger.info("Professional spectrogram generation completed")
            return result
            
        except Exception as e:
            self.logger.error(f"Spectrogram generation failed: {e}")
            raise
    
    def _create_colormap(self, scheme: ColorScheme) -> LinearSegmentedColormap:
        """Create custom colormap for professional visualization."""
        colors = self.color_schemes[scheme]['colors']
        name = self.color_schemes[scheme]['name']
        
        return LinearSegmentedColormap.from_list(name, colors, N=256)
    
    async def _analyze_spectrogram(self, S_db: np.ndarray, frequencies: np.ndarray, times: np.ndarray) -> Dict[str, Any]:
        """Perform advanced spectrogram analysis."""
        try:
            analysis = {}
            
            # Spectral features over time
            analysis['spectral_centroid_curve'] = []
            analysis['spectral_bandwidth_curve'] = []
            analysis['spectral_rolloff_curve'] = []
            
            for t_idx in range(S_db.shape[1]):
                frame = S_db[:, t_idx]
                
                # Spectral centroid
                centroid = np.sum(frequencies * frame) / (np.sum(frame) + 1e-10)
                analysis['spectral_centroid_curve'].append(float(centroid))
                
                # Spectral bandwidth
                deviation = np.sqrt(np.sum(((frequencies - centroid) ** 2) * frame) / (np.sum(frame) + 1e-10))
                analysis['spectral_bandwidth_curve'].append(float(deviation))
                
                # Spectral rolloff (85% of energy)
                cumsum = np.cumsum(frame)
                rolloff_idx = np.where(cumsum >= 0.85 * cumsum[-1])[0]
                rolloff = frequencies[rolloff_idx[0]] if len(rolloff_idx) > 0 else frequencies[-1]
                analysis['spectral_rolloff_curve'].append(float(rolloff))
            
            # Overall statistics
            analysis['mean_spectral_centroid'] = float(np.mean(analysis['spectral_centroid_curve']))
            analysis['mean_spectral_bandwidth'] = float(np.mean(analysis['spectral_bandwidth_curve']))
            analysis['mean_spectral_rolloff'] = float(np.mean(analysis['spectral_rolloff_curve']))
            
            # Frequency band energy distribution
            total_energy = np.sum(S_db)
            
            # Define frequency bands
            bands = {
                'sub_bass': (20, 60),
                'bass': (60, 250),
                'low_mid': (250, 1000),
                'mid': (1000, 4000),
                'high_mid': (4000, 8000),
                'treble': (8000, 20000)
            }
            
            analysis['frequency_bands'] = {}
            for band_name, (low, high) in bands.items():
                mask = (frequencies >= low) & (frequencies <= high)
                if np.any(mask):
                    band_energy = np.sum(S_db[mask])
                    analysis['frequency_bands'][band_name] = float(band_energy / total_energy)
                else:
                    analysis['frequency_bands'][band_name] = 0.0
            
            # Detect harmonic content
            analysis['harmonic_ratio'] = await self._detect_harmonic_content(S_db, frequencies)
            
            # Detect noise floor
            analysis['noise_floor'] = float(np.percentile(S_db, 10))
            
            # Dynamic range
            analysis['dynamic_range'] = float(np.max(S_db) - analysis['noise_floor'])
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Spectrogram analysis failed: {e}")
            return {}
    
    async def _detect_harmonic_content(self, S_db: np.ndarray, frequencies: np.ndarray) -> float:
        """Detect harmonic vs. inharmonic content ratio."""
        try:
            # Simplified harmonic detection
            # Look for peaks that are harmonically related
            
            harmonic_energy = 0.0
            total_energy = np.sum(S_db)
            
            # Average spectrum
            avg_spectrum = np.mean(S_db, axis=1)
            
            # Find peaks
            peaks, _ = scipy.signal.find_peaks(avg_spectrum, height=np.max(avg_spectrum) * 0.1)
            
            if len(peaks) > 1:
                # Check for harmonic relationships
                fundamental_candidates = peaks[:5]  # Top 5 peaks
                
                for fundamental_idx in fundamental_candidates:
                    fundamental_freq = frequencies[fundamental_idx]
                    harmonic_strength = avg_spectrum[fundamental_idx]
                    
                    # Check for harmonics (2f, 3f, 4f, etc.)
                    for harmonic_num in range(2, 6):
                        harmonic_freq = fundamental_freq * harmonic_num
                        
                        # Find closest frequency bin
                        closest_idx = np.argmin(np.abs(frequencies - harmonic_freq))
                        
                        if frequencies[closest_idx] <= frequencies[-1]:
                            harmonic_strength += avg_spectrum[closest_idx] * (0.8 ** (harmonic_num - 1))
                    
                    harmonic_energy = max(harmonic_energy, harmonic_strength)
            
            harmonic_ratio = harmonic_energy / (total_energy + 1e-10)
            return min(1.0, harmonic_ratio)
            
        except:
            return 0.0
    
    async def generate_combined_visualization(self, 
                                            audio_data: np.ndarray,
                                            waveform_config: WaveformConfig = None,
                                            spectrogram_config: SpectrogramConfig = None) -> VisualizationResult:
        """Generate combined waveform and spectrogram visualization.
        
        Args:
            audio_data: Input audio signal
            waveform_config: Waveform configuration
            spectrogram_config: Spectrogram configuration
            
        Returns:
            Combined visualization result
        """
        try:
            self.logger.info("Generating combined visualization...")
            
            # Generate individual visualizations
            waveform_result = await self.generate_professional_waveform(audio_data, waveform_config)
            spectrogram_result = await self.generate_professional_spectrogram(audio_data, spectrogram_config)
            
            # Create combined figure
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(19.2, 14.4), dpi=100)
            
            # Display waveform
            ax1.imshow(waveform_result.image_data)
            ax1.set_title('Waveform', color='white', fontsize=14, pad=20)
            ax1.axis('off')
            
            # Display spectrogram
            ax2.imshow(spectrogram_result.image_data)
            ax2.set_title('Spectrogram', color='white', fontsize=14, pad=20)
            ax2.axis('off')
            
            # Set background
            fig.patch.set_facecolor('#1a1a1a')
            
            # Adjust layout
            plt.tight_layout()
            
            # Save to bytes
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', facecolor='#1a1a1a', bbox_inches='tight', dpi=100)
            buffer.seek(0)
            
            # Convert to array
            img = Image.open(buffer)
            img_array = np.array(img)
            
            # Create base64 encoding
            base64_str = base64.b64encode(buffer.getvalue()).decode()
            
            plt.close(fig)
            
            # Combine metadata
            combined_metadata = {
                'waveform': waveform_result.metadata,
                'spectrogram': spectrogram_result.metadata,
                'combined': True
            }
            
            # Combine analysis data
            combined_analysis = {
                'waveform_analysis': {},
                'spectrogram_analysis': spectrogram_result.analysis_data or {}
            }
            
            result = VisualizationResult(
                image_data=img_array,
                metadata=combined_metadata,
                base64_image=f"data:image/png;base64,{base64_str}",
                analysis_data=combined_analysis
            )
            
            self.logger.info("Combined visualization generation completed")
            return result
            
        except Exception as e:
            self.logger.error(f"Combined visualization generation failed: {e}")
            raise
    
    async def save_visualization(self, result: VisualizationResult, output_path: str) -> str:
        """Save visualization result to file.
        
        Args:
            result: Visualization result to save
            output_path: Output file path
            
        Returns:
            Saved file path
        """
        try:
            # Convert base64 to image
            img_data = base64.b64decode(result.base64_image.split(',')[1])
            
            # Save to file
            with open(output_path, 'wb') as f:
                f.write(img_data)
            
            self.logger.info(f"Visualization saved to: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to save visualization: {e}")
            raise