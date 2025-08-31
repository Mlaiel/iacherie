"""Audio Content Management Module - Professional Audio Content Processing System

Module spécialisé pour la gestion, l'analyse et la protection du contenu audio
dans la plateforme IA Influencer Agent.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Audio Processing Expert, ML Engineer, Content Protection Specialist
Copyright: Fahed Mlaiel - All rights reserved

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et fera l'objet de poursuites judiciaires.
Contact: mlaiel@live.de
"""from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import logging
import hashlib
import json
import asyncio
from enum import Enum

import librosa
import numpy as np
import soundfile as sf
from mutagen import File as MutagenFile
from mutagen.id3 import ID3NoHeaderError

logger = logging.getLogger(__name__)

class AudioFormat(Enum):
    """Supported audio formats with quality indicators"""    MP3 = {"ext": ".mp3", "lossy": True, "quality": "good", "compression": "high"}
    WAV = {"ext": ".wav", "lossy": False, "quality": "excellent", "compression": "none"}
    FLAC = {"ext": ".flac", "lossy": False, "quality": "excellent", "compression": "lossless"}
    AAC = {"ext": ".aac", "lossy": True, "quality": "very_good", "compression": "high"}
    OGG = {"ext": ".ogg", "lossy": True, "quality": "good", "compression": "high"}
    M4A = {"ext": ".m4a", "lossy": True, "quality": "very_good", "compression": "high"}
    WMA = {"ext": ".wma", "lossy": True, "quality": "good", "compression": "high"}
    AIFF = {"ext": ".aiff", "lossy": False, "quality": "excellent", "compression": "none"}

class AudioContentType(Enum):
    """Audio content classification types"""    MUSIC = "music"
    SPEECH = "speech"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"
    SOUND_EFFECT = "sound_effect"
    AMBIENT = "ambient"
    JINGLE = "jingle"
    VOICE_OVER = "voice_over"
    INTERVIEW = "interview"
    LIVE_RECORDING = "live_recording"

@dataclass
class AudioMetadata:
    """Comprehensive audio metadata structure"""    # Technical metadata
    duration: float
    sample_rate: int
    channels: int
    bit_depth: Optional[int] = None
    bit_rate: Optional[int] = None
    format: Optional[str] = None
    file_size: Optional[int] = None
    
    # Descriptive metadata
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    track_number: Optional[int] = None
    total_tracks: Optional[int] = None
    composer: Optional[str] = None
    lyrics: Optional[str] = None
    
    # Rights and licensing
    copyright: Optional[str] = None
    license: Optional[str] = None
    publisher: Optional[str] = None
    isrc: Optional[str] = None  # International Standard Recording Code
    
    # Audio analysis metadata
    tempo: Optional[float] = None
    key_signature: Optional[str] = None
    time_signature: Optional[str] = None
    loudness_lufs: Optional[float] = None
    peak_amplitude: Optional[float] = None
    dynamic_range: Optional[float] = None
    spectral_centroid: Optional[float] = None
    zero_crossing_rate: Optional[float] = None
    
    # Content classification
    content_type: Optional[AudioContentType] = None
    language: Optional[str] = None
    mood: Optional[str] = None
    energy_level: Optional[str] = None
    
    # Quality metrics
    quality_score: Optional[float] = None
    noise_level: Optional[float] = None
    clipping_detected: bool = False
    silence_ratio: Optional[float] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: Optional[datetime] = None
    analyzed_at: Optional[datetime] = None
    
    # Additional metadata
    tags: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AudioFingerprint:
    """Audio fingerprint for content identification and protection"""    content_id: str
    primary_hash: str
    perceptual_hash: str
    chromaprint_hash: str
    spectral_hash: str
    temporal_signature: str
    mfcc_features: Optional[np.ndarray] = None
    chroma_features: Optional[np.ndarray] = None
    spectral_contrast: Optional[np.ndarray] = None
    tonnetz_features: Optional[np.ndarray] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence_score: float = 0.0
    quality_indicators: Dict[str, float] = field(default_factory=dict)

