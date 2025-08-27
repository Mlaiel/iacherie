"""
🎵 Audio Processing Core Module - Professional Audio Intelligence Engine

Advanced core components for high-performance audio processing in the IA Influencer Agent platform.
Implements industrial-grade audio analysis, enhancement, and processing capabilities.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from pathlib import Path
import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from sklearn.preprocessing import StandardScaler
import torch
import torchaudio
from dataclasses import dataclass
from abc import ABC, abstractmethod
import psutil
from concurrent.futures import ThreadPoolExecutor
import time

from .config import AudioProcessingConfig

logger = logging.getLogger(__name__)


@dataclass
class AudioMetadata:
    """Comprehensive audio metadata structure"""
    sample_rate: int
    channels: int
    duration: float
    bit_depth: Optional[int] = None
    format: Optional[str] = None
    codec: Optional[str] = None
    bitrate: Optional[int] = None
    file_size: Optional[int] = None
    checksum: Optional[str] = None


@dataclass
class AudioFeatures:
    """Rich audio feature representation"""
    mfcc: np.ndarray
    spectral_centroid: np.ndarray
    spectral_rolloff: np.ndarray
    zero_crossing_rate: np.ndarray
    chroma: np.ndarray
    tempo: float
    spectral_bandwidth: np.ndarray
    rms_energy: np.ndarray
    spectral_contrast: np.ndarray
    tonnetz: np.ndarray
    onset_frames: np.ndarray


@dataclass
class AudioAnalysisResult:
    """Comprehensive audio analysis output"""
    metadata: AudioMetadata
    features: AudioFeatures
    quality_score: float
    predicted_genre: str
    predicted_mood: str
    energy_level: float
    danceability: float
    valence: float
    acousticness: float
    instrumentalness: float
    liveness: float
    speechiness: float
    loudness: float
    key: str
    mode: str
    time_signature: int


class AudioProcessor:
    """
    🎵 Professional Audio Processor
    
    High-performance audio processing engine with advanced capabilities:
    - Multi-format support (WAV, MP3, FLAC, AAC, OGG)
    - Real-time processing with low latency
    - Batch processing with parallel execution
    - Memory-efficient streaming for large files
    - GPU acceleration when available
    """
    
    def __init__(self, config: Optional[AudioProcessingConfig] = None):
        self.config = config or AudioProcessingConfig()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
        self._setup_processing_environment()
        
        logger.info(f"AudioProcessor initialized with device: {self.device}")
    
    def _setup_processing_environment(self):
        """Setup optimal processing environment"""
        if self.device.type == "cuda":
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
        
        # Set optimal thread counts for audio processing
        torch.set_num_threads(min(psutil.cpu_count(), self.config.max_workers))
    
    async def load_audio(self, 
                        file_path: Union[str, Path], 
                        target_sr: Optional[int] = None,
                        mono: bool = True,
                        normalize: bool = True) -> Tuple[np.ndarray, int]:
        """
        Load audio file with advanced preprocessing
        
        Args:
            file_path: Path to audio file
            target_sr: Target sample rate (None = keep original)
            mono: Convert to mono if True
            normalize: Normalize audio to [-1, 1] range
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {file_path}")
            
            # Load with librosa for comprehensive format support
            audio_data, sample_rate = librosa.load(
                str(file_path),
                sr=target_sr,
                mono=mono,
                res_type='soxr_hq'  # High-quality resampling
            )
            
            if normalize:
                # Advanced normalization with headroom
                peak = np.max(np.abs(audio_data))
                if peak > 0:
                    audio_data = audio_data / (peak * 1.1)  # Leave 10% headroom
            
            logger.info(f"Loaded audio: {file_path.name}, SR: {sample_rate}, "
                       f"Duration: {len(audio_data)/sample_rate:.2f}s")
            
            return audio_data, sample_rate
            
        except Exception as e:
            logger.error(f"Failed to load audio {file_path}: {e}")
            raise
    
    async def save_audio(self,
                        audio_data: np.ndarray,
                        sample_rate: int,
                        output_path: Union[str, Path],
                        format: str = "wav",
                        quality: str = "high") -> bool:
        """
        Save audio with optimized quality settings
        
        Args:
            audio_data: Audio samples
            sample_rate: Sample rate
            output_path: Output file path
            format: Output format (wav, mp3, flac, etc.)
            quality: Quality setting (low, medium, high, lossless)
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Quality-based encoding parameters
            quality_settings = {
                "low": {"bitrate": 128, "bit_depth": 16},
                "medium": {"bitrate": 192, "bit_depth": 16}, 
                "high": {"bitrate": 320, "bit_depth": 24},
                "lossless": {"bitrate": None, "bit_depth": 24}
            }
            
            settings = quality_settings.get(quality, quality_settings["high"])
            
            if format.lower() == "wav":
                sf.write(str(output_path), audio_data, sample_rate, 
                        subtype=f'PCM_{settings["bit_depth"]}')
            else:
                # Use torchaudio for other formats
                audio_tensor = torch.from_numpy(audio_data).unsqueeze(0)
                torchaudio.save(str(output_path), audio_tensor, sample_rate)
            
            logger.info(f"Saved audio: {output_path}, Format: {format}, Quality: {quality}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save audio to {output_path}: {e}")
            return False
    
    async def resample_audio(self,
                           audio_data: np.ndarray,
                           original_sr: int,
                           target_sr: int,
                           method: str = "soxr_hq") -> np.ndarray:
        """High-quality audio resampling"""
        if original_sr == target_sr:
            return audio_data
        
        try:
            resampled = librosa.resample(
                audio_data, 
                orig_sr=original_sr, 
                target_sr=target_sr,
                res_type=method
            )
            
            logger.debug(f"Resampled audio: {original_sr}Hz -> {target_sr}Hz")
            return resampled
            
        except Exception as e:
            logger.error(f"Resampling failed: {e}")
            raise
    
    async def trim_silence(self,
                          audio_data: np.ndarray,
                          sample_rate: int,
                          threshold_db: float = -40.0,
                          frame_length: int = 2048) -> np.ndarray:
        """Intelligent silence trimming"""
        try:
            # Convert dB threshold to amplitude
            threshold_amp = librosa.db_to_amplitude(threshold_db)
            
            # Trim silence from beginning and end
            trimmed, _ = librosa.effects.trim(
                audio_data,
                top_db=-threshold_db,
                frame_length=frame_length
            )
            
            trim_amount = len(audio_data) - len(trimmed)
            logger.debug(f"Trimmed {trim_amount/sample_rate:.2f}s of silence")
            
            return trimmed
            
        except Exception as e:
            logger.error(f"Silence trimming failed: {e}")
            return audio_data


class AudioAnalyzer:
    """
    🔍 Advanced Audio Analyzer
    
    Comprehensive audio analysis engine providing:
    - Spectral analysis and feature extraction
    - Music information retrieval features
    - Audio quality assessment
    - Genre and mood prediction
    - Tempo and key detection
    """
    
    def __init__(self, config: Optional[AudioProcessingConfig] = None):
        self.config = config or AudioProcessingConfig()
        self.scaler = StandardScaler()
        
    async def extract_features(self,
                             audio_data: np.ndarray,
                             sample_rate: int) -> AudioFeatures:
        """Extract comprehensive audio features"""
        try:
            # Basic spectral features
            mfcc = librosa.feature.mfcc(
                y=audio_data, 
                sr=sample_rate, 
                n_mfcc=13,
                hop_length=512
            )
            
            spectral_centroid = librosa.feature.spectral_centroid(
                y=audio_data, 
                sr=sample_rate
            )
            
            spectral_rolloff = librosa.feature.spectral_rolloff(
                y=audio_data, 
                sr=sample_rate
            )
            
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
            
            # Harmonic features
            chroma = librosa.feature.chroma_stft(
                y=audio_data, 
                sr=sample_rate
            )
            
            # Rhythm features
            tempo, _ = librosa.beat.beat_track(
                y=audio_data, 
                sr=sample_rate
            )
            
            # Advanced spectral features
            spectral_bandwidth = librosa.feature.spectral_bandwidth(
                y=audio_data, 
                sr=sample_rate
            )
            
            rms_energy = librosa.feature.rms(y=audio_data)
            
            spectral_contrast = librosa.feature.spectral_contrast(
                y=audio_data, 
                sr=sample_rate
            )
            
            tonnetz = librosa.feature.tonnetz(
                y=audio_data, 
                sr=sample_rate
            )
            
            onset_frames = librosa.onset.onset_detect(
                y=audio_data,
                sr=sample_rate,
                units='frames'
            )
            
            return AudioFeatures(
                mfcc=mfcc,
                spectral_centroid=spectral_centroid,
                spectral_rolloff=spectral_rolloff,
                zero_crossing_rate=zero_crossing_rate,
                chroma=chroma,
                tempo=float(tempo),
                spectral_bandwidth=spectral_bandwidth,
                rms_energy=rms_energy,
                spectral_contrast=spectral_contrast,
                tonnetz=tonnetz,
                onset_frames=onset_frames
            )
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            raise
    
    async def analyze_audio_comprehensive(self,
                                        audio_data: np.ndarray,
                                        sample_rate: int,
                                        file_path: Optional[Path] = None) -> AudioAnalysisResult:
        """Perform comprehensive audio analysis"""
        try:
            # Extract features
            features = await self.extract_features(audio_data, sample_rate)
            
            # Create metadata
            metadata = AudioMetadata(
                sample_rate=sample_rate,
                channels=1 if audio_data.ndim == 1 else audio_data.shape[0],
                duration=len(audio_data) / sample_rate,
                file_size=file_path.stat().st_size if file_path else None
            )
            
            # Calculate advanced audio properties
            quality_score = self._calculate_quality_score(audio_data, sample_rate)
            
            # Predict musical characteristics
            genre = self._predict_genre(features)
            mood = self._predict_mood(features)
            
            # Calculate Spotify-like features
            energy_level = self._calculate_energy(features)
            danceability = self._calculate_danceability(features)
            valence = self._calculate_valence(features)
            acousticness = self._calculate_acousticness(features)
            instrumentalness = self._calculate_instrumentalness(features)
            liveness = self._calculate_liveness(features)
            speechiness = self._calculate_speechiness(features)
            loudness = self._calculate_loudness(audio_data)
            
            # Music theory analysis
            key, mode = self._analyze_key_mode(features.chroma)
            time_signature = self._detect_time_signature(audio_data, sample_rate)
            
            return AudioAnalysisResult(
                metadata=metadata,
                features=features,
                quality_score=quality_score,
                predicted_genre=genre,
                predicted_mood=mood,
                energy_level=energy_level,
                danceability=danceability,
                valence=valence,
                acousticness=acousticness,
                instrumentalness=instrumentalness,
                liveness=liveness,
                speechiness=speechiness,
                loudness=loudness,
                key=key,
                mode=mode,
                time_signature=time_signature
            )
            
        except Exception as e:
            logger.error(f"Comprehensive audio analysis failed: {e}")
            raise
    
    def _calculate_quality_score(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate audio quality score (0-100)"""
        try:
            # SNR estimation
            signal_power = np.mean(audio_data ** 2)
            noise_floor = np.percentile(np.abs(audio_data), 5) ** 2
            snr = 10 * np.log10(signal_power / (noise_floor + 1e-10))
            
            # Dynamic range
            dynamic_range = 20 * np.log10(np.max(np.abs(audio_data)) / 
                                        (np.percentile(np.abs(audio_data), 10) + 1e-10))
            
            # Clipping detection
            clipping_ratio = np.sum(np.abs(audio_data) > 0.99) / len(audio_data)
            
            # Sample rate quality factor
            sr_factor = min(1.0, sample_rate / 44100)
            
            # Combine metrics
            quality = (
                (snr / 60) * 0.4 +  # SNR contribution
                (dynamic_range / 60) * 0.3 +  # Dynamic range
                (1 - clipping_ratio) * 0.2 +  # No clipping bonus
                sr_factor * 0.1  # Sample rate factor
            ) * 100
            
            return max(0, min(100, quality))
            
        except Exception:
            return 50.0  # Default quality score
    
    def _predict_genre(self, features: AudioFeatures) -> str:
        """Predict musical genre based on features"""
        # Simplified genre prediction based on feature analysis
        mean_mfcc = np.mean(features.mfcc, axis=1)
        spectral_centroid_mean = np.mean(features.spectral_centroid)
        tempo = features.tempo
        
        # Simple rule-based classification (in production, use trained ML model)
        if tempo > 120 and spectral_centroid_mean > 2000:
            if np.mean(mean_mfcc[:3]) > 0:
                return "Electronic"
            else:
                return "Pop"
        elif tempo < 80:
            return "Ambient"
        elif spectral_centroid_mean < 1500:
            return "Classical"
        else:
            return "Rock"
    
    def _predict_mood(self, features: AudioFeatures) -> str:
        """Predict emotional mood from audio features"""
        energy = np.mean(features.rms_energy)
        valence_proxy = np.mean(features.chroma)
        tempo = features.tempo
        
        if energy > 0.1 and tempo > 120:
            return "Energetic"
        elif valence_proxy > 0.5 and tempo > 100:
            return "Happy"
        elif energy < 0.05 and tempo < 80:
            return "Calm"
        elif valence_proxy < 0.3:
            return "Melancholic"
        else:
            return "Neutral"
    
    def _calculate_energy(self, features: AudioFeatures) -> float:
        """Calculate energy level (0-1)"""
        rms_mean = np.mean(features.rms_energy)
        spectral_centroid_mean = np.mean(features.spectral_centroid)
        return min(1.0, (rms_mean * 10 + spectral_centroid_mean / 5000) / 2)
    
    def _calculate_danceability(self, features: AudioFeatures) -> float:
        """Calculate danceability score (0-1)"""
        tempo_factor = 1.0 if 90 <= features.tempo <= 140 else 0.5
        rhythm_regularity = 1.0 - np.std(np.diff(features.onset_frames)) / 100
        return min(1.0, tempo_factor * rhythm_regularity)
    
    def _calculate_valence(self, features: AudioFeatures) -> float:
        """Calculate musical valence/positivity (0-1)"""
        chroma_brightness = np.mean(features.chroma[:7])  # Major scale notes
        spectral_rolloff_mean = np.mean(features.spectral_rolloff)
        return min(1.0, (chroma_brightness + spectral_rolloff_mean / 5000) / 2)
    
    def _calculate_acousticness(self, features: AudioFeatures) -> float:
        """Calculate acousticness score (0-1)"""
        spectral_contrast_var = np.var(features.spectral_contrast)
        return max(0.0, 1.0 - spectral_contrast_var / 10)
    
    def _calculate_instrumentalness(self, features: AudioFeatures) -> float:
        """Calculate instrumentalness score (0-1)"""
        mfcc_variance = np.var(features.mfcc)
        return min(1.0, mfcc_variance / 50)
    
    def _calculate_liveness(self, features: AudioFeatures) -> float:
        """Calculate liveness score (0-1)"""
        spectral_bandwidth_var = np.var(features.spectral_bandwidth)
        return min(1.0, spectral_bandwidth_var / 1000000)
    
    def _calculate_speechiness(self, features: AudioFeatures) -> float:
        """Calculate speechiness score (0-1)"""
        zcr_mean = np.mean(features.zero_crossing_rate)
        return min(1.0, zcr_mean * 20)
    
    def _calculate_loudness(self, audio_data: np.ndarray) -> float:
        """Calculate loudness in dB"""
        rms = np.sqrt(np.mean(audio_data ** 2))
        return 20 * np.log10(rms + 1e-10)
    
    def _analyze_key_mode(self, chroma: np.ndarray) -> Tuple[str, str]:
        """Analyze musical key and mode"""
        chroma_mean = np.mean(chroma, axis=1)
        key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Find dominant pitch class
        key_idx = np.argmax(chroma_mean)
        key = key_names[key_idx]
        
        # Simple major/minor detection
        major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
        minor_profile = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])
        
        major_correlation = np.corrcoef(chroma_mean, major_profile)[0, 1]
        minor_correlation = np.corrcoef(chroma_mean, minor_profile)[0, 1]
        
        mode = "major" if major_correlation > minor_correlation else "minor"
        
        return key, mode
    
    def _detect_time_signature(self, audio_data: np.ndarray, sample_rate: int) -> int:
        """Detect time signature"""
        try:
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            beat_intervals = np.diff(beats)
            
            # Simple heuristic for time signature detection
            if np.mean(beat_intervals) > sample_rate * 0.6:  # Slow beats
                return 4  # Assume 4/4
            else:
                return 4  # Default to 4/4
                
        except Exception:
            return 4  # Default


