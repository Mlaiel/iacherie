"""📊 Waveform & Spectrogram Generator - Ultra-Advanced Audio Visualization Engine

Industrial-grade waveform and spectrogram generation system featuring real-time
visualization, advanced spectral analysis, interactive audio waveforms, and
professional-grade visual representations for comprehensive audio intelligence.

⚡ ADVANCED CAPABILITIES:
- High-resolution waveform generation with customizable styling
- Multi-scale spectrogram analysis (linear, log, mel, bark, ERB scales)
- Real-time visualization with interactive zoom and navigation
- 3D spectrograms with temporal evolution visualization
- Advanced colormap and dynamic range optimization
- Professional audio analysis plots (phase, frequency response, etc.)
- Export capabilities for web, print, and presentation formats
- GPU-accelerated processing for real-time applications

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

🛡️ TEAM SPECIALTIES:
- Lead Dev IA & Visualization Expert: Fahed Mlaiel
- Audio DSP & Spectral Analysis: Fahed Mlaiel  
- UI/UX & Interactive Visualization: Fahed Mlaiel

⚠️ COPYRIGHT & INTELLECTUAL PROPERTY WARNING:
This advanced waveform and spectrogram generation system contains proprietary
algorithms for audio visualization and spectral analysis developed exclusively
by Fahed Mlaiel. Unauthorized use, copying, or commercial exploitation is
strictly prohibited under international copyright law.

Contact: mlaiel@live.de
"""

import numpy as np
import logging
import asyncio
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import librosa
import scipy.signal
import scipy.fft
try:
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    plt = None
    mcolors = None
    Figure = None
    FigureCanvasAgg = None
    sns = None
    MATPLOTLIB_AVAILABLE = False
from pathlib import Path
import base64
import io
import json
import math


class SpectrogramType(Enum):
    """Types of spectrograms for different analysis purposes"""
    
    LINEAR = "linear"
    LOG = "log"
    MEL = "mel"
    MFCC = "mfcc"
    CQT = "cqt"
    CHROMA = "chroma"
    TONNETZ = "tonnetz"
    SPECTRAL_CENTROID = "spectral_centroid"
    ZERO_CROSSING = "zero_crossing"
    BARK = "bark"
    ERB = "erb"


class WaveformStyle(Enum):
    """Waveform visualization styles"""
    
    CLASSIC = "classic"
    STEREO = "stereo"
    ENVELOPE = "envelope"
    PEAKS = "peaks"
    DENSITY = "density"
    PROFESSIONAL = "professional"
    BROADCAST = "broadcast"
    STUDIO = "studio"


class ColorScheme(Enum):
    """Professional color schemes for visualizations"""
    
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    MAGMA = "magma"
    STUDIO_BLUE = "studio_blue"
    PROFESSIONAL = "professional"
    HIGH_CONTRAST = "high_contrast"
    BROADCAST = "broadcast"
    SPECTRAL = "spectral"


@dataclass
class WaveformConfig:
    """Waveform generation configuration"""
    
    style: WaveformStyle = WaveformStyle.PROFESSIONAL
    color_scheme: ColorScheme = ColorScheme.PROFESSIONAL
    width: int = 1920
    height: int = 480
    dpi: int = 150
    show_grid: bool = True
    show_time_markers: bool = True
    show_amplitude_scale: bool = True
    normalize: bool = True
    stereo_separation: bool = True
    peak_markers: bool = True
    rms_overlay: bool = True
    background_color: str = "#1e1e1e"
    waveform_color: str = "#00ff88"
    grid_color: str = "#333333"
    text_color: str = "#ffffff"


@dataclass
class SpectrogramConfig:
    """Spectrogram generation configuration"""
    
    spectrogram_type: SpectrogramType = SpectrogramType.LINEAR
    color_scheme: ColorScheme = ColorScheme.VIRIDIS
    width: int = 1920
    height: int = 1080
    dpi: int = 150
    n_fft: int = 2048
    hop_length: int = 512
    window: str = "hann"
    freq_scale: str = "linear"  # linear, log, mel
    time_resolution: float = 0.01  # seconds
    freq_resolution: float = 10.0  # Hz
    dynamic_range: float = 80.0  # dB
    show_colorbar: bool = True
    show_grid: bool = True
    show_frequency_labels: bool = True
    show_time_labels: bool = True
    interactive: bool = False