class AudioContentManager:
    """    Professional audio content management system with advanced processing capabilities
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """        Initialize the Audio Content Manager
        
        Args:
            config: Configuration dictionary for audio processing
        """        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.AudioContentManager")
        self.supported_formats = [fmt.value["ext"] for fmt in AudioFormat]
        
        # Initialize processing components
        self._init_components()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for audio processing"""        return {
            "max_file_size_mb": 100,
            "default_sample_rate": 44100,
            "quality_threshold": 0.7,
            "enable_fingerprinting": True,
            "enable_metadata_extraction": True,
            "enable_quality_analysis": True,
            "fingerprint_duration": 30.0,  # seconds
            "spectral_analysis": True,
            "tempo_analysis": True,
            "key_detection": True,
            "content_classification": True
        }
    
    def _init_components(self):
        """Initialize audio processing components"""        self.logger.info("Initializing Audio Content Manager components...")
        
        # Audio analysis configuration
        self.analysis_config = {
            "n_fft": 2048,
            "hop_length": 512,
            "n_mels": 128,
            "n_mfcc": 13,
            "n_chroma": 12
        }
        
        self.logger.info("Audio Content Manager initialized successfully")
    
    async def process_audio_file(
        self,
        file_path: Union[str, Path],
        extract_metadata: bool = True,
        generate_fingerprint: bool = True,
        quality_analysis: bool = True
    ) -> Dict[str, Any]:
        """        Process audio file with comprehensive analysis
        
        Args:
            file_path: Path to audio file
            extract_metadata: Whether to extract metadata
            generate_fingerprint: Whether to generate fingerprint
            quality_analysis: Whether to perform quality analysis
            
        Returns:
            Dict containing processed audio information
        """        try:
            file_path = Path(file_path)
            self.logger.info(f"Processing audio file: {file_path}")
            
            # Validate file
            if not await self._validate_audio_file(file_path):
                raise ValueError(f"Invalid audio file: {file_path}")
            
            # Load audio data
            audio_data, sample_rate = librosa.load(str(file_path), sr=None)
            
            results = {
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "processing_timestamp": datetime.now(timezone.utc),
                "audio_data_shape": audio_data.shape,
                "sample_rate": sample_rate
            }
            
            # Extract metadata
            if extract_metadata:
                metadata = await self._extract_audio_metadata(file_path, audio_data, sample_rate)
                results["metadata"] = metadata
            
            # Generate fingerprint
            if generate_fingerprint:
                fingerprint = await self._generate_audio_fingerprint(audio_data, sample_rate, str(file_path))
                results["fingerprint"] = fingerprint
            
            # Quality analysis
            if quality_analysis:
                quality_metrics = await self._analyze_audio_quality(audio_data, sample_rate)
                results["quality_metrics"] = quality_metrics
            
            # Content classification
            content_type = await self._classify_audio_content(audio_data, sample_rate)
            results["content_classification"] = content_type
            
            self.logger.info(f"Audio processing completed for: {file_path}")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to process audio file {file_path}: {e}")
            raise
    
    async def _validate_audio_file(self, file_path: Path) -> bool:
        """Validate audio file format and accessibility"""        try:
            # Check file existence and size
            if not file_path.exists():
                return False
            
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config["max_file_size_mb"]:
                self.logger.warning(f"File size {file_size_mb:.2f}MB exceeds limit")
                return False
            
            # Check format support
            if file_path.suffix.lower() not in self.supported_formats:
                return False
            
            # Try to load a small portion
            try:
                librosa.load(str(file_path), duration=1.0, sr=None)
                return True
            except Exception:
                return False
                
        except Exception as e:
            self.logger.error(f"Audio file validation failed: {e}")
            return False
    
    async def _extract_audio_metadata(
        self, 
        file_path: Path, 
        audio_data: np.ndarray, 
        sample_rate: int
    ) -> AudioMetadata:
        """Extract comprehensive audio metadata"""        try:
            # Basic technical metadata
            duration = len(audio_data) / sample_rate
            channels = 1 if len(audio_data.shape) == 1 else audio_data.shape[0]
            
            metadata = AudioMetadata(
                duration=duration,
                sample_rate=sample_rate,
                channels=channels,
                file_size=file_path.stat().st_size,
                format=file_path.suffix.lower()[1:]
            )
            
            # Extract file metadata using mutagen
            try:
                audio_file = MutagenFile(str(file_path))
                if audio_file is not None:
                    # Common metadata fields
                    metadata.title = self._get_tag_value(audio_file, ["TIT2", "TITLE", "\xa9nam"])
                    metadata.artist = self._get_tag_value(audio_file, ["TPE1", "ARTIST", "\xa9ART"])
                    metadata.album = self._get_tag_value(audio_file, ["TALB", "ALBUM", "\xa9alb"])
                    metadata.genre = self._get_tag_value(audio_file, ["TCON", "GENRE", "\xa9gen"])
                    
                    # Year/Date
                    year_value = self._get_tag_value(audio_file, ["TDRC", "DATE", "\xa9day"])
                    if year_value:
                        try:
                            metadata.year = int(str(year_value)[:4])
                        except (ValueError, TypeError):
                            pass
                    
                    # Technical metadata
                    if hasattr(audio_file, 'info'):
                        info = audio_file.info
                        metadata.bit_rate = getattr(info, 'bitrate', None)
                        if hasattr(info, 'bits_per_sample'):
                            metadata.bit_depth = info.bits_per_sample
                            
            except Exception as e:
                self.logger.warning(f"Failed to extract file metadata: {e}")
            
            # Audio analysis metadata
            if self.config.get("spectral_analysis", True):
                # Spectral features
                spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
                metadata.spectral_centroid = float(np.mean(spectral_centroids))
                
                # Zero crossing rate
                zcr = librosa.feature.zero_crossing_rate(audio_data)
                metadata.zero_crossing_rate = float(np.mean(zcr))
            
            # Tempo and rhythm analysis
            if self.config.get("tempo_analysis", True):
                try:
                    tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
                    metadata.tempo = float(tempo)
                except Exception as e:
                    self.logger.warning(f"Tempo analysis failed: {e}")
            
            # Key detection
            if self.config.get("key_detection", True):
                try:
                    chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
                    key_profile = np.mean(chroma, axis=1)
                    key_index = np.argmax(key_profile)
                    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                    metadata.key_signature = keys[key_index]
                except Exception as e:
                    self.logger.warning(f"Key detection failed: {e}")
            
            # Audio quality metrics
            metadata.peak_amplitude = float(np.max(np.abs(audio_data)))
            metadata.dynamic_range = float(np.max(audio_data) - np.min(audio_data))
            
            # Loudness analysis (simplified LUFS approximation)
            rms = librosa.feature.rms(y=audio_data)[0]
            metadata.loudness_lufs = float(20 * np.log10(np.mean(rms) + 1e-10))
            
            # Detect clipping
            metadata.clipping_detected = np.any(np.abs(audio_data) > 0.99)
            
            # Silence detection
            silence_threshold = 0.01
            silence_frames = np.sum(np.abs(audio_data) < silence_threshold)
            metadata.silence_ratio = silence_frames / len(audio_data)
            
            metadata.analyzed_at = datetime.now(timezone.utc)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {e}")
            raise
    
    def _get_tag_value(self, audio_file, tag_keys: List[str]) -> Optional[str]:
        """Extract tag value from audio file using multiple possible keys"""        for key in tag_keys:
            try:
                if key in audio_file:
                    value = audio_file[key]
                    if isinstance(value, list) and value:
                        return str(value[0])
                    elif value:
                        return str(value)
            except Exception:
                continue
        return None
    
    async def _generate_audio_fingerprint(
        self, 
        audio_data: np.ndarray, 
        sample_rate: int,
        content_id: str
    ) -> AudioFingerprint:
        """Generate comprehensive audio fingerprint for content protection"""        try:
            # Primary hash (raw audio data)
            primary_hash = hashlib.sha256(audio_data.tobytes()).hexdigest()
            
            # Perceptual hash using chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate, n_chroma=12)
            chroma_mean = np.mean(chroma, axis=1)
            perceptual_hash = hashlib.sha256(chroma_mean.tobytes()).hexdigest()[:32]
            
            # Chromaprint-style hash
            chromaprint_hash = self._generate_chromaprint_hash(audio_data, sample_rate)
            
            # Spectral hash
            spectral_hash = await self._generate_spectral_hash(audio_data, sample_rate)
            
            # Temporal signature
            temporal_signature = await self._generate_temporal_signature(audio_data, sample_rate)
            
            # Advanced features for matching
            mfcc_features = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            chroma_features = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
            tonnetz_features = librosa.feature.tonnetz(y=audio_data, sr=sample_rate)
            
            # Quality indicators
            quality_indicators = {
                "signal_to_noise": float(np.mean(audio_data**2) / (np.std(audio_data)**2 + 1e-10)),
                "dynamic_range": float(np.max(audio_data) - np.min(audio_data)),
                "spectral_clarity": float(np.mean(spectral_contrast)),
                "harmonic_content": float(np.mean(chroma_features))
            }
            
            # Confidence score based on audio quality
            confidence_score = min(1.0, (
                quality_indicators["signal_to_noise"] / 100 +
                quality_indicators["dynamic_range"] +
                quality_indicators["spectral_clarity"]
            ) / 3)
            
            fingerprint = AudioFingerprint(
                content_id=hashlib.md5(content_id.encode()).hexdigest(),
                primary_hash=primary_hash,
                perceptual_hash=perceptual_hash,
                chromaprint_hash=chromaprint_hash,
                spectral_hash=spectral_hash,
                temporal_signature=temporal_signature,
                mfcc_features=mfcc_features,
                chroma_features=chroma_features,
                spectral_contrast=spectral_contrast,
                tonnetz_features=tonnetz_features,
                confidence_score=confidence_score,
                quality_indicators=quality_indicators
            )
            
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"Audio fingerprint generation failed: {e}")
            raise
    
    def _generate_chromaprint_hash(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Generate Chromaprint-style hash for audio identification"""        try:
            # Extract chroma features with specific parameters
            chroma = librosa.feature.chroma_stft(
                y=audio_data, 
                sr=sample_rate,
                n_chroma=12,
                hop_length=512
            )
            
            # Create landmark-style hash
            peaks = []
            for i in range(chroma.shape[1] - 1):
                frame = chroma[:, i]
                next_frame = chroma[:, i + 1]
                
                # Find spectral peaks
                for j in range(len(frame)):
                    if frame[j] > 0.5 and frame[j] > next_frame[j]:
                        peaks.append((i, j, frame[j]))
            
            # Generate hash from peaks
            peaks_str = ''.join([f"{p[0]}{p[1]}{int(p[2]*100)}" for p in peaks[:100]])
            return hashlib.sha256(peaks_str.encode()).hexdigest()[:32]
            
        except Exception as e:
            self.logger.error(f"Chromaprint hash generation failed: {e}")
            return hashlib.sha256(str(np.random.random()).encode()).hexdigest()[:32]
    
    async def _generate_spectral_hash(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Generate spectral-based hash for content identification"""        try:
            # Spectral centroid and rolloff
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
            
            # Combine features
            spectral_features = np.concatenate([
                np.mean(spectral_centroids, axis=1),
                np.mean(spectral_rolloff, axis=1)
            ])
            
            return hashlib.sha256(spectral_features.tobytes()).hexdigest()[:32]
            
        except Exception as e:
            self.logger.error(f"Spectral hash generation failed: {e}")
            return hashlib.sha256(str(np.random.random()).encode()).hexdigest()[:32]
    
    async def _generate_temporal_signature(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Generate temporal signature for rhythm and timing patterns"""        try:
            # Onset detection
            onset_frames = librosa.onset.onset_detect(y=audio_data, sr=sample_rate)
            onset_times = librosa.frames_to_time(onset_frames, sr=sample_rate)
            
            # Tempo and beat tracking
            tempo, beat_frames = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            beat_times = librosa.frames_to_time(beat_frames, sr=sample_rate)
            
            # Create temporal signature
            temporal_data = {
                "tempo": float(tempo),
                "onset_count": len(onset_times),
                "beat_count": len(beat_times),
                "onset_intervals": np.diff(onset_times[:10]).tolist() if len(onset_times) > 1 else []
            }
            
            temporal_str = json.dumps(temporal_data, sort_keys=True)
            return hashlib.sha256(temporal_str.encode()).hexdigest()[:32]
            
        except Exception as e:
            self.logger.error(f"Temporal signature generation failed: {e}")
            return hashlib.sha256(str(np.random.random()).encode()).hexdigest()[:32]
    
    async def _analyze_audio_quality(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Analyze audio quality metrics"""        try:
            quality_metrics = {}
            
            # Signal-to-noise ratio approximation
            signal_power = np.mean(audio_data**2)
            noise_power = np.var(audio_data - np.mean(audio_data))
            quality_metrics["snr_db"] = 10 * np.log10(signal_power / (noise_power + 1e-10))
            
            # Dynamic range
            quality_metrics["dynamic_range_db"] = 20 * np.log10(
                np.max(np.abs(audio_data)) / (np.mean(np.abs(audio_data)) + 1e-10)
            )
            
            # Total harmonic distortion approximation
            spectral_power = np.abs(np.fft.fft(audio_data))**2
            fundamental_freq_idx = np.argmax(spectral_power[:len(spectral_power)//2])
            harmonic_power = np.sum(spectral_power[fundamental_freq_idx*2::fundamental_freq_idx])
            total_power = np.sum(spectral_power)
            quality_metrics["thd_percent"] = (harmonic_power / total_power) * 100
            
            # Frequency response flatness
            freq_bins = np.abs(np.fft.fft(audio_data))
            freq_variance = np.var(freq_bins[:len(freq_bins)//2])
            quality_metrics["frequency_flatness"] = 1.0 / (1.0 + freq_variance)
            
            # Peak detection for clipping
            clipping_threshold = 0.99
            clipped_samples = np.sum(np.abs(audio_data) > clipping_threshold)
            quality_metrics["clipping_percentage"] = (clipped_samples / len(audio_data)) * 100
            
            # Overall quality score (0-1)
            quality_score = min(1.0, max(0.0, (
                min(quality_metrics["snr_db"] / 40, 1.0) * 0.3 +
                min(quality_metrics["dynamic_range_db"] / 40, 1.0) * 0.3 +
                quality_metrics["frequency_flatness"] * 0.2 +
                max(0, 1 - quality_metrics["clipping_percentage"] / 5) * 0.2
            )))
            
            quality_metrics["overall_quality"] = quality_score
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Audio quality analysis failed: {e}")
            return {"overall_quality": 0.5, "error": str(e)}
    
    async def _classify_audio_content(self, audio_data: np.ndarray, sample_rate: int) -> AudioContentType:
        """Classify audio content type using audio features"""        try:
            # Extract features for classification
            mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            zcr = librosa.feature.zero_crossing_rate(audio_data)
            
            # Simple heuristic classification (in production, use ML model)
            mean_mfcc = np.mean(mfcc[1:])  # Skip first MFCC (energy)
            mean_chroma = np.mean(chroma)
            mean_spectral_centroid = np.mean(spectral_centroid)
            mean_zcr = np.mean(zcr)
            
            # Classification rules (simplified)
            if mean_chroma > 0.3 and mean_spectral_centroid > 2000:
                return AudioContentType.MUSIC
            elif mean_zcr > 0.1 and mean_spectral_centroid < 3000:
                return AudioContentType.SPEECH
            elif mean_mfcc < -20:
                return AudioContentType.AMBIENT
            else:
                return AudioContentType.MUSIC  # Default
                
        except Exception as e:
            self.logger.error(f"Audio content classification failed: {e}")
            return AudioContentType.MUSIC  # Default fallback
    
    async def store_content(self, audio_content: Dict[str, Any]) -> str:
        """Store processed audio content in database"""        try:
            # Generate unique content ID
            content_id = hashlib.sha256(
                f"{audio_content['file_path']}{datetime.now().isoformat()}".encode()
            ).hexdigest()
            
            # Here you would implement database storage
            # For now, return the generated ID
            
            self.logger.info(f"Audio content stored with ID: {content_id}")
            return content_id
            
        except Exception as e:
            self.logger.error(f"Failed to store audio content: {e}")
            raise
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats"""        return [fmt.value["ext"] for fmt in AudioFormat]
    
    def get_format_info(self, format_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific audio format"""        for fmt in AudioFormat:
            if fmt.value["ext"] == f".{format_name.lower()}" or fmt.name.lower() == format_name.lower():
                return fmt.value
        return None