class AudioEnhancer:
    """
    ✨ Professional Audio Enhancer
    
    Advanced audio enhancement capabilities:
    - Noise reduction and restoration
    - Dynamic range optimization
    - Spectral enhancement
    - Mastering-grade processing
    - Real-time enhancement
    """
    
    def __init__(self, config: Optional[AudioProcessingConfig] = None):
        self.config = config or AudioProcessingConfig()
    
    async def denoise_audio(self,
                          audio_data: np.ndarray,
                          sample_rate: int,
                          noise_floor_db: float = -40.0) -> np.ndarray:
        """Advanced noise reduction using spectral gating"""
        try:
            # Convert to frequency domain
            stft = librosa.stft(audio_data, hop_length=512)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise floor
            noise_threshold = librosa.db_to_amplitude(noise_floor_db)
            
            # Create spectral gate
            gate = magnitude > noise_threshold
            
            # Apply soft gating to avoid artifacts
            soft_gate = np.where(gate, 1.0, magnitude / noise_threshold * 0.1)
            
            # Apply enhancement
            enhanced_magnitude = magnitude * soft_gate
            
            # Reconstruct audio
            enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
            enhanced_audio = librosa.istft(enhanced_stft, hop_length=512)
            
            logger.debug("Applied noise reduction")
            return enhanced_audio
            
        except Exception as e:
            logger.error(f"Noise reduction failed: {e}")
            return audio_data
    
    async def normalize_loudness(self,
                               audio_data: np.ndarray,
                               target_lufs: float = -23.0) -> np.ndarray:
        """Normalize audio to target loudness (LUFS)"""
        try:
            # Calculate current RMS (approximation of LUFS)
            current_rms = np.sqrt(np.mean(audio_data ** 2))
            current_db = 20 * np.log10(current_rms + 1e-10)
            
            # Calculate gain needed
            gain_db = target_lufs - current_db
            gain_linear = 10 ** (gain_db / 20)
            
            # Apply gain with limiting
            normalized = audio_data * gain_linear
            
            # Soft limiting to prevent clipping
            peak = np.max(np.abs(normalized))
            if peak > 0.95:
                normalized = normalized / peak * 0.95
            
            logger.debug(f"Normalized loudness: {gain_db:.1f}dB gain applied")
            return normalized
            
        except Exception as e:
            logger.error(f"Loudness normalization failed: {e}")
            return audio_data
    
    async def enhance_clarity(self,
                            audio_data: np.ndarray,
                            sample_rate: int,
                            enhancement_factor: float = 1.5) -> np.ndarray:
        """Enhance audio clarity and presence"""
        try:
            # Apply subtle high-frequency enhancement
            nyquist = sample_rate // 2
            high_freq = 5000  # 5kHz and above
            
            # Design high-shelf filter
            b, a = signal.iirfilter(
                2, high_freq / nyquist, 
                btype='high', 
                ftype='butter',
                output='ba'
            )
            
            # Apply enhancement
            enhanced = signal.filtfilt(b, a, audio_data)
            enhanced = enhanced * enhancement_factor
            
            # Blend with original
            result = 0.7 * audio_data + 0.3 * enhanced
            
            logger.debug("Applied clarity enhancement")
            return result
            
        except Exception as e:
            logger.error(f"Clarity enhancement failed: {e}")
            return audio_data
    
    async def apply_compression(self,
                              audio_data: np.ndarray,
                              threshold: float = 0.5,
                              ratio: float = 4.0,
                              attack_ms: float = 10.0,
                              release_ms: float = 100.0,
                              sample_rate: int = 44100) -> np.ndarray:
        """Apply dynamic range compression"""
        try:
            # Convert time constants to samples
            attack_samples = int(attack_ms * sample_rate / 1000)
            release_samples = int(release_ms * sample_rate / 1000)
            
            # Initialize variables
            envelope = 0.0
            compressed = np.zeros_like(audio_data)
            
            for i, sample in enumerate(audio_data):
                # Envelope following
                sample_abs = abs(sample)
                if sample_abs > envelope:
                    envelope += (sample_abs - envelope) / attack_samples
                else:
                    envelope += (sample_abs - envelope) / release_samples
                
                # Compression
                if envelope > threshold:
                    reduction = threshold + (envelope - threshold) / ratio
                    gain = reduction / (envelope + 1e-10)
                else:
                    gain = 1.0
                
                compressed[i] = sample * gain
            
            logger.debug(f"Applied compression: {ratio}:1 ratio at {threshold:.2f} threshold")
            return compressed
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            return audio_data