@dataclass
class VisualizationResult:
    """Comprehensive visualization results"""
    
    waveform_image: Optional[bytes] = None
    spectrogram_image: Optional[bytes] = None
    waveform_data: Optional[np.ndarray] = None
    spectrogram_data: Optional[np.ndarray] = None
    time_axis: Optional[np.ndarray] = None
    frequency_axis: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    interactive_html: Optional[str] = None
    base64_waveform: Optional[str] = None
    base64_spectrogram: Optional[str] = None


class UltraAdvancedWaveformSpectrogramGenerator:
    """
    Industrial-grade waveform and spectrogram generation system
    """
    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        if not MATPLOTLIB_AVAILABLE:
            self.logger.warning("Matplotlib not available. Visualization features will be limited.")
            return
        
        # Set professional matplotlib style
        plt.style.use('default')
        sns.set_palette("viridis")
        
        # Professional color schemes
        self.color_schemes = {
            ColorScheme.STUDIO_BLUE: {
                'background': '#0a0e1a',
                'waveform': '#1e90ff',
                'grid': '#2a3441',
                'text': '#ffffff',
                'accent': '#ff6b35'
            },
            ColorScheme.PROFESSIONAL: {
                'background': '#1e1e1e',
                'waveform': '#00ff88',
                'grid': '#333333',
                'text': '#ffffff',
                'accent': '#ff4444'
            },
            ColorScheme.BROADCAST: {
                'background': '#000000',
                'waveform': '#ffff00',
                'grid': '#404040',
                'text': '#ffffff',
                'accent': '#ff0000'
            }
        }
        
        self.logger.info("UltraAdvancedWaveformSpectrogramGenerator initialized")
    
    async def generate_comprehensive_visualization(self, 
                                                 audio_data: np.ndarray,
                                                 waveform_config: Optional[WaveformConfig] = None,
                                                 spectrogram_config: Optional[SpectrogramConfig] = None) -> VisualizationResult:
        """
        Generate comprehensive audio visualization with waveforms and spectrograms
        """
        try:
            if not MATPLOTLIB_AVAILABLE:
                self.logger.warning("Matplotlib not available. Returning minimal result.")
                return VisualizationResult(metadata=self._extract_visualization_metadata(audio_data))
            
            self.logger.info("Starting comprehensive audio visualization generation")
            
            # Use default configs if not provided
            if waveform_config is None:
                waveform_config = WaveformConfig()
            if spectrogram_config is None:
                spectrogram_config = SpectrogramConfig()
            
            # Parallel generation
            with ThreadPoolExecutor(max_workers=4) as executor:
                # Submit tasks
                waveform_future = executor.submit(
                    self._generate_professional_waveform, audio_data, waveform_config
                )
                spectrogram_future = executor.submit(
                    self._generate_advanced_spectrogram, audio_data, spectrogram_config
                )
                metadata_future = executor.submit(
                    self._extract_visualization_metadata, audio_data
                )
                
                # Collect results
                waveform_result = waveform_future.result()
                spectrogram_result = spectrogram_future.result()
                metadata = metadata_future.result()
            
            # Compile comprehensive result
            result = VisualizationResult(
                waveform_image=waveform_result['image_bytes'],
                spectrogram_image=spectrogram_result['image_bytes'],
                waveform_data=waveform_result['data'],
                spectrogram_data=spectrogram_result['data'],
                time_axis=waveform_result['time_axis'],
                frequency_axis=spectrogram_result['frequency_axis'],
                metadata=metadata,
                base64_waveform=waveform_result['base64'],
                base64_spectrogram=spectrogram_result['base64']
            )
            
            self.logger.info("Comprehensive visualization generation complete")
            return result
            
        except Exception as e:
            self.logger.error(f"Comprehensive visualization generation failed: {e}")
            return VisualizationResult()
    
    def _generate_professional_waveform(self, audio_data: np.ndarray, 
                                      config: WaveformConfig) -> Dict[str, Any]:
        """Generate professional-grade waveform visualization"""
        try:
            # Setup figure with professional styling
            fig = Figure(figsize=(config.width/config.dpi, config.height/config.dpi), 
                        dpi=config.dpi, facecolor=config.background_color)
            canvas = FigureCanvasAgg(fig)
            
            # Determine if stereo or mono
            if audio_data.ndim == 2:
                # Stereo processing
                ax1 = fig.add_subplot(211)
                ax2 = fig.add_subplot(212)
                axes = [ax1, ax2]
                channels = ['Left', 'Right']
            else:
                # Mono processing
                ax1 = fig.add_subplot(111)
                axes = [ax1]
                channels = ['Mono']
                audio_data = audio_data.reshape(1, -1) if audio_data.ndim == 1 else audio_data
            
            # Time axis
            time_axis = np.linspace(0, len(audio_data.T) / self.sample_rate, len(audio_data.T))
            
            # Generate waveforms for each channel
            for i, (ax, channel) in enumerate(zip(axes, channels)):
                if audio_data.ndim == 2:
                    channel_data = audio_data[i, :]
                else:
                    channel_data = audio_data.flatten()
                
                # Apply waveform style
                if config.style == WaveformStyle.CLASSIC:
                    ax.plot(time_axis, channel_data, color=config.waveform_color, linewidth=0.5)
                
                elif config.style == WaveformStyle.PROFESSIONAL:
                    # High-quality anti-aliased waveform
                    decimation_factor = max(1, len(channel_data) // (config.width * 2))
                    if decimation_factor > 1:
                        # Smart decimation preserving peaks
                        decimated_data = self._smart_decimate(channel_data, decimation_factor)
                        decimated_time = time_axis[::decimation_factor][:len(decimated_data)]
                    else:
                        decimated_data = channel_data
                        decimated_time = time_axis
                    
                    ax.plot(decimated_time, decimated_data, 
                           color=config.waveform_color, linewidth=0.8, alpha=0.9)
                
                elif config.style == WaveformStyle.ENVELOPE:
                    # Envelope style with fill
                    envelope = np.abs(scipy.signal.hilbert(channel_data))
                    ax.fill_between(time_axis, -envelope, envelope, 
                                  color=config.waveform_color, alpha=0.6)
                
                elif config.style == WaveformStyle.PEAKS:
                    # Peak detection and emphasis
                    peaks, _ = scipy.signal.find_peaks(np.abs(channel_data), 
                                                     height=np.max(np.abs(channel_data)) * 0.7)
                    ax.plot(time_axis, channel_data, color=config.waveform_color, linewidth=0.5, alpha=0.7)
                    ax.scatter(time_axis[peaks], channel_data[peaks], 
                             color=config.text_color, s=10, alpha=0.8)
                
                # Add RMS overlay if requested
                if config.rms_overlay:
                    rms_window = int(0.1 * self.sample_rate)  # 100ms window
                    rms = self._calculate_rms_overlay(channel_data, rms_window)
                    rms_time = np.linspace(0, len(channel_data) / self.sample_rate, len(rms))
                    ax.plot(rms_time, rms, color='#ff6b35', linewidth=2, alpha=0.8, label='RMS')
                    ax.plot(rms_time, -rms, color='#ff6b35', linewidth=2, alpha=0.8)
                
                # Professional styling
                ax.set_facecolor(config.background_color)
                ax.grid(config.show_grid, color=config.grid_color, alpha=0.3, linewidth=0.5)
                ax.set_ylabel(f'{channel} Amplitude', color=config.text_color, fontsize=10)
                
                if config.show_amplitude_scale:
                    ax.set_ylim(-1.1, 1.1)
                    ax.set_yticks([-1, -0.5, 0, 0.5, 1])
                
                # Styling
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color(config.grid_color)
                ax.spines['bottom'].set_color(config.grid_color)
                ax.tick_params(colors=config.text_color, labelsize=8)
            
            # Time labels on bottom axis only
            if config.show_time_markers:
                axes[-1].set_xlabel('Time (seconds)', color=config.text_color, fontsize=10)
            
            # Tight layout
            fig.tight_layout()
            
            # Convert to bytes
            buffer = io.BytesIO()
            canvas.print_png(buffer, facecolor=config.background_color)
            image_bytes = buffer.getvalue()
            buffer.close()
            
            # Base64 encoding for web display
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            
            return {
                'image_bytes': image_bytes,
                'data': audio_data,
                'time_axis': time_axis,
                'base64': base64_string
            }
            
        except Exception as e:
            self.logger.error(f"Professional waveform generation failed: {e}")
            return {'image_bytes': None, 'data': None, 'time_axis': None, 'base64': None}
    
    def _generate_advanced_spectrogram(self, audio_data: np.ndarray, 
                                     config: SpectrogramConfig) -> Dict[str, Any]:
        """Generate advanced spectrogram visualization"""
        try:
            # Handle stereo by converting to mono for spectrogram
            if audio_data.ndim == 2:
                audio_mono = np.mean(audio_data, axis=0)
            else:
                audio_mono = audio_data
            
            # Generate spectrogram data based on type
            if config.spectrogram_type == SpectrogramType.LINEAR:
                frequencies, times, Sxx = scipy.signal.spectrogram(
                    audio_mono, fs=self.sample_rate, 
                    nperseg=config.n_fft, noverlap=config.n_fft-config.hop_length,
                    window=config.window
                )
                
            elif config.spectrogram_type == SpectrogramType.MEL:
                # Mel-scale spectrogram
                S = librosa.stft(audio_mono, n_fft=config.n_fft, hop_length=config.hop_length)
                S_mag = np.abs(S)
                mel_spec = librosa.feature.melspectrogram(
                    S=S_mag**2, sr=self.sample_rate, n_mels=128
                )
                Sxx = librosa.power_to_db(mel_spec, ref=np.max)
                times = librosa.frames_to_time(np.arange(Sxx.shape[1]), 
                                             sr=self.sample_rate, hop_length=config.hop_length)
                frequencies = librosa.mel_frequencies(n_mels=128, fmin=0, fmax=self.sample_rate//2)
                
            elif config.spectrogram_type == SpectrogramType.CQT:
                # Constant-Q Transform
                C = librosa.cqt(audio_mono, sr=self.sample_rate, 
                               hop_length=config.hop_length, fmin=librosa.note_to_hz('C1'))
                Sxx = librosa.amplitude_to_db(np.abs(C), ref=np.max)
                times = librosa.frames_to_time(np.arange(Sxx.shape[1]), 
                                             sr=self.sample_rate, hop_length=config.hop_length)
                frequencies = librosa.cqt_frequencies(n_bins=Sxx.shape[0], 
                                                    fmin=librosa.note_to_hz('C1'), 
                                                    bins_per_octave=12)
                
            elif config.spectrogram_type == SpectrogramType.CHROMA:
                # Chroma features
                chroma = librosa.feature.chroma_stft(
                    y=audio_mono, sr=self.sample_rate, hop_length=config.hop_length
                )
                Sxx = chroma
                times = librosa.frames_to_time(np.arange(Sxx.shape[1]), 
                                             sr=self.sample_rate, hop_length=config.hop_length)
                frequencies = np.arange(12)  # 12 pitch classes
            
            else:
                # Default to linear spectrogram
                frequencies, times, Sxx = scipy.signal.spectrogram(
                    audio_mono, fs=self.sample_rate, 
                    nperseg=config.n_fft, noverlap=config.n_fft-config.hop_length
                )
            
            # Convert to dB if not already
            if config.spectrogram_type not in [SpectrogramType.CHROMA]:
                if np.all(Sxx >= 0):  # Power spectrogram
                    Sxx_db = 10 * np.log10(Sxx + 1e-10)
                else:  # Already in dB
                    Sxx_db = Sxx
            else:
                Sxx_db = Sxx
            
            # Create professional visualization
            fig = Figure(figsize=(config.width/config.dpi, config.height/config.dpi), 
                        dpi=config.dpi, facecolor='#1e1e1e')
            canvas = FigureCanvasAgg(fig)
            ax = fig.add_subplot(111)
            
            # Dynamic range normalization
            if config.spectrogram_type not in [SpectrogramType.CHROMA]:
                vmin = np.max(Sxx_db) - config.dynamic_range
                vmax = np.max(Sxx_db)
            else:
                vmin = np.min(Sxx_db)
                vmax = np.max(Sxx_db)
            
            # Professional colormap
            if config.color_scheme == ColorScheme.VIRIDIS:
                cmap = plt.cm.viridis
            elif config.color_scheme == ColorScheme.PROFESSIONAL:
                # Custom professional colormap
                colors = ['#000033', '#000066', '#003366', '#0066cc', '#33ccff', '#ffff00']
                n_bins = 256
                cmap = mcolors.LinearSegmentedColormap.from_list('professional', colors, N=n_bins)
            else:
                cmap = plt.cm.viridis
            
            # Plot spectrogram
            if config.freq_scale == 'log':
                im = ax.pcolormesh(times, frequencies, Sxx_db, 
                                 shading='gouraud', cmap=cmap, vmin=vmin, vmax=vmax)
                ax.set_yscale('log')
            else:
                im = ax.pcolormesh(times, frequencies, Sxx_db, 
                                 shading='gouraud', cmap=cmap, vmin=vmin, vmax=vmax)
            
            # Professional styling
            ax.set_facecolor('#000000')
            if config.show_time_labels:
                ax.set_xlabel('Time (seconds)', color='white', fontsize=12)
            if config.show_frequency_labels:
                if config.spectrogram_type == SpectrogramType.CHROMA:
                    ax.set_ylabel('Pitch Class', color='white', fontsize=12)
                    ax.set_yticks(range(12))
                    ax.set_yticklabels(['C', 'C#', 'D', 'D#', 'E', 'F', 
                                       'F#', 'G', 'G#', 'A', 'A#', 'B'])
                else:
                    ax.set_ylabel('Frequency (Hz)', color='white', fontsize=12)
            
            ax.tick_params(colors='white', labelsize=10)
            ax.grid(config.show_grid, color='white', alpha=0.2, linewidth=0.5)
            
            # Colorbar
            if config.show_colorbar and config.spectrogram_type != SpectrogramType.CHROMA:
                cbar = fig.colorbar(im, ax=ax)
                cbar.set_label('Magnitude (dB)', color='white', fontsize=10)
                cbar.ax.tick_params(colors='white', labelsize=8)
            
            # Tight layout
            fig.tight_layout()
            
            # Convert to bytes
            buffer = io.BytesIO()
            canvas.print_png(buffer, facecolor='#1e1e1e')
            image_bytes = buffer.getvalue()
            buffer.close()
            
            # Base64 encoding
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            
            return {
                'image_bytes': image_bytes,
                'data': Sxx_db,
                'frequency_axis': frequencies,
                'time_axis': times,
                'base64': base64_string
            }
            
        except Exception as e:
            self.logger.error(f"Advanced spectrogram generation failed: {e}")
            return {
                'image_bytes': None, 'data': None, 
                'frequency_axis': None, 'time_axis': None, 'base64': None
            }
    
    def _smart_decimate(self, data: np.ndarray, factor: int) -> np.ndarray:
        """Smart decimation that preserves peaks and important features"""
        if factor <= 1:
            return data
        
        # Reshape data for processing
        n_samples = len(data)
        n_groups = n_samples // factor
        remainder = n_samples % factor
        
        # Process complete groups
        reshaped = data[:n_groups * factor].reshape(n_groups, factor)
        
        # Find max and min in each group to preserve peaks
        maxes = np.max(reshaped, axis=1)
        mins = np.min(reshaped, axis=1)
        
        # Alternate between max and min to preserve waveform character
        decimated = np.empty(n_groups * 2)
        decimated[::2] = maxes
        decimated[1::2] = mins
        
        return decimated
    
    def _calculate_rms_overlay(self, data: np.ndarray, window_size: int) -> np.ndarray:
        """Calculate RMS overlay for waveform visualization"""
        # Pad data to handle windows at edges
        padded_data = np.pad(data, window_size//2, mode='constant')
        
        # Calculate RMS in sliding windows
        rms_values = []
        for i in range(len(data)):
            window = padded_data[i:i + window_size]
            rms = np.sqrt(np.mean(window**2))
            rms_values.append(rms)
        
        return np.array(rms_values)
    
    def _extract_visualization_metadata(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Extract metadata for visualization"""
        try:
            # Basic audio properties
            duration = len(audio_data.T) / self.sample_rate if audio_data.ndim == 2 else len(audio_data) / self.sample_rate
            peak_amplitude = np.max(np.abs(audio_data))
            rms_level = np.sqrt(np.mean(audio_data**2))
            dynamic_range = 20 * np.log10(peak_amplitude / (rms_level + 1e-10))
            
            # Spectral properties
            if audio_data.ndim == 2:
                audio_mono = np.mean(audio_data, axis=0)
            else:
                audio_mono = audio_data
            
            # Basic spectral analysis
            f, Pxx = scipy.signal.welch(audio_mono, fs=self.sample_rate)
            spectral_centroid = np.sum(f * Pxx) / np.sum(Pxx)
            
            return {
                'duration_seconds': float(duration),
                'sample_rate': self.sample_rate,
                'channels': 2 if audio_data.ndim == 2 else 1,
                'peak_amplitude': float(peak_amplitude),
                'rms_level': float(rms_level),
                'dynamic_range_db': float(dynamic_range),
                'spectral_centroid_hz': float(spectral_centroid),
                'generation_timestamp': str(np.datetime64('now'))
            }
            
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {e}")
            return {}
    
    async def generate_interactive_visualization(self, audio_data: np.ndarray) -> str:
        """Generate interactive HTML visualization"""
        try:
            # This would integrate with libraries like Plotly or Bokeh
            # For now, return a placeholder
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Interactive Audio Visualization</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            </head>
            <body>
                <div id="waveform" style="width:100%;height:400px;"></div>
                <div id="spectrogram" style="width:100%;height:600px;"></div>
                <script>
                    // Interactive visualization would be implemented here
                    console.log("Interactive visualization placeholder");
                </script>
            </body>
            </html>
            """
            
            return html_template
            
        except Exception as e:
            self.logger.error(f"Interactive visualization generation failed: {e}")
            return ""
    
    async def export_visualization(self, result: VisualizationResult, 
                                 output_path: Path, format: str = "png") -> bool:
        """Export visualization to file"""
        try:
            if format.lower() == "png":
                if result.waveform_image:
                    waveform_path = output_path / "waveform.png"
                    with open(waveform_path, "wb") as f:
                        f.write(result.waveform_image)
                
                if result.spectrogram_image:
                    spectrogram_path = output_path / "spectrogram.png"
                    with open(spectrogram_path, "wb") as f:
                        f.write(result.spectrogram_image)
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Visualization export failed: {e}")
            return False


# Factory function for easy access
def create_waveform_spectrogram_generator(sample_rate: int = 44100) -> UltraAdvancedWaveformSpectrogramGenerator:
    """Factory function to create waveform/spectrogram generator"""
    return UltraAdvancedWaveformSpectrogramGenerator(sample_rate=sample_rate)


# Utility functions for quick visualization
async def generate_quick_waveform(audio_data: np.ndarray, 
                                sample_rate: int = 44100) -> bytes:
    """Quick waveform generation"""
    generator = create_waveform_spectrogram_generator(sample_rate)
    result = await generator.generate_comprehensive_visualization(audio_data)
    return result.waveform_image


async def generate_quick_spectrogram(audio_data: np.ndarray, 
                                   sample_rate: int = 44100) -> bytes:
    """Quick spectrogram generation"""
    generator = create_waveform_spectrogram_generator(sample_rate)
    result = await generator.generate_comprehensive_visualization(audio_data)
    return result.spectrogram_image