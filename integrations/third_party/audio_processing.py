"""Audio Processing Services - Comprehensive Audio Processing and Analysis
========================================================================

Advanced audio processing system for the Ainflue platform supporting audio
analysis, enhancement, format conversion, and AI-powered audio generation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import os
import tempfile
from typing import Dict, List, Optional, Any, Union, BinaryIO, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
import hashlib
import base64
from pathlib import Path

import numpy as np
import librosa
import soundfile as sf
import scipy.signal
from scipy.io import wavfile
import aiofiles
import aiohttp

logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    """Supported audio formats."""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    OPUS = "opus"
    WEBM = "webm"


class AudioQuality(Enum):
    """Audio quality presets."""
    LOW = "low"           # 64 kbps
    STANDARD = "standard" # 128 kbps
    HIGH = "high"         # 256 kbps
    PREMIUM = "premium"   # 320 kbps
    LOSSLESS = "lossless" # No compression


class AudioProcessingTask(Enum):
    """Audio processing tasks."""
    NORMALIZE = "normalize"
    ENHANCE = "enhance"
    DENOISE = "denoise"
    CONVERT_FORMAT = "convert_format"
    EXTRACT_FEATURES = "extract_features"
    TRIM = "trim"
    FADE_IN_OUT = "fade_in_out"
    CHANGE_SPEED = "change_speed"
    CHANGE_PITCH = "change_pitch"
    ADD_REVERB = "add_reverb"
    EQUALIZE = "equalize"
    COMPRESS = "compress"
    AMPLIFY = "amplify"
    GENERATE_SPECTROGRAM = "generate_spectrogram"
    DETECT_BEATS = "detect_beats"
    SEPARATE_VOCALS = "separate_vocals"
    TRANSCRIBE = "transcribe"


class MusicGenre(Enum):
    """Music genres for classification."""
    POP = "pop"
    ROCK = "rock"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    ELECTRONIC = "electronic"
    HIP_HOP = "hip_hop"
    COUNTRY = "country"
    REGGAE = "reggae"
    BLUES = "blues"
    FOLK = "folk"
    METAL = "metal"
    AMBIENT = "ambient"
    UNKNOWN = "unknown"


@dataclass
class AudioMetadata:
    """Audio file metadata."""
    duration: float
    sample_rate: int
    channels: int
    bit_depth: int
    format: AudioFormat
    file_size: int
    bitrate: Optional[int] = None
    codec: Optional[str] = None
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None


@dataclass
class AudioFeatures:
    """Extracted audio features."""
    tempo: float
    key: str
    mode: str  # major/minor
    energy: float
    valence: float  # positivity
    danceability: float
    acousticness: float
    instrumentalness: float
    liveness: float
    loudness: float
    speechiness: float
    spectral_centroid: float
    spectral_bandwidth: float
    spectral_rolloff: float
    zero_crossing_rate: float
    mfcc: List[float]
    chroma: List[float]
    tonnetz: List[float]
    onset_times: List[float]
    beat_times: List[float]


@dataclass
class AudioProcessingResult:
    """Audio processing result."""
    task: AudioProcessingTask
    success: bool
    output_path: Optional[str]
    output_data: Optional[bytes]
    metadata: Optional[AudioMetadata]
    features: Optional[AudioFeatures]
    processing_time: float
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VoiceAnalysis:
    """Voice analysis results."""
    is_speech: bool
    confidence: float
    language: Optional[str]
    gender: Optional[str]  # male/female/unknown
    age_range: Optional[str]  # young/adult/senior
    emotion: Optional[str]
    speaker_count: int
    clarity_score: float
    noise_level: float
    transcription: Optional[str] = None


class AudioProcessor:
    """Advanced audio processing engine."""
    
    def __init__(self, temp_dir -> None: Optional[str] = None, max_file_size -> None: int = 100 * 1024 * 1024) -> None:
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.max_file_size = max_file_size  # 100MB default
        
        # Processing parameters
        self.default_sample_rate = 44100
        self.default_channels = 2
        self.chunk_size = 8192
        
        # Feature extraction cache
        self.feature_cache: Dict[str, AudioFeatures] = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Supported formats
        self.supported_formats = {
            AudioFormat.WAV: "wav",
            AudioFormat.MP3: "mp3", 
            AudioFormat.FLAC: "flac",
            AudioFormat.OGG: "ogg"
        }
        
        # Audio effects presets
        self.preset_configs = {
            "voice_enhance": {
                "normalize": True,
                "denoise": True,
                "eq_params": {"low_shelf": -2, "high_shelf": 3, "mid_boost": 2}
            },
            "music_master": {
                "normalize": True,
                "compress": {"threshold": -12, "ratio": 4, "attack": 0.003, "release": 0.1},
                "eq_params": {"low_shelf": 1, "high_shelf": 2}
            },
            "podcast_ready": {
                "normalize": True,
                "denoise": True,
                "compress": {"threshold": -16, "ratio": 3, "attack": 0.005, "release": 0.2},
                "gate": {"threshold": -35, "ratio": 10}
            }
        }
    
    async def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file and return audio data and sample rate."""
        try:
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                raise ValueError(f"File size {file_size} exceeds maximum {self.max_file_size}")
            
            # Load audio using librosa
            audio_data, sample_rate = librosa.load(file_path, sr=None, mono=False)
            
            # Ensure stereo if mono
            if audio_data.ndim == 1:
                audio_data = np.stack([audio_data, audio_data])
            
            logger.debug(f"Loaded audio: {file_path}, SR: {sample_rate}, Shape: {audio_data.shape}")
            return audio_data, sample_rate
            
        except Exception as e:
            logger.error(f"Failed to load audio file {file_path}: {str(e)}")
            raise
    
    async def save_audio(self, audio_data: np.ndarray, sample_rate: int, 
                        output_path: str, format: AudioFormat = AudioFormat.WAV) -> bool:
        """Save audio data to file."""
        try:
            # Ensure audio data is in correct format
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Transpose if needed (librosa uses channels last)
            if audio_data.ndim == 2 and audio_data.shape[0] == 2:
                audio_data = audio_data.T
            
            # Save using soundfile
            sf.write(output_path, audio_data, sample_rate, format=format.value)
            
            logger.debug(f"Saved audio to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save audio to {output_path}: {str(e)}")
            return False
    
    async def get_audio_metadata(self, file_path: str) -> AudioMetadata:
        """Extract comprehensive audio metadata."""
        try:
            # Load basic info
            info = sf.info(file_path)
            file_size = os.path.getsize(file_path)
            
            # Calculate bitrate
            bitrate = None
            if info.duration > 0:
                bitrate = int((file_size * 8) / info.duration)
            
            # Determine format
            format_map = {
                'WAV': AudioFormat.WAV,
                'FLAC': AudioFormat.FLAC,
                'OGG': AudioFormat.OGG,
                'MP3': AudioFormat.MP3
            }
            audio_format = format_map.get(info.format, AudioFormat.WAV)
            
            metadata = AudioMetadata(
                duration=info.duration,
                sample_rate=info.samplerate,
                channels=info.channels,
                bit_depth=32,  # soundfile uses 32-bit float internally
                format=audio_format,
                file_size=file_size,
                bitrate=bitrate,
                codec=info.subtype
            )
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get audio metadata: {str(e)}")
            raise
    
    async def extract_features(self, file_path: str) -> AudioFeatures:
        """Extract comprehensive audio features."""
        try:
            # Check cache
            file_hash = hashlib.md5(file_path.encode()).hexdigest()
            if file_hash in self.feature_cache:
                return self.feature_cache[file_hash]
            
            # Load audio
            y, sr = librosa.load(file_path, sr=self.default_sample_rate)
            
            # Extract features
            features = {}
            
            # Tempo and beat tracking
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beat_frames, sr=sr)
            features['tempo'] = float(tempo)
            features['beat_times'] = beat_times.tolist()
            
            # Onset detection
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            onset_times = librosa.frames_to_time(onset_frames, sr=sr)
            features['onset_times'] = onset_times.tolist()
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            
            features['spectral_centroid'] = float(np.mean(spectral_centroids))
            features['spectral_bandwidth'] = float(np.mean(spectral_bandwidth))
            features['spectral_rolloff'] = float(np.mean(spectral_rolloff))
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            features['zero_crossing_rate'] = float(np.mean(zcr))
            
            # MFCCs
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            features['mfcc'] = np.mean(mfccs, axis=1).tolist()
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            features['chroma'] = np.mean(chroma, axis=1).tolist()
            
            # Tonnetz
            tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr)
            features['tonnetz'] = np.mean(tonnetz, axis=1).tolist()
            
            # Energy and loudness
            rms_energy = librosa.feature.rms(y=y)[0]
            features['energy'] = float(np.mean(rms_energy))
            features['loudness'] = float(20 * np.log10(np.mean(rms_energy) + 1e-6))
            
            # Key detection (simplified)
            chroma_mean = np.mean(chroma, axis=1)
            key_idx = np.argmax(chroma_mean)
            keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            features['key'] = keys[key_idx]
            features['mode'] = 'major'  # Simplified
            
            # High-level features (simplified calculations)
            features['valence'] = float(np.clip((features['energy'] - 0.3) * 2, 0, 1))
            features['danceability'] = float(np.clip(tempo / 140.0, 0, 1))
            features['acousticness'] = float(1.0 - np.clip(features['energy'], 0, 1))
            features['instrumentalness'] = float(1.0 - np.clip(features['zero_crossing_rate'] * 10, 0, 1))
            features['liveness'] = float(np.clip(np.std(rms_energy) * 5, 0, 1))
            features['speechiness'] = float(np.clip(features['zero_crossing_rate'] * 3, 0, 1))
            
            audio_features = AudioFeatures(**features)
            
            # Cache features
            self.feature_cache[file_hash] = audio_features
            
            return audio_features
            
        except Exception as e:
            logger.error(f"Failed to extract audio features: {str(e)}")
            raise
    
    async def normalize_audio(self, audio_data: np.ndarray, target_lufs: float = -23.0) -> np.ndarray:
        """Normalize audio to target LUFS level."""
        try:
            # Calculate current RMS level
            current_rms = np.sqrt(np.mean(audio_data ** 2))
            
            # Convert target LUFS to linear scale (simplified)
            target_linear = 10 ** (target_lufs / 20.0)
            
            # Calculate gain
            if current_rms > 0:
                gain = target_linear / current_rms
                gain = min(gain, 10.0)  # Limit gain to prevent distortion
            else:
                gain = 1.0
            
            # Apply gain
            normalized_audio = audio_data * gain
            
            # Prevent clipping
            max_val = np.max(np.abs(normalized_audio))
            if max_val > 0.95:
                normalized_audio = normalized_audio * (0.95 / max_val)
            
            return normalized_audio.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Failed to normalize audio: {str(e)}")
            return audio_data
    
    async def denoise_audio(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Remove noise from audio using spectral gating."""
        try:
            # Convert to mono for noise analysis
            if audio_data.ndim == 2:
                mono_audio = np.mean(audio_data, axis=0)
            else:
                mono_audio = audio_data
            
            # Compute STFT
            stft = librosa.stft(mono_audio, n_fft=2048, hop_length=512)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise floor (bottom 20% of magnitude)
            noise_floor = np.percentile(magnitude, 20, axis=1, keepdims=True)
            
            # Create spectral mask
            mask = magnitude / (noise_floor + 1e-6)
            mask = np.clip(mask - 1.0, 0, 1)  # Gate below noise floor
            mask = scipy.signal.medfilt2d(mask, kernel_size=(3, 3))  # Smooth mask
            
            # Apply mask
            denoised_stft = magnitude * mask * np.exp(1j * phase)
            
            # Convert back to time domain
            denoised_audio = librosa.istft(denoised_stft, hop_length=512)
            
            # Restore original shape
            if audio_data.ndim == 2:
                # Apply same processing to both channels
                denoised_stereo = np.zeros_like(audio_data)
                for ch in range(audio_data.shape[0]):
                    denoised_stereo[ch] = denoised_audio[:len(audio_data[ch])]
                return denoised_stereo.astype(np.float32)
            else:
                return denoised_audio.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Failed to denoise audio: {str(e)}")
            return audio_data
    
    async def apply_compression(self, audio_data: np.ndarray, 
                              threshold: float = -12.0, ratio: float = 4.0,
                              attack: float = 0.003, release: float = 0.1) -> np.ndarray:
        """Apply dynamic range compression."""
        try:
            # Convert threshold to linear
            threshold_linear = 10 ** (threshold / 20.0)
            
            # Calculate envelope
            envelope = np.abs(audio_data)
            
            # Smooth envelope (simplified attack/release)
            smoothed_envelope = np.zeros_like(envelope)
            for i in range(1, len(envelope)):
                if envelope[i] > smoothed_envelope[i-1]:
                    # Attack
                    alpha = 1 - np.exp(-1 / (attack * self.default_sample_rate))
                else:
                    # Release
                    alpha = 1 - np.exp(-1 / (release * self.default_sample_rate))
                
                smoothed_envelope[i] = (alpha * envelope[i] + 
                                      (1 - alpha) * smoothed_envelope[i-1])
            
            # Calculate gain reduction
            gain_reduction = np.ones_like(smoothed_envelope)
            above_threshold = smoothed_envelope > threshold_linear
            
            gain_reduction[above_threshold] = (
                threshold_linear / smoothed_envelope[above_threshold]
            ) ** ((ratio - 1) / ratio)
            
            # Apply compression
            compressed_audio = audio_data * gain_reduction
            
            return compressed_audio.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Failed to apply compression: {str(e)}")
            return audio_data
    
    async def apply_eq(self, audio_data: np.ndarray, sample_rate: int,
                      low_shelf: float = 0, mid_boost: float = 0, high_shelf: float = 0) -> np.ndarray:
        """Apply 3-band EQ."""
        try:
            # Convert to frequency domain
            fft = np.fft.fft(audio_data, axis=-1)
            freqs = np.fft.fftfreq(audio_data.shape[-1], 1/sample_rate)
            
            # Define frequency bands
            low_cutoff = 250
            high_cutoff = 4000
            
            # Create EQ curve
            eq_curve = np.ones_like(freqs)
            
            # Low shelf (below 250 Hz)
            low_mask = np.abs(freqs) < low_cutoff
            eq_curve[low_mask] *= 10 ** (low_shelf / 20.0)
            
            # High shelf (above 4 kHz)
            high_mask = np.abs(freqs) > high_cutoff
            eq_curve[high_mask] *= 10 ** (high_shelf / 20.0)
            
            # Mid boost (250 Hz - 4 kHz)
            mid_mask = (np.abs(freqs) >= low_cutoff) & (np.abs(freqs) <= high_cutoff)
            eq_curve[mid_mask] *= 10 ** (mid_boost / 20.0)
            
            # Apply EQ
            eq_fft = fft * eq_curve
            
            # Convert back to time domain
            eq_audio = np.fft.ifft(eq_fft, axis=-1).real
            
            return eq_audio.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Failed to apply EQ: {str(e)}")
            return audio_data
    
    async def change_speed(self, audio_data: np.ndarray, speed_factor: float) -> np.ndarray:
        """Change audio speed without affecting pitch."""
        try:
            if audio_data.ndim == 2:
                # Process each channel
                processed_channels = []
                for ch in range(audio_data.shape[0]):
                    processed_ch = librosa.effects.time_stretch(audio_data[ch], rate=speed_factor)
                    processed_channels.append(processed_ch)
                return np.array(processed_channels).astype(np.float32)
            else:
                processed_audio = librosa.effects.time_stretch(audio_data, rate=speed_factor)
                return processed_audio.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Failed to change speed: {str(e)}")
            return audio_data
    
    async def change_pitch(self, audio_data: np.ndarray, sample_rate: int, semitones: float) -> np.ndarray:
        """Change audio pitch without affecting speed."""
        try:
            if audio_data.ndim == 2:
                # Process each channel
                processed_channels = []
                for ch in range(audio_data.shape[0]):
                    processed_ch = librosa.effects.pitch_shift(
                        audio_data[ch], sr=sample_rate, n_steps=semitones
                    )
                    processed_channels.append(processed_ch)
                return np.array(processed_channels).astype(np.float32)
            else:
                processed_audio = librosa.effects.pitch_shift(
                    audio_data, sr=sample_rate, n_steps=semitones
                )
                return processed_audio.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Failed to change pitch: {str(e)}")
            return audio_data
    
    async def add_fade(self, audio_data: np.ndarray, sample_rate: int,
                      fade_in_duration: float = 0.0, fade_out_duration: float = 0.0) -> np.ndarray:
        """Add fade in/out effects."""
        try:
            audio_length = audio_data.shape[-1]
            fade_in_samples = int(fade_in_duration * sample_rate)
            fade_out_samples = int(fade_out_duration * sample_rate)
            
            # Create fade curves
            if fade_in_samples > 0:
                fade_in_curve = np.linspace(0, 1, fade_in_samples)
                if audio_data.ndim == 2:
                    audio_data[:, :fade_in_samples] *= fade_in_curve
                else:
                    audio_data[:fade_in_samples] *= fade_in_curve
            
            if fade_out_samples > 0:
                fade_out_curve = np.linspace(1, 0, fade_out_samples)
                if audio_data.ndim == 2:
                    audio_data[:, -fade_out_samples:] *= fade_out_curve
                else:
                    audio_data[-fade_out_samples:] *= fade_out_curve
            
            return audio_data.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Failed to add fade: {str(e)}")
            return audio_data
    
    async def analyze_voice(self, file_path: str) -> VoiceAnalysis:
        """Analyze voice characteristics in audio."""
        try:
            # Load audio
            y, sr = librosa.load(file_path, sr=self.default_sample_rate)
            
            # Extract features for voice analysis
            features = await self.extract_features(file_path)
            
            # Simple voice detection based on spectral characteristics
            is_speech = features.speechiness > 0.5
            confidence = features.speechiness
            
            # Gender detection (simplified based on fundamental frequency)
            f0 = librosa.yin(y, fmin=50, fmax=500, sr=sr)
            f0_mean = np.nanmean(f0[f0 > 0])
            
            if np.isnan(f0_mean):
                gender = "unknown"
            elif f0_mean < 140:
                gender = "male"
            elif f0_mean > 200:
                gender = "female"
            else:
                gender = "unknown"
            
            # Age estimation (simplified)
            if f0_mean > 250:
                age_range = "young"
            elif f0_mean < 100:
                age_range = "senior"
            else:
                age_range = "adult"
            
            # Emotion detection (simplified based on energy and spectral features)
            if features.energy > 0.7 and features.valence > 0.6:
                emotion = "happy"
            elif features.energy < 0.3 and features.valence < 0.4:
                emotion = "sad"
            elif features.energy > 0.8:
                emotion = "excited"
            else:
                emotion = "neutral"
            
            # Clarity score (based on spectral centroid and bandwidth)
            clarity_score = min(features.spectral_centroid / 3000.0, 1.0)
            
            # Noise level estimation
            noise_level = 1.0 - clarity_score
            
            voice_analysis = VoiceAnalysis(
                is_speech=is_speech,
                confidence=confidence,
                language=None,  # Would require language detection model
                gender=gender,
                age_range=age_range,
                emotion=emotion,
                speaker_count=1,  # Would require speaker diarization
                clarity_score=clarity_score,
                noise_level=noise_level,
                transcription=None  # Would require speech-to-text service
            )
            
            return voice_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze voice: {str(e)}")
            raise
    
    async def generate_spectrogram(self, audio_data: np.ndarray, sample_rate: int,
                                 output_path: str) -> bool:
        """Generate and save spectrogram image."""
        try:
            import matplotlib.pyplot as plt
            
            # Convert to mono if stereo
            if audio_data.ndim == 2:
                mono_audio = np.mean(audio_data, axis=0)
            else:
                mono_audio = audio_data
            
            # Compute spectrogram
            D = librosa.amplitude_to_db(np.abs(librosa.stft(mono_audio)), ref=np.max)
            
            # Create plot
            plt.figure(figsize=(12, 8))
            librosa.display.specshow(D, sr=sample_rate, x_axis='time', y_axis='hz')
            plt.colorbar(format='%+2.0f dB')
            plt.title('Spectrogram')
            plt.tight_layout()
            
            # Save plot
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate spectrogram: {str(e)}")
            return False
    
    async def process_audio(self, file_path: str, tasks: List[AudioProcessingTask],
                          parameters: Optional[Dict[str, Any]] = None) -> List[AudioProcessingResult]:
        """Process audio with specified tasks."""
        try:
            parameters = parameters or {}
            results = []
            
            # Load audio
            audio_data, sample_rate = await self.load_audio(file_path)
            current_audio = audio_data.copy()
            
            for task in tasks:
                start_time = time.time()
                success = True
                output_path = None
                output_data = None
                metadata = None
                features = None
                error_message = None
                warnings = []
                
                try:
                    if task == AudioProcessingTask.NORMALIZE:
                        target_lufs = parameters.get('target_lufs', -23.0)
                        current_audio = await self.normalize_audio(current_audio, target_lufs)
                    
                    elif task == AudioProcessingTask.DENOISE:
                        current_audio = await self.denoise_audio(current_audio, sample_rate)
                    
                    elif task == AudioProcessingTask.ENHANCE:
                        # Apply preset enhancement
                        preset = parameters.get('preset', 'voice_enhance')
                        if preset in self.preset_configs:
                            config = self.preset_configs[preset]
                            if config.get('normalize'):
                                current_audio = await self.normalize_audio(current_audio)
                            if config.get('denoise'):
                                current_audio = await self.denoise_audio(current_audio, sample_rate)
                            if 'eq_params' in config:
                                current_audio = await self.apply_eq(current_audio, sample_rate, **config['eq_params'])
                            if 'compress' in config:
                                current_audio = await self.apply_compression(current_audio, **config['compress'])
                    
                    elif task == AudioProcessingTask.CONVERT_FORMAT:
                        output_format = parameters.get('format', AudioFormat.WAV)
                        output_path = f"{self.temp_dir}/converted_{int(time.time())}.{output_format.value}"
                        await self.save_audio(current_audio, sample_rate, output_path, output_format)
                    
                    elif task == AudioProcessingTask.EXTRACT_FEATURES:
                        features = await self.extract_features(file_path)
                    
                    elif task == AudioProcessingTask.TRIM:
                        start_time_sec = parameters.get('start_time', 0.0)
                        end_time_sec = parameters.get('end_time', None)
                        start_sample = int(start_time_sec * sample_rate)
                        end_sample = int(end_time_sec * sample_rate) if end_time_sec else None
                        current_audio = current_audio[..., start_sample:end_sample]
                    
                    elif task == AudioProcessingTask.FADE_IN_OUT:
                        fade_in = parameters.get('fade_in_duration', 0.0)
                        fade_out = parameters.get('fade_out_duration', 0.0)
                        current_audio = await self.add_fade(current_audio, sample_rate, fade_in, fade_out)
                    
                    elif task == AudioProcessingTask.CHANGE_SPEED:
                        speed_factor = parameters.get('speed_factor', 1.0)
                        current_audio = await self.change_speed(current_audio, speed_factor)
                    
                    elif task == AudioProcessingTask.CHANGE_PITCH:
                        semitones = parameters.get('semitones', 0.0)
                        current_audio = await self.change_pitch(current_audio, sample_rate, semitones)
                    
                    elif task == AudioProcessingTask.EQUALIZE:
                        eq_params = parameters.get('eq_params', {})
                        current_audio = await self.apply_eq(current_audio, sample_rate, **eq_params)
                    
                    elif task == AudioProcessingTask.COMPRESS:
                        compress_params = parameters.get('compress_params', {})
                        current_audio = await self.apply_compression(current_audio, **compress_params)
                    
                    elif task == AudioProcessingTask.GENERATE_SPECTROGRAM:
                        output_path = f"{self.temp_dir}/spectrogram_{int(time.time())}.png"
                        await self.generate_spectrogram(current_audio, sample_rate, output_path)
                    
                    else:
                        warnings.append(f"Task {task.value} not implemented")
                
                except Exception as e:
                    success = False
                    error_message = str(e)
                
                processing_time = time.time() - start_time
                
                result = AudioProcessingResult(
                    task=task,
                    success=success,
                    output_path=output_path,
                    output_data=output_data,
                    metadata=metadata,
                    features=features,
                    processing_time=processing_time,
                    error_message=error_message,
                    warnings=warnings,
                    parameters=parameters
                )
                
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to process audio: {str(e)}")
            raise


# Example usage
async def main() -> None:
    """Example usage of audio processor."""
    processor = AudioProcessor()
    
    # Create a test audio file (sine wave)
    duration = 5.0  # seconds
    sample_rate = 44100
    frequency = 440.0  # A4 note
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    test_audio = np.sin(frequency * 2 * np.pi * t) * 0.5
    
    # Save test file
    test_file = "test_audio.wav"
    sf.write(test_file, test_audio, sample_rate)
    
    try:
        # Extract features
        features = await processor.extract_features(test_file)
        print(f"🎵 Audio features extracted:")
        print(f"   Tempo: {features.tempo:.1f} BPM")
        print(f"   Key: {features.key}")
        print(f"   Energy: {features.energy:.3f}")
        print(f"   Spectral Centroid: {features.spectral_centroid:.1f} Hz")
        
        # Process audio with multiple tasks
        tasks = [
            AudioProcessingTask.NORMALIZE,
            AudioProcessingTask.ENHANCE,
            AudioProcessingTask.GENERATE_SPECTROGRAM
        ]
        
        parameters = {
            'preset': 'music_master',
            'target_lufs': -16.0
        }
        
        results = await processor.process_audio(test_file, tasks, parameters)
        
        for result in results:
            if result.success:
                print(f"✅ {result.task.value}: {result.processing_time:.3f}s")
                if result.output_path:
                    print(f"   Output: {result.output_path}")
            else:
                print(f"❌ {result.task.value}: {result.error_message}")
        
        # Analyze voice (will show it's not voice since it's a sine wave)
        voice_analysis = await processor.analyze_voice(test_file)
        print(f"🎤 Voice analysis:")
        print(f"   Is speech: {voice_analysis.is_speech}")
        print(f"   Confidence: {voice_analysis.confidence:.3f}")
        print(f"   Clarity: {voice_analysis.clarity_score:.3f}")
        
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    asyncio.run(main())